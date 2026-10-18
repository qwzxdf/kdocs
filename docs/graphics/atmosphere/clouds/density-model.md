---
title: Cloud Density Model
tags:
  - 描画
---

# Cloud Density Model

<strong>雲の形は、ノイズで作ります</strong>。<strong>低周波のノイズで大きな形、高周波のノイズで細部</strong>を作り、重ねます。このページでは、雲の密度のモデルを説明します。

!!! tip "ポイント"
    - 基本形：Perlin-Worley ノイズ。
    - 細部：高周波のノイズで、縁を削る。
    - カバレッジで、雲の量を制御。
    - 3D テクスチャに事前計算して、実行時に読む。

<!-- fig:cloud-coverage:begin -->

<svg class="fig illust motion" data-fig="cloud-coverage" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-cloud-coverage" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">雲の量(カバレッジ): ノイズから、しきい値を引いて、残った所だけを、雲にする</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">32×12 のノイズ(0〜1)。カバレッジ 0.2・0.5・0.8 で、雲になる画素の割合と、雲のつながり(塊の数)を計算する</text>
<rect x="30" y="96" width="294.0" height="114.0" fill="#ffffff" stroke="#64748b" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#64748b">元のノイズ</text>
<rect x="33.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d3d3d3"/></rect>
<rect x="42.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e1e1e1"/></rect>
<rect x="51.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="60.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b8b8b8"/></rect>
<rect x="69.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#959595"/></rect>
<rect x="78.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#cbcbcb"/></rect>
<rect x="87.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="96.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5c5c5c"/></rect>
<rect x="105.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#373737"/></rect>
<rect x="114.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#565656"/></rect>
<rect x="123.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#989898"/></rect>
<rect x="132.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e3e3e3"/></rect>
<rect x="141.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f0f0f0"/></rect>
<rect x="150.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#ababab"/></rect>
<rect x="159.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e1e1e1"/></rect>
<rect x="168.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d5d5d5"/></rect>
<rect x="177.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a3a3a3"/></rect>
<rect x="186.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5e5e5e"/></rect>
<rect x="195.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#939393"/></rect>
<rect x="204.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dbdbdb"/></rect>
<rect x="213.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c4c4c4"/></rect>
<rect x="222.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b0b0b0"/></rect>
<rect x="231.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#bababa"/></rect>
<rect x="240.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c5c5c5"/></rect>
<rect x="249.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d2d2d2"/></rect>
<rect x="258.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c1c1c1"/></rect>
<rect x="267.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5f5f5f"/></rect>
<rect x="276.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="285.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#686868"/></rect>
<rect x="294.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#757575"/></rect>
<rect x="303.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5a5a5a"/></rect>
<rect x="312.0" y="99.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#929292"/></rect>
<rect x="33.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#959595"/></rect>
<rect x="42.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9c9c9c"/></rect>
<rect x="51.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a7a7a7"/></rect>
<rect x="60.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a4a4a4"/></rect>
<rect x="69.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a2a2a2"/></rect>
<rect x="78.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b1b1b1"/></rect>
<rect x="87.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#979797"/></rect>
<rect x="96.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="105.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#585858"/></rect>
<rect x="114.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#535353"/></rect>
<rect x="123.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#878787"/></rect>
<rect x="132.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dfdfdf"/></rect>
<rect x="141.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f0f0f0"/></rect>
<rect x="150.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#bdbdbd"/></rect>
<rect x="159.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b1b1b1"/></rect>
<rect x="168.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a5a5a5"/></rect>
<rect x="177.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#979797"/></rect>
<rect x="186.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8a8a8a"/></rect>
<rect x="195.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9b9b9b"/></rect>
<rect x="204.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b5b5b5"/></rect>
<rect x="213.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b5b5b5"/></rect>
<rect x="222.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#bdbdbd"/></rect>
<rect x="231.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b3b3b3"/></rect>
<rect x="240.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#afafaf"/></rect>
<rect x="249.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d4d4d4"/></rect>
<rect x="258.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d1d1d1"/></rect>
<rect x="267.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#7f7f7f"/></rect>
<rect x="276.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4e4e4e"/></rect>
<rect x="285.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#414141"/></rect>
<rect x="294.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#565656"/></rect>
<rect x="303.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#787878"/></rect>
<rect x="312.0" y="108.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#afafaf"/></rect>
<rect x="33.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#474747"/></rect>
<rect x="42.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#484848"/></rect>
<rect x="51.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4b4b4b"/></rect>
<rect x="60.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#747474"/></rect>
<rect x="69.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8e8e8e"/></rect>
<rect x="78.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#848484"/></rect>
<rect x="87.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#787878"/></rect>
<rect x="96.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8e8e8e"/></rect>
<rect x="105.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="114.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#606060"/></rect>
<rect x="123.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#7c7c7c"/></rect>
<rect x="132.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d1d1d1"/></rect>
<rect x="141.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dfdfdf"/></rect>
<rect x="150.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="159.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#858585"/></rect>
<rect x="168.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#848484"/></rect>
<rect x="177.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9a9a9a"/></rect>
<rect x="186.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b7b7b7"/></rect>
<rect x="195.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a2a2a2"/></rect>
<rect x="204.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8b8b8b"/></rect>
<rect x="213.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9a9a9a"/></rect>
<rect x="222.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#bebebe"/></rect>
<rect x="231.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a8a8a8"/></rect>
<rect x="240.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9f9f9f"/></rect>
<rect x="249.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dbdbdb"/></rect>
<rect x="258.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e5e5e5"/></rect>
<rect x="267.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a5a5a5"/></rect>
<rect x="276.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#424242"/></rect>
<rect x="285.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#313131"/></rect>
<rect x="294.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4a4a4a"/></rect>
<rect x="303.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9c9c9c"/></rect>
<rect x="312.0" y="117.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#cacaca"/></rect>
<rect x="33.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#282828"/></rect>
<rect x="42.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#2e2e2e"/></rect>
<rect x="51.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#333333"/></rect>
<rect x="60.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#494949"/></rect>
<rect x="69.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#575757"/></rect>
<rect x="78.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#474747"/></rect>
<rect x="87.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#525252"/></rect>
<rect x="96.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9c9c9c"/></rect>
<rect x="105.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b4b4b4"/></rect>
<rect x="114.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#989898"/></rect>
<rect x="123.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9a9a9a"/></rect>
<rect x="132.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#afafaf"/></rect>
<rect x="141.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#afafaf"/></rect>
<rect x="150.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a3a3a3"/></rect>
<rect x="159.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8f8f8f"/></rect>
<rect x="168.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a6a6a6"/></rect>
<rect x="177.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#bcbcbc"/></rect>
<rect x="186.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c4c4c4"/></rect>
<rect x="195.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#929292"/></rect>
<rect x="204.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#595959"/></rect>
<rect x="213.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#727272"/></rect>
<rect x="222.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#ababab"/></rect>
<rect x="231.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b5b5b5"/></rect>
<rect x="240.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c5c5c5"/></rect>
<rect x="249.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="258.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dbdbdb"/></rect>
<rect x="267.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#aeaeae"/></rect>
<rect x="276.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#666666"/></rect>
<rect x="285.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#616161"/></rect>
<rect x="294.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#757575"/></rect>
<rect x="303.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#acacac"/></rect>
<rect x="312.0" y="126.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c7c7c7"/></rect>
<rect x="33.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#595959"/></rect>
<rect x="42.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#626262"/></rect>
<rect x="51.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#686868"/></rect>
<rect x="60.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#262626"/></rect>
<rect x="69.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#000000"/></rect>
<rect x="78.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5c5c5c"/></rect>
<rect x="87.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9f9f9f"/></rect>
<rect x="96.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a0a0a0"/></rect>
<rect x="105.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a3a3a3"/></rect>
<rect x="114.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a3a3a3"/></rect>
<rect x="123.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a3a3a3"/></rect>
<rect x="132.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#adadad"/></rect>
<rect x="141.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9c9c9c"/></rect>
<rect x="150.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="159.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d2d2d2"/></rect>
<rect x="168.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#f7f7f7"/></rect>
<rect x="177.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dedede"/></rect>
<rect x="186.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#888888"/></rect>
<rect x="195.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#909090"/></rect>
<rect x="204.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#aaaaaa"/></rect>
<rect x="213.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#818181"/></rect>
<rect x="222.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#7d7d7d"/></rect>
<rect x="231.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a5a5a5"/></rect>
<rect x="240.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#cecece"/></rect>
<rect x="249.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#ececec"/></rect>
<rect x="258.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e4e4e4"/></rect>
<rect x="267.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#969696"/></rect>
<rect x="276.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="285.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b7b7b7"/></rect>
<rect x="294.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b8b8b8"/></rect>
<rect x="303.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#858585"/></rect>
<rect x="312.0" y="135.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a3a3a3"/></rect>
<rect x="33.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#282828"/></rect>
<rect x="42.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#2b2b2b"/></rect>
<rect x="51.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#2d2d2d"/></rect>
<rect x="60.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#313131"/></rect>
<rect x="69.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#353535"/></rect>
<rect x="78.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#595959"/></rect>
<rect x="87.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#828282"/></rect>
<rect x="96.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#ababab"/></rect>
<rect x="105.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b7b7b7"/></rect>
<rect x="114.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8d8d8d"/></rect>
<rect x="123.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#858585"/></rect>
<rect x="132.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a8a8a8"/></rect>
<rect x="141.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a0a0a0"/></rect>
<rect x="150.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#858585"/></rect>
<rect x="159.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#949494"/></rect>
<rect x="168.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b4b4b4"/></rect>
<rect x="177.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c4c4c4"/></rect>
<rect x="186.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b8b8b8"/></rect>
<rect x="195.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a2a2a2"/></rect>
<rect x="204.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#919191"/></rect>
<rect x="213.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#898989"/></rect>
<rect x="222.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a1a1a1"/></rect>
<rect x="231.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a2a2a2"/></rect>
<rect x="240.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#adadad"/></rect>
<rect x="249.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e0e0"/></rect>
<rect x="258.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e9e9e9"/></rect>
<rect x="267.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#adadad"/></rect>
<rect x="276.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#7d7d7d"/></rect>
<rect x="285.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#767676"/></rect>
<rect x="294.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#808080"/></rect>
<rect x="303.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#989898"/></rect>
<rect x="312.0" y="144.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b2b2b2"/></rect>
<rect x="33.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#191919"/></rect>
<rect x="42.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#1a1a1a"/></rect>
<rect x="51.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#1d1d1d"/></rect>
<rect x="60.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#454545"/></rect>
<rect x="69.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5e5e5e"/></rect>
<rect x="78.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#626262"/></rect>
<rect x="87.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#777777"/></rect>
<rect x="96.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b1b1b1"/></rect>
<rect x="105.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="114.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#818181"/></rect>
<rect x="123.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="132.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#919191"/></rect>
<rect x="141.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8a8a8a"/></rect>
<rect x="150.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#7d7d7d"/></rect>
<rect x="159.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6c6c6c"/></rect>
<rect x="168.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#929292"/></rect>
<rect x="177.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b8b8b8"/></rect>
<rect x="186.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d2d2d2"/></rect>
<rect x="195.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b4b4b4"/></rect>
<rect x="204.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#959595"/></rect>
<rect x="213.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a3a3a3"/></rect>
<rect x="222.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c4c4c4"/></rect>
<rect x="231.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a7a7a7"/></rect>
<rect x="240.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#979797"/></rect>
<rect x="249.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#cccccc"/></rect>
<rect x="258.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="267.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#afafaf"/></rect>
<rect x="276.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5e5e5e"/></rect>
<rect x="285.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#565656"/></rect>
<rect x="294.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5f5f5f"/></rect>
<rect x="303.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8e8e8e"/></rect>
<rect x="312.0" y="153.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9b9b9b"/></rect>
<rect x="33.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#2d2d2d"/></rect>
<rect x="42.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#373737"/></rect>
<rect x="51.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#444444"/></rect>
<rect x="60.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5f5f5f"/></rect>
<rect x="69.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="78.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#565656"/></rect>
<rect x="87.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5c5c5c"/></rect>
<rect x="96.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a8a8a8"/></rect>
<rect x="105.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c1c1c1"/></rect>
<rect x="114.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9c9c9c"/></rect>
<rect x="123.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#7d7d7d"/></rect>
<rect x="132.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#686868"/></rect>
<rect x="141.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#585858"/></rect>
<rect x="150.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5d5d5d"/></rect>
<rect x="159.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="168.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a5a5a5"/></rect>
<rect x="177.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c7c7c7"/></rect>
<rect x="186.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d4d4d4"/></rect>
<rect x="195.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b2b2b2"/></rect>
<rect x="204.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#888888"/></rect>
<rect x="213.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#aeaeae"/></rect>
<rect x="222.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dadada"/></rect>
<rect x="231.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c4c4c4"/></rect>
<rect x="240.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b3b3b3"/></rect>
<rect x="249.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b7b7b7"/></rect>
<rect x="258.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b3b3b3"/></rect>
<rect x="267.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#989898"/></rect>
<rect x="276.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#646464"/></rect>
<rect x="285.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#686868"/></rect>
<rect x="294.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6b6b6b"/></rect>
<rect x="303.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#797979"/></rect>
<rect x="312.0" y="162.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="33.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6c6c6c"/></rect>
<rect x="42.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#797979"/></rect>
<rect x="51.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#888888"/></rect>
<rect x="60.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#595959"/></rect>
<rect x="69.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3c3c3c"/></rect>
<rect x="78.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#898989"/></rect>
<rect x="87.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b4b4b4"/></rect>
<rect x="96.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a5a5a5"/></rect>
<rect x="105.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a1a1a1"/></rect>
<rect x="114.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#909090"/></rect>
<rect x="123.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#757575"/></rect>
<rect x="132.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#676767"/></rect>
<rect x="141.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4c4c4c"/></rect>
<rect x="150.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#2c2c2c"/></rect>
<rect x="159.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a2a2a2"/></rect>
<rect x="168.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="177.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#dadada"/></rect>
<rect x="186.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9a9a9a"/></rect>
<rect x="195.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#bcbcbc"/></rect>
<rect x="204.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#efefef"/></rect>
<rect x="213.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d8d8d8"/></rect>
<rect x="222.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c1c1c1"/></rect>
<rect x="231.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b5b5b5"/></rect>
<rect x="240.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#ababab"/></rect>
<rect x="249.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b5b5b5"/></rect>
<rect x="258.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="267.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#777777"/></rect>
<rect x="276.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9c9c9c"/></rect>
<rect x="285.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a3a3a3"/></rect>
<rect x="294.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#949494"/></rect>
<rect x="303.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#434343"/></rect>
<rect x="312.0" y="171.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3b3b3b"/></rect>
<rect x="33.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#373737"/></rect>
<rect x="42.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#3c3c3c"/></rect>
<rect x="51.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#464646"/></rect>
<rect x="60.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#626262"/></rect>
<rect x="69.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#727272"/></rect>
<rect x="78.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#848484"/></rect>
<rect x="87.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#999999"/></rect>
<rect x="96.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#bbbbbb"/></rect>
<rect x="105.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="114.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#858585"/></rect>
<rect x="123.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#626262"/></rect>
<rect x="132.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#717171"/></rect>
<rect x="141.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5f5f5f"/></rect>
<rect x="150.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#505050"/></rect>
<rect x="159.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5f5f5f"/></rect>
<rect x="168.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8f8f8f"/></rect>
<rect x="177.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#afafaf"/></rect>
<rect x="186.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#bcbcbc"/></rect>
<rect x="195.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b7b7b7"/></rect>
<rect x="204.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b4b4b4"/></rect>
<rect x="213.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#bebebe"/></rect>
<rect x="222.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#cccccc"/></rect>
<rect x="231.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a6a6a6"/></rect>
<rect x="240.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8a8a8a"/></rect>
<rect x="249.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b3b3b3"/></rect>
<rect x="258.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c4c4c4"/></rect>
<rect x="267.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#979797"/></rect>
<rect x="276.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#616161"/></rect>
<rect x="285.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5e5e5e"/></rect>
<rect x="294.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5e5e5e"/></rect>
<rect x="303.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="312.0" y="180.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="33.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#323232"/></rect>
<rect x="42.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#373737"/></rect>
<rect x="51.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#434343"/></rect>
<rect x="60.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#707070"/></rect>
<rect x="69.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8a8a8a"/></rect>
<rect x="78.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#898989"/></rect>
<rect x="87.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9a9a9a"/></rect>
<rect x="96.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d3d3d3"/></rect>
<rect x="105.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="114.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9d9d9d"/></rect>
<rect x="123.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#717171"/></rect>
<rect x="132.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#767676"/></rect>
<rect x="141.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#636363"/></rect>
<rect x="150.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#565656"/></rect>
<rect x="159.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#444444"/></rect>
<rect x="168.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#676767"/></rect>
<rect x="177.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8b8b8b"/></rect>
<rect x="186.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a6a6a6"/></rect>
<rect x="195.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#909090"/></rect>
<rect x="204.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#777777"/></rect>
<rect x="213.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="222.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#afafaf"/></rect>
<rect x="231.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#959595"/></rect>
<rect x="240.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#878787"/></rect>
<rect x="249.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="258.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#c5c5c5"/></rect>
<rect x="267.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9d9d9d"/></rect>
<rect x="276.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#535353"/></rect>
<rect x="285.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4d4d4d"/></rect>
<rect x="294.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#595959"/></rect>
<rect x="303.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#898989"/></rect>
<rect x="312.0" y="189.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#999999"/></rect>
<rect x="33.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#454545"/></rect>
<rect x="42.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#535353"/></rect>
<rect x="51.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#676767"/></rect>
<rect x="60.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#848484"/></rect>
<rect x="69.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#939393"/></rect>
<rect x="78.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#7c7c7c"/></rect>
<rect x="87.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#888888"/></rect>
<rect x="96.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#e0e0e0"/></rect>
<rect x="105.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#ffffff"/></rect>
<rect x="114.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#d5d5d5"/></rect>
<rect x="123.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#9f9f9f"/></rect>
<rect x="132.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#6c6c6c"/></rect>
<rect x="141.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#515151"/></rect>
<rect x="150.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4d4d4d"/></rect>
<rect x="159.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#464646"/></rect>
<rect x="168.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#676767"/></rect>
<rect x="177.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#7b7b7b"/></rect>
<rect x="186.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#828282"/></rect>
<rect x="195.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#585858"/></rect>
<rect x="204.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#252525"/></rect>
<rect x="213.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#4b4b4b"/></rect>
<rect x="222.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#8a8a8a"/></rect>
<rect x="231.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#999999"/></rect>
<rect x="240.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#acacac"/></rect>
<rect x="249.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b8b8b8"/></rect>
<rect x="258.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#aeaeae"/></rect>
<rect x="267.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#919191"/></rect>
<rect x="276.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#5d5d5d"/></rect>
<rect x="285.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#616161"/></rect>
<rect x="294.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#737373"/></rect>
<rect x="303.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#a0a0a0"/></rect>
<rect x="312.0" y="198.0" width="9.3" height="9.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#e5e7eb;#b4b4b4"/></rect>
<rect x="330" y="96" width="294.0" height="114.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="330" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">カバレッジ 0.2</text>
<rect x="333.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="342.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="351.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="360.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="369.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="378.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="387.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="396.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="405.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="414.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="423.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="432.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="459.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="468.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="486.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="495.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="504.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="513.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="522.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="531.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="540.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="549.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="576.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="585.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="594.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="603.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="612.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="333.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="342.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="351.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="360.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="369.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="378.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="387.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="396.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="405.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="414.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="423.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="432.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="459.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="468.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="486.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="495.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="504.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="513.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="522.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="531.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="540.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="549.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="576.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="585.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="594.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="603.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="612.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="333.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="342.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="351.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="360.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="369.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="378.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="387.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="396.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="405.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="414.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="423.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="432.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="459.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="468.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="486.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="495.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="504.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="513.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="522.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="531.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="540.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="549.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="576.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="585.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#7dd3fc;#80d4fc"/></rect>
<rect x="594.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="603.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="612.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="333.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0693" values="#7dd3fc;#93dafd"/></rect>
<rect x="342.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0702" values="#7dd3fc;#88d7fc"/></rect>
<rect x="351.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0711" values="#7dd3fc;#7ed3fc"/></rect>
<rect x="360.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="369.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="378.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="387.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="396.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="405.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="414.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="423.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="432.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="459.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="468.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="486.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="495.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="504.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="513.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="522.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="531.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="540.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="549.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="576.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="585.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="594.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="603.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="612.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="333.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="342.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="351.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="360.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0729" values="#7dd3fc;#97dcfd"/></rect>
<rect x="369.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#7dd3fc;#e5f6fe"/></rect>
<rect x="378.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="387.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="396.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="405.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="414.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="423.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="432.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="459.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="468.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="486.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="495.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="504.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="513.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="522.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="531.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="540.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="549.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="576.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="585.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="594.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="603.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="612.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="333.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0711" values="#7dd3fc;#93dafc"/></rect>
<rect x="342.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#7dd3fc;#8ed9fc"/></rect>
<rect x="351.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0729" values="#7dd3fc;#8ad7fc"/></rect>
<rect x="360.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#7dd3fc;#80d4fc"/></rect>
<rect x="369.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="378.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="387.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="396.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="405.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="414.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="423.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="432.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="459.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="468.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="486.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="495.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="504.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="513.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="522.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="531.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="540.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="549.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="576.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="585.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="594.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="603.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="612.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="333.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#7dd3fc;#b2e5fd"/></rect>
<rect x="342.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0729" values="#7dd3fc;#b0e4fd"/></rect>
<rect x="351.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#7dd3fc;#a9e2fd"/></rect>
<rect x="360.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="369.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="378.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="387.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="396.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="405.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="414.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="423.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="432.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="459.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="468.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="486.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="495.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="504.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="513.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="522.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="531.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="540.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="549.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="576.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="585.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="594.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="603.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="612.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="333.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0729" values="#7dd3fc;#89d7fc"/></rect>
<rect x="342.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="351.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="360.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="369.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="378.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="387.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="396.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="405.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="414.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="423.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="432.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="459.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="468.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="486.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="495.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="504.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="513.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="522.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="531.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="540.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="549.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="576.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="585.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="594.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="603.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="612.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="333.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="342.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="351.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="360.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="369.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="378.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="387.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="396.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="405.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="414.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="423.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="432.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0853" values="#7dd3fc;#8bd8fc"/></rect>
<rect x="459.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="468.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="486.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="495.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="504.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="513.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="522.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="531.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="540.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="549.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="576.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="585.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="594.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="603.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="612.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="333.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="342.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="351.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="360.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="369.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="378.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="387.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="396.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="405.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="414.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="423.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="432.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="459.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="468.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="486.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="495.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="504.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="513.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="522.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="531.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="540.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="549.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="576.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="585.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="594.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="603.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="612.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="333.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#7dd3fc;#7fd4fc"/></rect>
<rect x="342.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="351.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="360.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="369.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="378.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="387.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="396.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="405.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="414.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="423.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="432.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="459.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="468.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="486.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="495.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="504.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="513.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="522.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="531.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="540.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="549.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="576.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="585.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="594.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="603.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="612.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="333.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="342.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="351.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="360.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="369.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="378.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="387.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="396.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="405.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="414.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="423.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="432.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="459.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="468.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="486.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="495.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="504.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#7dd3fc;#99dcfd"/></rect>
<rect x="513.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="522.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="531.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="540.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="549.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="576.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="585.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="594.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="603.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="612.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="640" y="96" width="294.0" height="114.0" fill="#ffffff" stroke="#2ea043" stroke-width="1.8" rx="6"/>
<text x="640" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">カバレッジ 0.5</text>
<rect x="643.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="652.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="661.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="670.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="679.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="688.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="697.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="706.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#7dd3fc;#c5ecfe"/></rect>
<rect x="715.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#7dd3fc;#ffffff"/></rect>
<rect x="724.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#7dd3fc;#d1f0fe"/></rect>
<rect x="733.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="742.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="751.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="760.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="769.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="778.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="787.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="796.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#7dd3fc;#c1eafe"/></rect>
<rect x="805.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="814.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="823.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="832.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="841.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="850.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="859.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="868.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="877.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#7dd3fc;#c0eafe"/></rect>
<rect x="886.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#7dd3fc;#9fdefd"/></rect>
<rect x="895.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#7dd3fc;#ace3fd"/></rect>
<rect x="904.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#7dd3fc;#92dafc"/></rect>
<rect x="913.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#7dd3fc;#caedfe"/></rect>
<rect x="922.0" y="99.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="643.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="652.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="661.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="670.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="679.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="688.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="697.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="706.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#7dd3fc;#9edefd"/></rect>
<rect x="715.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#7dd3fc;#cdeefe"/></rect>
<rect x="724.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#7dd3fc;#d8f2fe"/></rect>
<rect x="733.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="742.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="751.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="760.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="769.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="778.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="787.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="796.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="805.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="814.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="823.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="832.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="841.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="850.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="859.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="868.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="877.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#7dd3fc;#7ed3fc"/></rect>
<rect x="886.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#7dd3fc;#e1f5fe"/></rect>
<rect x="895.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#7dd3fc;#fcfeff"/></rect>
<rect x="904.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#7dd3fc;#d2f0fe"/></rect>
<rect x="913.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#7dd3fc;#8cd8fc"/></rect>
<rect x="922.0" y="108.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="643.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2684" values="#7dd3fc;#f0faff"/></rect>
<rect x="652.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2693" values="#7dd3fc;#eff9ff"/></rect>
<rect x="661.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2702" values="#7dd3fc;#e8f7fe"/></rect>
<rect x="670.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#7dd3fc;#94dbfd"/></rect>
<rect x="679.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="688.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="697.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#7dd3fc;#8bd8fc"/></rect>
<rect x="706.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="715.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="724.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#7dd3fc;#bde9fd"/></rect>
<rect x="733.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#7dd3fc;#85d6fc"/></rect>
<rect x="742.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="751.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="760.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="769.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="778.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="787.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="796.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="805.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="814.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="823.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="832.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="841.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="850.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="859.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="868.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="877.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="886.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#7dd3fc;#fafdff"/></rect>
<rect x="895.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#7dd3fc;#ffffff"/></rect>
<rect x="904.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#7dd3fc;#eaf8ff"/></rect>
<rect x="913.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="922.0" y="117.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="643.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2693" values="#7dd3fc;#ffffff"/></rect>
<rect x="652.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2702" values="#7dd3fc;#ffffff"/></rect>
<rect x="661.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#7dd3fc;#ffffff"/></rect>
<rect x="670.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2720" values="#7dd3fc;#ebf8ff"/></rect>
<rect x="679.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#7dd3fc;#d0effe"/></rect>
<rect x="688.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#7dd3fc;#f1faff"/></rect>
<rect x="697.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#7dd3fc;#daf3fe"/></rect>
<rect x="706.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="715.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="724.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="733.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="742.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="751.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="760.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="769.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="778.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="787.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="796.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="805.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="814.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#7dd3fc;#cbedfe"/></rect>
<rect x="823.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#7dd3fc;#98dcfd"/></rect>
<rect x="832.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="841.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="850.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="859.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="868.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="877.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="886.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#7dd3fc;#b0e4fd"/></rect>
<rect x="895.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#7dd3fc;#bbe8fd"/></rect>
<rect x="904.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#7dd3fc;#93dafd"/></rect>
<rect x="913.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="922.0" y="126.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="643.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2702" values="#7dd3fc;#cceefe"/></rect>
<rect x="652.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#7dd3fc;#bae8fd"/></rect>
<rect x="661.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2720" values="#7dd3fc;#aee3fd"/></rect>
<rect x="670.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#7dd3fc;#ffffff"/></rect>
<rect x="679.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#7dd3fc;#ffffff"/></rect>
<rect x="688.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#7dd3fc;#c5ebfe"/></rect>
<rect x="697.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="706.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="715.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="724.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="733.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="742.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="751.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="760.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#7dd3fc;#a0dffd"/></rect>
<rect x="769.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="778.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="787.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="796.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="805.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="814.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="823.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="832.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#7dd3fc;#83d5fc"/></rect>
<rect x="841.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="850.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="859.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="868.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="877.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="886.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="895.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="904.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="913.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="922.0" y="135.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="643.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#7dd3fc;#ffffff"/></rect>
<rect x="652.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2720" values="#7dd3fc;#ffffff"/></rect>
<rect x="661.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#7dd3fc;#ffffff"/></rect>
<rect x="670.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#7dd3fc;#ffffff"/></rect>
<rect x="679.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#7dd3fc;#ffffff"/></rect>
<rect x="688.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#7dd3fc;#cbedfe"/></rect>
<rect x="697.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="706.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="715.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="724.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="733.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="742.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="751.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="760.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="769.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="778.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="787.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="796.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="805.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="814.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="823.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="832.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="841.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="850.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="859.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="868.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="877.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="886.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#7dd3fc;#82d5fc"/></rect>
<rect x="895.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2960" values="#7dd3fc;#90d9fc"/></rect>
<rect x="904.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="913.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="922.0" y="144.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="643.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2720" values="#7dd3fc;#ffffff"/></rect>
<rect x="652.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#7dd3fc;#ffffff"/></rect>
<rect x="661.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#7dd3fc;#ffffff"/></rect>
<rect x="670.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#7dd3fc;#f4fbff"/></rect>
<rect x="679.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#7dd3fc;#c2eafe"/></rect>
<rect x="688.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#7dd3fc;#bae8fd"/></rect>
<rect x="697.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#7dd3fc;#8ed9fc"/></rect>
<rect x="706.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="715.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="724.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="733.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#7dd3fc;#a1dffd"/></rect>
<rect x="742.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="751.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="760.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#7dd3fc;#83d5fc"/></rect>
<rect x="769.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#7dd3fc;#a6e1fd"/></rect>
<rect x="778.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="787.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="796.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="805.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="814.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="823.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="832.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="841.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="850.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="859.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="868.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="877.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="886.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2960" values="#7dd3fc;#c2eafe"/></rect>
<rect x="895.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2969" values="#7dd3fc;#d2f0fe"/></rect>
<rect x="904.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#7dd3fc;#bfe9fe"/></rect>
<rect x="913.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="922.0" y="153.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="643.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#7dd3fc;#ffffff"/></rect>
<rect x="652.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#7dd3fc;#ffffff"/></rect>
<rect x="661.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#7dd3fc;#f6fcff"/></rect>
<rect x="670.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#7dd3fc;#c0eafe"/></rect>
<rect x="679.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#7dd3fc;#a3e0fd"/></rect>
<rect x="688.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#7dd3fc;#d1effe"/></rect>
<rect x="697.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#7dd3fc;#c5ebfe"/></rect>
<rect x="706.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="715.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="724.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="733.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#7dd3fc;#82d5fc"/></rect>
<rect x="742.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#7dd3fc;#ade3fd"/></rect>
<rect x="751.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#7dd3fc;#cdeefe"/></rect>
<rect x="760.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#7dd3fc;#c3ebfe"/></rect>
<rect x="769.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#7dd3fc;#a4e0fd"/></rect>
<rect x="778.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="787.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="796.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="805.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="814.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="823.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="832.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="841.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="850.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="859.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="868.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="877.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="886.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2969" values="#7dd3fc;#b5e6fd"/></rect>
<rect x="895.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#7dd3fc;#aee3fd"/></rect>
<rect x="904.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2987" values="#7dd3fc;#a8e1fd"/></rect>
<rect x="913.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2996" values="#7dd3fc;#8bd8fc"/></rect>
<rect x="922.0" y="162.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3004" values="#7dd3fc;#a3e0fd"/></rect>
<rect x="643.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#7dd3fc;#a4e0fd"/></rect>
<rect x="652.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#7dd3fc;#8bd8fc"/></rect>
<rect x="661.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="670.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#7dd3fc;#cbeefe"/></rect>
<rect x="679.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#7dd3fc;#ffffff"/></rect>
<rect x="688.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="697.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="706.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="715.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="724.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="733.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#7dd3fc;#93dafd"/></rect>
<rect x="742.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#7dd3fc;#afe4fd"/></rect>
<rect x="751.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#7dd3fc;#e7f7fe"/></rect>
<rect x="760.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#7dd3fc;#ffffff"/></rect>
<rect x="769.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="778.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="787.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="796.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="805.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="814.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="823.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="832.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="841.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="850.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="859.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="868.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="877.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2969" values="#7dd3fc;#8dd9fc"/></rect>
<rect x="886.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="895.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="904.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="913.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3004" values="#7dd3fc;#f7fcff"/></rect>
<rect x="922.0" y="171.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3013" values="#7dd3fc;#ffffff"/></rect>
<rect x="643.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#7dd3fc;#ffffff"/></rect>
<rect x="652.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#7dd3fc;#ffffff"/></rect>
<rect x="661.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#7dd3fc;#f2fbff"/></rect>
<rect x="670.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#7dd3fc;#bae8fd"/></rect>
<rect x="679.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#7dd3fc;#98dcfd"/></rect>
<rect x="688.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="697.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="706.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="715.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="724.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="733.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#7dd3fc;#b8e7fd"/></rect>
<rect x="742.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#7dd3fc;#9bddfd"/></rect>
<rect x="751.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#7dd3fc;#bfe9fe"/></rect>
<rect x="760.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#7dd3fc;#def4fe"/></rect>
<rect x="769.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#7dd3fc;#c0eafe"/></rect>
<rect x="778.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="787.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="796.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="805.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="814.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="823.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="832.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="841.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="850.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="859.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="868.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="877.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="886.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2987" values="#7dd3fc;#bbe8fd"/></rect>
<rect x="895.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2996" values="#7dd3fc;#c2eafe"/></rect>
<rect x="904.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3004" values="#7dd3fc;#c1eafe"/></rect>
<rect x="913.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3013" values="#7dd3fc;#a4e0fd"/></rect>
<rect x="922.0" y="180.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3022" values="#7dd3fc;#a2dffd"/></rect>
<rect x="643.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#7dd3fc;#ffffff"/></rect>
<rect x="652.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#7dd3fc;#ffffff"/></rect>
<rect x="661.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#7dd3fc;#f8fdff"/></rect>
<rect x="670.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#7dd3fc;#9ddefd"/></rect>
<rect x="679.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="688.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="697.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="706.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="715.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="724.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="733.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#7dd3fc;#9addfd"/></rect>
<rect x="742.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#7dd3fc;#91dafc"/></rect>
<rect x="751.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#7dd3fc;#b7e7fd"/></rect>
<rect x="760.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#7dd3fc;#d1f0fe"/></rect>
<rect x="769.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#7dd3fc;#f6fcff"/></rect>
<rect x="778.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#7dd3fc;#aee4fd"/></rect>
<rect x="787.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="796.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="805.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="814.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#7dd3fc;#8ed9fc"/></rect>
<rect x="823.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="832.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="841.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="850.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="859.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="868.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="877.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="886.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2996" values="#7dd3fc;#d9f2fe"/></rect>
<rect x="895.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3004" values="#7dd3fc;#e3f6fe"/></rect>
<rect x="904.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3013" values="#7dd3fc;#cceefe"/></rect>
<rect x="913.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="922.0" y="189.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="643.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#7dd3fc;#f4fbff"/></rect>
<rect x="652.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#7dd3fc;#d8f2fe"/></rect>
<rect x="661.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#7dd3fc;#afe4fd"/></rect>
<rect x="670.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="679.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="688.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#7dd3fc;#85d6fc"/></rect>
<rect x="697.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="706.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="715.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="724.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="733.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="742.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#7dd3fc;#a5e1fd"/></rect>
<rect x="751.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#7dd3fc;#dcf3fe"/></rect>
<rect x="760.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#7dd3fc;#e5f6fe"/></rect>
<rect x="769.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#7dd3fc;#f2fbff"/></rect>
<rect x="778.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#7dd3fc;#b0e4fd"/></rect>
<rect x="787.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#7dd3fc;#86d6fc"/></rect>
<rect x="796.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="805.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#7dd3fc;#ceeefe"/></rect>
<rect x="814.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#7dd3fc;#ffffff"/></rect>
<rect x="823.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#7dd3fc;#e7f7fe"/></rect>
<rect x="832.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="841.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="850.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="859.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="868.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="877.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="886.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3004" values="#7dd3fc;#c2eafe"/></rect>
<rect x="895.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3013" values="#7dd3fc;#bbe8fd"/></rect>
<rect x="904.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3022" values="#7dd3fc;#96dcfd"/></rect>
<rect x="913.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="922.0" y="198.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="330" y="230" width="294.0" height="114.0" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="330" y="220" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">カバレッジ 0.8</text>
<rect x="333.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="342.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="351.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="360.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4693" values="#7dd3fc;#a6e1fd"/></rect>
<rect x="369.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#7dd3fc;#eef9ff"/></rect>
<rect x="378.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4711" values="#7dd3fc;#7fd4fc"/></rect>
<rect x="387.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#7dd3fc;#aae2fd"/></rect>
<rect x="396.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#7dd3fc;#ffffff"/></rect>
<rect x="405.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#7dd3fc;#ffffff"/></rect>
<rect x="414.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#7dd3fc;#ffffff"/></rect>
<rect x="423.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#7dd3fc;#e6f7fe"/></rect>
<rect x="432.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#7dd3fc;#c1eafe"/></rect>
<rect x="459.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="468.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#7dd3fc;#d0effe"/></rect>
<rect x="486.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#7dd3fc;#ffffff"/></rect>
<rect x="495.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#7dd3fc;#f2fbff"/></rect>
<rect x="504.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="513.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#7dd3fc;#8dd9fc"/></rect>
<rect x="522.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#7dd3fc;#b6e6fd"/></rect>
<rect x="531.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#7dd3fc;#a1dffd"/></rect>
<rect x="540.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#7dd3fc;#8cd8fc"/></rect>
<rect x="549.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#7dd3fc;#93dafd"/></rect>
<rect x="567.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#7dd3fc;#ffffff"/></rect>
<rect x="576.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#7dd3fc;#ffffff"/></rect>
<rect x="585.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#7dd3fc;#ffffff"/></rect>
<rect x="594.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#7dd3fc;#ffffff"/></rect>
<rect x="603.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#7dd3fc;#ffffff"/></rect>
<rect x="612.0" y="233.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#7dd3fc;#f3fbff"/></rect>
<rect x="333.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4676" values="#7dd3fc;#edf9ff"/></rect>
<rect x="342.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4684" values="#7dd3fc;#def4fe"/></rect>
<rect x="351.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4693" values="#7dd3fc;#c8ecfe"/></rect>
<rect x="360.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#7dd3fc;#cfeffe"/></rect>
<rect x="369.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4711" values="#7dd3fc;#d3f0fe"/></rect>
<rect x="378.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#7dd3fc;#b3e5fd"/></rect>
<rect x="387.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#7dd3fc;#e8f7fe"/></rect>
<rect x="396.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#7dd3fc;#ffffff"/></rect>
<rect x="405.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#7dd3fc;#ffffff"/></rect>
<rect x="414.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#7dd3fc;#ffffff"/></rect>
<rect x="423.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#7dd3fc;#ffffff"/></rect>
<rect x="432.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#7dd3fc;#9cdefd"/></rect>
<rect x="459.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#7dd3fc;#b4e6fd"/></rect>
<rect x="468.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#7dd3fc;#cdeefe"/></rect>
<rect x="477.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#7dd3fc;#e9f7fe"/></rect>
<rect x="486.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#7dd3fc;#ffffff"/></rect>
<rect x="495.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#7dd3fc;#e0f5fe"/></rect>
<rect x="504.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#7dd3fc;#ace3fd"/></rect>
<rect x="513.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#7dd3fc;#ace3fd"/></rect>
<rect x="522.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#7dd3fc;#9bddfd"/></rect>
<rect x="531.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#7dd3fc;#b1e5fd"/></rect>
<rect x="540.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#7dd3fc;#b8e7fd"/></rect>
<rect x="549.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#7dd3fc;#ffffff"/></rect>
<rect x="576.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#7dd3fc;#ffffff"/></rect>
<rect x="585.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#7dd3fc;#ffffff"/></rect>
<rect x="594.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#7dd3fc;#ffffff"/></rect>
<rect x="603.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#7dd3fc;#ffffff"/></rect>
<rect x="612.0" y="242.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#7dd3fc;#b9e7fd"/></rect>
<rect x="333.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4684" values="#7dd3fc;#ffffff"/></rect>
<rect x="342.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4693" values="#7dd3fc;#ffffff"/></rect>
<rect x="351.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#7dd3fc;#ffffff"/></rect>
<rect x="360.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4711" values="#7dd3fc;#ffffff"/></rect>
<rect x="369.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#7dd3fc;#fcfeff"/></rect>
<rect x="378.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#7dd3fc;#ffffff"/></rect>
<rect x="387.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#7dd3fc;#ffffff"/></rect>
<rect x="396.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#7dd3fc;#fcfeff"/></rect>
<rect x="405.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#7dd3fc;#ffffff"/></rect>
<rect x="414.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#7dd3fc;#ffffff"/></rect>
<rect x="423.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#7dd3fc;#ffffff"/></rect>
<rect x="432.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="441.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="450.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#7dd3fc;#97dcfd"/></rect>
<rect x="459.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#7dd3fc;#ffffff"/></rect>
<rect x="468.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#7dd3fc;#ffffff"/></rect>
<rect x="477.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#7dd3fc;#e4f6fe"/></rect>
<rect x="486.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#7dd3fc;#a7e1fd"/></rect>
<rect x="495.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#7dd3fc;#d3f0fe"/></rect>
<rect x="504.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#7dd3fc;#ffffff"/></rect>
<rect x="513.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#7dd3fc;#e3f5fe"/></rect>
<rect x="522.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#7dd3fc;#9bddfd"/></rect>
<rect x="531.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#7dd3fc;#c7ecfe"/></rect>
<rect x="540.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#7dd3fc;#d9f2fe"/></rect>
<rect x="549.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#7dd3fc;#cceefe"/></rect>
<rect x="576.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#7dd3fc;#ffffff"/></rect>
<rect x="585.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#7dd3fc;#ffffff"/></rect>
<rect x="594.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#7dd3fc;#ffffff"/></rect>
<rect x="603.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#7dd3fc;#e0f4fe"/></rect>
<rect x="612.0" y="251.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#7dd3fc;#81d4fc"/></rect>
<rect x="333.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4693" values="#7dd3fc;#ffffff"/></rect>
<rect x="342.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#7dd3fc;#ffffff"/></rect>
<rect x="351.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4711" values="#7dd3fc;#ffffff"/></rect>
<rect x="360.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#7dd3fc;#ffffff"/></rect>
<rect x="369.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#7dd3fc;#ffffff"/></rect>
<rect x="378.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#7dd3fc;#ffffff"/></rect>
<rect x="387.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#7dd3fc;#ffffff"/></rect>
<rect x="396.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#7dd3fc;#def4fe"/></rect>
<rect x="405.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#7dd3fc;#aee4fd"/></rect>
<rect x="414.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#7dd3fc;#e8f7fe"/></rect>
<rect x="423.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#7dd3fc;#e3f6fe"/></rect>
<rect x="432.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#7dd3fc;#b7e7fd"/></rect>
<rect x="441.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#7dd3fc;#b8e7fd"/></rect>
<rect x="450.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#7dd3fc;#d0effe"/></rect>
<rect x="459.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#7dd3fc;#fafdff"/></rect>
<rect x="468.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#7dd3fc;#caedfe"/></rect>
<rect x="477.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#7dd3fc;#9edefd"/></rect>
<rect x="486.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#7dd3fc;#8ed9fc"/></rect>
<rect x="495.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#7dd3fc;#f4fbff"/></rect>
<rect x="504.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#7dd3fc;#ffffff"/></rect>
<rect x="513.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#7dd3fc;#ffffff"/></rect>
<rect x="522.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#7dd3fc;#c0eafe"/></rect>
<rect x="531.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#7dd3fc;#ade3fd"/></rect>
<rect x="540.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#7dd3fc;#8bd8fc"/></rect>
<rect x="549.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#7dd3fc;#bae8fd"/></rect>
<rect x="576.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#7dd3fc;#ffffff"/></rect>
<rect x="585.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#7dd3fc;#ffffff"/></rect>
<rect x="594.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#7dd3fc;#ffffff"/></rect>
<rect x="603.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#7dd3fc;#bee9fe"/></rect>
<rect x="612.0" y="260.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#7dd3fc;#87d6fc"/></rect>
<rect x="333.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#7dd3fc;#ffffff"/></rect>
<rect x="342.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4711" values="#7dd3fc;#ffffff"/></rect>
<rect x="351.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#7dd3fc;#ffffff"/></rect>
<rect x="360.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#7dd3fc;#ffffff"/></rect>
<rect x="369.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#7dd3fc;#ffffff"/></rect>
<rect x="378.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#7dd3fc;#ffffff"/></rect>
<rect x="387.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#7dd3fc;#d9f2fe"/></rect>
<rect x="396.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#7dd3fc;#d7f1fe"/></rect>
<rect x="405.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#7dd3fc;#d0effe"/></rect>
<rect x="414.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#7dd3fc;#d0effe"/></rect>
<rect x="423.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#7dd3fc;#d0effe"/></rect>
<rect x="432.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#7dd3fc;#bde8fd"/></rect>
<rect x="441.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#7dd3fc;#def4fe"/></rect>
<rect x="450.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#7dd3fc;#ffffff"/></rect>
<rect x="459.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="468.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="486.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#7dd3fc;#ffffff"/></rect>
<rect x="495.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#7dd3fc;#f8fdff"/></rect>
<rect x="504.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#7dd3fc;#c3ebfe"/></rect>
<rect x="513.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#7dd3fc;#ffffff"/></rect>
<rect x="522.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#7dd3fc;#ffffff"/></rect>
<rect x="531.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#7dd3fc;#cceefe"/></rect>
<rect x="540.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="549.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#7dd3fc;#ecf8ff"/></rect>
<rect x="576.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#7dd3fc;#abe2fd"/></rect>
<rect x="585.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#7dd3fc;#a7e1fd"/></rect>
<rect x="594.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#7dd3fc;#a5e1fd"/></rect>
<rect x="603.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#7dd3fc;#ffffff"/></rect>
<rect x="612.0" y="269.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4978" values="#7dd3fc;#d1effe"/></rect>
<rect x="333.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4711" values="#7dd3fc;#ffffff"/></rect>
<rect x="342.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#7dd3fc;#ffffff"/></rect>
<rect x="351.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#7dd3fc;#ffffff"/></rect>
<rect x="360.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#7dd3fc;#ffffff"/></rect>
<rect x="369.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#7dd3fc;#ffffff"/></rect>
<rect x="378.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#7dd3fc;#ffffff"/></rect>
<rect x="387.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#7dd3fc;#ffffff"/></rect>
<rect x="396.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#7dd3fc;#c0eafe"/></rect>
<rect x="405.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#7dd3fc;#a8e2fd"/></rect>
<rect x="414.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#7dd3fc;#fdfeff"/></rect>
<rect x="423.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#7dd3fc;#ffffff"/></rect>
<rect x="432.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#7dd3fc;#c7ecfe"/></rect>
<rect x="441.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#7dd3fc;#d7f2fe"/></rect>
<rect x="450.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#7dd3fc;#ffffff"/></rect>
<rect x="459.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#7dd3fc;#f0faff"/></rect>
<rect x="468.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#7dd3fc;#aee4fd"/></rect>
<rect x="477.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#7dd3fc;#8ed9fc"/></rect>
<rect x="486.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#7dd3fc;#a7e1fd"/></rect>
<rect x="495.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#7dd3fc;#d3f0fe"/></rect>
<rect x="504.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#7dd3fc;#f6fcff"/></rect>
<rect x="513.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#7dd3fc;#ffffff"/></rect>
<rect x="522.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#7dd3fc;#d5f1fe"/></rect>
<rect x="531.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#7dd3fc;#d2f0fe"/></rect>
<rect x="540.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#7dd3fc;#bde9fd"/></rect>
<rect x="549.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#7dd3fc;#bce8fd"/></rect>
<rect x="576.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#7dd3fc;#ffffff"/></rect>
<rect x="585.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#7dd3fc;#ffffff"/></rect>
<rect x="594.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#7dd3fc;#ffffff"/></rect>
<rect x="603.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4978" values="#7dd3fc;#e8f7fe"/></rect>
<rect x="612.0" y="278.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4987" values="#7dd3fc;#b3e5fd"/></rect>
<rect x="333.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#7dd3fc;#ffffff"/></rect>
<rect x="342.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#7dd3fc;#ffffff"/></rect>
<rect x="351.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#7dd3fc;#ffffff"/></rect>
<rect x="360.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#7dd3fc;#ffffff"/></rect>
<rect x="369.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#7dd3fc;#ffffff"/></rect>
<rect x="378.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#7dd3fc;#ffffff"/></rect>
<rect x="387.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#7dd3fc;#ffffff"/></rect>
<rect x="396.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#7dd3fc;#b4e6fd"/></rect>
<rect x="405.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#7dd3fc;#97dcfd"/></rect>
<rect x="414.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#7dd3fc;#ffffff"/></rect>
<rect x="423.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#7dd3fc;#ffffff"/></rect>
<rect x="432.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#7dd3fc;#f5fcff"/></rect>
<rect x="441.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#7dd3fc;#ffffff"/></rect>
<rect x="450.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#7dd3fc;#ffffff"/></rect>
<rect x="459.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#7dd3fc;#ffffff"/></rect>
<rect x="468.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#7dd3fc;#f4fbff"/></rect>
<rect x="477.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#7dd3fc;#a6e1fd"/></rect>
<rect x="486.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="495.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#7dd3fc;#ade3fd"/></rect>
<rect x="504.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#7dd3fc;#edf9ff"/></rect>
<rect x="513.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#7dd3fc;#d1effe"/></rect>
<rect x="522.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#7dd3fc;#8ed9fc"/></rect>
<rect x="531.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#7dd3fc;#c8ecfe"/></rect>
<rect x="540.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#7dd3fc;#e8f7fe"/></rect>
<rect x="549.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="558.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="567.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#7dd3fc;#b9e7fd"/></rect>
<rect x="576.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#7dd3fc;#ffffff"/></rect>
<rect x="585.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#7dd3fc;#ffffff"/></rect>
<rect x="594.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4978" values="#7dd3fc;#ffffff"/></rect>
<rect x="603.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4987" values="#7dd3fc;#fbfdff"/></rect>
<rect x="612.0" y="287.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996" values="#7dd3fc;#e1f5fe"/></rect>
<rect x="333.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#7dd3fc;#ffffff"/></rect>
<rect x="342.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#7dd3fc;#ffffff"/></rect>
<rect x="351.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#7dd3fc;#ffffff"/></rect>
<rect x="360.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#7dd3fc;#ffffff"/></rect>
<rect x="369.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#7dd3fc;#ffffff"/></rect>
<rect x="378.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#7dd3fc;#ffffff"/></rect>
<rect x="387.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#7dd3fc;#ffffff"/></rect>
<rect x="396.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#7dd3fc;#c6ecfe"/></rect>
<rect x="405.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#7dd3fc;#93dafd"/></rect>
<rect x="414.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#7dd3fc;#dff4fe"/></rect>
<rect x="423.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#7dd3fc;#ffffff"/></rect>
<rect x="432.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#7dd3fc;#ffffff"/></rect>
<rect x="441.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#7dd3fc;#ffffff"/></rect>
<rect x="450.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#7dd3fc;#ffffff"/></rect>
<rect x="459.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#7dd3fc;#ffffff"/></rect>
<rect x="468.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#7dd3fc;#cceefe"/></rect>
<rect x="477.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#7dd3fc;#87d6fc"/></rect>
<rect x="486.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="495.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#7dd3fc;#b3e5fd"/></rect>
<rect x="504.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#7dd3fc;#ffffff"/></rect>
<rect x="513.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#7dd3fc;#bbe8fd"/></rect>
<rect x="522.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="531.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#7dd3fc;#8ed9fc"/></rect>
<rect x="540.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#7dd3fc;#afe4fd"/></rect>
<rect x="549.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#7dd3fc;#a8e1fd"/></rect>
<rect x="558.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#7dd3fc;#afe4fd"/></rect>
<rect x="567.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#7dd3fc;#e7f7fe"/></rect>
<rect x="576.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#7dd3fc;#ffffff"/></rect>
<rect x="585.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4978" values="#7dd3fc;#ffffff"/></rect>
<rect x="594.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4987" values="#7dd3fc;#ffffff"/></rect>
<rect x="603.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996" values="#7dd3fc;#ffffff"/></rect>
<rect x="612.0" y="296.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5004" values="#7dd3fc;#ffffff"/></rect>
<rect x="333.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#7dd3fc;#ffffff"/></rect>
<rect x="342.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#7dd3fc;#ffffff"/></rect>
<rect x="351.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#7dd3fc;#ffffff"/></rect>
<rect x="360.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#7dd3fc;#ffffff"/></rect>
<rect x="369.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#7dd3fc;#ffffff"/></rect>
<rect x="378.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#7dd3fc;#ffffff"/></rect>
<rect x="387.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#7dd3fc;#aee3fd"/></rect>
<rect x="396.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#7dd3fc;#cceefe"/></rect>
<rect x="405.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#7dd3fc;#d5f1fe"/></rect>
<rect x="414.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#7dd3fc;#f8fdff"/></rect>
<rect x="423.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#7dd3fc;#ffffff"/></rect>
<rect x="432.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#7dd3fc;#ffffff"/></rect>
<rect x="441.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#7dd3fc;#ffffff"/></rect>
<rect x="450.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#7dd3fc;#ffffff"/></rect>
<rect x="459.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#7dd3fc;#d3f0fe"/></rect>
<rect x="468.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="477.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="486.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#7dd3fc;#e3f5fe"/></rect>
<rect x="495.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#7dd3fc;#9edefd"/></rect>
<rect x="504.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="513.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="522.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#7dd3fc;#94dbfd"/></rect>
<rect x="531.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#7dd3fc;#abe3fd"/></rect>
<rect x="540.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#7dd3fc;#c1eafe"/></rect>
<rect x="549.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#7dd3fc;#ace3fd"/></rect>
<rect x="558.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#7dd3fc;#abe3fd"/></rect>
<rect x="567.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#7dd3fc;#ffffff"/></rect>
<rect x="576.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4978" values="#7dd3fc;#def4fe"/></rect>
<rect x="585.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4987" values="#7dd3fc;#d0effe"/></rect>
<rect x="594.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996" values="#7dd3fc;#eff9ff"/></rect>
<rect x="603.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5004" values="#7dd3fc;#ffffff"/></rect>
<rect x="612.0" y="305.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5013" values="#7dd3fc;#ffffff"/></rect>
<rect x="333.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4747" values="#7dd3fc;#ffffff"/></rect>
<rect x="342.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#7dd3fc;#ffffff"/></rect>
<rect x="351.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#7dd3fc;#ffffff"/></rect>
<rect x="360.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#7dd3fc;#ffffff"/></rect>
<rect x="369.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#7dd3fc;#ffffff"/></rect>
<rect x="378.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#7dd3fc;#ffffff"/></rect>
<rect x="387.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#7dd3fc;#e5f6fe"/></rect>
<rect x="396.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#7dd3fc;#9fdefd"/></rect>
<rect x="405.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#7dd3fc;#91dafc"/></rect>
<rect x="414.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#7dd3fc;#ffffff"/></rect>
<rect x="423.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#7dd3fc;#ffffff"/></rect>
<rect x="432.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#7dd3fc;#ffffff"/></rect>
<rect x="441.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#7dd3fc;#ffffff"/></rect>
<rect x="450.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#7dd3fc;#ffffff"/></rect>
<rect x="459.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#7dd3fc;#ffffff"/></rect>
<rect x="468.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#7dd3fc;#fafdff"/></rect>
<rect x="477.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#7dd3fc;#b8e7fd"/></rect>
<rect x="486.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#7dd3fc;#9edefd"/></rect>
<rect x="495.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#7dd3fc;#a8e2fd"/></rect>
<rect x="504.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#7dd3fc;#ade3fd"/></rect>
<rect x="513.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#7dd3fc;#9addfd"/></rect>
<rect x="522.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="531.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#7dd3fc;#cbedfe"/></rect>
<rect x="540.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#7dd3fc;#ffffff"/></rect>
<rect x="549.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#7dd3fc;#afe4fd"/></rect>
<rect x="558.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#7dd3fc;#8dd9fc"/></rect>
<rect x="567.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4978" values="#7dd3fc;#eaf8ff"/></rect>
<rect x="576.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4987" values="#7dd3fc;#ffffff"/></rect>
<rect x="585.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996" values="#7dd3fc;#ffffff"/></rect>
<rect x="594.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5004" values="#7dd3fc;#ffffff"/></rect>
<rect x="603.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5013" values="#7dd3fc;#ffffff"/></rect>
<rect x="612.0" y="314.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#7dd3fc;#ffffff"/></rect>
<rect x="333.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#7dd3fc;#ffffff"/></rect>
<rect x="342.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#7dd3fc;#ffffff"/></rect>
<rect x="351.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#7dd3fc;#ffffff"/></rect>
<rect x="360.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#7dd3fc;#ffffff"/></rect>
<rect x="369.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#7dd3fc;#ffffff"/></rect>
<rect x="378.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#7dd3fc;#ffffff"/></rect>
<rect x="387.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#7dd3fc;#e3f5fe"/></rect>
<rect x="396.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="405.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="414.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#7dd3fc;#ddf4fe"/></rect>
<rect x="423.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#7dd3fc;#ffffff"/></rect>
<rect x="432.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#7dd3fc;#ffffff"/></rect>
<rect x="441.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#7dd3fc;#ffffff"/></rect>
<rect x="450.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#7dd3fc;#ffffff"/></rect>
<rect x="459.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#7dd3fc;#ffffff"/></rect>
<rect x="468.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#7dd3fc;#ffffff"/></rect>
<rect x="477.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#7dd3fc;#ffffff"/></rect>
<rect x="486.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#7dd3fc;#caedfe"/></rect>
<rect x="495.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#7dd3fc;#f7fcff"/></rect>
<rect x="504.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#7dd3fc;#ffffff"/></rect>
<rect x="513.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#7dd3fc;#ffffff"/></rect>
<rect x="522.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#7dd3fc;#b8e7fd"/></rect>
<rect x="531.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#7dd3fc;#edf9ff"/></rect>
<rect x="540.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#7dd3fc;#ffffff"/></rect>
<rect x="549.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#7dd3fc;#aae2fd"/></rect>
<rect x="558.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4978" values="#7dd3fc;#8cd8fc"/></rect>
<rect x="567.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4987" values="#7dd3fc;#def4fe"/></rect>
<rect x="576.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996" values="#7dd3fc;#ffffff"/></rect>
<rect x="585.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5004" values="#7dd3fc;#ffffff"/></rect>
<rect x="594.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5013" values="#7dd3fc;#ffffff"/></rect>
<rect x="603.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#7dd3fc;#ffffff"/></rect>
<rect x="612.0" y="323.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5031" values="#7dd3fc;#e6f6fe"/></rect>
<rect x="333.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4764" values="#7dd3fc;#ffffff"/></rect>
<rect x="342.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#7dd3fc;#ffffff"/></rect>
<rect x="351.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#7dd3fc;#ffffff"/></rect>
<rect x="360.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#7dd3fc;#ffffff"/></rect>
<rect x="369.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#7dd3fc;#f1faff"/></rect>
<rect x="378.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#7dd3fc;#ffffff"/></rect>
<rect x="387.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4818" values="#7dd3fc;#ffffff"/></rect>
<rect x="396.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="405.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="414.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"/>
<rect x="423.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4853" values="#7dd3fc;#d9f2fe"/></rect>
<rect x="432.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#7dd3fc;#ffffff"/></rect>
<rect x="441.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4871" values="#7dd3fc;#ffffff"/></rect>
<rect x="450.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#7dd3fc;#ffffff"/></rect>
<rect x="459.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#7dd3fc;#ffffff"/></rect>
<rect x="468.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#7dd3fc;#ffffff"/></rect>
<rect x="477.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#7dd3fc;#ffffff"/></rect>
<rect x="486.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#7dd3fc;#ffffff"/></rect>
<rect x="495.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4924" values="#7dd3fc;#ffffff"/></rect>
<rect x="504.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#7dd3fc;#ffffff"/></rect>
<rect x="513.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#7dd3fc;#ffffff"/></rect>
<rect x="522.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#7dd3fc;#ffffff"/></rect>
<rect x="531.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960" values="#7dd3fc;#e6f6fe"/></rect>
<rect x="540.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#7dd3fc;#bee9fe"/></rect>
<rect x="549.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4978" values="#7dd3fc;#a7e1fd"/></rect>
<rect x="558.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4987" values="#7dd3fc;#bae8fd"/></rect>
<rect x="567.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996" values="#7dd3fc;#f5fcff"/></rect>
<rect x="576.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5004" values="#7dd3fc;#ffffff"/></rect>
<rect x="585.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5013" values="#7dd3fc;#ffffff"/></rect>
<rect x="594.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#7dd3fc;#ffffff"/></rect>
<rect x="603.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5031" values="#7dd3fc;#d8f2fe"/></rect>
<rect x="612.0" y="332.0" width="9.3" height="9.3" fill="#7dd3fc"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5040" values="#7dd3fc;#afe4fd"/></rect>
<text x="40" y="262" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">雲になる画素の割合(%):</text>
<text x="240" y="266" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1056;0.1058;1.0000" values="1;1;0;0"/></text>
<text x="240" y="266" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">3<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1056;0.1058;0.3056;0.3058;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="266" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">35<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3056;0.3058;0.5056;0.5058;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="266" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">89<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5056;0.5058;1.0000" values="0;0;1;1"/></text>
<text x="40" y="300" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">雲の塊の数:</text>
<text x="240" y="304" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1056;0.1058;1.0000" values="1;1;0;0"/></text>
<text x="240" y="304" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2563eb" opacity="0">5<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1056;0.1058;0.3056;0.3058;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="304" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2563eb" opacity="0">12<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3056;0.3058;0.5056;0.5058;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="304" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2563eb" opacity="0">1<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5056;0.5058;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6532;0.6533;1.0000" values="0;0;1;1"/><rect x="330" y="230" width="600" height="90" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="346" y="254" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">カバレッジを上げると、雲の割合が、3% → 35% → 89% と増え、塊が、つながる(塊の数 5 → 12 → 1)</text>
<text x="346" y="277" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">濃さ = (ノイズ − (1 − カバレッジ)) ÷ 幅 を 0〜1 に切る。カバレッジは、天気で動かす</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">同じノイズから、雲の量を、1 つのつまみで決める<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">しきい値より大きい所だけが、雲になる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.6665;0.6667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">天気の遷移は、カバレッジを動かすだけ<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6665;0.6667;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:cloud-coverage:end -->

