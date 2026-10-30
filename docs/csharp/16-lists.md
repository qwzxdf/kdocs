---
title: 第 16 章 リストとデータ表示
tags:
  - C#連携
---

# 第 16 章 リストとデータ表示

エディタの画面は、リストだらけです。シーンの物、アセット、ログ、プロパティ。WPF にはリストを表示する部品が何種類かあって、「どれを使えばいいの？」と迷います。この章では、Editor の下のパネルに、アセットの一覧とログの一覧を作りながら、部品の違い、選択の扱い、大量のデータを速く出す方法を見ていきます。

!!! info "このページを読む前に"
    - [第 15 章 バインディングを掘り下げる](15-binding.md)（前の章。この章は、そこで作った Editor に足していく）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）

!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Asset/AssetEntry.cs`（新規） | アセット 1 件（フォルダーとファイル） |
    | `Log/LogEntry.cs`（新規） | ログ 1 行 |
    | `Asset/AssetViewModel.cs`（新規） | アセットの一覧、選択、種類での絞り込み |
    | `Log/LogViewModel.cs`（新規） | ログの一覧 |
    | `MainWindowViewModel.cs`（変更） | 上の 2 つを持たせる |
    | `MainWindow.xaml`（変更） | 下のパネルの「アセット」と「ログ」のタブ |

## リスト系の部品の使い分け

第 6 章で、下のパネルには `TabControl` を置いて、中身は文字だけにしていました。ここに一覧を置く前に、リスト系の部品を整理しておきます。

| 部品 | どんなときに |
| --- | --- |
| `ItemsControl` | 選択が要らない一覧。ただ並べるだけ（ツール バーのボタンの並び、タグの一覧） |
| `ListBox` | 縦（や横）に並べて、選択できる。一番基本のリスト |
| `ListView` | 列を持つ表のようなリスト（`GridView` を付ける）や、タイル表示 |
| `ComboBox` | ドロップダウンで 1 つ選ぶ |
| `DataGrid` | 編集もできる表。列ごとに型や編集方法を決められる |
| `TreeView` | 階層構造（第 41 章） |
| `TabControl` | タブ |

これらは全部 `ItemsControl` を元にしていて、使い方はほとんど共通です。`ItemsSource` に集まりを渡し、`ItemTemplate` で 1 件の見た目を決めます。部品を変えても、書き方はほとんど変わりません。アセットは `ListBox`、ログは `DataGrid` で作ります。

## アセットの一覧を作る

アセット ブラウザは、あとの章で、本物のフォルダーを読むようにします。今はつなぐ先がないので、ダミーのデータを並べます。まず、アセット 1 件を表すクラスを作ります。フォルダーとファイルは、見た目も持つ情報も違うので、別の型にします。

```csharp title="Asset/AssetEntry.cs（新規）"
namespace Editor.Asset;

public abstract class AssetEntry
{
    protected AssetEntry(string name) => Name = name;

    public string Name { get; }
}

public class FolderEntry : AssetEntry
{
    public FolderEntry(string name) : base(name) { }
}

public class FileEntry : AssetEntry
{
    public FileEntry(string name, string kind, long sizeBytes) : base(name)
    {
        Kind = kind;
        SizeBytes = sizeBytes;
    }

    public string Kind { get; }          // "scene"、"texture"、"mesh"
    public long SizeBytes { get; }
}
```

`abstract class` は、それ自体は作れず、継承して使う前提のクラスです。C++ の純粋仮想関数を持つ基底クラスに近いものです。

これを持つビューモデルです。

```csharp title="Asset/AssetViewModel.cs（新規）"
using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;

namespace Editor.Asset;

public record KindOption(string Id, string Name);

public partial class AssetViewModel : ObservableObject
{
    public AssetViewModel()
    {
        Entries = new ObservableCollection<AssetEntry>
        {
            new FolderEntry("Scenes"),
            new FolderEntry("Textures"),
            new FileEntry("main.scene", "scene", 4_096),
            new FileEntry("brick.png", "texture", 262_144),
            new FileEntry("cube.mesh", "mesh", 8_192),
        };
    }

    public ObservableCollection<AssetEntry> Entries { get; }

