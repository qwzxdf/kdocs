---
title: Chunking
tags:
  - 描画
---

# Chunking

<strong>大きな地形は 1 枚のメッシュにせず、チャンク（区画）に分けます</strong>。見える区画だけを描き遠い区画は粗くすることで、効率よく描けます。このページではチャンク分割の考え方を説明します。

!!! tip "ポイント"
    - 区画ごとに描画・カリングできる。
    - ストリーミング（必要な区画だけ読み込み）ができる。
    - 境界の継ぎ目に注意。
    - 区画の大きさは 64〜256 頂点が目安。

!!! info "このページを読む前に"
    - [Heightmaps and Meshes](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## チャンクに分割する
<strong>広大な地形を 1 枚のメッシュで描く</strong>と、画面外も全部描いてしまいます。チャンク（タイル）に分けて見える所だけ描きます。

| 項目 | 内容 |
| --- | --- |
| チャンクのサイズ | 32〜128 マス四方（頂点が 65×65・129×129 など） |
| 視錐台カリング | チャンクごとに AABB を持ち、視錐台の外を描かない |
| AABB の高さ | チャンク内の最小・最大の高さを事前に計算して持つ |
| メッシュの共有 | 全チャンクで同じ格子メッシュを使い、位置と高さマップの範囲だけを渡す（インスタンシング） |
| ストリーミング | カメラ周りのチャンクだけ、高さマップを読み込む |

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

チャンクごとに LOD を変えると、遠くのチャンクを粗くして、三角形の数を大きく減らせます（[LOD](../lod/index.md)）。

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

## チャンクの大きさをどう決めるか

チャンクは <strong>小さすぎても大きすぎても、困ります</strong>。

| 大きさ | 利点 | 欠点 |
| --- | --- | --- |
| 小さい（17×17 頂点など） | カリングが細かい。見えない部分を無駄に描かない | チャンクの数が、爆発する。ドローコールと CPU のカリングの仕事が増える |
| 大きい（513×513 頂点など） | チャンクの数が、少ない | 画面に少しだけ入っている、巨大なチャンクを丸ごと描く。LOD の細かさが粗い |
| 中くらい（65×65〜129×129） | 両方の、ちょうど中間 | — |

目安は 1 つのチャンクが画面上で、数百〜数千三角形程度になる大きさです。それより小さいチャンクを大量に、個別のドローコールにするのは、割に合いません。

### 数の見積もり

世界を 16 km × 16 km、チャンクを 64 m 四方にすると

```text
チャンクの総数 = (16000 / 64)² = 250² = 62,500 個
```

カメラの周りの視錐台に入るのは、数百〜1,000 個ほどです。62,500 個を毎フレーム、全部調べるのは無駄です。四分木などで 大きい範囲をまとめて捨てるようにします（[CDLOD](../lod/cdlod.md) の四分木）。

## チャンクが持つもの

```cpp
struct TerrainChunk {
  int grid_x, grid_z;            // チャンクの格子上の位置
  float min_height, max_height;  // 高さの最小・最大（AABB のため）
  BoundingBox bounds;            // ワールド座標の AABB
  int lod_level;                 // いまの LOD
  bool loaded;                   // 高さデータが、メモリに、あるか
};

BoundingBox ChunkBounds(const TerrainChunk& c, float chunk_size) {
  const float x0 = c.grid_x * chunk_size, z0 = c.grid_z * chunk_size;
  return {{x0, c.min_height, z0}, {x0 + chunk_size, c.max_height, z0 + chunk_size}};
}
```

<strong>高さの最小・最大はチャンクごとに、事前に求めておく</strong>必要があります。山の中のチャンクと谷のチャンクでは、AABB の縦の長さがまるで違います。最小と最大が不正確だと カリングで、見えるはずの山が消えることがあります。

## 視錐台カリング

```cpp
// AABB と 6 枚の平面の、判定（p 頂点テスト）。
bool Visible(const Frustum& f, const BoundingBox& box) {
  for (const Plane& pl : f.planes) {
    // 平面の法線の向きに、最も進んだ頂点（positive vertex）を選ぶ
    const float3 p = {pl.n.x >= 0 ? box.max.x : box.min.x,
                      pl.n.y >= 0 ? box.max.y : box.min.y,
                      pl.n.z >= 0 ? box.max.z : box.min.z};
    if (Dot(pl.n, p) + pl.d < 0) return false;   // 完全に外側
  }
  return true;
}

void CullChunks(const std::vector<TerrainChunk>& all, const Frustum& f,
                std::vector<const TerrainChunk*>& visible) {
  for (const TerrainChunk& c : all) {
    if (c.loaded && Visible(f, c.bounds)) visible.push_back(&c);
  }
}
```

p 頂点テストは AABB の 8 頂点を調べず、<strong>平面ごとに 1 つの頂点だけ</strong>で、判定できます。視錐台の少し外側にはみ出た AABB が、「見える」と判定されることはありますが、描いても画面に出ないだけで問題はありません。

## 描画：インスタンスでまとめる

見えるチャンクは <strong>同じ格子メッシュ</strong>を、位置だけ変えて描きます。

| 方法 | ドローコール | 特徴 |
| --- | --- | --- |
| 1 チャンク = 1 ドローコール | チャンクの数 | 簡単。数百個なら問題ない |
| インスタンシング | 1 回（または、LOD ごと） | チャンクの位置などを、インスタンス バッファへ。CPU の仕事が最小 |

```cpp
// 見えるチャンクの情報を、インスタンス バッファに詰めて、1 回で描く。
struct ChunkInstance { float2 origin; float size; float level; float2 uv_origin; float2 uv_size; };

std::vector<ChunkInstance> instances;
for (const TerrainChunk* c : visible) {
  instances.push_back({ChunkOrigin(*c), chunk_size, float(c->lod_level),
                       ChunkUvOrigin(*c), ChunkUvSize(*c)});
}
UploadToInstanceBuffer(context, instance_buffer, instances);
context->DrawIndexedInstanced(index_count, UINT(instances.size()), 0, 0, 0);
```

LOD ごとに頂点数の違う格子を、使うなら LOD ごとに 1 回ずつ描きます。

## 高さデータの持ち方

チャンクごとに高さをどこへ置くか。2 つの方法があります。

| 方法 | 内容 | 特徴 |
| --- | --- | --- |
| 全体で 1 枚の巨大なテクスチャ | 世界全体の高さマップを、1 枚に持つ | 単純。巨大な地形ではメモリに収まらない |
| チャンクごとに別のテクスチャ | チャンクごとに、小さな高さマップを持つ | ストリーミングが簡単。ドローコールごとにテクスチャを切り替える必要がある |
| テクスチャ配列 | 同じ大きさの、チャンクの高さを配列のスライスにする | 1 回のドローコールで、全チャンクを描ける。スライスの番号をインスタンスに持たせる |
| アトラス（大きな 1 枚に、並べる） | カメラの周りの、チャンクだけを窓として持つ | クリップマップと、似た発想（[Geometry Clipmaps](../lod/clipmap.md)） |

<strong>テクスチャ配列</strong>はインスタンシングと、相性が良くよく使われる方法です。

```hlsl
Texture2DArray<float> g_height_array : register(t0);

struct VSInput {
  float2 grid : POSITION;
  float4 chunk : CHUNK;         // xy = 原点, z = 大きさ, w = スライス番号
};

float height = g_height_array.SampleLevel(g_linear_clamp, float3(uv, input.chunk.w), 0);
```

## ストリーミング

世界がメモリより大きいとき <strong>プレイヤーの周りの、チャンクだけをメモリに置く</strong>必要があります。

| 範囲 | 状態 |
| --- | --- |
| 描画範囲 | 高さデータが、メモリに読み込み済み |
| 先読み範囲（描画範囲の少し外） | これから使うので、非同期で読み込み中 |
| それ以外 | メモリから、解放 |

```cpp
// プレイヤーの周りの、チャンクの範囲を、計算して、読み込み・解放する。
void UpdateStreaming(const float3& player, int load_radius, int unload_radius) {
  const int px = int(player.x / chunk_size), pz = int(player.z / chunk_size);
  for (TerrainChunk& c : chunks) {
    const int d = std::max(std::abs(c.grid_x - px), std::abs(c.grid_z - pz));
    if (d <= load_radius && !c.loaded && !c.loading) RequestLoadAsync(c);
    if (d > unload_radius && c.loaded) Unload(c);        // load より大きい半径で解放（ヒステリシス）
  }
}
```

読み込む半径より少し大きい半径で、解放する（ヒステリシス）と、境界の近くを行き来したときに、読み込みと解放が毎フレーム繰り返されません。

## チャンクの継ぎ目

| 継ぎ目の原因 | 対策 |
| --- | --- |
| 隣り合うチャンクの境界の高さが、違う | 境界の画素を両側のチャンクで、同じ値にする（共有する） |
| 隣り合うチャンクの LOD が違う | モーフィング、スカートなど（[Cracks and Seams](../lod/cracks.md)） |
| 高さマップの半画素のずれ | UV の範囲を、半画素分、内側へ寄せる |
| 法線が境界で不連続 | 隣のチャンクの、高さを読んで法線を計算する（または、法線マップを共有する） |

境界の画素は <strong>両方のチャンクに、同じ値を重複して保存</strong>します（`N×N` でなく、`(N+1)×(N+1)` 画素）。そうすると、隣のチャンクを読み込まなくても、境界が合います。

## よくあるミス

??? failure "区画の境目に、隙間が見える"
    <strong>境界の頂点の高さを揃える</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 区画に分けて、描画・読み込みを効率化

## 参考

- Ulrich, "Rendering Massive Terrains Using Chunked Level of Detail Control", SIGGRAPH 2002 Course Notes
- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps", Journal of Graphics, GPU, and Game Tools, Vol. 14, No. 4, 2009
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（地形、ビュー フラスタム カリング、法線、補間の章）
- Gribb, Hartmann, "Fast Extraction of Viewing Frustum Planes from the World-View-Projection Matrix", 2001（視錐台の平面を、行列から取り出す）

## 関連ページ

- [Heightmaps and Meshes](index.md)
- [LOD](../lod/index.md)
