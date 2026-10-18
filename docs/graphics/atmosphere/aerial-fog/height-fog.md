---
title: Height Fog
tags:
  - 描画
---

# Height Fog

**霧は、低い所にたまります**。**フォグの密度を、高さで指数的に減らす**と、**谷にたまる霧**が**表現**できます。このページでは、**高さフォグ**を説明します。

!!! tip "ポイント"
    - **密度 ＝ 基準密度 × exp(−高さ × 係数)**。
    - **視線に沿って積分すると、解析的に求まる**。
    - **低い所ほど、濃い霧**。
    - **朝霧・谷の霧の表現**に向く。

<!-- fig:height-fog-ray:begin -->

<svg class="fig illust motion" data-fig="height-fog-ray" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-height-fog-ray" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">高さ霧: 低い所ほど濃い霧を、視線に沿って積分する(式で一発 vs 少しずつ進める)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">霧の濃さ = σ0 · exp(−b · 高さ)。カメラは高さ 4 から、斜め下の地面を見る。進める歩数で、式の値に近づく</text>
<rect x="30" y="96" width="900" height="250" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 断面(青い濃さ = 霧の濃さ)</text>
<rect x="60.0" y="326.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.63"/>
<rect x="60.0" y="322.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.61"/>
<rect x="60.0" y="318.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.59"/>
<rect x="60.0" y="314.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.58"/>
<rect x="60.0" y="310.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.56"/>
<rect x="60.0" y="306.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.54"/>
<rect x="60.0" y="302.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.53"/>
<rect x="60.0" y="298.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.51"/>
<rect x="60.0" y="294.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.5"/>
<rect x="60.0" y="290.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.48"/>
<rect x="60.0" y="286.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.47"/>
<rect x="60.0" y="282.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.45"/>
<rect x="60.0" y="278.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.44"/>
<rect x="60.0" y="274.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.43"/>
<rect x="60.0" y="270.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.42"/>
<rect x="60.0" y="266.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.41"/>
<rect x="60.0" y="262.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.39"/>
<rect x="60.0" y="258.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.38"/>
<rect x="60.0" y="254.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.37"/>
<rect x="60.0" y="250.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.36"/>
<rect x="60.0" y="246.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.35"/>
<rect x="60.0" y="242.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.34"/>
<rect x="60.0" y="238.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.33"/>
<rect x="60.0" y="234.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.33"/>
<rect x="60.0" y="230.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.32"/>
<rect x="60.0" y="226.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.31"/>
<rect x="60.0" y="222.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.3"/>
<rect x="60.0" y="218.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.29"/>
<rect x="60.0" y="214.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.29"/>
<rect x="60.0" y="210.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.28"/>
<rect x="60.0" y="206.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.27"/>
<rect x="60.0" y="202.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.27"/>
<rect x="60.0" y="198.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.26"/>
<rect x="60.0" y="194.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.25"/>
<rect x="60.0" y="190.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.25"/>
<rect x="60.0" y="186.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.24"/>
<rect x="60.0" y="182.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.24"/>
<rect x="60.0" y="178.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.23"/>
<rect x="60.0" y="174.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.23"/>
<rect x="60.0" y="170.0" width="800.0" height="4.3" fill="#60a5fa" fill-opacity="0.22"/>
<line x1="60.0" y1="330.0" x2="860.0" y2="330.0" stroke="#475569" stroke-width="4"/>
<circle cx="60.0" cy="170.0" r="8" fill="#1f2937"/>
<text x="72.0" y="164.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">カメラ(高さ 4)</text>
<line x1="60.0" y1="170.0" x2="860.0" y2="330.0" stroke="#fca5a5" stroke-width="2" stroke-dasharray="6 5"/>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2169;0.2170;1.0000" values="1;1;0;0"/><circle cx="260.0" cy="210.0" r="6" fill="#e5484d"/>
<circle cx="660.0" cy="290.0" r="6" fill="#e5484d"/>
<text x="60" y="128" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d">歩数 2</text>
<text x="60" y="152" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">霧の濃さの積分(光学的厚さ)= 1.060</text>
<text x="60" y="174" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">式の値 1.082 に対するずれ 2.0%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2169;0.2170;0.3700;0.3702;1.0000" values="0;0;1;1;0;0"/><circle cx="160.0" cy="190.0" r="6" fill="#e5aa28"/>
<circle cx="360.0" cy="230.0" r="6" fill="#e5aa28"/>
<circle cx="560.0" cy="270.0" r="6" fill="#e5aa28"/>
<circle cx="760.0" cy="310.0" r="6" fill="#e5aa28"/>
<text x="60" y="128" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5aa28">歩数 4</text>
<text x="60" y="152" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">霧の濃さの積分(光学的厚さ)= 1.076</text>
<text x="60" y="174" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">式の値 1.082 に対するずれ 0.5%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3700;0.3702;0.5232;0.5234;1.0000" values="0;0;1;1;0;0"/><circle cx="110.0" cy="180.0" r="6" fill="#2ea043"/>
<circle cx="210.0" cy="200.0" r="6" fill="#2ea043"/>
<circle cx="310.0" cy="220.0" r="6" fill="#2ea043"/>
<circle cx="410.0" cy="240.0" r="6" fill="#2ea043"/>
<circle cx="510.0" cy="260.0" r="6" fill="#2ea043"/>
<circle cx="610.0" cy="280.0" r="6" fill="#2ea043"/>
<circle cx="710.0" cy="300.0" r="6" fill="#2ea043"/>
<circle cx="810.0" cy="320.0" r="6" fill="#2ea043"/>
<text x="60" y="128" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2ea043">歩数 8</text>
<text x="60" y="152" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">霧の濃さの積分(光学的厚さ)= 1.080</text>
<text x="60" y="174" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">式の値 1.082 に対するずれ 0.1%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5232;0.5234;0.6764;0.6766;1.0000" values="0;0;1;1;0;0"/><circle cx="85.0" cy="175.0" r="5.5" fill="#2563eb"/>
<circle cx="135.0" cy="185.0" r="5.5" fill="#2563eb"/>
<circle cx="185.0" cy="195.0" r="5.5" fill="#2563eb"/>
<circle cx="235.0" cy="205.0" r="5.5" fill="#2563eb"/>
<circle cx="285.0" cy="215.0" r="5.5" fill="#2563eb"/>
<circle cx="335.0" cy="225.0" r="5.5" fill="#2563eb"/>
<circle cx="385.0" cy="235.0" r="5.5" fill="#2563eb"/>
<circle cx="435.0" cy="245.0" r="5.5" fill="#2563eb"/>
<circle cx="485.0" cy="255.0" r="5.5" fill="#2563eb"/>
<circle cx="535.0" cy="265.0" r="5.5" fill="#2563eb"/>
<circle cx="585.0" cy="275.0" r="5.5" fill="#2563eb"/>
<circle cx="635.0" cy="285.0" r="5.5" fill="#2563eb"/>
<circle cx="685.0" cy="295.0" r="5.5" fill="#2563eb"/>
<circle cx="735.0" cy="305.0" r="5.5" fill="#2563eb"/>
<circle cx="785.0" cy="315.0" r="5.5" fill="#2563eb"/>
<circle cx="835.0" cy="325.0" r="5.5" fill="#2563eb"/>
<text x="60" y="128" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb">歩数 16</text>
<text x="60" y="152" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">霧の濃さの積分(光学的厚さ)= 1.081</text>
<text x="60" y="174" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">式の値 1.082 に対するずれ 0.0%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6764;0.6766;1.0000" values="0;0;1;1"/><circle cx="66.25" cy="171.25" r="3.625" fill="#7c3aed"/>
<circle cx="78.75" cy="173.75" r="3.625" fill="#7c3aed"/>
<circle cx="91.25" cy="176.25" r="3.625" fill="#7c3aed"/>
<circle cx="103.75" cy="178.75" r="3.625" fill="#7c3aed"/>
<circle cx="116.25" cy="181.25" r="3.625" fill="#7c3aed"/>
<circle cx="128.75" cy="183.75" r="3.625" fill="#7c3aed"/>
<circle cx="141.25" cy="186.25" r="3.625" fill="#7c3aed"/>
<circle cx="153.75" cy="188.75" r="3.625" fill="#7c3aed"/>
<circle cx="166.25" cy="191.25" r="3.625" fill="#7c3aed"/>
<circle cx="178.75" cy="193.75" r="3.625" fill="#7c3aed"/>
<circle cx="191.25" cy="196.25" r="3.625" fill="#7c3aed"/>
<circle cx="203.75" cy="198.75" r="3.625" fill="#7c3aed"/>
<circle cx="216.25" cy="201.25" r="3.625" fill="#7c3aed"/>
<circle cx="228.75" cy="203.75" r="3.625" fill="#7c3aed"/>
<circle cx="241.25" cy="206.25" r="3.625" fill="#7c3aed"/>
<circle cx="253.75" cy="208.75" r="3.625" fill="#7c3aed"/>
<circle cx="266.25" cy="211.25" r="3.625" fill="#7c3aed"/>
<circle cx="278.75" cy="213.75" r="3.625" fill="#7c3aed"/>
<circle cx="291.25" cy="216.25" r="3.625" fill="#7c3aed"/>
<circle cx="303.75" cy="218.75" r="3.625" fill="#7c3aed"/>
<circle cx="316.25" cy="221.25" r="3.625" fill="#7c3aed"/>
<circle cx="328.75" cy="223.75" r="3.625" fill="#7c3aed"/>
<circle cx="341.25" cy="226.25" r="3.625" fill="#7c3aed"/>
<circle cx="353.75" cy="228.75" r="3.625" fill="#7c3aed"/>
<circle cx="366.25" cy="231.25" r="3.625" fill="#7c3aed"/>
<circle cx="378.75" cy="233.75" r="3.625" fill="#7c3aed"/>
<circle cx="391.25" cy="236.25" r="3.625" fill="#7c3aed"/>
<circle cx="403.75" cy="238.75" r="3.625" fill="#7c3aed"/>
<circle cx="416.25" cy="241.25" r="3.625" fill="#7c3aed"/>
<circle cx="428.75" cy="243.75" r="3.625" fill="#7c3aed"/>
<circle cx="441.25" cy="246.25" r="3.625" fill="#7c3aed"/>
<circle cx="453.75" cy="248.75" r="3.625" fill="#7c3aed"/>
<circle cx="466.25" cy="251.25" r="3.625" fill="#7c3aed"/>
<circle cx="478.75" cy="253.75" r="3.625" fill="#7c3aed"/>
<circle cx="491.25" cy="256.25" r="3.625" fill="#7c3aed"/>
<circle cx="503.75" cy="258.75" r="3.625" fill="#7c3aed"/>
<circle cx="516.25" cy="261.25" r="3.625" fill="#7c3aed"/>
<circle cx="528.75" cy="263.75" r="3.625" fill="#7c3aed"/>
<circle cx="541.25" cy="266.25" r="3.625" fill="#7c3aed"/>
<circle cx="553.75" cy="268.75" r="3.625" fill="#7c3aed"/>
<circle cx="566.25" cy="271.25" r="3.625" fill="#7c3aed"/>
<circle cx="578.75" cy="273.75" r="3.625" fill="#7c3aed"/>
<circle cx="591.25" cy="276.25" r="3.625" fill="#7c3aed"/>
<circle cx="603.75" cy="278.75" r="3.625" fill="#7c3aed"/>
<circle cx="616.25" cy="281.25" r="3.625" fill="#7c3aed"/>
<circle cx="628.75" cy="283.75" r="3.625" fill="#7c3aed"/>
<circle cx="641.25" cy="286.25" r="3.625" fill="#7c3aed"/>
<circle cx="653.75" cy="288.75" r="3.625" fill="#7c3aed"/>
<circle cx="666.25" cy="291.25" r="3.625" fill="#7c3aed"/>
<circle cx="678.75" cy="293.75" r="3.625" fill="#7c3aed"/>
<circle cx="691.25" cy="296.25" r="3.625" fill="#7c3aed"/>
<circle cx="703.75" cy="298.75" r="3.625" fill="#7c3aed"/>
<circle cx="716.25" cy="301.25" r="3.625" fill="#7c3aed"/>
<circle cx="728.75" cy="303.75" r="3.625" fill="#7c3aed"/>
<circle cx="741.25" cy="306.25" r="3.625" fill="#7c3aed"/>
<circle cx="753.75" cy="308.75" r="3.625" fill="#7c3aed"/>
<circle cx="766.25" cy="311.25" r="3.625" fill="#7c3aed"/>
<circle cx="778.75" cy="313.75" r="3.625" fill="#7c3aed"/>
<circle cx="791.25" cy="316.25" r="3.625" fill="#7c3aed"/>
<circle cx="803.75" cy="318.75" r="3.625" fill="#7c3aed"/>
<circle cx="816.25" cy="321.25" r="3.625" fill="#7c3aed"/>
<circle cx="828.75" cy="323.75" r="3.625" fill="#7c3aed"/>
<circle cx="841.25" cy="326.25" r="3.625" fill="#7c3aed"/>
<circle cx="853.75" cy="328.75" r="3.625" fill="#7c3aed"/>
<text x="60" y="128" text-anchor="start" style="font-size:18px;font-weight:700;fill:#7c3aed">歩数 64</text>
<text x="60" y="152" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">霧の濃さの積分(光学的厚さ)= 1.082</text>
<text x="60" y="174" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">式の値 1.082 に対するずれ 0.0%</text>
</g>
<rect x="30" y="360" width="560" height="150" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 歩数ごとのずれ(%)</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0764;0.0766;1.0000" values="0;0;1;1"/><text x="46" y="400" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">2 歩</text>
<rect x="100" y="388" width="28.18" height="16" fill="#e5484d" opacity="0.85"/>
<text x="136.18004097720987" y="401" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">2.0%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2296;0.2298;1.0000" values="0;0;1;1"/><text x="46" y="424" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">4 歩</text>
<rect x="100" y="412" width="7.12" height="16" fill="#e5aa28" opacity="0.85"/>
<text x="115.12038405388644" y="425" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">0.5%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3828;0.3830;1.0000" values="0;0;1;1"/><text x="46" y="448" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">8 歩</text>
<rect x="100" y="436" width="2.0" height="16" fill="#2ea043" opacity="0.85"/>
<text x="110.0" y="449" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">0.1%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5360;0.5362;1.0000" values="0;0;1;1"/><text x="46" y="472" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">16 歩</text>
<rect x="100" y="460" width="2.0" height="16" fill="#2563eb" opacity="0.85"/>
<text x="110.0" y="473" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">0.0%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6892;0.6894;1.0000" values="0;0;1;1"/><text x="46" y="496" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">64 歩</text>
<rect x="100" y="484" width="2.0" height="16" fill="#7c3aed" opacity="0.85"/>
<text x="110.0" y="497" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">0.0%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8126;0.8128;1.0000" values="0;0;1;1"/><rect x="620" y="372" width="310" height="130" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="636" y="396" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">式 exp で、積分が一発で出る</text>
<text x="636" y="420" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">τ = σ0·e^(−b·h0)·(1 − e^(−b·dy·L)) ÷ (b·dy)</text>
<text x="636" y="442" text-anchor="start" style="font-size:14px;font-weight:700;fill:#166534">= 1.082(歩数 0 のコスト)</text>
<text x="636" y="465" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">少しずつ進めると、歩数分の計算が必要</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">霧は、低い所ほど濃い。視線が通る高さで、濃さが変わる<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">少しずつ進めて足すと、歩数が増えるほど、式の値に近づく<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.8296;0.8298;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">濃さが指数関数なら、積分は式で一発。毎画素の積分でも、歩数ゼロで正確<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8296;0.8298;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:height-fog-ray:end -->

