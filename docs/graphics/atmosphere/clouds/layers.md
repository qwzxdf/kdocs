---
title: Cloud Layers
tags:
  - 描画
---

# Cloud Layers

<strong>雲には高さごとに種類があります</strong>。<strong>低い所の積雲、高い所の巻雲など</strong>、層ごとに密度の分布を変えると、リアルです。このページでは雲の層を説明します。

!!! tip "ポイント"
    - 層積雲・積雲・巻雲など、高度で種類が違う。
    - 高さに応じて密度のプロファイルを変える。
    - 層ごとにレイマーチの範囲を限定する。
    - 天気（晴れ・曇り）を、カバレッジで制御。

## 雲の層
<strong>積雲（もこもこした雲）などの雲は地面から離れた高さ 1.5〜4 km 程度の層</strong>にできます。<strong>空に「雲の層」（地表からの高さの範囲）を決め、その中だけを描きます</strong>。

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

<strong>視線が雲の層の内側の球殻と外側の球殻のどちらにぶつかるかを求めて、その間だけレイマーチ</strong>します（[Atmospheric Scattering](../scattering/index.md)の球との交差と同じ）。

### 雲の種類と高度

大気中の雲は現れる高度で種類が分かれます。高い順に見ていきます。

高度 6 km 以上の高い空には、<strong>巻雲</strong>（すじ雲）や巻積雲が現れます。氷の結晶でできていて薄く繊維状に伸びます。密度が低いのでレイマーチはせず、テクスチャを貼った 2D の層で表すことが多いです。中層（2〜6 km）には<strong>高積雲</strong>（ひつじ雲）や高層雲が現れます。低層（2 km 以下）には <strong>層積雲</strong>（どんよりした曇り空）、<strong>層雲</strong>（霧に近い）、<strong>積雲</strong>（綿のようにもこもこした雲）が現れます。雨を降らせる<strong>積乱雲</strong>は低層から高層まで一気に立ち上がる巨大な雲です。

ゲームで描く雲の中心は積雲・層積雲・積乱雲のような、厚みのある低層の雲です。ここにボリューメトリック レイマーチの価値があります。

<!-- fig:cloud-profiles:begin -->

