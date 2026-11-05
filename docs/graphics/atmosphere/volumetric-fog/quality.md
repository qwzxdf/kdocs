---
title: Quality and Performance
tags:
  - 描画
---

# Quality and Performance

ボリューメトリック フォグは froxel の分割数 3 つ（横・縦・奥行き）で、品質とコストがほぼ決まります。分割を細かくすれば細い光の筋は出ますが、セルの数は 3 乗で増えます。粗くすれば軽くなりますが奥行きの縞や光漏れが出ます。どこまで粗くできるかは見た目の問題ごとにセルの大きさで見積もれます。このページでは Wronski（Assassin's Creed IV）の報告した数字を拠り所に、プリセットごとのセル数・メモリ・セルの大きさを C++ で計算し縞、ぼやけ光漏れ遠景の 4 つの問題と対策をコメント付きの HLSL で説明します。

!!! tip "ポイント"
    - 標準の 160 × 90 × 64 は 921,600 セルで、720p の画素数と同じである。コストは画面の解像度に依存しない。
    - Wronski の報告では、全体で約 1.1 ms。最も重いのは密度とライティング（約 0.43 ms）で、ほかの段階は 0.2 ms 未満である。
    - 奥行きの分割は横・縦に比べて粗い。標準ではセルの奥行きが横幅の約 7 倍ある。縞の主な原因はここにある。
    - 光漏れはセルが壁より厚くなる距離（標準で 15.6 m）から始まる。壁の近くではセル内の複数サンプルが効く。
    - 遠くは froxel で粗く持たず空気遠近法に任せる。境目はフェードで消す。

!!! info "このページを読む前に"
    - [Volumetric Fog](index.md)（このセクション全体の地図と、読む順番）
    - [Froxels](froxel.md)（froxel の配置と奥行きの分割）

## 読んだ資料 {#sources}

- Bart Wronski, "Volumetric Fog: Unified, Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014 Advances in Real-Time Rendering in Games。スライドとノート 67 枚の本文を全部読みました。図とビデオと付録のコード（画像）は読めていません。
- Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015 は、取得できず読んでいません。

プリセット（低・中・高・最高）の値は、資料にありません。Wronski の標準に合わせて、このページが決めた一例です。3 次補間、セル内の複数サンプル、ディザ、ライトの除外も資料にない一般的な手法で、このページで足した部品です。

## Wronski の報告した数字 {#reported}

- 大きさは 160 × 90 × 64、またはプラットフォームによって 160 × 90 × 128。
- 160 × 90 × 64 のセル数は、720p の画素数と同じ。ただしセルごとのライティングは 1 回だけ。
- 距離は 50〜128 m（美術の設定）。「指数の奥行きの分割かカスケードにすれば、もっと遠くもできる」と書かれています。
- 全体のコストは約 1.1 ms。倍の解像度では 1.6 ms。最も重いのは密度とライティングの構築で約 0.43 ms。ほかの段階はすべて 0.2 ms 未満。適用の段階は他のパスと統合すれば「無料」になる。
- コストの一部はシャドウ マップの準備なので、他の低周波のライティング（パーティクル、半透明、海）と共有できる。

「倍の解像度で 1.6 ms」は 1.1 ms の 1.45 倍です。セル数が 4 倍（横縦それぞれ 2 倍）になっても 4 倍にならないのは、シャドウ マップの縮小などセル数に比例しない固定の費用があるからです。

## コストはどこで決まるか {#cost-model}

最も重いのは光の注入です。セルごとにすべてのライトと影を評価します。セル数 × ライト数におおよそ比例します。積分は(x, y) の列ごとに奥行きを 1 回なぞるだけで、軽い処理です。適用は画素ごとに 3D テクスチャを 1 回引くだけです。

コストを下げるには注入を見ます。次の 3 つがあります。

1. 影付きのライトを減らす。遠くのライトから省く。
2. セル数を下げる。
3. 届かないライトをセルごとに先に除外する。Wronski は Forward+ やクラスタードのようなライトの絞り込みを、フォグにも使えると書いています。

## 品質プリセット：数えてみる {#presets}

セル数・メモリ・影を引く回数を C++ で計算しました。メモリは RGBA16F の 3D テクスチャ 3 枚（散乱、積分、履歴）として見積もっています。

| 設定 | froxel | 最大距離 | 影を引くライト | 時間方向 |
| --- | --- | --- | --- | --- |
| 低 | 80×45×32 | 64 m | 太陽のみ | あり |
| 中 | 160×90×64 | 128 m | 太陽 + 影つき 2 | あり |
| 高 | 240×135×96 | 256 m | 太陽 + 影つき 4 | あり |
| 最高 | 320×180×128 | 512 m | 太陽 + 影つき 7 | あり |

