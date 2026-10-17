---
title: Interpolation Methods
tags:
  - 描画
---

# Interpolation Methods

**物体の位置は、プローブとプローブの間にあるので、周囲のプローブから補間して、値を求めます**。**単純な 3 線形補間だと、壁の向こうのプローブの光が漏れる**ので、**可視性を考慮する**方式があります。このページでは、**補間の方式と、光漏れの対策**を説明します。

!!! tip "ポイント"
    - **3 線形補間 ＝ 周囲の 8 プローブを、距離で重み付け**。
    - **壁の向こうのプローブも混ざると、光が漏れる**。
    - **可視性（そのプローブから見えるか）で、重みを減らす**。
    - **DDGI は、深度情報で可視性を判定**する（[DDGI](../ddgi.md)）。

## 補間の方式
### 四面体分割（Delaunay）

**プローブを不規則に置いて**、**その点群を四面体に分割**します。**物体がどの四面体の中にいるか**を調べ、**その 4 つの頂点のプローブ**を、**重心座標の重み**で**補間**します。

四面体分割の利点は、プローブを自由に配置でき、重要な場所は密に、他は疎に置けることです。欠点は、物体ごとに（CPU で）四面体を検索する必要があること、そして四面体が壁を貫通して光が漏れることがあることです。Unity の Light Probe Group が、この方式です。

<!-- fig:probe-bilinear:begin -->

