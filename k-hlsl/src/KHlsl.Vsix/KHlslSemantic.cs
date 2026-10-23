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
            public int Index;
            public Block Parent;
        }

        private static readonly Regex RxNamespace = new Regex(@"\bnamespace\s+([A-Za-z_]\w*)");
        private static readonly Regex RxStruct = new Regex(@"\b(struct|class|interface)\s+(?:\[[^\]]*\]\s*)*([A-Za-z_]\w*)");
        private static readonly Regex RxEnum = new Regex(@"\benum\b(?:\s+class)?\s*(?:\[[^\]]*\]\s*)*([A-Za-z_]\w*)?");
        private static readonly Regex RxCbuffer = new Regex(@"\b(cbuffer|tbuffer)\s+([A-Za-z_]\w*)");
        private static readonly Regex RxFuncTail = new Regex(@"\)\s*(?:const\s*)?(?::\s*\w+\s*)?$");
        private static readonly Regex RxFirstWord = new Regex(@"^\s*(?:\[[^\]]*\]\s*)*([A-Za-z_]\w*)");
        private static readonly Regex RxDecl = new Regex(
            @"(?<![\w.>])(?<t>(?:[A-Za-z_]\w*::)*[A-Za-z_]\w*)(?<g>\s*<[^;(){}]*>)?(?:\s*[&*])?\s+(?<n>[A-Za-z_]\w*)\s*(?=[=;,)\[:])", RegexOptions.Compiled);
        private static readonly Regex RxMemberFunc = new Regex(
            @"(?<![\w.>])(?<t>(?:[A-Za-z_]\w*::)*[A-Za-z_]\w*)(?<g>\s*<[^;(){}]*>)?(?:\s*[&*])?\s+(?<n>[A-Za-z_]\w*)\s*\(", RegexOptions.Compiled);
        private static readonly Regex RxMoreNames = new Regex(@"\G\s*,\s*(?<n>[A-Za-z_]\w*)\s*(?:\[[^\]]*\]\s*)*(?:=[^,;()]*)?", RegexOptions.Compiled);
        private static readonly Regex RxIdent = new Regex(@"[A-Za-z_]\w*");
        private static readonly Regex RxLabel = new Regex(@"(?:^|[;{}])[ \t\r\n]*(?<l>[A-Za-z_]\w*)[ \t]*:(?!:)", RegexOptions.Multiline | RegexOptions.Compiled);

        // 組み込みの構造体のフィールド(RayDesc、BuiltInTriangleIntersectionAttributes)
        private static readonly HashSet<string> BuiltinMembers = new HashSet<string> { "Origin", "Direction", "TMin", "TMax", "barycentrics" };

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
            var ctxAt = new int[n + 1];        // その位置を含む、いちばん内側のブロックの番号(なければ -1)
            var parenOwner = new int[n + 1];   // その位置が、どの関数の引数リストの中か(なければ -1)
            for (int k = 0; k <= n; k++) parenOwner[k] = -1;
            int paren = 0, stmtStart = 0;
            for (int i = 0; i < n; i++)
            {
                parenAt[i] = paren;
                ctxAt[i] = stack.Count > 0 ? stack.Peek().Index : -1;
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
                        b.Index = blocks.Count;
                        b.Parent = stack.Count > 0 ? stack.Peek() : null;
                        if (b.Kind == 'F' && b.ParenOpen >= 0)
                            for (int k = b.ParenOpen + 1; k < b.ParenClose && k <= n; k++) parenOwner[k] = b.Index;
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
            ctxAt[n] = -1;

            Func<int, Block> innermost = p => p >= 0 && p <= n && ctxAt[p] >= 0 ? blocks[ctxAt[p]] : null;
            Func<int, char, Block> enclosing = (p, kind) =>
            {
                var b = innermost(p);
                while (b != null && b.Kind != kind) b = b.Parent;
                return b;
            };
            Func<int, Block> paramsOf = p => p >= 0 && p <= n && parenOwner[p] >= 0 ? blocks[parenOwner[p]] : null;

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
            // #include した先で定義された型は、このファイルからは見えない。「型らしい語 + 名前」の形から、型の名前を推測する
            var inferredTypes = new HashSet<string>();
            var nameType = new Dictionary<string, string>();

            foreach (Match d in RxDecl.Matches(m))
            {
                string typeWord = d.Groups["t"].Value;
                if (!isTypeWord(typeWord))
                {
                    if (!LooksLikeDecl(m, d.Groups["t"].Index, typeWord, lx)) continue;
                    inferredTypes.Add(typeWord.Contains("::") ? typeWord.Substring(typeWord.LastIndexOf("::", StringComparison.Ordinal) + 2) : typeWord);
                }
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
                    nameType[name] = typeWord;
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

            for (int ti = 0; ti < toks.Count; ti++)
            {
                if (toks[ti].Kind != Tk.Identifier) continue;
                int p = toks[ti].Start;
                if (m[p] == ' ') continue;     // ディレクティブの行の中は、対象にしない
                string w = text.Substring(p, toks[ti].Length);
                char prev = prevChar(p);
                Tk? kind = null;

                bool arrow = prev == '>' && PrevTwo(m, p) == "->";
                if (prev != '.' && !arrow && inferredTypes.Contains(w)) kind = Tk.Type;
                else if (declOnlyParams.Contains(p)) kind = Tk.Param;
                else if (prev == '.' || arrow)
                {
                    if (allMembers.Contains(w) || BuiltinMembers.Contains(w)) kind = Tk.Member;
                    else if (IsFirstMemberOfStruct(m, p, nameType, userTypes, inferredTypes)) kind = Tk.Member;
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
                var tk = toks[ti];
                tk.Kind = kind.Value;
                toks[ti] = tk;
            }

            // 字句の段階で関数にした物のうち、メンバー関数(定義・呼び出し)を付け替える
            for (int i = 0; i < toks.Count; i++)
            {
                var t = toks[i];
                string name = text.Substring(t.Start, t.Length);
                bool dot = prevChar(t.Start) == '.';
                if (t.Kind == Tk.Intrinsic)
                {
                    // 独自のメンバー関数と同じ名前の呼び出しは、組み込みではなく、メンバー関数にする
                    if (dot && memberFuncs.Contains(name)) { t.Kind = Tk.MemberFunc; toks[i] = t; }
                    continue;
                }
                if (t.Kind != Tk.Function) continue;
                bool member = dot;
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

        /// <summary>
        /// 「型 名前」の形の宣言らしいか。型が、このファイルで分からない名前でも、文の頭(; { } ( , ] の直後や、
        /// const static などの修飾子の直後)にあれば、宣言と見なす。
        /// </summary>
        private static bool LooksLikeDecl(string m, int typeStart, string typeWord, Lexicon lx)
        {
            string last = typeWord.Contains("::") ? typeWord.Substring(typeWord.LastIndexOf("::", StringComparison.Ordinal) + 2) : typeWord;
            if (NotNames.Contains(last) || lx.Control.Contains(last) || lx.Keywords.Contains(last) || lx.Intrinsics.Contains(last)
                || lx.Constants.Contains(last) || lx.Semantics.Contains(last)) return false;
            int k = typeStart - 1;
            while (k >= 0 && char.IsWhiteSpace(m[k])) k--;
            if (k < 0) return true;
            char c = m[k];
            if (c == ';' || c == '{' || c == '}' || c == '(' || c == ',' || c == ']') return true;
            if (!(char.IsLetterOrDigit(c) || c == '_')) return false;
            int e = k;
            while (k >= 0 && (char.IsLetterOrDigit(m[k]) || m[k] == '_')) k--;
            string word = m.Substring(k + 1, e - k);
            return lx.Keywords.Contains(word) && word != "return";
        }

        /// <summary>obj.member の member か(obj は、構造体型の変数)。obj は ] の前でもよい(arr[i].member)。</summary>
        private static bool IsFirstMemberOfStruct(string m, int p, Dictionary<string, string> nameType,
            HashSet<string> userTypes, HashSet<string> inferredTypes)
        {
            int k = p - 1;
            while (k >= 0 && char.IsWhiteSpace(m[k])) k--;
            if (k >= 1 && m[k] == '>' && m[k - 1] == '-') k -= 2; else if (k >= 0 && m[k] == '.') k--; else return false;
            while (k >= 0 && char.IsWhiteSpace(m[k])) k--;
            while (k >= 0 && m[k] == ']')
            {
                int depth = 0;
                while (k >= 0)
                {
                    if (m[k] == ']') depth++;
                    else if (m[k] == '[') { depth--; if (depth == 0) break; }
                    k--;
                }
                k--;
                while (k >= 0 && char.IsWhiteSpace(m[k])) k--;
            }
            if (k < 0 || !(char.IsLetterOrDigit(m[k]) || m[k] == '_')) return false;
            int e = k;
            while (k >= 0 && (char.IsLetterOrDigit(m[k]) || m[k] == '_')) k--;
            string root = m.Substring(k + 1, e - k);
            int b = k;
            while (b >= 0 && char.IsWhiteSpace(m[b])) b--;
            if (b >= 0 && (m[b] == '.' || (m[b] == '>' && b >= 1 && m[b - 1] == '-'))) return false;   // 2 つ目以降のメンバーは対象外
            string type;
            if (!nameType.TryGetValue(root, out type)) return false;
            string last = type.Contains("::") ? type.Substring(type.LastIndexOf("::", StringComparison.Ordinal) + 2) : type;
            return userTypes.Contains(last) || inferredTypes.Contains(last);
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
