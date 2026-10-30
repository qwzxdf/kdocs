---
title: 第 33 章 P/Invoke で C# から呼ぶ
tags:
  - C#連携
---

# 第 33 章 P/Invoke で C# から呼ぶ

第 32 章で作った `EngineApi.dll` の C の関数を C# から呼びます。宣言の書き方、構造体や文字列の受け渡し、ハンドルを安全に持つ `SafeHandle`、C++ から C# を呼ぶコールバックと、順番に進めます。この章の終わりには、ビューモデルが使える `IEngineService` ができあがります。

!!! info "このページを読む前に"
    - [第 32 章 EngineApi：C の入口を作る](32-engine-api.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## P/Invoke は、宣言をもう一度書く仕組み

P/Invoke は、「C の関数の宣言を C# の側にもう一度書く」という仕組みです。

```c
/* C の宣言（EngineApi.h） */
ME_API int32_t me_get_api_version(void);
```

```csharp
// C# の宣言
[LibraryImport("EngineApi.dll")]
internal static partial int me_get_api_version();
```

C# のコンパイラーは、C のヘッダーを読めません。だから、C# 側の宣言が C 側と食い違っていても、ビルドは通ります。食い違いは、実行時にクラッシュや値の化けとして現れます。これが P/Invoke でいちばん気をつけるところなので、宣言を書くときは、C のヘッダーと一行ずつ見比べるようにしてください。

呼び出す瞬間、CLR は裏でいくつか仕事をしています。引数を C の形に変換し（マーシャリング）、GC が C# のメモリを動かさないように必要なものを固定し、実行をマネージドからネイティブに切り替え、戻り値を C# の形に戻します。整数や `float`、ポインターのような、そのまま渡せる型だけなら変換が要らず、1 回の呼び出しは数十ナノ秒で済みます。1 フレームに何十回呼んでも、問題にはなりません。

## 準備：unsafe を許可する

`Editor.csproj` に、`AllowUnsafeBlocks` を足します。

```xml
<PropertyGroup>
  <AllowUnsafeBlocks>true</AllowUnsafeBlocks>
</PropertyGroup>
```

`unsafe` は、C# でポインターを直接使うための区画で、コンパイラーが型の安全の保証を一部あきらめます。`[LibraryImport]` が生成するコードが `unsafe` を使うので、この設定が必要になります。

また、`EngineApi.dll` と `Engine.dll` は、第 1 章の設定で `Editor.exe` と同じフォルダーに出力されます。この章では、DLL が `Editor.exe` の隣にあることを前提にしています。

## 最初の関数を呼ぶ

`Editor` に `Interop` フォルダーを作って、`NativeMethods.cs` を書きます。

```csharp title="Engine/NativeMethods.cs"
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace Editor.Engine;

// EngineApi.dll の C の関数の宣言。
// C のヘッダー（EngineApi.h）と、一行ずつ見比べて書くこと。
internal static partial class NativeMethods
{
    private const string Dll = "EngineApi.dll";

    [LibraryImport(Dll)]
    [UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
    internal static partial int me_get_api_version();
}
```

使うときは、普通の関数のように呼べます。

```csharp
int version = NativeMethods.me_get_api_version();
```

`[LibraryImport(Dll)]` は、「この関数の実体は、`Dll`（`EngineApi.dll`）の中にあります」という属性です。関数に本体がなく `partial` だけが付いているのは、本体をコンパイラーが自動で生成して埋めてくれるからです。生成されるのは、引数の変換とネイティブ呼び出しのコードで、クラスにも `partial` を付ける必要があります。

関数の名前は、初期状態では C# のメソッド名と同じ名前の関数を DLL から探します。C の名前と一致させてください。違う名前にしたいときは、`EntryPoint = "..."` で指定できます。`[UnmanagedCallConv]` は呼び出し規約の指定です。x64 では 1 種類しかないので省略しても動きますが、書く習慣にしておきます。

型は大きさで対応させます。C の `int32_t` は、C# の `int` です。

!!! note "古い DllImport との違い"
    昔からある `[DllImport]` でも、同じことができます。違いは、`[DllImport]` が変換のコードを実行時に作るのに対して、`[LibraryImport]` はコンパイル時に作る点です。後者のほうが起動が速く、生成されたコードを読んで確かめることもできます。この教材は `[LibraryImport]` を使います。

### 動かして確かめる

`App.xaml.cs` の `OnInitialized`（Prism が準備を終えたあとに呼ばれる）に仮のコードを足します。

```csharp
protected override void OnInitialized()
{
    base.OnInitialized();
    int version = Interop.NativeMethods.me_get_api_version();
    System.Diagnostics.Debug.WriteLine($"EngineApi version = {version}");
}
```

デバッグ実行して、出力ウィンドウに `EngineApi version = 1` が出れば成功です。`DllNotFoundException` が出たら、`bin\x64\Debug\` に `EngineApi.dll` と `Engine.dll` が両方あるかを確かめてください。それでも直らないときは、第 35 章に原因の探し方があります。

## エラー コードを例外に変える

`me_get_api_version` 以外の関数は、`MeResult` を返します。C# らしく使うために、エラー コードを例外に変換する仕組みを作ります。

まず、結果コードの列挙型です。

```csharp title="Engine/MeResult.cs"
namespace Editor.Engine;

// EngineApi.h の ME_* と同じ値にする
internal enum MeResult : int
{
    Ok = 0,
    InvalidArgument = 1,
    InitFailed = 2,
    NotFound = 3,
    Exception = 4,
    InvalidState = 5,
}
```

`: int` と土台の型を書いているのは、C の `int32_t` と大きさをそろえるためです。数字も C 側と同じにします。順番を変えるときは、両方を変えます。

次に、エンジンの失敗を表す例外クラスです。

```csharp title="Engine/EngineException.cs"
namespace Editor.Engine;

public class EngineException : Exception
{
    internal MeResult Result { get; }

    internal EngineException(MeResult result, string message)
        : base(message)
    {
        Result = result;
    }
}
```

`Exception` を継承した自作の例外です。こうしておくと、`catch (EngineException e)` で、エンジンの失敗だけを捕まえられます。

最後に、`NativeMethods` に `me_get_last_error` の宣言と、失敗を例外にする関数を足します。

```csharp
[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial nint me_get_last_error();

// 失敗なら例外にする
internal static void ThrowIfFailed(MeResult result)
{
    if (result == MeResult.Ok) return;
    nint pointer = me_get_last_error();
    string message = Marshal.PtrToStringUTF8(pointer) ?? "(理由なし)";
    throw new EngineException(result, $"{result}: {message}");
}
```

ここで `me_get_last_error` の戻り値を `string` ではなく `nint` で受けているのには、理由があります。`const char*` を `string` で受けると、CLR がそのポインターを解放しようとすることがあります。ところが、このポインターは C++ 側が持っている文字列を指しているので、C# が解放してはいけません。持ち主を取り違えないために、いったん `nint`（ポインターと同じ大きさの整数）で受けて、`Marshal.PtrToStringUTF8` でコピーして `string` に変換しています。

## 構造体と出力引数

`me_engine_create` は、構造体を入力で受け取り、ハンドルを出力引数で返します。

```c
ME_API MeResult me_engine_create(const MeEngineDesc* desc, MeEngine** out_engine);
```

構造体は、C の定義と同じ並びで宣言します。

```csharp title="Engine/MeEngineDesc.cs"
using System.Runtime.InteropServices;

namespace Editor.Engine;

// EngineApi.h の MeEngineDesc と、同じ並びにする
[StructLayout(LayoutKind.Sequential)]
internal struct MeEngineDesc
{
    public nint Window;     // void*    window
    public uint Width;      // uint32_t width
    public uint Height;     // uint32_t height
}
```

`[StructLayout(LayoutKind.Sequential)]` は、フィールドを宣言した順に並べる指定です。構造体には初期状態でも付いていますが、C の構造体と並びを合わせたいことを示すために、明示しておきます。C の構造体は、フィールドの大きさに合わせてパディング（隙間）を入れますが、C# の `Sequential` も同じ規則で隙間を入れるので、同じ並びで宣言すれば大きさも合います。この構造体は、8 バイトの `nint` に 4 バイトの `uint` が 2 つで、16 バイトです。

!!! warning "構造体のずれは、ビルドで見つからない"
    C 側と C# 側のどちらかでフィールドを足したり順番を変えたりすると、ビルドは通ったまま値が化けます。せめて大きさだけでも両側で固定しておきましょう。C 側に `static_assert(sizeof(MeEngineDesc) == 16)`、C# 側に `Debug.Assert(Marshal.SizeOf<MeEngineDesc>() == 16)` を書いておくと、ずれた瞬間に気づけます。

関数の宣言は、こうなります。

```csharp
[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_engine_create(in MeEngineDesc desc, out nint engine);
```

`in` は「読み取り専用の参照渡し」で、C の `const MeEngineDesc*` に当たります。`out` は「呼ばれた側が必ず値を書く参照渡し」で、C の `MeEngine**` に当たります。入出力の両方に使う `ref` もあります。呼ぶ側は次のように書きます。

```csharp
var desc = new MeEngineDesc { Window = hwnd, Width = 1280, Height = 720 };
MeResult result = NativeMethods.me_engine_create(in desc, out nint engine);
NativeMethods.ThrowIfFailed(result);
```

## ハンドルを SafeHandle で包む

`out nint engine` で受け取ったハンドルは、ただの整数です。これを `Editor` のあちこちに持ち回ると、解放し忘れ、二重に解放、解放したあとで使う、といった間違いが起きます。C++ の `unique_ptr` の役目を C# では `SafeHandle` が担います。

```csharp title="Engine/EngineHandle.cs"
using System.Runtime.InteropServices;

namespace Editor.Engine;

// MeEngine* を安全に持つ入れ物。Dispose されると me_engine_destroy を呼ぶ。
internal sealed class EngineHandle : SafeHandle
{
    // マーシャリングのために、引数なしのコンストラクターが必要
    public EngineHandle() : base(nint.Zero, ownsHandle: true)
    {
    }

    public override bool IsInvalid => handle == nint.Zero;

    protected override bool ReleaseHandle()
    {
        NativeMethods.me_engine_destroy(handle);
        return true;
    }
}
```

`SafeHandle` は、`Dispose()` か GC による破棄のときに、`ReleaseHandle()` がちょうど 1 回だけ呼ばれることを保証してくれます。`handle` は、持っているポインターの値です。`ownsHandle: true` は、「このオブジェクトが解放の責任を持つ」という意味です。

関数の宣言を `nint` から `EngineHandle` に変えます。

```csharp
[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_engine_create(in MeEngineDesc desc, out EngineHandle engine);

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial void me_engine_destroy(nint engine);

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_engine_resize(EngineHandle engine, uint width, uint height);

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_engine_tick(EngineHandle engine, float deltaSeconds);

[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_engine_get_frame_count(EngineHandle engine, out ulong count);
```

`out EngineHandle engine` と書くと、呼び出しから戻るときに、マーシャリングが `EngineHandle` のオブジェクトを自動で作って、ハンドルの値を入れてくれます。そのために、引数なしのコンストラクターが必要でした。`me_engine_destroy` だけ `nint` なのは、`ReleaseHandle` の中から呼ぶ関数で、`EngineHandle` が使えないからです。

`SafeHandle` を引数に取る関数は、呼び出している間、ハンドルの解放を遅らせてくれるという利点もあります。呼び出しの最中に別のスレッドが `Dispose` しても、クラッシュしません。

解放し忘れても、GC がいつか `ReleaseHandle()` を呼んでくれるので、完全なリークにはなりません。ただし、エンジンの破棄は GPU を使う処理なので、`Dispose` で明示的に行うのが正しい使い方です。

## IEngineService を作る

ビューモデルが `NativeMethods` や `EngineHandle` を直接触らなくて済むように、窓口のインターフェースを作ります。次の章の C++/CLI 版も、同じインターフェースを実装します。

```csharp title="Engine/IEngineService.cs"
namespace Editor.Engine;

// エンジンへの窓口。ビューモデルは、これだけを知る。
public interface IEngineService : IDisposable
{
    bool IsRunning { get; }

    // 描画先のウィンドウ（HWND）を渡して、エンジンを作る
    void Initialize(nint windowHandle, uint width, uint height);

    void Resize(uint width, uint height);
    void Tick(float deltaSeconds);
    ulong FrameCount { get; }
}
```

```csharp title="Engine/PInvokeEngineService.cs"
namespace Editor.Engine;

public sealed class PInvokeEngineService : IEngineService
{
    private EngineHandle? _handle;

    public bool IsRunning => _handle is { IsInvalid: false };

    public void Initialize(nint windowHandle, uint width, uint height)
    {
        if (IsRunning) throw new InvalidOperationException("すでに初期化されています");

        var desc = new MeEngineDesc { Window = windowHandle, Width = width, Height = height };
        NativeMethods.ThrowIfFailed(NativeMethods.me_engine_create(in desc, out var handle));
        _handle = handle;
    }

    public void Resize(uint width, uint height)
    {
        NativeMethods.ThrowIfFailed(NativeMethods.me_engine_resize(Handle, width, height));
    }

    public void Tick(float deltaSeconds)
    {
        NativeMethods.ThrowIfFailed(NativeMethods.me_engine_tick(Handle, deltaSeconds));
    }

    public ulong FrameCount
    {
        get
        {
            NativeMethods.ThrowIfFailed(NativeMethods.me_engine_get_frame_count(Handle, out var count));
            return count;
        }
    }

    public void Dispose()
    {
        _handle?.Dispose();
        _handle = null;
    }

    // 初期化前に呼ばれたら、分かりやすい例外にする
    private EngineHandle Handle =>
        _handle is { IsInvalid: false } h ? h : throw new InvalidOperationException("エンジンが初期化されていません");
}
```

目新しい書き方が 2 つ出てきました。`_handle is { IsInvalid: false }` は「`_handle` が `null` ではなく、かつ `IsInvalid` が `false` なら真」というパターンです。最後の `Handle` プロパティの `is { ... } h ? h : throw ...` は、パターンに合えばその値を `h` に取り出し、合わなければ例外を投げます。`throw` は式としても書けるので、こうして 1 行で書けます。

毎回 `Handle` を通す理由は、`null` の確認を書き忘れて `NullReferenceException` になるのを防ぐためです。初期化前に呼ばれたときは、「初期化されていません」と分かりやすい例外になります。

`App.xaml.cs` の `RegisterTypes` で、登録します。

```csharp
containerRegistry.RegisterSingleton<IEngineService, PInvokeEngineService>();
```

## ログのコールバックを受け取る

ここまでは C# から C++ を呼ぶ向きでした。逆向きの連携も作ります。エンジンの `LogInfo` が呼ばれたら、エディタのログ タブに出したいのです。

C 側の宣言はこうでした。

```c
typedef void (*MeLogCallback)(MeLogLevel level, const char* message, void* user_data);
ME_API void me_set_log_callback(MeLogCallback callback, void* user_data);
```

C# から、関数ポインターを渡す必要があります。方法は 2 つあって、おすすめは `[UnmanagedCallersOnly]` を使うほうです。

### 方法 A：UnmanagedCallersOnly（おすすめ）

C# の `static` なメソッドに `[UnmanagedCallersOnly]` を付けると、C から直接呼べる関数になり、そのアドレスを取れます。

```csharp title="Engine/NativeLog.cs"
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace Editor.Engine;

internal static unsafe class NativeLog
{
    // ログを受け取る先。UI スレッド以外から呼ばれるので、スレッドセーフなものにする。
    private static Action<int, string>? s_sink;

    // C から直接呼ばれる。例外を外に出してはいけない。
    [UnmanagedCallersOnly(CallConvs = new[] { typeof(CallConvCdecl) })]
    private static void OnLog(int level, byte* message, nint userData)
    {
        try
        {
            string text = Marshal.PtrToStringUTF8((nint)message) ?? "";
            s_sink?.Invoke(level, text);
        }
        catch
        {
            // C++ の呼び出しスタックへ例外を通さない
        }
    }

    public static void Install(Action<int, string> sink)
    {
        s_sink = sink;
        NativeMethods.me_set_log_callback(
            (delegate* unmanaged[Cdecl]<int, byte*, nint, void>)&OnLog, nint.Zero);
    }

    public static void Uninstall()
    {
        NativeMethods.me_set_log_callback(null, nint.Zero);
        s_sink = null;
    }
}
```

`NativeMethods` の宣言は、関数ポインターを受け取る形にします。

```csharp
[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static unsafe partial void me_set_log_callback(
    delegate* unmanaged[Cdecl]<int, byte*, nint, void> callback, nint userData);
```

見慣れない書き方が多いので、ひとつずつ見ます。

- `delegate* unmanaged[Cdecl]<int, byte*, nint, void>` が関数ポインターの型です。最後の型が戻り値で、C の `void (*)(int, const char*, void*)` にそのまま対応します。
- `byte* message` は `unsafe` なポインターで、C の `const char*` に当たります。
- `&OnLog` はメソッドのアドレスを取る式で、`[UnmanagedCallersOnly]` が付いたメソッドにだけ使えます。
- `catch { }` が空なのは意図的です。C++ のスタックの中に C# の例外が通り抜けると、クラッシュするからです。例外はここで握りつぶします。
- `static` フィールドの名前を `s_` で始めるのは、C# の慣習です。
- `null` を渡すと C の `NULL` になり、登録が解除されます。

この方法が優れているのは、関数のアドレスが固定されていることです。GC に動かされたり回収されたりしないので、次の方法のような延命の工夫が要りません。

### 方法 B：デリゲート

`unsafe` を使いたくないなら、デリゲートを渡す方法もあります。

```csharp
[UnmanagedFunctionPointer(CallingConvention.Cdecl)]
internal delegate void LogCallbackDelegate(int level, nint message, nint userData);

[LibraryImport(Dll)]
internal static partial void me_set_log_callback(LogCallbackDelegate? callback, nint userData);
```

```csharp
private static LogCallbackDelegate? s_callback;   // 必ず static フィールドで持っておく

public static void Install(Action<int, string> sink)
{
    s_callback = (level, message, user) => sink(level, Marshal.PtrToStringUTF8(message) ?? "");
    NativeMethods.me_set_log_callback(s_callback, nint.Zero);
}
```

こちらには落とし穴があります。C++ に渡したデリゲートを C# 側のどこにも保持していないと、GC に回収されてしまい、あとで C++ が呼んだときにクラッシュします。`static` フィールドに入れて、登録を解除するまで持ち続けてください。

### ログをエディタのログに流す

サービスがそろったあとの `App.xaml.cs` で、結び付けます。

```csharp
protected override void OnInitialized()
{
    base.OnInitialized();

    int version = Interop.NativeMethods.me_get_api_version();
    var log = Container.Resolve<ILogService>();

    // C++ のログをエディタのログへ
    Interop.NativeLog.Install((level, message) =>
    {
        switch (level)
        {
            case 0: log.Info(message); break;
            case 1: log.Warning(message); break;
            default: log.Error(message); break;
        }
    });
    log.Info($"EngineApi version {version}");
}

protected override void OnExit(ExitEventArgs e)
{
    Interop.NativeLog.Uninstall();
    base.OnExit(e);
}
```

`OnExit` で登録を解除しているのは、アプリが終わったあとに C++ がコールバックを呼ばないようにするためです。`LogService` は、別のスレッドから呼ばれても安全に作ってあるので（第 24 章）、エンジンが別のスレッドからログを出しても、UI スレッドに回して追加されます。

## 文字列を渡す関数の書き方

この先、アセットのパスのように、C# の文字列を C++ に渡す場面が出てきます。ここで書き方をまとめておきます。

```c
ME_API MeResult me_asset_load(MeEngine* engine, const char* path_utf8);
```

```csharp
[LibraryImport(Dll, StringMarshalling = StringMarshalling.Utf8)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_asset_load(EngineHandle engine, string path);
```

`StringMarshalling.Utf8` を指定すると、`string` を UTF-8 の `char*` に変換して渡してくれます。変換用の一時的なバッファーは、呼び出しの間だけ有効で、戻れば解放されます。だから C++ 側は、受け取った `const char*` を呼び出しの外に持ち出してはいけません（保存したいなら、コピーを取ります）。Windows API を呼ぶときは `Utf16` を使います。

逆に、C++ が文字列を書き込んで返したいときは、C# がバッファーを用意して渡します。

```c
/* buffer に UTF-8 で書く。buffer_size は終端 NUL を含む大きさ。必要な大きさを out_required に返す。 */
ME_API MeResult me_object_get_name(const MeEngine* engine, uint32_t id, char* buffer, uint32_t buffer_size, uint32_t* out_required);
```

```csharp
[LibraryImport(Dll)]
internal static unsafe partial MeResult me_object_get_name(
    EngineHandle engine, uint id, byte* buffer, uint bufferSize, out uint required);
```

```csharp
public string GetName(uint id)
{
    unsafe
    {
        byte* buffer = stackalloc byte[256];                        // スタックに 256 バイト
        NativeMethods.ThrowIfFailed(NativeMethods.me_object_get_name(Handle, id, buffer, 256, out _));
        return Marshal.PtrToStringUTF8((nint)buffer) ?? "";
    }
}
```

`stackalloc` は、スタック上に配列を確保します。関数を抜けると自動で消えるので、GC の対象になりません。`out _` は、出力引数を受け取らずに捨てる書き方です。この例は、第 40 章のシーンの API で、実際に使います。

## 失敗する経路も動かしてみる

最後に、エラーの経路が通っているかを確かめます。`MainWindowViewModel` のコンストラクターに `IEngineService` と `ILogService` を一時的に足して、わざと失敗する呼び出しを書きます（確かめたら消します）。

```csharp title="実験：わざと失敗させる（確かめたら消す）"
public DelegateCommand TestErrorCommand { get; }

public MainWindowViewModel(IEngineService engine, ILogService log /* ほかの引数は前のとおり */)
{
    TestErrorCommand = new DelegateCommand(() =>
    {
        try
        {
            // ウィンドウ ハンドルが null なので、InvalidArgument になるはず
            engine.Initialize(nint.Zero, 640, 480);
        }
        catch (Interop.EngineException e)
        {
            log.Error(e.Message);
        }
    });
}
```

ボタンを押すと、ログにこう出ます。

```text
InvalidArgument: window が null、または大きさが 0
```

C++ 側で `SetLastError` した文字列がそのまま C# の例外のメッセージになりました。エラー コードを返して、理由を別の関数で取る、という経路が通っています。

確かめたいのは次の点です。

- 起動すると、ログに `EngineApi version 1` が出る。
- テスト ボタンを押すと、上のメッセージがログに出る。アプリはクラッシュしない。
- 終了するときに、例外が出ない。

??? failure "`DllNotFoundException`（`Unable to load DLL 'EngineApi.dll'`）"
    DLL が `Editor.exe` の隣にない、依存する `Engine.dll` がない、あるいはビット数が違います。調べ方は第 35 章にあります。

??? failure "`EntryPointNotFoundException`"
    DLL の中にその名前の関数がありません。C# 側の名前のタイプミス、`extern "C"` の付け忘れ、または `dumpbin /exports` に出ていないことが原因です。

??? failure "値が化ける、ランダムにクラッシュする"
    構造体のフィールドの型や順番が C 側と違うか、`bool` を使っているか、`long` を使っています（C# の `long` は 64 ビット）。宣言を C のヘッダーと見比べてください。

??? failure "ログのコールバックで、突然クラッシュする"
    デリゲートを `static` に持っていなくて GC に回収されたか、コールバックの中から例外が漏れています。方法 A にすると、前者は起きません。

??? failure "`CS0227`（unsafe コードは `/unsafe` を付けてコンパイルしたときだけ使える）"
    `.csproj` に `<AllowUnsafeBlocks>true</AllowUnsafeBlocks>` を足していません。

??? failure "終了するときにクラッシュする"
    終了の途中で、C++ が、すでに片付けられた C# のコールバックを呼んでいます。`OnExit` で `NativeLog.Uninstall()` を呼びます。

## この章のまとめ

- 宣言は `[LibraryImport]` の `partial` メソッドで書く。C のヘッダーと一行ずつ見比べる。
- 渡せる型は、そのまま渡せる型だけ。`bool` と C++ の `long` は避ける。
- 構造体は `[StructLayout(Sequential)]` で並びを合わせ、大きさを両側で確かめておく。
- 出力は `out` / `in` / `ref`、文字列は `StringMarshalling.Utf8`。
- ハンドルは `SafeHandle` で包んで、`Dispose` で解放する。
- エラー コードは例外に変換する。コールバックは `[UnmanagedCallersOnly]` で、例外を外に漏らさない。

次の章では、同じ `IEngineService` を C++/CLI で実装して、P/Invoke との手間の違いを比べます。

[第 34 章 C++/CLI で橋を作る](34-cpp-cli.md) へ進みます。
