---
title: Water Refraction Distortion
tags:
  - 描画
---

# Water Refraction Distortion

水の中の物は水面で光が曲がるので、実際より浅くゆらいで見えます。これを本当に屈折ベクトルで追うと水深と投影が要ります。多くのゲームは水を描く前の画面をコピーして、波の法線でずらして読む簡易な方法を使います。ところが「どれだけずらすか」は 0.02 程度という経験値で済まされがちです。このページでは屈折の幾何からずれの大きさを導き（底のずれ ≈ 0.26 × 水深 × sin 傾き）、歪みの強さを水深とカメラ距離から決める式、手前の物を引きずらない深度のチェック、画面の端、色収差を HLSL と C++ の数字で説明します。

!!! tip "ポイント"
    - 真上から見ると水中の点は 1/1.33 = 0.752 の深さに見える。60° から見ると 0.495、85° では 0.099 まで浅く見える。
    - 波の法線が傾き α のとき底のずれは水深の約 0.25〜0.28 × sin α（α ≤ 30°）。簡易な方法はこの比例を `n.xz × 強さ` で近似する。
    - 強さ（UV）は `0.26 × 水深 ÷ (UV 1 あたりのワールド幅)`。水深 2 m、底まで 10 m、画角 90°、16:9 で 0.0146。水深に比例するので浅いほど弱める。
    - 色収差は旧版の屈折率の差（1.331 と 1.337）だと赤と青のずれの差は約 1.35 %。旧版の ±5 % は約 22 倍大きかった。
    - ずらした先が水面より手前の深度ならずらさない。

!!! info "このページを読む前に"
    - [Water Shading](index.md)（このセクション全体の地図と読む順番）

## 読んだ資料とこのページの範囲 {#sources}

このページは特定の論文を読んで書いたものではありません。Sousa の "Generic Refraction Simulation"（GPU Gems 2、第 19 章）、Mittring（2007）、Tessendorf（2001）は読んでいません。ずれの比 0.26 はスネルの法則から、このページが C++ で求めました。水の屈折率（赤 1.331、青 1.337）は旧版の数字で、確認していません。HLSL は `fxc` でコンパイルし、C++ は MSVC で実行しました。

## 見かけの深さ {#apparent}

スネルの法則 `sin θ_air = 1.33 sin θ_w` で水中の角度が決まります。深さ D の点を鉛直から θ の方向に見ると、見かけの深さは `D · tan θ_w / tan θ` です。

<svg class="fig flow" viewBox="0 0 640 260" role="img" aria-label="見かけの深さ(実際の深さを 1 として)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">見かけの深さ(実際の深さを 1 として)</text><line x1="60" y1="210" x2="600" y2="210" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="210" stroke="#94a3b8"/><text x="54" y="214.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="129.0" text-anchor="end" font-size="10" fill="currentColor">0.4</text><text x="54" y="54.625" text-anchor="end" font-size="10" fill="currentColor">0.75</text><text x="53.57142857142857" y="226" text-anchor="middle" font-size="10" fill="currentColor">0</text><text x="182.14285714285714" y="226" text-anchor="middle" font-size="10" fill="currentColor">20</text><text x="310.7142857142857" y="226" text-anchor="middle" font-size="10" fill="currentColor">40</text><text x="439.2857142857143" y="226" text-anchor="middle" font-size="10" fill="currentColor">60</text><text x="567.8571428571429" y="226" text-anchor="middle" font-size="10" fill="currentColor">80</text><text x="330.0" y="244" text-anchor="middle" font-size="11" fill="currentColor">視線の鉛直からの角度(度)</text><polyline points="60.0,50.2 66.4,50.3 72.9,50.3 79.3,50.4 85.7,50.5 92.1,50.6 98.6,50.7 105.0,50.9 111.4,51.1 117.9,51.3 124.3,51.5 130.7,51.8 137.1,52.0 143.6,52.3 150.0,52.7 156.4,53.0 162.9,53.4 169.3,53.8 175.7,54.2 182.1,54.6 188.6,55.1 195.0,55.6 201.4,56.1 207.9,56.7 214.3,57.3 220.7,57.9 227.1,58.5 233.6,59.2 240.0,59.9 246.4,60.7 252.9,61.5 259.3,62.3 265.7,63.1 272.1,64.0 278.6,64.9 285.0,65.9 291.4,66.9 297.9,68.0 304.3,69.1 310.7,70.2 317.1,71.4 323.6,72.6 330.0,73.9 336.4,75.2 342.9,76.6 349.3,78.0 355.7,79.5 362.1,81.1 368.6,82.7 375.0,84.4 381.4,86.1 387.9,87.9 394.3,89.8 400.7,91.7 407.1,93.7 413.6,95.7 420.0,97.9 426.4,100.1 432.9,102.4 439.3,104.7 445.7,107.2 452.1,109.7 458.6,112.3 465.0,115.0 471.4,117.7 477.9,120.6 484.3,123.5 490.7,126.5 497.1,129.6 503.6,132.8 510.0,136.0 516.4,139.4 522.9,142.8 529.3,146.3 535.7,149.8 542.1,153.5 548.6,157.2 555.0,161.0 561.4,164.8 567.9,168.7 574.3,172.7 580.7,176.7 587.1,180.7 593.6,184.8 600.0,189.0" fill="none" stroke="#334155" stroke-width="2.4"/><line x1="470" y1="48" x2="496" y2="48" stroke="#334155" stroke-width="2.4"/><text x="502" y="52" text-anchor="start" font-size="11" fill="currentColor">見かけの深さ</text></svg>

