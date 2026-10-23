---
title: 第 40 章 アセット ブラウザ
tags:
  - C#連携
---

# 第 40 章 アセット ブラウザ

この章で、プロジェクトのフォルダーの中身（シーン、テクスチャ、モデル…）を一覧する、アセット ブラウザを作ります。フォルダーの木、ファイルの一覧、検索、画像のサムネイル、フォルダーの変更の自動検出、そしてファイルをビューポートへドラッグ アンド ドロップして物を置く操作までを扱います。第 5 部（エディタの機能）の最後の章です。

!!! info "このページを読む前に"
    - [第 39 章 保存と読み込み](39-save-load.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## 作る前に知っておく 4 つの問題

アセット ブラウザは、ファイル システムの見た目です。作り始めると、次の問題にぶつかります。

| 問題 | 内容 | 対処 |
| --- | --- | --- |
| ファイルが多い | 数千のファイルを一度に UI へ載せると遅い | 仮想化（見える分だけ作る）。サムネイルは非同期 |
| 画像の読み込みが重い | 4096×4096 の画像をそのまま読むと、メモリも時間もかかる | 小さく読む（`DecodePixelWidth`）。UI スレッド以外で読む |
| 外部の変更 | エクスプローラーでファイルを追加／削除しても、画面を更新したい | `FileSystemWatcher` で監視する |
| スレッド | 監視のイベントは別のスレッドから来る。UI は触れない | UI スレッドに戻してから更新する |

この章のゴールは次のとおりです。

- プロジェクト フォルダーを選ぶと、左にフォルダーの木、右にファイルの一覧が出る。
- 検索ボックスでファイル名を絞り込める。画像はサムネイルが出る。
- エクスプローラーでファイルを追加／削除すると、自動で更新される。
- `.scene` をダブルクリックで開ける。
- ファイルをビューポートへドロップすると、その位置に物が置かれる。

## 項目（AssetEntry）

フォルダーまたはファイル 1 つ分を表すモデルです。

```csharp title="Models/AssetEntry.cs"
using System.Windows.Media;
using Prism.Mvvm;

namespace Editor.Models;

public enum AssetKind { Folder, Scene, Texture, Model, Shader, Other }

// フォルダーまたはファイル 1 つ分
public class AssetEntry : BindableBase
{
    public AssetEntry(string fullPath, bool isDirectory)
    {
        FullPath = fullPath;
        IsDirectory = isDirectory;
        Name = Path.GetFileName(fullPath);
        Kind = isDirectory ? AssetKind.Folder : KindOf(Path.GetExtension(fullPath));
    }

    public string FullPath { get; }
    public string Name { get; }
    public bool IsDirectory { get; }
    public AssetKind Kind { get; }

    // 一覧に出す、小さな記号（アイコンの代わり）
    public string Glyph => Kind switch
    {
        AssetKind.Folder => "📁",
        AssetKind.Scene => "🎬",
        AssetKind.Texture => "🖼",
        AssetKind.Model => "🧊",
        AssetKind.Shader => "📜",
        _ => "📄",
    };

    // サムネイル（画像のとき、あとから非同期で設定される）
    private ImageSource? _thumbnail;
    public ImageSource? Thumbnail
    {
        get => _thumbnail;
        set => SetProperty(ref _thumbnail, value);
    }

    private static AssetKind KindOf(string extension) => extension.ToLowerInvariant() switch
    {
        ".scene" => AssetKind.Scene,
        ".png" or ".jpg" or ".jpeg" or ".bmp" or ".tga" => AssetKind.Texture,
        ".gltf" or ".glb" or ".fbx" or ".obj" => AssetKind.Model,
        ".hlsl" or ".hlsli" => AssetKind.Shader,
        _ => AssetKind.Other,
    };
}
```

`Path.GetFileName` と `Path.GetExtension` で、パスからファイル名と拡張子（`.png`）を取り出します。拡張子の比較は、大文字小文字を区別したくないので、`ToLowerInvariant()`（カルチャーに依存しない小文字化）にそろえます。`".png" or ".jpg" or …` は switch 式のパターンで、複数の値のどれかに当てはまる、という意味です。

アイコンの代わりに絵文字を使っているのは、画像ファイルを用意せずに済ませる簡易な方法です。フォントによって見え方が変わるので、本格的には画像リソースを用意します。`ImageSource` は WPF の画像の基底クラスで、`BitmapImage` などがこれを継承しています。

## サービス

フォルダーの一覧と、変更の監視を担当するサービスです。

```csharp title="Services/IAssetService.cs"
using Editor.Models;

namespace Editor.Services;

public interface IAssetService
{
    string? RootPath { get; }
    void SetRoot(string path);

    // フォルダーの直下の項目（フォルダーが先、名前順）
    IReadOnlyList<AssetEntry> List(string folder);

    // 何かが変わった（追加、削除、名前変更）。UI スレッドで通知される
    event Action<string>? FolderChanged;
}
```

```csharp title="Services/AssetService.cs"
using System.IO;
using System.Windows.Threading;
using Editor.Models;

namespace Editor.Services;

public sealed class AssetService : IAssetService, IDisposable
{
    private FileSystemWatcher? _watcher;
    private readonly DispatcherTimer _debounce;
    private readonly HashSet<string> _pending = new();

    public AssetService()
    {
        // 変更の通知は、短い間にたくさん来ることがある。0.3 秒まとめてから、1 度だけ通知する。
        _debounce = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(300) };
        _debounce.Tick += (_, _) =>
        {
            _debounce.Stop();
            var folders = _pending.ToList();
            _pending.Clear();
            foreach (var folder in folders) FolderChanged?.Invoke(folder);
        };
    }

    public string? RootPath { get; private set; }
    public event Action<string>? FolderChanged;

    public void SetRoot(string path)
    {
        _watcher?.Dispose();
        RootPath = path;

        _watcher = new FileSystemWatcher(path)
        {
            IncludeSubdirectories = true,
            NotifyFilter = NotifyFilters.FileName | NotifyFilters.DirectoryName | NotifyFilters.LastWrite,
            EnableRaisingEvents = true,
        };
        _watcher.Created += OnWatcherEvent;
        _watcher.Deleted += OnWatcherEvent;
        _watcher.Renamed += (s, e) => OnWatcherEvent(s, e);
        _watcher.Error += (_, _) => { /* バッファーがあふれたとき。全体の再読み込みで復旧する */ };
    }

    // 注意：FileSystemWatcher のイベントは、UI ではない別のスレッドで呼ばれる
    private void OnWatcherEvent(object sender, FileSystemEventArgs e)
    {
        string? folder = Path.GetDirectoryName(e.FullPath);
        if (folder == null) return;
        System.Windows.Application.Current.Dispatcher.BeginInvoke(() =>
        {
            _pending.Add(folder);
            _debounce.Stop();
            _debounce.Start();                       // タイマーを延長する（デバウンス）
        });
    }

    public IReadOnlyList<AssetEntry> List(string folder)
    {
        try
        {
            var dirs = Directory.EnumerateDirectories(folder)
                .Where(d => !Path.GetFileName(d).StartsWith('.'))             // 隠しフォルダー（.git など）を除く
                .OrderBy(d => d, StringComparer.OrdinalIgnoreCase)
                .Select(d => new AssetEntry(d, true));
            var files = Directory.EnumerateFiles(folder)
                .OrderBy(f => f, StringComparer.OrdinalIgnoreCase)
                .Select(f => new AssetEntry(f, false));
            return dirs.Concat(files).ToList();
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException)
        {
            return Array.Empty<AssetEntry>();
        }
    }

    public void Dispose() => _watcher?.Dispose();
}
```

`FileSystemWatcher` は、フォルダーを監視して `Created`、`Deleted`、`Renamed` などを通知する標準クラスです。`IncludeSubdirectories` でサブフォルダーも対象にし、`EnableRaisingEvents = true` で監視を始めます。

このクラスで気をつけるのは、2 つです。

1つ目は、`FileSystemWatcher` のイベントが、UI ではない別のスレッドで呼ばれることです。UI のタイマーや `HashSet` をそのスレッドから触ると、おかしくなります。だから、`Dispatcher.BeginInvoke` で UI スレッドへ回してから触っています（第 18 章）。

2つ目は、通知が短時間に何度も来ることです。ファイル 1 つをコピーしただけでも、複数のイベントが飛んできます。そのたびに一覧を更新すると、重くてちらつきます。そこでデバウンスを使います。イベントが来るたびにタイマーを延長して、0.3 秒、何も来なくなってから 1 回だけ通知します。

`List` の `Directory.EnumerateFiles` は、全部を配列にする `GetFiles` と違い、遅延評価で 1 つずつ取り出します。`OrderBy(…, StringComparer.OrdinalIgnoreCase)` で大文字小文字を区別せずに並べ、フォルダーを先に、ファイルを後に連結しています。`.git` のような隠しフォルダーは除きます。

なお、`FileSystemWatcher` は内部のバッファーがあふれると `Error` を起こして、変更の一部を取りこぼします。そのときは、全体を読み直すのが安全です。

## ビューモデル

```csharp title="Modules/Asset/ViewModels/AssetViewModel.cs"
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Windows.Data;
using Microsoft.Win32;
using Prism.Commands;
using Prism.Mvvm;

using Editor.Models;
using Editor.Services;

namespace Editor.Modules.Asset.ViewModels;

public class AssetViewModel : BindableBase
{
    private readonly IAssetService _assets;
    private readonly ISceneFileService _files;
    private string? _currentFolder;
    private string _filterText = "";

    public AssetViewModel(IAssetService assets, ISceneFileService files)
    {
        _assets = assets;
        _files = files;

        Entries = new ObservableCollection<AssetEntry>();
        EntriesView = CollectionViewSource.GetDefaultView(Entries);
        EntriesView.Filter = o => o is AssetEntry e && (FilterText.Length == 0 || e.Name.Contains(FilterText, StringComparison.OrdinalIgnoreCase));

        OpenProjectCommand = new DelegateCommand(OpenProject);
        UpCommand = new DelegateCommand(Up, () => CanGoUp);
        OpenEntryCommand = new DelegateCommand<AssetEntry>(OpenEntry);

        _assets.FolderChanged += folder =>
        {
            // 見ているフォルダーが変わったら、読み直す（サブフォルダーのツリーも）
            if (string.Equals(folder, _currentFolder, StringComparison.OrdinalIgnoreCase)) Reload();
            RefreshTree();
        };
    }

    public string Title => "アセット";

    // ── ファイル一覧 ──
    public ObservableCollection<AssetEntry> Entries { get; }
    public ICollectionView EntriesView { get; }

    public string FilterText
    {
        get => _filterText;
        set
        {
            if (SetProperty(ref _filterText, value)) EntriesView.Refresh();     // 絞り込みを、かけ直す
        }
    }

    public string CurrentFolderDisplay => _currentFolder ?? "（プロジェクト フォルダーを選んでください）";

    // ── フォルダーの木 ──
    public ObservableCollection<FolderNode> Roots { get; } = new();

    public DelegateCommand OpenProjectCommand { get; }
    public DelegateCommand UpCommand { get; }
    public DelegateCommand<AssetEntry> OpenEntryCommand { get; }

    private bool CanGoUp =>
        _currentFolder != null && _assets.RootPath != null &&
        !string.Equals(_currentFolder, _assets.RootPath, StringComparison.OrdinalIgnoreCase);

    private void OpenProject()
    {
        var dialog = new OpenFolderDialog { Title = "プロジェクト フォルダーを選択" };
        if (dialog.ShowDialog() != true) return;
        _assets.SetRoot(dialog.FolderName);
        RefreshTree();
        Navigate(dialog.FolderName);
    }

    public void Navigate(string folder)
    {
        _currentFolder = folder;
        RaisePropertyChanged(nameof(CurrentFolderDisplay));
        UpCommand.RaiseCanExecuteChanged();
        Reload();
    }

    private void Reload()
    {
        Entries.Clear();
        if (_currentFolder == null) return;
        foreach (var entry in _assets.List(_currentFolder))
        {
            Entries.Add(entry);
            if (entry.Kind == AssetKind.Texture) _ = LoadThumbnailAsync(entry);      // 画像は、サムネイルを非同期で読む
        }
    }

    private void Up()
    {
        var parent = Path.GetDirectoryName(_currentFolder);
        if (parent != null) Navigate(parent);
    }

    private async void OpenEntry(AssetEntry entry)
    {
        if (entry.IsDirectory) Navigate(entry.FullPath);
        else if (entry.Kind == AssetKind.Scene) await _files.OpenPathAsync(entry.FullPath);
    }
```

検索の絞り込みに使っている `CollectionViewSource.GetDefaultView(コレクション)` は、コレクションを加工して見せる窓（`ICollectionView`）です。元のコレクションは変えずに、絞り込み、並べ替え、グループ化ができます。`Filter` に条件（`true` を返した要素だけが表示される）を渡し、条件が変わったら `Refresh()` でかけ直します。ビューには、元の `Entries` ではなく `EntriesView` を渡す点に注意してください。

`OpenFolderDialog` は、.NET 8 で WPF に加わった、フォルダーを選ぶ標準ダイアログです。`_ = LoadThumbnailAsync(entry)` の `_ =` は、「`Task` を待たずに開始して、戻り値は意図して無視する」という書き方です。`OpenEntry` は `async void` ですが、コマンドのハンドラーなので許されます。例外が漏れると落ちるので、`OpenPathAsync` の内部で例外を処理する形にします。

`ISceneFileService` には、パスを指定して開く `OpenPathAsync(string path)` を足します。第 39 章の `OpenAsync` から、ダイアログの部分を取り出した形です。

### フォルダーの木

```csharp
// 左の木の 1 項目
public class FolderNode : BindableBase
{
    public FolderNode(string path) { Path = path; Name = System.IO.Path.GetFileName(path); }

    public string Path { get; }
    public string Name { get; }
    public ObservableCollection<FolderNode> Children { get; } = new();

    private bool _isExpanded;
    public bool IsExpanded { get => _isExpanded; set => SetProperty(ref _isExpanded, value); }
}

private void RefreshTree()
{
    Roots.Clear();
    if (_assets.RootPath is not { } root) return;
    var rootNode = new FolderNode(root) { IsExpanded = true };
    Fill(rootNode);
    Roots.Add(rootNode);
}

private void Fill(FolderNode node)
{
    foreach (var d in _assets.List(node.Path).Where(e => e.IsDirectory))
    {
        var child = new FolderNode(d.FullPath);
        Fill(child);
        node.Children.Add(child);
    }
}
```

大きなプロジェクトでは、すべてのサブフォルダーを最初に読むと遅くなります。本来は、ノードが展開されたときに読む（遅延読み込み）のが正解ですが、この教材では簡単さを優先しています。

### サムネイルの非同期読み込み

```csharp
private static readonly SemaphoreSlim ThumbnailGate = new(4);        // 同時に 4 枚まで

private static async Task LoadThumbnailAsync(AssetEntry entry)
{
    await ThumbnailGate.WaitAsync();
    try
    {
        // 画像の読み込みと縮小は、別のスレッドで行う
        ImageSource? image = await Task.Run(() =>
        {
            try
            {
                var bitmap = new BitmapImage();
                bitmap.BeginInit();
                bitmap.UriSource = new Uri(entry.FullPath);
                bitmap.DecodePixelWidth = 96;                          // 読み込むとき小さくする（メモリ節約）
                bitmap.CacheOption = BitmapCacheOption.OnLoad;         // すぐ読み込んで、ファイルを解放する
                bitmap.EndInit();
                bitmap.Freeze();                                       // スレッド間で共有できるようにする
                return (ImageSource?)bitmap;
            }
            catch
            {
                return null;                                           // 壊れた画像など
            }
        });
        entry.Thumbnail = image;                                       // await の後は UI スレッド
    }
    finally
    {
        ThumbnailGate.Release();
    }
}
```

ここは重い画像を扱うので、一つずつ理由を押さえます。

- `DecodePixelWidth = 96`：読み込む時点で縮小します。4096 ピクセルの画像でも、96 ピクセル分のメモリで済みます。あとから小さく表示するだけでは、元のサイズでメモリを使ってしまうので、必ず指定します。
- `BitmapCacheOption.OnLoad`：読み込みが終わったらファイルを閉じます。指定しないと、ファイルを掴みっぱなしで、削除や上書きができなくなります。
- `Freeze()`：変更不可にして、別のスレッドから渡せるようにします。凍結していない WPF のオブジェクトは、作ったスレッドでしか触れません。ここでは別のスレッドで作って、UI スレッドで使うので、必須です。
- `SemaphoreSlim(4)`：同時に入れる数を 4 に制限します。サムネイルを 1000 枚、一斉に読み始めると、メモリも CPU も尽きるからです。`WaitAsync` で枠を待ち、`finally` で必ず `Release` して返します。
- 壊れた画像は `null` を返して、サムネイルなし（記号のまま）にします。

## ビュー

```xml title="Views/AssetView.xaml"
<UserControl x:Class="Editor.Modules.Asset.Views.AssetView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:prism="http://prismlibrary.com/"
             xmlns:models="clr-namespace:Editor.Models"
             prism:ViewModelLocator.AutoWireViewModel="True">
    <DockPanel>
        <!-- 上：プロジェクトを開く、上へ、検索 -->
        <Grid DockPanel.Dock="Top" Margin="4">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="Auto" />
                <ColumnDefinition Width="Auto" />
                <ColumnDefinition Width="*" />
                <ColumnDefinition Width="180" />
            </Grid.ColumnDefinitions>
            <Button Grid.Column="0" Content="フォルダーを開く…" Command="{Binding OpenProjectCommand}" Padding="8,2" />
            <Button Grid.Column="1" Content="↑" Command="{Binding UpCommand}" Margin="4,0" Width="28" />
            <TextBlock Grid.Column="2" Text="{Binding CurrentFolderDisplay}" VerticalAlignment="Center" TextTrimming="CharacterEllipsis" />
            <TextBox Grid.Column="3" Text="{Binding FilterText, UpdateSourceTrigger=PropertyChanged}" />
        </Grid>

        <Grid>
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="180" />
                <ColumnDefinition Width="Auto" />
                <ColumnDefinition Width="*" />
            </Grid.ColumnDefinitions>

            <!-- 左：フォルダーの木 -->
            <TreeView x:Name="FolderTree" Grid.Column="0" ItemsSource="{Binding Roots}"
                      SelectedItemChanged="OnFolderSelected">
                <TreeView.ItemTemplate>
                    <HierarchicalDataTemplate ItemsSource="{Binding Children}">
                        <TextBlock Text="{Binding Name}" />
                    </HierarchicalDataTemplate>
                </TreeView.ItemTemplate>
                <TreeView.ItemContainerStyle>
                    <Style TargetType="TreeViewItem">
                        <Setter Property="IsExpanded" Value="{Binding IsExpanded, Mode=TwoWay}" />
                    </Style>
                </TreeView.ItemContainerStyle>
            </TreeView>
            <GridSplitter Grid.Column="1" Width="4" HorizontalAlignment="Stretch" />

            <!-- 右：ファイルの一覧（タイル表示） -->
            <ListBox x:Name="EntryList" Grid.Column="2" ItemsSource="{Binding EntriesView}"
                     SelectionMode="Extended" ScrollViewer.HorizontalScrollBarVisibility="Disabled"
                     PreviewMouseLeftButtonDown="OnEntryMouseDown" PreviewMouseMove="OnEntryMouseMove">
                <ListBox.ItemsPanel>
                    <ItemsPanelTemplate>
                        <WrapPanel />
                    </ItemsPanelTemplate>
                </ListBox.ItemsPanel>
                <ListBox.ItemTemplate>
                    <DataTemplate DataType="{x:Type models:AssetEntry}">
                        <StackPanel Width="84" Margin="4" ToolTip="{Binding FullPath}">
                            <Grid Height="64">
                                <Image Source="{Binding Thumbnail}" Stretch="Uniform" />
                                <TextBlock Text="{Binding Glyph}" FontSize="36" HorizontalAlignment="Center" VerticalAlignment="Center">
                                    <TextBlock.Style>
                                        <Style TargetType="TextBlock">
                                            <Style.Triggers>
                                                <!-- サムネイルがあれば、記号は隠す -->
                                                <DataTrigger Binding="{Binding Thumbnail, Converter={StaticResource NotNullToCollapsed}}" Value="True">
                                                    <Setter Property="Visibility" Value="Collapsed" />
                                                </DataTrigger>
                                            </Style.Triggers>
                                        </Style>
                                    </TextBlock.Style>
                                </TextBlock>
                            </Grid>
                            <TextBlock Text="{Binding Name}" TextAlignment="Center" TextTrimming="CharacterEllipsis" />
                        </StackPanel>
                    </DataTemplate>
                </ListBox.ItemTemplate>
                <ListBox.ItemContainerStyle>
                    <Style TargetType="ListBoxItem">
                        <EventSetter Event="MouseDoubleClick" Handler="OnEntryDoubleClick" />
                    </Style>
                </ListBox.ItemContainerStyle>
            </ListBox>
        </Grid>
    </DockPanel>
</UserControl>
```

一覧は、`ListBox` の `ItemsPanel` を `WrapPanel` に差し替えて、タイル状に折り返す並びにしています。リストの並べ方は、`ItemsPanelTemplate` で変えられます。`SelectionMode="Extended"` で `Ctrl`/`Shift` による複数選択ができ、`EventSetter` は、スタイルの中でイベント ハンドラーを結ぶための要素で、ここでは各項目のダブルクリックに使っています。`NotNullToCollapsed` は、`null` でなければ `True` を返すコンバーターです（第 12 章の要領で作ります）。

ここには落とし穴が 1 つあります。`ListBox` は既定で仮想化されますが、`WrapPanel` に変えると仮想化されなくなります。数千項目を扱うなら、別のライブラリを使うか、行ごとの表示に切り替える必要があります。

### コードビハインド

ドラッグのような、画面操作そのものの処理は、ビューのコードビハインドに置きます。

```csharp
private void OnFolderSelected(object sender, RoutedPropertyChangedEventArgs<object> e)
{
    if (e.NewValue is FolderNode node) ViewModel?.Navigate(node.Path);
}

private void OnEntryDoubleClick(object sender, MouseButtonEventArgs e)
{
    if ((sender as ListBoxItem)?.DataContext is AssetEntry entry) ViewModel?.OpenEntryCommand.Execute(entry);
}

// ── ドラッグ開始（ファイルをビューポートへ） ──
private Point _dragStart;
private void OnEntryMouseDown(object sender, MouseButtonEventArgs e) => _dragStart = e.GetPosition(null);

private void OnEntryMouseMove(object sender, MouseEventArgs e)
{
    if (e.LeftButton != MouseButtonState.Pressed) return;
    var delta = e.GetPosition(null) - _dragStart;
    if (Math.Abs(delta.X) < SystemParameters.MinimumHorizontalDragDistance &&
        Math.Abs(delta.Y) < SystemParameters.MinimumVerticalDragDistance) return;

    var paths = EntryList.SelectedItems.OfType<AssetEntry>().Where(a => !a.IsDirectory).Select(a => a.FullPath).ToArray();
    if (paths.Length == 0) return;
    var data = new DataObject(DataFormats.FileDrop, paths);        // ファイルのドラッグの標準形式
    DragDrop.DoDragDrop(EntryList, data, DragDropEffects.Copy);
}
```

ドラッグは、押した位置から少し動いてから始めます。クリックのつもりが、ほんの少しの手ぶれでドラッグになるのを防ぐためで、「少し」の目安は OS の値（`SystemParameters.MinimumHorizontalDragDistance` など）を使います。ドラッグするデータは `DataFormats.FileDrop`（ファイルのパスの `string[]`）という標準の形式にします。エクスプローラーからのドロップと同じ形式なので、受ける側は 1 つの処理で両方を扱えます。

## ビューポートへドロップ

ビューポートは `HwndHost`（子ウィンドウ）なので、WPF のドロップ（`AllowDrop` と `Drop` イベント）は効きません。子ウィンドウは WPF の外の Win32 のウィンドウだからです。そこで、Win32 の仕組み `WM_DROPFILES` を使います。

まず、`Win32.cs` に宣言を足します。

```csharp
public const int WM_DROPFILES = 0x0233;
public const int WS_EX_ACCEPTFILES = 0x00000010;

[LibraryImport("shell32.dll")]
public static partial void DragAcceptFiles(nint hwnd, [MarshalAs(UnmanagedType.Bool)] bool accept);

[LibraryImport("shell32.dll", EntryPoint = "DragQueryFileW", StringMarshalling = StringMarshalling.Utf16)]
public static partial uint DragQueryFile(nint drop, uint index, [Out] char[]? buffer, uint size);

[LibraryImport("shell32.dll")]
[return: MarshalAs(UnmanagedType.Bool)]
public static partial bool DragQueryPoint(nint drop, out POINT point);

[LibraryImport("shell32.dll")]
public static partial void DragFinish(nint drop);
```

`ViewportHost` の `BuildWindowCore` で `DragAcceptFiles(_hwnd, true)` を呼び、「このウィンドウはファイルのドロップを受け付ける」と宣言します。そして `WndProc` で、`WM_DROPFILES` を受け取ります。

```csharp
public event EventHandler<ViewportDropEventArgs>? FilesDropped;

// WndProc の中
case Win32.WM_DROPFILES:
{
    nint drop = wParam;
    uint count = Win32.DragQueryFile(drop, 0xFFFFFFFF, null, 0);       // ファイルの個数
    var paths = new List<string>();
    for (uint i = 0; i < count; ++i)
    {
        uint length = Win32.DragQueryFile(drop, i, null, 0);           // 文字数
        var buffer = new char[length + 1];
        Win32.DragQueryFile(drop, i, buffer, length + 1);
        paths.Add(new string(buffer, 0, (int)length));
    }
    Win32.DragQueryPoint(drop, out var point);                          // ドロップされた位置（クライアント座標）
    Win32.DragFinish(drop);                                              // 必ず呼ぶ（メモリの解放）
    FilesDropped?.Invoke(this, new ViewportDropEventArgs(paths, point.X, point.Y));
    handled = true;
    break;
}
```

`wParam` は、ドロップ情報のハンドル（`HDROP`）です。`DragQueryFile` の使い方は少し独特です。インデックスに `0xFFFFFFFF` を渡すとファイルの個数が返り、各ファイルについては、1 回目でバッファー無しで文字数を聞き、バッファーを用意してから、2 回目で受け取ります。C でよくある 2 段階の取得です。最後の `DragFinish` でドロップ情報を解放します。呼び忘れるとメモリが漏れるので、必ず呼びます。

ドロップされた位置から地面（`y = 0`）との交点を求めて、そこに物を作ります。レイの計算は、第 37 章のものと同じです。第 37 章では `GizmoController` の中に書いたので、`CameraMath` という共有のクラスに取り出して、どちらからも使うようにします（第 37 章の `MakeRay` を、そのまま `static` クラスへ移すだけです）。

```csharp
// ViewportViewModel
public void OnFilesDropped(IReadOnlyList<string> paths, float x, float y)
{
    var camera = _loop.Invoke(e => e.GetCameraInfo());
    Ray ray = CameraMath.MakeRay(camera, x, y);

    // 地面 (y = 0) との交点。平行、またはカメラの後ろなら、カメラ前方 5 m
    Vector3 position;
    if (MathF.Abs(ray.Direction.Y) > 1e-5f && -ray.Origin.Y / ray.Direction.Y is var t && t > 0)
        position = ray.Origin + ray.Direction * t;
    else
        position = ray.Origin + ray.Direction * 5f;
    position.Y = 0.5f;

    foreach (var path in paths)
    {
        var name = Path.GetFileNameWithoutExtension(path);
        _editor.CreateObject(name, null, position);
        position.X += 1.5f;                                   // 複数なら、少しずつ離して並べる
    }
}
```

レイ `O + tD` が `y = 0` になるのは `t = -O.y / D.y` のときです。`D.y` がほぼ 0 なら地面と平行、`t` が負なら地面はカメラの後ろなので、その場合はカメラの前方 5 m に置きます。`... is var t && t > 0` は、計算結果を `t` に取って、そのまま条件に使うパターンです。物は `ISceneEditor` 経由で作るので、Undo で戻せます。

なお、ここで置くのは、ファイル名を持った箱です。ファイルの中身（メッシュやテクスチャ）をエンジンが読み込み、物に割り当てるのは、アセット システムというエンジン側の機能で、この教材の範囲を超えます。物に `AssetPath` を持たせ、エンジンに `me_asset_load` を足す形が、自然な拡張です。

## 動かして確かめる

| 操作 | 期待する結果 |
| --- | --- |
| 「フォルダーを開く…」で選ぶ | 左にフォルダーの木、右にファイルの一覧が出る |
| 左の木でフォルダーを選ぶ | 右の一覧が切り替わる。`↑` で親へ |
| 検索ボックスに入力 | 名前に一致するものだけが残る |
| 画像ファイル | 絵文字の代わりに、サムネイルが少し遅れて出る |
| エクスプローラーでファイルを追加／削除 | 約 0.3 秒後に、一覧が更新される |
| `.scene` をダブルクリック | シーンが開く（未保存なら確認が出る） |
| ファイルをビューポートへドラッグ | 地面の落とした位置に、ファイル名の物が置かれる。Undo で戻せる |
| エクスプローラーから直接ドロップ | 同様に動く |

??? failure "ビューポートにドロップできない（禁止マークが出る）"
    `HwndHost` には WPF の `AllowDrop` が効きません。子ウィンドウに `DragAcceptFiles(hwnd, true)` を設定したかを確認します。エディタが管理者権限で動いていると、一般権限のエクスプローラーからのドロップはブロックされます（UIPI）。

??? failure "一覧に画像が出ず、ずっと記号のまま"
    サムネイルの読み込みで例外が出て `null` になっています。`catch` の中でログを出して、原因を見ます。

??? failure "画像ファイルが削除できない／上書きできない"
    `BitmapCacheOption.OnLoad` を指定していません。画像を掴みっぱなしになります。

??? failure "メモリが増え続ける"
    `DecodePixelWidth` を指定していません。元のサイズでデコードされています。

??? failure "`FileSystemWatcher` のイベントで `InvalidOperationException`（別のスレッド）"
    ハンドラーの中で、直接 UI（`ObservableCollection` など）を触っています。`Dispatcher.BeginInvoke` で UI スレッドに回します。

??? failure "更新が何度も走って、一覧がちらつく"
    デバウンスをしていません。1 つのファイルの保存でも、複数のイベントが来ます。

## 第 5 部のまとめ

| 章 | 作ったもの |
| --- | --- |
| 第 34 章 | シーンのデータ（エディタが正）と、エンジンへの同期 |
| 第 35 章 | シーン ツリー（選択、追加、削除、名前変更、ドラッグで親子づけ） |
| 第 36 章 | プロパティ パネル（型ごとの DataTemplate、入力の検証） |
| 第 37 章 | ピッキングとギズモ（レイ、スラブ法、最近点） |
| 第 38 章 | Undo/Redo（コマンド パターン、トランザクション、スナップショット） |
| 第 39 章 | 保存と読み込み（DTO、検証、一時ファイル、非同期） |
| 第 40 章 | アセット ブラウザ（`FileSystemWatcher`、サムネイル、ドラッグ アンド ドロップ） |

これで、ふつうのエディタができました。残るのは、このエディタを、ゲームの開発に使うための機能です。

次の章から第 6 部です。ゲームのコードを `Game.dll` として分けて、エンジンが読み込んで動かす仕組みを作ります。

[第 41 章 Game DLL のインターフェース](41-game-interface.md) へ進みます。
