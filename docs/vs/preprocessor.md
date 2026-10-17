---
title: プリプロセッサマクロ
tags:
  - Visual Studio
---

# プリプロセッサマクロ

C++ のビルドでは、コンパイルの前に、**プリプロセッサ**が `#include` や `#define` を処理します。**ビルド設定で、マクロを定義する**ことで、**コードを書き換えずに、動作を切り替える**ことができます。Windows の `min` / `max` 問題を避ける **`NOMINMAX`**、ImGui の **`IMGUI_API`**、Debug / Release を分ける **`_DEBUG`** など、**ゲーム開発でよく出てくるマクロ**を、Visual Studio での設定方法とあわせてまとめます。

!!! tip "ポイント"
    - マクロは、<strong>ソースの `#define`</strong> か、<strong>プロジェクトのプロパティ（C/C++ → プリプロセッサ → プリプロセッサの定義）</strong>で定義する。<strong>全部のファイルに効かせたいなら、プロパティ</strong>。
    - Windows を使うなら、<strong>`NOMINMAX`</strong> と <strong>`WIN32_LEAN_AND_MEAN`</strong> は、<strong>ほぼ必須</strong>。<strong>`#include <windows.h>` より前に</strong>効いていること。
    - <strong>構成（Debug / Release）ごとに、別の定義</strong>ができる。設定するときは、<strong>どの構成に設定しているか</strong>を確認。
    - <strong>ライブラリとプロジェクトで、定義をそろえる</strong>（`_ITERATOR_DEBUG_LEVEL`、Jolt の定義など）。<strong>ずれると、実行時に壊れる</strong>。
    - <strong>`_DEBUG` と `NDEBUG`</strong> は、Visual Studio が自動で定義する。<strong>自分の機能スイッチ（`ENABLE_PROFILER` など）</strong>も、プロパティで切り替えられる。

## マクロの定義のしかた

### プロパティで定義する

1. ソリューション エクスプローラーで**プロジェクトを右クリック → プロパティ**
2. 上部の**構成**を「**すべての構成**」（または Debug / Release）、**プラットフォーム**を「**x64**」にする
3. **C/C++ → プリプロセッサ → プリプロセッサの定義** を開く
4. **`;` 区切り**で追加する（`NOMINMAX;WIN32_LEAN_AND_MEAN`）。末尾の `%(PreprocessorDefinitions)` は、**残す**（既定の定義が消える）

```text
NOMINMAX;WIN32_LEAN_AND_MEAN;_CRT_SECURE_NO_WARNINGS;%(PreprocessorDefinitions)
```

| 設定 | 説明 |
| --- | --- |
| **値付きで定義** | `MY_LEVEL=3` のように `=` をつける（コードでは、`MY_LEVEL` が `3` になる） |
| **値なしで定義** | `NOMINMAX` だけ（`1` として扱われる） |
| **構成ごとの違い** | Debug だけ `ENABLE_PROFILER`、のように、**構成を選んで**設定する |
| **`%(PreprocessorDefinitions)`** | **上位の設定（既定値・プロパティシート）を引き継ぐ**。**消さない** |

### コマンドラインでの指定（/D）

プロパティで設定した内容は、**コンパイラの `/D` オプション**になります。CMake や Ninja で、自分でコンパイラを呼ぶときに使います。

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
| **プロパティ・`/D`** | **全ファイルに効く**。書き忘れがない | プロジェクトの設定を見ないと、分からない |
| **ソースの `#define`** | コードを見れば、分かる | **ファイルごとに書く**必要がある。**`#include` より前**に書かないと、効かない |
| **共通ヘッダ** | まとめて書ける | **include の順番**に依存して、ずれやすい |

!!! warning "ソースで定義するなら、include より前"
    `#include <windows.h>` の**後**に `#define NOMINMAX` と書いても、**もう手遅れ**です（`windows.h` が、`min` / `max` マクロを、定義済み）。**プロパティで、全体に定義**するのが、確実です。

### プロパティ シート

**複数のプロジェクトで同じマクロ**を使うなら、<strong>プロパティ シート（`.props`）</strong>にまとめると、**1 か所の修正**で、全プロジェクトに反映できます。**`Directory.Build.props`** を、ソリューションのフォルダーに置くと、**自動で、配下の全プロジェクト**に適用されます。

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

