---
title: Monte Carlo Integration
tags:
  - 描画
---

# Monte Carlo Integration

ある点に周りの全方向から届く光を足し合わせるのが、レンダリング方程式の積分です。方向は半球の全体にあって反射を重ねるごとに次元が増えます。ふつうの数値積分（格子状に区切る方法）は、次元が上がるほど点の数が爆発して、現実的ではなくなります。

<strong>モンテカルロ積分はランダムに方向を選んで試して、その平均を取ります</strong>。次元がいくら上がっても同じ形で使えます。ノイズが出ますがサンプルを増やせば、真の値に近づきます。このページでは基本の推定量、ノイズと収束（実測つき）、重点サンプリングと余弦重み付き乱数の選び方（R2 列と層別サンプリングの実測）、直交基底、リアルタイムでの使い方を説明します。

!!! tip "ポイント"
    - ランダムな方向でサンプルして、平均すると積分の近似になります。偏りはありません。
    - 誤差は `1/√N` で減ります。実測でサンプルを 1 から 256 へ 256 倍にすると、誤差が約 1/16 になりました。
    - 余弦重み付きサンプリングは、拡散反射の式から `cosθ` と `π` を消して、平均だけにします。
    - 乱数の選び方でも誤差は大きく変わります。R2 列は同じ本数で白色乱数の約 7.7 分の 1（256 本）でした。
    - リアルタイムでは少ないサンプルとデノイズや時間蓄積が基本です。

!!! info "このページを読む前に"
    - [GI Theory](index.md)（このセクション全体の地図と読む順番）

<!-- fig:monte-carlo-converge:begin -->

