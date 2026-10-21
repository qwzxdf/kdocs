---
title: 第 12 章 EngineApi：C の入口を作る
tags:
  - C#連携
---

# 第 12 章 EngineApi：C の入口を作る

この章では `EngineApi` プロジェクトに <strong>C から呼べる関数</strong>を作ります。`Engine`（C++ のクラス）を<strong>C の関数と不透明なハンドル</strong>に包み C# から呼べる形にします。この章で作る C の関数の一覧が、第 13 章の P/Invoke の宣言の元になります。

## この章の考え方

第 11 章で見たとおり C++ のクラスを境界の向こうへそのまま渡すことはできません。そこで、<strong>クラスのオブジェクトをポインター 1 つ（ハンドル）で表し、操作を関数にします</strong>。

```cpp
// C++ のクラス（境界を越えられない）
Engine* e = Engine::Create(desc);
e->Tick(dt);
Engine::Destroy(e);
```

```c
/* C の関数（境界を越えられる） */
MeEngine* engine;
me_engine_create(&desc, &engine);
me_engine_tick(engine, dt);
me_engine_destroy(engine);
```

`MeEngine*` の中身は C# からは見えません（<strong>不透明</strong>）。C# はこのポインターを受け取って持って、返すだけです。中身を知っているのは `EngineApi` と `Engine` だけです。

この形は Windows API（`HWND`、`HANDLE`）や Vulkan（`VkInstance`）、SDL（`SDL_Window*`）など多くの C の API が使っている、実績のある方式です。

## この章のゴール

- 公開ヘッダー `EngineApi.h` を<strong>純粋な C</strong> で書く。
- 関数ごとに例外を捕まえて、エラー コードを返す。
- 失敗の理由を文字列で取れる。
- `EngineApi.dll` が C の名前で関数を公開していることを確認する。

## 設計の方針

| 方針 | 内容 |
| --- | --- |
| 名前 | 関数は `me_` で始め型は `Me` で始める（他のライブラリと衝突しないように） |
| 戻り値 | 失敗しうる関数は `MeResult`（`int32_t`）を返す。`ME_OK` が 0 |
| 出力 | 戻り値はエラー コードに使うので、結果は<strong>出力引数</strong>（ポインター）で返す |
| 型 | `int32_t`、`uint32_t`、`float`、`void*`、`const char*` だけ。`bool` は使わない |
| 例外 | 関数の中ですべて捕まえる。外には出さない |
| 所有 | `create` したら必ず `destroy`。文字列は呼び出しの間だけ有効 |
| バージョン | `me_get_api_version()` で API の版が分かる |

## 手順 1：プロジェクトの設定

`EngineApi` プロジェクトの設定です。

| 場所 | 項目 | 値 |
| --- | --- | --- |
| 全般 | 構成の種類 | ダイナミック ライブラリ (.dll) |
| 全般 | C++ 言語標準 | ISO C++23 プレビュー（`/std:c++latest`） |
| C/C++ → 全般 | 追加のインクルード ディレクトリ | `$(ProjectDir)include;$(SolutionDir)Engine\include` |
| C/C++ → プリプロセッサ | プリプロセッサの定義 | `ENGINE_API_EXPORTS;_WINDOWS;_USRDLL;%(PreprocessorDefinitions)` |
| C/C++ → 全般 | 警告をエラーとして扱う | はい（`/WX`）、警告レベル `/W4` |
| C/C++ → コード生成 | ランタイム ライブラリ | Debug: `/MDd`、Release: `/MD` |
| ビルド依存 | プロジェクト参照 | `Engine`（参照の追加。インポート ライブラリが自動でリンクされる） |

第 2 章で `Engine` に対して行った設定と同じ手順です。`dllmain.cpp`、`framework.h`、`pch.h`、`pch.cpp` は削除します。

## 手順 2：公開ヘッダー

`EngineApi\include\EngineApi\EngineApi.h`:

