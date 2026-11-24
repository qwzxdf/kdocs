using System;
using System.Windows;
using System.Windows.Markup;
using System.Windows.Media;
using KCppAssist.ErrorLog;

namespace KCppAssist.Vcpkg
{
    /// <summary>
    /// K-vcpkg の窓の見た目(Fluent 風: 角丸・ふわっとした面・アクセント色)。
    /// 部品の形は XAML の文字列で定義して、色は DynamicResource の名前で引く。色は VS のテーマ(ダーク / ライト)から作り直せる。
    /// </summary>
    internal static class FluentStyles
    {
        public const string Xaml = @"
<ResourceDictionary xmlns='http://schemas.microsoft.com/winfx/2006/xaml/presentation' xmlns:x='http://schemas.microsoft.com/winfx/2006/xaml'>

  <!-- ボタン(標準) -->
  <Style x:Key='FButton' TargetType='Button'>
    <Setter Property='Foreground' Value='{DynamicResource TextBrush}'/>
    <Setter Property='Background' Value='{DynamicResource CardBrush}'/>
    <Setter Property='BorderBrush' Value='{DynamicResource LineBrush}'/>
    <Setter Property='BorderThickness' Value='1'/>
    <Setter Property='Padding' Value='14,6'/>
    <Setter Property='Margin' Value='0,0,8,6'/>
    <Setter Property='Cursor' Value='Hand'/>
    <Setter Property='FocusVisualStyle' Value='{x:Null}'/>
    <Setter Property='Template'>
      <Setter.Value>
        <ControlTemplate TargetType='Button'>
          <Border x:Name='b' Background='{TemplateBinding Background}' BorderBrush='{TemplateBinding BorderBrush}' BorderThickness='{TemplateBinding BorderThickness}' CornerRadius='5' Padding='{TemplateBinding Padding}'>
            <ContentPresenter HorizontalAlignment='Center' VerticalAlignment='Center' RecognizesAccessKey='False'/>
          </Border>
          <ControlTemplate.Triggers>
            <Trigger Property='IsMouseOver' Value='True'><Setter TargetName='b' Property='Background' Value='{DynamicResource HoverBrush}'/></Trigger>
            <Trigger Property='IsPressed' Value='True'><Setter TargetName='b' Property='Background' Value='{DynamicResource PressBrush}'/></Trigger>
            <Trigger Property='IsEnabled' Value='False'><Setter Property='Opacity' Value='0.4'/></Trigger>
          </ControlTemplate.Triggers>
        </ControlTemplate>
      </Setter.Value>
    </Setter>
  </Style>

  <!-- ボタン(主な操作。アクセント色) -->
  <Style x:Key='FPrimary' TargetType='Button'>
    <Setter Property='Foreground' Value='{DynamicResource AccentFgBrush}'/>
    <Setter Property='Background' Value='{DynamicResource AccentBrush}'/>
    <Setter Property='BorderThickness' Value='0'/>
    <Setter Property='Padding' Value='16,6'/>
    <Setter Property='Margin' Value='0,0,8,6'/>
    <Setter Property='FontWeight' Value='SemiBold'/>
    <Setter Property='Cursor' Value='Hand'/>
    <Setter Property='FocusVisualStyle' Value='{x:Null}'/>
    <Setter Property='Template'>
      <Setter.Value>
        <ControlTemplate TargetType='Button'>
          <Border x:Name='b' Background='{TemplateBinding Background}' CornerRadius='5' Padding='{TemplateBinding Padding}'>
            <ContentPresenter HorizontalAlignment='Center' VerticalAlignment='Center' RecognizesAccessKey='False'/>
          </Border>
          <ControlTemplate.Triggers>
            <Trigger Property='IsMouseOver' Value='True'><Setter TargetName='b' Property='Background' Value='{DynamicResource AccentHoverBrush}'/></Trigger>
            <Trigger Property='IsPressed' Value='True'><Setter TargetName='b' Property='Opacity' Value='0.8'/></Trigger>
            <Trigger Property='IsEnabled' Value='False'><Setter Property='Opacity' Value='0.4'/></Trigger>
          </ControlTemplate.Triggers>
        </ControlTemplate>
      </Setter.Value>
    </Setter>
  </Style>

