using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// ファイルの #include の並びを読んで、新しい 1 行を足す場所と文字を決める。VS に依存しない。
    /// 並べ方は、すでにある #include に合わせる(空行でグループが分かれていれば、グループごと。分かれていなければ、1 つの塊として並べ替えずに差し込む)。
    /// グループの順は Google style: 自分のヘッダー、C のヘッダー、C++ の標準ヘッダー、その他の &lt;&gt;、プロジェクトの "" 。
    /// </summary>
    internal static class IncludeEditor
    {
        public sealed class Edit
        {
            public int Position;
            public string Text;
        }

        private sealed class Inc
        {
            public int Start, End;        // 行の頭と、次の行の頭
            public bool Angle;
            public string Path;
            public int Group;
            public string Key;
        }

        private static readonly Regex Directive = new Regex(@"^[ \t]*#[ \t]*(\w+)([^\r\n]*)", RegexOptions.Multiline | RegexOptions.Compiled);
        private static readonly Regex IncArg = new Regex(@"^\s*([<""])([^>""\r\n]+)[>""]", RegexOptions.Compiled);

        private static readonly HashSet<string> CHeaders = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "assert.h", "ctype.h", "errno.h", "float.h", "limits.h", "locale.h", "math.h", "setjmp.h", "signal.h",
            "stdarg.h", "stddef.h", "stdint.h", "stdio.h", "stdlib.h", "string.h", "time.h", "wchar.h", "wctype.h",
        };

        private static int Group(bool angle, string path)
        {
            if (!angle) return 4;
            if (path.IndexOf('/') < 0 && path.IndexOf('.') < 0) return 2;
            if (path.IndexOf('/') < 0 && CHeaders.Contains(path)) return 1;
            return 3;
        }

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

        /// <summary>同じ名前のヘッダーがすでに #include されているか(フォルダーの書き方と &lt;&gt; / "" の違いは見ない)。</summary>
        public static bool Has(string text, string path)
        {
            string file = FileName(path);
            foreach (Match d in Directive.Matches(text))
            {
                if (d.Groups[1].Value != "include") continue;
                var a = IncArg.Match(d.Groups[2].Value);
                if (a.Success && string.Equals(FileName(a.Groups[2].Value), file, StringComparison.OrdinalIgnoreCase)) return true;
            }
            return false;
        }

        /// <summary>
        /// token(「&lt;vector&gt;」「"core/scene.h"」)の #include を足す編集。すでにあれば null。
        /// ownStem は、cpp のファイル名(拡張子なし)。同じ名前のヘッダーを先頭のグループにする。ヘッダーのときは null。
        /// </summary>
        public static Edit Plan(string text, string token, string ownStem, string eol)
        {
            bool angle = token[0] == '<';
            string path = token.Substring(1, token.Length - 2);
            if (Has(text, path)) return null;

            string line = "#include " + token;
            bool own = !angle && ownStem != null && string.Equals(Stem(path), ownStem, StringComparison.OrdinalIgnoreCase);
            int g = own ? 0 : Group(angle, path);
            string key = path.ToLowerInvariant();
            bool endsWithNewline = text.Length == 0 || text[text.Length - 1] == '\n';

            List<Inc> list = Collect(text, ownStem);
            if (list.Count == 0) return PlanFirst(text, line, eol, endsWithNewline);

            bool grouped = false;
            for (int i = 0; i + 1 < list.Count; i++)
                if (list[i + 1].Start > list[i].End) { grouped = true; break; }
            // 自分のヘッダーだけがある状態で、別の種類を足すときは、空行で分ける
            if (!grouped && g != 0 && list.All(x => x.Group == 0)) grouped = true;

            if (!grouped)
            {
                Inc before = list.FirstOrDefault(x => x.Group > g || (x.Group == g && string.CompareOrdinal(x.Key, key) > 0));
                if (before != null) return new Edit { Position = before.Start, Text = line + eol };
                return After(list[list.Count - 1], text, line, eol, endsWithNewline);
            }

            var same = list.Where(x => x.Group == g).ToList();
            if (same.Count > 0)
            {
                Inc before = same.FirstOrDefault(x => string.CompareOrdinal(x.Key, key) > 0);
                if (before != null) return new Edit { Position = before.Start, Text = line + eol };
                return After(same[same.Count - 1], text, line, eol, endsWithNewline);
            }

            Inc lower = list.LastOrDefault(x => x.Group < g);
            if (lower == null) return new Edit { Position = list[0].Start, Text = line + eol + eol };

            // 下のグループの末尾のあとに、空行をはさんで新しいグループを作る
            int pos = lower.End;
            string t = eol + line + eol;
            if (pos >= text.Length) { if (!endsWithNewline) t = eol + t; }
            else if (!NextIsBlank(text, pos)) t += eol;
            return new Edit { Position = pos, Text = t };
        }

        private static Edit After(Inc last, string text, string line, string eol, bool endsWithNewline)
        {
            if (last.End >= text.Length && !endsWithNewline) return new Edit { Position = text.Length, Text = eol + line };
            return new Edit { Position = last.End, Text = line + eol };
        }

        private static bool NextIsBlank(string text, int pos)
        {
            int e = text.IndexOf('\n', pos);
            string next = e < 0 ? text.Substring(pos) : text.Substring(pos, e - pos);
            return next.Trim().Length == 0;
        }

        /// <summary>#include がまだ 1 つもないファイルで、入れる場所(#pragma once / インクルードガード / 先頭のコメントのあと)。</summary>
        private static Edit PlanFirst(string text, string line, string eol, bool endsWithNewline)
        {
            int at = 0;
            int pos = 0;
            bool inBlockComment = false;
            string pendingGuard = null;
            while (pos < text.Length)
            {
                int e = text.IndexOf('\n', pos);
                int next = e < 0 ? text.Length : e + 1;
                string t = text.Substring(pos, next - pos).Trim();
                if (inBlockComment) { if (t.Contains("*/")) { inBlockComment = false; at = next; } }
                else if (t.Length == 0) { }
                else if (t.StartsWith("//")) at = next;
                else if (t.StartsWith("/*")) { if (t.Contains("*/")) at = next; else inBlockComment = true; }
                else if (Regex.IsMatch(t, @"^#\s*pragma\s+once\b")) at = next;
                else if (pendingGuard == null && Regex.IsMatch(t, @"^#\s*ifndef\s+\w+")) pendingGuard = Regex.Match(t, @"^#\s*ifndef\s+(\w+)").Groups[1].Value;
                else if (pendingGuard != null && Regex.IsMatch(t, @"^#\s*define\s+" + Regex.Escape(pendingGuard) + @"\b")) { at = next; pendingGuard = null; }
                else break;
                pos = next;
            }

            bool prevNonBlank = at > 0;   // at は、読み終えた行(空でない)の直後
            bool restNonBlank = at < text.Length && text.Substring(at).Trim().Length > 0 && !NextIsBlank(text, at);
            string r = (at > 0 && !endsWithNewline && at >= text.Length ? eol : "") + (prevNonBlank ? eol : "") + line + eol + (restNonBlank ? eol : "");
            return new Edit { Position = at, Text = r };
        }

        /// <summary>
        /// ファイルの先頭にある #include を集める。コードが始まったあとのものと、#if の中のもの(インクルードガードは除く)は数えない。
        /// </summary>
        private static List<Inc> Collect(string text, string ownStem)
        {
            string masked = CppText.Mask(text);
            int codeStart = text.Length;
            for (int i = 0; i < masked.Length; i++)
                if (!char.IsWhiteSpace(masked[i])) { codeStart = i; break; }

            var list = new List<Inc>();
            int depth = 0, baseDepth = 0;
            string first = null;
            string guard = null;
            foreach (Match d in Directive.Matches(text))
            {
                string kind = d.Groups[1].Value;
                if (first == null)
                {
                    first = kind;
                    if (kind == "ifndef") { guard = d.Groups[2].Value.Trim(); }
                }
                else if (guard != null && kind == "define" && baseDepth == 0 && depth == 1 && d.Groups[2].Value.Trim().StartsWith(guard))
                {
                    baseDepth = 1;
                }
                if (kind == "if" || kind == "ifdef" || kind == "ifndef") depth++;
                else if (kind == "endif") depth--;
                else if (kind == "include" && depth == baseDepth && d.Index < codeStart)
                {
                    var a = IncArg.Match(d.Groups[2].Value);
                    if (!a.Success) continue;
                    int nl = text.IndexOf('\n', d.Index + d.Length);
                    bool angle = a.Groups[1].Value == "<";
                    string path = a.Groups[2].Value;
                    bool own = !angle && ownStem != null && string.Equals(Stem(path), ownStem, StringComparison.OrdinalIgnoreCase);
                    list.Add(new Inc
                    {
                        Start = d.Index,
                        End = nl < 0 ? text.Length : nl + 1,
                        Angle = angle,
                        Path = path,
                        Group = own ? 0 : Group(angle, path),
                        Key = path.ToLowerInvariant(),
                    });
                }
            }
            return list;
        }
    }
}
