---
title: Ray-Traced Reflections
tags:
  - 描画
---

# Ray-Traced Reflections

**レイトレ反射は、GPU のレイトレーシング機能で、実際にシーンへレイを飛ばして、反射を求める手法**です。**画面の外の物も、隠れた物も、正確に映せます**が、**コストが高く、ノイズも出る**ので、**工夫が必要**です。このセクションでは、**SSR との違い・レイの生成・ヒット点のシェーディング・ハイブリッド構成・ノイズ除去**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **画面外・隠れた物も、正確に映る**。
    - **コストが高い**。**粗い面ではノイズが出る**。
    - **SSR とのハイブリッド**が、**現実的**。
    - **デノイザ（ノイズ除去）が、品質を左右**する。

## SSR との違い
SSR との違いを整理します。探索の相手が、SSR は深度バッファ（画面）、レイトレ反射は BVH（シーンの三角形）です。そのため、SSR では画面外や裏側が映りませんが、レイトレでは映ります。半透明の向こうも、SSR は映せず、レイトレは any-hit シェーダーで映せます。反射の中の反射は、SSR では不可能（あるいは 1 回だけ）で、レイトレは再帰で可能ですが、コストが増えます。必要な機能は、SSR が深度と色だけなのに対し、レイトレは対応 GPU と BVH です。ヒット点の色は、SSR は画面の画像から取りますが、レイトレはマテリアルと光をその場で評価します。コストは、SSR が中程度、レイトレが大きいです。

## 全体の流れ
全体の流れは、6 つのパスです。最初に、G-Buffer から位置・法線・粗さを得て、GGX の可視法線サンプリングで<strong>レイの方向を作ります</strong>。次に、`TraceRay`（または `RayQuery`）で BVH をトレースし、最も近い交点を求めます。当たった点で、マテリアル（アルベド・粗さ・法線）と直接光（影のレイ）と間接光から色を計算します（<strong>ヒット点のシェーディング</strong>）。何にも当たらなければ、空（スカイ）の色を返します。得られた色には強いノイズがあるので、空間と時間のフィルタで<strong>デノイズ</strong>します。最後に、BRDF の積分（スケールとバイアス）を掛け、フォールバックと混ぜて<strong>合成</strong>します。

### 歴史

ゲームでのレイトレ反射の本格的な採用は、2018 年の DXR 登場と、それを使った『Battlefield V』が最初です。同じ頃、SEED の PICA PICA プロジェクトが、ハイブリッド構成（SSR で足りない部分だけレイトレ）の実用的な設計を公開しました。また、Stachowiak の "Stochastic all the things"（SIGGRAPH 2018）は、確率的なレイとデノイズで反射を出す設計を示しました。いまの商用エンジンの反射は、これらの流れの上にあります。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Ray Generation](ray-generation.md) | 反射レイ・粗さに応じた方向 |
| [ヒット点のシェーディング](hit-shading.md) | 当たった先の色の求め方・BVH |
| [Hybrid Pipeline](hybrid.md) | SSR とレイトレの組み合わせ・性能の工夫 |
| [Denoising](denoise.md) | デノイズ・長所と短所 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **レイトレ反射は、正確だが重い**
    - [x] **ハイブリッドとデノイズで、実用にする**

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [Reflections](../index.md)
- [SSR Basics](../ssr-basics/index.md)
- [Ray-Traced GI](../../gi/rt-gi/index.md)
