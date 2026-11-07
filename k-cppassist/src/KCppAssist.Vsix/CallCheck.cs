using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// std::make_unique&lt;T&gt;(...)、std::make_shared&lt;T&gt;(...)、new T(...) の引数の「個数」が、T のどのコンストラクターにも合わない呼び出しを見つける。VS に依存しない。
    /// 型の細かい食い違い(暗黙の変換・const・参照)は見ない。確実に間違いと言えるものだけを出す。
    /// 次のクラスは調べない(コンパイラしか決められない): コンストラクターを書いていない(集成体・暗黙のもの)、テンプレート、
    /// 継承したコンストラクター(using Base::Base)、マクロが書かれている、定義が 1 つに決まらない。
    /// </summary>
    internal static class CallCheck
    {
        public sealed class Ctor
        {
            public int Min;         // 必要な引数の数
            public int Max;         // 受け取れる最大の数。負なら上限なし(可変長)
            public string Text;     // 表示用: Name(HWND, int)
        }

        public sealed class ClassInfo
        {
            public string Name;
            public List<Ctor> Ctors = new List<Ctor>();
        }

        public sealed class Finding
        {
            public int Start, Length;       // 赤線を引く範囲
            public int Given;               // 渡している引数の数
            public string Class;
            public string Message;
        }

        public sealed class Options
        {
            public bool Make = true;                    // make_unique / make_shared を調べる
            public bool New = true;                     // new T(...) を調べる
            public ISet<string> Ignore;                 // 調べないクラス名
            public int Caret = -1;                      // 入力中の位置。その呼び出しの括弧の中なら、「足りない」とは言わない(まだ打っている途中)
            public bool Suppressed;                     // (結果) キャレットのために見送ったものがあった
        }

        private static readonly Regex MakeCall = new Regex(
            @"(?<![\w:.>])(?:std\s*::\s*)?(?<fn>make_unique|make_shared)\s*<\s*(?<t>(?:::)?[A-Za-z_]\w*(?:\s*::\s*[A-Za-z_]\w*)*)\s*>\s*\(",
            RegexOptions.Compiled);
        private static readonly Regex NewCall = new Regex(
            @"(?<![\w.>])new\s+(?<t>(?:::)?[A-Za-z_]\w*(?:\s*::\s*[A-Za-z_]\w*)*)\s*\(",
            RegexOptions.Compiled);
        private static readonly Regex Literal = new Regex(
            @"^(?:[+-]?\d[\w.']*|true|false|nullptr|NULL|(?:u8|u|U|L)?""(?:[^""\\]|\\.)*""(?:\s*""(?:[^""\\]|\\.)*"")*|(?:u8|u|U|L)?'(?:[^'\\]|\\.)*')$",
            RegexOptions.Compiled);

        /// <summary>lookup(修飾, 名前) は、クラスの情報(コンストラクターの一覧)。調べられないときは null を返す。</summary>
        public static List<Finding> Check(string text, Func<string, string, ClassInfo> lookup, Options o)
        {
            var found = new List<Finding>();
            if (o == null) o = new Options();
            string m = CppText.Mask(text);
            if (o.Make) foreach (Match x in MakeCall.Matches(m)) Examine(text, m, x, "std::" + x.Groups["fn"].Value, lookup, o, found);
            if (o.New) foreach (Match x in NewCall.Matches(m)) Examine(text, m, x, "new", lookup, o, found);
            found.Sort((a, b) => a.Start.CompareTo(b.Start));
            return found;
        }

        private static void Examine(string text, string m, Match x, string via, Func<string, string, ClassInfo> lookup, Options o, List<Finding> found)
        {
            string full = Regex.Replace(x.Groups["t"].Value, @"\s+", "").TrimStart(':');
            string[] parts = full.Split(new[] { "::" }, StringSplitOptions.RemoveEmptyEntries);
            string name = parts[parts.Length - 1];
            string qual = parts.Length > 1 ? parts[parts.Length - 2] : null;
            if (parts[0] == "std") return;
            if (o.Ignore != null && o.Ignore.Contains(name)) return;

            int open = x.Index + x.Length - 1;
            int close = FunctionScan.MatchClose(m, open, '(', ')');
            if (close < 0) return;
            bool pack;
            var args = Split(m, text, open + 1, close, out pack);
            if (args == null || pack) return;
            int n = args.Count;

            ClassInfo ci = lookup(qual, name);
            if (ci == null || ci.Ctors.Count == 0) return;

            if (ci.Ctors.Any(c => n >= c.Min && (c.Max < 0 || n <= c.Max))) return;
            // 1 個だけ渡していて、リテラルでないなら、同じクラスのコピー・ムーブかもしれない
            if (n == 1 && !Literal.IsMatch(text.Substring(args[0][0], args[0][1] - args[0][0]))) return;

            int minAll = ci.Ctors.Min(c => c.Min);
            bool unbounded = ci.Ctors.Any(c => c.Max < 0);
            int maxAll = unbounded ? -1 : ci.Ctors.Max(c => c.Max);
            bool tooMany = !unbounded && n > maxAll;

            if (!tooMany && o.Caret > open && o.Caret <= close) { o.Suppressed = true; return; }

            var f = new Finding { Class = name, Given = n };
            if (tooMany && maxAll < n && maxAll >= 0 && maxAll < args.Count)
            {
                f.Start = args[maxAll][0];
                f.Length = args[n - 1][1] - args[maxAll][0];
            }
            else
            {
                f.Start = open;
                f.Length = close - open + 1;
            }
            f.Message = Describe(name, via, n, minAll, maxAll, unbounded, ci);
            found.Add(f);
        }

        private static string Describe(string name, string via, int given, int minAll, int maxAll, bool unbounded, ClassInfo ci)
        {
            var sb = new System.Text.StringBuilder();
            string what = via == "new" ? "new " + name : via + "<" + name + ">";
            sb.Append(what).Append(": ").Append(name).Append(" のコンストラクターに、").Append(given).Append(" 個の引数を受け取るものがありません。");
            sb.Append("\n");
            if (given < minAll) sb.Append("引数が足りません(最低 ").Append(minAll).Append(" 個)。");
            else if (!unbounded && given > maxAll) sb.Append("引数が多すぎます(最大 ").Append(maxAll).Append(" 個)。");
            else sb.Append("その個数のコンストラクターがありません。");
            sb.Append("\n候補:");
            foreach (var c in ci.Ctors.Take(5)) sb.Append("\n  ").Append(c.Text);
            if (ci.Ctors.Count > 5) sb.Append("\n  ...");
            return sb.ToString();
        }

        // ---- クラスの読み取り ----

        /// <summary>
        /// text(ヘッダーか cpp)から、クラス name の定義を探し、コンストラクターの一覧を返す。
        /// 調べるべきでないクラス(上の説明)や、定義が見つからない・複数あるときは null。qualifier は「ns::Name」の ns(なければ null)。
        /// </summary>
        public static ClassInfo ReadClass(string text, string name, string qualifier)
        {
            string m = CppText.Mask(text);
            var re = new Regex(
                @"(?<![\w])(?<!\benum\s+)(?:class|struct)\s+" +
                @"(?:(?:alignas\s*\([^)]*\)|__declspec\s*\([^)]*\)|\[\[[^\]]*\]\]|[A-Z][A-Z0-9_]*_API|[A-Z][A-Z0-9_]*EXPORT[A-Z0-9_]*)\s+)*" +
                Regex.Escape(name) + @"\s*(?:final\s*)?(?::[^;{}]*)?\{");
            var hits = re.Matches(m);
            if (hits.Count != 1) return null;
            Match hit = hits[0];
            int bodyOpen = hit.Index + hit.Length - 1;
            int bodyClose = FunctionScan.MatchClose(m, bodyOpen, '{', '}');
            if (bodyClose < 0) return null;

            // テンプレートのクラスは調べない
            int sep = m.LastIndexOfAny(new[] { ';', '{', '}' }, Math.Max(0, hit.Index - 1));
            string lead = m.Substring(sep < 0 ? 0 : sep + 1, hit.Index - (sep < 0 ? 0 : sep + 1));
            if (Regex.IsMatch(lead, @"\btemplate\s*<")) return null;

            // 「ns::Name」と書いてあるなら、そのヘッダーが ns を名前空間として持っていること(別の名前空間の同じ名前を避ける)
            if (!string.IsNullOrEmpty(qualifier) && !Regex.IsMatch(m, @"\bnamespace\s+(?:[\w:]+\s*::\s*)?" + Regex.Escape(qualifier) + @"\b") &&
                !Regex.IsMatch(m, @"(?<![\w])(?:class|struct)\s+" + Regex.Escape(qualifier) + @"\b[^;{]*\{")) return null;

            string body = m.Substring(bodyOpen + 1, bodyClose - bodyOpen - 1);
            if (Regex.IsMatch(body, @"\busing\s+(?:\w+\s*::\s*)*(\w+)\s*::\s*\1\s*;")) return null;     // using Base::Base
            if (Regex.IsMatch(body, @"\b[A-Z][A-Z0-9_]{2,}\s*\(")) return null;                           // マクロ

            var info = new ClassInfo { Name = name };
            foreach (var s in FunctionScan.Scan(text))
            {
                if (s.Class != name || s.Name != name || s.Open <= bodyOpen || s.Open >= bodyClose) continue;
                bool pack;
                var ps = Split(m, text, s.Open + 1, s.Close, out pack);
                if (ps == null) return null;
                var c = new Ctor();
                int req = 0, all = 0;
                bool packSeen = false;
                bool onlyVoid = ps.Count == 1 && m.Substring(ps[0][0], ps[0][1] - ps[0][0]).Trim() == "void";
                if (!onlyVoid)
                    foreach (var p in ps)
                    {
                        string pt = m.Substring(p[0], p[1] - p[0]);
                        if (pt.Contains("...")) { packSeen = true; continue; }
                        all++;
                        if (pt.IndexOf('=') < 0) req++;
                    }
                c.Min = req;
                c.Max = packSeen ? -1 : all;
                string inner = Regex.Replace(text.Substring(s.Open + 1, s.Close - s.Open - 1), @"\s+", " ").Trim();
                if (inner.Length > 70) inner = inner.Substring(0, 67) + "...";
                c.Text = name + "(" + inner + ")";
                info.Ctors.Add(c);
            }
            return info.Ctors.Count == 0 ? null : info;
        }

        /// <summary>text がクラス name を定義しているか(前方宣言は含めない)。</summary>
        public static bool DefinesClass(string text, string name)
        {
            return Regex.IsMatch(CppText.Mask(text),
                @"(?<![\w])(?<!\benum\s+)(?:class|struct)\s+(?:[A-Z][A-Z0-9_]*_API\s+)?" + Regex.Escape(name) + @"\s*(?:final\s*)?(?::[^;{}]*)?\{");
        }

        // ---- 引数の切り分け ----

        /// <summary>
        /// m の [from, to) を、一番外側のカンマで区切った各引数の範囲 {開始, 終わり} にする。空なら 0 個。
        /// カンマの数え間違いのおそれがある(括弧や &lt;&gt; が閉じていない、空の引数)ときは null。... があれば pack = true。
        /// </summary>
        public static List<int[]> Split(string m, string orig, int from, int to, out bool pack)
        {
            pack = false;
            var list = new List<int[]>();
            if (orig.Substring(from, to - from).Trim().Length == 0) return list;
            int depth = 0, angle = 0, start = from;
            for (int i = from; i < to; i++)
            {
                char c = m[i];
                if (c == '.' && i + 2 < to && m[i + 1] == '.' && m[i + 2] == '.') pack = true;
                if (c == '(' || c == '[' || c == '{') depth++;
                else if (c == ')' || c == ']' || c == '}') { depth--; if (depth < 0) return null; }
                else if (depth == 0)
                {
                    if (c == '<' && i > from && CppText.IsId(m[i - 1]) && !(i + 1 < to && (m[i + 1] == '<' || m[i + 1] == '='))) angle++;
                    else if (c == '>' && angle > 0 && !(i > from && m[i - 1] == '-')) angle--;
                    else if (c == ',' && angle == 0)
                    {
                        if (!Add(list, orig, start, i)) return null;
                        start = i + 1;
                    }
                }
            }
            if (depth != 0 || angle != 0) return null;
            if (!Add(list, orig, start, to)) return null;
            return list;
        }

        private static bool Add(List<int[]> list, string orig, int s, int e)
        {
            while (s < e && char.IsWhiteSpace(orig[s])) s++;
            while (e > s && char.IsWhiteSpace(orig[e - 1])) e--;
            if (e <= s) return false;
            list.Add(new[] { s, e });
            return true;
        }
    }
}
