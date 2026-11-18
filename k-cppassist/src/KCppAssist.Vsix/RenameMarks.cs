using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.Linq;
using System.Windows.Media;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Classification;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Text.Tagging;
using Microsoft.VisualStudio.Utilities;

namespace KCppAssist
{
    /// <summary>
    /// 名前を変えている間、一緒に変わる場所を枠で囲む(C# の名前の変更と同じ見え方)。
    /// 打っている宣言の名前は実線、一緒に変わる場所は点線。名前の変更が終わると消える。
    /// どのファイルの、どこを囲むかは SymbolSyncSession が Set / Clear で渡す。
    /// </summary>
    internal static class RenameMarks
    {
        public const string DeclFormat = "K-CppAssist Rename Declaration";
        public const string RefFormat = "K-CppAssist Rename Reference";

        private sealed class Entry
        {
            public ITextBuffer Buffer;
            public ITrackingSpan Span;
            public bool Decl;
        }

        private static readonly object gate = new object();
        private static readonly Dictionary<object, List<Entry>> byOwner = new Dictionary<object, List<Entry>>();

        /// <summary>囲む場所が変わったバッファー。タガーが、描き直しを頼む。</summary>
        public static event Action<ITextBuffer> Changed;

        /// <summary>owner(名前の変更 1 回)の囲む場所を、まとめて入れ替える。</summary>
        public static void Set(object owner, ITextBuffer declBuffer, ITrackingSpan decl, IEnumerable<KeyValuePair<ITextBuffer, ITrackingSpan>> refs)
        {
            var list = new List<Entry>();
            if (decl != null) list.Add(new Entry { Buffer = declBuffer, Span = decl, Decl = true });
            foreach (var r in refs) list.Add(new Entry { Buffer = r.Key, Span = r.Value });
            List<Entry> old;
            lock (gate)
            {
                byOwner.TryGetValue(owner, out old);
                byOwner[owner] = list;
            }
            Raise(list.Concat(old ?? new List<Entry>()));
        }

        public static void Clear(object owner)
        {
            List<Entry> old;
            lock (gate)
            {
                if (!byOwner.TryGetValue(owner, out old)) return;
                byOwner.Remove(owner);
            }
            Raise(old);
        }

        public static List<KeyValuePair<SnapshotSpan, bool>> For(ITextSnapshot snap)
        {
            var result = new List<KeyValuePair<SnapshotSpan, bool>>();
            lock (gate)
            {
                foreach (var list in byOwner.Values)
                    foreach (var e in list)
                    {
                        if (e.Buffer != snap.TextBuffer) continue;
                        try
                        {
                            SnapshotSpan sp = e.Span.GetSpan(snap);
                            if (sp.Length > 0) result.Add(new KeyValuePair<SnapshotSpan, bool>(sp, e.Decl));
                        }
                        catch (Exception) { }      // 古い版の範囲(元に戻したあとなど)は描かない
                    }
            }
            return result;
        }

        private static void Raise(IEnumerable<Entry> entries)
        {
            var h = Changed;
            if (h == null) return;
            foreach (var b in entries.Select(e => e.Buffer).Distinct())
            {
                try { h(b); } catch (Exception ex) { KCppAssistPackage.Log("rename marks raise failed: " + ex.Message); }
            }
        }
    }

    [Export(typeof(EditorFormatDefinition))]
    [Name(RenameMarks.DeclFormat)]
    [UserVisible(true)]
    internal sealed class RenameDeclFormat : MarkerFormatDefinition
    {
        public RenameDeclFormat()
        {
            DisplayName = "K-CppAssist: 名前を変えている宣言";
            var pen = new Pen(new SolidColorBrush(Color.FromRgb(0x4A, 0x9E, 0xE8)), 1.2);
            pen.Freeze();
            Border = pen;
            Fill = new SolidColorBrush(Color.FromArgb(0x22, 0x4A, 0x9E, 0xE8));
            Fill.Freeze();
            ZOrder = 5;
        }
    }

    [Export(typeof(EditorFormatDefinition))]
    [Name(RenameMarks.RefFormat)]
    [UserVisible(true)]
    internal sealed class RenameRefFormat : MarkerFormatDefinition
    {
        public RenameRefFormat()
        {
            DisplayName = "K-CppAssist: 一緒に変わる場所";
            // 点線。明るい背景でも暗い背景でも見える青
            var pen = new Pen(new SolidColorBrush(Color.FromRgb(0x4A, 0x9E, 0xE8)), 1.0) { DashStyle = new DashStyle(new double[] { 2, 2 }, 0) };
            pen.Freeze();
            Border = pen;
            ZOrder = 5;
        }
    }

    [Export(typeof(IViewTaggerProvider))]
    [ContentType("C/C++")]
    [TagType(typeof(TextMarkerTag))]
    internal sealed class RenameMarkTaggerProvider : IViewTaggerProvider
    {
        public ITagger<T> CreateTagger<T>(ITextView textView, ITextBuffer buffer) where T : ITag
        {
            if (textView == null || buffer == null || textView.TextBuffer != buffer) return null;
            // ビューごとに作り、ビューを閉じたら static のイベントから外す(外さないと、閉じたファイルのバッファーが残り続ける)
            var tagger = new RenameMarkTagger(buffer);
            textView.Closed += (s, e) => tagger.Detach();
            return tagger as ITagger<T>;
        }
    }

    internal sealed class RenameMarkTagger : ITagger<TextMarkerTag>
    {
        private static readonly TextMarkerTag DeclTag = new TextMarkerTag(RenameMarks.DeclFormat);
        private static readonly TextMarkerTag RefTag = new TextMarkerTag(RenameMarks.RefFormat);
        private readonly ITextBuffer buffer;

        public RenameMarkTagger(ITextBuffer buffer)
        {
            this.buffer = buffer;
            RenameMarks.Changed += OnMarksChanged;
        }

        public event EventHandler<SnapshotSpanEventArgs> TagsChanged;

        public void Detach() { RenameMarks.Changed -= OnMarksChanged; }

        private void OnMarksChanged(ITextBuffer b)
        {
            if (b != buffer) return;
            var snap = buffer.CurrentSnapshot;
            TagsChanged?.Invoke(this, new SnapshotSpanEventArgs(new SnapshotSpan(snap, 0, snap.Length)));
        }

        public IEnumerable<ITagSpan<TextMarkerTag>> GetTags(NormalizedSnapshotSpanCollection spans)
        {
            if (spans.Count == 0) yield break;
            var snap = spans[0].Snapshot;
            foreach (var m in RenameMarks.For(snap))
                if (spans.IntersectsWith(new NormalizedSnapshotSpanCollection(m.Key)))
                    yield return new TagSpan<TextMarkerTag>(m.Key, m.Value ? DeclTag : RefTag);
        }
    }
}