<svg class="fig illust motion" data-fig="monte-carlo-converge" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-monte-carlo-converge" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">モンテカルロ:サンプルを増やすほど、平均が真の値に近づく</text>
<rect x="50" y="80" width="330" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="132.5" y1="80" x2="132.5" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="135.0" x2="380" y2="135.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="215.0" y1="80" x2="215.0" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="190.0" x2="380" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="297.5" y1="80" x2="297.5" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="245.0" x2="380" y2="245.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="380" y="320" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">x</text>
<text x="50" y="72" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">f(x)</text>
<path d="M50.0,300.0 L55.5,288.49 L61.0,277.0 L66.5,265.58 L72.0,254.26 L77.5,243.06 L83.0,232.02 L88.5,221.16 L94.0,210.52 L99.5,200.12 L105.0,190.0 L110.5,180.18 L116.0,170.69 L121.5,161.55 L127.0,152.79 L132.5,144.44 L138.0,136.51 L143.5,129.03 L149.0,122.02 L154.5,115.49 L160.0,109.47 L165.5,103.98 L171.0,99.02 L176.5,94.61 L182.0,90.77 L187.5,87.5 L193.0,84.81 L198.5,82.71 L204.0,81.21 L209.5,80.3 L215.0,80.0 L220.5,80.3 L226.0,81.21 L231.5,82.71 L237.0,84.81 L242.5,87.5 L248.0,90.77 L253.5,94.61 L259.0,99.02 L264.5,103.98 L270.0,109.47 L275.5,115.49 L281.0,122.02 L286.5,129.03 L292.0,136.51 L297.5,144.44 L303.0,152.79 L308.5,161.55 L314.0,170.69 L319.5,180.18 L325.0,190.0 L330.5,200.12 L336.0,210.52 L341.5,221.16 L347.0,232.02 L352.5,243.06 L358.0,254.26 L363.5,265.58 L369.0,277.0 L374.5,288.49 L380.0,300.0" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<circle cx="104.43" cy="191.03" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="0;0;1;1"/></circle>
<line x1="104.43" y1="300.0" x2="104.43" y2="191.03" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="0;0;1;1"/></line>
<circle cx="277.62" cy="117.95" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0770;0.0772;1.0000" values="0;0;1;1"/></circle>
<line x1="277.62" y1="300.0" x2="277.62" y2="117.95" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0770;0.0772;1.0000" values="0;0;1;1"/></line>
<circle cx="259.55" cy="99.49" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0852;0.0855;1.0000" values="0;0;1;1"/></circle>
<line x1="259.55" y1="300.0" x2="259.55" y2="99.49" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0852;0.0855;1.0000" values="0;0;1;1"/></line>
<circle cx="208.1" cy="80.47" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0935;0.0938;1.0000" values="0;0;1;1"/></circle>
<line x1="208.1" y1="300.0" x2="208.1" y2="80.47" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0935;0.0938;1.0000" values="0;0;1;1"/></line>
<circle cx="121.28" cy="161.9" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1018;0.1021;1.0000" values="0;0;1;1"/></circle>
<line x1="121.28" y1="300.0" x2="121.28" y2="161.9" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1018;0.1021;1.0000" values="0;0;1;1"/></line>
<circle cx="311.57" cy="166.6" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1101;0.1103;1.0000" values="0;0;1;1"/></circle>
<line x1="311.57" y1="300.0" x2="311.57" y2="166.6" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1101;0.1103;1.0000" values="0;0;1;1"/></line>
<circle cx="316.59" cy="175.12" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1183;0.1186;1.0000" values="0;0;1;1"/></circle>
<line x1="316.59" y1="300.0" x2="316.59" y2="175.12" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1183;0.1186;1.0000" values="0;0;1;1"/></line>
<circle cx="219.11" cy="80.17" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1266;0.1269;1.0000" values="0;0;1;1"/></circle>
<line x1="219.11" y1="300.0" x2="219.11" y2="80.17" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1266;0.1269;1.0000" values="0;0;1;1"/></line>
<circle cx="216.68" cy="80.03" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1349;0.1352;1.0000" values="0;0;1;1"/></circle>
<line x1="216.68" y1="300.0" x2="216.68" y2="80.03" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1349;0.1352;1.0000" values="0;0;1;1"/></line>
<circle cx="127.9" cy="151.4" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1432;0.1434;1.0000" values="0;0;1;1"/></circle>
<line x1="127.9" y1="300.0" x2="127.9" y2="151.4" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1432;0.1434;1.0000" values="0;0;1;1"/></line>
<circle cx="51.05" cy="297.8" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1514;0.1517;1.0000" values="0;0;1;1"/></circle>
<line x1="51.05" y1="300.0" x2="51.05" y2="297.8" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1514;0.1517;1.0000" values="0;0;1;1"/></line>
<circle cx="172.45" cy="97.81" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></circle>
<line x1="172.45" y1="300.0" x2="172.45" y2="97.81" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1597;0.1600;1.0000" values="0;0;1;1"/></line>
<circle cx="243.17" cy="87.86" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1680;0.1683;1.0000" values="0;0;1;1"/></circle>
<line x1="243.17" y1="300.0" x2="243.17" y2="87.86" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1680;0.1683;1.0000" values="0;0;1;1"/></line>
<circle cx="72.86" cy="252.5" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1763;0.1766;1.0000" values="0;0;1;1"/></circle>
<line x1="72.86" y1="300.0" x2="72.86" y2="252.5" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1763;0.1766;1.0000" values="0;0;1;1"/></line>
<circle cx="311.94" cy="167.22" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1846;0.1848;1.0000" values="0;0;1;1"/></circle>
<line x1="311.94" y1="300.0" x2="311.94" y2="167.22" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1846;0.1848;1.0000" values="0;0;1;1"/></line>
<circle cx="126.64" cy="153.35" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1928;0.1931;1.0000" values="0;0;1;1"/></circle>
<line x1="126.64" y1="300.0" x2="126.64" y2="153.35" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1928;0.1931;1.0000" values="0;0;1;1"/></line>
<circle cx="126.79" cy="153.12" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2011;0.2014;1.0000" values="0;0;1;1"/></circle>
<line x1="126.79" y1="300.0" x2="126.79" y2="153.12" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2011;0.2014;1.0000" values="0;0;1;1"/></line>
<circle cx="63.97" cy="270.83" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2094;0.2097;1.0000" values="0;0;1;1"/></circle>
<line x1="63.97" y1="300.0" x2="63.97" y2="270.83" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2094;0.2097;1.0000" values="0;0;1;1"/></line>
<circle cx="379.2" cy="298.31" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2177;0.2179;1.0000" values="0;0;1;1"/></circle>
<line x1="379.2" y1="300.0" x2="379.2" y2="298.31" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2177;0.2179;1.0000" values="0;0;1;1"/></line>
<circle cx="293.77" cy="139.01" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2259;0.2262;1.0000" values="0;0;1;1"/></circle>
<line x1="293.77" y1="300.0" x2="293.77" y2="139.01" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2259;0.2262;1.0000" values="0;0;1;1"/></line>
<circle cx="338.76" cy="215.83" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2342;0.2345;1.0000" values="0;0;1;1"/></circle>
<line x1="338.76" y1="300.0" x2="338.76" y2="215.83" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2342;0.2345;1.0000" values="0;0;1;1"/></line>
<circle cx="253.24" cy="94.42" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2425;0.2428;1.0000" values="0;0;1;1"/></circle>
<line x1="253.24" y1="300.0" x2="253.24" y2="94.42" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2425;0.2428;1.0000" values="0;0;1;1"/></line>
<circle cx="61.24" cy="276.5" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2508;0.2510;1.0000" values="0;0;1;1"/></circle>
<line x1="61.24" y1="300.0" x2="61.24" y2="276.5" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2508;0.2510;1.0000" values="0;0;1;1"/></line>
<circle cx="158.55" cy="111.01" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;1.0000" values="0;0;1;1"/></circle>
<line x1="158.55" y1="300.0" x2="158.55" y2="111.01" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;1.0000" values="0;0;1;1"/></line>
<circle cx="214.19" cy="80.01" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2673;0.2676;1.0000" values="0;0;1;1"/></circle>
<line x1="214.19" y1="300.0" x2="214.19" y2="80.01" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2673;0.2676;1.0000" values="0;0;1;1"/></line>
<circle cx="88.22" cy="221.71" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2756;0.2759;1.0000" values="0;0;1;1"/></circle>
<line x1="88.22" y1="300.0" x2="88.22" y2="221.71" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2756;0.2759;1.0000" values="0;0;1;1"/></line>
<circle cx="364.15" cy="266.93" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2839;0.2841;1.0000" values="0;0;1;1"/></circle>
<line x1="364.15" y1="300.0" x2="364.15" y2="266.93" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2839;0.2841;1.0000" values="0;0;1;1"/></line>
<circle cx="171.59" cy="98.52" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2921;0.2924;1.0000" values="0;0;1;1"/></circle>
<line x1="171.59" y1="300.0" x2="171.59" y2="98.52" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2921;0.2924;1.0000" values="0;0;1;1"/></line>
<circle cx="101.09" cy="197.17" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3004;0.3007;1.0000" values="0;0;1;1"/></circle>
<line x1="101.09" y1="300.0" x2="101.09" y2="197.17" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3004;0.3007;1.0000" values="0;0;1;1"/></line>
<circle cx="319.78" cy="180.67" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3087;0.3090;1.0000" values="0;0;1;1"/></circle>
<line x1="319.78" y1="300.0" x2="319.78" y2="180.67" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3087;0.3090;1.0000" values="0;0;1;1"/></line>
<circle cx="91.21" cy="215.89" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3170;0.3172;1.0000" values="0;0;1;1"/></circle>
<line x1="91.21" y1="300.0" x2="91.21" y2="215.89" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3170;0.3172;1.0000" values="0;0;1;1"/></line>
<circle cx="356.22" cy="250.62" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3252;0.3255;1.0000" values="0;0;1;1"/></circle>
<line x1="356.22" y1="300.0" x2="356.22" y2="250.62" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3252;0.3255;1.0000" values="0;0;1;1"/></line>
<circle cx="199.53" cy="82.38" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3335;0.3338;1.0000" values="0;0;1;1"/></circle>
<line x1="199.53" y1="300.0" x2="199.53" y2="82.38" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3335;0.3338;1.0000" values="0;0;1;1"/></line>
<circle cx="232.16" cy="82.93" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3418;0.3421;1.0000" values="0;0;1;1"/></circle>
<line x1="232.16" y1="300.0" x2="232.16" y2="82.93" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3418;0.3421;1.0000" values="0;0;1;1"/></line>
<circle cx="163.16" cy="106.25" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3501;0.3503;1.0000" values="0;0;1;1"/></circle>
<line x1="163.16" y1="300.0" x2="163.16" y2="106.25" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3501;0.3503;1.0000" values="0;0;1;1"/></line>
<circle cx="209.95" cy="80.25" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3583;0.3586;1.0000" values="0;0;1;1"/></circle>
<line x1="209.95" y1="300.0" x2="209.95" y2="80.25" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3583;0.3586;1.0000" values="0;0;1;1"/></line>
<circle cx="111.68" cy="178.11" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3666;0.3669;1.0000" values="0;0;1;1"/></circle>
<line x1="111.68" y1="300.0" x2="111.68" y2="178.11" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3666;0.3669;1.0000" values="0;0;1;1"/></line>
<circle cx="62.26" cy="274.39" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3749;0.3752;1.0000" values="0;0;1;1"/></circle>
<line x1="62.26" y1="300.0" x2="62.26" y2="274.39" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3749;0.3752;1.0000" values="0;0;1;1"/></line>
<circle cx="335.74" cy="210.03" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3832;0.3834;1.0000" values="0;0;1;1"/></circle>
<line x1="335.74" y1="300.0" x2="335.74" y2="210.03" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3832;0.3834;1.0000" values="0;0;1;1"/></line>
<circle cx="127.51" cy="152.01" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3914;0.3917;1.0000" values="0;0;1;1"/></circle>
<line x1="127.51" y1="300.0" x2="127.51" y2="152.01" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3914;0.3917;1.0000" values="0;0;1;1"/></line>
<circle cx="307.49" cy="159.9" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/></circle>
<line x1="307.49" y1="300.0" x2="307.49" y2="159.9" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/></line>
<circle cx="118.83" cy="165.95" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4080;0.4083;1.0000" values="0;0;1;1"/></circle>
<line x1="118.83" y1="300.0" x2="118.83" y2="165.95" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4080;0.4083;1.0000" values="0;0;1;1"/></line>
<circle cx="369.69" cy="278.45" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4163;0.4166;1.0000" values="0;0;1;1"/></circle>
<line x1="369.69" y1="300.0" x2="369.69" y2="278.45" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4163;0.4166;1.0000" values="0;0;1;1"/></line>
<circle cx="345.01" cy="228.06" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4246;0.4248;1.0000" values="0;0;1;1"/></circle>
<line x1="345.01" y1="300.0" x2="345.01" y2="228.06" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4246;0.4248;1.0000" values="0;0;1;1"/></line>
<circle cx="299.08" cy="146.8" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4328;0.4331;1.0000" values="0;0;1;1"/></circle>
<line x1="299.08" y1="300.0" x2="299.08" y2="146.8" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4328;0.4331;1.0000" values="0;0;1;1"/></line>
<circle cx="301.72" cy="150.81" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4411;0.4414;1.0000" values="0;0;1;1"/></circle>
<line x1="301.72" y1="300.0" x2="301.72" y2="150.81" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4411;0.4414;1.0000" values="0;0;1;1"/></line>
<circle cx="241.65" cy="87.04" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4494;0.4497;1.0000" values="0;0;1;1"/></circle>
<line x1="241.65" y1="300.0" x2="241.65" y2="87.04" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4494;0.4497;1.0000" values="0;0;1;1"/></line>
<circle cx="290.82" cy="134.86" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4577;0.4579;1.0000" values="0;0;1;1"/></circle>
<line x1="290.82" y1="300.0" x2="290.82" y2="134.86" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4577;0.4579;1.0000" values="0;0;1;1"/></line>
<circle cx="90.42" cy="217.42" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4659;0.4662;1.0000" values="0;0;1;1"/></circle>
<line x1="90.42" y1="300.0" x2="90.42" y2="217.42" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4659;0.4662;1.0000" values="0;0;1;1"/></line>
<circle cx="207.19" cy="80.61" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4742;0.4745;1.0000" values="0;0;1;1"/></circle>
<line x1="207.19" y1="300.0" x2="207.19" y2="80.61" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4742;0.4745;1.0000" values="0;0;1;1"/></line>
<circle cx="322.92" cy="186.24" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4825;0.4828;1.0000" values="0;0;1;1"/></circle>
<line x1="322.92" y1="300.0" x2="322.92" y2="186.24" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4825;0.4828;1.0000" values="0;0;1;1"/></line>
<circle cx="116.36" cy="170.08" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4908;0.4910;1.0000" values="0;0;1;1"/></circle>
<line x1="116.36" y1="300.0" x2="116.36" y2="170.08" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4908;0.4910;1.0000" values="0;0;1;1"/></line>
<circle cx="354.65" cy="247.41" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4990;0.4993;1.0000" values="0;0;1;1"/></circle>
<line x1="354.65" y1="300.0" x2="354.65" y2="247.41" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4990;0.4993;1.0000" values="0;0;1;1"/></line>
<circle cx="342.89" cy="223.89" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5073;0.5076;1.0000" values="0;0;1;1"/></circle>
<line x1="342.89" y1="300.0" x2="342.89" y2="223.89" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5073;0.5076;1.0000" values="0;0;1;1"/></line>
<circle cx="185.17" cy="88.81" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5156;0.5159;1.0000" values="0;0;1;1"/></circle>
<line x1="185.17" y1="300.0" x2="185.17" y2="88.81" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5156;0.5159;1.0000" values="0;0;1;1"/></line>
<circle cx="170.52" cy="99.43" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5239;0.5241;1.0000" values="0;0;1;1"/></circle>
<line x1="170.52" y1="300.0" x2="170.52" y2="99.43" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5239;0.5241;1.0000" values="0;0;1;1"/></line>
<circle cx="198.94" cy="82.57" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5321;0.5324;1.0000" values="0;0;1;1"/></circle>
<line x1="198.94" y1="300.0" x2="198.94" y2="82.57" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5321;0.5324;1.0000" values="0;0;1;1"/></line>
<circle cx="177.31" cy="94.01" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5404;0.5407;1.0000" values="0;0;1;1"/></circle>
<line x1="177.31" y1="300.0" x2="177.31" y2="94.01" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5404;0.5407;1.0000" values="0;0;1;1"/></line>
<circle cx="378.3" cy="296.44" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5487;0.5490;1.0000" values="0;0;1;1"/></circle>
<line x1="378.3" y1="300.0" x2="378.3" y2="296.44" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5487;0.5490;1.0000" values="0;0;1;1"/></line>
<circle cx="177.58" cy="93.82" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5570;0.5572;1.0000" values="0;0;1;1"/></circle>
<line x1="177.58" y1="300.0" x2="177.58" y2="93.82" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5570;0.5572;1.0000" values="0;0;1;1"/></line>
<circle cx="58.86" cy="281.47" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5652;0.5655;1.0000" values="0;0;1;1"/></circle>
<line x1="58.86" y1="300.0" x2="58.86" y2="281.47" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5652;0.5655;1.0000" values="0;0;1;1"/></line>
<circle cx="80.78" cy="236.46" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5735;0.5738;1.0000" values="0;0;1;1"/></circle>
<line x1="80.78" y1="300.0" x2="80.78" y2="236.46" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5735;0.5738;1.0000" values="0;0;1;1"/></line>
<circle cx="286.97" cy="129.65" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5818;0.5821;1.0000" values="0;0;1;1"/></circle>
<line x1="286.97" y1="300.0" x2="286.97" y2="129.65" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5818;0.5821;1.0000" values="0;0;1;1"/></line>
<circle cx="377.63" cy="295.04" r="4" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5901;0.5903;1.0000" values="0;0;1;1"/></circle>
<line x1="377.63" y1="300.0" x2="377.63" y2="295.04" stroke="#e5484d" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5901;0.5903;1.0000" values="0;0;1;1"/></line>
<rect x="450" y="80" width="290" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="522.5" y1="80" x2="522.5" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="450" y1="135.0" x2="740" y2="135.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="595.0" y1="80" x2="595.0" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="450" y1="190.0" x2="740" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="667.5" y1="80" x2="667.5" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="450" y1="245.0" x2="740" y2="245.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="740" y="320" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">サンプル数</text>
<text x="450" y="72" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">推定した積分</text>
<line x1="450" y1="159.94" x2="740" y2="159.94" stroke="#2ea043" stroke-width="2" stroke-dasharray="5 4"/>
<text x="740" y="153.94" text-anchor="end" style="font-size:11px;font-weight:700;fill:#2ea043">真の値 2/π ≒ 0.64</text>
<circle cx="454.53" cy="191.03" r="5" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="0;0;1;1"/><animate attributeName="cx" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0690;0.0772;0.0855;0.0938;0.1021;0.1103;0.1186;0.1269;0.1352;0.1434;0.1517;0.1600;0.1683;0.1766;0.1848;0.1931;0.2014;0.2097;0.2179;0.2262;0.2345;0.2428;0.2510;0.2593;0.2676;0.2759;0.2841;0.2924;0.3007;0.3090;0.3172;0.3255;0.3338;0.3421;0.3503;0.3586;0.3669;0.3752;0.3834;0.3917;0.4000;0.4083;0.4166;0.4248;0.4331;0.4414;0.4497;0.4579;0.4662;0.4745;0.4828;0.4910;0.4993;0.5076;0.5159;0.5241;0.5324;0.5407;0.5490;0.5572;0.5655;0.5738;0.5821;0.5903;1.0000" values="454.53;454.53;459.06;463.59;468.12;472.66;477.19;481.72;486.25;490.78;495.31;499.84;504.38;508.91;513.44;517.97;522.5;527.03;531.56;536.09;540.62;545.16;549.69;554.22;558.75;563.28;567.81;572.34;576.88;581.41;585.94;590.47;595;599.53;604.06;608.59;613.12;617.66;622.19;626.72;631.25;635.78;640.31;644.84;649.38;653.91;658.44;662.97;667.5;672.03;676.56;681.09;685.62;690.16;694.69;699.22;703.75;708.28;712.81;717.34;721.88;726.41;730.94;735.47;740;740"/><animate attributeName="cy" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0690;0.0772;0.0855;0.0938;0.1021;0.1103;0.1186;0.1269;0.1352;0.1434;0.1517;0.1600;0.1683;0.1766;0.1848;0.1931;0.2014;0.2097;0.2179;0.2262;0.2345;0.2428;0.2510;0.2593;0.2676;0.2759;0.2841;0.2924;0.3007;0.3090;0.3172;0.3255;0.3338;0.3421;0.3503;0.3586;0.3669;0.3752;0.3834;0.3917;0.4000;0.4083;0.4166;0.4248;0.4331;0.4414;0.4497;0.4579;0.4662;0.4745;0.4828;0.4910;0.4993;0.5076;0.5159;0.5241;0.5324;0.5407;0.5490;0.5572;0.5655;0.5738;0.5821;0.5903;1.0000" values="191.03;191.03;154.49;136.16;122.24;130.17;136.24;141.8;134.09;128.08;130.42;145.63;141.65;137.51;145.72;147.16;147.54;147.87;154.7;162.26;161.1;163.71;160.56;165.6;163.32;159.99;162.36;166.24;163.82;164.97;165.49;167.12;169.73;167.08;164.6;162.94;160.64;161.11;164.09;165.27;164.94;164.82;164.84;167.49;168.86;168.37;167.99;166.27;165.61;166.67;164.95;165.37;165.46;167;168.06;166.62;165.42;163.96;162.76;165.02;163.84;165.77;166.91;166.31;168.33;168.33"/></circle>
<path d="M454.53,191.03 L459.06,154.49 L463.59,136.16 L468.12,122.24 L472.66,130.17 L477.19,136.24 L481.72,141.8 L486.25,134.09 L490.78,128.08 L495.31,130.42 L499.84,145.63 L504.38,141.65 L508.91,137.51 L513.44,145.72 L517.97,147.16 L522.5,147.54 L527.03,147.87 L531.56,154.7 L536.09,162.26 L540.62,161.1 L545.16,163.71 L549.69,160.56 L554.22,165.6 L558.75,163.32 L563.28,159.99 L567.81,162.36 L572.34,166.24 L576.88,163.82 L581.41,164.97 L585.94,165.49 L590.47,167.12 L595.0,169.73 L599.53,167.08 L604.06,164.6 L608.59,162.94 L613.12,160.64 L617.66,161.11 L622.19,164.09 L626.72,165.27 L631.25,164.94 L635.78,164.82 L640.31,164.84 L644.84,167.49 L649.38,168.86 L653.91,168.37 L658.44,167.99 L662.97,166.27 L667.5,165.61 L672.03,166.67 L676.56,164.95 L681.09,165.37 L685.62,165.46 L690.16,167.0 L694.69,168.06 L699.22,166.62 L703.75,165.42 L708.28,163.96 L712.81,162.76 L717.34,165.02 L721.88,163.84 L726.41,165.77 L730.94,166.91 L735.47,166.31 L740.0,168.33" fill="none" stroke="#e5484d" stroke-width="2.5" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5983;0.5986;1.0000" values="0;0;1;1"/></path>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 1 個:推定 0.50（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.1018;0.1021;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 5 個:推定 0.77（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1018;0.1021;0.1349;0.1352;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 9 個:推定 0.78（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1349;0.1352;0.1680;0.1683;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 13 個:推定 0.74（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1680;0.1683;0.2011;0.2014;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 17 個:推定 0.69（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2011;0.2014;0.2342;0.2345;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 22 個:推定 0.63（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2342;0.2345;0.2673;0.2676;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 26 個:推定 0.63（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2673;0.2676;0.3004;0.3007;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 30 個:推定 0.61（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3004;0.3007;0.3335;0.3338;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 34 個:推定 0.62（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3335;0.3338;0.3666;0.3669;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 38 個:推定 0.62（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3666;0.3669;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 43 個:推定 0.60（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;0.4328;0.4331;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 47 個:推定 0.61（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4328;0.4331;0.4659;0.4662;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 51 個:推定 0.61（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4659;0.4662;0.4990;0.4993;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 55 個:推定 0.61（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4990;0.4993;0.5321;0.5324;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 59 個:推定 0.61（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5321;0.5324;0.5652;0.5655;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">サンプル 64 個:推定 0.60（真の値 0.64）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5652;0.5655;0.5983;0.5986;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="376" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">誤差はサンプル数の平方根に反比例。4 倍に増やして、誤差が半分。<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
</svg>

