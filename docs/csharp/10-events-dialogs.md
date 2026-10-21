---
title: 第 10 章 イベント集約、ダイアログ、サービス
tags:
  - C#連携
---

# 第 10 章 イベント集約、ダイアログ、サービス

この章では Prism の残りの大事な 3 つ <strong>IEventAggregator</strong>（部品どうしのメッセージ）、<strong>ダイアログ サービス</strong>（ビューモデルから、ダイアログを開く）、そして<strong>サービス</strong>（共有する機能の置き場所）を学びます。この章で第 2 部（C#・WPF・Prism の学習）は終わりです。

## この章の考え方

第 9 章で画面を機能ごとのモジュールに分けました。すると、次の問題が出てきます。

> シーン ツリーで「Cube」を選んだらプロパティ パネルに Cube の値を出したい。でもシーン ツリーのモジュールとプロパティのモジュールは、お互いを知らない。どうやって伝える？

直接、お互いの参照を持つとモジュールを分けた意味がなくなります。解決は 2 つあります。

| 方法 | 仕組み | 向いている場面 |
| --- | --- | --- |
| <strong>共有サービス</strong> | 両方が同じ「選択サービス」を DI で受け取り、そこに書き込み・読み取りをする | 「今の状態」を共有する（今の選択、今開いているシーン） |
| <strong>イベント集約（EventAggregator）</strong> | 片方がメッセージを「公開」し、もう片方が「購読」する。お互いは相手を知らない | 「何かが起きた」という通知（保存されたログが追加された） |

この教材では両方を使います。状態を持つものはサービス、通知はイベント集約、と使い分けます。

## この章のゴール

- `IEventAggregator` でモジュール間のメッセージを送受信できる。
- `IDialogService` でビューモデルからダイアログを開ける。
- 共有サービス（ログ、選択）を作り DI で配れる。

## 手順 1：IEventAggregator

### イベントの型を作る

メッセージの種類ごとに `PubSubEvent<T>` を継承した型を作ります。`T` はメッセージの中身（ペイロード）です。

```csharp
using Prism.Events;

namespace Editor.Infrastructure.Events;

// 「選択が変わった」。中身は、選ばれた物の ID（何も選ばれていなければ null）
public class SelectionChangedEvent : PubSubEvent<int?>
{
}
```

### 公開（Publish）

```csharp
public class SceneTreeViewModel : BindableBase
{
    private readonly IEventAggregator _events;

    public SceneTreeViewModel(IEventAggregator events)
    {
        _events = events;
    }

    private void OnSelected(int objectId)
    {
        _events.GetEvent<SelectionChangedEvent>().Publish(objectId);
    }
}
```

### 購読（Subscribe）

```csharp
public class PropertyViewModel : BindableBase
{
    public PropertyViewModel(IEventAggregator events)
    {
        events.GetEvent<SelectionChangedEvent>().Subscribe(OnSelectionChanged);
    }

    private void OnSelectionChanged(int? objectId)
    {
        // 選ばれた物に応じて、表示を切り替える
    }
}
```

`IEventAggregator` は Prism が DI コンテナーに登録済みなので、コンストラクターの引数に書くだけで受け取れます。

| 新しく出てきたもの | 説明 |
| --- | --- |
| `IEventAggregator` | メッセージの<strong>仲介役</strong>。発信側と受信側はお互いを知らずこれだけを知っている |
| `PubSubEvent<TPayload>` | イベントの種類を表す基底クラス。派生クラスを作って種類を区別する |
| `GetEvent<T>()` | その種類のイベント オブジェクトを取り出す。同じ型なら常に同じオブジェクトが返る |
| `Publish(payload)` | メッセージを送る。購読している全員の関数が呼ばれる |
| `Subscribe(action)` | 受け取る関数を登録する |
| `int?` | `null` を許す `int`（第 5 章）。「何も選ばれていない」を表すために使う |

### スレッドの指定

