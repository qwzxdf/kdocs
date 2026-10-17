---
title: シャドウ マップの基礎
tags:
  - 描画
---

# シャドウ マップの基礎

**シャドウ マップ**（Shadow Mapping）は、1978 年に Williams が提案した方式で、現在も**最も使われている影の方式**です。発想は単純です。<strong>光源から見て、各方向で「一番手前の面までの距離」</strong>を、あらかじめ<strong>画像（深度マップ）</strong>に撮っておきます。<strong>画面の点が光から見て、その一番手前より奥にあれば、遮られている（影）</strong>、**一番手前なら、光が当たっている**。**深度を比べる**だけで**あらゆる形の影**が作れます。

!!! tip "ポイント"
    - <strong>パス 1</strong>：<strong>光源の視点から、シーンの深度だけを描く</strong>（シャドウ マップ）。
    - <strong>パス 2</strong>：<strong>通常の描画</strong>で各点を<strong>光の座標に変換</strong>し、<strong>シャドウ マップの深度と比べる</strong>。
    - 比べるとき、<strong>光から見た、その点の深度 ＞ マップの深度</strong>なら、影。
    - 平行光（太陽）は<strong>正射影</strong>、スポットライトは<strong>透視投影</strong>、点光源は<strong>6 面（キューブ）</strong>。
    - <strong>比較サンプラー（`SampleCmp`）</strong>で、ハードウェアが比較と、2×2 の補間を一度に行う。
    - 課題：<strong>解像度（エイリアシング）・バイアス・縁のぼかし</strong>。

## 原理

<svg class="fig illust" viewBox="0 0 780 290" role="img" aria-label="シャドウ マップの原理">
<text x="20" y="24" class="fig-title">光から見た一番手前の深度（シャドウ マップ）と、点の深度を比べる</text>
<circle cx="90" cy="130" r="11" fill="#e5a828"/><text x="70" y="112" style="font-size:12px">光源</text>
<rect x="320" y="90" width="26" height="80" fill="rgba(150,150,150,0.6)" stroke="currentColor" stroke-width="2"/><text x="300" y="82" style="font-size:12px">遮蔽物</text>
<line x1="40" y1="250" x2="740" y2="250" stroke="currentColor" stroke-width="4"/>
<line x1="90" y1="130" x2="320" y2="95" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="90" y1="130" x2="320" y2="165" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="90" y1="130" x2="200" y2="250" stroke="#2ea043" stroke-width="2.5"/>
<circle cx="200" cy="250" r="6" fill="#2ea043"/><text x="150" y="272" style="font-size:12px;fill:#2ea043;font-weight:700">日向（光から一番手前）</text>
<line x1="346" y1="125" x2="470" y2="250" stroke="#e5484d" stroke-width="2.5"/>
<circle cx="470" cy="250" r="6" fill="#e5484d"/><text x="400" y="272" style="font-size:12px;fill:#e5484d;font-weight:700">影（手前に遮蔽物がある）</text>
<text x="500" y="110" style="font-weight:700">シャドウ マップ ＝ 各方向の</text>
<text x="500" y="132" style="font-weight:700">「光から一番手前の面」までの深度</text>
<text x="500" y="164" style="font-size:12px">点の深度 ＞ マップの深度 → 遮られている（影）</text>
<text x="500" y="184" style="font-size:12px">点の深度 ≦ マップの深度 → 光が当たっている</text>
</svg>

<!-- fig:shadow-map-probe:begin -->

