---
title: 第 29 章 Play モード
tags:
  - C#連携
---

# 第 29 章 Play モード

この章ではエディタに<strong>編集モード</strong>と <strong>Play モード</strong>を作ります。Play ボタンでゲームが動き出し、Stop ボタンで<strong>動かす前のシーンに戻ります</strong>。Unity や Unreal Engine と同じ操作です。第 20 章で決めた「<strong>データの持ち主はエディタ、エンジンは写し</strong>」という設計が、ここで報われます。

## この章の考え方

### Play でシーンはどうなるのか

ゲームを動かすと物の位置や色が変わります（例：`SpinnerGame` が物を回す）。Stop したとき<strong>動かす前の状態に戻っていなければ</strong>、エディタとして使えません。ゲームを遊んだせいで置いた物の向きが変わってしまうからです。

戻す方法は 2 つあります。

| 方式 | 内容 | 問題 |
| --- | --- | --- |
| Play 前に状態を<strong>保存</strong>し、Stop で<strong>復元</strong>する | シーン全体をコピーする | コピーを取る処理が必要。Play 中の変更を間違ってドキュメントに混ぜない注意が必要 |
| <strong>ドキュメントは触らずエンジンのコピーだけが動く</strong>（採用） | Play 中に動くのは、エンジンの写しだけ。Stop で写しを<strong>ドキュメントから作り直す</strong> | 追加のコピー処理が要らない |

この教材の構造では<strong>ドキュメント（`SceneDocument`）はエンジンの外にあり Play 中は一切変わりません</strong>。ゲームが動かすのはエンジンの `Scene`（写し）だけです。だから、Stop のときは

> エンジンのシーンを空にして、ドキュメントの内容から<strong>作り直す</strong>

だけで元に戻ります。

```text
編集モード                Play                    Stop
Document ──同期──▶ Engine    Document（変わらない）     Document ──作り直し──▶ Engine
  [Cube]            [Cube]     [Cube]        [Cube が回る]   [Cube]            [Cube]（元の向き）
```

### Play 中の編集

Play 中にツリーやプロパティを編集できると、どうなるでしょう。ドキュメントが変わり Stop で作り直すと<strong>Play 中の編集が反映されます</strong>。しかし、Play 中は「エンジンの写し」が動いているので、編集とゲームの動きが<strong>混ざって</strong>混乱します。

そこで、この教材では<strong>Play 中は編集を禁止</strong>します。

| 操作 | Play 中 |
| --- | --- |
| ツリーの追加、削除、親子づけ | 禁止（グレーアウト） |
| プロパティの編集 | 禁止 |
| ギズモで動かす | 禁止 |
| Undo/Redo | 禁止 |
| 新規、開く保存 | 新規と開くは禁止。保存は可能（ドキュメントは変わらないので） |
| 選択（ツリー、クリック） | 可能（見るだけ） |
| カメラの操作 | 可能 |

Unity は Play 中の編集を許して、Stop で捨てます。これは使い勝手が良い反面、「Play 中に直したのに消えた」という事故が起きます。この教材は安全な側に倒しています。

## この章のゴール

- ツール バーに Play、Pause、Step、Stop が並ぶ。
- Play でゲームが動く。Stop で<strong>シーンが元に戻る</strong>。
- Play 中は編集が無効になり画面の枠がオレンジ色になる。
- ゲームが例外を出して止まったときもエディタが編集モードに戻る。

## 手順 1：エンジンの Play 状態

### C の API

```c
/* 0: 編集, 1: Play, 2: 一時停止 */
ME_API MeResult me_play_set_state(MeEngine* engine, int32_t state);
ME_API MeResult me_play_get_state(const MeEngine* engine, int32_t* out_state);
ME_API MeResult me_play_step(MeEngine* engine);                  /* 一時停止中に、1 フレームだけ進める */
```

### エンジン側

第 27 章の `SetPlaying(bool)` は、この章の `SetPlayState(PlayState)` に置き換えます（一時停止を表せないため）。Player の `SetPlaying(true)` も、`SetPlayState(PlayState::Playing)` に直してください。

`Engine` の `Impl` に状態を持たせます。

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

| 部分 | 説明 |
| --- | --- |
| `enum class PlayState : std::int32_t` | 土台の型を `int32_t` に固定する。C の `int32_t` と対応させる（第 13 章と同じ作法） |
| 状態の遷移 | 「編集 → Play」で `OnPlay`、「Play → 編集」で `OnStop`。「Play ⇄ 一時停止」では呼ばない（ゲームには、中断としか見えない） |
| `step_requested` | 一時停止中でも 1 回だけ `OnUpdate` を呼ぶ。1 フレームずつ動きを確かめるデバッグ機能 |
| 例外で編集に戻す | ゲームが失敗したら、`Playing` のまま例外が続くのを避ける。<strong>エディタはこれをポーリングで検出する</strong>（手順 4） |

