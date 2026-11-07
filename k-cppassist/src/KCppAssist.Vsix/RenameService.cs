using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using EnvDTE;
using Microsoft.VisualStudio;
using Microsoft.VisualStudio.Editor;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Operations;

namespace KCppAssist
{
    /// <summary>
    /// ヘッダーか cpp の名前を変えたとき、相手のファイルの名前、ソリューション中の #include、CMake の書き方を、新しい名前にそろえる。
    /// エディターで開いているファイルは、エディターの文字を書き換える(Undo できる。保存はしない)。開いていないファイルは、文字コードを保って直接書く。
    /// </summary>
    internal static class RenameService
    {
        public const string EditTag = "K-CppAssist.Rename";

        /// <summary>自分で名前を変えている間は、名前変更の監視を止める(相手の名前変更で、また動かないように)。</summary>
        public static volatile bool Busy;

        internal static OptionsPage Options { get { return IncludeService.Options; } }

        /// <summary>
        /// first(すでに名前が変わった 1 つ目)に続けて、相手の名前、#include、ビルド ファイルを直す。結果を 1 行の文にして返す。
        /// UI スレッドから呼ぶ。
        /// </summary>
        public static async Task<string> FollowAsync(KCppAssistPackage pkg, RenameSync.Move first, IVsEditorAdaptersFactoryService adapters, ITextUndoHistoryRegistry undo)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
            var opt = Options;
            RenameHub.Remember(first);
            var moves = new List<RenameSync.Move> { first };
            var notes = new List<string>();

            // 1. 相手のファイル(Foo.h → Foo.cpp)
            if (opt.RenamePair)
            {
                var pair = RenameSync.PairOf(first.Old, first.New, File.Exists);
                if (pair != null)
                {
                    RenameHub.Remember(pair);
                    string err = RenameFile(pair.Old, pair.New);
                    if (err == null) { moves.Add(pair); notes.Add("相手 " + Path.GetFileName(pair.Old) + " → " + Path.GetFileName(pair.New)); }
                    else notes.Add("相手 " + Path.GetFileName(pair.Old) + " は、名前を変えられませんでした (" + err + ")");
                }
            }

            // 2. #include と CMake
            string root = IncludeService.RootFor(first.New);
            var skip = IncludeService.SkipDirs(opt);
            await Task.Run(() => IncludeService.Index.Refresh(root, skip, false));
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
            var roots = IncludeService.Index.IncludeRoots();

            var openPaths = OpenDocumentPaths();
            bool buildFiles = opt.RenameBuildFiles;
            bool includes = opt.RenameUpdateIncludes;
            var counts = await Task.Run(() => RewriteDiskFiles(root, skip, moves, roots, openPaths, includes, buildFiles));
            int sites = counts.IncludeSites, files = counts.IncludeFiles, build = counts.BuildSites;

            // 開いているファイルは、エディターの文字を書き換える
            foreach (string path in openPaths)
            {
                if (!((includes && RenameSync.IsCode(path)) || (buildFiles && RenameSync.IsBuildFile(path)))) continue;
                ITextBuffer buf = SyncService.OpenBuffer(path, adapters);
                if (buf == null) continue;
                string text = buf.CurrentSnapshot.GetText();
                var edits = RenameSync.IsBuildFile(path)
                    ? RenameSync.RewriteBuildFile(text, Path.GetDirectoryName(path), moves)
                    : RenameSync.RewriteIncludes(text, Path.GetDirectoryName(path), moves, roots, File.Exists);
                if (edits.Count == 0) continue;
                ApplyToBuffer(buf, edits, undo);
                if (RenameSync.IsBuildFile(path)) build += edits.Count; else { sites += edits.Count; files++; }
                KCppAssistPackage.Log("rename: edited open document " + path + " (" + edits.Count + ")");
            }

