---
title: SSGI
tags:
  - 描画
---

# SSGI

<strong>SSGI</strong>（Screen-Space Global Illumination、画面空間 GI）は <strong>[SSAO](../ao/ssao-hemisphere.md) と同じ発想</strong>を、<strong>「暗さ」だけでなく「光（色）」にまで広げた</strong>ものです。<strong>画素の周りの半球にレイを飛ばし</strong>（深度バッファ上で）、<strong>当たった画素の「色（その画素の出射光）」</strong>を、間接光として集めます。事前計算が不要で動く物・動くライトも自動的に反映されます。ただし、画面に映っているものしか見えないという画面空間の限界があります。

!!! tip "ポイント"
    - <strong>画素から半球方向にレイ</strong>を飛ばし（<strong>深度バッファ上</strong>）、<strong>当たった点の色</strong>を<strong>間接光</strong>として<strong>平均</strong>。
    - <strong>SSAO は「遮られた量」</strong>、<strong>SSGI は「当たった先の色」</strong>。
    - <strong>前フレームの最終画像（ライティング済み）</strong>を<strong>光源として使う</strong>と<strong>多バウンス</strong>が<strong>ほぼ無料</strong>で得られる。
    - <strong>少ないレイ ＋ ノイズ ＋ デノイズ（時間・空間）</strong>が<strong>必須</strong>。
    - 限界：<strong>画面外・裏側・隠れた面</strong>は<strong>見えない</strong>。<strong>画面端でゲインが変わる</strong>。
    - <strong>他の GI（プローブ等）の補助</strong>として、<strong>近距離の細かい間接光</strong>を足す使い方が多い。

## 原理

<strong>SSAO</strong>は<strong>半球に飛ばしたレイが「遮られたか」</strong>だけを見ました。<strong>SSGI</strong>は<strong>レイが当たった画素の「光（色）」</strong>を読みます。

| 項目 | SSAO | SSGI |
| --- | --- | --- |
| レイの結果 | <strong>遮られた（0/1）</strong> | <strong>当たった点の色（RGB）</strong> |
| 出力 | <strong>暗さ（スカラー）</strong> | <strong>間接光（RGB）</strong> |
| 色の効果 | なし | カラー ブリーディング |

<!-- fig:ssgi-bounce:begin -->

