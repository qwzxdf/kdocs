---
title: Step 1: Density
tags:
  - 描画
---

# Step 1: Density

ボリューム フォグの最初の仕事は「どこの霧がどれだけ濃いか」を格子の各セルに書き込むことです。一様な霞だけでは画面が単調になります。谷にたまる朝霧、風に流れるむら部屋の中の煙のような濃淡を作るには、複数の材料を足し合わせます。

<strong>各 froxel の霧の濃さ（密度）を一様な霧、高さによる減衰、ノイズ、局所的なボリュームの足し算で決めます</strong>。さらに、密度を散乱係数と消散係数に変換します。このページでは密度の材料、散乱と吸収の分け方、単位とスケール（透過率の数字つき）、froxel の積分の精度（実測つき）、計算シェーダーの完成形を説明します。

!!! tip "ポイント"
    - 基本の密度に高さによる指数の減衰、ノイズ、局所的なボリュームを足します。
    - 密度は散乱係数と吸収係数（合わせて消散係数）に分けます。霧は散乱が主で煙は吸収も多いです。
    - 消散係数は 1/メートルの単位です。視界の距離はおおよそ `3 / σ_t` です。
    - ノイズは風の速度 × 時間でずらして、流します。濃さの平均を 1 にそろえて、全体の濃さを変えません。
    - 局所的な霧（沼、洞窟）は箱の形のボリュームとして足します。縁をなめらかに薄くします。

!!! info "このページを読む前に"
    - [Volumetric Fog](index.md)（このセクション全体の地図と、読む順番）

## 密度の材料 {#materials}

霧の密度は複数の材料を足し合わせて作ります。

- 一様な密度は空間全体に一定の薄い霧です（空気の霞）。
- 高さによる密度は地面に近いほど濃い霧です。高さで指数的に減ります（谷の霧、朝霧。[Height Fog](../aerial-fog/height-fog.md)）。
- ノイズは 3D ノイズで霧にむらを与えます。時間で動かすと霧が渦を巻くように流れます。
- 局所的な霧のボリュームは箱や球の中だけ濃い霧です（沼、洞窟の入口、魔法の霧）。
- パーティクルは煙や爆発が、霧の密度を足します（煙幕）。

<svg class="fig flow" viewBox="0 0 720 240" role="img" aria-label="消散係数ごとの、100 m 先の透過率と視界の距離"><text x="14" y="22" class="fig-title">消散係数 σ_t と、100 m 先の透過率</text>
<line x1="60" y1="190" x2="690" y2="190" stroke="currentColor" stroke-width="1.5"/>
<g stroke-width="2"><rect x="120" y="50" width="100" height="140" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"/><rect x="290" y="123" width="100" height="67" fill="rgba(229,170,40,0.3)" stroke="#e5aa28"/><rect x="460" y="188" width="100" height="2" fill="rgba(229,72,77,0.4)" stroke="#e5484d"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="170" y="44">95 %</text><text x="340" y="117">37 %</text><text x="510" y="182">0.7 %</text>
<text x="170" y="210">σ_t = 0.0005（薄い霞）</text><text x="340" y="210">0.01（霧）</text><text x="510" y="210">0.05（濃霧）</text>
<text x="170" y="228">視界 約 6000 m</text><text x="340" y="228">約 300 m</text><text x="510" y="228">約 60 m</text></g></svg>



## 単位とスケール {#scale}

密度は物理的には消散係数 `σ_t`（1/m）です。光が媒質を距離 `d` だけ進んだとき残る割合（透過率）は、ベールの法則で `exp(−σ_t · d)` です。

視界の距離は透過率が `exp(−3) ≒ 5 %` になる距離で、`3 / σ_t` が目安です。

- 薄い霞は `σ_t = 0.0005`（1/m）で視界が約 6000 m です。100 m の透過率は 95 % です。
- 霧は `σ_t = 0.01` で視界が約 300 m です。100 m の透過率は 37 % です。
- 濃霧は `σ_t = 0.05` で視界が約 60 m です。100 m の透過率は 0.7 % で、ほぼ見えません。

ゲームの空間のスケールに合わせて、消散係数を決めます。視界が 300 m の霧は 0.01 程度です（[Fog Equations](../aerial-fog/fog-equation.md)）。

## 高さによる密度 {#height}

