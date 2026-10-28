---
title: Ray-Traced Reflections
tags:
  - 描画
---

# Ray-Traced Reflections

<strong>レイトレ反射は GPU のレイトレーシング機能で、実際にシーンへレイを飛ばして、反射を求める手法</strong>です。<strong>画面の外の物も隠れた物も正確に映せます</strong>が、コストが高くノイズも出るので、工夫が必要です。このセクションでは SSR との違い・レイの生成・ヒット点のシェーディング・ハイブリッド構成・ノイズ除去を 1 つずつ別のページで説明します。

## SSR との違い
| 項目 | SSR | レイトレ反射 |
| --- | --- | --- |
| 探索の相手 | 深度バッファ（画面） | <strong>BVH（シーンの三角形）</strong> |
| 画面外・裏側 | 映らない | 映る |
| 半透明の向こう | 映らない | 映る（any-hit） |
| 反射の中の反射 | 不可（または 1 回だけ） | 再帰で可能（コスト増） |
| 必要な機能 | 深度・色 | レイトレ対応 GPU・BVH |
| ヒット点の色 | 画面の画像から取る | マテリアルと光をその場で評価 |
| コスト | 中 | 大 |

## 全体の流れ
| パス | 内容 |
| --- | --- |
| ① レイの生成 | G-Buffer から、位置・法線・粗さを得て GGX VNDF で方向を選ぶ |
| ② BVH のトレース | `TraceRay`（または `RayQuery`）で、最も近い交点を求める |
| ③ ヒット点のシェーディング | <strong>マテリアル（アルベド・粗さ・法線）</strong>と、直接光（影のレイ）・間接光で色を計算 |
| ④ ミス | 何にも当たらなければ、<strong>空（スカイ）</strong> |
| ⑤ デノイズ | 空間・時間でノイズを消す |
| ⑥ 合成 | <strong>BRDF の積分（スケール・バイアス）</strong>を掛ける。フォールバックと混ぜる |

### 歴史

ゲームでのレイトレ反射の本格的な採用は、2018 年の DXR 登場と、それを使った『Battlefield V』が最初です。同じ頃、SEED の PICA PICA プロジェクトがハイブリッド構成（SSR で足りない部分だけレイトレ）の実用的な設計を公開しました。また、Stachowiak の "Stochastic all the things"（SIGGRAPH 2018）は、確率的なレイとデノイズで反射を出す設計を示しました。いまの商用エンジンの反射はこれらの流れの上にあります。

### 歴史

ゲームでのレイトレ反射の本格的な採用は、2018 年の DXR 登場と、それを使った『Battlefield V』が最初です。同じ頃、SEED の PICA PICA プロジェクトがハイブリッド構成（SSR で足りない部分だけレイトレ）の実用的な設計を公開しました。また、Stachowiak の "Stochastic all the things"（SIGGRAPH 2018）は、確率的なレイとデノイズで反射を出す設計を示しました。いまの商用エンジンの反射はこれらの流れの上にあります。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Ray Generation](ray-generation.md) | 反射レイ・粗さに応じた方向 |
| [Hit Shading and BVH](hit-shading.md) | 当たった先の色の求め方・BVH |
| [Hybrid Pipeline](hybrid.md) | SSR とレイトレの組み合わせ・性能の工夫 |
| [Denoising](denoise.md) | デノイズ・長所と短所 |

## レイトレーシングで反射を描く

<strong>ハードウェア レイトレーシング</strong>（DXR）を使うと、<strong>反射</strong>を実際の三角形にレイを飛ばして正確に求められます。SSR の限界（画面の外、隠れた面）がありません。反射の反射（多重反射）、屈折、ガラスの反射も自然に扱えます。

## 基本の流れ

```text
各画素（反射する面）から、反射方向に、レイを、飛ばす（DXR の TraceRay）
   ↓ 当たった面の、色を、求める（ヒット シェーダー）
当たった面の、ライティング（直接光 + 影レイ）+ 当たった面が、さらに、反射するなら、もう一度、レイ
   ↓
ノイズを、取る（デノイズ）→ 反射を、画面に、合成
```

## 構成要素

