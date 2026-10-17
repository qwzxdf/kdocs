---
title: 事前フィルタ（Split-Sum）
tags:
  - 描画
---

# 事前フィルタ（Split-Sum）

**粗い面の反射は、周囲の広い範囲の光の平均**になります。**これを、毎回ピクセルごとに計算するのは重すぎる**ので、**粗さごとに、キューブマップを事前にぼかして、ミップに入れておきます**。**Split-Sum 近似**と呼ばれる、**ほとんどのエンジンで使われる方式**です。このページでは、**事前フィルタの考え方とミップの使い方**を説明します。

!!! tip "ポイント"
    - **粗さ ＝ ミップ レベル**（粗いほど、ぼけたミップ）。
    - **事前に、GGX 分布で重み付けして、ぼかす**。
    - **もう 1 つの項（BRDF の積分）は、LUT に入れておく**。
    - **実行時は、ミップ 1 回 ＋ LUT 1 回の読み出しだけ**。

## 粗さへの対応：事前フィルタ（Split-Sum）
粗い面の反射は、**BRDF の山の範囲の景色を、重み付きで平均**したものでした（[反射](../index.md)）。これを**表面ごとに実行時に計算するのは重い**ので、**事前計算**します。Epic の Karis が提案した **Split-Sum 近似**が、標準になっています。

### 式を 2 つに分ける

<div class="formula">∫ L_i · f_spec · cosθ dω　≈　( ∫ L_i · D · cosθ dω ) × ( ∫ f_spec · cosθ dω )</div>

| 項 | 内容 | 事前計算 |
| --- | --- | --- |
| **第 1 項：事前フィルタした環境マップ** | **粗さごとに環境をぼかした**キューブマップ（ミップ） | プローブごとに（キューブマップのミップとして） |
| <strong>第 2 項：BRDF の積分（スケールとバイアス）</strong> | `F0 · A + B`（A・B は、`n·v` と粗さから引く） | **BRDF LUT**（2D テクスチャ）を、1 つだけ事前計算 |

詳しい導出は、[PBR](../../../3d/pbr.md)の IBL を参照してください。

### ミップ レベルの選び方

**粗さが大きいほど、ぼけた（高いミップの）レベル**を読みます。

```hlsl
float3 SpecularIBL(float3 N, float3 V, float3 albedo, float metallic, float roughness) {
  float3 R = reflect(-V, N);
  float mip = roughness * (max_mip - 1.0);
  float3 prefiltered = env_cube.SampleLevel(linear_sampler, R, mip).rgb;

  float n_dot_v = saturate(dot(N, V));
  float2 brdf = brdf_lut.Sample(linear_sampler, float2(n_dot_v, roughness)).rg;

  float3 F0 = lerp(0.04, albedo, metallic);
  return prefiltered * (F0 * brdf.x + brdf.y);
}
```

| 点 | 説明 |
| --- | --- |
| **`mip = roughness × (最大ミップ)`** | 粗さ 0 でミップ 0（くっきり）、粗さ 1 で最大のミップ（ぼんやり） |
| **BRDF LUT** | `n·v` と粗さを入力にした、2 値（スケール・バイアス）。**プロジェクト全体で 1 枚** |
| **`F0`** | 非金属は約 0.04、金属はアルベド色 |
| **ミップ間はトリリニア補間** | 滑らかに粗さが変わる |

### 事前フィルタの作り方

**各ミップ**は**その粗さの GGX 分布**で、**環境マップを重要度サンプリング**して作ります。

| ミップ | 粗さ | 作り方 |
| --- | --- | --- |
| **0** | 0 | 元のキューブマップ |
| **1〜N** | 粗さを段階的に上げる | **GGX の重要度サンプリング**で、各テクセルを再計算（コンピュート・ピクセルシェーダー） |

**重要度サンプリング**は、**分布の山の部分から多くサンプル**する手法で、**サンプル数を減らせます**（[確率的 SSR](../ssr-stochastic.md)で詳しく）。

## よくあるミス

??? failure "粗い面の反射が、鏡のようにくっきり"
    **粗さに応じたミップ**を選ぶ。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **粗さごとに、事前にぼかす**
    - [x] **実行時は、ミップと LUT を読むだけ**

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [反射プローブ](index.md)
- [視差補正](parallax.md)
- [確率的 SSR](../ssr-stochastic.md)