## 密度のモデル
<strong>雲の密度は複数の要素を掛け合わせて作ります</strong>。

| 要素 | 役割 |
| --- | --- |
| <strong>天気マップ（2D）</strong> | どこに雲があるか（被覆率）・どんな種類か |
| <strong>高さの形（ゲイン）</strong> | 層の下と上で薄くなる（雲の底は平ら、頂は丸い） |
| 基本形の 3D ノイズ | 雲全体の大まかな塊（低周波。Perlin–Worley） |
| ディテールの 3D ノイズ | 塊の縁の細かい凹凸（高周波。Worley） |
| 風の流れ | ノイズの座標を時間で動かす |

```hlsl
float CloudDensity(float3 position, float height_fraction) {
  float coverage = weather_map.SampleLevel(linear_wrap, position.xz * weather_scale, 0).r;
  float height_gradient = saturate(Remap(height_fraction, 0.0, 0.1, 0.0, 1.0))
                        * saturate(Remap(height_fraction, 0.6, 1.0, 1.0, 0.0));

  float3 shape_uvw = position * shape_scale + wind * time;
  float4 noise = shape_noise.SampleLevel(linear_wrap, shape_uvw, 0);
  float shape_fbm = dot(noise.gba, float3(0.5, 0.25, 0.125)) ;
  float base = Remap(noise.r, shape_fbm - 1.0, 1.0, 0.0, 1.0);

  float density = Remap(base * height_gradient, 1.0 - coverage, 1.0, 0.0, 1.0) * coverage;

  if (density > 0.0) {
    float3 detail_uvw = position * detail_scale + wind * time * 2.0;
    float3 detail = detail_noise.SampleLevel(linear_wrap, detail_uvw, 0).rgb;
    float detail_fbm = dot(detail, float3(0.5, 0.25, 0.125));
    float detail_mix = lerp(detail_fbm, 1.0 - detail_fbm, saturate(height_fraction * 5.0));
    density = Remap(density, detail_mix * detail_strength, 1.0, 0.0, 1.0);
  }
  return max(density, 0.0);
}

float Remap(float v, float a, float b, float c, float d) {
  return c + (v - a) / (b - a) * (d - c);
}
```

