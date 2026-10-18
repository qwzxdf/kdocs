---
title: Grid Mesh
tags:
  - 描画
---

# Grid Mesh

**格子状に頂点を並べ、各頂点の高さを、高さマップから読み出して設定**します。**頂点の数が、地形の細かさ**を決めます。このページでは、**格子メッシュの作り方と、頂点の高さ**を説明します。

!!! tip "ポイント"
    - **格子 ＝ 規則的に並べた頂点とインデックス**。
    - **頂点シェーダーで、高さマップを読んで持ち上げる**（頂点テクスチャ フェッチ）。
    - **同じ格子メッシュを、何度も再利用できる**。
    - **頂点が多いほど細かいが、重い**。

<!-- fig:heightmap-lift:begin -->

<svg class="fig illust motion" data-fig="heightmap-lift" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-heightmap-lift" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">高さマップを、格子の頂点の高さに使う: 平らな格子を、1 頂点ずつ持ち上げ、法線は、隣の高さの差から求める</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 次元の断面。頂点 17 個の平らな線を、高さマップで持ち上げる。三角形の数と、各頂点の法線の傾きを計算する</text>
<rect x="30" y="96" width="900" height="270" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 平らな格子 → 高さで持ち上げた格子(青 = 持ち上げた線)</text>
<line x1="70.0" y1="330.0" x2="870.0" y2="330.0" stroke="#94a3b8" stroke-width="2.5" stroke-dasharray="5 4"/>
<circle cx="70.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="120.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="170.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="220.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="270.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="320.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="370.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="420.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="470.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="520.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="570.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="620.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="670.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="720.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="770.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="820.0" cy="330.0" r="4" fill="#94a3b8"/>
<circle cx="870.0" cy="330.0" r="4" fill="#94a3b8"/>
<path d="M70.0,330.0 L120.0,330.0 L170.0,330.0 L220.0,330.0 L270.0,330.0 L320.0,330.0 L370.0,330.0 L420.0,330.0 L470.0,330.0 L520.0,330.0 L570.0,330.0 L620.0,330.0 L670.0,330.0 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0" fill="none" stroke="#2563eb" stroke-width="3.5"><animate attributeName="d" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222" values="M70.0,330.0 L120.0,330.0 L170.0,330.0 L220.0,330.0 L270.0,330.0 L320.0,330.0 L370.0,330.0 L420.0,330.0 L470.0,330.0 L520.0,330.0 L570.0,330.0 L620.0,330.0 L670.0,330.0 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,330.0 L170.0,330.0 L220.0,330.0 L270.0,330.0 L320.0,330.0 L370.0,330.0 L420.0,330.0 L470.0,330.0 L520.0,330.0 L570.0,330.0 L620.0,330.0 L670.0,330.0 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,330.0 L220.0,330.0 L270.0,330.0 L320.0,330.0 L370.0,330.0 L420.0,330.0 L470.0,330.0 L520.0,330.0 L570.0,330.0 L620.0,330.0 L670.0,330.0 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,330.0 L270.0,330.0 L320.0,330.0 L370.0,330.0 L420.0,330.0 L470.0,330.0 L520.0,330.0 L570.0,330.0 L620.0,330.0 L670.0,330.0 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,258.24 L270.0,330.0 L320.0,330.0 L370.0,330.0 L420.0,330.0 L470.0,330.0 L520.0,330.0 L570.0,330.0 L620.0,330.0 L670.0,330.0 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,258.24 L270.0,266.24 L320.0,330.0 L370.0,330.0 L420.0,330.0 L470.0,330.0 L520.0,330.0 L570.0,330.0 L620.0,330.0 L670.0,330.0 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,258.24 L270.0,266.24 L320.0,282.49 L370.0,330.0 L420.0,330.0 L470.0,330.0 L520.0,330.0 L570.0,330.0 L620.0,330.0 L670.0,330.0 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,258.24 L270.0,266.24 L320.0,282.49 L370.0,286.74 L420.0,330.0 L470.0,330.0 L520.0,330.0 L570.0,330.0 L620.0,330.0 L670.0,330.0 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,258.24 L270.0,266.24 L320.0,282.49 L370.0,286.74 L420.0,280.15 L470.0,330.0 L520.0,330.0 L570.0,330.0 L620.0,330.0 L670.0,330.0 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,258.24 L270.0,266.24 L320.0,282.49 L370.0,286.74 L420.0,280.15 L470.0,290.8 L520.0,330.0 L570.0,330.0 L620.0,330.0 L670.0,330.0 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,258.24 L270.0,266.24 L320.0,282.49 L370.0,286.74 L420.0,280.15 L470.0,290.8 L520.0,270.59 L570.0,330.0 L620.0,330.0 L670.0,330.0 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,258.24 L270.0,266.24 L320.0,282.49 L370.0,286.74 L420.0,280.15 L470.0,290.8 L520.0,270.59 L570.0,266.42 L620.0,330.0 L670.0,330.0 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,258.24 L270.0,266.24 L320.0,282.49 L370.0,286.74 L420.0,280.15 L470.0,290.8 L520.0,270.59 L570.0,266.42 L620.0,240.24 L670.0,330.0 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,258.24 L270.0,266.24 L320.0,282.49 L370.0,286.74 L420.0,280.15 L470.0,290.8 L520.0,270.59 L570.0,266.42 L620.0,240.24 L670.0,248.09 L720.0,330.0 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,258.24 L270.0,266.24 L320.0,282.49 L370.0,286.74 L420.0,280.15 L470.0,290.8 L520.0,270.59 L570.0,266.42 L620.0,240.24 L670.0,248.09 L720.0,260.25 L770.0,330.0 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,258.24 L270.0,266.24 L320.0,282.49 L370.0,286.74 L420.0,280.15 L470.0,290.8 L520.0,270.59 L570.0,266.42 L620.0,240.24 L670.0,248.09 L720.0,260.25 L770.0,317.5 L820.0,330.0 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,258.24 L270.0,266.24 L320.0,282.49 L370.0,286.74 L420.0,280.15 L470.0,290.8 L520.0,270.59 L570.0,266.42 L620.0,240.24 L670.0,248.09 L720.0,260.25 L770.0,317.5 L820.0,325.93 L870.0,330.0;M70.0,310.84 L120.0,294.03 L170.0,263.55 L220.0,258.24 L270.0,266.24 L320.0,282.49 L370.0,286.74 L420.0,280.15 L470.0,290.8 L520.0,270.59 L570.0,266.42 L620.0,240.24 L670.0,248.09 L720.0,260.25 L770.0,317.5 L820.0,325.93 L870.0,310.93"/></path>
<circle cx="70.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="330;330;310.84;310.84"/></circle>
<circle cx="120.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;1.0000" values="330;330;294.03;294.03"/></circle>
<circle cx="170.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1109;0.1111;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1109;0.1111;1.0000" values="330;330;263.55;263.55"/></circle>
<circle cx="220.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1332;0.1333;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1332;0.1333;1.0000" values="330;330;258.24;258.24"/></circle>
<circle cx="270.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;1.0000" values="330;330;266.24;266.24"/></circle>
<circle cx="320.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1776;0.1778;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1776;0.1778;1.0000" values="330;330;282.49;282.49"/></circle>
<circle cx="370.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;1.0000" values="330;330;286.74;286.74"/></circle>
<circle cx="420.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2220;0.2222;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2220;0.2222;1.0000" values="330;330;280.15;280.15"/></circle>
<circle cx="470.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2443;0.2444;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2443;0.2444;1.0000" values="330;330;290.8;290.8"/></circle>
<circle cx="520.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2665;0.2667;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2665;0.2667;1.0000" values="330;330;270.59;270.59"/></circle>
<circle cx="570.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2887;0.2889;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2887;0.2889;1.0000" values="330;330;266.42;266.42"/></circle>
<circle cx="620.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;1.0000" values="330;330;240.24;240.24"/></circle>
<circle cx="670.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3332;0.3333;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3332;0.3333;1.0000" values="330;330;248.09;248.09"/></circle>
<circle cx="720.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3554;0.3556;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3554;0.3556;1.0000" values="330;330;260.25;260.25"/></circle>
<circle cx="770.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3776;0.3778;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3776;0.3778;1.0000" values="330;330;317.5;317.5"/></circle>
<circle cx="820.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;1.0000" values="330;330;325.93;325.93"/></circle>
<circle cx="870.0" cy="330.0" r="5.5" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;1.0000" values="0;0;1;1"/><animate attributeName="cy" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;1.0000" values="330;330;310.93;310.93"/></circle>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4709;0.4711;1.0000" values="0;0;1;1"/><line x1="70.0" y1="310.84" x2="59.0" y2="287.29" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4776;0.4778;1.0000" values="0;0;1;1"/><line x1="120.0" y1="294.03" x2="105.72" y2="272.3" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4843;0.4844;1.0000" values="0;0;1;1"/><line x1="170.0" y1="263.55" x2="158.43" y2="240.26" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4909;0.4911;1.0000" values="0;0;1;1"/><line x1="220.0" y1="258.24" x2="220.97" y2="232.26" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4976;0.4978;1.0000" values="0;0;1;1"/><line x1="270.0" y1="266.24" x2="278.3" y2="241.6" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5043;0.5044;1.0000" values="0;0;1;1"/><line x1="320.0" y1="282.49" x2="327.12" y2="257.49" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5109;0.5111;1.0000" values="0;0;1;1"/><line x1="370.0" y1="286.74" x2="369.15" y2="260.75" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5176;0.5178;1.0000" values="0;0;1;1"/><line x1="420.0" y1="280.15" x2="421.46" y2="254.19" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5243;0.5244;1.0000" values="0;0;1;1"/><line x1="470.0" y1="290.8" x2="466.58" y2="265.02" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5309;0.5311;1.0000" values="0;0;1;1"/><line x1="520.0" y1="270.59" x2="511.66" y2="245.96" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5376;0.5378;1.0000" values="0;0;1;1"/><line x1="570.0" y1="266.42" x2="559.9" y2="242.46" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5443;0.5444;1.0000" values="0;0;1;1"/><line x1="620.0" y1="240.24" x2="613.58" y2="215.05" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5509;0.5511;1.0000" values="0;0;1;1"/><line x1="670.0" y1="248.09" x2="676.96" y2="223.04" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5576;0.5578;1.0000" values="0;0;1;1"/><line x1="720.0" y1="260.25" x2="738.05" y2="241.53" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5643;0.5644;1.0000" values="0;0;1;1"/><line x1="770.0" y1="317.5" x2="787.52" y2="298.29" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5709;0.5711;1.0000" values="0;0;1;1"/><line x1="820.0" y1="325.93" x2="817.64" y2="300.04" stroke="#e5484d" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5776;0.5778;1.0000" values="0;0;1;1"/><line x1="870.0" y1="310.93" x2="860.0" y2="286.93" stroke="#e5484d" stroke-width="2.5"/>
</g>
<text x="40" y="404" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">格子の頂点:</text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">1<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.0887;0.0889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">2<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;0.1109;0.1111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">3<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1109;0.1111;0.1332;0.1333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">4<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1332;0.1333;0.1554;0.1556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">5<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.1776;0.1778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">6<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1776;0.1778;0.1998;0.2000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">7<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1998;0.2000;0.2220;0.2222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">8<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2220;0.2222;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">9<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2443;0.2444;0.2665;0.2667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">10<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2665;0.2667;0.2887;0.2889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">11<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2887;0.2889;0.3109;0.3111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">12<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;0.3332;0.3333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">13<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3332;0.3333;0.3554;0.3556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">14<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3554;0.3556;0.3776;0.3778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3776;0.3778;0.3998;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">16<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;0.4220;0.4222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="408" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">17<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;1.0000" values="0;0;1;1"/></text>
<text x="40" y="440" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="0">法線(赤い線)は、左右の高さの差 (b − a) から求める: 法線 = (−(b − a)÷間隔, 1) を、正規化<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4709;0.4711;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6109;0.6111;1.0000" values="0;0;1;1"/><rect x="40" y="456" width="880" height="56" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="480" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">頂点を動かすだけ。三角形の数(2D では 32)は、変わらない。いちばん傾いた所の法線: 傾き 0.69</text>
<text x="56" y="503" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">頂点シェーダーで、高さマップを読んで、持ち上げる(CPU でメッシュを作り直さない)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">平らな格子に、高さマップを、1 頂点ずつ当てはめる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">頂点を持ち上げる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.4709;0.4711;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">隣の高さの差から、法線(陰の向き)を求める<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4709;0.4711;0.6109;0.6111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">メッシュの形は変えず、頂点の高さだけで、地形になる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6109;0.6111;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:heightmap-lift:end -->

