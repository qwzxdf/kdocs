---
title: 第 22 章 コードビハインドを減らす（Behaviors）
tags:
  - C#連携
---

# 第 22 章 コードビハインドを減らす（Behaviors）

MVVM では、ボタンの処理はコマンドで書けます。でも、`Button` 以外のイベント（ウィンドウが開いたとき、リストをダブルクリックしたとき、フォーカスが外れたとき）は、そのままではコマンドに結べません。かといって、そのたびにコードビハインドを書くと、画面側のコードが増えていきます。この章では、イベントをコマンドに結ぶ方法と、コードビハインドに書いてよいものの目安を説明します。

## まず、標準の機能で済むもの

NuGet を足さなくても、次のものは XAML だけで書けます。

### キーとマウスの操作（InputBindings）

```xml
<ListBox ItemsSource="{Binding Items}">
    <ListBox.InputBindings>
        <KeyBinding Key="Delete" Command="{Binding DeleteCommand}" />
        <KeyBinding Key="F2" Command="{Binding RenameCommand}" />
        <MouseBinding Gesture="LeftDoubleClick" Command="{Binding OpenCommand}" />
    </ListBox.InputBindings>
</ListBox>
```

`Key` と `Modifiers`（`Control` など）の組み合わせでキー操作、`MouseBinding` でダブルクリックなどのマウス操作を、コマンドに結べます。ショートカットやダブルクリックなら、これで足ります。第 35 章の `Delete` や `F2` もこの方法でした。

### コマンドを持つコントロール

`Button`、`MenuItem`、`Hyperlink`、`ToggleButton` などは `Command` プロパティを持っているので、そのままバインドできます。

## イベントをコマンドに結ぶ：Microsoft.Xaml.Behaviors

それ以外のイベントをコマンドに結ぶときは、`Microsoft.Xaml.Behaviors.Wpf` という NuGet パッケージを使います。旧 Blend SDK の後継で、WPF の標準的な選択です。

1. NuGet で `Microsoft.Xaml.Behaviors.Wpf` を入れます。
2. XAML に名前空間を足します。

```xml
xmlns:i="http://schemas.microsoft.com/xaml/behaviors"
```

3. イベントを指定して、コマンドを呼びます。

```xml
<Window ...>
    <i:Interaction.Triggers>
        <i:EventTrigger EventName="Loaded">
            <i:InvokeCommandAction Command="{Binding LoadedCommand}" />
        </i:EventTrigger>
        <i:EventTrigger EventName="Closing">
            <i:InvokeCommandAction Command="{Binding ClosingCommand}" PassEventArgsToCommand="True" />
        </i:EventTrigger>
    </i:Interaction.Triggers>
</Window>
```

`EventTrigger` が「どのイベントを待つか」、`InvokeCommandAction` が「起きたらどのコマンドを呼ぶか」です。`PassEventArgsToCommand="True"` を付けると、イベントの引数（`CancelEventArgs` など）が、コマンドの引数として渡されます。

ビューモデル側では、渡された引数を使えます。

```csharp
ClosingCommand = new DelegateCommand<CancelEventArgs>(e =>
{
    if (HasUnsavedChanges) e.Cancel = true;     // 閉じるのを止める
});
```

ただし、`CancelEventArgs` のような「画面の型」をビューモデルが受け取ると、ビューモデルが画面に依存してしまいます。Prism の `InvokeCommandAction` を使うと、イベント引数の特定のプロパティだけを取り出して渡せます。

```xml
<i:EventTrigger EventName="SelectionChanged">
    <prism:InvokeCommandAction Command="{Binding SelectionChangedCommand}"
                               TriggerParameterPath="AddedItems" />
</i:EventTrigger>
```

`TriggerParameterPath` で `AddedItems` を指定すると、`SelectionChangedEventArgs` ではなく、選ばれた要素の集まりだけがコマンドに渡ります。ビューモデルは、画面の型を知らずに済みます。

## 自分でビヘイビアを作る

標準のトリガーで足りない場合は、`Behavior<T>` を継承して、部品に「振る舞い」を足せます。たとえば「入力欄にフォーカスが当たったら、全選択する」ビヘイビアです。

