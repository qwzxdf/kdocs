---
title: SAO (Scalable AO)
tags:
  - 描画
---

# SAO (Scalable AO)

<strong>SAO</strong>（Scalable Ambient Obscurance）は、2012 年に McGuire らが発表した方式です。[Alchemy AO](alchemy-ao.md)の<strong>式はそのまま</strong>にメモリ アクセスと実装を徹底的に最適化しました。最大の改良は深度バッファのミップ マップを作って、遠いサンプルは、粗いミップから読むことです。これで半径をいくら大きくしても、実行時間がほぼ一定になります（スケーラブル）。論文では、2560×1600 で、Alchemy の約 7 倍速と報告されています。

!!! tip "ポイント"
    - 式は <strong>Alchemy AO と同じ</strong>。<strong>変わったのは深度の読み方</strong>。
    - <strong>線形深度のミップ チェーン</strong>を作る。<strong>サンプルが遠いほど、粗いミップ</strong>を読む → <strong>キャッシュに乗り、半径に依存しない速さ</strong>。
    - ミップの作り方は<strong>平均ではなく、代表の 1 点を選ぶ</strong>（境界で嘘の深度ができるのを防ぐ）。
    - 深度だけから、位置と法線を<strong>高精度に復元</strong>する。<strong>G-Buffer 不要</strong>。
    - <strong>後の多くの SSAO 実装に影響</strong>した方式（深度のミップ・キャッシュを意識した設計）。

## 問題：半径が大きいとなぜ遅いか

Alchemy AO は、<strong>画面上の螺旋</strong>でサンプルを置きます。<strong>半径 R が大きい</strong>とサンプルは画面上で遠くに散ります。深度テクスチャの離れた位置を、バラバラに読むのでテクスチャ キャッシュが効かず、メモリ アクセスが遅くなります。

GPU のテクスチャ読み込みは、隣り合う画素をまとめてキャッシュに載せて速くしています。半径が小さければ、サンプルは p の近くにまとまり、同じキャッシュ ラインから何度も読めます。半径が大きいと、サンプルは画面の遠くに散り、1 回読むたびに別のメモリ領域へアクセスする形になります。メモリの帯域が足りなくなり、AO の計算は「計算量」でなく「メモリ待ち」で遅くなります。

HBAO や Alchemy AO でも、半径を大きくすると急に重くなることがありました。これは式の問題でなく、<strong>深度の読み方の問題</strong>です。SAO は式を変えず、読み方だけを変えて、この問題を解きます。

## 解決：深度のミップ マップ

<strong>深度テクスチャのミップ チェーン</strong>を作ります。<strong>遠くのサンプルは、粗いミップ</strong>から読みます。粗いミップは小さいので、キャッシュに収まり、散らばっても速いのです。

<svg class="fig illust" viewBox="0 0 760 270" role="img" aria-label="深度のミップとサンプル">
<text x="20" y="24" class="fig-title">近いサンプルは細かい深度（ミップ 0）、遠いサンプルは粗い深度（ミップが大きい）から読む</text>
<rect x="40" y="60" width="200" height="160" fill="rgba(76,139,245,0.2)" stroke="currentColor" stroke-width="2"/><text x="60" y="52" style="font-size:12px">ミップ 0（フル解像度）</text>
<rect x="270" y="90" width="100" height="100" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="2"/><text x="272" y="82" style="font-size:12px">ミップ 1</text>
<rect x="400" y="110" width="50" height="60" fill="rgba(229,170,40,0.3)" stroke="currentColor" stroke-width="2"/><text x="400" y="102" style="font-size:12px">ミップ 2</text>
<rect x="480" y="125" width="25" height="30" fill="rgba(229,72,77,0.3)" stroke="currentColor" stroke-width="2"/><text x="470" y="117" style="font-size:12px">ミップ 3</text>
<circle cx="140" cy="140" r="6" fill="currentColor"/><text x="120" y="168" style="font-size:12px">p</text>
<g fill="#4c8bf5"><circle cx="150" cy="130" r="4"/><circle cx="125" cy="150" r="4"/><circle cx="160" cy="155" r="4"/></g>
<g fill="#2ea043"><circle cx="190" cy="120" r="4"/><circle cx="100" cy="95" r="4"/></g>
<g fill="#e5a828"><circle cx="215" cy="185" r="4"/></g>
<text x="560" y="90" style="font-size:13px">近いサンプル → ミップ 0</text>
<text x="560" y="115" style="font-size:13px">中くらい → ミップ 1</text>
<text x="560" y="140" style="font-size:13px">遠い → ミップ 2・3</text>
<text x="20" y="250" style="font-size:12px">遠くのサンプルは、細かい位置の精度が不要なので、粗いミップで十分。小さいテクスチャを読むので、キャッシュに収まり速い</text>
</svg>