  <!-- 絞り込みのチップ(選ぶと、アクセント色になる) -->
  <Style x:Key='FChip' TargetType='ToggleButton'>
    <Setter Property='Foreground' Value='{DynamicResource TextBrush}'/>
    <Setter Property='Margin' Value='0,0,6,6'/>
    <Setter Property='Padding' Value='11,3'/>
    <Setter Property='Cursor' Value='Hand'/>
    <Setter Property='FocusVisualStyle' Value='{x:Null}'/>
    <Setter Property='Template'>
      <Setter.Value>
        <ControlTemplate TargetType='ToggleButton'>
          <Border x:Name='b' Background='{DynamicResource CardBrush}' BorderBrush='{DynamicResource LineBrush}' BorderThickness='1' CornerRadius='13' Padding='{TemplateBinding Padding}'>
            <ContentPresenter x:Name='c' HorizontalAlignment='Center' VerticalAlignment='Center'/>
          </Border>
          <ControlTemplate.Triggers>
            <Trigger Property='IsMouseOver' Value='True'><Setter TargetName='b' Property='Background' Value='{DynamicResource HoverBrush}'/></Trigger>
            <Trigger Property='IsChecked' Value='True'>
              <Setter TargetName='b' Property='Background' Value='{DynamicResource AccentBrush}'/>
              <Setter TargetName='b' Property='BorderBrush' Value='{DynamicResource AccentBrush}'/>
              <Setter Property='Foreground' Value='{DynamicResource AccentFgBrush}'/>
            </Trigger>
          </ControlTemplate.Triggers>
        </ControlTemplate>
      </Setter.Value>
    </Setter>
  </Style>

  <!-- 入力欄 -->
  <Style x:Key='FTextBox' TargetType='TextBox'>
    <Setter Property='Foreground' Value='{DynamicResource TextBrush}'/>
    <Setter Property='Background' Value='{DynamicResource CardBrush}'/>
    <Setter Property='BorderBrush' Value='{DynamicResource LineBrush}'/>
    <Setter Property='CaretBrush' Value='{DynamicResource TextBrush}'/>
    <Setter Property='Padding' Value='8,6'/>
    <Setter Property='FocusVisualStyle' Value='{x:Null}'/>
    <Setter Property='Template'>
      <Setter.Value>
        <ControlTemplate TargetType='TextBox'>
          <Border x:Name='b' Background='{TemplateBinding Background}' BorderBrush='{TemplateBinding BorderBrush}' BorderThickness='1' CornerRadius='5'>
            <ScrollViewer x:Name='PART_ContentHost' Margin='{TemplateBinding Padding}' VerticalAlignment='Center'/>
          </Border>
          <ControlTemplate.Triggers>
            <Trigger Property='IsKeyboardFocused' Value='True'><Setter TargetName='b' Property='BorderBrush' Value='{DynamicResource AccentBrush}'/></Trigger>
            <Trigger Property='IsEnabled' Value='False'><Setter Property='Opacity' Value='0.5'/></Trigger>
          </ControlTemplate.Triggers>
        </ControlTemplate>
      </Setter.Value>
    </Setter>
  </Style>

  <Style x:Key='FComboItem' TargetType='ComboBoxItem'>
    <Setter Property='Foreground' Value='{DynamicResource TextBrush}'/>
    <Setter Property='Padding' Value='10,6'/>
    <Setter Property='Template'>
      <Setter.Value>
        <ControlTemplate TargetType='ComboBoxItem'>
          <Border x:Name='b' Background='Transparent' CornerRadius='4' Margin='3,1' Padding='{TemplateBinding Padding}'>
            <ContentPresenter/>
          </Border>
          <ControlTemplate.Triggers>
            <Trigger Property='IsHighlighted' Value='True'><Setter TargetName='b' Property='Background' Value='{DynamicResource HoverBrush}'/></Trigger>
            <Trigger Property='IsSelected' Value='True'><Setter TargetName='b' Property='Background' Value='{DynamicResource SelectBrush}'/></Trigger>
          </ControlTemplate.Triggers>
        </ControlTemplate>
      </Setter.Value>
    </Setter>
  </Style>

