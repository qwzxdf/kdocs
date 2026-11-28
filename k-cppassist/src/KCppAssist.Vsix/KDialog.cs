using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Markup;
using System.Windows.Media;
using System.Windows.Media.Effects;
using Microsoft.VisualStudio.PlatformUI;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;

namespace KCppAssist
{
    /// <summary>
    /// K-CppUltimateAssist のダイアログの共通の見た目。枠のない角丸のウィンドウに影を付け、色は VS のテーマ(ダーク・ライト)から取る。
    /// ボタン・チェックボックス・入力欄・一覧は、テーマに合わせて自前で描く(WPF の既定の見た目は、ダークで白く浮くため)。
    /// </summary>
    internal static class KDialog
    {
        // ---- 色 ----

        private static Color Themed(ThemeResourceKey key, Color fallback)
        {
            try { var c = VSColorTheme.GetThemedColor(key); return Color.FromArgb(c.A, c.R, c.G, c.B); }
            catch (Exception) { return fallback; }
        }

        private static Color Mix(Color a, Color b, double t)
        {
            return Color.FromRgb((byte)(a.R + (b.R - a.R) * t), (byte)(a.G + (b.G - a.G) * t), (byte)(a.B + (b.B - a.B) * t));
        }

        private static string Hex(Color c) { return "#" + c.A.ToString("X2") + c.R.ToString("X2") + c.G.ToString("X2") + c.B.ToString("X2"); }

        internal sealed class Palette
        {
            public Color Bg, Fg, Panel, Border, Hover, Accent, AccentSoft, Muted;
            public bool Dark;
        }

        internal static Palette Colors()
        {
            var p = new Palette();
            p.Bg = Themed(EnvironmentColors.ToolWindowBackgroundColorKey, Color.FromRgb(0x25, 0x25, 0x26));
            p.Fg = Themed(EnvironmentColors.ToolWindowTextColorKey, Color.FromRgb(0xE6, 0xE6, 0xE6));
            p.Dark = (0.299 * p.Bg.R + 0.587 * p.Bg.G + 0.114 * p.Bg.B) < 128;
            // 少しだけ前景色に寄せた面(入力欄・補足の箱)と、線
            p.Panel = Mix(p.Bg, p.Fg, p.Dark ? 0.07 : 0.04);
            p.Border = Mix(p.Bg, p.Fg, p.Dark ? 0.22 : 0.18);
            p.Hover = Mix(p.Bg, p.Fg, p.Dark ? 0.12 : 0.08);
            p.Muted = Mix(p.Bg, p.Fg, 0.68);
            // アクセントは、Windows の青(ダークでは少し明るく)
            p.Accent = p.Dark ? Color.FromRgb(0x3B, 0x8E, 0xEA) : Color.FromRgb(0x00, 0x67, 0xC0);
            p.AccentSoft = Mix(p.Bg, p.Accent, p.Dark ? 0.30 : 0.16);
            return p;
        }

        // ---- 部品の見た目(XAML の文字から作る) ----