```csharp
events.GetEvent<LogAddedEvent>().Subscribe(
    OnLogAdded,
    ThreadOption.UIThread,       // UI スレッドで呼ぶ
    keepSubscriberReferenceAlive: false);
```

| 引数 | 意味 |
| --- | --- |
| `ThreadOption.PublisherThread` | 既定。<strong>送った側のスレッド</strong>で呼ぶ |
| `ThreadOption.UIThread` | <strong>UI スレッド</strong>で呼ぶ。画面を触る処理はこれにする |
| `ThreadOption.BackgroundThread` | 別のスレッドで呼ぶ |
| `keepSubscriberReferenceAlive` | `false`（既定）なら購読者を<strong>弱い参照</strong>で持つ。購読者が不要になれば GC で片付く。`true` なら強い参照（購読を解除するまで残る） |
| `filter` | 受け取る条件を関数で指定する |

!!! warning "UI スレッドの決まり"
    WPF の画面の部品は <strong>作ったスレッド（UI スレッド）からしか触れません</strong>。別のスレッドから触ると `InvalidOperationException` になります。エンジンのログのように別のスレッドから届く通知を画面に出すときは、`ThreadOption.UIThread` にします。

### 購読を解除する

```csharp
private SubscriptionToken? _token;

_token = events.GetEvent<SelectionChangedEvent>().Subscribe(OnSelectionChanged);
// 不要になったら
events.GetEvent<SelectionChangedEvent>().Unsubscribe(_token);
```

`Subscribe` は解除に使う `SubscriptionToken` を返します。

## 手順 2：共有サービス

「今の選択」のような<strong>状態</strong>はイベントだけだと後から画面を開いたときに値が分かりません。状態はサービスに持たせます。

### ログ サービス

エンジン側のログ（第 2 章の `SetLogCallback`）も最終的にここに集めます。今は C# 側のログだけを作ります。

```csharp
using System.Collections.ObjectModel;

namespace Editor.Services;

public enum LogLevel { Info, Warning, Error }

public record LogEntry(DateTime Time, LogLevel Level, string Message);

public interface ILogService
{
    ObservableCollection<LogEntry> Entries { get; }
    void Info(string message);
    void Warning(string message);
    void Error(string message);
}
```

実装では UI スレッド以外から呼ばれても安全にします。

```csharp
using System.Windows;

namespace Editor.Services;

public class LogService : ILogService
{
    public ObservableCollection<LogEntry> Entries { get; } = new();

    public void Info(string message) => Add(LogLevel.Info, message);
    public void Warning(string message) => Add(LogLevel.Warning, message);
    public void Error(string message) => Add(LogLevel.Error, message);

    private void Add(LogLevel level, string message)
    {
        var entry = new LogEntry(DateTime.Now, level, message);
        // ObservableCollection は UI スレッドで変更する必要がある
        var dispatcher = Application.Current.Dispatcher;
        if (dispatcher.CheckAccess())
        {
            Entries.Add(entry);
        }
        else
        {
            dispatcher.BeginInvoke(() => Entries.Add(entry));
        }
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `enum` | 列挙型。`LogLevel.Info` のように型名を付けて参照する |
| `record LogEntry(DateTime Time, …)` | 値の入れ物。コンストラクターとプロパティが自動で作られる |
| `Dispatcher` | UI スレッドの<strong>仕事の受付</strong>。`Application.Current.Dispatcher` で取る |
| `CheckAccess()` | 今のスレッドが UI スレッドかどうか |
| `BeginInvoke(action)` | UI スレッドに仕事を依頼する（待たずに戻る）。`Invoke` は完了まで待つ |
| `DateTime.Now` | 現在時刻 |

`App.xaml.cs` の `RegisterTypes` で登録します。

```csharp
containerRegistry.RegisterSingleton<ILogService, LogService>();
```

### ログ パネルに表示する

`LogViewModel` が `ILogService` を受け取り `Entries` を公開します。

```csharp
public class LogViewModel : BindableBase
{
    public string Title => "ログ";
    public ObservableCollection<LogEntry> Entries { get; }

