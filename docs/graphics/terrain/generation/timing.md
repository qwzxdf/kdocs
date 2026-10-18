---
title: When to Generate
tags:
  - 描画
---

# When to Generate

**地形の生成は、事前に行うか、実行時に行うか、選べます**。**事前なら重い処理ができ、実行時なら無限に広い地形が作れます**。このページでは、**生成のタイミングの選び方**を説明します。

!!! tip "ポイント"
    - **事前生成：高品質（侵食も）。データが大きい**。
    - **実行時生成：無限の地形。軽いノイズだけ**。
    - **ハイブリッド：事前の骨格 ＋ 実行時の細部**。
    - **シード値で、同じ地形を再現できる**。

## When to Generate {#生成のタイミング}
生成のタイミングは 3 つの方式があります。事前に作って焼く方式（オフライン）は、地形ツール（World Machine・Gaea・Houdini）や自作ツールで高さマップを生成し、ゲームにはテクスチャとして持ち込みます。ランタイム生成は、ゲーム中にシードから生成する方式で、ノイズ関数は軽いので、チャンクごとに GPU や CPU で生成できます。無限の世界やランダム ステージに向きます。ハイブリッドは、大きな形は手で描き、細かい起伏だけノイズで足します。

**ランタイム生成**では、**チャンクの境界で値が連続する**こと（**ワールド座標でノイズを引く**）、**侵食は隣のチャンクにも影響する**ため**難しい**ことに**注意**します。

## Common Mistakes {#よくあるミス}

??? failure "実行時に侵食を計算して、重い"
    **事前に計算**して、**結果を保存**する。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **重い処理は事前、細部は実行時**

## References {#参考}

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## Related Pages {#関連ページ}

- [Terrain Generation](index.md)
- [Chunking](../heightmap-mesh/chunks.md)
