---
title: ufbx の導入（Visual Studio）
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# ufbx の導入（Visual Studio）

ufbx は、**`ufbx.c` と `ufbx.h` の 2 ファイルだけ**です。**ファイルを置いて、プロジェクトに追加**するのが、**最も簡単**です（導入の基本は [外部ライブラリの入れ方](../../vs/libraries.md)）。

=== "ファイルを置く"

    1. [GitHub の ufbx](https://github.com/ufbx/ufbx) から、**`ufbx.c`** と **`ufbx.h`** を取得し、`third_party/ufbx/` に置く
    2. **ソリューション エクスプローラーで、`ufbx.c` を、プロジェクトに追加**（追加 → 既存の項目）
    3. プロジェクトのプロパティを開き、構成を **すべての構成**、プラットフォームを **x64** にする
    4. **C/C++ → 全般 → 追加のインクルード ディレクトリ** に、`$(SolutionDir)third_party\ufbx` を追加する
    5. `#include "ufbx.h"` と書いてビルドする

    **`ufbx.c` は、C のファイル**です。**C++ のプロジェクトでも、そのままビルドできます**（拡張子 `.c` の、C コンパイル）。**プリコンパイル済みヘッダー**を使っている場合は、<strong>`ufbx.c` では、「プリコンパイル済みヘッダーを使用しない」</strong>にします（`/Yu` を外す）。

=== "vcpkg"

    ```powershell
    vcpkg install ufbx:x64-windows
    ```

    （`vcpkg search ufbx` で、**ポートがあるか**、確認します。マニフェスト モードなら `vcpkg.json` に `"ufbx"` を足す）

    ```cpp
    #include <ufbx.h>
    ```

=== "CMake（FetchContent）"

    ```cmake
    include(FetchContent)
    FetchContent_Declare(
      ufbx
      GIT_REPOSITORY https://github.com/ufbx/ufbx.git
      GIT_TAG master)
    FetchContent_MakeAvailable(ufbx)

    add_library(ufbx STATIC ${ufbx_SOURCE_DIR}/ufbx.c)
    target_include_directories(ufbx PUBLIC ${ufbx_SOURCE_DIR})
    target_link_libraries(my_game PRIVATE ufbx)
    ```

    **`GIT_TAG` は、リリースのタグ**に固定します（`master` は、変わる）。

## ビルドの設定

| 設定 | 説明 |
| --- | --- |
| **C++ のプロジェクトで OK** | **`.c` として、別にコンパイル**される |
| **最適化は Release で** | ufbx の読み込みは、**Debug だと遅い**（数倍） |
| **警告** | **ufbx.c は、警告が出る**場合がある。**`/W3`**（このファイルだけ）にする |
| **`UFBX_*` の定義** | **機能の、有効・無効<strong>（`UFBX_NO_...`）。</strong>通常は、不要** |

## よくあるミス

??? failure "`ufbx.c` を、プロジェクトに追加し忘れて、`LNK2019`（未解決の外部シンボル）"
    **`ufbx.h` を置くだけでは、不十分**です。**`ufbx.c` も、プロジェクトに追加**します。

??? failure "プリコンパイル済みヘッダーで、`ufbx.c` がエラーになる"
    **`ufbx.c` だけ、プリコンパイル済みヘッダーを、使わない**設定にします。

??? failure "Debug で、読み込みが、極端に遅い"
    **Release** で測ります（[コンパイラとビルド](../../basics/compiler.md)）。

## 関連ページ

- [ufbx（目次）](index.md)
- [FBX と ufbx の基本](quickstart.md)
- [外部ライブラリの入れ方](../../vs/libraries.md)
