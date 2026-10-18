---
title: Height Fog
tags:
  - 描画
---

# Height Fog

<strong>霧は低い所にたまります</strong>。<strong>フォグの密度を高さで指数的に減らす</strong>と、谷にたまる霧が表現できます。このページでは高さフォグを説明します。

!!! tip "ポイント"
    - 密度 ＝ 基準密度 × exp(−高さ × 係数)。
    - 視線に沿って積分すると、解析的に求まる。
    - 低い所ほど濃い霧。
    - 朝霧・谷の霧の表現に向く。

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

## 高さフォグ
<strong>谷や低地に霧が溜まる</strong>表現です。<strong>霧の密度が高さに対して指数的に減る</strong>と仮定します。

<div class="formula">density(h) = density₀ · exp( −falloff · h )</div>

<strong>視線に沿った光学的厚さは密度を積分した値</strong>です。<strong>指数関数の積分は解析的に求まる</strong>のでステップを刻まず 1 回で計算できます。

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
| 解析解 | 視線の高さが変わる区間の積分を、閉じた式で（ステップ不要） |
| `base` | カメラの高さでの密度 |
| 高さ差が 0 に近い | 0 除算を避けるため、積分の値を 1 に |
| `fog_base_height` | 霧が最も濃い高さ（谷底・海面） |
| `falloff` | 大きいほど霧が薄い層に集中 |

<strong>雲海・谷の霧・朝霧</strong>の表現に<strong>効果的</strong>です。

### 積分の導出

なぜ解析解が出るのかを確認します。視線をカメラから画素までの線分としてパラメータ s（0 から d）で表します。カメラの高さを h₀、画素の高さとの差を Δh とすると、線分上の高さは `h(s) = h₀ + Δh · s / d` です。密度は `density₀ · exp(−falloff · h)` なので光学的厚さは次の積分になります。

<div class="formula">τ = ∫₀^d density₀ · exp(−k (h₀ + Δh · s/d)) ds = density₀ · exp(−k h₀) · d · (1 − exp(−k Δh)) / (k Δh)</div>

指数関数の積分は指数関数のままなので、閉じた式で書けます。コードの `integral` がこの `(1 − exp(−k Δh)) / (k Δh)` の部分です。Δh が 0 に近いと分母が 0 になりますが、極限は 1 です（水平に近い視線では、高さが変わらず一定密度の霧と同じです）。これは Wenzel の GDC 2007 の講演 "Real-time Atmospheric Effects in Games Revisited" で広まった、実用的な高さフォグの定式化です。

### 使い方のコツ

`falloff` は霧の層の厚みを決めます。たとえば 0.1 なら高さ 10 m ごとに密度が約 1/e（37 %）に下がります。層の厚みを 20〜50 m にしたければ、falloff を 0.02〜0.05 程度にします。`fog_base_height` を水面の高さに合わせれば、海岸の霞が自然に出ます。複数の層を重ねたり時間で `fog_base_height` を動かしたりすると、朝霧が晴れていく演出も作れます。

高さフォグの弱点は <strong>霧が空間に一様に広がる</strong>ことです。特定の谷だけに霧を溜めたい場合や、光線が差し込む様子（ライト シャフト）を出したい場合には、3D ボリュームを使う[ボリューメトリック フォグ](../volumetric-fog/index.md)が必要になります。

## 高さで濃さが変わる霧

<strong>谷にたまった朝霧</strong>、<strong>地面に近いほど濃い霧</strong>のように、霧の濃さは高さで変わります。高さフォグは霧の密度を高さの関数として、扱います。

```text
密度 ρ(h) = ρ₀ × exp( −k × h )          h: 霧の層の、基準からの、高さ。k: 減り方の速さ
```

<strong>地面で最も濃く</strong>、<strong>高くなるほど指数関数的に薄く</strong>なります。大気そのものの密度（レイリー、ミー）と同じ形です。

## 光学的な厚さを解析的に求める

視線に沿って <strong>密度を積分した値</strong>（<strong>光学的な、厚さ</strong>）が透過率を決めます。密度が指数関数なら積分も解析的に、求められます。

```text
視線: 始点の高さ h₀、終点の高さ h₁、その間の、距離 d。高さは、直線的に変わる。

τ = ρ₀ × d × ( exp(−k h₀) − exp(−k h₁) ) / ( k × (h₁ − h₀) )       （h₁ ≠ h₀ のとき）
τ = ρ₀ × d × exp(−k h₀)                                              （h₁ = h₀ のとき。視線が、水平）
```

