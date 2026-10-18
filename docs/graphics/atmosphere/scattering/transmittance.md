---
title: Transmittance
tags:
  - 描画
---

# Transmittance

<strong>光が大気を通ると、散乱や吸収で弱まります</strong>。<strong>弱まる割合が透過率で、Beer の法則（指数）で表します</strong>。このページでは、透過率の計算を説明します。

!!! tip "ポイント"
    - 透過率 ＝ exp(−∫ 消散係数 ds)。
    - 波長（RGB）ごとに計算する。
    - 長い道のり ＝ 低い太陽 ＝ 赤くなる（青が先に消える）。
    - LUT に事前計算しておくと速い。

<!-- fig:sun-transmittance:begin -->

<svg class="fig illust motion" data-fig="sun-transmittance" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-sun-transmittance" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">透過率:太陽が低いほど、光が長く大気を通り、青が先に消える</text>
<rect x="50" y="80" width="330" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="132.5" y1="80" x2="132.5" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="135.0" x2="380" y2="135.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="215.0" y1="80" x2="215.0" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="190.0" x2="380" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="297.5" y1="80" x2="297.5" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="245.0" x2="380" y2="245.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="380" y="320" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">大気を通る長さ（天頂で 1）</text>
<text x="50" y="72" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">残る光の割合</text>
<path d="M50.0,80.0 L56.6,85.22 L63.2,90.31 L69.8,95.28 L76.4,100.14 L83.0,104.88 L89.6,109.5 L96.2,114.02 L102.8,118.43 L109.4,122.74 L116.0,126.94 L122.6,131.05 L129.2,135.05 L135.8,138.96 L142.4,142.78 L149.0,146.51 L155.6,150.15 L162.2,153.7 L168.8,157.17 L175.4,160.56 L182.0,163.87 L188.6,167.1 L195.2,170.25 L201.8,173.32 L208.4,176.33 L215.0,179.26 L221.6,182.12 L228.2,184.92 L234.8,187.65 L241.4,190.31 L248.0,192.91 L254.6,195.45 L261.2,197.93 L267.8,200.35 L274.4,202.72 L281.0,205.02 L287.6,207.28 L294.2,209.47 L300.8,211.62 L307.4,213.72 L314.0,215.76 L320.6,217.76 L327.2,219.71 L333.8,221.62 L340.4,223.47 L347.0,225.29 L353.6,227.06 L360.2,228.79 L366.8,230.48 L373.4,232.13 L380.0,233.74" fill="none" stroke="#e5484d" stroke-width="4" opacity="1"/>
<path d="M50.0,80.0 L56.6,88.8 L63.2,97.24 L69.8,105.35 L76.4,113.13 L83.0,120.6 L89.6,127.77 L96.2,134.66 L102.8,141.27 L109.4,147.61 L116.0,153.7 L122.6,159.55 L129.2,165.17 L135.8,170.56 L142.4,175.73 L149.0,180.7 L155.6,185.47 L162.2,190.05 L168.8,194.45 L175.4,198.67 L182.0,202.72 L188.6,206.61 L195.2,210.34 L201.8,213.92 L208.4,217.37 L215.0,220.67 L221.6,223.84 L228.2,226.89 L234.8,229.81 L241.4,232.61 L248.0,235.31 L254.6,237.89 L261.2,240.38 L267.8,242.76 L274.4,245.05 L281.0,247.25 L287.6,249.36 L294.2,251.38 L300.8,253.32 L307.4,255.19 L314.0,256.98 L320.6,258.7 L327.2,260.35 L333.8,261.94 L340.4,263.46 L347.0,264.92 L353.6,266.32 L360.2,267.67 L366.8,268.96 L373.4,270.2 L380.0,271.39" fill="none" stroke="#2ea043" stroke-width="4" opacity="1"/>
<path d="M50.0,80.0 L56.6,96.75 L63.2,112.23 L69.8,126.53 L76.4,139.74 L83.0,151.94 L89.6,163.21 L96.2,173.63 L102.8,183.25 L109.4,192.14 L116.0,200.35 L122.6,207.94 L129.2,214.95 L135.8,221.43 L142.4,227.41 L149.0,232.94 L155.6,238.04 L162.2,242.76 L168.8,247.12 L175.4,251.15 L182.0,254.87 L188.6,258.3 L195.2,261.48 L201.8,264.41 L208.4,267.12 L215.0,269.62 L221.6,271.94 L228.2,274.07 L234.8,276.05 L241.4,277.87 L248.0,279.56 L254.6,281.11 L261.2,282.55 L267.8,283.88 L274.4,285.11 L281.0,286.24 L287.6,287.29 L294.2,288.26 L300.8,289.15 L307.4,289.98 L314.0,290.74 L320.6,291.45 L327.2,292.1 L333.8,292.7 L340.4,293.25 L347.0,293.77 L353.6,294.24 L360.2,294.68 L366.8,295.09 L373.4,295.46 L380.0,295.81" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<line x1="77.5" y1="80" x2="77.5" y2="300" stroke="#e5aa28" stroke-width="2.5"><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.0832;0.1072;0.1311;0.1551;0.1790;0.2030;0.2269;0.2509;0.2748;0.2988;0.3227;0.3467;0.3706;0.3946;0.4185;0.4425;0.4664;0.4904;0.5143;0.5383;0.5622;0.5862;0.6101;0.6341;0.6580;0.6820;0.7059;0.7299;0.7538;0.7778;1.0000" values="77.5;77.5;77.54;77.64;77.83;78.09;78.43;78.85;79.37;79.98;80.7;81.54;82.52;83.65;84.96;86.47;88.23;90.27;92.66;95.48;98.84;102.88;107.82;113.96;121.76;131.98;145.88;165.84;196.76;250.92;369.78;380;380"/><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.0832;0.1072;0.1311;0.1551;0.1790;0.2030;0.2269;0.2509;0.2748;0.2988;0.3227;0.3467;0.3706;0.3946;0.4185;0.4425;0.4664;0.4904;0.5143;0.5383;0.5622;0.5862;0.6101;0.6341;0.6580;0.6820;0.7059;0.7299;0.7538;0.7778;1.0000" values="77.5;77.5;77.54;77.64;77.83;78.09;78.43;78.85;79.37;79.98;80.7;81.54;82.52;83.65;84.96;86.47;88.23;90.27;92.66;95.48;98.84;102.88;107.82;113.96;121.76;131.98;145.88;165.84;196.76;250.92;369.78;380;380"/></line>
<rect x="430" y="90" width="300" height="200" fill="#7dd3fc"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.0832;0.1072;0.1311;0.1551;0.1790;0.2030;0.2269;0.2509;0.2748;0.2988;0.3227;0.3467;0.3706;0.3946;0.4185;0.4425;0.4664;0.4904;0.5143;0.5383;0.5622;0.5862;0.6101;0.6341;0.6580;0.6820;0.7059;0.7299;0.7538;0.7778;1.0000" values="#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7dd3fc;#7ed3fb;#80d2f8;#82d0f4;#85cff0;#88cdeb;#8ccbe5;#91c9de;#98c5d3;#a1c1c6;#aebab2;#c2af93;#e69d5d;#33264a;#1e1b4b;#1e1b4b"/></rect>
<rect x="430" y="250" width="300" height="40" fill="#334155"/>
<circle cx="580" cy="200" r="26" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0832;0.1072;0.1311;0.1551;0.1790;0.2030;0.2269;0.2509;0.2748;0.2988;0.3227;0.3467;0.3706;0.3946;0.4185;0.4425;0.4664;0.4904;0.5143;0.5383;0.5622;0.5862;0.6101;0.6341;0.6580;0.6820;0.7059;0.7299;0.7538;0.7778;1.0000" values="#ffffff;#ffffff;#f4e4c2;#f4e4c2;#f4e3c2;#f4e3c1;#f4e3c1;#f4e3c0;#f4e2bf;#f3e2be;#f3e1bd;#f3e1bc;#f3e0ba;#f2dfb9;#f2deb6;#f1ddb4;#f1dbb1;#f0daae;#efd8ab;#efd6a7;#eed4a2;#ecd19d;#ebcd97;#e9c990;#e7c487;#e5be7d;#e1b772;#ddad63;#d8a152;#d08f3d;#c47524;#b04e0c;#af4b0b;#af4b0b"/><animate attributeName="cy" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0832;0.1072;0.1311;0.1551;0.1790;0.2030;0.2269;0.2509;0.2748;0.2988;0.3227;0.3467;0.3706;0.3946;0.4185;0.4425;0.4664;0.4904;0.5143;0.5383;0.5622;0.5862;0.6101;0.6341;0.6580;0.6820;0.7059;0.7299;0.7538;0.7778;1.0000" values="200;200;100;100.2;100.79;101.77;103.13;104.89;107.02;109.53;112.41;115.64;119.23;123.16;127.43;132.01;136.91;142.1;147.57;153.31;159.31;165.54;172;178.66;185.5;192.52;199.68;206.98;214.39;221.89;229.47;237.1;244.77;244.77"/></circle>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 90° → 大気を通る長さ 1.0<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0829;0.0832;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 86° → 大気を通る長さ 1.0<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0829;0.0832;0.1069;0.1072;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 83° → 大気を通る長さ 1.0<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1069;0.1072;0.1308;0.1311;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 80° → 大気を通る長さ 1.0<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1308;0.1311;0.1548;0.1551;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 77° → 大気を通る長さ 1.0<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1548;0.1551;0.1787;0.1790;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 74° → 大気を通る長さ 1.0<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1787;0.1790;0.2027;0.2030;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 71° → 大気を通る長さ 1.1<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2027;0.2030;0.2266;0.2269;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 68° → 大気を通る長さ 1.1<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2266;0.2269;0.2506;0.2509;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 65° → 大気を通る長さ 1.1<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2506;0.2509;0.2745;0.2748;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 62° → 大気を通る長さ 1.1<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2745;0.2748;0.2985;0.2988;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 59° → 大気を通る長さ 1.2<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2985;0.2988;0.3224;0.3227;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 56° → 大気を通る長さ 1.2<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3224;0.3227;0.3464;0.3467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 53° → 大気を通る長さ 1.2<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3464;0.3467;0.3703;0.3706;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 50° → 大気を通る長さ 1.3<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3703;0.3706;0.3943;0.3946;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 47° → 大気を通る長さ 1.4<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3943;0.3946;0.4182;0.4185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 44° → 大気を通る長さ 1.4<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4182;0.4185;0.4422;0.4425;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 41° → 大気を通る長さ 1.5<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4422;0.4425;0.4661;0.4664;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 38° → 大気を通る長さ 1.6<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4661;0.4664;0.4901;0.4904;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 35° → 大気を通る長さ 1.7<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4901;0.4904;0.5140;0.5143;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 32° → 大気を通る長さ 1.9<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5140;0.5143;0.5380;0.5383;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 29° → 大気を通る長さ 2.0<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5380;0.5383;0.5619;0.5622;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 26° → 大気を通る長さ 2.3<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5619;0.5622;0.5859;0.5862;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 23° → 大気を通る長さ 2.5<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5859;0.5862;0.6098;0.6101;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 20° → 大気を通る長さ 2.9<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6098;0.6101;0.6338;0.6341;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 17° → 大気を通る長さ 3.4<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6338;0.6341;0.6577;0.6580;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 14° → 大気を通る長さ 4.1<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6577;0.6580;0.6817;0.6820;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 11° → 大気を通る長さ 5.2<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6817;0.6820;0.7056;0.7059;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 8° → 大気を通る長さ 7.1<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7056;0.7059;0.7296;0.7299;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 5° → 大気を通る長さ 11.4<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7296;0.7299;0.7535;0.7538;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 2° → 大気を通る長さ 12.0<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7535;0.7538;0.7775;0.7778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="380" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">透過率 = exp(−消散係数 × 長さ)。青（消散が大）が先に消え、白 → 黄 → 橙 → 赤と変わる。</text>
</svg>