`<windows.h>` は、**`min` と `max` を、マクロとして定義**します。すると、`std::min` や `std::max` が、**構文エラー**になります。

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
| **`NOMINMAX` を定義**（**推奨**） | `min` / `max` マクロを、**定義させない**。**`std::min` が普通に使える** |
| `(std::min)(a, b)` | カッコで、マクロの展開を避ける。**応急処置** |
| `#undef min` | あとから消す。**他のヘッダへの影響**が読みにくい |

**`NOMINMAX` は、最初からプロパティに入れておく**のが、定石です。

### WIN32_LEAN_AND_MEAN

`<windows.h>` が読み込む、**あまり使わないヘッダ**（`winsock.h`、`ole2.h`、`commdlg.h` など）を、**省略**します。**コンパイルが速く**なり、**`winsock.h` と `winsock2.h` の衝突**も防げます。

| 効果 | 説明 |
| --- | --- |
| **ビルドが速くなる** | 読むヘッダが、減る（[ビルド時間の最適化](../optimize/build-time.md)） |
| **Winsock の衝突を防ぐ** | `winsock2.h` を使うとき、`windows.h` が古い `winsock.h` を先に読むと、**再定義エラー**になる |
| **注意** | `shellapi.h`、`ole2.h`、`commdlg.h` などが必要なら、**自分で include** する |

### そのほかの Windows 関連

| マクロ | 効果 |
| --- | --- |
| **`VC_EXTRALEAN`** | `WIN32_LEAN_AND_MEAN` より、さらに省略（古い MFC 由来） |
| **`NOGDI`** | GDI（描画 API）を、読まない。**`DrawText` などのマクロ衝突**を、避けられる |
| **`STRICT`** | ハンドルの型を、厳密にする（最近は、既定でオン） |
| **`UNICODE` / `_UNICODE`** | `CreateWindow` などが、<strong>`W` 版（UTF-16）</strong>になる。**Visual Studio は、既定で定義**。[Windows API と文字コード](../encoding/windows-api.md) |
| **`_WIN32_WINNT` / `WINVER`** | 対象の Windows のバージョン。**新しい API を使うとき**に、必要。SDK の `sdkddkver.h` で設定 |
| **`WIN32` / `_WIN32` / `_WIN64`** | コンパイラや Visual Studio が、**自動で定義**。OS の判定に使う |

## CRT・標準ライブラリ

### _CRT_SECURE_NO_WARNINGS

`strcpy`、`sprintf`、`fopen` などの**古い C の関数**を使うと、MSVC が、**警告 C4996**（「`strcpy_s` を使いなさい」）を出します。

| 対策 | 説明 |
| --- | --- |
| **`_CRT_SECURE_NO_WARNINGS` を定義** | 警告を消す。**ただし、危険な関数のままなので、注意** |
| **安全な関数に置き換える** | `std::string`、`std::format`、`std::filesystem`、`std::fstream` など、**C++ の機能**を使う |

**警告を消すだけ**にせず、**そもそも、古い C の関数を使わない**のが、本来の対応です。

### _USE_MATH_DEFINES

`M_PI` のような、**数学の定数**（`<cmath>`）を、**使えるようにします**。

```cpp
#define _USE_MATH_DEFINES
#include <cmath>
```

**C++20 以降は、`<numbers>` の `std::numbers::pi_v<float>` を使う**ほうが、標準で、移植性があります。

### _ITERATOR_DEBUG_LEVEL

標準ライブラリの、**イテレータの検査**（範囲外アクセスなどを、実行時に検出）の強さです。

| 値 | 意味 |
| --- | --- |
| **0** | 検査なし（Release の既定） |
| **1** | 検査あり（軽め） |
| **2** | <strong>検査あり（Debug の既定）</strong>。**遅い** |

!!! warning "ライブラリとプロジェクトで、値をそろえる"
    **異なる値でビルドしたオブジェクト**を、リンクすると、<strong>`LNK2038`（不一致が検出されました）</strong>になります。**外部ライブラリを Release で、自分のプロジェクトを Debug でビルド**すると、起きます（[よくあるエラー](errors.md)）。

### そのほか

