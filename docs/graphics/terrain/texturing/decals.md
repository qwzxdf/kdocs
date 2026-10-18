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

## Terrain Decals and Roads {#地形のデカールと道}
| 要素 | 内容 |
| --- | --- |
| **道・小道** | **スプラット マップにスプライン沿いに塗る** |
| **足跡・タイヤの跡** | **スプラット／デカールに描き込む** |
| **焼け跡・血痕** | **デカール**を**投影** |
| **整地** | **高さマップも同時に整える** |

## Common Mistakes {#よくあるミス}

??? failure "道が地形から浮いて見える"
    **地形に投影**する、または**高さを合わせる**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **地形に投影して、道や足跡を重ねる**

## References {#参考}

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## Related Pages {#関連ページ}

- [Terrain Texturing](index.md)
- [Virtual Texturing](virtual-texture.md)