  <!-- コンボ ボックス -->
  <Style x:Key='FCombo' TargetType='ComboBox'>
    <Setter Property='Foreground' Value='{DynamicResource TextBrush}'/>
    <Setter Property='ItemContainerStyle' Value='{StaticResource FComboItem}'/>
    <Setter Property='FocusVisualStyle' Value='{x:Null}'/>
    <Setter Property='Template'>
      <Setter.Value>
        <ControlTemplate TargetType='ComboBox'>
          <Grid>
            <ToggleButton x:Name='tb' Focusable='False' ClickMode='Press' IsChecked='{Binding IsDropDownOpen, Mode=TwoWay, RelativeSource={RelativeSource TemplatedParent}}'>
              <ToggleButton.Template>
                <ControlTemplate TargetType='ToggleButton'>
                  <Border x:Name='bd' Background='{DynamicResource CardBrush}' BorderBrush='{DynamicResource LineBrush}' BorderThickness='1' CornerRadius='5'>
                    <Path Data='M0,0 L4,4 L8,0' Stroke='{DynamicResource SubBrush}' StrokeThickness='1.5' Margin='0,0,11,0' HorizontalAlignment='Right' VerticalAlignment='Center'/>
                  </Border>
                  <ControlTemplate.Triggers>
                    <Trigger Property='IsMouseOver' Value='True'><Setter TargetName='bd' Property='Background' Value='{DynamicResource HoverBrush}'/></Trigger>
                  </ControlTemplate.Triggers>
                </ControlTemplate>
              </ToggleButton.Template>
            </ToggleButton>
            <ContentPresenter IsHitTestVisible='False' Margin='11,6,30,6' VerticalAlignment='Center' HorizontalAlignment='Left' Content='{TemplateBinding SelectionBoxItem}' ContentTemplate='{TemplateBinding SelectionBoxItemTemplate}'/>
            <Popup IsOpen='{TemplateBinding IsDropDownOpen}' Placement='Bottom' AllowsTransparency='True' Focusable='False' PopupAnimation='Fade'>
              <Border MinWidth='{TemplateBinding ActualWidth}' MaxHeight='{TemplateBinding MaxDropDownHeight}' Background='{DynamicResource CardBrush}' BorderBrush='{DynamicResource LineBrush}' BorderThickness='1' CornerRadius='6' Margin='0,3,8,10' Padding='0,4'>
                <Border.Effect><DropShadowEffect BlurRadius='10' ShadowDepth='2' Opacity='0.35'/></Border.Effect>
                <ScrollViewer><StackPanel IsItemsHost='True'/></ScrollViewer>
              </Border>
            </Popup>
          </Grid>
        </ControlTemplate>
      </Setter.Value>
    </Setter>
  </Style>

  <!-- チェック ボックス -->
  <Style x:Key='FCheck' TargetType='CheckBox'>
    <Setter Property='Foreground' Value='{DynamicResource TextBrush}'/>
    <Setter Property='Margin' Value='0,3,0,0'/>
    <Setter Property='Cursor' Value='Hand'/>
    <Setter Property='FocusVisualStyle' Value='{x:Null}'/>
    <Setter Property='Template'>
      <Setter.Value>
        <ControlTemplate TargetType='CheckBox'>
          <StackPanel Orientation='Horizontal' Background='Transparent'>
            <Border x:Name='box' Width='18' Height='18' CornerRadius='4' BorderThickness='1' BorderBrush='{DynamicResource SubBrush}' Background='Transparent' VerticalAlignment='Top' Margin='0,1,9,0'>
              <Path x:Name='mark' Data='M3.5,9 L7.5,13 L14.5,5' Stroke='{DynamicResource AccentFgBrush}' StrokeThickness='2' StrokeStartLineCap='Round' StrokeEndLineCap='Round' StrokeLineJoin='Round' Visibility='Collapsed'/>
            </Border>
            <ContentPresenter VerticalAlignment='Top' MaxWidth='520'/>
          </StackPanel>
          <ControlTemplate.Triggers>
            <Trigger Property='IsChecked' Value='True'>
              <Setter TargetName='box' Property='Background' Value='{DynamicResource AccentBrush}'/>
              <Setter TargetName='box' Property='BorderBrush' Value='{DynamicResource AccentBrush}'/>
              <Setter TargetName='mark' Property='Visibility' Value='Visible'/>
            </Trigger>
            <Trigger Property='IsMouseOver' Value='True'><Setter TargetName='box' Property='BorderBrush' Value='{DynamicResource AccentBrush}'/></Trigger>
            <Trigger Property='IsEnabled' Value='False'><Setter Property='Opacity' Value='0.5'/></Trigger>
          </ControlTemplate.Triggers>
        </ControlTemplate>
      </Setter.Value>
    </Setter>
  </Style>

