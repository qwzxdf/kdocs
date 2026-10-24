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
        private readonly ComboBox _blocks = new ComboBox { MinWidth = 260, Margin = new Thickness(0, 0, 8, 0) };
        private readonly CheckBox _structs = new CheckBox { Content = "struct も表示", Margin = new Thickness(0, 0, 8, 0), VerticalAlignment = VerticalAlignment.Center };
        private readonly TextBlock _file = new TextBlock { VerticalAlignment = VerticalAlignment.Center };
        private readonly TextBlock _summary = new TextBlock { Margin = new Thickness(8, 4, 8, 4), TextWrapping = TextWrapping.Wrap };
        private readonly ScrollViewer _gridHost = new ScrollViewer
        {
            HorizontalScrollBarVisibility = ScrollBarVisibility.Auto,
            VerticalScrollBarVisibility = ScrollBarVisibility.Auto
        };

        private readonly CppComparePanel _compare = new CppComparePanel { Visibility = Visibility.Collapsed };
        private readonly GridSplitter _splitter = new GridSplitter { Height = 4, HorizontalAlignment = HorizontalAlignment.Stretch, Background = Brushes.Gray, Visibility = Visibility.Collapsed };
        private string _cmpPath, _cmpText, _cmpStruct;
        private readonly RowDefinition _cmpRow = new RowDefinition { Height = GridLength.Auto };

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

            var gridScroll = _gridHost;

            var grid = new Grid();
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(_cmpRow);
            Grid.SetRow(_splitter, 3);
            Grid.SetRow(_compare, 4);
            grid.Children.Add(_splitter);
            grid.Children.Add(_compare);
            _compare.HlslBlockChanged = name => RunCompare(name);
            Grid.SetRow(bar, 0);
            Grid.SetRow(_summary, 1);
            Grid.SetRow(gridScroll, 2);
            grid.Children.Add(bar);
            grid.Children.Add(_summary);
            grid.Children.Add(gridScroll);
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
                    _gridHost.Content = null;
                    _summary.Text = "このファイルには、cbuffer・ConstantBuffer<T> がありません。「struct も表示」で、struct のレイアウトも見られます。";
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

        // ---- C++ の構造体との比較 ----

        /// <summary>C++ の構造体を、HLSL の cbuffer と比べて、結果を下の領域に出す。</summary>
        public void ShowCompare(string cppPath, string cppText, string cppStruct)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            _cmpPath = cppPath; _cmpText = cppText; _cmpStruct = cppStruct;
            _compare.Visibility = Visibility.Visible;
            _splitter.Visibility = Visibility.Visible;
            _cmpRow.Height = new GridLength(1, GridUnitType.Star);
            _compare.ShowMessage("比べています...");
            RunCompare(null);
        }

        private void RunCompare(string hlslBlock)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            string cppPath = _cmpPath, cppText = _cmpText, cppStruct = _cmpStruct;
            string hlslUri = _path != null ? new Uri(_path).AbsoluteUri : null;
            ThreadHelper.JoinableTaskFactory.RunAsync(async () =>
            {
                JToken result = null;
                string error = null;
                try
                {
                    result = await KHlslLanguageClient.RequestAsync("khlsl/cppcompare", new { cppPath, cppText, cppStruct, hlslUri, hlslBlock });
                }
                catch (Exception ex) { error = ex.Message; }
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                if (result == null) { _compare.ShowMessage(error != null ? "言語サーバーに問い合わせられませんでした: " + error : "言語サーバーがまだ起動していません。HLSL のファイルを開いて、少し待ってから、もう一度試してください。"); return; }
                var o = (JObject)result;
                if (o["error"] != null) { _compare.ShowMessage((string)o["error"]); return; }
                _compare.Show(o);
            });
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

            _gridHost.Content = CBufferGrid.Build(b, 24, 30, 11, EnvironmentColors.ToolWindowTextBrushKey, GoTo);

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