<!-- fig:sun-transmittance:end -->

## 透過率
<strong>光が距離 d を進むと、強さは指数的に減ります</strong>（Beer–Lambert の法則）。

<div class="formula">T(a → b) = exp( −∫ σt(s) ds )　（光学的厚さ τ = ∫ σt ds）</div>

```hlsl
float3 Transmittance(float3 start, float3 end, int steps) {
  float3 delta = (end - start) / steps;
  float step_length = length(delta);
  float3 optical_depth = 0;
  for (int i = 0; i < steps; ++i) {
    float3 p = start + delta * (i + 0.5);
    float h = length(p) - kPlanetRadius;
    float3 extinction = kRayleighScattering * exp(-h / kRayleighScaleHeight)
                      + kMieExtinction * exp(-h / kMieScaleHeight)
                      + kOzoneAbsorption * OzoneDensity(h);
    optical_depth += extinction * step_length;
  }
  return exp(-optical_depth);
}
```

コードの要点です。中点法で、各区間の中点で密度を取ります。色ごとに別の値を持ちます（RGB の消散係数が違うので、青が先に減ります）。球の外や内への扱いとして、地面にぶつかる向きは、光が届かない（T = 0）として扱います。

## 透過率とは、何か

光が、霧や大気の中を、距離 `d` だけ進むと、<strong>一部が、吸収・散乱で、進行方向から、失われます</strong>。<strong>そのまま、進行方向に、残る光の割合</strong>が、透過率 `T` です。