<!-- fig:monte-carlo-converge:end -->

## 基本の推定量 {#estimator}

積分をサンプルの平均で近似します。

```text
∫ f(ω) dω  ≈  (1 / N) × Σ_k  f(ω_k) / pdf(ω_k)          ω_k は確率密度 pdf で選んだ k 番目のランダムな方向
```

`N` はサンプル数、`ω_k` はランダムに選んだ k 番目の方向、`pdf(ω_k)` はその方向を選ぶ確率密度（偏りの補正に使います）です。`f(ω_k) / pdf(ω_k)` が 1 サンプルの推定値で、確率で割るのでよく選ばれる方向は重みが小さくなります。確率で割ることでサンプルの選び方に偏りがあっても、平均すると真の積分値に近づく（偏りのない推定）ことが保証されます。

## 一様なサンプリング {#uniform}

半球を一様に（どの方向も同じ確率で）サンプリングすると、`pdf = 1 / (2π)` です。放射照度の推定は次のとおりです。

```text
E ≈ (1 / N) × Σ L_i(ω_k) × cosθ_k / (1 / 2π) = (2π / N) × Σ L_i(ω_k) × cosθ_k
```

## 重点サンプリング: サンプルを無駄にしない {#importance}

放射照度の積分には余弦（`cosθ`）が掛かっています。法線に近い方向（`cosθ` が大きい）は寄与が大きく、横に近い方向（`cosθ` が小さい）は寄与が小さいです。一様にサンプルすると寄与の小さい方向にサンプルを無駄遣いします。寄与の大きい方向を多めに選ぶのが、重点サンプリングです。

