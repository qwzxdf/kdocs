---
title: Thickness and Color
tags:
  - 描画
---

# Thickness and Color

<strong>色付きのガラスや水は光が通る距離（厚み）が長いほど、色が濃くなります</strong>。これがビア＝ランバートの法則で、吸収を指数で表します。このページでは厚みの求め方と、色の付け方を説明します。

!!! tip "ポイント"
    - 透過率 ＝ exp(−吸収係数 × 厚み)。
    - 厚み ＝ 裏面の深度 − 表面の深度で求める。
    - 色ごとに吸収係数を変えると、色付きになる。
    - 厚みが一定でも見た目を作れる（簡易版）。

!!! info "このページを読む前に"
    - [Refraction](index.md)（このセクション全体の地図と、読む順番）

<!-- fig:beer-thickness:begin -->

<svg class="fig illust motion" data-fig="beer-thickness" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-beer-thickness" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">色つきガラス: 光が通る厚さに応じて、色ごとに光が減る(ベールの法則)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">緑がかったガラスは、赤と青を多く吸う。厚い所ほど、緑が濃く、暗くなる</text>
<text x="60.0" y="110" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">くさび形のガラス(左 = 薄い 0、右 = 厚い 4)</text>
<rect x="60.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#f7fdf9"/></rect>
<rect x="80.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#e5e7eb;#e9faee"/></rect>
<rect x="100.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#dbf7e4"/></rect>
<rect x="120.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#e5e7eb;#cff5da"/></rect>
<rect x="140.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#e5e7eb;#c3f2d0"/></rect>
<rect x="160.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#b7efc7"/></rect>
<rect x="180.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#e5e7eb;#adecbe"/></rect>
<rect x="200.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#e5e7eb;#a3e9b6"/></rect>
<rect x="220.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#e5e7eb;#99e6ae"/></rect>
<rect x="240.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#90e4a6"/></rect>
<rect x="260.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#e5e7eb;#88e19f"/></rect>
<rect x="280.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#e5e7eb;#80de98"/></rect>
<rect x="300.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1367" values="#e5e7eb;#78db91"/></rect>
<rect x="320.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1423" values="#e5e7eb;#71d98b"/></rect>
<rect x="340.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1479" values="#e5e7eb;#6bd685"/></rect>
<rect x="360.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1535" values="#e5e7eb;#65d47f"/></rect>
<rect x="380.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1591" values="#e5e7eb;#5fd179"/></rect>
<rect x="400.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1647" values="#e5e7eb;#59cf74"/></rect>
<rect x="420.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1702" values="#e5e7eb;#54cc6f"/></rect>
<rect x="440.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1758" values="#e5e7eb;#4fca6a"/></rect>
<rect x="460.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1814" values="#e5e7eb;#4bc765"/></rect>
<rect x="480.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1870" values="#e5e7eb;#46c561"/></rect>
<rect x="500.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1926" values="#e5e7eb;#42c35d"/></rect>
<rect x="520.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1981" values="#e5e7eb;#3ec059"/></rect>
<rect x="540.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2037" values="#e5e7eb;#3bbe55"/></rect>
<rect x="560.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2093" values="#e5e7eb;#37bc51"/></rect>
<rect x="580.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2149" values="#e5e7eb;#34ba4d"/></rect>
<rect x="600.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2205" values="#e5e7eb;#31b74a"/></rect>
<rect x="620.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2260" values="#e5e7eb;#2eb547"/></rect>
<rect x="640.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2316" values="#e5e7eb;#2bb344"/></rect>
<rect x="660.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2372" values="#e5e7eb;#29b141"/></rect>
<rect x="680.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2428" values="#e5e7eb;#27af3e"/></rect>
<rect x="700.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2484" values="#e5e7eb;#24ad3b"/></rect>
<rect x="720.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2540" values="#e5e7eb;#22ab38"/></rect>
<rect x="740.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2595" values="#e5e7eb;#20a936"/></rect>
<rect x="760.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2651" values="#e5e7eb;#1ea734"/></rect>
<rect x="780.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2707" values="#e5e7eb;#1da531"/></rect>
<rect x="800.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2763" values="#e5e7eb;#1ba32f"/></rect>
<rect x="820.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2819" values="#e5e7eb;#19a12d"/></rect>
<rect x="840.0" y="120.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2874" values="#e5e7eb;#189f2b"/></rect>
<rect x="60.0" y="120" width="800.0" height="20.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="40.0" y="168" width="840.0" height="130" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="40.0" y="158" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">色ごとに通る光の割合(厚さ → 光)</text>
<path d="M60.0,184.0 L73.33,187.76 L86.67,191.38 L100.0,194.86 L113.33,198.19 L126.67,201.4 L140.0,204.48 L153.33,207.44 L166.67,210.29 L180.0,213.02 L193.33,215.65 L206.67,218.17 L220.0,220.6 L233.33,222.93 L246.67,225.16 L260.0,227.31 L273.33,229.38 L286.67,231.36 L300.0,233.27 L313.33,235.1 L326.67,236.86 L340.0,238.56 L353.33,240.18 L366.67,241.74 L380.0,243.24 L393.33,244.68 L406.67,246.07 L420.0,247.4 L433.33,248.68 L446.67,249.91 L460.0,251.09 L473.33,252.22 L486.67,253.31 L500.0,254.36 L513.33,255.36 L526.67,256.33 L540.0,257.25 L553.33,258.15 L566.67,259.0 L580.0,259.83 L593.33,260.62 L606.67,261.38 L620.0,262.11 L633.33,262.81 L646.67,263.48 L660.0,264.13 L673.33,264.75 L686.67,265.35 L700.0,265.93 L713.33,266.48 L726.67,267.01 L740.0,267.52 L753.33,268.01 L766.67,268.48 L780.0,268.93 L793.33,269.36 L806.67,269.78 L820.0,270.18 L833.33,270.57 L846.67,270.94 L860.0,271.29" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3068;0.3070;1.0000" values="0;0;1;1"/></path>
<text x="852.0" y="265.2910764842164" text-anchor="end" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="0">R<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3068;0.3070;1.0000" values="0;0;1;1"/></text>
<path d="M60.0,184.0 L73.33,184.76 L86.67,185.52 L100.0,186.28 L113.33,187.02 L126.67,187.76 L140.0,188.5 L153.33,189.23 L166.67,189.95 L180.0,190.67 L193.33,191.38 L206.67,192.09 L220.0,192.79 L233.33,193.48 L246.67,194.17 L260.0,194.86 L273.33,195.53 L286.67,196.21 L300.0,196.87 L313.33,197.54 L326.67,198.19 L340.0,198.85 L353.33,199.49 L366.67,200.13 L380.0,200.77 L393.33,201.4 L406.67,202.03 L420.0,202.65 L433.33,203.27 L446.67,203.88 L460.0,204.48 L473.33,205.09 L486.67,205.68 L500.0,206.27 L513.33,206.86 L526.67,207.44 L540.0,208.02 L553.33,208.6 L566.67,209.17 L580.0,209.73 L593.33,210.29 L606.67,210.85 L620.0,211.4 L633.33,211.94 L646.67,212.49 L660.0,213.02 L673.33,213.56 L686.67,214.09 L700.0,214.61 L713.33,215.13 L726.67,215.65 L740.0,216.16 L753.33,216.67 L766.67,217.18 L780.0,217.68 L793.33,218.17 L806.67,218.67 L820.0,219.15 L833.33,219.64 L846.67,220.12 L860.0,220.6" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3393;0.3395;1.0000" values="0;0;1;1"/></path>
<text x="852.0" y="214.5967943866105" text-anchor="end" style="font-size:13px;font-weight:700;fill:#2ea043" opacity="0">G<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3393;0.3395;1.0000" values="0;0;1;1"/></text>
<path d="M60.0,184.0 L73.33,186.84 L86.67,189.59 L100.0,192.26 L113.33,194.86 L126.67,197.37 L140.0,199.81 L153.33,202.18 L166.67,204.48 L180.0,206.72 L193.33,208.88 L206.67,210.98 L220.0,213.02 L233.33,215.0 L246.67,216.92 L260.0,218.79 L273.33,220.6 L286.67,222.35 L300.0,224.06 L313.33,225.71 L326.67,227.31 L340.0,228.87 L353.33,230.38 L366.67,231.85 L380.0,233.27 L393.33,234.65 L406.67,235.99 L420.0,237.29 L433.33,238.56 L446.67,239.78 L460.0,240.97 L473.33,242.12 L486.67,243.24 L500.0,244.33 L513.33,245.38 L526.67,246.41 L540.0,247.4 L553.33,248.36 L566.67,249.3 L580.0,250.2 L593.33,251.09 L606.67,251.94 L620.0,252.77 L633.33,253.57 L646.67,254.36 L660.0,255.11 L673.33,255.85 L686.67,256.56 L700.0,257.25 L713.33,257.93 L726.67,258.58 L740.0,259.21 L753.33,259.83 L766.67,260.42 L780.0,261.0 L793.33,261.56 L806.67,262.11 L820.0,262.64 L833.33,263.15 L846.67,263.65 L860.0,264.13" fill="none" stroke="#2563eb" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3719;0.3721;1.0000" values="0;0;1;1"/></path>
<text x="852.0" y="258.1313067307277" text-anchor="end" style="font-size:13px;font-weight:700;fill:#2563eb" opacity="0">B<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3719;0.3721;1.0000" values="0;0;1;1"/></text>
<text x="40" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">ガラスの球(中心ほど厚い)を正面から見る</text>
<rect x="60.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="68.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="76.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="84.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="92.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="100.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="108.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#ffffff;#baefc9"/></rect>
<rect x="116.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4179" values="#ffffff;#99e6ae"/></rect>
<rect x="124.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4184" values="#ffffff;#8ee3a5"/></rect>
<rect x="132.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4190" values="#ffffff;#8ee3a5"/></rect>
<rect x="140.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4195" values="#ffffff;#99e6ae"/></rect>
<rect x="148.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4201" values="#ffffff;#baefc9"/></rect>
<rect x="156.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="164.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="172.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="180.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="188.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="196.0" y="338.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="60.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="68.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="76.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="84.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="92.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4167" values="#ffffff;#a7eaba"/></rect>
<rect x="100.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#ffffff;#7edd96"/></rect>
<rect x="108.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4179" values="#ffffff;#6cd786"/></rect>
<rect x="116.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4184" values="#ffffff;#63d37d"/></rect>
<rect x="124.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4190" values="#ffffff;#5fd179"/></rect>
<rect x="132.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4195" values="#ffffff;#5fd179"/></rect>
<rect x="140.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4201" values="#ffffff;#63d37d"/></rect>
<rect x="148.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4207" values="#ffffff;#6cd786"/></rect>
<rect x="156.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4212" values="#ffffff;#7edd96"/></rect>
<rect x="164.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4218" values="#ffffff;#a7eaba"/></rect>
<rect x="172.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="180.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="188.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="196.0" y="346.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="60.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="68.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="76.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="84.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4167" values="#ffffff;#8ee3a5"/></rect>
<rect x="92.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#ffffff;#6cd786"/></rect>
<rect x="100.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4179" values="#ffffff;#5bd076"/></rect>
<rect x="108.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4184" values="#ffffff;#52cb6c"/></rect>
<rect x="116.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4190" values="#ffffff;#4cc867"/></rect>
<rect x="124.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4195" values="#ffffff;#4ac765"/></rect>
<rect x="132.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4201" values="#ffffff;#4ac765"/></rect>
<rect x="140.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4207" values="#ffffff;#4cc867"/></rect>
<rect x="148.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4212" values="#ffffff;#52cb6c"/></rect>
<rect x="156.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4218" values="#ffffff;#5bd076"/></rect>
<rect x="164.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4223" values="#ffffff;#6cd786"/></rect>
<rect x="172.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4229" values="#ffffff;#8ee3a5"/></rect>
<rect x="180.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="188.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="196.0" y="354.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="60.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="68.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="76.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4167" values="#ffffff;#8ee3a5"/></rect>
<rect x="84.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#ffffff;#67d581"/></rect>
<rect x="92.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4179" values="#ffffff;#54cc6f"/></rect>
<rect x="100.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4184" values="#ffffff;#4ac765"/></rect>
<rect x="108.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4190" values="#ffffff;#43c35e"/></rect>
<rect x="116.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4195" values="#ffffff;#3fc15a"/></rect>
<rect x="124.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4201" values="#ffffff;#3ec058"/></rect>
<rect x="132.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4207" values="#ffffff;#3ec058"/></rect>
<rect x="140.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4212" values="#ffffff;#3fc15a"/></rect>
<rect x="148.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4218" values="#ffffff;#43c35e"/></rect>
<rect x="156.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4223" values="#ffffff;#4ac765"/></rect>
<rect x="164.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4229" values="#ffffff;#54cc6f"/></rect>
<rect x="172.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4234" values="#ffffff;#67d581"/></rect>
<rect x="180.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#ffffff;#8ee3a5"/></rect>
<rect x="188.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="196.0" y="362.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="60.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="68.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4167" values="#ffffff;#a7eaba"/></rect>
<rect x="76.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#ffffff;#6cd786"/></rect>
<rect x="84.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4179" values="#ffffff;#54cc6f"/></rect>
<rect x="92.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4184" values="#ffffff;#47c662"/></rect>
<rect x="100.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4190" values="#ffffff;#3fc15a"/></rect>
<rect x="108.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4195" values="#ffffff;#3abe54"/></rect>
<rect x="116.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4201" values="#ffffff;#37bc51"/></rect>
<rect x="124.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4207" values="#ffffff;#36bb4f"/></rect>
<rect x="132.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4212" values="#ffffff;#36bb4f"/></rect>
<rect x="140.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4218" values="#ffffff;#37bc51"/></rect>
<rect x="148.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4223" values="#ffffff;#3abe54"/></rect>
<rect x="156.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4229" values="#ffffff;#3fc15a"/></rect>
<rect x="164.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4234" values="#ffffff;#47c662"/></rect>
<rect x="172.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#ffffff;#54cc6f"/></rect>
<rect x="180.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4246" values="#ffffff;#6cd786"/></rect>
<rect x="188.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4251" values="#ffffff;#a7eaba"/></rect>
<rect x="196.0" y="370.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="60.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="68.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#ffffff;#7edd96"/></rect>
<rect x="76.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4179" values="#ffffff;#5bd076"/></rect>
<rect x="84.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4184" values="#ffffff;#4ac765"/></rect>
<rect x="92.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4190" values="#ffffff;#3fc15a"/></rect>
<rect x="100.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4195" values="#ffffff;#39bd53"/></rect>
<rect x="108.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4201" values="#ffffff;#34ba4e"/></rect>
<rect x="116.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4207" values="#ffffff;#32b84b"/></rect>
<rect x="124.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4212" values="#ffffff;#31b74a"/></rect>
<rect x="132.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4218" values="#ffffff;#31b74a"/></rect>
<rect x="140.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4223" values="#ffffff;#32b84b"/></rect>
<rect x="148.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4229" values="#ffffff;#34ba4e"/></rect>
<rect x="156.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4234" values="#ffffff;#39bd53"/></rect>
<rect x="164.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#ffffff;#3fc15a"/></rect>
<rect x="172.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4246" values="#ffffff;#4ac765"/></rect>
<rect x="180.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4251" values="#ffffff;#5bd076"/></rect>
<rect x="188.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="#ffffff;#7edd96"/></rect>
<rect x="196.0" y="378.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="60.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4173" values="#ffffff;#baefc9"/></rect>
<rect x="68.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4179" values="#ffffff;#6cd786"/></rect>
<rect x="76.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4184" values="#ffffff;#52cb6c"/></rect>
<rect x="84.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4190" values="#ffffff;#43c35e"/></rect>
<rect x="92.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4195" values="#ffffff;#3abe54"/></rect>
<rect x="100.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4201" values="#ffffff;#34ba4e"/></rect>
<rect x="108.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4207" values="#ffffff;#31b74a"/></rect>
<rect x="116.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4212" values="#ffffff;#2eb547"/></rect>
<rect x="124.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4218" values="#ffffff;#2db546"/></rect>
<rect x="132.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4223" values="#ffffff;#2db546"/></rect>
<rect x="140.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4229" values="#ffffff;#2eb547"/></rect>
<rect x="148.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4234" values="#ffffff;#31b74a"/></rect>
<rect x="156.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#ffffff;#34ba4e"/></rect>
<rect x="164.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4246" values="#ffffff;#3abe54"/></rect>
<rect x="172.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4251" values="#ffffff;#43c35e"/></rect>
<rect x="180.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="#ffffff;#52cb6c"/></rect>
<rect x="188.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4262" values="#ffffff;#6cd786"/></rect>
<rect x="196.0" y="386.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4268" values="#ffffff;#baefc9"/></rect>
<rect x="60.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4179" values="#ffffff;#99e6ae"/></rect>
<rect x="68.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4184" values="#ffffff;#63d37d"/></rect>
<rect x="76.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4190" values="#ffffff;#4cc867"/></rect>
<rect x="84.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4195" values="#ffffff;#3fc15a"/></rect>
<rect x="92.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4201" values="#ffffff;#37bc51"/></rect>
<rect x="100.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4207" values="#ffffff;#32b84b"/></rect>
<rect x="108.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4212" values="#ffffff;#2eb547"/></rect>
<rect x="116.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4218" values="#ffffff;#2cb445"/></rect>
<rect x="124.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4223" values="#ffffff;#2bb344"/></rect>
<rect x="132.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4229" values="#ffffff;#2bb344"/></rect>
<rect x="140.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4234" values="#ffffff;#2cb445"/></rect>
<rect x="148.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#ffffff;#2eb547"/></rect>
<rect x="156.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4246" values="#ffffff;#32b84b"/></rect>
<rect x="164.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4251" values="#ffffff;#37bc51"/></rect>
<rect x="172.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="#ffffff;#3fc15a"/></rect>
<rect x="180.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4262" values="#ffffff;#4cc867"/></rect>
<rect x="188.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4268" values="#ffffff;#63d37d"/></rect>
<rect x="196.0" y="394.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4273" values="#ffffff;#99e6ae"/></rect>
<rect x="60.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4184" values="#ffffff;#8ee3a5"/></rect>
<rect x="68.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4190" values="#ffffff;#5fd179"/></rect>
<rect x="76.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4195" values="#ffffff;#4ac765"/></rect>
<rect x="84.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4201" values="#ffffff;#3ec058"/></rect>
<rect x="92.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4207" values="#ffffff;#36bb4f"/></rect>
<rect x="100.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4212" values="#ffffff;#31b74a"/></rect>
<rect x="108.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4218" values="#ffffff;#2db546"/></rect>
<rect x="116.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4223" values="#ffffff;#2bb344"/></rect>
<rect x="124.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4229" values="#ffffff;#2ab242"/></rect>
<rect x="132.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4234" values="#ffffff;#2ab242"/></rect>
<rect x="140.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#ffffff;#2bb344"/></rect>
<rect x="148.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4246" values="#ffffff;#2db546"/></rect>
<rect x="156.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4251" values="#ffffff;#31b74a"/></rect>
<rect x="164.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="#ffffff;#36bb4f"/></rect>
<rect x="172.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4262" values="#ffffff;#3ec058"/></rect>
<rect x="180.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4268" values="#ffffff;#4ac765"/></rect>
<rect x="188.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4273" values="#ffffff;#5fd179"/></rect>
<rect x="196.0" y="402.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4279" values="#ffffff;#8ee3a5"/></rect>
<rect x="60.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4190" values="#ffffff;#8ee3a5"/></rect>
<rect x="68.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4195" values="#ffffff;#5fd179"/></rect>
<rect x="76.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4201" values="#ffffff;#4ac765"/></rect>
<rect x="84.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4207" values="#ffffff;#3ec058"/></rect>
<rect x="92.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4212" values="#ffffff;#36bb4f"/></rect>
<rect x="100.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4218" values="#ffffff;#31b74a"/></rect>
<rect x="108.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4223" values="#ffffff;#2db546"/></rect>
<rect x="116.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4229" values="#ffffff;#2bb344"/></rect>
<rect x="124.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4234" values="#ffffff;#2ab242"/></rect>
<rect x="132.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#ffffff;#2ab242"/></rect>
<rect x="140.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4246" values="#ffffff;#2bb344"/></rect>
<rect x="148.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4251" values="#ffffff;#2db546"/></rect>
<rect x="156.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="#ffffff;#31b74a"/></rect>
<rect x="164.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4262" values="#ffffff;#36bb4f"/></rect>
<rect x="172.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4268" values="#ffffff;#3ec058"/></rect>
<rect x="180.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4273" values="#ffffff;#4ac765"/></rect>
<rect x="188.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4279" values="#ffffff;#5fd179"/></rect>
<rect x="196.0" y="410.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4285" values="#ffffff;#8ee3a5"/></rect>
<rect x="60.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4195" values="#ffffff;#99e6ae"/></rect>
<rect x="68.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4201" values="#ffffff;#63d37d"/></rect>
<rect x="76.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4207" values="#ffffff;#4cc867"/></rect>
<rect x="84.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4212" values="#ffffff;#3fc15a"/></rect>
<rect x="92.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4218" values="#ffffff;#37bc51"/></rect>
<rect x="100.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4223" values="#ffffff;#32b84b"/></rect>
<rect x="108.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4229" values="#ffffff;#2eb547"/></rect>
<rect x="116.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4234" values="#ffffff;#2cb445"/></rect>
<rect x="124.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#ffffff;#2bb344"/></rect>
<rect x="132.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4246" values="#ffffff;#2bb344"/></rect>
<rect x="140.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4251" values="#ffffff;#2cb445"/></rect>
<rect x="148.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="#ffffff;#2eb547"/></rect>
<rect x="156.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4262" values="#ffffff;#32b84b"/></rect>
<rect x="164.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4268" values="#ffffff;#37bc51"/></rect>
<rect x="172.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4273" values="#ffffff;#3fc15a"/></rect>
<rect x="180.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4279" values="#ffffff;#4cc867"/></rect>
<rect x="188.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4285" values="#ffffff;#63d37d"/></rect>
<rect x="196.0" y="418.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4290" values="#ffffff;#99e6ae"/></rect>
<rect x="60.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4201" values="#ffffff;#baefc9"/></rect>
<rect x="68.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4207" values="#ffffff;#6cd786"/></rect>
<rect x="76.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4212" values="#ffffff;#52cb6c"/></rect>
<rect x="84.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4218" values="#ffffff;#43c35e"/></rect>
<rect x="92.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4223" values="#ffffff;#3abe54"/></rect>
<rect x="100.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4229" values="#ffffff;#34ba4e"/></rect>
<rect x="108.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4234" values="#ffffff;#31b74a"/></rect>
<rect x="116.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#ffffff;#2eb547"/></rect>
<rect x="124.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4246" values="#ffffff;#2db546"/></rect>
<rect x="132.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4251" values="#ffffff;#2db546"/></rect>
<rect x="140.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="#ffffff;#2eb547"/></rect>
<rect x="148.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4262" values="#ffffff;#31b74a"/></rect>
<rect x="156.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4268" values="#ffffff;#34ba4e"/></rect>
<rect x="164.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4273" values="#ffffff;#3abe54"/></rect>
<rect x="172.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4279" values="#ffffff;#43c35e"/></rect>
<rect x="180.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4285" values="#ffffff;#52cb6c"/></rect>
<rect x="188.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4290" values="#ffffff;#6cd786"/></rect>
<rect x="196.0" y="426.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296" values="#ffffff;#baefc9"/></rect>
<rect x="60.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="68.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4212" values="#ffffff;#7edd96"/></rect>
<rect x="76.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4218" values="#ffffff;#5bd076"/></rect>
<rect x="84.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4223" values="#ffffff;#4ac765"/></rect>
<rect x="92.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4229" values="#ffffff;#3fc15a"/></rect>
<rect x="100.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4234" values="#ffffff;#39bd53"/></rect>
<rect x="108.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#ffffff;#34ba4e"/></rect>
<rect x="116.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4246" values="#ffffff;#32b84b"/></rect>
<rect x="124.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4251" values="#ffffff;#31b74a"/></rect>
<rect x="132.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="#ffffff;#31b74a"/></rect>
<rect x="140.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4262" values="#ffffff;#32b84b"/></rect>
<rect x="148.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4268" values="#ffffff;#34ba4e"/></rect>
<rect x="156.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4273" values="#ffffff;#39bd53"/></rect>
<rect x="164.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4279" values="#ffffff;#3fc15a"/></rect>
<rect x="172.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4285" values="#ffffff;#4ac765"/></rect>
<rect x="180.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4290" values="#ffffff;#5bd076"/></rect>
<rect x="188.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296" values="#ffffff;#7edd96"/></rect>
<rect x="196.0" y="434.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="60.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="68.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4218" values="#ffffff;#a7eaba"/></rect>
<rect x="76.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4223" values="#ffffff;#6cd786"/></rect>
<rect x="84.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4229" values="#ffffff;#54cc6f"/></rect>
<rect x="92.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4234" values="#ffffff;#47c662"/></rect>
<rect x="100.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#ffffff;#3fc15a"/></rect>
<rect x="108.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4246" values="#ffffff;#3abe54"/></rect>
<rect x="116.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4251" values="#ffffff;#37bc51"/></rect>
<rect x="124.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="#ffffff;#36bb4f"/></rect>
<rect x="132.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4262" values="#ffffff;#36bb4f"/></rect>
<rect x="140.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4268" values="#ffffff;#37bc51"/></rect>
<rect x="148.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4273" values="#ffffff;#3abe54"/></rect>
<rect x="156.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4279" values="#ffffff;#3fc15a"/></rect>
<rect x="164.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4285" values="#ffffff;#47c662"/></rect>
<rect x="172.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4290" values="#ffffff;#54cc6f"/></rect>
<rect x="180.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296" values="#ffffff;#6cd786"/></rect>
<rect x="188.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4301" values="#ffffff;#a7eaba"/></rect>
<rect x="196.0" y="442.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="60.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="68.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="76.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4229" values="#ffffff;#8ee3a5"/></rect>
<rect x="84.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4234" values="#ffffff;#67d581"/></rect>
<rect x="92.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#ffffff;#54cc6f"/></rect>
<rect x="100.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4246" values="#ffffff;#4ac765"/></rect>
<rect x="108.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4251" values="#ffffff;#43c35e"/></rect>
<rect x="116.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="#ffffff;#3fc15a"/></rect>
<rect x="124.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4262" values="#ffffff;#3ec058"/></rect>
<rect x="132.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4268" values="#ffffff;#3ec058"/></rect>
<rect x="140.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4273" values="#ffffff;#3fc15a"/></rect>
<rect x="148.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4279" values="#ffffff;#43c35e"/></rect>
<rect x="156.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4285" values="#ffffff;#4ac765"/></rect>
<rect x="164.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4290" values="#ffffff;#54cc6f"/></rect>
<rect x="172.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296" values="#ffffff;#67d581"/></rect>
<rect x="180.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4301" values="#ffffff;#8ee3a5"/></rect>
<rect x="188.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="196.0" y="450.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="60.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="68.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="76.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="84.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4240" values="#ffffff;#8ee3a5"/></rect>
<rect x="92.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4246" values="#ffffff;#6cd786"/></rect>
<rect x="100.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4251" values="#ffffff;#5bd076"/></rect>
<rect x="108.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="#ffffff;#52cb6c"/></rect>
<rect x="116.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4262" values="#ffffff;#4cc867"/></rect>
<rect x="124.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4268" values="#ffffff;#4ac765"/></rect>
<rect x="132.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4273" values="#ffffff;#4ac765"/></rect>
<rect x="140.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4279" values="#ffffff;#4cc867"/></rect>
<rect x="148.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4285" values="#ffffff;#52cb6c"/></rect>
<rect x="156.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4290" values="#ffffff;#5bd076"/></rect>
<rect x="164.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296" values="#ffffff;#6cd786"/></rect>
<rect x="172.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4301" values="#ffffff;#8ee3a5"/></rect>
<rect x="180.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="188.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="196.0" y="458.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="60.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="68.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="76.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="84.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="92.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4251" values="#ffffff;#a7eaba"/></rect>
<rect x="100.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="#ffffff;#7edd96"/></rect>
<rect x="108.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4262" values="#ffffff;#6cd786"/></rect>
<rect x="116.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4268" values="#ffffff;#63d37d"/></rect>
<rect x="124.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4273" values="#ffffff;#5fd179"/></rect>
<rect x="132.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4279" values="#ffffff;#5fd179"/></rect>
<rect x="140.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4285" values="#ffffff;#63d37d"/></rect>
<rect x="148.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4290" values="#ffffff;#6cd786"/></rect>
<rect x="156.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296" values="#ffffff;#7edd96"/></rect>
<rect x="164.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4301" values="#ffffff;#a7eaba"/></rect>
<rect x="172.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="180.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="188.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="196.0" y="466.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="60.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="68.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="76.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="84.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="92.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="100.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="108.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4268" values="#ffffff;#baefc9"/></rect>
<rect x="116.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4273" values="#ffffff;#99e6ae"/></rect>
<rect x="124.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4279" values="#ffffff;#8ee3a5"/></rect>
<rect x="132.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4285" values="#ffffff;#8ee3a5"/></rect>
<rect x="140.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4290" values="#ffffff;#99e6ae"/></rect>
<rect x="148.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296" values="#ffffff;#baefc9"/></rect>
<rect x="156.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="164.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="172.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="180.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="188.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"/>
<rect x="196.0" y="474.0" width="8.3" height="8.3" fill="#ffffff"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4835;0.4837;1.0000" values="0;0;1;1"/><rect x="260" y="338" width="670" height="130" rx="12" fill="#f0fdf4" stroke="#2ea043" stroke-width="2.5"/>
<text x="276" y="362" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">薄い所(厚さ 0.5): R 74% / G 94% / B 80% → ほぼ透明</text>
<text x="276" y="385" text-anchor="start" style="font-size:14px;font-weight:700;fill:#166534">球の中心(厚さ 3.0): R 17% / G 70% / B 26% → 濃い緑</text>
<text x="276" y="408" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">色ごとの係数 σ が違うので、厚さによって「色合い」が変わる</text>
<text x="276" y="430" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">(薄くて青白い → 厚くて濃い緑)。厚さ = 表と裏の深度の差で、画素ごとに求める</text>
</g>
<text x="260" y="500" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">計算した画素:</text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4138;0.4140;1.0000" values="1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4138;0.4140;0.4143;0.4145;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4143;0.4145;0.4149;0.4151;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4149;0.4151;0.4154;0.4156;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4154;0.4156;0.4160;0.4162;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4160;0.4162;0.4166;0.4167;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4166;0.4167;0.4171;0.4173;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">11<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4171;0.4173;0.4177;0.4179;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">19<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4177;0.4179;0.4182;0.4184;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">28<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4182;0.4184;0.4188;0.4190;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">38<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4188;0.4190;0.4193;0.4195;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">49<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4193;0.4195;0.4199;0.4201;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">61<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4199;0.4201;0.4205;0.4207;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">72<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4205;0.4207;0.4210;0.4212;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">84<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4210;0.4212;0.4216;0.4218;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">97<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4216;0.4218;0.4221;0.4223;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">109<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4221;0.4223;0.4227;0.4229;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">122<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4227;0.4229;0.4233;0.4234;1.0000" values="0;0;1;1;0;0"/></text>
<text x="380" y="504" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">134<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4233;0.4234;1.0000" values="0;0;1;1"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">色つきのガラスは、光が通る距離が長いほど、色が濃くなる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">厚さ 0 → 4 で、色ごとの光の減り方が変わる(緑は減りにくい)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.4091;0.4093;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">球では、中心ほど厚いので、中心が濃い緑、ふちは薄く透明になる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4138;0.4140;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:beer-thickness:end -->

