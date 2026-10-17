---
title: Dynamic Updates
tags:
  - 描画
---

# Dynamic Updates

**ベイクしたプローブは、光や物が動くと、古くなります**。**動的に更新するには、プローブごとにレイを飛ばして、再計算します**。**1 フレームに更新する数を絞る**のが**コツ**です。このページでは、**動的更新の考え方**を説明します。

!!! tip "ポイント"
    - **ベイクだけだと、昼夜の変化・動く光に追従できない**。
    - **プローブからレイを飛ばして、再計算**（DDGI など）。
    - **1 フレームに更新するプローブ数を絞る**。
    - **変化が無い所は、更新を省く**。

## 動的な更新
**ベイクしたプローブ**は、**静的な光**に対する**固定**の値です。

| 方式 | 内容 |
| --- | --- |
| **ベイクのみ** | **固定**。**最も安い** |
| **ライトの強さ・色を実行時に掛ける** | **ライトごとにプローブを別々にベイク**し、**実行時に強さ・色で合成**（**複数ライト分のメモリ**） |
| **実行時に再ライティング** | **プローブごとにレイ・キューブマップ**で**毎フレーム更新**（[DDGI](../ddgi.md)・[Ray-Traced GI](../rt-gi/index.md)） |
| **時間帯の切り替え** | <strong>複数セット（朝・昼・夕）</strong>を、**補間** |

## よくあるミス

??? failure "光を動かしても、間接光がまったく変わらない"
    **動的更新（またはリアルタイム GI）**を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **レイで再計算して、動的に更新**
    - [x] **更新数を絞って、コストを抑える**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Probe GI](index.md)
- [DDGI](../ddgi.md)
- [置き方](placement.md)
