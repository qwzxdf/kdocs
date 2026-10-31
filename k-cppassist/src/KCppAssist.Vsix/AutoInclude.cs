using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Threading;
using EnvDTE;
using Microsoft.VisualStudio.Language.Intellisense.AsyncCompletion;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Text.Operations;
using Microsoft.VisualStudio.Text.Tagging;
using Microsoft.VisualStudio.Utilities;

namespace KCppAssist
{
    /// <summary>C/C++ のエディターが開くたびに、入力中の #include 自動挿入の監視を付ける。設定が Auto でなければ、何もしない。</summary>
    [Export(typeof(IWpfTextViewCreationListener))]
    [ContentType("C/C++")]
    [TextViewRole(PredefinedTextViewRoles.Document)]
    internal sealed class AutoIncludeListener : IWpfTextViewCreationListener
    {
        [Import] internal ITextDocumentFactoryService Documents { get; set; }
        [Import] internal IViewTagAggregatorFactoryService Tags { get; set; }
        [Import] internal ITextUndoHistoryRegistry Undo { get; set; }
        [Import] internal IAsyncCompletionBroker Completion { get; set; }

        public void TextViewCreated(IWpfTextView view)
        {
            try { new AutoIncludeSession(view, this); }
            catch (Exception ex) { KCppAssistPackage.Log("auto include attach failed: " + ex); }
        }
    }

    /// <summary>
    /// 1 つのエディターについて、識別子を打ち終えた(区切りを打った)ところを覚え、入力が止まってから調べて、足りない #include を足す。
    /// 足すのは、識別子に「未定義」の波線が付いていて、型として使われていて、ヘッダーが 1 つに決まるときだけ。
    /// </summary>
    internal sealed class AutoIncludeSession
    {
        private sealed class Pending
        {
            public ITrackingSpan Span;
            public string Name;          // 1 つの識別子のとき。貼り付けなどのまとまった範囲のときは null
            public DateTime Deadline;
        }

        private sealed class Added
        {
            public ITrackingSpan Ident;
            public string Name;
            public string Text;          // 足した文字(取り消すときに、そのまま探す)
            public DateTime Until;
        }

        private const int MaxPerTick = 1;

        private readonly IWpfTextView view;
        private readonly AutoIncludeListener owner;
        private readonly ITagAggregator<IErrorTag> errors;
        private readonly DispatcherTimer timer;
        private readonly List<Pending> pending = new List<Pending>();
        private readonly List<Added> added = new List<Added>();
        private string path;
        private bool busy;

        public AutoIncludeSession(IWpfTextView view, AutoIncludeListener owner)
        {
            this.view = view;
            this.owner = owner;
            ITextDocument doc;
            if (owner.Documents.TryGetTextDocument(view.TextBuffer, out doc)) path = doc.FilePath;
            errors = owner.Tags.CreateTagAggregator<IErrorTag>(view);
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
            errors.Dispose();
            pending.Clear();
            added.Clear();
        }

        private static OptionsPage Opt { get { return IncludeService.Options; } }

        private static bool IsAuto
        {
            get { var o = Opt; return o != null && o.IncludeMode == IncludeMode.Auto; }
        }

        private void Arm(int ms)
        {
            timer.Interval = TimeSpan.FromMilliseconds(Math.Max(200, ms));
            timer.Stop();
            timer.Start();
        }

        private void OnChanged(object sender, TextContentChangedEventArgs e)
        {
            if (!IsAuto) return;
            if (e.EditTag is string && (string)e.EditTag == IncludeService.EditTag) return;
            bool any = false;
            ITextSnapshot after = e.After;
            foreach (var c in e.Changes)
            {
                if (c.NewLength == 0) { any = true; continue; }
                string ins = c.NewText;
                if (ins.Trim().Length == 0 || (ins.Length == 1 && "<>:*&(){},;".IndexOf(ins[0]) >= 0))
                {
                    // 区切りを打った。その左の識別子が、打ち終えたもの
                    int end = c.NewPosition;
                    int st = end;
                    while (st > 0 && CppText.IsId(after[st - 1])) st--;
                    if (end > st && !char.IsDigit(after[st]))
                    {
                        pending.Add(new Pending
                        {
                            Span = after.CreateTrackingSpan(st, end - st, SpanTrackingMode.EdgeExclusive),
                            Name = after.GetText(st, end - st),
                            Deadline = DateTime.UtcNow.AddSeconds(10),
                        });
                        any = true;
                    }
                }
                else if (ins.Length > 1)
                {
                    // 貼り付けや補完の確定など、まとまった入力
                    pending.Add(new Pending
                    {
                        Span = after.CreateTrackingSpan(c.NewPosition, c.NewLength, SpanTrackingMode.EdgeInclusive),
                        Deadline = DateTime.UtcNow.AddSeconds(12),
                    });
                    any = true;
                }
            }
            if (any || added.Count > 0) Arm(Opt.IncludeDelayMs);
        }

        private async void OnTick(object sender, EventArgs e)
        {
            timer.Stop();
            if (busy) return;
            busy = true;
            try { await TickAsync(); }
            catch (Exception ex) { KCppAssistPackage.Log("auto include failed: " + ex); }
            finally { busy = false; }
        }

