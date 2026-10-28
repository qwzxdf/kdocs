---
title: 第 45 章 スレッド、メモリ、IDisposable
tags:
  - C#連携
---

# 第 45 章 スレッド、メモリ、IDisposable

ここまでの章で、スレッドとメモリに関する約束があちこちに散らばって出てきました。この章では、それらを 1 か所にまとめて整理します。さらに、長時間動かしたときの問題（メモリが増え続ける、終了時に固まる）の見つけ方と直し方を学びます。「動いた」から「安定して動き続ける」へ進むための章です。

## 起きる問題は 4 つ

C# には GC があるので、メモリを気にしなくてよいと思われがちです。しかし、エディタのようなアプリでは、次の 4 つの問題が必ず起きます。

| 問題 | 原因 | 症状 |
| --- | --- | --- |
| 管理されたメモリのリーク | 使い終わったオブジェクトをどこかが参照し続ける（イベントの購読の解除忘れなど） | シーンを開き直すたびに、メモリが増える |
| ネイティブの資源のリーク | `Dispose` を呼ばない。GC は、ネイティブの資源の大きさを知らない | GPU メモリが減る。終了時にエンジンが壊れない |
| スレッドの競合 | 複数のスレッドが同じデータを同時に触る | まれにクラッシュ、値が化ける |
| 終了時の固まり | スレッドが止まらない。ループが終わらない | プロセスが残り続ける |

この章のゴールは次のとおりです。

- この教材のスレッドの約束を表で言える。
- イベントの購読が原因のリークを見つけて直せる。
- `IDisposable` を正しく実装できる。
- 長時間動かして、メモリが増えないことを確かめられる。

## スレッドの約束（まとめ）

この教材には、3 種類のスレッドが出てきました。

| スレッド | 役割 | 触ってよい物 |
| --- | --- | --- |
| UI スレッド | WPF の画面、ビューモデル、`SceneDocument`、`ObservableCollection` | 画面の部品、ドキュメント。エンジンは直接触らない |
| 描画スレッド（`RenderLoop`） | `Engine` の作成、`Tick`、シーンの更新、破棄 | エンジンだけ。UI は触らない |
| スレッド プール（`Task.Run`） | ファイルの読み込み、サムネイルのデコード、`msbuild` の待ち | 自分のデータだけ。UI もエンジンも直接は触らない |

スレッドをまたぐ受け渡しの方法も、決まっています。

| 方向 | 方法 | 注意 |
| --- | --- | --- |
| UI → 描画 | `IRenderLoop.Post`（非同期）、`Invoke`（同期） | 値をコピーしてから渡す。UI の可変オブジェクトをラムダで捕まえない |
| 描画 → UI | ポーリング（UI のタイマーで読む）、または `Dispatcher.BeginInvoke` | 描画スレッドは UI を待たない（デッドロックの回避） |
| スレッド プール → UI | `await` で戻る（UI スレッドに戻る）、`Dispatcher.BeginInvoke` | `ConfigureAwait(false)` は、UI を触らない所だけ |
| ネイティブ → C# のコールバック | `[UnmanagedCallersOnly]` の関数。どのスレッドからでも呼ばれうる | 中で UI を触らない。`Dispatcher` に回す。例外を漏らさない |

守る規則をチェックリストにします。

- [ ] `Engine` の関数（`me_*`）は、描画スレッドからだけ呼ぶ（`IRenderLoop` を通す）。
- [ ] `ObservableCollection`、`SceneDocument`、ビューモデルは、UI スレッドだけで変更する。
- [ ] 別のスレッドから UI を触るときは、`Dispatcher` を通す。
- [ ] 描画スレッドは、UI スレッドを待たない。
- [ ] `Post` に渡すラムダは、可変な共有データを捕まえない（値のコピーを使う）。
- [ ] ネイティブのコールバックの中で、例外を漏らさない。
- [ ] `Task` は、`await` するか、内部で `try/catch` する（`_ = …` で放置しない）。

## イベントの購読とリーク

C# で最も多いリークは、イベントの購読を外し忘れることです。

```csharp
public class PropertyViewModel
{
    public PropertyViewModel(ISelectionService selection)
    {
        selection.SelectionChanged += OnSelectionChanged;      // 購読
    }
}
```

