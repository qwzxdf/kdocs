---
title: Cloud Lighting
tags:
  - 描画
---

# Cloud Lighting

<strong>雲は、光が内部で散乱するので、明るく、ふわふわに見えます</strong>。<strong>各点で太陽の方向にもう一度進んで、光の減衰（自己影）を求めます</strong>。このページでは、雲のライティングを説明します。

!!! tip "ポイント"
    - 太陽方向へ、短くマーチして、光の減衰を求める。
    - 位相関数（前方散乱）で、縁が光る。
    - 多重散乱の近似を足して、暗くなりすぎを防ぐ。
    - パウダー効果で、縁が暗く沈む表現。

## 光の計算
### Beer の法則

<strong>太陽に向かって雲の中を進むと、水滴にぶつかって光が減ります</strong>。<strong>密度を太陽方向に積分した「厚み」から、届く光が決まります</strong>。

<div class="formula">届く光 = exp( −厚み × 消散係数 )</div>

```hlsl
float LightMarch(float3 position, float3 sun_dir) {
  float optical_depth = 0;
  float step_length = kLightStepLength;
  for (int i = 1; i <= kLightStepCount; ++i) {
    float3 p = position + sun_dir * step_length * i;
    float density = CloudDensity(p, HeightFraction(p));
    optical_depth += density * step_length;
    step_length *= 1.5;
  }
  return optical_depth;
}
```

コードの要点です。サンプル数は 4〜6 個に抑えます。視線のサンプルごとに必要になるからです。ステップを伸ばしていく（`step *= 1.5`）のは、近くを細かく、遠くを粗くするためです。コストは、視線 N 回に光 M 回を掛けた量で、これが雲の描画が重い主な理由です。

<!-- fig:cloud-beer-powder:begin -->

