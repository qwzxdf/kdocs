---
title: 第 24 章 イベント集約、ダイアログ、サービス
tags:
  - C#連携
---

# 第 24 章 イベント集約、ダイアログ、サービス

第 23 章で、画面を機能ごとのモジュールに分けました。すると今度は、こういう問題が出てきました。実行すると、シーン ツリーでどのオブジェクトを選んでも、プロパティ パネルは「(仮) Cube」のままです。

!!! info "このページを読む前に"
    - [第 23 章 リージョン、モジュール、ナビゲーション](23-regions-modules.md)（前の章。この章は、そこで分けたモジュールをつなぐ）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）

> シーン ツリーで「Cube」を選んだら、プロパティ パネルに Cube の値を出したい。でも、シーン ツリーのモジュールとプロパティのモジュールは、お互いを知らない。どうやって伝える？

お互いの参照を持たせてしまうと、せっかく分けた意味がなくなります。この章では、お互いを知らない部品どうしが連絡を取る方法（`IEventAggregator` と共有サービス）、ビューモデルからダイアログを開く方法、そして共通の機能を置く「サービス」の作り方を学びます。第 2 部の最後の章です。

!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Scene/SelectionChangedEvent.cs`（新規） | 「選択が変わった」というメッセージ |
    | `Scene/SelectionService.cs`（新規） | 今の選択を持つサービス |
    | `Log/LogService.cs`（新規） | ログの収集。どのスレッドからでも呼べる |
    | `Shared/FileDialogService.cs`（新規） | ファイルを開く・保存するダイアログを包む（使うのは第 45 章） |
    | `Shared/Dialogs/ConfirmDialog.xaml`・`ConfirmDialogViewModel.cs`（新規） | 「はい」「いいえ」の確認ダイアログ |
    | `SceneTreeViewModel`・`PropertyViewModel`・`MainWindowViewModel`（変更） | 選択をつなぐ。終了のときに確認する |
    | `LogViewModel`・`AssetViewModel`（変更） | ログは `ILogService` を通す |
    | `App.xaml.cs`（変更） | サービスとダイアログを登録する |

## 連絡の取り方は 2 通りある

| 方法 | 仕組み | 向いている場面 |
| --- | --- | --- |
| 共有サービス | 両方が同じ「選択サービス」を DI で受け取って、そこに書き込み・読み取りをする | 「今の状態」を共有したいとき（今の選択、今開いているシーン） |
| イベント集約 | 片方がメッセージを送り（Publish）、もう片方が受け取る（Subscribe）。お互いは相手を知らない | 「何かが起きた」と知らせたいとき（保存された、ログが追加された） |

状態を持つものはサービス、出来事の通知はイベント集約、と使い分けるのが基本です。この章の選択は、両方を使います。

## 選択をつなぐ

### IEventAggregator

まず、メッセージの種類ごとに、`PubSubEvent<T>` を継承したクラスを作ります。`T` はメッセージに添える中身です。

```csharp title="Scene/SelectionChangedEvent.cs（新規）"
using Prism.Events;

namespace Editor.Scene;

// 「選択が変わった」。中身は選ばれたオブジェクト（何も選ばれていなければ null）
public class SelectionChangedEvent : PubSubEvent<SceneObjectViewModel?>
{
}
```

送る側と受け取る側は、どちらも `IEventAggregator` を DI で受け取ります（Prism が最初から登録してくれているので、自分で登録しなくて構いません）。

```csharp title="送る側の形"
_events.GetEvent<SelectionChangedEvent>().Publish(obj);
```

```csharp title="受け取る側の形"
events.GetEvent<SelectionChangedEvent>().Subscribe(OnSelectionChanged);
```

`SceneObjectViewModel?` の `?` は、「何も選ばれていない」を `null` で表すためのものです。`GetEvent<T>()` は、型ごとに 1 つの仲介オブジェクトを返します。送る側と受け取る側は、お互いを知らなくても、同じ型を指定するだけでつながります。

### どのスレッドで受け取るか

受け取る関数を呼ぶスレッドを指定できます。

```csharp
events.GetEvent<SelectionChangedEvent>().Subscribe(
    OnSelectionChanged,
    ThreadOption.UIThread,            // UI スレッドで呼んでもらう
    keepSubscriberReferenceAlive: false);
