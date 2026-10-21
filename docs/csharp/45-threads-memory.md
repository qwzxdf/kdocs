---
title: 第 45 章 スレッド、メモリ、IDisposable
tags:
  - C#連携
---

# 第 45 章 スレッド、メモリ、IDisposable

ここまでの章で、スレッドとメモリに関する約束が、あちこちに散らばって出てきました。この章では、それらを<strong>1 か所にまとめて整理</strong>し、さらに<strong>長時間動かしたときの問題</strong>（メモリが増え続ける、終了時に固まる）の見つけ方と直し方を学びます。「動いた」から「安定して動き続ける」に進むための章です。

## この章の考え方

C# には GC があるので、メモリを気にしなくてよいと思われがちです。しかし、エディタのようなアプリでは、次の 4 つの問題が必ず起きます。

| 問題 | 原因 | 症状 |
| --- | --- | --- |
| <strong>管理されたメモリのリーク</strong> | 使い終わったオブジェクトを、どこかが<strong>参照し続ける</strong>（イベントの購読の解除忘れなど） | シーンを開き直すたびに、メモリが増える |
| <strong>ネイティブの資源のリーク</strong> | `Dispose` を呼ばない。GC は、ネイティブの資源の大きさを知らない | GPU メモリが減る。終了時にエンジンが壊れない |
| <strong>スレッドの競合</strong> | 複数のスレッドが、同じデータを同時に触る | まれにクラッシュ、値が化ける |
| <strong>終了時の固まり</strong> | スレッドが止まらない。ループが終わらない | プロセスが残り続ける |

## この章のゴール

- この教材のスレッドの約束を、表で言える。
- イベントの購読が原因のリークを、見つけて直せる。
- `IDisposable` を正しく実装できる。
- 長時間動かして、メモリが増えないことを確かめられる。

## スレッドの約束（まとめ）

この教材には、3 種類のスレッドが出てきました。

| スレッド | 役割 | 触ってよい物 |
| --- | --- | --- |
| <strong>UI スレッド</strong> | WPF の画面、ビューモデル、`SceneDocument`、`ObservableCollection` | 画面の部品、ドキュメント。<strong>エンジンは直接触らない</strong> |
| <strong>描画スレッド</strong>（`RenderLoop`） | `Engine` の作成、`Tick`、シーンの更新、破棄 | <strong>エンジンだけ</strong>。UI は触らない |
| <strong>スレッド プール</strong>（`Task.Run`） | ファイルの読み込み、サムネイルのデコード、`msbuild` の待ち | 自分のデータだけ。UI も、エンジンも直接は触らない |

### 受け渡しの方法

| 方向 | 方法 | 注意 |
| --- | --- | --- |
| UI → 描画 | `IRenderLoop.Post`（非同期）、`Invoke`（同期） | <strong>値をコピー</strong>してから渡す。UI の可変オブジェクトを、ラムダで捕まえない |
| 描画 → UI | <strong>ポーリング</strong>（UI のタイマーで読む）、または `Dispatcher.BeginInvoke` | 描画スレッドは UI を<strong>待たない</strong>（デッドロックの回避） |
| スレッド プール → UI | `await` で戻る（UI スレッドに戻る）、`Dispatcher.BeginInvoke` | `ConfigureAwait(false)` は、UI を触らない所だけ |
| ネイティブ → C# のコールバック | `[UnmanagedCallersOnly]` の関数。<strong>どのスレッドからでも呼ばれうる</strong> | 中で UI を触らない。`Dispatcher` に回す。例外を漏らさない |

### 守る規則のチェックリスト

- [ ] `Engine` の関数（`me_*`）は、<strong>描画スレッドからだけ</strong>呼ぶ（`IRenderLoop` を通す）。
- [ ] `ObservableCollection`、`SceneDocument`、ビューモデルは、<strong>UI スレッドだけ</strong>で変更する。
- [ ] 別のスレッドから UI を触るときは、`Dispatcher` を通す。
- [ ] 描画スレッドは、UI スレッドを<strong>待たない</strong>。
- [ ] `Post` に渡すラムダは、<strong>可変な共有データを捕まえない</strong>（値のコピーを使う）。
- [ ] ネイティブのコールバックの中で、<strong>例外を漏らさない</strong>。
- [ ] `Task` は、`await` するか、内部で `try/catch` する（`_ = …` で放置しない）。

## 手順 1：イベントの購読とリーク

C# の最も多いリークは、<strong>イベントの購読を外し忘れる</strong>ことです。

```csharp
public class PropertyViewModel
{
    public PropertyViewModel(ISelectionService selection)
    {
        selection.SelectionChanged += OnSelectionChanged;      // 購読
    }
}
```

