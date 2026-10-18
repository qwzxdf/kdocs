---
title: Step 1: Density
tags:
  - 描画
---

# Step 1: Density

**最初の段階で、各 froxel の霧の濃さ（密度）を決めます**。**一様な霧・高さフォグ・ノイズの雲のような濃淡**を**組み合わせます**。このページでは、**密度の決め方**を説明します。

!!! tip "ポイント"
    - **基本の密度 ＋ 高さによる減衰**。
    - **ノイズで、濃淡を付ける**（動かして、流れを出す）。
    - **ローカルなボリューム（部屋の霧）も足せる**。
    - **密度は、散乱係数と吸収係数に分ける**。

## ① 密度
**霧の濃さを各 froxel に書きます**。**複数の要素を足し合わせます**。

| 要素 | 内容 |
| --- | --- |
| **全体の霧** | **一様な基準の密度**（`global_density`） |
| **高さフォグ** | **高さで指数的に減る**（[Aerial Perspective and Fog](../aerial-fog/index.md)） |
| **ノイズ** | **3D ノイズで濃淡**を付け、**風で流す** |
| **ローカルな霧のボリューム** | **箱・球で局所的に濃くする**（部屋の煙、洞窟） |
| **パーティクル** | **煙のパーティクルが密度を足す** |

```hlsl
float3 world_position = FroxelToWorld(id, slice_count);
float density = global_density;
density += height_density * exp(-height_falloff * (world_position.y - fog_base));
density *= 1.0 + noise_strength * Noise3D(world_position * noise_scale + wind * time);
density = max(density, 0.0);
```

### 密度から散乱と消散へ

密度は、そのまま光の計算に使うのではなく、物理的な係数に変換します。媒質を光が通るときに、光を弱める要因は 2 つあります。<strong>散乱</strong>は、光が別の方向に飛ばされることで、霧が白く見える理由です。<strong>吸収</strong>は、光が熱などに変わって消えることで、煙が暗く見える理由です。この 2 つを合わせた「光が弱まる量」を<strong>消散</strong>（extinction）と呼びます。

<div class="formula">消散係数 σ_t = 散乱係数 σ_s + 吸収係数 σ_a</div>

霧（水滴）はほとんど吸収せず、散乱が主です。煙は吸収も多く、暗くなります。密度に散乱の色（アルベド）を掛けて σ_s を、吸収の色を掛けて σ_a を求めます。たとえば、白い霧なら、散乱の色が (1,1,1)、吸収が 0 です。黒い煙なら、散乱を小さく、吸収を大きくします。

この分け方のおかげで、同じ「密度」でも、霧と煙で見た目を変えられます。密度は「どれだけ濃いか」、散乱と吸収のアルベドは「どんな物質か」を表す、2 つの独立なパラメータです。

### ノイズの使い方

ノイズは、3D ノイズ テクスチャ（Perlin や Worley）を、ワールド座標でサンプルします。座標に風の速度 × 時間を足すと、霧が風で流れます。複数のスケールのノイズを重ねると（フラクタル）、大きな塊と細かい揺らぎを持つ、自然な濃淡になります。ただし、froxel の解像度が粗いので、細かいノイズは時間蓄積でないとちらつきやすいです（[Temporal Accumulation](temporal.md)）。

## よくあるミス

??? failure "霧が一様で、単調"
    **ノイズ**で**濃淡**を付ける。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **基本の密度に、ノイズと高さを組み合わせる**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Volumetric Fog](index.md)
- [Froxels](froxel.md)
- [Step 2: Light Injection](injection.md)