セル数は低が標準の 0.12 倍（115,200）、高が 3.38 倍（3,110,400）、最高が 8 倍（7,372,800）です。3 枚のメモリは 2.6 MiB、21.1 MiB、71.2 MiB、168.8 MiB です。影を引く回数は 1 フレームあたり低が約 0.1 M、中が 2.8 M、高が 15.6 M、最高が 59 M です。最高は中の約 21 倍で設定をひとつ上げるごとに影の評価が急に増えることが分かります。

## セルの形：奥行きが粗い {#cell-shape}

<svg class="fig flow" viewBox="0 0 660 226" role="img" aria-label="セルの横幅とスライスの厚み"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">標準 160x90x64: 距離ごとの、セルの横幅(青)と、スライスの厚み(黄)[m]</text><line x1="60" y1="184" x2="620" y2="184" stroke="#94a3b8"/><rect x="80" y="183.6" width="30" height="1.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="95" y="179.58947368421053" text-anchor="middle" font-size="10" fill="currentColor">0.03</text><rect x="114" y="181.1" width="30" height="2.9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="129" y="177.1421052631579" text-anchor="middle" font-size="10" fill="currentColor">0.18</text><text x="112" y="200" text-anchor="middle" font-size="10" fill="currentColor">2 m</text><rect x="170" y="183.0" width="30" height="1.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="185" y="178.98947368421054" text-anchor="middle" font-size="10" fill="currentColor">0.06</text><rect x="204" y="177.2" width="30" height="6.8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="219" y="173.19473684210527" text-anchor="middle" font-size="10" fill="currentColor">0.43</text><text x="202" y="200" text-anchor="middle" font-size="10" fill="currentColor">5 m</text><rect x="260" y="182.0" width="30" height="2.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="275" y="177.97894736842105" text-anchor="middle" font-size="10" fill="currentColor">0.13</text><rect x="294" y="170.4" width="30" height="13.6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="309" y="166.40526315789475" text-anchor="middle" font-size="10" fill="currentColor">0.86</text><text x="292" y="200" text-anchor="middle" font-size="10" fill="currentColor">10 m</text><rect x="350" y="177.9" width="30" height="6.1" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="365" y="173.92105263157896" text-anchor="middle" font-size="10" fill="currentColor">0.39</text><rect x="384" y="142.1" width="30" height="41.9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="399" y="138.06315789473683" text-anchor="middle" font-size="10" fill="currentColor">2.66</text><text x="382" y="200" text-anchor="middle" font-size="10" fill="currentColor">30 m</text><rect x="440" y="171.8" width="30" height="12.2" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="455" y="167.8421052631579" text-anchor="middle" font-size="10" fill="currentColor">0.77</text><rect x="474" y="100.1" width="30" height="83.9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="489" y="96.12631578947367" text-anchor="middle" font-size="10" fill="currentColor">5.31</text><text x="472" y="200" text-anchor="middle" font-size="10" fill="currentColor">60 m</text><rect x="530" y="163.7" width="30" height="20.3" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="545" y="159.7421052631579" text-anchor="middle" font-size="10" fill="currentColor">1.28</text><rect x="564" y="43.0" width="30" height="141.0" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="579" y="38.952631578947376" text-anchor="middle" font-size="10" fill="currentColor">8.93</text><text x="562" y="200" text-anchor="middle" font-size="10" fill="currentColor">100 m</text><text x="60" y="222" text-anchor="start" font-size="10" fill="currentColor">どの距離でも、スライスの厚みは横幅の約 7 倍(比 0.14)。縞は奥行きの粗さから出る</text></svg>

標準の froxel のセルは画面の横・縦はほぼ正方形で、距離 10 m で 0.128 m 四方です。ところが、奥行きの厚みは 10 m で 0.861 m あります。セルの幅と厚みの比はどの距離でも約 0.14（横は奥行きの約 7 分の 1）です。つまり、セルは奥行き方向に長い細長い形です。

これは指数の分割の性質です。距離 z のスライスの厚みは `z × ((far/near)^(1/N) − 1)` で、標準（0.5〜128 m、64 層）では z × 0.0905 です。横方向の大きさは `2 z tan(画角/2) / 分割数` なので、どちらも z に比例し比は距離によりません。

線形に分割したら 1 スライスが 1.99 m です。指数なら 2 m で 0.181 m（線形の 11 分の 1）になります。近くを細かくするために遠くを粗くした結果、100 m では 9.05 m です。

## 見た目の問題と対策 {#problems}

### ① 縞（バンディング）{#banding}

スライスに沿った縞はスライスの厚みが、セル幅の約 7 倍あることが主な原因です。横方向をどれだけ細かくしても、奥行きの縞は変わりません。

対策は 3 つです。奥行きのスライス数を増やす（64 → 96 → 128）ことと補間を 3 次にすること、ディザで縞を細かいノイズに変えることです。Wronski は時間方向のジッター（サンプル位置をフレームごとにずらす）と再投影を、アーティファクトを消す手段として挙げています。1 サンプルのジッターだけで、輪郭のアーティファクトがほぼ消えたと書かれています。

