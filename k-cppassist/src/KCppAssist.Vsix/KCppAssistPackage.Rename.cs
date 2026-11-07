using System;
using System.ComponentModel.Design;
using System.IO;
using System.Linq;
using EnvDTE;
using Microsoft.VisualStudio.ComponentModelHost;
using Microsoft.VisualStudio.Editor;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Microsoft.VisualStudio.Text.Operations;
using Microsoft.VisualStudio.TextManager.Interop;
using Task = System.Threading.Tasks.Task;

namespace KCppAssist
{
    /// <summary>ヘッダーや cpp の名前を変えたとき、相手・#include・CMake に写す部分。</summary>
    public sealed partial class KCppAssistPackage
    {
        internal const int CmdRename = 0x0108;

        private RenameWatcher _renameWatcher;
        private uint _renameCookie;
        private SolutionEvents _solutionEvents;     // イベントを保つ(参照を持たないと、回収される)

        private async Task InitializeRenameAsync()
        {
            var tracker = await GetServiceAsync(typeof(SVsTrackProjectDocuments)) as IVsTrackProjectDocuments2;
            if (tracker == null) { Log("rename: IVsTrackProjectDocuments2 is not available"); return; }
            _renameWatcher = new RenameWatcher(this);
            tracker.AdviseTrackProjectDocumentsEvents(_renameWatcher, out _renameCookie);

            // フォルダーの監視も、始める(フォルダー ビュー、エクスプローラー、別のツールでの名前変更も見つけるため)
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            try
            {
                var dte = await GetServiceAsync(typeof(DTE)) as DTE;
                string sln = dte == null ? null : dte.Solution.FullName;
                if (!string.IsNullOrEmpty(sln)) RenameHub.EnsureDir(Path.GetDirectoryName(sln));
                if (dte != null)
                {
                    _solutionEvents = dte.Events.SolutionEvents;
                    _solutionEvents.Opened += () =>
                    {
                        ThreadHelper.ThrowIfNotOnUIThread();
                        try { string s = dte.Solution.FullName; if (!string.IsNullOrEmpty(s)) RenameHub.EnsureDir(Path.GetDirectoryName(s)); }
                        catch (Exception ex) { Log("rename: solution opened handler failed: " + ex.Message); }
                    };
                }
            }
            catch (Exception ex) { Log("rename: start watching failed: " + ex.Message); }
        }

        /// <summary>Solution Explorer などで、ヘッダー・cpp の名前が変わった(監視から呼ばれる)。</summary>
        internal void OnFileRenamed(RenameSync.Move move, bool fromFileSystem)
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try
                {
                    await Task.Delay(400);   // 名前変更の処理が終わるのを待つ
                    await JoinableTaskFactory.SwitchToMainThreadAsync();
                    if (RenameService.Busy) return;
                    var opt = RenameService.Options;
                    if (opt == null || opt.RenameMode != RenameMode.Auto) return;
                    if (fromFileSystem && !opt.RenameWatchFiles) return;
                    // 通知のあと、元に戻された・すでに別の名前になった、などのときは、何もしない
                    if (!File.Exists(move.New) || File.Exists(move.Old)) return;
                    if (RenameHub.IsBulk) { IncludeService.Status("多数のファイル名の変更を検出したので、自動では直しません"); return; }
                    if (opt.RenameConfirm)
                    {
                        var ans = System.Windows.MessageBox.Show(
                            Path.GetFileName(move.Old) + " → " + Path.GetFileName(move.New) + "\n\n相手のファイル、#include、CMake も、新しい名前に直しますか?",
                            "K-CppAssist", System.Windows.MessageBoxButton.YesNo, System.Windows.MessageBoxImage.Question);
                        if (ans != System.Windows.MessageBoxResult.Yes) return;
                    }
                    var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
                    var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
                    var undo = model.GetService<ITextUndoHistoryRegistry>();
                    RenameService.Busy = true;
                    string msg;
                    try { msg = await RenameService.FollowAsync(this, move, adapters, undo); }
                    finally { RenameService.Busy = false; }
                    IncludeService.Status(msg);
                }
                catch (Exception ex) { Log("rename follow failed: " + ex); }
            });
        }

        private void RunRename()
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunRenameAsync(); }
                catch (Exception ex) { await ReportAsync("例外: " + ex.Message, true); Log(ex.ToString()); }
            });
        }

        /// <summary>
        /// いま開いているヘッダー(か cpp)の名前を、入力欄で変え、相手のファイル・#include・CMake にも写す。
        /// </summary>
        private async Task RunRenameAsync()
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var opt = RenameService.Options;
            if (opt.RenameMode == RenameMode.Off) { await ReportAsync("ファイル名の同期は、設定で Off になっています", true); return; }

            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var undo = model.GetService<ITextUndoHistoryRegistry>();
            var dte = (DTE)await GetServiceAsync(typeof(DTE));
            string path = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;
            if (path == null || !(RenameSync.IsHeader(path) || RenameSync.IsSource(path)))
            { await ReportAsync("ヘッダーか cpp を開いて、押してください", true); return; }

            string dir = Path.GetDirectoryName(path);
            string ext = Path.GetExtension(path);
            string oldStem = Path.GetFileNameWithoutExtension(path);
            string input = Ask("新しいファイル名を入力してください (拡張子なし)。\n相手のファイル、#include、CMake も、同じ名前に直します。", oldStem);
            if (string.IsNullOrWhiteSpace(input)) { await ReportAsync("やめました", true); return; }
            string newStem = input.Trim();
            if (newStem.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0 || newStem.EndsWith(".")) { await ReportAsync("ファイル名に使えない文字があります", true); return; }
            if (string.Equals(newStem, oldStem, StringComparison.Ordinal)) { await ReportAsync("名前が変わっていません", true); return; }
            string newPath = Path.Combine(dir, newStem + ext);
            if (File.Exists(newPath)) { await ReportAsync(Path.GetFileName(newPath) + " はすでにあります", true); return; }

            // 開いている文書を保存して、名前を変える(プロジェクトに入っていれば、プロジェクトごと)
            try { dte.ActiveDocument.Save(); } catch (Exception) { }
            var first = new RenameSync.Move { Old = path, New = newPath };
            string msg;
            RenameService.Busy = true;
            try
            {
                string err = RenameService.RenameFile(path, newPath);
                if (err != null) { await ReportAsync("名前を変えられませんでした: " + err, true); return; }
                msg = await RenameService.FollowAsync(this, first, adapters, undo);
            }
            finally { RenameService.Busy = false; }

            // フォルダー ビュー(CMake)などで、名前を変えたファイルが閉じていたら、開き直す
            try
            {
                if (File.Exists(newPath))
                {
                    IVsUIHierarchy hier; uint id; IVsWindowFrame frame;
                    if (!VsShellUtilities.IsDocumentOpen(this, newPath, Guid.Empty, out hier, out id, out frame))
                        VsShellUtilities.OpenDocument(this, newPath, Guid.Empty, out hier, out id, out frame);
                }
            }
            catch (Exception ex) { Log("rename: reopen failed: " + ex.Message); }
            await ReportAsync(msg, false);
        }
    }
}