| 点 | 説明 |
| --- | --- |
| `Remap` | 値の範囲を変換する道具。閾値で塊を切り出すのに便利 |
| `height_fraction` | 層の下端を 0、上端を 1 とした位置 |
| `height_gradient` | 下と上で薄くなる山型（底が柔らかく、頂が丸く） |
| <strong>被覆率（coverage）</strong> | 大きいほど雲が多い |
| ディテールは密度がある所だけ | `if (density > 0)` で計算を省く |
| 3D ノイズは事前生成 | 128³ と 32³ のテクスチャ（Perlin と Worley を重ねる） |

<strong>ノイズ テクスチャ</strong>は<strong>事前に生成</strong>します（Perlin ノイズに Worley ノイズを重ね、4 チャンネルに異なる周波数を入れる）。

## 雲の、密度を、どう作るか

<strong>ボリューム レンダリング</strong>で、雲を描くには、<strong>空間の、各点での、雲の密度</strong>（どれだけ、濃いか）が、必要です。3D の、密度の、データを、そのまま、持つ（ボクセル）と、巨大になるので、ノイズ テクスチャを、組み合わせて、実行時に、密度を、作ります（Schneider と Vos、2015）。

| 材料 | 内容 |
| --- | --- |
| 天気マップ（2D） | どこに、雲があるか（カバレッジ）、どんな種類か。大きなスケールの、配置 |
| 基本の形（3D ノイズ、低周波） | 雲の、大きな、もこもこの形 |
| 細部（3D ノイズ、高周波） | 雲の縁の、細かい、ちぎれ・渦 |
| 高さの、グラデーション | 雲の種類ごとの、高さ方向の、密度の、山 |

