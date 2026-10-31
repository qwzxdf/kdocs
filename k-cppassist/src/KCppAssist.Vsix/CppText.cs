using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>cpp の文字を読む小さな道具。コメントや文字列を除いた文字を作り、識別子が「型として使われているか」を見る。VS に依存しない。</summary>
    internal static class CppText
    {
        /// <summary>
        /// コメント・文字列・文字リテラルと、「#」で始まる行(継続行を含む)を空白に置き換える。
        /// 長さと改行の位置は変えないので、元の文字と位置がそのまま対応する。
        /// </summary>
        public static string Mask(string s)
        {
            var r = s.ToCharArray();
            int n = s.Length;
            bool lineStart = true;
            int i = 0;
            while (i < n)
            {
                char c = s[i];
                if (c == '\n') { lineStart = true; i++; continue; }
                if (c == ' ' || c == '\t' || c == '\r') { i++; continue; }

                if (lineStart && c == '#')
                {
                    while (i < n)
                    {
                        if (s[i] == '\n')
                        {
                            bool cont = (i > 0 && s[i - 1] == '\\') || (i > 1 && s[i - 1] == '\r' && s[i - 2] == '\\');
                            if (cont) { i++; continue; }
                            break;
                        }
                        if (s[i] != '\r') r[i] = ' ';
                        i++;
                    }
                    continue;
                }
                lineStart = false;

                if (c == '/' && i + 1 < n && s[i + 1] == '/')
                {
                    while (i < n && s[i] != '\n') { if (s[i] != '\r') r[i] = ' '; i++; }
                    continue;
                }
                if (c == '/' && i + 1 < n && s[i + 1] == '*')
                {
                    int e = s.IndexOf("*/", i + 2, StringComparison.Ordinal);
                    int end = e < 0 ? n : e + 2;
                    Blank(s, r, i, end);
                    i = end;
                    continue;
                }
                if (c == '"')
                {
                    if (i > 0 && s[i - 1] == 'R')
                    {
                        int p = s.IndexOf('(', i);
                        if (p > 0 && p - i <= 17)
                        {
                            string delim = s.Substring(i + 1, p - i - 1);
                            int e = s.IndexOf(")" + delim + "\"", p, StringComparison.Ordinal);
                            int end = e < 0 ? n : e + delim.Length + 2;
                            Blank(s, r, i, end);
                            i = end;
                            continue;
                        }
                    }
                    int j = SkipQuoted(s, i, '"');
                    Blank(s, r, i, j);
                    i = j;
                    continue;
                }
                if (c == '\'')
                {
                    // 1'000'000 の区切りは文字リテラルではない
                    if (i > 0 && char.IsLetterOrDigit(s[i - 1]) && i + 1 < n && char.IsLetterOrDigit(s[i + 1])) { i++; continue; }
                    int j = SkipQuoted(s, i, '\'');
                    Blank(s, r, i, j);
                    i = j;
                    continue;
                }
                i++;
            }
            return new string(r);
        }

        private static int SkipQuoted(string s, int open, char q)
        {
            int j = open + 1;
            while (j < s.Length && s[j] != q && s[j] != '\n')
            {
                if (s[j] == '\\') j++;
                j++;
            }
            if (j < s.Length && s[j] == q) j++;
            return Math.Min(j, s.Length);
        }

        private static void Blank(string s, char[] r, int from, int to)
        {
            for (int k = from; k < to && k < r.Length; k++)
                if (s[k] != '\n' && s[k] != '\r') r[k] = ' ';
        }

        public static bool IsId(char c) { return char.IsLetterOrDigit(c) || c == '_'; }

        /// <summary>
        /// 識別子 [start, end) の左へ「a::b::」をたどって、修飾名(a::b::name)と、その先頭の位置を返す。
        /// 先頭が「::」だけのとき(グローバル)は、修飾なしとみなす。「Foo&lt;int&gt;::Bar」のように決められないときは null。
        /// </summary>
        public static string Chain(string m, int start, int end, out int chainStart)
        {
            chainStart = start;
            string chain = m.Substring(start, end - start);
            int s = start;
            while (true)
            {
                int p = s - 1;
                while (p >= 0 && (m[p] == ' ' || m[p] == '\t')) p--;
                if (p < 1 || m[p] != ':' || m[p - 1] != ':') break;
                int q = p - 2;
                while (q >= 0 && (m[q] == ' ' || m[q] == '\t')) q--;
                int idEnd = q + 1;
                while (q >= 0 && IsId(m[q])) q--;
                int idStart = q + 1;
                if (idEnd > idStart && !char.IsDigit(m[idStart]))
                {
                    chain = m.Substring(idStart, idEnd - idStart) + "::" + chain;
                    s = idStart;
                    continue;
                }
                if (q >= 0 && (m[q] == '>' || m[q] == ')' || m[q] == ']')) return null;
                s = p - 1;
                break;
            }
            chainStart = s;
            return chain;
        }

        private static readonly HashSet<string> DeclaringWords = new HashSet<string>
        {
            "class", "struct", "enum", "union", "namespace", "using", "typedef", "goto",
        };

        /// <summary>
        /// 識別子 [start, end) が、型の名前として使われている形か。そうなら修飾名を返す(違えば null)。
        /// 「.名前」「->名前」、宣言そのもの(class Foo)、関数や変数の名前のような形は、型ではないとして除く。
        /// m は Mask の結果。
        /// </summary>
        public static string TypeUseName(string m, int start, int end, out int chainStart)
        {
            string chain = Chain(m, start, end, out chainStart);
            if (chain == null) return null;

            int b = chainStart - 1;
            while (b >= 0 && char.IsWhiteSpace(m[b])) b--;
            char prev = b >= 0 ? m[b] : '\0';
            if (prev == '.' || prev == '~') return null;
            if (prev == '>' && b >= 1 && m[b - 1] == '-') return null;
            if (IsId(prev))
            {
                int w = b;
                while (w >= 0 && IsId(m[w])) w--;
                if (DeclaringWords.Contains(m.Substring(w + 1, b - w))) return null;
            }

            int a = end;
            while (a < m.Length && char.IsWhiteSpace(m[a])) a++;
            char next = a < m.Length ? m[a] : '\0';
            char next2 = a + 1 < m.Length ? m[a + 1] : '\0';
            bool ok;
            if (next == ':') ok = next2 == ':';
            else if (next == '(')
            {
                // 「Foo::Instance()」のような、クラスや名前空間の関数の呼び出しは、型ではない。std:: のものだけ型(std::vector<int>() など)として扱う
                ok = chain.IndexOf("::", StringComparison.Ordinal) < 0 || chain.StartsWith("std::", StringComparison.Ordinal);
            }
            else if (next == '<' || next == '*' || next == '&' || next == '{') ok = true;
            else if (IsId(next)) ok = true;
            else if (next == '>' || next == ',' || next == ')') ok = prev == '<' || prev == ',' || prev == '(';
            else ok = false;
            return ok ? chain : null;
        }

        private static readonly Regex Ident = new Regex(@"(?<![\w])[A-Za-z_]\w*", RegexOptions.Compiled);

        /// <summary>m の [from, to) にある識別子(位置と名前)。</summary>
        public static List<KeyValuePair<int, string>> Identifiers(string m, int from, int to)
        {
            var list = new List<KeyValuePair<int, string>>();
            to = Math.Min(to, m.Length);
            for (Match x = Ident.Match(m, Math.Max(0, from)); x.Success && x.Index < to; x = x.NextMatch())
                list.Add(new KeyValuePair<int, string>(x.Index, x.Value));
            return list;
        }
    }
}
