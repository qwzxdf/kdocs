---
title: AO Theory
tags:
  - 描画
---

# AO Theory

<strong>環境光遮蔽（AO）</strong>は、<strong>「ある点が、周りの物にどれだけ遮られて、環境光が届きにくいか」</strong>を表します。くぼみ・隅・物の接地部が暗くなるので、立体感と接地感が増します。その数学的な定義と近似の仕方を知ると、各方式（SSAO・HBAO・GTAO…）の違いが整理できます。このセクションでは、レンダリング方程式から AO への導出・球面座標・オブスキュランス・近似の 3 つのやり方・スクリーン空間の可視性・使い方と誤解を、1 つずつ別のページで説明します。

## このセクションの読み方

AO を実装するだけなら、理論を読まなくても動くコードは書けます。しかし、<strong>なぜその式になっているのか</strong>を知らないと、パラメータを触ったときに何が起きているのか分からず、不具合の原因も探せません。ここでは、数式をできるだけ図と言葉に置き換えながら、次の順で理解を進めます。

まず、レンダリング方程式から出発して、「環境光が全方向から一様に来る」という仮定を置くと、方程式が<strong>遮られていない方向の割合</strong>という単純な形に変わることを見ます（[From the Rendering Equation to AO](from-rendering-equation.md)）。次に、遠い物まで遮蔽に数えてしまう問題を、距離で弱める工夫（オブスキュランス）で直します（[Obscurance](obscurance.md)）。そのうえで、この積分を実際に計算する 3 つの近似法を眺め（[Approximating the Integral](approximation.md)）、深度バッファしか持たない画面空間では何が分かって何が分からないのかを確認します（[Screen-Space Visibility](screen-space-visibility.md)）。最後に、結果をどこに掛けるべきか、よくある誤解を整理します（[Usage and Misconceptions of AO](usage-misconceptions.md)）。

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
    - [x] AO ＝ 遮られていない方向の、コサイン重み付きの割合
    - [x] 方式の違いは、積分の近似の仕方の違い

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [Ambient Occlusion (AO)](../index.md)
- [AO Comparison](../comparison.md)
