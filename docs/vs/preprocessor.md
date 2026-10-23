---
title: プリプロセッサマクロ
tags:
  - Visual Studio
---

# プリプロセッサマクロ

C++ のビルドではコンパイルの前に**プリプロセッサ**が `#include` や `#define` を処理します。ビルド設定でマクロを定義することで、コードを書き換えずに動作を切り替えることができます。Windows の `min` / `max` 問題を避ける `NOMINMAX`、ImGui の `IMGUI_API`、Debug / Release を分ける `_DEBUG` などゲーム開発でよく出てくるマクロを、Visual Studio での設定方法とあわせてまとめます。

!!! tip "ポイント"
    - マクロは <strong>ソースの `#define`</strong> か <strong>プロジェクトのプロパティ（C/C++ → プリプロセッサ → プリプロセッサの定義）</strong>で定義する。全部のファイルに効かせたいならプロパティ。
    - Windows を使うなら `NOMINMAX` と `WIN32_LEAN_AND_MEAN` は、ほぼ必須。`#include <windows.h>` より前に効いていること。
    - 構成（Debug / Release）ごとに別の定義ができる。設定するときは どの構成に設定しているかを確認。
    - ライブラリとプロジェクトで、定義をそろえる（`_ITERATOR_DEBUG_LEVEL`、Jolt の定義など）。ずれると実行時に壊れる。
    - `_DEBUG` と `NDEBUG` は Visual Studio が自動で定義する。自分の機能スイッチ（`ENABLE_PROFILER` など）もプロパティで切り替えられる。

## マクロの定義のしかた

### プロパティで定義する

1. ソリューション エクスプローラーでプロジェクトを選んで、メニューの<strong>プロジェクト → プロパティ</strong>を開く
2. 上部の構成を「すべての構成」（または Debug / Release）、プラットフォームを「x64」にする
3. C/C++ → プリプロセッサ → プリプロセッサの定義 を開く
4. `;` 区切りで追加する（`NOMINMAX;WIN32_LEAN_AND_MEAN`）。末尾の `%(PreprocessorDefinitions)` は残す（既定の定義が消える）

```text
NOMINMAX;WIN32_LEAN_AND_MEAN;_CRT_SECURE_NO_WARNINGS;%(PreprocessorDefinitions)
```

![C/C++ → プリプロセッサ のページ。先頭がプリプロセッサの定義。既定で `_UNICODE;UNICODE` が入っている](img/props-preprocessor.jpg)

| 設定 | 説明 |
| --- | --- |
| 値付きで定義 | `MY_LEVEL=3` のように `=` をつける（コードでは、`MY_LEVEL` が `3` になる） |
| 値なしで定義 | `NOMINMAX` だけ（`1` として扱われる） |
| 構成ごとの違い | Debug だけ `ENABLE_PROFILER`、のように構成を選んで設定する |
| `%(PreprocessorDefinitions)` | 上位の設定（既定値・プロパティシート）を引き継ぐ。消さない |

### コマンドラインでの指定（/D）

プロパティで設定した内容はコンパイラの `/D` オプションになります。CMake や Ninja で、自分でコンパイラを呼ぶときに使います。

```text
cl /DNOMINMAX /DWIN32_LEAN_AND_MEAN /DMY_LEVEL=3 main.cpp
```

```cmake
target_compile_definitions(app PRIVATE NOMINMAX WIN32_LEAN_AND_MEAN MY_LEVEL=3)
```

### ソースの `#define`

```cpp
#define NOMINMAX
#include <windows.h>
```

| 方法 | 長所 | 短所 |
| --- | --- | --- |
| プロパティ・`/D` | 全ファイルに効く。書き忘れがない | プロジェクトの設定を見ないと分からない |
| ソースの `#define` | コードを見れば、分かる | ファイルごとに書く必要がある。`#include` より前に書かないと効かない |
| 共通ヘッダ | まとめて書ける | include の順番に依存して、ずれやすい |

!!! warning "ソースで定義するなら include より前"
    `#include <windows.h>` の後に `#define NOMINMAX` と書いても、もう手遅れです（`windows.h` が、`min` / `max` マクロを定義済み）。プロパティで全体に定義するのが、確実です。

### プロパティ シート

