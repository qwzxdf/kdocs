---
title: MSAA
tags:
  - 描画
---

# MSAA

<strong>MSAA（マルチサンプル アンチエイリアス）</strong>は、**三角形の縁だけを、1 画素に複数のサンプル点で判定して、滑らかにする**方式です。**ピクセル シェーダーは 1 画素につき 1 回だけ**走るので、**画素を全部 4 倍や 8 倍に増やす SSAA より、はるかに安い**のに**ジオメトリの縁のジャギーはしっかり消せます**。ただし、**シェーダー内のエイリアシングには効かず、ディファード レンダリングとは相性が悪い**という**弱点**があります。このページでは、**SSAA との違い・サンプル パターン・カバレッジとリゾルブ・DX11 の設定・弱点と対処**を説明します。

!!! tip "ポイント"
    - MSAA ＝ <strong>1 画素に複数のサンプル点（2・4・8）</strong>。<strong>三角形が各サンプルを覆うかを判定</strong>。
    - <strong>ピクセル シェーダーは 1 画素 1 回</strong>。<strong>覆ったサンプルすべてに同じ色を書く</strong>。
    - 縁の画素だけ<strong>サンプルごとに色が違う</strong>→ <strong>リゾルブ（平均）</strong>で<strong>滑らかな縁</strong>。
    - <strong>効く</strong>のは<strong>ジオメトリの縁</strong>。<strong>効かない</strong>のは<strong>シェーダー内・テクスチャ内</strong>のエイリアシング。
    - <strong>メモリと帯域が サンプル数 倍</strong>。<strong>ディファードの G バッファは特に重い</strong>。
    - <strong>VR・モバイル（タイルベース）</strong>では<strong>今も現役</strong>。

<!-- fig:msaa-samples:begin -->

