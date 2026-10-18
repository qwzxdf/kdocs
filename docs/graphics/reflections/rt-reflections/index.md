---
title: Ray-Traced Reflections
tags:
  - 描画
---

# Ray-Traced Reflections

**レイトレ反射は、GPU のレイトレーシング機能で、実際にシーンへレイを飛ばして、反射を求める手法**です。**画面の外の物も、隠れた物も、正確に映せます**が、**コストが高く、ノイズも出る**ので、**工夫が必要**です。このセクションでは、**SSR との違い・レイの生成・ヒット点のシェーディング・ハイブリッド構成・ノイズ除去**を、**1 つずつ別のページ**で説明します。

## SSR との違い
| 項目 | SSR | レイトレ反射 |
| --- | --- | --- |
| **探索の相手** | 深度バッファ（画面） | <strong>BVH（シーンの三角形）</strong> |
| **画面外・裏側** | **映らない** | **映る** |
| **半透明の向こう** | 映らない | **映る**（any-hit） |
| **反射の中の反射** | 不可（または 1 回だけ） | **再帰で可能**（コスト増） |
| **必要な機能** | 深度・色 | **レイトレ対応 GPU・BVH** |
| **ヒット点の色** | 画面の画像から取る | **マテリアルと光をその場で評価** |
| **コスト** | 中 | **大** |

## 全体の流れ
| パス | 内容 |
| --- | --- |
| **① レイの生成** | G-Buffer から、**位置・法線・粗さ**を得て、**GGX VNDF** で方向を選ぶ |
| **② BVH のトレース** | **`TraceRay`**（または `RayQuery`）で、**最も近い交点**を求める |
| **③ ヒット点のシェーディング** | <strong>マテリアル（アルベド・粗さ・法線）</strong>と、**直接光（影のレイ）・間接光**で**色を計算** |
| **④ ミス** | 何にも当たらなければ、<strong>空（スカイ）</strong> |
| **⑤ デノイズ** | **空間・時間**でノイズを消す |
| **⑥ 合成** | <strong>BRDF の積分（スケール・バイアス）</strong>を掛ける。**フォールバック**と混ぜる |

### 歴史

ゲームでのレイトレ反射の本格的な採用は、2018 年の DXR 登場と、それを使った『Battlefield V』が最初です。同じ頃、SEED の PICA PICA プロジェクトが、ハイブリッド構成（SSR で足りない部分だけレイトレ）の実用的な設計を公開しました。また、Stachowiak の "Stochastic all the things"（SIGGRAPH 2018）は、確率的なレイとデノイズで反射を出す設計を示しました。いまの商用エンジンの反射は、これらの流れの上にあります。

### 歴史

ゲームでのレイトレ反射の本格的な採用は、2018 年の DXR 登場と、それを使った『Battlefield V』が最初です。同じ頃、SEED の PICA PICA プロジェクトが、ハイブリッド構成（SSR で足りない部分だけレイトレ）の実用的な設計を公開しました。また、Stachowiak の "Stochastic all the things"（SIGGRAPH 2018）は、確率的なレイとデノイズで反射を出す設計を示しました。いまの商用エンジンの反射は、これらの流れの上にあります。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Ray Generation](ray-generation.md) | 反射レイ・粗さに応じた方向 |
| [Hit Shading and BVH](hit-shading.md) | 当たった先の色の求め方・BVH |
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
