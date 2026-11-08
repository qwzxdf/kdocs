---
title: 第 57 章 落ちたら立て直す
tags:
  - C#連携
---

# 第 57 章 落ちたら立て直す

エンジンを別プロセスにした目的はエンジンが落ちても、エディタが生きていることでした。生きているだけではまだ半分です。ビューポートは止まったままで、ユーザーは「エンジンを再起動してください」と言われても、シーンが消えていたら困ります。

この章ではエンジンが落ちたことを検出して、新しいエンジンを起動しエディタが持っているシーンを送り直して、元の状態に戻す仕組みを作ります。作るのは `EngineSupervisor` という 1 つのクラスです。

!!! info "このページを読む前に"
    - [第 53 章 プロセスを分ける：落ちても生きる構成](53-process-split.md)（`Disconnected` と、2 種類の例外）
    - [第 55 章 エンジンをサーバーにする：EngineHost](55-engine-host.md)（`EngineProcess`）
    - [第 40 章 Scene API](40-scene-api.md)（エディタが持つシーンが、元のデータであること）
    - [第 44 章 Undo / Redo](44-undo-redo.md)（落ちても残したい履歴）

## 元のデータは、エディタが持つ

立て直しの前提はシーンの本物が、エディタ側にあることです。第 40 章でエディタが `SceneDocument`（オブジェクトの木と各オブジェクトの値）を持ち、エンジンにはその写しを送るという形にしました。この形のおかげでエンジンが落ちても、シーンは失われません。

エンジンの中にしかないものは、落ちると消えます。たとえば、物理シミュレーションの途中の速度、パーティクルの位置、読み込み途中のアセットです。これらは送り直せません。エディタの編集中の状態ではなく、再生中の状態なので立て直したあとは「再生前の状態に戻る」のが正しい動きです。

<svg class="fig flow" viewBox="0 0 720 230" role="img" aria-label="エンジンが落ちる、切断を検出する、新しいエンジンを起動する、シーンを送り直す、の流れ"><defs><marker id="rcA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">落ちてから、元に戻るまで</text><rect x="16" y="44" width="150" height="70" rx="12" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="91" y="70" text-anchor="middle" style="font-size:12px;font-weight:600">1 エンジンが落ちる</text><text x="91" y="92" text-anchor="middle" style="font-size:11px;font-weight:400">パイプが切れる</text><rect x="186" y="44" width="150" height="70" rx="12" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="261" y="70" text-anchor="middle" style="font-size:12px;font-weight:600">2 検出</text><text x="261" y="92" text-anchor="middle" style="font-size:11px;font-weight:400">Disconnected が起きる</text><rect x="356" y="44" width="150" height="70" rx="12" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="431" y="70" text-anchor="middle" style="font-size:12px;font-weight:600">3 再起動</text><text x="431" y="92" text-anchor="middle" style="font-size:11px;font-weight:400">新しい名前のパイプで</text><rect x="526" y="44" width="178" height="70" rx="12" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="615" y="70" text-anchor="middle" style="font-size:12px;font-weight:600">4 送り直す</text><text x="615" y="92" text-anchor="middle" style="font-size:11px;font-weight:400">SceneDocument を全部</text><line x1="166" y1="79" x2="186" y2="79" stroke="currentColor" stroke-width="2" marker-end="url(#rcA)"/><line x1="336" y1="79" x2="356" y2="79" stroke="currentColor" stroke-width="2" marker-end="url(#rcA)"/><line x1="506" y1="79" x2="526" y2="79" stroke="currentColor" stroke-width="2" marker-end="url(#rcA)"/><text x="360" y="160" text-anchor="middle" style="font-size:12px;font-weight:400">この間、エディタの UI は生きていて、シーン、Undo の履歴、パネルの状態はそのまま残る。</text><text x="360" y="182" text-anchor="middle" style="font-size:12px;font-weight:400">ビューポートだけが、2 から 4 の間、止まった絵になる。</text><text x="360" y="204" text-anchor="middle" style="font-size:12px;font-weight:400">連続で失敗したら、あきらめて「エンジンを起動できません」と知らせる。</text></svg>

## 状態を持つ

