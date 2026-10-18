---
title: Ground and Space Views
tags:
  - 描画
---

# Ground and Space Views

**視点が地面にある時と、宇宙にある時で、大気の見え方は違います**。**地面からは空が、宇宙からは地球の縁が光る**ように見えます。このページでは、**視点の位置による違い**を説明します。

!!! tip "ポイント"
    - **地面：空の色と、地平線の霞**。
    - **宇宙：地球の縁（リム）の大気**。
    - **視点の高さで、LUT の使い方が変わる**。
    - **地面の反射（アルベド）も、空に影響**する。

## 地面と宇宙
| 状況 | 扱い |
| --- | --- |
| **地面の反射** | **地面のアルベドで地平線付近が明るくなる**。**地面からの散乱を足す** |
| **宇宙から見た地球** | **視点が大気の外のとき、大気の入口まで進めてから積分**（**惑星表面の光る縁**） |
| **日食・月食** | **太陽の円盤が欠けるとき、直射光を減らす** |
| **影の中の空気** | **山の影で空気中の光の筋が途切れる**（[光の筋](../god-rays/index.md)） |

## よくあるミス

??? failure "宇宙から見た地球に、大気の縁が見えない"
    **宇宙からの視点**でも**大気の積分**を**行う**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **視点の高さで、積分の範囲が変わる**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Bruneton Precomputed Scattering](bruneton.md)