<strong>透過率</strong>は `exp(−τ)` です。<strong>積分をループで数値計算せず</strong>、式 1 つで求まります。

## 実装

```hlsl
// カメラから、ワールド位置までの、高さフォグの、透過率を、解析的に求める。
float HeightFogTransmittance(float3 camera, float3 world_pos) {
  float3 ray = world_pos - camera;
  float dist = length(ray);
  float h0 = camera.y - g_fog_base_height;                  // 霧の層の基準から見た、カメラの高さ
  float dh = ray.y;                                         // 視線に沿った、高さの変化
```

<strong>カメラの高さ</strong>と <strong>視線の上下方向の、変化</strong>（`dh`）を求めます。霧の基準の高さ（`g_fog_base_height`）より上か下かを `h0` が、表します。

```hlsl
  float k = g_fog_falloff;                                  // 減り方の速さ（1/m）
  float exponent = k * dh;                                  // 視線に沿った、指数の、変化量
  float fog_at_camera = g_fog_density * exp(-k * h0);       // カメラの位置での、密度
```

<strong>カメラの位置での密度</strong>（`fog_at_camera`）が、<strong>積分の出発点</strong>です。

```hlsl
  // 積分の核: (1 − exp(−k·dh)) / (k·dh)。dh が、ほぼ 0 のとき（水平）は、1 に近づく。
  float integral = (abs(exponent) > 1e-4) ? (1.0 - exp(-exponent)) / exponent : 1.0;
  float optical_depth = fog_at_camera * dist * integral;
  return exp(-optical_depth);
}
```

`(1 − exp(−x)) / x` が <strong>積分の解析解</strong>で <strong>`x → 0`</strong>（水平な視線）で、1 に近づきます。ゼロ割を避けるために `abs(x)` が小さいときは、極限の値（1）を使います。これを距離に掛ければ光学的な厚さが、求まります。

```hlsl
float3 ApplyHeightFog(float3 scene_color, float3 camera, float3 world_pos) {
  float t = HeightFogTransmittance(camera, world_pos);
  return scene_color * t + g_fog_color * (1.0 - t);
}
```

最後に、<strong>通常の霧と同じ式</strong>で <strong>物の色と、霧の色</strong>を混ぜます。

## 見た目の特徴

| 状況 | 見え方 |
| --- | --- |
| カメラが霧の層の中（低い所） | 周りが霧に、包まれる。視界が短い |
| カメラが層の上（高い所） | 下の方に霧が、たまって見える（雲海、谷の霧）。上空は澄んでいる |
| 視線が上向き | 高さが、上がるので霧が薄く（空は霧が、少ない） |
| 視線が下向き（地面） | 濃い層を、通るので霧が濃い |

<strong>山の上から谷を見下ろす</strong>と、<strong>谷底に霧がたまっている</strong>様子が自然に、出ます。

## 他の霧との組み合わせ

<strong>高さフォグ</strong>と <strong>距離フォグ</strong>（[Fog Equations](fog-equation.md)）を、足し合わせることができます（光学的な厚さを、合計）。

```hlsl
// 一様な、霧（遠景の、霞）と、高さフォグ（谷の、霧）を、光学的な厚さの、足し算で、組み合わせる。
float tau_uniform = g_uniform_density * dist;
float tau_height = ...;                                    // 上の式で求めた、高さフォグの、光学的な厚さ
float transmittance = exp(-(tau_uniform + tau_height));
```

<strong>透過率の掛け算</strong>（`exp(−a) × exp(−b) = exp(−(a + b))`）なので、<strong>足し算</strong>で合成できます。

## 注意点

| 項目 | 内容 |
| --- | --- |
| 視線が地面を貫く | 視線が、霧の層の下（地面の下）に潜る場合は地面で、止める（物の位置が終点） |
| 霧の層の上端 | 指数関数は、無限に続くのである高さで霧を、0 にするクランプも使う（層の上端が、はっきりする見た目） |
| 局所的な霧（沼地だけ） | 全体の、高さフォグではできない。ボリューム フォグ（[Volumetric Fog](../volumetric-fog/index.md)）、または霧のボリュームを置く |

## よくあるミス

??? failure "霧が、高さに関係なく一様"
    <strong>高さで密度を減らす</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 高さで密度を減らして、霧をたまらせる

## 参考

- Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）
- Beer, "Bestimmung der Absorption des rothen Lichts in farbigen Flüssigkeiten", Annalen der Physik, 1852（吸収の法則）

## 関連ページ

- [Aerial Perspective and Fog](index.md)
- [Volumetric Fog](../volumetric-fog/index.md)
