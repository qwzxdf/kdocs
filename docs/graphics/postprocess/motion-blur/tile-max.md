---
title: Tile Max Velocity
tags:
  - 描画
---

# Tile Max Velocity

<strong>画素ごとに長い距離を多数サンプル</strong>するのは重いうえ、速い物体の輪郭の外側（背景）の画素は自分の速度が 0 なので、尾が伸びません。そこで画面を小さなタイル（例：16×16 画素）に分け、各タイルの「最大の速度」を求め、周囲のタイルの最大速度も合わせた「近傍最大速度」を作るのが標準の手法です。ぼかしの方向・長さ・スキップの判断に使えます。このページでは、TileMax・NeighborMax の 2 段階・実装・使い方・コストを説明します。

!!! tip "ポイント"
    - TileMax ＝ <strong>各タイル（16×16 画素）内で最大の速度ベクトル</strong>（<strong>長さが最大のもの</strong>）。
    - NeighborMax ＝ 周囲 3×3 タイルの TileMax の中で、最大のもの。隣のタイルの速い動きが、流れ込むのを考慮。
    - ぼかしの方向と長さはNeighborMaxから決める。輪郭の外にも尾が伸びる。
    - NeighborMax の長さが閾値以下のタイルはぼかしをスキップ（高速化）。
    - タイル サイズ ＝ 最大ブラー長にそろえる。
    - タイルの数は少ない（1080p で 120×68）。コストは小さい。

!!! info "このページを読む前に"
    - [Motion Blur](index.md)（このセクション全体の地図と、読む順番）

<!-- fig:tile-max:begin -->

