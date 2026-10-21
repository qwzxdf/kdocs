---
title: 第 26 章 アセット ブラウザ
tags:
  - C#連携
---

# 第 26 章 アセット ブラウザ

この章では、プロジェクトのフォルダーの中身（シーン、テクスチャ、モデル…）を一覧する<strong>アセット ブラウザ</strong>を作ります。フォルダーの木、ファイルの一覧、検索、画像のサムネイル、フォルダーの変更の自動検出、そして<strong>ファイルをビューポートへドラッグ アンド ドロップ</strong>して物を置く操作までを扱います。第 5 部（エディタの機能）の最後の章です。

## この章の考え方

アセット ブラウザは、ファイル システムの<strong>見た目</strong>です。作るときに、次の 4 つの問題が出てきます。

| 問題 | 内容 | 対処 |
| --- | --- | --- |
| ファイルが多い | 数千のファイルを、一度に UI に載せると遅い | <strong>仮想化</strong>（見える分だけ作る）、サムネイルは<strong>非同期</strong> |
| 画像の読み込みが重い | 4096×4096 の画像を、そのまま読むと、メモリと時間がかかる | <strong>小さく読む</strong>（`DecodePixelWidth`）、<strong>UI スレッド以外</strong>で |
| 外部の変更 | エクスプローラーでファイルを追加／削除しても、画面を更新したい | <strong>`FileSystemWatcher`</strong> で監視 |
| スレッド | 監視のイベントは別のスレッドから来る。UI は触れない | <strong>UI スレッドに戻して</strong>から更新 |

## この章のゴール

- プロジェクト フォルダーを選ぶと、左にフォルダーの木、右にファイルの一覧が出る。
- 検索ボックスで、ファイル名を絞り込める。
- 画像ファイルは、サムネイルが出る。
- エクスプローラーでファイルを追加／削除すると、自動で更新される。
- `.scene` をダブルクリックで開く。
- ファイルをビューポートへドロップすると、その位置に物が置かれる。

## 手順 1：モデルとサービス

### 項目（AssetEntry）

`Models\AssetEntry.cs`:

```csharp
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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Path.GetFileName` / `Path.GetExtension` | パスからファイル名／拡張子（`.png`）を取り出す |
| `ToLowerInvariant()` | カルチャーに依存しない小文字化。拡張子の比較は、大文字小文字を区別しない |
| `".png" or ".jpg" or …` | switch 式のパターン。<strong>複数の値のどれか</strong> |
| `ImageSource` | WPF の画像の基底クラス。`BitmapImage` などがこれ |
| 絵文字を記号に使う | 画像ファイルを用意せず、文字で済ます簡易な方法。フォントによって見え方が変わる。本格的には画像リソース |

### サービス

`Services\IAssetService.cs`:

```csharp
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

`Services\AssetService.cs`:

```csharp
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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `FileSystemWatcher` | フォルダーを監視して、`Created`/`Deleted`/`Renamed`/`Changed` を通知する標準クラス。<strong>イベントは別のスレッドで呼ばれる</strong> |
| `IncludeSubdirectories` | サブフォルダーも監視する |
| `NotifyFilter` | 何の変化を通知するか |
| `EnableRaisingEvents = true` | 監視を開始する |
| `Dispatcher.BeginInvoke(…)` | UI スレッドに処理を回す（第 10 章）。UI のタイマーや `HashSet` を、UI スレッドだけで触るようにする |
| デバウンス | 短時間に何度も来る通知を、<strong>最後の 1 回にまとめる</strong>。ファイル 1 つのコピーでも、複数のイベントが来るため、毎回更新すると重い |
| `Directory.EnumerateFiles` | 遅延評価の列挙。1 つずつ取り出す（`GetFiles` は全部を配列にする） |
| `OrderBy(…, StringComparer.OrdinalIgnoreCase)` | 大文字小文字を区別せずに並べる |
| `StartsWith('.')` | `char` を取る版。先頭が `.` か |
| `Array.Empty<T>()` | 空の配列（毎回新しく作らない共有のもの） |

`FileSystemWatcher` は、バッファーがあふれると `Error` を起こし、変更の一部を取りこぼします。その場合は、全体を読み直すのが安全です。

## 手順 2：ビューモデル

`Modules\Asset\ViewModels\AssetViewModel.cs`:

