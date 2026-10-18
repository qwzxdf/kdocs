---
title: Geometry Clipmaps
tags:
  - 描画
---

# Geometry Clipmaps

**クリップマップは、カメラを中心に、同心の格子を重ねる手法**で、**外側ほど粗く**なります。**メッシュがシンプルで、四分木が要りません**。このページでは、**クリップマップの仕組み**を説明します。

!!! tip "ポイント"
    - **カメラ中心に、入れ子の格子（リング）を並べる**。
    - **外側のリングほど、2 倍の大きさ・粗さ**。
    - **カメラが動くと、格子をずらす**。
    - **高さデータも、同じ入れ子で持つ**。

## クリップマップ
**ジオメトリ クリップマップ**（Losasso & Hoppe、2004）は、**カメラを中心に入れ子になった正方形リング**で**LOD を表現**します。**一番内側が最も細かく、外側ほど 2 倍ずつ粗く**なります。

| 項目 | 内容 |
| --- | --- |
| **構造** | **同じ頂点数の正方形リングが、倍々の大きさで重なる**（例：各 255×255） |
| **カメラ追従** | **カメラが動くとリングをグリッド単位でスクロール**（**円環バッファ**で高さを更新） |
| **利点** | **三角形の数が一定**。**構造が単純**。**GPU に向く** |
| **欠点** | **視点から遠くてもリングの数だけは描く**（**画面外を捨てにくい**）。**高さデータをリングごとに管理** |
| **用途** | **広大な地形・海面**（[水面のクリップマップ](../../water/waves/index.md)と同じ構造） |

**四分木はノードごとにカリングができて柔軟**、**クリップマップは、構造が単純で三角形数が一定**という**違い**があります。

<!-- fig:clipmap-rings:begin -->

