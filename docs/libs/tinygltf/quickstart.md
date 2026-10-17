---
title: 最小の読み込みと Model の全体像
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# 最小の読み込みと Model の全体像

**ファイルを読み込む最小のコード**と、`tinygltf::Model` の中身の見取り図、よくあるミスです。

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

- [tinygltf（目次）](index.md)
- [glTF の構造](structure.md)
- [データの取り出し方](reading.md)