    // 選ばれているアセット。選ばれていないときは null
    [ObservableProperty]
    private AssetEntry? _selectedAsset;
}
```

`record` は、値を持つだけの小さなクラスを 1 行で書く C# の書き方です。ここでは、あとで使う ComboBox の選択肢の入れ物にしています。

ファイルは `Asset/` と `Log/` に置きます。アセットのデータの型 `AssetEntry` も、アセットだけが使うので、ビューモデルと同じ `Asset/` に置きます。いまは画面がまだ `MainWindow.xaml` の中にありますが、第 23 章でそれぞれを `AssetView` と `LogView` に切り出すとき、同じフォルダーに並べるだけで済むように、先にここへ置いておきます。

`MainWindowViewModel` に、このビューモデルを持たせます。

```csharp title="MainWindowViewModel.cs（変更）"
using Editor.Asset;
using Editor.Log;

public AssetViewModel AssetBrowser { get; } = new();
public LogViewModel Log { get; } = new();
```

画面は、第 6 章で文字だけを置いた「アセット」のタブを差し替えます。

```xml title="MainWindow.xaml（変更：下のパネル）"
<TabControl Grid.Row="2">
    <TabItem Header="アセット">
        <DockPanel DataContext="{Binding AssetBrowser}">
            <ListBox ItemsSource="{Binding Entries}"
                     SelectedItem="{Binding SelectedAsset}"
                     Background="Transparent" BorderThickness="0" Foreground="White" />
        </DockPanel>
    </TabItem>
    <!-- ログのタブは、あとで -->
</TabControl>
```

`DockPanel` に `DataContext="{Binding AssetBrowser}"` を付けているのが、ポイントです。ウィンドウの `DataContext` は `MainWindowViewModel` ですが、このパネルの中では `AssetBrowser` に切り替わります。中の `{Binding Entries}` は、`AssetViewModel.Entries` を見に行きます。

実行すると、一覧に `Editor.Asset.FolderEntry` と `Editor.Asset.FileEntry` という文字が並びます。`ListBox` に自作クラスを渡すと、見た目の指定がないため、クラス名がそのまま出ます。次の節で直します。

### 要素の種類で見た目を切り替える

リストの要素が種類の違うオブジェクトを含んでいるときは、型ごとに別のテンプレートを用意できます。

```xml title="MainWindow.xaml（変更：ListBox に足す）"
<ListBox.Resources>
    <DataTemplate DataType="{x:Type models:FolderEntry}">
        <TextBlock Text="{Binding Name, StringFormat=📁 {0}}" FontWeight="Bold" />
    </DataTemplate>
    <DataTemplate DataType="{x:Type models:FileEntry}">
        <StackPanel Orientation="Horizontal">
            <TextBlock Text="{Binding Name}" />
            <TextBlock Text="{Binding SizeBytes, StringFormat=({0:N0} B)}"
                       Foreground="Gray" Margin="8,0,0,0" />
        </StackPanel>
    </DataTemplate>
</ListBox.Resources>
```

`models:` は、`Window` タグに `xmlns:models="clr-namespace:Editor.Asset"` を足して使えるようにします。`DataType` を指定した `DataTemplate` は、その型の要素に自動で使われます。フォルダーは太字に 📁 付き、ファイルは名前とサイズ、という見た目になります。

型以外の条件（値によって切り替えたい）なら、`DataTemplateSelector` を実装します。今回は型で足りるので、Editor には入れません。

```csharp title="実験：DataTemplateSelector（Editor には入れない）"
public class EntryTemplateSelector : DataTemplateSelector
{
    public DataTemplate? FolderTemplate { get; set; }
    public DataTemplate? FileTemplate { get; set; }

    public override DataTemplate? SelectTemplate(object item, DependencyObject container)
        => item is FolderEntry ? FolderTemplate : FileTemplate;
}
```

### 項目の入れ物（ItemContainerStyle）

リストの要素 1 つ 1 つは、`ListBoxItem` や `TreeViewItem` といった入れ物に包まれて表示されます。その入れ物のスタイルを決めるのが `ItemContainerStyle` です。選択された行の色、行の高さ、ダブルクリックのイベント、`IsSelected` や `IsExpanded` のバインディングは、ここに書きます。行の間が詰まっていて見づらいので、余白を足します。

```xml title="MainWindow.xaml（変更：ListBox に足す）"
<ListBox.ItemContainerStyle>
    <Style TargetType="ListBoxItem">
        <Setter Property="Padding" Value="4" />
    </Style>
