using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Threading;
using DTE = EnvDTE.DTE;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Text.Formatting;

namespace KCppAssist
{
    /// <summary>
    /// ほかの場所を書き換えたとき、何を変えたかを、小さなウィンドウで少しの間だけ見せる。
    /// ウィンドウは、変えた名前(関数の名前など)の 1 文字目に左端をそろえて、その行のすぐ上に出す。名前には重ねない。
    /// フォーカスは奪わず、Visual Studio を持ち主にして出すので、ほかのアプリの上には出ない。
    /// </summary>
    internal static class SyncPreview
    {
        private const double MaxWidth = 460;
        private static Window current;
        private static Border currentBorder;
        private static DispatcherTimer closeTimer;
        private static int generation;

        private static readonly Color Red = Color.FromArgb(0x70, 0xB0, 0x3A, 0x3A);
        private static readonly Color Green = Color.FromArgb(0x70, 0x2E, 0xA0, 0x43);

        /// <summary>引数を相手のファイルへ写したことを、前(赤)とあと(緑)の行で見せる。</summary>
        /// <param name="anchor">いま作業しているエディター。</param>
        /// <param name="anchorPos">anchor の中の、変えた関数の名前の頭の位置。この真上に出す。分からなければ -1(キャレットの行)。</param>
        /// <param name="file">書き換えた相手のファイル名。</param>
        /// <param name="after">書き換えたあとの相手の文字。</param>
        /// <param name="open">相手の関数の「(」の位置。</param>
        /// <param name="newLength">書き換えたあとの括弧の中身の長さ。</param>
        /// <param name="oldInner">書き換える前の括弧の中身。</param>
        public static void Show(IWpfTextView anchor, int anchorPos, string file, ITextSnapshot after, int open, int newLength, string oldInner)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var o = SyncService.Options;
            if (o == null || !o.ShowSyncPreview || anchor == null) return;
            try
            {
                int first = after.GetLineNumberFromPosition(open);
                int last = after.GetLineNumberFromPosition(Math.Min(after.Length, open + 1 + newLength));
                // 書き換える前の行と、あとの行を、並べて見せる(前の行は、あとの行の括弧の中身を、前の中身に戻して作る)
                int blockStart = after.GetLineFromLineNumber(first).Start.Position;
                int blockEnd = after.GetLineFromLineNumber(last).End.Position;
                string block = after.GetText(blockStart, blockEnd - blockStart);
                int innerAt = Math.Max(0, Math.Min(block.Length, open + 1 - blockStart));
                int innerLen = Math.Max(0, Math.Min(block.Length - innerAt, newLength));
                string oldBlock = block.Substring(0, innerAt) + oldInner + block.Substring(innerAt + innerLen);

                var panel = Panel(file + " に写しました");
                AddCode(panel, oldBlock, Red);
                AddCode(panel, block, Green);
                Present(anchor, anchorPos, panel);
            }
            catch (Exception ex) { KCppAssistPackage.Log("sync preview failed: " + ex.Message); }
        }

        /// <summary>題と、その下の何行かの説明を見せる(名前を変えた、呼び出しの引数を並べ替えた、など)。</summary>
        /// <param name="before">赤で見せる 1 行(変える前)。なければ null。</param>
        /// <param name="after">緑で見せる 1 行(変えたあと)。なければ null。</param>
        public static void ShowNote(IWpfTextView anchor, int anchorPos, string title, string before, string after, IEnumerable<string> lines)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var o = SyncService.Options;
            if (o == null || !o.ShowSyncPreview || anchor == null || anchor.IsClosed) return;
            try
            {
                var panel = Panel(title);
                if (before != null) AddCode(panel, before, Red);
                if (after != null) AddCode(panel, after, Green);
                if (lines != null)
                    foreach (string ln in lines)
                        panel.Children.Add(new TextBlock
                        {
                            Text = ln,
                            FontSize = 12,
                            Foreground = new SolidColorBrush(Color.FromRgb(0xD0, 0xD0, 0xD0)),
                            TextTrimming = TextTrimming.CharacterEllipsis,
                            Margin = new Thickness(0, 2, 0, 0),
                        });
                Present(anchor, anchorPos, panel);
            }
            catch (Exception ex) { KCppAssistPackage.Log("sync note failed: " + ex.Message); }
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

        private static StackPanel Panel(string title)
        {
            var panel = new StackPanel { Margin = new Thickness(10, 8, 10, 8) };
            panel.Children.Add(new TextBlock
            {
                Text = title,
                FontWeight = FontWeights.SemiBold,
                Foreground = Brushes.White,
                TextTrimming = TextTrimming.CharacterEllipsis,
                Margin = new Thickness(0, 0, 0, 4),
            });
            return panel;
        }

        private static void AddCode(StackPanel panel, string code, Color bg)
        {
            var mono = new FontFamily("Consolas");
            foreach (string ln in code.Replace("\r", "").Split('\n'))
                panel.Children.Add(new TextBlock
                {
                    Text = ln.Replace("\t", "    "),
                    FontFamily = mono,
                    FontSize = 12,
                    Foreground = Brushes.White,
                    Background = new SolidColorBrush(bg),
                    TextTrimming = TextTrimming.CharacterEllipsis,
                    Padding = new Thickness(2, 0, 2, 0),
                });
        }