    public LogViewModel(ILogService log)
    {
        Entries = log.Entries;
        log.Info("エディタを起動しました");
    }
}
```

```xml
<ListBox ItemsSource="{Binding Entries}">
    <ListBox.ItemTemplate>
        <DataTemplate>
            <StackPanel Orientation="Horizontal">
                <TextBlock Text="{Binding Time, StringFormat=HH:mm:ss}" Foreground="Gray" />
                <TextBlock Text="{Binding Level}" Margin="8,0" Width="60" />
                <TextBlock Text="{Binding Message}" />
            </StackPanel>
        </DataTemplate>
    </ListBox.ItemTemplate>
</ListBox>
```

### 選択サービス

```csharp
using Prism.Events;
using Prism.Mvvm;

using Editor.Infrastructure.Events;

namespace Editor.Services;

public interface ISelectionService
{
    int? SelectedId { get; set; }
}

public class SelectionService : BindableBase, ISelectionService
{
    private readonly IEventAggregator _events;

    public SelectionService(IEventAggregator events)
    {
        _events = events;
    }

    private int? _selectedId;
    public int? SelectedId
    {
        get => _selectedId;
        set
        {
            if (SetProperty(ref _selectedId, value))
            {
                _events.GetEvent<SelectionChangedEvent>().Publish(value);   // 状態を持ち、変化を通知する
            }
        }
    }
}
```

状態の保持と変化の通知を <strong>1 つのサービスにまとめる</strong>のが、よく使う形です。

| 新しく出てきたもの | 説明 |
| --- | --- |
| `SetProperty` の戻り値 | 値が変わったとき `true`。変わっていなければ `false` を返すので、`if` で通知の要否を決められる |
| `BindableBase` をサービスにも使う | `INotifyPropertyChanged` が欲しいだけならビューモデル以外にも使える |
| サービスの生存期間 | 状態を共有するので、`RegisterSingleton`（アプリで 1 つ） |

## 手順 3：ダイアログ サービス

「ファイルを保存しますか？」のような確認や入力ダイアログをビューモデルから開きたいことがあります。ビューモデルが `MessageBox` を直接呼ぶと画面に依存してしまいテストできません。Prism の <strong>`IDialogService`</strong> を使います。

!!! warning "Prism 9 の変更点"
    ダイアログの API は Prism 8 から 9 で変わりました。この教材は <strong>Prism 9</strong> です。Prism 8 以前の記事では名前空間が `Prism.Services.Dialogs`、`IDialogAware.RequestClose` が `event Action<IDialogResult>` でした。Prism 9 では名前空間が `Prism.Dialogs`、`RequestClose` は `DialogCloseListener` 型です。コンパイル エラーが出たら使っている Prism の版を確認してください。

### ダイアログのビュー

`Views\ConfirmDialog.xaml`:

```xml
<UserControl x:Class="Editor.Views.ConfirmDialog"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:prism="http://prismlibrary.com/"
             prism:ViewModelLocator.AutoWireViewModel="True"
             Width="320">
    <StackPanel Margin="16">
        <TextBlock Text="{Binding Message}" TextWrapping="Wrap" />
        <StackPanel Orientation="Horizontal" HorizontalAlignment="Right" Margin="0,16,0,0">
            <Button Content="はい" Command="{Binding YesCommand}" Width="72" Margin="0,0,8,0" />
            <Button Content="いいえ" Command="{Binding NoCommand}" Width="72" />
        </StackPanel>
    </StackPanel>
</UserControl>
```

ダイアログの中身は `UserControl` です。外側のウィンドウは Prism が作ります。

### ダイアログのビューモデル

```csharp
using Prism.Commands;
using Prism.Dialogs;
using Prism.Mvvm;

namespace Editor.ViewModels;

public class ConfirmDialogViewModel : BindableBase, IDialogAware
{
    private string _message = "";
    public string Message
    {
        get => _message;
        set => SetProperty(ref _message, value);
    }

    public string Title => "確認";