立て直しの途中で UI が「いま何が起きているか」を知る必要があります。ボタンを無効にするビューポートに「再起動中」と重ねるといった表示のためです。そこで、エンジンの状態を 4 つに分けます。

```csharp
public enum EngineState { Stopped, Running, Restarting, Failed }
```

`Stopped` はまだ起動していないまたは自分で閉じた状態です。`Running` は繋がっていて命令を送れます。`Restarting` は落ちたことを検出して立て直している最中です。`Failed` は何度やっても起動できずあきらめた状態です。`Failed` を分けておくのは起動に失敗し続けるエンジンを無限に再起動しないためです。

## EngineSupervisor

```csharp
public sealed class EngineSupervisor : IAsyncDisposable
{
    private readonly string _exePath;
    private readonly string _pipeBase;
    private readonly Func<EngineClient, Task> _restore;
    private readonly int _maxConsecutiveFailures;
    private readonly TimeSpan _startTimeout = TimeSpan.FromSeconds(5);

    private EngineProcess? _current;
    private int _generation;                 // 起動のたびに増やす。パイプの名前に使う
    private int _disposed;
    private int _restarting;                 // 立て直しの二重起動を防ぐ旗

    public EngineState State { get; private set; } = EngineState.Stopped;
    public EngineClient? Client => _current?.Client;
    public int RestartCount { get; private set; }

    // 状態が変わったときに呼ばれる（スレッド プールのスレッド。画面を触るときは Dispatcher を通す）
    public event Action<EngineState>? StateChanged;
```

`_restore` は新しいエンジンにエディタのシーンを送り直す処理です。呼び出し側が渡します。`Supervisor` 自身はシーンの中身を知りません。エンジンのプロセスを生かす仕事と状態を戻す仕事を分けておくためです。

```csharp
    public EngineSupervisor(string exePath, string pipeBase, Func<EngineClient, Task> restore, int maxConsecutiveFailures = 3)
    {
        _exePath = exePath;
        _pipeBase = pipeBase;
        _restore = restore;
        _maxConsecutiveFailures = maxConsecutiveFailures;
    }

    public async Task StartAsync()
    {
        await LaunchAsync();
        SetState(EngineState.Running);
    }

    private async Task LaunchAsync()
    {
        string pipeName = $"{_pipeBase}.{Interlocked.Increment(ref _generation)}";   // 毎回、別の名前にする
        EngineProcess process = await EngineProcess.StartAsync(_exePath, pipeName, _startTimeout);
        process.Client.Disconnected += () => OnDisconnected(process);
        _current = process;
        await _restore(process.Client);
    }
```

パイプの名前を毎回変えるのは、前のエンジンのプロセスがまだ終了しきっていない間に新しいエンジンが同じ名前でパイプを作ろうとすると、失敗することがあるからです。第 53 章のサーバーはパイプの最大インスタンス数を 1 にしているので、古いパイプが残っていれば新しいパイプは作れません。世代番号を付けておけばこの衝突は起きません。

起動してパイプが繋がったら `Disconnected` に購読し、最後に `_restore` を呼びます。`_restore` の中で例外が出れば起動の失敗として扱われます。

## 落ちたときの動き

```csharp
    private void OnDisconnected(EngineProcess process)
    {
        if (Volatile.Read(ref _disposed) == 1) return;               // 自分で閉じたときは、立て直さない
        if (!ReferenceEquals(process, _current)) return;             // 古いエンジンの通知は、無視する
        _ = RecoverAsync();
    }
```

`Disconnected` はエンジンが落ちたときだけでなく、自分で `Dispose` したときにも起きます。そのため、`_disposed` を見て後始末の最中は立て直さないようにします。もう 1 つの検査は古いエンジンからの遅れた通知を無視するためです。立て直しの途中で前のエンジンの `Disconnected` がもう一度届くと二重に再起動してしまいます。