### 余弦重み付きサンプリング

`pdf = cosθ / π`（余弦に比例）でサンプルします。拡散反射の積分で最も自然な選び方です。円盤の上に一様に点を打って半球の表面へ持ち上げると、自動的に `cosθ` に比例した分布になります（Malley の方法）。

```hlsl
// 余弦重み付きの半球サンプル（ローカル座標、z が法線）。pdf = cosθ / π。u1, u2 は 0..1 の乱数
float3 CosineHemisphere(float u1, float u2) {
  float r = sqrt(u1);                              // 円盤上に一様にサンプルして、半球へ持ち上げる
  float phi = 2.0 * 3.14159265 * u2;
  return float3(r * cos(phi), r * sin(phi), sqrt(max(0.0, 1.0 - u1)));
}
```

余弦重み付きでサンプルすると、拡散反射の式がほぼ消えます。

```text
L_o = ∫ (albedo / π) × L_i(ω) × cosθ dω
    ≈ (1 / N) × Σ (albedo / π) × L_i(ω_k) × cosθ_k / (cosθ_k / π)
    = albedo × (1 / N) × Σ L_i(ω_k)                     ← cosθ と π が約分されて消える
```

サンプルした方向の `L_i` を平均して、`albedo` を掛けるだけです。

## ノイズと収束を測る {#measure}