<svg class="fig illust motion" data-fig="msaa-samples" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-msaa-samples" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">MSAA:1 画素に複数のサンプルを置き、三角形に覆われた数で縁の濃さが決まる</text>
<rect x="40" y="90" width="69" height="69" fill="#f8fafc"/>
<rect x="110" y="90" width="69" height="69" fill="#f8fafc"/>
<rect x="180" y="90" width="69" height="69" fill="#f8fafc"/>
<rect x="250" y="90" width="69" height="69" fill="#f8fafc"/>
<rect x="320" y="90" width="69" height="69" fill="#f8fafc"/>
<rect x="390" y="90" width="69" height="69" fill="#f8fafc"/>
<rect x="460" y="90" width="69" height="69" fill="#f8fafc"/>
<rect x="40" y="160" width="69" height="69" fill="#f8fafc"/>
<rect x="110" y="160" width="69" height="69" fill="#f8fafc"/>
<rect x="180" y="160" width="69" height="69" fill="#f8fafc"/>
<rect x="250" y="160" width="69" height="69" fill="#f8fafc"/>
<rect x="320" y="160" width="69" height="69" fill="#f8fafc"/>
<rect x="390" y="160" width="69" height="69" fill="#f8fafc"/>
<rect x="460" y="160" width="69" height="69" fill="#f8fafc"/>
<rect x="40" y="230" width="69" height="69" fill="#f8fafc"/>
<rect x="110" y="230" width="69" height="69" fill="#f8fafc"/>
<rect x="180" y="230" width="69" height="69" fill="#f8fafc"/>
<rect x="250" y="230" width="69" height="69" fill="#f8fafc"/>
<rect x="320" y="230" width="69" height="69" fill="#f8fafc"/>
<rect x="390" y="230" width="69" height="69" fill="#f8fafc"/>
<rect x="460" y="230" width="69" height="69" fill="#f8fafc"/>
<rect x="40" y="300" width="69" height="69" fill="#f8fafc"/>
<rect x="110" y="300" width="69" height="69" fill="#f8fafc"/>
<rect x="180" y="300" width="69" height="69" fill="#f8fafc"/>
<rect x="250" y="300" width="69" height="69" fill="#f8fafc"/>
<rect x="320" y="300" width="69" height="69" fill="#f8fafc"/>
<rect x="390" y="300" width="69" height="69" fill="#f8fafc"/>
<rect x="460" y="300" width="69" height="69" fill="#f8fafc"/>
<line x1="40" y1="125.0" x2="435.16" y2="370" stroke="#2563eb" stroke-width="3.5"/>
<text x="530" y="392" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2563eb">青い線の上側が三角形</text>
<circle cx="48.75" cy="133.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/></circle>
<circle cx="66.25" cy="98.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/></circle>
<circle cx="83.75" cy="151.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/></circle>
<circle cx="101.25" cy="116.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/></circle>
<circle cx="118.75" cy="133.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0871;0.0874;1.0000" values="0;0;1;1"/></circle>
<circle cx="136.25" cy="98.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0871;0.0874;1.0000" values="0;0;1;1"/></circle>
<circle cx="153.75" cy="151.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0871;0.0874;1.0000" values="0;0;1;1"/></circle>
<circle cx="171.25" cy="116.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0871;0.0874;1.0000" values="0;0;1;1"/></circle>
<circle cx="188.75" cy="133.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1004;0.1007;1.0000" values="0;0;1;1"/></circle>
<circle cx="206.25" cy="98.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1004;0.1007;1.0000" values="0;0;1;1"/></circle>
<circle cx="223.75" cy="151.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1004;0.1007;1.0000" values="0;0;1;1"/></circle>
<circle cx="241.25" cy="116.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1004;0.1007;1.0000" values="0;0;1;1"/></circle>
<circle cx="258.75" cy="133.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1138;0.1141;1.0000" values="0;0;1;1"/></circle>
<circle cx="276.25" cy="98.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1138;0.1141;1.0000" values="0;0;1;1"/></circle>
<circle cx="293.75" cy="151.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1138;0.1141;1.0000" values="0;0;1;1"/></circle>
<circle cx="311.25" cy="116.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1138;0.1141;1.0000" values="0;0;1;1"/></circle>
<circle cx="328.75" cy="133.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1271;0.1274;1.0000" values="0;0;1;1"/></circle>
<circle cx="346.25" cy="98.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1271;0.1274;1.0000" values="0;0;1;1"/></circle>
<circle cx="363.75" cy="151.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1271;0.1274;1.0000" values="0;0;1;1"/></circle>
<circle cx="381.25" cy="116.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1271;0.1274;1.0000" values="0;0;1;1"/></circle>
<circle cx="398.75" cy="133.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1404;0.1407;1.0000" values="0;0;1;1"/></circle>
<circle cx="416.25" cy="98.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1404;0.1407;1.0000" values="0;0;1;1"/></circle>
<circle cx="433.75" cy="151.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1404;0.1407;1.0000" values="0;0;1;1"/></circle>
<circle cx="451.25" cy="116.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1404;0.1407;1.0000" values="0;0;1;1"/></circle>
<circle cx="468.75" cy="133.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1538;0.1541;1.0000" values="0;0;1;1"/></circle>
<circle cx="486.25" cy="98.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1538;0.1541;1.0000" values="0;0;1;1"/></circle>
<circle cx="503.75" cy="151.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1538;0.1541;1.0000" values="0;0;1;1"/></circle>
<circle cx="521.25" cy="116.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1538;0.1541;1.0000" values="0;0;1;1"/></circle>
<circle cx="48.75" cy="203.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1671;0.1674;1.0000" values="0;0;1;1"/></circle>
<circle cx="66.25" cy="168.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1671;0.1674;1.0000" values="0;0;1;1"/></circle>
<circle cx="83.75" cy="221.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1671;0.1674;1.0000" values="0;0;1;1"/></circle>
<circle cx="101.25" cy="186.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1671;0.1674;1.0000" values="0;0;1;1"/></circle>
<circle cx="118.75" cy="203.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1804;0.1807;1.0000" values="0;0;1;1"/></circle>
<circle cx="136.25" cy="168.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1804;0.1807;1.0000" values="0;0;1;1"/></circle>
<circle cx="153.75" cy="221.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1804;0.1807;1.0000" values="0;0;1;1"/></circle>
<circle cx="171.25" cy="186.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1804;0.1807;1.0000" values="0;0;1;1"/></circle>
<circle cx="188.75" cy="203.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1938;0.1941;1.0000" values="0;0;1;1"/></circle>
<circle cx="206.25" cy="168.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1938;0.1941;1.0000" values="0;0;1;1"/></circle>
<circle cx="223.75" cy="221.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1938;0.1941;1.0000" values="0;0;1;1"/></circle>
<circle cx="241.25" cy="186.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1938;0.1941;1.0000" values="0;0;1;1"/></circle>
<circle cx="258.75" cy="203.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2071;0.2074;1.0000" values="0;0;1;1"/></circle>
<circle cx="276.25" cy="168.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2071;0.2074;1.0000" values="0;0;1;1"/></circle>
<circle cx="293.75" cy="221.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2071;0.2074;1.0000" values="0;0;1;1"/></circle>
<circle cx="311.25" cy="186.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2071;0.2074;1.0000" values="0;0;1;1"/></circle>
<circle cx="328.75" cy="203.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2204;0.2207;1.0000" values="0;0;1;1"/></circle>
<circle cx="346.25" cy="168.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2204;0.2207;1.0000" values="0;0;1;1"/></circle>
<circle cx="363.75" cy="221.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2204;0.2207;1.0000" values="0;0;1;1"/></circle>
<circle cx="381.25" cy="186.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2204;0.2207;1.0000" values="0;0;1;1"/></circle>
<circle cx="398.75" cy="203.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2338;0.2341;1.0000" values="0;0;1;1"/></circle>
<circle cx="416.25" cy="168.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2338;0.2341;1.0000" values="0;0;1;1"/></circle>
<circle cx="433.75" cy="221.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2338;0.2341;1.0000" values="0;0;1;1"/></circle>
<circle cx="451.25" cy="186.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2338;0.2341;1.0000" values="0;0;1;1"/></circle>
<circle cx="468.75" cy="203.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2471;0.2474;1.0000" values="0;0;1;1"/></circle>
<circle cx="486.25" cy="168.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2471;0.2474;1.0000" values="0;0;1;1"/></circle>
<circle cx="503.75" cy="221.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2471;0.2474;1.0000" values="0;0;1;1"/></circle>
<circle cx="521.25" cy="186.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2471;0.2474;1.0000" values="0;0;1;1"/></circle>
<circle cx="48.75" cy="273.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2604;0.2607;1.0000" values="0;0;1;1"/></circle>
<circle cx="66.25" cy="238.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2604;0.2607;1.0000" values="0;0;1;1"/></circle>
<circle cx="83.75" cy="291.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2604;0.2607;1.0000" values="0;0;1;1"/></circle>
<circle cx="101.25" cy="256.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2604;0.2607;1.0000" values="0;0;1;1"/></circle>
<circle cx="118.75" cy="273.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2738;0.2741;1.0000" values="0;0;1;1"/></circle>
<circle cx="136.25" cy="238.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2738;0.2741;1.0000" values="0;0;1;1"/></circle>
<circle cx="153.75" cy="291.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2738;0.2741;1.0000" values="0;0;1;1"/></circle>
<circle cx="171.25" cy="256.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2738;0.2741;1.0000" values="0;0;1;1"/></circle>
<circle cx="188.75" cy="273.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2871;0.2874;1.0000" values="0;0;1;1"/></circle>
<circle cx="206.25" cy="238.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2871;0.2874;1.0000" values="0;0;1;1"/></circle>
<circle cx="223.75" cy="291.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2871;0.2874;1.0000" values="0;0;1;1"/></circle>
<circle cx="241.25" cy="256.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2871;0.2874;1.0000" values="0;0;1;1"/></circle>
<circle cx="258.75" cy="273.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3004;0.3007;1.0000" values="0;0;1;1"/></circle>
<circle cx="276.25" cy="238.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3004;0.3007;1.0000" values="0;0;1;1"/></circle>
<circle cx="293.75" cy="291.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3004;0.3007;1.0000" values="0;0;1;1"/></circle>
<circle cx="311.25" cy="256.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3004;0.3007;1.0000" values="0;0;1;1"/></circle>
<circle cx="328.75" cy="273.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3138;0.3141;1.0000" values="0;0;1;1"/></circle>
<circle cx="346.25" cy="238.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3138;0.3141;1.0000" values="0;0;1;1"/></circle>
<circle cx="363.75" cy="291.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3138;0.3141;1.0000" values="0;0;1;1"/></circle>
<circle cx="381.25" cy="256.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3138;0.3141;1.0000" values="0;0;1;1"/></circle>
<circle cx="398.75" cy="273.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3271;0.3274;1.0000" values="0;0;1;1"/></circle>
<circle cx="416.25" cy="238.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3271;0.3274;1.0000" values="0;0;1;1"/></circle>
<circle cx="433.75" cy="291.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3271;0.3274;1.0000" values="0;0;1;1"/></circle>
<circle cx="451.25" cy="256.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3271;0.3274;1.0000" values="0;0;1;1"/></circle>
<circle cx="468.75" cy="273.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3404;0.3407;1.0000" values="0;0;1;1"/></circle>
<circle cx="486.25" cy="238.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3404;0.3407;1.0000" values="0;0;1;1"/></circle>
<circle cx="503.75" cy="291.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3404;0.3407;1.0000" values="0;0;1;1"/></circle>
<circle cx="521.25" cy="256.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3404;0.3407;1.0000" values="0;0;1;1"/></circle>
<circle cx="48.75" cy="343.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3538;0.3541;1.0000" values="0;0;1;1"/></circle>
<circle cx="66.25" cy="308.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3538;0.3541;1.0000" values="0;0;1;1"/></circle>
<circle cx="83.75" cy="361.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3538;0.3541;1.0000" values="0;0;1;1"/></circle>
<circle cx="101.25" cy="326.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3538;0.3541;1.0000" values="0;0;1;1"/></circle>
<circle cx="118.75" cy="343.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3671;0.3674;1.0000" values="0;0;1;1"/></circle>
<circle cx="136.25" cy="308.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3671;0.3674;1.0000" values="0;0;1;1"/></circle>
<circle cx="153.75" cy="361.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3671;0.3674;1.0000" values="0;0;1;1"/></circle>
<circle cx="171.25" cy="326.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3671;0.3674;1.0000" values="0;0;1;1"/></circle>
<circle cx="188.75" cy="343.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3804;0.3807;1.0000" values="0;0;1;1"/></circle>
<circle cx="206.25" cy="308.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3804;0.3807;1.0000" values="0;0;1;1"/></circle>
<circle cx="223.75" cy="361.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3804;0.3807;1.0000" values="0;0;1;1"/></circle>
<circle cx="241.25" cy="326.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3804;0.3807;1.0000" values="0;0;1;1"/></circle>
<circle cx="258.75" cy="343.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3938;0.3941;1.0000" values="0;0;1;1"/></circle>
<circle cx="276.25" cy="308.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3938;0.3941;1.0000" values="0;0;1;1"/></circle>
<circle cx="293.75" cy="361.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3938;0.3941;1.0000" values="0;0;1;1"/></circle>
<circle cx="311.25" cy="326.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3938;0.3941;1.0000" values="0;0;1;1"/></circle>
<circle cx="328.75" cy="343.75" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4071;0.4074;1.0000" values="0;0;1;1"/></circle>
<circle cx="346.25" cy="308.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4071;0.4074;1.0000" values="0;0;1;1"/></circle>
<circle cx="363.75" cy="361.25" r="6" fill="#ffffff" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4071;0.4074;1.0000" values="0;0;1;1"/></circle>
<circle cx="381.25" cy="326.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4071;0.4074;1.0000" values="0;0;1;1"/></circle>
<circle cx="398.75" cy="343.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4204;0.4207;1.0000" values="0;0;1;1"/></circle>
<circle cx="416.25" cy="308.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4204;0.4207;1.0000" values="0;0;1;1"/></circle>
<circle cx="433.75" cy="361.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4204;0.4207;1.0000" values="0;0;1;1"/></circle>
<circle cx="451.25" cy="326.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4204;0.4207;1.0000" values="0;0;1;1"/></circle>
<circle cx="468.75" cy="343.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4338;0.4341;1.0000" values="0;0;1;1"/></circle>
<circle cx="486.25" cy="308.75" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4338;0.4341;1.0000" values="0;0;1;1"/></circle>
<circle cx="503.75" cy="361.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4338;0.4341;1.0000" values="0;0;1;1"/></circle>
<circle cx="521.25" cy="326.25" r="6" fill="#e5484d" stroke="#1f2937" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4338;0.4341;1.0000" values="0;0;1;1"/></circle>
<rect x="43" y="93" width="63" height="63" fill="#505050" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="113" y="93" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="183" y="93" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="253" y="93" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="323" y="93" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="393" y="93" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="463" y="93" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="43" y="163" width="63" height="63" fill="#f2f2f2" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="113" y="163" width="63" height="63" fill="#868686" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="183" y="163" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="253" y="163" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="323" y="163" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="393" y="163" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="463" y="163" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="43" y="233" width="63" height="63" fill="#f2f2f2" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="113" y="233" width="63" height="63" fill="#f2f2f2" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="183" y="233" width="63" height="63" fill="#f2f2f2" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="253" y="233" width="63" height="63" fill="#868686" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="323" y="233" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="393" y="233" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="463" y="233" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="43" y="303" width="63" height="63" fill="#f2f2f2" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="113" y="303" width="63" height="63" fill="#f2f2f2" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="183" y="303" width="63" height="63" fill="#f2f2f2" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="253" y="303" width="63" height="63" fill="#f2f2f2" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="323" y="303" width="63" height="63" fill="#868686" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="393" y="303" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<rect x="463" y="303" width="63" height="63" fill="#191919" opacity="0" rx="3"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="0;0;1;1"/></rect>
<text x="40" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">各画素の 4 つのサンプルが、三角形の内側（赤）か外側（白）かを調べる<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000" values="1;1;0;0"/></text>
<text x="40" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">覆われたサンプルの割合で、画素の色を混ぜる（0/4〜4/4）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4841;0.4844;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">シェーディング（ライティング）は、画素ごとに 1 回だけ。深度・カバレッジだけを、サンプルごとに持つ。縁だけが滑らかになる。</text>
</svg>

