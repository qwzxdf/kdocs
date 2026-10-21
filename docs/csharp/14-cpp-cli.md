---
title: 第 14 章 C++/CLI で橋を作る
tags:
  - C#連携
---

# 第 14 章 C++/CLI で橋を作る

この章では、第 13 章と同じ `IEngineService` を、<strong>C++/CLI</strong> で実装します。P/Invoke 版とは違い、C の API（`EngineApi`）を通らず、<strong>C++ の `Engine` クラスを直接</strong>包みます。作り終えたら、2 つの方式を、手間・書き味・落とし穴の面から比べます。

## この章の考え方

C++/CLI は、普通の C++ に、<strong>マネージドの型</strong>（`ref class`）を書ける拡張を加えた言語です。1 つの `.cpp` ファイルの中に、<strong>ネイティブの C++ と、C# から見える .NET のクラス</strong>を、同居させられます。

```cpp
public ref class EngineBridge {      // C# からは普通の .NET クラスに見える
 public:
  void Tick(float dt) {
    engine_->Tick(dt);               // 中では、ネイティブの C++ クラスをそのまま呼ぶ
  }
 private:
  mini::Engine* engine_;             // ネイティブのポインターを持てる
};
```

C# は、この `EngineBridge` を、`new EngineBridge(…)` で作り、メソッドを呼びます。<strong>P/Invoke のような宣言の二重書きが要りません</strong>。C# のコンパイラーは、`EngineBridge.dll` の<strong>型情報（メタデータ）</strong>を読めるので、引数の型が違えばビルドで分かります。

一方、C++/CLI の仕事は、<strong>橋を作ること専用</strong>です。ゲームのコードやエンジンの中核を、C++/CLI で書くことはしません。

## この章のゴール

- C++/CLI のプロジェクトを作り、`Engine` を包む。
- C# の `Editor` から、参照して使う。
- `IEngineService` の C++/CLI 版を、DI で差し替えられる。
- P/Invoke 版と比べて、違いを説明できる。

## 手順 1：C++/CLI プロジェクトを作る

1. ソリューションを右クリック →「追加 → 新しいプロジェクト」。
2. 言語を C++ にして、<strong>「CLR クラス ライブラリ (.NET)」</strong>を探す。名前を `EngineBridge` にする。

!!! warning "テンプレートの名前"
    テンプレートは、「CLR クラス ライブラリ (.NET)」（.NET 5 以降向け）と、「CLR クラス ライブラリ (.NET Framework)」（旧）の 2 つがあります。必ず <strong>(.NET)</strong> のほうを選びます。見つからないときは、第 0 章の「C++/CLI サポート」のコンポーネントを入れたか、確認します。

3. 作られた `Class1.h`、`Class1.cpp`、`pch.h`、`pch.cpp` などは、削除する（プリコンパイル済みヘッダーは使わない。プロジェクトのプロパティで「プリコンパイル済みヘッダー」を「使用しない」にする）。

### プロジェクトの設定

| 場所 | 項目 | 値 |
| --- | --- | --- |
| 全般 | 構成の種類 | ダイナミック ライブラリ (.dll) |
| 全般 | 共通言語ランタイム サポート | <strong>.NET ランタイム サポート (/clr:netcore)</strong> |
| 全般 | .NET ターゲット フレームワーク | `net8.0` |
| C/C++ → 全般 | 追加のインクルード ディレクトリ | `$(SolutionDir)Engine\include` |
| C/C++ → 全般 | C++ 言語標準 | ISO C++20（`/std:c++20`）。C++/CLI は、最新のプレビュー版の標準に対応しないことがある |
| C/C++ → コード生成 | ランタイム ライブラリ | Debug: `/MDd`、Release: `/MD`（C++/CLI は `/MT` 不可） |
| C/C++ → コード生成 | C++ 例外を有効にする | はい（`/EHa`、C++/CLI の既定） |
| ビルド依存 | プロジェクト参照 | `Engine`（インポート ライブラリのリンク） |

| 新しく出てきたもの | 説明 |
| --- | --- |
| `/clr:netcore` | .NET（旧称 .NET Core）向けに、マネージド コードを書けるようにするコンパイラー オプション。`/clr`（.NET Framework 向け）とは別 |
| 混在アセンブリ | マネージドのコードと、ネイティブのコードが、1 つの DLL に混ざったもの。`EngineBridge.dll` はこれ |
| `/EHa` | 非同期例外（SEH）も `catch` できる例外モデル。C++/CLI の既定 |