## Height Fog {#高さフォグ}
**谷や低地に霧が溜まる**表現です。**霧の密度が高さに対して指数的に減る**と**仮定します**。

<div class="formula">density(h) = density₀ · exp( −falloff · h )</div>

**視線に沿った光学的厚さは、密度を積分した値**です。**指数関数の積分は、解析的に求まる**ので**ステップを刻まず 1 回で計算できます**。

```hlsl
float HeightFogOpticalDepth(float3 camera_pos, float3 world_pos) {
  float3 delta = world_pos - camera_pos;
  float distance_to_pixel = length(delta);
  float height_difference = delta.y;

  float falloff = fog_height_falloff;
  float base = fog_density * exp(-falloff * (camera_pos.y - fog_base_height));
  float integral;
  if (abs(height_difference) > 0.0001) {
    integral = (1.0 - exp(-falloff * height_difference)) / (falloff * height_difference);
  } else {
    integral = 1.0;
  }
  return base * integral * distance_to_pixel;
}

float transmittance = exp(-HeightFogOpticalDepth(camera_position, world_position));
```

| 点 | 説明 |
| --- | --- |
| **解析解** | **視線の高さが変わる区間の積分を、閉じた式で**（**ステップ不要**） |
| **`base`** | **カメラの高さでの密度** |
| **高さ差が 0 に近い** | **0 除算を避けるため、積分の値を 1 に** |
| **`fog_base_height`** | **霧が最も濃い高さ**（**谷底・海面**） |
| **`falloff`** | **大きいほど、霧が薄い層に集中** |

