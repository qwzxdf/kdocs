---
title: Comparison Samplers
tags:
  - 描画
---

# Comparison Samplers

<strong>シャドウ マップが描けたら、画面の各点で「光から見た深度」と「マップの深度」を比べます</strong>。この比較を GPU の比較サンプラーに任せると、ハードウェア PCF（2×2 の補間）も同時に得られます。このページでは比較の手順・比較サンプラーの設定・ハードウェア PCF の効果を説明します。

!!! tip "ポイント"
    - 画面の点を光の空間へ変換し、マップの深度と比べる。奥なら影。
    - 比較サンプラー（`SampleCmp`）は、比較をハードウェアに任せる。
    - 線形フィルタ ＋ 比較で、2×2 のハードウェア PCFになる。
    - 範囲外（マップの外）は、光が当たる扱いにする（境界色・クランプ）。

!!! info "このページを読む前に"
    - [Shadow Map Basics](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## ③〜⑤ 比較
<strong>ワールド位置</strong>を光のクリップ空間に変換し、シャドウ マップの座標と深度を得ます。

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
| `ndc.xy * (0.5, −0.5) + 0.5` | NDC（−1〜1、y は上向き）をテクスチャ座標（0〜1、v は下向き）に |
| `depth = ndc.z − bias` | バイアスで自己影を防ぐ（[Shadow Bias](../bias/index.md)） |
| 範囲外 | シャドウ マップの外は、影なし（1）として扱う（または別の扱い） |
| `SampleCmpLevelZero` | 比較サンプラー。比較して結果（0〜1）を 2×2 でバイリニア補間 |

### 比較サンプラー

比較サンプラーは ハードウェアが「保存された深度」と「参照値」を比べる機能です。結果は比較が真なら 1、偽なら 0でバイリニアで補間されます（4 点の比較結果を混ぜる）。

```cpp
D3D11_SAMPLER_DESC sampler = {};
sampler.Filter = D3D11_FILTER_COMPARISON_MIN_MAG_LINEAR_MIP_POINT;
sampler.AddressU = sampler.AddressV = sampler.AddressW = D3D11_TEXTURE_ADDRESS_BORDER;
sampler.BorderColor[0] = sampler.BorderColor[1] = sampler.BorderColor[2] = sampler.BorderColor[3] = 1.0f;
sampler.ComparisonFunc = D3D11_COMPARISON_LESS_EQUAL;
device->CreateSamplerState(&sampler, &shadow_sampler);
```

サンプラー設定の意味です。`COMPARISON_..._LINEAR` は 4 点の比較結果を線形補間するもので、これが最も簡単な PCF になります。`ComparisonFunc = LESS_EQUAL` は参照値が保存された深度以下なら 1（光が当たる）を返します。アドレス モードを BORDER、色を 1.0 にするとシャドウ マップの外は影なし（1）になります。

!!! note "標準 Z のとき"
    標準の Z（near → 0、far → 1）では遠いほど深度が大きいので、`LESS_EQUAL` を使います。reverse-Z のときは、`GREATER_EQUAL` です（[投影](../../../3d/projection.md)）。

## 比較サンプラーとは

影の判定は <strong>「シャドウ マップの深度」と、「画素の光からの深度」を比較</strong>する作業です。この比較を ハードウェアがやってくれるのが、比較サンプラーです。さらに、4 つの隣の画素で比較して結果を、バイリニア補間してくれる（2×2 の PCF がただで、できる）ためシャドウ マップの、読み取りは比較サンプラーを使うのが、定番です。

## 比較サンプラーの作り方

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
| `Filter` | `COMPARISON_` で始まるものを選ぶ。`MIN_MAG_LINEAR_MIP_POINT` なら比較した結果をバイリニアで、補間（影の縁がなめらか）。`MIN_MAG_MIP_POINT` なら補間なし（硬い縁） |
| `ComparisonFunc` | `LESS_EQUAL`：参照値（画素の深度）が、テクスチャの値以下なら 1（光が当たる）。通常の、深度（小さいほど近い）で使う |
| `AddressU/V` | `BORDER`：範囲外は `BorderColor`。1.0にすると範囲外は影にならない |

## シェーダーでの使い方

比較サンプラーは HLSL では、<strong>`SamplerComparisonState`</strong> 型で受け `SampleCmp` または `SampleCmpLevelZero` で、読みます。

```hlsl
Texture2D<float> g_shadow_map : register(t5);
SamplerComparisonState g_shadow_sampler : register(s5);

// 戻り値: 0（影の中）〜 1（光が当たる）。2×2 の結果が、補間されて、0〜1 の中間値になる。
float lit = g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, shadow_uv, shadow_depth);
```

| 関数 | 内容 |
| --- | --- |
| `SampleCmp` | ミップ レベルを、自動で選ぶ（画面の微分を使う）。分岐の中では使えない（微分が、不定になる） |
| `SampleCmpLevelZero` | ミップ 0 を使う。分岐の中でも使える。シャドウ マップはミップを持たないので、これが標準 |

## 比較の意味

```text
SampleCmpLevelZero(map, uv, ref):
   mapの、(uv の周りの 4 画素)  それぞれについて
      ref <= map値  なら 1、そうでなければ 0
   その 4 つの結果を、uv の小数部で、バイリニア補間
```

<strong>重要</strong>：深度を補間してから、比較するのではなく比較してから、補間します。深度を先に補間すると遮蔽物の縁で、存在しない中間の深度ができて、間違った影になります。比較してから補間するのが PCF の、正しい手順でハードウェアがそれを行います（[PCF](../pcf.md)）。

### 手動で比較する場合（比較サンプラーが、使えない）

```hlsl
// 通常のサンプラーで、深度を、読んで、手で比較する（補間なし。ハードの PCF は、無い）。
float stored = g_shadow_map.SampleLevel(g_point_clamp, shadow_uv, 0);
float lit = (shadow_depth <= stored) ? 1.0 : 0.0;
```

比較サンプラーが 使えない場面（VSM や、ESM のように 深度そのものを、使う場合、深度の別の形式）ではこの方法に、なります（[VSM, ESM and MSM](../vsm/index.md)）。

## 使うべき理由

| | 手動の比較 | 比較サンプラー |
| --- | --- | --- |
| 速さ | 4 回読む場合は、4 回のテクスチャ読み込み | ハードウェアが、1 回で 2×2 を処理 |
| 縁のなめらかさ | 自分で、実装 | 標準で 2×2 のバイリニア PCF |
| コード | 長い | 1 行 |

## 注意点

| 項目 | 内容 |
| --- | --- |
| 深度の向き | reversed-Z（遠いほど、小さい）を使っているなら `ComparisonFunc` を、`GREATER_EQUAL` にする |
| 形式 | シャドウ マップの、SRV は `R32_FLOAT`（または `R24_UNORM_X8_TYPELESS`）。比較サンプラーで読める |
| ミップ | シャドウ マップは、ミップを作らない（深度の平均は、意味がない） |
| テクスチャ配列 | カスケードを、配列にするなら `Texture2DArray` と `float3(uv, slice)` で読む |

## よくあるミス

??? failure "比較サンプラーなのに、通常のサンプラーで読んでおかしい"
    <strong>`SamplerComparisonState` を使い `SampleCmp` で読む</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 光の空間の深度とマップの深度を比べる
    - [x] 比較サンプラーで、ハードウェア PCF も得られる

## 参考

- Reeves, Salesin, Cook, "Rendering Antialiased Shadows with Depth Maps", SIGGRAPH 1987（PCF の原典）
- Microsoft Learn, "D3D11_SAMPLER_DESC"（`D3D11_FILTER_COMPARISON_*`、`ComparisonFunc`）
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"（Direct3D 11 のドキュメント。バイアス、平行光源、PCF）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）

## 関連ページ

- [Shadow Map Basics](index.md)
- [Rendering Depth](render-depth.md)
- [PCF](../pcf.md)