複数のプロジェクトで同じマクロを使うなら プロパティ シート（`.props`）にまとめると、1 か所の修正で全プロジェクトに反映できます。`Directory.Build.props` をソリューションのフォルダーに置くと自動で、配下の全プロジェクトに適用されます。

```xml
<Project>
  <ItemDefinitionGroup>
    <ClCompile>
      <PreprocessorDefinitions>NOMINMAX;WIN32_LEAN_AND_MEAN;%(PreprocessorDefinitions)</PreprocessorDefinitions>
    </ClCompile>
  </ItemDefinitionGroup>
</Project>
```

## Windows のマクロ

### NOMINMAX

`<windows.h>` は**`min` と `max` をマクロとして定義**します。すると、`std::min` や `std::max` が構文エラーになります。

```cpp
#include <windows.h>
#include <algorithm>

int a = std::min(1, 2);
```

```text
error C2589: '(': '::' の右側のトークンが正しくありません
```

| 対策 | 説明 |
| --- | --- |
| `NOMINMAX` を定義（推奨） | `min` / `max` マクロを定義させない。`std::min` が普通に使える |
| `(std::min)(a, b)` | カッコでマクロの展開を避ける。応急処置 |
| `#undef min` | あとから消す。他のヘッダへの影響が読みにくい |

`NOMINMAX` は最初からプロパティに入れておくのが、定石です。

### WIN32_LEAN_AND_MEAN

`<windows.h>` が読み込むあまり使わないヘッダ（`winsock.h`、`ole2.h`、`commdlg.h` など）を省略します。コンパイルが速くなり`winsock.h` と `winsock2.h` の衝突も防げます。

| 効果 | 説明 |
| --- | --- |
| ビルドが速くなる | 読むヘッダが、減る（[ビルド時間の最適化](../optimize/build-time.md)） |
| Winsock の衝突を防ぐ | `winsock2.h` を使うとき `windows.h` が古い `winsock.h` を先に読むと、再定義エラーになる |
| 注意 | `shellapi.h`、`ole2.h`、`commdlg.h` などが必要なら自分で include する |

### そのほかの Windows 関連

| マクロ | 効果 |
| --- | --- |
| `VC_EXTRALEAN` | `WIN32_LEAN_AND_MEAN` よりさらに省略（古い MFC 由来） |
| `NOGDI` | GDI（描画 API）を読まない。`DrawText` などのマクロ衝突を避けられる |
| `STRICT` | ハンドルの型を厳密にする（最近は、既定でオン） |
| `UNICODE` / `_UNICODE` | `CreateWindow` などが、`W` 版（UTF-16）になる。Visual Studio は既定で定義。[Windows API と文字コード](../encoding/windows-api.md) |
| `_WIN32_WINNT` / `WINVER` | 対象の Windows のバージョン。新しい API を使うときに必要。SDK の `sdkddkver.h` で設定 |
| `WIN32` / `_WIN32` / `_WIN64` | コンパイラや Visual Studio が、自動で定義。OS の判定に使う |

## CRT・標準ライブラリ

### _CRT_SECURE_NO_WARNINGS

`strcpy`、`sprintf`、`fopen` などの**古い C の関数**を使うと MSVC が、警告 C4996（「`strcpy_s` を使いなさい」）を出します。

| 対策 | 説明 |
| --- | --- |
| `_CRT_SECURE_NO_WARNINGS` を定義 | 警告を消す。ただし、危険な関数のままなので注意 |
| 安全な関数に置き換える | `std::string`、`std::format`、`std::filesystem`、`std::fstream` などC++ の機能を使う |

警告を消すだけにせずそもそも古い C の関数を使わないのが、本来の対応です。

### _USE_MATH_DEFINES

`M_PI` のような数学の定数（`<cmath>`）を使えるようにします。

```cpp
#define _USE_MATH_DEFINES
#include <cmath>
```

C++20 以降は `<numbers>` の `std::numbers::pi_v<float>` を使うほうが標準で、移植性があります。

### _ITERATOR_DEBUG_LEVEL

標準ライブラリのイテレータの検査（範囲外アクセスなどを実行時に検出）の強さです。

| 値 | 意味 |
| --- | --- |
| 0 | 検査なし（Release の既定） |
| 1 | 検査あり（軽め） |
| 2 | 検査あり（Debug の既定）。遅い |

