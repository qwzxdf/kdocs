---
title: Contact Shadows
tags:
  - 描画
---

# Contact Shadows

シャドウ マップは、**解像度に限りがあり**、**バイアスで少し浮かせる**ので**物体が地面に接する付近の細かい影**が**欠けたり、浮いて見えたり**します（ピーター パンニング）。**コンタクト シャドウ**（Contact Shadows）は、<strong>画面空間（深度バッファ）</strong>で、**画素から光の方向へ短いレイを進め**、**手前にある物に当たるか**を調べる方式です。**接触部の細かい影**を**シャドウ マップを補って**、**安く**描きます。

!!! tip "ポイント"
    - <strong>画素から、光の方向へ深度バッファの上で短いレイ</strong>を進める。
    - <strong>レイの深度が深度バッファより奥に入ったら、遮蔽された</strong>。
    - <strong>距離は短い</strong>（数十 cm〜1 m）。<strong>シャドウ マップの接触部の欠けを補う</strong>のが目的。
    - 欠点：<strong>見えている面しか、知らない</strong>（画面外・裏側は遮蔽物にならない）。<strong>厚み</strong>の仮定。
    - <strong>画素ごとにジッター</strong>して、<strong>サンプル数を減らし</strong>、ノイズを<strong>時間蓄積</strong>で消す。
    - <strong>[SSR](../reflections/ssr-basics/index.md)・[SSAO](../ao/ssao-hemisphere.md) と同じ「画面空間」の方式</strong>で<strong>同じ限界</strong>を持つ。

## なぜ接触部で影が欠けるのか

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="接触部の影の欠け">
<text x="20" y="24" class="fig-title">シャドウ マップは、接触部で影が浮く・欠ける（ピーター パンニング）</text>
<line x1="60" y1="200" x2="720" y2="200" stroke="currentColor" stroke-width="4"/>
<rect x="150" y="150" width="70" height="50" fill="rgba(150,150,150,0.8)" stroke="currentColor" stroke-width="2"/><text x="140" y="140" style="font-size:12px">物体（地面に接している）</text>
<rect x="220" y="196" width="140" height="8" fill="#111" opacity="0.85"/><rect x="220" y="196" width="22" height="8" fill="#e5484d" opacity="0.5"/>
<text x="250" y="226" style="font-size:12px;fill:#e5484d;font-weight:700">接触部の影が欠ける</text>
<text x="420" y="70" style="font-size:13px">原因：</text><text x="420" y="94" style="font-size:12px">・バイアスで深度を浮かせる → 近い所は影が出ない</text><text x="420" y="114" style="font-size:12px">・シャドウ マップの 1 テクセルが、物の大きさに比べて粗い</text>
<text x="420" y="152" style="font-size:13px">解決：</text><text x="420" y="176" style="font-size:11px">画面の深度で、短い距離を調べる → 接触部だけ、細かく影を補う</text>
</svg>

<!-- fig:contact-shadow-march:begin -->

<svg class="fig illust motion" data-fig="contact-shadow-march" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-contact-shadow-march" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">コンタクト シャドウ: 画面の深度を、光の方向へたどって、物の足元の細かい影を作る</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。地面に、高さ 1.5 の小さな物。シャドウ マップ(荒い)で見逃す足元の影を、画面の深度で補う</text>
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
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">荒いシャドウ マップは、物の足元の短い影を、バイアスで見逃す<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">画面の深度を、光の方向に 6 歩たどると、足元の短い影が見つかる(遠くの影は、届かない)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.9328;0.9330;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">遠くの大きな影はシャドウ マップ、足元の細かい影はコンタクト、と役割を分ける<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.9328;0.9330;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:contact-shadow-march:end -->

## 原理：画面空間のレイマーチ

**画素のビュー空間位置** `P` から、**光の方向** `L` へ**短いレイ**を**少しずつ進め**ます。**各ステップの位置を画面に投影**し、**その画素の深度**と比べます。**レイが深度バッファの面より奥に入った**ら、**面の裏側に潜った＝遮蔽**されたと判断します。

| 手順 | 内容 |
| --- | --- |
| **① レイの端点** | `P` と、`P + L · max_distance`（ビュー空間） |
| **② 画面に投影** | 両端をスクリーン座標へ（[SSR](../reflections/ssr-basics/index.md)と同じ） |
| **③ ステップごとに比べる** | 各サンプルで**レイの深度 ＞ 深度バッファ** ならば、遮蔽 |
| **④ 厚みを考慮** | **深度の差が大きすぎる**場合は、**遠くの面の手前を通っただけ**として、無視 |

```hlsl
float ContactShadow(float3 view_pos, float3 light_dir_view, float2 pixel, float jitter) {
  float3 ray_end = view_pos + light_dir_view * kContactDistance;
  float2 uv0 = ProjectToUV(view_pos);
  float2 uv1 = ProjectToUV(ray_end);
  float z0 = view_pos.z;
  float z1 = ray_end.z;

  float shadow = 1.0;
  [loop] for (int i = 1; i <= kContactSteps; ++i) {
    float t = (i - 1.0 + jitter) / kContactSteps;
    float2 uv = lerp(uv0, uv1, t);
    float ray_z = 1.0 / lerp(1.0 / z0, 1.0 / z1, t);
    float scene_z = LinearDepth(depth_tex.SampleLevel(point_sampler, uv, 0).r);
    float diff = ray_z - scene_z;
    if (diff > kBias && diff < kThickness) {
      shadow = 0.0;
      break;
    }
  }
  return shadow;
}
```

