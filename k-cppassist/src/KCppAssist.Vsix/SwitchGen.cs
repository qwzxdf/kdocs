using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// switch に、enum の足りない case を足す。VS に依存しない。
    /// enum の型は、すでにある case のラベルか、switch の式の変数の宣言から決める。決められなければ、何もしない。
    /// </summary>
    internal static class SwitchGen
    {
        public sealed class EnumDef
        {
            public string Name;
            public bool Scoped;                                   // enum class / enum struct
            public List<string> Chain = new List<string>();       // 囲んでいる namespace / class(外側から順。enum 自身は含まない)
            public List<string> Values = new List<string>();
        }

        public sealed class Plan
        {
            public int Position;                                  // 挿入する位置
            public string Text;                                   // 挿入する文字
            public string EnumName;
            public List<string> Added = new List<string>();
        }

        private static readonly Regex EnumHead = new Regex(
            @"\benum\s+(?:(class|struct)\s+)?([A-Za-z_]\w*)\s*(?::\s*[A-Za-z_][\w:\s]*?)?\s*\{", RegexOptions.Compiled);

        /// <summary>text の中の enum の定義を集める。</summary>
        public static List<EnumDef> ParseEnums(string text)
        {
            string m = CppText.Mask(text);
            var scopes = Scopes.Parse(text);
            var list = new List<EnumDef>();
            foreach (Match x in EnumHead.Matches(m))
            {
                int open = x.Index + x.Length - 1;
                int close = Scopes.MatchBrace(m, open);
                if (close < 0) continue;
                var def = new EnumDef { Name = x.Groups[2].Value, Scoped = x.Groups[1].Success };
                var inner = scopes.Where(s => s.Open < open && open < s.Close).OrderByDescending(s => s.Open).FirstOrDefault();
                if (inner != null) def.Chain = inner.Chain();
                foreach (string part in SplitTop(m.Substring(open + 1, close - open - 1)))
                {
                    Match v = Regex.Match(part, @"^\s*([A-Za-z_]\w*)");
                    if (v.Success) def.Values.Add(v.Groups[1].Value);
                }
                list.Add(def);
            }
            return list;
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
            if (start < s.Length) yield return s.Substring(start);
        }

        // 最後の enumerator が、個数を数えるための印(Count、Max など)のときは、case を作らない
        private static readonly Regex Sentinel = new Regex(
            @"^(?:k?(?:count|num|max|size|length|total|last|end)|.*_(?:count|max|num|size)|(?:num|max)_.*|.*(?:Count|Num|Max|Size))$",
            RegexOptions.Compiled | RegexOptions.IgnoreCase);

        private sealed class Sw { public int Start, Open, Close; public string Expr; }

        /// <summary>caret を含む switch(複数なら一番内側)に足りない case を足す計画。できなければ null で、理由を why に入れる。</summary>
        public static Plan Make(string text, int caret, IList<EnumDef> enums, string eol, out string why)
        {
            why = null;
            string m = CppText.Mask(text);

            // ---- caret を含む switch ----
            Sw sw = null;
            foreach (Match x in Regex.Matches(m, @"\bswitch\s*\("))
            {
                int po = x.Index + x.Length - 1;
                int pc = MatchParen(m, po);
                if (pc < 0) continue;
                int ob = pc + 1;
                while (ob < m.Length && char.IsWhiteSpace(m[ob])) ob++;
                if (ob >= m.Length || m[ob] != '{') continue;
                int cb = Scopes.MatchBrace(m, ob);
                if (cb < 0) continue;
                int lineStart = LineStart(text, x.Index);
                if (caret < lineStart || caret > cb + 1) continue;
                if (sw == null || x.Index > sw.Start) sw = new Sw { Start = x.Index, Open = ob, Close = cb, Expr = text.Substring(po + 1, pc - po - 1).Trim() };
            }
            if (sw == null) { why = "カーソルが、switch の中にありません"; return null; }

            // ---- いまある case と default(switch 直下だけ。入れ子の switch は見ない) ----
            var labels = new List<string>();
            int firstCase = -1, defaultPos = -1;
            int depth = 0;
            for (int i = sw.Open + 1; i < sw.Close; i++)
            {
                char c = m[i];
                if (c == '{') depth++;
                else if (c == '}') depth--;
                else if (depth == 0 && (i == 0 || !CppText.IsId(m[i - 1])))
                {
                    if (string.CompareOrdinal(m, i, "case", 0, 4) == 0 && (i + 4 >= m.Length || !CppText.IsId(m[i + 4])))
                    {
                        int j = i + 4;
                        while (j < sw.Close)
                        {
                            if (m[j] == ':') { if (j + 1 < m.Length && m[j + 1] == ':') { j += 2; continue; } break; }
                            j++;
                        }
                        labels.Add(text.Substring(i + 4, j - (i + 4)).Trim());
                        if (firstCase < 0) firstCase = i;
                        i = j;
                    }
                    else if (string.CompareOrdinal(m, i, "default", 0, 7) == 0 && (i + 7 >= m.Length || !CppText.IsId(m[i + 7])) && Regex.IsMatch(m.Substring(i + 7, Math.Min(20, m.Length - i - 7)), @"^\s*:(?!:)"))
                    {
                        if (defaultPos < 0) defaultPos = i;
                    }
                }
            }
            var labelNames = new HashSet<string>(StringComparer.Ordinal);
            string prefixStyle = null;
            foreach (string l in labels)
            {
                Match nm = Regex.Match(l, @"([A-Za-z_]\w*)\s*$");
                if (!nm.Success) continue;
                labelNames.Add(nm.Groups[1].Value);
                if (prefixStyle == null) prefixStyle = Regex.Replace(l.Substring(0, nm.Index), @"\s+", "");
            }

            // ---- enum の型 ----
            EnumDef best = null;
            int bestScore = 0;
            foreach (var e in enums)
            {
                int score = 0;
                foreach (string l in labels)
                {
                    Match nm = Regex.Match(l, @"([A-Za-z_]\w*)\s*$");
                    if (!nm.Success || !e.Values.Contains(nm.Groups[1].Value)) continue;
                    Match q = Regex.Match(l.Substring(0, nm.Index), @"([A-Za-z_]\w*)\s*::\s*$");
                    if (q.Success && e.Scoped && q.Groups[1].Value != e.Name) continue;
                    score++;
                }
                if (score > bestScore) { best = e; bestScore = score; }
            }
            if (best == null)
            {
                Match last = Regex.Match(sw.Expr, @"([A-Za-z_]\w*)\s*$");
                if (last.Success && !sw.Expr.EndsWith(")", StringComparison.Ordinal))
                {
                    string v = last.Groups[1].Value;
                    foreach (var e in enums)
                    {
                        if (Regex.IsMatch(m, @"\b(?:[A-Za-z_]\w*\s*::\s*)*" + Regex.Escape(e.Name) + @"\b\s*[&*]?\s*(?:const\s*)?[&*]?\s*" + Regex.Escape(v) + @"\b(?=\s*[;,)=\{\[])"))
                        { best = e; break; }
                    }
                }
            }
            if (best == null) { why = "enum の型を決められません。case を 1 つ書くか、変数の宣言が見える場所で試してください"; return null; }

            // ---- 足りない enumerator ----
            var values = best.Values.ToList();
            if (values.Count > 1 && Sentinel.IsMatch(values[values.Count - 1])) values.RemoveAt(values.Count - 1);
            var missing = values.Where(v => !labelNames.Contains(v)).ToList();
            if (missing.Count == 0) { why = "足りない case はありません (" + best.Name + ")"; return null; }

            // ---- 書き方(字下げと、名前の前の修飾)を、いまの case にそろえる ----
            string indent;
            if (firstCase >= 0) indent = LeadingSpace(text, firstCase);
            else indent = LeadingSpace(text, sw.Start) + "  ";
            string body = indent + "  ";

            string prefix;
            if (prefixStyle != null) prefix = prefixStyle;
            else
            {
                var cur = Scopes.Parse(text).Where(s => s.Open < sw.Start && sw.Start < s.Close).OrderByDescending(s => s.Open).FirstOrDefault();
                var curChain = cur == null ? new List<string>() : cur.Chain();
                int common = 0;
                while (common < curChain.Count && common < best.Chain.Count && curChain[common] == best.Chain[common]) common++;
                var parts = best.Chain.Skip(common).ToList();
                if (best.Scoped) parts.Add(best.Name);
                prefix = parts.Count == 0 ? "" : string.Join("::", parts) + "::";
            }

            var sb = new StringBuilder();
            foreach (string v in missing)
                sb.Append(indent).Append("case ").Append(prefix).Append(v).Append(':').Append(eol).Append(body).Append("break;").Append(eol);

            // ---- 挿入する位置: default の前、なければ、閉じる } の前 ----
            int pos;
            string textOut = sb.ToString();
            int anchor = defaultPos >= 0 ? defaultPos : sw.Close;
            int ls = LineStart(text, anchor);
            if (text.Substring(ls, anchor - ls).Trim().Length == 0) pos = ls;
            else { pos = anchor; textOut = eol + textOut + LeadingSpace(text, sw.Start); }

            var plan = new Plan { Position = pos, Text = textOut, EnumName = best.Name };
            plan.Added.AddRange(missing);
            return plan;
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

        /// <summary>pos のある行の、行頭の空白。</summary>
        private static string LeadingSpace(string text, int pos)
        {
            int ls = LineStart(text, pos);
            int e = ls;
            while (e < text.Length && (text[e] == ' ' || text[e] == '\t')) e++;
            return text.Substring(ls, e - ls);
        }
    }
}
