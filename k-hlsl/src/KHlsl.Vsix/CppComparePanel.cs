using System;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using Microsoft.VisualStudio.PlatformUI;
using Newtonsoft.Json.Linq;

namespace KHlsl.Vsix
{
    /// <summary>C++ の構造体と、HLSL の cbuffer のレイアウトを比べた結果(表と、レジスタの図)。</summary>
    public sealed class CppComparePanel : UserControl
    {
        private readonly TextBlock _title = new TextBlock { FontWeight = FontWeights.SemiBold, Margin = new Thickness(0, 0, 8, 0), VerticalAlignment = VerticalAlignment.Center };
        private readonly ComboBox _hlsl = new ComboBox { MinWidth = 200, Margin = new Thickness(0, 0, 8, 0) };
        private readonly TextBlock _status = new TextBlock { Margin = new Thickness(6, 2, 6, 6), TextWrapping = TextWrapping.Wrap };
        private readonly Grid _table = new Grid { Margin = new Thickness(6, 0, 6, 6) };
        private readonly StackPanel _figures = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(6, 0, 6, 6) };
        private bool _filling;

        /// <summary>比べる HLSL を、コンボ ボックスで選び直した(引数は、cbuffer / struct の名前)。</summary>
        public Action<string> HlslBlockChanged;

        public CppComparePanel()
        {
            var bar = new DockPanel { Margin = new Thickness(6, 4, 6, 4), LastChildFill = false };
            var vs = new TextBlock { Text = "HLSL:", Margin = new Thickness(0, 0, 4, 0), VerticalAlignment = VerticalAlignment.Center };
            foreach (var t in new[] { _title, vs, _status })
                t.SetResourceReference(TextBlock.ForegroundProperty, EnvironmentColors.ToolWindowTextBrushKey);
            DockPanel.SetDock(_title, Dock.Left);
            DockPanel.SetDock(vs, Dock.Left);
            DockPanel.SetDock(_hlsl, Dock.Left);
            bar.Children.Add(_title);
            bar.Children.Add(vs);
            bar.Children.Add(_hlsl);
            _hlsl.SelectionChanged += (s, e) =>
            {
                if (_filling) return;
                var item = _hlsl.SelectedItem as ComboBoxItem;
                if (item != null && HlslBlockChanged != null) HlslBlockChanged((string)item.Tag);
            };

            var body = new StackPanel();
            body.Children.Add(bar);
            body.Children.Add(_status);
            body.Children.Add(_table);
            body.Children.Add(_figures);
            Content = new ScrollViewer { Content = body, VerticalScrollBarVisibility = ScrollBarVisibility.Auto, HorizontalScrollBarVisibility = ScrollBarVisibility.Auto };
        }

        public void ShowMessage(string text)
        {
            _title.Text = "C++ と比べる";
            _status.Text = text;
            _table.Children.Clear();
            _table.RowDefinitions.Clear();
            _table.ColumnDefinitions.Clear();
            _figures.Children.Clear();
        }

        public void Show(JObject r)
        {
            _title.Text = "C++ " + (string)r["cppStruct"] + "  ↔";
            // 比べる HLSL の候補
            _filling = true;
            _hlsl.Items.Clear();
            string current = (string)((JObject)r["hlsl"])["name"];
            foreach (JObject c in (JArray)r["candidates"])
            {
                var item = new ComboBoxItem { Content = (string)c["title"], Tag = (string)c["name"] };
                _hlsl.Items.Add(item);
                if ((string)c["name"] == current) _hlsl.SelectedItem = item;
            }
            _filling = false;

            int bad = (int)r["mismatches"];
            bool sizeOk = (bool)r["sizeOk"];
            string first = (string)r["first"];
            string text;
            Brush brush;
            if ((bool)r["ok"]) { text = "一致しています(C++ " + (int)r["cppSize"] + " バイト / HLSL " + (int)r["hlslPaddedSize"] + " バイト)。"; brush = new SolidColorBrush(Color.FromRgb(0x3C, 0xB0, 0x5A)); }
            else
            {
                text = (bad > 0 ? bad + " か所がずれています。最初のずれ: " + first + "。" : "メンバーは一致しています。") +
                       (sizeOk ? "" : " 全体の大きさが違います(C++ " + (int)r["cppSize"] + " / HLSL " + (int)r["hlslPaddedSize"] + " バイト。HLSL は 16 の倍数)。");
                brush = new SolidColorBrush(Color.FromRgb(0xE5, 0x4B, 0x4B));
            }
            _status.Text = text;
            _status.Foreground = brush;

            BuildTable((JArray)r["rows"]);

            _figures.Children.Clear();
            _figures.Children.Add(Figure("C++  " + (string)r["cppStruct"], (JObject)r["cpp"]));
            _figures.Children.Add(Figure("HLSL  " + (string)r["hlslName"], (JObject)r["hlsl"]));
        }

