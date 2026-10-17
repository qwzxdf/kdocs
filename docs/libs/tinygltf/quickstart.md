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

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `&model` | `tinygltf::Model*` | 読み込み結果を受け取る |
| `&error` | `std::string*` | 失敗したときの**エラーメッセージ** |
| `&warning` | `std::string*` | 続行できる**警告**（拡張の未対応など） |
| `path` | `const std::string&` | ファイルのパス（アセットのパスは、**ASCII にする**のが無難。[文字コード](../../encoding/index.md)） |

**`bool` が `true` でも、`warning` は確認します**。**未対応の拡張**などは、警告で出ます。


## tinygltf::Model の全体像

`tinygltf::Model` は、**glTF のファイルの内容を、そのまま構造体にした**ものです。**中身は、配列（`std::vector`）の集まり**です。

<svg class="fig flow" viewBox="0 0 831 340" role="img" aria-label="tinygltf::Model は、種類ごとの配列を持つ。要素同士は「番号」でつながる"><defs><marker id="fl95997" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">tinygltf::Model は、種類ごとの配列を持つ。要素同士は「番号」でつながる</text><line x1="146.4" y1="185.0" x2="231.0" y2="143.9" stroke="currentColor" stroke-width="2" marker-end="url(#fl95997)"/><line x1="173.0" y1="188.7" x2="380.5" y2="134.7" stroke="currentColor" stroke-width="2" marker-end="url(#fl95997)"/><path d="M99.0,186.0 Q339.8,50.0 580.5,102.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl95997)"/><path d="M99.0,186.0 Q423.2,50.0 747.5,102.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl95997)"/><path d="M99.0,186.0 Q423.2,134.0 747.5,186.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl95997)"/><line x1="173.0" y1="208.0" x2="371.0" y2="208.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl95997)"/><path d="M99.0,186.0 Q339.8,134.0 580.5,186.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl95997)"/><line x1="173.0" y1="220.9" x2="539.5" y2="284.8" stroke="currentColor" stroke-width="2" marker-end="url(#fl95997)"/><path d="M99.0,186.0 Q423.2,134.0 747.5,270.0" fill="none" stroke="currentColor" stroke-width="2" marker-end="url(#fl95997)"/><rect x="28.0" y="188.0" width="142" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2" opacity="0.55"/><text x="99.0" y="208.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">tinygltf::Model</text><circle cx="30.0" cy="190.0" r="10" fill="#4c8bf5"/><text x="30.0" y="190.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="234.0" y="104.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="272.0" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">nodes</text><circle cx="236.0" cy="106.0" r="10" fill="#2ea043"/><text x="236.0" y="106.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="383.5" y="104.0" width="76" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="421.5" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">meshes</text><circle cx="385.5" cy="106.0" r="10" fill="#2ea043"/><text x="385.5" y="106.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="533.0" y="104.0" width="95" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="580.5" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">accessors</text><circle cx="535.0" cy="106.0" r="10" fill="#2ea043"/><text x="535.0" y="106.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="692.0" y="104.0" width="111" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="747.5" y="124.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">bufferViews</text><circle cx="694.0" cy="106.0" r="10" fill="#2ea043"/><text x="694.0" y="106.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="707.5" y="188.0" width="80" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="747.5" y="208.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">buffers</text><circle cx="709.5" cy="190.0" r="10" fill="#e5a828"/><text x="709.5" y="190.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="374.0" y="188.0" width="95" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="421.5" y="208.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">materials</text><circle cx="376.0" cy="190.0" r="10" fill="#e5a828"/><text x="376.0" y="190.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="536.5" y="188.0" width="88" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="580.5" y="208.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">textures</text><circle cx="538.5" cy="190.0" r="10" fill="#e5a828"/><text x="538.5" y="190.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="542.5" y="272.0" width="76" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="580.5" y="292.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">images</text><circle cx="544.5" cy="274.0" r="10" fill="#e5a828"/><text x="544.5" y="274.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="703.5" y="272.0" width="88" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="747.5" y="292.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">samplers</text><circle cx="705.5" cy="274.0" r="10" fill="#e5a828"/><text x="705.5" y="274.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

| 配列 | 中身 |
| --- | --- |
| **`scenes`** | シーン（どのノードを表示するか） |
| **`nodes`** | **ノード**（位置・回転・拡大、親子関係）。**メッシュやボーンと結びつく** |
| **`meshes`** | **メッシュ**（三角形の集まり）。中に **`primitives`** がある |
| **`accessors`** | **データの読み方**（「ここから、float 3 つずつ、何個」） |
| **`bufferViews`** | **バッファの、どの範囲か** |
| **`buffers`** | **バイナリデータ本体**（`std::vector<unsigned char>`） |
| **`materials`** | **マテリアル**（色・金属度・粗さ・どのテクスチャを使うか） |
| **`textures`** | テクスチャ（**画像 + サンプラー**の組み合わせ） |
| **`images`** | **画像データ**（読み込み済みのピクセル） |
| **`samplers`** | サンプラー（フィルター・ラップの設定） |
| **`skins`** | スキン（ボーンのノード番号のリスト） |
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
    **左手系への変換**（Z の反転・巻き順の入れ替え。[glTF の基本と規約](gltf-basics.md#to-left-handed)）と、**前方向**（glTF は +Z が正面）を確認します。


## これだけ覚える

!!! abstract "まとめ"
    - [x] glTF は、<strong>JSON ＋ バイナリ ＋ 画像</strong>。<strong>`.glb` は 1 ファイルにまとめたもの</strong>
    - [x] tinygltf は<strong>`tinygltf::Model` に読み込む</strong>だけ。<strong>描画用のバッファは自分で作る</strong>
    - [x] <strong>`TINYGLTF_IMPLEMENTATION` は、1 つの `.cpp` だけ</strong>。Windows は <strong>`NOMINMAX`</strong>
    - [x] <strong>要素同士の参照は、すべて「配列の番号（インデックス）」</strong>
    - [x] 座標系は<strong>右手系・Y 上</strong>。<strong>左手系へは Z を反転し、巻き順を入れ替える</strong>。<strong>UV は左上原点で、反転不要</strong>
    - [x] <strong>圧縮拡張（Draco など）は、tinygltf だけでは、デコードできない</strong>

## 関連ページ

- [tinygltf（目次）](index.md)
- [glTF の構造](structure.md)
- [データの取り出し方](reading.md)

