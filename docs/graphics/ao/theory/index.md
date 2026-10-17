---
title: AO Theory
tags:
  - 描画
---

# AO Theory

**環境光遮蔽（AO）**は、**「ある点が、周りの物にどれだけ遮られて、環境光が届きにくいか」**を**表します**。**くぼみ・隅・物の接地部が暗くなる**ので、**立体感と接地感**が**増します**。**その数学的な定義と近似の仕方を知ると、各方式（SSAO・HBAO・GTAO…）の違いが整理できます**。このセクションでは、**レンダリング方程式から AO への導出・球面座標・オブスキュランス・近似の 3 つのやり方・スクリーン空間の可視性・使い方と誤解**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **AO ＝ 点の周りの半球で、遮られていない方向の割合**（**コサイン重み付き**）。
    - **環境光が一様に明るいと仮定**して、**レンダリング方程式を単純化**したもの。
    - **オブスキュランスは、遠い物の遮蔽を弱める**（**距離で減衰**）。
    - **近似の 3 つ**：**サンプルする・水平線を探す・解析的に近似**。
    - **スクリーン空間では、深度バッファから、可視性 V を推定する**。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [From the Rendering Equation to AO](from-rendering-equation.md) | 出発点・一様な天球の仮定・球面座標 |
| [Obscurance](obscurance.md) | 距離の減衰を足す |
| [Approximating the Integral](approximation.md) | 3 つのやり方・方式を分けるもの |
| [Screen-Space Visibility](screen-space-visibility.md) | 深度バッファから V を求める |
| [Usage and Misconceptions of AO](usage-misconceptions.md) | 適用の仕方・よくある誤解 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **AO ＝ 遮られていない方向の、コサイン重み付きの割合**
    - [x] **方式の違いは、積分の近似の仕方の違い**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [Ambient Occlusion (AO)](../index.md)
- [方式の比較](../comparison.md)
