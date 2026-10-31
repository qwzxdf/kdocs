---
title: Cel Shading
tags:
  - 描画
---

# Cel Shading

<strong>セル シェーディング（トゥーン シェーディング）</strong>は、陰影を滑らかなグラデーションではなく、数段階（2〜3 段）に区切る表現です。手描きアニメの「セル画」のように、「明るい面」「影の面」がくっきり分かれるので、アニメ調の絵になります。ライティングの結果（明るさ）を段階に変換する関数が核で、ランプ テクスチャで自由に調整できます。写実的な高品質とは別の方向の表現で、画風に合うかどうかが基準です。このページでは、基本の段階化・ランプ テクスチャ・なめらかな境・スペキュラとリム ライト・影の色・影を受けるときの扱いを説明します。

!!! tip "ポイント"
    - セル シェーディング ＝ <strong>ライティングの明るさを数段階に区切る</strong>。
    - 基本 ＝ <strong>`N·L`（拡散）をしきい値で段階化</strong>。`step` や `smoothstep`。
    - ランプ テクスチャ：`N·L` を座標に色を引く 1D テクスチャ。アーティストが段階を自由に調整できる。
    - 境を少しぼかす（`smoothstep`）とちらつき・ジャギーが減る。
    - 影の色を暗い灰色でなく、色相を変えた暗い色に。
    - スペキュラはしきい値で、くっきりした白いハイライト。リム ライトで輪郭を明るく。

!!! info "このページを読む前に"
    - [Outlines and Toon](index.md)（このセクション全体の地図と、読む順番）

## 基本：N·L を段階化

<strong>普通のライティング</strong>は、`N·L`（法線と光の向きの内積）で、明るさが滑らかに変わります。セルではこれをしきい値で数段階に変換します。

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="セル シェーディング">
<text x="20" y="26" class="fig-title">滑らかな明るさを段階に区切る</text>
<defs><linearGradient id="cs-smooth" x1="0" x2="1"><stop offset="0" stop-color="#1e293b"/><stop offset="1" stop-color="#f8e9c8"/></linearGradient></defs>
<g transform="translate(40,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">通常（滑らか）</text>
<circle cx="90" cy="70" r="62" fill="url(#cs-smooth)"/>
</g>
<g transform="translate(280,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">2 段（明・影）</text>
<circle cx="90" cy="70" r="62" fill="#f8e9c8"/><path d="M90,8 A62,62 0 0 0 90,132 Z" fill="#8a7a90" transform="translate(20,0)"/>
</g>
<g transform="translate(520,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">3 段（明・中・影）</text>
<circle cx="90" cy="70" r="62" fill="#f8e9c8"/><circle cx="90" cy="70" r="62" fill="#b5a3a8" clip-path="inset(0 0 0 0)" opacity="0"/>
<path d="M90,8 A62,62 0 0 0 90,132 Z" fill="#b5a3a8" transform="translate(30,0)"/><path d="M90,8 A62,62 0 0 0 90,132 Z" fill="#6f5f78" transform="translate(5,0)"/>
</g>
</svg>

```hlsl
float3 CelShade(float3 albedo, float3 normal, float3 light_dir, float3 light_color) {
  float n_dot_l = dot(normal, light_dir);
  float lit = step(0.0, n_dot_l);
  float3 shadow_color = albedo * float3(0.55, 0.5, 0.7);
  return lerp(shadow_color, albedo * light_color, lit);
}
```

2 段階のセル シェーディングのコードの要点です。`step(0, N·L)` は、光に向いていれば 1、背を向けていれば 0 で、2 段になります。`shadow_color` は影の色で、暗い灰色でなく、色味のある暗い色にします。`lerp` で、影と明部を切り替えます。

## なめらかな境

<strong>`step` は境がジャギーで、動くとちらつきます</strong>。境を少しだけぼかす（`smoothstep`）ときれいです。

```hlsl
float Toon(float n_dot_l, float threshold, float softness) {
  return smoothstep(threshold - softness, threshold + softness, n_dot_l);
}
```

`softness` による見た目です。0.0〜0.01 はほぼシャープで、アニメ調になります。0.05〜0.1 は少し柔らかく、水彩やイラスト調になります。