## 密度を、組み立てる、手順

<strong>5 つの手順</strong>で、密度が、決まります。<strong>1 つずつ、コード</strong>を、追います。

### ① 天気マップから、カバレッジと、種類を読む

```hlsl
// 天気マップ: R = 雲の量（カバレッジ）、G = 雨の確率、B = 雲の種類（0 = 層雲、0.5 = 積雲、1 = 積乱雲）。
float3 weather = g_weather_map.SampleLevel(g_linear_wrap, position.xz * g_weather_scale, 0).rgb;
float coverage = weather.r;
float cloud_type = weather.b;
```

<strong>天気マップ</strong>は、<strong>空を、真上から見た、2D の画像</strong>です。どこに、雲があるか（R）、どんな種類か（B）を、画素ごとに、決めるので、アーティストが、空の、雲の配置を、描けます。位置（`position.xz`）から、UV を、作って、読みます。

### ② 高さの、グラデーション

```hlsl
// 雲の層の中での、高さの割合（0 = 底、1 = 上端）。
float height_fraction = (length(position) - g_cloud_bottom_radius) / (g_cloud_top_radius - g_cloud_bottom_radius);
float gradient = HeightGradient(height_fraction, cloud_type);        // 種類ごとの、高さ方向の、密度の山
```

雲の、<strong>層</strong>（惑星の周りの、球殻）の中で、<strong>どの高さか</strong>を、0〜1 で、求めます。種類ごとの、グラデーション（[Cloud Layers](layers.md)）を、掛けて、底は、平ら、上端は、丸い形に、します。

