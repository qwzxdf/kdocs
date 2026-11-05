using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading;

namespace KErrorLog
{
    /// <summary>未解決のシンボルを参照している場所。</summary>
    public sealed class RefSite
    {
        public string Obj = "";
        public SymInfo From;
        public string Project = "";
    }

    /// <summary>同じシンボルを 1 つにまとめたもの。</summary>
    public sealed class UnresolvedSym
    {
        public string Mangled = "";
        public SymInfo Info;
        public List<RefSite> Refs = new List<RefSite>();
        /// <summary>null は「まだ探していない」。</summary>
        public List<LibHit> Libs;
        public List<SrcHit> Defs;
        public string Win32Lib;
    }

    /// <summary>原因が同じシンボルのまとまり。</summary>
    public sealed class CauseGroup
    {
        public string Key = "";
        public string Title = "";
        public List<string> Explain = new List<string>();
        public List<string> Remedies = new List<string>();
        public List<UnresolvedSym> Items = new List<UnresolvedSym>();
    }

    public sealed class AnalysisContext
    {
        public string SolutionDir = "";
        /// <summary>アクティブな構成のプラットフォーム("x64"、"Win32" など)。分からなければ空。</summary>
        public string Platform = "";
    }

    public static class Diagnoser
    {
        private static readonly HashSet<string> EntryNames = new HashSet<string>(StringComparer.Ordinal)
        {
            "main", "wmain", "WinMain", "wWinMain", "mainCRTStartup", "wmainCRTStartup", "WinMainCRTStartup", "wWinMainCRTStartup"
        };

        private static readonly HashSet<string> CrtNames = new HashSet<string>(StringComparer.Ordinal)
        {
            "CxxThrowException", "CxxFrameHandler3", "CxxFrameHandler4", "security_check_cookie", "security_cookie", "GSHandlerCheck",
            "chkstk", "alloca_probe", "fltused", "report_rangecheckfailure", "RTC_InitBase", "RTC_Shutdown", "RTC_CheckStackVars",
            "RTC_CheckEsp", "CrtDbgReport", "CrtDbgReportW", "purecall", "ehvec_ctor", "ehvec_dtor"
        };

        private static readonly Regex StdcallTail = new Regex(@"@\d+$", RegexOptions.Compiled);

        /// <summary>解析した結果から、未解決のシンボルを 1 つずつにまとめて取り出す。</summary>
        public static List<UnresolvedSym> Collect(BuildReport report)
        {
            var map = new Dictionary<string, UnresolvedSym>(StringComparer.Ordinal);
            var list = new List<UnresolvedSym>();
            foreach (Diag d in report.Diags)
            {
                if (d.Kind != DiagKind.Unresolved || d.Unresolved == null) continue;
                UnresolvedRef r = d.Unresolved;
                UnresolvedSym s;
                if (!map.TryGetValue(r.SymbolMangled, out s))
                {
                    s = new UnresolvedSym { Mangled = r.SymbolMangled, Info = SymbolPretty.Parse(r.SymbolDem, r.SymbolMangled) };
                    s.Win32Lib = Hints.Win32Lib(r.SymbolMangled);
                    map[r.SymbolMangled] = s;
                    list.Add(s);
                }
                s.Refs.Add(new RefSite
                {
                    Obj = r.FromObj,
                    From = r.FuncDem.Length > 0 ? SymbolPretty.Parse(r.FuncDem, r.FuncMangled) : null,
                    Project = d.Project
                });
                foreach (KeyValuePair<string, string> more in r.More)
                    s.Refs.Add(new RefSite
                    {
                        Obj = more.Key,
                        From = more.Value.Length > 0 ? SymbolPretty.Parse(more.Value, more.Value) : null,
                        Project = d.Project
                    });
            }
            return list;
        }

