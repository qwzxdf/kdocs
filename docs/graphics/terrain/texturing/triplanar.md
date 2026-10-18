---
title: Triplanar Mapping
tags:
  - 描画
---

# Triplanar Mapping

**急斜面では、上から貼ったテクスチャが、縦に引き伸ばされます**。**X・Y・Z の 3 方向から貼って、法線に応じて混ぜる**ことで、**伸びを防げます**。このページでは、**トライプラナー マッピング**を説明します。

!!! tip "ポイント"
    - **3 方向（XY・YZ・ZX）から、テクスチャを貼る**。
    - **法線の向きで、3 つを混ぜる**。
    - **テクスチャの読み込みが、3 倍になる**。
    - **崖・岩に使う**。

<!-- fig:triplanar-weights:begin -->

<svg class="fig illust motion" data-fig="triplanar-weights" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-triplanar-weights" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">トライプラナー:斜面の向きで、3 方向のテクスチャを混ぜる</text>
<rect x="50" y="80" width="330" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="132.5" y1="80" x2="132.5" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="135.0" x2="380" y2="135.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="215.0" y1="80" x2="215.0" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="190.0" x2="380" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="297.5" y1="80" x2="297.5" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="245.0" x2="380" y2="245.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="380" y="320" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">斜面の傾き（0° = 平ら、90° = 垂直な崖）</text>
<text x="50" y="72" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">重み</text>
<path d="M50.0,80.0 L55.5,80.0 L61.0,80.0 L66.5,80.01 L72.0,80.03 L77.5,80.07 L83.0,80.14 L88.5,80.26 L94.0,80.45 L99.5,80.73 L105.0,81.13 L110.5,81.68 L116.0,82.43 L121.5,83.41 L127.0,84.68 L132.5,86.29 L138.0,88.32 L143.5,90.83 L149.0,93.89 L154.5,97.59 L160.0,102.0 L165.5,107.19 L171.0,113.22 L176.5,120.13 L182.0,127.94 L187.5,136.63 L193.0,146.15 L198.5,156.41 L204.0,167.25 L209.5,178.52 L215.0,190.0 L220.5,201.48 L226.0,212.75 L231.5,223.59 L237.0,233.85 L242.5,243.37 L248.0,252.06 L253.5,259.87 L259.0,266.78 L264.5,272.81 L270.0,278.0 L275.5,282.41 L281.0,286.11 L286.5,289.17 L292.0,291.68 L297.5,293.71 L303.0,295.32 L308.5,296.59 L314.0,297.57 L319.5,298.32 L325.0,298.87 L330.5,299.27 L336.0,299.55 L341.5,299.74 L347.0,299.86 L352.5,299.93 L358.0,299.97 L363.5,299.99 L369.0,300.0 L374.5,300.0 L380.0,300.0" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<path d="M50.0,300.0 L55.5,300.0 L61.0,300.0 L66.5,299.99 L72.0,299.97 L77.5,299.93 L83.0,299.86 L88.5,299.74 L94.0,299.55 L99.5,299.27 L105.0,298.87 L110.5,298.32 L116.0,297.57 L121.5,296.59 L127.0,295.32 L132.5,293.71 L138.0,291.68 L143.5,289.17 L149.0,286.11 L154.5,282.41 L160.0,278.0 L165.5,272.81 L171.0,266.78 L176.5,259.87 L182.0,252.06 L187.5,243.37 L193.0,233.85 L198.5,223.59 L204.0,212.75 L209.5,201.48 L215.0,190.0 L220.5,178.52 L226.0,167.25 L231.5,156.41 L237.0,146.15 L242.5,136.63 L248.0,127.94 L253.5,120.13 L259.0,113.22 L264.5,107.19 L270.0,102.0 L275.5,97.59 L281.0,93.89 L286.5,90.83 L292.0,88.32 L297.5,86.29 L303.0,84.68 L308.5,83.41 L314.0,82.43 L319.5,81.68 L325.0,81.13 L330.5,80.73 L336.0,80.45 L341.5,80.26 L347.0,80.14 L352.5,80.07 L358.0,80.03 L363.5,80.01 L369.0,80.0 L374.5,80.0 L380.0,80.0" fill="none" stroke="#e5484d" stroke-width="4" opacity="1"/>
<text x="79.33" y="102.0" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">上から（XZ）</text>
<text x="277.33" y="102.0" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">横から（XY）</text>
<circle cx="50.0" cy="80.0" r="6" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0872;0.1104;0.1336;0.1568;0.1800;0.2032;0.2264;0.2496;0.2728;0.2960;0.3192;0.3424;0.3656;0.3888;0.4120;0.4352;0.4584;0.4816;0.5048;0.5280;0.5512;0.5744;0.5976;0.6208;0.6440;0.6672;0.6904;0.7136;0.7368;0.7600;1.0000" values="50;50;60.76;71.51;82.27;93.02;103.78;114.53;125.29;136.04;146.8;157.56;168.31;179.07;189.82;200.58;211.33;222.09;232.84;243.6;254.36;265.11;275.87;286.62;297.38;308.13;318.89;329.64;340.4;351.16;361.91;372.67;372.67"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0872;0.1104;0.1336;0.1568;0.1800;0.2032;0.2264;0.2496;0.2728;0.2960;0.3192;0.3424;0.3656;0.3888;0.4120;0.4352;0.4584;0.4816;0.5048;0.5280;0.5512;0.5744;0.5976;0.6208;0.6440;0.6672;0.6904;0.7136;0.7368;0.7600;1.0000" values="80;80;80;80.02;80.13;80.41;81.03;82.21;84.25;87.55;92.59;99.95;110.16;123.67;140.56;160.44;182.33;204.77;226.16;245.17;261;273.43;282.68;289.23;293.67;296.52;298.25;299.22;299.71;299.92;299.99;300;300"/></circle>
<circle cx="50.0" cy="300.0" r="6" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0872;0.1104;0.1336;0.1568;0.1800;0.2032;0.2264;0.2496;0.2728;0.2960;0.3192;0.3424;0.3656;0.3888;0.4120;0.4352;0.4584;0.4816;0.5048;0.5280;0.5512;0.5744;0.5976;0.6208;0.6440;0.6672;0.6904;0.7136;0.7368;0.7600;1.0000" values="50;50;60.76;71.51;82.27;93.02;103.78;114.53;125.29;136.04;146.8;157.56;168.31;179.07;189.82;200.58;211.33;222.09;232.84;243.6;254.36;265.11;275.87;286.62;297.38;308.13;318.89;329.64;340.4;351.16;361.91;372.67;372.67"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0872;0.1104;0.1336;0.1568;0.1800;0.2032;0.2264;0.2496;0.2728;0.2960;0.3192;0.3424;0.3656;0.3888;0.4120;0.4352;0.4584;0.4816;0.5048;0.5280;0.5512;0.5744;0.5976;0.6208;0.6440;0.6672;0.6904;0.7136;0.7368;0.7600;1.0000" values="300;300;300;299.98;299.87;299.59;298.97;297.79;295.75;292.45;287.41;280.05;269.84;256.33;239.44;219.56;197.67;175.23;153.84;134.83;119;106.57;97.32;90.77;86.33;83.48;81.75;80.78;80.29;80.08;80.01;80;80"/></circle>
<line x1="400" y1="330" x2="700" y2="330" stroke="#a8a29e" stroke-width="2"/>
<line x1="480" y1="330" x2="680" y2="330" stroke="#b8794b" stroke-width="10"><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.0872;0.1104;0.1336;0.1568;0.1800;0.2032;0.2264;0.2496;0.2728;0.2960;0.3192;0.3424;0.3656;0.3888;0.4120;0.4352;0.4584;0.4816;0.5048;0.5280;0.5512;0.5744;0.5976;0.6208;0.6440;0.6672;0.6904;0.7136;0.7368;0.7600;1.0000" values="680;680;640;639.79;639.16;638.12;636.66;634.79;632.51;629.83;626.77;623.31;619.49;615.29;610.74;605.85;600.63;595.09;589.26;583.13;576.74;570.09;563.2;556.1;548.8;541.32;533.67;525.89;517.98;509.98;501.9;493.76;485.58;485.58"/><animate attributeName="y2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0872;0.1104;0.1336;0.1568;0.1800;0.2032;0.2264;0.2496;0.2728;0.2960;0.3192;0.3424;0.3656;0.3888;0.4120;0.4352;0.4584;0.4816;0.5048;0.5280;0.5512;0.5744;0.5976;0.6208;0.6440;0.6672;0.6904;0.7136;0.7368;0.7600;1.0000" values="330;330;320.79;311.6;302.46;293.4;284.42;275.57;266.86;258.32;249.97;241.82;233.91;226.24;218.85;211.75;204.96;198.5;192.38;186.62;181.24;176.25;171.66;167.49;163.74;160.43;157.56;155.15;153.19;151.69;150.67;150.11;150.11"/></line>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 0° → 上から 1.00、横から 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.0869;0.0872;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 3° → 上から 1.00、横から 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0869;0.0872;0.1101;0.1104;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 6° → 上から 1.00、横から 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1101;0.1104;0.1333;0.1336;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 9° → 上から 1.00、横から 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1333;0.1336;0.1565;0.1568;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 12° → 上から 1.00、横から 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1565;0.1568;0.1797;0.1800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 15° → 上から 0.99、横から 0.01<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1797;0.1800;0.2029;0.2032;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 18° → 上から 0.99、横から 0.01<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2029;0.2032;0.2261;0.2264;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 21° → 上から 0.98、横から 0.02<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2261;0.2264;0.2493;0.2496;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 24° → 上から 0.96、横から 0.04<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2493;0.2496;0.2725;0.2728;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 27° → 上から 0.93、横から 0.07<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2725;0.2728;0.2957;0.2960;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 30° → 上から 0.89、横から 0.11<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2957;0.2960;0.3189;0.3192;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 33° → 上から 0.84、横から 0.16<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3189;0.3192;0.3421;0.3424;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 36° → 上から 0.77、横から 0.23<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3421;0.3424;0.3653;0.3656;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 39° → 上から 0.69、横から 0.31<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3653;0.3656;0.3885;0.3888;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 42° → 上から 0.59、横から 0.41<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3885;0.3888;0.4117;0.4120;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 46° → 上から 0.48、横から 0.52<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4117;0.4120;0.4349;0.4352;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 49° → 上から 0.38、横から 0.62<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4349;0.4352;0.4581;0.4584;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 52° → 上から 0.28、横から 0.72<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4581;0.4584;0.4813;0.4816;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 55° → 上から 0.20、横から 0.80<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4813;0.4816;0.5045;0.5048;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 58° → 上から 0.14、横から 0.86<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5045;0.5048;0.5277;0.5280;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 61° → 上から 0.09、横から 0.91<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;0.5509;0.5512;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 64° → 上から 0.06、横から 0.94<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5509;0.5512;0.5741;0.5744;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 67° → 上から 0.03、横から 0.97<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5741;0.5744;0.5973;0.5976;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 70° → 上から 0.02、横から 0.98<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5973;0.5976;0.6205;0.6208;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 73° → 上から 0.01、横から 0.99<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6205;0.6208;0.6437;0.6440;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 76° → 上から 0.00、横から 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6437;0.6440;0.6669;0.6672;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 79° → 上から 0.00、横から 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6669;0.6672;0.6901;0.6904;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 82° → 上から 0.00、横から 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6901;0.6904;0.7133;0.7136;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 85° → 上から 0.00、横から 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7133;0.7136;0.7365;0.7368;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="346" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">傾き 88° → 上から 0.00、横から 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7365;0.7368;0.7597;0.7600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="380" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">平らな所は、上から貼ったテクスチャ。崖に近づくと、横から貼ったテクスチャに切り替わる → 縦に伸びない。</text>
</svg>