## 厚みと色（ビア＝ランバートの法則）
<strong>色付きガラスや水は厚いほど、光が吸収されて色が濃く</strong>なります。

<div class="formula">T = exp(−σ · d)　（T：透過率、σ：吸収係数（RGB）、d：厚み）</div>

記号の意味です。σ（シグマ）は単位長さあたりの吸収で、色ごとに違います。水は赤を強く吸収します（σ_r が大きい）。d は光が媒質の中を進む距離（厚み）です。T は透過する光の割合（RGB）です。この式は Beer-Lambert の法則です。

```hlsl
float3 absorption = float3(0.4, 0.1, 0.05);
float3 transmittance = exp(-absorption * thickness);
float3 tinted_background = background * transmittance;
```

コードの要点です。`absorption` は吸収係数（RGB）で水なら赤を強く、青を弱く吸収して青緑に見えます。`thickness` は厚みでガラスならほぼ一定、水なら水深（深度差）です。`exp(-σd)` により厚いほど急に暗く濃くなります。

水深（水面から底までの距離）は、不透明の深度と水面の深度の差から求められます（[Water](../../water/index.md)）。

## 色付きガラスは厚いほど濃い

色付きのガラス（緑のボトル、青い氷）は <strong>光がガラスの中を通る距離が長いほど濃く</strong>見えます。光が ガラスに吸収されるためで、水の中の光と同じ原理です（[Color by Water Depth](../../water/shading/depth-color.md)）。

