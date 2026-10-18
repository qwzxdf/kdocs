---
title: Depth Peeling
tags:
  - 描画
---

# Depth Peeling

**Depth Peeling は、最も手前の層を描いて、その次の層、さらに次…と、1 枚ずつ剥ぎながら描く手法**です。**正確ですが、層の数だけ描画が必要**で、**重い**です。このページでは、**Depth Peeling の仕組みと限界**を説明します。

!!! tip "ポイント"
    - **1 パスごとに、1 層ずつ（手前から）取り出す**。
    - **層の数だけ、パスが必要**（4 層なら 4 パス）。
    - **正確だが、重い**。
    - **現在は、PPLL や WBOIT に置き換わっている**。

<!-- fig:depth-peeling-passes:begin -->

<svg class="fig illust motion" data-fig="depth-peeling-passes" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-depth-peeling-passes" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">デプス ピーリング: 手前の層から 1 枚ずつ「皮をむく」ように取り出して、正しく混ぜる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 24 画素に、3 枚の半透明を重ねる。毎回の描画(パス)で、まだ取っていない一番手前の層を取る</text>
<text x="60.0" y="96" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">半透明の 3 枚(深度: 小さいほど手前)</text>
<rect x="126.0" y="102" width="396.0" height="18" fill="#f24c4c" fill-opacity="0.5"/>
<text x="132.0" y="116" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">A 深度 5</text>
<rect x="324.0" y="124" width="396.0" height="18" fill="#33bf4c" fill-opacity="0.6"/>
<text x="330.0" y="138" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">B 深度 3</text>
<rect x="60.0" y="146" width="726.0" height="18" fill="#4073ff" fill-opacity="0.5"/>
<text x="66.0" y="160" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">C 深度 7</text>
<text x="60.0" y="187" text-anchor="start" style="font-size:13px;font-weight:700;fill:#7c3aed">パス 1: 1 番目に手前の層を取る</text>
<rect x="60.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0732" values="#e5e7eb;#99b2f9"/></rect>
<rect x="93.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0780" values="#e5e7eb;#99b2f9"/></rect>
<rect x="126.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0829" values="#e5e7eb;#f29f9f"/></rect>
<rect x="159.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0878" values="#e5e7eb;#f29f9f"/></rect>
<rect x="192.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0927" values="#e5e7eb;#f29f9f"/></rect>
<rect x="225.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0976" values="#e5e7eb;#f29f9f"/></rect>
<rect x="258.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1024" values="#e5e7eb;#f29f9f"/></rect>
<rect x="291.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1073" values="#e5e7eb;#f29f9f"/></rect>
<rect x="324.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1122" values="#e5e7eb;#80d48f"/></rect>
<rect x="357.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1171" values="#e5e7eb;#80d48f"/></rect>
<rect x="390.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1220" values="#e5e7eb;#80d48f"/></rect>
<rect x="423.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1268" values="#e5e7eb;#80d48f"/></rect>
<rect x="456.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1317" values="#e5e7eb;#80d48f"/></rect>
<rect x="489.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1366" values="#e5e7eb;#80d48f"/></rect>
<rect x="522.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1415" values="#e5e7eb;#80d48f"/></rect>
<rect x="555.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1463" values="#e5e7eb;#80d48f"/></rect>
<rect x="588.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1512" values="#e5e7eb;#80d48f"/></rect>
<rect x="621.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1561" values="#e5e7eb;#80d48f"/></rect>
<rect x="654.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1610" values="#e5e7eb;#80d48f"/></rect>
<rect x="687.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1659" values="#e5e7eb;#80d48f"/></rect>
<rect x="720.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1707" values="#e5e7eb;#99b2f9"/></rect>
<rect x="753.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1756" values="#e5e7eb;#99b2f9"/></rect>
<rect x="786.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="819.0" y="190.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="60.0" y="190" width="792.0" height="33.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="249" text-anchor="start" style="font-size:13px;font-weight:700;fill:#7c3aed">パス 2: 2 番目に手前の層を取る</text>
<rect x="60.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="93.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="126.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2780" values="#e5e7eb;#99b2f9"/></rect>
<rect x="159.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2829" values="#e5e7eb;#99b2f9"/></rect>
<rect x="192.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2878" values="#e5e7eb;#99b2f9"/></rect>
<rect x="225.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2927" values="#e5e7eb;#99b2f9"/></rect>
<rect x="258.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2976" values="#e5e7eb;#99b2f9"/></rect>
<rect x="291.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3024" values="#e5e7eb;#99b2f9"/></rect>
<rect x="324.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3073" values="#e5e7eb;#f29f9f"/></rect>
<rect x="357.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3122" values="#e5e7eb;#f29f9f"/></rect>
<rect x="390.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3171" values="#e5e7eb;#f29f9f"/></rect>
<rect x="423.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3220" values="#e5e7eb;#f29f9f"/></rect>
<rect x="456.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3268" values="#e5e7eb;#f29f9f"/></rect>
<rect x="489.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3317" values="#e5e7eb;#f29f9f"/></rect>
<rect x="522.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3366" values="#e5e7eb;#99b2f9"/></rect>
<rect x="555.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3415" values="#e5e7eb;#99b2f9"/></rect>
<rect x="588.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3463" values="#e5e7eb;#99b2f9"/></rect>
<rect x="621.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3512" values="#e5e7eb;#99b2f9"/></rect>
<rect x="654.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3561" values="#e5e7eb;#99b2f9"/></rect>
<rect x="687.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3610" values="#e5e7eb;#99b2f9"/></rect>
<rect x="720.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="753.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="786.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="819.0" y="252.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="60.0" y="252" width="792.0" height="33.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="311" text-anchor="start" style="font-size:13px;font-weight:700;fill:#7c3aed">パス 3: 3 番目に手前の層を取る</text>
<rect x="60.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="93.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="126.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="159.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="192.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="225.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="258.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="291.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="324.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5024" values="#e5e7eb;#99b2f9"/></rect>
<rect x="357.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5073" values="#e5e7eb;#99b2f9"/></rect>
<rect x="390.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5122" values="#e5e7eb;#99b2f9"/></rect>
<rect x="423.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5171" values="#e5e7eb;#99b2f9"/></rect>
<rect x="456.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5220" values="#e5e7eb;#99b2f9"/></rect>
<rect x="489.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5268" values="#e5e7eb;#99b2f9"/></rect>
<rect x="522.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="555.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="588.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="621.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="654.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="687.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="720.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="753.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="786.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="819.0" y="314.0" width="33.3" height="33.3" fill="#e5e7eb"/>
<rect x="60.0" y="314" width="792.0" height="33.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="392" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">描いた断片の数(各パスで全部描き直す):</text>
<text x="390.0" y="394" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0730;0.0732;1.0000" values="1;1;0;0"/></text>
<text x="390.0" y="394" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">46<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0730;0.0732;0.2681;0.2683;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390.0" y="394" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">92<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2681;0.2683;0.4632;0.4634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390.0" y="394" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">138<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.4632;0.4634;1.0000" values="0;0;1;1"/></text>
<text x="60.0" y="422" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">奥のパスから手前へ混ぜた結果</text>
<rect x="60.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6585" values="#e5e7eb;#99b2f9"/></rect>
<rect x="93.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6615" values="#e5e7eb;#99b2f9"/></rect>
<rect x="126.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6644" values="#e5e7eb;#c680a3"/></rect>
<rect x="159.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6673" values="#e5e7eb;#c680a3"/></rect>
<rect x="192.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6702" values="#e5e7eb;#c680a3"/></rect>
<rect x="225.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6732" values="#e5e7eb;#c680a3"/></rect>
<rect x="258.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6761" values="#e5e7eb;#c680a3"/></rect>
<rect x="291.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6790" values="#e5e7eb;#c680a3"/></rect>
<rect x="324.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6820" values="#e5e7eb;#6ea66f"/></rect>
<rect x="357.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6849" values="#e5e7eb;#6ea66f"/></rect>
<rect x="390.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6878" values="#e5e7eb;#6ea66f"/></rect>
<rect x="423.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#e5e7eb;#6ea66f"/></rect>
<rect x="456.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6937" values="#e5e7eb;#6ea66f"/></rect>
<rect x="489.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6966" values="#e5e7eb;#6ea66f"/></rect>
<rect x="522.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6995" values="#e5e7eb;#5cba91"/></rect>
<rect x="555.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7024" values="#e5e7eb;#5cba91"/></rect>
<rect x="588.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7054" values="#e5e7eb;#5cba91"/></rect>
<rect x="621.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7083" values="#e5e7eb;#5cba91"/></rect>
<rect x="654.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7112" values="#e5e7eb;#5cba91"/></rect>
<rect x="687.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7141" values="#e5e7eb;#5cba91"/></rect>
<rect x="720.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7171" values="#e5e7eb;#99b2f9"/></rect>
<rect x="753.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7200" values="#e5e7eb;#99b2f9"/></rect>
<rect x="786.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7229" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="819.0" y="428.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7259" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="60.0" y="428" width="792.0" height="33.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.7676;0.7678;1.0000" values="0;0;1;1"/><rect x="60" y="462" width="840" height="56" rx="12" fill="#f0fdf4" stroke="#2ea043" stroke-width="2.5"/>
<text x="76" y="486" text-anchor="start" style="font-size:15px;font-weight:700;fill:#166534">結果は、奥から順に混ぜた正解と完全に一致(ずれ 0)</text>
<text x="76" y="510" text-anchor="start" style="font-size:14px;font-weight:700;fill:#991b1b">代わりに、層の数 3 回、シーンを描き直す(断片 46 個 → 合計 138 個)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">画素ごとに、手前から何枚重なっているかは、描くまで分からない<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0730;0.0732;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">毎回、前のパスで取った層より奥で、一番手前の層だけを残す<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0730;0.0732;0.6583;0.6585;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">取れた層を、奥から手前へ混ぜる<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.6583;0.6585;0.7676;0.7678;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">正確だが、層の数だけ描き直す(高コスト)<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.7676;0.7678;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:depth-peeling-passes:end -->

