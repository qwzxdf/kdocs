---
title: tinygltf の導入（Visual Studio）
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# tinygltf の導入（Visual Studio）

Visual Studio での tinygltf の入れ方です。

Visual Studio での入れ方の基本は [外部ライブラリの入れ方](../../vs/libraries.md) にまとめています。

=== "ファイルを置く"

    1. [GitHub の tinygltf](https://github.com/syoyo/tinygltf) から、**`tiny_gltf.h`**、**`json.hpp`**（nlohmann/json）、**`stb_image.h`**、**`stb_image_write.h`** を取得し `third_party/tinygltf/` に置く
    2. プロジェクトのプロパティを開き構成を **すべての構成**、プラットフォームを **x64** にする
    3. **C/C++ → 全般 → 追加のインクルード ディレクトリ** に、`$(SolutionDir)third_party\tinygltf` を追加する
    4. **1 つの `.cpp` だけ**（たとえば `gltf_loader.cpp`）で、次のように書く

        ```cpp
        #define TINYGLTF_IMPLEMENTATION
        #define STB_IMAGE_IMPLEMENTATION
        #define STB_IMAGE_WRITE_IMPLEMENTATION
        #include "tiny_gltf.h"
        ```

    5. ほかのファイルでは `#include "tiny_gltf.h"` だけを書く（`#define` は書かない）

=== "vcpkg"

    1. 初回だけ Developer PowerShell で `vcpkg integrate install` を実行する（[準備](../../vs/libraries.md#vcpkg)）
    2. ライブラリを入れる

        ```powershell
        vcpkg install tinygltf:x64-windows
        ```

        （マニフェスト モードなら `vcpkg.json` の `dependencies` に `"tinygltf"` を足す）
    3. **1 つの `.cpp` だけ**で、`TINYGLTF_IMPLEMENTATION` を書いてから `#include <tiny_gltf.h>` する（上と同じ）

!!! warning "TINYGLTF_IMPLEMENTATION は、1 つの .cpp だけ"
    `#define TINYGLTF_IMPLEMENTATION` を**複数の `.cpp`** に書くと**関数の二重定義**（`LNK2005`）になります。**1 つの専用の `.cpp`** に閉じ込めます（[ビルド時間の最適化](../../optimize/build-time.md)）。

!!! warning "Windows では、NOMINMAX を定義する"
    `<windows.h>` の `min` / `max` マクロと衝突します。プロジェクトで **`NOMINMAX`** を定義します（[プリプロセッサマクロ](../../vs/preprocessor.md)）。

## 関連ページ

- [tinygltf（目次）](index.md)
- [glTF の構造](structure.md)
- [データの取り出し方](reading.md)