<!-- fig:msaa-samples:end -->

## SSAA との違い

<strong>SSAA（スーパー サンプリング）</strong>は、**画面全体を縦横 2 倍（面積 4 倍）で描いて縮小**する方式です。**最も高品質**ですが**ピクセル シェーダーも 4 倍回るので、非常に重い**です。

SSAA 4x と MSAA 4x を比べます。SSAA 4x は、ピクセル シェーダーが 4 倍、メモリも 4 倍で、縁もシェーダー内も滑らかになります。MSAA 4x は、ピクセル シェーダーは 1 倍で済み、メモリ（カラーと深度）は 4 倍ですが、縁は滑らかになるものの、シェーダー内のエイリアシングには効きません。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="MSAA のサンプル">
<text x="20" y="26" class="fig-title">MSAA：縁をまたぐ画素だけ、サンプルごとに「覆っているか」を判定</text>
<g transform="translate(40,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">1 サンプル（通常）</text>
<rect x="0" y="0" width="160" height="160" fill="#f8fafc" stroke="#94a3b8"/>
<polygon points="0,160 160,160 160,0" fill="#2563eb" fill-opacity="0.25"/>
<g fill="#334155"><rect x="80" y="80" width="80" height="80" opacity="0.6"/></g>
<circle cx="120" cy="120" r="4" fill="#fff"/>
<text x="0" y="182" style="font-size:12px">画素の中心だけで判定 → 全部か、ゼロ</text>
</g>
<g transform="translate(300,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">4 サンプル（MSAA 4x）</text>
<rect x="0" y="0" width="160" height="160" fill="#f8fafc" stroke="#94a3b8"/>
<polygon points="0,160 160,160 160,0" fill="#2563eb" fill-opacity="0.25"/>
<g stroke="#94a3b8"><line x1="80" y1="0" x2="80" y2="160"/><line x1="0" y1="80" x2="160" y2="80"/></g>
<circle cx="50" cy="50" r="5" fill="#94a3b8"/><circle cx="110" cy="40" r="5" fill="#94a3b8"/><circle cx="40" cy="110" r="5" fill="#2563eb"/><circle cx="110" cy="115" r="5" fill="#2563eb"/>
<text x="0" y="182" style="font-size:12px">4 点のうち 2 点が内側 → 50 % の色</text>
</g>
<g font-size="13"><text x="520" y="100" style="font-weight:700">リゾルブ（解像）</text>
<text x="520" y="124">各画素のサンプルを平均して</text>
<text x="520" y="146">最終的な 1 画素の色にする</text></g>
</svg>