```hlsl
// ボリューメトリック フォグの「品質」に効く 5 つの部品。
//   ① 奥行きの縞を目立たなくする: 3 次補間で読む、ディザを足す
//   ② 光漏れを減らす: セルの中で影を複数回引いて平均する
//   ③ 遠くを切る: 最大距離の手前で、フォグの寄与をフェードアウトさせる
//   ④ コストを下げる: セルに届かないライトを先に捨てる
// 土台の注入と積分は、[Volume-Based God Rays] のコードと同じ。ここは、その上に足す部分だけ。
// Wronski (2014) は、品質の主な手段として、ESM への縮小、時間方向のジッター、3D の補間を挙げている。
// 3 次補間、セル内の複数サンプル、ディザ、ライトの除外は、この資料にない一般的な手法で、このページが足したもの。

Texture3D<float4> g_integrated : register(t0);          // 積分済みの froxel。rgb = 散乱光、a = 透過率
Texture2D<float> g_esm : register(t1);                  // 縮小した ESM
SamplerState g_linear_clamp : register(s0);
RWTexture3D<float4> g_scatter_out : register(u0);

cbuffer FogQualityCB : register(b0) {
  float4x4 g_inv_view_proj;
  float4x4 g_sun_view_proj;
  float3 g_camera_pos;
  float g_near;                    // froxel の手前端 [m]
  float3 g_sun_dir;
  float g_far;                     // froxel の奥端 [m]
  float3 g_sun_color;
  float g_esm_c;                   // ESM の指数
  uint3 g_grid;                    // 分割数（例: 160, 90, 64）
  uint g_light_count;
  float g_fade_start;              // フェード開始の距離 [m]（例: 最大距離の 0.8 倍）
  float g_cell_jitter_scale;       // セル内の複数サンプルの広がり（1 = セルいっぱい）
  uint g_shadow_samples;           // セルの中で影を引く回数（1, 2, 4）
  uint g_frame;                    // フレーム番号（ジッターの種）
};

struct PointLight {
  float3 position;                 // ワールドの位置 [m]
  float radius;                    // 影響半径 [m]
  float3 color;                    // 色 × 強さ
  float pad;
};
StructuredBuffer<PointLight> g_lights : register(t2);

// ================= ① 縞を隠す =================

// 3 次 B スプラインの重み（Sigg & Hadwiger の方法）。f は 0〜1 の小数部。
// 戻り値の w01 = 2 つのタップの位置の補正、w23 = 重み。
void CubicBSplineWeights(float f, out float4 w) {
  float f2 = f * f;
  float f3 = f2 * f;
  w.x = (1.0 - f) * (1.0 - f) * (1.0 - f) / 6.0;                       // 左端の重み
  w.y = (3.0 * f3 - 6.0 * f2 + 4.0) / 6.0;                             // 左の中心
  w.z = (-3.0 * f3 + 3.0 * f2 + 3.0 * f + 1.0) / 6.0;                  // 右の中心
  w.w = f3 / 6.0;                                                      // 右端
}

// 3 次 B スプラインで 3D テクスチャを読む。64 回の読み込みを、トライリニアの 8 回にまとめる。
// 各軸で、4 つのタップを 2 組に分け、組の中は GPU のトライリニアにまかせる。
// 3 次にすると、スライスの境目で値の傾きも連続になり、縞が目立ちにくい。コストは約 8 倍の読み込み。
float4 SampleFroxelCubic(Texture3D<float4> tex, float3 uvw, float3 size) {
  float3 coord = uvw * size - 0.5;                                     // テクセル座標（中心が整数）
  float3 base = floor(coord);
  float3 f = coord - base;                                             // 小数部

  float4 wx, wy, wz;
  CubicBSplineWeights(f.x, wx);
  CubicBSplineWeights(f.y, wy);
  CubicBSplineWeights(f.z, wz);

  // 4 タップを 2 組にまとめる。組の位置 = 重みの比で補正した位置。
  float3 g0 = float3(wx.x + wx.y, wy.x + wy.y, wz.x + wz.y);           // 左の組の重み
  float3 g1 = float3(wx.z + wx.w, wy.z + wy.w, wz.z + wz.w);           // 右の組の重み
  float3 h0 = base + float3(-1.0 + wx.y / g0.x, -1.0 + wy.y / g0.y, -1.0 + wz.y / g0.z) + 0.5;   // 左の組の読み位置
  float3 h1 = base + float3(1.0 + wx.w / g1.x, 1.0 + wy.w / g1.y, 1.0 + wz.w / g1.z) + 0.5;      // 右の組の読み位置
  h0 /= size;
  h1 /= size;

  // 8 通りの組み合わせを、重みを掛けて足す。
  float4 r = 0;
  r += g0.x * g0.y * g0.z * tex.SampleLevel(g_linear_clamp, float3(h0.x, h0.y, h0.z), 0);
  r += g1.x * g0.y * g0.z * tex.SampleLevel(g_linear_clamp, float3(h1.x, h0.y, h0.z), 0);
  r += g0.x * g1.y * g0.z * tex.SampleLevel(g_linear_clamp, float3(h0.x, h1.y, h0.z), 0);
  r += g1.x * g1.y * g0.z * tex.SampleLevel(g_linear_clamp, float3(h1.x, h1.y, h0.z), 0);
  r += g0.x * g0.y * g1.z * tex.SampleLevel(g_linear_clamp, float3(h0.x, h0.y, h1.z), 0);
  r += g1.x * g0.y * g1.z * tex.SampleLevel(g_linear_clamp, float3(h1.x, h0.y, h1.z), 0);
  r += g0.x * g1.y * g1.z * tex.SampleLevel(g_linear_clamp, float3(h0.x, h1.y, h1.z), 0);
  r += g1.x * g1.y * g1.z * tex.SampleLevel(g_linear_clamp, float3(h1.x, h1.y, h1.z), 0);
  return r;
}

// 三角分布のディザ（-1〜+1）。画素の位置とフレームから作る。8 bit の出力に足すと、縞が細かいノイズになる。
float TriangularDither(uint2 pix, uint frame) {
  uint h = pix.x * 1973u + pix.y * 9277u + frame * 26699u;             // 簡単な整数ハッシュ
  h = (h ^ (h >> 13)) * 1274126177u;
  float a = (h & 0xFFFFu) / 65535.0;
  float b = ((h >> 16) & 0xFFFFu) / 65535.0;
  return a + b - 1.0;                                                  // 2 つの一様乱数の和 - 1 = 三角分布
}
```