```

| 指定 | 意味 |
| --- | --- |
| `PublisherThread` | 送った側のスレッドで呼ぶ（既定） |
| `UIThread` | UI スレッドで呼ぶ。画面を触る処理は、これにする |
| `BackgroundThread` | 別のスレッドで呼ぶ |

WPF の画面の部品は、作ったスレッド（UI スレッド）からしか触れません。別のスレッドから触ると `InvalidOperationException` になります。エンジンのログのように、別のスレッドから届く通知を画面に出すときは、`UIThread` を指定してください。

`keepSubscriberReferenceAlive` は、受け取る側を「弱い参照」で持つかどうかの指定です。`false`（既定）なら弱い参照なので、受け取る側のオブジェクトが不要になれば GC が片付けてくれます。解除し忘れによるメモリの滞留が起きにくい、安全な設定です。

受け取るのをやめたいときは、`Subscribe` が返す `SubscriptionToken` を使って `Unsubscribe` します。

### 共有サービス：今の状態を持つ

イベントだけでは足りない場面があります。後から開いた画面は、イベントが送られたことを知らないので、今の選択が分からないからです。Editor でも起きます。起動すると、シーン ツリーのモジュールが先に初期化されて、最初の選択（`Cube`）を済ませます。そのあとで作られるプロパティ パネルは、その時点のイベントを受け取れません。

そこで、「今の選択」は、サービスに持たせます。サービスは、DI で配るただのクラスです。状態を持つことと、変わったときに知らせることを、1 つのクラスにまとめます。

```csharp title="Scene/SelectionService.cs（新規）"
using System.Reactive.Linq;
using Prism.Events;
using Reactive.Bindings;

namespace Editor.Scene;

public interface ISelectionService
{
    ReactivePropertySlim<SceneObjectViewModel?> Selected { get; }
}

public class SelectionService : ISelectionService
{
    public SelectionService(IEventAggregator events)
    {
        // 値が変わったら、イベントで知らせる。登録した時点の 1 回目は読み飛ばす
        Selected.Skip(1).Subscribe(value =>
            events.GetEvent<SelectionChangedEvent>().Publish(value));
    }

    public ReactivePropertySlim<SceneObjectViewModel?> Selected { get; } = new();
}
```

「今の選択」は、第 14 章と同じ `ReactivePropertySlim` で持ちます。`Selected.Skip(1)` は、`Subscribe` が登録時にも 1 回呼ばれる動き（第 14 章）を避けるための、読み飛ばしです。付けないと、サービスを作った瞬間に、`null` の選択変更が送られます。

ReactiveProperty は値の変化を購読できるので、受け取る側が `ISelectionService.Selected` を直接 `Subscribe` する書き方もできます。それでも `IEventAggregator` を挟んでいるのは、受け取る側が、サービスの型を知らなくてよくなるからです。イベントの型（`SelectionChangedEvent`）だけを共有します。

このサービスは、複数のモジュールが共有するので、`App` に登録します（第 23 章のとおりです）。

```csharp title="App.xaml.cs（変更）"
containerRegistry.RegisterSingleton<ISelectionService, SelectionService>();
```

### 3 か所をつなぐ

送る側のシーン ツリーは、選ばれたオブジェクトをサービスに書き込みます。

```csharp title="SceneTree/SceneTreeViewModel.cs（変更）"
private readonly ISelectionService _selection;

