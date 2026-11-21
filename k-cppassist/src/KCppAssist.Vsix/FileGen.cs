using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// ファイルをまたぐ生成の計算。VS に依存しない。
    /// クラスを自分の名前のファイル(.h / .cpp)へ移す、宣言だけの関数を探す。
    /// </summary>
    internal static class FileGen
    {
        public sealed class Extract
        {
            public string ClassName;
            public string NewHeader;                                  // 新しい .h の中身
            public Refactor.Change OldHeader = new Refactor.Change(); // 元のヘッダーの編集(クラスを消して #include を足す)
        }

        private static readonly Regex IncludeLine = new Regex(@"^[ \t]*#[ \t]*include[^\r\n]*", RegexOptions.Multiline);

        /// <summary>
        /// caret のクラスを、新しいヘッダー(クラス名.h)へ移す計算。元のヘッダーの #include は、そのまま新しいヘッダーへ写す
        /// (使っていないものは、あとで「#include を整理」で消す)。template のクラスと、入れ子のクラスは移さない。
        /// </summary>
        public static Extract ExtractClass(string text, int caret, string headerFileName, string eol, out string why)
        {
            why = null;
            var cls = MemberScan.At(text, caret);
            if (cls == null) { why = L.T("カーソルが、class / struct の中にありません"); return null; }
            if (cls.Scope.Parent != null && cls.Scope.Parent.IsClass) { why = L.T("入れ子のクラスは移せません"); return null; }
            string newName = cls.Name + ".h";
            if (string.Equals(headerFileName, newName, StringComparison.OrdinalIgnoreCase)) { why = L.F("このファイルが、すでに {0} です", newName); return null; }
            string m = CppText.Mask(text);
            // クラスの頭(「class」の位置)。直前の template<…> があれば断る
            int head = m.LastIndexOf(cls.IsStruct ? "struct" : "class", cls.Scope.Open, StringComparison.Ordinal);
            while (head > 0 && Regex.IsMatch(m.Substring(Math.Max(0, head - 1), 1), @"\w")) head = m.LastIndexOf(cls.IsStruct ? "struct" : "class", head - 1, StringComparison.Ordinal);
            if (head < 0) { why = L.T("クラスの頭が読めません"); return null; }
            int ls = MemberScan.LineStart(text, head);
            if (Regex.IsMatch(m.Substring(Math.Max(0, ls - 200), ls - Math.Max(0, ls - 200)), @"template\s*<[^;{}]*>\s*$")) { why = L.T("template のクラスは移せません"); return null; }
            // 真上のコメント行も一緒に移す
            int start = ls;
            while (start > 0)
            {
                int prev = MemberScan.LineStart(text, start - 1);
                string pl = text.Substring(prev, start - prev).Trim();
                if (pl.StartsWith("//") || pl.StartsWith("/*") || pl.StartsWith("*")) start = prev; else break;
            }
            int semi = m.IndexOf(';', cls.Scope.Close);
            if (semi < 0) { why = L.T("クラスの「;」が見つかりません"); return null; }
            int end = semi + 1;
            int lineEnd = text.IndexOf('\n', end);
            end = lineEnd < 0 ? text.Length : lineEnd + 1;
            string body = text.Substring(start, end - start).TrimEnd('\r', '\n');

            var sb = new StringBuilder();
            sb.Append("#pragma once").Append(eol).Append(eol);
            var incs = IncludeLine.Matches(text).Cast<Match>().Select(x => x.Value.Trim()).Where(x => !x.Contains("\"" + newName + "\"")).Distinct().ToList();
            foreach (string inc in incs) sb.Append(inc).Append(eol);
            if (incs.Count > 0) sb.Append(eol);
            var ns = cls.Scope.ParentChain();
            string nsName = string.Join("::", ns);
            if (ns.Count > 0) sb.Append("namespace ").Append(nsName).Append(" {").Append(eol).Append(eol);
            sb.Append(body).Append(eol);
            if (ns.Count > 0) sb.Append(eol).Append("}").Append(eol);

            var x2 = new Extract { ClassName = cls.Name, NewHeader = sb.ToString() };
            // 消したあとに空行が 2 つ続かないよう、後ろの空行を 1 つ一緒に消す
            int cut = end;
            bool blankBefore = text.Substring(0, start).EndsWith("\n\n") || text.Substring(0, start).EndsWith("\r\n\r\n");
            if (blankBefore && text.Substring(cut).StartsWith("\r\n")) cut += 2;
            else if (blankBefore && text.Substring(cut).StartsWith("\n")) cut += 1;
            x2.OldHeader.Add(start, cut - start, "");
            Refactor.AddInclude(x2.OldHeader, text, "\"" + newName + "\"", eol);
            x2.OldHeader.Message = cls.Name + " を " + newName + " に移しました";
            return x2;
        }

        /// <summary>cpp の中の「Class::Func」の定義(本体つき)の範囲。真上のコメント行を含み、行の終わりまで。</summary>
        public static List<Tuple<int, int>> DefinitionsOf(string cppText, string className)
        {
            var list = new List<Tuple<int, int>>();
            string m = CppText.Mask(cppText);
            foreach (var s in FunctionScan.Scan(cppText).Where(f => f.HasBody && !f.InClass && f.Class == className))
            {
                // 文の頭は、前の「}」「;」「{」の直後なので、コメントと空白を飛ばした、最初のコードの行から
                int code = s.PrefixStart;
                while (code < s.NameStart && char.IsWhiteSpace(m[code])) code++;
                int start = MemberScan.LineStart(cppText, code);
                while (start > 0)
                {
                    int prev = MemberScan.LineStart(cppText, start - 1);
                    string pl = cppText.Substring(prev, start - prev).Trim();
                    if (pl.StartsWith("//")) start = prev; else break;
                }
                int nl = cppText.IndexOf('\n', s.End);
                int end = nl < 0 ? cppText.Length : nl + 1;
                // 後ろの空行 1 つも一緒に
                if (end < cppText.Length && cppText[end] == '\n') end++;
                else if (end + 1 < cppText.Length && cppText[end] == '\r' && cppText[end + 1] == '\n') end += 2;
                list.Add(Tuple.Create(start, end));
            }
            return list;
        }

        /// <summary>新しい cpp の中身。元の cpp の #include を写し、新しいヘッダーを足す。定義が namespace の中なら同じ namespace で囲む。</summary>
        public static string NewSource(string cppText, string className, List<Tuple<int, int>> defs, string eol)
        {
            var sb = new StringBuilder();
            var incs = IncludeLine.Matches(cppText).Cast<Match>().Select(x => x.Value.Trim()).Distinct().ToList();
            // プリコンパイル済みヘッダーは先頭のまま。その次に、自分のヘッダー
            var pch = incs.Where(i => Regex.IsMatch(i, @"[""<](?:pch|stdafx)\.h[>""]")).ToList();
            foreach (string p in pch) sb.Append(p).Append(eol);
            sb.Append("#include \"").Append(className).Append(".h\"").Append(eol).Append(eol);
            var rest = incs.Where(i => !pch.Contains(i)).ToList();
            foreach (string i in rest) sb.Append(i).Append(eol);
            if (rest.Count > 0) sb.Append(eol);
            var scopes = Scopes.Parse(cppText);
            var ns = defs.Count == 0 ? new List<string>() : Scopes.NamespacesAt(scopes, defs[0].Item1);
            string nsName = string.Join("::", ns);
            if (ns.Count > 0) sb.Append("namespace ").Append(nsName).Append(" {").Append(eol).Append(eol);
            sb.Append(string.Join("", defs.Select(d => cppText.Substring(d.Item1, d.Item2 - d.Item1))).TrimEnd('\r', '\n')).Append(eol);
            if (ns.Count > 0) sb.Append(eol).Append("}").Append(eol);
            return sb.ToString();
        }

        /// <summary>
        /// クラスの本体の中の、定義の要る宣言(本体がなく、= 0 / = default / = delete / friend / static でない変数ではないもの)。
        /// </summary>
        public static List<FunctionScan.Sig> Declarations(string headerText, Scopes.Scope cls)
        {
            string m = CppText.Mask(headerText);
            var list = new List<FunctionScan.Sig>();
            foreach (var s in FunctionScan.Scan(headerText))
            {
                if (s.HasBody || !s.InClass || s.Open < cls.Open || s.Close > cls.Close) continue;
                if (s.Class != cls.Name) continue;
                string tail = m.Substring(s.Close + 1, Math.Max(0, s.End - s.Close - 1));
                if (Regex.IsMatch(tail, @"=\s*(?:0|default|delete)\b")) continue;
                string prefix = m.Substring(s.PrefixStart, s.NameStart - s.PrefixStart);
                if (Regex.IsMatch(prefix, @"\b(?:friend|template|constexpr|consteval)\b") || s.InTemplate) continue;
                list.Add(s);
            }
            return list;
        }
    }
}
