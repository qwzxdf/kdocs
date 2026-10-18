---
title: Cloud Raymarching
tags:
  - 描画
---

# Cloud Raymarching

<strong>視線に沿って少しずつ進み、各点で密度と光を計算して、足し合わせる</strong>のが<strong>レイマーチ</strong>です。ステップ数が品質とコストを決めるので、工夫が必要です。このページでは、レイマーチを説明します。

!!! tip "ポイント"
    - 視線に沿って進み、密度を足す。
    - 雲に入るまでは、大きな歩幅。
    - ジッタで開始位置をずらし、縞を消す。
    - 透過率が低くなったら、打ち切る。

## レイマーチ
<strong>視線に沿って、雲の層の中を一定のステップで進み、各点の密度から光を積みます</strong>。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="雲のレイマーチ">
<text x="20" y="24" class="fig-title">視線に沿って進み、各点で「太陽に向けても少し進んで」光の量を調べる</text>
<rect x="260" y="60" width="300" height="110" rx="40" fill="#fff" fill-opacity="0.35" stroke="currentColor" stroke-opacity="0.4"/>
<circle cx="120" cy="220" r="6" fill="#e5484d"/><text x="90" y="244" style="font-size:12px">カメラ</text>
<line x1="120" y1="220" x2="540" y2="80" stroke="currentColor" stroke-width="2"/>
<g fill="#2ea043"><circle cx="300" cy="160" r="4"/><circle cx="360" cy="140" r="4"/><circle cx="420" cy="120" r="4"/><circle cx="480" cy="100" r="4"/></g>
<text x="300" y="186" style="font-size:11px;fill:#2ea043">視線のサンプル点</text>
<g stroke="#e5aa28" stroke-dasharray="4 3"><line x1="360" y1="140" x2="440" y2="40"/><line x1="420" y1="120" x2="500" y2="28"/></g>
<circle cx="640" cy="50" r="14" fill="#e5aa28"/><text x="620" y="82" style="font-size:12px">太陽</text>
<text x="460" y="236" style="font-size:11px">各サンプルから太陽へ 4〜6 回、密度を足して「厚み」を測る</text>
</svg>

```hlsl
float4 MarchClouds(float3 ray_origin, float3 ray_dir, float t_start, float t_end, float3 sun_dir) {
  float step_length = (t_end - t_start) / kStepCount;
  float jitter = BlueNoise(input.position.xy);
  float transmittance = 1.0;
  float3 scattered = 0;
```

レイの、区間を、`kStepCount` 個に、分け、歩幅を、決めます。開始位置を、ブルー ノイズで、ずらして、縞を、ノイズに、変えます。`transmittance`（透過率）は、1 から、減らしていき、`scattered` に、散乱光を、貯めます。

```hlsl
  for (int i = 0; i < kStepCount; ++i) {
    float t = t_start + (i + jitter) * step_length;
    float3 position = ray_origin + ray_dir * t;
    float height_fraction = HeightFraction(position);
    float density = CloudDensity(position, height_fraction);
    if (density <= 0.001) continue;
```

1 歩ごとの、位置を、求め、そこの、雲の、密度を、調べます。雲の外（密度が、ほぼ 0）は、飛ばします。高さの割合 `height_fraction` は、雲の層の、中で、どの高さかを、表します（0 が、底、1 が、頂上）。

```hlsl
    float light_optical_depth = LightMarch(position, sun_dir);
    float3 sun_light = sun_color * exp(-light_optical_depth * extinction);
    sun_light *= PowderEffect(density);
    float phase = CloudPhase(dot(ray_dir, sun_dir));
    float3 ambient = ambient_color * lerp(0.4, 1.0, height_fraction);
```

太陽の光を、求めます。その位置から、太陽へ、短く、もう一度、進んで、光学的な厚さを、測り、ビア・ランベルトの法則で、減衰させます。粉砂糖効果（雲の、縁が、暗くなる）と、位相関数（太陽の、向きによる、明るさの違い）を、掛け、空からの、環境光を、足します。

```hlsl
    float3 luminance = (sun_light * phase + ambient) * density * scattering_coeff;
    float step_transmittance = exp(-density * extinction * step_length);
    float3 integrated = (luminance - luminance * step_transmittance) / max(density * extinction, 1e-5);
```

この区間で、散乱される光を、求めます。区間の中で、密度が、一定と、みなし、解析的に、積分した、式で、歩幅が、大きくても、安定します。

```hlsl
    scattered += integrated * transmittance;
    transmittance *= step_transmittance;
    if (transmittance < 0.01) break;
  }
```

散乱光を、足し、透過率を、下げます。透過率が、ほぼ 0 になったら、奥は、見えないので、打ち切ります。戻り値は、散乱光と、透過率で、あとで、空の色に、合成します。

```hlsl
  return float4(scattered, transmittance);
}
```

| 点 | 説明 |
| --- | --- |
| ステップ数 | 近くは細かく、遠くは粗く（32〜64 段）。雲に入ったら細かく |
| ブルー ノイズのジッター | 開始位置をずらして縞を消す。時間蓄積と相性が良い |
| 早期終了 | 透過率が 1 % を切ったら打ち切る（不透明になった） |
| 密度 0 は飛ばす | 何もない空間を粗いステップで進み、雲に当たったら細かくにする工夫 |
| 戻り値 | 散乱光 RGB と透過率（空の上に合成） |

