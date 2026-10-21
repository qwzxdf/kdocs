---
title: 第 22 章 プロパティ パネル
tags:
  - C#連携
---

# 第 22 章 プロパティ パネル

この章では選択した物の<strong>名前、位置、回転、拡大、色</strong>を入力欄とスライダーで編集できるようにします。エディタの中で最もよく使う画面の 1 つです。WPF の `TextBox` のバインディング、入力の検証、型ごとの `DataTemplate`、バインディングの再利用の考え方を学びます。

## この章の考え方

プロパティ パネルは「<strong>選択中の物のデータ</strong>を編集可能な形で見せる」ビューです。作るときに決めておくことが 3 つあります。

### 1. 編集は 1 か所の窓口を通す

入力欄に数字を打ち込んだとき `obj.Position = …` と直接書いてもよいのですが、第 24 章で <strong>Undo/Redo</strong> を入れます。Undo は「何をどう変えたか」の記録が要ります。そこで、<strong>すべての編集を `ISceneEditor` という窓口を通す<strong>ようにしておきます。今は窓口が直接値を変えるだけですが、第 24 章で中身を「コマンドを記録する」形に差し替えます。</strong>呼ぶ側（プロパティ パネル）は変えずに済みます</strong>。

```text
入力欄 ─▶ PropertyViewModel ─▶ ISceneEditor.SetPosition(...) ─▶ SceneObject を変更 ─▶ SceneDocument.Changed ─▶ エンジンへ
                                       ▲
                                第 24 章で、Undo 用の記録をここに足す
```

### 2. 値の「成分」を編集する

`Position` は `Vector3`（構造体）です。XAML の `TextBox` が編集したいのは、その中の <strong>X、Y、Z のそれぞれ</strong>です。第 20 章で述べたとおり `Position.X = 5` はコピーを書き換えるだけで効きません。<strong>X が変わったら新しい `Vector3` を作って、丸ごと入れ替える</strong>必要があります。

この「Vector3 を X、Y、Z に分けて編集する」部品を 1 つのクラス（`Vector3EditorViewModel`）にしておけば位置、回転、拡大の 3 か所で<strong>使い回せます</strong>。

### 3. 画面は型で選ぶ

位置、回転、拡大はどれも「`X Y Z` を 3 つ並べる」画面です。WPF の `DataTemplate` は<strong>データの型に対して</strong>自動で選ばれるので、`Vector3EditorViewModel` に 1 つ作れば 3 か所とも同じ見た目になります。

## この章のゴール

- 選択中の物の名前、位置、回転、拡大、色を編集できる。
- 値を変えるとビューポートの箱が即座に変わる。
- 選択が変わるとパネルの内容が切り替わる。何も選ばれていなければ空の表示になる。
- 不正な入力（文字、0 の拡大）を扱える。

## 手順 1：編集の窓口（ISceneEditor）

`Services\ISceneEditor.cs`:

```csharp
using System.Numerics;
using Editor.Models;

namespace Editor.Services;

// シーンの編集は、すべてこの窓口を通す。第 24 章で、Undo/Redo の記録を足す。
public interface ISceneEditor
{
    void SetName(SceneObject obj, string name);
    void SetPosition(SceneObject obj, Vector3 value);
    void SetRotationDegrees(SceneObject obj, Vector3 value);
    void SetScale(SceneObject obj, Vector3 value);
    void SetColor(SceneObject obj, Vector4 value);
}
```

`Services\SceneEditor.cs`:

