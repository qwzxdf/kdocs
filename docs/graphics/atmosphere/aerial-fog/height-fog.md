---
title: 高さフォグ
tags:
  - 描画
---

# 高さフォグ

**霧は、低い所にたまります**。**フォグの密度を、高さで指数的に減らす**と、**谷にたまる霧**が**表現**できます。このページでは、**高さフォグ**を説明します。

!!! tip "ポイント"
    - **密度 ＝ 基準密度 × exp(−高さ × 係数)**。
    - **視線に沿って積分すると、解析的に求まる**。
    - **低い所ほど、濃い霧**。
    - **朝霧・谷の霧の表現**に向く。

<!-- fig:height-fog-ray:begin -->

<svg class="fig illust motion" data-fig="height-fog-ray" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-height-fog-ray" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">高さフォグ:カメラが霧の中にいるか、上にいるかで、遠景の霞み方が変わる</text>
<rect x="40" y="322" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.85"/>
<rect x="40" y="314" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.73"/>
<rect x="40" y="306" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.64"/>
<rect x="40" y="298" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.55"/>
<rect x="40" y="290" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.48"/>
<rect x="40" y="282" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.41"/>
<rect x="40" y="274" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.36"/>
<rect x="40" y="266" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.31"/>
<rect x="40" y="258" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.27"/>
<rect x="40" y="250" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.23"/>
<rect x="40" y="242" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.2"/>
<rect x="40" y="234" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.17"/>
<rect x="40" y="226" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.15"/>
<rect x="40" y="218" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.13"/>
<rect x="40" y="210" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.11"/>
<rect x="40" y="202" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.1"/>
<rect x="40" y="194" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.08"/>
<rect x="40" y="186" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.07"/>
<rect x="40" y="178" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.06"/>
<rect x="40" y="170" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.05"/>
<rect x="40" y="162" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.05"/>
<rect x="40" y="154" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.04"/>
<rect x="40" y="146" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.03"/>
<rect x="40" y="138" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.03"/>
<rect x="40" y="130" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.03"/>
<rect x="40" y="122" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.02"/>
<rect x="40" y="114" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.02"/>
<rect x="40" y="106" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.02"/>
<rect x="40" y="98" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.01"/>
<rect x="40" y="90" width="700" height="8.5" fill="#94a3b8" fill-opacity="0.01"/>
<rect x="40" y="330" width="700" height="20" fill="#a16207" fill-opacity="0.6"/>
<text x="50" y="106" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">上へ行くほど、霧が薄い</text>
<rect x="670" y="190" width="24" height="140" fill="#166534"/>
<circle cx="90" cy="320" r="9" fill="#2563eb" stroke="#ffffff" stroke-width="2"><animate attributeName="cy" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.2222;0.5185;0.6667;0.8519;1.0000" values="320;320;320;100;100;320;320"/></circle>
<line x1="90" y1="320" x2="670" y2="260" stroke="#2563eb" stroke-width="2.5"><animate attributeName="y1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.2222;0.5185;0.6667;0.8519;1.0000" values="320;320;320;100;100;320;320"/></line>
<rect x="610" y="60" width="110" height="30" fill="#166534" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.2222;0.5185;0.6667;0.8519;1.0000" values="#166534;#166534;#80a799;#80a799;#31754d;#31754d;#80a799;#80a799"/></rect>
<text x="600" y="80" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">塔の見え方</text>
<text x="40" y="396" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">カメラが地面近く（霧の中）:視線が、濃い霧の中を長く通る → 塔は霞む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;1.0000" values="1;1;0;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">カメラを上げていく…<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;0.5182;0.5185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">霧の上:視線が薄い霧を通る → 塔がはっきり見える<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;0.6664;0.6667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">下げると、また霞む<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6664;0.6667;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:height-fog-ray:end -->

## 高さフォグ
**谷や低地に霧が溜まる**表現です。**霧の密度が高さに対して指数的に減る**と**仮定します**。

<div class="formula">density(h) = density₀ · exp( −falloff · h )</div>

**視線に沿った光学的厚さは、密度を積分した値**です。**指数関数の積分は、解析的に求まる**ので**ステップを刻まず 1 回で計算できます**。

```hlsl
float HeightFogOpticalDepth(float3 camera_pos, float3 world_pos) {
  float3 delta = world_pos - camera_pos;
  float distance_to_pixel = length(delta);
  float height_difference = delta.y;

  float falloff = fog_height_falloff;
  float base = fog_density * exp(-falloff * (camera_pos.y - fog_base_height));
  float integral;
  if (abs(height_difference) > 0.0001) {
    integral = (1.0 - exp(-falloff * height_difference)) / (falloff * height_difference);
  } else {
    integral = 1.0;
  }
  return base * integral * distance_to_pixel;
}

float transmittance = exp(-HeightFogOpticalDepth(camera_position, world_position));
```

| 点 | 説明 |
| --- | --- |
| **解析解** | **視線の高さが変わる区間の積分を、閉じた式で**（**ステップ不要**） |
| **`base`** | **カメラの高さでの密度** |
| **高さ差が 0 に近い** | **0 除算を避けるため、積分の値を 1 に** |
| **`fog_base_height`** | **霧が最も濃い高さ**（**谷底・海面**） |
| **`falloff`** | **大きいほど、霧が薄い層に集中** |

**雲海・谷の霧・朝霧**の表現に**効果的**です。

## よくあるミス

??? failure "霧が、高さに関係なく一様"
    **高さで密度を減らす**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **高さで密度を減らして、霧をたまらせる**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [空気遠近法・フォグ](index.md)
- [ボリューメトリック フォグ](../volumetric-fog/index.md)
