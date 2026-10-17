---
title: 雲
tags:
  - 描画
---

# 雲

**雲は空の表情を決める主役**です。**板に雲の絵を貼る**簡単な方法から、**雲の体積そのものをレイマーチで描く**方法まで、**段階があります**。**現代のゲームでは、雲の「密度」を 3D ノイズで作り、視線に沿って光の散乱を積分する**方式が**標準**です。このページでは、**雲の密度モデル（ノイズと高さの形）・レイマーチ・光の計算（Beer の法則・Powder 効果・位相関数）・影・時間蓄積による高速化・簡易な代替**を説明します。

!!! tip "ポイント"
    - 雲 ＝ <strong>空中に浮かぶ「密度」の塊</strong>。<strong>光を散らす水滴の集まり</strong>。
    - 描画 ＝ <strong>視線に沿って雲の層を歩き（レイマーチ）、密度から光と透過率を積む</strong>。
    - 密度は<strong>3D ノイズ（Perlin–Worley）の重ね合わせ</strong> × <strong>高さ方向の形</strong> × <strong>天気マップ（どこに雲があるか）</strong>。
    - 光は<strong>太陽方向へ数回サンプルして、雲の厚みを調べる</strong>（<strong>Beer の法則</strong>）。<strong>Powder 効果</strong>で<strong>縁が暗くなる</strong>のを表現。
    - 雲は<strong>前方に強く光を散らす</strong>（<strong>二重ローブの位相関数</strong>）。<strong>太陽の周りが銀色に光る</strong>。
    - 重いので<strong>解像度を落として描き、時間蓄積</strong>で<strong>補う</strong>。

## 雲の描き方の段階

| 方式 | 内容 | 特徴 |
| --- | --- | --- |
| **スカイボックスの絵** | **雲の絵を空に貼る** | **最も安い。動かない・光が変わらない** |
| <strong>板ポリ（ビルボード）</strong> | **雲の絵を貼った板を空に多数置く** | **動かせる。近づくと板だと分かる** |
| <strong>レイマーチ（ボリューム）</strong> | **雲の体積を視線に沿って積分** | **リアル。重い** |

## 雲の層

**積雲（もこもこした雲）などの雲は地面から離れた高さ 1.5〜4 km 程度の層**にできます。**空に「雲の層」（地表からの高さの範囲）を決め、その中だけを描きます**。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="雲の層">
<text x="20" y="24" class="fig-title">雲の層：地表から見て、ある高さの範囲にだけ雲がある</text>
<path d="M40,230 A400,400 0 0 1 740,230" fill="none" stroke="#4c8bf5" stroke-opacity="0.3" stroke-width="2"/>
<path d="M80,230 A340,340 0 0 1 700,230" fill="#e5aa28" fill-opacity="0.12" stroke="none"/>
<path d="M120,230 A280,280 0 0 1 660,230" fill="#fff" fill-opacity="0.0" stroke="none"/>
<path d="M40,230 A400,400 0 0 1 740,230 L700,230 A340,340 0 0 0 80,230 Z" fill="#8a8a8a" fill-opacity="0.2"/>
<line x1="40" y1="230" x2="740" y2="230" stroke="currentColor" stroke-opacity="0.5"/>
<circle cx="390" cy="230" r="6" fill="#e5484d"/><text x="400" y="250" style="font-size:12px">観測者</text>
<text x="300" y="60" style="font-size:12px;font-weight:700">雲の層（高さ 1.5〜4 km）</text>
<ellipse cx="260" cy="110" rx="50" ry="22" fill="#fff" fill-opacity="0.75"/><ellipse cx="300" cy="100" rx="40" ry="26" fill="#fff" fill-opacity="0.8"/>
<ellipse cx="500" cy="95" rx="55" ry="24" fill="#fff" fill-opacity="0.75"/><ellipse cx="540" cy="108" rx="40" ry="20" fill="#fff" fill-opacity="0.7"/>
</svg>

**視線が雲の層の内側の球殻と外側の球殻のどちらにぶつかるかを求めて、その間だけレイマーチ**します（[大気散乱](scattering.md)の球との交差と同じ）。

## 密度のモデル

**雲の密度は複数の要素を掛け合わせて作ります**。

