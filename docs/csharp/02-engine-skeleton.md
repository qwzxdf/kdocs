---
title: 第 2 章 Engine プロジェクト：DLL の骨組み
tags:
  - C#連携
---

# 第 2 章 Engine プロジェクト：DLL の骨組み

この章では `Engine` プロジェクトに最初のコードを書きます。DirectX 12 は次の章まで、待ちます。ここでは、<strong>DLL からクラスや関数を公開する方法</strong>と <strong>公開してよい形</strong>を決めます。この章で決める形が後の章の EngineApi、Game、Player のすべてに効いてきます。

## この章の考え方

DLL は、<strong>「他のプログラムに貸し出す部品」</strong>です。貸し出すには、「何を貸すか」を決める必要があります。それが<strong>公開ヘッダー</strong>です。利用者（Player、Game、EngineApi）は、公開ヘッダーに書かれた宣言だけを見て、DLL の中身（実装）は見ません。

ここで大事なのは、<strong>公開ヘッダーを小さく保つ</strong>ことです。DirectX のヘッダーや、内部で使うクラスを公開ヘッダーに出してしまうと、利用者もそれを読み込むことになり、ビルドが遅くなり、内部を変えるたびに利用者が壊れます。そのため、この章では、実装の詳細を隠す <strong>Pimpl（ピンプル）</strong>という書き方を使います。クラスの中身を `Impl` という構造体に包んで、ヘッダーには「ポインターを 1 つ持つ」ことだけを書きます。

また、DLL の境界を越えて、`std::string` や `std::vector` を渡すのは、危険です。DLL ごとに、メモリを確保する側と解放する側がずれて、クラッシュすることがあるからです。この章では、<strong>境界を越えるのは、単純な型（整数、浮動小数、ポインター、`const char*`）だけ</strong>にする、という方針で書きます。

## この章のゴール

- Engine を <strong>公開ヘッダー</strong>（`include/`）と <strong>非公開のソース</strong>（`src/`）に分ける。
- `__declspec(dllexport)` / `dllimport` を切り替えるマクロ `ENGINE_API` を作る。
- <strong>ログの仕組み</strong>と <strong>エンジンの入口</strong>（`Engine::Create` / `Tick` / `Destroy`）を作る。
- 他のプロジェクトが `Engine.lib` をリンクして `Engine.dll` を使えるように設定する。

## 追加するもの

```text
Engine\
  include\Engine\          ← 公開ヘッダー（他のプロジェクトが #include する）
    Export.h               ENGINE_API マクロ
    Log.h                  ログ
    Engine.h               エンジンの入口
  src\                     ← 非公開（Engine の中だけで使う）
    Log.cpp
    Engine.cpp
```

## DLL とは何を公開するのか

DLL（Dynamic Link Library）は、<strong>実行時に読み込まれるコードの束</strong>です。ところが、DLL の中の関数やクラスは何も指定しないと <strong>外から、見えません</strong>。外に見せたい物に <strong>エクスポート</strong>の印を付けます。

| 側 | 印 | 意味 |
| --- | --- | --- |
| DLL を作る側（Engine） | `__declspec(dllexport)` | この関数・クラスを DLL の外に、公開する |
| DLL を使う側（Player など） | `__declspec(dllimport)` | この関数・クラスは、DLL から読み込む |

同じヘッダーを作る側と使う側で、共有したいので <strong>マクロで切り替えます</strong>。

### 手順 1：Export.h

`Engine\include\Engine\Export.h` を作ります（フォルダーが無ければ、作る）。

