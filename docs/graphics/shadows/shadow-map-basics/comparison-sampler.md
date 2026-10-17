---
title: Comparison Samplers
tags:
  - 描画
---

# Comparison Samplers

**シャドウ マップが描けたら、画面の各点で「光から見た深度」と「マップの深度」を比べます**。**この比較を、GPU の比較サンプラーに任せる**と、**ハードウェア PCF（2×2 の補間）**も**同時に**得られます。このページでは、**比較の手順・比較サンプラーの設定・ハードウェア PCF の効果**を説明します。

!!! tip "ポイント"
    - **画面の点を光の空間へ変換**し、**マップの深度と比べる**。**奥なら影**。
    - **比較サンプラー**（`SampleCmp`）は、**比較をハードウェアに任せる**。
    - **線形フィルタ ＋ 比較**で、**2×2 のハードウェア PCF**になる。
    - **範囲外（マップの外）は、光が当たる扱い**にする（**境界色・クランプ**）。

## ③〜⑤ 比較
**ワールド位置**を**光のクリップ空間**に変換し、**シャドウ マップの座標と深度**を得ます。

```hlsl
float ShadowFactor(float3 world_pos) {
  float4 light_clip = mul(float4(world_pos, 1.0), light_view_projection);
  float3 ndc = light_clip.xyz / light_clip.w;

  float2 uv = ndc.xy * float2(0.5, -0.5) + 0.5;
  float depth = ndc.z - bias;

  if (any(uv < 0.0) || any(uv > 1.0) || ndc.z > 1.0) return 1.0;

  return shadow_tex.SampleCmpLevelZero(shadow_sampler, uv, depth);
}
```

コードの要点です。`ndc.xy * (0.5, −0.5) + 0.5` は、NDC（−1〜1、y は上向き）を、テクスチャ座標（0〜1、v は下向き）に変換します。`depth = ndc.z − bias` は、バイアスで自己影を防ぎます（[Shadow Bias](../bias/index.md)）。範囲外は、影なし（1）として扱うか、別の扱いにします。`SampleCmpLevelZero` は比較サンプラーで、比較した結果（0〜1）を 2×2 でバイリニア補間します。

### 比較サンプラー

**比較サンプラー**は、**ハードウェアが「保存された深度」と「参照値」を比べる**機能です。結果は**比較が真なら 1、偽なら 0**で**バイリニアで補間**されます（4 点の比較結果を混ぜる）。

```cpp
D3D11_SAMPLER_DESC sampler = {};
sampler.Filter = D3D11_FILTER_COMPARISON_MIN_MAG_LINEAR_MIP_POINT;
sampler.AddressU = sampler.AddressV = sampler.AddressW = D3D11_TEXTURE_ADDRESS_BORDER;
sampler.BorderColor[0] = sampler.BorderColor[1] = sampler.BorderColor[2] = sampler.BorderColor[3] = 1.0f;
sampler.ComparisonFunc = D3D11_COMPARISON_LESS_EQUAL;
device->CreateSamplerState(&sampler, &shadow_sampler);
```

サンプラー設定の意味です。`COMPARISON_..._LINEAR` は、4 点の比較結果を線形補間するもので、これが最も簡単な PCF になります。`ComparisonFunc = LESS_EQUAL` は、参照値が保存された深度以下なら 1（光が当たる）を返します。アドレス モードを BORDER、色を 1.0 にすると、シャドウ マップの外は影なし（1）になります。

!!! note "標準 Z のとき"
    標準の Z（near → 0、far → 1）では**遠いほど深度が大きい**ので、`LESS_EQUAL` を使います。**reverse-Z** のときは、`GREATER_EQUAL` です（[投影](../../../3d/projection.md)）。

## よくあるミス

??? failure "比較サンプラーなのに、通常のサンプラーで読んで、おかしい"
    **`SamplerComparisonState` を使い、`SampleCmp` で読む**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **光の空間の深度とマップの深度を比べる**
    - [x] **比較サンプラーで、ハードウェア PCF も得られる**

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [Shadow Map Basics](index.md)
- [Rendering Depth](render-depth.md)
- [PCF](../pcf.md)