<svg class="fig illust motion" data-fig="cloud-profiles" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-cloud-profiles" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">雲の高さ方向の形: 雲の種類ごとに、高さに応じた、密度の山(プロファイル)を掛ける</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">高さ 0〜1(雲の層の下端〜上端)。積雲・層雲・積乱雲の密度の形と、垂直に積分した「厚さ」を、計算する</text>
<rect x="30" y="96" width="560" height="310" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 高さと密度(横 = 密度、縦 = 高さ)</text>
<line x1="110.0" y1="130" x2="110.0" y2="380" stroke="#94a3b8" stroke-width="2"/>
<text x="70" y="134" text-anchor="start" style="font-size:11px;font-weight:700;fill:#64748b">上端</text>
<text x="70" y="384" text-anchor="start" style="font-size:11px;font-weight:700;fill:#64748b">下端</text>
<path d="M110.0,380.0 L122.32,377.5 L155.76,375.0 L205.04,372.5 L264.88,370.0 L330.0,367.5 L395.12,365.0 L454.96,362.5 L504.24,360.0 L537.68,357.5 L550.0,355.0 L550.0,352.5 L550.0,350.0 L550.0,347.5 L550.0,345.0 L550.0,342.5 L550.0,340.0 L550.0,337.5 L550.0,335.0 L550.0,332.5 L550.0,330.0 L537.68,327.5 L504.24,325.0 L454.96,322.5 L395.12,320.0 L330.0,317.5 L264.88,315.0 L205.04,312.5 L155.76,310.0 L122.32,307.5 L110.0,305.0 L110.0,302.5 L110.0,300.0 L110.0,297.5 L110.0,295.0 L110.0,292.5 L110.0,290.0 L110.0,287.5 L110.0,285.0 L110.0,282.5 L110.0,280.0 L110.0,277.5 L110.0,275.0 L110.0,272.5 L110.0,270.0 L110.0,267.5 L110.0,265.0 L110.0,262.5 L110.0,260.0 L110.0,257.5 L110.0,255.0 L110.0,252.5 L110.0,250.0 L110.0,247.5 L110.0,245.0 L110.0,242.5 L110.0,240.0 L110.0,237.5 L110.0,235.0 L110.0,232.5 L110.0,230.0 L110.0,227.5 L110.0,225.0 L110.0,222.5 L110.0,220.0 L110.0,217.5 L110.0,215.0 L110.0,212.5 L110.0,210.0 L110.0,207.5 L110.0,205.0 L110.0,202.5 L110.0,200.0 L110.0,197.5 L110.0,195.0 L110.0,192.5 L110.0,190.0 L110.0,187.5 L110.0,185.0 L110.0,182.5 L110.0,180.0 L110.0,177.5 L110.0,175.0 L110.0,172.5 L110.0,170.0 L110.0,167.5 L110.0,165.0 L110.0,162.5 L110.0,160.0 L110.0,157.5 L110.0,155.0 L110.0,152.5 L110.0,150.0 L110.0,147.5 L110.0,145.0 L110.0,142.5 L110.0,140.0 L110.0,137.5 L110.0,135.0 L110.0,132.5 L110.0,130.0" fill="none" stroke="#2563eb" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></path>
<path d="M110.0,380 L110.0,380.0 L122.32,377.5 L155.76,375.0 L205.04,372.5 L264.88,370.0 L330.0,367.5 L395.12,365.0 L454.96,362.5 L504.24,360.0 L537.68,357.5 L550.0,355.0 L550.0,352.5 L550.0,350.0 L550.0,347.5 L550.0,345.0 L550.0,342.5 L550.0,340.0 L550.0,337.5 L550.0,335.0 L550.0,332.5 L550.0,330.0 L537.68,327.5 L504.24,325.0 L454.96,322.5 L395.12,320.0 L330.0,317.5 L264.88,315.0 L205.04,312.5 L155.76,310.0 L122.32,307.5 L110.0,305.0 L110.0,302.5 L110.0,300.0 L110.0,297.5 L110.0,295.0 L110.0,292.5 L110.0,290.0 L110.0,287.5 L110.0,285.0 L110.0,282.5 L110.0,280.0 L110.0,277.5 L110.0,275.0 L110.0,272.5 L110.0,270.0 L110.0,267.5 L110.0,265.0 L110.0,262.5 L110.0,260.0 L110.0,257.5 L110.0,255.0 L110.0,252.5 L110.0,250.0 L110.0,247.5 L110.0,245.0 L110.0,242.5 L110.0,240.0 L110.0,237.5 L110.0,235.0 L110.0,232.5 L110.0,230.0 L110.0,227.5 L110.0,225.0 L110.0,222.5 L110.0,220.0 L110.0,217.5 L110.0,215.0 L110.0,212.5 L110.0,210.0 L110.0,207.5 L110.0,205.0 L110.0,202.5 L110.0,200.0 L110.0,197.5 L110.0,195.0 L110.0,192.5 L110.0,190.0 L110.0,187.5 L110.0,185.0 L110.0,182.5 L110.0,180.0 L110.0,177.5 L110.0,175.0 L110.0,172.5 L110.0,170.0 L110.0,167.5 L110.0,165.0 L110.0,162.5 L110.0,160.0 L110.0,157.5 L110.0,155.0 L110.0,152.5 L110.0,150.0 L110.0,147.5 L110.0,145.0 L110.0,142.5 L110.0,140.0 L110.0,137.5 L110.0,135.0 L110.0,132.5 L110.0,130.0 L110.0,130 Z" fill="#2563eb" fill-opacity="0.12" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></path>
<path d="M110.0,380.0 L122.32,377.5 L155.76,375.0 L205.04,372.5 L264.88,370.0 L330.0,367.5 L395.12,365.0 L454.96,362.5 L504.24,360.0 L537.68,357.5 L550.0,355.0 L550.0,352.5 L550.0,350.0 L550.0,347.5 L550.0,345.0 L550.0,342.5 L550.0,340.0 L550.0,337.5 L550.0,335.0 L550.0,332.5 L550.0,330.0 L550.0,327.5 L550.0,325.0 L550.0,322.5 L550.0,320.0 L550.0,317.5 L550.0,315.0 L550.0,312.5 L550.0,310.0 L550.0,307.5 L550.0,305.0 L550.0,302.5 L550.0,300.0 L550.0,297.5 L550.0,295.0 L550.0,292.5 L550.0,290.0 L550.0,287.5 L550.0,285.0 L550.0,282.5 L550.0,280.0 L550.0,277.5 L550.0,275.0 L550.0,272.5 L550.0,270.0 L550.0,267.5 L550.0,265.0 L550.0,262.5 L550.0,260.0 L550.0,257.5 L550.0,255.0 L550.0,252.5 L550.0,250.0 L550.0,247.5 L550.0,245.0 L550.0,242.5 L550.0,240.0 L550.0,237.5 L550.0,235.0 L550.0,232.5 L550.0,230.0 L548.57,227.5 L544.39,225.0 L537.68,222.5 L528.62,220.0 L517.41,217.5 L504.24,215.0 L489.31,212.5 L472.82,210.0 L454.96,207.5 L435.93,205.0 L415.91,202.5 L395.12,200.0 L373.74,197.5 L351.97,195.0 L330.0,192.5 L308.03,190.0 L286.26,187.5 L264.88,185.0 L244.09,182.5 L224.07,180.0 L205.04,177.5 L187.18,175.0 L170.69,172.5 L155.76,170.0 L142.59,167.5 L131.38,165.0 L122.32,162.5 L115.61,160.0 L111.43,157.5 L110.0,155.0 L110.0,152.5 L110.0,150.0 L110.0,147.5 L110.0,145.0 L110.0,142.5 L110.0,140.0 L110.0,137.5 L110.0,135.0 L110.0,132.5 L110.0,130.0" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2798;0.2800;1.0000" values="0;0;1;1"/></path>
<path d="M110.0,380 L110.0,380.0 L122.32,377.5 L155.76,375.0 L205.04,372.5 L264.88,370.0 L330.0,367.5 L395.12,365.0 L454.96,362.5 L504.24,360.0 L537.68,357.5 L550.0,355.0 L550.0,352.5 L550.0,350.0 L550.0,347.5 L550.0,345.0 L550.0,342.5 L550.0,340.0 L550.0,337.5 L550.0,335.0 L550.0,332.5 L550.0,330.0 L550.0,327.5 L550.0,325.0 L550.0,322.5 L550.0,320.0 L550.0,317.5 L550.0,315.0 L550.0,312.5 L550.0,310.0 L550.0,307.5 L550.0,305.0 L550.0,302.5 L550.0,300.0 L550.0,297.5 L550.0,295.0 L550.0,292.5 L550.0,290.0 L550.0,287.5 L550.0,285.0 L550.0,282.5 L550.0,280.0 L550.0,277.5 L550.0,275.0 L550.0,272.5 L550.0,270.0 L550.0,267.5 L550.0,265.0 L550.0,262.5 L550.0,260.0 L550.0,257.5 L550.0,255.0 L550.0,252.5 L550.0,250.0 L550.0,247.5 L550.0,245.0 L550.0,242.5 L550.0,240.0 L550.0,237.5 L550.0,235.0 L550.0,232.5 L550.0,230.0 L548.57,227.5 L544.39,225.0 L537.68,222.5 L528.62,220.0 L517.41,217.5 L504.24,215.0 L489.31,212.5 L472.82,210.0 L454.96,207.5 L435.93,205.0 L415.91,202.5 L395.12,200.0 L373.74,197.5 L351.97,195.0 L330.0,192.5 L308.03,190.0 L286.26,187.5 L264.88,185.0 L244.09,182.5 L224.07,180.0 L205.04,177.5 L187.18,175.0 L170.69,172.5 L155.76,170.0 L142.59,167.5 L131.38,165.0 L122.32,162.5 L115.61,160.0 L111.43,157.5 L110.0,155.0 L110.0,152.5 L110.0,150.0 L110.0,147.5 L110.0,145.0 L110.0,142.5 L110.0,140.0 L110.0,137.5 L110.0,135.0 L110.0,132.5 L110.0,130.0 L110.0,130 Z" fill="#2ea043" fill-opacity="0.12" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2798;0.2800;1.0000" values="0;0;1;1"/></path>
<path d="M110.0,380.0 L134.37,377.5 L197.23,375.0 L283.18,372.5 L376.82,370.0 L462.77,367.5 L525.63,365.0 L550.0,362.5 L550.0,360.0 L550.0,357.5 L550.0,355.0 L550.0,352.5 L550.0,350.0 L550.0,347.5 L550.0,345.0 L550.0,342.5 L550.0,340.0 L550.0,337.5 L550.0,335.0 L550.0,332.5 L550.0,330.0 L550.0,327.5 L550.0,325.0 L550.0,322.5 L550.0,320.0 L550.0,317.5 L550.0,315.0 L550.0,312.5 L550.0,310.0 L550.0,307.5 L550.0,305.0 L550.0,302.5 L550.0,300.0 L550.0,297.5 L550.0,295.0 L550.0,292.5 L550.0,290.0 L550.0,287.5 L550.0,285.0 L550.0,282.5 L550.0,280.0 L550.0,277.5 L550.0,275.0 L550.0,272.5 L550.0,270.0 L550.0,267.5 L550.0,265.0 L550.0,262.5 L550.0,260.0 L550.0,257.5 L550.0,255.0 L550.0,252.5 L550.0,250.0 L550.0,247.5 L550.0,245.0 L550.0,242.5 L550.0,240.0 L550.0,237.5 L550.0,235.0 L550.0,232.5 L550.0,230.0 L550.0,227.5 L550.0,225.0 L550.0,222.5 L550.0,220.0 L550.0,217.5 L550.0,215.0 L550.0,212.5 L550.0,210.0 L550.0,207.5 L550.0,205.0 L550.0,202.5 L550.0,200.0 L550.0,197.5 L550.0,195.0 L550.0,192.5 L550.0,190.0 L550.0,187.5 L550.0,185.0 L550.0,182.5 L550.0,180.0 L550.0,177.5 L550.0,175.0 L550.0,172.5 L550.0,170.0 L550.0,167.5 L550.0,165.0 L550.0,162.5 L550.0,160.0 L550.0,157.5 L550.0,155.0 L537.68,152.5 L504.24,150.0 L454.96,147.5 L395.12,145.0 L330.0,142.5 L264.88,140.0 L205.04,137.5 L155.76,135.0 L122.32,132.5 L110.0,130.0" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4932;0.4933;1.0000" values="0;0;1;1"/></path>
<path d="M110.0,380 L110.0,380.0 L134.37,377.5 L197.23,375.0 L283.18,372.5 L376.82,370.0 L462.77,367.5 L525.63,365.0 L550.0,362.5 L550.0,360.0 L550.0,357.5 L550.0,355.0 L550.0,352.5 L550.0,350.0 L550.0,347.5 L550.0,345.0 L550.0,342.5 L550.0,340.0 L550.0,337.5 L550.0,335.0 L550.0,332.5 L550.0,330.0 L550.0,327.5 L550.0,325.0 L550.0,322.5 L550.0,320.0 L550.0,317.5 L550.0,315.0 L550.0,312.5 L550.0,310.0 L550.0,307.5 L550.0,305.0 L550.0,302.5 L550.0,300.0 L550.0,297.5 L550.0,295.0 L550.0,292.5 L550.0,290.0 L550.0,287.5 L550.0,285.0 L550.0,282.5 L550.0,280.0 L550.0,277.5 L550.0,275.0 L550.0,272.5 L550.0,270.0 L550.0,267.5 L550.0,265.0 L550.0,262.5 L550.0,260.0 L550.0,257.5 L550.0,255.0 L550.0,252.5 L550.0,250.0 L550.0,247.5 L550.0,245.0 L550.0,242.5 L550.0,240.0 L550.0,237.5 L550.0,235.0 L550.0,232.5 L550.0,230.0 L550.0,227.5 L550.0,225.0 L550.0,222.5 L550.0,220.0 L550.0,217.5 L550.0,215.0 L550.0,212.5 L550.0,210.0 L550.0,207.5 L550.0,205.0 L550.0,202.5 L550.0,200.0 L550.0,197.5 L550.0,195.0 L550.0,192.5 L550.0,190.0 L550.0,187.5 L550.0,185.0 L550.0,182.5 L550.0,180.0 L550.0,177.5 L550.0,175.0 L550.0,172.5 L550.0,170.0 L550.0,167.5 L550.0,165.0 L550.0,162.5 L550.0,160.0 L550.0,157.5 L550.0,155.0 L537.68,152.5 L504.24,150.0 L454.96,147.5 L395.12,145.0 L330.0,142.5 L264.88,140.0 L205.04,137.5 L155.76,135.0 L122.32,132.5 L110.0,130.0 L110.0,130 Z" fill="#e5484d" fill-opacity="0.12" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4932;0.4933;1.0000" values="0;0;1;1"/></path>
<rect x="620" y="96" width="310" height="310" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="620" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 垂直に積分した厚さ</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1022;1.0000" values="0;0;1;1"/><text x="636" y="136" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">層雲(薄く平ら)</text>
<rect x="636" y="146" width="54.64" height="22" fill="#2563eb" opacity="0.85"/>
<text x="698.6448087431694" y="163" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">0.20</text>
<text x="636" y="192" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">密度のピーク: 高さ 0.10</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3154;0.3156;1.0000" values="0;0;1;1"/><text x="636" y="226" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">積雲(もこもこ)</text>
<rect x="636" y="236" width="191.26" height="22" fill="#2ea043" opacity="0.85"/>
<text x="835.2568306010928" y="253" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">0.70</text>
<text x="636" y="282" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">密度のピーク: 高さ 0.10</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5287;0.5289;1.0000" values="0;0;1;1"/><text x="636" y="316" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">積乱雲(高く伸びる)</text>
<rect x="636" y="326" width="250.0" height="22" fill="#e5484d" opacity="0.85"/>
<text x="894.0" y="343" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">0.92</text>
<text x="636" y="372" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">密度のピーク: 高さ 0.07</text>
</g>
<text x="40" y="440" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">垂直の厚さ(×100):</text>
<text x="200" y="444" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1022;1.0000" values="1;1;0;0"/></text>
<text x="200" y="444" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">20<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1022;0.3154;0.3156;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="444" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">70<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3154;0.3156;0.5287;0.5289;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="444" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">92<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5287;0.5289;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6932;0.6933;1.0000" values="0;0;1;1"/><rect x="330" y="424" width="600" height="90" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="346" y="448" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">同じ天気の値でも、種類ごとに、高さ方向の密度が違う</text>
<text x="346" y="471" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">厚さの比: 層雲 0.20 : 積雲 0.70 : 積乱雲 0.92。厚いほど、暗く、影が濃い</text>
<text x="346" y="493" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">雲の形 = 横の形(ノイズ)× 高さの形(プロファイル)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">雲の層の中の、高さごとの密度を決める<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">種類ごとに、密度の山の位置と幅が違う<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.7065;0.7067;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">プロファイルを掛けると、雲の底は平らに、頂上は丸くなる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:cloud-profiles:end -->

