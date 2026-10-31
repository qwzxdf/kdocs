---
title: Chromatic Aberration
tags:
  - 描画
---

# Chromatic Aberration

<strong>色収差（Chromatic Aberration）</strong>は、レンズを通った光が波長（色）によって、わずかに違う位置に像を結ぶために起きる現象です。画面の端で物の輪郭が赤と青（または緑とマゼンタ）にずれて、にじんで見えます。カメラの欠点ですがゲームでは「ホラー・SF・ダメージ・サイバーパンク」などの演出として使われます。高品質になるわけではなく、完全に好みの問題です。このページでは、起きる理由・基本の実装・分散（多サンプル）による高品質版・かけ方（どこに・どれくらい）・演出での使い方を説明します。

!!! tip "ポイント"
    - 色収差 ＝ <strong>波長ごとに、屈折率が違い、赤・緑・青が少しずつずれて結像する</strong>。
    - <strong>画面の中心はほぼずれず、端ほど大きくずれる</strong>（距離の 2 乗に比例）。
    - 実装 ＝ R・G・B を中心から外へ（または逆に）ずらしてサンプル。
    - 高品質版は多数のサンプルを波長に応じてずらし、色に変換して積分する。
    - 強さは 0.005〜0.02 程度。強すぎると画面が溶けて見え、酔う。
    - 演出：被ダメージ・ワープ・ホラー・グリッチ。一時的に強くする。

!!! info "このページを読む前に"
    - [Lens Effects](index.md)（このセクション全体の地図と、読む順番）

## 起きる理由

<strong>ガラスの屈折率は、光の波長で少し違います</strong>（青は強く曲がり、赤は弱く曲がる）。そのため、レンズに入った白い光は、色ごとに少しずつ違う場所に像を結びます。

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="色収差の原理">
<text x="20" y="26" class="fig-title">青は強く曲がり、赤は弱く曲がるので、結像する位置が違う</text>
<line x1="40" y1="120" x2="700" y2="120" stroke="currentColor" stroke-opacity="0.3" stroke-dasharray="4 3"/>
<ellipse cx="300" cy="120" rx="16" ry="70" fill="#e0f2fe" stroke="currentColor" stroke-width="3"/>
<text x="270" y="40" style="font-size:12px">レンズ</text>
<g stroke-width="2.5" fill="none"><line x1="40" y1="75" x2="300" y2="75" stroke="#94a3b8"/><line x1="40" y1="165" x2="300" y2="165" stroke="#94a3b8"/>
<line x1="300" y1="75" x2="470" y2="120" stroke="#2563eb"/><line x1="300" y1="165" x2="470" y2="120" stroke="#2563eb"/>
<line x1="300" y1="75" x2="560" y2="120" stroke="#2ea043"/><line x1="300" y1="165" x2="560" y2="120" stroke="#2ea043"/>
<line x1="300" y1="75" x2="640" y2="120" stroke="#e5484d"/><line x1="300" y1="165" x2="640" y2="120" stroke="#e5484d"/></g>
<circle cx="470" cy="120" r="4" fill="#2563eb"/><circle cx="560" cy="120" r="4" fill="#2ea043"/><circle cx="640" cy="120" r="4" fill="#e5484d"/>
<text x="446" y="146" style="font-size:12px;fill:#2563eb">青の焦点</text><text x="534" y="146" style="font-size:12px;fill:#2ea043">緑</text><text x="622" y="146" style="font-size:12px;fill:#e5484d">赤の焦点</text>
<text x="40" y="206" style="font-size:12px">センサーの位置では、色ごとに像の大きさ・位置がずれる → 端で色のにじみ</text>
</svg>

色収差には 2 種類あります。軸上色収差は、色ごとにピントの位置が違うもので、ぼけた部分に色のにじみが出ます。倍率色収差は、色ごとに像の倍率が違うもので、画面の端で輪郭が色ずれします。ゲームで再現するのは、主に倍率色収差です。レンズの屈折率が波長ごとに違うことが原因です。

## 基本の実装

<strong>緑を基準に赤と青を画面中心からの距離に応じて、逆方向にずらしてサンプル</strong>します。

```hlsl
float3 ChromaticAberration(float2 uv, float intensity) {
  float2 center_offset = uv - 0.5;
  float distance_squared = dot(center_offset, center_offset);
  float2 shift = center_offset * distance_squared * intensity;

  float r = scene_color.SampleLevel(linear_clamp, uv + shift, 0).r;
  float g = scene_color.SampleLevel(linear_clamp, uv, 0).g;
  float b = scene_color.SampleLevel(linear_clamp, uv - shift, 0).b;
  return float3(r, g, b);
}
```

