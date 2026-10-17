---
title: Atmosphere Model
tags:
  - 描画
---

# Atmosphere Model

**大気を、高さごとの密度を持つ層として表します**。**空気分子（レイリー）、エアロゾル（ミー）、オゾンが、それぞれ違う散乱・吸収を持ちます**。このページでは、**大気のモデル**を説明します。

!!! tip "ポイント"
    - **レイリー：高さとともに指数で薄くなる（約 8 km）**。
    - **ミー：低い所に多い（約 1.2 km）**。
    - **オゾン：青を吸収し、夕空の色に効く**。
    - **散乱係数は、波長ごとに持つ**。

<!-- fig:rayleigh-wavelength:begin -->

<svg class="fig illust motion" data-fig="rayleigh-wavelength" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-rayleigh-wavelength" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">レイリー散乱:波長が短い（青い）光ほど、強く散る（1 / λ⁴）</text>
<rect x="60" y="80" width="400" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="160.0" y1="80" x2="160.0" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="135.0" x2="460" y2="135.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="260.0" y1="80" x2="260.0" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="190.0" x2="460" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="360.0" y1="80" x2="360.0" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="245.0" x2="460" y2="245.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="460" y="320" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">波長（nm）</text>
<text x="60" y="72" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">散乱の強さ</text>
<path d="M60.0,80.0 L66.67,90.66 L73.33,100.69 L80.0,110.12 L86.67,119.01 L93.33,127.37 L100.0,135.26 L106.67,142.71 L113.33,149.74 L120.0,156.38 L126.67,162.66 L133.33,168.59 L140.0,174.21 L146.67,179.54 L153.33,184.58 L160.0,189.37 L166.67,193.9 L173.33,198.21 L180.0,202.3 L186.67,206.19 L193.33,209.89 L200.0,213.4 L206.67,216.75 L213.33,219.94 L220.0,222.97 L226.67,225.86 L233.33,228.62 L240.0,231.25 L246.67,233.76 L253.33,236.16 L260.0,238.45 L266.67,240.64 L273.33,242.73 L280.0,244.73 L286.67,246.65 L293.33,248.48 L300.0,250.23 L306.67,251.91 L313.33,253.52 L320.0,255.06 L326.67,256.54 L333.33,257.96 L340.0,259.32 L346.67,260.63 L353.33,261.89 L360.0,263.09 L366.67,264.25 L373.33,265.36 L380.0,266.43 L386.67,267.46 L393.33,268.45 L400.0,269.4 L406.67,270.32 L413.33,271.2 L420.0,272.05 L426.67,272.87 L433.33,273.66 L440.0,274.42 L446.67,275.15 L453.33,275.86 L460.0,276.54" fill="none" stroke="#7c3aed" stroke-width="4" opacity="1"/>
<rect x="60.0" y="328" width="7.17" height="14" fill="#ff00ff"/>
<rect x="66.67" y="328" width="7.17" height="14" fill="#df00ff"/>
<rect x="73.33" y="328" width="7.17" height="14" fill="#bf00ff"/>
<rect x="80.0" y="328" width="7.17" height="14" fill="#9f00ff"/>
<rect x="86.67" y="328" width="7.17" height="14" fill="#8000ff"/>
<rect x="93.33" y="328" width="7.17" height="14" fill="#6000ff"/>
<rect x="100.0" y="328" width="7.17" height="14" fill="#4000ff"/>
<rect x="106.67" y="328" width="7.17" height="14" fill="#2000ff"/>
<rect x="113.33" y="328" width="7.17" height="14" fill="#0000ff"/>
<rect x="120.0" y="328" width="7.17" height="14" fill="#001aff"/>
<rect x="126.67" y="328" width="7.17" height="14" fill="#0033ff"/>
<rect x="133.33" y="328" width="7.17" height="14" fill="#004cff"/>
<rect x="140.0" y="328" width="7.17" height="14" fill="#0066ff"/>
<rect x="146.67" y="328" width="7.17" height="14" fill="#0080ff"/>
<rect x="153.33" y="328" width="7.17" height="14" fill="#0099ff"/>
<rect x="160.0" y="328" width="7.17" height="14" fill="#00b2ff"/>
<rect x="166.67" y="328" width="7.17" height="14" fill="#00ccff"/>
<rect x="173.33" y="328" width="7.17" height="14" fill="#00e6ff"/>
<rect x="180.0" y="328" width="7.17" height="14" fill="#00ffff"/>
<rect x="186.67" y="328" width="7.17" height="14" fill="#00ffbf"/>
<rect x="193.33" y="328" width="7.17" height="14" fill="#00ff80"/>
<rect x="200.0" y="328" width="7.17" height="14" fill="#00ff40"/>
<rect x="206.67" y="328" width="7.17" height="14" fill="#00ff00"/>
<rect x="213.33" y="328" width="7.17" height="14" fill="#12ff00"/>
<rect x="220.0" y="328" width="7.17" height="14" fill="#24ff00"/>
<rect x="226.67" y="328" width="7.17" height="14" fill="#37ff00"/>
<rect x="233.33" y="328" width="7.17" height="14" fill="#49ff00"/>
<rect x="240.0" y="328" width="7.17" height="14" fill="#5bff00"/>
<rect x="246.67" y="328" width="7.17" height="14" fill="#6dff00"/>
<rect x="253.33" y="328" width="7.17" height="14" fill="#80ff00"/>
<rect x="260.0" y="328" width="7.17" height="14" fill="#92ff00"/>
<rect x="266.67" y="328" width="7.17" height="14" fill="#a4ff00"/>
<rect x="273.33" y="328" width="7.17" height="14" fill="#b6ff00"/>
<rect x="280.0" y="328" width="7.17" height="14" fill="#c8ff00"/>
<rect x="286.67" y="328" width="7.17" height="14" fill="#dbff00"/>
<rect x="293.33" y="328" width="7.17" height="14" fill="#edff00"/>
<rect x="300.0" y="328" width="7.17" height="14" fill="#ffff00"/>
<rect x="306.67" y="328" width="7.17" height="14" fill="#ffeb00"/>
<rect x="313.33" y="328" width="7.17" height="14" fill="#ffd800"/>
<rect x="320.0" y="328" width="7.17" height="14" fill="#ffc400"/>
<rect x="326.67" y="328" width="7.17" height="14" fill="#ffb100"/>
<rect x="333.33" y="328" width="7.17" height="14" fill="#ff9d00"/>
<rect x="340.0" y="328" width="7.17" height="14" fill="#ff8900"/>
<rect x="346.67" y="328" width="7.17" height="14" fill="#ff7600"/>
<rect x="353.33" y="328" width="7.17" height="14" fill="#ff6200"/>
<rect x="360.0" y="328" width="7.17" height="14" fill="#ff4e00"/>
<rect x="366.67" y="328" width="7.17" height="14" fill="#ff3b00"/>
<rect x="373.33" y="328" width="7.17" height="14" fill="#ff2700"/>
<rect x="380.0" y="328" width="7.17" height="14" fill="#ff1400"/>
<rect x="386.67" y="328" width="7.17" height="14" fill="#ff0000"/>
<rect x="393.33" y="328" width="7.17" height="14" fill="#ff0000"/>
<rect x="400.0" y="328" width="7.17" height="14" fill="#ff0000"/>
<rect x="406.67" y="328" width="7.17" height="14" fill="#ff0000"/>
<rect x="413.33" y="328" width="7.17" height="14" fill="#ff0000"/>
<rect x="420.0" y="328" width="7.17" height="14" fill="#ff0000"/>
<rect x="426.67" y="328" width="7.17" height="14" fill="#ff0000"/>
<rect x="433.33" y="328" width="7.17" height="14" fill="#ff0000"/>
<rect x="440.0" y="328" width="7.17" height="14" fill="#ff0000"/>
<rect x="446.67" y="328" width="7.17" height="14" fill="#ff0000"/>
<rect x="453.33" y="328" width="7.17" height="14" fill="#ff0000"/>
<circle cx="460.0" cy="276.54" r="7" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0889;0.1137;0.1386;0.1634;0.1883;0.2131;0.2380;0.2629;0.2877;0.3126;0.3374;0.3623;0.3871;0.4120;0.4369;0.4617;0.4866;0.5114;0.5363;0.5611;0.5860;0.6109;0.6357;0.6606;0.6854;0.7103;0.7351;0.7600;1.0000" values="460;460;445.71;431.43;417.14;402.86;388.57;374.29;360;345.71;331.43;317.14;302.86;288.57;274.29;260;245.71;231.43;217.14;202.86;188.57;174.29;160;145.71;131.43;117.14;102.86;88.57;74.29;60;60"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0889;0.1137;0.1386;0.1634;0.1883;0.2131;0.2380;0.2629;0.2877;0.3126;0.3374;0.3623;0.3871;0.4120;0.4369;0.4617;0.4866;0.5114;0.5363;0.5611;0.5860;0.6109;0.6357;0.6606;0.6854;0.7103;0.7351;0.7600;1.0000" values="276.54;276.54;275.05;273.44;271.69;269.8;267.75;265.52;263.09;260.45;257.56;254.41;250.96;247.18;243.02;238.45;233.41;227.85;221.69;214.86;207.27;198.81;189.37;178.79;166.93;153.58;138.51;121.45;102.07;80;80"/></circle>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 700 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.0885;0.0889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 688 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0885;0.0889;0.1134;0.1137;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 677 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1134;0.1137;0.1383;0.1386;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 666 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1383;0.1386;0.1631;0.1634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 655 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1631;0.1634;0.1880;0.1883;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 644 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1880;0.1883;0.2128;0.2131;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 633 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2128;0.2131;0.2377;0.2380;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 622 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2377;0.2380;0.2625;0.2629;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 611 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2625;0.2629;0.2874;0.2877;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 600 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2874;0.2877;0.3123;0.3126;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 588 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3123;0.3126;0.3371;0.3374;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 577 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3371;0.3374;0.3620;0.3623;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 566 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3620;0.3623;0.3868;0.3871;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 555 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3868;0.3871;0.4117;0.4120;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 544 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4117;0.4120;0.4365;0.4369;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 533 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4365;0.4369;0.4614;0.4617;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 522 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4614;0.4617;0.4863;0.4866;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 511 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4863;0.4866;0.5111;0.5114;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 500 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5111;0.5114;0.5360;0.5363;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 488 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5360;0.5363;0.5608;0.5611;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 477 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5608;0.5611;0.5857;0.5860;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 466 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5857;0.5860;0.6105;0.6109;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 455 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6105;0.6109;0.6354;0.6357;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 444 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6354;0.6357;0.6603;0.6606;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 433 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6603;0.6606;0.6851;0.6854;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 422 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6851;0.6854;0.7100;0.7103;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 411 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7100;0.7103;0.7348;0.7351;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="120" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">波長 400 nm<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7348;0.7351;0.7597;0.7600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 1.0 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.0885;0.0889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 1.1 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0885;0.0889;0.1134;0.1137;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 1.1 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1134;0.1137;0.1383;0.1386;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 1.2 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1383;0.1386;0.1631;0.1634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 1.3 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1631;0.1634;0.1880;0.1883;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 1.4 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1880;0.1883;0.2128;0.2131;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 1.5 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2128;0.2131;0.2377;0.2380;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 1.6 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2377;0.2380;0.2625;0.2629;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 1.7 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2625;0.2629;0.2874;0.2877;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 1.9 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2874;0.2877;0.3123;0.3126;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 2.0 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3123;0.3126;0.3371;0.3374;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 2.2 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3371;0.3374;0.3620;0.3623;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 2.3 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3620;0.3623;0.3868;0.3871;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 2.5 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3868;0.3871;0.4117;0.4120;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 2.7 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4117;0.4120;0.4365;0.4369;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 3.0 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4365;0.4369;0.4614;0.4617;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 3.2 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4614;0.4617;0.4863;0.4866;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 3.5 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4863;0.4866;0.5111;0.5114;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 3.8 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5111;0.5114;0.5360;0.5363;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 4.2 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5360;0.5363;0.5608;0.5611;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 4.6 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5608;0.5611;0.5857;0.5860;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 5.1 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5857;0.5860;0.6105;0.6109;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 5.6 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6105;0.6109;0.6354;0.6357;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 6.2 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6354;0.6357;0.6603;0.6606;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 6.8 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6603;0.6606;0.6851;0.6854;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 7.6 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6851;0.6854;0.7100;0.7103;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 8.4 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7100;0.7103;0.7348;0.7351;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="154" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed" opacity="0">700 nm の 9.4 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7348;0.7351;0.7597;0.7600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="500" y="220" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">赤（700 nm）に比べ、青（450 nm）は</text>
<text x="500" y="242" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">約 5.9 倍も強く散る → 空は青い</text>
<text x="500" y="280" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">夕焼けは、光が長く通って、青が散りきり、</text>
<text x="500" y="302" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">赤だけが残る。</text>
</svg>

