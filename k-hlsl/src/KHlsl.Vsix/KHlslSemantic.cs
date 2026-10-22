using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KHlsl.Vsix
{
    /// <summary>
    /// 識別子を、スコープごとに分類する(VS の C++ の意味的な色付けと同じ分け方)。
    /// 引数・ローカル変数・メンバー変数・メンバー関数・グローバル変数・列挙子・ラベル。
    /// 型の解決まではしない、簡易な解析。字句の段階で分類できなかった識別子だけを対象にする。
    /// </summary>
    internal static class KHlslSemantic
    {
        private sealed class Block
        {
            public int Open, Close;
            public char Kind;           // N 名前空間 / S 構造体・クラス / E 列挙型 / B cbuffer / F 関数 / P その他
            public string Name;
            public int ParenOpen = -1, ParenClose = -1;   // 関数のヘッダーの引数リスト
        }

        private static readonly Regex RxNamespace = new Regex(@"\bnamespace\s+([A-Za-z_]\w*)");
        private static readonly Regex RxStruct = new Regex(@"\b(struct|class|interface)\s+([A-Za-z_]\w*)");
        private static readonly Regex RxEnum = new Regex(@"\benum\b(?:\s+class)?\s*([A-Za-z_]\w*)?");
        private static readonly Regex RxCbuffer = new Regex(@"\b(cbuffer|tbuffer)\s+([A-Za-z_]\w*)");
        private static readonly Regex RxFuncTail = new Regex(@"\)\s*(?:const\s*)?(?::\s*\w+\s*)?$");
        private static readonly Regex RxFirstWord = new Regex(@"^\s*(?:\[[^\]]*\]\s*)*([A-Za-z_]\w*)");
        private static readonly Regex RxDecl = new Regex(
            @"(?<![\w.>])(?<t>(?:[A-Za-z_]\w*::)*[A-Za-z_]\w*)(?<g>\s*<[^;(){}]*>)?(?:\s*[&*])?\s+(?<n>[A-Za-z_]\w*)\s*(?=[=;,)\[:])");
        private static readonly Regex RxMemberFunc = new Regex(
            @"(?<![\w.>])(?<t>(?:[A-Za-z_]\w*::)*[A-Za-z_]\w*)(?<g>\s*<[^;(){}]*>)?(?:\s*[&*])?\s+(?<n>[A-Za-z_]\w*)\s*\(");
        private static readonly Regex RxMoreNames = new Regex(@"\G\s*,\s*(?<n>[A-Za-z_]\w*)\s*(?:\[[^\]]*\]\s*)*(?:=[^,;()]*)?");
        private static readonly Regex RxIdent = new Regex(@"[A-Za-z_]\w*");
        private static readonly Regex RxLabel = new Regex(@"(?:^|[;{}])[ \t\r\n]*(?<l>[A-Za-z_]\w*)[ \t]*:(?!:)", RegexOptions.Multiline);

        private static readonly HashSet<string> NotNames = new HashSet<string>
        {
            "case", "default", "public", "private", "protected", "return", "else", "register", "packoffset"
        };

        public static void Run(string text, List<Tok> toks, Lexicon lx, HashSet<string> userTypes)
        {
            int n = text.Length;
            if (n == 0) return;
            string m = Mask(text, toks);

            // ---- 1. ブロックの構造 ----
            var blocks = new List<Block>();
            var stack = new Stack<Block>();
            var parenAt = new int[n + 1];
            int paren = 0, stmtStart = 0;
            for (int i = 0; i < n; i++)
            {
                parenAt[i] = paren;
                char c = m[i];
                if (c == '(') paren++;
                else if (c == ')') { if (paren > 0) paren--; }
                else if (paren == 0)
                {
                    if (c == ';') stmtStart = i + 1;
                    else if (c == '{')
                    {
                        var b = Header(m, stmtStart, i);
                        b.Open = i;
                        b.Close = n;
                        stack.Push(b);
                        blocks.Add(b);
                        stmtStart = i + 1;
                    }
                    else if (c == '}')
                    {
                        if (stack.Count > 0) stack.Pop().Close = i;
                        stmtStart = i + 1;
                    }
                }
            }
            parenAt[n] = paren;

            Func<int, Block> innermost = p =>
            {
                Block best = null;
                foreach (var b in blocks)
                    if (b.Open < p && p < b.Close && (best == null || b.Open > best.Open)) best = b;
                return best;
            };
            Func<int, char, Block> enclosing = (p, kind) =>
            {
                Block best = null;
                foreach (var b in blocks)
                    if (b.Kind == kind && b.Open < p && p < b.Close && (best == null || b.Open > best.Open)) best = b;
                return best;
            };
            Func<int, Block> paramsOf = p =>
            {
                foreach (var b in blocks)
                    if (b.Kind == 'F' && b.ParenOpen >= 0 && b.ParenOpen < p && p < b.ParenClose) return b;
                return null;
            };

            Func<string, bool> isTypeWord = t =>
            {
                string last = t.Contains("::") ? t.Substring(t.LastIndexOf("::", StringComparison.Ordinal) + 2) : t;
                if (NotNames.Contains(last) || lx.Control.Contains(last)) return false;
                return KHlslLexer.IsVecMat(last) || lx.ScalarTypes.Contains(last) || lx.ResourceTypes.Contains(t)
                    || lx.ResourceTypes.Contains(last) || userTypes.Contains(last) || last == "auto"
                    || last == "unsigned" || last == "signed" || last == "long" || last == "short" || last == "char";
            };

            // ---- 2. 宣言を集める ----
            var globals = new HashSet<string>();
            var allMembers = new HashSet<string>();
            var membersOf = new Dictionary<Block, HashSet<string>>();
            var memberFuncs = new HashSet<string>();
            var memberFuncsOf = new Dictionary<Block, HashSet<string>>();
            var locals = new Dictionary<Block, Dictionary<string, int>>();
            var paramNames = new Dictionary<Block, HashSet<string>>();
            var declOnlyParams = new HashSet<int>();
            var enumerators = new HashSet<string>();
            var labels = new HashSet<string>();

            foreach (Match d in RxDecl.Matches(m))
            {
                if (!isTypeWord(d.Groups["t"].Value)) continue;
                var names = new List<Group> { d.Groups["n"] };
                int p0 = d.Groups["n"].Index;
                if (parenAt[p0] == 0)
                {
                    int pos = d.Index + d.Length;
                    Match more;
                    while ((more = RxMoreNames.Match(m, pos)).Success && more.Index == pos)
                    {
                        names.Add(more.Groups["n"]);
                        pos = more.Index + more.Length;
                    }
                }
                foreach (var g in names)
                {
                    string name = g.Value;
                    int p = g.Index;
                    if (NotNames.Contains(name) || lx.Control.Contains(name) || lx.Keywords.Contains(name)) continue;
                    var fp = paramsOf(p);
                    if (fp != null)
                    {
                        HashSet<string> set;
                        if (!paramNames.TryGetValue(fp, out set)) paramNames[fp] = set = new HashSet<string>();
                        set.Add(name);
                        continue;
                    }
                    var ctx = innermost(p);
                    if (ctx == null || ctx.Kind == 'N' || ctx.Kind == 'B')
                    {
                        if (parenAt[p] > 0) declOnlyParams.Add(p);
                        else globals.Add(name);
                    }
                    else if (ctx.Kind == 'S')
                    {
                        if (parenAt[p] > 0) declOnlyParams.Add(p);
                        else
                        {
                            allMembers.Add(name);
                            HashSet<string> set;
                            if (!membersOf.TryGetValue(ctx, out set)) membersOf[ctx] = set = new HashSet<string>();
                            set.Add(name);
                        }
                    }
                    else if (ctx.Kind == 'F' || ctx.Kind == 'P')
                    {
                        var fb = enclosing(p, 'F');
                        if (fb == null) continue;
                        Dictionary<string, int> dict;
                        if (!locals.TryGetValue(fb, out dict)) locals[fb] = dict = new Dictionary<string, int>();
                        if (!dict.ContainsKey(name)) dict[name] = p;
                    }
                }
            }

            foreach (Match d in RxMemberFunc.Matches(m))
            {
                string t = d.Groups["t"].Value;
                if (!isTypeWord(t) && t != "void") continue;
                var ctx = innermost(d.Groups["n"].Index);
                if (ctx == null || ctx.Kind != 'S' || parenAt[d.Groups["n"].Index] != 0) continue;
                memberFuncs.Add(d.Groups["n"].Value);
                HashSet<string> set;
                if (!memberFuncsOf.TryGetValue(ctx, out set)) memberFuncsOf[ctx] = set = new HashSet<string>();
                set.Add(d.Groups["n"].Value);
            }

            foreach (var b in blocks.Where(x => x.Kind == 'E'))
            {
                int depth = 0;
                bool expectName = true;
                for (int i = b.Open + 1; i < Math.Min(b.Close, n); i++)
                {
                    char c = m[i];
                    if (c == '(' || c == '[') depth++;
                    else if (c == ')' || c == ']') depth--;
                    else if (c == ',' && depth == 0) expectName = true;
                    else if (expectName && depth == 0 && (char.IsLetter(c) || c == '_'))
                    {
                        var id = RxIdent.Match(m, i);
                        enumerators.Add(id.Value);
                        i = id.Index + id.Length - 1;
                        expectName = false;
                    }
                }
            }

            foreach (Match l in RxLabel.Matches(m))
            {
                string name = l.Groups["l"].Value;
                if (NotNames.Contains(name) || lx.Semantics.Contains(name)) continue;
                if (enclosing(l.Groups["l"].Index, 'F') == null) continue;
                labels.Add(name);
            }

            // ---- 3. 識別子を分類する ----
            // 字句の段階で分類できなかった識別子(Identifier)だけを、付け替える対象にする
            var tokenStarts = new HashSet<int>(toks.Where(t => t.Kind != Tk.Identifier).Select(t => t.Start));
            var identIndex = new Dictionary<int, int>();
            for (int i = 0; i < toks.Count; i++) if (toks[i].Kind == Tk.Identifier) identIndex[toks[i].Start] = i;
            var added = new List<Tok>();
            Func<int, char> prevChar = p =>
            {
                int k = p - 1;
                while (k >= 0 && char.IsWhiteSpace(m[k])) k--;
                return k >= 0 ? m[k] : '\0';
            };
            Func<int, char> nextChar = p =>
            {
                int k = p;
                while (k < n && char.IsWhiteSpace(m[k])) k++;
                return k < n ? m[k] : '\0';
            };

            foreach (Match id in RxIdent.Matches(m))
            {
                int p = id.Index;
                if (p > 0 && (char.IsLetterOrDigit(m[p - 1]) || m[p - 1] == '_')) continue;
                if (tokenStarts.Contains(p)) continue;
                string w = id.Value;
                char prev = prevChar(p);
                Tk? kind = null;

                bool arrow = prev == '>' && PrevTwo(m, p) == "->";
                if (declOnlyParams.Contains(p)) kind = Tk.Param;
                else if (prev == '.' || arrow)
                {
                    if (allMembers.Contains(w)) kind = Tk.Member;
                }
                else
                {
                    var fb = enclosing(p, 'F');
                    int declPos;
                    Dictionary<string, int> dict;
                    HashSet<string> pset;
                    var fpb = paramsOf(p);
                    if (fpb != null && paramNames.TryGetValue(fpb, out pset) && pset.Contains(w)) kind = Tk.Param;
                    else if (fb != null && locals.TryGetValue(fb, out dict) && dict.TryGetValue(w, out declPos) && declPos <= p) kind = Tk.Local;
                    else if (fb != null && paramNames.TryGetValue(fb, out pset) && pset.Contains(w)) kind = Tk.Param;
                    else
                    {
                        var sb = enclosing(p, 'S');
                        HashSet<string> mset;
                        // 構造体・クラスの中では、継承したメンバーも、メンバーとして扱う(継承元は、同じ名前のメンバーで近似する)
                        if (sb != null && ((membersOf.TryGetValue(sb, out mset) && mset.Contains(w)) || allMembers.Contains(w))) kind = Tk.Member;
                        else if (labels.Contains(w) && fb != null) kind = Tk.Label;
                        else if (globals.Contains(w)) kind = Tk.Global;
                        else if (enumerators.Contains(w)) kind = Tk.Enumerator;
                    }
                }
                if (!kind.HasValue) continue;
                int idx;
                if (identIndex.TryGetValue(p, out idx)) { var t = toks[idx]; t.Kind = kind.Value; toks[idx] = t; }
                else added.Add(new Tok { Start = p, Length = w.Length, Kind = kind.Value });
            }

            // 字句の段階で関数にした物のうち、メンバー関数(定義・呼び出し)を付け替える
            for (int i = 0; i < toks.Count; i++)
            {
                if (toks[i].Kind != Tk.Function) continue;
                var t = toks[i];
                string name = text.Substring(t.Start, t.Length);
                bool member = prevChar(t.Start) == '.';
                if (!member && memberFuncs.Contains(name) && enclosing(t.Start, 'S') != null) member = true;
                if (member) { t.Kind = Tk.MemberFunc; toks[i] = t; }
            }

            if (added.Count > 0)
            {
                toks.AddRange(added);
                toks.Sort((x, y) => x.Start.CompareTo(y.Start));
            }
        }

        /// <summary>コメント・文字列・プリプロセッサ行を空白にした文字列(位置は変えない)。</summary>
        private static string Mask(string text, List<Tok> toks)
        {
            var sb = new StringBuilder(text);
            Action<int, int> blank = (s, len) =>
            {
                for (int i = s; i < s + len && i < sb.Length; i++)
                    if (sb[i] != '\n' && sb[i] != '\r') sb[i] = ' ';
            };
            foreach (var t in toks)
            {
                if (t.Kind == Tk.Comment || t.Kind == Tk.String || t.Kind == Tk.Escape || t.Kind == Tk.Format || t.Kind == Tk.StringDelim)
                    blank(t.Start, t.Length);
                else if (t.Kind == Tk.Preprocessor && text[t.Start] == '#')
                {
                    // ディレクティブの行(\ で続く行を含む)を空白にする
                    int e = t.Start;
                    while (e < text.Length)
                    {
                        int nl = text.IndexOf('\n', e);
                        if (nl < 0) { e = text.Length; break; }
                        int back = nl - 1;
                        if (back >= 0 && text[back] == '\r') back--;
                        if (back >= t.Start && text[back] == '\\') { e = nl + 1; continue; }
                        e = nl;
                        break;
                    }
                    blank(t.Start, e - t.Start);
                }
            }
            return sb.ToString();
        }

        private static string PrevTwo(string m, int p)
        {
            int k = p - 1;
            while (k >= 0 && char.IsWhiteSpace(m[k])) k--;
            return k >= 1 ? m.Substring(k - 1, 2) : "";
        }

        private static Block Header(string m, int start, int open)
        {
            string header = m.Substring(start, open - start);
            string trimmed = header.Trim();
            var b = new Block { Kind = 'P' };
            Match x;
            if (trimmed.IndexOf('=') < 0 && (x = RxNamespace.Match(trimmed)).Success) { b.Kind = 'N'; b.Name = x.Groups[1].Value; return b; }
            if (trimmed.IndexOf('=') < 0 && trimmed.IndexOf('(') < 0 && (x = RxStruct.Match(trimmed)).Success) { b.Kind = 'S'; b.Name = x.Groups[2].Value; return b; }
            if (trimmed.IndexOf('=') < 0 && trimmed.IndexOf('(') < 0 && (x = RxEnum.Match(trimmed)).Success) { b.Kind = 'E'; b.Name = x.Groups[1].Value; return b; }
            if ((x = RxCbuffer.Match(trimmed)).Success) { b.Kind = 'B'; b.Name = x.Groups[2].Value; return b; }
            if (trimmed.Length > 0 && RxFuncTail.IsMatch(trimmed))
            {
                var fw = RxFirstWord.Match(trimmed);
                string first = fw.Success ? fw.Groups[1].Value : "";
                if (first != "if" && first != "for" && first != "while" && first != "switch" && first != "catch" && first != "else" && first != "do" && first != "try")
                {
                    // 最後の ) に対応する ( を、後ろから探す
                    int close = -1;
                    for (int i = header.Length - 1; i >= 0; i--) if (header[i] == ')') { close = i; break; }
                    if (close >= 0)
                    {
                        int depth = 0, openIdx = -1;
                        for (int i = close; i >= 0; i--)
                        {
                            if (header[i] == ')') depth++;
                            else if (header[i] == '(') { depth--; if (depth == 0) { openIdx = i; break; } }
                        }
                        if (openIdx >= 0)
                        {
                            b.Kind = 'F';
                            b.ParenOpen = start + openIdx;
                            b.ParenClose = start + close;
                        }
                    }
                }
            }
            return b;
        }
    }
}