<!-- fig:sao-mip:begin -->

<svg class="fig illust motion" data-fig="sao-mip" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-sao-mip" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">SAO: 遠いサンプルほど、深度の「ミップ」の、粗い層から読む。半径が大きくても、読む範囲は一定</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 画素あたり 16 サンプル。サンプルの距離ごとに、読むミップの層を選ぶ。普通に読むと、キャッシュに入りきらない範囲を、読む</text>
<rect x="30" y="96" width="900" height="190" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 距離ごとに、読むミップの層(サンプル 16 個の、層番号)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/><text x="44" y="152" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">半径 4</text>
<rect x="130" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="152" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="178" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="200" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="226" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="248" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="274" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="296" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="322" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="344" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="370" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="392" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="418" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="440" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="466" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="488" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="514" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="536" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="562" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="584" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="610" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="632" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="658" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="680" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="706" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="728" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="754" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="776" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="802" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="824" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="850" y="138" width="44" height="24" fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="1.5"/>
<text x="872" y="155" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2709;0.2711;1.0000" values="0;0;1;1"/><text x="44" y="188" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">半径 16</text>
<rect x="130" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<text x="152" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="178" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<text x="200" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="226" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<text x="248" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="274" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<text x="296" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="322" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<text x="344" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="370" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<text x="392" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="418" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.25" stroke="#2563eb" stroke-width="1.5"/>
<text x="440" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="466" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.4" stroke="#2563eb" stroke-width="1.5"/>
<text x="488" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L1</text>
<rect x="514" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.4" stroke="#2563eb" stroke-width="1.5"/>
<text x="536" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L1</text>
<rect x="562" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.4" stroke="#2563eb" stroke-width="1.5"/>
<text x="584" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L1</text>
<rect x="610" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.4" stroke="#2563eb" stroke-width="1.5"/>
<text x="632" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L1</text>
<rect x="658" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.4" stroke="#2563eb" stroke-width="1.5"/>
<text x="680" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L1</text>
<rect x="706" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.4" stroke="#2563eb" stroke-width="1.5"/>
<text x="728" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L1</text>
<rect x="754" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.4" stroke="#2563eb" stroke-width="1.5"/>
<text x="776" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L1</text>
<rect x="802" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.4" stroke="#2563eb" stroke-width="1.5"/>
<text x="824" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L1</text>
<rect x="850" y="174" width="44" height="24" fill="#2563eb" fill-opacity="0.55" stroke="#2563eb" stroke-width="1.5"/>
<text x="872" y="191" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L2</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4754;0.4756;1.0000" values="0;0;1;1"/><text x="44" y="224" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">半径 64</text>
<rect x="130" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.25" stroke="#e5aa28" stroke-width="1.5"/>
<text x="152" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L0</text>
<rect x="178" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.4" stroke="#e5aa28" stroke-width="1.5"/>
<text x="200" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L1</text>
<rect x="226" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.4" stroke="#e5aa28" stroke-width="1.5"/>
<text x="248" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L1</text>
<rect x="274" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.55" stroke="#e5aa28" stroke-width="1.5"/>
<text x="296" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L2</text>
<rect x="322" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.55" stroke="#e5aa28" stroke-width="1.5"/>
<text x="344" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L2</text>
<rect x="370" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.55" stroke="#e5aa28" stroke-width="1.5"/>
<text x="392" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L2</text>
<rect x="418" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.55" stroke="#e5aa28" stroke-width="1.5"/>
<text x="440" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L2</text>
<rect x="466" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.7" stroke="#e5aa28" stroke-width="1.5"/>
<text x="488" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L3</text>
<rect x="514" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.7" stroke="#e5aa28" stroke-width="1.5"/>
<text x="536" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L3</text>
<rect x="562" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.7" stroke="#e5aa28" stroke-width="1.5"/>
<text x="584" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L3</text>
<rect x="610" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.7" stroke="#e5aa28" stroke-width="1.5"/>
<text x="632" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L3</text>
<rect x="658" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.7" stroke="#e5aa28" stroke-width="1.5"/>
<text x="680" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L3</text>
<rect x="706" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.7" stroke="#e5aa28" stroke-width="1.5"/>
<text x="728" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L3</text>
<rect x="754" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.7" stroke="#e5aa28" stroke-width="1.5"/>
<text x="776" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L3</text>
<rect x="802" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.7" stroke="#e5aa28" stroke-width="1.5"/>
<text x="824" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L3</text>
<rect x="850" y="210" width="44" height="24" fill="#e5aa28" fill-opacity="0.85" stroke="#e5aa28" stroke-width="1.5"/>
<text x="872" y="227" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L4</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6798;0.6800;1.0000" values="0;0;1;1"/><text x="44" y="260" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">半径 256</text>
<rect x="130" y="246" width="44" height="24" fill="#e5484d" fill-opacity="0.55" stroke="#e5484d" stroke-width="1.5"/>
<text x="152" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L2</text>
<rect x="178" y="246" width="44" height="24" fill="#e5484d" fill-opacity="0.7" stroke="#e5484d" stroke-width="1.5"/>
<text x="200" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L3</text>
<rect x="226" y="246" width="44" height="24" fill="#e5484d" fill-opacity="0.7" stroke="#e5484d" stroke-width="1.5"/>
<text x="248" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L3</text>
<rect x="274" y="246" width="44" height="24" fill="#e5484d" fill-opacity="0.85" stroke="#e5484d" stroke-width="1.5"/>
<text x="296" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L4</text>
<rect x="322" y="246" width="44" height="24" fill="#e5484d" fill-opacity="0.85" stroke="#e5484d" stroke-width="1.5"/>
<text x="344" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L4</text>
<rect x="370" y="246" width="44" height="24" fill="#e5484d" fill-opacity="0.85" stroke="#e5484d" stroke-width="1.5"/>
<text x="392" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L4</text>
<rect x="418" y="246" width="44" height="24" fill="#e5484d" fill-opacity="0.85" stroke="#e5484d" stroke-width="1.5"/>
<text x="440" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L4</text>
<rect x="466" y="246" width="44" height="24" fill="#e5484d" fill-opacity="1.0" stroke="#e5484d" stroke-width="1.5"/>
<text x="488" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L5</text>
<rect x="514" y="246" width="44" height="24" fill="#e5484d" fill-opacity="1.0" stroke="#e5484d" stroke-width="1.5"/>
<text x="536" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L5</text>
<rect x="562" y="246" width="44" height="24" fill="#e5484d" fill-opacity="1.0" stroke="#e5484d" stroke-width="1.5"/>
<text x="584" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L5</text>
<rect x="610" y="246" width="44" height="24" fill="#e5484d" fill-opacity="1.0" stroke="#e5484d" stroke-width="1.5"/>
<text x="632" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L5</text>
<rect x="658" y="246" width="44" height="24" fill="#e5484d" fill-opacity="1.0" stroke="#e5484d" stroke-width="1.5"/>
<text x="680" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L5</text>
<rect x="706" y="246" width="44" height="24" fill="#e5484d" fill-opacity="1.0" stroke="#e5484d" stroke-width="1.5"/>
<text x="728" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L5</text>
<rect x="754" y="246" width="44" height="24" fill="#e5484d" fill-opacity="1.0" stroke="#e5484d" stroke-width="1.5"/>
<text x="776" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L5</text>
<rect x="802" y="246" width="44" height="24" fill="#e5484d" fill-opacity="1.0" stroke="#e5484d" stroke-width="1.5"/>
<text x="824" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L5</text>
<rect x="850" y="246" width="44" height="24" fill="#e5484d" fill-opacity="1.15" stroke="#e5484d" stroke-width="1.5"/>
<text x="872" y="263" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">L6</text>
</g>
<rect x="30" y="306" width="900" height="150" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="296" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 半径ごとの、読み込み回数</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1198;0.1200;1.0000" values="0;0;1;1"/><text x="44" y="354" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">半径 4</text>
<rect x="130" y="340" width="3" height="10" fill="#e5484d" opacity="0.85"/>
<text x="138.126953125" y="350" text-anchor="start" style="font-size:11px;font-weight:700;fill:#e5484d">全部読むなら 64</text>
<rect x="130" y="352" width="3" height="9" fill="#2ea043" opacity="0.9"/>
<text x="141" y="361" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2ea043">SAO 16</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3243;0.3244;1.0000" values="0;0;1;1"/><text x="44" y="380" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">半径 16</text>
<rect x="130" y="366" width="3" height="10" fill="#e5484d" opacity="0.85"/>
<text x="140.03125" y="376" text-anchor="start" style="font-size:11px;font-weight:700;fill:#e5484d">全部読むなら 1,024</text>
<rect x="130" y="378" width="3" height="9" fill="#2ea043" opacity="0.9"/>
<text x="141" y="387" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2ea043">SAO 16</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5287;0.5289;1.0000" values="0;0;1;1"/><text x="44" y="406" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">半径 64</text>
<rect x="130" y="392" width="32.5" height="10" fill="#e5484d" opacity="0.85"/>
<text x="170.5" y="402" text-anchor="start" style="font-size:11px;font-weight:700;fill:#e5484d">全部読むなら 16,384</text>
<rect x="130" y="404" width="3" height="9" fill="#2ea043" opacity="0.9"/>
<text x="141" y="413" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2ea043">SAO 16</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7332;0.7333;1.0000" values="0;0;1;1"/><text x="44" y="432" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">半径 256</text>
<rect x="130" y="418" width="520.0" height="10" fill="#e5484d" opacity="0.85"/>
<text x="658.0" y="428" text-anchor="start" style="font-size:11px;font-weight:700;fill:#e5484d">全部読むなら 262,144</text>
<rect x="130" y="430" width="3" height="9" fill="#2ea043" opacity="0.9"/>
<text x="141" y="439" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2ea043">SAO 16</text>
</g>
<text x="40" y="484" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">サンプル数(画素あたり):</text>
<text x="240" y="488" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1198;0.1200;1.0000" values="1;1;0;0"/></text>
<text x="240" y="488" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">16<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1198;0.1200;0.3243;0.3244;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="488" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">16<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3243;0.3244;0.5287;0.5289;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="488" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">16<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5287;0.5289;0.7332;0.7333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="488" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">16<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7332;0.7333;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8709;0.8711;1.0000" values="0;0;1;1"/><rect x="360" y="468" width="570" height="60" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="376" y="492" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">半径 256 でも、サンプル 16 個。全部読むと 262,144 回(約 16384 倍)</text>
<text x="376" y="515" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">遠い層は小さく、キャッシュに収まる。ミップの作り方(平均しない)に注意</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">広い範囲を調べたいが、全部読むのは高い<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">遠いサンプルは、粗いミップから読む(1 テクセルが、広い範囲)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8843;0.8844;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">半径が 64 倍になっても、読む回数は、ほぼ同じ<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8843;0.8844;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:sao-mip:end -->

