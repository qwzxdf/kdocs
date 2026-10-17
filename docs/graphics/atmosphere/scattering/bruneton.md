---
title: Bruneton Precomputed Scattering
tags:
  - 描画
---

# Bruneton Precomputed Scattering

**Bruneton の手法は、散乱の結果を、高さ・視線の角度・太陽の角度の 4 次元のテーブルに、事前計算しておく**ものです。**実行時は、テーブルを引くだけ**で、**高品質**ですが、**メモリが大きい**です。このページでは、**Bruneton の事前計算**を説明します。

!!! tip "ポイント"
    - **4D のテーブル（高さ・視線・太陽・太陽と視線）**を事前計算。
    - **実行時は、テーブルを読むだけ**。
    - **品質が高い。メモリが大きい**。
    - **大気の設定を変えると、再計算が必要**。

## Bruneton の事前計算
<strong>Bruneton & Neyret（2008）</strong>は、**単散乱・多重散乱をすべて 4D のテーブルに事前計算**し、**実行時は表引き**で空を描きます。

| 項目 | 内容 |
| --- | --- |
| **4 つの次元** | **観測者の高さ・視線の天頂角・太陽の天頂角・視線と太陽の方位角差** |
| **3D テクスチャに詰める** | **4D を 3D テクスチャに展開**（**方位角を横に並べる**） |
| **利点** | **実行時は数回のサンプルだけ**。**多重散乱込みで正確** |
| **欠点** | **事前計算が重い**。**時刻や大気の組成を変えると、計算し直し**（**太陽の位置は表の次元にあるので動かせる**が、**大気の密度は固定**） |
| **用途** | **地上〜宇宙まで**、**大気の組成が固定**のゲーム |

## よくあるミス

??? failure "大気のパラメータを変えても、空が変わらない"
    **テーブルを再計算**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **4D テーブルに事前計算して、引くだけ**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Hillaire 2020](hillaire.md)
