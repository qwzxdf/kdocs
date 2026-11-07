using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// 関数の本体を、ヘッダー ⇄ cpp の間で移す。VS に依存しない。
    /// 文字の編集(位置・長さ・文字)の一覧だけを返す。ファイルを開く・書くのは呼び出し側。
    /// ToCpp: ヘッダーに本体まで書いた関数を、宣言だけに縮めて、cpp に定義として移す。
    /// ToHeader: cpp の定義(Class::Func)を消して、ヘッダーの宣言の「;」を本体に置き換える(クラスの中に書いた関数にする)。
    /// </summary>
    internal static class MoveGen
    {
        public sealed class Edit
        {
            public int Position;
            public int Length;      // 置き換える長さ(挿入だけなら 0)
            public string Text;
        }

        public sealed class Plan
        {
            public List<Edit> Source = new List<Edit>();    // 本体を取り出す側(ToCpp ならヘッダー、ToHeader なら cpp)
            public List<Edit> Target = new List<Edit>();    // 本体を受け取る側
            public int TargetCaret = -1;                    // 適用後に受け取る側へ置くカーソルの位置の目安(Target を適用する前の位置)
        }

        private static readonly Regex InlineWord = new Regex(@"\binline\b[ \t]*", RegexOptions.Compiled);
        private static readonly Regex Blocked = new Regex(@"\b(?:template|constexpr|consteval|friend)\b", RegexOptions.Compiled);

        // ---- ヘッダー → cpp ----

        public static Plan ToCpp(string headerText, FunctionScan.Sig sig, string cppText, string eol, out string why)
        {
            why = null;
            if (!sig.HasBody || sig.BodyOpen < 0) { why = "本体のない関数です"; return null; }
            if (sig.Class != null && !sig.InClass) { why = "ヘッダーに書いた Class::Func の定義は、cpp へ移せません (クラスの中に書いた関数が対象です)"; return null; }
            if (sig.InTemplate) { why = "template のクラスの関数は、移しません (cpp に書けません)"; return null; }
            string m = CppText.Mask(headerText);
            string before = m.Substring(sig.PrefixStart, Math.Max(0, sig.NameStart - sig.PrefixStart));
            if (Blocked.IsMatch(before)) { why = "template・constexpr・friend の関数は、移しません (cpp に書けません)"; return null; }
            if (SignatureSync.HasDirectives(sig.Inner(headerText))) { why = "引数の途中に #if があるので、移せません"; return null; }

            int bodyFirst = sig.InitStart >= 0 ? sig.InitStart : sig.BodyOpen;
            int tailEnd = bodyFirst;
            while (tailEnd > sig.Close + 1 && char.IsWhiteSpace(headerText[tailEnd - 1])) tailEnd--;
            string gap = headerText.Substring(tailEnd, bodyFirst - tailEnd);

            var plan = new Plan();
            // ヘッダー: 本体を「;」に縮める。クラスの外の inline 関数は、宣言から inline を外す
            plan.Source.Add(new Edit { Position = tailEnd, Length = sig.End + 1 - tailEnd, Text = ";" });
            int removed = 0;
            if (!sig.InClass)
            {
                var im = InlineWord.Match(before);
                if (im.Success)
                {
                    plan.Source.Add(new Edit { Position = sig.PrefixStart + im.Index, Length = im.Length, Text = "" });
                    removed = im.Length;
                }
            }
            plan.Source = plan.Source.OrderByDescending(e => e.Position).ToList();

            // 縮めたヘッダーから、宣言として読み直して、cpp の定義の雛形を作らせる
            string h2 = Apply(headerText, plan.Source);
            int expected = sig.Open - removed;
            var decl = FunctionScan.Scan(h2).Where(s => !s.HasBody && s.Name == sig.Name && s.Chain.SequenceEqual(sig.Chain))
                .OrderBy(s => Math.Abs(s.Open - expected)).FirstOrDefault();
            if (decl == null) { why = "宣言に縮めたあとの関数を読み直せませんでした"; return null; }
            var edit = DefinitionGen.PlanDefinition(h2, decl, cppText, eol, out why);
            if (edit == null) return null;

            // 雛形の「{ ... }」を、元の本体に置き換える
            int a = 0;
            while (a < edit.Text.Length && (edit.Text[a] == '\r' || edit.Text[a] == '\n')) a++;
            int z = edit.Text.Length;
            while (z > a && (edit.Text[z - 1] == '\r' || edit.Text[z - 1] == '\n')) z--;
            string pre = edit.Text.Substring(0, a), stub = edit.Text.Substring(a, z - a), suf = edit.Text.Substring(z);
            int brace = stub.LastIndexOf(eol + "{" + eol, StringComparison.Ordinal);
            if (brace < 0) { why = "定義の雛形を読めませんでした"; return null; }
            string head = stub.Substring(0, brace);

            string indent = IndentOf(headerText, FirstCode(m, sig.PrefixStart));
            string bodyText = Dedent(headerText.Substring(bodyFirst, sig.End + 1 - bodyFirst), indent, eol);
            bool allman = gap.Contains("\n");
            string composed = Compose(head, bodyText, sig.InitStart >= 0, sig.BodyOpen - bodyFirst, allman, eol);
            plan.Target.Add(new Edit { Position = edit.Position, Length = 0, Text = pre + composed + suf });
            plan.TargetCaret = edit.Position + pre.Length;
            return plan;
        }

        /// <summary>head(戻り値・名前・引数・const まで)と本体を、cpp の書き方でつなぐ。</summary>
        private static string Compose(string head, string body, bool hasInit, int bodyBraceOffset, bool allman, string eol)
        {
            var sb = new StringBuilder(head);
            string init = "", braced = body;
            if (hasInit)
            {
                init = body.Substring(0, bodyBraceOffset).Trim();
                braced = body.Substring(bodyBraceOffset);
            }
            braced = Expand(braced, eol);
            if (hasInit)
            {
                sb.Append(eol).Append("    ").Append(Regex.Replace(init, @"\s*\r?\n\s*", eol + "    "));
                sb.Append(' ').Append(braced);
            }
            else if (allman) sb.Append(eol).Append(braced);
            else sb.Append(' ').Append(braced);
            return sb.ToString();
        }

        /// <summary>1 行の本体「{ return x_; }」を、複数行「{ / return x_; / }」にする。複数行のものはそのまま。</summary>
        private static string Expand(string braced, string eol)
        {
            if (braced.Contains("\n")) return braced;
            string inner = braced.Substring(1, braced.Length - 2).Trim();
            if (inner.Length == 0) return "{" + eol + "}";
            return "{" + eol + "  " + inner + eol + "}";
        }

        /// <summary>空の本体は「{}」、1 文だけの短い本体は「{ 文 }」の 1 行にする(ヘッダーに書く短い関数の形)。</summary>
        private static string Collapse(string braced)
        {
            var lines = braced.Replace("\r\n", "\n").Split('\n');
            if (lines.Length == 2 && lines[0].Trim() == "{" && lines[1].Trim() == "}") return "{}";
            if (lines.Length == 3 && lines[0].Trim() == "{" && lines[2].Trim() == "}")
            {
                string x = lines[1].Trim();
                if (x.Length > 0 && x.Length <= 60 && !x.Contains("//") && !x.Contains("/*")) return "{ " + x + " }";
            }
            return braced;
        }

        // ---- cpp → ヘッダー ----

        /// <summary>
        /// cpp の定義 def を消して、ヘッダーの宣言 decl(headerText の中)の「;」を本体に置き換える。
        /// 引数の名前が違えば、本体の中の名前に合わせて、ヘッダーの引数の名前を cpp のものにする(既定値はヘッダーのものを残す)。
        /// </summary>
        public static Plan ToHeader(string cppText, FunctionScan.Sig def, string headerText, FunctionScan.Sig decl, string eol, out string why)
        {
            why = null;
            if (!def.HasBody || def.BodyOpen < 0) { why = "本体のない関数です"; return null; }
            if (def.InClass) { why = "クラスの中に書いた関数です"; return null; }
            if (decl.HasBody) { why = "ヘッダーの関数に、すでに本体があります"; return null; }
            string mc = CppText.Mask(cppText);
            string mh = CppText.Mask(headerText);
            string beforeDef = mc.Substring(def.PrefixStart, Math.Max(0, def.NameStart - def.PrefixStart));
            string beforeDecl = mh.Substring(decl.PrefixStart, Math.Max(0, decl.NameStart - decl.PrefixStart));
            if (Blocked.IsMatch(beforeDef) || Blocked.IsMatch(beforeDecl)) { why = "template・constexpr・friend の関数は、移しません"; return null; }
            string declTail = Regex.Replace(mh.Substring(decl.Close + 1, Math.Max(0, decl.End - decl.Close - 1)), @"\s+", " ");
            if (Regex.IsMatch(declTail, @"=\s*(?:0|default|delete)\b")) { why = "純粋仮想・= default・= delete の宣言には、本体を移せません"; return null; }
            if (SignatureSync.HasDirectives(def.Inner(cppText)) || SignatureSync.HasDirectives(decl.Inner(headerText))) { why = "引数の途中に #if があるので、移せません"; return null; }

            var defParams = SignatureSync.SplitParams(def.Inner(cppText));
            var declParams = SignatureSync.SplitParams(decl.Inner(headerText));
            if (defParams == null || declParams == null) { why = "引数を読めませんでした (書きかけかもしれません)"; return null; }
            if (defParams.Count != declParams.Count) { why = "宣言と定義で、引数の個数が違います"; return null; }

            var plan = new Plan();
            string indent = IndentOf(headerText, FirstCode(mh, decl.PrefixStart));
            int bodyFirst = def.InitStart >= 0 ? def.InitStart : def.BodyOpen;
            int tailEnd = bodyFirst;
            while (tailEnd > def.Close + 1 && char.IsWhiteSpace(cppText[tailEnd - 1])) tailEnd--;
            bool allman = cppText.Substring(tailEnd, bodyFirst - tailEnd).Contains("\n");
            string body = Dedent(cppText.Substring(bodyFirst, def.End + 1 - bodyFirst), IndentOf(cppText, FirstCode(mc, def.PrefixStart)), eol);

            // ヘッダー側の編集(後ろから適用する順)
            var h = new List<Edit>();
            string indented = Indent(def.InitStart >= 0 ? body : Collapse(body), indent, eol);
            string joined;
            if (def.InitStart >= 0)
            {
                string init = body.Substring(0, def.BodyOpen - bodyFirst).Trim();
                string braced = body.Substring(def.BodyOpen - bodyFirst);
                joined = eol + indent + "    " + Regex.Replace(init, @"\s*\r?\n\s*", eol + indent + "    ") + " " + Indent(Collapse(braced), indent, eol).TrimStart();
            }
            else if (allman) joined = eol + indent + indented.TrimStart();
            else joined = " " + indented.TrimStart();
            h.Add(new Edit { Position = decl.End, Length = 1, Text = joined });

            // 名前の違いは、本体が使う cpp の名前にそろえる
            var defNames = defParams.Select(p => SignatureSync.ParamName(SignatureSync.StripComments(SignatureSync.StripDefault(p, out _tmp))) ?? "").ToList();
            var declNames = declParams.Select(p => SignatureSync.ParamName(SignatureSync.StripComments(SignatureSync.StripDefault(p, out _tmp))) ?? "").ToList();
            if (!defNames.SequenceEqual(declNames))
            {
                var parts = new List<string>();
                for (int i = 0; i < defParams.Count; i++)
                {
                    string dd;
                    string core = Regex.Replace(SignatureSync.StripComments(SignatureSync.StripDefault(defParams[i], out dd)), @"\s+", " ").Trim();
                    string hd;
                    SignatureSync.StripDefault(declParams[i], out hd);
                    parts.Add(core + (hd != null ? " = " + hd : ""));
                }
                h.Add(new Edit { Position = decl.Open + 1, Length = decl.Close - decl.Open - 1, Text = string.Join(", ", parts) });
            }

            // 関数が cpp の自由関数のとき(Class なし)は、ヘッダーで inline が要る
            if (def.Class == null && !InlineWord.IsMatch(beforeDecl) && !Regex.IsMatch(beforeDecl, @"\bstatic\b"))
            {
                int at = FirstCode(mh, decl.PrefixStart);
                h.Add(new Edit { Position = at, Length = 0, Text = "inline " });
            }
            plan.Target = h.OrderByDescending(e => e.Position).ToList();

            // cpp: 定義を、前後の空行ごと消す
            int start = FirstCode(mc, def.PrefixStart);
            while (start > 0 && cppText[start - 1] != '\n') start--;
            int end = def.End + 1;
            while (end < cppText.Length && (cppText[end] == ' ' || cppText[end] == '\t')) end++;
            if (end < cppText.Length && cppText[end] == '\r') end++;
            if (end < cppText.Length && cppText[end] == '\n') end++;
            // 直前の行が空行なら、その 1 行も一緒に消して、空行が重ならないようにする
            if (start > 0 && cppText[start - 1] == '\n')
            {
                int q = start - 1;
                if (q > 0 && cppText[q - 1] == '\r') q--;
                int ls = q;
                while (ls > 0 && cppText[ls - 1] != '\n') ls--;
                if (cppText.Substring(ls, q - ls).Trim().Length == 0) start = ls;
            }
            plan.Source.Add(new Edit { Position = start, Length = end - start, Text = "" });
            return plan;
        }

        // 引数なしの StripDefault 呼び出し用の使い捨て
        [ThreadStatic] private static string _tmp;

        // ---- 部品 ----

        public static string Apply(string text, List<Edit> descending)
        {
            foreach (var e in descending.OrderByDescending(x => x.Position))
                text = text.Substring(0, e.Position) + e.Text + text.Substring(e.Position + e.Length);
            return text;
        }

        private static int FirstCode(string masked, int from)
        {
            int i = from;
            while (i < masked.Length && char.IsWhiteSpace(masked[i])) i++;
            return i;
        }

        /// <summary>pos のある行の、行頭の空白。</summary>
        private static string IndentOf(string text, int pos)
        {
            int s = pos;
            while (s > 0 && text[s - 1] != '\n') s--;
            int e = s;
            while (e < text.Length && (text[e] == ' ' || text[e] == '\t')) e++;
            return text.Substring(s, e - s);
        }

        /// <summary>2 行目以降の行頭から indent を取り除く(改行は eol にそろえる)。</summary>
        private static string Dedent(string body, string indent, string eol)
        {
            var lines = body.Replace("\r\n", "\n").Split('\n');
            for (int i = 1; i < lines.Length; i++)
            {
                string l = lines[i];
                if (indent.Length > 0 && l.StartsWith(indent, StringComparison.Ordinal)) lines[i] = l.Substring(indent.Length);
                else if (indent.Length > 0) lines[i] = l.TrimStart(' ', '\t').Length == 0 ? "" : l.Substring(Math.Min(l.Length - l.TrimStart(' ', '\t').Length, indent.Length));
            }
            return string.Join(eol, lines);
        }

        /// <summary>2 行目以降の行頭に indent を足す(空行は足さない)。</summary>
        private static string Indent(string body, string indent, string eol)
        {
            var lines = body.Replace("\r\n", "\n").Split('\n');
            for (int i = 1; i < lines.Length; i++)
                if (lines[i].Trim().Length > 0) lines[i] = indent + lines[i];
            return string.Join(eol, lines);
        }
    }
}
