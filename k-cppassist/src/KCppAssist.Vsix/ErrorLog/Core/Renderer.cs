using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

namespace KCppAssist.ErrorLog
{
    public sealed class RenderOptions
    {
        public bool ShowWarnings;
        public bool FullTrace;
        public bool AttachRaw;
        public bool RawMode;
    }

    public sealed class RenderInput
    {
        public BuildReport Report;
        public List<UnresolvedSym> Syms = new List<UnresolvedSym>();
        public AnalysisContext Ctx = new AnalysisContext();
        /// <summary>.lib とソースを検索している最中か。</summary>
        public bool Pending;
    }

    public static class Paths
    {
        private static readonly string[] LibraryMarks =
        {
            @"\vc\tools\msvc\", @"\windows kits\", @"\microsoft visual studio\", @"\vcpkg_installed\",
            @"\vcpkg\installed\", @"\vcpkg\packages\", "/usr/include/", "/usr/lib/"
        };

        public static bool IsLibraryFile(string path)
        {
            if (string.IsNullOrEmpty(path)) return false;
            string p = path.Replace('/', '\\').ToLowerInvariant();
            foreach (string mark in LibraryMarks)
                if (p.Contains(mark.Replace('/', '\\'))) return true;
            return false;
        }

        /// <summary>自分のコードか。ソリューションのフォルダーが分かればその下、分からなければライブラリ以外。</summary>
        public static bool IsUserFile(string path, string solutionDir)
        {
            if (string.IsNullOrEmpty(path) || IsLibraryFile(path)) return false;
            if (string.IsNullOrEmpty(solutionDir)) return true;
            try
            {
                string full = Path.GetFullPath(path);
                string dir = Path.GetFullPath(solutionDir).TrimEnd('\\') + "\\";
                return full.StartsWith(dir, StringComparison.OrdinalIgnoreCase);
            }
            catch (Exception) { return true; }
        }

        /// <summary>表示用の短いパス。自分のコードはソリューションからの相対、それ以外はファイル名だけ。</summary>
        public static string Display(string path, string solutionDir)
        {
            if (string.IsNullOrEmpty(path)) return "";
            if (IsUserFile(path, solutionDir) && !string.IsNullOrEmpty(solutionDir))
            {
                try
                {
                    string dir = Path.GetFullPath(solutionDir).TrimEnd('\\') + "\\";
                    string full = Path.GetFullPath(path);
                    if (full.StartsWith(dir, StringComparison.OrdinalIgnoreCase)) return full.Substring(dir.Length);
                }
                catch (Exception) { }
            }
            try { return Path.GetFileName(path); } catch (Exception) { return path; }
        }
    }

    /// <summary>解析した結果を、色つきの文書(Doc)にする。</summary>
    public static class Renderer
    {
        // 描画中だけ使う(同じスレッドで、同期的に呼ばれる)
        private static bool _pending;
        private static BuildReport _report;
        private static Dictionary<Diag, string> _cascade = new Dictionary<Diag, string>();
        private static Diag _cascadeRoot;
        private static readonly Dictionary<string, string[]> LineCache = new Dictionary<string, string[]>(StringComparer.OrdinalIgnoreCase);

        public static Doc Render(RenderInput input, RenderOptions opt)
        {
            var doc = new Doc();
            LineCache.Clear();
            _pending = input != null && input.Pending;
            BuildReport report = input.Report;
            if (report == null)
            {
                new LineBuilder(doc).Add("ビルドの出力はまだありません。ビルドすると、ここにエラーが出ます。", Role.Dim).Done();
                return doc;
            }
            _report = report;
            Cascade.Result casc = ErrorLogSettings.ShowCascade ? Cascade.Analyze(report) : new Cascade.Result();
            _cascade = casc.Notes;
            _cascadeRoot = casc.Root;
            if (opt.RawMode) RenderRaw(doc, input, opt);
            else RenderOrganized(doc, input, opt);
            return doc;
        }

        // =========================================================================
        // 整理した表示
        // =========================================================================