<svg class="fig illust motion" data-fig="tile-max" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-tile-max" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">タイルの最大速度: 画面を小さなタイルに分け、タイルごとの最大の動きを調べて、ぼかす必要のない所を飛ばす</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">48×24 画素の速度(明るさ = 動きの大きさ)。4×4 のタイルごとに最大を取り、隣のタイルへ広げる。速い所だけ、重いぼかしをする</text>
<rect x="30" y="100" width="292.0" height="148.0" fill="#ffffff" stroke="#e5aa28" stroke-width="1.8" rx="6"/>
<text x="30" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">① 速度(明るい = 速い)</text>
<rect x="335" y="100" width="292.0" height="148.0" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="335" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② タイルごとの最大</text>
<rect x="640" y="100" width="292.0" height="148.0" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="640" y="90" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">③ 隣へ広げた最大(赤 = 重いぼかしが必要)</text>
<rect x="30.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="102.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="108.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="114.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="72.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="78.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="84.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="90.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="96.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="120.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="72.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="78.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="84.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="90.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="96.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="126.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="72.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="78.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="84.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="90.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="96.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="132.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="72.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="78.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="84.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="90.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="96.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="138.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="72.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="78.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="84.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="90.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#fde68a"/></rect>
<rect x="96.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="144.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="150.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="156.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="162.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="168.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="174.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="180.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="186.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="192.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="240.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="246.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="252.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="258.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="264.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="198.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="240.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="246.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="252.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="258.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="264.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="204.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="240.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="246.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="252.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="258.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="264.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="210.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="240.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="246.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="252.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="258.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#938a5f"/></rect>
<rect x="264.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="216.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="222.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="228.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="234.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="30.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="36.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="42.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="48.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="54.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="60.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="66.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="72.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="78.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="84.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="90.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="96.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="102.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="108.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="114.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="120.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="126.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="132.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="138.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="144.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="150.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="156.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="162.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="168.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="174.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="180.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="186.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="192.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="198.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="204.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="210.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="216.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="222.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="228.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="234.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="240.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="246.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="252.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="258.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="264.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="270.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="276.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="282.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="288.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="294.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="300.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="306.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="312.0" y="240.0" width="6.3" height="6.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0133" values="#0f172a;#141c2c"/></rect>
<rect x="335.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667" values="#0f172a;#131b2f"/></rect>
<rect x="359.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#0f172a;#c4b5fd"/></rect>
<rect x="383.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#0f172a;#c4b5fd"/></rect>
<rect x="407.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#0f172a;#131b2f"/></rect>
<rect x="431.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#0f172a;#131b2f"/></rect>
<rect x="455.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#0f172a;#131b2f"/></rect>
<rect x="479.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0987" values="#0f172a;#131b2f"/></rect>
<rect x="503.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1040" values="#0f172a;#131b2f"/></rect>
<rect x="527.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093" values="#0f172a;#131b2f"/></rect>
<rect x="551.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1147" values="#0f172a;#131b2f"/></rect>
<rect x="575.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#131b2f"/></rect>
<rect x="599.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1253" values="#0f172a;#131b2f"/></rect>
<rect x="335.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#0f172a;#131b2f"/></rect>
<rect x="359.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#0f172a;#c4b5fd"/></rect>
<rect x="383.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#0f172a;#c4b5fd"/></rect>
<rect x="407.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#0f172a;#131b2f"/></rect>
<rect x="431.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#0f172a;#131b2f"/></rect>
<rect x="455.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0987" values="#0f172a;#131b2f"/></rect>
<rect x="479.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1040" values="#0f172a;#131b2f"/></rect>
<rect x="503.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093" values="#0f172a;#131b2f"/></rect>
<rect x="527.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1147" values="#0f172a;#131b2f"/></rect>
<rect x="551.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#131b2f"/></rect>
<rect x="575.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1253" values="#0f172a;#131b2f"/></rect>
<rect x="599.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1307" values="#0f172a;#131b2f"/></rect>
<rect x="335.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#0f172a;#131b2f"/></rect>
<rect x="359.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#0f172a;#131b2f"/></rect>
<rect x="383.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#0f172a;#131b2f"/></rect>
<rect x="407.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#0f172a;#131b2f"/></rect>
<rect x="431.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0987" values="#0f172a;#131b2f"/></rect>
<rect x="455.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1040" values="#0f172a;#131b2f"/></rect>
<rect x="479.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093" values="#0f172a;#131b2f"/></rect>
<rect x="503.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1147" values="#0f172a;#131b2f"/></rect>
<rect x="527.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#131b2f"/></rect>
<rect x="551.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1253" values="#0f172a;#131b2f"/></rect>
<rect x="575.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1307" values="#0f172a;#131b2f"/></rect>
<rect x="599.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1360" values="#0f172a;#131b2f"/></rect>
<rect x="335.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#0f172a;#131b2f"/></rect>
<rect x="359.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#0f172a;#131b2f"/></rect>
<rect x="383.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#0f172a;#131b2f"/></rect>
<rect x="407.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0987" values="#0f172a;#131b2f"/></rect>
<rect x="431.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1040" values="#0f172a;#131b2f"/></rect>
<rect x="455.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093" values="#0f172a;#131b2f"/></rect>
<rect x="479.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1147" values="#0f172a;#131b2f"/></rect>
<rect x="503.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#131b2f"/></rect>
<rect x="527.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1253" values="#0f172a;#131b2f"/></rect>
<rect x="551.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1307" values="#0f172a;#131b2f"/></rect>
<rect x="575.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1360" values="#0f172a;#131b2f"/></rect>
<rect x="599.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1413" values="#0f172a;#131b2f"/></rect>
<rect x="335.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#0f172a;#131b2f"/></rect>
<rect x="359.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#0f172a;#131b2f"/></rect>
<rect x="383.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0987" values="#0f172a;#131b2f"/></rect>
<rect x="407.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1040" values="#0f172a;#131b2f"/></rect>
<rect x="431.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093" values="#0f172a;#131b2f"/></rect>
<rect x="455.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1147" values="#0f172a;#131b2f"/></rect>
<rect x="479.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#131b2f"/></rect>
<rect x="503.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1253" values="#0f172a;#131b2f"/></rect>
<rect x="527.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1307" values="#0f172a;#746f9f"/></rect>
<rect x="551.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1360" values="#0f172a;#746f9f"/></rect>
<rect x="575.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1413" values="#0f172a;#131b2f"/></rect>
<rect x="599.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1467" values="#0f172a;#131b2f"/></rect>
<rect x="335.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#0f172a;#131b2f"/></rect>
<rect x="359.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0987" values="#0f172a;#131b2f"/></rect>
<rect x="383.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1040" values="#0f172a;#131b2f"/></rect>
<rect x="407.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093" values="#0f172a;#131b2f"/></rect>
<rect x="431.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1147" values="#0f172a;#131b2f"/></rect>
<rect x="455.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#131b2f"/></rect>
<rect x="479.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1253" values="#0f172a;#131b2f"/></rect>
<rect x="503.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1307" values="#0f172a;#131b2f"/></rect>
<rect x="527.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1360" values="#0f172a;#131b2f"/></rect>
<rect x="551.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1413" values="#0f172a;#131b2f"/></rect>
<rect x="575.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1467" values="#0f172a;#131b2f"/></rect>
<rect x="599.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1520" values="#0f172a;#131b2f"/></rect>
<rect x="640.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2444" values="#0f172a;#ef4444"/></rect>
<rect x="664.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2498" values="#0f172a;#ef4444"/></rect>
<rect x="688.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2551" values="#0f172a;#ef4444"/></rect>
<rect x="712.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2604" values="#0f172a;#ef4444"/></rect>
<rect x="736.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2658" values="#0f172a;#1e293b"/></rect>
<rect x="760.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#0f172a;#1e293b"/></rect>
<rect x="784.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#0f172a;#1e293b"/></rect>
<rect x="808.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#0f172a;#1e293b"/></rect>
<rect x="832.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#0f172a;#1e293b"/></rect>
<rect x="856.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#0f172a;#1e293b"/></rect>
<rect x="880.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#0f172a;#1e293b"/></rect>
<rect x="904.0" y="102.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3031" values="#0f172a;#1e293b"/></rect>
<rect x="640.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2498" values="#0f172a;#ef4444"/></rect>
<rect x="664.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2551" values="#0f172a;#ef4444"/></rect>
<rect x="688.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2604" values="#0f172a;#ef4444"/></rect>
<rect x="712.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2658" values="#0f172a;#ef4444"/></rect>
<rect x="736.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#0f172a;#1e293b"/></rect>
<rect x="760.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#0f172a;#1e293b"/></rect>
<rect x="784.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#0f172a;#1e293b"/></rect>
<rect x="808.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#0f172a;#1e293b"/></rect>
<rect x="832.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#0f172a;#1e293b"/></rect>
<rect x="856.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#0f172a;#1e293b"/></rect>
<rect x="880.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3031" values="#0f172a;#1e293b"/></rect>
<rect x="904.0" y="126.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3084" values="#0f172a;#1e293b"/></rect>
<rect x="640.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2551" values="#0f172a;#ef4444"/></rect>
<rect x="664.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2604" values="#0f172a;#ef4444"/></rect>
<rect x="688.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2658" values="#0f172a;#ef4444"/></rect>
<rect x="712.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#0f172a;#ef4444"/></rect>
<rect x="736.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#0f172a;#1e293b"/></rect>
<rect x="760.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#0f172a;#1e293b"/></rect>
<rect x="784.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#0f172a;#1e293b"/></rect>
<rect x="808.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#0f172a;#1e293b"/></rect>
<rect x="832.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#0f172a;#1e293b"/></rect>
<rect x="856.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3031" values="#0f172a;#1e293b"/></rect>
<rect x="880.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3084" values="#0f172a;#1e293b"/></rect>
<rect x="904.0" y="150.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3138" values="#0f172a;#1e293b"/></rect>
<rect x="640.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2604" values="#0f172a;#1e293b"/></rect>
<rect x="664.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2658" values="#0f172a;#1e293b"/></rect>
<rect x="688.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#0f172a;#1e293b"/></rect>
<rect x="712.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#0f172a;#1e293b"/></rect>
<rect x="736.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#0f172a;#1e293b"/></rect>
<rect x="760.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#0f172a;#1e293b"/></rect>
<rect x="784.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#0f172a;#1e293b"/></rect>
<rect x="808.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#0f172a;#ef4444"/></rect>
<rect x="832.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3031" values="#0f172a;#ef4444"/></rect>
<rect x="856.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3084" values="#0f172a;#ef4444"/></rect>
<rect x="880.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3138" values="#0f172a;#ef4444"/></rect>
<rect x="904.0" y="174.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3191" values="#0f172a;#1e293b"/></rect>
<rect x="640.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2658" values="#0f172a;#1e293b"/></rect>
<rect x="664.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#0f172a;#1e293b"/></rect>
<rect x="688.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#0f172a;#1e293b"/></rect>
<rect x="712.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#0f172a;#1e293b"/></rect>
<rect x="736.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#0f172a;#1e293b"/></rect>
<rect x="760.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#0f172a;#1e293b"/></rect>
<rect x="784.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#0f172a;#1e293b"/></rect>
<rect x="808.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3031" values="#0f172a;#ef4444"/></rect>
<rect x="832.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3084" values="#0f172a;#ef4444"/></rect>
<rect x="856.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3138" values="#0f172a;#ef4444"/></rect>
<rect x="880.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3191" values="#0f172a;#ef4444"/></rect>
<rect x="904.0" y="198.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3244" values="#0f172a;#1e293b"/></rect>
<rect x="640.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#0f172a;#1e293b"/></rect>
<rect x="664.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#0f172a;#1e293b"/></rect>
<rect x="688.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#0f172a;#1e293b"/></rect>
<rect x="712.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#0f172a;#1e293b"/></rect>
<rect x="736.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#0f172a;#1e293b"/></rect>
<rect x="760.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#0f172a;#1e293b"/></rect>
<rect x="784.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3031" values="#0f172a;#1e293b"/></rect>
<rect x="808.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3084" values="#0f172a;#ef4444"/></rect>
<rect x="832.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3138" values="#0f172a;#ef4444"/></rect>
<rect x="856.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3191" values="#0f172a;#ef4444"/></rect>
<rect x="880.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3244" values="#0f172a;#ef4444"/></rect>
<rect x="904.0" y="222.0" width="24.3" height="24.3" fill="#0f172a"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3298" values="#0f172a;#1e293b"/></rect>
<text x="40" y="270" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">タイルの数:</text>
<text x="150" y="274" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1625;0.1627;1.0000" values="1;1;0;0"/></text>
<text x="150" y="274" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">72<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1625;0.1627;0.3403;0.3404;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="274" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">24<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3403;0.3404;1.0000" values="0;0;1;1"/></text>
<text x="190" y="274" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">(最初は全 72 個 → 重いぼかしが必要 24 個)</text>
<rect x="30" y="300" width="900" height="170" fill="#ffffff" stroke="#2ea043" stroke-width="1.8" rx="6"/>
<text x="30" y="290" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">ぼかしの読み込み(1 タイルあたり: 重い 40、軽い 2)</text>
<text x="50" y="350" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">全タイルを重いぼかし<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4443;0.4444;1.0000" values="0;0;1;1"/></text>
<rect x="290" y="336" width="1" height="22" fill="#e5484d" opacity="0.85"><animate attributeName="width" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4444;0.4889;1.0000" values="1;1;560;560"/></rect>
<text x="860.0" y="353" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="0">2880(×1 タイル)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4887;0.4889;1.0000" values="0;0;1;1"/></text>
<text x="50" y="386" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">タイルの最大で、振り分ける<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4976;0.4978;1.0000" values="0;0;1;1"/></text>
<rect x="290" y="372" width="1" height="22" fill="#2ea043" opacity="0.85"><animate attributeName="width" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4978;0.5422;1.0000" values="1;1;205.33;205.33"/></rect>
<text x="505.3333333333333" y="389" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043" opacity="0">1056(×1 タイル)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5420;0.5422;1.0000" values="0;0;1;1"/></text>
<text x="50" y="436" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb" opacity="0">約 2.7 倍 速い。隣のタイルへ広げる理由: 隣の速い物の流れが、このタイルにはみ出してくるから<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5776;0.5778;1.0000" values="0;0;1;1"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">画面の大半は、動かないので、ブラーは要らない<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">タイルごとに、最大の速さを調べる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.2443;0.2444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">隣のタイルへ広げて、はみ出しに備える<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2443;0.2444;0.4220;0.4222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">速いタイルだけに、重い処理をする<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4220;0.4222;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:tile-max:end -->