**雲海・谷の霧・朝霧**の表現に**効果的**です。

### Deriving the Integral {#積分の導出}

なぜ解析解が出るのかを確認します。視線を、カメラから画素までの線分としてパラメータ s（0 から d）で表します。カメラの高さを h₀、画素の高さとの差を Δh とすると、線分上の高さは `h(s) = h₀ + Δh · s / d` です。密度は `density₀ · exp(−falloff · h)` なので、光学的厚さは次の積分になります。

<div class="formula">τ = ∫₀^d density₀ · exp(−k (h₀ + Δh · s/d)) ds = density₀ · exp(−k h₀) · d · (1 − exp(−k Δh)) / (k Δh)</div>

指数関数の積分は、指数関数のままなので、閉じた式で書けます。コードの `integral` がこの `(1 − exp(−k Δh)) / (k Δh)` の部分です。Δh が 0 に近いと分母が 0 になりますが、極限は 1 です（水平に近い視線では、高さが変わらず、一定密度の霧と同じです）。これは Wenzel の GDC 2007 の講演 "Real-time Atmospheric Effects in Games Revisited" で広まった、実用的な高さフォグの定式化です。

### Usage Tips {#使い方のコツ}

`falloff` は、霧の層の厚みを決めます。たとえば 0.1 なら、高さ 10 m ごとに密度が約 1/e（37 %）に下がります。層の厚みを 20〜50 m にしたければ、falloff を 0.02〜0.05 程度にします。`fog_base_height` を水面の高さに合わせれば、海岸の霞が自然に出ます。複数の層を重ねたり、時間で `fog_base_height` を動かしたりすると、朝霧が晴れていく演出も作れます。

高さフォグの弱点は、<strong>霧が空間に一様に広がる</strong>ことです。特定の谷だけに霧を溜めたい場合や、光線が差し込む様子（ライト シャフト）を出したい場合には、3D ボリュームを使う[ボリューメトリック フォグ](../volumetric-fog/index.md)が必要になります。

## Common Mistakes {#よくあるミス}

??? failure "霧が、高さに関係なく一様"
    **高さで密度を減らす**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **高さで密度を減らして、霧をたまらせる**

## References {#参考}

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## Related Pages {#関連ページ}

- [Aerial Perspective and Fog](index.md)
- [Volumetric Fog](../volumetric-fog/index.md)
