using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace KCppAssist
{
    /// <summary>
    /// ヘッダーや cpp のファイル名を変えたとき、相手のファイル・#include・ビルド ファイル(CMake)を、新しい名前にそろえる。
    /// ここは VS に依存しない部分(相手の決め方と、文字の書き換え)。
    /// </summary>
    internal static class RenameSync
    {
        public sealed class Move
        {
            public string Old, New;
        }

        /// <summary>文字列のうち、[Start, Start+Length) を Text に置き換える。</summary>
        public sealed class TextEdit
        {
            public int Start, Length;
            public string Text;
        }

        private static readonly string[] HeaderExt = { ".h", ".hpp", ".hh", ".hxx" };
        private static readonly string[] SourceExt = { ".cpp", ".cc", ".cxx", ".c++" };

        public static bool IsHeader(string path) { return HeaderExt.Contains(Path.GetExtension(path).ToLowerInvariant()); }
        public static bool IsSource(string path) { return SourceExt.Contains(Path.GetExtension(path).ToLowerInvariant()); }
        public static bool IsCode(string path) { return IsHeader(path) || IsSource(path) || Path.GetExtension(path).ToLowerInvariant() == ".c" || Path.GetExtension(path).ToLowerInvariant() == ".inl"; }

        public static bool IsBuildFile(string path)
        {
            string name = Path.GetFileName(path);
            return string.Equals(name, "CMakeLists.txt", StringComparison.OrdinalIgnoreCase)
                || string.Equals(Path.GetExtension(name), ".cmake", StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>
        /// oldPath を newPath に変えたとき、同じフォルダーにある「相手」(Foo.h なら Foo.cpp、Foo.cpp なら Foo.h)の移動を決める。
        /// 名前(拡張子を除く部分)が変わっていないとき、フォルダーが変わったとき、相手がいないとき、新しい名前が使われているときは null。
        /// </summary>
        public static Move PairOf(string oldPath, string newPath, Func<string, bool> exists)
        {
            string dir = Path.GetDirectoryName(oldPath);
            if (!string.Equals(dir, Path.GetDirectoryName(newPath), StringComparison.OrdinalIgnoreCase)) return null;
            string oldStem = Path.GetFileNameWithoutExtension(oldPath);
            string newStem = Path.GetFileNameWithoutExtension(newPath);
            if (string.Equals(oldStem, newStem, StringComparison.Ordinal)) return null;

            string[] candidates = IsHeader(oldPath) ? SourceExt : IsSource(oldPath) ? HeaderExt : null;
            if (candidates == null) return null;
            foreach (string ext in candidates)
            {
                string from = Path.Combine(dir, oldStem + ext);
                string to = Path.Combine(dir, newStem + ext);
                if (exists(from) && !exists(to)) return new Move { Old = from, New = to };
            }
            return null;
        }

        private static string Full(string p)
        {
            try { return Path.GetFullPath(p); } catch (Exception) { return p; }
        }

        private static bool Same(string a, string b)
        {
            return string.Equals(Full(a), Full(b), StringComparison.OrdinalIgnoreCase);
        }

        private static readonly Regex IncludeLine = new Regex(@"^([ \t]*#[ \t]*include[ \t]*)([<""])([^>""\r\n]+)([>""])", RegexOptions.Multiline | RegexOptions.Compiled);

        /// <summary>
        /// text(includerDir にあるファイル)の #include のうち、moves の古いファイルを指しているものを、新しい名前に直す編集を返す。
        /// 指しているかどうかは、そのファイルのフォルダー、または roots(プロジェクトが使う #include の基準)からたどって、同じファイルになるかで決める。
        /// 名前が同じだけの別のファイルには、触れない。
        /// </summary>
        public static List<TextEdit> RewriteIncludes(string text, string includerDir, IList<Move> moves, IList<string> roots, Func<string, bool> exists = null)
        {
            if (exists == null) exists = _ => false;
            var edits = new List<TextEdit>();
            foreach (Match m in IncludeLine.Matches(text))
            {
                string rel = m.Groups[3].Value;
                string file = rel.Substring(rel.LastIndexOfAny(new[] { '/', '\\' }) + 1);
                bool quoted = m.Groups[2].Value == "\"";
                foreach (Move mv in moves)
                {
                    if (!string.Equals(file, Path.GetFileName(mv.Old), StringComparison.OrdinalIgnoreCase)) continue;
                    string relWin = rel.Replace('/', '\\');
                    // コンパイラは、"" の include を、そのファイルのフォルダー、プロジェクトの基準の順に探す。
                    // 先に見つかるファイルが、別の(実在する)ファイルなら、動かしたファイルのことではない
                    bool hit = false, shadowed = false;
                    if (quoted)
                    {
                        string local = Path.Combine(includerDir, relWin);
                        if (Same(local, mv.Old)) hit = true;
                        else if (exists(local)) shadowed = true;
                    }
                    if (!hit && !shadowed && roots != null)
                        foreach (string r in roots)
                        {
                            string cand = Path.Combine(r, relWin);
                            if (Same(cand, mv.Old)) { hit = true; break; }
                            if (exists(cand)) break;
                        }
                    if (!hit) continue;

                    string newRel = rel.Substring(0, rel.Length - file.Length) + Path.GetFileName(mv.New);
                    edits.Add(new TextEdit { Start = m.Groups[3].Index, Length = rel.Length, Text = newRel });
                    break;
                }
            }
            return edits;
        }

        /// <summary>
        /// CMakeLists.txt / .cmake の中で、古いファイルの書き方(buildDir からの相対。/ と \ のどちらでも)を、新しい名前に直す編集を返す。
        /// 名前の一部だけが同じ別のファイル(MyFoo.cpp、Foo.cpp.in など)には、触れない。
        /// </summary>
        public static List<TextEdit> RewriteBuildFile(string text, string buildDir, IList<Move> moves)
        {
            var edits = new List<TextEdit>();
            foreach (Move mv in moves)
            {
                string relOld = Rel(buildDir, mv.Old);
                string relNew = Rel(buildDir, mv.New);
                if (relOld == null || relNew == null) continue;
                foreach (char sep in new[] { '/', '\\' })
                {
                    string o = relOld.Replace('/', sep), n = relNew.Replace('/', sep);
                    var re = new Regex(@"(?<![\w.\-/\\])" + Regex.Escape(o) + @"(?![\w.])", RegexOptions.IgnoreCase);
                    foreach (Match m in re.Matches(text))
                        if (!edits.Any(e => e.Start == m.Index))
                            edits.Add(new TextEdit { Start = m.Index, Length = m.Length, Text = n });
                }
            }
            return edits;
        }

        /// <summary>dir から file への相対パス(/ 区切り)。同じドライブでなければ null。</summary>
        public static string Rel(string dir, string file)
        {
            try
            {
                string d = Full(dir).TrimEnd('\\', '/') + "\\";
                var u = new Uri(d).MakeRelativeUri(new Uri(Full(file)));
                return Uri.UnescapeDataString(u.ToString());
            }
            catch (Exception) { return null; }
        }

        /// <summary>編集を、後ろから順に当てた文字列。重なる編集は、先の 1 つだけを使う。</summary>
        public static string Apply(string text, IList<TextEdit> edits)
        {
            var ordered = edits.OrderBy(e => e.Start).ToList();
            var kept = new List<TextEdit>();
            int end = -1;
            foreach (var e in ordered)
            {
                if (e.Start < end) continue;
                kept.Add(e);
                end = e.Start + e.Length;
            }
            var sb = new StringBuilder(text);
            for (int i = kept.Count - 1; i >= 0; i--)
                sb.Remove(kept[i].Start, kept[i].Length).Insert(kept[i].Start, kept[i].Text);
            return sb.ToString();
        }

        // ---- ディスクのファイル(エディターで開いていないもの)の読み書き ----

        /// <summary>
        /// 文字コードを保ったまま読む。BOM があればそれ、なければ UTF-8 として厳密に読めれば UTF-8(BOM なし)、読めなければシフト JIS(932)。
        /// </summary>
        public static string ReadKeepingEncoding(string path, out Encoding encoding)
        {
            byte[] bytes = File.ReadAllBytes(path);
            if (bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF)
            {
                encoding = new UTF8Encoding(true);
                return encoding.GetString(bytes, 3, bytes.Length - 3);
            }
            if (bytes.Length >= 2 && bytes[0] == 0xFF && bytes[1] == 0xFE) { encoding = new UnicodeEncoding(false, true); return encoding.GetString(bytes, 2, bytes.Length - 2); }
            if (bytes.Length >= 2 && bytes[0] == 0xFE && bytes[1] == 0xFF) { encoding = new UnicodeEncoding(true, true); return encoding.GetString(bytes, 2, bytes.Length - 2); }
            try
            {
                encoding = new UTF8Encoding(false);
                return new UTF8Encoding(false, true).GetString(bytes);
            }
            catch (Exception)
            {
                try { encoding = Encoding.GetEncoding(932); return encoding.GetString(bytes); }
                catch (Exception) { encoding = Encoding.Default; return encoding.GetString(bytes); }
            }
        }

        public static void WriteKeepingEncoding(string path, string text, Encoding encoding)
        {
            byte[] body = encoding.GetBytes(text);
            byte[] preamble = encoding.GetPreamble();
            var all = new byte[preamble.Length + body.Length];
            Buffer.BlockCopy(preamble, 0, all, 0, preamble.Length);
            Buffer.BlockCopy(body, 0, all, preamble.Length, body.Length);
            File.WriteAllBytes(path, all);
        }
    }
}