### ③ 基本の、形

```hlsl
// 低周波の 3D ノイズ（Perlin-Worley）: 雲の、大きなもこもこ。R = Perlin-Worley、GBA = 異なる周波数の Worley。
float4 low = g_base_noise.SampleLevel(g_linear_wrap, position * g_base_scale + g_wind_offset, 0);
float low_freq_fbm = low.g * 0.625 + low.b * 0.25 + low.a * 0.125;     // Worley の 3 オクターブを、足す
float base_cloud = Remap(low.r, -(1.0 - low_freq_fbm), 1.0, 0.0, 1.0); // Perlin-Worley を、Worley の fBm で、持ち上げる
base_cloud *= gradient;                                                 // 高さの、グラデーションを、掛ける
```

<strong>基本の形</strong>は、<strong>128³ の、3D テクスチャ</strong>から、読みます。R チャンネルは、Perlin ノイズ（なめらかな、うねり）に、Worley ノイズ（もこもこの、粒）を、混ぜたもので、GBA は、周波数の違う、Worley ノイズです。Worley の fBm で、Perlin-Worley を、持ち上げる（`Remap` の、下限を、動かす）ことで、雲の、もこもこした、輪郭が、できます。

```hlsl
// Remap: 値 v を、範囲 [l0, h0] から、範囲 [l1, h1] へ、線形に、写す（範囲の外は、そのまま、外挿）。
float Remap(float v, float l0, float h0, float l1, float h1) {
  return l1 + (v - l0) * (h1 - l1) / (h0 - l0);
}
```

