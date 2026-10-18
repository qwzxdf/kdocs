---
title: Bilateral Blur
tags:
  - 描画
---

# Bilateral Blur

**AO のノイズを消すには、ぼかすのが基本**ですが、**普通のぼかしは、物体の境界（エッジ）をまたいでにじみ、境界に黒や白のハロー**ができます。**深度や法線が近い画素だけを混ぜる「バイラテラル ブラー」**なら、**エッジを保ったままノイズだけ消せます**。このページでは、**バイラテラル ブラーの考え方・重みの付け方・実装・パラメータ**を説明します。

!!! tip "ポイント"
    - **バイラテラル ブラー ＝ 空間的に近く、かつ、深度・法線も近い画素だけを混ぜる**。
    - **エッジをまたがない**ので**ハローが出ない**。
    - **横 → 縦の 2 パス**に**分離**する（**厳密には分離できないが、実用上は十分**）。
    - **重みは、ガウス ×（深度の差の重み）×（法線の差の重み）**。

## Spatial Filter: Bilateral Blur {#空間フィルタバイラテラル-ブラー}
<!-- fig:bilateral-blur:begin -->

<svg class="fig illust motion" data-fig="bilateral-blur" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bilateral-blur" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">バイラテラル ブラー: 深度が近い画素だけを平均して、輪郭をにじませずにノイズを消す</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 48 画素。左は手前(深度 1)、右は奥(深度 3)。AO にノイズが乗っている</text>
<text x="60.0" y="96" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">深度(濃い = 手前 / 薄い = 奥)</text>
<rect x="60.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="77.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="94.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="111.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="128.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="145.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="162.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="179.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="196.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="213.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="230.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="247.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="264.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="281.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="298.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="315.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="332.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="349.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="366.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="383.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="400.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="417.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="434.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="451.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#334155"/></rect>
<rect x="468.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="485.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="502.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="519.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="536.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="553.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="570.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="587.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="604.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="621.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="638.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="655.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="672.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="689.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="706.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="723.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="740.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="757.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="774.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="791.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="808.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="825.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="842.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="859.0" y="102.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cbd5e1"/></rect>
<rect x="60.0" y="102" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="138" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">ノイズのある AO</text>
<rect x="60.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#989898"/></rect>
<rect x="77.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#ffffff"/></rect>
<rect x="94.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#f4f4f4"/></rect>
<rect x="111.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="128.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#c1c1c1"/></rect>
<rect x="145.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#ffffff"/></rect>
<rect x="162.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#ffffff"/></rect>
<rect x="179.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#ffffff"/></rect>
<rect x="196.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#aaaaaa"/></rect>
<rect x="213.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#ffffff"/></rect>
<rect x="230.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#a9a9a9"/></rect>
<rect x="247.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#ffffff"/></rect>
<rect x="264.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#ffffff"/></rect>
<rect x="281.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#c9c9c9"/></rect>
<rect x="298.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#a9a9a9"/></rect>
<rect x="315.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#ffffff"/></rect>
<rect x="332.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#f7f7f7"/></rect>
<rect x="349.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#a0a0a0"/></rect>
<rect x="366.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#fbfbfb"/></rect>
<rect x="383.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dadada"/></rect>
<rect x="400.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#bebebe"/></rect>
<rect x="417.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#f9f9f9"/></rect>
<rect x="434.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#ffffff"/></rect>
<rect x="451.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#cccccc"/></rect>
<rect x="468.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#848484"/></rect>
<rect x="485.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#717171"/></rect>
<rect x="502.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#2f2f2f"/></rect>
<rect x="519.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#444444"/></rect>
<rect x="536.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#808080"/></rect>
<rect x="553.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#7d7d7d"/></rect>
<rect x="570.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#888888"/></rect>
<rect x="587.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#b7b7b7"/></rect>
<rect x="604.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#3c3c3c"/></rect>
<rect x="621.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#919191"/></rect>
<rect x="638.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#535353"/></rect>
<rect x="655.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#525252"/></rect>
<rect x="672.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#585858"/></rect>
<rect x="689.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#ababab"/></rect>
<rect x="706.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#696969"/></rect>
<rect x="723.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#3c3c3c"/></rect>
<rect x="740.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#9e9e9e"/></rect>
<rect x="757.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#8d8d8d"/></rect>
<rect x="774.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#474747"/></rect>
<rect x="791.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#585858"/></rect>
<rect x="808.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#6a6a6a"/></rect>
<rect x="825.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#5f5f5f"/></rect>
<rect x="842.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#818181"/></rect>
<rect x="859.0" y="142.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#3f3f3f"/></rect>
<rect x="60.0" y="142" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="188" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">普通のぼかし(ガウス)</text>
<rect x="60.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0513" values="#e5e7eb;#d8d8d8"/></rect>
<rect x="77.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0595" values="#e5e7eb;#dddddd"/></rect>
<rect x="94.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0677" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="111.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0759" values="#e5e7eb;#e4e4e4"/></rect>
<rect x="128.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0841" values="#e5e7eb;#e7e7e7"/></rect>
<rect x="145.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0923" values="#e5e7eb;#e7e7e7"/></rect>
<rect x="162.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#e5e7eb;#e7e7e7"/></rect>
<rect x="179.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1087" values="#e5e7eb;#e5e5e5"/></rect>
<rect x="196.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1169" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="213.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1251" values="#e5e7eb;#dfdfdf"/></rect>
<rect x="230.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1333" values="#e5e7eb;#dfdfdf"/></rect>
<rect x="247.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1415" values="#e5e7eb;#dedede"/></rect>
<rect x="264.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1497" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="281.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1579" values="#e5e7eb;#dbdbdb"/></rect>
<rect x="298.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1662" values="#e5e7eb;#dbdbdb"/></rect>
<rect x="315.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1744" values="#e5e7eb;#dadada"/></rect>
<rect x="332.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1826" values="#e5e7eb;#dadada"/></rect>
<rect x="349.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1908" values="#e5e7eb;#dadada"/></rect>
<rect x="366.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1990" values="#e5e7eb;#dbdbdb"/></rect>
<rect x="383.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2072" values="#e5e7eb;#dbdbdb"/></rect>
<rect x="400.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2154" values="#e5e7eb;#d8d8d8"/></rect>
<rect x="417.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2236" values="#e5e7eb;#d0d0d0"/></rect>
<rect x="434.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2318" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="451.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#afafaf"/></rect>
<rect x="468.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2482" values="#e5e7eb;#999999"/></rect>
<rect x="485.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2564" values="#e5e7eb;#858585"/></rect>
<rect x="502.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2646" values="#e5e7eb;#787878"/></rect>
<rect x="519.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2728" values="#e5e7eb;#707070"/></rect>
<rect x="536.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2810" values="#e5e7eb;#707070"/></rect>
<rect x="553.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2892" values="#e5e7eb;#737373"/></rect>
<rect x="570.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2974" values="#e5e7eb;#767676"/></rect>
<rect x="587.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3056" values="#e5e7eb;#767676"/></rect>
<rect x="604.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3138" values="#e5e7eb;#757575"/></rect>
<rect x="621.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3221" values="#e5e7eb;#717171"/></rect>
<rect x="638.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3303" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="655.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3385" values="#e5e7eb;#6c6c6c"/></rect>
<rect x="672.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3467" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="689.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3549" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="706.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3631" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="723.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3713" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="740.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3795" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="757.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3877" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="774.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3959" values="#e5e7eb;#6a6a6a"/></rect>
<rect x="791.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4041" values="#e5e7eb;#666666"/></rect>
<rect x="808.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4123" values="#e5e7eb;#646464"/></rect>
<rect x="825.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4205" values="#e5e7eb;#636363"/></rect>
<rect x="842.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4287" values="#e5e7eb;#616161"/></rect>
<rect x="859.0" y="192.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4369" values="#e5e7eb;#5f5f5f"/></rect>
<rect x="60.0" y="192" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="238" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">バイラテラル(深度も見る)</text>
<rect x="60.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0513" values="#e5e7eb;#d8d8d8"/></rect>
<rect x="77.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0595" values="#e5e7eb;#dddddd"/></rect>
<rect x="94.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0677" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="111.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0759" values="#e5e7eb;#e4e4e4"/></rect>
<rect x="128.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0841" values="#e5e7eb;#e7e7e7"/></rect>
<rect x="145.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0923" values="#e5e7eb;#e7e7e7"/></rect>
<rect x="162.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#e5e7eb;#e7e7e7"/></rect>
<rect x="179.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1087" values="#e5e7eb;#e5e5e5"/></rect>
<rect x="196.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1169" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="213.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1251" values="#e5e7eb;#dfdfdf"/></rect>
<rect x="230.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1333" values="#e5e7eb;#dfdfdf"/></rect>
<rect x="247.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1415" values="#e5e7eb;#dedede"/></rect>
<rect x="264.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1497" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="281.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1579" values="#e5e7eb;#dbdbdb"/></rect>
<rect x="298.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1662" values="#e5e7eb;#dbdbdb"/></rect>
<rect x="315.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1744" values="#e5e7eb;#dadada"/></rect>
<rect x="332.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1826" values="#e5e7eb;#dadada"/></rect>
<rect x="349.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1908" values="#e5e7eb;#dadada"/></rect>
<rect x="366.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1990" values="#e5e7eb;#dbdbdb"/></rect>
<rect x="383.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2072" values="#e5e7eb;#dddddd"/></rect>
<rect x="400.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2154" values="#e5e7eb;#dfdfdf"/></rect>
<rect x="417.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2236" values="#e5e7eb;#e0e0e0"/></rect>
<rect x="434.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2318" values="#e5e7eb;#e1e1e1"/></rect>
<rect x="451.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#e3e3e3"/></rect>
<rect x="468.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2482" values="#e5e7eb;#646464"/></rect>
<rect x="485.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2564" values="#e5e7eb;#636363"/></rect>
<rect x="502.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2646" values="#e5e7eb;#656565"/></rect>
<rect x="519.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2728" values="#e5e7eb;#686868"/></rect>
<rect x="536.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2810" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="553.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2892" values="#e5e7eb;#737373"/></rect>
<rect x="570.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2974" values="#e5e7eb;#767676"/></rect>
<rect x="587.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3056" values="#e5e7eb;#767676"/></rect>
<rect x="604.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3138" values="#e5e7eb;#757575"/></rect>
<rect x="621.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3221" values="#e5e7eb;#717171"/></rect>
<rect x="638.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3303" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="655.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3385" values="#e5e7eb;#6c6c6c"/></rect>
<rect x="672.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3467" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="689.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3549" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="706.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3631" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="723.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3713" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="740.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3795" values="#e5e7eb;#6f6f6f"/></rect>
<rect x="757.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3877" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="774.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3959" values="#e5e7eb;#6a6a6a"/></rect>
<rect x="791.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4041" values="#e5e7eb;#666666"/></rect>
<rect x="808.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4123" values="#e5e7eb;#646464"/></rect>
<rect x="825.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4205" values="#e5e7eb;#636363"/></rect>
<rect x="842.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4287" values="#e5e7eb;#616161"/></rect>
<rect x="859.0" y="242.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4369" values="#e5e7eb;#5f5f5f"/></rect>
<rect x="60.0" y="242" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="288" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">正解(ノイズなし)</text>
<rect x="60.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="77.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="94.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="111.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="128.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="145.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="162.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="179.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="196.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="213.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="230.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="247.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="264.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="281.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="298.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="315.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="332.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="349.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="366.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="383.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="400.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="417.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="434.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="451.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="468.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="485.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="502.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="519.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="536.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="553.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="570.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="587.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="604.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="621.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="638.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="655.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="672.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="689.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="706.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="723.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="740.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="757.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="774.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="791.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="808.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="825.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="842.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="859.0" y="292.0" width="17.3" height="17.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0154" values="#e5e7eb;#727272"/></rect>
<rect x="60.0" y="292" width="816.0" height="17.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="60.0" y="136" width="17.0" height="173" fill="none" stroke="#e5aa28" stroke-width="3" opacity="0"><animate attributeName="x" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0593;0.0595;0.0675;0.0677;0.0757;0.0759;0.0839;0.0841;0.0921;0.0923;0.1003;0.1005;0.1085;0.1087;0.1167;0.1169;0.1249;0.1251;0.1331;0.1333;0.1413;0.1415;0.1495;0.1497;0.1577;0.1579;0.1659;0.1662;0.1742;0.1744;0.1824;0.1826;0.1906;0.1908;0.1988;0.1990;0.2070;0.2072;0.2152;0.2154;0.2234;0.2236;0.2316;0.2318;0.2398;0.2400;0.2480;0.2482;0.2562;0.2564;0.2644;0.2646;0.2726;0.2728;0.2808;0.2810;0.2890;0.2892;0.2972;0.2974;0.3054;0.3056;0.3136;0.3138;0.3218;0.3221;0.3301;0.3303;0.3383;0.3385;0.3465;0.3467;0.3547;0.3549;0.3629;0.3631;0.3711;0.3713;0.3793;0.3795;0.3875;0.3877;0.3957;0.3959;0.4039;0.4041;0.4121;0.4123;0.4203;0.4205;0.4285;0.4287;0.4367;0.4369;1.0000" values="60;60;77;77;94;94;111;111;128;128;145;145;162;162;179;179;196;196;213;213;230;230;247;247;264;264;281;281;298;298;315;315;332;332;349;349;366;366;383;383;400;400;417;417;434;434;451;451;468;468;485;485;502;502;519;519;536;536;553;553;570;570;587;587;604;604;621;621;638;638;655;655;672;672;689;689;706;706;723;723;740;740;757;757;774;774;791;791;808;808;825;825;842;842;859;859"/><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;0.4449;0.4451;1.0000" values="0;0;1;1;0;0"/></rect>
<line x1="468.0" y1="96" x2="468.0" y2="314" stroke="#e5484d" stroke-width="2" stroke-dasharray="5 4"/>
<text x="468.0" y="332" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">深度の段差(輪郭)</text>
<rect x="60.0" y="350.0" width="420" height="150" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="60.0" y="340.0" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">輪郭の近くの画素(画素 23)が使う重み</text>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2521;0.2523;1.0000" values="0;0;1;1"/><rect x="80.0" y="459.17" width="20.0" height="10.83" fill="#fca5a5" opacity="0.9"/>
<rect x="98.0" y="459.17" width="16.0" height="10.83" fill="#3b82f6" opacity="0.95"/>
<text x="100.0" y="488.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">18</text>
<rect x="116.0" y="447.76" width="20.0" height="22.24" fill="#fca5a5" opacity="0.9"/>
<rect x="134.0" y="447.76" width="16.0" height="22.24" fill="#3b82f6" opacity="0.95"/>
<text x="136.0" y="488.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">19</text>
<rect x="152.0" y="431.06" width="20.0" height="38.94" fill="#fca5a5" opacity="0.9"/>
<rect x="170.0" y="431.06" width="16.0" height="38.94" fill="#3b82f6" opacity="0.95"/>
<text x="172.0" y="488.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">20</text>
<rect x="188.0" y="411.91" width="20.0" height="58.09" fill="#fca5a5" opacity="0.9"/>
<rect x="206.0" y="411.91" width="16.0" height="58.09" fill="#3b82f6" opacity="0.95"/>
<text x="208.0" y="488.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">21</text>
<rect x="224.0" y="396.15" width="20.0" height="73.85" fill="#fca5a5" opacity="0.9"/>
<rect x="242.0" y="396.15" width="16.0" height="73.85" fill="#3b82f6" opacity="0.95"/>
<text x="244.0" y="488.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">22</text>
<rect x="260.0" y="390.0" width="20.0" height="80.0" fill="#fca5a5" opacity="0.9"/>
<rect x="278.0" y="390.0" width="16.0" height="80.0" fill="#3b82f6" opacity="0.95"/>
<text x="280.0" y="488.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">23</text>
<rect x="296.0" y="396.15" width="20.0" height="73.85" fill="#fca5a5" opacity="0.9"/>
<rect x="314.0" y="396.15" width="16.0" height="73.85" fill="#3b82f6" opacity="0.95"/>
<text x="316.0" y="488.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">24</text>
<rect x="332.0" y="411.91" width="20.0" height="58.09" fill="#fca5a5" opacity="0.9"/>
<rect x="350.0" y="470.0" width="16.0" height="0.5" fill="#3b82f6" opacity="0.95"/>
<text x="352.0" y="488.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#e5484d">25</text>
<rect x="368.0" y="431.06" width="20.0" height="38.94" fill="#fca5a5" opacity="0.9"/>
<rect x="386.0" y="470.0" width="16.0" height="0.5" fill="#3b82f6" opacity="0.95"/>
<text x="388.0" y="488.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#e5484d">26</text>
<rect x="404.0" y="447.76" width="20.0" height="22.24" fill="#fca5a5" opacity="0.9"/>
<rect x="422.0" y="470.0" width="16.0" height="0.5" fill="#3b82f6" opacity="0.95"/>
<text x="424.0" y="488.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#e5484d">27</text>
<rect x="440.0" y="459.17" width="20.0" height="10.83" fill="#fca5a5" opacity="0.9"/>
<rect x="458.0" y="470.0" width="16.0" height="0.5" fill="#3b82f6" opacity="0.95"/>
<text x="460.0" y="488.0" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#e5484d">28</text>
<text x="270.0" y="390.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">赤 = ガウス / 青 = バイラテラル</text>
</g>
<text x="520" y="372" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">輪郭の向こう側(赤い番号)の重み:</text>
<text x="520" y="396" text-anchor="start" style="font-size:17px;font-weight:700;fill:#7c3aed" opacity="0">ガウス 27% → バイラテラル 0.0%<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2675;0.2677;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4757;0.4759;1.0000" values="0;0;1;1"/><rect x="520" y="416" width="410" height="100" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="536" y="440" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">正解とのずれ(全体): ガウス 0.051 / バイラテラル 0.034</text>
<text x="536" y="463" text-anchor="start" style="font-size:14px;font-weight:700;fill:#991b1b">輪郭の近く(8 画素): ガウス 0.080 / バイラテラル 0.039</text>
<text x="536" y="486" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">ガウスは輪郭を越えて混ぜるので、段差がにじむ</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ノイズのある AO を、ぼかして消したい<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">左から右へ、各画素の周り 11 画素を、重み付きで平均する<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;0.4449;0.4451;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">バイラテラルは、深度が違う画素の重みを 0 に近づけるので、輪郭が保たれる<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4449;0.4451;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:bilateral-blur:end -->