<svg class="fig illust motion" data-fig="shadow-map-probe" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-shadow-map-probe" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">シャドウ マップ:光から見た最短の深度と比べて、影かどうかを決める</text>
<line x1="40" y1="320" x2="740" y2="320" stroke="#1f2937" stroke-width="3"/>
<rect x="330" y="210" width="70" height="52" fill="#b8794b" stroke="#7a4b2a" stroke-width="2"/>
<circle cx="110" cy="112" r="14" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<text x="132" y="117" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">光</text>
<line x1="110" y1="112" x2="150.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="150.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="165.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0619;0.0621;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="165.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0619;0.0621;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="180.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0669;0.0671;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="180.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0669;0.0671;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="195.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0719;0.0721;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="195.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0719;0.0721;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="210.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0769;0.0771;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="210.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0769;0.0771;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="225.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0819;0.0821;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="225.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0819;0.0821;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="240.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0869;0.0871;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="240.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0869;0.0871;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="255.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0919;0.0921;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="255.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0919;0.0921;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="270.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0969;0.0971;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="270.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.0969;0.0971;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="285.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1019;0.1021;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="285.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1019;0.1021;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="300.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1069;0.1071;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="300.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1069;0.1071;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="315.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1119;0.1121;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="315.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1119;0.1121;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="330.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1169;0.1171;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="330.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1169;0.1171;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="345.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1219;0.1221;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="345.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1219;0.1221;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="360.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1269;0.1271;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="360.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1269;0.1271;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="375.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1319;0.1321;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="375.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1319;0.1321;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="390.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1369;0.1371;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="390.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1369;0.1371;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="405.0" y2="320.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1419;0.1421;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="405.0" cy="320.0" r="3.5" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1419;0.1421;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="330.0" y2="259.61" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1469;0.1471;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="330.0" cy="259.61" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1469;0.1471;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="330.0" y2="252.8" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1519;0.1521;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="330.0" cy="252.8" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1519;0.1521;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="330.0" y2="246.59" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1569;0.1571;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="330.0" cy="246.59" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1569;0.1571;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="330.0" y2="240.9" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1619;0.1621;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="330.0" cy="240.9" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1619;0.1621;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="330.0" y2="235.68" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1669;0.1671;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="330.0" cy="235.68" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1669;0.1671;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="330.0" y2="230.86" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1719;0.1721;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="330.0" cy="230.86" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1719;0.1721;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="330.0" y2="226.4" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1769;0.1771;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="330.0" cy="226.4" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1769;0.1771;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="330.0" y2="222.27" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1819;0.1821;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="330.0" cy="222.27" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1819;0.1821;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="330.0" y2="218.42" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1869;0.1871;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="330.0" cy="218.42" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1869;0.1871;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="330.0" y2="214.83" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1919;0.1921;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="330.0" cy="214.83" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1919;0.1921;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="330.0" y2="211.48" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1969;0.1971;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="330.0" cy="211.48" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.1969;0.1971;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="333.8" y2="210.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2019;0.2021;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="333.8" cy="210.0" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2019;0.2021;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="340.87" y2="210.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2069;0.2071;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="340.87" cy="210.0" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2069;0.2071;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="347.93" y2="210.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2119;0.2121;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="347.93" cy="210.0" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2119;0.2121;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="355.0" y2="210.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2169;0.2171;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="355.0" cy="210.0" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2169;0.2171;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="362.07" y2="210.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2221;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="362.07" cy="210.0" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2221;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="369.13" y2="210.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2269;0.2271;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="369.13" cy="210.0" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2269;0.2271;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="376.2" y2="210.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2319;0.2321;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="376.2" cy="210.0" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2319;0.2321;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="383.27" y2="210.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2369;0.2371;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="383.27" cy="210.0" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2369;0.2371;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="390.34" y2="210.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2419;0.2421;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="390.34" cy="210.0" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2419;0.2421;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<line x1="110" y1="112" x2="397.4" y2="210.0" stroke="#e5aa28" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2469;0.2471;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></line>
<circle cx="397.4" cy="210.0" r="3.5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.2469;0.2471;0.2854;0.2857;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="150" cy="320" r="8" fill="#ffffff" stroke="#1f2937" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3140;0.3143;0.8926;0.8929;1.0000" values="0;0;1;1;0;0"/><animate attributeName="cx" dur="14s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3143;0.3264;0.3386;0.3507;0.3629;0.3750;0.3871;0.3993;0.4114;0.4236;0.4357;0.4479;0.4600;0.4721;0.4843;0.4964;0.5086;0.5207;0.5329;0.5450;0.5571;0.5693;0.5814;0.5936;0.6057;0.6179;0.6300;0.6421;0.6543;0.6664;0.6786;0.6907;0.7029;0.7150;0.7271;0.7393;0.7514;0.7636;0.7757" values="150;150;165;180;195;210;225;240;255;270;285;300;315;330;345;360;375;390;405;420;435;450;465;480;495;510;525;540;555;570;585;600;615;630;645;660;675;690;705;720"/></circle>
<line x1="110" y1="112" x2="150" y2="320" stroke="#e5aa28" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3140;0.3143;0.8926;0.8929;1.0000" values="0;0;1;1;0;0"/><animate attributeName="x2" dur="14s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3143;0.3264;0.3386;0.3507;0.3629;0.3750;0.3871;0.3993;0.4114;0.4236;0.4357;0.4479;0.4600;0.4721;0.4843;0.4964;0.5086;0.5207;0.5329;0.5450;0.5571;0.5693;0.5814;0.5936;0.6057;0.6179;0.6300;0.6421;0.6543;0.6664;0.6786;0.6907;0.7029;0.7150;0.7271;0.7393;0.7514;0.7636;0.7757" values="150;150;165;180;195;210;225;240;255;270;285;300;315;330;345;360;375;390;405;420;435;450;465;480;495;510;525;540;555;570;585;600;615;630;645;660;675;690;705;720"/><animate attributeName="stroke" dur="14s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3143;0.3264;0.3386;0.3507;0.3629;0.3750;0.3871;0.3993;0.4114;0.4236;0.4357;0.4479;0.4600;0.4721;0.4843;0.4964;0.5086;0.5207;0.5329;0.5450;0.5571;0.5693;0.5814;0.5936;0.6057;0.6179;0.6300;0.6421;0.6543;0.6664;0.6786;0.6907;0.7029;0.7150;0.7271;0.7393;0.7514;0.7636;0.7757" values="#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5aa28;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d"/></line>
<rect x="142.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3140;0.3143;1.0000" values="0;0;1;1"/></rect>
<rect x="157.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3261;0.3264;1.0000" values="0;0;1;1"/></rect>
<rect x="172.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3383;0.3386;1.0000" values="0;0;1;1"/></rect>
<rect x="187.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3504;0.3507;1.0000" values="0;0;1;1"/></rect>
<rect x="202.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3626;0.3629;1.0000" values="0;0;1;1"/></rect>
<rect x="217.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3747;0.3750;1.0000" values="0;0;1;1"/></rect>
<rect x="232.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3869;0.3871;1.0000" values="0;0;1;1"/></rect>
<rect x="247.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3990;0.3993;1.0000" values="0;0;1;1"/></rect>
<rect x="262.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4111;0.4114;1.0000" values="0;0;1;1"/></rect>
<rect x="277.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4233;0.4236;1.0000" values="0;0;1;1"/></rect>
<rect x="292.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4354;0.4357;1.0000" values="0;0;1;1"/></rect>
<rect x="307.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4476;0.4479;1.0000" values="0;0;1;1"/></rect>
<rect x="322.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4597;0.4600;1.0000" values="0;0;1;1"/></rect>
<rect x="337.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4719;0.4721;1.0000" values="0;0;1;1"/></rect>
<rect x="352.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4840;0.4843;1.0000" values="0;0;1;1"/></rect>
<rect x="367.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4961;0.4964;1.0000" values="0;0;1;1"/></rect>
<rect x="382.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5083;0.5086;1.0000" values="0;0;1;1"/></rect>
<rect x="397.5" y="316" width="15" height="8" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5204;0.5207;1.0000" values="0;0;1;1"/></rect>
<rect x="412.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5326;0.5329;1.0000" values="0;0;1;1"/></rect>
<rect x="427.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5447;0.5450;1.0000" values="0;0;1;1"/></rect>
<rect x="442.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5569;0.5571;1.0000" values="0;0;1;1"/></rect>
<rect x="457.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5690;0.5693;1.0000" values="0;0;1;1"/></rect>
<rect x="472.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5811;0.5814;1.0000" values="0;0;1;1"/></rect>
<rect x="487.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5933;0.5936;1.0000" values="0;0;1;1"/></rect>
<rect x="502.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6054;0.6057;1.0000" values="0;0;1;1"/></rect>
<rect x="517.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6176;0.6179;1.0000" values="0;0;1;1"/></rect>
<rect x="532.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6297;0.6300;1.0000" values="0;0;1;1"/></rect>
<rect x="547.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6419;0.6421;1.0000" values="0;0;1;1"/></rect>
<rect x="562.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6540;0.6543;1.0000" values="0;0;1;1"/></rect>
<rect x="577.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6661;0.6664;1.0000" values="0;0;1;1"/></rect>
<rect x="592.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6783;0.6786;1.0000" values="0;0;1;1"/></rect>
<rect x="607.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6904;0.6907;1.0000" values="0;0;1;1"/></rect>
<rect x="622.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.7026;0.7029;1.0000" values="0;0;1;1"/></rect>
<rect x="637.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.7147;0.7150;1.0000" values="0;0;1;1"/></rect>
<rect x="652.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.7269;0.7271;1.0000" values="0;0;1;1"/></rect>
<rect x="667.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.7390;0.7393;1.0000" values="0;0;1;1"/></rect>
<rect x="682.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.7511;0.7514;1.0000" values="0;0;1;1"/></rect>
<rect x="697.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.7633;0.7636;1.0000" values="0;0;1;1"/></rect>
<rect x="712.5" y="316" width="15" height="8" fill="#334155" opacity="0"><animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.7754;0.7757;1.0000" values="0;0;1;1"/></rect>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 21.2　シャドウ マップの値 m = 21.2　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3140;0.3143;0.3261;0.3264;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 21.5　シャドウ マップの値 m = 21.5　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3261;0.3264;0.3383;0.3386;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 21.9　シャドウ マップの値 m = 21.9　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3383;0.3386;0.3504;0.3507;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 22.5　シャドウ マップの値 m = 22.5　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3504;0.3507;0.3626;0.3629;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 23.1　シャドウ マップの値 m = 23.1　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3626;0.3629;0.3747;0.3750;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 23.8　シャドウ マップの値 m = 23.8　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3747;0.3750;0.3869;0.3871;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 24.5　シャドウ マップの値 m = 24.5　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3869;0.3871;0.3990;0.3993;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 25.4　シャドウ マップの値 m = 25.4　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3990;0.3993;0.4111;0.4114;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 26.2　シャドウ マップの値 m = 26.2　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4111;0.4114;0.4233;0.4236;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 27.2　シャドウ マップの値 m = 27.2　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4233;0.4236;0.4354;0.4357;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 28.2　シャドウ マップの値 m = 28.2　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4354;0.4357;0.4476;0.4479;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 29.2　シャドウ マップの値 m = 29.2　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4476;0.4479;0.4597;0.4600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 30.3　シャドウ マップの値 m = 30.3　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4597;0.4600;0.4719;0.4721;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 31.4　シャドウ マップの値 m = 31.4　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4719;0.4721;0.4840;0.4843;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 32.5　シャドウ マップの値 m = 32.5　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4840;0.4843;0.4961;0.4964;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 33.7　シャドウ マップの値 m = 33.7　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.4961;0.4964;0.5083;0.5086;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 34.9　シャドウ マップの値 m = 34.9　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5083;0.5086;0.5204;0.5207;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 36.1　シャドウ マップの値 m = 36.1　→ d = m なので光が当たる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5204;0.5207;0.5326;0.5329;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 37.3　シャドウ マップの値 m = 26.5　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5326;0.5329;0.5447;0.5450;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 38.6　シャドウ マップの値 m = 26.1　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5447;0.5450;0.5569;0.5571;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 39.9　シャドウ マップの値 m = 25.8　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5569;0.5571;0.5690;0.5693;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 41.1　シャドウ マップの値 m = 25.5　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5690;0.5693;0.5811;0.5814;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 42.4　シャドウ マップの値 m = 25.2　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5811;0.5814;0.5933;0.5936;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 43.8　シャドウ マップの値 m = 25.0　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.5933;0.5936;0.6054;0.6057;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 45.1　シャドウ マップの値 m = 24.8　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6054;0.6057;0.6176;0.6179;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 46.4　シャドウ マップの値 m = 24.6　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6176;0.6179;0.6297;0.6300;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 47.8　シャドウ マップの値 m = 24.4　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6297;0.6300;0.6419;0.6421;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 49.1　シャドウ マップの値 m = 24.3　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6419;0.6421;0.6540;0.6543;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 50.5　シャドウ マップの値 m = 24.1　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6540;0.6543;0.6661;0.6664;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 51.9　シャドウ マップの値 m = 24.4　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6661;0.6664;0.6783;0.6786;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 53.2　シャドウ マップの値 m = 25.1　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6783;0.6786;0.6904;0.6907;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 54.6　シャドウ マップの値 m = 25.7　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.6904;0.6907;0.7026;0.7029;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 56.0　シャドウ マップの値 m = 26.4　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.7026;0.7029;0.7147;0.7150;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 57.4　シャドウ マップの値 m = 27.0　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.7147;0.7150;0.7269;0.7271;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 58.8　シャドウ マップの値 m = 27.7　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.7269;0.7271;0.7390;0.7393;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 60.2　シャドウ マップの値 m = 28.4　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.7390;0.7393;0.7511;0.7514;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 61.6　シャドウ マップの値 m = 29.0　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.7511;0.7514;0.7633;0.7636;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 63.0　シャドウ マップの値 m = 29.7　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.7633;0.7636;0.7754;0.7757;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">この点までの距離 d = 64.4　シャドウ マップの値 m = 30.4　→ d &gt; m なので影<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.7754;0.7757;0.8926;0.8929;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">① 光から見て、各方向で一番近い物までの距離を記録する（シャドウ マップ）<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3140;0.3143;1.0000" values="1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">② 画面の点を光から見た距離と、記録された距離で比べる<animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0.0000;0.3140;0.3143;0.8926;0.8929;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="402" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">記録より遠ければ（間に何かある）影、同じなら光が当たる。</text>
</svg>

