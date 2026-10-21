---
title: 第 21 章 シーン ツリー
tags:
  - C#連携
---

# 第 21 章 シーン ツリー

この章では、`SceneDocument` を<strong>木（ツリー）として表示</strong>し、物を選択、名前変更、追加、削除、そして<strong>ドラッグ アンド ドロップで親子づけ</strong>できるようにします。WPF の `TreeView`、`HierarchicalDataTemplate`、コンテキスト メニュー、キー操作、ドラッグ アンド ドロップが、一度に出てくる章です。

## この章の考え方

シーン ツリーは、<strong>ドキュメントの見た目</strong>です。ここでの原則は、第 7 章の MVVM と同じです。

- ツリーは、`SceneDocument.Roots`（`ObservableCollection`）を<strong>バインディングで見る</strong>だけ。
- 追加・削除は、<strong>コマンド</strong>でドキュメントを変える。ドキュメントが変われば、ツリーは<strong>自動で</strong>更新される。
- ツリーの内部（`TreeViewItem`）を、コードで直接いじらない。

選択も同じです。「今、何が選ばれているか」は、ツリーだけの話ではなく、ビューポート（青い枠）やプロパティ パネルも知りたい情報です。そこで、<strong>選択を持つサービス</strong>（`ISelectionService`）を作り、ツリー、ビューポート、プロパティの 3 者が、<strong>そのサービスを介して</strong>やり取りします（第 10 章の考え方）。

```text
ツリーで選ぶ ─▶ ISelectionService ─▶ プロパティ パネルが切り替わる
ビューポートで選ぶ ─▶       │      ─▶ ツリーの選択表示が追従
                           └──────▶ エンジンの強調表示（黄色）
```

## この章のゴール

- `TreeView` に、物の木を表示する。
- ツリーで選んだ物を、`ISelectionService` を通して共有する。選んだ物が、ビューポートで黄色になる。
- ボタン、右クリックのメニュー、`Delete` キー、`F2` キーで、追加・削除・名前変更ができる。
- ドラッグ アンド ドロップで、親子関係を変えられる。

## 手順 1：選択サービス

第 10 章では、`int?` の ID で選択を持つ簡易版を書きました。ここで、<strong>物そのもの</strong>を持つ形に作り直します。

`Services\ISelectionService.cs`:

```csharp
using Editor.Models;

namespace Editor.Services;

public interface ISelectionService
{
    // 選択中の物（先頭が「主」の選択）
    IReadOnlyList<SceneObject> Selection { get; }

    // 主の選択。何も選ばれていなければ null
    SceneObject? Primary { get; }

    // 選択を置き換える。additive が true なら、追加（Ctrl を押しながらの選択）
    void Select(SceneObject? obj, bool additive = false);
    void SelectMany(IEnumerable<SceneObject> objects);
    void Clear();

    event Action? SelectionChanged;
}
```

`Services\SelectionService.cs`:

```csharp
using Editor.Models;

namespace Editor.Services;

public sealed class SelectionService : ISelectionService
{
    private readonly List<SceneObject> _selection = new();
    private readonly IRenderLoop _loop;

    public SelectionService(SceneDocument document, IRenderLoop loop)
    {
        _loop = loop;
        // 選択中の物が、ドキュメントから消えたら、選択からも外す
        document.Changed += change =>
        {
            if (change.Kind == SceneChangeKind.Destroyed && _selection.Remove(change.Object))
            {
                change.Object.IsSelected = false;
                RaiseChanged();
            }
        };
    }

    public IReadOnlyList<SceneObject> Selection => _selection;
    public SceneObject? Primary => _selection.Count > 0 ? _selection[0] : null;
    public event Action? SelectionChanged;

    public void Select(SceneObject? obj, bool additive = false)
    {
        if (!additive) ClearSilently();
        if (obj != null && !_selection.Contains(obj))
        {
            _selection.Insert(0, obj);      // 最後に選んだ物を「主」にする
            obj.IsSelected = true;
        }
        RaiseChanged();
    }

    public void SelectMany(IEnumerable<SceneObject> objects)
    {
        ClearSilently();
        foreach (var o in objects)
        {
            _selection.Add(o);
            o.IsSelected = true;
        }
        RaiseChanged();
    }

    public void Clear()
    {
        ClearSilently();
        RaiseChanged();
    }

    private void ClearSilently()
    {
        foreach (var o in _selection) o.IsSelected = false;
        _selection.Clear();
    }

    private void RaiseChanged()
    {
        // 選択をエンジンに伝える（強調表示のため）
        uint[] ids = _selection.Select(o => o.Id).ToArray();
        _loop.Post(e => e.SceneSetSelection(ids));
        SelectionChanged?.Invoke();
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `IReadOnlyList<T>` | 読み取り専用のリスト。外から `Add` できない。`List<T>` を返しても、この型で見せると変更されない |
| `IsSelected` | `SceneObject` に追加するプロパティ。ツリーの選択表示と、バインディングする（次の手順） |
| `Insert(0, obj)` | 先頭に入れる。最後に選んだ物が、`Primary` になる |
| `_selection.Select(o => o.Id).ToArray()` | LINQ の `Select`（変換）で、ID の配列を作る。<strong>この `Select` は LINQ</strong>で、サービスの `Select` メソッドとは別物 |
| `ids` を作ってから `Post` | 描画スレッドで実行される時点の選択ではなく、<strong>今の選択のコピー</strong>を送る（第 20 章） |

`SceneObject` に、画面用の状態を足します。

```csharp
// SceneObject.cs に追加（保存しない、画面の状態）
private bool _isSelected;
public bool IsSelected
{
    get => _isSelected;
    set => SetProperty(ref _isSelected, value);
}

