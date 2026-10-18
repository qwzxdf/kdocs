---
title: Terrain LOD
tags:
  - 描画
---

# Terrain LOD

**地形は広く、全部を細かいメッシュで描くと重すぎます**。**近くは細かく、遠くは粗く**する**LOD（レベル オブ ディテール）**が、**必須**です。このセクションでは、**LOD が要る理由・CDLOD・モーフィング・継ぎ目・クリップマップ・テッセレーション・高さマップのミップ・選び方**を、**1 つずつ別のページ**で説明します。

## なぜ LOD が要るか
**透視投影では遠くの物は小さく見える**ので、**同じ大きさのマスでも遠くは画面上でとても小さい**です。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="距離とマスの大きさ">
<text x="20" y="24" class="fig-title">遠くのマスは、画面上で小さい：同じ細かさで描くと無駄</text>
<polygon points="60,200 740,200 740,60 60,120" fill="#2ea043" fill-opacity="0.15"/>
<g stroke="currentColor" stroke-opacity="0.5">
<line x1="60" y1="200" x2="60" y2="120"/><line x1="140" y1="200" x2="140" y2="128"/><line x1="220" y1="200" x2="220" y2="135"/><line x1="300" y1="200" x2="300" y2="141"/><line x1="380" y1="200" x2="380" y2="146"/><line x1="460" y1="200" x2="460" y2="150"/><line x1="540" y1="200" x2="540" y2="153"/><line x1="620" y1="200" x2="620" y2="156"/><line x1="700" y1="200" x2="700" y2="158"/>
</g>
<circle cx="40" cy="190" r="8" fill="#e5484d"/>
<text x="30" y="214" style="font-size:12px;fill:#e5484d">カメラ</text>
<text x="500" y="100" style="font-size:12px">遠く：マスが画面上で細く、数が多すぎる</text>
</svg>

LOD の目標は 3 つあります。画面上の誤差を、LOD を下げたことによる見た目のずれが数ピクセル以下にすること。三角形の大きさを、画面上でおおむね均一にすること（小さな三角形は GPU が不得意です）。総数の上限を決め、視点がどこでも三角形の数がほぼ一定になるようにすることです。

### なぜ LOD が必要なのか

地形を最高の細かさで全域に描くと、三角形が多すぎて描けません。たとえば 4 km 四方を 1 m 刻みで作ると、約 3200 万の三角形になります。ところが、遠くの地形は、画面上では 1 画素にも満たない大きさなので、細かく描く意味がありません。距離に応じて細かさを変えて、画面上でどの三角形もほぼ同じ大きさ（たとえば 2〜4 画素）になるようにすれば、総数は視点の周りの数万〜数十万に収まります。

LOD の設計で難しいのは、切り替えです。細かさが変わる境目で、メッシュの形が突然変わると「ポップ」が見え、隣り合う LOD の境目に隙間（クラック）ができます。この 2 つの問題に対して、モーフィングとクラック処理が必要になります。

## LOD の選び方の目安
| 状況 | 向く方式 |
| --- | --- |
| <strong>標準的なゲーム（数 km）</strong> | <strong>四分木（CDLOD）</strong>。**モーフィング付き** |
| **無限に近い地形・海** | **クリップマップ** |
| **既存のエンジンで簡単に** | **テッセレーション ＋ 距離係数** |
| **非常に大規模・密** | **メッシュ シェーダー ＋ GPU ドリブン**（[GPU Driven](../../../rendering/index.md)） |

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [CDLOD (Quadtree)](cdlod.md) | 距離で、四分木を分割 |
| [Geomorphing](morphing.md) | 切り替えを、なめらかに |
| [Cracks and Seams](cracks.md) | LOD の境目の隙間 |
| [Geometry Clipmaps](clipmap.md) | カメラ中心の同心の格子 |
| [Hardware Tessellation](tessellation.md) | ハードウェアで細分割 |
| [Heightmap LOD (Mips)](height-mip.md) | 遠くは粗い高さを読む |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **近くは細かく、遠くは粗く**
    - [x] **切り替えは、モーフィングでなめらかに**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain](../index.md)
- [Heightmaps and Meshes](../heightmap-mesh/index.md)
- [LOD とインポスター](../../../rendering/lod.md)
