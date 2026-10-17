---
title: ボリューメトリック フォグ
tags:
  - 描画
---

# ボリューメトリック フォグ

**ボリューメトリック フォグは、霧の中を光が通る様子を、3D の体積として計算する手法**です。**光の筋や、影の中の霧、ライトの周りの光の玉**が**表現**できます。このセクションでは、**通常のフォグとの違い・froxel・手順・密度・光の注入・積分と適用・時間蓄積・品質と速度**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **空間を、3D のグリッド（froxel）に分ける**。
    - **各セルに、密度と光を計算して、視線に沿って積分**。
    - **シャドウを考慮した光の筋**ができる。
    - **時間蓄積でノイズを消す**。

## 何が違うか
| 方式 | 内容 |
| --- | --- |
| **距離フォグ** | **ピクセルの距離のみ。光は関係なし** |
| **高さフォグ** | **高さと距離。光は関係なし** |
| **ボリューメトリック フォグ** | **空間の各点で光を計算。光の筋・影・光る霧** |

## 手順
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

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [froxel](froxel.md) | 視錐台のグリッド |
| [① 密度](density.md) | 霧の濃さを決める |
| [② 光の注入](injection.md) | 各セルにライトを足す |
| [③ 積分と ④ 適用](integration.md) | 視線に沿って足し、シーンに合成 |
| [時間蓄積](temporal.md) | ノイズを消す |
| [品質と速度](quality.md) | 解像度・スライス数の目安 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **froxel に光を注入して、積分する**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [大気](../index.md)
- [空気遠近法・フォグ](../aerial-fog/index.md)
- [ゴッド レイ](../god-rays/index.md)
