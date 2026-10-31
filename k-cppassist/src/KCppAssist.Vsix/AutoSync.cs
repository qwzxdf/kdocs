using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Threading;
using Microsoft.VisualStudio.Editor;
using Microsoft.VisualStudio.Language.Intellisense.AsyncCompletion;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Text.Operations;
using Microsoft.VisualStudio.Utilities;

namespace KCppAssist
{
    /// <summary>C/C++ のエディターが開くたびに、関数の引数の変更を相手(ヘッダー⇔cpp)へ写す監視を付ける。設定が Auto でなければ、何もしない。</summary>
    [Export(typeof(IWpfTextViewCreationListener))]
    [ContentType("C/C++")]
    [TextViewRole(PredefinedTextViewRoles.Document)]
    internal sealed class SignatureSyncListener : IWpfTextViewCreationListener
    {
        [Import] internal ITextDocumentFactoryService Documents { get; set; }
        [Import] internal ITextUndoHistoryRegistry Undo { get; set; }
        [Import] internal IAsyncCompletionBroker Completion { get; set; }
        [Import] internal IVsEditorAdaptersFactoryService Adapters { get; set; }

        public void TextViewCreated(IWpfTextView view)
        {
            try { new SignatureSyncSession(view, this); }
            catch (Exception ex) { KCppAssistPackage.Log("signature sync attach failed: " + ex); }
        }
    }

    /// <summary>
    /// 1 つのエディターについて、関数の引数の括弧を追跡する。引数が変わって入力が落ち着いたら、相手側の同じ関数の引数を書き換える。
    /// 相手が見つからない、複数ある、エディターで開いていない、書きかけのときは、何もしない(開いていないときはステータスバーで知らせる)。
    /// </summary>
    internal sealed class SignatureSyncSession
    {
        private sealed class Item
        {
            public ITrackingSpan Inner;      // 括弧の中身
            public string Class, Name;
            public string Text;              // 変える前の中身
            public bool HasBody;
        }

        private readonly IWpfTextView view;
        private readonly SignatureSyncListener owner;
        private readonly DispatcherTimer timer;
        private readonly string path;
        private List<Item> baseline;
        private DateTime lastChange = DateTime.MinValue;
        private bool busy;

        public SignatureSyncSession(IWpfTextView view, SignatureSyncListener owner)
        {
            this.view = view;
            this.owner = owner;
            ITextDocument doc;
            if (owner.Documents.TryGetTextDocument(view.TextBuffer, out doc)) path = doc.FilePath;
            timer = new DispatcherTimer(DispatcherPriority.ApplicationIdle, view.VisualElement.Dispatcher);
            timer.Tick += OnTick;
            view.TextBuffer.Changed += OnChanged;
            view.Closed += OnClosed;
        }

        private void OnClosed(object sender, EventArgs e)
        {
            timer.Stop();
            timer.Tick -= OnTick;
            view.TextBuffer.Changed -= OnChanged;
            view.Closed -= OnClosed;
            baseline = null;
        }

        private static bool IsAuto
        {
            get { var o = SyncService.Options; return o != null && o.SyncMode == SyncMode.Auto; }
        }

        private void Arm(int ms)
        {
            timer.Interval = TimeSpan.FromMilliseconds(Math.Max(200, ms));
            timer.Stop();
            timer.Start();
        }

        private void OnChanged(object sender, TextContentChangedEventArgs e)
        {
            if (path == null || !IsAuto) return;
            // 相手の編集としてこちらに写された変更は、また相手へ戻さない
            if (e.EditTag is string && (string)e.EditTag == SyncService.EditTag) { baseline = Build(e.After); return; }
            if (baseline == null) baseline = Build(e.Before);
            lastChange = DateTime.UtcNow;
            Arm(1200);
        }

        /// <summary>いまの文字から、引数を追跡する関数の一覧を作る(クラスの中に本体のある関数は、相手がないので除く)。</summary>
        private List<Item> Build(ITextSnapshot snap)
        {
            var list = new List<Item>();
            try
            {
                foreach (var s in FunctionScan.Scan(snap.GetText()))
                {
                    if (s.HasBody && s.InClass) continue;
                    list.Add(new Item
                    {
                        Inner = snap.CreateTrackingSpan(s.Open + 1, s.Close - s.Open - 1, SpanTrackingMode.EdgeInclusive),
                        Class = s.Class,
                        Name = s.Name,
                        HasBody = s.HasBody,
                        Text = snap.GetText(s.Open + 1, s.Close - s.Open - 1),
                    });
                }
            }
            catch (Exception ex) { KCppAssistPackage.Log("sync build failed: " + ex.Message); }
            return list;
        }