## Grid Mesh {#格子メッシュ}
**高さマップの各テクセルに、頂点を 1 つ**対応させると、**格子状のメッシュ**になります。**N×N 頂点の格子は、(N−1)×(N−1) マスで、1 マスが三角形 2 枚**です。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="格子メッシュ">
<text x="20" y="24" class="fig-title">格子メッシュ：1 マスは三角形 2 枚</text>
<g stroke="currentColor" stroke-opacity="0.6" fill="none">
<rect x="100" y="50" width="120" height="120"/><rect x="220" y="50" width="120" height="120"/>
<line x1="100" y1="50" x2="220" y2="170"/><line x1="220" y1="50" x2="340" y2="170"/>
</g>
<circle cx="100" cy="50" r="4" fill="#4c8bf5"/><circle cx="220" cy="50" r="4" fill="#4c8bf5"/><circle cx="340" cy="50" r="4" fill="#4c8bf5"/>
<circle cx="100" cy="170" r="4" fill="#4c8bf5"/><circle cx="220" cy="170" r="4" fill="#4c8bf5"/><circle cx="340" cy="170" r="4" fill="#4c8bf5"/>
<text x="100" y="40" text-anchor="middle" style="font-size:11px">0</text><text x="220" y="40" text-anchor="middle" style="font-size:11px">1</text><text x="340" y="40" text-anchor="middle" style="font-size:11px">2</text>
<text x="100" y="190" text-anchor="middle" style="font-size:11px">N</text><text x="220" y="190" text-anchor="middle" style="font-size:11px">N+1</text><text x="340" y="190" text-anchor="middle" style="font-size:11px">N+2</text>
<text x="420" y="90" style="font-size:13px">頂点番号 ＝ z × N ＋ x</text>
<text x="420" y="116" style="font-size:13px">1 マス ＝ (i, i+1, i+N) と (i+1, i+N+1, i+N)</text>
<text x="420" y="142" style="font-size:13px">時計回りが表（左手系）</text>
</svg>