        /// <summary>panel を小さなウィンドウに入れて出す。もう出ていれば、中身を入れ替えて、置き直す(打つたびに作り直すと、ちらつく)。</summary>
        private static void Present(IWpfTextView anchor, int anchorPos, StackPanel panel)
        {
            if (current == null)
            {
                currentBorder = new Border
                {
                    Background = new SolidColorBrush(Color.FromArgb(0xEE, 0x25, 0x25, 0x26)),
                    BorderBrush = new SolidColorBrush(Color.FromRgb(0x3F, 0x8F, 0xE0)),
                    BorderThickness = new Thickness(1),
                    CornerRadius = new CornerRadius(4),
                    MaxWidth = MaxWidth,
                };
                current = new Window
                {
                    WindowStyle = WindowStyle.None,
                    ResizeMode = ResizeMode.NoResize,
                    AllowsTransparency = true,
                    Background = Brushes.Transparent,
                    ShowInTaskbar = false,
                    ShowActivated = false,
                    Focusable = false,
                    IsHitTestVisible = false,
                    SizeToContent = SizeToContent.WidthAndHeight,
                    MaxWidth = MaxWidth,
                    Content = currentBorder,
                };
                // Visual Studio を持ち主にして、フォーカスを奪わずに出す
                var dte = (DTE)Package.GetGlobalService(typeof(DTE));
                if (dte != null) new WindowInteropHelper(current) { Owner = (IntPtr)dte.MainWindow.HWnd };
            }
            Window win = current;
            win.BeginAnimation(UIElement.OpacityProperty, null);     // 消えかけていたら、戻す
            win.Opacity = 1;
            currentBorder.Child = panel;
            currentBorder.Measure(new Size(MaxWidth, double.PositiveInfinity));
            Place(win, anchor, anchorPos, currentBorder.DesiredSize.Width, currentBorder.DesiredSize.Height);
            if (!win.IsVisible) win.Show();

            int gen = ++generation;
            if (closeTimer != null) closeTimer.Stop();
            closeTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(2800) };
            closeTimer.Tick += (s, e) =>
            {
                ((DispatcherTimer)s).Stop();
                if (gen != generation || current != win) return;
                var fade = new DoubleAnimation(0, TimeSpan.FromMilliseconds(300));
                fade.Completed += (s2, e2) => { if (gen == generation && current == win) Close(); };
                win.BeginAnimation(UIElement.OpacityProperty, fade);
            };
            closeTimer.Start();
        }

        /// <summary>
        /// ウィンドウを、anchorPos の文字の真上に置く(左端を、その文字の左端にそろえる)。上に収まらなければ、その行のすぐ下に置く。
        /// どちらでも、その行には重ならない。PointToScreen は画面のピクセル、Window.Left/Top はデバイス非依存の単位なので、変換する。
        /// </summary>
        private static void Place(Window win, IWpfTextView anchor, int anchorPos, double w, double h)
        {
            FrameworkElement el = anchor.VisualElement;
            PresentationSource src = PresentationSource.FromVisual(el);
            Func<Point, Point> toDip = pt => src != null ? src.CompositionTarget.TransformFromDevice.Transform(pt) : pt;
            Point topLeft = toDip(el.PointToScreen(new Point(0, 0)));
            Point bottomRight = toDip(el.PointToScreen(new Point(el.ActualWidth, el.ActualHeight)));

            double left = bottomRight.X - w - 24, top = topLeft.Y + 8;     // 行が見えていないときは、右上
            try
            {
                ITextSnapshot snap = anchor.TextSnapshot;
                SnapshotPoint caret = anchor.Caret.Position.BufferPosition;
                SnapshotPoint pt = anchorPos >= 0 && anchorPos < snap.Length ? new SnapshotPoint(snap, anchorPos) : caret;
                ITextViewLine line = VisibleLine(anchor, pt);
                if (line == null && pt != caret) { pt = caret; line = VisibleLine(anchor, pt); }
                if (line != null)
                {
                    TextBounds tb = line.GetCharacterBounds(pt);
                    Point above = toDip(el.PointToScreen(new Point(tb.Left - anchor.ViewportLeft, line.Top - anchor.ViewportTop)));
                    Point below = toDip(el.PointToScreen(new Point(tb.Left - anchor.ViewportLeft, line.Bottom - anchor.ViewportTop)));
                    left = above.X;
                    top = above.Y - h - 3;
                    if (top < topLeft.Y) top = below.Y + 3;
                }
            }
            catch (Exception) { }
            win.Left = Math.Max(topLeft.X + 4, Math.Min(left, bottomRight.X - w - 8));
            win.Top = Math.Max(topLeft.Y, Math.Min(top, bottomRight.Y - h));
        }

        private static ITextViewLine VisibleLine(IWpfTextView view, SnapshotPoint pt)
        {
            ITextViewLine line = view.TextViewLines == null ? null : view.TextViewLines.GetTextViewLineContainingBufferPosition(pt);
            if (line == null || line.VisibilityState == VisibilityState.Hidden || line.VisibilityState == VisibilityState.Unattached) return null;
            return line;
        }

        private static void Close()
        {
            if (closeTimer != null) { closeTimer.Stop(); closeTimer = null; }
            if (current != null) { try { current.Close(); } catch (Exception) { } current = null; currentBorder = null; }
        }
    }
}
