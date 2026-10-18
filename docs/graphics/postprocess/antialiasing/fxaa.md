---
title: FXAA
tags:
  - 描画
---

# FXAA

<strong>FXAA（Fast Approximate Anti-Aliasing）</strong>は、**完成した画像だけを見て、「縁らしい所」を見つけてぼかす**、**1 パスの後処理 AA** です。**深度も法線も速度も要らず、どんなレンダラーにも後付けできる**ので、**導入が非常に簡単**で**コストも小さい**です。**一方で縁以外（テクスチャの文字や細かい模様）まで少しぼかし、時間的なちらつきは直せません**。このページでは、**考え方・輝度による縁の検出・縁の向きと方向に沿ったぼかし・品質プリセット・弱点と使いどころ**を説明します。

!!! tip "ポイント"
    - FXAA ＝ <strong>最終画像の輝度から、コントラストが高い所（縁）を見つけ、縁に沿った方向と直交方向に、ぼかす</strong>。
    - <strong>入力は、1 枚の画像だけ</strong>。<strong>深度・速度が要らない</strong>。<strong>1 パス</strong>。
    - <strong>低コスト</strong>（1080p で 0.2〜0.5 ms）。<strong>どの描画方式にも付けられる</strong>。
    - <strong>欠点</strong>：<strong>文字・細かい模様も少しぼける</strong>。<strong>時間的なちらつきは残る</strong>。<strong>細い線は救えない</strong>。
    - <strong>輝度はガンマ空間（LDR・トーンマップ後）</strong>で<strong>判定する</strong>（<strong>人の見た目に近いコントラスト</strong>）。
    - <strong>UI を描く前に掛ける</strong>。

<!-- fig:fxaa-edge:begin -->

