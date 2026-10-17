---
title: ボリューメトリック フォグ
tags:
  - 描画
---

# ボリューメトリック フォグ

**距離フォグ**（[距離フォグ](aerial-fog.md)）は、**画面の各ピクセルの距離だけで霞ませます**。**光の柱・光る霧・スポットライトの光の筋**のように、**霧の中を光が通る様子**を**出すには**、**空間そのものに霧の密度と光を持たせる**必要があります。これが**ボリューメトリック フォグ**です。このページでは、**froxel（視錐台に沿ったボクセル）・密度の与え方・光の注入・シャドウ・積分・時間蓄積・適用**を説明します。

!!! tip "ポイント"
    - 霧 ＝ <strong>空間の各点が持つ「密度」と「受ける光」</strong>。<strong>光が当たった霧が視線方向に光る</strong>。
    - <strong>froxel</strong> ＝ <strong>視錐台を、画面に沿って格子（幅×高さ×奥行き）に切った小部屋</strong>。<strong>3D テクスチャ</strong>で持つ。
    - 処理は<strong>① 密度を書く → ② 光を注入 → ③ 奥へ積分 → ④ 画面に合成</strong>。
    - 光の注入は<strong>シャドウ マップ</strong>を引く。<strong>影の中の霧は光らない</strong>（<strong>光の筋が出る理由</strong>）。
    - 解像度は低く（例：160×90×64）。<strong>時間方向に蓄積</strong>して<strong>ノイズ・縞を消す</strong>。
    - 奥行きの割り当ては<strong>非線形</strong>（近くを細かく）。

## 何が違うか

| 方式 | 内容 |
| --- | --- |
| **距離フォグ** | **ピクセルの距離のみ。光は関係なし** |
| **高さフォグ** | **高さと距離。光は関係なし** |
| **ボリューメトリック フォグ** | **空間の各点で光を計算。光の筋・影・光る霧** |

## froxel

**froxel**（frustum voxel）は、**カメラの視錐台を画面の格子（X, Y）と奥行き（Z）で分割した 3D 格子**です。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="froxel">
<text x="20" y="24" class="fig-title">froxel：視錐台を、画面に沿った 3D の格子に切る</text>
<polygon points="80,140 400,60 400,220" fill="#4c8bf5" fill-opacity="0.1" stroke="#4c8bf5" stroke-width="2"/>
<g stroke="currentColor" stroke-opacity="0.4">
<line x1="130" y1="127" x2="130" y2="153"/><line x1="190" y1="112" x2="190" y2="168"/><line x1="260" y1="95" x2="260" y2="185"/><line x1="340" y1="75" x2="340" y2="205"/><line x1="400" y1="60" x2="400" y2="220"/>
</g>
<circle cx="80" cy="140" r="6" fill="#e5484d"/><text x="60" y="164" style="font-size:12px">カメラ</text>
<text x="130" y="120" style="font-size:11px">近い：薄い</text><text x="320" y="62" style="font-size:11px">遠い：厚い</text>
<g transform="translate(470,50)">
<text x="0" y="0" style="font-size:12px;font-weight:700">画面方向の格子（幅×高さ）</text>
<g stroke="currentColor" stroke-opacity="0.4" fill="none"><rect x="0" y="14" width="240" height="135"/>
<line x1="60" y1="14" x2="60" y2="149"/><line x1="120" y1="14" x2="120" y2="149"/><line x1="180" y1="14" x2="180" y2="149"/>
<line x1="0" y1="48" x2="240" y2="48"/><line x1="0" y1="82" x2="240" y2="82"/><line x1="0" y1="116" x2="240" y2="116"/></g>
<rect x="120" y="48" width="60" height="34" fill="#e5aa28" fill-opacity="0.5"/>
<text x="0" y="176" style="font-size:12px">1 マス ＝ 画面の 8×8 ピクセルほど</text>
<text x="0" y="198" style="font-size:12px">奥行き方向に 64 枚ほどのスライス</text>
</g>
</svg>

