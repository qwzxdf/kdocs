---
title: Step 1: Density
tags:
  - 描画
---

# Step 1: Density

<strong>最初の段階で各 froxel の霧の濃さ（密度）を決めます</strong>。一様な霧・高さフォグ・ノイズの雲のような濃淡を組み合わせます。このページでは密度の決め方を説明します。

!!! tip "ポイント"
    - 基本の密度 ＋ 高さによる減衰。
    - ノイズで濃淡を付ける（動かして、流れを出す）。
    - ローカルなボリューム（部屋の霧）も足せる。
    - 密度は散乱係数と吸収係数に分ける。

!!! info "このページを読む前に"
    - [Volumetric Fog](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## ① 密度
<strong>霧の濃さを各 froxel に書きます</strong>。複数の要素を足し合わせます。

| 要素 | 内容 |
| --- | --- |
| 全体の霧 | 一様な基準の密度（`global_density`） |
| 高さフォグ | 高さで指数的に減る（[Aerial Perspective and Fog](../aerial-fog/index.md)） |
| ノイズ | 3D ノイズで濃淡を付け、風で流す |
| ローカルな霧のボリューム | 箱・球で局所的に濃くする（部屋の煙、洞窟） |
| パーティクル | 煙のパーティクルが密度を足す |

```hlsl
float3 world_position = FroxelToWorld(id, slice_count);
float density = global_density;
density += height_density * exp(-height_falloff * (world_position.y - fog_base));
density *= 1.0 + noise_strength * Noise3D(world_position * noise_scale + wind * time);
density = max(density, 0.0);
```

### 密度から散乱と消散へ

密度はそのまま光の計算に使うのではなく、物理的な係数に変換します。媒質を光が通るときに光を弱める要因は 2 つあります。散乱は光が別の方向に飛ばされることで、霧が白く見える理由です。吸収は光が熱などに変わって消えることで、煙が暗く見える理由です。この 2 つを合わせた「光が弱まる量」を消散（extinction）と呼びます。

<div class="formula">消散係数 σ_t = 散乱係数 σ_s + 吸収係数 σ_a</div>

霧（水滴）はほとんど吸収せず、散乱が主です。煙は吸収も多く暗くなります。密度に散乱の色（アルベド）を掛けて σ_s を吸収の色を掛けて σ_a を求めます。たとえば、白い霧なら散乱の色が (1,1,1)、吸収が 0 です。黒い煙なら散乱を小さく吸収を大きくします。

この分け方のおかげで同じ「密度」でも、霧と煙で見た目を変えられます。密度は「どれだけ濃いか」、散乱と吸収のアルベドは「どんな物質か」を表す、2 つの独立なパラメータです。

### ノイズの使い方

ノイズは 3D ノイズ テクスチャ（Perlin や Worley）をワールド座標でサンプルします。座標に風の速度 × 時間を足すと、霧が風で流れます。複数のスケールのノイズを重ねると（フラクタル）、大きな塊と細かい揺らぎを持つ、自然な濃淡になります。ただし、froxel の解像度が粗いので、細かいノイズは時間蓄積でないとちらつきやすいです（[Temporal Accumulation](temporal.md)）。

## ステップ 1：各セルの霧の濃さ

<strong>ボリューム フォグ</strong>の最初の段階は、froxel の各セルの霧の密度（消散係数、`σ_t`）を決めることです。密度が高いセルほど光をよく散らし、遮ります。

## 密度の材料

<strong>複数の材料を足し合わせて</strong>、最終的な密度を作ります。

| 材料 | 内容 | 例 |
| --- | --- | --- |
| 一様な密度 | 空間全体に一定の、薄い霧 | 空気の霞 |
| 高さによる密度 | 地面に近いほど濃い（[Height Fog](../aerial-fog/height-fog.md)） | 谷の霧、朝霧 |
| ノイズ | 3D ノイズで霧にむらを与える。時間で動かす | 渦を巻く霧 |
| 局所的な霧のボリューム | 箱や、球の中だけ濃い霧 | 沼、洞窟の入口、魔法の霧 |
| パーティクル | 煙や爆発が霧の密度を足す | 煙幕 |

## 計算シェーダーで書く

```hlsl
RWTexture3D<float4> g_froxel_scatter : register(u0);       // xyz = 散乱係数 × アルベド、w = 消散係数（密度）

[numthreads(8, 8, 4)]
void DensityCS(uint3 id : SV_DispatchThreadID) {
  float3 world = FroxelToWorld(float3(id) + JitterOffset());              // セルの、ワールド位置（ジッター付き。下記）
```

まず、<strong>セルの中心</strong>のワールド位置を求めます（[Froxels](froxel.md)）。`JitterOffset()` は フレームごとのわずかな、ずらしで時間方向の平均で縞を消すために使います（[Temporal Accumulation](temporal.md)）。

```hlsl
  // ① 一様な密度 + 高さによる密度。
  float h = world.y - g_fog_base_height;
  float density = g_uniform_density + g_height_density * exp(-g_height_falloff * max(h, 0.0));
```

基本の霧です。一様な部分と高さで指数的に薄くなる部分を足します。

```hlsl
  // ② ノイズで、むらを与える。3D ノイズを風で、流す。
  float3 noise_pos = world * g_noise_scale + g_wind_direction * g_time * g_wind_speed;
  float noise = g_noise_3d.SampleLevel(g_linear_wrap, noise_pos, 0).r;           // 0〜1
  density *= lerp(1.0, noise * 2.0, g_noise_strength);                            // ノイズで、濃さを変える
```

3D ノイズ（Perlin、Worley）で霧の濃さにむらを与え風で流すと霧が動いて見えます。ノイズの値（平均 0.5）に 2 を掛けて平均を 1 にそろえ全体の濃さを変えず、むらだけを足します。

```hlsl
  // ③ 局所的な、霧のボリューム（箱）を足す。各ボリュームの、中だけ、密度を足す。
  for (uint i = 0; i < g_fog_volume_count; ++i) {
    FogVolume v = g_fog_volumes[i];
    float3 local = mul(float4(world, 1.0), v.world_to_local).xyz;                 // ボリュームの、ローカル座標（-0.5〜0.5 の箱）
    float inside = all(abs(local) < 0.5) ? 1.0 : 0.0;
    // 箱の縁をなめらかに（端で、密度が 0 に落ちる）
    float edge = saturate(min(min(0.5 - abs(local.x), 0.5 - abs(local.y)), 0.5 - abs(local.z)) / v.edge_softness);
    density += v.density * inside * edge;
  }
```

局所的な霧（沼、洞窟）は 箱（または球）の形の、ボリュームとして置きます。セルが箱の中にあれば密度を足し縁は、なめらかに薄くします。ボリュームをアーティストがレベルに置く（霧のボリューム アクター）ことで、場所ごとの霧を作れます。

```hlsl
  // 散乱係数と、吸収（アルベド）。霧は、ほぼ散乱だけ（アルベドが高い）。消散 = 散乱 + 吸収。
  float3 scattering = g_fog_albedo * density;              // 散乱係数（RGB）
  float extinction = density;                              // 消散係数（散乱 + 吸収）。アルベドが 1 なら、散乱と、同じ。
  g_froxel_scatter[id] = float4(scattering, extinction);
}
```

最後に、散乱係数（`σ_s`、光を曲げる）と 消散係数（`σ_t`、光を失う）を書き込みます。アルベド（散乱 / 消散）は、霧の色に相当し 1 に近いと白い霧、小さいと暗い煤けた霧になります。

## 単位とスケール

| 値 | 意味 | 例 |
| --- | --- | --- |
| 消散係数（1/m） | 1 m 進むと光が失われる割合 | 薄い霞 0.0005、霧 0.01、濃霧 0.05 |
| 視界の距離 | 約 `3 / 消散係数` | 0.01 → 約 300 m |

<strong>ゲームの空間のスケール</strong>に、合わせて 消散係数を決めます。視界が 300 m の霧は 0.01 程度です（[Fog Equations](../aerial-fog/fog-equation.md)）。

## 事前に決めるデータ

<strong>局所的な霧のボリューム</strong>は、CPU 側でリストにして、定数バッファ（または構造化バッファ）で、渡します。カメラの近くにあるボリュームだけを絞って渡すと、ループが短くなります。

```cpp
struct FogVolume {
  Matrix world_to_local;     // ワールド → ボリュームの、ローカル（箱が-0.5〜0.5 になる）
  float density;
  float edge_softness;
  float2 pad;
};
// カメラの視錐台と、交わるボリュームだけを集めて、GPU に渡す。
```

## よくあるミス

??? failure "霧が一様で単調"
    <strong>ノイズ</strong>で濃淡を付ける。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 基本の密度にノイズと高さを組み合わせる

## 参考

- Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Volumetric Fog](index.md)
- [Froxels](froxel.md)
- [Step 2: Light Injection](injection.md)
