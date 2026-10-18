---
title: Trees
tags:
  - 描画
---

# Trees

**木は、近くは詳細なメッシュ、遠くは簡易なメッシュやビルボード**にして、**LOD で負荷を下げます**。このページでは、**木の描画**を説明します。

!!! tip "ポイント"
    - **近く：幹と枝のメッシュ ＋ 葉のカード**。
    - **中距離：簡易メッシュ**。
    - **遠く：ビルボード（板に木の絵）**。
    - **LOD の切り替えは、ディザでなめらかに**。

## 木
**木はポリゴンが多く（数万）、枚数も多い**ので、**LOD が重要**です。

| LOD | 内容 |
| --- | --- |
| <strong>LOD 0（近景）</strong> | <strong>幹・枝の 3D モデル ＋ 葉のカード（板に葉の絵）</strong> |
| **LOD 1〜2** | **枝を減らす・葉のカードを統合** |
| <strong>インポスター（遠景）</strong> | **木を数方向から撮った絵（板ポリ）に置き換え**。**カメラの向きに応じて、絵を切り替える／混ぜる** |
| <strong>ビルボード（最遠）</strong> | **1 枚の板** |

**インポスター**は、**事前に木を複数の視点（例：8×8 = 64 方向）から撮影**し、**アトラスに並べます**。**描画時はカメラに最も近い方向の絵を選び、板に貼ります**。**法線・深度もアトラスに持つと、ライティングも正しく**なります。

| 点 | 説明 |
| --- | --- |
| **LOD の切り替え** | <strong>ディザリング（市松のフェード）</strong>で、**ポップを隠す**（[半透明](../../translucency/alpha-test/index.md)） |
| **葉のカード** | **1 枚に複数の葉を描いた板**。**アルファ テスト** |
| **幹と葉でマテリアルを分ける** | **幹は不透明、葉はアルファ テスト** |
| **影** | **影の LOD は、描画より粗くする**（[影](../../shadows/index.md)） |

## よくあるミス

??? failure "LOD が切り替わる時、木がポップする"
    **ディザ フェード**で**切り替える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **近くは詳細、遠くはビルボード**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Vegetation](index.md)
- [Dithered Transparency](../../translucency/alpha-test/dither.md)
