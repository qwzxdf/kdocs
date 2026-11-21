using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using EnvDTE;
using Microsoft.VisualStudio.ComponentModelHost;
using Microsoft.VisualStudio.Editor;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text.Operations;
using Task = System.Threading.Tasks.Task;

namespace KCppAssist
{
    /// <summary>
    /// VS の「名前の変更」(Ctrl+R, R)でクラス名が変わったら、ファイル名と #include も直すか聞く。
    /// 実行の前にヘッダーのクラス名を控え、実行のあとに(ダイアログが閉じるまで待ちながら)見比べて、1 つだけ名前が変わっていたら出す。
    /// </summary>
    public sealed partial class KCppAssistPackage
    {
        private CommandEvents _refactorRenameEvents;       // イベントを保つ
        private Dictionary<string, List<string>> _classesBefore;
        private int _classWatchRun;

        private void HookClassRename(DTE dte)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                Command cmd = null;
                foreach (string name in new[] { "Refactor.Rename", "Edit.Rename" })
                {
                    try { cmd = dte.Commands.Item(name, -1); if (cmd != null) break; } catch (Exception) { }
                }
                if (cmd == null) { Log("class rename: Refactor.Rename was not found"); return; }
                _refactorRenameEvents = dte.Events.get_CommandEvents(cmd.Guid, cmd.ID);
                _refactorRenameEvents.BeforeExecute += (string g, int id, object ci, object co, ref bool cancel) =>
                {
                    ThreadHelper.ThrowIfNotOnUIThread();
                    try { SnapshotClasses(dte); } catch (Exception ex) { Log("class rename: snapshot failed: " + ex.Message); }
                };
                _refactorRenameEvents.AfterExecute += (string g, int id, object ci, object co) =>
                {
                    ThreadHelper.ThrowIfNotOnUIThread();
                    if (_classesBefore == null || _classesBefore.Count == 0) return;
                    int run = ++_classWatchRun;
                    var before = _classesBefore;
                    _ = JoinableTaskFactory.RunAsync(() => WatchClassRenameAsync(run, before));
                };
            }
            catch (Exception ex) { Log("class rename: hook failed: " + ex.Message); }
        }

        private void SnapshotClasses(DTE dte)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            _classesBefore = null;
            var opt = RenameService.Options;
            if (opt == null || opt.RenameMode == RenameMode.Off) return;
            string path = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;
            if (path == null || !(RenameSync.IsHeader(path) || RenameSync.IsSource(path))) return;
            var model = (IComponentModel)GetGlobalService(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var files = new List<string> { path };
            string dir = Path.GetDirectoryName(path), stem = Path.GetFileNameWithoutExtension(path);
            foreach (string ext in new[] { ".h", ".hpp", ".hh", ".hxx" })
            {
                string h = Path.Combine(dir, stem + ext);
                if (!files.Contains(h, StringComparer.OrdinalIgnoreCase) && File.Exists(h)) files.Add(h);
            }
            var map = new Dictionary<string, List<string>>(StringComparer.OrdinalIgnoreCase);
            foreach (string f in files)
            {
                if (!RenameSync.IsHeader(f)) continue;
                string text = RenameService.ReadAny(f, adapters);
                if (text != null) map[f] = RenameSync.ClassesIn(text);
            }
            _classesBefore = map;
        }

        private async Task WatchClassRenameAsync(int run, Dictionary<string, List<string>> before)
        {
            try
            {
                // 最初は短い間隔で見る(名前の変更は、ダイアログを閉じた直後に終わることが多い)。60 秒ほどで、あきらめる
                for (int i = 0; i < 130 && run == _classWatchRun; i++)
                {
                    await Task.Delay(i < 20 ? 250 : 500);
                    await JoinableTaskFactory.SwitchToMainThreadAsync();
                    if (run != _classWatchRun || RenameService.Busy) return;
                    var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
                    var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
                    foreach (var kv in before)
                    {
                        string text = RenameService.ReadAny(kv.Key, adapters);
                        if (text == null) continue;
                        var now = RenameSync.ClassesIn(text);
                        var gone = kv.Value.Where(c => !now.Contains(c)).ToList();
                        var added = now.Where(c => !kv.Value.Contains(c)).ToList();
                        if (gone.Count != 1 || added.Count != 1) continue;
                        _classWatchRun++;
                        await OfferFileRenameAsync(kv.Key, gone[0], added[0], model);
                        return;
                    }
                }
            }
            catch (Exception ex) { Log("class rename watch failed: " + ex); }
        }

        private async Task OfferFileRenameAsync(string header, string oldName, string newName, IComponentModel model)
        {
            string dir = Path.GetDirectoryName(header), ext = Path.GetExtension(header), oldStem = Path.GetFileNameWithoutExtension(header);
            // ファイル名は、古いファイル名の書き方に合わせる(Google の game_object.h なら、GameEntity → game_entity.h)。接頭辞(APawn の A)は外す
            string prefix;
            bool matched = RenameSync.Corresponds(oldName, oldStem, out prefix);
            string newStem = RenameSync.StemForNewClass(newName, prefix, oldStem);
            if (string.Equals(oldStem, newStem, StringComparison.Ordinal)) return;
            string newPath = Path.Combine(dir, newStem + ext);
            if (newStem.Length == 0 || newStem.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0 || File.Exists(newPath)) return;
            var move = new RenameSync.Move { Old = header, New = newPath };
            var pair = RenameSync.PairOf(header, newPath, File.Exists);
            string detail = Path.GetFileName(header) + " → " + Path.GetFileName(newPath);
            if (pair != null) detail += "\n" + Path.GetFileName(pair.Old) + " → " + Path.GetFileName(pair.New);
            detail += "\n#include \"" + Path.GetFileName(header) + "\" → #include \"" + Path.GetFileName(newPath) + "\"";
            var opt = RenameService.Options;
            if (opt != null && opt.RenameConfirm)
            {
                bool dontAsk;
                string text = matched
                    ? "ファイル名・相手のファイル・#include・CMake も直す"
                    : "ファイル名も直す (いまのファイル名 " + Path.GetFileName(header) + " は、クラス名と違っています)";
                var res = RenamePrompt.Show("クラス名が変わりました", oldName + " → " + newName,
                    new List<RenamePrompt.Item> { new RenamePrompt.Item { Text = text, Detail = detail, Checked = matched } },
                    out dontAsk);
                if (res == null) return;
                if (dontAsk) RenamePrompt.TurnOffConfirm();
                if (!res[0]) return;
            }
            // 確認しないときは、ダイアログの初期値と同じく、ファイル名がクラス名と同じだったときだけ直す
            else if (!matched) return;

            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var undo = model.GetService<ITextUndoHistoryRegistry>();
            var dte = (DTE)await GetServiceAsync(typeof(DTE));
            try { foreach (Document d in dte.Documents) { try { if (string.Equals(d.FullName, header, StringComparison.OrdinalIgnoreCase)) d.Save(); } catch (Exception) { } } } catch (Exception) { }
            string msg;
            // 名前を変える前に、自分の変更だと覚える(フォルダーの監視の通知が先に届くと、ファイル名の変更のダイアログがもう一度出る)
            RenameHub.Remember(move);
            RenameService.Busy = true;
            try
            {
                string err = RenameService.RenameFile(header, newPath);
                if (err != null) { await ReportAsync("ファイル名を変えられませんでした: " + err, true); return; }
                msg = await RenameService.FollowAsync(this, move, adapters, undo);
            }
            finally { RenameService.Busy = false; }
            await ReportAsync(msg, false);
        }
    }
}