        private const string StylesXaml = @"
<ResourceDictionary xmlns='http://schemas.microsoft.com/winfx/2006/xaml/presentation' xmlns:x='http://schemas.microsoft.com/winfx/2006/xaml'>
  <Style x:Key='KButton' TargetType='Button'>
    <Setter Property='Foreground' Value='{FG}'/>
    <Setter Property='Background' Value='{PANEL}'/>
    <Setter Property='BorderBrush' Value='{BORDER}'/>
    <Setter Property='Padding' Value='18,7'/>
    <Setter Property='MinWidth' Value='96'/>
    <Setter Property='Cursor' Value='Hand'/>
    <Setter Property='FocusVisualStyle' Value='{x:Null}'/>
    <Setter Property='Template'><Setter.Value>
      <ControlTemplate TargetType='Button'>
        <Border x:Name='b' CornerRadius='6' Background='{TemplateBinding Background}' BorderBrush='{TemplateBinding BorderBrush}' BorderThickness='1' Padding='{TemplateBinding Padding}'>
          <ContentPresenter HorizontalAlignment='Center' VerticalAlignment='Center'/>
        </Border>
        <ControlTemplate.Triggers>
          <Trigger Property='IsMouseOver' Value='True'><Setter TargetName='b' Property='Background' Value='{HOVER}'/></Trigger>
          <Trigger Property='IsKeyboardFocused' Value='True'><Setter TargetName='b' Property='BorderBrush' Value='{ACCENT}'/></Trigger>
          <Trigger Property='IsPressed' Value='True'><Setter TargetName='b' Property='Opacity' Value='0.8'/></Trigger>
        </ControlTemplate.Triggers>
      </ControlTemplate>
    </Setter.Value></Setter>
  </Style>
  <Style x:Key='KPrimary' TargetType='Button'>
    <Setter Property='Foreground' Value='#FFFFFFFF'/>
    <Setter Property='Padding' Value='18,7'/>
    <Setter Property='MinWidth' Value='96'/>
    <Setter Property='Cursor' Value='Hand'/>
    <Setter Property='FontWeight' Value='SemiBold'/>
    <Setter Property='FocusVisualStyle' Value='{x:Null}'/>
    <Setter Property='Template'><Setter.Value>
      <ControlTemplate TargetType='Button'>
        <Border x:Name='b' CornerRadius='6' Background='{ACCENT}' BorderBrush='{ACCENT}' BorderThickness='1' Padding='{TemplateBinding Padding}'>
          <ContentPresenter HorizontalAlignment='Center' VerticalAlignment='Center'/>
        </Border>
        <ControlTemplate.Triggers>
          <Trigger Property='IsMouseOver' Value='True'><Setter TargetName='b' Property='Opacity' Value='0.88'/></Trigger>
          <Trigger Property='IsPressed' Value='True'><Setter TargetName='b' Property='Opacity' Value='0.75'/></Trigger>
        </ControlTemplate.Triggers>
      </ControlTemplate>
    </Setter.Value></Setter>
  </Style>
  <Style x:Key='KClose' TargetType='Button'>
    <Setter Property='Foreground' Value='{MUTED}'/>
    <Setter Property='Cursor' Value='Hand'/>
    <Setter Property='FocusVisualStyle' Value='{x:Null}'/>
    <Setter Property='Template'><Setter.Value>
      <ControlTemplate TargetType='Button'>
        <Border x:Name='b' CornerRadius='6' Background='Transparent' Width='28' Height='28'>
          <ContentPresenter HorizontalAlignment='Center' VerticalAlignment='Center'/>
        </Border>
        <ControlTemplate.Triggers>
          <Trigger Property='IsMouseOver' Value='True'><Setter TargetName='b' Property='Background' Value='{HOVER}'/></Trigger>
        </ControlTemplate.Triggers>
      </ControlTemplate>
    </Setter.Value></Setter>
  </Style>
  <Style x:Key='KCheck' TargetType='CheckBox'>
    <Setter Property='Foreground' Value='{FG}'/>
    <Setter Property='Cursor' Value='Hand'/>
    <Setter Property='FocusVisualStyle' Value='{x:Null}'/>
    <Setter Property='Template'><Setter.Value>
      <ControlTemplate TargetType='CheckBox'>
        <Grid Background='Transparent'>
          <Grid.ColumnDefinitions><ColumnDefinition Width='Auto'/><ColumnDefinition Width='*'/></Grid.ColumnDefinitions>
          <Border x:Name='box' Width='18' Height='18' CornerRadius='4' BorderThickness='1.5' BorderBrush='{BORDER}' Background='{PANEL}' VerticalAlignment='Top' Margin='0,1,0,0'>
            <Path x:Name='mark' Data='M3.5,9 L7.5,12.5 L14,5' Stroke='#FFFFFFFF' StrokeThickness='2' StrokeStartLineCap='Round' StrokeEndLineCap='Round' StrokeLineJoin='Round' Visibility='Collapsed' Margin='-1,-1,0,0'/>
          </Border>
          <ContentPresenter Grid.Column='1' Margin='10,0,0,0' VerticalAlignment='Center'/>
        </Grid>
        <ControlTemplate.Triggers>
          <Trigger Property='IsChecked' Value='True'>
            <Setter TargetName='box' Property='Background' Value='{ACCENT}'/>
            <Setter TargetName='box' Property='BorderBrush' Value='{ACCENT}'/>
            <Setter TargetName='mark' Property='Visibility' Value='Visible'/>
          </Trigger>
          <Trigger Property='IsMouseOver' Value='True'><Setter TargetName='box' Property='BorderBrush' Value='{ACCENT}'/></Trigger>
          <Trigger Property='IsKeyboardFocused' Value='True'><Setter TargetName='box' Property='BorderBrush' Value='{ACCENT}'/></Trigger>
        </ControlTemplate.Triggers>
      </ControlTemplate>
    </Setter.Value></Setter>
  </Style>
  <Style x:Key='KText' TargetType='TextBox'>
    <Setter Property='Foreground' Value='{FG}'/>
    <Setter Property='CaretBrush' Value='{FG}'/>
    <Setter Property='SelectionBrush' Value='{ACCENT}'/>
    <Setter Property='Padding' Value='8,6'/>
    <Setter Property='FontSize' Value='14'/>
    <Setter Property='Template'><Setter.Value>
      <ControlTemplate TargetType='TextBox'>
        <Border x:Name='b' CornerRadius='6' Background='{PANEL}' BorderBrush='{BORDER}' BorderThickness='1'>
          <ScrollViewer x:Name='PART_ContentHost' Margin='{TemplateBinding Padding}'/>
        </Border>
        <ControlTemplate.Triggers>
          <Trigger Property='IsKeyboardFocused' Value='True'><Setter TargetName='b' Property='BorderBrush' Value='{ACCENT}'/></Trigger>
        </ControlTemplate.Triggers>
      </ControlTemplate>
    </Setter.Value></Setter>
  </Style>
  <Style x:Key='KList' TargetType='ListBox'>
    <Setter Property='Foreground' Value='{FG}'/>
    <Setter Property='Background' Value='{PANEL}'/>
    <Setter Property='BorderBrush' Value='{BORDER}'/>
    <Setter Property='BorderThickness' Value='1'/>
    <Setter Property='Padding' Value='4'/>
    <Setter Property='ScrollViewer.HorizontalScrollBarVisibility' Value='Disabled'/>
    <Setter Property='Template'><Setter.Value>
      <ControlTemplate TargetType='ListBox'>
        <Border CornerRadius='6' Background='{TemplateBinding Background}' BorderBrush='{TemplateBinding BorderBrush}' BorderThickness='{TemplateBinding BorderThickness}' Padding='{TemplateBinding Padding}'>
          <ScrollViewer Focusable='False'><ItemsPresenter/></ScrollViewer>
        </Border>
      </ControlTemplate>
    </Setter.Value></Setter>
    <Setter Property='ItemContainerStyle'><Setter.Value>
      <Style TargetType='ListBoxItem'>
        <Setter Property='Foreground' Value='{FG}'/>
        <Setter Property='Cursor' Value='Hand'/>
        <Setter Property='FocusVisualStyle' Value='{x:Null}'/>
        <Setter Property='Template'><Setter.Value>
          <ControlTemplate TargetType='ListBoxItem'>
            <Border x:Name='b' CornerRadius='4' Padding='10,6' Background='Transparent'><ContentPresenter/></Border>
            <ControlTemplate.Triggers>
              <Trigger Property='IsMouseOver' Value='True'><Setter TargetName='b' Property='Background' Value='{HOVER}'/></Trigger>
              <Trigger Property='IsSelected' Value='True'><Setter TargetName='b' Property='Background' Value='{ACCENTSOFT}'/></Trigger>
            </ControlTemplate.Triggers>
          </ControlTemplate>
        </Setter.Value></Setter>
      </Style>
    </Setter.Value></Setter>
  </Style>
</ResourceDictionary>";

