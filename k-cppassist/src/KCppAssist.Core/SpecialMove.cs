using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// クラスのコンストラクター・デストラクターを、ヘッダーから cpp に移す(宣言だけをヘッダーに残す)。
    /// 本体のあるもの、「= default」のもの、どちらも対象。VS に依存しない。
    /// 加えて、class を struct にする(デフォルトのコンストラクター・デストラクターを消す)。
    /// </summary>
    internal static class SpecialMove
    {
        public sealed class Result
        {
            public string Header, Cpp;
            public List<string> Moved = new List<string>();
        }

        /// <summary>
        /// caret のクラスの、コンストラクター・デストラクターを cpp に移した結果。移せるものがなければ null で、理由を why に入れる。
        /// cppText が空でもよい(新しい cpp)。
        /// </summary>
        public static Result Make(string header, int caret, string cppText, string eol, out string why)
        {
            why = null;
            var cls = MemberScan.At(header, caret);
            if (cls == null) { why = L.T("カーソルが、class / struct の中にありません"); return null; }
            string name = cls.Name, n = Regex.Escape(name);
            int open = cls.Scope.Open;
            var r = new Result { Header = header, Cpp = cppText };

            // 1. 本体のあるコンストラクター(初期化子リストも含めて、MoveGen に任せる)
            var skipped = new HashSet<string>();
            for (int guard = 0; guard < 60; guard++)
            {
                int close = Scopes.MatchBrace(CppText.Mask(r.Header), open);
                if (close < 0) break;
                var sig = FunctionScan.Scan(r.Header).FirstOrDefault(s => s.HasBody && s.InClass && s.Class == name && s.Name == name && s.Open > open && s.Open < close
                    && !s.InTemplate && !skipped.Contains(s.Inner(r.Header).Trim()));
                if (sig == null) break;
                string w;
                var plan = MoveGen.ToCpp(r.Header, sig, r.Cpp, eol, out w);
                if (plan == null) { skipped.Add(sig.Inner(r.Header).Trim()); continue; }
                r.Header = MoveGen.Apply(r.Header, plan.Source);
                r.Cpp = MoveGen.Apply(r.Cpp, plan.Target);
                r.Moved.Add(name + "(" + Regex.Replace(sig.Inner(header).Trim(), @"\s+", " ") + ")");
            }

            // 2. 「= default」のコンストラクター(引数なし)
            var rxCtorDef = new Regex(@"^([ \t]*)((?:explicit[ \t]+)?)" + n + @"[ \t]*\(\s*\)[ \t]*(noexcept)?[ \t]*=[ \t]*default[ \t]*;", RegexOptions.Multiline);
            for (int guard = 0; guard < 10; guard++)
            {
                var m = FindIn(r.Header, open, rxCtorDef);
                if (m == null) break;
                string repl = m.Groups[1].Value + m.Groups[2].Value + name + "()" + (m.Groups[3].Success ? " noexcept" : "") + ";";
                r.Header = r.Header.Substring(0, m.Index) + repl + r.Header.Substring(m.Index + m.Length);
                var decl = FunctionScan.Scan(r.Header).FirstOrDefault(s => !s.HasBody && s.Class == name && s.Name == name && s.Open > open && s.Inner(r.Header).Trim().Length == 0);
                string w;
                var de = decl == null ? null : DefinitionGen.PlanDefinition(r.Header, decl, r.Cpp, eol, out w);
                if (de != null) r.Cpp = r.Cpp.Substring(0, de.Position) + ForwardDecl.AsDefaulted(de.Text, eol) + r.Cpp.Substring(de.Position);
                r.Moved.Add(name + "()");
            }

            // 3. デストラクター(= default と、本体のあるもの)
            var rxDtor = new Regex(@"^([ \t]*)((?:virtual[ \t]+)?)~" + n + @"[ \t]*\(\s*\)[ \t]*(noexcept)?[ \t]*(override)?[ \t]*(=[ \t]*default[ \t]*;|(?=\{))", RegexOptions.Multiline);
            for (int guard = 0; guard < 10; guard++)
            {
                var m = FindIn(r.Header, open, rxDtor);
                if (m == null) break;
                bool noex = m.Groups[3].Success;
                string body = null;
                int end = m.Index + m.Length;
                if (!m.Groups[5].Value.StartsWith("="))
                {
                    int bo = end;
                    while (bo < r.Header.Length && r.Header[bo] != '{') bo++;
                    int bc = Scopes.MatchBrace(CppText.Mask(r.Header), bo);
                    if (bc < 0) break;
                    string inner = r.Header.Substring(bo + 1, bc - bo - 1);
                    string cUnit = CppText.IndentUnit(r.Cpp, r.Header), hUnit = CppText.IndentUnit(r.Header, r.Cpp);
                    body = ReindentBody(inner, m.Groups[1].Value + hUnit, cUnit, eol);
                    end = bc + 1;
                    while (end < r.Header.Length && (r.Header[end] == ' ' || r.Header[end] == '\t')) end++;
                    if (end < r.Header.Length && r.Header[end] == ';') end++;
                }
                string repl = m.Groups[1].Value + m.Groups[2].Value + "~" + name + "()" + (noex ? " noexcept" : "") + (m.Groups[4].Success ? " override" : "") + ";";
                r.Header = r.Header.Substring(0, m.Index) + repl + r.Header.Substring(end);
                string after = ForwardDecl.AddOutOfClassDef(r.Header, r.Cpp, name, "dtor", noex, eol, body, MoveGen.AllmanOf(r.Cpp) ?? MoveGen.AllmanOf(r.Header) ?? false);
                if (after == r.Cpp) { r.Moved.Add("~" + name + "()"); continue; }
                r.Cpp = after;
                r.Moved.Add("~" + name + "()");
            }

            if (r.Moved.Count == 0) { why = L.T("cpp に移せるコンストラクター・デストラクターがありません (宣言だけのものは、そのままです)"); return null; }
            return r;
        }

        /// <summary>class の本体の中(open の「{」より後ろ、閉じるまで)で最初に見つかる match。</summary>
        private static Match FindIn(string text, int open, Regex rx)
        {
            string m = CppText.Mask(text);
            int close = Scopes.MatchBrace(m, open);
            if (close < 0) return null;
            var x = rx.Match(m, open + 1);
            return x.Success && x.Index < close ? x : null;
        }

        /// <summary>デストラクターの本体(波括弧の中)を、cpp の字下げにして、各行の末尾に eol を付けて返す。空の本体は ""。</summary>
        private static string ReindentBody(string inner, string headerIndent, string cUnit, string eol)
        {
            var lines = inner.Replace("\r\n", "\n").Split('\n').ToList();
            while (lines.Count > 0 && lines[0].Trim().Length == 0) lines.RemoveAt(0);
            while (lines.Count > 0 && lines[lines.Count - 1].Trim().Length == 0) lines.RemoveAt(lines.Count - 1);
            var sb = new StringBuilder();
            foreach (string l in lines)
            {
                string t = l.StartsWith(headerIndent, StringComparison.Ordinal) ? l.Substring(headerIndent.Length) : l.TrimStart(' ', '\t');
                if (t.Trim().Length > 0) sb.Append(cUnit).Append(t.TrimEnd());
                sb.Append(eol);
            }
            return sb.ToString();
        }

        // ---- class → struct ----

        /// <summary>
        /// class を struct にする。デフォルトのコンストラクター・デストラクター(「Foo() = default;」「Foo() {}」「~Foo() = default;」「~Foo() {}」)を消す。
        /// 先頭の public: は要らないので消す。先頭に指定子なしで書いたメンバー(class では private)は、private のまま残すために、private: を足す。
        /// 継承の指定子がないもの(class では private 継承)は、private 継承のまま残すために private を足す。
        /// </summary>
        public static Refactor.Change ToStruct(string text, MemberScan.ClassInfo cls, string eol, out string why)
        {
            why = null;
            if (cls.IsStruct) { why = L.T("すでに struct です"); return null; }
            string m = CppText.Mask(text);
            int open = cls.Scope.Open, close = cls.Scope.Close;
            string n = Regex.Escape(cls.Name);

            // 頭の「class」
            Match head = null;
            foreach (Match x in Regex.Matches(m.Substring(0, open), @"\bclass\b(?=\s+(?:[A-Z][A-Z0-9_]*_API\s+|alignas\s*\([^)]*\)\s+)*" + n + @"\b)")) head = x;
            if (head == null) { why = L.T("class の行を読めませんでした"); return null; }
            var ch = new Refactor.Change();
            ch.Add(head.Index, 5, "struct");

            // 継承の指定子がなければ、private を足す(class の既定は private 継承。struct は public 継承になるので、意味を変えない)
            int colon = -1;
            {
                int p = head.Index + head.Length;
                int angle = 0;
                for (int i = p; i < open; i++)
                {
                    char c = m[i];
                    if (c == '<') angle++;
                    else if (c == '>') angle--;
                    else if (c == ':' && angle == 0 && !(i + 1 < open && m[i + 1] == ':') && !(i > 0 && m[i - 1] == ':')) { colon = i; break; }
                }
            }
            if (colon >= 0)
            {
                string list = m.Substring(colon + 1, open - colon - 1);
                int angle = 0, start = 0;
                var parts = new List<Tuple<int, int>>();
                for (int i = 0; i <= list.Length; i++)
                {
                    char c = i < list.Length ? list[i] : ',';
                    if (c == '<') angle++;
                    else if (c == '>') angle--;
                    else if (c == ',' && angle == 0) { parts.Add(Tuple.Create(start, i)); start = i + 1; }
                }
                foreach (var pt in parts)
                {
                    string seg = list.Substring(pt.Item1, pt.Item2 - pt.Item1);
                    if (seg.Trim().Length == 0 || Regex.IsMatch(seg, @"\b(?:public|private|protected)\b")) continue;
                    int at = colon + 1 + pt.Item1;
                    while (at < open && char.IsWhiteSpace(m[at])) at++;
                    ch.Add(at, 0, "private ");
                }
            }

            // クラスの本体の直下の行(入れ子の中は見ない)
            bool hasOtherCtor = false;
            var lines = new List<Tuple<int, int, string>>();      // (行の頭, 行の長さ(改行を含む), 種類)
            int depth = 0;
            int firstStmt = -1, firstLabel = -1;
            string firstLabelName = null;
            for (int i = open; i < close; i++)
            {
                char c = m[i];
                if (c == '{') depth++;
                else if (c == '}') depth--;
                if (!(c == '\n' && depth == 1)) continue;
                int ls = i + 1, le = ls;
                while (le < close && m[le] != '\n') le++;
                string ml = m.Substring(ls, le - ls).Trim();
                if (ml.Length == 0) continue;
                var lab = Regex.Match(ml, @"^(public|protected|private)\s*:$");
                if (lab.Success) { if (firstLabel < 0) { firstLabel = ls; firstLabelName = lab.Groups[1].Value; } continue; }
                if (firstStmt < 0 && firstLabel < 0) firstStmt = ls;
                int lineLen = Math.Min(text.Length, le + 1) - ls;
                if (Regex.IsMatch(ml, @"^(?:explicit\s+)?" + n + @"\s*\(\s*\)\s*(?:noexcept\s*)?(?:=\s*default\s*;|\{\s*\})$")) lines.Add(Tuple.Create(ls, lineLen, "ctor"));
                else if (Regex.IsMatch(ml, @"^~" + n + @"\s*\(\s*\)\s*(?:noexcept\s*)?(?:=\s*default\s*;|\{\s*\})$")) lines.Add(Tuple.Create(ls, lineLen, "dtor"));
                else if (Regex.IsMatch(ml, @"(?<![~\w])" + n + @"\s*\(") && !Regex.IsMatch(ml, n + @"\s*\(\s*(?:const\s+)?" + n + @"\s*&")) hasOtherCtor = true;
            }
            var removes = new List<Tuple<int, int>>();
            foreach (var l in lines)
            {
                // ほかのコンストラクターがあるとき、引数なしのコンストラクターを消すと、書けなくなる(暗黙の既定コンストラクターが作られない)
                if (l.Item3 == "ctor" && hasOtherCtor) continue;
                // 継承や仮想関数があるとき、デストラクターを消すと、意味が変わりうる(virtual は、そもそも対象の形ではない)
                removes.Add(Tuple.Create(l.Item1, l.Item2));
            }

            // 先頭の public: は消す。先頭に指定子なしで書いたメンバーがあれば、private: を足す
            string classIndent = ClassPlace.ClassIndent(text, cls.Scope);
            string labelIndent = classIndent + CppText.LabelOffset(text);
            if (firstStmt >= 0 && (firstLabel < 0 || firstStmt < firstLabel))
                ch.Add(firstStmt, 0, labelIndent + "private:" + eol);
            else if (firstLabel >= 0 && firstLabelName == "public" && (firstStmt < 0 || firstLabel < firstStmt))
            {
                int le = firstLabel;
                while (le < close && text[le] != '\n') le++;
                removes.Add(Tuple.Create(firstLabel, Math.Min(text.Length, le + 1) - firstLabel));
            }
            // 消した行が「{」の行の直後から続いていて、その次が空行なら、空行も消す(先頭に空行が残らないように)
            removes = removes.OrderBy(x => x.Item1).ToList();
            int headLineEnd = text.IndexOf('\n', open);
            var merged = new List<Tuple<int, int>>();
            foreach (var rm in removes)
            {
                if (merged.Count > 0 && merged[merged.Count - 1].Item1 + merged[merged.Count - 1].Item2 == rm.Item1)
                    merged[merged.Count - 1] = Tuple.Create(merged[merged.Count - 1].Item1, merged[merged.Count - 1].Item2 + rm.Item2);
                else merged.Add(rm);
            }
            foreach (var rm in merged)
            {
                int len = rm.Item2;
                int e = rm.Item1 + len;
                if (headLineEnd >= 0 && rm.Item1 == headLineEnd + 1)
                    while (e < close)
                    {
                        int nl = text.IndexOf('\n', e);
                        if (nl < 0 || nl >= close || text.Substring(e, nl - e).Trim().Length > 0) break;
                        len += nl + 1 - e; e = nl + 1;
                    }
                ch.Add(rm.Item1, len, "");
            }
            int removed = lines.Count(l => !(l.Item3 == "ctor" && hasOtherCtor));
            ch.Message = L.F("{0} を struct にしました{1}", cls.Name, removed > 0 ? L.F(" (デフォルトのコンストラクター・デストラクターを {0} 個消しました)", removed) : "");
            return ch;
        }
    }
}
