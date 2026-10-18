---
title: Height-Based Blending
tags:
  - 描画
---

# Height-Based Blending

**重みだけで混ぜると、境目がぼやけて、のっぺりします**。**各テクスチャの「高さ（凹凸）」を使って混ぜる**と、**土の隙間から草が生える**ような、**自然な境目**になります。このページでは、**高さブレンド**を説明します。

!!! tip "ポイント"
    - **各テクスチャに、高さ情報を持たせる**。
    - **重み ＋ 高さの大きい方が勝つ**ように、混ぜる。
    - **境目に、凹凸に沿った模様が出る**。
    - **コストは少し増える**。

## 高さによるブレンド
**重みの線形ブレンドは、境目がぼんやり混ざって不自然**です。**実際の地面は、「石の隙間に土が入り込む」ように凹凸に沿って境ができます**。**各テクスチャの高さ（ハイトマップ）を足し込んでから、一番高い層を優先**すると**自然な境目**になります。

```hlsl
float4 heights = float4(
  height_array.Sample(linear_wrap, float3(tile_uv, 0)).r,
  height_array.Sample(linear_wrap, float3(tile_uv, 1)).r,
  height_array.Sample(linear_wrap, float3(tile_uv, 2)).r,
  height_array.Sample(linear_wrap, float3(tile_uv, 3)).r);

float4 blended = weights + heights * height_strength;
float max_value = max(max(blended.r, blended.g), max(blended.b, blended.a)) - blend_depth;
float4 final_weights = max(blended - max_value, 0.0);
final_weights /= (final_weights.r + final_weights.g + final_weights.b + final_weights.a);
```

高さブレンドのコードの要点です。`blend_depth` は境目の幅（0.1 程度）で、小さいと鋭く、大きいとぼやけます。高い層が勝つので、凸な所が先に現れ、凹んだ所に他の層が残ります。テクスチャごとに高さのチャンネルが必要で、法線マップのアルファなどに詰めます。

## よくあるミス

??? failure "テクスチャの境目が、ぼやけてのっぺり"
    **高さブレンド**を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **凹凸の高さを使って、混ぜる**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain Texturing](index.md)
- [Splat Weights](weights.md)
