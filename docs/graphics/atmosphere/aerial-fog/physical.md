---
title: Physically Based Aerial Perspective
tags:
  - 描画
---

# Physically Based Aerial Perspective

**大気散乱の LUT（空気遠近法 LUT）を使うと、距離ごとの散乱と透過率を、物理的に正しく求められます**。**空と完全に一致する**のが**利点**です。このページでは、**物理に基づく空気遠近法**を説明します。

!!! tip "ポイント"
    - **カメラからの距離ごとの、散乱と透過率を LUT に**。
    - **空と同じ計算なので、色が一致**。
    - **時刻・天候が変わっても、自動で追従**。
    - **Hillaire 2020 の空気遠近法 LUT**。

## 物理に基づく空気遠近法
**大気散乱**（[Atmospheric Scattering](../scattering/index.md)）の**LUT** を**使うと**、**距離フォグを物理的に決められます**。<strong>Hillaire 2020 の「空気遠近法 LUT」</strong> は、**カメラ前方の froxel ごとの「散乱光」と「透過率」を保持**します。

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

### 空気遠近法 LUT の作り方

Hillaire の方式（EGSR 2020、"A Scalable and Production Ready Sky and Atmosphere Rendering Technique"）では、カメラの前方に、画面に合わせた 3D テクスチャ（froxel 格子）を用意します。解像度は 32×32×32 程度の小さなものです。x と y が画面上の位置、z がカメラからの距離（深度スライス）に対応します。

毎フレーム、この 3D テクスチャの各セルで、「カメラからそのセルまでの視線」に沿って、単散乱をレイマーチで積分します。各セルには、そこまでの<strong>散乱光（RGB）</strong>と<strong>透過率</strong>（アルファに、RGB の平均値）を保存します。多重散乱は、別に用意した小さな LUT（Multi-Scattering LUT）から近似して足します（[Multiple Scattering](../scattering/multiple-scattering.md)）。

実行時は、画面のピクセルの深度から、対応するスライスを求め、その位置で LUT を 1 回引くだけです。フォグの計算は、ピクセルあたりテクスチャ 1 回の読み込みで済みます。LUT が小さいので、生成のコストも小さく（0.1 ms 前後）、品質と速さを両立できます。

LUT の距離方向は、線形でなく、近くを細かく取る非線形な配置にします。近くのフォグは細かい距離変化が目につき、遠くは緩やかな変化で十分だからです。また、最大距離（たとえば 128 km）は、シーンの規模に合わせて決めます。

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

- [Aerial Perspective and Fog](index.md)
- [Hillaire 2020](../scattering/hillaire.md)
