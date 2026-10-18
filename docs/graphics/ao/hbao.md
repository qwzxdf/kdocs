---
title: HBAO
tags:
  - 描画
---

# HBAO

**HBAO**（Horizon-Based Ambient Occlusion）は、2008 年に NVIDIA の Bavoil らが発表した方式です。これまでの SSAO が、**ランダムな点を置いて「遮られているか」を数えた**（モンテカルロ法）のに対し、HBAO は**方向を決めて、その方向に深度バッファを歩き、「遮蔽が始まる角度（地平線＝ホライゾン）」を見つけ**て、**その間の角度を式で積分**します。**サンプルを点でなく、「線」で扱う**ので**少ないサンプルでもノイズが小さく**なります。

!!! tip "ポイント"
    - 画素の周りを<strong>N 個の方向（スライス）</strong>に分け、<strong>各方向に深度バッファを数ステップ歩く</strong>。
    - 各方向で<strong>「地平線の角度 h（一番高く見える遮蔽物）」</strong>と、<strong>「面自身の傾き（接線角 t）」</strong>を求める。
    - その方向の遮蔽は、<strong>sin h − sin t</strong>（h と t の間の角度の、積分）。<strong>全方向で平均</strong>したものが AO。
    - <strong>点を数えるのでなく、角度を積分する</strong>ので<strong>少ないサンプルで滑らか</strong>。
    - <strong>距離の減衰 W(r)</strong>を掛けて、遠い遮蔽を弱める。
    - 弱点：<strong>コサイン重みを省略</strong>（立体角の割合）。<strong>GTAO</strong> が修正。

## 発想：地平線を探す

点 p に立って、<strong>ある 1 方向（たとえば右）</strong>を見ます。その方向の**断面**（p とその方向と視線を含む平面）を考えます。

- 面自身は**接線**（面の傾き）を持ちます。
- 近くの物体がその方向に立ちはだかっていれば、**見上げる角度**（地平線の高さ h）が、接線より**高く**なります。
- **接線と地平線の間の角度**が、**遮蔽されている範囲**です。

<svg class="fig illust" viewBox="0 0 764 280" role="img" aria-label="地平線と接線">
<text x="20" y="24" class="fig-title">ある 1 方向の断面：接線角 t から地平線 h までが、遮蔽されている範囲</text>
<line x1="60" y1="220" x2="400" y2="220" stroke="currentColor" stroke-width="4"/>
<polygon points="400,220 400,110 470,110 470,220" fill="rgba(150,150,150,0.5)" stroke="currentColor" stroke-width="2"/>
<circle cx="170" cy="220" r="7" fill="currentColor"/><text x="160" y="246" style="font-size:12px">点 p</text>
<line x1="170" y1="220" x2="380" y2="220" stroke="#2ea043" stroke-width="2" stroke-dasharray="5 3"/><text x="300" y="238" style="font-size:12px;fill:#2ea043">接線（t = 0 の例）</text>
<line x1="170" y1="220" x2="400" y2="112" stroke="#e5484d" stroke-width="3"/><text x="290" y="150" style="font-size:12px;fill:#e5484d;font-weight:700">地平線 h</text>
<path d="M230,220 A60,60 0 0 0 220,194" fill="none" stroke="currentColor"/><text x="236" y="206" style="font-size:12px">h</text>
<polygon points="170,220 380,220 400,112" fill="rgba(229,72,77,0.18)"/>
<text x="480" y="130" style="font-weight:700">遮蔽 ＝ sin h − sin t</text>
<text x="480" y="154" style="font-size:12px">（h の上は、空が見えている）</text>
<text x="480" y="184" style="font-size:12px">この 1 方向の結果を、全方向（N 本）で平均する</text>
<text x="20" y="268" style="font-size:12px">壁が高いほど h が大きくなり、遮蔽が増える。壁がなければ h = t で、遮蔽 0</text>
</svg>

<!-- fig:hbao-horizon:begin -->