### 高度プロファイルの考え方

雲の種類ごとに「雲の層の中での高さ」と「密度」の関係が違います。層の下端を 0、上端を 1 とした正規化した高さ h で表します。

* <strong>層雲</strong>：下側に偏った平らな密度。h = 0.0〜0.2 あたりで密度が立ち上がり、すぐ下がる。
* <strong>層積雲</strong>：層の下半分に厚みがある、緩やかな山形。
* <strong>積雲</strong>：下端がくっきり平らで（雲底）、上へ行くほど丸く膨らみてっぺんで急に消える。

これらを関数として `h` から密度の倍率を返す形で持ちます（たとえば、積雲なら `saturate(remap(h, 0.0, 0.07, 0, 1)) * saturate(remap(h, 0.2, 1.0, 1, 0))` のような台形）。ノイズで作った形にこの高度プロファイルを掛けると、雲底が平らで頂上が丸い雲らしい輪郭が得られます。

### 天気の制御

どの種類の雲がどこにどれだけあるかは、<strong>天気マップ</strong>（2D のテクスチャ）で制御するのが一般的です。たとえば、R チャンネルにカバレッジ（雲の量）、G チャンネルに降水（雨雲かどうか）、B チャンネルに雲の種類（層雲〜積雲の混合比）を入れます。このマップを風でスクロールさせるだけで、天気が時間とともに移り変わります。晴れの日は R を小さく曇りの日は大きくすれば、同じ仕組みで天候が切り替わります。