        private static void RenderOrganized(Doc doc, RenderInput input, RenderOptions opt)
        {
            BuildReport report = input.Report;
            string sol = input.Ctx.SolutionDir;

            int errors = report.ErrorCount;
            // 集計の行(LNK1120 など)しか読めなかったときも、ビルドは失敗している
            bool onlySummary = errors == 0 && report.Diags.Any(d => d.IsSummary);
            int warnings = report.WarningCount;
            int linker = report.Diags.Count(d => d.Sev == Sev.Error && d.IsLinker && !d.IsSummary);

            var head = new LineBuilder(doc);
            if (errors > 0)
            {
                head.Add("✖ ビルドに失敗しました", Role.Error, true);
                head.Add("   エラー " + errors + " 件", Role.Error);
                head.Add(" (リンカー " + linker + " / コンパイラ " + (errors - linker) + ")", Role.Dim);
            }
            else if (onlySummary)
            {
                head.Add("✖ ビルドに失敗しました", Role.Error, true);
                head.Add("   リンカーの集計行だけを読めました。「原文」表示で全文を確かめてください", Role.Dim);
            }
            else
            {
                head.Add("✔ エラーはありません", Role.Good, true);
            }
            head.Add("   警告 " + warnings + " 件", warnings > 0 ? Role.Warning : Role.Dim);
            head.Done();

            var sub = new LineBuilder(doc);
            if (report.Config.Length > 0) sub.Add("構成: " + report.Config + "   ", Role.Dim);
            if (report.Projects.Count > 0) sub.Add("プロジェクト: " + string.Join(", ", report.Projects.Values.Distinct()) + "   ", Role.Dim);
            if (report.Summary.Length > 0) sub.Add(report.Summary, Role.Dim);
            sub.Done();
            if (errors >= 2) AddOrderAdvice(doc, report, sol);

            // 同じ内容のエラー(場所だけが違う)は、1 つにまとめる
            var sameMap = new Dictionary<string, List<Diag>>();
            foreach (Diag d in report.Diags)
            {
                if (d.Kind != DiagKind.Generic || d.IsLinker) continue;
                string k = SameKey(d);
                List<Diag> list;
                if (!sameMap.TryGetValue(k, out list)) sameMap[k] = list = new List<Diag>();
                list.Add(d);
            }
            var sameShown = new HashSet<string>();

            bool unresolvedDone = false;
            int shown = 0;
            foreach (Diag d in report.Diags)
            {
                if (d.Sev == Sev.Warning && !opt.ShowWarnings) continue;
                if (d.IsSummary) continue;

                // 同じ内容は 1 つにまとめて出すので、2 つ目以降は数えない(上限に入れない)
                List<Diag> same = null;
                if (d.Kind == DiagKind.Generic && !d.IsLinker)
                {
                    string k = SameKey(d);
                    if (!sameShown.Add(k)) continue;
                    sameMap.TryGetValue(k, out same);
                }

                if (d.Kind == DiagKind.Unresolved)
                {
                    if (unresolvedDone) continue;
                    unresolvedDone = true;
                    RenderUnresolved(doc, input, opt);
                    shown++;
                    continue;
                }
                if (++shown > ErrorLogSettings.MaxItems)
                {
                    new LineBuilder(doc).Space().Add("… 件数が多いので、ここから先は省略しました。「原文」表示で全部を読めます。", Role.Dim).Done();
                    break;
                }
                switch (d.Kind)
                {
                    case DiagKind.MultiDefined: RenderMultiDef(doc, d, opt, sol); break;
                    case DiagKind.Mismatch: RenderMismatch(doc, d, opt, sol); break;
                    default: RenderGeneric(doc, d, opt, sol, same); break;
                }
            }

            if (shown == 0 && errors == 0 && report.Diags.Count == 0)
                new LineBuilder(doc).Space().Add("出力にエラーも警告もありません。", Role.Dim).Done();
        }

        /// <summary>エラーが複数あるとき、「一番上から直す」案内と、連鎖している件数を出す。</summary>
        private static void AddOrderAdvice(Doc doc, BuildReport report, string sol)
        {
            if (!ErrorLogSettings.ShowHints || !ErrorLogSettings.ShowAdvice) return;
            var lb = new LineBuilder(doc).Space();
            lb.Add("まず: ", Role.Hint, true).Add("一番上のエラーから直して、ビルドし直します。1 つの原因から、あとのエラーが連鎖して出ることが多いからです。", Role.Normal);
            lb.Done();
            if (_cascade.Count > 0)
                Line(doc, 1, null).Add("この " + report.ErrorCount + " 件のうち " + _cascade.Count + " 件は、上のエラーの影響で出ている可能性があります (「連鎖の可能性」と書いた項目)。", Role.Dim).Done();
            if (_cascadeRoot != null && _cascadeRoot.HasLocation)
                Line(doc, 1, null).Add("原因の候補: ", Role.Dim).Add(_cascadeRoot.Code + "  ", Role.Code, true)
                    .Link(Paths.Display(_cascadeRoot.File, sol) + "(" + _cascadeRoot.Line + ")", _cascadeRoot.File, _cascadeRoot.Line, _cascadeRoot.Col).Done();
        }

        private static string SameKey(Diag d)
        {
            return d.Sev + "|" + d.Code + "|" + d.Message;
        }

        private static LineBuilder Line(Doc doc, int indent, Role? bar)
        {
            var lb = new LineBuilder(doc, indent);
            if (bar != null) lb.Bar(bar.Value);
            return lb;
        }

        // ---- 未解決の外部シンボル ----

