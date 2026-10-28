---
title: ufbx の導入（Visual Studio）
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# ufbx の導入（Visual Studio）

ufbx は**`ufbx.c` と `ufbx.h` の 2 ファイルだけ**です。ファイルを置いてプロジェクトに追加するのが、最も簡単です（導入の基本は [外部ライブラリの入れ方](../../vs/libraries.md)）。

!!! info "このページを読む前に"
    - [ufbx（FBX の読み込み）](index.md)（このセクション全体の地図と、読む順番）
    - [3D モデルの読み込みライブラリの選び方](../model-loading.md)（3D モデルの読み込みの選び方）


=== "ファイルを置く"

    1. [GitHub の ufbx](https://github.com/ufbx/ufbx) から、`ufbx.c` と `ufbx.h` を取得し、`third_party/ufbx/` に置く
    2. ソリューション エクスプローラーで、`ufbx.c` をプロジェクトに追加（追加 → 既存の項目）
    3. プロジェクトのプロパティを開き（[画面つきの手順](../../vs/include-dirs.md#additional)）構成を すべての構成、プラットフォームを x64 にする
    4. C/C++ → 全般 → 追加のインクルード ディレクトリ に、`$(SolutionDir)third_party\ufbx` を追加する
    5. `#include "ufbx.h"` と書いてビルドする

    `ufbx.c` は C のファイルです。C++ のプロジェクトでもそのままビルドできます（拡張子 `.c` の、C コンパイル）。プリコンパイル済みヘッダーを使っている場合は、`ufbx.c` では「プリコンパイル済みヘッダーを使用しない」にします（`/Yu` を外す）。

=== "vcpkg"

    ```powershell
    vcpkg install ufbx:x64-windows
    ```

    （`vcpkg search ufbx` でポートがあるか、確認します。マニフェスト モードなら `vcpkg.json` に `"ufbx"` を足す）

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

    `GIT_TAG` はリリースのタグに固定します（`master` は、変わる）。

## ビルドの設定

| 設定 | 説明 |
| --- | --- |
| **C++ のプロジェクトで OK** | `.c` として、別にコンパイルされる |
| 最適化は Release で | ufbx の読み込みは、Debug だと遅い（数倍） |
| 警告 | ufbx.c は、警告が出る場合がある。`/W3`（このファイルだけ）にする |
| **`UFBX_*` の定義 | 機能の有効・無効（`UFBX_NO_...`）。通常は不要** |

## よくあるミス

??? failure "`ufbx.c` をプロジェクトに追加し忘れて、`LNK2019`（未解決の外部シンボル）"
    **`ufbx.h` を置くだけでは不十分**です。`ufbx.c` もプロジェクトに追加します。

??? failure "プリコンパイル済みヘッダーで、`ufbx.c` がエラーになる"
    `ufbx.c` だけプリコンパイル済みヘッダーを使わない設定にします。

??? failure "Debug で、読み込みが極端に遅い"
    Release で測ります（[コンパイラとビルド](../../basics/compiler.md)）。

## 動作確認：FBX を 1 つ読んでみる

`.fbx` ファイルを 1 つ用意して、次のプログラムで読めるかを確かめます。

```cpp
#include <print>

#include "ufbx.h"

int main() {
  ufbx_load_opts opts = {};                                        // 既定の設定（すべて 0）
  ufbx_error error;
  ufbx_scene* scene = ufbx_load_file("model.fbx", &opts, &error);
  if (!scene) {
    std::println("読み込みに失敗: {}", error.description.data);    // 理由が文字列で入る
    return 1;
  }

  std::println("メッシュ: {} 個、ノード: {} 個、マテリアル: {} 個", scene->meshes.count, scene->nodes.count,
               scene->materials.count);

  ufbx_free_scene(scene);                                           // 使い終わったら、必ず、解放する
}
```

`ufbx_load_file` は失敗すると `nullptr` を返し、理由が `error.description` に入ります。<strong>戻り値の確認が必須</strong>です。読めたシーンは `ufbx_free_scene` で解放します（`ComPtr` のような自動解放は、ないので `std::unique_ptr` にカスタム デリーターを付けると、安全です）。

```cpp
// 解放を自動にする。
struct SceneDeleter { void operator()(ufbx_scene* s) const { ufbx_free_scene(s); } };
using ScenePtr = std::unique_ptr<ufbx_scene, SceneDeleter>;
```

## よくあるエラー

| エラー | 原因 | 直し方 |
| --- | --- | --- |
| `C1010`（プリコンパイル済みヘッダーを探している間にファイルの終わり） | `ufbx.c` に、プリコンパイル済みヘッダー（`pch.h`）の設定が掛かっている | `ufbx.c` のプロパティで、<strong>プリコンパイル済みヘッダー → 使用しない</strong> |
| `LNK2019`（`ufbx_load_file` が未解決） | `ufbx.c` をプロジェクトに追加していない | ソリューション エクスプローラーで、`ufbx.c` を追加 |
| `ufbx.c` が C++ としてコンパイルされて、大量のエラー | ファイルのプロパティで、コンパイル言語が C++ になっている | C/C++ → 詳細設定 → コンパイル言語を「既定」（`.c` は C として）にする |
| `C4244` などの警告が大量 | ufbx の内部コード | `ufbx.c` だけ警告レベルを下げる（`/W3`）。自分のコードには影響しない |
| 読み込みが遅い（Debug） | ufbx は、最適化が効かないと遅い | Debug でも `ufbx.c` だけ最適化（`/O2`）を有効にする |

## ビルドの時間を抑える

`ufbx.c` は 1 ファイルで数万行あるので、<strong>変更しないファイル</strong>です。プロジェクトを整理するときは `ufbx.c` を静的ライブラリに分けるかプリコンパイルを避けて、再ビルドの対象から外します（[ビルド時間の最適化](../../optimize/build-time.md)）。

## 関連ページ

- [ufbx（目次）](index.md)
- [FBX と ufbx の基本](quickstart.md)
- [外部ライブラリの入れ方](../../vs/libraries.md)
