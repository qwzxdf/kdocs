---
title: 継ぎ目（クラック）
tags:
  - 描画
---

# 継ぎ目（クラック）

**LOD の異なる区画が隣り合うと、境界で頂点が合わず、隙間（クラック）ができます**。**境界の頂点を調整する**ことで、**隙間を埋められます**。このページでは、**継ぎ目の原因と対策**を説明します。

!!! tip "ポイント"
    - **原因 ＝ 隣の区画の頂点が、粗い側にはない**。
    - **対策 1：粗い側に合わせて、細かい側の境界頂点を動かす**。
    - **対策 2：境界にスカート（垂れ幕）を付ける**。
    - **CDLOD は、モーフィングで自然に解決**する。

## 継ぎ目（クラック）
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

## よくあるミス

??? failure "LOD の境界に、背景が見える隙間が出る"
    **スカート**または**境界の頂点調整**を入れる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **境界の頂点を合わせるか、スカートで隠す**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [地形の LOD](index.md)
- [モーフィング](morphing.md)
