---
title: ビルドと CMake の構成
tags:
  - 設計
  - 実践
---

# ビルドと CMake の構成

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
</div>

**ビルド**は、ソースコードを、実行できるファイルにする作業です。ゲームが大きくなると、**ビルドの設計**（どのファイルを、どのまとまりで、どの順番で作るか）が、**開発の快適さを左右**します。「ビルドに 10 分かかる」「ヘッダを 1 行直しただけで、全部がビルドし直される」「他の人の PC で、ビルドが通らない」といった問題は、**コードの設計（[ヘッダとソースの分け方](../foundations/header-source.md)、[レイヤー](../foundations/layers.md)）と、ビルドの構成**の両方で、防げます。このページは、ヘッダとソースの分離の**延長**として、**ビルドを速く、再現可能に、整理して保つ**考え方を説明します（Visual Studio の操作は [Visual Studio](../../vs/index.md)、CMake の基本は [CMake で使う](../../vs/cmake.md)）。

!!! tip "ポイント"
    - **ビルドが遅い原因は、ほとんど `#include`**。ヘッダに入れる `#include` を減らす（前方宣言、PImpl）。
    - コードを**ライブラリ（静的ライブラリ）に分ける**と、**変更した部分だけ**がビルドされ、**依存の向き**も守りやすい。
    - **ビルドの設定は、ファイルに書いて Git に入れる**（`CMakeLists.txt`、`vcxproj`、`vcpkg.json`）。**手で設定した画面の内容は、他の人に伝わらない**。
    - **外部ライブラリは、バージョンを固定する**（vcpkg のマニフェスト、Git のタグ）。
    - 「**クローンして、1 コマンドでビルドできる**」状態を、常に保つ。

## ビルドが遅くなる原因

| 原因 | 説明 | 対策 |
| --- | --- | --- |
| **ヘッダの `#include` が多い** | 1 つのヘッダを直すと、それを include した全ファイルが再ビルド | 前方宣言、PImpl、`.cpp` で include |
| **巨大なヘッダ**（`<windows.h>`、nlohmann/json、`<regex>`） | include するだけで、何万行も読む | `.cpp` だけで include。プリコンパイル済みヘッダ |
| **テンプレートの多用** | コンパイルのたびに、展開される | `extern template`、実装を `.cpp` に |
| **1 つのファイルが巨大** | 1 行直すと、全体が再コンパイル | ファイルを分ける |
| **並列ビルドをしていない** | 1 コアしか使っていない | `/MP`（MSVC）、`ninja` |
| **全部が 1 つのプロジェクト** | どれを変えても、全部ビルド | ライブラリに分ける |

### 計測する

「ビルドが遅い」と感じたら、**どこで時間を使っているか**を、測ります。

| 道具 | 説明 |
| --- | --- |
| **MSVC の `/Bt+`**（C/C++ → コマンド ライン） | ファイルごとのコンパイル時間を表示 |
| <strong>Visual Studio の「ビルド インサイト」</strong> | 時間のかかる `#include` や、テンプレートを可視化 |
| **`/showIncludes`** | ヘッダの include の一覧を出す |
| **ClangBuildAnalyzer** | 時間がかかるヘッダ・テンプレートを、集計する |

## 1. ヘッダを軽くする

| 方法 | 説明 |
| --- | --- |
| **前方宣言**（`class Enemy;`） | ヘッダでは、ポインタ・参照だけで使い、`#include` しない |
| **`.cpp` で `#include`** | 実装でだけ必要なヘッダは、ヘッダに書かない |
| **PImpl** | 外部ライブラリを `.cpp` に隠す（[PImpl](../patterns/pimpl.md)） |
| <strong>「使うものを include」</strong> | 他のヘッダ経由で入ってくるのに頼らない（`include-what-you-use`） |
| **`#pragma once`** | インクルードガード（二重 include の防止） |
| **巨大ヘッダは、プリコンパイル済みヘッダ（PCH）に** | 一度だけコンパイルして、使い回す |

### プリコンパイル済みヘッダ（PCH）

**変更されない巨大なヘッダ**（標準ライブラリ、`<windows.h>`、外部ライブラリ）を、**先に 1 回だけコンパイルして、使い回す**仕組みです。

| 手順（Visual Studio） | 内容 |
| --- | --- |
| ① `pch.h` を作る | `#include <vector>`、`<string>`、`<windows.h>` など、**変更しないもの**だけを書く |
| ② `pch.cpp` を作る | `#include "pch.h"` だけを書く |
| ③ プロパティ → C/C++ → プリコンパイル済みヘッダー | `pch.cpp` は「<strong>作成 (/Yc)</strong>」、他は「<strong>使用 (/Yu)</strong>」、ファイル名は `pch.h` |
| ④ すべての `.cpp` の**最初の行**に `#include "pch.h"` | |

CMake なら `target_precompile_headers(MyGame PRIVATE pch.h)` の 1 行です。

