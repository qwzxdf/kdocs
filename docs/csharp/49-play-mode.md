---
title: 第 49 章 Play モード
tags:
  - C#連携
---

# 第 49 章 Play モード

この章で、エディタに編集モードと Play モードを作ります。Play ボタンでゲームが動き出し、Stop ボタンで、動かす前のシーンに戻ります。Unity や Unreal Engine と同じ操作です。第 40 章で決めた「データの持ち主はエディタ、エンジンは写し」という設計がここで報われます。

!!! info "このページを読む前に"
    - [第 48 章 ホット リロード](48-hot-reload.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Play/IPlayModeService.cs`（新規） | Play モードの状態を持つ窓口 |
    | `Play/PlayModeService.cs`（新規） | Play / Pause / Stop の状態遷移 |


## Play でシーンはどうなるのか

ゲームを動かすと、物の位置や色が変わります（たとえば `SpinnerGame` が物を回します）。Stop したときに、動かす前の状態に戻っていなければ、エディタとして使えません。ゲームを遊んだせいで、置いた物の向きが変わってしまうからです。

戻す方法は 2 つあります。

| 方式 | 内容 | 問題 |
| --- | --- | --- |
| Play 前に状態を保存し、Stop で復元する | シーン全体をコピーする | コピーを取る処理が要る。Play 中の変更を間違ってドキュメントに混ぜない注意が要る |
| ドキュメントは触らず、エンジンのコピーだけが動く（採用） | Play 中に動くのはエンジンの写しだけ。Stop で、写しをドキュメントから作り直す | 追加のコピー処理が要らない |

この教材の構造では、ドキュメント（`SceneDocument`）はエンジンの外にあって、Play 中は一切変わりません。ゲームが動かすのは、エンジンの `Scene`（写し）だけです。だから、Stop のときは、エンジンのシーンを空にして、ドキュメントの内容から作り直すだけで、元に戻ります。

```text
編集モード                Play                    Stop
Document ──同期──▶ Engine    Document（変わらない）     Document ──作り直し──▶ Engine
  [Cube]            [Cube]     [Cube]        [Cube が回る]   [Cube]            [Cube]（元の向き）
```

### Play 中の編集は禁止する

Play 中にツリーやプロパティを編集できたら、どうなるでしょう。ドキュメントが変わり、Stop で作り直すと、Play 中の編集が反映されます。しかし、Play 中に動いているのは「エンジンの写し」なので、編集とゲームの動きが混ざって、混乱します。

そこで、この教材では、Play 中は編集を禁止します。

| 操作 | Play 中 |
| --- | --- |
| ツリーの追加、削除、親子づけ | 禁止（グレーアウト） |
| プロパティの編集 | 禁止 |
| ギズモで動かす | 禁止 |
| Undo/Redo | 禁止 |
| 新規、開く、保存 | 新規と開くは禁止。保存は可能（ドキュメントは変わらないので） |
| 選択（ツリー、クリック） | 可能（見るだけ） |
| カメラの操作 | 可能 |

Unity は、Play 中の編集を許して、Stop で捨てます。使い勝手は良い反面、「Play 中に直したのに消えた」という事故が起きます。この教材は、安全な側に倒しています。

この章のゴールは次のとおりです。

- ツール バーに Play、Pause、Step、Stop が並ぶ。
- Play でゲームが動く。Stop でシーンが元に戻る。
- Play 中は編集が無効になり、画面の枠がオレンジ色になる。
- ゲームが例外を出して止まったときも、エディタが編集モードに戻る。

## エンジンの Play 状態

C の API は 3 つです。

```c
/* 0: 編集, 1: Play, 2: 一時停止 */
ME_API MeResult me_play_set_state(MeEngine* engine, int32_t state);
ME_API MeResult me_play_get_state(const MeEngine* engine, int32_t* out_state);
ME_API MeResult me_play_step(MeEngine* engine);                  /* 一時停止中に、1 フレームだけ進める */
```

エンジン側では、第 47 章の `SetPlaying(bool)` をこの章の `SetPlayState(PlayState)` に置き換えます。一時停止が `bool` では表せないからです。Player の `SetPlaying(true)` も、`SetPlayState(PlayState::Playing)` に直してください。

```cpp
enum class PlayState : std::int32_t { Edit = 0, Playing = 1, Paused = 2 };

struct Engine::Impl {
  // …
  PlayState play_state = PlayState::Edit;
  bool step_requested = false;
};

void Engine::SetPlayState(PlayState next) {
  auto& s = *impl_;
  if (s.play_state == next) return;

  const bool was_running = s.play_state != PlayState::Edit;
  const bool will_run = next != PlayState::Edit;

  if (!was_running && will_run && s.game && s.game->IsLoaded()) s.game->Module()->OnPlay();      // 編集 → Play
  if (was_running && !will_run && s.game && s.game->IsLoaded()) s.game->Module()->OnStop();      // Play → 編集
  s.play_state = next;
}

void Engine::Tick(float delta_seconds) {
  auto& s = *impl_;
  // …
  const bool run = s.play_state == PlayState::Playing || (s.play_state == PlayState::Paused && s.step_requested);
  if (run && s.game && s.game->IsLoaded()) {
    const float dt = s.step_requested ? 1.0f / 60.0f : delta_seconds;       // ステップは、固定の 1/60 秒
    s.step_requested = false;
    try {
      s.game->Module()->OnUpdate(dt);
    } catch (const std::exception& e) {
      LogError("ゲームの更新で例外: {}。Play を止めます", e.what());
      SetPlayState(PlayState::Edit);                // エディタが気づけるよう、状態を編集に戻す
    }
  }
  // …
}
```

`enum class PlayState : std::int32_t` は、土台の型を `int32_t` に固定して、C の `int32_t` と対応させます（第 33 章と同じ作法）。ゲームの `OnPlay` と `OnStop` を呼ぶのは、編集と Play の境目を越えるときだけです。「Play ⇄ 一時停止」では呼びません。ゲームから見ると、中断に過ぎないからです。

`step_requested` は、一時停止中でも `OnUpdate` を 1 回だけ呼ぶための印です。1 フレームずつ動きを確かめる、デバッグ向けの機能で、時間は固定の 1/60 秒で進めます。ゲームが例外を出したら、`Playing` のまま例外が続かないよう、状態を編集に戻します。エディタは、これをポーリングで見つけます（あとの節）。

## エンジンのシーンをドキュメントから作り直す

Stop のとき、エンジンの `Scene` をドキュメントの内容にそろえます。`SceneEngineSync` に `Resync` を足します。

```csharp
public sealed class SceneEngineSync
{
    private readonly SceneDocument _document;
    private readonly IRenderLoop _loop;
    // …

    // エンジンのシーンを空にして、ドキュメントの内容から作り直す。
    public void Resync()
    {
        // 親が先になるように、木をたどって、(id, parentId, name, 変換, 色) の一覧を作る
        var list = new List<(uint Id, uint ParentId, string Name, Vector3 Position, Vector3 Rotation, Vector3 Scale, Vector4 Color)>();
        void Walk(SceneObject o)
        {
            list.Add((o.Id, o.Parent?.Id ?? 0, o.Name, o.Position,
                      o.RotationDegrees * (MathF.PI / 180f), o.Scale, o.Color));
            foreach (var child in o.Children) Walk(child);
        }
        foreach (var root in _document.Roots) Walk(root);

        // 1 つの命令にまとめる。途中で、ほかの命令が割り込まない。
        _loop.Post(e =>
        {
            e.SceneClear();
            foreach (var o in list)
            {
                e.SceneCreate(o.Id, o.ParentId, o.Name);
                e.SceneSetTransform(o.Id, o.Position, o.Rotation, o.Scale);
                e.SceneSetColor(o.Id, o.Color);
            }
        });
    }
}
```

`List<(uint Id, …)>` の中身は、名前付きの要素を持つ「タプル」です。小さなデータ型をいちいち定義せずに済みます。ローカル関数 `Walk` は木を再帰的にたどり、親が先に追加される（深さ優先の行きがけ順）ので、`SceneCreate` を呼ぶ時点で、親が必ず存在します。

全体を 1 つの `Post` にしているのは、途中で別の命令が割り込まないようにするためです。描画スレッドは命令を処理し終えてから描くので、作りかけのシーンが画面に出ることもありません。最後に、現在の選択を `SceneSetSelection` で送り直します（`Resync` は選択も消すからです）。

## Play モードのサービス

エディタ側の、状態の持ち主です。

```csharp title="Play/IPlayModeService.cs（新規）"
namespace Editor.Play;

public enum PlayState { Edit = 0, Playing = 1, Paused = 2 }

public interface IPlayModeService
{
    PlayState State { get; }
    bool IsEditing { get; }              // 編集してよいか
    bool CanPlay { get; }                // ゲームが読み込まれているか

    void Play();
    void Pause();
    void Stop();
    void Step();

    event Action? StateChanged;
}
```

```csharp title="Play/PlayModeService.cs（新規）"
using System.Windows.Threading;
using Editor.Engine;
using Editor.Log;
using Editor.Viewport;

namespace Editor.Play;

public sealed class PlayModeService : IPlayModeService
{
    private readonly IRenderLoop _loop;
    private readonly IGameService _game;
    private readonly SceneEngineSync _sync;
    private readonly ILogService _log;
    private readonly DispatcherTimer _watch;

    public PlayModeService(IRenderLoop loop, IGameService game, SceneEngineSync sync, ILogService log)
    {
        _loop = loop;
        _game = game;
        _sync = sync;
        _log = log;

        // エンジンが（ゲームの例外で）自分で Play を止めたことに、気づくためのポーリング
        _watch = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(200) };
        _watch.Tick += (_, _) => CheckEngineState();
        _game.StateChanged += () => StateChanged?.Invoke();
    }

    public PlayState State { get; private set; } = PlayState.Edit;
    public bool IsEditing => State == PlayState.Edit;
    public bool CanPlay => _game.IsLoaded && _loop.IsRunning;
    public event Action? StateChanged;

    public void Play()
    {
        if (State == PlayState.Playing) return;
        if (State == PlayState.Edit && !CanPlay)
        {
            _log.Warning("ゲームが読み込まれていないので、Play できません");
            return;
        }
        SetState(PlayState.Playing);
        _watch.Start();
    }

    public void Pause()
    {
        if (State == PlayState.Playing) SetState(PlayState.Paused);
        else if (State == PlayState.Paused) SetState(PlayState.Playing);       // もう一度押すと再開
    }

    public void Step()
    {
        if (State == PlayState.Paused) _loop.Post(e => e.PlayStep());
    }

    public void Stop()
    {
        if (State == PlayState.Edit) return;
        _watch.Stop();
        SetState(PlayState.Edit);
        _sync.Resync();                           // 動いたシーンを捨てて、ドキュメントから作り直す
    }

    private void SetState(PlayState next)
    {
        State = next;
        int value = (int)next;
        _loop.Post(e => e.PlaySetState(value));
        StateChanged?.Invoke();
    }

    private void CheckEngineState()
    {
        if (State == PlayState.Edit) return;
        // 非同期で聞く（UI を止めない）
        _ = Task.Run(() => _loop.Invoke(e => e.PlayGetState())).ContinueWith(task =>
        {
            if (task.IsCompletedSuccessfully && task.Result == (int)PlayState.Edit && State != PlayState.Edit)
            {
                // エンジンの側から止まった（ゲームの例外）。エディタも編集に戻して、作り直す
                _log.Warning("ゲームが停止しました。編集モードに戻ります");
                _watch.Stop();
                State = PlayState.Edit;
                _sync.Resync();
                StateChanged?.Invoke();
            }
        }, TaskScheduler.FromCurrentSynchronizationContext());
    }
}
```

Play の状態は、エディタ（`State`）とエンジン（`play_state`）の両方にあります。普段はエディタが決めてエンジンに送りますが、ゲームの例外のように、エンジンが自分で状態を変えることもあります。エディタはそれを知る手段がないので、200 ミリ秒ごとにエンジンへ状態を聞く、ポーリングで気づきます。

`ContinueWith(task => …, TaskScheduler.FromCurrentSynchronizationContext())` は、非同期の処理が終わったあと、UI スレッドで続きを実行する、古い書き方です。`async/await` を使えない文脈で、同じことをします。`_ =` で `Task` を放置していますが、例外は `ContinueWith` の中で見ているので問題ありません。

`Stop` の順序にも意味があります。先にエンジンへ「編集に戻れ」（ゲームの `OnStop`）、続けて `Resync` を送ります。どちらも `Post` なので、積んだ順に実行されます。`IPlayModeService` と `IGameService` は、`App.xaml.cs` で `RegisterSingleton` します。

## 編集を禁止する

画面の側だけでなく、ロジックの側でも編集を止めます。画面の無効化は、ショートカットなどですり抜けられるからです。

窓口（`UndoableSceneEditor`）で止めます。

```csharp
private bool CanEdit()
{
    if (_play.IsEditing) return true;
    _log.Warning("Play 中は、シーンを編集できません");
    return false;
}

