---
title: Minimal Code
tags:
  - 描画
---

# Minimal Code

**ここまでの手順を、最小のコードでつなげて見ます**。**1 本の平行光（太陽）**に対する**シャドウ マップの全体の流れ**です。**実際の製品では、バイアス・フィルタ・カスケードを足します**。このページでは、**全体のコードの流れ**を示します。

!!! tip "ポイント"
    - **全体 ＝ 光の行列 → 深度パス → 比較（ライティング）**。
    - **最小版は、バイアス・フィルタなし**。**これに、バイアスと PCF を足して実用に**。

## 全体のコード（最小）
```hlsl
Texture2D<float> shadow_tex : register(t5);
SamplerComparisonState shadow_sampler : register(s5);

cbuffer ShadowConstant : register(b3) {
  row_major float4x4 light_view_projection;
  float shadow_bias;
}

float3 Shade(float3 world_pos, float3 N, float3 L, float3 albedo, float3 light_color) {
  float shadow = ShadowFactor(world_pos);
  return albedo * light_color * saturate(dot(N, L)) * shadow;
}
```

## 最小の、シャドウ マップ（全体の流れ）

ここまでの、ページの、内容を、**1 つの、流れ**に、まとめます。**太陽（平行光源）**の、**1 枚の、シャドウ マップ**です。座標系は、右手系・Y 上、反時計回りが表です。

### ① リソースを、作る（起動時）

```cpp
// シャドウ マップ（2048×2048）、DSV、SRV、比較サンプラー、ラスタライザー ステート。
CreateShadowMap(device, 2048, &shadow_tex, &shadow_dsv, &shadow_srv);   // Rendering Depth のコード

D3D11_SAMPLER_DESC sd = {};
sd.Filter = D3D11_FILTER_COMPARISON_MIN_MAG_LINEAR_MIP_POINT;
sd.AddressU = sd.AddressV = sd.AddressW = D3D11_TEXTURE_ADDRESS_BORDER;
sd.BorderColor[0] = sd.BorderColor[1] = sd.BorderColor[2] = sd.BorderColor[3] = 1.0f;
sd.ComparisonFunc = D3D11_COMPARISON_LESS_EQUAL;
sd.MaxLOD = D3D11_FLOAT32_MAX;
device->CreateSamplerState(&sd, &shadow_sampler);

// シャドウ パス用: ハードウェアのバイアス（Constant Bias / Slope-Scale Bias）。
D3D11_RASTERIZER_DESC rs = {};
rs.FillMode = D3D11_FILL_SOLID;
rs.CullMode = D3D11_CULL_BACK;
rs.FrontCounterClockwise = TRUE;
rs.DepthBias = 1000;                          // 24 ビット深度なら、この値 × 最小の深度の刻み
rs.SlopeScaledDepthBias = 1.5f;
rs.DepthBiasClamp = 0.01f;
rs.DepthClipEnable = TRUE;
device->CreateRasterizerState(&rs, &shadow_rs);
```

### ② 毎フレーム：シャドウ パス

```cpp
// 光の行列を作る（Light Matrix）。
Matrix light_view = Matrix::CreateLookAt(eye, center, up);
Matrix light_proj = Matrix::CreateOrthographicOffCenter(-r, r, -r, r, 0.0f, 2.0f * r);
Matrix shadow_matrix = light_view * light_proj * ndc_to_uv;

// 深度だけを描く。
context->OMSetRenderTargets(0, nullptr, shadow_dsv.Get());
context->ClearDepthStencilView(shadow_dsv.Get(), D3D11_CLEAR_DEPTH, 1.0f, 0);
context->RSSetViewports(1, &shadow_viewport);
context->RSSetState(shadow_rs.Get());
context->VSSetShader(shadow_vs.Get(), nullptr, 0);
context->PSSetShader(nullptr, nullptr, 0);
UpdateLightCB(light_view * light_proj);
DrawShadowCasters();
```

### ③ 毎フレーム：メイン パス