## 手順 2：エンジンのシーンをドキュメントから作り直す

Stop でエンジンの `Scene` をドキュメントの内容にそろえます。`SceneEngineSync` に `Resync` を足します。

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| タプルのリスト `List<(uint Id, …)>` | 名前付きの要素を持つ<strong>タプル</strong>をまとめて持つ。小さなデータ型をいちいち定義しない |
| ローカル関数 `Walk` | 木を再帰的にたどる。<strong>親が先に追加される</strong>（深さ優先の行きがけ順）ので `SceneCreate` で、親が先に存在する |
| `SceneClear` | エンジンのシーンを全部消す（第 20 章で作った API） |
| 1 つの `Post` | 全体を 1 回で実行する。途中で描画が走っても `Tick` は命令の<strong>後</strong>に行われる（描画スレッドは、命令を処理してから描く） |
| 選択の再送 | `Resync` の最後に現在の選択を `SceneSetSelection` で送り直す |

## 手順 3：Play モードのサービス

`Services\IPlayModeService.cs`:

```csharp
namespace Editor.Services;

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

`Services\PlayModeService.cs`:

```csharp
using System.Windows.Threading;

namespace Editor.Services;

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| 状態の持ち主 | 状態はエディタ（`State`）とエンジン（`play_state`）の<strong>両方</strong>にある。普段はエディタが決めてエンジンに送る。エンジンが自分で変えたとき（ゲームの例外）は、エディタが<strong>ポーリングで気づく</strong> |
| `ContinueWith(task => …, TaskScheduler.FromCurrentSynchronizationContext())` | 非同期の処理が終わったら、<strong>UI スレッドで</strong>続きを実行する。`async/await` を使えない文脈で同じことをする古い書き方 |
| `task.IsCompletedSuccessfully` | 例外なく完了したか |
| `Stop` の順序 | 先にエンジンに「編集に戻れ」（ゲームの `OnStop`）、続けて `Resync`。どちらも `Post` なので<strong>積んだ順に</strong>実行される |
| `_ =` | 戻り値の `Task` を待たずに放置する。例外は `ContinueWith` の中で見ているので問題ない |

`App.xaml.cs` で `IPlayModeService` を `RegisterSingleton` します。`IGameService` も同様です。

## 手順 4：編集を禁止する

画面の側だけでなく<strong>ロジックの側でも</strong>編集を止めます（画面の無効化は、ショートカットなどですり抜けられるため）。

### 窓口で止める

```csharp
// UndoableSceneEditor
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

`CreateObject`、`DestroyObjects`、`Reparent`、そのほかのメソッドの先頭にも同じ検査を入れます。

### 履歴とファイル

```csharp
// MainWindowViewModel
UndoCommand = new DelegateCommand(_history.Undo, () => _history.CanUndo && _play.IsEditing);
RedoCommand = new DelegateCommand(_history.Redo, () => _history.CanRedo && _play.IsEditing);
NewCommand = DelegateCommand.FromAsync(async () => await files.NewAsync(), () => _play.IsEditing);
OpenCommand = DelegateCommand.FromAsync(async () => await files.OpenAsync(), () => _play.IsEditing);
// _play.StateChanged で、これらの RaiseCanExecuteChanged を呼ぶ
```

### 画面を無効にする

各パネル（ツリー、プロパティ）の外側に `IsEnabled` をバインドします。

```csharp
// SceneTreeViewModel、PropertyViewModel
public bool IsEditingEnabled => _play.IsEditing;
// _play.StateChanged で RaisePropertyChanged(nameof(IsEditingEnabled))
```

```xml
<!-- PropertyView.xaml の外側の StackPanel -->
<StackPanel IsEnabled="{Binding IsEditingEnabled}">
```

`IsEnabled` は<strong>子の部品にも伝わる</strong>ので、外側の入れ物に 1 つ付ければ足ります。ただし、`PropertyView` は第 22 章で `IsEnabled="{Binding HasTarget}"` を付けているので、<strong>両方の条件を満たす</strong>ために別の入れ物（`Border`）に分けて、それぞれに付けます。

### ビューポートの操作

```csharp
// ViewportViewModel.OnInput の冒頭
if (!_play.IsEditing)
{
    // Play 中：カメラの操作だけ許す（右、中ボタン、ホイール）。ギズモとピッキングは行わない。
    if (button == 0) return;
}
```

## 手順 5：ツール バーと見た目

### ツール バー

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
PlayCommand = new DelegateCommand(_play.Play, () => _play.CanPlay && _play.State != PlayState.Playing);
PauseCommand = new DelegateCommand(_play.Pause, () => _play.State != PlayState.Edit);
StepCommand = new DelegateCommand(_play.Step, () => _play.State == PlayState.Paused);
StopCommand = new DelegateCommand(_play.Stop, () => _play.State != PlayState.Edit);
TogglePlayCommand = new DelegateCommand(() => { if (_play.State == PlayState.Edit) _play.Play(); else _play.Stop(); });
```