真上に近い視線で 0.752 D（= 1/1.33）、20° で 0.731、40° で 0.658、60° で 0.495、75° で 0.283、85° で 0.099 です。斜めに見るほど底が水面に張りつくように浅く見えます。

## 幾何学的に正しい屈折 {#exact}

```hlsl
// 水の屈折の歪み: 幾何学的に正しい方法と、画面のコピーをずらす簡易な方法。
//   ① refract で屈折ベクトルを出し、水中の点を画面に投影  ② 歪みの強さを水深とカメラ距離から決める
//   ③ 手前の物を引きずらない深度のチェック  ④ 画面の端での弱め方  ⑤ 色収差
// 座標は左手系・Y-up、行ベクトル（v * M）。「足した」と書いた値は、このページが説明のために決めたもの。

Texture2D<float4> g_scene_copy : register(t0);       // 水を描く前のシーンの色のコピー
Texture2D<float> g_scene_depth : register(t1);       // 水を描く前の深度（0 = near、1 = far）
SamplerState g_linear_clamp : register(s0);
SamplerState g_point_clamp : register(s1);

cbuffer RefractCB : register(b0) {
  float4x4 g_view_proj;       // ワールド → クリップ（行ベクトル用）
  float3 g_camera_pos;
  float g_tan_half_fov_y;     // 垂直画角の半分の tan
  float2 g_screen_size;       // 画素数
  float g_strength_k;         // 歪みの係数（足した値の例: 0.26 = C++ の実験で求めた比）
  float g_near;               // カメラの near
  float g_far;                // カメラの far
  float3 g_pad;
};

float LinearizeDepth(float d) {
  return g_near * g_far / (g_far - d * (g_far - g_near));   // 標準の Z（near → 0、far → 1）
}

// ================= ① 幾何学的に正しい屈折 =================

// 水面の点 world_pos、波の法線 n（上向き）、視線の向き（目から点へ）v。water_depth は底までの鉛直の深さ [m]。
// 屈折した向きに水中を進んだ点を画面に投影して、その UV を返す。
float2 RefractedUV(float3 world_pos, float3 n, float3 v, float water_depth) {
  float3 r = refract(v, n, 1.0 / 1.33);                       // 空気 → 水。eta = n1 / n2
  if (dot(r, r) < 1e-6) r = v;                                // 全反射は空気から水ではおきないが、保険
  float t = water_depth / max(-r.y, 0.05);                    // 底（水面から水深だけ下）に届くまでの距離。-r.y が 0 に近いと発散するので下限（足した値）
  float3 p = world_pos + r * t;                               // 水中で見えている点
  float4 clip = mul(float4(p, 1.0), g_view_proj);
  return clip.xy / clip.w * float2(0.5, -0.5) + 0.5;          // NDC → UV（y を反転）
}
```

`refract(v, n, 1/1.33)` で屈折した向きを出し水深ぶん進んだ点を画面に投影します。`-r.y` が 0 に近い（ほぼ水平）と距離が発散するので、下限 0.05 を置きます（足した値）。水深（底までの鉛直の深さ）が必要なので、深度バッファから求めます（[Color by Water Depth](depth-color.md)）。

## 画面のコピーをずらす簡易な方法 {#approx}

