using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Media;
using Microsoft.VisualStudio.PlatformUI;

namespace KErrorLog
{
    /// <summary>色つきのエラーログを表示する窓の中身。「出力」ウィンドウのように文字が並び、選択とコピーができ、リンクを押すとその場所へ飛ぶ。</summary>
    public sealed class LogView : UserControl
    {
        private readonly RichTextBox _rtb = new RichTextBox();
        private readonly CheckBox _raw = new CheckBox { Content = "原文", ToolTip = "ビルド出力を、整理せずに色だけ付けて表示します" };
        private readonly CheckBox _warn = new CheckBox { Content = "警告も表示" };
        private readonly CheckBox _trace = new CheckBox { Content = "経路を全部表示", ToolTip = "テンプレートの経路のうち、ライブラリ内の段も省略せずに出します" };
        private readonly CheckBox _attach = new CheckBox { Content = "原文を併記", ToolTip = "整理した各項目の下に、元のメッセージも出します" };
        private readonly Button _reload = new Button { Content = "再読み込み" };
        private readonly Button _copy = new Button { Content = "コピー", ToolTip = "いま表示している内容を、文字としてコピーします" };
        private readonly Button _copyRaw = new Button { Content = "原文をコピー", ToolTip = "ビルド出力をそのままコピーします(AI や質問に貼る用)" };
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
            foreach (CheckBox c in new[] { _raw, _warn, _trace, _attach })
            {
                c.Margin = new Thickness(0, 0, 12, 0);
                c.VerticalAlignment = VerticalAlignment.Center;
                c.Click += (s, e) => Rebuild();
            }
            _warn.IsChecked = false;

            foreach (Button b in new[] { _reload, _copy, _copyRaw })
            {
                b.Padding = new Thickness(8, 2, 8, 2);
                b.Margin = new Thickness(0, 0, 8, 0);
            }
            _reload.Click += (s, e) => { if (RefreshRequested != null) RefreshRequested(); };
            _copy.Click += (s, e) => CopyText(_doc.ToPlainText());
            _copyRaw.Click += (s, e) => CopyText(_input != null && _input.Report != null ? _input.Report.RawText : "");

            _bar.Children.Add(_reload);
            _bar.Children.Add(_raw);
            _bar.Children.Add(_warn);
            _bar.Children.Add(_trace);
            _bar.Children.Add(_attach);
            _bar.Children.Add(_copy);
            _bar.Children.Add(_copyRaw);

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
            foreach (CheckBox c in new[] { _raw, _warn, _trace, _attach }) c.Foreground = new SolidColorBrush(fore);
            foreach (Button b in new[] { _reload, _copy, _copyRaw })
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
                KErrorLogPackage.Log("render failed: " + ex);
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

            foreach (DocLine line in doc.Lines)
            {
                if (line.RuleAbove)
                {
                    var rule = new Paragraph(new System.Windows.Documents.Run(" "))
                    {
                        FontSize = 2,
                        Margin = new Thickness(0, 10, 0, 4),
                        BorderBrush = Theme.BrushFor(Role.Dim),
                        BorderThickness = new Thickness(0, 1, 0, 0)
                    };
                    fd.Blocks.Add(rule);
                }

                var p = new Paragraph { Margin = new Thickness(0, line.SpaceBefore ? 8 : 0, 0, 0) };
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

                foreach (Run r in line.Runs) p.Inlines.Add(MakeInline(r));
                if (line.Runs.Count == 0) p.Inlines.Add(new System.Windows.Documents.Run(" "));
                fd.Blocks.Add(p);
            }
            _rtb.Document = fd;
        }

        private Inline MakeInline(Run r)
        {
            var text = new System.Windows.Documents.Run(r.Text)
            {
                Foreground = Theme.BrushFor(r.Role),
                FontWeight = r.Bold ? FontWeights.SemiBold : FontWeights.Normal,
                FontStyle = r.Italic ? FontStyles.Italic : FontStyles.Normal
            };
            if (!r.IsLink) return text;

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
            catch (Exception ex) { KErrorLogPackage.Log("copy failed: " + ex.Message); }
        }
    }
}
