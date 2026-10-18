---
title: Sun, Moon and Stars
tags:
  - 描画
---

# Sun, Moon and Stars

<strong>空には、太陽・月・星があります</strong>。<strong>太陽はディスク、月はテクスチャ付きの球、星は点の集まりで描きます</strong>。このページでは、天体の描き方を説明します。

!!! tip "ポイント"
    - 太陽 ＝ 明るいディスク ＋ 光の拡がり。
    - 月 ＝ 位相（満ち欠け）を持つ球。
    - 星 ＝ キューブマップ、または点の集まり。
    - 昼は、星が見えない（空の明るさに負ける）。

## 太陽・月・星
<strong>空の主役</strong>は<strong>太陽</strong>です。

### 太陽の円盤

<strong>太陽は視線と太陽の方向の角度が小さい所だけ、非常に明るい円盤</strong>です。<strong>実際の太陽の見た目の大きさは、約 0.53°</strong>（半径 約 0.265°）です。

```hlsl
float SunDisk(float3 view_dir, float3 sun_dir) {
  float cos_angle = dot(view_dir, sun_dir);
  float cos_radius = cos(radians(0.265));
  float edge = smoothstep(cos_radius - 0.00002, cos_radius, cos_angle);
  return edge * sun_intensity;
}
```

| 点 | 説明 |
| --- | --- |
| 角度を内積で | `acos` を避け、`cos` の値で比べる |
| 縁を少し滑らかに | ジャギーを防ぐ（TAA で滑らかになる） |
| HDR の強度 | 昼の太陽は空の 1 万倍以上明るい。ブルームが光る |
| <strong>周りのにじみ（コロナ）</strong> | 指数関数的に減る光を足す：`exp(-angle * k)` |
| 大きすぎる太陽は不自然 | 誇張しすぎない |

### 夕焼けの色

<strong>太陽が地平線に近づくと、光が大気を長く通る</strong>ので、<strong>青が散り尽くして、赤が残ります</strong>。太陽の色を高さに応じて変えるだけで、夕焼けの雰囲気が出ます。

```hlsl
float3 SunColor(float sun_height) {
  float t = saturate(sun_height * 4.0);
  return lerp(float3(1.0, 0.35, 0.1), float3(1.0, 0.95, 0.85), t);
}
```

<strong>正確には大気の透過率（光学的厚さ）から求めます</strong>（[Atmospheric Scattering](../scattering/index.md)）。

### 月と星

| 要素 | 内容 |
| --- | --- |
| 月 | 太陽と同様に円盤。月の満ち欠けは、太陽の向きとの角度から、球の陰影で表す |
| 星 | <strong>星空のキューブマップ（HDR）</strong>を回して貼る。空が暗いほど見える（昼の明るさで消える） |
| 夜空の明るさ | 月明かり・星明かりを環境光に足す |
| またたき | 星に時間でわずかな明滅 |

```hlsl
float3 stars = star_cubemap.Sample(linear_wrap, mul(view_dir, star_rotation)).rgb;
float night_factor = saturate(-sun_dir.y * 5.0);
float3 sky = day_sky + stars * night_factor;
```

<!-- fig:sun-arc:begin -->