<!-- fig:cloud-raymarch:begin -->

<svg class="fig illust motion" data-fig="cloud-raymarch" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-cloud-raymarch" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">雲のレイマーチ: 光線を少しずつ進めて、密度を読み、透過率が下がったら打ち切る</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">雲の断面(40×14 マス)。カメラから右上へ光線を飛ばす。1 歩ごとに、密度から透過率を更新する</text>
<rect x="30" y="96" width="580.0" height="216.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">雲(濃い所ほど青白く)と、光線</text>
<rect x="40.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="54.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="68.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="82.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="96.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="110.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="124.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="138.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="152.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="166.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f3f5f8"/></rect>
<rect x="180.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#edf0f4"/></rect>
<rect x="194.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e8ebf0"/></rect>
<rect x="208.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e3e7ec"/></rect>
<rect x="222.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e1e5eb"/></rect>
<rect x="236.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e1e5ea"/></rect>
<rect x="250.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e3e7ec"/></rect>
<rect x="264.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e7eaef"/></rect>
<rect x="278.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#eceff3"/></rect>
<rect x="292.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f1f4f7"/></rect>
<rect x="306.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f6f8fa"/></rect>
<rect x="320.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="334.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="348.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="362.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="376.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="390.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="404.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="418.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="432.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="446.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="460.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="474.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="488.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="502.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="516.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="530.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="544.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="558.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="572.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="586.0" y="100.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="40.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="54.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="68.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="82.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="96.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="110.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="124.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="138.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f5f8fa"/></rect>
<rect x="152.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#edf0f4"/></rect>
<rect x="166.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e4e8ec"/></rect>
<rect x="180.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#dadfe5"/></rect>
<rect x="194.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d1d7de"/></rect>
<rect x="208.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#cad0d9"/></rect>
<rect x="222.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c6cdd6"/></rect>
<rect x="236.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c5ccd5"/></rect>
<rect x="250.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c8cfd8"/></rect>
<rect x="264.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#ced4dc"/></rect>
<rect x="278.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d5dbe2"/></rect>
<rect x="292.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#dee2e8"/></rect>
<rect x="306.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e5e9ed"/></rect>
<rect x="320.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#ebeef2"/></rect>
<rect x="334.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#eef1f4"/></rect>
<rect x="348.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#eef1f4"/></rect>
<rect x="362.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#eceff3"/></rect>
<rect x="376.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e7ebef"/></rect>
<rect x="390.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e3e7ec"/></rect>
<rect x="404.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e1e5eb"/></rect>
<rect x="418.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e2e6eb"/></rect>
<rect x="432.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e7ebef"/></rect>
<rect x="446.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#eef1f5"/></rect>
<rect x="460.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f6f8fb"/></rect>
<rect x="474.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="488.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="502.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="516.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="530.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="544.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="558.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="572.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="586.0" y="114.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="40.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="54.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="68.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="82.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="96.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="110.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="124.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f6f8fa"/></rect>
<rect x="138.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#eceff3"/></rect>
<rect x="152.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e0e4e9"/></rect>
<rect x="166.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d2d7df"/></rect>
<rect x="180.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c3cad4"/></rect>
<rect x="194.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#b6beca"/></rect>
<rect x="208.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#acb5c2"/></rect>
<rect x="222.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#a5afbd"/></rect>
<rect x="236.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#a4aebc"/></rect>
<rect x="250.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#a7b1bf"/></rect>
<rect x="264.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#afb8c4"/></rect>
<rect x="278.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#b8c0cb"/></rect>
<rect x="292.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c2c9d3"/></rect>
<rect x="306.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#ccd2da"/></rect>
<rect x="320.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d3d8df"/></rect>
<rect x="334.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d6dbe2"/></rect>
<rect x="348.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d5dae1"/></rect>
<rect x="362.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d0d5dd"/></rect>
<rect x="376.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c8ced7"/></rect>
<rect x="390.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c0c8d1"/></rect>
<rect x="404.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#bdc4cf"/></rect>
<rect x="418.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#bfc7d1"/></rect>
<rect x="432.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c8cfd8"/></rect>
<rect x="446.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d6dbe2"/></rect>
<rect x="460.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e5e9ed"/></rect>
<rect x="474.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f2f5f8"/></rect>
<rect x="488.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="502.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="516.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="530.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="544.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="558.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="572.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="586.0" y="128.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="40.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="54.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="68.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="82.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="96.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="110.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="124.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f0f3f6"/></rect>
<rect x="138.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e3e7ec"/></rect>
<rect x="152.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d3d9e0"/></rect>
<rect x="166.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c1c9d2"/></rect>
<rect x="180.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#afb8c4"/></rect>
<rect x="194.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#9ea8b7"/></rect>
<rect x="208.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#909cac"/></rect>
<rect x="222.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8794a6"/></rect>
<rect x="236.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8491a3"/></rect>
<rect x="250.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8693a5"/></rect>
<rect x="264.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8d99ab"/></rect>
<rect x="278.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#97a2b2"/></rect>
<rect x="292.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#a1abb9"/></rect>
<rect x="306.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#aab3c1"/></rect>
<rect x="320.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#b1bac6"/></rect>
<rect x="334.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#b4bdc8"/></rect>
<rect x="348.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#b3bbc7"/></rect>
<rect x="362.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#acb5c2"/></rect>
<rect x="376.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#a2adbb"/></rect>
<rect x="390.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#9aa5b4"/></rect>
<rect x="404.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#96a2b1"/></rect>
<rect x="418.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#9ba6b5"/></rect>
<rect x="432.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#aab3c0"/></rect>
<rect x="446.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#bec5d0"/></rect>
<rect x="460.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d4d9e0"/></rect>
<rect x="474.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e7ebef"/></rect>
<rect x="488.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f6f8fb"/></rect>
<rect x="502.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="516.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="530.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="544.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="558.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="572.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="586.0" y="142.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="40.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="54.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="68.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="82.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="96.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="110.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f7f9fb"/></rect>
<rect x="124.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#eceff3"/></rect>
<rect x="138.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#dee2e8"/></rect>
<rect x="152.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#ccd2da"/></rect>
<rect x="166.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#b7c0cb"/></rect>
<rect x="180.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#a2acbb"/></rect>
<rect x="194.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8e9aab"/></rect>
<rect x="208.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#7e8b9f"/></rect>
<rect x="222.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#738196"/></rect>
<rect x="236.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#6d7d92"/></rect>
<rect x="250.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#6d7d92"/></rect>
<rect x="264.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#718095"/></rect>
<rect x="278.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#77869a"/></rect>
<rect x="292.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#7e8c9f"/></rect>
<rect x="306.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8592a4"/></rect>
<rect x="320.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8b97a9"/></rect>
<rect x="334.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8e9aab"/></rect>
<rect x="348.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8f9bac"/></rect>
<rect x="362.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8b97a9"/></rect>
<rect x="376.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8592a4"/></rect>
<rect x="390.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#808da0"/></rect>
<rect x="404.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#808da0"/></rect>
<rect x="418.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8995a7"/></rect>
<rect x="432.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#9ba5b5"/></rect>
<rect x="446.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#b3bbc7"/></rect>
<rect x="460.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#ccd2db"/></rect>
<rect x="474.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e3e7ec"/></rect>
<rect x="488.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f3f6f9"/></rect>
<rect x="502.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="516.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="530.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="544.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="558.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="572.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="586.0" y="156.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="40.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="54.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="68.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="82.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="96.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="110.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f7f9fb"/></rect>
<rect x="124.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#eceff3"/></rect>
<rect x="138.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#dee2e8"/></rect>
<rect x="152.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#ccd2da"/></rect>
<rect x="166.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#b7bfcb"/></rect>
<rect x="180.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#a2acba"/></rect>
<rect x="194.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8e9aab"/></rect>
<rect x="208.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#7c8a9e"/></rect>
<rect x="222.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#707f94"/></rect>
<rect x="236.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#68788e"/></rect>
<rect x="250.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#64748b"/></rect>
<rect x="264.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#64748b"/></rect>
<rect x="278.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#64748b"/></rect>
<rect x="292.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#64748b"/></rect>
<rect x="306.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#66768d"/></rect>
<rect x="320.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#6a7990"/></rect>
<rect x="334.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#6f7e93"/></rect>
<rect x="348.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#748297"/></rect>
<rect x="362.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#78869a"/></rect>
<rect x="376.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#7b889c"/></rect>
<rect x="390.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#7e8b9f"/></rect>
<rect x="404.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8491a3"/></rect>
<rect x="418.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#919cad"/></rect>
<rect x="432.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#a4aebc"/></rect>
<rect x="446.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#bbc3cd"/></rect>
<rect x="460.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d3d8df"/></rect>
<rect x="474.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e7ebef"/></rect>
<rect x="488.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f6f8fa"/></rect>
<rect x="502.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="516.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="530.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="544.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="558.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="572.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="586.0" y="170.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="40.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="54.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="68.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="82.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="96.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="110.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="124.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f0f2f6"/></rect>
<rect x="138.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e3e7ec"/></rect>
<rect x="152.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d3d9e0"/></rect>
<rect x="166.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c1c8d2"/></rect>
<rect x="180.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#aeb7c4"/></rect>
<rect x="194.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#9ca6b6"/></rect>
<rect x="208.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8c98a9"/></rect>
<rect x="222.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#7f8ca0"/></rect>
<rect x="236.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#768498"/></rect>
<rect x="250.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#6e7d93"/></rect>
<rect x="264.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#68788e"/></rect>
<rect x="278.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#64748b"/></rect>
<rect x="292.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#64748b"/></rect>
<rect x="306.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#64748b"/></rect>
<rect x="320.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#64748b"/></rect>
<rect x="334.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#64748b"/></rect>
<rect x="348.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#6c7b91"/></rect>
<rect x="362.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#78869a"/></rect>
<rect x="376.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8592a4"/></rect>
<rect x="390.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#919dae"/></rect>
<rect x="404.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#9ea9b7"/></rect>
<rect x="418.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#adb6c3"/></rect>
<rect x="432.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#bfc6d0"/></rect>
<rect x="446.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d1d7de"/></rect>
<rect x="460.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e3e7ec"/></rect>
<rect x="474.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f1f4f7"/></rect>
<rect x="488.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="502.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="516.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="530.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="544.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="558.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="572.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="586.0" y="184.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="40.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="54.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="68.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="82.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="96.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="110.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="124.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f6f8fa"/></rect>
<rect x="138.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#eceff3"/></rect>
<rect x="152.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#dfe4e9"/></rect>
<rect x="166.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d1d7df"/></rect>
<rect x="180.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c2cad3"/></rect>
<rect x="194.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#b4bcc8"/></rect>
<rect x="208.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#a7b1be"/></rect>
<rect x="222.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#9ca6b6"/></rect>
<rect x="236.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#929eae"/></rect>
<rect x="250.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8996a8"/></rect>
<rect x="264.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#808ea1"/></rect>
<rect x="278.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#778599"/></rect>
<rect x="292.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#6e7d93"/></rect>
<rect x="306.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#68788e"/></rect>
<rect x="320.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#67778e"/></rect>
<rect x="334.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#6e7d93"/></rect>
<rect x="348.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#7b889c"/></rect>
<rect x="362.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8b98a9"/></rect>
<rect x="376.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#9ea8b7"/></rect>
<rect x="390.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#afb8c5"/></rect>
<rect x="404.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c0c7d1"/></rect>
<rect x="418.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#ced4dc"/></rect>
<rect x="432.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#dce1e7"/></rect>
<rect x="446.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e9ecf0"/></rect>
<rect x="460.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f4f6f9"/></rect>
<rect x="474.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="488.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="502.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="516.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="530.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="544.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="558.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="572.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="586.0" y="198.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="40.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="54.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="68.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="82.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="96.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="110.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="124.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="138.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f5f8fa"/></rect>
<rect x="152.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#edf0f4"/></rect>
<rect x="166.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e3e7ec"/></rect>
<rect x="180.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d9dee4"/></rect>
<rect x="194.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#cfd5dd"/></rect>
<rect x="208.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c5ccd5"/></rect>
<rect x="222.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#bdc5cf"/></rect>
<rect x="236.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#b5bec9"/></rect>
<rect x="250.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#adb6c3"/></rect>
<rect x="264.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#a4aebc"/></rect>
<rect x="278.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#9ba6b5"/></rect>
<rect x="292.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#929dae"/></rect>
<rect x="306.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8b98a9"/></rect>
<rect x="320.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8a96a8"/></rect>
<rect x="334.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#8f9bac"/></rect>
<rect x="348.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#9ba6b5"/></rect>
<rect x="362.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#abb4c1"/></rect>
<rect x="376.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#bcc4cf"/></rect>
<rect x="390.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#cdd3dc"/></rect>
<rect x="404.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#dce1e7"/></rect>
<rect x="418.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e8ecf0"/></rect>
<rect x="432.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f2f5f7"/></rect>
<rect x="446.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="460.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="474.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="488.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="502.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="516.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="530.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="544.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="558.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="572.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="586.0" y="212.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="40.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="54.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="68.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="82.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="96.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="110.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="124.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="138.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="152.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="166.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f3f5f8"/></rect>
<rect x="180.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#eceff3"/></rect>
<rect x="194.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e6eaee"/></rect>
<rect x="208.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e0e5ea"/></rect>
<rect x="222.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#dbe0e6"/></rect>
<rect x="236.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d6dbe2"/></rect>
<rect x="250.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#d0d6dd"/></rect>
<rect x="264.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c9d0d8"/></rect>
<rect x="278.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c2c9d3"/></rect>
<rect x="292.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#bbc3ce"/></rect>
<rect x="306.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#b6bfca"/></rect>
<rect x="320.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#b5bec9"/></rect>
<rect x="334.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#b9c1cc"/></rect>
<rect x="348.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#c1c8d2"/></rect>
<rect x="362.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#cdd3db"/></rect>
<rect x="376.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#dadee5"/></rect>
<rect x="390.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e6eaee"/></rect>
<rect x="404.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f1f3f6"/></rect>
<rect x="418.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="432.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="446.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="460.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="474.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="488.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="502.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="516.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="530.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="544.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="558.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="572.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="586.0" y="226.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="40.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="54.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="68.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="82.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="96.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="110.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="124.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="138.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="152.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="166.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="180.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="194.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f7f9fb"/></rect>
<rect x="208.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f4f6f9"/></rect>
<rect x="222.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f1f4f7"/></rect>
<rect x="236.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#eef1f4"/></rect>
<rect x="250.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#ebeef2"/></rect>
<rect x="264.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e7ebef"/></rect>
<rect x="278.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e3e7ec"/></rect>
<rect x="292.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#dfe3e9"/></rect>
<rect x="306.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#dce1e7"/></rect>
<rect x="320.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#dbe0e6"/></rect>
<rect x="334.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#dde2e7"/></rect>
<rect x="348.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e2e6eb"/></rect>
<rect x="362.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#e9ecf0"/></rect>
<rect x="376.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f0f3f6"/></rect>
<rect x="390.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f7f9fb"/></rect>
<rect x="404.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="418.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="432.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="446.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="460.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="474.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="488.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="502.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="516.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="530.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="544.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="558.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="572.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="586.0" y="240.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="40.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="54.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="68.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="82.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="96.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="110.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="124.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="138.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="152.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="166.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="180.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="194.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="208.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="222.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="236.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="250.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="264.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="278.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="292.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f6f8fa"/></rect>
<rect x="306.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f5f7f9"/></rect>
<rect x="320.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f4f7f9"/></rect>
<rect x="334.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0195" values="#f8fafc;#f5f8fa"/></rect>
<rect x="348.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="362.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="376.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="390.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="404.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="418.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="432.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="446.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="460.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="474.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="488.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="502.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="516.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="530.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="544.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="558.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="572.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="586.0" y="254.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="40.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="54.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="68.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="82.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="96.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="110.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="124.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="138.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="152.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="166.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="180.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="194.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="208.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="222.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="236.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="250.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="264.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="278.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="292.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="306.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="320.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="334.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="348.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="362.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="376.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="390.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="404.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="418.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="432.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="446.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="460.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="474.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="488.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="502.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="516.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="530.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="544.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="558.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="572.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="586.0" y="268.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="40.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="54.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="68.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="82.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="96.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="110.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="124.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="138.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="152.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="166.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="180.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="194.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="208.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="222.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="236.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="250.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="264.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="278.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="292.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="306.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="320.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="334.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="348.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="362.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="376.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="390.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="404.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="418.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="432.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="446.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="460.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="474.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="488.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="502.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="516.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="530.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="544.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="558.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="572.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<rect x="586.0" y="282.0" width="14.3" height="14.3" fill="#f8fafc"/>
<circle cx="54.0" cy="275.0" r="8" fill="#1f2937"/>
<text x="64.0" y="297.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">カメラ</text>
<circle cx="60.06" cy="273.26" r="3.2" fill="#34d399" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;1.0000" values="0;0;1;1"/></circle>
<circle cx="72.17" cy="269.79" r="3.2" fill="#34d399" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0564;0.0566;1.0000" values="0;0;1;1"/></circle>
<circle cx="84.28" cy="266.32" r="3.2" fill="#34d399" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0642;0.0644;1.0000" values="0;0;1;1"/></circle>
<circle cx="96.39" cy="262.84" r="3.2" fill="#34d399" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0720;0.0722;1.0000" values="0;0;1;1"/></circle>
<circle cx="108.5" cy="259.37" r="3.2" fill="#34d399" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;1.0000" values="0;0;1;1"/></circle>
<circle cx="120.62" cy="255.9" r="3.2" fill="#34d399" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0876;0.0878;1.0000" values="0;0;1;1"/></circle>
<circle cx="132.73" cy="252.43" r="3.2" fill="#34d399" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0954;0.0956;1.0000" values="0;0;1;1"/></circle>
<circle cx="144.84" cy="248.95" r="3.2" fill="#34d399" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1032;0.1034;1.0000" values="0;0;1;1"/></circle>
<circle cx="156.95" cy="245.48" r="3.2" fill="#34d399" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1110;0.1112;1.0000" values="0;0;1;1"/></circle>
<circle cx="169.06" cy="242.01" r="3.2" fill="#34d399" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1188;0.1190;1.0000" values="0;0;1;1"/></circle>
<circle cx="181.17" cy="238.53" r="3.290970010828409" fill="#3bce96" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1266;0.1268;1.0000" values="0;0;1;1"/></circle>
<circle cx="193.29" cy="235.06" r="3.5180799149718815" fill="#4cc18e" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1344;0.1346;1.0000" values="0;0;1;1"/></circle>
<circle cx="205.4" cy="231.59" r="3.790294804597281" fill="#60b185" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1422;0.1424;1.0000" values="0;0;1;1"/></circle>
<circle cx="217.51" cy="228.11" r="4.103527662105188" fill="#789f7a" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1500;0.1502;1.0000" values="0;0;1;1"/></circle>
<circle cx="229.62" cy="224.64" r="4.453841363173282" fill="#928b6e" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1579;0.1580;1.0000" values="0;0;1;1"/></circle>
<circle cx="241.73" cy="221.17" r="4.839747868125224" fill="#af7561" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1657;0.1659;1.0000" values="0;0;1;1"/></circle>
<circle cx="253.85" cy="217.69" r="5.261767204482382" fill="#ce5d53" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1735;0.1737;1.0000" values="0;0;1;1"/></circle>
<circle cx="265.96" cy="214.22" r="5.717375439968945" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1813;0.1815;1.0000" values="0;0;1;1"/></circle>
<circle cx="278.07" cy="210.75" r="6.1921377099821395" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1891;0.1893;1.0000" values="0;0;1;1"/></circle>
<circle cx="290.18" cy="207.28" r="6.65167193933765" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1969;0.1971;1.0000" values="0;0;1;1"/></circle>
<circle cx="302.29" cy="203.8" r="7.041547049377677" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2047;0.2049;1.0000" values="0;0;1;1"/></circle>
<circle cx="314.41" cy="200.33" r="7.2" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2125;0.2127;1.0000" values="0;0;1;1"/></circle>
<circle cx="326.52" cy="196.86" r="7.2" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2203;0.2205;1.0000" values="0;0;1;1"/></circle>
<circle cx="338.63" cy="193.38" r="7.2" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2281;0.2283;1.0000" values="0;0;1;1"/></circle>
<circle cx="350.74" cy="189.91" r="7.079071615223052" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2359;0.2361;1.0000" values="0;0;1;1"/></circle>
<circle cx="362.85" cy="186.44" r="6.832871114295086" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2437;0.2439;1.0000" values="0;0;1;1"/></circle>
<circle cx="374.97" cy="182.96" r="6.64203017072495" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2515;0.2517;1.0000" values="0;0;1;1"/></circle>
<circle cx="387.08" cy="179.49" r="6.545788365451731" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2593;0.2595;1.0000" values="0;0;1;1"/></circle>
<circle cx="399.19" cy="176.02" r="6.510825402082949" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2671;0.2673;1.0000" values="0;0;1;1"/></circle>
<circle cx="411.3" cy="172.55" r="6.4461564415050185" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2749;0.2751;1.0000" values="0;0;1;1"/></circle>
<circle cx="423.41" cy="169.07" r="6.251720598187985" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2827;0.2829;1.0000" values="0;0;1;1"/></circle>
<circle cx="435.52" cy="165.6" r="5.872996199380328" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2905;0.2907;1.0000" values="0;0;1;1"/></circle>
<circle cx="447.64" cy="162.13" r="5.329522792318041" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2983;0.2985;1.0000" values="0;0;1;1"/></circle>
<circle cx="459.75" cy="158.65" r="4.702817788037618" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3061;0.3063;1.0000" values="0;0;1;1"/></circle>
<circle cx="471.86" cy="155.18" r="4.095458299256984" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3140;0.3141;1.0000" values="0;0;1;1"/></circle>
<circle cx="483.97" cy="151.71" r="3.588303105615107" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3218;0.3220;1.0000" values="0;0;1;1"/></circle>
<circle cx="496.08" cy="148.23" r="3.2" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3296;0.3298;1.0000" values="0;0;1;1"/></circle>
<circle cx="508.2" cy="144.76" r="3.2" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3374;0.3376;1.0000" values="0;0;1;1"/></circle>
<circle cx="520.31" cy="141.29" r="3.2" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3452;0.3454;1.0000" values="0;0;1;1"/></circle>
<circle cx="532.42" cy="137.82" r="3.2" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3530;0.3532;1.0000" values="0;0;1;1"/></circle>
<circle cx="544.53" cy="134.34" r="3.2" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3608;0.3610;1.0000" values="0;0;1;1"/></circle>
<circle cx="556.64" cy="130.87" r="3.2" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3686;0.3688;1.0000" values="0;0;1;1"/></circle>
<circle cx="568.76" cy="127.4" r="3.2" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3764;0.3766;1.0000" values="0;0;1;1"/></circle>
<circle cx="580.87" cy="123.92" r="3.2" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3842;0.3844;1.0000" values="0;0;1;1"/></circle>
<circle cx="592.98" cy="120.45" r="3.2" fill="#9ca3af" stroke="#ffffff" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3920;0.3922;1.0000" values="0;0;1;1"/></circle>
<circle cx="253.85" cy="217.69" r="13" fill="none" stroke="#e5484d" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1759;0.1761;1.0000" values="0;0;1;1"/></circle>
<text x="253.8463065855765" y="197.69499372564587" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">透過率 5% 未満で打ち切り<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1759;0.1761;1.0000" values="0;0;1;1"/></text>
<rect x="650" y="96" width="280" height="250" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="650" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">透過率 T と、集めた光</text>
<rect x="680" y="150" width="36" height="150" fill="#c4b5fd" stroke="#7c3aed" stroke-width="2"><animate attributeName="y" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1266;0.1268;0.1344;0.1346;0.1422;0.1424;0.1500;0.1502;0.1579;0.1580;0.1657;0.1659;0.1735;0.1737;1.0000" values="150;150;157.77;157.77;181.92;181.92;216.4;216.4;250.72;250.72;276.34;276.34;290.93;290.93;297.29;297.29"/><animate attributeName="height" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1266;0.1268;0.1344;0.1346;0.1422;0.1424;0.1500;0.1502;0.1579;0.1580;0.1657;0.1659;0.1735;0.1737;1.0000" values="150;150;142.23;142.23;118.08;118.08;83.6;83.6;49.28;49.28;23.66;23.66;9.07;9.07;2.71;2.71"/></rect>
<text x="698" y="322" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#7c3aed">T</text>
<rect x="780" y="300" width="36" height="0.5" fill="#fde68a" stroke="#f59e0b" stroke-width="2"><animate attributeName="y" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1266;0.1268;0.1344;0.1346;0.1422;0.1424;0.1500;0.1502;0.1579;0.1580;0.1657;0.1659;0.1735;0.1737;1.0000" values="300;300;292.23;292.23;268.08;268.08;233.6;233.6;199.28;199.28;173.66;173.66;159.07;159.07;152.71;152.71"/><animate attributeName="height" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1266;0.1268;0.1344;0.1346;0.1422;0.1424;0.1500;0.1502;0.1579;0.1580;0.1657;0.1659;0.1735;0.1737;1.0000" values="0.5;0.5;7.77;7.77;31.92;31.92;66.4;66.4;100.72;100.72;126.34;126.34;140.93;140.93;147.29;147.29"/></rect>
<text x="798" y="322" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#b45309">光</text>
<text x="840" y="190" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">T の値:</text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;1.0000" values="1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">100<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;0.0564;0.0566;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">100<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0564;0.0566;0.0642;0.0644;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">100<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0642;0.0644;0.0720;0.0722;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">100<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0720;0.0722;0.0798;0.0800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">100<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;0.0876;0.0878;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">100<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0876;0.0878;0.0954;0.0956;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">100<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0954;0.0956;0.1032;0.1034;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">100<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1032;0.1034;0.1110;0.1112;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">100<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1110;0.1112;0.1188;0.1190;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">100<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1188;0.1190;0.1266;0.1268;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">95<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1266;0.1268;0.1344;0.1346;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">79<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1344;0.1346;0.1422;0.1424;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">56<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1422;0.1424;0.1500;0.1502;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">33<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1500;0.1502;0.1579;0.1580;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1579;0.1580;0.1657;0.1659;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">6<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1657;0.1659;0.1735;0.1737;1.0000" values="0;0;1;1;0;0"/></text>
<text x="840" y="220" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">2<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1735;0.1737;1.0000" values="0;0;1;1"/></text>
<text x="882" y="220" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">%</text>
<text x="30" y="392" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937">密度を読んだ回数:</text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;1.0000" values="1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;0.0564;0.0566;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0564;0.0566;0.0642;0.0644;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0642;0.0644;0.0720;0.0722;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0720;0.0722;0.0798;0.0800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">5<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;0.0876;0.0878;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">6<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0876;0.0878;0.0954;0.0956;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">7<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0954;0.0956;0.1032;0.1034;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">8<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1032;0.1034;0.1110;0.1112;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">9<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1110;0.1112;0.1188;0.1190;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">10<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1188;0.1190;0.1266;0.1268;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">11<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1266;0.1268;0.1344;0.1346;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">12<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1344;0.1346;0.1422;0.1424;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">13<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1422;0.1424;0.1500;0.1502;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">14<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1500;0.1502;0.1579;0.1580;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">15<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1579;0.1580;0.1657;0.1659;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">16<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1657;0.1659;0.1735;0.1737;1.0000" values="0;0;1;1;0;0"/></text>
<text x="190" y="396" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">17<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1735;0.1737;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2203;0.2205;1.0000" values="0;0;1;1"/><rect x="330" y="372" width="600" height="124" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="346" y="396" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1e3a8a">最後まで進めると 45 回、打ち切ると 17 回(62% 減)</text>
<text x="346" y="421" text-anchor="start" style="font-size:15px;font-weight:700;fill:#166534">集めた光: 最後まで 1.000 / 打ち切り 0.982(差 1.8%)</text>
<text x="346" y="445" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">濃い雲に入ると、奥は、ほとんど見えない。だから、早めにやめて良い</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光線を少しずつ進めて、その場所の雲の密度を読む<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">雲に入ると、密度に応じて透過率 T が下がり、光が集まる<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;0.1813;0.1815;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">T が十分小さくなったら、残りの区間は、見た目にほぼ影響しない<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1813;0.1815;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:cloud-raymarch:end -->