        private static ResourceDictionary Styles(Palette p)
        {
            string x = StylesXaml
                .Replace("{FG}", Hex(p.Fg)).Replace("{PANEL}", Hex(p.Panel)).Replace("{BORDER}", Hex(p.Border))
                .Replace("{HOVER}", Hex(p.Hover)).Replace("{ACCENTSOFT}", Hex(p.AccentSoft)).Replace("{ACCENT}", Hex(p.Accent))
                .Replace("{MUTED}", Hex(p.Muted));
            return (ResourceDictionary)XamlReader.Parse(x);
        }

        // ---- 枠 ----

        /// <summary>ダイアログ 1 つ分の部品。Body に中身を足し、Footer の左に補足(チェックなど)を置き、ボタンを足してから Show する。</summary>
        internal sealed class Frame
        {
            public Window Window;
            public StackPanel Body;
            public DockPanel Footer;
            public StackPanel Buttons;
            public Palette P;
            public ResourceDictionary Res;

            public Button AddButton(string text, bool primary, bool isDefault, bool isCancel, Action onClick)
            {
                var b = new Button { Content = text, IsDefault = isDefault, IsCancel = isCancel, Margin = new Thickness(8, 0, 0, 0) };
                b.Style = (Style)Res[primary ? "KPrimary" : "KButton"];
                if (onClick != null) b.Click += (s, e) => onClick();
                Buttons.Children.Add(b);
                return b;
            }

