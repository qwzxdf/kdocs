using System;
using System.Collections.Generic;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using Microsoft.VisualStudio.PlatformUI;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Microsoft.VisualStudio.TextManager.Interop;

namespace KCppErr
{
    /// <summary>エラーの一覧。見出しをダブルクリックすると、自分のコードの原因の場所へ飛ぶ。</summary>
    public sealed class ErrorView : UserControl
    {
        private readonly TreeView _tree = new TreeView();
        private readonly TextBlock _summary = new TextBlock();
        private readonly CheckBox _warnings = new CheckBox { Content = "警告も表示" };
        private IServiceProvider _services;
        private List<ErrorGroup> _groups = new List<ErrorGroup>();
        private string _solutionDir = "";

        public Action RefreshRequested;

        public ErrorView()
        {
            SetResourceReference(BackgroundProperty, EnvironmentColors.ToolWindowBackgroundBrushKey);
            SetResourceReference(ForegroundProperty, EnvironmentColors.ToolWindowTextBrushKey);

            var bar = new DockPanel { Margin = new Thickness(6, 4, 6, 4), LastChildFill = true };
            var refresh = new Button { Content = "ビルド出力を読み直す", Padding = new Thickness(8, 2, 8, 2), Margin = new Thickness(0, 0, 10, 0) };
            refresh.Click += (s, e) => { if (RefreshRequested != null) RefreshRequested(); };
            _warnings.Margin = new Thickness(0, 0, 10, 0);
            _warnings.VerticalAlignment = VerticalAlignment.Center;
            _warnings.SetResourceReference(Control.ForegroundProperty, EnvironmentColors.ToolWindowTextBrushKey);
            _warnings.Click += (s, e) => Render();
            _summary.VerticalAlignment = VerticalAlignment.Center;
            _summary.SetResourceReference(TextBlock.ForegroundProperty, EnvironmentColors.ToolWindowTextBrushKey);
            DockPanel.SetDock(refresh, Dock.Left);
            DockPanel.SetDock(_warnings, Dock.Left);
            bar.Children.Add(refresh);
            bar.Children.Add(_warnings);
            bar.Children.Add(_summary);

            _tree.BorderThickness = new Thickness(0);
            _tree.Background = Brushes.Transparent;
            _tree.SetResourceReference(Control.ForegroundProperty, EnvironmentColors.ToolWindowTextBrushKey);
            ScrollViewer.SetHorizontalScrollBarVisibility(_tree, ScrollBarVisibility.Auto);

            var grid = new Grid();
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            Grid.SetRow(bar, 0);
            Grid.SetRow(_tree, 1);
            grid.Children.Add(bar);
            grid.Children.Add(_tree);
            Content = grid;
        }

        public void Initialize(IServiceProvider services)
        {
            _services = services;
        }

        public void SetResult(List<ErrorGroup> groups, string solutionDir)
        {
            _groups = groups ?? new List<ErrorGroup>();
            _solutionDir = solutionDir ?? "";
            Render();
        }

        private void Render()
        {
            _tree.Items.Clear();
            int errors = 0, warnings = 0;
            foreach (ErrorGroup g in _groups)
            {
                if (g.IsError) errors++; else warnings++;
                if (!g.IsError && _warnings.IsChecked != true) continue;
                _tree.Items.Add(MakeGroupItem(g));
            }
            _summary.Text = errors + " 件のエラー、" + warnings + " 件の警告";
            if (_groups.Count == 0) _summary.Text = "ビルド出力にエラーはありません";
        }

