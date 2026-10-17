---
title: 雲の影
tags:
  - 描画
---

# 雲の影

**雲は、地上に影を落とします**。**雲の密度を、太陽方向に積分した「影マップ」**を**作り、地面の明るさに反映**します。このページでは、**雲の影**を説明します。

!!! tip "ポイント"
    - **雲の透過率を、太陽方向のマップに記録**。
    - **地面のシェーディングで、そのマップを参照**。
    - **雲が動くと、影も動く**。
    - **低解像度で十分**。

## 影
**雲は地面や他の雲に影を落とします**。

| 影の種類 | 内容 |
| --- | --- |
| <strong>雲の影（地面へ）</strong> | **地面の位置から太陽方向へ雲を積分して、日が差す量を減らす**。**または雲の影用のマップ（光方向の透過率）を事前に作る** |
| **雲の自己影** | <strong>光のマーチ（上記）</strong> |
| **山の影が雲に** | **シャドウ マップを雲のサンプルで引く** |
| **光の筋** | **雲の隙間から差す光**（[光の筋](../god-rays/index.md)） |

## よくあるミス

??? failure "雲の影が地上に落ちない"
    **雲の影マップ**を作り、**地面で参照**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **雲の透過率を、影マップにして使う**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [雲](index.md)
- [カスケード シャドウ](../../shadows/cascaded.md)
