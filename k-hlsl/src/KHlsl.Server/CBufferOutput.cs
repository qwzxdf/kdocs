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
            sb.Append("`").Append(TypeLabel(m)).Append(" ").Append(m.Name).Append("`\n\n");
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
            };
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
    }
}
