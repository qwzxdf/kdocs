---
title: Depth Peeling
tags:
  - 描画
---

# Depth Peeling

半透明の物を正しい順番で重ねるには画素ごとに奥から手前へ並べ替える必要があります。メッシュをソートする方法は三角形が互いに貫通すると破綻します。画素ごとの並べ替えを深度テストの力でやるのが、Depth Peeling です。

<strong>Depth Peeling は最も手前の層を描いて、その次の層、さらに次…と 1 枚ずつ剥ぎながら描く手法です</strong>。順序が完全に正しくなる代わりに層の数だけ描画が必要で、重くなります。このページでは仕組みシェーダーと C++ の骨組み必要な層の数（実測つき）、メモリと時間の見積もりデュアル デプス ピーリング、使いどころを説明します。

!!! tip "ポイント"
    - 1 パスごとに手前から 1 層ずつ取り出します。前のパスの深度より手前のフラグメントは捨てます。
    - 層の数だけパスが要ります。4 層なら 4 パスでそのたびに半透明のジオメトリを全部流します。
    - 順序は正確です。層が足りない画素は奥が欠けます。
    - 実測では平均の重なりが 4 の場面で、4 層だと 37 % の画素が足りませんでした。
    - 現在は PPLL や WBOIT に置き換わっていて、使いどころは小さな半透明物かリファレンスの作成です。

