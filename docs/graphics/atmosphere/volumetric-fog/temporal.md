---
title: Temporal Accumulation
tags:
  - 描画
---

# Temporal Accumulation

**froxel の解像度は低いので、ノイズや段が出ます**。**毎フレーム、サンプルの位置をずらして、前フレームと混ぜる**と、**実質の解像度が上がり、なめらか**になります。このページでは、**時間蓄積**を説明します。

!!! tip "ポイント"
    - **毎フレーム、サンプル位置を少しずらす（ジッタ）**。
    - **前フレームの結果を、再投影して混ぜる**。
    - **動く物体の周りで、ゴーストに注意**。
    - **TAA と同じ考え方**。

## 時間蓄積（TAA 風）
**froxel の解像度が低く、サンプルが少ない**ので**そのままだとノイズや縞が出ます**。**前フレームの結果を再利用して、時間方向に平均します**。

| 工夫 | 内容 |
| --- | --- |
| **ジッター** | **毎フレーム、froxel 内のサンプル位置を少しずらす**（ブルー ノイズなど） |
| **履歴の再投影** | **前フレームの froxel の位置を、カメラの動きで求めて、その値を混ぜる** |
| **ブレンド率** | **新 5〜10 %、履歴 90〜95 %** |
| **履歴の拒否** | **ライトが動いたとき／急な変化は、履歴を弱める** |

```hlsl
float3 previous_uvw = ReprojectFroxel(world_position, previous_view_projection);
float4 history = history_volume.SampleLevel(linear_clamp, previous_uvw, 0);
float4 current = float4(scattering, extinction);
float blend = IsValidHistory(previous_uvw) ? 0.05 : 1.0;
float4 result = lerp(history, current, blend);
```

## よくあるミス

??? failure "霧が、動くと尾を引く"
    **履歴の拒否**・**ブレンド率の調整**をする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **ジッタと再投影で、実質の解像度を上げる**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Volumetric Fog](index.md)
- [TAA](../../postprocess/antialiasing/taa.md)