| 要素 | 役割 |
| --- | --- |
| <strong>天気マップ（2D）</strong> | **どこに雲があるか（被覆率）・どんな種類か** |
| <strong>高さの形（ゲイン）</strong> | **層の下と上で薄くなる**（**雲の底は平ら、頂は丸い**） |
| **基本形の 3D ノイズ** | **雲全体の大まかな塊**（低周波。Perlin–Worley） |
| **ディテールの 3D ノイズ** | **塊の縁の細かい凹凸**（高周波。Worley） |
| **風の流れ** | **ノイズの座標を時間で動かす** |

```hlsl
float CloudDensity(float3 position, float height_fraction) {
  float coverage = weather_map.SampleLevel(linear_wrap, position.xz * weather_scale, 0).r;
  float height_gradient = saturate(Remap(height_fraction, 0.0, 0.1, 0.0, 1.0))
                        * saturate(Remap(height_fraction, 0.6, 1.0, 1.0, 0.0));

  float3 shape_uvw = position * shape_scale + wind * time;
  float4 noise = shape_noise.SampleLevel(linear_wrap, shape_uvw, 0);
  float shape_fbm = dot(noise.gba, float3(0.5, 0.25, 0.125)) ;
  float base = Remap(noise.r, shape_fbm - 1.0, 1.0, 0.0, 1.0);

  float density = Remap(base * height_gradient, 1.0 - coverage, 1.0, 0.0, 1.0) * coverage;

  if (density > 0.0) {
    float3 detail_uvw = position * detail_scale + wind * time * 2.0;
    float3 detail = detail_noise.SampleLevel(linear_wrap, detail_uvw, 0).rgb;
    float detail_fbm = dot(detail, float3(0.5, 0.25, 0.125));
    float detail_mix = lerp(detail_fbm, 1.0 - detail_fbm, saturate(height_fraction * 5.0));
    density = Remap(density, detail_mix * detail_strength, 1.0, 0.0, 1.0);
  }
  return max(density, 0.0);
}

float Remap(float v, float a, float b, float c, float d) {
  return c + (v - a) / (b - a) * (d - c);
}
```

| 点 | 説明 |
| --- | --- |
| **`Remap`** | **値の範囲を変換する道具**。**閾値で塊を切り出すのに便利** |
| **`height_fraction`** | **層の下端を 0、上端を 1 とした位置** |
| **`height_gradient`** | **下と上で薄くなる山型**（底が柔らかく、頂が丸く） |
| <strong>被覆率（coverage）</strong> | **大きいほど雲が多い** |
| **ディテールは密度がある所だけ** | **`if (density > 0)` で計算を省く** |
| **3D ノイズは事前生成** | **128³ と 32³ のテクスチャ**（Perlin と Worley を重ねる） |

**ノイズ テクスチャ**は**事前に生成**します（Perlin ノイズに Worley ノイズを重ね、4 チャンネルに異なる周波数を入れる）。

## レイマーチ

**視線に沿って、雲の層の中を一定のステップで進み、各点の密度から光を積みます**。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="雲のレイマーチ">
<text x="20" y="24" class="fig-title">視線に沿って進み、各点で「太陽に向けても少し進んで」光の量を調べる</text>
<rect x="260" y="60" width="300" height="110" rx="40" fill="#fff" fill-opacity="0.35" stroke="currentColor" stroke-opacity="0.4"/>
<circle cx="120" cy="220" r="6" fill="#e5484d"/><text x="90" y="244" style="font-size:12px">カメラ</text>
<line x1="120" y1="220" x2="540" y2="80" stroke="currentColor" stroke-width="2"/>
<g fill="#2ea043"><circle cx="300" cy="160" r="4"/><circle cx="360" cy="140" r="4"/><circle cx="420" cy="120" r="4"/><circle cx="480" cy="100" r="4"/></g>
<text x="300" y="186" style="font-size:11px;fill:#2ea043">視線のサンプル点</text>
<g stroke="#e5aa28" stroke-dasharray="4 3"><line x1="360" y1="140" x2="440" y2="40"/><line x1="420" y1="120" x2="500" y2="28"/></g>
<circle cx="640" cy="50" r="14" fill="#e5aa28"/><text x="620" y="82" style="font-size:12px">太陽</text>
<text x="460" y="236" style="font-size:12px">各サンプルから太陽へ 4〜6 回、密度を足して「厚み」を測る</text>
</svg>

