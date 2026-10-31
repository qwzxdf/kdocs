using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// cpp / ヘッダーの文字から、関数の宣言と定義(名前と、引数の括弧の位置)を集める。VS に依存しない。
    /// 名前空間とクラスの直下だけを読み、関数の本体・列挙・初期化子の中身は読まない。
    /// </summary>
    internal static class FunctionScan
    {
        public sealed class Sig
        {
            public string Class;        // クラスのメンバーなら、そのクラス(Class::Func の定義なら Class)。それ以外は null
            public string Name;
            public int Open, Close;     // '(' と ')' の位置
            public bool HasBody;        // 本体({ ... })がある(定義)
            public bool InClass;        // クラスの本体の中に書かれている
            public List<string> Chain = new List<string>();   // 名前の前に付く、namespace とクラスの並び(外側から順。囲んでいるものと、Class::Func の修飾の両方)
            public bool IsConst;        // ')' のあとに const が付く(オーバーロードの区別に使う)

            public string Inner(string text) { return text.Substring(Open + 1, Close - Open - 1); }
        }

        private static readonly Regex EnumHead = new Regex(@"\benum\b", RegexOptions.Compiled);
        private static readonly Regex ClassHead = new Regex(
            @"(?<![\w])(?:class|struct|union)\s+" +
            @"(?:(?:alignas\s*\([^)]*\)|__declspec\s*\([^)]*\)|\[\[[^\]]*\]\]|[A-Z][A-Z0-9_]*_API|[A-Z][A-Z0-9_]*EXPORT[A-Z0-9_]*)\s+)*" +
            @"([A-Za-z_]\w*)\s*(?:final\s*)?(?::[^;{}]*)?\s*$", RegexOptions.Compiled);
        private static readonly Regex NsHead = new Regex(@"(?:\bnamespace\b[^;{}]*|\bextern\s*)$", RegexOptions.Compiled);
        private static readonly Regex NsName = new Regex(@"\bnamespace\s+((?:[A-Za-z_]\w*\s*::\s*)*[A-Za-z_]\w*)\s*$", RegexOptions.Compiled);
        private static readonly Regex Access = new Regex(@"^\s*(public|protected|private)\s*$", RegexOptions.Compiled);
        private static readonly Regex NameTail = new Regex(@"((?:[A-Za-z_]\w*\s*(?:<[^<>]*>)?\s*::\s*)*)(~?[A-Za-z_]\w*)\s*$", RegexOptions.Compiled);
        private static readonly Regex Keywords = new Regex(
            @"\b(if|for|while|switch|return|sizeof|new|delete|catch|typedef|using|throw|else|decltype|static_assert|alignas|alignof|noexcept|co_return|co_await)\b", RegexOptions.Compiled);

        public static List<Sig> Scan(string text)
        {
            string m = CppText.Mask(text);
            var sigs = new List<Sig>();
            var stack = new Stack<KeyValuePair<bool, string>>();   // (クラスか, 名前)。名前空間は (false, null)
            int n = m.Length, i = 0, stmt = 0;
            while (i < n)
            {
                char c = m[i];
                if (c == ';') { stmt = ++i; continue; }
                if (c == '}') { if (stack.Count > 0) stack.Pop(); stmt = ++i; continue; }
                if (c == '{')
                {
                    string head = Head(m, stmt, i);
                    Match cm;
                    if (!EnumHead.IsMatch(head) && (cm = ClassHead.Match(head)).Success)
                        stack.Push(new KeyValuePair<bool, string>(true, cm.Groups[1].Value));
                    else if (NsHead.IsMatch(head))
                    {
                        var nm = NsName.Match(head);
                        stack.Push(new KeyValuePair<bool, string>(false, nm.Success ? Regex.Replace(nm.Groups[1].Value, @"\s+", "") : null));
                    }
                    else
                    {
                        int e = MatchClose(m, i, '{', '}');
                        i = e < 0 ? n : e + 1;
                        stmt = i;
                        continue;
                    }
                    stmt = ++i;
                    continue;
                }
                if (c == ':' && !(i + 1 < n && m[i + 1] == ':') && !(i > 0 && m[i - 1] == ':') && Access.IsMatch(Head(m, stmt, i)))
                { stmt = ++i; continue; }
                if (c == '(')
                {
                    int close = MatchClose(m, i, '(', ')');
                    if (close < 0) break;
                    var top = stack.Count > 0 ? stack.Peek() : new KeyValuePair<bool, string>(false, null);
                    int after;
                    Sig s = TryFunction(m, stmt, i, close, top, EnclosingNames(stack), out after);
                    if (s != null)
                    {
                        sigs.Add(s);
                        i = after;
                        stmt = i;
                    }
                    else i = close + 1;
                    continue;
                }
                i++;
            }
            return sigs;
        }

        /// <summary>
        /// 文の頭から end までの文字。「;」「{」「}」のない長い範囲(マクロや表)でも正規表現が遅くならないように、
        /// 末尾の 600 文字だけにする(関数の頭や、クラスの頭がこれより長いことはない)。
        /// </summary>
        private static string Head(string m, int stmt, int end)
        {
            const int Max = 600;
            if (end - stmt <= Max) return m.Substring(stmt, end - stmt);
            int from = end - Max;
            while (from < end && !char.IsWhiteSpace(m[from])) from++;
            return m.Substring(from, end - from);
        }

        /// <summary>囲んでいる namespace とクラスの名前を、外側から順に並べる(無名のものは入れない。「a::b」は a, b に分ける)。</summary>
        private static List<string> EnclosingNames(Stack<KeyValuePair<bool, string>> stack)
        {
            var list = new List<string>();
            foreach (var e in stack.Reverse())
                if (e.Value != null) list.AddRange(e.Value.Split(new[] { "::" }, StringSplitOptions.RemoveEmptyEntries));
            return list;
        }

        private static Sig TryFunction(string m, int stmt, int open, int close, KeyValuePair<bool, string> top, List<string> enclosing, out int after)
        {
            after = open + 1;
            string prefix = Head(m, stmt, open);
            var nm = NameTail.Match(prefix);
            if (!nm.Success) return null;
            string name = nm.Groups[2].Value;
            string qual = nm.Groups[1].Value;
            string before = prefix.Substring(0, nm.Index);
            if (name.StartsWith("~") || name == "operator") return null;
            if (Keywords.IsMatch(before) || Keywords.IsMatch(name)) return null;
            if (before.IndexOf('=') >= 0) return null;
            // std::function<void(int)> のように、テンプレートの引数の中の括弧は関数ではない
            if (prefix.Count(ch => ch == '<') > prefix.Count(ch => ch == '>')) return null;

            string cls = null;
            if (qual.Trim().Length > 0)
            {
                var parts = qual.Split(new[] { "::" }, StringSplitOptions.RemoveEmptyEntries);
                if (parts.Length > 0) cls = Regex.Replace(parts[parts.Length - 1], @"\s*<.*>\s*", "").Trim();
            }
            else if (top.Key) cls = top.Value;

            bool ctor = cls != null && name == cls;
            if (!ctor && !Regex.IsMatch(before, @"[\w>\*&]")) return null;     // 戻り値の型がない(マクロの呼び出しなど)

            // ')' のあと、最初の ';' か本体の '{' まで
            int n = m.Length, j = close + 1;
            bool body = false;
            while (j < n)
            {
                char d = m[j];
                if (d == ';') break;
                if (d == '{') { body = true; break; }
                if (d == '}') return null;
                if (d == '(') { int e = MatchClose(m, j, '(', ')'); if (e < 0) return null; j = e + 1; continue; }
                if (d == ':' && !(j + 1 < n && m[j + 1] == ':') && !(j > 0 && m[j - 1] == ':'))
                {
                    // コンストラクターの初期化子リスト。メンバー{...} は初期化、それ以外の '{' が本体
                    j++;
                    while (j < n)
                    {
                        char ch = m[j];
                        if (ch == '(') { int e = MatchClose(m, j, '(', ')'); if (e < 0) return null; j = e + 1; continue; }
                        if (ch == '{')
                        {
                            int p = j - 1;
                            while (p >= 0 && char.IsWhiteSpace(m[p])) p--;
                            if (p >= 0 && (CppText.IsId(m[p]) || m[p] == '>'))
                            {
                                int e = MatchClose(m, j, '{', '}');
                                if (e < 0) return null;
                                j = e + 1;
                                continue;
                            }
                            break;
                        }
                        if (ch == ';' || ch == '}') break;
                        j++;
                    }
                    if (j < n && m[j] == '{') body = true;
                    break;
                }
                j++;
            }
            if (j >= n || (m[j] != ';' && m[j] != '{')) return null;

            var sig = new Sig { Class = cls, Name = name, Open = open, Close = close, HasBody = body, InClass = qual.Trim().Length == 0 && top.Key };
            sig.Chain.AddRange(enclosing);
            if (qual.Trim().Length > 0)
                foreach (string part in qual.Split(new[] { "::" }, StringSplitOptions.RemoveEmptyEntries))
                    sig.Chain.Add(Regex.Replace(part, @"\s*<.*>\s*", "").Trim());
            // ')' のあと、本体・初期化子リスト・「;」・「->」の手前までに const があるか
            string tail = m.Substring(close + 1, Math.Max(0, j - close - 1));
            int cut = tail.IndexOfAny(new[] { ':', '{', ';' });
            if (cut >= 0) tail = tail.Substring(0, cut);
            int arrow = tail.IndexOf("->", StringComparison.Ordinal);
            if (arrow >= 0) tail = tail.Substring(0, arrow);
            sig.IsConst = Regex.IsMatch(tail, @"\bconst\b");
            if (body)
            {
                int e = MatchClose(m, j, '{', '}');
                after = e < 0 ? n : e + 1;
            }
            else after = j + 1;
            return sig;
        }

        public static int MatchClose(string m, int open, char o, char c)
        {
            int depth = 0;
            for (int i = open; i < m.Length; i++)
            {
                if (m[i] == o) depth++;
                else if (m[i] == c) { depth--; if (depth == 0) return i; }
            }
            return -1;
        }
    }
}
