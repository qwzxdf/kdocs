using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Media;
using Microsoft.VisualStudio.PlatformUI;

namespace KCppAssist.ErrorLog
{
    /// <summary>色つきのエラーログを表示する窓の中身。「出力」ウィンドウのように文字が並び、選択とコピーができ、リンクを押すとその場所へ飛ぶ。</summary>
    public sealed class LogView : UserControl
    {
        private readonly RichTextBox _rtb = new RichTextBox();
        private readonly CheckBox _raw = new CheckBox { Content = "原文", ToolTip = "ビルド出力を、整理せずに色だけ付けて表示します" };
        private readonly CheckBox _warn = new CheckBox { Content = "警告も表示" };
        private readonly MenuItem _trace = new MenuItem { Header = "経路を全部表示", IsCheckable = true, ToolTip = "テンプレートの経路のうち、ライブラリ内の段も省略せずに出します" };
        private readonly MenuItem _attach = new MenuItem { Header = "原文を併記", IsCheckable = true, ToolTip = "整理した各項目の下に、元のメッセージも出します" };
        private readonly MenuItem _expandAll = new MenuItem { Header = "すべての詳細を開く", IsCheckable = true, ToolTip = "各エラーの ▸ を、すべて開いた状態にします" };
        private readonly MenuItem _copyRawItem = new MenuItem { Header = "原文をコピー", ToolTip = "ビルド出力をそのままコピーします(AI や質問に貼る用)" };
        private readonly Button _more = new Button { Content = "…", ToolTip = "そのほかの表示とコピー" };
        private readonly HashSet<int> _open = new HashSet<int>();
        private readonly Dictionary<string, Paragraph> _anchors = new Dictionary<string, Paragraph>();
        private readonly Button _reload = new Button { Content = "再読み込み" };
        private readonly Button _copy = new Button { Content = "コピー", ToolTip = "いま表示している内容を、文字としてコピーします" };
        private readonly WrapPanel _bar = new WrapPanel { Margin = new Thickness(6, 4, 6, 4) };

        private RenderInput _input;
        private Doc _doc = new Doc();
        private string _message = "ビルドすると、ここにエラーが出ます。";

        /// <summary>「再読み込み」が押された。</summary>
        public Action RefreshRequested;
        /// <summary>リンク(ファイルの場所、または検索語)が押された。</summary>
        public Action<Run> LinkClicked;

        public LogView()
        {
            foreach (CheckBox c in new[] { _raw, _warn })
            {
                c.Margin = new Thickness(0, 0, 12, 0);
                c.VerticalAlignment = VerticalAlignment.Center;
                c.Click += (s, e) => Rebuild();
            }
            _warn.IsChecked = false;
            foreach (MenuItem m in new[] { _trace, _attach, _expandAll }) m.Click += (s, e) => Rebuild();

            foreach (Button b in new[] { _reload, _copy, _more })
            {
                b.Padding = new Thickness(8, 2, 8, 2);
                b.Margin = new Thickness(0, 0, 8, 0);
            }
            _reload.Click += (s, e) => { if (RefreshRequested != null) RefreshRequested(); };
            _copy.Click += (s, e) => CopyText(_doc.ToPlainText());
            _copyRaw_Click();
            var menu = new ContextMenu();
            menu.Items.Add(_expandAll);
            menu.Items.Add(_trace);
            menu.Items.Add(_attach);
            menu.Items.Add(new Separator());
            menu.Items.Add(_copyRawItem);
            _more.ContextMenu = menu;
            _more.Click += (s, e) =>
            {
                menu.PlacementTarget = _more;
                menu.Placement = System.Windows.Controls.Primitives.PlacementMode.Top;
                menu.IsOpen = true;
            };

            _bar.Children.Add(_reload);
            _bar.Children.Add(_warn);
            _bar.Children.Add(_raw);
            _bar.Children.Add(_copy);
            _bar.Children.Add(_more);

            _rtb.IsReadOnly = true;
            _rtb.IsDocumentEnabled = true;                 // Hyperlink を押せるようにする
            _rtb.BorderThickness = new Thickness(0);
            _rtb.VerticalScrollBarVisibility = ScrollBarVisibility.Auto;
            _rtb.HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled;

            var grid = new Grid();
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            Grid.SetRow(_bar, 0);
            Grid.SetRow(_rtb, 1);
            grid.Children.Add(_bar);
            grid.Children.Add(_rtb);
            Content = grid;

            Loaded += (s, e) => { VSColorTheme.ThemeChanged += OnThemeChanged; Rebuild(); };
            Unloaded += (s, e) => VSColorTheme.ThemeChanged -= OnThemeChanged;
            ApplyColors();
        }

