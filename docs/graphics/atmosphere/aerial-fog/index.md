---
title: Aerial Perspective and Fog
tags:
  - 描画
---

# Aerial Perspective and Fog

**遠くの景色は、空気の層を通って、青く霞んで見えます**。**これを空気遠近法と呼び、距離感を出すために、とても重要**です。このセクションでは、**必要な理由・フォグの式・高さフォグ・太陽方向のにじみ・色を空に合わせる・物理に基づく空気遠近法・適用する場所**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **遠くほど、霞んで、空の色に近づく**。
    - **フォグがないと、距離感が失われる**。
    - **フォグの色を、空に合わせる**のが**重要**。
    - **高さフォグで、谷に霧がたまる表現**ができる。

## なぜ必要か
**フォグがない**と**遠くの物が近くの物と同じコントラストで見え**、**平面的**で**スケール感が出ません**。**フォグ**は**遠い物ほど霞ませる**ことで、**奥行きを伝えます**。

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="空気遠近法">
<text x="20" y="24" class="fig-title">フォグなし（上）とあり（下）：遠くほど空の色に近づく</text>
<polygon points="40,90 160,50 240,90 320,40 420,90 520,55 620,90 740,45 740,90" fill="#2d5a3d"/>
<polygon points="40,185 160,145 240,185 320,135 420,185 520,150 620,185 740,140 740,185" fill="#2d5a3d" opacity="0.9"/>
<polygon points="320,185 420,185 520,150 620,185 740,140 740,185" fill="#b8c9e0" opacity="0.65"/>
<polygon points="520,185 620,185 740,140 740,185" fill="#b8c9e0" opacity="0.4"/>
<text x="40" y="112" style="font-size:12px">全部同じ濃さ</text>
<text x="40" y="206" style="font-size:12px">遠いほど霞む</text>
</svg>

## 空気遠近法の物理

遠くの山が青く霞んで見える現象は、画家たちが昔から「空気遠近法」と呼んで、絵に奥行きを出すために使ってきました。レオナルド・ダ・ヴィンチも、遠景ほど青みを帯びてコントラストが下がる様子を記録しています。物理的には、空気中の分子や微粒子が光を散らすために起きます。

遠くの物体から目に届く光は、2 つの変化を受けます。1 つは<strong>減衰</strong>です。物体から目に向かう光の一部は、途中で空気に散らされて、別の方向へ逸れてしまいます。距離が長いほど、物体本来の光は弱まります。もう 1 つは<strong>加算</strong>です。太陽や空から来た光が、視線上の空気で目の方向へ散らされて、新しく目に入ってきます。これは物体とは無関係の、空気自身の光で、青みがかっています（空が青い理由と同じ、レイリー散乱です）。この 2 つを合わせると、遠景は「本来の色が薄れ、空の色が混ざった」姿になります。

<div class="formula">最終色 = 物体の色 × T + 空気の散乱光 × (1 − T)　　（T は透過率、距離が長いほど 0 に近づく）</div>

ゲームでは、これを<strong>フォグ</strong>として実装します。深度から距離を求め、透過率 T を計算し、物体の色と空気の色を T で混ぜるだけです。式は単純ですが、T の決め方（距離だけか、高さも見るか）と、空気の色の決め方（一定か、空から取るか、太陽に応じて変えるか）で、見た目がまったく変わります。このセクションは、その選択肢を順に見ていきます。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Fog Equations](fog-equation.md) | 線形・指数・指数二乗 |
| [Height Fog](height-fog.md) | 低い所に霧がたまる |
| [Sun Inscatter](sun-inscatter.md) | 太陽の方向が明るく霞む |
| [色を空に合わせる](color-match.md) | フォグの色の決め方 |
| [Physically Based Aerial Perspective](physical.md) | 散乱の LUT を使う |
| [Where to Apply Fog](where.md) | 夜・屋内・閉所の扱い |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **距離で霞ませ、空の色になじませる**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [大気](../index.md)
- [Atmospheric Scattering](../scattering/index.md)
- [Volumetric Fog](../volumetric-fog/index.md)
