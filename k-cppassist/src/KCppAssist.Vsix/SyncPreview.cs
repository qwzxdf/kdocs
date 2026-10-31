using System;
using System.Text.RegularExpressions;
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

namespace KCppAssist
{
    /// <summary>
    /// 引数を相手のファイルへ写したとき、書き換えた場所を、エディターの右上に小さなウィンドウで少しの間だけ見せる。
    /// フォーカスは奪わず、Visual Studio を持ち主にして出すので、ほかのアプリの上には出ない。
    /// </summary>
    internal static class SyncPreview
    {
        private static Window current;
        private static DispatcherTimer closeTimer;

        /// <param name="anchor">いま作業しているエディター。この右上に出す。</param>
        /// <param name="file">書き換えた相手のファイル名。</param>
        /// <param name="after">書き換えたあとの相手の文字。</param>
        /// <param name="open">相手の関数の「(」の位置。</param>
        /// <param name="newLength">書き換えたあとの括弧の中身の長さ。</param>
        /// <param name="oldInner">書き換える前の括弧の中身。</param>
        public static void Show(IWpfTextView anchor, string file, ITextSnapshot after, int open, int newLength, string oldInner)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var o = SyncService.Options;
            if (o == null || !o.ShowSyncPreview || anchor == null) return;
            try { ShowCore(anchor, file, after, open, newLength, oldInner); }
            catch (Exception ex) { KCppAssistPackage.Log("sync preview failed: " + ex.Message); }
        }

        private static void ShowCore(IWpfTextView anchor, string file, ITextSnapshot after, int open, int newLength, string oldInner)
        {
            Close();

            int first = after.GetLineNumberFromPosition(open);
            int last = after.GetLineNumberFromPosition(Math.Min(after.Length, open + 1 + newLength));
            int from = Math.Max(0, first - 1);
            int to = Math.Min(after.LineCount - 1, last + 1);

            var mono = new FontFamily("Consolas");
            var panel = new StackPanel { Margin = new Thickness(10, 8, 10, 8) };
            panel.Children.Add(new TextBlock
            {
                Text = file + " に写しました",
                FontWeight = FontWeights.SemiBold,
                Foreground = Brushes.White,
                Margin = new Thickness(0, 0, 0, 4),
            });
            panel.Children.Add(new TextBlock
            {
                Text = "前: (" + Collapse(oldInner) + ")",
                FontFamily = mono,
                FontSize = 12,
                Foreground = new SolidColorBrush(Color.FromRgb(0xB0, 0xB0, 0xB0)),
                TextDecorations = TextDecorations.Strikethrough,
                TextTrimming = TextTrimming.CharacterEllipsis,
                Margin = new Thickness(0, 0, 0, 2),
            });
            for (int i = from; i <= to; i++)
            {
                bool changed = i >= first && i <= last;
                panel.Children.Add(new TextBlock
                {
                    Text = after.GetLineFromLineNumber(i).GetText().Replace("\t", "    "),
                    FontFamily = mono,
                    FontSize = 12,
                    Foreground = changed ? Brushes.White : new SolidColorBrush(Color.FromRgb(0x9A, 0x9A, 0x9A)),
                    Background = changed ? new SolidColorBrush(Color.FromArgb(0x70, 0x2E, 0xA0, 0x43)) : Brushes.Transparent,
                    TextTrimming = TextTrimming.CharacterEllipsis,
                    Padding = new Thickness(2, 0, 2, 0),
                });
            }

            var win = new Window
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
                MaxWidth = 460,
                Content = new Border
                {
                    Background = new SolidColorBrush(Color.FromArgb(0xEE, 0x25, 0x25, 0x26)),
                    BorderBrush = new SolidColorBrush(Color.FromRgb(0x3F, 0x8F, 0xE0)),
                    BorderThickness = new Thickness(1),
                    CornerRadius = new CornerRadius(4),
                    Child = panel,
                },
            };

            // Visual Studio を持ち主にして、フォーカスを奪わずに出す
            var dte = (DTE)Package.GetGlobalService(typeof(DTE));
            if (dte != null) new WindowInteropHelper(win) { Owner = (IntPtr)dte.MainWindow.HWnd };

            // エディターの右上(余白 24)に置く。PointToScreen は画面のピクセル、Window.Left/Top はデバイス非依存の単位
            FrameworkElement el = anchor.VisualElement;
            Point px = el.PointToScreen(new Point(el.ActualWidth, 0));
            PresentationSource src = PresentationSource.FromVisual(el);
            Point dip = src != null ? src.CompositionTarget.TransformFromDevice.Transform(px) : px;
            win.Measure(new Size(460, double.PositiveInfinity));
            win.Left = Math.Max(0, dip.X - win.DesiredSize.Width - 24);
            win.Top = dip.Y + 8;

            current = win;
            win.Show();

            closeTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(2800) };
            closeTimer.Tick += (s, e) =>
            {
                closeTimer.Stop();
                var w = win;
                var fade = new DoubleAnimation(0, TimeSpan.FromMilliseconds(300));
                fade.Completed += (s2, e2) =>
                {
                    if (current == w) Close();
                    else { try { w.Close(); } catch (Exception) { } }
                };
                w.BeginAnimation(UIElement.OpacityProperty, fade);
            };
            closeTimer.Start();
        }

        private static string Collapse(string s)
        {
            return Regex.Replace(s ?? "", @"\s+", " ").Trim();
        }

        private static void Close()
        {
            if (closeTimer != null) { closeTimer.Stop(); closeTimer = null; }
            if (current != null) { try { current.Close(); } catch (Exception) { } current = null; }
        }
    }
}
