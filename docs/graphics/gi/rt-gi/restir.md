---
title: ReSTIR GI
tags:
  - 描画
---

# ReSTIR GI

<strong>ReSTIR は、「良いサンプルを、隣の画素や前フレームから借りる」ことで、少ないレイでも、きれいな結果を出す手法</strong>です。<strong>重みつきリザーバー サンプリング</strong>を使い、サンプルを再利用します。このページでは、ReSTIR の考え方と効果を説明します。

!!! tip "ポイント"
    - リザーバーに、「良さそうなサンプル」を 1 つだけ保持する。
    - 隣の画素・前フレームのリザーバーと混ぜる（再利用）。
    - 再利用すると、実質のサンプル数が、桁違いに増える。
    - バイアスの管理（再利用してよいかの判定）が難しい。

<!-- fig:restir-reservoir:begin -->

<svg class="fig illust motion" data-fig="restir-reservoir" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-restir-reservoir" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ReSTIR: たくさんの光から、明るさに比例して 1 つだけ選ぶ(リザーバー)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">光 16 個のうち、影の光線を飛ばせるのは 1 本だけ。選び方で、結果のばらつきが大きく変わる</text>
<rect x="30" y="92" width="480" height="220" fill="#ffffff" stroke="#e5aa28" stroke-width="1.8" rx="6"/>
<text x="30" y="82" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">16 個の光(棒 = 影を無視した明るさ)</text>
<rect x="44.0" y="282.0" width="26.0" height="6.0" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/>
<text x="57.0" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">1</text>
<rect x="73.5" y="279.0" width="26.0" height="9.0" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/>
<text x="86.5" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">2</text>
<rect x="103.0" y="282.0" width="26.0" height="6.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
<text x="116.0" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">3</text>
<rect x="132.5" y="276.0" width="26.0" height="12.0" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/>
<text x="145.5" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">4</text>
<rect x="162.0" y="138.0" width="26.0" height="150.0" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/>
<text x="175.0" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">5</text>
<rect x="191.5" y="279.0" width="26.0" height="9.0" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/>
<text x="204.5" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">6</text>
<rect x="221.0" y="282.0" width="26.0" height="6.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
<text x="234.0" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">7</text>
<rect x="250.5" y="279.0" width="26.0" height="9.0" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/>
<text x="263.5" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">8</text>
<rect x="280.0" y="279.0" width="26.0" height="9.0" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/>
<text x="293.0" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">9</text>
<rect x="309.5" y="183.0" width="26.0" height="105.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
<text x="322.5" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">10</text>
<rect x="339.0" y="282.0" width="26.0" height="6.0" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/>
<text x="352.0" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">11</text>
<rect x="368.5" y="282.0" width="26.0" height="6.0" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/>
<text x="381.5" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">12</text>
<rect x="398.0" y="279.0" width="26.0" height="9.0" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/>
<text x="411.0" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">13</text>
<rect x="427.5" y="276.0" width="26.0" height="12.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
<text x="440.5" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">14</text>
<rect x="457.0" y="282.0" width="26.0" height="6.0" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/>
<text x="470.0" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">15</text>
<rect x="486.5" y="279.0" width="26.0" height="9.0" fill="#fbbf24" stroke="#f59e0b" stroke-width="1.5"/>
<text x="499.5" y="302.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">16</text>
<circle cx="50" cy="110" r="6" fill="#fbbf24"/>
<text x="60" y="114" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">光が届く</text>
<circle cx="121.6" cy="110" r="6" fill="#cbd5e1"/>
<text x="131.6" y="114" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">影になる(隠れている)</text>
<text x="44" y="136" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">正解 = 届く光の合計 = 8.0</text>
<rect x="130.5" y="272.0" width="30.0" height="20.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;0.0593;0.0595;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M145.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;0.0593;0.0595;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="455.0" y="278.0" width="30.0" height="14.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.0595;0.0724;0.0726;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M145.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.0595;0.0724;0.0726;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="307.5" y="179.0" width="30.0" height="113.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0724;0.0726;0.0854;0.0856;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M145.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0724;0.0726;0.0854;0.0856;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="455.0" y="278.0" width="30.0" height="14.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0854;0.0856;0.0984;0.0986;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M145.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0854;0.0856;0.0984;0.0986;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="42.0" y="278.0" width="30.0" height="14.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0984;0.0986;0.1114;0.1116;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M145.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0984;0.0986;0.1114;0.1116;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="425.5" y="272.0" width="30.0" height="20.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1114;0.1116;0.1245;0.1247;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M145.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1114;0.1116;0.1245;0.1247;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="189.5" y="275.0" width="30.0" height="17.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1245;0.1247;0.1375;0.1377;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M145.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1245;0.1247;0.1375;0.1377;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="42.0" y="278.0" width="30.0" height="14.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1375;0.1377;0.1505;0.1507;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M145.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1375;0.1377;0.1905;0.1907;1.0000" values="0;0;1;1;0;0"/></path>
<text x="560" y="130" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed" opacity="0">試行 1<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;0.1952;0.1953;1.0000" values="0;0;1;1;0;0"/></text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1505;0.1507;0.2045;0.2047;1.0000" values="0;0;1;1;0;0"/><text x="560" y="152" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">候補 8 個の合計 5.4 → 選んだ光 #4(届く)</text>
<text x="560" y="172" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">推定 = 10.8(正解 8.0)</text>
</g>
<rect x="484.5" y="275.0" width="30.0" height="17.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2045;0.2047;0.2175;0.2177;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M499.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2045;0.2047;0.2175;0.2177;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="484.5" y="275.0" width="30.0" height="17.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2175;0.2177;0.2305;0.2307;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M499.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2175;0.2177;0.2305;0.2307;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="278.0" y="275.0" width="30.0" height="17.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2305;0.2307;0.2435;0.2437;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M293.0,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2305;0.2307;0.2435;0.2437;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="248.5" y="275.0" width="30.0" height="17.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2435;0.2437;0.2566;0.2567;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M263.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2435;0.2437;0.2566;0.2567;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="278.0" y="275.0" width="30.0" height="17.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2566;0.2567;0.2696;0.2698;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M263.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2566;0.2567;0.2696;0.2698;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="307.5" y="179.0" width="30.0" height="113.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2696;0.2698;0.2826;0.2828;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M322.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2696;0.2698;0.2826;0.2828;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="396.0" y="275.0" width="30.0" height="17.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2826;0.2828;0.2956;0.2958;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M322.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2826;0.2828;0.2956;0.2958;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="396.0" y="275.0" width="30.0" height="17.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2956;0.2958;0.3087;0.3088;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M322.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2956;0.2958;0.3487;0.3488;1.0000" values="0;0;1;1;0;0"/></path>
<text x="560" y="196" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed" opacity="0">試行 2<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2045;0.2047;0.3533;0.3535;1.0000" values="0;0;1;1;0;0"/></text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3087;0.3088;0.3626;0.3628;1.0000" values="0;0;1;1;0;0"/><text x="560" y="218" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">候補 8 個の合計 5.6 → 選んだ光 #10(影)</text>
<text x="560" y="238" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">推定 = 0.0(正解 8.0)</text>
</g>
<rect x="248.5" y="275.0" width="30.0" height="17.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3626;0.3628;0.3756;0.3758;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M263.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3626;0.3628;0.3756;0.3758;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="425.5" y="272.0" width="30.0" height="20.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3756;0.3758;0.3887;0.3888;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M263.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3756;0.3758;0.3887;0.3888;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="189.5" y="275.0" width="30.0" height="17.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3887;0.3888;0.4017;0.4019;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M204.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3887;0.3888;0.4017;0.4019;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="248.5" y="275.0" width="30.0" height="17.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4017;0.4019;0.4147;0.4149;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M204.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4017;0.4019;0.4147;0.4149;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="71.5" y="275.0" width="30.0" height="17.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4147;0.4149;0.4277;0.4279;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M204.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4147;0.4149;0.4277;0.4279;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="366.5" y="278.0" width="30.0" height="14.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4277;0.4279;0.4407;0.4409;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M204.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4277;0.4279;0.4407;0.4409;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="425.5" y="272.0" width="30.0" height="20.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4407;0.4409;0.4538;0.4540;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M204.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4407;0.4409;0.4538;0.4540;1.0000" values="0;0;1;1;0;0"/></path>
<rect x="189.5" y="275.0" width="30.0" height="17.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4538;0.4540;0.4668;0.4670;1.0000" values="0;0;1;1;0;0"/></rect>
<path d="M204.5,312.0 l-8,-14 l16,0 z" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4538;0.4540;0.5068;0.5070;1.0000" values="0;0;1;1;0;0"/></path>
<text x="560" y="262" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed" opacity="0">試行 3<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3626;0.3628;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4668;0.4670;1.0000" values="0;0;1;1"/><text x="560" y="284" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">候補 8 個の合計 2.5 → 選んだ光 #6(届く)</text>
<text x="560" y="304" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">推定 = 5.0(正解 8.0)</text>
</g>
<rect x="30" y="332" width="900" height="168" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="322" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">2000 回ためしたときの、正解からのずれ(小さいほど良い)</text>
<text x="50" y="392" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">光を 1 つ、でたらめに選ぶ</text>
<rect x="420" y="372" width="1" height="28" fill="#e5484d" opacity="0.85"><animate attributeName="width" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5488;0.6233;1.0000" values="1;1;316.21;316.21"/></rect>
<text x="746.2090669161781" y="393" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">ずれ 243%<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6231;0.6233;1.0000" values="0;0;1;1"/></text>
<text x="50" y="446" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">ReSTIR: 8 個の候補から、明るさに比例して 1 つ選ぶ</text>
<rect x="420" y="426" width="1" height="28" fill="#2563eb" opacity="0.85"><animate attributeName="width" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5488;0.6233;1.0000" values="1;1;139.52;139.52"/></rect>
<text x="569.5201758483339" y="447" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">ずれ 107%<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6231;0.6233;1.0000" values="0;0;1;1"/></text>
<text x="50" y="485" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">ずれ = 2000 回の推定値の、二乗平均の平方根 ÷ 正解</text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光は 16 個。影の光線を飛ばせるのは 1 本だけ<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;1.0000" values="1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">候補を 1 つずつ受け取り、明るさに比例した確率で「選択中」を入れ替える<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;0.5487;0.5488;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="530" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">明るい光を選びやすいので、同じ 1 本でも、ばらつきが大幅に減る<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5487;0.5488;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:restir-reservoir:end -->