| 項目 | 内容 |
| --- | --- |
| **解像度** | **160×90×64 程度**（画面の 1/8 の解像度）。**ピクセルを 1 つずつでなく、まとめて計算** |
| **形式** | **3D テクスチャ**（`RGBA16F`：散乱光 RGB ＋ 密度） |
| **奥行きの割り当て** | **近くを細かく**（指数的）。**`z = near * pow(far/near, slice/N)`** |
| **カメラに追従** | **視錐台と一緒に動く**。**画面の解像度に依存しない** |

```hlsl
float SliceToDepth(float slice, float near_z, float far_z, float slice_count) {
  return near_z * pow(far_z / near_z, slice / slice_count);
}

float DepthToSlice(float depth, float near_z, float far_z, float slice_count) {
  return log(depth / near_z) / log(far_z / near_z) * slice_count;
}
```

## 手順

<svg class="fig illust" viewBox="0 0 780 160" role="img" aria-label="ボリューメトリック フォグの手順"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">4 つのパス</text>
<g font-size="12">
<rect x="20" y="56" width="165" height="70" rx="8" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5" stroke-width="2"/><text x="102" y="86" text-anchor="middle" style="font-weight:700">① 密度</text><text x="102" y="106" text-anchor="middle" style="font-size:11px">各 froxel の霧の濃さ</text>
<rect x="215" y="56" width="165" height="70" rx="8" fill="#e5aa28" fill-opacity="0.22" stroke="#e5aa28" stroke-width="2"/><text x="297" y="86" text-anchor="middle" style="font-weight:700">② 光の注入</text><text x="297" y="106" text-anchor="middle" style="font-size:11px">光 × 影 × 位相関数</text>
<rect x="410" y="56" width="165" height="70" rx="8" fill="#9664e6" fill-opacity="0.2" stroke="#9664e6" stroke-width="2"/><text x="492" y="86" text-anchor="middle" style="font-weight:700">③ 積分</text><text x="492" y="106" text-anchor="middle" style="font-size:11px">奥へ足して透過率</text>
<rect x="605" y="56" width="155" height="70" rx="8" fill="#2ea043" fill-opacity="0.2" stroke="#2ea043" stroke-width="2"/><text x="682" y="86" text-anchor="middle" style="font-weight:700">④ 適用</text><text x="682" y="106" text-anchor="middle" style="font-size:11px">画面に合成</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="187" y1="91" x2="213" y2="91" marker-end="url(#rfa)"/><line x1="382" y1="91" x2="408" y2="91" marker-end="url(#rfa)"/><line x1="577" y1="91" x2="603" y2="91" marker-end="url(#rfa)"/></g>
</svg>

## ① 密度

**霧の濃さを各 froxel に書きます**。**複数の要素を足し合わせます**。

| 要素 | 内容 |
| --- | --- |
| **全体の霧** | **一様な基準の密度**（`global_density`） |
| **高さフォグ** | **高さで指数的に減る**（[距離フォグ](aerial-fog.md)） |
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

## ② 光の注入

**各 froxel が受けている光を計算します**。<strong>太陽光とローカル ライト（点光源・スポットライト）</strong>が**対象**です。

<div class="formula">散乱光 = 密度 × アルベド × Σ ( 光の色 × 影 × 位相関数(θ) )</div>

```hlsl
float3 inscattered = 0;

float shadow = SampleCascadeShadow(world_position);
float phase = HenyeyGreenstein(dot(view_dir, -sun_direction), g);
inscattered += sun_color * shadow * phase;

for (uint i = 0; i < light_count; ++i) {
  float3 to_light = lights[i].position - world_position;
  float distance_to_light = length(to_light);
  float3 light_dir = to_light / distance_to_light;
  float attenuation = LightAttenuation(lights[i], distance_to_light);
  float light_shadow = SampleLocalShadow(lights[i], world_position);
  float p = HenyeyGreenstein(dot(view_dir, -light_dir), g);
  inscattered += lights[i].color * attenuation * light_shadow * p;
}

inscattered += ambient_fog_color;
float3 scattering = inscattered * density * albedo;
```

