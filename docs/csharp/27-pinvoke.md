---
title: 第 27 章 P/Invoke で C# から呼ぶ
tags:
  - C#連携
---

# 第 27 章 P/Invoke で C# から呼ぶ

この章では、第 26 章で作った `EngineApi.dll` の C の関数を、C# から呼びます。P/Invoke の宣言の書き方、構造体や文字列の受け渡し、ハンドルの安全な管理（`SafeHandle`）、C++ から C# を呼ぶコールバックを、一つずつ学びます。章の終わりには、ビューモデルが使える `IEngineService` ができます。

## この章の考え方

P/Invoke は、「<strong>C# の側に、C の関数の宣言をもう一度書く</strong>」仕組みです。

```c
/* C の宣言（EngineApi.h） */
ME_API int32_t me_get_api_version(void);
```

```csharp
// C# の宣言
[LibraryImport("EngineApi.dll")]
internal static partial int me_get_api_version();
```

C# のコンパイラーは、C の宣言を読めません。そのため、<strong>C# 側の宣言が、C 側と食い違っていても、ビルドは通ります</strong>。食い違いは、実行時に、<strong>クラッシュや、値の化け</strong>として現れます。これが P/Invoke の最大の注意点です。宣言を書くときは、C のヘッダーと、一行ずつ見比べます。

呼び出しの瞬間に、CLR は次の仕事をします。

1. 引数を、C の形に<strong>変換</strong>する（マーシャリング）。
2. GC が、C# のメモリを動かさないよう、必要な物を<strong>固定</strong>（ピン留め）する。
3. 実行を、マネージドからネイティブに<strong>切り替える</strong>。
4. 戻り値を、C# の形に変換して返す。

blittable な型（整数、`float`、ポインター）だけなら、1 の変換が要らず、呼び出しの負担は、<strong>数十ナノ秒</strong>です。1 フレームに数十回呼んでも、問題になりません。

## この章のゴール

- `[LibraryImport]` で、C の関数を宣言できる。
- 構造体、出力引数、文字列を、正しく受け渡せる。
- エラー コードを、C# の例外に変換できる。
- `SafeHandle` で、エンジンのハンドルを、安全に管理できる。
- C++ からのログのコールバックを、受け取れる。
- `IEngineService` を作り、DI で配れる。

## 手順 1：プロジェクトの設定

`Editor.csproj` に、`AllowUnsafeBlocks` を足します。

```xml
<PropertyGroup>
  <AllowUnsafeBlocks>true</AllowUnsafeBlocks>
</PropertyGroup>
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `unsafe` | C# で、ポインターを直接使うための区画。コンパイラーが、型の安全の保証を、一部あきらめる |
| `AllowUnsafeBlocks` | `unsafe` を許可するプロジェクト設定。`[LibraryImport]` が生成するコードが、`unsafe` を使うので必要 |

`EngineApi.dll` と `Engine.dll` は、第 1 章の設定で、`Editor.exe` と同じフォルダーに出力されます。この章で、<strong>DLL を `Editor.exe` の隣に置く</strong>という前提を使います。

## 手順 2：最初の関数を呼ぶ

`Editor` に、`Interop` フォルダーを作り、`NativeMethods.cs` を書きます。

```csharp
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace Editor.Interop;

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

使うときは、普通の関数のように呼びます。