## ReSTIR GI

<strong>ReSTIR</strong>（Reservoir-based Spatiotemporal Importance Resampling）は、<strong>「良いサンプルを近い画素や前フレームから借りる」</strong>ことで、1 画素あたりの有効なサンプル数を、桁違いに増やす手法です。2020 年に Bitterli らが直接光（ReSTIR DI）で提案し、2021 年に Ouyang らが間接光（ReSTIR GI）へ拡張しました。ここでは、手法の背景から順に、仕組みを組み立てます。

### 出発点：サンプルを賢く選びたい

レイトレ GI のノイズの根本原因は、<strong>「寄与の大きいサンプルを引き当てる確率が低い」</strong>ことです。画素の周りの半球に、ランダムにレイを 1 本飛ばしても、明るい壁や光源に当たる確率は小さく、大半のレイは暗い場所に当たって、ほとんど寄与しません。たまに明るい所に当たる画素と、当たらない画素が混在して、ノイズになります。

もし「どの方向のサンプルが寄与が大きいか」が事前に分かっていれば、その方向だけを選べばよいのですが、それは答えを知っているのと同じで、不可能です。そこで、<strong>安いサンプルを大量に作り、その中から質の良いものを選ぶ</strong>という考え方が出てきます。

### RIS：候補を作って、良いものを選ぶ

