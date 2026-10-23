---
title: PCSS
tags:
  - 描画
---

# PCSS

[PCF](pcf.md)は、<strong>どこでも同じ幅</strong>で影の縁をぼかします。しかし、現実の影は遮蔽物に近い所は鋭く、離れるほどぼやけます（半影が広がる）。PCSS（Percentage-Closer Soft Shadows）は、遮蔽物までの距離をシャドウ マップから見積もり、その距離に応じて、PCF のカーネルの大きさを変える方式です。2005 年に NVIDIA の Fernando が提案しました。面光源が作る半影をシャドウ マップ 1 枚で、近似できます。

!!! tip "ポイント"
    - 半影の幅は<strong>(受け手の距離 − 遮蔽物の距離) × 光源の大きさ ÷ 遮蔽物の距離</strong>（相似三角形）。
    - 3 段階：<strong>① 遮蔽物の探索（平均の遮蔽物の深度を求める）</strong> → ② 半影の幅を計算 → ③ その幅で PCF。
    - 遮蔽物に近い → 鋭い、遠い → ソフト（接触硬化）。
    - 光源の大きさ（光源サイズ）が、ぼけの強さを決めるパラメータ。
    - コストは探索 ＋ 大きな PCFで、重い。サンプル数を減らす工夫が要る。
    - シャドウ マップは1 枚だけ。1 つの遮蔽物（平均）を仮定する近似。

