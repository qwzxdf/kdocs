---
title: World-Space AO Comparison
tags:
  - 描画
---

# World-Space AO Comparison

**世界空間 AO の 3 方式と、スクリーン空間の AO は、それぞれ得意・不得意が違います**。このページでは、**3 方式の比較・スクリーン空間との使い分け**を説明します。

!!! tip "ポイント"
    - **RTAO**：**最も正確・ハードウェア必要・デノイズ**。
    - **DFAO**：**ハードウェア不要・静的向き**。
    - **VXAO**：**動的に強い・メモリ**。
    - **スクリーン空間 AO**は**安いが、画面外に弱い**。**併用**も**多い**。

## 3 方式の比較

3 つの方式は、「V（遮蔽の有無）を何から求めるか」が違います。RTAO は三角形の BVH、DFAO は符号付き距離場（SDF）、VXAO はボクセルとそのミップです。

<strong>精度</strong>は、RTAO が最も正確で、DFAO は SDF の解像度、VXAO はボクセルの解像度で決まります。薄い物や細部は、RTAO が正確に扱えるのに対し、DFAO と VXAO は解像度の粗さのせいで潰れやすいです。<strong>ノイズ</strong>は、RTAO がレイ 1〜2 本という少なさのため大きく、デノイズが必須です。DFAO と VXAO は円錐トレースなので、ノイズは小さめです。

<strong>動的なシーン</strong>への強さは、VXAO が最も強く（毎フレーム再ボクセル化できる）、RTAO は BVH の更新で対応し、DFAO は SDF の更新が重いため弱いです。<strong>ハードウェア</strong>は、RTAO だけがレイトレ対応 GPU を必要とします。<strong>メモリ</strong>は、それぞれ BVH、SDF のボリューム、ボクセルのボリュームを持ちます。

向く場面は、RTAO は高品質・レイトレ対応の環境、DFAO は静的な屋外や広い範囲、VXAO は動的なシーンや GI との併用です。

## スクリーン空間との使い分け

広い対応環境なら、スクリーン空間（[GTAO](../gtao.md) など）を選びます。画面外の遮蔽が必要で最高品質を求めるなら RTAO、広い屋外の静的な AO なら DFAO、GI とまとめて動的に扱うなら VXAO などです。

実際には<strong>併用</strong>が多いです。大きな遮蔽は世界空間の方式で、細部の接触はスクリーン空間で、というように、得意な範囲を分担させます。世界空間の方式は解像度が粗く、スクリーン空間の方式は画面外を扱えないので、互いの弱点を補い合う関係になります。

## よくあるミス

??? failure "世界空間 AO だけにして、細かい接地感が足りない"
    **スクリーン空間の AO（GTAO など）も併用**して、**細部を補う**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **3 方式は、精度・必要な機能・コストが違う**
    - [x] **スクリーン空間と併用することが多い**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [世界空間 AO](index.md)
- [GTAO](../gtao.md)
- [方式の比較](../comparison.md)