### どのミップから読むか

<strong>画面上のサンプルまでの距離</strong>（ピクセル）に応じて、ミップを選びます。

<div class="formula">m = clamp( ⌊log₂(距離)⌋ − 定数, 0, 最大ミップ )</div>

参照実装（G3D）ではこの<strong>定数</strong>（`LOG_MAX_OFFSET`）が 3 です。<strong>距離が 8 ピクセル以内ならミップ 0</strong>、16 ピクセルまでミップ 1、…と距離が 2 倍になるごとに、ミップが 1 つ上がります。

```hlsl
int MipLevel(float screen_distance) {
  return clamp(int(floor(log2(screen_distance))) - kLogMaxOffset, 0, kMaxMip);
}

float3 SamplePosition(float2 uv, int mip) {
  float z = z_mip_tex.SampleLevel(point_sampler, uv, mip).r;
  return ViewPositionFromLinearZ(uv, z);
}
```

## ミップの作り方：平均してはいけない

深度のミップは、<strong>普通のミップ（4 画素の平均）で作ってはいけません</strong>。<strong>物体の境界</strong>で手前の画素と奥の画素を平均すると、どちらにも存在しない、中間の深度ができます。この嘘の深度が、AO で幽霊のような遮蔽を作ります。

手前の物体の画素（深度 2 m）と、その背後の壁の画素（深度 10 m）を平均すると、6 m という値ができます。ところが、画面のその場所には、6 m の所に面は存在しません。この<strong>存在しない面</strong>が、AO の計算のとき、サンプルを遮る幽霊のような遮蔽物として働きます。