## レイマーチで、雲を、描く

<strong>雲</strong>は、<strong>空間に、密度が、分布する、ボリューム</strong>です。画面の、各画素から、視線を、雲の殻（[Cloud Layers](layers.md)）の中へ、少しずつ進み、各点で、密度と、光を、調べて、色を、積算します。レイマーチです。

## 全体の、骨格

```hlsl
float4 CloudPS(float2 uv : TEXCOORD0) : SV_Target {
  float3 ray_dir = ScreenToWorldDir(uv);
  float3 origin = g_camera_position_from_planet_center;
  float2 range = CloudLayerIntersect(origin, ray_dir);                  // 雲の殻との、交わる区間
  if (range.y <= range.x) return float4(0, 0, 0, 1);                    // 交わらない → 雲なし（透過率 1）
```

まず、<strong>視線が、雲の殻と、交わる区間</strong>（入口と出口）を、求めます（[Cloud Layers](layers.md)）。<strong>交わらなければ</strong>、雲は、ありません（色 0、透過率 1）。

```hlsl
  const int kSteps = 64;
  float distance_range = min(range.y - range.x, g_max_march_distance);  // 遠すぎる区間は、打ち切る
  float step_len = distance_range / kSteps;
  float t = range.x + step_len * InterleavedGradientNoise(uv * g_screen_size);   // 開始位置を、ノイズで、ずらす（ジッター）
```

