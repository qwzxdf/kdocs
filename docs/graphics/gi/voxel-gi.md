---
title: Voxel GI
tags:
  - 描画
---

# Voxel GI

**SSGI**は**画面に映っているもの**しか見えませんでした。**ボクセル GI**（Voxel Cone Tracing、**VXGI**）は、**シーン全体を 3D の格子（ボクセル）に変換**し、**そこに「形（遮蔽）」と「光（出射光）」を保存**します。**画素から、半球の方向に「円錐（コーン）」を飛ばし**、**ボクセルの上をミップ マップをたどりながら進む**ことで、**画面外・裏側も含めた間接光**を<strong>ノイズなし（または少なく）</strong>で得られます。**2011 年の Crassin らの手法**で、**当時、リアルタイム GI の大きな進歩**でした。

!!! tip "ポイント"
    - シーンを<strong>ボクセル化</strong>し、<strong>各ボクセルに「不透明度」と「出射光（放射輝度）」</strong>を保存。
    - <strong>ボクセルのミップ マップ</strong>を作る（粗い階層）。<strong>遠くほど粗いミップを読む</strong>。
    - <strong>コーン トレース</strong>：<strong>画素から円錐を飛ばし</strong>、<strong>円錐の広がりに合うミップ</strong>を<strong>前から後ろへ累積</strong>。
    - <strong>拡散</strong>は<strong>広い円錐を数本</strong>（5〜6 本）、<strong>鏡面</strong>は<strong>細い円錐 1 本</strong>。
    - <strong>画面外も反映</strong>。<strong>ノイズが少ない</strong>（円錐が空間をまとめて積分）。
    - 欠点：<strong>ボクセルの解像度が粗い</strong>（<strong>光漏れ</strong>）。<strong>メモリ・更新コスト</strong>が重い。

## 原理

### ① ボクセル化

**シーンのジオメトリ**を、**3D の格子**（例：256³）に**書き込みます**。**各ボクセル**に<strong>そこにある表面の「色（アルベド）」・「法線」・「不透明度」</strong>を**保存**します。

ボクセル化の方法は、大きく 2 つあります。1 つは、ラスタライズを利用する方法です。三角形を、最も面積が大きくなる軸の方向に投影し、ピクセル シェーダーで 3D テクスチャに書き込みます。保守的ラスタライズを併用すると、小さな三角形も漏れなく拾えます。もう 1 つは、コンピュート シェーダーで、三角形ごとにボクセルへ書き込む方法です。更新のコストを抑えるため、静的な部分はキャッシュしておき、動く物だけを毎フレーム更新します。

### ② 光の注入

**各ボクセルに**、**直接光**（光源から、**シャドウ マップ**を使って）を**当てて**、<strong>そのボクセルの「出射光」</strong>（**アルベド × 直接光**）を計算し、**3D テクスチャに保存**します。

ボクセルに保存する値は、放射輝度（RGB）と不透明度（A）です。さらに、方向性も持たせる<strong>異方性ボクセル</strong>では、±X, ±Y, ±Z の 6 方向ごとに、その方向から見たときの値を保存します。これにより、方向による違い（薄い壁の表と裏で光が違うこと）を表せます。

### ③ ミップ マップの生成

**3D テクスチャ**に**ミップ マップ**を作ります。<strong>上位のミップほど、粗く（広い範囲の平均）</strong>なります。**円錐が広がるにつれて**、**粗いミップ**を読むことで、**円錐の太さに合った**、**範囲の平均**を得ます。

**異方性ボクセル**では、**ミップを作る際、方向ごとの値をそれぞれ平均**します。

<!-- fig:voxel-cone-trace:begin -->