<svg class="fig illust motion" data-fig="ssgi-bounce" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-ssgi-bounce" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">SSGI: 画面に見えている色を、周りの画素から集めて、壁の色が床へ「にじむ」</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。右に赤い壁、床は灰色。床の 1 画素が、周りの見える画素(の明るさと色)を 16 個サンプルして集める</text>
<rect x="30" y="96" width="840" height="150" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 断面</text>
<rect x="660.0" y="130.0" width="19.0" height="96.0" fill="#e62e26"/>
<rect x="680.0" y="130.0" width="19.0" height="96.0" fill="#e62e26"/>
<rect x="700.0" y="130.0" width="19.0" height="96.0" fill="#e62e26"/>
<rect x="720.0" y="130.0" width="19.0" height="96.0" fill="#e62e26"/>
<rect x="740.0" y="130.0" width="19.0" height="96.0" fill="#e62e26"/>
<rect x="760.0" y="130.0" width="19.0" height="96.0" fill="#e62e26"/>
<rect x="780.0" y="130.0" width="19.0" height="96.0" fill="#e62e26"/>
<rect x="800.0" y="130.0" width="19.0" height="96.0" fill="#e62e26"/>
<rect x="820.0" y="130.0" width="19.0" height="96.0" fill="#e62e26"/>
<rect x="840.0" y="130.0" width="19.0" height="96.0" fill="#e62e26"/>
<line x1="60.0" y1="226.0" x2="860.0" y2="226.0" stroke="#94a3b8" stroke-width="3"/>
<circle cx="590.0" cy="225.52" r="7" fill="#1f2937"/>
<text x="590.0" y="244.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">調べる画素</text>
<path d="M470.0,226.0 A120.0,144.0 0 0 1 710.0,226.0" fill="none" stroke="#93c5fd" stroke-width="2" stroke-dasharray="5 4"/>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="637.77" y2="219.87" stroke="#86efac" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="637.77" cy="219.87" r="4.5" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0657;0.0659;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="678.52" y2="193.3" stroke="#e5484d" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="678.52" cy="193.3" r="4.5" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0827;0.0829;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="647.32" y2="188.75" stroke="#86efac" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="647.32" cy="188.75" r="4.5" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0998;0.1000;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="674.64" y2="142.16" stroke="#e5484d" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="674.64" cy="142.16" r="4.5" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1169;0.1171;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="642.02" y2="149.46" stroke="#86efac" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="642.02" cy="149.46" r="4.5" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1340;0.1341;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="615.69" y2="167.85" stroke="#86efac" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="615.69" cy="167.85" r="4.5" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1510;0.1512;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="618.74" y2="111.85" stroke="#86efac" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="618.74" cy="111.85" r="4.5" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1681;0.1683;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="597.01" y2="140.15" stroke="#86efac" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="597.01" cy="140.15" r="4.5" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.1852;0.1854;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="578.63" y2="87.01" stroke="#86efac" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="578.63" cy="87.01" r="4.5" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2022;0.2024;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="564.31" y2="123.91" stroke="#86efac" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="564.31" cy="123.91" r="4.5" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2193;0.2195;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="561.25" y2="160.98" stroke="#86efac" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="561.25" cy="160.98" r="4.5" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2364;0.2366;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="523.08" y2="127.67" stroke="#86efac" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="523.08" cy="127.67" r="4.5" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2535;0.2537;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="529.72" y2="166.15" stroke="#86efac" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="529.72" cy="166.15" r="4.5" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2705;0.2707;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="545.48" y2="196.96" stroke="#86efac" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="545.48" cy="196.96" r="4.5" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2876;0.2878;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="499.11" y2="192.44" stroke="#86efac" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="499.11" cy="192.44" r="4.5" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3047;0.3049;1.0000" values="0;0;1;1"/><line x1="590.0" y1="225.52" x2="522.85" y2="217.58" stroke="#86efac" stroke-width="1.2" stroke-dasharray="3 3"/>
<circle cx="522.85" cy="217.58" r="4.5" fill="#2ea043"/>
</g>
<text x="40" y="276" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">サンプル 16 個のうち、赤い壁に当たったのは 2 個</text>
<text x="40" y="302" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">色のにじみなし(直接光だけ)</text>
<rect x="60.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3610" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="80.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3629" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="100.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3649" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="120.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3668" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="140.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3688" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="160.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3707" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="180.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3727" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="200.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3746" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="220.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3766" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="240.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="260.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3805" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="280.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3824" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="300.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3844" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="320.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3863" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="340.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3883" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="360.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3902" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="380.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3922" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="400.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3941" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="420.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3961" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="440.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3980" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="460.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4000" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="480.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4020" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="500.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4039" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="520.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4059" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="540.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4078" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="560.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4098" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="580.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4117" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="600.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4137" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="620.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4156" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="640.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4176" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="660.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4195" values="#e5e7eb;#cf2922"/></rect>
<rect x="680.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4215" values="#e5e7eb;#cf2922"/></rect>
<rect x="700.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4234" values="#e5e7eb;#cf2922"/></rect>
<rect x="720.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4254" values="#e5e7eb;#cf2922"/></rect>
<rect x="740.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4273" values="#e5e7eb;#cf2922"/></rect>
<rect x="760.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4293" values="#e5e7eb;#cf2922"/></rect>
<rect x="780.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4312" values="#e5e7eb;#cf2922"/></rect>
<rect x="800.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4332" values="#e5e7eb;#cf2922"/></rect>
<rect x="820.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4351" values="#e5e7eb;#cf2922"/></rect>
<rect x="840.0" y="306.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4371" values="#e5e7eb;#cf2922"/></rect>
<rect x="60.0" y="306" width="800.0" height="20.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="40" y="346" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">SSGI(16 サンプル)</text>
<rect x="60.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4683" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="80.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="100.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4722" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="120.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4741" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="140.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4761" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="160.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4780" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="180.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4800" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="200.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4820" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="220.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4839" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="240.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4859" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="260.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4878" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="280.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="300.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4917" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="320.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4937" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="340.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4956" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="360.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4976" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="380.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4995" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="400.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5015" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="420.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5034" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="440.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5054" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="460.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5073" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="480.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5093" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="500.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5112" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="520.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5132" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="540.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5151" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="560.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5171" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="580.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5190" values="#e5e7eb;#c7bbb5"/></rect>
<rect x="600.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5210" values="#e5e7eb;#dbbfb9"/></rect>
<rect x="620.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5229" values="#e5e7eb;#dcbfb9"/></rect>
<rect x="640.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5249" values="#e5e7eb;#ebc2bb"/></rect>
<rect x="660.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5268" values="#e5e7eb;#cf2922"/></rect>
<rect x="680.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5288" values="#e5e7eb;#cf2922"/></rect>
<rect x="700.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5307" values="#e5e7eb;#cf2922"/></rect>
<rect x="720.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5327" values="#e5e7eb;#cf2922"/></rect>
<rect x="740.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5346" values="#e5e7eb;#cf2922"/></rect>
<rect x="760.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5366" values="#e5e7eb;#cf2922"/></rect>
<rect x="780.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5385" values="#e5e7eb;#cf2922"/></rect>
<rect x="800.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5405" values="#e5e7eb;#cf2922"/></rect>
<rect x="820.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5424" values="#e5e7eb;#cf2922"/></rect>
<rect x="840.0" y="350.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5444" values="#e5e7eb;#cf2922"/></rect>
<rect x="60.0" y="350" width="800.0" height="20.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="40" y="390" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">正解(細かい光線 180 本)</text>
<rect x="60.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5756" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="80.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5776" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="100.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5795" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="120.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5815" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="140.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5834" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="160.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5854" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="180.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5873" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="200.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5893" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="220.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5912" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="240.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5932" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="260.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5951" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="280.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5971" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="300.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5990" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="320.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6010" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="340.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6029" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="360.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6049" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="380.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6068" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="400.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6088" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="420.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6107" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="440.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6127" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="460.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6146" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="480.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6166" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="500.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6185" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="520.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6205" values="#e5e7eb;#b8b8b3"/></rect>
<rect x="540.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6224" values="#e5e7eb;#bfb9b4"/></rect>
<rect x="560.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6244" values="#e5e7eb;#ccbcb6"/></rect>
<rect x="580.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6263" values="#e5e7eb;#d4bdb8"/></rect>
<rect x="600.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6283" values="#e5e7eb;#debfb9"/></rect>
<rect x="620.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6302" values="#e5e7eb;#edc2bc"/></rect>
<rect x="640.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6322" values="#e5e7eb;#ffc6bf"/></rect>
<rect x="660.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6341" values="#e5e7eb;#cf2922"/></rect>
<rect x="680.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6361" values="#e5e7eb;#cf2922"/></rect>
<rect x="700.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6380" values="#e5e7eb;#cf2922"/></rect>
<rect x="720.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6400" values="#e5e7eb;#cf2922"/></rect>
<rect x="740.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6420" values="#e5e7eb;#cf2922"/></rect>
<rect x="760.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6439" values="#e5e7eb;#cf2922"/></rect>
<rect x="780.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6459" values="#e5e7eb;#cf2922"/></rect>
<rect x="800.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6478" values="#e5e7eb;#cf2922"/></rect>
<rect x="820.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6498" values="#e5e7eb;#cf2922"/></rect>
<rect x="840.0" y="394.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6517" values="#e5e7eb;#cf2922"/></rect>
<rect x="60.0" y="394" width="800.0" height="20.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="40" y="450" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">サンプル数(画素あたり):</text>
<text x="250" y="450" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">SSGI 16 個 / 正解 180 本</text>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.7071;0.7073;1.0000" values="0;0;1;1"/><rect x="40" y="462" width="860" height="56" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="486" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">壁に近い床へ、赤い色がにじむ。正解とのずれ(平均): にじみなし 0.013 → SSGI 0.005</text>
<text x="56" y="510" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">画面に見えていない物(壁の裏・画面の外)の色は、集められない</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">床の画素が、周りの見える画素の色を集める<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">半円の中に、16 個のサンプルを撒き、壁に当たったら、その色を足す<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;0.3608;0.3610;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">全部の画素で繰り返すと、壁の近くの床が、赤みを帯びる<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3608;0.3610;0.7071;0.7073;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">細かい光線の正解に、近い色になる(サンプルが少ないとノイズが出る)<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.7071;0.7073;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:ssgi-bounce:end -->

