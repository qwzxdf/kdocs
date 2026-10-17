---
title: 空気遠近法・フォグ
tags:
  - 描画
---

# 空気遠近法・フォグ

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

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [フォグの式](fog-equation.md) | 線形・指数・指数二乗 |
| [高さフォグ](height-fog.md) | 低い所に霧がたまる |
| [太陽方向のにじみ](sun-inscatter.md) | 太陽の方向が明るく霞む |
| [色を空に合わせる](color-match.md) | フォグの色の決め方 |
| [物理に基づく空気遠近法](physical.md) | 散乱の LUT を使う |
| [適用する場所](where.md) | 夜・屋内・閉所の扱い |

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
- [大気散乱](../scattering/index.md)
- [ボリューメトリック フォグ](../volumetric-fog/index.md)