3 次 B スプラインは 64 回の読み込みが必要なところをトライリニアの 8 回にまとめます。各軸で 4 つのタップを 2 組に分け組の読み位置を重みの比で補正することで、1 組を GPU のトライリニア 1 回に置き換えます。スライスの境目で値の傾きまで連続になるので、縞が目立ちにくくなります。コストは読み込みが約 8 倍になります。

### ② 光の筋がぼやける {#blur}

低解像度の froxel では細い光の筋（窓の格子）が失われます。標準の 160 × 90 は画面の幅を 160 に分けるので、1 セルが画面で 12 画素を覆います。

Wronski はこれを欠点として認めたうえで、「実際の大気では多重散乱で光の筋が柔らかくなるので、見た目に合う」と書いています。細い筋が必要な場所だけ別の方法で補います（[Screen-Space Radial Blur](../god-rays/radial-blur.md)、[Light Shaft Meshes](../god-rays/mesh-shafts.md)）。時間方向のジッターで見かけの解像度を上げる方法もあります（[Temporal Accumulation](temporal.md)）。

### ③ 光漏れ {#leak}

セルが壁より厚くなると壁の向こうの光が、こちら側のセルに混ざります。壁の厚みを 0.2 m とすると、セル幅がそれを超える距離は低で 7.8 m、中で 15.6 m、高で 23.4 m、最高で 31.2 m です。標準では 15.6 m より遠くで、薄い壁の光漏れが起こりえます。

対策はセルを小さくすることセルの中で複数の位置の影を引いて平均することジッターと履歴で平均することです。複数サンプルは壁がセルの途中にあっても、壁より手前にあるサンプルの割合に応じた明るさになります。1 回だけだとセルの中心が壁のどちら側かで、セル全体が 0 か 1 になります。