<svg class="fig illust motion" data-fig="voxel-cone-trace" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-voxel-cone-trace" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ボクセル コーン トレーシング: 太る円錐で進み、遠いほど「粗いボクセル」を読む</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">2 次元のボクセル(24×12)。光線ではなく、広がる円錐を 1 本飛ばして、周りの色と遮蔽を一度に集める</text>
<rect x="30" y="96" width="596.0" height="318.0" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① ボクセル(色つきが壁・床・箱)と、円錐</text>
<rect x="40.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="64.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="88.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="112.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="136.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="160.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="184.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="208.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="232.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="256.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="280.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="304.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="328.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="352.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="376.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="400.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="424.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="448.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="472.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="496.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="520.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="544.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="568.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="592.0" y="360.0" width="23.0" height="23.0" fill="#ccccb2" stroke="#ffffff" stroke-width="0.8"/>
<rect x="448.0" y="336.0" width="23.0" height="23.0" fill="#f2332e" stroke="#ffffff" stroke-width="0.8"/>
<rect x="448.0" y="312.0" width="23.0" height="23.0" fill="#f2332e" stroke="#ffffff" stroke-width="0.8"/>
<rect x="448.0" y="288.0" width="23.0" height="23.0" fill="#f2332e" stroke="#ffffff" stroke-width="0.8"/>
<rect x="448.0" y="264.0" width="23.0" height="23.0" fill="#f2332e" stroke="#ffffff" stroke-width="0.8"/>
<rect x="448.0" y="240.0" width="23.0" height="23.0" fill="#f2332e" stroke="#ffffff" stroke-width="0.8"/>
<rect x="448.0" y="216.0" width="23.0" height="23.0" fill="#f2332e" stroke="#ffffff" stroke-width="0.8"/>
<rect x="448.0" y="192.0" width="23.0" height="23.0" fill="#f2332e" stroke="#ffffff" stroke-width="0.8"/>
<rect x="472.0" y="336.0" width="23.0" height="23.0" fill="#f2332e" stroke="#ffffff" stroke-width="0.8"/>
<rect x="472.0" y="312.0" width="23.0" height="23.0" fill="#f2332e" stroke="#ffffff" stroke-width="0.8"/>
<rect x="472.0" y="288.0" width="23.0" height="23.0" fill="#f2332e" stroke="#ffffff" stroke-width="0.8"/>
<rect x="472.0" y="264.0" width="23.0" height="23.0" fill="#f2332e" stroke="#ffffff" stroke-width="0.8"/>
<rect x="472.0" y="240.0" width="23.0" height="23.0" fill="#f2332e" stroke="#ffffff" stroke-width="0.8"/>
<rect x="472.0" y="216.0" width="23.0" height="23.0" fill="#f2332e" stroke="#ffffff" stroke-width="0.8"/>
<rect x="472.0" y="192.0" width="23.0" height="23.0" fill="#f2332e" stroke="#ffffff" stroke-width="0.8"/>
<rect x="304.0" y="336.0" width="23.0" height="23.0" fill="#f2d933" stroke="#ffffff" stroke-width="0.8"/>
<rect x="304.0" y="312.0" width="23.0" height="23.0" fill="#f2d933" stroke="#ffffff" stroke-width="0.8"/>
<rect x="328.0" y="336.0" width="23.0" height="23.0" fill="#f2d933" stroke="#ffffff" stroke-width="0.8"/>
<rect x="328.0" y="312.0" width="23.0" height="23.0" fill="#f2d933" stroke="#ffffff" stroke-width="0.8"/>
<circle cx="208.0" cy="359.52" r="7" fill="#1f2937"/>
<text x="208.0" y="381.52" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">調べる点(床の上)</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;1.0000" values="1;1;0;0"/><line x1="208.0" y1="359.52" x2="523.74" y2="474.44" stroke="#93c5fd" stroke-width="1.5" stroke-dasharray="5 4"/>
<line x1="208.0" y1="359.52" x2="479.83" y2="162.02" stroke="#93c5fd" stroke-width="1.5" stroke-dasharray="5 4"/>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0679;0.0681;1.0000" values="0;0;1;1"/><circle cx="231.77" cy="356.18" r="12.76" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="231.77" cy="356.18" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0892;0.0894;1.0000" values="0;0;1;1"/><circle cx="255.53" cy="352.84" r="25.52" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="255.53" cy="352.84" r="4" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1105;0.1106;1.0000" values="0;0;1;1"/><circle cx="280.81" cy="349.29" r="39.09" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="280.81" cy="349.29" r="4" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1317;0.1319;1.0000" values="0;0;1;1"/><circle cx="319.52" cy="343.85" r="59.88" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="319.52" cy="343.85" r="4" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1530;0.1532;1.0000" values="0;0;1;1"/><circle cx="378.81" cy="335.51" r="91.72" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="378.81" cy="335.51" r="4" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1743;0.1745;1.0000" values="0;0;1;1"/><circle cx="469.64" cy="322.75" r="140.48" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="469.64" cy="322.75" r="4" fill="#e5484d"/>
</g>
<text x="560" y="120" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">円錐 1(角度 8°)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;0.6211;0.6213;1.0000" values="0;0;1;1;0;0"/><line x1="208.0" y1="359.52" x2="543.18" y2="336.08" stroke="#93c5fd" stroke-width="1.5" stroke-dasharray="5 4"/>
<line x1="208.0" y1="359.52" x2="376.0" y2="68.54" stroke="#93c5fd" stroke-width="1.5" stroke-dasharray="5 4"/>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3573;0.3574;1.0000" values="0;0;1;1"/><circle cx="228.35" cy="346.8" r="12.76" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="228.35" cy="346.8" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3786;0.3787;1.0000" values="0;0;1;1"/><circle cx="248.71" cy="334.08" r="25.52" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="248.71" cy="334.08" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;1.0000" values="0;0;1;1"/><circle cx="270.35" cy="320.56" r="39.09" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="270.35" cy="320.56" r="4" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4211;0.4213;1.0000" values="0;0;1;1"/><circle cx="303.5" cy="299.84" r="59.88" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="303.5" cy="299.84" r="4" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4424;0.4426;1.0000" values="0;0;1;1"/><circle cx="354.28" cy="268.11" r="91.72" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="354.28" cy="268.11" r="4" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4637;0.4638;1.0000" values="0;0;1;1"/><circle cx="432.06" cy="219.51" r="140.48" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="432.06" cy="219.51" r="4" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4849;0.4851;1.0000" values="0;0;1;1"/><circle cx="551.2" cy="145.07" r="215.18" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="551.2" cy="145.07" r="4" fill="#2ea043"/>
</g>
<text x="560" y="120" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">円錐 2(角度 32°)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6211;0.6213;1.0000" values="0;0;1;1"/><line x1="208.0" y1="359.52" x2="486.56" y2="171.63" stroke="#93c5fd" stroke-width="1.5" stroke-dasharray="5 4"/>
<line x1="208.0" y1="359.52" x2="208.0" y2="23.52" stroke="#93c5fd" stroke-width="1.5" stroke-dasharray="5 4"/>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6466;0.6468;1.0000" values="0;0;1;1"/><circle cx="219.27" cy="338.33" r="12.76" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="219.27" cy="338.33" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6679;0.6681;1.0000" values="0;0;1;1"/><circle cx="230.53" cy="317.14" r="25.52" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="230.53" cy="317.14" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6892;0.6894;1.0000" values="0;0;1;1"/><circle cx="242.52" cy="294.6" r="39.09" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="242.52" cy="294.6" r="4" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7105;0.7106;1.0000" values="0;0;1;1"/><circle cx="260.87" cy="260.09" r="59.88" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="260.87" cy="260.09" r="4" fill="#2ea043"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7317;0.7319;1.0000" values="0;0;1;1"/><circle cx="288.98" cy="207.22" r="91.72" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="288.98" cy="207.22" r="4" fill="#e5484d"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7530;0.7532;1.0000" values="0;0;1;1"/><circle cx="332.04" cy="126.24" r="140.48" fill="#60a5fa" fill-opacity="0.14" stroke="#3b82f6" stroke-width="1.5"/>
<circle cx="332.04" cy="126.24" r="4" fill="#2ea043"/>
</g>
<text x="560" y="120" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">円錐 3(角度 62°)</text>
</g>
<rect x="690" y="96" width="240" height="330" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="690" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 進むたびの読み込み</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;1.0000" values="1;1;0;0"/><g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0679;0.0681;1.0000" values="0;0;1;1"/><text x="702" y="130" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 1: 幅 1.1 → ミップ 0</text>
<text x="915" y="130" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">遮蔽 0.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0892;0.0894;1.0000" values="0;0;1;1"/><text x="702" y="151" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 2: 幅 2.1 → ミップ 1</text>
<text x="915" y="151" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5484d">遮蔽 0.65</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1105;0.1106;1.0000" values="0;0;1;1"/><text x="702" y="172" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 3: 幅 3.3 → ミップ 2</text>
<text x="915" y="172" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5484d">遮蔽 0.82</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1317;0.1319;1.0000" values="0;0;1;1"/><text x="702" y="193" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 4: 幅 5.0 → ミップ 2</text>
<text x="915" y="193" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5484d">遮蔽 0.91</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1530;0.1532;1.0000" values="0;0;1;1"/><text x="702" y="214" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 5: 幅 7.6 → ミップ 3</text>
<text x="915" y="214" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5484d">遮蔽 0.93</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1743;0.1745;1.0000" values="0;0;1;1"/><text x="702" y="235" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 6: 幅 11.7 → ミップ 3</text>
<text x="915" y="235" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5484d">遮蔽 0.96</text>
</g>
<text x="702" y="392" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">集めた色:</text>
<rect x="780" y="376" width="60" height="22" fill="#c8c29d" stroke="#334155" stroke-width="1.5"/>
<text x="850" y="392" text-anchor="start" style="font-size:13px;font-weight:700;fill:#7c3aed">遮蔽 0.96</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3317;0.3319;0.6211;0.6213;1.0000" values="0;0;1;1;0;0"/><g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3573;0.3574;1.0000" values="0;0;1;1"/><text x="702" y="130" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 1: 幅 1.1 → ミップ 0</text>
<text x="915" y="130" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">遮蔽 0.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3786;0.3787;1.0000" values="0;0;1;1"/><text x="702" y="151" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 2: 幅 2.1 → ミップ 1</text>
<text x="915" y="151" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">遮蔽 0.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3998;0.4000;1.0000" values="0;0;1;1"/><text x="702" y="172" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 3: 幅 3.3 → ミップ 2</text>
<text x="915" y="172" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">遮蔽 0.49</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4211;0.4213;1.0000" values="0;0;1;1"/><text x="702" y="193" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 4: 幅 5.0 → ミップ 2</text>
<text x="915" y="193" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5484d">遮蔽 0.74</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4424;0.4426;1.0000" values="0;0;1;1"/><text x="702" y="214" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 5: 幅 7.6 → ミップ 3</text>
<text x="915" y="214" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5484d">遮蔽 0.80</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4637;0.4638;1.0000" values="0;0;1;1"/><text x="702" y="235" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 6: 幅 11.7 → ミップ 3</text>
<text x="915" y="235" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5484d">遮蔽 0.89</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4849;0.4851;1.0000" values="0;0;1;1"/><text x="702" y="256" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 7: 幅 17.9 → ミップ 3</text>
<text x="915" y="256" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5484d">遮蔽 0.89</text>
</g>
<text x="702" y="392" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">集めた色:</text>
<rect x="780" y="376" width="60" height="22" fill="#c2b075" stroke="#334155" stroke-width="1.5"/>
<text x="850" y="392" text-anchor="start" style="font-size:13px;font-weight:700;fill:#7c3aed">遮蔽 0.89</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6211;0.6213;1.0000" values="0;0;1;1"/><g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6466;0.6468;1.0000" values="0;0;1;1"/><text x="702" y="130" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 1: 幅 1.1 → ミップ 0</text>
<text x="915" y="130" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">遮蔽 0.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6679;0.6681;1.0000" values="0;0;1;1"/><text x="702" y="151" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 2: 幅 2.1 → ミップ 1</text>
<text x="915" y="151" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">遮蔽 0.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6892;0.6894;1.0000" values="0;0;1;1"/><text x="702" y="172" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 3: 幅 3.3 → ミップ 2</text>
<text x="915" y="172" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">遮蔽 0.49</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7105;0.7106;1.0000" values="0;0;1;1"/><text x="702" y="193" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 4: 幅 5.0 → ミップ 2</text>
<text x="915" y="193" text-anchor="end" style="font-size:11px;font-weight:700;fill:#64748b">遮蔽 0.49</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7317;0.7319;1.0000" values="0;0;1;1"/><text x="702" y="214" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 5: 幅 7.6 → ミップ 3</text>
<text x="915" y="214" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5484d">遮蔽 0.61</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7530;0.7532;1.0000" values="0;0;1;1"/><text x="702" y="235" text-anchor="start" style="font-size:11px;font-weight:700;fill:#1f2937">歩 6: 幅 11.7 → ミップ 3</text>
<text x="915" y="235" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5484d">遮蔽 0.61</text>
</g>
<text x="702" y="392" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">集めた色:</text>
<rect x="780" y="376" width="60" height="22" fill="#858053" stroke="#334155" stroke-width="1.5"/>
<text x="850" y="392" text-anchor="start" style="font-size:13px;font-weight:700;fill:#7c3aed">遮蔽 0.61</text>
</g>
<text x="40" y="452" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">円錐 1 本あたりの歩数:</text>
<text x="240" y="456" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1956;0.1957;1.0000" values="1;1;0;0"/></text>
<text x="240" y="456" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">6<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1956;0.1957;0.5062;0.5064;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="456" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">7<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5062;0.5064;0.7743;0.7745;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="456" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2563eb" opacity="0">6<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7743;0.7745;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8892;0.8894;1.0000" values="0;0;1;1"/><rect x="330" y="436" width="600" height="80" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="346" y="460" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">円錐 3 本で 19 歩。1 歩ごとに、広い範囲を 1 回で読める</text>
<text x="346" y="484" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">最後の幅は 12 ボクセル。細い光線なら、同じ幅を埋めるのに 12 本ずつ必要</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">細い光線を何百本も飛ばす代わりに、広がる円錐を数本飛ばす<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">遠くなるほど円錐が太くなり、粗い(ぼかした)ボクセルを読む<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;0.9105;0.9106;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">遮蔽が十分に溜まったら終わり。壁の赤い色が、床へにじむ<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.9105;0.9106;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:voxel-cone-trace:end -->