!!! warning "PCH に、自分のよく変わるヘッダを入れない"
    PCH を変更すると、**全部のファイルが再ビルド**になります。標準ライブラリと外部ライブラリだけを入れます。

## 2. コードを、ライブラリに分ける

**一番効果が大きい**ビルドの設計です。コードを、<strong>静的ライブラリ（`.lib`）</strong>のまとまりに分けます。

<div class="anim" data-type="graph" data-label="ライブラリの依存：下の層から積む">
n base base.lib 0 2
# 基盤層（何にも依存しない）
---
n base base.lib 0 2
n engine engine.lib 1 1 new
l engine base new
# エンジン層：base に依存
---
n base base.lib 0 2
n engine engine.lib 1 1
n game game.lib 2 0 new
l engine base
l game engine new
# ゲーム層：engine に依存
---
n base base.lib 0 2
n engine engine.lib 1 1
n game game.lib 2 0
n exe MyGame.exe 3 0 new
l engine base
l game engine
l exe game new
# アプリ：全部をつなぐ。依存の向きは、いつも「上から下」
---
n base base.lib 0 2 hit
n engine engine.lib 1 1
n game game.lib 2 0
n exe MyGame.exe 3 0
l engine base
l game engine
l exe game
# base を変えると、それに依存する全部が再ビルド。game だけ変えれば、game と exe だけ
</div>


| 利点 | 説明 |
| --- | --- |
| **変更した部分だけ再ビルド** | `game.lib` を直しても、`engine.lib` と `base.lib` は再ビルドされない |
| **依存の向きを強制できる** | `base` が `game` を include すると、ビルドが通らない（[レイヤー](../foundations/layers.md)） |
| **ツールとゲームで共有できる** | エディタも `engine.lib` にリンクして、同じコードを使う |
| **テストしやすい** | `base.lib` だけを、テスト用の exe にリンクして、単体テスト（[テスト容易性](../foundations/testability.md)） |

### CMake での書き方

```cmake
cmake_minimum_required(VERSION 3.25)
project(MyGame LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 基盤層
add_library(base STATIC
  src/base/log.cpp
  src/base/math.cpp)
target_include_directories(base PUBLIC src/base)

# エンジン層：base に依存
add_library(engine STATIC
  src/engine/renderer.cpp
  src/engine/audio.cpp)
target_include_directories(engine PUBLIC src/engine)
target_link_libraries(engine PUBLIC base)

# ゲーム層：engine と base に依存
add_library(game STATIC
  src/game/player.cpp
  src/game/enemy.cpp)
target_link_libraries(game PUBLIC engine)

# アプリ：全部をつなぐ
add_executable(MyGame src/app/main.cpp)
target_link_libraries(MyGame PRIVATE game)
```

| 命令 | 意味 |
| --- | --- |
| `add_library(名前 STATIC ソース…)` | 静的ライブラリを作る |
| `target_include_directories(名前 PUBLIC パス)` | その名前を使う側にも、パスを伝える（`PUBLIC`）。内部だけなら `PRIVATE` |
| `target_link_libraries(A PUBLIC B)` | A は B に依存し、A を使う側も B を使う |
| `PUBLIC` / `PRIVATE` / `INTERFACE` | 依存を、**使う側に伝える**か、**内部だけ**にするか |

`engine` が `base` に `PUBLIC` でリンクしているので、`game` は `engine` にリンクするだけで、`base` も使えます。**依存の向き**（下から上へ）が、`CMakeLists.txt` にそのまま書かれます。

## 3. ファイルとフォルダーの構成

```text
MyGame/
├── CMakeLists.txt          … ビルドの定義（または .sln / .vcxproj）
├── vcpkg.json              … 外部ライブラリの一覧（バージョン固定）
├── .gitignore              … ビルド結果を、Git に入れない
├── .clang-format           … 整形のルール
├── src/
│   ├── base/               … 基盤層
│   ├── engine/             … エンジン層
│   ├── game/               … ゲーム層
│   └── app/main.cpp        … アプリ層
├── assets/                 … 画像・音・データ
├── third_party/            … 外部ライブラリ（vcpkg を使わないもの）
├── tests/                  … 単体テスト
└── tools/                  … ビルド補助スクリプト
```

| ルール | 理由 |
| --- | --- |
| **フォルダー = モジュール**（ライブラリ） | 依存関係が、フォルダーで見える |
| **公開するヘッダと、内部のヘッダを分ける**（`include/` と `src/`） | 使う側に見せるものを、最小にする |
| **ビルド結果は、ソースと別の場所**（`build/`、`out/`） | `.gitignore` が簡単。きれいに作り直せる |
| **ビルド設定は、ファイルで管理** | 画面で設定した内容は、Git に入らず、他の人に伝わらない |

## 4. 外部ライブラリの管理

