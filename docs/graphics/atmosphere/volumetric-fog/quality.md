---
title: Quality and Performance
tags:
  - 描画
---

# Quality and Performance

**ボリューメトリック フォグは、解像度とスライス数で、品質とコストが大きく変わります**。このページでは、**品質と速度の目安**を説明します。

!!! tip "ポイント"
    - **解像度：160×90 が標準**（1080p の場合）。
    - **スライス数：64**が**標準**。
    - **ライトの数が多いと、重い**。
    - **品質設定で、解像度とスライス数を切り替える**。

## 品質と速度
| 項目 | 内容 |
| --- | --- |
| **解像度** | **160×90×64 で十分**。**重ければ 80×45×32** |
| **コスト** | **0.3〜1 ms 程度** |
| **局所ライトの数** | **多いほど重い**。**影付きのライトは数本まで** |
| **遠距離** | **範囲外は距離フォグ（[距離フォグ](../aerial-fog/index.md)）に任せる** |
| **雲・大気との組み合わせ** | **近くはボリューメトリック フォグ、遠くは空気遠近法 LUT** |

## よくあるミス

??? failure "フォグの計算が重く、フレーム時間が伸びる"
    **解像度・スライス数を下げる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **解像度とスライス数で、調整**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Volumetric Fog](index.md)
- [Froxels](froxel.md)