<svg class="fig illust motion" data-fig="fxaa-edge" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-fxaa-edge" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">FXAA: 輝度の差が大きい画素だけを見つけて、周りの色と混ぜる(後処理 1 回)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">縁のある 20×8 画素の画像。まず、周りと輝度が大きく違う画素を探し、そこだけ、ぼかす</text>
<rect x="30" y="100" width="260.0" height="104.0" fill="#ffffff" stroke="#64748b" stroke-width="1.8" rx="6"/>
<text x="30" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#64748b">① 入力(ジャギー)</text>
<rect x="30.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="43.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="56.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="69.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="82.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="95.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="108.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="121.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="134.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="147.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="160.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="173.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="186.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="199.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="212.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="225.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="238.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="251.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="264.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="277.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="30.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="43.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="56.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="69.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="82.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="95.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="108.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="121.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="134.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="147.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="160.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="173.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="186.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="199.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="212.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="225.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="238.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="251.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="264.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="277.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="30.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="43.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="56.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="69.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="82.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="95.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="108.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="121.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="134.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="147.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="160.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="173.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="186.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="199.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="212.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="225.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="238.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="251.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="264.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="277.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="30.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="43.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="56.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="69.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="82.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="95.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="108.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="121.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="134.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="147.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="160.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="173.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="186.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="199.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="212.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="225.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="238.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="251.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="264.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="277.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="30.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="43.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="56.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="69.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="82.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="95.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="108.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="121.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="134.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="147.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="160.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="173.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="186.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="199.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="212.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="225.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="238.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="251.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="264.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="277.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="30.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="43.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="56.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="69.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="82.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="95.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="108.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="121.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="134.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="147.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="160.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="173.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="186.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="199.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="212.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="225.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="238.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="251.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="264.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="277.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="30.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="43.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="56.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="69.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="82.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="95.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="108.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="121.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="134.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="147.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="160.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="173.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="186.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="199.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="212.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="225.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="238.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="251.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="264.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="277.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="30.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="43.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="56.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="69.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="82.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="95.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="108.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="121.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="134.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="147.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="160.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="173.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="186.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="199.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="212.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="225.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="238.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="251.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="264.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="277.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335" y="100" width="260.0" height="104.0" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="335" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">② 縁の画素を探す(赤枠)</text>
<rect x="335.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="348.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="361.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="374.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="387.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="400.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="413.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="426.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="439.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="452.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="465.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="478.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="491.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="504.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="517.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="530.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="543.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="556.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="569.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="582.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="348.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="361.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="374.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="387.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="400.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="413.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="426.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="439.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="452.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="465.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="478.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="491.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="504.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="517.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="530.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="543.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="556.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="569.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="582.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="348.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="361.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="374.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="387.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="400.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="413.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="426.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="439.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="452.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="465.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="478.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="491.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="504.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="517.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="530.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="543.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="556.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="569.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="582.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="348.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="361.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="374.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="387.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="400.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="413.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="426.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="439.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="452.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="465.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="478.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="491.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="504.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="517.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="530.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="543.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="556.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="569.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="582.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="348.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="361.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="374.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="387.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="400.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="413.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="426.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="439.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="452.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="465.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="478.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="491.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="504.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="517.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="530.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="543.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="556.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="569.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="582.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="348.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="361.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="374.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="387.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="400.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="413.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="426.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="439.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="452.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="465.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="478.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="491.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="504.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="517.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="530.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="543.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="556.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="569.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="582.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="348.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="361.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="374.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="387.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="400.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="413.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="426.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="439.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="452.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="465.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="478.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="491.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="504.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="517.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="530.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="543.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="556.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="569.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="582.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="335.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="348.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="361.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="374.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="387.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="400.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="413.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="426.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="439.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="452.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="465.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="478.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="491.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="504.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="517.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="530.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="543.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#262626"/></rect>
<rect x="556.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="569.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="582.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0256" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="361.0" y="100.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0890;0.0892;1.0000" values="0;0;1;1"/></rect>
<rect x="374.0" y="100.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0952;0.0954;1.0000" values="0;0;1;1"/></rect>
<rect x="387.0" y="100.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1013;0.1015;1.0000" values="0;0;1;1"/></rect>
<rect x="374.0" y="113.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0962;0.0964;1.0000" values="0;0;1;1"/></rect>
<rect x="387.0" y="113.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1024;0.1026;1.0000" values="0;0;1;1"/></rect>
<rect x="400.0" y="113.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1085;0.1087;1.0000" values="0;0;1;1"/></rect>
<rect x="413.0" y="113.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1147;0.1149;1.0000" values="0;0;1;1"/></rect>
<rect x="400.0" y="126.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1095;0.1097;1.0000" values="0;0;1;1"/></rect>
<rect x="413.0" y="126.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1157;0.1159;1.0000" values="0;0;1;1"/></rect>
<rect x="426.0" y="126.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1218;0.1221;1.0000" values="0;0;1;1"/></rect>
<rect x="439.0" y="126.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1280;0.1282;1.0000" values="0;0;1;1"/></rect>
<rect x="426.0" y="139.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1229;0.1231;1.0000" values="0;0;1;1"/></rect>
<rect x="439.0" y="139.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1290;0.1292;1.0000" values="0;0;1;1"/></rect>
<rect x="452.0" y="139.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1352;0.1354;1.0000" values="0;0;1;1"/></rect>
<rect x="465.0" y="139.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1413;0.1415;1.0000" values="0;0;1;1"/></rect>
<rect x="452.0" y="152.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1362;0.1364;1.0000" values="0;0;1;1"/></rect>
<rect x="465.0" y="152.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1424;0.1426;1.0000" values="0;0;1;1"/></rect>
<rect x="478.0" y="152.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1485;0.1487;1.0000" values="0;0;1;1"/></rect>
<rect x="491.0" y="152.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1547;0.1549;1.0000" values="0;0;1;1"/></rect>
<rect x="478.0" y="165.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1495;0.1497;1.0000" values="0;0;1;1"/></rect>
<rect x="491.0" y="165.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1557;0.1559;1.0000" values="0;0;1;1"/></rect>
<rect x="504.0" y="165.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1618;0.1621;1.0000" values="0;0;1;1"/></rect>
<rect x="517.0" y="165.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1680;0.1682;1.0000" values="0;0;1;1"/></rect>
<rect x="504.0" y="178.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1629;0.1631;1.0000" values="0;0;1;1"/></rect>
<rect x="517.0" y="178.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1690;0.1692;1.0000" values="0;0;1;1"/></rect>
<rect x="530.0" y="178.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1752;0.1754;1.0000" values="0;0;1;1"/></rect>
<rect x="543.0" y="178.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1813;0.1815;1.0000" values="0;0;1;1"/></rect>
<rect x="530.0" y="191.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1762;0.1764;1.0000" values="0;0;1;1"/></rect>
<rect x="543.0" y="191.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1824;0.1826;1.0000" values="0;0;1;1"/></rect>
<rect x="556.0" y="191.0" width="13.0" height="13.0" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1885;0.1887;1.0000" values="0;0;1;1"/></rect>
<rect x="640" y="100" width="260.0" height="104.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="640" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">③ 縁だけ、周りと混ぜた結果</text>
<rect x="640.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4615" values="#e5e7eb;#262626"/></rect>
<rect x="653.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4652" values="#e5e7eb;#262626"/></rect>
<rect x="666.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4689" values="#e5e7eb;#404040"/></rect>
<rect x="679.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4726" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="692.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4763" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="705.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="718.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4837" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="731.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4874" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="744.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4911" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="757.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4948" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="770.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4985" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="783.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="796.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5058" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="809.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5095" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="822.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5132" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="835.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5169" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="848.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5206" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="861.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5243" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="874.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5280" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="887.0" y="100.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5317" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="640.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4615" values="#e5e7eb;#262626"/></rect>
<rect x="653.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4652" values="#e5e7eb;#262626"/></rect>
<rect x="666.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4689" values="#e5e7eb;#262626"/></rect>
<rect x="679.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4726" values="#e5e7eb;#404040"/></rect>
<rect x="692.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4763" values="#e5e7eb;#595959"/></rect>
<rect x="705.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="718.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4837" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="731.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4874" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="744.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4911" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="757.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4948" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="770.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4985" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="783.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="796.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5058" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="809.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5095" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="822.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5132" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="835.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5169" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="848.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5206" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="861.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5243" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="874.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5280" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="887.0" y="113.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5317" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="640.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4615" values="#e5e7eb;#262626"/></rect>
<rect x="653.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4652" values="#e5e7eb;#262626"/></rect>
<rect x="666.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4689" values="#e5e7eb;#262626"/></rect>
<rect x="679.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4726" values="#e5e7eb;#262626"/></rect>
<rect x="692.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4763" values="#e5e7eb;#262626"/></rect>
<rect x="705.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#404040"/></rect>
<rect x="718.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4837" values="#e5e7eb;#595959"/></rect>
<rect x="731.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4874" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="744.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4911" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="757.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4948" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="770.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4985" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="783.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="796.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5058" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="809.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5095" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="822.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5132" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="835.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5169" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="848.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5206" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="861.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5243" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="874.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5280" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="887.0" y="126.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5317" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="640.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4615" values="#e5e7eb;#262626"/></rect>
<rect x="653.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4652" values="#e5e7eb;#262626"/></rect>
<rect x="666.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4689" values="#e5e7eb;#262626"/></rect>
<rect x="679.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4726" values="#e5e7eb;#262626"/></rect>
<rect x="692.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4763" values="#e5e7eb;#262626"/></rect>
<rect x="705.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#262626"/></rect>
<rect x="718.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4837" values="#e5e7eb;#262626"/></rect>
<rect x="731.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4874" values="#e5e7eb;#404040"/></rect>
<rect x="744.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4911" values="#e5e7eb;#595959"/></rect>
<rect x="757.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4948" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="770.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4985" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="783.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="796.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5058" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="809.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5095" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="822.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5132" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="835.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5169" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="848.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5206" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="861.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5243" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="874.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5280" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="887.0" y="139.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5317" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="640.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4615" values="#e5e7eb;#262626"/></rect>
<rect x="653.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4652" values="#e5e7eb;#262626"/></rect>
<rect x="666.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4689" values="#e5e7eb;#262626"/></rect>
<rect x="679.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4726" values="#e5e7eb;#262626"/></rect>
<rect x="692.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4763" values="#e5e7eb;#262626"/></rect>
<rect x="705.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#262626"/></rect>
<rect x="718.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4837" values="#e5e7eb;#262626"/></rect>
<rect x="731.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4874" values="#e5e7eb;#262626"/></rect>
<rect x="744.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4911" values="#e5e7eb;#262626"/></rect>
<rect x="757.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4948" values="#e5e7eb;#404040"/></rect>
<rect x="770.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4985" values="#e5e7eb;#595959"/></rect>
<rect x="783.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="796.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5058" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="809.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5095" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="822.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5132" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="835.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5169" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="848.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5206" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="861.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5243" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="874.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5280" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="887.0" y="152.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5317" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="640.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4615" values="#e5e7eb;#262626"/></rect>
<rect x="653.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4652" values="#e5e7eb;#262626"/></rect>
<rect x="666.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4689" values="#e5e7eb;#262626"/></rect>
<rect x="679.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4726" values="#e5e7eb;#262626"/></rect>
<rect x="692.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4763" values="#e5e7eb;#262626"/></rect>
<rect x="705.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#262626"/></rect>
<rect x="718.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4837" values="#e5e7eb;#262626"/></rect>
<rect x="731.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4874" values="#e5e7eb;#262626"/></rect>
<rect x="744.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4911" values="#e5e7eb;#262626"/></rect>
<rect x="757.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4948" values="#e5e7eb;#262626"/></rect>
<rect x="770.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4985" values="#e5e7eb;#262626"/></rect>
<rect x="783.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#e5e7eb;#404040"/></rect>
<rect x="796.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5058" values="#e5e7eb;#595959"/></rect>
<rect x="809.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5095" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="822.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5132" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="835.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5169" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="848.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5206" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="861.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5243" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="874.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5280" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="887.0" y="165.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5317" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="640.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4615" values="#e5e7eb;#262626"/></rect>
<rect x="653.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4652" values="#e5e7eb;#262626"/></rect>
<rect x="666.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4689" values="#e5e7eb;#262626"/></rect>
<rect x="679.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4726" values="#e5e7eb;#262626"/></rect>
<rect x="692.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4763" values="#e5e7eb;#262626"/></rect>
<rect x="705.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#262626"/></rect>
<rect x="718.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4837" values="#e5e7eb;#262626"/></rect>
<rect x="731.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4874" values="#e5e7eb;#262626"/></rect>
<rect x="744.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4911" values="#e5e7eb;#262626"/></rect>
<rect x="757.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4948" values="#e5e7eb;#262626"/></rect>
<rect x="770.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4985" values="#e5e7eb;#262626"/></rect>
<rect x="783.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#e5e7eb;#262626"/></rect>
<rect x="796.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5058" values="#e5e7eb;#262626"/></rect>
<rect x="809.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5095" values="#e5e7eb;#404040"/></rect>
<rect x="822.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5132" values="#e5e7eb;#595959"/></rect>
<rect x="835.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5169" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="848.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5206" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="861.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5243" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="874.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5280" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="887.0" y="178.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5317" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="640.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4615" values="#e5e7eb;#262626"/></rect>
<rect x="653.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4652" values="#e5e7eb;#262626"/></rect>
<rect x="666.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4689" values="#e5e7eb;#262626"/></rect>
<rect x="679.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4726" values="#e5e7eb;#262626"/></rect>
<rect x="692.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4763" values="#e5e7eb;#262626"/></rect>
<rect x="705.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#262626"/></rect>
<rect x="718.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4837" values="#e5e7eb;#262626"/></rect>
<rect x="731.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4874" values="#e5e7eb;#262626"/></rect>
<rect x="744.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4911" values="#e5e7eb;#262626"/></rect>
<rect x="757.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4948" values="#e5e7eb;#262626"/></rect>
<rect x="770.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4985" values="#e5e7eb;#262626"/></rect>
<rect x="783.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#e5e7eb;#262626"/></rect>
<rect x="796.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5058" values="#e5e7eb;#262626"/></rect>
<rect x="809.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5095" values="#e5e7eb;#262626"/></rect>
<rect x="822.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5132" values="#e5e7eb;#262626"/></rect>
<rect x="835.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5169" values="#e5e7eb;#404040"/></rect>
<rect x="848.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5206" values="#e5e7eb;#595959"/></rect>
<rect x="861.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5243" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="874.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5280" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="887.0" y="191.0" width="13.3" height="13.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5317" values="#e5e7eb;#f2f2f2"/></rect>
<text x="335" y="330" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">縁の画素:</text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0767;0.0769;1.0000" values="1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0767;0.0769;0.0829;0.0831;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0829;0.0831;0.0890;0.0892;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0890;0.0892;0.0952;0.0954;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0952;0.0954;0.1013;0.1015;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">5<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1013;0.1015;0.1075;0.1077;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">7<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1075;0.1077;0.1136;0.1138;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">9<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1136;0.1138;0.1198;0.1200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">11<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1198;0.1200;0.1259;0.1262;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">13<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1259;0.1262;0.1321;0.1323;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">15<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1321;0.1323;0.1383;0.1385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">17<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1383;0.1385;0.1444;0.1446;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">19<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1444;0.1446;0.1506;0.1508;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">21<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1506;0.1508;0.1567;0.1569;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">23<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1567;0.1569;0.1629;0.1631;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">25<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1629;0.1631;0.1690;0.1692;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">27<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1690;0.1692;0.1752;0.1754;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">29<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1752;0.1754;0.1813;0.1815;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">30<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1813;0.1815;0.1875;0.1877;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">30<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1875;0.1877;0.1936;0.1938;1.0000" values="0;0;1;1;0;0"/></text>
<text x="425" y="332" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">30<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1936;0.1938;1.0000" values="0;0;1;1"/></text>
<text x="465" y="332" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b">/ 160</text>
<text x="640" y="330" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">ずれ(正解との平均差):</text>
<text x="640" y="356" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">入力 0.022 → 結果 0.022<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5383;0.5385;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5639;0.5641;1.0000" values="0;0;1;1"/><rect x="30" y="384" width="900" height="110" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="46" y="408" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">縁の画素 30 個だけ、念入りに処理。残り 130 個(81%)は、輝度の差が小さいので、そのまま</text>
<text x="46" y="432" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">手順: ① 周りの 4 画素と輝度の差を調べる → ② 差が大きければ縁 → ③ 縁なら、周りの色と混ぜる(差が大きいほど、多く)</text>
<text x="46" y="454" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">1 回の後処理で済み、とても軽い。ただし、細かい模様まで、ぼかしてしまうことがある</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ジャギーは、輝度の差が大きい所(縁)にだけ出る<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0767;0.0769;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">画面をなぞって、縁の画素に印を付ける<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0767;0.0769;0.4613;0.4615;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">縁の画素だけを、周りの画素と混ぜる<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4613;0.4615;0.5639;0.5641;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">縁以外は、触らないので軽い<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5639;0.5641;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:fxaa-edge:end -->