!!! note "C++ の標準のバージョン"
    C++/CLI は、`/std:c++latest` に対応しない場合があります。`Engine` の公開ヘッダーが C++23 の機能（`std::format` は C++20 でも可）を要求していない限り、`/std:c++20` で足ります。`Engine` のヘッダーに C++23 専用の機能を使わないことを、ここで意識しておくと、橋が作りやすくなります。

## 手順 2：EngineBridge クラス

`EngineBridge\EngineBridge.h`:

```cpp
#pragma once

#include <Engine/Engine.h>

namespace MiniEngine {
namespace Bridge {

// Engine を .NET から使えるように包むクラス。
public ref class EngineBridge sealed : public System::IDisposable {
 public:
  EngineBridge(System::IntPtr window, System::UInt32 width, System::UInt32 height);

  // ~ は Dispose、! はファイナライザー（GC による破棄）
  ~EngineBridge();
  !EngineBridge();

  void Resize(System::UInt32 width, System::UInt32 height);
  void Tick(float delta_seconds);

  property System::UInt64 FrameCount {
    System::UInt64 get();
  }

 private:
  mini::Engine* engine_;   // ネイティブのポインター
};

}  // namespace Bridge
}  // namespace MiniEngine
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `public ref class` | <strong>マネージドの参照型</strong>を宣言する。`public` を付けると、アセンブリの外（C#）から見える。C# の `public class` に当たる |
| `sealed` | これ以上継承できない |
| `: public System::IDisposable` | .NET のインターフェースを実装する |
| `System::IntPtr` | C# の `nint` / `IntPtr`。`HWND` を受け取る |
| `System::UInt32`、`System::UInt64` | C# の `uint`、`ulong` |
| `~EngineBridge()` | <strong>デストラクター</strong>。C++/CLI では、これが <strong>`Dispose()` として</strong>C# から見える。C# の `using` や `Dispose()` で呼ばれる |
| `!EngineBridge()` | <strong>ファイナライザー</strong>。GC がオブジェクトを回収するとき、`Dispose` されていなければ呼ばれる。解放の最後の砦 |
| `property T Name { T get(); }` | .NET の<strong>プロパティ</strong>を宣言する構文。C# から `bridge.FrameCount` と読める |
| `mini::Engine* engine_` | マネージドのクラスが、ネイティブのポインターを持つ。GC の管理外なので、自分で解放する |
| `namespace MiniEngine { namespace Bridge {…} }` | .NET 側の名前空間。C# からは `MiniEngine.Bridge.EngineBridge` |

### デストラクターとファイナライザー

C++/CLI のクラスの後始末は、2 段構えです。

| | `~EngineBridge()` | `!EngineBridge()` |
| --- | --- | --- |
| 呼ばれるとき | `Dispose()` が呼ばれたとき（`using` の終わり） | GC が回収するとき（`Dispose` されていなければ） |
| 役割 | 通常の後始末 | 最後の砦（呼び忘れの救済） |
| 実装 | <strong>`!EngineBridge()` を呼ぶだけ</strong>にする | ネイティブの資源を解放する |

```cpp
EngineBridge::~EngineBridge() {
  this->!EngineBridge();     // ファイナライザーの処理を、ここで実行する
}

EngineBridge::!EngineBridge() {
  if (engine_) {
    mini::Engine::Destroy(engine_);
    engine_ = nullptr;
  }
}
```

## 手順 3：実装

`EngineBridge\EngineBridge.cpp`:

```cpp
#include "EngineBridge.h"

#include <exception>
#include <string>

using namespace System;