ずらし方のコードの要点です。`center_offset × distance_squared` は、中心はほぼ 0、周辺で急に大きくなる量で、実際のレンズの特性に近づきます。R と B を逆方向にずらし、緑を基準に赤は外へ青は内へずらすと、縁取りの色の順序が現実に近くなります。`intensity` は強さで、0.005〜0.02 です。

<!-- fig:chromatic-aberration-compare:begin -->

<svg class="fig illust motion" data-fig="chromatic-aberration-compare" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-chromatic-aberration-compare" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">色収差の作り方: 3 色だけをずらす方法(速い)と、スペクトルを細かくたどる方法(きれい)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">白と黒の縁。ずらす量は同じ(8 画素)。3 サンプル(R・G・B のみ)と 9 サンプル(波長を等間隔)の、縁の見え方を比べる</text>
<text x="60.0" y="108" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">元の縁(白と黒)</text>
<rect x="60.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="80.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="100.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="120.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="140.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="160.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="180.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="200.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="220.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="240.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="260.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="280.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="300.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="320.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="340.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="360.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="380.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="400.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="420.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="440.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="460.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="480.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="500.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="520.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="540.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="560.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="580.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="600.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="620.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="640.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="660.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="680.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="700.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="720.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="740.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="760.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="780.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="800.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="820.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="840.0" y="112.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="60.0" y="112" width="800.0" height="34.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="178" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">3 サンプル(R・G・B をずらす)</text>
<rect x="60.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#000000"/></rect>
<rect x="80.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721" values="#e5e7eb;#000000"/></rect>
<rect x="100.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#000000"/></rect>
<rect x="120.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#e5e7eb;#000000"/></rect>
<rect x="140.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#000000"/></rect>
<rect x="160.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0814" values="#e5e7eb;#000000"/></rect>
<rect x="180.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#000000"/></rect>
<rect x="200.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0860" values="#e5e7eb;#000000"/></rect>
<rect x="220.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#000000"/></rect>
<rect x="240.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#e5e7eb;#000000"/></rect>
<rect x="260.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#000000"/></rect>
<rect x="280.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0953" values="#e5e7eb;#000000"/></rect>
<rect x="300.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#0000ff"/></rect>
<rect x="320.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000" values="#e5e7eb;#0000ff"/></rect>
<rect x="340.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#0000ff"/></rect>
<rect x="360.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047" values="#e5e7eb;#0000ff"/></rect>
<rect x="380.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#0000ff"/></rect>
<rect x="400.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093" values="#e5e7eb;#0000ff"/></rect>
<rect x="420.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#0000ff"/></rect>
<rect x="440.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1140" values="#e5e7eb;#0000ff"/></rect>
<rect x="460.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#00ffff"/></rect>
<rect x="480.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186" values="#e5e7eb;#00ffff"/></rect>
<rect x="500.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#00ffff"/></rect>
<rect x="520.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233" values="#e5e7eb;#00ffff"/></rect>
<rect x="540.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#e5e7eb;#00ffff"/></rect>
<rect x="560.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1279" values="#e5e7eb;#00ffff"/></rect>
<rect x="580.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1302" values="#e5e7eb;#00ffff"/></rect>
<rect x="600.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1326" values="#e5e7eb;#00ffff"/></rect>
<rect x="620.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1349" values="#e5e7eb;#ffffff"/></rect>
<rect x="640.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1372" values="#e5e7eb;#ffffff"/></rect>
<rect x="660.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1395" values="#e5e7eb;#ffffff"/></rect>
<rect x="680.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1419" values="#e5e7eb;#ffffff"/></rect>
<rect x="700.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1442" values="#e5e7eb;#ffffff"/></rect>
<rect x="720.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1465" values="#e5e7eb;#ffffff"/></rect>
<rect x="740.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1488" values="#e5e7eb;#ffffff"/></rect>
<rect x="760.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1512" values="#e5e7eb;#ffffff"/></rect>
<rect x="780.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1535" values="#e5e7eb;#ffffff"/></rect>
<rect x="800.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1558" values="#e5e7eb;#ffffff"/></rect>
<rect x="820.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1581" values="#e5e7eb;#ffffff"/></rect>
<rect x="840.0" y="182.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1605" values="#e5e7eb;#ffffff"/></rect>
<rect x="60.0" y="182" width="800.0" height="34.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="248" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">9 サンプル(波長をたどる)</text>
<rect x="60.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2558" values="#e5e7eb;#000000"/></rect>
<rect x="80.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2581" values="#e5e7eb;#000000"/></rect>
<rect x="100.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2605" values="#e5e7eb;#000000"/></rect>
<rect x="120.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2628" values="#e5e7eb;#000000"/></rect>
<rect x="140.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2651" values="#e5e7eb;#000000"/></rect>
<rect x="160.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2674" values="#e5e7eb;#000000"/></rect>
<rect x="180.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#e5e7eb;#000000"/></rect>
<rect x="200.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2721" values="#e5e7eb;#000000"/></rect>
<rect x="220.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2744" values="#e5e7eb;#000000"/></rect>
<rect x="240.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2767" values="#e5e7eb;#000000"/></rect>
<rect x="260.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#000000"/></rect>
<rect x="280.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2814" values="#e5e7eb;#000000"/></rect>
<rect x="300.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2837" values="#e5e7eb;#6d0000"/></rect>
<rect x="320.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2860" values="#e5e7eb;#6d0000"/></rect>
<rect x="340.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2884" values="#e5e7eb;#bb0c00"/></rect>
<rect x="360.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#bb0c00"/></rect>
<rect x="380.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2930" values="#e5e7eb;#ec2b00"/></rect>
<rect x="400.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2953" values="#e5e7eb;#ec2b00"/></rect>
<rect x="420.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2977" values="#e5e7eb;#ff5d00"/></rect>
<rect x="440.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3000" values="#e5e7eb;#ff5d00"/></rect>
<rect x="460.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3023" values="#e5e7eb;#ffa200"/></rect>
<rect x="480.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3047" values="#e5e7eb;#ffa200"/></rect>
<rect x="500.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3070" values="#e5e7eb;#ffd413"/></rect>
<rect x="520.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3093" values="#e5e7eb;#ffd413"/></rect>
<rect x="540.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3116" values="#e5e7eb;#fff344"/></rect>
<rect x="560.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3140" values="#e5e7eb;#fff344"/></rect>
<rect x="580.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3163" values="#e5e7eb;#ffff92"/></rect>
<rect x="600.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3186" values="#e5e7eb;#ffff92"/></rect>
<rect x="620.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3209" values="#e5e7eb;#ffffff"/></rect>
<rect x="640.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3233" values="#e5e7eb;#ffffff"/></rect>
<rect x="660.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3256" values="#e5e7eb;#ffffff"/></rect>
<rect x="680.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3279" values="#e5e7eb;#ffffff"/></rect>
<rect x="700.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3302" values="#e5e7eb;#ffffff"/></rect>
<rect x="720.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3326" values="#e5e7eb;#ffffff"/></rect>
<rect x="740.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3349" values="#e5e7eb;#ffffff"/></rect>
<rect x="760.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3372" values="#e5e7eb;#ffffff"/></rect>
<rect x="780.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3395" values="#e5e7eb;#ffffff"/></rect>
<rect x="800.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3419" values="#e5e7eb;#ffffff"/></rect>
<rect x="820.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3442" values="#e5e7eb;#ffffff"/></rect>
<rect x="840.0" y="252.0" width="20.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3465" values="#e5e7eb;#ffffff"/></rect>
<rect x="60.0" y="252" width="800.0" height="34.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="30" y="320" width="900" height="150" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="310" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">比べる</text>
<text x="50" y="358" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">縁にできる色の段階<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4649;0.4651;1.0000" values="0;0;1;1"/></text>
<text x="330" y="358" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">3 サンプル: 4 段階(帯がはっきり)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4649;0.4651;1.0000" values="0;0;1;1"/></text>
<text x="640" y="358" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">9 サンプル: 10 段階(なめらかな虹)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4649;0.4651;1.0000" values="0;0;1;1"/></text>
<text x="50" y="402" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 画素あたりの読み込み<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5207;0.5209;1.0000" values="0;0;1;1"/></text>
<text x="330" y="402" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">3 サンプル: 3 回<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5207;0.5209;1.0000" values="0;0;1;1"/></text>
<text x="640" y="402" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">9 サンプル: 9 回(3 倍)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5207;0.5209;1.0000" values="0;0;1;1"/></text>
<text x="50" y="450" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb" opacity="0">ゲームでは、まず 3 サンプルで十分。大きなずれでは、帯が目立つので、サンプルを増やす<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6045;0.6047;1.0000" values="0;0;1;1"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">色収差は、色ごとに、ずれる量が違う<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">3 色だけずらすと、縁が 3 つの帯になる。多く取ると、連続した虹になる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.4649;0.4651;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ずらす量が小さければ 3 サンプル、大きければ多サンプル<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4649;0.4651;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:chromatic-aberration-compare:end -->