<svg class="fig illust motion" data-fig="hbao-horizon" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-hbao-horizon" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">HBAO: 左右に進みながら「いちばん高い見上げ角(水平線)」を探して、AO を決める</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">同じ断面で、SSAO(サンプル 8 個)と比べる。正解は、全方向を細かく調べた値</text>
<rect x="30" y="90" width="490" height="274" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="80" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 左右に 0.5 ずつ進んで、見上げ角を調べる</text>
<rect x="120.0" y="294.8" width="20.0" height="35.2" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/>
<rect x="140.0" y="294.8" width="20.0" height="35.2" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/>
<rect x="260.0" y="242.0" width="20.0" height="88.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/>
<rect x="280.0" y="132.0" width="20.0" height="198.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/>
<rect x="300.0" y="132.0" width="20.0" height="198.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/>
<rect x="320.0" y="132.0" width="20.0" height="198.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1"/>
<line x1="40.0" y1="330.0" x2="520.0" y2="330.0" stroke="#94a3b8" stroke-width="2"/>
<circle cx="250.0" cy="330.0" r="8" fill="#1f2937"/>
<text x="242.0" y="354.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">調べるピクセル</text>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0613;0.0615;0.0829;0.0831;1.0000" values="0;0;1;1;0;0"/><line x1="250.0" y1="330.0" x2="260.0" y2="242.0" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="260.0" cy="242.0" r="5" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250.0" y1="330.0" x2="265.52" y2="193.4" stroke="#e5484d" stroke-width="3.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0829;0.0831;0.1044;0.1046;1.0000" values="0;0;1;1;0;0"/><line x1="250.0" y1="330.0" x2="270.0" y2="242.0" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="270.0" cy="242.0" r="5" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250.0" y1="330.0" x2="265.52" y2="193.4" stroke="#e5484d" stroke-width="3.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1044;0.1046;0.1259;0.1262;1.0000" values="0;0;1;1;0;0"/><line x1="250.0" y1="330.0" x2="280.0" y2="132.0" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="280.0" cy="132.0" r="5" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250.0" y1="330.0" x2="265.52" y2="193.4" stroke="#e5484d" stroke-width="3.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1259;0.1262;0.1475;0.1477;1.0000" values="0;0;1;1;0;0"/><line x1="250.0" y1="330.0" x2="290.0" y2="132.0" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="290.0" cy="132.0" r="5" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250.0" y1="330.0" x2="265.52" y2="193.4" stroke="#e5484d" stroke-width="3.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1475;0.1477;0.1690;0.1692;1.0000" values="0;0;1;1;0;0"/><line x1="250.0" y1="330.0" x2="300.0" y2="132.0" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="300.0" cy="132.0" r="5" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250.0" y1="330.0" x2="265.52" y2="193.4" stroke="#e5484d" stroke-width="3.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1690;0.1692;0.1906;0.1908;1.0000" values="0;0;1;1;0;0"/><line x1="250.0" y1="330.0" x2="310.0" y2="132.0" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="310.0" cy="132.0" r="5" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250.0" y1="330.0" x2="265.52" y2="193.4" stroke="#e5484d" stroke-width="3.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1906;0.1908;0.2121;0.2123;1.0000" values="0;0;1;1;0;0"/><line x1="250.0" y1="330.0" x2="320.0" y2="132.0" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="320.0" cy="132.0" r="5" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250.0" y1="330.0" x2="265.52" y2="193.4" stroke="#e5484d" stroke-width="3.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2121;0.2123;0.2336;0.2338;1.0000" values="0;0;1;1;0;0"/><line x1="250.0" y1="330.0" x2="240.0" y2="330.0" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="240.0" cy="330.0" r="5" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250.0" y1="330.0" x2="186.0" y2="330.0" stroke="#e5484d" stroke-width="3.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2336;0.2338;0.2552;0.2554;1.0000" values="0;0;1;1;0;0"/><line x1="250.0" y1="330.0" x2="230.0" y2="330.0" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="230.0" cy="330.0" r="5" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250.0" y1="330.0" x2="186.0" y2="330.0" stroke="#e5484d" stroke-width="3.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2552;0.2554;0.2767;0.2769;1.0000" values="0;0;1;1;0;0"/><line x1="250.0" y1="330.0" x2="220.0" y2="330.0" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="220.0" cy="330.0" r="5" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250.0" y1="330.0" x2="186.0" y2="330.0" stroke="#e5484d" stroke-width="3.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2767;0.2769;0.2983;0.2985;1.0000" values="0;0;1;1;0;0"/><line x1="250.0" y1="330.0" x2="210.0" y2="330.0" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="210.0" cy="330.0" r="5" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250.0" y1="330.0" x2="186.0" y2="330.0" stroke="#e5484d" stroke-width="3.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2983;0.2985;0.3198;0.3200;1.0000" values="0;0;1;1;0;0"/><line x1="250.0" y1="330.0" x2="200.0" y2="330.0" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="200.0" cy="330.0" r="5" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250.0" y1="330.0" x2="186.0" y2="330.0" stroke="#e5484d" stroke-width="3.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3198;0.3200;0.3413;0.3415;1.0000" values="0;0;1;1;0;0"/><line x1="250.0" y1="330.0" x2="190.0" y2="330.0" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="190.0" cy="330.0" r="5" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250.0" y1="330.0" x2="186.0" y2="330.0" stroke="#e5484d" stroke-width="3.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3413;0.3415;1.0000" values="0;0;1;1"/><line x1="250.0" y1="330.0" x2="180.0" y2="330.0" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="180.0" cy="330.0" r="5" fill="#2ea043" stroke="#ffffff" stroke-width="1.5"/>
<line x1="250.0" y1="330.0" x2="186.0" y2="330.0" stroke="#e5484d" stroke-width="3.5"/>
</g>
<text x="40" y="350" text-anchor="start" style="font-size:12px;font-weight:500;fill:#e5484d">赤い線 = ここまでで一番高い見上げ角(水平線)</text>
<rect x="550" y="90" width="380" height="274" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="550" y="80" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 進むたびの見上げ角</text>
<text x="566" y="114" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">高さ(深度から読む)→ 見上げ角 → これまでの最大</text>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0613;0.0615;1.0000" values="0;0;1;1"/><text x="566" y="138" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">→1</text>
<text x="592" y="138" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">高さ 2.0</text>
<text x="650" y="138" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">76°</text>
<text x="692" y="138" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">最大 76°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0829;0.0831;1.0000" values="0;0;1;1"/><text x="566" y="163" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">→2</text>
<text x="592" y="163" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">高さ 2.0</text>
<text x="650" y="163" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">63°</text>
<text x="692" y="163" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">最大 76°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1044;0.1046;1.0000" values="0;0;1;1"/><text x="566" y="188" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">→3</text>
<text x="592" y="188" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">高さ 4.5</text>
<text x="650" y="188" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">72°</text>
<text x="692" y="188" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">最大 76°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1259;0.1262;1.0000" values="0;0;1;1"/><text x="566" y="213" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">→4</text>
<text x="592" y="213" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">高さ 4.5</text>
<text x="650" y="213" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">66°</text>
<text x="692" y="213" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">最大 76°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1475;0.1477;1.0000" values="0;0;1;1"/><text x="566" y="238" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">→5</text>
<text x="592" y="238" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">高さ 4.5</text>
<text x="650" y="238" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">61°</text>
<text x="692" y="238" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">最大 76°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1690;0.1692;1.0000" values="0;0;1;1"/><text x="566" y="263" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">→6</text>
<text x="592" y="263" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">高さ 4.5</text>
<text x="650" y="263" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">56°</text>
<text x="692" y="263" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">最大 76°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1906;0.1908;1.0000" values="0;0;1;1"/><text x="566" y="288" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">→7</text>
<text x="592" y="288" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">高さ 4.5</text>
<text x="650" y="288" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">52°</text>
<text x="692" y="288" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">最大 76°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2121;0.2123;1.0000" values="0;0;1;1"/><text x="748" y="138" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">←1</text>
<text x="774" y="138" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">高さ 0.0</text>
<text x="832" y="138" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043"> 0°</text>
<text x="874" y="138" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">最大  0°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2336;0.2338;1.0000" values="0;0;1;1"/><text x="748" y="163" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">←2</text>
<text x="774" y="163" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">高さ 0.0</text>
<text x="832" y="163" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043"> 0°</text>
<text x="874" y="163" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">最大  0°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2552;0.2554;1.0000" values="0;0;1;1"/><text x="748" y="188" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">←3</text>
<text x="774" y="188" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">高さ 0.0</text>
<text x="832" y="188" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043"> 0°</text>
<text x="874" y="188" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">最大  0°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2767;0.2769;1.0000" values="0;0;1;1"/><text x="748" y="213" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">←4</text>
<text x="774" y="213" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">高さ 0.0</text>
<text x="832" y="213" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043"> 0°</text>
<text x="874" y="213" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">最大  0°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2983;0.2985;1.0000" values="0;0;1;1"/><text x="748" y="238" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">←5</text>
<text x="774" y="238" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">高さ 0.0</text>
<text x="832" y="238" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043"> 0°</text>
<text x="874" y="238" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">最大  0°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3198;0.3200;1.0000" values="0;0;1;1"/><text x="748" y="263" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">←6</text>
<text x="774" y="263" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">高さ 0.0</text>
<text x="832" y="263" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043"> 0°</text>
<text x="874" y="263" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">最大  0°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3413;0.3415;1.0000" values="0;0;1;1"/><text x="748" y="288" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed">←7</text>
<text x="774" y="288" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">高さ 0.0</text>
<text x="832" y="288" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043"> 0°</text>
<text x="874" y="288" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">最大  0°</text>
</g>
<text x="566" y="330" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">深度の読み込み:</text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0613;0.0615;1.0000" values="1;1;0;0"/></text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">1<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0613;0.0615;0.0829;0.0831;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">2<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0829;0.0831;0.1044;0.1046;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">3<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1044;0.1046;0.1259;0.1262;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1259;0.1262;0.1475;0.1477;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">5<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1475;0.1477;0.1690;0.1692;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">6<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1690;0.1692;0.1906;0.1908;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">7<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1906;0.1908;0.2121;0.2123;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">8<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2121;0.2123;0.2336;0.2338;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">9<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2336;0.2338;0.2552;0.2554;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">10<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2552;0.2554;0.2767;0.2769;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">11<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2767;0.2769;0.2983;0.2985;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">12<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2983;0.2985;0.3198;0.3200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">13<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3198;0.3200;0.3413;0.3415;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="332" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">14<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3413;0.3415;1.0000" values="0;0;1;1"/></text>
<text x="566" y="352" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed" opacity="0">AO = (cos 0° + cos 76°)/2 = 0.621<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3629;0.3631;1.0000" values="0;0;1;1"/></text>
<text x="30" y="392" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">③ 全部の列で同じことをして、SSAO(8 サンプル)と、正解とを比べる</text>
<text x="30" y="419" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">正解</text>
<rect x="200.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4144" values="#e5e7eb;#ffffff"/></rect>
<rect x="220.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4221" values="#e5e7eb;#f9f9f9"/></rect>
<rect x="240.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4297" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="260.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4374" values="#e5e7eb;#c9c9c9"/></rect>
<rect x="280.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4451" values="#e5e7eb;#ffffff"/></rect>
<rect x="300.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4528" values="#e5e7eb;#ffffff"/></rect>
<rect x="320.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4605" values="#e5e7eb;#c9c9c9"/></rect>
<rect x="340.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4682" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="360.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4759" values="#e5e7eb;#e0e0e0"/></rect>
<rect x="380.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#d1d1d1"/></rect>
<rect x="400.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4913" values="#e5e7eb;#a8a8a8"/></rect>
<rect x="420.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4990" values="#e5e7eb;#a2a2a2"/></rect>
<rect x="440.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5067" values="#e5e7eb;#ffffff"/></rect>
<rect x="460.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5144" values="#e5e7eb;#ffffff"/></rect>
<rect x="480.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5221" values="#e5e7eb;#ffffff"/></rect>
<rect x="500.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5297" values="#e5e7eb;#9c9c9c"/></rect>
<rect x="520.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5374" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="540.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5451" values="#e5e7eb;#dfdfdf"/></rect>
<rect x="560.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5528" values="#e5e7eb;#ffffff"/></rect>
<rect x="580.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5605" values="#e5e7eb;#ffffff"/></rect>
<rect x="600.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5682" values="#e5e7eb;#ffffff"/></rect>
<rect x="620.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5759" values="#e5e7eb;#ffffff"/></rect>
<rect x="640.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5836" values="#e5e7eb;#ffffff"/></rect>
<rect x="660.0" y="404.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5913" values="#e5e7eb;#ffffff"/></rect>
<rect x="200" y="404" width="480.0" height="20.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="30" y="445" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">HBAO(14 回読む)</text>
<rect x="200.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4144" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="220.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4221" values="#e5e7eb;#fafafa"/></rect>
<rect x="240.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4297" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="260.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4374" values="#e5e7eb;#c9c9c9"/></rect>
<rect x="280.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4451" values="#e5e7eb;#ffffff"/></rect>
<rect x="300.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4528" values="#e5e7eb;#ffffff"/></rect>
<rect x="320.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4605" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="340.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4682" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="360.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4759" values="#e5e7eb;#cfcfcf"/></rect>
<rect x="380.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#c4c4c4"/></rect>
<rect x="400.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4913" values="#e5e7eb;#a8a8a8"/></rect>
<rect x="420.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4990" values="#e5e7eb;#a3a3a3"/></rect>
<rect x="440.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5067" values="#e5e7eb;#ffffff"/></rect>
<rect x="460.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5144" values="#e5e7eb;#ffffff"/></rect>
<rect x="480.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5221" values="#e5e7eb;#ffffff"/></rect>
<rect x="500.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5297" values="#e5e7eb;#a5a5a5"/></rect>
<rect x="520.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5374" values="#e5e7eb;#bbbbbb"/></rect>
<rect x="540.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5451" values="#e5e7eb;#cccccc"/></rect>
<rect x="560.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5528" values="#e5e7eb;#ffffff"/></rect>
<rect x="580.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5605" values="#e5e7eb;#ffffff"/></rect>
<rect x="600.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5682" values="#e5e7eb;#ffffff"/></rect>
<rect x="620.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5759" values="#e5e7eb;#ffffff"/></rect>
<rect x="640.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5836" values="#e5e7eb;#ffffff"/></rect>
<rect x="660.0" y="430.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5913" values="#e5e7eb;#ffffff"/></rect>
<rect x="200" y="430" width="480.0" height="20.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="30" y="471" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">SSAO(8 回読む)</text>
<rect x="200.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4144" values="#e5e7eb;#ffffff"/></rect>
<rect x="220.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4221" values="#e5e7eb;#ffffff"/></rect>
<rect x="240.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4297" values="#e5e7eb;#ffffff"/></rect>
<rect x="260.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4374" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="280.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4451" values="#e5e7eb;#ffffff"/></rect>
<rect x="300.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4528" values="#e5e7eb;#ffffff"/></rect>
<rect x="320.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4605" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="340.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4682" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="360.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4759" values="#e5e7eb;#ffffff"/></rect>
<rect x="380.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="400.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4913" values="#e5e7eb;#c6c6c6"/></rect>
<rect x="420.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4990" values="#e5e7eb;#a9a9a9"/></rect>
<rect x="440.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5067" values="#e5e7eb;#ffffff"/></rect>
<rect x="460.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5144" values="#e5e7eb;#ffffff"/></rect>
<rect x="480.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5221" values="#e5e7eb;#ffffff"/></rect>
<rect x="500.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5297" values="#e5e7eb;#ffffff"/></rect>
<rect x="520.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5374" values="#e5e7eb;#ffffff"/></rect>
<rect x="540.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5451" values="#e5e7eb;#ffffff"/></rect>
<rect x="560.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5528" values="#e5e7eb;#ffffff"/></rect>
<rect x="580.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5605" values="#e5e7eb;#ffffff"/></rect>
<rect x="600.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5682" values="#e5e7eb;#ffffff"/></rect>
<rect x="620.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5759" values="#e5e7eb;#ffffff"/></rect>
<rect x="640.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5836" values="#e5e7eb;#ffffff"/></rect>
<rect x="660.0" y="456.0" width="20.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5913" values="#e5e7eb;#ffffff"/></rect>
<rect x="200" y="456" width="480.0" height="20.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="692" y="420" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">HBAO の読み込み:</text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4142;0.4144;1.0000" values="1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">14<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4142;0.4144;0.4218;0.4221;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">28<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4218;0.4221;0.4295;0.4297;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">42<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4295;0.4297;0.4372;0.4374;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">56<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4372;0.4374;0.4449;0.4451;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">70<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4449;0.4451;0.4526;0.4528;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">84<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4526;0.4528;0.4603;0.4605;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">98<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4603;0.4605;0.4680;0.4682;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">112<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4680;0.4682;0.4757;0.4759;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">126<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4757;0.4759;0.4834;0.4836;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">140<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4834;0.4836;0.4911;0.4913;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">154<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4911;0.4913;0.4988;0.4990;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">168<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4988;0.4990;0.5065;0.5067;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">182<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5065;0.5067;0.5142;0.5144;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">196<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5142;0.5144;0.5218;0.5221;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">210<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5218;0.5221;0.5295;0.5297;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">224<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5295;0.5297;0.5372;0.5374;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">238<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5372;0.5374;0.5449;0.5451;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">252<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5449;0.5451;0.5526;0.5528;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">266<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5526;0.5528;0.5603;0.5605;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">280<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5603;0.5605;0.5680;0.5682;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">294<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5680;0.5682;0.5757;0.5759;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">308<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5757;0.5759;0.5834;0.5836;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">322<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5834;0.5836;0.5911;0.5913;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="422" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">336<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5911;0.5913;1.0000" values="0;0;1;1"/></text>
<text x="692" y="446" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">SSAO の読み込み:</text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4142;0.4144;1.0000" values="1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">8<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4142;0.4144;0.4218;0.4221;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">16<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4218;0.4221;0.4295;0.4297;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">24<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4295;0.4297;0.4372;0.4374;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">32<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4372;0.4374;0.4449;0.4451;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">40<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4449;0.4451;0.4526;0.4528;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">48<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4526;0.4528;0.4603;0.4605;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">56<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4603;0.4605;0.4680;0.4682;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">64<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4680;0.4682;0.4757;0.4759;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">72<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4757;0.4759;0.4834;0.4836;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">80<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4834;0.4836;0.4911;0.4913;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">88<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4911;0.4913;0.4988;0.4990;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">96<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4988;0.4990;0.5065;0.5067;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">104<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5065;0.5067;0.5142;0.5144;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">112<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5142;0.5144;0.5218;0.5221;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">120<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5218;0.5221;0.5295;0.5297;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">128<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5295;0.5297;0.5372;0.5374;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">136<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5372;0.5374;0.5449;0.5451;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">144<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5449;0.5451;0.5526;0.5528;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">152<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5526;0.5528;0.5603;0.5605;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">160<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5603;0.5605;0.5680;0.5682;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">168<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5680;0.5682;0.5757;0.5759;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">176<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5757;0.5759;0.5834;0.5836;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">184<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5834;0.5836;0.5911;0.5913;1.0000" values="0;0;1;1;0;0"/></text>
<text x="830" y="448" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">192<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5911;0.5913;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6244;0.6246;1.0000" values="0;0;1;1"/><rect x="692" y="460" width="238" height="60" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="708" y="484" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">正解とのずれ(平均)</text>
<text x="708" y="505" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">HBAO 0.019 / SSAO 0.066</text>
</g>
<text x="30" y="532" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">断面で、1 つのピクセルから左右に進む<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0613;0.0615;1.0000" values="1;1;0;0"/></text>
<text x="30" y="532" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">進むたびに、見上げ角の最大値(水平線)を更新する<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0613;0.0615;0.3629;0.3631;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="532" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">左右の水平線から、光が見える角度の広さ(AO)が決まる<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3629;0.3631;0.4142;0.4144;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="532" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">全部の列で繰り返し、SSAO と正解を並べる<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4142;0.4144;0.6244;0.6246;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="532" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">HBAO は「方向」を調べるので、同じ回数なら正解に近い<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6244;0.6246;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:hbao-horizon:end -->