namespace MiniEngine {
namespace Bridge {

namespace {

// ネイティブの UTF-8 の文字列を、.NET の String に変える。
String^ ToManaged(const char* text) {
  if (!text) return String::Empty;
  return gcnew String(text, 0, static_cast<int>(std::strlen(text)), System::Text::Encoding::UTF8);
}

}  // namespace

EngineBridge::EngineBridge(IntPtr window, UInt32 width, UInt32 height) : engine_(nullptr) {
  mini::EngineDesc desc;
  desc.window = static_cast<mini::NativeWindow>(window.ToPointer());
  desc.width = width;
  desc.height = height;

  try {
    engine_ = mini::Engine::Create(desc);
  } catch (const std::exception& e) {
    // ネイティブの例外を、.NET の例外に変える
    throw gcnew InvalidOperationException(ToManaged(e.what()));
  }
  if (!engine_) {
    throw gcnew InvalidOperationException("Engine の作成に失敗しました。ログを確認してください");
  }
}

EngineBridge::~EngineBridge() {
  this->!EngineBridge();
}

EngineBridge::!EngineBridge() {
  if (engine_) {
    mini::Engine::Destroy(engine_);
    engine_ = nullptr;
  }
}

void EngineBridge::Resize(UInt32 width, UInt32 height) {
  if (!engine_) throw gcnew ObjectDisposedException("EngineBridge");
  try {
    engine_->Resize(width, height);
  } catch (const std::exception& e) {
    throw gcnew InvalidOperationException(ToManaged(e.what()));
  }
}

void EngineBridge::Tick(float delta_seconds) {
  if (!engine_) throw gcnew ObjectDisposedException("EngineBridge");
  try {
    engine_->Tick(delta_seconds);
  } catch (const std::exception& e) {
    throw gcnew InvalidOperationException(ToManaged(e.what()));
  }
}

UInt64 EngineBridge::FrameCount::get() {
  if (!engine_) throw gcnew ObjectDisposedException("EngineBridge");
  return engine_->FrameCount();
}

}  // namespace Bridge
}  // namespace MiniEngine
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `String^` | <strong>マネージドの文字列へのハンドル</strong>。`^` は、GC が管理するオブジェクトへの参照を表す記号（C# の参照型の変数に当たる）。ネイティブの `*` と区別する |
| `gcnew` | <strong>GC のヒープに</strong>オブジェクトを作る。C++ の `new` に当たるが、解放は GC が行う。戻り値は `^` |
| `gcnew String(char*, start, length, encoding)` | ネイティブのバイト列を、指定の文字コード（UTF-8）で .NET の文字列に変換する |
| `IntPtr::ToPointer()` | `void*` を取り出す |
| `throw gcnew InvalidOperationException(…)` | .NET の例外を投げる。C# の `catch (InvalidOperationException)` で受けられる |
| `ObjectDisposedException` | 「破棄済みのオブジェクトを使った」ときの、標準の例外 |
| `FrameCount::get()` | プロパティの getter の実装。`クラス名::プロパティ名::get()` の形 |
| 例外の変換 | <strong>ネイティブの `std::exception` を `catch` して .NET の例外に変える</strong>。P/Invoke 版の `Guard` + エラー コードの仕事を、C++/CLI では `try/catch` で直接書く |

`marshal_as` を使うと、`std::string` と `String^` の変換を簡単にできます。

```cpp
#include <msclr/marshal_cppstd.h>

std::string native = msclr::interop::marshal_as<std::string>(managed_string);
String^ managed = msclr::interop::marshal_as<String^>(native);
```

ただし、`marshal_as` の `std::string` は、<strong>システムのコード ページ（ANSI）</strong>で変換します。UTF-8 で受け渡したいときは、`ToManaged` のように、エンコーディングを指定して変換します。

## 手順 4：ログのコールバック

ネイティブの関数ポインターから、.NET のデリゲートを呼びます。

```cpp
#include <msclr/gcroot.h>

public ref class EngineLog abstract sealed {
 public:
  static void Install(System::Action<int, System::String^>^ sink);
  static void Uninstall();
};
```

