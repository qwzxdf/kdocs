---
title: fastgltf の導入（Visual Studio）
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# fastgltf の導入（Visual Studio）

fastgltf は、**ヘッダ ＋ ビルドが必要なライブラリ**（`.cpp` を含む）です。**simdjson**にも依存します。**Visual Studio で入れるなら、vcpkg が簡単**です（導入の基本は [外部ライブラリの入れ方](../../vs/libraries.md)）。

=== "vcpkg"

    1. 初回だけ、Developer PowerShell で `vcpkg integrate install` を実行する（[準備](../../vs/libraries.md#vcpkg)）
    2. ライブラリを入れる

        ```powershell
        vcpkg install fastgltf:x64-windows
        ```

        （マニフェスト モードなら、`vcpkg.json` の `dependencies` に `"fastgltf"` を足す）
    3. `#include <fastgltf/core.hpp>` と書けば使える（simdjson も、自動で入る）

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

    **タグは、最新を確認**して指定します。**simdjson は、fastgltf が、取得してくれます**。

=== "ソースを入れる"

    1. [GitHub の fastgltf](https://github.com/spnda/fastgltf) を取得し、`third_party/fastgltf/` に置く
    2. **`src/` の `.cpp`**（`fastgltf.cpp`・`base64_decode.cpp` など）と、**simdjson**（`simdjson.cpp`）を、プロジェクトに追加
    3. 追加のインクルード ディレクトリに、`include` を追加

    **依存が多い**ので、**vcpkg か CMake が、おすすめ**です（手間が減ります）。

## C++ の設定

| 設定 | 説明 |
| --- | --- |
| **C++17 以上** | **このサイトの設定の C++23 で問題なし** |
| **`NOMINMAX`** | Windows では定義する（[プリプロセッサマクロ](../../vs/preprocessor.md)） |
| **ランタイム** | **vcpkg は `/MD`**。自分のプロジェクトと、そろえる（[ランタイム ライブラリ](../../vs/errors.md#runtime_library)） |

## 画像のデコード

**fastgltf は、画像（PNG・JPG）を、デコードしません**。**ファイルの場所・バイト列を、返す**だけです。**`stb_image`**（[ImGui のテクスチャ](../imgui/textures.md)で紹介）などで、**自分で展開**します。

## よくあるミス

??? failure "`fastgltf/core.hpp` が見つからない（古い版のヘッダ名で書いている）"
    **バージョンで、ヘッダの構成が変わります**（`fastgltf/parser.hpp` → `fastgltf/core.hpp`）。**使っている版のサンプル**を確認します。

??? failure "simdjson のリンクエラー"
    **simdjson が、リンクされていません**。**vcpkg や CMake なら、自動**です。

## 関連ページ

- [fastgltf（目次）](index.md)
- [特徴と最小の読み込み](quickstart.md)
- [外部ライブラリの入れ方](../../vs/libraries.md)