## The Idea {#考え方}

**FXAA は画像を見て、次の 3 段階**を**行います**。

<svg class="fig illust" viewBox="0 0 780 190" role="img" aria-label="FXAA の流れ">
<text x="20" y="26" class="fig-title">FXAA：縁を見つけて、縁に沿って分析し、縁をまたいでぼかす</text>
<defs><marker id="fx-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<g font-size="13">
<rect x="20" y="56" width="200" height="90" rx="8" fill="#4c8bf5" fill-opacity="0.18" stroke="#4c8bf5" stroke-width="2"/><text x="120" y="86" text-anchor="middle" style="font-weight:700">① 縁を探す</text><text x="120" y="108" text-anchor="middle" style="font-size:11px">周囲 5 画素の輝度差が、</text><text x="120" y="124" text-anchor="middle" style="font-size:11px">しきい値以上なら縁</text>
<rect x="290" y="56" width="200" height="90" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/><text x="390" y="86" text-anchor="middle" style="font-weight:700">② 縁の向きと端</text><text x="390" y="108" text-anchor="middle" style="font-size:11px">水平か垂直か、</text><text x="390" y="124" text-anchor="middle" style="font-size:11px">縁がどこまで続くか</text>
<rect x="560" y="56" width="200" height="90" rx="8" fill="#2ea043" fill-opacity="0.18" stroke="#2ea043" stroke-width="2"/><text x="660" y="86" text-anchor="middle" style="font-weight:700">③ 縁と直交にぼかす</text><text x="660" y="108" text-anchor="middle" style="font-size:11px">縁の位置に応じた、</text><text x="660" y="124" text-anchor="middle" style="font-size:11px">サブピクセルのずれで混ぜる</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="222" y1="101" x2="288" y2="101" marker-end="url(#fx-arrow)"/><line x1="492" y1="101" x2="558" y2="101" marker-end="url(#fx-arrow)"/></g>
</svg>