        private static void RenderUnresolved(Doc doc, RenderInput input, RenderOptions opt)
        {
            List<UnresolvedSym> syms = input.Syms;
            List<CauseGroup> groups = Diagnoser.Group(syms, input.Ctx);
            int total = syms.Count;

            new LineBuilder(doc).Rule().Space()
                .Add("■ 未解決の外部シンボル", Role.Error, true)
                .Add("  LNK2019 / LNK2001", Role.Code)
                .Add("   " + total + " 件を、原因 " + groups.Count + " 個にまとめました", Role.Dim)
                .Done();

            if (input.Report.LinkerUnresolvedTotal > 0)
                new LineBuilder(doc).Add("リンカーの集計 (LNK1120): " + input.Report.LinkerUnresolvedTotal + " 件", Role.Dim).Done();

            if (input.Pending)
                new LineBuilder(doc).Add("ソリューションの .lib とソースを検索中です。終わると、原因の分類が更新されます…", Role.Hint, false, true).Done();
            else if (!string.IsNullOrEmpty(input.Ctx.SolutionDir))
                new LineBuilder(doc).Add("検索範囲: " + input.Ctx.SolutionDir + " の下の .lib と、ソース " + SourceScanner.FilesScanned + " ファイル", Role.Dim).Done();

            int gi = 0;
            foreach (CauseGroup g in groups)
            {
                gi++;
                Line(doc, 0, Role.Error).Space()
                    .Add("原因 " + gi + " / " + groups.Count + "   ", Role.Dim)
                    .Add(g.Title, Role.Error, true)
                    .Add("   " + g.Items.Count + " 件", Role.Dim)
                    .Done();

                foreach (string e in g.Explain)
                    Line(doc, 1, Role.Error).Add(e, Role.Normal).Done();

                if (g.Remedies.Count > 0)
                {
                    Line(doc, 1, Role.Error).Add("対処", Role.Hint, true).Done();
                    int n = 0;
                    foreach (string r in g.Remedies)
                        Line(doc, 2, Role.Error).Add(++n + ". ", Role.Hint).Add(r, Role.Normal).Done();
                }

                Line(doc, 1, Role.Error).Add("該当するシンボル", Role.Hint, true).Done();
                foreach (UnresolvedSym s in g.Items)
                    AddSymbol(doc, s, opt, input.Ctx, g);
            }
        }

        private static void AddSymbol(Doc doc, UnresolvedSym s, RenderOptions opt, AnalysisContext ctx, CauseGroup g)
        {
            SymInfo info = s.Info;
            var lb = Line(doc, 2, Role.Error);
            lb.Add("✖ ", Role.Error).Code(info.Pretty);
            if (info.KindLabel.Length > 0) lb.Add("   " + info.KindLabel, Role.Dim);
            if (info.Import) lb.Add("  dllimport", Role.Dim);
            string term = SearchTerm(info);
            if (term.Length > 0) lb.Add("   ", Role.Normal).SearchLink("[宣言を検索]", term);
            lb.Done();

            if (info.Note.Length > 0)
                Line(doc, 3, Role.Error).Add(info.Note, Role.Dim, false, true).Done();

            // 参照元(同じ関数・同じ obj は 1 つにまとめる)
            var seen = new HashSet<string>();
            int shown = 0, hidden = 0;
            foreach (RefSite r in s.Refs)
            {
                string key = (r.From != null ? r.From.Pretty : "") + "|" + r.Obj;
                if (!seen.Add(key)) continue;
                if (shown >= 3) { hidden++; continue; }
                shown++;
                var rb = Line(doc, 3, Role.Error).Add("← ", Role.Dim);
                if (r.From != null) AddFuncRef(rb, r.From);
                else rb.Add("(参照元の関数は不明)", Role.Dim);
                if (r.Obj.Length > 0) rb.Add("   " + r.Obj, Role.Dim);
                rb.Done();
            }
            if (hidden > 0) Line(doc, 3, Role.Error).Add("   ほか " + hidden + " か所から参照されています", Role.Dim).Done();

            // ソースから見つかった定義の候補
            if (s.Defs != null)
                foreach (SrcHit h in s.Defs)
                {
                    string text = h.Text.Length > 90 ? h.Text.Substring(0, 90) + "…" : h.Text;
                    Line(doc, 3, Role.Error).Add("定義の候補: ", Role.Good)
                        .Link(Paths.Display(h.File, ctx.SolutionDir) + "(" + h.Line + ")", h.File, h.Line, 0)
                        .Add("   " + text, Role.Dim).Done();
                }

            if (opt.AttachRaw)
            {
                Line(doc, 3, Role.Error).Add(s.Info.Raw, Role.Dim).Done();
                Line(doc, 3, Role.Error).Add(s.Mangled, Role.Dim).Done();
            }
        }

        private static void AddFuncRef(LineBuilder rb, SymInfo from)
        {
            if (from.Kind == SymKind.Lambda)
            {
                int n;
                bool numeric = int.TryParse(from.LambdaId, out n);
                rb.Add("ラムダ" + (numeric ? " #" + from.LambdaId : "") + " in ", Role.Dim);
            }
            rb.Code(from.Pretty);
            if (from.Note.Length > 0) rb.Add("  (" + from.Note + ")", Role.Dim);
        }

        private static string SearchTerm(SymInfo info)
        {
            string n = info.Name ?? "";
            int lt = n.IndexOf('<');
            if (lt > 0) n = n.Substring(0, lt);
            n = n.TrimStart('~');
            if (n.StartsWith("`", StringComparison.Ordinal) || n.StartsWith("operator", StringComparison.Ordinal) || n.Length == 0)
            {
                string c = info.Class ?? "";
                lt = c.IndexOf('<');
                if (lt > 0) c = c.Substring(0, lt);
                return c;
            }
            return n;
        }

        // ---- 二重定義・設定の不一致 ----