## 仕組み

| 手順 | 内容 |
| --- | --- |
| **① 各サンプルのカバレッジ** | **三角形が画素内の複数のサンプル点を、それぞれ覆うかを判定**（ラスタライザ） |
| **② ピクセル シェーダーは 1 回** | **画素ごとに 1 回、色を計算**（**画素の中心付近**） |
| **③ 覆ったサンプルに書く** | **その色を覆ったサンプルすべてに書く**（**深度はサンプルごとに別**） |
| **④ リゾルブ** | **各画素のサンプルを平均して、1 つの色に** |

**内側の画素**は**全サンプルが同じ色**なので、**平均しても変わりません**。**縁の画素**だけ、<strong>サンプルごとに色が違い（三角形の色と背景の色）</strong>、**平均すると中間色になり、滑らか**になります。

## サンプル パターン

**サンプル点の位置**は、**規則格子ではなく、回転した（ずらした）配置**が使われます。

サンプル点の位置は、規則格子でなく、回転した（ずらした）配置が使われます。2x は斜めに 2 点です。4x は回転した格子（RGSS）で、水平や垂直の縁で異なる段階を作れます。8x はさらに多様な位置を取ります。

**規則格子**（**縦横にそろう**）だと**水平・垂直に近い縁でサンプルの高さが同じになり、段階が減ります**。**回転・ずらした配置**にすると**どの傾きの縁でも多くの段階**が**得られます**。