### 手順

| 手順 | 内容 |
| --- | --- |
| ① サンプル方向の生成 | 画素の法線を中心とする半球で、余弦重み付きのランダムな方向 |
| ② 画面空間のレイマーチ | 深度バッファ上でレイを進める（[SSR](../reflections/ssr-basics/index.md) や [Hi-Z](../reflections/ssr-hiz.md) と同じ） |
| ③ ヒット判定 | レイの深度が深度バッファの奥に入ったら、ヒット |
| ④ 色を読む | ヒット画素の出射光（前フレームの最終色）を読む |
| ⑤ 平均 | 全レイの色を平均して、間接光 |

```hlsl
float3 SSGI(float3 view_pos, float3 view_normal, float2 pixel) {
  float3 sum = 0.0;
  [loop] for (int i = 0; i < kRayCount; ++i) {
    float3 dir = CosineSampleHemisphere(view_normal, Hash(pixel, i));
    float2 hit_uv;
    float hit_depth;
    if (ScreenSpaceTrace(view_pos, dir, hit_uv, hit_depth)) {
      float3 radiance = prev_frame_color.SampleLevel(linear_sampler, hit_uv, 0).rgb;
      sum += radiance;
    }
  }
  return sum / kRayCount;
}
```

コードの要点です。`prev_frame_color` は前フレームの最終的な画像（ライティング済み、ポストプロセス前）で間接光も含んでいるので多バウンスになります。余弦重み付きのサンプルは `(n·ω)/pdf` が定数になり、単純な平均で済みます。`ScreenSpaceTrace` は画面空間のレイマーチです（[SSR](../reflections/ssr-basics/index.md)、[Hi-Z トレース](../reflections/ssr-hiz.md)）。