<!-- fig:shadow-map-probe:end -->

## 手順

| 手順 | 内容 |
| --- | --- |
| **① 光のビュー・射影行列を作る** | 光の位置・向きから、**ビュー**と**射影**（平行光は正射影） |
| **② シャドウ マップを描く** | 光の視点から、**影を落とす物体**の深度だけを描く（**ピクセルシェーダーなし**） |
| **③ 通常の描画で光の座標に変換** | 各ピクセルの**ワールド位置**を、**光のクリップ空間**へ |
| **④ シャドウ マップを引く** | 変換した <strong>(u, v)</strong> で、保存された深度を読む |
| **⑤ 深度を比べる** | <strong>自分の深度（光から見た）</strong>が、**保存された深度より奥**なら、影 |

## ① 光の行列

### 平行光（太陽）：正射影

平行光は**光が全て平行**なので**正射影**（遠近感なし）で撮ります。**光の向き**を前方向にして、**シーンの範囲（影を落とす物・受ける物）を覆う箱**を決めます。

```cpp
Matrix LightViewProjection(const Vector3& light_dir, const Vector3& center, float radius) {
  Vector3 light_pos = center - light_dir * radius * 2.0f;
  Matrix view = XMMatrixLookAtLH(light_pos, center, Vector3::Up);
  Matrix proj = XMMatrixOrthographicLH(radius * 2.0f, radius * 2.0f, 0.0f, radius * 4.0f);
  return view * proj;
}
```