            string head = Path.GetFileName(first.Old) + " → " + Path.GetFileName(first.New);
            var parts = new List<string>(notes);
            if (sites > 0) parts.Add("#include " + sites + " か所 (" + files + " ファイル)");
            if (build > 0) parts.Add("CMake " + build + " か所 (保存したあと、CMake を再構成してください)");
            if (parts.Count == 0) parts.Add("ほかに直す所はありませんでした");
            string msg = head + ": " + string.Join("、", parts);
            if (openPaths.Count > 0 && (sites > 0 || build > 0)) msg += "。開いているファイルは、保存していません";
            return msg;
        }

        private sealed class Counts { public int IncludeSites, IncludeFiles, BuildSites; }

        /// <summary>エディターで開いていないファイルを、直接書き換える(別のスレッドで呼ぶ)。</summary>
        private static Counts RewriteDiskFiles(string root, ISet<string> skip, List<RenameSync.Move> moves, List<string> roots, HashSet<string> open, bool includes, bool buildFiles)
        {
            var c = new Counts();
            if (string.IsNullOrEmpty(root) || !Directory.Exists(root)) return c;
            var stack = new Stack<string>();
            stack.Push(root);
            int seen = 0;
            while (stack.Count > 0 && seen < 30000)
            {
                string dir = stack.Pop();
                try
                {
                    foreach (string f in Directory.GetFiles(dir))
                    {
                        bool code = includes && RenameSync.IsCode(f);
                        bool build = buildFiles && RenameSync.IsBuildFile(f);
                        if (!code && !build) continue;
                        seen++;
                        if (open.Contains(f)) continue;
                        if (new FileInfo(f).Length > 4 * 1024 * 1024) continue;
                        Encoding enc;
                        string text;
                        try { text = RenameSync.ReadKeepingEncoding(f, out enc); } catch (Exception) { continue; }
                        var edits = build
                            ? RenameSync.RewriteBuildFile(text, dir, moves)
                            : RenameSync.RewriteIncludes(text, dir, moves, roots, File.Exists);
                        if (edits.Count == 0) continue;
                        try { RenameSync.WriteKeepingEncoding(f, RenameSync.Apply(text, edits), enc); }
                        catch (Exception ex) { KCppAssistPackage.Log("rename: write failed " + f + ": " + ex.Message); continue; }
                        if (build) c.BuildSites += edits.Count; else { c.IncludeSites += edits.Count; c.IncludeFiles++; }
                        KCppAssistPackage.Log("rename: edited " + f + " (" + edits.Count + ")");
                    }
                    foreach (string d in Directory.GetDirectories(dir))
                    {
                        string leaf = Path.GetFileName(d);
                        if (!skip.Contains(leaf) && !leaf.StartsWith("cmake-build", StringComparison.OrdinalIgnoreCase)) stack.Push(d);
                    }
                }
                catch (Exception) { }
            }
            return c;
        }