| マクロ | 効果 |
| --- | --- |
| **`_HAS_EXCEPTIONS=0`** | 標準ライブラリの**例外を、無効**にする（`/EHs-c-` と組み合わせ）。例外を使わないゲームで |
| **`_SILENCE_*_DEPRECATION_WARNING`** | 特定の**非推奨の警告<strong>を、消す。</strong>警告を消す前に、置き換えを検討** |
| **`_CRTDBG_MAP_ALLOC`** | メモリリークの、**行番号つき**の報告（[デバッグ](debugging.md)） |
| **`_HAS_CXX23` など** | 標準ライブラリの対応状況（通常は、`/std:c++latest` で自動） |
| **`NDEBUG`** | **assert を無効**にする（Release で、自動定義） |
| **`_DEBUG`** | **Debug で、自動定義**。**デバッグ専用のコード**の切り替え |

## Debug と Release の切り替え

| マクロ | 定義される構成 | 用途 |
| --- | --- | --- |
| **`_DEBUG`** | **Debug**（Visual Studio が、自動で） | デバッグ専用のコード（検査、ログ） |
| **`NDEBUG`** | **Release**（自動で） | `assert` の無効化。**ターゲット製品用** |

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
| **`_DEBUG` と `NDEBUG` は、両方とも未定義**にも、できる | 構成を自作した場合は、**どちらを定義するか**を決める |
| **`#ifdef` の中身は、コンパイルされない** | **Release でビルドエラー**になる、**Debug だけにある変数**に注意 |
| **assert** | `NDEBUG` で、**消える**。**副作用のある式を、入れない** |

## 自分で作る機能スイッチ

**コードを書き換えず**に、**機能のオン・オフ**を、ビルド設定で切り替えられます。

```cpp
#ifdef ENABLE_PROFILER
#define PROFILE_SCOPE(name) ProfileScope scope_##__LINE__(name)
#else
#define PROFILE_SCOPE(name)
#endif
```

| 用途 | マクロの例 |
| --- | --- |
| **プロファイラーの有効化** | `ENABLE_PROFILER`（Debug と Profile 構成だけ） |
| **デバッグ描画** | `ENABLE_DEBUG_DRAW` |
| **チートコマンド・開発メニュー** | `ENABLE_DEV_MENU`（製品では、無効） |
| **ログのレベル** | `LOG_LEVEL=2` |
| **プラットフォームの切り替え** | `PLATFORM_WINDOWS`、`PLATFORM_SWITCH` |

<strong>ビルド構成を 3 つ（Debug / Profile / Release）</strong>にして、**Profile には、最適化 + プロファイラーだけ**を有効にする、という使い方がよくあります（[プロファイラー](profiler.md)）。

### 注意

| 注意 | 説明 |
| --- | --- |
| **マクロの名前の衝突** | `DEBUG`、`ERROR`、`min` などの**短い名前**は、他のライブラリと衝突。**プレフィックス**（`MYGAME_`）をつける |
| **`#if` と `#ifdef`** | `#ifdef X` は「**定義されているか**」。`#if X` は「**値が 0 でないか**」（`X=0` で定義したときの、挙動が違う） |
| **マクロより、`constexpr` / `if constexpr`** | **型チェックが効く**。**可能なら、そちら** |
| **使いすぎ** | `#ifdef` だらけは、**読みにくい**。切り替えは、**1 か所**（インターフェース）にまとめる |

## ライブラリのマクロ

### ImGui の IMGUI_API

**Dear ImGui** は、関数の宣言に、**`IMGUI_API`** というマクロを付けています。

```cpp
IMGUI_API bool Button(const char* label, const ImVec2& size = ImVec2(0, 0));
```

**既定では、`IMGUI_API` は、空**です。**ImGui を DLL にして**、**エクスポート・インポート**したいときに、使います。

| 状況 | 設定 |
| --- | --- |
| **普通に、ソースをプロジェクトに入れる** | **何も設定しない**（空のまま） |
| <strong>ImGui を DLL にする（DLL 側）</strong> | `IMGUI_API=__declspec(dllexport)` を定義 |
| <strong>ImGui の DLL を使う（利用側）</strong> | `IMGUI_API=__declspec(dllimport)` を定義 |
| **ゲーム本体（exe）と、ツール（DLL）で、ImGui を共有** | **同じ ImGui を共有**し、**`ImGui::SetCurrentContext`** で、コンテキストを渡す |