<svg class="fig illust motion" data-fig="sun-arc" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-sun-arc" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">時刻から太陽の向きを決める: 1 日で半円を描く</text>
<line x1="130" y1="300" x2="650" y2="300" stroke="#94a3b8" stroke-width="2"/>
<path d="M160,300 A230,230 0 0 1 620,300" fill="none" stroke="#e2e8f0" stroke-width="3" stroke-dasharray="6 6"/>
<circle cx="160" cy="300" r="16" fill="#e5aa28"><animate attributeName="cx" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0690;0.0833;0.0977;0.1121;0.1264;0.1408;0.1552;0.1695;0.1839;0.1983;0.2126;0.2270;0.2414;0.2557;0.2701;0.2845;0.2989;0.3132;0.3276;0.3420;0.3563;0.3707;0.3851;0.3994;0.4138;0.4282;0.4425;0.4569;0.4713;0.4856;0.5000;0.5144;0.5287;0.5431;0.5575;0.5718;0.5862;0.6006;0.6149;0.6293;0.6437;0.6580;0.6724;0.6868;0.7011;0.7155;0.7299;0.7443;0.7586;1.0000" values="160;160;160.492;161.968;164.419;167.837;172.206;177.508;183.719;190.814;198.762;207.529;217.077;227.365;238.35;249.985;262.219;275;288.274;301.983;316.069;330.472;345.129;359.979;374.957;390;405.043;420.021;434.871;449.528;463.931;478.017;491.726;505;517.781;530.015;541.65;552.635;562.923;572.471;581.238;589.186;596.281;602.492;607.794;612.163;615.581;618.032;619.508;620;620"/><animate attributeName="cy" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0690;0.0833;0.0977;0.1121;0.1264;0.1408;0.1552;0.1695;0.1839;0.1983;0.2126;0.2270;0.2414;0.2557;0.2701;0.2845;0.2989;0.3132;0.3276;0.3420;0.3563;0.3707;0.3851;0.3994;0.4138;0.4282;0.4425;0.4569;0.4713;0.4856;0.5000;0.5144;0.5287;0.5431;0.5575;0.5718;0.5862;0.6006;0.6149;0.6293;0.6437;0.6580;0.6724;0.6868;0.7011;0.7155;0.7299;0.7443;0.7586;1.0000" values="300;300;284.957;269.979;255.129;240.472;226.069;211.983;198.274;185;172.219;159.985;148.35;137.365;127.077;117.529;108.762;100.814;93.719;87.508;82.206;77.837;74.419;71.968;70.492;70;70.492;71.968;74.419;77.837;82.206;87.508;93.719;100.814;108.762;117.529;127.077;137.365;148.35;159.985;172.219;185;198.274;211.983;226.069;240.472;255.129;269.979;284.957;300;300"/></circle>
<circle cx="620" cy="300" r="12" fill="#94a3b8" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7721;0.7724;1.0000" values="0;0;1;1"/></circle>
<text x="160" y="322" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">日の出（東）</text>
<text x="620" y="322" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">日没（西）</text>
<text x="390" y="50" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">正午</text>
<text x="390" y="370" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">6 時: 地平線(長い影・赤い空)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.2066;0.2069;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="370" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">9 時: 昇る途中(影は西に長い)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2066;0.2069;0.3446;0.3448;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="370" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">12 時: 最も高い(影は最短)<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3446;0.3448;0.4825;0.4828;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="370" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">15 時: 下がる途中<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4825;0.4828;0.6204;0.6207;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="370" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">18 時: 地平線に沈む → 月が昇る<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6204;0.6207;0.7583;0.7586;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:sun-arc:end -->

## 太陽・月・星を、空に置く

大気の散乱で、空の色が、決まっても、<strong>太陽の円盤</strong>、<strong>月</strong>、星が、無ければ、空は、のっぺりしています。これらの、天体を、空に、描き足します。

## 太陽の、位置

太陽の、<strong>方向</strong>（空の、どこに、あるか）は、<strong>時刻</strong>と、緯度・日付から、決まります。

### 簡易版：ゲームの、時刻から

ゲームでは、<strong>1 日を、数十分〜数時間</strong>に、縮めて、<strong>太陽を、一定の速さで、動かす</strong>ことが、多いです。時刻（0〜24）から、太陽の、天頂角と、方位角を、決めます。

```hlsl
// 時刻（0〜24）から、太陽の方向（光が来る向き）を求める。単純化: 東から昇り、西に沈む、円軌道。
float3 SunDirection(float hour, float latitude_rad, float axial_tilt_rad) {
  float hour_angle = (hour - 12.0) * (2.0 * 3.14159265 / 24.0);       // 正午を 0 とした、時角
  float elevation_noon = 3.14159265 * 0.5 - latitude_rad + axial_tilt_rad;   // 正午の、太陽の高さ（概算）
```

<strong>時角</strong>（<strong>正午を 0</strong> とした、時刻の、角度）が、地球の、自転を、表します。1 時間が、15°（360° / 24）です。