        private async void OnTick(object sender, EventArgs e)
        {
            timer.Stop();
            if (busy) return;
            busy = true;
            try { await TickAsync(); }
            catch (Exception ex) { KCppAssistPackage.Log("signature sync failed: " + ex); }
            finally { busy = false; }
        }

        private async Task TickAsync()
        {
            if (!IsAuto || baseline == null) { if (!IsAuto) baseline = null; return; }
            if (SyncService.IsBusy(view, owner.Completion)) { Arm(1000); return; }

            ITextSnapshot snap = view.TextSnapshot;
            string text = snap.GetText();
            var sigs = FunctionScan.Scan(text);

            var changed = new List<KeyValuePair<Item, FunctionScan.Sig>>();
            foreach (Item b in baseline)
            {
                SnapshotSpan span = b.Inner.GetSpan(snap);
                var cs = sigs.FirstOrDefault(s => s.Open == span.Start.Position - 1 && s.Close == span.End.Position && s.Name == b.Name && s.Class == b.Class);
                if (cs == null) continue;
                if (SignatureSync.Norm(span.GetText()) != SignatureSync.Norm(b.Text)) changed.Add(new KeyValuePair<Item, FunctionScan.Sig>(b, cs));
            }
            if (changed.Count == 0) { baseline = Build(snap); return; }

            // 括弧の中で、いま打っている最中なら、少し長く待つ
            int caret = view.Caret.Position.BufferPosition.Position;
            bool inside = changed.Any(c => caret >= c.Value.Open && caret <= c.Value.Close + 1);
            if (inside && (DateTime.UtcNow - lastChange).TotalMilliseconds < 4000) { Arm(1000); return; }

            foreach (var c in changed.Take(3))
            {
                SnapshotSpan span = c.Key.Inner.GetSpan(snap);
                await SyncOneAsync(c.Key, span.GetText());
            }
            baseline = Build(view.TextSnapshot);
        }

        private async Task SyncOneAsync(Item b, string curInner)
        {
            var oldList = SignatureSync.SplitParams(b.Text);
            var newList = SignatureSync.SplitParams(curInner);
            if (oldList == null || newList == null) return;          // 書きかけ

            var opt = SyncService.Options;
            bool wantDef = !b.HasBody;                               // 宣言を変えたなら定義を、定義を変えたなら宣言を探す
            string root = IncludeService.RootFor(path);
            var skip = IncludeService.SkipDirs(opt);
            List<string> files = await Task.Run(() =>
            {
                if (!wantDef) IncludeService.Index.Refresh(root, skip, false);
                return SyncService.Candidates(path, b.Class, root, wantDef, opt);
            });
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

            string label = (b.Class == null ? "" : b.Class + "::") + b.Name;
            var targets = SyncService.FindTargets(files, wantDef, b.Class, b.Name, owner.Adapters);
            var oldKeys = SignatureSync.TypeKeys(oldList);
            var newKeys = SignatureSync.TypeKeys(newList);
            Func<SyncService.Target, List<string>> keysOf = t => { var l = SignatureSync.SplitParams(t.Inner); return l == null ? null : SignatureSync.TypeKeys(l); };

            var matches = targets.Where(t => SyncService.SameKeys(keysOf(t), oldKeys)).ToList();
            if (matches.Count == 0)
            {
                if (targets.Any(t => SyncService.SameKeys(keysOf(t), newKeys))) return;       // もう合っている
                IncludeService.Status(label + " の" + (wantDef ? "定義" : "宣言") + "が見つからないので、引数を写せませんでした");
                return;
            }
            if (matches.Count > 1) { IncludeService.Status(label + " の" + (wantDef ? "定義" : "宣言") + "が複数あるので、引数を写せませんでした (Alt+G で選べます)"); return; }

            var t0 = matches[0];
            if (t0.Buffer == null)
            {
                IncludeService.Status(Path.GetFileName(t0.File) + " は開いていません。Alt+G で " + label + " の引数を写せます");
                return;
            }
            var cpList = SignatureSync.SplitParams(t0.Inner);
            if (cpList == null || t0.Buffer.CurrentSnapshot.Length != t0.Text.Length) return;
            string newInner = SignatureSync.Rebuild(oldList, newList, cpList, !wantDef, t0.Inner);
            SyncService.Replace(t0.Buffer, t0.Sig.Open + 1, t0.Sig.Close - t0.Sig.Open - 1, newInner, owner.Undo, "K-CppAssist: 引数を合わせる");
            IncludeService.Status(label + " の引数を " + Path.GetFileName(t0.File) + " に写しました");
        }
    }
}