高さ `h` での密度を `σ(h) = σ₀ · exp(−k · h)` と置きます。`k` が減衰の強さで `k = 0.15`（1/m）なら約 4.6 m 上がるごとに密度が半分になります（`ln 2 / k`）。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="高さに対する密度の指数減衰。k = 0.15 で 4.6 m ごとに半分"><text x="14" y="22" class="fig-title">高さによる密度（k = 0.15）</text>
<line x1="70" y1="190" x2="680" y2="190" stroke="currentColor" stroke-width="1.5"/><line x1="70" y1="190" x2="70" y2="40" stroke="currentColor" stroke-width="1.5"/>
<text x="62" y="56" text-anchor="end" style="font-size:12px">σ₀</text><text x="62" y="194" text-anchor="end" style="font-size:12px">0</text>
<text x="680" y="212" text-anchor="end" style="font-size:12px">高さ h（メートル）0 〜 20</text>
<path d="M70.0,50.0 L85.0,60.1 L100.0,69.5 L115.0,78.2 L130.0,86.3 L145.0,93.8 L160.0,100.7 L175.0,107.2 L190.0,113.2 L205.0,118.7 L220.0,123.9 L235.0,128.6 L250.0,133.1 L265.0,137.2 L280.0,141.0 L295.0,144.5 L310.0,147.8 L325.0,150.9 L340.0,153.7 L355.0,156.3 L370.0,158.8 L385.0,161.0 L400.0,163.1 L415.0,165.1 L430.0,166.9 L445.0,168.5 L460.0,170.1 L475.0,171.5 L490.0,172.9 L505.0,174.1 L520.0,175.2 L535.0,176.3 L550.0,177.3 L565.0,178.2 L580.0,179.1 L595.0,179.9 L610.0,180.6 L625.0,181.3 L640.0,181.9 L655.0,182.5 L670.0,183.0" fill="none" stroke="#4c8bf5" stroke-width="3.5"/>
<line x1="70" y1="120" x2="217" y2="120" stroke="#94a3b8" stroke-dasharray="4 4"/><line x1="217" y1="120" x2="217" y2="190" stroke="#94a3b8" stroke-dasharray="4 4"/>
<text x="224" y="116" style="font-size:12px">半分 σ₀/2（h = 4.6 m）</text><text x="400" y="150" style="font-size:12px">h = 20 m で σ₀ × 0.05</text></svg>

カメラから視線に沿った光学的厚さ `τ` は、視線の仰角 `φ`、距離 `D` で次のとおりです。

<div class="formula">τ = σ₀ · exp(−k · h₀) · (1 − exp(−k · sin φ · D)) / (k · sin φ)</div>

froxel の積分がこの式にどれだけ近いかを測りました。`σ₀ = 0.02`、`k = 0.15`、カメラの高さ `h₀ = 5 m` で近い面 0.5 m、遠い面 300 m、スライスを指数的に分けて各スライスの中央で密度をサンプルして、距離 200 m までの `τ` を足しました。仰角 0° では式が 1.8895、froxel（64 スライス）が 1.8847 で、誤差は 0.3 % でした。仰角 3° では 0.9531 に対して 0.9482（0.5 %）、10° では 0.3607 に対して 0.3558（1.4 %）、30° では 0.126 に対して 0.1212（3.8 %）でした。スライス数を 16 から 128 まで変えても、仰角 10° で 0.3518 から 0.356 の範囲で、スライス数よりスライス中央での 1 点サンプルの偏りが主な誤差でした。

仰角が大きい（上を向く）ほど視線が短い距離で密度が大きく変わるので、誤差が大きくなります。霧の密度が急に変わる所はスライスを細かくするか解析的な積分を使います。

## 散乱と吸収に分ける {#sigma}

密度はそのまま光の計算に使わず物理的な係数に変換します。媒質を光が通るとき光を弱める要因は 2 つあります。散乱は光が別の方向へ飛ばされることで、霧が白く見える理由です。吸収は光が熱などに変わって消えることで、煙が暗く見える理由です。この 2 つを合わせた「光が弱まる量」が、消散です。

<div class="formula">消散係数 σ_t = 散乱係数 σ_s + 吸収係数 σ_a</div>

