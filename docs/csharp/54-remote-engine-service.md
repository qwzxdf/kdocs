---
title: 第 54 章 IEngineService を差し替える
tags:
  - C#連携
---

# 第 54 章 IEngineService を差し替える

エンジンを別のプロセスに出すとき、いちばん心配なのは「ここまで作ったエディタを書き直すことにならないか」です。シーン ツリーもプロパティ パネルも Undo も、エンジンを呼ぶ所は山ほどあります。それを全部 `await` だらけに書き換えるのは、現実的ではありません。

ここで効いてくるのが、第 33 章で作った `IEngineService` です。ビューモデルも `SceneEngineSync` も、エンジンを `IEngineService` 越しにしか触っていません。第 34 章で C++/CLI 版を作ったときも、この窓口の実装を 1 つ足しただけでした。パイプ版は 3 つ目の実装として足せます。

この章では前の章の `EngineClient` を使って、`RemoteEngineService` を作ります。そして、エンジンのプロセスがまだなくても、偽のエンジンを相手に動かして確かめます。

!!! info "このページを読む前に"
    - [第 53 章 プロセスを分ける：落ちても生きる構成](53-process-split.md)（前の章。`EngineClient` とメッセージの形）
    - [第 33 章 P/Invoke で C# から呼ぶ](33-pinvoke.md)（`IEngineService` の元の形）
    - [第 38 章 描画ループとスレッド](38-render-loop.md)（エンジンを触るのは描画スレッドだけ、という約束）
    - [C# 連携](index.md)（このセクション全体の地図と読む順番）


!!! abstract "この章で足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Editor/Engine/RemoteEngineService.cs`（新規） | `IEngineService` のパイプ版。命令を JSON にして送る |
    | `Editor/App.xaml.cs`（変更） | 起動の引数で、P/Invoke 版とパイプ版を切り替える |
    | `Editor.Tests/FakeEngine.cs`（新規） | テスト用の偽のエンジン。パイプの向こうで命令を受けるだけ |


<svg class="fig flow" viewBox="0 0 720 270" role="img" aria-label="ビューモデルは IEngineService だけを知る。実装は P/Invoke 版、C++/CLI 版、パイプ版の 3 つ"><defs><marker id="reA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">窓口は 1 つ、実装は 3 つ</text><rect x="16" y="104" width="150" height="50" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="91" y="129" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">ビューモデルなど</text><rect x="216" y="104" width="150" height="50" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="291" y="129" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">IEngineService</text><line x1="166" y1="129" x2="216" y2="129" stroke="currentColor" stroke-width="2" marker-end="url(#reA)"/><rect x="430" y="44" width="270" height="40" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="565" y="64" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">PInvokeEngineService（第 33 章）</text><rect x="430" y="104" width="270" height="40" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="565" y="124" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">ClrEngineService（第 34 章）</text><rect x="430" y="164" width="270" height="40" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="565" y="184" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">RemoteEngineService（この章）</text><line x1="366" y1="120" x2="430" y2="64" stroke="currentColor" stroke-width="2" marker-end="url(#reA)"/><line x1="366" y1="129" x2="430" y2="124" stroke="currentColor" stroke-width="2" marker-end="url(#reA)"/><line x1="366" y1="138" x2="430" y2="184" stroke="currentColor" stroke-width="2" marker-end="url(#reA)"/><text x="360" y="236" text-anchor="middle" style="font-size:12px;font-weight:400">上の 2 つは同じプロセスの DLL を呼び、一番下だけがパイプで別のプロセスに送る。</text><text x="360" y="254" text-anchor="middle" style="font-size:12px;font-weight:400">ビューモデルのコードは、どれが選ばれていても変わらない。</text></svg>

## 同期のインターフェースと非同期の通信

`IEngineService` のメソッドはすべて同期です。`SceneCreate(...)` は呼べば終わってから戻ってきます。一方、前の章の `EngineClient` は `await` する非同期です。この食い違いをどう埋めるかを最初に決めます。

選択肢は 2 つあります。1 つは `IEngineService` を `Task` を返す形に作り替えることです。呼ぶ側のコードがすべて `await` になります。第 40〜49 章のコードをほぼ全部書き直すことになります。

もう 1 つは、`RemoteEngineService` の中で、結果が返るまで待ってしまうことです。呼ぶ側から見ると、同期のメソッドのままです。この教材は、こちらを選びます。待ってよい理由は、第 38 章の約束にあります。エンジンへの命令はすべて描画スレッドが実行します。描画スレッドは画面とは関係のない専用のスレッドなので、ここが数十マイクロ秒待っても、画面は止まりません。

その代わり守る約束が 1 つ増えます。<strong>`RemoteEngineService` を UI スレッドから呼ばない</strong>ことです。UI スレッドから呼ぶと、エンジンが固まったとき、時間切れ（この章では 5 秒）までウィンドウが固まります。第 38 章の `IRenderLoop.Invoke` を UI スレッドから呼んでいる所（ピッキングの結果を聞く所など）は、描画スレッドで待つ間、UI スレッドも待ちます。普段は一瞬ですが、エンジンが固まったときの被害は、ここが一番大きくなります。第 48 章の `Task.Run(() => _loop.Invoke(...))` のようにバックグラウンドで待つ形に寄せておくと安全です。

`IEngineService` を非同期にしたほうが良くなるのは、エンジンとの会話が描画スレッドでは足りないほど増えたときです。そのときは、この章の `Call` を `await` に変える作業の範囲が、`IEngineService` を使う全部のコードに広がります。

## 命令の名前と形

`IEngineService` の 1 メソッドを 1 つの命令にします。命令の名前は C の API（`me_scene_create_object` など）の `me_` を外して、小文字の単語を `_` でつなぎます。引数は JSON の `args` に名前をつけて入れます。

| メソッド | `cmd` | `args` |
| --- | --- | --- |
| `Initialize` | `initialize` | `width`、`height` |
| `Resize` | `resize` | `width`、`height` |
| `Tick` | `tick` | `dt` |
| `FrameCount` | `get_frame_count` | なし（`result.count` に入る） |
| `SceneCreate` | `scene_create` | `id`、`parent`、`name` |
| `SceneDestroy` | `scene_destroy` | `id` |
| `SceneSetTransform` | `scene_set_transform` | `id`、`position`、`rotation`、`scale` |
| `SceneSetColor` | `scene_set_color` | `id`、`color` |

`SceneClear`、`SceneSetParent`、`SceneSetName` も同じ形で、表では省きました。ピッキング、ゲームの読み込み、Play モードの命令も、同じ決まりで増やします。

ベクトルは数の配列 `[x, y, z]` で送ります。`System.Numerics.Vector3` をそのまま JSON にすると、`{}`（空のオブジェクト）になってしまうからです。`Vector3` の `X`、`Y`、`Z` はプロパティではなくフィールドで、`System.Text.Json` は既定でフィールドを読みません。実際に、`JsonSerializer.Serialize(new Vector3(1, 2, 3))` が `{}` を返すことを確かめました。

## RemoteEngineService を書く

土台と最初の命令です。

```csharp title="Editor/Engine/RemoteEngineService.cs（新規）"
using System.Numerics;
using System.Text.Json;

namespace Editor.Engine;

// IEngineService の、パイプ版。命令を JSON にして、別プロセスのエンジンへ送る。
// 呼ぶのは描画スレッドだけ（第 38 章）。ここで待つので、UI スレッドから呼ばない。
public sealed class RemoteEngineService : IEngineService
{
    private static readonly TimeSpan CallTimeout = TimeSpan.FromSeconds(5);

    private readonly EngineClient _client;
    private bool _running;

    public RemoteEngineService(EngineClient client) => _client = client;

    public bool IsRunning => _running;

    public void Initialize(nint windowHandle, uint width, uint height)
    {
        if (_running) throw new InvalidOperationException("すでに初期化されています");
        Call("initialize", new { width, height });     // windowHandle は使わない（別プロセスの HWND には描けない）
        _running = true;
    }

    public void Resize(uint width, uint height) => Call("resize", new { width, height });

    public void Tick(float deltaSeconds) => Call("tick", new { dt = deltaSeconds });

    public ulong FrameCount => Call("get_frame_count").GetProperty("result").GetProperty("count").GetUInt64();
```

`Initialize` の `windowHandle` は受け取るだけで使いません。P/Invoke 版ではエンジンがこの `HWND` に直接描いていました。別プロセスのエンジンはエディタのウィンドウに描けません。絵をエディタに届ける方法は第 56 章で扱います。インターフェースのシグネチャを変えずに済ませたのは、呼ぶ側のコードを変えないためです。使わない引数が残るのはこの方式の代償です。

`Tick` は第 38 章の描画ループが毎フレーム呼びます。つまり、毎フレーム 1 回の往復です。前の章で測った約 35 μs は 60 fps の 1 フレーム（約 16.7 ms）の 0.2 % ほどで、問題になりません。

`_running` をこの中で持っているのにも理由があります。P/Invoke 版はネイティブのハンドルが有効かどうかで `IsRunning` を決めていました。パイプ版にはそのようなハンドルがないので、`Initialize` が成功したかどうかで決めます。エンジンが落ちたあとも `true` のままになる点は、第 57 章で直します。

次に、シーンの命令です。

```csharp title="Editor/Engine/RemoteEngineService.cs（続き）"
    public void SceneClear() => Call("scene_clear");

    public void SceneCreate(uint id, uint parentId, string name)
        => Call("scene_create", new { id, parent = parentId, name });

    public void SceneDestroy(uint id) => Call("scene_destroy", new { id });

    public void SceneSetParent(uint id, uint parentId) => Call("scene_set_parent", new { id, parent = parentId });

    public void SceneSetName(uint id, string name) => Call("scene_set_name", new { id, name });

    public void SceneSetTransform(uint id, Vector3 position, Vector3 rotationRadians, Vector3 scale)
        => Call("scene_set_transform", new
        {
            id,
            position = new[] { position.X, position.Y, position.Z },
            rotation = new[] { rotationRadians.X, rotationRadians.Y, rotationRadians.Z },
            scale = new[] { scale.X, scale.Y, scale.Z },
        });

    public void SceneSetColor(uint id, Vector4 color)
        => Call("scene_set_color", new { id, color = new[] { color.X, color.Y, color.Z, color.W } });
```

どのメソッドも `Call` を 1 行呼ぶだけです。P/Invoke 版で `NativeMethods.ThrowIfFailed(NativeMethods.me_scene_xxx(Handle, ...))` と書いていた所が、そのまま `Call("scene_xxx", new { ... })` に置き換わりました。匿名型 `new { id, parent = parentId, name }` の名前がそのまま JSON のキーになります。`id` や `name` のように、変数名とキーが同じなら、`id` だけで書けます。

最後に、片付けと待つ処理です。

```csharp title="Editor/Engine/RemoteEngineService.cs（続き）"
    public void Dispose()
    {
        if (!_running) return;
        _running = false;
        try { Call("shutdown"); }                       // エンジンに「終わり」を伝える。もう切れていても構わない
        catch (Exception e) when (e is EngineDisconnectedException or TimeoutException) { }
    }

    // 同期の窓口にするために、待つのはここだけ。GetResult は、例外を包まずにそのまま投げ直す
    private JsonElement Call(string cmd, object? args = null)
        => _client.RequestAsync(cmd, args, CallTimeout).GetAwaiter().GetResult();
}
```

`Call` がこの章の要です。`RequestAsync` が返す `Task` を `.GetAwaiter().GetResult()` で待ちます。`.Result` や `.Wait()` と違って、失敗したときに `AggregateException` に包まず、元の例外（`EngineCommandException`、`EngineDisconnectedException`、`TimeoutException`）をそのまま投げ直します。呼ぶ側が `catch (EngineCommandException)` と書けるのはこの性質のおかげです。

`Dispose` で `shutdown` を送るのはエンジンのプロセスに「これで終わり」と伝えるためです。エンジンが先に落ちていれば `EngineDisconnectedException` になるので、無視します。

P/Invoke 版の `EngineException` とこの章の `EngineCommandException` は、別の型です。ビューモデルが `catch (EngineException)` と書いていた所があれば、パイプ版では捕まりません。エンジンの失敗をまとめて受けたいなら、`EngineCommandException` も受けるか、両方に共通の親を作ってください。

## 起動の引数で切り替える

どちらの実装を使うかは起動の引数で決めます。`App.xaml.cs` の登録を次のように変えます。

```csharp title="App.xaml.cs（変更。コンパイルしていない）"
protected override void RegisterTypes(IContainerRegistry containerRegistry)
{
    // ……（ほかの登録はそのまま）

    if (Environment.GetCommandLineArgs().Contains("--remote-engine"))
    {
        // 接続は、エンジンのプロセスを起動したあとに行う（第 55 章）
        containerRegistry.RegisterInstance(new EngineClient());
        containerRegistry.RegisterSingleton<IEngineService, RemoteEngineService>();
    }
    else
    {
        containerRegistry.RegisterSingleton<IEngineService, PInvokeEngineService>();
    }
}
```

どちらでも `IEngineService` で解決されるので、ほかのクラスは何も変わりません。ビューモデルの側から見るとエンジンが同じプロセスにいるのか別のプロセスにいるのかは分かりません。

この切り替えはしばらく残しておくのが安全です。別プロセスの構成で調べにくい不具合が出たとき、同じ操作を P/Invoke 版で試して、「通信が原因か、エンジンが原因か」を切り分けられます。

## 偽のエンジンでテストする

エンジンのプロセス（第 55 章）がなくても、`RemoteEngineService` は動かせます。パイプの向こうに、命令を受けてシーンを辞書で覚えるだけの、偽のエンジンを置きます。`Editor.Tests` に入れて `dotnet test` で動かすことを想定したテスト用のクラスです。

```csharp title="Editor.Tests/FakeEngine.cs（新規。抜粋）"
public sealed class FakeEngine
{
    private readonly record struct Obj(uint Parent, string Name, float[] Position);

    private readonly Dictionary<uint, Obj> _scene = new();
    private ulong _frames;
    private bool _initialized;

    public int ObjectCount => _scene.Count;

    // 1 つの接続を受けて、shutdown が来るか切れるまで、要求を処理する
    public async Task RunAsync(string pipeName) { /* パイプを作り、長さ + JSON を読んで Handle に渡し、返事を書く */ }

    private string Handle(JsonElement req)
    {
        int id = req.GetProperty("id").GetInt32();
        string cmd = req.GetProperty("cmd").GetString()!;
        JsonElement a = req.TryGetProperty("args", out var x) ? x : default;
        try
        {
            string result = "null";
            switch (cmd)
            {
                case "initialize":
                    if (_initialized) throw new InvalidOperationException("already initialized");
                    _initialized = true;
                    break;
                case "tick": _frames++; break;
                case "get_frame_count": result = "{\"count\":" + _frames + "}"; break;
                case "scene_create":
                {
                    uint oid = a.GetProperty("id").GetUInt32();
                    if (_scene.ContainsKey(oid)) throw new InvalidOperationException($"duplicate id: {oid}");
                    _scene[oid] = new Obj(a.GetProperty("parent").GetUInt32(), a.GetProperty("name").GetString()!, new float[3]);
                    break;
                }
                // scene_destroy、scene_set_transform なども同じ形。未知の cmd は、例外にする
                default: throw new InvalidOperationException($"unknown cmd: {cmd}");
            }
            return "{\"id\":" + id + ",\"ok\":true,\"result\":" + result + "}";
        }
        catch (Exception e)
        {
            return JsonSerializer.Serialize(new { id, ok = false, error = e.Message });   // 失敗は ok:false で返す
        }
    }
}
```

`Handle` の作りは前の章の C++ の `HandleRequest` と同じです。例外を捕まえて `ok: false` の返事にします。これが本物のエンジンも守る約束です。偽のエンジンが同じ約束で動くので、`RemoteEngineService` の失敗の扱いを本物のエンジンなしに確かめられます。

テストの本体は描画スレッドを真似た普通の `Thread` から `RemoteEngineService` を同期で使います。

```csharp title="確認用のコンソール（Editor には入れない）"
var fake = new FakeEngine();
var server = Task.Run(() => fake.RunAsync("MiniEngineFake"));

await using var client = new EngineClient("MiniEngineFake");
await client.ConnectAsync();

var thread = new Thread(() =>
{
    using IEngineService engine = new RemoteEngineService(client);
    engine.Initialize(0, 1280, 720);
    engine.SceneCreate(1, 0, "Cube");
    engine.SceneCreate(2, 1, "Child");
    engine.SceneSetTransform(1, new Vector3(1, 2, 3), Vector3.Zero, Vector3.One);
    for (int i = 0; i < 3; i++) engine.Tick(1f / 60f);
    Console.WriteLine($"IsRunning={engine.IsRunning} FrameCount={engine.FrameCount}");

    try { engine.SceneSetTransform(99, Vector3.Zero, Vector3.Zero, Vector3.One); }
    catch (EngineCommandException e) { Console.WriteLine("unknown id -> EngineCommandException: " + e.Message); }

    try { engine.SceneCreate(1, 0, "Dup"); }
    catch (EngineCommandException e) { Console.WriteLine("duplicate -> EngineCommandException: " + e.Message); }

    try { engine.Initialize(0, 1, 1); }
    catch (InvalidOperationException e) { Console.WriteLine("re-init -> InvalidOperationException: " + e.Message); }
});
thread.Start();
thread.Join();
await server;
Console.WriteLine($"fake engine: objects={fake.ObjectCount} position(1)=({string.Join(",", fake.PositionOf(1))})");
```

```text title="実行結果"
IsRunning=True FrameCount=3
unknown id -> EngineCommandException: unknown object: 99
duplicate -> EngineCommandException: duplicate id: 1
re-init -> InvalidOperationException: すでに初期化されています
fake engine: objects=2 position(1)=(1,2,3)
```

上から読みます。`Initialize`、`SceneCreate`、`SceneSetTransform`、`Tick` を呼んだあと、`FrameCount` が `3` なのは、`Tick` を 3 回呼んで偽のエンジンが数えたからです。同じ ID で 2 回作ろうとすると、偽のエンジンの `ok: false` が `EngineCommandException` になって届きます。最後の `engine.Initialize` は通信に出る前に `RemoteEngineService` の中で止まります。偽のエンジンが覚えた位置が `(1,2,3)` なのは、ベクトルが配列で正しく届いた証拠です。

この確認は `RemoteEngineService`、`EngineClient`、偽のエンジンを、.NET 8 向けのコンソール アプリに入れて、実際に動かして確かめました。`App.xaml.cs` の登録はコンパイルしていません。

## 大量の命令はまとめて送る

このやり方で気をつけたいのは、命令の数です。`SceneEngineSync`（第 40 章）は物を作るたびに、作成、変換、色の 3 つの命令を送ります。往復が 1 回あたり約 35 μs なので、1 つの物は約 0.1 ms です。10 個なら 1 ms で気づきません。

しかし、10,000 個の物があるシーンを読み込む場面では、3 万回の往復になり約 1 秒かかります。P/Invoke 版ではこのコストがほとんどありませんでした。ここが別プロセスにした代償のいちばん分かりやすい姿です。

対策は、1 つのメッセージに複数の命令を入れることです。たとえば、`{"cmd": "batch", "args": {"commands": [ {...}, {...} ]}}` のように命令の配列を 1 回で送り、エンジンが順に実行して、結果の配列を返します。往復は 1 回で済みます。この章では作りません。シーンの読み込み（第 45 章）のように命令が大量に出る所だけに、あとから足せるようにしてあります。

## よくあるミス

??? failure "ベクトルを送ると、エンジンが 0 を受け取る"
    `Vector3` をそのまま匿名型に入れていませんか。`System.Text.Json` は `Vector3` の `X`、`Y`、`Z` を（フィールドなので）読まず、`{}` を送ります。エンジンの側では、キーが見つからず、0 になったり、失敗になったりします。`new[] { v.X, v.Y, v.Z }` の配列にして送ります。

??? failure "ピッキングや保存のたびにウィンドウが数秒固まる"
    `IRenderLoop.Invoke` を UI スレッドから呼んでいて、エンジンの返事を待っています。エンジンが忙しいか固まっていると、時間切れまで UI スレッドが止まります。`Task.Run(() => _loop.Invoke(...))` でバックグラウンドに出してください。

??? failure "UI スレッドから RequestAsync(...).Result で待つと、固まって戻らない"
    `EngineClient` の `await` に `ConfigureAwait(false)` が付いていれば、普通は起きません。付け忘れた `await` が 1 つでもあると、続きが UI スレッドに戻ろうとして、待っている UI スレッドと行き違いになります。通信の部品の中の `await` にはすべて付けてください。

??? failure "再起動したエンジンに同じ ID の物を作ろうとして失敗する"
    エンジンを再起動しても、エディタの `SceneDocument` は残っています。再起動したエンジンにシーンを送り直す前に `SceneClear` を呼ぶか、新しいエンジンが空であることを確かめてください。この手順は第 57 章でまとめます。

## この章のまとめ

- `IEngineService` の実装を 1 つ足すだけで、エディタの残りのコードを変えずにエンジンを別のプロセスに出せる。
- 同期のインターフェースのまま `RemoteEngineService` の中で結果を待つ。待ってよいのは描画スレッドだけで、UI スレッドから呼ばない。
- 命令は `cmd` と `args` の JSON。ベクトルは `Vector3` をそのまま使わず、数の配列にする。
- エンジンの失敗は `EngineCommandException`、消滅は `EngineDisconnectedException` で P/Invoke 版の `EngineException` とは別の型になる。
- 命令が大量に出る場面は `batch` のようにまとめて送る形に変える。

次の章ではエンジンの側、つまり `EngineHost.exe` を作ります。