## なぜ必要か

<strong>速い物体のブラー</strong>は、物体の外側にも尾を引くべきです。画素 P 自身の速度だけを使うと、P が背景（速度 0）なら、ぼけません。P の近くに速い物体があれば、その速度の分だけ、P の周りを見る必要があります。

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="タイルの最大速度">
<text x="20" y="26" class="fig-title">タイルの最大速度：近くにある速い動きを周りの画素に知らせる</text>
<g transform="translate(40,56)">
<rect x="0" y="0" width="320" height="140" fill="#f8fafc" stroke="#94a3b8"/>
<g stroke="#e2e8f0"><line x1="80" y1="0" x2="80" y2="140"/><line x1="160" y1="0" x2="160" y2="140"/><line x1="240" y1="0" x2="240" y2="140"/><line x1="0" y1="35" x2="320" y2="35"/><line x1="0" y1="70" x2="320" y2="70"/><line x1="0" y1="105" x2="320" y2="105"/></g>
<rect x="165" y="45" width="30" height="20" fill="#2563eb"/>
<line x1="165" y1="55" x2="130" y2="55" stroke="#e5484d" stroke-width="3" marker-end="url(#tm2-arrow)"/>
<defs><marker id="tm2-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#e5484d"/></marker></defs>
<rect x="160" y="35" width="80" height="35" fill="#e5aa28" fill-opacity="0.35"/>
<text x="164" y="30" style="font-size:11px">速い物体を含むタイル</text>
<rect x="80" y="35" width="80" height="35" fill="#e5484d" fill-opacity="0.2"/>
<text x="84" y="88" style="font-size:11px">隣のタイル（背景）にも伝える</text>
</g>
<g font-size="13"><text x="400" y="90" style="font-weight:700">2 段階</text>
<text x="400" y="116">① TileMax：各タイルの最大速度</text>
<text x="400" y="140">② NeighborMax：周囲 3×3 の最大</text>
<text x="400" y="176" style="font-weight:700">→ 背景のタイルにも、物体の速度が伝わる</text></g>
</svg>