```hlsl
float4 MarchClouds(float3 ray_origin, float3 ray_dir, float t_start, float t_end, float3 sun_dir) {
  float step_length = (t_end - t_start) / kStepCount;
  float jitter = BlueNoise(input.position.xy);
  float transmittance = 1.0;
  float3 scattered = 0;

  for (int i = 0; i < kStepCount; ++i) {
    float t = t_start + (i + jitter) * step_length;
    float3 position = ray_origin + ray_dir * t;
    float height_fraction = HeightFraction(position);
    float density = CloudDensity(position, height_fraction);
    if (density <= 0.001) continue;

    float light_optical_depth = LightMarch(position, sun_dir);
    float3 sun_light = sun_color * exp(-light_optical_depth * extinction);
    sun_light *= PowderEffect(density);
    float phase = CloudPhase(dot(ray_dir, sun_dir));
    float3 ambient = ambient_color * lerp(0.4, 1.0, height_fraction);

    float3 luminance = (sun_light * phase + ambient) * density * scattering_coeff;
    float step_transmittance = exp(-density * extinction * step_length);
    float3 integrated = (luminance - luminance * step_transmittance) / max(density * extinction, 1e-5);

    scattered += integrated * transmittance;
    transmittance *= step_transmittance;
    if (transmittance < 0.01) break;
  }
  return float4(scattered, transmittance);
}
```

| 点 | 説明 |
| --- | --- |
| **ステップ数** | **近くは細かく、遠くは粗く**（32〜64 段）。**雲に入ったら細かく** |
| **ブルー ノイズのジッター** | **開始位置をずらして縞を消す。時間蓄積と相性が良い** |
| **早期終了** | **透過率が 1 % を切ったら打ち切る**（不透明になった） |
| **密度 0 は飛ばす** | **何もない空間を粗いステップで進み、雲に当たったら細かく**にする工夫 |
| **戻り値** | **散乱光 RGB と透過率**（**空の上に合成**） |

<!-- fig:cloud-raymarch:begin -->