```c
#pragma once

#include <stdint.h>

/* DLL の書き出し／読み込みの切り替え */
#if defined(ENGINE_API_EXPORTS)
#define ME_API __declspec(dllexport)
#else
#define ME_API __declspec(dllimport)
#endif

#ifdef __cplusplus
extern "C" {
#endif
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `#include <stdint.h>` | C の標準の整数型。C++ の `<cstdint>` の C 版 |
| `ME_API` | 第 2 章の `ENGINE_API` と同じ考え方。`EngineApi` のビルド時は書き出し利用側は読み込み |
| `#ifdef __cplusplus` | C++ のコンパイラーが読むときだけ有効なブロック。`__cplusplus` は C++ のコンパイラーが定義するマクロ |
| `extern "C" {` | この範囲の関数を C の名前規則（名前修飾なし）で扱う。C のコンパイラーは `extern "C"` を知らないので、`#ifdef` で囲む |

### 型とエラー コード

```c
/* エンジンを表す不透明なハンドル（中身は C# から見えない） */
typedef struct MeEngine MeEngine;

/* 結果コード */
typedef int32_t MeResult;
enum {
  ME_OK = 0,
  ME_ERROR_INVALID_ARGUMENT = 1,   /* 引数が不正（null など） */
  ME_ERROR_INIT_FAILED = 2,        /* 初期化に失敗（GPU が非対応など） */
  ME_ERROR_NOT_FOUND = 3,          /* 指定された物が無い */
  ME_ERROR_EXCEPTION = 4,          /* 想定外の例外 */
  ME_ERROR_INVALID_STATE = 5       /* 今は呼べない状態 */
};

/* ログの重大度 */
typedef int32_t MeLogLevel;
enum { ME_LOG_INFO = 0, ME_LOG_WARNING = 1, ME_LOG_ERROR = 2 };

/* ログを受け取る関数の型 */
typedef void (*MeLogCallback)(MeLogLevel level, const char* message, void* user_data);
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `typedef struct MeEngine MeEngine;` | <strong>不完全型</strong>（中身を宣言しない構造体）に別名を付ける。`MeEngine*` というポインター型だけが使え中身は見えない。ハンドルの定番の書き方 |
| `typedef int32_t MeResult;` | 戻り値を `int32_t` の別名にする。意味が分かりやすくなり C# 側も `int` で受けられる |
| 無名の `enum { … };` | 名前付きの定数群。C の `enum` は `int` として扱える。`ME_OK` を 0 にするのは「0 が成功」の慣習 |
| `MeLogCallback` | <strong>関数ポインター</strong>の型。`void (*名前)(引数…)` の形。C# からはデリゲートが対応する（第 13 章） |
| `void* user_data` | 呼び出し側が好きな値を持たせるための引数。コールバックにそのまま返される（C# 側では使わないことが多い） |

### 構造体

```c
/* エンジンの作成時に渡す設定 */
typedef struct MeEngineDesc {
  void*    window;   /* 描画先の HWND */
  uint32_t width;    /* クライアント領域の幅（ピクセル） */
  uint32_t height;   /* クライアント領域の高さ（ピクセル） */
} MeEngineDesc;
```

C# から同じ並びの構造体を作って渡します（第 13 章）。<strong>並びを変えたら C# 側も変える</strong>必要があります。

### 関数

```c
/* 共通 */
ME_API int32_t     me_get_api_version(void);
ME_API const char* me_get_last_error(void);
ME_API void        me_set_log_callback(MeLogCallback callback, void* user_data);

/* エンジン */
ME_API MeResult me_engine_create(const MeEngineDesc* desc, MeEngine** out_engine);
ME_API void     me_engine_destroy(MeEngine* engine);
ME_API MeResult me_engine_resize(MeEngine* engine, uint32_t width, uint32_t height);
ME_API MeResult me_engine_tick(MeEngine* engine, float delta_seconds);
ME_API MeResult me_engine_get_frame_count(const MeEngine* engine, uint64_t* out_count);