```cpp
#pragma once

// Engine を「作る」ときは ENGINE_EXPORTS が定義されている（Visual Studio が、DLL のプロジェクトに、自動で付ける）。
// 「使う」側では、定義されていない。
#ifdef ENGINE_EXPORTS
#define ENGINE_API __declspec(dllexport)
#else
#define ENGINE_API __declspec(dllimport)
#endif
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `#pragma once` | このヘッダーを同じ翻訳単位に 2 回読み込まない（インクルード ガード） |
| `__declspec(dllexport)` | MSVC の拡張。この宣言を DLL からエクスポートする。ビルドすると `.lib`（インポート ライブラリ）にも書き出される |
| `__declspec(dllimport)` | この宣言は他の DLL にある。呼び出しが少し速くなる（間接呼び出しの最適化） |
| `ENGINE_EXPORTS` | `<プロジェクト名>_EXPORTS` の形で DLL のテンプレートが、プリプロセッサ定義に入れている（プロパティ → C/C++ → プリプロセッサ） |

## 公開ヘッダーと非公開ソースを分ける

Engine の外から見える物は <strong>`include\Engine\` の中だけ</strong>にします。`src\` の中は Engine の内部の実装で、他のプロジェクトは見ません。

### 手順 2：インクルード ディレクトリを設定する

Engine プロジェクトのプロパティ（構成: すべての構成、プラットフォーム: x64）を開きます。

| 場所 | 設定 | 値 |
| --- | --- | --- |
| C/C++ → 全般 → 追加のインクルード ディレクトリ | 追加 | `$(ProjectDir)include;$(ProjectDir)src` |
| C/C++ → 言語 → C++ 言語標準 | 選択 | `ISO C++23 標準 (/std:c++latest)` |
| C/C++ → 全般 → 警告レベル | 選択 | `Level4 (/W4)` |
| C/C++ → 全般 → 警告をエラーとして扱う | 選択 | `はい (/WX)` |
| C/C++ → コード生成 → ランタイム ライブラリ | 確認 | Debug は `マルチスレッド デバッグ DLL (/MDd)`、Release は `マルチスレッド DLL (/MD)`（既定） |

| 新しく出てきたもの | 説明 |
| --- | --- |
| `$(ProjectDir)` | このプロジェクトの `.vcxproj` がある、フォルダー（`\` で終わる） |
| `/W4`、`/WX` | 警告を多めに出し警告をエラーにする。バグを早く見つける |
| `/MD`・`/MDd` | C ランタイム（`malloc` や `std::` の実装）を <strong>DLL として、共有</strong>する。<strong>全プロジェクトでそろえる</strong>（DLL の間で、メモリを渡すため） |

## ログを作る

エンジンのメッセージ（警告、エラー）は <strong>エディタのログ画面に表示</strong>したくなります。そのため、ログの出力先を <strong>後から差し替えられる</strong>ようにします。

### 手順 3：Log.h

`include\Engine\Log.h`:

```cpp
#pragma once

#include <cstdint>
#include <format>
#include <utility>

#include "Engine/Export.h"

namespace mini {

enum class LogLevel : std::int32_t { Info, Warning, Error };

// ログの出力先。C 言語の関数ポインターにして、C# からも渡せる形にしておく（第 27 章）。
// user: 登録した側が、好きに使える、ポインター（コールバックに、そのまま、返ってくる）。
using LogCallback = void (*)(LogLevel level, const char* message, void* user);

// 出力先を差し替える。nullptr で、既定（デバッガーの出力ウィンドウ）に戻す。
ENGINE_API void SetLogCallback(LogCallback callback, void* user);

// 1 件のメッセージを出す（UTF-8 の文字列）。
ENGINE_API void Log(LogLevel level, const char* message);

// 書式つき。std::format と同じ書き方。ヘッダーに書いた、テンプレートなので、使う側で、展開される。
template <typename... Args>
void LogInfo(std::format_string<Args...> format, Args&&... args) {
  Log(LogLevel::Info, std::format(format, std::forward<Args>(args)...).c_str());
}
template <typename... Args>
void LogWarning(std::format_string<Args...> format, Args&&... args) {
  Log(LogLevel::Warning, std::format(format, std::forward<Args>(args)...).c_str());
}
template <typename... Args>
void LogError(std::format_string<Args...> format, Args&&... args) {
  Log(LogLevel::Error, std::format(format, std::forward<Args>(args)...).c_str());
}

}  // namespace mini
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `using LogCallback = void (*)(...)` | 関数ポインターの別名。<strong>C の関数ポインター</strong>にしておくと後で、C# の `delegate` と対応させられる |
| `std::format_string<Args...>` | `std::format` の書式文字列を <strong>コンパイル時に検査</strong>する型（C++20） |
| `std::forward` | 引数を元の値カテゴリー（左辺値・右辺値）のまま渡す（完全転送） |
| ヘッダーに書くテンプレート | DLL の境界を越えない。使う側のプロジェクトに展開されて、`Log`（エクスポート済み）だけを呼ぶ |