```text
T = exp( −σ × d )                       一様な媒質（霧）の場合

T = exp( −∫ σ(s) ds )                   密度が、場所で変わる媒質（大気）の場合。積分は、光の通り道に沿って
```

`σ`（消散係数、1/m）は、<strong>単位長さあたり、どれだけ、光が失われるか</strong>を表します。指数関数の形（Beer–Lambert の法則）なのは、<strong>進んだ分の、一定の割合</strong>が、失われ続けるためです。

## 一様な、媒質：1 行で、済む

霧の、密度が、一定なら、積分は、不要です。

```hlsl
float3 transmittance = exp(-g_sigma_t * distance);
```

`g_sigma_t` は、<strong>RGB の、3 成分</strong>の、消散係数です。空気中の、レイリー散乱は、<strong>青の方が、大きく</strong>、赤の方が、小さいので、遠くの景色は、青みを帯びます（[Rayleigh Scattering](../scattering/index.md)）。

## 密度が、変わる媒質：数値積分

大気の、密度は、<strong>高度とともに、指数関数的に、薄く</strong>なります。

```text
ρ(h) = exp( −h / H )         h: 地表からの高さ、H: スケール ハイト（レイリー 8 km、ミー 1.2 km）
```

光の通り道に沿った、積分は、<strong>分割して、足し合わせる</strong>ことで、近似します。