## 手順

タイル最大速度の手順は 3 段階です。TileMax は、各タイル内の速度のうち、長さが最大のベクトルを求めます（共有メモリで縮約）。NeighborMax は、周囲 3×3 の TileMax の最大を求めます。ぼかしでは、NeighborMax の方向と長さでサンプルします。

## ① TileMax

```hlsl
Texture2D<float2> velocity_buffer : register(t0);
RWTexture2D<float2> tile_max : register(u0);

groupshared float2 s_velocity[256];

[numthreads(16, 16, 1)]
void TileMaxMain(uint3 id : SV_DispatchThreadID, uint3 group_id : SV_GroupID, uint group_index : SV_GroupIndex) {
  float2 v = velocity_buffer.Load(int3(id.xy, 0));
  s_velocity[group_index] = v;
  GroupMemoryBarrierWithGroupSync();
  for (uint stride = 128; stride > 0; stride >>= 1) {
    if (group_index < stride) {
      float2 other = s_velocity[group_index + stride];
      if (dot(other, other) > dot(s_velocity[group_index], s_velocity[group_index])) {
        s_velocity[group_index] = other;
      }
    }
    GroupMemoryBarrierWithGroupSync();
  }
  if (group_index == 0) tile_max[group_id.xy] = s_velocity[0];
}
```