## 式

半球を**方位角 θ**（画面上の方向）と、**仰角 α**（その方向の断面での持ち上げ角）で表します。**可視な範囲は、t(θ) から h(θ) の「間」ではなく、h(θ) より上**ですが、AO は<strong>「遮蔽されている量」</strong>で書きます。

<div class="formula">AO = 1 − (1 / 2π) · ∫_{θ=−π}^{π} ∫_{α=t(θ)}^{h(θ)} W(θ) · cosα  dα dθ</div>

内側の積分は`∫ cosα dα = sin h − sin t` です。**距離の減衰 W** を方向ごとに一定とみなし、**方向を N 本に離散化**すると、次のとおりです。

<div class="formula">AO ≈ 1 − (1 / N) · Σ_{i=1}^{N} W(θᵢ) · ( sin h(θᵢ) − sin t(θᵢ) )</div>

| 記号 | 意味 |
| --- | --- |
| **N** | 方向（スライス）の数（8 程度） |
| <strong>h(θ)</strong> | 方向 θ での**地平線の角度**（歩いた中で最も高く見えた遮蔽物の仰角） |
| <strong>t(θ)</strong> | 方向 θ での**面自身の接線の角度**（法線から決まる） |
| **W** | 距離の減衰。`W(r) = 1 − r²/R²`（R は影響半径） |