| 点 | 説明 |
| --- | --- |
| **光の位置** | **シーンの中心から、光の逆向きに十分に離れた所**。平行光では位置は本質的ではないが、**ビュー行列を作るため**に必要 |
| **正射影の大きさ** | 影を受ける範囲を覆う。**大きいほど、1 テクセルが粗い**（エイリアシング） |
| **近・遠クリップ** | 影を落とす物体が範囲内に入るように |
| **上方向 `Up`** | 光の向きと平行だと破綻する（真上からの光）。別の軸を使う |

### スポットライト：透視投影

**スポットライト**は、**一点から円錐状**に光が出るので、**透視投影**で撮ります。**視野角**はスポットの**円錐の角度**に合わせます。

### 点光源：キューブマップ

**全方向**に光が出るので<strong>6 方向（キューブマップ）</strong>で撮ります（[点光源・スポットライトの影](local-lights.md)）。

## ② シャドウ マップを描く

**深度だけ**を描きます。**ピクセルシェーダーは不要**（アルファ テストする物を除く）で、**非常に速い**描画です。

```cpp
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = 2048;
desc.Height = 2048;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R32_TYPELESS;
desc.SampleDesc.Count = 1;
desc.BindFlags = D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &shadow_tex);

D3D11_DEPTH_STENCIL_VIEW_DESC dsv_desc = {};
dsv_desc.Format = DXGI_FORMAT_D32_FLOAT;
dsv_desc.ViewDimension = D3D11_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(shadow_tex, &dsv_desc, &shadow_dsv);

D3D11_SHADER_RESOURCE_VIEW_DESC srv_desc = {};
srv_desc.Format = DXGI_FORMAT_R32_FLOAT;
srv_desc.ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D;
srv_desc.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(shadow_tex, &srv_desc, &shadow_srv);
```

