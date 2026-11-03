---
title: Contact Shadows
tags:
  - 描画
---

# Contact Shadows

シャドウ マップは、解像度に限りがあります。さらに、面の上に縞が出る（アクネ）のを避けるために、バイアスで少し浮かせます。そのため、物体が地面に接する付近では、細かい影が欠けたり、浮いて見えたりします（ピーター パンニング）。コンタクト シャドウ（Contact Shadows）は、この接触部を補う方式です。画面空間（深度バッファ）で、画素から光の方向へ短いレイを進めて、手前の物に当たるかを調べます。短いレイだけなので、安く描けます。

!!! tip "ポイント"
    - 画素から光の方向へ、深度バッファの上で短いレイを進めます。
    - レイの深度が、深度バッファの面より奥に入ったら、遮蔽されたと判断します。
    - レイは短く（数十 cm〜1 m）します。目的は、シャドウ マップの接触部の欠けを補うことです。
    - 深度バッファには見えている面しかないので、画面の外や物の裏側は、遮蔽物にできません。面の厚みは、仮定で決めます。
    - ステップ数を減らしたぶんの縞は、画素ごとのジッターでノイズに変えて、TAA で消します。
    - [SSR](../reflections/ssr-basics/index.md)・[SSAO](../ao/ssao-hemisphere.md) と同じ画面空間の方式なので、同じ限界を持ちます。