!!! info "このページを読む前に"
    - [Order-Independent Transparency (OIT)](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

<!-- fig:depth-peeling-passes:begin -->

<svg class="fig illust motion" data-fig="depth-peeling-passes" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-depth-peeling-passes" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">デプス ピーリング: 手前の層から 1 枚ずつ「皮をむく」ように取り出して、正しく混ぜる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 24 画素に 3 枚の半透明を重ねる。毎回の描画(パス)で、まだ取っていない一番手前の層を取る</text>
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
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">取れた層を奥から手前へ混ぜる<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.6583;0.6585;0.7676;0.7678;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">正確だが、層の数だけ描き直す(高コスト)<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.7676;0.7678;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:depth-peeling-passes:end -->

## 考え方: 1 層ずつ剥がす {#idea}

画素ごとに半透明のフラグメントが、深度の順に並んでいます。最も手前の層は通常の深度テスト（`LESS`）で取り出せます。2 枚目は「1 枚目より奥で、最も手前」を取り出せば得られます。これを繰り返して層を剥がしていきます。

1. 1 枚目のパスで最も手前の半透明の層を画像 1 に描きます。このときの深度 1 を保存します。
2. 2 枚目のパスで深度 1 より奥の最も手前を画像 2 に描きます。前の深度より手前（同じ深度を含む）のフラグメントは捨てます。
3. N 枚目まで層の数だけ繰り返します。
4. 取り出した N 枚の画像を手前から奥へ（または奥から手前へ）、順序どおりにブレンドします。

各層は画素ごとに 1 つのフラグメントです。順序どおりに合成できるので順序に依存しない透明が、正確に得られます。原典は Everitt の "Interactive Order-Independent Transparency"（NVIDIA、2001）です。後に Bavoil と Myers が、手前と奥を同時に剥がす Dual Depth Peeling（2008）で、パスを半分にしました。

## 仕組み: 前のパスの深度を読む {#shader}

前のパスの深度をテクスチャとして、ピクセル シェーダーで読んで、それ以下のフラグメントを捨てます。

```hlsl
Texture2D<float> g_prev_depth : register(t0);       // 前のパスで取り出した層の深度
Texture2D<float4> g_albedo : register(t1);
SamplerState g_linear_wrap : register(s0);

cbuffer PeelConstants : register(b0) {
  float g_epsilon;           // 同じ深度とみなす誤差。例: 1e-6
  uint g_layer_index;        // 0 = 最初のパス（前の深度がない）
  float2 _pad;
};

struct PsInput {
  float4 position : SV_Position;
  float2 uv : TEXCOORD0;
};

// 各層のパス: 前の層より奥の、最も手前のフラグメントだけが残る（深度テスト LESS と組み合わせる）
float4 PeelPS(PsInput i) : SV_Target {
  if (g_layer_index > 0) {
    float prev = g_prev_depth.Load(int3(i.position.xy, 0));
    // 前の層以下（手前、または同じ）のフラグメントは、すでに取り出したので捨てる
    if (i.position.z <= prev + g_epsilon) discard;
  }
  float4 c = g_albedo.Sample(g_linear_wrap, i.uv);
  return c;                  // プリマルチプライドにするかは、合成の式に合わせて決める
}
```

深度テストは `LESS` にします。そのパスで残るフラグメントのうち最も手前の 1 つだけが、深度バッファに残ります。深度の書き込みは有効にします。前のパスの深度は読み取り元と書き込み先を別のテクスチャにして、2 枚を交互に使います（ping-pong）。色は各パスの結果を別のレンダー ターゲットに保存します。

`g_epsilon` は前の層のフラグメントそのものを確実に捨てるための誤差です。浮動小数点の深度の比較で同じ値が、わずかに小さく出ることがあるためです。小さすぎると前の層が捨てられずに同じ層が 2 回取り出されます。大きすぎると近い 2 つの層が 1 つにまとめて捨てられます。

C++ 側は層ごとに描画先と深度を切り替えます。

```cpp
// （コンパイルしていない）各層: 深度は 2 枚を交互に使う。色は層ごとに別のテクスチャへ
for (int layer = 0; layer < kMaxLayers; ++layer) {
  const int write = layer & 1, read = 1 - write;
  context->OMSetRenderTargets(1, layer_rtv[layer].GetAddressOf(), depth_dsv[write].Get());
  context->ClearDepthStencilView(depth_dsv[write].Get(), D3D11_CLEAR_DEPTH, 1.0f, 0);
  context->ClearRenderTargetView(layer_rtv[layer].Get(), kTransparentBlack);   // 剥がし切った画素は透明のまま
  context->PSSetShaderResources(0, 1, depth_srv[read].GetAddressOf());          // 前の層の深度
  DrawTransparentObjects(layer);                                                // g_layer_index を渡す
}
```

最後に、層を合成します。手前から奥へ取り出しているので、手前から順に積む形が自然です。透過率 `T` を持ち各層の色に `T × a` を掛けて足して、`T` を `(1 − a)` ずつ縮めます。

```hlsl
Texture2D<float4> g_layers[4] : register(t2);        // 層 0 が最も手前（プリマルチプライドでない色と a）

float4 CompositePS(float4 pos : SV_Position) : SV_Target {
  float3 color = 0.0;
  float transmittance = 1.0;                         // まだ背景の光が残っている割合
  [unroll] for (int k = 0; k < 4; ++k) {
    float4 layer = g_layers[k].Load(int3(pos.xy, 0));
    color += transmittance * layer.rgb * layer.a;    // 手前の層が隠さなかった分だけが見える
    transmittance *= (1.0 - layer.a);
  }
  // 背景（不透明の描画結果）は、残った透過率の分だけ見える。ここでは透過率を返して、ブレンドで合成する
  return float4(color, transmittance);               // ブレンド: SrcBlend = ONE, DestBlend = SRC_ALPHA
}
```

最後のブレンドは `背景 × transmittance + color` になります。`SrcBlend = ONE`、`DestBlend = SRC_ALPHA` で実現します。

## 必要な層の数 {#layers}

必要なパスの数は画素ごとの最大の重なり（深度の複雑度）です。窓ガラスは 1〜2、葉の群れは 5〜20、髪の毛は 10〜50 です。すべての層を取り出すにはパスの数 × 半透明の描画コストがかかります。実用では手前の数層だけを正確に出して、残りは捨てるか近似します。

画素ごとの重なりがポアソン分布に従うと仮定して、シミュレーションで測りました。20 万画素にランダムな深度、色、アルファ（0.2〜0.8）のフラグメントを置いて、手前から N 層だけを合成した結果を全層の正しい合成と比べました。

平均の重なりが 2 の場面では 2 層で足りない画素が 32.5 %、3 層で 14.4 %、4 層で 5.3 %、6 層で 0.4 % でした。平均 4 の場面では 4 層で 37.3 %、6 層で 11.1 %、8 層で 2.1 % が足りません。平均 8 の場面では 8 層でも 40.8 % が足りませんでした。

<svg class="fig flow" viewBox="0 0 720 270" role="img" aria-label="平均の重なりが 4 のとき、N 層だけ剥がすと足りない画素の割合"><text x="14" y="22" class="fig-title">N 層で足りない画素の割合（平均の重なり 4）</text>
<line x1="60" y1="210" x2="690" y2="210" stroke="currentColor" stroke-width="1.5"/>
<g fill="rgba(76,139,245,0.28)" stroke="#4c8bf5" stroke-width="2"><rect x="80" y="30" width="48" height="180"/><rect x="146" y="45" width="48" height="165"/><rect x="212" y="75" width="48" height="135"/><rect x="278" y="121" width="48" height="89"/><rect x="344" y="158" width="48" height="52"/><rect x="410" y="184" width="48" height="26"/><rect x="476" y="198" width="48" height="12"/><rect x="542" y="205" width="48" height="5"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="104" y="24">91 %</text><text x="170" y="39">76 %</text><text x="236" y="69">57 %</text><text x="302" y="115">37 %</text><text x="368" y="152">22 %</text><text x="434" y="178">11 %</text><text x="500" y="192">5 %</text><text x="566" y="199">2 %</text>
<text x="104" y="230">1 層</text><text x="170" y="230">2</text><text x="236" y="230">3</text><text x="302" y="230">4</text><text x="368" y="230">5</text><text x="434" y="230">6</text><text x="500" y="230">7</text><text x="566" y="230">8</text></g>
<text x="360" y="258" text-anchor="middle" style="font-size:12px">4 層でも 3 分の 1 の画素が足りない。層を増やすほど、パスもメモリも増える</text></svg>

足りない画素は奥の層が欠けます。合成結果との差（最大のチャンネル差の平均）は、平均 4 の場面で 4 層で 0.011、2 層で 0.101、1 層で 0.254 でした。4 層での誤差は 1 % 程度で小さく見えますが、画素の 3 分の 1 に出ています。層が多い場面（髪、葉）で使うには現実的でありません。

## コストの見積もり {#cost}

1920 × 1080 の画面で、層の色を RGBA8 にすると、1 枚 `1920 × 1080 × 4 B ≒ 7.9 MiB` です。深度の `R32` も 1 枚 7.9 MiB で、ping-pong に 2 枚要ります。4 層なら色が約 32 MiB、深度が約 16 MiB で合計約 48 MiB です。8 層なら色が約 63 MiB で、合計約 79 MiB になります。

時間のコストは層の数 × 半透明のジオメトリの描画です。頂点シェーダーも層の数だけ繰り返します。ジオメトリが重いほど層の数に比例して重くなります。

## デュアル デプス ピーリング {#dual}

Bavoil と Myers（2008）のデュアル デプス ピーリングは、最も手前と最も奥の両方を同時に剥がす方法です。パスの数が約半分になります。層が 8 なら通常は 8 パスで、デュアルは 4 パスです。

最小深度と最大深度を同時に追跡するためにブレンドの `MAX` 演算を使います。深度を `(−z, z)` の 2 成分で 1 つのテクスチャに入れると、`MAX` ブレンドで成分 1 には最小の `z`（符号反転）、成分 2 には最大の `z` が残ります。

```hlsl
Texture2D<float2> g_dual_depth : register(t3);       // (-最小 z, 最大 z)。前のパスの結果

struct DualOut {
  float2 depth : SV_Target0;       // ブレンド MAX。次のパスの窓を決める
  float4 front : SV_Target1;      // 手前の層の色（アンダー合成）
  float4 back  : SV_Target2;      // 奥の層の色（オーバー合成）
};

// Bavoil と Myers の考え方を自分で書いたもの。実行はしていない
DualOut DualPeelPS(PsInput i) {
  float2 window = g_dual_depth.Load(int3(i.position.xy, 0));
  float near_z = -window.x;          // 窓の手前の境界
  float far_z = window.y;            // 窓の奥の境界
  float z = i.position.z;

  DualOut o;
  o.depth = float2(-1.0, -1.0);      // MAX ブレンドで、何も書かないことと同じ（十分小さい値）
  o.front = 0.0;
  o.back = 0.0;

  // 窓の外のフラグメントは、すでに取り出したので捨てる
  if (z < near_z - g_epsilon || z > far_z + g_epsilon) return o;

  float4 c = g_albedo.Sample(g_linear_wrap, i.uv);
  if (z > near_z + g_epsilon && z < far_z - g_epsilon) {
    o.depth = float2(-z, z);         // 窓の内側。次のパスの窓を狭める候補にする
  } else if (z <= near_z + g_epsilon) {
    o.front = c;                     // 窓の手前の境界のフラグメントを、手前の層として出す
  } else {
    o.back = c;                      // 窓の奥の境界のフラグメントを、奥の層として出す
  }
  return o;
}
```

実装は複雑ですがパスの半減が得られます。最初のパスで窓を `(−最小 z, 最大 z)` で初期化する処理が別に必要です。

!!! note "確かめた範囲"
    層ごとの誤差と足りない画素の割合は、C++ のシミュレーションで測りました（MSVC `/W4`、C++ 最新で実行。フラグメントは乱数）。HLSL は `fxc`（`ps_5_0`）で `PeelPS`、`CompositePS`、`DualPeelPS` をコンパイルしてエラーが出ないことを確かめました。デュアルのシェーダーは動作を確かめていません。GPU での描画は確認していません。

## 長所と短所 {#pros-cons}

長所は順序が完全に正しいことです。ソートが要らず考え方が単純です。

短所は重いことです。層の数だけ描画が増えて層が足りないと奥が欠けます。層ごとのレンダー ターゲット（1 層が画面 1 枚）でメモリも要ります。半透明を何度も描くので頂点シェーダーも繰り返します。

## 使いどころ {#usage}

- 小さな重要な半透明（ガラスの造形物）には、使えます。
- 重なりが多い物（髪、葉、煙）は重すぎます。[WBOIT](wboit.md) や [PPLL](ppll.md) を使います。
- オフラインの正解画像の作成には最適です。比較用のリファレンスになります。

## よくあるミス {#mistakes}

??? failure "層が多いシーンで、Depth Peeling が遅すぎる"
    原因は層の数だけ半透明のジオメトリを全部流していることです。重なりが多い場面では実測でも 8 層で 4 割の画素が足りません。PPLL や WBOIT に切り替えます。

??? failure "同じ層が 2 回出るまたは層が飛ぶ"
    原因は前の深度との比較の誤差 `g_epsilon` が合っていないことです。小さすぎると同じ層が 2 回出ます。大きすぎると近い 2 つの層が 1 つにまとめられて、層が飛びます。深度の精度に合わせて決めます。

??? failure "深度の読み取りと書き込みで、エラーになる"
    原因は同じ深度テクスチャを読み取り元と書き込み先に同時に使っていることです。2 枚を交互に使います（ping-pong）。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 前の層の深度より奥の最も手前を 1 層ずつ取り出して、順序どおりに合成します。
    - [x] 層の数だけパスとメモリが要ります。平均の重なり 4 では 4 層でも約 37 % の画素が足りません。
    - [x] デュアルで、パスが約半分になります。
    - [x] 重なりの多い物には、PPLL や WBOIT を使います。

## 参考 {#references}

このページは次の資料を読まずに書きました。誤差と割合は C++ のシミュレーションで測った値です。デュアルのシェーダーは考え方を自分で書いたものです。

- Everitt, "Interactive Order-Independent Transparency", NVIDIA White Paper, 2001（デプス ピーリング）
- Bavoil, Myers, "Order Independent Transparency with Dual Depth Peeling", NVIDIA White Paper, 2008
- Carpenter, "The A-buffer, an Antialiased Hidden Surface Method", SIGGRAPH 1984
- Wyman, "Exploring and Expanding the Continuum of OIT Algorithms", High-Performance Graphics 2016

## 関連ページ

- [OIT](index.md)
- [PPLL](ppll.md)
- [WBOIT](wboit.md)