```hlsl
// ================= ④ ライトの除外 =================

// セルを含む球（中心 cell_center、半径 cell_radius）に、ライトの影響球が届くか。届かなければ、計算を省く。
bool LightReachesCell(PointLight light, float3 cell_center, float cell_radius) {
  float d = distance(light.position, cell_center);
  return d < light.radius + cell_radius;
}

// ================= ② セル内の影（光漏れ対策）=================

// ESM の影。world は、影を引きたいワールド位置。
float ShadowAt(float3 world) {
  float4 clip = mul(float4(world, 1.0), g_sun_view_proj);
  float3 ndc = clip.xyz / clip.w;
  float2 uv = ndc.xy * float2(0.5, -0.5) + 0.5;
  if (any(uv < 0.0) || any(uv > 1.0)) return 1.0;                      // シャドウ マップの外は、日向
  return saturate(g_esm.SampleLevel(g_linear_clamp, uv, 0) * exp(-g_esm_c * ndc.z));
}

// セルの中の複数の位置で影を引いて平均する。壁がセルの途中にあっても、その割合に応じた明るさになる。
// 1 回だと、セルの中心が壁のこちら側か向こう側かで、セル全体が 0 か 1 になり、光が漏れる。
float CellShadow(float3 cell_center, float3 cell_extent, uint3 id) {
  float sum = 0;
  for (uint i = 0; i < g_shadow_samples; ++i) {
    // 各軸 -0.5〜+0.5 の疑似乱数（セルの添字、サンプル番号、フレームから）。
    uint seed = id.x * 73856093u ^ id.y * 19349663u ^ id.z * 83492791u ^ (i * 2654435761u) ^ (g_frame * 40503u);
    float3 r = float3((seed & 255u), ((seed >> 8) & 255u), ((seed >> 16) & 255u)) / 255.0 - 0.5;
    sum += ShadowAt(cell_center + r * cell_extent * g_cell_jitter_scale);
  }
  return sum / g_shadow_samples;
}

[numthreads(8, 8, 4)]
void InjectQualityCS(uint3 id : SV_DispatchThreadID) {
  if (any(id >= g_grid)) return;

  // セルの中心と大きさ（ワールド）。スライスの距離は指数の刻み。
  float3 uvw = (float3(id) + 0.5) / float3(g_grid);
  float dist = g_near * pow(max(g_far / g_near, 1.0), uvw.z);          // このスライスの距離 [m]
  float dist_next = g_near * pow(max(g_far / g_near, 1.0), (id.z + 1.0) / g_grid.z);
  float2 ndc = uvw.xy * float2(2, -2) + float2(-1, 1);
  float4 far_clip = mul(float4(ndc, 1.0, 1.0), g_inv_view_proj);
  float3 dir = normalize(far_clip.xyz / far_clip.w - g_camera_pos);
  float3 center = g_camera_pos + dir * dist;

  // セルのおおよその大きさ: 横・縦は距離に比例、奥行きはスライスの厚み。
  float lateral = dist * 2.0 / g_grid.y * 0.5774;                      // 縦の画角 60 度の場合の 1 セルの縦の大きさ
  float3 extent = float3(lateral, lateral, dist_next - dist);
  float cell_radius = 0.5 * length(extent);

  // 太陽: セル内で複数回、影を引く。
  float3 radiance = g_sun_color * CellShadow(center, extent, id);

  // 局所ライト: 届くものだけを足す（影なしの簡易）。
  for (uint i = 0; i < g_light_count; ++i) {
    PointLight light = g_lights[i];
    if (!LightReachesCell(light, center, cell_radius)) continue;       // 届かないライトを捨てる
    float d = distance(light.position, center);
    float atten = saturate(1.0 - d / light.radius);
    radiance += light.color * atten * atten;
  }

  g_scatter_out[id] = float4(radiance, 1.0);
```

`LightReachesCell` はライトの影響球とセルを含む球が重なるかを調べて、届かないライトを計算から外します。`CellShadow` はセルの中の疑似乱数の位置で、ESM の影を引いて平均します。サンプル数 `g_shadow_samples` は 1、2、4 のように選びます。

### ④ 遠景：froxel の範囲 {#far}

froxel はカメラのごく近い範囲に限るのが現実的です。Wronski は 50〜128 m で、遠景の長い距離のフォグを現世代のアートに合わせていました。範囲の外は空気遠近法（[Aerial Perspective and Fog](../aerial-fog/index.md)）に任せます。

境目で急に変わらないよう最大距離の手前で froxel の寄与をフェードアウトさせます。

```hlsl
// ================= ③ 遠くを切る =================

// 最大距離の手前から、フォグの寄与をなめらかに 0 にする。1 = そのまま、0 = 寄与なし。
float FarFade(float distance_m) {
  return 1.0 - smoothstep(g_fade_start, g_far, distance_m);
}

// 画面に適用。遠くは、froxel の寄与を弱めて、空気遠近法（別の LUT）に任せる。
float3 ApplyFogQuality(float3 scene_color, float2 screen_uv, float distance_m, uint2 pix, float3 aerial_scatter,
                       float3 aerial_transmittance) {
  float slice = log(max(distance_m, g_near) / g_near) / log(g_far / g_near);   // 0〜1 の奥行き座標
  float3 uvw = float3(screen_uv, saturate(slice));
  float4 fog = SampleFroxelCubic(g_integrated, uvw, float3(g_grid));          // 3 次補間で読む
  float fade = FarFade(distance_m);

  // 近くは froxel、遠くは空気遠近法。fade で混ぜる（透過率は掛け算、散乱光は足し算で混ぜる）。
  float3 transmittance = lerp(aerial_transmittance, fog.a, fade);
  float3 scatter = lerp(aerial_scatter, fog.rgb, fade);
  float3 color = scene_color * transmittance + scatter;

  // 出力が 8 bit のとき、ディザで縞を隠す。1/255 の振幅で足す。
  return color + TriangularDither(pix, g_frame) / 255.0;
}
```

```hlsl
}

// 画素シェーダー: 画面に適用する（②〜④の部品を呼ぶ入口）。aerial は別の LUT から読んだ値を渡す想定。足した処理。
float4 ApplyFogPS(float4 pos : SV_Position, float2 uv : TEXCOORD0, float distance_m : TEXCOORD1,
                  float3 scene_color : TEXCOORD2) : SV_Target {
  float3 aerial_scatter = 0;               // 本番では、空気遠近法の LUT から読む
  float3 aerial_transmittance = 1;
  return float4(ApplyFogQuality(scene_color, uv, distance_m, uint2(pos.xy), aerial_scatter, aerial_transmittance), 1.0);
}
```