## 多バウンスの得かた

<strong>前フレームの最終画像に前フレームの SSGI の結果が含まれている</strong>ので、<strong>フレームを重ねるごとに</strong>、バウンスが増えるように見えます。

バウンス数は何を読むかで決まります。現在のフレームの直接光だけを読めば、1 バウンスです。前フレームの最終画像（間接光を含む）を読めば、フレームごとに 1 バウンスずつ蓄積するので、多バウンスが無料で得られます。注意すべきはゲインが 1 を超えると発散する（明るくなり続ける）ことです。必ず 1 未満の減衰を掛けます。

## ノイズとデノイズ

<strong>画素あたり 1〜数本</strong>のレイでは、<strong>ノイズ</strong>が非常に目立ちます。

| 手法 | 内容 |
| --- | --- |
| 時間蓄積 | 前フレームの結果を再投影して混ぜる（動きのベクトルが必要） |
| 空間フィルタ | バイラテラル・À-trousで法線・深度を手がかりにエッジを保ってぼかす |
| 半分の解像度 | 半解像度で計算し、バイラテラル アップサンプル |
| ブルー ノイズ | ノイズの質を良くする（ブルー ノイズ・IGN） |
| TAA との併用 | TAA が時間方向の平均を取る |


ノイズが大きいので時間蓄積と空間フィルタの組み合わせは、ほぼ必須です。

ノイズが大きいので時間蓄積と空間フィルタの組み合わせは、ほぼ必須です。

<strong>ノイズが大きい</strong>ので<strong>時間蓄積と空間フィルタ</strong>の組み合わせが、ほぼ必須です。