```csharp
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

`App.xaml.cs` で登録します。`containerRegistry.RegisterSingleton<ISceneEditor, SceneEditor>();`

| 新しく出てきたもの | 説明 |
| --- | --- |
| `obj.Position == value` | `Vector3` の `==` は 3 成分がすべて等しいかを比べる。同じ値なら何もしない（無駄な通知とエンジンへの命令を防ぐ） |
| 通知は窓口が出す | `SceneObject` のプロパティは画面用の `PropertyChanged` を出す。<strong>エンジンへの同期</strong>は `Changed` イベント。この 2 つは別の通知。窓口が両方を面倒見る |

## 手順 2：Vector3 の編集部品

`Modules\Property\ViewModels\Vector3EditorViewModel.cs`:

```csharp
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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Func<Vector3> get`、`Action<Vector3> set` | 「値を読む関数」と「値を書く関数」を受け取る。<strong>読み書きの場所を知らない</strong>ので、位置にも回転にも使える |
| `with { X = value }` | <strong>with 式</strong>。構造体（やレコード）を<strong>コピーして、一部の成分だけを変えた</strong>新しい値を作る。元の値は変わらない |
| `_get().X` | `get` 関数を呼んで、その `X` を読む |
| `RaisePropertyChanged(nameof(X))` | `BindableBase` のメソッド。指定したプロパティが変わったと通知する。`nameof(X)` で文字列 `"X"` を安全に得る |
| `Refresh()` | 選択中の物の値が、Undo やエンジン側の変更で変わったとき画面を更新するために呼ぶ |

## 手順 3：プロパティのビューモデル

`Modules\Property\ViewModels\PropertyViewModel.cs`:

```csharp
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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Target?.Position ?? Vector3.Zero` | `Target` が `null` のときは `Vector3.Zero`。`Vector3`（値型）の場合、`?.` の結果は `Vector3?` になり `??` で値に戻している |
| `_target.PropertyChanged += …` | 対象の物の変更を購読する。<strong>購読は対象が変わったときに外す</strong>（外し忘れは、メモリリークと二重更新の原因） |
| `SetProperty(…) && _target != null` | `SetProperty` が `true`（変わった）で、かつ新しい対象があるとき購読する |
| `RaisePropertyChanged()`（引数なし） | 呼び出し元のプロパティ名（`[CallerMemberName]`）で通知する。`Name` の `set` が拒否された値のとき入力欄を元の値に<strong>戻す</strong>ために呼んでいる |
| `Vector3.Max(a, b)` | 成分ごとの大きい方。`new Vector3(0.001f)` は 3 成分が同じ値の `Vector3` |
| `string.IsNullOrWhiteSpace` | `null`、空、空白だけのいずれかなら `true`。空の名前を拒否する |
| ラムダの再利用 | `SetColor(c => c with { X = value })`。変更の仕方を<strong>関数で渡す</strong>ので R、G、B で `SetColor` を共有できる |

!!! note "値を読み取り専用の窓口にする"
    `Position`、`Rotation`、`Scale` の 3 つは `Vector3EditorViewModel` の<strong>同じクラスの別のインスタンス</strong>です。読み書きの先だけをコンストラクターの関数で変えています。これは<strong>同じ部品を設定（関数）だけ変えて再利用する</strong>設計の典型です。

## 手順 4：ビュー

### Vector3 の見た目（DataTemplate）

`Modules\Property\Views\PropertyView.xaml` の `Resources` に `Vector3EditorViewModel` 用のテンプレートを書きます。

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `DataTemplate DataType="{x:Type vm:Vector3EditorViewModel}"` | この型のデータを表示するとき<strong>自動でこのテンプレートが選ばれる</strong>。`xmlns:vm` の宣言が要る |
| `StringFormat=F3` | 小数 3 桁で表示する。入力した文字列が `float` に変換されるときは、書式は無視される |
| `UpdateSourceTrigger=LostFocus` | <strong>入力欄からフォーカスが外れたとき</strong>（または `Enter`）に値を反映する。1 文字ごとに反映すると `1.` と打つ途中で `1` に戻されるなど入力しにくくなる |
| 不正な入力 | `abc` のような変換できない文字は、バインディングが失敗して入力欄が<strong>赤枠</strong>になる。値は反映されない |

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `ContentControl Content="{Binding Position}"` | 中身に `Vector3EditorViewModel` を入れる。WPF が<strong>型に合う `DataTemplate`</strong> を探して表示する |
| `IsEnabled="{Binding HasTarget}"` | `false` のとき子の部品もすべて無効（グレー）になる。選択がないときに編集できなくする |
| `Slider` | つまみを動かす部品。`Minimum`、`Maximum`、`Value`。`Value` は既定で双方向。つまみを動かすたびに更新される |
| `ScrollViewer` | 内容が大きいときスクロールできるようにする |

## 手順 5：色の見本

スライダーだけだとどの色か分かりにくいので、色の見本を出します。`Vector4` を `Brush` に変える<strong>コンバーター</strong>（第 7 章）を作ります。

```csharp
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

見本の `Border` は `ColorR/G/B` が変わるたびに更新したいので、`PropertyViewModel` に `SwatchBrush` を足します。

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| ローカル関数 `byte R(float f) => …` | メソッドの中に書ける小さな関数。この関数の中でだけ使う変換をまとめて名前を付ける |
| `Color.FromRgb(r, g, b)` | WPF の色。各成分は `byte`（0〜255） |
| `SolidColorBrush` | 単色のブラシ（第 6 章） |
| `Freeze()` | 変更できない状態にする。WPF がより効率よく扱える（スレッド間の共有もできる） |
| ビューモデルが `Brush` を返す | ビューモデルが画面の型（`Brush`）を返すのは、MVVM の純粋さでは好ましくない。`Brush` を使わず<strong>色の値</strong>を返して、コンバーターで変換するのが本来の形。ここでは簡単さを優先している |