## Depth Peeling
<strong>「最も手前の層」を、深度テストで取り出し、次に「その次の層」を取り出し…と、層を剥がしていく</strong>方法です。

| 手順 | 内容 |
| --- | --- |
| **① 1 枚目** | **通常の深度テスト**で、**最も手前の半透明の層**を、**画像 1 に描く**。**深度 1 を保存** |
| **② 2 枚目** | **深度 1 より奥の最も手前**を、**画像 2 に描く**（**前の深度より手前のフラグメントは、捨てる**） |
| **③ N 枚目まで繰り返す** | **層の数だけ、描画を繰り返す** |
| **④ 合成** | **奥の層から手前へ**、**N 枚の画像を重ねる** |


原典は、Everitt の "Interactive Order-Independent Transparency"（NVIDIA、2001）で、後に Bavoil と Myers が、手前と奥を同時に剥がす Dual Depth Peeling（2008）で、パスを半分にしました。

原典は、Everitt の "Interactive Order-Independent Transparency"（NVIDIA、2001）で、後に Bavoil と Myers が、手前と奥を同時に剥がす Dual Depth Peeling（2008）で、パスを半分にしました。

```hlsl
float4 PSMain(VsOutput input) : SV_Target {
  float previous_depth = previous_depth_texture.Load(int3(input.position.xy, 0)).r;
  clip(input.position.z - previous_depth - kEpsilon);
  return Shade(input);
}
```