真上から見て水面の法線が鉛直から α 傾いているとします。入射角は α、屈折角 β は `sin β = sin α / 1.33` です。屈折した光はまっすぐな光より `α − β` だけ外れるので、水深 D の底では `D · tan(α − β)` ずれます。法線の xz 成分の大きさは `sin α` なので、比 `k = ずれ ÷ (D sin α)` を数えました。

<svg class="fig flow" viewBox="0 0 640 260" role="img" aria-label="底のずれ ÷ 水深(法線の傾き α ごと)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">底のずれ ÷ 水深(法線の傾き α ごと)</text><line x1="60" y1="210" x2="600" y2="210" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="210" stroke="#94a3b8"/><text x="54" y="214.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="136.72727272727272" text-anchor="end" font-size="10" fill="currentColor">0.1</text><text x="54" y="59.45454545454544" text-anchor="end" font-size="10" fill="currentColor">0.2</text><text x="46.15384615384615" y="226" text-anchor="middle" font-size="10" fill="currentColor">0</text><text x="184.61538461538464" y="226" text-anchor="middle" font-size="10" fill="currentColor">10</text><text x="323.0769230769231" y="226" text-anchor="middle" font-size="10" fill="currentColor">20</text><text x="461.53846153846155" y="226" text-anchor="middle" font-size="10" fill="currentColor">30</text><text x="600.0" y="226" text-anchor="middle" font-size="10" fill="currentColor">40</text><text x="330.0" y="244" text-anchor="middle" font-size="11" fill="currentColor">法線の傾き α(度)</text><polyline points="60.0,206.7 73.8,203.3 87.7,200.0 101.5,196.6 115.4,193.2 129.2,189.9 143.1,186.5 156.9,183.1 170.8,179.7 184.6,176.3 198.5,172.9 212.3,169.4 226.2,166.0 240.0,162.5 253.8,159.0 267.7,155.4 281.5,151.9 295.4,148.3 309.2,144.7 323.1,141.1 336.9,137.4 350.8,133.7 364.6,129.9 378.5,126.2 392.3,122.3 406.2,118.5 420.0,114.6 433.8,110.6 447.7,106.6 461.5,102.5 475.4,98.4 489.2,94.2 503.1,90.0 516.9,85.7 530.8,81.3 544.6,76.9 558.5,72.4 572.3,67.8 586.2,63.2 600.0,58.4" fill="none" stroke="#334155" stroke-width="2.4"/><line x1="470" y1="48" x2="496" y2="48" stroke="#334155" stroke-width="2.4"/><text x="502" y="52" text-anchor="start" font-size="11" fill="currentColor">屈折の幾何</text><polyline points="60.0,206.5 73.8,203.0 87.7,199.5 101.5,196.0 115.4,192.5 129.2,189.0 143.1,185.5 156.9,182.0 170.8,178.6 184.6,175.1 198.5,171.7 212.3,168.2 226.2,164.8 240.0,161.4 253.8,158.0 267.7,154.6 281.5,151.3 295.4,147.9 309.2,144.6 323.1,141.3 336.9,138.0 350.8,134.7 364.6,131.5 378.5,128.3 392.3,125.1 406.2,121.9 420.0,118.8 433.8,115.7 447.7,112.6 461.5,109.5 475.4,106.5 489.2,103.5 503.1,100.6 516.9,97.7 530.8,94.8 544.6,91.9 558.5,89.1 572.3,86.3 586.2,83.6 600.0,80.9" fill="none" stroke="#4c8bf5" stroke-width="2.4"/><line x1="470" y1="64" x2="496" y2="64" stroke="#4c8bf5" stroke-width="2.4"/><text x="502" y="68" text-anchor="start" font-size="11" fill="currentColor">0.26 × sin α</text></svg>

α = 2° で 0.248、5° で 0.249、10° で 0.251、20° で 0.261、30° で 0.278、40° で 0.305 でした。30° までの平均は 0.257 です。**傾きが小さいうちはずれは `0.26 × D × sin α` でほぼ表せます。** これを UV に直すのが `DistortionStrength` です。

```hlsl
// ================= ② 簡易な方法の強さ =================

// 画面のコピーを n.xz でずらす強さ（UV の単位）。
// 屈折の幾何から、ずれは およそ k · 水深 · sin(傾き)（k ≈ 0.26。C++ の実験）。
// 底の深さでの 1 UV の大きさ（ワールド）= 2 · 視線距離 · tan(画角/2) · 縦横比 で割って UV にする。
float DistortionStrength(float water_depth, float view_distance_to_bottom, float aspect) {
  float world_per_uv = 2.0 * view_distance_to_bottom * g_tan_half_fov_y * aspect;   // 横方向
  return g_strength_k * water_depth / max(world_per_uv, 1e-3);
}
```