シングルトンの `selection` が持つ `SelectionChanged` イベントは、購読した `PropertyViewModel` への参照を持ちます。`PropertyViewModel` を使い終わっても、`selection` が生きている限り、GC は `PropertyViewModel` を回収できません。

```text
ISelectionService（アプリの間ずっと生きる）
 └─ SelectionChanged ─▶ PropertyViewModel#1（もう使わない）  ← 回収されない
                       ├▶ PropertyViewModel#2（もう使わない）
                       └▶ PropertyViewModel#3
```

画面を作り直すたびに、古いビューモデルが残ってメモリが増えます。しかも古いビューモデルがイベントに反応し続けるので、二重更新や無駄な処理も起きます。

直し方は、いくつかあります。

| 方法 | 内容 | 向いている場面 |
| --- | --- | --- |
| 購読を解除する（`-=`） | `Dispose` や `Unloaded` で解除する | 基本。確実 |
| 弱いイベント | 購読者を弱い参照で持つ。購読者が不要になれば、GC が回収する | 解除のタイミングが分かりにくいとき |
| 寿命をそろえる | 発行側と購読側が同じ寿命なら、問題ない | サービスどうしなど |
| `IEventAggregator` | Prism のイベントは、既定で購読者を弱い参照で持つ（`keepSubscriberReferenceAlive: false`） | モジュール間の通知 |

### 弱いイベントの書き方（WeakEventManager）

解除のタイミングが分かりにくいときは、WPF が用意している `WeakEventManager` を使います。通常の `+=` では、発行側が購読者への強い参照を持ちます。`WeakEventManager` は、間に仲介役を挟んで、発行側から購読者への参照を弱い参照にします。

```csharp
// 通常の購読（発行側が購読者を強く参照する）
source.Changed += OnChanged;

// 弱い購読（購読者が不要になれば、GC が回収できる）
WeakEventManager<SceneDocument, EventArgs>.AddHandler(source, nameof(SceneDocument.Changed), OnChanged);

// 解除したいときは RemoveHandler。ただし、忘れても致命的ではない
WeakEventManager<SceneDocument, EventArgs>.RemoveHandler(source, nameof(SceneDocument.Changed), OnChanged);
```

型引数は、発行側の型とイベント引数の型です。イベント名は、文字列で渡します。イベントの型が `EventHandler<TEventArgs>` か、`EventArgs` から派生した引数を持つ `EventHandler` のときに使えます。

`INotifyPropertyChanged` の `PropertyChanged` には、専用の `PropertyChangedEventManager` があります。

```csharp
PropertyChangedEventManager.AddHandler(source, OnSourcePropertyChanged, nameof(Source.Name));
```

弱いイベントには、次の注意点があります。

- ラムダ式は渡さないでください。ラムダは、どこからも参照されないため、すぐに GC に回収されて、通知が届かなくなります。`OnChanged` のような名前付きのメソッドを渡します。
- 解除が不要になるのは、「メモリが残る」問題だけです。購読者が回収されるまでは、通知が届き続けます。購読者が `Dispose` された後に反応してほしくないなら、やはり明示的に解除してください。

購読が多いビューモデルでは、解除を忘れがちです。購読解除の処理を溜めておいて、`Dispose` で一括解除する、小さな仕組みを作ります。

```csharp
namespace Editor.Infrastructure;

// 購読解除の処理を溜めておき、Dispose でまとめて実行する
public sealed class SubscriptionBag : IDisposable
{
    private readonly List<Action> _unsubscribers = new();

    public void Add(Action unsubscribe) => _unsubscribers.Add(unsubscribe);

    public void Dispose()
    {
        foreach (var unsubscribe in _unsubscribers) unsubscribe();
        _unsubscribers.Clear();
    }
}
```

```csharp
public class PropertyViewModel : BindableBase, IDisposable
{
    private readonly SubscriptionBag _subscriptions = new();

    public PropertyViewModel(ISelectionService selection)
    {
        selection.SelectionChanged += OnSelectionChanged;
        _subscriptions.Add(() => selection.SelectionChanged -= OnSelectionChanged);
    }

    public void Dispose() => _subscriptions.Dispose();
}
```

購読を始める行の隣に解除を登録する行を書きます。ペアで書く習慣にすれば、忘れません。

では、`Dispose` は誰が呼ぶのでしょうか。

