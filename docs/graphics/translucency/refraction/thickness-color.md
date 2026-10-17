---
title: 厚みと色
tags:
  - 描画
---

# 厚みと色

**色付きのガラスや水は、光が通る距離（厚み）が長いほど、色が濃くなります**。**これがビア＝ランバートの法則**で、**吸収を指数で表します**。このページでは、**厚みの求め方と、色の付け方**を説明します。

!!! tip "ポイント"
    - **透過率 ＝ exp(−吸収係数 × 厚み)**。
    - **厚み ＝ 裏面の深度 − 表面の深度**で求める。
    - **色ごとに吸収係数を変える**と、**色付きになる**。
    - **厚みが一定でも、見た目を作れる**（簡易版）。

## 厚みと色（ビア＝ランバートの法則）
**色付きガラスや水は、厚いほど、光が吸収されて色が濃く**なります。

<div class="formula">T = exp(−σ · d)　（T：透過率、σ：吸収係数（RGB）、d：厚み）</div>

| 記号 | 意味 |
| --- | --- |
| <strong>σ（シグマ）</strong> | **単位長さあたりの吸収**（**色ごと**）。**水は赤を強く吸収**（σ_r が大きい） |
| **d** | **光が媒質の中を進む距離**（厚み） |
| **T** | **透過する光の割合**（RGB） |

```hlsl
float3 absorption = float3(0.4, 0.1, 0.05);
float3 transmittance = exp(-absorption * thickness);
float3 tinted_background = background * transmittance;
```

| 点 | 説明 |
| --- | --- |
| **`absorption`** | <strong>吸収係数（RGB）</strong>。**水なら、赤を強く、青を弱く**吸収し、**青緑に見える** |
| **`thickness`** | **厚み**。**ガラスなら、ほぼ一定**。<strong>水なら、水深（深度差）</strong> |
| **`exp(-σd)`** | **厚いほど、急に暗く・濃く** |

**水深**（水面から底までの距離）は、**不透明の深度と、水面の深度の差**から**求められます**（[水](../../water/index.md)）。

## よくあるミス

??? failure "厚いガラスも薄いガラスも、同じ色"
    **厚みで、濃さを変える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **厚みが長いほど、色が濃い**
    - [x] **exp で吸収を表す**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [屈折](index.md)
- [薄いガラスと厚いガラス](thin-thick.md)
- [水の質感](../../water/shading/index.md)