!!! note "コサイン重みが入っていない"
    式は**立体角の割合**（`cosα dα dθ` は、半球上の面積要素）を、**そのまま**積分しています。[理論](theory/index.md)の AO は**法線とのコサイン `n·ω`**を掛けた積分でした。**HBAO はこのコサインを省略**しています（法線に近い遮蔽も横の遮蔽も立体角が同じなら、同じ重み）。そのため、**正確な AO より、少しだけ、横方向の遮蔽が強く**効きます。この点を修正したのが、[GTAO](gtao.md) です。

## 手順

1 つの画素について、HBAO は次の順に計算します。

まず方向を決めます。N 本（8 本程度）の方向を、画面上に放射状に取り、画素ごとにランダムに回転させて（4×4 のノイズ）縞をノイズに変えます。各方向について、法線と方向から、断面での面の傾き（接線角 t）を計算します。そして、その方向に深度バッファを M ステップ（6 程度）歩きます。ステップの幅は画面上のピクセルで一定にし、半径 R を画面の大きさに直したものを M で割って決めます。

各ステップでは、深度から遮蔽物の位置 S を復元し、S − P のベクトル H の仰角を計算します。これが今までの最大の仰角より高ければ、地平線が上がったことになるので、<strong>上がった差の分だけ AO に足し</strong>、地平線を更新します。全方向について足し終えたら、平均を取って `AO = 1 − 平均` とします。