入射光が一様な環境光 0.2 と太陽方向のきつい山 `5 · max(0, d)¹⁶`（`d` は太陽方向との内積）でできている点で、放射照度を推定して誤差を測りました（C++、MSVC `/W4`）。基準値は余弦サンプリング 2²⁵ 個の平均で、`E = 2.248` です（環境光だけなら `0.2π = 0.628`）。各 `N` で 4000 回推定して、相対 RMS 誤差（`E` に対する割合）を求めました。

- `N = 1`: 一様 2.18、余弦 1.47、余弦 + R2 列 1.48、余弦 + 層別 1.46
- `N = 4`: 一様 1.10、余弦 0.728、余弦 + R2 0.522、余弦 + 層別 0.598
- `N = 16`: 一様 0.554、余弦 0.366、余弦 + R2 0.148、余弦 + 層別 0.160
- `N = 64`: 一様 0.273、余弦 0.186、余弦 + R2 0.039、余弦 + 層別 0.055
- `N = 256`: 一様 0.138、余弦 0.089、余弦 + R2 0.0116、余弦 + 層別 0.0153

<svg class="fig flow" viewBox="0 0 720 260" role="img" aria-label="N = 64 での相対 RMS 誤差。一様 0.273、余弦 0.186、層別 0.055、R2 列 0.039"><text x="14" y="22" class="fig-title">N = 64 本での相対誤差（4000 回の平均。小さいほど良い）</text>
<line x1="60" y1="200" x2="690" y2="200" stroke="currentColor" stroke-width="1.5"/>
<g stroke-width="2"><rect x="110" y="48" width="100" height="152" fill="rgba(229,72,77,0.28)" stroke="#e5484d"/><rect x="250" y="96" width="100" height="104" fill="rgba(229,170,40,0.3)" stroke="#e5aa28"/><rect x="390" y="169" width="100" height="31" fill="rgba(60,160,90,0.3)" stroke="#3ca05a"/><rect x="530" y="178" width="100" height="22" fill="rgba(76,139,245,0.28)" stroke="#4c8bf5"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="160" y="42">0.273</text><text x="300" y="90">0.186</text><text x="440" y="163">0.055</text><text x="580" y="172">0.039</text>
<text x="160" y="220">一様乱数</text><text x="300" y="220">余弦重み付き</text><text x="440" y="220">余弦 + 層別</text><text x="580" y="220">余弦 + R2 列</text></g>
<text x="360" y="248" text-anchor="middle" style="font-size:12px">余弦重み付きで約 1.5 倍、R2 列でさらに約 4.8 倍、一様乱数と比べて約 7 倍改善</text></svg>