!!! note "なぜ `std::string` を引数にしないのか"
    DLL の境界を `std::string` で越えると、DLL と使う側で <strong>標準ライブラリの実装や設定が、違う</strong>とき（Debug と Release の混在など）、壊れます。このため境界では `const char*` のような <strong>単純な型</strong>だけを渡す方針にします。`LogInfo` のようなテンプレートは使う側で、展開されて最後に `const char*` の `Log` を呼ぶので、安全です。

### 手順 4：Log.cpp

`src\Log.cpp`:

```cpp
#include "Engine/Log.h"

#include <windows.h>

#include <cstdio>
#include <mutex>

namespace mini {
namespace {

std::mutex g_mutex;                       // ログは、複数のスレッドから、呼ばれうる
LogCallback g_callback = nullptr;
void* g_user = nullptr;

const char* LevelName(LogLevel level) {
  switch (level) {
    case LogLevel::Info: return "INFO";
    case LogLevel::Warning: return "WARN";
    case LogLevel::Error: return "ERROR";
  }
  return "?";
}

}  // namespace

void SetLogCallback(LogCallback callback, void* user) {
  std::lock_guard lock(g_mutex);
  g_callback = callback;
  g_user = user;
}

void Log(LogLevel level, const char* message) {
  LogCallback callback;
  void* user;
  {
    std::lock_guard lock(g_mutex);
    callback = g_callback;
    user = g_user;
  }
  if (callback) {
    callback(level, message, user);       // 登録された出力先（エディタなど）へ
    return;
  }
  // 既定: デバッガーの出力ウィンドウと、標準エラー出力へ。
  char line[1024];
  std::snprintf(line, sizeof(line), "[%s] %s\n", LevelName(level), message);
  OutputDebugStringA(line);
  std::fputs(line, stderr);
}

}  // namespace mini
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| 無名名前空間 `namespace { ... }` | この `.cpp` の中だけで見える変数や関数（`static` と同じ効果）。グローバル変数を外に出さない |
| `std::mutex`、`std::lock_guard` | 複数のスレッドが同時に同じ変数を触らないように守る（排他制御） |
| コールバックをロックの外で呼ぶ | コールバックの中で、また `Log` が呼ばれても <strong>デッドロックしない</strong>ようにするため |
| `OutputDebugStringA` | Visual Studio の「出力」ウィンドウに文字列を出す Win32 関数 |

## エンジンの入口を作る

### 手順 5：Engine.h

`include\Engine\Engine.h`:

```cpp
#pragma once

#include <cstdint>

#include "Engine/Export.h"

// windows.h を、公開ヘッダーに、引き込まないための、前方宣言。HWND は、この型へのポインター。
struct HWND__;

namespace mini {

using NativeWindow = HWND__*;             // HWND と同じ型

struct EngineDesc {
  NativeWindow window = nullptr;          // 描画先のウィンドウ（第 3 章で使う）
  std::uint32_t width = 0;                // 描画領域の大きさ（ピクセル）
  std::uint32_t height = 0;
};

// エンジン 1 台ぶん。Create で作り、Destroy で壊す。
class ENGINE_API Engine {
 public:
  static Engine* Create(const EngineDesc& desc);
  static void Destroy(Engine* engine);

