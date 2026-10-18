---
title: Cracks and Seams
tags:
  - 描画
---

# Cracks and Seams

**LOD の異なる区画が隣り合うと、境界で頂点が合わず、隙間（クラック）ができます**。**境界の頂点を調整する**ことで、**隙間を埋められます**。このページでは、**継ぎ目の原因と対策**を説明します。

!!! tip "ポイント"
    - **原因 ＝ 隣の区画の頂点が、粗い側にはない**。
    - **対策 1：粗い側に合わせて、細かい側の境界頂点を動かす**。
    - **対策 2：境界にスカート（垂れ幕）を付ける**。
    - **CDLOD は、モーフィングで自然に解決**する。

<!-- fig:lod-cracks:begin -->

<svg class="fig illust motion" data-fig="lod-cracks" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-lod-cracks" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">LOD の継ぎ目の割れ目: 粗い側と細かい側で、境の頂点の高さが食い違うと、穴が空く。細かい側を、粗い側に合わせる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。左は LOD 1(間隔 2)、右は LOD 0(間隔 1)。境(x = 8)の近くの高さを、計算して、割れ目の大きさを測る</text>
<rect x="30" y="96" width="900" height="260" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 高さ(黒 = 細かい LOD の頂点、赤い線 = 粗い LOD の辺)</text>
<path d="M60.0,259.8 L110.0,195.96 L160.0,174.65 L210.0,175.28 L260.0,231.02 L310.0,235.1 L360.0,203.12 L410.0,196.94 L460.0,228.4 L510.0,229.44 L560.0,274.97 L610.0,264.42 L660.0,242.93 L710.0,249.79 L760.0,229.36 L810.0,235.07 L860.0,253.01" fill="none" stroke="#1f2937" stroke-width="2.5"/>
<circle cx="60.0" cy="259.8" r="4" fill="#1f2937"/>
<circle cx="110.0" cy="195.96" r="4" fill="#1f2937"/>
<circle cx="160.0" cy="174.65" r="4" fill="#1f2937"/>
<circle cx="210.0" cy="175.28" r="4" fill="#1f2937"/>
<circle cx="260.0" cy="231.02" r="4" fill="#1f2937"/>
<circle cx="310.0" cy="235.1" r="4" fill="#1f2937"/>
<circle cx="360.0" cy="203.12" r="4" fill="#1f2937"/>
<circle cx="410.0" cy="196.94" r="4" fill="#1f2937"/>
<circle cx="460.0" cy="228.4" r="4" fill="#1f2937"/>
<circle cx="510.0" cy="229.44" r="4" fill="#1f2937"/>
<circle cx="560.0" cy="274.97" r="4" fill="#1f2937"/>
<circle cx="610.0" cy="264.42" r="4" fill="#1f2937"/>
<circle cx="660.0" cy="242.93" r="4" fill="#1f2937"/>
<circle cx="710.0" cy="249.79" r="4" fill="#1f2937"/>
<circle cx="760.0" cy="229.36" r="4" fill="#1f2937"/>
<circle cx="810.0" cy="235.07" r="4" fill="#1f2937"/>
<circle cx="860.0" cy="253.01" r="4" fill="#1f2937"/>
<line x1="460.0" y1="110" x2="460.0" y2="330.0" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 4"/>
<text x="466.0" y="124" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">LOD の境</text>
<path d="M60.0,259.8 L85.0,238.51 L110.0,217.22 L135.0,195.94 L160.0,174.65 L185.0,188.74 L210.0,202.84 L235.0,216.93 L260.0,231.02 L285.0,224.05 L310.0,217.07 L335.0,210.1 L360.0,203.12 L385.0,209.44 L410.0,215.76 L435.0,222.08 L460.0,228.4" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></path>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1243;0.1244;1.0000" values="0;0;1;1"/><line x1="110.0" y1="195.96" x2="110.0" y2="217.22" stroke="#e5aa28" stroke-width="5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1509;0.1511;1.0000" values="0;0;1;1"/><line x1="210.0" y1="175.28" x2="210.0" y2="202.84" stroke="#e5aa28" stroke-width="5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1776;0.1778;1.0000" values="0;0;1;1"/><line x1="310.0" y1="235.1" x2="310.0" y2="217.07" stroke="#e5aa28" stroke-width="5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2043;0.2044;1.0000" values="0;0;1;1"/><line x1="410.0" y1="196.94" x2="410.0" y2="215.76" stroke="#e5aa28" stroke-width="5"/>
</g>
<text x="70" y="134" text-anchor="start" style="font-size:13px;font-weight:700;fill:#b45309" opacity="0">オレンジ = 割れ目(同じ x で、高さが違う)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1109;0.1111;1.0000" values="0;0;1;1"/></text>
<text x="40" y="380" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">奇数の頂点での割れ目:</text>
<text x="240" y="384" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1243;0.1244;1.0000" values="1;1;0;0"/></text>
<text x="240" y="384" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">59<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1243;0.1244;0.1509;0.1511;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="384" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">77<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1509;0.1511;0.1776;0.1778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="384" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">50<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1776;0.1778;0.2043;0.2044;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="384" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">52<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2043;0.2044;1.0000" values="0;0;1;1"/></text>
<text x="290" y="384" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">(×0.01 m。粗い辺と、細かい頂点の高さの差)</text>
<path d="M60.0,259.8 L110.0,217.22 L160.0,174.65 L210.0,202.84 L260.0,231.02 L310.0,217.07 L360.0,203.12 L410.0,215.76 L460.0,228.4 L510.0,229.44 L560.0,274.97 L610.0,264.42 L660.0,242.93 L710.0,249.79 L760.0,229.36 L810.0,235.07 L860.0,253.01" fill="none" stroke="#2ea043" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;1.0000" values="0;0;1;1"/></path>
<text x="40" y="420" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">対策: 粗い辺の上にある、細かい頂点を、粗い辺の高さへ下ろす(奇数番目を、両隣の平均にする)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;1.0000" values="0;0;1;1"/><rect x="40" y="446" width="880" height="60" rx="12" fill="#f0fdf4" stroke="#2ea043" stroke-width="2.5"/>
<text x="56" y="470" text-anchor="start" style="font-size:15px;font-weight:700;fill:#166534">割れ目の最大 0.77 m → 対策後 0 m</text>
<text x="56" y="494" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">頂点の高さを、LOD 境でだけ、粗い側に合わせると、継ぎ目が閉じる(スカートで、隠す方法もある)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">LOD の異なる地形が、隣り合う<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">細かい側の頂点が、粗い辺の上にないと、高さが食い違って、穴が見える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.3109;0.3111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">境の頂点を、粗い辺に載せれば、割れ目が閉じる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3109;0.3111;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:lod-cracks:end -->

