using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.Linq;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Shapes;
using System.Windows.Threading;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Utilities;

namespace KCppAssist
{
    /// <summary>点線を描く層(テキストの上)の定義。</summary>
    internal sealed class ChangeMarkLayer
    {
        public const string Name = "KCppAssistChange";

        [Export(typeof(AdornmentLayerDefinition))]
        [Name(Name)]
        [Order(After = PredefinedAdornmentLayers.Text)]
        internal AdornmentLayerDefinition Definition = null;
    }

    /// <summary>
    /// ほかの場所を書き換えたとき(引数を相手のファイルへ写した、名前を変えた、呼び出しの引数を直した)、書き換えた名前の下に、
    /// 点線を少しの間だけ出す。C# の名前の変更と同じ見せかたで、ウィンドウは出さない(下や上のコードを隠さない)。
    /// 点線は、いま開いているエディターの中の、変えた名前だけに出る。ほかのファイルの変更は、点線では見えない。
    /// </summary>
    internal static class SyncPreview
    {
        private static readonly Brush LineBrush = Freeze(new SolidColorBrush(Color.FromRgb(0x3F, 0x8F, 0xE0)));
        private static DispatcherTimer closeTimer;
        private static IWpfTextView markedView;
        private static int generation;

        private static Brush Freeze(SolidColorBrush b) { b.Freeze(); return b; }

        /// <summary>引数を相手のファイルへ写したとき。変えた関数の名前(anchorPos)に、点線を出す。残りの引数は、点線を出す場所の目印だけに使う。</summary>
        public static void Show(IWpfTextView anchor, int anchorPos, string file, ITextSnapshot after, int open, int newLength, string oldInner)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var o = SyncService.Options;
            if (o == null || !o.ShowSyncPreview || anchor == null || anchor.IsClosed) return;
            var spans = new List<SnapshotSpan>();
            SnapshotSpan? name = NameSpan(anchor.TextSnapshot, anchorPos >= 0 ? anchorPos : anchor.Caret.Position.BufferPosition.Position);
            if (name.HasValue) spans.Add(name.Value);
            Mark(anchor, spans);
        }

        /// <summary>名前を変えた・呼び出しを直したとき。spans(開いているエディターの中の、変えた場所)と、anchorPos の名前に、点線を出す。</summary>
        public static void ShowNote(IWpfTextView anchor, int anchorPos, string title, string before, string after, IEnumerable<string> lines, bool hold = false, IEnumerable<SnapshotSpan> spans = null)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var o = SyncService.Options;
            if (o == null || !o.ShowSyncPreview || anchor == null || anchor.IsClosed) return;
            var all = new List<SnapshotSpan>();
            if (spans != null) all.AddRange(spans);
            if (anchorPos >= 0)
            {
                SnapshotSpan? name = NameSpan(anchor.TextSnapshot, anchorPos);
                if (name.HasValue && !all.Any(s => s.Start == name.Value.Start)) all.Add(name.Value);
            }
            Mark(anchor, all);
        }

        /// <summary>snap の「(」の位置 open の左にある、関数の名前の頭の位置。</summary>
        public static int NameStart(ITextSnapshot snap, int open)
        {
            int e = Math.Max(0, Math.Min(open, snap.Length));
            while (e > 0 && char.IsWhiteSpace(snap[e - 1])) e--;
            int s = e;
            while (s > 0 && CppText.IsId(snap[s - 1])) s--;
            return s;
        }

        /// <summary>pos から始まる識別子の範囲。識別子でなければ null。</summary>
        private static SnapshotSpan? NameSpan(ITextSnapshot snap, int pos)
        {
            if (pos < 0 || pos >= snap.Length) return null;
            int s = pos;
            while (s > 0 && CppText.IsId(snap[s - 1])) s--;
            int e = pos;
            while (e < snap.Length && CppText.IsId(snap[e])) e++;
            return e > s ? new SnapshotSpan(snap, s, e - s) : (SnapshotSpan?)null;
        }

        /// <summary>spans の下に、点線を引く。前の点線は消す。約 3 秒で薄くなって消える。</summary>
        private static void Mark(IWpfTextView view, IEnumerable<SnapshotSpan> spans)
        {
            try
            {
                Clear();
                IAdornmentLayer layer = view.GetAdornmentLayer(ChangeMarkLayer.Name);
                int count = 0;
                foreach (SnapshotSpan span in spans)
                {
                    SnapshotSpan s = span.TranslateTo(view.TextSnapshot, SpanTrackingMode.EdgeInclusive);
                    if (s.IsEmpty) continue;
                    Geometry g = view.TextViewLines.GetMarkerGeometry(s);
                    if (g == null) continue;                                    // 画面に見えていない行
                    Rect r = g.Bounds;
                    var line = new Line
                    {
                        X1 = r.Left, X2 = r.Right, Y1 = r.Bottom - 1, Y2 = r.Bottom - 1,
                        Stroke = LineBrush,
                        StrokeThickness = 1.5,
                        StrokeDashArray = new DoubleCollection { 1, 2 },        // 点線(点 1 : すき間 2)
                        StrokeDashCap = PenLineCap.Round,
                        IsHitTestVisible = false,
                    };
                    layer.AddAdornment(AdornmentPositioningBehavior.TextRelative, s, null, line, null);
                    count++;
                }
                if (count == 0) return;
                markedView = view;
                int gen = ++generation;
                closeTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(2800) };
                closeTimer.Tick += (sender, e) =>
                {
                    ((DispatcherTimer)sender).Stop();
                    if (gen != generation) return;
                    Clear();
                };
                closeTimer.Start();
            }
            catch (Exception ex) { KCppAssistPackage.Log("sync mark failed: " + ex.Message); }
        }

        private static void Clear()
        {
            if (closeTimer != null) { closeTimer.Stop(); closeTimer = null; }
            IWpfTextView v = markedView;
            markedView = null;
            if (v == null || v.IsClosed) return;
            try { v.GetAdornmentLayer(ChangeMarkLayer.Name).RemoveAllAdornments(); } catch (Exception swallowed) { Safe.Ignore(swallowed); }
        }
    }
}
