---
title: Steps 3 and 4: Integration and Application
tags:
  - 描画
---

# Steps 3 and 4: Integration and Application

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

積分のコードの要点です。スライスの厚みは奥ほど大きいので、厚みを考慮して積分を厳密にします。区間内の透過率を指数で厳密に扱うので（解析的な積分）、粗いステップでも安定します。結果は 3D テクスチャに保存し、各スライスまでの累積を適用時に、深度に応じた位置で引きます。1 つのスレッドが奥まで受け持ち、画面方向は並列、奥行き方向は順次処理です。

## ④ 適用
**不透明のシーンの色に積分結果を合成します**。**ピクセルの深度から、対応するスライスを求めて、3D テクスチャを引きます**。

```hlsl
float depth = LinearizeDepth(depth_texture.Sample(point_clamp, uv).r);
float slice = DepthToSlice(depth, kNear, kFar, kSliceCount);
float3 froxel_uvw = float3(uv, slice / kSliceCount);
float4 fog = integrated_volume.SampleLevel(linear_clamp, froxel_uvw, 0);

float3 final_color = scene_color * fog.a + fog.rgb;
```

適用のコードの要点です。`fog.a` は透過率で、シーンの色に掛けます。`fog.rgb` は散乱光で、足します。三線形補間で、froxel の粗さを滑らかにします。半透明の物体も、ピクセル シェーダーの中で同じ式を適用します。

### 積分式の導出

累積の式が、なぜこの形なのかを確認します。1 つのスライスの内側で、散乱光 S（単位長さあたりに散乱される光）と消散 σ が一定だとします。スライスの手前の端から距離 x の位置で散乱された光は、スライスの手前の端に届くまでに `exp(−σ x)` の割合に弱まります。スライス全体で足し合わせると、次の積分になります。

<div class="formula">∫₀^Δz S · exp(−σ x) dx = S · (1 − exp(−σ Δz)) / σ</div>

コードの `(scattering - scattering * slice_transmittance) / extinction` が、まさにこれです。この<strong>区間内の解析積分</strong>がポイントです。単純に `scattering * thickness` を足すだけでは、密度が高いときにエネルギーが保存されず、濃い霧で光が過剰になります（特に、スライスが厚い遠方）。解析積分なら、どんなに濃くても、光の量が上限（S / σ）を超えません。この定式化は、Hillaire の Frostbite の発表で広まりました。

スライス全体を手前から奥へ回し、それまでの透過率 `transmittance` を、現在のスライスの寄与に掛けてから足します。手前の濃い霧は、奥の光を隠すので、奥の寄与が手前の透過率で減衰します。この累積を、スライスごとに保存すれば、適用のときは、画素の深度に対応するスライスの値を 1 回引くだけで、「カメラからその距離までの全フォグ」が得られます。

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

- [Volumetric Fog](index.md)
- [光の注入](injection.md)
- [時間蓄積](temporal.md)