```cpp
// メインの描画: シャドウ マップを SRV として読む（DSV としては、外す）。
context->OMSetRenderTargets(1, scene_rtv.GetAddressOf(), scene_dsv.Get());   // シャドウ DSV は、外れる
context->RSSetViewports(1, &main_viewport);
context->RSSetState(main_rs.Get());
context->PSSetShaderResources(5, 1, shadow_srv.GetAddressOf());
context->PSSetSamplers(5, 1, shadow_sampler.GetAddressOf());
UpdateShadowCB(shadow_matrix);
DrawScene();
```

**同じテクスチャを、DSV と SRV に、同時にバインドしない**ことに、注意します。メインの、`OMSetRenderTargets` で、シャドウ DSV が、**外れる**ので、**SRV として、読めます**。

### ④ シェーダー

```hlsl
// メイン パスの、ピクセル シェーダー（抜粋）。
cbuffer ShadowCB : register(b2) { float4x4 g_shadow_matrix; };
Texture2D<float> g_shadow_map : register(t5);
SamplerComparisonState g_shadow_sampler : register(s5);

float ShadowFactor(float3 world_pos) {
  float4 p = mul(float4(world_pos, 1.0), g_shadow_matrix);
  float3 coord = p.xyz / p.w;                                         // xy = UV、z = 深度
  if (any(coord.xy < 0.0) || any(coord.xy > 1.0) || coord.z > 1.0) return 1.0;
  return g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, coord.xy, coord.z);
}

float4 main(PSInput input) : SV_Target {
  float3 N = normalize(input.world_normal);
  float n_dot_l = saturate(dot(N, -g_light_dir));
  float shadow = ShadowFactor(input.world_position);
  float3 diffuse = g_albedo * g_light_color * n_dot_l * shadow;      // 影の中は、直接光が、0
  float3 ambient = g_albedo * g_ambient;                              // 環境光は、影に関係なく残る
  return float4(diffuse + ambient, 1.0);
}
```

## 動かない、ときの、点検

| 症状 | 見るところ |
| --- | --- |
| 影が、**全く出ない** | シャドウ パスで、物が、描かれているか（PIX / RenderDoc で、シャドウ マップの内容を見る）。光の行列が、正しいか |
| 影が、**上下逆** | NDC → UV の変換で、`y` を反転したか（`ndc.y * -0.5 + 0.5`） |
| 全体が、**縞模様**（シャドウ アクネ） | バイアスが、足りない（[Shadow Bias](../bias/index.md)） |
| 影が、物から、**浮いている** | バイアスが、大きすぎる（ピーター パンニング） |
| 影が、**ずれている** | 光の行列が、シャドウ パスと、メイン パスで、**同じ**か。**カメラの位置を、使っていないか** |
| 影が、**常に、真っ暗** | 比較関数の向き（reversed-Z）。範囲外の、境界色 |
| 影の端が、**ギザギザ** | 解像度を上げる、PCF（[PCF](../pcf.md)） |
| 地形の、**遠くで**、影が、無い | シャドウ マップの、範囲（`radius`）が、足りない。カスケード（[CSM](../cascaded.md)） |

デバッグには、**シャドウ マップを、画面に、表示**するのが、最も、効果的です。深度を、白黒で、画面の隅に、描きます。

```hlsl
// デバッグ表示: シャドウ マップの深度を、グレースケールで、画面に表示する。
float d = g_shadow_map.Load(int3(pos.xy, 0));
return float4(d.xxx, 1.0);
```

## よくあるミス

??? failure "最小のコードのまま製品に使って、アクネ・ジャギーが出る"
    **バイアス（[Shadow Bias](../bias/index.md)）とフィルタ（[PCF](../pcf.md)）を足す**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **最小のコードで、全体の流れを確認**
    - [x] **実用にはバイアスとフィルタが必須**

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces", SIGGRAPH 1978（シャドウ マップの原典）
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"（Direct3D 11 のドキュメント。バイアス、平行光源、PCF）
- Microsoft Learn, "D3D11_RASTERIZER_DESC"（`DepthBias`、`SlopeScaledDepthBias`、`DepthBiasClamp`）
- Microsoft Learn, "D3D11_SAMPLER_DESC"（`D3D11_FILTER_COMPARISON_*`、`ComparisonFunc`）

## 関連ページ

- [Shadow Map Basics](index.md)
- [Shadow Bias](../bias/index.md)
- [PCF](../pcf.md)