### 層の形状（球殻）

地球は丸いので雲の層は<strong>平面でなく球殻</strong>として扱います。内側の球（地表から高度 1.5 km）と外側の球（高度 4 km）の間が雲の層です。平面の層にすると地平線の方向で層が際限なく遠くまで続いて、雲が細長く伸びて見えます。球殻なら遠くの雲は地平線の向こうに自然に消えます。半径は地球の半径 6371 km に高度を足したものです。

## 雲の種類と高さ

雲には <strong>種類</strong>があり <strong>高さ</strong>と形が、違います。同じノイズから種類ごとの雲を、作るには高さ方向の密度の山（高さのグラデーション）を、変えます。

| 種類 | 高さ | 形 | 見た目 |
| --- | --- | --- | --- |
| 層雲（stratus） | 低い（0〜2 km） | 薄く、平ら | 空を覆う灰色の層。霧の持ち上がったような |
| 積雲（cumulus） | 中（1〜3 km） | もこもこ。底は平ら上は丸い | 晴れた日の、綿雲 |
| 積乱雲（cumulonimbus） | 低〜高（1〜12 km） | 非常に高く、伸びる。上端がかなとこ状 | 入道雲、雷雲 |

## 高さのグラデーション

<strong>雲の層</strong>（惑星を覆う球殻）の中で、<strong>高さの割合</strong>（`h`: 0 = 底、1 = 上端）に応じて密度に掛ける、係数です。

