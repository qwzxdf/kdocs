using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>引数のリストを分けて、型だけの形にそろえ、変えた側の変更を相手側のリストに写す。VS に依存しない。</summary>
    internal static class SignatureSync
    {
        private static readonly HashSet<string> Builtins = new HashSet<string>
        {
            "int", "char", "short", "long", "float", "double", "bool", "void", "unsigned", "signed", "wchar_t", "auto", "char8_t", "char16_t", "char32_t",
        };
        private static readonly HashSet<string> Qualifiers = new HashSet<string> { "const", "volatile", "struct", "class", "enum", "typename" };

        /// <summary>
        /// 括弧の中身を、引数ごとに分ける。「」と「void」は引数なし。
        /// 書きかけ(末尾のカンマ、空の引数)のときは null。
        /// </summary>
        public static List<string> SplitParams(string inner)
        {
            var list = new List<string>();
            string t = inner.Trim();
            if (t.Length == 0 || t == "void") return list;
            int depth = 0, start = 0;
            for (int i = 0; i < inner.Length; i++)
            {
                char c = inner[i];
                if (c == '"' || c == '\'')
                {
                    for (i++; i < inner.Length && inner[i] != c; i++) if (inner[i] == '\\') i++;
                    continue;
                }
                if (c == '(' || c == '[' || c == '{') depth++;
                else if (c == ')' || c == ']' || c == '}') depth--;
                else if (c == '<' && i > 0 && (CppText.IsId(inner[i - 1]) || inner[i - 1] == ' ' && i > 1 && CppText.IsId(inner[i - 2]))) depth++;
                else if (c == '>' && depth > 0 && !(i > 0 && inner[i - 1] == '-')) depth--;
                else if (c == ',' && depth == 0)
                {
                    list.Add(inner.Substring(start, i - start).Trim());
                    start = i + 1;
                }
            }
            list.Add(inner.Substring(start).Trim());
            if (list.Any(p => p.Length == 0)) return null;
            return list;
        }

        /// <summary>「int a = 3」を「int a」と既定値「3」に分ける。既定値がなければ def は null。</summary>
        public static string StripDefault(string p, out string def)
        {
            def = null;
            int depth = 0;
            for (int i = 0; i < p.Length; i++)
            {
                char c = p[i];
                if (c == '"' || c == '\'')
                {
                    for (i++; i < p.Length && p[i] != c; i++) if (p[i] == '\\') i++;
                    continue;
                }
                if (c == '(' || c == '[' || c == '{' || c == '<') depth++;
                else if (c == ')' || c == ']' || c == '}' || c == '>') depth--;
                else if (c == '=' && depth <= 0)
                {
                    def = p.Substring(i + 1).Trim();
                    return p.Substring(0, i).Trim();
                }
            }
            return p.Trim();
        }

        private static readonly Regex NameSplit = new Regex(@"^(.+[\s\*&>])([A-Za-z_]\w*)(\s*\[[^\]]*\])*$", RegexOptions.Compiled);

        private static readonly Regex Comments = new Regex(@"/\*.*?\*/|//[^\r\n]*", RegexOptions.Singleline | RegexOptions.Compiled);

        // SAL 注釈(_In_ / _Out_writes_bytes_(n) / _COM_Outptr_opt_ など)。ヘッダーにだけあって、cpp は _Use_decl_annotations_ で省くことがある
        private static readonly Regex Sal = new Regex(@"(?<![A-Za-z0-9])_[A-Z][A-Za-z0-9_]*_(?:\s*\((?:[^()]|\((?:[^()]|\([^()]*\))*\))*\))?", RegexOptions.Compiled);

        /// <summary>コメントと SAL 注釈を空白にする(型の比較と名前の取り出しの前に使う)。</summary>
        public static string StripComments(string p) { return Calls.Replace(Sal.Replace(Comments.Replace(p, " "), " "), " "); }

        // 呼び出し規約(void __cdecl() と void() は同じ型)
        private static readonly Regex Calls = new Regex(@"\b__(?:cdecl|stdcall|fastcall|vectorcall)\b", RegexOptions.Compiled);

        /// <summary>引数の名前。名前のない引数(型だけ)なら null。</summary>
        public static string ParamName(string p)
        {
            p = StripComments(p);
            string def;
            string core = Regex.Replace(StripDefault(p, out def), @"\s+", " ").Trim();
            var m = NameSplit.Match(core);
            if (!m.Success) return null;
            string ident = m.Groups[2].Value;
            if (Builtins.Contains(ident)) return null;
            string head = m.Groups[1].Value;
            var words = Regex.Matches(head, @"\w+").Cast<Match>().Select(x => x.Value).ToList();
            if (words.Count > 0 && words.All(w => Qualifiers.Contains(w))) return null;   // const Foo のような、名前のない型
            return ident;
        }

        /// <summary>引数の型だけを、空白を整えた形にしたもの(名前と既定値を除く)。</summary>
        public static string TypeKey(string p)
        {
            p = StripComments(p);
            string def;
            string core = Regex.Replace(StripDefault(p, out def), @"\s+", " ").Trim();
            string name = ParamName(p);
            if (name != null)
            {
                var m = NameSplit.Match(core);
                core = m.Groups[1].Value.Trim();
            }
            core = Regex.Replace(core, @"^(struct|class|enum|typename)\s+", "");
            core = Regex.Replace(core, @"\s*([*&<>,:()])\s*", "$1");
            // 「Foo const&」と「const Foo&」は同じ型。const を先頭にそろえる(「char* const」のように、* のあとの const はそのまま)
            core = Regex.Replace(core, @"^((?:[A-Za-z_][\w:]*(?:<[^<>]*>)?)(?:\s+[A-Za-z_]\w*)*?)\s+const(?=\s*[*&]|\s*$)", "const $1");
            return core;
        }

        public static List<string> TypeKeys(List<string> ps) { return ps.Select(TypeKey).ToList(); }

        /// <summary>引数のリストで、既定値のある引数のあとに、既定値のない引数があるか(C++ では書けない)。</summary>
        public static bool DefaultsOutOfOrder(List<string> ps)
        {
            bool seen = false;
            foreach (string p in ps)
            {
                string def;
                StripDefault(p, out def);
                if (def != null) seen = true;
                else if (seen) return true;
            }
            return false;
        }

        public static string Norm(string s) { return Regex.Replace(s, @"\s+", " ").Trim(); }

        /// <summary>newKeys[j] が oldKeys のどれと対応するか(最長の共通部分列)。対応するものがなければ -1。</summary>
        public static int[] Align(List<string> oldKeys, List<string> newKeys)
        {
            int a = oldKeys.Count, b = newKeys.Count;
            var dp = new int[a + 1, b + 1];
            for (int i = a - 1; i >= 0; i--)
                for (int j = b - 1; j >= 0; j--)
                    dp[i, j] = oldKeys[i] == newKeys[j] ? dp[i + 1, j + 1] + 1 : Math.Max(dp[i + 1, j], dp[i, j + 1]);
            var map = Enumerable.Repeat(-1, b).ToArray();
            for (int i = 0, j = 0; i < a && j < b;)
            {
                if (oldKeys[i] == newKeys[j]) { map[j] = i; i++; j++; }
                else if (dp[i + 1, j] >= dp[i, j + 1]) i++;
                else j++;
            }
            return map;
        }

        private static readonly Regex NameTail = new Regex(@"^(.+[\s\*&>])([A-Za-z_]\w*)((?:\s*\[[^\]]*\])*)$", RegexOptions.Compiled);

        /// <summary>
        /// 変えた側の新しい引数(newChanged)を、相手側の括弧の中身に写した文字を作る。
        /// oldChanged は変える前の引数、counterpart は相手側の今の引数(型の並びは oldChanged と同じ)。
        /// 方針: 残る引数は、相手の書き方(名前・既定値・const の位置)のまま残す。cpp の本文が使っている名前を壊さないため。
        ///   ・cpp の引数を改名したときだけ、ヘッダーにも新しい名前を写す(ヘッダーの既定値は残す)。ヘッダーの改名は、cpp に写さない。
        ///   ・型だけ変えたとき(同じ位置で、名前が同じ)は、相手の名前を残して、型だけ新しくする。
        ///   ・増えた引数は、変えた側の書き方で足す(cpp に足すときは既定値を付けない)。
        /// toHeader が true のとき、相手はヘッダーで、false のとき、相手は cpp。
        /// </summary>
        public static string Rebuild(List<string> oldChanged, List<string> newChanged, List<string> counterpart, bool toHeader, string counterpartInner)
        {
            int[] map = Align(TypeKeys(oldChanged), TypeKeys(newChanged));
            bool sameCount = oldChanged.Count == newChanged.Count && counterpart.Count == oldChanged.Count;
            var parts = new List<string>();
            for (int j = 0; j < newChanged.Count; j++)
            {
                string def;
                string core = StripDefault(newChanged[j], out def);
                int a = map[j];
                if (a >= 0 && a < counterpart.Count)
                {
                    string oldName = ParamName(oldChanged[a]);
                    string newName = ParamName(core);
                    bool renamed = newName != null && newName != oldName;
                    if (toHeader && renamed)
                    {
                        string cpDef;
                        StripDefault(counterpart[a], out cpDef);
                        parts.Add(cpDef != null ? core + " = " + cpDef : core);
                    }
                    else parts.Add(counterpart[a]);
                    continue;
                }
                // 型だけ変えた(同じ位置・同じ名前)
                if (sameCount && j < counterpart.Count)
                {
                    string nm = ParamName(core);
                    string cpName = ParamName(counterpart[j]);
                    var m = NameTail.Match(Regex.Replace(core, @"\s+", " ").Trim());
                    if (nm != null && nm == ParamName(oldChanged[j]) && cpName != null && m.Success)
                    {
                        string cpDef;
                        StripDefault(counterpart[j], out cpDef);
                        string typed = m.Groups[1].Value + cpName + m.Groups[3].Value;
                        parts.Add(toHeader && cpDef != null ? typed + " = " + cpDef : typed);
                        continue;
                    }
                }
                parts.Add(core);
            }

            string sep = ", ";
            if (counterpartInner.IndexOf('\n') >= 0)
            {
                var lines = counterpartInner.Split('\n');
                string indent = lines.Length > 1 ? new string(lines[1].TakeWhile(c => c == ' ' || c == '\t').ToArray()) : "";
                bool crlf = counterpartInner.Contains("\r\n");
                sep = "," + (crlf ? "\r\n" : "\n") + indent;
            }
            return string.Join(sep, parts);
        }
    }
}
