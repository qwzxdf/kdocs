---
title: World-Space AO Comparison
tags:
  - 描画
---

# World-Space AO Comparison

<strong>世界空間 AO の 3 方式とスクリーン空間の AO は、それぞれ得意・不得意が違います</strong>。このページでは <strong>3 方式の比較・スクリーン空間との使い分け</strong>を説明します。

!!! tip "ポイント"
    - RTAO：最も正確・ハードウェア必要・デノイズ。
    - DFAO：ハードウェア不要・静的向き。
    - VXAO：動的に強い・メモリ。
    - スクリーン空間 AOは安いが、画面外に弱い。併用も多い。

!!! info "このページを読む前に"
    - [Ray-Traced, Distance-Field and Voxel AO](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 3 方式の比較

3 つの方式は「V（遮蔽の有無）を何から求めるか」が違います。RTAO は三角形の BVH、DFAO は符号付き距離場（SDF）、VXAO はボクセルとそのミップです。

<strong>精度</strong>は RTAO が最も正確で、DFAO は SDF の解像度、VXAO はボクセルの解像度で決まります。薄い物や細部は RTAO が正確に扱えるのに対し、DFAO と VXAO は解像度の粗さのせいで潰れやすいです。<strong>ノイズ</strong>は RTAO がレイ 1〜2 本という少なさのため大きく、デノイズが必須です。DFAO と VXAO は円錐トレースなので、ノイズは小さめです。

<strong>動的なシーン</strong>への強さは VXAO が最も強く（毎フレーム再ボクセル化できる）、RTAO は BVH の更新で対応し、DFAO は SDF の更新が重いため弱いです。<strong>ハードウェア</strong>は RTAO だけがレイトレ対応 GPU を必要とします。<strong>メモリ</strong>はそれぞれ BVH、SDF のボリューム、ボクセルのボリュームを持ちます。

向く場面は RTAO は高品質・レイトレ対応の環境、DFAO は静的な屋外や広い範囲、VXAO は動的なシーンや GI との併用です。

## スクリーン空間との使い分け

広い対応環境ならスクリーン空間（[GTAO](../gtao.md) など）を選びます。画面外の遮蔽が必要で最高品質を求めるなら RTAO、広い屋外の静的な AO なら DFAO、GI とまとめて動的に扱うなら VXAO などです。

実際には<strong>併用</strong>が多いです。大きな遮蔽は世界空間の方式で、細部の接触はスクリーン空間で、というように得意な範囲を分担させます。世界空間の方式は解像度が粗く、スクリーン空間の方式は画面外を扱えないので、互いの弱点を補い合う関係になります。

## よくあるミス

??? failure "世界空間 AO だけにして、細かい接地感が足りない"
    <strong>スクリーン空間の AO（GTAO など）も併用</strong>して、<strong>細部を補う</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 3 方式は精度・必要な機能・コストが違う
    - [x] スクリーン空間と併用することが多い

## 参考

- Wright, "Dynamic Occlusion with Signed Distance Fields", SIGGRAPH 2015, Advances in Real-Time Rendering in Games（Unreal Engine 4 の DFAO）
- Crassin, Neyret, Sainz, Green, Eisemann, "Interactive Indirect Illumination Using Voxel Cone Tracing", Computer Graphics Forum (Pacific Graphics 2011)
- Barré-Brisebois, Halén, Wihlidal, Lauritzen, Bekkers, Stachowiak, Andersson, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 25, 2019
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（Ambient Occlusion の章）

## 関連ページ

- [Ray-Traced, Distance-Field and Voxel AO](index.md)
- [GTAO](../gtao.md)
- [AO Comparison](../comparison.md)