```hlsl
// 高さの割合 h と、種類 type（0 = 層雲、0.5 = 積雲、1 = 積乱雲）から、高さ方向の、密度の山を返す。
float HeightGradient(float h, float type) {
  // 層雲: 低い位置に、薄い層。0〜0.1 で立ち上がり、0.2〜0.3 で、消える。
  float stratus = Remap(h, 0.0, 0.1, 0.0, 1.0) * Remap(h, 0.2, 0.3, 1.0, 0.0);
  // 積雲: 0〜0.1 で、立ち上がり（底は、はっきり）、0.6〜0.95 で、ゆるやかに、消える（上は、丸い）。
  float cumulus = Remap(h, 0.0, 0.1, 0.0, 1.0) * Remap(h, 0.6, 0.95, 1.0, 0.0);
  // 積乱雲: 0〜0.1 で、立ち上がり、0.9〜1.0 まで、ほぼ、一定（高く、伸びる）。
  float cumulonimbus = Remap(h, 0.0, 0.07, 0.0, 1.0) * Remap(h, 0.9, 1.0, 1.0, 0.0);
```

<strong>3 つの関数</strong>は <strong>どれも `Remap` で、立ち上がり</strong>（底）と消え方（上端）を、作ります。

- 層雲は高さ 0.2〜0.3 でもう、消える（薄い層）
- 積雲は 0.6 からゆっくり消えて上端が丸い
- 積乱雲はほぼ上端まで密度が、続く（高く伸びる）

