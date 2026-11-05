using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

namespace KErrorLog
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
        public static Doc Render(RenderInput input, RenderOptions opt)
        {
            var doc = new Doc();
            BuildReport report = input.Report;
            if (report == null)
            {
                new LineBuilder(doc).Add("ビルドの出力はまだありません。ビルドすると、ここにエラーが出ます。", Role.Dim).Done();
                return doc;
            }
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
            int warnings = report.WarningCount;
            int linker = report.Diags.Count(d => d.Sev == Sev.Error && d.IsLinker);

            var head = new LineBuilder(doc);
            if (errors > 0)
            {
                head.Add("✖ ビルドに失敗しました", Role.Error, true);
                head.Add("   エラー " + errors + " 件", Role.Error);
                head.Add(" (リンカー " + linker + " / コンパイラ " + (errors - linker) + ")", Role.Dim);
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

            bool unresolvedDone = false;
            int shown = 0;
            foreach (Diag d in report.Diags)
            {
                if (d.Sev == Sev.Warning && !opt.ShowWarnings) continue;
                if (d.Code == "LNK1120" || d.Code == "LNK1169") continue;

                if (d.Kind == DiagKind.Unresolved)
                {
                    if (unresolvedDone) continue;
                    unresolvedDone = true;
                    RenderUnresolved(doc, input, opt);
                    shown++;
                    continue;
                }
                if (++shown > 400)
                {
                    new LineBuilder(doc).Space().Add("… 件数が多いので、ここから先は省略しました。「原文」表示で全部を読めます。", Role.Dim).Done();
                    break;
                }
                switch (d.Kind)
                {
                    case DiagKind.MultiDefined: RenderMultiDef(doc, d, opt, sol); break;
                    case DiagKind.Mismatch: RenderMismatch(doc, d, opt, sol); break;
                    default: RenderGeneric(doc, d, opt, sol); break;
                }
            }

            if (shown == 0 && errors == 0 && report.Diags.Count == 0)
                new LineBuilder(doc).Space().Add("出力にエラーも警告もありません。", Role.Dim).Done();
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
            if (h == null) return;
            Line(doc, indent, null).Add("ヒント: ", Role.Hint, true).Add(h.Text, Role.Normal).Done();
        }

        private static void AddRaw(Doc doc, Diag d, int indent)
        {
            foreach (string r in d.Raw)
                Line(doc, indent, null).Add(r, Role.Dim).Done();
        }

        private static void RenderGeneric(Doc doc, Diag d, RenderOptions opt, string sol)
        {
            Hint hint = Hints.For(d.Code);
            string title = hint != null ? hint.Title : (d.Sev == Sev.Error ? "エラー" : "警告");
            Header(doc, d, title, sol);

            Role baseRole = d.Sev == Sev.Error ? Role.Normal : Role.Dim;
            if (d.Message.Length > 0)
                Line(doc, 1, null).Message(d.Message, baseRole).Done();

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
            AddHintText(doc, hint, 1);
            if (opt.AttachRaw) AddRaw(doc, d, 1);
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