public void SetPosition(SceneObject obj, Vector3 value)
{
    if (!CanEdit() || obj.Position == value) return;
    // …
}
```

`CreateObject`、`DestroyObjects`、`Reparent` などの先頭にも、同じ検査を入れます。

履歴とファイルの操作は、コマンドの `CanExecute` で止めます。

```csharp
// MainWindowViewModel：第 44、45 章の CanExecute に、「編集中か」を足す
private bool CanUndo() => _history.CanUndo && _play.IsEditing;
private bool CanRedo() => _history.CanRedo && _play.IsEditing;
private bool CanFile() => _play.IsEditing;

[RelayCommand(CanExecute = nameof(CanFile))] private Task New() => _files.NewAsync();
[RelayCommand(CanExecute = nameof(CanFile))] private Task Open() => _files.OpenAsync();

// _play.StateChanged で、これらの NotifyCanExecuteChanged を呼ぶ
_play.StateChanged += () =>
{
    UndoCommand.NotifyCanExecuteChanged();
    RedoCommand.NotifyCanExecuteChanged();
    NewCommand.NotifyCanExecuteChanged();
    OpenCommand.NotifyCanExecuteChanged();
};
```

画面の側は、パネルの外側に `IsEnabled` をバインドします。

```csharp
// SceneTreeViewModel、PropertyViewModel
public bool IsEditingEnabled => _play.IsEditing;
// _play.StateChanged で OnPropertyChanged(nameof(IsEditingEnabled)) を呼ぶ
```

```xml
<!-- PropertyView.xaml の外側の StackPanel -->
<StackPanel IsEnabled="{Binding IsEditingEnabled}">
```

`IsEnabled` は子の部品にも伝わるので、外側の入れ物に 1 つ付ければ足ります。ただし `PropertyView` は、第 42 章で `IsEnabled="{Binding HasTarget}"` をすでに付けています。両方の条件を満たすために、別の入れ物（`Border`）に分けて、それぞれに付けます。

ビューポートの操作は、Play 中にカメラだけを許します。

```csharp
// ViewportViewModel.OnInput の冒頭
if (!_play.IsEditing)
{
    // Play 中：カメラの操作だけ許す（右、中ボタン、ホイール）。ギズモとピッキングは行わない。
    if (button == 0) return;
}
```

## ツール バーと見た目

`MainWindow.xaml` のメニューの下にツール バーを足します。

```xml
<ToolBar DockPanel.Dock="Top">
    <Button Command="{Binding PlayCommand}" ToolTip="Play / 再開 (Ctrl+P)">▶</Button>
    <Button Command="{Binding PauseCommand}" ToolTip="一時停止 (Ctrl+Shift+P)">⏸</Button>
    <Button Command="{Binding StepCommand}" ToolTip="1 フレーム進める (Ctrl+Alt+P)">⏭</Button>
    <Button Command="{Binding StopCommand}" ToolTip="停止 (Ctrl+P)">⏹</Button>
