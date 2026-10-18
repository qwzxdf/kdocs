---
title: Underwater Fog
tags:
  - 描画
---

# Underwater Fog

**水中では、遠くほど、青緑に霞みます**。**距離に応じた指数フォグ**で**表現**でき、**水の色と深さで、霧の色を変えます**。このページでは、**水中の霧**を説明します。

!!! tip "ポイント"
    - **指数フォグ：距離が遠いほど、水の色に近づく**。
    - **水の吸収係数を使う**（赤が先に消える）。
    - **深いほど、暗くする**。
    - **水面からの光の量を、深さで減らす**。

## 水中の霧
**水中では遠くの物ほど、水の色に近づきます**。**地上のフォグと同じ構造**ですが、**吸収が色ごとに違う**のが**特徴**です。

<div class="formula">T = exp( −σ · d )　（σ：吸収係数（RGB）、d：カメラから物までの距離）</div>

```hlsl
float3 absorption = float3(0.45, 0.07, 0.03);
float3 transmittance = exp(-absorption * distance_to_pixel);
float3 scattered = water_color * (1.0 - transmittance);
float3 final_color = scene_color * transmittance + scattered;
```

| 点 | 説明 |
| --- | --- |
| **赤が先に消える** | **遠くは青緑**になる |
| **`distance_to_pixel`** | **深度から求めた、カメラからの距離**（水面を通る分も含む） |
| **水深で明るさを変える** | **深いほど暗い**（**太陽光が届かない**）。**`exp(−k · depth)`** |
| **空は水の色** | **空の部分は遠距離扱いで水の色になる** |

<svg class="fig illust" viewBox="0 0 780 200" role="img" aria-label="水中の霧">
<text x="20" y="24" class="fig-title">水中の霧：距離とともに、赤 → 緑 → 青の順に消える</text>
<line x1="80" y1="170" x2="720" y2="170" stroke="currentColor" stroke-opacity="0.5"/>
<line x1="80" y1="50" x2="80" y2="170" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#e5484d" stroke-width="3" points="80,52 160,100 240,132 320,150 400,160 560,167 720,169"/>
<polyline fill="none" stroke="#2ea043" stroke-width="3" points="80,52 160,60 240,70 320,82 400,95 560,120 720,140"/>
<polyline fill="none" stroke="#4c8bf5" stroke-width="3" points="80,52 160,55 240,58 320,63 400,69 560,80 720,98"/>
<text x="720" y="192" text-anchor="end" style="font-size:12px">距離 d →</text>
<text x="86" y="44" style="font-size:12px">残る光の割合 T</text>
<text x="170" y="118" style="font-size:12px;fill:#e5484d">赤（すぐ消える）</text>
<text x="420" y="110" style="font-size:12px;fill:#2ea043">緑</text>
<text x="420" y="64" style="font-size:12px;fill:#4c8bf5">青（最後まで残る）</text>
</svg>

## よくあるミス

??? failure "水中なのに、遠くまでくっきり見える"
    **距離フォグ**を**かける**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **距離と深さで、色と明るさが変わる**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Underwater Rendering](index.md)
- [Color by Water Depth](../shading/depth-color.md)
- [Aerial Perspective and Fog](../../atmosphere/aerial-fog/index.md)