public SceneTreeViewModel(ISelectionService selection)
{
    _selection = selection;
    // 以下は前のとおり

    // 選択が変わったら、サービスに知らせる
    Selected.Subscribe(value => _selection.Selected.Value = value);
}
```

`Selected` の定義は、前の章のままです。変わったときの処理を、プロパティの外に 1 行書くだけで済みます。

受け取る側のプロパティは、作られたときにサービスから今の状態を読み、そのあとはイベントで追いかけます。

```csharp title="Property/PropertyViewModel.cs（変更）"
public PropertyViewModel(ISelectionService selection, IEventAggregator events)
{
    Target.Value = selection.Selected.Value;        // 後から開いたので、今の状態を読む
    events.GetEvent<SelectionChangedEvent>().Subscribe(
        obj => Target.Value = obj, ThreadOption.UIThread);   // 以降は変わるたびに受け取る
}
```

前の章で置いた「仮のオブジェクト」の行は、消します。

もう 1 か所、ステータス バーです。第 23 章で消した「選択中の名前」を、イベントで戻します。

```csharp title="MainWindowViewModel.cs（変更）"
public MainWindowViewModel(IRegionManager regionManager, IEventAggregator events)
{
    _regionManager = regionManager;
    NavigateCommand = new ReactiveCommand<string>().WithSubscribe(
        viewName => _regionManager.RequestNavigate(RegionNames.Property, viewName));

    events.GetEvent<SelectionChangedEvent>().Subscribe(
        obj => StatusText.Value = obj is null ? "準備完了" : $"選択: {obj.Name.Value}");
}
```

実行して、シーン ツリーで別の行を選ぶと、プロパティが切り替わり、ステータス バーの文字も変わります。3 つのクラスは、互いを知りません。同じ `SelectionChangedEvent` を指しているだけです。

この選択サービスは、1 つだけ選べる簡易版です。第 41 章で、複数選択にも対応した形に作り直します。

## ログをサービスにする

`LogViewModel` は、第 17 章で、どのスレッドからでも `Add` できるようにしました。ところが、`AssetViewModel` は、`LogViewModel`、つまり画面のビューモデルを受け取って、ログを書いています。画面のためのクラスに、ほかの機能が依存するのは、よい形ではありません。ログを書く機能を、画面から切り離して、サービスにします。

```csharp title="Log/LogService.cs（新規）"
using System.Collections.ObjectModel;
using System.Windows;

namespace Editor.Log;

public interface ILogService
{
    ObservableCollection<LogEntry> Entries { get; }
    void Info(string message);
    void Warning(string message);
    void Error(string message);
}

public class LogService : ILogService
{
    public ObservableCollection<LogEntry> Entries { get; } = new();

    public void Info(string message) => Add(LogLevel.Info, message);
    public void Warning(string message) => Add(LogLevel.Warning, message);
    public void Error(string message) => Add(LogLevel.Error, message);

    private void Add(LogLevel level, string message)
    {
        var entry = new LogEntry(DateTime.Now, level, message);
        // ObservableCollection は、UI スレッドで変更しなければならない
        var dispatcher = Application.Current.Dispatcher;
        if (dispatcher.CheckAccess())
            Entries.Add(entry);
        else
            dispatcher.InvokeAsync(() => Entries.Add(entry));
    }
}
```

`Dispatcher` は、UI スレッドへの仕事の受付窓口です。`CheckAccess()` は「今のスレッドが UI スレッドか」を返し、そうでなければ `InvokeAsync` で UI スレッドに仕事を頼みます（頼んだら待たずに戻ります）。第 17 章で `LogViewModel.Add` に書いた中身を、そのままサービスに移しました。

`LogViewModel` は、サービスの一覧を出すだけの小さなクラスになります。`AssetViewModel` は、`LogViewModel` の代わりに `ILogService` を受け取ります。

```csharp title="Log/LogViewModel.cs（変更：全体）"
using System.Collections.ObjectModel;

namespace Editor.Log;

public class LogViewModel
{
    public LogViewModel(ILogService log)
    {
        Entries = log.Entries;
        log.Info("Editor を起動しました");
    }