<svg class="fig illust motion" data-fig="cloud-beer-powder" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-cloud-beer-powder" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">雲の光: Beer の法則(奥へ進むと暗い)に、Powder 効果(縁は暗い)を掛けて、雲らしい明暗にする</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">雲の中へ、光が深さ d まで入る。Beer = exp(−k·d)、Powder = 1 − exp(−2k·d)。縁(浅い所)と奥の明るさを、式で計算する</text>
<rect x="30" y="96" width="560" height="260" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 光が入る深さと、明るさ</text>
<text x="70.0" y="348" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">0</text>
<text x="195.0" y="348" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">1</text>
<text x="320.0" y="348" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">2</text>
<text x="445.0" y="348" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">3</text>
<text x="570.0" y="348" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">4</text>
<text x="580" y="348" text-anchor="end" style="font-size:10px;font-weight:500;fill:#64748b">深さ d</text>
<path d="M70.0,130.0 L76.25,141.65 L82.5,152.62 L88.75,162.95 L95.0,172.67 L101.25,181.84 L107.5,190.46 L113.75,198.59 L120.0,206.24 L126.25,213.45 L132.5,220.24 L138.75,226.63 L145.0,232.65 L151.25,238.32 L157.5,243.66 L163.75,248.69 L170.0,253.42 L176.25,257.88 L182.5,262.08 L188.75,266.04 L195.0,269.76 L201.25,273.27 L207.5,276.57 L213.75,279.68 L220.0,282.61 L226.25,285.37 L232.5,287.97 L238.75,290.42 L245.0,292.73 L251.25,294.9 L257.5,296.94 L263.75,298.87 L270.0,300.68 L276.25,302.39 L282.5,303.99 L288.75,305.51 L295.0,306.93 L301.25,308.28 L307.5,309.54 L313.75,310.73 L320.0,311.86 L326.25,312.91 L332.5,313.91 L338.75,314.85 L345.0,315.73 L351.25,316.56 L357.5,317.34 L363.75,318.08 L370.0,318.77 L376.25,319.43 L382.5,320.04 L388.75,320.62 L395.0,321.17 L401.25,321.68 L407.5,322.17 L413.75,322.62 L420.0,323.05 L426.25,323.46 L432.5,323.84 L438.75,324.2 L445.0,324.54 L451.25,324.85 L457.5,325.15 L463.75,325.44 L470.0,325.7 L476.25,325.95 L482.5,326.19 L488.75,326.41 L495.0,326.62 L501.25,326.82 L507.5,327.0 L513.75,327.18 L520.0,327.34 L526.25,327.49 L532.5,327.64 L538.75,327.78 L545.0,327.91 L551.25,328.03 L557.5,328.14 L563.75,328.25 L570.0,328.35" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></path>
<text x="557.5" y="320.144197222587" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043" opacity="0">Beer(奥へ減る)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,330.0 L76.25,307.38 L82.5,287.33 L88.75,269.54 L95.0,253.76 L101.25,239.76 L107.5,227.35 L113.75,216.34 L120.0,206.58 L126.25,197.92 L132.5,190.24 L138.75,183.43 L145.0,177.39 L151.25,172.03 L157.5,167.27 L163.75,163.06 L170.0,159.32 L176.25,156.01 L182.5,153.07 L188.75,150.46 L195.0,148.14 L201.25,146.09 L207.5,144.27 L213.75,142.66 L220.0,141.23 L226.25,139.96 L232.5,138.83 L238.75,137.83 L245.0,136.95 L251.25,136.16 L257.5,135.46 L263.75,134.85 L270.0,134.3 L276.25,133.81 L282.5,133.38 L288.75,133.0 L295.0,132.66 L301.25,132.36 L307.5,132.09 L313.75,131.86 L320.0,131.65 L326.25,131.46 L332.5,131.29 L338.75,131.15 L345.0,131.02 L351.25,130.9 L357.5,130.8 L363.75,130.71 L370.0,130.63 L376.25,130.56 L382.5,130.5 L388.75,130.44 L395.0,130.39 L401.25,130.35 L407.5,130.31 L413.75,130.27 L420.0,130.24 L426.25,130.21 L432.5,130.19 L438.75,130.17 L445.0,130.15 L451.25,130.13 L457.5,130.12 L463.75,130.1 L470.0,130.09 L476.25,130.08 L482.5,130.07 L488.75,130.06 L495.0,130.06 L501.25,130.05 L507.5,130.04 L513.75,130.04 L520.0,130.04 L526.25,130.03 L532.5,130.03 L538.75,130.02 L545.0,130.02 L551.25,130.02 L557.5,130.02 L563.75,130.02 L570.0,130.01" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2665;0.2667;1.0000" values="0;0;1;1"/></path>
<text x="557.5" y="122.01722001974326" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5aa28" opacity="0">Powder(縁は暗い)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2665;0.2667;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,330.0 L76.25,287.4 L82.5,254.3 L88.75,228.99 L95.0,210.05 L101.25,196.3 L107.5,186.77 L113.75,180.64 L120.0,177.26 L126.25,176.06 L132.5,176.59 L138.75,178.49 L145.0,181.43 L151.25,185.17 L157.5,189.5 L163.75,194.25 L170.0,199.3 L176.25,204.52 L182.5,209.83 L188.75,215.16 L195.0,220.45 L201.25,225.67 L207.5,230.77 L213.75,235.74 L220.0,240.55 L226.25,245.19 L232.5,249.66 L238.75,253.94 L245.0,258.04 L251.25,261.95 L257.5,265.69 L263.75,269.24 L270.0,272.62 L276.25,275.83 L282.5,278.87 L288.75,281.75 L295.0,284.48 L301.25,287.07 L307.5,289.51 L313.75,291.83 L320.0,294.01 L326.25,296.08 L332.5,298.02 L338.75,299.86 L345.0,301.6 L351.25,303.24 L357.5,304.78 L363.75,306.24 L370.0,307.62 L376.25,308.91 L382.5,310.13 L388.75,311.29 L395.0,312.37 L401.25,313.39 L407.5,314.36 L413.75,315.27 L420.0,316.12 L426.25,316.93 L432.5,317.69 L438.75,318.4 L445.0,319.08 L451.25,319.71 L457.5,320.31 L463.75,320.88 L470.0,321.41 L476.25,321.91 L482.5,322.38 L488.75,322.82 L495.0,323.24 L501.25,323.63 L507.5,324.0 L513.75,324.35 L520.0,324.68 L526.25,324.99 L532.5,325.28 L538.75,325.56 L545.0,325.82 L551.25,326.06 L557.5,326.29 L563.75,326.5 L570.0,326.71" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4665;0.4667;1.0000" values="0;0;1;1"/></path>
<text x="557.5" y="318.28871401477875" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">Beer × Powder × 2<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4665;0.4667;1.0000" values="0;0;1;1"/></text>
<rect x="620" y="96" width="310" height="260" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="620" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 雲の断面(左 = 縁、右 = 奥)</text>
<text x="636" y="136" text-anchor="start" style="font-size:11px;font-weight:700;fill:#2ea043">Beer(奥へ減る)</text>
<rect x="636.0" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667" values="#e5e7eb;#e5e5e5"/></rect>
<rect x="647.5" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0684" values="#e5e7eb;#bebebe"/></rect>
<rect x="659.0" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0702" values="#e5e7eb;#9d9d9d"/></rect>
<rect x="670.5" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#e5e7eb;#828282"/></rect>
<rect x="682.0" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="693.5" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#5b5b5b"/></rect>
<rect x="705.0" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#4c4c4c"/></rect>
<rect x="716.5" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#404040"/></rect>
<rect x="728.0" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#363636"/></rect>
<rect x="739.5" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#2e2e2e"/></rect>
<rect x="751.0" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#282828"/></rect>
<rect x="762.5" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#e5e7eb;#222222"/></rect>
<rect x="774.0" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#1e1e1e"/></rect>
<rect x="785.5" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#1a1a1a"/></rect>
<rect x="797.0" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#181818"/></rect>
<rect x="808.5" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#151515"/></rect>
<rect x="820.0" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#e5e7eb;#131313"/></rect>
<rect x="831.5" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0969" values="#e5e7eb;#121212"/></rect>
<rect x="843.0" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0987" values="#e5e7eb;#101010"/></rect>
<rect x="854.5" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1004" values="#e5e7eb;#0f0f0f"/></rect>
<rect x="866.0" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022" values="#e5e7eb;#0e0e0e"/></rect>
<rect x="877.5" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1040" values="#e5e7eb;#0d0d0d"/></rect>
<rect x="889.0" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1058" values="#e5e7eb;#0d0d0d"/></rect>
<rect x="900.5" y="140.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1076" values="#e5e7eb;#0c0c0c"/></rect>
<rect x="636" y="140" width="276.0" height="34.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="636" y="206" text-anchor="start" style="font-size:11px;font-weight:700;fill:#e5aa28">Powder(縁は暗い)</text>
<rect x="636.0" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2667" values="#e5e7eb;#363636"/></rect>
<rect x="647.5" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2684" values="#e5e7eb;#787878"/></rect>
<rect x="659.0" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2702" values="#e5e7eb;#a3a3a3"/></rect>
<rect x="670.5" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2720" values="#e5e7eb;#c1c1c1"/></rect>
<rect x="682.0" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2738" values="#e5e7eb;#d4d4d4"/></rect>
<rect x="693.5" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2756" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="705.0" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2773" values="#e5e7eb;#eaeaea"/></rect>
<rect x="716.5" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#f0f0f0"/></rect>
<rect x="728.0" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#e5e7eb;#f4f4f4"/></rect>
<rect x="739.5" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2827" values="#e5e7eb;#f7f7f7"/></rect>
<rect x="751.0" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2844" values="#e5e7eb;#f9f9f9"/></rect>
<rect x="762.5" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2862" values="#e5e7eb;#fafafa"/></rect>
<rect x="774.0" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2880" values="#e5e7eb;#fbfbfb"/></rect>
<rect x="785.5" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#fbfbfb"/></rect>
<rect x="797.0" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2916" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="808.5" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="820.0" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2951" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="831.5" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2969" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="843.0" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2987" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="854.5" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3004" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="866.0" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3022" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="877.5" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3040" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="889.0" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3058" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="900.5" y="210.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3076" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="636" y="210" width="276.0" height="34.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="636" y="276" text-anchor="start" style="font-size:11px;font-weight:700;fill:#e5484d">Beer × Powder × 2</text>
<rect x="636.0" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4667" values="#e5e7eb;#5a5a5a"/></rect>
<rect x="647.5" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4684" values="#e5e7eb;#acacac"/></rect>
<rect x="659.0" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#e5e7eb;#c4c4c4"/></rect>
<rect x="670.5" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="682.0" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#e5e7eb;#afafaf"/></rect>
<rect x="693.5" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#e5e7eb;#9a9a9a"/></rect>
<rect x="705.0" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#e5e7eb;#848484"/></rect>
<rect x="716.5" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#e5e7eb;#717171"/></rect>
<rect x="728.0" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#e5e7eb;#606060"/></rect>
<rect x="739.5" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#e5e7eb;#515151"/></rect>
<rect x="751.0" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#e5e7eb;#454545"/></rect>
<rect x="762.5" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#e5e7eb;#3a3a3a"/></rect>
<rect x="774.0" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#e5e7eb;#323232"/></rect>
<rect x="785.5" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#e5e7eb;#2b2b2b"/></rect>
<rect x="797.0" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#e5e7eb;#252525"/></rect>
<rect x="808.5" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#e5e7eb;#202020"/></rect>
<rect x="820.0" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#e5e7eb;#1c1c1c"/></rect>
<rect x="831.5" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#e5e7eb;#191919"/></rect>
<rect x="843.0" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4987" values="#e5e7eb;#161616"/></rect>
<rect x="854.5" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5004" values="#e5e7eb;#141414"/></rect>
<rect x="866.0" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#e5e7eb;#121212"/></rect>
<rect x="877.5" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5040" values="#e5e7eb;#111111"/></rect>
<rect x="889.0" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5058" values="#e5e7eb;#101010"/></rect>
<rect x="900.5" y="280.0" width="11.8" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5076" values="#e5e7eb;#0f0f0f"/></rect>
<rect x="636" y="280" width="276.0" height="34.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="40" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">縁の明るさ(d = 0.1)/ 最も明るい所 / 奥(d = 3):</text>
<text x="40" y="420" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">Beer だけ: 0.89 / 1.00 / 0.03<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></text>
<text x="40" y="444" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">Beer × Powder × 2: 0.38 / 0.77(深さ 0.45)/ 0.05<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4665;0.4667;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6532;0.6533;1.0000" values="0;0;1;1"/><rect x="430" y="400" width="500" height="90" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="446" y="424" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1e3a8a">Beer だけだと、縁がいちばん明るい。Powder を掛けると、縁が暗く、少し奥で最大(深さ 0.45)</text>
<text x="446" y="446" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">雲の縁が暗く縁取られる、ふわふわした感じが出る(太陽に向かう側では弱い)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">雲に入った光は、進むほど、吸われて減る(Beer の法則)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">Beer だけでは、縁が、いちばん明るく見える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.2665;0.2667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">縁は、まだ光が散っていないので暗い(Powder)。掛けると、縁だけが暗くなる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2665;0.2667;0.6665;0.6667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">雲らしい、中が明るく、縁が少し暗い見た目<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6665;0.6667;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:cloud-beer-powder:end -->