### ④ コーン トレース

**画素から**、**半球に数本の円錐**を**飛ばします**。**円錐は進むにつれて、広がり**ます。**各ステップで円錐の太さに対応するミップ**を**読み**、**前から後ろへ（アルファ ブレンドのように）累積**します。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="コーン トレース">
<text x="20" y="24" class="fig-title">円錐が広がるにつれて、粗いミップを読み、前から後ろへ累積する</text>
<circle cx="80" cy="140" r="6" fill="currentColor"/><text x="60" y="166" style="font-size:12px">画素</text>
<polygon points="80,140 700,60 700,220" fill="rgba(76,139,245,0.12)" stroke="currentColor" stroke-dasharray="4 3"/>
<circle cx="140" cy="132" r="8" fill="none" stroke="currentColor"/><circle cx="220" cy="122" r="16" fill="none" stroke="currentColor"/><circle cx="350" cy="106" r="32" fill="none" stroke="currentColor"/><circle cx="550" cy="82" r="60" fill="none" stroke="currentColor"/>
<text x="110" y="210" style="font-size:12px">細かいミップ</text><text x="500" y="210" style="font-size:12px">粗いミップ</text>
<text x="40" y="250" style="font-size:12px">ステップごとに、円の大きさ（円錐の太さ）に合うミップ レベルを読む。不透明度が 1 に達したら終了</text>
</svg>