## 画面空間の限界

| 限界 | 内容 |
| --- | --- |
| 画面外の光源・面 | 見えないので間接光に寄与しない。カメラの向きで明るさが変わる |
| 隠れた面の裏側 | 深度バッファは、一番手前の面だけ。裏側・遮蔽物の向こうは不明 |
| 画面端 | サンプルが画面外へ出るので端で暗くなる（フェードが必要） |
| 厚み | 薄い物の背後を通過できない／遠くの面の手前を、誤ってヒット |
| 視点依存 | カメラを動かすと間接光が変わって見える（破綻） |


そのため、SSGI 単体では安定した GI になりません。プローブやライトマップなどのベースの GI に、近距離の細かい間接光とカラー ブリーディングを足す使い方が、一般的です。

そのため、SSGI 単体では安定した GI になりません。プローブやライトマップなどのベースの GI に、近距離の細かい間接光とカラー ブリーディングを足す使い方が、一般的です。

<strong>そのため SSGI 単体で安定した GI にはなりません</strong>。<strong>プローブやライトマップなどの、ベースの GI</strong>に近距離の細かい間接光・カラー ブリーディングを足す使い方が、一般的です。

## コストと工夫

| 項目 | 内容 |
| --- | --- |
| レイ数 | 画素あたり 1〜4 本。多いほどきれい・重い |
| レイの距離 | 短いほど安い（近距離のみ） |
| 半解像度 | 計算量を 1/4 |
| Hi-Z トレース | 遠くまで少ないステップで |
| 法線・深度の事前フィルタ | ノイズ低減に有利 |

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| 事前計算が不要（動く物・動くライトを反映） | 画面にあるものしか見えない |
| 実装が比較的簡単（SSAO・SSR の拡張） | ノイズ・デノイズが必須 |
| カラー ブリーディングが出る | 視点依存（カメラで変わる） |
| 多バウンスがほぼ無料 | 画面外の光源が効かない |
| 他の GI の補助として良い | 単独では安定しない |


### より良いやり方

SSGI の弱点は「画面外が見えない」の一点に集約されます。そのため、より良い設計は SSGI を単独で使わずに、<strong>見えなかった分を別の GI に任せる</strong>ことです。レイが画面外に出たり深度バッファで当たらなかったりしたとき、その方向の光をライト プローブや DDGI のような世界空間の GI から読みます。つまり、<strong>SSGI は近距離の細部を担当し、遠くと画面外は世界空間の GI が担当する</strong>階層にします。Lumen が画面空間トレースを最初の手段として使い、外れたら距離場、さらに外れたらワールド プローブ、と順に落ちていく設計はまさにこの考え方です（[Lumen-Style Approaches](rt-gi/lumen-style.md)）。

### より良いやり方

SSGI の弱点は「画面外が見えない」の一点に集約されます。そのため、より良い設計は SSGI を単独で使わずに、<strong>見えなかった分を別の GI に任せる</strong>ことです。レイが画面外に出たり深度バッファで当たらなかったりしたとき、その方向の光をライト プローブや DDGI のような世界空間の GI から読みます。つまり、<strong>SSGI は近距離の細部を担当し、遠くと画面外は世界空間の GI が担当する</strong>階層にします。Lumen が画面空間トレースを最初の手段として使い、外れたら距離場、さらに外れたらワールド プローブ、と順に落ちていく設計はまさにこの考え方です（[Lumen-Style Approaches](rt-gi/lumen-style.md)）。

## 画面の情報だけで間接光を求める

<strong>SSGI</strong>（Screen-Space Global Illumination）は、<strong>画面に映っている情報</strong>（色、深度、法線）だけを使って間接光を近似する方法です（Ritschel ら、2009）。シーンの形状を持たず G バッファと、深度バッファだけでポスト プロセスとして、実行できるので導入が簡単です。

## 基本の考え方

<strong>各画素</strong>から <strong>半球のランダムな、方向</strong>に画面空間でレイを飛ばし（レイマーチ）、当たった画素の色をその方向から、来る光として集めます。