            public CheckBox Check(object content, bool isChecked)
            {
                return new CheckBox { Content = content, IsChecked = isChecked, Style = (Style)Res["KCheck"] };
            }

            public TextBlock Text(string s, double size = 13, double opacity = 1, bool wrap = true)
            {
                return new TextBlock { Text = s, FontSize = size, Opacity = opacity, Foreground = new SolidColorBrush(P.Fg), TextWrapping = wrap ? TextWrapping.Wrap : TextWrapping.NoWrap };
            }

            /// <summary>「A.h → B.h」のような、等幅の小さな箱。</summary>
            public Border Code(string s)
            {
                return new Border
                {
                    CornerRadius = new CornerRadius(6),
                    Background = new SolidColorBrush(P.Panel),
                    Padding = new Thickness(10, 6, 10, 6),
                    Child = new TextBlock { Text = s, FontFamily = new FontFamily("Cascadia Mono, Consolas"), FontSize = 12, Foreground = new SolidColorBrush(P.Fg), Opacity = 0.9, TextWrapping = TextWrapping.Wrap },
                };
            }

            public void Show()
            {
                try { Owner(Window); } catch (Exception swallowed) { Safe.Ignore(swallowed); }
                Window.ShowDialog();
            }
        }

        private static void Owner(Window w)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var shell = Package.GetGlobalService(typeof(SVsUIShell)) as IVsUIShell;
            IntPtr hwnd;
            if (shell != null && shell.GetDialogOwnerHwnd(out hwnd) == 0 && hwnd != IntPtr.Zero)
            {
                new WindowInteropHelper(w).Owner = hwnd;
                w.WindowStartupLocation = WindowStartupLocation.CenterOwner;
                w.Topmost = false;
            }
        }

        /// <summary>見出し(title)と、その下の小さな文(subtitle、null なら出さない)の枠を作る。</summary>
        public static Frame Create(string title, string subtitle, double width = 480)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            title = L.T(title);
            var f = new Frame { P = Colors() };
            f.Res = Styles(f.P);
            var p = f.P;

            var root = new StackPanel { Margin = new Thickness(24, 18, 24, 20), Width = width };