```text
透過率 T = exp( −σ × 厚み )          σ: 吸収係数（RGB ごと）
```

| 厚み | 緑のガラス（赤と青を吸収） |
| --- | --- |
| 薄い（縁のとがった所） | ほぼ透明 |
| 中くらい | 薄い緑 |
| 厚い（底、中心） | 濃い緑 |

厚みが場所で違うことが ガラスの、立体感を作ります（コップの底が濃い、ボトルの肩の薄い所が明るい）。

## 厚みを求める

### ① 解析的な形（球、箱）

形が単純なら <strong>視線が物体を通る長さ</strong>を数式で、求められます。

```hlsl
// 球: 視線（原点 ro、方向 rd）が中心 c、半径 r の球を通り抜ける長さ。
float SphereThickness(float3 ro, float3 rd, float3 c, float r) {
  float3 oc = ro - c;
  float b = dot(oc, rd);
  float h = b * b - (dot(oc, oc) - r * r);
  if (h < 0.0) return 0.0;                       // 当たらない
  return 2.0 * sqrt(h);                           // 入口と出口の距離
}
```

### ② 手前と奥の深度の差

任意の形では 物体の背面の深度と、前面の深度の差がその画素での、厚みです。背面を先に描いて深度を別のテクスチャに保存し、前面を描くときに読みます。