```csharp
int version = NativeMethods.me_get_api_version();
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `[LibraryImport(Dll)]` | 「この関数の実体は、`Dll`（`EngineApi.dll`）にある」という<strong>属性</strong>。.NET 7 以降の、推奨される方式 |
| `partial` メソッド | <strong>本体を書かない宣言</strong>。コンパイル時に、ジェネレーター（コード自動生成の仕組み）が、本体（マーシャリングの処理と、ネイティブ呼び出し）を生成して埋める。クラスにも `partial` が要る |
| `internal static partial class` | 外には見せない（`internal`）、インスタンスを作らない（`static`）、複数に分けて書ける（`partial`） |
| 関数名 | 既定で、C# のメソッド名と同じ名前の関数を DLL から探す。`me_get_api_version` の名前を、C の名前と一致させる。別名にするなら `EntryPoint = "…"` |
| `[UnmanagedCallConv]` | 呼び出し規約の指定。`CallConvCdecl` で `__cdecl`。x64 では 1 種類なので省略しても動くが、<strong>明示する習慣</strong>にする |
| `private const string Dll` | DLL 名を 1 か所にまとめる定数 |
| `int` ⇔ `int32_t` | C の `int32_t` は、C# の `int`（32 ビット）。大きさで対応させる |

!!! note "DllImport との違い"
    古くからある `[DllImport]` も同じことができます。違いは、`[DllImport]` は呼び出しの変換コードを<strong>実行時に</strong>生成し、`[LibraryImport]` は<strong>コンパイル時に</strong>生成する点です。後者のほうが、速く起動し、生成された変換コードを読んで確かめられます。AOT コンパイルにも対応します。この教材は `[LibraryImport]` を使います。`[DllImport]` が使えるのは、古い環境、または `bool` の既定のマーシャリングに頼る古いコードなどです。

### 動かして確かめる

`App.xaml.cs` の `OnInitialized`（Prism が全部の準備を終えた後に呼ぶ）に、仮のコードを足して確かめます。

```csharp
protected override void OnInitialized()
{
    base.OnInitialized();
    int version = Interop.NativeMethods.me_get_api_version();
    System.Diagnostics.Debug.WriteLine($"EngineApi version = {version}");
}
```

デバッグ実行して、出力ウィンドウに `EngineApi version = 1` が出れば成功です。`DllNotFoundException` が出たら、`bin\x64\Debug\` に `EngineApi.dll` と `Engine.dll` が並んでいるか確認します（くわしくは第 29 章）。

## 手順 3：エラー コードと例外

`me_get_api_version` 以外の関数は、`MeResult` を返します。C# では、<strong>エラー コードを例外に変換</strong>して使います。

### 結果コードの列挙型

```csharp
namespace Editor.Interop;

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `enum MeResult : int` | 土台の型を `int`（32 ビット）に指定した列挙型。C の `int32_t` の `MeResult` と同じ大きさ。<strong>土台の型を明示する</strong>習慣をつける |
| 値の対応 | C の `ME_OK = 0` と C# の `Ok = 0`、…を<strong>同じ数字</strong>にする。順番を変えるときは、両方を変える |

### 例外クラス

```csharp
namespace Editor.Interop;

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Exception` を継承 | 自作の例外型。`catch (EngineException e)` で、エンジンの失敗だけを捕まえられる |
| `: base(message)` | 基底クラスのコンストラクターを呼ぶ。C++ の `: Base(message)` と同じ |
| `internal MeResult Result { get; }` | 例外にエラー コードを持たせる。`get` だけで、コンストラクターで設定する |

### 失敗を例外に変える関数

`NativeMethods` に、`me_get_last_error` の宣言と、変換用の関数を足します。

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `nint` | ポインターと同じ大きさの整数。`IntPtr` の新しい名前。C の `const char*` や `void*` を、そのまま受ける型 |
| `Marshal.PtrToStringUTF8(nint)` | ネイティブの UTF-8 の文字列（`char*`）を、C# の `string`（UTF-16）に<strong>コピーして変換</strong>する。`Marshal` は `System.Runtime.InteropServices` の、変換用の静的クラス |
| 戻り値を `string` で受けない理由 | `const char*` を `string` で受けると、CLR が<strong>解放しようとする</strong>ことがある。`me_get_last_error` が返すのは、C++ が持っている文字列なので、`nint` で受けて自分で変換する。所有者を、取り違えない |
| `?? "(理由なし)"` | 第 5 章の `??`。`null` のときの代わりの値 |

## 手順 4：構造体と出力引数

`me_engine_create` は、構造体を<strong>入力</strong>で受け取り、ハンドルを<strong>出力引数</strong>で返します。

```c
ME_API MeResult me_engine_create(const MeEngineDesc* desc, MeEngine** out_engine);
```

### 構造体の宣言