!!! warning "DLL をまたぐとき"
    **DLL 側で作った `ImGuiContext` を、exe 側から使う**には、**`ImGui::SetCurrentContext` と `SetAllocatorFunctions`** を、**両方で呼ぶ**必要があります（ImGui のグローバル状態が、DLL ごとに別になるため）。詳しくは、[Dear ImGui](../libs/imgui/index.md) を見てください。

### ImGui のそのほかのマクロ

`imconfig.h` に書くか、**プロジェクトの定義**で指定します。

| マクロ | 効果 |
| --- | --- |
| **`IMGUI_DEFINE_MATH_OPERATORS`** | `ImVec2` の `+`、`-`、`*` などの**演算子**を、使えるようにする（**`imgui_internal.h` を include する前**に定義）。ImGuizmo・ImNodes などで必要 |
| **`IMGUI_DISABLE_OBSOLETE_FUNCTIONS`** | **古い関数を、使えなくする**（移行の確認に） |
| **`IMGUI_DISABLE_DEMO_WINDOWS`** | デモを、ビルドから除く（サイズ削減） |
| **`IMGUI_USER_CONFIG`** | `imconfig.h` の代わりに、**自分の設定ファイル**を指定 |
| <strong>`ImDrawIdx`（`imconfig.h`）</strong> | 頂点インデックスの型（`unsigned short` が既定。**65536 頂点を超える**描画に、`unsigned int`） |
| **`IMGUI_IMPL_*`** | バックエンドの切り替え（`IMGUI_IMPL_WIN32_DISABLE_GAMEPAD` など） |

```text
IMGUI_DEFINE_MATH_OPERATORS;IMGUI_DISABLE_OBSOLETE_FUNCTIONS;%(PreprocessorDefinitions)
```

**`imconfig.h` を直接書き換える**と、**ImGui の更新で、衝突**します。**`IMGUI_USER_CONFIG`** で、**自分のファイル**を指す方法が、おすすめです（[Dear ImGui](../libs/imgui/index.md)）。

### 自作ライブラリの API マクロ（DLL）

自分で DLL を作るときの、**エクスポート・インポート**の定番のパターンです。

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
| **DLL をビルドするプロジェクト** | `MYGAME_BUILD_DLL` を定義（**プロパティで**） |
| **DLL を使うプロジェクト** | 定義しない（`dllimport` になる） |

Visual Studio の DLL プロジェクトには、`プロジェクト名_EXPORTS` が、**自動で定義**されます。これを使う方法もあります。

### 外部ライブラリのビルドの定義

**ライブラリのビルドと、使う側で、定義をそろえる**必要があるものがあります。

| ライブラリ | 例 | 注意 |
| --- | --- | --- |
| **Jolt Physics** | `JPH_DEBUG_RENDERER`、`JPH_PROFILE_ENABLED`、`JPH_DOUBLE_PRECISION` | **食い違うと、クラスの大きさが変わって、クラッシュ**（[Jolt](../libs/jolt/index.md)） |
| **ImGui** | `IMGUI_DEFINE_MATH_OPERATORS` | ライブラリ側と、使う側で、**同じ** `imconfig.h` を見る |
| **simdjson** | `SIMDJSON_*` | ビルドのオプション |
| **nlohmann/json** | `JSON_USE_IMPLICIT_CONVERSIONS=0`、`JSON_NOEXCEPTION` | 全部のファイルで、**同じ設定** |
| **標準ライブラリ** | `_ITERATOR_DEBUG_LEVEL`、`_HAS_EXCEPTIONS` | ライブラリとプロジェクトで、そろえる |

**vcpkg や CMake で入れると、ビルドの定義が、自動でそろい**ます。**手作業で設定する**ときは、**ライブラリのドキュメントの「ビルド設定」の節**を、必ず読みます。

## コンパイラが定義する、定義済みマクロ