## ランプ テクスチャ

<strong>`N·L`（0〜1 に直したもの）を座標に色を引く 1D テクスチャ</strong>です。アーティストが段階の数・境の位置・色の変化を自由に描けます。

```hlsl
Texture2D ramp_texture : register(t3);

float3 CelShadeRamp(float3 albedo, float3 normal, float3 light_dir) {
  float n_dot_l = dot(normal, light_dir) * 0.5 + 0.5;
  float3 ramp = ramp_texture.SampleLevel(clamp_linear, float2(n_dot_l, 0.5), 0).rgb;
  return albedo * ramp;
}
```

ランプ テクスチャのコードの要点です。`N·L × 0.5 + 0.5` で、−1〜1 を 0〜1 にします（ハーフ ランバート）。ランプの形は、階段状の画像をバイリニアでサンプルして作ります。利点は、コードを変えずに画風を変えられることで、キャラクターごとにランプを差し替えられます。

<!-- fig:cel-ramp:begin -->

<svg class="fig illust motion" data-fig="cel-ramp" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-cel-ramp" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">セル シェーディング: N·L を段に区切ると、アニメ調の影になる。段数でタッチが変わる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">球の断面(光は左上)。N·L を 2・3・4 段に区切って塗る。なめらかな陰影と、どれだけ違うかを計算する</text>
<text x="60.0" y="108" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">なめらか(通常)</text>
<rect x="60.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="74.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0712" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="89.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0726" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="103.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="118.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="132.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="147.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="161.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="176.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#2c2c2c"/></rect>
<rect x="190.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0823" values="#e5e7eb;#393939"/></rect>
<rect x="205.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#464646"/></rect>
<rect x="219.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0851" values="#e5e7eb;#525252"/></rect>
<rect x="234.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#e5e7eb;#5f5f5f"/></rect>
<rect x="248.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0879" values="#e5e7eb;#6b6b6b"/></rect>
<rect x="263.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#e5e7eb;#777777"/></rect>
<rect x="277.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#e5e7eb;#838383"/></rect>
<rect x="292.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#e5e7eb;#8f8f8f"/></rect>
<rect x="306.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0935" values="#e5e7eb;#9a9a9a"/></rect>
<rect x="321.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#e5e7eb;#a5a5a5"/></rect>
<rect x="335.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963" values="#e5e7eb;#afafaf"/></rect>
<rect x="350.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#b9b9b9"/></rect>
<rect x="364.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0991" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="379.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#e5e7eb;#cbcbcb"/></rect>
<rect x="393.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1019" values="#e5e7eb;#d3d3d3"/></rect>
<rect x="408.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#e5e7eb;#dadada"/></rect>
<rect x="422.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047" values="#e5e7eb;#e1e1e1"/></rect>
<rect x="437.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#e5e7eb;#e7e7e7"/></rect>
<rect x="451.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1074" values="#e5e7eb;#ededed"/></rect>
<rect x="466.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#e5e7eb;#f1f1f1"/></rect>
<rect x="480.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#e5e7eb;#f6f6f6"/></rect>
<rect x="495.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#f9f9f9"/></rect>
<rect x="509.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1130" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="524.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#e5e7eb;#fdfdfd"/></rect>
<rect x="538.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1158" values="#e5e7eb;#ffffff"/></rect>
<rect x="553.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#e5e7eb;#ffffff"/></rect>
<rect x="567.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186" values="#e5e7eb;#ffffff"/></rect>
<rect x="582.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#fdfdfd"/></rect>
<rect x="596.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1214" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="611.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#e5e7eb;#f9f9f9"/></rect>
<rect x="625.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1242" values="#e5e7eb;#f6f6f6"/></rect>
<rect x="640.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#e5e7eb;#f1f1f1"/></rect>
<rect x="654.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1270" values="#e5e7eb;#ededed"/></rect>
<rect x="669.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#e5e7eb;#e7e7e7"/></rect>
<rect x="683.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1298" values="#e5e7eb;#e1e1e1"/></rect>
<rect x="698.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#e5e7eb;#dadada"/></rect>
<rect x="712.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1326" values="#e5e7eb;#d3d3d3"/></rect>
<rect x="727.0" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1340" values="#e5e7eb;#cbcbcb"/></rect>
<rect x="741.5" y="112.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1353" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="60.0" y="112" width="696.0" height="34.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1440;0.1442;1.0000" values="0;0;1;1"/></g>
<text x="60.0" y="170" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">2 段</text>
<rect x="60.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2558" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="74.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2572" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="89.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2586" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="103.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2600" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="118.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2614" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="132.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2628" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="147.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2642" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="161.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2656" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="176.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2670" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="190.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2684" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="205.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="219.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2712" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="234.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2726" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="248.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2740" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="263.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2753" values="#e5e7eb;#ffffff"/></rect>
<rect x="277.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2767" values="#e5e7eb;#ffffff"/></rect>
<rect x="292.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2781" values="#e5e7eb;#ffffff"/></rect>
<rect x="306.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2795" values="#e5e7eb;#ffffff"/></rect>
<rect x="321.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#e5e7eb;#ffffff"/></rect>
<rect x="335.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2823" values="#e5e7eb;#ffffff"/></rect>
<rect x="350.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2837" values="#e5e7eb;#ffffff"/></rect>
<rect x="364.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2851" values="#e5e7eb;#ffffff"/></rect>
<rect x="379.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2865" values="#e5e7eb;#ffffff"/></rect>
<rect x="393.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2879" values="#e5e7eb;#ffffff"/></rect>
<rect x="408.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2893" values="#e5e7eb;#ffffff"/></rect>
<rect x="422.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#ffffff"/></rect>
<rect x="437.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2921" values="#e5e7eb;#ffffff"/></rect>
<rect x="451.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2935" values="#e5e7eb;#ffffff"/></rect>
<rect x="466.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2949" values="#e5e7eb;#ffffff"/></rect>
<rect x="480.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963" values="#e5e7eb;#ffffff"/></rect>
<rect x="495.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2977" values="#e5e7eb;#ffffff"/></rect>
<rect x="509.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2991" values="#e5e7eb;#ffffff"/></rect>
<rect x="524.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3005" values="#e5e7eb;#ffffff"/></rect>
<rect x="538.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3019" values="#e5e7eb;#ffffff"/></rect>
<rect x="553.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3033" values="#e5e7eb;#ffffff"/></rect>
<rect x="567.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3047" values="#e5e7eb;#ffffff"/></rect>
<rect x="582.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3060" values="#e5e7eb;#ffffff"/></rect>
<rect x="596.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3074" values="#e5e7eb;#ffffff"/></rect>
<rect x="611.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3088" values="#e5e7eb;#ffffff"/></rect>
<rect x="625.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3102" values="#e5e7eb;#ffffff"/></rect>
<rect x="640.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3116" values="#e5e7eb;#ffffff"/></rect>
<rect x="654.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3130" values="#e5e7eb;#ffffff"/></rect>
<rect x="669.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3144" values="#e5e7eb;#ffffff"/></rect>
<rect x="683.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3158" values="#e5e7eb;#ffffff"/></rect>
<rect x="698.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3172" values="#e5e7eb;#ffffff"/></rect>
<rect x="712.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3186" values="#e5e7eb;#ffffff"/></rect>
<rect x="727.0" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3200" values="#e5e7eb;#ffffff"/></rect>
<rect x="741.5" y="174.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3214" values="#e5e7eb;#ffffff"/></rect>
<rect x="60.0" y="174" width="696.0" height="34.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3300;0.3302;1.0000" values="0;0;1;1"/><text x="766.0" y="188" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">なめらかとの差 0.147</text>
<text x="766.0" y="206" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">境目 1 本</text>
</g>
<text x="60.0" y="232" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">3 段</text>
<rect x="60.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4419" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="74.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4433" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="89.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4447" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="103.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4460" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="118.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="132.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4488" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="147.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4502" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="161.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4516" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="176.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4530" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="190.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4544" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="205.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4558" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="219.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4572" values="#e5e7eb;#8f8f8f"/></rect>
<rect x="234.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4586" values="#e5e7eb;#8f8f8f"/></rect>
<rect x="248.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4600" values="#e5e7eb;#8f8f8f"/></rect>
<rect x="263.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4614" values="#e5e7eb;#8f8f8f"/></rect>
<rect x="277.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4628" values="#e5e7eb;#8f8f8f"/></rect>
<rect x="292.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4642" values="#e5e7eb;#8f8f8f"/></rect>
<rect x="306.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4656" values="#e5e7eb;#8f8f8f"/></rect>
<rect x="321.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4670" values="#e5e7eb;#8f8f8f"/></rect>
<rect x="335.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4684" values="#e5e7eb;#ffffff"/></rect>
<rect x="350.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4698" values="#e5e7eb;#ffffff"/></rect>
<rect x="364.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4712" values="#e5e7eb;#ffffff"/></rect>
<rect x="379.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4726" values="#e5e7eb;#ffffff"/></rect>
<rect x="393.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4740" values="#e5e7eb;#ffffff"/></rect>
<rect x="408.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4753" values="#e5e7eb;#ffffff"/></rect>
<rect x="422.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4767" values="#e5e7eb;#ffffff"/></rect>
<rect x="437.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4781" values="#e5e7eb;#ffffff"/></rect>
<rect x="451.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4795" values="#e5e7eb;#ffffff"/></rect>
<rect x="466.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#e5e7eb;#ffffff"/></rect>
<rect x="480.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4823" values="#e5e7eb;#ffffff"/></rect>
<rect x="495.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4837" values="#e5e7eb;#ffffff"/></rect>
<rect x="509.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4851" values="#e5e7eb;#ffffff"/></rect>
<rect x="524.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4865" values="#e5e7eb;#ffffff"/></rect>
<rect x="538.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4879" values="#e5e7eb;#ffffff"/></rect>
<rect x="553.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4893" values="#e5e7eb;#ffffff"/></rect>
<rect x="567.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#e5e7eb;#ffffff"/></rect>
<rect x="582.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4921" values="#e5e7eb;#ffffff"/></rect>
<rect x="596.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4935" values="#e5e7eb;#ffffff"/></rect>
<rect x="611.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4949" values="#e5e7eb;#ffffff"/></rect>
<rect x="625.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963" values="#e5e7eb;#ffffff"/></rect>
<rect x="640.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4977" values="#e5e7eb;#ffffff"/></rect>
<rect x="654.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4991" values="#e5e7eb;#ffffff"/></rect>
<rect x="669.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5005" values="#e5e7eb;#ffffff"/></rect>
<rect x="683.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5019" values="#e5e7eb;#ffffff"/></rect>
<rect x="698.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5033" values="#e5e7eb;#ffffff"/></rect>
<rect x="712.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5047" values="#e5e7eb;#ffffff"/></rect>
<rect x="727.0" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5060" values="#e5e7eb;#ffffff"/></rect>
<rect x="741.5" y="236.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5074" values="#e5e7eb;#ffffff"/></rect>
<rect x="60.0" y="236" width="696.0" height="34.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5161;0.5163;1.0000" values="0;0;1;1"/><text x="766.0" y="250" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">なめらかとの差 0.097</text>
<text x="766.0" y="268" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">境目 2 本</text>
</g>
<text x="60.0" y="294" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">4 段</text>
<rect x="60.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6279" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="74.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6293" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="89.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6307" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="103.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6321" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="118.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6335" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="132.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6349" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="147.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6363" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="161.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6377" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="176.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6391" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="190.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6405" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="205.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6419" values="#e5e7eb;#696969"/></rect>
<rect x="219.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6433" values="#e5e7eb;#696969"/></rect>
<rect x="234.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6447" values="#e5e7eb;#696969"/></rect>
<rect x="248.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6460" values="#e5e7eb;#696969"/></rect>
<rect x="263.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6474" values="#e5e7eb;#696969"/></rect>
<rect x="277.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6488" values="#e5e7eb;#b4b4b4"/></rect>
<rect x="292.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6502" values="#e5e7eb;#b4b4b4"/></rect>
<rect x="306.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6516" values="#e5e7eb;#b4b4b4"/></rect>
<rect x="321.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6530" values="#e5e7eb;#b4b4b4"/></rect>
<rect x="335.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6544" values="#e5e7eb;#b4b4b4"/></rect>
<rect x="350.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6558" values="#e5e7eb;#b4b4b4"/></rect>
<rect x="364.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6572" values="#e5e7eb;#ffffff"/></rect>
<rect x="379.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6586" values="#e5e7eb;#ffffff"/></rect>
<rect x="393.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6600" values="#e5e7eb;#ffffff"/></rect>
<rect x="408.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6614" values="#e5e7eb;#ffffff"/></rect>
<rect x="422.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6628" values="#e5e7eb;#ffffff"/></rect>
<rect x="437.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6642" values="#e5e7eb;#ffffff"/></rect>
<rect x="451.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6656" values="#e5e7eb;#ffffff"/></rect>
<rect x="466.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6670" values="#e5e7eb;#ffffff"/></rect>
<rect x="480.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6684" values="#e5e7eb;#ffffff"/></rect>
<rect x="495.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6698" values="#e5e7eb;#ffffff"/></rect>
<rect x="509.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6712" values="#e5e7eb;#ffffff"/></rect>
<rect x="524.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6726" values="#e5e7eb;#ffffff"/></rect>
<rect x="538.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6740" values="#e5e7eb;#ffffff"/></rect>
<rect x="553.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6753" values="#e5e7eb;#ffffff"/></rect>
<rect x="567.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6767" values="#e5e7eb;#ffffff"/></rect>
<rect x="582.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6781" values="#e5e7eb;#ffffff"/></rect>
<rect x="596.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6795" values="#e5e7eb;#ffffff"/></rect>
<rect x="611.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6809" values="#e5e7eb;#ffffff"/></rect>
<rect x="625.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6823" values="#e5e7eb;#ffffff"/></rect>
<rect x="640.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6837" values="#e5e7eb;#ffffff"/></rect>
<rect x="654.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6851" values="#e5e7eb;#ffffff"/></rect>
<rect x="669.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6865" values="#e5e7eb;#ffffff"/></rect>
<rect x="683.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6879" values="#e5e7eb;#ffffff"/></rect>
<rect x="698.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6893" values="#e5e7eb;#ffffff"/></rect>
<rect x="712.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#e5e7eb;#ffffff"/></rect>
<rect x="727.0" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6921" values="#e5e7eb;#ffffff"/></rect>
<rect x="741.5" y="298.0" width="14.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6935" values="#e5e7eb;#ffffff"/></rect>
<rect x="60.0" y="298" width="696.0" height="34.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7021;0.7023;1.0000" values="0;0;1;1"/><text x="766.0" y="312" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">なめらかとの差 0.080</text>
<text x="766.0" y="330" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">境目 3 本</text>
</g>
<rect x="30" y="372" width="900" height="110" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="362" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">段のしきい値と、タッチ</text>
<text x="50" y="416" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="0">2 段<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.8277;0.8279;1.0000" values="0;0;1;1"/></text>
<text x="130" y="416" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937" opacity="0">N·L ≥ 0.35 で、明るい。それ以外は、影。はっきりしたマンガ調<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.8277;0.8279;1.0000" values="0;0;1;1"/></text>
<text x="50" y="438" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043" opacity="0">3 段<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.8742;0.8744;1.0000" values="0;0;1;1"/></text>
<text x="130" y="438" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937" opacity="0">明・中・影。もっとも標準的なアニメ調<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.8742;0.8744;1.0000" values="0;0;1;1"/></text>
<text x="50" y="460" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb" opacity="0">4 段<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.9207;0.9209;1.0000" values="0;0;1;1"/></text>
<text x="130" y="460" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937" opacity="0">段が多い分、なめらかに近づく。グラデーション寄り<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.9207;0.9209;1.0000" values="0;0;1;1"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">なめらかな陰影を段に区切る<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">段が少ないほど、くっきり。多いほど、なめらかに近づく<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.8277;0.8279;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">段の境目の位置(しきい値)で、影の形が決まる。ランプ画像で、アーティストが調整する<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.8277;0.8279;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:cel-ramp:end -->