結果から 3 つのことが分かります。

1. 誤差は `1/√N` で減ります。一様乱数で `N` を 1 から 256 へ 256 倍にすると、誤差は 2.18 から 0.138 へ約 15.8 分の 1（`√256 = 16`）になりました。ノイズを半分にするのにサンプルを 4 倍にする必要があります。
2. 余弦重み付きサンプリングは一様より約 1.5 倍誤差が小さいです（分散で約 2.2 倍）。サンプルを寄与の大きい方向に集めたためです。
3. 乱数の選び方でも差が出ます。R2 列（低食い違い量列）は `N = 256` で 0.0116 で、白色乱数の余弦（0.089）の約 7.7 分の 1 です。`N = 64` の層別サンプリングも白色乱数の約 3.4 倍良くなりました。`N = 1` では差がありません。

低食い違い量列はサンプルの偏り（団子と空き）を避けて、均等に散らします。誤差が `1/N` に近い速さで減るのが、白色乱数と違う点です。

## 乱数と直交基底 {#sequence}

R2 列は 2 次元の点を黄金比に似た定数（一般化した黄金比 `g ≈ 1.3247`）で、並べる列です。

```hlsl
// R2 列（Roberts）。k 番目の 2 次元の点 (0..1)。shift は画素ごとのランダムなずらし（Cranley–Patterson 回転）
float2 R2Sequence(uint k, float2 shift) {
  const float g = 1.32471795724474602596;
  const float2 a = float2(1.0 / g, 1.0 / (g * g));
  return frac(shift + (k + 1) * a);
}
```