```text
画素 P から、法線の側の半球へ、ランダムな方向にレイを飛ばす（画面空間で、深度バッファを、辿る）
        ↓ 当たった画素 Q の「ライティング済みの色」を、P に届く光として、足す
```

<strong>当たった画素 Q</strong> は <strong>すでに、ライティングされた画面の色</strong>（直接光 + 前フレームの、間接光）です。Q の色が P を照らすので 1 回の、バウンスの間接光が得られます。

## 画面空間のレイマーチ

```hlsl
// 画素 P から、方向 dir へ、画面空間で、レイを進めて、最初に交わった画素の色を返す（交わらなければ、false）。
bool TraceScreenSpace(float3 origin_vs, float3 dir_vs, float2 pixel, out float3 hit_color) {
  const int kSteps = 16;
  float step_len = g_ssgi_max_distance / kSteps;
  float jitter = InterleavedGradientNoise(pixel);                      // 開始を、ずらして、縞を消す
  hit_color = 0;
  for (int i = 0; i < kSteps; ++i) {
    float3 p_vs = origin_vs + dir_vs * ((i + jitter) * step_len);      // ビュー空間での、レイ上の点
    float4 clip = mul(float4(p_vs, 1.0), g_proj);
    float2 uv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;
    if (any(uv < 0.0) || any(uv > 1.0)) return false;                  // 画面の外 → 情報がない
```

<strong>ビュー空間でレイを進め</strong>、各点を <strong>画面の uv に投影</strong>します。画面の外に出たら情報が無いので、打ち切ります。

```hlsl
    float scene_depth = g_depth.SampleLevel(g_point_clamp, uv, 0);     // その画素の、深度（ビュー空間の、距離）
    float ray_depth = -p_vs.z;                                          // レイ上の点の、深度（右手系は、前方が -Z）
    float diff = ray_depth - scene_depth;
    if (diff > 0.0 && diff < g_thickness) {                             // レイが、面の「裏」に入った（交差した）。厚み以内なら、当たりとする。
      hit_color = g_lit_scene.SampleLevel(g_linear_clamp, uv, 0).rgb;   // 当たった画素の、ライティング済みの色
      return true;
    }
  }
  return false;
}
```

<strong>レイ上の点の深度</strong>が <strong>その画素の、深度より奥</strong>（`diff > 0`）になった瞬間が面との、交差です。厚み（`g_thickness`）の範囲内なら当たりと、みなします（薄い物の裏を通り抜けるのを、避けるため。[Thickness](../reflections/ssr-basics/thickness.md)）。当たった画素のライティング済みの色（`g_lit_scene`）を、間接光として使います。

## 間接光を積算する

```hlsl
float3 SSGI(float2 pixel, float3 position_vs, float3 normal_vs, float3 albedo) {
  float3 sum = 0.0;
  const int kRays = 2;                                                  // 1 画素あたりの、レイ（少なく。デノイズで補う）
  for (int k = 0; k < kRays; ++k) {
    float2 u = Random2(pixel, g_frame_index * kRays + k);
    float3 dir = LocalToWorld(CosineHemisphere(u.x, u.y), normal_vs);   // 余弦重みづけ（[Monte Carlo Integration]）
    float3 hit_color;
    if (TraceScreenSpace(position_vs + normal_vs * 0.02, dir, pixel, hit_color)) {
      sum += hit_color;                                                  // 当たった → その色が、光
    } else {
      sum += g_sky_ambient;                                              // 当たらない → 空の環境光で、補う（画面の外は、不明）
    }
  }
  return albedo * sum / kRays;                                           // 余弦重みづけなので、albedo × 平均
}
```

<strong>余弦重みづけのサンプリング</strong>（[Monte Carlo Integration](theory/monte-carlo.md)）で、<strong>拡散の間接光</strong>は当たった色の、平均 × アルベドになります。当たらなかった（画面の外、遠すぎる）場合は空の環境光など、フォールバックで補います。

## 時間方向の蓄積とフィルタ