### Powder 効果

<strong>雲の縁（薄い所）は、Beer の法則だと「明るすぎる」ですが実際には暗いことがあります</strong>。<strong>散乱された光が雲の奥から出てこないため</strong>です。Powder 効果はこれを近似します。

<div class="formula">Powder = 1 − exp( −2 · density )</div>

```hlsl
float PowderEffect(float density) {
  return 1.0 - exp(-density * 2.0);
}
```

<strong>Beer（薄いほど明るい）と Powder（薄いほど暗い）を掛ける</strong>と<strong>縁が暗く、中が明るい</strong>という実際の雲の見え方に近づきます（Beer-Powder）。

### 位相関数

<strong>雲の水滴は大きいため、光を前方に強く散らします</strong>。<strong>太陽の方を見ると雲の縁が銀色に光る（シルバーライニング）のはこれが理由</strong>です。前方ローブと後方ローブを混ぜた二重 Henyey-Greenstein を使います。

```hlsl
float CloudPhase(float cos_theta) {
  float forward = HenyeyGreenstein(cos_theta, 0.8);
  float backward = HenyeyGreenstein(cos_theta, -0.3);
  return lerp(backward, forward, 0.7);
}
```

### 多重散乱の近似

<strong>雲の中では光が何度も散らされ、明るく見えます</strong>。<strong>Beer の法則だけだと、厚い雲が暗くなりすぎます</strong>。消散・位相の寄与を数オクターブ分、減衰させながら足す近似で、厚い雲を適度に明るくします。