画素ごとに `shift` を変えてずらします。同じ列を全画素に使うと画素間でパターンがそろって見えるからです。

サンプルしたローカル座標の方向を法線の向きへ回すには、直交基底（接線 `t`、従接線 `b`、法線 `n`）が要ります。Duff ら（2017）の方法は場合分けが少なく、法線がどの向きでも安定します。

```hlsl
// 法線 n から、直交基底 (t, b, n) を作る（Duff ら 2017）
void BuildBasis(float3 n, out float3 t, out float3 b) {
  float sign = (n.z >= 0.0) ? 1.0 : -1.0;
  float a = -1.0 / (sign + n.z);
  float c = n.x * n.y * a;
  t = float3(1.0 + sign * n.x * n.x * a, sign * c, -sign * n.x);
  b = float3(c, sign + n.y * n.y * a, -n.y);
}

float3 LocalToWorld(float3 v, float3 n) {
  float3 t, b;
  BuildBasis(n, t, b);
  return t * v.x + b * v.y + n * v.z;
}
```

100 万個のランダムな法線（上半球と下半球の両方）で、直交性と長さの誤差の最大を測りました。結果は `4.5 × 10⁻¹⁶` で倍精度の丸め誤差の範囲でした。

次の関数は拡散の間接光を `N` 本のレイで推定する例です。`TraceRadiance` はその方向から来る光を返す関数です（ここでは宣言だけにして、レイトレーシングの実装は省いています）。

