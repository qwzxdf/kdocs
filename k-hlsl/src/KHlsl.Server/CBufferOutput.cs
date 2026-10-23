using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Newtonsoft.Json.Linq;

namespace KHlsl.Server
{
    /// <summary>レイアウトを、ホバーの文章・ビジュアライザー用の JSON・C++ の struct にする。</summary>
    internal static class CBufferOutput
    {
        public static string Register(int offset)
        {
            return "c" + offset / 16 + "." + "xyzw"[offset % 16 / 4] + (offset % 4 != 0 ? "+" + offset % 4 : "");
        }

        public static string TypeLabel(LMember m)
        {
            return m.Type + (m.ArrayCount > 0 ? "[" + m.ArrayCount + "]" : "");
        }

        public static string Title(LBlock b)
        {
            switch (b.Kind)
            {
                case "ConstantBuffer": return "ConstantBuffer<" + b.TypeName + "> " + b.Name;
                case "struct": return "struct " + b.Name;
                default: return b.Kind + " " + b.Name;
            }
        }

        public static string Summary(LBlock b)
        {
            int wasted = CBufferLayout.WastedBytes(b);
            return b.Size + " バイト(" + b.PaddedSize / 16 + " レジスタ)・隙間 " + wasted + " バイト";
        }

        /// <summary>
        /// ホバー用の Markdown。1 行の要約だけにする(VS のホバーは Markdown の表を描けず、大きくなる)。
        /// 表と図は、VS 拡張のホバー(CBufferQuickInfo)とツール ウィンドウが出す。
        /// </summary>
        public static string HoverMarkdown(LBlock b, string highlight)
        {
            var sb = new StringBuilder();
            sb.Append("**").Append(Title(b)).Append("** — ").Append(Summary(b));
            if (b.Kind == "struct") sb.Append("\n\n*cbuffer の先頭に置いたときのレイアウト*");
            if (b.Problems.Count > 0) sb.Append("\n\n⚠ ").Append(string.Join(" / ", b.Problems));
            return sb.ToString();
        }

        /// <summary>メンバー 1 つのホバー。</summary>
        public static string MemberMarkdown(LBlock b, LMember m)
        {
            var sb = new StringBuilder();
            sb.Append("```hlsl\n").Append(TypeLabel(m)).Append(" ").Append(m.Name).Append("\n```\n");
            sb.Append("`").Append(Title(b)).Append("` の **オフセット ").Append(m.Offset).Append("**・サイズ ").Append(m.Size).Append(" バイト・レジスタ ").Append(Register(m.Offset));
            if (m.ArrayCount > 0) sb.Append("・要素の間隔 ").Append(m.Stride).Append(" バイト");
            sb.Append("\n\n").Append(Summary(b));
            return sb.ToString();
        }

        // ---- JSON(ビジュアライザー用) ----

        public static JObject ToJson(CBufferLayout.TypeTable table, LayoutOptions opt, LBlock b)
        {
            var members = new JArray();
            foreach (var m in b.Members) members.Add(MemberJson(m));
            var segments = new JArray();
            foreach (var s in CBufferLayout.Segments(b))
                segments.Add(new JObject { ["path"] = s.Path, ["type"] = s.Type, ["offset"] = s.Offset, ["size"] = s.Size, ["group"] = s.Group });

            var o = new JObject
            {
                ["kind"] = b.Kind,
                ["name"] = b.Name,
                ["title"] = Title(b),
                ["file"] = b.File,
                ["line"] = b.Line,
                ["size"] = b.Size,
                ["paddedSize"] = b.PaddedSize,
                ["wasted"] = CBufferLayout.WastedBytes(b),
                ["incomplete"] = b.Incomplete,
                ["problems"] = new JArray(b.Problems),
                ["members"] = members,
                ["segments"] = segments,
                ["cpp"] = CppStruct(b),
            };
            var r = CBufferLayout.SuggestReorder(table, opt, b);
            if (r != null)
            {
                var order = new JArray();
                foreach (var m in r.Order) order.Add(m.Name);
                o["reorder"] = new JObject { ["order"] = order, ["size"] = r.Size, ["saved"] = r.Saved, ["hlsl"] = ReorderedHlsl(b, r) };
            }
            return o;
        }

        private static JObject MemberJson(LMember m)
        {
            var o = new JObject
            {
                ["name"] = m.Name,
                ["type"] = TypeLabel(m),
                ["offset"] = m.Offset,
                ["size"] = m.Size,
                ["register"] = Register(m.Offset),
                ["file"] = m.File,
                ["line"] = m.Line,
                ["stride"] = m.Stride,
            };
            if (m.Fields.Count > 0)
            {
                var f = new JArray();
                foreach (var x in m.Fields) f.Add(MemberJson(x));
                o["fields"] = f;
            }
            return o;
        }

        public static string ReorderedHlsl(LBlock b, CBufferLayout.Reorder r)
        {
            var sb = new StringBuilder();
            string head = b.Kind == "cbuffer" || b.Kind == "tbuffer" ? b.Kind + " " + b.Name : "struct " + (b.Kind == "ConstantBuffer" ? b.TypeName : b.Name);
            sb.Append(head).Append("\n{\n");
            foreach (var m in r.Order) sb.Append("    ").Append(m.Decl).Append("\n");
            sb.Append("};\n");
            return sb.ToString();
        }

        // ---- C++ の struct ----