```hlsl
float3 MultiScatteredLight(float optical_depth, float phase_cos) {
  float3 luminance = 0;
  float attenuation = 1.0;
  float contribution = 1.0;
  float phase_attenuation = 1.0;
  for (int octave = 0; octave < 4; ++octave) {
    float p = CloudPhaseWithG(phase_cos, 0.8 * phase_attenuation);
    luminance += contribution * p * exp(-optical_depth * attenuation) * sun_color;
    attenuation *= 0.5;
    contribution *= 0.5;
    phase_attenuation *= 0.5;
  }
  return luminance;
}
```

### 4 つの項目の関係

ここまでの要素が、雲の明るさにどう関わるかをまとめます。ある点の明るさは、次の形で書けます。

<div class="formula">L = 太陽光 × 位相関数 × 透過率（太陽まで）× Powder + 環境光</div>

太陽光は、太陽から来る光の強さです。位相関数は、散乱の方向依存性（前方に強く散らす）で、縁の銀色の輝き（シルバー ライニング）を作ります。太陽までの透過率は、Beer の法則で、雲の奥ほど暗くします（自己影）。Powder は、薄い縁を暗く沈ませる補正です。環境光は、空からの光で、太陽の当たらない雲の底面や影を青白く照らします。

雲の下側（底）は暗く、青みがかります。これは、雲の中を通り抜けた太陽光がほとんど残らず、空と地面からの環境光が主になるためです。環境光を考えずに太陽光だけで描くと、雲の底が真っ黒になって不自然です。環境光は、高さに応じて、底で暗く、上で明るくなるグラデーションにすると、簡単で効果的です。