## DX11 での設定

```cpp
DXGI_SAMPLE_DESC sample_desc = {4, 0};

D3D11_TEXTURE2D_DESC color_desc = {};
color_desc.Width = width;
color_desc.Height = height;
color_desc.MipLevels = 1;
color_desc.ArraySize = 1;
color_desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;
color_desc.SampleDesc = sample_desc;
color_desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&color_desc, nullptr, msaa_color.GetAddressOf());

context->ResolveSubresource(resolved.Get(), 0, msaa_color.Get(), 0, DXGI_FORMAT_R16G16B16A16_FLOAT);
```

設定の要点です。`SampleDesc = {4, 0}` で 4x MSAA になり、カラーも深度も同じサンプル数です。`ResolveSubresource` は、ハードウェアがサンプルを平均して 1 サンプルの画像にします。HDR では、リゾルブが単純平均なので、明るい点が混ざってトーンマップ後の見た目が悪化することがあります（次の節）。

### HDR でのリゾルブの注意

<strong>HDR（値が 1 を超える）</strong>を**そのまま平均**すると**明るい点が支配的になり、トーンマップ後に縁がジャギーのまま見えます**。**対策**：

HDR（値が 1 を超える）をそのまま平均すると、明るい点が支配的になり、トーンマップ後に縁がジャギーのまま見えます。対策は 2 つです。サンプルごとにトーンマップ（またはその近似）してから平均して戻す方法。コンピュート シェーダーのカスタム リゾルブで、サンプルを読み、輝度で重み付けして平均する方法です（ファイアフライ対策と同様です）。

