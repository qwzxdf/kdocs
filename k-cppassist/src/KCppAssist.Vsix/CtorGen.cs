using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// クラスのデータ メンバーから、初期化リストつきのコンストラクターを作る。VS に依存しない。
    /// 静的メンバー、関数、using、friend、ビットフィールド、配列は対象にしない。
    /// </summary>
    internal static class CtorGen
    {
        public sealed class Plan
        {
            public int Position;
            public string Text;
            public string ClassName;
            public int Count;
        }

        private sealed class Member { public string Type, Name, Param, ParamType, Init; }

        private static readonly Regex Skip = new Regex(
            @"^(?:static|using|typedef|friend|template|virtual|inline|constexpr|consteval|constinit|mutable|extern|enum|class|struct|union|namespace|operator|explicit|static_assert|thread_local)\b",
            RegexOptions.Compiled);

        private static readonly Regex Builtin = new Regex(
            @"^(?:(?:unsigned|signed|long|short)\s+)*(?:bool|char|char8_t|char16_t|char32_t|wchar_t|int|float|double|size_t|ptrdiff_t|intptr_t|uintptr_t|(?:std::)?u?int(?:8|16|32|64)_t|(?:std::)?(?:size_t|ptrdiff_t|byte|string_view|wstring_view|u8string_view|nullptr_t))$|^(?:unsigned|signed|long|short)(?:\s+(?:unsigned|signed|long|short|int))*$",
            RegexOptions.Compiled);

        private static readonly HashSet<string> Keywords = new HashSet<string>
        {
            "new","delete","class","struct","int","float","double","bool","char","long","short","unsigned","signed","this",
            "default","switch","case","do","if","else","for","while","return","operator","template","typename","namespace","register","auto","const","static","void"
        };

        public static Plan Make(string text, int caret, string eol, out string why)
        {
            why = null;
            string m = CppText.Mask(text);
            var scopes = Scopes.Parse(text);
            var cls = scopes.Where(s => s.IsClass && s.Open < caret && caret <= s.Close).OrderByDescending(s => s.Open).FirstOrDefault();
            if (cls == null) { why = "カーソルが、class / struct の中にありません"; return null; }
            if (LineStart(text, cls.Open) == LineStart(text, cls.Close)) { why = "クラスが 1 行に書かれています。複数行に広げてください"; return null; }

            var members = new List<Member>();
            var ctorCounts = new List<int>();
            int firstPublicLabelEnd = -1, firstLabelStart = -1, firstStmt = -1;
            bool refused = false;
            string refuseReason = null;

            int st = cls.Open + 1;
            for (int i = cls.Open + 1; i < cls.Close; i++)
            {
                char c = m[i];
                if (c == ':' && (i + 1 >= m.Length || m[i + 1] != ':') && (i == 0 || m[i - 1] != ':'))
                {
                    Match lab = Regex.Match(m.Substring(st, i - st), @"^\s*(public|private|protected)\s*$");
                    if (lab.Success)
                    {
                        if (firstLabelStart < 0) firstLabelStart = st + lab.Groups[1].Index;
                        if (lab.Groups[1].Value == "public" && firstPublicLabelEnd < 0) firstPublicLabelEnd = i + 1;
                        st = i + 1;
                        continue;
                    }
                }
                if (c == '{')
                {
                    string prefix = m.Substring(st, i - st);
                    int close = Scopes.MatchBrace(m, i);
                    if (close < 0 || close > cls.Close) break;
                    if (Regex.IsMatch(prefix, @"\b(?:class|struct|enum|union|namespace)\b") && !prefix.Contains("=") )
                    {
                        i = close; st = close + 1; continue;
                    }
                    if (prefix.Contains("(") && !HasTopEquals(prefix))
                    {
                        // 関数(本体つき)。コンストラクターの初期化リストの「b{2}」の後ろに本体が続くので、そこまで読み進める
                        RecordFunction(prefix, ctorCounts, cls.Name);
                        int e = close;
                        while (true)
                        {
                            int k = e + 1;
                            while (k < cls.Close && char.IsWhiteSpace(m[k])) k++;
                            if (k < cls.Close && m[k] == '{') { e = Scopes.MatchBrace(m, k); if (e < 0) { e = cls.Close; } break; }
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
                        if (st < cls.Close && m[st] == ';') { i = st; st = st + 1; }
                        continue;
                    }
                    i = close;     // メンバーの初期化子「int a{0};」。文は「;」まで続く
                    continue;
                }
                if (c == '(')
                {
                    // 括弧の中の「;」「{」は、文の区切りにしない
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
                int stmtStart = st;
                st = i + 1;
                string orig = Regex.Replace(stmt, @"\s+", " ").Trim();
                if (orig.Length == 0) continue;
                if (firstStmt < 0) firstStmt = stmtStart + (stmt.Length - stmt.TrimStart().Length);

                if (orig.Contains("(")) { RecordFunction(orig, ctorCounts, cls.Name); if (!HasTopEquals(orig)) continue; }
                if (Skip.IsMatch(orig) || orig.Contains("~")) continue;

                string decl = CutInitializer(orig);
                if (decl.Contains("(")) continue;                       // 関数ポインターなど
                if (Regex.IsMatch(decl, @"(?<!:):(?!:)")) continue;     // ビットフィールド
                if (TopComma(decl)) { refused = true; refuseReason = "1 行に複数のメンバーを宣言している行があります: " + orig; break; }
                if (Regex.IsMatch(decl, @"\]\s*$")) continue;           // 配列

                Match dm = Regex.Match(decl, @"^(.*?[\s&*>])([A-Za-z_]\w*)$");
                if (!dm.Success) continue;
                string type = dm.Groups[1].Value.Trim();
                string name = dm.Groups[2].Value;
                if (type.Length == 0 || Skip.IsMatch(type) || Regex.IsMatch(type, @"^(?:public|private|protected)\b")) continue;
                members.Add(new Member { Type = type, Name = name });
            }
            if (refused) { why = refuseReason; return null; }
            if (members.Count == 0) { why = "データ メンバーが見つかりません"; return null; }

            // ---- 引数の名前と型 ----
            var used = new HashSet<string>(StringComparer.Ordinal);
            foreach (var mem in members)
            {
                string p = mem.Name;
                if (p.StartsWith("m_", StringComparison.Ordinal) && p.Length > 2) p = p.Substring(2);
                p = p.TrimEnd('_');
                if (p.Length == 0 || Keywords.Contains(p)) p = mem.Name.Trim('_') + "_value";
                if (p.Length == 0 || Keywords.Contains(p)) p = "value";
                string cand = p; int n = 2;
                while (!used.Add(cand)) cand = p + n++;
                mem.Param = cand;
                ParamTypeOf(mem);
            }

            if (ctorCounts.Contains(members.Count) && !(members.Count == 1 && !ctorCounts.Contains(1)))
            {
                why = "引数が " + members.Count + " 個のコンストラクターが、すでにあります";
                return null;
            }

            // ---- 字下げ ----
            string classIndent = LeadingSpace(text, cls.Open);
            if (text.Substring(LineStart(text, cls.Open), cls.Open - LineStart(text, cls.Open)).Trim().Length == 0)
            {
                // 「{」だけの行。クラス名の行の字下げを使う
                int prev = LineStart(text, cls.Open) - 1;
                if (prev > 0) classIndent = LeadingSpace(text, prev - 1 < 0 ? 0 : prev - 1);
            }
            string indent = firstStmt >= 0 ? LeadingSpace(text, firstStmt) : classIndent + "  ";
            if (indent.Length <= classIndent.Length) indent = classIndent + "  ";
            string labelIndent = firstLabelStart >= 0 ? LeadingSpace(text, firstLabelStart) : classIndent + " ";

            string ctor = Build(cls.Name, members, indent, eol);

            // ---- 挿入する位置 ----
            int pos;
            string outText;
            if (firstPublicLabelEnd >= 0)
            {
                pos = NextLineStart(text, firstPublicLabelEnd);
                outText = ctor + eol;
            }
            else if (cls.IsStruct)
            {
                pos = NextLineStart(text, cls.Open);
                outText = ctor + eol;
            }
            else
            {
                bool startsWithLabel = firstLabelStart >= 0 && text.Substring(cls.Open + 1, firstLabelStart - cls.Open - 1).Trim().Length == 0;
                if (startsWithLabel)
                {
                    pos = LineStart(text, firstLabelStart);
                    outText = labelIndent + "public:" + eol + ctor + eol;
                }
                else
                {
                    pos = NextLineStart(text, cls.Open);
                    outText = labelIndent + "public:" + eol + ctor + eol + labelIndent + "private:" + eol;
                }
            }
            return new Plan { Position = pos, Text = outText, ClassName = cls.Name, Count = members.Count };
        }

        private static void RecordFunction(string s, List<int> ctorCounts, string className)
        {
            Match mm = Regex.Match(s, @"(?:^|[\s:;{}])" + Regex.Escape(className) + @"\s*\(");
            if (!mm.Success) return;
            // 「Name(」の前が「~」なら、デストラクター
            int idx = mm.Index + mm.Length - 1;
            int nameStart = s.IndexOf(className, mm.Index, StringComparison.Ordinal);
            if (nameStart > 0 && s[nameStart - 1] == '~') return;
            int depth = 0, end = -1;
            for (int k = idx; k < s.Length; k++)
            {
                if (s[k] == '(') depth++;
                else if (s[k] == ')') { depth--; if (depth == 0) { end = k; break; } }
            }
            if (end < 0) return;
            string inner = s.Substring(idx + 1, end - idx - 1).Trim();
            if (Regex.IsMatch(inner, @"\b" + Regex.Escape(className) + @"\s*&")) return;   // コピー・ムーブは、数えない
            int cnt = inner.Length == 0 || inner == "void" ? 0 : SplitComma(inner).Count();
            ctorCounts.Add(cnt);
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
                    return true;
                }
            }
            return false;
        }

        private static string CutInitializer(string s)
        {
            int depth = 0;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '<' || c == '[') depth++;
                else if (c == '>' || c == ']') depth--;
                else if (depth == 0 && (c == '=' || c == '{')) return s.Substring(0, i).Trim();
            }
            return s.Trim();
        }

        private static bool TopComma(string s)
        {
            int depth = 0;
            foreach (char c in s)
            {
                if (c == '<' || c == '(' || c == '[') depth++;
                else if (c == '>' || c == ')' || c == ']') depth--;
                else if (c == ',' && depth == 0) return true;
            }
            return false;
        }

        private static IEnumerable<string> SplitComma(string s)
        {
            int depth = 0, start = 0;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '<' || c == '(' || c == '[' || c == '{') depth++;
                else if (c == '>' || c == ')' || c == ']' || c == '}') depth--;
                else if (c == ',' && depth == 0) { yield return s.Substring(start, i - start); start = i + 1; }
            }
            yield return s.Substring(start);
        }

        private static void ParamTypeOf(Member mem)
        {
            string t = Regex.Replace(mem.Type, @"\s+", " ").Trim();
            t = Regex.Replace(t, @"\s*([&*])", "$1");           // 「int &」→「int&」
            mem.Init = mem.Param;
            if (t.EndsWith("&&", StringComparison.Ordinal)) { mem.ParamType = t; mem.Init = "std::move(" + mem.Param + ")"; return; }
            if (t.EndsWith("&", StringComparison.Ordinal) || t.EndsWith("*", StringComparison.Ordinal) || t.EndsWith("* const", StringComparison.Ordinal))
            { mem.ParamType = t; return; }
            string bare = Regex.Replace(t, @"^(?:const\s+)|(?:\s+const)$", "").Trim();
            if (Builtin.IsMatch(bare)) { mem.ParamType = bare; return; }
            if (Regex.IsMatch(bare, @"^(?:std::)?(?:unique_ptr|shared_ptr)\s*<")) { mem.ParamType = bare; mem.Init = "std::move(" + mem.Param + ")"; return; }
            mem.ParamType = "const " + bare + "&";
        }

        private static string Build(string name, List<Member> ms, string indent, string eol)
        {
            string ex = ms.Count == 1 ? "explicit " : "";
            var ps = ms.Select(x => x.ParamType + " " + x.Param).ToList();
            var inits = ms.Select(x => x.Name + "(" + x.Init + ")").ToList();
            string head = indent + ex + name + "(";
            const int Limit = 80;

            var sb = new StringBuilder();
            string oneLine = head + string.Join(", ", ps) + ") : " + string.Join(", ", inits) + " {}";
            if (oneLine.Length <= Limit) return oneLine + eol;

            string sig = head + string.Join(", ", ps) + ")";
            string cont = indent + "    : ";
            if (sig.Length <= Limit)
            {
                sb.Append(sig).Append(eol);
            }
            else
            {
                string pad = new string(' ', head.Length);
                for (int i = 0; i < ps.Count; i++)
                {
                    sb.Append(i == 0 ? head : pad).Append(ps[i]).Append(i == ps.Count - 1 ? ")" : ",").Append(eol);
                }
            }
            string joined = cont + string.Join(", ", inits) + " {}";
            if (joined.Length <= Limit) { sb.Append(joined).Append(eol); return sb.ToString(); }
            string pad2 = indent + "      ";
            for (int i = 0; i < inits.Count; i++)
            {
                sb.Append(i == 0 ? cont : pad2).Append(inits[i]).Append(i == inits.Count - 1 ? " {}" : ",").Append(eol);
            }
            return sb.ToString();
        }

        private static int LineStart(string text, int pos)
        {
            int i = Math.Min(pos, text.Length);
            while (i > 0 && text[i - 1] != '\n') i--;
            return i;
        }

        private static int NextLineStart(string text, int pos)
        {
            int i = text.IndexOf('\n', Math.Min(pos, text.Length));
            return i < 0 ? text.Length : i + 1;
        }

        private static string LeadingSpace(string text, int pos)
        {
            int ls = LineStart(text, pos);
            int e = ls;
            while (e < text.Length && (text[e] == ' ' || text[e] == '\t')) e++;
            return text.Substring(ls, e - ls);
        }
    }
}