#ifdef __cplusplus
}  /* extern "C" */
#endif
```

| 関数 | 役割 |
| --- | --- |
| `me_get_api_version` | API の版を返す。C# が DLL の版と合っているか起動時に確かめる |
| `me_get_last_error` | 直近の失敗の理由（UTF-8 の文字列）を返す。スレッドごとに持つ。なければ空文字列 |
| `me_set_log_callback` | エンジンのログを受け取る関数を登録する。`NULL` で解除 |
| `me_engine_create` | エンジンを作りハンドルを `*out_engine` に書く |
| `me_engine_destroy` | エンジンを破棄する。`NULL` を渡しても何もしない。<strong>戻り値なし</strong>（失敗しても、できることがないので） |
| `me_engine_resize` | 描画面の大きさを変える |
| `me_engine_tick` | 1 フレーム進める |
| `me_engine_get_frame_count` | 経過フレーム数を取る |

`me_engine_create` の第 2 引数 `MeEngine** out_engine` は<strong>ポインターへのポインター</strong>です。C++ の `MeEngine*& out_engine`（ポインターの参照）と同じ役割で、「呼ばれた関数が呼ぶ側のポインター変数に値を書き込む」ためです。C には参照がないのでポインターのポインターを使います。

## 手順 3：実装

`EngineApi\src\EngineApi.cpp` を書きます。まず、<strong>例外を止めるための道具</strong>から。

### 失敗の理由を保持する

```cpp
#include "EngineApi/EngineApi.h"

#include <exception>
#include <string>

#include "Engine/Engine.h"
#include "Engine/Log.h"

// MeEngine の実体。C++ の Engine を 1 つ持つだけの入れ物。
struct MeEngine {
  mini::Engine* engine = nullptr;
};

namespace {

// 直近のエラー メッセージ。スレッドごとに別の領域を持つ（thread_local）。
thread_local std::string g_last_error;

void SetLastError(const char* message) {
  g_last_error = message ? message : "";
}

}  // namespace
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `struct MeEngine { … };` | ヘッダーでは宣言だけだった構造体の<strong>定義</strong>。ここ（`EngineApi.cpp`）だけが中身を知っている |
| `thread_local` | スレッドごとに別々の変数を持つ。複数のスレッドが同時に API を呼んでもエラーメッセージが混ざらない |
| 無名 `namespace` | このファイルの中だけで使う関数・変数 |

### 例外を止める

すべての関数が同じ形（`try { … } catch { … }`）を使うので、マクロにまとめます。

```cpp
namespace {

// 関数の本体を包み、例外をエラー コードに変換する。
template <typename Fn>
MeResult Guard(Fn&& body) noexcept {
  try {
    return body();
  } catch (const std::exception& e) {
    SetLastError(e.what());
    return ME_ERROR_EXCEPTION;
  } catch (...) {
    SetLastError("不明な例外");
    return ME_ERROR_EXCEPTION;
  }
}

}  // namespace
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Guard` | 関数の本体（ラムダ式）を受け取り `try` で包んで呼ぶ。本体が例外を投げたらエラー コードに変えて返す |
| `noexcept` | この関数は例外を投げない、という約束。`Guard` が `catch (...)` で全部を捕まえるので、守られる |
| `catch (...)` | あらゆる型の例外を捕まえる。`std::exception` を継承しない例外もあるため |
| `Fn&&` | 転送参照。ラムダ式をコピーせずに受け取る |

### 共通の関数

```cpp
extern "C" {

int32_t me_get_api_version(void) {
  return 1;
}

const char* me_get_last_error(void) {
  return g_last_error.c_str();
}

void me_set_log_callback(MeLogCallback callback, void* user_data) {
  if (!callback) {
    mini::SetLogCallback(nullptr, nullptr);
    return;
  }
  // 型を合わせて、Engine のログ コールバックとして登録する。
  mini::SetLogCallback(reinterpret_cast<mini::LogCallback>(callback), user_data);
}
```

