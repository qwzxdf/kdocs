using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// クラスの本体を文に分けて、データ メンバー(型・名前・配列)と、関数の宣言を集める。VS に依存しない。
    /// 生成の機能(特殊メンバー関数、formatter、入力レイアウト、定数バッファの並び…)が共通に使う。
    /// </summary>
    internal static class MemberScan
    {
        public sealed class Member
        {
            public string Type;       // 「const float」「std::vector<int>」。初期化子と配列は含まない
            public string Name;
            public string Array = ""; // 「[4]」「[2][3]」。配列でなければ空
            public string Access;     // public / protected / private
            public int Start;         // 文の頭(空白を除く)
            public int End;           // 文の「;」の位置
        }

        public sealed class ClassInfo
        {
            public Scopes.Scope Scope;
            public string Name;
            public bool IsStruct;
            public List<Member> Members = new List<Member>();
            public List<string> Functions = new List<string>();   // 関数の宣言・定義の頭(本体は含まない。空白は 1 つにそろえる)
            public bool HasVirtual;
            public bool HasUserCtor;                              // コピー・ムーブ以外のコンストラクターがある
            public List<string> Qualified = new List<string>();   // 囲んでいる namespace とクラスと、自分の名前(外側から順)

            public string FullName { get { return string.Join("::", Qualified); } }
        }

        private static readonly Regex Skip = new Regex(
            @"^(?:static|using|typedef|friend|template|virtual|inline|constexpr|consteval|constinit|extern|enum|class|struct|union|namespace|operator|explicit|static_assert|thread_local|NLOHMANN_\w+|[A-Z][A-Z0-9_]*\s*\()\b",
            RegexOptions.Compiled);

        /// <summary>caret の位置のクラス。本体の中か、「class X」「struct X」の頭の行にあれば、そのクラス。なければ null。</summary>
        public static ClassInfo At(string text, int caret)
        {
            var scopes = Scopes.Parse(text);
            var cls = scopes.Where(s => s.IsClass && s.Open < caret && caret <= s.Close).OrderByDescending(s => s.Open).FirstOrDefault();
            if (cls == null)
            {
                // 「struct Vertex {」の行や、「{」の前の行にカーソルがあるとき
                int ls = LineStart(text, caret);
                int le = text.IndexOf('\n', caret);
                if (le < 0) le = text.Length;
                cls = scopes.Where(s => s.IsClass && s.Open >= ls && LineStart(text, s.Open) <= le + 1 && HeadOn(text, ls, le, s.Name)).OrderBy(s => s.Open).FirstOrDefault();
            }
            return cls == null ? null : Of(text, cls, scopes);
        }

        private static bool HeadOn(string text, int ls, int le, string name)
        {
            string line = text.Substring(ls, le - ls);
            return Regex.IsMatch(line, @"\b(?:class|struct)\b[^;]*\b" + Regex.Escape(name) + @"\b");
        }

        public static ClassInfo Of(string text, Scopes.Scope cls, List<Scopes.Scope> scopes = null)
        {
            string m = CppText.Mask(text);
            var info = new ClassInfo { Scope = cls, Name = cls.Name, IsStruct = cls.IsStruct };
            info.Qualified = cls.Chain();
            string access = cls.IsStruct ? "public" : "private";

            int st = cls.Open + 1;
            for (int i = cls.Open + 1; i < cls.Close; i++)
            {
                char c = m[i];
                if (c == ':' && (i + 1 >= m.Length || m[i + 1] != ':') && m[i - 1] != ':')
                {
                    Match lab = Regex.Match(m.Substring(st, i - st), @"^\s*(public|private|protected)\s*$");
                    if (lab.Success) { access = lab.Groups[1].Value; st = i + 1; continue; }
                }
                if (c == '{')
                {
                    string prefix = m.Substring(st, i - st);
                    int close = Scopes.MatchBrace(m, i);
                    if (close < 0 || close > cls.Close) break;
                    if (Regex.IsMatch(prefix, @"\b(?:class|struct|enum|union|namespace)\b") && !prefix.Contains("="))
                    {
                        // 入れ子の型。「struct { … } name;」の宣言子は、「;」まで読み飛ばす
                        int semi = m.IndexOf(';', close);
                        i = semi < 0 || semi > cls.Close ? close : semi;
                        st = i + 1;
                        continue;
                    }
                    if (CtorGen.ParenOutsideAngles(prefix) && !HasTopEquals(prefix))
                    {
                        AddFunction(info, prefix);
                        // 初期化子リストの「a{1}, b{2}」の後ろに本体が続く。本体の「}」まで進める
                        int e = close;
                        while (true)
                        {
                            int k = e + 1;
                            while (k < cls.Close && char.IsWhiteSpace(m[k])) k++;
                            if (k < cls.Close && m[k] == '{') { e = Scopes.MatchBrace(m, k); if (e < 0) e = cls.Close; break; }
                            if (k < cls.Close && m[k] == ',')
                            {
                                int n = k;
                                while (n < cls.Close && m[n] != '{' && m[n] != ';') n++;
                                if (n >= cls.Close || m[n] == ';') { e = n; break; }
                                e = Scopes.MatchBrace(m, n);
                                if (e < 0) { e = cls.Close; break; }
                                continue;
                            }
                            break;
                        }
                        i = e; st = e + 1;
                        if (st < cls.Close && m[st] == ';') { i = st; st++; }
                        continue;
                    }
                    i = close;   // 「int a{0};」の初期化子
                    continue;
                }
                if (c == '(')
                {
                    int depth = 0, k = i;
                    for (; k < cls.Close; k++)
                    {
                        if (m[k] == '(') depth++;
                        else if (m[k] == ')') { depth--; if (depth == 0) break; }
                    }
                    i = k;
                    continue;
                }
                if (c != ';') continue;

                string stmt = m.Substring(st, i - st);
                int stmtStart = st + (stmt.Length - stmt.TrimStart().Length);
                st = i + 1;
                string flat = Regex.Replace(stmt, @"\s+", " ").Trim();
                if (flat.Length == 0) continue;
                if (CtorGen.ParenOutsideAngles(CutInitializer(flat)))
                {
                    AddFunction(info, flat);
                    continue;
                }
                if (Skip.IsMatch(flat) || flat.Contains("~")) continue;
                string decl = CutInitializerAll(flat);
                if (Regex.IsMatch(decl, @"(?<!:):(?!:)")) continue;   // ビットフィールド
                var parts = SplitTop(decl);
                Match first = Regex.Match(parts[0].Trim(), @"^(.*?[\s&*>])\s*([A-Za-z_]\w*)\s*((?:\[[^\]]*\])*)$");
                if (!first.Success) continue;
                string type = first.Groups[1].Value.Trim();
                if (type.Length == 0 || Regex.IsMatch(type, @"^(?:public|private|protected|return|mutable)$")) continue;
                type = Regex.Replace(type, @"^mutable\s+", "");
                string baseType = Regex.Replace(type, @"\s*[*&]+$", "");
                info.Members.Add(new Member { Type = type, Name = first.Groups[2].Value, Array = first.Groups[3].Value.Replace(" ", ""), Access = access, Start = stmtStart, End = i });
                // 「float x, y, z;」の 2 つ目から。「*」は、その名前だけに付く
                for (int p = 1; p < parts.Count; p++)
                {
                    Match more = Regex.Match(parts[p].Trim(), @"^([*&]*)\s*([A-Za-z_]\w*)\s*((?:\[[^\]]*\])*)$");
                    if (!more.Success) continue;
                    string t = more.Groups[1].Value.Length > 0 ? baseType + more.Groups[1].Value : baseType;
                    info.Members.Add(new Member { Type = t, Name = more.Groups[2].Value, Array = more.Groups[3].Value.Replace(" ", ""), Access = access, Start = stmtStart, End = i });
                }
            }
            return info;
        }

        private static void AddFunction(ClassInfo info, string prefix)
        {
            string flat = Regex.Replace(prefix, @"\s+", " ").Trim();
            info.Functions.Add(flat);
            if (Regex.IsMatch(flat, @"\bvirtual\b") || Regex.IsMatch(flat, @"\boverride\b")) info.HasVirtual = true;
            Match ctor = Regex.Match(flat, @"(?:^|[\s:;])(?:explicit\s+|constexpr\s+)*" + Regex.Escape(info.Name) + @"\s*\(([^)]*)\)");
            if (ctor.Success && !flat.Contains("~" + info.Name) && !Regex.IsMatch(ctor.Groups[1].Value, @"\b" + Regex.Escape(info.Name) + @"\s*&")) info.HasUserCtor = true;
        }

        /// <summary>「Foo(const Foo&amp;)」のような関数が、クラスにすでにあるか(空白は無視)。</summary>
        public static bool HasFunction(ClassInfo info, string pattern)
        {
            var rx = new Regex(pattern);
            return info.Functions.Any(f => rx.IsMatch(f));
        }

        private static bool HasTopEquals(string s)
        {
            int depth = 0;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '(' || c == '<' || c == '[') depth++;
                else if (c == ')' || c == '>' || c == ']') depth--;
                else if (c == '=' && depth == 0)
                {
                    char prev = i > 0 ? s[i - 1] : ' ';
                    char next = i + 1 < s.Length ? s[i + 1] : ' ';
                    if (prev == '=' || prev == '!' || prev == '<' || prev == '>' || next == '=') continue;
                    if (IsOperatorName(s, i)) continue;
                    return true;
                }
            }
            return false;
        }

        /// <summary>最初の初期化子(「=」か「{」)より前。</summary>
        private static string CutInitializer(string s)
        {
            int depth = 0;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '<' || c == '[') depth++;
                else if (c == '>' || c == ']') depth--;
                else if (depth == 0 && (c == '=' || c == '{') && !IsOperatorName(s, i)) return s.Substring(0, i).Trim();
            }
            return s.Trim();
        }

        /// <summary>s[i] の「=」が、「operator=」「operator+=」の名前の一部か。</summary>
        private static bool IsOperatorName(string s, int i)
        {
            return Regex.IsMatch(s.Substring(0, i), @"\boperator\s*[+\-*/%^&|<>!=]*\s*$");
        }

        /// <summary>「float x = 1, y{2}, z;」から、各宣言子の初期化子を除いて「float x, y, z」にする。</summary>
        private static string CutInitializerAll(string s)
        {
            var parts = SplitTop(s);
            return string.Join(",", parts.Select(CutInitializer));
        }

        /// <summary>括弧・山括弧・波括弧の外の「,」で分ける。</summary>
        public static List<string> SplitTop(string s)
        {
            var list = new List<string>();
            int depth = 0, start = 0;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '<' || c == '(' || c == '[' || c == '{') depth++;
                else if (c == '>' || c == ')' || c == ']' || c == '}') depth--;
                else if (c == ',' && depth == 0) { list.Add(s.Substring(start, i - start)); start = i + 1; }
            }
            list.Add(s.Substring(start));
            return list;
        }

        public static int LineStart(string text, int pos)
        {
            int i = Math.Min(pos, text.Length);
            while (i > 0 && text[i - 1] != '\n') i--;
            return i;
        }

        public static int LineEnd(string text, int pos)
        {
            int i = text.IndexOf('\n', Math.Min(pos, text.Length));
            if (i < 0) return text.Length;
            return i > 0 && text[i - 1] == '\r' ? i - 1 : i;
        }

        public static string Indent(string text, int pos)
        {
            int ls = LineStart(text, pos);
            int e = ls;
            while (e < text.Length && (text[e] == ' ' || text[e] == '\t')) e++;
            return text.Substring(ls, e - ls);
        }
    }
}