### The Problem with a Plain Blur {#通常のぼかしの問題}

AO の画像を**そのままぼかす**と**物体の境界**で**手前の物体の AO と、奥の物体の AO が混ざり**ます。手前の物体の縁に**暗い輪**が出たり、**接地の暗さがにじんで広がる**ことがあります。

### Bilateral: Blend Only "Nearby" Pixels {#バイラテラル近いものだけを混ぜる}

**バイラテラル フィルタ**は、中心の画素と**似た画素だけ**を、重み付きで混ぜます。**似ている**とは、AO では**深度（と法線）が近い**ことです。

<div class="formula">AO′(p) = Σ_q w(p, q) · AO(q) / Σ_q w(p, q)　、　w = w_空間 · w_深度 · w_法線</div>

| 重み | 式の例 | 意味 |
| --- | --- | --- |
| **w_空間** | ガウス、または一様 | 距離が近いほど大 |
| **w_深度** | `exp(−\|z_p − z_q\| · k)` または `1 / (ε + \|z_p − z_q\|)` | **深度が近い**ほど大。**別の面なら 0 に近づく** |
| **w_法線** | `pow(saturate(dot(n_p, n_q)), 8)` | **法線が近い**ほど大。**向きの違う面を混ぜない** |

```hlsl
float BilateralBlur(float2 uv, float2 dir) {
  float center_z = LinearDepth(uv);
  float3 center_n = Normal(uv);
  float sum = 0.0;
  float weight_sum = 0.0;

  [unroll] for (int i = -kRadius; i <= kRadius; ++i) {
    float2 suv = uv + dir * texel_size * i;
    float ao = ao_tex.SampleLevel(point_sampler, suv, 0).r;
    float z = LinearDepth(suv);

    float w = gaussian[abs(i)];
    w *= exp(-abs(center_z - z) * depth_sharpness / center_z);
    w *= pow(saturate(dot(center_n, Normal(suv))), 8.0);

    sum += ao * w;
    weight_sum += w;
  }
  return sum / max(weight_sum, 1e-4);
}
```