## Seams (Cracks) {#継ぎ目クラック}
**LOD の違うタイルが隣り合う**と、<strong>境界で頂点の位置が合わず、隙間（クラック）</strong>ができます。**細かい側の境界の頂点が、粗い側の辺の上にないため**です。

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="LOD の継ぎ目">
<text x="20" y="24" class="fig-title">LOD の継ぎ目：細かい側の頂点が、粗い側の辺から浮く</text>
<line x1="120" y1="150" x2="420" y2="150" stroke="currentColor" stroke-opacity="0.7" stroke-width="2"/>
<polyline fill="none" stroke="#4c8bf5" stroke-width="2" points="120,150 195,128 270,150 345,118 420,150"/>
<circle cx="195" cy="128" r="4" fill="#e5484d"/><circle cx="345" cy="118" r="4" fill="#e5484d"/>
<text x="120" y="190" style="font-size:12px">粗い側の辺 / 細かい側（青）の中間頂点が、辺から離れる → 隙間</text>
<line x1="500" y1="150" x2="740" y2="150" stroke="currentColor" stroke-opacity="0.7" stroke-width="2"/>
<polyline fill="none" stroke="#2ea043" stroke-width="2" points="500,150 560,150 620,150 680,150 740,150"/>
<text x="500" y="190" style="font-size:12px">対策：中間頂点を、辺の上へ寄せる</text>
</svg>

| 対策 | 内容 |
| --- | --- |
| **モーフィング** | **境界の頂点が粗い側の辺の上に来るまで、距離で寄せる**。<strong>連続的（CDLOD はこれ）</strong> |
| **スカート** | **タイルの縁から、下向きに垂れ幕を追加**して**隙間を隠す**。**簡単だが見た目が少し粗い** |
| **境界専用のインデックス** | **隣が粗いとき、細かい側の境界を三角形の貼り方で繋ぐ**（**LOD の組み合わせごとにメッシュが要る**） |
| **共通の頂点を使う** | **境界の頂点の高さを両側で同じ式（粗い側の補間）で決める** |
| **隣のレベル差を 1 までに制限** | **隣接するタイルの LOD の差を 1 以内**にする（**四分木の制約**） |

## Common Mistakes {#よくあるミス}

??? failure "LOD の境界に、背景が見える隙間が出る"
    **スカート**または**境界の頂点調整**を入れる。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **境界の頂点を合わせるか、スカートで隠す**

## References {#参考}

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## Related Pages {#関連ページ}

- [Terrain LOD](index.md)
- [Geomorphing](morphing.md)