```xml
<Window.InputBindings>
    <KeyBinding Key="P" Modifiers="Control" Command="{Binding TogglePlayCommand}" />
    <KeyBinding Key="P" Modifiers="Control+Shift" Command="{Binding PauseCommand}" />
    <KeyBinding Key="P" Modifiers="Control+Alt" Command="{Binding StepCommand}" />
</Window.InputBindings>
```

### Play 中はオレンジの枠

Play 中であることを<strong>色で一目で分かる</strong>ようにします。`MainWindow.xaml` の本体を枠（`Border`）で囲み状態に応じて色を変えます。

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `DataTrigger` と列挙型 | バインドした値が `PlayState.Playing` のとき文字列 `"Playing"` と比べられる。XAML では列挙型の値を名前の文字列で比較できる |
| スタイルの既定値と上書き | `Setter` が既定（透明）。トリガーが当たったとき上書きする |
| 色で状態を伝える | 動作中の判別を文字の変化だけに頼らない |

## 動作確認

| 操作 | 期待する結果 |
| --- | --- |
| ゲームを読み込んでいない状態 | Play ボタンがグレー。`Ctrl+P` を押すとログに警告 |
| `Spin_A` という物を作って Play（`Ctrl+P`） | 枠がオレンジになり箱が回る。ツリーとプロパティがグレー |
| Play 中にツリーを操作 | 反応しない（グレーアウト） |
| Play 中に箱をクリック | 選択はできる。ギズモは出ない |
| カメラの右ドラッグ | 動かせる |
| Pause | 回転が止まる。枠が青になる。Step で少しずつ進む |
| Stop（`Ctrl+P`） | 箱が<strong>動かす前の向き</strong>に戻る。枠が消える。編集できる |
| Play 中に `kSpeed` を書き換えてビルド | 回転の速さが変わる。向きが飛ばない（ホット リロード） |
| ゲームの `OnUpdate` で例外を投げる | ログに警告が出て、自動で編集モードに戻る |
| Play 中に保存 | 保存できる。ドキュメントは動かす前の状態のまま |
| Play 中にウィンドウを閉じる | 正常に終了する |

## よくあるミス

??? failure "Stop しても、物の向きが戻らない"
    `Resync` を呼んでいない。または、`Resync` がエンジンのシーンを `Clear` した<strong>後</strong>に作り直す命令を積み忘れている。`SceneClear` の後に `SceneCreate` が続く 1 つの `Post` になっているか確認する。

??? failure "Play 中にギズモで動かせてしまう"
    画面の側だけで止めている。`ISceneEditor` の窓口で `CanEdit()` を検査する。ロジックの側で止めるのが確実。

??? failure "Stop した後、選択の黄色い枠が消える"
    `Resync` はエンジンのシーンを空にするので、選択も消える。`Resync` の最後に選択を再送する。

??? failure "Play 中にホット リロードで物が回らなくなる"
    第 28 章の順序を確認する。新しいゲームに `OnPlay` を呼びその後で `LoadState` する。

??? failure "ゲームが例外で止まったのに、エディタが Play 表示のまま"
    ポーリング（`CheckEngineState`）が動いていない。`_watch.Start()` を呼んでいるか確認する。

??? failure "Stop したのに、ゲームが動き続ける"
    `PlaySetState(0)` の命令が積まれていない。または、`OnStop` の中でゲームが集めた物の一覧を空にしていないため、次の Play で古い ID を触っている。

## この章のまとめ

- <strong>ドキュメントはエンジンの外にあり Play 中は変わらない</strong>。Stop はエンジンのシーンを<strong>ドキュメントから作り直す</strong>だけで、元に戻る。
- Play 中の編集は<strong>窓口（ロジック）と画面の両方</strong>で禁止する。
- エンジンが自分で状態を変える場合（ゲームの例外）は、エディタが<strong>ポーリング</strong>で気づく。
- 状態は<strong>色</strong>（枠）でも見せる。

## 次の章へ

次の章（[第 30 章 ログとエラー処理](30-logging-errors.md)）では、エディタ全体の<strong>エラー処理の方針</strong>を整えます。未処理の例外の捕捉、ログのファイル出力、ログ パネルの改良、そしてネイティブのクラッシュへの備えを扱います。