## ① Edge Detection {#①-縁の検出}

**画素とその上下左右の 5 画素の輝度**を**調べ、最大と最小の差**が**しきい値より小さければ、縁ではない**として**そのまま返します**（**早期終了**）。

```hlsl
float Luma(float3 rgb) {
  return dot(rgb, float3(0.299, 0.587, 0.114));
}

float4 FxaaPS(float2 uv) {
  float3 c = color.SampleLevel(linear_clamp, uv, 0).rgb;
  float luma_m = Luma(c);
  float luma_n = Luma(color.SampleLevel(linear_clamp, uv + float2(0, -1) * texel, 0).rgb);
  float luma_s = Luma(color.SampleLevel(linear_clamp, uv + float2(0, 1) * texel, 0).rgb);
  float luma_w = Luma(color.SampleLevel(linear_clamp, uv + float2(-1, 0) * texel, 0).rgb);
  float luma_e = Luma(color.SampleLevel(linear_clamp, uv + float2(1, 0) * texel, 0).rgb);

  float luma_min = min(luma_m, min(min(luma_n, luma_s), min(luma_w, luma_e)));
  float luma_max = max(luma_m, max(max(luma_n, luma_s), max(luma_w, luma_e)));
  float range = luma_max - luma_min;
  if (range < max(kEdgeThresholdMin, luma_max * kEdgeThreshold)) {
    return float4(c, 1);
  }
  // 続きは ② ③
}
```

