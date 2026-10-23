---
title: tinygltf の導入（Visual Studio）
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# tinygltf の導入（Visual Studio）

Visual Studio での tinygltf の入れ方です。

!!! info "このページを読む前に"
    - [tinygltf（glTF の読み込み）](index.md)（このセクション全体の地図と、読む順番）
    - [3D モデルの読み込みライブラリの選び方](../model-loading.md)（3D モデルの読み込みの選び方）


Visual Studio での入れ方の基本は [外部ライブラリの入れ方](../../vs/libraries.md) にまとめています。

=== "ファイルを置く"

    1. [GitHub の tinygltf](https://github.com/syoyo/tinygltf) から、**`tiny_gltf.h`**、`json.hpp`（nlohmann/json）、`stb_image.h`、`stb_image_write.h` を取得し `third_party/tinygltf/` に置く
    2. プロジェクトのプロパティを開き（[画面つきの手順](../../vs/include-dirs.md#additional)）構成を すべての構成、プラットフォームを x64 にする
    3. C/C++ → 全般 → 追加のインクルード ディレクトリ に、`$(SolutionDir)third_party\tinygltf` を追加する
    4. 1 つの `.cpp` だけ（たとえば `gltf_loader.cpp`）で、次のように書く

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
    3. 1 つの `.cpp` だけで、`TINYGLTF_IMPLEMENTATION` を書いてから `#include <tiny_gltf.h>` する（上と同じ）

!!! warning "TINYGLTF_IMPLEMENTATION は、1 つの .cpp だけ"
    `#define TINYGLTF_IMPLEMENTATION` を複数の `.cpp` に書くと関数の二重定義（`LNK2005`）になります。1 つの専用の `.cpp` に閉じ込めます（[ビルド時間の最適化](../../optimize/build-time.md)）。

!!! warning "Windows では、NOMINMAX を定義する"
    `<windows.h>` の `min` / `max` マクロと衝突します。プロジェクトで `NOMINMAX` を定義します（[プリプロセッサマクロ](../../vs/preprocessor.md)）。

## 動作確認：glTF を 1 つ読んでみる

導入できたかは <strong>小さなプログラム</strong>で確かめます。`.glb` ファイル（なんでもよい。[Khronos のサンプル](https://github.com/KhronosGroup/glTF-Sample-Assets)など）を 1 つ用意します。

```cpp
// gltf_loader.cpp: tinygltf の実装は、このファイルだけに入れる。
#define TINYGLTF_IMPLEMENTATION
#define STB_IMAGE_IMPLEMENTATION
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "tiny_gltf.h"

#include <print>
#include <string>

int main() {
  tinygltf::TinyGLTF loader;
  tinygltf::Model model;
  std::string err;
  std::string warn;

  // .glb（バイナリ）を読む。.gltf（テキスト）なら LoadASCIIFromFile。
  const bool ok = loader.LoadBinaryFromFile(&model, &err, &warn, "model.glb");
  if (!warn.empty()) std::println("警告: {}", warn);
  if (!err.empty()) std::println("エラー: {}", err);
  if (!ok) return 1;

  std::println("メッシュ: {} 個、マテリアル: {} 個、テクスチャ: {} 枚", model.meshes.size(), model.materials.size(),
               model.textures.size());
}
```

数が出れば導入は成功です。`LoadBinaryFromFile` は成功で `true` を返し失敗の理由は `err` に入ります。必ず `err` と `warn` を表示します（ファイルが見つからない、拡張子が違うなどがここに出ます）。

## よくあるエラー

| エラー | 原因 | 直し方 |
| --- | --- | --- |
| `LNK2005`（関数がすでに定義されている） | `TINYGLTF_IMPLEMENTATION` を複数の `.cpp` に書いた | 専用の `.cpp` 1 つだけに書く |
| `LNK2019`（未解決の外部シンボル）。`tinygltf::TinyGLTF::LoadBinaryFromFile` など | 実装をどの `.cpp` にも書いていない | `TINYGLTF_IMPLEMENTATION` を書いた `.cpp` を、プロジェクトに追加 |
| `C1083`（`json.hpp` を開けない） | `json.hpp`（nlohmann/json）が、見つからない | `third_party/tinygltf/` に置く。または、vcpkg の nlohmann-json を使う |
| `stb_image` の二重定義 | プロジェクトが、すでに `STB_IMAGE_IMPLEMENTATION` を持っている | `TINYGLTF_NO_STB_IMAGE` を定義し、自分の `stb_image` を使う（画像の読み込みを自分で行う） |
| `C2589`、`C2059`（`min` や `max` 周辺） | `<windows.h>` のマクロとの衝突 | `NOMINMAX` を定義 |
| `C4996`（非推奨の関数） | 古い C の関数 | `_CRT_SECURE_NO_WARNINGS` を定義するか警告を、個別に無効化 |

## CMake で使う

vcpkg で入れた場合の CMake の書き方です。

```cmake
find_package(tinygltf CONFIG REQUIRED)
target_link_libraries(MyGame PRIVATE tinygltf::tinygltf)
```

ヘッダーのみのライブラリですが、`TINYGLTF_IMPLEMENTATION` を書いた `.cpp` が必要な点は同じです。

## バージョンを固定する

glTF のライブラリはバージョンで、挙動や API が変わります。<strong>再現性のあるビルド</strong>のためにバージョンを固定します。

| 方法 | 内容 |
| --- | --- |
| ファイルを置く | リポジトリにヘッダーをそのままコミットする（バージョンが、固定される） |
| vcpkg（マニフェスト） | `vcpkg.json` の `builtin-baseline` に vcpkg のコミット ハッシュを書く |
| FetchContent | `GIT_TAG` にタグ（`v2.9.x`）、またはコミット ハッシュを書く |

## 関連ページ

- [tinygltf（目次）](index.md)
- [glTF の構造](structure.md)
- [データの取り出し方](reading.md)