| 点 | 説明 |
| --- | --- |
| **`R32_TYPELESS`** | **深度として書き、シェーダーから読む**ため、型なしで作る |
| **DSV は `D32_FLOAT`、SRV は `R32_FLOAT`** | 同じ領域を、2 通りに見る |
| **解像度** | 1024〜4096。**大きいほど細かい影・メモリと帯域を食う**（[メモリ帯域幅](../../rendering/bandwidth.md)） |
| **フォーマット** | 16 ビットで足りることも多い（精度を許容できれば、帯域が半分） |
| **描画する物** | **影を落とす物だけ**。**ライティングなし**のシェーダー（頂点シェーダーのみ） |

## ③〜⑤ 比較

**ワールド位置**を**光のクリップ空間**に変換し、**シャドウ マップの座標と深度**を得ます。

```hlsl
float ShadowFactor(float3 world_pos) {
  float4 light_clip = mul(float4(world_pos, 1.0), light_view_projection);
  float3 ndc = light_clip.xyz / light_clip.w;

  float2 uv = ndc.xy * float2(0.5, -0.5) + 0.5;
  float depth = ndc.z - bias;

  if (any(uv < 0.0) || any(uv > 1.0) || ndc.z > 1.0) return 1.0;

  return shadow_tex.SampleCmpLevelZero(shadow_sampler, uv, depth);
}
```