<!-- fig:rayleigh-wavelength:end -->

## 大気のモデル
**地球の大気は球殻**です。**密度は高さに対して指数的に減ります**。

<div class="formula">ρ(h) = exp( −h / H )　（H：スケール ハイト）</div>

大気は、3 つの成分でできています。<strong>レイリー（空気分子）</strong>は、スケール ハイトが約 8 km で、青い光を強く散らします。前にも後ろにもほぼ均等に散らします。<strong>ミー（エアロゾル）</strong>は、スケール ハイトが約 1.2 km で、ほぼ白く散らし、前方への散乱が強いのが特徴です（太陽の周りのにじみ）。<strong>オゾン</strong>は、高さ 25 km 付近に層があり、光を散らさず吸収します。朝夕の空の青みの基になります。

**地球の半径は 6360 km、大気の上端は 6460 km**（高さ 100 km）です。

係数は 3 種類あります。<strong>散乱係数 σs</strong>は、単位長さあたり散らされる割合で、RGB で値が違います。<strong>吸収係数 σa</strong>は、単位長さあたり吸われる割合です。<strong>消散係数 σt = σs + σa</strong>は、減る割合の合計です。

具体的な値として、Hillaire の実装で使われる地表（高さ 0）での値（単位は 1/km）を挙げます。レイリー散乱は (5.802, 13.558, 33.1) × 10⁻³ で、青が赤の約 5.7 倍と、先ほどの波長の比に対応します。ミー散乱は 3.996 × 10⁻³、ミー消散は 4.44 × 10⁻³ （吸収が少し含まれる）です。オゾン吸収は (0.650, 1.881, 0.085) × 10⁻³ で、緑の吸収が最も強く、これが夕方の空に紫や青みを足します。

これらの値に、高さごとの密度 ρ(h) = exp(−h / H) を掛けると、その高さでの係数になります。ミーとレイリーは指数関数的に薄くなりますが、オゾンは高さ 25 km を中心とした三角形状の分布で近似します。

<strong>レイリー散乱係数（海面）</strong> は、**RGB で (5.8, 13.5, 33.1) × 10⁻⁶ /m** 程度（**青が大きい**）、**ミー散乱は (3.9, 3.9, 3.9) × 10⁻⁶ /m** 程度です。

## よくあるミス

??? failure "夕焼けが、赤くならない"
    **オゾンの吸収**と **波長ごとの散乱係数**を**入れる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **高さごとの密度と、波長ごとの係数**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Transmittance](transmittance.md)
