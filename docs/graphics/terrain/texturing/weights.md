---
title: Splat Weights
tags:
  - 描画
---

# Splat Weights

**スプラットの重みは、どのテクスチャを、どれだけ使うかを決める値**です。**手でペイント**、**または高さ・傾きから自動で決める**ことが**多い**です。このページでは、**重みの決め方**を説明します。

!!! tip "ポイント"
    - **ペイント：スプラット マップ（RGBA）に塗る**。
    - **自動：高さ・傾きで決める**（雪は高所、岩は急斜面）。
    - **重みの合計を 1 にする**。
    - **4 枚ごとに 1 枚のスプラット マップ**。

<!-- fig:splat-weights:begin -->

<svg class="fig illust motion" data-fig="splat-weights" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-splat-weights" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">スプラットの重み:高さと傾きで、草・岩・雪を混ぜる</text>
<rect x="50" y="80" width="340" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="135.0" y1="80" x2="135.0" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="135.0" x2="390" y2="135.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="220.0" y1="80" x2="220.0" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="190.0" x2="390" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="305.0" y1="80" x2="305.0" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="245.0" x2="390" y2="245.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="390" y="320" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">高さ（0 = 低い、1 = 高い）</text>
<text x="50" y="72" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">重み</text>
<path d="M50.0,80.0 L55.67,87.98 L61.33,95.9 L67.0,103.78 L72.67,111.6 L78.33,119.37 L84.0,127.08 L89.67,134.74 L95.33,142.34 L101.0,149.87 L106.67,157.35 L112.33,164.76 L118.0,172.1 L123.67,179.37 L129.33,186.57 L135.0,193.7 L140.67,200.75 L146.33,207.71 L152.0,214.59 L157.67,221.38 L163.33,228.07 L169.0,234.65 L174.67,241.13 L180.33,247.49 L186.0,253.73 L191.67,259.83 L197.33,265.78 L203.0,271.56 L208.67,277.15 L214.33,282.51 L220.0,287.62 L225.67,292.39 L231.33,296.69 L237.0,300.0 L242.67,300.0 L248.33,300.0 L254.0,300.0 L259.67,300.0 L265.33,300.0 L271.0,300.0 L276.67,300.0 L282.33,300.0 L288.0,300.0 L293.67,300.0 L299.33,300.0 L305.0,300.0 L310.67,300.0 L316.33,300.0 L322.0,300.0 L327.67,300.0 L333.33,300.0 L339.0,300.0 L344.67,300.0 L350.33,300.0 L356.0,300.0 L361.67,300.0 L367.33,300.0 L373.0,300.0 L378.67,300.0 L384.33,300.0 L390.0,300.0" fill="none" stroke="#2ea043" stroke-width="4" opacity="1"/>
<path d="M50.0,300.0 L55.67,292.02 L61.33,284.1 L67.0,276.22 L72.67,268.4 L78.33,260.63 L84.0,252.92 L89.67,245.26 L95.33,237.66 L101.0,230.13 L106.67,222.65 L112.33,215.24 L118.0,207.9 L123.67,200.63 L129.33,193.43 L135.0,186.3 L140.67,179.25 L146.33,172.29 L152.0,165.41 L157.67,158.62 L163.33,151.93 L169.0,145.35 L174.67,138.87 L180.33,132.51 L186.0,126.27 L191.67,120.17 L197.33,114.22 L203.0,108.44 L208.67,102.85 L214.33,97.49 L220.0,92.38 L225.67,87.61 L231.33,83.31 L237.0,80.0 L242.67,84.21 L248.33,89.68 L254.0,95.75 L259.67,102.25 L265.33,109.08 L271.0,116.19 L276.67,123.54 L282.33,131.11 L288.0,138.87 L293.67,146.8 L299.33,154.9 L305.0,163.14 L310.67,171.52 L316.33,180.03 L322.0,188.67 L327.67,197.42 L333.33,206.28 L339.0,215.24 L344.67,224.31 L350.33,233.47 L356.0,242.72 L361.67,252.07 L367.33,261.49 L373.0,271.0 L378.67,280.59 L384.33,290.26 L390.0,300.0" fill="none" stroke="#78716c" stroke-width="4" opacity="1"/>
<path d="M50.0,300.0 L55.67,300.0 L61.33,300.0 L67.0,300.0 L72.67,300.0 L78.33,300.0 L84.0,300.0 L89.67,300.0 L95.33,300.0 L101.0,300.0 L106.67,300.0 L112.33,300.0 L118.0,300.0 L123.67,300.0 L129.33,300.0 L135.0,300.0 L140.67,300.0 L146.33,300.0 L152.0,300.0 L157.67,300.0 L163.33,300.0 L169.0,300.0 L174.67,300.0 L180.33,300.0 L186.0,300.0 L191.67,300.0 L197.33,300.0 L203.0,300.0 L208.67,300.0 L214.33,300.0 L220.0,300.0 L225.67,300.0 L231.33,300.0 L237.0,300.0 L242.67,295.79 L248.33,290.32 L254.0,284.25 L259.67,277.75 L265.33,270.92 L271.0,263.81 L276.67,256.46 L282.33,248.89 L288.0,241.13 L293.67,233.2 L299.33,225.1 L305.0,216.86 L310.67,208.48 L316.33,199.97 L322.0,191.33 L327.67,182.58 L333.33,173.72 L339.0,164.76 L344.67,155.69 L350.33,146.53 L356.0,137.28 L361.67,127.93 L367.33,118.51 L373.0,109.0 L378.67,99.41 L384.33,89.74 L390.0,80.0" fill="none" stroke="#64748b" stroke-width="4" opacity="1"/>
<text x="77.2" y="102.0" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">草</text>
<text x="220.0" y="245.0" text-anchor="start" style="font-size:13px;font-weight:700;fill:#78716c">岩</text>
<text x="356.0" y="102.0" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">雪</text>
<line x1="50.0" y1="80" x2="50.0" y2="300" stroke="#e5aa28" stroke-width="2.5"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0872;0.1104;0.1336;0.1568;0.1800;0.2032;0.2264;0.2496;0.2728;0.2960;0.3192;0.3424;0.3656;0.3888;0.4120;0.4352;0.4584;0.4816;0.5048;0.5280;0.5512;0.5744;0.5976;0.6208;0.6440;0.6672;0.6904;0.7136;0.7368;0.7600;1.0000" values="50;50;61.33;72.67;84;95.33;106.67;118;129.33;140.67;152;163.33;174.67;186;197.33;208.67;220;231.33;242.67;254;265.33;276.67;288;299.33;310.67;322;333.33;344.67;356;367.33;378.67;390;390"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0872;0.1104;0.1336;0.1568;0.1800;0.2032;0.2264;0.2496;0.2728;0.2960;0.3192;0.3424;0.3656;0.3888;0.4120;0.4352;0.4584;0.4816;0.5048;0.5280;0.5512;0.5744;0.5976;0.6208;0.6440;0.6672;0.6904;0.7136;0.7368;0.7600;1.0000" values="50;50;61.33;72.67;84;95.33;106.67;118;129.33;140.67;152;163.33;174.67;186;197.33;208.67;220;231.33;242.67;254;265.33;276.67;288;299.33;310.67;322;333.33;344.67;356;367.33;378.67;390;390"/></line>
<polygon points="440,330 510,270 590,190 660,130 730,190 770,330" fill="#d6d3d1" stroke="#78716c" stroke-width="2"/>
<rect x="440" y="350" width="120" height="34" fill="#2ea043" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0872;0.1104;0.1336;0.1568;0.1800;0.2032;0.2264;0.2496;0.2728;0.2960;0.3192;0.3424;0.3656;0.3888;0.4120;0.4352;0.4584;0.4816;0.5048;0.5280;0.5512;0.5744;0.5976;0.6208;0.6440;0.6672;0.6904;0.7136;0.7368;0.7600;1.0000" values="#2ea043;#2ea043;#339d46;#399949;#3e964c;#43934f;#488f51;#4d8c54;#528957;#57865a;#5b835c;#60805f;#647e61;#687b63;#6c7866;#707668;#74746a;#77726b;#7a746f;#817a76;#88827f;#908b88;#989492;#a19e9c;#aaa8a7;#b4b2b2;#bdbdbd;#c7c8c8;#d1d3d4;#dcdee0;#e6e9ed;#f1f5f9;#f1f5f9"/></rect>
<text x="440" y="342" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">この高さの地面の色</text>
<circle cx="460" cy="310" r="7" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.0872;0.1104;0.1336;0.1568;0.1800;0.2032;0.2264;0.2496;0.2728;0.2960;0.3192;0.3424;0.3656;0.3888;0.4120;0.4352;0.4584;0.4816;0.5048;0.5280;0.5512;0.5744;0.5976;0.6208;0.6440;0.6672;0.6904;0.7136;0.7368;0.7600;1.0000" values="460;460;440;447.33;454.67;462;469.33;476.67;484;491.33;498.67;506;513.33;520.67;528;535.33;542.67;550;557.33;564.67;572;579.33;586.67;594;601.33;608.67;616;623.33;630.67;638;645.33;652.67;660;660"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.0872;0.1104;0.1336;0.1568;0.1800;0.2032;0.2264;0.2496;0.2728;0.2960;0.3192;0.3424;0.3656;0.3888;0.4120;0.4352;0.4584;0.4816;0.5048;0.5280;0.5512;0.5744;0.5976;0.6208;0.6440;0.6672;0.6904;0.7136;0.7368;0.7600;1.0000" values="310;310;330;323.33;316.67;310;303.33;296.67;290;283.33;276.67;270;263.33;256.67;250;243.33;236.67;230;223.33;216.67;210;203.33;196.67;190;183.33;176.67;170;163.33;156.67;150;143.33;136.67;130;130"/></circle>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.00:草 1.00  岩 0.00  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.0869;0.0872;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.03:草 0.93  岩 0.07  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0869;0.0872;0.1101;0.1104;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.07:草 0.85  岩 0.15  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1101;0.1104;0.1333;0.1336;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.10:草 0.78  岩 0.22  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1333;0.1336;0.1565;0.1568;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.14:草 0.71  岩 0.29  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1565;0.1568;0.1797;0.1800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.17:草 0.64  岩 0.36  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1797;0.1800;0.2029;0.2032;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.21:草 0.57  岩 0.43  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2029;0.2032;0.2261;0.2264;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.24:草 0.50  岩 0.50  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2261;0.2264;0.2493;0.2496;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.28:草 0.43  岩 0.57  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2493;0.2496;0.2725;0.2728;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.31:草 0.37  岩 0.63  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2725;0.2728;0.2957;0.2960;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.34:草 0.31  岩 0.69  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2957;0.2960;0.3189;0.3192;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.38:草 0.25  岩 0.75  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3189;0.3192;0.3421;0.3424;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.41:草 0.19  岩 0.81  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3421;0.3424;0.3653;0.3656;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.45:草 0.13  岩 0.87  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3653;0.3656;0.3885;0.3888;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.48:草 0.08  岩 0.92  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3885;0.3888;0.4117;0.4120;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.52:草 0.03  岩 0.97  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4117;0.4120;0.4349;0.4352;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.55:草 0.00  岩 1.00  雪 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4349;0.4352;0.4581;0.4584;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.59:草 0.00  岩 0.95  雪 0.05<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4581;0.4584;0.4813;0.4816;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.62:草 0.00  岩 0.89  雪 0.11<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4813;0.4816;0.5045;0.5048;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.66:草 0.00  岩 0.83  雪 0.17<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5045;0.5048;0.5277;0.5280;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.69:草 0.00  岩 0.75  雪 0.25<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;0.5509;0.5512;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.72:草 0.00  岩 0.68  雪 0.32<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5509;0.5512;0.5741;0.5744;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.76:草 0.00  岩 0.60  雪 0.40<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5741;0.5744;0.5973;0.5976;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.79:草 0.00  岩 0.52  雪 0.48<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5973;0.5976;0.6205;0.6208;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.83:草 0.00  岩 0.44  雪 0.56<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6205;0.6208;0.6437;0.6440;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.86:草 0.00  岩 0.36  雪 0.64<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6437;0.6440;0.6669;0.6672;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.90:草 0.00  岩 0.27  雪 0.73<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6669;0.6672;0.6901;0.6904;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.93:草 0.00  岩 0.18  雪 0.82<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6901;0.6904;0.7133;0.7136;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 0.97:草 0.00  岩 0.09  雪 0.91<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7133;0.7136;0.7365;0.7368;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">高さ 1.00:草 0.00  岩 0.00  雪 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7365;0.7368;0.7597;0.7600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="380" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">傾き（急斜面は岩）なども使う。合計は 1</text>
</svg>

<!-- fig:splat-weights:end -->

## 重みを決める
| 方法 | 内容 |
| --- | --- |
| **手描き** | **地形エディタでブラシで塗る** |
| **ルールで自動** | **高さ・傾きから決める**（下の表） |
| **侵食の結果から** | **堆積した所は土・砂、削られた所は岩**（[Terrain Generation](../generation/index.md)） |

| 条件 | 地面 |
| --- | --- |
| **傾きが緩やか・低い** | **草** |
| **傾きが急** | **岩** |
| **高い所** | **雪** |
| **水の近く** | **砂・泥** |

```hlsl
float slope = 1.0 - saturate(normal.y);
float rock = smoothstep(0.35, 0.55, slope);
float snow = smoothstep(snow_line, snow_line + 20.0, world_position.y) * (1.0 - rock);
float grass = (1.0 - rock) * (1.0 - snow);
```

**ルールで基礎を作り、手描きの重みを足して調整する**のが**実用的**です。

## よくあるミス

??? failure "重みの合計が 1 でなく、地形が暗い・明るい"
    **重みを正規化**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **ペイントか自動で決め、合計 1 にする**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain Texturing](index.md)
- [Height-Based Blending](height-blend.md)
