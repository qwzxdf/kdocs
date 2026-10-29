---
title: 第 32 章 EngineApi：C の入口を作る
tags:
  - C#連携
---

# 第 32 章 EngineApi：C の入口を作る

この章では、`EngineApi` プロジェクトに C から呼べる関数を作ります。`Engine`（C++ のクラス）を C の関数と「中身の見えないハンドル」に包んで、C# から呼べる形にします。ここで作る関数の一覧がそのまま次の章の P/Invoke 宣言の元になります。

!!! info "このページを読む前に"
    - [第 31 章 C# から C++ を呼ぶ：連携方式の比較](31-interop-overview.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## クラスをポインター 1 つで表す

第 31 章で見たとおり、C++ のクラスを境界の向こうに直接渡すことはできません。そこで、オブジェクトを「ポインター 1 つ（ハンドル）」で表して、操作はすべて関数にします。

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

`MeEngine*` の中身は、C# からは見えません。C# はこのポインターを受け取って、持っておいて、あとで返すだけです。中身を知っているのは `EngineApi` と `Engine` だけなので、`Engine` の中身を変えても、C# には影響しません。

この形は、Windows API の `HWND` や `HANDLE`、Vulkan の `VkInstance`、SDL の `SDL_Window*` など、多くの C の API が使っている定番の方式です。

## API を作るときの決めごと

関数を書き始める前に全部の関数に共通するルールを決めておきます。あとで「この関数だけ違う」が出てくると、C# 側が書きにくくなるからです。

- 関数は `me_`、型は `Me` で始めます。ほかのライブラリと名前がぶつからないようにするためです。
- 失敗するかもしれない関数は、`MeResult`（中身は `int32_t`）を返します。`ME_OK` は 0 です。
- 戻り値はエラー コードに使ってしまうので、結果は出力引数（ポインター）で返します。
- 使う型は `int32_t`、`uint32_t`、`float`、`void*`、`const char*` だけにします。`bool` は使いません（第 31 章）。
- 例外は関数の中ですべて捕まえて、外に出しません。
- 作ったら必ず `destroy` します。文字列は、呼び出しの間だけ有効です。
- `me_get_api_version()` で、API の版が分かるようにします。

## プロジェクトを設定する

`EngineApi` の設定です。第 2 章で `Engine` に行った設定と同じ手順です。

| 場所 | 項目 | 値 |
| --- | --- | --- |
| 全般 | 構成の種類 | ダイナミック ライブラリ (.dll) |
| 全般 | C++ 言語標準 | ISO C++23 プレビュー（`/std:c++latest`） |
| C/C++ → 全般 | 追加のインクルード ディレクトリ | `$(ProjectDir)include;$(SolutionDir)Engine\include` |
| C/C++ → プリプロセッサ | プリプロセッサの定義 | `ENGINE_API_EXPORTS;_WINDOWS;_USRDLL;%(PreprocessorDefinitions)` |
| C/C++ → 全般 | 警告をエラーとして扱う | はい（`/WX`）。警告レベルは `/W4` |
| C/C++ → コード生成 | ランタイム ライブラリ | Debug は `/MDd`、Release は `/MD` |
| ビルド依存 | プロジェクト参照 | `Engine`（参照を追加すると、インポート ライブラリも自動でリンクされる） |

テンプレートが作った `dllmain.cpp`、`framework.h`、`pch.h`、`pch.cpp` は削除します。

## 公開ヘッダーを書く

`EngineApi\include\EngineApi\EngineApi.h` を純粋な C で書きます。まず、DLL の出し入れと `extern "C"` の準備です。

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

`ME_API` の考え方は、第 2 章の `ENGINE_API` と同じです。`EngineApi` 自身をビルドするときは書き出し、利用する側は読み込みになります。`extern "C"` を `#ifdef __cplusplus` で囲んでいるのは、このヘッダーを C のコンパイラーが読むときにも、エラーにならないようにするためです（C のコンパイラーは `extern "C"` を知りません）。

### 型とエラー コード

```c
/* エンジンを表す、中身の見えないハンドル */
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

`typedef struct MeEngine MeEngine;` は、中身を書かない構造体に名前だけ付ける書き方です（不完全型）。こうしておくと、`MeEngine*` というポインター型だけを使えて、中身は誰にも見えません。ハンドルを作るときの定番の書き方です。

`MeResult` を `int32_t` の別名にしているのは、「これはエラー コードです」と読み手に伝えるためです。C# 側では普通の `int` で受け取れます。0 を成功にするのは、C の世界の慣習に従っています。

`MeLogCallback` は関数ポインターの型で、第 33 章で C# のデリゲートに対応させます。`user_data` は、呼び出す側が好きな値を持たせておくための引数で、コールバックにそのまま返されます（C# では使わないことが多いです）。

### 構造体

```c
/* エンジンの作成時に渡す設定 */
typedef struct MeEngineDesc {
  void*    window;   /* 描画先の HWND */
  uint32_t width;    /* クライアント領域の幅（ピクセル） */
  uint32_t height;   /* クライアント領域の高さ（ピクセル） */
} MeEngineDesc;
```

C# 側にも、同じ並びの構造体を作って渡します（第 33 章）。この並びを変えたら C# 側も変えないといけません。ここをうっかり忘れると、実行時に値が化けるので気をつけてください。

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

`me_get_api_version` は、C# が起動時に「この DLL は自分が期待している版か」を確かめるための関数です。`me_get_last_error` は、直近の失敗の理由を UTF-8 の文字列で返します。スレッドごとに別々に持っているので、複数のスレッドが同時に呼んでも混ざりません。`me_set_log_callback` は、エンジンのログを受け取る関数を登録します。`NULL` を渡すと解除です。

`me_engine_destroy` だけ戻り値がありません。破棄に失敗しても、呼び出し側にできることは何もないからです。`NULL` を渡しても何も起きないようにしておきます。

`me_engine_create` の第 2 引数 `MeEngine** out_engine` は、ポインターへのポインターです。C++ なら `MeEngine*& out_engine` と書くところですが、C には参照がないので、「呼ばれた関数が呼び出し側のポインター変数に値を書き込む」ために、アドレスを渡します。

## 実装する

`EngineApi\src\EngineApi.cpp` を書きます。最初に、例外を止めるための道具を用意します。

### エラーの理由を覚えておく

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

ヘッダーでは宣言だけだった `MeEngine` に、ここで中身を与えています。この中身を知っているのは `EngineApi.cpp` だけです。`thread_local` は、スレッドごとに別の変数を持つ指定で、これのおかげで、あるスレッドで起きたエラーのメッセージが別のスレッドのものと混ざりません。

### 例外を止める

どの関数も `try { ... } catch { ... }` を書くことになるので、1 か所にまとめます。

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

`Guard` は、関数の本体をラムダ式で受け取って、`try` で包んで実行します。本体が例外を投げたら、エラー コードに変えて返します。`catch (...)` は、`std::exception` を継承していない例外も含めて、何でも捕まえます。この関数自体は、絶対に例外を外に出さないので、`noexcept` を付けています。

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

`me_get_last_error` が返すのは、`std::string` の中身へのポインターなので、次に同じスレッドで API を呼ぶまでしか有効ではありません。C# 側は、受け取ったらすぐに文字列へコピーします。

`me_set_log_callback` の `reinterpret_cast` は、`MeLogCallback` と `mini::LogCallback` がまったく同じ形の関数ポインターだから成り立ちます。第 2 章の `LogLevel` は、土台の型が `int32_t` と決めてあるので、値の並び（0、1、2）も大きさも一致しています。この対応が壊れると危険なので、`enum class LogLevel : std::int32_t` と土台の型を明示してあります。もし型の大きさが違うものに変えるなら、`EngineApi` の中に変換用の関数を挟んでください。

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

どの関数も、同じ形をしています。`Guard` にラムダ式を渡し、まず引数を疑い、問題がなければ本来の処理を呼びます。境界の入口では、引数を必ず疑ってください。C# 側のバグで `null` が渡されても、クラッシュさせずに、エラー コードで返せます。

`me_engine_create` は、失敗したときも出力引数が不定にならないように、最初に `*out_engine = nullptr;` で初期化しています。

## 公開された名前を確認する

`EngineApi` をビルドしたら、Visual Studio の開発者コマンド プロンプト（「ツール → コマンド ライン → 開発者コマンド プロンプト」）で、次を実行します。

```bash
dumpbin /exports bin\x64\Debug\EngineApi.dll
```

関数が C の名前のまま並んでいれば成功です。

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

`?me_engine_create@@YA...` のように、`?` や `@` を含む長い名前が並んでいたら、`extern "C"` が効いていません。

`EngineApi.dll` は `Engine.dll` を必要とします。第 1 章で出力先をそろえたので、`bin\x64\Debug\` に両方が並んでいるはずです。片方が欠けると `EngineApi.dll` 自体が読み込めなくなります（原因の見分け方は第 35 章で扱います）。

??? failure "`dumpbin` の名前が長いまま"
    `extern "C"` が付いていません。ヘッダーの `extern "C" {` を閉じ忘れているか、`.cpp` の関数定義が `extern "C"` の外に出ています。

??? failure "`LNK2019`（`mini::Engine::Create` が未解決）"
    `Engine` へのプロジェクト参照がありません。または、`Engine` 側の `ENGINE_API`（`dllexport`）が付いていません。第 2 章を見直してください。

??? failure "`C4190` の警告（`extern "C"` の関数が C++ の型を返す）"
    公開ヘッダーに C++ の型（`std::string` やクラス）を書いています。`EngineApi.h` は純粋な C で書きます。

??? failure "`MeEngine` の定義が重複する"
    ヘッダーで `struct MeEngine { ... };` と中身まで書いています。ヘッダーには宣言だけを置き、定義は `.cpp` に書きます。

## この API の作りが、あとで効いてくる理由

- ハンドルにしておいたので、`Engine` の中身を自由に変えられます。C# は影響を受けません。
- すべての関数が `Guard` を通るので、C++ の例外が境界を越えません。クラッシュではなく、エラー コードになります。
- 戻り値のエラー コードと `me_get_last_error` の組み合わせは、どの言語からでも同じ形で扱えます。
- `me_get_api_version` があるので、C# と C++ のビルドがずれていても、起動時に見つけられます。

次の章では、この C の関数を C# から呼び出します。

[第 33 章 P/Invoke で C# から呼ぶ](33-pinvoke.md) へ進みます。