| 点 | 説明 |
| --- | --- |
| **`clip(z - previous_depth - ε)`** | **前の層と同じか手前**の**フラグメント**を**捨てる** |
| **層の数** | **4 層で、多くのシーンは足りる**が、**足りない画素は、欠ける** |
| **コスト** | **N 回の描画**（**シーン全体の半透明ジオメトリを、N 回流す**） |
| **派生** | **Dual Depth Peeling**（**手前と奥を、同時に剥がす**：パスが半分） |

## 考え方：1 層ずつ、剥がす

**デプス ピーリング**（Everitt、2001）は、**最も手前の層から、順に、1 層ずつ**、**剥がす**ように、取り出していく方法です。

```text
視線 ──→  ┌────┐   ┌────┐   ┌────┐
          │ 層1 │   │ 層2 │   │ 層3 │     層 1 が、最も手前
          └────┘   └────┘   └────┘
```

1. 最初のパスで、**最も手前の層**（層 1）を、描く
2. 2 つ目のパスで、**層 1 より、奥の、最も手前**（層 2）を、描く
3. 3 つ目のパスで、**層 2 より、奥の、最も手前**（層 3）を、描く
4. …（層が、なくなるまで）
5. 取り出した層を、**奥から手前**の順に、**ブレンド**する

**各層は、画素ごとに、1 つの、フラグメント**です。**正確な順序**で、ブレンドできるので、**順序に依存しない透明が、正確に**、得られます。

## 仕組み：深度を、2 枚、使う

**前のパスの深度**を、テクスチャとして、**ピクセル シェーダーで、読み**、**それより、手前のフラグメントを、捨てます**。