            // 見出しの行: 左に「K-Cpp」と見出し、右に閉じるボタン
            var head = new DockPanel { LastChildFill = true };
            var close = new Button { Content = new TextBlock { Text = "✕", FontSize = 12 }, Style = (Style)f.Res["KClose"], VerticalAlignment = VerticalAlignment.Top };
            DockPanel.SetDock(close, Dock.Right);
            head.Children.Add(close);
            var titles = new StackPanel();
            var brand = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(0, 0, 0, 6) };
            brand.Children.Add(new Border { Width = 8, Height = 8, CornerRadius = new CornerRadius(4), Background = new SolidColorBrush(p.Accent), VerticalAlignment = VerticalAlignment.Center, Margin = new Thickness(0, 0, 8, 0) });
            brand.Children.Add(new TextBlock { Text = "K-Cpp", FontSize = 11, Foreground = new SolidColorBrush(p.Muted) });
            titles.Children.Add(brand);
            titles.Children.Add(new TextBlock { Text = title, FontSize = 17, FontWeight = FontWeights.SemiBold, Foreground = new SolidColorBrush(p.Fg), TextWrapping = TextWrapping.Wrap });
            head.Children.Add(titles);
            root.Children.Add(head);
            if (!string.IsNullOrEmpty(subtitle))
            {
                var sub = f.Code(subtitle);
                sub.Margin = new Thickness(0, 10, 0, 0);
                sub.HorizontalAlignment = HorizontalAlignment.Left;
                root.Children.Add(sub);
            }

            f.Body = new StackPanel { Margin = new Thickness(0, 14, 0, 0) };
            root.Children.Add(f.Body);

            f.Footer = new DockPanel { LastChildFill = false, Margin = new Thickness(0, 20, 0, 0) };
            f.Buttons = new StackPanel { Orientation = Orientation.Horizontal };
            DockPanel.SetDock(f.Buttons, Dock.Right);
            f.Footer.Children.Add(f.Buttons);
            root.Children.Add(f.Footer);

            var card = new Border
            {
                CornerRadius = new CornerRadius(10),
                Background = new SolidColorBrush(p.Bg),
                BorderBrush = new SolidColorBrush(p.Border),
                BorderThickness = new Thickness(1),
                Margin = new Thickness(18),             // 影の分のすき間
                Effect = new DropShadowEffect { BlurRadius = 28, ShadowDepth = 6, Direction = 270, Opacity = p.Dark ? 0.55 : 0.25, Color = System.Windows.Media.Colors.Black },
                Child = root,
            };

            var w = new Window
            {
                Title = "K-Cpp",
                Content = card,
                WindowStyle = WindowStyle.None,
                AllowsTransparency = true,
                Background = Brushes.Transparent,
                ResizeMode = ResizeMode.NoResize,
                SizeToContent = SizeToContent.WidthAndHeight,
                WindowStartupLocation = WindowStartupLocation.CenterScreen,
                ShowInTaskbar = false,
                Topmost = true,
                FontFamily = new FontFamily("Segoe UI, Yu Gothic UI, Meiryo UI"),
            };
            TextOptions.SetTextFormattingMode(w, TextFormattingMode.Display);
            w.Resources.MergedDictionaries.Add(f.Res);
            // 枠のどこをつかんでも動かせる(ボタンや入力欄の上は、それぞれの操作が先)
            card.MouseLeftButtonDown += (s, e) => { try { if (e.ButtonState == MouseButtonState.Pressed) w.DragMove(); } catch (Exception swallowed) { Safe.Ignore(swallowed); } };
            close.Click += (s, e) => w.Close();
            w.KeyDown += (s, e) => { if (e.Key == Key.Escape) w.Close(); };
            f.Window = w;
            return f;
        }

        // ---- よく使う形 ----

        /// <summary>はい・いいえを聞く。message は本文、detail は等幅の箱で見せる一覧(null なら出さない)。</summary>
        public static bool Confirm(string title, string message, string detail, string okText = "実行する", string cancelText = "やめる")
        {
            var f = Create(title, null);
            f.Body.Children.Add(f.Text(message, 13, 0.85));
            if (!string.IsNullOrEmpty(detail))
            {
                var box = f.Code(detail);
                box.Margin = new Thickness(0, 12, 0, 0);
                var scroll = new ScrollViewer { Content = box, MaxHeight = 260, VerticalScrollBarVisibility = ScrollBarVisibility.Auto };
                f.Body.Children.Add(scroll);
            }
            bool ok = false;
            var yes = f.AddButton(L.T(okText), true, true, false, () => { ok = true; f.Window.Close(); });
            f.AddButton(L.T(cancelText), false, false, true, () => f.Window.Close());
            f.Window.Loaded += (s, e) => yes.Focus();
            f.Show();
            return ok;
        }

        /// <summary>1 行の入力欄。キャンセルなら null。</summary>
        public static string Input(string title, string message, string initial, string okText = "OK")
        {
            var f = Create(title, null);
            if (!string.IsNullOrEmpty(message)) f.Body.Children.Add(f.Text(message, 13, 0.85));
            var box = new TextBox { Text = initial ?? "", Style = (Style)f.Res["KText"], Margin = new Thickness(0, 12, 0, 0) };
            f.Body.Children.Add(box);
            string result = null;
            f.AddButton(L.T(okText), true, true, false, () => { result = box.Text; f.Window.Close(); });
            f.AddButton(L.T("やめる"), false, false, true, () => f.Window.Close());
            f.Window.Loaded += (s, e) => { box.Focus(); box.SelectAll(); };
            f.Show();
            return result;
        }

        /// <summary>一覧から 1 つ選ぶ。キャンセルなら null。</summary>
        public static string Choose(string title, string message, IList<string> items)
        {
            var f = Create(title, null);
            if (!string.IsNullOrEmpty(message)) f.Body.Children.Add(f.Text(message, 13, 0.85));
            var list = new ListBox { Style = (Style)f.Res["KList"], Margin = new Thickness(0, 12, 0, 0), MaxHeight = 280 };
            foreach (string s in items) list.Items.Add(new TextBlock { Text = s, FontFamily = new FontFamily("Cascadia Mono, Consolas"), FontSize = 12, Tag = s, TextWrapping = TextWrapping.Wrap });
            list.SelectedIndex = 0;
            f.Body.Children.Add(list);
            string result = null;
            Action pick = () => { var t = list.SelectedItem as TextBlock; if (t != null) { result = (string)t.Tag; f.Window.Close(); } };
            f.AddButton(L.T("選ぶ"), true, true, false, pick);
            f.AddButton(L.T("やめる"), false, false, true, () => f.Window.Close());
            list.MouseDoubleClick += (s, e) => pick();
            f.Window.Loaded += (s, e) => { list.Focus(); var c = list.ItemContainerGenerator.ContainerFromIndex(0) as ListBoxItem; if (c != null) c.Focus(); };
            f.Show();
            return result;
        }
    }
}
