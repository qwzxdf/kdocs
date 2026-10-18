---
title: Chunking
tags:
  - 描画
---

# Chunking

**大きな地形は、1 枚のメッシュにせず、チャンク（区画）に分けます**。**見える区画だけを描き、遠い区画は粗くする**ことで、**効率よく描けます**。このページでは、**チャンク分割の考え方**を説明します。

!!! tip "ポイント"
    - **区画ごとに描画・カリング**できる。
    - **ストリーミング（必要な区画だけ読み込み）**ができる。
    - **境界の継ぎ目**に注意。
    - **区画の大きさは、64〜256 頂点**が**目安**。

## チャンクに分割する
**広大な地形を 1 枚のメッシュで描く**と、**画面外も全部描いてしまいます**。**チャンク（タイル）に分けて、見える所だけ描きます**。

| 項目 | 内容 |
| --- | --- |
| **チャンクのサイズ** | **32〜128 マス四方**（**頂点が 65×65・129×129** など） |
| **視錐台カリング** | **チャンクごとに AABB を持ち、視錐台の外を描かない** |
| **AABB の高さ** | **チャンク内の最小・最大の高さを事前に計算して持つ** |
| **メッシュの共有** | **全チャンクで同じ格子メッシュ**を使い、**位置と高さマップの範囲**だけを**渡す**（インスタンシング） |
| **ストリーミング** | **カメラ周りのチャンクだけ、高さマップを読み込む** |

```cpp
struct TerrainChunk {
  int grid_x;
  int grid_z;
  float min_height;
  float max_height;
  BoundingBox bounds;
  int lod_level;
};
```

**チャンクごとに LOD を変える**と、**遠くのチャンクを粗くして**、**三角形の数を大きく減らせます**（[LOD](../lod/index.md)）。

<!-- fig:chunk-stream:begin -->

