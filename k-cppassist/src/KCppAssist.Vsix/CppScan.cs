using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>cpp の文字から、カーソルのいる関数がどのクラスのメンバー関数かを探す。VS に依存しない。</summary>
    internal static class CppScan
    {
        private static readonly Regex Def = new Regex(
            @"(?<![\w:])(?:[A-Za-z_]\w*(?:<[^<>]*>)?::)*([A-Za-z_]\w*(?:<[^<>]*>)?)::~?[A-Za-z_]\w*\s*\(");

        /// <summary>
        /// 「Class::Func(...) ... {」の本体にカーソルが入っていれば、Class を返す。なければ null。
        /// 字下げや、引数が複数行に分かれている書き方でも見つかる。
        /// </summary>
        public static string EnclosingClass(string text, int caret)
        {
            var matches = Def.Matches(text);
            int checkedCount = 0;
            for (int i = matches.Count - 1; i >= 0 && checkedCount < 60; i--)
            {
                Match m = matches[i];
                if (m.Index >= caret) continue;
                checkedCount++;

                // 戻り値の型や修飾だけが前にある行(「x = Foo::Bar(」や「return Foo::Bar(」は関数の定義ではない)
                int ls = m.Index;
                while (ls > 0 && text[ls - 1] != '\n') ls--;
                string prefix = text.Substring(ls, m.Index - ls);
                if (!Regex.IsMatch(prefix, @"^[\s\w:<>\*&,~]*$")) continue;
                if (Regex.IsMatch(prefix, @"\b(return|else|case|co_return|throw|new|delete|if|while|for|switch)\b")) continue;

                int open = m.Index + m.Length - 1;                 // '('
                int close = MatchParen(text, open);
                if (close < 0) continue;
                // ')' のあと、最初に来るのが '{' なら定義(';' なら呼び出しか宣言)
                int j = close + 1;
                while (j < text.Length && text[j] != '{' && text[j] != ';') j++;
                if (j >= text.Length || text[j] != '{') continue;
                int bodyOpen = j;
                int bodyClose = AccessorEditor.FindClose(text, bodyOpen);
                if (bodyOpen < caret && (bodyClose < 0 || caret <= bodyClose))
                    return Regex.Replace(m.Groups[1].Value, @"<.*>", "");
            }
            return null;
        }

        private static int MatchParen(string s, int open)
        {
            int depth = 0;
            for (int i = open; i < s.Length; i++)
            {
                if (s[i] == '(') depth++;
                else if (s[i] == ')') { depth--; if (depth == 0) return i; }
            }
            return -1;
        }
    }
}