```hlsl
  // 太陽の、赤緯（日付による、高さの変化）。ここでは、axial_tilt で、近似。
  float declination = axial_tilt_rad;
  float sin_elevation = sin(latitude_rad) * sin(declination) + cos(latitude_rad) * cos(declination) * cos(hour_angle);
  float elevation = asin(sin_elevation);                               // 地平線からの、高さ
  float cos_azimuth = (sin(declination) - sin(elevation) * sin(latitude_rad)) / (cos(elevation) * cos(latitude_rad));
  float azimuth = acos(clamp(cos_azimuth, -1.0, 1.0));
  if (hour_angle > 0.0) azimuth = 2.0 * 3.14159265 - azimuth;          // 午後は、西側
```

<strong>緯度</strong>、<strong>赤緯</strong>（季節）、時角から、太陽の、高さ（仰角）と、方位が、天文学の、標準的な式で、決まります。ゲームでは、緯度や、赤緯を、固定して、時角だけを、動かすのが、普通です。

```hlsl
  // 方位角・仰角から、方向ベクトルへ（右手系、Y 上）。方位角は、北を 0、東を +90° とする。
  return float3(sin(azimuth) * cos(elevation), sin(elevation), -cos(azimuth) * cos(elevation));
}
```

<strong>天文学の、精密な、位置計算</strong>（日付、時刻、緯度・経度から）は、Meeus の『Astronomical Algorithms』（1991）に、<strong>詳しい式</strong>があります。リアルな、星空（実在の星座）を、再現したいときに、必要です。

## 太陽の、円盤

太陽は、<strong>視直径が、約 0.53°</strong> の、<strong>明るい円盤</strong>です。大気の、散乱だけでは、円盤が、描かれません。円盤を、明るさつきで、描き足します。

```hlsl
// 太陽の円盤: 視線と太陽の、角度が、太陽の視半径より、小さければ、非常に明るい。
float SunDisk(float3 view_dir, float3 sun_dir) {
  float cos_angle = dot(view_dir, sun_dir);
  const float kSunCosAngle = 0.99998;                    // cos(0.265°)。太陽の視半径は、約 0.265°
  // 縁を、少しだけ、なめらかにする（エイリアシング防止）。
  return smoothstep(kSunCosAngle - 0.00001, kSunCosAngle + 0.00001, cos_angle);
}
float3 sun_color = g_sun_luminance * SunDisk(view_dir, sun_dir);
```

`kSunCosAngle` の、`0.99998` は、<strong>太陽の視半径</strong>（約 0.265°）の、<strong>cos</strong> です。`smoothstep` で、縁を、わずかに、ぼかして、ギザギザを、防ぎます。太陽の、明るさは、非常に高い（空の、数万倍）ので、HDR で、描き、ブルームで、光らせます（[Post-Processing](../../postprocess/index.md)）。

### 大気を、通した、太陽の色

<strong>太陽が、低い</strong>（朝夕）と、<strong>光が、大気を、長く通る</strong>ので、赤く、暗くなります。透過率（[Transmittance](../scattering/transmittance.md)）を、掛けて、円盤の色を、決めます。

```hlsl
float3 sun_through_atmosphere = g_sun_luminance * SunTransmittance(g_camera_position, sun_dir);
float3 sun_disk_color = sun_through_atmosphere * SunDisk(view_dir, sun_dir);
```

<strong>夕日が、赤い、橙の円盤</strong>として、見えるのは、<strong>この透過率</strong>の、効果です。

## 月

月は、<strong>太陽と、同じ</strong>程度の、<strong>視直径</strong>（約 0.52°）ですが、ずっと、暗く（太陽の、約 40 万分の 1）、満ち欠けします。

| 要素 | 内容 |
| --- | --- |
| 円盤 | 太陽と、同じ方法。テクスチャ（月の表面の模様）を、貼る |
| 満ち欠け | 月の、照らされた部分は、太陽の、方向で決まる。球として、描き、太陽の光で、ライティングする |
| 位置 | 太陽と、独立に、動く（約 29.5 日の周期で、太陽との角度が、一巡） |
| 明るさ | 太陽の、約 0.0000025（満月で）。夜の空の、主な光源 |

