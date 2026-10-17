---
title: tinygltf（glTF の読み込み）
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# tinygltf（glTF の読み込み）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
</div>

**tinygltf**（ティニー ジーエルティーエフ）は、**glTF**（ジーエルティーエフ）という 3D モデルのファイルを、**C++ で読み書きする**ヘッダのみのライブラリです。glTF は、<strong>「3D 界の JPEG」</strong>とも呼ばれる、**オープンな 3D モデルの形式**で、メッシュ・マテリアル・テクスチャ・骨・アニメーションを、1 つのファイルにまとめられます。tinygltf は、**ファイルを読んで、C++ の構造体（`tinygltf::Model`）にするところまで**を担当します。**画面に出す部分は、自分で書きます**（[メッシュとテクスチャ](../../3d/mesh-textures.md)）。このページは、導入と、最小の読み込み、全体像をまとめ、**glTF のデータの構造**は [glTF の構造](structure.md)、**データの取り出し方**は [データの取り出し方](reading.md) で説明します。

!!! tip "ポイント"
    - glTF は、<strong>JSON（構造）+ バイナリ（頂点などの数値）+ 画像</strong>の組み合わせ。<strong>1 つにまとめた `.glb`</strong> もある。
    - tinygltf は、<strong>ファイルを `tinygltf::Model` に読み込む</strong>だけ。<strong>描画用のバッファは、自分で作る</strong>。
    - <strong>`tinygltf::Model` の中の「参照」は、すべて、配列の番号（インデックス）</strong>。ポインタではない。→ [glTF の構造](structure.md)
    - 導入は、<strong>`tiny_gltf.h` と、`json.hpp`、`stb_image.h` などを置く</strong>か、<strong>vcpkg</strong>。<strong>`TINYGLTF_IMPLEMENTATION` を、1 つの `.cpp` だけ</strong>に書く。
    - glTF の座標系は、<strong>右手系・Y が上・前は −Z</strong>。<strong>SimpleMath と同じ</strong>なので、そのまま使える。
    - 圧縮拡張（Draco など）は、自分ではデコードしない。

## glTF とは

| 項目 | 内容 |
| --- | --- |
| **正式名称** | GL Transmission Format |
| **作った所** | Khronos Group（OpenGL / Vulkan の団体）。**オープン**な規格 |
| **バージョン** | **2.0** が、現在の標準 |
| **特徴** | **軽量**。**PBR のマテリアル**（金属度・粗さ）に対応。骨・アニメーションも持てる |
| **向き** | **ゲーム・Web・アプリ**への、**配布・受け渡し** |
| **拡張子** | `.gltf`（JSON + 外部ファイル）、`.glb`（1 ファイルにまとめたバイナリ） |

### ファイルの形

| 形式 | 構成 | 特徴 |
| --- | --- | --- |
| **`.gltf`** | JSON ＋ `.bin`（バイナリ）＋ 画像（`.png` など） | ファイルが分かれる。**中身を、テキストエディターで見られる** |
| **`.glb`** | **すべてを 1 つにまとめたバイナリ** | 1 ファイルで、扱いやすい。**配布向き** |
| **埋め込み `.gltf`** | JSON の中に、データを `base64` で入れたもの | 1 ファイルだが、サイズが大きくなる |

## 導入（Visual Studio）

Visual Studio での入れ方の基本は [外部ライブラリの入れ方](../../vs/libraries.md) にまとめています。