```hlsl
// 地表の中心を原点とした、座標で、位置 p の、高さ（地表からの高さ）を求める。
float HeightAt(float3 p) { return length(p) - g_planet_radius; }
```

大気は、<strong>惑星の中心を、原点</strong>にした、<strong>球</strong>として、扱います。`length(p)` が、中心からの距離で、惑星の半径を引くと、高度です。

```hlsl
// 密度（高度 h での、基準の密度に対する、割合）。レイリーと、ミーで、スケール ハイトが違う。
float DensityRayleigh(float h) { return exp(-h / 8000.0); }       // 8 km
float DensityMie(float h) { return exp(-h / 1200.0); }            // 1.2 km
```

レイリー散乱（空気の分子）の、層は、<strong>厚く</strong>（8 km）、ミー散乱（エアロゾル、細かい塵や、水滴）の層は、<strong>薄い</strong>（1.2 km、地表の近く）です。ミー散乱が、地表の近くに、集まっているので、地平線の、すぐ上だけ、白っぽく濁ります。

```hlsl
// 光の通り道（点 a から、方向 dir へ、長さ length）の、光学的な厚さ（密度の積分）を、数値で求める。
float2 OpticalDepth(float3 a, float3 dir, float length_m, int steps) {
  float step_len = length_m / steps;
  float2 sum = 0.0;                                               // x = レイリー、y = ミー
  for (int i = 0; i < steps; ++i) {
    float3 p = a + dir * ((i + 0.5) * step_len);                  // 区間の中央で、評価（中点法）
    float h = HeightAt(p);
    sum += float2(DensityRayleigh(h), DensityMie(h)) * step_len;
  }
  return sum;
}
```

