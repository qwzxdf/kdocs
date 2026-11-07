using System;
using System.Collections.Generic;
using System.Windows.Media;
using Microsoft.VisualStudio.PlatformUI;
using Microsoft.VisualStudio.Shell;

namespace KCppAssist.ErrorLog
{
    /// <summary>
    /// 文字の役割(Role)を、Visual Studio のテーマ(ダーク / ライト)に合わせた色にする。
    /// コードの色は、VS の配色 Dark+ / Light+ に合わせてある。
    /// </summary>
    internal static class Theme
    {
        private static readonly Dictionary<Role, Color> Dark = new Dictionary<Role, Color>
        {
            [Role.Error] = Rgb(0xF4, 0x87, 0x71),
            [Role.Warning] = Rgb(0xE5, 0xC0, 0x7B),
            [Role.Note] = Rgb(0x9C, 0xDC, 0xFE),
            [Role.Code] = Rgb(0xD7, 0xBA, 0x7D),
            [Role.Link] = Rgb(0x4F, 0xA3, 0xFF),
            [Role.Scope] = Rgb(0x9A, 0x9A, 0x9A),
            [Role.Func] = Rgb(0xDC, 0xDC, 0xAA),
            [Role.Type] = Rgb(0x4E, 0xC9, 0xB0),
            [Role.Keyword] = Rgb(0x56, 0x9C, 0xD6),
            [Role.Number] = Rgb(0xB5, 0xCE, 0xA8),
            [Role.Punct] = Rgb(0x8C, 0x8C, 0x8C),
            [Role.Heading] = Rgb(0xFF, 0xFF, 0xFF),
            [Role.Good] = Rgb(0x89, 0xD1, 0x85),
            [Role.Hint] = Rgb(0xCE, 0x91, 0x78),
            [Role.Dim] = Rgb(0x8C, 0x8C, 0x8C),
        };

        private static readonly Dictionary<Role, Color> Light = new Dictionary<Role, Color>
        {
            [Role.Error] = Rgb(0xCD, 0x31, 0x31),
            [Role.Warning] = Rgb(0xBF, 0x88, 0x03),
            [Role.Note] = Rgb(0x00, 0x66, 0xB8),
            [Role.Code] = Rgb(0x79, 0x5E, 0x26),
            [Role.Link] = Rgb(0x00, 0x66, 0xCC),
            [Role.Scope] = Rgb(0x6E, 0x6E, 0x6E),
            [Role.Func] = Rgb(0x79, 0x5E, 0x26),
            [Role.Type] = Rgb(0x26, 0x7F, 0x99),
            [Role.Keyword] = Rgb(0x00, 0x00, 0xFF),
            [Role.Number] = Rgb(0x09, 0x86, 0x58),
            [Role.Punct] = Rgb(0x6E, 0x6E, 0x6E),
            [Role.Heading] = Rgb(0x00, 0x00, 0x00),
            [Role.Good] = Rgb(0x2E, 0x7D, 0x32),
            [Role.Hint] = Rgb(0xA3, 0x15, 0x15),
            [Role.Dim] = Rgb(0x76, 0x76, 0x76),
        };

        private static Color Rgb(byte r, byte g, byte b) { return Color.FromRgb(r, g, b); }

        public static Color Background
        {
            get
            {
                try
                {
                    var c = VSColorTheme.GetThemedColor(EnvironmentColors.ToolWindowBackgroundColorKey);
                    return Color.FromArgb(c.A, c.R, c.G, c.B);
                }
                catch (Exception) { return Color.FromRgb(0x1E, 0x1E, 0x1E); }
            }
        }

        public static Color Foreground
        {
            get
            {
                try
                {
                    var c = VSColorTheme.GetThemedColor(EnvironmentColors.ToolWindowTextColorKey);
                    return Color.FromArgb(c.A, c.R, c.G, c.B);
                }
                catch (Exception) { return Color.FromRgb(0xD4, 0xD4, 0xD4); }
            }
        }

        public static bool IsDark
        {
            get
            {
                Color b = Background;
                return (0.299 * b.R + 0.587 * b.G + 0.114 * b.B) < 128;
            }
        }

        public static Brush BrushFor(Role role)
        {
            if (role == Role.Normal) return Freeze(new SolidColorBrush(Foreground));
            Dictionary<Role, Color> table = IsDark ? Dark : Light;
            Color c;
            if (!table.TryGetValue(role, out c)) c = Foreground;
            return Freeze(new SolidColorBrush(c));
        }

        public static Color ButtonBackground
        {
            get
            {
                Color b = Background;
                int d = IsDark ? 24 : -16;
                return Color.FromRgb(Clamp(b.R + d), Clamp(b.G + d), Clamp(b.B + d));
            }
        }

        private static byte Clamp(int v) { return (byte)Math.Max(0, Math.Min(255, v)); }

        private static Brush Freeze(SolidColorBrush b)
        {
            b.Freeze();
            return b;
        }
    }
}
