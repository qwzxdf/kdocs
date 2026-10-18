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

木の LOD です。LOD 0（近景）は、幹と枝の 3D モデルに、葉のカード（板に葉の絵）を組み合わせます。LOD 1〜2 は、枝を減らし、葉のカードを統合します。インポスター（遠景）は、木を数方向から撮った絵（板ポリ）に置き換え、カメラの向きに応じて絵を切り替えたり混ぜたりします。ビルボード（最遠）は、1 枚の板です。

**インポスター**は、**事前に木を複数の視点（例：8×8 = 64 方向）から撮影**し、**アトラスに並べます**。**描画時はカメラに最も近い方向の絵を選び、板に貼ります**。**法線・深度もアトラスに持つと、ライティングも正しく**なります。

補足の要点です。LOD の切り替えは、ディザリング（市松のフェード）でポップを隠します（[Alpha Testing](../../translucency/alpha-test/index.md)）。葉のカードは、1 枚に複数の葉を描いた板で、アルファ テストを使います。幹と葉でマテリアルを分け、幹は不透明、葉はアルファ テストにします。影の LOD は、描画より粗くします（[Shadows](../../shadows/index.md)）。

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
