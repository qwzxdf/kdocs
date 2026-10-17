---
title: ② 光の注入
tags:
  - 描画
---

# ② 光の注入

**各 froxel に、太陽やライトの光を計算して、足します**。**シャドウ マップを参照**して、**影の中は光を入れない**ので、**光の筋ができます**。このページでは、**光の注入**を説明します。

!!! tip "ポイント"
    - **各セルで、ライトの光 × 位相関数 × 影**。
    - **太陽・点光源・スポットライトのすべてに対応**。
    - **シャドウ マップを参照**して、**光の筋**を作る。
    - **ライトの数が多いと、重い**（クラスタ化で軽く）。

## ② 光の注入
**各 froxel が受けている光を計算します**。<strong>太陽光とローカル ライト（点光源・スポットライト）</strong>が**対象**です。

<div class="formula">散乱光 = 密度 × アルベド × Σ ( 光の色 × 影 × 位相関数(θ) )</div>

```hlsl
float3 inscattered = 0;

float shadow = SampleCascadeShadow(world_position);
float phase = HenyeyGreenstein(dot(view_dir, -sun_direction), g);
inscattered += sun_color * shadow * phase;

for (uint i = 0; i < light_count; ++i) {
  float3 to_light = lights[i].position - world_position;
  float distance_to_light = length(to_light);
  float3 light_dir = to_light / distance_to_light;
  float attenuation = LightAttenuation(lights[i], distance_to_light);
  float light_shadow = SampleLocalShadow(lights[i], world_position);
  float p = HenyeyGreenstein(dot(view_dir, -light_dir), g);
  inscattered += lights[i].color * attenuation * light_shadow * p;
}

inscattered += ambient_fog_color;
float3 scattering = inscattered * density * albedo;
```

| 点 | 説明 |
| --- | --- |
| **シャドウ マップを引く** | **影の中の霧は光らない**。**この結果、物の影が光の筋として見える** |
| **位相関数** | <strong>前方に強く散る（g ≈ 0.6〜0.8）</strong>。**太陽の方を見ると霧が明るい**（[大気散乱](../scattering/index.md)） |
| **環境光** | **全体にうっすら足す**（暗すぎる霧の防止） |
| **ライトの数が多い場合** | **froxel ごとにライトをカリング**（[ライト カリング](../../../rendering/light-culling.md)） |
| **解像度が低くても綺麗** | **霧は低周波**（細かい構造がない）ので低解像度で十分 |

## よくあるミス

??? failure "光の筋が出ない"
    **シャドウ マップを参照**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **セルごとに、ライトと影を計算**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [ボリューメトリック フォグ](index.md)
- [密度](density.md)
- [積分](integration.md)
