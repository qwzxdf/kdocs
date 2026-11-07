using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Adornments;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Text.Tagging;
using Microsoft.VisualStudio.Utilities;

namespace KCppAssist
{
    /// <summary>
    /// 開いているファイルと、そのヘッダーの内容(保存していない編集も含む)を共有する場所。
    /// ヘッダーを編集したら、ほかの開いているファイルの呼び出しチェックをやり直す。
    /// </summary>
    internal static class CallCheckHub
    {
        private static readonly object gate = new object();
        private static readonly Dictionary<string, WeakReference<ITextBuffer>> buffers = new Dictionary<string, WeakReference<ITextBuffer>>(StringComparer.OrdinalIgnoreCase);
        private static readonly List<WeakReference<CallCheckTagger>> taggers = new List<WeakReference<CallCheckTagger>>();

        public static void Register(string path, ITextBuffer buffer, CallCheckTagger tagger)
        {
            lock (gate)
            {
                if (path != null) buffers[path] = new WeakReference<ITextBuffer>(buffer);
                taggers.RemoveAll(w => { CallCheckTagger t; return !w.TryGetTarget(out t); });
                taggers.Add(new WeakReference<CallCheckTagger>(tagger));
            }
        }

        /// <summary>開いているファイルなら、いまのエディターの文字。開いていなければ null。</summary>
        public static string OpenText(string path)
        {
            WeakReference<ITextBuffer> w;
            lock (gate) { if (!buffers.TryGetValue(path, out w)) return null; }
            ITextBuffer b;
            return w.TryGetTarget(out b) ? b.CurrentSnapshot.GetText() : null;
        }

        /// <summary>ヘッダーが編集された。from 以外の、開いているファイルのチェックをやり直す。</summary>
        public static void HeaderEdited(CallCheckTagger from)
        {
            List<CallCheckTagger> list;
            lock (gate)
                list = taggers.Select(w => { CallCheckTagger t; return w.TryGetTarget(out t) ? t : null; }).Where(t => t != null && t != from).ToList();
            foreach (var t in list) t.Schedule();
        }
    }

    /// <summary>クラスの定義(コンストラクターの一覧)を探す。ファイルの内容が変わらない限り、読み取りの結果を覚えておく。</summary>
    internal static class CallCheckLookup
    {
        private sealed class Cached { public string Text; public CallCheck.ClassInfo Info; }

        private static readonly Dictionary<string, Cached> cache = new Dictionary<string, Cached>(StringComparer.OrdinalIgnoreCase);

        /// <summary>
        /// name の型を定義しているのが、いま調べているファイルか、索引で 1 つに決まるヘッダーのときだけ、その情報を返す。
        /// 複数あって決まらない、索引にない、読めない、などは null(=調べない)。
        /// </summary>
        public static CallCheck.ClassInfo Find(string curPath, string curText, string qualifier, string name)
        {
            try
            {
                if (CallCheck.DefinesClass(curText, name)) return CallCheck.ReadClass(curText, name, qualifier);

                var files = IncludeService.Index.Lookup(name).Where(f => !string.Equals(f, curPath, StringComparison.OrdinalIgnoreCase)).ToList();
                if (files.Count != 1) return null;
                string file = files[0];
                string text = CallCheckHub.OpenText(file);
                if (text == null) text = File.ReadAllText(file);
                string key = file + "|" + name + "|" + qualifier;
                Cached c;
                lock (cache)
                    if (cache.TryGetValue(key, out c) && c.Text == text) return c.Info;
                var info = CallCheck.DefinesClass(text, name) ? CallCheck.ReadClass(text, name, qualifier) : null;
                lock (cache) cache[key] = new Cached { Text = text, Info = info };
                return info;
            }
            catch (Exception ex)
            {
                KCppAssistPackage.Log("call check: lookup failed for " + name + ": " + ex.Message);
                return null;
            }
        }
    }

    [Export(typeof(ITaggerProvider))]
    [ContentType("C/C++")]
    [TagType(typeof(IErrorTag))]
    internal sealed class CallCheckTaggerProvider : ITaggerProvider
    {
        [Import] internal ITextDocumentFactoryService Documents { get; set; }

        public ITagger<T> CreateTagger<T>(ITextBuffer buffer) where T : ITag
        {
            try { return CallCheckTagger.For(buffer, Documents) as ITagger<T>; }
            catch (Exception ex) { KCppAssistPackage.Log("call check attach failed: " + ex); return null; }
        }
    }

    /// <summary>エディターが開くたびに、キャレットの位置をタガーに教える(入力中の呼び出しに、「足りない」と言わないため)。</summary>
    [Export(typeof(IWpfTextViewCreationListener))]
    [ContentType("C/C++")]
    [TextViewRole(PredefinedTextViewRoles.Document)]
    internal sealed class CallCheckViewListener : IWpfTextViewCreationListener
    {
        [Import] internal ITextDocumentFactoryService Documents { get; set; }

        public void TextViewCreated(IWpfTextView view)
        {
            try { CallCheckTagger.For(view.TextBuffer, Documents).Attach(view); }
            catch (Exception ex) { KCppAssistPackage.Log("call check view attach failed: " + ex); }
        }
    }

    /// <summary>
    /// 1 つのファイルについて、std::make_unique&lt;T&gt;(…)・std::make_shared&lt;T&gt;(…)・new T(…) の引数の個数が合わない呼び出しに、
    /// ビルドの前に、エディター上で波線(赤、設定で緑)を引く。入力が止まってから調べる。
    /// </summary>
    internal sealed class CallCheckTagger : ITagger<IErrorTag>
    {
        private sealed class Item { public ITrackingSpan Span; public string Message; }