        private bool Blocked()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            if (!view.HasAggregateFocus) return true;
            try { if (owner.Completion.IsCompletionActive(view)) return true; } catch (Exception) { }
            try
            {
                var dte = (DTE)Package.GetGlobalService(typeof(DTE));
                if (dte != null && dte.Solution.SolutionBuild.BuildState == vsBuildState.vsBuildStateInProgress) return true;
            }
            catch (Exception) { }
            return false;
        }

        private async Task TickAsync()
        {
            var opt = Opt;
            if (opt == null || opt.IncludeMode != IncludeMode.Auto) { pending.Clear(); added.Clear(); return; }

            RevertStale();

            DateTime now = DateTime.UtcNow;
            pending.RemoveAll(p => p.Deadline < now);
            if (pending.Count == 0 || path == null) { if (path == null) pending.Clear(); return; }
            if (Blocked()) { Arm(1000); return; }

            string root = IncludeService.RootFor(path);
            var skip = IncludeService.SkipDirs(opt);
            await Task.Run(() => IncludeService.Index.Refresh(root, skip, false));
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
            if (!IsAuto) return;

            ITextSnapshot snap = view.TextSnapshot;
            string text = snap.GetText();
            string masked = CppText.Mask(text);
            int caret = view.Caret.Position.BufferPosition.Position;
            bool inHeader = IncludeService.IsHeader(path);
            string stem = inHeader ? null : Path.GetFileNameWithoutExtension(path);
            string eol = text.Contains("\r\n") ? "\r\n" : "\n";

            int done = 0;
            foreach (Pending p in pending.ToList())
            {
                SnapshotSpan span = p.Span.GetSpan(snap);
                if (span.IsEmpty) { pending.Remove(p); continue; }

                IEnumerable<KeyValuePair<int, string>> idents;
                if (p.Name != null)
                {
                    if (span.GetText() != p.Name) { pending.Remove(p); continue; }
                    idents = new[] { new KeyValuePair<int, string>(span.Start.Position, p.Name) };
                }
                else idents = CppText.Identifiers(masked, span.Start.Position, span.End.Position);

                bool keep = false;
                bool applied = false;
                foreach (var id in idents)
                {
                    int start = id.Key, end = id.Key + id.Value.Length;
                    if (caret > start && caret <= end) { keep = true; continue; }          // まだ、その識別子の上で編集している
                    if (masked.Substring(start, end - start) != id.Value) continue;         // コメントや文字列の中
                    int chainStart;
                    string chain = CppText.TypeUseName(masked, start, end, out chainStart);
                    if (chain == null) continue;                                            // 型として使われている形ではない
                    if (!IncludeService.HasError(errors, new SnapshotSpan(snap, chainStart, end - chainStart)))
                    { keep = true; continue; }                                              // 波線がまだ出ていない(か、解決済み)

                    var res = IncludeService.Resolve(chain, path, root, opt, false);
                    if (res == null || res.Token == null) continue;                         // 知らない名前、または複数あって決まらない
                    if (inHeader && res.Source != IncludeService.TableSource) continue;     // ヘッダーでは、表のものだけ自動
                    if (IncludeService.WouldCycle(res.File, path)) continue;
                    var edit = IncludeEditor.Plan(text, res.Token, stem, eol);
                    if (edit == null) continue;                                             // すでにある

                    var tracker = snap.CreateTrackingSpan(start, end - start, SpanTrackingMode.EdgeExclusive);
                    IncludeService.Apply(view.TextBuffer, edit.Position, edit.Text, owner.Undo, "K-CppAssist: #include を追加");
                    added.Add(new Added { Ident = tracker, Name = id.Value, Text = edit.Text, Until = DateTime.UtcNow.AddSeconds(40) });
                    IncludeService.Status(id.Value + " のために " + res.Token + " を追加しました (" + res.Source + ")");
                    done++;
                    applied = true;
                    break;
                }
                if (applied || !keep) pending.Remove(p);
                if (done >= MaxPerTick) break;                                              // 文字が変わったので、残りは次の回
            }

            if (pending.Count > 0 || added.Count > 0) Arm(done > 0 ? 300 : 1000);
        }

        /// <summary>足した直後に、その識別子を消したり書き換えたりしたら、足した #include も戻す。</summary>
        private void RevertStale()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            if (added.Count == 0) return;
            ITextSnapshot snap = view.TextSnapshot;
            DateTime now = DateTime.UtcNow;
            foreach (Added a in added.ToList())
            {
                if (a.Until < now) { added.Remove(a); continue; }
                SnapshotSpan sp = a.Ident.GetSpan(snap);
                if (!sp.IsEmpty && sp.GetText() == a.Name) continue;

                added.Remove(a);
                string text = snap.GetText();
                if (Regex.IsMatch(CppText.Mask(text), @"(?<![\w])" + Regex.Escape(a.Name) + @"(?![\w])")) continue;   // 別の場所でまだ使っている
                int idx = text.IndexOf(a.Text, StringComparison.Ordinal);
                if (idx < 0) continue;
                IncludeService.Remove(view.TextBuffer, idx, a.Text.Length, owner.Undo, "K-CppAssist: 自動で足した #include を戻す");
                IncludeService.Status(a.Name + " を消したので、足した #include も戻しました");
            }
        }
    }
}