霧（水滴）はほとんど吸収せず散乱が主です。煙は吸収も多くて暗くなります。密度に散乱の色（アルベド）を掛けて `σ_s` を吸収の色を掛けて `σ_a` を求めます。たとえば、白い霧ならアルベドが `(1, 1, 1)` で、`σ_a = 0` です。黒い煙ならアルベドを 0.3 程度にして、吸収を多くします。アルベド `a` は `σ_s / σ_t` で `a = 0.95` の霧なら散乱が 95 %、吸収が 5 % です。

この分け方のおかげで同じ「密度」でも霧と煙で見た目を変えられます。密度は「どれだけ濃いか」、アルベドは「どんな物質か」を表す独立な 2 つのパラメータです。

## ノイズの使い方 {#noise}

ノイズは 3D ノイズ テクスチャ（Perlin や Worley）をワールド座標でサンプルします。座標に風の速度 × 時間を足すと霧が風で流れます。複数のスケールのノイズを重ねると（フラクタル）、大きな塊と細かい揺らぎを持つ自然な濃淡になります。

ノイズの値は平均がおよそ 0.5 なので、2 を掛けて平均を 1 にそろえます。こうすると全体の濃さは変わらずむらだけを足せます。`lerp(1.0, noise * 2.0, strength)` で強さ `strength` を決めます。ただし、froxel の解像度が粗いので、細かいノイズは時間蓄積でないとちらつきやすいです（[Temporal Accumulation](temporal.md)）。

## 計算シェーダーで書く {#shader}

最初にデータとセルの位置を求める関数です。

```hlsl
RWTexture3D<float4> g_froxel_scatter : register(u0);   // xyz = 散乱係数（RGB）、w = 消散係数（密度）
Texture3D<float> g_noise_3d : register(t0);             // 低周波の 3D ノイズ（0..1。平均 0.5）
SamplerState g_linear_wrap : register(s0);

struct FogVolume {
  float4x4 world_to_local;   // ワールド → ボリュームのローカル（箱が -0.5〜0.5 になる）
  float density;             // ボリュームの中で足す消散係数（1/m）
  float edge_softness;       // 縁をなめらかにする幅（ローカル座標。0〜0.5）
  float2 pad;
};
StructuredBuffer<FogVolume> g_fog_volumes : register(t1);

cbuffer FogConstants : register(b0) {
  float4x4 g_inv_view_proj;
  float3 g_camera_position;
  float g_near;              // froxel の近い面（メートル）。例: 0.5
  float3 g_wind_direction;   // 風の向き（正規化）
  float g_far;               // froxel の遠い面（メートル）。例: 300
  float3 g_fog_albedo;       // 散乱の色（アルベド）。白い霧なら (1, 1, 1) に近い
  float g_uniform_density;   // 一様な消散係数（1/m）。例: 0.002
  float g_height_density;    // 高さによる消散係数の基準（1/m）。例: 0.02
  float g_height_falloff;    // 高さの減衰 k（1/m）。例: 0.15
  float g_fog_base_height;   // 霧の基準の高さ（ワールド y）
  float g_noise_scale;       // ノイズの周波数（1/m）。例: 0.02
  float g_noise_strength;    // ノイズの強さ 0..1。例: 0.6
  float g_wind_speed;        // 風の速さ（m/s）
  float g_time;              // 秒
  uint g_fog_volume_count;
  uint3 g_grid_size;         // froxel の解像度。例: (160, 90, 64)
  uint g_frame_index;
};

// フレームごとにわずかにずらすジッター（-0.5..0.5）。時間蓄積で縞を消すために使う
float3 JitterOffset() {
  return frac(float3(g_frame_index * 0.7548776662, g_frame_index * 0.5698402909, g_frame_index * 0.618034)) - 0.5;
}

// froxel の座標（セルの中心 +ジッター）→ ワールド位置。奥行きは指数的に分ける
float3 FroxelToWorld(float3 grid_pos) {
  float2 uv = grid_pos.xy / g_grid_size.xy;
  float slice = grid_pos.z / g_grid_size.z;                          // 0..1
  float view_depth = g_near * pow(g_far / g_near, slice);            // 指数分割
  float4 ndc_far = float4(uv.x * 2.0 - 1.0, 1.0 - uv.y * 2.0, 1.0, 1.0);
  float4 w = mul(ndc_far, g_inv_view_proj);
  float3 dir = normalize(w.xyz / w.w - g_camera_position);
  return g_camera_position + dir * view_depth;                      // 簡略化: 視線方向の距離で置く（足した処理）
}
```

