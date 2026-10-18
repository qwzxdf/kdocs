---
title: Physically Based Aerial Perspective
tags:
  - 描画
---

# Physically Based Aerial Perspective

**大気散乱の LUT（空気遠近法 LUT）を使うと、距離ごとの散乱と透過率を、物理的に正しく求められます**。**空と完全に一致する**のが**利点**です。このページでは、**物理に基づく空気遠近法**を説明します。

!!! tip "ポイント"
    - **カメラからの距離ごとの、散乱と透過率を LUT に**。
    - **空と同じ計算なので、色が一致**。
    - **時刻・天候が変わっても、自動で追従**。
    - **Hillaire 2020 の空気遠近法 LUT**。

## 物理に基づく空気遠近法
**大気散乱**（[Atmospheric Scattering](../scattering/index.md)）の**LUT** を**使うと**、**距離フォグを物理的に決められます**。<strong>Hillaire 2020 の「空気遠近法 LUT」</strong> は、**カメラ前方の froxel ごとの「散乱光」と「透過率」を保持**します。

```hlsl
float4 aerial = aerial_perspective_lut.SampleLevel(linear_clamp, float3(uv, depth_slice), 0);
float3 inscattered = aerial.rgb;
float transmittance = aerial.a;
float3 final_color = scene_color * transmittance + inscattered;
```

| 点 | 説明 |
| --- | --- |
| **`inscattered`** | **視線上で散乱して、カメラに入る光**（**霞の明るさと色**） |
| **`transmittance`** | **物の光が残る割合** |
| **深度スライス** | **深度をスライス番号に変換**（**非線形**）して**サンプル** |
| **利点** | **昼・夕・夜で自動的に色が変わる**。**太陽の方向も反映** |

<!-- fig:beer-rgb:begin -->

