using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using KHlsl.Vsix;
using Winterdom.Viasfora.Languages.BraceScanners;
using Winterdom.Viasfora.Languages.Sequences;
using Winterdom.Viasfora.Rainbow;
using Winterdom.Viasfora.Util;

/// <summary>
/// K-HLSL のレキサーと、Viasfora 自身の CBraceScanner / CStringScanner(DLL そのまま)の出力を突き合わせる。
/// </summary>
internal static class Program
{
    private static int _mismatches;
    private static int _checks;

    private static int Main(string[] args)
    {
        var files = new List<string>();
        foreach (var dir in args.Where(a => Directory.Exists(a)))
            files.AddRange(Directory.EnumerateFiles(dir, "*.*", SearchOption.AllDirectories)
                .Where(f => f.EndsWith(".hlsl", StringComparison.OrdinalIgnoreCase) || f.EndsWith(".hlsli", StringComparison.OrdinalIgnoreCase)
                         || f.EndsWith(".fx", StringComparison.OrdinalIgnoreCase) || f.EndsWith(".fxh", StringComparison.OrdinalIgnoreCase)));
        files.AddRange(args.Where(a => File.Exists(a)));
        Console.WriteLine("ファイル数: " + files.Count);

        foreach (var f in files)
        {
            string text;
            try { text = File.ReadAllText(f); } catch (Exception) { continue; }
            Compare(f, text, true);
        }
        Console.WriteLine("実ファイル: 照合 {0} 件、不一致 {1} 件", _checks, _mismatches);

        // ランダム入力(括弧: 全文字種、文字列: 引用符・バックスラッシュ・% など)
        int fileMismatches = _mismatches;
        var rnd = new Random(12345);
        string[] pieces = { "(", ")", "{", "}", "[", "]", "\"", "'", "\\", "/", "*", "//", "/*", "*/", "\n", "\r\n", " ", "a", "f", "u8", "x", "u", "U", "0", "9", "%", "%%", "%d", "\\n", "\\x41", "\\u0041", ";", "#include ", "<", ">", "if", "(1)", "{}", "\"%d\"", "'a'" };
        string[] strPieces = { "\"", "\\", "%", "%%", "d", "5", ".", "x", "u", "U", "A", "f", " ", "\n", "(", ")", "\\n", "\\x4", "\\u00", "%d", "%s", "a1", "\\\\", "//", "/*" };
        int fuzz = 0, fuzzBad = 0;
        for (int k = 0; k < 120000; k++)
        {
            var sb = new StringBuilder();
            int len = rnd.Next(1, 60);
            var set = k % 2 == 0 ? pieces : strPieces;
            for (int j = 0; j < len; j++) sb.Append(set[rnd.Next(set.Length)]);
            string t = sb.ToString();
            fuzz++;
            int before = _mismatches;
            Compare("fuzz#" + k, t, k % 2 == 0 ? true : false, k % 2 == 0);
            if (_mismatches != before) fuzzBad++;
        }
        Console.WriteLine("ランダム: {0} 件中、不一致 {1} 件", fuzz, fuzzBad);
        Console.WriteLine("合計の不一致: " + _mismatches);
        return _mismatches == 0 ? 0 : 1;
    }

    private static int _printed;

    private static void Report(string where, string what, string text, string detail)
    {
        _mismatches++;
        if (_printed++ < 12)
        {
            Console.WriteLine("--- 不一致 [{0}] {1}", where, what);
            Console.WriteLine("    " + detail);
            string show = text.Length > 160 ? text.Substring(0, 160) + "..." : text;
            Console.WriteLine("    入力: " + show.Replace("\r", "\\r").Replace("\n", "\\n"));
        }
    }

    private static void Compare(string where, string text, bool braces, bool strings = true)
    {
        var toks = KHlslLexer.Lex(text, Lexicon.Instance);
        if (braces)
        {
            _checks++;
            var theirs = ViasforaBraces(text);
            var mine = toks.Where(t => t.Kind >= Tk.Rainbow1 && t.Kind <= Tk.RainbowError)
                .Select(t => Tuple.Create(t.Start, t.Kind == Tk.RainbowError ? -1 : (int)(t.Kind - Tk.Rainbow1))).ToList();
            if (!theirs.SequenceEqual(mine))
            {
                int d = 0;
                while (d < theirs.Count && d < mine.Count && theirs[d].Equals(mine[d])) d++;
                string a = d < theirs.Count ? theirs[d].ToString() : "(なし)";
                string b = d < mine.Count ? mine[d].ToString() : "(なし)";
                Report(where, "レインボー括弧", text, "最初の相違 #" + d + "  Viasfora=" + a + "  K-HLSL=" + b + "  (件数 " + theirs.Count + " / " + mine.Count + ")");
            }
        }
        if (strings)
        {
            _checks++;
            var theirs = new List<Tuple<int, int, string>>();
            foreach (var lit in Literals(text))
            {
                string s = text.Substring(lit.Item1, lit.Item2 - lit.Item1);
                if (s.Length < 1) continue;
                var sc = new CStringScanner(s);
                StringPart? p;
                int guard = 0;
                while ((p = sc.Next()).HasValue && guard++ < 10000)
                {
                    var part = p.Value;
                    string kind = part.Type == StringPartType.EscapeSequence ? "Escape" : part.Type == StringPartType.FormatSpecifier ? "Format" : "Other";
                    theirs.Add(Tuple.Create(lit.Item1 + part.Span.Start, part.Span.Length, kind));
                }
            }
            var mine = toks.Where(t => t.Kind == Tk.Escape || t.Kind == Tk.Format)
                .Select(t => Tuple.Create(t.Start, t.Length, t.Kind == Tk.Escape ? "Escape" : "Format")).ToList();
            if (!theirs.SequenceEqual(mine))
            {
                int d = 0;
                while (d < theirs.Count && d < mine.Count && theirs[d].Equals(mine[d])) d++;
                string a = d < theirs.Count ? theirs[d].ToString() : "(なし)";
                string b = d < mine.Count ? mine[d].ToString() : "(なし)";
                Report(where, "エスケープ/書式指定子", text, "最初の相違 #" + d + "  Viasfora=" + a + "  K-HLSL=" + b + "  (件数 " + theirs.Count + " / " + mine.Count + ")");
            }
        }
    }

