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

## Cloud Layers {#雲の層}
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

### Cloud Types and Altitudes {#雲の種類と高度}

大気中の雲は、現れる高度で種類が分かれます。高い順に見ていきます。

高度 6 km 以上の高い空には、<strong>巻雲</strong>（すじ雲）や巻積雲が現れます。氷の結晶でできていて、薄く、繊維状に伸びます。密度が低いので、レイマーチはせず、テクスチャを貼った 2D の層で表すことが多いです。中層（2〜6 km）には<strong>高積雲</strong>（ひつじ雲）や高層雲が現れます。低層（2 km 以下）には、<strong>層積雲</strong>（どんよりした曇り空）、<strong>層雲</strong>（霧に近い）、<strong>積雲</strong>（綿のようにもこもこした雲）が現れます。雨を降らせる<strong>積乱雲</strong>は、低層から高層まで一気に立ち上がる巨大な雲です。

ゲームで描く雲の中心は、積雲・層積雲・積乱雲のような、厚みのある低層の雲です。ここにボリューメトリック レイマーチの価値があります。

<!-- fig:cloud-profiles:begin -->

<svg class="fig illust motion" data-fig="cloud-profiles" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-cloud-profiles" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">雲の種類で、高さごとの密度の形が違う</text>
<rect x="70" y="70" width="640" height="250" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="230.0" y1="70" x2="230.0" y2="320" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="132.5" x2="710" y2="132.5" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="70" x2="390.0" y2="320" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="195.0" x2="710" y2="195.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="550.0" y1="70" x2="550.0" y2="320" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="257.5" x2="710" y2="257.5" stroke="#e2e8f0" stroke-width="1"/>
<text x="70" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">密度</text>
<text x="710" y="356" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">層の中の高さ（0: 下端 〜 1: 上端）</text>
<path d="M70.0,320.0 L76.4,296.19 L82.8,272.38 L89.2,248.57 L95.6,224.76 L102.0,200.95 L108.4,177.14 L114.8,153.33 L121.2,129.52 L127.6,105.71 L134.0,81.9 L140.4,81.9 L146.8,81.9 L153.2,81.9 L159.6,81.9 L166.0,81.9 L172.4,81.9 L178.8,81.9 L185.2,81.9 L191.6,81.9 L198.0,81.9 L204.4,105.71 L210.8,129.52 L217.2,153.33 L223.6,177.14 L230.0,200.95 L236.4,224.76 L242.8,248.57 L249.2,272.38 L255.6,296.19 L262.0,320.0 L268.4,320.0 L274.8,320.0 L281.2,320.0 L287.6,320.0 L294.0,320.0 L300.4,320.0 L306.8,320.0 L313.2,320.0 L319.6,320.0 L326.0,320.0 L332.4,320.0 L338.8,320.0 L345.2,320.0 L351.6,320.0 L358.0,320.0 L364.4,320.0 L370.8,320.0 L377.2,320.0 L383.6,320.0 L390.0,320.0 L396.4,320.0 L402.8,320.0 L409.2,320.0 L415.6,320.0 L422.0,320.0 L428.4,320.0 L434.8,320.0 L441.2,320.0 L447.6,320.0 L454.0,320.0 L460.4,320.0 L466.8,320.0 L473.2,320.0 L479.6,320.0 L486.0,320.0 L492.4,320.0 L498.8,320.0 L505.2,320.0 L511.6,320.0 L518.0,320.0 L524.4,320.0 L530.8,320.0 L537.2,320.0 L543.6,320.0 L550.0,320.0 L556.4,320.0 L562.8,320.0 L569.2,320.0 L575.6,320.0 L582.0,320.0 L588.4,320.0 L594.8,320.0 L601.2,320.0 L607.6,320.0 L614.0,320.0 L620.4,320.0 L626.8,320.0 L633.2,320.0 L639.6,320.0 L646.0,320.0 L652.4,320.0 L658.8,320.0 L665.2,320.0 L671.6,320.0 L678.0,320.0 L684.4,320.0 L690.8,320.0 L697.2,320.0 L703.6,320.0 L710.0,320.0" fill="none" stroke="#2563eb" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/></path>
<text x="90" y="100" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb" opacity="0">層雲: 下側に薄く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,320.0 L76.4,308.1 L82.8,296.19 L89.2,284.29 L95.6,272.38 L102.0,260.48 L108.4,248.57 L114.8,236.67 L121.2,224.76 L127.6,212.86 L134.0,200.95 L140.4,189.05 L146.8,177.14 L153.2,165.24 L159.6,153.33 L166.0,141.43 L172.4,129.52 L178.8,117.62 L185.2,105.71 L191.6,93.81 L198.0,81.9 L204.4,81.9 L210.8,81.9 L217.2,81.9 L223.6,81.9 L230.0,81.9 L236.4,81.9 L242.8,81.9 L249.2,81.9 L255.6,81.9 L262.0,81.9 L268.4,81.9 L274.8,81.9 L281.2,81.9 L287.6,81.9 L294.0,81.9 L300.4,81.9 L306.8,81.9 L313.2,81.9 L319.6,81.9 L326.0,81.9 L332.4,89.84 L338.8,97.78 L345.2,105.71 L351.6,113.65 L358.0,121.59 L364.4,129.52 L370.8,137.46 L377.2,145.4 L383.6,153.33 L390.0,161.27 L396.4,169.21 L402.8,177.14 L409.2,185.08 L415.6,193.02 L422.0,200.95 L428.4,208.89 L434.8,216.83 L441.2,224.76 L447.6,232.7 L454.0,240.63 L460.4,248.57 L466.8,256.51 L473.2,264.44 L479.6,272.38 L486.0,280.32 L492.4,288.25 L498.8,296.19 L505.2,304.13 L511.6,312.06 L518.0,320.0 L524.4,320.0 L530.8,320.0 L537.2,320.0 L543.6,320.0 L550.0,320.0 L556.4,320.0 L562.8,320.0 L569.2,320.0 L575.6,320.0 L582.0,320.0 L588.4,320.0 L594.8,320.0 L601.2,320.0 L607.6,320.0 L614.0,320.0 L620.4,320.0 L626.8,320.0 L633.2,320.0 L639.6,320.0 L646.0,320.0 L652.4,320.0 L658.8,320.0 L665.2,320.0 L671.6,320.0 L678.0,320.0 L684.4,320.0 L690.8,320.0 L697.2,320.0 L703.6,320.0 L710.0,320.0" fill="none" stroke="#2ea043" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3040;0.3043;1.0000" values="0;0;1;1"/></path>
<text x="90" y="120" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043" opacity="0">層積雲: 下半分に厚み<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3040;0.3043;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,320.0 L76.4,285.99 L82.8,251.97 L89.2,217.96 L95.6,183.95 L102.0,149.93 L108.4,115.92 L114.8,81.9 L121.2,81.9 L127.6,81.9 L134.0,81.9 L140.4,81.9 L146.8,81.9 L153.2,81.9 L159.6,81.9 L166.0,81.9 L172.4,81.9 L178.8,81.9 L185.2,81.9 L191.6,81.9 L198.0,81.9 L204.4,84.88 L210.8,87.86 L217.2,90.83 L223.6,93.81 L230.0,96.79 L236.4,99.76 L242.8,102.74 L249.2,105.71 L255.6,108.69 L262.0,111.67 L268.4,114.64 L274.8,117.62 L281.2,120.6 L287.6,123.57 L294.0,126.55 L300.4,129.52 L306.8,132.5 L313.2,135.48 L319.6,138.45 L326.0,141.43 L332.4,144.4 L338.8,147.38 L345.2,150.36 L351.6,153.33 L358.0,156.31 L364.4,159.29 L370.8,162.26 L377.2,165.24 L383.6,168.21 L390.0,171.19 L396.4,174.17 L402.8,177.14 L409.2,180.12 L415.6,183.1 L422.0,186.07 L428.4,189.05 L434.8,192.02 L441.2,195.0 L447.6,197.98 L454.0,200.95 L460.4,203.93 L466.8,206.9 L473.2,209.88 L479.6,212.86 L486.0,215.83 L492.4,218.81 L498.8,221.79 L505.2,224.76 L511.6,227.74 L518.0,230.71 L524.4,233.69 L530.8,236.67 L537.2,239.64 L543.6,242.62 L550.0,245.6 L556.4,248.57 L562.8,251.55 L569.2,254.52 L575.6,257.5 L582.0,260.48 L588.4,263.45 L594.8,266.43 L601.2,269.4 L607.6,272.38 L614.0,275.36 L620.4,278.33 L626.8,281.31 L633.2,284.29 L639.6,287.26 L646.0,290.24 L652.4,293.21 L658.8,296.19 L665.2,299.17 L671.6,302.14 L678.0,305.12 L684.4,308.1 L690.8,311.07 L697.2,314.05 L703.6,317.02 L710.0,320.0" fill="none" stroke="#e5484d" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000" values="0;0;1;1"/></path>
<text x="90" y="140" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="0">積雲: 雲底が平ら、上は丸い<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000" values="0;0;1;1"/></text>
<text x="390" y="365" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ノイズの形に、高さのプロファイルを掛ける<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="1;1;0;0"/></text>
<text x="390" y="365" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">プロファイルを変えるだけで、雲の種類が変わる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.7388;0.7391;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="365" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">積雲: 底が平らで、てっぺんが丸い、雲らしい輪郭<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.7388;0.7391;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:cloud-profiles:end -->