<div class="formula">color ← color + (1 − α) · c_i　、　α ← α + (1 − α) · a_i　（前から後ろへ）</div>

```hlsl
float4 ConeTrace(float3 origin, float3 dir, float aperture) {
  float4 acc = 0.0;
  float dist = kVoxelSize;
  [loop] for (int i = 0; i < kConeSteps && acc.a < 1.0; ++i) {
    float diameter = max(kVoxelSize, 2.0 * aperture * dist);
    float mip = log2(diameter / kVoxelSize);
    float3 uvw = WorldToVoxelUVW(origin + dir * dist);
    float4 s = voxel_tex.SampleLevel(linear_sampler, uvw, mip);
    acc += (1.0 - acc.a) * s;
    dist += diameter * 0.5;
  }
  return acc;
}
```

| 点 | 説明 |
| --- | --- |
| **`aperture`** | **円錐の開き**（`tan(半角)`）。**広いほど、ぼやけた結果** |
| **`diameter`** | **その距離での円錐の太さ**（`2 · aperture · dist`）。**ミップ選択**に使う |
| **`mip = log2(diameter / voxel_size)`** | **太さがボクセル何個分か**を**ミップ レベル**に**変換** |
| **前から後ろ** | **不透明度が 1 に達する**と、**以降は見えない**ので**打ち切る** |