<!-- fig:froxel-depth-split:begin -->

<svg class="fig illust motion" data-fig="froxel-depth-split" viewBox="0 0 780 340" role="img"><rect x="0" y="0" width="780" height="340" rx="14" fill="#ffffff"/>
<defs><marker id="arr-froxel-depth-split" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">スライスを奥行きに並べる 2 通り: 等間隔と、手前を細かく</text>
<line x1="60" y1="110" x2="720" y2="110" stroke="#94a3b8" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;1.0000" values="0;0;1;1"/><line x1="60.0" y1="88" x2="60.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="101.25" y1="88" x2="101.25" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="142.5" y1="88" x2="142.5" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="183.75" y1="88" x2="183.75" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="225.0" y1="88" x2="225.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="266.25" y1="88" x2="266.25" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="307.5" y1="88" x2="307.5" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="348.75" y1="88" x2="348.75" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="390.0" y1="88" x2="390.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="431.25" y1="88" x2="431.25" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="472.5" y1="88" x2="472.5" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="513.75" y1="88" x2="513.75" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="555.0" y1="88" x2="555.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="596.25" y1="88" x2="596.25" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="637.5" y1="88" x2="637.5" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="678.75" y1="88" x2="678.75" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="720.0" y1="88" x2="720.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<text x="60" y="72" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">等間隔(1 枚 6.3 m)</text>
</g>
<line x1="60" y1="220" x2="720" y2="220" stroke="#94a3b8" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;1.0000" values="0;0;1;1"/><line x1="60.0" y1="198" x2="60.0" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="63.49744860406542" y1="198" x2="63.49744860406542" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="67.98826150524448" y1="198" x2="67.98826150524448" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="73.75457941194762" y1="198" x2="73.75457941194762" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="81.1586781648561" y1="198" x2="81.1586781648561" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="90.66572915125658" y1="198" x2="90.66572915125658" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="102.87302425554108" y1="198" x2="102.87302425554108" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="118.54750143845021" y1="198" x2="118.54750143845021" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="138.6739285345976" y1="198" x2="138.6739285345976" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="164.5167724731637" y1="198" x2="164.5167724731637" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="197.69964092977727" y1="198" x2="197.69964092977727" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="240.3072874266751" y1="198" x2="240.3072874266751" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="295.01658847393827" y1="198" x2="295.01658847393827" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="365.2647215478455" y1="198" x2="365.2647215478455" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="455.46510988960506" y1="198" x2="455.46510988960506" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="571.2847011155291" y1="198" x2="571.2847011155291" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="720.0" y1="198" x2="720.0" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<text x="60" y="182" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">指数(手前が細かい)</text>
</g>
<text x="60" y="275" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">カメラ 0 m</text>
<text x="720" y="275" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">100 m</text>
<text x="390" y="315" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">16 枚のスライスを 0〜100 m に並べる<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;1.0000" values="1;1;0;0"/></text>
<text x="390" y="315" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">等間隔: 遠くも近くも同じ粗さ<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;0.3330;0.3333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="315" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">指数: 目に近い所を細かく、遠くを粗く(遠くは、もともと小さく見える)<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:froxel-depth-split:end -->

`FarFade` は `smoothstep` で 1 から 0 へ滑らかに変えます。画素シェーダー `ApplyFogPS` はこれらの部品を呼ぶ入口です。近くの froxel と遠くの空気遠近法を透過率と散乱光の両方でこの重みで混ぜます。

<svg class="fig flow" viewBox="0 0 700 176" role="img" aria-label="プリセットのセル数"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">プリセットのセル数(対数軸)と、影を引く回数 / フレーム</text><text x="162" y="52" text-anchor="end" font-size="11" fill="currentColor">低 80x45x32</text><rect x="170" y="34" width="132.7" height="24" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="308.6815598858991" y="51" text-anchor="start" font-size="10" fill="currentColor">115,200  影 0.1 M</text><text x="162" y="86" text-anchor="end" font-size="11" fill="currentColor">中 160x90x64</text><rect x="170" y="68" width="245.6" height="24" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="421.5678082598921" y="85" text-anchor="start" font-size="10" fill="currentColor">921,600  影 2.8 M</text><text x="162" y="120" text-anchor="end" font-size="11" fill="currentColor">高 240x135x96</text><rect x="170" y="102" width="311.6" height="24" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="487.6020304057726" y="119" text-anchor="start" font-size="10" fill="currentColor">3,110,400  影 15.6 M</text><text x="162" y="154" text-anchor="end" font-size="11" fill="currentColor">最高 320x180x128</text><rect x="170" y="136" width="358.5" height="24" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="534.4540566338851" y="153" text-anchor="start" font-size="10" fill="currentColor">7,372,800  影 59.0 M</text></svg>

