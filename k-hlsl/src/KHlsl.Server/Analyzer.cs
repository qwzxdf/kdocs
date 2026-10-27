using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KHlsl.Server
{
    internal enum SymKind { Function, Struct, CBuffer, Namespace, Enum, Variable, Macro, TypeAlias }

    internal sealed class Sym
    {
        public SymKind Kind;
        public string Name;
        public string Type;       // 変数の型 / 関数の戻り値
        public string Container;  // 所属する struct / cbuffer / namespace の名前
        public string Params;     // 関数の引数リスト(かっこの中)
        public string Value;      // マクロの本体
        public string File;
        public int Line;
        public int Col;
        public int Offset;
        public bool IsParam;
        public bool Local;        // 関数の本体の中で宣言された
        public int ScopeStart = -1;
        public int ScopeEnd = -1;

        public string Signature
        {
            get
            {
                switch (Kind)
                {
                    case SymKind.Function: return (Type + " " + Name + "(" + Params + ")").Trim();
                    case SymKind.Struct: return "struct " + Name;
                    case SymKind.CBuffer: return "cbuffer " + Name;
                    case SymKind.Namespace: return "namespace " + Name;
                    case SymKind.Enum: return "enum " + Name;
                    case SymKind.Macro: return "#define " + Name + (Params != null ? "(" + Params + ")" : "") + (string.IsNullOrWhiteSpace(Value) ? "" : " " + Value.Trim());
                    case SymKind.TypeAlias: return "typedef " + Type + " " + Name;
                    default: return (Type + " " + Name).Trim();
                }
            }
        }
    }

    internal sealed class FileScan
    {
        public string Path;
        public List<Sym> Syms = new List<Sym>();
        public List<string> Includes = new List<string>();
    }

    internal static class Analyzer
    {
        private static readonly HashSet<string> NotType = new HashSet<string>
        {
            "return", "else", "case", "goto", "new", "delete", "typedef", "using", "namespace", "struct", "class",
            "interface", "cbuffer", "tbuffer", "enum", "if", "while", "for", "switch", "do", "sizeof", "default",
            "in", "out", "inout", "const", "static", "uniform", "extern", "volatile", "shared", "groupshared",
            "inline", "precise", "linear", "centroid", "nointerpolation", "noperspective", "sample", "row_major",
            "column_major", "export", "register", "packoffset", "break", "continue", "discard", "template",
            "operator", "public", "private", "protected", "unsigned", "snorm", "unorm", "globallycoherent",
            "reordercoherent", "payload", "vertices", "indices", "primitives", "perprimitive", "pervertex",
            "triangle", "line", "point", "lineadj", "triangleadj", "true", "false", "this"
        };

        /// <summary>コメントと文字列の中身を空白にする。改行と位置は保つ。</summary>
        public static string Mask(string t)
        {
            var sb = new StringBuilder(t.Length);
            int i = 0, n = t.Length;
            while (i < n)
            {
                char c = t[i];
                if (c == '/' && i + 1 < n && t[i + 1] == '/')
                {
                    while (i < n && t[i] != '\n')
                    {
                        // 行末の \ で続く
                        if (t[i] == '\\' && i + 1 < n && (t[i + 1] == '\n' || t[i + 1] == '\r'))
                        {
                            sb.Append(' ');
                            i++;
                            if (t[i] == '\r' && i + 1 < n && t[i + 1] == '\n') { sb.Append('\r'); i++; }
                            sb.Append('\n'); i++;
                            continue;
                        }
                        sb.Append(t[i] == '\r' ? '\r' : ' ');
                        i++;
                    }
                }
                else if (c == '/' && i + 1 < n && t[i + 1] == '*')
                {
                    sb.Append("  "); i += 2;
                    while (i < n && !(t[i] == '*' && i + 1 < n && t[i + 1] == '/'))
                    {
                        sb.Append(t[i] == '\n' || t[i] == '\r' ? t[i] : ' ');
                        i++;
                    }
                    if (i < n) { sb.Append("  "); i += 2; }
                }
                else if (c == '"' || c == '\'')
                {
                    // #include "x" の x を消さないよう、ここでは中身だけ空白にする
                    sb.Append(c); i++;
                    while (i < n && t[i] != c && t[i] != '\n')
                    {
                        if (t[i] == '\\' && i + 1 < n) { sb.Append("  "); i += 2; continue; }
                        sb.Append(' '); i++;
                    }
                    if (i < n && t[i] == c) { sb.Append(c); i++; }
                }
                else { sb.Append(c); i++; }
            }
            return sb.ToString();
        }

        private static readonly Regex RxTypeDecl = new Regex(@"\b(struct|class|interface|cbuffer|tbuffer|namespace|enum)\s+(?:class\s+)?([A-Za-z_]\w*)", RegexOptions.Compiled);
        private static readonly Regex RxFunc = new Regex(@"(?<![\w.])(?<ret>[A-Za-z_][\w:]*(?:\s*<[^<>;(){}]*(?:<[^<>;(){}]*>[^<>;(){}]*)*>)?)\s+(?<name>[A-Za-z_]\w*(?:::\w+)*)\s*\(", RegexOptions.Compiled);
        private static readonly Regex RxVar = new Regex(@"(?<![\w.])(?<type>[A-Za-z_][\w:]*(?:\s*<[^<>;(){}]*(?:<[^<>;(){}]*>[^<>;(){}]*)*>)?)(?:\s*\*)?\s+(?<name>[A-Za-z_]\w*)\s*(?:\[[^\]]*\]\s*)*(?=[;=,:)\[])", RegexOptions.Compiled);
        private static readonly Regex RxDefine = new Regex(@"^[ \t]*#[ \t]*define[ \t]+(?<name>[A-Za-z_]\w*)(?<p>\([^)\r\n]*\))?(?<v>[^\r\n]*)", RegexOptions.Compiled | RegexOptions.Multiline);
        private static readonly Regex RxInclude = new Regex(@"^[ \t]*#[ \t]*include[ \t]*[""<](?<f>[^"">\r\n]+)["">]", RegexOptions.Compiled | RegexOptions.Multiline);
        private static readonly Regex RxTypedef = new Regex(@"\btypedef\s+(?<t>[^;{}]+?)\s+(?<n>[A-Za-z_]\w*)\s*;", RegexOptions.Compiled);

        /// <summary>1 ファイルのシンボルを集める。</summary>
        public static FileScan Scan(string path, string text)
        {
            var scan = new FileScan { Path = path };
            string m = Mask(text);
            var lineStarts = LineStarts(text);

            foreach (Match x in RxInclude.Matches(text)) scan.Includes.Add(x.Groups["f"].Value);

            // ブロックの種類(型 / その他)を押さえる
            var blocks = new List<Block>();
            var stack = new Stack<Block>();
            var declAt = new Dictionary<int, Match>();
            foreach (Match x in RxTypeDecl.Matches(m)) declAt[x.Index] = x;
            var inOther = new bool[m.Length + 1];
            int otherDepth = 0;
            var typeMatches = RxTypeDecl.Matches(m).Cast<Match>().ToList();
            int tmi = 0;
            Match pendingDecl = null;
            for (int i = 0; i < m.Length; i++)
            {
                char c = m[i];
                if (c == ';' ) pendingDecl = null;
                while (tmi < typeMatches.Count && typeMatches[tmi].Index + typeMatches[tmi].Length <= i)
                {
                    pendingDecl = typeMatches[tmi]; tmi++;
                }
                if (c == '{')
                {
                    bool isType = false;
                    if (pendingDecl != null)
                    {
                        string between = m.Substring(pendingDecl.Index + pendingDecl.Length, i - (pendingDecl.Index + pendingDecl.Length));
                        if (Regex.IsMatch(between, @"^\s*(?::\s*[\w:,\s<>]+)?\s*$") || between.Trim().Length == 0 || Regex.IsMatch(between, @"^\s*:\s*[\w:,\s]+$")) isType = true;
                        // cbuffer Name : register(b0, space1) { ... } のように、かっこ付きの指定が入ることがある
                        else if ((pendingDecl.Groups[1].Value == "cbuffer" || pendingDecl.Groups[1].Value == "tbuffer") && between.IndexOfAny(new[] { ';', '{', '}' }) < 0) isType = true;
                    }
                    var b = new Block { Start = i, IsType = isType, Name = isType ? pendingDecl.Groups[2].Value : null, Kind = isType ? pendingDecl.Groups[1].Value : null };
                    if (isType) pendingDecl = null;
                    stack.Push(b);
                    blocks.Add(b);
                    if (!isType) otherDepth++;
                }
                else if (c == '}' && stack.Count > 0)
                {
                    var b = stack.Pop();
                    b.End = i;
                    if (!b.IsType) otherDepth--;
                }
                inOther[i] = otherDepth > 0;
            }
            foreach (var b in stack) b.End = m.Length;

            Func<int, Block> typeContainer = pos =>
            {
                Block best = null;
                foreach (var b in blocks)
                    if (b.IsType && b.Start < pos && pos < b.End && (best == null || b.Start > best.Start)) best = b;
                return best;
            };
            Func<int, Block> funcBlock = pos =>
            {
                Block best = null;
                foreach (var b in blocks)
                    if (!b.IsType && b.Start < pos && pos < b.End && (best == null || b.Start < best.Start)) best = b;
                return best;
            };

            // 型 / 名前空間
            foreach (var x in typeMatches)
            {
                string kw = x.Groups[1].Value;
                var s = new Sym { Name = x.Groups[2].Value, File = path, Offset = x.Groups[2].Index };
                switch (kw)
                {
                    case "cbuffer": case "tbuffer": s.Kind = SymKind.CBuffer; break;
                    case "namespace": s.Kind = SymKind.Namespace; break;
                    case "enum": s.Kind = SymKind.Enum; break;
                    default: s.Kind = SymKind.Struct; break;
                }
                Place(s, lineStarts, x.Groups[2].Index);
                var outer = typeContainer(x.Index);
                if (outer != null) s.Container = outer.Name;
                scan.Syms.Add(s);
            }

            // enum の値
            foreach (var b in blocks.Where(b => b.IsType && b.Kind == "enum"))
            {
                string body = m.Substring(b.Start + 1, Math.Max(0, b.End - b.Start - 1));
                foreach (Match ev in Regex.Matches(body, @"(?:^|,)\s*([A-Za-z_]\w*)"))
                {
                    var s = new Sym { Kind = SymKind.Variable, Name = ev.Groups[1].Value, Type = b.Name, Container = b.Name, File = path };
                    Place(s, lineStarts, b.Start + 1 + ev.Groups[1].Index);
                    scan.Syms.Add(s);
                }
            }

            // 関数
            var funcSpans = new List<int[]>();
            var paramSpans = new List<int[]>();
            foreach (Match x in RxFunc.Matches(m))
            {
                string ret = x.Groups["ret"].Value.Trim();
                string name = x.Groups["name"].Value;
                if (NotType.Contains(ret) && ret != "static" && ret != "inline" && ret != "export" && ret != "precise" && ret != "const" && ret != "unsigned") continue;
                if (inOther[x.Index]) continue;
                int open = x.Index + x.Length - 1;
                int close = MatchParen(m, open);
                if (close < 0) continue;
                // かっこの後ろ(: SEMANTIC の可能性あり)が { か ; のときだけ関数
                int j = close + 1;
                while (j < m.Length && char.IsWhiteSpace(m[j])) j++;
                if (j < m.Length && m[j] == ':' && !(j + 1 < m.Length && m[j + 1] == ':'))
                {
                    j++;
                    while (j < m.Length && (char.IsWhiteSpace(m[j]) || char.IsLetterOrDigit(m[j]) || m[j] == '_')) j++;
                }
                while (j < m.Length && char.IsWhiteSpace(m[j])) j++;
                if (j >= m.Length || (m[j] != '{' && m[j] != ';')) continue;
                // 戻り値の型の前の修飾子(static など)を落とす
                string rtype = ret;
                var s = new Sym
                {
                    Kind = SymKind.Function, Name = name, Type = rtype, File = path,
                    Params = Regex.Replace(m.Substring(open + 1, close - open - 1), @"\s+", " ").Trim()
                };
                Place(s, lineStarts, x.Groups["name"].Index);
                var cont = typeContainer(x.Index);
                if (cont != null) s.Container = cont.Name;
                if (name.Contains("::")) { s.Container = name.Substring(0, name.LastIndexOf("::", StringComparison.Ordinal)); }
                scan.Syms.Add(s);
                if (m[j] == '{')
                {
                    int bodyEnd = MatchBrace(m, j);
                    funcSpans.Add(new[] { open, bodyEnd < 0 ? m.Length : bodyEnd, scan.Syms.Count - 1 });
                }
                // 引数を変数として登録する
                paramSpans.Add(new[] { open, close });
                int pstart = open + 1;
                foreach (var p in SplitTopLevel(m.Substring(open + 1, close - open - 1), pstart))
                {
                    var pm = Regex.Match(p.Item1, @"(?<type>[A-Za-z_][\w:]*(?:\s*<[^<>]*(?:<[^<>]*>[^<>]*)*>)?)\s+(?<name>[A-Za-z_]\w*)\s*(?:\[[^\]]*\]\s*)*(?::\s*\w+\s*)?(?:=.*)?$", RegexOptions.Singleline);
                    if (!pm.Success) continue;
                    var ps = new Sym { Kind = SymKind.Variable, Name = pm.Groups["name"].Value, Type = Regex.Replace(pm.Groups["type"].Value, @"\s+", ""), File = path, IsParam = true, Local = true };
                    Place(ps, lineStarts, p.Item2 + pm.Groups["name"].Index);
                    ps.ScopeStart = open;
                    ps.ScopeEnd = m[j] == '{' ? (MatchBrace(m, j) < 0 ? m.Length : MatchBrace(m, j)) : close;
                    scan.Syms.Add(ps);
                }
            }

            // 変数(グローバル / メンバー / ローカル)
            foreach (Match x in RxVar.Matches(m))
            {
                string type = x.Groups["type"].Value;
                string name = x.Groups["name"].Value;
                string typeBase = Regex.Replace(type, @"<.*$", "").Trim();
                if (NotType.Contains(typeBase)) continue;
                if (NotType.Contains(name)) continue;
                // 関数の引数リストの中は、関数のほうで登録済み
                if (paramSpans.Any(p => x.Index > p[0] && x.Index < p[1])) continue;
                var s = new Sym { Kind = SymKind.Variable, Name = name, Type = Regex.Replace(type, @"\s+", ""), File = path };
                Place(s, lineStarts, x.Groups["name"].Index);
                var fb = funcBlock(x.Index);
                if (fb != null) { s.Local = true; s.ScopeStart = fb.Start; s.ScopeEnd = fb.End; }
                else
                {
                    var cont = typeContainer(x.Index);
                    if (cont != null) s.Container = cont.Name;
                }
                scan.Syms.Add(s);

                // float a, b = 1, c[4]; の 2 つ目以降
                int tail = x.Index + x.Length;
                if (tail < m.Length && (m[tail] == ',' || m[tail] == '='))
                {
                    int depth = 0, end = tail;
                    for (; end < m.Length; end++)
                    {
                        char ch = m[end];
                        if (ch == '(' || ch == '[' || ch == '{') depth++;
                        else if (ch == ')' || ch == ']' || ch == '}') { if (--depth < 0) break; }
                        else if (ch == ';' && depth == 0) break;
                    }
                    string rest = m.Substring(tail, end - tail);
                    foreach (var piece in SplitTopLevel(rest, tail))
                    {
                        var dm2 = Regex.Match(piece.Item1, @"^\s*\*?\s*(?<name>[A-Za-z_]\w*)\s*(?:\[[^\]]*\]\s*)*(?::\s*\w+(?:\([^)]*\))?\s*)?(?:=.*)?$", RegexOptions.Singleline);
                        if (!dm2.Success || NotType.Contains(dm2.Groups["name"].Value)) continue;
                        var s2 = new Sym { Kind = SymKind.Variable, Name = dm2.Groups["name"].Value, Type = s.Type, File = path, Container = s.Container, Local = s.Local, ScopeStart = s.ScopeStart, ScopeEnd = s.ScopeEnd };
                        Place(s2, lineStarts, piece.Item2 + dm2.Groups["name"].Index);
                        scan.Syms.Add(s2);
                    }
                }
            }

            // typedef
            foreach (Match x in RxTypedef.Matches(m))
            {
                var s = new Sym { Kind = SymKind.TypeAlias, Name = x.Groups["n"].Value, Type = Regex.Replace(x.Groups["t"].Value, @"\s+", " ").Trim(), File = path };
                Place(s, lineStarts, x.Groups["n"].Index);
                scan.Syms.Add(s);
            }

            // マクロ(コメントは消した本文を使う)
            foreach (Match x in RxDefine.Matches(m))
            {
                var s = new Sym
                {
                    Kind = SymKind.Macro, Name = x.Groups["name"].Value, File = path,
                    Params = x.Groups["p"].Success ? x.Groups["p"].Value.Trim('(', ')') : null,
                    Value = x.Groups["v"].Value.Trim()
                };
                Place(s, lineStarts, x.Groups["name"].Index);
                scan.Syms.Add(s);
            }
            return scan;
        }

        private sealed class Block { public int Start, End; public bool IsType; public string Name; public string Kind; }

        private static IEnumerable<Tuple<string, int>> SplitTopLevel(string s, int baseOffset)
        {
            int depth = 0, start = 0;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '(' || c == '<' || c == '[') depth++;
                else if (c == ')' || c == '>' || c == ']') depth--;
                else if (c == ',' && depth <= 0)
                {
                    yield return Tuple.Create(s.Substring(start, i - start), baseOffset + start);
                    start = i + 1;
                }
            }
            if (start < s.Length) yield return Tuple.Create(s.Substring(start), baseOffset + start);
        }

        private static int MatchParen(string m, int open)
        {
            int d = 0;
            for (int i = open; i < m.Length; i++)
            {
                if (m[i] == '(') d++;
                else if (m[i] == ')') { d--; if (d == 0) return i; }
                else if (m[i] == ';' || m[i] == '{' || m[i] == '}') { if (d > 0 && m[i] != ';') { } }
            }
            return -1;
        }

        private static int MatchBrace(string m, int open)
        {
            int d = 0;
            for (int i = open; i < m.Length; i++)
            {
                if (m[i] == '{') d++;
                else if (m[i] == '}') { d--; if (d == 0) return i; }
            }
            return -1;
        }

        public static List<int> LineStarts(string t)
        {
            var ls = new List<int> { 0 };
            for (int i = 0; i < t.Length; i++)
                if (t[i] == '\n') ls.Add(i + 1);
            return ls;
        }

        private static void Place(Sym s, List<int> lineStarts, int offset)
        {
            int idx = lineStarts.BinarySearch(offset);
            if (idx < 0) idx = ~idx - 1;
            s.Line = idx;
            s.Col = offset - lineStarts[idx];
            s.Offset = offset;
        }

        public static int OffsetOf(string text, int line, int col)
        {
            int off = 0, l = 0;
            while (l < line)
            {
                int nl = text.IndexOf('\n', off);
                if (nl < 0) return text.Length;
                off = nl + 1; l++;
            }
            return Math.Min(text.Length, off + col);
        }

        public static void PositionOf(string text, int offset, out int line, out int col)
        {
            line = 0; int last = 0;
            for (int i = 0; i < offset && i < text.Length; i++)
                if (text[i] == '\n') { line++; last = i + 1; }
            col = offset - last;
        }
    }
}