```csharp title="Behaviors/SelectAllOnFocusBehavior.cs"
using Microsoft.Xaml.Behaviors;

namespace Editor.Behaviors;

public class SelectAllOnFocusBehavior : Behavior<TextBox>
{
    protected override void OnAttached()
    {
        base.OnAttached();
        AssociatedObject.GotKeyboardFocus += OnGotFocus;
    }

    protected override void OnDetaching()
    {
        AssociatedObject.GotKeyboardFocus -= OnGotFocus;
        base.OnDetaching();
    }

    private void OnGotFocus(object sender, KeyboardFocusChangedEventArgs e)
    {
        AssociatedObject.SelectAll();
    }
}
```

```xml
<TextBox Text="{Binding Name}">
    <i:Interaction.Behaviors>
        <behaviors:SelectAllOnFocusBehavior />
    </i:Interaction.Behaviors>
</TextBox>
```

`AssociatedObject` は、このビヘイビアが付けられた部品（ここでは `TextBox`）です。`OnAttached` で登録し、`OnDetaching` で解除するのが決まりです（解除を忘れると、メモリが残る原因になります。第 45 章）。

ビヘイビアの良いところは、一度書いたら、XAML に 1 行書くだけで、どの画面の部品にも付けられることです。コードビハインドにそのつど書くよりも、再利用できます。

### 添付プロパティで書く方法

もっと軽く、`True` にするだけで振る舞いを足したいなら、添付プロパティ（第 10 章）を使う方法もあります。

```csharp
public static class TextBoxHelper
{
    public static readonly DependencyProperty SelectAllOnFocusProperty =
        DependencyProperty.RegisterAttached("SelectAllOnFocus", typeof(bool), typeof(TextBoxHelper),
            new PropertyMetadata(false, OnChanged));

    public static bool GetSelectAllOnFocus(DependencyObject d) => (bool)d.GetValue(SelectAllOnFocusProperty);
    public static void SetSelectAllOnFocus(DependencyObject d, bool v) => d.SetValue(SelectAllOnFocusProperty, v);

    private static void OnChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is not TextBox box) return;
        box.GotKeyboardFocus -= OnFocus;
        if ((bool)e.NewValue) box.GotKeyboardFocus += OnFocus;
    }

    private static void OnFocus(object sender, KeyboardFocusChangedEventArgs e) => ((TextBox)sender).SelectAll();
}
```

```xml
<TextBox helpers:TextBoxHelper.SelectAllOnFocus="True" />
```

`Behavior<T>` と添付プロパティのどちらでも構いません。ライブラリを増やしたくなければ、添付プロパティで十分です。

## コードビハインドに書いてよいもの

コードビハインドは絶対に禁止、ではありません。迷ったときの目安を書いておきます。

| 内容 | 書き場所 |
| --- | --- |
| 部品そのものを触る処理（`SelectAll()`、`ScrollIntoView()`、`Focus()`） | ビヘイビア か、ビューのコードビハインド |
| `HwndHost` のイベントを受けてビューモデルに橋渡しする | ビューのコードビハインド |
| ドラッグ アンド ドロップの座標計算、ヒットテスト | ビューのコードビハインド（結果だけをビューモデルへ渡す） |
| アニメーションの細かい制御 | XAML（トリガー）か、ビューのコードビハインド |
| ビジネス ロジック、データの計算、ファイルの読み書き | ビューモデルかサービス（コードビハインドには書かない） |

判断の基準は、「その処理は、画面を変えたときに一緒に変わるべきか」です。画面の部品だけに関係するなら、ビューに置いてよく、データや操作に関係するなら、ビューモデルに置きます。

??? failure "`EventTrigger` が反応しない"
    `EventName` が、その部品に存在するイベントの名前と一致していません。`Loaded` や `Click` のようなルーテッド イベントは、その部品または子から起きたものだけが対象です。

??? failure "`Interaction` が見つからない（`The attachable property 'Triggers' was not found`）"
    古い `System.Windows.Interactivity` の名前空間（`http://schemas.microsoft.com/expression/2010/interactivity`）を使っています。新しい `Microsoft.Xaml.Behaviors.Wpf` では、`http://schemas.microsoft.com/xaml/behaviors` です。

次の章では、起動と終了、ウィンドウ、標準のコマンドなど、アプリそのものの話をまとめます。

[第 23 章 アプリの基本（起動・終了・ウィンドウ・コマンド）](23-app-basics.md) へ進みます。