## 高品質版：多サンプル

<strong>3 チャンネルだけをずらす</strong>と、縁取りが赤と青の 2 色で、くっきり段になります。実際のレンズでは、波長ごとに連続的にずれるので、縁取りが虹のように滑らかです。

```hlsl
float3 ChromaticAberrationSpectral(float2 uv, float intensity) {
  float2 center_offset = uv - 0.5;
  float distance_squared = dot(center_offset, center_offset);
  float3 sum = 0;
  float3 weight_sum = 0;
  const int kSamples = 8;
  for (int i = 0; i < kSamples; ++i) {
    float t = i / (kSamples - 1.0);
    float2 shift = center_offset * distance_squared * intensity * (t * 2.0 - 1.0);
    float3 wavelength_weight = float3(saturate(1.0 - 2.0 * t), 1.0 - abs(2.0 * t - 1.0), saturate(2.0 * t - 1.0));
    sum += scene_color.SampleLevel(linear_clamp, uv + shift, 0).rgb * wavelength_weight;
    weight_sum += wavelength_weight;
  }
  return sum / weight_sum;
}
```

| 点 | 説明 |
| --- | --- |
| `t` | 波長（0 ＝ 青側、1 ＝ 赤側） |
| `wavelength_weight` | その波長が RGB のどれに寄与するか（簡易的な波長 → 色の変換） |
| サンプル数 | 8 程度。多いほど虹が滑らか |
| 正規化 | 重みの合計で割る（明るさを保つ） |

