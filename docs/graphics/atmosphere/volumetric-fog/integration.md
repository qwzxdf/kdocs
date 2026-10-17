---
title: ③ 積分と ④ 適用
tags:
  - 描画
---

# ③ 積分と ④ 適用

**注入した光を、視線に沿って奥から手前へ足し合わせます（積分）**。**その結果を、シーンの色に合成（適用）します**。このページでは、**積分と適用**を説明します。

!!! tip "ポイント"
    - **奥行き方向に、散乱光を累積し、透過率も求める**。
    - **結果は、3D テクスチャ（累積済み）**。
    - **適用：シーンの色 × 透過率 ＋ 散乱光**。
    - **シーンの深度から、froxel の位置を引く**。

## ③ 積分
**視線に沿って、手前から奥へ光と透過率を累積します**。**奥行き方向（Z）にループ**し、**各 froxel の寄与を足します**。

<div class="formula">
累積光 += 透過率 × 散乱光 × (1 − exp(−消散 × 厚み)) / 消散<br>
透過率 *= exp(−消散 × 厚み)
</div>

```hlsl
[numthreads(8, 8, 1)]
void IntegrateCS(uint3 id : SV_DispatchThreadID) {
  float3 accumulated = 0;
  float transmittance = 1.0;

  for (uint z = 0; z < kSliceCount; ++z) {
    float4 data = scattering_volume[uint3(id.xy, z)];
    float3 scattering = data.rgb;
    float extinction = max(data.a, 1e-5);

    float thickness = SliceThickness(z);
    float slice_transmittance = exp(-extinction * thickness);
    float3 integrated = (scattering - scattering * slice_transmittance) / extinction;

    accumulated += integrated * transmittance;
    transmittance *= slice_transmittance;

    integrated_volume[uint3(id.xy, z)] = float4(accumulated, transmittance);
  }
}
```

| 点 | 説明 |
| --- | --- |
| **厚みを考慮** | **スライスの厚みは奥ほど大きい**ので、**厚みで積分を厳密に**する |
| **解析的な積分** | **区間内の透過率を指数で厳密に**（粗いステップでも安定） |
| **結果を 3D テクスチャに保存** | **各スライスまでの累積**を保存し、**適用時に深度に応じた位置を引く** |
| **1 スレッドが奥まで** | **画面方向は並列、奥行き方向は順次** |

## ④ 適用
**不透明のシーンの色に積分結果を合成します**。**ピクセルの深度から、対応するスライスを求めて、3D テクスチャを引きます**。

```hlsl
float depth = LinearizeDepth(depth_texture.Sample(point_clamp, uv).r);
float slice = DepthToSlice(depth, kNear, kFar, kSliceCount);
float3 froxel_uvw = float3(uv, slice / kSliceCount);
float4 fog = integrated_volume.SampleLevel(linear_clamp, froxel_uvw, 0);

float3 final_color = scene_color * fog.a + fog.rgb;
```

| 点 | 説明 |
| --- | --- |
| **`fog.a` ＝ 透過率** | **シーンの色にかける** |
| **`fog.rgb` ＝ 散乱光** | **足す** |
| **三線形補間** | **froxel の粗さを滑らかにする** |
| **半透明** | **半透明の物もピクセル シェーダー内で同じ式を適用** |

## よくあるミス

??? failure "積分の結果が、手前の物にも霧がかかる"
    **物体の深度**で**積分の位置を引く**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **奥から累積して、深度で引いて合成**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [ボリューメトリック フォグ](index.md)
- [光の注入](injection.md)
- [時間蓄積](temporal.md)