</ListBox.ItemContainerStyle>
```

`DataTemplate`（中身の見た目）と `ItemContainerStyle`（入れ物の見た目と状態）の違いを意識しておくと、どちらに書くべきか迷いません。第 41 章のシーン ツリーでは、ここに `IsSelected` と `IsExpanded` のバインディングを書きます。

## 選択を使う

一覧で選んだアセットの名前を、パネルの下に出します。

```xml title="MainWindow.xaml（変更：DockPanel の ListBox の前に足す）"
<TextBlock DockPanel.Dock="Bottom" Margin="4" Foreground="Gray"
           Text="{Binding SelectedAsset.Name, TargetNullValue=(未選択), FallbackValue=(未選択)}" />
```

`SelectedItem` に結び付けた `SelectedAsset` が変わるたびに、この文字が変わります。逆に、ビューモデルが `SelectedAsset = Entries[2]` と書けば、画面の選択も動きます。

### 深掘り：選択まわりのプロパティ

選択できるリストは、「何が選ばれているか」をプロパティで持っています。

| プロパティ | 意味 |
| --- | --- |
| `SelectedItem` | 選ばれた要素そのもの（`object`） |
| `SelectedIndex` | 選ばれた要素の番号（なければ `-1`） |
| `SelectedValue` / `SelectedValuePath` | 要素の中の特定のプロパティの値で選ぶ |
| `SelectedItems` | 複数選択のときの、選ばれた要素の集まり（`SelectionMode="Extended"` など） |

`SelectedItem` は依存関係プロパティなので、バインディングできます。既定で双方向なので、`Mode=TwoWay` は書かなくても動きます。

`SelectedValue` は、「表示は名前、保存するのは ID」にしたいときに使います。次の節の `ComboBox` で、実際に使います。

`SelectedItems` は、依存関係プロパティではありません。そのため `{Binding SelectedItems}` と書けません。回避策はいくつかあります。

- コードビハインドの `SelectionChanged` で受け取って、ビューモデルに橋渡しする。
- 各要素に `IsSelected` のプロパティを持たせて、`ItemContainerStyle` で `IsSelected` を結び付ける（第 41 章のシーン ツリーがこの方法）。
- Behavior（第 28 章）で `SelectedItems` を扱う添付ビヘイビアを使う。

## 種類で絞り込む

アセットが増えたときのために、上に「すべて、シーン、テクスチャ、メッシュ」を選ぶ `ComboBox` を置いて、選んだ種類だけを見せます。絞り込みは、第 15 章の `CollectionView` を使います。

```csharp title="Asset/AssetViewModel.cs（変更）"
using System.ComponentModel;
using System.Windows.Data;

private readonly ICollectionView _entriesView;

public IReadOnlyList<KindOption> Kinds { get; } = new[]
{
    new KindOption("all", "すべて"),
    new KindOption("scene", "シーン"),
    new KindOption("texture", "テクスチャ"),
    new KindOption("mesh", "メッシュ"),
};

[ObservableProperty]
private string _kindId = "all";

// KindId が変わったら、絞り込みをかけ直す
partial void OnKindIdChanged(string value) => _entriesView.Refresh();

// コンストラクターの最後
_entriesView = CollectionViewSource.GetDefaultView(Entries);
_entriesView.Filter = o => o is FolderEntry
    || _kindId == "all"
    || (o is FileEntry f && f.Kind == _kindId);
```

```xml title="MainWindow.xaml（変更：DockPanel の先頭に足す）"
<ComboBox DockPanel.Dock="Top" Margin="4"
          ItemsSource="{Binding Kinds}"
          DisplayMemberPath="Name"
          SelectedValuePath="Id"
          SelectedValue="{Binding KindId}" />