| 点 | 説明 |
| --- | --- |
| **`1/z` で補間** | **透視投影では、1/z が画面上で線形**（[SSR](../reflections/ssr-basics/index.md)） |
| **`jitter`** | **画素ごとのステップ位置のずらし**（IGN）。**ステップ数を少なく**しても、**縞がノイズに変わる** |
| **`kBias`** | **自己遮蔽（面自身）を避ける**、小さな許容値 |
| **`kThickness`** | **厚み**。**これ以上、遮蔽物の奥にある**ものは、**遮蔽物ではない**として扱う |
| **`kContactDistance`** | **短い距離**（0.1〜1 m 程度） |

## 厚みの問題

**深度バッファは、「一番手前の面」の深度しか持たない**ので、**その面の厚み**（裏側までの奥行き）が、**分かりません**。

厚みの設定による結果です。薄すぎると、細い物（柵・草）をすり抜けることがあります。厚すぎると、遠くの面の手前を通っただけでも遮蔽扱いになり、誤った影が出ます。適度な値は、シーンに合わせて調整し、距離や物のスケールで変えます。

**完全な解決はなく**、**パラメータの調整**で**妥当な見た目**に寄せます。

## シャドウ マップとの合成

**コンタクト シャドウ**は、**単独ではなく、シャドウ マップを補う**ために使います。

コンタクト シャドウは、単独でなく、シャドウ マップを補うために使います。合成は、暗い方を取る `shadow = min(shadow_map, contact)` が一般的です。コンタクト シャドウは近くだけで使うので、距離でフェードアウトさせます。接触部をコンタクト シャドウが担当してくれるので、シャドウ マップのバイアスは安全側（アクネを避ける方）に振れます。

## コストと工夫

| 項目 | 内容 |
| --- | --- |
| **ステップ数** | **8〜16**。**多いほど、細部を捉える** |
| **レイの距離** | **短い**ほど安い |
| **ジッター ＋ 時間蓄積** | **少ないステップ**＋**ノイズ**を**TAA**で消す |
| **画面中心・近景に限定** | **遠くはコンタクト シャドウを省略** |
| **ライト ごとに計算** | **主ライト（太陽）だけ**に適用することが多い |
| **コンピュート シェーダー** | **グループ共有メモリ**に**深度を読み込み**、**キャッシュ効率**を上げる実装もある |

## 画面空間の限界

| 限界 | 内容 |
| --- | --- |
| **画面外の遮蔽物** | **深度バッファにない**ので、**遮蔽物として使えない** |
| **見えない面の裏側** | **厚みを知らない** |
| **視点依存** | **カメラが動くと**、**影が変わって見える**ことがある |
| **画面端** | **サンプルが画面外に出る**と**情報がない** |

**そのため、あくまで補助**で**シャドウ マップの代わりには、できません**。

## 長所と短所

| 長所 | 短所 |
| --- | --- |
| **接触部の細かい影**が出る | **画面にある物だけ**が遮蔽物 |
| **安い**（短いレイ） | **厚みの扱いが難しい** |
| **シャドウ マップのバイアスの問題を補える** | **画面外・裏側は不可** |
| **細い物（草・髪・ディテール）にもある程度、効く** | **ノイズ**が出る（ジッターのとき） |

## よくあるミス

??? failure "自己遮蔽で、面全体が暗くなる"
    **小さなバイアス**を入れる、**レイの開始位置を法線方向に少しずらす**。

??? failure "遠くの面の手前を通っただけで、影になる"
    **厚み**（`kThickness`）を、設定します。

??? failure "非線形の深度のまま比べて、距離でおかしくなる"
    **線形な深度**（ビュー空間の z）で、比べます。

??? failure "全画面・長い距離で計算して、重い"
    **近景だけ・短い距離**にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コンタクト シャドウ ＝ <strong>画素から光の方向へ、深度バッファ上で短いレイを進め</strong>、<strong>遮蔽</strong>を調べる
    - [x] <strong>シャドウ マップの、接触部の欠け・ピーター パンニングを補う</strong>
    - [x] <strong>厚み</strong>の仮定が必要（<strong>薄すぎ → すり抜け、厚すぎ → 誤った影</strong>）
    - [x] <strong>画面にある物しか見えない</strong>（<strong>補助</strong>として使う）
    - [x] <strong>ジッター ＋ 時間蓄積</strong>で、<strong>ステップ数を減らす</strong>

## 参考

- Sousa, "Secrets of CryEngine 3 Graphics Technology"（2011、画面空間の影）
- Bend Studio, "Screen Space Shadows"（GDC 2023 など）

## 関連ページ

- [Shadows](index.md)
- [Shadow Bias](bias/index.md)
- [SSR（画面空間の反射）](../reflections/ssr-basics/index.md)
- [SSAO](../ao/ssao-hemisphere.md)