!!! warning "ライブラリとプロジェクトで、値をそろえる"
    異なる値でビルドしたオブジェクトをリンクすると、`LNK2038`（不一致が検出されました）になります。外部ライブラリを Release で、自分のプロジェクトを Debug でビルドすると、起きます（[よくあるエラー](errors.md)）。

### そのほか

| マクロ | 効果 |
| --- | --- |
| `_HAS_EXCEPTIONS=0` | 標準ライブラリの例外を無効にする（`/EHs-c-` と組み合わせ）。例外を使わないゲームで |
| **`_SILENCE_*_DEPRECATION_WARNING` | 特定の非推奨の警告を消す。警告を消す前に置き換えを検討** |
| `_CRTDBG_MAP_ALLOC` | メモリリークの行番号つきの報告（[デバッグ](debugging.md)） |
| `_HAS_CXX23` など | 標準ライブラリの対応状況（通常は、`/std:c++latest` で自動） |
| `NDEBUG` | assert を無効にする（Release で、自動定義） |
| `_DEBUG` | Debug で、自動定義。デバッグ専用のコードの切り替え |

## Debug と Release の切り替え

| マクロ | 定義される構成 | 用途 |
| --- | --- | --- |
| **`_DEBUG`** | Debug（Visual Studio が、自動で） | デバッグ専用のコード（検査、ログ） |
| `NDEBUG` | Release（自動で） | `assert` の無効化。ターゲット製品用 |

```cpp
#ifdef _DEBUG
  std::println("debug: x = {}", x);
#endif

#ifndef NDEBUG
  CheckInvariants();
#endif
```

| 注意 | 説明 |
| --- | --- |
| `_DEBUG` と `NDEBUG` は両方とも未定義にもできる | 構成を自作した場合は、どちらを定義するかを決める |
| `#ifdef` の中身はコンパイルされない | Release でビルドエラーになる、Debug だけにある変数に注意 |
| assert | `NDEBUG` で、消える。副作用のある式を入れない |

## 自分で作る機能スイッチ

**コードを書き換えず**に機能のオン・オフをビルド設定で切り替えられます。

```cpp
#ifdef ENABLE_PROFILER
#define PROFILE_SCOPE(name) ProfileScope scope_##__LINE__(name)
#else
#define PROFILE_SCOPE(name)
#endif
```

| 用途 | マクロの例 |
| --- | --- |
| プロファイラーの有効化 | `ENABLE_PROFILER`（Debug と Profile 構成だけ） |
| デバッグ描画 | `ENABLE_DEBUG_DRAW` |
| チートコマンド・開発メニュー | `ENABLE_DEV_MENU`（製品では、無効） |
| ログのレベル | `LOG_LEVEL=2` |
| プラットフォームの切り替え | `PLATFORM_WINDOWS`、`PLATFORM_SWITCH` |

ビルド構成を 3 つ（Debug / Profile / Release）にして、Profile には最適化 + プロファイラーだけを有効にする、という使い方がよくあります（[プロファイラー](profiler.md)）。

### 注意

| 注意 | 説明 |
| --- | --- |
| マクロの名前の衝突 | `DEBUG`、`ERROR`、`min` などの短い名前は他のライブラリと衝突。プレフィックス（`MYGAME_`）をつける |
| `#if` と `#ifdef` | `#ifdef X` は「定義されているか」。`#if X` は「値が 0 でないか」（`X=0` で定義したときの挙動が違う） |
| マクロより `constexpr` / `if constexpr` | 型チェックが効く。可能ならそちら |
| 使いすぎ | `#ifdef` だらけは、読みにくい。切り替えは1 か所（インターフェース）にまとめる |

## ライブラリのマクロ

### ImGui の IMGUI_API

**Dear ImGui** は関数の宣言に`IMGUI_API` というマクロを付けています。

```cpp
IMGUI_API bool Button(const char* label, const ImVec2& size = ImVec2(0, 0));
```

既定では `IMGUI_API` は空です。ImGui を DLL にして、エクスポート・インポートしたいときに使います。

| 状況 | 設定 |
| --- | --- |
| 普通にソースをプロジェクトに入れる | 何も設定しない（空のまま） |
| ImGui を DLL にする（DLL 側） | `IMGUI_API=__declspec(dllexport)` を定義 |
| ImGui の DLL を使う（利用側） | `IMGUI_API=__declspec(dllimport)` を定義 |
| ゲーム本体（exe）とツール（DLL）で、ImGui を共有 | 同じ ImGui を共有し、`ImGui::SetCurrentContext` でコンテキストを渡す |