## 使い方

| 設定 | 内容 |
| --- | --- |
| 強さ | <strong>控えめ（0.005〜0.01）</strong>で、カメラらしさ。強め（0.02〜0.05）で、演出 |
| 範囲 | 画面全体に距離の 2 乗で。中心はほぼ無効 |
| 向き | 画面中心から放射状（倍率色収差） |
| 順序 | トーンマップ後（LDR）にかける |

### 演出での使い方

| 場面 | 使い方 |
| --- | --- |
| ダメージを受けた | 一瞬、強い色収差（0.03〜0.05） → すぐ戻す |
| ワープ・加速 | 強度を速度に比例 |
| ホラー・幻覚 | 不安定に揺らす（時間でノイズ） |
| グリッチ | 横方向だけ、大きくずらす |
| サイバーパンク | 常時、控えめにかける |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| 距離の 2 乗でずらす | <strong>中心がくっきり、端でにじむ（自然）</strong> |
| 多サンプルで虹のように | 高品質（コストに余裕があれば） |
| LDR でトーンマップ後に | 見た目の色にかける |
| 他のパスと統合 | ビネット・グレイン・トーンマップと 1 パス |
| オプションで切れる／強さ調整 | 酔いやすい人・アクセシビリティ |
| UI の前に | 文字が色ずれしない |

## よくあるミス

??? failure "強くしすぎて、画面が溶けて見え、酔う"
    <strong>0.005〜0.02</strong>。オプションで調整できるように。

??? failure "画面中心まで色がずれて、全体がぼやける"
    距離の 2 乗をかけ、中心は 0 に近くする。

??? failure "UI の文字まで色ずれして、読みにくい"
    UI は色収差の後に描く。

??? failure "縁取りが赤と青の 2 色だけで、安っぽい"
    多サンプル（スペクトル）版にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 色収差 ＝ <strong>波長ごとに屈折が違い、画面の端で赤・緑・青がずれる</strong>
    - [x] 実装 ＝ 緑を基準に赤・青を中心から逆方向へずらす。距離の 2 乗
    - [x] 多サンプル（波長）で虹のように滑らか
    - [x] 控えめに（0.005〜0.02）。演出では一時的に強く
    - [x] 表現の好み。設定で切れるように

## 参考

- Wikipedia, "Chromatic aberration"
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Pharr, Jakob, Humphreys, "Physically Based Rendering"（レンズのモデル）

## 関連ページ

- [Lens Effects](index.md)
- [Vignette](vignette.md)
- [Film Grain](film-grain.md)
- [Depth of Field (DOF)](../dof/index.md)