        private static HashSet<string> OpenDocumentPaths()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var set = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            try
            {
                var dte = (DTE)Package.GetGlobalService(typeof(DTE));
                foreach (Document d in dte.Documents)
                {
                    try { if (!string.IsNullOrEmpty(d.FullName)) set.Add(d.FullName); } catch (Exception) { }
                }
            }
            catch (Exception ex) { KCppAssistPackage.Log("rename: list documents failed: " + ex.Message); }
            return set;
        }

        private static void ApplyToBuffer(ITextBuffer buffer, List<RenameSync.TextEdit> edits, ITextUndoHistoryRegistry undo)
        {
            ITextUndoHistory history = null;
            if (undo != null) { try { undo.TryGetHistory(buffer, out history); } catch (Exception) { } }
            using (var tx = history == null ? null : history.CreateTransaction("K-CppAssist: ファイル名の変更を反映"))
            {
                var edit = buffer.CreateEdit(EditOptions.None, null, EditTag);
                foreach (var e in edits.OrderBy(x => x.Start))
                    edit.Replace(e.Start, e.Length, e.Text);
                edit.Apply();
                if (tx != null) tx.Complete();
            }
        }

        /// <summary>ファイルの名前を変える。プロジェクトに入っていれば、プロジェクトごと(Solution Explorer の名前変更と同じ)。成功なら null、失敗なら理由。</summary>
        public static string RenameFile(string oldPath, string newPath)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            bool was = Busy;
            Busy = true;
            try
            {
                if (File.Exists(newPath)) return "同じ名前のファイルがあります";
                try
                {
                    var dte = (DTE)Package.GetGlobalService(typeof(DTE));
                    ProjectItem item = dte.Solution.FindProjectItem(oldPath);
                    if (item != null)
                    {
                        item.Name = Path.GetFileName(newPath);
                        if (File.Exists(newPath)) return null;
                    }
                }
                catch (Exception ex) { KCppAssistPackage.Log("rename: project item rename failed: " + ex.Message); }
                if (!File.Exists(oldPath)) return File.Exists(newPath) ? null : "元のファイルがありません";
                File.Move(oldPath, newPath);
                return null;
            }
            catch (Exception ex) { return ex.Message; }
            finally { Busy = was; }
        }
    }

    /// <summary>Solution Explorer での名前変更を見て、相手・#include・CMake を直す。</summary>
    internal sealed class RenameWatcher : IVsTrackProjectDocumentsEvents2
    {
        private readonly KCppAssistPackage package;

        public RenameWatcher(KCppAssistPackage package) { this.package = package; }

        public int OnAfterRenameFiles(int cProjects, int cFiles, IVsProject[] rgpProjects, int[] rgFirstIndices, string[] rgszMkOldNames, string[] rgszMkNewNames, VSRENAMEFILEFLAGS[] rgFlags)
        {
            try
            {
                if (RenameService.Busy || rgszMkOldNames == null || rgszMkNewNames == null) return VSConstants.S_OK;
                var opt = RenameService.Options;
                if (opt == null || opt.RenameMode != RenameMode.Auto) return VSConstants.S_OK;
                for (int i = 0; i < Math.Min(cFiles, rgszMkOldNames.Length); i++)
                {
                    string oldName = rgszMkOldNames[i], newName = rgszMkNewNames[i];
                    if (string.IsNullOrEmpty(oldName) || string.IsNullOrEmpty(newName)) continue;
                    if (!(RenameSync.IsHeader(oldName) || RenameSync.IsSource(oldName))) continue;
                    var move = new RenameSync.Move { Old = oldName, New = newName };
                    if (RenameHub.Accept(move)) package.OnFileRenamed(move, false);
                }
            }
            catch (Exception ex) { KCppAssistPackage.Log("rename watcher failed: " + ex.Message); }
            return VSConstants.S_OK;
        }

        // 以下は、使わない通知
        public int OnQueryAddFiles(IVsProject pProject, int cFiles, string[] rgpszMkDocuments, VSQUERYADDFILEFLAGS[] rgFlags, VSQUERYADDFILERESULTS[] pSummaryResult, VSQUERYADDFILERESULTS[] rgResults) { return VSConstants.S_OK; }
        public int OnAfterAddFilesEx(int cProjects, int cFiles, IVsProject[] rgpProjects, int[] rgFirstIndices, string[] rgpszMkDocuments, VSADDFILEFLAGS[] rgFlags) { return VSConstants.S_OK; }
        public int OnAfterAddDirectoriesEx(int cProjects, int cDirectories, IVsProject[] rgpProjects, int[] rgFirstIndices, string[] rgpszMkDocuments, VSADDDIRECTORYFLAGS[] rgFlags) { return VSConstants.S_OK; }
        public int OnAfterRemoveFiles(int cProjects, int cFiles, IVsProject[] rgpProjects, int[] rgFirstIndices, string[] rgpszMkDocuments, VSREMOVEFILEFLAGS[] rgFlags) { return VSConstants.S_OK; }
        public int OnAfterRemoveDirectories(int cProjects, int cDirectories, IVsProject[] rgpProjects, int[] rgFirstIndices, string[] rgpszMkDocuments, VSREMOVEDIRECTORYFLAGS[] rgFlags) { return VSConstants.S_OK; }
        public int OnQueryRenameFiles(IVsProject pProject, int cFiles, string[] rgszMkOldNames, string[] rgszMkNewNames, VSQUERYRENAMEFILEFLAGS[] rgFlags, VSQUERYRENAMEFILERESULTS[] pSummaryResult, VSQUERYRENAMEFILERESULTS[] rgResults) { return VSConstants.S_OK; }
        public int OnQueryRenameDirectories(IVsProject pProject, int cDirs, string[] rgszMkOldNames, string[] rgszMkNewNames, VSQUERYRENAMEDIRECTORYFLAGS[] rgFlags, VSQUERYRENAMEDIRECTORYRESULTS[] pSummaryResult, VSQUERYRENAMEDIRECTORYRESULTS[] rgResults) { return VSConstants.S_OK; }
        public int OnAfterRenameDirectories(int cProjects, int cDirs, IVsProject[] rgpProjects, int[] rgFirstIndices, string[] rgszMkOldNames, string[] rgszMkNewNames, VSRENAMEDIRECTORYFLAGS[] rgFlags) { return VSConstants.S_OK; }
        public int OnQueryAddDirectories(IVsProject pProject, int cDirectories, string[] rgpszMkDocuments, VSQUERYADDDIRECTORYFLAGS[] rgFlags, VSQUERYADDDIRECTORYRESULTS[] pSummaryResult, VSQUERYADDDIRECTORYRESULTS[] rgResults) { return VSConstants.S_OK; }
        public int OnQueryRemoveFiles(IVsProject pProject, int cFiles, string[] rgpszMkDocuments, VSQUERYREMOVEFILEFLAGS[] rgFlags, VSQUERYREMOVEFILERESULTS[] pSummaryResult, VSQUERYREMOVEFILERESULTS[] rgResults) { return VSConstants.S_OK; }
        public int OnQueryRemoveDirectories(IVsProject pProject, int cDirectories, string[] rgpszMkDocuments, VSQUERYREMOVEDIRECTORYFLAGS[] rgFlags, VSQUERYREMOVEDIRECTORYRESULTS[] pSummaryResult, VSQUERYREMOVEDIRECTORYRESULTS[] rgResults) { return VSConstants.S_OK; }
        public int OnAfterSccStatusChanged(int cProjects, int cFiles, IVsProject[] rgpProjects, int[] rgFirstIndices, string[] rgpszMkDocuments, uint[] rgdwSccStatus) { return VSConstants.S_OK; }
    }

    /// <summary>
    /// ファイル名の変更を、見つけて 1 か所に集める。Solution Explorer の通知と、フォルダーの監視(フォルダー ビュー、エクスプローラー、別のツール)の
    /// 両方から来るので、同じ変更の二重処理と、git のブランチ切り替えのような一括の変更を、ここで除く。
    /// </summary>
    internal static class RenameHub
    {
        private static readonly object Gate = new object();
        private static readonly Dictionary<string, FileSystemWatcher> Watchers = new Dictionary<string, FileSystemWatcher>(StringComparer.OrdinalIgnoreCase);
        private static readonly Dictionary<string, DateTime> Seen = new Dictionary<string, DateTime>(StringComparer.OrdinalIgnoreCase);
        private static readonly List<DateTime> Burst = new List<DateTime>();
        private static DateTime bulkUntil = DateTime.MinValue;
        private static volatile string[] skipSegments = new string[0];
        public static volatile int BulkLimit = 4;

        private static string Key(RenameSync.Move m) { return (m.Old + "|" + m.New).ToLowerInvariant(); }

        /// <summary>自分で名前を変えたものを覚える。そのあとに来る、同じ変更の通知を無視するため。</summary>
        public static void Remember(RenameSync.Move m)
        {
            lock (Gate) Seen[Key(m)] = DateTime.UtcNow;
        }

        /// <summary>
        /// 名前の変更の通知を受ける。二重の通知と、一括の変更なら false(処理しない)。
        /// 別のスレッドからも呼ばれる。
        /// </summary>
        public static bool Accept(RenameSync.Move m)
        {
            DateTime now = DateTime.UtcNow;
            lock (Gate)
            {
                foreach (string k in Seen.Where(kv => (now - kv.Value).TotalSeconds > 30).Select(kv => kv.Key).ToList()) Seen.Remove(k);
                string key = Key(m);
                if (Seen.ContainsKey(key)) return false;
                Seen[key] = now;

                Burst.RemoveAll(t => (now - t).TotalSeconds > 3);
                Burst.Add(now);
                if (Burst.Count > BulkLimit) bulkUntil = now.AddSeconds(10);
                if (now < bulkUntil)
                {
                    KCppAssistPackage.Log("rename: ignored (bulk operation) " + m.Old + " -> " + m.New);
                    return false;
                }
                return true;
            }
        }

        public static bool IsBulk { get { lock (Gate) return DateTime.UtcNow < bulkUntil; } }

        /// <summary>path のあるフォルダー(ソリューションか、.git のあるフォルダー)を、監視する。UI スレッドから呼ぶ。</summary>
        public static void Ensure(string path)
        {
            if (string.IsNullOrEmpty(path)) return;
            ThreadHelper.ThrowIfNotOnUIThread();
            EnsureDir(IncludeService.RootFor(path));
        }

        public static void EnsureDir(string root)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var opt = RenameService.Options;
            if (opt == null || opt.RenameMode != RenameMode.Auto || !opt.RenameWatchFiles) return;
            BulkLimit = Math.Max(1, opt.RenameBulkLimit);
            skipSegments = IncludeService.SkipDirs(opt).ToArray();
            if (string.IsNullOrEmpty(root) || !Directory.Exists(root)) return;
            lock (Gate)
            {
                if (Watchers.Count >= 4) return;
                foreach (string k in Watchers.Keys)
                    if (string.Equals(root, k, StringComparison.OrdinalIgnoreCase) || root.StartsWith(k.TrimEnd('\\') + "\\", StringComparison.OrdinalIgnoreCase)) return;
                try
                {
                    var w = new FileSystemWatcher(root) { IncludeSubdirectories = true, NotifyFilter = NotifyFilters.FileName, InternalBufferSize = 64 * 1024 };
                    w.Renamed += OnRenamed;
                    w.EnableRaisingEvents = true;
                    Watchers[root] = w;
                    KCppAssistPackage.Log("rename: watching " + root);
                }
                catch (Exception ex) { KCppAssistPackage.Log("rename: watch failed " + root + ": " + ex.Message); }
            }
        }

        private static void OnRenamed(object sender, RenamedEventArgs e)
        {
            try
            {
                // ヘッダーや cpp どうしの名前変更だけ。保存の一時ファイル(.tmp → .cpp)などは、見ない
                if (!(RenameSync.IsHeader(e.OldFullPath) || RenameSync.IsSource(e.OldFullPath))) return;
                if (!(RenameSync.IsHeader(e.FullPath) || RenameSync.IsSource(e.FullPath))) return;
                var skip = skipSegments;
                string[] parts = e.FullPath.Split('\\');
                foreach (string p in parts) if (skip.Contains(p, StringComparer.OrdinalIgnoreCase)) return;

                var move = new RenameSync.Move { Old = e.OldFullPath, New = e.FullPath };
                if (!Accept(move)) return;
                var pkg = KCppAssistPackage.Instance;
                if (pkg != null) pkg.OnFileRenamed(move, true);
            }
            catch (Exception ex) { KCppAssistPackage.Log("rename: watcher event failed: " + ex.Message); }
        }
    }
}