!!! warning "DLL をまたぐとき"
    DLL 側で作った `ImGuiContext` を exe 側から使うには、`ImGui::SetCurrentContext` と `SetAllocatorFunctions` を両方で呼ぶ必要があります（ImGui のグローバル状態が、DLL ごとに別になるため）。詳しくは[Dear ImGui](../libs/imgui/index.md) を見てください。

### ImGui のそのほかのマクロ

`imconfig.h` に書くかプロジェクトの定義で指定します。

| マクロ | 効果 |
| --- | --- |
| `IMGUI_DEFINE_MATH_OPERATORS` | `ImVec2` の `+`、`-`、`*` などの演算子を使えるようにする（`imgui_internal.h` を include する前に定義）。ImGuizmo・ImNodes などで必要 |
| `IMGUI_DISABLE_OBSOLETE_FUNCTIONS` | 古い関数を使えなくする（移行の確認に） |
| `IMGUI_DISABLE_DEMO_WINDOWS` | デモをビルドから除く（サイズ削減） |
| `IMGUI_USER_CONFIG` | `imconfig.h` の代わりに自分の設定ファイルを指定 |
| `ImDrawIdx`（`imconfig.h`） | 頂点インデックスの型（`unsigned short` が既定。65536 頂点を超える描画に `unsigned int`） |
| **`IMGUI_IMPL_*`** | バックエンドの切り替え（`IMGUI_IMPL_WIN32_DISABLE_GAMEPAD` など） |

```text
IMGUI_DEFINE_MATH_OPERATORS;IMGUI_DISABLE_OBSOLETE_FUNCTIONS;%(PreprocessorDefinitions)
```

`imconfig.h` を直接書き換えるとImGui の更新で、衝突します。`IMGUI_USER_CONFIG` で自分のファイルを指す方法が、おすすめです（[Dear ImGui](../libs/imgui/index.md)）。

### 自作ライブラリの API マクロ（DLL）

自分で DLL を作るときのエクスポート・インポートの定番のパターンです。

```cpp
#ifdef MYGAME_BUILD_DLL
#define MYGAME_API __declspec(dllexport)
#else
#define MYGAME_API __declspec(dllimport)
#endif

class MYGAME_API Engine {
 public:
  void Run();
};
```

| 側 | 設定 |
| --- | --- |
| DLL をビルドするプロジェクト | `MYGAME_BUILD_DLL` を定義（プロパティで） |
| DLL を使うプロジェクト | 定義しない（`dllimport` になる） |

Visual Studio の DLL プロジェクトには `プロジェクト名_EXPORTS` が、自動で定義されます。これを使う方法もあります。

### 外部ライブラリのビルドの定義

ライブラリのビルドと使う側で、定義をそろえる必要があるものがあります。

| ライブラリ | 例 | 注意 |
| --- | --- | --- |
| Jolt Physics | `JPH_DEBUG_RENDERER`、`JPH_PROFILE_ENABLED`、`JPH_DOUBLE_PRECISION` | 食い違うとクラスの大きさが変わって、クラッシュ（[Jolt](../libs/jolt/index.md)） |
| ImGui | `IMGUI_DEFINE_MATH_OPERATORS` | ライブラリ側と使う側で、同じ `imconfig.h` を見る |
| simdjson | `SIMDJSON_*` | ビルドのオプション |
| nlohmann/json | `JSON_USE_IMPLICIT_CONVERSIONS=0`、`JSON_NOEXCEPTION` | 全部のファイルで同じ設定 |
| 標準ライブラリ | `_ITERATOR_DEBUG_LEVEL`、`_HAS_EXCEPTIONS` | ライブラリとプロジェクトで、そろえる |

vcpkg や CMake で入れると、ビルドの定義が自動でそろいます。手作業で設定するときはライブラリのドキュメントの「ビルド設定」の節を、必ず読みます。

## コンパイラが定義する定義済みマクロ

