---
title: 風
tags:
  - 描画
---

# 風

**風で草や木をなびかせると、世界が生きて見えます**。**頂点シェーダーで、頂点を動かす**のが**基本**です。このページでは、**風の表現**を説明します。

!!! tip "ポイント"
    - **頂点を、サイン波とノイズで揺らす**。
    - **根元は固定、先端ほど大きく動く**（頂点カラーで指定）。
    - **風の向きと強さを、全体で共有**。
    - **位置ごとに位相をずらして、波のように見せる**。

## 風
**風で揺れる草・木は画面に動きと生気**を**与えます**。**頂点シェーダーで頂点をずらす**のが**基本**です。

<svg class="fig illust motion" data-fig="grass-wind" viewBox="0 0 780 200" role="img" aria-label="風で揺れる草">
<text x="20" y="24" class="fig-title">風：根元は動かず、先端ほど大きく揺れる</text>
<line x1="40" y1="170" x2="740" y2="170" stroke="currentColor" stroke-opacity="0.4"/>
<g stroke="#2ea043" stroke-width="5" fill="none" stroke-linecap="round">
<path d="M120,170 Q120,110 120,60"><animate attributeName="d" values="M120,170 Q120,110 120,60;M120,170 Q125,110 150,62;M120,170 Q120,110 120,60;M120,170 Q115,110 95,64;M120,170 Q120,110 120,60" dur="3s" repeatCount="indefinite"/></path>
<path d="M300,170 Q300,115 300,70"><animate attributeName="d" values="M300,170 Q300,115 300,70;M300,170 Q305,115 328,72;M300,170 Q300,115 300,70;M300,170 Q295,115 275,74;M300,170 Q300,115 300,70" dur="3s" begin="0.4s" repeatCount="indefinite"/></path>
<path d="M480,170 Q480,105 480,50"><animate attributeName="d" values="M480,170 Q480,105 480,50;M480,170 Q486,105 512,54;M480,170 Q480,105 480,50;M480,170 Q474,105 452,56;M480,170 Q480,105 480,50" dur="3s" begin="0.8s" repeatCount="indefinite"/></path>
<path d="M660,170 Q660,112 660,66"><animate attributeName="d" values="M660,170 Q660,112 660,66;M660,170 Q665,112 688,68;M660,170 Q660,112 660,66;M660,170 Q655,112 636,70;M660,170 Q660,112 660,66" dur="3s" begin="1.2s" repeatCount="indefinite"/></path>
</g>
</svg>

```hlsl
float3 ApplyWind(float3 world_position, float height_t, float2 wind_direction, float wind_strength, float time) {
  float phase = dot(world_position.xz, wind_direction) * 0.4 + time * 2.0;
  float sway = sin(phase) + 0.5 * sin(phase * 2.3 + 1.7);
  float amount = height_t * height_t * wind_strength * sway;
  return world_position + float3(wind_direction.x, 0, wind_direction.y) * amount;
}
```

| 点 | 説明 |
| --- | --- |
| **位置に応じた位相** | **場所ごとにずらす**と**風が波のように草原を渡る** |
| **周波数の違う波を足す** | **単調でなくなる** |
| **`height_t²`** | **根元は動かず、先端が大きく動く** |
| **風のテクスチャ** | **風の強さ・向きをスクロールするノイズのテクスチャ**で**与える**（**突風が移動する**） |
| **木の揺れ** | **幹はゆっくり大きく、枝は中くらい、葉は細かく速く**の**3 層** |

**頂点カラーに揺れの強さ（幹 0・先端 1）を焼いておく**と**美術側で調整**できます。

## よくあるミス

??? failure "すべての草が、同じ動きで揺れる"
    **位置ごとに位相をずらす**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **頂点を揺らす。根元は固定**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [植生](index.md)
- [草の形](grass-shape.md)
