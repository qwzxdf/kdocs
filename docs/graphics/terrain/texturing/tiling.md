---
title: 繰り返しを隠す
tags:
  - 描画
---

# 繰り返しを隠す

**タイル テクスチャは、広い範囲に貼ると、繰り返しが目立ちます**。**大きさの違うテクスチャを重ねる・ランダムに回転させる**ことで、**隠せます**。このページでは、**タイリングの隠し方**を説明します。

!!! tip "ポイント"
    - **異なるスケールで 2 回貼って、混ぜる**。
    - **ノイズで、テクスチャ座標をずらす**。
    - **タイルごとに、ランダムに回す・反転する**。
    - **遠くは、低周波の色むらを重ねる**。

## 繰り返し（タイリング）を隠す
**繰り返しテクスチャは、広い範囲に貼ると同じ模様の並びが目立ちます**。

| 工夫 | 内容 |
| --- | --- |
| **2 つのスケールを重ねる** | **大きさの違う 2 枚を混ぜる**（**周期がずれる**） |
| **近景・遠景のスケール** | **距離で細かいタイルと大きなタイルを切り替える** |
| **タイルごとにランダムに回す** | **セルごとに回転・オフセットを変える**（**ハッシュで決める**）。**境でブレンド** |
| **マクロ バリエーション** | **低周波のノイズで色を少しずらす** |
| **ディテール テクスチャ** | **近づいたときだけ、細かい模様を重ねる** |

```hlsl
float2 uv_near = world_position.xz * 0.5;
float2 uv_far = world_position.xz * 0.043;
float3 near_color = albedo.Sample(linear_wrap, uv_near).rgb;
float3 far_color = albedo.Sample(linear_wrap, uv_far).rgb;
float3 color = near_color * far_color * 2.0;
```

**2 枚を掛けて 2 倍**にすると、**平均の明るさが保たれます**。

## よくあるミス

??? failure "格子状の繰り返しが、遠くから見て目立つ"
    **スケールを変えた重ね貼り**をする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **スケールを変えて重ね、ノイズでずらす**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [地形のテクスチャ](index.md)
- [トライプラナー](triplanar.md)
