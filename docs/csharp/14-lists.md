---
title: 第 14 章 リストとデータ表示
tags:
  - C#連携
---

# 第 14 章 リストとデータ表示

エディタの画面は、リストだらけです。シーンの物、アセット、ログ、プロパティ。WPF にはリストを表示する部品が何種類かあって、「どれを使えばいいの？」と迷います。この章では、それぞれの違いと、選択の扱い、大量のデータを速く出す方法を説明します。

!!! info "このページを読む前に"
    - [第 13 章 バインディングを掘り下げる](13-binding.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## リスト系の部品の使い分け

| 部品 | どんなときに |
| --- | --- |
| `ItemsControl` | 選択が要らない一覧。ただ並べるだけ（ツール バーのボタンの並び、タグの一覧） |
| `ListBox` | 縦（や横）に並べて、選択できる。一番基本のリスト |
| `ListView` | 列を持つ表のようなリスト（`GridView` を付ける）や、タイル表示 |
| `ComboBox` | ドロップダウンで 1 つ選ぶ |
| `DataGrid` | 編集もできる表。列ごとに型や編集方法を決められる |
| `TreeView` | 階層構造（第 35 章） |
| `TabControl` | タブ |

これらは全部 `ItemsControl` を元にしていて、使い方はほとんど共通です。`ItemsSource` に集まりを渡し、`ItemTemplate` で 1 件の見た目を決めます。部品を変えても、書き方はほとんど変わりません。

## 選択の扱い

選択できるリストは、「何が選ばれているか」をプロパティで持っています。

| プロパティ | 意味 |
| --- | --- |
| `SelectedItem` | 選ばれた要素そのもの（`object`） |
| `SelectedIndex` | 選ばれた要素の番号（なければ `-1`） |
| `SelectedValue` / `SelectedValuePath` | 要素の中の特定のプロパティの値で選ぶ |
| `SelectedItems` | 複数選択のときの、選ばれた要素の集まり（`SelectionMode="Extended"` など） |

`SelectedItem` は、依存関係プロパティなのでバインディングできます。

```xml
<ListBox ItemsSource="{Binding Items}"
         SelectedItem="{Binding SelectedItem, Mode=TwoWay}" />
```

ビューモデルに `SelectedItem` プロパティを用意すれば、選ばれたときにそこへ入ります。逆にビューモデル側から `SelectedItem = items[2]` と書けば、画面の選択も動きます。

`SelectedValue` は、たとえば `ComboBox` で「表示は名前、保存するのは ID」にしたいときに使います。

```xml
<ComboBox ItemsSource="{Binding Kinds}"
          DisplayMemberPath="Name"
          SelectedValuePath="Id"
          SelectedValue="{Binding KindId}" />
```

`DisplayMemberPath` は、要素のどのプロパティを表示に使うかの指定で、簡単な表示なら `ItemTemplate` の代わりになります。

### 複数選択はバインディングできない

`SelectedItems` は、依存関係プロパティではありません。そのため `{Binding SelectedItems}` と書けません。回避策はいくつかあります。

- コードビハインドの `SelectionChanged` で受け取って、ビューモデルに橋渡しする。
- 各要素に `IsSelected` のプロパティを持たせて、`ItemContainerStyle` で `IsSelected` を結び付ける（第 35 章のシーン ツリーがこの方法）。
- Behavior（第 22 章）で `SelectedItems` を扱う添付ビヘイビアを使う。

## 1 件ごとの見せ方を変える

### DataTemplate

第 12 章のとおりです。`ItemTemplate` に `DataTemplate` を書きます。

### 要素の種類で見た目を切り替える

リストの要素が、種類の違うオブジェクト（フォルダーとファイル、など）を含んでいるときは、型ごとに別のテンプレートを用意できます。

```xml
<ListBox.Resources>
    <DataTemplate DataType="{x:Type models:FolderEntry}">
        <TextBlock Text="{Binding Name, StringFormat=📁 {0}}" />
    </DataTemplate>
    <DataTemplate DataType="{x:Type models:FileEntry}">
        <TextBlock Text="{Binding Name}" />
    </DataTemplate>
</ListBox.Resources>
```

`DataType` を指定した `DataTemplate` は、その型の要素に自動で使われます。型以外の条件（値によって切り替えたい）なら、`DataTemplateSelector` を実装します。

```csharp
public class EntryTemplateSelector : DataTemplateSelector
{
    public DataTemplate? FolderTemplate { get; set; }
    public DataTemplate? FileTemplate { get; set; }

    public override DataTemplate? SelectTemplate(object item, DependencyObject container)
        => item is AssetEntry { IsDirectory: true } ? FolderTemplate : FileTemplate;
}
```

### 項目の入れ物（ItemContainerStyle）

リストの要素 1 つ 1 つは、`ListBoxItem` や `TreeViewItem` といった入れ物に包まれて表示されます。その入れ物のスタイルを決めるのが `ItemContainerStyle` です。選択された行の色、行の高さ、ダブルクリックのイベント、`IsSelected` や `IsExpanded` のバインディングは、ここに書きます。

```xml
<ListBox.ItemContainerStyle>
    <Style TargetType="ListBoxItem">
        <Setter Property="IsSelected" Value="{Binding IsSelected, Mode=TwoWay}" />
        <Setter Property="Padding" Value="4" />
    </Style>
</ListBox.ItemContainerStyle>
```

`DataTemplate`（中身の見た目）と `ItemContainerStyle`（入れ物の見た目と状態）の違いを意識しておくと、どちらに書くべきか迷いません。

## 並べ替え・絞り込み

`CollectionView` を使います（第 13 章）。元のコレクションは変えず、見せ方だけを変えられます。

## DataGrid

表を編集したいときは `DataGrid` を使います。

```xml
<DataGrid ItemsSource="{Binding Entries}" AutoGenerateColumns="False" CanUserAddRows="False">
    <DataGrid.Columns>
        <DataGridTextColumn Header="時刻" Binding="{Binding Time, StringFormat=HH:mm:ss}" IsReadOnly="True" />
        <DataGridTextColumn Header="重大度" Binding="{Binding Level}" IsReadOnly="True" />
        <DataGridTextColumn Header="メッセージ" Binding="{Binding Message}" Width="*" />
    </DataGrid.Columns>
</DataGrid>
```

`AutoGenerateColumns="True"` にすると、型のプロパティから列を自動で作りますが、どの列を出すか、列の名前、書式を細かく指定したいので、普通は `False` にして自分で列を並べます。

| 列の種類 | 用途 |
| --- | --- |
| `DataGridTextColumn` | 文字・数値 |
| `DataGridCheckBoxColumn` | `bool` |
| `DataGridComboBoxColumn` | 選択肢から選ぶ |
| `DataGridTemplateColumn` | 好きな見た目（ボタン、画像など）を入れる |

列の見出しをクリックすると並べ替えができ、これは `CollectionView` の機能です。

## 大量のデータを速く出す（仮想化）

1 万件のリストを `ListBox` に渡しても、普通は問題なく動きます。WPF は UI 仮想化といって、画面に見えている分だけ入れ物（`ListBoxItem`）を作り、スクロールすると使い回すからです。

ところが、仮想化が効かなくなる条件があって、それに気づかないと急に重くなります。

| 仮想化が切れる条件 | 対処 |
| --- | --- |
| 縦の `StackPanel` や `ScrollViewer` の中に置いている（高さが無制限になる） | `Grid` の `*` の行に置く。外側の `ScrollViewer` を外す |
| `ItemsPanel` を `WrapPanel` などに変えている（第 40 章のタイル表示） | `VirtualizingStackPanel` 以外のパネルは、標準では仮想化しない。数が少ないときだけ使う |
| `ScrollViewer.CanContentScroll="False"` | 既定の `True` に戻す |
| `TreeView` | 既定では仮想化されない。`VirtualizingStackPanel.IsVirtualizing="True"` を付ける |
| 要素を `ListBoxItem` として直接並べている（バインディングを使わない） | `ItemsSource` で渡す |

仮想化を強めたいときは、次の指定が使えます。

```xml
<ListBox VirtualizingStackPanel.IsVirtualizing="True"
         VirtualizingStackPanel.VirtualizationMode="Recycling"
         ScrollViewer.IsDeferredScrollingEnabled="True" />
```

`Recycling` は、使い終わった入れ物を作り直さず再利用する指定です。`IsDeferredScrollingEnabled` は、スクロール バーのつまみを動かしている間は、中身の更新を後回しにします。

UI 仮想化は、入れ物の数を減らす工夫です。データそのもの（1 万件のオブジェクト）はメモリ上にあります。数十万件を超えるようなデータは、必要な分だけ読み込む「データ仮想化」を自分で組む必要があります。

## 項目の追加・削除と画面

`ObservableCollection` は、追加・削除をすると、画面が自動で更新されます。ただし、複数の要素を一度に追加すると、要素ごとに通知が飛んで重くなります。まとめて入れたいときは、次のような手があります。

- 新しいコレクションを作って、プロパティごと差し替える（プロパティの通知が必要）。
- 追加の間だけ、画面との接続を外す（`ItemsSource = null` にしておいて、追加後に戻す）。

100 件程度なら気にしなくて構いません。数千件を一度に入れるときに、重さを感じたら思い出してください。

## この章のまとめ

- リスト系の部品は全部 `ItemsControl` の仲間。使い方は共通で、`ItemsSource` と `ItemTemplate`。
- 選択は `SelectedItem`（双方向でバインド）。複数選択は直接バインドできないので、`IsSelected` を要素に持たせるなどの工夫をする。
- 要素の見た目は `DataTemplate`、入れ物の状態は `ItemContainerStyle`。
- 大量に出すときは、仮想化が切れていないかを確かめる。縦の `StackPanel` の中は、まず疑う。

次の章では、画面を固まらせないための非同期処理と、UI スレッドの決まりごとを説明します。

[第 15 章 非同期処理と UI スレッド](15-async-ui.md) へ進みます。