<strong>区間を、64 に分け</strong>、<strong>開始位置を、ノイズで、ずらします</strong>（ジッター）。画素ごとに、違う位置から、始まるので、縞（バンディング）が、細かいノイズに、変わり、TAA で、なめらかに、ならされます（[Cloud Temporal Reprojection](temporal.md)）。

```hlsl
  float3 scattered = 0.0;                                               // 積算した、散乱光
  float transmittance = 1.0;                                            // ここまでの、透過率
  for (int i = 0; i < kSteps; ++i) {
    float3 p = origin + ray_dir * t;
    float density = CloudDensity(p);                                    // 密度（[Cloud Density Model]）
    if (density > 0.001) {
```

各ステップで、<strong>その点の、密度</strong>を、求めます。<strong>密度が、ほぼ 0</strong>（雲の、外）の点は、何も、しません（空の、部分は、スキップ）。

```hlsl
      float3 light = CloudLighting(p, ray_dir, density);                // その点で、視線の方向へ、散る光（[Cloud Lighting]）
      float sigma_t = density * g_extinction;                           // 消散係数
      float step_transmittance = exp(-sigma_t * step_len);
      // 区間内の、積分（解析的）: エネルギーを、保つ、形。
      float3 integral = (light - light * step_transmittance) / max(sigma_t, 1e-5);
      scattered += transmittance * integral;
      transmittance *= step_transmittance;
```