        private static void RenderMultiDef(Doc doc, Diag d, RenderOptions opt, string sol)
        {
            MultiDefRef m = d.MultiDef;
            SymInfo info = SymbolPretty.Parse(m.SymbolDem, m.SymbolMangled);
            Header(doc, d, "同じシンボルが二重に定義されています", sol);
            Line(doc, 1, null).Add("シンボル: ", Role.Dim).Code(info.Pretty).Done();
            Line(doc, 1, null).Add("定義の場所: ", Role.Dim).Add(m.InObj, Role.Type).Add("  と  ", Role.Dim).Add(m.OtherObj, Role.Type).Done();
            AddHintText(doc, Hints.For(d.Code), 1);
            bool isVar = info.Kind == SymKind.Variable || info.Kind == SymKind.StaticVariable;
            if (isVar)
                Line(doc, 1, null).Add("多くは、ヘッダーに変数を書いた (extern が付いていない) ことが原因です。ヘッダーには extern を付けた宣言だけを書き、定義は 1 つの .cpp に書きます。C++17 なら、ヘッダーに inline 変数として書けます。", Role.Normal).Done();
            else
                Line(doc, 1, null).Add("多くは、ヘッダーに関数の本体を書いた (inline が付いていない) ことが原因です。inline を付けるか、本体を .cpp に移します。", Role.Normal).Done();
            if (opt.AttachRaw) AddRaw(doc, d, 1);
        }

        private static void RenderMismatch(Doc doc, Diag d, RenderOptions opt, string sol)
        {
            MismatchRef m = d.Mismatch;
            Header(doc, d, "設定の不一致: " + m.Key, sol);
            Line(doc, 1, null).Add(m.InObj, Role.Type).Add("   → ", Role.Dim).Add(Hints.DescribeMismatch(m.Key, m.ValueHere), Role.Warning).Done();
            Line(doc, 1, null).Add(m.OtherObj.Length > 0 ? m.OtherObj : "(もう一方)", Role.Type).Add("   → ", Role.Dim).Add(Hints.DescribeMismatch(m.Key, m.ValueOther), Role.Warning).Done();
            if (m.Key == "RuntimeLibrary")
                Line(doc, 1, null).Add("対処: ", Role.Hint, true)
                    .Add("すべてのプロジェクトと、リンクする .lib を、同じランタイム ライブラリにそろえます (C/C++ > コード生成 > ランタイム ライブラリ)。", Role.Normal).Done();
            else if (m.Key == "_ITERATOR_DEBUG_LEVEL")
                Line(doc, 1, null).Add("対処: ", Role.Hint, true)
                    .Add("Debug 用と Release 用のライブラリが混ざっています。構成に合った .lib を使います。", Role.Normal).Done();
            else
                AddHintText(doc, Hints.For(d.Code), 1);
            if (opt.AttachRaw) AddRaw(doc, d, 1);
        }

        // ---- 普通のエラー・警告 ----

        private static void Header(Doc doc, Diag d, string title, string sol)
        {
            Role role = d.Sev == Sev.Error ? Role.Error : Role.Warning;
            var lb = new LineBuilder(doc).Rule().Space();
            lb.Add(d.Sev == Sev.Error ? "✖ " : "⚠ ", role);
            if (d.Code.Length > 0) lb.Add(d.Code, Role.Code, true).Add("  ", Role.Normal);
            lb.Add(title, role, true);
            if (Regex.IsMatch(d.Code, @"^[A-Z]{1,4}\d{3,5}$"))
                lb.Add("  ", Role.Normal).UrlLink("[詳細]", "https://learn.microsoft.com/ja-jp/search/?terms=" + d.Code);
            if (d.Project.Length > 0) lb.Add("   [" + d.Project + "]", Role.Dim);
            lb.Done();

            if (d.HasLocation)
            {
                string disp = Paths.Display(d.File, sol) + (d.Col > 0 ? "(" + d.Line + "," + d.Col + ")" : "(" + d.Line + ")");
                Line(doc, 1, null).Link(disp, d.File, d.Line, d.Col).Done();
            }
            else if (d.File.Length > 0 && !d.IsLinker)
            {
                Line(doc, 1, null).Add(d.File, Role.Dim).Done();
            }
        }

        private static void AddHintText(Doc doc, Hint h, int indent)
        {
            if (h == null || !ErrorLogSettings.ShowHints) return;
            Line(doc, indent, null).Add("ヒント: ", Role.Hint, true).Add(h.Text, Role.Normal).Done();
        }

        private static void AddRaw(Doc doc, Diag d, int indent)
        {
            foreach (string r in d.Raw)
                Line(doc, indent, null).Add(r, Role.Dim).Done();
        }