    public string Title => "ログ";
    public ObservableCollection<LogEntry> Entries { get; }
}
```

```csharp title="Asset/AssetViewModel.cs（変更）"
public AssetViewModel(ILogService log, IAssetScanner scanner)    // LogViewModel の代わり
```

`_log.Add(LogLevel.Info, msg)` と書いていた所は、`_log.Info(msg)`、`_log.Error(...)` に直します。

登録は、`LogViewModel` から `ILogService` に替えます。

```csharp title="App.xaml.cs（変更）"
// containerRegistry.RegisterSingleton<LogViewModel>();    // これは消す
containerRegistry.RegisterSingleton<ILogService, LogService>();
```

`LogViewModel` は ViewModelLocator が作るので、登録しなくても動きます。共有する実体は `LogService` の `Entries` のほうで、どちらのモジュールが先に初期化されても、同じ一覧を見ます。第 23 章の落とし穴が、これで起きなくなりました。

## ダイアログ

「保存しますか？」の確認や入力ダイアログをビューモデルから開きたいことがあります。ビューモデルから `MessageBox.Show` を直接呼ぶと、画面に依存してしまい、テストもできません。Prism の `IDialogService` を使います。Editor では、「ファイル → 終了」を選んだときの確認に使います。

!!! warning "Prism 9 の変更点"
    ダイアログの API は、Prism 8 から 9 で変わりました。8 までは名前空間が `Prism.Services.Dialogs` で、`IDialogAware` に `Title` があり、`RequestClose` はイベントでした。9 では名前空間が `Prism.Dialogs` になり、`Title` がなくなり、`RequestClose` は `DialogCloseListener` 型になっています。古い記事のコードがコンパイルできないときは、まずバージョンを疑ってください。

### ダイアログのビュー

ダイアログの中身は `UserControl` です。外側のウィンドウは Prism が作ります。ウィンドウのタイトルや大きさは、ビューの中の `prism:Dialog.WindowStyle` で指定します。

```xml title="Shared/Dialogs/ConfirmDialog.xaml（新規）"
<UserControl x:Class="Editor.Shared.Dialogs.ConfirmDialog"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:prism="http://prismlibrary.com/"
             prism:ViewModelLocator.AutoWireViewModel="True"
             Width="320">
    <prism:Dialog.WindowStyle>
        <Style TargetType="Window">
            <Setter Property="prism:Dialog.WindowStartupLocation" Value="CenterOwner" />
            <Setter Property="Title" Value="確認" />
            <Setter Property="SizeToContent" Value="WidthAndHeight" />
            <Setter Property="ResizeMode" Value="NoResize" />
        </Style>
    </prism:Dialog.WindowStyle>

    <StackPanel Margin="16">
        <TextBlock Text="{Binding Message.Value}" TextWrapping="Wrap" />
        <StackPanel Orientation="Horizontal" HorizontalAlignment="Right" Margin="0,16,0,0">
            <Button Content="はい" Command="{Binding YesCommand}" Width="72" Margin="0,0,8,0" />
            <Button Content="いいえ" Command="{Binding NoCommand}" Width="72" />
        </StackPanel>
    </StackPanel>
</UserControl>
```

### ダイアログのビューモデル

```csharp title="Shared/Dialogs/ConfirmDialogViewModel.cs（新規）"
using Prism.Dialogs;
using Reactive.Bindings;

namespace Editor.Shared.Dialogs;

public class ConfirmDialogViewModel : IDialogAware
{
    public ReactivePropertySlim<string> Message { get; } = new("");

    public ReactiveCommand YesCommand { get; }
    public ReactiveCommand NoCommand { get; }

    public ConfirmDialogViewModel()
    {
        YesCommand = new ReactiveCommand().WithSubscribe(() => RequestClose.Invoke(ButtonResult.Yes));
        NoCommand = new ReactiveCommand().WithSubscribe(() => RequestClose.Invoke(ButtonResult.No));
    }

    // ダイアログを閉じるための窓口。値は DialogService が設定するので、自分では代入しない
    public DialogCloseListener RequestClose { get; }

