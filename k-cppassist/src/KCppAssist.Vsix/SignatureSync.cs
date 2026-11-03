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

        // 関数ポインタの引数: void (*handle_result)(void* arg, const Slice& k)。1 = 戻り値の型、2 = 名前(なくてもよい)、3 = 引数のリスト
        private static readonly Regex FnPtr = new Regex(
            @"^(.*?)\(\s*(?:[*&^]|\w+::\*)\s*([A-Za-z_]\w*)?\s*(?:\[[^\]]*\])?\s*\)\s*\((.*)\)\s*(?:const|noexcept|volatile|\s)*$", RegexOptions.Singleline | RegexOptions.Compiled);

        /// <summary>引数の名前。名前のない引数(型だけ)なら null。</summary>
        public static string ParamName(string p)
        {
            p = StripComments(p);
            string def;
            string core = Regex.Replace(StripDefault(p, out def), @"\s+", " ").Trim();
            var fp = FnPtr.Match(core);
            if (fp.Success) return fp.Groups[2].Success && fp.Groups[2].Length > 0 ? fp.Groups[2].Value : null;
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
            var fp = FnPtr.Match(core);
            if (fp.Success)
            {
                // 関数ポインタは、内側の引数の名前を除いて「戻り値(*)(型, 型)」にそろえる
                var inner = SplitParams(fp.Groups[3].Value);
                string args = inner == null ? Regex.Replace(fp.Groups[3].Value, @"\s+", "") : string.Join(",", inner.Select(TypeKey));
                string ret = Regex.Replace(Regex.Replace(fp.Groups[1].Value, @"\s+", " ").Trim(), @"\s*([*&<>,:()])\s*", "$1");
                return ret + "(*)(" + args + ")";
            }
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

        // ---- 別名(HANDLE と void* など)----

        private static readonly Dictionary<string, string> Aliases = new Dictionary<string, string>
        {
            { "HANDLE", "void*" }, { "LPVOID", "void*" }, { "PVOID", "void*" }, { "LPCVOID", "const void*" },
            { "LPSTR", "char*" }, { "PSTR", "char*" }, { "LPCSTR", "const char*" }, { "PCSTR", "const char*" },
            { "LPWSTR", "wchar_t*" }, { "PWSTR", "wchar_t*" }, { "LPCWSTR", "const wchar_t*" }, { "PCWSTR", "const wchar_t*" },
            { "DWORD", "unsigned long" }, { "ULONG", "unsigned long" }, { "LONG", "long" }, { "WORD", "unsigned short" }, { "USHORT", "unsigned short" },
            { "BYTE", "unsigned char" }, { "UCHAR", "unsigned char" }, { "UINT", "unsigned int" }, { "INT", "int" }, { "BOOL", "int" },
            { "uint8_t", "unsigned char" }, { "uint16_t", "unsigned short" }, { "uint32_t", "unsigned int" }, { "uint64_t", "unsigned long long" },
            { "int8_t", "signed char" }, { "int16_t", "short" }, { "int32_t", "int" }, { "int64_t", "long long" },
            { "UINT8", "unsigned char" }, { "UINT16", "unsigned short" }, { "UINT32", "unsigned int" }, { "UINT64", "unsigned long long" },
            { "INT8", "signed char" }, { "INT16", "short" }, { "INT32", "int" }, { "INT64", "long long" },
        };
        private static readonly Regex AliasWord = new Regex(@"(?<![\w:])(?:std::)?([A-Za-z_]\w*)(?![\w])", RegexOptions.Compiled);

        /// <summary>
        /// 型のキーを、別名をそろえた形にする(HANDLE = void*、uint32_t = unsigned int、unsigned = unsigned int など)。
        /// 相手の引数を探すときの比較にだけ使う。引数の並びを合わせる(Align)には使わない(int を int32_t に変えたら、その変更を写したいので)。
        /// </summary>
        public static string AliasNorm(string key)
        {
            string s = AliasWord.Replace(key, m => { string v; return Aliases.TryGetValue(m.Groups[1].Value, out v) ? v : m.Value; });
            s = Regex.Replace(s, @"\b(unsigned|signed)\b(?!\s+(?:int|long|short|char)\b)", "$1 int");
            s = Regex.Replace(s, @"\bsigned int\b", "int");
            s = Regex.Replace(s, @"\b(long|short)\s+int\b", "$1");
            s = Regex.Replace(s, @"\bunsigned (long|short) int\b", "unsigned $1");
            s = Regex.Replace(s, @"\s+", " ");
            return Regex.Replace(s, @"\s*([*&<>,:()])\s*", "$1").Trim();
        }

        // ---- 引数の途中に #if が入るもの ----

        private static readonly Regex Directive = new Regex(@"^[ \t]*#[ \t]*(\w+)", RegexOptions.Compiled);

        /// <summary>引数の括弧の中に、#if などのプリプロセッサの行があるか。</summary>
        public static bool HasDirectives(string inner) { return Regex.IsMatch(inner, @"(?m)^[ \t]*#"); }

        /// <summary>
        /// #if / #else の枝を 1 つずつ選んだ中身を全部返す(最大 16 通り)。#if だけで #else がないときは、その枝を使わない場合も入れる。
        /// </summary>
        public static List<string> Variants(string inner)
        {
            var lines = inner.Replace("\r", "").Split('\n');
            int i = 0;
            string end;
            return ExpandLines(lines, ref i, out end);
        }

        private static List<string> ExpandLines(string[] lines, ref int i, out string end)
        {
            var results = new List<string> { "" };
            while (i < lines.Length)
            {
                var m = Directive.Match(lines[i]);
                if (m.Success)
                {
                    string d = m.Groups[1].Value;
                    if (d == "if" || d == "ifdef" || d == "ifndef")
                    {
                        i++;
                        var branches = new List<string>();
                        bool hasElse = false;
                        while (true)
                        {
                            string e;
                            branches.AddRange(ExpandLines(lines, ref i, out e));
                            if (e == "elif") continue;
                            if (e == "else") { hasElse = true; continue; }
                            break;
                        }
                        if (!hasElse) branches.Add("");
                        var next = new List<string>();
                        foreach (string r in results)
                            foreach (string b in branches)
                            {
                                if (next.Count >= 16) break;
                                next.Add(r + b);
                            }
                        results = next;
                        continue;
                    }
                    if (d == "elif" || d == "else" || d == "endif") { end = d; i++; return results; }
                    i++;
                    continue;
                }
                for (int k = 0; k < results.Count; k++) results[k] += lines[i] + "\n";
                i++;
            }
            end = null;
            return results;
        }

        /// <summary>括弧の中身から、引数の型のキーの並びを返す。#if があれば、枝の選び方ごとに 1 つずつ。読めないものは入れない。</summary>
        public static List<List<string>> KeyVariants(string inner)
        {
            var result = new List<List<string>>();
            foreach (string v in HasDirectives(inner) ? Variants(inner) : new List<string> { inner })
            {
                var l = SplitParams(v);
                if (l != null) result.Add(TypeKeys(l));
            }
            return result;
        }

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
