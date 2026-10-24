using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace KHlsl.Server
{
    /// <summary>C++ の構造体と、HLSL の cbuffer(struct)のレイアウトを、メンバーごとに比べる。</summary>
    internal static class CppCompare
    {
        internal sealed class Node
        {
            public string Name, Type;
            public int Offset, Size, ArrayCount, Stride;
            public bool IsMatrix;
            public List<Node> Fields = new List<Node>();
        }

        internal sealed class Row
        {
            public string Path;
            public Node Cpp, Hlsl;
            public string Status;      // ok / offset / size / shifted / renamed / padding / onlyHlsl / onlyCpp
            public string Note = "";
        }

        public static Node FromCpp(CMember m)
        {
            var n = new Node { Name = m.Name, Type = m.Type, Offset = m.Offset, Size = m.Size, ArrayCount = m.ArrayCount, Stride = m.Stride };
            foreach (var f in m.Fields) n.Fields.Add(FromCpp(f));
            return n;
        }

        public static Node FromHlsl(LMember m)
        {
            var n = new Node { Name = m.Name, Type = CBufferOutput.TypeLabel(m), Offset = m.Offset, Size = m.Size, ArrayCount = m.ArrayCount, Stride = m.Stride, IsMatrix = m.IsMatrix };
            foreach (var f in m.Fields) n.Fields.Add(FromHlsl(f));
            return n;
        }

        // m_foo / foo_ / Foo / foo_bar / fooBar を、同じ名前とみなす
        public static string Normalize(string name)
        {
            string s = name;
            if (s.StartsWith("m_", StringComparison.Ordinal)) s = s.Substring(2);
            s = s.TrimEnd('_');
            return s.Replace("_", "").ToLowerInvariant();
        }

        private static bool LooksLikePadding(string name)
        {
            string n = Normalize(name);
            return n.StartsWith("pad") || n.StartsWith("reserved") || n.StartsWith("dummy") || n.StartsWith("unused") || n.StartsWith("filler");
        }

        public static List<Row> Compare(List<Node> cpp, List<Node> hlsl)
        {
            var rows = new List<Row>();
            CompareLevel(cpp, hlsl, "", rows);
            // 最初にずれた行から後ろは、同じ差(ずれ)の続きなら「続き」にする
            int? delta = null;
            foreach (var r in rows)
            {
                if (r.Cpp == null || r.Hlsl == null) continue;
                if (r.Status == "offset")
                {
                    int d = r.Hlsl.Offset - r.Cpp.Offset;
                    if (delta == null) delta = d;
                    else if (d == delta.Value) { r.Status = "shifted"; r.Note = "手前のずれ(" + Signed(d) + " バイト)の続き"; }
                    else delta = d;
                }
                else if (r.Status == "ok" || r.Status == "renamed") { }
            }
            return rows;
        }

        private static string Signed(int d) { return d > 0 ? "+" + d : d.ToString(); }

        private static void CompareLevel(List<Node> cpp, List<Node> hlsl, string prefix, List<Row> rows)
        {
            var usedCpp = new HashSet<Node>();
            var pairs = new List<Tuple<Node, Node, bool>>();       // (cpp, hlsl, 名前が違う)
            var cppBy = new Dictionary<string, Node>();
            foreach (var c in cpp) { string k = Normalize(c.Name); if (!cppBy.ContainsKey(k)) cppBy[k] = c; }
            var unmatchedHlsl = new List<Node>();
            foreach (var h in hlsl)
            {
                Node c;
                if (cppBy.TryGetValue(Normalize(h.Name), out c) && !usedCpp.Contains(c)) { usedCpp.Add(c); pairs.Add(Tuple.Create(c, h, false)); }
                else unmatchedHlsl.Add(h);
            }
            // 名前で対応しなかった物は、パディングを除いて、並びの順で対応づける
            var restCpp = cpp.Where(c => !usedCpp.Contains(c) && !LooksLikePadding(c.Name)).ToList();
            var paired = new Dictionary<Node, Node>();
            for (int i = 0; i < unmatchedHlsl.Count && i < restCpp.Count; i++)
            {
                paired[unmatchedHlsl[i]] = restCpp[i];
                usedCpp.Add(restCpp[i]);
            }

            foreach (var h in hlsl)
            {
                Tuple<Node, Node, bool> pr = pairs.FirstOrDefault(p => p.Item2 == h);
                Node c = pr != null ? pr.Item1 : null;
                bool renamed = false;
                if (c == null && paired.TryGetValue(h, out c)) renamed = true;
                string path = prefix + h.Name;
                if (c == null) { rows.Add(new Row { Path = path, Hlsl = h, Status = "onlyHlsl", Note = "C++ 側に、対応するメンバーが見つかりません" }); continue; }

                // 両方が構造体なら、中身を比べる
                if (h.Fields.Count > 0 && c.Fields.Count > 0 && h.ArrayCount == c.ArrayCount)
                {
                    CompareLevel(c.Fields, h.Fields, path + ".", rows);
                    continue;
                }
                rows.Add(MakeRow(path, c, h, renamed));
            }
            foreach (var c in cpp)
            {
                if (usedCpp.Contains(c)) continue;
                if (LooksLikePadding(c.Name)) rows.Add(new Row { Path = prefix + c.Name, Cpp = c, Status = "padding", Note = "パディング(HLSL には宣言がなく、隙間として扱われる)" });
                else rows.Add(new Row { Path = prefix + c.Name, Cpp = c, Status = "onlyCpp", Note = "HLSL 側に、対応するメンバーが見つかりません" });
            }
            // 並びを、オフセット順に直す(HLSL 側の行を先に、C++ だけの行はオフセットの位置へ)
            // ここでは、行の順を保つ(HLSL の宣言順)。C++ だけの行は後ろにある
        }

        private static Row MakeRow(string path, Node c, Node h, bool renamed)
        {
            var r = new Row { Path = path, Cpp = c, Hlsl = h, Status = "ok" };
            string note = "";
            if (c.Offset != h.Offset) { r.Status = "offset"; note = OffsetNote(c, h); }
            else if (c.Size != h.Size || (c.ArrayCount > 0 && c.Stride != h.Stride)) { r.Status = "size"; note = SizeNote(c, h); }
            if (renamed)
            {
                r.Note = "名前が違う(C++ の " + c.Name + ")ので、並びの順で対応づけた" + (note.Length > 0 ? "。" + note : "");
                if (r.Status == "ok") r.Status = "renamed";
            }
            else r.Note = note;
            return r;
        }

        private static string OffsetNote(Node c, Node h)
        {
            int d = h.Offset - c.Offset;
            if (Regex.IsMatch(c.Type, @"\bbool\b")) return "C++ の bool は 1 バイトです。HLSL は 4 バイトなので、uint32_t で受けます";
            if (d > 0 && h.Offset % 16 == 0)
                return "HLSL は、変数が 16 バイトの境界をまたげないので、" + h.Offset + " の先頭へ送ります。C++ にも " + d + " バイトのパディングが要ります";
            if (d > 0) return "HLSL のほうが " + d + " バイト後ろです。C++ に " + d + " バイトのパディングを入れます";
            return "C++ のほうが " + (-d) + " バイト後ろです。パディングが多いか、アラインメントが大きいことが原因です";
        }

        private static string SizeNote(Node c, Node h)
        {
            if (h.ArrayCount > 0 && c.ArrayCount > 0 && h.Stride != c.Stride)
                return "配列の要素の間隔が違います(HLSL " + h.Stride + " / C++ " + c.Stride + " バイト)。HLSL は要素ごとに 16 バイトのレジスタを使います";
            if (h.IsMatrix) return "行列の大きさが違います(HLSL " + h.Size + " / C++ " + c.Size + " バイト)。HLSL は、列(または行)ごとに 16 バイトのレジスタを使います";
            if (Regex.IsMatch(c.Type, @"\bbool\b")) return "C++ の bool は 1 バイトです。HLSL は 4 バイトです";
            return "大きさが違います(HLSL " + h.Size + " / C++ " + c.Size + " バイト)";
        }

        // ---- JSON ----
        public static JObject ToJson(CStruct cpp, LBlock hlsl, List<Row> rows)
        {
            var arr = new JArray();
            foreach (var r in rows) arr.Add(RowJson(r));
            var first = rows.FirstOrDefault(r => r.Status == "offset" || r.Status == "size" || r.Status == "onlyHlsl" || r.Status == "onlyCpp");
            int bad = rows.Count(r => r.Status == "offset" || r.Status == "size" || r.Status == "onlyHlsl" || r.Status == "onlyCpp");
            bool sizeOk = cpp.Size == hlsl.PaddedSize;
            return new JObject
            {
                ["cpp"] = CppBlockJson(cpp),
                ["hlslName"] = CBufferOutput.Title(hlsl),
                ["rows"] = arr,
                ["mismatches"] = bad,
                ["first"] = first == null ? null : first.Path,
                ["cppSize"] = cpp.Size,
                ["hlslSize"] = hlsl.Size,
                ["hlslPaddedSize"] = hlsl.PaddedSize,
                ["sizeOk"] = sizeOk,
                ["ok"] = bad == 0 && sizeOk
            };
        }

        private static JObject RowJson(Row r)
        {
            return new JObject
            {
                ["path"] = r.Path,
                ["status"] = r.Status,
                ["note"] = r.Note,
                ["cpp"] = r.Cpp == null ? null : new JObject { ["type"] = r.Cpp.Type, ["offset"] = r.Cpp.Offset, ["size"] = r.Cpp.Size },
                ["hlsl"] = r.Hlsl == null ? null : new JObject { ["type"] = r.Hlsl.Type, ["offset"] = r.Hlsl.Offset, ["size"] = r.Hlsl.Size },
            };
        }

        /// <summary>C++ の構造体を、レジスタの図(CBufferGrid)に渡せる形にする。</summary>
        public static JObject CppBlockJson(CStruct s)
        {
            var segments = new JArray();
            var members = new JArray();
            for (int i = 0; i < s.Members.Count; i++)
            {
                var m = s.Members[i];
                members.Add(new JObject { ["name"] = m.Name, ["file"] = m.File, ["line"] = m.Line });
                Walk(m, m.Name, i, segments);
            }
            int padded = (s.Size + 15) / 16 * 16;
            return new JObject
            {
                ["title"] = "C++ " + s.Name,
                ["name"] = s.Name,
                ["file"] = s.File,
                ["line"] = s.Line,
                ["size"] = s.Size,
                ["paddedSize"] = padded,
                ["incomplete"] = s.Incomplete,
                ["problems"] = new JArray(s.Problems),
                ["members"] = members,
                ["segments"] = segments,
            };
        }

        private static void Walk(CMember m, string path, int group, JArray list)
        {
            int count = m.ArrayCount > 0 ? m.ArrayCount : 1;
            for (int i = 0; i < count; i++)
            {
                string p = m.ArrayCount > 0 ? path + "[" + i + "]" : path;
                int off = m.Offset + i * (m.ArrayCount > 0 ? m.Stride : 0);
                if (m.IsStruct && m.Fields.Count > 0)
                {
                    foreach (var f in m.Fields) Walk(Shift(f, i * (m.ArrayCount > 0 ? m.Stride : 0)), p + "." + f.Name, group, list);
                }
                else
                {
                    int size = m.ArrayCount > 0 ? m.Stride : m.Size;
                    list.Add(new JObject { ["path"] = p, ["type"] = m.Type, ["offset"] = off, ["size"] = size, ["group"] = group });
                }
            }
        }

        private static CMember Shift(CMember f, int by)
        {
            var c = new CMember
            {
                Name = f.Name, Type = f.Type, Offset = f.Offset + by, Size = f.Size, Align = f.Align, ArrayCount = f.ArrayCount,
                Stride = f.Stride, IsStruct = f.IsStruct, Line = f.Line, File = f.File
            };
            c.Fields = f.Fields.Select(x => Shift(x, by)).ToList();
            return c;
        }
    }
}
