---
title: Grid Mesh
tags:
  - 描画
---

# Grid Mesh

<strong>格子状に頂点を並べ各頂点の高さを、高さマップから読み出して設定</strong>します。頂点の数が地形の細かさを決めます。このページでは格子メッシュの作り方と、頂点の高さを説明します。

!!! tip "ポイント"
    - 格子 ＝ 規則的に並べた頂点とインデックス。
    - 頂点シェーダーで、高さマップを読んで持ち上げる（頂点テクスチャ フェッチ）。
    - 同じ格子メッシュを、何度も再利用できる。
    - 頂点が多いほど細かいが重い。

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

## 格子メッシュ
<strong>高さマップの各テクセルに頂点を 1 つ</strong>対応させると、格子状のメッシュになります。N×N 頂点の格子は(N−1)×(N−1) マスで、1 マスが三角形 2 枚です。

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
<text x="420" y="142" style="font-size:13px">反時計回りが表（右手系）</text>
</svg>

頂点は(x, z) の位置だけ持てば十分です（高さは頂点シェーダーで読む）。メッシュは全タイルで共有できます。

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

格子メッシュのインデックスのコードの要点です。反時計回りが表です（右手系・Y 上で、上から見て反時計回り。[座標系](../../../3d/index.md)）。対角線の向きは一方向に揃えると斜めの縞が出ることがあるので、交互に切り替える（ジグザグ）と自然です。インデックス数は (N−1)² × 6 で、65×65 頂点で約 2.5 万です。

### 頂点シェーダーで高さを読む

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

高さを読む頂点シェーダーのコードの要点です。`SampleLevel` は頂点シェーダーではミップ レベルを自分で指定するために使います（`Sample` は使えません）。ミップ レベルを距離で選び遠くの頂点は粗いミップから読むとちらつきません。UV はワールド座標から求め、タイルの位置が違っても同じ高さマップを共有します。

## 格子の作り方を決める 4 つのこと

| 決めること | 選び方 |
| --- | --- |
| ① 1 枚の格子の頂点数 | 65×65、129×129、257×257 など `2^n + 1`。LOD で半分に間引けるので、偶数のマス数にする |
| ② インデックスの幅 | 16 ビット（頂点が 65,536 個まで、つまり 256×256 頂点まで）か、32 ビット |
| ③ 三角形の貼り方 | 全マスで同じ対角線か、市松（交互）か |
| ④ 頂点の形式 | `float2`（x, z）か、`uint16×2`（格子の整数座標）か |

### ① 頂点数と三角形の数

N×N 頂点の格子は `(N − 1)²` 個のマスで、`2 × (N − 1)²` 枚の三角形になります。

| 頂点数 | マス数 | 三角形 | 16 ビット index |
| --- | --- | --- | --- |
| 33×33 | 32×32 | 2,048 | 使える |
| 65×65 | 64×64 | 8,192 | 使える |
| 129×129 | 128×128 | 32,768 | 使える |
| 257×257 | 256×256 | 131,072 | 頂点が 66,049 個で、16 ビットでは足りない |

16 ビットのインデックスは、<strong>メモリの帯域が半分</strong>で済み、頂点バッファも小さくできます。1 枚の格子は 129×129 までに、とどめると扱いやすいです。それ以上の広さは同じ格子を位置を変えて、何枚も描きます（[Chunking](chunks.md)）。

### ② 頂点は(x, z) だけでよい

高さは頂点シェーダーが高さマップから読みます。頂点バッファには 0〜1 の格子上の位置（x, z）だけを持ちます。

```cpp
struct GridVertex { float x, z; };   // 0〜1

std::vector<GridVertex> BuildGridVertices(uint32_t n) {
  std::vector<GridVertex> v;
  v.reserve(n * n);
  for (uint32_t z = 0; z < n; ++z) {
    for (uint32_t x = 0; x < n; ++x) {
      v.push_back({float(x) / (n - 1), float(z) / (n - 1)});
    }
  }
  return v;
}
```