!!! tip "色の選択はどうするか"
    WPF の標準には色選択のダイアログ／部品がありません。実用的にはサードパーティのライブラリ（`Extended.Wpf.Toolkit` の `ColorPicker` など）を NuGet で入れます。この教材ではスライダーで十分です。

## 手順 6：複数選択のときの扱い

第 21 章の選択は複数を持てます。複数の物を選んだときプロパティ パネルは、次のどれかにします。

| 方針 | 内容 |
| --- | --- |
| <strong>A: 主の選択だけを編集</strong> | 先頭の物だけを編集する。最も簡単（この教材） |
| B: 全員に同じ値を設定 | 編集したら、選択中の全員にその値を設定する。値が違う項目は空欄（`—`）で表示 |
| C: 相対的に変える | 位置を動かしたら、全員が同じ<strong>差分</strong>だけ動く |

A は実装が単純でまず動かすのに向いています。B・C への拡張は `ISceneEditor` の呼び出しを `Selection` の全員に対して行うだけです。そのときに、Undo の 1 操作として<strong>まとめる</strong>ことが大切です（第 24 章）。

## 動作確認

| 操作 | 期待する結果 |
| --- | --- |
| 何も選ばない | パネルが無効（グレー）で、空欄 |
| ツリーで物を選ぶ | パネルに名前、位置、回転、拡大、色が出る |
| 位置 X を `3` にして `Tab` | ビューポートの箱が、X 方向に動く |
| 回転 Y を `45` に | 箱が、Y 軸まわりに 45 度回る |
| 拡大に `0` を入れる | 下限（0.001）に切り詰められ箱が潰れすぎない |
| 数字以外（`abc`）を入れる | 入力欄が赤枠になり値は反映されない |
| R のスライダー | 箱の色（線の色）が、リアルタイムに変わる |
| 名前を変更 | ツリーの表示も同時に変わる |
| 別の物を選ぶ | パネルの内容が切り替わる |

## よくあるミス

??? failure "入力しても反映されない"
    `UpdateSourceTrigger=LostFocus` なので `Tab` か `Enter` でフォーカスを外すまで反映されない。または、`StringFormat=F3` のある欄に `1,5` のようなカンマ区切り（地域設定によって小数点が違う）を入れた。

??? failure "選択を変えても、パネルの内容が変わらない"
    `RefreshAll` が `RaisePropertyChanged` を忘れている。または、`Target` の `set` で `PropertyChanged` の購読と解除が、正しく行われていない。

??? failure "`with` 式がコンパイルエラー（`CS8858`）"
    C# 10 より前の書き方になっている。.NET 8（C# 12）では動く。型が `System.Numerics.Vector3`（構造体）か `record` であることを確認する。

??? failure "位置を編集しても、ビューポートの箱が動かない"
    `ISceneEditor.SetPosition` が `NotifyChanged(TransformChanged)` を呼んでいない。または、`SceneEngineSync` が解決されていない（第 20 章）。

??? failure "DataTemplate が使われず `Vector3EditorViewModel` という文字がそのまま出る"
    `DataTemplate` の `DataType` の `xmlns:vm` が、正しい名前空間を指していない。または、`UserControl.Resources` ではなく別の場所に書いていて、スコープ外になっている。

??? failure "回転の入れ方が、ねじれる（ジンバルロック）"
    オイラー角の宿命。X を 90 度にすると Y と Z の軸が重なる。実用的なエディタは内部をクォータニオンで持ち表示だけオイラー角にする。この教材では簡単さを優先して、オイラー角で持つ。

## この章のまとめ

- 編集は `ISceneEditor` を通す。第 24 章で Undo/Redo を差し込む。
- 構造体の成分は `with` 式で<strong>新しい値を作って</strong>入れ替える。
- 型ごとの見た目は `DataTemplate` の `DataType` で、自動で選ばれる。
- 入力欄は `UpdateSourceTrigger=LostFocus`。1 文字ごとの更新を避ける。

## 次の章へ

次の章（[第 23 章 ピッキングとギズモ](23-picking-gizmo.md)）では、ビューポートの物を<strong>クリックして選ぶ</strong>（ピッキング）、そして<strong>矢印をドラッグして動かす</strong>（ギズモ）機能を作ります。