| 方法 | 説明 |
| --- | --- |
| <strong>vcpkg（マニフェスト）</strong> | `vcpkg.json` に書く。バージョンも固定できる（[外部ライブラリの入れ方](../../vs/libraries.md)） |
| **CMake の `FetchContent`** | ダウンロードして、一緒にビルド。タグで固定 |
| **Git サブモジュール** | 外部ライブラリを、特定のコミットで、リポジトリに取り込む |
| **`third_party/` にコピー** | 小さなヘッダ ライブラリ。簡単だが、更新が手作業 |

**バージョンを固定**します（`master` ではなく、タグやコミットを指定）。固定しないと、ある日、ライブラリが更新されて、ビルドが壊れます。

## 5. ビルドの構成（Debug / Release / Development）

| 構成 | 最適化 | デバッグ情報 | `assert` | 用途 |
| --- | --- | --- | --- | --- |
| **Debug** | なし（`/Od`） | あり | 有効 | バグ探し（遅い） |
| **Development**（自作） | あり（`/O2`） | あり | 有効 | 普段の開発・テスト プレイ（速く、デバッグ機能あり） |
| **Release** | あり（`/O2`） | 少し | 無効 | 製品版 |

CMake では、`CMAKE_CONFIGURATION_TYPES` や、`target_compile_definitions` で、構成ごとの定義（`ENABLE_DEBUG_UI` など）を切り替えます。

```cmake
target_compile_definitions(game PRIVATE
  $<$<CONFIG:Debug>:ENABLE_DEBUG_UI>      # Debug のときだけ定義
  $<$<CONFIG:Release>:NDEBUG>)            # Release のとき
```

## 6. 自動化（CI）

**CI**（継続的インテグレーション）は、**Git に push するたびに、自動でビルドとテストを実行する**仕組みです。GitHub Actions なら、リポジトリに設定ファイルを置くだけです。

| 効果 | 説明 |
| --- | --- |
| <strong>「自分の PC でだけ動く」を防ぐ</strong> | きれいな環境で、毎回ビルドする |
| **壊れたら、すぐ分かる** | push 直後に、通知される |
| **テストが、自動で回る** | [テスト](../foundations/testability.md)を、実行し忘れない |

```yaml
# .github/workflows/build.yml（Windows でビルドする例）
name: build
on: [push, pull_request]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - name: Configure
        run: cmake -S . -B build -G "Visual Studio 17 2022" -A x64
      - name: Build
        run: cmake --build build --config Release
      - name: Test
        run: ctest --test-dir build -C Release
```

## ゲームでの使いどころ

| 場面 | 設計 |
| --- | --- |
| ビルドが 5 分を超えてきた | ビルド インサイトで原因を探す → PCH、前方宣言、ライブラリ分割 |
| エディタとゲームで、コードを共有 | エンジンを静的ライブラリにして、両方からリンク |
| チームで、環境が違ってビルドが通らない | vcpkg のマニフェストと、`CMakePresets.json` を Git に入れる |
| 外部ライブラリが大きくなった | vcpkg にして、バイナリ キャッシュを使う |
| アセットのビルド（画像の圧縮など） | ビルド ステップに組み込む（`add_custom_command`） |
| 製品版の配布 | Release 構成で、`assets/` と DLL をまとめて、ZIP にする |

## よくあるミス

??? failure "全部のヘッダを、`common.h` にまとめて、全員が include する"
    `common.h` を 1 行変えると、**全部が再ビルド**されます。必要なものだけ、必要な場所で include します。

??? failure "ビルド結果（`Debug/`、`x64/`、`.vs/`）を Git に入れる"
    リポジトリが巨大になり、他の人の環境と衝突します。`.gitignore` に入れます。

??? failure "Visual Studio の画面でだけ設定して、ファイルに残さない"
    `.vcxproj` に保存されますが、パスが**自分の PC の絶対パス**だと、他の人のビルドが壊れます。`$(SolutionDir)` などのマクロを使います（[外部ライブラリの入れ方](../../vs/libraries.md)）。

??? failure "外部ライブラリを `master` で取り込む"
    ある日、ライブラリの更新で、ビルドが壊れます。**バージョンを固定**します。

??? failure "循環したライブラリ依存"
    `engine` が `game` を使い、`game` が `engine` を使うと、リンクが通りません。依存の向きを、一方向にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ビルドが遅い原因の大半は `#include`。前方宣言・PImpl・PCH で減らす
    - [x] コードを層ごとの**静的ライブラリ**に分けると、速く、依存も守れる
    - [x] ビルド設定は**ファイルに書いて Git に入れる**（CMake / vcxproj / vcpkg.json）
    - [x] 外部ライブラリは**バージョンを固定**。「クローンして 1 コマンドでビルド」を保つ
    - [x] 構成は Debug / Development / Release。CI で自動ビルド

## 関連ページ

- [ヘッダとソースの分け方](../foundations/header-source.md)
- [モジュール境界とレイヤー設計](../foundations/layers.md)
- [PImpl](../patterns/pimpl.md)
- [Visual Studio：CMake で使う](../../vs/cmake.md)
- [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md)