さらに小さくするなら座標を `uint16` 2 つ（0〜n−1 の整数）にして、シェーダーで `/ (n - 1)` します。129×129 頂点なら頂点バッファが、約 66 KB から 33 KB に、減ります。1 つの格子を数百回、使い回すので 頂点バッファ自体の大きさは、ほとんど問題になりません。大切なのは インデックスと頂点シェーダーの、軽さです。

### ③ 三角形の貼り方

1 つのマス（四角形）を 2 枚の三角形に分けるとき、対角線の向きが 2 通りあります。

| 方式 | 見た目 | 使いどころ |
| --- | --- | --- |
| 全マス、同じ向き | 斜面の同じ方向に、筋が出ることがある | 簡単 |
| 市松（交互） | 筋が目立ちにくい | モーフィング（CDLOD）を使うなら、必須（[CDLOD](../lod/cdlod.md)） |
| 高さに応じて向きを選ぶ | 谷や尾根の形に沿って貼る。見た目は最も自然 | 頂点ごとの判断が要る。実行時に決めにくい |

市松の貼り方では 2×2 マスごとに、対角線が交差する形になります。粗い LOD に落とすと粗い 1 マスの、2 枚の三角形にきれいにまとまります。

```cpp
std::vector<uint16_t> BuildCheckerIndices(uint32_t n) {
  std::vector<uint16_t> idx;
  idx.reserve((n - 1) * (n - 1) * 6);
  for (uint32_t z = 0; z + 1 < n; ++z) {
    for (uint32_t x = 0; x + 1 < n; ++x) {
      const uint16_t a = z * n + x;        // 左上
      const uint16_t b = a + 1;            // 右上
      const uint16_t c = a + n;            // 左下
      const uint16_t d = c + 1;            // 右下
      // 上から見て反時計回りが表。マスの位置で、対角線の向きを変える。
      if (((x + z) & 1) == 0) {
        idx.insert(idx.end(), {a, c, d, a, d, b});
      } else {
        idx.insert(idx.end(), {a, c, b, b, c, d});
      }
    }
  }
  return idx;
}
```

### ④ 表裏の向き（ワインディング）

地形は 上から見たとき反時計回りの三角形が表です（右手系・Y 上）。Direct3D 11 の既定は、時計回りが表なのでラスタライザー ステートで、反転します。

```cpp
D3D11_RASTERIZER_DESC rs = {};
rs.FillMode = D3D11_FILL_SOLID;
rs.CullMode = D3D11_CULL_BACK;
rs.FrontCounterClockwise = TRUE;      // 反時計回りを表にする（このサイトの決まり）
rs.DepthClipEnable = TRUE;
device->CreateRasterizerState(&rs, &rasterizer_state);
```

向きが逆だと地形が 裏返しになって、地面の上の面が消えます（裏面カリング）。地形がまるごと見えないときは最初に、この設定を疑います。

## 三角形ストリップとリスト

| 方式 | インデックス数（N×N 頂点） | 特徴 |
| --- | --- | --- |
| 三角形リスト | `6 × (N−1)²` | 簡単。LOD やモーフィングと相性がよい |
| 三角形ストリップ | 約 `2 × N × (N−1)` ＋ 切れ目 | インデックスは、約 1/3。行ごとにリスタート値（`0xFFFF`）で、つなぐ |

ストリップはインデックスの数が減りますが、<strong>現代の GPU の頂点キャッシュは、リストでも十分に効く</strong>ので差は、小さくなりました。市松の対角線はストリップでは、表現しにくいのでリストを使うのが、無難です。

## 頂点キャッシュに合わせる

GPU は <strong>直前に処理した頂点の結果を、数十個だけキャッシュ</strong>しています。同じ頂点を続けて使うほど処理が減ります。

格子を 行ごとに順番に並べると、1 行ぶんの頂点数がキャッシュの大きさを超えて、上の行の頂点がキャッシュから出てしまいます。

| 並べ方 | 頂点の再利用 |
| --- | --- |
| 行ごとの順（上のコード） | 頂点が、ほぼ 2 回、使われる。キャッシュが小さいと再計算が増える |
| 小さなブロック（例：8×8）ごとの順 | ブロック内で頂点を、使い回せる。キャッシュに収まりやすい |
| 最適化ツール（Forsyth のアルゴリズムなど）で並べ替え | インデックスを、キャッシュに最適な順に並べ替える。地形の格子のような規則的なメッシュでは効果は、限定的 |

