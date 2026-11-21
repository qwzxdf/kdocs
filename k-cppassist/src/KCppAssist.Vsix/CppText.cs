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
        // 電球の一覧などは、同じ文字(同じ string)を何度も走査する。直前の 1 つを、スレッドごとに覚えて使い回す
        // (string は変わらないので、同じ参照なら結果も同じ)
        [ThreadStatic] private static string maskIn, maskOut;

        public static string Mask(string s)
        {
            if (ReferenceEquals(s, maskIn)) return maskOut;
            string r = MaskCore(s);
            maskIn = s; maskOut = r;
            return r;
        }

        private static string MaskCore(string s)
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
                    // 1'000'000 や 0xFF'FF の区切りは、文字リテラルではない。L'a'・u8'a'・U'a' は文字リテラル(直前の語が数字で始まるかで見分ける)
                    if (IsDigitSeparator(s, i)) { i++; continue; }
                    int j = SkipQuoted(s, i, '\'');
                    Blank(s, r, i, j);
                    i = j;
                    continue;
                }
                i++;
            }
            return new string(r);
        }

        /// <summary>s[i] の「'」が、数の中の区切り(1'000)か。直前の語(英数字と区切りの並び)が数字で始まり、直後が英数字のとき。</summary>
        public static bool IsDigitSeparator(string s, int i)
        {
            if (i <= 0 || i + 1 >= s.Length || !char.IsLetterOrDigit(s[i - 1]) || !char.IsLetterOrDigit(s[i + 1])) return false;
            int k = i - 1;
            while (k > 0 && (char.IsLetterOrDigit(s[k - 1]) || s[k - 1] == '\'' || s[k - 1] == '.')) k--;
            if (!char.IsDigit(s[k])) return false;                     // L'a'・u8'a' の L・u8 は数字で始まらない
            return k == 0 || !(char.IsLetterOrDigit(s[k - 1]) || s[k - 1] == '_');
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

        /// <summary>文字の改行の種類。CRLF が 1 つでもあれば「\r\n」、なければ「\n」。足す文字の改行を、元のファイルにそろえるために使う。</summary>
        public static string Eol(string text) { return text.Contains("\r\n") ? "\r\n" : "\n"; }

        /// <summary>
        /// ファイルの字下げ 1 段の文字(タブ、空白 2 つ、空白 4 つ)。行頭がタブの行と空白の行を数えて、多いほう。
        /// 空白なら、4 の倍数でない字下げ(2・6・10…)が 2 割以上あれば 2、なければ 4。字下げのある行が 1 行もないときは、タブ(VS の C++ の既定)。
        /// </summary>
        /// <summary>IndentUnit と同じ。ただし、text に字下げのある行がなければ(新しい cpp など)、fallback(相手のヘッダーなど)から決める。</summary>
        public static string IndentUnit(string text, string fallback)
        {
            bool any = text != null && System.Text.RegularExpressions.Regex.IsMatch(text, @"(?m)^(?:\t|  )\S");
            return IndentUnit(any ? text : fallback);
        }

        public static string IndentUnit(string text)
        {
            int tab = 0, sp2 = 0, sp4 = 0;
            if (text != null)
                foreach (string line in text.Split('\n'))
                {
                    if (line.Length == 0) continue;
                    if (line[0] == '\t') { tab++; continue; }
                    int n = 0;
                    while (n < line.Length && line[n] == ' ') n++;
                    if (n == 0 || n == line.Length || line[n] == '\r') continue;
                    if (n % 2 != 0) continue;           // 「 public:」(Google の 1 字)や、行の続きのそろえは数えない
                    if (n % 4 == 0) sp4++; else sp2++;
                }
            if (tab + sp2 + sp4 == 0) return "\t";
            if (tab >= sp2 + sp4) return "\t";
            return sp2 * 5 >= sp2 + sp4 ? "  " : "    ";
        }

        /// <summary>
        /// public: などのアクセス指定子を、クラスの行からどれだけ下げて書くか。ファイルの中の最初の指定子と、その上の class / struct の行を見比べる。
        /// 見つからなければ ""(クラスと同じ位置。VS の既定)。Google スタイルなら " "。
        /// </summary>
        public static string LabelOffset(string text)
        {
            if (string.IsNullOrEmpty(text)) return "";
            var lines = text.Split('\n');
            for (int i = 0; i < lines.Length; i++)
            {
                var lm = System.Text.RegularExpressions.Regex.Match(lines[i], @"^([ \t]*)(?:public|protected|private)\s*:(?!:)");
                if (!lm.Success) continue;
                for (int j = i - 1; j >= 0 && j >= i - 200; j--)
                {
                    var cm = System.Text.RegularExpressions.Regex.Match(lines[j], @"^([ \t]*)(?:template\s*<.*>\s*)?(?:class|struct)\s+\w");
                    if (!cm.Success || lines[j].TrimEnd().EndsWith(";")) continue;
                    string label = lm.Groups[1].Value, head = cm.Groups[1].Value;
                    return label.StartsWith(head, StringComparison.Ordinal) ? label.Substring(head.Length) : "";
                }
                return "";
            }
            return "";
        }

        /// <summary>Eol と同じ。ただし、改行が 1 つもない(新しい・1 行の)ファイルなら、fallback(相手のファイルの改行)を使う。</summary>
        public static string Eol(string text, string fallback) { return text.Contains("\r\n") ? "\r\n" : text.Contains("\n") ? "\n" : fallback; }

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
