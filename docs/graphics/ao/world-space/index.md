---
title: Ray-Traced, Distance-Field and Voxel AO
tags:
  - 描画
---

# Ray-Traced, Distance-Field and Voxel AO

<strong>スクリーン空間の AO は、画面に写っている物しか見ない</strong>ため、<strong>画面外の遮蔽物や、薄い物の裏側を扱えません</strong>。画面に頼らず、ワールド空間（シーンそのもの）を使って AO を求める方式が世界空間 AOで、レイトレース AO・距離場 AO・ボクセル AOの3 つが代表的です。このセクションでは、共通する考え方・各方式・比較・スクリーン空間との使い分けを、1 つずつ別のページで説明します。

## 共通する考え方
[理論](../theory/index.md)の AO は、`AO = (1/π) ∫ V(ω)(n·ω) dω` でした。V(ω) は、<strong>方向 ω にレイを飛ばして、半径 R 以内に何かに当たるか</strong>です。3 方式は<strong>この V を別々のデータ構造で求める</strong>だけです。

RTAO は、三角形の BVH（加速構造）を使い、実際にレイを飛ばして、最大距離 R 以内に当たるかを数えます。DFAO は、符号付き距離場（SDF）を使い、円錐に沿って進みながら、距離場の値から遮蔽の割合を求めます。VXAO は、ボクセル（占有度の 3D グリッド）を使い、円錐に沿ってボクセルの占有度を積み上げます。

レイを 1 本ずつ当てる RTAO は、正確ですがノイズが出ます。円錐でまとめて調べる DFAO と VXAO は、1 本のトレースで広がりのある方向をまとめて評価できるので、ノイズが小さい代わりに、データ構造の解像度に精度が縛られます。この「正確さとノイズ」「粗さと滑らかさ」の取引が、3 方式の性格を決めています。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Ray-Traced AO (RTAO)](rtao.md) | 半球にレイを飛ばして、遮蔽を数える |
| [Distance Field AO (DFAO)](dfao.md) | 符号付き距離場で、円錐を進める |
| [Voxel AO (VXAO)](vxao.md) | ボクセルのミップで、円錐トレース |
| [World-Space AO Comparison](comparison.md) | 3 方式の比較・使い分け |

## 3 つの方式の、距離の測り方

| 方式 | 何を持つか | 空間の問い | 更新 |
| --- | --- | --- | --- |
| RTAO | 三角形の BVH | 「この方向のレイは、近くで何かに当たるか」を、直接調べる | TLAS を毎フレーム更新 |
| DFAO | メッシュごとの、距離場（SDF） | 「この点から、どれだけ進んでも、物に当たらないか」を、距離で知る | 動く物は、変換だけ。メッシュ自体の変形は不可 |
| VXAO | ボクセル格子 | 「この円錐の中は、どれだけ埋まっているか」を、ミップで知る | 動く物を、毎フレーム再ボクセル化 |

どれも、<strong>画面の外や、手前の物の裏側の遮蔽</strong>を扱える点が、スクリーン空間の AO との違いです（[Screen-Space Visibility](../theory/screen-space-visibility.md)）。そのかわり、ジオメトリをもう 1 つ（BVH、SDF、ボクセル）持つコストと、手間がかかります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 画面に頼らず、シーンから AO を求める
    - [x] RTAO・DFAO・VXAO の 3 方式

## 参考

- Wright, "Dynamic Occlusion with Signed Distance Fields", SIGGRAPH 2015, Advances in Real-Time Rendering in Games（Unreal Engine 4 の DFAO）
- Crassin, Neyret, Sainz, Green, Eisemann, "Interactive Indirect Illumination Using Voxel Cone Tracing", Computer Graphics Forum (Pacific Graphics 2011)
- Microsoft, "DirectX Raytracing (DXR) Functional Spec"
- Barré-Brisebois, Halén, Wihlidal, Lauritzen, Bekkers, Stachowiak, Andersson, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 25, 2019

## 関連ページ

- [Ambient Occlusion (AO)](../index.md)
- [GTAO](../gtao.md)
- [AO Comparison](../comparison.md)