        private static string CppScalar(LMember m)
        {
            switch (m.Scalar)
            {
                case 'f': return m.ElemSize == 8 ? "double" : m.ElemSize == 2 ? "uint16_t /*half*/" : "float";
                case 'i': return m.ElemSize == 8 ? "int64_t" : m.ElemSize == 2 ? "int16_t" : "int32_t";
                case 'u': return m.ElemSize == 8 ? "uint64_t" : m.ElemSize == 2 ? "uint16_t" : "uint32_t";
                default: return "uint32_t /*bool*/";
            }
        }

        /// <summary>HLSL と同じ配置になる C++ の struct。隙間は _pad で明示して、static_assert で確かめる。</summary>
        public static string CppStruct(LBlock b)
        {
            string typeName = b.Kind == "ConstantBuffer" ? b.TypeName : b.Name;
            var body = new StringBuilder();
            var asserts = new StringBuilder();
            int cursor = 0, padIndex = 0;
            var names = new HashSet<string>();

            Action<int> padTo = target =>
            {
                int gap = target - cursor;
                if (gap <= 0) return;
                if (gap % 4 == 0) body.Append("    uint32_t _pad").Append(padIndex++).Append("[").Append(gap / 4).Append("];  // 隙間 ").Append(gap).Append(" バイト\n");
                else body.Append("    uint8_t _pad").Append(padIndex++).Append("[").Append(gap).Append("];  // 隙間 ").Append(gap).Append(" バイト\n");
                cursor = target;
            };

            Action<string, string, int> field = null;
            Action<LMember, string> emit = null;
            field = (decl, name, offset) =>
            {
                padTo(offset);
                body.Append("    ").Append(decl).Append(";  // ").Append(offset).Append("\n");
                asserts.Append("static_assert(offsetof(").Append(typeName).Append(", ").Append(name).Append(") == ").Append(offset).Append(");\n");
            };
            emit = (m, name) =>
            {
                int count = m.ArrayCount > 0 ? m.ArrayCount : 1;
                // 16 バイトちょうどの要素の配列は、そのまま配列にする
                if (m.ArrayCount > 16 && !m.IsStruct && m.Stride == 16 && m.Size - (m.ArrayCount - 1) * 16 == 16 && !m.IsMatrix)
                {
                    string t4 = m.Scalar == 'f' && m.ElemSize == 4 ? "DirectX::XMFLOAT4" : "uint32_t";
                    field(t4 + " " + name + "[" + m.ArrayCount + (t4 == "uint32_t" ? " * 4" : "") + "]", name, m.Offset);
                    cursor = m.Offset + m.Size;
                    return;
                }
                for (int i = 0; i < count; i++)
                {
                    string n = m.ArrayCount > 0 ? name + "_" + i : name;
                    int off = m.Offset + i * m.Stride;
                    if (m.IsStruct)
                    {
                        foreach (var f in m.Fields)
                        {
                            var shifted = f.ShallowCopy();
                            ShiftTree(shifted, i * m.Stride);
                            emit(shifted, n + "_" + f.Name);
                        }
                        continue;
                    }
                    if (m.IsMatrix)
                    {
                        if (m.Rows == 4 && m.Cols == 4 && m.ElemSize == 4 && m.Scalar == 'f')
                            field("DirectX::XMFLOAT4X4 " + n, n, off);
                        else
                        {
                            int words = (MatrixBytes(m) + 3) / 4;
                            field(CppScalar(m).Replace("uint16_t /*half*/", "float") + " " + n + "[" + words + "]", n, off);
                        }
                        cursor = off + MatrixBytes(m);
                        continue;
                    }
                    if (m.Comps == 1) field(CppScalar(m) + " " + n, n, off);
                    else if (m.Scalar == 'f' && m.ElemSize == 4) field("DirectX::XMFLOAT" + m.Comps + " " + n, n, off);
                    else if (m.Scalar == 'i' && m.ElemSize == 4) field("DirectX::XMINT" + m.Comps + " " + n, n, off);
                    else if (m.Scalar == 'u' && m.ElemSize == 4) field("DirectX::XMUINT" + m.Comps + " " + n, n, off);
                    else field(CppScalar(m) + " " + n + "[" + m.Comps + "]", n, off);
                    cursor = off + m.Comps * m.ElemSize;
                }
            };

            // packoffset で順番が入れ替わっているときは、オフセットの順に並べる(C++ の struct は、後ろへ戻れない)
            foreach (var m in b.Members.OrderBy(x => x.Offset)) emit(m, m.Name);
            padTo(b.PaddedSize);

            var sb = new StringBuilder();
            sb.Append("// HLSL: ").Append(Title(b)).Append("(").Append(b.Size).Append(" バイト。バッファは 16 の倍数の ").Append(b.PaddedSize).Append(" バイト)\n");
            sb.Append("// 行列は HLSL の既定(列優先)なので、CPU 側で転置して書き込む\n");
            sb.Append("struct ").Append(typeName).Append(" {\n").Append(body).Append("};\n");
            sb.Append("static_assert(sizeof(").Append(typeName).Append(") == ").Append(b.PaddedSize).Append(");\n");
            sb.Append(asserts);
            return sb.ToString();
        }

        private static int MatrixBytes(LMember m)
        {
            int vecs = m.RowMajor ? m.Rows : m.Cols;
            int len = m.RowMajor ? m.Cols : m.Rows;
            int me = Math.Max(4, m.ElemSize);
            int stride = (len * me + 15) / 16 * 16;
            return (vecs - 1) * stride + len * me;
        }

        private static void ShiftTree(LMember m, int by)
        {
            m.Offset += by;
            var copy = new List<LMember>();
            foreach (var f in m.Fields)
            {
                var c = f.ShallowCopy();
                ShiftTree(c, by);
                copy.Add(c);
            }
            m.Fields = copy;
        }
    }
}