        private static void RenderGeneric(Doc doc, Diag d, RenderOptions opt, string sol, List<Diag> same)
        {
            Hint hint = Hints.For(d.Code);
            bool known = hint != null;
            if (!known) hint = Hints.Fallback(d.Sev);
            if (d.Code == "C2220" && !known) hint = Hints.For("C2220");
            string title = known || d.Code == "C2220" ? hint.Title : (d.Sev == Sev.Error ? "エラー" : "警告");
            Header(doc, d, title, sol);

            Role baseRole = d.Sev == Sev.Error ? Role.Normal : Role.Dim;
            if (d.Message.Length > 0)
                Line(doc, 1, null).Message(d.Message, baseRole).Done();

            string cascadeNote;
            if (_cascade.TryGetValue(d, out cascadeNote))
                Line(doc, 1, null).Add("連鎖の可能性: ", Role.Warning, true).Add(cascadeNote, Role.Dim).Done();

            if (d.Code == "C2220") AddWarningsAsErrors(doc, d, sol);

            AddSnippet(doc, d, sol);
            AddSameLocations(doc, d, same, sol);

            // 足りない #include
            IncludeAdvisor.Suggestion sug = IncludeAdvisor.Suggest(d);
            if (sug != null)
                Line(doc, 1, null).Add("足りない #include の候補: ", Role.Good, true)
                    .Add(sug.Display, Role.Type, true).Add("   (" + sug.Name + " を使うには)", Role.Dim).Done();

            // 足りないファイル(include、.lib)がソリューションの下にあるか
            AddFound(doc, d, sol);

            // 型の変換: 渡した型と、期待する型
            AddConversion(doc, d);

            // テンプレート引数 (with [ _Ty=int ])
            AddTemplateArgs(doc, d);

            // 原因の場所
            Frame userFrame = FindUserFrame(d, sol);
            bool insideLibrary = d.HasLocation && Paths.IsLibraryFile(d.File);
            if (insideLibrary && userFrame != null)
            {
                Line(doc, 1, null).Add("原因の場所: ", Role.Good, true)
                    .Link(Paths.Display(userFrame.File, sol) + "(" + userFrame.Line + ")", userFrame.File, userFrame.Line, userFrame.Col, true)
                    .Add("   エラーはライブラリの中で出ていますが、呼び出している自分のコードの場所はここです。", Role.Dim).Done();
            }
            else if (insideLibrary)
            {
                Line(doc, 1, null).Add("エラーはライブラリの中で出ています。下の「経路」をたどると、自分のコードの場所が分かります。", Role.Dim).Done();
            }

            AddTrace(doc, d, opt, sol);
            AddCandidates(doc, d, sol);
            AddDecls(doc, d, sol);
            AddNotes(doc, d);
            string specific = Hints.Specific(d);
            if (specific != null && ErrorLogSettings.ShowHints)
                Line(doc, 1, null).Add("このエラー: ", Role.Hint, true).Add(specific, Role.Normal).Done();
            // 名前入りの説明が、一般のヒントを含んでいるコードは、一般のヒントを省く(同じ文の繰り返しを減らす)
            bool specificCoversHint = specific != null && (d.Code == "C2065" || d.Code == "C3861" || d.Code == "C2039");
            if (!specificCoversHint) AddHintText(doc, hint, 1);
            AddExample(doc, hint);
            if (opt.AttachRaw) AddRaw(doc, d, 1);
        }

        private static readonly HashSet<string> NoteCodes = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "C2259", "C2280", "C2248", "C2512", "C2338", "C2440"
        };

        /// <summary>note の行のうち、原因を言っているもの(足りない純粋仮想関数、削除された理由など)を出す。</summary>
        private static void AddNotes(Doc doc, Diag d)
        {
            if (!NoteCodes.Contains(d.Code)) return;
            var notes = d.Frames.Where(f => f.Kind == FrameKind.Reason && f.Message.Length > 0).Take(6).ToList();
            if (notes.Count == 0) return;
            Line(doc, 1, null).Add("補足", Role.Hint, true).Done();
            foreach (Frame f in notes)
                Line(doc, 2, null).Message(f.Message, Role.Dim).Done();
        }

        private static void AddExample(Doc doc, Hint h)
        {
            if (h == null || string.IsNullOrEmpty(h.Example) || !ErrorLogSettings.ShowHints || !ErrorLogSettings.ShowExamples) return;
            Line(doc, 1, null).Add("例", Role.Hint, true).Done();
            foreach (string line in h.Example.Split('\n'))
                Line(doc, 2, null).Add(line, Role.Code).Done();
        }

        /// <summary>C2220(警告がエラー扱い)のとき、同じファイルの、原因の警告を出す。</summary>
        private static void AddWarningsAsErrors(Doc doc, Diag d, string sol)
        {
            if (_report == null) return;
            var causes = _report.Diags.Where(w => w.Sev == Sev.Warning && string.Equals(w.File, d.File, StringComparison.OrdinalIgnoreCase)
                                                    && (w.ProjectNo == d.ProjectNo)).Take(8).ToList();
            Line(doc, 1, null).Add("原因の警告", Role.Hint, true).Done();
            if (causes.Count == 0)
            {
                Line(doc, 2, null).Add("(この出力には、見つかりませんでした。上の警告を探します)", Role.Dim).Done();
                return;
            }
            foreach (Diag w in causes)
            {
                var lb = Line(doc, 2, null).Add(w.Code + "  ", Role.Code, true);
                if (w.HasLocation) lb.Link(Paths.Display(w.File, sol) + "(" + w.Line + ")", w.File, w.Line, w.Col).Add("   ", Role.Normal);
                lb.Message(w.Message, Role.Dim).Done();
            }
        }

