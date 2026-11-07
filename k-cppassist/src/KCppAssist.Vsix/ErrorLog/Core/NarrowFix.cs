using System;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist.ErrorLog
{
    /// <summary>
    /// 縮小変換の警告・エラー(double から int など)を、右辺を static_cast で包んで直す。VS に依存しない。
    /// 対象は 1 行で終わる「型 名前 = 式;」「名前 = 式;」「return 式;」「型 名前{式};」だけ。
    /// 引数の途中や複数行の式のような、場所を確実に決められないものは、直さない(null を返す)。
    /// </summary>
    internal static class NarrowFix
    {
        public sealed class Plan
        {
            public int Start;           // 行の中の位置
            public int Length;          // 置き換える長さ
            public string Text;         // 置き換える文字(static_cast<T>(式))
        }

        // 縮小変換を言うコード
        //   C4244: double から int など(データが失われる)   C4267: size_t から int など
        //   C4305: double から float への切り詰め            C4838 / C2397: { } の中の縮小変換
        public static bool IsCandidate(string code)
        {
            return code == "C4244" || code == "C4267" || code == "C4305" || code == "C4838" || code == "C2397";
        }

        private static readonly Regex FromToEn = new Regex(@"from '(?<a>[^']+)' to '(?<b>[^']+)'", RegexOptions.Compiled);
        private static readonly Regex FromToJa = new Regex(@"'(?<a>[^']+)'\s*から\s*'(?<b>[^']+)'", RegexOptions.Compiled);
        private static readonly Regex ScalarType = new Regex(@"^(?:(?:unsigned|signed|const)\s+)*[A-Za-z_][\w:]*(?:\s+(?:int|long|short|char))*$", RegexOptions.Compiled);

        /// <summary>メッセージの「'A' から 'B'」の B(変換先の型)。ポインター・参照・取り出せないときは null。</summary>
        public static string TargetType(string message)
        {
            Match m = FromToEn.Match(message ?? "");
            if (!m.Success) m = FromToJa.Match(message ?? "");
            if (!m.Success) return null;
            string b = m.Groups["b"].Value.Trim();
            if (b.IndexOfAny(new[] { '*', '&', '<', '>', '(', '[' }) >= 0) return null;
            return ScalarType.IsMatch(b) ? b : null;
        }

        /// <summary>文字列・文字・コメントの中身を空白にした、同じ長さの文字列。</summary>
        private static string Mask(string s)
        {
            var sb = new StringBuilder(s);
            int i = 0;
            while (i < s.Length)
            {
                char c = s[i];
                if (c == '/' && i + 1 < s.Length && s[i + 1] == '/')
                {
                    for (; i < s.Length; i++) sb[i] = ' ';
                }
                else if (c == '/' && i + 1 < s.Length && s[i + 1] == '*')
                {
                    int e = s.IndexOf("*/", i + 2, StringComparison.Ordinal);
                    int end = e < 0 ? s.Length : e + 2;
                    for (; i < end; i++) sb[i] = ' ';
                }
                else if (c == '"' || c == '\'')
                {
                    int j = i + 1;
                    while (j < s.Length && s[j] != c) { if (s[j] == '\\') j++; j++; }
                    for (int k = i + 1; k < j && k < s.Length; k++) sb[k] = 'x';
                    i = j + 1;
                }
                else i++;
            }
            return sb.ToString();
        }

        private static readonly Regex Keyword = new Regex(@"^\s*(?:for|while|if|switch|else|do|case|using|typedef)\b", RegexOptions.Compiled);
        private static readonly Regex Return = new Regex(@"^(?<head>\s*return\s+)(?<rhs>.+?)\s*;\s*$", RegexOptions.Compiled);

        /// <summary>行 line の右辺を static_cast&lt;type&gt;(...) で包む編集。できなければ null。</summary>
        public static Plan Make(string line, string type)
        {
            if (string.IsNullOrEmpty(line) || string.IsNullOrEmpty(type)) return null;
            string m = Mask(line);
            if (Keyword.IsMatch(m)) return null;

            int rs, re;
            Match r = Return.Match(m);
            if (r.Success)
            {
                rs = r.Groups["rhs"].Index;
                re = rs + r.Groups["rhs"].Length;
            }
            else
            {
                int semi = m.LastIndexOf(';');
                if (semi < 0 || m.Substring(semi + 1).Trim().Length > 0) return null;
                if (!FindRhs(m, semi, out rs, out re)) return null;
            }
            while (rs < re && char.IsWhiteSpace(m[rs])) rs++;
            while (re > rs && char.IsWhiteSpace(m[re - 1])) re--;
            if (re <= rs) return null;

            string rhsMasked = m.Substring(rs, re - rs);
            string rhs = line.Substring(rs, re - rs);
            if (rhsMasked.StartsWith("{", StringComparison.Ordinal)) return null;
            if (HasTopLevelComma(rhsMasked)) return null;
            if (Regex.IsMatch(rhsMasked, @"^(?:static_cast|reinterpret_cast|const_cast|dynamic_cast)\s*<")) return null;
            if (Regex.IsMatch(rhsMasked, @"^\(\s*(?:unsigned\s+|signed\s+)?(?:int|float|double|char|short|long|size_t|u?int\d+_t)\s*\)")) return null;

            // 全体が 1 組の ( ) なら、その中身を使う(static_cast<int>((a + b)) にしない)
            string inner = rhs;
            if (WholeParen(rhsMasked)) inner = rhs.Substring(1, rhs.Length - 2).Trim();
            return new Plan { Start = rs, Length = re - rs, Text = "static_cast<" + type + ">(" + inner + ")" };
        }

        /// <summary>semi の前の、最初の = の右(代入・初期化)か、{ } の中身。</summary>
        private static bool FindRhs(string m, int semi, out int rs, out int re)
        {
            rs = re = 0;
            int depth = 0;
            for (int i = 0; i < semi; i++)
            {
                char c = m[i];
                if (c == '(' || c == '[' || c == '{') { if (c == '{' && depth == 0) { return BraceInit(m, i, semi, out rs, out re); } depth++; }
                else if (c == ')' || c == ']' || c == '}') depth--;
                else if (c == '=' && depth == 0)
                {
                    char prev = i > 0 ? m[i - 1] : ' ';
                    char next = i + 1 < m.Length ? m[i + 1] : ' ';
                    if (next == '=') { i++; continue; }                              // ==
                    if ("+-*/%&|^<>!=".IndexOf(prev) >= 0) return false;            // += <= != などは、対象にしない
                    rs = i + 1;
                    re = semi;
                    return true;
                }
            }
            return false;
        }

        /// <summary>型 名前{式}; の { } の中身(1 つの式だけ)。</summary>
        private static bool BraceInit(string m, int open, int semi, out int rs, out int re)
        {
            rs = re = 0;
            int close = m.LastIndexOf('}', semi - 1);
            if (close <= open) return false;
            if (m.Substring(close + 1, semi - close - 1).Trim().Length > 0) return false;
            if (open == 0 || !CppId(m[open - 1]) && !char.IsWhiteSpace(m[open - 1])) return false;
            rs = open + 1;
            re = close;
            return true;
        }

        private static bool CppId(char c) { return char.IsLetterOrDigit(c) || c == '_'; }

        private static bool HasTopLevelComma(string s)
        {
            int depth = 0;
            foreach (char c in s)
            {
                if (c == '(' || c == '[' || c == '{') depth++;
                else if (c == ')' || c == ']' || c == '}') depth--;
                else if (c == ',' && depth == 0) return true;
            }
            return false;
        }

        private static bool WholeParen(string s)
        {
            if (s.Length < 2 || s[0] != '(' || s[s.Length - 1] != ')') return false;
            int depth = 0;
            for (int i = 0; i < s.Length; i++)
            {
                if (s[i] == '(') depth++;
                else if (s[i] == ')') { depth--; if (depth == 0 && i < s.Length - 1) return false; }
            }
            return depth == 0;
        }
    }
}
