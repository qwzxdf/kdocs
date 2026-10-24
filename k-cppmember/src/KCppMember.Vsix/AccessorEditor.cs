using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppMember
{
    /// <summary>メンバー変数のゲッター・セッターを作る。ヘッダーの文字だけを見る(VS に依存しない)。</summary>
    internal static class AccessorEditor
    {
        public sealed class ClassSpan
        {
            public string Name;
            public int Open;   // '{' の位置
            public int Close;  // '}' の位置
            public bool IsStruct;
        }

        private static readonly Regex Head = new Regex(
            @"\b(class|struct)\s+(?:[A-Za-z_]\w*\s+)*?([A-Za-z_]\w*)\s*(?:final\s*)?(?::[^;{]*)?\{", RegexOptions.Compiled);

        /// <summary>text の中の class / struct の定義を、外側から順に列挙する(enum class は除く)。</summary>
        public static List<ClassSpan> All(string text)
        {
            var list = new List<ClassSpan>();
            foreach (Match m in Head.Matches(text))
            {
                string before = text.Substring(Math.Max(0, m.Index - 8), Math.Min(8, m.Index));
                if (Regex.IsMatch(before, @"enum\s*$")) continue;
                int open = m.Index + m.Length - 1;
                int close = FindClose(text, open);
                if (close < 0) continue;
                list.Add(new ClassSpan { Name = m.Groups[2].Value, Open = open, Close = close, IsStruct = m.Groups[1].Value == "struct" });
            }
            return list;
        }

        /// <summary>offset を中に含む、いちばん内側のクラス。</summary>
        public static ClassSpan ClassAt(string text, int offset)
        {
            ClassSpan best = null;
            foreach (var c in All(text))
                if (c.Open < offset && offset < c.Close && (best == null || c.Open > best.Open)) best = c;
            return best;
        }

        public static ClassSpan Find(string text, string className)
        {
            foreach (var c in All(text)) if (c.Name == className) return c;
            return null;
        }

        /// <summary>宣言の 1 行(「UINT stride_;」など)から、変数名を取り出す。関数や using などは null。</summary>
        public static string NameFromDeclarationLine(string line)
        {
            var m = Regex.Match(line, @"^\s*(?:mutable\s+)?[\w:<>,\* &]+?[\s\*&]([A-Za-z_]\w*)\s*(?:=[^;]*|\{[^;]*\})?;");
            if (!m.Success) return null;
            string head = line.TrimStart();
            if (Regex.IsMatch(head, @"^(return|using|typedef|friend|delete|goto|break|continue|public|private|protected)\b")) return null;
            return m.Groups[1].Value;
        }

        /// <summary>クラスの本文から、変数 name の宣言を探して型を返す。見つからない・配列・static は null。</summary>
        public static string FindMemberType(string text, ClassSpan c, string name)
        {
            string body = text.Substring(c.Open + 1, c.Close - c.Open - 1);
            var m = Regex.Match(body,
                @"(?m)^[ \t]*((?:(?:mutable|static|inline|constexpr|const)[ \t]+)*[\w:<>,\* &]*?[\w>])(\s+|[ \t]*[\*&]+[ \t]*)" + Regex.Escape(name) + @"[ \t]*(\[[^\]]*\])?[ \t]*(=[^;]*|\{[^;]*\})?;");
            if (!m.Success || m.Groups[3].Success) return null;
            string type = m.Groups[1].Value;
            if (Regex.IsMatch(type, @"\b(static|constexpr)\b")) return null;
            type = Regex.Replace(type, @"\bmutable\s+", "");
            if (m.Groups[2].Value.IndexOf('*') >= 0) type += "*";
            if (m.Groups[2].Value.IndexOf('&') >= 0) type += "&";
            return TypeInference.Clean(type.Trim());
        }

        /// <summary>stride_ → Stride、cpu_start_ → CpuStart、m_foo → Foo。</summary>
        public static string BaseName(string member)
        {
            string s = member;
            if (s.StartsWith("m_")) s = s.Substring(2);
            s = s.Trim('_');
            var sb = new StringBuilder();
            foreach (string part in s.Split(new[] { '_' }, StringSplitOptions.RemoveEmptyEntries))
                sb.Append(char.ToUpperInvariant(part[0])).Append(part.Substring(1));
            return sb.ToString();
        }

        private static bool IsSmall(string type)
        {
            if (type.EndsWith("*")) return true;
            return Regex.IsMatch(type, @"^(?:(?:unsigned|signed|short|long|int|char|float|double|bool|size_t|ptrdiff_t|u?int(?:8|16|32|64)_t|char\d*_t|wchar_t|std::nullptr_t|std::string_view|std::byte)\s*)+$")
                || Regex.IsMatch(type, @"^[A-Z][A-Z0-9_]*$"); // UINT / DWORD / HRESULT など
        }

        /// <summary>
        /// 追加する行を作る。ゲッターの名前は Get○○、セッターは Set○○。
        /// 小さい型は値、大きい型は const 参照。std::unique_ptr はゲッターだけで、生ポインターを返す。
        /// 本文にすでにあるものは足さない(skipped に名前を入れる)。
        /// </summary>
        public static List<string> MakeLines(string text, ClassSpan c, string member, string type, List<string> skipped)
        {
            string body = text.Substring(c.Open + 1, c.Close - c.Open - 1);
            string n = BaseName(member);
            var lines = new List<string>();
            var smart = Regex.Match(type, @"^std::unique_ptr\s*<\s*(.+?)\s*(?:,.*)?>$");

            string get = "Get" + n;
            if (Regex.IsMatch(body, @"\b" + get + @"\s*\(")) skipped.Add(get);
            else if (smart.Success) lines.Add(smart.Groups[1].Value + "* " + get + "() const { return " + member + ".get(); }");
            else if (IsSmall(type)) lines.Add(type + " " + get + "() const { return " + member + "; }");
            else lines.Add("const " + type + "& " + get + "() const { return " + member + "; }");

            string set = "Set" + n;
            if (smart.Success) { }
            else if (Regex.IsMatch(body, @"\b" + set + @"\s*\(")) skipped.Add(set);
            else if (IsSmall(type)) lines.Add("void " + set + "(" + type + " value) { " + member + " = value; }");
            else lines.Add("void " + set + "(const " + type + "& value) { " + member + " = value; }");
            return lines;
        }

        /// <summary>lines を、クラスの public: の末尾に足す編集を返す。public: が無ければ、先頭に作る。</summary>
        public static HeaderEditor.Edit PlanPublic(string text, ClassSpan c, List<string> lines, string eol)
        {
            string body = text.Substring(c.Open + 1, c.Close - c.Open - 1);
            // 直下(波括弧の深さ 0)のアクセス指定子
            var specs = new List<KeyValuePair<string, int>>();
            int depth = 0;
            for (int i = 0; i < body.Length; i++)
            {
                char ch = body[i];
                if (ch == '{') depth++;
                else if (ch == '}') depth--;
                else if (depth == 0 && ch == 'p' && (i == 0 || !(char.IsLetterOrDigit(body[i - 1]) || body[i - 1] == '_')))
                {
                    var s = Regex.Match(body.Substring(i), @"^(public|protected|private)\s*:(?!:)");
                    if (s.Success) specs.Add(new KeyValuePair<string, int>(s.Groups[1].Value, i));
                }
            }

            int lineStartOfClose = c.Close;
            while (lineStartOfClose > 0 && text[lineStartOfClose - 1] != '\n') lineStartOfClose--;
            bool braceFirst = text.Substring(lineStartOfClose, c.Close - lineStartOfClose).Trim().Length == 0;
            string closeIndent = braceFirst ? text.Substring(lineStartOfClose, c.Close - lineStartOfClose) : "";

            int pubIdx = specs.FindLastIndex(s => s.Key == "public");
            int boundary;            // この位置の「行の頭」の手前までが public の範囲
            string specIndent = closeIndent + " ";
            bool needSpec = false;
            if (pubIdx >= 0)
            {
                int pubAbs = c.Open + 1 + specs[pubIdx].Value;
                specIndent = LineIndent(text, pubAbs);
                boundary = pubIdx + 1 < specs.Count ? c.Open + 1 + specs[pubIdx + 1].Value : c.Close;
            }
            else if (c.IsStruct && specs.Count == 0)
            {
                boundary = c.Close;      // struct は何も書かなければ public
            }
            else
            {
                // public: を作って、本文の先頭(波括弧のすぐ後ろの行末)に入れる
                needSpec = true;
                boundary = -1;
            }

            var sb = new StringBuilder();
            if (needSpec)
            {
                int eolAt = text.IndexOf('\n', c.Open);
                int pos = eolAt < 0 ? c.Open + 1 : eolAt + 1;
                string indent = closeIndent + "  ";
                sb.Append(closeIndent).Append(" public:").Append(eol);
                foreach (string l in lines) sb.Append(indent).Append(l).Append(eol);
                sb.Append(eol);
                return new HeaderEditor.Edit { Position = pos, Text = sb.ToString() };
            }

            // boundary が指す行の頭から、空行をさかのぼって、最後の中身のある行の次を挿入位置にする
            int lineStart = boundary;
            while (lineStart > 0 && text[lineStart - 1] != '\n') lineStart--;
            bool boundaryAtLineHead = text.Substring(lineStart, boundary - lineStart).Trim().Length == 0;
            if (!boundaryAtLineHead) return new HeaderEditor.Edit { Position = boundary, Text = eol + string.Join(eol, lines) + eol };

            int insertAt = lineStart;
            string memberIndent = null;
            int p = lineStart - 1; // 直前の行末('\n')
            while (p > c.Open)
            {
                int s = p;
                while (s > 0 && text[s - 1] != '\n') s--;
                string prev = text.Substring(s, p - s).TrimEnd('\r');
                if (prev.Trim().Length == 0) { insertAt = s; p = s - 1; continue; }
                if (!Regex.IsMatch(prev, @"^\s*(public|protected|private)\s*:") && prev.Trim().Length > 0)
                    memberIndent = prev.Substring(0, prev.Length - prev.TrimStart().Length);
                break;
            }
            if (memberIndent == null) memberIndent = specIndent.Length == 0 ? "    " : specIndent + " ";
            foreach (string l in lines) sb.Append(memberIndent).Append(l).Append(eol);
            return new HeaderEditor.Edit { Position = insertAt, Text = sb.ToString() };
        }

        private static string LineIndent(string text, int pos)
        {
            int a = pos;
            while (a > 0 && text[a - 1] != '\n') a--;
            string s = text.Substring(a, pos - a);
            return s.Trim().Length == 0 ? s : "";
        }

        private static int FindClose(string s, int open)
        {
            int depth = 0;
            for (int i = open; i < s.Length; i++)
            {
                char ch = s[i];
                if (ch == '/' && i + 1 < s.Length && s[i + 1] == '/') { while (i < s.Length && s[i] != '\n') i++; continue; }
                if (ch == '/' && i + 1 < s.Length && s[i + 1] == '*')
                {
                    int e = s.IndexOf("*/", i + 2, StringComparison.Ordinal);
                    if (e < 0) return -1;
                    i = e + 1;
                    continue;
                }
                if (ch == '"' || ch == '\'')
                {
                    char q = ch;
                    for (i++; i < s.Length && s[i] != q; i++) if (s[i] == '\\') i++;
                    continue;
                }
                if (ch == '{') depth++;
                else if (ch == '}') { depth--; if (depth == 0) return i; }
            }
            return -1;
        }
    }
}
