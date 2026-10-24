using System;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>右辺の式と Quick Info の文字から、変数の型を決める。VS に依存しない。</summary>
    internal static class TypeInference
    {
        private static readonly Regex Noise = new Regex(
            @"\b(virtual|static|inline|constexpr|consteval|extern|friend|explicit|volatile|__stdcall|__cdecl|__fastcall|__vectorcall|__forceinline|_Check_return_|_Must_inspect_result_)\b|\[\[nodiscard\]\]",
            RegexOptions.Compiled);

        /// <summary>
        /// 「cond ? A : B」を、A と B の 2 つ(前後の空白を除いたもの。値は rhs の中での位置)に分ける。
        /// 括弧・波括弧・文字列の中の ? と :、::、入れ子の三項演算子は、外側だけを数える。三項演算子でなければ null。
        /// </summary>
        public static System.Collections.Generic.List<System.Collections.Generic.KeyValuePair<string, int>> TernaryBranches(string rhs)
        {
            int depth = 0, q = -1, nested = 0, colon = -1;
            for (int i = 0; i < rhs.Length; i++)
            {
                char c = rhs[i];
                if (c == '"' || c == '\'')
                {
                    for (i++; i < rhs.Length && rhs[i] != c; i++) if (rhs[i] == '\\') i++;
                    continue;
                }
                if (c == '(' || c == '[' || c == '{') depth++;
                else if (c == ')' || c == ']' || c == '}') depth--;
                else if (depth == 0 && c == '?')
                {
                    if (q < 0) q = i; else nested++;
                }
                else if (depth == 0 && c == ':' && q >= 0)
                {
                    if ((i + 1 < rhs.Length && rhs[i + 1] == ':') || (i > 0 && rhs[i - 1] == ':')) continue;
                    if (nested > 0) nested--; else { colon = i; break; }
                }
            }
            if (q < 0 || colon < 0) return null;
            var list = new System.Collections.Generic.List<System.Collections.Generic.KeyValuePair<string, int>>();
            foreach (var range in new[] { new[] { q + 1, colon }, new[] { colon + 1, rhs.Length } })
            {
                string part = rhs.Substring(range[0], range[1] - range[0]);
                int lead = part.Length - part.TrimStart().Length;
                list.Add(new System.Collections.Generic.KeyValuePair<string, int>(part.Trim(), range[0] + lead));
            }
            return list;
        }

        /// <summary>式そのものから決められる型。決められなければ null。</summary>
        public static string FromExpression(string rhs)
        {
            rhs = rhs.Trim();
            Match m;
            if (rhs == "true" || rhs == "false") return "bool";
            if (rhs == "nullptr") return "std::nullptr_t";
            if (Regex.IsMatch(rhs, @"^-?\d+$")) return "int";
            if (Regex.IsMatch(rhs, @"^-?\d+[uU]$")) return "unsigned int";
            if (Regex.IsMatch(rhs, @"^-?\d+([uU][lL]{2}|[lL]{2}[uU])$")) return "unsigned long long";
            if (Regex.IsMatch(rhs, @"^-?\d+[lL]{2}$")) return "long long";
            if (Regex.IsMatch(rhs, @"^-?\d+[uU][lL]$")) return "unsigned long";
            if (Regex.IsMatch(rhs, @"^-?\d+[lL]$")) return "long";
            if (Regex.IsMatch(rhs, @"^-?0[xX][0-9a-fA-F]+$")) return "int";
            if (Regex.IsMatch(rhs, @"^-?(\d+\.\d*|\.\d+)([eE][-+]?\d+)?[fF]$") || Regex.IsMatch(rhs, @"^-?\d+[fF]$")) return "float";
            if (Regex.IsMatch(rhs, @"^-?(\d+\.\d*|\.\d+)([eE][-+]?\d+)?$")) return "double";
            if (Regex.IsMatch(rhs, @"^'(\\.|[^'\\])'$")) return "char";
            if (Regex.IsMatch(rhs, "^\"(\\\\.|[^\"\\\\])*\"$")) return "const char*";
            if (Regex.IsMatch(rhs, @"^sizeof\b")) return "size_t";

            m = Regex.Match(rhs, @"^(?:static|reinterpret|const|dynamic)_cast\s*<\s*(.+?)\s*>\s*\(.*\)$");
            if (m.Success) return Clean(m.Groups[1].Value);
            m = Regex.Match(rhs, @"^(?:std::)?make_unique\s*<\s*(.+?)\s*>\s*\(.*\)$");
            if (m.Success) return "std::unique_ptr<" + m.Groups[1].Value + ">";
            m = Regex.Match(rhs, @"^(?:std::)?make_shared\s*<\s*(.+?)\s*>\s*\(.*\)$");
            if (m.Success) return "std::shared_ptr<" + m.Groups[1].Value + ">";
            m = Regex.Match(rhs, @"^new\s+([\w:<>]+)");
            if (m.Success) return m.Groups[1].Value + "*";
            return null;
        }

        /// <summary>関数呼び出しの Quick Info(「virtual UINT __stdcall ID3D12Device::Foo(...)」など)から、戻り値の型を取り出す。</summary>
        public static string FromFunctionInfo(string info, string func)
        {
            if (string.IsNullOrEmpty(info)) return null;
            var m = Regex.Match(info, @"((?:[A-Za-z_]\w*(?:<[^<>]*>)?::)*)" + Regex.Escape(func) + @"\s*\(");
            if (!m.Success) return null;
            string head = info.Substring(0, m.Index);
            int nl = head.LastIndexOf('\n');
            if (nl >= 0) head = head.Substring(nl + 1);
            head = Regex.Replace(head, @"^\s*\([^)]*\)\s*", ""); // 「(関数)」などの前置き
            return Clean(head);
        }

        /// <summary>変数や引数の Quick Info(「(parameter) T name」「T Class::name」)から、型を取り出す。</summary>
        public static string FromVariableInfo(string info, string name)
        {
            if (string.IsNullOrEmpty(info)) return null;
            string first = info.Split('\n')[0].Trim();
            first = Regex.Replace(first, @"^\s*\([^)]*\)\s*", "");
            var m = Regex.Match(first, @"^(.+?)\s+(?:[A-Za-z_]\w*(?:<[^<>]*>)?::)*" + Regex.Escape(name) + @"\s*(\[.*\])?$");
            return m.Success ? Clean(m.Groups[1].Value) : null;
        }

        /// <summary>const・参照・呼び出し規約などを外して、値の型にそろえる。</summary>
        public static string Clean(string t)
        {
            if (t == null) return null;
            t = Noise.Replace(t, " ");
            t = Regex.Replace(t, @"\s+", " ").Trim();
            t = Regex.Replace(t, @"\s*&{1,2}$", "").Trim();
            if (t.IndexOf('*') < 0)
            {
                t = Regex.Replace(t, @"^const\s+", "");
                t = Regex.Replace(t, @"\s+const$", "");
            }
            t = Regex.Replace(t, @"\s+\*", "*").Trim();
            if (t.Length == 0 || t == "void" || t.Contains("auto")) return null;
            return t;
        }
    }
}
