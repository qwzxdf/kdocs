---
title: Ambient Occlusion (AO)
tags:
  - 描画
---

# Ambient Occlusion (AO)

<strong>環境光遮蔽</strong>（Ambient Occlusion、AO）は、<strong>「周囲から届く光が近くの物体に遮られて、どれだけ暗くなるか」</strong>を表す量です。部屋の隅・物の接地面・壁と床の境目が暗く見えるのは、周囲の空（天球）の光がそこには届きにくいからです。ライトの種類や位置には関係なく、<strong>形だけから</strong>決まります。ゲームでは間接光（環境光）の項に掛ける係数として使い、画面に奥行きと接地感を足します。

このセクションでは、AO を<strong>方式ごとに</strong>扱います。最初に「AO とは何を計算しているのか」を式で整理し（[理論](theory/index.md)）、そのあと画面の深度バッファだけで近似する<strong>スクリーン空間</strong>の方式（SSAO・Alchemy・SAO・HBAO・HBAO+・GTAO）を、古い方式から順に何を改善したのかを追いながら見ます。

## AO を学ぶ順番

方式が多く、名前も似ているので、迷いやすい分野です。次の順で読むと、それぞれの方式が「前の方式の何を直したのか」が分かり、自然に頭に入ります。

最初に[理論](theory/index.md)で、AO が何を計算しているのか（遮られていない方向の割合）を押さえます。式を暗記する必要はありません。「コサイン重み」「半径」「画面の深度しか知らない」という 3 つの言葉の意味が分かれば十分です。次に、最初の SSAO である [Crytek SSAO](ssao-crytek.md) を読み、「深度バッファのサンプル点が面の奥にあれば遮蔽」という発想と、平らな面が灰色になる弱点を知ります。それを直した [Hemisphere SSAO](ssao-hemisphere.md) が、実装の出発点になります。

ここから先は、目的で分かれます。精度を追うなら [HBAO](hbao.md) から [GTAO](gtao.md) へ。速さを追うなら [Alchemy AO](alchemy-ao.md) から [SAO](sao.md)、[HBAO+](hbao-plus.md) へ。どちらの道でも、[AO Filtering](filtering/index.md) のノイズ除去が必須です。ノイズを抑えられなければ、どの方式でも使い物になりません。最後に、画面に頼らない[世界空間の方式](world-space/index.md)と、[方式の比較](comparison.md)で全体を整理します。不具合が出たときは、[AO Artifacts](artifacts/index.md) を症状から引いてください。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [AO Theory](theory/index.md) | AO の定義・積分・コサイン重み・オブスキュランス・近似の分類 |
| [Crytek SSAO](ssao-crytek.md) | 最初の SSAO。深度バッファと球サンプルで近似する発想 |
| [Hemisphere SSAO](ssao-hemisphere.md) | 法線を使った半球サンプル。現在の「標準的な SSAO」 |
| [Alchemy AO](alchemy-ao.md) | AO の式を解析的に近似。物理的な導出がある方式 |
| [SAO (Scalable AO)](sao.md) | Alchemy ＋ 深度のミップ。半径に依存しない速さ |
| [HBAO](hbao.md) | 地平線（ホライゾン）を探して、遮蔽を積分する方式 |
| [HBAO+](hbao-plus.md) | NVIDIA の高速版。フル解像度・キャッシュ効率 |
| [GTAO](gtao.md) | コサイン重みを正しく積分する。バウンス・スペキュラ遮蔽も |
| [Ray-Traced, Distance-Field and Voxel AO](world-space/index.md) | 画面に頼らない方式 |
| [AO Filtering](filtering/index.md) | バイラテラル ブラー・アップサンプル・ノイズ・時間蓄積 |
| [AO Comparison](comparison.md) | 原理・入力・コスト・弱点の一覧と選び方 |
| [AO Artifacts](artifacts/index.md) | ハロー・画面端・薄い物・自己遮蔽・適用方法の間違い |

## 時間の流れで見る AO

<div class="anim" data-type="graph" data-label="スクリーン空間 AO の系譜">
n a Crytek_SSAO 0 0 new
n b 半球_SSAO 1 0
n c Alchemy_AO 2 0
n d SAO 3 0
n e HBAO 1.5 1.5
n f HBAO+ 2.5 1.5
n g GTAO 3.5 1.5 new
l a b - 法線を使う
l b c - 式を導出
l c d - ミップで速く
l a e - 地平線を探す
l e f - 高速化
l e g - コサイン重みを正しく
</div>

## 参考

- Landis, "Production-Ready Global Illumination", SIGGRAPH 2002 Course 16（ambient occlusion の、映画制作での、使われ方）
- Zhukov, Iones, Kronin, "An Ambient Light Illumination Model", Rendering Techniques '98（Eurographics Workshop on Rendering 1998）（obscurance の原典）
- Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games
- Bavoil, Sainz, Dimitrov, "Image-Space Horizon-Based Ambient Occlusion", SIGGRAPH 2008 Talks
- Jimenez, Wu, Pesce, Jarabo, "Practical Real-Time Strategies for Accurate Indirect Occlusion", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（Ambient Occlusion の章）

## 関連ページ

- [シェーダー](../index.md)
- [AO Theory](theory/index.md)
- [法線とライティング](../../3d/lighting-normals.md)
- [PBR（物理ベースレンダリング）](../../3d/pbr.md)
- [縮小バッファの効果](../../rendering/low-res-effects.md)
- [描画最適化](../../rendering/index.md)
