using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// ヘッダーの #include を、前方宣言に置き換える(cpp 側に #include を移す)。VS に依存しない。
    /// ポインター・参照・shared_ptr / weak_ptr の中でしか使っていない型だけが対象で、少しでも怪しければ、作らない。
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
        private static readonly Regex SmartBefore = new Regex(@"(?:shared_ptr|weak_ptr)\s*<\s*(?:const\s+)?$", RegexOptions.Compiled);

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
                    if (Ptr.IsMatch(noInc, after)) continue;
                    string before = beforeAll.Substring(Math.Max(0, beforeAll.Length - 60));
                    before = Regex.Replace(before, @"(?:[A-Za-z_]\w*\s*::\s*)+$", "");     // game::Scene の「game::」は飛ばす
                    if (SmartBefore.IsMatch(before))
                    {
                        var close = Regex.Match(noInc.Substring(after, Math.Min(10, noInc.Length - after)), @"^\s*>");
                        if (close.Success) continue;
                    }
                    why = t.Name + " を、ポインター・参照以外で使っています (" + line + " 行目)";
                    return null;
                }
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
    }
}