## 数字を出した C++ {#cpp}

プリセットのセル数とメモリ、セルの大きさ光漏れの距離を数えた C++ です。

MSVC（`/std:c++latest /W4`）でコンパイルして実行しました。HLSL は `fxc`（cs_5_0、ps_5_0）でコンパイルして確かめました。実行して絵は確かめていません。

```cpp
// ボリューメトリック フォグの品質プリセットを、数字で比べる。
//  1. セル数・メモリ・影を引く回数
//  2. セルの大きさ（横・縦）とスライスの厚み（距離ごと）
//  3. 壁の厚みよりセルが大きくなる距離（光漏れの目安）
//  4. 近い範囲の「1 セルあたりの角度」と、画面の画素との比
#include <cmath>
#include <cstdio>
#include <initializer_list>

namespace {
constexpr double kMiB = 1024.0 * 1024.0;
constexpr double kTanV = 0.57735026919;          // 縦の画角 60 度の tan(30°)
constexpr double kAspect = 16.0 / 9.0;
constexpr double kTanH = kTanV * kAspect;

struct Preset {
  const char* name;
  int nx, ny, nz;
  double near_m, far_m;
  int lights;           // 影を引くライトの数（太陽を含む）
};

// スライス k の手前端の距離（指数の刻み）。
double SliceStart(const Preset& p, double k) { return p.near_m * std::pow(p.far_m / p.near_m, k / p.nz); }
}  // namespace

int main() {
  const Preset presets[] = {{"低", 80, 45, 32, 0.5, 64, 1},
                            {"中", 160, 90, 64, 0.5, 128, 3},
                            {"高", 240, 135, 96, 0.5, 256, 5},
                            {"最高", 320, 180, 128, 0.5, 512, 8}};

  std::printf("== セル数・メモリ・影を引く回数（RGBA16F の 3D テクスチャ 3 枚: 散乱・積分・履歴）==\n");
  std::printf("設定  froxel          セル数      1 枚[MiB]  3 枚[MiB]  影を引く回数/フレーム\n");
  for (const Preset& p : presets) {
    const double cells = static_cast<double>(p.nx) * p.ny * p.nz;
    std::printf("%-4s  %3dx%3dx%3d  %10.0f   %8.2f   %8.2f   %12.1f M\n", p.name, p.nx, p.ny, p.nz, cells,
                cells * 8 / kMiB, 3 * cells * 8 / kMiB, cells * p.lights / 1e6);
  }
  const double base = 160.0 * 90 * 64;
  std::printf("標準(160x90x64)に対するセル数の比: 低 %.2f、高 %.2f、最高 %.2f\n", 80.0 * 45 * 32 / base,
              240.0 * 135 * 96 / base, 320.0 * 180 * 128 / base);

  std::printf("\n== セルの大きさ（横）とスライスの厚み: 標準 160x90x64、0.5〜128 m ==\n");
  const Preset& mid = presets[1];
  std::printf("距離[m]  セル幅[m]  セル高さ[m]  スライス厚[m]   セル幅 / 厚み\n");
  for (double z : {2.0, 5.0, 10.0, 30.0, 60.0, 100.0}) {
    const double w = 2 * z * kTanH / mid.nx;
    const double h = 2 * z * kTanV / mid.ny;
    const double k = std::log(z / mid.near_m) / std::log(mid.far_m / mid.near_m) * mid.nz;
    const double thick = SliceStart(mid, std::floor(k) + 1) - SliceStart(mid, std::floor(k));
    std::printf("%6.0f   %8.3f   %9.3f    %9.3f       %.2f\n", z, w, h, thick, w / thick);
  }

  std::printf("\n== 壁の厚み 0.2 m より、セルが大きくなる距離（光漏れの目安）==\n");
  for (const Preset& p : presets) {
    const double z = 0.2 * p.nx / (2 * kTanH);
    std::printf("%-4s (%3d 分割): %5.1f m より遠いと、1 セルが壁より厚い\n", p.name, p.nx, z);
  }

  std::printf("\n== 奥行きの分割: 近くを細かく取る効果（標準、指数 vs 線形）==\n");
  std::printf("線形なら 1 スライス = (128 - 0.5) / 64 = %.2f m。指数なら、距離 z のスライス厚は z x %.4f\n",
              (mid.far_m - mid.near_m) / mid.nz, std::pow(mid.far_m / mid.near_m, 1.0 / mid.nz) - 1.0);
  std::printf("2 m では指数 %.3f m（線形の %.0f 分の 1）、100 m では指数 %.2f m\n",
              2.0 * (std::pow(mid.far_m / mid.near_m, 1.0 / mid.nz) - 1.0),
              ((mid.far_m - mid.near_m) / mid.nz) / (2.0 * (std::pow(mid.far_m / mid.near_m, 1.0 / mid.nz) - 1.0)),
              100.0 * (std::pow(mid.far_m / mid.near_m, 1.0 / mid.nz) - 1.0));
  return 0;
}
```