`Remap` は、<strong>この方式の、基本の道具</strong>です。<strong>ノイズの値の、範囲を、動かして</strong>、雲の量（カバレッジ）や、輪郭の、細かさを、調整します。

### ④ カバレッジを、適用する

```hlsl
// カバレッジ（0〜1）で、雲の量を決める。カバレッジが、大きいほど、下限が、下がり、雲が、増える。
float base_with_coverage = Remap(base_cloud, coverage, 1.0, 0.0, 1.0);
base_with_coverage *= coverage;                                          // カバレッジが、小さいとき、密度も、薄く
```

<strong>カバレッジ</strong>以下の、ノイズの値は、<strong>0</strong>（雲なし）に、切られ、それより上が、雲になります。カバレッジが、大きいほど、切られる部分が、減って、雲が、増えます。最後に、カバレッジを掛けて、少ない雲が、薄くなるようにします。

### ⑤ 細部で、縁を、削る（エロージョン）

```hlsl
// 高周波の 3D ノイズ（Worley の fBm）で、雲の縁を、削って、細かいちぎれを、作る。
float3 high = g_detail_noise.SampleLevel(g_linear_wrap, position * g_detail_scale + g_wind_offset * 0.3, 0).rgb;
float high_freq_fbm = high.r * 0.625 + high.g * 0.25 + high.b * 0.125;
// 底（height_fraction が小さい）では、ノイズを、反転して、ふわっとした底に。上は、そのまま。
float detail_modifier = lerp(high_freq_fbm, 1.0 - high_freq_fbm, saturate(height_fraction * 10.0));
float density = Remap(base_with_coverage, detail_modifier * 0.2, 1.0, 0.0, 1.0);
```

