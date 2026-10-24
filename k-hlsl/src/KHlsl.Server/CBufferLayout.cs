using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KHlsl.Server
{
    /// <summary>レイアウトを出すときの設定(DXC の引数や #pragma に当たる物)。</summary>
    internal sealed class LayoutOptions
    {
        /// <summary>-enable-16bit-types。half と min16xxx が 2 バイトになる。</summary>
        public bool Enable16Bit;
        /// <summary>-Zpr または #pragma pack_matrix(row_major)。既定は列優先。</summary>
        public bool RowMajorDefault;
    }

    /// <summary>レイアウトの 1 メンバー。Offset は、バッファの先頭からの絶対位置(バイト)。</summary>
    internal sealed class LMember
    {
        public string Name;
        public string Type;             // 表示用の型名("float3"、"Light"、"float4x4")
        public int Offset;
        public int Size;                // 配列なら全体の大きさ
        public int ArrayCount;          // 0 = 配列ではない
        public int Stride;              // 配列の要素の間隔(バイト)
        public int Rows, Cols;          // 行列のとき(float3x4 なら Rows=3, Cols=4)
        public int Comps;               // ベクトルの成分数。スカラーは 1
        public int ElemSize;            // 成分 1 つのバイト数
        public char Scalar;             // 'f' 浮動小数点 / 'i' 符号つき整数 / 'u' 符号なし整数 / 'b' bool
        public bool RowMajor;
        public bool IsStruct;
        public bool HasPackoffset;
        public bool MinPrecision;       // min16float など(16 ビット型を有効にしていないとき、専用のレジスタに入る)
        public string Decl;             // 元の宣言("float3 eye;")
        public string File;
        public int Line;                // 0 始まり
        public List<LMember> Fields = new List<LMember>();   // 構造体の中身(配列なら先頭の要素)

        public bool IsMatrix { get { return Rows > 0; } }
        /// <summary>16 バイトの境界から始まらなければならない型(配列・行列・構造体・16 バイトを超えるベクトル)。</summary>
        public bool NeedsRegisterStart { get { return ArrayCount > 0 || IsMatrix || IsStruct || Size > 16; } }
        public int End { get { return Offset + Size; } }
        public LMember ShallowCopy() { return (LMember)MemberwiseClone(); }
    }

    internal sealed class LBlock
    {
        public string Kind;             // "cbuffer" / "tbuffer" / "ConstantBuffer" / "struct"
        public string Name;
        public string TypeName;         // ConstantBuffer<T> の T
        public string File;
        public int Line;
        public List<LMember> Members = new List<LMember>();
        public int Size;                // 最後のメンバーの終わり
        public bool Incomplete;         // 知らない型があって、計算できなかった
        public bool UsesPackoffset;
        public List<string> Problems = new List<string>();

        public int PaddedSize { get { return (Size + 15) / 16 * 16; } }
    }

    /// <summary>cbuffer / ConstantBuffer&lt;T&gt; / struct のパッキング(16 バイトのレジスタ)を計算する。</summary>
    internal static class CBufferLayout
    {
        // ---- 型の表 ----
        private sealed class ScalarInfo { public int Size; public char Kind; public bool Half; }
        private static readonly Dictionary<string, ScalarInfo> Scalars = new Dictionary<string, ScalarInfo>
        {
            ["bool"] = new ScalarInfo { Size = 4, Kind = 'b' },
            ["int"] = new ScalarInfo { Size = 4, Kind = 'i' },
            ["uint"] = new ScalarInfo { Size = 4, Kind = 'u' },
            ["dword"] = new ScalarInfo { Size = 4, Kind = 'u' },
            ["float"] = new ScalarInfo { Size = 4, Kind = 'f' },
            ["half"] = new ScalarInfo { Size = 4, Kind = 'f', Half = true },
            ["double"] = new ScalarInfo { Size = 8, Kind = 'f' },
            ["min16float"] = new ScalarInfo { Size = 4, Kind = 'f', Half = true },
            ["min10float"] = new ScalarInfo { Size = 4, Kind = 'f', Half = true },
            ["min16int"] = new ScalarInfo { Size = 4, Kind = 'i', Half = true },
            ["min12int"] = new ScalarInfo { Size = 4, Kind = 'i', Half = true },
            ["min16uint"] = new ScalarInfo { Size = 4, Kind = 'u', Half = true },
            ["float16_t"] = new ScalarInfo { Size = 2, Kind = 'f' },
            ["int16_t"] = new ScalarInfo { Size = 2, Kind = 'i' },
            ["uint16_t"] = new ScalarInfo { Size = 2, Kind = 'u' },
            ["int32_t"] = new ScalarInfo { Size = 4, Kind = 'i' },
            ["uint32_t"] = new ScalarInfo { Size = 4, Kind = 'u' },
            ["float32_t"] = new ScalarInfo { Size = 4, Kind = 'f' },
            ["int64_t"] = new ScalarInfo { Size = 8, Kind = 'i' },
            ["uint64_t"] = new ScalarInfo { Size = 8, Kind = 'u' },
            ["float64_t"] = new ScalarInfo { Size = 8, Kind = 'f' },
        };

        private static readonly Regex RxVecMat = new Regex(@"^(?<s>bool|int|uint|dword|float|half|double|min16float|min10float|min16int|min12int|min16uint|float16_t|int16_t|uint16_t|int32_t|uint32_t|float32_t|int64_t|uint64_t|float64_t)(?<a>[1-4])(?:x(?<b>[1-4]))?$", RegexOptions.Compiled);
        private static readonly Regex RxTemplVec = new Regex(@"^vector\s*<\s*(?<s>\w+)\s*,\s*(?<n>[1-4])\s*>$", RegexOptions.Compiled);
        private static readonly Regex RxTemplMat = new Regex(@"^matrix\s*<\s*(?<s>\w+)\s*,\s*(?<r>[1-4])\s*,\s*(?<c>[1-4])\s*>$", RegexOptions.Compiled);

        /// <summary>1 つのソース(マスク済みの本文)。</summary>
        internal sealed class Source
        {
            public string Path;
            public string Text;       // 元の本文
            public string Masked;     // コメントと文字列を空白にした本文
            public List<int> LineStarts;
        }

        internal sealed class StructDef
        {
            public string Name;
            public string Base;
            public Source Src;
            public int BodyStart, BodyEnd;      // { の次 〜 } の位置
            public int Line;
        }

        /// <summary>型の定義を集めた表。</summary>
        internal sealed class TypeTable
        {
            internal Dictionary<string, StructDef> Structs = new Dictionary<string, StructDef>();
            internal Dictionary<string, string> Aliases = new Dictionary<string, string>();
            internal Dictionary<string, string> Constants = new Dictionary<string, string>();   // #define N 4 / static const int N = 4;
            internal HashSet<string> Unresolved = new HashSet<string>();
            internal List<CBufDef> CBufs = new List<CBufDef>();
            internal List<CBufVar> CBufVars = new List<CBufVar>();
        }

        internal sealed class CBufDef { public string Kind, Name; public Source Src; public int BodyStart, BodyEnd, Line; }
        internal sealed class CBufVar { public string TypeName, Name; public Source Src; public int Line; }

        public static Source MakeSource(string path, string text)
        {
            var s = new Source { Path = path, Text = text, Masked = Analyzer.Mask(text) };
            s.LineStarts = Analyzer.LineStarts(text);
            return s;
        }

        private static int LineOf(Source s, int offset)
        {
            int idx = s.LineStarts.BinarySearch(offset);
            if (idx < 0) idx = ~idx - 1;
            return idx;
        }

        private static readonly Regex RxBlock = new Regex(@"\b(?<k>struct|class|cbuffer|tbuffer)\s+(?<n>[A-Za-z_]\w*)", RegexOptions.Compiled);
        private static readonly Regex RxTypedef = new Regex(@"\btypedef\s+(?<t>[^;{}]+?)\s+(?<n>[A-Za-z_]\w*)\s*;", RegexOptions.Compiled);
        private static readonly Regex RxUsing = new Regex(@"\busing\s+(?<n>[A-Za-z_]\w*)\s*=\s*(?<t>[^;{}]+);", RegexOptions.Compiled);
        private static readonly Regex RxDefineConst = new Regex(@"^[ \t]*#[ \t]*define[ \t]+(?<n>[A-Za-z_]\w*)[ \t]+(?<v>[\w\s+\-*/()]+?)[ \t]*$", RegexOptions.Compiled | RegexOptions.Multiline);
        private static readonly Regex RxConstInt = new Regex(@"\b(?:static\s+)?const\s+(?:int|uint|unsigned\s+int)\s+(?<n>[A-Za-z_]\w*)\s*=\s*(?<v>[^;]+);", RegexOptions.Compiled);
        private static readonly Regex RxConstBufVar = new Regex(@"\bConstantBuffer\s*<\s*(?<t>[A-Za-z_]\w*)\s*>\s+(?<n>[A-Za-z_]\w*)", RegexOptions.Compiled);

        /// <summary>ソースから struct / cbuffer / typedef / ConstantBuffer&lt;T&gt; を集める。</summary>
        public static TypeTable Collect(IEnumerable<Source> sources)
        {
            var table = new TypeTable();
            foreach (var src in sources)
            {
                string m = src.Masked;
                foreach (Match x in RxTypedef.Matches(m)) table.Aliases[x.Groups["n"].Value] = Regex.Replace(x.Groups["t"].Value, @"\s+", " ").Trim();
                foreach (Match x in RxUsing.Matches(m)) table.Aliases[x.Groups["n"].Value] = Regex.Replace(x.Groups["t"].Value, @"\s+", " ").Trim();
                foreach (Match x in RxDefineConst.Matches(m)) table.Constants[x.Groups["n"].Value] = x.Groups["v"].Value.Trim();
                foreach (Match x in RxConstInt.Matches(m)) table.Constants[x.Groups["n"].Value] = x.Groups["v"].Value.Trim();
                foreach (Match x in RxConstBufVar.Matches(m))
                    table.CBufVars.Add(new CBufVar { TypeName = x.Groups["t"].Value, Name = x.Groups["n"].Value, Src = src, Line = LineOf(src, x.Groups["n"].Index) });

                foreach (Match x in RxBlock.Matches(m))
                {
                    int p = x.Index + x.Length;
                    // 名前のあと、"{" までに ";" や "(" 以外が来るのは宣言ではない(": register(b0)" と ": Base" は許す)
                    int brace = -1;
                    for (int i = p; i < m.Length; i++)
                    {
                        char c = m[i];
                        if (c == '{') { brace = i; break; }
                        if (c == ';' || c == '}' || c == '=') break;
                    }
                    if (brace < 0) continue;
                    string between = m.Substring(p, brace - p);
                    if (!Regex.IsMatch(between, @"^\s*(?::\s*[\w:,\s<>]+?(?:\(\s*[\w\s,]*\))?\s*)?$")) continue;
                    int end = MatchBrace(m, brace);
                    if (end < 0) continue;
                    string kind = x.Groups["k"].Value;
                    string name = x.Groups["n"].Value;
                    int line = LineOf(src, x.Groups["n"].Index);
                    if (kind == "cbuffer" || kind == "tbuffer")
                        table.CBufs.Add(new CBufDef { Kind = kind, Name = name, Src = src, BodyStart = brace + 1, BodyEnd = end, Line = line });
                    else
                    {
                        string baseName = null;
                        var bm = Regex.Match(between, @"^\s*:\s*(?:public\s+)?([A-Za-z_]\w*)");
                        if (bm.Success) baseName = bm.Groups[1].Value;
                        table.Structs[name] = new StructDef { Name = name, Base = baseName, Src = src, BodyStart = brace + 1, BodyEnd = end, Line = line };
                    }
                }
            }
            return table;
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

        // ---- 配置 ----

        /// <summary>全ブロック(cbuffer・ConstantBuffer&lt;T&gt;・struct)のレイアウトを出す。</summary>
        public static List<LBlock> LayoutAll(TypeTable table, LayoutOptions opt, bool includeStructs)
        {
            var result = new List<LBlock>();
            foreach (var cb in table.CBufs)
                result.Add(LayoutBody(table, opt, cb.Kind, cb.Name, null, cb.Src, cb.BodyStart, cb.BodyEnd, cb.Line));
            foreach (var v in table.CBufVars)
            {
                var b = LayoutStruct(table, opt, v.TypeName);
                if (b == null) continue;
                b.Kind = "ConstantBuffer";
                b.Name = v.Name;
                b.TypeName = v.TypeName;
                b.File = v.Src.Path;
                b.Line = v.Line;
                result.Add(b);
            }
            if (includeStructs)
                foreach (var s in table.Structs.Values.OrderBy(s => s.Src.Path).ThenBy(s => s.Line))
                {
                    var b = LayoutStruct(table, opt, s.Name);
                    if (b != null) result.Add(b);
                }
            return result;
        }

        /// <summary>struct を、cbuffer の先頭に置いたときのレイアウト。</summary>
        public static LBlock LayoutStruct(TypeTable table, LayoutOptions opt, string name)
        {
            StructDef def;
            if (!table.Structs.TryGetValue(Resolve(table, name), out def)) return null;
            var b = LayoutBody(table, opt, "struct", def.Name, null, def.Src, def.BodyStart, def.BodyEnd, def.Line);
            if (def.Base != null)
            {
                var baseBlock = LayoutStruct(table, opt, def.Base);
                if (baseBlock != null)
                {
                    // 基底クラスのメンバーが先に来る。派生側を、その後ろへ置き直す
                    var ordered = new List<Decl>();
                    CollectDecls(table, def, ordered, 0);
                    b = LayoutDecls(table, opt, "struct", def.Name, null, def.Src, def.Line, ordered);
                }
            }
            return b;
        }

        private sealed class Decl
        {
            public string TypeText, Name, Packoffset, Text;
            public List<string> Dims = new List<string>();   // 配列の要素数("4"、"MAX_LIGHTS" など)
            public bool RowMajor, ColMajor;
            public Source Src;
            public int Line;
        }

        private static string Resolve(TypeTable table, string name)
        {
            for (int i = 0; i < 8 && table.Aliases.ContainsKey(name); i++) name = table.Aliases[name];
            return name;
        }

        private static void CollectDecls(TypeTable table, StructDef def, List<Decl> into, int depth)
        {
            if (depth > 8) return;
            StructDef bd;
            if (def.Base != null && table.Structs.TryGetValue(Resolve(table, def.Base), out bd)) CollectDecls(table, bd, into, depth + 1);
            into.AddRange(ParseDecls(def.Src, def.BodyStart, def.BodyEnd));
        }

        private static LBlock LayoutBody(TypeTable table, LayoutOptions opt, string kind, string name, string typeName, Source src, int start, int end, int line)
        {
            return LayoutDecls(table, opt, kind, name, typeName, src, line, ParseDecls(src, start, end));
        }

        private static readonly HashSet<string> Skip = new HashSet<string> { "static", "groupshared", "typedef", "using", "template", "enum" };
        private static readonly HashSet<string> Modifiers = new HashSet<string>
        {
            "const", "uniform", "volatile", "precise", "linear", "centroid", "nointerpolation", "noperspective", "sample",
            "shared", "extern", "snorm", "unorm", "globallycoherent", "inline", "export"
        };

        /// <summary>本体を ";" で区切って、宣言(型・名前・配列・packoffset)にする。メンバー関数と static は飛ばす。</summary>
        private static List<Decl> ParseDecls(Source src, int start, int end)
        {
            var list = new List<Decl>();
            string m = src.Masked;
            int depth = 0, from = start;
            for (int i = start; i < end; i++)
            {
                char c = m[i];
                if (c == '{' || c == '(' || c == '[' || c == '<') depth++;
                else if (c == '}' || c == ')' || c == ']' || c == '>') depth--;
                else if (c == ';' && depth <= 0)
                {
                    AddDecls(list, src, from, i);
                    from = i + 1;
                    depth = 0;
                }
            }
            return list;
        }

        private static void AddDecls(List<Decl> list, Source src, int from, int to)
        {
            string raw = src.Masked.Substring(from, to - from);
            string text = Regex.Replace(raw, @"\s+", " ").Trim();
            if (text.Length == 0) return;
            // 関数(本体つき・宣言とも)と、入れ子の定義は対象外
            if (text.Contains("{")) return;
            if (text.Contains("(") && !text.Contains("packoffset")) return;
            string[] words = Regex.Split(text, @"[\s<]+");
            if (Skip.Contains(words[0])) return;

            // packoffset(c1.y) を取り出す
            string pack = null;
            var pm = Regex.Match(text, @":\s*packoffset\s*\(\s*(?<p>[^)]*)\)");
            if (pm.Success) { pack = pm.Groups["p"].Value.Trim(); text = text.Remove(pm.Index, pm.Length).Trim(); }
            // register(...) とセマンティクス(": NAME")は捨てる
            text = Regex.Replace(text, @":\s*register\s*\([^)]*\)", "").Trim();

            // 初期値は捨てる
            int eq = IndexOfTopLevel(text, '=');
            if (eq >= 0) text = text.Substring(0, eq).Trim();

            // 型の部分(修飾子と型)と、宣言子(名前 [配列] : セマンティクス , ...)に分ける
            var tokens = new List<string>();
            int pos = 0;
            bool rowMajor = false, colMajor = false;
            string typeText = null;
            while (pos < text.Length)
            {
                while (pos < text.Length && char.IsWhiteSpace(text[pos])) pos++;
                int s = pos;
                while (pos < text.Length && (char.IsLetterOrDigit(text[pos]) || text[pos] == '_' || text[pos] == ':' && pos + 1 < text.Length && text[pos + 1] == ':')) pos++;
                if (pos == s) break;
                if (pos < text.Length && text[pos] == ':' ) { pos += 2; continue; }
                string w = text.Substring(s, pos - s);
                if (w == "row_major") { rowMajor = true; continue; }
                if (w == "column_major") { colMajor = true; continue; }
                if (Modifiers.Contains(w)) continue;
                // テンプレート引数 vector<float, 3> / matrix<float,3,4>
                int q = pos;
                while (q < text.Length && char.IsWhiteSpace(text[q])) q++;
                if (q < text.Length && text[q] == '<')
                {
                    int close = text.IndexOf('>', q);
                    if (close < 0) return;
                    w = w + text.Substring(q, close - q + 1);
                    pos = close + 1;
                }
                typeText = Regex.Replace(w, @"\s+", "");
                break;
            }
            if (typeText == null) return;
            string rest = text.Substring(pos).Trim();
            if (rest.Length == 0) return;
            foreach (string part in SplitTop(rest, ','))
            {
                string d = part.Trim();
                // ": SEMANTIC" を捨てる
                var sem = Regex.Match(d, @"^(?<n>[A-Za-z_]\w*)\s*(?<a>(?:\[[^\]]*\]\s*)*)\s*(?::\s*\w+)?$");
                if (!sem.Success) continue;
                var dims = new List<string>();
                foreach (Match a in Regex.Matches(sem.Groups["a"].Value, @"\[\s*([^\]]*)\s*\]"))
                    dims.Add(a.Groups[1].Value.Trim());
                int line = LineOf(src, from + Math.Max(0, raw.IndexOf(sem.Groups["n"].Value, StringComparison.Ordinal)));
                list.Add(new Decl
                {
                    TypeText = typeText, Name = sem.Groups["n"].Value, Dims = dims, Packoffset = pack,
                    RowMajor = rowMajor, ColMajor = colMajor, Src = src, Line = line,
                    Text = (Regex.Replace(src.Text.Substring(from, to - from), @"\s+", " ").Trim()) + ";"
                });
            }
        }

        private static int IndexOfTopLevel(string s, char ch)
        {
            int depth = 0;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (c == '(' || c == '[' || c == '{' || c == '<') depth++;
                else if (c == ')' || c == ']' || c == '}' || c == '>') depth--;
                else if (c == ch && depth == 0) return i;
            }
            return -1;
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

        private static LBlock LayoutDecls(TypeTable table, LayoutOptions opt, string kind, string name, string typeName, Source src, int line, List<Decl> decls)
        {
            var b = new LBlock { Kind = kind, Name = name, TypeName = typeName, File = src.Path, Line = line };
            int cur = 0;
            bool prevMin = false;
            foreach (var d in decls)
            {
                string problem;
                LMember mem = Place(table, opt, d, cur, prevMin, 0, out problem);
                prevMin = mem != null && mem.MinPrecision;
                if (mem == null)
                {
                    b.Incomplete = true;
                    b.Problems.Add("型 '" + d.TypeText + "' を知らないので、'" + d.Name + "' の大きさが分かりません");
                    continue;
                }
                if (mem.HasPackoffset) b.UsesPackoffset = true;
                b.Members.Add(mem);
                cur = mem.End;
            }
            b.Size = b.Members.Count == 0 ? 0 : b.Members.Max(x => x.End);
            if (table.Unresolved.Count > 0)
                b.Problems.Add("配列の要素数 " + string.Join(", ", table.Unresolved.Select(x => "'" + x + "'")) + " を解決できなかったので、1 として数えました");
            table.Unresolved.Clear();
            return b;
        }

        private static int Align16(int x) { return (x + 15) / 16 * 16; }

        /// <summary>配列の要素数(多次元は積)。0 は配列ではない。#define や const int で決めた数も解決する。</summary>
        private static int ArrayCountOf(TypeTable table, Decl d)
        {
            if (d.Dims.Count == 0) return 0;
            int count = 1;
            foreach (string dim in d.Dims)
            {
                int n;
                if (!TryEval(table, dim, 0, out n) || n < 1)
                {
                    table.Unresolved.Add(dim);
                    n = 1;
                }
                count *= n;
            }
            return count;
        }

        private static bool TryEval(TypeTable table, string expr, int depth, out int value)
        {
            value = 0;
            if (depth > 8 || string.IsNullOrWhiteSpace(expr)) return false;
            // 識別子を、定数の値に置き換える
            string replaced = Regex.Replace(expr, @"[A-Za-z_]\w*", m =>
            {
                string v;
                int inner;
                if (table.Constants.TryGetValue(m.Value, out v) && TryEval(table, v, depth + 1, out inner)) return inner.ToString();
                return "?";
            });
            if (replaced.Contains("?") || !Regex.IsMatch(replaced, @"^[\d\s+\-*/()]+$")) return false;
            try
            {
                object r = new System.Data.DataTable().Compute(replaced, null);
                value = (int)Math.Floor(Convert.ToDouble(r));
                return true;
            }
            catch (Exception) { return false; }
        }

        /// <summary>メンバーを cur 以降のどこに置くかを決めて、LMember を作る。</summary>
        private static LMember Place(TypeTable table, LayoutOptions opt, Decl d, int cur, bool prevMin, int depth, out string problem)
        {
            problem = null;
            if (depth > 12) { problem = "入れ子が深すぎます"; return null; }
            var mem = new LMember
            {
                Name = d.Name, Decl = d.Text, File = d.Src.Path, Line = d.Line, ArrayCount = ArrayCountOf(table, d),
                RowMajor = d.RowMajor || (!d.ColMajor && opt.RowMajorDefault)
            };
            string t = Resolve(table, d.TypeText);
            mem.Type = d.TypeText;

            int elemSize = 0, comps = 1, rows = 0, cols = 0;
            char kind = 'f';
            StructDef sdef = null;
            ScalarInfo si;
            Match vm = null;
            if (Scalars.TryGetValue(t, out si)) { elemSize = Sz(si, opt); kind = si.Kind; }
            else if ((vm = RxVecMat.Match(t)).Success)
            {
                si = Scalars[vm.Groups["s"].Value];
                elemSize = Sz(si, opt); kind = si.Kind;
                if (vm.Groups["b"].Success) { rows = int.Parse(vm.Groups["a"].Value); cols = int.Parse(vm.Groups["b"].Value); }
                else comps = int.Parse(vm.Groups["a"].Value);
            }
            else if ((vm = RxTemplVec.Match(t)).Success && Scalars.TryGetValue(Resolve(table, vm.Groups["s"].Value), out si))
            { elemSize = Sz(si, opt); kind = si.Kind; comps = int.Parse(vm.Groups["n"].Value); }
            else if ((vm = RxTemplMat.Match(t)).Success && Scalars.TryGetValue(Resolve(table, vm.Groups["s"].Value), out si))
            { elemSize = Sz(si, opt); kind = si.Kind; rows = int.Parse(vm.Groups["r"].Value); cols = int.Parse(vm.Groups["c"].Value); }
            else if (table.Structs.TryGetValue(t, out sdef)) { }
            else { problem = "unknown"; return null; }

            mem.ElemSize = elemSize; mem.Scalar = kind; mem.Comps = comps; mem.Rows = rows; mem.Cols = cols;
            mem.IsStruct = sdef != null;
            mem.MinPrecision = !opt.Enable16Bit && mem.ArrayCount == 0 && IsMinName(t, vm);

            // 1 要素の大きさ(先頭からのオフセットで測る)と、その中身を、仮に 0 番地へ置いて求める
            int elemBytes;       // 配列の 1 要素の大きさ
            var fields = new List<LMember>();
            if (sdef != null)
            {
                var inner = new List<Decl>();
                CollectDecls(table, sdef, inner, 0);
                int c2 = 0;
                bool fPrevMin = false;
                foreach (var fd in inner)
                {
                    string p2;
                    LMember fm = Place(table, opt, fd, c2, fPrevMin, depth + 1, out p2);
                    fPrevMin = fm != null && fm.MinPrecision;
                    if (fm == null) { problem = p2 ?? "unknown"; return null; }
                    fields.Add(fm);
                    c2 = fm.End;
                }
                elemBytes = fields.Count == 0 ? 0 : fields.Max(f => f.End);
            }
            else if (rows > 0)
            {
                // 行列: 主な方向のベクトルごとに 1 レジスタ(16 バイト)。最後のベクトルは、使う分だけ
                int vecs = mem.RowMajor ? rows : cols;
                int len = mem.RowMajor ? cols : rows;
                int me = Math.Max(4, elemSize);   // 16 ビットの行列も、要素 4 バイトで数える(DXC の実測)
                int stride = Align16(len * me);
                elemBytes = (vecs - 1) * stride + len * me;
            }
            else elemBytes = comps * elemSize;

            // packoffset があれば、そこへ置く。なければ規則どおり
            int offset;
            int po = ParsePackoffset(d.Packoffset);
            if (po >= 0) { offset = po; mem.HasPackoffset = true; }
            else if (mem.ArrayCount > 0 || mem.IsStruct || rows > 0) offset = Align16(cur);
            else
            {
                offset = cur;
                // min16float などは専用のレジスタに入る。前後が普通の型なら、レジスタの境界に揃える
                if (mem.MinPrecision != prevMin) offset = Align16(offset);
                if (elemSize > 1) offset = (offset + elemSize - 1) / elemSize * elemSize;
                if (elemBytes > 16) offset = Align16(offset);
                else if (offset % 16 + elemBytes > 16) offset = Align16(offset);
            }
            mem.Offset = offset;

            if (mem.ArrayCount > 0)
            {
                mem.Stride = Align16(elemBytes);
                mem.Size = (mem.ArrayCount - 1) * mem.Stride + elemBytes;
            }
            else mem.Size = elemBytes;

            if (sdef != null)
            {
                foreach (var f in fields) Shift(f, offset);
                mem.Fields = fields;
            }
            return mem;
        }

        private static bool IsMinName(string t, Match vm)
        {
            string baseName = vm != null && vm.Success && vm.Groups["s"].Success ? vm.Groups["s"].Value : t;
            return baseName.StartsWith("min16") || baseName.StartsWith("min12") || baseName.StartsWith("min10");
        }

        private static int Sz(ScalarInfo si, LayoutOptions opt)
        {
            if (si.Half && opt.Enable16Bit) return 2;
            return si.Size;
        }

        private static void Shift(LMember m, int by)
        {
            m.Offset += by;
            foreach (var f in m.Fields) Shift(f, by);
        }

        /// <summary>packoffset(c1.y) → バイト位置。指定がなければ -1。</summary>
        private static int ParsePackoffset(string p)
        {
            if (string.IsNullOrEmpty(p)) return -1;
            var m = Regex.Match(p, @"^c(?<r>\d+)(?:\.(?<c>[xyzwrgba]))?$");
            if (!m.Success) return -1;
            int reg = int.Parse(m.Groups["r"].Value);
            int comp = 0;
            if (m.Groups["c"].Success) comp = "xyzw".IndexOf(m.Groups["c"].Value[0]) >= 0 ? "xyzw".IndexOf(m.Groups["c"].Value[0]) : "rgba".IndexOf(m.Groups["c"].Value[0]);
            return reg * 16 + comp * 4;
        }

        // ---- 描画用の細かい区画 ----

        /// <summary>1 つの塗りつぶし区画(葉)。4 バイトの升目を、どのメンバーが使っているかを示す。</summary>
        internal sealed class Segment
        {
            public string Path;
            public string Type;
            public int Offset, Size;
            public int Group;         // 最上位のメンバーの番号(色分け用)
        }

        public static List<Segment> Segments(LBlock b)
        {
            var list = new List<Segment>();
            for (int i = 0; i < b.Members.Count; i++) Walk(b.Members[i], b.Members[i].Name, i, list);
            return list;
        }

        private static void Walk(LMember m, string path, int group, List<Segment> list)
        {
            int count = m.ArrayCount > 0 ? m.ArrayCount : 1;
            for (int i = 0; i < count; i++)
            {
                string p = m.ArrayCount > 0 ? path + "[" + i + "]" : path;
                int baseOffset = m.Offset + i * m.Stride;
                if (m.IsStruct)
                {
                    foreach (var f in m.Fields)
                    {
                        // 配列の i 番目の要素の位置は、先頭の要素の位置から i * Stride ずらした所
                        var shifted = Clone(f, i * m.Stride);
                        Walk(shifted, p + "." + f.Name, group, list);
                    }
                }
                else if (m.IsMatrix)
                {
                    int vecs = m.RowMajor ? m.Rows : m.Cols;
                    int len = m.RowMajor ? m.Cols : m.Rows;
                    int me = Math.Max(4, m.ElemSize);
                    int stride = Align16(len * me);
                    for (int v = 0; v < vecs; v++)
                        list.Add(new Segment { Path = p + (m.RowMajor ? " 行" : " 列") + v, Type = m.Type, Offset = baseOffset + v * stride, Size = len * me, Group = group });
                }
                else list.Add(new Segment { Path = p, Type = m.Type, Offset = baseOffset, Size = m.Comps * m.ElemSize, Group = group });
            }
        }

        private static LMember Clone(LMember f, int by)
        {
            var c = f.ShallowCopy();
            c.Offset = f.Offset + by;
            c.Fields = f.Fields.Select(x => Clone(x, by)).ToList();
            return c;
        }

        /// <summary>使われていないバイト(隙間)の合計。PaddedSize までの間で数える。</summary>
        public static int WastedBytes(LBlock b)
        {
            var used = new bool[b.PaddedSize];
            foreach (var s in Segments(b))
                for (int i = s.Offset; i < s.Offset + s.Size && i < used.Length; i++) used[i] = true;
            return used.Count(u => !u);
        }
    }
}