そこで、SAO は 4 画素の中から<strong>実在する 1 画素を選ぶ</strong>方法を採ります（ポイント サンプリングで縮小）。選ばれた値は必ずどこかに実在する深度なので、境界で嘘の深度が生まれません。最小値（最も手前）を取る方法もあり、遮蔽を多めに見る安全側の選択ですが、手前の細い物が太く見えるという副作用があります。最大値（最も奥）を取る方法はその逆で、遮蔽を少なめに見ます。

SAO の方式は、<strong>代表の 1 点を選ぶ</strong>だけで、各ミップは前のミップから 1 パスで作れます。

```hlsl
float MipDown(float2 uv_in_src) {
  return src_tex.Load(int3(2 * pixel, src_mip)).r;
}
```

## 位置と法線を深度から復元する

SAO は、<strong>G-Buffer の法線を使いません</strong>。<strong>深度だけ</strong>から、位置と法線を復元します。

<strong>位置</strong>は、線形深度 z と画面上の位置から計算します。画面の座標 (ndc_x, ndc_y) を −1〜1 で表すと、`x = ndc_x · z · tanX`、`y = ndc_y · z · tanY` です（tanX・tanY は視野角の半分の tan。[Crytek SSAO](ssao-crytek.md)）。

<strong>法線</strong>は、隣の画素の位置との差を 2 本とって外積を取れば求まります。ここでの工夫は、左右・上下のうち<strong>深度の差が小さい側</strong>を選ぶことです。物体の輪郭では、片側が別の面になっていて、そちらを使うと法線が大きくずれます。差が小さいほうは、同じ面の側である可能性が高いからです。

