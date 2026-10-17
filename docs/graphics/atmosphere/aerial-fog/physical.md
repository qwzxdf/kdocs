---
title: 物理に基づく空気遠近法
tags:
  - 描画
---

# 物理に基づく空気遠近法

**大気散乱の LUT（空気遠近法 LUT）を使うと、距離ごとの散乱と透過率を、物理的に正しく求められます**。**空と完全に一致する**のが**利点**です。このページでは、**物理に基づく空気遠近法**を説明します。

!!! tip "ポイント"
    - **カメラからの距離ごとの、散乱と透過率を LUT に**。
    - **空と同じ計算なので、色が一致**。
    - **時刻・天候が変わっても、自動で追従**。
    - **Hillaire 2020 の空気遠近法 LUT**。

## 物理に基づく空気遠近法
**大気散乱**（[大気散乱](../scattering/index.md)）の**LUT** を**使うと**、**距離フォグを物理的に決められます**。<strong>Hillaire 2020 の「空気遠近法 LUT」</strong> は、**カメラ前方の froxel ごとの「散乱光」と「透過率」を保持**します。

```hlsl
float4 aerial = aerial_perspective_lut.SampleLevel(linear_clamp, float3(uv, depth_slice), 0);
float3 inscattered = aerial.rgb;
float transmittance = aerial.a;
float3 final_color = scene_color * transmittance + inscattered;
```

| 点 | 説明 |
| --- | --- |
| **`inscattered`** | **視線上で散乱して、カメラに入る光**（**霞の明るさと色**） |
| **`transmittance`** | **物の光が残る割合** |
| **深度スライス** | **深度をスライス番号に変換**（**非線形**）して**サンプル** |
| **利点** | **昼・夕・夜で自動的に色が変わる**。**太陽の方向も反映** |

## よくあるミス

??? failure "空とフォグの色が合わない"
    **空と同じ LUT** を**フォグにも使う**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **空と同じ LUT で、色が一致する**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [空気遠近法・フォグ](index.md)
- [Hillaire 2020](../scattering/hillaire.md)