  <!-- 一覧の行 -->
  <Style x:Key='FListItem' TargetType='ListBoxItem'>
    <Setter Property='Foreground' Value='{DynamicResource TextBrush}'/>
    <Setter Property='Padding' Value='10,8'/>
    <Setter Property='Margin' Value='0,0,0,2'/>
    <Setter Property='HorizontalContentAlignment' Value='Stretch'/>
    <Setter Property='FocusVisualStyle' Value='{x:Null}'/>
    <Setter Property='Template'>
      <Setter.Value>
        <ControlTemplate TargetType='ListBoxItem'>
          <Grid>
            <Border x:Name='bd' Background='Transparent' CornerRadius='6' Padding='{TemplateBinding Padding}'>
              <ContentPresenter/>
            </Border>
            <Border x:Name='bar' Width='3' Height='18' CornerRadius='2' Background='{DynamicResource AccentBrush}' HorizontalAlignment='Left' VerticalAlignment='Center' Margin='1,0,0,0' Visibility='Collapsed'/>
          </Grid>
          <ControlTemplate.Triggers>
            <Trigger Property='IsMouseOver' Value='True'><Setter TargetName='bd' Property='Background' Value='{DynamicResource HoverBrush}'/></Trigger>
            <Trigger Property='IsSelected' Value='True'>
              <Setter TargetName='bd' Property='Background' Value='{DynamicResource SelectBrush}'/>
              <Setter TargetName='bar' Property='Visibility' Value='Visible'/>
            </Trigger>
          </ControlTemplate.Triggers>
        </ControlTemplate>
      </Setter.Value>
    </Setter>
  </Style>

  <Style x:Key='FList' TargetType='ListBox'>
    <Setter Property='Background' Value='Transparent'/>
    <Setter Property='BorderThickness' Value='0'/>
    <Setter Property='Foreground' Value='{DynamicResource TextBrush}'/>
    <Setter Property='ItemContainerStyle' Value='{StaticResource FListItem}'/>
    <Setter Property='ScrollViewer.HorizontalScrollBarVisibility' Value='Disabled'/>
    <Setter Property='HorizontalContentAlignment' Value='Stretch'/>
  </Style>

  <!-- タブ(見出しの下に、アクセント色の線) -->
  <Style x:Key='FTabItem' TargetType='TabItem'>
    <Setter Property='Foreground' Value='{DynamicResource SubBrush}'/>
    <Setter Property='FontSize' Value='14'/>
    <Setter Property='Padding' Value='4,6'/>
    <Setter Property='Margin' Value='0,0,18,0'/>
    <Setter Property='Cursor' Value='Hand'/>
    <Setter Property='FocusVisualStyle' Value='{x:Null}'/>
    <Setter Property='Template'>
      <Setter.Value>
        <ControlTemplate TargetType='TabItem'>
          <Border x:Name='b' BorderThickness='0,0,0,3' BorderBrush='Transparent' Padding='{TemplateBinding Padding}' Background='Transparent'>
            <ContentPresenter ContentSource='Header' HorizontalAlignment='Center'/>
          </Border>
          <ControlTemplate.Triggers>
            <Trigger Property='IsMouseOver' Value='True'><Setter Property='Foreground' Value='{DynamicResource TextBrush}'/></Trigger>
            <Trigger Property='IsSelected' Value='True'>
              <Setter Property='Foreground' Value='{DynamicResource TextBrush}'/>
              <Setter Property='FontWeight' Value='SemiBold'/>
              <Setter TargetName='b' Property='BorderBrush' Value='{DynamicResource AccentBrush}'/>
            </Trigger>
          </ControlTemplate.Triggers>
        </ControlTemplate>
      </Setter.Value>
    </Setter>
  </Style>

  <Style x:Key='FTabs' TargetType='TabControl'>
    <Setter Property='Background' Value='Transparent'/>
    <Setter Property='BorderThickness' Value='0'/>
    <Setter Property='Padding' Value='0'/>
    <Setter Property='ItemContainerStyle' Value='{StaticResource FTabItem}'/>
    <Setter Property='Template'>
      <Setter.Value>
        <ControlTemplate TargetType='TabControl'>
          <Grid>
            <Grid.RowDefinitions><RowDefinition Height='Auto'/><RowDefinition Height='*'/></Grid.RowDefinitions>
            <Border BorderThickness='0,0,0,1' BorderBrush='{DynamicResource LineBrush}' Margin='0,0,0,10'>
              <StackPanel IsItemsHost='True' Orientation='Horizontal' Margin='2,0,0,-1'/>
            </Border>
            <ContentPresenter Grid.Row='1' ContentSource='SelectedContent'/>
          </Grid>
        </ControlTemplate>
      </Setter.Value>
    </Setter>
  </Style>

