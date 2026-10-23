---
title: カリング
tags:
  - 最適化
  - 3Dゲーム
---

# カリング

**カリング**は見えないものを描かないことです。最も効果が大きく、基本の最適化でドロー コール・頂点処理・ピクセル処理のすべてを、減らせます。このページはカリングの種類（視錐台・オクルージョン・距離・LOD）、それぞれが何を減らすのか、CPU でやる場合の課題、段階的な発展（GPU Driven・Meshlet へ）を、説明します。基本は [深度とカリング](../3d/depth-culling.md) にあります。

!!! tip "ポイント"
    - <strong>カリングの目的</strong>：<strong>描画命令・頂点・ピクセルの無駄をなくす</strong>。早い段階で除外するほど、効果が大きい。
    - 視錐台カリング：カメラの視界の外を除外。最も基本。
    - オクルージョン カリング：ほかの物に隠れた物を除外。効果が大きいが実装が難しい。
    - 距離・小物カリング、LOD：遠い・小さい物を除外・簡略化。
    - CPU でのカリングの限界：物体数が増えると判断自体が、CPU の負担。→ 階層構造・GPU Driven・Meshlet。
    - カリングの単位（物体・クラスター・三角形）を、細かくするほど、無駄が減る（が、判断の数は増える）。

!!! info "このページを読む前に"
    - [描画最適化](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [何が重いのか（ボトルネック）](bottlenecks.md)（CPU と GPU のどちらが遅いかの切り分け）

## カリングの種類

<svg class="fig illust" viewBox="0 0 800 300" role="img" aria-label="カリングの種類（真上から見た図）">
<text x="20" y="24" class="fig-title">真上から見た図：カメラから見えるもの（緑）と、見えないもの（赤）</text>
<circle cx="90" cy="170" r="7" fill="currentColor"/><text x="70" y="196" style="font-size:12px">カメラ</text>
<polygon points="90,170 420,50 420,290" fill="rgba(76,139,245,0.1)" stroke="currentColor" stroke-width="2"/>
<rect x="190" y="150" width="30" height="30" fill="rgba(46,160,67,0.5)" stroke="currentColor"/><text x="186" y="198" style="font-size:11px">描く</text>
<rect x="330" y="120" width="30" height="30" fill="rgba(229,72,77,0.5)" stroke="currentColor"/><text x="318" y="168" style="font-size:11px">壁の裏（隠れる）</text>
<rect x="300" y="60" width="16" height="190" fill="rgba(150,150,150,0.5)" stroke="currentColor" stroke-width="2"/><text x="288" y="52" style="font-size:11px">大きな壁</text>
<rect x="180" y="50" width="30" height="30" fill="rgba(229,72,77,0.5)" stroke="currentColor"/><text x="150" y="44" style="font-size:11px">視錐台の外</text>
<rect x="190" y="250" width="30" height="30" fill="rgba(229,72,77,0.5)" stroke="currentColor"/><text x="150" y="296" style="font-size:11px">視錐台の外</text>
<rect x="470" y="130" width="30" height="30" fill="rgba(229,72,77,0.5)" stroke="currentColor"/><text x="440" y="178" style="font-size:11px">遠すぎる</text>
<text x="560" y="80" style="font-weight:700">視錐台カリング</text><text x="560" y="100" style="font-size:12px">視界の外を、除外</text>
<text x="560" y="140" style="font-weight:700">オクルージョン カリング</text><text x="560" y="160" style="font-size:12px">壁の裏に、隠れた物を除外</text>
<text x="560" y="200" style="font-weight:700">距離カリング</text><text x="560" y="220" style="font-size:12px">遠すぎ・小さすぎを、除外</text>
</svg>

| カリング | 何を除外するか | どこで効くか |
| --- | --- | --- |
| **視錐台カリング** | 画面の外（カメラの後ろ・左右・上下） | ドロー コール・頂点 |
| オクルージョン カリング | ほかの物に隠れた物 | ドロー コール・頂点・ピクセル |
| 距離カリング | 遠すぎる物 | 同上 |
| 小物（スモール オブジェクト）カリング | 画面で数ピクセル以下の物 | 同上 |
| バックフェイス カリング | 裏を向いた三角形 | ピクセル（約半分） |
| LOD | 遠い物を簡易なモデルに | 頂点・ピクセル |

## 視錐台カリング

**カメラの視界（視錐台）の外**の物体を描画しない。物体の境界（球・箱）が、視錐台と交わるかで判定します（[深度とカリング](../3d/depth-culling.md)）。

| 点 | 説明 |
| --- | --- |
| 効果 | 振り向いたとき、背後の物体は描かれない。視界が狭い（FOV が小さい）ほど、効く |
| 判定の速さ | 球は速い。箱（AABB）は、正確 |
| CPU の負担 | 物体 1 つずつ、6 つの平面と判定（数万個で重い） |

### 階層構造で速くする

物体を、1 つずつ判定するのは、遅いです。空間を階層（木）にして、「木の枝全体が外」なら、中の物をまとめて除外します。

| 構造 | 説明 |
| --- | --- |
| 八分木（Octree）・BVH | 空間を再帰的に分割。親が外なら、子は判定しない |
| グリッド | セルごとに物体を持つ。セル単位で判定 |
| 効果 | 判定の回数が、O(n) から O(log n) に（[空間分割](../optimize/algorithms.md)） |

<!-- fig:frustum-culling-sweep:begin -->

<svg class="fig illust motion" data-fig="frustum-culling-sweep" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-frustum-culling-sweep" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">視錐台カリング:カメラが回ると、視野に入った物だけ描く</text>
<rect x="40" y="50" width="700" height="330" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<polygon points="390,340 235.13,118.83 283.06,92.08 335.4,75.58 390.0,70.0 444.6,75.58 496.94,92.08 544.87,118.83" fill="#2563eb" fill-opacity="0.15" stroke="#2563eb" stroke-width="2"><animate attributeName="points" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="390,340 235.13,118.83 283.06,92.08 335.4,75.58 390.0,70.0 444.6,75.58 496.94,92.08 544.87,118.83;390,340 265.97,100.17 317.03,80.05 371.11,70.66 425.96,72.41 479.33,85.21 529.01,108.54 572.95,141.43;390,340 298.36,86.03 351.61,72.74 406.45,70.5 460.61,79.4 511.85,99.06 558.05,128.68 597.32,167.03;390,340 330.97,76.53 385.46,70.04 440.15,74.7 492.76,90.32 541.13,116.26 583.25,151.44 617.39,194.41;390,340 362.46,71.41 417.34,71.39 471.1,82.47 521.5,104.19 566.47,135.65 604.14,175.56 632.97,222.26;390,340 391.66,70.01 446.23,75.92 498.47,92.75 546.23,119.79 587.53,155.93 620.67,199.68 644.28,249.22;390,340 417.63,71.42 471.37,82.55 521.75,104.33 566.68,135.84 604.32,175.78 633.1,222.51 651.83,274.1;390,340 439.65,74.6 492.3,90.13 540.71,115.98 582.9,151.08 617.12,193.99 641.95,242.93 656.37,295.89;390,340 457.3,78.52 508.79,97.53 555.36,126.56 595.11,164.41 626.38,209.52 647.88,260.01 658.73,313.81;390,340 470.33,82.23 520.79,103.8 565.86,135.12 603.65,174.92 632.62,221.53 651.57,273.04 659.7,327.32;390,340 478.64,84.96 528.38,108.16 572.4,140.93 608.89,181.93 636.33,229.45 653.6,281.55 659.97,336.06;390,340 482.2,86.23 531.61,110.12 575.17,143.5 611.08,185.01 637.86,232.91 654.39,285.25 660.0,339.84;390,340 481.01,85.8 530.53,109.46 574.25,142.64 610.35,183.97 637.35,231.76 654.13,284.01 660.0,338.58;390,340 475.07,83.75 525.13,106.25 569.61,138.41 606.67,178.89 634.77,226.03 652.76,277.88 659.89,332.3;390,340 464.4,80.45 515.35,100.86 561.12,131.15 599.81,170.07 629.84,216.0 649.96,267.07 659.34,321.14;390,340 449.04,76.53 501.1,93.92 548.57,121.47 589.48,158.05 622.16,202.15 645.24,251.94 657.77,305.37;390,340 429.17,72.86 482.38,86.29 531.77,110.22 575.31,143.63 611.19,185.16 637.93,233.09 654.43,285.43;390,340 405.1,70.42 459.3,79.05 510.64,98.45 556.99,127.84 596.45,165.99 627.37,211.33 648.48,261.99;390,340 377.41,70.29 432.21,73.32 485.27,87.37 534.39,111.85 577.54,145.76 612.94,187.7 639.14,235.93;390,340 346.93,73.46 401.72,70.25 456.02,78.2 507.6,96.96 554.32,125.76 594.25,163.41 625.74,208.36;390,340 314.72,80.71 368.71,70.84 423.58,72.1 477.06,84.42 526.95,107.31 571.17,139.81 607.91,180.58;390,340 282.06,92.52 334.33,75.8 388.91,70.0 443.53,75.36 495.94,91.65 543.97,118.2 585.64,153.92;390,340 250.28,108.96 299.89,85.48 353.22,72.52 408.07,70.61 462.17,79.82 513.29,99.79 559.32,129.69;390,340 220.68,129.69 266.71,99.79 317.83,79.82 371.93,70.61 426.78,72.52 480.11,85.48 529.72,108.96;390,340 194.36,153.92 236.03,118.2 284.06,91.65 336.47,75.36 391.09,70.0 445.67,75.8 497.94,92.52;390,340 172.09,180.58 208.83,139.81 253.05,107.31 302.94,84.42 356.42,72.1 411.29,70.84 465.28,80.71;390,340 154.26,208.36 185.75,163.41 225.68,125.76 272.4,96.96 323.98,78.2 378.28,70.25 433.07,73.46;390,340 140.86,235.93 167.06,187.7 202.46,145.76 245.61,111.85 294.73,87.37 347.79,73.32 402.59,70.29;390,340 131.52,261.99 152.63,211.33 183.55,165.99 223.01,127.84 269.36,98.45 320.7,79.05 374.9,70.42;390,340 125.57,285.43 142.07,233.09 168.81,185.16 204.69,143.63 248.23,110.22 297.62,86.29 350.83,72.86;390,340 122.23,305.37 134.76,251.94 157.84,202.15 190.52,158.05 231.43,121.47 278.9,93.92 330.96,76.53;390,340 120.66,321.14 130.04,267.07 150.16,216.0 180.19,170.07 218.88,131.15 264.65,100.86 315.6,80.45;390,340 120.11,332.3 127.24,277.88 145.23,226.03 173.33,178.89 210.39,138.41 254.87,106.25 304.93,83.75;390,340 120.0,338.58 125.87,284.01 142.65,231.76 169.65,183.97 205.75,142.64 249.47,109.46 298.99,85.8;390,340 120.0,339.84 125.61,285.25 142.14,232.91 168.92,185.01 204.83,143.5 248.39,110.12 297.8,86.23;390,340 120.03,336.06 126.4,281.55 143.67,229.45 171.11,181.93 207.6,140.93 251.62,108.16 301.36,84.96;390,340 120.3,327.32 128.43,273.04 147.38,221.53 176.35,174.92 214.14,135.12 259.21,103.8 309.67,82.23;390,340 121.27,313.81 132.12,260.01 153.62,209.52 184.89,164.41 224.64,126.56 271.21,97.53 322.7,78.52;390,340 123.63,295.89 138.05,242.93 162.88,193.99 197.1,151.08 239.29,115.98 287.7,90.13 340.35,74.6;390,340 128.17,274.1 146.9,222.51 175.68,175.78 213.32,135.84 258.25,104.33 308.63,82.55 362.37,71.42;390,340 135.72,249.22 159.33,199.68 192.47,155.93 233.77,119.79 281.53,92.75 333.77,75.92 388.34,70.01;390,340 147.03,222.26 175.86,175.56 213.53,135.65 258.5,104.19 308.9,82.47 362.66,71.39 417.54,71.41;390,340 162.61,194.41 196.75,151.44 238.87,116.26 287.24,90.32 339.85,74.7 394.54,70.04 449.03,76.53;390,340 182.68,167.03 221.95,128.68 268.15,99.06 319.39,79.4 373.55,70.5 428.39,72.74 481.64,86.03;390,340 207.05,141.43 250.99,108.54 300.67,85.21 354.04,72.41 408.89,70.66 462.97,80.05 514.03,100.17;390,340 235.13,118.83 283.06,92.08 335.4,75.58 390.0,70.0 444.6,75.58 496.94,92.08 544.87,118.83"/></polygon>
<circle cx="233.71" cy="224.8" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1"/></circle>
<circle cx="447.52" cy="194.73" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043"/></circle>
<circle cx="238.47" cy="190.77" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1"/></circle>
<circle cx="512.92" cy="234.11" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1"/></circle>
<circle cx="391.6" cy="227.52" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043"/></circle>
<circle cx="255.51" cy="315.05" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1"/></circle>
<circle cx="409.47" cy="259.86" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043"/></circle>
<circle cx="471.77" cy="263.75" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1"/></circle>
<circle cx="337.29" cy="283.02" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1"/></circle>
<circle cx="589.64" cy="303.4" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1"/></circle>
<circle cx="546.64" cy="249.59" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1"/></circle>
<circle cx="265.46" cy="305.58" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1"/></circle>
<circle cx="389.38" cy="249.16" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043"/></circle>
<circle cx="519.88" cy="298.59" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1"/></circle>
<circle cx="211.62" cy="216.16" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1"/></circle>
<circle cx="184.69" cy="221.56" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1"/></circle>
<circle cx="367.9" cy="172.09" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043"/></circle>
<circle cx="323.22" cy="197.64" r="10" fill="#cbd5e1" stroke="#1f2937" stroke-width="1.5"><animate attributeName="fill" dur="9s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0222;0.0444;0.0667;0.0889;0.1111;0.1333;0.1556;0.1778;0.2000;0.2222;0.2444;0.2667;0.2889;0.3111;0.3333;0.3556;0.3778;0.4000;0.4222;0.4444;0.4667;0.4889;0.5111;0.5333;0.5556;0.5778;0.6000;0.6222;0.6444;0.6667;0.6889;0.7111;0.7333;0.7556;0.7778;0.8000;0.8222;0.8444;0.8667;0.8889;0.9111;0.9333;0.9556;0.9778;1.0000" values="#cbd5e1;#2ea043;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#cbd5e1;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043;#2ea043"/></circle>
<circle cx="390" cy="340" r="9" fill="#e5484d" stroke="#ffffff" stroke-width="2"/>
<text x="372" y="368" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">カメラ</text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:6 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.0218;0.0222;1.0000" values="1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.0218;0.0222;0.0440;0.0444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.0440;0.0444;0.0662;0.0667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.0662;0.0667;0.0884;0.0889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.0884;0.0889;0.1107;0.1111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.1107;0.1111;0.1329;0.1333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.1329;0.1333;0.1551;0.1556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.1551;0.1556;0.1773;0.1778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.1773;0.1778;0.1996;0.2000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.1996;0.2000;0.2218;0.2222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.2218;0.2222;0.2440;0.2444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.2440;0.2444;0.2662;0.2667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.2662;0.2667;0.2884;0.2889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.2884;0.2889;0.3107;0.3111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.3107;0.3111;0.3329;0.3333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.3329;0.3333;0.3551;0.3556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.3551;0.3556;0.3773;0.3778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.3773;0.3778;0.3996;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.3996;0.4000;0.4218;0.4222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.4218;0.4222;0.4440;0.4444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.4440;0.4444;0.4662;0.4667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.4662;0.4667;0.4884;0.4889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:6 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.4884;0.4889;0.5107;0.5111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.5107;0.5111;0.5329;0.5333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.5329;0.5333;0.5551;0.5556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:9 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.5551;0.5556;0.5773;0.5778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:10 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.5773;0.5778;0.5996;0.6000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:9 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.5996;0.6000;0.6218;0.6222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:10 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.6218;0.6222;0.6440;0.6444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:9 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.6440;0.6444;0.6662;0.6667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.6662;0.6667;0.6884;0.6889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.6884;0.6889;0.7107;0.7111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.7107;0.7111;0.7329;0.7333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.7329;0.7333;0.7551;0.7556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.7551;0.7556;0.7773;0.7778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.7773;0.7778;0.7996;0.8000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.7996;0.8000;0.8218;0.8222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.8218;0.8222;0.8440;0.8444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:9 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.8440;0.8444;0.8662;0.8667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:10 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.8662;0.8667;0.8884;0.8889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:10 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.8884;0.8889;0.9107;0.9111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:9 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.9107;0.9111;0.9329;0.9333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:9 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.9329;0.9333;0.9551;0.9556;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:8 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.9551;0.9556;0.9773;0.9778;1.0000" values="0;0;1;1;0;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:7 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.9773;0.9778;0.9996;1.0000" values="0;0;1;1;0"/></text>
<text x="56" y="76" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">描く物:6 / 18<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;0.9996;1.0000;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="404" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">緑 = 視野に入っている（描く）、灰色 = 外（描かない）。外の物は、頂点シェーダーにも回らない。<animate attributeName="opacity" dur="9s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
</svg>

<!-- fig:frustum-culling-sweep:end -->

## オクルージョン カリング

**壁・建物・地形の裏に隠れた物**を除外します。視錐台カリングより、効果が大きい（都市・室内）が、実装が難しいです。

### 手法

| 手法 | 仕組み | 長所 | 短所 |
| --- | --- | --- | --- |
| 事前計算（PVS） | 「この場所から見える物」を、あらかじめ計算（ベイク） | 実行時がほぼゼロ | 動くものに使えない・ビルドが重い |
| ソフトウェア ラスタライザ | CPU で低解像度の深度バッファを描き、物体の境界が隠れるか判定 | GPU を使わない・同期待ちなし | CPU の負担 |
| GPU オクルージョン クエリ | 物体の境界を描いて、1 ピクセルでも通れば、見えると判定 | GPU の深度を使える | 結果が遅れて届く（数フレーム） |
| Hi-Z（階層的な深度） | 前フレームの深度から、階層（ミップ）を作り、GPU で物体が隠れるか判定 | GPU で並列・高速 | 前フレームの情報（動きに遅れる）（[Hi-Z](hiz.md)） |

### 時間の遅れの問題

GPU クエリや Hi-Z は、前のフレームの深度を使うことが多く、カメラが急に動くと、「見えるはずの物がまだ見えない」（ポップイン）ことが起きます。対策：保守的に（少し、多めに描く）、2 パス（前フレームで見えていた物を、先に描き、その深度で残りを判定）にします（[GPU Driven](gpu-driven.md)）。

## 距離カリング・小物カリング

| カリング | 説明 |
| --- | --- |
| **距離カリング** | ある距離より遠い物は、描かない（フォグで隠す） |
| 小物カリング | 画面上の大きさが数ピクセル以下なら、描かない（見た目にほぼ影響しない） |

物体の「画面上の大きさ」は、境界球の半径 ÷ 距離で、簡単に求められます。

## LOD（Level of Detail）

**遠い物を頂点の少ない、簡易なモデルに切り替える**。

| 種類 | 説明 |
| --- | --- |
| 離散 LOD | LOD0（詳細）・LOD1・LOD2 ... を距離で切り替え |
| インポスター（ビルボード） | 遠い物を画像 1 枚に（木・建物） |
| 連続 LOD・クラスター LOD | 三角形の塊（Meshlet）単位で滑らかに詳細度を変える（[Mesh Shader](mesh-shaders.md)） |

LOD の切り替わりが、目立つ（ポップ）ときはディザリング（ディザ フェード）で、混ぜます。

## バックフェイス カリング・そのほか

| カリング | 説明 |
| --- | --- |
| **バックフェイス** | 裏向きの三角形をラスタライズ前に除外（ハードウェアの機能。`CullMode = BACK`） |
| ポータル・セル | 部屋（セル）と、ドア（ポータル）で、見える部屋だけを描く（室内ゲーム） |
| 影のカリング | 影を落とさない物・影が見えない物を影マップの描画から、除外 |

## カリングの単位を、細かくする

カリングは**どの単位で判定するか**で効果と判定のコストが変わります。

<svg class="fig illust" viewBox="0 0 800 240" role="img" aria-label="カリングの単位の、細かさ">
<defs><marker id="cu1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">単位を細かくするほど、無駄は減るが、判定の数は、増える</text>
<rect x="20" y="50" width="170" height="90" rx="10" fill="rgba(229,72,77,0.2)" stroke="currentColor" stroke-width="3"/><text x="105" y="82" text-anchor="middle" style="font-weight:700">物体ごと</text><text x="105" y="104" text-anchor="middle" style="font-size:12px">（CPU で判定）</text><text x="105" y="122" text-anchor="middle" style="font-size:12px">一部が見えれば、全部描く</text>
<line x1="196" y1="95" x2="246" y2="95" stroke="currentColor" stroke-width="3" marker-end="url(#cu1)"/>
<rect x="254" y="50" width="170" height="90" rx="10" fill="rgba(229,170,40,0.25)" stroke="currentColor" stroke-width="3"/><text x="339" y="82" text-anchor="middle" style="font-weight:700">サブメッシュごと</text><text x="339" y="104" text-anchor="middle" style="font-size:12px">（GPU Driven）</text><text x="339" y="122" text-anchor="middle" style="font-size:12px">物体の一部を、除外</text>
<line x1="430" y1="95" x2="480" y2="95" stroke="currentColor" stroke-width="3" marker-end="url(#cu1)"/>
<rect x="488" y="50" width="170" height="90" rx="10" fill="rgba(76,139,245,0.25)" stroke="currentColor" stroke-width="3"/><text x="573" y="82" text-anchor="middle" style="font-weight:700">Meshlet ごと</text><text x="573" y="104" text-anchor="middle" style="font-size:12px">（64 頂点ほどの塊）</text><text x="573" y="122" text-anchor="middle" style="font-size:12px">細かく除外</text>
<line x1="664" y1="95" x2="704" y2="95" stroke="currentColor" stroke-width="3" marker-end="url(#cu1)"/>
<rect x="712" y="50" width="78" height="90" rx="10" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="3"/><text x="751" y="86" text-anchor="middle" style="font-weight:700">三角形</text><text x="751" y="108" text-anchor="middle" style="font-size:11px">最も細かい</text>
<text x="20" y="190" style="font-size:12px">粗い（物体）：判定は少ない／無駄は多い　→　細かい（三角形）：無駄は少ない／判定は多い（GPU で並列にやる）</text>
</svg>

| 単位 | 説明 |
| --- | --- |
| 物体（インスタンス） | CPU で判定。大きな物体は一部だけ見えても全体を描く |
| サブメッシュ | 物体を分割（建物の部屋ごと）。無駄が減る |
| Meshlet（クラスター） | 64 頂点・124 三角形ほどの塊。GPU が塊ごとにカリング（[Mesh Shader](mesh-shaders.md)） |
| 三角形 | 最も細かい。GPU のフィクスト ファンクションが、行う（バックフェイスなど） |

物体数が多く・形が複雑になるほど、判定を、CPU から GPU へ、単位を細かく——この流れが次の GPU Driven・Meshletです。

## 段階のまとめ

| 段階 | 手法 | カリングの場所 | 単位 |
| --- | --- | --- | --- |
| **1** | 視錐台カリング（CPU） | CPU | 物体 |
| 2 | 階層構造（Octree・BVH） | CPU | 物体 |
| 3 | オクルージョン（Hi-Z・ソフトウェア） | CPU / GPU | 物体 |
| 4 | GPU Driven（コンピュートでカリング） | GPU | 物体・サブメッシュ |
| 5 | Meshlet カリング（Mesh Shader） | GPU | Meshlet |

## よくあるミス

??? failure "境界ボックスが、大きすぎて、カリングが効かない"
    **物体にぴったりの境界**にします（回転で広がる AABB に注意）。

??? failure "オクルージョンで、見えるはずの物が消える"
    前フレームの情報の遅れです。保守的な判定・2 パスにします。

??? failure "カリングの判定が、重すぎて、CPU が詰まる"
    階層構造にする、GPU に任せる。

??? failure "LOD の切り替わりが、目立つ"
    ディザ フェード・切り替え距離のヒステリシス。

??? failure "影の描画で、カリングしていない"
    影を落とす物・見える範囲で別にカリングします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] カリング ＝ 見えないものを、描かない。早い段階で除外するほど、効果が大きい
    - [x] 種類：視錐台・オクルージョン・距離・小物・バックフェイス・LOD
    - [x] 視錐台カリングは、基本。階層構造（Octree・BVH）で、速くする
    - [x] オクルージョンは、効果大・難しい。Hi-Z が主流。前フレームの遅れに注意
    - [x] 単位を細かく（物体 → サブメッシュ → Meshlet）。判定を、CPU から GPU へ

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [ドロー コールとバッチ](draw-calls.md)
- [GPU Driven Rendering](gpu-driven.md)
- [Hi-Z とスクリーン空間トレース](hiz.md)
- [深度とカリング](../3d/depth-culling.md)
- [空間分割（アルゴリズム）](../optimize/algorithms.md)