```text
① 背面だけを描く（表面をカリング）→ 背面の深度を、テクスチャに保存
② 前面を描く → 前面の深度と、保存した背面の深度の、差が、厚み
```

```hlsl
Texture2D<float> g_back_depth : register(t2);          // 背面の深度（視点深度）

float4 main(PSInput input) : SV_Target {
  float front = LinearizeDepth(input.position.z);
  float back = LinearizeDepth(g_back_depth.Load(int3(input.position.xy, 0)));
  float thickness = max(back - front, 0.0);
  // 視線方向の距離にする（視点深度の差は、カメラの前方向に沿っているので、cos で割る）
  thickness /= max(dot(normalize(input.world_position - g_camera_position), g_camera_forward), 0.1);

  float3 T = exp(-g_absorption * thickness);            // 色ごとの透過率
  float3 refracted = SampleBackground(...) * T;
  ...
}
```

### ③ 厚みをテクスチャに焼く

物体ごとの厚みの分布を事前に、テクスチャ（厚みマップ）に焼いておく方法です。物体の内側から外へレイを飛ばして厚みを求め、UV に焼きます（ツールで事前計算）。実行時はテクスチャを読むだけで、安いです。視線の向きによらない（近似）ので、簡易です。

| 方法 | 正確さ | コスト | 向き |
| --- | --- | --- | --- |
| 解析的 | 完全 | 最小 | 球、箱、円柱 |
| 背面の深度 | 視線に正しい | 追加のパス（背面を描く） | 任意の、凸な形 |
| 厚みマップ | 視線に依存しない（近似） | 最小 | 複雑な、静止物（彫像、瓶） |