=== "ファイルを置く"

    1. [GitHub の tinygltf](https://github.com/syoyo/tinygltf) から、**`tiny_gltf.h`**、**`json.hpp`**（nlohmann/json）、**`stb_image.h`**、**`stb_image_write.h`** を取得し、`third_party/tinygltf/` に置く
    2. プロジェクトのプロパティを開き、構成を **すべての構成**、プラットフォームを **x64** にする
    3. **C/C++ → 全般 → 追加のインクルード ディレクトリ** に、`$(SolutionDir)third_party\tinygltf` を追加する
    4. **1 つの `.cpp` だけ**（たとえば `gltf_loader.cpp`）で、次のように書く

        ```cpp
        #define TINYGLTF_IMPLEMENTATION
        #define STB_IMAGE_IMPLEMENTATION
        #define STB_IMAGE_WRITE_IMPLEMENTATION
        #include "tiny_gltf.h"
        ```

    5. ほかのファイルでは、`#include "tiny_gltf.h"` だけを書く（`#define` は書かない）

=== "vcpkg"

    1. 初回だけ、Developer PowerShell で `vcpkg integrate install` を実行する（[準備](../../vs/libraries.md#vcpkg)）
    2. ライブラリを入れる

        ```powershell
        vcpkg install tinygltf:x64-windows
        ```

        （マニフェスト モードなら、`vcpkg.json` の `dependencies` に `"tinygltf"` を足す）
    3. **1 つの `.cpp` だけ**で、`TINYGLTF_IMPLEMENTATION` を書いてから `#include <tiny_gltf.h>` する（上と同じ）

!!! warning "TINYGLTF_IMPLEMENTATION は、1 つの .cpp だけ"
    `#define TINYGLTF_IMPLEMENTATION` を、**複数の `.cpp`** に書くと、**関数の二重定義**（`LNK2005`）になります。**1 つの専用の `.cpp`** に閉じ込めます（[ビルド時間の最適化](../../optimize/build-time.md)）。

!!! warning "Windows では、NOMINMAX を定義する"
    `<windows.h>` の `min` / `max` マクロと衝突します。プロジェクトで **`NOMINMAX`** を定義します（[プリプロセッサマクロ](../../vs/preprocessor.md)）。

## 最小の読み込み

```cpp
#include <print>
#include <string>

#include "tiny_gltf.h"

bool LoadModel(const std::string& path, tinygltf::Model& model) {
  tinygltf::TinyGLTF loader;
  std::string error;
  std::string warning;

  bool ok = path.ends_with(".glb")
                ? loader.LoadBinaryFromFile(&model, &error, &warning, path)
                : loader.LoadASCIIFromFile(&model, &error, &warning, path);

  if (!warning.empty()) std::println("警告: {}", warning);
  if (!error.empty()) std::println("エラー: {}", error);
  return ok;
}
```

| 関数 | 用途 |
| --- | --- |
| **`LoadASCIIFromFile`** | **`.gltf`**（JSON）を読む。`.bin` や画像も、**同じフォルダー**から読む |
| **`LoadBinaryFromFile`** | **`.glb`** を読む |
| `LoadASCIIFromString` / `LoadBinaryFromMemory` | メモリ上のデータから読む（アーカイブ・ネットワーク経由） |
| `WriteGltfSceneToFile` | `Model` を、ファイルに書く（ツールで出力するとき） |

| 引数 | 意味 |
| --- | --- |
| `&model` | 読み込み結果を受け取る |
| `&error` | 失敗したときの**エラーメッセージ** |
| `&warning` | 続行できる**警告**（拡張の未対応など） |
| `path` | ファイルのパス（アセットのパスは、**ASCII にする**のが無難。[文字コード](../../encoding/index.md)） |

**`bool` が `true` でも、`warning` は確認します**。**未対応の拡張**などは、警告で出ます。

## tinygltf::Model の全体像

`tinygltf::Model` は、**glTF のファイルの内容を、そのまま構造体にした**ものです。**中身は、配列（`std::vector`）の集まり**です。

<div class="anim" data-type="graph" data-label="tinygltf::Model は、種類ごとの配列を持つ。要素同士は「番号」でつながる">
n model tinygltf::Model 0 1 hit
---
n model tinygltf::Model 0 1
n nodes nodes 1 0 new
n meshes meshes 2 0 new
n acc accessors 3 0 new
n bv bufferViews 4 0 new
l model nodes hit
l model meshes hit
l model acc hit
l model bv hit
---
n model tinygltf::Model 0 1 dim
n nodes nodes 1 0
n meshes meshes 2 0
n acc accessors 3 0
n bv bufferViews 4 0
n buf buffers 4 1 new
n mat materials 2 1 new
n tex textures 3 1 new
n img images 3 2 new
n smp samplers 4 2 new
l model buf hit
l model mat hit
l model tex hit
l model img hit
l model smp hit
</div>

| 配列 | 中身 |
| --- | --- |
| **`scenes`** | シーン（どのノードを表示するか） |
| **`nodes`** | **ノード**（位置・回転・拡大、親子関係）。**メッシュや骨と結びつく** |
| **`meshes`** | **メッシュ**（三角形の集まり）。中に **`primitives`** がある |
| **`accessors`** | **データの読み方**（「ここから、float 3 つずつ、何個」） |
| **`bufferViews`** | **バッファの、どの範囲か** |
| **`buffers`** | **バイナリデータ本体**（`std::vector<unsigned char>`） |
| **`materials`** | **マテリアル**（色・金属度・粗さ・どのテクスチャを使うか） |
| **`textures`** | テクスチャ（**画像 + サンプラー**の組み合わせ） |
| **`images`** | **画像データ**（読み込み済みのピクセル） |
| **`samplers`** | サンプラー（フィルター・ラップの設定） |
| **`skins`** | スキン（骨のノード番号のリスト） |
| **`animations`** | アニメーション（どのノードを、どう動かすか） |
| `cameras` | カメラ（透視・正射） |

**これらの要素は、ポインタではなく、「配列の番号（インデックス）」でつながっています**。この仕組みが、glTF を扱う上での、**一番大事なところ**です。詳しくは、[glTF の構造](structure.md)で説明します。

## glTF の座標系・規約

| 項目 | glTF | このサイトの規約（SimpleMath / DX11） |
| --- | --- | --- |
| **座標系** | **右手系** | 右手系（同じ） |
| **上方向** | **+Y** | +Y（同じ） |
| **前方向** | <strong>+Z が「正面向き」</strong>（モデルが、+Z を向いて作られる） | カメラの前は −Z（[座標系](../../3d/coordinate-systems.md)） |
| **単位** | **メートル** | メートル（同じ） |
| **UV の原点** | **左上**（V は下向き） | **左上**（DirectX と同じ。**反転は不要**） |
| **三角形の表** | <strong>反時計回り（CCW）</strong> | CCW（`FrontCounterClockwise = TRUE`） |
| <strong>回転（クォータニオン）</strong> | **`(x, y, z, w)`** の順 | SimpleMath の `Quaternion(x, y, z, w)`（同じ） |
| **行列** | **列優先**（column-major）の 16 個 | 行ベクトル規約（行優先）。**転置と同じ並びなので、そのまま `memcpy` できる**（[データの取り出し方](reading.md)） |

**SimpleMath と、並びが同じ**なので、座標の変換は、ほぼ不要です。**モデルを、カメラの向きに合わせたいときは、`Matrix::CreateRotationY(XM_PI)` で反転**します。

## 拡張（extensions）

glTF は、**拡張**で機能を足せます。**未対応の拡張**は、`warning` に出ます。

| 拡張 | 内容 | tinygltf の対応 |
| --- | --- | --- |
| `KHR_materials_*` | クリアコート・透過・光沢などの、**マテリアルの追加機能** | **値は読める**（`extensions` に入る。解釈は自分で） |
| `KHR_texture_transform` | UV の移動・回転・拡大 | 値は読める。自分で適用 |
| `KHR_lights_punctual` | ライト | 読める |
| `KHR_draco_mesh_compression` | **Draco による、メッシュ圧縮** | **デコードしない**（別のライブラリが必要） |
| `EXT_meshopt_compression` | meshopt による圧縮 | デコードしない |
| `KHR_texture_basisu` | KTX2（Basis）のテクスチャ圧縮 | **画像として読めない**（別のライブラリが必要） |

**圧縮された glTF** は、tinygltf だけでは、頂点が取り出せません。**書き出しのときに、圧縮を使わない**設定にするのが、いちばん簡単です。

## ほかの選択肢

| ライブラリ | 特徴 |
| --- | --- |
| **tinygltf** | **ヘッダのみ・使いやすい**。構造がそのまま見える。**学習・小規模向き** |
| **fastgltf** | **速い**（simdjson 使用）。**C++17 以降**。**大きなデータ向き** |
| **cgltf** | **C 言語**の、単一ヘッダ。**軽い**。構造がポインタで辿れる |
| **Assimp** | **多くの形式**に対応（glTF・FBX・OBJ…）。**重い** |

**学習・普通のゲームなら、tinygltf**が、理解しやすいです。

## よくあるミス

??? failure "`LNK2005`（多重定義）になる"
    `TINYGLTF_IMPLEMENTATION` を、複数の `.cpp` に書いています。**1 つだけ**にします。

??? failure "`min` / `max` でコンパイルエラーになる"
    `NOMINMAX` を定義します。

??? failure "`LoadASCIIFromFile` が `false` を返し、画像が読めない"
    `.gltf` と、同じフォルダーにある `.bin` や画像の**相対パス**が、正しくない可能性があります。**ファイルを動かさずに、まとめて**置きます。

??? failure "`.glb` を `LoadASCIIFromFile` で読んでいる"
    `.glb` は **`LoadBinaryFromFile`** です。

??? failure "`warning` を見ず、拡張が使われていることに、気づかない"
    `warning` を、**ログに出して**確認します。

??? failure "モデルが、後ろ向き・裏返しで表示される"
    **巻き順**（`FrontCounterClockwise`）と、**前方向**（+Z が正面）を確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] glTF は、<strong>JSON ＋ バイナリ ＋ 画像</strong>。<strong>`.glb` は 1 ファイルにまとめたもの</strong>
    - [x] tinygltf は<strong>`tinygltf::Model` に読み込む</strong>だけ。<strong>描画用のバッファは自分で作る</strong>
    - [x] <strong>`TINYGLTF_IMPLEMENTATION` は、1 つの `.cpp` だけ</strong>。Windows は <strong>`NOMINMAX`</strong>
    - [x] <strong>要素同士の参照は、すべて「配列の番号（インデックス）」</strong>
    - [x] 座標系は<strong>右手系・Y 上</strong>で、<strong>SimpleMath と同じ</strong>。<strong>UV は左上原点で、反転不要</strong>
    - [x] <strong>圧縮拡張（Draco など）は、tinygltf だけでは、デコードできない</strong>

## 関連ページ

- [glTF の構造](structure.md)
- [データの取り出し方](reading.md)
- [メッシュとテクスチャ](../../3d/mesh-textures.md)
- [3D モデルの基礎](../../3d/model-basics.md)
- [PBR（物理ベースレンダリング）](../../3d/pbr.md)
- [スキニングとアニメーション](../../3d/skinning-animation.md)
- [外部ライブラリの入れ方](../../vs/libraries.md)
