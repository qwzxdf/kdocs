---
title: 第 41 章 シーン ツリー
tags:
  - C#連携
---

# 第 41 章 シーン ツリー

この章では、`SceneDocument` を木（ツリー）として表示して、物の選択、名前の変更、追加、削除、そしてドラッグ アンド ドロップによる親子づけができるようにします。`TreeView`、`HierarchicalDataTemplate`、右クリック メニュー、キー操作、ドラッグ アンド ドロップが一度に出てくる章です。

!!! info "このページを読む前に"
    - [第 40 章 シーンのデータと API](40-scene-api.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## ツリーはドキュメントの見た目にすぎない

シーン ツリーの原則は、第 14 章の MVVM と同じです。ツリーは、`SceneDocument.Roots`（`ObservableCollection`）をバインディングで見るだけです。追加や削除はコマンドでドキュメントを変えて、変わったドキュメントを見て、ツリーが自動で更新されます。`TreeViewItem` をコードから直接いじることは、しません。

選択も同じ考え方です。「いま何が選ばれているか」は、ツリーだけの話ではありません。ビューポート（黄色い枠）も、プロパティ パネルも知りたい情報です。そこで、選択を持つサービス（`ISelectionService`）を作って、ツリー、ビューポート、プロパティの 3 者がそのサービスを介してやり取りする形にします（第 24 章の考え方です）。

```text
ツリーで選ぶ ─▶ ISelectionService ─▶ プロパティ パネルが切り替わる
ビューポートで選ぶ ─▶       │      ─▶ ツリーの選択表示が追従
                           └──────▶ エンジンの強調表示（黄色）
```

## 選択サービス

第 24 章では、1 つだけ選べる簡易版（`SceneObjectViewModel` を 1 つ持つ）を書きました。ここで、シーンの物（`SceneObject`）を、複数持てる形に作り直します。

```csharp title="Services/ISelectionService.cs"
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

```csharp title="Services/SelectionService.cs"
using Editor.Models;

namespace Editor.Services;

public sealed class SelectionService : ISelectionService
{
    private readonly List<SceneObject> _selection = new();
    private readonly IRenderLoop _loop;

    public SelectionService(SceneDocument document, IRenderLoop loop)
    {
        _loop = loop;
        // 選択中の物がドキュメントから消えたら、選択からも外す
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

`IReadOnlyList<T>` は、読み取り専用のリストです。`List<T>` をこの型で見せれば、外から `Add` される心配がありません。最後に選んだ物を `Insert(0, obj)` で先頭に入れて、それを `Primary`（主の選択）と呼びます。

`RaiseChanged` の `_selection.Select(o => o.Id).ToArray()` の `Select` は、LINQ の変換用の関数で、クラス自身の `Select` メソッドとは別物です。ここで ID の配列を作ってから `Post` している点にも注目してください。描画スレッドで実行される時点の選択ではなく、今の選択のコピーを送るためです（第 40 章と同じ理由です）。

`SceneObject` には、画面の状態を持たせるプロパティを足します。保存はしない値です。

```csharp
// SceneObject.cs に追加
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

エンジンに選択を伝えるために、`IEngineService` に `SceneSetSelection(uint[] ids)` を足して、P/Invoke の宣言も書きます。

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

`fixed (uint* p = ids)` は、配列をピン留めして（GC に動かされないようにして）先頭のポインターを得る書き方です。ブロックを出ると解除されます。配列を C++ に渡すときの定番です。長さ 0 の配列だと `p` が `null` になりますが、C++ 側が `count == 0` のとき `ids` を読まない作りにしてあるので（第 40 章）、問題ありません。

## ビューモデル

```csharp title="Modules/SceneTree/SceneTreeViewModel.cs"
using System.Collections.ObjectModel;
using System.Numerics;
using Prism.Commands;
using Prism.Mvvm;

using Editor.Models;
using Editor.Services;

namespace Editor.Modules.SceneTree;

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

    // ツリーで選ばれた（ビューのコードビハインドから呼ぶ）
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

選択が必要なコマンド（子を追加、削除、名前の変更）は、`DelegateCommand` の第 2 引数に `() => _selection.Primary != null` を渡して、選択があるときだけ押せるようにしています。選択が変わったら `RaiseCanExecuteChanged()` で、押せるかどうかを聞き直させます（第 14 章）。`Roots` は、ドキュメントの `Roots` をそのまま公開しているだけで、ツリーはドキュメントを直接見る形になります。

`Reparent` の空の `catch` に注目してください。輪になる移動は、想定内の失敗なので、静かに無視します。ただし、握りつぶすのは `InvalidOperationException` だけです。想定外の例外まで握りつぶさないように、型を限定しています。

## ビュー（XAML）

まず、ツール バーとツリーの骨組みです。

```xml title="SceneTreeView.xaml"
<UserControl x:Class="Editor.Modules.SceneTree.SceneTreeView"
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

`TreeView` の `ItemsSource` には、最上位の要素の集まりを渡します。`AllowDrop="True"` は、ドラッグ アンド ドロップを受ける側になれる指定です。`InputBindings` の `KeyBinding` は、キー操作をコマンドに結びます（`Modifiers="Control" Key="D"` のように、修飾キー付きも書けます）。

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

`HierarchicalDataTemplate` は、`DataTemplate` に「子の集まりをどこから取るか」（`ItemsSource="{Binding Children}"`）を加えたものです。子も同じテンプレートで、再帰的に表示されます。`DataType="{x:Type models:SceneObject}"` と書くと、「この型のデータには、自動でこのテンプレートを使う」という意味になり、`ItemTemplate` を書かなくても、型で選ばれます。

名前の部分は、通常は `TextBlock` で表示して、`F2` で `IsEditing` が `true` になったら、`TextBlock` を隠して `TextBox` を出す、という切り替えをしています。切り替えには `DataTrigger`（データの値に応じて見た目を変えるトリガー。第 11 章）を使いました。

### 選択と展開をバインドする

```xml
<TreeView.ItemContainerStyle>
    <Style TargetType="TreeViewItem">
        <Setter Property="IsSelected" Value="{Binding IsSelected, Mode=TwoWay}" />
        <Setter Property="IsExpanded" Value="{Binding IsExpanded, Mode=TwoWay}" />
    </Style>
</TreeView.ItemContainerStyle>
```

`TreeView.SelectedItem` は読み取り専用なので、バインディングできません。そこで、各 `TreeViewItem` の `IsSelected` をデータの `IsSelected` にバインドします。これで、ツリーでクリックすると `SceneObject.IsSelected = true` になり、コードで `IsSelected = true` にすると（ビューポートで選んだときなど）ツリーの選択も追従します。

ただし、これだけでは、ツリーのクリックが `ISelectionService` に届きません。クリックを伝える橋をコードビハインドに作ります。

### ツリーの選択をサービスに伝える

```xml
<TreeView x:Name="Tree" ... SelectedItemChanged="OnTreeSelectedItemChanged">
```

```csharp title="SceneTreeView.xaml.cs"
using System.Windows;
using System.Windows.Controls;

using Editor.Models;

namespace Editor.Modules.SceneTree;

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

`e.NewValue is SceneObject obj` で、型の確認と取り出しを一度にやっています。

!!! note "無限ループにならないか？"
    `Select(obj)` が `obj.IsSelected = true` にする → ツリーが更新される → `SelectedItemChanged` が呼ばれる → `OnItemSelected` → `Select(obj)`、と、ぐるぐる回りそうに見えます。実際は、「すでに同じ物が先頭にあるなら何もしない」ことで止まります。念のため、`Select` の先頭に同じ選択なら何もせず戻る検査を入れておくと安全です。

## 右クリック メニュー

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

`ContextMenu` は、部品の木の外にある独立したウィンドウなので、`{Binding}` が `DataContext` を引き継ぎません。メニューのコマンドが効かないときは、`PlacementTarget`（`ContextMenu` を開いた元の部品、ここでは `TreeView`）を経由して、その `DataContext`（ビューモデル）を指します。

```xml
<MenuItem Header="削除"
          Command="{Binding PlacementTarget.DataContext.DeleteCommand,
                            RelativeSource={RelativeSource AncestorType=ContextMenu}}" />
```

`RelativeSource={RelativeSource AncestorType=ContextMenu}` は、「祖先の `ContextMenu`」をバインディングの元にする書き方です（第 15 章）。

## ドラッグ アンド ドロップで親子を変える

ツリーの項目を別の項目の上にドロップすると、親子関係が変わるようにします。コードビハインドに書きます。

### ドラッグを始める

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

`Preview` で始まるイベント（`PreviewMouseLeftButtonDown`）は、トンネリングといって、親から子へ向かって伝わるので、通常のイベントより先に、親で受け取れます（第 10 章）。

マウスを少し動かしただけでドラッグを始めてしまうと、クリックで選択できなくなります。そこで、OS が決めている「ドラッグとみなす最小の距離」（`SystemParameters.MinimumHorizontalDragDistance`、通常 4 ピクセル）を超えるまでは、クリック扱いにしています。距離を超えたら `DragDrop.DoDragDrop` でドラッグを始めます。ドロップされるまで、この関数は戻りません。

クリックされた場所の部品（`e.OriginalSource`）は、たいてい中の `TextBlock` などです。そこから `VisualTreeHelper.GetParent` で親をたどって、`TreeViewItem` を探し、そのデータ（`SceneObject`）を取り出しています。

### ドロップを受ける

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

`DragOver` は、ドラッグ中に部品の上を通るたびに呼ばれ、ここで「ドロップを許可するか」を `e.Effects` で答えます。`Drop` で、ドラッグされてきたデータを取り出して、ビューモデルの `Reparent` を呼びます。空白にドロップしたときは `FindObjectAt` が `null` を返すので、最上位に戻す操作になります。

## 動かして確かめる

- 「＋ 追加」で、ツリーに項目が増え、ビューポートに箱が出て、黄色になる。
- 項目をクリックすると、その箱が黄色になって、ほかは灰色になる。
- 「＋ 子」で、選択中の物の下に子ができる（ツリーでは入れ子になる）。
- `F2` で名前を編集できる。`Enter` かフォーカスを外すと確定する。
- `Delete` で、選択中の物と子が消える。ビューポートからも消える。
- 別の項目の上にドロップすると、その子になる。空白へのドロップで最上位に戻る。自分の子孫の下へのドロップは、何も起きない。

??? failure "ツリーに何も出ない"
    `ItemsSource` のバインディングが失敗しています（出力ウィンドウを見ます）。`HierarchicalDataTemplate` の `DataType` が合っていないか、`xmlns:models` の指定が違っているかもしれません。

??? failure "展開や選択の状態がおかしくなる"
    `TreeViewItem` は画面外に出ると再利用されます。状態を `TreeViewItem` ではなく、データの `IsExpanded` / `IsSelected` に持たせていれば、再利用されても崩れません。

??? failure "`F2` を押しても、編集にならない"
    `TextBox` にフォーカスが移っていません。`IsEditing` が `true` になった直後に `TextBox` に `Focus()` を呼ぶ処理が要ります。`TextBox.Loaded` で `Focus` と `SelectAll` を呼ぶのが簡単です。

??? failure "ドラッグがすぐ始まって、クリックで選択できない"
    `MinimumHorizontalDragDistance` の検査が抜けています。

??? failure "右クリックのメニューが反応しない"
    `ContextMenu` は `DataContext` を引き継ぎません。`PlacementTarget.DataContext` 経由で、コマンドを指します。

??? failure "削除したのに、ツリーに残る"
    `Destroy` で `Children` / `Roots` から `Remove` していません。`ObservableCollection` から消さないと、画面は変わりません。

## この章のまとめ

- ツリーはドキュメントを見るだけ。変更はコマンドでドキュメントを変える。
- 選択は `ISelectionService` を介して、ツリー、ビューポート、プロパティで共有する。
- 木の見た目と子の取り出し方は、`HierarchicalDataTemplate` で決める。
- `TreeViewItem` の `IsSelected` と `IsExpanded` をデータにバインドする。
- ドラッグ アンド ドロップは、`DoDragDrop`、`DragOver`、`Drop` の組み合わせ。

次の章では、選択中の物の位置、回転、拡大、色を入力欄で編集できるようにします。

[第 42 章 プロパティ パネル](42-property-panel.md) へ進みます。
