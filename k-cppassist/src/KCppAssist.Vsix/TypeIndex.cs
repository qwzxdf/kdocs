using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// ソリューションのヘッダーから、「型の定義」(class / struct / enum / union / using X = / typedef)だけを集めた索引。
    /// 関数・メソッド・変数・クラスの中の入れ子の型は入れない(Instance() のような名前が、ヘッダーに引かれないようにする)。
    /// </summary>
    internal sealed class TypeIndex
    {
        private sealed class Entry { public long Ticks; public string[] Names; public string[] Includes = new string[0]; }

        private static readonly Regex QuotedInclude = new Regex(@"^[ \t]*#[ \t]*include[ \t]*""([^""\r\n]+/[^""\r\n]+)""", RegexOptions.Multiline | RegexOptions.Compiled);
        private static readonly string[] SourceExt = { ".cpp", ".cc", ".cxx", ".c++" };
        private List<string> includeRoots = new List<string>();

        /// <summary>
        /// プロジェクトが実際に使っている「#include のフォルダーの基準」。
        /// 既存の #include "a/b.h" が、どの親フォルダーからなら開けるかを数えて、多い順に並べたもの。
        /// </summary>
        public List<string> IncludeRoots()
        {
            lock (gate) return new List<string>(includeRoots);
        }

        private static List<string> LearnRoots(Dictionary<string, Entry> files)
        {
            var votes = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
            var exists = new Dictionary<string, bool>(StringComparer.OrdinalIgnoreCase);
            foreach (var kv in files)
            {
                string dir = Path.GetDirectoryName(kv.Key);
                foreach (string rel in kv.Value.Includes)
                {
                    string r = rel.Replace('/', Path.DirectorySeparatorChar);
                    if (r.StartsWith("." + Path.DirectorySeparatorChar) || r.StartsWith(".." + Path.DirectorySeparatorChar)) continue;
                    for (string a = Path.GetDirectoryName(dir); !string.IsNullOrEmpty(a); a = Path.GetDirectoryName(a))
                    {
                        string full = Path.Combine(a, r);
                        bool ok;
                        if (!exists.TryGetValue(full, out ok)) exists[full] = ok = File.Exists(full);
                        if (!ok) continue;
                        int n; votes.TryGetValue(a, out n); votes[a] = n + 1;
                        break;
                    }
                }
            }
            return votes.OrderByDescending(v => v.Value).ThenByDescending(v => v.Key.Length).Select(v => v.Key).ToList();
        }

        private readonly Dictionary<string, Entry> files = new Dictionary<string, Entry>(StringComparer.OrdinalIgnoreCase);
        private Dictionary<string, List<string>> byName = new Dictionary<string, List<string>>(StringComparer.Ordinal);
        private readonly object gate = new object();
        private DateTime lastRefresh = DateTime.MinValue;
        private string lastRoot;

        private static readonly string[] HeaderExt = { ".h", ".hpp", ".hh", ".hxx" };

        /// <summary>root の下のヘッダーを読み直す。前回から変わっていないファイルは読まない。force でなければ 15 秒は何もしない。</summary>
        public void Refresh(string root, ISet<string> skipDirs, bool force)
        {
            if (string.IsNullOrEmpty(root) || !Directory.Exists(root)) return;
            lock (gate)
            {
                if (!force && root == lastRoot && (DateTime.UtcNow - lastRefresh).TotalSeconds < 15) return;
                lastRoot = root;
                lastRefresh = DateTime.UtcNow;

                var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                bool changed = false;
                var stack = new Stack<string>();
                stack.Push(root);
                while (stack.Count > 0 && seen.Count < 20000)
                {
                    string dir = stack.Pop();
                    try
                    {
                        foreach (string f in Directory.GetFiles(dir))
                        {
                            string ext = Path.GetExtension(f).ToLowerInvariant();
                            bool header = HeaderExt.Contains(ext);
                            if (!header && !SourceExt.Contains(ext)) continue;
                            seen.Add(f);
                            Entry e;
                            var info = new FileInfo(f);
                            if (files.TryGetValue(f, out e) && e.Ticks == info.LastWriteTimeUtc.Ticks) continue;
                            changed = true;
                            if (info.Length > 2 * 1024 * 1024) { files[f] = new Entry { Ticks = info.LastWriteTimeUtc.Ticks, Names = new string[0] }; continue; }
                            try
                            {
                                string text = File.ReadAllText(f);
                                files[f] = new Entry
                                {
                                    Ticks = info.LastWriteTimeUtc.Ticks,
                                    Names = header ? ParseTypes(text).ToArray() : new string[0],
                                    Includes = QuotedInclude.Matches(text).Cast<Match>().Select(x => x.Groups[1].Value).Distinct().ToArray(),
                                };
                            }
                            catch (Exception) { files[f] = new Entry { Ticks = info.LastWriteTimeUtc.Ticks, Names = new string[0] }; }
                        }
                        foreach (string d in Directory.GetDirectories(dir))
                        {
                            string leaf = Path.GetFileName(d);
                            if (skipDirs.Contains(leaf) || leaf.StartsWith("cmake-build", StringComparison.OrdinalIgnoreCase)) continue;
                            stack.Push(d);
                        }
                    }
                    catch (Exception) { }
                }
                foreach (string gone in files.Keys.Where(k => !seen.Contains(k)).ToList()) { files.Remove(gone); changed = true; }
                if (changed || includeRoots.Count == 0) includeRoots = LearnRoots(files);

                var map = new Dictionary<string, List<string>>(StringComparer.Ordinal);
                foreach (var kv in files)
                    foreach (string name in kv.Value.Names)
                    {
                        List<string> list;
                        if (!map.TryGetValue(name, out list)) map[name] = list = new List<string>();
                        list.Add(kv.Key);
                    }
                byName = map;
            }
        }

        /// <summary>name の型を定義しているヘッダーの一覧(なければ空)。</summary>
        public List<string> Lookup(string name)
        {
            lock (gate)
            {
                List<string> list;
                return byName.TryGetValue(name, out list) ? new List<string>(list) : new List<string>();
            }
        }

        // ---- 解析(VS に依存しない) ----

        private static readonly Regex TypeDef = new Regex(
            @"\b(?:class|struct|union|enum(?:\s+(?:class|struct))?)\s+" +
            @"(?:(?:alignas\s*\([^)]*\)|__declspec\s*\([^)]*\)|\[\[[^\]]*\]\]|[A-Z][A-Z0-9_]*_API|[A-Z][A-Z0-9_]*EXPORT[A-Z0-9_]*)\s+)*" +
            @"([A-Za-z_]\w*)\s*(?:final\s*)?(?::[^;{}]*)?\{",
            RegexOptions.Compiled);
        private static readonly Regex UsingAlias = new Regex(@"\busing\s+([A-Za-z_]\w*)\s*=", RegexOptions.Compiled);
        private static readonly Regex Typedef = new Regex(@"\btypedef\b[^;{}]*?\b([A-Za-z_]\w*)\s*;", RegexOptions.Compiled);
        private static readonly Regex TypedefFn = new Regex(@"\btypedef\b[^;{}]*?\(\s*[\w:]*\*\s*([A-Za-z_]\w*)\s*\)", RegexOptions.Compiled);
        private static readonly Regex NamespaceHead = new Regex(@"(?:\bnamespace\b[^;{}]*|\bextern\s*)$", RegexOptions.Compiled);

        /// <summary>ヘッダーの文字から、名前空間の直下で定義されている型の名前を集める。</summary>
        public static List<string> ParseTypes(string text)
        {
            string m = CppText.Mask(text);
            var hits = new List<KeyValuePair<int, string>>();
            foreach (Match x in TypeDef.Matches(m)) hits.Add(new KeyValuePair<int, string>(x.Index + x.Length - 1, x.Groups[1].Value));
            foreach (Match x in UsingAlias.Matches(m)) hits.Add(new KeyValuePair<int, string>(x.Index, x.Groups[1].Value));
            foreach (Match x in Typedef.Matches(m)) hits.Add(new KeyValuePair<int, string>(x.Index, x.Groups[1].Value));
            foreach (Match x in TypedefFn.Matches(m)) hits.Add(new KeyValuePair<int, string>(x.Index, x.Groups[1].Value));
            hits.Sort((a, b) => a.Key.CompareTo(b.Key));

            var names = new List<string>();
            var stack = new Stack<bool>();   // 波括弧ごとに「名前空間か」
            int other = 0;                   // 名前空間でない波括弧(クラスや関数)の深さ
            int h = 0;
            for (int i = 0; i < m.Length; i++)
            {
                while (h < hits.Count && hits[h].Key == i)
                {
                    if (other == 0 && !names.Contains(hits[h].Value)) names.Add(hits[h].Value);
                    h++;
                }
                char c = m[i];
                if (c == '{')
                {
                    int from = Math.Max(0, i - 300);
                    int sep = m.LastIndexOfAny(new[] { ';', '{', '}' }, i - 1 < 0 ? 0 : i - 1, i - from);
                    string head = m.Substring(sep < from ? from : sep + 1, i - (sep < from ? from : sep + 1));
                    bool ns = NamespaceHead.IsMatch(head);
                    stack.Push(ns);
                    if (!ns) other++;
                }
                else if (c == '}' && stack.Count > 0)
                {
                    if (!stack.Pop()) other--;
                }
            }
            return names;
        }
    }
}