| 点 | 説明 |
| --- | --- |
| <strong>`Luma`（0.299, 0.587, 0.114）</strong> | **輝度の近似**（**緑のチャンネルだけで代用する簡易版もある**） |
| <strong>`kEdgeThreshold`（約 0.125〜0.166）</strong> | **明るさに対する相対のしきい値**（**暗い所でも検出できる**） |
| <strong>`kEdgeThresholdMin`（約 0.0312）</strong> | **暗すぎる所は無視**する下限 |
| **早期終了** | **縁でない画素（大半）は、ここで終わる → 速い** |

## ② Edge Direction and Searching Along the Edge {#②-縁の向きと端の探索}

**縁が水平か垂直か**を**判定**し、**縁に沿って両方向へ進み、縁の端**を**探します**。

縁の判定です。縁の向きは、水平方向の輝度の変化と、垂直方向の変化の大きさを比べて決めます。縁の反対側は、縁をまたぐ輝度差が大きい側（上か下、左か右）を決めます。端の探索は、縁に沿って進み、輝度がある程度変わった所（縁の終わり）まで行います。

**縁の端までの距離**から、**画素が縁のどの位置にあるか**が**分かり**、<strong>ぼかす量（サブピクセルのずらし）</strong>を**決めます**。

## ③ Blurring Perpendicular to the Edge {#③-縁と直交方向のぼかし}