<strong>細部のノイズ</strong>（<strong>32³</strong>）で、基本の形の、縁を、削ります。雲の、内側（密度が、高い所）は、ほとんど、削られず、縁（密度が、低い所）が、大きく、削られるので、縁だけが、ちぎれたような、細かい形に、なります。`height_fraction` で、底と上端の、削り方を、変えて、底は、ふわっと、上は、もこもこに、します。

```hlsl
return max(density, 0.0) * g_density_scale;                              // 負の値を、切り、全体の濃さの、係数を、掛ける
```

## ノイズ テクスチャの、作り方

<strong>ノイズ テクスチャ</strong>は、<strong>事前に、ツールで、作って</strong>、3D テクスチャとして、読み込みます（実行時には、作りません）。

| テクスチャ | 大きさ | 内容 |
| --- | --- | --- |
| 基本の形 | 128×128×128（`R8G8B8A8`） | R = Perlin-Worley、G/B/A = Worley（周波数 1×、2×、4×） |
| 細部 | 32×32×32（`R8G8B8A8`） | R/G/B = Worley（周波数 2×、4×、8×） |

```hlsl
// Worley ノイズ（セル ノイズ）: 各セルに、ランダムな点を置き、最も近い点までの、距離を、返す。1 から引いて、「もこもこ」にする。
float Worley3D(float3 p, float frequency) {
  float3 q = p * frequency;
  float3 cell = floor(q);
  float3 f = frac(q);
  float min_dist = 1.0;
  for (int z = -1; z <= 1; ++z)
    for (int y = -1; y <= 1; ++y)
      for (int x = -1; x <= 1; ++x) {
        float3 neighbor = float3(x, y, z);
        float3 point = Hash33(fmod(cell + neighbor, frequency));       // 周期的になるように、frequency で、折り返す
        float d = length(neighbor + point - f);
        min_dist = min(min_dist, d);
      }
  return 1.0 - saturate(min_dist);                                     // 点の近くが、明るい（雲の、もこもこ）
}
```