| 要素 | 内容 | ページ |
| --- | --- | --- |
| レイの生成 | どの画素から、どの方向にレイを飛ばすか（粗さに応じた、分布） | [Ray Generation](ray-generation.md) |
| ヒット シェーディング | 当たった面の色を求める。BVH（加速構造）の管理 | [Hit Shading and BVH](hit-shading.md) |
| ハイブリッド | SSR と、レイトレーシングの組み合わせ（画面内は SSR、外れたら RT） | [Hybrid Pipeline](hybrid.md) |
| デノイズ | ノイズを取り除く | [Denoising](denoise.md) |

## SSR との比較

| | SSR | レイトレーシング（RT） |
| --- | --- | --- |
| 画面の外の物 | ×（映らない） | ○（映る） |
| 隠れた面（物の裏） | ×（穴があく） | ○（正確） |
| 反射の反射 | △（前フレームの色で、近似） | ○（正確。再帰） |
| ガラスの屈折・反射 | ×（簡易） | ○（レイを屈折・反射させられる） |
| コスト | 中 | 大（レイ、BVH、シェーディング） |
| 必要なハードウェア | 不要（どの GPU でも） | DXR 対応の GPUが必要 |
| ノイズ | 中（粗い面） | 大（粗い面はレイが散らばる） |
| 実装の難しさ | 中 | 高（BVH、シェーダー テーブル、デノイズ） |

## RT 反射の現実的な使い方

<strong>フルスクリーンの RT 反射</strong>は、<strong>重い</strong>ので工夫して使います。

| 工夫 | 内容 |
| --- | --- |
| ハイブリッド | SSR で、取れる画素は SSR（安い）、取れなかった画素だけ RT（[Hybrid Pipeline](hybrid.md)） |
| 反射が強い（つるつるの）面だけ、RT | 粗い面や非金属は反射プローブで、十分 |
| 半分の解像度で RT | レイ数が 1/4。アップサンプルしてデノイズ |
| レイの最大距離を短く | 遠くは、プローブに任せる |
| ヒット シェーディングを簡略化 | 当たった面は低品質なシェーディング（影なし、簡易ライティング） |

## DirectX 11 では動かない部分

<strong>DXR（DirectX Raytracing）は、DirectX 12 の機能です。DirectX 11 にはありません。</strong>このページの `TraceRay`・`RayQuery` を使うコードは、D3D12 のレンダラーで動かします。D3D11 だけで同じ効果を狙うときは、次のように置き換えます。

| やりたいこと | D3D11 での代用 |
| --- | --- |
| レイと三角形の交差 | 距離場（SDF）・ボクセル、またはスクリーン空間のレイマーチ（[Linear Marching](../../reflections/ssr-basics/linear-march.md)） |
| 影 | シャドウ マップ（[Shadow Map Basics](../../shadows/shadow-map-basics/index.md)） |
| 間接光 | ライトマップ・プローブ・SSGI・ボクセル GI（[Global Illumination (GI)](../../gi/index.md)） |

D3D12 側の初期化（加速構造・ステート オブジェクト・シェーダー テーブル・`DispatchRays`）は、[DXR Host Setup](../../../directx/dx12/dxr-host.md) に、まとめています。

## これだけ覚える

!!! abstract "まとめ"
    - [x] レイトレ反射は、正確だが重い
    - [x] ハイブリッドとデノイズで、実用にする

## 参考

- Microsoft, "DirectX Raytracing (DXR) Functional Spec"
- Stachowiak, "Stochastic All The Things: Raytracing in Hybrid Real-Time Rendering", Digital Dragons 2018
- Barré-Brisebois, Halén, Wihlidal, Lauritzen, Bekkers, Stachowiak, Andersson, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 25, 2019
- Schied et al., "Spatiotemporal Variance-Guided Filtering: Real-Time Reconstruction for Path-Traced Global Illumination", High-Performance Graphics 2017
- Heitz, "Sampling the GGX Distribution of Visible Normals", Journal of Computer Graphics Techniques, Vol. 7, No. 4, 2018

## 関連ページ

- [Reflections](../index.md)
- [SSR Basics](../ssr-basics/index.md)
- [Ray-Traced GI](../../gi/rt-gi/index.md)