<svg class="fig illust motion" data-fig="beer-rgb" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-beer-rgb" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">空気遠近法: 青の光ほど散って減り、遠くの山は、青く霞んで、薄くなる(物の色 + 空気の色)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">同じ茶色の山が、距離 0.5〜48 km に並ぶ。色ごとに、減る割合と、空気が足す光(空の青)を計算して、1 つずつ見る</text>
<rect x="30" y="96" width="900" height="160" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 山の色(左 = 近い、右 = 遠い)</text>
<rect x="32" y="98" width="896" height="156" fill="#b1d2ff" fill-opacity="0.35"/>
<polygon points="50.0,240 89.0,150 128.0,240" fill="#e5e7eb" opacity="0"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="#e5e7eb;#e5e7eb;#b19582;#b19582"/><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="0;0;1;1"/></polygon>
<text x="89.0" y="252" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b" opacity="0">0.5 km<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="0;0;1;1"/></text>
<polygon points="128.0,240 167.0,150 206.0,240" fill="#e5e7eb" opacity="0"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0934;0.0936;1.0000" values="#e5e7eb;#e5e7eb;#b19688;#b19688"/><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0934;0.0936;1.0000" values="0;0;1;1"/></polygon>
<text x="167.0" y="252" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b" opacity="0">1 km<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0934;0.0936;1.0000" values="0;0;1;1"/></text>
<polygon points="206.0,240 245.0,150 284.0,240" fill="#e5e7eb" opacity="0"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1232;0.1234;1.0000" values="#e5e7eb;#e5e7eb;#b19893;#b19893"/><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1232;0.1234;1.0000" values="0;0;1;1"/></polygon>
<text x="245.0" y="252" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b" opacity="0">2 km<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1232;0.1234;1.0000" values="0;0;1;1"/></text>
<polygon points="284.0,240 323.0,150 362.0,240" fill="#e5e7eb" opacity="0"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1530;0.1532;1.0000" values="#e5e7eb;#e5e7eb;#b19ca5;#b19ca5"/><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1530;0.1532;1.0000" values="0;0;1;1"/></polygon>
<text x="323.0" y="252" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b" opacity="0">4 km<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1530;0.1532;1.0000" values="0;0;1;1"/></text>
<polygon points="362.0,240 401.0,150 440.0,240" fill="#e5e7eb" opacity="0"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1828;0.1830;1.0000" values="#e5e7eb;#e5e7eb;#b1a2be;#b1a2be"/><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1828;0.1830;1.0000" values="0;0;1;1"/></polygon>
<text x="401.0" y="252" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b" opacity="0">8 km<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1828;0.1830;1.0000" values="0;0;1;1"/></text>
<polygon points="440.0,240 479.0,150 518.0,240" fill="#e5e7eb" opacity="0"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2126;0.2128;1.0000" values="#e5e7eb;#e5e7eb;#b1a8cf;#b1a8cf"/><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2126;0.2128;1.0000" values="0;0;1;1"/></polygon>
<text x="479.0" y="252" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b" opacity="0">12 km<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2126;0.2128;1.0000" values="0;0;1;1"/></text>
<polygon points="518.0,240 557.0,150 596.0,240" fill="#e5e7eb" opacity="0"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2424;0.2426;1.0000" values="#e5e7eb;#e5e7eb;#b1afe0;#b1afe0"/><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2424;0.2426;1.0000" values="0;0;1;1"/></polygon>
<text x="557.0" y="252" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b" opacity="0">18 km<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2424;0.2426;1.0000" values="0;0;1;1"/></text>
<polygon points="596.0,240 635.0,150 674.0,240" fill="#e5e7eb" opacity="0"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2722;0.2723;1.0000" values="#e5e7eb;#e5e7eb;#b1b6ec;#b1b6ec"/><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2722;0.2723;1.0000" values="0;0;1;1"/></polygon>
<text x="635.0" y="252" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b" opacity="0">25 km<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2722;0.2723;1.0000" values="0;0;1;1"/></text>
<polygon points="674.0,240 713.0,150 752.0,240" fill="#e5e7eb" opacity="0"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3020;0.3021;1.0000" values="#e5e7eb;#e5e7eb;#b1bcf4;#b1bcf4"/><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3020;0.3021;1.0000" values="0;0;1;1"/></polygon>
<text x="713.0" y="252" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b" opacity="0">33 km<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3020;0.3021;1.0000" values="0;0;1;1"/></text>
<polygon points="752.0,240 791.0,150 830.0,240" fill="#e5e7eb" opacity="0"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;1.0000" values="#e5e7eb;#e5e7eb;#b1c0f8;#b1c0f8"/><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;1.0000" values="0;0;1;1"/></polygon>
<text x="791.0" y="252" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b" opacity="0">40 km<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;1.0000" values="0;0;1;1"/></text>
<polygon points="830.0,240 869.0,150 908.0,240" fill="#e5e7eb" opacity="0"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3615;0.3617;1.0000" values="#e5e7eb;#e5e7eb;#b1c4fb;#b1c4fb"/><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3615;0.3617;1.0000" values="0;0;1;1"/></polygon>
<text x="869.0" y="252" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b" opacity="0">48 km<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3615;0.3617;1.0000" values="0;0;1;1"/></text>
<rect x="30" y="276" width="440" height="190" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="266" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 色ごとに残る光 T = exp(−σ·距離)</text>
<path d="M60.0,316.0 L64.06,316.78 L68.12,317.55 L72.19,318.32 L76.25,319.08 L80.31,319.84 L84.38,320.6 L88.44,321.35 L92.5,322.09 L96.56,322.83 L100.62,323.57 L104.69,324.3 L108.75,325.03 L112.81,325.75 L116.88,326.47 L120.94,327.19 L125.0,327.9 L129.06,328.61 L133.12,329.31 L137.19,330.01 L141.25,330.7 L145.31,331.39 L149.38,332.08 L153.44,332.76 L157.5,333.43 L161.56,334.11 L165.62,334.78 L169.69,335.44 L173.75,336.1 L177.81,336.76 L181.88,337.41 L185.94,338.06 L190.0,338.71 L194.06,339.35 L198.12,339.99 L202.19,340.62 L206.25,341.25 L210.31,341.88 L214.38,342.5 L218.44,343.12 L222.5,343.74 L226.56,344.35 L230.62,344.96 L234.69,345.56 L238.75,346.16 L242.81,346.76 L246.88,347.35 L250.94,347.94 L255.0,348.53 L259.06,349.11 L263.12,349.69 L267.19,350.27 L271.25,350.84 L275.31,351.41 L279.38,351.98 L283.44,352.54 L287.5,353.1 L291.56,353.65 L295.62,354.21 L299.69,354.76 L303.75,355.3 L307.81,355.84 L311.88,356.38 L315.94,356.92 L320.0,357.45 L324.06,357.98 L328.12,358.51 L332.19,359.03 L336.25,359.55 L340.31,360.07 L344.38,360.58 L348.44,361.09 L352.5,361.6 L356.56,362.11 L360.62,362.61 L364.69,363.11 L368.75,363.6 L372.81,364.1 L376.88,364.59 L380.94,365.07 L385.0,365.56 L389.06,366.04 L393.12,366.52 L397.19,366.99 L401.25,367.47 L405.31,367.94 L409.38,368.4 L413.44,368.87 L417.5,369.33 L421.56,369.79 L425.62,370.24 L429.69,370.7 L433.75,371.15 L437.81,371.59 L441.88,372.04 L445.94,372.48 L450.0,372.92" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4126;0.4128;1.0000" values="0;0;1;1"/></path>
<text x="454.0" y="376.9214821244131" text-anchor="start" style="font-size:11px;font-weight:700;fill:#e5484d" opacity="0">R 56%<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4126;0.4128;1.0000" values="0;0;1;1"/></text>
<path d="M60.0,316.0 L64.06,317.81 L68.12,319.59 L72.19,321.35 L76.25,323.08 L80.31,324.79 L84.38,326.47 L88.44,328.14 L92.5,329.77 L96.56,331.39 L100.62,332.98 L104.69,334.55 L108.75,336.1 L112.81,337.63 L116.88,339.14 L120.94,340.62 L125.0,342.09 L129.06,343.53 L133.12,344.96 L137.19,346.36 L141.25,347.75 L145.31,349.11 L149.38,350.46 L153.44,351.79 L157.5,353.1 L161.56,354.39 L165.62,355.66 L169.69,356.92 L173.75,358.16 L177.81,359.38 L181.88,360.58 L185.94,361.77 L190.0,362.94 L194.06,364.1 L198.12,365.24 L202.19,366.36 L206.25,367.47 L210.31,368.56 L214.38,369.63 L218.44,370.7 L222.5,371.74 L226.56,372.78 L230.62,373.79 L234.69,374.8 L238.75,375.79 L242.81,376.76 L246.88,377.73 L250.94,378.67 L255.0,379.61 L259.06,380.53 L263.12,381.44 L267.19,382.34 L271.25,383.23 L275.31,384.1 L279.38,384.96 L283.44,385.81 L287.5,386.65 L291.56,387.47 L295.62,388.28 L299.69,389.09 L303.75,389.88 L307.81,390.66 L311.88,391.43 L315.94,392.19 L320.0,392.93 L324.06,393.67 L328.12,394.4 L332.19,395.12 L336.25,395.82 L340.31,396.52 L344.38,397.21 L348.44,397.89 L352.5,398.56 L356.56,399.22 L360.62,399.87 L364.69,400.51 L368.75,401.14 L372.81,401.76 L376.88,402.38 L380.94,402.99 L385.0,403.58 L389.06,404.17 L393.12,404.75 L397.19,405.33 L401.25,405.89 L405.31,406.45 L409.38,407.0 L413.44,407.54 L417.5,408.08 L421.56,408.61 L425.62,409.12 L429.69,409.64 L433.75,410.14 L437.81,410.64 L441.88,411.13 L445.94,411.62 L450.0,412.1" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4509;0.4511;1.0000" values="0;0;1;1"/></path>
<text x="454.0" y="416.0959508754539" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2ea043" opacity="0">G 26%<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4509;0.4511;1.0000" values="0;0;1;1"/></text>
<path d="M60.0,316.0 L64.06,320.16 L68.12,324.18 L72.19,328.08 L76.25,331.85 L80.31,335.5 L84.38,339.03 L88.44,342.45 L92.5,345.76 L96.56,348.97 L100.62,352.07 L104.69,355.08 L108.75,357.98 L112.81,360.8 L116.88,363.52 L120.94,366.16 L125.0,368.71 L129.06,371.18 L133.12,373.58 L137.19,375.89 L141.25,378.13 L145.31,380.3 L149.38,382.41 L153.44,384.44 L157.5,386.41 L161.56,388.31 L165.62,390.16 L169.69,391.94 L173.75,393.67 L177.81,395.35 L181.88,396.96 L185.94,398.53 L190.0,400.05 L194.06,401.52 L198.12,402.94 L202.19,404.32 L206.25,405.65 L210.31,406.94 L214.38,408.19 L218.44,409.4 L222.5,410.57 L226.56,411.7 L230.62,412.8 L234.69,413.86 L238.75,414.89 L242.81,415.88 L246.88,416.85 L250.94,417.78 L255.0,418.68 L259.06,419.56 L263.12,420.4 L267.19,421.22 L271.25,422.01 L275.31,422.78 L279.38,423.52 L283.44,424.24 L287.5,424.94 L291.56,425.61 L295.62,426.26 L299.69,426.89 L303.75,427.5 L307.81,428.1 L311.88,428.67 L315.94,429.22 L320.0,429.76 L324.06,430.28 L328.12,430.78 L332.19,431.27 L336.25,431.74 L340.31,432.19 L344.38,432.64 L348.44,433.06 L352.5,433.48 L356.56,433.88 L360.62,434.27 L364.69,434.64 L368.75,435.0 L372.81,435.36 L376.88,435.7 L380.94,436.03 L385.0,436.34 L389.06,436.65 L393.12,436.95 L397.19,437.24 L401.25,437.52 L405.31,437.79 L409.38,438.06 L413.44,438.31 L417.5,438.56 L421.56,438.79 L425.62,439.02 L429.69,439.25 L433.75,439.46 L437.81,439.67 L441.88,439.87 L445.94,440.07 L450.0,440.26" fill="none" stroke="#2563eb" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4892;0.4894;1.0000" values="0;0;1;1"/></path>
<text x="454.0" y="444.25956810543994" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2563eb" opacity="0">B 4%<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4892;0.4894;1.0000" values="0;0;1;1"/></text>
<rect x="490" y="276" width="440" height="190" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="490" y="266" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">③ 遠い山が、物の色と、空の色の、どちらに近いか</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5403;0.5404;1.0000" values="0;0;1;1"/><rect x="510" y="312" width="60" height="32" fill="#b1c4fb" stroke="#94a3b8" stroke-width="1.5"/>
<text x="582" y="333" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">48 km 先の山   R 0.45 / G 0.56 / B 0.96</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5743;0.5745;1.0000" values="0;0;1;1"/><rect x="510" y="356" width="60" height="32" fill="#b1d2ff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="582" y="377" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">空の色   R 0.45 / G 0.65 / B 1.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6083;0.6085;1.0000" values="0;0;1;1"/><rect x="510" y="400" width="60" height="32" fill="#b19582" stroke="#94a3b8" stroke-width="1.5"/>
<text x="582" y="421" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">近い山(0.5 km)   R 0.45 / G 0.30 / B 0.23</text>
</g>
<text x="40" y="494" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">遠い山と空の、色の差(R の差 + G の差 + B の差):</text>
<text x="430" y="498" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5403;0.5404;1.0000" values="1;1;0;0"/></text>
<text x="430" y="498" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">112<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5403;0.5404;0.6424;0.6426;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="498" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">13<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6424;0.6426;1.0000" values="0;0;1;1"/></text>
<text x="480" y="498" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">(×0.01。近い山 → 48 km 先)</text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">遠くの物は、色が薄くなり、青みを帯びる(空気遠近法)<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">距離を増やすと、山の色が、空の色へ近づく<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.4126;0.4128;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">赤は残り、青は先に消える。代わりに、空気が、青い光を足す<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4126;0.4128;0.6892;0.6894;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">遠景を空の色に近づけると、奥行きが出る<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6892;0.6894;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:beer-rgb:end -->