ループの中で、<strong>各区間の中央</strong>の、密度を、読み、<strong>区間の長さを掛けて</strong>、足し合わせます。これが、積分の、近似です（中点法）。`steps` は、精度と、速さの、バランスで、16〜64 が、よく使われます。

```hlsl
// 透過率 = exp( −(σ_レイリー × 光学的厚さ_レイリー + σ_ミー × 光学的厚さ_ミー) )
float3 Transmittance(float3 a, float3 dir, float length_m) {
  float2 od = OpticalDepth(a, dir, length_m, 32);
  float3 tau = g_rayleigh_extinction * od.x + g_mie_extinction * od.y;       // RGB ごとの、光学的な深さ
  return exp(-tau);
}
```

<strong>消散係数</strong>（`σ`）は、<strong>基準の密度での、値</strong>で、光学的厚さ（密度の積分）と、掛け合わせます。RGB ごとに、別の `σ` を持つので、透過率も、RGB ごとに、違う値になります。

## 計算量の、問題

太陽の光は、<strong>大気の外から、各点まで</strong>、<strong>透過率</strong>を掛けて、届きます。空の、各方向について、視線に沿った、各サンプル点で、太陽方向の透過率を、求めると、二重ループになります。

```text
空の画素 × 視線のサンプル（32） × 太陽方向のサンプル（32）  =  画素あたり 約 1,000 回の、密度計算
```

画面の、全画素で、これを行うのは、<strong>重すぎます</strong>。そこで、<strong>太陽方向の透過率</strong>は、事前に、テクスチャ（LUT）に、計算しておきます。

## 透過率 LUT

<strong>透過率</strong>は、<strong>「点の高度」と「方向の、天頂角」</strong>の、2 つだけで、決まります（大気は、球対称なので）。この 2 変数の、関数を、2 次元のテクスチャに、焼いておきます（Bruneton と Neyret、2008）。Hillaire（2020）の、実装では、256×64 画素です。

```hlsl
// LUT の uv から、（高度、天頂角の cos）を、求める。
// uv.y は、高度、uv.x は、「大気の上端までの距離」を、正規化した値で、地平線の近くを、細かく取る。
void UvToTransmittanceParams(float2 uv, out float view_height, out float cos_zenith) {
  float H = sqrt(g_top_radius * g_top_radius - g_bottom_radius * g_bottom_radius);   // 地表の接線の、大気の上端までの距離
  float rho = H * uv.y;                                                              // 地平線までの距離
  view_height = sqrt(rho * rho + g_bottom_radius * g_bottom_radius);
  float d_min = g_top_radius - view_height;                                          // 真上に向かう場合の、距離
  float d_max = rho + H;                                                             // 地平線の方向に向かう場合の、距離
  float d = d_min + uv.x * (d_max - d_min);                                          // 大気の上端までの距離
  cos_zenith = (d == 0.0) ? 1.0 : (H * H - rho * rho - d * d) / (2.0 * view_height * d);
  cos_zenith = clamp(cos_zenith, -1.0, 1.0);
}
```

