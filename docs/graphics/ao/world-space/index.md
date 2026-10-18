---
title: Ray-Traced, Distance-Field and Voxel AO
tags:
  - 描画
---

# Ray-Traced, Distance-Field and Voxel AO

**スクリーン空間の AO は、画面に写っている物しか見ない**ため、**画面外の遮蔽物や、薄い物の裏側を扱えません**。**画面に頼らず、ワールド空間（シーンそのもの）を使って AO を求める**方式が**世界空間 AO**で、**レイトレース AO・距離場 AO・ボクセル AO**の**3 つ**が**代表的**です。このセクションでは、**共通する考え方・各方式・比較・スクリーン空間との使い分け**を、**1 つずつ別のページ**で説明します。

## 共通する考え方
[理論](../theory/index.md)の AO は、`AO = (1/π) ∫ V(ω)(n·ω) dω` でした。V(ω) は、**方向 ω にレイを飛ばして、半径 R 以内に何かに当たるか**です。3 方式は**この V を別々のデータ構造で求める**だけです。

RTAO は、三角形の BVH（加速構造）を使い、実際にレイを飛ばして、最大距離 R 以内に当たるかを数えます。DFAO は、符号付き距離場（SDF）を使い、円錐に沿って進みながら、距離場の値から遮蔽の割合を求めます。VXAO は、ボクセル（占有度の 3D グリッド）を使い、円錐に沿ってボクセルの占有度を積み上げます。

レイを 1 本ずつ当てる RTAO は、正確ですがノイズが出ます。円錐でまとめて調べる DFAO と VXAO は、1 本のトレースで広がりのある方向をまとめて評価できるので、ノイズが小さい代わりに、データ構造の解像度に精度が縛られます。この「正確さとノイズ」「粗さと滑らかさ」の取引が、3 方式の性格を決めています。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Ray-Traced AO (RTAO)](rtao.md) | 半球にレイを飛ばして、遮蔽を数える |
| [Distance Field AO (DFAO)](dfao.md) | 符号付き距離場で、円錐を進める |
| [Voxel AO (VXAO)](vxao.md) | ボクセルのミップで、円錐トレース |
| [World-Space AO Comparison](comparison.md) | 3 方式の比較・使い分け |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **画面に頼らず、シーンから AO を求める**
    - [x] **RTAO・DFAO・VXAO の 3 方式**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [Ambient Occlusion (AO)](../index.md)
- [GTAO](../gtao.md)
- [AO Comparison](../comparison.md)