```hlsl
// 月: 球として、太陽の光で、ライティング（満ち欠けは、自動的に、出る）。
float3 MoonColor(float3 view_dir, float3 moon_dir, float3 sun_dir, float moon_angular_radius) {
  float cos_angle = dot(view_dir, moon_dir);
  if (cos_angle < cos(moon_angular_radius)) return 0.0;               // 月の円盤の外
  // 円盤上の位置から、月の表面の法線を、復元する（球とみなす）。
  float3 moon_normal = MoonSurfaceNormal(view_dir, moon_dir, moon_angular_radius);
  float lit = saturate(dot(moon_normal, sun_dir));                     // 太陽に向いた面だけ、明るい
  float3 albedo = g_moon_texture.Sample(g_linear_clamp, MoonUv(moon_normal)).rgb;
  return albedo * lit * g_moon_luminance;
}
```

<strong>球としての、法線</strong>を、求めて、<strong>太陽の光で、ライティング</strong>するだけで、満ち欠けが、自然に、再現されます。太陽と、月の、位置関係（角度）が、満ち欠けを、決めるからです。

## 星空

星は、<strong>夜に、見える</strong>、<strong>無数の、点</strong>です。

| 方法 | 内容 |
| --- | --- |
| キューブマップ（星空の画像） | 実在の、星図（天球全体の画像）を、キューブマップに。簡単で、高品質 |
| ランダムな点 | 乱数で、点を散らす。実在の星座は、再現できないが、軽い |
| 星表（実在の、星の位置・明るさ） | 数千個の星の、データから、点を描く。星の明るさ・色を、反映 |

```hlsl
// 星空のキューブマップに、夜の明るさを、掛けて、足す。昼は、見えない（空が、明るすぎる）。
float night_factor = saturate(-sun_dir.y * 5.0 + 0.2);                // 太陽が、地平線の下に行くほど、1
float3 stars = g_star_cubemap.Sample(g_linear_clamp, view_dir).rgb * night_factor;
// 星は、空の明るさに、負けるので、空の輝度で、隠す（空が、明るいほど、星が、消える）。
float3 final_color = sky_color + stars * saturate(1.0 - Luminance(sky_color) * 10.0);
```

<strong>星が、昼間に、見えない</strong>のは、<strong>空の、明るさ</strong>に、かき消されるためです。空の輝度が、高いほど、星を、弱めると、薄明（夕暮れ）で、明るい星から、順に、見え始める様子が、再現できます。

### 星の、回転

<strong>地球の、自転</strong>で、星は、<strong>1 日に 1 回</strong>、夜空を、回ります。星空の、キューブマップを、時刻に応じて、回転させます。回転の、軸は、天の北極（北極星の方向）で、緯度に、応じて、傾きます。

```cpp
// 星空の、回転: 地球の自転（時角）と、観測者の緯度から、回転行列を作る。
Matrix star_rotation = Matrix::CreateRotationY(-hour_angle) * Matrix::CreateRotationX(latitude_rad - DirectX::XM_PIDIV2);
```

## 描く順序

| 順 | 描くもの |
| --- | --- |
| 1 | 星空（最も、奥） |
| 2 | 大気の散乱（空の色。星を、隠す） |
| 3 | 月、太陽の円盤 |
| 4 | 雲（[Clouds](../clouds/index.md)） |

<strong>星が、大気の、向こう</strong>にあるので、<strong>星を、先に描き</strong>、大気の、明るさで、隠します。太陽と月は、大気の、手前の、明るい点として、足します。

## よくあるミス

??? failure "昼なのに、星が透けて見える"
    <strong>空の明るさに応じて、星を弱める</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 太陽・月・星を、それぞれに合う方法で

## 参考

- Meeus, "Astronomical Algorithms", Willmann-Bell, 1991（太陽・月の位置の計算）
- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)
- Bruneton, Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum (EGSR 2008)
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Sky Models](index.md)
- [Day-Night Cycle](day-night.md)