```csharp
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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `CollectionViewSource.GetDefaultView(コレクション)` | コレクションを<strong>加工して見せる</strong>ビュー（`ICollectionView`）。元のコレクションを変えずに、<strong>絞り込み、並べ替え、グループ化</strong>ができる |
| `EntriesView.Filter` | 絞り込みの条件。`true` を返した要素だけが表示される |
| `EntriesView.Refresh()` | 条件を変えたとき、かけ直す |
| `Contains(text, StringComparison.OrdinalIgnoreCase)` | 大文字小文字を区別しない部分一致 |
| `OpenFolderDialog` | .NET 8 で WPF に追加された、<strong>フォルダーを選ぶ</strong>標準ダイアログ |
| `_ = LoadThumbnailAsync(entry)` | 非同期の処理を<strong>待たずに</strong>開始する。`_ =` は、「戻り値（`Task`）を意図して無視する」書き方 |
| `async void OpenEntry` | コマンドのハンドラー。例外が漏れると落ちるので、中で `try/catch` を使うのが安全（ここでは `OpenPathAsync` が内部で処理する） |

`ISceneFileService` に、パスを指定して開く `OpenPathAsync(string path)` を足します（第 25 章の `OpenAsync` から、ダイアログの部分を取り出す）。

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

大きなプロジェクトでは、すべてのサブフォルダーを一度に読むと遅くなります。展開されたときに読む（<strong>遅延読み込み</strong>）のが、本来の形ですが、この教材では簡単さを優先しています。

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `BitmapImage` | WPF の画像。`BeginInit()` … `EndInit()` の間で設定する |
| `DecodePixelWidth` | <strong>デコード時に縮小</strong>する。4096 ピクセルの画像でも、96 ピクセルだけのメモリで済む。<strong>必ず指定する</strong>（後から縮小表示するだけだと、元のサイズでメモリを使う） |
| `BitmapCacheOption.OnLoad` | 読み込み完了時にファイルを閉じる。指定しないと、ファイルを掴んだままで、削除や上書きができなくなる |
| `Freeze()` | 変更不可にして、<strong>別のスレッドから渡せる</strong>ようにする。凍結していない WPF のオブジェクトは、作ったスレッドでしか触れない |
| `SemaphoreSlim(4)` | 同時に入れる数を制限する。サムネイルを 1000 枚、一斉に読み始めると、メモリと CPU が尽きる |
| `WaitAsync` / `Release` | 枠を待つ／返す。`try/finally` で、必ず返す |
| 戻り値を `null` に | 壊れた画像のとき、サムネイルなしにする |

## 手順 3：ビュー

`Views\AssetView.xaml`:

```xml
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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `ItemsSource="{Binding EntriesView}"` | 絞り込み済みの<strong>ビュー</strong>を渡す。元の `Entries` ではなく |
| `ItemsPanelTemplate` + `WrapPanel` | リストの項目の<strong>並べ方</strong>を変える。縦並びの既定を、折り返しの横並びにして、タイル表示にする |
| `SelectionMode="Extended"` | `Ctrl`/`Shift` で複数選択 |
| `TextTrimming="CharacterEllipsis"` | はみ出た文字を `…` にする |
| `ToolTip` | マウスを載せたときに出る説明 |
| `EventSetter` | スタイルの中で、イベント ハンドラーを結びつける。ここでは、各項目のダブルクリック |
| `StaticResource NotNullToCollapsed` | `null` でなければ `True` を返すコンバーター（`value != null`）。第 7 章の要領で作る |
| 仮想化 | `ListBox` の既定（`VirtualizingStackPanel`）は仮想化するが、<strong>`WrapPanel` に変えると仮想化されない</strong>。数千項目のときは、別のライブラリや、行ごとの表示に切り替える |

### コードビハインド（ビューの橋渡し）

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `DataFormats.FileDrop` | 「ファイルのパスの配列」を表す、標準のドラッグ形式（`string[]`）。エクスプローラーからのドロップと<strong>同じ形式</strong>なので、受ける側は、1 つの処理で両方を扱える |
| `OfType<AssetEntry>()` | 型が合う要素だけを取り出す LINQ |
| `SelectedItems` | 複数選択された項目（`IList`） |

## 手順 4：ビューポートへドロップ

ビューポートは `HwndHost`（子ウィンドウ）なので、WPF のドロップ（`AllowDrop`、`Drop` イベント）が<strong>効きません</strong>。子ウィンドウは、WPF の外の Win32 のウィンドウだからです。Win32 の仕組み、<strong>`WM_DROPFILES`</strong> を使います。

### Win32 の宣言

`Win32.cs` に追加します。

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

### 受け取る

`BuildWindowCore` で、`DragAcceptFiles(_hwnd, true)` を呼びます。`WndProc` に追加します。

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `WM_DROPFILES` | ファイルがドロップされたときのメッセージ。`wParam` が `HDROP`（ドロップ情報のハンドル） |
| `DragAcceptFiles` | このウィンドウが、ファイルのドロップを受け付けると宣言する |
| `DragQueryFile(drop, 0xFFFFFFFF, null, 0)` | インデックスに `0xFFFFFFFF` を渡すと、<strong>ファイルの個数</strong>を返す |
| 2 回呼ぶ | 1 回目で文字数を聞き、バッファーを用意して、2 回目で受け取る。（C のよくある 2 段階の取得） |
| `DragFinish` | ドロップ情報を解放する。<strong>必ず呼ぶ</strong> |
| `[Out] char[]?` | 呼ばれた側が書き込む配列。`[Out]` で、書き込み結果を C# に戻す指定 |

