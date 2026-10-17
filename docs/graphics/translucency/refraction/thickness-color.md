---
title: Thickness and Color
tags:
  - 描画
---

# Thickness and Color

**色付きのガラスや水は、光が通る距離（厚み）が長いほど、色が濃くなります**。**これがビア＝ランバートの法則**で、**吸収を指数で表します**。このページでは、**厚みの求め方と、色の付け方**を説明します。

!!! tip "ポイント"
    - **透過率 ＝ exp(−吸収係数 × 厚み)**。
    - **厚み ＝ 裏面の深度 − 表面の深度**で求める。
    - **色ごとに吸収係数を変える**と、**色付きになる**。
    - **厚みが一定でも、見た目を作れる**（簡易版）。

<!-- fig:beer-thickness:begin -->

<svg class="fig illust motion" data-fig="beer-thickness" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-beer-thickness" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ビア＝ランバート:光が通る厚みが増えると、色が指数で濃くなる</text>
<rect x="60.0" y="278.0952380952381" width="10.6" height="21.904761904761905" fill="#f4fbfe"/>
<rect x="70.0" y="274.2857142857143" width="10.6" height="25.714285714285715" fill="#e0f3fb"/>
<rect x="80.0" y="270.4761904761905" width="10.6" height="29.523809523809526" fill="#ceebf8"/>
<rect x="90.0" y="266.6666666666667" width="10.6" height="33.33333333333333" fill="#bde3f5"/>
<rect x="100.0" y="262.8571428571429" width="10.6" height="37.14285714285714" fill="#addbf2"/>
<rect x="110.0" y="259.04761904761904" width="10.6" height="40.95238095238095" fill="#9fd4ef"/>
<rect x="120.0" y="255.23809523809524" width="10.6" height="44.76190476190476" fill="#92cded"/>
<rect x="130.0" y="251.42857142857144" width="10.6" height="48.57142857142857" fill="#86c7ea"/>
<rect x="140.0" y="247.61904761904762" width="10.6" height="52.38095238095238" fill="#7bc0e7"/>
<rect x="150.0" y="243.8095238095238" width="10.6" height="56.19047619047619" fill="#71bae5"/>
<rect x="160.0" y="240.0" width="10.6" height="60.0" fill="#68b4e2"/>
<rect x="170.0" y="236.1904761904762" width="10.6" height="63.80952380952381" fill="#5faee0"/>
<rect x="180.0" y="232.38095238095238" width="10.6" height="67.61904761904762" fill="#57a8dd"/>
<rect x="190.0" y="228.57142857142856" width="10.6" height="71.42857142857143" fill="#50a3db"/>
<rect x="200.0" y="224.76190476190476" width="10.6" height="75.23809523809524" fill="#4a9dd8"/>
<rect x="210.0" y="220.95238095238096" width="10.6" height="79.04761904761905" fill="#4498d6"/>
<rect x="220.0" y="217.14285714285714" width="10.6" height="82.85714285714286" fill="#3e93d3"/>
<rect x="230.0" y="213.33333333333331" width="10.6" height="86.66666666666667" fill="#398ed1"/>
<rect x="240.0" y="209.52380952380952" width="10.6" height="90.47619047619048" fill="#348ace"/>
<rect x="250.0" y="205.71428571428572" width="10.6" height="94.28571428571429" fill="#3085cc"/>
<rect x="260.0" y="201.90476190476193" width="10.6" height="98.09523809523809" fill="#2c81ca"/>
<rect x="270.0" y="198.0952380952381" width="10.6" height="101.9047619047619" fill="#287dc7"/>
<rect x="280.0" y="194.28571428571428" width="10.6" height="105.71428571428571" fill="#2578c5"/>
<rect x="290.0" y="190.47619047619048" width="10.6" height="109.52380952380952" fill="#2275c3"/>
<rect x="300.0" y="186.66666666666666" width="10.6" height="113.33333333333334" fill="#1f71c1"/>
<rect x="310.0" y="182.85714285714286" width="10.6" height="117.14285714285714" fill="#1d6dbf"/>
<rect x="320.0" y="179.04761904761904" width="10.6" height="120.95238095238095" fill="#1a69bc"/>
<rect x="330.0" y="175.23809523809524" width="10.6" height="124.76190476190476" fill="#1866ba"/>
<rect x="340.0" y="171.42857142857142" width="10.6" height="128.57142857142858" fill="#1663b8"/>
<rect x="350.0" y="167.61904761904762" width="10.6" height="132.38095238095238" fill="#145fb6"/>
<rect x="360.0" y="163.8095238095238" width="10.6" height="136.1904761904762" fill="#135cb4"/>
<rect x="370.0" y="160.0" width="10.6" height="140.0" fill="#1159b2"/>
<rect x="380.0" y="156.1904761904762" width="10.6" height="143.8095238095238" fill="#1056b0"/>
<rect x="390.0" y="152.38095238095238" width="10.6" height="147.61904761904762" fill="#0e53ae"/>
<rect x="400.0" y="148.57142857142858" width="10.6" height="151.42857142857142" fill="#0d51ac"/>
<rect x="410.0" y="144.76190476190476" width="10.6" height="155.23809523809524" fill="#0c4eaa"/>
<rect x="420.0" y="140.95238095238096" width="10.6" height="159.04761904761904" fill="#0b4ca8"/>
<rect x="430.0" y="137.14285714285714" width="10.6" height="162.85714285714286" fill="#0a49a6"/>
<rect x="440.0" y="133.33333333333334" width="10.6" height="166.66666666666666" fill="#0947a4"/>
<rect x="450.0" y="129.52380952380952" width="10.6" height="170.47619047619048" fill="#0944a2"/>
<rect x="460.0" y="125.71428571428572" width="10.6" height="174.28571428571428" fill="#0842a1"/>
<rect x="470.0" y="121.9047619047619" width="10.6" height="178.0952380952381" fill="#07409f"/>
<polygon points="60,300 480,300 480,120" fill="none" stroke="#1f2937" stroke-width="2"/>
<text x="60" y="320" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">薄い</text>
<text x="480" y="320" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">厚い</text>
<rect x="540" y="100" width="200" height="160" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="590.0" y1="100" x2="590.0" y2="260" stroke="#e2e8f0" stroke-width="1"/>
<line x1="540" y1="140.0" x2="740" y2="140.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="640.0" y1="100" x2="640.0" y2="260" stroke="#e2e8f0" stroke-width="1"/>
<line x1="540" y1="180.0" x2="740" y2="180.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="690.0" y1="100" x2="690.0" y2="260" stroke="#e2e8f0" stroke-width="1"/>
<line x1="540" y1="220.0" x2="740" y2="220.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="740" y="280" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">厚み</text>
<text x="540" y="92" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">透過率</text>
<path d="M540.0,100.0 L545.0,113.77 L550.0,126.36 L555.0,137.86 L560.0,148.37 L565.0,157.98 L570.0,166.76 L575.0,174.79 L580.0,182.12 L585.0,188.82 L590.0,194.95 L595.0,200.55 L600.0,205.66 L605.0,210.34 L610.0,214.62 L615.0,218.52 L620.0,222.09 L625.0,225.35 L630.0,228.34 L635.0,231.06 L640.0,233.55 L645.0,235.83 L650.0,237.91 L655.0,239.81 L660.0,241.55 L665.0,243.14 L670.0,244.59 L675.0,245.91 L680.0,247.13 L685.0,248.23 L690.0,249.25 L695.0,250.17 L700.0,251.02 L705.0,251.79 L710.0,252.5 L715.0,253.14 L720.0,253.73 L725.0,254.27 L730.0,254.77 L735.0,255.22 L740.0,255.63" fill="none" stroke="#e5484d" stroke-width="3" opacity="1"/>
<path d="M540.0,100.0 L545.0,105.5 L550.0,110.82 L555.0,115.95 L560.0,120.9 L565.0,125.69 L570.0,130.31 L575.0,134.77 L580.0,139.07 L585.0,143.23 L590.0,147.25 L595.0,151.13 L600.0,154.87 L605.0,158.49 L610.0,161.98 L615.0,165.35 L620.0,168.61 L625.0,171.75 L630.0,174.79 L635.0,177.72 L640.0,180.55 L645.0,183.28 L650.0,185.92 L655.0,188.47 L660.0,190.93 L665.0,193.3 L670.0,195.6 L675.0,197.81 L680.0,199.95 L685.0,202.02 L690.0,204.01 L695.0,205.94 L700.0,207.8 L705.0,209.59 L710.0,211.32 L715.0,213.0 L720.0,214.62 L725.0,216.18 L730.0,217.68 L735.0,219.14 L740.0,220.54" fill="none" stroke="#2ea043" stroke-width="3" opacity="1"/>
<path d="M540.0,100.0 L545.0,101.91 L550.0,103.79 L555.0,105.66 L560.0,107.5 L565.0,109.32 L570.0,111.12 L575.0,112.89 L580.0,114.65 L585.0,116.38 L590.0,118.09 L595.0,119.79 L600.0,121.46 L605.0,123.11 L610.0,124.74 L615.0,126.36 L620.0,127.95 L625.0,129.53 L630.0,131.08 L635.0,132.62 L640.0,134.14 L645.0,135.64 L650.0,137.12 L655.0,138.59 L660.0,140.04 L665.0,141.47 L670.0,142.88 L675.0,144.28 L680.0,145.66 L685.0,147.02 L690.0,148.37 L695.0,149.7 L700.0,151.02 L705.0,152.32 L710.0,153.6 L715.0,154.87 L720.0,156.13 L725.0,157.37 L730.0,158.59 L735.0,159.8 L740.0,160.99" fill="none" stroke="#2563eb" stroke-width="3" opacity="1"/>
<line x1="60" y1="60" x2="60" y2="304" stroke="#e5aa28" stroke-width="3"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0889;0.1137;0.1386;0.1634;0.1883;0.2131;0.2380;0.2629;0.2877;0.3126;0.3374;0.3623;0.3871;0.4120;0.4369;0.4617;0.4866;0.5114;0.5363;0.5611;0.5860;0.6109;0.6357;0.6606;0.6854;0.7103;0.7351;0.7600;1.0000" values="60;60;75;90;105;120;135;150;165;180;195;210;225;240;255;270;285;300;315;330;345;360;375;390;405;420;435;450;465;480;480"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0889;0.1137;0.1386;0.1634;0.1883;0.2131;0.2380;0.2629;0.2877;0.3126;0.3374;0.3623;0.3871;0.4120;0.4369;0.4617;0.4866;0.5114;0.5363;0.5611;0.5860;0.6109;0.6357;0.6606;0.6854;0.7103;0.7351;0.7600;1.0000" values="60;60;75;90;105;120;135;150;165;180;195;210;225;240;255;270;285;300;315;330;345;360;375;390;405;420;435;450;465;480;480"/></line>
<circle cx="540.0" cy="100.0" r="5" fill="#1f2937"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0889;0.1137;0.1386;0.1634;0.1883;0.2131;0.2380;0.2629;0.2877;0.3126;0.3374;0.3623;0.3871;0.4120;0.4369;0.4617;0.4866;0.5114;0.5363;0.5611;0.5860;0.6109;0.6357;0.6606;0.6854;0.7103;0.7351;0.7600;1.0000" values="540;540;547.14;554.29;561.43;568.57;575.71;582.86;590;597.14;604.29;611.43;618.57;625.71;632.86;640;647.14;654.29;661.43;668.57;675.71;682.86;690;697.14;704.29;711.43;718.57;725.71;732.86;740;740"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0889;0.1137;0.1386;0.1634;0.1883;0.2131;0.2380;0.2629;0.2877;0.3126;0.3374;0.3623;0.3871;0.4120;0.4369;0.4617;0.4866;0.5114;0.5363;0.5611;0.5860;0.6109;0.6357;0.6606;0.6854;0.7103;0.7351;0.7600;1.0000" values="100;100;119.3;136.28;151.21;164.33;175.87;186.02;194.95;202.8;209.7;215.77;221.1;225.8;229.92;233.55;236.74;239.55;242.02;244.19;246.09;247.77;249.25;250.54;251.69;252.69;253.57;254.35;255.03;255.63;255.63"/></circle>
<rect x="540" y="300" width="200" height="36" fill="#ffffff" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0889;0.1137;0.1386;0.1634;0.1883;0.2131;0.2380;0.2629;0.2877;0.3126;0.3374;0.3623;0.3871;0.4120;0.4369;0.4617;0.4866;0.5114;0.5363;0.5611;0.5860;0.6109;0.6357;0.6606;0.6854;0.7103;0.7351;0.7600;1.0000" values="#ffffff;#ffffff;#e0f3fb;#c5e7f6;#addbf2;#98d1ee;#86c7ea;#76bde6;#68b4e2;#5babde;#50a3db;#469bd7;#3e93d3;#378cd0;#3085cc;#2a7fc9;#2578c5;#2173c2;#1d6dbf;#1968bb;#1663b8;#135eb5;#1159b2;#0f55af;#0d51ac;#0c4da9;#0a49a6;#0945a3;#0842a1;#073f9e;#073f9e"/></rect>
<text x="640" y="290" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">通り抜けた後の色</text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 0.0:赤の透過率 1.00、緑 1.00、青 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.0885;0.0889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 0.1:赤の透過率 0.88、緑 0.95、青 0.98<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0885;0.0889;0.1134;0.1137;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 0.3:赤の透過率 0.77、緑 0.90、青 0.97<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1134;0.1137;0.1383;0.1386;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 0.4:赤の透過率 0.67、緑 0.86、青 0.95<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1383;0.1386;0.1631;0.1634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 0.6:赤の透過率 0.59、緑 0.81、青 0.93<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1631;0.1634;0.1880;0.1883;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 0.7:赤の透過率 0.51、緑 0.77、青 0.91<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1880;0.1883;0.2128;0.2131;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 0.9:赤の透過率 0.45、緑 0.73、青 0.90<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2128;0.2131;0.2377;0.2380;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 1.0:赤の透過率 0.39、緑 0.70、青 0.88<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2377;0.2380;0.2625;0.2629;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 1.2:赤の透過率 0.34、緑 0.66、青 0.87<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2625;0.2629;0.2874;0.2877;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 1.3:赤の透過率 0.30、緑 0.63、青 0.85<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2874;0.2877;0.3123;0.3126;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 1.5:赤の透過率 0.26、緑 0.60、青 0.84<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3123;0.3126;0.3371;0.3374;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 1.6:赤の透過率 0.23、緑 0.57、青 0.82<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3371;0.3374;0.3620;0.3623;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 1.8:赤の透過率 0.20、緑 0.54、青 0.81<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3620;0.3623;0.3868;0.3871;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 1.9:赤の透過率 0.18、緑 0.51、青 0.79<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3868;0.3871;0.4117;0.4120;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 2.1:赤の透過率 0.15、緑 0.48、青 0.78<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4117;0.4120;0.4365;0.4369;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 2.2:赤の透過率 0.14、緑 0.46、青 0.77<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4365;0.4369;0.4614;0.4617;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 2.4:赤の透過率 0.12、緑 0.44、青 0.75<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4614;0.4617;0.4863;0.4866;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 2.5:赤の透過率 0.10、緑 0.41、青 0.74<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4863;0.4866;0.5111;0.5114;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 2.7:赤の透過率 0.09、緑 0.39、青 0.73<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5111;0.5114;0.5360;0.5363;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 2.8:赤の透過率 0.08、緑 0.37、青 0.71<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5360;0.5363;0.5608;0.5611;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 3.0:赤の透過率 0.07、緑 0.35、青 0.70<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5608;0.5611;0.5857;0.5860;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 3.1:赤の透過率 0.06、緑 0.34、青 0.69<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5857;0.5860;0.6105;0.6109;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 3.3:赤の透過率 0.05、緑 0.32、青 0.68<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6105;0.6109;0.6354;0.6357;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 3.4:赤の透過率 0.05、緑 0.30、青 0.66<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6354;0.6357;0.6603;0.6606;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 3.6:赤の透過率 0.04、緑 0.29、青 0.65<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6603;0.6606;0.6851;0.6854;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 3.7:赤の透過率 0.04、緑 0.27、青 0.64<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6851;0.6854;0.7100;0.7103;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 3.9:赤の透過率 0.03、緑 0.26、青 0.63<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7100;0.7103;0.7348;0.7351;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="352" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">厚み 4.0:赤の透過率 0.03、緑 0.25、青 0.62<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7348;0.7351;0.7597;0.7600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="380" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">透過率 = exp(−吸収係数 × 厚み)。色ごとに吸収が違うので、厚いほど色が付く（赤から先に消える ＝ 青緑）。</text>
</svg>

