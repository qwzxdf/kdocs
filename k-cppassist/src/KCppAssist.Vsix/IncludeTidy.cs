using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// #include の整理(並べ替え・重複の削除)と、使っていない #include の検出。VS に依存しない。
    /// 文字の編集の結果(新しい文字列)だけを返す。ファイルを開く・書くのは呼び出し側。
    /// </summary>
    internal static class IncludeTidy
    {
        public sealed class Item
        {
            public int Start, End;          // 行の頭と、次の行の頭(行末の改行を含む)
            public bool Angle;
            public string Path;             // 「vector」「core/scene.h」
            public string Line;             // 行の文字(改行なし)
            public int Depth;               // #if の入れ子の深さ(0 が外)
            public bool Keep;               // 行に「keep」の注釈がある
            public string Token { get { return (Angle ? "<" : "\"") + Path + (Angle ? ">" : "\""); } }
        }

        private static readonly Regex IncludeLine = new Regex(@"^[ \t]*#[ \t]*include[ \t]*([<""])([^>""\r\n]+)[>""][ \t]*(.*?)[ \t]*$", RegexOptions.Compiled);
        private static readonly Regex CondOpen = new Regex(@"^[ \t]*#[ \t]*if", RegexOptions.Compiled);
        private static readonly Regex CondClose = new Regex(@"^[ \t]*#[ \t]*endif", RegexOptions.Compiled);
        private static readonly Regex Ident = new Regex(@"[A-Za-z_]\w*", RegexOptions.Compiled);

        private static readonly HashSet<string> CHeaders = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "assert.h", "ctype.h", "errno.h", "float.h", "limits.h", "locale.h", "math.h", "setjmp.h", "signal.h",
            "stdarg.h", "stddef.h", "stdint.h", "stdio.h", "stdlib.h", "string.h", "time.h", "wchar.h", "wctype.h",
        };

        private static string FileName(string path)
        {
            int k = path.LastIndexOfAny(new[] { '/', '\\' });
            return k < 0 ? path : path.Substring(k + 1);
        }

        private static string Stem(string path)
        {
            string f = FileName(path);
            int k = f.LastIndexOf('.');
            return k < 0 ? f : f.Substring(0, k);
        }

        /// <summary>並べる順のグループ: 0 自分のヘッダー、1 C の標準、2 C++ の標準、3 そのほかの &lt;&gt;、4 "..."。</summary>
        private static int Group(Item it, string ownStem)
        {
            if (!it.Angle)
            {
                if (ownStem != null && string.Equals(Stem(it.Path), ownStem, StringComparison.OrdinalIgnoreCase)) return 0;
                return 4;
            }
            if (it.Path.IndexOf('/') < 0 && it.Path.IndexOf('.') < 0) return 2;
            if (it.Path.IndexOf('/') < 0 && CHeaders.Contains(it.Path)) return 1;
            return 3;
        }

        /// <summary>#include の行を、#if の深さつきで全部集める。</summary>
        public static List<Item> Parse(string text)
        {
            var list = new List<Item>();
            int depth = 0, pos = 0;
            while (pos < text.Length)
            {
                int nl = text.IndexOf('\n', pos);
                int end = nl < 0 ? text.Length : nl + 1;
                string line = text.Substring(pos, (nl < 0 ? text.Length : nl) - pos).TrimEnd('\r');
                if (CondOpen.IsMatch(line)) depth++;
                else if (CondClose.IsMatch(line)) { if (depth > 0) depth--; }
                else
                {
                    var m = IncludeLine.Match(line);
                    if (m.Success)
                        list.Add(new Item
                        {
                            Start = pos, End = end, Angle = m.Groups[1].Value == "<", Path = m.Groups[2].Value, Line = line, Depth = depth,
                            Keep = Regex.IsMatch(m.Groups[3].Value, @"\bkeep\b", RegexOptions.IgnoreCase),
                        });
                }
                pos = end;
            }
            return list;
        }

        // ---- 整理 ----

        /// <summary>
        /// 続いている #include のまとまり(間に空行とコメントだけがあるもの)ごとに、グループ分け・並べ替え・重複の削除をした文字列を返す。
        /// #if の中の #include と、#include 以外の行をはさむものは、そのまま。変わらなければ null。
        /// ownStem は cpp のファイル名(拡張子なし)。ヘッダーのときは null。
        /// </summary>
        public static string Organize(string text, string ownStem, string eol)
        {
            var lines = SplitLines(text);
            // 行ごとの、#if の深さと、#include かどうか
            int depth = 0;
            var info = new List<Item>(lines.Count);
            for (int i = 0; i < lines.Count; i++)
            {
                string l = lines[i].Text;
                Item it = null;
                if (CondOpen.IsMatch(l)) depth++;
                else if (CondClose.IsMatch(l)) { if (depth > 0) depth--; }
                else
                {
                    var m = IncludeLine.Match(l);
                    if (m.Success) it = new Item { Angle = m.Groups[1].Value == "<", Path = m.Groups[2].Value, Line = l, Depth = depth, Keep = Regex.IsMatch(m.Groups[3].Value, @"\bkeep\b", RegexOptions.IgnoreCase) };
                }
                info.Add(it != null && it.Depth == 0 ? it : null);
                if (it != null && it.Depth != 0) info[info.Count - 1] = null;
            }

            var result = new StringBuilder();
            bool firstCluster = true, changed = false;
            int idx = 0;
            while (idx < lines.Count)
            {
                if (info[idx] == null) { result.Append(lines[idx].Raw); idx++; continue; }

                // idx から始まるまとまり: #include と、空行と、// コメントの行
                int a = idx, b = idx;
                for (int j = idx; j < lines.Count; j++)
                {
                    string t = lines[j].Text.Trim();
                    if (info[j] != null) { b = j; continue; }
                    if (t.Length == 0 || t.StartsWith("//")) continue;
                    break;
                }
                // 末尾の、#include でない行(空行・コメント)は、まとまりに入れない
                var items = new List<KeyValuePair<List<string>, Item>>();   // (直前のコメント行, #include)
                var pending = new List<string>();
                for (int j = a; j <= b; j++)
                {
                    if (info[j] != null) { items.Add(new KeyValuePair<List<string>, Item>(pending, info[j])); pending = new List<string>(); }
                    else if (lines[j].Text.Trim().StartsWith("//")) pending.Add(lines[j].Text);
                    // 空行は捨てる(グループの区切りは作り直す)
                }

                // 重複(同じ文字)を落として、グループ・名前の順に並べる
                var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                var kept = new List<KeyValuePair<List<string>, Item>>();
                foreach (var kv in items)
                    if (seen.Add(kv.Value.Token)) kept.Add(kv);
                var ordered = kept
                    .Select((kv, n) => new { kv, g = Group(kv.Value, firstCluster ? ownStem : null), n })
                    .OrderBy(x => x.g).ThenBy(x => x.kv.Value.Path.ToLowerInvariant(), StringComparer.Ordinal).ThenBy(x => x.n)
                    .ToList();

                var sb = new StringBuilder();
                int prevGroup = -1;
                foreach (var x in ordered)
                {
                    if (prevGroup >= 0 && x.g != prevGroup) sb.Append(eol);
                    foreach (string c in x.kv.Key) sb.Append(c).Append(eol);
                    sb.Append(x.kv.Value.Line).Append(eol);
                    prevGroup = x.g;
                }
                // まとまりの後ろの空行・コメントは、元のまま残す
                string original = string.Concat(lines.Skip(a).Take(b - a + 1).Select(l => l.Raw));
                bool lastHadEol = lines[b].Raw.EndsWith("\n");
                string rebuilt = sb.ToString();
                if (!lastHadEol && rebuilt.EndsWith(eol)) rebuilt = rebuilt.Substring(0, rebuilt.Length - eol.Length);
                if (rebuilt != original) changed = true;
                result.Append(rebuilt);
                idx = b + 1;
                firstCluster = false;
            }
            return changed ? result.ToString() : null;
        }

        private sealed class Line { public string Text, Raw; }

        private static List<Line> SplitLines(string text)
        {
            var list = new List<Line>();
            int pos = 0;
            while (pos < text.Length)
            {
                int nl = text.IndexOf('\n', pos);
                int end = nl < 0 ? text.Length : nl + 1;
                list.Add(new Line { Raw = text.Substring(pos, end - pos), Text = text.Substring(pos, (nl < 0 ? text.Length : nl) - pos).TrimEnd('\r') });
                pos = end;
            }
            return list;
        }

        // ---- 使っていない #include ----

        /// <summary>
        /// ヘッダーが定義している名前(クラス・列挙型とその値・using・typedef・マクロ・関数・定数)の集まり。
        /// 「使っているか」を見るためなので、多めに拾う(拾いすぎは、消さない方に働く)。
        /// </summary>
        public static HashSet<string> Provided(string headerText)
        {
            var set = new HashSet<string>(StringComparer.Ordinal);
            string m = CppText.Mask(headerText);
            foreach (Match x in Regex.Matches(m, @"\b(?:class|struct|union|enum)\s+(?:class\s+|struct\s+)?(?:alignas\s*\([^)]*\)\s*|__declspec\s*\([^)]*\)\s*|\[\[[^\]]*\]\]\s*|[A-Z][A-Z0-9_]*_API\s+|[A-Z][A-Z0-9]*_[A-Z0-9_]+\s+)*([A-Za-z_]\w*)"))
                set.Add(x.Groups[1].Value);
            foreach (Match x in Regex.Matches(m, @"\busing\s+([A-Za-z_]\w*)\s*="))
                set.Add(x.Groups[1].Value);
            foreach (Match x in Regex.Matches(m, @"\btypedef\b[^;{}]*?([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*;"))
                set.Add(x.Groups[1].Value);
            foreach (Match x in Regex.Matches(headerText, @"(?m)^[ \t]*#[ \t]*define[ \t]+([A-Za-z_]\w*)"))
                set.Add(x.Groups[1].Value);
            // 列挙子: enum ... { A, B = 1, C }
            foreach (Match x in Regex.Matches(m, @"\benum\b[^;{}]*\{([^{}]*)\}"))
                foreach (string item in x.Groups[1].Value.Split(','))
                {
                    var id = Ident.Match(item);
                    if (id.Success) set.Add(id.Value);
                }
            // 定数・変数: 名前 = 値; や 名前[...]
            foreach (Match x in Regex.Matches(m, @"\b([A-Za-z_]\w*)\s*(?:=(?!=)|\[)"))
                set.Add(x.Groups[1].Value);
            // 関数(クラスのメンバーでないもの)
            foreach (var s in FunctionScan.Scan(headerText))
                if (s.Class == null) set.Add(s.Name);
            return set;
        }

        /// <summary>text の中で使っている識別子(コメント・文字列は除く)。#include の行は数えない。</summary>
        public static HashSet<string> Used(string text)
        {
            string m = CppText.Mask(text);
            m = Regex.Replace(m, @"(?m)^[ \t]*#[ \t]*include[^\r\n]*", "");
            var set = new HashSet<string>(StringComparer.Ordinal);
            foreach (Match x in Ident.Matches(m)) set.Add(x.Value);
            return set;
        }

        /// <summary>
        /// 使っていない #include を返す。provided(item) は、そのヘッダーが(間接に include するものも含めて)定義している名前。
        /// 読めないヘッダー・名前を 1 つも拾えないヘッダーは、null を返してもらって、残す。
        /// 自分のヘッダー・「keep」の注釈のある行・#if の中の行は、いつも残す。
        /// </summary>
        public static List<Item> Unused(string text, string ownStem, Func<Item, ISet<string>> provided)
        {
            var used = Used(text);
            var list = new List<Item>();
            foreach (var it in Parse(text))
            {
                if (it.Depth != 0 || it.Keep) continue;
                if (!it.Angle && ownStem != null && string.Equals(Stem(it.Path), ownStem, StringComparison.OrdinalIgnoreCase)) continue;
                var names = provided(it);
                if (names == null || names.Count == 0) continue;
                bool any = false;
                foreach (string n in names) if (used.Contains(n)) { any = true; break; }
                if (!any) list.Add(it);
            }
            return list;
        }

        /// <summary>items の行を消した文字列。</summary>
        public static string Remove(string text, IEnumerable<Item> items)
        {
            foreach (var it in items.OrderByDescending(i => i.Start))
                text = text.Substring(0, it.Start) + text.Substring(it.End);
            return text;
        }
    }
}