## 弱点

| 弱点 | 理由 | 対処 |
| --- | --- | --- |
| **シェーダー内のエイリアシングに効かない** | **シェーダーは 1 画素 1 回** | **TAA・スペキュラ AA** |
| **アルファ テストの縁に効かない** | **テクスチャのアルファ判定は、画素単位** | <strong>A2C（アルファ トゥ カバレッジ）</strong> |
| **ディファードで重い** | **G バッファがサンプル数 倍** | **フォワード系・MSAA を諦める** |
| **メモリと帯域が サンプル数 倍** | **深度・カラーのサンプルが増える** | **サンプル数を下げる・圧縮に頼る** |
| **ポストプロセスと相性が悪い** | **リゾルブ前のサンプルは、画面全体の加工に使いにくい** | **リゾルブしてから加工** |

### アルファ トゥ カバレッジ（A2C）

**葉・フェンスのアルファ テスト**の縁は、**MSAA で滑らかになりません**。**A2C** を**有効にする**と、**ピクセル シェーダーが出力したアルファを、カバレッジ マスクに変換**し、**サンプルごとに覆う・覆わないを決めます**。

```cpp
D3D11_BLEND_DESC blend = {};
blend.AlphaToCoverageEnable = TRUE;
```

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| <strong>フォワード ＋ MSAA（VR・モバイル）</strong> | <strong>タイルベース GPU は、MSAA がほぼ無料（タイル内で解決）</strong> |
| **MSAA ＋ TAA** | **縁は MSAA、残りは TAA で**（**重くなる**） |
| **A2C で葉・フェンス** | **アルファ テストの縁も滑らかに** |
| **HDR はトーンマップ後の見た目でリゾルブ** | **明るい点でジャギーが復活しないよう** |
| **スペキュラ AA を併用** | **シェーダー内のちらつきは、別に対策**（法線の分散を粗さに足す） |