```cpp
namespace {

// 「managed のデリゲートを、native のコードから安全に持つ」ための入れ物
msclr::gcroot<System::Action<int, System::String^>^>* g_sink = nullptr;

// ネイティブから呼ばれる関数
void NativeLogThunk(mini::LogLevel level, const char* message, void* /*user*/) {
  try {
    if (g_sink) {
      (*g_sink)->Invoke(static_cast<int>(level), ToManaged(message));
    }
  } catch (...) {
    // 例外は外に出さない
  }
}

}  // namespace

void EngineLog::Install(Action<int, String^>^ sink) {
  Uninstall();
  g_sink = new msclr::gcroot<Action<int, String^>^>(sink);
  mini::SetLogCallback(&NativeLogThunk, nullptr);
}

void EngineLog::Uninstall() {
  mini::SetLogCallback(nullptr, nullptr);
  delete g_sink;
  g_sink = nullptr;
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `abstract sealed`（`ref class`） | C# の `static class` に当たる指定。インスタンスを作れず、`static` なメンバーだけを持つ |
| `Action<int, String^>^` | .NET のデリゲート型への参照 |
| `msclr::gcroot<T>` | <strong>マネージドのオブジェクトへの参照を、ネイティブのメモリに保持する</strong>ための道具。GC が参照を追跡し続けるので、回収も移動もされても安全。`GCHandle` を包んだもの |
| `->Invoke(…)` | デリゲートを呼ぶ |
| ネイティブの関数 `NativeLogThunk` | C++ の普通の `static` 関数。`mini::LogCallback` の形に一致する。P/Invoke 版の `[UnmanagedCallersOnly]` に当たる役目 |

P/Invoke 版は、`delegate* unmanaged` と `[UnmanagedCallersOnly]` を使いました。C++/CLI 版は、<strong>マネージドとネイティブの変換を、`gcroot` が担います</strong>。

## 手順 5：C# から使う

`Editor` から、`EngineBridge` を参照します。

1. `Editor` を右クリック →「追加 → プロジェクト参照」。
2. `EngineBridge` にチェック。

!!! warning ".NET の C# から C++/CLI を参照するときの注意"
    C# の SDK 形式のプロジェクトから、`/clr:netcore` の C++/CLI プロジェクトを参照するときは、<strong>ビルドの順番</strong>と、<strong>ターゲット フレームワークの一致</strong>（`net8.0` と `net8.0-windows`）に注意します。うまく参照できないときは、`Editor.csproj` の `<ProjectReference>` に `<SetPlatform>Platform=x64</SetPlatform>` を足す、`EngineBridge` の .NET ターゲットを `net8.0` にそろえる、といった対処を試します。

`Services\ClrEngineService.cs`:

```csharp
using MiniEngine.Bridge;

namespace Editor.Services;

// C++/CLI 版の実装。IEngineService の P/Invoke 版と差し替えられる。
public sealed class ClrEngineService : IEngineService
{
    private EngineBridge? _bridge;

    public bool IsRunning => _bridge != null;

    public void Initialize(nint windowHandle, uint width, uint height)
    {
        if (_bridge != null) throw new InvalidOperationException("すでに初期化されています");
        _bridge = new EngineBridge(windowHandle, width, height);
    }

    public void Resize(uint width, uint height) => Bridge.Resize(width, height);
    public void Tick(float deltaSeconds) => Bridge.Tick(deltaSeconds);
    public ulong FrameCount => Bridge.FrameCount;

    public void Dispose()
    {
        _bridge?.Dispose();
        _bridge = null;
    }

    private EngineBridge Bridge => _bridge ?? throw new InvalidOperationException("エンジンが初期化されていません");
}
```

`ClrEngineService` は、`PInvokeEngineService` と比べて、<strong>とても短い</strong>です。エラー コード、`SafeHandle`、宣言の二重書きがありません。

### どちらを使うか切り替える

`Editor.csproj` に、条件付きコンパイル シンボルを使います。

```xml
<PropertyGroup Condition="'$(UseCppCli)' == 'true'">
  <DefineConstants>$(DefineConstants);USE_CPPCLI</DefineConstants>
</PropertyGroup>
```

`App.xaml.cs` の `RegisterTypes` は、次のように書きます。

```csharp
#if USE_CPPCLI
containerRegistry.RegisterSingleton<IEngineService, ClrEngineService>();
#else
containerRegistry.RegisterSingleton<IEngineService, PInvokeEngineService>();
#endif
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `#if USE_CPPCLI … #else … #endif` | C# の条件付きコンパイル。C++ の `#if` と同じ |
| `DefineConstants` | C# のコンパイル時に定義するシンボル |
| `Condition="'$(UseCppCli)' == 'true'"` | MSBuild の条件。`msbuild -p:UseCppCli=true` や、プロパティ指定で有効にできる |

ビューモデルは `IEngineService` だけを知っているので、<strong>どちらの実装か</strong>に関係なく、同じコードで動きます。

## 手順 6：比べる

P/Invoke 版（第 12、13 章）と C++/CLI 版（この章）を、第 11 章の観点で比べます。