<svg class="fig illust motion" data-fig="cloud-raymarch" viewBox="0 0 780 380" role="img"><rect x="0" y="0" width="780" height="380" rx="14" fill="#ffffff"/>
<defs><marker id="arr-cloud-raymarch" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">雲のレイマーチ:視線を少しずつ進んで、密度から光を積み上げる</text>
<ellipse cx="430" cy="170" rx="70" ry="38" fill="#cbd5e1" opacity="0.8"/>
<ellipse cx="500" cy="150" rx="60" ry="34" fill="#cbd5e1" opacity="0.8"/>
<ellipse cx="360" cy="190" rx="50" ry="28" fill="#cbd5e1" opacity="0.8"/>
<ellipse cx="460" cy="200" rx="65" ry="30" fill="#cbd5e1" opacity="0.8"/>
<rect x="40" y="60" width="520" height="260" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="70" cy="300" r="8" fill="#e5484d"/>
<text x="84" y="292" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">カメラ</text>
<text x="52" y="78" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">雲（上から見た断面）</text>
<line x1="70" y1="300" x2="550" y2="90" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="77.5" cy="296.72" r="3.0" fill="#ffffff" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;1.0000" values="0;0;1;1"/></circle>
<circle cx="92.5" cy="290.16" r="3.0" fill="#ffffff" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0880;0.0883;1.0000" values="0;0;1;1"/></circle>
<circle cx="107.5" cy="283.59" r="3.0" fill="#ffffff" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1097;0.1100;1.0000" values="0;0;1;1"/></circle>
<circle cx="122.5" cy="277.03" r="3.0" fill="#ffffff" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1313;0.1317;1.0000" values="0;0;1;1"/></circle>
<circle cx="137.5" cy="270.47" r="3.000000000000001" fill="#ffffff" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1530;0.1533;1.0000" values="0;0;1;1"/></circle>
<circle cx="152.5" cy="263.91" r="3.0000000000000373" fill="#ffffff" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1747;0.1750;1.0000" values="0;0;1;1"/></circle>
<circle cx="167.5" cy="257.34" r="3.0000000000016573" fill="#ffffff" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1963;0.1967;1.0000" values="0;0;1;1"/></circle>
<circle cx="182.5" cy="250.78" r="3.000000000071172" fill="#ffffff" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2180;0.2183;1.0000" values="0;0;1;1"/></circle>
<circle cx="197.5" cy="244.22" r="3.000000003276357" fill="#ffffff" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2397;0.2400;1.0000" values="0;0;1;1"/></circle>
<circle cx="212.5" cy="237.66" r="3.000000143371633" fill="#ffffff" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2613;0.2617;1.0000" values="0;0;1;1"/></circle>
<circle cx="227.5" cy="231.09" r="3.000004862640613" fill="#ffffff" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2830;0.2833;1.0000" values="0;0;1;1"/></circle>
<circle cx="242.5" cy="224.53" r="3.0001142391235884" fill="#ffffff" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3047;0.3050;1.0000" values="0;0;1;1"/></circle>
<circle cx="257.5" cy="217.97" r="3.001782349163526" fill="#ffffff" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3263;0.3267;1.0000" values="0;0;1;1"/></circle>
<circle cx="272.5" cy="211.41" r="3.018202748881747" fill="#fefeff" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3480;0.3483;1.0000" values="0;0;1;1"/></circle>
<circle cx="287.5" cy="204.84" r="3.121141615045074" fill="#fbfcfc" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3697;0.3700;1.0000" values="0;0;1;1"/></circle>
<circle cx="302.5" cy="198.28" r="3.525429172519642" fill="#eff0f2" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3913;0.3917;1.0000" values="0;0;1;1"/></circle>
<circle cx="317.5" cy="191.72" r="4.492458229013869" fill="#d1d5da" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4130;0.4133;1.0000" values="0;0;1;1"/></circle>
<circle cx="332.5" cy="185.16" r="5.8187129517628255" fill="#a9afb9" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4347;0.4350;1.0000" values="0;0;1;1"/></circle>
<circle cx="347.5" cy="178.59" r="6.698357962576185" fill="#8e96a3" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4563;0.4567;1.0000" values="0;0;1;1"/></circle>
<circle cx="362.5" cy="172.03" r="6.782650080884132" fill="#8b94a0" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4780;0.4783;1.0000" values="0;0;1;1"/></circle>
<circle cx="377.5" cy="165.47" r="6.697575715515082" fill="#8e96a3" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4997;0.5000;1.0000" values="0;0;1;1"/></circle>
<circle cx="392.5" cy="158.91" r="6.880029651283381" fill="#88919e" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5213;0.5217;1.0000" values="0;0;1;1"/></circle>
<circle cx="407.5" cy="152.34" r="6.981753202970777" fill="#858e9b" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5430;0.5433;1.0000" values="0;0;1;1"/></circle>
<circle cx="422.5" cy="145.78" r="6.669994495565467" fill="#8e97a3" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5647;0.5650;1.0000" values="0;0;1;1"/></circle>
<circle cx="437.5" cy="139.22" r="6.125475184839541" fill="#9fa6b1" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5863;0.5867;1.0000" values="0;0;1;1"/></circle>
<circle cx="452.5" cy="132.66" r="5.637084001985818" fill="#aeb4bd" stroke="#475569" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.6080;0.6083;1.0000" values="0;0;1;1"/></circle>
<text x="610" y="82" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">光が通り抜ける割合（透過率）</text>
<rect x="610" y="96" width="140" height="22" fill="#f1f5f9" stroke="#94a3b8"/>
<rect x="610" y="96" width="140" height="22" fill="#2563eb"><animate attributeName="width" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0883;0.1100;0.1317;0.1533;0.1750;0.1967;0.2183;0.2400;0.2617;0.2833;0.3050;0.3267;0.3483;0.3700;0.3917;0.4133;0.4350;0.4567;0.4783;0.5000;0.5217;0.5433;0.5650;0.5867;0.6083;1.0000" values="140;140;140;140;140;140;140;140;140;140;140;140;140;139.98;139.74;138.2;131.7;114.86;88.71;63.2;44.68;31.84;22.31;15.49;11.06;8.31;6.52;6.52"/></rect>
<text x="610" y="168" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">積み上がった光（雲の明るさ）</text>
<rect x="610" y="182" width="140" height="22" fill="#f1f5f9" stroke="#94a3b8"/>
<rect x="610" y="182" width="0" height="22" fill="#e5aa28"><animate attributeName="width" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0883;0.1100;0.1317;0.1533;0.1750;0.1967;0.2183;0.2400;0.2617;0.2833;0.3050;0.3267;0.3483;0.3700;0.3917;0.4133;0.4350;0.4567;0.4783;0.5000;0.5217;0.5433;0.5650;0.5867;0.6083;1.0000" values="0;0;0;0;0;0;0;0;0;0;0;0;0;0.02;0.16;1.13;5.19;15.71;32.06;48;59.57;67.6;73.56;77.82;80.59;82.31;83.42;83.42"/></rect>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 1.00<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;0.0880;0.0883;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 1.00<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0880;0.0883;0.1097;0.1100;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 1.00<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1097;0.1100;0.1313;0.1317;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 1.00<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1313;0.1317;0.1530;0.1533;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 1.00<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1530;0.1533;0.1747;0.1750;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 1.00<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1747;0.1750;0.1963;0.1967;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 1.00<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1963;0.1967;0.2180;0.2183;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 1.00<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2180;0.2183;0.2397;0.2400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 1.00<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2397;0.2400;0.2613;0.2617;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 1.00<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2613;0.2617;0.2830;0.2833;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 1.00<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2830;0.2833;0.3047;0.3050;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 1.00<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3047;0.3050;0.3263;0.3267;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 1.00<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3263;0.3267;0.3480;0.3483;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 1.00<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3480;0.3483;0.3697;0.3700;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 0.99<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3697;0.3700;0.3913;0.3917;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 0.94<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3913;0.3917;0.4130;0.4133;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 0.82<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4130;0.4133;0.4347;0.4350;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 0.63<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4347;0.4350;0.4563;0.4567;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 0.45<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4563;0.4567;0.4780;0.4783;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 0.32<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4780;0.4783;0.4997;0.5000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 0.23<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4997;0.5000;0.5213;0.5217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 0.16<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5213;0.5217;0.5430;0.5433;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 0.11<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5430;0.5433;0.5647;0.5650;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 0.08<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5647;0.5650;0.5863;0.5867;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 0.06<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5863;0.5867;0.6080;0.6083;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="250" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">透過率 T = 0.05<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.6080;0.6083;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 1（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;0.0880;0.0883;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 2（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0880;0.0883;0.1097;0.1100;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 3（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1097;0.1100;0.1313;0.1317;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 4（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1313;0.1317;0.1530;0.1533;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 5（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1530;0.1533;0.1747;0.1750;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 6（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1747;0.1750;0.1963;0.1967;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 7（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1963;0.1967;0.2180;0.2183;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 8（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2180;0.2183;0.2397;0.2400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 9（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2397;0.2400;0.2613;0.2617;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 10（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2613;0.2617;0.2830;0.2833;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 11（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2830;0.2833;0.3047;0.3050;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 12（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3047;0.3050;0.3263;0.3267;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 13（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3263;0.3267;0.3480;0.3483;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 14（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3480;0.3483;0.3697;0.3700;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 15（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3697;0.3700;0.3913;0.3917;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 16（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3913;0.3917;0.4130;0.4133;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 17（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4130;0.4133;0.4347;0.4350;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 18（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4347;0.4350;0.4563;0.4567;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 19（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4563;0.4567;0.4780;0.4783;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 20（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4780;0.4783;0.4997;0.5000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 21（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4997;0.5000;0.5213;0.5217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 22（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5213;0.5217;0.5430;0.5433;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 23（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5430;0.5433;0.5647;0.5650;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 24（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5647;0.5650;0.5863;0.5867;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 25（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5863;0.5867;0.6080;0.6083;1.0000" values="0;0;1;1;0;0"/></text>
<text x="610" y="278" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">ステップ 26（最大 32）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.6080;0.6083;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="352" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">視線を一定のステップで進む<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1663;0.1667;1.0000" values="1;1;0;0"/></text>
<text x="40" y="352" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">雲の中では密度が高く、透過率が急に下がり、光が積み上がる<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1663;0.1667;0.6297;0.6300;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="352" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">透過率が 0 に近づいたので、ここで打ち切る → このピクセルの色が決まる<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.6297;0.6300;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:cloud-raymarch:end -->