<!-- fig:beer-thickness:end -->

## 厚みと色（ビア＝ランバートの法則）
**色付きガラスや水は、厚いほど、光が吸収されて色が濃く**なります。

<div class="formula">T = exp(−σ · d)　（T：透過率、σ：吸収係数（RGB）、d：厚み）</div>

| 記号 | 意味 |
| --- | --- |
| <strong>σ（シグマ）</strong> | **単位長さあたりの吸収**（**色ごと**）。**水は赤を強く吸収**（σ_r が大きい） |
| **d** | **光が媒質の中を進む距離**（厚み） |
| **T** | **透過する光の割合**（RGB） |

```hlsl
float3 absorption = float3(0.4, 0.1, 0.05);
float3 transmittance = exp(-absorption * thickness);
float3 tinted_background = background * transmittance;
```

| 点 | 説明 |
| --- | --- |
| **`absorption`** | <strong>吸収係数（RGB）</strong>。**水なら、赤を強く、青を弱く**吸収し、**青緑に見える** |
| **`thickness`** | **厚み**。**ガラスなら、ほぼ一定**。<strong>水なら、水深（深度差）</strong> |
| **`exp(-σd)`** | **厚いほど、急に暗く・濃く** |

**水深**（水面から底までの距離）は、**不透明の深度と、水面の深度の差**から**求められます**（[Water](../../water/index.md)）。

## よくあるミス

??? failure "厚いガラスも薄いガラスも、同じ色"
    **厚みで、濃さを変える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **厚みが長いほど、色が濃い**
    - [x] **exp で吸収を表す**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [Refraction](index.md)
- [Thin and Thick Glass](thin-thick.md)
- [Water Shading](../../water/shading/index.md)