<strong>散乱光</strong>を、<strong>積算</strong>します。区間の中でも、光は、減るので、解析的な、積分（`(1 − exp(−σΔs)) / σ`）を、使うと、ステップが、粗くても、安定します（[Single-Scattering Integral](../scattering/single-scattering.md)）。透過率は、区間ごとに、掛けて、更新します。

```hlsl
      if (transmittance < 0.01) break;                                  // ほぼ、不透明になったら、打ち切る（以降は、見えない）
    }
    t += step_len;
  }
  return float4(scattered, transmittance);
}
```

<strong>透過率が、ほぼ 0</strong>（雲が、濃く、<strong>向こうが、見えない</strong>）なら、それ以上進んでも、結果が、変わらないので、打ち切ります（早期終了）。最後に、散乱光と、透過率を、返し、空の色（背景）を、透過率で、重ねます。

```hlsl
// 呼び出し側: 空の色（背景）に、雲を重ねる。
float4 cloud = CloudPS(uv);
float3 final_color = sky_color * cloud.a + cloud.rgb;                   // 背景 × 透過率 + 雲の散乱光
```

## ステップの、工夫（速くする）

64 ステップを、<strong>全画素</strong>で、回すと、重いです。<strong>無駄</strong>を、減らす、工夫です。

### ① 空の部分は、大きく進む

