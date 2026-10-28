---
title: 第 23 章 イベント集約、ダイアログ、サービス
tags:
  - C#連携
---

# 第 23 章 イベント集約、ダイアログ、サービス

第 22 章で、画面を機能ごとのモジュールに分けました。すると今度は、こういう問題が出てきます。

!!! info "このページを読む前に"
    - [第 22 章 リージョン、モジュール、ナビゲーション](22-regions-modules.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


> シーン ツリーで「Cube」を選んだら、プロパティ パネルに Cube の値を出したい。でも、シーン ツリーのモジュールとプロパティのモジュールは、お互いを知らない。どうやって伝える？

お互いの参照を持たせてしまうと、せっかく分けた意味がなくなります。この章では、お互いを知らない部品どうしが連絡を取る方法（`IEventAggregator` と共有サービス）、ビューモデルからダイアログを開く方法、そして共通の機能を置く「サービス」の作り方を学びます。第 2 部の最後の章です。

## 連絡の取り方は 2 通りある

| 方法 | 仕組み | 向いている場面 |
| --- | --- | --- |
| 共有サービス | 両方が同じ「選択サービス」を DI で受け取って、そこに書き込み・読み取りをする | 「今の状態」を共有したいとき（今の選択、今開いているシーン） |
| イベント集約 | 片方がメッセージを送り（Publish）、もう片方が受け取る（Subscribe）。お互いは相手を知らない | 「何かが起きた」と知らせたいとき（保存された、ログが追加された） |

状態を持つものはサービス、出来事の通知はイベント集約、と使い分けるのが基本です。この教材でも両方使います。

## IEventAggregator

まず、メッセージの種類ごとに、`PubSubEvent<T>` を継承したクラスを作ります。`T` はメッセージに添える中身です。

```csharp title="Infrastructure/Events/SelectionChangedEvent.cs"
using Prism.Events;

namespace Editor.Infrastructure.Events;

// 「選択が変わった」。中身は選ばれた物の ID（何も選ばれていなければ null）
public class SelectionChangedEvent : PubSubEvent<int?>
{
}
```

送る側と受け取る側は、どちらも `IEventAggregator` を DI で受け取ります（Prism が最初から登録してくれているので、自分で登録しなくて構いません）。

```csharp title="送る側（シーン ツリー）"
public SceneTreeViewModel(IEventAggregator events)
{
    _events = events;
}

private void OnSelected(int objectId)
{
    _events.GetEvent<SelectionChangedEvent>().Publish(objectId);
}
```

```csharp title="受け取る側（プロパティ）"
public PropertyViewModel(IEventAggregator events)
{
    events.GetEvent<SelectionChangedEvent>().Subscribe(OnSelectionChanged);
}

private void OnSelectionChanged(int? objectId)
{
    // 選ばれた物に応じて表示を切り替える
}
```

`int?` は「`null` も入れられる `int`」で、「何も選ばれていない」を `null` で表すために使っています。`GetEvent<T>()` は、型ごとに 1 つの仲介オブジェクトを返します。送る側と受け取る側は、お互いを知らなくても、同じ型を指定するだけでつながります。

### どのスレッドで受け取るか

受け取る関数を呼ぶスレッドを指定できます。

```csharp
events.GetEvent<LogAddedEvent>().Subscribe(
    OnLogAdded,
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

## 共有サービス

「今の選択」のような状態は、イベントだけでは足りません。後から開いた画面は、イベントが送られたことを知らないので、今の状態が分からないからです。状態は、サービスに持たせます。

サービスは、DI で配るただのクラスです。まずはログのサービスを作ります。

```csharp title="Services/LogService.cs"
using System.Collections.ObjectModel;
using System.Windows;

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

`Dispatcher` は、UI スレッドへの仕事の受付窓口です。`CheckAccess()` は「今のスレッドが UI スレッドか」を返し、そうでなければ `BeginInvoke` で UI スレッドに仕事を頼みます（頼んだら待たずに戻ります）。ログは、エンジンから別のスレッドで呼ばれることがあるので、この作りにしておきます。

`App.xaml.cs` の `RegisterTypes` で登録します。

```csharp
containerRegistry.RegisterSingleton<ILogService, LogService>();
```

ログ パネルのビューモデルは、`ILogService` を受け取って `Entries` を公開するだけです。

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

次は選択のサービスです。状態を持つことと、変わったときに知らせることを 1 つのクラスにまとめます。

```csharp title="Services/SelectionService.cs"
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
                _events.GetEvent<SelectionChangedEvent>().Publish(value);
            }
        }
    }
}
```

`SetProperty` は値が変わったときだけ `true` を返すので、変わったときにだけイベントを送れます。`BindableBase` は、`INotifyPropertyChanged` が欲しいだけなら、ビューモデル以外でも使えます。

この選択サービスは、仕組みを見るための簡易版です。第 40 章で、物そのもの（`SceneObject`）を持ち、複数選択にも対応した形に作り直します。

## ダイアログ

「保存しますか？」の確認や入力ダイアログをビューモデルから開きたいことがあります。ビューモデルから `MessageBox.Show` を直接呼ぶと、画面に依存してしまい、テストもできません。Prism の `IDialogService` を使います。

!!! warning "Prism 9 の変更点"
    ダイアログの API は、Prism 8 から 9 で変わりました。8 までは名前空間が `Prism.Services.Dialogs` で、`IDialogAware` に `Title` があり、`RequestClose` はイベントでした。9 では名前空間が `Prism.Dialogs` になり、`Title` がなくなり、`RequestClose` は `DialogCloseListener` 型になっています。古い記事のコードがコンパイルできないときは、まずバージョンを疑ってください。

### ダイアログのビュー

ダイアログの中身は `UserControl` です。外側のウィンドウは Prism が作ります。ウィンドウのタイトルや大きさは、ビューの中の `prism:Dialog.WindowStyle` で指定します。

```xml title="Dialogs/ConfirmDialog.xaml"
<UserControl x:Class="Editor.Dialogs.ConfirmDialog"
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
        <TextBlock Text="{Binding Message}" TextWrapping="Wrap" />
        <StackPanel Orientation="Horizontal" HorizontalAlignment="Right" Margin="0,16,0,0">
            <Button Content="はい" Command="{Binding YesCommand}" Width="72" Margin="0,0,8,0" />
            <Button Content="いいえ" Command="{Binding NoCommand}" Width="72" />
        </StackPanel>
    </StackPanel>
</UserControl>
```

### ダイアログのビューモデル

```csharp title="Dialogs/ConfirmDialogViewModel.cs"
using Prism.Commands;
using Prism.Dialogs;
using Prism.Mvvm;

namespace Editor.Dialogs;

public class ConfirmDialogViewModel : BindableBase, IDialogAware
{
    private string _message = "";
    public string Message
    {
        get => _message;
        set => SetProperty(ref _message, value);
    }

    public DelegateCommand YesCommand { get; }
    public DelegateCommand NoCommand { get; }

    public ConfirmDialogViewModel()
    {
        YesCommand = new DelegateCommand(() => RequestClose.Invoke(ButtonResult.Yes));
        NoCommand = new DelegateCommand(() => RequestClose.Invoke(ButtonResult.No));
    }

    // ダイアログを閉じるための窓口。値は DialogService が設定するので、自分では代入しない
    public DialogCloseListener RequestClose { get; }

    public bool CanCloseDialog() => true;
    public void OnDialogClosed() { }

    public void OnDialogOpened(IDialogParameters parameters)
    {
        Message = parameters.GetValue<string>("message");
    }
}
```

`IDialogAware` には 4 つのメンバーがあります。

| メンバー | 役目 |
| --- | --- |
| `RequestClose` | ダイアログを閉じる依頼。`Invoke(ButtonResult.Yes)` のように、結果を添えて閉じる |
| `CanCloseDialog()` | 今、閉じてよいかを返す。`false` なら閉じられない（入力途中の確認など） |
| `OnDialogOpened(parameters)` | 開いたときに呼ばれる。呼び出し側が渡した値を `parameters` から読む |
| `OnDialogClosed()` | 閉じたあとの後片付け |

`ButtonResult` は `OK`、`Cancel`、`Yes`、`No` などのどのボタンで閉じたかを表す列挙型です。

### 登録して開く

```csharp
containerRegistry.RegisterDialog<ConfirmDialog, ConfirmDialogViewModel>();
```

開く側は、`IDialogService` を受け取って `ShowDialog` を呼びます。

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
        _dialogs.ShowDialog(nameof(ConfirmDialog), parameters, new DialogCallback().OnClose(result =>
        {
            if (result.Result == ButtonResult.Yes)
            {
                Application.Current.Shutdown();
            }
        }));
    }
}
```

`nameof(ConfirmDialog)` は、型の名前を文字列 `"ConfirmDialog"` として得る式です。名前を変えたときに自動で追従します。`DialogParameters` はダイアログに渡す値の入れ物で、キーと値の組を並べます。`DialogCallback` は Prism 9 で導入された、「閉じたときの処理」を指定する入れ物です。

`ShowDialog` は閉じるまで他の操作を止めるダイアログ、`Show` は他の操作もできるダイアログを開きます。ウィンドウ自体の見た目を変えたいときは、`RegisterDialogWindow<T>()` で自作の `Window` を登録します（第 24 章）。

## ファイルを開く・保存するダイアログ

`OpenFileDialog` と `SaveFileDialog` は WPF に最初から入っていますが、これもビューモデルから直接呼ぶと画面に依存します。小さなサービスに包みます。

```csharp title="Services/FileDialogService.cs"
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