    public bool CanCloseDialog() => true;
    public void OnDialogClosed() { }

    public void OnDialogOpened(IDialogParameters parameters)
    {
        Message.Value = parameters.GetValue<string>("message");
    }
}
```

呼ばれる順は、ダイアログを開いて「いいえ」で閉じたとき、次のとおりです（Prism 9.0.537 で、各メンバーに出力を足して確かめました）。

```text title="実験の出力：開いて、「いいえ」で閉じたとき"
ctor                  （ビューモデルのコンストラクター）
OnDialogOpened
（ここで、ボタンを押す）
CanCloseDialog
OnDialogClosed
callback No           （ShowDialog に渡した、閉じたときの処理）
```

`ShowDialog` は、このあとで戻ります。`CanCloseDialog` が `false` を返すと、ダイアログは閉じられません。

`IDialogAware` には 4 つのメンバーがあります。

| メンバー | 役目 |
| --- | --- |
| `RequestClose` | ダイアログを閉じる依頼。`Invoke(ButtonResult.Yes)` のように、結果を添えて閉じる |
| `CanCloseDialog()` | 今、閉じてよいかを返す。`false` なら閉じられない（入力途中の確認など） |
| `OnDialogOpened(parameters)` | 開いたときに呼ばれる。呼び出し側が渡した値を `parameters` から読む |
| `OnDialogClosed()` | 閉じたあとの後片付け |

`ButtonResult` は `OK`、`Cancel`、`Yes`、`No` などのどのボタンで閉じたかを表す列挙型です。

### 登録して開く

```csharp title="App.xaml.cs（変更）"
containerRegistry.RegisterDialog<ConfirmDialog, ConfirmDialogViewModel>();
```

開く側は、`IDialogService` を受け取って `ShowDialog` を呼びます。メニューの「終了」に結びます。

```csharp title="MainWindowViewModel.cs（変更）"
private readonly IDialogService _dialogs;

public ReactiveCommand ExitCommand { get; }

// コンストラクターの引数に IDialogService dialogs を足して
_dialogs = dialogs;
ExitCommand = new ReactiveCommand().WithSubscribe(ConfirmExit);

private void ConfirmExit()
{
    var parameters = new DialogParameters { { "message", "保存せずに終了しますか？" } };
    _dialogs.ShowDialog(nameof(ConfirmDialog), parameters, new DialogCallback().OnClose(result =>
    {
        if (result.Result == ButtonResult.Yes)
        {
            Application.Current.Shutdown();
        }
    }));
}
```

```xml title="MainWindow.xaml（変更：ファイル メニュー）"
<MenuItem Header="終了(_X)" Command="{Binding ExitCommand}" />
```

`nameof(ConfirmDialog)` は、型の名前を文字列 `"ConfirmDialog"` として得る式です。名前を変えたときに自動で追従します。`DialogParameters` はダイアログに渡す値の入れ物で、キーと値の組を並べます。`DialogCallback` は Prism 9 で導入された、「閉じたときの処理」を指定する入れ物です。

`ShowDialog` は閉じるまで他の操作を止めるダイアログ、`Show` は他の操作もできるダイアログを開きます。ウィンドウ自体の見た目を変えたいときは、`RegisterDialogWindow<T>()` で自作の `Window` を登録します（第 25 章）。

## ファイルを開く・保存するダイアログ

`OpenFileDialog` と `SaveFileDialog` は WPF に最初から入っていますが、これもビューモデルから直接呼ぶと画面に依存します。小さなサービスに包んでおきます。使うのは第 45 章の保存・読み込みですが、ここで作って登録しておきます。

```csharp title="Shared/FileDialogService.cs（新規）"
using Microsoft.Win32;
using Editor.Engine;

namespace Editor.Shared;

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

```csharp title="App.xaml.cs（変更）"
containerRegistry.RegisterSingleton<IFileDialogService, FileDialogService>();
```