### 空気遠近法 LUT の作り方

Hillaire の方式（EGSR 2020、"A Scalable and Production Ready Sky and Atmosphere Rendering Technique"）では、カメラの前方に、画面に合わせた 3D テクスチャ（froxel 格子）を用意します。解像度は 32×32×32 程度の小さなものです。x と y が画面上の位置、z がカメラからの距離（深度スライス）に対応します。

毎フレーム、この 3D テクスチャの各セルで、「カメラからそのセルまでの視線」に沿って、単散乱をレイマーチで積分します。各セルには、そこまでの<strong>散乱光（RGB）</strong>と<strong>透過率</strong>（アルファに、RGB の平均値）を保存します。多重散乱は、別に用意した小さな LUT（Multi-Scattering LUT）から近似して足します（[Multiple Scattering](../scattering/multiple-scattering.md)）。

実行時は、画面のピクセルの深度から、対応するスライスを求め、その位置で LUT を 1 回引くだけです。フォグの計算は、ピクセルあたりテクスチャ 1 回の読み込みで済みます。LUT が小さいので、生成のコストも小さく（0.1 ms 前後）、品質と速さを両立できます。

LUT の距離方向は、線形でなく、近くを細かく取る非線形な配置にします。近くのフォグは細かい距離変化が目につき、遠くは緩やかな変化で十分だからです。また、最大距離（たとえば 128 km）は、シーンの規模に合わせて決めます。

## よくあるミス

??? failure "空とフォグの色が合わない"
    **空と同じ LUT** を**フォグにも使う**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **空と同じ LUT で、色が一致する**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Aerial Perspective and Fog](index.md)
- [Hillaire 2020](../scattering/hillaire.md)
