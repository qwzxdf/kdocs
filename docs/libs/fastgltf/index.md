---
title: fastgltf（高速な glTF 読み込み）
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# fastgltf（高速な glTF 読み込み）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-17">C++17〜</span>
</div>

**fastgltf**（ファスト ジーエルティーエフ）は、**glTF 2.0 を速く読み込む** C++ ライブラリです。JSON の解析に **simdjson**（SIMD で速い）を使い、**大きなモデルでも、短い時間**で読めます。[tinygltf](../tinygltf/index.md) と**同じ glTF**（構造は「番号でつながる」）を読みますが、**型が厳密（`std::variant`・`std::optional`）で、速さ重視<strong>の作りです。</strong>大きなアセットを多数ロードする**ゲームで、向いています。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [導入（Visual Studio）](install.md) | vcpkg・CMake での入れ方 |
| [特徴と最小の読み込み](quickstart.md) | tinygltf との違い、`Parser`・`Asset`、エラー処理 |
| [データの取り出し方](reading.md) | メッシュ・ノード・マテリアル・アニメーションを SimpleMath で取り出す |

## 関連ページ

- [3D モデルの読み込みライブラリの選び方](../model-loading.md)
- [glTF の構造](../tinygltf/structure.md)
- [tinygltf](../tinygltf/index.md)
- [メッシュとテクスチャ](../../3d/mesh-textures.md)