| 点 | 説明 |
| --- | --- |
| **深度の差を中心の深度で割る** | **遠いほど、深度の差が大きく出る**ので、相対的な差で比べる |
| **`depth_sharpness`** | 大きいほど、境界を厳しく守る |
| **ポイント サンプリング** | AO と深度は、**補間せず**に読む |

### Making It Separable (Horizontal, Then Vertical) {#分離可能にする横--縦}

2D のぼかしを**横 1 回 ＋ 縦 1 回**に分けると、**N² → 2N** 回の読み込みで済みます。**バイラテラルは、厳密には分離できません**（重みが、2D の位置に依存）が、**実用上は分離して近似**します。

| 方式 | 読み込み回数（半径 4 の例） | 品質 |
| --- | --- | --- |
| <strong>2D（全画素）</strong> | 81 | 正確 |
| <strong>分離（横 → 縦）</strong> | 18 | 縦横の斜めでわずかな乱れ |

### A Box Blur Matched to 4×4 Noise {#44-ノイズに合わせたボックス-ぼかし}

**4×4 のノイズ テクスチャ**を使った SSAO（[Hemisphere SSAO](../ssao-hemisphere.md)）では**ノイズが 4 画素周期**で繰り返すので、**4×4 のボックス ぼかし**で、**周期のパターンがちょうど消えます**。**深度の重み付き**にすれば、境界も守れます。

## Common Mistakes {#よくあるミス}

??? failure "通常のガウスでぼかして、物の輪郭に AO のにじみ（ハロー）が出る"
    **深度・法線で重みを付ける**（バイラテラル）。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **深度・法線が近い画素だけ混ぜる**
    - [x] **エッジを保って、ノイズだけ消す**

## References {#参考}

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## Related Pages {#関連ページ}

- [AO Filtering](index.md)
- [Upsampling](upsample.md)
- [Gaussian Blur](../../postprocess/bloom/gaussian.md)
