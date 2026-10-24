using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace KHlsl.Server
{
    /// <summary>C++ の構造体のメンバー。Offset は、構造体の先頭からの絶対位置(バイト)。</summary>
    internal sealed class CMember
    {
        public string Name;
        public string Type;             // 表示用("float"、"DirectX::XMFLOAT3"、"Light")
        public int Offset;
        public int Size;                // 配列なら全体の大きさ
        public int Align;
        public int ArrayCount;          // 0 = 配列ではない
        public int Stride;              // 配列の要素の間隔
        public bool IsStruct;
        public int Line;                // 0 始まり
        public string File;
        public List<CMember> Fields = new List<CMember>();   // 構造体の中身(配列なら先頭の要素)

        public int End { get { return Offset + Size; } }
    }

    internal sealed class CStruct
    {
        public string Name;
        public string File;
        public int Line;
        public int Size;
        public int Align;
        public List<CMember> Members = new List<CMember>();
        public List<string> Problems = new List<string>();
        public bool Incomplete;
    }

    /// <summary>MSVC(x64)の規則で、C++ の構造体の大きさと、メンバーのオフセットを計算する。</summary>
    internal static class CppLayout
    {
        // ---- 型の表(大きさ, アラインメント) ----
        private static readonly Dictionary<string, int[]> Known = new Dictionary<string, int[]>
        {
            ["bool"] = new[] { 1, 1 }, ["char"] = new[] { 1, 1 }, ["signed char"] = new[] { 1, 1 }, ["unsigned char"] = new[] { 1, 1 },
            ["int8_t"] = new[] { 1, 1 }, ["uint8_t"] = new[] { 1, 1 }, ["byte"] = new[] { 1, 1 },
            ["wchar_t"] = new[] { 2, 2 }, ["char16_t"] = new[] { 2, 2 }, ["short"] = new[] { 2, 2 }, ["unsigned short"] = new[] { 2, 2 },
            ["int16_t"] = new[] { 2, 2 }, ["uint16_t"] = new[] { 2, 2 }, ["half"] = new[] { 2, 2 },
            ["int"] = new[] { 4, 4 }, ["unsigned"] = new[] { 4, 4 }, ["unsigned int"] = new[] { 4, 4 }, ["long"] = new[] { 4, 4 }, ["unsigned long"] = new[] { 4, 4 },
            ["int32_t"] = new[] { 4, 4 }, ["uint32_t"] = new[] { 4, 4 }, ["float"] = new[] { 4, 4 }, ["char32_t"] = new[] { 4, 4 },
            ["UINT"] = new[] { 4, 4 }, ["DWORD"] = new[] { 4, 4 }, ["INT"] = new[] { 4, 4 }, ["BOOL"] = new[] { 4, 4 }, ["FLOAT"] = new[] { 4, 4 },
            ["long long"] = new[] { 8, 8 }, ["unsigned long long"] = new[] { 8, 8 }, ["int64_t"] = new[] { 8, 8 }, ["uint64_t"] = new[] { 8, 8 },
            ["double"] = new[] { 8, 8 }, ["size_t"] = new[] { 8, 8 }, ["ptrdiff_t"] = new[] { 8, 8 }, ["uintptr_t"] = new[] { 8, 8 }, ["intptr_t"] = new[] { 8, 8 },
            ["UINT64"] = new[] { 8, 8 }, ["UINT8"] = new[] { 1, 1 }, ["UINT16"] = new[] { 2, 2 },
            // DirectXMath
            ["XMFLOAT2"] = new[] { 8, 4 }, ["XMFLOAT3"] = new[] { 12, 4 }, ["XMFLOAT4"] = new[] { 16, 4 },
            ["XMINT2"] = new[] { 8, 4 }, ["XMINT3"] = new[] { 12, 4 }, ["XMINT4"] = new[] { 16, 4 },
            ["XMUINT2"] = new[] { 8, 4 }, ["XMUINT3"] = new[] { 12, 4 }, ["XMUINT4"] = new[] { 16, 4 },
            ["XMFLOAT3X3"] = new[] { 36, 4 }, ["XMFLOAT4X3"] = new[] { 48, 4 }, ["XMFLOAT3X4"] = new[] { 48, 4 }, ["XMFLOAT4X4"] = new[] { 64, 4 },
            ["XMFLOAT2A"] = new[] { 8, 16 }, ["XMFLOAT3A"] = new[] { 12, 16 }, ["XMFLOAT4A"] = new[] { 16, 16 },
            ["XMINT2A"] = new[] { 8, 16 }, ["XMUINT2A"] = new[] { 8, 16 },
            ["XMFLOAT4X4A"] = new[] { 64, 16 }, ["XMFLOAT4X3A"] = new[] { 48, 16 }, ["XMFLOAT3X4A"] = new[] { 48, 16 },
            ["XMVECTOR"] = new[] { 16, 16 }, ["XMMATRIX"] = new[] { 64, 16 }, ["XMVECTORF32"] = new[] { 16, 16 }, ["XMVECTORI32"] = new[] { 16, 16 },
            ["XMCOLOR"] = new[] { 4, 4 }, ["XMHALF2"] = new[] { 4, 2 }, ["XMHALF4"] = new[] { 8, 2 },
            // SimpleMath
            ["Vector2"] = new[] { 8, 4 }, ["Vector3"] = new[] { 12, 4 }, ["Vector4"] = new[] { 16, 4 }, ["Matrix"] = new[] { 64, 4 },
            ["Quaternion"] = new[] { 16, 4 }, ["Color"] = new[] { 16, 4 }, ["Plane"] = new[] { 16, 4 }, ["Ray"] = new[] { 24, 4 }, ["Rectangle"] = new[] { 16, 4 },
        };

        private static readonly string[] Namespaces = { "DirectX::SimpleMath::", "DirectX::", "SimpleMath::", "std::" };

        // ---- 定義の収集 ----
        internal sealed class Def
        {
            public string Name, Base;
            public CBufferLayout.Source Src;
            public int BodyStart, BodyEnd, Line;
            public int AlignAs;          // struct 自体の alignas(0 = なし)
            public int Pack;             // #pragma pack の値(0 = 既定)
            public bool IsUnion;
        }

        internal sealed class Table
        {
            internal Dictionary<string, Def> Structs = new Dictionary<string, Def>();
            internal Dictionary<string, string> Aliases = new Dictionary<string, string>();
            internal Dictionary<string, string> Constants = new Dictionary<string, string>();
            internal HashSet<string> Unresolved = new HashSet<string>();
        }

        private static readonly Regex RxStruct = new Regex(@"\b(?<k>struct|class|union)\s+(?:alignas\s*\(\s*(?<a>\d+)\s*\)\s*)?(?:__declspec\s*\(\s*align\s*\(\s*(?<d>\d+)\s*\)\s*\)\s*)?(?<n>[A-Za-z_]\w*)", RegexOptions.Compiled);
        private static readonly Regex RxTypedef = new Regex(@"\btypedef\s+(?<t>[^;{}]+?)\s+(?<n>[A-Za-z_]\w*)\s*;", RegexOptions.Compiled);
        private static readonly Regex RxUsing = new Regex(@"\busing\s+(?<n>[A-Za-z_]\w*)\s*=\s*(?<t>[^;{}]+);", RegexOptions.Compiled);
        private static readonly Regex RxConst = new Regex(@"\b(?:static\s+)?(?:constexpr|const)\s+(?:inline\s+)?(?:int|unsigned|unsigned\s+int|uint32_t|int32_t|size_t|UINT)\s+(?<n>[A-Za-z_]\w*)\s*=\s*(?<v>[^;]+);", RegexOptions.Compiled);
        private static readonly Regex RxDefine = new Regex(@"^[ \t]*#[ \t]*define[ \t]+(?<n>[A-Za-z_]\w*)[ \t]+(?<v>[\w\s+\-*/()]+?)[ \t]*$", RegexOptions.Compiled | RegexOptions.Multiline);
        private static readonly Regex RxPack = new Regex(@"#\s*pragma\s+pack\s*\(\s*(?<a>[^)]*)\)", RegexOptions.Compiled);

        public static Table Collect(IEnumerable<CBufferLayout.Source> sources)
        {
            var table = new Table();
            foreach (var src in sources)
            {
                string m = src.Masked;
                foreach (Match x in RxTypedef.Matches(m)) table.Aliases[x.Groups["n"].Value] = Clean(x.Groups["t"].Value);
                foreach (Match x in RxUsing.Matches(m)) table.Aliases[x.Groups["n"].Value] = Clean(x.Groups["t"].Value);
                foreach (Match x in RxConst.Matches(m)) table.Constants[x.Groups["n"].Value] = x.Groups["v"].Value.Trim();
                foreach (Match x in RxDefine.Matches(m)) table.Constants[x.Groups["n"].Value] = x.Groups["v"].Value.Trim();

                // #pragma pack の履歴(位置順)
                var packs = new List<Tuple<int, string>>();
                foreach (Match x in RxPack.Matches(m)) packs.Add(Tuple.Create(x.Index, x.Groups["a"].Value.Trim()));

                foreach (Match x in RxStruct.Matches(m))
                {
                    int p = x.Index + x.Length;
                    int brace = -1;
                    for (int i = p; i < m.Length; i++)
                    {
                        char c = m[i];
                        if (c == '{') { brace = i; break; }
                        if (c == ';' || c == '}' || c == '(' || c == '=') break;
                    }
                    if (brace < 0) continue;
                    string between = m.Substring(p, brace - p);
                    if (!Regex.IsMatch(between, @"^\s*(?:final\s*)?(?::\s*(?:public\s+|private\s+|protected\s+)?[\w:]+\s*)?$")) continue;
                    int end = MatchBrace(m, brace);
                    if (end < 0) continue;
                    string name = x.Groups["n"].Value;
                    var def = new Def
                    {
                        Name = name, Src = src, BodyStart = brace + 1, BodyEnd = end,
                        Line = LineOf(src, x.Groups["n"].Index), IsUnion = x.Groups["k"].Value == "union"
                    };
                    var bm = Regex.Match(between, @":\s*(?:public\s+|private\s+|protected\s+)?([\w:]+)");
                    if (bm.Success) def.Base = StripNs(bm.Groups[1].Value);
                    if (x.Groups["a"].Success) def.AlignAs = int.Parse(x.Groups["a"].Value);
                    else if (x.Groups["d"].Success) def.AlignAs = int.Parse(x.Groups["d"].Value);
                    else
                    {
                        // alignas(16) struct Foo { ... }
                        int from = Math.Max(0, x.Index - 40);
                        var am = Regex.Match(m.Substring(from, x.Index - from), @"alignas\s*\(\s*(\d+)\s*\)\s*$");
                        if (am.Success) def.AlignAs = int.Parse(am.Groups[1].Value);
                    }
                    def.Pack = PackAt(packs, x.Index);
                    table.Structs[name] = def;
                }
            }
            return table;
        }

        private static int PackAt(List<Tuple<int, string>> packs, int pos)
        {
            var stack = new Stack<int>();
            int cur = 0;
            foreach (var pk in packs)
            {
                if (pk.Item1 > pos) break;
                string a = pk.Item2;
                if (a.Length == 0) { cur = 0; continue; }
                var parts = a.Split(',').Select(x => x.Trim()).ToList();
                if (parts[0] == "push") { stack.Push(cur); if (parts.Count > 1) { int n; cur = int.TryParse(parts[parts.Count - 1], out n) ? n : cur; } }
                else if (parts[0] == "pop") { cur = stack.Count > 0 ? stack.Pop() : 0; }
                else { int n; if (int.TryParse(parts[0], out n)) cur = n; }
            }
            return cur;
        }

        private static string Clean(string s) { return Regex.Replace(s, @"\s+", " ").Trim(); }

        private static string StripNs(string t)
        {
            foreach (var ns in Namespaces) if (t.StartsWith(ns, StringComparison.Ordinal)) t = t.Substring(ns.Length);
            if (t.StartsWith("::", StringComparison.Ordinal)) t = t.Substring(2);
            return t;
        }

        private static int LineOf(CBufferLayout.Source s, int offset)
        {
            int idx = s.LineStarts.BinarySearch(offset);
            if (idx < 0) idx = ~idx - 1;
            return idx;
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

        /// <summary>ソースにある struct / class の一覧(定義の順)。</summary>
        public static List<string> StructNames(Table t, string file)
        {
            return t.Structs.Values.Where(d => d.Src.Path == file && !d.IsUnion).OrderBy(d => d.Line).Select(d => d.Name).ToList();
        }

        public static bool Has(Table t, string name) { return t.Structs.ContainsKey(name); }

        public static string StructAt(Table t, string file, int line)
        {
            // 行が含まれる最も内側の struct
            Def best = null;
            foreach (var d in t.Structs.Values)
            {
                if (d.Src.Path != file) continue;
                int l0 = LineOf(d.Src, d.BodyStart), l1 = LineOf(d.Src, d.BodyEnd);
                if (line >= d.Line && line <= l1 && (best == null || d.Line > best.Line)) best = d;
            }
            return best == null ? null : best.Name;
        }

        // ---- 配置 ----
        private sealed class Decl
        {
            public string TypeText, Name;
            public List<string> Dims = new List<string>();
            public int AlignAs;
            public int Line;
            public bool Bitfield;
        }

        public static CStruct Layout(Table table, string name)
        {
            Def def;
            if (!table.Structs.TryGetValue(name, out def)) return null;
            var result = new CStruct { Name = def.Name, File = def.Src.Path, Line = def.Line };
            int align, size;
            var members = LayoutDef(table, def, 0, result, out size, out align, 0);
            if (members == null) { result.Incomplete = true; return result; }
            result.Members = members;
            result.Size = size;
            result.Align = align;
            if (table.Unresolved.Count > 0)
                result.Problems.Add("配列の要素数 " + string.Join(", ", table.Unresolved.Select(x => "'" + x + "'")) + " を解決できなかったので、1 として数えました");
            table.Unresolved.Clear();
            return result;
        }

        private static List<CMember> LayoutDef(Table table, Def def, int baseOffset, CStruct report, out int size, out int align, int depth)
        {
            size = 0; align = 1;
            if (depth > 12) { report.Problems.Add("入れ子が深すぎます"); return null; }
            if (def.IsUnion) { report.Problems.Add("union は計算できません(" + def.Name + ")"); return null; }
            var members = new List<CMember>();
            int cur = 0;
            int pack = def.Pack;

            if (def.Base != null)
            {
                Def bd;
                if (table.Structs.TryGetValue(def.Base, out bd))
                {
                    int bs, ba;
                    var bm = LayoutDef(table, bd, baseOffset, report, out bs, out ba, depth + 1);
                    if (bm == null) return null;
                    members.AddRange(bm);
                    // 中身のない基底クラスは、場所を取らない(空基底最適化)
                    cur = bm.Count == 0 ? 0 : bs;
                    if (bm.Count > 0) align = Math.Max(align, ba);
                }
                else { report.Problems.Add("基底クラス '" + def.Base + "' の定義が見つかりません"); return null; }
            }

            foreach (var d in ParseDecls(def))
            {
                if (d.Bitfield) { report.Problems.Add("ビット フィールドは計算できません('" + d.Name + "')"); return null; }
                int mAlign, mSize, count;
                List<CMember> fields = null;
                string problem;
                if (!TypeInfo(table, d.TypeText, depth, report, out mSize, out mAlign, out fields, out problem))
                {
                    report.Problems.Add(problem ?? ("型 '" + d.TypeText + "' を知らないので、'" + d.Name + "' の大きさが分かりません"));
                    return null;
                }
                count = ArrayCountOf(table, d);
                // #pragma pack は、自然なアラインメント(8 以下)だけを小さくする。alignas や XMVECTOR など 16 以上の指定は、そのまま
                int effAlign = (pack > 0 && mAlign <= 8) ? Math.Min(mAlign, pack) : mAlign;
                if (d.AlignAs > effAlign) effAlign = d.AlignAs;
                cur = (cur + effAlign - 1) / effAlign * effAlign;
                var mem = new CMember
                {
                    Name = d.Name, Type = d.TypeText, Offset = baseOffset + cur, Align = effAlign, ArrayCount = count,
                    File = def.Src.Path, Line = d.Line, IsStruct = fields != null
                };
                mem.Stride = count > 0 ? mSize : 0;
                mem.Size = count > 0 ? mSize * count : mSize;
                if (fields != null)
                    mem.Fields = fields.Select(f => ShiftCopy(f, baseOffset + cur - 0)).ToList();
                members.Add(mem);
                cur += mem.Size;
                align = Math.Max(align, effAlign);
            }
            if (def.AlignAs > align) align = def.AlignAs;
            if (members.Count == 0 && def.Base == null) { size = 1; return members; }
            size = (cur + align - 1) / align * align;
            return members;
        }

        private static CMember ShiftCopy(CMember f, int by)
        {
            var c = new CMember
            {
                Name = f.Name, Type = f.Type, Offset = f.Offset + by, Size = f.Size, Align = f.Align, ArrayCount = f.ArrayCount,
                Stride = f.Stride, IsStruct = f.IsStruct, Line = f.Line, File = f.File
            };
            c.Fields = f.Fields.Select(x => ShiftCopy(x, by)).ToList();
            return c;
        }

        /// <summary>型の大きさ・アラインメントと、構造体なら、中身(先頭からの位置)。</summary>
        private static bool TypeInfo(Table table, string typeText, int depth, CStruct report, out int size, out int align, out List<CMember> fields, out string problem)
        {
            size = 0; align = 1; fields = null; problem = null;
            string t = Clean(typeText);
            // ポインター・参照は 8 バイト
            if (t.EndsWith("*", StringComparison.Ordinal) || t.EndsWith("&", StringComparison.Ordinal)) { size = 8; align = 8; return true; }
            t = StripNs(t);
            t = Regex.Replace(t, @"^(?:struct|class|enum|const|volatile)\s+", "");
            for (int i = 0; i < 8 && table.Aliases.ContainsKey(t); i++) t = StripNs(table.Aliases[t]);

            int[] k;
            if (Known.TryGetValue(t, out k)) { size = k[0]; align = k[1]; return true; }

            // std::array<T, N>
            var am = Regex.Match(t, @"^array\s*<\s*(?<t>.+?)\s*,\s*(?<n>[^,<>]+?)\s*>$");
            if (am.Success)
            {
                int es, ea; List<CMember> ef; string pr;
                if (!TypeInfo(table, am.Groups["t"].Value, depth + 1, report, out es, out ea, out ef, out pr)) { problem = pr; return false; }
                int n;
                if (!TryEval(table, am.Groups["n"].Value, 0, out n)) n = 1;
                size = es * n; align = ea;
                return true;
            }

            Def def;
            if (table.Structs.TryGetValue(t, out def))
            {
                int s, a;
                var m = LayoutDef(table, def, 0, report, out s, out a, depth + 1);
                if (m == null) return false;
                size = s; align = a; fields = m;
                return true;
            }
            problem = "型 '" + typeText.Trim() + "' を知らないので、計算できません";
            return false;
        }

        // ---- メンバーの宣言の読み取り ----
        private static readonly HashSet<string> SkipWords = new HashSet<string> { "static", "typedef", "using", "friend", "enum", "template", "virtual", "public", "private", "protected", "operator", "constexpr", "inline", "extern" };
        private static readonly HashSet<string> DropWords = new HashSet<string> { "const", "volatile", "mutable", "alignas_dummy", "struct", "class" };

        private static List<Decl> ParseDecls(Def def)
        {
            var list = new List<Decl>();
            string m = def.Src.Masked;
            int depth = 0, from = def.BodyStart;
            for (int i = def.BodyStart; i < def.BodyEnd; i++)
            {
                char c = m[i];
                if (c == '{' || c == '(' || c == '[') depth++;
                else if (c == '}' || c == ')' || c == ']')
                {
                    depth--;
                    // 関数の本体("void f() { ... }")は、";" なしで終わる。そこで宣言を区切る
                    if (c == '}' && depth <= 0 && Regex.IsMatch(m.Substring(from, i - from + 1), @"\)\s*(?:const\s*)?(?:noexcept\s*)?(?:override\s*)?(?:final\s*)?\{"))
                    {
                        from = i + 1; depth = 0;
                    }
                }
                else if (c == ';' && depth <= 0)
                {
                    AddDecls(list, def, from, i);
                    from = i + 1; depth = 0;
                }

            }
            return list;
        }

        private static void AddDecls(List<Decl> list, Def def, int from, int to)
        {
            string raw = def.Src.Masked.Substring(from, to - from);
            // アクセス指定子("public:")を落とす
            string text = Regex.Replace(raw, @"\b(?:public|private|protected)\s*:", " ");
            // 入れ子の定義 "struct X { ... } name" は、名前だけにする
            text = ReplaceNestedDefinition(text);
            text = Regex.Replace(text, @"\[\[[^\]]*\]\]", " ");
            text = Regex.Replace(text, @"\s+", " ").Trim();
            if (text.Length == 0) return;
            // 初期化子: "= 値" と、"{ 値 }"
            int eq = text.IndexOf('=');
            if (eq >= 0) text = text.Substring(0, eq).Trim();
            text = Regex.Replace(text, @"\s*\{[^{}]*\}\s*$", "");
            if (text.Contains("(") && !Regex.IsMatch(text, @"alignas\s*\(")) return;      // 関数
            string first = Regex.Match(text, @"^[A-Za-z_]\w*").Value;
            if (SkipWords.Contains(first)) return;

            int alignAs = 0;
            var am = Regex.Match(text, @"alignas\s*\(\s*(?<n>\d+)\s*\)");
            if (am.Success) { alignAs = int.Parse(am.Groups["n"].Value); text = text.Remove(am.Index, am.Length).Trim(); }
            else
            {
                var dm = Regex.Match(text, @"__declspec\s*\(\s*align\s*\(\s*(?<n>\d+)\s*\)\s*\)");
                if (dm.Success) { alignAs = int.Parse(dm.Groups["n"].Value); text = text.Remove(dm.Index, dm.Length).Trim(); }
            }
            if (text.Contains("(")) return;

            // "型 名前[配列][配列], 名前2" を分ける。型は、最初の宣言子の手前まで
            var dm2 = Regex.Match(text, @"^(?<type>.+?)\s+(?<rest>[\*&]*\s*[A-Za-z_]\w*\s*(?:\[[^\]]*\]\s*)*(?::\s*\d+)?(?:\s*,.*)?)$");
            if (!dm2.Success) return;
            string type = dm2.Groups["type"].Value;
            string rest = dm2.Groups["rest"].Value;
            // 型の中の const などを落とす
            type = string.Join(" ", type.Split(' ').Where(w => !DropWords.Contains(w)));
            type = Regex.Replace(type, @"\s*::\s*", "::");
            type = Regex.Replace(type, @"\s*<\s*", "<").Replace(" >", ">");
            type = type.Replace(" *", "*").Replace(" &", "&");
            int lineBase = LineOf(def.Src, from + Math.Max(0, raw.IndexOf(rest.TrimStart('*', '&', ' '), StringComparison.Ordinal)));

            foreach (string part in SplitTop(rest, ','))
            {
                var pm = Regex.Match(part.Trim(), @"^(?<p>[\*&]*)\s*(?<n>[A-Za-z_]\w*)\s*(?<a>(?:\[[^\]]*\]\s*)*)(?::\s*(?<b>\d+))?$");
                if (!pm.Success) continue;
                var d = new Decl
                {
                    TypeText = type + pm.Groups["p"].Value, Name = pm.Groups["n"].Value, AlignAs = alignAs, Line = lineBase,
                    Bitfield = pm.Groups["b"].Success
                };
                foreach (Match a in Regex.Matches(pm.Groups["a"].Value, @"\[\s*([^\]]*)\s*\]")) d.Dims.Add(a.Groups[1].Value.Trim());
                list.Add(d);
            }
        }

        private static string ReplaceNestedDefinition(string text)
        {
            int open = text.IndexOf('{');
            if (open < 0) return text;
            var head = Regex.Match(text.Substring(0, open), @"(?:struct|class|union)\s+([A-Za-z_]\w*)\s*$");
            if (!head.Success) return text;
            int depth = 0, close = -1;
            for (int i = open; i < text.Length; i++)
            {
                if (text[i] == '{') depth++;
                else if (text[i] == '}') { depth--; if (depth == 0) { close = i; break; } }
            }
            if (close < 0) return text;
            return text.Substring(0, head.Index) + head.Groups[1].Value + " " + text.Substring(close + 1);
        }

        private static IEnumerable<string> SplitTop(string s, char sep)
        {
            int depth = 0, start = 0;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '(' || c == '[' || c == '{' || c == '<') depth++;
                else if (c == ')' || c == ']' || c == '}' || c == '>') depth--;
                else if (c == sep && depth == 0) { yield return s.Substring(start, i - start); start = i + 1; }
            }
            yield return s.Substring(start);
        }

        private static int ArrayCountOf(Table table, Decl d)
        {
            if (d.Dims.Count == 0) return 0;
            int count = 1;
            foreach (string dim in d.Dims)
            {
                int n;
                if (!TryEval(table, dim, 0, out n) || n < 1) { table.Unresolved.Add(dim); n = 1; }
                count *= n;
            }
            return count;
        }

        private static bool TryEval(Table table, string expr, int depth, out int value)
        {
            value = 0;
            if (depth > 8 || string.IsNullOrWhiteSpace(expr)) return false;
            string replaced = Regex.Replace(expr, @"[A-Za-z_]\w*", mm =>
            {
                string v; int inner;
                if (table.Constants.TryGetValue(mm.Value, out v) && TryEval(table, v, depth + 1, out inner)) return inner.ToString();
                return "?";
            });
            replaced = Regex.Replace(replaced, @"(\d+)[uUlL]+", "$1");
            if (replaced.Contains("?") || !Regex.IsMatch(replaced, @"^[\d\s+\-*/()]+$")) return false;
            try
            {
                object r = new System.Data.DataTable().Compute(replaced, null);
                value = (int)Math.Floor(Convert.ToDouble(r));
                return true;
            }
            catch (Exception) { return false; }
        }
    }
}