<strong>雲が、ない、空間</strong>（密度 0）では、<strong>細かく、進む必要が、ありません</strong>。粗い、サンプル（安い）で、密度を、調べ、雲に、入ったら、細かい、サンプル（重い）に、切り替えます。

```hlsl
// 2 段階: 最初は、粗い歩幅で、安い密度（基本の形だけ）を、調べる。雲に入ったら、細かい歩幅で、細部まで。
bool in_cloud = false;
float coarse_step = step_len * 2.0;
for (int i = 0; i < kSteps; ++i) {
  float3 p = origin + ray_dir * t;
  if (!in_cloud) {
    float coarse = CloudDensityCheap(p);                                // 基本の形だけ（細部のノイズを、読まない。安い）
    if (coarse > 0.0) { in_cloud = true; t -= coarse_step; continue; }  // 雲に入った → 1 歩戻って、細かく
    t += coarse_step;
  } else {
    // ... 通常の、細かい計算 ...
  }
}
```

<strong>空の部分</strong>は、<strong>基本の形だけの、安い密度</strong>で、大きな歩幅で、進み、雲に、当たったら、1 歩戻って、細かく、進みます。雲が、少ない画素では、大幅に、速くなります。

### ② 遠くほど、歩幅を、広げる

<strong>遠くの雲の、細部</strong>は、<strong>画面上で、小さく</strong>、見えません。距離に応じて、歩幅を、広げます。