        private static UIElement Figure(string title, JObject block)
        {
            var panel = new StackPanel { Margin = new Thickness(0, 0, 14, 0) };
            var t = new TextBlock { Text = title, FontSize = 10, FontWeight = FontWeights.SemiBold, Margin = new Thickness(0, 0, 0, 2) };
            t.SetResourceReference(TextBlock.ForegroundProperty, EnvironmentColors.ToolWindowTextBrushKey);
            panel.Children.Add(t);
            if (block == null || ((JArray)block["segments"]).Count == 0 && (int)block["size"] == 0) return panel;
            panel.Children.Add(CBufferGrid.Build(block, 16, 22, 9, EnvironmentColors.ToolWindowTextBrushKey, null));
            return panel;
        }

        private void BuildTable(JArray rows)
        {
            _table.Children.Clear();
            _table.RowDefinitions.Clear();
            _table.ColumnDefinitions.Clear();
            for (int c = 0; c < 4; c++)
                _table.ColumnDefinitions.Add(new ColumnDefinition { Width = c == 3 ? new GridLength(1, GridUnitType.Star) : GridLength.Auto });
            AddRow(0, new[] { "メンバー", "C++ (位置 / 大きさ)", "HLSL (位置 / 大きさ)", "状態" }, null, true);
            int i = 1;
            foreach (JObject row in rows)
            {
                string status = (string)row["status"];
                string path = (string)row["path"];
                string cpp = Cell(row["cpp"] as JObject);
                string hlsl = Cell(row["hlsl"] as JObject);
                string label = StatusLabel(status);
                string note = (string)row["note"];
                if (note.Length > 0) label += "  " + note;
                Brush bg = null;
                if (status == "offset" || status == "size" || status == "onlyHlsl" || status == "onlyCpp") bg = new SolidColorBrush(Color.FromArgb(70, 0xE5, 0x4B, 0x4B));
                else if (status == "shifted") bg = new SolidColorBrush(Color.FromArgb(50, 0xE5, 0xAA, 0x28));
                else if (status == "padding") bg = new SolidColorBrush(Color.FromArgb(30, 128, 128, 128));
                AddRow(i++, new[] { path, cpp, hlsl, label }, bg, false);
            }
        }

        private static string Cell(JObject o)
        {
            return o == null ? "—" : (string)o["type"] + "  " + (int)o["offset"] + " / " + (int)o["size"];
        }

        private static string StatusLabel(string s)
        {
            switch (s)
            {
                case "ok": return "一致";
                case "offset": return "位置がずれ";
                case "size": return "大きさが違う";
                case "shifted": return "ずれの続き";
                case "renamed": return "名前違い";
                case "padding": return "パディング";
                case "onlyHlsl": return "C++ になし";
                case "onlyCpp": return "HLSL になし";
                default: return s;
            }
        }

        private void AddRow(int rowIndex, string[] cells, Brush bg, bool header)
        {
            _table.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            for (int c = 0; c < cells.Length; c++)
            {
                var tb = new TextBlock
                {
                    Text = cells[c],
                    Margin = new Thickness(6, 2, 10, 2),
                    FontSize = 11,
                    FontWeight = header ? FontWeights.SemiBold : FontWeights.Normal,
                    TextWrapping = c == 3 ? TextWrapping.Wrap : TextWrapping.NoWrap
                };
                tb.SetResourceReference(TextBlock.ForegroundProperty, EnvironmentColors.ToolWindowTextBrushKey);
                var host = new Border { Child = tb, Background = bg };
                Grid.SetRow(host, rowIndex);
                Grid.SetColumn(host, c);
                _table.Children.Add(host);
            }
        }
    }
}