<strong>1 画素あたり 1〜2 本の、レイ</strong>では <strong>ノイズだらけ</strong>です。時間蓄積と空間フィルタでなめらかに、します（[Fighting Noise](rt-gi/noise.md)）。前のフレームの結果と混ぜ法線・深度が近い、画素どうしでぼかします。

## SSGI の問題

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| 画面の外の光が使えない | 画面に、映っていない光源・壁は間接光に、反映されない。カメラを動かすと明るさが変わる（画面の端で光が、出入りする） | フォールバック（ライト プローブ、空の環境光）。画面を少し広く描く |
| 隠れた面が使えない | 手前の物の裏は、見えていないので反射光が出ない | 深度の厚みを仮定。限界として許容 |
| 遠くの光は使えない | レイの、最大距離を短く（数 m）。遠くからの間接光は無い | プローブ GI などと、併用 |
| ノイズ | 少ないレイ | 時間蓄積 + 空間フィルタ |
| コスト | 画面解像度に、比例 | 半分の解像度で計算して、アップサンプル |

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 導入が簡単（ポスト プロセス）。シーンの形状・事前計算が不要 |
| 長所 | 完全に動的（動く物、動くライトも反映） |
| 長所 | レイトレーシング ハードウェアが、不要 |
| 短所 | 画面の外の情報が、無い（カメラを動かすとちらつく） |
| 短所 | 単独では不十分。他の手法（プローブ、ライトマップ）と併用が前提 |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| 補助（近距離の間接光、色のにじみ） | 向く（プローブ GI の、細かい部分を補う） |
| GI の主役 | 向かない（画面の外の情報が、無い） |
| ハードウェア RT がない環境の、動的な GI | 選択肢の 1 つ（他の手法と、併用） |

## よくあるミス

??? failure "画面端で、間接光が急に暗くなる"
    <strong>画面端付近をフェード</strong>させる・<strong>ベースの GI にフォールバック</strong>します。

??? failure "前フレームの色を、再投影せずに読んで動くとずれる"
    <strong>動きのベクトル</strong>で<strong>再投影</strong>します。

??? failure "前フレーム色を、減衰なしで読み続けて発散して明るくなる"
    <strong>減衰</strong>（1 未満）を掛けます。

??? failure "ノイズが残って、チラつく"
    <strong>時間蓄積 ＋ 空間フィルタ</strong>を強め、<strong>ブルー ノイズ</strong>を使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SSGI ＝ <strong>SSAO の拡張</strong>。<strong>半球レイが当たった画素の「色」</strong>を、<strong>間接光</strong>として集める
    - [x] <strong>前フレームの最終画像</strong>を光源にすると、<strong>多バウンスがほぼ無料</strong>
    - [x] <strong>少ないレイ ＋ 時間・空間デノイズ</strong>が<strong>必須</strong>
    - [x] <strong>画面外・裏側は見えない</strong>。<strong>視点依存</strong>。<strong>単独は不安定</strong>
    - [x] <strong>ベースの GI ＋ SSGI（近距離の補助）</strong>が実用的

## 参考

- Ritschel, Grosch, Seidel, "Approximating Dynamic Global Illumination in Image Space", Symposium on Interactive 3D Graphics and Games 2009（スクリーン スペースの、間接光）
- Stachowiak, "Stochastic All The Things: Raytracing in Hybrid Real-Time Rendering", Digital Dragons 2018（SEED のハイブリッド レイトレーシング）
- Schied, Kaplanyan, Wyman, Patney, Chaitanya, Burgess, Liu, Dachsbacher, Lefohn, Salvi, "Spatiotemporal Variance-Guided Filtering: Real-Time Reconstruction for Path-Traced Global Illumination", High-Performance Graphics 2017（SVGF）
- McGuire, Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014

## 関連ページ

- [Global Illumination (GI)](index.md)
- [GI Theory](theory/index.md)
- [SSAO](../ao/ssao-hemisphere.md)
- [SSR Basics](../reflections/ssr-basics/index.md)
- [Hi-Z SSR](../reflections/ssr-hiz.md)
- [AO Filtering](../ao/filtering/index.md)