| 部分 | 説明 |
| --- | --- |
| `extern "C" { … }` | 実装側でも同じ宣言の範囲で `extern "C"` にする（ヘッダーで宣言済みなら、実装側は省略できるが書いておくと分かりやすい） |
| `g_last_error.c_str()` | `std::string` の中身を `const char*` で返す。<strong>次に同じスレッドで API を呼ぶまで有効</strong>。C# 側はすぐに文字列へコピーする |
| `reinterpret_cast<mini::LogCallback>` | `MeLogCallback` と `mini::LogCallback` は<strong>同じ形</strong>（`void(*)(int32_t, const char*, void*)`）にしてあるので、変換できる。第 2 章の `LogLevel` を `enum class LogLevel : int32_t` にしておくとこの変換が安全になる |

!!! note "ログの型をそろえておく"
    第 2 章の `LogLevel` は `enum class LogLevel { Info, Warning, Error };` で、土台の型は `int`（32 ビット）です。`MeLogLevel`（`int32_t`）と同じ大きさで値も `0, 1, 2` で一致しているので、`reinterpret_cast` で関数ポインターを読み替えられます。この対応を壊さないために `Engine` 側で `enum class LogLevel : std::int32_t` と土台の型を<strong>明示</strong>しておくと安全です（第 2 章の宣言を、そのように直してください）。大きさが違う型に変えたときは `EngineApi` の中に変換用の関数（トランポリン）を書きます。

### エンジンの操作

```cpp
MeResult me_engine_create(const MeEngineDesc* desc, MeEngine** out_engine) {
  return Guard([&]() -> MeResult {
    if (!desc || !out_engine) {
      SetLastError("desc または out_engine が null");
      return ME_ERROR_INVALID_ARGUMENT;
    }
    if (!desc->window || desc->width == 0 || desc->height == 0) {
      SetLastError("window が null、または大きさが 0");
      return ME_ERROR_INVALID_ARGUMENT;
    }
    *out_engine = nullptr;

    mini::EngineDesc engine_desc;
    engine_desc.window = static_cast<mini::NativeWindow>(desc->window);
    engine_desc.width = desc->width;
    engine_desc.height = desc->height;

    mini::Engine* engine = mini::Engine::Create(engine_desc);
    if (!engine) {
      SetLastError("Engine の作成に失敗しました。ログを確認してください");
      return ME_ERROR_INIT_FAILED;
    }
    *out_engine = new MeEngine{engine};
    return ME_OK;
  });
}

void me_engine_destroy(MeEngine* engine) {
  if (!engine) return;
  // 破棄で例外が出ても、外へは出さない
  Guard([&]() -> MeResult {
    mini::Engine::Destroy(engine->engine);
    delete engine;
    return ME_OK;
  });
}

MeResult me_engine_resize(MeEngine* engine, uint32_t width, uint32_t height) {
  return Guard([&]() -> MeResult {
    if (!engine) {
      SetLastError("engine が null");
      return ME_ERROR_INVALID_ARGUMENT;
    }
    engine->engine->Resize(width, height);
    return ME_OK;
  });
}

MeResult me_engine_tick(MeEngine* engine, float delta_seconds) {
  return Guard([&]() -> MeResult {
    if (!engine) {
      SetLastError("engine が null");
      return ME_ERROR_INVALID_ARGUMENT;
    }
    engine->engine->Tick(delta_seconds);
    return ME_OK;
  });
}

MeResult me_engine_get_frame_count(const MeEngine* engine, uint64_t* out_count) {
  return Guard([&]() -> MeResult {
    if (!engine || !out_count) {
      SetLastError("引数が null");
      return ME_ERROR_INVALID_ARGUMENT;
    }
    *out_count = engine->engine->FrameCount();
    return ME_OK;
  });
}

}  // extern "C"
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `[&]() -> MeResult { … }` | ラムダ式。`[&]` は外の変数を参照で使う。`-> MeResult` は戻り値の型の明示 |
| 引数の検査 | <strong>境界の入口では、引数を必ず疑う</strong>。C# 側のバグで `null` が来ても、クラッシュさせずエラー コードで返す |
| `*out_engine = nullptr;` | 失敗したときも出力引数が不定にならないように先に初期化する |
| `new MeEngine{engine}` | ハンドルの実体をヒープに作る。`destroy` で `delete` する |
| `me_engine_destroy` の戻り値なし | 破棄の失敗は、呼び出し側にできることがないので `void`。ただし、例外は `Guard` で止める |

## 手順 4：ビルドして公開された名前を確認する

`EngineApi` をビルドします。成功したら<strong>Visual Studio の開発者コマンド プロンプト</strong>（「ツール → コマンド ライン → 開発者コマンド プロンプト」）で、次を実行します。

```bash
dumpbin /exports bin\x64\Debug\EngineApi.dll
```

次のように<strong>C の名前のまま</strong>で並びます。

```text
    ordinal hint RVA      name
          1    0 00001000 me_engine_create
          2    1 00001050 me_engine_destroy
          3    2 000010A0 me_engine_get_frame_count
          4    3 00001100 me_engine_resize
          5    4 00001150 me_engine_tick
          6    5 00001190 me_get_api_version
          7    6 000011A0 me_get_last_error
          8    7 000011B0 me_set_log_callback