## 光の計算

### Beer の法則

**太陽に向かって雲の中を進むと、水滴にぶつかって光が減ります**。**密度を太陽方向に積分した「厚み」から、届く光が決まります**。

<div class="formula">届く光 = exp( −厚み × 消散係数 )</div>

```hlsl
float LightMarch(float3 position, float3 sun_dir) {
  float optical_depth = 0;
  float step_length = kLightStepLength;
  for (int i = 1; i <= kLightStepCount; ++i) {
    float3 p = position + sun_dir * step_length * i;
    float density = CloudDensity(p, HeightFraction(p));
    optical_depth += density * step_length;
    step_length *= 1.5;
  }
  return optical_depth;
}
```

| 点 | 説明 |
| --- | --- |
| **サンプル数 4〜6** | **視線のサンプルごとに必要**なので**少なく**する |
| **ステップを伸ばす** | **近くを細かく、遠くを粗く**（`step *= 1.5`） |
| **コスト** | **視線 N 回 × 光 M 回**。**雲の描画が重い主な理由** |

### Powder 効果

**雲の縁（薄い所）は、Beer の法則だと「明るすぎる」ですが実際には暗いことがあります**。**散乱された光が雲の奥から出てこないため**です。**Powder 効果**は**これを近似**します。

<div class="formula">Powder = 1 − exp( −2 · density )</div>