```

`DisplayMemberPath` は、要素のどのプロパティを表示に使うかの指定で、簡単な表示なら `ItemTemplate` の代わりになります。`SelectedValuePath` は、選ばれたときに、どのプロパティを `SelectedValue` として取り出すかの指定です。ここでは、画面には「テクスチャ」と出て、ビューモデルの `KindId` には `"texture"` が入ります。

## ログの一覧を作る

もう 1 つのタブには、ログを出します。時刻、重大度、メッセージの 3 列の表なので、`DataGrid` が向いています。

```csharp title="Log/LogEntry.cs（新規）"
namespace Editor.Log;

public enum LogLevel { Info, Warning, Error }

public record LogEntry(DateTime Time, LogLevel Level, string Message);
```

```csharp title="Log/LogViewModel.cs（新規）"
using System.Collections.ObjectModel;

namespace Editor.Log;

public class LogViewModel
{
    public ObservableCollection<LogEntry> Entries { get; } = new()
    {
        new(DateTime.Now, LogLevel.Info, "Editor を起動しました"),
        new(DateTime.Now, LogLevel.Warning, "エンジンにはまだつながっていません"),
    };
}
```

```xml title="MainWindow.xaml（変更：TabControl の中。アセットの TabItem のあとに足す）"
<TabItem Header="ログ">
    <DataGrid DataContext="{Binding Log}" ItemsSource="{Binding Entries}"
              AutoGenerateColumns="False" CanUserAddRows="False" IsReadOnly="True">
        <DataGrid.Columns>
            <DataGridTextColumn Header="時刻" Binding="{Binding Time, StringFormat=HH:mm:ss}" />
            <DataGridTextColumn Header="重大度" Binding="{Binding Level}" />
            <DataGridTextColumn Header="メッセージ" Binding="{Binding Message}" Width="*" />
        </DataGrid.Columns>
    </DataGrid>
</TabItem>
```

`AutoGenerateColumns="True"` にすると、型のプロパティから列を自動で作りますが、どの列を出すか、列の名前、書式を細かく指定したいので、普通は `False` にして自分で列を並べます。`IsReadOnly="True"` は、ログは書き換えない表なので、編集できないようにする指定です。

| 列の種類 | 用途 |
| --- | --- |
| `DataGridTextColumn` | 文字・数値 |
| `DataGridCheckBoxColumn` | `bool` |
| `DataGridComboBoxColumn` | 選択肢から選ぶ |
| `DataGridTemplateColumn` | 好きな見た目（ボタン、画像など）を入れる |

列の見出しをクリックすると並べ替えができ、これは `CollectionView` の機能です。

## 大量のデータを速く出す（仮想化）

ログは、エンジンが動き始めると、あっという間に何万行にもなります。1 万件のリストを `ListBox` や `DataGrid` に渡しても、普通は問題なく動きます。WPF は UI 仮想化といって、画面に見えている分だけ入れ物（`ListBoxItem` や `DataGridRow`）を作り、スクロールすると使い回すからです。

確かめてみましょう。次のコードは、1 万件を足す実験用のものです。

```csharp title="実験：ログを 1 万件足す（Editor には入れない）"
for (int i = 0; i < 10_000; i++)
    Entries.Add(new(DateTime.Now, LogLevel.Info, $"テスト {i}"));
```

`LogViewModel` のコンストラクターに一時的に置いて実行しても、スクロールは軽いままです。確かめたら、消してください。

ところが、仮想化が効かなくなる条件があって、それに気づかないと急に重くなります。

| 仮想化が切れる条件 | 対処 |
| --- | --- |
| 縦の `StackPanel` や `ScrollViewer` の中に置いている（高さが無制限になる） | `Grid` の `*` の行に置く。外側の `ScrollViewer` を外す |
| `ItemsPanel` を `WrapPanel` などに変えている（第 46 章のタイル表示） | `VirtualizingStackPanel` 以外のパネルは、標準では仮想化しない。数が少ないときだけ使う |
| `ScrollViewer.CanContentScroll="False"` | 既定の `True` に戻す |
| `TreeView` | 既定では仮想化されない。`VirtualizingStackPanel.IsVirtualizing="True"` を付ける |
| 要素を `ListBoxItem` として直接並べている（バインディングを使わない） | `ItemsSource` で渡す |

Editor のログは、`Grid` の `*` の行にある `TabControl` の中なので、条件に当てはまりません。仮想化を強めたいときは、次の指定が使えます。

```xml
<ListBox VirtualizingStackPanel.IsVirtualizing="True"
         VirtualizingStackPanel.VirtualizationMode="Recycling"
         ScrollViewer.IsDeferredScrollingEnabled="True" />
