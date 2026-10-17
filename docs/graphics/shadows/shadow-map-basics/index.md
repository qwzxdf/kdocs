---
title: シャドウ マップの基礎
tags:
  - 描画
---

# シャドウ マップの基礎

**シャドウ マップ**は、**「光から見える一番手前の物までの距離」を画像に記録し、画面の点がそれより遠ければ影**と判定する方式です。**原理が簡単で、GPU に向いている**ので、**現代のリアルタイムの影の土台**です。このセクションでは、**原理と手順・光の行列・深度を描くパス・比較と比較サンプラー・エイリアシングと安定化・最小のコード**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **シャドウ マップ ＝ 光から見た深度の画像**。**画面の点の深度と比べて、遠ければ影**。
    - **手順**：**① 光の行列 → ② 深度を描く → ③ 比べる**。
    - **平行光は正射影、スポットは透視投影、点光源はキューブ マップ**。
    - **アクネ（縞）・ピーター パンニング（浮き）**は**バイアス**で**対処**する。
    - **エイリアシングは 2 種類**（**解像度不足・テクセルの揺れ**）。

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

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [光の行列](light-matrix.md) | 平行光・スポット・点光源の、ビューと射影 |
| [深度を描く](render-depth.md) | 光から見た深度だけのパス・設定 |
| [比較とサンプラー](comparison-sampler.md) | 深度の比較・比較サンプラー（ハードウェア PCF） |
| [エイリアシングと安定化](aliasing-stabilize.md) | 解像度不足・テクセルの揺れ・スナップ |
| [最小のコード](minimal-code.md) | 全体の流れを、最小のコードで通す |

## 動きで見る

<!-- fig:shadow-map-probe:begin -->
<!-- fig:shadow-map-probe:end -->

## よくあるミス

??? failure "影が出ない・全面が影になる"
    **深度の向き（比較の向き）・行列の掛け順・ビューポート**を**確認**する。**RenderDoc でシャドウ マップの中身を見る**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **光から見た深度を撮り、画面の点と比べる**
    - [x] **行列 → 深度パス → 比較**の 3 手順
    - [x] **バイアスとエイリアシング対策が品質の鍵**

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [影](../index.md)
- [バイアス](../bias/index.md)
- [PCF](../pcf.md)