    // ---- Viasfora(括弧): CBraceScanner を行ごとに回し、TextBufferBraces.MatchBrace と同じ規則で数える ----
    private static List<Tuple<int, int>> ViasforaBraces(string text)
    {
        var res = new List<Tuple<int, int>>();
        var scanner = new CBraceScanner();
        scanner.Reset(0);
        var stack = new Stack<Tuple<char, int>>();
        int i = 0;
        while (true)
        {
            int nl = text.IndexOf('\n', i);
            int lineEnd = nl < 0 ? text.Length : nl;
            if (lineEnd > i && text[lineEnd - 1] == '\r') lineEnd--;
            if (lineEnd > i)
            {
                var sc = new StringChars(text, i, lineEnd);
                var cp = CharPos.Empty;
                while (!sc.AtEnd)
                {
                    if (scanner.Extract(sc, ref cp))
                    {
                        char c = cp.Char;
                        if (c == '(' || c == '[' || c == '{')
                        {
                            res.Add(Tuple.Create(cp.Position, stack.Count % 4));
                            stack.Push(Tuple.Create(c, stack.Count));
                        }
                        else if (stack.Count > 0)
                        {
                            var top = stack.Peek();
                            char want = top.Item1 == '(' ? ')' : top.Item1 == '[' ? ']' : '}';
                            if (want == c) { stack.Pop(); res.Add(Tuple.Create(cp.Position, top.Item2 % 4)); }
                            else res.Add(Tuple.Create(cp.Position, -1));
                        }
                        else res.Add(Tuple.Create(cp.Position, -1));
                    }
                }
            }
            if (nl < 0) break;
            i = nl + 1;
        }
        return res;
    }

    // ---- 文字列リテラルの範囲(下の色付けが「文字列」と判定する範囲の代わり) ----
    private static List<Tuple<int, int>> Literals(string t)
    {
        var res = new List<Tuple<int, int>>();
        int n = t.Length, i = 0;
        while (i < n)
        {
            char c = t[i];
            if (c == '/' && i + 1 < n && t[i + 1] == '*')
            {
                int e = t.IndexOf("*/", i + 2, StringComparison.Ordinal);
                i = e < 0 ? n : e + 2;
                continue;
            }
            if (c == '/' && i + 1 < n && t[i + 1] == '/')
            {
                int e = t.IndexOf('\n', i);
                i = e < 0 ? n : e;
                continue;
            }
            if (c == '#')
            {
                // #include <...> は、下の色付けでは、ひとまとまりの文字列(中の引用符は数えない)
                int ls = i - 1;
                bool lineStart = true;
                while (ls >= 0 && t[ls] != '\n') { if (t[ls] != ' ' && t[ls] != '\t' && t[ls] != '\r') { lineStart = false; break; } ls--; }
                if (lineStart)
                {
                    int q = i + 1;
                    while (q < n && (t[q] == ' ' || t[q] == '\t')) q++;
                    if (string.CompareOrdinal(t, q, "include", 0, 7) == 0)
                    {
                        q += 7;
                        while (q < n && (t[q] == ' ' || t[q] == '\t')) q++;
                        if (q < n && t[q] == '<')
                        {
                            int r = q + 1;
                            while (r < n && t[r] != '>' && t[r] != '\n' && t[r] != '\r') r++;
                            if (r < n && t[r] == '>') r++;
                            i = r;
                            continue;
                        }
                    }
                }
            }
            if (c == '"' || c == '\'')
            {
                int j = i + 1;
                while (j < n && t[j] != '\n' && t[j] != '\r')
                {
                    if (t[j] == '\\') { if (j + 1 >= n || t[j + 1] == '\n' || t[j + 1] == '\r') { j++; break; } j += 2; continue; }
                    if (t[j] == c) { j++; break; }
                    j++;
                }
                res.Add(Tuple.Create(i, Math.Min(j, n)));
                i = Math.Min(j, n);
                continue;
            }
            i++;
        }
        return res;
    }
}