<strong>画素の位置（縁の端に近いか、中央か）</strong>に**応じて**、**縁と直交する方向にサンプル位置をずらして読み**ます。**バイリニア補間が隣の画素と混ぜてくれる**ので、**縁がなめらか**になります。

ぼかしの要点です。サブピクセルのずれは、縁に対する画素の位置から、ずらす量を決めます。ずらした位置を読むだけで、バイリニア補間が隣と混ぜてくれます（サンプル 1 回）。孤立した細い線や点には、別計算のサブピクセル AA で、周りと平均してぼかします（係数で強さを調整できます）。

## Quality Presets {#品質プリセット}

**FXAA には、品質プリセット**（**サンプル数・端の探索の歩数**が違う）が**あります**。

| プリセット | 内容 | コスト |
| --- | --- | --- |
| <strong>低（10）</strong> | **探索の歩数が少ない** | **最小** |
| <strong>中（15）</strong> | **標準** | **小** |
| <strong>高（29）</strong> | **歩数が多い・端の探索が丁寧** | **少し大きい** |

**実際の実装**（**Timothy Lottes の FXAA 3.11**）は、**数百行の HLSL**です。**公開されているものをそのまま使う**のが**一般的**です。

## Weaknesses {#弱点}

| 弱点 | 理由 |
| --- | --- |
| **文字・細かい模様がぼける** | **コントラストの高い所を、すべて縁とみなす** |
| **時間的なちらつきは残る** | **1 フレームの画像だけを見ている** |
| **細い線・点の途切れは救えない** | **画像に情報がない** |
| **斜めの縁の品質は、MSAA に劣る** | **推測で補う** |
| **半透明・パーティクルの縁にも作用** | **画像なので区別できない** |


