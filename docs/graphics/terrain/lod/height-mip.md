---
title: Heightmap LOD (Mips)
tags:
  - 描画
---

# Heightmap LOD (Mips)

**遠くの地形は、高さマップも粗くてよく、ミップマップが使えます**。**LOD に応じて、読むミップを選ぶ**と、**テクスチャのちらつきと帯域**を**減らせます**。このページでは、**高さマップのミップ**を説明します。

!!! tip "ポイント"
    - **高さマップにも、ミップを作る**。
    - **頂点の LOD に合わせて、ミップを選ぶ**。
    - **ミップで高さの平均を取ると、山が低くなる**。
    - **最大・最小のミップも用意すると、カリングに使える**。

## 高さマップの LOD（ミップ）
**メッシュだけでなく、高さマップもミップを使います**。**遠くの頂点は粗いミップから読む**と**ちらつかず、メモリ アクセスも減ります**。

対応の要点です。ミップ レベルは LOD レベルに対応し、LOD が 1 下がるごとに、ミップを 1 上げます。高さのミップは平均でよいですが、最大値のミップもカリングに使えます。最小・最大の高さは、ノードの境界ボックスに使います。

## よくあるミス

??? failure "遠くの山が、低く見える"
    **最大値のミップ**も**併用**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **LOD に合わせて、ミップを選ぶ**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain LOD](index.md)
- [Heightmaps and Meshes](../heightmap-mesh/index.md)
