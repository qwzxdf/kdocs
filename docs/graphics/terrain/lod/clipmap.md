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

<svg class="fig illust motion" data-fig="clipmap-rings" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-clipmap-rings" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">クリップマップ: 同じ頂点数の層を、倍々の広さで入れ子にする。頂点数は一定で、遠くまで届く</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面。層ごとに、33 頂点。層 0 の間隔が 1 m、層 1 が 2 m、層 2 が 4 m、…。カメラの周りだけ、細かい</text>
<rect x="30" y="96" width="900" height="280" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">層の広がり(横 = カメラからの距離 m、対数)</text>
<line x1="60" y1="330.0" x2="900" y2="330.0" stroke="#94a3b8" stroke-width="2"/>
<circle cx="70.0" cy="330.0" r="7" fill="#1f2937"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/><rect x="70.0" y="130" width="402.21" height="26" fill="#2ea043" opacity="0.8"/>
<text x="76.0" y="148" text-anchor="start" style="font-size:12px;font-weight:700;fill:#ffffff">層 0: 間隔 1 m、〜 16 m</text>
<line x1="70.0" y1="156" x2="70.0" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="70.0" y1="156" x2="70.0" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="169.45" y1="156" x2="169.45" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="227.62" y1="156" x2="227.62" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="268.9" y1="156" x2="268.9" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="300.91" y1="156" x2="300.91" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="327.07" y1="156" x2="327.07" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="349.19" y1="156" x2="349.19" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="368.34" y1="156" x2="368.34" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="385.24" y1="156" x2="385.24" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="400.36" y1="156" x2="400.36" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="414.03" y1="156" x2="414.03" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="426.52" y1="156" x2="426.52" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="438.0" y1="156" x2="438.0" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="448.63" y1="156" x2="448.63" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="458.53" y1="156" x2="458.53" y2="162" stroke="#2ea043" stroke-width="1.5"/>
<line x1="467.79" y1="156" x2="467.79" y2="162" stroke="#2ea043" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2176;0.2178;1.0000" values="0;0;1;1"/><rect x="70.0" y="166" width="501.66" height="26" fill="#2563eb" opacity="0.8"/>
<text x="76.0" y="184" text-anchor="start" style="font-size:12px;font-weight:700;fill:#ffffff">層 1: 間隔 2 m、〜 33 m</text>
<line x1="70.0" y1="192" x2="70.0" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="169.45" y1="192" x2="169.45" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="268.9" y1="192" x2="268.9" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="327.07" y1="192" x2="327.07" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="368.34" y1="192" x2="368.34" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="400.36" y1="192" x2="400.36" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="426.52" y1="192" x2="426.52" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="448.63" y1="192" x2="448.63" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="467.79" y1="192" x2="467.79" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="484.69" y1="192" x2="484.69" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="499.81" y1="192" x2="499.81" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="513.48" y1="192" x2="513.48" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="525.97" y1="192" x2="525.97" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="537.45" y1="192" x2="537.45" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="548.08" y1="192" x2="548.08" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="557.98" y1="192" x2="557.98" y2="198" stroke="#2563eb" stroke-width="1.5"/>
<line x1="567.24" y1="192" x2="567.24" y2="198" stroke="#2563eb" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3687;0.3689;1.0000" values="0;0;1;1"/><rect x="70.0" y="202" width="601.1" height="26" fill="#e5aa28" opacity="0.8"/>
<text x="76.0" y="220" text-anchor="start" style="font-size:12px;font-weight:700;fill:#ffffff">層 2: 間隔 4 m、〜 66 m</text>
<line x1="70.0" y1="228" x2="70.0" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="268.9" y1="228" x2="268.9" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="368.34" y1="228" x2="368.34" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="426.52" y1="228" x2="426.52" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="467.79" y1="228" x2="467.79" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="499.81" y1="228" x2="499.81" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="525.97" y1="228" x2="525.97" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="548.08" y1="228" x2="548.08" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="567.24" y1="228" x2="567.24" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="584.14" y1="228" x2="584.14" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="599.26" y1="228" x2="599.26" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="612.93" y1="228" x2="612.93" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="625.41" y1="228" x2="625.41" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="636.9" y1="228" x2="636.9" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="647.53" y1="228" x2="647.53" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="657.43" y1="228" x2="657.43" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
<line x1="666.69" y1="228" x2="666.69" y2="234" stroke="#e5aa28" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5198;0.5200;1.0000" values="0;0;1;1"/><rect x="70.0" y="238" width="700.55" height="26" fill="#e5484d" opacity="0.8"/>
<text x="76.0" y="256" text-anchor="start" style="font-size:12px;font-weight:700;fill:#ffffff">層 3: 間隔 8 m、〜 132 m</text>
<line x1="70.0" y1="264" x2="70.0" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="368.34" y1="264" x2="368.34" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="467.79" y1="264" x2="467.79" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="525.97" y1="264" x2="525.97" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="567.24" y1="264" x2="567.24" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="599.26" y1="264" x2="599.26" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="625.41" y1="264" x2="625.41" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="647.53" y1="264" x2="647.53" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="666.69" y1="264" x2="666.69" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="683.59" y1="264" x2="683.59" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="698.7" y1="264" x2="698.7" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="712.38" y1="264" x2="712.38" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="724.86" y1="264" x2="724.86" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="736.35" y1="264" x2="736.35" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="746.98" y1="264" x2="746.98" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="756.88" y1="264" x2="756.88" y2="270" stroke="#e5484d" stroke-width="1.5"/>
<line x1="766.14" y1="264" x2="766.14" y2="270" stroke="#e5484d" stroke-width="1.5"/>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6709;0.6711;1.0000" values="0;0;1;1"/><rect x="70.0" y="274" width="800.0" height="26" fill="#7c3aed" opacity="0.8"/>
<text x="76.0" y="292" text-anchor="start" style="font-size:12px;font-weight:700;fill:#ffffff">層 4: 間隔 16 m、〜 264 m</text>
<line x1="70.0" y1="300" x2="70.0" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="467.79" y1="300" x2="467.79" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="567.24" y1="300" x2="567.24" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="625.41" y1="300" x2="625.41" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="666.69" y1="300" x2="666.69" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="698.7" y1="300" x2="698.7" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="724.86" y1="300" x2="724.86" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="746.98" y1="300" x2="746.98" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="766.14" y1="300" x2="766.14" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="783.04" y1="300" x2="783.04" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="798.15" y1="300" x2="798.15" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="811.83" y1="300" x2="811.83" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="824.31" y1="300" x2="824.31" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="835.79" y1="300" x2="835.79" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="846.43" y1="300" x2="846.43" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="856.33" y1="300" x2="856.33" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
<line x1="865.59" y1="300" x2="865.59" y2="306" stroke="#7c3aed" stroke-width="1.5"/>
</g>
<text x="40" y="400" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">頂点の数(層ごとに 33×33):</text>
<text x="280" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="280" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">1,089<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.2176;0.2178;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">2,178<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2176;0.2178;0.3687;0.3689;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">3,267<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3687;0.3689;0.5198;0.5200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">4,356<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5198;0.5200;0.6709;0.6711;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="404" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">5,445<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6709;0.6711;1.0000" values="0;0;1;1"/></text>
<text x="40" y="436" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">同じ範囲を、全部 1 m 間隔で作ると:</text>
<text x="330" y="436" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">278,784 頂点(約 51 倍)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8220;0.8222;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8665;0.8667;1.0000" values="0;0;1;1"/><rect x="40" y="456" width="880" height="56" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="480" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">5 層 5,445 頂点で、半径 264 m まで届く。近く(1 m 間隔)から、遠く(16 m 間隔)まで、頂点数は一定</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">遠くの地形を、近くと同じ細かさで描くのは、無駄<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">層を足すごとに、広さが 2 倍、間隔も 2 倍になる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8665;0.8667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">カメラが動くと、層ごとに、動く単位(間隔)ぶんだけ、ずらして、追いかける<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8665;0.8667;1.0000;1.0000" values="0;0;1;1;0"/></text>
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
