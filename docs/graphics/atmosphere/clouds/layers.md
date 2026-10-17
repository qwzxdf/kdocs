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

### 雲の種類と高度

大気中の雲は、現れる高度で種類が分かれます。高い順に見ていきます。

高度 6 km 以上の高い空には、<strong>巻雲</strong>（すじ雲）や巻積雲が現れます。氷の結晶でできていて、薄く、繊維状に伸びます。密度が低いので、レイマーチはせず、テクスチャを貼った 2D の層で表すことが多いです。中層（2〜6 km）には<strong>高積雲</strong>（ひつじ雲）や高層雲が現れます。低層（2 km 以下）には、<strong>層積雲</strong>（どんよりした曇り空）、<strong>層雲</strong>（霧に近い）、<strong>積雲</strong>（綿のようにもこもこした雲）が現れます。雨を降らせる<strong>積乱雲</strong>は、低層から高層まで一気に立ち上がる巨大な雲です。

ゲームで描く雲の中心は、積雲・層積雲・積乱雲のような、厚みのある低層の雲です。ここにボリューメトリック レイマーチの価値があります。

### 高度プロファイルの考え方

雲の種類ごとに、「雲の層の中での高さ」と「密度」の関係が違います。層の下端を 0、上端を 1 とした正規化した高さ h で表します。

* <strong>層雲</strong>：下側に偏った、平らな密度。h = 0.0〜0.2 あたりで密度が立ち上がり、すぐ下がる。
* <strong>層積雲</strong>：層の下半分に厚みがある、緩やかな山形。
* <strong>積雲</strong>：下端がくっきり平らで（雲底）、上へ行くほど丸く膨らみ、てっぺんで急に消える。

これらを関数として、`h` から密度の倍率を返す形で持ちます（たとえば、積雲なら `saturate(remap(h, 0.0, 0.07, 0, 1)) * saturate(remap(h, 0.2, 1.0, 1, 0))` のような台形）。ノイズで作った形に、この高度プロファイルを掛けると、雲底が平らで頂上が丸い、雲らしい輪郭が得られます。

### 天気の制御

どの種類の雲が、どこにどれだけあるかは、<strong>天気マップ</strong>（2D のテクスチャ）で制御するのが一般的です。たとえば、R チャンネルにカバレッジ（雲の量）、G チャンネルに降水（雨雲かどうか）、B チャンネルに雲の種類（層雲〜積雲の混合比）を入れます。このマップを風でスクロールさせるだけで、天気が時間とともに移り変わります。晴れの日は R を小さく、曇りの日は大きくすれば、同じ仕組みで天候が切り替わります。

### 層の形状（球殻）

地球は丸いので、雲の層は<strong>平面でなく球殻</strong>として扱います。内側の球（地表から高度 1.5 km）と外側の球（高度 4 km）の間が雲の層です。平面の層にすると、地平線の方向で層が際限なく遠くまで続いて、雲が細長く伸びて見えます。球殻なら、遠くの雲は地平線の向こうに自然に消えます。半径は、地球の半径 6371 km に高度を足したものです。

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
