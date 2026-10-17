---
title: Floating Objects
tags:
  - 描画
---

# Floating Objects

**船や浮き輪を、波に合わせて動かすには、波の高さを、CPU 側でも求める必要があります**。**頂点シェーダーの波の式を、CPU に同じ形で実装**するのが**簡単**です。このページでは、**浮力のための高さの取得**を説明します。

!!! tip "ポイント"
    - **波の式を、GPU と CPU の両方に実装**する。
    - **物体の数点で高さを取り、位置と傾きを決める**。
    - **FFT の場合は、GPU から読み戻すか、CPU で近似**する。
    - **浮力の物理は、[Water Interaction](../interaction/index.md)**を参照。

## 物を水に浮かせる
**ボートや浮き**を**波に合わせて動かす**には、**CPU 側でも同じ波の高さを計算**する必要があります。

| 方法 | 内容 |
| --- | --- |
| **同じ式を、CPU で計算** | **Gerstner 波**なら、**シェーダーと同じ式を C++ で実装**。**複数点をサンプルして、傾き・高さを決める** |
| **GPU から読み戻す** | **FFT の高さマップを、読み戻して**サンプル（**数フレーム遅れ**） |
| **簡易な近似** | **大きな波だけ**を CPU で計算し、**細かい波は無視** |

<strong>浮力（アルキメデスの原理）</strong>で、**水に浸かった体積に応じた力**を**与える**と、**物理的に浮く**動きになります。

## よくあるミス

??? failure "船が、見た目の波と合わずに浮く"
    **GPU と同じ式・同じ時間**で、**CPU 側も計算**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **CPU 側でも、波の高さを求める**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Water Waves](index.md)
- [Water Interaction](../interaction/index.md)
