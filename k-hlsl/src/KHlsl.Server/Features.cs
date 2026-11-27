using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace KHlsl.Server
{
    internal sealed partial class Server
    {
        // LSP の CompletionItemKind
        private const int KMethod = 2, KFunction = 3, KField = 5, KVariable = 6, KClass = 7, KModule = 9,
            KProperty = 10, KEnum = 13, KKeyword = 14, KSnippet = 15, KConstant = 21, KStruct = 22, KEnumMember = 20,
            KTypeParameter = 25;

        private sealed class Ctx
        {
            public string Uri, Text, Masked;
            public int Offset, Line, Col;
        }

        private Ctx MakeCtx(JToken p)
        {
            var c = new Ctx { Uri = (string)p["textDocument"]["uri"] };
            c.Text = TextOf(c.Uri);
            c.Line = (int)p["position"]["line"];
            c.Col = (int)p["position"]["character"];
            c.Offset = Analyzer.OffsetOf(c.Text, c.Line, c.Col);
            c.Masked = Analyzer.Mask(c.Text);
            return c;
        }

        private static string DocText(string sig, string doc, string sm)
        {
            var sb = new StringBuilder();
            if (!string.IsNullOrEmpty(sig)) sb.Append("```hlsl\n").Append(sig.Replace("\r", "").TrimEnd('\n')).Append("\n```\n\n");
            if (!string.IsNullOrEmpty(doc)) sb.Append(doc);
            if (!string.IsNullOrEmpty(sm) && sm != "0" && sm != "1.0") sb.Append("\n\n*Shader Model ").Append(sm).Append(" 以降*");
            return sb.ToString();
        }

        // ---- 補完 ----
        /// <summary>補完の結果に、置き換える範囲(キャレットより前の語だけ)を付ける。
        /// 範囲を付けないと、VS はキャレットの前後の語をまとめて置き換えるので、IME の確定(Enter)などで後ろの文字が消えることがある。</summary>
        private JToken Completion(JToken p)
        {
            var res = CompletionCore(p);
            try
            {
                // 範囲は、要求のキャレット位置(行・文字)をそのまま使う。
                // サーバーの本文が一瞬古いと、本文から求めた位置は別の行や手前にずれて、
                // VS は「範囲がキャレットを含まない」として、候補を出した直後に閉じてしまう。
                string text = TextOf((string)p["textDocument"]["uri"]);
                int line = (int)p["position"]["line"];
                int col = (int)p["position"]["character"];
                string[] ls = HlslFormatter.SplitLines(text);
                string cur = line >= 0 && line < ls.Length ? ls[line] : "";
                string before = cur.Substring(0, Math.Min(col, cur.Length));
                // #include のファイル名は、\ や . を含むので対象外
                if (Regex.IsMatch(before, @"^\s*#\s*include")) return res;
                int ws = before.Length;
                while (ws > 0 && (char.IsLetterOrDigit(before[ws - 1]) || before[ws - 1] == '_')) ws--;
                // 本文が古くて行が短いときも、語の開始位置はそのまま(足りない分は、直前に打った語の続き)
                var items = res == null ? null : res["items"] as JArray;
                if (items == null) return res;
                var range = Range(line, ws, line, col);
                foreach (JObject it in items)
                {
                    if (it["textEdit"] != null) continue;
                    it["textEdit"] = new JObject { ["range"] = range.DeepClone(), ["newText"] = (string)it["label"] };
                }
            }
            catch (Exception) { }
            return res;
        }

        private JToken CompletionCore(JToken p)
        {
            var c = MakeCtx(p);
            string m = c.Masked;
            int off = Math.Min(c.Offset, m.Length);
            // #include "…" のファイル名。引用符の中は「文字列の中」と判定されるので、その判定より先に、
            // コメントと文字列を消す前の本文で見る(消した本文では、打ったファイル名が空白になる)
            {
                int rs = off;
                while (rs > 0 && c.Text[rs - 1] != '\n') rs--;
                var im = Regex.Match(c.Text.Substring(rs, off - rs), @"^\s*#\s*include\s*[""<]([^"">]*)$");
                if (im.Success && m.Substring(rs, off - rs).TrimStart().StartsWith("#", StringComparison.Ordinal))
                    return Items(IncludeFiles(c.Uri, im.Groups[1].Value));
            }
            // コメントや文字列の中
            if (IsInCommentOrString(c.Text, off)) return Items(new List<JObject>());
            int ls = off;
            while (ls > 0 && m[ls - 1] != '\n') ls--;
            string before = m.Substring(ls, off - ls);
            var syms = Collect(c.Uri, c.Text);
            var items = new List<JObject>();

            // #directive
            var dm = Regex.Match(before, @"^\s*#\s*(\w*)$");
            if (dm.Success)
            {
                foreach (var d in _db.directives)
                    items.Add(Item(d.n, KKeyword, d.syntax, DocText(d.syntax, d.d, null)));
                return Items(items);
            }
            // メンバー補完(. の後)
            var mm = Regex.Match(before, @"(?<expr>[\w\]\[\.\s]*?)\.\s*(?<w>\w*)$");
            if (mm.Success && !Regex.IsMatch(before, @"\d\.\w*$") || mm.Success && Regex.IsMatch(before, @"[A-Za-z_]\w*\s*\.\s*\w*$"))
            {
                int dot = ls + before.LastIndexOf('.');
                string type = ExprType(m, dot, off, syms);
                var list = MemberItems(type, syms);
                return Items(list);
            }

            // 名前空間 (dx:: など)
            var nm = Regex.Match(before, @"([A-Za-z_]\w*(?:::\w+)*)::\w*$");
            if (nm.Success)
            {
                string ns = nm.Groups[1].Value;
                if (ns == "dx")
                {
                    items.Add(Item("HitObject", KClass, "dx::HitObject", DocText("dx::HitObject", _db.TypeByName["dx::HitObject"].d, "6.9")));
                    var mr = _db.IntrinsicByName["dx::MaybeReorderThread"];
                    items.Add(Item("MaybeReorderThread", KFunction, mr.s[0], DocText(string.Join("\n", mr.s), mr.d, mr.m)));
                }
                else if (ns == "dx::HitObject")
                {
                    foreach (var f in _db.methods["hitobject"].Where(x => x.s[0].StartsWith("static")))
                        items.Add(Item(f.n, KFunction, f.s[0], DocText(string.Join("\n", f.s), f.d, f.m)));
                }
                else
                {
                    foreach (var s in syms.Where(s => s.Container == ns && !s.Local)) items.Add(SymItem(s));
                }
                return Items(items);
            }

            // セマンティクス( : の後 )
            if (Regex.IsMatch(before, @"(?<![:?])\:\s*[A-Za-z_]*\d*$") && !Regex.IsMatch(before, @"\?[^:]*:\s*\w*$") && !Regex.IsMatch(before, @"\b(case|default)\b"))
            {
                foreach (var s in _db.semantics)
                    items.Add(Item(s.n, KEnumMember, null, DocText(null, s.d, null)));
                items.Add(Item("register", KKeyword, "register(b0, space0)", "レジスタと space を指定する。"));
                items.Add(Item("packoffset", KKeyword, "packoffset(c0)", "定数バッファの中での位置を指定する。"));
                return Items(items);
            }

            // 属性 [ の後
            var am = Regex.Match(before, @"(?:^|[;{})\]\s])\[\[?\s*[A-Za-z_:]*$");
            if (am.Success && !Regex.IsMatch(before, @"[\w\]\)]\s*\[\s*\w*$"))
            {
                foreach (var a in _db.attributes)
                    items.Add(Item(a.n, KProperty, a.syntax, DocText(a.syntax, a.d, a.m)));
                return Items(items);
            }

            // 一般
            foreach (var k in _db.keywords) items.Add(Item(k.n, KKeyword, null, k.d.Length > 0 ? DocText(null, k.d, null) : null));
            foreach (var t in _db.types.Where(t => !t.n.Contains("::")))
                items.Add(Item(t.n, t.scalar ? KKeyword : KClass, null, string.IsNullOrEmpty(t.d) ? null : DocText(null, t.d, t.m)));
            foreach (var n in new[] { "float", "int", "uint", "half", "double", "bool", "min16float", "min16int", "min16uint" })
            {
                foreach (var d in new[] { "2", "3", "4" }) items.Add(Item(n + d, KClass, null, null));
                foreach (var d in new[] { "2x2", "3x3", "4x4", "3x4", "4x3" }) items.Add(Item(n + d, KClass, null, null));
            }
            foreach (var f in _db.intrinsics)
                items.Add(Item(f.n, KFunction, f.s[0], DocText(string.Join("\n", f.s), f.d, f.m)));
            foreach (var cst in _db.constants)
                items.Add(Item(cst.n, KConstant, null, DocText(null, cst.d, null)));
            foreach (var mac in _db.macros) items.Add(Item(mac.n, KConstant, null, DocText(null, mac.d, null)));
            foreach (var s in _db.special) items.Add(Item(s.n, KVariable, null, DocText(null, s.d, s.m)));
            foreach (var s in syms)
            {
                if (s.Local && !(s.ScopeStart <= off && off <= s.ScopeEnd && s.File == PathOf(c.Uri))) continue;
                if (s.Kind == SymKind.Variable && s.Container != null && s.Local == false && !IsGlobalMember(s, syms)) continue;
                items.Add(SymItem(s));
            }
            return Items(Dedup(items));
        }

        private static bool IsGlobalMember(Sym s, List<Sym> all)
        {
            // cbuffer のメンバーはグローバル、struct のメンバーは違う
            return all.Any(x => x.Kind == SymKind.CBuffer && x.Name == s.Container);
        }

        private static List<JObject> Dedup(List<JObject> items)
        {
            var seen = new HashSet<string>();
            var res = new List<JObject>();
            // 後から来る(ユーザーのシンボル)を優先して、同名の組み込みを隠す
            for (int i = items.Count - 1; i >= 0; i--)
            {
                string key = (string)items[i]["label"] + "|" + (int)items[i]["kind"];
                string nameOnly = (string)items[i]["label"];
                if (seen.Add(nameOnly)) res.Add(items[i]);
            }
            res.Reverse();
            return res;
        }

        private static JToken Items(List<JObject> items)
        {
            return new JObject { ["isIncomplete"] = false, ["items"] = new JArray(items) };
        }

        private static JObject Item(string label, int kind, string detail, string doc)
        {
            var o = new JObject { ["label"] = label, ["kind"] = kind };
            if (detail != null) o["detail"] = detail;
            if (!string.IsNullOrEmpty(doc)) o["documentation"] = Markdown(doc);
            return o;
        }

        private JObject SymItem(Sym s)
        {
            int kind;
            switch (s.Kind)
            {
                case SymKind.Function: kind = KFunction; break;
                case SymKind.Struct: kind = KStruct; break;
                case SymKind.CBuffer: kind = KStruct; break;
                case SymKind.Namespace: kind = KModule; break;
                case SymKind.Enum: kind = KEnum; break;
                case SymKind.Macro: kind = KConstant; break;
                case SymKind.TypeAlias: kind = KClass; break;
                default: kind = s.Container != null && !s.IsParam ? KField : KVariable; break;
            }
            string where = s.File != null ? Path.GetFileName(s.File) + ":" + (s.Line + 1) : null;
            return Item(s.Name, kind, s.Signature, DocText(s.Signature, where != null ? "`" + where + "` で定義" : null, null));
        }

        private List<JObject> MemberItems(string type, List<Sym> syms)
        {
            var items = new List<JObject>();
            if (type != null)
            {
                string bare = BaseType(type);
                var ms = _db.MethodsOf(bare);
                foreach (var f in ms)
                    items.Add(Item(f.n, KMethod, f.s[0], DocText(string.Join("\n", f.s), f.d, f.m)));
                if (ms.Count > 0 && _db.TypeByName[bare].g.Any(g => g == "tex" || g == "ms"))
                {
                    if (_db.TypeByName[bare].g.Contains("texlod")) items.Add(Item("mips", KProperty, "mips[mipLevel][pos]", "mip レベルを指定して読む。"));
                    if (_db.TypeByName[bare].g.Contains("ms")) items.Add(Item("sample", KProperty, "sample[sampleIndex][pos]", "サンプルを指定して読む。"));
                }
                // struct のメンバー
                string tn = Regex.Replace(type, @"<.*$", "");
                foreach (var s in syms.Where(s => s.Kind == SymKind.Variable && s.Container == tn && !s.Local)) items.Add(SymItem(s));
                foreach (var s in syms.Where(s => s.Kind == SymKind.Function && s.Container == tn)) items.Add(SymItem(s));
                // ベクターのスウィズル
                var vm = Regex.Match(bare, @"^(?:bool|int|uint|half|float|double|min\d+\w+|\w+_t)([1-4])$");
                if (vm.Success)
                {
                    int n = int.Parse(vm.Groups[1].Value);
                    foreach (var set in new[] { "xyzw", "rgba" })
                    {
                        string comps = set.Substring(0, n);
                        foreach (char ch in comps) items.Add(Item(ch.ToString(), KField, null, null));
                        for (int len = 2; len <= 4; len++)
                        {
                            items.Add(Item(comps.Substring(0, Math.Min(len, n)), KField, null, null));
                        }
                    }
                }
                var mx = Regex.Match(bare, @"^(?:bool|int|uint|half|float|double|min\d+\w+)([1-4])x([1-4])$");
                if (mx.Success)
                {
                    int r = int.Parse(mx.Groups[1].Value), cc = int.Parse(mx.Groups[2].Value);
                    for (int i = 1; i <= r; i++) for (int j = 1; j <= cc; j++) items.Add(Item("_m" + (i - 1) + (j - 1), KField, null, "行 " + (i - 1) + "、列 " + (j - 1) + "(0 始まり)"));
                    for (int i = 1; i <= r; i++) for (int j = 1; j <= cc; j++) items.Add(Item("_" + i + j, KField, null, "行 " + i + "、列 " + j + "(1 始まり)"));
                }
                if (items.Count > 0) return Dedup(items);
            }
            // 型が分からないときは、全部出す
            foreach (var f in _db.AllMethods())
                items.Add(Item(f.n, KMethod, f.s[0], DocText(string.Join("\n", f.s), f.d, f.m)));
            foreach (var s in syms.Where(s => s.Kind == SymKind.Variable && s.Container != null && !s.Local)) items.Add(SymItem(s));
            return Dedup(items);
        }

        private List<JObject> IncludeFiles(string uri, string typed)
        {
            var items = new List<JObject>();
            try
            {
                string path = PathOf(uri);
                var cfg = Config.For(path);
                var dirs = new List<string> { Path.GetDirectoryName(path) };
                dirs.AddRange(cfg.ResolvedIncludeDirs());
                string sub = typed.Replace('/', '\\');
                int cut = sub.LastIndexOf('\\');
                string subDir = cut >= 0 ? sub.Substring(0, cut) : "";
                foreach (var d in dirs)
                {
                    string dir = Path.Combine(d, subDir);
                    if (!Directory.Exists(dir)) continue;
                    foreach (var e in Directory.GetFileSystemEntries(dir))
                    {
                        string name = Path.GetFileName(e);
                        bool isDir = Directory.Exists(e);
                        if (!isDir && !Regex.IsMatch(name, @"\.(hlsli?|fxh?|h|inc|cginc|usf|ush)$", RegexOptions.IgnoreCase)) continue;
                        items.Add(Item(name, isDir ? 19 : 17, null, null));
                    }
                }
            }
            catch (Exception) { }
            return items;
        }

        private static bool IsInCommentOrString(string text, int offset)
        {
            string masked = Analyzer.Mask(text.Substring(0, Math.Min(offset, text.Length)));
            // 末尾付近で、元は文字だったのに空白になっている = コメントか文字列の中
            int i = masked.Length - 1;
            if (i < 0) return false;
            if (masked[i] == ' ' && text[i] != ' ' && text[i] != '\t') return true;
            // 行コメントの途中(// の直後)
            int ls = text.LastIndexOf('\n', Math.Max(0, i)) + 1;
            for (int k = ls; k < i; k++)
                if (masked[k] == ' ' && text[k] == '/') return true;
            return false;
        }

        // ---- 式の型 ----
        private static string BaseType(string type)
        {
            if (type == null) return null;
            return Regex.Replace(type, @"<.*$", "").Trim();
        }

        private static string InnerType(string type)
        {
            if (type == null) return null;
            var m = Regex.Match(type, @"<(.+)>$");
            if (!m.Success) return null;
            string inner = m.Groups[1].Value;
            // vector<T,N> のようなコンマはそのまま返さない
            int depth = 0;
            for (int i = 0; i < inner.Length; i++)
            {
                if (inner[i] == '<') depth++;
                else if (inner[i] == '>') depth--;
                else if (inner[i] == ',' && depth == 0) return inner.Substring(0, i);
            }
            return inner;
        }

        private static string ResolveAlias(string type, List<Sym> syms)
        {
            for (int i = 0; i < 6 && type != null; i++)
            {
                string b = BaseType(type);
                var a = syms.FirstOrDefault(s => s.Kind == SymKind.TypeAlias && s.Name == b);
                if (a == null) break;
                type = a.Type;
            }
            return type;
        }

        private static string VarType(string name, int offset, string file, List<Sym> syms)
        {
            Sym best = null;
            foreach (var s in syms)
            {
                if (s.Kind != SymKind.Variable || s.Name != name || s.Container != null && !s.IsParam && s.Local == false && !syms.Any(x => x.Kind == SymKind.CBuffer && x.Name == s.Container)) continue;
                if (s.Local && !(s.ScopeStart <= offset && offset <= s.ScopeEnd && s.File == file)) continue;
                if (best == null || (s.Local && !best.Local) || (s.Local == best.Local && s.File == file && s.Offset <= offset && s.Offset >= best.Offset)) best = s;
            }
            return best == null ? null : ResolveAlias(best.Type, syms);
        }

        /// <summary>m[..dot) の末尾の式(a.b[3].c)の型を求める。分からなければ null。</summary>
        private string ExprType(string m, int dot, int caret, List<Sym> syms)
        {
            int i = dot - 1;
            while (i >= 0 && m[i] == ' ') i--;
            int end = i + 1;
            while (i >= 0)
            {
                if (IsIdent(m[i]) || m[i] == '.') { i--; continue; }
                if (m[i] == ']')
                {
                    int d = 0;
                    while (i >= 0) { if (m[i] == ']') d++; else if (m[i] == '[') { d--; if (d == 0) break; } i--; }
                    i--;
                    continue;
                }
                break;
            }
            string expr = m.Substring(i + 1, end - (i + 1));
            // 区切って先頭から辿る
            var parts = new List<string>();
            var sb = new StringBuilder();
            int depth = 0;
            foreach (char ch in expr)
            {
                if (ch == '[') depth++;
                if (ch == ']') depth--;
                if (ch == '.' && depth == 0) { parts.Add(sb.ToString()); sb.Clear(); }
                else sb.Append(ch);
            }
            parts.Add(sb.ToString());
            string type = null;
            for (int k = 0; k < parts.Count; k++)
            {
                var pm = Regex.Match(parts[k].Trim(), @"^(?<n>[A-Za-z_]\w*)(?<idx>(?:\s*\[.*\])*)$", RegexOptions.Singleline);
                if (!pm.Success) return null;
                string name = pm.Groups["n"].Value;
                bool indexed = pm.Groups["idx"].Value.Length > 0;
                if (k == 0)
                {
                    if (name == "ResourceDescriptorHeap" || name == "SamplerDescriptorHeap") return null;
                    string t = VarType(name, caret, null, syms) ?? VarTypeAnyFile(name, caret, syms);
                    if (t == null) return null;
                    type = t;
                }
                else
                {
                    string tn = BaseType(type);
                    var mem = syms.FirstOrDefault(s => s.Kind == SymKind.Variable && s.Container == tn && s.Name == name);
                    if (mem == null) return null;
                    type = ResolveAlias(mem.Type, syms);
                }
                if (indexed)
                {
                    string bt = BaseType(type);
                    string inner = InnerType(type);
                    if (inner != null && (bt.Contains("Buffer") || bt.StartsWith("Texture") || bt.StartsWith("RWTexture") || bt.StartsWith("RasterizerOrdered") || bt == "ConstantBuffer" || bt == "TextureBuffer"))
                        type = ResolveAlias(inner, syms);
                    else if (bt.Contains("Buffer") || bt.Contains("Texture")) type = null;
                    if (type == null) return null;
                }
                // ConstantBuffer<T> は添字なしで T のメンバーに触る
                if (BaseType(type) == "ConstantBuffer" || BaseType(type) == "TextureBuffer")
                {
                    string inner = InnerType(type);
                    if (inner != null && k < parts.Count - 1) type = ResolveAlias(inner, syms);
                    else if (inner != null) type = ResolveAlias(inner, syms);
                }
            }
            return type;
        }

        private static string VarTypeAnyFile(string name, int offset, List<Sym> syms)
        {
            // 位置に依存せず、最も近い宣言を使う
            Sym best = null;
            foreach (var s in syms)
            {
                if (s.Kind != SymKind.Variable || s.Name != name) continue;
                if (s.Local && !(s.ScopeStart <= offset && offset <= s.ScopeEnd)) continue;
                if (best == null || (s.Local && !best.Local)) best = s;
            }
            return best == null ? null : ResolveAlias(best.Type, syms);
        }

        // ---- ホバー ----
        private string WordAt(string text, int offset, out int start, out int end)
        {
            start = offset; end = offset;
            if (offset > text.Length) offset = text.Length;
            while (start > 0 && (IsIdent(text[start - 1]) || (start > 1 && text[start - 1] == ':' && text[start - 2] == ':') || (start > 1 && text[start - 1] == ':' && start < text.Length && text[start] == ':'))) start--;
            while (end < text.Length && (IsIdent(text[end]) || (end + 1 < text.Length && text[end] == ':' && text[end + 1] == ':' && end + 2 < text.Length && IsIdent(text[end + 2])) || (end > 0 && text[end] == ':' && text[end - 1] == ':' && end + 1 < text.Length && IsIdent(text[end + 1])))) end++;
            while (start < end && !(IsIdent(text[start]))) start++;
            return start < end ? text.Substring(start, end - start) : null;
        }

        private JToken Hover(JToken p)
        {
            var c = MakeCtx(p);
            int s, e;
            string word = WordAt(c.Masked, c.Offset, out s, out e);
            if (word == null || IsInCommentOrString(c.Text, c.Offset) && c.Masked[Math.Max(0, Math.Min(c.Masked.Length - 1, c.Offset))] == ' ') return null;
            var syms = Collect(c.Uri, c.Text);
            string md = Describe(word, s, e, c, syms);
            string layout = null;
            try { layout = LayoutHover(c, word); } catch (Exception ex) { FileLog("layout hover failed: " + ex.Message); }
            if (layout != null) md = md == null ? layout : md + "\n\n---\n\n" + layout;
            if (md == null) return null;
            int l1, c1, l2, c2;
            Analyzer.PositionOf(c.Text, s, out l1, out c1);
            Analyzer.PositionOf(c.Text, e, out l2, out c2);
            return new JObject { ["contents"] = Markdown(md), ["range"] = Range(l1, c1, l2, c2) };
        }

        private string Describe(string word, int s, int e, Ctx c, List<Sym> syms)
        {
            string m = c.Masked;
            int pi = s - 1;
            while (pi >= 0 && m[pi] == ' ') pi--;
            char prev = pi >= 0 ? m[pi] : '\0';
            string bare = word.Contains("::") ? word.Substring(word.LastIndexOf("::", StringComparison.Ordinal) + 2) : word;

            // x.Method
            if (prev == '.')
            {
                string type = ExprType(m, pi, c.Offset, syms);
                Db.Func f = null;
                if (type != null)
                {
                    f = _db.MethodsOf(BaseType(type)).FirstOrDefault(x => x.n == word);
                    if (f == null)
                    {
                        string tn = BaseType(type);
                        var mem = syms.FirstOrDefault(x => x.Container == tn && x.Name == word);
                        if (mem != null) return DocText(mem.Signature, "`" + tn + "` のメンバー", null);
                    }
                }
                if (f == null) f = _db.FindMethodAnywhere(word);
                if (f != null) return DocText(string.Join("\n", f.s), f.d, f.m);
                if (word == "mips") return DocText("mips[mipLevel][pos]", "mip レベルを指定して読む。", null);
                if (word == "sample") return DocText("sample[sampleIndex][pos]", "サンプルを指定して読む。", null);
                return null;
            }

            // dx::
            if (word.StartsWith("dx::", StringComparison.Ordinal))
            {
                Db.Func fi; Db.TypeInfo ti;
                if (_db.IntrinsicByName.TryGetValue(word, out fi)) return DocText(string.Join("\n", fi.s), fi.d, fi.m);
                if (_db.TypeByName.TryGetValue(word, out ti)) return DocText(word, ti.d, ti.m);
                var hm = _db.methods["hitobject"].FirstOrDefault(x => x.n == bare);
                if (hm != null) return DocText(string.Join("\n", hm.s), hm.d, hm.m);
            }

            // 属性
            if (prev == '[' && _db.AttrByName.ContainsKey(word))
            {
                var a = _db.AttrByName[word];
                return DocText(a.syntax, a.d, a.m);
            }
            if (prev == '[' && word.StartsWith("vk::")) { }
            // セマンティクス
            if ((prev == ':' || Regex.IsMatch(word, @"^SV_", RegexOptions.IgnoreCase)))
            {
                string key = Regex.Replace(word, @"\d+$", "").ToLowerInvariant();
                Db.Sem sem;
                if (_db.SemByName.TryGetValue(key, out sem) || _db.SemByName.TryGetValue(word.ToLowerInvariant(), out sem))
                    return DocText(sem.n + (Regex.IsMatch(word, @"\d+$") ? Regex.Match(word, @"\d+$").Value : ""), sem.d, null);
            }

            // ユーザー定義(組み込みと同名なら、ユーザー側を優先)
            var user = FindUser(word, s, c, syms);
            if (user != null)
            {
                string where = user.File != null ? Path.GetFileName(user.File) + ":" + (user.Line + 1) : null;
                return DocText(user.Signature, where != null ? "`" + where + "` で定義" : null, null);
            }

            Db.Func intr; Db.TypeInfo typ; Db.Keyword kw; Db.Const cst; Db.Macro mac; Db.Special sp;
            if (_db.IntrinsicByName.TryGetValue(word, out intr)) return DocText(string.Join("\n", Concretize(intr.s, e, s, c, syms)), intr.d, intr.m);
            if (_db.TypeByName.TryGetValue(word, out typ)) return DocText(word, typ.d, typ.m);
            if (_db.SpecialByName.TryGetValue(word, out sp)) return DocText(word, sp.d, sp.m);
            if (_db.ConstByName.TryGetValue(word, out cst)) return DocText(word, cst.d, null);
            if (_db.MacroByName.TryGetValue(word, out mac)) return DocText("#define " + word, mac.d, null);
            if (_db.KeywordByName.TryGetValue(word, out kw) && kw.d.Length > 0) return DocText(word, kw.d, null);
            var vec = Regex.Match(word, @"^(bool|int|uint|half|float|double|min\d+\w+)([1-4])(?:x([1-4]))?$");
            if (vec.Success)
            {
                return vec.Groups[3].Success
                    ? DocText(word, vec.Groups[2].Value + " 行 " + vec.Groups[3].Value + " 列の " + vec.Groups[1].Value + " 行列。", null)
                    : DocText(word, vec.Groups[2].Value + " 成分の " + vec.Groups[1].Value + " ベクター。", null);
            }
            return null;
        }


        // ---- 総称型(T F I U)を、呼び出しの引数の型で具体型にする ----
        private static readonly Regex GenericLetter = new Regex(@"\b[TFIU]\b", RegexOptions.Compiled);
        private static readonly Regex TypeShape = new Regex(@"^(bool|int|uint|half|float|double)([1-4])?(x[1-4])?$", RegexOptions.Compiled);

        /// <summary>T F I U を含むシグネチャを、呼び出しの引数の型で書き換える。引数の型が分からなければ、そのまま返す。</summary>
        private IList<string> Concretize(IList<string> sigs, int wordEnd, int wordStart, Ctx c, List<Sym> syms)
        {
            if (!sigs.Any(x => GenericLetter.IsMatch(x))) return sigs;
            var args = CallArgs(c.Masked, wordEnd);
            if (args == null || args.Count == 0) return sigs;
            var types = args.Select(a => ArgType(a, wordStart, syms)).ToList();
            if (types.All(x => x == null)) return sigs;
            // 最初は、型の種類(float / int)まで合う候補だけ。なければ、暗黙の変換を許す
            foreach (bool strict in new[] { true, false })
            {
                var res = new List<string>();
                foreach (var sig in sigs)
                {
                    string r = Substitute(sig, types, strict);
                    if (r != null) res.Add(r);
                }
                if (res.Count > 0) return res;
            }
            return sigs;
        }

        private static string ScalarOf(string t) { var m = TypeShape.Match(t); return m.Success ? m.Groups[1].Value : null; }

        /// <summary>type の次元(float3 の 3 など)はそのままで、要素の型だけを scalar にする。</summary>
        private static string WithScalar(string type, string scalar)
        {
            var m = TypeShape.Match(type);
            return m.Success ? scalar + m.Groups[2].Value + m.Groups[3].Value : null;
        }

        private static string Substitute(string sig, List<string> argTypes, bool strict)
        {
            int open = sig.IndexOf('(');
            int close = sig.LastIndexOf(')');
            if (open < 0 || close < open) return sig;
            string plist = sig.Substring(open + 1, close - open - 1);
            var ps = plist.Split(',').Select(x => x.Trim()).ToList();
            var repl = new Dictionary<char, string>();
            string baseType = null;
            for (int i = 0; i < ps.Count; i++)
            {
                var m = Regex.Match(ps[i], @"^(?:(?:out|inout|in)\s+)?([TFIU])\s+\w+$");
                if (!m.Success) continue;
                char L = m.Groups[1].Value[0];
                string a = i < argTypes.Count ? argTypes[i] : null;
                if (a == null || ScalarOf(a) == null || repl.ContainsKey(L)) continue;
                string sc = ScalarOf(a);
                bool isFloat = sc == "float" || sc == "half" || sc == "double";
                bool isInt = sc == "int" || sc == "uint";
                if (strict && ((L == 'F' && !isFloat) || ((L == 'I' || L == 'U') && !isInt))) return null;
                repl[L] = L == 'T' ? a
                        : L == 'F' ? WithScalar(a, isFloat ? sc : "float")
                        : L == 'I' ? WithScalar(a, isInt ? sc : "int")
                        : WithScalar(a, isInt ? sc : "uint");
                if (baseType == null) baseType = a;
            }
            if (baseType == null) return sig;
            // 引数にない文字(戻り値だけの F I U)は、最初の引数の次元で補う
            foreach (char L in "FIU")
                if (!repl.ContainsKey(L) && Regex.IsMatch(sig, @"\b" + L + @"\b"))
                    repl[L] = WithScalar(baseType, L == 'F' ? "float" : L == 'I' ? "int" : "uint");
            return Regex.Replace(sig, @"\b[TFIU]\b", mm => repl.ContainsKey(mm.Value[0]) ? repl[mm.Value[0]] : mm.Value);
        }

        /// <summary>word の直後の ( ) の中身を、最上位の , で分ける。呼び出しでなければ null。</summary>
        private static List<string> CallArgs(string m, int i)
        {
            while (i < m.Length && (m[i] == ' ' || m[i] == '\t')) i++;
            if (i >= m.Length || m[i] != '(') return null;
            var res = new List<string>();
            var sb = new StringBuilder();
            int depth = 0;
            for (i++; i < m.Length; i++)
            {
                char ch = m[i];
                if (ch == '(' || ch == '[' || ch == '{') depth++;
                else if (ch == ')' || ch == ']' || ch == '}')
                {
                    if (depth == 0) { if (sb.ToString().Trim().Length > 0) res.Add(sb.ToString().Trim()); return res; }
                    depth--;
                }
                else if (ch == ',' && depth == 0) { res.Add(sb.ToString().Trim()); sb.Clear(); continue; }
                else if (ch == ';') return null;
                sb.Append(ch);
            }
            return null;
        }

        /// <summary>引数の式の型。リテラル・変数・スウィズル・float3(...) だけ分かる。それ以外は null。</summary>
        private string ArgType(string a, int offset, List<Sym> syms)
        {
            a = a.Trim();
            while (a.StartsWith("-") || a.StartsWith("+") || a.StartsWith("!")) a = a.Substring(1).TrimStart();
            if (a.Length == 0) return null;
            if (a == "true" || a == "false") return "bool";
            if (Regex.IsMatch(a, @"^(\d+\.\d*|\.\d+|\d+)([eE][+-]?\d+)?[fFhH]$|^(\d+\.\d*|\.\d+)([eE][+-]?\d+)?$")) return "float";
            if (Regex.IsMatch(a, @"^(\d+|0[xX][0-9a-fA-F]+)[uU]$")) return "uint";
            if (Regex.IsMatch(a, @"^(\d+|0[xX][0-9a-fA-F]+)$")) return "int";
            var ctor = Regex.Match(a, @"^([A-Za-z_]\w*)\s*\(");
            if (ctor.Success && TypeShape.IsMatch(ctor.Groups[1].Value) && a.EndsWith(")")) return ctor.Groups[1].Value;
            if (Regex.IsMatch(a, @"^[A-Za-z_]\w*$"))
            {
                string t = VarTypeAnyFile(a, offset, syms);
                return t != null && TypeShape.IsMatch(t) ? t : null;
            }
            var sw = Regex.Match(a, @"^([A-Za-z_]\w*)\.([xyzwrgba]{1,4})$");
            if (sw.Success)
            {
                string t = VarTypeAnyFile(sw.Groups[1].Value, offset, syms);
                string sc = t == null ? null : ScalarOf(t);
                if (sc == null) return null;
                int n = sw.Groups[2].Length;
                return n == 1 ? sc : sc + n;
            }
            return null;
        }

        private Sym FindUser(string word, int offset, Ctx c, List<Sym> syms)
        {
            string file = PathOf(c.Uri);
            string bare = word.Contains("::") ? word.Substring(word.LastIndexOf("::", StringComparison.Ordinal) + 2) : word;
            Sym best = null;
            foreach (var s in syms)
            {
                if (s.Name != bare) continue;
                if (s.Local && !(s.ScopeStart <= offset && offset <= s.ScopeEnd && s.File == file)) continue;
                if (best == null) { best = s; continue; }
                if (s.Local && !best.Local) { best = s; continue; }
                if (best.Kind == SymKind.Function && s.Kind == SymKind.Function && s.Offset > best.Offset && best.File == s.File && false) best = s;
            }
            return best;
        }

        // ---- 定義へ移動 ----
        private JToken Definition(JToken p)
        {
            var c = MakeCtx(p);
            // #include "x"
            int ls = c.Text.LastIndexOf('\n', Math.Max(0, Math.Min(c.Text.Length - 1, c.Offset - 1))) + 1;
            int le = c.Text.IndexOf('\n', Math.Min(c.Text.Length, c.Offset));
            if (le < 0) le = c.Text.Length;
            string line = c.Text.Substring(ls, le - ls);
            var im = Regex.Match(line, @"^\s*#\s*include\s*[""<]([^"">]+)["">]");
            if (im.Success)
            {
                string r = ResolveInclude(im.Groups[1].Value, PathOf(c.Uri), Config.For(PathOf(c.Uri)));
                if (r != null) return new JObject { ["uri"] = UriOf(r), ["range"] = Range(0, 0, 0, 0) };
            }
            int s, e;
            string word = WordAt(c.Masked, c.Offset, out s, out e);
            if (word == null) return null;
            var syms = Collect(c.Uri, c.Text);
            var user = FindUser(word, s, c, syms);
            if (user == null) return null;
            return new JObject { ["uri"] = UriOf(user.File), ["range"] = Range(user.Line, user.Col, user.Line, user.Col + user.Name.Length) };
        }

        // ---- ドキュメント シンボル ----
        private JToken DocumentSymbols(JToken p)
        {
            string uri = (string)p["textDocument"]["uri"];
            string text = TextOf(uri);
            string path = PathOf(uri);
            var scan = Analyzer.Scan(path, text);
            var arr = new JArray();
            foreach (var s in scan.Syms)
            {
                if (s.Local || s.IsParam) continue;
                int kind;
                switch (s.Kind)
                {
                    case SymKind.Function: kind = s.Container != null ? 6 : 12; break;
                    case SymKind.Struct: kind = 23; break;
                    case SymKind.CBuffer: kind = 23; break;
                    case SymKind.Namespace: kind = 3; break;
                    case SymKind.Enum: kind = 10; break;
                    case SymKind.Macro: kind = 14; break;
                    case SymKind.TypeAlias: kind = 26; break;
                    default: kind = s.Container != null ? (scan.Syms.Any(x => x.Kind == SymKind.Enum && x.Name == s.Container) ? 22 : 8) : 13; break;
                }
                var o = new JObject
                {
                    ["name"] = s.Name,
                    ["kind"] = kind,
                    ["location"] = new JObject { ["uri"] = uri, ["range"] = Range(s.Line, s.Col, s.Line, s.Col + s.Name.Length) }
                };
                if (s.Container != null) o["containerName"] = s.Container;
                arr.Add(o);
            }
            return arr;
        }

        // ---- シグネチャ ヘルプ ----
        private JToken SignatureHelp(JToken p)
        {
            var c = MakeCtx(p);
            string m = c.Masked;
            int off = Math.Min(c.Offset, m.Length);
            int depth = 0, commas = 0, open = -1;
            for (int i = off - 1; i >= 0; i--)
            {
                char ch = m[i];
                if (ch == ')' || ch == ']' || ch == '}') depth++;
                else if (ch == '(' || ch == '[' || ch == '{')
                {
                    if (depth == 0) { if (ch == '(') { open = i; break; } return null; }
                    depth--;
                }
                else if (ch == ',' && depth == 0) commas++;
                else if (ch == ';' && depth == 0) return null;
            }
            if (open < 0) return null;
            int ne = open;
            while (ne > 0 && m[ne - 1] == ' ') ne--;
            int ns = ne;
            while (ns > 0 && (IsIdent(m[ns - 1]) || (ns > 1 && m[ns - 1] == ':' && m[ns - 2] == ':') || (m[ns - 1] == ':' && ns < m.Length && m[ns] == ':'))) ns--;
            if (ns >= ne) return null;
            string name = m.Substring(ns, ne - ns);
            string bare = name.Contains("::") ? name.Substring(name.LastIndexOf("::", StringComparison.Ordinal) + 2) : name;
            int pi = ns - 1;
            while (pi >= 0 && m[pi] == ' ') pi--;
            var syms = Collect(c.Uri, c.Text);

            var sigs = new List<Tuple<string, string, string>>(); // シグネチャ, 説明, SM
            if (pi >= 0 && m[pi] == '.')
            {
                string type = ExprType(m, pi, off, syms);
                Db.Func f = null;
                if (type != null) f = _db.MethodsOf(BaseType(type)).FirstOrDefault(x => x.n == bare);
                if (f == null) f = _db.FindMethodAnywhere(bare);
                if (f != null) foreach (var sg in f.s) sigs.Add(Tuple.Create(sg, f.d, f.m));
            }
            else
            {
                foreach (var s in syms.Where(s => s.Kind == SymKind.Function && s.Name == bare))
                    sigs.Add(Tuple.Create(s.Signature, (string)null, (string)null));
                if (sigs.Count == 0)
                {
                    Db.Func f;
                    if (_db.IntrinsicByName.TryGetValue(name, out f) || _db.IntrinsicByName.TryGetValue(bare, out f))
                        foreach (var sg in f.s) sigs.Add(Tuple.Create(sg, f.d, f.m));
                    else if (name.StartsWith("dx::HitObject::", StringComparison.Ordinal))
                    {
                        var hm = _db.methods["hitobject"].FirstOrDefault(x => x.n == bare);
                        if (hm != null) foreach (var sg in hm.s) sigs.Add(Tuple.Create(sg, hm.d, hm.m));
                    }
                }
            }
            if (sigs.Count == 0) return null;
            var arr = new JArray();
            int active = 0, best = int.MaxValue;
            for (int i = 0; i < sigs.Count; i++)
            {
                string label = CleanSig(sigs[i].Item1);
                var plist = ParamLabels(label);
                var pa = new JArray(plist.Select(x => new JObject { ["label"] = x }));
                var si = new JObject { ["label"] = label, ["parameters"] = pa };
                if (!string.IsNullOrEmpty(sigs[i].Item2)) si["documentation"] = Markdown(DocText(null, sigs[i].Item2, sigs[i].Item3));
                arr.Add(si);
                int diff = Math.Abs(plist.Count - (commas + 1));
                if (plist.Count >= commas + 1 && diff < best) { best = diff; active = i; }
            }
            return new JObject { ["signatures"] = arr, ["activeSignature"] = active, ["activeParameter"] = commas };
        }

        private static string CleanSig(string sig)
        {
            string s = sig.Replace("[,", ",").Replace("[", "").Replace("]", "");
            return Regex.Replace(s, @"\s+", " ").Replace(" ,", ",");
        }

        private static List<string> ParamLabels(string label)
        {
            int o = label.IndexOf('(');
            int cl = label.LastIndexOf(')');
            var res = new List<string>();
            if (o < 0 || cl <= o) return res;
            string inner = label.Substring(o + 1, cl - o - 1);
            int depth = 0, start = 0;
            for (int i = 0; i < inner.Length; i++)
            {
                char ch = inner[i];
                if (ch == '<' || ch == '(') depth++;
                else if (ch == '>' || ch == ')') depth--;
                else if (ch == ',' && depth == 0) { res.Add(inner.Substring(start, i - start).Trim()); start = i + 1; }
            }
            if (inner.Substring(start).Trim().Length > 0) res.Add(inner.Substring(start).Trim());
            return res;
        }
    }
}