```hlsl
float PowderEffect(float density) {
  return 1.0 - exp(-density * 2.0);
}
```

**Beer（薄いほど明るい）と Powder（薄いほど暗い）を掛ける**と**縁が暗く、中が明るい**という**実際の雲の見え方**に**近づきます**（**Beer-Powder**）。

### 位相関数

**雲の水滴は大きいため、光を前方に強く散らします**。**太陽の方を見ると雲の縁が銀色に光る（シルバーライニング）のはこれが理由**です。**前方ローブと後方ローブを混ぜた二重 Henyey-Greenstein** を使います。

```hlsl
float CloudPhase(float cos_theta) {
  float forward = HenyeyGreenstein(cos_theta, 0.8);
  float backward = HenyeyGreenstein(cos_theta, -0.3);
  return lerp(backward, forward, 0.7);
}
```

### 多重散乱の近似

**雲の中では光が何度も散らされ、明るく見えます**。**Beer の法則だけだと、厚い雲が暗くなりすぎます**。**消散・位相の寄与を数オクターブ分、減衰させながら足す近似**で、**厚い雲を適度に明るくします**。

```hlsl
float3 MultiScatteredLight(float optical_depth, float phase_cos) {
  float3 luminance = 0;
  float attenuation = 1.0;
  float contribution = 1.0;
  float phase_attenuation = 1.0;
  for (int octave = 0; octave < 4; ++octave) {
    float p = CloudPhaseWithG(phase_cos, 0.8 * phase_attenuation);
    luminance += contribution * p * exp(-optical_depth * attenuation) * sun_color;
    attenuation *= 0.5;
    contribution *= 0.5;
    phase_attenuation *= 0.5;
  }
  return luminance;
}
```

## 影

**雲は地面や他の雲に影を落とします**。

| 影の種類 | 内容 |
| --- | --- |
| <strong>雲の影（地面へ）</strong> | **地面の位置から太陽方向へ雲を積分して、日が差す量を減らす**。**または雲の影用のマップ（光方向の透過率）を事前に作る** |
| **雲の自己影** | <strong>光のマーチ（上記）</strong> |
| **山の影が雲に** | **シャドウ マップを雲のサンプルで引く** |
| **光の筋** | **雲の隙間から差す光**（[光の筋](god-rays.md)） |

## 高速化：時間蓄積

