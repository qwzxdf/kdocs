using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace KErrorLog
{
    /// <summary>
    /// 「出力」ウィンドウのビルド欄の文字を、エラーごとに分ける。
    /// MSVC(英語・日本語)の形式に加えて、GCC / Clang の形式と、リンカー(LNK)の未解決シンボル・二重定義・設定の不一致を読む。
    /// </summary>
    public static class BuildLogParser
    {
        // MSVC: C:\path\file.cpp(12,5): error C2664: メッセージ
        private static readonly Regex Msvc = new Regex(
            @"^(?<file>.+?)\((?<line>\d+)(?:,(?<col>\d+))?(?:,\d+,\d+)?\)\s*:\s*(?<sev>fatal error|error|warning|note|message)\b\s*(?<code>[A-Za-z]{1,4}\d{3,5})?\s*:?\s*(?<msg>.*)$",
            RegexOptions.Compiled);

        // 行番号のない診断: LINK : fatal error LNK1104: ... / foo.obj : error LNK2019: ...
        private static readonly Regex NoLine = new Regex(
            @"^(?<file>.+?)\s:\s*(?<sev>fatal error|error|warning)\s+(?<code>[A-Za-z]{1,4}\d{3,5})\s*:\s*(?<msg>.*)$",
            RegexOptions.Compiled);

        // GCC / Clang: /path/file.cpp:12:5: error: メッセージ
        private static readonly Regex Gcc = new Regex(
            @"^(?<file>(?:[A-Za-z]:)?[^:]+):(?<line>\d+):(?:(?<col>\d+):)?\s*(?<sev>fatal error|error|warning|note):\s*(?<msg>.*)$",
            RegexOptions.Compiled);

        private static readonly Regex GccTrace = new Regex(
            @"^(?<file>(?:[A-Za-z]:)?[^:]+):(?<line>\d+):(?:(?<col>\d+):)?\s+(?<msg>(?:required from|in instantiation of).*)$",
            RegexOptions.Compiled | RegexOptions.IgnoreCase);

        private static readonly Regex Prefix = new Regex(@"^\s*(\d+)>", RegexOptions.Compiled);

        private static readonly Regex ProjHeader = new Regex(
            @"-{3,}.*?(?:プロジェクト|Project):\s*(?<proj>[^,]+?)\s*,\s*(?:構成|Configuration):\s*(?<cfg>.+?)\s*-{3,}",
            RegexOptions.Compiled);

        // lld-link / ld.lld: "lld-link: error: undefined symbol: foo" のあとに、">>> referenced by ..." が続く
        private static readonly Regex LldUndef = new Regex(
            @"^(?<tool>[^\s:]*(?:lld|ld|link)[^\s:]*):\s*error:\s*undefined symbol:\s*(?<sym>.+)$", RegexOptions.Compiled);
        private static readonly Regex LldRef = new Regex(
            @"^>>>\s*referenced by\s+(?<by>.+)$", RegexOptions.Compiled);
        private static readonly Regex LldRefObjFunc = new Regex(
            @"^(?<obj>\S+?):\((?<fn>.*)\)$", RegexOptions.Compiled);

        // GNU ld: "main.o: in function `main':" と、"main.cpp:(.text+0x10): undefined reference to `foo(int)'"
        private static readonly Regex LdFunc = new Regex(
            @"^(?:.*?ld[^\s:]*:\s*)?(?<obj>\S+?\.(?:o|obj|a(?:\([^)]*\))?)):\s*in function [`'‘](?<fn>.+?)['’]:?$", RegexOptions.Compiled);
        private static readonly Regex LdUndef = new Regex(
            @"^(?:.*?ld[^\s:]*:\s*)?(?<loc>.+?):(?:\((?<sec>[^)]*)\)|\d+)(?::\s*|\s)undefined reference to [`'‘](?<sym>.+)['’]$", RegexOptions.Compiled);

        private static readonly Regex QuotedFirst = new Regex(@"'(?<n>[^']+)'", RegexOptions.Compiled);
        private static readonly Regex GccNoFile = new Regex(@"^(?<n>\S+): No such file", RegexOptions.Compiled);

        private static readonly Regex SummaryLine = new Regex(@"^={5,}\s*(?<s>.*?)\s*={5,}$", RegexOptions.Compiled);

        public static BuildReport Parse(string text)
        {
            var report = new BuildReport { RawText = text ?? "" };
            if (string.IsNullOrEmpty(text)) return report;

            var seen = new HashSet<string>();
            Diag current = null;
            Frame last = null;
            bool skipping = false;
            string ldObj = "", ldFunc = "";

            foreach (string rawLine in text.Split('\n'))
            {
                string line = rawLine.TrimEnd('\r');
                int projNo = 0;
                Match pm = Prefix.Match(line);
                if (pm.Success)
                {
                    int.TryParse(pm.Groups[1].Value, out projNo);
                    line = line.Substring(pm.Length);
                }
                line = line.TrimEnd(' ', '\t');

                var raw = new RawLine { Text = line };
                report.RawLines.Add(raw);

                Match hm = ProjHeader.Match(line);
                if (hm.Success)
                {
                    report.Projects[projNo] = hm.Groups["proj"].Value.Trim();
                    report.Config = hm.Groups["cfg"].Value.Trim();
                    raw.Kind = RawKind.ProjectHeader;
                    current = null; last = null; skipping = false;
                    continue;
                }
                Match sm = SummaryLine.Match(line);
                if (sm.Success)
                {
                    report.Summary = sm.Groups["s"].Value;
                    raw.Kind = RawKind.Summary;
                    current = null; last = null; skipping = false;
                    continue;
                }

                // lld の続きの行(">>> referenced by foo.obj:(func)")
                if (current != null && current.Kind == DiagKind.Unresolved && line.StartsWith(">>>", StringComparison.Ordinal))
                {
                    if (!skipping) { AddLldRef(current, line); current.Raw.Add(line); }
                    raw.Kind = RawKind.Normal;
                    continue;
                }

                // GNU ld
                Match ldf = LdFunc.Match(line);
                if (ldf.Success)
                {
                    ldObj = ldf.Groups["obj"].Value;
                    ldFunc = ldf.Groups["fn"].Value;
                    current = null; last = null; skipping = false;
                    continue;
                }
                Match ldu = LdUndef.Match(line);
                Match lldu = ldu.Success ? null : LldUndef.Match(line);
                if (ldu.Success || (lldu != null && lldu.Success))
                {
                    var f2 = new Frame { Sev = Sev.Error, Message = line };
                    raw.Parsed = f2;
                    raw.Kind = RawKind.Error;
                    raw.Linker = true;

                    var d2 = new Diag { ProjectNo = projNo, Sev = Sev.Error, Message = line, Kind = DiagKind.Unresolved };
                    var r2 = new UnresolvedRef();
                    if (ldu.Success)
                    {
                        r2.SymbolDem = r2.SymbolMangled = ldu.Groups["sym"].Value;
                        r2.FromObj = ldObj.Length > 0 ? ldObj : ldu.Groups["loc"].Value;
                        r2.FuncDem = r2.FuncMangled = ldFunc;
                        d2.File = r2.FromObj;
                    }
                    else
                    {
                        r2.SymbolDem = r2.SymbolMangled = lldu.Groups["sym"].Value.Trim();
                        d2.File = lldu.Groups["tool"].Value;
                    }
                    d2.Unresolved = r2;
                    f2.File = d2.File;
                    string key2 = projNo + "|" + DedupKey(d2);
                    skipping = !seen.Add(key2);
                    if (skipping) { current = null; last = null; continue; }
                    d2.Raw.Add(line);
                    report.Diags.Add(d2);
                    current = d2;
                    last = null;
                    continue;
                }

                Frame f = ParseLine(line);
                if (f != null)
                {
                    raw.Parsed = f;
                    raw.Linker = f.Code.StartsWith("LNK", StringComparison.OrdinalIgnoreCase);
                    raw.Kind = f.Sev == Sev.Error ? RawKind.Error : f.Sev == Sev.Warning ? RawKind.Warning : RawKind.Note;

                    bool primary = f.Sev == Sev.Error || f.Sev == Sev.Warning;
                    if (primary)
                    {
                        Diag d = MakeDiag(f, projNo, report);
                        string key = projNo + "|" + DedupKey(d);
                        skipping = !seen.Add(key);
                        if (skipping) { current = null; last = null; continue; }
                        d.Raw.Add(line);
                        report.Diags.Add(d);
                        current = d;
                        last = null;
                        if (d.Code == "LNK1120") report.LinkerUnresolvedTotal = ParseTotal(d.Message);
                    }
                    else if (current != null && !skipping)
                    {
                        f.Kind = Classify(f.Message);
                        current.Frames.Add(f);
                        current.Raw.Add(line);
                        last = f;
                    }
                    continue;
                }

                // インデントされた補足行("with" や "[ _Ty=int ]" など)
                if (current != null && !skipping && line.Length > 0 && char.IsWhiteSpace(rawLine.Length > pm.Length ? rawLine[pm.Length] : 'x') && line.Trim().Length > 0)
                {
                    current.Raw.Add(line);
                    if (last != null) last.Details.Add(line.Trim());
                    else current.Details.Add(line.Trim());
                    continue;
                }

                // インデントのない普通の行(「Main.cpp」「Generating Code...」など)でグループを閉じる
                current = null;
                last = null;
                skipping = false;
            }

            foreach (Diag d in report.Diags)
                if (d.ProjectNo > 0 && report.Projects.ContainsKey(d.ProjectNo)) d.Project = report.Projects[d.ProjectNo];
            return report;
        }

        private static void AddLldRef(Diag d, string line)
        {
            Match m = LldRef.Match(line);
            if (!m.Success || d.Unresolved == null) return;
            string by = m.Groups["by"].Value.Trim();
            string obj = by, fn = "";
            Match of = LldRefObjFunc.Match(by);
            if (of.Success) { obj = of.Groups["obj"].Value; fn = of.Groups["fn"].Value; }
            UnresolvedRef r = d.Unresolved;
            if (r.FromObj.Length == 0 && r.FuncDem.Length == 0)
            {
                r.FromObj = obj;
                r.FuncDem = r.FuncMangled = fn;
            }
            else
            {
                r.More.Add(new KeyValuePair<string, string>(obj, fn));
            }
        }

        private static string ExtractMissing(Diag d)
        {
            if (d.Code == "C1083" || d.Code == "LNK1104" || d.Code == "LNK1181")
            {
                Match m = QuotedFirst.Match(d.Message);
                return m.Success ? m.Groups["n"].Value : "";
            }
            if (d.Code.Length == 0)
            {
                Match m = GccNoFile.Match(d.Message);
                return m.Success ? m.Groups["n"].Value : "";
            }
            return "";
        }

        private static string DedupKey(Diag d)
        {
            if (d.Kind == DiagKind.Unresolved)
                return d.Code + "|" + d.Unresolved.SymbolMangled + "|" + d.Unresolved.FuncMangled + "|" + d.Unresolved.FromObj;
            return d.File + "|" + d.Line + "|" + d.Col + "|" + d.Code + "|" + d.Message;
        }

        private static int ParseTotal(string msg)
        {
            Match m = Regex.Match(msg, @"(\d+)");
            int n;
            return m.Success && int.TryParse(m.Groups[1].Value, out n) ? n : 0;
        }

        private static Frame ParseLine(string line)
        {
            // 経路の行("note: see reference to ...")は、インデントされて出ることがあるので、先頭の空白は許す
            if (line.Length == 0) return null;
            Match m = Msvc.Match(line);
            if (m.Success) return Make(m, true);
            m = NoLine.Match(line);
            if (m.Success) return Make(m, false);
            m = GccTrace.Match(line);
            if (m.Success)
            {
                Frame t = Make(m, true);
                t.Sev = Sev.Note;
                return t;
            }
            m = Gcc.Match(line);
            if (m.Success) return Make(m, true);
            return null;
        }

        private static Frame Make(Match m, bool hasLine)
        {
            var f = new Frame
            {
                File = m.Groups["file"].Value.Trim(),
                Code = m.Groups["code"].Success ? m.Groups["code"].Value : "",
                Message = m.Groups["msg"].Value.Trim()
            };
            string sev = m.Groups["sev"].Success ? m.Groups["sev"].Value : "note";
            f.Sev = sev == "warning" ? Sev.Warning : (sev == "error" || sev == "fatal error") ? Sev.Error : Sev.Note;
            if (hasLine)
            {
                int line, col;
                if (int.TryParse(m.Groups["line"].Value, out line)) f.Line = line;
                if (m.Groups["col"].Success && int.TryParse(m.Groups["col"].Value, out col)) f.Col = col;
            }
            return f;
        }

        /// <summary>補足行の種類(経路・宣言・候補・理由)を、メッセージの文面で決める。英語と日本語の両方に対応する。</summary>
        public static FrameKind Classify(string message)
        {
            string l = (message ?? "").TrimStart();
            if (l.IndexOf("see declaration of", StringComparison.OrdinalIgnoreCase) >= 0
                || Regex.IsMatch(l, @"の宣言を(?:確認|参照)"))
                return FrameKind.Decl;

            if (l.IndexOf("see reference to", StringComparison.OrdinalIgnoreCase) >= 0
                || l.StartsWith("required from", StringComparison.OrdinalIgnoreCase)
                || l.StartsWith("in instantiation of", StringComparison.OrdinalIgnoreCase)
                || l.IndexOf("while compiling", StringComparison.OrdinalIgnoreCase) >= 0
                || l.IndexOf("being compiled", StringComparison.OrdinalIgnoreCase) >= 0
                || l.Contains("への参照") || l.Contains("の参照を")
                || (l.Contains("インスタンス化") && l.Contains("参照"))
                || l.Contains("をコンパイルしています") || l.Contains("コンパイル中"))
                return FrameKind.Trace;

            if (l.StartsWith("could be", StringComparison.OrdinalIgnoreCase)
                || l.StartsWith("or '", StringComparison.OrdinalIgnoreCase)
                || l.StartsWith("or ", StringComparison.OrdinalIgnoreCase)
                || l.StartsWith("candidate", StringComparison.OrdinalIgnoreCase)
                || l.StartsWith("または", StringComparison.Ordinal)
                || l.Contains("の可能性があります")
                || l.Contains("可能性があります"))
                return FrameKind.Candidate;

            return FrameKind.Reason;
        }

        // ---- 主エラー ----

        private static Diag MakeDiag(Frame f, int projNo, BuildReport report)
        {
            var d = new Diag
            {
                ProjectNo = projNo,
                Sev = f.Sev,
                Code = f.Code,
                File = f.File,
                Line = f.Line,
                Col = f.Col,
                Message = f.Message
            };
            if (d.IsLinker) ParseLinker(d);
            d.MissingName = ExtractMissing(d);
            return d;
        }

        private static readonly Regex UnresolvedHead = new Regex(
            @"^(?:unresolved external symbol|未解決の外部シンボル)\s+(?<rest>.*)$", RegexOptions.Compiled | RegexOptions.Singleline);
        private static readonly Regex FuncHead = new Regex(
            @"^\s*(?:referenced in function|が関数)\s+(?<fn>.*)$", RegexOptions.Compiled | RegexOptions.Singleline);
        private static readonly Regex QuotedSym = new Regex(
            @"^""(?<d>.*?)""\s*\((?<m>[^\s()]+)\)", RegexOptions.Compiled | RegexOptions.Singleline);
        private static readonly Regex AlreadyDefined = new Regex(
            @"^\s*(?:already defined in|は既に)\s+(?<o>\S+)", RegexOptions.Compiled);
        private static readonly Regex QuotedWord = new Regex(@"'([A-Za-z0-9_]+)'", RegexOptions.Compiled);
        private static readonly Regex ObjName = new Regex(@"(\S+\.(?:obj|lib|o|a))", RegexOptions.Compiled | RegexOptions.IgnoreCase);

        private static void ParseLinker(Diag d)
        {
            try
            {
                if (d.Code == "LNK2019" || d.Code == "LNK2001")
                {
                    Match h = UnresolvedHead.Match(d.Message);
                    if (!h.Success) return;
                    var r = new UnresolvedRef { FromObj = d.File };
                    string rest = ReadSymbol(h.Groups["rest"].Value, out r.SymbolDem, out r.SymbolMangled);
                    Match f = FuncHead.Match(rest);
                    if (f.Success) ReadSymbol(f.Groups["fn"].Value, out r.FuncDem, out r.FuncMangled);
                    if (r.SymbolMangled.Length == 0) return;
                    d.Unresolved = r;
                    d.Kind = DiagKind.Unresolved;
                }
                else if (d.Code == "LNK2005")
                {
                    var r = new MultiDefRef { InObj = d.File };
                    string rest = ReadSymbol(d.Message, out r.SymbolDem, out r.SymbolMangled);
                    Match a = AlreadyDefined.Match(rest);
                    if (a.Success) r.OtherObj = a.Groups["o"].Value;
                    if (r.SymbolMangled.Length == 0) return;
                    d.MultiDef = r;
                    d.Kind = DiagKind.MultiDefined;
                }
                else if (d.Code == "LNK2038")
                {
                    var qs = QuotedWord.Matches(d.Message).Cast<Match>().Select(x => x.Groups[1].Value).ToList();
                    if (qs.Count < 3) return;
                    var r = new MismatchRef { Key = qs[0], ValueHere = qs[1], ValueOther = qs[2], InObj = d.File };
                    Match o = ObjName.Match(d.Message);
                    if (o.Success) r.OtherObj = o.Groups[1].Value;
                    d.Mismatch = r;
                    d.Kind = DiagKind.Mismatch;
                }
            }
            catch (Exception) { /* 解釈できなければ、普通のエラーとして出す */ }
        }

        /// <summary>
        /// 「"demangled" (mangled)」または、引用符なしの名前を 1 つ読んで、残りの文字列を返す。
        /// </summary>
        private static string ReadSymbol(string s, out string dem, out string mangled)
        {
            s = s.TrimStart();
            dem = "";
            mangled = "";
            if (s.Length == 0) return "";
            if (s[0] == '"')
            {
                Match m = QuotedSym.Match(s);
                if (m.Success)
                {
                    dem = m.Groups["d"].Value;
                    mangled = m.Groups["m"].Value;
                    return s.Substring(m.Length);
                }
                int close = s.IndexOf('"', 1);
                if (close > 0)
                {
                    dem = s.Substring(1, close - 1);
                    mangled = dem;
                    return s.Substring(close + 1);
                }
            }
            int k = 0;
            while (k < s.Length && !char.IsWhiteSpace(s[k])) k++;
            dem = mangled = s.Substring(0, k);
            return s.Substring(k);
        }
    }
}