        private TreeViewItem MakeGroupItem(ErrorGroup g)
        {
            Frame target = Analyzer.FindUserFrame(g, _solutionDir);
            var head = new StackPanel { Margin = new Thickness(0, 3, 0, 3) };

            var title = new TextBlock { TextWrapping = TextWrapping.Wrap };
            title.Inlines.Add(new System.Windows.Documents.Run((g.IsError ? "✖ " : "⚠ "))
            {
                Foreground = g.IsError ? new SolidColorBrush(Color.FromRgb(0xE5, 0x4B, 0x4B)) : new SolidColorBrush(Color.FromRgb(0xE5, 0xAA, 0x28))
            });
            if (g.Primary.Code.Length > 0)
                title.Inlines.Add(new System.Windows.Documents.Run("[" + g.Primary.Code + "] ") { FontWeight = FontWeights.SemiBold });
            title.Inlines.Add(new System.Windows.Documents.Run(Analyzer.Shorten(g.Primary.Message, 200)));
            head.Children.Add(title);

            var where = new TextBlock { Margin = new Thickness(18, 1, 0, 0), TextWrapping = TextWrapping.Wrap };
            if (target != null)
            {
                where.Inlines.Add(new System.Windows.Documents.Run("→ " + Path.GetFileName(target.File) + " の " + target.Line + " 行目")
                {
                    Foreground = new SolidColorBrush(Color.FromRgb(0x4C, 0x8B, 0xF5)),
                    FontWeight = FontWeights.SemiBold
                });
                where.Inlines.Add(new System.Windows.Documents.Run("  (ダブルクリックで移動)") { Foreground = Brushes.Gray });
            }
            else
            {
                where.Inlines.Add(new System.Windows.Documents.Run("自分のコードの場所は、出力から見つかりませんでした") { Foreground = Brushes.Gray });
            }
            head.Children.Add(where);

            var item = new TreeViewItem { Header = head, IsExpanded = true };
            item.MouseDoubleClick += (s, e) =>
            {
                if (!ReferenceEquals(e.OriginalSource, null) && IsOnHeader(item, e.OriginalSource as DependencyObject))
                {
                    if (target != null) Open(target);
                    e.Handled = true;
                }
            };

            string hint = Analyzer.HintFor(g, _solutionDir);
            if (hint.Length > 0)
                item.Items.Add(new TreeViewItem { Header = new TextBlock { Text = "💡 " + hint, TextWrapping = TextWrapping.Wrap, MaxWidth = 700 }, IsExpanded = true });

            AddFrames(item, "呼び出しの経路(内側から外側へ)", g, FrameKind.Trace, true);
            AddFrames(item, "候補", g, FrameKind.Candidate, false);
            AddFrames(item, "そのほかの補足", g, FrameKind.Other, false);

            var raw = new TreeViewItem { Header = "元のメッセージ(" + g.Raw.Count + " 行)" };
            foreach (string line in g.Raw)
                raw.Items.Add(new TreeViewItem { Header = new TextBlock { Text = line.TrimEnd(), FontFamily = new FontFamily("Consolas"), TextWrapping = TextWrapping.Wrap } });
            item.Items.Add(raw);
            return item;
        }

        private void AddFrames(TreeViewItem parent, string title, ErrorGroup g, FrameKind kind, bool expand)
        {
            var list = g.Frames.FindAll(f => f.Kind == kind);
            if (list.Count == 0) return;
            var node = new TreeViewItem { Header = title + "(" + list.Count + ")", IsExpanded = expand };
            foreach (Frame f in list)
            {
                bool user = f.HasLocation && Analyzer.IsUserFile(f.File, _solutionDir);
                var text = new TextBlock { TextWrapping = TextWrapping.Wrap, MaxWidth = 700 };
                if (f.HasLocation)
                    text.Inlines.Add(new System.Windows.Documents.Run(Path.GetFileName(f.File) + ":" + f.Line + "  ")
                    {
                        FontWeight = user ? FontWeights.SemiBold : FontWeights.Normal,
                        Foreground = user ? new SolidColorBrush(Color.FromRgb(0x4C, 0x8B, 0xF5)) : Brushes.Gray
                    });
                text.Inlines.Add(new System.Windows.Documents.Run(Analyzer.Shorten(f.Message, 300)));
                var child = new TreeViewItem { Header = text, ToolTip = f.Location };
                Frame captured = f;
                child.MouseDoubleClick += (s, e) =>
                {
                    if (captured.HasLocation) Open(captured);
                    e.Handled = true;
                };
                node.Items.Add(child);
            }
            parent.Items.Add(node);
        }

        // ダブルクリックが、子の項目ではなく見出しの上で起きたか
        private static bool IsOnHeader(TreeViewItem item, DependencyObject source)
        {
            while (source != null)
            {
                var tvi = source as TreeViewItem;
                if (tvi != null) return ReferenceEquals(tvi, item);
                source = (source is System.Windows.Media.Visual || source is System.Windows.Media.Media3D.Visual3D)
                    ? VisualTreeHelper.GetParent(source)
                    : LogicalTreeHelper.GetParent(source);
            }
            return false;
        }

        private void Open(Frame f)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                if (_services == null || !File.Exists(f.File)) return;
                IVsUIHierarchy hier;
                uint itemId;
                IVsWindowFrame frame;
                VsShellUtilities.OpenDocument(_services, f.File, Guid.Empty, out hier, out itemId, out frame);
                if (frame == null) return;
                frame.Show();
                IVsTextView view = VsShellUtilities.GetTextView(frame);
                if (view == null) return;
                int line = Math.Max(f.Line - 1, 0);
                int col = Math.Max(f.Col - 1, 0);
                view.SetCaretPos(line, col);
                view.CenterLines(line, 1);
            }
            catch (Exception ex)
            {
                KCppErrPackage.Log("open failed: " + ex.Message);
            }
        }
    }
}