<svg class="fig illust motion" data-fig="probe-bilinear" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-probe-bilinear" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">プローブの補間:周りの 4 つ（3D では 8 つ）を、距離で重み付けして混ぜる</text>
<rect x="110" y="100" width="260" height="260" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="110" cy="100" r="20" fill="#e5484d" stroke="#ffffff" stroke-width="3"/>
<circle cx="370" cy="100" r="20" fill="#2563eb" stroke="#ffffff" stroke-width="3"/>
<circle cx="110" cy="360" r="20" fill="#2ea043" stroke="#ffffff" stroke-width="3"/>
<circle cx="370" cy="360" r="20" fill="#e5aa28" stroke="#ffffff" stroke-width="3"/>
<circle cx="162.0" cy="165.0" r="10" fill="#ffffff" stroke="#1f2937" stroke-width="3"><animate attributeName="cx" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.0720;0.0847;0.0974;0.1101;0.1228;0.1354;0.1481;0.1608;0.1735;0.1862;0.1989;0.2116;0.2243;0.2370;0.2497;0.2624;0.2751;0.2878;0.3005;0.3132;0.3259;0.3386;0.3513;0.3640;0.3767;0.3894;0.4021;0.4148;0.4275;0.4402;0.4529;0.4656;0.4783;0.4910;0.5037;0.5164;0.5291;0.5418;0.5545;0.5672;0.5799;0.5926;0.6053;0.6180;0.6307;0.6434;0.6561;0.6688;0.6815;0.6942;0.7069;0.7196;0.7323;0.7450;0.7577;0.7704;1.0000" values="162;162;173.14;184.29;195.43;206.57;217.71;228.86;240;251.14;262.29;273.43;284.57;295.71;306.86;318;317.07;316.14;315.21;314.29;313.36;312.43;311.5;310.57;309.64;308.71;307.79;306.86;305.93;305;295.71;286.43;277.14;267.86;258.57;249.29;240;230.71;221.43;212.14;202.86;193.57;184.29;175;179.64;184.29;188.93;193.57;198.21;202.86;207.5;212.14;216.79;221.43;226.07;230.71;235.36;240;240"/><animate attributeName="cy" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.0720;0.0847;0.0974;0.1101;0.1228;0.1354;0.1481;0.1608;0.1735;0.1862;0.1989;0.2116;0.2243;0.2370;0.2497;0.2624;0.2751;0.2878;0.3005;0.3132;0.3259;0.3386;0.3513;0.3640;0.3767;0.3894;0.4021;0.4148;0.4275;0.4402;0.4529;0.4656;0.4783;0.4910;0.5037;0.5164;0.5291;0.5418;0.5545;0.5672;0.5799;0.5926;0.6053;0.6180;0.6307;0.6434;0.6561;0.6688;0.6815;0.6942;0.7069;0.7196;0.7323;0.7450;0.7577;0.7704;1.0000" values="165;165;164.07;163.14;162.21;161.29;160.36;159.43;158.5;157.57;156.64;155.71;154.79;153.86;152.93;152;163.14;174.29;185.43;196.57;207.71;218.86;230;241.14;252.29;263.43;274.57;285.71;296.86;308;307.07;306.14;305.21;304.29;303.36;302.43;301.5;300.57;299.64;298.71;297.79;296.86;295.93;295;290.36;285.71;281.07;276.43;271.79;267.14;262.5;257.86;253.21;248.57;243.93;239.29;234.64;230;230"/></circle>
<rect x="470" y="100" width="130" height="90" fill="#888888" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0720;0.0847;0.0974;0.1101;0.1228;0.1354;0.1481;0.1608;0.1735;0.1862;0.1989;0.2116;0.2243;0.2370;0.2497;0.2624;0.2751;0.2878;0.3005;0.3132;0.3259;0.3386;0.3513;0.3640;0.3767;0.3894;0.4021;0.4148;0.4275;0.4402;0.4529;0.4656;0.4783;0.4910;0.5037;0.5164;0.5291;0.5418;0.5545;0.5672;0.5799;0.5926;0.6053;0.6180;0.6307;0.6434;0.6561;0.6688;0.6815;0.6942;0.7069;0.7196;0.7323;0.7450;0.7577;0.7704;1.0000" values="#888888;#888888;#a46361;#a06366;#9c646b;#986570;#936575;#8f667a;#8b6780;#866785;#81688a;#7d6990;#786a95;#736a9b;#6d6ba0;#686ca6;#636cac;#6870a5;#6d739e;#737696;#78798f;#7d7c88;#817f82;#86827b;#8b8574;#8f896d;#938c67;#988f60;#9c9259;#a09553;#a4984c;#9f984d;#9b974d;#97964d;#94954d;#90954d;#8c944d;#88934d;#85924c;#82924c;#7e914c;#7b904c;#788f4b;#758e4b;#728e4a;#758c4c;#788b4d;#7b8a4f;#7d8951;#7f8753;#818655;#838557;#848459;#85835b;#86825e;#878160;#877f63;#877e66;#877d69;#877d69"/></rect>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.60  青 0.15<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0827;0.0830;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.57  青 0.18<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0827;0.0830;0.1064;0.1067;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.51  青 0.25<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1064;0.1067;0.1301;0.1304;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.45  青 0.32<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1301;0.1304;0.1538;0.1541;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.39  青 0.39<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1538;0.1541;0.1775;0.1778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.32  青 0.46<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1775;0.1778;0.2012;0.2015;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.26  青 0.53<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2012;0.2015;0.2249;0.2252;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.19  青 0.60<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2249;0.2252;0.2486;0.2489;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.15  青 0.60<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2486;0.2489;0.2723;0.2726;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.14  青 0.53<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2723;0.2726;0.2960;0.2963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.13  青 0.46<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;0.3197;0.3200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.11  青 0.39<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3197;0.3200;0.3434;0.3437;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.10  青 0.32<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3434;0.3437;0.3671;0.3674;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.08  青 0.25<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3671;0.3674;0.3908;0.3911;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.06  青 0.18<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3908;0.3911;0.4145;0.4148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.05  青 0.15<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4145;0.4148;0.4382;0.4385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.07  青 0.14<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4382;0.4385;0.4619;0.4622;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.08  青 0.13<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4619;0.4622;0.4856;0.4859;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.10  青 0.12<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4856;0.4859;0.5093;0.5096;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.12  青 0.11<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5093;0.5096;0.5330;0.5333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.14  青 0.09<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5330;0.5333;0.5567;0.5570;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.16  青 0.08<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5567;0.5570;0.5804;0.5807;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.19  青 0.06<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5804;0.5807;0.6041;0.6044;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.20  青 0.08<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6041;0.6044;0.6279;0.6281;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.22  青 0.10<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6279;0.6281;0.6516;0.6519;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.23  青 0.13<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6516;0.6519;0.6753;0.6756;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.24  青 0.15<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6753;0.6756;0.6990;0.6993;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.24  青 0.18<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6990;0.6993;0.7227;0.7230;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.25  青 0.22<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7227;0.7230;0.7464;0.7467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="224" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重み 赤 0.25  青 0.25<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7464;0.7467;0.7701;0.7704;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.20  黄 0.05<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0827;0.0830;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.19  黄 0.06<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0827;0.0830;0.1064;0.1067;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.16  黄 0.08<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1064;0.1067;0.1301;0.1304;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.14  黄 0.10<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1301;0.1304;0.1538;0.1541;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.11  黄 0.11<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1538;0.1541;0.1775;0.1778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.09  黄 0.13<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1775;0.1778;0.2012;0.2015;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.07  黄 0.14<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2012;0.2015;0.2249;0.2252;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.05  黄 0.15<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2249;0.2252;0.2486;0.2489;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.05  黄 0.19<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2486;0.2489;0.2723;0.2726;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.07  黄 0.26<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2723;0.2726;0.2960;0.2963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.09  黄 0.32<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;0.3197;0.3200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.11  黄 0.39<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3197;0.3200;0.3434;0.3437;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.14  黄 0.45<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3434;0.3437;0.3671;0.3674;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.16  黄 0.51<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3671;0.3674;0.3908;0.3911;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.19  黄 0.57<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3908;0.3911;0.4145;0.4148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.20  黄 0.60<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4145;0.4148;0.4382;0.4385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.25  黄 0.54<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4382;0.4385;0.4619;0.4622;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.31  黄 0.48<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4619;0.4622;0.4856;0.4859;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.36  黄 0.42<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4856;0.4859;0.5093;0.5096;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.41  黄 0.36<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5093;0.5096;0.5330;0.5333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.46  黄 0.30<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5330;0.5333;0.5567;0.5570;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.51  黄 0.24<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5567;0.5570;0.5804;0.5807;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.56  黄 0.19<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5804;0.5807;0.6041;0.6044;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.51  黄 0.20<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6041;0.6044;0.6279;0.6281;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.46  黄 0.22<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6279;0.6281;0.6516;0.6519;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.41  黄 0.23<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6516;0.6519;0.6753;0.6756;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.37  黄 0.24<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6753;0.6756;0.6990;0.6993;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.33  黄 0.24<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6990;0.6993;0.7227;0.7230;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.29  黄 0.25<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7227;0.7230;0.7464;0.7467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">     緑 0.25  黄 0.25<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7464;0.7467;0.7701;0.7704;1.0000" values="0;0;1;1;0;0"/></text>
<text x="470" y="90" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">混ざった色（その点の間接光）</text>
<text x="40" y="396" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">近いプローブほど重い。重みの合計は 1。物体が動いても、プローブ間を滑らかに補間するので、色がちらつかない。</text>
</svg>