<!-- fig:triplanar-weights:end -->

## トライプラナー
**XZ 平面に投影する UV は、急斜面や崖でテクスチャが縦に引き伸ばされます**。**X・Y・Z の 3 方向から投影した 3 枚を、法線の向きで混ぜる**のが**トライプラナー マッピング**です。

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="トライプラナー">
<text x="20" y="24" class="fig-title">トライプラナー：面の向きに応じて、3 方向の投影を混ぜる</text>
<polyline fill="#a0763c" fill-opacity="0.3" stroke="currentColor" stroke-opacity="0.7" stroke-width="2" points="60,190 220,190 300,70 440,70 520,190 720,190"/>
<g stroke="#4c8bf5" stroke-width="2"><line x1="120" y1="40" x2="120" y2="190"/><line x1="160" y1="40" x2="160" y2="190"/><line x1="200" y1="40" x2="200" y2="190"/></g>
<text x="60" y="34" style="font-size:12px;fill:#4c8bf5">上から投影：平らな所は良い</text>
<g stroke="#e5484d" stroke-width="2"><line x1="260" y1="110" x2="320" y2="110" /><line x1="262" y1="140" x2="320" y2="140"/></g>
<text x="330" y="150" style="font-size:12px;fill:#e5484d">崖は上から投影すると引き伸ばされる</text>
<g stroke="#2ea043" stroke-width="2"><line x1="420" y1="95" x2="470" y2="95" stroke-dasharray="3 3"/><line x1="440" y1="130" x2="490" y2="130" stroke-dasharray="3 3"/></g>
<text x="450" y="64" style="font-size:12px;fill:#2ea043">横から投影すれば良い</text>
</svg>