原典は、Timothy Lottes（NVIDIA）の "FXAA" の白書（2009）です。

原典は、Timothy Lottes（NVIDIA）の "FXAA" の白書（2009）です。

## Better Approaches {#より良いやり方}

| 工夫 | 内容 |
| --- | --- |
| **UI の前に掛ける** | **文字がぼけない** |
| **ガンマ空間（トーンマップ後）で** | **HDR のままだと縁の検出がずれる** |
| **しきい値を調整** | **強すぎるとぼやけ、弱すぎると残る** |
| **ミニマムなコスト用途に** | **低スペック・モバイル・ウェブ** |
| **他の方式に置き換える** | **品質重視なら SMIL・TAA**（[SMAA](smaa.md)・[TAA](taa.md)） |
| **文字をマスクして除外** | **ぼけを避ける** |

## Common Mistakes {#よくあるミス}

??? failure "UI や文字まで、ぼけてしまう"
    **UI を描く前**に FXAA を掛ける。**UI は別パス**。

??? failure "HDR のまま FXAA を掛けて、縁が検出されない・おかしい"
    **トーンマップ後（ガンマ空間）の LDR で**行う。

??? failure "動くとちらつきが残る"
    **FXAA は時間方向を見ない**。**TAA を併用または置換**。

??? failure "シーン全体がぼやけて見える"
    **しきい値を上げる**、**サブピクセル AA の係数を下げる**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] FXAA ＝ <strong>最終画像の輝度から縁を見つけ、縁と直交方向にぼかす</strong>。<strong>1 パス</strong>
    - [x] <strong>深度・速度が不要</strong>で<strong>どんな描画にも後付け</strong>、<strong>低コスト</strong>
    - [x] <strong>弱点</strong>：<strong>文字もぼける・ちらつきは残る・細い線は救えない</strong>
    - [x] <strong>LDR（トーンマップ後）で、UI の前</strong>に掛ける
    - [x] <strong>品質重視なら SMAA・TAA</strong>

## References {#参考}

- Lottes, "FXAA"（NVIDIA White Paper, 2009）
- Lottes, "FXAA 3.11 Source"
- Jimenez et al., "Filtering Approaches for Real-Time Anti-Aliasing"（SIGGRAPH 2011 Course）

## Related Pages {#関連ページ}

- [Anti-Aliasing](index.md)
- [MSAA](msaa.md)
- [SMAA](smaa.md)
- [TAA](taa.md)