## 影の色

<strong>影を単純に「暗くする」と、絵が重く、汚く見えます</strong>。影は色相を少し変え、彩度を保った、暗い色にするとアニメ的です。

| 影の付け方 | 見た目 |
| --- | --- |
| 単純に暗く（× 0.5） | 灰色っぽく、汚い |
| 色相をずらす（青・紫寄り） | アニメ調の澄んだ影 |
| 肌：赤みを保つ | 健康的な肌 |
| アルベドごとの影色 | 材質ごとに別の影の色（テクスチャ・パラメータ） |

```hlsl
float3 shadow_tint = lerp(float3(1, 1, 1), float3(0.6, 0.55, 0.85), shadow_strength);
float3 shaded = albedo * shadow_tint;
```

## スペキュラとリム ライト

スペキュラとリム ライトの要素です。スペキュラは、ハーフ ベクトルとの内積をしきい値で 2 値化して、くっきりした白いハイライトにします。リム ライトは、視線と法線が直角に近い所（輪郭付近）を明るくして、輪郭を際立たせます。

```hlsl
float ToonSpecular(float3 normal, float3 view_dir, float3 light_dir, float shininess, float threshold) {
  float3 half_vector = normalize(light_dir + view_dir);
  float n_dot_h = saturate(dot(normal, half_vector));
  return step(threshold, pow(n_dot_h, shininess));
}

float RimLight(float3 normal, float3 view_dir, float power, float threshold) {
  float rim = 1.0 - saturate(dot(normal, view_dir));
  return step(threshold, pow(rim, power));
}
```