    public DelegateCommand YesCommand { get; }
    public DelegateCommand NoCommand { get; }

    public ConfirmDialogViewModel()
    {
        YesCommand = new DelegateCommand(() => Close(ButtonResult.Yes));
        NoCommand = new DelegateCommand(() => Close(ButtonResult.No));
    }

    // 閉じるための窓口（Prism 9）
    public DialogCloseListener RequestClose { get; }

    private void Close(ButtonResult result)
    {
        RequestClose.Invoke(new DialogResult(result));
    }

    public bool CanCloseDialog() => true;
    public void OnDialogClosed() { }

    public void OnDialogOpened(IDialogParameters parameters)
    {
        Message = parameters.GetValue<string>("message");
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `IDialogAware` | ダイアログのビューモデルが実装するインターフェース |
| `Title` | ダイアログのウィンドウのタイトル |
| `RequestClose`（Prism 9） | ダイアログを閉じる依頼。`Invoke(new DialogResult(結果))` で結果つきで閉じる |
| `ButtonResult` | `OK`、`Cancel`、`Yes`、`No` などどのボタンで閉じたかを表す列挙型 |
| `CanCloseDialog()` | 閉じてよいか。`false` を返すと閉じられない（入力途中の確認など） |
| `OnDialogClosed()` | 閉じた後の後始末 |
| `OnDialogOpened(parameters)` | 開いたときに呼ばれる。呼び出し側が渡した値を `IDialogParameters` から読む |
| `parameters.GetValue<T>(key)` | 渡された値を取り出す |

### 登録して開く

`RegisterTypes` でビューとビューモデルを登録します。

```csharp
containerRegistry.RegisterDialog<ConfirmDialog, ConfirmDialogViewModel>();
```

開く側（任意のビューモデル）は `IDialogService` を受け取ります。

```csharp
public class MainWindowViewModel : BindableBase
{
    private readonly IDialogService _dialogs;

    public MainWindowViewModel(IDialogService dialogs)
    {
        _dialogs = dialogs;
    }

    private void ConfirmExit()
    {
        var parameters = new DialogParameters { { "message", "保存せずに終了しますか？" } };
        _dialogs.ShowDialog(nameof(ConfirmDialog), parameters, result =>
        {
            if (result.Result == ButtonResult.Yes)
            {
                Application.Current.Shutdown();
            }
        });
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `IDialogService` | ダイアログを開くサービス。DI で受け取る |
| `ShowDialog(名前, パラメーター, コールバック)` | モーダル（閉じるまで他を操作できない）で開く。閉じたときコールバックが呼ばれる |
| `nameof(ConfirmDialog)` | 型や変数の<strong>名前を文字列で</strong>得る式。`"ConfirmDialog"` になる。名前を変えたときに追従する |
| `DialogParameters` | ダイアログに渡す値の入れ物（キーと値の組） |
| `result.Result` | どのボタンで閉じたか |
| `Show`（`ShowDialog` との違い） | `Show` はモードレス（他の操作もできる） |

ダイアログのウィンドウの見た目（枠、アイコン、大きさ）を変えたいときは `RegisterDialogWindow<T>()` で、自作の `Window` を登録できます。

## 手順 4：ファイル ダイアログ

「ファイルを開く」「保存」のダイアログは、WPF 標準の `OpenFileDialog` / `SaveFileDialog` があります。これもビューモデルから直接呼ぶと画面に依存するので、サービスに包みます。

```csharp
using Microsoft.Win32;

namespace Editor.Services;

public interface IFileDialogService
{
    string? OpenFile(string filter);
    string? SaveFile(string filter, string defaultName);
}

public class FileDialogService : IFileDialogService
{
    public string? OpenFile(string filter)
    {
        var dialog = new OpenFileDialog { Filter = filter };
        return dialog.ShowDialog() == true ? dialog.FileName : null;
    }

    public string? SaveFile(string filter, string defaultName)
    {
        var dialog = new SaveFileDialog { Filter = filter, FileName = defaultName };
        return dialog.ShowDialog() == true ? dialog.FileName : null;
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `OpenFileDialog` / `SaveFileDialog` | `Microsoft.Win32` 名前空間の標準のファイル選択ダイアログ |
| `Filter` | `"シーン (*.scene)\|*.scene\|すべて (*.*)\|*.*"` のように `表示名\|パターン` を `\|` でつなぐ |
| `ShowDialog()` の戻り値 | `bool?`（`true`、`false`、`null` の 3 値）。OK で閉じたとき `true` |
| `== true` | `bool?` を `true` と比べる。`null` や `false` のときは偽になる |
| `string?` を返す | キャンセルされたとき `null` を返す |

登録は `containerRegistry.RegisterSingleton<IFileDialogService, FileDialogService>();`。

## 手順 5：サービスの全体像

ここまででアプリ共通のサービスが出そろいました。

| サービス | 役割 | 登録 | 使う章 |
| --- | --- | --- | --- |
| `ILogService` | ログの収集と表示 | シングルトン | 全体 |
| `ISelectionService` | 今の選択の共有 | シングルトン | 第 21〜23 章 |
| `IFileDialogService` | ファイルを開く・保存 | シングルトン | 第 25〜26 章 |
| `IDialogService`（Prism） | ダイアログを開く | Prism が登録済み | 全体 |
| `IEventAggregator`（Prism） | メッセージの仲介 | Prism が登録済み | 全体 |
| `IRegionManager`（Prism） | リージョンの管理 | Prism が登録済み | 第 9 章 |
| `IEngineService` | エンジンの窓口 | シングルトン | 第 13 章以降 |

## 動作確認

| 見る所 | 期待する結果 |
| --- | --- |
| 起動 | ログ タブに「エディタを起動しました」が出る |
| 選択サービス | （第 21 章で試す）選択を変えると、プロパティ パネルが変わる |
| ダイアログ | 確認ダイアログが開き「はい」「いいえ」で閉じて、結果が分かれる |

## よくあるミス

??? failure "別スレッドから `ObservableCollection` を変更して例外になる"
    `NotSupportedException: This type of CollectionView does not support changes to its SourceCollection from a thread different from the Dispatcher thread`。UI スレッドへ `Dispatcher.BeginInvoke` で渡す。

??? failure "イベントを購読しているのに、呼ばれない"
    `keepSubscriberReferenceAlive: false`（既定）で購読者が GC に片付けられた。購読者をどこかが保持しているか確認する。ビューモデルはビューの `DataContext` が持つので、通常は消えない。

??? failure "ダイアログが開かない（`ContainerResolutionException`）"
    `RegisterDialog` を忘れている。または、`ShowDialog` に渡す名前がビューの型名と違う。

??? failure "`DialogCloseListener` が見つからない（`CS0246`）"
    Prism 8 以前のパッケージを使っている。`Prism.DryIoc` を 9 以降に更新する。または、Prism 8 のコードを写している。

## 第 2 部のまとめ

| 章 | 学んだこと |
| --- | --- |
| 第 5 章 | C# の基本（型、クラス、プロパティ、null、コレクション、デリゲート、`using`） |
| 第 6 章 | WPF と XAML（要素、プロパティ、レイアウト、リソース） |
| 第 7 章 | データ バインディング、MVVM、`INotifyPropertyChanged`、`ICommand` |
| 第 8 章 | Prism、DI コンテナー、ViewModelLocator、`BindableBase`、`DelegateCommand` |
| 第 9 章 | リージョン、モジュール、ナビゲーション |
| 第 10 章 | `IEventAggregator`、ダイアログ サービス、共有サービス |

エディタの<strong>画面の骨組み</strong>が、完成しました。しかし、まだエンジンとはつながっていません。

## 次の章へ

次の章（[第 11 章 C# から C++ を呼ぶ：連携方式の比較](11-interop-overview.md)）から、第 3 部です。C# と C++ をつなぐ方法を整理し、この教材で使う方式を決めます。
