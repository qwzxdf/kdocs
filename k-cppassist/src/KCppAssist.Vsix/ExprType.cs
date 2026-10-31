using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// 演算子を含む右辺(「a + b」「x &lt; y」「(float)n」「!flag」)の型を、部分の型から組み立てる。VS に依存しない。
    /// 部分の型(変数や関数の戻り値)は、呼び出し側が Quick Info から取ってくる。
    /// </summary>
    internal static class ExprType
    {
        public sealed class Binary
        {
            public int Class;                                              // 優先順位の群(1=||、2=&&、3=|、4=^、5=&、6=== !=、7=比較、8=シフト、9=+ -、10=* / %)
            public List<string> Ops = new List<string>();
            public List<KeyValuePair<string, int>> Operands = new List<KeyValuePair<string, int>>();   // 部分の式と、その位置
        }

        private static readonly string[] BuiltinWords = { "int", "unsigned", "signed", "short", "long", "char", "float", "double", "bool", "wchar_t", "size_t" };

        /// <summary>式全体を包む余分な括弧を外す。外した分の位置のずれを offset に返す。</summary>
        public static string StripParens(string e, out int offset)
        {
            offset = 0;
            while (true)
            {
                string t = e.Trim();
                int lead = e.Length - e.TrimStart().Length;
                if (t.Length >= 2 && t[0] == '(' && Matching(t, 0, '(', ')') == t.Length - 1 && !IsCastParen(t, t.Length - 1))
                {
                    e = t.Substring(1, t.Length - 2);
                    offset += lead + 1;
                    continue;
                }
                offset += lead;
                return t;
            }
        }

        private static int Matching(string s, int open, char o, char c)
        {
            int depth = 0;
            for (int i = open; i < s.Length; i++)
            {
                if (s[i] == '"' || s[i] == '\'')
                {
                    char q = s[i];
                    for (i++; i < s.Length && s[i] != q; i++) if (s[i] == '\\') i++;
                    continue;
                }
                if (s[i] == o) depth++;
                else if (s[i] == c) { depth--; if (depth == 0) return i; }
            }
            return -1;
        }

        /// <summary>s[close] の「)」が、キャストの括弧(「(float)」「(Foo*)」)か。変数を括っただけの「(a)」は違う。</summary>
        private static bool IsCastParen(string s, int close)
        {
            int depth = 0, open = -1;
            for (int i = close; i >= 0; i--)
            {
                if (s[i] == ')') depth++;
                else if (s[i] == '(') { depth--; if (depth == 0) { open = i; break; } }
            }
            if (open < 0) return false;
            if (open > 0 && (CppText.IsId(s[open - 1]) || s[open - 1] == '>' || s[open - 1] == ')' || s[open - 1] == ']')) return false;   // 関数呼び出し
            string inner = s.Substring(open + 1, close - open - 1).Trim();
            if (inner.Length == 0 || !Regex.IsMatch(inner, @"^[A-Za-z_][\w:<>\s\*&,]*$")) return false;
            if (Regex.IsMatch(inner, @"[\*&:<]")) return true;                       // Foo* / Foo& / ns::T / std::vector<int>
            return inner.Split(new[] { ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries).All(w => BuiltinWords.Contains(w) || w == "const");
        }

        /// <summary>「(T)x」の T。キャストでなければ null。</summary>
        public static string CastType(string e)
        {
            e = e.Trim();
            if (e.Length < 3 || e[0] != '(') return null;
            int close = Matching(e, 0, '(', ')');
            if (close < 0 || close == e.Length - 1) return null;
            if (!IsCastParen(e.Substring(0, close + 1), close)) return null;
            string rest = e.Substring(close + 1).TrimStart();
            if (rest.Length == 0 || !(CppText.IsId(rest[0]) || rest[0] == '(' || rest[0] == '-' || rest[0] == '+' || rest[0] == '*' || rest[0] == '&' || rest[0] == '!' || rest[0] == '~')) return null;
            return TypeInference.Clean(e.Substring(1, close - 1));
        }

        private static int ClassOf(string op)
        {
            switch (op)
            {
                case "||": return 1;
                case "&&": return 2;
                case "|": return 3;
                case "^": return 4;
                case "&": return 5;
                case "==": case "!=": return 6;
                case "<": case ">": case "<=": case ">=": return 7;
                case "<<": case ">>": return 8;
                case "+": case "-": return 9;
                case "*": case "/": case "%": return 10;
            }
            return 0;
        }

        /// <summary>
        /// 深さ 0 の二項演算子のうち、いちばん優先順位が低い群で、式を分ける。二項演算子がなければ null。
        /// 文字列・括弧の中、テンプレートの「&lt; &gt;」(前後に空白のないもの)、単項の「-」「*」「&amp;」は数えない。
        /// </summary>
        public static Binary SplitBinary(string e)
        {
            var found = new List<KeyValuePair<int, string>>();    // 位置、演算子
            int depth = 0;
            for (int i = 0; i < e.Length; i++)
            {
                char c = e[i];
                if (c == '"' || c == '\'')
                {
                    for (i++; i < e.Length && e[i] != c; i++) if (e[i] == '\\') i++;
                    continue;
                }
                if (c == '(' || c == '[' || c == '{') { depth++; continue; }
                if (c == ')' || c == ']' || c == '}') { depth--; continue; }
                if (depth != 0) continue;

                string op = null;
                if (i + 1 < e.Length)
                {
                    string two = e.Substring(i, 2);
                    if (two == "||" || two == "&&" || two == "==" || two == "!=" || two == "<=" || two == ">=" || two == "<<" || two == ">>") op = two;
                }
                if (op == null && "|^&<>+-*/%".IndexOf(c) >= 0) op = c.ToString();
                if (op == null) continue;

                int after = i + op.Length;
                // 「->」「++」「--」「::」「+=」のような別の記号の一部は除く
                if (c == '-' && i + 1 < e.Length && (e[i + 1] == '>' || e[i + 1] == '-')) { i++; continue; }
                if (c == '+' && i + 1 < e.Length && e[i + 1] == '+') { i++; continue; }
                if (c == '>' && i > 0 && e[i - 1] == '-') continue;
                if (after < e.Length && e[after] == '=' && op.Length == 1 && op != "<" && op != ">") { i = after; continue; }
                if (after < e.Length && e[after] == '=' && (op == "<<" || op == ">>")) { i = after; continue; }

                bool spacedBoth = i > 0 && char.IsWhiteSpace(e[i - 1]) && after < e.Length && char.IsWhiteSpace(e[after]);
                if ((op == "<" || op == ">" || op == "<=" || op == ">=" || op == "<<" || op == ">>") && !spacedBoth) { i = after - 1; continue; }

                // 左に式の終わりがあるときだけ二項演算子
                int p = i - 1;
                while (p >= 0 && char.IsWhiteSpace(e[p])) p--;
                if (p < 0) { i = after - 1; continue; }
                char prev = e[p];
                bool operandEnd = CppText.IsId(prev) || prev == ')' || prev == ']' || prev == '"' || prev == '\'' || prev == '}';
                if (!operandEnd) { i = after - 1; continue; }
                // 指数の符号(1e-3)
                if ((op == "-" || op == "+") && (prev == 'e' || prev == 'E') && Regex.IsMatch(e.Substring(0, p + 1), @"(?<![\w.])\d[\w.]*[eE]$")) continue;
                // (float)-x のように、キャストの直後の符号は単項
                if (prev == ')' && (op == "-" || op == "+" || op == "*" || op == "&") && IsCastParen(e.Substring(0, p + 1), p)) continue;

                found.Add(new KeyValuePair<int, string>(i, op));
                i = after - 1;
            }
            if (found.Count == 0) return null;

            int low = found.Min(f => ClassOf(f.Value));
            var r = new Binary { Class = low };
            int start = 0;
            foreach (var f in found.Where(f => ClassOf(f.Value) == low))
            {
                AddOperand(r, e, start, f.Key);
                r.Ops.Add(f.Value);
                start = f.Key + f.Value.Length;
            }
            AddOperand(r, e, start, e.Length);
            return r.Operands.Any(o => o.Key.Length == 0) ? null : r;
        }

        private static void AddOperand(Binary r, string e, int from, int to)
        {
            string part = e.Substring(from, to - from);
            int lead = part.Length - part.TrimStart().Length;
            r.Operands.Add(new KeyValuePair<string, int>(part.Trim(), from + lead));
        }

        /// <summary>単項演算子(「!x」「-x」「~x」「&amp;x」「*p」)。そうでなければ null。operand と位置を返す。</summary>
        public static string Unary(string e, out string op, out int offset)
        {
            op = null; offset = 0;
            e = e.Trim();
            if (e.Length < 2) return null;
            char c = e[0];
            if ("!-+~&*".IndexOf(c) < 0) return null;
            if (e.Length > 1 && e[1] == c && (c == '-' || c == '+')) return null;       // ++x / --x
            op = c.ToString();
            string rest = e.Substring(1);
            offset = 1 + (rest.Length - rest.TrimStart().Length);
            return rest.Trim();
        }

        // ---- 算術の型 ----

        private struct Arith { public int Rank; public string Name; }

        private static readonly Dictionary<string, Arith> Table = BuildTable();

        private static Dictionary<string, Arith> BuildTable()
        {
            var d = new Dictionary<string, Arith>();
            Action<int, string, string[]> add = (rank, name, aliases) =>
            {
                d[name] = new Arith { Rank = rank, Name = name };
                foreach (string a in aliases) d[a] = new Arith { Rank = rank, Name = name };
            };
            add(1, "int", new[] { "bool", "char", "signed char", "unsigned char", "short", "unsigned short", "short int", "unsigned short int", "wchar_t", "char8_t", "char16_t",
                                  "int8_t", "uint8_t", "int16_t", "uint16_t", "BYTE", "WORD", "INT", "int32_t", "signed", "signed int", "INT32", "BOOL" });
            add(2, "unsigned int", new[] { "unsigned", "UINT", "uint32_t", "UINT32", "DWORD", "ULONG", "char32_t" });
            add(3, "long", new[] { "long int", "LONG" });
            add(4, "unsigned long", new[] { "unsigned long int" });
            add(5, "long long", new[] { "long long int", "int64_t", "INT64", "ptrdiff_t", "intptr_t", "LONGLONG", "ssize_t", "LONG_PTR", "INT_PTR" });
            add(6, "unsigned long long", new[] { "unsigned long long int", "uint64_t", "UINT64", "size_t", "SIZE_T", "uintptr_t", "ULONGLONG", "UINT_PTR", "ULONG_PTR", "DWORD64" });
            add(7, "float", new string[0]);
            add(8, "double", new string[0]);
            add(9, "long double", new string[0]);
            return d;
        }

        private static string Norm(string t)
        {
            t = Regex.Replace(t ?? "", @"\bconst\b|\bvolatile\b", " ");
            t = Regex.Replace(t, @"^\s*(::)?(std::)?", "");
            return Regex.Replace(t, @"\s+", " ").Trim();
        }

        private static bool TryArith(string type, out Arith a) { return Table.TryGetValue(Norm(type), out a); }

        private static bool IsPointer(string type) { return Norm(type).EndsWith("*"); }

        /// <summary>
        /// 二項演算の結果の型。比較と論理は bool、シフトは左の型、それ以外は通常の算術変換
        /// (型の綴りがそろっていて int 以上なら、その綴りのまま)。クラスが混じるときは、最初のクラスの型。決められなければ null。
        /// </summary>
        public static string BinaryResult(Binary b, IList<string> types)
        {
            if (types.Any(string.IsNullOrWhiteSpace)) return null;
            if (b.Class <= 2 || b.Class == 6 || b.Class == 7) return "bool";

            if (b.Class == 8)
            {
                Arith la;
                return TryArith(types[0], out la) ? Promote(types[0]) : TypeInference.Clean(types[0]);
            }

            var arith = new List<Arith>();
            var classes = new List<string>();
            var pointers = new List<string>();
            foreach (string t in types)
            {
                Arith a;
                if (TryArith(t, out a)) arith.Add(a);
                else if (IsPointer(t)) pointers.Add(TypeInference.Clean(t));
                else classes.Add(TypeInference.Clean(t));
            }
            if (classes.Count > 0)
            {
                string first = classes[0];
                if (classes.Count > 1 && b.Ops.Contains("-") && Regex.IsMatch(first, @"time_point|iterator")) return null;
                return first;
            }
            if (pointers.Count > 0)
            {
                if (pointers.Count == 1 && (b.Class == 9)) return pointers[0];
                if (pointers.Count == 2 && b.Class == 9 && b.Ops.All(o => o == "-")) return "ptrdiff_t";
                return null;
            }

            int rank = arith.Max(a => a.Rank);
            // 綴りがすべて同じで、int 以上なら、その綴りを残す(UINT + UINT は UINT)
            string spelling = Norm(types[0]);
            if (types.All(t => Norm(t) == spelling) && Table[spelling].Rank >= 2 || types.All(t => Norm(t) == spelling) && spelling == "int")
                return spelling;
            return Table.Values.First(a => a.Rank == rank).Name;
        }

        private static string Promote(string type)
        {
            Arith a;
            if (!TryArith(type, out a)) return type;
            string n = Norm(type);
            return a.Rank <= 1 ? "int" : n;
        }

        /// <summary>単項演算の結果の型。</summary>
        public static string UnaryResult(string op, string operandType)
        {
            if (op == "!") return "bool";
            if (string.IsNullOrWhiteSpace(operandType)) return null;
            if (op == "&") return TypeInference.Clean(operandType) + "*";
            if (op == "*")
            {
                string n = TypeInference.Clean(operandType);
                return n != null && n.EndsWith("*") ? n.Substring(0, n.Length - 1).TrimEnd() : null;
            }
            Arith a;
            if (TryArith(operandType, out a)) return Promote(operandType);
            return TypeInference.Clean(operandType);
        }
    }
}