### 拡散と鏡面

円錐の使い方は、用途によって変わります。拡散の間接光には、半球に 5〜6 本の広い円錐を余弦重み付きで配置します。鏡面の間接光には、反射方向に細い円錐を 1 本置き、粗さで開きを調整します。短い距離の円錐の不透明度からは、環境光遮蔽（AO）も同時に得られます。

## 利点と限界

| 利点 | 限界 |
| --- | --- |
| **画面外・裏側**も**反映**（**世界全体が対象**） | **ボクセルが粗い**（256³ で数 cm〜数十 cm の分解能） |
| **ノイズが少ない**（**円錐が積分済みの値を読む**） | **光漏れ**（**薄い壁**で**ボクセルが混ざる**） |
| **動く物・動くライトが反映される** | **メモリ**（3D テクスチャ ＋ ミップ ＋ 異方性） |
| <strong>鏡面（粗めの反射）</strong>も、**同じ構造**で得られる | **ボクセル化・注入・ミップ生成が毎フレームのコスト** |
| **AO も同時に得られる** | **カスケード**で**遠くを粗く**する工夫が必要（視点の周りのみ） |


限界は、ボクセルが粗いこと（256³ で数 cm〜数十 cm の分解能）、薄い壁でボクセルが混ざる光漏れ、3D テクスチャとミップと異方性によるメモリの大きさ、ボクセル化・注入・ミップ生成が毎フレームのコストになること、そして遠くを粗くするカスケードが必要になることです。