        /// <summary>.lib とソースを探して、シンボルに結果を書き込む(時間がかかるので、別のスレッドで呼ぶ)。</summary>
        public static void Enrich(List<UnresolvedSym> syms, AnalysisContext ctx, CancellationToken ct)
        {
            foreach (UnresolvedSym s in syms)
            {
                s.Libs = new List<LibHit>();
                s.Defs = new List<SrcHit>();
            }
            if (string.IsNullOrEmpty(ctx.SolutionDir)) return;
            var searchable = syms.Where(s => !IsEntry(s)).ToList();
            LibScanner.Scan(searchable, ctx.SolutionDir, ct, 6000);
            SourceScanner.Scan(searchable, ctx.SolutionDir, ct, 6000);
        }

        /// <summary>足りないファイルを、ソリューションの下から探す必要があるか。</summary>
        public static bool NeedsFileSearch(BuildReport report)
        {
            return report != null && report.Diags.Any(d => d.MissingName.Length > 0);
        }

        private static readonly HashSet<string> SkipDirs = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            ".git", ".vs", "node_modules", ".svn", "ipch"
        };

        /// <summary>
        /// 「ファイルを開けない」エラー(C1083、LNK1104、LNK1181)の、足りないファイルを、ソリューションの下から探す。
        /// 見つかれば、追加のインクルード / ライブラリ ディレクトリに入れる場所が分かる。
        /// </summary>
        public static void EnrichFiles(BuildReport report, AnalysisContext ctx, CancellationToken ct)
        {
            var wanted = report.Diags.Where(d => d.MissingName.Length > 0).ToList();
            if (wanted.Count == 0 || string.IsNullOrEmpty(ctx.SolutionDir) || !Directory.Exists(ctx.SolutionDir)) return;

            var tails = new List<KeyValuePair<Diag, string>>();
            foreach (Diag d in wanted)
            {
                d.Found.Clear();
                string n = d.MissingName.Replace('/', '\\');
                while (n.StartsWith("..\\", StringComparison.Ordinal) || n.StartsWith(".\\", StringComparison.Ordinal))
                    n = n.Substring(n.IndexOf('\\') + 1);
                if (n.Length > 0) tails.Add(new KeyValuePair<Diag, string>(d, "\\" + n));
            }
            if (tails.Count == 0) return;

            var sw = System.Diagnostics.Stopwatch.StartNew();
            var stack = new Stack<string>();
            stack.Push(ctx.SolutionDir);
            int files = 0;
            while (stack.Count > 0 && !ct.IsCancellationRequested && sw.ElapsedMilliseconds < 4000 && files < 100000)
            {
                string dir = stack.Pop();
                string[] list = null;
                try { list = Directory.GetFiles(dir); } catch (Exception) { }
                if (list != null)
                    foreach (string f in list)
                    {
                        files++;
                        foreach (var t in tails)
                            if (t.Key.Found.Count < 5 && f.EndsWith(t.Value, StringComparison.OrdinalIgnoreCase))
                                t.Key.Found.Add(f);
                    }
                string[] subs = null;
                try { subs = Directory.GetDirectories(dir); } catch (Exception) { }
                if (subs == null) continue;
                foreach (string sub in subs)
                    if (!SkipDirs.Contains(Path.GetFileName(sub))) stack.Push(sub);
            }
        }

        public static string CoreName(string mangled)
        {
            string n = mangled ?? "";
            if (n.StartsWith("__imp_", StringComparison.Ordinal)) n = n.Substring(6);
            n = n.TrimStart('_');
            return StdcallTail.Replace(n, "");
        }

        public static bool IsEntry(UnresolvedSym s)
        {
            return EntryNames.Contains(CoreName(s.Mangled));
        }

        // ---- 原因ごとにまとめる ----

        public static List<CauseGroup> Group(List<UnresolvedSym> syms, AnalysisContext ctx)
        {
            var groups = new Dictionary<string, CauseGroup>(StringComparer.Ordinal);
            var order = new List<CauseGroup>();
            foreach (UnresolvedSym s in syms)
            {
                CauseGroup g = Assign(s, ctx, groups, order);
                g.Items.Add(s);
            }
            return order.OrderByDescending(g => g.Items.Sum(i => Math.Max(1, i.Refs.Count))).ThenBy(g => g.Key, StringComparer.Ordinal).ToList();
        }

