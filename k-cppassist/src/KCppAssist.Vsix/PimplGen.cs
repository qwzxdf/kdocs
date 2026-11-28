using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// クラスを pimpl にする。private のデータ メンバーを cpp の「struct Foo::Impl」に移し、ヘッダーには std::unique_ptr&lt;Impl&gt; impl_ だけを残す。
    /// cpp の Foo:: の関数の本体では、移したメンバーを impl_-&gt;名前 に書き換える。VS に依存しない。
    /// ヘッダーに本体のある関数が、移すメンバーを使っているときは、作らない(ヘッダーの中では Impl が不完全な型なので、impl_-&gt; と書けない)。
    /// </summary>
    internal static class PimplGen
    {
        public sealed class Result
        {
            public string Header;
            public string Cpp;
            public List<string> Moved = new List<string>();     // 移したメンバーの名前
        }

        public static Result Make(string header, string cpp, int caret, string eol, out string why)
        {
            why = null;
            var cls = MemberScan.At(header, caret);
            if (cls == null) { why = L.T("カーソルが、class / struct の中にありません"); return null; }
            string c = cls.Name;
            string hm = CppText.Mask(header);
            string body0 = hm.Substring(cls.Scope.Open, cls.Scope.Close - cls.Scope.Open);
            if (Regex.IsMatch(body0, @"\bstruct\s+Impl\s*;") || Regex.IsMatch(body0, @"\bimpl_\b")) { why = L.F("{0} は、すでに pimpl です", c); return null; }

            // 移すのは private のデータ メンバー(protected は派生クラスが使うかもしれないので残す)
            var moved = cls.Members.Where(m => m.Access == "private").ToList();
            if (moved.Count == 0) { why = L.F("{0} に、private のデータ メンバーがありません", c); return null; }
            var names = moved.Select(m => m.Name).ToList();
            var nameRx = new Regex(@"(?<![\w.]|->|::)\b(?:" + string.Join("|", names.Select(Regex.Escape)) + @")\b");

            // ヘッダーに本体を書いた関数が、移すメンバーを使っていないか
            var bad = new List<string>();
            foreach (var f in FunctionScan.Scan(header).Where(s => s.HasBody && s.InClass && s.Class == c && s.Open > cls.Scope.Open && s.End < cls.Scope.Close))
            {
                int from = f.InitStart >= 0 ? f.InitStart : f.BodyOpen;
                if (from < 0) continue;
                if (nameRx.IsMatch(hm.Substring(from, f.End - from + 1))) bad.Add(f.Name);
            }
            if (bad.Count > 0)
            {
                why = L.F("ヘッダーに本体のある関数 ({0}) が、移すメンバーを使っています。先に「実装を cpp に移す」で cpp に移してください", string.Join(", ", bad.Distinct()));
                return null;
            }
            foreach (var m in moved)
                if (m.Type.EndsWith("&") || Regex.IsMatch(m.Type, @"^const\b") && cpp != null && Regex.IsMatch(CppText.Mask(cpp), @"\b" + Regex.Escape(c) + @"\s*::\s*" + Regex.Escape(c) + @"\s*\([^)]*\)\s*:[^{]*\b" + Regex.Escape(m.Name) + @"\s*[({]"))
                { why = L.F("{0} は参照か const で、コンストラクターの初期化子リストで決めています。pimpl にすると Impl の中で決める必要があるので、手で移してください", m.Name); return null; }

            // ---- ヘッダー ----
            // 移すメンバーの文(1 行に 1 つ)を消し、最初の行の場所に、struct Impl; と impl_ を置く
            var stmts = moved.GroupBy(m => m.Start).Select(g => g.First()).OrderBy(m => m.Start).ToList();
            var lines = new List<Tuple<int, int>>();            // 消す行(頭、次の行の頭)
            var implLines = new List<string>();                 // Impl の中に書く文
            foreach (var m in stmts)
            {
                int ls = MemberScan.LineStart(header, m.Start), le = MemberScan.LineEnd(header, m.End);
                string rest = (header.Substring(ls, m.Start - ls) + header.Substring(m.End + 1, le - m.End - 1)).Trim();
                if (rest.Length > 0 && !rest.StartsWith("//")) { why = L.F("{0} の行に、ほかのものも書いてあります。1 行 1 メンバーにしてください", m.Name); return null; }
                int next = le < header.Length && header[le] == '\r' ? le + 1 : le;
                if (next < header.Length && header[next] == '\n') next++;
                lines.Add(Tuple.Create(ls, next));
                implLines.Add(header.Substring(m.Start, le - m.Start).TrimEnd());
            }
            string indent = MemberScan.Indent(header, stmts[0].Start);
            string h = header;
            for (int i = lines.Count - 1; i >= 0; i--)
            {
                string put = i == 0 ? indent + "struct Impl;" + eol + indent + "std::unique_ptr<Impl> impl_;" + eol : "";
                h = h.Substring(0, lines[i].Item1) + put + h.Substring(lines[i].Item2);
            }
            var inc = IncludeEditor.Plan(h, "<memory>", null, eol);
            if (inc != null) h = h.Substring(0, inc.Position) + inc.Text + h.Substring(inc.Position);

            // 引数のないコンストラクターがなく、ほかのコンストラクターもないときは、宣言を足す(暗黙のコンストラクターでは impl_ が空のまま)
            var cls2 = Scopes.Parse(h).Where(s => s.IsClass && s.Name == c).OrderBy(s => Math.Abs(s.Open - cls.Scope.Open)).FirstOrDefault();
            if (cls2 == null) { why = L.T("書き換えたあとのクラスを読み直せませんでした"); return null; }
            var info2 = MemberScan.Of(h, cls2);
            bool hasDefaultCtor = MemberScan.HasFunction(info2, @"(?<![~\w])" + Regex.Escape(c) + @"\s*\(\s*(?:void\s*)?\)");
            if (!hasDefaultCtor && !info2.HasUserCtor)
            {
                var add = DefinitionGen.PlanPublicMember(h, cls2.Open, cls2.IsStruct, c + "();", eol);
                if (add != null) h = h.Substring(0, add.Position) + add.Text + h.Substring(add.Position);
            }
            // デストラクター・ムーブは、Impl が完全な型になる cpp に置く(unique_ptr の決まり)
            List<string> specials;
            h = ForwardDecl.MoveSpecialsOut(h, new[] { "Impl" }, eol, out specials);

            // ---- cpp ----
            string cppText = cpp ?? "";
            string unit = CppText.IndentUnit(cppText, header);
            // 既存の Foo:: の定義の中で、移したメンバーを impl_-> にする(後ろの定義から)
            var defs = FunctionScan.Scan(cppText).Where(s => s.HasBody && !s.InClass && s.Class == c).OrderByDescending(s => s.PrefixStart).ToList();
            string ct = cppText;
            foreach (var d in defs)
            {
                bool isCtor = d.Name == c;
                bool isMove = isCtor && Regex.IsMatch(d.Inner(ct), @"&&");
                bool isCopy = isCtor && !isMove && Regex.IsMatch(d.Inner(ct), @"^\s*const\s+" + Regex.Escape(c) + @"\s*&");
                // 本体
                string bodyText = ct.Substring(d.BodyOpen, d.End - d.BodyOpen + 1);
                string newBody = RewriteUses(bodyText, CppText.Mask(bodyText), names);
                var assigns = new List<string>();
                string init = null;
                if (isCtor && !isMove)
                {
                    // 初期化子リストから、移したメンバーを外して、本体の先頭の代入にする
                    var items = new List<string>();
                    if (d.InitStart >= 0)
                    {
                        string list = ct.Substring(d.InitStart + 1, d.BodyOpen - d.InitStart - 1);
                        foreach (string it in SplitTop(list))
                        {
                            string t = it.Trim();
                            var im = Regex.Match(t, @"^([A-Za-z_]\w*)\s*([({])([\s\S]*)[)}]$");
                            if (im.Success && names.Contains(im.Groups[1].Value))
                            {
                                string val = RewriteUses(im.Groups[3].Value, CppText.Mask(im.Groups[3].Value), names);
                                assigns.Add("impl_->" + im.Groups[1].Value + " = " + (im.Groups[2].Value == "{" ? "{" + val + "}" : val) + ";");
                            }
                            else if (t.Length > 0) items.Add(RewriteUses(t, CppText.Mask(t), names));
                        }
                    }
                    items.Insert(0, isCopy ? "impl_(std::make_unique<Impl>(*other.impl_))" : "impl_(std::make_unique<Impl>())");
                    init = " : " + string.Join(", ", items);
                    if (isCopy)
                    {
                        // コピー コンストラクターの引数名(なければ other を付ける)
                        var pm = Regex.Match(d.Inner(ct), @"&\s*([A-Za-z_]\w*)\s*$");
                        if (pm.Success) init = init.Replace("*other.impl_", "*" + pm.Groups[1].Value + ".impl_");
                    }
                }
                if (assigns.Count > 0)
                {
                    int br = newBody.IndexOf('{');
                    newBody = newBody.Substring(0, br + 1) + eol + string.Concat(assigns.Select(a => unit + a + eol)) + newBody.Substring(br + 1).TrimStart('\r', '\n');
                }
                // 「)」から本体の「{」まで。初期化子リストを作り直すときは「) : impl_(…), …」+ 改行 + 「{」にする
                int headEnd = d.InitStart >= 0 ? d.InitStart : d.BodyOpen;
                string head = ct.Substring(d.Close + 1, headEnd - d.Close - 1);
                string between = init != null ? head.TrimEnd() + init + eol : ct.Substring(d.Close + 1, d.BodyOpen - d.Close - 1);
                ct = ct.Substring(0, d.Close + 1) + between + newBody + ct.Substring(d.End + 1);
            }

            // struct Foo::Impl を、最初の Foo:: の定義の前(なければ namespace の枠の中か末尾)に置く
            var implText = new StringBuilder();
            implText.Append("struct ").Append(c).Append("::Impl {").Append(eol);
            foreach (string l in implLines) implText.Append(unit).Append(l.Trim()).Append(eol);
            implText.Append("};").Append(eol);
            var firstDef = FunctionScan.Scan(ct).Where(s => s.HasBody && !s.InClass && s.Class == c).OrderBy(s => s.PrefixStart).FirstOrDefault();
            if (firstDef != null)
            {
                int at = MemberScan.LineStart(ct, firstDef.NameStart);      // 名前の行の頭(PrefixStart は namespace の行まで戻ることがある)
                ct = ct.Substring(0, at) + implText + eol + ct.Substring(at);
            }
            else
            {
                // 定義がない: 宣言から作る雛形と同じ置き場所(namespace の枠の中)を使う
                var probe = FunctionScan.Scan(h).FirstOrDefault(s => !s.HasBody && s.Class == c);
                string w;
                var pe = probe == null ? null : DefinitionGen.PlanDefinition(h, probe, ct, eol, out w);
                if (pe != null)
                {
                    // 雛形の場所に、Impl だけを置く(雛形そのものは、下でまとめて作る)。前の空行は、雛形と同じにする
                    string stub = pe.Text;
                    string lead = stub.Substring(0, stub.Length - stub.TrimStart('\r', '\n').Length);
                    ct = ct.Substring(0, pe.Position) + lead + implText.ToString().TrimEnd('\r', '\n') + ct.Substring(pe.Position);
                }
                else ct = ct + (ct.Length > 0 && !ct.EndsWith("\n") ? eol : "") + eol + implText;
            }

            // ヘッダーで宣言だけにしたもの(コンストラクター・デストラクター・ムーブ)の定義を作る
            foreach (var decl in FunctionScan.Scan(h).Where(s => !s.HasBody && s.Class == c && (s.Name == c || s.Name == "~" + c || s.Name.StartsWith("operator", StringComparison.Ordinal))).ToList())
            {
                string inner = decl.Inner(h);
                bool move = inner.Contains("&&");
                if (decl.Name.StartsWith("operator", StringComparison.Ordinal) && !move) continue;
                if (Regex.IsMatch(h.Substring(decl.Close, decl.End - decl.Close), @"=\s*(?:delete|default)")) continue;
                if (FunctionScan.Scan(ct).Any(s => s.HasBody && s.Name == decl.Name && SyncPlan.Counterpart(s, decl, true) > 0)) continue;     // ~Foo と Foo を取り違えないように、名前もそろえる
                if (decl.Name == c && inner.Trim().Length > 0 && !move) continue;      // 引数のあるコンストラクターは、手で書いたもの
                string w2;
                var de = DefinitionGen.PlanDefinition(h, decl, ct, eol, out w2);
                if (de == null) continue;
                string t = de.Text;
                if (decl.Name == c && !move)
                {
                    // 引数のないコンストラクター: Impl を作る
                    int k = t.LastIndexOf(eol + "{" + eol + "}", StringComparison.Ordinal);
                    if (k >= 0) t = t.Substring(0, k) + eol + unit + ": impl_(std::make_unique<Impl>())" + t.Substring(k);
                }
                else t = ForwardDecl.AsDefaulted(t, eol);
                ct = ct.Substring(0, de.Position) + t + ct.Substring(de.Position);
            }

            // デストラクターとムーブ代入(FunctionScan では見つからないもの)
            string hmask = CppText.Mask(h);
            if (Regex.IsMatch(hmask, @"~\s*" + Regex.Escape(c) + @"\s*\(\s*\)\s*(?:override\s*)?;"))
                ct = ForwardDecl.AddOutOfClassDef(h, ct, c, "dtor", false, eol);
            var ma = Regex.Match(hmask, Regex.Escape(c) + @"\s*&\s*operator\s*=\s*\(\s*" + Regex.Escape(c) + @"\s*&&\s*\w*\s*\)\s*(noexcept)?\s*;");
            if (ma.Success) ct = ForwardDecl.AddOutOfClassDef(h, ct, c, "moveassign", ma.Groups[1].Success, eol);

            return new Result { Header = h, Cpp = ct, Moved = names };
        }

        /// <summary>移したメンバーの名前(単語の単位)を impl_-&gt;名前 にする。「this-&gt;x_」も直す。「obj.x_」「p-&gt;x_」「A::x_」は触らない。</summary>
        public static string RewriteUses(string text, string masked, IList<string> names)
        {
            if (names.Count == 0) return text;
            string alt = string.Join("|", names.Select(Regex.Escape));
            var sb = new StringBuilder(text);
            var hits = new List<Tuple<int, int, string>>();
            foreach (Match m in Regex.Matches(masked, @"\bthis\s*->\s*(" + alt + @")\b"))
                hits.Add(Tuple.Create(m.Index, m.Length, "impl_->" + m.Groups[1].Value));
            foreach (Match m in Regex.Matches(masked, @"(?<![\w.]|->|::)\b(" + alt + @")\b"))
            {
                if (hits.Any(x => m.Index >= x.Item1 && m.Index < x.Item1 + x.Item2)) continue;
                hits.Add(Tuple.Create(m.Index, m.Length, "impl_->" + m.Groups[1].Value));
            }
            foreach (var x in hits.OrderByDescending(x => x.Item1)) { sb.Remove(x.Item1, x.Item2); sb.Insert(x.Item1, x.Item3); }
            return sb.ToString();
        }

        private static List<string> SplitTop(string s)
        {
            var list = new List<string>();
            int depth = 0, start = 0;
            for (int i = 0; i < s.Length; i++)
            {
                char ch = s[i];
                if (ch == '(' || ch == '{' || ch == '[' || ch == '<') depth++;
                else if (ch == ')' || ch == '}' || ch == ']' || ch == '>') depth--;
                else if (ch == ',' && depth == 0) { list.Add(s.Substring(start, i - start)); start = i + 1; }
            }
            list.Add(s.Substring(start));
            return list;
        }
    }
}
