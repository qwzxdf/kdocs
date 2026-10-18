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

<svg class="fig illust motion" data-fig="lod-cracks" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-lod-cracks" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">継ぎ目:LOD が違うと、境界で頂点が合わず、隙間ができる</text>
<path d="M70,210 L110,190 L150,215 L190,195 L230,200 L270,185 L310,180 L310,180 L350,205 L390,160" fill="none" stroke="#2563eb" stroke-width="3.5"><animate attributeName="d" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3478;0.5217;1.0000" values="M70,210 L110,190 L150,215 L190,195 L230,200 L270,185 L310,180 L310,180 L350,205 L390,160;M70,210 L110,190 L150,215 L190,195 L230,200 L270,185 L310,180 L310,180 L350,205 L390,160;M70,210 L110,190 L150,215 L190,195 L230,200 L270,185 L310,180 L310,180 L350,170 L390,160;M70,210 L110,190 L150,215 L190,195 L230,200 L270,185 L310,180 L310,180 L350,170 L390,160"/></path>
<path d="M390,160 L550,150 L720,185" fill="none" stroke="#2ea043" stroke-width="3.5"/>
<line x1="390" y1="100" x2="390" y2="350" stroke="#e2e8f0" stroke-width="2" stroke-dasharray="4 4"/>
<text x="200" y="100" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#2563eb">細かい LOD</text>
<text x="560" y="100" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#2ea043">粗い LOD</text>
<line x1="310" y1="180" x2="390" y2="160" stroke="#2ea043" stroke-width="2.5" stroke-dasharray="5 4"/>
<circle cx="350" cy="205" r="8" fill="#e5484d" stroke="#ffffff" stroke-width="2"><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3478;0.5217;1.0000" values="205;205;170;170"/></circle>
<line x1="350" y1="205" x2="350" y2="170" stroke="#e5484d" stroke-width="3" opacity="1"><animate attributeName="y1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3478;0.5217;1.0000" values="205;205;170;170"/><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5217;0.5391;1.0000" values="1;1;0;0"/></line>
<text x="360" y="250" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">隙間（背景が見える）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000" values="1;1;0;0"/></text>
<text x="40" y="300" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">赤い頂点は、細かい側にだけある。粗い側の辺（緑の点線）から、ずれている → 隙間<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3475;0.3478;1.0000" values="1;1;0;0"/></text>
<text x="40" y="300" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">対策 1:赤い頂点を、粗い辺の上へ動かす<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3475;0.3478;0.5214;0.5217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="300" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">隙間が消えた（頂点が辺の上にあるので、ぴったり合う）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="340" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">対策 2:境界にスカート（垂れ幕）を付けて、隙間を隠す方法もある。</text>
</svg>

<!-- fig:lod-cracks:end -->

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

- [Terrain LOD](index.md)
- [Geomorphing](morphing.md)
