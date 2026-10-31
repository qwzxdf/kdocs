using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using EnvDTE;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Operations;
using Microsoft.VisualStudio.Text.Tagging;

namespace KCppAssist
{
    /// <summary>#include を足す仕事のうち、Alt+F と入力中の自動挿入で共通の部分(ヘッダーの決定、編集の適用、エラーの波線の確認)。</summary>
    internal static class IncludeService
    {
        public const string EditTag = "K-CppAssist.Include";

        public static readonly TypeIndex Index = new TypeIndex();

        public sealed class Resolution
        {
            /// <summary>決まったヘッダー(「&lt;vector&gt;」「"core/scene.h"」)。複数あって決まらないときは null。</summary>
            public string Token;
            /// <summary>表(標準・Windows・DirectX)か、索引(ソリューションのヘッダー)か。</summary>
            public string Source;
            /// <summary>Token が null のときの候補(token → ヘッダーのフルパス)。</summary>
            public Dictionary<string, string> Choices = new Dictionary<string, string>();
            /// <summary>索引から決めたとき、そのヘッダーのフルパス。</summary>
            public string File;
        }

        public const string TableSource = "表";
        public const string IndexSource = "索引";

        internal static OptionsPage Options
        {
            get { return KCppAssistPackage.Instance == null ? null : (OptionsPage)KCppAssistPackage.Instance.GetDialogPage(typeof(OptionsPage)); }
        }

        public static bool IsHeader(string path)
        {
            string ext = path == null ? "" : Path.GetExtension(path).ToLowerInvariant();
            return ext == ".h" || ext == ".hpp" || ext == ".hh" || ext == ".hxx";
        }

        /// <summary>ヘッダーを探す範囲のフォルダー。ソリューションのフォルダーの下のファイルならそこ。そうでなければ、.git のあるフォルダー、なければファイルのフォルダー。</summary>
        public static string RootFor(string path)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                var dte = (DTE)Package.GetGlobalService(typeof(DTE));
                string sln = dte == null ? null : dte.Solution.FullName;
                if (!string.IsNullOrEmpty(sln) && path != null)
                {
                    string d = Path.GetDirectoryName(sln);
                    if (path.StartsWith(d + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) return d;
                }
            }
            catch (Exception) { }
            string dir = path == null ? "" : Path.GetDirectoryName(path);
            for (string p = dir; !string.IsNullOrEmpty(p); p = Path.GetDirectoryName(p))
                if (Directory.Exists(Path.Combine(p, ".git"))) return p;
            return dir;
        }

        public static ISet<string> SkipDirs(OptionsPage opt)
        {
            var set = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { ".git", ".vs", "bin", "obj", "x64", "Debug", "Release", "vcpkg_installed", "packages" };
            foreach (string s in Split(opt == null ? "" : opt.IncludeSkipDirs)) set.Add(s);
            return set;
        }

        private static IEnumerable<string> Split(string csv)
        {
            return (csv ?? "").Split(new[] { ',', ';', ' ' }, StringSplitOptions.RemoveEmptyEntries).Select(s => s.Trim());
        }

        /// <summary>
        /// name(std::vector、ComPtr、render::Camera など)のヘッダーを決める。見つからなければ null。
        /// manual が false(自動)のときは、索引から引く名前から、設定の拒否リストの名前を除く。
        /// </summary>
        public static Resolution Resolve(string name, string curPath, string root, OptionsPage opt, bool manual)
        {
            string std = StdHeaders.Lookup(name);
            if (std != null) return new Resolution { Token = std, Source = TableSource };
            if (name.StartsWith("std::", StringComparison.Ordinal)) return null;

            int k = name.LastIndexOf("::", StringComparison.Ordinal);
            string last = k < 0 ? name : name.Substring(k + 2);
            if (!manual && Split(opt == null ? "" : opt.IncludeDeny).Contains(last)) return null;

            var files = Index.Lookup(last).Where(f => !string.Equals(f, curPath, StringComparison.OrdinalIgnoreCase)).ToList();
            if (files.Count == 0) return null;

            var r = new Resolution { Source = IndexSource };
            foreach (string f in files) r.Choices[Token(f, curPath, root)] = f;
            if (r.Choices.Count == 1)
            {
                var only = r.Choices.First();
                r.Token = only.Key;
                r.File = only.Value;
                r.Choices.Clear();
            }
            return r;
        }

