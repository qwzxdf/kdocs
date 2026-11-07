using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist.ErrorLog
{
    /// <summary>
    /// MSVC が出す型名を、人間が書く形に直す。
    ///   class std::unique_ptr&lt;class prest::Engine,struct std::default_delete&lt;class prest::Engine&gt; &gt;
    ///   → std::unique_ptr&lt;prest::Engine&gt;
    /// 標準ライブラリの「既定のテンプレート引数」(allocator、char_traits、default_delete など)を落とし、
    /// class / struct / 呼び出し規約を消し、「X const &amp;」を「const X&amp;」に直す。
    /// </summary>
    public static class TypePretty
    {
        private static readonly Regex DeclSpec = new Regex(@"__declspec\((?:dllimport|dllexport)\)\s*", RegexOptions.Compiled);
        private static readonly Regex CallConv = new Regex(@"\b__(?:cdecl|stdcall|thiscall|fastcall|vectorcall|clrcall|ptr64|ptr32|unaligned|restrict)\b\s?", RegexOptions.Compiled);
        private static readonly Regex TagKeyword = new Regex(@"\b(?:class|struct|union|enum)\s+(?=[A-Za-z_:`(<{])", RegexOptions.Compiled);
        private static readonly Regex Ident = new Regex(@"[A-Za-z_][\w:]*$", RegexOptions.Compiled);
        private static readonly Regex ConstTail = new Regex(@"\s+const(?<r>(?:\s*[&*]+)?)\s*$", RegexOptions.Compiled);
        private static readonly Regex SpaceBeforeRef = new Regex(@"(?<=[\w>\)\]]) +(?=[&*])", RegexOptions.Compiled);
        private static readonly Regex CommaSpace = new Regex(@",(?=\S)", RegexOptions.Compiled);
        private static readonly Regex Spaces = new Regex(@"[ \t]{2,}", RegexOptions.Compiled);
        private static readonly Regex IterInner = new Regex(@"^std::(?<val>_\w+_val)<std::_Simple_types<(?<t>.+)>>$", RegexOptions.Compiled);

        /// <summary>型の文字列を、読みやすい形にする。</summary>
        public static string Type(string s)
        {
            if (string.IsNullOrWhiteSpace(s)) return "";
            if (!ErrorLogSettings.ShortenTypes) return s.Trim();
            try
            {
                string x = Simplify(Clean(s));
                x = FixConst(x.Trim());
                return Tidy(x);
            }
            catch (Exception) { return s.Trim(); }
        }

        /// <summary>呼び出し規約・class / struct などの印を消す(テンプレート引数の整理はしない)。</summary>
        public static string Clean(string s)
        {
            s = DeclSpec.Replace(s, "");
            s = CallConv.Replace(s, "");
            s = TagKeyword.Replace(s, "");
            s = s.Replace("(anonymous namespace)", "{匿名}").Replace("`anonymous namespace'", "{匿名}");
            s = s.Replace("__cxx11::", "").Replace("__1::", "");
            return s;
        }

        /// <summary>空白を整える。</summary>
        public static string Tidy(string s)
        {
            s = SpaceBeforeRef.Replace(s, "");
            s = CommaSpace.Replace(s, ", ");
            s = Spaces.Replace(s, " ");
            return s.Trim();
        }

        /// <summary>「X const &amp;」を「const X&amp;」に直す。X にポインターが入るときは、そのままにする。</summary>
        public static string FixConst(string a)
        {
            a = a.Trim();
            Match m = ConstTail.Match(a);
            if (!m.Success) return a;
            string t = a.Substring(0, m.Index).Trim();
            if (t.Length == 0 || t.StartsWith("const ", StringComparison.Ordinal)) return a;
            if (HasTopLevel(t, '*') || HasTopLevel(t, '&') || HasTopLevel(t, '(')) return a;
            return "const " + t + Regex.Replace(m.Groups["r"].Value, @"\s+", "");
        }

        private static bool HasTopLevel(string s, char ch)
        {
            int depth = 0;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '<' || c == '[' || c == '{') depth++;
                else if ((c == '>' && !(i > 0 && s[i - 1] == '-')) || c == ']' || c == '}') depth--;
                else if (c == ch && depth == 0) return true;
                else if (c == '(' && ch != '(') { depth++; }
                else if (c == ')' && ch != '(') { depth--; }
            }
            return false;
        }

        // ---- テンプレート引数の整理 ----

        public static string Simplify(string s)
        {
            var sb = new StringBuilder(s.Length);
            int i = 0;
            while (i < s.Length)
            {
                char c = s[i];
                if (c == '<' && IsTemplateOpen(s, i))
                {
                    int j = FindClose(s, i);
                    if (j < 0) { sb.Append(c); i++; continue; }

                    string inner = s.Substring(i + 1, j - i - 1);
                    string soFar = sb.ToString();
                    Match q = Ident.Match(soFar);
                    string qual = q.Success ? q.Value : "";
                    if (qual.StartsWith("::", StringComparison.Ordinal)) qual = qual.Substring(2);

                    var args = new List<string>();
                    foreach (string a in SplitTop(inner))
                        args.Add(FixConst(Simplify(a.Trim())));

                    string alias;
                    ApplyRules(qual, args, out alias);
                    if (alias != null)
                    {
                        sb.Length -= q.Success ? q.Value.Length : 0;
                        sb.Append(alias);
                    }
                    else
                    {
                        sb.Append('<').Append(string.Join(", ", args)).Append('>');
                    }
                    i = j + 1;
                    continue;
                }
                sb.Append(c);
                i++;
            }
            return sb.ToString();
        }

        private static bool IsIdentChar(char c) { return char.IsLetterOrDigit(c) || c == '_'; }

        private static bool EndsWithOperator(string s, int end)
        {
            // s[0..end) の末尾が "operator" か
            return end >= 8 && string.CompareOrdinal(s, end - 8, "operator", 0, 8) == 0
                   && (end == 8 || !IsIdentChar(s[end - 9]));
        }

        private static bool IsTemplateOpen(string s, int i)
        {
            if (i == 0) return false;
            char p = s[i - 1];
            return IsIdentChar(p) && !EndsWithOperator(s, i);
        }

        // "<lambda_1>" のように、"::" の直後の < ... > も、対として数える
        private static bool CountsAsOpen(string s, int i)
        {
            if (i == 0) return false;
            char p = s[i - 1];
            if (p == ':') return true;
            return IsIdentChar(p) && !EndsWithOperator(s, i);
        }

        private static bool CountsAsClose(string s, int i)
        {
            if (i > 0 && s[i - 1] == '-') return false;
            return !EndsWithOperator(s, i);
        }

        private static int FindClose(string s, int open)
        {
            int depth = 0;
            for (int k = open; k < s.Length; k++)
            {
                char c = s[k];
                if (c == '<' && CountsAsOpen(s, k)) depth++;
                else if (c == '>' && CountsAsClose(s, k))
                {
                    depth--;
                    if (depth == 0) return k;
                }
            }
            return -1;
        }

        /// <summary>最上位のカンマで分ける(&lt;&gt; () [] {} の中は分けない)。</summary>
        public static List<string> SplitTop(string s)
        {
            var list = new List<string>();
            int depth = 0, start = 0;
            for (int k = 0; k < s.Length; k++)
            {
                char c = s[k];
                if (c == '<' && CountsAsOpen(s, k)) depth++;
                else if (c == '>' && CountsAsClose(s, k)) depth--;
                else if (c == '(' || c == '[' || c == '{') depth++;
                else if (c == ')' || c == ']' || c == '}') depth--;
                else if (c == ',' && depth == 0)
                {
                    list.Add(s.Substring(start, k - start));
                    start = k + 1;
                }
            }
            string last = s.Substring(start);
            if (last.Trim().Length > 0 || list.Count > 0) list.Add(last);
            return list;
        }

        private static string Compact(string s) { return Regex.Replace(s, @"\s+", ""); }
        private static bool Same(string a, string b) { return Compact(a) == Compact(b); }

        private static void DropDefaults(List<string> args, int minKeep, Func<int, string> expected)
        {
            while (args.Count > minKeep)
            {
                string e = expected(args.Count - 1);
                if (e == null || !Same(args[args.Count - 1], e)) break;
                args.RemoveAt(args.Count - 1);
            }
        }

        private static string CharAlias(string c, string stem)
        {
            switch (c)
            {
                case "char": return "std::" + stem;
                case "wchar_t": return "std::w" + stem;
                case "char8_t": return "std::u8" + stem;
                case "char16_t": return "std::u16" + stem;
                case "char32_t": return "std::u32" + stem;
            }
            return null;
        }

        private static readonly Dictionary<string, string> CharStreams = new Dictionary<string, string>
        {
            ["std::basic_ostream"] = "ostream",
            ["std::basic_istream"] = "istream",
            ["std::basic_iostream"] = "iostream",
            ["std::basic_ofstream"] = "ofstream",
            ["std::basic_ifstream"] = "ifstream",
            ["std::basic_fstream"] = "fstream",
            ["std::basic_streambuf"] = "streambuf",
            ["std::basic_ios"] = "ios",
            ["std::basic_filebuf"] = "filebuf"
        };

        private static readonly Dictionary<string, string> StringStreams = new Dictionary<string, string>
        {
            ["std::basic_ostringstream"] = "ostringstream",
            ["std::basic_istringstream"] = "istringstream",
            ["std::basic_stringstream"] = "stringstream",
            ["std::basic_stringbuf"] = "stringbuf"
        };

        // MSVC 内部のイテレーター名 → 人間が書く名前
        private static readonly Dictionary<string, string[]> Iterators = new Dictionary<string, string[]>
        {
            ["std::_Vector_iterator"] = new[] { "std::vector", "iterator" },
            ["std::_Vector_const_iterator"] = new[] { "std::vector", "const_iterator" },
            ["std::_List_iterator"] = new[] { "std::list", "iterator" },
            ["std::_List_const_iterator"] = new[] { "std::list", "const_iterator" },
            ["std::_String_iterator"] = new[] { "std::basic_string", "iterator" },
            ["std::_String_const_iterator"] = new[] { "std::basic_string", "const_iterator" }
        };

        private static void ApplyRules(string qual, List<string> args, out string alias)
        {
            alias = null;
            if (args.Count == 0) return;

            switch (qual)
            {
                case "std::basic_string":
                    DropDefaults(args, 1, k => k == 1 ? "std::char_traits<" + args[0] + ">" : k == 2 ? "std::allocator<" + args[0] + ">" : null);
                    if (args.Count == 1) alias = CharAlias(args[0], "string");
                    return;
                case "std::basic_string_view":
                    DropDefaults(args, 1, k => k == 1 ? "std::char_traits<" + args[0] + ">" : null);
                    if (args.Count == 1) alias = CharAlias(args[0], "string_view");
                    return;
                case "std::vector":
                case "std::deque":
                case "std::list":
                case "std::forward_list":
                    DropDefaults(args, 1, k => k == 1 ? "std::allocator<" + args[0] + ">" : null);
                    return;
                case "std::set":
                case "std::multiset":
                    DropDefaults(args, 1, k => k == 1 ? "std::less<" + args[0] + ">" : k == 2 ? "std::allocator<" + args[0] + ">" : null);
                    return;
                case "std::map":
                case "std::multimap":
                    if (args.Count >= 2)
                        DropDefaults(args, 2, k => k == 2 ? "std::less<" + args[0] + ">"
                            : k == 3 ? "std::allocator<std::pair<const " + args[0] + ", " + args[1] + ">>" : null);
                    return;
                case "std::unordered_map":
                case "std::unordered_multimap":
                    if (args.Count >= 2)
                        DropDefaults(args, 2, k => k == 2 ? "std::hash<" + args[0] + ">"
                            : k == 3 ? "std::equal_to<" + args[0] + ">"
                            : k == 4 ? "std::allocator<std::pair<const " + args[0] + ", " + args[1] + ">>" : null);
                    return;
                case "std::unordered_set":
                case "std::unordered_multiset":
                    DropDefaults(args, 1, k => k == 1 ? "std::hash<" + args[0] + ">"
                        : k == 2 ? "std::equal_to<" + args[0] + ">"
                        : k == 3 ? "std::allocator<" + args[0] + ">" : null);
                    return;
                case "std::unique_ptr":
                    DropDefaults(args, 1, k => k == 1 ? "std::default_delete<" + args[0] + ">" : null);
                    return;
                case "std::stack":
                case "std::queue":
                    DropDefaults(args, 1, k => k == 1 ? "std::deque<" + args[0] + ">" : null);
                    return;
                case "std::priority_queue":
                    if (args.Count == 3 && args[2].StartsWith("std::less<", StringComparison.Ordinal)) args.RemoveAt(2);
                    if (args.Count == 2 && Same(args[1], "std::vector<" + args[0] + ">")) args.RemoveAt(1);
                    return;
                case "std::span":
                    if (args.Count == 2 && args[1] == "18446744073709551615") args.RemoveAt(1);
                    return;
            }

            string stem;
            if (CharStreams.TryGetValue(qual, out stem))
            {
                DropDefaults(args, 1, k => k == 1 ? "std::char_traits<" + args[0] + ">" : null);
                if (args.Count == 1) alias = CharAlias(args[0], stem);
                return;
            }
            if (StringStreams.TryGetValue(qual, out stem))
            {
                DropDefaults(args, 1, k => k == 1 ? "std::char_traits<" + args[0] + ">" : k == 2 ? "std::allocator<" + args[0] + ">" : null);
                if (args.Count == 1) alias = CharAlias(args[0], stem);
                return;
            }

            if (qual.StartsWith("std::make_", StringComparison.Ordinal) && args.Count >= 2 && args[args.Count - 1] == "0")
            {
                args.RemoveAt(args.Count - 1);   // SFINAE 用の「0」
                return;
            }

            string[] it;
            if (Iterators.TryGetValue(qual, out it) && args.Count == 1)
            {
                Match m = IterInner.Match(args[0]);
                if (m.Success)
                {
                    string t = m.Groups["t"].Value;
                    string owner = it[0] + "<" + t + ">";
                    if (it[0] == "std::basic_string")
                    {
                        string a = CharAlias(t, "string");
                        if (a != null) owner = a;
                    }
                    alias = owner + "::" + it[1];
                }
            }
        }
    }
}
