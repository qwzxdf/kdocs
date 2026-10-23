using System;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using Microsoft.VisualStudio.PlatformUI;
using Newtonsoft.Json.Linq;
using Rectangle = System.Windows.Shapes.Rectangle;

namespace KHlsl.Vsix
{
    /// <summary>定数バッファのレイアウトの図(16 バイトの行 × 4 バイトの升目)。ツール ウィンドウとホバーで使う。</summary>
    internal static class CBufferGrid
    {
        // 明るい中間色。文字は黒で、ライト/ダークの両方で読める
        private static readonly Color[] Palette =
        {
            Color.FromRgb(0x8E, 0xB8, 0xF5), Color.FromRgb(0xF2, 0xB8, 0x7C), Color.FromRgb(0x9C, 0xD6, 0x9C), Color.FromRgb(0xE0, 0x9C, 0xD6),
            Color.FromRgb(0xE8, 0xD8, 0x6E), Color.FromRgb(0x7F, 0xD0, 0xD0), Color.FromRgb(0xF0, 0xA0, 0xA0), Color.FromRgb(0xB8, 0xA8, 0xE8),
            Color.FromRgb(0xC8, 0xC8, 0x8A), Color.FromRgb(0x9F, 0xC8, 0xB0)
        };

        public static Canvas Build(JObject b, double byteW, double rowH, double fontSize, object textKey, Action<string, int> goTo)
        {
            var canvas = new Canvas();
            double labelW = fontSize * 4.5;
            int padded = Math.Max((int)b["paddedSize"], 16);
            int rows = padded / 16;
            var members = (JArray)b["members"];
            double width = labelW + 16 * byteW + 10;
            canvas.Width = width;
            canvas.Height = rows * rowH + 24;

            // 見出しの行(+0 +4 +8 +12)
            for (int c = 0; c < 4; c++)
                AddText(canvas, textKey, "+" + c * 4, labelW + c * 4 * byteW + 4, 2, Brushes.Gray, fontSize - 1);

            // 行のラベルと、薄い下地(隙間)
            for (int r = 0; r < rows; r++)
            {
                double y = 20 + r * rowH;
                AddText(canvas, textKey, "c" + r, 2, y + (rowH - fontSize - 4) / 2, null, fontSize);
                var bg = new Rectangle
                {
                    Width = 16 * byteW, Height = rowH - 2,
                    Fill = new SolidColorBrush(Color.FromArgb(40, 128, 128, 128)),
                    Stroke = new SolidColorBrush(Color.FromArgb(70, 128, 128, 128)),
                    StrokeThickness = 1
                };
                Canvas.SetLeft(bg, labelW);
                Canvas.SetTop(bg, y);
                canvas.Children.Add(bg);
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
                    Width = (k - start) * byteW, Height = rowH - 2,
                    Fill = HatchBrush(),
                    ToolTip = "隙間 " + (k - start) + " バイト(オフセット " + start + ")"
                };
                Canvas.SetLeft(gap, labelW + start % 16 * byteW);
                Canvas.SetTop(gap, 20 + start / 16 * rowH);
                canvas.Children.Add(gap);
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
                        Width = (end - pos) * byteW - 1, Height = rowH - 2,
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
                            if (g < members.Count) goTo?.Invoke((string)members[g]["file"], (int)members[g]["line"]);
                            e.Handled = true;
                        }
                    };
                    Canvas.SetLeft(rect, labelW + pos % 16 * byteW);
                    Canvas.SetTop(rect, 20 + pos / 16 * rowH);
                    canvas.Children.Add(rect);
                    if (first || (end - pos) >= 8)
                    {
                        var t = new TextBlock
                        {
                            Text = first ? path : "…",
                            Foreground = Brushes.Black, FontSize = fontSize,
                            IsHitTestVisible = false,
                            MaxWidth = Math.Max(8, (end - pos) * byteW - 6),
                            TextTrimming = TextTrimming.CharacterEllipsis
                        };
                        Canvas.SetLeft(t, labelW + pos % 16 * byteW + 3);
                        Canvas.SetTop(t, 20 + pos / 16 * rowH + (rowH - fontSize - 4) / 2);
                        canvas.Children.Add(t);
                    }
                    first = false;
                    pos = end;
                }
            }
            return canvas;
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

        private static void AddText(Canvas canvas, object textKey, string text, double x, double y, Brush fg, double size)
        {
            var t = new TextBlock { Text = text, FontSize = size };
            if (fg != null) t.Foreground = fg;
            else t.SetResourceReference(TextBlock.ForegroundProperty, textKey);
            Canvas.SetLeft(t, x);
            Canvas.SetTop(t, y);
            canvas.Children.Add(t);
        }
    }
}
