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

<svg class="fig illust motion" data-fig="height-mip-bars" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-height-mip-bars" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">高さのミップ: 隣り合う高さを平均して、半分の大きさを作る。遠景は粗い層で、足りる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 次元の高さ 16 点。層 0(16 点)→ 層 1(8 点)→ 層 2(4 点)→ 層 3(2 点)。層が粗いほど、元の地形との差が増える</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.2679;0.2681;1.0000" values="0;0;1;1;0;0"/><rect x="72.0" y="302.4" width="46.0" height="57.6" fill="#64748b" opacity="0.35"/>
<rect x="122.0" y="308.8" width="46.0" height="51.2" fill="#64748b" opacity="0.35"/>
<rect x="172.0" y="313.41" width="46.0" height="46.59" fill="#64748b" opacity="0.35"/>
<rect x="222.0" y="256.37" width="46.0" height="103.63" fill="#64748b" opacity="0.35"/>
<rect x="272.0" y="208.31" width="46.0" height="151.69" fill="#64748b" opacity="0.35"/>
<rect x="322.0" y="213.65" width="46.0" height="146.35" fill="#64748b" opacity="0.35"/>
<rect x="372.0" y="276.29" width="46.0" height="83.71" fill="#64748b" opacity="0.35"/>
<rect x="422.0" y="269.32" width="46.0" height="90.68" fill="#64748b" opacity="0.35"/>
<rect x="472.0" y="205.49" width="46.0" height="154.51" fill="#64748b" opacity="0.35"/>
<rect x="522.0" y="212.05" width="46.0" height="147.95" fill="#64748b" opacity="0.35"/>
<rect x="572.0" y="218.53" width="46.0" height="141.47" fill="#64748b" opacity="0.35"/>
<rect x="622.0" y="278.7" width="46.0" height="81.3" fill="#64748b" opacity="0.35"/>
<rect x="672.0" y="247.03" width="46.0" height="112.97" fill="#64748b" opacity="0.35"/>
<rect x="722.0" y="255.28" width="46.0" height="104.72" fill="#64748b" opacity="0.35"/>
<rect x="772.0" y="211.7" width="46.0" height="148.3" fill="#64748b" opacity="0.35"/>
<rect x="822.0" y="222.26" width="46.0" height="137.74" fill="#64748b" opacity="0.35"/>
<text x="70.0" y="128" text-anchor="start" style="font-size:15px;font-weight:700;fill:#64748b">層 0(16 点): 元との差(平均)0.00 / 最大 0.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2679;0.2681;0.4722;0.4723;1.0000" values="0;0;1;1;0;0"/><rect x="72.0" y="305.6" width="96.0" height="54.4" fill="#2563eb" opacity="0.55"/>
<rect x="172.0" y="284.89" width="96.0" height="75.11" fill="#2563eb" opacity="0.55"/>
<rect x="272.0" y="210.98" width="96.0" height="149.02" fill="#2563eb" opacity="0.55"/>
<rect x="372.0" y="272.8" width="96.0" height="87.2" fill="#2563eb" opacity="0.55"/>
<rect x="472.0" y="208.77" width="96.0" height="151.23" fill="#2563eb" opacity="0.55"/>
<rect x="572.0" y="248.61" width="96.0" height="111.39" fill="#2563eb" opacity="0.55"/>
<rect x="672.0" y="251.15" width="96.0" height="108.85" fill="#2563eb" opacity="0.55"/>
<rect x="772.0" y="216.98" width="96.0" height="143.02" fill="#2563eb" opacity="0.55"/>
<text x="70.0" y="128" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">層 1(8 点): 元との差(平均)0.28 / 最大 0.84</text>
<path d="M95.0,302.4 L145.0,308.8 L195.0,313.41 L245.0,256.37 L295.0,208.31 L345.0,213.65 L395.0,276.29 L445.0,269.32 L495.0,205.49 L545.0,212.05 L595.0,218.53 L645.0,278.7 L695.0,247.03 L745.0,255.28 L795.0,211.7 L845.0,222.26" fill="none" stroke="#1f2937" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4722;0.4723;0.6764;0.6766;1.0000" values="0;0;1;1;0;0"/><rect x="72.0" y="295.25" width="196.0" height="64.75" fill="#2ea043" opacity="0.55"/>
<rect x="272.0" y="241.89" width="196.0" height="118.11" fill="#2ea043" opacity="0.55"/>
<rect x="472.0" y="228.69" width="196.0" height="131.31" fill="#2ea043" opacity="0.55"/>
<rect x="672.0" y="234.07" width="196.0" height="125.93" fill="#2ea043" opacity="0.55"/>
<text x="70.0" y="128" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">層 2(4 点): 元との差(平均)0.64 / 最大 1.39</text>
<path d="M95.0,302.4 L145.0,308.8 L195.0,313.41 L245.0,256.37 L295.0,208.31 L345.0,213.65 L395.0,276.29 L445.0,269.32 L495.0,205.49 L545.0,212.05 L595.0,218.53 L645.0,278.7 L695.0,247.03 L745.0,255.28 L795.0,211.7 L845.0,222.26" fill="none" stroke="#1f2937" stroke-width="2.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6764;0.6766;1.0000" values="0;0;1;1"/><rect x="72.0" y="268.57" width="396.0" height="91.43" fill="#e5aa28" opacity="0.55"/>
<rect x="472.0" y="231.38" width="396.0" height="128.62" fill="#e5aa28" opacity="0.55"/>
<text x="70.0" y="128" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">層 3(2 点): 元との差(平均)0.74 / 最大 1.67</text>
<path d="M95.0,302.4 L145.0,308.8 L195.0,313.41 L245.0,256.37 L295.0,208.31 L345.0,213.65 L395.0,276.29 L445.0,269.32 L495.0,205.49 L545.0,212.05 L595.0,218.53 L645.0,278.7 L695.0,247.03 L745.0,255.28 L795.0,211.7 L845.0,222.26" fill="none" stroke="#1f2937" stroke-width="2.5"/>
</g>
<line x1="70.0" y1="360.0" x2="870.0" y2="360.0" stroke="#94a3b8" stroke-width="2"/>
<text x="40" y="420" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">点の数:</text>
<text x="120" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="120" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.2679;0.2681;1.0000" values="0;0;1;1;0;0"/></text>
<text x="120" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">8<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2679;0.2681;0.4722;0.4723;1.0000" values="0;0;1;1;0;0"/></text>
<text x="120" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4722;0.4723;0.6764;0.6766;1.0000" values="0;0;1;1;0;0"/></text>
<text x="120" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">2<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6764;0.6766;1.0000" values="0;0;1;1"/></text>
<text x="40" y="458" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">元の地形との差(×0.01 m):</text>
<text x="280" y="462" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="280" y="462" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.2679;0.2681;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="462" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">28<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2679;0.2681;0.4722;0.4723;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="462" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">64<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4722;0.4723;0.6764;0.6766;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="462" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">74<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6764;0.6766;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8594;0.8596;1.0000" values="0;0;1;1"/><rect x="440" y="410" width="490" height="100" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="456" y="434" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">層が 1 つ上がると、点は半分、差は増える(0.00 → 0.74)</text>
<text x="456" y="457" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">遠くは、画面で 1 画素が数 m ぶんなので、粗い層で、見た目が変わらない</text>
<text x="456" y="479" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">遠い頂点を、粗い層から読めば、テクスチャの読み込みが軽く、キャッシュにも優しい</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">高さを、隣と平均して、小さな高さマップを作る<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">層を重ねるほど、粗く、小さく<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.8807;0.8809;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">距離に応じて、層を選ぶ(ミップ)<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8807;0.8809;1.0000;1.0000" values="0;0;1;1;0"/></text>
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