```text title="実行結果"
== セル数・メモリ・影を引く回数（RGBA16F の 3D テクスチャ 3 枚: 散乱・積分・履歴）==
設定  froxel          セル数      1 枚[MiB]  3 枚[MiB]  影を引く回数/フレーム
低    80x 45x 32      115200       0.88       2.64            0.1 M
中   160x 90x 64      921600       7.03      21.09            2.8 M
高   240x135x 96     3110400      23.73      71.19           15.6 M
最高  320x180x128     7372800      56.25     168.75           59.0 M
標準(160x90x64)に対するセル数の比: 低 0.12、高 3.38、最高 8.00
```

```text title="実行結果（続き）"
== セルの大きさ（横）とスライスの厚み: 標準 160x90x64、0.5〜128 m ==
距離[m]  セル幅[m]  セル高さ[m]  スライス厚[m]   セル幅 / 厚み
     2      0.026       0.026        0.181       0.14
     5      0.064       0.064        0.431       0.15
    10      0.128       0.128        0.861       0.15
    30      0.385       0.385        2.656       0.14
    60      0.770       0.770        5.312       0.14
   100      1.283       1.283        8.933       0.14
```

```text title="実行結果（続き）"
== 壁の厚み 0.2 m より、セルが大きくなる距離（光漏れの目安）==
低  ( 80 分割):   7.8 m より遠いと、1 セルが壁より厚い
中  (160 分割):  15.6 m より遠いと、1 セルが壁より厚い
高  (240 分割):  23.4 m より遠いと、1 セルが壁より厚い
最高 (320 分割):  31.2 m より遠いと、1 セルが壁より厚い
```

```text title="実行結果（続き）"
== 奥行きの分割: 近くを細かく取る効果（標準、指数 vs 線形）==
線形なら 1 スライス = (128 - 0.5) / 64 = 1.99 m。指数なら、距離 z のスライス厚は z x 0.0905
2 m では指数 0.181 m（線形の 11 分の 1）、100 m では指数 9.05 m
```

## 長所と短所とコストの目安

Wronski の報告にあるのは、全体の約 1.1 ms と構築の約 0.43 ms だけです。プリセットごとの ms は資料にないので、書きません。各自の環境で測ってください。セル数に比例する部分（注入）と比例しない固定費（影の縮小）に分けて測れば、プリセットの選び方が決められます。

## よくあるミス

??? failure "奥行き方向に縞が出る"
    奥行きのスライスが粗い。スライス数を増やすか 3 次補間で読む。ディザを足して縞を細かいノイズにする。横方向の解像度を上げても縞は消えない。

??? failure "壁の向こうの光が漏れる"
    セルが壁より厚い。セルを小さくするかセル内で影を複数回引く。ジッターと履歴で平均する。

??? failure "遠景に急な境目が見える"
    froxel の最大距離で、フォグが急に切れている。最大距離の手前から `smoothstep` でフェードアウトさせ空気遠近法と混ぜる。

??? failure "フォグが重く、フレーム時間が伸びる"
    注入のコストが大きい。影付きライトを減らしセルに届かないライトを除外する。セル数を下げて時間蓄積で補う。

??? failure "フェードの手前で、フォグが不自然に濃くなる"
    froxel の透過率と空気遠近法の透過率を別々に掛けて重ねている。フェードの重みで透過率も散乱光も混ぜる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準は 160 × 90 × 64（720p の画素数と同じ）。コストは画面の解像度によらない。
    - [x] 重いのは注入。影付きライトの数とセル数に比例する。
    - [x] 奥行きの分割は粗い（標準で、セルは奥行きが横の約 7 倍）。縞はここから出る。
    - [x] 光漏れはセルが壁より厚くなる距離から。セル内の複数サンプルが効く。
    - [x] 遠くは空気遠近法に任せ境目はフェードで消す。

## 参考

- Bart Wronski, "Volumetric Fog: Unified, Compute Shader Based Solution to Atmospheric Scattering", ACM SIGGRAPH 2014 Courses, Advances in Real-Time Rendering in Games, 2014. <https://advances.realtimerendering.com/s2014/wronski/bwronski_volumetric_fog_siggraph2014.pdf>（スライドとノートの本文を全部読んだ。図とビデオ、付録のコード画像は読めていない）
- Sébastien Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015（取得できず、読んでいない）
- Karis, "High Quality Temporal Supersampling", SIGGRAPH 2014（読んでいない）
- C. Sigg, M. Hadwiger, "Fast Third-Order Texture Filtering", GPU Gems 2, Chapter 20, 2005（3 次補間の元。読んでいない。コードは一般的な形から書いた）

## 関連ページ

- [Volumetric Fog](index.md)
- [Froxels](froxel.md)
- [Temporal Accumulation](temporal.md)
- [Volume-Based God Rays](../god-rays/volume.md)