<strong>uv を、角度や、高度に、そのまま、割り当てる</strong>と、<strong>地平線の近く</strong>（変化が、急）の、解像度が、足りません。大気の上端までの距離で、横軸を、決めると、地平線の近くを、細かく、取れます（Hillaire の実装）。この関数は、LUT を、作るとき（各画素が、どの高度・角度を、表すか）に、使います。

```hlsl
// 逆変換: （高度、天頂角の cos）から、LUT の uv を求める。LUT を読むときに使う。
float2 TransmittanceParamsToUv(float view_height, float cos_zenith) {
  float H = sqrt(max(0.0, g_top_radius * g_top_radius - g_bottom_radius * g_bottom_radius));
  float rho = sqrt(max(0.0, view_height * view_height - g_bottom_radius * g_bottom_radius));
  float discriminant = view_height * view_height * (cos_zenith * cos_zenith - 1.0) + g_top_radius * g_top_radius;
  float d = max(0.0, -view_height * cos_zenith + sqrt(discriminant));                // 大気の上端までの距離
  float d_min = g_top_radius - view_height;
  float d_max = rho + H;
  return float2((d - d_min) / (d_max - d_min), rho / H);
}
```

読むときは、<strong>この逆変換で、uv を求め</strong>、<strong>テクスチャを 1 回引く</strong>だけです。透過率の、積分が、1 回の、テクスチャ読み込みに、化けます。

```hlsl
// 太陽方向の、透過率を、LUT から引く（一瞬で済む）。
float3 SunTransmittance(float3 position, float3 sun_dir) {
  float h = length(position);
  float cos_zenith = dot(position / h, sun_dir);
  return g_transmittance_lut.SampleLevel(g_linear_clamp, TransmittanceParamsToUv(h, cos_zenith), 0).rgb;
}
```

`position / h` は、<strong>位置での、真上の向き</strong>（地表の、法線）で、`sun_dir` との内積が、<strong>太陽の天頂角の cos</strong> です。

## 地面に、遮られる光

光の、通り道が、<strong>地面</strong>に当たる場合（太陽が、地平線の、下にある）、<strong>その方向の、透過率は、0</strong> と、みなします。

```hlsl
// 惑星（地面）に、遮られるか。
float2 RaySphere(float3 origin, float3 dir, float radius);      // 交点までの、距離（2 つ。当たらなければ、負）

bool HitsGround(float3 position, float3 dir) {
  float2 t = RaySphere(position, dir, g_bottom_radius);
  return t.x > 0.0 || t.y > 0.0;                                   // 前方で、地面と交わる
}
```

太陽が、地平線の、<strong>少し下</strong>に、沈んだ後も、<strong>空が、しばらく、明るい</strong>のは、散乱した光が、回り込んでくるためです（[Day-Night Cycle](../sky-models/day-night.md)）。透過率だけでは、直接の光が、消える瞬間は、出せますが、残照は、出ません。

## よくあるミス

??? failure "日没の太陽が、白いまま"
    <strong>透過率を RGB ごと</strong>に<strong>計算</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 距離と係数で、指数で減衰する

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)（4 つの LUT を使う方式。公開デモの実装がある）
- Bruneton, Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum (Eurographics Symposium on Rendering 2008)
- Bruneton, "A Qualitative and Quantitative Evaluation of 8 Clear Sky Models", IEEE Transactions on Visualization and Computer Graphics, Vol. 23, No. 12, 2017（参照実装 `ebruneton/precomputed_atmospheric_scattering` が公開されている）
- Nishita, Sirai, Tadamura, Nakamae, "Display of the Earth Taking into Account Atmospheric Scattering", SIGGRAPH 1993（大気散乱の、CG への導入）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大気散乱、参加媒質の章）

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Atmosphere Model](atmosphere-model.md)
- [Single-Scattering Integral](single-scattering.md)