**雲のレイマーチは重い**ので、**画面全体を毎フレーム描かず、1/4 の画素だけ描いて、時間をかけて埋めます**。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="雲の時間蓄積">
<text x="20" y="24" class="fig-title">4×4 のうち 1 ピクセルだけ毎フレーム更新して、16 フレームで全体が埋まる</text>
<g transform="translate(40,50)">
<g stroke="currentColor" stroke-opacity="0.4" fill="none"><rect x="0" y="0" width="128" height="128"/>
<line x1="32" y1="0" x2="32" y2="128"/><line x1="64" y1="0" x2="64" y2="128"/><line x1="96" y1="0" x2="96" y2="128"/>
<line x1="0" y1="32" x2="128" y2="32"/><line x1="0" y1="64" x2="128" y2="64"/><line x1="0" y1="96" x2="128" y2="96"/></g>
<rect x="32" y="64" width="32" height="32" fill="#e5484d" fill-opacity="0.6"/>
<text x="64" y="156" text-anchor="middle" style="font-size:12px">今のフレームで描く位置</text>
</g>
<g font-size="12">
<text x="240" y="82" style="font-weight:700">手順</text>
<text x="240" y="106">① 1/4 解像度（または 4×4 に 1 画素）だけレイマーチ</text>
<text x="240" y="130">② 前フレームの結果を、カメラの動きで再投影して持ってくる</text>
<text x="240" y="154">③ 新しく描いた画素だけ置き換える</text>
<text x="240" y="178">④ 動く物の裏など、履歴が使えない所は新しい結果を優先</text>
<text x="240" y="212" style="font-weight:700">コスト：1/16 〜 1/4 に。ただしゴースト（残像）に注意</text>
</g>
</svg>

| 工夫 | 内容 |
| --- | --- |
| **低解像度で描く** | **半分／1/4 の解像度**で**レイマーチ**し、**アップサンプル** |
| **ブルー ノイズ ジッター** | **フレームごとに開始位置を変えて、平均で滑らか** |
| **履歴の再投影** | **前フレームの雲をカメラ移動分だけ動かす**（雲は遠いので回転だけで近似できる） |
| **層の距離を使う** | **雲までの距離（深度）を持って、再投影の精度を上げる** |
| **早期の打ち切り** | **透過率が低ければ打ち切る** |

## 簡易な代替

**重いレイマーチが使えない場面**の**代替**です。

| 方式 | 内容 |
| --- | --- |
| **雲のスカイボックス** | **事前に描いた雲のキューブマップを回す** |
| <strong>2D の雲（スカイドームの絵）</strong> | **スクロールする雲のテクスチャ ＋ 法線マップで凹凸** |
| **フローマップで動かす** | **雲の絵を流れの向きに動かす**（[水のフローマップ](../water/interaction.md)） |
| <strong>ボリューム テクスチャ（事前焼き）</strong> | **雲の塊を 3D テクスチャに焼き、ビルボードで描く** |
| <strong>雲の板（インポスター）</strong> | **遠景の雲を板で置く** |

## よくあるミス

??? failure "雲が板状に見えて、立体感がない"
    **ディテール ノイズ・光のマーチを入れて、縁と中の陰影をつける**。

??? failure "雲の縁にバンディング（縞）が出る"
    **ブルー ノイズのジッターと、時間蓄積**を入れる。

??? failure "太陽が雲の向こうにあるのに、雲が暗くなりすぎる"
    **多重散乱の近似と位相関数の前方ローブ**を入れる。

??? failure "カメラを動かすと、雲がゴーストを引く"
    **履歴の再投影を雲の距離に合わせる**。**履歴の信頼度を落とす**。

??? failure "レイマーチが重くて、フレームが落ちる"
    **低解像度＋時間蓄積**、**ステップ数を減らす**、**空白は粗いステップで飛ばす**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 雲 ＝ <strong>密度の塊</strong>。<strong>視線に沿ってレイマーチし、光と透過率を積む</strong>
    - [x] 密度 ＝ <strong>天気マップ × 高さの形 × 3D ノイズ（形＋ディテール）</strong>
    - [x] 光 ＝ <strong>Beer の法則（太陽方向の厚み）× Powder × 前方に強い位相関数</strong>。<strong>多重散乱を近似</strong>
    - [x] <strong>重いので低解像度 ＋ ジッター ＋ 時間蓄積</strong>
    - [x] <strong>代替</strong>に<strong>スカイボックス・2D の雲</strong>

## 参考

- Schneider & Vos, "The Real-time Volumetric Cloudscapes of Horizon: Zero Dawn"（SIGGRAPH 2015）
- Schneider, "Nubis: Authoring Real-Time Volumetric Cloudscapes with the Decima Engine"（SIGGRAPH 2017）
- Hillaire, "Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite"（SIGGRAPH 2016）

## 関連ページ

- [空と大気](index.md)
- [大気散乱](scattering.md)
- [ボリューメトリック フォグ](volumetric-fog.md)
- [光の筋](god-rays.md)