```

`Recycling` は、使い終わった入れ物を作り直さず再利用する指定です。`IsDeferredScrollingEnabled` は、スクロール バーのつまみを動かしている間は、中身の更新を後回しにします。

UI 仮想化は、入れ物の数を減らす工夫です。データそのもの（1 万件のオブジェクト）はメモリ上にあります。数十万件を超えるようなデータは、必要な分だけ読み込む「データ仮想化」を自分で組む必要があります。

### 項目の追加・削除と画面

`ObservableCollection` は、追加・削除をすると、画面が自動で更新されます。ただし、複数の要素を一度に追加すると、要素ごとに通知が飛んで重くなります。まとめて入れたいときは、次のような手があります。

- 新しいコレクションを作って、プロパティごと差し替える（プロパティの通知が必要）。
- 追加の間だけ、画面との接続を外す（`ItemsSource = null` にしておいて、追加後に戻す）。

100 件程度なら気にしなくて構いません。数千件を一度に入れるときに、重さを感じたら思い出してください。

## 動かして確かめる

`F5` で実行して、次を確かめてください。

- 下のパネルの「アセット」に、フォルダー 2 つ（太字、📁 付き）とファイル 3 つ（名前とサイズ）が並ぶ。
- 行を選ぶと、パネルの下に名前が出る。何も選んでいないときは `(未選択)` と出る。
- 上の ComboBox で「テクスチャ」を選ぶと、`brick.png` とフォルダーだけが残る。
- 「ログ」のタブに、時刻、重大度、メッセージの 3 列の表が出る。列の見出しをクリックすると並べ替わる。

??? failure "一覧に `Editor.Asset.FileEntry` と出る"
    `DataTemplate` の `DataType` が、実際の型と合っていません。`xmlns:models` の名前空間と、クラスのつづりを確かめます。`ListBox.Resources` の中に書いたかも見てください。

??? failure "ComboBox を変えても、一覧が変わらない"
    `partial void OnKindIdChanged` で `_entriesView.Refresh()` を呼んでいるか、`SelectedValuePath="Id"` を書いたかを確かめます。`SelectedValuePath` がないと、`KindOption` オブジェクトそのものが `SelectedValue` に入ろうとして、`string` の `KindId` に入りません。

??? failure "DataGrid の列が出ない"
    `AutoGenerateColumns="False"` にしたときは、`DataGrid.Columns` を自分で書く必要があります。`Binding` の名前が `LogEntry` のプロパティと合っているかも見てください。

## ここまでの Editor

```text
Editor/
├─ Asset/
│   ├─ AssetEntry.cs                 FolderEntry、FileEntry
│   └─ AssetViewModel.cs             一覧、選択、種類での絞り込み
├─ Log/
│   ├─ LogEntry.cs
│   └─ LogViewModel.cs
├─ Scene/
│   └─ SceneObjectViewModel.cs
├─ MainWindowViewModel.cs            AssetBrowser、Log を持つ
└─ MainWindow.xaml                   下のパネルが、アセットとログの一覧になった
```

## この章のまとめ

- リスト系の部品は全部 `ItemsControl` の仲間。使い方は共通で、`ItemsSource` と `ItemTemplate`。
- 選択は `SelectedItem`（双方向でバインド）。複数選択は直接バインドできないので、`IsSelected` を要素に持たせるなどの工夫をする。
- 要素の見た目は `DataTemplate`（型ごとに自動で選ばれる）、入れ物の状態は `ItemContainerStyle`。
- 絞り込みや並べ替えは `CollectionView`。表は `DataGrid`。
- 大量に出すときは、仮想化が切れていないかを確かめる。縦の `StackPanel` の中は、まず疑う。

次の章では、画面を固まらせないための非同期処理と、UI スレッドの決まりごとを説明します。アセット一覧をフォルダーから読み込むときに、さっそく必要になります。

[第 17 章 非同期処理と UI スレッド](17-async-ui.md) へ進みます。