## よくあるミス

??? failure "MSAA を有効にしたのに、スペキュラのちらつきが消えない"
    **MSAA はジオメトリの縁だけ**。**TAA・スペキュラ AA** を使う。

??? failure "HDR でリゾルブして、明るい縁がジャギーに見える"
    **トーンマップしてからリゾルブ**、または**重み付きリゾルブ**。

??? failure "ディファードで MSAA を有効にして、極端に重くなる"
    **G バッファが全サンプル分**。**フォワード系にするか、TAA に切り替える**。

??? failure "葉のアルファ テストの縁が、ジャギーのまま"
    <strong>A2C（`AlphaToCoverageEnable`）</strong>を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] MSAA ＝ <strong>1 画素に複数サンプル</strong>。<strong>縁だけサンプルごとに判定</strong>。<strong>シェーダーは 1 回</strong>
    - [x] <strong>ジオメトリの縁に効く</strong>が、<strong>シェーダー内には効かない</strong>
    - [x] <strong>リゾルブ（平均）</strong>で<strong>滑らかな縁</strong>。<strong>HDR ではリゾルブの順序に注意</strong>
    - [x] <strong>メモリ・帯域が サンプル数 倍</strong>。<strong>ディファードとは相性が悪い</strong>
    - [x] <strong>A2C</strong> で<strong>アルファ テストの縁</strong>も

## 参考

- Akeley, "RealityEngine Graphics"（SIGGRAPH 1993）
- Microsoft, "Multisampling Anti-Aliasing"（Microsoft Learn）
- Pettineo, "A Quick Overview of MSAA"（The Danger Zone）

## 関連ページ

- [Anti-Aliasing](index.md)
- [FXAA](fxaa.md)
- [TAA](taa.md)
- [Comparison and Choosing](comparison.md)
- [ラスタライズ（MSAA）](../../../3d/render-flow/rasterize.md)
