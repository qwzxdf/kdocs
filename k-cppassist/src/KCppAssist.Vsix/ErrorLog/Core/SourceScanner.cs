using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text.RegularExpressions;
using System.Threading;

namespace KCppAssist.ErrorLog
{
    public sealed class SrcHit
    {
        public string File = "";
        public int Line;
        public string Text = "";
    }

    /// <summary>
    /// 未解決の関数・変数の「定義らしい行」を、ソリューションのソースから探す。
    /// 見つかれば「定義はあるのに、リンクされていない」、見つからなければ「定義を書いていない」と分かる。
    /// 文字列の検索による推測なので、見つからなくても、ソリューションの外のソースにあるかもしれない。
    /// </summary>
    public static class SourceScanner
    {
        private static readonly HashSet<string> SkipDirs = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            ".git", ".vs", "vcpkg_installed", "packages", "node_modules", "obj", "ipch", "x64", "x86", "Win32",
            "Debug", "Release", "bin", "out", "build", ".svn"
        };

        private static readonly HashSet<string> Extensions = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            ".cpp", ".cc", ".cxx", ".c", ".h", ".hpp", ".hh", ".hxx", ".inl", ".ixx", ".cppm", ".ipp", ".tpp"
        };

        private sealed class Target
        {
            public string Token;
            public bool IsVariable;
            /// <summary>コンストラクター・デストラクターは、戻り値の型がないので、名前の前が空でもよい。</summary>
            public bool AllowEmptyPrefix;
            public List<UnresolvedSym> Syms = new List<UnresolvedSym>();
        }

        private static readonly Regex TemplateTail = new Regex(@"<.*$", RegexOptions.Compiled | RegexOptions.Singleline);

        public static int FilesScanned;

        public static void Scan(List<UnresolvedSym> syms, string root, CancellationToken ct, int maxMilliseconds)
        {
            FilesScanned = 0;
            if (string.IsNullOrEmpty(root) || !Directory.Exists(root)) return;

            var targets = new Dictionary<string, Target>(StringComparer.Ordinal);
            foreach (UnresolvedSym s in syms)
            {
                if (s.Win32Lib != null || s.Info == null) continue;
                string token = TokenFor(s.Info);
                if (token == null) continue;
                bool isVar = !s.Info.IsFunction;
                Target t;
                if (!targets.TryGetValue(token, out t)) targets[token] = t = new Target
                {
                    Token = token,
                    IsVariable = isVar,
                    AllowEmptyPrefix = s.Info.Kind == SymKind.Ctor || s.Info.Kind == SymKind.Dtor
                };
                t.Syms.Add(s);
            }
            if (targets.Count == 0) return;

            var list = new List<Target>(targets.Values);
            var sw = Stopwatch.StartNew();
            foreach (string file in EnumerateSources(root, ct))
            {
                if (ct.IsCancellationRequested || sw.ElapsedMilliseconds > maxMilliseconds) break;
                try
                {
                    var fi = new FileInfo(file);
                    if (fi.Length > 2 * 1024 * 1024) continue;
                    FilesScanned++;
                    int lineNo = 0;
                    foreach (string line in File.ReadLines(file))
                    {
                        lineNo++;
                        if (line.Length < 4 || line.Length > 400) continue;
                        foreach (Target t in list)
                        {
                            int idx = line.IndexOf(t.Token, StringComparison.Ordinal);
                            if (idx < 0) continue;
                            if (!LooksLikeDefinition(line, idx, t)) continue;
                            foreach (UnresolvedSym s in t.Syms)
                            {
                                if (s.Defs == null) s.Defs = new List<SrcHit>();
                                if (s.Defs.Count < 3)
                                    s.Defs.Add(new SrcHit { File = file, Line = lineNo, Text = line.Trim() });
                            }
                        }
                    }
                }
                catch (Exception) { /* 読めないファイルは飛ばす */ }
            }
        }

        /// <summary>探す文字列。メンバーなら「Class::Name」、それ以外なら関数名。探しようがなければ null。</summary>
        private static string TokenFor(SymInfo info)
        {
            if (info.Kind == SymKind.Lambda || info.Kind == SymKind.Special || info.Kind == SymKind.VTable || info.Kind == SymKind.CSymbol && info.Name.Length < 4)
                return null;
            string name = TemplateTail.Replace(info.Name, "");
            if (name.Length == 0 || name.StartsWith("`", StringComparison.Ordinal)) return null;
            if (name.StartsWith("operator", StringComparison.Ordinal)) return null;

            if (info.IsMember && info.Class.Length > 0)
            {
                string cls = TemplateTail.Replace(info.Class, "");
                return cls + "::" + name;
            }
            return name;
        }

        private static bool LooksLikeDefinition(string line, int idx, Target t)
        {
            string trimmed = line.TrimStart();
            if (trimmed.StartsWith("//", StringComparison.Ordinal) || trimmed.StartsWith("*", StringComparison.Ordinal)
                || trimmed.StartsWith("#", StringComparison.Ordinal) || trimmed.StartsWith("/*", StringComparison.Ordinal))
                return false;

            // トークンの直前・直後が、別の識別子の一部でないこと
            if (idx > 0 && IsIdent(line[idx - 1]) ) return false;
            int end = idx + t.Token.Length;
            if (t.IsVariable)
            {
                if (end < line.Length && IsIdent(line[end])) return false;
                if (end < line.Length && line[end] == '(') return false;
            }
            else
            {
                int k = end;
                while (k < line.Length && line[k] == ' ') k++;
                if (k >= line.Length || line[k] != '(') return false;
            }

            string prefix = line.Substring(0, idx);
            // 呼び出し・代入・return・メンバー アクセスは、定義ではない
            if (prefix.IndexOf('=') >= 0 || prefix.IndexOf('(') >= 0 || prefix.IndexOf('.') >= 0 || prefix.IndexOf("->", StringComparison.Ordinal) >= 0
                || prefix.IndexOf("return", StringComparison.Ordinal) >= 0 || prefix.IndexOf("new ", StringComparison.Ordinal) >= 0
                || prefix.IndexOf("co_", StringComparison.Ordinal) >= 0 || prefix.IndexOf(',') >= 0
                || prefix.IndexOf("<<", StringComparison.Ordinal) >= 0 || prefix.IndexOf(">>", StringComparison.Ordinal) >= 0)
                return false;

            // 定義には、型(戻り値の型)が前に付く。使うだけの `Foo::count++;` や `Foo::Create(` は、前が空
            string before = prefix.TrimEnd();
            if (before.Length == 0)
            {
                if (!t.AllowEmptyPrefix) return false;
            }
            else
            {
                char last = before[before.Length - 1];
                if (!(IsIdent(last) || last == '*' || last == '&' || last == '>')) return false;
            }

            if (t.IsVariable)
            {
                // 定義は「= 初期値」「{初期値}」「[要素数]」「;」のどれかで続く。`++` や `+=` で続くのは使うだけ
                string after = line.Substring(end).TrimStart();
                if (!(after.StartsWith("=", StringComparison.Ordinal) && !after.StartsWith("==", StringComparison.Ordinal)
                      || after.StartsWith("{", StringComparison.Ordinal) || after.StartsWith("[", StringComparison.Ordinal)
                      || after.StartsWith(";", StringComparison.Ordinal)))
                    return false;
            }
            else
            {
                string tail = trimmed.TrimEnd();
                // 「foo();」のような、呼び出しか宣言の 1 行は除く(定義は、本体の「{」や引数の続きで終わる)
                if (tail.EndsWith(";", StringComparison.Ordinal)) return false;
            }
            return true;
        }

        private static bool IsIdent(char c) { return char.IsLetterOrDigit(c) || c == '_'; }

        private static IEnumerable<string> EnumerateSources(string root, CancellationToken ct)
        {
            var stack = new Stack<string>();
            stack.Push(root);
            int n = 0;
            while (stack.Count > 0 && !ct.IsCancellationRequested)
            {
                string dir = stack.Pop();
                string[] files = null;
                try { files = Directory.GetFiles(dir); } catch (Exception) { }
                if (files != null)
                    foreach (string f in files)
                    {
                        if (!Extensions.Contains(Path.GetExtension(f))) continue;
                        if (++n > 6000) yield break;
                        yield return f;
                    }
                string[] subs = null;
                try { subs = Directory.GetDirectories(dir); } catch (Exception) { }
                if (subs == null) continue;
                foreach (string sub in subs)
                {
                    if (SkipDirs.Contains(Path.GetFileName(sub))) continue;
                    stack.Push(sub);
                }
            }
        }
    }
}