<strong>Worley ノイズ</strong>（Worley、1996）は、<strong>各セルに、1 つ、ランダムな点</strong>を置き、各位置から、最も近い点までの、距離で、値を決めます。1 から引くと、点の周りが、明るい、丸い塊に、なり、雲の、もこもこに、似ます。`fmod(cell + neighbor, frequency)` で、周期的に（端で、つながる）、3D テクスチャを、繰り返して、使えるようにします。

## 風で、動かす

<strong>ノイズの、読み込み位置</strong>を、<strong>時間とともに、ずらす</strong>と、雲が、風で、流れます。

```hlsl
float3 wind_offset = g_wind_direction * g_time * g_wind_speed;          // 風の向きに、時間とともに、ずらす
// 基本の形は、ゆっくり、細部は、少し速く（細部が、基本の形の中を、流れる、ように見える）。
float4 low = g_base_noise.SampleLevel(g_linear_wrap, position * g_base_scale + wind_offset, 0);
float3 high = g_detail_noise.SampleLevel(g_linear_wrap, position * g_detail_scale + wind_offset * 1.5, 0).rgb;
```

<strong>基本の形と、細部の、動く速さを、少し、変える</strong>と、<strong>雲が、変形しながら、流れる</strong>ように、見えます（ただ、並行移動する、だけだと、平板）。

## 密度の、使い方

ここで、求めた、<strong>密度</strong>は、<strong>レイマーチの、各サンプル</strong>で、散乱・吸収の、計算に、使います（[Cloud Raymarching](raymarch.md)）。密度が、高い所ほど、光を、よく散らし、よく、遮ります。

## よくあるミス

??? failure "雲の縁が、なめらかすぎる"
    <strong>高周波のノイズ</strong>で<strong>縁を削る</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 低周波で形、高周波で細部

## 参考

- Schneider, Vos, "The Real-Time Volumetric Cloudscapes of Horizon: Zero Dawn", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Schneider, "Nubis: Authoring Real-Time Volumetric Cloudscapes with the Decima Engine", SIGGRAPH 2017, Advances in Real-Time Rendering in Games
- Worley, "A Cellular Texture Basis Function", SIGGRAPH 1996（Worley ノイズ。雲のもこもこに使う）
- Perlin, "An Image Synthesizer", SIGGRAPH 1985
- Hillaire, "Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite", SIGGRAPH 2016, Physically Based Shading in Theory and Practice

## 関連ページ

- [Clouds](index.md)
- [Cloud Layers](layers.md)
- [Cloud Raymarching](raymarch.md)