次に、密度を求める本体です。

```hlsl
[numthreads(8, 8, 4)]
void DensityCS(uint3 id : SV_DispatchThreadID) {
  if (any(id >= g_grid_size)) return;
  float3 world = FroxelToWorld(float3(id) + 0.5 + JitterOffset());   // セルの中心 + ジッター

  // ① 一様な密度 + 高さによる密度
  float h = world.y - g_fog_base_height;
  float density = g_uniform_density + g_height_density * exp(-g_height_falloff * max(h, 0.0));

  // ② ノイズでむらを与える。風でずらして流す。平均 1 にそろえて、全体の濃さを変えない
  float3 noise_pos = world * g_noise_scale + g_wind_direction * g_time * g_wind_speed;
  float noise = g_noise_3d.SampleLevel(g_linear_wrap, noise_pos, 0);
  density *= lerp(1.0, noise * 2.0, g_noise_strength);

  // ③ 局所的な霧のボリューム（箱）を足す。箱の中だけ、縁をなめらかに
  for (uint i = 0; i < g_fog_volume_count; ++i) {
    FogVolume v = g_fog_volumes[i];
    float3 local = mul(float4(world, 1.0), v.world_to_local).xyz;    // -0.5〜0.5 の箱
    float inside = all(abs(local) < 0.5) ? 1.0 : 0.0;
    float edge = saturate(min(min(0.5 - abs(local.x), 0.5 - abs(local.y)), 0.5 - abs(local.z)) / max(v.edge_softness, 1e-4));
    density += v.density * inside * edge;
  }
  density = max(density, 0.0);

  // ④ 散乱係数（アルベド × 密度）と消散係数（密度）を書く。霧はほぼ散乱だけ（アルベドが高い）
  float3 scattering = g_fog_albedo * density;
  g_froxel_scatter[id] = float4(scattering, density);
}
```

局所的な霧（沼、洞窟）は箱（または球）の形のボリュームとして置きます。セルが箱の中にあれば密度を足して、縁はなめらかに薄くします。ボリュームをアーティストがレベルに置く（霧のボリューム アクター）ことで、場所ごとの霧を作れます。

局所的な霧のボリュームは CPU 側でリストにして、構造化バッファで渡します。カメラの視錐台と交わるボリュームだけを集めて渡すとループが短くなります。

```cpp
// （コンパイルしていない）カメラの視錐台と交わるボリュームだけを集めて、GPU に渡す
struct FogVolume {
  Matrix world_to_local;     // ワールド → ボリュームのローカル（箱が -0.5〜0.5 になる）
  float density;
  float edge_softness;
  float pad[2];
};
```

!!! note "確かめた範囲"
    HLSL は `fxc`（`cs_5_0`）で、`DensityCS` をコンパイルしてエラーが出ないことを確かめました。透過率と視界の数字、froxel の積分の誤差は Python での計算です。GPU での実行は確認していません。

## よくあるミス {#mistakes}

??? failure "霧が一様で単調"
    原因は基本の密度だけで、ノイズや高さを足していないことです。3D ノイズで濃淡を付けて風でずらして流します。高さによる減衰も足します。

??? failure "ノイズを足したら、全体が暗く（濃く）なった"
    原因はノイズの平均を 1 にそろえていないことです。ノイズの値（平均 0.5）をそのまま掛けると、全体が半分になります。2 を掛けて平均を 1 にします。

??? failure "霧のボリュームの縁に硬い線が出る"
    原因は箱の縁で密度が急に 0 になることです。縁に向かってなめらかに（`edge`）密度を落とします。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 密度は一様、高さノイズ、局所ボリュームの足し算です。
    - [x] 消散係数 `σ_t` は 1/m で、視界は約 `3 / σ_t` です。0.01 なら約 300 m です。
    - [x] 散乱と吸収に分けて、霧と煙で見た目を変えます。
    - [x] ノイズは平均 1 にそろえます。

## 参考 {#references}

このページは次の資料を読まずに書きました。数字は式からの計算（Python）です。

- Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Volumetric Fog](index.md)
- [Froxels](froxel.md)
- [Step 2: Light Injection](injection.md)
