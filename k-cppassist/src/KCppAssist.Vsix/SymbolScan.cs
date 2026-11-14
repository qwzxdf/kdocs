using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// 名前の宣言(ローカル変数・引数・メンバー変数・メンバー関数・関数)を文字から見分けて、その名前を使っている場所を集める。VS に依存しない。
    /// 型の解決はしない。確かに同じものと言える場所(Certain)と、受け手の型が分からない obj.name(あいまい)を分けて返す。
    /// </summary>
    internal static class SymbolScan
    {
        public enum Kind { Local, Param, Field, Method, Function }

        public enum Verdict { No, Yes, Unknown }

        public sealed class Decl
        {
            public Kind Kind;
            public string Name;
            public int Start;                       // 名前の頭の位置
            public string Class;                    // Field / Method: そのクラス
            public List<string> Chain = new List<string>();   // Function: 囲んでいる namespace
            public bool Private;                    // Field / Method: private か protected
            public bool FileLocal;                  // Function: static か、無名の namespace の中(ほかのファイルからは見えない)
            public int ScopeStart, ScopeEnd;        // Local / Param: 名前が見える範囲(同じファイルの中)
            public FunctionScan.Sig Sig;            // Param / Method / Function: その関数
        }

        public sealed class Ref
        {
            public int Start;
            public bool Certain;
        }

        public sealed class Edit
        {
            public int Start, Length;
            public string Text;
        }

        /// <summary>ファイルをまたいで調べるための手がかり。</summary>
        public sealed class Context
        {
            /// <summary>同じメンバーを持つクラス(宣言したクラスと、その派生クラス。仮想関数なら基底も)。</summary>
            public HashSet<string> Family = new HashSet<string>();

            /// <summary>クラスの名前から、そのクラスを定義しているファイルの文字を引く。なければ null でよい。</summary>
            public Func<string, IEnumerable<string>> ClassTexts;

            /// <summary>
            /// 同じ名前で引数の違う関数(オーバーロード)があるとき、変える関数の引数の型の並び。
            /// null でなければ、宣言と定義はこの並びのものだけを変え、呼び出しは「あいまい」にする。
            /// </summary>
            public List<List<string>> OverloadKeys;

            /// <summary>クラスの名前から、その基底クラス。なければ null でよい。</summary>
            public Dictionary<string, HashSet<string>> Bases;

            /// <summary>関数: 同じ名前の関数が、別の namespace にもある。修飾のない呼び出しは、同じ namespace の中のものだけを確かとする。</summary>
            public bool NameClash;

            /// <summary>name が、プロジェクトのどこかで定義されているクラスか(Bases がなければ、分からないので false)。</summary>
            public bool IsClass(string name) { return Bases != null && name != null && Bases.ContainsKey(name); }

            public IEnumerable<string> TextsOf(string cls)
            {
                if (ClassTexts == null || cls == null) return Enumerable.Empty<string>();
                return ClassTexts(cls) ?? Enumerable.Empty<string>();
            }
        }

        // 名前にならない語
        private static readonly HashSet<string> Reserved = new HashSet<string>
        {
            "int", "char", "short", "long", "float", "double", "bool", "void", "unsigned", "signed", "wchar_t", "auto", "char8_t", "char16_t", "char32_t",
            "const", "constexpr", "consteval", "constinit", "static", "inline", "mutable", "volatile", "thread_local", "extern", "register", "typename", "virtual", "explicit",
            "if", "else", "for", "while", "do", "switch", "case", "default", "break", "continue", "return", "goto", "try", "catch", "throw",
            "new", "delete", "sizeof", "alignof", "alignas", "decltype", "noexcept", "static_assert", "operator", "template", "typedef", "using", "namespace",
            "class", "struct", "enum", "union", "friend", "public", "private", "protected", "override", "final",
            "this", "true", "false", "nullptr", "co_return", "co_yield", "co_await", "and", "or", "not", "xor",
        };

        // 型の前に付くだけで、それ自体は型にならない語
        private static readonly HashSet<string> TypeQualifiers = new HashSet<string>
        {
            "const", "constexpr", "constinit", "static", "inline", "mutable", "volatile", "thread_local", "extern", "register", "typename", "virtual", "explicit",
        };

        // 宣言の頭にあってはいけない語(文が宣言ではない)
        private static readonly HashSet<string> NotDeclWords = new HashSet<string>
        {
            "return", "delete", "new", "throw", "goto", "case", "using", "namespace", "typedef", "class", "struct", "enum", "union", "else",
            "co_return", "co_yield", "co_await", "operator", "friend", "public", "private", "protected", "sizeof", "template", "static_assert",
            "break", "continue", "do", "default", "if", "for", "while", "switch", "try", "catch", "this", "true", "false", "nullptr", "not", "and", "or",
        };

        private static readonly HashSet<string> SmartPointers = new HashSet<string>
        {
            "unique_ptr", "shared_ptr", "weak_ptr", "optional", "ComPtr", "not_null", "observer_ptr", "reference_wrapper",
        };

        // ---- 文字の小道具 ----

        private static int Prev(string m, int i)
        {
            int p = i - 1;
            while (p >= 0 && char.IsWhiteSpace(m[p])) p--;
            return p;
        }

        private static int Next(string m, int i)
        {
            while (i < m.Length && char.IsWhiteSpace(m[i])) i++;
            return i;
        }

        private static char At(string m, int i) { return i >= 0 && i < m.Length ? m[i] : '\0'; }

        public static bool IsIdentifier(string s)
        {
            if (string.IsNullOrEmpty(s) || char.IsDigit(s[0])) return false;
            foreach (char c in s) if (!CppText.IsId(c)) return false;
            return !Reserved.Contains(s);
        }

        /// <summary>pos を含む(か、pos で終わる・始まる)識別子の範囲。なければ false。</summary>
        public static bool IdentAt(string m, int pos, out int start, out int end)
        {
            start = end = Math.Max(0, Math.Min(pos, m.Length));
            while (start > 0 && CppText.IsId(m[start - 1])) start--;
            while (end < m.Length && CppText.IsId(m[end])) end++;
            return end > start && !char.IsDigit(m[start]);
        }

        private static bool WordAt(string m, int i, string word)
        {
            if (i < 0 || i + word.Length > m.Length) return false;
            if (string.CompareOrdinal(m, i, word, 0, word.Length) != 0) return false;
            if (i > 0 && CppText.IsId(m[i - 1])) return false;
            return !(i + word.Length < m.Length && CppText.IsId(m[i + word.Length]));
        }

        /// <summary>end(含まない)の直前で終わる識別子。なければ null。</summary>
        private static string WordBefore(string m, int end, out int start)
        {
            start = end;
            while (start > 0 && CppText.IsId(m[start - 1])) start--;
            return end > start ? m.Substring(start, end - start) : null;
        }

        /// <summary>
        /// p が「型(と *・&amp;)」だけでできているか。そうなら型の文字を返す。
        /// commaSplits が true のときは、一番外側のカンマで区切った最後の部分だけを見る(ラムダの引数)。
        /// </summary>
        public static string TypePrefix(string p, bool commaSplits)
        {
            int i = 0, n = p.Length, segStart = 0, words = 0;
            bool lastScope = false, prevWord = false;
            while (i < n)
            {
                char c = p[i];
                if (char.IsWhiteSpace(c)) { i++; continue; }
                if (c == '*' || c == '&') { if (words == 0) return null; prevWord = false; i++; continue; }
                if (c == ':' && i + 1 < n && p[i + 1] == ':') { i += 2; lastScope = true; prevWord = false; continue; }
                if (CppText.IsId(c) && !char.IsDigit(c))
                {
                    int j = i;
                    while (j < n && CppText.IsId(p[j])) j++;
                    string word = p.Substring(i, j - i);
                    if (NotDeclWords.Contains(word)) return null;
                    if (!TypeQualifiers.Contains(word)) { words++; prevWord = true; }
                    else prevWord = false;
                    i = j;
                    lastScope = false;
                    continue;
                }
                if (c == '<')
                {
                    if (!prevWord) return null;
                    int depth = 0, j = i;
                    for (; j < n; j++)
                    {
                        char d = p[j];
                        if (d == '<') depth++;
                        else if (d == '>') { if (j > 0 && p[j - 1] == '-') continue; depth--; if (depth == 0) break; }
                        else if (d == ';' || d == '{' || d == '}') return null;
                    }
                    if (j >= n) return null;
                    i = j + 1;
                    lastScope = false;
                    prevWord = false;
                    continue;
                }
                if (c == ',' && commaSplits) { segStart = i + 1; words = 0; lastScope = false; prevWord = false; i++; continue; }
                return null;
            }
            if (words == 0 || lastScope) return null;
            return p.Substring(segStart).Trim();
        }

        /// <summary>k から始まる文の終わり(「;」か、ブロックの「}」)の位置。else が続けば、その終わりまで。</summary>
        private static int StatementEnd(string m, int k, int limit)
        {
            k = Next(m, k);
            if (k >= limit) return limit;
            int end;
            if (m[k] == '{')
            {
                end = FunctionScan.MatchClose(m, k, '{', '}');
                if (end < 0) return limit;
            }
            else
            {
                bool isIf = WordAt(m, k, "if");
                if (isIf || WordAt(m, k, "for") || WordAt(m, k, "while") || WordAt(m, k, "switch"))
                {
                    int open = m.IndexOf('(', k);
                    int close = open < 0 ? -1 : FunctionScan.MatchClose(m, open, '(', ')');
                    if (close < 0) return limit;
                    end = StatementEnd(m, close + 1, limit);
                }
                else
                {
                    int depth = 0;
                    end = limit;
                    for (int i = k; i < limit; i++)
                    {
                        char c = m[i];
                        if (c == '(' || c == '{' || c == '[') depth++;
                        else if (c == ')' || c == '}' || c == ']') { depth--; if (depth < 0) { end = i; break; } }
                        else if (c == ';' && depth == 0) { end = i; break; }
                    }
                }
            }
            int e = Next(m, end + 1);
            if (WordAt(m, e, "else")) return StatementEnd(m, e + 4, limit);
            return end;
        }

        // ---- 宣言を見分ける ----

        /// <summary>
        /// 関数の本体の中の識別子 [s, e) が、ローカル変数の宣言(型 名前 …)の名前か。そうなら型の文字と、名前が見える範囲の終わりを返す。
        /// for / if / while / switch / catch の括弧の中の宣言と、ラムダの引数も見る。lower は関数の本体の「{」の位置。
        /// </summary>
        public static bool LocalDeclAt(string m, int s, int e, int lower, int upper, out string type, out int scopeEnd)
        {
            type = null;
            scopeEnd = -1;
            int depth = 0, i = s - 1, paren = -1;
            for (; i > lower; i--)
            {
                char c = m[i];
                if (c == ')') depth++;
                else if (c == '(') { if (depth == 0) { paren = i; break; } depth--; }
                else if (depth == 0 && (c == ';' || c == '{' || c == '}')) break;
            }
            int stmt = i + 1;
            if (s - stmt > 300) return false;
            string prefix = m.Substring(stmt, s - stmt);
            char next = At(m, Next(m, e));
            char next2 = At(m, Next(m, e) + 1);

            if (paren >= 0)
            {
                int pw = Prev(m, paren);
                bool lambda = pw >= 0 && m[pw] == ']';
                string ctrl = null;
                if (!lambda)
                {
                    int ws;
                    ctrl = pw >= 0 ? WordBefore(m, pw + 1, out ws) : null;
                    if (ctrl != "for" && ctrl != "if" && ctrl != "while" && ctrl != "switch" && ctrl != "catch") return false;
                }
                type = TypePrefix(prefix, lambda);
                if (type == null) return false;
                if (lambda) { if (next != ',' && next != ')' && next != '=') return false; }
                else if (ctrl == "catch") { if (next != ')') return false; }
                else if (ctrl == "for") { if (!(next == '=' || next == '{' || next == '(' || next == ';' || next == '[' || (next == ':' && next2 != ':'))) return false; }
                else if (!(next == '=' && next2 != '=') && next != '{') return false;
                if (next == '=' && next2 == '=') return false;

                int close = FunctionScan.MatchClose(m, paren, '(', ')');
                if (close < 0 || close > upper) return false;
                int k = Next(m, close + 1);
                if (lambda)
                {
                    int stop = Math.Min(upper, k + 200);
                    while (k < stop && m[k] != '{' && m[k] != ';') k++;
                    if (k >= stop || m[k] != '{') return false;
                    scopeEnd = FunctionScan.MatchClose(m, k, '{', '}');
                    return scopeEnd > 0;
                }
                scopeEnd = StatementEnd(m, k, upper);
                return true;
            }

            type = TypePrefix(prefix, false);
            if (type == null) return false;
            if (next == '=' && next2 == '=') return false;
            if (!(next == '=' || next == ';' || next == '{' || next == '(' || next == '[' || next == ',')) return false;

            // 名前が見えるのは、囲んでいるブロックの終わりまで
            int d2 = 0, open = lower;
            for (int j = stmt - 1; j > lower; j--)
            {
                if (m[j] == '}') d2++;
                else if (m[j] == '{') { if (d2 == 0) { open = j; break; } d2--; }
            }
            scopeEnd = FunctionScan.MatchClose(m, open, '{', '}');
            if (scopeEnd < 0) scopeEnd = upper;
            return true;
        }

        /// <summary>識別子 [s, e) が、関数 sig の引数の名前か。</summary>
        public static bool ParamAt(string text, string m, FunctionScan.Sig sig, int s, int e)
        {
            if (!(sig.Open < s && e <= sig.Close)) return false;
            bool pack;
            var ranges = CallCheck.Split(m, text, sig.Open + 1, sig.Close, out pack);
            if (ranges == null) return false;
            var r = ranges.FirstOrDefault(x => x[0] <= s && e <= x[1]);
            if (r == null || r[0] == s) return false;      // 前に型がない
            string name = m.Substring(s, e - s);
            if (SignatureSync.ParamName(text.Substring(r[0], r[1] - r[0])) != name) return false;
            // 既定値(= …)の中の同じ名前ではないこと
            int depth = 0;
            for (int i = r[0]; i < s; i++)
            {
                char c = m[i];
                if (c == '(' || c == '[' || c == '{' || c == '<') depth++;
                else if (c == ')' || c == ']' || c == '}' || c == '>') depth--;
                else if (c == '=' && depth <= 0) return false;
            }
            char next = At(m, Next(m, e));
            return next == ',' || next == ')' || next == '=' || next == '[';
        }

        /// <summary>クラスの本体のすぐ下(関数の中ではない)にある識別子 [s, e) が、メンバー変数の宣言の名前か。</summary>
        public static bool FieldDeclAt(string m, int s, int e, Scopes.Scope cls, out string type)
        {
            type = null;
            int depth = 0;
            for (int i = cls.Open + 1; i < s; i++)
            {
                if (m[i] == '{') depth++;
                else if (m[i] == '}') depth--;
            }
            if (depth != 0) return false;
            int k = s - 1, paren = 0;
            for (; k > cls.Open; k--)
            {
                char c = m[k];
                if (c == ')') { paren++; continue; }                 // std::function<void(int)> の括弧は、型の一部
                if (c == '(') { if (paren == 0) return false; paren--; continue; }
                if (paren > 0) continue;
                if (c == ';' || c == '{' || c == '}') break;
                if (c == ':' && At(m, k - 1) != ':' && At(m, k + 1) != ':') break;      // public: など
            }
            int stmt = k + 1;
            if (s - stmt > 300) return false;
            type = TypePrefix(m.Substring(stmt, s - stmt), false);
            if (type == null) return false;
            int a = Next(m, e);
            char next = At(m, a), next2 = At(m, a + 1);
            if (next == ':') return next2 != ':';
            if (next == '=') return next2 != '=';
            return next == ';' || next == '{' || next == '[' || next == ',';
        }

        /// <summary>クラスの本体の pos が、private か protected の区画にあるか。</summary>
        public static bool IsPrivateAt(string m, Scopes.Scope cls, int pos)
        {
            bool priv = !cls.IsStruct;
            int depth = 0;
            for (int i = cls.Open + 1; i < pos && i < m.Length; i++)
            {
                char c = m[i];
                if (c == '{') depth++;
                else if (c == '}') depth--;
                else if (depth == 0 && c == 'p')
                {
                    string w = WordAt(m, i, "public") ? "public" : WordAt(m, i, "private") ? "private" : WordAt(m, i, "protected") ? "protected" : null;
                    if (w == null) continue;
                    int a = Next(m, i + w.Length);
                    if (At(m, a) == ':' && At(m, a + 1) != ':') priv = w != "public";
                    i += w.Length - 1;
                }
            }
            return priv;
        }

        /// <summary>関数 sig の名前の頭の位置(修飾 Class:: は含まない)。読めなければ -1。</summary>
        public static int NamePos(string m, FunctionScan.Sig sig)
        {
            int end = Prev(m, sig.Open) + 1;
            int start = end - sig.Name.Length;
            if (start < 0 || string.CompareOrdinal(m, start, sig.Name, 0, sig.Name.Length) != 0) return -1;
            return start;
        }

        private static Scopes.Scope ClassAt(List<Scopes.Scope> scopes, int p)
        {
            return scopes.Where(x => x.IsClass && x.Open < p && p < x.Close).OrderByDescending(x => x.Open).FirstOrDefault();
        }

        private static FunctionScan.Sig SigAt(List<FunctionScan.Sig> sigs, int p)
        {
            return sigs.LastOrDefault(x => x.PrefixStart <= p && p <= x.End);
        }

        /// <summary>pos にある識別子が、名前を変えられる宣言なら、その宣言。そうでなければ null。</summary>
        public static Decl DeclAt(string text, int pos)
        {
            string m = CppText.Mask(text);
            int s, e;
            if (!IdentAt(m, pos, out s, out e)) return null;
            string name = m.Substring(s, e - s);
            if (Reserved.Contains(name)) return null;
            var sigs = FunctionScan.Scan(text);

            foreach (var sig in sigs)
            {
                if (NamePos(m, sig) != s) continue;
                if (sig.Class != null && sig.Name == sig.Class) return null;       // コンストラクター(クラスの名前)は扱わない
                // 行を複製して、写しのほうの名前を書き換えている(同じ名前・同じ引数の宣言がもう 1 つある)ときは、名前の変更ではない
                var keys = SignatureSync.KeyVariants(sig.Inner(text));
                if (keys.Count > 0 && sigs.Any(o => o != sig && o.Name == sig.Name && o.Class == sig.Class && o.HasBody == sig.HasBody && o.InClass == sig.InClass
                        && o.IsConst == sig.IsConst && o.Chain.SequenceEqual(sig.Chain) && SyncPlan.SameKeysAny(SignatureSync.KeyVariants(o.Inner(text)), keys)))
                    return null;
                var d = new Decl { Kind = sig.Class != null ? Kind.Method : Kind.Function, Name = name, Start = s, Class = sig.Class, Sig = sig };
                if (sig.Class == null)
                {
                    d.Chain.AddRange(sig.Chain);
                    d.FileLocal = Regex.IsMatch(m.Substring(sig.PrefixStart, Math.Max(0, s - sig.PrefixStart)), @"\bstatic\b")
                        || Scopes.Parse(text).Any(x => !x.IsClass && x.Name == null && x.Open < s && s < x.Close);
                }
                else if (sig.InClass)
                {
                    var cls = ClassAt(Scopes.Parse(text), s);
                    d.Private = cls != null && IsPrivateAt(m, cls, s);
                }
                return d;
            }

            var inSig = SigAt(sigs, s);
            if (inSig != null)
            {
                if (ParamAt(text, m, inSig, s, e))
                {
                    var ps = SignatureSync.SplitParams(inSig.Inner(text));
                    if (ps != null && ps.Count(x => SignatureSync.ParamName(x) == name) > 1) return null;      // 複製した引数
                    var d = new Decl { Kind = Kind.Param, Name = name, Start = s, Sig = inSig };
                    if (inSig.HasBody) { d.ScopeStart = inSig.Close + 1; d.ScopeEnd = inSig.End; }
                    return d;
                }
                if (inSig.HasBody && inSig.BodyOpen < s && s < inSig.End)
                {
                    string type;
                    int scopeEnd;
                    if (!LocalDeclAt(m, s, e, inSig.BodyOpen, inSig.End, out type, out scopeEnd)) return null;
                    // 同じブロックに、同じ名前の宣言がもう 1 つある(行を複製して、写しの名前を書き換えている)ときは、名前の変更ではない
                    foreach (var id in CppText.Identifiers(m, inSig.BodyOpen, scopeEnd))
                    {
                        if (id.Value != name || id.Key == s) continue;
                        string t2;
                        int end2;
                        if (LocalDeclAt(m, id.Key, id.Key + name.Length, inSig.BodyOpen, inSig.End, out t2, out end2) && end2 == scopeEnd) return null;
                    }
                    return new Decl { Kind = Kind.Local, Name = name, Start = s, Sig = inSig, ScopeStart = e, ScopeEnd = scopeEnd };
                }
                return null;
            }

            var owner = ClassAt(Scopes.Parse(text), s);
            if (owner != null)
            {
                string type;
                if (!FieldDeclAt(m, s, e, owner, out type)) return null;
                foreach (var id in CppText.Identifiers(m, owner.Open + 1, owner.Close))
                {
                    string t2;
                    if (id.Value == name && id.Key != s && FieldDeclAt(m, id.Key, id.Key + name.Length, owner, out t2)) return null;     // 複製した行
                }
                return new Decl { Kind = Kind.Field, Name = name, Start = s, Class = owner.Name, Private = IsPrivateAt(m, owner, s) };
            }
            return null;
        }

        // ---- 使っている場所 ----

        private static bool AfterMemberAccess(string m, int p, out int op)
        {
            op = -1;
            int b = Prev(m, p);
            if (b < 0) return false;
            if (m[b] == '.') { if (At(m, b - 1) == '.') return false; op = b; return true; }     // 「...」は除く
            if (m[b] == '>' && At(m, b - 1) == '-') { op = b - 1; return true; }
            return false;
        }

        private static bool AfterScope(string m, int p)
        {
            int b = Prev(m, p);
            return b >= 1 && m[b] == ':' && m[b - 1] == ':';
        }

        /// <summary>コンストラクターの初期化子リストの「名前(…)」「名前{…}」の名前(メンバーの側)か。</summary>
        private static bool IsInitTarget(string m, FunctionScan.Sig sig, int p, int e)
        {
            if (sig == null || sig.InitStart < 0 || p <= sig.InitStart || p >= sig.BodyOpen) return false;
            int b = Prev(m, p);
            if (b < 0 || !(m[b] == ',' || (m[b] == ':' && At(m, b - 1) != ':'))) return false;
            char next = At(m, Next(m, e));
            if (next != '(' && next != '{') return false;
            int depth = 0;
            for (int i = sig.InitStart; i < p; i++)
            {
                if (m[i] == '(' || m[i] == '{') depth++;
                else if (m[i] == ')' || m[i] == '}') depth--;
            }
            return depth == 0;
        }

        /// <summary>ローカル変数・引数 d を使っている場所(宣言そのものは含まない)。同じ名前を内側で宣言し直した範囲は除く。</summary>
        public static List<Ref> LocalRefs(string text, Decl d)
        {
            var list = new List<Ref>();
            if (d.ScopeEnd <= d.ScopeStart) return list;
            string m = CppText.Mask(text);
            int skipUntil = -1;
            foreach (var id in CppText.Identifiers(m, d.ScopeStart, d.ScopeEnd))
            {
                if (id.Value != d.Name || id.Key == d.Start || id.Key < skipUntil) continue;
                int p = id.Key, e = p + d.Name.Length, op;
                if (AfterMemberAccess(m, p, out op) || AfterScope(m, p)) continue;
                int a = Next(m, e);
                if (At(m, a) == ':' && At(m, a + 1) == ':') continue;
                if (d.Kind == Kind.Param && IsInitTarget(m, d.Sig, p, e)) continue;
                if (d.Sig != null && d.Sig.BodyOpen >= 0 && p > d.Sig.BodyOpen)
                {
                    string type;
                    int inner;
                    if (LocalDeclAt(m, p, e, d.Sig.BodyOpen, d.Sig.End, out type, out inner)) { skipUntil = inner; continue; }
                }
                list.Add(new Ref { Start = p, Certain = true });
            }
            return list;
        }

        /// <summary>関数 sig の中の p から見て、name が引数かローカル変数として宣言されているか。型も返す。</summary>
        private static bool LocalDeclared(string text, string m, FunctionScan.Sig sig, string name, int p, out string type, out string init)
        {
            type = init = null;
            if (sig == null) return false;
            var ps = SignatureSync.SplitParams(sig.Inner(text));
            if (ps != null)
                foreach (string prm in ps)
                {
                    if (SignatureSync.ParamName(prm) != name) continue;
                    string def;
                    string core = SignatureSync.StripDefault(SignatureSync.StripComments(prm), out def).Trim();
                    var x = Regex.Match(core, @"^(.*?)\b" + Regex.Escape(name) + @"\s*(\[[^\]]*\])*$", RegexOptions.Singleline);
                    type = x.Success ? x.Groups[1].Value.Trim() : core;
                    return true;
                }
            if (!sig.HasBody || p <= sig.BodyOpen) return false;
            bool found = false;
            foreach (var id in CppText.Identifiers(m, sig.BodyOpen, p + 1))      // p そのものが宣言のときも含める
            {
                if (id.Value != name) continue;
                string t;
                int scopeEnd;
                if (!LocalDeclAt(m, id.Key, id.Key + name.Length, sig.BodyOpen, sig.End, out t, out scopeEnd)) continue;
                if (scopeEnd < p) continue;
                type = t;
                int semi = m.IndexOf(';', id.Key);
                int to = semi < 0 ? Math.Min(m.Length, id.Key + 200) : Math.Min(semi, id.Key + 200);
                init = m.Substring(id.Key + name.Length, to - id.Key - name.Length);
                found = true;       // 内側で宣言し直していれば、あとのものが勝つ
            }
            return found;
        }

        /// <summary>text の中のクラス cls の、メンバー変数 name の型。なければ null。</summary>
        public static string FieldType(string text, string cls, string name)
        {
            string m = CppText.Mask(text);
            foreach (var sc in Scopes.Parse(text).Where(x => x.IsClass && x.Name == cls))
                foreach (var id in CppText.Identifiers(m, sc.Open + 1, sc.Close))
                {
                    if (id.Value != name) continue;
                    string type;
                    if (FieldDeclAt(m, id.Key, id.Key + name.Length, sc, out type)) return type;
                }
            return null;
        }

        /// <summary>text の中のクラス cls が、メンバー関数 name を宣言しているか。private かどうかも返す。</summary>
        public static bool DeclaresMethod(string text, string cls, string name, out bool isPrivate)
        {
            isPrivate = false;
            if (text.IndexOf(name, StringComparison.Ordinal) < 0) return false;
            string m = CppText.Mask(text);
            var scopes = Scopes.Parse(text);
            foreach (var sig in FunctionScan.Scan(text))
            {
                if (!sig.InClass || sig.Class != cls || sig.Name != name) continue;
                int p = NamePos(m, sig);
                var sc = p < 0 ? null : ClassAt(scopes, p);
                isPrivate = sc != null && IsPrivateAt(m, sc, p);
                return true;
            }
            return false;
        }

        /// <summary>
        /// 型の文字(と、auto のときの初期化の式)から、その変数が family のクラスの物かを決める。
        /// arrow は「->」で使っているか。スマート ポインターは「->」のときだけ中身のクラスのメンバーになる。
        /// </summary>
        public static Verdict TypeVerdict(string type, string init, HashSet<string> family, bool arrow, Func<string, bool> isClass = null)
        {
            if (type == null) return Verdict.Unknown;
            // family にない名前が、ほかのクラスだと分かっていれば「違う」。分からない名前(using の別名、テンプレート引数)は「分からない」
            bool std = Regex.IsMatch(type, @"\bstd\s*::");
            Func<string, Verdict> other = n => isClass == null || std || Reserved.Contains(n) || isClass(n) ? Verdict.No : Verdict.Unknown;
            string t = Regex.Replace(type, @"\b(const|constexpr|constinit|static|inline|mutable|volatile|thread_local|extern|typename|struct|class)\b", " ");
            t = Regex.Replace(t, @"\s+", " ").Trim().TrimEnd('&', '*', ' ').Trim();
            if (t.Length == 0) return Verdict.Unknown;
            if (t == "auto" || t == "decltype(auto)")
            {
                if (init == null) return Verdict.Unknown;
                var mk = Regex.Match(init, @"^\s*[=({]\s*(?:std\s*::\s*)?make_(?:unique|shared)\s*<\s*(?:\w+\s*::\s*)*(\w+)\s*>");
                if (!mk.Success) mk = Regex.Match(init, @"^\s*[=({]\s*new\s+(?:\w+\s*::\s*)*(\w+)");
                if (mk.Success) return family.Contains(mk.Groups[1].Value) && arrow ? Verdict.Yes : Verdict.No;
                var ct = Regex.Match(init, @"^\s*[=({]\s*(?:\w+\s*::\s*)*(\w+)\s*[({]");
                if (ct.Success && family.Contains(ct.Groups[1].Value)) return arrow ? Verdict.No : Verdict.Yes;
                return Verdict.Unknown;
            }
            var wrap = Regex.Match(t, @"^(?:\w+\s*::\s*)*(\w+)\s*<\s*(?:const\s+)?(?:\w+\s*::\s*)*(\w+)\s*\*?\s*(?:const\s*)?>$");
            if (wrap.Success)
            {
                if (!SmartPointers.Contains(wrap.Groups[1].Value)) return Verdict.No;       // コンテナーなど。中身のクラスのメンバーではない
                if (!arrow) return Verdict.No;
                return family.Contains(wrap.Groups[2].Value) ? Verdict.Yes : isClass == null || Reserved.Contains(wrap.Groups[2].Value) || isClass(wrap.Groups[2].Value) ? Verdict.No : Verdict.Unknown;
            }
            var plain = Regex.Match(t, @"^(?:\w+\s*::\s*)*(\w+)$");
            if (plain.Success) return family.Contains(plain.Groups[1].Value) ? Verdict.Yes : other(plain.Groups[1].Value);
            return Verdict.Unknown;
        }

        /// <summary>「recv.name」「recv->name」の recv が、ただの識別子ならその名前。式(a.b、f()、v[i])なら null。</summary>
        private static string Receiver(string m, int op)
        {
            int b = Prev(m, op);
            if (b < 0 || !CppText.IsId(m[b])) return null;
            int start;
            string r = WordBefore(m, b + 1, out start);
            if (r == null || char.IsDigit(r[0])) return null;
            int pb = Prev(m, start);
            if (pb >= 0 && (m[pb] == '.' || m[pb] == ':' || (m[pb] == '>' && At(m, pb - 1) == '-'))) return null;
            return r;
        }

        private static Verdict ReceiverVerdict(string text, string m, FunctionScan.Sig sig, Scopes.Scope cls, List<Scopes.Scope> scopes, string recv, int p, bool arrow, Context ctx)
        {
            string type, init;
            Func<string, bool> isClass = ctx.Bases == null ? (Func<string, bool>)null : ctx.IsClass;
            if (LocalDeclared(text, m, sig, recv, p, out type, out init)) return TypeVerdict(type, init, ctx.Family, arrow, isClass);
            string owner = sig != null ? sig.Class : cls != null ? cls.Name : null;
            if (owner == null) return Verdict.Unknown;
            string ft = scopes.Any(x => x.IsClass && x.Name == owner) ? FieldType(text, owner, recv) : null;
            if (ft == null)
                foreach (string t in ctx.TextsOf(owner))
                {
                    ft = FieldType(t, owner, recv);
                    if (ft != null) break;
                }
            return ft == null ? Verdict.Unknown : TypeVerdict(ft, null, ctx.Family, arrow, isClass);
        }

        /// <summary>
        /// メンバー変数・メンバー関数・関数 d を、text の中で使っている場所。宣言と定義(Class::name)も含む。skipPos は、編集中の宣言そのものの位置。
        /// </summary>
        public static List<Ref> MemberRefs(string text, Decl d, Context ctx, int skipPos)
        {
            var list = new List<Ref>();
            if (text.IndexOf(d.Name, StringComparison.Ordinal) < 0) return list;
            string m = CppText.Mask(text);
            var ids = CppText.Identifiers(m, 0, m.Length).Where(x => x.Value == d.Name).ToList();
            if (ids.Count == 0) return list;
            var sigs = FunctionScan.Scan(text);
            var scopes = Scopes.Parse(text);
            var sigNames = new Dictionary<int, FunctionScan.Sig>();
            foreach (var s in sigs)
            {
                if (s.Name != d.Name) continue;
                int np = NamePos(m, s);
                if (np >= 0) sigNames[np] = s;
            }
            bool member = d.Kind == Kind.Field || d.Kind == Kind.Method;
            var extra = ExtraOwners(m);

            foreach (var id in ids)
            {
                int p = id.Key, e = p + d.Name.Length;
                if (p == skipPos) continue;
                int a = Next(m, e);
                bool call = At(m, a) == '(';
                if (At(m, a) == ':' && At(m, a + 1) == ':') continue;         // name::x は、名前空間やクラス
                FunctionScan.Sig sig = SigAt(sigs, p);
                Scopes.Scope cls = ClassAt(scopes, p);
                string owner = sig != null ? sig.Class : cls != null ? cls.Name : null;
                if (sig == null && cls == null)
                    foreach (var x in extra) if (x.Item1 < p && p < x.Item2) owner = x.Item3;
                bool inFamily = owner != null && ctx.Family.Contains(owner);
                FunctionScan.Sig asSig;
                sigNames.TryGetValue(p, out asSig);

                // オーバーロードがあるとき: 引数の型が同じ宣言・定義だけを変える
                if (ctx.OverloadKeys != null)
                {
                    if (asSig == null) { if (call) list.Add(new Ref { Start = p, Certain = false }); continue; }
                    bool mine = member ? asSig.Class != null && ctx.Family.Contains(asSig.Class) : asSig.Class == null;
                    if (mine && SyncPlan.SameKeysAny(SignatureSync.KeyVariants(asSig.Inner(text)), ctx.OverloadKeys)) list.Add(new Ref { Start = p, Certain = true });
                    continue;
                }

                if (AfterScope(m, p))
                {
                    int cs;
                    string chain = CppText.Chain(m, p, e, out cs);
                    if (chain == null) continue;
                    var parts = chain.Split(new[] { "::" }, StringSplitOptions.RemoveEmptyEntries);
                    string qual = parts.Length >= 2 ? parts[parts.Length - 2] : null;
                    if (member) { if (qual != null && ctx.Family.Contains(qual)) list.Add(new Ref { Start = p, Certain = true }); }
                    else if (qual == null ? d.Chain.Count == 0 : d.Chain.Count > 0 && d.Chain[d.Chain.Count - 1] == qual)
                    {
                        if (call) list.Add(new Ref { Start = p, Certain = true });
                    }
                    continue;
                }

                int op;
                if (AfterMemberAccess(m, p, out op))
                {
                    if (!member) continue;
                    if (d.Kind == Kind.Method && !call) continue;
                    bool arrow = m[op] == '-';
                    int b = Prev(m, op);
                    int ws;
                    string before = b >= 0 && CppText.IsId(m[b]) ? WordBefore(m, b + 1, out ws) : null;
                    if (before == "this") { if (inFamily) list.Add(new Ref { Start = p, Certain = true }); continue; }
                    string recv = Receiver(m, op);
                    Verdict v = recv == null ? Verdict.Unknown : ReceiverVerdict(text, m, sig, cls, scopes, recv, p, arrow, ctx);
                    if (v == Verdict.No) continue;
                    // private なメンバーを、同じクラスの関数の中から obj.name で触っているなら、同じクラスの物
                    bool certain = v == Verdict.Yes || (inFamily && d.Private);
                    list.Add(new Ref { Start = p, Certain = certain });
                    continue;
                }

                // 修飾のない名前
                if (!member)
                {
                    if (asSig != null)
                    {
                        // 宣言と定義。「ns::Func() {…}」と名前空間で修飾した定義は、Class に名前空間が入っている
                        bool free = asSig.Class == null || (!asSig.InClass && !ctx.IsClass(asSig.Class) && ctx.Bases != null);
                        // 修飾つきの定義は、変える関数に namespace があるときだけ(「Other::Func」の Other が、見つけられなかったクラスかもしれない)
                        if (free && SyncPlan.ChainScore(asSig.Chain, d.Chain) > 0 && (asSig.Class == null || d.Chain.Count > 0))
                            list.Add(new Ref { Start = p, Certain = true });
                        continue;
                    }
                    if (!call) continue;
                    if (owner != null && OwnerDeclares(text, owner, d.Name, ctx)) continue;     // そのクラスの同じ名前のメンバー関数の呼び出し
                    if (sig != null)
                    {
                        string t, init;
                        if (LocalDeclared(text, m, sig, d.Name, p, out t, out init)) continue;  // 同じ名前のローカル変数(関数オブジェクト)
                    }
                    bool sure = true;
                    if (ctx.NameClash)
                    {
                        // 同じ名前の関数が別の namespace にもある。呼び出しが、変える関数の namespace の中にあるときだけ確か
                        var here = Scopes.NamespacesAt(scopes, p);
                        sure = d.Chain.Count == 0 ? here.Count == 0 : here.Count >= d.Chain.Count && here.Take(d.Chain.Count).SequenceEqual(d.Chain);
                    }
                    list.Add(new Ref { Start = p, Certain = sure });
                    continue;
                }
                if (!inFamily) continue;
                if (asSig != null) { if (d.Kind == Kind.Method) list.Add(new Ref { Start = p, Certain = true }); continue; }
                if (d.Kind == Kind.Method) { if (call) list.Add(new Ref { Start = p, Certain = true }); continue; }
                // メンバー変数: 引数やローカル変数に同じ名前があれば、そちらが勝つ(初期化子リストの「名前(…)」の名前は、メンバー)
                if (sig != null && !IsInitTarget(m, sig, p, e))
                {
                    if (sig.Open < p && p < sig.Close) continue;
                    string t, init;
                    if (LocalDeclared(text, m, sig, d.Name, p, out t, out init)) continue;
                }
                list.Add(new Ref { Start = p, Certain = true });
            }
            return list;
        }

        private static readonly Regex OutOfClassSpecial = new Regex(
            @"(?<![\w:])([A-Za-z_]\w*)\s*(?:<[^<>;{}]*>)?\s*::\s*(?:~\s*[A-Za-z_]\w*|operator\b[^;{}(]*(?:\(\s*\))?)\s*\(", RegexOptions.Compiled);

        /// <summary>
        /// FunctionScan が拾わない、クラスの外に書いたデストラクターと演算子(Class::~Class、Class::operator==)の本体の範囲と、そのクラス。
        /// </summary>
        private static List<Tuple<int, int, string>> ExtraOwners(string m)
        {
            var list = new List<Tuple<int, int, string>>();
            if (m.IndexOf("::", StringComparison.Ordinal) < 0) return list;
            foreach (Match x in OutOfClassSpecial.Matches(m))
            {
                int open = x.Index + x.Length - 1;
                int close = FunctionScan.MatchClose(m, open, '(', ')');
                if (close < 0) continue;
                int j = close + 1;
                while (j < m.Length && m[j] != '{' && m[j] != ';' && m[j] != '}') j++;
                if (j >= m.Length || m[j] != '{') continue;
                int end = FunctionScan.MatchClose(m, j, '{', '}');
                if (end > 0) list.Add(Tuple.Create(j, end, x.Groups[1].Value));
            }
            return list;
        }

        private static bool OwnerDeclares(string text, string owner, string name, Context ctx)
        {
            // owner と、その基底クラス(5 段まで)のどれかが、同じ名前のメンバー関数を宣言しているか
            var todo = new List<string> { owner };
            var seen = new HashSet<string> { owner };
            for (int depth = 0; depth < 6 && todo.Count > 0; depth++)
            {
                var next = new List<string>();
                foreach (string cls in todo)
                {
                    bool priv;
                    if (DeclaresMethod(text, cls, name, out priv)) return true;
                    foreach (string t in ctx.TextsOf(cls))
                        if (DeclaresMethod(t, cls, name, out priv)) return true;
                    HashSet<string> bs;
                    if (ctx.Bases != null && ctx.Bases.TryGetValue(cls, out bs))
                        foreach (string b in bs) if (seen.Add(b)) next.Add(b);
                }
                todo = next;
            }
            return false;
        }

        // ---- 継承 ----

        private static readonly Regex ClassHeadRe = new Regex(
            @"\b(?:class|struct)\s+(?:[A-Za-z_]\w*\s+)*?([A-Za-z_]\w*)\s*(?:final\s*)?(?::([^;{}]*))?\{", RegexOptions.Compiled);

        /// <summary>text の中の class / struct の名前と、その基底クラスを集める(bases[派生] = 基底の集合。基底がなくても、名前は入る)。</summary>
        public static void CollectClasses(string text, Dictionary<string, HashSet<string>> bases)
        {
            if (text.IndexOf("class", StringComparison.Ordinal) < 0 && text.IndexOf("struct", StringComparison.Ordinal) < 0) return;
            foreach (Match x in ClassHeadRe.Matches(text))
            {
                string name = x.Groups[1].Value;
                HashSet<string> set;
                if (!bases.TryGetValue(name, out set)) bases[name] = set = new HashSet<string>();
                if (!x.Groups[2].Success) continue;
                string list = x.Groups[2].Value;
                while (true)
                {
                    string r = Regex.Replace(list, @"<[^<>]*>", "");
                    if (r == list) break;
                    list = r;
                }
                foreach (string part in list.Split(','))
                {
                    var words = Regex.Matches(part, @"[A-Za-z_]\w*");
                    if (words.Count > 0) set.Add(words[words.Count - 1].Value);
                }
            }
        }

        /// <summary>
        /// cls と同じメンバーを持つクラスの集合。派生クラスをたどる。upward が true(メンバー関数)のときは、
        /// declares(その名前の関数を宣言しているクラス)に入っている基底クラスもたどる(仮想関数の override)。
        /// </summary>
        public static HashSet<string> BuildFamily(string cls, bool upward, Dictionary<string, HashSet<string>> bases, HashSet<string> declares)
        {
            var family = new HashSet<string> { cls };
            bool grew = true;
            while (grew)
            {
                grew = false;
                foreach (var kv in bases)
                {
                    if (!family.Contains(kv.Key) && kv.Value.Any(family.Contains)) { family.Add(kv.Key); grew = true; }
                    if (upward && family.Contains(kv.Key))
                        foreach (string b in kv.Value)
                            if (declares.Contains(b) && family.Add(b)) grew = true;
                }
            }
            return family;
        }

        // ---- 引数の並べ替え・削除を、呼び出しへ写す ----

        /// <summary>
        /// 新しい引数 newPs[j] が、古い引数 oldPs のどれに当たるか(なければ -1)。名前が同じもの、次に型が同じもの、の順に対応させる。
        /// 残りが同じ数なら、位置の順に対応させる(型と名前を両方変えた)。
        /// 対応を決められない(同じ型の引数のどれを消したか分からない)ときは null。
        /// </summary>
        public static int[] ParamMap(List<string> oldPs, List<string> newPs)
        {
            var map = Enumerable.Repeat(-1, newPs.Count).ToArray();
            var used = new bool[oldPs.Count];
            var oldNames = oldPs.Select(SignatureSync.ParamName).ToList();
            var newNames = newPs.Select(SignatureSync.ParamName).ToList();
            for (int j = 0; j < newPs.Count; j++)
            {
                if (newNames[j] == null) continue;
                int i = FirstIndex(oldPs.Count, k => !used[k] && oldNames[k] == newNames[j]);
                if (i >= 0) { map[j] = i; used[i] = true; }
            }
            var oldKeys = SignatureSync.TypeKeys(oldPs);
            var newKeys = SignatureSync.TypeKeys(newPs);
            for (int j = 0; j < newPs.Count; j++)
            {
                if (map[j] >= 0) continue;
                // 同じ型の引数がいくつも残っていて、数も変わったときは、どれを消したのか決められない
                int same = 0;
                for (int k = 0; k < oldPs.Count; k++) if (!used[k] && oldKeys[k] == newKeys[j]) same++;
                if (same > 1 && oldPs.Count != newPs.Count) return null;
                int i = j < oldPs.Count && !used[j] && oldKeys[j] == newKeys[j] ? j
                    : FirstIndex(oldPs.Count, k => !used[k] && oldKeys[k] == newKeys[j]);
                if (i >= 0) { map[j] = i; used[i] = true; }
            }
            var freeNew = Enumerable.Range(0, newPs.Count).Where(j => map[j] < 0).ToList();
            var freeOld = Enumerable.Range(0, oldPs.Count).Where(i => !used[i]).ToList();
            if (freeNew.Count == freeOld.Count)
                for (int k = 0; k < freeNew.Count; k++) map[freeNew[k]] = freeOld[k];
            return map;
        }

        private static int FirstIndex(int count, Func<int, bool> pred)
        {
            for (int k = 0; k < count; k++) if (pred(k)) return k;
            return -1;
        }

        /// <summary>
        /// 「ns::Func() {…}」のように名前空間で修飾した定義は、FunctionScan では Class に名前空間が入る。
        /// その名前のクラスがどこにもなければ、メンバー関数ではなく、名前空間の中の関数として扱う。
        /// </summary>
        public static void NormalizeKind(Decl d, Context ctx)
        {
            if (d.Kind != Kind.Method || d.Sig == null || d.Sig.InClass || ctx.Bases == null || ctx.IsClass(d.Class)) return;
            d.Kind = Kind.Function;
            d.Chain = new List<string>(d.Sig.Chain);
            d.Class = null;
        }

        public static bool IsIdentity(int[] map, int oldCount)
        {
            if (map.Length != oldCount) return false;
            for (int j = 0; j < map.Length; j++) if (map[j] != j) return false;
            return true;
        }

        /// <summary>
        /// 呼び出しの引数 args を、新しい並びに直す。直せない(足した引数に渡す値がない、可変長)ときは null。
        /// 末尾の、既定値で省いていた引数は、省いたままにする。
        /// </summary>
        public static List<string> RewriteArgs(List<string> args, int oldCount, int[] map, bool[] newHasDefault)
        {
            if (args.Count > oldCount) return null;
            var vals = new string[map.Length];
            for (int j = 0; j < map.Length; j++)
            {
                if (map[j] >= 0 && map[j] < args.Count) vals[j] = args[map[j]];
                else if (map[j] < 0 && !newHasDefault[j]) return null;        // 足した引数に、渡す値がない
            }
            int last = vals.Length - 1;
            while (last >= 0 && vals[last] == null) last--;
            var list = new List<string>();
            for (int j = 0; j <= last; j++)
            {
                if (vals[j] == null) return null;       // 途中の引数は省けない
                list.Add(vals[j]);
            }
            return list;
        }

        /// <summary>
        /// text の中の d の呼び出しの引数を、新しい並びに直す編集。直せなかった呼び出しの位置は skipped に入る。
        /// </summary>
        public static List<Edit> CallEdits(string text, Decl d, Context ctx, bool includeAmbiguous, int oldCount, int[] map, bool[] newHasDefault, List<int> skipped)
        {
            var edits = new List<Edit>();
            var refs = MemberRefs(text, d, ctx, -1);
            if (refs.Count == 0) return edits;
            string m = CppText.Mask(text);
            var sigNames = new HashSet<int>(FunctionScan.Scan(text).Where(s => s.Name == d.Name).Select(s => NamePos(m, s)));
            foreach (var r in refs)
            {
                if (sigNames.Contains(r.Start)) continue;                    // 宣言と定義は、引数の同期が直す
                int open = Next(m, r.Start + d.Name.Length);
                if (At(m, open) != '(') continue;
                if (!r.Certain && !includeAmbiguous) { skipped.Add(r.Start); continue; }
                int close = FunctionScan.MatchClose(m, open, '(', ')');
                bool pack;
                var ranges = close < 0 ? null : CallCheck.Split(m, text, open + 1, close, out pack);
                if (ranges == null) { skipped.Add(r.Start); continue; }
                var args = ranges.Select(x => text.Substring(x[0], x[1] - x[0])).ToList();
                var rewritten = RewriteArgs(args, oldCount, map, newHasDefault);
                if (rewritten == null) { skipped.Add(r.Start); continue; }
                if (rewritten.SequenceEqual(args)) continue;
                edits.Add(new Edit { Start = open + 1, Length = close - open - 1, Text = string.Join(", ", rewritten) });
            }
            return edits;
        }

        public static string Apply(string text, IEnumerable<Edit> edits)
        {
            var sb = new System.Text.StringBuilder(text);
            foreach (var e in edits.OrderByDescending(x => x.Start)) { sb.Remove(e.Start, e.Length); sb.Insert(e.Start, e.Text); }
            return sb.ToString();
        }

        /// <summary>pos の行番号(1 から)。</summary>
        public static int LineOf(string text, int pos)
        {
            int line = 1;
            for (int i = 0; i < pos && i < text.Length; i++) if (text[i] == '\n') line++;
            return line;
        }
    }
}