| 点 | 説明 |
| --- | --- |
| **`ndc.xy * (0.5, −0.5) + 0.5`** | NDC（−1〜1、y は上向き）を、テクスチャ座標（0〜1、v は下向き）に |
| **`depth = ndc.z − bias`** | **バイアス**で自己影を防ぐ（[バイアス](bias.md)） |
| **範囲外** | シャドウ マップの外は、**影なし**（1）として扱う（または別の扱い） |
| **`SampleCmpLevelZero`** | **比較サンプラー**。**比較して、結果（0〜1）を、2×2 でバイリニア補間** |

### 比較サンプラー

**比較サンプラー**は、**ハードウェアが「保存された深度」と「参照値」を比べる**機能です。結果は**比較が真なら 1、偽なら 0**で**バイリニアで補間**されます（4 点の比較結果を混ぜる）。

```cpp
D3D11_SAMPLER_DESC sampler = {};
sampler.Filter = D3D11_FILTER_COMPARISON_MIN_MAG_LINEAR_MIP_POINT;
sampler.AddressU = sampler.AddressV = sampler.AddressW = D3D11_TEXTURE_ADDRESS_BORDER;
sampler.BorderColor[0] = sampler.BorderColor[1] = sampler.BorderColor[2] = sampler.BorderColor[3] = 1.0f;
sampler.ComparisonFunc = D3D11_COMPARISON_LESS_EQUAL;
device->CreateSamplerState(&sampler, &shadow_sampler);
```

| 設定 | 説明 |
| --- | --- |
| **`COMPARISON_..._LINEAR`** | 4 点の比較結果を**線形補間**（これが最も簡単な PCF） |
| **`ComparisonFunc = LESS_EQUAL`** | **参照値 ≦ 保存された深度**なら 1（光が当たる） |
| **アドレス モード：BORDER、色 1.0** | シャドウ マップの外は、<strong>影なし（1）</strong> |

!!! note "標準 Z のとき"
    標準の Z（near → 0、far → 1）では**遠いほど深度が大きい**ので、`LESS_EQUAL` を使います。**reverse-Z** のときは、`GREATER_EQUAL` です（[投影](../../3d/projection.md)）。

## 問題の整理

