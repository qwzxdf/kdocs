---
title: ReSTIR GI
tags:
  - 描画
---

# ReSTIR GI

**ReSTIR は、「良いサンプルを、隣の画素や前フレームから借りる」ことで、少ないレイでも、きれいな結果を出す手法**です。**重みつきリザーバー サンプリング**を使い、**サンプルを再利用**します。このページでは、**ReSTIR の考え方と効果**を説明します。

!!! tip "ポイント"
    - **リザーバーに、「良さそうなサンプル」を 1 つだけ保持**する。
    - **隣の画素・前フレームのリザーバーと混ぜる（再利用）**。
    - **再利用すると、実質のサンプル数が、桁違いに増える**。
    - **バイアスの管理（再利用してよいかの判定）が難しい**。

## ReSTIR GI
**ReSTIR**（Reservoir-based Spatiotemporal Importance Resampling）は、<strong>「良いサンプルを近い画素・前フレームから借りる」</strong>ことで、**1 画素あたりの有効なサンプル数**を**大幅に増やす**手法です。

| 概念 | 内容 |
| --- | --- |
| **リザーバー** | <strong>画素ごとに、「これまでで最良のサンプル 1 つ」</strong>と**重みの合計**を保持（**重み付きリザーバー サンプリング**） |
| **時間的な再利用** | **前フレームの同じ位置のリザーバー**と**マージ** |
| **空間的な再利用** | **近隣の画素のリザーバー**と**マージ** |
| **バイアスの補正** | **他の画素のサンプル**が**この画素にとって有効か**（**可視性・ヤコビアン**）を**補正** |
| **効果** | <strong>少ないレイ（1 本）</strong>で、**多数のレイを飛ばしたような**品質 |

**ReSTIR DI**（直接光）から、**ReSTIR GI**（間接光）、**ReSTIR PT**（パス全体）へと**発展**しています。**NVIDIA RTXDI・RTXGI** などに**採用**されています。

## よくあるミス

??? failure "再利用が強すぎて、光が不自然ににじむ"
    **法線・深度が合わないサンプルは再利用しない**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **良いサンプルを借りて、少ないレイで高品質**
    - [x] **バイアスの管理が、鍵**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [レイトレ GI](index.md)
- [ノイズとの戦い](noise.md)
- [手法の選び方](choosing.md)