<strong>精度</strong>も大切です。復元した位置の誤差は、そのまま AO の縞になります。深度は 32 ビット浮動小数点で持つか、上位・下位の 2 チャンネルに分けて高精度に保存します。

```hlsl
float3 ReconstructNormal(int2 pixel, float3 c) {
  float3 px = Position(pixel + int2(1, 0));
  float3 nx = Position(pixel + int2(-1, 0));
  float3 py = Position(pixel + int2(0, 1));
  float3 ny = Position(pixel + int2(0, -1));

  float3 dx = abs(px.z - c.z) < abs(nx.z - c.z) ? px - c : c - nx;
  float3 dy = abs(py.z - c.z) < abs(ny.z - c.z) ? py - c : c - ny;
  return normalize(cross(dx, dy));
}
```

!!! info "ここで使われる「積分」を、やさしく言うと"
    SAO は、<strong>Alchemy AO と同じ式</strong>（周りの点ごとの寄与を足す）を使います。違いは、<strong>「点を、どこから読むか」</strong>だけです。

    - 遠い点は、細かく読んでも、AO に、ほとんど効かない。
    - そこで、遠い点は、<strong>深度のミップ マップ</strong>（縮小した深度）から読む。メモリを、読む量が減り、半径が大きくても、遅くならない。

    積分（足し算）の中身は、同じで、<strong>足す材料の、読み方だけを速くした</strong>方式です。

    <strong>数式を使わない、くわしい説明</strong>は [Integrals and Elevation Angles in Plain Words](theory/integral-intuition.md) です。

## 処理の流れ

SAO は 5 つのパスで構成されます。

最初に、深度バッファを<strong>線形深度</strong>に変換し、同時にミップ チェーンを作ります。次に、AO を計算します。各画素で螺旋状にサンプルを置き、サンプルまでの画面上の距離に応じたミップから深度を読み、Alchemy の式で足し合わせます。その後、バイラテラル ブラーを横方向、縦方向の順に 2 回かけて、ノイズを消します。バイラテラル ブラーは 2 次元のぼかしを縦横の 1 次元に分けた（分離可能）形で、コストを大幅に減らします。最後に、結果を間接光に掛けて合成します。

論文には、実装の細かい最適化もあります。AO の結果と深度を、1 枚のテクスチャのチャンネルに<strong>詰めて</strong>保存し、ブラーのパスでテクスチャを読む回数を減らします。1 回のテクスチャ読み込みで、AO と深度の両方が手に入るためです。メモリ帯域が律速になる処理では、こういう工夫の積み重ねが効きます。