`Filter` は `"シーン (*.scene)|*.scene|すべて (*.*)|*.*"` のように、表示名とパターンを `|` でつなぎます。`ShowDialog()` が返すのは `bool?`（`true` / `false` / `null`）で、OK で閉じたときだけ `true` です。キャンセルされたときは `null` を返すことにしてあります。

## サービスの一覧

ここまでで、アプリ共通のサービスがそろいました。

| サービス | 役目 | 登録 |
| --- | --- | --- |
| `ILogService` | ログの収集と表示 | 自作、シングルトン |
| `ISelectionService` | 今の選択を共有 | 自作、シングルトン |
| `IFileDialogService` | ファイルを開く・保存 | 自作、シングルトン |
| `IAssetScanner` | アセットのフォルダーを読む | 自作、シングルトン（`AssetModule`） |
| `IDialogService` | ダイアログを開く | Prism が登録済み |
| `IEventAggregator` | メッセージの仲介 | Prism が登録済み |
| `IRegionManager` | リージョンの管理 | Prism が登録済み |
| `IEngineService` | エンジンの窓口 | 第 33 章で自作 |

## 動かして確かめる

- シーン ツリーで別のオブジェクトを選ぶと、プロパティ パネルの内容とステータス バーの「選択: …」が切り替わる。
- 起動直後から、プロパティ パネルに「Cube」が出ている（サービスから読んでいるから）。
- ログ タブに「Editor を起動しました」と出る。アセットの読み込みでも、ログが増える。
- 「ファイル → 終了」で確認ダイアログが開き、「いいえ」なら閉じるだけ、「はい」ならアプリが終わる。

??? failure "別のスレッドから `ObservableCollection` を変更して例外になる"
    `This type of CollectionView does not support changes to its SourceCollection from a thread different from the Dispatcher thread` と出ます。`Dispatcher` で UI スレッドに回してください（`LogService` はその形です）。

??? failure "イベントを購読しているのに、呼ばれない"
    受け取る側が GC に片付けられた可能性があります（`keepSubscriberReferenceAlive: false` の場合）。受け取る側のオブジェクトがどこかに保持されているか確かめます。ビューモデルは画面の `DataContext` が持っているので、普通は消えません。

??? failure "プロパティ パネルが、起動直後は空になる"
    `PropertyViewModel` のコンストラクターで、`selection.Selected` を読んでいますか。イベントだけに頼ると、あとから作られたビューモデルは、最初の選択を受け取れません。

??? failure "ダイアログが開かない"
    `RegisterDialog` を書き忘れているか、`ShowDialog` に渡した名前がビューの型名と違っています。

??? failure "`DialogCloseListener` が見つからない（`CS0246`）"
    使っている Prism のバージョンが 8 以前です。`Prism.DryIoc` を 9 以降に更新するか、Prism 8 用の書き方を調べてください。

## ここまでの Editor

```text
Editor/
├─ App.xaml.cs                       サービスとダイアログの登録
├─ Asset/                            選択がつながった。Log と Asset は ILogService を使う
├─ Log/
│   ├─ ILogService.cs / LogService.cs    ログ（新規）
│   └─ （LogEntry、LogView … 変更なし）
├─ Scene/
│   ├─ SelectionService.cs           今の選択（新規）
│   ├─ SelectionChangedEvent.cs      「選択が変わった」メッセージ（新規）
│   └─ SceneObjectViewModel.cs
├─ Shared/
│   ├─ RegionNames.cs
│   ├─ FileDialogService.cs          ファイル ダイアログ（新規）
│   └─ Dialogs/
│       ├─ ConfirmDialog.xaml
│       └─ ConfirmDialogViewModel.cs
├─ Property/ ・ SceneTree/           （選択サービスにつながった）
└─ MainWindowViewModel.cs            終了の確認、ステータス バーの選択表示
```

次の章では、画面遷移の確認、ビューの寿命、コマンドの束ね方など、Prism をもう少し掘り下げます。

[第 25 章 Prism を掘り下げる](25-prism-deep.md) へ進みます。