<strong>RIS</strong>（Resampled Importance Sampling、Talbot ら 2005）は、まず M 個の候補サンプルを、簡単な分布（たとえば BRDF に従う方向）で作ります。次に、各候補の「良さ」を、安く計算できる<strong>目標関数</strong> p̂ で評価します。ReSTIR GI では、p̂ は、そのサンプルの寄与の大きさ（反射光の輝度）です。そして、p̂ に比例する確率で、M 個の中から 1 個を選びます。選ばれたサンプルには、補正の重みが付きます。

ポイントは、<strong>候補の評価（p̂ の計算）はレイトレースを必要としない</strong>ことです。レイを飛ばさなくても、サンプルがすでにどこに当たるか分かっていれば、その寄与は計算できます。したがって、M を増やしても、コストの増え方が小さいまま、質の良い 1 個を選べます。

### リザーバー：1 個だけ覚えておく

RIS で M 個の候補を、画素ごとに全部保存すると、メモリが膨大です。そこで、<strong>重み付きリザーバー サンプリング</strong>（Chao 1982）を使います。候補を 1 個ずつ処理しながら、「今までで選ばれたサンプル 1 個」と「重みの合計」だけを覚えておけば、最終的に RIS と同じ分布のサンプルが得られる、という仕組みです。このデータの入れ物を<strong>リザーバー</strong>と呼びます。

```hlsl
struct Reservoir {
  Sample sample;
  float w_sum;
  float m;
};

void Update(inout Reservoir r, Sample s, float weight, float u) {
  r.w_sum += weight;
  r.m += 1.0;
  if (u * r.w_sum < weight) {
    r.sample = s;
  }
}
```

新しい候補が来るたびに、`weight / w_sum` の確率でサンプルを入れ替えます。早く来た候補ほど、後から置き換えられる確率が高くなるので、結果的に全候補が、重みに比例する確率で選ばれます。リザーバーのサイズは、サンプル 1 個分に固定で、M がいくつでも変わりません。

### 再利用：リザーバー同士をマージする