  void Resize(std::uint32_t width, std::uint32_t height);
  void Tick(float delta_seconds);                       // 1 フレーム進める（更新 + 描画）
  std::uint64_t FrameCount() const;

 private:
  Engine() = default;
  ~Engine() = default;
  Engine(const Engine&) = delete;
  Engine& operator=(const Engine&) = delete;

  struct Impl;                                          // 実装の詳細は、.cpp に隠す（pimpl）
  Impl* impl_ = nullptr;
};

}  // namespace mini
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `struct HWND__;` | `HWND`（ウィンドウ ハンドル）は、`struct HWND__*` の別名。前方宣言だけして巨大な `<windows.h>` を公開ヘッダーに持ち込まない |
| `ENGINE_API` をクラスに付ける | クラスのすべてのメンバー関数が、エクスポートされる |
| `private` なコンストラクター・デストラクター | 利用者が `new Engine` や `delete` を直接しないようにする。`Create`/`Destroy` を通させる |
| `Create`/`Destroy` を対にする | <strong>メモリの確保と解放を同じ DLL の中で、行う</strong>。DLL をまたいで `new` と `delete` を混ぜると、ヒープが別々のとき壊れる |
| pimpl（`struct Impl; Impl* impl_;`） | 内部のデータを `.cpp` に隠す。ヘッダーに `std::vector` などを書くと警告 `C4251`（DLL の境界で、STL を使っている）が出るため、これを避ける |

### 手順 6：Engine.cpp

`src\Engine.cpp`:

```cpp
#include "Engine/Engine.h"

#include "Engine/Log.h"

namespace mini {

struct Engine::Impl {
  EngineDesc desc;
  std::uint64_t frame_count = 0;
};

Engine* Engine::Create(const EngineDesc& desc) {
  auto* engine = new Engine();
  engine->impl_ = new Impl();
  engine->impl_->desc = desc;
  LogInfo("Engine を作成しました（{}x{}）", desc.width, desc.height);
  return engine;
}

void Engine::Destroy(Engine* engine) {
  if (!engine) return;
  LogInfo("Engine を破棄します（{} フレーム）", engine->impl_->frame_count);
  delete engine->impl_;
  delete engine;
}

void Engine::Resize(std::uint32_t width, std::uint32_t height) {
  impl_->desc.width = width;
  impl_->desc.height = height;
}

void Engine::Tick(float /*delta_seconds*/) {
  ++impl_->frame_count;
}

std::uint64_t Engine::FrameCount() const {
  return impl_->frame_count;
}

}  // namespace mini
```

`Engine::Engine()` が `private` でも `Create`（静的メンバー関数）の中からは `new Engine()` を呼べます。クラスのメンバー関数は自分の `private` に触れるためです。

## 他のプロジェクトから使えるようにする

`Engine.dll` を使う側（Player、EngineApi、Game）では次の 2 つを設定します。<strong>この設定は第 3 章以降、何度も使います。</strong>

### 手順 7：参照の追加とインクルード ディレクトリ

`EngineApi` を例に説明します。

1. ソリューション エクスプローラーで、`EngineApi` の「参照」ではなく <strong>プロジェクトを右クリック → 「追加 → 参照」</strong>を開く。
2. 「プロジェクト」の一覧から、<strong>`Engine` にチェック</strong>を入れて OK。
3. `EngineApi` のプロパティ → C/C++ → 全般 → 追加のインクルード ディレクトリ に `$(SolutionDir)Engine\include` を、追加する。