```csharp
using System.Runtime.InteropServices;

namespace Editor.Interop;

// EngineApi.h の MeEngineDesc と、同じ並びにする
[StructLayout(LayoutKind.Sequential)]
internal struct MeEngineDesc
{
    public nint Window;     // void*    window
    public uint Width;      // uint32_t width
    public uint Height;     // uint32_t height
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `struct` | 値型（第 5 章）。メモリ上に、フィールドが並ぶ。C の `struct` と同じ使い方ができる |
| `[StructLayout(LayoutKind.Sequential)]` | フィールドを、<strong>宣言した順に</strong>並べる指定。C の構造体と並びを合わせるために付ける。構造体には、既定でも `Sequential` だが、<strong>明示する</strong>習慣 |
| `nint Window` | C の `void* window` に対応 |
| `uint Width` | C の `uint32_t width` に対応（`uint` は 32 ビット符号なし） |
| パディング | C は、フィールドの大きさに合わせて<strong>隙間</strong>（パディング）を入れる。`nint`（8 バイト）の後に `uint` が 2 つなので、全体は 16 バイト。C# の `Sequential` も、同じ規則で隙間を入れるので、同じ並びで宣言すれば合う |

!!! warning "構造体のずれを検出する"
    C 側と C# 側のどちらかのフィールドを足したり、順番を変えたりすると、<strong>ビルドが通ったまま、値が化けます</strong>。対策として、C 側に `static_assert(sizeof(MeEngineDesc) == 16)` を書き、C# 側に `Debug.Assert(Marshal.SizeOf<MeEngineDesc>() == 16)` を書いて、<strong>大きさ</strong>だけでも、両側で固定しておきます。

### 関数の宣言（入力の構造体、出力のポインター）

```csharp
[LibraryImport(Dll)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_engine_create(in MeEngineDesc desc, out nint engine);
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `in MeEngineDesc desc` | <strong>読み取り専用の参照渡し</strong>。C の `const MeEngineDesc*` に対応。呼ぶ側は、`in` を書かなくてもよい |
| `out nint engine` | <strong>出力専用の参照渡し</strong>。C の `MeEngine**` に対応。呼ばれた側が必ず値を書く。呼ぶ側は `out var engine` や `out nint engine` と書く |
| `ref` | 入出力兼用の参照渡し。`in` と `out` の両方 |
| 戻り値の `MeResult` | 土台が `int` の列挙型は、`int` として渡される。blittable |

呼ぶ側は次のようになります。

```csharp
var desc = new MeEngineDesc { Window = hwnd, Width = 1280, Height = 720 };
MeResult result = NativeMethods.me_engine_create(in desc, out nint engine);
NativeMethods.ThrowIfFailed(result);
```

## 手順 5：ハンドルを SafeHandle で包む

`out nint engine` で受け取った `nint` は、<strong>ただの整数</strong>です。これを `Editor` のあちこちに渡すと、<strong>解放し忘れ</strong>、<strong>二重に解放</strong>、<strong>解放後に使う</strong>といった間違いが起きます。C++ の `unique_ptr` に当たる役目を、C# では <strong>`SafeHandle`</strong> が担います。

```csharp
using System.Runtime.InteropServices;

namespace Editor.Interop;

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

関数の宣言を、`nint` から `EngineHandle` に変えます。

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `SafeHandle` | ネイティブのハンドルを持つ<strong>抽象基底クラス</strong>。`Dispose()` か、GC による破棄のときに、`ReleaseHandle()` が<strong>ちょうど 1 回</strong>呼ばれることを保証する |
| `handle` | `SafeHandle` が持つ、実際のポインター（`nint`）。`protected` なメンバー |
| `IsInvalid` | ハンドルが無効かどうか。`nint.Zero` なら無効 |
| `ReleaseHandle()` | 解放の処理。ここで `me_engine_destroy(handle)` を呼ぶ。成功したら `true` |
| `base(nint.Zero, ownsHandle: true)` | 基底クラスの初期化。`ownsHandle: true` で、このオブジェクトが、解放の責任を持つ |
| `sealed` | これ以上継承できない（`SafeHandle` の派生は `sealed` にする習慣） |
| 引数に `EngineHandle` を取る | P/Invoke の呼び出し中、<strong>ハンドルの解放を、遅らせる</strong>（参照を数える）。呼び出しの途中で別スレッドが `Dispose` しても、クラッシュしない |
| `out EngineHandle engine` | 呼び出しの戻り時に、マーシャリングが、`EngineHandle` のオブジェクトを<strong>自動で作って</strong>、ハンドルの値を入れる（そのために、引数なしのコンストラクターが要る） |
| `out ulong count` | C の `uint64_t*` に対応 |
| `me_engine_destroy` だけ `nint` | `ReleaseHandle` の中から呼ぶので、`EngineHandle` ではなく、生の値を渡す |

`SafeHandle` を使うと、`using` や `Dispose()` でエンジンを解放できます。<strong>解放し忘れても、GC がいつか `ReleaseHandle()` を呼ぶ</strong>ので、完全なリークにはなりません（ただし、エンジンの破棄は、GPU を使う処理なので、`Dispose` で<strong>明示的に</strong>行うのが正しい使い方です）。

## 手順 6：IEngineService を作る

ビューモデルが、`NativeMethods` や `EngineHandle` を直接触らないよう、<strong>窓口のインターフェース</strong>を作ります。第 28 章の C++/CLI 版も、同じインターフェースを実装します。

`Services\IEngineService.cs`:

```csharp
namespace Editor.Services;

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

`Services\PInvokeEngineService.cs`:

```csharp
using Editor.Interop;

namespace Editor.Services;

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `interface IEngineService : IDisposable` | インターフェースを、さらに別のインターフェースから派生させる。`Dispose()` を持つことを、約束させる |
| `IDisposable` | `Dispose()` を持つインターフェース。`using` で自動的に呼べる（第 5 章） |
| `_handle is { IsInvalid: false }` | <strong>プロパティ パターン</strong>。`_handle` が `null` でなく、`IsInvalid` が `false` のとき真 |
| `is { … } h ? h : throw …` | パターンに合えば、その値を `h` に取り出して使い、合わなければ例外を投げる。`throw` は<strong>式</strong>としても書ける |
| `InvalidOperationException` | 「今の状態では、呼べない」ときに投げる標準の例外 |
| `out var handle` | 出力引数を受ける変数を、その場で宣言する。型は推論される |
| `Handle` を経由する理由 | 毎回 `null` の確認を書かずに済む。確認し忘れて `NullReferenceException` になるのを防ぐ |

`App.xaml.cs` の `RegisterTypes` で、登録します。

```csharp
containerRegistry.RegisterSingleton<IEngineService, PInvokeEngineService>();
```

## 手順 7：ログのコールバック

C++ から C# を呼ぶ方向の連携です。エンジンの `LogInfo` が呼ばれたら、エディタの「ログ」タブに出します。

C の宣言は、次のとおりです。

```c
typedef void (*MeLogCallback)(MeLogLevel level, const char* message, void* user_data);
ME_API void me_set_log_callback(MeLogCallback callback, void* user_data);
```

C# から、<strong>関数ポインター</strong>を渡す必要があります。2 つの方法があります。

### 方法 A：UnmanagedCallersOnly（推奨）

C# の `static` なメソッドに `[UnmanagedCallersOnly]` を付けると、<strong>C から直接呼べる関数</strong>になり、そのアドレスを取れます。

```csharp
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace Editor.Interop;

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
            // C++ の呼び出しスタックへ、例外を通さない
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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `[UnmanagedCallersOnly]` | 「このメソッドは、ネイティブコードから呼ばれる」という属性。C# のコードからは直接呼べない。`static` のみ |
| `byte* message` | `unsafe` のポインター。C の `const char*` と同じ。`unsafe` なクラスやメソッドの中でだけ書ける |
| `delegate* unmanaged[Cdecl]<引数…, 戻り値>` | <strong>関数ポインターの型</strong>。C の `void (*)(int, const char*, void*)` に、そのまま対応する。最後の型が戻り値 |
| `&OnLog` | メソッドのアドレスを取る（`unsafe`）。`[UnmanagedCallersOnly]` のメソッドだけに許される |
| `(nint)message` | ポインターを整数に変換 |
| `catch { }` | <strong>例外を握りつぶして、C++ に戻す</strong>。C++ のスタックへ、例外が通るとクラッシュするため |
| `static Action<…>? s_sink` | ログの出力先。`static` なので、C から呼ばれる `static` メソッドからも見える。慣習として、`static` フィールドは `s_` で始める |
| `null` を渡す | `delegate*` 型に `null` を渡すと、C の `NULL` になり、登録が解除される |

!!! tip "この方式が推奨の理由"
    関数のアドレスが、<strong>固定</strong>です。GC が動かしたり、回収したりしないので、`GCHandle` もデリゲートの延命も要りません。呼び出しの負担も小さいです。

### 方法 B：デリゲート

`[UnmanagedCallersOnly]` が使えない環境（`unsafe` を使いたくない）では、<strong>デリゲート</strong>を渡す方法があります。

```csharp
[UnmanagedFunctionPointer(CallingConvention.Cdecl)]
internal delegate void LogCallbackDelegate(int level, nint message, nint userData);

[LibraryImport(Dll)]
internal static partial void me_set_log_callback(LogCallbackDelegate? callback, nint userData);
```

```csharp
private static LogCallbackDelegate? s_callback;   // 必ず static フィールドで保持する

public static void Install(Action<int, string> sink)
{
    s_callback = (level, message, user) => sink(level, Marshal.PtrToStringUTF8(message) ?? "");
    NativeMethods.me_set_log_callback(s_callback, nint.Zero);
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `[UnmanagedFunctionPointer]` | デリゲート型を、C の関数ポインターとして使うための属性 |
| `delegate void X(…)` | デリゲート型の宣言（第 5 章） |
| 保持が必須 | C++ に渡したデリゲートを、C# 側が<strong>どこにも参照を持たないと、GC に回収される</strong>。その後に C++ が呼ぶと、<strong>クラッシュ</strong>する。`static` フィールドか、`GCHandle` で、解除するまで保持する |

### ログをエディタのログに流す

`App.xaml.cs` で、サービスができた後に、結びつけます。

```csharp
protected override void OnInitialized()
{
    base.OnInitialized();

    int version = Interop.NativeMethods.me_get_api_version();
    var log = Container.Resolve<ILogService>();

    // C++ のログを、エディタのログへ
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

`LogService` は、第 18 章で、<strong>別のスレッドから呼ばれても安全</strong>にしてあります。エンジンが、別のスレッドからログを出しても、`Dispatcher` を介して UI スレッドで追加されます。

| 新しく出てきたもの | 説明 |
| --- | --- |
| `OnInitialized` | Prism が、モジュールの初期化まで終えた後に呼ぶ。サービスがそろっている |
| `OnExit` | アプリが終了するときに呼ばれる。ここで、<strong>コールバックを解除</strong>する（終了後に C++ が呼ばないように） |
| `switch` 文 | `case 0:` … `break;`。C++ と同じ形 |

## 手順 8：文字列を渡す関数の書き方

このあと、アセットのパスのように、C# の文字列を C++ に渡す場面が出てきます。ここで書き方を整理します。

```c
ME_API MeResult me_asset_load(MeEngine* engine, const char* path_utf8);
```

```csharp
[LibraryImport(Dll, StringMarshalling = StringMarshalling.Utf8)]
[UnmanagedCallConv(CallConvs = new[] { typeof(CallConvCdecl) })]
internal static partial MeResult me_asset_load(EngineHandle engine, string path);
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `StringMarshalling = StringMarshalling.Utf8` | `string` 引数を、<strong>UTF-8 の `char*` に変換して</strong>渡す指定。呼び出しの間だけ有効な一時的なバッファーが作られ、戻れば解放される |
| `StringMarshalling.Utf16` | UTF-16（`wchar_t*`）で渡す。Windows API を呼ぶときに使う |
| `StringMarshalling.Custom` | 変換を自分で書く |
| 規則 | C++ は、受け取った `const char*` を、<strong>呼び出しの外に保持しない</strong>（保持したいなら、コピーする） |

C# から C++ へ、<strong>文字列を受け取る</strong>（C++ が書き込む）ときは、<strong>バッファーを渡す</strong>形にします。

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `stackalloc` | スタックに配列を確保する。関数を抜けると自動で消える。GC の対象外。C++ の `alloca` / 固定長の配列に近い |
| `out _` | 出力引数を、<strong>捨てる</strong>（受け取らない） |
| `byte*` | `unsafe` のポインター。C の `char*` に対応 |

この例は、第 34 章のシーンの API で、実際に使います。

## 手順 9：動作確認用の画面

ここまでの内容を、簡単に確かめます。`MainWindowViewModel` に、`IEngineService` を受け取らせ、<strong>エンジンの作成に失敗するケース</strong>を試します。

```csharp
public DelegateCommand TestErrorCommand { get; }

public MainWindowViewModel(IEngineService engine, ILogService log)
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

ボタンを押すと、ログに次のように出ます。

```text
InvalidArgument: window が null、または大きさが 0
```

C++ 側で `SetLastError` した文字列が、C# の例外のメッセージになりました。エラーの経路が、通っていることが確認できます。

## 動作確認

| 見る所 | 期待する結果 |
| --- | --- |
| 起動 | ログに `EngineApi version 1` が出る |
| テスト ボタン | `InvalidArgument: window が null…` がログに出る。クラッシュしない |
| エンジンのログ | （第 31 章以降）エンジンの `LogInfo` が、ログ タブに出る |
| 終了 | 例外なく終了する |

## よくあるミス

??? failure "`DllNotFoundException`／`Unable to load DLL 'EngineApi.dll'`"
    DLL が `Editor.exe` の隣に無い、または、依存する `Engine.dll` が無い、ビット数が違う。第 29 章の手順で原因を探す。

??? failure "`EntryPointNotFoundException`"
    DLL に、その名前の関数が無い。C# 側の名前のタイプミス、`extern "C"` の付け忘れ、`dumpbin /exports` に出ていない。

??? failure "値が化ける／ランダムなクラッシュ"
    構造体のフィールドの型や順番が、C 側と違う。`bool` を使っている。`long` を使っている（C# の `long` は 64 ビット）。宣言を、C のヘッダーと見比べる。

??? failure "ログのコールバックで、突然クラッシュする"
    デリゲートを `static` に保持していない（GC に回収された）。または、コールバックの中で例外が漏れている。方法 A（`UnmanagedCallersOnly`）にすると、前者は起きない。

??? failure "`CS0227: unsafe コードは AllowUnsafeBlocks が必要です`"
    `.csproj` に `<AllowUnsafeBlocks>true</AllowUnsafeBlocks>` を足していない。

??? failure "終了時にクラッシュする"
    終了の途中で、C++ が、すでに解放された C# のコールバックを呼んでいる。`OnExit` で `NativeLog.Uninstall()` を呼ぶ。

## この章のまとめ

| 項目 | 結論 |
| --- | --- |
| 関数の宣言 | `[LibraryImport]` の `partial` メソッド。C のヘッダーと一行ずつ見比べる |
| 型 | blittable な型だけを使う。`bool`、`long`（Windows の C++ の `long`）は避ける |
| 構造体 | `[StructLayout(Sequential)]` で並びを合わせる。大きさを両側で検査する |
| 出力 | `out` / `in` / `ref` で、ポインターを表す |
| 文字列 | `StringMarshalling.Utf8`。受け取るときは、バッファーを渡す |
| ハンドル | `SafeHandle` で包み、`Dispose` で解放する |
| エラー | エラー コード → `EngineException` に変換 |
| コールバック | `[UnmanagedCallersOnly]` と `delegate* unmanaged`。例外を漏らさない |

## 次の章へ

次の章（[第 28 章 C++/CLI で橋を作る](28-cpp-cli.md)）では、同じ `IEngineService` を、<strong>C++/CLI</strong> で実装します。P/Invoke との違いを、手間と書き味で比べます。