### Thinking About Altitude Profiles {#高度プロファイルの考え方}

雲の種類ごとに、「雲の層の中での高さ」と「密度」の関係が違います。層の下端を 0、上端を 1 とした正規化した高さ h で表します。

* <strong>層雲</strong>：下側に偏った、平らな密度。h = 0.0〜0.2 あたりで密度が立ち上がり、すぐ下がる。
* <strong>層積雲</strong>：層の下半分に厚みがある、緩やかな山形。
* <strong>積雲</strong>：下端がくっきり平らで（雲底）、上へ行くほど丸く膨らみ、てっぺんで急に消える。

これらを関数として、`h` から密度の倍率を返す形で持ちます（たとえば、積雲なら `saturate(remap(h, 0.0, 0.07, 0, 1)) * saturate(remap(h, 0.2, 1.0, 1, 0))` のような台形）。ノイズで作った形に、この高度プロファイルを掛けると、雲底が平らで頂上が丸い、雲らしい輪郭が得られます。

### Controlling the Weather {#天気の制御}

どの種類の雲が、どこにどれだけあるかは、<strong>天気マップ</strong>（2D のテクスチャ）で制御するのが一般的です。たとえば、R チャンネルにカバレッジ（雲の量）、G チャンネルに降水（雨雲かどうか）、B チャンネルに雲の種類（層雲〜積雲の混合比）を入れます。このマップを風でスクロールさせるだけで、天気が時間とともに移り変わります。晴れの日は R を小さく、曇りの日は大きくすれば、同じ仕組みで天候が切り替わります。

### Layer Shape (Spherical Shell) {#層の形状球殻}

地球は丸いので、雲の層は<strong>平面でなく球殻</strong>として扱います。内側の球（地表から高度 1.5 km）と外側の球（高度 4 km）の間が雲の層です。平面の層にすると、地平線の方向で層が際限なく遠くまで続いて、雲が細長く伸びて見えます。球殻なら、遠くの雲は地平線の向こうに自然に消えます。半径は、地球の半径 6371 km に高度を足したものです。

## Common Mistakes {#よくあるミス}

??? failure "どの雲も同じ形に見える"
    **高さ別の密度プロファイル**を**使い分ける**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **高度ごとに、密度のプロファイルを変える**

## References {#参考}

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## Related Pages {#関連ページ}

- [Clouds](index.md)
- [Cloud Density Model](density-model.md)