        private void _copyRaw_Click()
        {
            _copyRawItem.Click += (s, e) => CopyText(_input != null && _input.Report != null ? _input.Report.RawText : "");
        }

        private void OnThemeChanged(ThemeChangedEventArgs e)
        {
            Dispatcher.BeginInvoke(new Action(() => { ApplyColors(); Rebuild(); }));
        }

        private void ApplyColors()
        {
            Color back = Theme.Background;
            Color fore = Theme.Foreground;
            Background = new SolidColorBrush(back);
            Foreground = new SolidColorBrush(fore);
            _rtb.Background = new SolidColorBrush(back);
            _rtb.Foreground = new SolidColorBrush(fore);
            _bar.Background = new SolidColorBrush(back);
            foreach (CheckBox c in new[] { _raw, _warn }) c.Foreground = new SolidColorBrush(fore);
            foreach (Button b in new[] { _reload, _copy, _more })
            {
                b.Foreground = new SolidColorBrush(fore);
                b.Background = new SolidColorBrush(Theme.ButtonBackground);
                b.BorderBrush = Theme.BrushFor(Role.Dim);
            }
        }

        /// <summary>解析結果を表示する。</summary>
        public void SetInput(RenderInput input)
        {
            _input = input;
            _open.Clear();
            Rebuild();
        }

        /// <summary>解析結果はそのままで、描き直す(検索が終わったときなど)。</summary>
        public void Redraw()
        {
            Rebuild();
        }

        /// <summary>文章だけを表示する(ビルド中など)。</summary>
        public void ShowMessage(string text)
        {
            _input = null;
            _message = text;
            Rebuild();
        }

        /// <summary>設定画面の「エラーログ」の、チェックボックスの初期値を入れる(窓を作ったときに 1 回)。</summary>
        public void ApplyDefaults(OptionsPage o)
        {
            if (o == null) return;
            _raw.IsChecked = o.ErrorLogRawMode;
            _warn.IsChecked = o.ErrorLogShowWarnings;
            _trace.IsChecked = o.ErrorLogFullTrace;
            _attach.IsChecked = o.ErrorLogAttachRaw;
            Rebuild();
        }

        private RenderOptions Options()
        {
            return new RenderOptions
            {
                RawMode = _raw.IsChecked == true,
                ShowWarnings = _warn.IsChecked == true,
                FullTrace = _trace.IsChecked == true,
                AttachRaw = _attach.IsChecked == true
            };
        }

        private void Rebuild()
        {
            double keep = _rtb.VerticalOffset;
            RebuildCore();
            if (keep > 0) _rtb.Dispatcher.BeginInvoke(new Action(() => _rtb.ScrollToVerticalOffset(keep)), System.Windows.Threading.DispatcherPriority.Loaded);
        }

        private void RebuildCore()
        {
            try
            {
                if (_input == null || _input.Report == null)
                {
                    _doc = new Doc();
                    new LineBuilder(_doc).Add(_message, Role.Dim).Done();
                }
                else
                {
                    _doc = Renderer.Render(_input, Options());
                }
                Fill(_doc);
            }
            catch (Exception ex)
            {
                KCppAssistPackage.Log("render failed: " + ex);
                _doc = new Doc();
                new LineBuilder(_doc).Add("表示の組み立てに失敗しました: " + ex.Message, Role.Error).Done();
                try { Fill(_doc); } catch (Exception) { }
            }
        }

