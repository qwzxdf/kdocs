---
title: ① 密度
tags:
  - 描画
---

# ① 密度

**最初の段階で、各 froxel の霧の濃さ（密度）を決めます**。**一様な霧・高さフォグ・ノイズの雲のような濃淡**を**組み合わせます**。このページでは、**密度の決め方**を説明します。

!!! tip "ポイント"
    - **基本の密度 ＋ 高さによる減衰**。
    - **ノイズで、濃淡を付ける**（動かして、流れを出す）。
    - **ローカルなボリューム（部屋の霧）も足せる**。
    - **密度は、散乱係数と吸収係数に分ける**。

## ① 密度
**霧の濃さを各 froxel に書きます**。**複数の要素を足し合わせます**。

| 要素 | 内容 |
| --- | --- |
| **全体の霧** | **一様な基準の密度**（`global_density`） |
| **高さフォグ** | **高さで指数的に減る**（[距離フォグ](../aerial-fog/index.md)） |
| **ノイズ** | **3D ノイズで濃淡**を付け、**風で流す** |
| **ローカルな霧のボリューム** | **箱・球で局所的に濃くする**（部屋の煙、洞窟） |
| **パーティクル** | **煙のパーティクルが密度を足す** |

```hlsl
float3 world_position = FroxelToWorld(id, slice_count);
float density = global_density;
density += height_density * exp(-height_falloff * (world_position.y - fog_base));
density *= 1.0 + noise_strength * Noise3D(world_position * noise_scale + wind * time);
density = max(density, 0.0);
```

## よくあるミス

??? failure "霧が一様で、単調"
    **ノイズ**で**濃淡**を付ける。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **基本の密度に、ノイズと高さを組み合わせる**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [ボリューメトリック フォグ](index.md)
- [froxel](froxel.md)
- [光の注入](injection.md)