!!! info "このページを読む前に"
    - [Shadows](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 半影の幾何

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="半影の幅の計算">
<text x="20" y="24" class="fig-title">相似三角形：半影の幅 ＝ (d_receiver − d_blocker) × 光源の幅 ÷ d_blocker</text>
<rect x="100" y="50" width="150" height="16" fill="rgba(229,170,40,0.7)" stroke="currentColor" stroke-width="2"/><text x="108" y="44" style="font-size:12px">面光源（幅 w_light）</text>
<rect x="150" y="140" width="50" height="16" fill="rgba(150,150,150,0.7)" stroke="currentColor" stroke-width="2"/><text x="206" y="154" style="font-size:12px">遮蔽物（距離 d_blocker）</text>
<line x1="20" y1="250" x2="560" y2="250" stroke="currentColor" stroke-width="4"/><text x="20" y="274" style="font-size:12px">受け手（距離 d_receiver）</text>
<line x1="100" y1="66" x2="360" y2="250" stroke="currentColor" stroke-dasharray="4 3"/><line x1="250" y1="66" x2="-10" y2="250" stroke="currentColor" stroke-dasharray="4 3"/>
<line x1="100" y1="66" x2="-10" y2="250" stroke="currentColor" stroke-dasharray="4 3" opacity="0.4"/><line x1="250" y1="66" x2="360" y2="250" stroke="currentColor" stroke-dasharray="4 3" opacity="0.4"/>
<rect x="140" y="246" width="70" height="8" fill="#111" opacity="0.85"/>
<rect x="70" y="246" width="70" height="8" fill="#666" opacity="0.6"/><rect x="210" y="246" width="70" height="8" fill="#666" opacity="0.6"/>
<text x="290" y="238" style="font-size:12px">半影の幅 w_penumbra</text>
<text x="400" y="110" style="font-weight:700">w_penumbra = (d_r − d_b) · w_light / d_b</text>
<text x="400" y="136" style="font-size:12px">遮蔽物が受け手に近い（d_r ≒ d_b）→ 半影が 0（鋭い）</text>
<text x="400" y="156" style="font-size:12px">遮蔽物が光源に近い・受け手が遠い → 半影が広い</text>
</svg>

<strong>光源から</strong>、遮蔽物までの距離を `d_b`、受け手までを `d_r`、光源の幅を `w_light` とすると、相似な三角形から、半影の幅は次のとおりです。

<div class="formula">w_penumbra = (d_r − d_b) · w_light / d_b</div>

| 場合 | 半影の幅 |
| --- | --- |
| 遮蔽物が受け手に接している（d_r = d_b） | 0（鋭い影） |
| 遮蔽物と受け手が離れている（d_r が d_b より大きい） | 広い（ソフト） |
| 光源が大きい（w_light が大きい） | 広い |
| 遮蔽物が光源に近い（d_b が小さい） | 広い |

物体の足元は鋭く、離れるほどぼやけるという、現実の影の性質がこの式で再現できます。

<!-- fig:pcss-penumbra:begin -->

<svg class="fig illust motion" data-fig="pcss-penumbra" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-pcss-penumbra" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">PCSS: 遮る物から受ける面までが遠いほど、影の縁(半影)が広がる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。面積のある光(幅 4)の下に遮る板。受ける床を 3 通りの高さに動かして、実際に光を数える</text>
<rect x="30" y="96" width="900" height="300" fill="#ffffff" stroke="#e5aa28" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">① 光・遮る板・受ける面(断面)</text>
<rect x="372.0" y="110.0" width="208.0" height="10" fill="#e5aa28"/>
<text x="476.0" y="104.0" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#92400e">面積のある光(幅 4)</text>
<rect x="398.0" y="180.0" width="156.0" height="8" fill="#475569"/>
<text x="476.0" y="174.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#475569">遮る板</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3198;0.3200;1.0000" values="1;1;0;0"/><line x1="60.0" y1="210.0" x2="892.0" y2="210.0" stroke="#94a3b8" stroke-width="3"/>
<line x1="372.0" y1="120.0" x2="411.0" y2="210.0" stroke="#fbbf24" stroke-width="1" stroke-dasharray="3 4" opacity="0.9"/>
<line x1="372.0" y1="120.0" x2="645.0" y2="210.0" stroke="#fbbf24" stroke-width="1" stroke-dasharray="3 4" opacity="0.9"/>
<line x1="580.0" y1="120.0" x2="307.0" y2="210.0" stroke="#fbbf24" stroke-width="1" stroke-dasharray="3 4" opacity="0.9"/>
<line x1="580.0" y1="120.0" x2="541.0" y2="210.0" stroke="#fbbf24" stroke-width="1" stroke-dasharray="3 4" opacity="0.9"/>
<text x="40" y="228.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">受ける面: 光から 4.5(板から 1.5)</text>
<rect x="60.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667" values="#e5e7eb;#fde68a"/></rect>
<rect x="80.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0689" values="#e5e7eb;#fde68a"/></rect>
<rect x="101.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0711" values="#e5e7eb;#fde68a"/></rect>
<rect x="122.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0733" values="#e5e7eb;#fde68a"/></rect>
<rect x="143.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#fde68a"/></rect>
<rect x="164.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0778" values="#e5e7eb;#fde68a"/></rect>
<rect x="184.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#fde68a"/></rect>
<rect x="205.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0822" values="#e5e7eb;#fde68a"/></rect>
<rect x="226.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#fde68a"/></rect>
<rect x="247.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0867" values="#e5e7eb;#fde68a"/></rect>
<rect x="268.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0889" values="#e5e7eb;#fde68a"/></rect>
<rect x="288.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0911" values="#e5e7eb;#fde68a"/></rect>
<rect x="309.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#e4d183"/></rect>
<rect x="330.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0956" values="#e5e7eb;#bbb079"/></rect>
<rect x="351.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978" values="#e5e7eb;#928e6e"/></rect>
<rect x="372.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000" values="#e5e7eb;#6c6f64"/></rect>
<rect x="392.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022" values="#e5e7eb;#434e59"/></rect>
<rect x="413.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1044" values="#e5e7eb;#334155"/></rect>
<rect x="434.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1067" values="#e5e7eb;#334155"/></rect>
<rect x="455.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1089" values="#e5e7eb;#334155"/></rect>
<rect x="476.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111" values="#e5e7eb;#334155"/></rect>
<rect x="496.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1133" values="#e5e7eb;#334155"/></rect>
<rect x="517.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1156" values="#e5e7eb;#334155"/></rect>
<rect x="538.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1178" values="#e5e7eb;#434e59"/></rect>
<rect x="559.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#6c6f64"/></rect>
<rect x="580.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1222" values="#e5e7eb;#928e6e"/></rect>
<rect x="600.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1244" values="#e5e7eb;#bbb079"/></rect>
<rect x="621.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1267" values="#e5e7eb;#e4d183"/></rect>
<rect x="642.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1289" values="#e5e7eb;#fde68a"/></rect>
<rect x="663.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1311" values="#e5e7eb;#fde68a"/></rect>
<rect x="684.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1333" values="#e5e7eb;#fde68a"/></rect>
<rect x="704.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1356" values="#e5e7eb;#fde68a"/></rect>
<rect x="725.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1378" values="#e5e7eb;#fde68a"/></rect>
<rect x="746.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1400" values="#e5e7eb;#fde68a"/></rect>
<rect x="767.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1422" values="#e5e7eb;#fde68a"/></rect>
<rect x="788.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1444" values="#e5e7eb;#fde68a"/></rect>
<rect x="808.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1467" values="#e5e7eb;#fde68a"/></rect>
<rect x="829.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1489" values="#e5e7eb;#fde68a"/></rect>
<rect x="850.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1511" values="#e5e7eb;#fde68a"/></rect>
<rect x="871.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1533" values="#e5e7eb;#fde68a"/></rect>
<rect x="60.0" y="346" width="832.0" height="20.8" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3198;0.3200;0.5954;0.5956;1.0000" values="0;0;1;1;0;0"/><line x1="60.0" y1="260.0" x2="892.0" y2="260.0" stroke="#94a3b8" stroke-width="3"/>
<line x1="372.0" y1="120.0" x2="432.67" y2="260.0" stroke="#fbbf24" stroke-width="1" stroke-dasharray="3 4" opacity="0.9"/>
<line x1="372.0" y1="120.0" x2="796.67" y2="260.0" stroke="#fbbf24" stroke-width="1" stroke-dasharray="3 4" opacity="0.9"/>
<line x1="580.0" y1="120.0" x2="155.33" y2="260.0" stroke="#fbbf24" stroke-width="1" stroke-dasharray="3 4" opacity="0.9"/>
<line x1="580.0" y1="120.0" x2="519.33" y2="260.0" stroke="#fbbf24" stroke-width="1" stroke-dasharray="3 4" opacity="0.9"/>
<text x="40" y="278.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">受ける面: 光から 7(板から 4)</text>
<rect x="60.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3422" values="#e5e7eb;#fde68a"/></rect>
<rect x="80.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3444" values="#e5e7eb;#fde68a"/></rect>
<rect x="101.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3467" values="#e5e7eb;#fde68a"/></rect>
<rect x="122.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3489" values="#e5e7eb;#fde68a"/></rect>
<rect x="143.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3511" values="#e5e7eb;#fde68a"/></rect>
<rect x="164.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3533" values="#e5e7eb;#f0dc87"/></rect>
<rect x="184.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3556" values="#e5e7eb;#e1cf83"/></rect>
<rect x="205.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3578" values="#e5e7eb;#d1c27e"/></rect>
<rect x="226.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3600" values="#e5e7eb;#c1b57a"/></rect>
<rect x="247.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3622" values="#e5e7eb;#b1a876"/></rect>
<rect x="268.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3644" values="#e5e7eb;#a59e73"/></rect>
<rect x="288.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3667" values="#e5e7eb;#95916f"/></rect>
<rect x="309.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3689" values="#e5e7eb;#85846b"/></rect>
<rect x="330.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3711" values="#e5e7eb;#757766"/></rect>
<rect x="351.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733" values="#e5e7eb;#666a62"/></rect>
<rect x="372.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3756" values="#e5e7eb;#59605f"/></rect>
<rect x="392.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3778" values="#e5e7eb;#49535b"/></rect>
<rect x="413.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3800" values="#e5e7eb;#394657"/></rect>
<rect x="434.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3822" values="#e5e7eb;#334155"/></rect>
<rect x="455.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3844" values="#e5e7eb;#334155"/></rect>
<rect x="476.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3867" values="#e5e7eb;#334155"/></rect>
<rect x="496.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3889" values="#e5e7eb;#334155"/></rect>
<rect x="517.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3911" values="#e5e7eb;#394657"/></rect>
<rect x="538.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3933" values="#e5e7eb;#49535b"/></rect>
<rect x="559.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3956" values="#e5e7eb;#59605f"/></rect>
<rect x="580.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3978" values="#e5e7eb;#666a62"/></rect>
<rect x="600.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4000" values="#e5e7eb;#757766"/></rect>
<rect x="621.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4022" values="#e5e7eb;#85846b"/></rect>
<rect x="642.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4044" values="#e5e7eb;#95916f"/></rect>
<rect x="663.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4067" values="#e5e7eb;#a59e73"/></rect>
<rect x="684.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4089" values="#e5e7eb;#b1a876"/></rect>
<rect x="704.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4111" values="#e5e7eb;#c1b57a"/></rect>
<rect x="725.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4133" values="#e5e7eb;#d1c27e"/></rect>
<rect x="746.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4156" values="#e5e7eb;#e1cf83"/></rect>
<rect x="767.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4178" values="#e5e7eb;#f0dc87"/></rect>
<rect x="788.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4200" values="#e5e7eb;#fde68a"/></rect>
<rect x="808.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4222" values="#e5e7eb;#fde68a"/></rect>
<rect x="829.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4244" values="#e5e7eb;#fde68a"/></rect>
<rect x="850.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4267" values="#e5e7eb;#fde68a"/></rect>
<rect x="871.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4289" values="#e5e7eb;#fde68a"/></rect>
<rect x="60.0" y="346" width="832.0" height="20.8" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5954;0.5956;1.0000" values="0;0;1;1"/><line x1="60.0" y1="340.0" x2="892.0" y2="340.0" stroke="#94a3b8" stroke-width="3"/>
<line x1="372.0" y1="120.0" x2="467.33" y2="340.0" stroke="#fbbf24" stroke-width="1" stroke-dasharray="3 4" opacity="0.9"/>
<line x1="372.0" y1="120.0" x2="1039.33" y2="340.0" stroke="#fbbf24" stroke-width="1" stroke-dasharray="3 4" opacity="0.9"/>
<line x1="580.0" y1="120.0" x2="-87.33" y2="340.0" stroke="#fbbf24" stroke-width="1" stroke-dasharray="3 4" opacity="0.9"/>
<line x1="580.0" y1="120.0" x2="484.67" y2="340.0" stroke="#fbbf24" stroke-width="1" stroke-dasharray="3 4" opacity="0.9"/>
<text x="40" y="358.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">受ける面: 光から 11(板から 8)</text>
<rect x="60.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6178" values="#e5e7eb;#c4b87b"/></rect>
<rect x="80.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6200" values="#e5e7eb;#bbb079"/></rect>
<rect x="101.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6222" values="#e5e7eb;#b4ab77"/></rect>
<rect x="122.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6244" values="#e5e7eb;#aea675"/></rect>
<rect x="143.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6267" values="#e5e7eb;#a59e73"/></rect>
<rect x="164.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6289" values="#e5e7eb;#9e9971"/></rect>
<rect x="184.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6311" values="#e5e7eb;#95916f"/></rect>
<rect x="205.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6333" values="#e5e7eb;#8f8c6d"/></rect>
<rect x="226.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6356" values="#e5e7eb;#88876b"/></rect>
<rect x="247.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6378" values="#e5e7eb;#7f7f69"/></rect>
<rect x="268.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6400" values="#e5e7eb;#787a67"/></rect>
<rect x="288.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6422" values="#e5e7eb;#6f7265"/></rect>
<rect x="309.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6444" values="#e5e7eb;#696d63"/></rect>
<rect x="330.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6467" values="#e5e7eb;#626861"/></rect>
<rect x="351.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6489" values="#e5e7eb;#59605f"/></rect>
<rect x="372.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6511" values="#e5e7eb;#535b5d"/></rect>
<rect x="392.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6533" values="#e5e7eb;#49535b"/></rect>
<rect x="413.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6556" values="#e5e7eb;#434e59"/></rect>
<rect x="434.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6578" values="#e5e7eb;#3c4957"/></rect>
<rect x="455.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6600" values="#e5e7eb;#334155"/></rect>
<rect x="476.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6622" values="#e5e7eb;#334155"/></rect>
<rect x="496.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6644" values="#e5e7eb;#3c4957"/></rect>
<rect x="517.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#434e59"/></rect>
<rect x="538.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6689" values="#e5e7eb;#49535b"/></rect>
<rect x="559.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6711" values="#e5e7eb;#535b5d"/></rect>
<rect x="580.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6733" values="#e5e7eb;#59605f"/></rect>
<rect x="600.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6756" values="#e5e7eb;#626861"/></rect>
<rect x="621.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6778" values="#e5e7eb;#696d63"/></rect>
<rect x="642.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#e5e7eb;#6f7265"/></rect>
<rect x="663.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6822" values="#e5e7eb;#787a67"/></rect>
<rect x="684.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6844" values="#e5e7eb;#7f7f69"/></rect>
<rect x="704.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6867" values="#e5e7eb;#88876b"/></rect>
<rect x="725.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6889" values="#e5e7eb;#8f8c6d"/></rect>
<rect x="746.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6911" values="#e5e7eb;#95916f"/></rect>
<rect x="767.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6933" values="#e5e7eb;#9e9971"/></rect>
<rect x="788.0" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6956" values="#e5e7eb;#a59e73"/></rect>
<rect x="808.8" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6978" values="#e5e7eb;#aea675"/></rect>
<rect x="829.6" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7000" values="#e5e7eb;#b4ab77"/></rect>
<rect x="850.4" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7022" values="#e5e7eb;#bbb079"/></rect>
<rect x="871.2" y="346.0" width="21.1" height="21.1" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7044" values="#e5e7eb;#c4b87b"/></rect>
<rect x="60.0" y="346" width="832.0" height="20.8" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<text x="60" y="340" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">受ける面での光の当たり方(黄 = 全部届く、暗い = 全部隠れる)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3198;0.3200;1.0000" values="1;1;0;0"/><text x="60" y="418" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d">半影の幅(実測): 1.90</text>
<text x="360" y="418" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">相似三角形: 光の幅 × 板から受ける面まで ÷ 光から板まで = 4 × 1.5 ÷ 3 = 2.00</text>
<text x="60" y="446" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">板に近い: 縁がくっきり(接触した影)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3198;0.3200;0.5954;0.5956;1.0000" values="0;0;1;1;0;0"/><text x="60" y="418" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d">半影の幅(実測): 5.08</text>
<text x="360" y="418" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">相似三角形: 光の幅 × 板から受ける面まで ÷ 光から板まで = 4 × 4 ÷ 3 = 5.33</text>
<text x="60" y="446" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">少し離れる: 縁がぼやけ始める</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5954;0.5956;1.0000" values="0;0;1;1"/><text x="60" y="418" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d">半影の幅(実測): 7.58</text>
<text x="360" y="418" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">相似三角形: 光の幅 × 板から受ける面まで ÷ 光から板まで = 4 × 8 ÷ 3 = 10.67</text>
<text x="60" y="446" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">さらに離れる: 縁が広くぼやける</text>
</g>
<text x="60" y="482" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">PCSS の 3 手順:</text>
<text x="190" y="482" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">① 板までの距離を調べる(ブロッカー探索)→ ② 半影の幅を計算 → ③ その幅で PCF</text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">面積のある光は、遮られ方が場所で変わるので、縁がぼける<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0443;0.0444;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">受ける面を動かして、光を 64 個の点に分けて数える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0443;0.0444;0.8709;0.8711;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">半影の幅は、板から受ける面までの距離に比例する。これを PCF の広さに使うのが PCSS<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8709;0.8711;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:pcss-penumbra:end -->

## 3 つの手順

### ① 遮蔽物の探索（Blocker Search）

<strong>受け手の点</strong>から、光源の方向にシャドウ マップのある範囲を探索し、「受け手より手前にある（遮蔽物の）深度」の平均を求めます。

探索する範囲の大きさは、光源の大きさと受け手の位置で決まります（光源の幅をシャドウ マップ上に投影した幅）。

<div class="formula">w_search = w_light · (d_r − near) / d_r　（透視投影の場合）</div>

```hlsl
float AverageBlockerDepth(float2 uv, float receiver_depth, float search_radius_uv) {
  float sum = 0.0;
  int count = 0;
  [unroll] for (int i = 0; i < kBlockerSamples; ++i) {
    float2 offset = kPoissonDisk[i] * search_radius_uv;
    float stored = shadow_tex_raw.SampleLevel(point_sampler, uv + offset, 0).r;
    if (stored < receiver_depth - bias) {
      sum += stored;
      count++;
    }
  }
  return count > 0 ? sum / count : -1.0;
}
```

| 点 | 説明 |
| --- | --- |
| 生の深度を読む | 比較サンプラーでなく、通常のサンプラーで深度そのものを読む（`shadow_tex_raw`） |
| 受け手より手前のものだけ | `stored < receiver_depth` を、遮蔽物として平均 |
| `count == 0` | 遮蔽物が見つからない → 日向（影なし）。以降の計算は不要 |
| サンプル数 | 8〜16（ポワソン円盤）。探索範囲の大きさが品質とコストを決める |

### ② 半影の幅を計算

見つかった平均の遮蔽物の深度 `d_b` から、半影の幅を計算します。

<div class="formula">w_penumbra = (d_r − d_b) · w_light / d_b</div>

深度を線形（光からの距離）にしてから計算します（非線形の深度のままだと、式が成り立ちません）。

```hlsl
float penumbra_width = (receiver_z - blocker_z) * light_size_uv / blocker_z;
```

### ③ 可変幅の PCF

半影の幅を、PCF のカーネルの半径にして、通常の PCF を行います。

```hlsl
float PCSS(float2 uv, float receiver_depth, float receiver_z) {
  float search_radius = light_size_uv * (receiver_z - near_z) / receiver_z;
  float blocker_depth = AverageBlockerDepth(uv, receiver_depth, search_radius);
  if (blocker_depth < 0.0) return 1.0;

  float blocker_z = LinearizeLightDepth(blocker_depth);
  float penumbra = (receiver_z - blocker_z) * light_size_uv / blocker_z;
  float filter_radius = penumbra * near_z / receiver_z;

  return PCFPoisson(uv, receiver_depth, filter_radius, rotation);
}
```

フィルタ側のコードの要点です。`filter_radius = penumbra · near / d_r` で、半影の幅を近クリップ面での大きさに直します（透視投影のシャドウ マップ上の幅です）。遮蔽物がなければ 1.0 を返して、無駄な PCF を避けます。PCF は通常の `SampleCmp` で、ポワソン円盤の半径を可変にします。

## 平行光（太陽）の PCSS

<strong>太陽</strong>は平行光で正射影のシャドウ マップです。光源の大きさは、視直径（約 0.53 度、半角で約 0.27 度）で表します。半影の幅は深度の差に角度のタンジェントを掛けたものです。

<div class="formula">w_penumbra = (d_r − d_b) · tan(θ_light)　（θ_light：光源の角半径）</div>

正射影（太陽など）での式の項です。`d_r − d_b` は、受け手と遮蔽物の光の方向の距離差（ワールド単位）です。`tan θ` は光源の見かけの大きさで、太陽は約 0.0047 です。シャドウ マップ上の幅は、ワールド単位の幅をマップの 1 テクセルの大きさで割って求めます。

正射影では探索範囲も一定（遠近の補正が不要）なので単純です。

## 現実の影との違い

PCSS は、<strong>1 枚のシャドウ マップ</strong>から、半影を近似します。以下の仮定・限界があります。

| 限界 | 説明 |
| --- | --- |
| 遮蔽物は平均 1 枚の面 | 複数の遮蔽物（深度が異なる）を、平均した 1 つの面として扱う。複雑な形（葉・髪）で、不正確 |
| シャドウ マップが遮蔽物しか持たない | 光から見て、一番手前の面だけ。奥の遮蔽物は見えない |
| 探索範囲の限界 | 探索範囲外の遮蔽物は、見逃す |
| 光源の形 | 円・矩形程度。複雑な形の面光源は、近似 |

## コストと工夫

PCSS は<strong>探索（8〜16 サンプル）＋ PCF（16 サンプル以上）</strong>で、画素あたり 30 回以上シャドウ マップを読む、重い方式です。

| 工夫 | 内容 |
| --- | --- |
| 探索のサンプル数を減らす | 4〜8 個に。画素ごとの回転 ＋ 時間蓄積 |
| PCF のサンプル数を減らす | 同上。半影が小さい所は、少なく |
| 探索範囲を制限 | 範囲を狭める（遠くの遮蔽物を諦める） |
| 早期終了 | 探索で遮蔽物がなければ即終了（日向）。ほぼ全て遮蔽なら、影（完全な影）として終了 |
| ノイズ ＋ TAA | サンプルを少なくし、ノイズを TAA（または時間蓄積）で消す |
| 半分の解像度で計算 | 影のマスクを半分の解像度で作り、アップサンプル（バイラテラル） |
| カスケードの近くだけ | 遠くは通常の PCF、近くだけ PCSS |

## 他の方式との比較

| 方式 | 接触硬化 | コスト | 備考 |
| --- | --- | --- | --- |
| PCF | なし（一定のぼけ） | 小〜中 | 簡単 |
| PCSS | あり | 大 | 光源サイズの調整が直感的 |
| VSM 系（[VSM](vsm/index.md)） | 近似的（フィルタの大きさを変える） | 中 | フィルタが安い。光漏れ |
| レイトレ影（[Ray-Traced Shadows](ray-traced.md)） | <strong>あり（正確）</strong> | 大（HW が必要） | 面光源を直接サンプル |
| 距離場の影（[Distance Field Shadows](sdf-shadows.md)） | あり（円錐） | 中 | 静的向き |

## 調整のしかた

| パラメータ | 意味 | 目安 |
| --- | --- | --- |
| 光源サイズ | 大きいほど、ソフト（半影が広がる） | 太陽なら、実際の視直径（または見た目で大きめ） |
| 探索サンプル数 | 遮蔽物の平均の精度 | 4〜16 |
| PCF サンプル数 | ぼかしの滑らかさ | 8〜32 |
| 最小・最大の半影幅 | 鋭さ・ぼけすぎの制限 | 最小は数テクセル（エイリアシングを隠す） |
| 探索範囲の上限 | 計算コストの制限 | シーンの大きさ |

<strong>半影の幅に最小値</strong>（たとえば 1〜2 テクセル）を設けると接触部でもエイリアシングが目立ちません。

## よくあるミス

??? failure "非線形の深度のまま、半影の式に入れて、ぼけが変"
    <strong>線形（光からの距離）に変換</strong>してから計算します。

??? failure "遮蔽物の探索で、比較サンプラーを使って、深度が得られない"
    通常のサンプラーで生の深度を読みます。

??? failure "遮蔽物が見つからないのに、PCF をして、無駄・誤判定"
    `count == 0` で、日向として終了します。

??? failure "探索範囲が小さすぎて、遠くの遮蔽物を見逃し、半影が狭すぎる"
    光源サイズ・受け手の距離から、探索範囲を適切に取ります。

??? failure "サンプルが少なすぎて、ノイズがひどい"
    画素ごとの回転 ＋ TAA、またはサンプルを増やす。

## これだけ覚える

!!! abstract "まとめ"
    - [x] PCSS ＝ <strong>遮蔽物との距離で、PCF のぼけの幅を変える</strong>（接触硬化を再現）
    - [x] 半影の幅 ＝ (d_receiver − d_blocker) × 光源の大きさ ÷ d_blocker
    - [x] 手順：① 遮蔽物の平均深度を探索 → ② 半影の幅を計算 → ③ その幅で PCF
    - [x] 深度は線形にして計算。遮蔽物が無ければ、日向で終了
    - [x] 重いのでサンプルを減らして、ノイズ ＋ 時間蓄積で補う

## 参考

- Fernando, "Percentage-Closer Soft Shadows", SIGGRAPH 2005 Sketches
- Reeves, Salesin, Cook, "Rendering Antialiased Shadows with Depth Maps", SIGGRAPH 1987
- Annen, Mertens, Bekaert, Seidel, Sillion, "Convolution Shadow Maps", Eurographics Symposium on Rendering 2007
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Shadows](index.md)
- [PCF](pcf.md)
- [VSM, ESM and MSM](vsm/index.md)
- [Ray-Traced Shadows](ray-traced.md)
- [Shadow Bias](bias/index.md)
