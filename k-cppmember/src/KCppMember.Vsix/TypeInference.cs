using System;
using System.Text.RegularExpressions;

namespace KCppMember
{
    /// <summary>右辺の式と Quick Info の文字から、変数の型を決める。VS に依存しない。</summary>
    internal static class TypeInference
    {
        private static readonly Regex Noise = new Regex(
            @"\b(virtual|static|inline|constexpr|consteval|extern|friend|explicit|volatile|__stdcall|__cdecl|__fastcall|__vectorcall|__forceinline|_Check_return_|_Must_inspect_result_)\b|\[\[nodiscard\]\]",
            RegexOptions.Compiled);

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
