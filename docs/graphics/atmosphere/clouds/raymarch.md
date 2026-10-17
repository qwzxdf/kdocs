---
title: Cloud Raymarching
tags:
  - 描画
---

# Cloud Raymarching

**視線に沿って少しずつ進み、各点で密度と光を計算して、足し合わせる**のが**レイマーチ**です。**ステップ数が品質とコストを決める**ので、**工夫が必要**です。このページでは、**レイマーチ**を説明します。

!!! tip "ポイント"
    - **視線に沿って進み、密度を足す**。
    - **雲に入るまでは、大きな歩幅**。
    - **ジッタで開始位置をずらし、縞を消す**。
    - **透過率が低くなったら、打ち切る**。

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

レイマーチのコードの要点です。ステップ数は、近くは細かく、遠くは粗く（32〜64 段）し、雲に入ったら細かくします。ブルー ノイズのジッターで開始位置をずらして縞を消します。時間蓄積と相性が良いです。透過率が 1 % を切ったら不透明になったとみなして打ち切ります。密度が 0 の空間は粗いステップで進み、雲に当たったら細かく進める工夫もあります。戻り値は、散乱光 RGB と透過率で、空の上に合成します。

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

## よくあるミス

??? failure "雲に縞模様（バンディング）が出る"
    **ジッタ**を入れて、**時間蓄積**で消す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **進みながら足す。歩幅とジッタが鍵**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Clouds](index.md)
- [光の計算](lighting.md)
- [高速化](temporal.md)
