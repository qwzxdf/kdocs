---
title: Heightmaps and Meshes
tags:
  - 描画
---

# Heightmaps and Meshes

**地形の基本は、「高さマップ」という白黒の画像で、各位置の高さを持つ**ことです。**これを格子状のメッシュに変換**して、**描画**します。このセクションでは、**高さマップ・格子メッシュ・法線・任意位置の高さ・チャンク分割・編集**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **高さマップ ＝ 各位置の高さを入れた画像**。
    - **格子メッシュの頂点を、高さマップで持ち上げる**。
    - **法線は、高さの差分から求める**。
    - **大きな地形は、チャンクに分けて扱う**。

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

高さマップの形式です。8 ビット（256 段階）は軽いですが、高さが段々になるので、広い地形には粗すぎます。16 ビット（65536 段階）が標準で、`R16_UNORM` を使います。高さの範囲を 0〜1 に正規化し、スケールで実際の高さに戻します。32 ビット浮動小数は精度が十分ですが大きいので、生成や編集時に使います。読み込み元は、画像（PNG16・RAW）、地形ツール（World Machine・Gaea）の出力、実測データ（DEM）です。

**実際の高さ**は**マップの値にスケールを掛けて求めます**。

<div class="formula">高さ(x, z) = height_map(x / world_size, z / world_size) × height_scale + base_height</div>

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Grid Mesh](grid-mesh.md) | 頂点を並べて、高さを与える |
| [Terrain Normals](normals.md) | 高さの差分から求める |
| [任意位置の高さ](height-query.md) | 補間して高さを取る |
| [Chunking](chunks.md) | 大きな地形を分ける |
| [Editing Heightmaps](editing.md) | ブラシ・保存 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **高さマップを、格子メッシュに変換して描く**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain](../index.md)
- [LOD](../lod/index.md)
- [地形生成](../generation/index.md)
