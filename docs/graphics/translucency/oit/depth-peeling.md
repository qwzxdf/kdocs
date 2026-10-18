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

## Common Mistakes {#よくあるミス}

??? failure "層が多いシーンで、Depth Peeling が遅すぎる"
    **PPLL や WBOIT**に切り替える。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **1 層ずつ剥いで、正確に描く**
    - [x] **重いので、現在は少数派**

## References {#参考}

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## Related Pages {#関連ページ}

- [OIT](index.md)
- [PPLL](ppll.md)
- [WBOIT](wboit.md)