### 多重散乱が必要な理由

厚い積乱雲の中心は、Beer の法則だけでは、太陽光が届かず真っ暗になってしまいます。しかし実際には、雲の中で光が何度も散乱して、雲全体が白く明るく見えます。多重散乱の近似（上のコード）は、この「何度も散乱した光」を、消散を弱めながら、位相関数を等方に近づけながら、数回分重ねて表現します。Wrenninge らの Production Volume Rendering（2012）で紹介された方法で、Schneider の Horizon Zero Dawn のあとも、Hillaire ら多くのゲーム エンジンの雲で使われています。

## 雲の、光の、特徴

<strong>雲が、白く、ふわふわして、立体的</strong>に、見えるのは、<strong>光の、散らばり方</strong>に、特徴が、あるためです。

| 現象 | 見え方 |
| --- | --- |
| 前方散乱（ミー散乱が、強い） | 太陽の方向の、雲の縁が、明るく、銀色に、光る（シルバー ライニング） |
| 多重散乱 | 雲の、内側まで、光が、届き、真っ黒にならない |
| 吸収と、散乱の、バランス | 厚い雲は、暗い、底（光が、届かない）、薄い縁は、明るい |
| 粉っぽさ（Powder） | 雲の、縁は、暗く、縁取られて見える（光が、散乱しきっていない） |