背面の深度を使う方法は 凸な形（瓶、球）で正確です。凹んだ形（ドーナツ、コップ）では視線が物体を 2 回以上通るので、不正確になります。

## 色の付け方

### 吸収係数 σ を色から作る

「<strong>1 m の厚さでこの色になる</strong>」と、アーティストが色を指定しそこから `σ` を逆算します。

```text
T(1m) = exp(−σ)   →   σ = −ln( T(1m) )
```

```hlsl
// 「1 メートル通ったあとの色」から、吸収係数を作る。
float3 AbsorptionFromColor(float3 color_at_1m) {
  return -log(max(color_at_1m, 0.001));
}
// 例: 緑のガラス（赤と青を吸収）
float3 sigma = AbsorptionFromColor(float3(0.2, 0.8, 0.3));
```

ガラスは薄い（数 mm〜数 cm）ので `color_at_1m` をそのまま使うとほとんど色が付きません。厚みのスケール（`thickness × scale`）を調整するか、「厚み 1 cm の色」を基準にします。

### 表面の色と内部の色

| 色 | 原因 | 表現 |
| --- | --- | --- |
| 内部の吸収 | 光がガラスの中を通る間に吸収される | `exp(−σ × 厚み)`（このページ） |
| 表面の反射 | 表面の反射。色が付かない（ガラスは反射が白い）。金属は反射に色が付く | フレネル（[Fresnel](fresnel.md)）。白い反射 |
| 内部の散乱 | すりガラス、乳白色、氷の気泡 | 屈折をぼかし散乱の色を足す |