TileMax のコードの要点です。16×16 のグループが 1 タイルを担当します。`dot(v, v)`（長さの 2 乗）で比較して、平方根を避けます。共有メモリでの縮約で、256 個を 8 回の比較で 1 個にします。

## ② NeighborMax

<strong>TileMax の画像（小さい）</strong>を読み、周囲 3×3 の最大を取ります。

```hlsl
Texture2D<float2> tile_max_texture : register(t0);
RWTexture2D<float2> neighbor_max : register(u0);

[numthreads(8, 8, 1)]
void NeighborMaxMain(uint3 id : SV_DispatchThreadID) {
  float2 best = 0;
  float best_length_sq = 0;
  for (int y = -1; y <= 1; ++y) {
    for (int x = -1; x <= 1; ++x) {
      int2 p = clamp(int2(id.xy) + int2(x, y), 0, tile_count - 1);
      float2 v = tile_max_texture.Load(int3(p, 0));
      float len_sq = dot(v, v);
      if (len_sq > best_length_sq) {
        best = v;
        best_length_sq = len_sq;
      }
    }
  }
  neighbor_max[id.xy] = best;
}
```

NeighborMax のコードの要点です。3×3 で見るのは、隣のタイルの速い物体が 1 タイル先まで影響するためです（タイルの大きさが最大ブラー長だからです）。端は `clamp` で、画面の外は端のタイルを繰り返します。