`Filter` は `"シーン (*.scene)|*.scene|すべて (*.*)|*.*"` のように、表示名とパターンを `|` でつなぎます。`ShowDialog()` が返すのは `bool?`（`true` / `false` / `null`）で、OK で閉じたときだけ `true` です。キャンセルされたときは `null` を返すことにしてあります。

## サービスの一覧

ここまでで、アプリ共通のサービスがそろいました。

| サービス | 役目 | 登録 |
| --- | --- | --- |
| `ILogService` | ログの収集と表示 | 自作、シングルトン |
| `ISelectionService` | 今の選択を共有 | 自作、シングルトン |
| `IFileDialogService` | ファイルを開く・保存 | 自作、シングルトン |
| `IDialogService` | ダイアログを開く | Prism が登録済み |
| `IEventAggregator` | メッセージの仲介 | Prism が登録済み |
| `IRegionManager` | リージョンの管理 | Prism が登録済み |
| `IEngineService` | エンジンの窓口 | 第 32 章で自作 |

## 動かして確かめる

- 起動すると、ログ タブに「エディタを起動しました」と出る。
- 確認ダイアログが開き、「はい」「いいえ」で閉じて、結果によって処理が分かれる。
- 選択サービスの動きは、第 40 章で実際に試す。

??? failure "別のスレッドから `ObservableCollection` を変更して例外になる"
    `This type of CollectionView does not support changes to its SourceCollection from a thread different from the Dispatcher thread` と出ます。`Dispatcher.BeginInvoke` で UI スレッドに回してください。

??? failure "イベントを購読しているのに、呼ばれない"
    受け取る側が GC に片付けられた可能性があります（`keepSubscriberReferenceAlive: false` の場合）。受け取る側のオブジェクトがどこかに保持されているか確かめます。ビューモデルは画面の `DataContext` が持っているので、普通は消えません。

??? failure "ダイアログが開かない"
    `RegisterDialog` を書き忘れているか、`ShowDialog` に渡した名前がビューの型名と違っています。

??? failure "`DialogCloseListener` が見つからない（`CS0246`）"
    使っている Prism のバージョンが 8 以前です。`Prism.DryIoc` を 9 以降に更新するか、Prism 8 用の書き方を調べてください。

次の章では、画面遷移の確認、ビューの寿命、コマンドの束ね方など、Prism をもう少し掘り下げます。

[第 24 章 Prism を掘り下げる](24-prism-deep.md) へ進みます。