```hlsl
// その方向から来る光。ここでは、空の明るさだけの仮の実装（実際はレイを飛ばして、当たった面の光を返す）
float3 TraceRadiance(float3 position, float3 direction) {
  return lerp(float3(0.2, 0.25, 0.3), float3(0.6, 0.8, 1.0), saturate(direction.y * 0.5 + 0.5));
}

cbuffer McConstants : register(b0) {
  uint g_frame_index;
  uint3 _pad;
};

float3 EstimateDiffuseIndirect(float3 position, float3 normal, float3 albedo, uint2 pixel) {
  // 画素ごとのずらし。整数のハッシュから 0..1 の値を作る（一例）
  float2 shift = frac(float2(pixel) * float2(0.7548776662, 0.5698402909));
  float3 sum = 0.0;
  const uint kRays = 4;
  for (uint k = 0; k < kRays; ++k) {
    float2 u = R2Sequence(g_frame_index * kRays + k, shift);        // 低食い違い量列（フレームをまたいでも続く）
    float3 local_dir = CosineHemisphere(u.x, u.y);
    float3 dir = LocalToWorld(local_dir, normal);                     // 法線の向きへ回す
    sum += TraceRadiance(position, dir);
  }
  return albedo * sum / kRays;          // 余弦重み付きなので、albedo と平均だけ
}

float4 MonteCarloPS(float4 pos : SV_Position, float3 world_pos : TEXCOORD0, float3 normal : TEXCOORD1) : SV_Target {
  return float4(EstimateDiffuseIndirect(world_pos, normalize(normal), float3(0.8, 0.8, 0.8), uint2(pos.xy)), 1.0);
}
```

!!! note "確かめた範囲"
    誤差の表と直交基底の誤差は C++（MSVC `/W4`）で実行して測った値です。HLSL は `fxc`（`ps_5_0`、`TraceRadiance` を仮の実装にしたもの）でコンパイルして、エラーが出ないことを確かめました。GPU での実行は確認していません。

## リアルタイムでは: 少ないサンプル + デノイズ {#realtime}

リアルタイムの GI では 1 画素あたり 1〜数本のレイしか飛ばせません。ノイズだらけの結果を後処理でなめらかにします。

- ブルー ノイズはサンプルの乱数に使います。ホワイト ノイズよりノイズが目立ちません（[Dithered Transparency](../../translucency/alpha-test/dither.md)）。
- 時間蓄積は前のフレームの結果と混ぜて、数十フレームのサンプルを集めます（[Fighting Noise](../rt-gi/noise.md)）。
- 空間フィルタ（デノイザー）は隣の画素と混ぜます。法線と深度が近い画素だけを混ぜます（[Fighting Noise](../rt-gi/noise.md)）。
- 低食い違い量列（Halton、Sobol、R2）はランダムより偏りなく散らします。実測で同じ本数でも誤差が小さくなりました。
- 再利用（ReSTIR）は隣の画素や前のフレームのサンプルを再利用して、実質的なサンプル数を増やします（[ReSTIR GI](../rt-gi/restir.md)）。

## よくあるミス {#mistakes}

??? failure "サンプルを増やしても、ノイズが減るのが遅い"
    原因は誤差が `1/√N` でしか減らないことです。実測で 256 倍のサンプルで、誤差は約 16 分の 1 でした。重点サンプリング、低食い違い量列、デノイズを併用します。

??? failure "余弦重み付きでサンプルしたのに、`cosθ` を掛けて暗くなった"
    原因は `pdf = cosθ / π` で割ったあとの式に `cosθ` を重ねて掛けていることです。余弦重み付きなら `cosθ` と `π` は消えて、`albedo × 平均` だけです。

??? failure "全画素で同じ乱数列を使って、画面に縞や格子が出る"
    原因は画素ごとのずらしがないことです。画素ごとに Cranley–Patterson 回転（`shift`）を変えます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] ランダムに試して、平均を取ります。偏りはなく誤差は `1/√N` で減ります。
    - [x] 余弦重み付きサンプリングは、拡散反射を `albedo × 平均` にします。誤差は一様の約 2/3 です。
    - [x] 低食い違い量列（R2）は、同じ本数で誤差を大きく減らします（256 本で約 7.7 分の 1）。
    - [x] リアルタイムは少数サンプルとデノイズが基本です。

## 参考 {#references}

このページは次の資料を読まずに書きました。数字は自分で書いた C++ の実測です。

- Pharr, Jakob, Humphreys, "Physically Based Rendering: From Theory to Implementation", 4th Edition, MIT Press, 2023（モンテカルロ積分、重点サンプリング）
- Veach, "Robust Monte Carlo Methods for Light Transport Simulation", Ph.D. thesis, Stanford University, 1997
- Duff, Burgess, Christensen, Hery, Kensler, Liani, Villemin, "Building an Orthonormal Basis, Revisited", Journal of Computer Graphics Techniques, Vol. 6, No. 1, 2017
- Kajiya, "The Rendering Equation", SIGGRAPH 1986（レンダリング方程式の原典）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明、放射照度、SH の章）

## 関連ページ

- [GI Theory](index.md)
- [Ray-Traced GI](../rt-gi/index.md)
- [Taxonomy of Methods](taxonomy.md)
