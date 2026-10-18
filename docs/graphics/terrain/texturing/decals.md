---
title: Terrain Decals and Roads
tags:
  - 描画
---

# Terrain Decals and Roads

**道や足跡のように、地形の一部に貼るものは、デカール（貼り付け）で表現します**。**地形の形に沿って、投影する**ことで、**自然に重ねられます**。このページでは、**地形のデカールと道**を説明します。

!!! tip "ポイント"
    - **デカール ＝ 地形に投影するテクスチャ**。
    - **道は、スプライン（曲線）に沿って、生成する**。
    - **足跡は、動的に追加する**。
    - **重ねすぎると、重い**。

## 地形のデカールと道
地形のデカールの要素です。道や小道は、スプラット マップにスプライン沿いに塗ります。足跡やタイヤの跡は、スプラットやデカールに描き込みます。焼け跡や血痕は、デカールを投影します。整地では、高さマップも同時に整えます。

## よくあるミス

??? failure "道が地形から浮いて見える"
    **地形に投影**する、または**高さを合わせる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **地形に投影して、道や足跡を重ねる**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain Texturing](index.md)
- [Virtual Texturing](virtual-texture.md)