| 作り方 | 呼ぶ人 |
| --- | --- |
| DI コンテナーが `Register` で作ったオブジェクト | コンテナーが自分が破棄されるときに `IDisposable` なら `Dispose` する（アプリの終了時） |
| ビュー（`UserControl`）が作るビューモデル | ビューの `Unloaded` イベントで、`(DataContext as IDisposable)?.Dispose()` を呼ぶ |
| 自分で `new` した物 | 自分 |
| ダイアログのビューモデル | `OnDialogClosed()` の中で |

```csharp
// ビューのコードビハインド
Unloaded += (_, _) => (DataContext as IDisposable)?.Dispose();
```

## IDisposable を正しく実装する

`IDisposable` は、ネイティブの資源や購読を確実に手放すための約束です。管理された資源だけを持つ場合は、単純です。

```csharp
public sealed class RenderLoop : IRenderLoop
{
    private bool _disposed;

    public void Dispose()
    {
        if (_disposed) return;                // 二重に呼ばれても安全に
        _disposed = true;
        Stop();                                // スレッドを止める
    }
}
```

ネイティブのハンドル（`nint`）を直接持つと、ファイナライザーが必要になり、複雑になります。標準的なパターンを示しますが、避けられるなら避けるべき形です。

```csharp
public class NativeThing : IDisposable
{
    private nint _handle;
    private bool _disposed;

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);             // ファイナライザーは、もう不要
    }

    protected virtual void Dispose(bool disposing)
    {
        if (_disposed) return;
        if (disposing)
        {
            // 管理された資源を解放する（他の IDisposable の Dispose など）
        }
        // ネイティブの資源は、disposing に関係なく、必ず解放する
        if (_handle != nint.Zero) { Free(_handle); _handle = nint.Zero; }
        _disposed = true;
    }

    ~NativeThing() => Dispose(false);          // Dispose を呼び忘れた場合の最後の砦
}
```

`Dispose(bool disposing)` の引数 `true` は、利用者が `Dispose()` を呼んだ場合で、`false` は GC のファイナライザーから呼ばれた場合です。ファイナライザーの中では、他の管理されたオブジェクトがすでに回収された可能性があるので、触ってはいけません。`~NativeThing()` がそのファイナライザーで、GC が回収するときに `Dispose` されていなければ呼ばれます。タイミングは不定で、専用のスレッドで走ります。`GC.SuppressFinalize(this)` は、明示的に `Dispose` されたので、ファイナライザーはもう要らないと GC に伝えます。

!!! tip "SafeHandle を使えば、これを書かなくて済む"
    第 27 章で作った `EngineHandle`（`SafeHandle`）がこの複雑な部分を引き受けています。ネイティブのハンドルは `SafeHandle` に包んで、自分ではファイナライザーを書かないのが、現代的な作法です。