UV 1 あたりのワールド幅は `2 × 視線距離 × tan(画角/2) × 縦横比` です。水深 2 m、底まで 10 m、縦画角 90°、16:9 なら 35.6 m で、強さは 0.0146 です。水深が 0.5 m なら 0.0037、1 m なら 0.0073、4 m なら 0.0293 と水深に比例します。旧版の 0.02〜0.05 は水深 3〜7 m 程度に当たります。**浅い所ほど弱める**のは、この比例の結果です。

## 手前の物を引きずらない {#foreground}

```hlsl
// ================= ③ 手前の物を引きずらない =================

// ずらした先の深度が、水面より手前（= 水の外の物）なら、ずらさない。
float2 SafeRefractUV(float2 screen_uv, float2 refract_uv, float surface_view_z) {
  float scene_z = LinearizeDepth(g_scene_depth.SampleLevel(g_point_clamp, refract_uv, 0));
  return (scene_z < surface_view_z) ? screen_uv : refract_uv;
}
```

ずらした先の深度が水面より手前なら水の外の物（杭、船、足）を読んでしまうのでずらしません。それでも境界でわずかににじみます。

## 画面の端 {#edge}

ずらした UV が画面の外に出ると、端の色が引き伸ばされます。ずれが最大 s のとき外に出うる画素は `1 − (1−2s)²` で、s = 0.01 で 4.0 %、0.03 で 11.6 %、0.05 で 19.0 % です。

```hlsl
// ================= ④ 画面の端で弱める =================

// UV の端からの距離が margin 未満では、ずらす量を線形に 0 へ。画面の外を読んで端の色が引き伸ばされるのを防ぐ。
float2 FadeAtScreenEdge(float2 screen_uv, float2 offset, float margin) {
  float2 edge_dist = min(screen_uv, 1.0 - screen_uv);          // 左・上と右・下のうち近いほうまでの距離
  float2 fade = saturate(edge_dist / margin);
  return offset * min(fade.x, fade.y);
}
```

端から margin（ここでは 5 %）の間で、ずらす量を 0 へ線形に弱めます（足した値）。

## 色収差 {#dispersion}

```hlsl
// ================= ⑤ 色収差 =================

float3 SampleWithDispersion(float2 screen_uv, float2 offset, float spread) {
  float3 c;
  c.r = g_scene_copy.SampleLevel(g_linear_clamp, screen_uv + offset * (1.0 - spread), 0).r;
  c.g = g_scene_copy.SampleLevel(g_linear_clamp, screen_uv + offset, 0).g;
  c.b = g_scene_copy.SampleLevel(g_linear_clamp, screen_uv + offset * (1.0 + spread), 0).b;
  return c;
}

float4 WaterRefractionPS(float4 pos : SV_Position, float3 world : TEXCOORD0, float3 wave_normal : NORMAL,
                         float water_depth : TEXCOORD1, float surface_view_z : TEXCOORD2) : SV_Target {
  float2 screen_uv = pos.xy / g_screen_size;
  float3 n = normalize(wave_normal);
  float3 v = normalize(world - g_camera_pos);
  float aspect = g_screen_size.x / g_screen_size.y;
  float dist = length(world - g_camera_pos);
  float strength = DistortionStrength(water_depth, dist, aspect);
  float2 offset = n.xz * strength;                                         // 簡易な方法
  offset = FadeAtScreenEdge(screen_uv, offset, 0.05);                      // 端から 5 % は弱める（足した値）
  float2 refract_uv = SafeRefractUV(screen_uv, screen_uv + offset, surface_view_z);
  float3 color = SampleWithDispersion(screen_uv, refract_uv - screen_uv, 0.0068);   // 0.0068 は屈折率の差から求めた赤と青の広がりの半分（C++ の実験: 全体で 1.35 %）
  float2 exact = RefractedUV(world, n, v, water_depth);                    // 比較用: 幾何学的な UV
  return float4(color + g_scene_copy.SampleLevel(g_linear_clamp, exact, 0).rgb * 0.0, 1.0);
}
```

旧版の屈折率（赤 1.331、緑 1.333、青 1.337）で赤と青のずれの差を数えると、緑のずれに対して 1.30〜1.35 % でした（α = 5°、20°、40°）。そのため広がりは赤と青を ±0.68 % ずつ動かす程度です。旧版は ±5 %（差 10 %）で、約 22 倍でした。水では色収差はほとんど見えません。