```hlsl
float step_len = lerp(g_min_step, g_max_step, saturate((t - range.x) / g_step_growth_distance));
```

### ③ 低解像度で、描く

<strong>雲は、ふわふわ</strong>で、<strong>細かい、エッジが、少ない</strong>ので、画面の、1/4 の解像度（縦横、半分）で、描いて、アップサンプルしても、目立ちません（[Cloud Temporal Reprojection](temporal.md)）。

| 工夫 | 効果（目安） |
| --- | --- |
| 空の部分を、大きく進む | 2〜3 倍 速い（雲が、疎な画素で） |
| 遠くで、歩幅を、広げる | 約 1.5 倍 |
| 低解像度（1/4 の画素数） | 4 倍 |
| 時間方向の、更新の、間引き（1/16 の画素だけ、毎フレーム） | 16 倍（[Cloud Temporal Reprojection](temporal.md)） |
| 早期終了（透過率が、小さい） | 濃い雲で、大幅 |

## 視線の、起点

<strong>カメラが、雲の殻の中</strong>（飛行機）や、<strong>上</strong>（宇宙）にある場合、入口の位置が、変わります（[Cloud Layers](layers.md)）。どの場合でも、入口から、出口までの、区間を、マーチする、1 つの、コードで、書けます。

## よくあるミス

??? failure "雲に縞模様（バンディング）が出る"
    <strong>ジッタ</strong>を入れて、<strong>時間蓄積</strong>で消す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 進みながら足す。歩幅とジッタが鍵

## 参考

- Schneider, Vos, "The Real-Time Volumetric Cloudscapes of Horizon: Zero Dawn", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Schneider, "Nubis: Authoring Real-Time Volumetric Cloudscapes with the Decima Engine", SIGGRAPH 2017, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014（Interleaved Gradient Noise）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Clouds](index.md)
- [Cloud Lighting](lighting.md)
- [Cloud Temporal Reprojection](temporal.md)
