---
title: Heightmaps and Meshes
tags:
  - 描画
---

# Heightmaps and Meshes

**地形の基本は、「高さマップ」という白黒の画像で、各位置の高さを持つ**ことです。**これを格子状のメッシュに変換**して、**描画**します。このセクションでは、**高さマップ・格子メッシュ・法線・任意位置の高さ・チャンク分割・編集**を、**1 つずつ別のページ**で説明します。

## 高さマップ
**高さマップ**は**白黒の画像**です。**明るいほど高く、暗いほど低い**。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="高さマップと地形">
<text x="20" y="24" class="fig-title">高さマップ（左）と、それを持ち上げた地形の断面（右）</text>
<defs>
<linearGradient id="hmg" x1="0" x2="1"><stop offset="0" stop-color="#202020"/><stop offset="0.25" stop-color="#707070"/><stop offset="0.5" stop-color="#f0f0f0"/><stop offset="0.75" stop-color="#808080"/><stop offset="1" stop-color="#303030"/></linearGradient>
</defs>
<rect x="40" y="50" width="240" height="160" fill="url(#hmg)" stroke="currentColor" stroke-opacity="0.5"/>
<text x="160" y="228" text-anchor="middle" style="font-size:12px">明るい ＝ 高い</text>
<line x1="330" y1="200" x2="740" y2="200" stroke="currentColor" stroke-opacity="0.4"/>
<polyline fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="3" points="330,200 330,190 400,170 470,120 530,70 580,95 640,150 700,175 740,185 740,200"/>
<text x="540" y="62" text-anchor="middle" style="font-size:12px">山頂</text>
<line x1="280" y1="130" x2="330" y2="130" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="4 4"/>
</svg>

| 形式 | 内容 |
| --- | --- |
| <strong>8 ビット（256 段階）</strong> | **軽いが高さが段々になる**。**広い地形には粗い** |
| <strong>16 ビット（65536 段階）</strong> | **標準**。**`R16_UNORM`**。**高さの範囲を 0〜1 に正規化し、スケールで実際の高さに戻す** |
| **32 ビット浮動小数** | **精度は十分だが大きい**。**生成・編集時に使う** |
| **読み込み元** | <strong>画像（PNG16・RAW）・地形ツール（World Machine・Gaea）の出力・実測データ（DEM）</strong> |

**実際の高さ**は**マップの値にスケールを掛けて求めます**。

<div class="formula">高さ(x, z) = height_map(x / world_size, z / world_size) × height_scale + base_height</div>

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Grid Mesh](grid-mesh.md) | 頂点を並べて、高さを与える |
| [Terrain Normals](normals.md) | 高さの差分から求める |
| [Height at Arbitrary Positions](height-query.md) | 補間して高さを取る |
| [Chunking](chunks.md) | 大きな地形を分ける |
| [Editing Heightmaps](editing.md) | ブラシ・保存 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **高さマップを、格子メッシュに変換して描く**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps", Journal of Graphics, GPU, and Game Tools, Vol. 14, No. 4, 2009
- Ulrich, "Rendering Massive Terrains Using Chunked Level of Detail Control", SIGGRAPH 2002 Course Notes
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（地形、ビュー フラスタム カリング、法線、補間の章）
- Forsyth, "Linear-Speed Vertex Cache Optimisation", 2006（頂点キャッシュに合わせた、インデックスの並べ替え）

## 関連ページ

- [Terrain](../index.md)
- [LOD](../lod/index.md)
- [Terrain Generation](../generation/index.md)
