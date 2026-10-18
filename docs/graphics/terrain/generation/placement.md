---
title: Placement Generation
tags:
  - 描画
---

# Placement Generation

**木・岩・草の配置も、ルールから自動で生成**できます。**高さ・傾き・湿度などの条件から、密度を決めて、散布**します。このページでは、**配置の生成**を説明します。

!!! tip "ポイント"
    - **条件（高さ・傾き・水辺）から、密度マップを作る**。
    - **ブルー ノイズで、均等に散布**する。
    - **シード値で、決定的にする**。
    - **手動の配置と、併用する**。

## 配置の生成
**地形の上に何を置くかも、手続き的に決められます**。

| 要素 | 内容 |
| --- | --- |
| **植生** | **高さ・傾き・湿度・ノイズから密度を決める**（[Vegetation](../vegetation/index.md)） |
| **岩** | **傾きが急な所／侵食で削れた所** |
| **道** | **2 点間の最小コスト経路（A\*）<strong>。</strong>傾きが緩い所を通る** |
| **集落** | **平らで水に近い所** |
| **ポアソン円盤サンプリング** | **点が近づきすぎない、自然な散らばり** |

## よくあるミス

??? failure "木が、一直線や固まりで並ぶ"
    **ブルー ノイズ**で**散布**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **条件で密度を決めて、散布**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain Generation](index.md)
- [Vegetation](../vegetation/index.md)