| 問題 | 症状 | 原因 | 対策 |
| --- | --- | --- | --- |
| **シャドウ アクネ** | 面に縞・斑点 | 深度の離散化で**自分自身を遮蔽物と誤判定** | [バイアス](bias.md) |
| **ピーター パンニング** | 影が物体から**浮く** | バイアスが大きすぎる | バイアスの調整・法線オフセット |
| **エイリアシング** | 影の縁が**ギザギザ** | シャドウ マップの解像度が足りない | [カスケード](cascaded.md)・高解像度・フィルタ |
| **縁がハード** | 影の縁がくっきりしすぎ | 点での比較（0/1）だけ | [PCF](pcf.md)・[PCSS](pcss.md) |
| **範囲外** | 画面の端で影が途切れる | シャドウ マップの範囲不足 | 範囲の設計・カスケード |
| **透明部分** | 葉・フェンスの影が板状 | 深度だけを描いている | [特殊なケース](special-cases.md) |

## エイリアシングの 2 種類

シャドウ マップは、**解像度が有限**なので**縁がギザギザ**になります。その原因は 2 つに分けられます。

| 種類 | 原因 | 対策 |
| --- | --- | --- |
| **投影エイリアシング** | <strong>光の向きと面の向きが近い（斜め）</strong>と、**1 テクセルが面の上で細長く伸びる** | **スロープ バイアス・面の向きに応じた処理** |
| **遠近エイリアシング** | **カメラの近くは、画面上の 1 ピクセルが、シャドウ マップの 1 テクセルより小さい**（粗く見える）。**遠くは逆に過剰** | <strong>カスケード（距離ごとに分割）</strong>、**射影の工夫**（LiSPSM・TSM など） |

**カメラの近くで細かい影が必要**なのに**マップは全体を均等に**覆っているので、**近くが粗く**、**遠くが無駄**になります。**距離に応じて、解像度を配分**する方式（**カスケード**）が、これを解決します。

## 安定させる：テクセルのスナップ

カメラや光が動くと**シャドウ マップの範囲**が動き、**影の縁がちらつきます**（テクセルの境界がずれるため）。**範囲の位置をテクセル単位に揃える**と、ちらつきが止まります（[カスケード](cascaded.md)）。

## 全体のコード（最小）

```hlsl
Texture2D<float> shadow_tex : register(t5);
SamplerComparisonState shadow_sampler : register(s5);

cbuffer ShadowConstant : register(b3) {
  row_major float4x4 light_view_projection;
  float shadow_bias;
}

float3 Shade(float3 world_pos, float3 N, float3 L, float3 albedo, float3 light_color) {
  float shadow = ShadowFactor(world_pos);
  return albedo * light_color * saturate(dot(N, L)) * shadow;
}
```

## よくあるミス

??? failure "バイアスなしで、平らな面に縞（アクネ）が出る"
    バイアスを入れます（[バイアス](bias.md)）。

??? failure "シャドウ マップを描くときに、表面を描かず、裏面だけを描く（または逆）"
    **カリングの設定**で**表・裏**どちらを描くかを選びます（[バイアス](bias.md)）。

??? failure "比較の向き（`LESS_EQUAL`・`GREATER_EQUAL`）が、reverse-Z と合っていない"
    影が全部ついたり、全部消えたりします。

??? failure "テクスチャ座標の y を反転し忘れて、影が上下逆"
    `uv = ndc.xy * float2(0.5, −0.5) + 0.5`。

??? failure "シャドウ マップの範囲の外が、真っ暗（影）になる"
    ボーダー色を **1.0**（影なし）にします。

??? failure "光や物体が動いて、影の縁がちらつく"
    **テクセルのスナップ**・範囲の安定化をします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] シャドウ マップ ＝ <strong>光から見た深度を撮り、各点を光の座標に変換して、深度を比べる</strong>
    - [x] 平行光は<strong>正射影</strong>、スポットは<strong>透視</strong>、点光源は<strong>キューブ</strong>
    - [x] <strong>比較サンプラー（`SampleCmp`）</strong>で、比較と補間をハードウェアに任せる
    - [x] 課題は<strong>バイアス・エイリアシング（遠近・投影）・縁のぼかし</strong>
    - [x] <strong>カスケード</strong>で距離ごとに解像度を配分。<strong>テクセルのスナップ</strong>でちらつきを止める

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（DirectX ドキュメント）

## 関連ページ

- [影](index.md)
- [バイアス](bias.md)
- [PCF](pcf.md)
- [カスケード シャドウ マップ](cascaded.md)
- [影のコスト（最適化）](../../rendering/shadows.md)