| マクロ | 意味 |
| --- | --- |
| **`_MSC_VER`** | MSVC のバージョン（Visual Studio 2026 は `1950` 台） |
| `_MSVC_LANG` | MSVC の C++ の標準（`202302L` など）。`__cplusplus` は `/Zc:__cplusplus` がないと古い値のまま |
| `_M_X64` / `_M_ARM64` | CPU の種類（64 ビット x86 / ARM） |
| `_WIN32` / `_WIN64` | Windows。64 ビットでも `_WIN32` は定義される |
| `__FILE__` / `__LINE__` | ファイル名と行番号（ログ・assert に） |
| `__has_include(<header>)` | ヘッダが、存在するか（C++17）。`#if __has_include(<print>)` |
| **`__cpp_lib_*`** | 標準ライブラリの機能が使えるか（`__cpp_lib_print`、`__cpp_lib_flat_map` など） |

```cpp
#if __has_include(<print>)
#include <print>
#endif

#if defined(_MSC_VER)
#define FORCE_INLINE __forceinline
#else
#define FORCE_INLINE inline __attribute__((always_inline))
#endif
```

## 確認する方法

| 方法 | 説明 |
| --- | --- |
| **プロパティの画面** | 構成・プラットフォームを選んで、値を直接確認 |
| `/P`（プリプロセス結果をファイルに出力） | マクロ展開後のソースを、`.i` ファイルに。どう展開されたかを見る |
| `/showIncludes` | どのヘッダをどの順に読んだか |
| `#pragma message("...")` | コンパイル時にメッセージを出す。`#pragma message("MYLEVEL = " _CRT_STRINGIZE(MY_LEVEL))` |
| `/d1PP`（`/E` と併用） | 展開の様子を詳しく |
| IntelliSense の淡色表示 | `#ifdef` で無効な部分が、灰色になる |

!!! note "IntelliSense が、プロパティの設定を見ていないとき"
    プロパティで定義したマクロは、IntelliSense にも反映されますが、CMake プロジェクトなどでは、反映が遅れることがあります。ビルドして確認します。

## よくあるミス

??? failure "`std::min` / `std::max` がエラーになる"
    **`NOMINMAX`** を定義します（プロパティで、全体に）。

??? failure "`windows.h` の後に `#define NOMINMAX` を書いた"
    手遅れです。プロパティで全体に定義します。

??? failure "`winsock2.h` で、再定義のエラーが大量に出る"
    `WIN32_LEAN_AND_MEAN` を定義するか `winsock2.h` を `windows.h` より先に include します。

??? failure "プリプロセッサの定義を末尾の `%(PreprocessorDefinitions)` ごと消した"
    既定の定義（`_DEBUG`、`WIN32` など）が失われます。`%(PreprocessorDefinitions)` は残します。

??? failure "Debug だけに設定して、Release でエラーになる"
    構成を「すべての構成」にして、設定します。

??? failure "ライブラリと自分のプロジェクトで、`_ITERATOR_DEBUG_LEVEL` が違って `LNK2038`"
    同じ構成（Debug / Release）で、ライブラリをビルドし直します。

??? failure "`IMGUI_DEFINE_MATH_OPERATORS` を `imgui_internal.h` の後に定義した"
    include の前に定義します。プロパティで全体にすると、確実です。

??? failure "短いマクロの名前（`DEBUG`、`ERROR`）が他のライブラリと衝突する"
    プレフィックス（`MYGAME_DEBUG`）をつけます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 全ファイルに効かせるなら プロパティ（C/C++ → プリプロセッサ → プリプロセッサの定義）。`%(PreprocessorDefinitions)` は残す
    - [x] Windows なら`NOMINMAX`・`WIN32_LEAN_AND_MEAN` を最初から定義
    - [x] `_DEBUG` は Debug、`NDEBUG` は Release。機能スイッチは自分で作れる
    - [x] ライブラリとプロジェクトで、定義をそろえる（`_ITERATOR_DEBUG_LEVEL`、Jolt）
    - [x] `IMGUI_API` は DLL をまたぐときだけ。`IMGUI_DEFINE_MATH_OPERATORS` は include の前に
    - [x] 確認は `/P`・`#pragma message`・`/showIncludes`

## 関連ページ

- [Visual Studio（目次）](index.md)
- [C++23 を使えるようにする設定](settings.md)
- [外部ライブラリの入れ方](libraries.md)
- [よくあるエラー](errors.md)
- [ビルド時間の最適化](../optimize/build-time.md)
- [Dear ImGui](../libs/imgui/index.md)
- [Jolt Physics](../libs/jolt/index.md)
