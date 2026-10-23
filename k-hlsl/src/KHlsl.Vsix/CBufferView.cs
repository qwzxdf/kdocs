using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using Rectangle = System.Windows.Shapes.Rectangle;
using EnvDTE;
using EnvDTE80;
using Microsoft.VisualStudio.PlatformUI;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Microsoft.VisualStudio.TextManager.Interop;
using Newtonsoft.Json.Linq;

namespace KHlsl.Vsix
{
    /// <summary>
    /// 定数バッファのレイアウトを、16 バイトのレジスタ × 4 バイトの升目で見せる。
    /// メンバーごとに色を変え、隙間は斜線の灰色で示す。区画をダブルクリックすると、宣言の行へ飛ぶ。
    /// </summary>
    public sealed class CBufferView : UserControl
    {
        private const double ByteW = 24;      // 1 バイトの幅(16 バイトで 384 px)
        private const double RowH = 30;
        private const double LabelW = 92;

        // 明るい中間色。文字は黒で、ライト/ダークの両方で読める
        private static readonly Color[] Palette =
        {
            Color.FromRgb(0x8E, 0xB8, 0xF5), Color.FromRgb(0xF2, 0xB8, 0x7C), Color.FromRgb(0x9C, 0xD6, 0x9C), Color.FromRgb(0xE0, 0x9C, 0xD6),
            Color.FromRgb(0xE8, 0xD8, 0x6E), Color.FromRgb(0x7F, 0xD0, 0xD0), Color.FromRgb(0xF0, 0xA0, 0xA0), Color.FromRgb(0xB8, 0xA8, 0xE8),
            Color.FromRgb(0xC8, 0xC8, 0x8A), Color.FromRgb(0x9F, 0xC8, 0xB0)
        };

        private readonly ComboBox _blocks = new ComboBox { MinWidth = 260, Margin = new Thickness(0, 0, 8, 0) };
        private readonly CheckBox _structs = new CheckBox { Content = "struct も表示", Margin = new Thickness(0, 0, 8, 0), VerticalAlignment = VerticalAlignment.Center };
        private readonly TextBlock _file = new TextBlock { VerticalAlignment = VerticalAlignment.Center };
        private readonly TextBlock _summary = new TextBlock { Margin = new Thickness(8, 4, 8, 4), TextWrapping = TextWrapping.Wrap };
        private readonly Canvas _canvas = new Canvas();
        private readonly TextBox _reorderBox = MakeCodeBox();
        private readonly TextBox _cppBox = MakeCodeBox();
        private readonly TextBlock _reorderNote = new TextBlock { Margin = new Thickness(6, 4, 6, 4), TextWrapping = TextWrapping.Wrap };

        private IServiceProvider _services;
        private string _path;
        private JArray _data = new JArray();
        private bool _loading;

