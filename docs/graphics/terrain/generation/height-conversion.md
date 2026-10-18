---
title: Converting Noise to Height
tags:
  - 描画
---

# Converting Noise to Height

**ノイズの値を、そのまま高さにすると、平らな所と山が同じ比率になって不自然**です。**カーブを通して、平地を広く、山を高くする**と、**地形らしくなります**。このページでは、**ノイズから高さへの変換**を説明します。

!!! tip "ポイント"
    - **カーブで、分布を整える**（平地を広く）。
    - **海面より下は平ら**に。
    - **高さに応じて、ノイズの種類を変える**。
    - **スケール（高さの最大）を調整**。

## 地形の高さへの変換
**ノイズ値をそのまま高さにするのではなく、形を整えます**。

ノイズを高さに変換する工夫です。べき乗（`pow(h, 2.0)`）で、平地を広く、山を急にします。大陸の形は、低周波のノイズで陸と海の分布を作り、山のノイズを陸にだけ掛けます。高さの段差（テラス）は、`floor` で段にして、少し滑らかにします。島の形は、中心から離れるほど高さを下げる円のマスクで作ります。バイオームは、高さと湿度（別のノイズ）で地面の種類を決めます。

## よくあるミス

??? failure "どこも似た起伏で、変化が無い"
    **カーブで、平地と山の差を付ける**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **カーブで、高さの分布を整える**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain Generation](index.md)
- [fBm](fbm.md)
