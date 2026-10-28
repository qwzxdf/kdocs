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

**tinygltf**（ティニー ジーエルティーエフ）は、**glTF**（ジーエルティーエフ）という 3D モデルのファイルを**C++ で読み書きする**ヘッダのみのライブラリです。glTF は、<strong>「3D 界の JPEG」</strong>とも呼ばれる、**オープンな 3D モデルの形式**で、メッシュ・マテリアル・テクスチャ・ボーン・アニメーションを 1 つのファイルにまとめられます。tinygltf は、**ファイルを読んで、C++ の構造体（`tinygltf::Model`）にするところまで**を担当します。**画面に出す部分は、自分で書きます**（[メッシュとテクスチャ](../../3d/mesh-textures.md)）。このページは、導入と、最小の読み込み、全体像をまとめ、**glTF のデータの構造**は [glTF の構造](structure.md)、**データの取り出し方**は [データの取り出し方](reading.md) で説明します。

## ページ一覧

**読む順番**：導入 → glTF の基本 → 構造 → 読み込みと取り出し。

| ページ | 内容 |
| --- | --- |
| [導入（Visual Studio）](install.md) | ファイルを置く・vcpkg での入れ方、`TINYGLTF_IMPLEMENTATION` |
| [glTF の基本と規約](gltf-basics.md) | glTF とは、ファイルの形、座標系、拡張、ほかの選択肢 |
| [最小の読み込みと Model の全体像](quickstart.md) | `LoadASCIIFromFile`、`tinygltf::Model` の中身、よくあるミス |
| [glTF の構造](structure.md) | 参照は「番号（インデックス）」。buffer・accessor・node・material |
| [データの取り出し方](reading.md) | 頂点・インデックス・ノード・マテリアル・テクスチャ・アニメの取り出し |

## 関連ページ

- [glTF の構造](structure.md)
- [データの取り出し方](reading.md)
- [メッシュとテクスチャ](../../3d/mesh-textures.md)
- [3D モデルの基礎](../../3d/model-basics.md)
- [PBR（物理ベースレンダリング）](../../3d/pbr.md)
- [スキニングとアニメーション](../../3d/skinning-animation.md)
- [外部ライブラリの入れ方](../../vs/libraries.md)