| 点 | 説明 |
| --- | --- |
| **シャドウ マップを引く** | **影の中の霧は光らない**。**この結果、物の影が光の筋として見える** |
| **位相関数** | <strong>前方に強く散る（g ≈ 0.6〜0.8）</strong>。**太陽の方を見ると霧が明るい**（[大気散乱](scattering.md)） |
| **環境光** | **全体にうっすら足す**（暗すぎる霧の防止） |
| **ライトの数が多い場合** | **froxel ごとにライトをカリング**（[ライト カリング](../../rendering/light-culling.md)） |
| **解像度が低くても綺麗** | **霧は低周波**（細かい構造がない）ので低解像度で十分 |

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

## 時間蓄積（TAA 風）

**froxel の解像度が低く、サンプルが少ない**ので**そのままだとノイズや縞が出ます**。**前フレームの結果を再利用して、時間方向に平均します**。

| 工夫 | 内容 |
| --- | --- |
| **ジッター** | **毎フレーム、froxel 内のサンプル位置を少しずらす**（ブルー ノイズなど） |
| **履歴の再投影** | **前フレームの froxel の位置を、カメラの動きで求めて、その値を混ぜる** |
| **ブレンド率** | **新 5〜10 %、履歴 90〜95 %** |
| **履歴の拒否** | **ライトが動いたとき／急な変化は、履歴を弱める** |

```hlsl
float3 previous_uvw = ReprojectFroxel(world_position, previous_view_projection);
float4 history = history_volume.SampleLevel(linear_clamp, previous_uvw, 0);
float4 current = float4(scattering, extinction);
float blend = IsValidHistory(previous_uvw) ? 0.05 : 1.0;
float4 result = lerp(history, current, blend);
```

## 品質と速度

| 項目 | 内容 |
| --- | --- |
| **解像度** | **160×90×64 で十分**。**重ければ 80×45×32** |
| **コスト** | **0.3〜1 ms 程度** |
| **局所ライトの数** | **多いほど重い**。**影付きのライトは数本まで** |
| **遠距離** | **範囲外は距離フォグ（[距離フォグ](aerial-fog.md)）に任せる** |
| **雲・大気との組み合わせ** | **近くはボリューメトリック フォグ、遠くは空気遠近法 LUT** |

## よくあるミス

??? failure "光の筋が出ない"
    **光の注入でシャドウを引いていない**。**影があって初めて光の筋が見える**。

??? failure "霧の中のスポットライトが、ちらつく／ノイズが多い"
    **ジッターと時間蓄積**を入れ、**ブルー ノイズ**を使う。

??? failure "奥行きに縞が出る"
    **スライス数を増やす**、**奥行きにジッターを加える**。

??? failure "霧の合成で、画面の端で濃さが違う"
    **スライスの深度を視線方向の距離で割り当てる**（Z 深度でなく）。

??? failure "霧が全体的に暗い"
    **環境光の項を足す**。**位相関数の `g` を下げる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ボリューメトリック フォグ ＝ <strong>空間の各点の密度と光を、3D テクスチャ（froxel）に持つ</strong>
    - [x] 手順：<strong>密度 → 光の注入（影込み）→ 奥へ積分 → 画面に合成</strong>
    - [x] <strong>影があるから光の筋</strong>が見える。<strong>位相関数</strong>で<strong>太陽方向が明るい</strong>
    - [x] <strong>低解像度 ＋ 時間蓄積</strong>で<strong>軽く滑らか</strong>
    - [x] <strong>奥行きは非線形</strong>（近くを細かく）

## 参考

- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014, Assassin's Creed 4）
- Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite"（SIGGRAPH 2015）
- Hillaire, "Improved Culling for Tiled and Clustered Rendering"

## 関連ページ

- [空と大気](index.md)
- [大気散乱](scattering.md)
- [距離フォグ](aerial-fog.md)
- [光の筋](god-rays.md)
- [雲](clouds.md)