## 濁り（散乱）

すりガラス、氷、乳白色のガラスは <strong>内部の散乱</strong>で、背景がぼやけます。

```hlsl
// 厚みに応じて、背景をぼかす（粗さを厚みで増やす）。
float lod = saturate(thickness / g_scatter_distance) * kMaxMip;
float3 background = g_scene_copy_blurred.SampleLevel(g_linear_clamp, refract_uv, lod).rgb;
// 散乱の色（白っぽい）を厚みに応じて、足す
float scatter = 1.0 - exp(-thickness * g_scatter_coeff);
float3 color = lerp(background * T, g_scatter_color, scatter);
```

厚みが増えるほど 背景がぼやけ、散乱の色（白、乳白）に近づきます。

## よくあるミス

??? failure "厚いガラスも薄いガラスも、同じ色"
    <strong>厚みで濃さを変える</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 厚みが長いほど、色が濃い
    - [x] exp で吸収を表す

## 参考

- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（屈折、フレネル、透過の章）
- Hecht, "Optics", 5th Edition, Pearson, 2016（スネルの法則、フレネルの式、分散）
- Beer, "Bestimmung der Absorption des rothen Lichts in farbigen Flüssigkeiten", Annalen der Physik, 1852（吸収の法則）
- Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, 2005

## 関連ページ

- [Refraction](index.md)
- [Thin and Thick Glass](thin-thick.md)
- [Water Shading](../../water/shading/index.md)
