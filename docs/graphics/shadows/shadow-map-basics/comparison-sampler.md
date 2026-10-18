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

| 点 | 説明 |
| --- | --- |
| **`ndc.xy * (0.5, −0.5) + 0.5`** | NDC（−1〜1、y は上向き）を、テクスチャ座標（0〜1、v は下向き）に |
| **`depth = ndc.z − bias`** | **バイアス**で自己影を防ぐ（[Shadow Bias](../bias/index.md)） |
| **範囲外** | シャドウ マップの外は、**影なし**（1）として扱う（または別の扱い） |
| **`SampleCmpLevelZero`** | **比較サンプラー**。**比較して、結果（0〜1）を、2×2 でバイリニア補間** |

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

## 比較サンプラーとは

影の判定は、**「シャドウ マップの深度」と、「画素の、光からの深度」を、比較**する作業です。この比較を、**ハードウェアが、やってくれる**のが、**比較サンプラー**です。**さらに**、**4 つの隣の画素**で、比較して、**結果を、バイリニア補間**してくれる（**2×2 の PCF が、ただで、できる**）ため、**シャドウ マップの、読み取りは、比較サンプラー**を使うのが、定番です。

## 比較サンプラーの、作り方

```cpp
D3D11_SAMPLER_DESC desc = {};
desc.Filter = D3D11_FILTER_COMPARISON_MIN_MAG_LINEAR_MIP_POINT;   // 比較 + 線形補間（2×2 PCF）
desc.AddressU = D3D11_TEXTURE_ADDRESS_BORDER;                     // 範囲外は、境界色
desc.AddressV = D3D11_TEXTURE_ADDRESS_BORDER;
desc.AddressW = D3D11_TEXTURE_ADDRESS_BORDER;
desc.BorderColor[0] = 1.0f;                                       // 範囲外の深度 = 1.0（最も遠い）→ 影なし
desc.BorderColor[1] = 1.0f;
desc.BorderColor[2] = 1.0f;
desc.BorderColor[3] = 1.0f;
desc.ComparisonFunc = D3D11_COMPARISON_LESS_EQUAL;                // 画素の深度 <= 保存された深度 → 光が当たる
desc.MaxLOD = D3D11_FLOAT32_MAX;
device->CreateSamplerState(&desc, &shadow_sampler);
```

| 設定 | 内容 |
| --- | --- |
| `Filter` | `COMPARISON_` で始まるものを、選ぶ。`MIN_MAG_LINEAR_MIP_POINT` なら、**比較した結果を、バイリニアで、補間**（影の縁が、なめらか）。`MIN_MAG_MIP_POINT` なら、補間なし（硬い縁） |
| `ComparisonFunc` | `LESS_EQUAL`：**参照値（画素の深度）が、テクスチャの値**以下なら、**1**（光が当たる）。**通常の、深度**（小さいほど、近い）で、使う |
| `AddressU/V` | `BORDER`：範囲外は、`BorderColor`。**1.0**にすると、範囲外は、**影にならない** |

## シェーダーでの、使い方

比較サンプラーは、HLSL では、**`SamplerComparisonState`** 型で、受け、**`SampleCmp`** または、**`SampleCmpLevelZero`** で、読みます。

```hlsl
Texture2D<float> g_shadow_map : register(t5);
SamplerComparisonState g_shadow_sampler : register(s5);

// 戻り値: 0（影の中）〜 1（光が当たる）。2×2 の結果が、補間されて、0〜1 の中間値になる。
float lit = g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, shadow_uv, shadow_depth);
```

| 関数 | 内容 |
| --- | --- |
| `SampleCmp` | **ミップ レベルを、自動で選ぶ**（画面の微分を使う）。分岐の中では、使えない（微分が、不定になる） |
| `SampleCmpLevelZero` | **ミップ 0 を、使う**。**分岐の中でも、使える**。**シャドウ マップは、ミップを持たない**ので、**これが標準** |

## 比較の、意味

```text
SampleCmpLevelZero(map, uv, ref):
   mapの、(uv の周りの 4 画素)  それぞれについて
      ref <= map値  なら 1、そうでなければ 0
   その 4 つの結果を、uv の小数部で、バイリニア補間
```

**重要**：**深度を、補間してから、比較**するのではなく、**比較してから、補間**します。**深度を、先に補間**すると、**遮蔽物の、縁**で、**存在しない、中間の深度**が、できて、**間違った影**になります。**比較してから、補間**するのが、**PCF の、正しい手順**で、ハードウェアが、**それを行います**（[PCF](../pcf.md)）。

### 手動で、比較する場合（比較サンプラーが、使えない）

```hlsl
// 通常のサンプラーで、深度を、読んで、手で比較する（補間なし。ハードの PCF は、無い）。
float stored = g_shadow_map.SampleLevel(g_point_clamp, shadow_uv, 0);
float lit = (shadow_depth <= stored) ? 1.0 : 0.0;
```

比較サンプラーが、**使えない場面**（VSM や、ESM のように、**深度そのものを、使う**場合、**深度の、別の形式**）では、この方法に、なります（[VSM, ESM and MSM](../vsm/index.md)）。

## 使うべき理由

| | 手動の比較 | 比較サンプラー |
| --- | --- | --- |
| 速さ | 4 回読む場合は、**4 回の、テクスチャ読み込み** | **ハードウェアが、1 回**で、2×2 を、処理 |
| 縁のなめらかさ | 自分で、実装 | **標準で、2×2 の、バイリニア PCF** |
| コード | 長い | **1 行** |

## 注意点

| 項目 | 内容 |
| --- | --- |
| 深度の向き | **reversed-Z**（遠いほど、小さい）を、使っているなら、`ComparisonFunc` を、`GREATER_EQUAL` にする |
| 形式 | シャドウ マップの、SRV は、`R32_FLOAT`（または `R24_UNORM_X8_TYPELESS`）。比較サンプラーで、読める |
| ミップ | シャドウ マップは、**ミップを、作らない**（深度の、平均は、意味がない） |
| テクスチャ配列 | カスケードを、**配列**にするなら、`Texture2DArray` と、`float3(uv, slice)` で読む |

## よくあるミス

??? failure "比較サンプラーなのに、通常のサンプラーで読んで、おかしい"
    **`SamplerComparisonState` を使い、`SampleCmp` で読む**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **光の空間の深度とマップの深度を比べる**
    - [x] **比較サンプラーで、ハードウェア PCF も得られる**

## 参考

- Reeves, Salesin, Cook, "Rendering Antialiased Shadows with Depth Maps", SIGGRAPH 1987（PCF の原典）
- Microsoft Learn, "D3D11_SAMPLER_DESC"（`D3D11_FILTER_COMPARISON_*`、`ComparisonFunc`）
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"（Direct3D 11 のドキュメント。バイアス、平行光源、PCF）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）

## 関連ページ

- [Shadow Map Basics](index.md)
- [Rendering Depth](render-depth.md)
- [PCF](../pcf.md)