private bool _isExpanded = true;
public bool IsExpanded
{
    get => _isExpanded;
    set => SetProperty(ref _isExpanded, value);
}

private bool _isEditing;
public bool IsEditing
{
    get => _isEditing;
    set => SetProperty(ref _isEditing, value);
}
```

`IEngineService` に `SceneSetSelection(uint[] ids)` を足し、P/Invoke の宣言も書きます。

```csharp
[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static unsafe partial MeResult me_scene_set_selection(EngineHandle engine, uint* ids, uint count);
```

```csharp
public void SceneSetSelection(uint[] ids)
{
    unsafe
    {
        fixed (uint* p = ids)               // 配列を固定して、アドレスを取る
        {
            NativeMethods.ThrowIfFailed(NativeMethods.me_scene_set_selection(Handle, p, (uint)ids.Length));
        }
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `fixed (uint* p = ids)` | 配列を<strong>ピン留め</strong>（GC が動かさない）にして、先頭のポインター `p` を得る。ブロックを出ると解除される。配列を C++ に渡すときの定番 |
| `uint*` | `unsafe` のポインター。C の `const uint32_t*` に当たる |
| 空の配列 | 長さ 0 の配列では、`fixed` が `null` を返す。C++ 側は、`count == 0` のとき `ids` を読まない（第 20 章の検査と合う） |

## 手順 2：ビューモデル

`Modules\SceneTree\ViewModels\SceneTreeViewModel.cs`:

```csharp
using System.Collections.ObjectModel;
using System.Numerics;
using Prism.Commands;
using Prism.Mvvm;

using Editor.Models;
using Editor.Services;

namespace Editor.Modules.SceneTree.ViewModels;

public class SceneTreeViewModel : BindableBase
{
    private readonly SceneDocument _document;
    private readonly ISelectionService _selection;

    public SceneTreeViewModel(SceneDocument document, ISelectionService selection)
    {
        _document = document;
        _selection = selection;

        AddEmptyCommand = new DelegateCommand(AddEmpty);
        AddChildCommand = new DelegateCommand(AddChild, () => _selection.Primary != null);
        DeleteCommand = new DelegateCommand(Delete, () => _selection.Primary != null);
        RenameCommand = new DelegateCommand(Rename, () => _selection.Primary != null);

        // 選択が変わったら、「選択が必要なコマンド」の有効・無効を再確認する
        _selection.SelectionChanged += () =>
        {
            AddChildCommand.RaiseCanExecuteChanged();
            DeleteCommand.RaiseCanExecuteChanged();
            RenameCommand.RaiseCanExecuteChanged();
        };
    }

    // ツリーの根（バインディング先）
    public ObservableCollection<SceneObject> Roots => _document.Roots;

    public DelegateCommand AddEmptyCommand { get; }
    public DelegateCommand AddChildCommand { get; }
    public DelegateCommand DeleteCommand { get; }
    public DelegateCommand RenameCommand { get; }

    // ツリーで選ばれた（TreeViewItem.IsSelected から呼ぶ。次の手順の XAML 参照）
    public void OnItemSelected(SceneObject obj) => _selection.Select(obj);

    private void AddEmpty()
    {
        var obj = _document.Create($"Object {_document.AllocateId()}");
        _selection.Select(obj);
    }

    private void AddChild()
    {
        var parent = _selection.Primary;
        if (parent == null) return;
        var obj = _document.Create($"Object {_document.AllocateId()}", parent);
        obj.Position = new Vector3(0, 1, 0);                    // 親の少し上
        _document.NotifyChanged(SceneChangeKind.TransformChanged, obj);
        _selection.Select(obj);
    }

    private void Delete()
    {
        foreach (var obj in _selection.Selection.ToList())
        {
            _document.Destroy(obj);
        }
    }

    private void Rename()
    {
        if (_selection.Primary is { } obj) obj.IsEditing = true;      // 編集モードにする
    }

    // ドラッグ アンド ドロップで、親を変える
    public void Reparent(SceneObject dragged, SceneObject? newParent)
    {
        if (dragged.Parent == newParent) return;
        try { _document.Reparent(dragged, newParent); }
        catch (InvalidOperationException) { /* 輪になる移動は、無視する */ }
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `() => _selection.Primary != null` | `DelegateCommand` の第 2 引数。<strong>選択があるときだけ</strong>押せる |
| `RaiseCanExecuteChanged()` | 条件が変わったので、有効・無効を確認し直させる（第 7 章） |
| `if (x is { } obj)` | プロパティ パターンの特別な形。`x` が `null` でなければ、`obj` に取り出す |
| `public ObservableCollection<SceneObject> Roots => _document.Roots;` | ドキュメントの `Roots` を、そのまま公開する。ツリーは、ドキュメントを<strong>直接見る</strong> |
| 空の `catch` | 想定内の失敗（輪になる移動）は、静かに無視する。<strong>想定外の例外は握りつぶさない</strong>ように、型を限定する |

## 手順 3：ビュー（XAML）

`Views\SceneTreeView.xaml`:

### 上部のボタンと、ツリー

```xml
<UserControl x:Class="Editor.Modules.SceneTree.Views.SceneTreeView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:prism="http://prismlibrary.com/"
             xmlns:models="clr-namespace:Editor.Models"
             prism:ViewModelLocator.AutoWireViewModel="True">
    <DockPanel Background="#FF252526">
        <!-- 上：ツール バー -->
        <ToolBar DockPanel.Dock="Top">
            <Button Content="＋ 追加" Command="{Binding AddEmptyCommand}" />
            <Button Content="＋ 子" Command="{Binding AddChildCommand}" />
            <Button Content="削除" Command="{Binding DeleteCommand}" />
        </ToolBar>

        <!-- ツリー本体 -->
        <TreeView x:Name="Tree" ItemsSource="{Binding Roots}" AllowDrop="True">
            <TreeView.InputBindings>
                <KeyBinding Key="Delete" Command="{Binding DeleteCommand}" />
                <KeyBinding Key="F2" Command="{Binding RenameCommand}" />
            </TreeView.InputBindings>
            <!-- 次の節で書く -->
        </TreeView>
    </DockPanel>
</UserControl>
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `ToolBar` | ボタンを並べる入れ物。標準のツール バー |
| `TreeView` | 木構造を表示する部品。`ItemsSource` に、<strong>最上位の要素の集まり</strong>を渡す |
| `AllowDrop="True"` | ドラッグ アンド ドロップの受け側になれる |
| `InputBindings` | キー操作とコマンドを結びつける。`KeyBinding Key="Delete"` で `Delete` キー |
| `Modifiers="Control" Key="D"` | `Ctrl + D` のように、修飾キー付きも書ける |

### 木の見た目：HierarchicalDataTemplate

木の各要素の見た目と、子の取り出し方を指定します。

```xml
<TreeView.Resources>
    <HierarchicalDataTemplate DataType="{x:Type models:SceneObject}" ItemsSource="{Binding Children}">
        <Grid>
            <!-- 通常表示 -->
            <TextBlock Text="{Binding Name}" Foreground="White">
                <TextBlock.Style>
                    <Style TargetType="TextBlock">
                        <Style.Triggers>
                            <DataTrigger Binding="{Binding IsEditing}" Value="True">
                                <Setter Property="Visibility" Value="Collapsed" />
                            </DataTrigger>
                        </Style.Triggers>
                    </Style>
                </TextBlock.Style>
            </TextBlock>
            <!-- 名前の編集（F2） -->
            <TextBox Text="{Binding Name, UpdateSourceTrigger=LostFocus}" MinWidth="80">
                <TextBox.Style>
                    <Style TargetType="TextBox">
                        <Setter Property="Visibility" Value="Collapsed" />
                        <Style.Triggers>
                            <DataTrigger Binding="{Binding IsEditing}" Value="True">
                                <Setter Property="Visibility" Value="Visible" />
                            </DataTrigger>
                        </Style.Triggers>
                    </Style>
                </TextBox.Style>
            </TextBox>
        </Grid>
    </HierarchicalDataTemplate>
</TreeView.Resources>
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `HierarchicalDataTemplate` | 木の 1 項目の見た目。`DataTemplate` に加えて、<strong>`ItemsSource` で子の集まり</strong>（`Children`）を指定する。子も同じテンプレートで再帰的に表示される |
| `DataType="{x:Type models:SceneObject}"` | 「この型のデータに、自動でこのテンプレートを使う」。`ItemTemplate` を書かなくても、型で選ばれる |
| `Style.Triggers` / `DataTrigger` | データの値に応じて、見た目を変える。`IsEditing` が `True` なら、通常表示を隠し、編集欄を出す |
| `Setter Property="Visibility"` | スタイルでプロパティを設定する |
| `Visibility="Collapsed"` | 見えず、場所もつぶれる（第 7 章） |
| `x:Type` | XAML で、型そのものを書く。`typeof(…)` に当たる |

### 選択と展開をバインドする

```xml
<TreeView.ItemContainerStyle>
    <Style TargetType="TreeViewItem">
        <Setter Property="IsSelected" Value="{Binding IsSelected, Mode=TwoWay}" />
        <Setter Property="IsExpanded" Value="{Binding IsExpanded, Mode=TwoWay}" />
    </Style>
</TreeView.ItemContainerStyle>
```

`TreeView.SelectedItem` は<strong>読み取り専用</strong>で、バインディングできません。代わりに、各 `TreeViewItem` の `IsSelected` を、データの `IsSelected` とバインドします。これで、

- ツリーでクリックすると、`SceneObject.IsSelected = true` になる。
- コードで `IsSelected = true` にすると、ツリーの選択が追従する（ビューポートで選んだとき）。

ただし、ツリーのクリックで `IsSelected` が変わっても、`ISelectionService` には届きません。ツリーのクリックを `ISelectionService` に伝える必要があります。

### ツリーの選択をサービスに伝える

`TreeView` の `SelectedItemChanged` を、コードビハインドから、ビューモデルに橋渡しします。

```xml
<TreeView x:Name="Tree" … SelectedItemChanged="OnTreeSelectedItemChanged">
```

```csharp
using System.Windows;
using System.Windows.Controls;

using Editor.Models;
using Editor.Modules.SceneTree.ViewModels;

namespace Editor.Modules.SceneTree.Views;

public partial class SceneTreeView : UserControl
{
    public SceneTreeView()
    {
        InitializeComponent();
    }

    private SceneTreeViewModel? ViewModel => DataContext as SceneTreeViewModel;

    private void OnTreeSelectedItemChanged(object sender, RoutedPropertyChangedEventArgs<object> e)
    {
        if (e.NewValue is SceneObject obj) ViewModel?.OnItemSelected(obj);
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `SelectedItemChanged` | 選択項目が変わったときのイベント |
| `RoutedPropertyChangedEventArgs<object>` | 変更の前後の値（`OldValue`、`NewValue`）を持つ引数 |
| `e.NewValue is SceneObject obj` | 型の判定と取り出しを一度に行うパターン |

!!! note "ここでの無限ループに注意"
    `SelectionService.Select(obj)` が `obj.IsSelected = true` にする → ツリーが選択を更新 → `SelectedItemChanged` が呼ばれる → `OnItemSelected` → `Select(obj)` …と、ぐるぐる回りそうに見えます。実際は、`Select` が「すでに同じ物が先頭ならば、変えない」ときに、ほぼ止まります。念のため、`Select` の先頭で、<strong>同じ選択なら何もせず戻る</strong>検査を入れておくと安全です。

## 手順 4：右クリック メニュー

```xml
<TreeView.ContextMenu>
    <ContextMenu>
        <MenuItem Header="空のオブジェクトを追加" Command="{Binding AddEmptyCommand}" />
        <MenuItem Header="子を追加" Command="{Binding AddChildCommand}" />
        <MenuItem Header="名前の変更 (F2)" Command="{Binding RenameCommand}" />
        <Separator />
        <MenuItem Header="削除 (Del)" Command="{Binding DeleteCommand}" />
    </ContextMenu>
</TreeView.ContextMenu>
```

`ContextMenu` は、ビジュアル ツリーの<strong>外</strong>にある独立したウィンドウなので、`{Binding}` が `DataContext` を引き継ぎません。このメニューのコマンドが効かないときは、`PlacementTarget` を経由します。

```xml
<MenuItem Header="削除"
          Command="{Binding PlacementTarget.DataContext.DeleteCommand,
                            RelativeSource={RelativeSource AncestorType=ContextMenu}}" />
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `ContextMenu` | 右クリックで出るメニュー。`TreeView.ContextMenu` に設定する |
| `RelativeSource={RelativeSource AncestorType=ContextMenu}` | バインディング元を、「<strong>祖先の `ContextMenu`</strong>」にする |
| `PlacementTarget` | `ContextMenu` を開いた元の部品（ここでは `TreeView`）。その `DataContext` が、ビューモデル |

## 手順 5：ドラッグ アンド ドロップ

ツリーの項目をドラッグして、別の項目の上にドロップすると、親子関係を変えます。`SceneTreeView.xaml.cs` に書きます。

### ドラッグの開始

```csharp
private Point _dragStart;
private SceneObject? _dragged;

// XAML: PreviewMouseLeftButtonDown="OnPreviewMouseLeftButtonDown" PreviewMouseMove="OnPreviewMouseMove"
private void OnPreviewMouseLeftButtonDown(object sender, MouseButtonEventArgs e)
{
    _dragStart = e.GetPosition(null);                       // 画面全体の座標
    _dragged = FindObjectAt(e.OriginalSource as DependencyObject);
}

private void OnPreviewMouseMove(object sender, MouseEventArgs e)
{
    if (e.LeftButton != MouseButtonState.Pressed || _dragged == null) return;

    Vector delta = e.GetPosition(null) - _dragStart;
    if (Math.Abs(delta.X) < SystemParameters.MinimumHorizontalDragDistance &&
        Math.Abs(delta.Y) < SystemParameters.MinimumVerticalDragDistance)
    {
        return;                                              // まだ「クリック」の範囲
    }

    var data = new DataObject(typeof(SceneObject), _dragged);
    DragDrop.DoDragDrop(Tree, data, DragDropEffects.Move);   // ここで、ドラッグが終わるまで戻らない
    _dragged = null;
}

// クリックされた部品から、親をたどって TreeViewItem を探し、その物を返す
private static SceneObject? FindObjectAt(DependencyObject? source)
{
    while (source != null && source is not TreeViewItem)
    {
        source = VisualTreeHelper.GetParent(source);
    }
    return (source as TreeViewItem)?.DataContext as SceneObject;
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `PreviewMouseLeftButtonDown` | <strong>Preview</strong> で始まるイベントは、<strong>トンネリング</strong>（親から子へ向かって伝わる）。通常のイベント（バブリング）より先に、親で受け取れる |
| `e.GetPosition(null)` | マウスの位置。`null` を渡すと、ウィンドウ全体の座標 |
| `SystemParameters.MinimumHorizontalDragDistance` | OS が決める「ドラッグとみなす最小の距離」（通常 4 ピクセル）。これ未満はクリック扱い |
| `DataObject(typeof(SceneObject), _dragged)` | ドラッグするデータの入れ物。型と値のペア |
| `DragDrop.DoDragDrop` | ドラッグ操作を始める。ドロップされるまで戻らない |
| `DragDropEffects.Move` | 「移動」の操作であることを示す |
| `e.OriginalSource` | 実際にクリックされた部品（`TextBlock` など）。そこから `VisualTreeHelper.GetParent` で、親をたどって `TreeViewItem` を探す |
| `VisualTreeHelper` | ビジュアル ツリー（部品の入れ子）をたどる静的クラス |
| `source is not TreeViewItem` | 型が違う間、ループする |

### ドロップ

```csharp
// XAML: DragOver="OnDragOver" Drop="OnDrop"
private void OnDragOver(object sender, DragEventArgs e)
{
    e.Effects = e.Data.GetDataPresent(typeof(SceneObject)) ? DragDropEffects.Move : DragDropEffects.None;
    e.Handled = true;
}

private void OnDrop(object sender, DragEventArgs e)
{
    if (e.Data.GetData(typeof(SceneObject)) is not SceneObject dragged) return;

    var target = FindObjectAt(e.OriginalSource as DependencyObject);   // 空白にドロップ → null（最上位へ）
    if (target == dragged) return;
    ViewModel?.Reparent(dragged, target);
    e.Handled = true;
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `DragOver` | ドラッグ中、部品の上を通るたびに呼ばれる。ここで、<strong>ドロップを許可するか</strong>を `e.Effects` で答える |
| `e.Data.GetDataPresent(型)` | ドラッグされているデータが、その型を含むか |
| `e.Data.GetData(型)` | データを取り出す。`is not SceneObject dragged` で、型の確認と取り出しを一度に |
| `Drop` | ドロップされたときに呼ばれる |
| 空白へのドロップ | `FindObjectAt` が `null` を返し、`Reparent(dragged, null)`。<strong>最上位に戻す</strong>操作になる |

## 動作確認

| 操作 | 期待する結果 |
| --- | --- |
| 「＋ 追加」 | ツリーに項目が増え、ビューポートに箱が出る。選択され、黄色になる |
| 項目をクリック | ビューポートの箱が黄色になる。ほかは灰色 |
| 「＋ 子」 | 選択中の物の下に、子が作られる（ツリーでは入れ子になる）。子は親の上方に表示される |
| `F2` | 名前が編集できる。`Enter` か、フォーカスを外すと確定 |
| `Delete` | 選択中の物と、その子が消える。ビューポートからも消える |
| ドラッグ アンド ドロップ | 別の項目の上にドロップすると、その子になる。空白へのドロップで、最上位に戻る |
| 自分の子孫の下へドロップ | 何も起きない |
| 親を動かす（第 22 章以降） | 子が追従する |

## よくあるミス

??? failure "ツリーに何も出ない"
    `ItemsSource` のバインディングが失敗している（出力ウィンドウを確認）。`HierarchicalDataTemplate` の `DataType` が合っていない。`xmlns:models` の名前空間の指定違い。

??? failure "展開や選択が、保存されない／おかしくなる"
    `TreeViewItem` は、画面外に出ると<strong>再利用</strong>（仮想化）される。状態を `TreeViewItem` ではなく、データの `IsExpanded`、`IsSelected` に持たせているので、再利用されても崩れない。

??? failure "`F2` を押しても、編集にならない"
    `TextBox` にフォーカスが移っていない。`IsEditing` が `true` になった直後に、`TextBox` に `Focus()` を呼ぶ処理が要る。簡単な方法は、`TextBox.Loaded` で `Focus` と `SelectAll` を呼ぶこと。

??? failure "ドラッグがすぐ始まって、クリックで選択できない"
    `MinimumHorizontalDragDistance` の検査を入れていない。

??? failure "右クリックのメニューが、反応しない"
    `ContextMenu` は `DataContext` を引き継がない。`PlacementTarget.DataContext` 経由で、コマンドを指す。

??? failure "削除したのに、ツリーに残る"
    `Destroy` で `Children`／`Roots` から `Remove` していない。`ObservableCollection` から消さないと、画面は変わらない。

## この章のまとめ

- ツリーは<strong>ドキュメントを見る</strong>だけ。変更はコマンドで、ドキュメントを変える。
- 選択は `ISelectionService` を介して、ツリー、ビューポート、プロパティで共有する。
- `HierarchicalDataTemplate` で、木の見た目と、子の取り出し方を決める。
- `TreeViewItem` の `IsSelected` と `IsExpanded` を、データにバインドする。
- ドラッグ アンド ドロップは `DoDragDrop` / `DragOver` / `Drop`。

## 次の章へ

次の章（[第 22 章 プロパティ パネル](22-property-panel.md)）では、選択中の物の位置、回転、拡大、色を<strong>入力欄で編集</strong>できるようにします。数値の入力、スライダー、色の選択、複数の物の編集を扱います。