```

`?` や `@` を含む長い名前（`?Create@Engine@mini@@…`）なら `extern "C"` が効いていません。

## 手順 5：Engine.dll を一緒に置く

`EngineApi.dll` は `Engine.dll` を必要とします。第 1 章で出力先をそろえたので、`bin\x64\Debug\` に両方が並んでいます。<strong>どちらかが欠けても `EngineApi.dll` は読み込めません</strong>（第 15 章で、エラーの見分け方を扱います）。

## 動作確認

| 見る所 | 期待する結果 |
| --- | --- |
| ビルド | `EngineApi` がエラー、警告なしで通る |
| `dumpbin /exports` | 8 つの関数が C の名前で並ぶ |
| `bin\x64\Debug\` | `Engine.dll`、`EngineApi.dll`、`EngineApi.lib` がそろう |

## よくあるミス

??? failure "`dumpbin` に関数名が長い形で出る"
    `extern "C"` が付いていない。ヘッダーの `#ifdef __cplusplus extern "C" {` が閉じていないか `.cpp` の側の定義が `extern "C"` の外にある。

??? failure "`LNK2019`（`mini::Engine::Create` が未解決）"
    `Engine` へのプロジェクト参照が無い。または、`Engine` の `ENGINE_API`（`dllexport`）が付いていない。第 2 章を確認する。

??? failure "`C4190`（`extern "C"` の関数が C++ の型を返す）"
    公開ヘッダーに C++ の型（`std::string`、クラス）を書いた。`EngineApi.h` は<strong>純粋な C</strong>で書く。

??? failure "`MeEngine` の定義が重複する"
    ヘッダーで `struct MeEngine { … };` と定義してしまった。ヘッダーでは宣言だけ（`typedef struct MeEngine MeEngine;`）、定義は `.cpp` に置く。

## 設計のふりかえり

この API の設計で後の章に効いてくる点です。

| 設計 | 効果 |
| --- | --- |
| ハンドル（不透明なポインター） | C# は、`Engine` の変更の影響を受けない。C++ 側は自由に内部を変えられる |
| すべての関数が `Guard` を通る | 例外が境界を越えない。クラッシュではなくエラー コードになる |
| 出力引数 + 戻り値のエラー コード | どの言語からも同じ形で扱える |
| `me_get_last_error` | エラー コードだけでは足りない詳細をあとから取れる |
| `me_get_api_version` | C# と C++ のビルドのずれを起動時に検出できる |

## 次の章へ

次の章（[第 13 章 P/Invoke で C# から呼ぶ](13-pinvoke.md)）では、この C の関数を C# から呼び出します。`LibraryImport`、構造体の受け渡し文字列、`SafeHandle`、コールバックを順に学びます。
