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
                if (dte != null) HookClassRename(dte);
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
        // 範囲選択でまとめて動かしたときの通知を、1 つにまとめる(鍵は「古い|新しい」、値は(変更, フォルダーの監視からだけ来たか))
        private readonly object _batchGate = new object();
        private readonly System.Collections.Generic.Dictionary<string, System.Collections.Generic.KeyValuePair<RenameSync.Move, bool>> _batch
            = new System.Collections.Generic.Dictionary<string, System.Collections.Generic.KeyValuePair<RenameSync.Move, bool>>(StringComparer.OrdinalIgnoreCase);
        private int _batchVer;

        internal void OnFileRenamed(RenameSync.Move renamed, bool fromFileSystem)
        {
            int ver;
            lock (_batchGate)
            {
                string key = renamed.Old + "|" + renamed.New;
                System.Collections.Generic.KeyValuePair<RenameSync.Move, bool> had;
                bool fs = fromFileSystem;
                if (_batch.TryGetValue(key, out had)) fs = had.Value && fromFileSystem;
                _batch[key] = new System.Collections.Generic.KeyValuePair<RenameSync.Move, bool>(renamed, fs);
                ver = ++_batchVer;
            }
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try
                {
                    // 範囲選択でまとめて動かすと、通知が 1 つずつ届く。最後の通知から少し待って、まとめて 1 回だけ聞く
                    await Task.Delay(250);
                    System.Collections.Generic.List<System.Collections.Generic.KeyValuePair<RenameSync.Move, bool>> taken;
                    lock (_batchGate)
                    {
                        if (ver != _batchVer) return;               // あとから別の通知が来た(そちらがまとめて扱う)
                        taken = _batch.Values.ToList();
                        _batch.Clear();
                    }
                    await JoinableTaskFactory.SwitchToMainThreadAsync();
                    if (RenameService.Busy) return;
                    var opt = RenameService.Options;
                    if (opt == null || opt.RenameMode != RenameMode.Auto) return;
                    // 通知のあと、元に戻された・すでに別の名前になった、などのものは除く
                    var picked = taken.Where(t => !t.Value || opt.RenameWatchFiles).Where(t => File.Exists(t.Key.New) && !File.Exists(t.Key.Old)).ToList();
                    if (picked.Count == 0) return;
                    // 一括の操作(git のブランチ切り替えなど)とみなすのは、全部がフォルダーの監視から来たときだけ
                    if (picked.All(t => t.Value) && RenameHub.IsBulk) { IncludeService.Status("多数のファイル名の変更を検出したので、自動では直しません"); return; }
                    if (picked.Count > 1) { await FollowManyAsync(picked.Select(t => t.Key).ToList(), opt); return; }
                    var move = picked[0].Key;
                    var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
                    var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
                    var undo = model.GetService<ITextUndoHistoryRegistry>();
                    bool follow = true, renameClass = false;
                    string clsOld = null, clsNew = null;
                    bool matched = false;
                    var pairMove = RenameSync.PairOf(move.Old, move.New, File.Exists);
                    {
                        // クラス名の候補(ヘッダーにあるクラス)を探す。確認しないときも、ダイアログの初期値(クラス名がファイル名と同じなら直す)で動く
                        string oldStem = Path.GetFileNameWithoutExtension(move.Old), newStem = Path.GetFileNameWithoutExtension(move.New);
                        string hdr = RenameSync.IsHeader(move.New) ? move.New : (pairMove != null && RenameSync.IsHeader(pairMove.Old) ? pairMove.Old : null);
                        if (hdr != null && !string.Equals(oldStem, newStem, StringComparison.Ordinal))
                        {
                            string htext = RenameService.ReadAny(hdr, adapters);
                            clsOld = htext == null ? null : RenameSync.PickClass(RenameSync.ClassesIn(htext), oldStem);
                            if (clsOld != null)
                            {
                                // クラス名が古いファイル名に対応していれば(Google の game_object.h と GameObject、Unreal の APawn と Pawn.h も)、
                                // 接頭辞と書き方を保って新しい名前を作る。対応していなければ、新規ファイルの「クラス名の決めかた」で作る
                                string prefix;
                                matched = RenameSync.Corresponds(clsOld, oldStem, out prefix);
                                clsNew = matched ? RenameSync.ClassForNewStem(clsOld, prefix, newStem) : NewFileGen.ClassName(newStem, NewFileService.NamingOf(opt));
                                if (clsNew.Length == 0 || clsNew == clsOld) { clsOld = null; matched = false; }
                            }
                        }
                        renameClass = clsOld != null && matched;
                    }
                    if (opt.RenameConfirm)
                    {
                        // 何が変わるかで、文面を変える(ヘッダー・cpp、相手のファイルのあるなし、別のフォルダーへの移動)
                        bool isHeader = RenameSync.IsHeader(move.New);
                        bool moved = !string.Equals(Path.GetDirectoryName(move.Old), Path.GetDirectoryName(move.New), StringComparison.OrdinalIgnoreCase);
                        string hOld = isHeader ? move.Old : pairMove?.Old, hNew = isHeader ? move.New : pairMove?.New;
                        var lines = new System.Collections.Generic.List<string>();
                        if (pairMove != null) lines.Add(Path.GetFileName(pairMove.Old) + " → " + Path.GetFileName(pairMove.New));
                        if (hOld != null) lines.Add("#include \"" + Path.GetFileName(hOld) + "\" → #include \"" + Path.GetFileName(hNew) + "\"" + (moved ? L.T("  (パスも)") : ""));
                        lines.Add(L.F("CMakeLists.txt の {0} → {1}", Path.GetFileName(move.Old), Path.GetFileName(move.New)));
                        string what = pairMove != null
                            ? (isHeader ? "相手の cpp の名前・#include・CMake も直す" : "相手のヘッダーの名前・#include・CMake も直す")
                            : (hOld != null ? "#include・CMake も直す" : "CMake のファイル名も直す");
                        var items = new System.Collections.Generic.List<RenamePrompt.Item>();
                        items.Add(new RenamePrompt.Item { Text = what, Detail = string.Join("\n", lines), Checked = true });
                        if (clsOld != null)
                            items.Add(new RenamePrompt.Item
                            {
                                Text = matched ? "クラス名も、新しいファイル名に合わせて直す" : "クラス名も直す(いまはファイル名と一致していません)",
                                Detail = "class " + clsOld + " → " + clsNew + L.T("  (コード全体の同じ名前の単語が変わります)"),
                                Checked = matched,
                            });
                        bool dontAsk;
                        string title = moved
                            ? (string.Equals(Path.GetFileName(move.Old), Path.GetFileName(move.New), StringComparison.OrdinalIgnoreCase) ? "ファイルを別のフォルダーに移しました" : "ファイルの名前と場所が変わりました")
                            : (isHeader ? "ヘッダーの名前が変わりました" : "cpp の名前が変わりました");
                        var res = RenamePrompt.Show(title, Path.GetFileName(move.Old) + " → " + Path.GetFileName(move.New), items, out dontAsk);
                        if (res == null) return;
                        if (dontAsk) RenamePrompt.TurnOffConfirm();
                        follow = res[0];
                        renameClass = clsOld != null && res[1];
                        if (!follow && !renameClass) return;
                    }
                    RenameService.Busy = true;
                    _classWatchRun++;       // Ctrl+R, R のあとの監視が残っていても、ここで書き換えたクラス名を、もう一度拾わせない
                    string msg = "";
                    try
                    {
                        if (follow) msg = await RenameService.FollowAsync(this, move, adapters, undo);
                        if (renameClass)
                        {
                            int n = await RenameService.ReplaceWordAsync(clsOld, clsNew, IncludeService.RootFor(move.New), IncludeService.SkipDirs(opt), adapters, undo);
                            msg += (msg.Length > 0 ? "。" : "") + "クラス名 " + clsOld + " → " + clsNew + " (" + n + " か所)";
                        }
                    }
                    finally { RenameService.Busy = false; }
                    IncludeService.Status(msg);
                }
                catch (Exception ex) { Log("rename follow failed: " + ex); }
            });
        }


        /// <summary>範囲選択でまとめて名前を変えた(動かした)ファイルを、1 つのダイアログで聞いて、まとめて直す。UI スレッドから呼ぶ。</summary>
        private async Task FollowManyAsync(System.Collections.Generic.List<RenameSync.Move> moves, OptionsPage opt)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var undo = model.GetService<ITextUndoHistoryRegistry>();
            // 相手(Foo.h に対する Foo.cpp)のうち、まとめて動かした中に入っていないもの
            var pairs = new System.Collections.Generic.List<RenameSync.Move>();
            if (opt.RenamePair)
                foreach (var m in moves)
                {
                    var p = RenameSync.PairOf(m.Old, m.New, File.Exists);
                    if (p != null && !moves.Any(x => string.Equals(x.Old, p.Old, StringComparison.OrdinalIgnoreCase)) && !pairs.Any(x => string.Equals(x.Old, p.Old, StringComparison.OrdinalIgnoreCase))) pairs.Add(p);
                }
            bool doPairs = pairs.Count > 0;
            if (opt.RenameConfirm)
            {
                var oldDirs = moves.Select(m => Path.GetDirectoryName(m.Old)).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
                var newDirs = moves.Select(m => Path.GetDirectoryName(m.New)).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
                bool moved = moves.Any(m => !string.Equals(Path.GetDirectoryName(m.Old), Path.GetDirectoryName(m.New), StringComparison.OrdinalIgnoreCase));
                string title = moved ? L.F("{0} 個のファイルを移しました", moves.Count) : L.F("{0} 個のファイルの名前が変わりました", moves.Count);
                string sub = moved && oldDirs.Count == 1 && newDirs.Count == 1 ? RenameService.FolderLabel(oldDirs[0], newDirs[0]) : null;
                System.Func<RenameSync.Move, string> line = m => moved
                    ? Path.GetFileName(m.Old) + " → " + Path.GetFileName(Path.GetDirectoryName(m.New)) + "/" + Path.GetFileName(m.New)
                    : Path.GetFileName(m.Old) + " → " + Path.GetFileName(m.New);
                string list = string.Join("\n", moves.Take(8).Select(line)) + (moves.Count > 8 ? L.F("\n… ほか {0} 個", moves.Count - 8) : "");
                var items = new System.Collections.Generic.List<RenamePrompt.Item>
                {
                    new RenamePrompt.Item { Text = "全部の #include・CMake を、新しいパスに直す", Detail = list, Checked = true },
                };
                if (pairs.Count > 0)
                    items.Add(new RenamePrompt.Item
                    {
                        Text = L.F("相手のファイル {0} 個の名前も直す", pairs.Count),
                        Detail = string.Join("\n", pairs.Take(6).Select(p => Path.GetFileName(p.Old) + " → " + Path.GetFileName(p.New))) + (pairs.Count > 6 ? "\n…" : ""),
                        Checked = true,
                    });
                bool dontAsk;
                var res = RenamePrompt.Show(title, sub, items, out dontAsk, "全部に反映する");
                if (res == null) return;
                if (dontAsk) RenamePrompt.TurnOffConfirm();
                if (!res[0]) return;
                doPairs = pairs.Count > 0 && res[1];
            }
            RenameService.Busy = true;
            _classWatchRun++;
            string msg;
            try { msg = await RenameService.FollowManyAsync(moves, doPairs ? pairs : null, adapters, undo); }
            finally { RenameService.Busy = false; }
            IncludeService.Status(msg);
        }

        /// <summary>ディスクのフォルダーの名前が変わった(か、移った)。中のヘッダーを #include している所と、CMake を直すか聞く。</summary>
        internal void OnFolderRenamed(string oldDir, string newDir, bool fromFileSystem)
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try
                {
                    await Task.Delay(300);   // 中のファイルの通知が落ち着くのを待つ
                    await JoinableTaskFactory.SwitchToMainThreadAsync();
                    if (RenameService.Busy) return;
                    var opt = RenameService.Options;
                    if (opt == null || opt.RenameMode != RenameMode.Auto) return;
                    if (fromFileSystem && !opt.RenameWatchFiles) return;
                    if (!Directory.Exists(newDir) || Directory.Exists(oldDir)) return;
                    var moves = await Task.Run(() => RenameService.MovesInFolder(oldDir, newDir));
                    await JoinableTaskFactory.SwitchToMainThreadAsync();
                    if (moves.Count == 0) return;
                    int headers = moves.Count(m => RenameSync.IsHeader(m.New));
                    var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
                    var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
                    var undo = model.GetService<ITextUndoHistoryRegistry>();
                    string label = RenameService.FolderLabel(oldDir, newDir);
                    bool samePlace = string.Equals(Path.GetDirectoryName(oldDir), Path.GetDirectoryName(newDir), StringComparison.OrdinalIgnoreCase);
                    if (opt.RenameConfirm)
                    {
                        var sample = moves.FirstOrDefault(m => RenameSync.IsHeader(m.New)) ?? moves[0];
                        string relOld = Path.GetFileName(oldDir) + "/" + Path.GetFileName(sample.Old), relNew = Path.GetFileName(newDir) + "/" + Path.GetFileName(sample.New);
                        var items = new System.Collections.Generic.List<RenamePrompt.Item>
                        {
                            new RenamePrompt.Item
                            {
                                Text = "中のファイルを #include している所と、CMake のパスを直す",
                                Detail = L.F("ヘッダー {0} 個、cpp {1} 個\n例: #include \"{2}\" → #include \"{3}\"", headers, moves.Count - headers, relOld, relNew),
                                Checked = true,
                            },
                        };
                        bool dontAsk;
                        var res = RenamePrompt.Show(samePlace ? "フォルダーの名前が変わりました" : "フォルダーを移しました", label, items, out dontAsk);
                        if (res == null) return;
                        if (dontAsk) RenamePrompt.TurnOffConfirm();
                        if (!res[0]) return;
                    }
                    RenameService.Busy = true;
                    string msg;
                    try { msg = await RenameService.FollowFolderAsync(oldDir, newDir, moves, adapters, undo); }
                    finally { RenameService.Busy = false; }
                    IncludeService.Status(msg);
                }
                catch (Exception ex) { Log("rename folder failed: " + ex); }
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
            // 名前を変える前に、自分の変更だと覚える(フォルダーの監視の通知が先に届くと、もう一度「名前が変わった」と見つけてしまう)
            RenameHub.Remember(first);
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