        private static CauseGroup Get(Dictionary<string, CauseGroup> groups, List<CauseGroup> order, string key, Action<CauseGroup> init)
        {
            CauseGroup g;
            if (groups.TryGetValue(key, out g)) return g;
            g = new CauseGroup { Key = key };
            init(g);
            groups[key] = g;
            order.Add(g);
            return g;
        }

        private static LibHit BestHit(UnresolvedSym s, AnalysisContext ctx, bool exact, bool? importLib)
        {
            if (s.Libs == null) return null;
            ushort want = LibScanner.MachineOf(ctx.Platform);
            return s.Libs
                .Where(h => h.Exact == exact && (importLib == null || h.IsImportLib == importLib.Value))
                .OrderByDescending(h => want != 0 && h.Machine == want)
                .ThenBy(h => h.Path.Length)
                .FirstOrDefault();
        }

        private static CauseGroup Assign(UnresolvedSym s, AnalysisContext ctx, Dictionary<string, CauseGroup> groups, List<CauseGroup> order)
        {
            SymInfo info = s.Info;
            ushort want = LibScanner.MachineOf(ctx.Platform);

            // 1. 起動関数
            if (IsEntry(s))
            {
                string core = CoreName(s.Mangled);
                return Get(groups, order, "entry", g =>
                {
                    g.Title = "起動関数 (" + core + ") が見つかりません";
                    g.Explain.Add("リンカーが、プログラムの入口になる関数を探しましたが、定義がありません。");
                    g.Remedies.Add("コンソール アプリ (/SUBSYSTEM:CONSOLE) には main、Windows アプリ (/SUBSYSTEM:WINDOWS) には WinMain / wWinMain が要ります。");
                    g.Remedies.Add("リンカー > システム > サブシステム の設定が、書いた関数と合っているか確かめます。");
                    g.Remedies.Add("main を書いたファイルが、プロジェクトに入っているか(ビルドから除外されていないか)確かめます。");
                    g.Remedies.Add("DLL や静的ライブラリのプロジェクトなら、構成の種類が .exe になっていないか確かめます。");
                });
            }

            // 2. .lib が見つかったとき
            if (s.Libs != null && s.Libs.Count > 0)
            {
                LibHit exact = BestHit(s, ctx, true, null);
                if (exact != null)
                {
                    bool machineOk = want == 0 || exact.Machine == want;
                    if (machineOk)
                    {
                        return Get(groups, order, "lib:" + exact.Path, g =>
                        {
                            g.Title = exact.FileName + " に実体があります (リンクされていません)";
                            g.Explain.Add("ビルド済みの " + Shorten(exact.Path, ctx.SolutionDir) + " (" + exact.MachineName + (exact.IsImportLib ? "、DLL の import lib" : "、静的ライブラリ") + ") に、このシンボルが入っています。このプロジェクトのリンカー入力に入っていないのが原因です。");
                            g.Remedies.Add("リンカー > 入力 > 追加の依存ファイル に " + exact.FileName + " を追加します。");
                            g.Remedies.Add("リンカー > 全般 > 追加のライブラリ ディレクトリ に " + Path.GetDirectoryName(exact.Path) + " を追加します(絶対パスでも可)。");
                            g.Remedies.Add("同じソリューション内のプロジェクトなら、参照の追加(プロジェクト参照)で、リンクが自動で済みます。");
                            g.Remedies.Add("コードで済ませるなら、#pragma comment(lib, \"" + exact.FileName + "\") でも同じ効果です。");
                        });
                    }
                    return Get(groups, order, "machine:" + exact.Path, g =>
                    {
                        g.Title = exact.FileName + " はビット数が違います (" + exact.MachineName + ")";
                        g.Explain.Add(Shorten(exact.Path, ctx.SolutionDir) + " に実体はありますが、" + exact.MachineName + " 用です。いまのビルドは " + LibScanner.MachineName(want) + " です。");
                        g.Remedies.Add("同じプラットフォーム (" + LibScanner.MachineName(want) + ") でビルドした .lib を使います。");
                        g.Remedies.Add("ライブラリのプロジェクトも、アクティブなプラットフォームでビルドしたか確かめます。");
                    });
                }

                // 名前は同じだが、__imp_ の有無だけが違う
                LibHit variant = BestHit(s, ctx, false, null);
                if (variant != null)
                {
                    if (info.Import && !variant.IsImportLib)
                    {
                        return Get(groups, order, "static-vs-import:" + variant.Path, g =>
                        {
                            g.Title = variant.FileName + " は静的ライブラリですが、ヘッダーは dllimport で宣言しています";
                            g.Explain.Add("シンボル名の頭の __imp_ は、ヘッダーが __declspec(dllimport) で宣言している印です。ところが " + Shorten(variant.Path, ctx.SolutionDir) + " には、__imp_ の付かない普通のシンボルしかありません (静的ライブラリ)。");
                            g.Remedies.Add("ヘッダーの API マクロ (PREST_API など) が、静的ライブラリのときは何も展開されないようにします。多くは「XXX_STATIC」のようなマクロを定義します。");
                            g.Remedies.Add("利用側のプロジェクトに、そのマクロが定義されているか確かめます (プリプロセッサの定義)。");
                            g.Remedies.Add("DLL として使うつもりなら、提供元を DLL でビルドし直して、その import lib をリンクします。");
                        });
                    }
                    if (!info.Import && variant.IsImportLib)
                    {
                        return Get(groups, order, "data-noimport:" + variant.Path, g =>
                        {
                            g.Title = variant.FileName + " の変数を、dllimport なしで参照しています";
                            g.Explain.Add("DLL が持つ変数 (データ) は、__declspec(dllimport) 付きで宣言しないと参照できません。関数と違い、変数にはリンク用の代わりの入口がありません。");
                            g.Remedies.Add("ヘッダーで、変数の宣言に API マクロ (dllimport を展開するもの) を付けます。");
                        });
                    }
                }
            }

            // 2.5 C ランタイムの内部の関数(ランタイムがリンクされていない)
            if (CrtNames.Contains(CoreName(s.Mangled)))
            {
                return Get(groups, order, "crt", g =>
                {
                    g.Title = "C ランタイム(CRT)の内部の関数が見つかりません";
                    g.Explain.Add("これらはコンパイラが自動で呼び出す関数で、ランタイム ライブラリ (vcruntime / ucrt) が提供します。ランタイムがリンクされていない構成で出ます。");
                    g.Remedies.Add("リンカー > 入力 > 「すべての既定のライブラリを無視」が「はい (/NODEFAULTLIB)」になっていないか確かめます。");
                    g.Remedies.Add("カーネル モードやスタートアップを自作する構成なら、_fltused や __security_cookie などを自分で定義します。");
                    g.Remedies.Add("/GS (バッファー セキュリティ チェック) を切ると、__security_cookie の参照は消えます。");
                    g.Remedies.Add("/MT と /MD の混在や、別のコンパイラで作った .lib のときも出ます。ランタイム ライブラリをそろえます。");
                });
            }

            // 3. Windows / DirectX
            if (s.Win32Lib != null)
            {
                string lib = s.Win32Lib;
                return Get(groups, order, "win32:" + lib, g =>
                {
                    g.Title = "Windows / SDK の関数です (" + lib + " が必要)";
                    g.Explain.Add("これらは " + lib + " が提供する関数です。ヘッダーを include しただけでは、リンクされません。");
                    g.Remedies.Add("リンカー > 入力 > 追加の依存ファイル に " + lib + " を追加します。");
                    g.Remedies.Add("コードで済ませるなら、#pragma comment(lib, \"" + lib + "\") でも同じ効果です。");
                });
            }

            // 4. vtable
            if (info.Kind == SymKind.VTable || s.Mangled.StartsWith("??_7", StringComparison.Ordinal))
            {
                string cls = info.Scope.Length > 0 ? info.Scope : info.Pretty;
                return Get(groups, order, "vtable:" + cls, g =>
                {
                    g.Title = cls + " の vtable (仮想関数の表) が見つかりません";
                    g.Explain.Add("vtable は、最初の非 inline の仮想関数 (キー関数) の定義と一緒に作られます。そのため、仮想関数の定義が 1 つ抜けていると、vtable ごと未解決になります。");
                    g.Remedies.Add(cls + " の virtual 関数 (純粋仮想関数 = 0 を除く) の、すべてに定義があるか確かめます。");
                    g.Remedies.Add("virtual デストラクターの定義 (または = default) を書き忘れていないか確かめます。");
                    g.Remedies.Add("そのクラスの .cpp が、プロジェクトに入っているか確かめます。");
                });
            }

            // 5. static メンバー変数・グローバル変数
            if (!info.IsFunction && (info.Kind == SymKind.StaticVariable || info.Kind == SymKind.Variable))
            {
                string cls = info.Class.Length > 0 ? info.Class : "(グローバル)";
                bool hasDef = s.Defs != null && s.Defs.Count > 0;
                return Get(groups, order, "var:" + cls + hasDef, g =>
                {
                    g.Title = info.Kind == SymKind.StaticVariable
                        ? cls + " の static メンバー変数の定義がありません"
                        : "グローバル変数の定義がありません";
                    g.Explain.Add("static メンバーや extern の宣言だけでは、実体は作られません。.cpp に 1 つだけ、定義が要ります。");
                    g.Remedies.Add("いずれかの .cpp に、型を付けて定義を書きます (例: int " + (info.Class.Length > 0 ? info.Class + "::" : "") + TemplateTailOf(info.Name) + " = 0;)。");
                    g.Remedies.Add("C++17 以降なら、宣言を inline static (または inline constexpr) にすると、ヘッダーだけで済みます。");
                    if (hasDef) g.Explain.Add("ソースに定義らしい行がありました。その .cpp が、プロジェクトに入っているか確かめます。");
                });
            }

            // 6. 定義がソースにある
            if (s.Defs != null && s.Defs.Count > 0)
            {
                return Get(groups, order, "def-found:" + (info.Import ? "imp:" : "") + (info.Class.Length > 0 ? info.Class : info.Namespace), g =>
                {
                    g.Title = "定義はソースにあるのに、リンクされていません";
                    g.Explain.Add("ソースの中に、これらの関数の定義らしい行が見つかりました (各項目の下に示します)。それでも未解決になるのは、その定義が、このプロジェクトのリンクに入っていないからです。");
                    if (info.Import)
                        g.Explain.Add("シンボルに __imp_ が付いているので、定義は別の DLL プロジェクトにあり、その import lib (.lib) が必要です。");
                    g.Remedies.Add("その .cpp が、プロジェクトに入っているか (ビルドから除外されていないか) 確かめます。");
                    g.Remedies.Add("別のプロジェクト (lib / DLL) にあるなら、参照の追加か、追加の依存ファイルで、その .lib をリンクします。");
                    g.Remedies.Add("#if や構成の違いで、その定義がコンパイルされていないか確かめます。");
                    g.Remedies.Add("宣言と定義の引数の型・const・名前空間が、1 つでも違うと別の関数になります。見比べます。");
                });
            }

            // 7. dllimport で、実体がどこにも見つからない
            if (info.Import)
            {
                string ns = info.Namespace.Length > 0 ? FirstScope(info.Namespace) : "";
                return Get(groups, order, "import:" + ns, g =>
                {
                    g.Title = "dllimport で参照している関数の実体が見つかりません" + (ns.Length > 0 ? " (" + ns + ")" : "");
                    g.Explain.Add("シンボル名の頭の __imp_ は、ヘッダーが __declspec(dllimport) で宣言している印です。DLL が提供する関数を使うには、その DLL と一緒に作られる import library (.lib) を、リンクする必要があります。");
                    g.Explain.Add("同じ名前空間のシンボルが並んでいる場合は、1 つの .lib が丸ごと足りない可能性が高いです。");
                    g.Remedies.Add("提供元の DLL プロジェクトをビルドして、.lib ができているか確かめます。");
                    g.Remedies.Add("その .lib を、リンカー > 入力 > 追加の依存ファイル に追加します (同じソリューションなら、参照の追加が早い)。");
                    g.Remedies.Add("静的ライブラリとして使うつもりなら、API マクロ (EXPORT / IMPORT) が dllimport にならないようにします。");
                });
            }

            // 8. テンプレート
            if (info.Kind == SymKind.TemplateFunction || (info.Name.IndexOf('<') >= 0 && info.IsFunction))
            {
                return Get(groups, order, "template", g =>
                {
                    g.Title = "テンプレートのインスタンスが見つかりません";
                    g.Explain.Add("テンプレートの定義を .cpp に書くと、使う側の翻訳単位ではインスタンス化できず、リンクで未解決になります。");
                    g.Remedies.Add("テンプレートの定義を、ヘッダーに移します。");
                    g.Remedies.Add("または、定義のある .cpp の末尾で、明示的にインスタンス化します (例: template void f<int>(int);)。");
                });
            }

            // 9. メンバー関数
            if (info.IsMember && info.Class.Length > 0)
            {
                string cls = info.Class;
                return Get(groups, order, "member:" + cls, g =>
                {
                    g.Title = cls + " のメンバー関数の定義が見つかりません";
                    g.Explain.Add("宣言はあるのに、定義がありません。または、宣言と定義が少しずれて、別の関数になっています。");
                    g.Remedies.Add("該当の関数の定義 (" + cls + "::関数名) を、.cpp に書いたか確かめます。");
                    g.Remedies.Add("宣言と定義の引数の型・const・参照・名前空間が、そろっているか確かめます。");
                    g.Remedies.Add("その .cpp が、プロジェクトに入っているか確かめます。");
                    g.Remedies.Add("呼ぶつもりのない関数なら、宣言を消します。");
                });
            }

            // 10. 関数 / C の名前 / そのほか
            string fnNs = info.Namespace.Length > 0 ? FirstScope(info.Namespace) : "";
            return Get(groups, order, "func:" + fnNs, g =>
            {
                g.Title = "関数の定義が見つかりません" + (fnNs.Length > 0 ? " (" + fnNs + ")" : "");
                g.Explain.Add("宣言はあるのに、定義がリンクされていません。");
                if (info.Kind == SymKind.CSymbol)
                    g.Explain.Add("装飾のない C の名前です。extern \"C\" の宣言と定義の、両方がそろっているか確かめます。");
                g.Remedies.Add("関数の定義を書いたか、その .cpp / .lib がプロジェクトに入っているか確かめます。");
                g.Remedies.Add("宣言と定義の引数の型・const・名前空間が、そろっているか確かめます。");
                g.Remedies.Add("C++ の関数を C のコードから呼ぶ (またはその逆) なら、extern \"C\" の有無をそろえます。");
            });
        }

        private static string TemplateTailOf(string name)
        {
            int i = name.IndexOf('<');
            return i > 0 ? name.Substring(0, i) : name;
        }

        private static string FirstScope(string ns)
        {
            int i = ns.IndexOf("::", StringComparison.Ordinal);
            return i > 0 ? ns.Substring(0, i) : ns;
        }

        public static string Shorten(string path, string root)
        {
            if (!string.IsNullOrEmpty(root) && path.StartsWith(root, StringComparison.OrdinalIgnoreCase))
                return path.Substring(root.Length).TrimStart('\\', '/');
            return path;
        }
    }
}
