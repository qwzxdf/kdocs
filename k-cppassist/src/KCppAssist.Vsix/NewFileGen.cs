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
            public bool NamespaceComment = false;       // 「}  // namespace X」
            public string Eol = "\r\n";
            // VS の「クラスの追加」が作ったファイルを書き直すときに、元の中身を引き継ぐ(null ならふつうのひな形)
            public string ClassHead;                    // 「class Foo : public Bar」。null ならファイル名から決める
            public List<string> Members;                // public: の下に置く宣言(「Foo();」など)
            public List<string> Includes;               // #pragma once / cpp の先頭に置く #include の行
            public List<string> Bodies;                 // cpp の namespace の中に置く定義(「Foo::Foo()\n{\n}」など)
            public bool CtorDefault;                    // class の public: に「Foo() = default;」「~Foo() = default;」を書く(Members が空のとき)
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
            if (o.Includes != null && o.Includes.Count > 0)
            {
                foreach (string inc in o.Includes) sb.Append(inc).Append(eol);
                sb.Append(eol);
            }
            string ind = o.IndentInNamespace && o.Namespace.Length > 0 ? o.Indent : "";
            if (o.Namespace.Length > 0) sb.Append("namespace ").Append(o.Namespace).Append(" {").Append(eol).Append(eol);
            if (o.MakeClass)
            {
                string head = o.ClassHead ?? ((o.IsStruct ? "struct " : "class ") + ClassName(stem, o.Naming));
                bool isStruct = head.StartsWith("struct", StringComparison.Ordinal);
                sb.Append(ind).Append(head).Append(" {").Append(eol);
                if (!isStruct) sb.Append(ind).Append("public:").Append(eol);
                var members = o.Members;
                if ((members == null || members.Count == 0) && o.CtorDefault && !isStruct)
                {
                    // クラス名は、head の最後の識別子(「class Foo : public Bar」なら Foo)
                    var hm = Regex.Match(head, @"(?:class|struct)\s+(?:[A-Za-z_]\w*\s+)*?([A-Za-z_]\w*)\s*(?:final\s*)?(?::|$)");
                    string cn = hm.Success ? hm.Groups[1].Value : ClassName(stem, o.Naming);
                    members = new List<string> { cn + "() = default;", "~" + cn + "() = default;" };
                }
                if (members != null && members.Count > 0)
                {
                    foreach (string mem in members) sb.Append(ind).Append(o.Indent).Append(mem).Append(eol);
                    caret = sb.Length - eol.Length;                  // 最後の宣言の行末
                }
                else
                {
                    caret = sb.Length + ind.Length + o.Indent.Length;    // カーソルを置く行(クラスの中の空行)
                    sb.Append(ind).Append(o.Indent).Append(eol);
                }
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
            if (o.Includes != null && o.Includes.Count > 0)
            {
                foreach (string inc in o.Includes) sb.Append(inc).Append(eol);
                sb.Append(eol);
            }
            else if (headerFile != null) sb.Append("#include \"").Append(headerFile).Append('"').Append(eol).Append(eol);
            string body = o.Bodies != null && o.Bodies.Count > 0 ? string.Join(eol + eol, o.Bodies.Select(b => b.Replace("\r\n", "\n").Replace("\n", eol))) : null;
            if (o.Namespace.Length > 0)
            {
                sb.Append("namespace ").Append(o.Namespace).Append(" {").Append(eol).Append(eol);
                if (body != null) sb.Append(body).Append(eol);
                sb.Append(eol);
                sb.Append("}").Append(o.NamespaceComment ? "  // namespace " + o.Namespace : "").Append(eol);
            }
            else if (body != null) sb.Append(body).Append(eol);
            return sb.ToString();
        }

        // ---- VS の「クラスの追加」が作ったファイル ----

        private static readonly Regex WizardHeaderRx = new Regex(
            @"^\s*#\s*pragma\s+once\s*((?:#\s*include[^\r\n]*\s*)*)((?:class|struct)\s+([A-Za-z_]\w*)(?:\s*:\s*[^{;]+?)?)\s*\{\s*(?:public\s*:\s*)?((?:(?:virtual\s+)?~?\3\s*\(\s*\)\s*(?:override\s*)?;\s*)*)\}\s*;\s*$");

        private static readonly Regex WizardSourceRx = new Regex(
            @"^\s*((?:#\s*include[^\r\n]*\s*)+)((?:[A-Za-z_]\w*::~?[A-Za-z_]\w*\s*\(\s*\)\s*\{\s*\}\s*)*)$");

        /// <summary>
        /// VS の「クラスの追加」が作ったヘッダー(#pragma once と、空のクラスか、コンストラクター・デストラクターの宣言だけ)なら true。
        /// head に「class Foo : public Bar」、members に宣言、includes に #include の行を返す。手で書き足したものは、false(触らない)。
        /// </summary>
        public static bool ParseWizardHeader(string text, out string head, out List<string> members, out List<string> includes)
        {
            head = null; members = new List<string>(); includes = new List<string>();
            var m = WizardHeaderRx.Match(text ?? "");
            if (!m.Success) return false;
            head = Regex.Replace(m.Groups[2].Value, @"\s+", " ").Trim();
            foreach (string l in m.Groups[1].Value.Split('\n')) if (l.Trim().Length > 0) includes.Add(l.Trim());
            foreach (Match d in Regex.Matches(m.Groups[4].Value, @"[^;]+;")) members.Add(Regex.Replace(d.Value, @"\s+", " ").Trim().Replace(" (", "(").Replace("( ", "(").Replace(" )", ")"));
            return true;
        }

        /// <summary>
        /// VS の「クラスの追加」が作った cpp(#include と、空のコンストラクター・デストラクターの定義だけ)なら true。
        /// includes に #include の行、bodies に定義(namespace は付けない形)を返す。
        /// </summary>
        public static bool ParseWizardSource(string text, out List<string> includes, out List<string> bodies)
        {
            includes = new List<string>(); bodies = new List<string>();
            var m = WizardSourceRx.Match(text ?? "");
            if (!m.Success) return false;
            foreach (string l in m.Groups[1].Value.Split('\n')) if (l.Trim().Length > 0) includes.Add(l.Trim());
            foreach (Match d in Regex.Matches(m.Groups[2].Value, @"([A-Za-z_]\w*::~?[A-Za-z_]\w*)\s*\(\s*\)"))
                bodies.Add(d.Groups[1].Value + "()\n{\n}");
            return true;
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