<!-- fig:probe-bilinear:end -->

### 3D 格子

**プローブを規則的な 3D 格子**に並べ、**格子上でトライリニア補間**します。

3D 格子の利点は、補間が安いことです。GPU で 3D テクスチャとして引けるので、画素ごとに補間できます。欠点は、密度が一様で疎な所が無駄になること、メモリが体積に比例して増えることです。Light Probe Volume、DDGI、モバイル向けの実装で採用されます。

### 四面体補間の中身

四面体の中の点 p は、4 つの頂点 a, b, c, d の<strong>重心座標</strong>で表せます。`p = w_a·a + w_b·b + w_c·c + w_d·d`（重みの合計は 1）。各頂点のプローブの SH 係数に、同じ重みを掛けて足したものが、p での SH です。重みは、p と他の 3 頂点が作る小さな四面体の体積の比で求まります。計算は軽いですが、どの四面体に p が入っているかを探す処理が必要で、物体が動くたびに、前フレームの四面体から隣へ辿って更新するのが一般的です。

### トライリニア補間の中身

格子の場合は、p を囲む 8 つの格子点があり、各軸で 0〜1 の小数部分を使って、2×2×2 の重みを作ります。ハードウェアの三線形フィルタがそのまま使えるので、SH の係数を 3D テクスチャに入れておけば、1 回のテクスチャ読み込みで補間が済みます。ただし、壁の向こう側のプローブも等しく混ざってしまうので、光漏れが起きます。DDGI のように、各プローブに距離情報を持たせ、見えないプローブの重みを下げる方式があります（[DDGI](../ddgi.md)）。

### 画素ごとの引き

<strong>物体ごと（1 点）</strong>でなく、**画素ごと**に**プローブを引く**（**GPU で、3D テクスチャ**から）と、**大きな物体・地形の場所による変化**が**反映**されます。**1 つの物体を 1 点で代表**すると、**大きな物体**で**不自然**です。

## よくあるミス

??? failure "壁の向こうの明るさが、手前に漏れる"
    **可視性を考慮した補間**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **周囲のプローブを、重み付きで補間**
    - [x] **可視性で、光漏れを防ぐ**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Probe GI](index.md)
- [DDGI](../ddgi.md)
- [置き方](placement.md)
