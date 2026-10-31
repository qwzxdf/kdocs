using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using EnvDTE;
using Microsoft.VisualStudio;
using Microsoft.VisualStudio.Editor;
using Microsoft.VisualStudio.Language.Intellisense.AsyncCompletion;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Text.Operations;
using Microsoft.VisualStudio.TextManager.Interop;

namespace KCppAssist
{
    /// <summary>ヘッダーの宣言と cpp の定義で、引数を合わせる仕事のうち、Alt+G と自動で共通の部分(相手のファイル探し、編集の適用)。</summary>
    internal static class SyncService
    {
        public const string EditTag = "K-CppAssist.Sync";

        private static readonly string[] SourceExt = { ".cpp", ".cc", ".cxx", ".c++" };
        private static readonly string[] HeaderExt = { ".h", ".hpp", ".hh", ".hxx" };

        public sealed class Target
        {
            public string File;
            public string Text;
            public FunctionScan.Sig Sig;
            public ITextBuffer Buffer;      // エディターで開いているとき。閉じていれば null
            public string Inner { get { return Sig.Inner(Text); } }
        }

        internal static OptionsPage Options { get { return IncludeService.Options; } }

        /// <summary>wantDefinition が true なら cpp(か、同じヘッダー)の定義、false ならヘッダーの宣言になりそうなファイルの一覧。ファイルの中身は読まない。</summary>
        public static List<string> Candidates(string path, string cls, string root, bool wantDefinition, OptionsPage opt)
        {
            var files = new List<string>();
            string dir = Path.GetDirectoryName(path);
            string stem = Path.GetFileNameWithoutExtension(path);
            if (wantDefinition)
            {
                if (IncludeService.IsHeader(path)) files.Add(path);
                var same = SourceExt.Select(e => Path.Combine(dir, stem + e)).Where(File.Exists).ToList();
                files.AddRange(same);
                if (same.Count == 0 && cls != null) files.AddRange(FindSources(root, cls, IncludeService.SkipDirs(opt)));
            }
            else
            {
                if (IncludeService.IsHeader(path)) files.Add(path);
                files.AddRange(HeaderExt.Select(e => Path.Combine(dir, stem + e)).Where(File.Exists));
                if (cls != null) files.AddRange(IncludeService.Index.Lookup(cls));
            }
            return files.Distinct(StringComparer.OrdinalIgnoreCase).ToList();
        }

        /// <summary>root の下の cpp から、「cls::」を含むものを探す(最大 5000 ファイルまで読む)。</summary>
        private static List<string> FindSources(string root, string cls, ISet<string> skip)
        {
            var found = new List<string>();
            if (string.IsNullOrEmpty(root) || !Directory.Exists(root)) return found;
            var re = new Regex(@"\b" + Regex.Escape(cls) + @"\s*::");
            var stack = new Stack<string>();
            stack.Push(root);
            int read = 0;
            while (stack.Count > 0 && read < 5000)
            {
                string dir = stack.Pop();
                try
                {
                    foreach (string f in Directory.GetFiles(dir))
                    {
                        if (!SourceExt.Contains(Path.GetExtension(f).ToLowerInvariant())) continue;
                        read++;
                        try { if (re.IsMatch(File.ReadAllText(f))) found.Add(f); } catch (Exception) { }
                    }
                    foreach (string d in Directory.GetDirectories(dir))
                    {
                        string leaf = Path.GetFileName(d);
                        if (!skip.Contains(leaf) && !leaf.StartsWith("cmake-build", StringComparison.OrdinalIgnoreCase)) stack.Push(d);
                    }
                }
                catch (Exception) { }
            }
            return found;
        }

        public static bool IsCounterpart(FunctionScan.Sig s, bool wantDefinition, string cls, string name)
        {
            if (s.Name != name || s.Class != cls) return false;
            if (wantDefinition) return s.HasBody && !s.InClass;
            return !s.HasBody && (cls == null ? !s.InClass : s.InClass);
        }

        /// <summary>files の中から、名前とクラスが合う宣言(か定義)を集める。開いているファイルは、エディターの文字を読む。</summary>
        public static List<Target> FindTargets(IEnumerable<string> files, bool wantDefinition, string cls, string name, IVsEditorAdaptersFactoryService adapters)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var list = new List<Target>();
            foreach (string f in files)
            {
                ITextBuffer buf = OpenBuffer(f, adapters);
                string text;
                try { text = buf != null ? buf.CurrentSnapshot.GetText() : File.ReadAllText(f); }
                catch (Exception) { continue; }
                foreach (var s in FunctionScan.Scan(text))
                    if (IsCounterpart(s, wantDefinition, cls, name))
                        list.Add(new Target { File = f, Text = text, Sig = s, Buffer = buf });
            }
            return list;
        }

        /// <summary>エディターで開いているファイルの文字列バッファー。開いていなければ null。</summary>
        public static ITextBuffer OpenBuffer(string path, IVsEditorAdaptersFactoryService adapters)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                IVsUIHierarchy hier; uint id; IVsWindowFrame frame;
                if (!VsShellUtilities.IsDocumentOpen(ServiceProvider.GlobalProvider, path, Guid.Empty, out hier, out id, out frame) || frame == null) return null;
                IVsTextView tv = VsShellUtilities.GetTextView(frame);
                IWpfTextView w = tv == null ? null : adapters.GetWpfTextView(tv);
                return w == null ? null : w.TextBuffer;
            }
            catch (Exception) { return null; }
        }

        /// <summary>ファイルを開いて(開いていなければ)、文字列バッファーを返す。</summary>
        public static ITextBuffer OpenForEdit(string path, IVsEditorAdaptersFactoryService adapters)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            ITextBuffer buf = OpenBuffer(path, adapters);
            if (buf != null) return buf;
            IVsUIHierarchy hier; uint id; IVsWindowFrame frame;
            VsShellUtilities.OpenDocument(ServiceProvider.GlobalProvider, path, Guid.Empty, out hier, out id, out frame);
            IVsTextView tv = frame == null ? null : VsShellUtilities.GetTextView(frame);
            IWpfTextView w = tv == null ? null : adapters.GetWpfTextView(tv);
            return w == null ? null : w.TextBuffer;
        }

        /// <summary>括弧の中身を置き換える。1 回の Undo。</summary>
        public static void Replace(ITextBuffer buffer, int start, int length, string text, ITextUndoHistoryRegistry undo, string description)
        {
            ITextUndoHistory history = null;
            if (undo != null) { try { undo.TryGetHistory(buffer, out history); } catch (Exception) { } }
            using (var tx = history == null ? null : history.CreateTransaction(description))
            {
                var edit = buffer.CreateEdit(EditOptions.None, null, EditTag);
                edit.Replace(start, length, text);
                edit.Apply();
                if (tx != null) tx.Complete();
            }
        }

        /// <summary>補完リストが出ている、ビルド中、エディターにフォーカスがない、のどれか。</summary>
        public static bool IsBusy(IWpfTextView view, IAsyncCompletionBroker completion)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            if (!view.HasAggregateFocus) return true;
            try { if (completion.IsCompletionActive(view)) return true; } catch (Exception) { }
            try
            {
                var dte = (DTE)Package.GetGlobalService(typeof(DTE));
                if (dte != null && dte.Solution.SolutionBuild.BuildState == vsBuildState.vsBuildStateInProgress) return true;
            }
            catch (Exception) { }
            return false;
        }

        public static bool SameKeys(List<string> a, List<string> b) { return a != null && b != null && a.SequenceEqual(b); }
    }
}