```csharp
    private async Task RecoverAsync()
    {
        if (Interlocked.Exchange(ref _restarting, 1) == 1) return;
        try
        {
            SetState(EngineState.Restarting);
            EngineProcess? dead = _current;
            _current = null;
            dead?.Dispose();                                         // 残っていれば片付ける

            for (int failures = 0; failures < _maxConsecutiveFailures; failures++)
            {
                if (Volatile.Read(ref _disposed) == 1) return;
                await Task.Delay(TimeSpan.FromMilliseconds(200 * (1 << failures)));   // 200, 400, 800 ms と待つ間隔を延ばす
                try
                {
                    await LaunchAsync();
                    RestartCount++;
                    SetState(EngineState.Running);
                    return;
                }
                catch (Exception e) when (e is InvalidOperationException or TimeoutException or IOException)
                {
                    _current?.Dispose();
                    _current = null;
                }
            }
            SetState(EngineState.Failed);                            // 何度やっても起動しない。人に知らせる
        }
        finally
        {
            Volatile.Write(ref _restarting, 0);
        }
    }
```

`Interlocked.Exchange` で旗を立て、すでに立て直し中なら何もしません。複数の場所から同時に `Disconnected` が届いても、再起動は 1 本だけです。

再起動の前に待つのは落ちた直後にすぐ起動し直すと同じ原因でまた落ちるからです。たとえば、壊れたシーンを送った直後にエンジンが落ちる場合、200 ms 待っても結果は同じですが、起動に失敗するたびに待つ時間を 200、400、800 ms と延ばすことで、CPU を使い切る再起動の連打を避けられます。

あきらめるまでの回数は連続で失敗した回数です。起動して `_restore` まで終われば `return` で抜けるので、次に落ちたときはまた最初から 3 回数えます。起動はできるがシーンを送り直すと必ず落ちるという場合、この数え方では永遠に再起動を繰り返します。その場合は `RestartCount` が短い時間に増え続けるのを見張って、`Failed` にする判断を足します。ここでは書いていません。

```csharp
    private void SetState(EngineState state)
    {
        State = state;
        StateChanged?.Invoke(state);
    }

    public async ValueTask DisposeAsync()
    {
        Interlocked.Exchange(ref _disposed, 1);
        _current?.Dispose();
        _current = null;
        await Task.CompletedTask;
    }
}
```

## シーンを送り直す：restore

`_restore` が行うのは第 40 章の `SceneDocument` を新しいエンジンの `IEngineService` の命令で再現することです。

```csharp
// 確かめていない。SceneDocument と SceneObject は、第 40 章のエディタ側のシーンを想定した名前
async Task RestoreAsync(EngineClient client)
{
    var engine = new RemoteEngineService(client);
    engine.Initialize(0, viewportWidth, viewportHeight);       // 共有メモリも作り直される（第 56 章）
    engine.SceneClear();
    foreach (SceneObject o in document.WalkParentsFirst())     // 親が先。子を作るときに親の id が要るため
    {
        engine.SceneCreate(o.Id, o.ParentId, o.Name);
        engine.SceneSetTransform(o.Id, o.Position, o.RotationRadians, o.Scale);
        engine.SceneSetColor(o.Id, o.Color);
    }
}
```

親から順に作るのは `SceneCreate` が親の id を必要とするからです。子が先だと「親がいない」という失敗が返ります。`Initialize` は第 56 章で見たとおり共有メモリを新しい名前で作り直します。ビューポートの側は `FrameChanged` を受けて、新しい `SharedFrame` を開き直します。

落ちる前に `IsRunning` を見ていた UI があれば、落ちた時点で `false` になる必要があります。`RemoteEngineService` は `EngineDisconnectedException` を受けたら `_running` を `false` にして、再び使えなくします。立て直したあとは新しい `RemoteEngineService` を作って差し替えるほうが、状態が混ざらず簡単です。

## UI に知らせる

`StateChanged` はスレッド プールのスレッドから呼ばれます。画面に反映するときは、`Dispatcher` を通します。

```csharp
supervisor.StateChanged += state => Dispatcher.BeginInvoke(() =>
{
    ViewportOverlay.Visibility = state == EngineState.Running ? Visibility.Collapsed : Visibility.Visible;
    OverlayText.Text = state switch
    {
        EngineState.Restarting => "エンジンを再起動しています…",
        EngineState.Failed => "エンジンを起動できません。ログを確認してください。",
        _ => "",
    };
});
```