ここで重要なのは、<strong>地平線は歩いている間に一方向にしか上がらない</strong>ことです。いちど高い遮蔽物が見つかれば、その後ろにある低い物は、地平線を更新しないので AO に加算されません。見えている範囲の「一番高い壁」だけが遮蔽として効く、という幾何学的に自然な仕組みです。

### 接線角 t

断面の**面の傾き**です。**法線 N と画面上の方向 d** から求めます。

**面が画面と平行**（法線がカメラの方を向いている）なら、**t = 0**（接線は水平）です。**面が傾いている**と**傾いた分だけ**、<strong>t が負（面が奥へ傾く）</strong>か<strong>正（面が手前へ傾く）</strong>になります。

左手系（カメラが +Z を見る）で、<strong>カメラの方向を「上」</strong>として仰角を測る場合、接線ベクトルと `sin t` は、次のとおりです。

<div class="formula">T = ( d.x , d.y , −(N.x·d.x + N.y·d.y) / N.z )　、　sin t = −T.z / |T|</div>

### 仰角の更新

**地平線の仰角の sin** を、歩きながら**最大値**で更新します。**更新のたびに増えた分を AO に足す**ので、**遠い遮蔽ほど弱く**（距離の減衰を掛けて）なります。

```hlsl
float HorizonAO(float2 uv, float3 p, float3 n, float2 dir_view, float step_uv) {
  float3 t_vec = float3(dir_view, -dot(n.xy, dir_view) / n.z);
  float sin_t = -t_vec.z / length(t_vec);

  float sin_h = sin_t;
  float ao = 0.0;
  for (int i = 1; i <= kSteps; ++i) {
    float2 suv = uv + float2(dir_view.x, -dir_view.y) * (step_uv * i);
    float3 s = ViewPositionFromDepth(suv);
    float3 h = s - p;
    float r2 = dot(h, h);

    float sin_s = -h.z / sqrt(r2);
    if (sin_s > sin_h) {
      float falloff = saturate(1.0 - r2 * inv_radius2);
      ao += (sin_s - sin_h) * falloff;
      sin_h = sin_s;
    }
  }
  return ao;
}
```

