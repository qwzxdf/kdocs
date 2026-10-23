---
title: fastgltf の導入（Visual Studio）
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# fastgltf の導入（Visual Studio）

fastgltf は**ヘッダ ＋ ビルドが必要なライブラリ**（`.cpp` を含む）です。simdjsonにも依存します。Visual Studio で入れるなら vcpkg が簡単です（導入の基本は [外部ライブラリの入れ方](../../vs/libraries.md)）。

=== "vcpkg"

    1. 初回だけ Developer PowerShell で `vcpkg integrate install` を実行する（[準備](../../vs/libraries.md#vcpkg)）
    2. ライブラリを入れる

        ```powershell
        vcpkg install fastgltf:x64-windows
        ```

        （マニフェスト モードなら `vcpkg.json` の `dependencies` に `"fastgltf"` を足す）
    3. `#include <fastgltf/core.hpp>` と書けば使える（simdjson も自動で入る）

=== "CMake（FetchContent）"

    ```cmake
    include(FetchContent)
    FetchContent_Declare(
      fastgltf
      GIT_REPOSITORY https://github.com/spnda/fastgltf.git
      GIT_TAG v0.8.0)
    FetchContent_MakeAvailable(fastgltf)
    target_link_libraries(my_game PRIVATE fastgltf::fastgltf)
    ```

    タグは最新を確認して指定します。simdjson は fastgltf が、取得してくれます。

=== "ソースを入れる"

    1. [GitHub の fastgltf](https://github.com/spnda/fastgltf) を取得し、`third_party/fastgltf/` に置く
    2. `src/` の `.cpp`（`fastgltf.cpp`・`base64_decode.cpp` など）とsimdjson（`simdjson.cpp`）を、プロジェクトに追加
    3. 追加のインクルード ディレクトリに `include` を追加

    依存が多いので、vcpkg か CMake が、おすすめです（手間が減ります）。

## C++ の設定

| 設定 | 説明 |
| --- | --- |
| **C++17 以上** | このサイトの設定の C++23 で問題なし |
| `NOMINMAX` | Windows では定義する（[プリプロセッサマクロ](../../vs/preprocessor.md)） |
| ランタイム | vcpkg は `/MD`。自分のプロジェクトとそろえる（[ランタイム ライブラリ](../../vs/errors.md#runtime_library)） |

## 画像のデコード

**fastgltf は画像（PNG・JPG）をデコードしません**。ファイルの場所・バイト列を返すだけです。`stb_image`（[ImGui のテクスチャ](../imgui/textures.md)で紹介）などで、自分で展開します。

## よくあるミス

??? failure "`fastgltf/core.hpp` が見つからない（古い版のヘッダ名で書いている）"
    **バージョンでヘッダの構成が変わります**（`fastgltf/parser.hpp` → `fastgltf/core.hpp`）。使っている版のサンプルを確認します。

??? failure "simdjson のリンクエラー"
    simdjson が、リンクされていません。vcpkg や CMake なら自動です。

## 動作確認のチェックリスト

fastgltf はバージョンで、API が変わるので動作確認のコードは、[クイックスタート](quickstart.md) のバージョンに合わせたものを使います。導入の段階では次の 5 つを確かめます。

| 確認 | 見るところ |
| --- | --- |
| ① C++ 標準 | プロジェクトの C++ 言語標準が、`/std:c++17` 以上 |
| ② ヘッダーが見える | `#include <fastgltf/core.hpp>` が、通る |
| ③ ライブラリがリンクされる | `fastgltf.lib`（と simdjson）が、リンクに含まれる。vcpkg か CMake なら自動 |
| ④ ランタイムがそろう | fastgltf のビルドと自分のプロジェクトで、`/MD` か `/MT` が同じ |
| ⑤ 1 つのファイルを読める | `.glb` を 1 つ読んで、メッシュの数を表示（クイックスタート） |

## よくあるエラー（導入編）

| エラー | 原因 | 直し方 |
| --- | --- | --- |
| `LNK2019`（`fastgltf::…` が未解決） | ライブラリをリンクしていない | CMake なら `target_link_libraries(… fastgltf::fastgltf)`、手動なら `fastgltf.lib` と `simdjson.lib` |
| `C1083`（`fastgltf/core.hpp` を開けない） | インクルード ディレクトリの設定が違う | `include` フォルダーのパスを、追加 |
| C++ の構文エラーが大量に出る | C++ の標準が、古い | `/std:c++17` 以上に |
| `LNK2038`（ランタイムの不一致） | `/MD` と `/MT` の取り違え | そろえる（[ランタイム ライブラリ](../../vs/errors.md#runtime_library)） |
| 古い記事のコードが動かない | fastgltf の API が、バージョンで変わった | 導入したバージョンのドキュメントとサンプルを見る |

## バージョンを固定する

fastgltf は更新が活発で、<strong>API が予告なく変わる</strong>ことがあります。タグ（またはコミット）を固定します。

| 方法 | 内容 |
| --- | --- |
| vcpkg（マニフェスト） | `vcpkg.json` の `builtin-baseline` で固定 |
| FetchContent | `GIT_TAG` にタグを書く |
| ソースを入れる | リポジトリにコミットする |

## 関連ページ

- [fastgltf（目次）](index.md)
- [特徴と最小の読み込み](quickstart.md)
- [外部ライブラリの入れ方](../../vs/libraries.md)
