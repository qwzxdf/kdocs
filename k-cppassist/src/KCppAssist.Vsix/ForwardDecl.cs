using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// ヘッダーの #include を、前方宣言に置き換える(cpp 側に #include を移す)。VS に依存しない。
    /// ポインター・参照・shared_ptr / weak_ptr / unique_ptr の中でしか使っていない型だけが対象で、少しでも怪しければ、作らない。
    /// unique_ptr のときは、呼び出し側が MoveSpecialsOut でコンストラクター・デストラクターを cpp に移す。
    /// </summary>
    internal static class ForwardDecl
    {
        public sealed class TypeInfo
        {
            public string Name;
            public string Kind;                         // "class" か "struct"
            public List<string> Namespaces = new List<string>();
        }

        public sealed class Result
        {
            public string NewText;                      // 前方宣言に置き換えたヘッダー
            public string CppToken;                     // cpp に足す #include(「"foo.h"」の形)
            public List<string> Names = new List<string>();
        }

        private static readonly Regex Ptr = new Regex(@"\G\s*(?:const\s+)?[*&]", RegexOptions.Compiled);
        // 「Foo* name」「Foo& name」「shared_ptr<Foo> name」の name(ポインター・参照で持っている名前)
        private static readonly Regex PtrName = new Regex(@"\G\s*(?:const\s+)?[*&]+\s*(?:const\s+)?([A-Za-z_]\w*)", RegexOptions.Compiled);
        private static readonly Regex SmartName = new Regex(@"\G\s*>\s*&?\s*([A-Za-z_]\w*)", RegexOptions.Compiled);
        private static readonly Regex SmartBefore = new Regex(@"(?:shared_ptr|weak_ptr|unique_ptr)\s*<\s*(?:const\s+)?$", RegexOptions.Compiled);

        /// <summary>#include foo.h を前方宣言にできるか。できなければ null で、理由を why に入れる。</summary>
        public static Result Make(string text, IncludeTidy.Item inc, List<TypeInfo> types, ISet<string> otherNames, string eol, out string why)
        {
            why = null;
            string m = CppText.Mask(text);
            string noInc = Regex.Replace(m, @"(?m)^[ \t]*#[^\r\n]*", match => new string(' ', match.Length));
            var used = IncludeTidy.Used(text);

            var usedTypes = types.Where(t => used.Contains(t.Name)).GroupBy(t => t.Name).Select(g => g.First()).ToList();
            if (usedTypes.Count == 0) { why = "このヘッダーの型を、使っていません"; return null; }
            var typeNames = new HashSet<string>(types.Select(t => t.Name));
            foreach (string o in otherNames) if (!typeNames.Contains(o) && used.Contains(o)) { why = "型以外の名前 " + o + " を使っているので、前方宣言にできません"; return null; }

            // 本体({ ... })の範囲(関数の中の使い方は、完全な型が要るかもしれない)
            var bodies = FunctionScan.Scan(text).Where(s => s.HasBody).Select(s => new[] { s.BodyOpen, s.End }).ToList();

            var already = new HashSet<string>(StringComparer.Ordinal);
            foreach (Match x in Regex.Matches(noInc, @"\b(?:class|struct)\s+([A-Za-z_]\w*)\s*;")) already.Add(x.Groups[1].Value);

            var holders = new Dictionary<string, string>(StringComparer.Ordinal);    // ポインター・参照で持っている名前 → 型
            foreach (var t in usedTypes)
            {
                foreach (Match o in Regex.Matches(noInc, @"(?<!\w)" + Regex.Escape(t.Name) + @"(?!\w)"))
                {
                    int line = text.Take(o.Index).Count(c => c == '\n') + 1;
                    string beforeAll = noInc.Substring(0, o.Index);
                    // 「class Foo;」の前方宣言そのもの
                    if (Regex.IsMatch(beforeAll, @"\b(?:class|struct)\s+$") && Regex.IsMatch(noInc.Substring(o.Index + o.Length, Math.Min(20, noInc.Length - o.Index - o.Length)), @"^\s*;")) continue;
                    if (bodies.Any(b => o.Index > b[0] && o.Index < b[1])) { why = t.Name + " を、関数の本体の中で使っています (" + line + " 行目)"; return null; }
                    int after = o.Index + o.Length;
                    if (Ptr.IsMatch(noInc, after))
                    {
                        Match pn = PtrName.Match(noInc, after);
                        if (pn.Success) holders[pn.Groups[1].Value] = t.Name;
                        continue;
                    }
                    string before = beforeAll.Substring(Math.Max(0, beforeAll.Length - 60));
                    before = Regex.Replace(before, @"(?:[A-Za-z_]\w*\s*::\s*)+$", "");     // game::Scene の「game::」は飛ばす
                    if (SmartBefore.IsMatch(before))
                    {
                        var close = Regex.Match(noInc.Substring(after, Math.Min(10, noInc.Length - after)), @"^\s*>");
                        if (close.Success)
                        {
                            Match sn = SmartName.Match(noInc, after);
                            if (sn.Success) holders[sn.Groups[1].Value] = t.Name;
                            continue;
                        }
                    }
                    why = t.Name + " を、ポインター・参照以外で使っています (" + line + " 行目)";
                    return null;
                }
            }

            // インライン関数の本体が、ポインター・参照の先を使っている(target_->Move() など)と、型名が書かれていなくても完全な型が要る
            foreach (var h in holders)
                foreach (var b in bodies)
                {
                    string body = noInc.Substring(b[0], Math.Max(0, b[1] - b[0]));
                    Match use = Regex.Match(body, @"(?<![\w.>])" + Regex.Escape(h.Key) + @"\s*(?:->|\.(?!\.))|\*\s*" + Regex.Escape(h.Key) + @"\b");
                    if (!use.Success) continue;
                    int line = text.Take(b[0] + use.Index).Count(c => c == '\n') + 1;
                    why = h.Key + " (" + h.Value + ") の中身を、関数の本体で使っています (" + line + " 行目)。前方宣言では型の中身が見えません";
                    return null;
                }

            // 前方宣言のブロックを作る(名前空間ごとにまとめる)
            var need = usedTypes.Where(t => !already.Contains(t.Name)).ToList();
            var sb = new StringBuilder();
            foreach (var g in need.GroupBy(t => string.Join("::", t.Namespaces)))
            {
                var ns = g.First().Namespaces;
                if (ns.Count > 0) sb.Append("namespace ").Append(string.Join("::", ns)).Append(" {").Append(eol);
                foreach (var t in g) sb.Append(t.Kind).Append(' ').Append(t.Name).Append(';').Append(eol);
                if (ns.Count > 0) sb.Append("}  // namespace ").Append(string.Join("::", ns)).Append(eol);
            }

            // #include の行を消して、残りの #include の最後のあと(なければ #pragma once のあと、なければ先頭)に置く
            string removed = text.Substring(0, inc.Start) + text.Substring(inc.End);
            if (sb.Length > 0)
            {
                int at = 0;
                var rest = IncludeTidy.Parse(removed).Where(i => i.Depth == 0).ToList();
                if (rest.Count > 0) at = rest[rest.Count - 1].End;
                else
                {
                    var pragma = Regex.Match(removed, @"(?m)^[ \t]*#[ \t]*pragma[ \t]+once[^\r\n]*\r?\n?");
                    if (pragma.Success) at = pragma.Index + pragma.Length;
                }
                string block = sb.ToString();
                bool needBlankBefore = at > 0;
                bool nextIsBlank = at >= removed.Length || removed.Substring(at).StartsWith(eol) || removed.Substring(at).StartsWith("\n");
                string ins = (needBlankBefore ? eol : "") + block + (nextIsBlank ? "" : eol);
                removed = removed.Substring(0, at) + ins + removed.Substring(at);
            }
            return new Result { NewText = removed, CppToken = inc.Token, Names = usedTypes.Select(t => t.Name).ToList() };
        }

        /// <summary>ヘッダーの文字から、前方宣言に使える型(class / struct の名前と、囲む namespace)を集める。</summary>
        public static List<TypeInfo> Types(string headerText)
        {
            var list = new List<TypeInfo>();
            foreach (var s in Scopes.Parse(headerText))
            {
                if (!s.IsClass) continue;
                var chain = s.Chain();
                if (chain.Count == 0) continue;
                // 入れ子のクラス(クラスの中のクラス)は、前方宣言できないので除く
                if (s.Parent != null && s.Parent.IsClass) continue;
                // template のクラスは、template<...> を付けた前方宣言が要るので、対象にしない
                if (Regex.IsMatch(CppText.Mask(headerText), @"template\s*<[^<>]*(?:<[^<>]*>[^<>]*)*>\s*(?:class|struct)\s+" + Regex.Escape(s.Name) + @"\b")) continue;
                var t = new TypeInfo { Name = s.Name, Kind = s.IsStruct ? "struct" : "class" };
                foreach (var p in chain.Take(chain.Count - 1)) t.Namespaces.Add(p);
                list.Add(t);
            }
            return list;
        }
            /// <summary>
        /// 前方宣言にした型(names)を std::unique_ptr で持つクラスの、コンストラクター・デストラクター・ムーブを、ヘッダーの中では宣言だけにする。
        /// unique_ptr のデストラクターは、中身の型の完全な定義を要るので、ヘッダーに「~Foo() = default;」があると、前方宣言だけではコンパイルできない
        /// (コンストラクターとムーブも、途中で例外が出たときや代入の前に、中身を消す処理を持つので同じ)。
        /// 「= default;」か「{}」のものだけを宣言にする(処理を書いたものは触らない)。デストラクターがなければ「~Foo();」を足す。
        /// moved に、宣言にしたもの(「Foo::~Foo」など)を入れる。直す所がなければ text をそのまま返す。
        /// </summary>
        public static string MoveSpecialsOut(string text, IEnumerable<string> names, string eol, out List<string> moved)
        {
            moved = new List<string>();
            var set = new HashSet<string>(names.Select(n => n.Substring(n.LastIndexOf(':') + 1)), StringComparer.Ordinal);
            if (set.Count == 0) return text;
            string alt = string.Join("|", set.Select(Regex.Escape));
            var uptr = new Regex(@"\b(?:std::)?unique_ptr\s*<\s*(?:const\s+)?(?:[A-Za-z_]\w*::)*(?:" + alt + @")\s*[,>]");
            // 後ろのクラスから直す(前の位置がずれないように)
            foreach (var s in Scopes.Parse(text).Where(x => x.IsClass && !string.IsNullOrEmpty(x.Name)).OrderByDescending(x => x.Open).ToList())
            {
                string m = CppText.Mask(text);
                if (s.Close >= m.Length) continue;
                var info = MemberScan.Of(text, s);
                if (!info.Members.Any(x => uptr.IsMatch(x.Type))) continue;
                string c = Regex.Escape(s.Name);
                var rules = new List<KeyValuePair<Regex, Func<Match, string>>>
                {
                    new KeyValuePair<Regex, Func<Match, string>>(new Regex(@"^([ \t]*)(explicit\s+)?" + c + @"\s*\(\s*\)\s*(noexcept\s*)?(?:=\s*default\s*;|\{\s*\})[ \t]*$"),
                        x => x.Groups[1].Value + x.Groups[2].Value + s.Name + "()" + (x.Groups[3].Success ? " noexcept" : "") + ";"),
                    new KeyValuePair<Regex, Func<Match, string>>(new Regex(@"^([ \t]*)(virtual\s+)?~" + c + @"\s*\(\s*\)\s*(noexcept\s*)?(override\s*)?(?:=\s*default\s*;|\{\s*\})[ \t]*$"),
                        x => x.Groups[1].Value + x.Groups[2].Value + "~" + s.Name + "()" + (x.Groups[4].Success ? " override" : "") + ";"),
                    new KeyValuePair<Regex, Func<Match, string>>(new Regex(@"^([ \t]*)" + c + @"\s*\(\s*" + c + @"\s*&&\s*\w*\s*\)\s*(noexcept\s*)?=\s*default\s*;[ \t]*$"),
                        x => x.Groups[1].Value + s.Name + "(" + s.Name + "&&)" + (x.Groups[2].Success ? " noexcept" : "") + ";"),
                    new KeyValuePair<Regex, Func<Match, string>>(new Regex(@"^([ \t]*)" + c + @"\s*&\s*operator\s*=\s*\(\s*" + c + @"\s*&&\s*\w*\s*\)\s*(noexcept\s*)?=\s*default\s*;[ \t]*$"),
                        x => x.Groups[1].Value + s.Name + "& operator=(" + s.Name + "&&)" + (x.Groups[2].Success ? " noexcept" : "") + ";"),
                };
                string[] label = { s.Name + "::" + s.Name, s.Name + "::~" + s.Name, s.Name + "::" + s.Name + "(&&)", s.Name + "::operator=(&&)" };
                // クラスの本体の直下の行を、1 行ずつ見る
                var edits = new List<Tuple<int, int, string>>();
                bool hasDtor = false;
                int depth = 0;
                for (int i = s.Open; i < s.Close; i++)
                {
                    char ch = m[i];
                    if (ch == '{') depth++;
                    else if (ch == '}') depth--;
                    if (!(ch == '\n' && depth == 1)) continue;
                    int ls = i + 1, le = ls;
                    while (le < s.Close && text[le] != '\n' && text[le] != '\r') le++;
                    string ml = m.Substring(ls, le - ls);
                    if (Regex.IsMatch(ml, @"~" + c + @"\s*\(")) hasDtor = true;
                    for (int r = 0; r < rules.Count; r++)
                    {
                        var hit = rules[r].Key.Match(ml);
                        if (!hit.Success) continue;
                        edits.Add(Tuple.Create(ls, le - ls, rules[r].Value(hit)));
                        moved.Add(label[r]);
                        break;
                    }
                }
                string before = text;
                foreach (var e in edits.OrderByDescending(e => e.Item1)) text = text.Substring(0, e.Item1) + e.Item3 + text.Substring(e.Item1 + e.Item2);
                if (!hasDtor)
                {
                    var sc = Scopes.Parse(text).FirstOrDefault(x => x.IsClass && x.Open == s.Open);
                    var add = sc == null ? null : DefinitionGen.PlanPublicMember(text, sc.Open, sc.IsStruct, "~" + s.Name + "();", eol);
                    if (add != null) { text = text.Substring(0, add.Position) + add.Text + text.Substring(add.Position); moved.Add(label[1]); }
                }
            }
            return text;
        }

        /// <summary>DefinitionGen.PlanDefinition の「{ }」の本体を、「= default;」にする(コンストラクター・デストラクター・ムーブは、空の本体だと中身を移さないため)。</summary>
        public static string AsDefaulted(string stub, string eol)
        {
            int k = stub.LastIndexOf(eol + "{" + eol + "}", StringComparison.Ordinal);
            if (k < 0) return stub;
            return stub.Substring(0, k) + " = default;" + stub.Substring(k + (eol + "{" + eol + "}").Length);
        }

    }
}
