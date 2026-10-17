---
title: Using the Sky for Lighting
tags:
  - 描画
---

# Using the Sky for Lighting

**空は、シーンを照らす光源でもあります**。**空の色を、環境マップ（IBL）に焼いて、拡散・鏡面の環境光に使う**と、**空と地上の色が自然になじみます**。このページでは、**空のライティング**を説明します。

!!! tip "ポイント"
    - **空のキューブマップを作って、環境光に使う**。
    - **拡散は SH、鏡面はミップ付きキューブマップ**。
    - **時間が変わるたびに、更新する**。
    - **1 フレームで少しずつ更新**して、**コストを分散**する。

## 空をライティングに使う
**空は大きな光源**でもあります。**地面や物は空から環境光を受けます**。

空をライティングに使う方法は 4 つあります。キューブマップに焼く方法は、空を 6 面に描画し、ミップで粗さを作ります（IBL）。空が変わったら更新します。球面調和関数（SH）の方法は、空の色を SH（L2 の 9 係数）に投影して、拡散の環境光に使います（[ライティング](../../../3d/lighting-normals.md)）。更新の頻度は、時間変化がゆっくりなので、数秒に 1 回、数フレームかけて更新します。太陽は直接光なので、太陽の寄与は環境マップから除き、平行光源として別に扱います（二重に数えないためです）。

## よくあるミス

??? failure "時間が変わっても、地上の明るさが変わらない"
    **環境マップを、空に合わせて更新**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **空を環境マップにして、光源に使う**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Sky Models](index.md)
- [Reflection Probes](../../reflections/probes/index.md)
- [GI Theory](../../gi/theory/index.md)
