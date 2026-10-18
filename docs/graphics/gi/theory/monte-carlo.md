---
title: Monte Carlo Integration
tags:
  - 描画
---

# Monte Carlo Integration

**レンダリング方程式は、一般に、解析的には解けません**。**そこで、ランダムに方向を選んで試し、その平均を取る「モンテカルロ積分」**で**近似**します。**サンプルが少ないとノイズが出ますが、数を増やすと、真の値に近づきます**。このページでは、**モンテカルロの考え方・ノイズと収束・重点サンプリング**を説明します。

!!! tip "ポイント"
    - **ランダムな方向でサンプルして、平均 ＝ 積分の近似**。
    - **誤差は、サンプル数の平方根に反比例して減る**（4 倍で、半分）。
    - **重点サンプリング ＝ 寄与の大きい方向を、多めに選ぶ**。
    - **リアルタイムでは、少ないサンプル ＋ デノイズ**が**基本**。

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

## Monte Carlo Integration {#モンテカルロ積分}
**半球の積分**を**ランダムな方向をサンプルして平均する**ことで、**近似**する方法です。

<div class="formula">E ≈ (1/N) · Σ  L_i(ω_k) · (n·ω_k) / pdf(ω_k)</div>

| 項 | 意味 |
| --- | --- |
| **N** | サンプル数 |
| **ω_k** | k 番目のランダムな方向 |
| <strong>pdf(ω_k)</strong> | その方向を選ぶ確率密度（サンプリングの偏りの補正） |

**余弦重み付きサンプリング**（`pdf = cosθ / π`）を使えば、**`(n·ω) / pdf = π`** と**定数**になり、**単純な平均**になります（[AO Theory](../../ao/theory/index.md)と同じ）。

| 性質 | 内容 |
| --- | --- |
| **偏りがない** | サンプルを増やすと**真の値に収束** |
| **ノイズ** | **誤差は、`1/√N` で減る**（**4 倍のサンプルで誤差は半分**） |
| **リアルタイム** | **少ないサンプル（画素あたり 1 本）＋ デノイズ・時間蓄積**で補う |

**サンプルの方向をどう選ぶか**（重要度サンプリング・ブルー ノイズ）、**ノイズをどう消すか**（時間蓄積・空間フィルタ・ReSTIR）が、**レイトレ GI の中心**です。

## Common Mistakes {#よくあるミス}

??? failure "サンプルを増やしても、ノイズが減るのが遅い"
    **重点サンプリング**と**デノイズ**を併用する。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **ランダムに試して平均を取る**
    - [x] **少数サンプル ＋ デノイズ**が基本

## References {#参考}

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## Related Pages {#関連ページ}

- [GI Theory](index.md)
- [Ray-Traced GI](../rt-gi/index.md)
- [Taxonomy of Methods](taxonomy.md)