| 新しく出てきたもの | 説明 |
| --- | --- |
| 参照（プロジェクト参照） | 他のプロジェクトを <strong>ビルドの順序</strong>と <strong>リンクの対象</strong>に、加える。C++ の DLL への参照では <strong>`Engine.lib`（インポート ライブラリ）が自動で、リンクされる</strong> |
| インポート ライブラリ（`.lib`） | DLL の <strong>目録</strong>。「`Engine::Create` は `Engine.dll` のここにある」という情報が入っている。使う側はこれをリンクして実行時に DLL から、読み込む |
| `$(SolutionDir)` | `.sln` があるフォルダー。他のプロジェクトのパスを指すのに使う |

!!! note "参照の追加で、起きること"
    プロジェクト参照を足すと Visual Studio は、リンカーの「追加の依存ファイル」に `Engine.lib` を自動で、足します（プロパティ → リンカー → 全般 → 「ライブラリの依存関係のリンク」が `はい`）。手動で `.lib` のパスを書く必要はありません。

`Game` と `Player` にも同じ設定（参照 `Engine`、インクルード `$(SolutionDir)Engine\include`）を行います。

## 公開した物を確かめる

Engine をビルドして <strong>本当にエクスポートされたか</strong>を確かめます。「x64 Native Tools Command Prompt for VS 2022」を開き、次を実行します。

```text
dumpbin /exports MiniEngine\bin\x64\Debug\Engine.dll
```

出力の中に次のような行があれば、成功です（名前の細部は異なります）。

```text
    1    0 00001000 ?Create@Engine@mini@@SAPEAV12@AEBUEngineDesc@2@@Z
    2    1 00001090 ?Destroy@Engine@mini@@SAXPEAV12@@Z
    3    2 000010C0 ?FrameCount@Engine@mini@@QEBA_KXZ
    ...
    ?Log@mini@@YAXW4LogLevel@1@PEBD@Z
    ?SetLogCallback@mini@@YAXP6AXW4LogLevel@1@PEBDPEAX@ZPEAX@Z
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `dumpbin` | MSVC に付属する、実行ファイルの調査ツール。`/exports` でエクスポートの一覧を出す |
| 名前の飾り（マングリング） | `?Create@Engine@mini@@...` のように C++ の関数名は、<strong>引数の型や名前空間を含む長い名前</strong>に変えられる（同名のオーバーロードを、区別するため）。これが <strong>C# から直接、呼べない</strong>理由で第 25 章の話題の核心 |

## よくあるミス

??? failure "`LNK2001`、`LNK2019`（`mini::Engine::Create` が未解決）"
    使う側が `Engine.lib` をリンクしていない。プロジェクト参照を追加したか確認する。

??? failure "使う側で `dllexport` になってしまう"
    使う側のプロジェクトに `ENGINE_EXPORTS` を定義していないか確認する。この定義は `Engine` プロジェクトにだけ必要。

??? failure "`C4251`（`std::` の型が、DLL インターフェイスを持つ必要）"
    エクスポートするクラスのメンバーに `std::vector` などを置いた。`Impl` に隠す（pimpl）。

??? failure "`Create` したのに、`delete` してクラッシュする"
    利用者が `delete engine` を直接、書いた。`Engine::Destroy` を呼ぶ（コンストラクターを `private` にすると、書けなくなる）。

??? failure "ログが、出力ウィンドウに出ない"
    Visual Studio で、デバッグ実行（`F5`）しているか確認する。`OutputDebugStringA` はデバッガーにつないでいるときだけ見える。

## この章で作ったもの

```text
Engine\include\Engine\Export.h   Log.h   Engine.h
Engine\src\Log.cpp   Engine.cpp
Engine.dll が、Engine::Create / Tick / Destroy と、Log を、エクスポートしている
```

## 次の章へ

次の章（[第 3 章 Engine に DirectX 12 を載せる](03-engine-dx12.md)）では、`Engine::Tick` の中身に <strong>DirectX 12 の描画</strong>を入れます。ウィンドウを 1 色で塗りつぶすところまで、進めます。
