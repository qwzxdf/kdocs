using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// カーソルのある「名前 = 右辺;」の文を、文字から切り出す。VS に依存しない。
    /// 行頭に限らず、複数行にわたる右辺や、ラムダの中の 1 文(「[this] { x_ = 1; }」)も対象にする。
    /// </summary>
    internal static class AssignScan
    {
        public sealed class Assign
        {
            public string Name;
            public bool HasThis;
            public int NameStart;     // 名前の位置(text の中)
            public int RhsStart;      // 右辺の最初の文字の位置
            public string Rhs;        // 右辺(改行も含めた元の文字。前後の空白は除く)
        }

        private static readonly Regex Label = new Regex(@"\G\s*(?:(?:public|private|protected)\s*:(?!:)|default\s*:(?!:)|case\s+[^:;{}]+:(?!:))\s*");
        private static readonly Regex Head = new Regex(@"\G\s*(this\s*->\s*)?([A-Za-z_]\w*)\s*=(?!=)\s*");

        /// <summary>caret を含む文が「名前 = 右辺」の形ならそれを返す。そうでなければ null。</summary>
        public static Assign Find(string text, int caret)
        {
            string m = CppText.Mask(text);
            int start = StatementStart(m, caret);
            var lab = Label.Match(m, start);
            if (lab.Success) start = lab.Index + lab.Length;
            var head = Head.Match(m, start);
            if (!head.Success) return null;

            int rhsStart = head.Index + head.Length;
            int end = StatementEnd(m, rhsStart);
            if (end <= rhsStart) return null;
            // この文にカーソルがない(次の文の頭より前に切れた)ときは対象にしない
            string rhs = text.Substring(rhsStart, end - rhsStart);
            string trimmed = rhs.TrimEnd();
            if (trimmed.Length == 0) return null;
            return new Assign
            {
                Name = head.Groups[2].Value,
                HasThis = head.Groups[1].Success,
                NameStart = head.Groups[2].Index,
                RhsStart = rhsStart,
                Rhs = trimmed,
            };
        }

        /// <summary>caret から後ろへ戻って、文の頭(前の「;」「{」「}」の次)を探す。括弧・波括弧が式の中で閉じているものは飛ばす。</summary>
        private static int StatementStart(string m, int caret)
        {
            int origin = caret;
            if (origin > m.Length) origin = m.Length;
            // 行末の「;」のあとにカーソルがあるときは、その文の中とみなす
            int k = origin;
            while (k > 0 && (m[k - 1] == ' ' || m[k - 1] == '\t' || m[k - 1] == '\r')) k--;
            if (k > 0 && m[k - 1] == ';') origin = k - 1;

            int paren = 0, brace = 0;
            int i = origin;
            while (i > 0)
            {
                char c = m[i - 1];
                if (c == ')' || c == ']') paren++;
                else if (c == '(' || c == '[') { if (paren > 0) paren--; }
                else if (c == '}')
                {
                    if (BraceBelongsToExpression(m, i - 1)) brace++;
                    else if (paren == 0 && brace == 0) break;
                }
                else if (c == '{')
                {
                    if (brace > 0) brace--;
                    else if (paren == 0) break;
                }
                else if (c == ';' && paren == 0 && brace == 0) break;
                i--;
            }
            return i;
        }

        /// <summary>「}」の次が「;」「,」「)」「.」などなら、初期化子リストやラムダの閉じで、文の終わりではない。</summary>
        private static bool BraceBelongsToExpression(string m, int close)
        {
            int j = close + 1;
            while (j < m.Length && char.IsWhiteSpace(m[j])) j++;
            if (j >= m.Length) return false;
            char n = m[j];
            return n == ';' || n == ',' || n == ')' || n == '.' || n == ']' || n == '}';
        }

        /// <summary>右辺の最初から、文の終わり(深さ 0 の「;」)を探す。「;」がまだ書かれていないときは、続きの行がなさそうな行末で切る。</summary>
        private static int StatementEnd(string m, int from)
        {
            int depth = 0;
            int limit = System.Math.Min(m.Length, from + 4000);
            for (int i = from; i < limit; i++)
            {
                char c = m[i];
                if (c == '(' || c == '[' || c == '{') depth++;
                else if (c == ')' || c == ']' || c == '}')
                {
                    if (depth == 0) return TrimEnd(m, from, i);     // 文が閉じる前に外側の括弧が閉じた(ラムダの最後の文など)
                    depth--;
                }
                else if (c == ';' && depth == 0) return i;
                else if (c == '\n' && depth == 0 && !Continues(m, from, i)) return TrimEnd(m, from, i);
            }
            return -1;
        }

        private static int TrimEnd(string m, int from, int end)
        {
            while (end > from && char.IsWhiteSpace(m[end - 1])) end--;
            return end;
        }

        /// <summary>行末(newline の位置)で、式が次の行に続くか。</summary>
        private static bool Continues(string m, int from, int nl)
        {
            int a = nl;
            while (a > from && char.IsWhiteSpace(m[a - 1])) a--;
            if (a <= from) return true;                                  // 右辺がまだ空
            char last = m[a - 1];
            if ("+-*/%&|^<>=?:,.(".IndexOf(last) >= 0) return true;      // 演算子で終わっている
            int b = nl + 1;
            while (b < m.Length && char.IsWhiteSpace(m[b])) b++;
            if (b >= m.Length) return false;
            char first = m[b];
            // 次の行が演算子で始まる(「+ x」「? a」「: b」「.f()」「-> f」)
            if ("+-*/%&|^?:.".IndexOf(first) >= 0)
            {
                // 「*p = 1;」「&x;」のような次の文の頭も同じ文字で始まるが、前の行が式として終わっていて、
                // 次の行が「+」「?」「:」「.」「->」「&&」「||」で始まるものだけを続きとみなす
                if (first == '*' || first == '&')
                    return b + 1 < m.Length && m[b + 1] == '&' && first == '&';
                if (first == '-') return b + 1 < m.Length && (m[b + 1] == '>' || m[b + 1] == ' ');
                return true;
            }
            if (first == '<' || first == '>' || first == '|') return true;
            return false;
        }
    }
}