| 点 | 説明 |
| --- | --- |
| **`sin_t` で初期化** | 地平線の初期値は、**面自身の高さ**（遮蔽なし）。**それより高い遮蔽物**だけが、AO に寄与 |
| **`−h.z`** | 左手系（+Z が奥）で、<strong>カメラに近い側を「上」</strong>にするため、符号を反転 |
| **`falloff`** | `1 − r²/R²`。**半径 R の外では 0** |
| **ステップの幅** | `step_uv` は、**画面上で一定**。**ビュー空間の半径 R ÷ ステップ数**を、距離で割って画面に直す |
| **`float2(dir.x, -dir.y)`** | 画面の方向（y 下向き）と、ビュー空間（y 上向き）の違い |

全体では画素ごとに N 方向を回します。

```hlsl
float HBAO(float2 uv) {
  float3 p = ViewPositionFromDepth(uv);
  float3 n = ViewNormal(uv);
  float2 noise = noise_tex.Sample(wrap_sampler, uv * noise_scale).xy;
  float step_uv = radius_uv_at(p.z) / kSteps * (0.5 + 0.5 * noise.y);

  float ao = 0.0;
  for (int i = 0; i < kDirections; ++i) {
    float angle = 6.2831853 * (i + noise.x) / kDirections;
    ao += HorizonAO(uv, p, n, float2(cos(angle), sin(angle)), step_uv);
  }
  return saturate(1.0 - ao / kDirections * intensity);
}
```