        private static readonly HashSet<string> SyntaxCodes = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "C2143", "C2146", "C2059", "C2447", "C2144", "C2181", "C3646", "C2061", "C2238", "C1004", "C1075", "C2001", "X3000", "C2628", "C2062"
        };

        private static string[] ReadLines(string path)
        {
            string[] lines;
            if (LineCache.TryGetValue(path, out lines)) return lines;
            try
            {
                var fi = new FileInfo(path);
                lines = fi.Exists && fi.Length < 2 * 1024 * 1024 ? File.ReadAllLines(path) : null;
            }
            catch (Exception) { lines = null; }
            LineCache[path] = lines;
            return lines;
        }

        /// <summary>エラーの行のソースを、行番号つきで出す(構文エラーは、1 つ前の行も)。</summary>
        private static void AddSnippet(Doc doc, Diag d, string sol)
        {
            if (!d.HasLocation || !Paths.IsUserFile(d.File, sol)) return;
            string[] lines = ReadLines(d.File);
            if (lines == null || d.Line < 1 || d.Line > lines.Length) return;

            int prev = 0;
            if (SyntaxCodes.Contains(d.Code))
            {
                int p = d.Line - 1;
                while (p >= 1 && lines[p - 1].Trim().Length == 0) p--;
                if (p >= 1 && p < d.Line) prev = p;
            }
            if (prev > 0)
            {
                string t = lines[prev - 1].Trim();
                if (t.Length > 160) t = t.Substring(0, 160) + "…";
                Line(doc, 2, null).Add(prev.ToString().PadLeft(5) + " | ", Role.Dim).Add(t, Role.Dim).Done();
            }

            string raw = lines[d.Line - 1];
            string trimmed = raw.TrimStart();
            int lead = raw.Length - trimmed.Length;
            string shown = trimmed.TrimEnd();
            if (shown.Length > 160) shown = shown.Substring(0, 160) + "…";
            Line(doc, 2, null).Add(d.Line.ToString().PadLeft(5) + " | ", Role.Dim).Code(shown, false).Done();

            if (d.Col > 0 && raw.IndexOf('\t') < 0)
            {
                int col0 = d.Col - 1 - lead;
                if (col0 >= 0 && col0 < shown.Length)
                    Line(doc, 2, null).Add(new string(' ', 8 + col0) + "^", Role.Error, true).Done();
            }
        }

        private static void AddSameLocations(Doc doc, Diag d, List<Diag> same, string sol)
        {
            if (same == null || same.Count <= 1) return;
            Line(doc, 1, null).Add("同じ内容が、ほか " + (same.Count - 1) + " か所でも出ています", Role.Warning).Done();
            int n = 0;
            foreach (Diag o in same)
            {
                if (ReferenceEquals(o, d) || !o.HasLocation) continue;
                if (++n > 8) break;
                Line(doc, 2, null).Link(Paths.Display(o.File, sol) + "(" + o.Line + ")", o.File, o.Line, o.Col).Done();
            }
            if (same.Count - 1 > 8) Line(doc, 2, null).Add("… ほか " + (same.Count - 1 - 8) + " か所", Role.Dim).Done();
        }

        private static void AddFound(Doc doc, Diag d, string sol)
        {
            if (d.MissingName.Length == 0) return;
            bool isLib = d.Code.StartsWith("LNK", StringComparison.OrdinalIgnoreCase);
            string name = d.MissingName.Replace('/', '\\');
            while (name.StartsWith("..\\", StringComparison.Ordinal) || name.StartsWith(".\\", StringComparison.Ordinal))
                name = name.Substring(name.IndexOf('\\') + 1);

            if (d.Found.Count == 0)
            {
                if (_pending)
                    Line(doc, 1, null).Add("ソリューションの下で、" + d.MissingName + " を探しています…", Role.Hint, false, true).Done();
                else if (!string.IsNullOrEmpty(sol))
                    Line(doc, 1, null).Add(d.MissingName + " は、ソリューションの下には見つかりませんでした。導入(vcpkg など)の有無と、綴りを確かめます。", Role.Dim).Done();
                return;
            }

            Line(doc, 1, null).Add("見つかった場所", Role.Good, true).Done();
            foreach (string f in d.Found.Take(3))
                Line(doc, 2, null).Link(Paths.Display(f, sol), f, 0, 0).Done();

            string first = d.Found[0];
            string dir;
            try
            {
                dir = isLib
                    ? Path.GetDirectoryName(first)
                    : first.Substring(0, Math.Max(0, first.Length - (name.Length + 1)));
            }
            catch (Exception) { return; }
            if (string.IsNullOrEmpty(dir)) return;
            Line(doc, 1, null).Add("対処: ", Role.Hint, true)
                .Add(isLib ? "リンカー > 全般 > 追加のライブラリ ディレクトリ に " : "C/C++ > 全般 > 追加のインクルード ディレクトリ に ", Role.Normal)
                .Add(dir, Role.Type).Add(" を追加します。", Role.Normal).Done();
        }

        private static Frame FindUserFrame(Diag d, string sol)
        {
            if (d.HasLocation && Paths.IsUserFile(d.File, sol)) return null;   // 主エラー自体が自分のコード
            foreach (Frame f in d.Frames)
                if (f.Kind == FrameKind.Trace && f.HasLocation && Paths.IsUserFile(f.File, sol)) return f;
            foreach (Frame f in d.Frames)
                if (f.HasLocation && Paths.IsUserFile(f.File, sol)) return f;
            return null;
        }

        private static readonly Regex ConvArgEn = new Regex(@"cannot convert argument (?<n>\d+) from '(?<a>.+?)' to '(?<b>.+?)'", RegexOptions.Compiled);
        private static readonly Regex ConvArgJa = new Regex(@"引数 (?<n>\d+) を '(?<a>.+?)' から '(?<b>.+?)' に変換できません", RegexOptions.Compiled);
        private static readonly Regex ConvEn = new Regex(@"cannot convert from '(?<a>.+?)' to '(?<b>.+?)'", RegexOptions.Compiled);
        private static readonly Regex ConvJa = new Regex(@"'(?<a>[^']+?)' から '(?<b>[^']+?)' に変換できません", RegexOptions.Compiled);

        private static void AddConversion(Doc doc, Diag d)
        {
            var texts = new List<string> { d.Message };
            texts.AddRange(d.Frames.Select(f => f.Message));
            foreach (string t in texts)
            {
                Match m = ConvArgEn.Match(t);
                if (!m.Success) m = ConvArgJa.Match(t);
                bool hasArg = m.Success;
                if (!m.Success) m = ConvEn.Match(t);
                if (!m.Success) m = ConvJa.Match(t);
                if (!m.Success) continue;

                string a = MessageFormat.PrettyAny(m.Groups["a"].Value);
                string b = MessageFormat.PrettyAny(m.Groups["b"].Value);
                string label = hasArg ? "引数 " + m.Groups["n"].Value : "変換";
                Line(doc, 1, null).Add(label + "  ", Role.Hint, true).Add("渡した型    ", Role.Dim).Code(a).Done();
                Line(doc, 1, null).Add(new string(' ', label.Length + 2), Role.Normal).Add("期待する型  ", Role.Dim).Code(b).Done();
                if (a == b)
                    Line(doc, 1, null).Add(new string(' ', label.Length + 2), Role.Normal).Add("(型の名前は同じです。const・参照・名前空間・別のヘッダーの同名の型を疑います)", Role.Dim).Done();
                return;
            }
        }

        private static void AddTemplateArgs(Doc doc, Diag d)
        {
            var details = new List<string>(d.Details);
            foreach (Frame f in d.Frames) details.AddRange(f.Details);
            if (details.Count == 0) return;

            string text = string.Join(" ", details);
            text = Regex.Replace(text, @"\bwith\b|次の場合:?|\[|\]", " ");
            var pairs = new List<KeyValuePair<string, string>>();
            foreach (string part in TypePretty.SplitTop(text))
            {
                Match m = Regex.Match(part, @"^\s*(?<n>\w+)\s*=\s*(?<v>.+?)\s*$", RegexOptions.Singleline);
                if (m.Success) pairs.Add(new KeyValuePair<string, string>(m.Groups["n"].Value, m.Groups["v"].Value));
            }
            if (pairs.Count == 0) return;

            Line(doc, 1, null).Add("テンプレート引数", Role.Hint, true).Done();
            foreach (var kv in pairs.Take(8))
                Line(doc, 2, null).Add(kv.Key + " = ", Role.Dim).Code(TypePretty.Type(kv.Value)).Done();
        }

        // ---- 経路 ----

        private static readonly Regex TemplateKind = new Regex(
            @"(function template|class template|variable template|member function|alias template|関数 ?テンプレート|クラス ?テンプレート|変数 ?テンプレート|メンバー関数)",
            RegexOptions.Compiled | RegexOptions.IgnoreCase);

        /// <summary>引用符に囲まれた中身(関数・型)と、その種類の言葉を取り出す。</summary>
        private static bool ExtractQuoted(string msg, out string label, out string pretty)
        {
            label = "";
            pretty = "";
            int a = msg.IndexOf('\'');
            int b = msg.LastIndexOf('\'');
            if (a < 0 || b <= a) return false;
            string inner = msg.Substring(a + 1, b - a - 1);
            pretty = MessageFormat.PrettyAny(inner);
            Match k = TemplateKind.Match(msg);
            if (k.Success)
            {
                string w = k.Value.ToLowerInvariant().Replace(" ", "");
                if (w.Contains("function") && w.Contains("template") || w.StartsWith("関数")) label = "関数テンプレート";
                else if (w.Contains("class") || w.StartsWith("クラス")) label = "クラステンプレート";
                else if (w.Contains("variable") || w.StartsWith("変数")) label = "変数テンプレート";
                else if (w.Contains("member") || w.StartsWith("メンバー")) label = "メンバー関数";
                else label = "";
            }
            return true;
        }

        private static void AddTrace(Doc doc, Diag d, RenderOptions opt, string sol)
        {
            var trace = d.Frames.Where(f => f.Kind == FrameKind.Trace).ToList();
            if (trace.Count == 0) return;

            Line(doc, 1, null).Add("経路", Role.Hint, true)
                .Add(" (エラーの現場 → 呼び出し元)  " + trace.Count + " 段", Role.Dim).Done();

            // ライブラリの連続した段は、まとめる
            int i = 0;
            while (i < trace.Count)
            {
                Frame f = trace[i];
                bool user = f.HasLocation && Paths.IsUserFile(f.File, sol);
                if (user || opt.FullTrace || trace.Count <= 5)
                {
                    AddTraceLine(doc, f, user, sol);
                    i++;
                    continue;
                }
                int j = i;
                while (j < trace.Count && !(trace[j].HasLocation && Paths.IsUserFile(trace[j].File, sol))) j++;
                int run = j - i;
                if (run <= 2)
                {
                    for (int k = i; k < j; k++) AddTraceLine(doc, trace[k], false, sol);
                }
                else
                {
                    AddTraceLine(doc, trace[i], false, sol);
                    Line(doc, 2, null).Add("… ライブラリ内の " + (run - 2) + " 段を省略 (「経路を全部表示」で展開)", Role.Dim, false, true).Done();
                    AddTraceLine(doc, trace[j - 1], false, sol);
                }
                i = j;
            }
        }

        private static void AddTraceLine(Doc doc, Frame f, bool user, string sol)
        {
            var lb = Line(doc, 2, null);
            if (f.HasLocation)
            {
                string disp = Paths.Display(f.File, sol) + "(" + f.Line + ")";
                if (user) lb.Link(disp, f.File, f.Line, f.Col, true);
                else lb.Add(disp, Role.Dim);
            }
            lb.Add("   ", Role.Normal);
            string label, pretty;
            if (ExtractQuoted(f.Message, out label, out pretty))
            {
                if (label.Length > 0) lb.Add(label + " ", Role.Dim);
                lb.Code(pretty, false);
            }
            else
            {
                lb.Message(f.Message, Role.Dim);
            }
            lb.Done();
        }

        // ---- 候補・宣言 ----

        private static void AddCandidates(Doc doc, Diag d, string sol)
        {
            if (!d.Frames.Any(f => f.Kind == FrameKind.Candidate)) return;
            Line(doc, 1, null).Add("候補", Role.Hint, true).Add(" (どれにも合いませんでした。右は落ちた理由)", Role.Dim).Done();

            Frame candidate = null;
            foreach (Frame f in d.Frames)
            {
                if (f.Kind == FrameKind.Candidate)
                {
                    candidate = f;
                    var lb = Line(doc, 2, null).Add("・", Role.Dim);
                    string label, pretty;
                    if (ExtractQuoted(f.Message, out label, out pretty)) lb.Code(pretty, false);
                    else lb.Message(f.Message, Role.Normal);
                    if (f.HasLocation)
                        lb.Add("   ", Role.Normal).Link(Paths.Display(f.File, sol) + "(" + f.Line + ")", f.File, f.Line, f.Col);
                    lb.Done();
                }
                else if (f.Kind == FrameKind.Reason && candidate != null)
                {
                    Line(doc, 3, null).Message(f.Message, Role.Dim).Done();
                    foreach (string det in f.Details.Take(3))
                        Line(doc, 4, null).Add(det, Role.Dim).Done();
                }
            }
        }

        private static void AddDecls(Doc doc, Diag d, string sol)
        {
            var decls = d.Frames.Where(f => f.Kind == FrameKind.Decl && f.HasLocation).ToList();
            if (decls.Count == 0) return;
            Line(doc, 1, null).Add("関連する宣言", Role.Hint, true).Done();
            foreach (Frame f in decls.Take(5))
            {
                var lb = Line(doc, 2, null);
                lb.Link(Paths.Display(f.File, sol) + "(" + f.Line + ")", f.File, f.Line, f.Col).Add("   ", Role.Normal);
                string label, pretty;
                if (ExtractQuoted(f.Message, out label, out pretty)) lb.Code(pretty, false);
                else lb.Message(f.Message, Role.Dim);
                lb.Done();
            }
        }

        // =========================================================================
        // 原文(色つき)
        // =========================================================================

        private static void RenderRaw(Doc doc, RenderInput input, RenderOptions opt)
        {
            string sol = input.Ctx.SolutionDir;
            int n = 0;
            foreach (RawLine l in input.Report.RawLines)
            {
                if (l.Kind == RawKind.Warning && !opt.ShowWarnings) continue;
                if (++n > 20000)
                {
                    new LineBuilder(doc).Add("… 20000 行を超えたので、ここで切りました。", Role.Dim).Done();
                    break;
                }

                if (l.Kind == RawKind.ProjectHeader)
                {
                    new LineBuilder(doc).Rule().Add(l.Text, Role.Heading, true).Done();
                    continue;
                }
                if (l.Kind == RawKind.Summary)
                {
                    new LineBuilder(doc).Space().Add(l.Text, Role.Heading, true).Done();
                    continue;
                }
                if (l.Parsed != null)
                {
                    Frame f = l.Parsed;
                    var lb = new LineBuilder(doc);
                    if (f.HasLocation) lb.Link(f.Location, f.File, f.Line, f.Col);
                    else lb.Add(f.File, Role.Dim);
                    lb.Add(" : ", Role.Dim);
                    Role sevRole = f.Sev == Sev.Error ? Role.Error : f.Sev == Sev.Warning ? Role.Warning : Role.Note;
                    lb.Add(f.Sev == Sev.Error ? "error" : f.Sev == Sev.Warning ? "warning" : "note", sevRole, true);
                    if (f.Code.Length > 0) lb.Add(" " + f.Code, Role.Code, true);
                    lb.Add(": ", Role.Dim);
                    lb.Message(f.Message, f.Sev == Sev.Note ? Role.Dim : Role.Normal);
                    lb.Done();
                    continue;
                }
                if (l.Text.Length == 0) { new LineBuilder(doc).Add(" ", Role.Dim).Done(); continue; }
                bool indented = l.Text.Length > 0 && char.IsWhiteSpace(l.Text[0]);
                new LineBuilder(doc).Add(l.Text, indented ? Role.Dim : Role.Normal).Done();
            }
        }
    }
}
