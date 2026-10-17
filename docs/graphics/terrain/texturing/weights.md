---
title: 重みを決める
tags:
  - 描画
---

# 重みを決める

**スプラットの重みは、どのテクスチャを、どれだけ使うかを決める値**です。**手でペイント**、**または高さ・傾きから自動で決める**ことが**多い**です。このページでは、**重みの決め方**を説明します。

!!! tip "ポイント"
    - **ペイント：スプラット マップ（RGBA）に塗る**。
    - **自動：高さ・傾きで決める**（雪は高所、岩は急斜面）。
    - **重みの合計を 1 にする**。
    - **4 枚ごとに 1 枚のスプラット マップ**。

## 重みを決める
| 方法 | 内容 |
| --- | --- |
| **手描き** | **地形エディタでブラシで塗る** |
| **ルールで自動** | **高さ・傾きから決める**（下の表） |
| **侵食の結果から** | **堆積した所は土・砂、削られた所は岩**（[地形の生成](../generation/index.md)） |

| 条件 | 地面 |
| --- | --- |
| **傾きが緩やか・低い** | **草** |
| **傾きが急** | **岩** |
| **高い所** | **雪** |
| **水の近く** | **砂・泥** |

```hlsl
float slope = 1.0 - saturate(normal.y);
float rock = smoothstep(0.35, 0.55, slope);
float snow = smoothstep(snow_line, snow_line + 20.0, world_position.y) * (1.0 - rock);
float grass = (1.0 - rock) * (1.0 - snow);
```

**ルールで基礎を作り、手描きの重みを足して調整する**のが**実用的**です。

## よくあるミス

??? failure "重みの合計が 1 でなく、地形が暗い・明るい"
    **重みを正規化**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **ペイントか自動で決め、合計 1 にする**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [地形のテクスチャ](index.md)
- [高さによるブレンド](height-blend.md)
