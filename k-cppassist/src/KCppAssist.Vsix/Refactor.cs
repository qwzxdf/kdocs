using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// 1 つのファイルの中で済む書き換え(C# の Ctrl+. のリファクタリングにあたるもの)。VS に依存しない。
    /// どれも (位置, 消す長さ, 入れる文字) の編集の並びを返す。位置はすべて、書き換える前の文字のもの。
    /// </summary>
    internal static class Refactor
    {
        public sealed class Change
        {
            public List<Tuple<int, int, string>> Edits = new List<Tuple<int, int, string>>();
            public string Message;

            public Change Add(int pos, int len, string text) { Edits.Add(Tuple.Create(pos, len, text)); return this; }

            /// <summary>編集を text に当てた結果(テスト用)。</summary>
            public string Apply(string text)
            {
                foreach (var e in Edits.OrderByDescending(x => x.Item1)) text = text.Remove(e.Item1, e.Item2).Insert(e.Item1, e.Item3);
                return text;
            }
        }

        /// <summary>電球に出す 1 項目。Id でもう一度計算し直して実行する。</summary>
        public sealed class Offer
        {
            public string Id;
            public string Title;
        }

        /// <summary>id の書き換えを計算する。使えないときは null で、理由を why に入れる。</summary>
        public static Change Make(string id, string text, int caret, string eol, bool header, out string why)
        {
            why = null;
            switch (id)
            {
                case "nullptr": return NullToNullptr(text, caret, false, out why);
                case "nullptr-file": return NullToNullptr(text, caret, true, out why);
                case "using": return TypedefToUsing(text, caret, out why);
                case "cast": return CastToStatic(text, caret, out why);
                case "rangefor": return RangeFor(text, caret, out why);
                case "invertif": return InvertIf(text, caret, out why);
                case "guard": return Guard(text, caret, out why);
                case "auto": return ToAuto(text, caret, out why);
                case "dbg": return DebugPrint(text, caret, eol, header, out why);
                case "dbg-clear": return DebugClear(text, out why);
                default: return ClassGen.Make(id, text, caret, eol, header, out why);
            }
        }

        /// <summary>caret の位置で使える書き換えの一覧(実際に計算して、できるものだけ)。</summary>
        public static List<Offer> Offers(string text, int caret, string eol, bool header)
        {
            var list = new List<Offer>();
            string why;
            void Try(string id, string title) { if (Make(id, text, caret, eol, header, out why) != null) list.Add(new Offer { Id = id, Title = L.T(title) }); }
            // 電球はカーソルが動くたびに呼ばれる。行の文字で先にふるい、重い計算(ファイル全体の走査)を減らす
            int ls = MemberScan.LineStart(text, caret), le = MemberScan.LineEnd(text, caret);
            string line = text.Substring(ls, le - ls);
            if (line.Contains("NULL")) { Try("nullptr", "NULL を nullptr にする (この行)"); if (list.Count > 0) Try("nullptr-file", "NULL を nullptr にする (ファイル全体)"); }
            if (line.Contains("typedef")) Try("using", "typedef を using にする");
            if (line.Contains(")")) Try("cast", "C のキャストを static_cast にする");
            if (line.Contains("for")) Try("rangefor", "添字の for を範囲 for にする");
            if (line.Contains("if")) { Try("invertif", "if を反転する (then と else を入れ替える)"); Try("guard", "if を早期 return / continue にして入れ子を浅くする"); }
            if (line.Contains("=")) Try("auto", "型を auto にする");
            if (!header && line.TrimEnd().EndsWith(";")) Try("dbg", "この変数をデバッグ出力する (OutputDebugString)");
            if (text.Contains(DbgMark)) Try("dbg-clear", "デバッグ出力の行 (// KDBG) をすべて消す");
            list.AddRange(ClassGen.Offers(text, caret, eol, header));
            return list;
        }

        // ---- NULL → nullptr ----

        private static Change NullToNullptr(string text, int caret, bool file, out string why)
        {
            why = null;
            string m = CppText.Mask(text);
            int from = file ? 0 : MemberScan.LineStart(text, caret);
            int to = file ? text.Length : MemberScan.LineEnd(text, caret);
            var ch = new Change();
            foreach (Match x in Regex.Matches(m.Substring(from, to - from), @"\bNULL\b"))
                ch.Add(from + x.Index, 4, "nullptr");
            if (ch.Edits.Count == 0) { why = L.T("NULL がありません"); return null; }
            ch.Message = L.F("NULL を nullptr にしました ({0} か所)", ch.Edits.Count);
            return ch;
        }

        // ---- typedef → using ----

        private static readonly Regex TypedefFn = new Regex(@"^(\s*)typedef\s+(.+?)\(\s*(__\w+\s+)?\*\s*([A-Za-z_]\w*)\s*\)\s*\((.*)\)\s*;\s*$");
        private static readonly Regex TypedefPlain = new Regex(@"^(\s*)typedef\s+([^;\[\(]+?[\s*&>])\s*([A-Za-z_]\w*)\s*((?:\[[^\]]*\])*)\s*;\s*$");

        private static Change TypedefToUsing(string text, int caret, out string why)
        {
            why = null;
            int ls = MemberScan.LineStart(text, caret), le = MemberScan.LineEnd(text, caret);
            string line = text.Substring(ls, le - ls);
            string masked = CppText.Mask(text).Substring(ls, le - ls);
            string comment = line.Substring(masked.TrimEnd().Length);   // 行末のコメントは残す
            string code = line.Substring(0, masked.TrimEnd().Length);
            Match f = TypedefFn.Match(code);
            string res = null;
            if (f.Success)
            {
                // typedef void (*Fn)(int);  →  using Fn = void (*)(int);
                string ret = f.Groups[2].Value.TrimEnd();
                res = f.Groups[1].Value + "using " + f.Groups[4].Value + " = " + ret + " (" + f.Groups[3].Value + "*)(" + f.Groups[5].Value + ");";
            }
            else
            {
                Match p = TypedefPlain.Match(code);
                if (!p.Success || Regex.IsMatch(p.Groups[2].Value, @"\b(?:struct|enum|union)\s*\{")) { why = L.T("この行は 1 行の typedef ではありません"); return null; }
                string type = Regex.Replace(p.Groups[2].Value.Trim(), @"\s+", " ");
                res = p.Groups[1].Value + "using " + p.Groups[3].Value + " = " + type + p.Groups[4].Value + ";";
            }
            var ch = new Change().Add(ls, code.Length, res);
            ch.Message = L.T("typedef を using にしました");
            return ch;
        }

        // ---- C のキャスト → static_cast ----

        private const string CastType =
            @"(?:const\s+)?(?:(?:unsigned|signed)\s+)?(?:long\s+long|long\s+double|bool|char|char8_t|char16_t|char32_t|wchar_t|short|int|long|float|double|unsigned|size_t|ptrdiff_t|(?:std::)?u?int(?:8|16|32|64)_t|(?:std::)?size_t|UINT|INT|DWORD|WORD|BYTE|BOOL|LONG|ULONG|UINT8|UINT16|UINT32|UINT64|INT8|INT16|INT32|INT64|FLOAT|SIZE_T|LONG_PTR|ULONG_PTR|UINT_PTR|INT_PTR)";
        private static readonly Regex CastHead = new Regex(@"\(\s*(" + CastType + @")\s*\)");

        private static Change CastToStatic(string text, int caret, out string why)
        {
            why = null;
            string m = CppText.Mask(text);
            int ls = MemberScan.LineStart(text, caret), le = MemberScan.LineEnd(text, caret);
            var ch = new Change();
            foreach (Match x in CastHead.Matches(m.Substring(ls, le - ls)))
            {
                int start = ls + x.Index;
                // 「sizeof(int)」「f(int)」の宣言は、キャストではない
                int b = start - 1;
                while (b >= 0 && (m[b] == ' ' || m[b] == '\t')) b--;
                if (b >= 0 && (CppText.IsId(m[b]) || m[b] == ')' || m[b] == ']')) continue;
                int opStart = start + x.Length;
                while (opStart < le && m[opStart] == ' ') opStart++;
                int opEnd = OperandEnd(m, opStart, le);
                if (opEnd <= opStart) continue;
                if (ch.Edits.Any(e => e.Item1 < opEnd && start < e.Item1 + e.Item2)) continue;
                string operand = text.Substring(opStart, opEnd - opStart);
                if (operand.StartsWith("(") && Matching(m, opStart) == opEnd - 1) operand = operand.Substring(1, operand.Length - 2);
                string type = Regex.Replace(x.Groups[1].Value, @"\s+", " ");
                ch.Add(start, opEnd - start, "static_cast<" + type + ">(" + operand + ")");
            }
            if (ch.Edits.Count == 0) { why = L.T("この行に、数の型への C のキャストがありません"); return null; }
            ch.Message = L.F("C のキャストを static_cast にしました ({0} か所)", ch.Edits.Count);
            return ch;
        }

        /// <summary>
        /// キャストの後ろの式(単項)の終わり。キャストは二項演算子より強く結び付くので、
        /// 「(float)a / b」は a だけ。識別子・数・括弧に、後置(.x ->x [i] (args) ::x)が続いたものまで。
        /// </summary>
        private static int OperandEnd(string m, int i, int limit)
        {
            if (i >= limit) return i;
            if (m[i] == '-' || m[i] == '!' || m[i] == '~' || m[i] == '*' || m[i] == '&')
            {
                int e = OperandEnd(m, i + 1, limit);
                return e == i + 1 ? i : e;
            }
            int k = i;
            if (m[k] == '(') { int c = Matching(m, k); if (c < 0) return i; k = c + 1; }
            else if (char.IsDigit(m[k]) || m[k] == '.')
            {
                while (k < limit && (CppText.IsId(m[k]) || m[k] == '.' || m[k] == '\'' || ((m[k] == '+' || m[k] == '-') && (m[k - 1] == 'e' || m[k - 1] == 'E')))) k++;
                return k;
            }
            else if (CppText.IsId(m[k])) { while (k < limit && CppText.IsId(m[k])) k++; }
            else return i;
            while (k < limit)
            {
                if (m[k] == '(' || m[k] == '[') { int c = Matching(m, k); if (c < 0) break; k = c + 1; continue; }
                if (m[k] == '.' && k + 1 < limit && CppText.IsId(m[k + 1])) { k++; while (k < limit && CppText.IsId(m[k])) k++; continue; }
                if (m[k] == '-' && k + 2 < limit && m[k + 1] == '>') { k += 2; while (k < limit && CppText.IsId(m[k])) k++; continue; }
                if (m[k] == ':' && k + 2 < limit && m[k + 1] == ':') { k += 2; while (k < limit && CppText.IsId(m[k])) k++; continue; }
                break;
            }
            return k;
        }

        /// <summary>m[open] の「(」「[」「{」に対応する閉じ括弧の位置。なければ -1。</summary>
        public static int Matching(string m, int open)
        {
            char o = m[open], c = o == '(' ? ')' : o == '[' ? ']' : '}';
            int depth = 0;
            for (int i = open; i < m.Length; i++)
            {
                if (m[i] == o) depth++;
                else if (m[i] == c) { depth--; if (depth == 0) return i; }
            }
            return -1;
        }

        // ---- 添字の for → 範囲 for ----

        private static readonly Regex IndexFor = new Regex(
            @"\bfor\s*\(\s*(?:(?:std::)?size_t|int|unsigned(?:\s+int)?|auto|uint32_t|UINT|int32_t)\s+([A-Za-z_]\w*)\s*=\s*0\s*;\s*\1\s*<\s*(?:([A-Za-z_][\w.\->]*)\s*\.\s*size\s*\(\s*\)|std::size\s*\(\s*([A-Za-z_][\w.\->]*)\s*\))\s*;\s*(?:\+\+\s*\1|\1\s*\+\+)\s*\)\s*\{");

        private static Change RangeFor(string text, int caret, out string why)
        {
            why = null;
            string m = CppText.Mask(text);
            int ls = MemberScan.LineStart(text, caret), le = MemberScan.LineEnd(text, caret);
            Match x = IndexFor.Match(m, ls);
            if (!x.Success || x.Index > le) { why = L.T("この行は「for (size_t i = 0; i < v.size(); ++i) {」の形ではありません"); return null; }
            string idx = x.Groups[1].Value;
            string cont = x.Groups[2].Success ? x.Groups[2].Value : x.Groups[3].Value;
            int open = x.Index + x.Length - 1;
            int close = Scopes.MatchBrace(m, open);
            if (close < 0) { why = L.T("for の本体の「}」が見つかりません"); return null; }

            // 本体で i を使っているのが、すべて「cont[i]」なら変えられる
            var uses = new List<int>();
            var accessRx = new Regex(Regex.Escape(cont).Replace(@"\.", @"\s*\.\s*") + @"\s*\[\s*" + Regex.Escape(idx) + @"\s*\]");
            var accesses = accessRx.Matches(m.Substring(open, close - open)).Cast<Match>().Select(a => Tuple.Create(open + a.Index, a.Length)).ToList();
            foreach (Match u in Regex.Matches(m.Substring(open, close - open), @"(?<![\w.])" + Regex.Escape(idx) + @"\b"))
            {
                int p = open + u.Index;
                if (!accesses.Any(a => a.Item1 < p && p < a.Item1 + a.Item2)) { why = L.F("本体で {0} を、{1}[{2}] 以外にも使っています (番号が要るので、範囲 for にできません)", idx, cont, idx); return null; }
            }
            if (accesses.Count == 0) { why = L.F("本体で {0}[{1}] を使っていません", cont, idx); return null; }
            // 本体で入れ物の大きさを変えると、範囲 for では、反復子が無効になる
            if (Regex.IsMatch(m.Substring(open, close - open), Regex.Escape(cont) + @"\s*\.\s*(?:push_back|emplace_back|erase|insert|clear|resize|pop_back)\b"))
            { why = L.F("本体で {0} の要素を足し引きしています。範囲 for にすると、反復子が無効になります", cont); return null; }

            string elem = Singular(cont);
            var bodyIds = new HashSet<string>(Regex.Matches(m.Substring(open, close - open), @"\b[A-Za-z_]\w*\b").Cast<Match>().Select(t => t.Value));
            while (bodyIds.Contains(elem) || elem == idx) elem += "_item";

            var ch = new Change();
            int forStart = x.Index;
            ch.Add(forStart, open - forStart, "for (auto& " + elem + " : " + cont + ") ");
            foreach (var a in accesses) ch.Add(a.Item1, a.Item2, elem);
            ch.Message = L.F("範囲 for にしました (要素の名前は {0}。const にしたいときは const auto& に)", elem);
            return ch;
        }

        /// <summary>入れ物の名前から、要素の名前を作る(enemies_ → enemy、items → item、list → list_item)。</summary>
        public static string Singular(string cont)
        {
            string n = cont;
            int k = Math.Max(n.LastIndexOf('.'), n.LastIndexOf('>'));
            if (k >= 0) n = n.Substring(k + 1);
            if (n.StartsWith("m_")) n = n.Substring(2);
            n = n.Trim('_');
            if (n.Length == 0) return "item";
            if (n.EndsWith("ies") && n.Length > 3) return n.Substring(0, n.Length - 3) + "y";
            if (Regex.IsMatch(n, "(?:ss|sh|ch|x)es$")) return n.Substring(0, n.Length - 2);
            if (n.EndsWith("s") && !n.EndsWith("ss") && n.Length > 1) return n.Substring(0, n.Length - 1);
            return char.ToLowerInvariant(n[0]) + n.Substring(1) + "_item";
        }

        // ---- if の反転 ----

        private sealed class IfStmt
        {
            public int IfStart, CondOpen, CondClose, ThenOpen, ThenClose, ElseStart = -1, ElseOpen = -1, ElseClose = -1;
        }

        /// <summary>caret の行で始まる「if (…) { … }」を読む。else if の連なりの途中は対象にしない。</summary>
        private static IfStmt FindIf(string m, string text, int caret)
        {
            int ls = MemberScan.LineStart(text, caret), le = MemberScan.LineEnd(text, caret);
            Match x = new Regex(@"\bif\s*(?:constexpr\s*)?\(").Match(m, ls);
            if (!x.Success || x.Index > le) return null;
            if (Regex.IsMatch(m.Substring(0, x.Index), @"\belse\s*$")) return null;
            if (m.Substring(x.Index, x.Length).Contains("constexpr")) return null;
            var s = new IfStmt { IfStart = x.Index, CondOpen = x.Index + x.Length - 1 };
            s.CondClose = Matching(m, s.CondOpen);
            if (s.CondClose < 0) return null;
            int k = s.CondClose + 1;
            while (k < m.Length && char.IsWhiteSpace(m[k])) k++;
            if (k >= m.Length || m[k] != '{') return null;
            s.ThenOpen = k;
            s.ThenClose = Scopes.MatchBrace(m, k);
            if (s.ThenClose < 0) return null;
            k = s.ThenClose + 1;
            while (k < m.Length && char.IsWhiteSpace(m[k])) k++;
            if (k + 4 <= m.Length && m.Substring(k, 4) == "else" && (k + 4 == m.Length || !CppText.IsId(m[k + 4])))
            {
                s.ElseStart = k;
                int e = k + 4;
                while (e < m.Length && char.IsWhiteSpace(m[e])) e++;
                if (e >= m.Length || m[e] != '{') return new IfStmt { IfStart = -1 };   // else if / 波括弧なし
                s.ElseOpen = e;
                s.ElseClose = Scopes.MatchBrace(m, e);
                if (s.ElseClose < 0) return null;
            }
            return s;
        }

        /// <summary>条件を否定する。比較 1 つなら演算子を裏返し、!x なら x、それ以外は !(…)。</summary>
        public static string Negate(string cond)
        {
            string c = cond.Trim();
            string mc = CppText.Mask(c);
            // 外側の括弧を外して考える
            while (mc.StartsWith("(") && Matching(mc, 0) == mc.Length - 1) { c = c.Substring(1, c.Length - 2).Trim(); mc = CppText.Mask(c); }
            if (mc.StartsWith("!") && !mc.StartsWith("!="))
            {
                string rest = c.Substring(1).Trim();
                string mr = CppText.Mask(rest);
                if (mr.StartsWith("(") && Matching(mr, 0) == mr.Length - 1) return rest.Substring(1, rest.Length - 2).Trim();
                if (Regex.IsMatch(mr, @"^[\w.:\->\[\]()]+$") && !TopLevelBinary(mr)) return rest;
            }
            if (!Regex.IsMatch(mc, @"&&|\|\||\?"))
            {
                var ops = new[] { "==", "!=", "<=", ">=", "<", ">" };
                var neg = new Dictionary<string, string> { { "==", "!=" }, { "!=", "==" }, { "<=", ">" }, { ">=", "<" }, { "<", ">=" }, { ">", "<=" } };
                int depth = 0, found = -1; string op = null; int count = 0;
                for (int i = 0; i < mc.Length; i++)
                {
                    char ch = mc[i];
                    if (ch == '(' || ch == '[' || ch == '{') { depth++; continue; }
                    if (ch == ')' || ch == ']' || ch == '}') { depth--; continue; }
                    if (depth != 0) continue;
                    foreach (string o in ops)
                    {
                        if (string.CompareOrdinal(mc, i, o, 0, o.Length) != 0) continue;
                        // 「->」「<<」「>>」「<=>」と、テンプレートの山括弧は除く
                        if (o == ">" && i > 0 && (mc[i - 1] == '-' || mc[i - 1] == '>')) break;
                        if ((o == "<" || o == ">") && i + 1 < mc.Length && (mc[i + 1] == o[0])) { i++; break; }
                        if (o.Length == 1 && i + 1 < mc.Length && mc[i + 1] == '=') break;
                        if (o == "<=" && i + 2 < mc.Length && mc[i + 2] == '>') break;
                        found = i; op = o; count++;
                        i += o.Length - 1;
                        break;
                    }
                }
                if (count == 1 && !Regex.IsMatch(mc, @"\w\s*<[^<>=]*>"))
                    return c.Substring(0, found).TrimEnd() + " " + neg[op] + " " + c.Substring(found + op.Length).TrimStart();
                if (count == 0 && Regex.IsMatch(mc, @"^[\w.:\->\[\]()]+$")) return "!" + c;
            }
            return "!(" + c + ")";
        }

        private static bool TopLevelBinary(string m)
        {
            int depth = 0;
            foreach (char ch in m)
            {
                if (ch == '(' || ch == '[') depth++;
                else if (ch == ')' || ch == ']') depth--;
                else if (depth == 0 && "+-*/%<>=&|^?".IndexOf(ch) >= 0) return true;
            }
            return false;
        }

        private static Change InvertIf(string text, int caret, out string why)
        {
            why = null;
            string m = CppText.Mask(text);
            var s = FindIf(m, text, caret);
            if (s == null || s.IfStart < 0) { why = L.T("この行は「if (…) { … } else { … }」(波括弧つき)の if ではありません"); return null; }
            if (s.ElseStart < 0) { why = L.T("else がない if です (早期 return のほうを使ってください)"); return null; }
            string cond = text.Substring(s.CondOpen + 1, s.CondClose - s.CondOpen - 1);
            string thenBody = text.Substring(s.ThenOpen, s.ThenClose - s.ThenOpen + 1);
            string elseBody = text.Substring(s.ElseOpen, s.ElseClose - s.ElseOpen + 1);
            var ch = new Change();
            ch.Add(s.ElseOpen, elseBody.Length, thenBody);
            ch.Add(s.ThenOpen, thenBody.Length, elseBody);
            ch.Add(s.CondOpen + 1, cond.Length, Negate(cond));
            ch.Message = L.T("if を反転しました");
            return ch;
        }

        // ---- 早期 return / continue ----

        private static Change Guard(string text, int caret, out string why)
        {
            why = null;
            string m = CppText.Mask(text);
            var s = FindIf(m, text, caret);
            if (s == null || s.IfStart < 0) { why = L.T("この行は波括弧つきの if ではありません"); return null; }
            if (s.ElseStart >= 0) { why = L.T("else のある if は、早期 return にできません"); return null; }
            // if が、囲んでいるブロックの最後の文か
            int k = s.ThenClose + 1;
            while (k < m.Length && char.IsWhiteSpace(m[k])) k++;
            if (k >= m.Length || m[k] != '}') { why = L.T("if の後ろに文が続いています。最後の文の if だけ早期 return にできます"); return null; }
            int outerClose = k;
            int outerOpen = OpenOf(m, outerClose);
            if (outerOpen < 0) return null;
            string head = m.Substring(Math.Max(0, outerOpen - 300), outerOpen - Math.Max(0, outerOpen - 300));
            string exit;
            if (Regex.IsMatch(head, @"\b(?:for|while)\s*\([^{};]*(?:\([^()]*\)[^{};]*)*\)\s*$") || Regex.IsMatch(head, @"\bdo\s*$")) exit = "continue;";
            else
            {
                var fn = FunctionScan.Scan(text).FirstOrDefault(f => f.HasBody && f.BodyOpen == outerOpen);
                if (fn == null) { why = L.T("if を囲んでいるのが、関数かループの本体ではありません"); return null; }
                string ret = text.Substring(fn.PrefixStart, fn.NameStart - fn.PrefixStart);
                bool isVoid = Regex.IsMatch(CppText.Mask(ret), @"\bvoid\s*$") || CppText.Mask(ret).Trim().Length == 0
                    || Regex.IsMatch(CppText.Mask(ret), @"^\s*(?:(?:inline|static|virtual|explicit|constexpr)\s+)*$");
                if (!isVoid) { why = L.T("戻り値のある関数です。何を返すか決められないので、早期 return にできません"); return null; }
                exit = "return;";
            }
            string ifIndent = MemberScan.Indent(text, s.IfStart);
            string cond = text.Substring(s.CondOpen + 1, s.CondClose - s.CondOpen - 1);
            // 本体の行を 1 段浅くする(本体の最初の行の字下げと、if の字下げの差を外す)
            string body = text.Substring(s.ThenOpen + 1, s.ThenClose - s.ThenOpen - 1);
            string eol = CppText.Eol(text);
            var lines = body.Split('\n').Select(l => l.TrimEnd('\r')).ToList();
            while (lines.Count > 0 && lines[0].Trim().Length == 0) lines.RemoveAt(0);
            while (lines.Count > 0 && lines[lines.Count - 1].Trim().Length == 0) lines.RemoveAt(lines.Count - 1);
            if (lines.Count == 0) { why = L.T("if の本体が空です"); return null; }
            string bodyIndent = Regex.Match(lines[0], @"^[ \t]*").Value;
            var outLines = lines.Select(l => l.StartsWith(bodyIndent) && bodyIndent.Length > ifIndent.Length ? ifIndent + l.Substring(bodyIndent.Length) : l).ToList();
            if (!outLines[0].StartsWith(ifIndent)) outLines[0] = ifIndent + outLines[0].TrimStart();
            string res = "if (" + Negate(cond) + ") " + exit + eol + eol + string.Join(eol, outLines);
            var ch = new Change().Add(s.IfStart, s.ThenClose + 1 - s.IfStart, res);
            ch.Message = L.F("早期 {0} にしました", exit.TrimEnd(';'));
            return ch;
        }

        /// <summary>m[close] の「}」に対応する「{」の位置。</summary>
        private static int OpenOf(string m, int close)
        {
            int depth = 0;
            for (int i = close; i >= 0; i--)
            {
                if (m[i] == '}') depth++;
                else if (m[i] == '{') { depth--; if (depth == 0) return i; }
            }
            return -1;
        }

        // ---- 型 → auto ----

        private static Change ToAuto(string text, int caret, out string why)
        {
            why = null;
            string m = CppText.Mask(text);
            int ls = MemberScan.LineStart(text, caret), le = MemberScan.LineEnd(text, caret);
            string line = m.Substring(ls, le - ls);
            Match d = Regex.Match(line, @"^(\s*)((?:const\s+)?[A-Za-z_][\w:]*(?:\s*<.*>)?(?:\s*::\s*\w+)*)\s*([*&]?)\s*([A-Za-z_]\w*)\s*=\s*(.+);\s*$");
            if (!d.Success || Regex.IsMatch(d.Groups[2].Value, @"^(?:const\s+)?auto$|^(?:return|using|typedef|static_assert)\b")) { why = L.T("この行は「型 名前 = 式;」の宣言ではありません"); return null; }
            string type = Regex.Replace(d.Groups[2].Value, @"\s+", " ").Trim();
            string bare = Regex.Replace(type, @"^const\s+", "");
            string rhs = d.Groups[5].Value.Trim();
            string star = d.Groups[3].Value;
            // 右辺が同じ型をそのまま書いているときだけ(型が変わる auto は作らない。float x = 1; を auto にすると int になる)
            bool same = false;
            Match uptr = Regex.Match(bare, @"^(?:std::)?(unique_ptr|shared_ptr)\s*<\s*(.+)\s*>$");
            if (star == "" && uptr.Success && Regex.IsMatch(rhs, @"^(?:std::)?make_" + (uptr.Groups[1].Value == "unique_ptr" ? "unique" : "shared") + @"\s*<\s*" + Regex.Escape(uptr.Groups[2].Value.Trim()) + @"\s*>\s*\(")) same = true;
            if (star == "*" && Regex.IsMatch(rhs, @"^new\s+" + Regex.Escape(bare) + @"\s*[({;\[]?")) same = true;
            if (star == "" && Regex.IsMatch(rhs, @"^(?:static_cast|reinterpret_cast|const_cast|dynamic_cast)\s*<\s*" + Regex.Escape(bare) + @"\s*>")) same = true;
            if (star == "*" && Regex.IsMatch(rhs, @"^(?:static_cast|reinterpret_cast|const_cast|dynamic_cast)\s*<\s*" + Regex.Escape(bare) + @"\s*\*\s*>")) same = true;
            if (star == "" && Regex.IsMatch(rhs, "^" + Regex.Escape(bare) + @"\s*[({]")) same = true;
            if (star == "" && Regex.IsMatch(bare, @"(?:^|::)(?:const_)?(?:reverse_)?iterator$") && Regex.IsMatch(rhs, @"\.\s*(?:c?r?begin|c?r?end|find|lower_bound|upper_bound)\s*\(")) same = true;
            if (!same) { why = L.F("右辺の型が {0}{1} と同じだと言い切れません (auto にすると型が変わることがあります)", type, star); return null; }
            string isConst = type.StartsWith("const ") ? "const " : "";
            int typeStart = ls + d.Groups[2].Index;
            int nameStart = ls + d.Groups[4].Index;
            var ch = new Change().Add(typeStart, nameStart - typeStart, isConst + "auto" + (star == "*" ? "*" : "") + " ");
            ch.Message = L.T("auto にしました");
            return ch;
        }

        // ---- デバッグ出力 ----

        public const string DbgMark = "// KDBG";

        private static Change DebugPrint(string text, int caret, string eol, bool header, out string why)
        {
            why = null;
            if (header) { why = L.T("ヘッダーでは使えません"); return null; }
            string m = CppText.Mask(text);
            int ls = MemberScan.LineStart(text, caret), le = MemberScan.LineEnd(text, caret);
            string line = m.Substring(ls, le - ls);
            if (!line.TrimEnd().EndsWith(";")) { why = L.T("「;」で終わる文の行で押してください"); return null; }
            // 関数の本体の中か
            var fn = FunctionScan.Scan(text).FirstOrDefault(f => f.HasBody && f.BodyOpen < ls && le <= f.End);
            if (fn == null) { why = L.T("関数の本体の中で押してください"); return null; }
            // 代入・宣言の左辺。なければ、カーソルの識別子
            string name = null;
            Match a = Regex.Match(line, @"^\s*(?:(?:const\s+)?[A-Za-z_][\w:<>,\s*&]*?\s+)?((?:this->)?[A-Za-z_][\w.\->\[\]]*)\s*(?:[+\-*/%|&^]?=|\{|\()(?!=)");
            if (a.Success && !Regex.IsMatch(a.Groups[1].Value, @"^(?:return|if|while|for|switch|delete)$")) name = a.Groups[1].Value;
            if (name == null || line.TrimStart().StartsWith("return"))
            {
                int s = caret, e = caret;
                while (s > ls && (CppText.IsId(m[s - 1]) || m[s - 1] == '.')) s--;
                while (e < le && CppText.IsId(m[e])) e++;
                name = e > s ? m.Substring(s, e - s).Trim('.') : null;
            }
            if (string.IsNullOrEmpty(name) || Regex.IsMatch(name, @"^(?:return|auto|const|int|float)$")) { why = L.T("出力する変数が見つかりません。変数の上で押してください"); return null; }
            string indent = MemberScan.Indent(text, ls);
            // 「ファイル(行): 文」の形で出すと、出力ウィンドウでダブルクリックしたとき、その行へ飛べる
            string stmt = "OutputDebugStringA(std::format(\"{}({}): " + name.Replace("\"", "\\\"") + " = {}\\n\", __FILE__, __LINE__, " + name + ").c_str());  " + DbgMark;
            var ch = new Change().Add(MemberScan.LineEnd(text, ls), 0, eol + indent + stmt);
            AddInclude(ch, text, "<format>", eol);
            if (!Regex.IsMatch(text, @"#\s*include\s*[<""](?:Windows|windows|pch|stdafx)\.h[>""]")) AddInclude(ch, text, "<Windows.h>", eol);
            ch.Message = L.F("{0} をデバッグ出力する行を足しました (出力ウィンドウに出ます。値が std::format で書けない型ならビルドエラーになります)", name);
            return ch;
        }

        private static Change DebugClear(string text, out string why)
        {
            why = null;
            var ch = new Change();
            int i = 0;
            while (i < text.Length)
            {
                int le = text.IndexOf('\n', i);
                int next = le < 0 ? text.Length : le + 1;
                string line = text.Substring(i, next - i);
                if (line.TrimEnd().EndsWith(DbgMark)) ch.Add(i, next - i, "");
                i = next;
            }
            if (ch.Edits.Count == 0) { why = L.T("// KDBG の行がありません"); return null; }
            ch.Message = L.F("デバッグ出力の行を {0} 行消しました", ch.Edits.Count);
            return ch;
        }

        /// <summary>#include がなければ足す編集を ch に加える。</summary>
        public static void AddInclude(Change ch, string text, string token, string eol)
        {
            if (IncludeEditor.Has(text, token.Substring(1, token.Length - 2))) return;
            var e = IncludeEditor.Plan(text, token, null, eol);
            if (e != null) ch.Add(e.Position, 0, e.Text);
        }
    }
}
