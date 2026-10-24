using System;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppMember
{
    /// <summary>クラスの宣言(ヘッダーの文字)を探し、メンバー変数を足す場所と文字を決める。VS に依存しない。</summary>
    internal static class HeaderEditor
    {
        public sealed class Edit
        {
            public int Position;
            public string Text;
        }

        /// <summary>class / struct の定義を探して、メンバー 1 行を入れる編集を返す。見つからなければ null。</summary>
        public static Edit Plan(string text, string className, string declaration, string eol)
        {
            var m = Regex.Match(text, @"\b(class|struct)\s+(?:[A-Za-z_]\w*\s+)*?" + Regex.Escape(className) + @"\b[^;{]*\{");
            if (!m.Success) return null;
            bool isStruct = m.Groups[1].Value == "struct";
            int open = m.Index + m.Length - 1;
            int close = FindClose(text, open);
            if (close < 0) return null;

            // クラスの直下(波括弧の深さ 0)にある、最後のアクセス指定子
            string body = text.Substring(open + 1, close - open - 1);
            string lastSpec = null;
            int lastSpecAt = -1;
            int depth = 0;
            for (int i = 0; i < body.Length; i++)
            {
                char c = body[i];
                if (c == '{') depth++;
                else if (c == '}') depth--;
                else if (depth == 0 && (c == 'p') && (i == 0 || !IsId(body[i - 1])))
                {
                    var s = Regex.Match(body.Substring(i), @"^(public|protected|private)\s*:(?!:)");
                    if (s.Success) { lastSpec = s.Groups[1].Value; lastSpecAt = i; }
                }
            }

            // 閉じ括弧の行の頭
            int lineStart = close;
            while (lineStart > 0 && text[lineStart - 1] != '\n') lineStart--;
            bool braceFirst = text.Substring(lineStart, close - lineStart).Trim().Length == 0;
            string closeIndent = braceFirst ? text.Substring(lineStart, close - lineStart) : "";

            // メンバーの字下げは、閉じ括弧の直前にある行(アクセス指定子以外)に合わせる。なければ 2 字下げ
            string memberIndent = closeIndent + "  ";
            int prevEnd = lineStart - 1;
            while (braceFirst && prevEnd > open)
            {
                int prevStart = prevEnd;
                while (prevStart > 0 && text[prevStart - 1] != '\n') prevStart--;
                string prev = text.Substring(prevStart, prevEnd - prevStart).TrimEnd('\r');
                prevEnd = prevStart - 1;
                if (prev.Trim().Length == 0) continue;
                if (Regex.IsMatch(prev, @"^\s*(public|protected|private)\s*:")) break;
                string indent = prev.Substring(0, prev.Length - prev.TrimStart().Length);
                if (indent.Length > closeIndent.Length) memberIndent = indent;
                break;
            }

            var sb = new StringBuilder();
            // private: が最後なら、その下に足す。そうでなければ、末尾に private: を作る
            bool needSpec = lastSpec != "private";
            if (needSpec)
            {
                // Google style: private: は 1 字下げ、メンバーは 2 字下げ
                memberIndent = closeIndent + "  ";
                sb.Append(eol).Append(closeIndent).Append(" private:").Append(eol);
            }
            sb.Append(memberIndent).Append(declaration).Append(eol);
            return new Edit
            {
                Position = braceFirst ? lineStart : close,
                Text = braceFirst ? sb.ToString() : eol + sb.ToString(),
            };
        }

        private static bool IsId(char c) { return char.IsLetterOrDigit(c) || c == '_'; }

        /// <summary>open の '{' に対応する '}' の位置。コメントと文字列の中は数えない。</summary>
        private static int FindClose(string s, int open)
        {
            int depth = 0;
            for (int i = open; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '/' && i + 1 < s.Length && s[i + 1] == '/') { while (i < s.Length && s[i] != '\n') i++; continue; }
                if (c == '/' && i + 1 < s.Length && s[i + 1] == '*')
                {
                    int e = s.IndexOf("*/", i + 2, StringComparison.Ordinal);
                    if (e < 0) return -1;
                    i = e + 1;
                    continue;
                }
                if (c == '"' || c == '\'')
                {
                    char q = c;
                    for (i++; i < s.Length && s[i] != q; i++) if (s[i] == '\\') i++;
                    continue;
                }
                if (c == '{') depth++;
                else if (c == '}') { depth--; if (depth == 0) return i; }
            }
            return -1;
        }
    }
}