!!! info "このページを読む前に"
    - [第 44 章 ログとエラー処理](44-logging-errors.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）

## 長時間動かしたときのメモリを調べる

メモリの増加は、見ないと気づきません。道具を使って見ます。

### Visual Studio の診断ツール

1. `Debug` で起動して、「デバッグ → ウィンドウ → 診断ツールの表示」（`Ctrl + Alt + F2`）を開く。
2. 「メモリ使用量」タブで、「スナップショットの作成」を押す。
3. 操作を繰り返す（シーンを開く → 閉じる、を 10 回）。もう 1 度スナップショットを取る。
4. 2 つを比較して、数が増えているオブジェクトの型を探す。`PropertyViewModel` が 10 個あれば、リーク。
5. 型をクリックして、「参照のパス」で、誰が参照しているか（GC ルートからの経路）を見る。

スナップショットは、その瞬間のマネージド ヒープ全体の記録で、差分を見ると、間に増えたオブジェクトが分かります。GC ルート（スタック上の変数、静的フィールドなど）は、GC が「生きている」と判断する出発点です。参照のパスは、ルートからそのオブジェクトまでの参照の連鎖なので、この連鎖のどこかを切れば、回収されます。

簡易的には、コードで確認する手もあります。

```csharp
// 強制的に GC を走らせて、残っているメモリを見る（デバッグ用）
GC.Collect();
GC.WaitForPendingFinalizers();
GC.Collect();
long bytes = GC.GetTotalMemory(forceFullCollection: true);
_log.Info($"managed メモリ: {bytes / 1024 / 1024} MB");
```

通常のコードで `GC.Collect()` を呼ぶのは避けます（GC に任せます）。調査のためだけの使い方です。

「破棄されたはずのオブジェクトが回収されたか」は、弱い参照で確かめられます。

```csharp
var weak = new WeakReference(viewModel);
viewModel = null;
GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();
Debug.Assert(!weak.IsAlive, "リーク：viewModel が回収されていない");
```

`WeakReference` は、オブジェクトを回収させる参照です。回収後は `IsAlive` が `false` になります。リークの自動テストに使えます。

### ネイティブのリーク

C# の診断ツールは、ネイティブのメモリを見ません。別の方法で確かめます。

| 確かめること | 方法 |
| --- | --- |
| C++ のヒープのリーク | Debug ビルドで `_CrtDumpMemoryLeaks()` を終了時に呼ぶ。出力ウィンドウにリークが出る。`_CRTDBG_MAP_ALLOC` を定義すると、場所の行番号が出る |
| DirectX のオブジェクトのリーク | DX12 の `IDXGIDebug1::ReportLiveObjects(DXGI_DEBUG_ALL, DXGI_DEBUG_RLO_ALL)` をエンジンの終了時に呼ぶ。解放されていない COM オブジェクトが一覧に出る |
| GPU メモリ | タスク マネージャーの「パフォーマンス → GPU → 専用 GPU メモリ」。シーンを開き直して増え続けるなら、リーク |
| ハンドル（Win32 の HANDLE） | タスク マネージャーの「詳細」→ 列の選択 →「ハンドル」。増え続けるなら、リーク |

```cpp
// Engine の終了時（Renderer の破棄の後）
Microsoft::WRL::ComPtr<IDXGIDebug1> debug;
if (SUCCEEDED(DXGIGetDebugInterface1(0, IID_PPV_ARGS(&debug)))) {
  debug->ReportLiveObjects(DXGI_DEBUG_ALL, DXGI_DEBUG_RLO_FLAGS(DXGI_DEBUG_RLO_SUMMARY | DXGI_DEBUG_RLO_IGNORE_INTERNAL));
}
```

## 終了処理の順序

終了時に固まる、またはクラッシュするのは、破棄の順序が原因のことがほとんどです。このエディタが閉じられるときの、正しい順序を表にします。

| 順 | 処理 | 担当 |
| --- | --- | --- |
| 1 | 未保存の確認（キャンセルされれば終了しない） | `MainWindow.OnClosing` |
| 2 | Play を止める | `IPlayModeService.Stop` |
| 3 | ファイル監視（`FileSystemWatcher`）を止める | `AssetService`、`GameService` の `Dispose` |
| 4 | 描画ループを止め、エンジンを破棄する | `ViewportHost.DestroyWindowCore` → `HandleDestroying` → `RenderLoop.Stop` |
| 5 | ネイティブのログ コールバックを解除する | `NativeLog.Uninstall`（`OnExit`） |
| 6 | ファイル ログを閉じる | `FileLogWriter.Dispose` |
| 7 | DI コンテナーが `IDisposable` なサービスを破棄する | Prism |
| 8 | プロセスの終了 | .NET |

4 を 5 より前にするのが重要です。エンジンが生きている間にコールバックを解除すると、エンジンのログが失われます。逆に、エンジンの破棄が終わったあとで、ネイティブからコールバックが呼ばれる可能性はありません。

```csharp
protected override void OnExit(ExitEventArgs e)
{
    // 描画スレッドとエンジンは、ViewportHost の破棄ですでに止まっている。
    Interop.NativeLog.Uninstall();
    (Container.Resolve<FileLogWriter>() as IDisposable)?.Dispose();
    base.OnExit(e);
}
```

終了時に固まるときは、次の表で原因を探します。

| 症状 | 調べること |
| --- | --- |
| プロセスが残る（タスク マネージャーに残る） | `IsBackground = false` のスレッドが止まっていない。`Thread.Join` で待っている相手が終わらない |
| 閉じるボタンで反応しない | UI スレッドで `Invoke`（同期）を待っている。描画スレッドが UI を待つ構造になっていないか |
| 終了時のクラッシュ | 破棄済みのオブジェクトを別のスレッドが使っている。順序を見直す |

デバッガーで固まった時点に「すべて中断」を押して、「デバッグ → ウィンドウ → スレッド」と「並列スタック」で、各スレッドが何を待っているかを見ます。

## 安定性のテスト

「しばらく動かしておいて、問題ないか」を確かめる習慣をつけます。

| テスト | 手順 | 合格の基準 |
| --- | --- | --- |
| 開閉の繰り返し | シーンを新規・開くで 100 回入れ替える | メモリ（管理・ネイティブ・GPU）がほぼ一定 |
| Play の繰り返し | Play → Stop を 100 回 | 同上。物が元に戻る |
| ホット リロードの繰り返し | Game を 50 回、ビルドして差し替える | 同上。一時フォルダーのコピーが溜まらない |
| リサイズの繰り返し | ウィンドウの大きさを速く動かし続ける | クラッシュしない。メモリが一定 |
| 長時間の放置 | 1 時間、Play したまま | メモリが一定。CPU が暴走しない |
| 終了 | 各状況で閉じる | 1 秒以内にプロセスが消える |

自動化できるものは、スクリプトにします（`UIAutomation` や、テスト用のコマンドライン引数で、同じ動作を内部から繰り返します）。

| 操作 | 期待する結果 |
| --- | --- |
| シーンを新規 → 開く、を 20 回 | 診断ツールのスナップショット差分で、`SceneObject` や各ビューモデルが増えていない |
| ホット リロードを 20 回 | `%TEMP%\MiniEngine\<pid>\` のファイルが増え続けない |
| 閉じる | すぐにプロセスが消える。ログの最後の行がファイルに残っている |
| Debug 終了時 | DXGI の `ReportLiveObjects` に、解放漏れが出ない |

??? failure "ビューが閉じられても、ビューモデルが生き続けている"
    ビューモデルがシングルトンのサービスのイベントを購読しています。`Dispose` で解除します。Prism の `IEventAggregator` を使えば、既定で弱い参照です。

??? failure "`Dispose` を呼んだのに、まだ GPU のメモリが減らない"
    GPU のオブジェクトは、コマンドが完了するまで解放されません。`WaitForGpu` してから解放します（第 3 章）。デスクリプター ヒープなど、他からの参照が残っていないかも確認します。

??? failure "ファイナライザーのスレッドで、例外が出て落ちる"
    ファイナライザーの中で、他のオブジェクト（すでに回収済み）を触っています。`Dispose(false)` の中では、管理された資源に触りません。

??? failure "`Dispatcher.Invoke` の呼び出しで、終了時にデッドロック"
    終了処理の途中で UI スレッドが閉じられ、`Invoke` が戻らなくなります。終了時に UI へ回すのは `BeginInvoke`（待たない）にします。または、終了フラグを見て何もしません。

??? failure "メモリは安定しているのに、ハンドル数が増える"
    ファイルのストリーム、`FileSystemWatcher`、`Process` を `Dispose` していません。`using` で包みます。

## 第 6 部のまとめ

| 章 | 作ったもの |
| --- | --- |
| 第 41 章 | ゲーム DLL のインターフェース（純粋仮想クラス、版の照合） |
| 第 42 章 | ホット リロード（シャドウ コピー、状態の引き継ぎ、失敗時の維持） |
| 第 43 章 | Play モード（ドキュメントは変えず、Stop で作り直す） |
| 第 44 章 | ログとエラー処理（3 つの捕捉場所、ファイル ログ、ダンプ） |
| 第 45 章 | スレッドとメモリ（約束の整理、リーク、`IDisposable`、終了の順序） |

## この章のまとめ

- スレッドの約束は、「エンジンは描画スレッドだけ、UI は UI スレッドだけ」。受け渡しは、値のコピーで。
- C# のリークの主犯は、イベントの購読の解除忘れ。解除するか、弱い参照にする。
- ネイティブの資源は `SafeHandle` に任せて、自分でファイナライザーを書かない。
- メモリは、診断ツールで見る。安定性は、繰り返しテストで確かめる。
- 破棄は、依存の逆順に行う。

次の章では、このエディタをほかの人に渡せる形にします。

[第 46 章 ビルド、テスト、配布](46-build-deploy.md) へ進みます。