```hlsl
Texture2D<float> g_prev_depth : register(t0);       // 前のパスで取り出した層の深度

struct PSOut { float4 color : SV_Target; };

PSOut main(PSInput input) {
  // 前の層の深度以下（手前）のフラグメントは、すでに取り出したので、捨てる。
  float prev = g_prev_depth.Load(int3(input.position.xy, 0));
  if (input.position.z <= prev + 1e-6) discard;

  PSOut o;
  o.color = ShadeFragment(input);                    // 通常の、ライティング
  return o;
}
```

| 設定 | 内容 |
| --- | --- |
| 深度テスト | `LESS`（最も手前の、1 つだけが、残る） |
| 深度の書き込み | 有効（そのパスでの、最も手前を、決めるため） |
| 前の深度 | **ping-pong**（2 枚の深度を、交互に、読み書き）。**書き込み先と、読み取り元は、別のテクスチャ** |
| 色 | 各パスの、色を、別の、レンダー ターゲットに、保存 |

```cpp
// 各層: 深度は 2 枚を交互に使う。色は、層ごとに別のテクスチャへ。
for (int layer = 0; layer < kMaxLayers; ++layer) {
  const int write = layer & 1, read = 1 - write;
  context->OMSetRenderTargets(1, layer_rtv[layer].GetAddressOf(), depth_dsv[write].Get());
  context->ClearDepthStencilView(depth_dsv[write].Get(), D3D11_CLEAR_DEPTH, 1.0f, 0);
  context->PSSetShaderResources(0, 1, depth_srv[read].GetAddressOf());
  DrawTransparentObjects();
}
// 最後に、層を奥（最後に取り出した層）から手前（最初）の順に、ブレンドする。
```

## 層の、数

必要な、パスの数は、**画素ごとの、最大の重なり（深度の複雑度）**です。

| 場面 | 重なり | パス |
| --- | --- | --- |
| 窓ガラス | 1〜2 | 2 |
| 葉の群れ | 5〜20 | 多い（重い） |
| 髪の毛 | 10〜50 | 非常に、多い |

**すべての層を、取り出す**には、**パスの数 × 半透明の描画コスト**が、かかります。実用では、**手前の、数層（3〜4 層）**だけを、正確に、残りは、近似、という使い方に、なります。

## デュアル デプス ピーリング

Bavoil と Myers（2008）の、**デュアル デプス ピーリング**は、**最も手前と、最も奥の、両方を、同時に、剥がす**方法です。**パスの数が、約半分**になります。

| 方式 | 1 パスで剥がす層 | 必要なパス（層が 8 のとき） |
| --- | --- | --- |
| 通常 | 手前から、1 層 | 8 |
| デュアル | 手前と奥から、各 1 層 | 4 |

**最小深度と、最大深度**を、同時に、追跡し、**ブレンドの、MIN / MAX 演算**を、使って、実現します（`BlendOp = MAX`、深度を、`-depth` で、2 つを、1 つのテクスチャに、格納する）。実装は、複雑ですが、**パスの、半減**が、得られます。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **正確**（順序が、完全に、正しい）。**ソート不要**。実装が、**概念的に**単純 |
| 短所 | **重い**。層の数 × 描画。**層が、足りないと、奥が、欠ける** |
| 短所 | **メモリ**：層ごとの、レンダー ターゲット（1 層 = 画面 1 枚） |
| 短所 | **半透明を、層の数だけ、何度も描く**（ジオメトリ、頂点シェーダーも、繰り返す） |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| 小さな、**重要な**半透明（ガラスの、造形物） | 使える |
| 重なりが、非常に多い（髪、葉、煙） | **重すぎる**。他の方式（[WBOIT](wboit.md)、[PPLL](ppll.md)） |
| オフラインの、正解画像の作成 | 最適（比較用の、リファレンス） |

## よくあるミス

??? failure "層が多いシーンで、Depth Peeling が遅すぎる"
    **PPLL や WBOIT**に切り替える。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **1 層ずつ剥いで、正確に描く**
    - [x] **重いので、現在は少数派**

## 参考

- Everitt, "Interactive Order-Independent Transparency", NVIDIA White Paper, 2001（デプス ピーリング）
- Bavoil, Myers, "Order Independent Transparency with Dual Depth Peeling", NVIDIA White Paper, 2008
- Carpenter, "The A-buffer, an Antialiased Hidden Surface Method", SIGGRAPH 1984
- Wyman, "Exploring and Expanding the Continuum of OIT Algorithms", High-Performance Graphics 2016

## 関連ページ

- [OIT](index.md)
- [PPLL](ppll.md)
- [WBOIT](wboit.md)
