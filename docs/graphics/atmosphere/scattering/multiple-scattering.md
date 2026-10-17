---
title: Multiple Scattering
tags:
  - 描画
---

# Multiple Scattering

**光は、何度も散乱しながら進みます**。**単散乱だけだと、空の暗い部分（影・夕方）が暗すぎます**。**多重散乱を近似して足す**と、**明るさが自然**になります。このページでは、**多重散乱**を説明します。

!!! tip "ポイント"
    - **単散乱だけだと、暗すぎる**。
    - **多重散乱は、全方向からの光の和**。
    - **LUT で、近似的に計算する**（Hillaire 2020）。
    - **空の暗部・影・雲が、自然になる**。

## 多重散乱
**単散乱だけだと夕方や影の側の空が暗くなりすぎます**。**実際には一度散った光が何度も散ります**（**多重散乱**）。**地球の大気では、昼間の空の明るさの 1〜2 割は多重散乱**で、**夕暮れの空の明るさは多重散乱で決まります**。

| 近似 | 内容 |
| --- | --- |
| **ambient の底上げ** | **単散乱に一定の環境光を足す**（手軽・粗い） |
| **Bruneton の多重散乱** | **散乱次数ごとに事前計算を繰り返す**（正確・重い） |
| **Hillaire の近似** | **多重散乱を等方・無限級数の閉じた式で近似**し、**小さな 2D LUT にまとめる**（軽い） |

## よくあるミス

??? failure "影になる部分の空が、真っ黒"
    **多重散乱**を**足す**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **何度も散乱した光を、近似で足す**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Hillaire 2020](hillaire.md)