## 1 点での、光の、計算

レイマーチの、<strong>各サンプル点</strong>で、<strong>太陽の光が、その点に、どれだけ、届くか</strong>を、求め、位相関数を、掛けて、視線の方向へ、散る光を、得ます。

```hlsl
float3 CloudLighting(float3 p, float3 view_dir, float density) {
  // ① 太陽の光が、この点まで、どれだけ届くか（太陽方向へ、密度を積分して、Beer の法則で、減衰）。
  float light_optical_depth = LightMarchDensity(p, g_sun_dir);
  float beer = exp(-light_optical_depth * g_extinction);
```

<strong>太陽の方向</strong>へ、<strong>短く、レイマーチ</strong>し（6〜8 ステップ）、途中の、密度を、積分します。Beer の法則（`exp(−τ)`）で、太陽の光が、点まで、届く割合を、求めます。雲の、厚い部分を、通った光ほど、弱くなります。

```hlsl
  // ② 位相関数（前方散乱 + 後方散乱の、2 つの HG）。太陽の方向を、向いているとき、強く光る。
  float cos_theta = dot(view_dir, g_sun_dir);
  float phase = lerp(HenyeyGreenstein(cos_theta, -0.3), HenyeyGreenstein(cos_theta, 0.8), 0.7);
```

<strong>2 つの、HG</strong>（<strong>前方の、強い山</strong>と、後方の、弱い山）を、混ぜた位相関数です（[Phase Functions](../scattering/phase-function.md)）。太陽の方を、向くと、前方散乱で、縁が、強く、光ります。

```hlsl
  // ③ 粉っぽさ（Powder）: 薄い所（密度が低い所）では、光が、まだ、散乱しきらず、暗く見える。
  float powder = 1.0 - exp(-density * g_extinction * 2.0);
  float beer_powder = 2.0 * beer * powder;
```

<strong>Beer の法則</strong>だけだと、<strong>雲の縁（薄い所）が、明るすぎ</strong>ます。Powder 効果（1 − exp(−2τ)）を、掛けると、縁が、暗く縁取られ、ふわふわした、雲らしさが、出ます（[Cloud Beer-Powder]の、図、参照）。太陽の方向を、向くときは、Powder の影響を、弱めます（縁が、輝くので）。

```hlsl
  // ④ 太陽の方を向くほど、Powder を弱める（縁が、輝くので）。
  float powder_blend = lerp(beer_powder, beer, saturate(cos_theta * 0.5 + 0.5));
  float3 sun_light = g_sun_color * powder_blend * phase;
```

<strong>太陽に、背を向ける</strong>ときは、<strong>Powder を、強く</strong>（縁が、暗く）、太陽に、向かうときは、Beer だけ（縁が、明るい）、と、補間します。

```hlsl
  // ⑤ 環境光（空の光）: 雲の、上は、空の光で、明るく、底は、地面からの、暗い反射光だけ。
  float height_fraction = HeightFractionAt(p);
  float3 ambient = lerp(g_ambient_bottom, g_ambient_top, saturate(height_fraction));
  return sun_light + ambient * 0.5;
}
```

<strong>環境光</strong>は、<strong>高さ</strong>で、変えます。雲の、上の方は、空の光で、明るく、底は、地面から、反射した、暗い光だけです。雲の底が、暗い（影っぽい）のは、雲の、厚みで、太陽の光が、届かず、環境光も、弱いためです。

## 光の、方向への、レイマーチ

<strong>太陽の方向</strong>へ、<strong>短く、レイマーチ</strong>して、密度を、積分します。この計算が、レイマーチの、各サンプルで、必要なので、ステップ数は、少なく（6〜8）します。