        /// <summary>
        /// ヘッダーを #include する書き方("core/scene.h")。同じフォルダーかその下なら、そこからの相対。
        /// そうでなければ、2 つのフォルダーの共通の親(ただし root より上にはならない)からの相対。
        /// </summary>
        public static string Token(string header, string curPath, string root)
        {
            string hd = Path.GetDirectoryName(header);
            string cd = curPath == null ? hd : Path.GetDirectoryName(curPath);
            string baseDir = null;
            if (IsUnder(hd, cd)) baseDir = cd;      // 同じフォルダーか、その下
            else
            {
                // プロジェクトが実際に使っている #include の基準(既存の #include から学んだもの)のうち、ヘッダーを含むもの
                foreach (string r in Index.IncludeRoots())
                    if (IsUnder(hd, r)) { baseDir = r; break; }
            }
            if (baseDir != null)
            {
                string rel = header.Substring(baseDir.Length).TrimStart('\\', '/').Replace('\\', '/');
                return "\"" + rel + "\"";
            }
            // 基準が分からないときは、このファイルのフォルダーからの相対(必ず開ける)
            string up = Uri.UnescapeDataString(new Uri(cd.TrimEnd('\\', '/') + "\\").MakeRelativeUri(new Uri(header)).ToString());
            return "\"" + up + "\"";
        }

        private static bool IsUnder(string dir, string parent)
        {
            if (string.IsNullOrEmpty(parent)) return false;
            parent = parent.TrimEnd('\\', '/');
            return string.Equals(dir, parent, StringComparison.OrdinalIgnoreCase)
                || dir.StartsWith(parent + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)
                || dir.StartsWith(parent + "/", StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>足そうとするヘッダーが、いま編集しているヘッダーを #include していれば true(足すと循環する)。</summary>
        public static bool WouldCycle(string headerFile, string curPath)
        {
            if (headerFile == null || curPath == null || !IsHeader(curPath)) return false;
            try { return IncludeEditor.Has(File.ReadAllText(headerFile), Path.GetFileName(curPath)); }
            catch (Exception) { return false; }
        }

        /// <summary>#include の編集を、1 回の Undo にして適用する。</summary>
        public static void Apply(ITextBuffer buffer, int position, string text, ITextUndoHistoryRegistry undo, string description)
        {
            ITextUndoHistory history = null;
            if (undo != null) { try { undo.TryGetHistory(buffer, out history); } catch (Exception) { } }
            using (var tx = history == null ? null : history.CreateTransaction(description))
            {
                var edit = buffer.CreateEdit(EditOptions.None, null, EditTag);
                edit.Insert(position, text);
                edit.Apply();
                if (tx != null) tx.Complete();
            }
        }

        /// <summary>#include を取り消す(足した文字をそのまま消す)。</summary>
        public static void Remove(ITextBuffer buffer, int position, int length, ITextUndoHistoryRegistry undo, string description)
        {
            ITextUndoHistory history = null;
            if (undo != null) { try { undo.TryGetHistory(buffer, out history); } catch (Exception) { } }
            using (var tx = history == null ? null : history.CreateTransaction(description))
            {
                var edit = buffer.CreateEdit(EditOptions.None, null, EditTag);
                edit.Delete(position, length);
                edit.Apply();
                if (tx != null) tx.Complete();
            }
        }

        /// <summary>span に、エラーの波線(IntelliSense の「未定義」など)が重なっているか。</summary>
        public static bool HasError(ITagAggregator<IErrorTag> errors, SnapshotSpan span)
        {
            foreach (var t in errors.GetTags(span))
            {
                string type = t.Tag.ErrorType ?? "";
                if (type.IndexOf("error", StringComparison.OrdinalIgnoreCase) < 0) continue;
                foreach (SnapshotSpan s in t.Span.GetSpans(span.Snapshot))
                    if (s.OverlapsWith(span)) return true;
            }
            return false;
        }

        public static void Status(string message)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            KCppAssistPackage.Log("include: " + message);
            var bar = Package.GetGlobalService(typeof(Microsoft.VisualStudio.Shell.Interop.SVsStatusbar)) as Microsoft.VisualStudio.Shell.Interop.IVsStatusbar;
            if (bar != null) bar.SetText("K-CppAssist: " + message);
        }
    }
}