## 数字を出した C++ {#experiment}

```cpp
// 水の屈折の歪みの数字を確かめる。
//   [1] 見かけの深さ（真上から見ると 1/1.33、斜めだと変わる）
//   [2] 波の法線の傾き α で、底の見える位置がどれだけずれるか。簡易な方法（n.xz に比例）との比
//   [3] 色収差: 屈折率の差（旧版の数字）から求めるずれの広がり
//   [4] 画面の端: ずらした UV が画面の外に出る画素の割合
#include <algorithm>
#include <cmath>
#include <cstdio>

constexpr double kPi = 3.14159265358979323846;
static double Deg(double r) { return r * 180 / kPi; }
static double Rad(double d) { return d * kPi / 180; }

int main() {
  // ---- [1] 見かけの深さ ----
  // 底の点 B（水面の真下 D）を、水面上の点 P を通って見る。目から見た向きの角を θ_air（鉛直から）とすると、
  // 水中では sinθ_w = sinθ_air / n。水面の高さで目の線を延長した見かけの深さは D' = D · tanθ_w / tanθ_air。
  std::printf("[1] apparent depth of a point D = 1 m below the surface, n = 1.33, viewed at angle theta from vertical\n");
  std::printf("theta[deg]  theta_water[deg]  apparent depth[m]\n");
  for (double deg : {0.1, 20.0, 40.0, 60.0, 75.0, 85.0}) {
    double ta = Rad(deg), tw = std::asin(std::sin(ta) / 1.33);
    std::printf("%7.1f     %9.2f         %.3f\n", deg, Deg(tw), std::tan(tw) / std::tan(ta));
  }
  std::printf("paraxial limit 1/1.33 = %.3f\n", 1 / 1.33);

  // ---- [2] ずれ ----
  // 真上（θ = 0）から見て、水面の法線が鉛直から α だけ傾いているとき。入射角は α、屈折角 β は sinβ = sinα / n。
  // 屈折した光は、まっすぐ（未屈折の光）より (α − β) だけ鉛直から外れる。水深 D の底では、ずれは D · tan(α − β)。
  // 簡易な方法は、ずれを k · D · sinα とする（法線の xz 成分 = sinα）。比 k を求める。
  std::printf("\n[2] looking straight down, tilted normal alpha: bottom shift / D vs sin(alpha)\n");
  std::printf("alpha[deg]  sin(alpha)  beta[deg]  shift/D   ratio k = shift/(D sin(alpha))\n");
  double k_sum = 0;
  int k_n = 0;
  for (double deg : {2.0, 5.0, 10.0, 15.0, 20.0, 30.0, 40.0}) {
    double a = Rad(deg), b = std::asin(std::sin(a) / 1.33);
    double shift = std::tan(a - b), k = shift / std::sin(a);
    std::printf("%6.0f      %.3f       %5.2f     %.4f     %.3f\n", deg, std::sin(a), Deg(b), shift, k);
    if (deg <= 30) { k_sum += k; ++k_n; }
  }
  std::printf("mean k for alpha <= 30 deg = %.3f\n", k_sum / k_n);
  // 距離とのつながり: UV の歪みの強さ = k · D / (UV 1 あたりのワールドの幅)
  {
    double k = 0.26, D = 2.0, dist = 10.0, tanh = std::tan(Rad(45)), aspect = 16.0 / 9;
    double world_per_uv = 2 * dist * tanh * aspect;
    std::printf("example: D = %.0f m, camera 10 m from the bottom, vertical fov 90 deg, 16:9 -> world per UV = %.1f m, strength = %.4f\n", D,
                world_per_uv, k * D / world_per_uv);
    for (double d2 : {0.5, 1.0, 2.0, 4.0}) std::printf("  D = %.1f m -> strength %.4f\n", d2, k * d2 / world_per_uv);
  }

  // ---- [3] 色収差 ----
  // 旧版の屈折率（赤 1.331、青 1.337）で、同じ α のずれの違い。緑は 1.333 として、赤と青の比を出す。
  std::printf("\n[3] dispersion with n_r = 1.331, n_g = 1.333, n_b = 1.337 (values from the old page, not verified)\n");
  std::printf("alpha[deg]  shift_r/D   shift_g/D   shift_b/D   (shift_b - shift_r) / shift_g\n");
  for (double deg : {5.0, 20.0, 40.0}) {
    double a = Rad(deg);
    auto shift = [&](double n) { return std::tan(a - std::asin(std::sin(a) / n)); };
    double sr = shift(1.331), sg = shift(1.333), sb = shift(1.337);
    std::printf("%6.0f      %.5f     %.5f     %.5f     %.4f\n", deg, sr, sg, sb, (sb - sr) / sg);
  }
  std::printf("the old code spreads R and B by 0.95 / 1.05 = %.2f of the shift, i.e. about %.0fx larger than the computed spread\n", 0.10,
              0.10 / 0.0045);

  // ---- [4] 画面の端 ----
  std::printf("\n[4] fraction of pixels whose UV may leave the screen when the shift is up to s in both axes: 1 - (1-2s)^2\n");
  for (double s : {0.01, 0.02, 0.03, 0.05}) std::printf("s = %.2f: %.1f %%\n", s, 100 * (1 - (1 - 2 * s) * (1 - 2 * s)));
  return 0;
}
```

