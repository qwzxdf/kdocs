using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>cpp の関数が属するクラス。名前の前に付いた修飾(入れ子のクラスや名前空間)も持つ。</summary>
    internal sealed class ClassRef
    {
        public string Name;
        public List<string> Outer = new List<string>();        // 「Outer::Inner::Func」の Outer。外側から順に
        public List<string> Namespaces = new List<string>();   // cpp でその関数を囲んでいる namespace。外側から順に
        public int InFileOpen = -1;                            // クラスが、いまのファイルの中で定義されているとき、その「{」の位置

        public string Qualified { get { return string.Join("::", Outer.Concat(new[] { Name })); } }
    }

    /// <summary>namespace / class / struct の入れ子を、文字から読む。VS に依存しない。</summary>
    internal static class Scopes
    {
        public sealed class Scope
        {
            public bool IsClass;
            public string Name;          // 無名 namespace は null、「a::b」の namespace は 2 つに分けずそのまま
            public int Open, Close;
            public bool IsStruct;
            public Scope Parent;

            /// <summary>外側から順の名前の並び(自分を含む)。「a::b」は a, b に分ける。</summary>
            public List<string> Chain()
            {
                var list = Parent == null ? new List<string>() : Parent.Chain();
                if (Name != null) list.AddRange(Name.Split(new[] { "::" }, StringSplitOptions.RemoveEmptyEntries).Select(s => s.Trim()));
                return list;
            }

            public List<string> ParentChain() { return Parent == null ? new List<string>() : Parent.Chain(); }
        }

        private static readonly Regex Ns = new Regex(@"\b(?:inline\s+)?namespace\s*((?:[A-Za-z_]\w*\s*::\s*)*[A-Za-z_]\w*)?\s*\{");
        private static readonly Regex Cls = new Regex(@"\b(class|struct)\s+(?:[A-Za-z_]\w*\s+)*?([A-Za-z_]\w*)\s*(?:final\s*)?(?::[^;{]*)?\{");

        /// <summary>text の中の namespace と class / struct(enum class は除く)を、位置の順に集める。</summary>
        public static List<Scope> Parse(string text)
        {
            string m = CppText.Mask(text);
            var list = new List<Scope>();
            foreach (Match x in Ns.Matches(m))
            {
                int open = x.Index + x.Length - 1;
                int close = Close(m, open);
                if (close < 0) continue;
                list.Add(new Scope { IsClass = false, Name = x.Groups[1].Success ? Regex.Replace(x.Groups[1].Value, @"\s+", "") : null, Open = open, Close = close });
            }
            foreach (Match x in Cls.Matches(m))
            {
                string before = m.Substring(Math.Max(0, x.Index - 8), Math.Min(8, x.Index));
                if (Regex.IsMatch(before, @"enum\s*$")) continue;
                int open = x.Index + x.Length - 1;
                int close = Close(m, open);
                if (close < 0) continue;
                list.Add(new Scope { IsClass = true, Name = x.Groups[2].Value, Open = open, Close = close, IsStruct = x.Groups[1].Value == "struct" });
            }
            list.Sort((a, b) => a.Open.CompareTo(b.Open));
            foreach (var s in list)
                s.Parent = list.Where(o => o != s && o.Open < s.Open && s.Close < o.Close).OrderByDescending(o => o.Open).FirstOrDefault();
            return list;
        }

        private static int Close(string m, int open)
        {
            int depth = 0;
            for (int i = open; i < m.Length; i++)
            {
                if (m[i] == '{') depth++;
                else if (m[i] == '}') { depth--; if (depth == 0) return i; }
            }
            return -1;
        }

        /// <summary>caret を中に含む namespace の名前の並び(外側から順)。</summary>
        public static List<string> NamespacesAt(List<Scope> scopes, int caret)
        {
            var inner = scopes.Where(s => !s.IsClass && s.Open < caret && caret < s.Close).OrderByDescending(s => s.Open).FirstOrDefault();
            return inner == null ? new List<string>() : inner.Chain();
        }

        /// <summary>
        /// ref に合うクラスを scopes の中から探して、合い具合の点を付ける(-1 は合わない)。
        /// 「Outer::Inner::Func」の Outer が、クラスの外側の並びの末尾と一致しなければ合わない。
        /// そのうえで、cpp を囲む namespace と外側の並びが末尾からどれだけ一致するかを点にする。
        /// </summary>
        public static int Score(Scope cls, ClassRef r)
        {
            if (!cls.IsClass || cls.Name != r.Name) return -1;
            var parents = cls.ParentChain();
            if (r.Outer.Count > 0)
            {
                if (parents.Count < r.Outer.Count) return -1;
                if (!parents.Skip(parents.Count - r.Outer.Count).SequenceEqual(r.Outer)) return -1;
            }
            var want = r.Namespaces.Concat(r.Outer).ToList();
            int score = 0;
            for (int i = 1; i <= Math.Min(parents.Count, want.Count); i++)
            {
                if (parents[parents.Count - i] == want[want.Count - i]) score++;
                else break;
            }
            return score;
        }

        /// <summary>text の中の、ref に合うクラス(点の高い順)。</summary>
        public static List<KeyValuePair<Scope, int>> Matches(string text, ClassRef r)
        {
            return Parse(text).Select(s => new KeyValuePair<Scope, int>(s, Score(s, r))).Where(p => p.Value >= 0).OrderByDescending(p => p.Value).ToList();
        }
    }
}