| マクロ | 意味 |
| --- | --- |
| **`_MSC_VER`** | MSVC のバージョン（Visual Studio 2022 は `1930` 台） |
| **`_MSVC_LANG`** | MSVC の C++ の標準（`202302L` など）。**`__cplusplus` は、`/Zc:__cplusplus` がないと、古い値のまま** |
| **`_M_X64` / `_M_ARM64`** | CPU の種類（64 ビット x86 / ARM） |
| **`_WIN32` / `_WIN64`** | Windows。**64 ビットでも `_WIN32` は定義される** |
| **`__FILE__` / `__LINE__`** | ファイル名と行番号（ログ・assert に） |
| **`__has_include(<header>)`** | **ヘッダが、存在するか**（C++17）。`#if __has_include(<print>)` |
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
| **プロパティの画面** | 構成・プラットフォームを選んで、**値を直接確認** |
| <strong>`/P`（プリプロセス結果をファイルに出力）</strong> | **マクロ展開後のソース**を、`.i` ファイルに。**どう展開されたか**を見る |
| **`/showIncludes`** | どのヘッダを、どの順に読んだか |
| **`#pragma message("...")`** | **コンパイル時に、メッセージを出す**。`#pragma message("MYLEVEL = " _CRT_STRINGIZE(MY_LEVEL))` |
| <strong>`/d1PP`（`/E` と併用）</strong> | 展開の様子を、詳しく |
| **IntelliSense の淡色表示** | `#ifdef` で無効な部分が、**灰色**になる |

!!! note "IntelliSense が、プロパティの設定を見ていないとき"
    **プロパティで定義したマクロ**は、IntelliSense にも反映されますが、**CMake プロジェクトなどでは、反映が遅れる**ことがあります。**ビルドして**確認します。

## よくあるミス

??? failure "`std::min` / `std::max` がエラーになる"
    **`NOMINMAX`** を定義します（プロパティで、全体に）。

??? failure "`windows.h` の後に `#define NOMINMAX` を書いた"
    **手遅れ**です。**プロパティ**で、全体に定義します。

??? failure "`winsock2.h` で、再定義のエラーが大量に出る"
    **`WIN32_LEAN_AND_MEAN`** を定義するか、`winsock2.h` を、`windows.h` より先に include します。

??? failure "プリプロセッサの定義を、末尾の `%(PreprocessorDefinitions)` ごと、消した"
    **既定の定義**（`_DEBUG`、`WIN32` など）が、失われます。**`%(PreprocessorDefinitions)` は、残します**。

??? failure "Debug だけに設定して、Release でエラーになる"
    <strong>構成を「すべての構成」</strong>にして、設定します。

??? failure "ライブラリと自分のプロジェクトで、`_ITERATOR_DEBUG_LEVEL` が違って、`LNK2038`"
    **同じ構成**（Debug / Release）で、ライブラリをビルドし直します。

??? failure "`IMGUI_DEFINE_MATH_OPERATORS` を、`imgui_internal.h` の後に定義した"
    **include の前**に定義します。**プロパティで全体に**すると、確実です。

??? failure "短いマクロの名前（`DEBUG`、`ERROR`）が、他のライブラリと衝突する"
    **プレフィックス**（`MYGAME_DEBUG`）をつけます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 全ファイルに効かせるなら、<strong>プロパティ（C/C++ → プリプロセッサ → プリプロセッサの定義）</strong>。<strong>`%(PreprocessorDefinitions)` は残す</strong>
    - [x] Windows なら<strong>`NOMINMAX`・`WIN32_LEAN_AND_MEAN`</strong> を、最初から定義
    - [x] <strong>`_DEBUG`</strong> は Debug、<strong>`NDEBUG`</strong> は Release。<strong>機能スイッチ</strong>は自分で作れる
    - [x] <strong>ライブラリとプロジェクトで、定義をそろえる</strong>（<strong>`_ITERATOR_DEBUG_LEVEL`</strong>、Jolt）
    - [x] <strong>`IMGUI_API`</strong> は、<strong>DLL をまたぐとき</strong>だけ。<strong>`IMGUI_DEFINE_MATH_OPERATORS`</strong> は、include の前に
    - [x] 確認は、<strong>`/P`・`#pragma message`・`/showIncludes`</strong>

## 関連ページ

- [Visual Studio（目次）](index.md)
- [C++23 を使えるようにする設定](settings.md)
- [外部ライブラリの入れ方](libraries.md)
- [よくあるエラー](errors.md)
- [ビルド時間の最適化](../optimize/build-time.md)
- [Dear ImGui](../libs/imgui/index.md)
- [Jolt Physics](../libs/jolt/index.md)