**頂点は、(x, z) の位置だけ**持てば**十分**です（**高さは頂点シェーダーで読む**）。**メッシュは全タイルで共有**できます。

```cpp
std::vector<uint32_t> BuildGridIndices(uint32_t n) {
  std::vector<uint32_t> indices;
  indices.reserve((n - 1) * (n - 1) * 6);
  for (uint32_t z = 0; z + 1 < n; ++z) {
    for (uint32_t x = 0; x + 1 < n; ++x) {
      uint32_t i = z * n + x;
      indices.push_back(i);
      indices.push_back(i + n);
      indices.push_back(i + 1);
      indices.push_back(i + 1);
      indices.push_back(i + n);
      indices.push_back(i + n + 1);
    }
  }
  return indices;
}
```

格子メッシュのインデックスのコードの要点です。時計回りが表です（左手系・Y 上・+Z 前方で、上から見て時計回り。[座標系](../../../3d/index.md)）。対角線の向きは、一方向に揃えると斜めの縞が出ることがあるので、交互に切り替える（ジグザグ）と自然です。インデックス数は (N−1)² × 6 で、65×65 頂点で約 2.5 万です。

### Reading Height in the Vertex Shader {#頂点シェーダーで高さを読む}

```hlsl
Texture2D<float> height_map : register(t0);
SamplerState linear_clamp : register(s0);

cbuffer TerrainParams : register(b1) {
  float2 terrain_origin;
  float terrain_size;
  float height_scale;
  float base_height;
};

VSOutput VSMain(VSInput input) {
  float2 world_xz = terrain_origin + input.grid_position * tile_size;
  float2 uv = (world_xz - terrain_origin_global) / terrain_size;
  float height = height_map.SampleLevel(linear_clamp, uv, 0) * height_scale + base_height;

  float3 world_position = float3(world_xz.x, height, world_xz.y);
  VSOutput output;
  output.position = mul(float4(world_position, 1), view_projection);
  output.world_position = world_position;
  output.uv = uv;
  return output;
}
```

高さを読む頂点シェーダーのコードの要点です。`SampleLevel` は、頂点シェーダーではミップ レベルを自分で指定するために使います（`Sample` は使えません）。ミップ レベルを距離で選び、遠くの頂点は粗いミップから読むとちらつきません。UV はワールド座標から求め、タイルの位置が違っても同じ高さマップを共有します。

## Common Mistakes {#よくあるミス}

??? failure "地形がカクカクして見える"
    **頂点密度を上げる**・**法線を滑らかに**する。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **格子の頂点を、高さマップで持ち上げる**

## References {#参考}

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## Related Pages {#関連ページ}

- [Heightmaps and Meshes](index.md)
- [LOD](../lod/index.md)