`selection`（シングルトン）の `SelectionChanged` イベントは、`PropertyViewModel` への<strong>参照</strong>を持ちます。`PropertyViewModel` を使い終わっても、`selection` が生きている限り、GC は `PropertyViewModel` を回収できません。

```text
ISelectionService（アプリの間ずっと生きる）
 └─ SelectionChanged ─▶ PropertyViewModel#1（もう使わない）  ← 回収されない
                       ├▶ PropertyViewModel#2（もう使わない）
                       └▶ PropertyViewModel#3
```

画面を作り直すたびに、古いビューモデルが残って、<strong>メモリが増え</strong>、しかも古いビューモデルも<strong>イベントに反応し続ける</strong>（二重更新、無駄な処理）。

### 直し方

| 方法 | 内容 | 向いている場面 |
| --- | --- | --- |
| <strong>購読を解除する</strong>（`-=`） | `Dispose` や `Unloaded` で解除する | 基本。<strong>確実</strong> |
| <strong>弱いイベント</strong> | 購読者を弱い参照で持つ。購読者が不要になれば、GC が回収する | 解除のタイミングが分かりにくいとき |
| <strong>寿命をそろえる</strong> | 発行側と購読側が、同じ寿命なら、問題ない | サービスどうしなど |
| <strong>`IEventAggregator`</strong> | Prism のイベントは、既定で購読者を弱い参照で持つ（`keepSubscriberReferenceAlive: false`） | モジュール間の通知 |

### 購読の解除を、まとめて管理する

購読が多いビューモデルでは、解除を忘れがちです。<strong>購読を溜めて、`Dispose` で一括解除</strong>する小さな仕組みを作ります。

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

### 誰が `Dispose` を呼ぶのか

ビューモデルの `Dispose` は、誰が呼ぶのでしょうか。

| 作り方 | 呼ぶ人 |
| --- | --- |
| DI コンテナーが `Register` で作ったオブジェクト | コンテナーが、自分が破棄されるときに `IDisposable` なら `Dispose` する（アプリの終了時） |
| ビュー（`UserControl`）が作るビューモデル | ビューの `Unloaded` イベントで、`(DataContext as IDisposable)?.Dispose()` を呼ぶ |
| 自分で `new` した物 | 自分 |
| ダイアログのビューモデル | `OnDialogClosed()` の中で |

```csharp
// ビューのコードビハインド
Unloaded += (_, _) => (DataContext as IDisposable)?.Dispose();
```

## 手順 2：IDisposable を正しく実装する

`IDisposable` は、ネイティブの資源や購読を<strong>確実に手放す</strong>ための約束です。

### 管理された資源だけを持つ場合

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

### ネイティブの資源を直接持つ場合（避ける）

ネイティブのハンドル（`nint`）を直接持つと、ファイナライザーが必要になり、複雑です。

```csharp
// 標準的なパターン
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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Dispose(bool disposing)` | `true` は、利用者が `Dispose()` を呼んだ。`false` は、<strong>GC のファイナライザー</strong>から。ファイナライザーの中では、他の管理されたオブジェクトが、すでに回収された可能性があるので、触らない |
| `~NativeThing()` | <strong>ファイナライザー</strong>。GC が回収するとき、`Dispose` されていなければ呼ばれる。実行のタイミングは不定で、専用のスレッドで走る |
| `GC.SuppressFinalize(this)` | 明示的に `Dispose` されたので、ファイナライザーを呼ばなくてよいと GC に伝える |

!!! tip "SafeHandle を使えば、これを書かなくて済む"
    第 27 章で作った `EngineHandle`（`SafeHandle`）が、ここの複雑な部分を引き受けています。<strong>ネイティブのハンドルは、`SafeHandle` に包み、自分では、ファイナライザーを書かない</strong>のが、現代的な作法です。

## 手順 3：長時間動かしたときのメモリを調べる

メモリの増加は、<strong>見ないと気づきません</strong>。次の道具で見ます。

### Visual Studio の診断ツール

1. `Debug` で起動し、「<strong>デバッグ → ウィンドウ → 診断ツールの表示</strong>」（`Ctrl + Alt + F2`）。
2. 「<strong>メモリ使用量</strong>」タブで、「<strong>スナップショットの作成</strong>」を押す。
3. 操作を繰り返す（シーンを開く → 閉じる、を 10 回）。もう 1 度スナップショット。
4. 2 つを比較して、<strong>数が増えているオブジェクトの型</strong>を探す。`PropertyViewModel` が 10 個あれば、リーク。
5. 型をクリックし、「<strong>参照のパス</strong>」で、<strong>誰が参照しているか</strong>（GC ルートからの経路）を見る。

| 新しく出てきたもの | 説明 |
| --- | --- |
| スナップショット | その瞬間の、マネージド ヒープ全体の記録 |
| 差分 | 2 つのスナップショットの間で、増えた／減ったオブジェクト |
| GC ルート | GC が「生きている」と判断する出発点（スタック上の変数、静的フィールドなど） |
| 参照のパス | ルートから、そのオブジェクトまでの参照の連鎖。<strong>この連鎖のどこかを切れば</strong>、回収される |

