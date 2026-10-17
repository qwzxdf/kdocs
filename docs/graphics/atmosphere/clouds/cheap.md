---
title: 簡易な代替
tags:
  - 描画
---

# 簡易な代替

**レイマーチが重い環境では、簡易な代替があります**。**スカイボックスのテクスチャ・ビルボード・平面に貼る雲**などで、**雰囲気を出します**。このページでは、**簡易な雲の表現**を説明します。

!!! tip "ポイント"
    - **スカイボックスに、雲を描いておく**。
    - **平面に、雲のテクスチャを流す**（スクロール）。
    - **ビルボードの雲**を配置する。
    - **モバイルでは、これが標準**。

## 簡易な代替
**重いレイマーチが使えない場面**の**代替**です。

| 方式 | 内容 |
| --- | --- |
| **雲のスカイボックス** | **事前に描いた雲のキューブマップを回す** |
| <strong>2D の雲（スカイドームの絵）</strong> | **スクロールする雲のテクスチャ ＋ 法線マップで凹凸** |
| **フローマップで動かす** | **雲の絵を流れの向きに動かす**（[水のフローマップ](../../water/interaction/index.md)） |
| <strong>ボリューム テクスチャ（事前焼き）</strong> | **雲の塊を 3D テクスチャに焼き、ビルボードで描く** |
| <strong>雲の板（インポスター）</strong> | **遠景の雲を板で置く** |

## よくあるミス

??? failure "簡易な雲が、動かず、不自然"
    **テクスチャを、ゆっくりスクロール**させる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **重い環境では、テクスチャとビルボードで代替**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [雲](index.md)
- [グラデーションの空](../sky-models/gradient.md)