<svg class="fig illust motion" data-fig="clipmap-rings" viewBox="0 0 780 480" role="img"><rect x="0" y="0" width="780" height="480" rx="14" fill="#ffffff"/>
<defs><marker id="arr-clipmap-rings" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">クリップマップ: 同じ格子数の層を、倍々の広さで入れ子にする</text>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6077;0.6080;1.0000" values="0;0;1;1"/><rect x="370.0" y="215.0" width="40.0" height="40.0" fill="none" stroke="#2ea043" stroke-width="2.5"/>
<line x1="375.0" y1="215.0" x2="375.0" y2="255.0" stroke="#2ea043" stroke-width="1"/>
<line x1="370.0" y1="220.0" x2="410.0" y2="220.0" stroke="#2ea043" stroke-width="1"/>
<line x1="380.0" y1="215.0" x2="380.0" y2="255.0" stroke="#2ea043" stroke-width="1"/>
<line x1="370.0" y1="225.0" x2="410.0" y2="225.0" stroke="#2ea043" stroke-width="1"/>
<line x1="385.0" y1="215.0" x2="385.0" y2="255.0" stroke="#2ea043" stroke-width="1"/>
<line x1="370.0" y1="230.0" x2="410.0" y2="230.0" stroke="#2ea043" stroke-width="1"/>
<line x1="390.0" y1="215.0" x2="390.0" y2="255.0" stroke="#2ea043" stroke-width="1"/>
<line x1="370.0" y1="235.0" x2="410.0" y2="235.0" stroke="#2ea043" stroke-width="1"/>
<line x1="395.0" y1="215.0" x2="395.0" y2="255.0" stroke="#2ea043" stroke-width="1"/>
<line x1="370.0" y1="240.0" x2="410.0" y2="240.0" stroke="#2ea043" stroke-width="1"/>
<line x1="400.0" y1="215.0" x2="400.0" y2="255.0" stroke="#2ea043" stroke-width="1"/>
<line x1="370.0" y1="245.0" x2="410.0" y2="245.0" stroke="#2ea043" stroke-width="1"/>
<line x1="405.0" y1="215.0" x2="405.0" y2="255.0" stroke="#2ea043" stroke-width="1"/>
<line x1="370.0" y1="250.0" x2="410.0" y2="250.0" stroke="#2ea043" stroke-width="1"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4317;0.4320;1.0000" values="0;0;1;1"/><rect x="350.0" y="195.0" width="80.0" height="80.0" fill="none" stroke="#2563eb" stroke-width="2.5"/>
<line x1="360.0" y1="195.0" x2="360.0" y2="275.0" stroke="#2563eb" stroke-width="1"/>
<line x1="350.0" y1="205.0" x2="430.0" y2="205.0" stroke="#2563eb" stroke-width="1"/>
<line x1="370.0" y1="195.0" x2="370.0" y2="275.0" stroke="#2563eb" stroke-width="1"/>
<line x1="350.0" y1="215.0" x2="430.0" y2="215.0" stroke="#2563eb" stroke-width="1"/>
<line x1="380.0" y1="195.0" x2="380.0" y2="275.0" stroke="#2563eb" stroke-width="1"/>
<line x1="350.0" y1="225.0" x2="430.0" y2="225.0" stroke="#2563eb" stroke-width="1"/>
<line x1="390.0" y1="195.0" x2="390.0" y2="275.0" stroke="#2563eb" stroke-width="1"/>
<line x1="350.0" y1="235.0" x2="430.0" y2="235.0" stroke="#2563eb" stroke-width="1"/>
<line x1="400.0" y1="195.0" x2="400.0" y2="275.0" stroke="#2563eb" stroke-width="1"/>
<line x1="350.0" y1="245.0" x2="430.0" y2="245.0" stroke="#2563eb" stroke-width="1"/>
<line x1="410.0" y1="195.0" x2="410.0" y2="275.0" stroke="#2563eb" stroke-width="1"/>
<line x1="350.0" y1="255.0" x2="430.0" y2="255.0" stroke="#2563eb" stroke-width="1"/>
<line x1="420.0" y1="195.0" x2="420.0" y2="275.0" stroke="#2563eb" stroke-width="1"/>
<line x1="350.0" y1="265.0" x2="430.0" y2="265.0" stroke="#2563eb" stroke-width="1"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2557;0.2560;1.0000" values="0;0;1;1"/><rect x="310.0" y="155.0" width="160.0" height="160.0" fill="none" stroke="#e5aa28" stroke-width="2.5"/>
<line x1="330.0" y1="155.0" x2="330.0" y2="315.0" stroke="#e5aa28" stroke-width="1"/>
<line x1="310.0" y1="175.0" x2="470.0" y2="175.0" stroke="#e5aa28" stroke-width="1"/>
<line x1="350.0" y1="155.0" x2="350.0" y2="315.0" stroke="#e5aa28" stroke-width="1"/>
<line x1="310.0" y1="195.0" x2="470.0" y2="195.0" stroke="#e5aa28" stroke-width="1"/>
<line x1="370.0" y1="155.0" x2="370.0" y2="315.0" stroke="#e5aa28" stroke-width="1"/>
<line x1="310.0" y1="215.0" x2="470.0" y2="215.0" stroke="#e5aa28" stroke-width="1"/>
<line x1="390.0" y1="155.0" x2="390.0" y2="315.0" stroke="#e5aa28" stroke-width="1"/>
<line x1="310.0" y1="235.0" x2="470.0" y2="235.0" stroke="#e5aa28" stroke-width="1"/>
<line x1="410.0" y1="155.0" x2="410.0" y2="315.0" stroke="#e5aa28" stroke-width="1"/>
<line x1="310.0" y1="255.0" x2="470.0" y2="255.0" stroke="#e5aa28" stroke-width="1"/>
<line x1="430.0" y1="155.0" x2="430.0" y2="315.0" stroke="#e5aa28" stroke-width="1"/>
<line x1="310.0" y1="275.0" x2="470.0" y2="275.0" stroke="#e5aa28" stroke-width="1"/>
<line x1="450.0" y1="155.0" x2="450.0" y2="315.0" stroke="#e5aa28" stroke-width="1"/>
<line x1="310.0" y1="295.0" x2="470.0" y2="295.0" stroke="#e5aa28" stroke-width="1"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="0;0;1;1"/><rect x="230.0" y="75.0" width="320.0" height="320.0" fill="none" stroke="#e5484d" stroke-width="2.5"/>
<line x1="270.0" y1="75.0" x2="270.0" y2="395.0" stroke="#e5484d" stroke-width="1"/>
<line x1="230.0" y1="115.0" x2="550.0" y2="115.0" stroke="#e5484d" stroke-width="1"/>
<line x1="310.0" y1="75.0" x2="310.0" y2="395.0" stroke="#e5484d" stroke-width="1"/>
<line x1="230.0" y1="155.0" x2="550.0" y2="155.0" stroke="#e5484d" stroke-width="1"/>
<line x1="350.0" y1="75.0" x2="350.0" y2="395.0" stroke="#e5484d" stroke-width="1"/>
<line x1="230.0" y1="195.0" x2="550.0" y2="195.0" stroke="#e5484d" stroke-width="1"/>
<line x1="390.0" y1="75.0" x2="390.0" y2="395.0" stroke="#e5484d" stroke-width="1"/>
<line x1="230.0" y1="235.0" x2="550.0" y2="235.0" stroke="#e5484d" stroke-width="1"/>
<line x1="430.0" y1="75.0" x2="430.0" y2="395.0" stroke="#e5484d" stroke-width="1"/>
<line x1="230.0" y1="275.0" x2="550.0" y2="275.0" stroke="#e5484d" stroke-width="1"/>
<line x1="470.0" y1="75.0" x2="470.0" y2="395.0" stroke="#e5484d" stroke-width="1"/>
<line x1="230.0" y1="315.0" x2="550.0" y2="315.0" stroke="#e5484d" stroke-width="1"/>
<line x1="510.0" y1="75.0" x2="510.0" y2="395.0" stroke="#e5484d" stroke-width="1"/>
<line x1="230.0" y1="355.0" x2="550.0" y2="355.0" stroke="#e5484d" stroke-width="1"/>
</g>
<circle cx="390" cy="235" r="6" fill="#1f2937"/>
<text x="400" y="227" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">カメラ</text>
<text x="390" y="450" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">どの層も 8×8 のマス(頂点の数は同じ)<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="390" y="450" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">層 0: 最も細かい。カメラの足元<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.2557;0.2560;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="450" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">層 1: 広さ 2 倍、マスも 2 倍の粗さ<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2557;0.2560;0.4317;0.4320;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="450" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">層 2: さらに 2 倍<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4317;0.4320;0.6077;0.6080;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="450" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">層 3: 遠景。頂点の数は変わらないのに、遠くまで届く<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6077;0.6080;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:clipmap-rings:end -->

## よくあるミス

??? failure "カメラの移動で、地形が揺れる"
    **格子の幅の整数倍で移動**して、**スナップ**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **カメラ中心の、入れ子の格子**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain LOD](index.md)
- [CDLOD](cdlod.md)