        private void Fill(Doc doc)
        {
            var fd = new FlowDocument
            {
                FontFamily = new FontFamily("Consolas, Yu Gothic UI, Meiryo UI"),
                FontSize = 13,
                PagePadding = new Thickness(8, 4, 8, 8),
                Background = Brushes.Transparent,
                Foreground = Theme.BrushFor(Role.Normal),
                PageWidth = double.NaN
            };

            _anchors.Clear();
            foreach (DocLine line in doc.Lines)
            {
                if (line.DetailGroup > 0 && _expandAll.IsChecked != true && !_open.Contains(line.DetailGroup)) continue;
                if (line.RuleAbove)
                {
                    var rule = new Paragraph(new System.Windows.Documents.Run(" "))
                    {
                        FontSize = 2,
                        Margin = new Thickness(0, 5, 0, 1),
                        BorderBrush = Theme.BrushFor(Role.Dim),
                        BorderThickness = new Thickness(0, 1, 0, 0)
                    };
                    fd.Blocks.Add(rule);
                }

                var p = new Paragraph { Margin = new Thickness(0, line.SpaceBefore ? 3 : 0, 0, 0) };
                double left = line.Indent * 20;
                if (line.Bar != null)
                {
                    p.BorderBrush = Theme.BrushFor(line.Bar.Value);
                    p.BorderThickness = new Thickness(3, 0, 0, 0);
                    p.Padding = new Thickness(8 + left, 0, 0, 0);
                    p.Margin = new Thickness(2, p.Margin.Top, 0, 0);
                }
                else
                {
                    p.Margin = new Thickness(left, p.Margin.Top, 0, 0);
                }

                if (!string.IsNullOrEmpty(line.Anchor)) _anchors[line.Anchor] = p;
                foreach (Run r in line.Runs) p.Inlines.Add(MakeInline(r));
                if (line.Runs.Count == 0) p.Inlines.Add(new System.Windows.Documents.Run(" "));
                fd.Blocks.Add(p);
            }
            _rtb.Document = fd;
        }

        private Inline MakeInline(Run r)
        {
            string shownText = r.Text;
            if (r.Toggle > 0) shownText = _expandAll.IsChecked == true || _open.Contains(r.Toggle) ? "▾ " : "▸ ";
            var text = new System.Windows.Documents.Run(shownText)
            {
                Foreground = Theme.BrushFor(r.Role),
                FontWeight = r.Bold ? FontWeights.SemiBold : FontWeights.Normal,
                FontStyle = r.Italic ? FontStyles.Italic : FontStyles.Normal
            };
            if (!r.IsLink) return text;

            if (r.Toggle > 0 || !string.IsNullOrEmpty(r.Jump))
            {
                var inner = new Hyperlink(text)
                {
                    Foreground = r.Toggle > 0 ? Theme.BrushFor(Role.Dim) : Theme.BrushFor(Role.Link),
                    Cursor = System.Windows.Input.Cursors.Hand,
                    TextDecorations = r.Toggle > 0 ? null : TextDecorations.Underline,
                    ToolTip = r.Toggle > 0 ? "押すと、詳細を開閉します" : "このファイルの最初のエラーへ移動します"
                };
                int group = r.Toggle;
                string jump = r.Jump;
                inner.Click += (s, e) =>
                {
                    if (group > 0)
                    {
                        if (!_open.Add(group)) _open.Remove(group);
                        Rebuild();
                    }
                    else
                    {
                        Paragraph target;
                        if (_anchors.TryGetValue(jump, out target)) target.BringIntoView();
                    }
                };
                return inner;
            }

            var link = new Hyperlink(text)
            {
                Foreground = Theme.BrushFor(Role.Link),
                Cursor = System.Windows.Input.Cursors.Hand,
                ToolTip = !string.IsNullOrEmpty(r.File) ? r.File + (r.Line > 0 ? " (" + r.Line + ")" : "")
                    : !string.IsNullOrEmpty(r.Url) ? "ブラウザーで開く: " + r.Url : "ソリューション内を検索"
            };
            Run captured = r;
            link.Click += (s, e) =>
            {
                if (LinkClicked != null) LinkClicked(captured);
            };
            return link;
        }

        private static void CopyText(string text)
        {
            try { if (!string.IsNullOrEmpty(text)) Clipboard.SetText(text); }
            catch (Exception ex) { KCppAssistPackage.Log("copy failed: " + ex.Message); }
        }
    }
}