## 性能の特徴

SAO のコストは、主に 3 つで決まります。サンプル数に比例して増えます（9〜13 個が目安）。画素数に比例して増えます（半分の解像度で計算すれば、さらに軽くなります。[低解像度のエフェクト](../../rendering/low-res-effects.md)）。そして、<strong>半径にはほぼ依存しません</strong>。これが「スケーラブル」の意味です。ブラーは分離可能なので、コストは小さいです。

## Alchemy AO との比較

AO の式そのものは Alchemy AO と同じで、変わったのは「読み方」だけです。Alchemy AO は常にミップ 0（フル解像度）の深度を読みます。SAO は距離に応じて粗いミップを読むので、半径を大きくしてもコストがほぼ一定です。法線も、G-Buffer に頼らず、深度だけから高精度に復元できます。ほかにも、キャッシュ、パッキング、ブラーの最適化など、実装面の工夫を多く入れています。

## 弱点

式が Alchemy のままなので、ハロー、薄い物、画面外といった[スクリーン空間 AO の共通の弱点](artifacts/index.md)は、そのまま残ります。

粗いミップを使うことによる弱点もあります。遠くの細かい遮蔽は、粗い深度では取りこぼします。半径が大きい場合に目立ちます。また、代表の 1 点を選ぶ方式は、カメラが動くと選ばれる画素が切り替わり、縮小した深度が<strong>ちらつく</strong>ことがあります（[Noise, Banding and Flicker](artifacts/noise-flicker.md)）。コサイン重みも近似なので、[GTAO](gtao.md) のような正確な積分ではありません。

## より良いやり方

SAO の「深度のミップ」の発想は、その後の多くの実装に受け継がれています。最近の実装は、深度のミップを Hi-Z（階層化深度バッファ）として使い回します。シーンの他の処理（SSR のレイ マーチ、カリング）と共有できるためです（[Hi-Z とスクリーン空間トレース](../../rendering/hiz.md)）。また、精度を重視するなら、SAO の速さの工夫に GTAO の積分を組み合わせた構成を取ります（実際、XeGTAO は深度のミップ チェーンに、GTAO の積分を載せています）。

## よくあるミス

??? failure "深度のミップを、通常の平均で作って、境界にゴーストが出る"
    <strong>代表の 1 点を選ぶ</strong>（または最小・最大）方式で作ります。

??? failure "非線形の深度のまま、ミップを作る"
    <strong>線形深度（ビュー空間の z）</strong>に変換してから、ミップを作ります。

??? failure "ミップの選び方を、サンプルの 3D 距離でなく、サンプルの番号で決める"
    <strong>画面上の距離（ピクセル）</strong>で選びます。

??? failure "16 ビットの深度で、平らな面に縞が出る"
    32 ビットの浮動小数点か、<strong>2 チャンネルに分けて</strong>精度を確保します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SAO ＝ <strong>Alchemy AO の式 ＋ 深度のミップ チェーン</strong>
    - [x] <strong>遠いサンプルは、粗いミップから</strong>読み、<strong>キャッシュを効かせる</strong>。<strong>半径に依存しない速さ</strong>
    - [x] ミップは<strong>平均せず、代表の 1 点</strong>で作る（境界のゴースト防止）
    - [x] <strong>深度だけから</strong>、位置と法線を復元（G-Buffer 不要）
    - [x] <strong>後の多くの SSAO 実装に影響</strong>した方式

## 参考

- McGuire, Mara, Luebke, "Scalable Ambient Obscurance", High-Performance Graphics 2012
- McGuire, Osman, Bukowski, Hennessy, "The Alchemy Screen-Space Ambient Obscurance Algorithm", High-Performance Graphics 2011
- Bavoil, Sainz, Dimitrov, "Image-Space Horizon-Based Ambient Occlusion", SIGGRAPH 2008 Talks

## 関連ページ

- [Ambient Occlusion (AO)](index.md)
- [Alchemy AO](alchemy-ao.md)
- [HBAO](hbao.md)
- [AO Filtering](filtering/index.md)
- [縮小バッファの効果](../../rendering/low-res-effects.md)
- [Hi-Z とスクリーン空間トレース](../../rendering/hiz.md)