```hlsl
float3 TriplanarWeights(float3 normal, float sharpness) {
  float3 w = pow(abs(normal), sharpness);
  return w / (w.x + w.y + w.z);
}

float3 Triplanar(Texture2D tex, float3 world_position, float3 normal, float scale) {
  float3 w = TriplanarWeights(normal, 4.0);
  float3 x = tex.Sample(linear_wrap, world_position.zy * scale).rgb;
  float3 y = tex.Sample(linear_wrap, world_position.xz * scale).rgb;
  float3 z = tex.Sample(linear_wrap, world_position.xy * scale).rgb;
  return x * w.x + y * w.y + z * w.z;
}
```

| 点 | 説明 |
| --- | --- |
| **サンプル数が 3 倍** | **3 方向から 1 回ずつ読む**ので**重い**。**急斜面（岩）の層だけに使う** |
| **`sharpness`** | **大きいほど、方向の切り替えが鋭い** |
| **法線マップも要注意** | **接線空間でなくワールド空間の法線に直す**（**投影ごとに軸を入れ替えて、法線を戻す**） |
| **傾きで使い分け** | **平らな所は 1 方向（安い）、急な所だけ 3 方向** |

## よくあるミス

??? failure "崖のテクスチャが、縦に伸びている"
    **トライプラナー**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **3 方向から貼って、法線で混ぜる**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain Texturing](index.md)
- [Hiding Tiling](tiling.md)
