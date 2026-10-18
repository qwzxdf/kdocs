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

<svg class="fig illust motion" data-fig="chunk-stream" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-chunk-stream" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">チャンクのストリーミング: カメラが動くと、近いチャンクを読み込み、遠いチャンクを捨てる。メモリは一定</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">20×8 のチャンクの世界。カメラの半径 2.5 チャンク以内を読み込む。カメラを右へ 8 チャンク動かして、読み込み・解放の数を数える</text>
<rect x="50.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="106.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="134.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="162.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="190.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="218.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="246.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="274.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="302.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="330.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="358.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="386.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="414.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="120.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="106.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="134.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="162.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="190.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="218.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="246.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="274.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="302.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="330.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="358.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="386.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="414.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="148.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957" values="#f1f5f9;#86efac;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="106.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="134.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="162.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="190.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="218.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="246.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="274.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="302.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="330.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="358.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="386.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e"/></rect>
<rect x="414.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="176.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957" values="#f1f5f9;#86efac;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="106.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="134.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="162.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="190.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="218.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="246.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="274.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="302.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="330.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="358.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="386.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e"/></rect>
<rect x="414.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="204.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957" values="#f1f5f9;#86efac;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="106.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="134.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="162.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="190.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="218.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="246.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="274.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="302.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="330.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="358.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="386.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e"/></rect>
<rect x="414.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="232.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957" values="#f1f5f9;#86efac;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="106.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="134.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="162.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0638;0.1021;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="190.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1574;0.1957;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="218.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2511;0.2894;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="246.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3447;0.3830;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="274.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4383;0.4766;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#fca5a5;#f1f5f9"/></rect>
<rect x="302.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5319;0.5702;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="330.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6255;0.6638;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="358.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7191;0.7574;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e;#22c55e;#22c55e"/></rect>
<rect x="386.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8128;0.8511" values="#f1f5f9;#86efac;#22c55e"/></rect>
<rect x="414.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="260.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="106.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="134.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="162.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="190.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="218.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="246.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="274.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="302.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="330.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="358.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="386.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="414.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="288.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="78.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="106.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="134.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="162.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="190.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="218.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="246.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="274.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="302.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="330.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="358.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="386.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="414.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="442.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="470.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="498.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="526.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="554.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="582.0" y="316.0" width="28.3" height="28.3" fill="#f1f5f9"/>
<rect x="50.0" y="120.0" width="560.0" height="224.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0.5"><line x1="78.0" y1="120.0" x2="78.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="106.0" y1="120.0" x2="106.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="134.0" y1="120.0" x2="134.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="162.0" y1="120.0" x2="162.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="190.0" y1="120.0" x2="190.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="218.0" y1="120.0" x2="218.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="246.0" y1="120.0" x2="246.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="274.0" y1="120.0" x2="274.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="302.0" y1="120.0" x2="302.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="330.0" y1="120.0" x2="330.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="358.0" y1="120.0" x2="358.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="386.0" y1="120.0" x2="386.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="414.0" y1="120.0" x2="414.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="442.0" y1="120.0" x2="442.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="470.0" y1="120.0" x2="470.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="498.0" y1="120.0" x2="498.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="526.0" y1="120.0" x2="526.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="554.0" y1="120.0" x2="554.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="582.0" y1="120.0" x2="582.0" y2="344.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="50.0" y1="148.0" x2="610.0" y2="148.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="50.0" y1="176.0" x2="610.0" y2="176.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="50.0" y1="204.0" x2="610.0" y2="204.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="50.0" y1="232.0" x2="610.0" y2="232.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="50.0" y1="260.0" x2="610.0" y2="260.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="50.0" y1="288.0" x2="610.0" y2="288.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="50.0" y1="316.0" x2="610.0" y2="316.0" stroke="#ffffff" stroke-width="0.5"/>
<rect x="50.0" y="120.0" width="560.0" height="224.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<circle cx="134.0" cy="232.0" r="9" fill="#1f2937"><animate attributeName="cx" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1064;0.1574;0.2000;0.2511;0.2936;0.3447;0.3872;0.4383;0.4809;0.5319;0.5745;0.6255;0.6681;0.7191;0.7617;0.8128;1.0000" values="134;134;162;162;190;190;218;218;246;246;274;274;302;302;330;330;358;358"/></circle>
<text x="40" y="398" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">読み込んだ数(累計):</text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.1573;0.1574;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">4<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1573;0.1574;0.2509;0.2511;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">8<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2509;0.2511;0.3445;0.3447;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">12<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3445;0.3447;0.4381;0.4383;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4381;0.4383;0.5317;0.5319;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">20<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5317;0.5319;0.6254;0.6255;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">24<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6254;0.6255;0.7190;0.7191;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">28<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7190;0.7191;0.8126;0.8128;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="402" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043" opacity="0">32<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8126;0.8128;1.0000" values="0;0;1;1"/></text>
<text x="40" y="430" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">捨てた数(累計):</text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.1573;0.1574;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1573;0.1574;0.2509;0.2511;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">8<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2509;0.2511;0.3445;0.3447;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">12<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3445;0.3447;0.4381;0.4383;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4381;0.4383;0.5317;0.5319;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">20<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5317;0.5319;0.6254;0.6255;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">24<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6254;0.6255;0.7190;0.7191;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">28<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7190;0.7191;0.8126;0.8128;1.0000" values="0;0;1;1;0;0"/></text>
<text x="230" y="434" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">32<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8126;0.8128;1.0000" values="0;0;1;1"/></text>
<text x="40" y="462" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">いま、メモリにあるチャンク:</text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.1573;0.1574;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1573;0.1574;0.2509;0.2511;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2509;0.2511;0.3445;0.3447;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3445;0.3447;0.4381;0.4383;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4381;0.4383;0.5317;0.5319;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5317;0.5319;0.6254;0.6255;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6254;0.6255;0.7190;0.7191;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7190;0.7191;0.8126;0.8128;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="466" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8126;0.8128;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8849;0.8851;1.0000" values="0;0;1;1"/><rect x="480" y="392" width="450" height="100" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="496" y="416" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">メモリのチャンクは 16〜16 個で、ほぼ一定</text>
<text x="496" y="439" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">1 歩あたり、新しく 4〜4、捨てる 4〜4</text>
<text x="496" y="461" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">世界が、どれだけ広くても、必要なメモリは、半径で決まる</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">広い世界を、全部は持てない<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">カメラの周りだけ持つ。動いた分だけ、読み込み・解放する<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.9062;0.9064;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">読み込みは、1 フレームに 1 つずつ、などに分けて、ガクつきを防ぐ<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.9062;0.9064;1.0000;1.0000" values="0;0;1;1;0"/></text>
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