```hlsl
  // 種類に応じて、3 つを、補間する（0〜0.5 で、層雲 → 積雲、0.5〜1 で、積雲 → 積乱雲）。
  float a = lerp(stratus, cumulus, saturate(type * 2.0));
  return lerp(a, cumulonimbus, saturate(type * 2.0 - 1.0));
}
```

<strong>種類</strong>（0〜1）で <strong>3 つの関数を、なめらかに補間</strong>します。天気マップ（[Cloud Density Model](density-model.md)）の、B チャンネルに種類を描いておけば、場所ごとに雲の種類が変わります。

## 雲の層の構成

<strong>雲を描く範囲</strong>は <strong>惑星の周りの、2 つの球</strong>（底の球と上端の球）に、挟まれた殻です。

```text
         上端の球（半径 = 惑星 + 雲の上端の、高さ）
       ╭─────────────╮
      ╱  ╭─────────╮  ╲        ← 雲は、この殻の中だけに、ある
     │  ╱  惑星     ╲  │
      ╲  ╲  ╱        ╱ ╱
       ╰──╰─────────╯──╯
         底の球（半径 = 惑星 + 雲の、底の高さ）
```

| 値 | 例 |
| --- | --- |
| 惑星の半径 | 6,360 km |
| 雲の底の高さ | 1,500 m |
| 雲の上端の高さ | 4,000 m |
| 殻の厚さ | 2,500 m |

