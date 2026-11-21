using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// 新しく作った(空の)ヘッダーと cpp に、決まった形を書く。VS に依存しない。
    /// 名前空間と字下げは、ソリューションの既存のヘッダーで一番多いものを使う(設定で固定もできる)。
    /// クラス名は、ファイル名から、設定の規則で決める。
    /// </summary>
    internal static class NewFileGen
    {
        /// <summary>ファイル名からクラス名を決める規則。</summary>
        public enum Naming { SameAsFile, Pascal, Snake, Camel }

        public enum Guard { PragmaOnce, IncludeGuard }

        public sealed class Options
        {
            public Naming Naming = Naming.SameAsFile;
            public Guard Guard = Guard.PragmaOnce;
            public bool MakeClass = true;
            public bool IsStruct;                       // class ではなく struct にする
            public string Namespace = "";               // 空なら namespace を書かない。「A::B」も可
            public string Indent = "\t";                // クラスの中の 1 段の字下げ
            public bool IndentInNamespace;              // namespace の中を字下げする
            public bool NamespaceComment = true;        // 「}  // namespace X」
            public string Eol = "\r\n";
        }

        // ---- 名前 ----

        /// <summary>ファイル名(拡張子なし)から、規則に合わせたクラス名。識別子にできない文字は「_」にする。</summary>
        public static string ClassName(string stem, Naming rule)
        {
            if (string.IsNullOrEmpty(stem)) return "";
            if (rule == Naming.SameAsFile) return Sanitize(stem);
            var words = Words(stem);
            if (words.Count == 0) return Sanitize(stem);
            switch (rule)
            {
                case Naming.Snake: return string.Join("_", words.Select(w => w.ToLowerInvariant()));
                case Naming.Camel: return words[0].ToLowerInvariant() + string.Concat(words.Skip(1).Select(Cap));
                default: return string.Concat(words.Select(Cap));
            }
        }

        private static string Cap(string w) { return w.Length == 0 ? w : char.ToUpperInvariant(w[0]) + w.Substring(1).ToLowerInvariant(); }

        /// <summary>「game_object」「GameObject」「game-object」を、単語(game, object)に分ける。「HTTPServer」は HTTP と Server。</summary>
        public static List<string> Words(string s)
        {
            var list = new List<string>();
            foreach (string part in Regex.Split(s, @"[^A-Za-z0-9]+"))
            {
                if (part.Length == 0) continue;
                foreach (string w in Regex.Split(part, @"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])"))
                    if (w.Length > 0) list.Add(w);
            }
            return list;
        }

        private static string Sanitize(string s)
        {
            string r = Regex.Replace(s, @"[^A-Za-z0-9_]", "_");
            return char.IsDigit(r[0]) ? "_" + r : r;
        }

        // ---- 既存のヘッダーから、標準の名前空間と字下げを調べる ----

        /// <summary>行頭の「namespace X {」で一番多い名前。1 つもなければ空。同数なら短いほう。</summary>
        public static string DetectNamespace(IEnumerable<string> texts)
        {
            var count = new Dictionary<string, int>();
            foreach (string t in texts)
            {
                string m = CppText.Mask(t);
                foreach (Match x in Regex.Matches(m, @"(?m)^namespace\s+([A-Za-z_]\w*(?:\s*::\s*[A-Za-z_]\w*)*)\s*\{"))
                {
                    string name = Regex.Replace(x.Groups[1].Value, @"\s+", "");
                    if (name == "std") continue;
                    int c;
                    count.TryGetValue(name, out c);
                    count[name] = c + 1;
                }
            }
            if (count.Count == 0) return "";
            return count.OrderByDescending(kv => kv.Value).ThenBy(kv => kv.Key.Length).ThenBy(kv => kv.Key, StringComparer.Ordinal).First().Key;
        }

        /// <summary>クラスの中の字下げに、タブと空白のどちらが多いか。空白なら、その幅(2 か 4)。判断できなければ null。</summary>
        public static string DetectIndent(IEnumerable<string> texts)
        {
            int tab = 0, sp2 = 0, sp4 = 0;
            foreach (string t in texts)
                foreach (string line in t.Split('\n'))
                {
                    if (line.Length == 0) continue;
                    if (line[0] == '\t') { tab++; continue; }
                    int n = 0;
                    while (n < line.Length && line[n] == ' ') n++;
                    if (n == 0 || n == line.Length) continue;
                    if (n % 4 == 0) sp4++;
                    else if (n % 2 == 0) sp2++;
                }
            if (tab + sp2 + sp4 < 5) return null;
            if (tab >= sp2 + sp4) return "\t";
            return sp2 > sp4 ? "  " : "    ";
        }

        // ---- 中身 ----

        /// <summary>空のヘッダーに書く文字。stem はファイル名(拡張子なし)。</summary>
        public static string Header(string stem, Options o, out int caret)
        {
            caret = 0;
            string eol = o.Eol;
            var sb = new StringBuilder();
            string guard = GuardName(stem, o.Namespace);
            if (o.Guard == Guard.PragmaOnce) sb.Append("#pragma once").Append(eol);
            else sb.Append("#ifndef ").Append(guard).Append(eol).Append("#define ").Append(guard).Append(eol);
            sb.Append(eol);
            string ind = o.IndentInNamespace && o.Namespace.Length > 0 ? o.Indent : "";
            if (o.Namespace.Length > 0) sb.Append("namespace ").Append(o.Namespace).Append(" {").Append(eol).Append(eol);
            if (o.MakeClass)
            {
                string cls = ClassName(stem, o.Naming);
                sb.Append(ind).Append(o.IsStruct ? "struct " : "class ").Append(cls).Append(" {").Append(eol);
                if (!o.IsStruct) sb.Append(ind).Append("public:").Append(eol);
                caret = sb.Length + ind.Length + o.Indent.Length;    // カーソルを置く行(クラスの中の空行)
                sb.Append(ind).Append(o.Indent).Append(eol);
                sb.Append(ind).Append("};").Append(eol);
                sb.Append(eol);
            }
            else { caret = sb.Length + ind.Length; sb.Append(ind).Append(eol); }
            if (o.Namespace.Length > 0) sb.Append("}").Append(o.NamespaceComment ? "  // namespace " + o.Namespace : "").Append(eol);
            if (o.Guard == Guard.IncludeGuard) sb.Append(eol).Append("#endif  // ").Append(guard).Append(eol);
            return sb.ToString();
        }

        /// <summary>空の cpp に書く文字。headerFile はインクルードするヘッダーのファイル名(なければ null)。</summary>
        public static string Source(string headerFile, Options o)
        {
            string eol = o.Eol;
            var sb = new StringBuilder();
            if (headerFile != null) sb.Append("#include \"").Append(headerFile).Append('"').Append(eol).Append(eol);
            if (o.Namespace.Length > 0)
            {
                sb.Append("namespace ").Append(o.Namespace).Append(" {").Append(eol).Append(eol);
                sb.Append(eol);
                sb.Append("}").Append(o.NamespaceComment ? "  // namespace " + o.Namespace : "").Append(eol);
            }
            return sb.ToString();
        }

        /// <summary>インクルード ガードのマクロ名。「Prest::Foo」と「game_object」から PREST_GAME_OBJECT_H_。</summary>
        public static string GuardName(string stem, string ns)
        {
            string s = (ns.Length > 0 ? ns + "_" : "") + stem;
            s = Regex.Replace(s, @"[^A-Za-z0-9]+", "_").Trim('_').ToUpperInvariant();
            return s + "_H_";
        }

        /// <summary>空(空白と改行だけ)か。</summary>
        public static bool IsBlank(string text)
        {
            // VS の「新しい項目」のひな形(#pragma once だけ)も、空とみなして、中身を入れ直す
            return Regex.Replace(text, @"^\s*#\s*pragma\s+once\s*$", "", RegexOptions.Multiline).Trim().Length == 0;
        }
    }
}