格子メッシュは規則的なので 元の並びでも、十分に効率が良いことが多いです。数百万頂点を描くのでなければ、頂点キャッシュの最適化は後回しで、かまいません。

## DirectX 11 で、格子を作る

```cpp
// 頂点バッファ（変更しないので IMMUTABLE）
D3D11_BUFFER_DESC vb_desc = {};
vb_desc.ByteWidth = UINT(vertices.size() * sizeof(GridVertex));
vb_desc.Usage = D3D11_USAGE_IMMUTABLE;
vb_desc.BindFlags = D3D11_BIND_VERTEX_BUFFER;
D3D11_SUBRESOURCE_DATA vb_data = {vertices.data()};
device->CreateBuffer(&vb_desc, &vb_data, &grid_vb);

// インデックス バッファ（16 ビット）
D3D11_BUFFER_DESC ib_desc = {};
ib_desc.ByteWidth = UINT(indices.size() * sizeof(uint16_t));
ib_desc.Usage = D3D11_USAGE_IMMUTABLE;
ib_desc.BindFlags = D3D11_BIND_INDEX_BUFFER;
D3D11_SUBRESOURCE_DATA ib_data = {indices.data()};
device->CreateBuffer(&ib_desc, &ib_data, &grid_ib);
```

```hlsl
// 頂点シェーダー: 格子の位置を、ワールドに直し、高さマップから、高さを読む。
Texture2D<float> g_height : register(t0);
SamplerState g_linear_clamp : register(s0);

cbuffer ChunkCB : register(b1) {
  float2 chunk_origin;     // このチャンクの、左下のワールド XZ
  float chunk_size;        // チャンクの 1 辺（メートル）
  float height_scale;
  float2 height_uv_origin; // 高さマップ上の、このチャンクの範囲
  float2 height_uv_size;
  float height_offset;
};

float4 main(float2 grid : POSITION) : SV_Position {
  float2 xz = chunk_origin + grid * chunk_size;
  float2 uv = height_uv_origin + grid * height_uv_size;
  float y = g_height.SampleLevel(g_linear_clamp, uv, 0) * height_scale + height_offset;
  return mul(float4(xz.x, y, xz.y, 1.0), view_proj);
}
```

高さマップの端の画素の中心が、チャンクの端の頂点に合うように、`height_uv_origin` と `height_uv_size` を <strong>半画素分、内側に</strong>寄せます。そうしないと隣のチャンクと 高さが、半画素分ずれて継ぎ目が出ます。

## 格子の解像度と高さマップの解像度

格子の頂点の間隔と高さマップの画素の間隔を、<strong>同じ</strong>にするのが標準です（頂点 1 つに、画素 1 つ）。

| 関係 | 内容 |
| --- | --- |
| 頂点の方が粗い | 高さマップの、細かい凹凸がメッシュに反映されない（LOD の遠景ではこれが、普通） |
| 頂点の方が細かい | 高さマップを、補間して使う。余計な頂点が増えるだけ |
| 同じ | 1 頂点 = 1 画素。無駄がない |

遠景で頂点の方が粗くなる場合は、ミップを選んで読むことで、ちらつきを防ぎます（[Heightmap LOD (Mips)](../lod/height-mip.md)）。

## よくあるミス

??? failure "地形がカクカクして見える"
    <strong>頂点密度を上げる</strong>・法線を滑らかにする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 格子の頂点を、高さマップで持ち上げる

## 参考

- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（地形、ビュー フラスタム カリング、法線、補間の章）
- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps", Journal of Graphics, GPU, and Game Tools, Vol. 14, No. 4, 2009
- Forsyth, "Linear-Speed Vertex Cache Optimisation", 2006（頂点キャッシュに合わせた、インデックスの並べ替え）
- Microsoft Learn, "D3D11_RASTERIZER_DESC"（`FrontCounterClockwise`）

## 関連ページ

- [Heightmaps and Meshes](index.md)
- [LOD](../lod/index.md)