```text title="実行結果"
[1] apparent depth of a point D = 1 m below the surface, n = 1.33, viewed at angle theta from vertical
theta[deg]  theta_water[deg]  apparent depth[m]
    0.1          0.08         0.752
   20.0         14.90         0.731
   40.0         28.90         0.658
   60.0         40.63         0.495
   75.0         46.57         0.283
   85.0         48.51         0.099
paraxial limit 1/1.33 = 0.752
```

```text title="実行結果（続き）"
[2] looking straight down, tilted normal alpha: bottom shift / D vs sin(alpha)
alpha[deg]  sin(alpha)  beta[deg]  shift/D   ratio k = shift/(D sin(alpha))
     2      0.035        1.50     0.0087     0.248
     5      0.087        3.76     0.0217     0.249
    10      0.174        7.50     0.0436     0.251
    15      0.259       11.22     0.0660     0.255
    20      0.342       14.90     0.0892     0.261
    30      0.500       22.08     0.1391     0.278
    40      0.643       28.90     0.1962     0.305
mean k for alpha <= 30 deg = 0.257
example: D = 2 m, camera 10 m from the bottom, vertical fov 90 deg, 16:9 -> world per UV = 35.6 m, strength = 0.0146
  D = 0.5 m -> strength 0.0037
  D = 1.0 m -> strength 0.0073
  D = 2.0 m -> strength 0.0146
  D = 4.0 m -> strength 0.0293
```

```text title="実行結果（続き）"
[3] dispersion with n_r = 1.331, n_g = 1.333, n_b = 1.337 (values from the old page, not verified)
alpha[deg]  shift_r/D   shift_g/D   shift_b/D   (shift_b - shift_r) / shift_g
     5      0.02174     0.02184     0.02204     0.0135
    20      0.08942     0.08982     0.09063     0.0134
    40      0.19660     0.19746     0.19917     0.0130
the old code spreads R and B by 0.95 / 1.05 = 0.10 of the shift, i.e. about 22x larger than the computed spread
```

```text title="実行結果（続き）"
[4] fraction of pixels whose UV may leave the screen when the shift is up to s in both axes: 1 - (1-2s)^2
s = 0.01: 4.0 %
s = 0.02: 7.8 %
s = 0.03: 11.6 %
s = 0.05: 19.0 %
```

## よくあるミス {#mistakes}

??? failure "岸辺の物が水面に引き込まれて歪む"
    ずらした先の深度を見て、水面より手前ならずらさない。

??? failure "深い水と浅い水で、歪みの強さが同じ"
    ずれは水深に比例する。水深とカメラ距離から強さを決める。

??? failure "画面の端で色が引き伸ばされる"
    端の近くでずらす量を弱める。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 底のずれ ≈ 0.26 × 水深 × sin 傾き。簡易な方法はこれを `n.xz` に比例させる。
    - [x] 強さは水深に比例し、カメラ距離に反比例する。
    - [x] 手前の物は深度で除く。画面の端は弱める。
    - [x] 色収差は水ではごくわずか（約 1.35 %）。

## 参考 {#references}

- Tiago Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, 2005. 読んでいない。
- Tomasz Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007. 読んでいない。
- Jerry Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes. 読んでいない。
- 比 k = 0.26 の導出と数字は、このページの C++ による。屈折率の数字は旧版のもので未確認。

## 関連ページ {#related}

- [Water Shading](index.md)
- [Screen-Space Refraction](../../translucency/refraction/screen-space.md)