### より正確な NeighborMax

単純な 3×3 の最大は、向きを無視して長さだけで選びます。「そのタイルの速度が自分のタイルに向かっているか」を考慮すると、より正確です（McGuire 方式）。

## ぼかしでの使い方

```hlsl
float2 neighbor_velocity = neighbor_max.SampleLevel(point_clamp, uv, 0).xy;
float neighbor_length = length(neighbor_velocity * resolution);
if (neighbor_length < kMinVelocityPixels) {
  return scene_color.SampleLevel(point_clamp, uv, 0).rgb;
}
```

| 用途 | 内容 |
| --- | --- |
| ぼかしの方向 | NeighborMax の向きにサンプルを配置 |
| ぼかしの長さ | NeighborMax の長さ（最大ブラー長で制限） |
| スキップ判定 | 長さが小さいタイル（< 0.5 画素）は、ぼかしを省略 |
| 自分の速度との組み合わせ | サンプルの重み付けに自分の速度も使う（[Blur Pass Implementation](blur-pass.md)） |

## コスト

コストです。TileMax は、フル解像度の速度を 1 回読むだけで、帯域は R16G16 のみです。NeighborMax は、タイル数分（1080p で 120×68）で、ほぼ無料です。効果として、静止している多くの画素でぼかしをスキップでき、フレーム全体で大幅に節約できます。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| タイル サイズ ＝ 最大ブラー長 | 16〜20 画素が一般的 |
| NeighborMax に向きを考慮 | 精度が上がる |
| スキップ判定で分岐の一貫性 | タイル単位で同じ分岐になり、GPU が無駄なく動く |
| DOF のタイルと共用 | 同じ 16×16 のタイルで、DOF の最大 CoC も計算（[Foreground and Background](../dof/near-far.md)） |

## よくあるミス

??? failure "NeighborMax を使わず、輪郭の外にブラーが出ない"
    <strong>周囲の速度をタイルの最大で伝える</strong>。

??? failure "タイルの大きさがブラー長より小さく、速い物体の尾が届かない"
    タイル サイズ ≧ 最大ブラー長にする。

??? failure "画面の端のタイルで、範囲外を読んで壊れる"
    `clamp` で端をそろえる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>TileMax</strong> ＝ タイルごとの最大速度。NeighborMax ＝ 周囲 3×3 の最大
    - [x] 背景の画素にも、近くの速い物体の速度を伝え、尾を伸ばす
    - [x] 遅いタイルは、ぼかしをスキップ（高速化）
    - [x] タイル サイズ ＝ 最大ブラー長
    - [x] 共有メモリで縮約

## 参考

- McGuire et al., "A Reconstruction Filter for Plausible Motion Blur"（I3D 2012）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）

## 関連ページ

- [Motion Blur](index.md)
- [Velocity Buffer](velocity-buffer.md)
- [Blur Pass Implementation](blur-pass.md)
- [Foreground and Background](../dof/near-far.md)