<svg class="fig illust motion" data-fig="chunk-stream" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-chunk-stream" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">カメラが動くと、近いチャンクを読み込み、遠いチャンクを捨てる</text>
<rect x="80" y="80" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="80" y="80" width="58" height="58" fill="#6ede97" opacity="0"/>
<rect x="142" y="80" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="142" y="80" width="58" height="58" fill="#6ede97" opacity="0"/>
<rect x="204" y="80" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="204" y="80" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.1997;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="266" y="80" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="266" y="80" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;0.3256;0.3259;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="328" y="80" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="328" y="80" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;0.4516;0.4519;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="390" y="80" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="390" y="80" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4516;0.4519;0.5775;0.5778;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="452" y="80" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="452" y="80" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5775;0.5778;0.7034;0.7037;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="514" y="80" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="514" y="80" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7034;0.7037;1.0000" values="0;0;1;1"/></rect>
<rect x="576" y="80" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="576" y="80" width="58" height="58" fill="#6ede97" opacity="0"/>
<rect x="638" y="80" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="638" y="80" width="58" height="58" fill="#6ede97" opacity="0"/>
<rect x="80" y="142" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="80" y="142" width="58" height="58" fill="#6ede97" opacity="0"/>
<rect x="142" y="142" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="142" y="142" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.1997;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="204" y="142" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="204" y="142" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.3256;0.3259;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="266" y="142" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="266" y="142" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.4516;0.4519;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="328" y="142" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="328" y="142" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;0.5775;0.5778;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="390" y="142" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="390" y="142" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;0.7034;0.7037;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="452" y="142" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="452" y="142" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4516;0.4519;1.0000" values="0;0;1;1"/></rect>
<rect x="514" y="142" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="514" y="142" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5775;0.5778;1.0000" values="0;0;1;1"/></rect>
<rect x="576" y="142" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="576" y="142" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7034;0.7037;1.0000" values="0;0;1;1"/></rect>
<rect x="638" y="142" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="638" y="142" width="58" height="58" fill="#6ede97" opacity="0"/>
<rect x="80" y="204" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="80" y="204" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.1997;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="142" y="204" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="142" y="204" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.3256;0.3259;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="204" y="204" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="204" y="204" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.4516;0.4519;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="266" y="204" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="266" y="204" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.5775;0.5778;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="328" y="204" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="328" y="204" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.7034;0.7037;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="390" y="204" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="390" y="204" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;1.0000" values="0;0;1;1"/></rect>
<rect x="452" y="204" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="452" y="204" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;1.0000" values="0;0;1;1"/></rect>
<rect x="514" y="204" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="514" y="204" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4516;0.4519;1.0000" values="0;0;1;1"/></rect>
<rect x="576" y="204" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="576" y="204" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5775;0.5778;1.0000" values="0;0;1;1"/></rect>
<rect x="638" y="204" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="638" y="204" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7034;0.7037;1.0000" values="0;0;1;1"/></rect>
<rect x="80" y="266" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="80" y="266" width="58" height="58" fill="#6ede97" opacity="0"/>
<rect x="142" y="266" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="142" y="266" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.1997;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="204" y="266" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="204" y="266" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.3256;0.3259;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="266" y="266" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="266" y="266" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.4516;0.4519;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="328" y="266" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="328" y="266" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;0.5775;0.5778;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="390" y="266" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="390" y="266" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;0.7034;0.7037;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="452" y="266" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="452" y="266" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4516;0.4519;1.0000" values="0;0;1;1"/></rect>
<rect x="514" y="266" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="514" y="266" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5775;0.5778;1.0000" values="0;0;1;1"/></rect>
<rect x="576" y="266" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="576" y="266" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7034;0.7037;1.0000" values="0;0;1;1"/></rect>
<rect x="638" y="266" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="638" y="266" width="58" height="58" fill="#6ede97" opacity="0"/>
<rect x="80" y="328" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="80" y="328" width="58" height="58" fill="#6ede97" opacity="0"/>
<rect x="142" y="328" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="142" y="328" width="58" height="58" fill="#6ede97" opacity="0"/>
<rect x="204" y="328" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="204" y="328" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.1997;0.2000;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="266" y="328" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="266" y="328" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;0.3256;0.3259;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="328" y="328" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="328" y="328" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;0.4516;0.4519;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="390" y="328" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="390" y="328" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4516;0.4519;0.5775;0.5778;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="452" y="328" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="452" y="328" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5775;0.5778;0.7034;0.7037;1.0000" values="0;0;1;1;0;0"/></rect>
<rect x="514" y="328" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="514" y="328" width="58" height="58" fill="#6ede97" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7034;0.7037;1.0000" values="0;0;1;1"/></rect>
<rect x="576" y="328" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="576" y="328" width="58" height="58" fill="#6ede97" opacity="0"/>
<rect x="638" y="328" width="58" height="58" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
<rect x="638" y="328" width="58" height="58" fill="#6ede97" opacity="0"/>
<circle cx="233.0" cy="233.0" r="9" fill="#1f2937"><animate attributeName="cx" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1407;0.2000;0.2667;0.3259;0.3926;0.4519;0.5185;0.5778;0.6444;0.7037;1.0000" values="233;233;295;295;357;357;419;419;481;481;543;543"/></circle>
<text x="80" y="68" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">緑 = 読み込み済みのチャンク（カメラから一定の距離内）</text>
<text x="390" y="420" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">カメラの周りだけ、メモリに置く<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="390" y="420" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">右へ動く: 前方のチャンクを読み込み、後ろを捨てる<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.3701;0.3704;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="420" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ワールド全体の大きさに関係なく、メモリ量が一定<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3701;0.3704;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:chunk-stream:end -->

## よくあるミス

??? failure "区画の境目に、隙間が見える"
    **境界の頂点の高さを揃える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **区画に分けて、描画・読み込みを効率化**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Heightmaps and Meshes](index.md)
- [LOD](../lod/index.md)