        public CBufferView()
        {
            SetResourceReference(BackgroundProperty, EnvironmentColors.ToolWindowBackgroundBrushKey);
            SetResourceReference(ForegroundProperty, EnvironmentColors.ToolWindowTextBrushKey);

            var bar = new DockPanel { Margin = new Thickness(6, 4, 6, 4), LastChildFill = true };
            var refresh = new Button { Content = "読み直す", Padding = new Thickness(10, 2, 10, 2), Margin = new Thickness(0, 0, 8, 0) };
            refresh.Click += (s, e) => Reload(true);
            _blocks.SelectionChanged += (s, e) => ShowSelected();
            _structs.Click += (s, e) => Reload(false);
            foreach (var t in new FrameworkElement[] { _structs, _file })
                if (t is CheckBox cb) cb.SetResourceReference(Control.ForegroundProperty, EnvironmentColors.ToolWindowTextBrushKey);
                else if (t is TextBlock tb) tb.SetResourceReference(TextBlock.ForegroundProperty, EnvironmentColors.ToolWindowTextBrushKey);
            DockPanel.SetDock(_blocks, Dock.Left);
            DockPanel.SetDock(refresh, Dock.Left);
            DockPanel.SetDock(_structs, Dock.Left);
            bar.Children.Add(_blocks);
            bar.Children.Add(refresh);
            bar.Children.Add(_structs);
            bar.Children.Add(_file);

            _summary.SetResourceReference(TextBlock.ForegroundProperty, EnvironmentColors.ToolWindowTextBrushKey);
            _reorderNote.SetResourceReference(TextBlock.ForegroundProperty, EnvironmentColors.ToolWindowTextBrushKey);

            var gridScroll = new ScrollViewer
            {
                Content = _canvas,
                HorizontalScrollBarVisibility = ScrollBarVisibility.Auto,
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto
            };

            var reorderPanel = new DockPanel();
            DockPanel.SetDock(_reorderNote, Dock.Top);
            reorderPanel.Children.Add(_reorderNote);
            reorderPanel.Children.Add(_reorderBox);

            var tabs = new TabControl { MinHeight = 150 };
            tabs.Items.Add(new TabItem { Header = "並べ替えの提案(HLSL)", Content = WithCopy(reorderPanel, _reorderBox) });
            tabs.Items.Add(new TabItem { Header = "C++ の struct", Content = WithCopy(_cppBox, _cppBox) });

            var grid = new Grid();
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(3, GridUnitType.Star) });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(2, GridUnitType.Star) });
            var splitter = new GridSplitter { Height = 4, HorizontalAlignment = HorizontalAlignment.Stretch, Background = Brushes.Gray };
            Grid.SetRow(bar, 0);
            Grid.SetRow(_summary, 1);
            Grid.SetRow(gridScroll, 2);
            Grid.SetRow(splitter, 3);
            Grid.SetRow(tabs, 4);
            grid.Children.Add(bar);
            grid.Children.Add(_summary);
            grid.Children.Add(gridScroll);
            grid.Children.Add(splitter);
            grid.Children.Add(tabs);
            Content = grid;

            IsVisibleChanged += (s, e) => { if (IsVisible) Reload(false); };
        }

        private static TextBox MakeCodeBox()
        {
            var tb = new TextBox
            {
                IsReadOnly = true,
                FontFamily = new FontFamily("Consolas"),
                FontSize = 12,
                AcceptsReturn = true,
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
                HorizontalScrollBarVisibility = ScrollBarVisibility.Auto,
                BorderThickness = new Thickness(0)
            };
            tb.SetResourceReference(Control.BackgroundProperty, EnvironmentColors.ToolWindowBackgroundBrushKey);
            tb.SetResourceReference(Control.ForegroundProperty, EnvironmentColors.ToolWindowTextBrushKey);
            return tb;
        }

        private static UIElement WithCopy(UIElement content, TextBox source)
        {
            var dock = new DockPanel();
            var copy = new Button { Content = "コピー", Padding = new Thickness(10, 2, 10, 2), Margin = new Thickness(4), HorizontalAlignment = HorizontalAlignment.Left };
            copy.Click += (s, e) =>
            {
                try { if (source.Text.Length > 0) Clipboard.SetText(source.Text); } catch (Exception) { }
            };
            DockPanel.SetDock(copy, Dock.Bottom);
            dock.Children.Add(copy);
            dock.Children.Add(content);
            return dock;
        }

        public void Initialize(IServiceProvider services)
        {
            _services = services;
            Reload(false);
        }

        // ---- 読み込み ----

        /// <summary>いま開いている HLSL ファイルを調べて、サーバーに問い合わせる。</summary>
        public void Reload(bool force)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            if (_loading) return;
            string path = ActiveHlslPath() ?? _path;
            if (path == null)
            {
                _summary.Text = "HLSL のファイル(.hlsl / .hlsli など)を開いてください。";
                return;
            }
            _path = path;
            _file.Text = Path.GetFileName(path);
            _loading = true;
            bool structs = _structs.IsChecked == true;
            ThreadHelper.JoinableTaskFactory.RunAsync(async () =>
            {
                JToken result = null;
                string error = null;
                try { result = await KHlslLanguageClient.RequestCBuffersAsync(path, structs); }
                catch (Exception ex) { error = ex.Message; }
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                _loading = false;
                if (result == null)
                {
                    _summary.Text = error != null ? "言語サーバーに問い合わせられませんでした: " + error
                        : "言語サーバーがまだ起動していません。HLSL のファイルを開いて、少し待ってから「読み直す」を押してください。";
                    return;
                }
                _data = result["blocks"] as JArray ?? new JArray();
                string keep = (_blocks.SelectedItem as ComboBoxItem)?.Tag as string;
                _blocks.Items.Clear();
                foreach (JObject b in _data)
                {
                    var item = new ComboBoxItem
                    {
                        Content = (string)b["title"] + "  —  " + (int)b["size"] + " バイト",
                        Tag = (string)b["title"]
                    };
                    _blocks.Items.Add(item);
                    if (keep != null && keep == (string)b["title"]) _blocks.SelectedItem = item;
                }
                if (_blocks.SelectedItem == null && _blocks.Items.Count > 0) _blocks.SelectedIndex = 0;
                if (_blocks.Items.Count == 0)
                {
                    _canvas.Children.Clear();
                    _summary.Text = "このファイルには、cbuffer・ConstantBuffer<T> がありません。「struct も表示」で、struct のレイアウトも見られます。";
                    _reorderBox.Text = _cppBox.Text = "";
                    _reorderNote.Text = "";
                }
            });
        }

        private string ActiveHlslPath()
        {
            try
            {
                var dte = Package.GetGlobalService(typeof(DTE)) as DTE2;
                var doc = dte?.ActiveDocument;
                if (doc != null && KHlslContentType.Extensions.Contains(Path.GetExtension(doc.FullName))) return doc.FullName;
            }
            catch (Exception) { }
            return null;
        }

        // ---- 描画 ----

        private void ShowSelected()
        {
            int i = _blocks.SelectedIndex;
            if (i < 0 || i >= _data.Count) return;
            var b = (JObject)_data[i];
            int size = (int)b["size"], padded = (int)b["paddedSize"], wasted = (int)b["wasted"];
            double pct = padded == 0 ? 0 : 100.0 * wasted / padded;
            string s = (string)b["title"] + "  :  " + size + " バイト(確保は 16 の倍数で " + padded + " バイト・" + padded / 16 + " レジスタ)  /  隙間 " + wasted + " バイト(" + pct.ToString("0") + "%)";
            if (((JArray)b["problems"]).Count > 0) s += "\n⚠ " + string.Join(" / ", ((JArray)b["problems"]).Select(x => (string)x));
            _summary.Text = s;

            Draw(b);

            var r = b["reorder"] as JObject;
            if (r != null)
            {
                _reorderNote.Text = "メンバーの順番を入れ替えると、" + (int)r["size"] + " バイトになります(" + (int)r["saved"] + " バイト減)。C++ 側の struct も、同じ順に直してください。";
                _reorderBox.Text = (string)r["hlsl"];
            }
            else
            {
                _reorderNote.Text = (bool)b["incomplete"] ? "計算できなかったので、提案を出せません。" : "これ以上は、入れ替えても小さくなりません(または packoffset を使っています)。";
                _reorderBox.Text = "";
            }
            _cppBox.Text = (string)b["cpp"];
        }

        private void Draw(JObject b)
        {
            _canvas.Children.Clear();
            int padded = Math.Max((int)b["paddedSize"], 16);
            int rows = padded / 16;
            var members = (JArray)b["members"];
            double width = LabelW + 16 * ByteW + 10;
            _canvas.Width = width;
            _canvas.Height = rows * RowH + 24;

            // 見出しの行(+0 +4 +8 +12)
            for (int c = 0; c < 4; c++)
                AddText("+" + c * 4, LabelW + c * 4 * ByteW + 4, 2, Brushes.Gray, 10);

            // 行のラベルと、薄い下地(隙間)
            for (int r = 0; r < rows; r++)
            {
                double y = 20 + r * RowH;
                AddText("c" + r + "  (" + r * 16 + ")", 2, y + 6, null, 11);
                var bg = new Rectangle
                {
                    Width = 16 * ByteW, Height = RowH - 2,
                    Fill = new SolidColorBrush(Color.FromArgb(40, 128, 128, 128)),
                    Stroke = new SolidColorBrush(Color.FromArgb(70, 128, 128, 128)),
                    StrokeThickness = 1
                };
                Canvas.SetLeft(bg, LabelW);
                Canvas.SetTop(bg, y);
                _canvas.Children.Add(bg);
            }

            // 隙間の斜線は、使われていないバイトに重ねる
            var used = new bool[rows * 16];
            foreach (JObject s in (JArray)b["segments"])
                for (int k = (int)s["offset"]; k < (int)s["offset"] + (int)s["size"] && k < used.Length; k++) used[k] = true;
            for (int k = 0; k < used.Length; )
            {
                if (used[k]) { k++; continue; }
                int start = k;
                while (k < used.Length && !used[k] && k / 16 == start / 16) k++;
                var gap = new Rectangle
                {
                    Width = (k - start) * ByteW, Height = RowH - 2,
                    Fill = HatchBrush(),
                    ToolTip = "隙間 " + (k - start) + " バイト(オフセット " + start + ")"
                };
                Canvas.SetLeft(gap, LabelW + start % 16 * ByteW);
                Canvas.SetTop(gap, 20 + start / 16 * RowH);
                _canvas.Children.Add(gap);
            }

            // メンバーの区画
            foreach (JObject s in (JArray)b["segments"])
            {
                int off = (int)s["offset"], size = (int)s["size"], group = (int)s["group"];
                string path = (string)s["path"];
                Color col = Palette[group % Palette.Length];
                int pos = off;
                bool first = true;
                while (pos < off + size)
                {
                    int rowEnd = (pos / 16 + 1) * 16;
                    int end = Math.Min(off + size, rowEnd);
                    var rect = new Rectangle
                    {
                        Width = (end - pos) * ByteW - 1, Height = RowH - 2,
                        Fill = new SolidColorBrush(col),
                        Stroke = new SolidColorBrush(Color.FromRgb(0x55, 0x55, 0x55)),
                        StrokeThickness = 0.5,
                        ToolTip = path + " : " + (string)s["type"] + "\nオフセット " + off + " ・ サイズ " + size + " バイト\nレジスタ c" + off / 16 + "." + "xyzw"[off % 16 / 4] + "\n(ダブルクリックで宣言へ)",
                        Cursor = Cursors.Hand,
                        Tag = group
                    };
                    rect.MouseLeftButtonDown += (sender, e) =>
                    {
                        if (e.ClickCount == 2)
                        {
                            int g = (int)((Rectangle)sender).Tag;
                            if (g < members.Count) GoTo((string)members[g]["file"], (int)members[g]["line"]);
                            e.Handled = true;
                        }
                    };
                    Canvas.SetLeft(rect, LabelW + pos % 16 * ByteW);
                    Canvas.SetTop(rect, 20 + pos / 16 * RowH);
                    _canvas.Children.Add(rect);
                    if (first || (end - pos) >= 8)
                    {
                        var t = new TextBlock
                        {
                            Text = first ? path : "…",
                            Foreground = Brushes.Black, FontSize = 11,
                            IsHitTestVisible = false,
                            MaxWidth = Math.Max(8, (end - pos) * ByteW - 6),
                            TextTrimming = TextTrimming.CharacterEllipsis
                        };
                        Canvas.SetLeft(t, LabelW + pos % 16 * ByteW + 3);
                        Canvas.SetTop(t, 20 + pos / 16 * RowH + 6);
                        _canvas.Children.Add(t);
                    }
                    first = false;
                    pos = end;
                }
            }
        }

        private static Brush HatchBrush()
        {
            var lines = new DrawingBrush
            {
                TileMode = TileMode.Tile,
                Viewport = new Rect(0, 0, 8, 8),
                ViewportUnits = BrushMappingMode.Absolute,
                Viewbox = new Rect(0, 0, 8, 8),
                ViewboxUnits = BrushMappingMode.Absolute
            };
            var g = new GeometryDrawing(null, new Pen(new SolidColorBrush(Color.FromArgb(150, 150, 150, 150)), 1.2), new LineGeometry(new Point(0, 8), new Point(8, 0)));
            lines.Drawing = g;
            return lines;
        }

        private void AddText(string text, double x, double y, Brush fg, double size)
        {
            var t = new TextBlock { Text = text, FontSize = size };
            if (fg != null) t.Foreground = fg;
            else t.SetResourceReference(TextBlock.ForegroundProperty, EnvironmentColors.ToolWindowTextBrushKey);
            Canvas.SetLeft(t, x);
            Canvas.SetTop(t, y);
            _canvas.Children.Add(t);
        }

        // ---- ファイルを開く ----
        private void GoTo(string file, int line)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                if (_services == null || !File.Exists(file)) return;
                IVsUIHierarchy hier;
                uint itemId;
                IVsWindowFrame frame;
                VsShellUtilities.OpenDocument(_services, file, Guid.Empty, out hier, out itemId, out frame);
                if (frame == null) return;
                frame.Show();
                IVsTextView view = VsShellUtilities.GetTextView(frame);
                if (view == null) return;
                view.SetCaretPos(Math.Max(line, 0), 0);
                view.CenterLines(Math.Max(line, 0), 1);
            }
            catch (Exception ex) { KHlslPackage.Log("open failed: " + ex.Message); }
        }
    }
}