</ToolBar>
```

```csharp
// MainWindowViewModel
[RelayCommand(CanExecute = nameof(CanPlay))] private void Play() => _play.Play();
[RelayCommand(CanExecute = nameof(CanPause))] private void Pause() => _play.Pause();
[RelayCommand(CanExecute = nameof(CanStep))] private void Step() => _play.Step();
[RelayCommand(CanExecute = nameof(CanStop))] private void Stop() => _play.Stop();
[RelayCommand] private void TogglePlay() { if (_play.State == PlayState.Edit) _play.Play(); else _play.Stop(); }

private bool CanPlay() => _play.CanPlay && _play.State != PlayState.Playing;
private bool CanPause() => _play.State != PlayState.Edit;
private bool CanStep() => _play.State == PlayState.Paused;
private bool CanStop() => _play.State != PlayState.Edit;

// _play.StateChanged で、各コマンドの NotifyCanExecuteChanged() を呼ぶ
```

```xml
<Window.InputBindings>
    <KeyBinding Key="P" Modifiers="Control" Command="{Binding TogglePlayCommand}" />
    <KeyBinding Key="P" Modifiers="Control+Shift" Command="{Binding PauseCommand}" />
    <KeyBinding Key="P" Modifiers="Control+Alt" Command="{Binding StepCommand}" />