ビューポートは、止まった最後の絵のまま残ります。その上に半透明の文字を重ねると、「固まった」のではなく「再起動している」と伝わります。`Failed` のときは、ログ パネル（第 50 章）への案内を出します。

## 動かして確かめる

テスト用のエンジンは、`crash` を受けるとアクセス違反で落ちます。新しい名前のパイプで、起動し直されることを確かめました。`restore` の中身は `ping` だけにしています。

```text title="実行結果"
  restore #1: ping -> pong
  state -> Running
crash #1
  crash -> EngineDisconnectedException
  state -> Restarting
  restore #2: ping -> pong
  state -> Running
  after recovery: state=Running restarts=1 ping=pong
crash #2
  state -> Restarting
  crash -> EngineDisconnectedException
  restore #3: ping -> pong
  state -> Running
  after recovery: state=Running restarts=2 ping=pong
```

1 回落ちるごとに `Restarting` を経て、`_restore` が呼ばれ `Running` に戻っています。2 回目の落下でも同じです。`crash` の呼び出しが `EngineDisconnectedException` になるのと `Restarting` への変化は、どちらが先に起きるか決まっていません（2 回目は順番が逆でした）。呼び出し側はどちらの順でも動くように書きます。

起動できないパスも確かめました。存在しない exe を渡すと、`StartAsync` が `Win32Exception` になります。ここで確かめたのは、最初の起動の失敗だけです。再起動の途中で連続して失敗し、`Failed` になるパスは、動かして確かめていません。

## 落ちる前に守っておくもの

立て直しで戻るのは、エディタが持っているものだけです。エディタ自身が落ちると、全部が消えます。次の備えを足しておくと安全です。

- **自動保存**: 数分おきにシーンを一時ファイルに書く。第 45 章の保存処理を別の名前で呼ぶだけで足りる
- **落ちた原因の記録**: エンジンの終了コード（`0xC0000005` はアクセス違反）と、標準エラーの最後の数十行をログに残す。再現のために直前に送った命令の履歴も数十件持っておく
- **同じ命令で落ち続けるときの検出**: 立て直し直後に、また同じ命令で落ちるなら、その命令の履歴を見せて、ユーザーに原因を伝える

どれも、この章では書いていません。

## よくあるミス

??? failure "再起動が、何十回も繰り返される"
    **原因**: 起動はできるが、シーンを送り直すと落ちる場合、連続失敗の数え方では毎回リセットされます。
    **対処**: 短い時間に何度も落ちたら、`Failed` にする判断を足します。

??? failure "再起動したのに、ビューポートが真っ黒のまま"
    **原因**: 新しいエンジンの共有メモリを、エディタが開き直していません。`FrameChanged` を購読していないか、古い `RemoteEngineService` を使い続けています。
    **対処**: 立て直しのたびに新しい `RemoteEngineService` を作って、`FrameChanged` と `FrameReady` を購読し直します。

??? failure "Disconnected で ObservableCollection を触って、例外になる"
    **原因**: `Disconnected` と `StateChanged` は、スレッド プールのスレッドで起きます。
    **対処**: 画面や UI にバインドしたコレクションに触るときは、`Dispatcher` を通します（第 17 章）。

## まとめ

- 立て直しの元になるのはエディタが持つ `SceneDocument`。エンジンの中にしかないものは、戻らない
- 状態は `Stopped`、`Running`、`Restarting`、`Failed` の 4 つ。UI は状態を見て表示を変える
- 再起動のたびにパイプの名前を替える。前のエンジンの残りと衝突しない
- 連続で失敗したら、待つ時間を延ばし、回数の上限であきらめる

!!! note "確かめたもの、確かめていないもの"
    `EngineSupervisor` はテスト用のエンジン（C++ は g++ の `-Wall -Wextra` で警告なし）と組み合わせて、落ちて立て直すところを 2 回、起動に失敗するところを 1 回、確かめた。`Failed` に至るパス、`_restore` の中での失敗、本物の `SceneDocument` での送り直しは確かめていない。`RestoreAsync` と `Dispatcher` のコードはコンパイルしていない。

次は、エンジンの操作を AI に開く話です。[第 58 章 AI から操作する：MCP](58-mcp.md) へ進みます。
