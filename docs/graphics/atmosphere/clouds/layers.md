---
title: Cloud Layers
tags:
  - 描画
---

# Cloud Layers

**雲には、高さごとに種類があります**。**低い所の積雲、高い所の巻雲など**、**層ごとに密度の分布を変える**と、**リアル**です。このページでは、**雲の層**を説明します。

!!! tip "ポイント"
    - **層積雲・積雲・巻雲など、高度で種類が違う**。
    - **高さに応じて、密度のプロファイルを変える**。
    - **層ごとに、レイマーチの範囲を限定**する。
    - **天気（晴れ・曇り）を、カバレッジで制御**。

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

**視線が雲の層の内側の球殻と外側の球殻のどちらにぶつかるかを求めて、その間だけレイマーチ**します（[Atmospheric Scattering](../scattering/index.md)の球との交差と同じ）。

## よくあるミス

??? failure "どの雲も同じ形に見える"
    **高さ別の密度プロファイル**を**使い分ける**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **高度ごとに、密度のプロファイルを変える**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Clouds](index.md)
- [Cloud Density Model](density-model.md)
