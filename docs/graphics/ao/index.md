---
title: Ambient Occlusion (AO)
tags:
  - 描画
---

# Ambient Occlusion (AO)

**環境光遮蔽**（Ambient Occlusion、AO）は、<strong>「周囲から届く光が近くの物体に遮られて、どれだけ暗くなるか」</strong>を表す量です。部屋の隅・物の接地面・壁と床の境目が暗く見えるのは、周囲の空（天球）の光がそこには届きにくいからです。ライトの種類や位置には関係なく、**形だけから**決まります。ゲームでは**間接光（環境光）の項**に掛ける係数として使い、画面に**奥行きと接地感**を足します。

このセクションでは、AO を**方式ごとに**扱います。最初に「AO とは何を計算しているのか」を式で整理し（[理論](theory/index.md)）、そのあと画面の深度バッファだけで近似する**スクリーン空間**の方式（SSAO・Alchemy・SAO・HBAO・HBAO+・GTAO）を、**古い方式から順**に**何を改善したのか**を追いながら見ます。

!!! tip "ポイント"
    - AO ＝ <strong>可視な半球の割合（コサイン重み）</strong>。<strong>式は 1 つ</strong>。方式の違いは<strong>その積分をどう安く近似するか</strong>。
    - スクリーン空間 AO（SSAO 系）は<strong>深度バッファ（と法線）</strong>から計算。<strong>ライトに依存せず、ジオメトリを増やさない</strong>。
    - 古い順に<strong>Crytek SSAO → 半球 SSAO → Alchemy → SAO → HBAO → HBAO+ → GTAO</strong>。<strong>精度（コサイン重み・地平線）と速さ（キャッシュ・ミップ）の両面</strong>で進化。
    - どの方式も<strong>見えない情報を持たない</strong>：<strong>画面外・隠れた物・薄い物</strong>で破綻する。
    - サンプル数を減らして<strong>ノイズ＋ぼかし（時間方向の再利用）</strong>で補うのが前提。
    - 画面に頼らない方式：<strong>レイトレ AO・距離場 AO・ボクセル AO</strong>。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [AO Theory](theory/index.md) | AO の定義・積分・コサイン重み・オブスキュランス・近似の分類 |
| [Crytek SSAO](ssao-crytek.md) | 最初の SSAO。深度バッファと球サンプルで近似する発想 |
| [Hemisphere SSAO](ssao-hemisphere.md) | 法線を使った半球サンプル。現在の「標準的な SSAO」 |
| [Alchemy AO](alchemy-ao.md) | AO の式を解析的に近似。物理的な導出がある方式 |
| [SAO（Scalable AO）](sao.md) | Alchemy ＋ 深度のミップ。半径に依存しない速さ |
| [HBAO](hbao.md) | 地平線（ホライゾン）を探して、遮蔽を積分する方式 |
| [HBAO+](hbao-plus.md) | NVIDIA の高速版。フル解像度・キャッシュ効率 |
| [GTAO](gtao.md) | コサイン重みを正しく積分する。バウンス・スペキュラ遮蔽も |
| [Ray-Traced, Distance-Field and Voxel AO](world-space/index.md) | 画面に頼らない方式 |
| [フィルタ（ぼかし・時間方向）](filtering/index.md) | バイラテラル ブラー・アップサンプル・ノイズ・時間蓄積 |
| [方式の比較](comparison.md) | 原理・入力・コスト・弱点の一覧と選び方 |
| [アーティファクト](artifacts/index.md) | ハロー・画面端・薄い物・自己遮蔽・適用方法の間違い |

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

## 関連ページ

- [描画](../index.md)
- [AO Theory](theory/index.md)
- [法線とライティング](../../3d/lighting-normals.md)
- [PBR（IBL と AO の使い方）](../../3d/pbr.md)
- [低解像度のエフェクト](../../rendering/low-res-effects.md)
