---
title: Heightmap LOD (Mips)
tags:
  - 描画
---

# Heightmap LOD (Mips)

**遠くの地形は、高さマップも粗くてよく、ミップマップが使えます**。**LOD に応じて、読むミップを選ぶ**と、**テクスチャのちらつきと帯域**を**減らせます**。このページでは、**高さマップのミップ**を説明します。

!!! tip "ポイント"
    - **高さマップにも、ミップを作る**。
    - **頂点の LOD に合わせて、ミップを選ぶ**。
    - **ミップで高さの平均を取ると、山が低くなる**。
    - **最大・最小のミップも用意すると、カリングに使える**。

## 高さマップの LOD（ミップ）
**メッシュだけでなく、高さマップもミップを使います**。**遠くの頂点は粗いミップから読む**と**ちらつかず、メモリ アクセスも減ります**。

対応の要点です。ミップ レベルは LOD レベルに対応し、LOD が 1 下がるごとに、ミップを 1 上げます。高さのミップは平均でよいですが、最大値のミップもカリングに使えます。最小・最大の高さは、ノードの境界ボックスに使います。

<!-- fig:height-mip-bars:begin -->

<svg class="fig illust motion" data-fig="height-mip-bars" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-height-mip-bars" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">高さのミップ: 隣り合う 2 つを平均して、半分の解像度を作る</text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.2960;0.2963;1.0000" values="0;0;1;1;0.25;0.25"/><rect x="113.0" y="270.0" width="64.0" height="60.0" fill="#64748b" opacity="0.7"/>
<rect x="183.0" y="170.0" width="64.0" height="160.0" fill="#64748b" opacity="0.7"/>
<rect x="253.0" y="220.0" width="64.0" height="110.00000000000001" fill="#64748b" opacity="0.7"/>
<rect x="323.0" y="200.0" width="64.0" height="130.0" fill="#64748b" opacity="0.7"/>
<rect x="393.0" y="290.0" width="64.0" height="40.0" fill="#64748b" opacity="0.7"/>
<rect x="463.0" y="260.0" width="64.0" height="70.0" fill="#64748b" opacity="0.7"/>
<rect x="533.0" y="150.0" width="64.0" height="180.0" fill="#64748b" opacity="0.7"/>
<rect x="603.0" y="230.0" width="64.0" height="100.0" fill="#64748b" opacity="0.7"/>
<text x="98" y="324" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">層 0（8 点）</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;0.5182;0.5185;1.0000" values="0;0;1;1;0.25;0.25"/><rect x="113.0" y="220.0" width="134.0" height="110.00000000000001" fill="#2563eb" opacity="0.85"/>
<rect x="253.0" y="210.0" width="134.0" height="120.00000000000001" fill="#2563eb" opacity="0.85"/>
<rect x="393.0" y="275.0" width="134.0" height="55.00000000000001" fill="#2563eb" opacity="0.85"/>
<rect x="533.0" y="190.0" width="134.0" height="140.0" fill="#2563eb" opacity="0.85"/>
<text x="98" y="324" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2563eb">層 1（4 点）</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;0.7404;0.7407;1.0000" values="0;0;1;1;0.25;0.25"/><rect x="113.0" y="215.0" width="274.0" height="115.00000000000001" fill="#2ea043" opacity="0.85"/>
<rect x="393.0" y="232.5" width="274.0" height="97.5" fill="#2ea043" opacity="0.85"/>
<text x="98" y="324" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043">層 2（2 点）</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7404;0.7407;1.0000" values="0;0;1;1"/><rect x="113.0" y="223.75" width="554.0" height="106.25" fill="#e5aa28" opacity="0.85"/>
<text x="98" y="324" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5aa28">層 3（1 点）</text>
</g>
<line x1="110" y1="330" x2="670" y2="330" stroke="#94a3b8" stroke-width="2"/>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">8 点の高さ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">元の高さ（層 0）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.2960;0.2963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2 つずつ平均 → 4 点（層 1）。山の細かい凹凸が消える<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;0.5182;0.5185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">さらに平均 → 2 点（層 2）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;0.7404;0.7407;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="385" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">最後は 1 点（全体の平均の高さ）。遠景には、粗い層を使う<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7404;0.7407;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:height-mip-bars:end -->

## よくあるミス

??? failure "遠くの山が、低く見える"
    **最大値のミップ**も**併用**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **LOD に合わせて、ミップを選ぶ**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain LOD](index.md)
- [Heightmaps and Meshes](../heightmap-mesh/index.md)