## ランダム化

方向の数 N が小さい（8）ので、そのままだと、方向の少なさによる縞が出ます。そこで、画素ごとに方向の開始角を回します。さらに、ステップの長さにも画素ごとにわずかなジッターを与えます。ステップの位置が全画素で同じだと、サンプル位置の並びが帯のように見えてしまうためです（バンディング）。どちらも、規則的な誤差を乱数に変えて、後のぼかしで消すための準備です（[Noise Patterns](filtering/noise-pattern.md)）。

## 点を数える方式との比較

[半球 SSAO](ssao-hemisphere.md) のように点を数える方式は、各サンプルが 0 か 1 の 2 値で、少ない点では量子化ノイズが大きくなります。HBAO は、角度という連続値を積分するので、少ない方向数でも滑らかです。コストは、N 個の独立サンプルに対して、HBAO は N 方向 × M ステップとやや多めですが、同じ方向の隣り合うアクセスはキャッシュに優しい面もあります。

共通の弱点もあります。地平線は最も高い 1 点で決まるため、HBAO も遮蔽物の厚みを区別できず、薄い柱の後ろを暗くしすぎる問題は同じように残ります。コサイン重みは、点を数える方式は一様な半球で雑に扱い、HBAO は省略しています。

## 長所と短所

HBAO の長所は、少ないサンプルで滑らかなことです。接線角で面の傾きを正しく扱うので、平らな面で自己遮蔽しにくく、距離の減衰が自然に式に入っています。「地平線を探して積分する」という考え方が、後の GTAO の基礎になりました。

