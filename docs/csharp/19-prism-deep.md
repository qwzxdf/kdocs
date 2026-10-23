---
title: 第 19 章 Prism を掘り下げる
tags:
  - C#連携
---

# 第 19 章 Prism を掘り下げる

本編の第 16〜18 章では、Prism の中でもよく使う部分を一通り扱いました。実際に画面遷移や複数の画面を作り込むと、「前に見ていた画面の状態が残ってしまう」「未保存なのに別の画面へ移ってしまう」「全部のモジュールを最初に読み込むと起動が遅い」といった問題が出てきます。この章では、そういう場面で使う Prism の機能をまとめます。

!!! info "このページを読む前に"
    - [第 18 章 イベント集約、ダイアログ、サービス](18-events-dialogs.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


Prism は、バージョンによって細かな API が変わります。ここに書いたコードがそのままコンパイルできないときは、使っているバージョンの公式ドキュメントと見比べてください。この章は Prism 9 を前提にしています。

## ナビゲーションで切り替えたビューは残る

第 17 章の `RequestNavigate` で切り替えたビューは、リージョンから外れずに残り続けます（非表示になっているだけ）。同じ画面に戻ってくると、新しく作られるのではなく、前に使っていたものが再び出てきます。

これが都合のよいこともあります（入力途中の内容が残る）が、都合の悪いこともあります（データが古いまま残る）。

### 残すかどうか決める：IRegionMemberLifetime

ビューまたはビューモデルに `IRegionMemberLifetime` を実装し、`KeepAlive` を返します。

```csharp
public class SettingsViewModel : BindableBase, IRegionMemberLifetime
{
    public bool KeepAlive => false;     // 切り替えたら、リージョンから外して捨てる
}
```

`false` を返すと、別の画面に移ったときにビューが破棄されます。戻ってきたときは、毎回新しく作られます。属性で書くこともできます。

```csharp
[RegionMemberLifetime(KeepAlive = false)]
public class SettingsViewModel : BindableBase { }
```

### 既存のビューを使い回すか決める：IsNavigationTarget

`INavigationAware.IsNavigationTarget` は、「今の移動先として、この既存のビューでよいか」を答えます（第 17 章）。たとえば、物の詳細画面を、物ごとに別のビューにしたいなら、渡されたパラメーターを見て判定します。

```csharp
public bool IsNavigationTarget(NavigationContext context)
{
    var id = context.Parameters.GetValue<int>("ObjectId");
    return id == _currentId;     // 同じ物の画面なら使い回し、違えば新しく作る
}
```

## 移動の前に確認する：IConfirmNavigationRequest

未保存の編集があるのに、別の画面に移動しようとしたときに、確認を出したい。そのときは `IConfirmNavigationRequest` を実装します。`INavigationAware` に、`ConfirmNavigationRequest` が加わったものです。

```csharp
public class EditorViewModel : BindableBase, IConfirmNavigationRequest
{
    public void ConfirmNavigationRequest(NavigationContext navigationContext, Action<bool> continuationCallback)
    {
        if (!HasUnsavedChanges)
        {
            continuationCallback(true);           // 移動してよい
            return;
        }
        // 確認する（ここでは、あとで非同期に答える例）
        var result = _messages.AskSave("編集中のデータ");
        continuationCallback(result != SaveChoice.Cancel);   // false を渡すと、移動が取り消される
    }

    // OnNavigatedTo / OnNavigatedFrom / IsNavigationTarget も実装する
}
```

`continuationCallback(true)` を呼ぶと移動が続き、`false` なら取り消されます。ダイアログのように答えを待つ処理がある場合は、答えが出てから、コールバックを呼べます。

移動の結果は、`RequestNavigate` のコールバックで受け取れます。

```csharp
_regionManager.RequestNavigate(RegionNames.Property, "SettingsView", result =>
{
    if (result.Result == false)
    {
        // 移動できなかった（確認でキャンセルされた、ビューが見つからない、など）
        _log.Warning($"移動に失敗: {result.Error?.Message}");
    }
});
```

### 戻る・進む（ナビゲーション ジャーナル）

`NavigationContext` から、ジャーナル（履歴）を使えます。

```csharp
public void OnNavigatedTo(NavigationContext navigationContext)
{
    _journal = navigationContext.NavigationService.Journal;
}

private void GoBack()
{
    if (_journal?.CanGoBack == true) _journal.GoBack();
}
```

ジャーナルを使うと、ウィザードのような「戻る」ボタンを作れます。

## リージョンの文脈を渡す：RegionContext

リージョンの中のビューに、リージョンを置いた側から値を渡したいときは、`RegionContext` を使います。親の画面に、次のように書きます。

```xml
<ContentControl prism:RegionManager.RegionName="DetailRegion"
                prism:RegionManager.RegionContext="{Binding SelectedItem}" />
```

リージョンの中のビュー側は、`RegionContext` を受け取れます。ナビゲーションのパラメーターよりも、「今選ばれている物を、そのまま下の画面に渡す」ような関係に向いています。

## コマンドを束ねる：CompositeCommand

「すべて保存」のように、複数のビューモデルのコマンドを、一度に呼びたいときは `CompositeCommand` を使います。

```csharp
// 共有の場所（サービスなど）に 1 つだけ作る
public interface IApplicationCommands
{
    CompositeCommand SaveAllCommand { get; }
}

public class ApplicationCommands : IApplicationCommands
{
    public CompositeCommand SaveAllCommand { get; } = new CompositeCommand();
}
```

```csharp
// 各ビューモデルが、自分の保存コマンドを登録する
public EditorViewModel(IApplicationCommands appCommands)
{
    SaveCommand = new DelegateCommand(Save);
    appCommands.SaveAllCommand.RegisterCommand(SaveCommand);
}
```

メニューの「すべて保存」は `SaveAllCommand` にバインドします。押すと、登録された全部の `SaveCommand` が呼ばれます。登録された中に 1 つでも実行できないコマンドがあると、全体の `CanExecute` が `false` になります。

「今画面に出ているビューのコマンドだけを呼びたい」場合は、ビューモデルに `IActiveAware` を実装して、アクティブな間だけ有効にできます（`CompositeCommand` の `monitorCommandActivity` を `true` にします）。

## モジュールを必要になるまで読み込まない

第 17 章では、`AddModule<T>()` で、すべてのモジュールを起動時に読み込みました。数が増えると、起動が遅くなります。使うまで読み込まないモジュールは、オンデマンドにできます。

```csharp
protected override void ConfigureModuleCatalog(IModuleCatalog moduleCatalog)
{
    moduleCatalog.AddModule<SceneTreeModule>();                                   // 起動時
    moduleCatalog.AddModule<AssetModule>(InitializationMode.OnDemand);            // 必要になったとき
}
```

必要になったところで、`IModuleManager` から読み込みます。

```csharp
public MainWindowViewModel(IModuleManager moduleManager)
{
    ShowAssetsCommand = new DelegateCommand(() => moduleManager.LoadModule(nameof(AssetModule)));
}
```

モジュールの名前は、クラス名（`AssetModule`）が既定で使われます。`[Module(ModuleName = "Asset")]` で付け替えられます。

### 別の DLL にあるモジュール

モジュールを別の C# プロジェクトに分けた場合、その DLL を実行ファイルと同じフォルダーに置いて、フォルダーを探索して読み込む方式もあります。

```csharp
protected override IModuleCatalog CreateModuleCatalog()
{
    return new DirectoryModuleCatalog { ModulePath = @".\Modules" };
}
```

フォルダー内の DLL から `IModule` を実装したクラスを探して、自動で登録します。アプリを再ビルドせずに、DLL を足すだけで機能を増やす（プラグインのような）構成に使えます。

## ダイアログの掘り下げ

### 自作のウィンドウを使う

既定のダイアログ ウィンドウの見た目（枠、タイトル バー、アイコン）を変えたいときは、`IDialogWindow` を実装した自作の `Window` を登録します。

```csharp
public partial class MyDialogWindow : Window, IDialogWindow
{
    public IDialogResult? Result { get; set; }

    public MyDialogWindow()
    {
        InitializeComponent();
    }
}
```

```csharp
containerRegistry.RegisterDialogWindow<MyDialogWindow>();
```

`IDialogWindow` には、`Content`、`DataContext`、`Owner`、`Show()` / `ShowDialog()`、`Closed` などのメンバーがありますが、`Window` がすでに持っているので、`Result` を足せば、満たせます。

### Show と ShowDialog

| メソッド | 動き |
| --- | --- |
| `ShowDialog` | モーダル（閉じるまで親を操作できない）で開く |
| `Show` | モードレス（親も操作できる）で開く |

ツール ウィンドウのように、開いたまま本体も操作したいなら `Show` を使います。

### ダイアログの閉じ方のパターン

`RequestClose.Invoke(...)` には、使い分けられる形がいくつかあります。

```csharp
RequestClose.Invoke();                                        // 結果なし
RequestClose.Invoke(ButtonResult.OK);                         // 結果だけ
RequestClose.Invoke(new DialogParameters { { "Name", name } }); // 値だけ
RequestClose.Invoke(new DialogParameters { { "Name", name } }, ButtonResult.OK);   // 両方
```

呼び出し側は、コールバックの `result.Parameters` から値を取り出せます。

## 入力の検証の補助：ErrorsContainer

`INotifyDataErrorInfo`（第 13 章）を実装するとき、エラーの一覧を管理する `ErrorsContainer<T>` が Prism に用意されています。自分で `Dictionary` を作らなくても済みます。

```csharp
private readonly ErrorsContainer<string> _errors;

public PlayerViewModel()
{
    _errors = new ErrorsContainer<string>(name => ErrorsChanged?.Invoke(this, new DataErrorsChangedEventArgs(name)));
}

public IEnumerable GetErrors(string? propertyName) => _errors.GetErrors(propertyName);
public bool HasErrors => _errors.HasErrors;
```

エラーを設定するときは `_errors.SetErrors(nameof(Hp), new[] { "0 以上にしてください" })` です。

## ViewModelLocator の動きを変える

規則に合わないビューとビューモデルを結びつけたい、あるいは規則そのものを変えたいときは、`ViewModelLocationProvider` を使います。

```csharp
protected override void ConfigureViewModelLocator()
{
    base.ConfigureViewModelLocator();

    // 規則を変える：Views.Xxx → ViewModels.XxxVM
    ViewModelLocationProvider.SetDefaultViewTypeToViewModelTypeResolver(viewType =>
    {
        var name = viewType.FullName!.Replace(".Views.", ".ViewModels.") + "VM";
        return Type.GetType(name);
    });

    // 個別に結び付ける
    ViewModelLocationProvider.Register<MainWindow, MainWindowViewModel>();
}
```

普段は、既定の規則のまま使うので、触る機会は多くありません。

## バージョンの違いに注意

Prism 7 以前の日本語の記事は、まだたくさん残っています。読むときは、次のあたりに差があります。

| 項目 | 古い記事（6〜7） | Prism 8〜9 |
| --- | --- | --- |
| 起動 | `Bootstrapper` クラス | `PrismApplication` |
| DI コンテナー | Unity が既定 | DryIoc が主流（Unity は別パッケージ） |
| DI コンテナーの操作 | `Container.RegisterType<...>()` | `IContainerRegistry` / `IContainerProvider` |
| プロパティ注入 | `[Dependency]` 属性 | 使えない（コンストラクター注入のみ） |
| ダイアログ | `InteractionRequest`（独自の仕組み） | `IDialogService` |
| ダイアログの名前空間 | （なし） | 8 は `Prism.Services.Dialogs`、9 は `Prism.Dialogs` |
| `IDialogAware.Title` | （なし） | 8 まではあり、9 はなし |
| `RequestClose` | （なし） | 8 はイベント、9 は `DialogCloseListener` |

古い記事を参考にするときは、「概念」は今も通じるので、そのまま読んで構いません。コードは、上の表にあるような違いを意識しながら読み替えます。

次の章では、Prism の `BindableBase` と、CommunityToolkit.Mvvm などの他のライブラリを書き比べます。

[第 20 章 MVVM ライブラリを比べる](20-mvvm-libraries.md) へ進みます。