```hlsl
// 太陽方向への、密度の、積分（光学的な厚さ）。少ないステップ数で、近似する。
float LightMarchDensity(float3 p, float3 sun_dir) {
  const int kLightSteps = 6;
  float step_len = g_light_march_length / kLightSteps;
  float sum = 0.0;
  for (int i = 1; i <= kLightSteps; ++i) {
    // ステップを、だんだん、大きく（遠い所は、粗くてよい）。ランダムな、円錐状のずれを、足す（ノイズ）。
    float t = step_len * i * i * 0.3;
    float3 sample_pos = p + sun_dir * t + RandomConeOffset(i) * t * 0.1;
    sum += CloudDensityCheap(sample_pos) * step_len;                 // 安い密度（細部のノイズは、読まない）
  }
  return sum;
}
```

<strong>光の方向の、積分</strong>は、<strong>細部が、不要</strong>（ぼんやり、減衰するだけ）なので、安い密度（基本の形だけ）で、十分です。ステップを、だんだん大きくし、円錐状に、少しずらす（ノイズ）と、少ないステップでも、なめらかに、なります。

## 多重散乱の、近似

<strong>1 回散乱</strong>（太陽 → 点 → 目）だけでは、<strong>雲の、内部が、暗すぎ</strong>ます。光は、雲の中で、何度も、散乱して、奥まで、届くためです。オクターブによる、近似（[Multiple Scattering](../scattering/multiple-scattering.md)）で、足します。

```hlsl
// 多重散乱: 散乱量 a を、半分ずつ、減衰 b を、弱く、位相の偏り c を、弱く（等方に、近づける）、4 回、足す。
float3 multi = 0.0;
float a = 1.0, b = 1.0, c = 1.0;
for (int octave = 0; octave < 4; ++octave) {
  float ph = DualLobePhase(cos_theta, 0.8 * c, -0.3 * c, 0.7);
  multi += a * ph * exp(-light_optical_depth * g_extinction * b);
  a *= 0.5; b *= 0.25; c *= 0.5;
}
float3 sun_light = g_sun_color * multi;
```

<strong>オクターブが、進むほど</strong>、<strong>散乱量が、半分</strong>に、減衰が、弱まり（深くまで、届く）、位相関数が、等方に近づく（散らばる）。これで、厚い雲の、内部でも、光が、ほどよく、届き、ふわっとした、明るさが、出ます。

## 長所と、調整

| 要素 | 効果 | 調整 |
| --- | --- | --- |
| 前方散乱（`g_forward`） | 太陽側の、縁が、光る | 0.6〜0.9。大きいほど、太陽の近くだけ、強く光る |
| 後方散乱（`g_back`） | 太陽の反対側の、うっすらとした、明るさ | −0.2〜−0.5 |
| Powder | 縁の、暗い縁取り | 強すぎると、雲が、ごつごつする |
| 消散係数 | 雲の、濃さ（暗さ） | 大きいと、暗く、濃い |
| 環境光 | 底の、明るさ | 底が、黒すぎないよう、少し、足す |

## よくあるミス

??? failure "雲が、のっぺり白い・立体感がない"
    <strong>自己影（太陽方向のマーチ）</strong>を<strong>入れる</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自己影・前方散乱・多重散乱の近似

## 参考

- Schneider, Vos, "The Real-Time Volumetric Cloudscapes of Horizon: Zero Dawn", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Wrenninge, "Art-Directable Multiple Volumetric Scattering", SIGGRAPH 2015 Talks
- Henyey, Greenstein, "Diffuse Radiation in the Galaxy", Astrophysical Journal, Vol. 93, 1941
- Beer, "Bestimmung der Absorption des rothen Lichts in farbigen Flüssigkeiten", Annalen der Physik, 1852
- Hillaire, "Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Clouds](index.md)
- [Phase Functions](../scattering/phase-function.md)
- [Multiple Scattering](../scattering/multiple-scattering.md)