短所は、コサイン重みがないこと（GTAO で修正）、方向数 × ステップ数でサンプルが多くなる（実質 8 × 6 = 48 回）こと、ハロー・画面端・薄い物の問題が残ること、そして法線が必要なことです。

## 次の方式

HBAO の重さとキャッシュの効きにくさは、フル解像度で処理し、デインターリーブで読み方を整えた [HBAO+](hbao-plus.md) が解決しました。コサイン重みがない問題とマルチ バウンスの欠如は、[GTAO](gtao.md) が解決しました。

## よくあるミス

??? failure "接線角 t を求めず、地平線を 0 から始めて、傾いた面が自己遮蔽する"
    初期値を面自身の `sin t` にします。

??? failure "ステップ幅を、ビュー空間の距離で固定して、遠くの物のサンプルが画面上で潰れる"
    画面上の**ピクセルで一定**の幅にし、半径は距離で割って画面に直します。

??? failure "地平線の更新に、距離の減衰を掛けず、遠い壁で暗くなる"
    更新の増分に、`falloff` を掛けます。

??? failure "y の向き（画面は下向き、ビュー空間は上向き）を取り違える"
    方向を画面（uv）とビュー空間で、**y の符号を反転**して使い分けます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] HBAO ＝ <strong>方向ごとに深度バッファを歩き、地平線の角度を求めて、角度を積分</strong>する
    - [x] AO ≈ <strong>1 − 平均( W · (sin h − sin t) )</strong>。<strong>t は面の接線角、h は地平線</strong>
    - [x] <strong>点を数えず、角度を積分</strong>するので<strong>少ないサンプルでも滑らか</strong>
    - [x] <strong>コサイン重みがない</strong>のが弱点（→ GTAO）
    - [x] ランダムな方向・ステップでノイズに変えてぼかす

## 参考

- Bavoil, Sainz, Dimitrov, "Image-Space Horizon-Based Ambient Occlusion"（SIGGRAPH 2008 Talks）

## 関連ページ

- [Ambient Occlusion (AO)](index.md)
- [HBAO+](hbao-plus.md)
- [GTAO](gtao.md)
- [AO Filtering](filtering/index.md)
- [AO Theory](theory/index.md)