```hlsl
// 視線が、雲の殻と、交わる区間（入口と、出口）を、求める。レイマーチは、この区間だけ。
float2 CloudLayerIntersect(float3 origin, float3 dir) {
  float2 t_bottom = RaySphere(origin, dir, g_planet_radius + g_cloud_bottom);
  float2 t_top = RaySphere(origin, dir, g_planet_radius + g_cloud_top);
  float height = length(origin) - g_planet_radius;
  float t_start, t_end;
  if (height < g_cloud_bottom) {                         // カメラが、雲の下
    t_start = t_bottom.y;                                // 底の球の、出口
    t_end = t_top.y;                                     // 上端の球の、出口
  } else if (height > g_cloud_top) {                     // カメラが、雲の上
    t_start = t_top.x;                                   // 上端の球の、入口
    t_end = t_bottom.x;                                  // 底の球の、入口
  } else {                                               // カメラが、雲の中
    t_start = 0.0;
    t_end = (t_bottom.x > 0.0) ? t_bottom.x : t_top.y;
  }
  return float2(t_start, t_end);
}
```

<strong>カメラの位置</strong>（<strong>雲の下、中、上</strong>）で入口と出口の組み合わせが、変わります。この区間だけをレイマーチします（[Cloud Raymarching](raymarch.md)）。

## 複数の層

<strong>低い雲</strong>（層雲、積雲）と <strong>高い雲</strong>（巻雲）を、別の層として重ねることもできます。

| 層 | 高さ | 描き方 |
| --- | --- | --- |
| 低い雲（積雲、層雲） | 1〜4 km | ボリューム（レイマーチ。本物の立体感） |
| 高い雲（巻雲、巻層雲） | 6〜10 km | 2D の、テクスチャ（空に貼る。立体感は不要。安い） |

<strong>高い雲</strong>は <strong>遠く薄く</strong>、立体感が見えないのでボリュームで、描く必要はありません。レイマーチは低い雲だけに使います（[Cheap Alternatives](cheap.md)）。

## 雲の遠近

<strong>地平線の近く</strong>では <strong>視線が、雲の殻を非常に長く通り</strong>ます。レイマーチの距離が長くなり重いです。

| 工夫 | 内容 |
| --- | --- |
| 最大距離を決める | 一定の距離（50 km）で、打ち切る。それ以上は霧の色にフェード |
| ステップを距離で広げる | 遠いほど、ステップを大きくする（遠くの細部は、見えない） |
| 遠景は低解像度 | 遠くの雲は、粗い（ノイズのミップを読む） |

## よくあるミス

??? failure "どの雲も同じ形に見える"
    <strong>高さ別の密度プロファイル</strong>を<strong>使い分ける</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 高度ごとに、密度のプロファイルを変える

## 参考

- Schneider, Vos, "The Real-Time Volumetric Cloudscapes of Horizon: Zero Dawn", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Schneider, "Nubis: Authoring Real-Time Volumetric Cloudscapes with the Decima Engine", SIGGRAPH 2017, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Clouds](index.md)
- [Cloud Density Model](density-model.md)
