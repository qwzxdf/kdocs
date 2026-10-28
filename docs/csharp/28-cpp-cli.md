---
title: 第 28 章 C++/CLI で橋を作る
tags:
  - C#連携
---

# 第 28 章 C++/CLI で橋を作る

この章では、第 27 章と同じ `IEngineService` を C++/CLI で実装します。P/Invoke 版は C の API（`EngineApi`）を通りましたが、こちらは C++ の `Engine` クラスを直接包みます。作り終えたら、2 つの方式を手間と書き味の両面から比べます。

!!! info "このページを読む前に"
    - [第 27 章 P/Invoke で C# から呼ぶ](27-pinvoke.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## C++/CLI とは

C++/CLI は、普通の C++ に、.NET の型（`ref class`）を書ける拡張を足した言語です。1 つの `.cpp` の中にネイティブの C++ と、C# から見える .NET のクラスを同居させられます。

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

C# は、この `EngineBridge` を `new EngineBridge(...)` で作って、メソッドを呼ぶだけです。P/Invoke のように宣言を二重に書く必要はなく、C# のコンパイラーは `EngineBridge.dll` の型情報（メタデータ）を読めるので、引数の型が違えばビルドで見つかります。

ただし、C++/CLI の役目は橋渡しだけです。エンジンの中核やゲームのコードを C++/CLI で書くことはしません。

## プロジェクトを作る

1. ソリューションを右クリックして「追加 → 新しいプロジェクト」を開きます。
2. 言語を C++ にして、「CLR クラス ライブラリ (.NET)」を探します。名前は `EngineBridge` にします。

!!! warning "テンプレートの名前に注意"
    似た名前で「CLR クラス ライブラリ (.NET Framework)」という古いテンプレートもあります。必ず `(.NET)` のほうを選びます。見つからないときは、第 0 章で触れた「C++/CLI サポート」のコンポーネントが入っているかを確かめてください。

3. 作られた `Class1.h`、`Class1.cpp`、`pch.h`、`pch.cpp` は削除します。プリコンパイル済みヘッダーは使わないので、プロパティで「使用しない」にします。

設定は次のとおりです。

| 場所 | 項目 | 値 |
| --- | --- | --- |
| 全般 | 構成の種類 | ダイナミック ライブラリ (.dll) |
| 全般 | 共通言語ランタイム サポート | .NET ランタイム サポート (`/clr:netcore`) |
| 全般 | .NET ターゲット フレームワーク | `net8.0` |
| C/C++ → 全般 | 追加のインクルード ディレクトリ | `$(SolutionDir)Engine\include` |
| C/C++ → 全般 | C++ 言語標準 | ISO C++20（`/std:c++20`） |
| C/C++ → コード生成 | ランタイム ライブラリ | Debug は `/MDd`、Release は `/MD`（`/MT` は不可） |
| C/C++ → コード生成 | C++ 例外を有効にする | はい（`/EHa`。C++/CLI の既定） |
| ビルド依存 | プロジェクト参照 | `Engine` |

`/clr:netcore` は、.NET（旧 .NET Core）向けにマネージド コードを書けるようにするオプションです。古い .NET Framework 向けの `/clr` とは別物です。できあがる `EngineBridge.dll` は、マネージドとネイティブのコードが 1 つに混ざった混在アセンブリになります。

C++ の標準を `/std:c++20` にしているのは、C++/CLI が最新のプレビュー標準に対応しないことがあるからです。`Engine` の公開ヘッダーを C++23 専用の機能に頼らず書いておくと、橋が作りやすくなります。

## EngineBridge クラスを書く

```cpp title="EngineBridge/EngineBridge.h"
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

見慣れない書き方を拾っていきます。

- `public ref class` は、マネージドの参照型の宣言です。`public` を付けると C# から見えます。C# の `public class` にあたります。
- `System::IntPtr` が C# の `nint`、`System::UInt32` / `UInt64` が `uint` / `ulong` です。
- `property T Name { T get(); }` は .NET のプロパティを宣言する書き方で、C# からは `bridge.FrameCount` と読めます。
- `mini::Engine* engine_` のように、マネージドのクラスがネイティブのポインターを持てます。ただし、GC の管理外なので、解放は自分でしなければなりません。

### デストラクターとファイナライザー

C++/CLI のクラスの後始末は、2 段構えです。

`~EngineBridge()`（デストラクター）は、C# から見ると `Dispose()` になります。C# の `using` や `Dispose()` で呼ばれる、普通の後始末の入口です。`!EngineBridge()`（ファイナライザー）は、`Dispose` が呼ばれなかったときに、GC が回収する際に呼ばれる、最後の砦です。

実装は、デストラクターからファイナライザーを呼ぶだけにして、実際の解放をファイナライザーに書きます。

```cpp
EngineBridge::~EngineBridge() {
  this->!EngineBridge();     // ファイナライザーの処理をここで実行する
}

EngineBridge::!EngineBridge() {
  if (engine_) {
    mini::Engine::Destroy(engine_);
    engine_ = nullptr;
  }
}
```

## 実装を書く

```cpp title="EngineBridge/EngineBridge.cpp"
#include "EngineBridge.h"

#include <exception>
#include <string>

using namespace System;

namespace MiniEngine {
namespace Bridge {

namespace {

// ネイティブの UTF-8 の文字列を.NET の String に変える。
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
    // ネイティブの例外を.NET の例外に変える
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

ここでも見慣れない記号が出てきます。

- `String^` は、マネージドの文字列へのハンドルです。`^` は「GC が管理するオブジェクトへの参照」を表す記号で、ネイティブの `*` と区別します。
- `gcnew` は、GC のヒープにオブジェクトを作る演算子で、C++ の `new` にあたりますが、解放は GC がやってくれます。
- `FrameCount::get()` は、プロパティの getter の実装です。
- 例外は、`std::exception` を `catch` して .NET の例外に変えて投げ直しています。P/Invoke 版では、エラー コードと `me_get_last_error` で行っていたことを C++/CLI では `try/catch` で直接書けます。

`std::string` と `String^` の変換には、`marshal_as` も使えます。

```cpp
#include <msclr/marshal_cppstd.h>

std::string native = msclr::interop::marshal_as<std::string>(managed_string);
String^ managed = msclr::interop::marshal_as<String^>(native);
```

ただし、`marshal_as` で `std::string` を作ると、システムのコード ページ（ANSI）で変換されます。UTF-8 でやり取りしたいなら、上の `ToManaged` のように、エンコーディングを指定して変換します。

## ログのコールバックを受ける

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

// マネージドのデリゲートをネイティブのコードから安全に持つための入れ物
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

`abstract sealed` を付けた `ref class` は、C# の `static class` にあたります。`msclr::gcroot<T>` は、マネージドのオブジェクトへの参照をネイティブのメモリの中に安全に持つための道具です。GC がその参照を追い続けてくれるので、回収されたり動かされたりしても大丈夫です。`NativeLogThunk` は、ただのネイティブの関数で、P/Invoke 版の `[UnmanagedCallersOnly]` のメソッドと同じ役目をしています。マネージドとネイティブの橋渡しを `gcroot` が担います。

## C# から使う

`Editor` から `EngineBridge` を参照します。`Editor` を右クリックして「追加 → プロジェクト参照」を開き、`EngineBridge` にチェックを入れます。

!!! warning "C++/CLI の参照は、少し癖がある"
    C# の SDK 形式のプロジェクトから、`/clr:netcore` の C++/CLI を参照するときは、ビルドの順番とターゲット フレームワークの一致（`net8.0` と `net8.0-windows`）に気をつけてください。うまく参照できないときは、`Editor.csproj` の `<ProjectReference>` に `<SetPlatform>Platform=x64</SetPlatform>` を足したり、`EngineBridge` の .NET ターゲットを `net8.0` にそろえたりして試します。

```csharp title="Services/ClrEngineService.cs"
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

`PInvokeEngineService` と見比べてください。エラー コードも、`SafeHandle` も、宣言の二重書きもなくて、ずっと短くなっています。

### 実装を切り替える

どちらを使うかは、条件付きコンパイルで切り替えます。`Editor.csproj` に、次を足します。

```xml
<PropertyGroup Condition="'$(UseCppCli)' == 'true'">
  <DefineConstants>$(DefineConstants);USE_CPPCLI</DefineConstants>
</PropertyGroup>
```

`App.xaml.cs` の `RegisterTypes` は、こう書きます。

```csharp
#if USE_CPPCLI
containerRegistry.RegisterSingleton<IEngineService, ClrEngineService>();
#else
containerRegistry.RegisterSingleton<IEngineService, PInvokeEngineService>();
#endif
```

`#if` は C++ と同じ条件付きコンパイルです。`msbuild -p:UseCppCli=true` でビルドすると、`USE_CPPCLI` が定義されて、C++/CLI 版が使われます。ビューモデルは `IEngineService` しか知らないので、どちらの実装でも同じコードのまま動きます。

## 2 つを比べる

実際に両方を作ってみると、違いが見えてきます。

| 観点 | P/Invoke + C API | C++/CLI |
| --- | --- | --- |
| 書く量 | `EngineApi`（C のヘッダーと実装）、C# の `NativeMethods`、構造体、`SafeHandle`、例外の変換 | `EngineBridge` のヘッダーと実装だけ |
| 関数を 1 つ足す手間 | C の宣言 → C の実装 → C# の宣言 → C# の窓口（4 か所） | C++/CLI の宣言 → 実装 → C# の窓口（3 か所） |
| 宣言のずれ | 実行時に発覚する | ビルドで発覚する |
| 例外 | エラー コードと `me_get_last_error` を自分で作る | `try/catch` で .NET の例外にする |
| 文字列 | UTF-8 に統一。変換は属性で書く | 自分で `gcnew String(..., UTF8)`。`marshal_as` は ANSI なので注意 |
| 所有の管理 | `SafeHandle` | デストラクターとファイナライザー |
| ビルド時間 | 速い | 遅い（`/clr` の混在コード、ヘッダーの取り込み） |
| 設定のクセ | 少ない | 多い（標準のバージョン、`/MD` 必須、ターゲット フレームワーク） |
| 他の OS | C API は使い回せる | 使えない |
| C++ のクラス | ハンドルと関数に分解する | クラスのまま包める |

書く量や宣言のずれの検出では、C++/CLI のほうが明らかに楽です。一方、設定の癖、ビルドの遅さ、Windows 専用という点では、P/Invoke が有利です。

選ぶときの目安はこうです。

- 関数が増えても構造が単純で、将来、他の OS や他の言語からも使いたいなら、P/Invoke + C API。
- すでにある C++ の API をクラスの形のまま見せたいなら、C++/CLI。
- C# 側の型のずれをビルドで見つけたいなら、C++/CLI。
- 設定の手間を減らしたい小さなチームなら、P/Invoke + C API。

この教材では、以降は P/Invoke + C API を使います。C のインターフェースを整理する作業がエンジンの設計の練習になり、ビルドも速いからです。ただ、`IEngineService` で分けてあるので、あとから C++/CLI 版に差し替えても、ビューモデルは変わりません。

## 動かして確かめる

- `EngineBridge` がエラーも警告もなくビルドでき、`bin\x64\Debug\EngineBridge.dll` ができる。
- `Editor` のビルドで、`EngineBridge` への参照が解決される。
- `-p:UseCppCli=true` を付けてビルドしたときに、`ClrEngineService` が使われる。

??? failure "`C1190: マネージド ターゲット コードには '/clr' または '/clr:pure' コンパイラ オプションが必要です`"
    プロジェクトの「共通言語ランタイム サポート」が `/clr:netcore` になっていません。

??? failure "`/clr` と `/EHs` が競合する（`D8016`）"
    例外処理のオプションが `/EHsc` になっています。C++/CLI では `/EHa` にします。

??? failure "`ref class` が理解されない（`C2065`、`C3699` など）"
    その `.cpp` に `/clr` が効いていません（ファイル単位でオフになっていることがあります）。ネイティブだけの `.cpp` が混ざっていないかも確かめます。

??? failure "`BadImageFormatException`"
    ビット数が違います（`EngineBridge` を `x64` でビルドしていない）。または、`net8.0` と `net8.0-windows` が食い違っています。

??? failure "`std::string` を返す関数を公開したらビルドが通らない"
    `public ref class` のメンバーには、ネイティブの型（`std::string`、`std::vector`）を公開できません。`String^` や `array<T>^` に変換して返してください。

次の章では、連携が動かないときの原因の探し方をまとめます。

[第 29 章 DLL の読み込み、x64、デバッグ](29-dll-loading.md) へ進みます。