        private readonly ITextBuffer buffer;
        private readonly string path;
        private readonly object gate = new object();
        private List<Item> items = new List<Item>();
        private IWpfTextView view;
        private int gen;
        private bool suppressed;      // キャレットのために見送った指摘がある(キャレットが動いたら、もう一度調べる)

        public event EventHandler<SnapshotSpanEventArgs> TagsChanged;

        internal static CallCheckTagger For(ITextBuffer buffer, ITextDocumentFactoryService docs)
        {
            return buffer.Properties.GetOrCreateSingletonProperty(typeof(CallCheckTagger), () =>
            {
                ITextDocument doc;
                string p = docs != null && docs.TryGetTextDocument(buffer, out doc) ? doc.FilePath : null;
                return new CallCheckTagger(buffer, p);
            });
        }

        private CallCheckTagger(ITextBuffer buffer, string path)
        {
            this.buffer = buffer;
            this.path = path;
            buffer.Changed += OnChanged;
            CallCheckHub.Register(path, buffer, this);
            Schedule();
        }

        private static OptionsPage Opt { get { return IncludeService.Options; } }

        internal void Attach(IWpfTextView v)
        {
            if (view != null) return;
            view = v;
            v.Caret.PositionChanged += OnCaret;
            v.Closed += (s, e) => { v.Caret.PositionChanged -= OnCaret; if (view == v) view = null; };
        }

        private void OnCaret(object sender, CaretPositionChangedEventArgs e)
        {
            if (suppressed) Schedule();
        }

        private void OnChanged(object sender, TextContentChangedEventArgs e)
        {
            Schedule();
            if (path != null && IncludeService.IsHeader(path)) CallCheckHub.HeaderEdited(this);
        }

        /// <summary>少し待ってから、調べ直す(続けて呼ばれたら、最後の 1 回だけ)。</summary>
        internal void Schedule()
        {
            int my = System.Threading.Interlocked.Increment(ref gen);
            _ = ThreadHelper.JoinableTaskFactory.RunAsync(async () =>
            {
                try
                {
                    var o = Opt;
                    int ms = o == null ? 700 : Math.Max(200, o.CallCheckDelayMs);
                    await Task.Delay(ms);
                    if (my != gen) return;
                    await RunAsync(my);
                }
                catch (Exception ex) { KCppAssistPackage.Log("call check failed: " + ex); }
            });
        }

        private async Task RunAsync(int my)
        {
            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
            if (my != gen) return;
            var opt = Opt;
            if (opt == null || !opt.CallCheckEnabled || path == null) { Publish(null, null); return; }
            if (!(opt.CallCheckMake || opt.CallCheckNew)) { Publish(null, null); return; }

            ITextSnapshot snap = buffer.CurrentSnapshot;
            string text = snap.GetText();
            string root = IncludeService.RootFor(path);
            var skip = IncludeService.SkipDirs(opt);
            int caret = -1;
            try { if (view != null) caret = view.Caret.Position.BufferPosition.TranslateTo(snap, PointTrackingMode.Positive).Position; } catch (Exception) { }
            var o = new CallCheck.Options
            {
                Make = opt.CallCheckMake,
                New = opt.CallCheckNew,
                Caret = caret,
                Ignore = new HashSet<string>((opt.CallCheckIgnore ?? "").Split(new[] { ',', ';', ' ', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries)),
            };
            string errorType = opt.CallCheckSeverity == CallCheckSeverity.Error ? PredefinedErrorTypeNames.CompilerError : PredefinedErrorTypeNames.Warning;

            List<CallCheck.Finding> found = null;
            await Task.Run(() =>
            {
                IncludeService.Index.Refresh(root, skip, false);
                found = CallCheck.Check(text, (q, n) => CallCheckLookup.Find(path, text, q, n), o);
            });

            await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
            if (my != gen) return;
            suppressed = o.Suppressed;
            Publish(found, snap, errorType);
        }

        private string errorTypeNow = PredefinedErrorTypeNames.CompilerError;

        private void Publish(List<CallCheck.Finding> found, ITextSnapshot snap, string errorType = null)
        {
            var list = new List<Item>();
            if (found != null)
                foreach (var f in found)
                {
                    if (f.Start < 0 || f.Start + f.Length > snap.Length) continue;
                    list.Add(new Item { Span = snap.CreateTrackingSpan(f.Start, f.Length, SpanTrackingMode.EdgeExclusive), Message = f.Message });
                }
            bool changed;
            lock (gate)
            {
                changed = list.Count > 0 || items.Count > 0 || (errorType != null && errorType != errorTypeNow);
                items = list;
                if (errorType != null) errorTypeNow = errorType;
            }
            if (!changed) return;
            if (found != null && found.Count > 0) KCppAssistPackage.Log("call check: " + Path.GetFileName(path) + ": " + found.Count + " finding(s)");
            var cur = buffer.CurrentSnapshot;
            var h = TagsChanged;
            if (h != null) h(this, new SnapshotSpanEventArgs(new SnapshotSpan(cur, 0, cur.Length)));
        }

        public IEnumerable<ITagSpan<IErrorTag>> GetTags(NormalizedSnapshotSpanCollection spans)
        {
            List<Item> now;
            string type;
            lock (gate) { now = items; type = errorTypeNow; }
            if (now.Count == 0 || spans.Count == 0) yield break;
            ITextSnapshot snap = spans[0].Snapshot;
            foreach (var it in now)
            {
                SnapshotSpan sp = it.Span.GetSpan(snap);
                if (sp.IsEmpty) continue;
                if (!spans.IntersectsWith(sp)) continue;
                yield return new TagSpan<IErrorTag>(sp, new ErrorTag(type, it.Message));
            }
        }
    }
}
