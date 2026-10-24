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

        // ---- C++ の構造体との比較 ----

        /// <summary>C++ ファイルと、#include "..." したファイルのソース(同じフォルダーと、親フォルダー 3 つまでを探す)。</summary>
        private List<CBufferLayout.Source> GatherCppSources(string path, string text)
        {
            var visited = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { path };
            var order = new List<CBufferLayout.Source>();
            Action<CBufferLayout.Source, int> visit = null;
            visit = (src, depth) =>
            {
                if (depth < 5)
                    foreach (Match m in Regex.Matches(src.Masked, @"^[ 	]*#[ 	]*include[ 	]*""(?<f>[^""
]+)""", RegexOptions.Multiline))
                    {
                        string resolved = null;
                        string dir = Path.GetDirectoryName(src.Path);
                        for (int up = 0; up < 4 && dir != null && resolved == null; up++, dir = Path.GetDirectoryName(dir))
                        {
                            try
                            {
                                string cand = Path.GetFullPath(Path.Combine(dir, m.Groups["f"].Value));
                                if (File.Exists(cand)) resolved = cand;
                            }
                            catch (Exception) { }
                        }
                        if (resolved == null || !visited.Add(resolved)) continue;
                        string t;
                        try { t = File.ReadAllText(resolved); } catch (Exception) { continue; }
                        visit(CBufferLayout.MakeSource(resolved, t), depth + 1);
                    }
                order.Add(src);
            };
            visit(CBufferLayout.MakeSource(path, text), 0);
            return order;
        }

        /// <summary>C++ のカーソル位置の語が、計算できる struct の名前か(ホバーに、比べるリンクを出すかどうか)。</summary>
        private JToken CppStructProbe(JToken p)
        {
            string path = (string)p["cppPath"];
            string text = (string)p["cppText"] ?? SafeRead(path);
            string word = (string)p["word"];
            int line = p["line"] == null ? -1 : (int)p["line"];
            var table = CppLayout.Collect(GatherCppSources(path, text));
            string name = CppLayout.Has(table, word) ? word : null;
            if (name == null && line >= 0) name = CppLayout.StructAt(table, path, line);
            if (name == null) return new JObject { ["found"] = false };
            var cs = CppLayout.Layout(table, name);
            if (cs == null || cs.Incomplete) return new JObject { ["found"] = false };
            return new JObject { ["found"] = true, ["name"] = name, ["size"] = cs.Size };
        }

        private static string SafeRead(string path)
        {
            try { return File.ReadAllText(path); } catch (Exception) { return ""; }
        }

        private JToken CppCompareRequest(JToken p)
        {
            string path = (string)p["cppPath"];
            string text = (string)p["cppText"] ?? SafeRead(path);
            string name = (string)p["cppStruct"];
            int line = p["line"] == null ? -1 : (int)p["line"];
            var table = CppLayout.Collect(GatherCppSources(path, text));
            if (name == null && line >= 0) name = CppLayout.StructAt(table, path, line);
            if (name == null) return new JObject { ["error"] = "C++ の構造体が見つかりません" };
            var cs = CppLayout.Layout(table, name);
            if (cs == null) return new JObject { ["error"] = "C++ の構造体 '" + name + "' の定義が見つかりません" };
            if (cs.Incomplete) return new JObject { ["error"] = "C++ の構造体 '" + name + "' を計算できません: " + string.Join(" / ", cs.Problems) };

            // 比べる相手の HLSL: 指定された物。なければ、開いている HLSL のうち、名前が合う物
            string uri = (string)p["hlslUri"];
            string wanted = (string)p["hlslBlock"];
            var uris = new List<string>();
            lock (_docs) uris.AddRange(_docs.Keys);
            if (uri != null) { uris.Remove(uri); uris.Insert(0, uri); }
            if (uris.Count == 0) return new JObject { ["error"] = "HLSL のファイルが開かれていません。比べる cbuffer のあるファイルを、K-HLSL で開いてください", ["cpp"] = CppCompare.CppBlockJson(cs) };

            LayoutSet chosenSet = null;
            LBlock chosen = null;
            var candidates = new JArray();
            string norm = CppCompare.Normalize(name);
            foreach (string u in uris)
            {
                var set = LayoutsFor(u, TextOf(u));
                var all = new List<LBlock>(set.Blocks);
                foreach (var s in set.Table.Structs.Values)
                {
                    var sb = CBufferLayout.LayoutStruct(set.Table, set.Opt, s.Name);
                    if (sb != null && sb.Members.Count > 0) all.Add(sb);
                }
                foreach (var b in all)
                    if (u == uris[0]) candidates.Add(new JObject { ["name"] = b.Name, ["title"] = CBufferOutput.Title(b) });
                LBlock hit = null;
                if (wanted != null) hit = all.FirstOrDefault(b => b.Name == wanted);
                if (hit == null && wanted == null) hit = all.FirstOrDefault(b => b.Kind != "struct" && CppCompare.Normalize(b.Name) == norm)
                    ?? all.FirstOrDefault(b => CppCompare.Normalize(b.Name) == norm);
                if (hit != null && chosen == null) { chosen = hit; chosenSet = set; }
                if (chosen != null && u == uris[0]) break;
            }
            if (chosen == null)
            {
                // 名前が合う物がないときは、最初の HLSL ファイルの先頭の cbuffer
                var set0 = LayoutsFor(uris[0], TextOf(uris[0]));
                chosen = set0.Blocks.FirstOrDefault();
                chosenSet = set0;
                if (chosen == null) return new JObject { ["error"] = "HLSL のファイルに、cbuffer が見つかりません", ["cpp"] = CppCompare.CppBlockJson(cs), ["candidates"] = candidates };
            }
            var rows = CppCompare.Compare(cs.Members.Select(CppCompare.FromCpp).ToList(), chosen.Members.Select(CppCompare.FromHlsl).ToList());
            var result = CppCompare.ToJson(cs, chosen, rows);
            result["hlsl"] = CBufferOutput.ToJson(chosenSet.Table, chosenSet.Opt, chosen);
            result["candidates"] = candidates;
            result["cppStruct"] = name;
            result["cppFile"] = cs.File;
            return result;
        }
    }
}