コードの要点です。`step(threshold, pow(...))` で、くっきりしたはっきりした形のハイライトになります。リム ライトは、輪郭が背景から浮き出る効果で、暗い背景で特に効きます。光の向きに沿ったリムだけにすると自然です（`rim × N·L`）。

## 影を受ける

<strong>シャドウ マップの影</strong>（[Shadows](../../shadows/index.md)）をセルの陰影に取り込むには影の判定値（0〜1）を `N·L` と掛け合わせます。

```hlsl
float shadow = SampleShadow(world_position);
float n_dot_l = dot(normal, light_dir);
float toon_input = n_dot_l * shadow;
float lit = smoothstep(0.0, 0.02, toon_input);
```

シャドウ マップの境が PCF などで柔らかいと、セルの境がぎざぎざになるので、境の硬さを合わせる（影も段階化する）のがよいです。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| ランプ テクスチャ | アーティストが画風を調整 |
| 影色を色相を変えた暗い色に | 澄んだ影 |
| `smoothstep` で境を滑らかに | ジャギー・ちらつきを防ぐ |
| 輪郭線と併用 | <strong>アウトライン（[Inverted Hull Outlines](outline-hull.md)・[Screen-Space Edge Detection](outline-edge.md)）</strong> |
| ライトの扱いをメイン ライトのみに | 複数ライトを段階化すると複雑 |
| 顔の影を別に調整 | 顔の陰影は法線を補正（顔の影が汚くならない） |
| キャラごとのランプ・影色 | 材質ごとのパラメータ |

