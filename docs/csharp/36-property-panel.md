---
title: 第 36 章 プロパティ パネル
tags:
  - C#連携
---

# 第 36 章 プロパティ パネル

この章では、選択した物の名前、位置、回転、拡大、色を、入力欄とスライダーで編集できるようにします。エディタの中でいちばんよく使う画面のひとつです。`TextBox` のバインディング、入力の検証、型ごとの `DataTemplate`、同じ部品の使い回しを学びます。

!!! info "このページを読む前に"
    - [第 35 章 シーン ツリー](35-scene-tree.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


作り始める前に、決めておきたいことが 3 つあります。

## 編集は、1 か所の窓口を通す

入力欄に数字を打ち込んだとき、`obj.Position = ...` と直接書いてもよいのですが、第 38 章で Undo/Redo を入れる予定です。Undo は、「何を、どう変えたか」の記録が必要です。あとから全部の編集コードを書き直すのは大変なので、最初から、すべての編集を `ISceneEditor` という窓口を通すようにしておきます。

今の窓口は、値を直接変えるだけです。第 38 章で、中身を「コマンドを記録する」形に差し替えます。呼ぶ側（プロパティ パネル）は、そのままで済みます。

```text
入力欄 ─▶ PropertyViewModel ─▶ ISceneEditor.SetPosition(...) ─▶ SceneObject を変更 ─▶ SceneDocument.Changed ─▶ エンジンへ
                                       ▲
                                第 38 章で、Undo 用の記録をここに足す
```

## Vector3 の「成分」を編集する

`Position` は `Vector3`（構造体）です。画面の `TextBox` が編集したいのは、その中の X、Y、Z のそれぞれです。第 34 章で触れたとおり、`Position.X = 5` はコピーを書き換えるだけで効きません。X が変わったら、新しい `Vector3` を作って丸ごと入れ替える必要があります。

「`Vector3` を X、Y、Z に分けて編集する」仕事は、位置、回転、拡大の 3 か所で同じです。1 つのクラス（`Vector3EditorViewModel`）にして、使い回します。

## 画面は型で選ぶ

位置、回転、拡大は、どれも「X Y Z を 3 つ並べる」同じ見た目です。WPF の `DataTemplate` は、データの型に対して自動で選ばれるので、`Vector3EditorViewModel` に 1 つ作れば、3 か所とも同じ見た目になります。

この章を終えると、選択中の物の値を編集して、ビューポートの箱が即座に変わり、選択を変えればパネルも切り替わります。何も選んでいなければパネルは無効になり、不正な入力（文字や 0 の拡大）も扱えます。

## 編集の窓口（ISceneEditor）

```csharp title="Services/ISceneEditor.cs"
using System.Numerics;
using Editor.Models;

namespace Editor.Services;

// シーンの編集は、すべてこの窓口を通す。第 38 章で、Undo/Redo の記録を足す。
public interface ISceneEditor
{
    void SetName(SceneObject obj, string name);
    void SetPosition(SceneObject obj, Vector3 value);
    void SetRotationDegrees(SceneObject obj, Vector3 value);
    void SetScale(SceneObject obj, Vector3 value);
    void SetColor(SceneObject obj, Vector4 value);
}
```

```csharp title="Services/SceneEditor.cs"
using System.Numerics;
using Editor.Models;

namespace Editor.Services;

public sealed class SceneEditor : ISceneEditor
{
    private readonly SceneDocument _document;

    public SceneEditor(SceneDocument document)
    {
        _document = document;
    }

    public void SetName(SceneObject obj, string name)
    {
        if (obj.Name == name) return;
        obj.Name = name;
        _document.NotifyChanged(SceneChangeKind.Renamed, obj);
    }

    public void SetPosition(SceneObject obj, Vector3 value)
    {
        if (obj.Position == value) return;
        obj.Position = value;
        _document.NotifyChanged(SceneChangeKind.TransformChanged, obj);
    }

    public void SetRotationDegrees(SceneObject obj, Vector3 value)
    {
        if (obj.RotationDegrees == value) return;
        obj.RotationDegrees = value;
        _document.NotifyChanged(SceneChangeKind.TransformChanged, obj);
    }

    public void SetScale(SceneObject obj, Vector3 value)
    {
        if (obj.Scale == value) return;
        obj.Scale = value;
        _document.NotifyChanged(SceneChangeKind.TransformChanged, obj);
    }

    public void SetColor(SceneObject obj, Vector4 value)
    {
        if (obj.Color == value) return;
        obj.Color = value;
        _document.NotifyChanged(SceneChangeKind.ColorChanged, obj);
    }
}
```

`App.xaml.cs` で、`containerRegistry.RegisterSingleton<ISceneEditor, SceneEditor>();` と登録します。

`obj.Position == value` は、`Vector3` の 3 成分がすべて等しいかを比べます。同じ値なら何もしないことで、無駄な通知とエンジンへの命令を省いています。

ここでは、通知が 2 種類あることに気づいてほしいです。`SceneObject` のプロパティが出す `PropertyChanged` は、画面を更新するための通知です。一方、エンジンへの同期は `SceneDocument.Changed` イベントです。この窓口が、両方の面倒を見ます。

## Vector3 を編集する部品

```csharp title="Modules/Property/ViewModels/Vector3EditorViewModel.cs"
using System.Numerics;
using Prism.Mvvm;

namespace Editor.Modules.Property.ViewModels;

// Vector3 を X、Y、Z の成分に分けて編集する部品。位置、回転、拡大で使い回す。
public sealed class Vector3EditorViewModel : BindableBase
{
    private readonly Func<Vector3> _get;
    private readonly Action<Vector3> _set;

    public Vector3EditorViewModel(string label, Func<Vector3> get, Action<Vector3> set)
    {
        Label = label;
        _get = get;
        _set = set;
    }

    public string Label { get; }

    public float X
    {
        get => _get().X;
        set => _set(_get() with { X = value });      // X だけ差し替えた、新しい Vector3 を作る
    }

    public float Y
    {
        get => _get().Y;
        set => _set(_get() with { Y = value });
    }

    public float Z
    {
        get => _get().Z;
        set => _set(_get() with { Z = value });
    }

    // 元の値が（外から）変わったとき、画面に再読み込みさせる
    public void Refresh()
    {
        RaisePropertyChanged(nameof(X));
        RaisePropertyChanged(nameof(Y));
        RaisePropertyChanged(nameof(Z));
    }
}
```

この部品は、「値を読む関数」と「値を書く関数」を、コンストラクターで受け取ります。値が実際にどこにあるのかは知らないので、位置にも回転にも使えます。

`with { X = value }` は with 式といって、構造体（や `record`）をコピーして、一部の成分だけを変えた新しい値を作ります。元の値は変わりません。`Refresh()` は、Undo やエンジン側の変更で、元の値が外から変わったときに、画面を読み直させるために呼びます。

## プロパティのビューモデル

```csharp title="Modules/Property/ViewModels/PropertyViewModel.cs"
using System.ComponentModel;
using System.Numerics;
using Prism.Mvvm;

using Editor.Models;
using Editor.Services;

namespace Editor.Modules.Property.ViewModels;

public class PropertyViewModel : BindableBase
{
    private readonly ISelectionService _selection;
    private readonly ISceneEditor _editor;
    private SceneObject? _target;

    public PropertyViewModel(ISelectionService selection, ISceneEditor editor)
    {
        _selection = selection;
        _editor = editor;

        Position = new Vector3EditorViewModel("位置", () => Target?.Position ?? Vector3.Zero,
            v => { if (Target != null) _editor.SetPosition(Target, v); });
        Rotation = new Vector3EditorViewModel("回転 (度)", () => Target?.RotationDegrees ?? Vector3.Zero,
            v => { if (Target != null) _editor.SetRotationDegrees(Target, v); });
        Scale = new Vector3EditorViewModel("拡大", () => Target?.Scale ?? Vector3.One,
            v => { if (Target != null) _editor.SetScale(Target, ClampScale(v)); });

        _selection.SelectionChanged += OnSelectionChanged;
        OnSelectionChanged();
    }

    public string Title => "プロパティ";

    public Vector3EditorViewModel Position { get; }
    public Vector3EditorViewModel Rotation { get; }
    public Vector3EditorViewModel Scale { get; }

    // 編集の対象（主の選択）。選択がなければ null
    public SceneObject? Target
    {
        get => _target;
        private set
        {
            if (_target != null) _target.PropertyChanged -= OnTargetPropertyChanged;
            if (SetProperty(ref _target, value) && _target != null)
            {
                _target.PropertyChanged += OnTargetPropertyChanged;
            }
            RaisePropertyChanged(nameof(HasTarget));
            RefreshAll();
        }
    }

    public bool HasTarget => _target != null;

    public string Name
    {
        get => _target?.Name ?? "";
        set
        {
            if (_target != null && !string.IsNullOrWhiteSpace(value)) _editor.SetName(_target, value);
            RaisePropertyChanged();
        }
    }

    // 色（0〜1）。スライダーに対応する
    public float ColorR { get => _target?.Color.X ?? 0; set => SetColor(c => c with { X = value }); }
    public float ColorG { get => _target?.Color.Y ?? 0; set => SetColor(c => c with { Y = value }); }
    public float ColorB { get => _target?.Color.Z ?? 0; set => SetColor(c => c with { Z = value }); }

    private void SetColor(Func<Vector4, Vector4> change)
    {
        if (_target != null) _editor.SetColor(_target, change(_target.Color));
    }

    private void OnSelectionChanged() => Target = _selection.Primary;

    // 対象の値が（Undo、エンジン、別の画面などから）変わったら、パネルを更新する
    private void OnTargetPropertyChanged(object? sender, PropertyChangedEventArgs e) => RefreshAll();

    private void RefreshAll()
    {
        Position.Refresh();
        Rotation.Refresh();
        Scale.Refresh();
        RaisePropertyChanged(nameof(Name));
        RaisePropertyChanged(nameof(ColorR));
        RaisePropertyChanged(nameof(ColorG));
        RaisePropertyChanged(nameof(ColorB));
    }

    // 拡大が 0 だと、箱が潰れて見えなくなり、行列も壊れる。小さな下限を設ける
    private static Vector3 ClampScale(Vector3 v) => Vector3.Max(v, new Vector3(0.001f));
}
```

`Position`、`Rotation`、`Scale` は、同じ `Vector3EditorViewModel` クラスの別のインスタンスです。読み書きの先だけを、コンストラクターに渡す関数で変えています。同じ部品を、設定（関数）だけ変えて使い回す設計の典型です。

注意したいところをいくつか拾います。

- `Target?.Position ?? Vector3.Zero` は、`Target` が `null` のときに `Vector3.Zero` を使う書き方です。
- `Target` の `set` で、前の対象の `PropertyChanged` の購読を外して、新しい対象を購読し直しています。購読の外し忘れは、メモリリークや二重更新の原因になります。
- `Name` の `set` で `RaisePropertyChanged()` を引数なしで呼んでいます。空の名前のように拒否した値が入力欄に残らないよう、元の値に戻させるためです。
- `ClampScale` は、拡大が 0 になるのを防ぎます。0 だと、箱が潰れて見えなくなり、行列も壊れます。
- `SetColor(c => c with { X = value })` のように、変更の仕方を関数で渡しているので、R、G、B で `SetColor` を共有できます。

## ビュー

### Vector3 の見た目（DataTemplate）

`PropertyView.xaml` の `Resources` に、`Vector3EditorViewModel` 用のテンプレートを書きます。

```xml
<UserControl.Resources>
    <DataTemplate DataType="{x:Type vm:Vector3EditorViewModel}">
        <Grid Margin="0,4">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="72" />
                <ColumnDefinition Width="*" />
                <ColumnDefinition Width="*" />
                <ColumnDefinition Width="*" />
            </Grid.ColumnDefinitions>
            <TextBlock Grid.Column="0" Text="{Binding Label}" VerticalAlignment="Center" />
            <TextBox Grid.Column="1" Margin="2,0" Text="{Binding X, StringFormat=F3, UpdateSourceTrigger=LostFocus}" />
            <TextBox Grid.Column="2" Margin="2,0" Text="{Binding Y, StringFormat=F3, UpdateSourceTrigger=LostFocus}" />
            <TextBox Grid.Column="3" Margin="2,0" Text="{Binding Z, StringFormat=F3, UpdateSourceTrigger=LostFocus}" />
        </Grid>
    </DataTemplate>
</UserControl.Resources>
```

`DataType` を指定した `DataTemplate` は、その型のデータを表示するときに、自動で選ばれます（`xmlns:vm` の宣言が必要です）。`StringFormat=F3` は、小数 3 桁で表示する指定です。`UpdateSourceTrigger=LostFocus` は、フォーカスが外れたとき（または `Enter`）に値を反映する指定で、1 文字ごとに反映すると、`1.` と打っている途中で `1` に戻されたりして、入力しにくいので、あえて既定の `LostFocus` にしています。`abc` のような変換できない文字を入れると、入力欄が赤枠になり、値は反映されません。

### 本体

```xml
<UserControl x:Class="Editor.Modules.Property.Views.PropertyView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:prism="http://prismlibrary.com/"
             xmlns:vm="clr-namespace:Editor.Modules.Property.ViewModels"
             prism:ViewModelLocator.AutoWireViewModel="True">
    <!-- UserControl.Resources は上のとおり -->
    <ScrollViewer VerticalScrollBarVisibility="Auto" Background="#FF252526">
        <StackPanel Margin="8" IsEnabled="{Binding HasTarget}">
            <TextBlock Text="プロパティ" FontWeight="Bold" />

            <TextBlock Text="名前" Margin="0,8,0,2" />
            <TextBox Text="{Binding Name, UpdateSourceTrigger=LostFocus}" />

            <TextBlock Text="トランスフォーム" FontWeight="Bold" Margin="0,12,0,2" />
            <ContentControl Content="{Binding Position}" />
            <ContentControl Content="{Binding Rotation}" />
            <ContentControl Content="{Binding Scale}" />

            <TextBlock Text="色" FontWeight="Bold" Margin="0,12,0,2" />
            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="24" />
                    <ColumnDefinition Width="*" />
                </Grid.ColumnDefinitions>
                <Grid.RowDefinitions>
                    <RowDefinition /><RowDefinition /><RowDefinition />
                </Grid.RowDefinitions>
                <TextBlock Grid.Row="0" Text="R" Foreground="#FFFF6060" />
                <Slider Grid.Row="0" Grid.Column="1" Minimum="0" Maximum="1" Value="{Binding ColorR}" />
                <TextBlock Grid.Row="1" Text="G" Foreground="#FF60FF60" />
                <Slider Grid.Row="1" Grid.Column="1" Minimum="0" Maximum="1" Value="{Binding ColorG}" />
                <TextBlock Grid.Row="2" Text="B" Foreground="#FF6080FF" />
                <Slider Grid.Row="2" Grid.Column="1" Minimum="0" Maximum="1" Value="{Binding ColorB}" />
            </Grid>
        </StackPanel>
    </ScrollViewer>
</UserControl>
```

`<ContentControl Content="{Binding Position}" />` は、中身に `Vector3EditorViewModel` を入れています。WPF が、型に合う `DataTemplate` を探して表示してくれるので、見た目を何度も書かずに済みます。`StackPanel` の `IsEnabled="{Binding HasTarget}"` は、選択がないときに、中の部品を全部まとめて無効（グレー）にします。`Slider` は、`Minimum`、`Maximum`、`Value` を持つ部品で、`Value` は既定で双方向、つまみを動かすたびに更新されます。

## 色の見本

スライダーだけでは、どんな色なのか分かりにくいので、見本を出します。`Vector4` を `Brush` に変えるコンバーター（第 12 章）を作ります。

```csharp title="Converters/ColorToBrushConverter.cs"
using System.Globalization;
using System.Numerics;
using System.Windows.Data;
using System.Windows.Media;

namespace Editor.Converters;

public class ColorToBrushConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        if (value is not Vector4 c) return Brushes.Transparent;
        byte R(float f) => (byte)Math.Clamp((int)MathF.Round(f * 255f), 0, 255);
        var brush = new SolidColorBrush(Color.FromRgb(R(c.X), R(c.Y), R(c.Z)));
        brush.Freeze();                       // 変更しないと宣言して、軽くする
        return brush;
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => throw new NotSupportedException();
}
```

見本の `Border` は、`ColorR/G/B` が変わるたびに更新したいので、`PropertyViewModel` に `SwatchBrush` を足します。

```csharp
public Brush SwatchBrush
{
    get
    {
        var c = _target?.Color ?? new Vector4(0, 0, 0, 1);
        byte R(float f) => (byte)Math.Clamp((int)MathF.Round(f * 255f), 0, 255);
        return new SolidColorBrush(Color.FromRgb(R(c.X), R(c.Y), R(c.Z)));
    }
}
// RefreshAll に追加： RaisePropertyChanged(nameof(SwatchBrush));
```

```xml
<Border Height="24" Margin="0,4" BorderBrush="Gray" BorderThickness="1" Background="{Binding SwatchBrush}" />
```

`byte R(float f) => ...` は、ローカル関数といって、メソッドの中に書ける小さな関数です。`Freeze()` は、「このブラシは、これ以上変更しません」と宣言して、WPF が効率よく扱えるようにします。

ビューモデルが `Brush`（画面の型）を返すのは、MVVM の純粋さでは好ましくありません。本来は、色の値を返して、コンバーターで `Brush` に変えるのが正しい形です。ここでは、簡単さを優先しました。

WPF の標準には、色を選ぶダイアログ（部品）がありません。実用的には、`Extended.Wpf.Toolkit` の `ColorPicker` のようなサードパーティのライブラリを NuGet で入れます。この教材では、スライダーで十分です。

## 複数の物を選んだとき

第 35 章の選択は、複数を持てます。複数選択したときの方針は、いくつか考えられます。

- 主の選択（先頭の物）だけを編集する。いちばん簡単で、この教材はこれにしています。
- 編集したら、選択中の全員に同じ値を設定する。値が違う項目は、空欄（`—`）で表示します。
- 位置を動かしたら、全員が同じ差分だけ動くようにする。

後者の 2 つも、`ISceneEditor` の呼び出しを、`Selection` の全員に対して行うだけで実現できます。ただし、Undo では、全員の変更を 1 つの操作にまとめなければいけません（第 38 章）。

## 動かして確かめる

- 何も選ばなければ、パネルはグレーで、空欄になる。
- ツリーで物を選ぶと、名前、位置、回転、拡大、色が出る。
- 位置 X を `3` にして `Tab` を押すと、ビューポートの箱が X 方向に動く。回転 Y に `45` を入れると、箱が Y 軸まわりに 45 度回る。
- 拡大に `0` を入れると、下限（0.001）に切り詰められ、箱が潰れすぎない。`abc` を入れると赤枠になり、値は反映されない。
- R のスライダーを動かすと、箱の線の色がリアルタイムに変わる。名前を変えると、ツリーの表示も同時に変わる。

??? failure "入力しても反映されない"
    `UpdateSourceTrigger=LostFocus` なので、`Tab` か `Enter` でフォーカスを外すまで反映されません。または、`StringFormat=F3` のある欄に `1,5` のようなカンマ区切りを入れています（地域設定によって小数点が違います）。

??? failure "選択を変えても、パネルの内容が変わらない"
    `RefreshAll` が `RaisePropertyChanged` を忘れているか、`Target` の `set` で `PropertyChanged` の購読と解除が正しく行われていません。

??? failure "`with` 式がコンパイルエラー（`CS8858`）"
    古い C# の書き方になっています。.NET 8（C# 12）なら動きます。型が `System.Numerics.Vector3`（構造体）か `record` であることを確認します。

??? failure "位置を編集しても、ビューポートの箱が動かない"
    `ISceneEditor.SetPosition` が `NotifyChanged(TransformChanged)` を呼んでいません。または、`SceneEngineSync` を解決していません（第 34 章）。

??? failure "`Vector3EditorViewModel` という文字がそのまま出る"
    `DataTemplate` の `DataType` の `xmlns:vm` が、正しい名前空間を指していません。または、`UserControl.Resources` ではなく別の場所に書いて、スコープ外になっています。

??? failure "回転の入れ方が、ねじれる（ジンバルロック）"
    オイラー角の宿命で、X を 90 度にすると Y と Z の軸が重なります。実用的なエディタは、内部をクォータニオンで持ち、表示だけをオイラー角にします。この教材は、簡単さを優先して、オイラー角のまま持っています。

## この章のまとめ

- 編集は `ISceneEditor` を通す。第 38 章で Undo/Redo を差し込む。
- 構造体の成分は、`with` 式で新しい値を作って入れ替える。
- 型ごとの見た目は、`DataTemplate` の `DataType` で、自動で選ばれる。
- 入力欄は `UpdateSourceTrigger=LostFocus` にして、1 文字ごとの更新を避ける。

次の章では、ビューポートの物をクリックして選ぶ（ピッキング）機能と、選んだ物を矢印で動かす（ギズモ）機能を作ります。

[第 37 章 ピッキングとギズモ](37-picking-gizmo.md) へ進みます。
