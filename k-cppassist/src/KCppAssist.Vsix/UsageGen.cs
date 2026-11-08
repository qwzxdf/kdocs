using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// 呼び出しの書き方(Foo(a, 1)、obj.Foo(x)、this->Foo())から、関数の宣言を決める。VS に依存しない。
    /// 引数の型は、リテラルと、同じ関数の中で見える変数の宣言から決める。決められないものは、int にして Unknown に入れる。
    /// </summary>
    internal static class UsageGen
    {
        public sealed class Usage
        {
            public string Name;
            public string Receiver;             // null: 修飾なし。"this": this-> 。それ以外: obj.Foo の obj
            public string ReceiverType;         // obj の型(ポインター・参照・const・スマートポインターを除いたクラス名)。決められなければ null
            public List<string> Args = new List<string>();
            public List<string> ParamTypes = new List<string>();
            public List<string> ParamNames = new List<string>();
            public List<string> Unknown = new List<string>();     // 型を決められなかった引数の式
            public string ReturnType;
            public bool ReturnGuessed;          // 戻り値の型を決められなかった(int にした)
            public int NameStart;

            public string Signature()
            {
                var ps = new List<string>();
                for (int i = 0; i < ParamTypes.Count; i++) ps.Add(ParamTypes[i] + " " + ParamNames[i]);
                return ReturnType + " " + Name + "(" + string.Join(", ", ps) + ")";
            }

            public string Declaration() { return Signature() + ";"; }
        }

        private static readonly HashSet<string> NotCalls = new HashSet<string>
        {
            "if","for","while","switch","return","sizeof","alignof","decltype","catch","static_assert","throw","new","delete","else","do","case","defined","typeid","noexcept"
        };

        private static readonly HashSet<string> NotTypes = new HashSet<string>
        {
            "return","else","delete","case","new","goto","throw","co_return","typedef","using","namespace","public","private","protected","do","if","while","for","switch"
        };

        private sealed class Call { public int NameStart, NameEnd, Open, Close; public string Receiver; }

        private static readonly Regex CallRx = new Regex(@"(?:([A-Za-z_]\w*(?:\s*(?:\.|->)\s*[A-Za-z_]\w*)*)\s*(\.|->)\s*)?(?<![\w])([A-Za-z_]\w*)\s*\(", RegexOptions.Compiled);

        public static Usage Find(string text, int caret, out string why)
        {
            why = null;
            string m = CppText.Mask(text);
            int ls = LineStart(text, caret);
            int le = text.IndexOf('\n', Math.Min(caret, text.Length));
            if (le < 0) le = text.Length;
            string line = m.Substring(ls, le - ls);

            // 行にある呼び出しのうち、カーソルを含むもの(複数なら、いちばん内側)。含むものがなければ、行の最初の呼び出し
            Call best = null, first = null;
            foreach (Match x in CallRx.Matches(line))
            {
                string name = x.Groups[3].Value;
                if (NotCalls.Contains(name)) continue;
                var c = new Call { NameStart = ls + x.Groups[3].Index, NameEnd = ls + x.Groups[3].Index + name.Length, Open = ls + x.Index + x.Length - 1 };
                c.Close = MatchParen(m, c.Open);
                if (c.Close < 0) continue;
                if (x.Groups[1].Success) c.Receiver = Regex.Replace(x.Groups[1].Value, @"\s+", "") + (x.Groups[2].Value == "." ? "." : "->");
                // 「Type name(args)」の宣言(戻り値の型がある)は呼び出しではない
                string before = line.Substring(0, x.Index).TrimEnd();
                if (!x.Groups[1].Success)
                {
                    // 「Type name(args)」は宣言(コンストラクターの呼び出し)で、関数の呼び出しではない
                    Match dm = Regex.Match(before + " ", @"(?:^|[;{}])\s*(?:const\s+)?([A-Za-z_][\w:]*)(?:\s*<[^;(){}]*>)?[\s&*]+$");
                    if (dm.Success && !NotTypes.Contains(dm.Groups[1].Value) && !Regex.IsMatch(dm.Groups[1].Value, @"^(?:co_await|co_yield|else)$")) continue;
                }
                if (first == null) first = c;
                if (caret >= c.NameStart && caret <= c.Close + 1 && (best == null || c.NameStart > best.NameStart)) best = c;
            }
            var call = best ?? first;
            if (call == null) { why = "カーソルの行に、関数の呼び出しが見つかりません"; return null; }

            var u = new Usage { Name = text.Substring(call.NameStart, call.NameEnd - call.NameStart), NameStart = call.NameStart };
            if (call.Receiver != null)
            {
                string r = call.Receiver;
                u.Receiver = r;
                string recvName = Regex.Replace(r, @"(\.|->)$", "");
                if (recvName == "this") u.Receiver = "this";
                else
                {
                    string t = recvName.Contains(".") || recvName.Contains("->") ? null : DeclType(m, recvName, call.NameStart);
                    u.ReceiverType = t == null ? null : ClassOf(t);
                }
            }

            // ---- 引数 ----
            string inner = text.Substring(call.Open + 1, call.Close - call.Open - 1);
            var args = inner.Trim().Length == 0 ? new List<string>() : SplitTop(inner).Select(a => a.Trim()).ToList();
            var usedNames = new HashSet<string>(StringComparer.Ordinal);
            for (int i = 0; i < args.Count; i++)
            {
                string a = args[i];
                string type = ArgType(m, text, a, call.NameStart);
                u.Args.Add(a);
                if (type == null) { u.Unknown.Add(a); type = "int"; }
                u.ParamTypes.Add(ParamTypeFor(type));
                string pn = Regex.IsMatch(a, @"^[A-Za-z_]\w*$") ? Regex.Replace(Regex.Replace(a, @"^m_", ""), @"_+$", "") : "arg" + (i + 1);
                if (pn.Length == 0 || NotTypes.Contains(pn) || a == "true" || a == "false" || a == "nullptr" || a == "this") pn = "arg" + (i + 1);
                string cand = pn; int n = 2;
                while (!usedNames.Add(cand)) cand = pn + n++;
                u.ParamNames.Add(cand);
            }

            // ---- 戻り値の型 ----
            string prefix = line.Substring(0, Math.Max(0, (call.Receiver != null ? FindReceiverStart(line, call.NameStart - ls) : call.NameStart - ls)));
            string rt = ReturnTypeFrom(m, text, prefix, call.NameStart, ls);
            if (rt == null) { u.ReturnType = "int"; u.ReturnGuessed = true; }
            else u.ReturnType = rt;
            return u;
        }

        private static int FindReceiverStart(string line, int nameStartInLine)
        {
            // 名前の前の「obj.」「a->b->」を飛ばした位置
            int i = nameStartInLine;
            while (i > 0)
            {
                int j = i;
                while (j > 0 && char.IsWhiteSpace(line[j - 1])) j--;
                if (j >= 2 && line[j - 1] == '>' && line[j - 2] == '-') j -= 2;
                else if (j >= 1 && line[j - 1] == '.') j -= 1;
                else break;
                while (j > 0 && char.IsWhiteSpace(line[j - 1])) j--;
                int k = j;
                while (k > 0 && (char.IsLetterOrDigit(line[k - 1]) || line[k - 1] == '_')) k--;
                if (k == j) break;
                i = k;
            }
            return i;
        }

        /// <summary>呼び出しの前の文字(prefix)から、戻り値の使われ方を見て型を決める。決められなければ null。</summary>
        private static string ReturnTypeFrom(string m, string text, string prefix, int nameStart, int lineStart)
        {
            string p = prefix.Trim();
            if (p.Length == 0 || p.EndsWith(";") || p.EndsWith("{") || p.EndsWith("}")) return "void";
            if (Regex.IsMatch(p, @"(?:^|[\s;{}])(?:else|do)$") || Regex.IsMatch(p, @"(?:^|[\s;{}])(?:if|for|while)\s*\(.*\)$") || Regex.IsMatch(p, @"(?:\bcase\s+[^:]+|\bdefault)\s*:$")) return "void";
            if (Regex.IsMatch(p, @"(?:\bif|\bwhile|\bswitch)\s*\(\s*$") ) return Regex.IsMatch(p, @"\bswitch\s*\(\s*$") ? null : "bool";
            if (Regex.IsMatch(p, @"(?:!|&&|\|\|)\s*$")) return "bool";
            if (Regex.IsMatch(p, @"\breturn\s*$"))
            {
                var sig = FunctionScan.Scan(text).Where(s => s.HasBody && s.BodyOpen >= 0 && s.BodyOpen < nameStart && nameStart < s.End).OrderByDescending(s => s.BodyOpen).FirstOrDefault();
                if (sig == null) return null;
                string head = m.Substring(sig.PrefixStart, sig.NameStart - sig.PrefixStart);
                head = Regex.Replace(head, @"\b(?:virtual|static|inline|constexpr|consteval|explicit|friend|extern)\b|\[\[[^\]]*\]\]|\btemplate\s*<[^>]*>", "");
                head = Regex.Replace(head, @"\s+", " ").Trim();
                if (head.Length == 0 || head == "auto") return null;
                return head;
            }
            Match d = Regex.Match(p, @"(?:^|[;{}(,]\s*)((?:const\s+)?[A-Za-z_][\w:]*(?:\s*<[^;(){}]*>)?(?:\s*[&*]+)?)\s+[A-Za-z_]\w*\s*=\s*$");
            if (d.Success)
            {
                string t = Regex.Replace(d.Groups[1].Value, @"\s+", " ").Trim();
                if (t == "auto" || t == "const auto" || NotTypes.Contains(t)) return null;
                return t;
            }
            Match a = Regex.Match(p, @"(?:^|[;{}]\s*)([A-Za-z_]\w*)\s*=\s*$");
            if (a.Success)
            {
                string t = DeclType(m, a.Groups[1].Value, nameStart);
                if (t != null && t != "auto") return t.StartsWith("const ") ? t.Substring(6) : t;
                return null;
            }
            return null;
        }

        /// <summary>name の宣言(before より前のいちばん近いもの)の型。見つからなければ null。auto は null。</summary>
        public static string DeclType(string m, string name, int before)
        {
            string head = m.Substring(0, Math.Min(before, m.Length));
            var rx = new Regex(@"(?<![\w.>])((?:const\s+)?[A-Za-z_][\w:]*(?:\s*<[^;(){}]*>)?)\s*([&*\s]*?)\b" + Regex.Escape(name) + @"\b\s*(?=[=;,)\({\[:])");
            Match last = null;
            foreach (Match x in rx.Matches(head))
            {
                string t0 = x.Groups[1].Value.Trim();
                string bare = Regex.Replace(t0, @"^const\s+", "");
                if (NotTypes.Contains(bare) || Regex.IsMatch(bare, @"^(?:public|private|protected)$")) continue;
                string tail = head.Substring(x.Index + x.Length);
                last = x;
            }
            if (last == null) return null;
            string type = Regex.Replace(last.Groups[1].Value, @"\s+", " ").Trim();
            string decor = Regex.Replace(last.Groups[2].Value, @"\s+", "");
            if (type == "auto" || type == "const auto") return null;
            return type + decor;
        }

        private static string ClassOf(string type)
        {
            string t = Regex.Replace(type, @"[&*]", " ");
            t = Regex.Replace(t, @"\bconst\b", " ");
            Match sp = Regex.Match(t, @"(?:std::)?(?:unique_ptr|shared_ptr|weak_ptr)\s*<\s*(?:const\s+)?([\w:]+)\s*>");
            if (sp.Success) t = sp.Groups[1].Value;
            t = t.Trim();
            Match n = Regex.Match(t, @"([A-Za-z_]\w*)\s*$");
            return n.Success ? n.Groups[1].Value : null;
        }

        private static string ArgType(string m, string text, string a, int before)
        {
            string t = TypeInference.FromExpression(a);
            if (t != null) return t;
            if (a == "this") return "void*";
            if (Regex.IsMatch(a, @"^[A-Za-z_]\w*$"))
            {
                string d = DeclType(m, a, before);
                return d;
            }
            Match addr = Regex.Match(a, @"^&\s*([A-Za-z_]\w*)$");
            if (addr.Success)
            {
                string d = DeclType(m, addr.Groups[1].Value, before);
                if (d != null && !d.EndsWith("*") && !d.EndsWith("&")) return d + "*";
                return null;
            }
            Match str = Regex.Match(a, "^L?\"");
            if (str.Success) return "const char*";
            return null;
        }

        private static readonly Regex Builtin = new Regex(
            @"^(?:(?:unsigned|signed|long|short)\s+)*(?:bool|char|char8_t|char16_t|char32_t|wchar_t|int|float|double|size_t|ptrdiff_t|(?:std::)?u?int(?:8|16|32|64)_t|(?:std::)?(?:size_t|string_view|byte|nullptr_t))$|^(?:unsigned|signed|long|short)(?:\s+(?:unsigned|signed|long|short|int))*$",
            RegexOptions.Compiled);

        /// <summary>引数に渡す値の型から、引数の型を決める。組み込み・ポインター・参照はそのまま、ほかは const T&amp;。</summary>
        public static string ParamTypeFor(string type)
        {
            string t = Regex.Replace(type, @"\s+", " ").Trim();
            t = Regex.Replace(t, @"\s*([&*])", "$1");
            if (t.EndsWith("&") || t.EndsWith("*")) return t;
            string bare = Regex.Replace(t, @"^const\s+", "").Trim();
            if (Builtin.IsMatch(bare)) return bare;
            return "const " + bare + "&";
        }

        /// <summary>enclosing 関数の前に、引数のない関数 u の定義(中身は TODO)を足す編集。enclosingStart は、囲んでいる関数の頭の位置。</summary>
        public static void PlanFreeDefinition(string text, int enclosingStart, Usage u, string eol, out int pos, out string outText)
        {
            pos = LineStart(text, enclosingStart);
            var sb = new StringBuilder();
            sb.Append(u.Signature()).Append(" {").Append(eol);
            sb.Append("  // TODO: ").Append(u.Name).Append(" を実装する").Append(eol);
            if (u.ReturnType != "void") sb.Append("  return {};").Append(eol);
            sb.Append("}").Append(eol).Append(eol);
            outText = sb.ToString();
        }

        private static IEnumerable<string> SplitTop(string s)
        {
            int depth = 0, start = 0;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '(' || c == '[' || c == '{') depth++;
                else if (c == ')' || c == ']' || c == '}') depth--;
                else if (c == ',' && depth == 0) { yield return s.Substring(start, i - start); start = i + 1; }
            }
            yield return s.Substring(start);
        }

        private static int MatchParen(string m, int open)
        {
            int depth = 0;
            for (int i = open; i < m.Length; i++)
            {
                if (m[i] == '(') depth++;
                else if (m[i] == ')') { depth--; if (depth == 0) return i; }
            }
            return -1;
        }

        private static int LineStart(string text, int pos)
        {
            int i = Math.Min(pos, text.Length);
            while (i > 0 && text[i - 1] != '\n') i--;
            return i;
        }
    }
}