## よくあるミス

??? failure "影の境がジャギー・ちらつく"
    <strong>`smoothstep` で、狭い範囲をぼかす</strong>。

??? failure "影が灰色っぽく、絵が汚い"
    影色に色相を持たせる。

??? failure "複数のライトを全部段階化して、ごちゃごちゃする"
    メイン ライトだけセル化し、他は弱い環境光に。

??? failure "顔に鼻や顎の汚い影が出る"
    顔の法線を平らにする（法線の補正）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] セル シェーディング ＝ <strong>ライティングの明るさを数段階に区切る</strong>
    - [x] `N·L` をしきい値で段階化。`smoothstep` で境を滑らかに
    - [x] ランプ テクスチャで画風を自由に調整
    - [x] 影は、色相を変えた暗い色に
    - [x] スペキュラ・リム ライトは、くっきり。輪郭線と併用

## 参考

- Xu et al., "Guilty Gear Xrd's Art Style: The X Factor Between 2D and 3D"（GDC 2015）
- Lake et al., "Stylized Rendering Techniques for Scalable Real-Time 3D Animation"（NPAR 2000）
- Barla et al., "X-Toon: An Extended Toon Shader"（NPAR 2006）

## 関連ページ

- [Outlines and Toon](index.md)
- [Inverted Hull Outlines](outline-hull.md)
- [Posterization and Halftone](posterize-halftone.md)
- [法線とライティング](../../../3d/lighting-normals.md)