ReSTIR の核心は、リザーバー同士を<strong>マージ</strong>できることです。隣の画素のリザーバーは、「その画素の M 個の候補から選ばれた 1 個」を持っています。この 1 個を、自分のリザーバーの候補として投入すれば、あたかも<strong>相手の M 個の候補をすべて見たかのように</strong>、サンプルを選べます。実際に追加でレイを飛ばす必要はありません。

<strong>時間的な再利用</strong>では、前フレームの同じ位置（動きベクトルで再投影）のリザーバーとマージします。毎フレーム、前フレームまでの全サンプル履歴を引き継ぐので、静止していればサンプル数は雪だるま式に増えます。<strong>空間的な再利用</strong>では、近隣（例：半径 30 画素以内）の数画素のリザーバーとマージします。隣の画素は、自分と似た環境にいるので、良いサンプルは自分にとっても良いサンプルである可能性が高いからです。

履歴が増えすぎて、古いサンプルばかりになると、変化への追従が遅れます。そのため、リザーバーの M に上限を設け（例：現在のフレームの 20 倍まで）、古い情報を徐々に薄めます。

### ReSTIR GI のサンプルとは何か

直接光の ReSTIR DI では、サンプルは「ライト上の 1 点」でした。間接光の ReSTIR GI では、サンプルは<strong>「画素から飛ばしたレイが最初に当たった点（二次ヒット点）とその点の情報」</strong>です。具体的には、二次ヒット点の位置 x₂、法線 n₂、そしてその点から画素の方向に出る放射輝度 L₂（直接光とキャッシュから得た間接光）を保存します。

このサンプルは、隣の画素が使うときに、<strong>そのまま再利用</strong>できます。隣の画素の視点位置 x₁' から、同じ二次ヒット点 x₂ へ向かう新しい経路を作り、その経路の寄与を、x₂ に保存された L₂ を使って計算します。これを<strong>再接続</strong>（reconnection）と呼びます。新たにレイトレースをしなくても（可視性の確認 1 回を除いて）、他の画素のサンプルを自分用の経路に変換できます。

### バイアスの管理：ヤコビアンと可視性

再利用で気をつけるのは、<strong>隣の画素のサンプルを、そのまま自分のサンプルとして扱うと、確率密度がずれる</strong>ことです。隣の画素から見た二次ヒット点の方向と、自分から見た方向は、一般に違うので、同じ点を選ぶ確率が違います。この確率密度の差を補正するのが、<strong>ヤコビアン</strong>（方向の測度から面積の測度への変換係数）です。ヤコビアンは、二次ヒット点までの距離と、二次ヒット点の法線と各視点方向のなす角の余弦から計算できます。

もう 1 つの補正は、<strong>可視性</strong>です。隣の画素から見えた二次ヒット点が、自分からは壁の裏に隠れて見えないことがあります。そのままだと、壁の向こうの光が漏れます。そこで、再接続の経路について、シャドウ レイを 1 本飛ばして、遮蔽されていれば、そのサンプルを捨てます。この 1 本のレイは安いので、全体のコストにはあまり響きません。

さらに、法線や深度が大きく違う画素のリザーバーは、そもそも再利用しません。これらの条件を満たさないサンプルを混ぜると、画面に不自然なにじみが出るからです。ヤコビアンと可視性の補正をきちんと入れる方式を<strong>不偏</strong>（unbiased）、入れずに近似する方式を<strong>偏りあり</strong>（biased）と呼びます。不偏のほうが正確ですが重く、実際の製品では、見た目に影響が出ない範囲で近似するのが普通です。

### 最終的なシェーディング

リザーバーに入っているサンプルと重みから、画素の間接光を計算します。ReSTIR 後のノイズは、通常の 1 画素 1 レイに比べて桁違いに小さくなりますが、まだ多少残るので、通常のデノイザーを軽く掛けて仕上げます。

### 発展と実装

ReSTIR は、DI（直接光）から GI（間接光）、さらに <strong>ReSTIR PT</strong>（Lin ら 2022、パス全体の再利用）へと発展しています。NVIDIA の RTXDI（直接光）や RTXGI などに採用され、商用エンジンへの組み込みも進んでいます。実装は複雑で、パラメータが多く（候補数、空間再利用の半径と数、M の上限、バイアス補正の方式）、デバッグも難しい手法です。まずは、時間的な再利用だけを実装して、効果を確かめるところから始めるのがよいでしょう。

## よくあるミス

??? failure "再利用が強すぎて、光が不自然ににじむ"
    <strong>法線・深度が合わないサンプルは再利用しない</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 良いサンプルを借りて、少ないレイで高品質
    - [x] バイアスの管理が、鍵

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Ray-Traced GI](index.md)
- [Fighting Noise](noise.md)
- [Choosing a Method](choosing.md)
