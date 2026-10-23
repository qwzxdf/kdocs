using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace KHlsl.Server
{
    /// <summary>定数バッファのレイアウト(ホバー・CodeLens・ビジュアライザー用のリクエスト)。</summary>
    internal sealed partial class Server
    {
        private sealed class LayoutSet
        {
            public CBufferLayout.TypeTable Table;
            public LayoutOptions Opt;
            public List<LBlock> Blocks;      // cbuffer と ConstantBuffer<T>
            public string Path;
        }

        private string _layoutKey;
        private DateTime _layoutAt;
        private LayoutSet _layoutCache;

        /// <summary>このファイルと、#include したファイルのソースを集める(本文は、開いているものを優先)。</summary>
        private List<CBufferLayout.Source> GatherSources(string uri, string text, Config cfg)
        {
            string path = PathOf(uri);
            var result = new List<CBufferLayout.Source>();
            var visited = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { path };
            var open = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            lock (_docs) foreach (var kv in _docs) open[PathOf(kv.Key)] = kv.Value;
            var own = CBufferLayout.MakeSource(path, text);
            // 先に include を読む(定義の順に並ぶように、include 先を先に入れる)
            var order = new List<CBufferLayout.Source>();
            Action<CBufferLayout.Source, int> visit = null;
            visit = (src, depth) =>
            {
                if (depth < 8)
                    foreach (Match m in Regex.Matches(src.Masked, @"^[ \t]*#[ \t]*include[ \t]*[""<](?<f>[^"">\r\n]+)["">]", RegexOptions.Multiline))
                    {
                        string resolved = ResolveInclude(m.Groups["f"].Value, src.Path, cfg);
                        if (resolved == null || !visited.Add(resolved)) continue;
                        string t;
                        if (!open.TryGetValue(resolved, out t))
                        {
                            try { t = File.ReadAllText(resolved); } catch (Exception) { continue; }
                        }
                        visit(CBufferLayout.MakeSource(resolved, t), depth + 1);
                    }
                order.Add(src);
            };
            visit(own, 0);
            return order;
        }

        private static LayoutOptions OptionsFor(Config cfg, string text)
        {
            var args = new List<string>(cfg.args);
            args.AddRange(Dxc.MagicArgs(text));
            var opt = new LayoutOptions
            {
                Enable16Bit = cfg.enable16bit || args.Contains("-enable-16bit-types"),
                RowMajorDefault = args.Contains("-Zpr")
            };
            Match last = null;
            foreach (Match m in Regex.Matches(text, @"#\s*pragma\s+pack_matrix\s*\(\s*(row_major|column_major)\s*\)")) last = m;
            if (last != null) opt.RowMajorDefault = last.Groups[1].Value == "row_major";
            return opt;
        }

        private LayoutSet LayoutsFor(string uri, string text)
        {
            string path = PathOf(uri);
            string key = uri + "|" + text.Length + "|" + text.GetHashCode();
            lock (_docs)
            {
                if (_layoutCache != null && _layoutKey == key && (DateTime.UtcNow - _layoutAt).TotalSeconds < 3) return _layoutCache;
            }
            var cfg = Config.For(path);
            var sources = GatherSources(uri, text, cfg);
            var table = CBufferLayout.Collect(sources);
            var opt = OptionsFor(cfg, text);
            var set = new LayoutSet { Table = table, Opt = opt, Blocks = CBufferLayout.LayoutAll(table, opt, false), Path = path };
            lock (_docs)
            {
                _layoutCache = set;
                _layoutKey = key;
                _layoutAt = DateTime.UtcNow;
            }
            return set;
        }

        private static bool SamePathText(string a, string b)
        {
            try { return string.Equals(Path.GetFullPath(a), Path.GetFullPath(b), StringComparison.OrdinalIgnoreCase); }
            catch (Exception) { return false; }
        }

        /// <summary>カーソル位置の単語が、cbuffer・ConstantBuffer 変数・struct・そのメンバーなら、レイアウトの説明を返す。</summary>
        private string LayoutHover(Ctx c, string word)
        {
            if (word == null || word.Contains("::")) return null;
            // 軽い下調べ: 本文に cbuffer / ConstantBuffer / struct / tbuffer がなければ、何もしない
            if (!Regex.IsMatch(c.Masked, @"\b(cbuffer|tbuffer|ConstantBuffer|struct|class)\b")) return null;
            var set = LayoutsFor(c.Uri, c.Text);

            // メンバーの宣言行にカーソルがある
            foreach (var b in AllBlocks(set))
                foreach (var m in b.Members)
                    if (m.Name == word && m.Line == c.Line && SamePathText(m.File, set.Path))
                        return CBufferOutput.MemberMarkdown(b, m);

            var blk = set.Blocks.FirstOrDefault(b => b.Name == word);
            if (blk != null) return CBufferOutput.HoverMarkdown(blk, null);

            // ConstantBuffer<T> の T、または struct の名前
            var sb = CBufferLayout.LayoutStruct(set.Table, set.Opt, word);
            if (sb != null && sb.Members.Count > 0) return CBufferOutput.HoverMarkdown(sb, null);
            return null;
        }

        private static IEnumerable<LBlock> AllBlocks(LayoutSet set)
        {
            foreach (var b in set.Blocks) yield return b;
            foreach (var s in set.Table.Structs.Values)
            {
                var b = CBufferLayout.LayoutStruct(set.Table, set.Opt, s.Name);
                if (b != null) yield return b;
            }
        }

        // ---- CodeLens ----
        private JToken CodeLens(JToken p)
        {
            string uri = (string)p["textDocument"]["uri"];
            string text = TextOf(uri);
            var result = new JArray();
            if (!Regex.IsMatch(Analyzer.Mask(text), @"\b(cbuffer|tbuffer|ConstantBuffer)\b")) return result;
            var set = LayoutsFor(uri, text);
            foreach (var b in set.Blocks)
            {
                if (!SamePathText(b.File, set.Path)) continue;
                int wasted = CBufferLayout.WastedBytes(b);
                string title = b.Size + " バイト(" + b.PaddedSize / 16 + " レジスタ)・隙間 " + wasted + " バイト";
                var r = CBufferLayout.SuggestReorder(set.Table, set.Opt, b);
                if (r != null) title += "・並べ替えで " + r.Saved + " バイト減らせる";
                result.Add(new JObject
                {
                    ["range"] = Range(b.Line, 0, b.Line, 0),
                    ["command"] = new JObject
                    {
                        ["title"] = title,
                        ["command"] = "khlsl.showCBuffer",
                        ["arguments"] = new JArray(b.Name)
                    }
                });
            }
            return result;
        }

        // ---- ビジュアライザー用のリクエスト ----
        private JToken CBuffersRequest(JToken p)
        {
            string uri = (string)p["uri"];
            bool includeStructs = p["includeStructs"] != null && (bool)p["includeStructs"];
            string text = TextOf(uri);
            var set = LayoutsFor(uri, text);
            var blocks = new JArray();
            foreach (var b in set.Blocks) blocks.Add(CBufferOutput.ToJson(set.Table, set.Opt, b));
            if (includeStructs)
                foreach (var s in set.Table.Structs.Values.OrderBy(x => x.Src.Path).ThenBy(x => x.Line))
                {
                    var b = CBufferLayout.LayoutStruct(set.Table, set.Opt, s.Name);
                    if (b != null && b.Members.Count > 0) blocks.Add(CBufferOutput.ToJson(set.Table, set.Opt, b));
                }
            return new JObject { ["uri"] = uri, ["blocks"] = blocks };
        }
    }
}