!!! info "このページを読む前に"
    - [Shadows](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）

## なぜ接触部で影が欠けるのか

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="接触部の影の欠け">
<text x="20" y="24" class="fig-title">シャドウ マップは、接触部で影が浮く・欠ける（ピーター パンニング）</text>
<line x1="60" y1="200" x2="720" y2="200" stroke="currentColor" stroke-width="4"/>
<rect x="150" y="150" width="70" height="50" fill="rgba(150,150,150,0.8)" stroke="currentColor" stroke-width="2"/><text x="140" y="140" style="font-size:12px">物体（地面に接している）</text>
<rect x="220" y="196" width="140" height="8" fill="#111" opacity="0.85"/><rect x="220" y="196" width="22" height="8" fill="#e5484d" opacity="0.5"/>
<text x="250" y="226" style="font-size:12px;fill:#e5484d;font-weight:700">接触部の影が欠ける</text>
<text x="420" y="70" style="font-size:13px">原因：</text><text x="420" y="94" style="font-size:12px">・バイアスで深度を浮かせる → 近い所は影が出ない</text><text x="420" y="114" style="font-size:12px">・シャドウ マップの 1 テクセルが物の大きさに比べて粗い</text>
<text x="420" y="152" style="font-size:13px">解決：</text><text x="420" y="176" style="font-size:11px">画面の深度で、短い距離を調べる → 接触部だけ、細かく影を補う</text>
</svg>

<!-- fig:contact-shadow-march:begin -->

<svg class="fig illust motion" data-fig="contact-shadow-march" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-contact-shadow-march" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">コンタクト シャドウ: 画面の深度を光の方向へたどって、物の足元の細かい影を作る</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。地面に高さ 1.5 の小さな物。シャドウ マップ(荒い)で見逃す足元の影を画面の深度で補う</text>
<rect x="30" y="96" width="900" height="190" fill="#ffffff" stroke="#e5aa28" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">① 断面(光は左上から)</text>
<line x1="40" y1="244.0" x2="872.0" y2="244.0" stroke="#94a3b8" stroke-width="3"/>
<rect x="378.0" y="190.0" width="26.0" height="54.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="404.0" y="190.0" width="26.0" height="54.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="430.0" y="190.0" width="26.0" height="54.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="612.0" y="100.0" width="26.0" height="144.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="638.0" y="100.0" width="26.0" height="144.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
<text x="417.0" y="184.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">小さな物</text>
<text x="638.0" y="94.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">高い物</text>
<line x1="66.0" y1="64.0" x2="220.93" y2="244.0" stroke="#fbbf24" stroke-width="1.2" stroke-dasharray="4 5" opacity="0.8"/>
<line x1="144.0" y1="64.0" x2="298.93" y2="244.0" stroke="#fbbf24" stroke-width="1.2" stroke-dasharray="4 5" opacity="0.8"/>
<line x1="222.0" y1="64.0" x2="376.93" y2="244.0" stroke="#fbbf24" stroke-width="1.2" stroke-dasharray="4 5" opacity="0.8"/>
<line x1="300.0" y1="64.0" x2="454.93" y2="244.0" stroke="#fbbf24" stroke-width="1.2" stroke-dasharray="4 5" opacity="0.8"/>
<line x1="378.0" y1="64.0" x2="532.93" y2="244.0" stroke="#fbbf24" stroke-width="1.2" stroke-dasharray="4 5" opacity="0.8"/>
<text x="40" y="314" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">正解(光線を細かく調べる)</text>
<rect x="40.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#fde68a"/></rect>
<rect x="66.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#e5e7eb;#fde68a"/></rect>
<rect x="92.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#fde68a"/></rect>
<rect x="118.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#e5e7eb;#fde68a"/></rect>
<rect x="144.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#e5e7eb;#fde68a"/></rect>
<rect x="170.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#fde68a"/></rect>
<rect x="196.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#e5e7eb;#fde68a"/></rect>
<rect x="222.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#e5e7eb;#fde68a"/></rect>
<rect x="248.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#e5e7eb;#fde68a"/></rect>
<rect x="274.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#fde68a"/></rect>
<rect x="300.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#e5e7eb;#fde68a"/></rect>
<rect x="326.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#e5e7eb;#fde68a"/></rect>
<rect x="352.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1367" values="#e5e7eb;#fde68a"/></rect>
<rect x="378.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1423" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="404.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1479" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="430.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1535" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="456.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1591" values="#e5e7eb;#334155"/></rect>
<rect x="482.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1647" values="#e5e7eb;#334155"/></rect>
<rect x="508.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1702" values="#e5e7eb;#fde68a"/></rect>
<rect x="534.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1758" values="#e5e7eb;#fde68a"/></rect>
<rect x="560.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1814" values="#e5e7eb;#fde68a"/></rect>
<rect x="586.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1870" values="#e5e7eb;#fde68a"/></rect>
<rect x="612.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1926" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="638.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1981" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="664.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2037" values="#e5e7eb;#334155"/></rect>
<rect x="690.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2093" values="#e5e7eb;#334155"/></rect>
<rect x="716.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2149" values="#e5e7eb;#334155"/></rect>
<rect x="742.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2205" values="#e5e7eb;#334155"/></rect>
<rect x="768.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2260" values="#e5e7eb;#334155"/></rect>
<rect x="794.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2316" values="#e5e7eb;#fde68a"/></rect>
<rect x="820.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2372" values="#e5e7eb;#fde68a"/></rect>
<rect x="846.0" y="318.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2428" values="#e5e7eb;#fde68a"/></rect>
<rect x="40.0" y="318" width="832.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="40" y="356" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">荒いシャドウ マップ(+ バイアス)</text>
<rect x="40.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2856" values="#e5e7eb;#fde68a"/></rect>
<rect x="66.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2912" values="#e5e7eb;#fde68a"/></rect>
<rect x="92.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2967" values="#e5e7eb;#fde68a"/></rect>
<rect x="118.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3023" values="#e5e7eb;#fde68a"/></rect>
<rect x="144.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3079" values="#e5e7eb;#fde68a"/></rect>
<rect x="170.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3135" values="#e5e7eb;#fde68a"/></rect>
<rect x="196.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3191" values="#e5e7eb;#fde68a"/></rect>
<rect x="222.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3247" values="#e5e7eb;#fde68a"/></rect>
<rect x="248.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3302" values="#e5e7eb;#fde68a"/></rect>
<rect x="274.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3358" values="#e5e7eb;#fde68a"/></rect>
<rect x="300.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3414" values="#e5e7eb;#fde68a"/></rect>
<rect x="326.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3470" values="#e5e7eb;#fde68a"/></rect>
<rect x="352.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3526" values="#e5e7eb;#fde68a"/></rect>
<rect x="378.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3581" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="404.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3637" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="430.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3693" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="456.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3749" values="#e5e7eb;#fde68a"/></rect>
<rect x="482.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3805" values="#e5e7eb;#fde68a"/></rect>
<rect x="508.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3860" values="#e5e7eb;#fde68a"/></rect>
<rect x="534.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3916" values="#e5e7eb;#fde68a"/></rect>
<rect x="560.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3972" values="#e5e7eb;#fde68a"/></rect>
<rect x="586.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4028" values="#e5e7eb;#fde68a"/></rect>
<rect x="612.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4084" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="638.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4140" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="664.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4195" values="#e5e7eb;#334155"/></rect>
<rect x="690.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4251" values="#e5e7eb;#334155"/></rect>
<rect x="716.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4307" values="#e5e7eb;#334155"/></rect>
<rect x="742.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4363" values="#e5e7eb;#334155"/></rect>
<rect x="768.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4419" values="#e5e7eb;#334155"/></rect>
<rect x="794.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474" values="#e5e7eb;#fde68a"/></rect>
<rect x="820.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4530" values="#e5e7eb;#fde68a"/></rect>
<rect x="846.0" y="360.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4586" values="#e5e7eb;#fde68a"/></rect>
<rect x="40.0" y="360" width="832.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="456.0" y="360.0" width="26.0" height="26.0" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3747;0.3749;1.0000" values="0;0;1;1"/></rect>
<rect x="482.0" y="360.0" width="26.0" height="26.0" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3803;0.3805;1.0000" values="0;0;1;1"/></rect>
<text x="40" y="398" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">画面の深度をたどる(コンタクト)</text>
<rect x="40.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5014" values="#e5e7eb;#fde68a"/></rect>
<rect x="66.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5070" values="#e5e7eb;#fde68a"/></rect>
<rect x="92.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5126" values="#e5e7eb;#fde68a"/></rect>
<rect x="118.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5181" values="#e5e7eb;#fde68a"/></rect>
<rect x="144.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5237" values="#e5e7eb;#fde68a"/></rect>
<rect x="170.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5293" values="#e5e7eb;#fde68a"/></rect>
<rect x="196.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5349" values="#e5e7eb;#fde68a"/></rect>
<rect x="222.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5405" values="#e5e7eb;#fde68a"/></rect>
<rect x="248.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5460" values="#e5e7eb;#fde68a"/></rect>
<rect x="274.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5516" values="#e5e7eb;#fde68a"/></rect>
<rect x="300.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5572" values="#e5e7eb;#fde68a"/></rect>
<rect x="326.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5628" values="#e5e7eb;#fde68a"/></rect>
<rect x="352.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5684" values="#e5e7eb;#fde68a"/></rect>
<rect x="378.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5740" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="404.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5795" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="430.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5851" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="456.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5907" values="#e5e7eb;#334155"/></rect>
<rect x="482.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5963" values="#e5e7eb;#334155"/></rect>
<rect x="508.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6019" values="#e5e7eb;#fde68a"/></rect>
<rect x="534.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6074" values="#e5e7eb;#fde68a"/></rect>
<rect x="560.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6130" values="#e5e7eb;#fde68a"/></rect>
<rect x="586.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6186" values="#e5e7eb;#fde68a"/></rect>
<rect x="612.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6242" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="638.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6298" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="664.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6353" values="#e5e7eb;#334155"/></rect>
<rect x="690.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6409" values="#e5e7eb;#334155"/></rect>
<rect x="716.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6465" values="#e5e7eb;#fde68a"/></rect>
<rect x="742.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6521" values="#e5e7eb;#fde68a"/></rect>
<rect x="768.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6577" values="#e5e7eb;#fde68a"/></rect>
<rect x="794.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6633" values="#e5e7eb;#fde68a"/></rect>
<rect x="820.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6688" values="#e5e7eb;#fde68a"/></rect>
<rect x="846.0" y="402.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6744" values="#e5e7eb;#fde68a"/></rect>
<rect x="40.0" y="402" width="832.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="716.0" y="402.0" width="26.0" height="26.0" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6463;0.6465;1.0000" values="0;0;1;1"/></rect>
<rect x="742.0" y="402.0" width="26.0" height="26.0" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6519;0.6521;1.0000" values="0;0;1;1"/></rect>
<rect x="768.0" y="402.0" width="26.0" height="26.0" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6575;0.6577;1.0000" values="0;0;1;1"/></rect>
<text x="40" y="440" text-anchor="start" style="font-size:13px;font-weight:700;fill:#7c3aed">両方をあわせる</text>
<rect x="40.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7172" values="#e5e7eb;#fde68a"/></rect>
<rect x="66.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7228" values="#e5e7eb;#fde68a"/></rect>
<rect x="92.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7284" values="#e5e7eb;#fde68a"/></rect>
<rect x="118.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7340" values="#e5e7eb;#fde68a"/></rect>
<rect x="144.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7395" values="#e5e7eb;#fde68a"/></rect>
<rect x="170.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7451" values="#e5e7eb;#fde68a"/></rect>
<rect x="196.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7507" values="#e5e7eb;#fde68a"/></rect>
<rect x="222.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7563" values="#e5e7eb;#fde68a"/></rect>
<rect x="248.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7619" values="#e5e7eb;#fde68a"/></rect>
<rect x="274.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7674" values="#e5e7eb;#fde68a"/></rect>
<rect x="300.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7730" values="#e5e7eb;#fde68a"/></rect>
<rect x="326.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7786" values="#e5e7eb;#fde68a"/></rect>
<rect x="352.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7842" values="#e5e7eb;#fde68a"/></rect>
<rect x="378.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7898" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="404.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7953" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="430.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8009" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="456.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8065" values="#e5e7eb;#334155"/></rect>
<rect x="482.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8121" values="#e5e7eb;#334155"/></rect>
<rect x="508.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8177" values="#e5e7eb;#fde68a"/></rect>
<rect x="534.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8233" values="#e5e7eb;#fde68a"/></rect>
<rect x="560.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8288" values="#e5e7eb;#fde68a"/></rect>
<rect x="586.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8344" values="#e5e7eb;#fde68a"/></rect>
<rect x="612.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8400" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="638.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8456" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="664.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8512" values="#e5e7eb;#334155"/></rect>
<rect x="690.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8567" values="#e5e7eb;#334155"/></rect>
<rect x="716.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8623" values="#e5e7eb;#334155"/></rect>
<rect x="742.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8679" values="#e5e7eb;#334155"/></rect>
<rect x="768.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8735" values="#e5e7eb;#334155"/></rect>
<rect x="794.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8791" values="#e5e7eb;#fde68a"/></rect>
<rect x="820.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8847" values="#e5e7eb;#fde68a"/></rect>
<rect x="846.0" y="444.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8902" values="#e5e7eb;#fde68a"/></rect>
<rect x="40.0" y="444" width="832.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5012;0.5014;0.7170;0.7172;1.0000" values="0;0;1;1;0;0"/><circle cx="459.04" cy="231.71" r="3.5" fill="#2ea043"/>
<circle cx="449.08" cy="220.14" r="3.5" fill="#e5484d"/>
<circle cx="439.12" cy="208.57" r="3.5" fill="#e5484d"/>
<circle cx="429.17" cy="197.0" r="3.5" fill="#e5484d"/>
<circle cx="419.21" cy="185.43" r="3.5" fill="#2ea043"/>
<circle cx="409.25" cy="173.86" r="3.5" fill="#2ea043"/>
<circle cx="469.0" cy="243.28" r="6" fill="#1f2937"/>
<text x="469.0" y="263.28" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">調べる画素</text>
</g>
<text x="560" y="312" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">深度の読み込み(コンタクト):</text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5012;0.5014;1.0000" values="1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">6<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5012;0.5014;0.5068;0.5070;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">12<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5068;0.5070;0.5124;0.5126;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">18<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5124;0.5126;0.5180;0.5181;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">24<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5180;0.5181;0.5235;0.5237;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">30<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5235;0.5237;0.5291;0.5293;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">36<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5291;0.5293;0.5347;0.5349;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">42<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5347;0.5349;0.5403;0.5405;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">48<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5403;0.5405;0.5459;0.5460;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">54<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5459;0.5460;0.5514;0.5516;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">60<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5514;0.5516;0.5570;0.5572;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">66<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5570;0.5572;0.5626;0.5628;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">72<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5626;0.5628;0.5682;0.5684;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">78<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5682;0.5684;0.5738;0.5740;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">78<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5738;0.5740;0.5793;0.5795;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">78<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5793;0.5795;0.5849;0.5851;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">78<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5849;0.5851;0.5905;0.5907;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">80<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5905;0.5907;0.5961;0.5963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">84<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5961;0.5963;0.6017;0.6019;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">90<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6017;0.6019;0.6073;0.6074;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">96<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6073;0.6074;0.6128;0.6130;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">102<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6128;0.6130;0.6184;0.6186;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">108<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6184;0.6186;0.6240;0.6242;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">108<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6240;0.6242;0.6296;0.6298;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">108<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6296;0.6298;0.6352;0.6353;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">110<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6352;0.6353;0.6407;0.6409;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">114<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6407;0.6409;0.6463;0.6465;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">120<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6463;0.6465;0.6519;0.6521;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">126<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6519;0.6521;0.6575;0.6577;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">132<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6575;0.6577;0.6631;0.6633;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">138<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6631;0.6633;0.6687;0.6688;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">144<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6687;0.6688;0.6742;0.6744;1.0000" values="0;0;1;1;0;0"/></text>
<text x="760" y="316" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">150<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6742;0.6744;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.9328;0.9330;1.0000" values="0;0;1;1"/><rect x="560" y="340" width="370" height="120" rx="12" fill="#faf5ff" stroke="#7c3aed" stroke-width="2.5"/>
<text x="576" y="364" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">正解とのくいちがい(画素数)</text>
<text x="576" y="386" text-anchor="start" style="font-size:14px;font-weight:700;fill:#991b1b">シャドウ マップだけ: 2 画素(足元を見逃す)</text>
<text x="576" y="409" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">コンタクトだけ: 3 画素(遠い影に届かない)</text>
<text x="576" y="432" text-anchor="start" style="font-size:14px;font-weight:700;fill:#166534">両方: 0 画素 → 足元まで影が付く</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">荒いシャドウ マップは、物の足元の短い影をバイアスで見逃す<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">画面の深度を光の方向に 6 歩たどると、足元の短い影が見つかる(遠くの影は、届かない)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.9328;0.9330;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">遠くの大きな影はシャドウ マップ、足元の細かい影はコンタクト、と役割を分ける<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.9328;0.9330;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:contact-shadow-march:end -->

## 原理：画面空間のレイマーチ

<strong>画素のビュー空間位置</strong> `P` から、光の方向 `L` へ短いレイを少しずつ進めます。各ステップの位置を画面に投影し、その画素の深度と比べます。レイが深度バッファの面より奥に入ったら、面の裏側に潜った＝遮蔽されたと判断します。

1. レイの端点を決めます。`P` と、`P + L · max_distance`（ビュー空間）の 2 点です。
2. 両端をスクリーン座標へ投影します。やり方は [SSR](../reflections/ssr-basics/index.md) と同じです。
3. レイに沿って少しずつ進み、各サンプルでレイの深度と深度バッファを比べます。レイのほうが奥なら、遮蔽されています。
4. 深度の差が大きすぎるときは、遠くの面の手前を通っただけとして無視します。これが、厚みの扱いです。

```hlsl
// 値は、どれも一例（ビュー空間の単位は m）。シーンに合わせて調整する
static const float kContactDistance = 0.5;   // レイの長さ
static const int kContactSteps = 16;         // ステップ数
static const float kBias = 0.02;             // これ以下の差は、面自身（自己遮蔽）とみなす
static const float kThickness = 0.2;         // 深度バッファの面の厚み
static const float kNearZ = 0.1;             // カメラの near plane までの距離

float ContactShadow(float3 view_pos, float3 light_dir_view, float jitter) {
  // 画素から光の方向へ、短いレイを伸ばす（長いと、別の面に当たって誤った影が出る）
  float3 ray_end = view_pos + light_dir_view * kContactDistance;
  // 光がカメラ側に向かうと、終点が near plane より手前に出る。そこで切る
  if (ray_end.z < kNearZ) {
    ray_end = view_pos + light_dir_view * ((kNearZ - view_pos.z) / light_dir_view.z);
  }
  float2 uv0 = ProjectToUV(view_pos);   // レイの始点の画面上の位置
  float2 uv1 = ProjectToUV(ray_end);    // 終点の画面上の位置
  float z0 = view_pos.z;
  float z1 = ray_end.z;

  float shadow = 1.0;                   // 1 = 光が当たる、0 = 影
  [loop] for (int i = 1; i <= kContactSteps; ++i) {
    // jitter で、ステップの位置を画素ごとに、少しずつずらす
    float t = (i - 1.0 + jitter) / kContactSteps;
    float2 uv = lerp(uv0, uv1, t);
    // 画面の外には深度が無いので、そこで打ち切る
    if (any(uv < 0.0) || any(uv > 1.0)) break;
    // 画面上で線形なのは 1/z なので、1/z を補間して z に戻す
    float ray_z = 1.0 / lerp(1.0 / z0, 1.0 / z1, t);
    float scene_z = LinearDepth(depth_tex.SampleLevel(point_sampler, uv, 0).r);

    // 正なら、レイは深度バッファの面より奥（面の裏側）にある
    float diff = ray_z - scene_z;
    // kBias 以下なら面そのもの（自己遮蔽）。kThickness 以上なら遠くの面
    if (diff > kBias && diff < kThickness) {
      shadow = 0.0;
      break;                            // 1 か所で遮られれば十分
    }
  }
  return shadow;
}
```

定数の値は一例です。`kThickness` は、扱う物の太さ（柵や草を通したくないなら薄く）に合わせます。`kBias` は、深度バッファの精度に合わせます（遠くほど誤差が大きくなります）。`1/z` で補間するやり方は、[SSR](../reflections/ssr-basics/index.md) と同じです。`jitter` の役割は、「コストと工夫」の「ジッターと時間蓄積」で説明します。

## ステップの取り方：間隔が粗いと、細い物を飛び越える

上のコードは、レイを `kContactSteps` 個に等分して、1 ステップにつき深度を 1 回だけ読みます。ところが、レイが画面上で何画素を横切るかは、カメラとの距離やレイの向きで変わります。サンプル数が固定だと、次の 2 つが起きます。

- レイが 100 画素を横切るのに 16 サンプルだけなら、6 画素に 1 回しか読みません。間にある画素は、見ていません。
- レイが 5 画素しか横切らないのに 16 サンプルなら、同じ画素を何度も読みます。読み込みの無駄です。

<svg class="fig flow" viewBox="0 0 640 436" role="img" aria-label="固定個数のサンプルと、隣り合う画素をたどる方法の比較">
<text x="48" y="42" style="font-size:14px;font-weight:700">サンプルが 6 個だけ：レイが通る 16 画素のうち、6 画素しか読まれない</text>
<rect x="48" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="82" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="116" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="150" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="184" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="218" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="252" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="286" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="320" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="354" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="388" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="422" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="456" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="490" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="524" y="56" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="558" y="56" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="48" y="90" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="82" y="90" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="116" y="90" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="150" y="90" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="184" y="90" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="218" y="90" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="252" y="90" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="286" y="90" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="320" y="90" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="354" y="90" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="388" y="90" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="422" y="90" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="456" y="90" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="490" y="90" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="524" y="90" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="558" y="90" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="48" y="124" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="82" y="124" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="116" y="124" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="150" y="124" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="184" y="124" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="218" y="124" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="252" y="124" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="286" y="124" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="320" y="124" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="354" y="124" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="388" y="124" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="422" y="124" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="456" y="124" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="490" y="124" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="524" y="124" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="558" y="124" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="48" y="158" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="82" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="116" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="150" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="184" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="218" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="252" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="286" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="320" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="354" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="388" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="422" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="456" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="490" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="524" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="558" y="158" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<line x1="65.0" y1="175.0" x2="575.0" y2="73.0" stroke="currentColor" stroke-width="1.5" stroke-dasharray="5 4"/>
<circle cx="65.0" cy="175.0" r="5" fill="#e5484d"/>
<circle cx="167.0" cy="154.6" r="5" fill="#e5484d"/>
<circle cx="269.0" cy="134.2" r="5" fill="#e5484d"/>
<circle cx="371.0" cy="113.8" r="5" fill="#e5484d"/>
<circle cx="473.0" cy="93.4" r="5" fill="#e5484d"/>
<circle cx="575.0" cy="73.0" r="5" fill="#e5484d"/>
<text x="48" y="248" style="font-size:14px;font-weight:700">隣り合う画素を 1 つずつたどる：通る画素を全部読む</text>
<rect x="48" y="262" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="82" y="262" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="116" y="262" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="150" y="262" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="184" y="262" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="218" y="262" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="252" y="262" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="286" y="262" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="320" y="262" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="354" y="262" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="388" y="262" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="422" y="262" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="456" y="262" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="490" y="262" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="524" y="262" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="558" y="262" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="48" y="296" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="82" y="296" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="116" y="296" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="150" y="296" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="184" y="296" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="218" y="296" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="252" y="296" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="286" y="296" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="320" y="296" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="354" y="296" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="388" y="296" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="422" y="296" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="456" y="296" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="490" y="296" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="524" y="296" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="558" y="296" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="48" y="330" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="82" y="330" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="116" y="330" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="150" y="330" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="184" y="330" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="218" y="330" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="252" y="330" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="286" y="330" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="320" y="330" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="354" y="330" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="388" y="330" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="422" y="330" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="456" y="330" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="490" y="330" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="524" y="330" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="558" y="330" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="48" y="364" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="82" y="364" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="116" y="364" width="34" height="34" fill="rgba(76,139,245,0.30)" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="150" y="364" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="184" y="364" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="218" y="364" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="252" y="364" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="286" y="364" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="320" y="364" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="354" y="364" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="388" y="364" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="422" y="364" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="456" y="364" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="490" y="364" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="524" y="364" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<rect x="558" y="364" width="34" height="34" fill="none" stroke="currentColor" stroke-opacity="0.35"/>
<line x1="65.0" y1="381.0" x2="575.0" y2="279.0" stroke="currentColor" stroke-width="1.5" stroke-dasharray="5 4"/>
<text x="48" y="428" style="font-size:12px">点線がレイ、青い画素が深度を読む画素、赤い点が固定個数のサンプル位置</text>
</svg>

McGuire と Mara の論文（参考）は、この問題を、2D の線を引くのと同じ要領でレイをたどって解決しています（DDA）。サンプルは、直前の画素のすぐ隣（斜めも含む）にあり、1 画素は多くて 1 回しか読みません。レイがカメラの近くの面（near plane）より手前に出る部分は切り、画面の外に出たら止めます。論文は、これを GPU で速く動かすための書き方（分岐を減らす、除算を掛け算に直すなど）も説明しています。

間隔を広げたいときのために、論文は `stride` を用意しています。`stride = 1` なら、全部の画素を読みます。大きくすると、読む画素が減って速くなりますが、画質が落ちて、縞（バンディング）が出ます。その縞を、画素ごとに開始位置を少しずらす `jitter` で、ノイズに変えて目立たなくします。論文は、`stride` を 1 より大きくするのは、細部が目立たない荒い面の反射だけにするよう勧めています。

コンタクト シャドウでは、細い物の影も出したいので、`stride` を広げる余裕はあまりありません。そこで、レイを短くして、間隔を保ちます。視線に垂直なレイなら、世界での間隔は「レイの長さ ÷ ステップ数」です。1 m を 16 ステップで読めば、約 6 cm ごとに 1 回です。これより細い物は、飛び越える可能性があります。0.5 m に縮めれば約 3 cm になるので、細い物（柵の 1 本、草の 1 枚）まで拾えます。

### DDA で書き直す

上の `ContactShadow` を、画面上で 1 画素ずつ進める形に書き直します。レイを画素座標に直して、長い方の軸が 1 画素ずつ進むように、増分を決めます。

```hlsl
static const int kMaxPixelSteps = 32;   // 画面上で 1 画素ずつ読む回数の上限（一例）

float ContactShadowDda(float3 view_pos, float3 light_dir_view,
                         float2 screen_size, float jitter) {
  // 終点を決めて near plane で切るところは、ContactShadow と同じ（省略）
  float3 ray_end = ClippedRayEnd(view_pos, light_dir_view);
  float2 p0 = ProjectToUV(view_pos) * screen_size;   // 始点の画素座標
  float2 p1 = ProjectToUV(ray_end) * screen_size;    // 終点の画素座標
  float k0 = 1.0 / view_pos.z;                       // 1/z は、画面上で線形に変わる
  float k1 = 1.0 / ray_end.z;
```

`ClippedRayEnd` は、前のコードの `ray_end` の計算と near plane で切る処理をまとめた関数です。`k = 1/z` を、画面上の位置と一緒に、同じ割合で進めます。論文の `k` と同じ考え方です（後の「論文のコードを読む」）。

```hlsl
  float2 delta = p1 - p0;
  float len = max(abs(delta.x), abs(delta.y));       // 画面上の長さ（画素）
  int n = (int)ceil(min(len, (float)kMaxPixelSteps));
  if (n == 0) return 1.0;                            // 1 画素にも満たない：影を調べるまでもない

  float2 dp = delta / n;                             // 1 ステップで進む画素数
  float dk = (k1 - k0) / n;
  float2 p = p0 + dp * jitter;                       // jitter で、開始位置を 1 ステップ未満ずらす
  float k = k0 + dk * jitter;
```

長い方の軸の長さ `len` が、画面上で何画素を横切るかです。`n` を `len` にそろえれば、1 ステップが、長い方の軸で 1 画素ぶんになります。上限 `kMaxPixelSteps` を超えるときは、`n` を上限で止めて、間隔を 1 画素より広げます（長いレイだけ、元の等分のやり方に戻ります）。

```hlsl
  float shadow = 1.0;
  [loop] for (int i = 0; i < n; ++i) {
    p += dp;
    k += dk;
    if (any(p < 0.0) || any(p >= screen_size)) break;         // 画面の外
    float ray_z = 1.0 / k;
    float scene_z = LinearDepth(depth_tex.Load(int3(p, 0)).r);  // 画素の座標で、直接読む
    float diff = ray_z - scene_z;
    if (diff > kBias && diff < kThickness) {
      shadow = 0.0;
      break;
    }
  }
  return shadow;
}
```

ループの中は、`ContactShadow` とほぼ同じです。違いは、`SampleLevel` ではなく `Load` で、画素の座標をそのまま読むことです。読む画素が、前の画素のすぐ隣になるので、飛ばしも重複もありません。

このコードは、HLSL としてコンパイルも実行もしていません。論文のコードのように、分岐を減らす工夫（軸の入れ替えなど）も入れていません。考え方を示すための例です。

## 厚みの扱い：深度バッファの面は、板として扱う

深度バッファは、各画素で、<strong>一番手前の面の深度</strong>しか持っていません。その面の裏側がどこまで続くか（厚み）は、分かりません。

そのため、サンプルの深度が、深度バッファの面より奥にあったとき、2 つの場合を区別できません。1 つは、レイが本当に物の中に入った（遮蔽されている）場合です。もう 1 つは、レイが、手前にある物の裏を通り過ぎた（柱の後ろを抜けた）だけの場合です。

そこで、深度バッファの面を、「手前の面から、`kThickness` だけ奥まである、厚みをもつ板」とみなします。レイがその板の中に入れば遮蔽、板より奥を通っていれば、遮蔽ではありません。論文も、各画素の深度に厚み（`zThickness`）を持たせて、レイがその範囲と重なったら当たりと判定しています。コードの `diff > kBias && diff < kThickness` が、この判定です。

<svg class="fig flow" viewBox="0 0 700 310" role="img" aria-label="厚みの内側と外側">
<defs><marker id="th-ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="26" style="font-size:14px;font-weight:700">深度バッファの面は、厚みをもつ板として扱う（横が奥行き、縦が画面上の位置）</text>
<line x1="40" y1="276" x2="660" y2="276" stroke="currentColor" stroke-width="1.5" marker-end="url(#th-ar)"/>
<text x="560" y="298" style="font-size:12px">奥行き（カメラから遠い）</text><text x="40" y="298" style="font-size:12px">カメラ側</text>
<rect x="300" y="70" width="140" height="190" fill="rgba(229,170,40,0.28)" stroke="currentColor" stroke-opacity="0.5"/>
<line x1="300" y1="70" x2="300" y2="260" stroke="currentColor" stroke-width="3"/>
<text x="296" y="64" text-anchor="end" style="font-size:12px">深度バッファの面（scene_z）</text>
<text x="370" y="64" text-anchor="middle" style="font-size:12px">kThickness</text>
<line x1="150" y1="240" x2="400" y2="120" stroke="#e5484d" stroke-width="2.5"/><circle cx="400" cy="120" r="5" fill="#e5484d"/>
<text x="40" y="264" style="font-size:12px;fill:#e5484d;font-weight:700">A：面の裏に入り、厚みの内側 → 遮蔽</text>
<line x1="500" y1="250" x2="610" y2="90" stroke="#2ea043" stroke-width="2.5"/><circle cx="610" cy="90" r="5" fill="#2ea043"/>
<text x="470" y="236" style="font-size:12px;fill:#2ea043;font-weight:700">B：厚みよりも奥 → 遮蔽ではない</text>
</svg>

厚みの値で、結果が大きく変わります。

- 薄すぎると、細い物（柵・草）は、板がレイの間隔より薄くて、すり抜けます。
- 厚すぎると、離れた壁の前に立つキャラクターのような場合に、壁の画素のレイが、キャラクターの後ろを通っただけで、遮蔽と判定されます。キャラクターの輪郭に沿って、壁に暗い縁が出ます。

論文は、1 枚の深度バッファだけで足りるとき（反射）には、ほぼ無限の厚みでも許容できると書いています。影は、遮蔽されるか、されないかの 2 択で、誤った遮蔽は、暗い領域としてそのまま出ます。そのため、厚みは、扱う物の太さに合わせて、小さめに決めたほうが安全です。遠くでは 1 画素が世界で大きくなり、深度の誤差も大きくなるので、厚みを距離に比例させる実装もあります。

完全な解決はなく、シーンごとの調整になります。論文は、深度を複数の層で持って、厚みを正しく扱う方法（最大 4 層）も説明していますが、その層を作るための描画が増えます。

## 自己遮蔽とバイアス：面自身で影にならないようにする

レイは、影を調べたい画素の面から出発します。つまり、最初のサンプルは、ほぼ面の上にあります。そこで、深度バッファの精度（16 ビットや 24 ビットの量子化と、ビュー空間の z への変換の誤差）で、レイの z が面より少し奥に見えると、面自身を遮蔽物と判定して、面全体が暗くなります（自己遮蔽）。

対策は、次の 3 つです。

- 判定に下限 `kBias` を設けます。`diff` が `kBias` 以下なら、面そのものとみなして、遮蔽にしません。
- 光が面とほぼ平行になる向き（斜めに差し込む光）は、レイが面に沿って進み、`diff` が小さいまま続きます。この向きでは、自己遮蔽が出やすくなります。`kBias` を大きめにするか、レイの開始位置を、法線の方向に少しずらします。
- 最初のサンプルの位置を、`jitter` で少しずらします（コードでは `t` の初期値）。毎回同じ位置から始めると、同じ縞が出ます。

`kBias` は、大きすぎると、接触部の影が浮いて見えます。小さすぎると、自己遮蔽が出ます。シャドウ マップのバイアスと同じ、トレードオフです。

## 論文のコードを読む

McGuire と Mara の論文には、GLSL で書いた実装（Listing 2 と 3）が載っています。関数 `traceScreenSpaceRay` が、レイの始点と方向から、当たった画素を返します。ここでは、このページのコードと関係の深い所だけを、短く引いて読みます（以下の 4 つの抜粋は論文のまま。全体は、論文の 3 節にあります）。

論文のコードは、反射用で、右手系のカメラ空間（+z が画面の手前）です。このページの HLSL は、左手系（+z が奥）なので、奥行きの向きが反対です。論文の `zThickness` は、z が小さい（奥の）側に、厚みを延ばしています。

```glsl
vec4 H0 = proj * vec4(csOrig, 1.0), H1 = proj * vec4(csEndPoint, 1.0);
float k0 = 1.0 / H0.w, k1 = 1.0 / H1.w;
point3 Q0 = csOrig * k0, Q1 = csEndPoint * k1;
point2 P0 = H0.xy * k0, P1 = H1.xy * k1;
```

始点と終点を、投影行列で、同次座標（`H`）にします。`k = 1/H.w` と `Q * k`（3D の点に `k` を掛けたもの）は、画面上で線形に変わります。論文の式 (1) のとおり、画面の任意の画素の 3D の位置は、`Q` に `k` を掛けた値を `k` で割れば戻ります。このページの HLSL では、`k = 1/z` だけを補間しているのが、これにあたります。`P0`・`P1` は、画面上の始点と終点です。

```glsl
bool permute = false;
if (abs(delta.x) < abs(delta.y)) {
   permute = true;
   delta = delta.yx; P0 = P0.yx; P1 = P1.yx;
}
```

DDA をそのまま書くと、4 つの象限 × 2 つの進む軸（x か y）で、場合分けが 8 通りになります。GPU は、同じグループの画素が別の枝に進むと、両方の枝を実行するので、遅くなります。そこで、y のほうが長いときは、x と y を入れ替えて、常に x の軸で進むように統一しています。入れ替えたかどうかは `permute` に残して、画素の座標を使うときに、元に戻します。

```glsl
dP *= stride; dQ *= stride; dk *= stride;
P0 += dP * jitter; Q0 += dQ * jitter; k0 += dk * jitter;
```

1 ステップの増分に `stride` を掛けて、間隔を広げます。そのあと、`jitter`（0〜1）に増分を掛けた量だけ、開始位置をずらします。`stride` と `jitter` の関係は、このページの「ステップの取り方」の説明のとおりです。

```glsl
float rayZMax = (dQ.z * 0.5 + Q.z) / (dk * 0.5 + k);
...
float4 sceneZMin = sceneZMax - zThickness;
if (((rayZMax >= sceneZMin[L]) && (rayZMin <= sceneZMax[L])) ||
    (sceneZMax[L] == 0)) {
```

当たりの判定です。論文は、レイを 1 点ではなく、1 画素の中でレイが通る奥行きの範囲 `[rayZMin, rayZMax]` として扱います。`rayZMax` は、半画素先の値で、`rayZMin` は前のステップの値です。この範囲が、深度バッファの面の範囲 `[sceneZMin, sceneZMax]`（面から `zThickness` だけ奥まで）と重なれば、当たりです。このページのコードは、サンプルの位置の 1 点だけで比べているので、論文の方法のほうが、細い面を取りこぼしにくくなります。

最後の `sceneZMax[L] == 0` は、画面の外の扱いです。論文は、画面の外を `texelFetch` で読むと 0 が返ることを使って、ここで条件を真にして、ループを止めます。そのあと、戻り値の判定で、画素が画面の中に入っているかを確かめて、外なら当たりとしません。このページのコードの、`break` と同じ役割です。

論文のコードは、反射用なので、当たった画素の座標を返します。影では、当たったかどうかだけが要ります。そのため、このページのコードは、`shadow = 0.0` を返す形にしました。

## 実装例：Days Gone

Bend Studio は、PS4 の Days Gone（2019 年）で、太陽光の影にスクリーン スペース シャドウを使いました（同社の説明では、太陽光の影に使った最初のタイトル）。シャドウ マップでは取れない小さな細部を補って、遠景の素材が平らに見えるのを和らげた、と説明しています。

同社は、SIGGRAPH 2023（Sony Creators Conference）で発表資料を公開し、Days Gone など Sony の複数のタイトルに入れたコードも公開しています（参考）。ここまでに書いた、ステップの取り方・厚み・バイアスが、実際のコードでどう決められているかを読むと、パラメータの決め方の参考になります。このページでは、公開されたコードの中身までは、解説していません。

## シャドウ マップとの合成

コンタクト シャドウは、単独ではなく、シャドウ マップを補うために使います。合成は、暗い方を取るのが一般的です。コンタクト シャドウは近くだけで使うので、距離でフェードアウトさせます。接触部をコンタクト シャドウが担当してくれるので、シャドウ マップのバイアスは、安全側（アクネを避ける方）に振れます。

```hlsl
// kFadeStart から kFadeEnd（m）にかけて、コンタクト シャドウを消していく
float fade = saturate((view_pos.z - kFadeStart) / (kFadeEnd - kFadeStart));  // 0 = 近い、1 = 遠い
float contact = lerp(ContactShadow(view_pos, light_dir_view, jitter), 1.0, fade);  // 遠くでは影なし
float shadow = min(shadow_map_value, contact);  // 暗い方を取る
```

## コストと工夫

コンタクト シャドウの重さは、ほぼ「画素数 × ステップ数」です。1 ステップごとに深度バッファを 1 回読むので、ステップを減らすか、計算する画素を減らすのが基本になります。

McGuire と Mara の論文には、1920 × 1080 の全画素で、25 ステップの斜めのレイを 1 本ずつ追った時間が出ています。2014 年のデスクトップ GPU（GeForce Titan）で 1.2 ms、ノート PC の GPU（GeForce 650M）で 6.4 ms です。反射用のレイなので、そのままコンタクト シャドウの時間にはなりませんが、「全画素 × 数十ステップ」が、数 ms の単位になる目安になります。今の GPU なら、もっと速くなります。

### ステップ数

8〜16 が目安です。ステップが少ないと、レイが細い物（柵の 1 本、草の 1 枚）を飛び越えて、影が抜けます。多くすれば細部を拾えますが、そのぶん深度バッファの読み込みが増えます。

### レイの距離

距離が短いほど、同じステップ数でも間隔が細かくなり、細部を拾えます。精度を保ったまま、ステップ数を減らせるので、安くなります。そのうえ、遠くの面を誤って遮蔽物にする失敗（厚みの問題）も減ります。接触部のための影なので、長くする理由はありません。

### ジッターと時間蓄積

ステップを少なくすると、レイの間隔が粗くなって、影に縞が出ます。そこで、画素ごとにステップの位置をずらします（ジッター）。ずらす量には、IGN（Interleaved Gradient Noise）のようなノイズ関数を使います。縞が、細かいノイズに変わります。毎フレームずらす量を変えて、TAA で時間方向に混ぜれば、ノイズが消えます。少ないステップで、多いステップに近い見た目にできます。コードでは、`t` の計算の `jitter` が、この量です。

### 近くの接触部に限定する

コンタクト シャドウは、カメラの近くの、接触部がはっきり見える範囲に効きます。遠くでは、接触部が数画素の大きさになるので、距離でフェードアウトさせて、遠くの画素は計算そのものを省くのが、よくある使い方です。一方、Days Gone のように、遠景の影の細部を補うために使う例もあります。どちらを選ぶかは、シーンの広さと、遠景の影のシャドウ マップの解像度で決まります。

### ライトごとの計算

ライトごとにレイを伸ばすので、ライトの数だけ、コストが増えます。そのため、主ライト（太陽）だけに適用することが多いです。ほかのライトは、シャドウ マップだけで済ませます。

### コンピュート シェーダー

ピクセル シェーダーでは、隣り合う画素が、同じ深度を何度も読みます。コンピュート シェーダーなら、グループ共有メモリに深度のタイルを先に読み込んで、グループ内のスレッドで使い回せます。深度バッファへのアクセスが減り、キャッシュ効率が上がります。ただし、実装が複雑になるので、必ず入れる工夫ではありません。

## 長所と画面空間の限界

長所は、接触部の細かい影が出ることです。短いレイだけなので安く、シャドウ マップのバイアスの問題も補えます。草・髪のような細い物にも、ある程度効きます。

一方、画面空間の技法なので、深度バッファに写っているものしか使えません。そこから、次の 4 つの限界が出ます。

画面の外にある遮蔽物は、深度バッファに入っていないので、遮蔽物として使えません。画面のすぐ外に柱があっても、その影は出ません。

見えない面の裏側は、深度バッファに入っていないので、厚みが分かりません。これへの対処は、「厚みの扱い」で説明したとおりです。

視点にも依存します。カメラが動くと、画面に写る物が変わるので、影が出たり消えたりして見えることがあります。

画面の端では、レイが画面の外に出ます。外には深度が無いので、サンプルを打ち切ります（上のコードの `break`）。打ち切った先に遮蔽物があっても、見えないので、端の近くでは、画面の外側にある物の影が出ません。

ジッターを使う場合は、ノイズも残ります。TAA で消すことが前提です。あくまで補助で、シャドウ マップの代わりにはできません。

## よくあるミス

??? failure "自己遮蔽で、面全体が暗くなる"
    レイの出発点は面の上にあるので、深度の精度の誤差だけで、面自身を遮蔽物と判定します。`kBias` で、`diff` が小さい（面そのものの）ヒットを除きます。斜めに差し込む光では、レイの開始位置を、法線の方向に少しずらします。

??? failure "厚みの上限が無い、または大きすぎて、輪郭に暗い縁が出る"
    離れた壁の前にいるキャラクターのように、レイが手前の物の後ろを通るだけで、遮蔽と判定されます。`diff < kThickness` の上限を付けて、厚みは、扱う物の太さに合わせて、小さめにします。

??? failure "非線形の深度のまま比べて、距離でおかしくなる"
    深度バッファの値（0〜1 の非線形な値）をそのまま比べると、遠くでは同じ差が小さな値になるので、`kBias` と `kThickness` の効き方が、距離で変わります。ビュー空間の z（線形）に直してから、`diff` を求めます（コードの `LinearDepth`）。

??? failure "画面の外を読んで、画面の端に偽の影が出る"
    `uv` が [0, 1] の外に出たのに打ち切らないと、サンプラーが、端の画素を返し続けます。外に出たら、`break` します。

??? failure "光がカメラ側に向くと、影が壊れる"
    終点が near plane より手前に出て、`1/z` の補間が、符号の変わる値を含みます。終点を、near plane で切ります（コードの `kNearZ` の処理）。

??? failure "ステップ数を減らしたら、細い物の影が抜けた"
    世界での間隔は、「レイの長さ ÷ ステップ数」です。1 m を 16 ステップで読むと約 6 cm なので、それより細い物は飛び越えます。ステップ数を減らすときは、レイも短くして、間隔を保ちます。

??? failure "全画面・長い距離で計算して、重い"
    ステップ数が同じでも、レイが長いと間隔が粗くなります。画素数 × ステップ数のコストも、全画面だと大きくなります。近景の画素と、短い距離に絞ります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コンタクト シャドウ ＝ <strong>画素から光の方向へ深度バッファ上で短いレイを進め</strong>、遮蔽を調べる
    - [x] シャドウ マップの、接触部の欠け・ピーター パンニングを補う
    - [x] 厚みの仮定が必要（薄すぎ → すり抜け、厚すぎ → 誤った影）
    - [x] 画面にある物しか見えない（補助として使う）
    - [x] ジッター ＋ 時間蓄積で、ステップ数を減らす
    - [x] 世界での間隔は「レイの長さ ÷ ステップ数」。これより細い物は飛び越える
    - [x] 深度バッファの面は、`kThickness` の厚みをもつ板として扱う。`kBias` で自己遮蔽を避ける
    - [x] 画面の外に出たら打ち切り、終点は near plane で切る
    - [x] 1 画素ずつ隣をたどる（DDA）と、飛ばしも重複もない。`k = 1/z` を一緒に進める

## 参考

- Morgan McGuire, Michael Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, pp. 73–85, 2014（[JCGT](https://jcgt.org/published/0003/04/04/)）。「ステップの取り方」と「厚みの扱い」は、1.2 節（2D の線形な反復）、3 節（DDA の実装）、4 節（パラメータ）を参照
- Graham Aldridge, "Screen Space Shadows", SIGGRAPH 2023, Sony Creators Conference と、サンプル コード（Bend Studio の [SIGGRAPH のページ](https://www.bendstudio.com/siggraph)、解説は [Inside Bend Screen Space Shadows](https://www.bendstudio.com/blog/inside-bend-screen-space-shadows/)）

## 関連ページ

- [Shadows](index.md)
- [Shadow Bias](bias/index.md)
- [SSR Basics](../reflections/ssr-basics/index.md)
- [SSAO](../ao/ssao-hemisphere.md)