### 簡易的な確認

```csharp
// 強制的に GC を走らせて、残っているメモリを見る（デバッグ用）
GC.Collect();
GC.WaitForPendingFinalizers();
GC.Collect();
long bytes = GC.GetTotalMemory(forceFullCollection: true);
_log.Info($"managed メモリ: {bytes / 1024 / 1024} MB");
```

通常のコードで `GC.Collect()` を呼ぶのは<strong>避けます</strong>（GC に任せる）。調査のためだけの使い方です。

### 弱い参照でリークを確かめる

```csharp
// 「破棄されたはずのオブジェクト」が、回収されたかを確かめる
var weak = new WeakReference(viewModel);
viewModel = null;
GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();
Debug.Assert(!weak.IsAlive, "リーク：viewModel が回収されていない");
```

`WeakReference` は、オブジェクトを<strong>回収させる</strong>参照です。回収後は `IsAlive` が `false` になります。リークの自動テストに使えます。

### ネイティブのリーク

C# の診断ツールは、ネイティブのメモリを見ません。

| 確かめること | 方法 |
| --- | --- |
| C++ のヒープのリーク | Debug ビルドで `_CrtDumpMemoryLeaks()` を終了時に呼ぶ。出力ウィンドウにリークが出る。`_CRTDBG_MAP_ALLOC` を定義して、場所の行番号を出す |
| DirectX のオブジェクトのリーク | DX12 の `IDXGIDebug1::ReportLiveObjects(DXGI_DEBUG_ALL, DXGI_DEBUG_RLO_ALL)` を、エンジンの終了時に呼ぶ。解放されていない COM オブジェクトが一覧に出る |
| GPU メモリ | タスク マネージャーの「パフォーマンス → GPU → 専用 GPU メモリ」。シーンを開き直して増え続けるなら、リーク |
| ハンドル（Win32 の HANDLE） | タスク マネージャーの「詳細」→ 列の選択 →「ハンドル」。増え続けるなら、リーク |

```cpp
// Engine の終了時（Renderer の破棄の後）
Microsoft::WRL::ComPtr<IDXGIDebug1> debug;
if (SUCCEEDED(DXGIGetDebugInterface1(0, IID_PPV_ARGS(&debug)))) {
  debug->ReportLiveObjects(DXGI_DEBUG_ALL, DXGI_DEBUG_RLO_FLAGS(DXGI_DEBUG_RLO_SUMMARY | DXGI_DEBUG_RLO_IGNORE_INTERNAL));
}
```

## 手順 4：終了処理の順序

終了時に固まる、またはクラッシュするのは、<strong>破棄の順序</strong>が原因のことがほとんどです。この教材のエディタが閉じられるときの、正しい順序です。

| 順 | 処理 | 担当 |
| --- | --- | --- |
| 1 | 未保存の確認（キャンセルされれば終了しない） | `MainWindow.OnClosing` |
| 2 | Play を止める | `IPlayModeService.Stop` |
| 3 | ファイル監視（`FileSystemWatcher`）を止める | `AssetService`、`GameService` の `Dispose` |
| 4 | <strong>描画ループを止め、エンジンを破棄する</strong> | `ViewportHost.DestroyWindowCore` → `HandleDestroying` → `RenderLoop.Stop` |
| 5 | ネイティブのログ コールバックを解除する | `NativeLog.Uninstall`（`OnExit`） |
| 6 | ファイル ログを閉じる | `FileLogWriter.Dispose` |
| 7 | DI コンテナーが、`IDisposable` なサービスを破棄する | Prism |
| 8 | プロセスの終了 | .NET |

<strong>4 を 5 より前に</strong>行うのが重要です。エンジンが生きている間に、コールバックを解除すると、エンジンのログが失われます。逆に、エンジンの破棄が終わった<strong>後</strong>に、ネイティブからコールバックが呼ばれる可能性は、ありません。

```csharp
protected override void OnExit(ExitEventArgs e)
{
    // 描画スレッドとエンジンは、ViewportHost の破棄ですでに止まっている。
    Interop.NativeLog.Uninstall();
    (Container.Resolve<FileLogWriter>() as IDisposable)?.Dispose();
    base.OnExit(e);
}
```

### 終了時に固まるとき

| 症状 | 調べること |
| --- | --- |
| プロセスが残る（タスク マネージャーに残る） | `IsBackground = false` のスレッドが、止まっていない。`Thread.Join` で待っている相手が、終わらない |
| 閉じるボタンで反応しない | UI スレッドで、`Invoke`（同期）を待っている。描画スレッドが、UI を待つ構造になっていないか |
| 終了時のクラッシュ | 破棄済みのオブジェクトを、別のスレッドが使っている。順序を見直す |