| 観点 | P/Invoke + C API | C++/CLI |
| --- | --- | --- |
| 追加するコード | `EngineApi`（C ヘッダー、実装）と、C# の `NativeMethods`、構造体、`SafeHandle`、例外の変換 | `EngineBridge`（ヘッダー、実装）のみ |
| 関数を 1 つ足す手間 | C の宣言 → C の実装 → C# の宣言 → C# の窓口（4 か所） | C++/CLI の宣言 → 実装 → C# の窓口（3 か所）。クラスのメソッドをそのまま包む |
| 宣言のずれ | <strong>実行時</strong>に発覚（化ける、クラッシュ） | <strong>ビルド時</strong>に発覚（型情報を、コンパイラーが読む） |
| 例外の扱い | エラー コード + `GetLastError` を、自分で作る | `try/catch` で .NET の例外に変換 |
| 文字列 | UTF-8 に統一。変換は属性で宣言 | `gcnew String(..., UTF8)`。`marshal_as` は ANSI なので注意 |
| 所有の管理 | `SafeHandle` | デストラクターとファイナライザー |
| コールバック | `[UnmanagedCallersOnly]`、または GC の保持に注意 | `gcroot` |
| ビルド時間 | 速い | 遅い（`/clr` の混在コード、ヘッダーの取り込み） |
| 設定の癖 | 少ない | 多い（標準のバージョン、`/MD` 必須、ターゲット フレームワーク） |
| 他の OS | C API は使い回せる | 使えない（Windows 専用） |
| ネイティブのクラスを公開 | ハンドル + 関数群に分解が必要 | クラスのまま包める |
| デバッグ | 混在デバッグの設定が必要（第 15 章） | 同じ（混在デバッグ） |

### まとめ

| 向いている場面 | 選ぶ方式 |
| --- | --- |
| 関数の数が増えても、構造が単純 | P/Invoke + C API |
| 将来、別の OS や他の言語からも使いたい | P/Invoke + C API |
| C++ の API を、すでに持っていて、クラスの形を保って見せたい | C++/CLI |
| C# 側の型のずれを、ビルドで検出したい | C++/CLI |
| 小さなチームで、設定の手間を減らしたい | P/Invoke + C API |

この教材では、以降、<strong>P/Invoke + C API</strong> を使います（C のインターフェース設計が、エンジンの設計の練習になること、ビルドが速いこと、移植しやすいことが理由です）。`IEngineService` を境界にしているので、<strong>C++/CLI 版に差し替えても、ビューモデルは変わりません</strong>。

## 動作確認

| 見る所 | 期待する結果 |
| --- | --- |
| `EngineBridge` のビルド | エラー、警告なし。`bin\x64\Debug\EngineBridge.dll` ができる |
| `Editor` のビルド | `EngineBridge` への参照が解決される |
| `-p:UseCppCli=true` でビルド | `ClrEngineService` が使われる |

## よくあるミス

??? failure "`C1190: マネージド ターゲット コードには '/clr' または '/clr:pure' コンパイラ オプションが必要です`"
    プロジェクトの「共通言語ランタイム サポート」が、`/clr:netcore` になっていない。

??? failure "`/clr` と `/EHs` が競合する（`D8016`）"
    例外処理のオプションが `/EHsc` になっている。C++/CLI では `/EHa` にする。

??? failure "`C2065`／`C3699` などで、`ref class` が理解されない"
    `.cpp` のファイルに、`/clr` が効いていない（ファイル単位でオフになっている）、または、ネイティブの C++ のファイルが混じっている。

??? failure "`BadImageFormatException`"
    ターゲットのビット数が違う（`EngineBridge` を `x64` でビルドしていない）。または `net8.0` と `net8.0-windows` の食い違い。

??? failure "`std::string` を返す関数を公開したらビルドが通らない"
    `public ref class` のメンバーには、ネイティブの型（`std::string`、`std::vector`）を<strong>公開できない</strong>。`String^` や `array<T>^` に変換して返す。

## この章のまとめ

- C++/CLI は、ネイティブの C++ クラスを、そのまま .NET のクラスに包める。<strong>宣言の二重書きが無い</strong>。
- 代わりに、<strong>ビルドの設定が癖だらけ</strong>で、Windows 専用。
- どちらの方式でも、`IEngineService` を境界にすれば、ビューモデルは影響を受けない。

## 次の章へ

次の章（[第 15 章 DLL の読み込み、x64、デバッグ](15-dll-loading.md)）では、連携が動かないときの<strong>原因の探し方</strong>を、まとめます。`DllNotFoundException`、`BadImageFormatException`、ネイティブのコードにブレークポイントを置く方法、クラッシュ ダンプの読み方を扱います。