</Window.InputBindings>
```

Play 中であることを色でも一目で分かるようにします。本体を `Border` で囲み、状態に応じて枠の色を変えます。

```xml
<Border BorderThickness="3">
    <Border.Style>
        <Style TargetType="Border">
            <Setter Property="BorderBrush" Value="Transparent" />
            <Style.Triggers>
                <DataTrigger Binding="{Binding PlayState}" Value="Playing">
                    <Setter Property="BorderBrush" Value="#FFF39C12" />
                </DataTrigger>
                <DataTrigger Binding="{Binding PlayState}" Value="Paused">
                    <Setter Property="BorderBrush" Value="#FF3498DB" />
                </DataTrigger>
            </Style.Triggers>
        </Style>
    </Border.Style>
    <!-- 既存の Grid（左・中・右） -->
</Border>
```

`Setter` が既定値（透明）で、`DataTrigger` が当たったときだけ上書きする形です（第 11 章）。XAML では、バインドした列挙型の値を名前の文字列（`"Playing"`）で比較できます。

## 動かして確かめる

| 操作 | 期待する結果 |
| --- | --- |
| ゲームを読み込んでいない状態 | Play ボタンがグレー。`Ctrl+P` を押すとログに警告 |
| `Spin_A` という物を作って Play（`Ctrl+P`） | 枠がオレンジになり、箱が回る。ツリーとプロパティがグレー |
| Play 中にツリーを操作 | 反応しない（グレーアウト） |
| Play 中に箱をクリック | 選択はできる。ギズモは出ない |
| カメラの右ドラッグ | 動かせる |
| Pause | 回転が止まる。枠が青になる。Step で少しずつ進む |
| Stop（`Ctrl+P`） | 箱が動かす前の向きに戻る。枠が消える。編集できる |
| Play 中に `kSpeed` を書き換えてビルド | 回転の速さが変わる。向きが飛ばない（ホット リロード） |
| ゲームの `OnUpdate` で例外を投げる | ログに警告が出て、自動で編集モードに戻る |
| Play 中に保存 | 保存できる。ドキュメントは動かす前の状態のまま |
| Play 中にウィンドウを閉じる | 正常に終了する |

??? failure "Stop しても、物の向きが戻らない"
    `Resync` を呼んでいないか、`SceneClear` のあとに作り直す命令を積み忘れています。`SceneClear` のあとに `SceneCreate` が続く 1 つの `Post` になっているか確認します。

??? failure "Play 中にギズモで動かせてしまう"
    画面の側だけで止めています。`ISceneEditor` の窓口で `CanEdit()` を検査します。ロジックの側で止めるのが確実です。

??? failure "Stop したあと、選択の黄色い枠が消える"
    `Resync` はエンジンのシーンを空にするので、選択も消えます。`Resync` の最後に選択を再送します。

??? failure "Play 中にホット リロードで物が回らなくなる"
    第 48 章の順序を確認します。新しいゲームに `OnPlay` を呼び、そのあとで `LoadState` します。

??? failure "ゲームが例外で止まったのに、エディタが Play 表示のまま"
    ポーリング（`CheckEngineState`）が動いていません。`_watch.Start()` を呼んでいるか確認します。

??? failure "Stop したのに、ゲームが動き続ける"
    `PlaySetState(0)` の命令が積まれていません。または、`OnStop` の中でゲームが集めた物の一覧を空にしていないため、次の Play で古い ID を触っています。

## この章のまとめ

- ドキュメントはエンジンの外にあって、Play 中は変わらない。Stop は、エンジンのシーンをドキュメントから作り直すだけで、元に戻る。
- Play 中の編集は、窓口（ロジック）と画面の両方で禁止する。
- エンジンが自分で状態を変える場合（ゲームの例外）は、エディタがポーリングで気づく。
- 状態は色（枠）でも見せる。

次の章では、エディタ全体のエラー処理の方針を整えます。

[第 50 章 ログとエラー処理](50-logging-errors.md) へ進みます。