デバッガーで固まった時点に「<strong>すべて中断</strong>」を押し、「<strong>デバッグ → ウィンドウ → スレッド</strong>」「<strong>並列スタック</strong>」で、各スレッドが何を待っているかを見ます。

## 手順 5：安定性のテスト

「しばらく動かしておいて、問題ないか」を確かめる習慣をつけます。

| テスト | 手順 | 合格の基準 |
| --- | --- | --- |
| <strong>開閉の繰り返し</strong> | シーンを、新規・開くで、100 回入れ替える | メモリ（管理・ネイティブ・GPU）が、ほぼ一定 |
| <strong>Play の繰り返し</strong> | Play → Stop を 100 回 | 同上。物が元に戻る |
| <strong>ホット リロードの繰り返し</strong> | Game を 50 回、ビルドして差し替える | 同上。一時フォルダーのコピーが溜まらない |
| <strong>リサイズの繰り返し</strong> | ウィンドウの大きさを、速く動かし続ける | クラッシュしない。メモリが一定 |
| <strong>長時間の放置</strong> | 1 時間、Play したまま | メモリが一定。CPU が暴走しない |
| <strong>終了</strong> | 各状況で閉じる | 1 秒以内にプロセスが消える |

自動化できるものは、スクリプトにします（`UIAutomation` や、テスト用のコマンドライン引数で、同じ動作を内部から繰り返す）。

## 動作確認

| 操作 | 期待する結果 |
| --- | --- |
| シーンを新規 → 開く、を 20 回 | 診断ツールのスナップショット差分で、`SceneObject` や各ビューモデルが増えていない |
| ホット リロードを 20 回 | `%TEMP%\MiniEngine\<pid>\` のファイルが増え続けない |
| 閉じる | すぐにプロセスが消える。ログの最後の行が、ファイルに残っている |
| Debug 終了時 | DXGI の `ReportLiveObjects` に、解放漏れが出ない |

## よくあるミス

??? failure "ビューが閉じられても、ビューモデルが生き続けている"
    ビューモデルが、シングルトンのサービスのイベントを購読している。`Dispose` で解除する。Prism の `IEventAggregator` を使えば、既定で弱い参照。

??? failure "`Dispose` を呼んだのに、まだ GPU のメモリが減らない"
    GPU のオブジェクトは、<strong>コマンドが完了するまで</strong>解放されない。`WaitForGpu` してから解放する（第 3 章）。デスクリプター ヒープなど、他からの参照が残っていないか確認する。

??? failure "ファイナライザーのスレッドで、例外が出て落ちる"
    ファイナライザーの中で、他のオブジェクト（すでに回収済み）を触っている。`Dispose(false)` の中では、管理された資源に触らない。

??? failure "`Dispatcher.Invoke` の呼び出しで、終了時にデッドロック"
    終了処理の途中で、UI スレッドが閉じられ、`Invoke` が戻らなくなる。終了時に UI へ回すのは、`BeginInvoke`（待たない）にする。または、終了フラグを見て、何もしない。

??? failure "メモリは安定しているのに、ハンドル数が増える"
    ファイルのストリーム、`FileSystemWatcher`、`Process` を `Dispose` していない。`using` で包む。

## 第 6 部のまとめ

| 章 | 作ったもの |
| --- | --- |
| 第 41 章 | ゲーム DLL のインターフェース（純粋仮想クラス、版の照合） |
| 第 42 章 | ホット リロード（シャドウ コピー、状態の引き継ぎ、失敗時の維持） |
| 第 43 章 | Play モード（ドキュメントは変えず、Stop で作り直す） |
| 第 44 章 | ログとエラー処理（3 つの捕捉場所、ファイル ログ、ダンプ） |
| 第 45 章 | スレッドとメモリ（約束の整理、リーク、`IDisposable`、終了の順序） |

## この章のまとめ

- スレッドの約束は、「<strong>エンジンは描画スレッドだけ、UI は UI スレッドだけ</strong>」。受け渡しは、値のコピーで。
- C# のリークの主犯は、<strong>イベントの購読の解除忘れ</strong>。解除する、または弱い参照にする。
- ネイティブの資源は `SafeHandle` に任せ、自分でファイナライザーを書かない。
- メモリは、<strong>診断ツールで見る</strong>。安定性は、繰り返しテストで確かめる。
- 破棄は、<strong>依存の逆順</strong>に行う。

## 次の章へ

次の章（[第 46 章 ビルド、テスト、配布](46-build-deploy.md)）では、このエディタを<strong>ほかの人に渡せる形</strong>にします。リリース ビルド、配布のフォルダー構成、ビルドの自動化、ビューモデルのテストを扱います。
