using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// 基底クラスの仮想関数から、派生クラスの override の宣言を作る。VS に依存しない。
    /// 基底クラスの定義は、呼び出し側が集めた文字(texts)から探す。
    /// </summary>
    internal static class OverrideGen
    {
        public sealed class Plan
        {
            public int Position;
            public string Text;
            public string ClassName;
            public List<string> Added = new List<string>();
            public bool PureOnly;       // 純粋仮想関数だけを足した
        }

        private sealed class Func
        {
            public string Name, Return, Params, Quals;
            public int ParamCount;
            public bool IsConst, Virtual, Override, Pure;
            public string Key { get { return Name + "/" + ParamCount + (IsConst ? "c" : ""); } }
        }

        /// <summary>caret を含むクラスの、基底クラスの名前(名前空間の修飾とテンプレート引数は除く)。クラスがなければ null。</summary>
        public static List<string> BaseNamesAt(string text, int caret)
        {
            string m = CppText.Mask(text);
            var cls = Innermost(text, caret);
            return cls == null ? null : BaseNames(m, cls);
        }

        private static Scopes.Scope Innermost(string text, int caret)
        {
            return Scopes.Parse(text).Where(s => s.IsClass && s.Open < caret && caret <= s.Close).OrderByDescending(s => s.Open).FirstOrDefault();
        }

        private static List<string> BaseNames(string m, Scopes.Scope cls)
        {
            var list = new List<string>();
            int from = Math.Max(0, cls.Open - 600);
            string head = m.Substring(from, cls.Open - from);
            Match h = Regex.Match(head, @"\b(?:class|struct)\s+[^;{}]*$");
            if (!h.Success) return list;
            Match colon = Regex.Match(h.Value, @"(?<!:):(?!:)");
            if (!colon.Success) return list;
            string bases = h.Value.Substring(colon.Index + 1);
            foreach (string part in SplitTop(bases))
            {
                string p = Regex.Replace(part, @"<.*>", "");
                p = Regex.Replace(p, @"\b(?:public|private|protected|virtual)\b", "");
                Match n = Regex.Match(p.Trim(), @"([A-Za-z_]\w*)\s*$");
                if (n.Success) list.Add(n.Groups[1].Value);
            }
            return list;
        }

        private static IEnumerable<string> SplitTop(string s)
        {
            int depth = 0, start = 0;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '<' || c == '(') depth++;
                else if (c == '>' || c == ')') depth--;
                else if (c == ',' && depth == 0) { yield return s.Substring(start, i - start); start = i + 1; }
            }
            yield return s.Substring(start);
        }

        // ---- クラスの本体の関数の宣言 ----

        private static List<Func> Funcs(string text, string m, Scopes.Scope cls)
        {
            var list = new List<Func>();
            string d0 = ClassPlace.Depth0(m, cls.Open, cls.Close);
            foreach (string raw in d0.Split(';'))
            {
                string s = Regex.Replace(raw, @"\s+", " ").Trim();
                s = Regex.Replace(s, @"^(?:(?:public|private|protected)\s*:\s*)+", "");
                if (s.Length == 0 || !s.Contains("(")) continue;
                if (Regex.IsMatch(s, @"^(?:using|typedef|friend|static_assert|template\s*<[^>]*>\s*(?:friend|using))\b")) continue;
                if (Regex.IsMatch(s, @"\boperator\b") || s.Contains("~")) continue;

                int po = FirstParen(s);
                if (po < 0) continue;
                int pc = MatchParen(s, po);
                if (pc < 0) continue;
                Match nm = Regex.Match(s.Substring(0, po), @"([A-Za-z_]\w*)\s*$");
                if (!nm.Success) continue;
                string name = nm.Groups[1].Value;
                string ret = s.Substring(0, nm.Index).Trim();
                string tail = s.Substring(pc + 1).Trim();
                var f = new Func { Name = name, Params = s.Substring(po + 1, pc - po - 1).Trim() };
                f.Virtual = Regex.IsMatch(ret, @"\bvirtual\b");
                f.Override = Regex.IsMatch(tail, @"\boverride\b");
                f.Pure = Regex.IsMatch(tail, @"=\s*0\s*$");
                f.IsConst = Regex.IsMatch(tail, @"^(?:\w+\s+)*?const\b");
                f.Return = Regex.Replace(ret, @"\b(?:virtual|inline|constexpr|static|explicit)\b", "").Trim();
                f.Return = Regex.Replace(f.Return, @"\s+", " ");
                if (f.Return.Length == 0 && !f.Override) continue;     // コンストラクター
                var q = new List<string>();
                if (f.IsConst) q.Add("const");
                if (Regex.IsMatch(tail, @"\bnoexcept\b")) q.Add("noexcept");
                f.Quals = string.Join(" ", q);
                f.ParamCount = f.Params.Length == 0 || f.Params == "void" ? 0 : SplitTop2(f.Params).Count();
                list.Add(f);
            }
            return list;
        }

        private static int FirstParen(string s)
        {
            // 戻り値の型の中の括弧(関数ポインターなど)は扱わない。名前の直後の最初の「(」
            return s.IndexOf('(');
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

        private static IEnumerable<string> SplitTop2(string s)
        {
            int depth = 0, start = 0;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '<' || c == '(' || c == '[' || c == '{') depth++;
                else if (c == '>' || c == ')' || c == ']' || c == '}') depth--;
                else if (c == ',' && depth == 0) { yield return s.Substring(start, i - start); start = i + 1; }
            }
            yield return s.Substring(start);
        }

        /// <summary>引数から、既定値(= ...)を取り除く(override には既定値を書かない)。</summary>
        private static string StripDefaults(string ps)
        {
            if (ps.Length == 0) return ps;
            var parts = new List<string>();
            foreach (string p in SplitTop2(ps))
            {
                int depth = 0, cut = -1;
                for (int i = 0; i < p.Length; i++)
                {
                    char c = p[i];
                    if (c == '<' || c == '(' || c == '[' || c == '{') depth++;
                    else if (c == '>' || c == ')' || c == ']' || c == '}') depth--;
                    else if (c == '=' && depth == 0) { cut = i; break; }
                }
                parts.Add((cut >= 0 ? p.Substring(0, cut) : p).Trim());
            }
            return string.Join(", ", parts);
        }

        // ---- 基底クラスの仮想関数を集める ----

        private sealed class Doc { public string Text, Mask; public List<Scopes.Scope> Scopes; }

        private static void Gather(string className, List<Doc> docs, Dictionary<string, Func> found, HashSet<string> visited, int depth)
        {
            if (depth > 6 || !visited.Add(className)) return;
            foreach (var d in docs)
            {
                var cls = d.Scopes.FirstOrDefault(s => s.IsClass && s.Name == className);
                if (cls == null) continue;
                foreach (var f in Funcs(d.Text, d.Mask, cls))
                    if ((f.Virtual || f.Override) && !found.ContainsKey(f.Key)) found[f.Key] = f;   // 近い基底が先
                foreach (string b in BaseNames(d.Mask, cls)) Gather(b, docs, found, visited, depth + 1);
                return;      // 最初に見つかった定義だけを使う
            }
        }

        /// <summary>caret のあるクラスに、まだない override の宣言を足す計画。できなければ null で、理由を why に入れる。</summary>
        public static Plan Make(string text, int caret, IList<string> otherTexts, string eol, out string why)
        {
            why = null;
            string m = CppText.Mask(text);
            var cls = Innermost(text, caret);
            if (cls == null) { why = "カーソルが、class / struct の中にありません"; return null; }
            if (ClassPlace.LineStart(text, cls.Open) == ClassPlace.LineStart(text, cls.Close)) { why = "クラスが 1 行に書かれています。複数行に広げてください"; return null; }
            var bases = BaseNames(m, cls);
            if (bases.Count == 0) { why = "基底クラスがありません。class " + cls.Name + " : public Base の形にしてください"; return null; }

            var docs = new List<Doc> { new Doc { Text = text, Mask = m, Scopes = Scopes.Parse(text) } };
            foreach (string t in otherTexts)
            {
                string mm = CppText.Mask(t);
                docs.Add(new Doc { Text = t, Mask = mm, Scopes = Scopes.Parse(t) });
            }
            var found = new Dictionary<string, Func>();
            var visited = new HashSet<string> { cls.Name };
            var missingBases = new List<string>();
            foreach (string b in bases)
            {
                if (!docs.Any(d => d.Scopes.Any(s => s.IsClass && s.Name == b))) { missingBases.Add(b); continue; }
                Gather(b, docs, found, visited, 0);
            }
            if (found.Count == 0)
            {
                why = missingBases.Count > 0 ? "基底クラスの定義が見つかりません (" + string.Join(", ", missingBases) + ")" : "基底クラスに、仮想関数がありません";
                return null;
            }

            // すでにこのクラスにある関数(名前と引数の個数が同じ)は足さない
            var own = new HashSet<string>(Funcs(text, m, cls).Select(f => f.Key));
            var todo = found.Values.Where(f => !own.Contains(f.Key)).ToList();
            if (todo.Count == 0) { why = "足りない仮想関数はありません"; return null; }

            // 純粋仮想関数が残っていれば、それだけを足す(派生クラスを作るのに必須)。なければ、残りの仮想関数を全部足す
            var pure = todo.Where(f => f.Pure).ToList();
            bool pureOnly = pure.Count > 0 && pure.Count < todo.Count;
            if (pure.Count > 0) todo = pure;

            string indent = ClassPlace.MemberIndent(text, m, cls);
            var sb = new StringBuilder();
            var plan = new Plan { ClassName = cls.Name, PureOnly = pureOnly };
            foreach (var f in todo)
            {
                sb.Append(indent).Append(f.Return).Append(' ').Append(f.Name).Append('(').Append(StripDefaults(f.Params)).Append(')');
                if (f.Quals.Length > 0) sb.Append(' ').Append(f.Quals);
                sb.Append(" override;").Append(eol);
                plan.Added.Add(f.Name);
            }
            ClassPlace.Insert(text, m, cls, sb.ToString(), eol, out plan.Position, out plan.Text);
            return plan;
        }
    }
}