### ドロップ位置に物を置く

ドロップされた位置から<strong>地面（y = 0）との交点</strong>を求め、そこに物を作ります。第 23 章の `MakeRay` を共有のクラスに取り出して使います。

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| 地面との交点 | レイ `O + tD` が `y = 0` になる `t = -O.y / D.y`。`D.y ≈ 0` は地面と平行 |
| `... is var t && t > 0` | 計算結果を `t` に取って、そのまま条件に使うパターン |
| `Path.GetFileNameWithoutExtension` | 拡張子を除いたファイル名 |
| 実際のアセットの扱い | この教材の物は、名前つきの箱です。ファイルの中身（メッシュ、テクスチャ）をエンジンが読み込み、物に割り当てるのは、エンジンの機能の追加（アセット システム）で、この教材の範囲を超えます。物に `AssetPath` を持たせ、エンジンに `me_asset_load` を足す形が自然な拡張です |

## 動作確認

| 操作 | 期待する結果 |
| --- | --- |
| 「フォルダーを開く…」で選ぶ | 左にフォルダーの木、右にファイルの一覧が出る |
| 左の木でフォルダーを選ぶ | 右の一覧が切り替わる。`↑` で親へ |
| 検索ボックスに入力 | 名前に一致するものだけが残る |
| 画像ファイル | 絵文字の代わりに、サムネイルが出る（少し遅れて） |
| エクスプローラーでファイルを追加／削除 | 約 0.3 秒後に、一覧が更新される |
| `.scene` をダブルクリック | シーンが開く（未保存なら確認が出る） |
| ファイルをビューポートへドラッグ | 地面の落とした位置に、そのファイル名の物が置かれる。Undo で戻せる |
| エクスプローラーから直接ドロップ | 同様に動く |

## よくあるミス

??? failure "ビューポートにドロップできない（禁止マークが出る）"
    `HwndHost` には WPF の `AllowDrop` が効かない。子ウィンドウに `DragAcceptFiles(hwnd, true)` を設定したか、`WS_EX_ACCEPTFILES` を付けたかを確認する。管理者権限で動いている場合、一般権限のエクスプローラーからのドロップはブロックされる（UIPI）。

??? failure "一覧に画像が出ず、ずっと記号のまま"
    サムネイルの読み込みで例外が出て `null` になっている。パスに日本語や空白があっても `Uri` は通るが、特殊な文字では失敗することがある。`catch` の中でログを出して原因を見る。

??? failure "画像ファイルが削除できない／上書きできない"
    `BitmapCacheOption.OnLoad` を指定していない。画像を掴みっぱなしになる。

??? failure "メモリが増え続ける"
    `DecodePixelWidth` を指定していない。元のサイズでデコードされている。

??? failure "`FileSystemWatcher` のイベントで、`InvalidOperationException`（別のスレッド）"
    ハンドラーの中で、直接 UI（`ObservableCollection` など）を触っている。`Dispatcher.BeginInvoke` で UI スレッドに回す。

??? failure "更新が何度も走って、一覧がちらつく"
    デバウンスをしていない。1 つのファイルの保存でも、複数のイベントが来る。

## 第 5 部のまとめ

| 章 | 作ったもの |
| --- | --- |
| 第 20 章 | シーンのデータ（エディタが正）と、エンジンへの同期 |
| 第 21 章 | シーン ツリー（選択、追加、削除、名前変更、ドラッグで親子づけ） |
| 第 22 章 | プロパティ パネル（型ごとの DataTemplate、入力の検証） |
| 第 23 章 | ピッキングとギズモ（レイ、スラブ法、最近点） |
| 第 24 章 | Undo/Redo（コマンド パターン、トランザクション、スナップショット） |
| 第 25 章 | 保存と読み込み（DTO、検証、一時ファイル、非同期） |
| 第 26 章 | アセット ブラウザ（`FileSystemWatcher`、サムネイル、ドラッグ アンド ドロップ） |

これで、<strong>ふつうのエディタ</strong>ができました。残るのは、このエディタを<strong>ゲームの開発に使う</strong>ための機能です。

## 次の章へ

次の章（[第 27 章 Game DLL のインターフェース](27-game-interface.md)）から第 6 部です。ゲームのコードを `Game.dll` として分離し、エンジンが読み込んで動かす仕組みを作ります。
