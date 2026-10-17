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

**fastgltf**（ファスト ジーエルティーエフ）は、**glTF 2.0 を、速く読み込む** C++ ライブラリです。JSON の解析に **simdjson**（SIMD で速い）を使い、**大きなモデルでも、短い時間**で読めます。[tinygltf](../tinygltf/index.md) と**同じ glTF**（構造は「番号でつながる」）を読みますが、**型が厳密（`std::variant`・`std::optional`）で、速さ重視**の作りです。**大きなアセットを、多数ロードする**ゲームで、向いています。

!!! tip "ポイント"
    - glTF の読み込みに特化。<strong>simdjson ベースで、JSON の解析が速い</strong>。
    - <strong>参照は、`std::size_t` の番号（インデックス）</strong>。tinygltf と同じ考え方（[glTF の構造](../tinygltf/structure.md)）。
    - <strong>`Parser::loadGltf` → `Asset`</strong>。<strong>エラーは `Expected`（`.error()` で確認）</strong>。
    - <strong>データの取り出しは、`iterateAccessor` / `copyFromAccessor`</strong>（アクセサーの型変換・stride を、ライブラリが処理）。
    - <strong>API が、バージョンで変わりやすい</strong>（特に 0.8 前後）。<strong>使うバージョンのドキュメントを確認</strong>。
    - 画像のデコードは<strong>しない</strong>（<strong>`stb_image` などを自分で</strong>）。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [導入（Visual Studio）](install.md) | vcpkg・CMake での入れ方 |
| [特徴と最小の読み込み](quickstart.md) | tinygltf との違い、`Parser`・`Asset`、エラー処理 |
| [データの取り出し方](reading.md) | メッシュ・ノード・マテリアル・アニメーションを、SimpleMath で取り出す |

## 関連ページ

- [3D モデルの読み込みライブラリの選び方](../model-loading.md)
- [glTF の構造](../tinygltf/structure.md)
- [tinygltf](../tinygltf/index.md)
- [メッシュとテクスチャ](../../3d/mesh-textures.md)
