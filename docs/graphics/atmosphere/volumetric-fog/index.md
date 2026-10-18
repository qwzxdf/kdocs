---
title: Volumetric Fog
tags:
  - 描画
---

# Volumetric Fog

**ボリューメトリック フォグは、霧の中を光が通る様子を、3D の体積として計算する手法**です。**光の筋や、影の中の霧、ライトの周りの光の玉**が**表現**できます。このセクションでは、**通常のフォグとの違い・froxel・手順・密度・光の注入・積分と適用・時間蓄積・品質と速度**を、**1 つずつ別のページ**で説明します。

## What Differs {#何が違うか}
フォグ系の方式の違いを整理します。距離フォグは、ピクセルの距離だけで決まり、光は関係しません。高さフォグは、高さと距離で決まり、これも光とは関係しません。ボリューメトリック フォグは、空間の各点で光を計算するので、光の筋・影・光る霧を表現できます。

## Steps {#手順}
<svg class="fig illust" viewBox="0 0 780 160" role="img" aria-label="ボリューメトリック フォグの手順"><defs><marker id="rfa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">4 つのパス</text>
<g font-size="12">
<rect x="20" y="56" width="165" height="70" rx="8" fill="#4c8bf5" fill-opacity="0.2" stroke="#4c8bf5" stroke-width="2"/><text x="102" y="86" text-anchor="middle" style="font-weight:700">① 密度</text><text x="102" y="106" text-anchor="middle" style="font-size:11px">各 froxel の霧の濃さ</text>
<rect x="215" y="56" width="165" height="70" rx="8" fill="#e5aa28" fill-opacity="0.22" stroke="#e5aa28" stroke-width="2"/><text x="297" y="86" text-anchor="middle" style="font-weight:700">② 光の注入</text><text x="297" y="106" text-anchor="middle" style="font-size:11px">光 × 影 × 位相関数</text>
<rect x="410" y="56" width="165" height="70" rx="8" fill="#9664e6" fill-opacity="0.2" stroke="#9664e6" stroke-width="2"/><text x="492" y="86" text-anchor="middle" style="font-weight:700">③ 積分</text><text x="492" y="106" text-anchor="middle" style="font-size:11px">奥へ足して透過率</text>
<rect x="605" y="56" width="155" height="70" rx="8" fill="#2ea043" fill-opacity="0.2" stroke="#2ea043" stroke-width="2"/><text x="682" y="86" text-anchor="middle" style="font-weight:700">④ 適用</text><text x="682" y="106" text-anchor="middle" style="font-size:11px">画面に合成</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="187" y1="91" x2="213" y2="91" marker-end="url(#rfa)"/><line x1="382" y1="91" x2="408" y2="91" marker-end="url(#rfa)"/><line x1="577" y1="91" x2="603" y2="91" marker-end="url(#rfa)"/></g>
</svg>

## Background: Why Froxels {#背景なぜ-froxel-なのか}

視線に沿って光を積分する処理（レイマーチ）は、画素ごとにシャドウ マップを何十回も引くので、重い処理です。ボリューメトリック フォグが実用になったのは、Wronski の SIGGRAPH 2014 の発表 "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering"（『Assassin's Creed IV』）が、この計算を<strong>画面の解像度に依存しない、低解像度の 3D テクスチャ</strong>に移したからです。

考え方は、次のとおりです。フォグは、細かい構造をほとんど持たない、低周波の現象です。画素ごとに正確に計算しなくても、視錐台を 160×90×64 のような粗いセルに分けて、セルごとに光の量を計算し、画素の位置では補間して取り出せば、見た目に十分です。計算量は、画素数（約 200 万）から、セル数（約 90 万）へ、さらに、各セルで 1 回だけ光を計算すれば済むので、画素ごとのレイマーチより桁違いに少なくなります。

さらに、セルごとに計算するので、ライトを複数注入するのが簡単です。ライトの数が増えても、セルごとにライトを足し合わせるだけで、画素ごとのマーチを増やす必要がありません。Hillaire の Frostbite での発表（"Physically Based and Unified Volumetric Rendering in Frostbite"、SIGGRAPH 2015）は、この仕組みを物理的に整えました。散乱係数と吸収係数を分けて持ち、フォグ・パーティクル・ローカルなボリュームをすべて同じ froxel に書き込む、統一された設計です。

## Page List {#ページ一覧}

| ページ | 内容 |
| --- | --- |
| [Froxels](froxel.md) | 視錐台のグリッド |
| [Step 1: Density](density.md) | 霧の濃さを決める |
| [Step 2: Light Injection](injection.md) | 各セルにライトを足す |
| [Steps 3 and 4: Integration and Application](integration.md) | 視線に沿って足し、シーンに合成 |
| [時間蓄積](temporal.md) | ノイズを消す |
| [Quality and Performance](quality.md) | 解像度・スライス数の目安 |

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **froxel に光を注入して、積分する**

## References {#参考}

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## Related Pages {#関連ページ}

- [大気](../index.md)
- [Aerial Perspective and Fog](../aerial-fog/index.md)
- [God Rays](../god-rays/index.md)