  <!-- 細いスクロール バー -->
  <Style TargetType='ScrollBar'>
    <Setter Property='Background' Value='Transparent'/>
    <Setter Property='Width' Value='10'/>
    <Setter Property='Template'>
      <Setter.Value>
        <ControlTemplate TargetType='ScrollBar'>
          <Grid Background='Transparent'>
            <Track x:Name='PART_Track' IsDirectionReversed='True'>
              <Track.DecreaseRepeatButton><RepeatButton Command='ScrollBar.PageUpCommand' Opacity='0' IsTabStop='False'/></Track.DecreaseRepeatButton>
              <Track.IncreaseRepeatButton><RepeatButton Command='ScrollBar.PageDownCommand' Opacity='0' IsTabStop='False'/></Track.IncreaseRepeatButton>
              <Track.Thumb>
                <Thumb>
                  <Thumb.Template>
                    <ControlTemplate TargetType='Thumb'>
                      <Border Background='{DynamicResource ThumbBrush}' CornerRadius='4' Margin='2,0'/>
                    </ControlTemplate>
                  </Thumb.Template>
                </Thumb>
              </Track.Thumb>
            </Track>
          </Grid>
        </ControlTemplate>
      </Setter.Value>
    </Setter>
    <Style.Triggers>
      <Trigger Property='Orientation' Value='Horizontal'>
        <Setter Property='Width' Value='Auto'/>
        <Setter Property='Height' Value='10'/>
        <Setter Property='Template'>
          <Setter.Value>
            <ControlTemplate TargetType='ScrollBar'>
              <Grid Background='Transparent'>
                <Track x:Name='PART_Track'>
                  <Track.DecreaseRepeatButton><RepeatButton Command='ScrollBar.PageLeftCommand' Opacity='0' IsTabStop='False'/></Track.DecreaseRepeatButton>
                  <Track.IncreaseRepeatButton><RepeatButton Command='ScrollBar.PageRightCommand' Opacity='0' IsTabStop='False'/></Track.IncreaseRepeatButton>
                  <Track.Thumb>
                    <Thumb>
                      <Thumb.Template>
                        <ControlTemplate TargetType='Thumb'>
                          <Border Background='{DynamicResource ThumbBrush}' CornerRadius='4' Margin='0,2'/>
                        </ControlTemplate>
                      </Thumb.Template>
                    </Thumb>
                  </Track.Thumb>
                </Track>
              </Grid>
            </ControlTemplate>
          </Setter.Value>
        </Setter>
      </Trigger>
    </Style.Triggers>
  </Style>
</ResourceDictionary>";

        private static ResourceDictionary _styles;

        /// <summary>部品の形(XAML)から作った辞書。1 回だけ読み込む。</summary>
        public static ResourceDictionary Styles
        {
            get { return _styles ?? (_styles = (ResourceDictionary)XamlReader.Parse(Xaml)); }
        }

        /// <summary>VS のテーマの色から、窓で使う色(辞書のキー)を作り直す。</summary>
        public static void ApplyColors(ResourceDictionary res)
        {
            Color back = Theme.Background, fore = Theme.Foreground;
            bool dark = Theme.IsDark;
            Color accent = dark ? Color.FromRgb(0x4C, 0xA8, 0xFF) : Color.FromRgb(0x00, 0x67, 0xC0);
            Color accentHover = dark ? Color.FromRgb(0x6B, 0xB9, 0xFF) : Color.FromRgb(0x00, 0x55, 0xA3);
            Color accentFg = dark ? Color.FromRgb(0x10, 0x10, 0x10) : Colors.White;
            Color card = Mix(back, fore, 0.06);                       // 背景に、文字色を少し混ぜると、面が浮いて見える
            Set(res, "BackBrush", back);
            Set(res, "TextBrush", fore);
            Set(res, "SubBrush", Mix(back, fore, 0.62));
            Set(res, "CardBrush", card);
            Set(res, "HoverBrush", Mix(back, fore, 0.12));
            Set(res, "PressBrush", Mix(back, fore, 0.18));
            Set(res, "LineBrush", Mix(back, fore, 0.2));
            Set(res, "ThumbBrush", Mix(back, fore, 0.35));
            Set(res, "AccentBrush", accent);
            Set(res, "AccentHoverBrush", accentHover);
            Set(res, "AccentFgBrush", accentFg);
            Set(res, "SelectBrush", Color.FromArgb(0x38, accent.R, accent.G, accent.B));
            Set(res, "OkBrush", dark ? Color.FromRgb(0x6C, 0xCB, 0x5F) : Color.FromRgb(0x0F, 0x7B, 0x0F));
            Set(res, "WarnBrush", dark ? Color.FromRgb(0xFC, 0xE1, 0x00) : Color.FromRgb(0x9D, 0x5D, 0x00));
        }

        private static void Set(ResourceDictionary res, string key, Color c)
        {
            res[key] = new SolidColorBrush(c);
        }

        private static Color Mix(Color a, Color b, double t)
        {
            return Color.FromRgb((byte)(a.R + (b.R - a.R) * t), (byte)(a.G + (b.G - a.G) * t), (byte)(a.B + (b.B - a.B) * t));
        }
    }
}