限界は、ボクセルが粗いこと（256³ で数 cm〜数十 cm の分解能）、薄い壁でボクセルが混ざる光漏れ、3D テクスチャとミップと異方性によるメモリの大きさ、ボクセル化・注入・ミップ生成が毎フレームのコストになること、そして遠くを粗くするカスケードが必要になることです。

### 光漏れ

**ボクセルが粗いと薄い壁の両側が同じボクセルに入り**、**壁を貫通して、光が漏れ**ます。

| 対策 | 内容 |
| --- | --- |
| **異方性ボクセル** | **方向ごとの値**を持ち、**表と裏を区別** |
| **ボクセルを細かく** | **解像度を上げる**（メモリ・コストが増える） |
| **壁の厚みを増やす** | **レベル デザインで薄い壁を避ける** |
| **オフセット** | **サンプル位置を法線方向にずらす** |

## カスケード（クリップマップ）

**シーン全体を細かいボクセルで覆う**ことは、**メモリが足りません**。**視点の周りに入れ子になった複数のボクセル グリッド**（**カスケード**）を置き、**近くは細かく、遠くは粗く**します（[Cascaded Shadow Maps (CSM)](../shadows/cascaded.md)と同じ発想）。**カメラの移動に応じて、グリッドをスクロール**させます。

## 現在の位置づけ

**Crassin の VXGI** は、**NVIDIA の VXGI**として製品化されましたが、**メモリ・コスト・光漏れ**の問題から、**現在の主流ではありません**。

ボクセル GI の後継や類似の方式が、いくつかあります。<strong>Lumen</strong>（Unreal Engine 5）は、ソフトウェアのレイトレースで距離場とサーフェス キャッシュを使い、画面空間、距離場、グローバル SDF の階層でトレースします。<strong>SDFGI</strong>（Godot）は、カスケードの SDF とプローブを組み合わせます。<strong>Radiance Cascades</strong> は、空間と方向の階層構造を持つ新しい方式です（[Ray-Traced GI](rt-gi/index.md)）。

<strong>「ボクセル（またはそれに類する 3D 格子）に光を保存し、円錐/レイでたどる」</strong>という**考え方**は、**多くの動的 GI に受け継がれています**。

## よくあるミス

??? failure "ボクセル化で小さい三角形が、漏れて、穴が空く"
    **保守的ラスタライズ**を使います。

??? failure "円錐のミップ選択が合わず、ぼやけすぎ・ブロック状になる"
    **`mip = log2(diameter / voxel_size)`** で、**太さに合わせて**選びます。

??? failure "薄い壁の向こうの光が、漏れる"
    **異方性ボクセル**・**壁を厚く**・**サンプル位置のオフセット**。

??? failure "メモリを使いすぎる"
    **カスケード**で**遠くを粗く**・**ボクセルの解像度を下げる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ボクセル GI ＝ <strong>シーンを 3D 格子に変換</strong>し、<strong>不透明度と出射光を保存</strong>、<strong>ミップ マップ</strong>を作る
    - [x] <strong>コーン トレース</strong>：<strong>円錐の太さに合うミップ</strong>を、<strong>前から後ろへ累積</strong>
    - [x] <strong>拡散は広い円錐を数本</strong>、<strong>鏡面は細い円錐 1 本</strong>
    - [x] <strong>画面外も反映・ノイズ少ない</strong>が<strong>解像度が粗い・光漏れ・メモリが重い</strong>
    - [x] <strong>現在は Lumen・SDFGI などの派生</strong>に、<strong>考え方が受け継がれている</strong>

## 参考

- Crassin et al., "Interactive Indirect Illumination Using Voxel Cone Tracing"（Pacific Graphics 2011）
- Crassin, "GigaVoxels"（博士論文、2011）
- Godot, "SDFGI"（ドキュメント）

## 関連ページ

- [Global Illumination (GI)](index.md)
- [GI Theory](theory/index.md)
- [SSGI](ssgi.md)
- [Ray-Traced GI](rt-gi/index.md)
- [Cascaded Shadow Maps (CSM)](../shadows/cascaded.md)
