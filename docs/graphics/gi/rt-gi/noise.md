---
title: Fighting Noise
tags:
  - 描画
---

# Fighting Noise

**画素あたり 1〜2 本のレイでは、間接光はノイズだらけ**です。**このノイズを、時間蓄積と空間フィルタで消す**のが**デノイズ**です。このページでは、**ノイズの原因と、デノイズの方針**を説明します。

!!! tip "ポイント"
    - **ノイズの原因 ＝ サンプル数が少ない**。
    - **時間蓄積：前フレームの結果と混ぜる**。
    - **空間フィルタ：法線・深度が近い画素だけ平均**。
    - **ゴーストとぼやけが、トレードオフ**。

## ノイズとの戦い
**画素あたり 1 本**のレイでは、**非常にノイズが多い**です。

### 重要度サンプリング

サンプル数が足りないなら、<strong>寄与の大きい方向に、サンプルを多く割り当てる</strong>のが、ノイズを減らす王道です。これを重要度サンプリングと呼びます。

基本は、余弦重み付きです。BRDF の余弦に従って方向を選べば、斜めの方向（寄与の小さい方向）にレイを無駄遣いしません。次に、<strong>NEE</strong>（Next Event Estimation）があります。レイがヒットした点で、ライトを直接サンプルして（シャドウ レイを光源に向けて飛ばす）、直接光を確実に拾う方法です。レイが偶然、小さな光源に当たるのを待つのでなく、光源を狙って飛ばすので、ノイズが激減します。さらに、サンプルの並べ方にも工夫が使えます。<strong>ブルー ノイズ</strong>を乱数として使うと、隣り合う画素のサンプルが偏らず、画面全体で誤差が均されます（[Noise Patterns](../../ao/filtering/noise-pattern.md)）。

### デノイズ

重要度サンプリングを使っても、1 画素 1 本のレイでは足りません。ノイズは、後処理の<strong>デノイザ</strong>で消します。主な手法は、段階的に発展してきました。

最も基本の技術は<strong>時間蓄積</strong>です。前のフレームの結果を、動きベクトルで再投影し、今のフレームと混ぜます（[Temporal Accumulation](../../ao/filtering/temporal.md)）。次に<strong>空間フィルタ</strong>で、法線と深度を手がかりに、同じ面の画素だけを平均してぼかします。この 2 つを組み合わせ、さらに「ノイズの大きさ（分散）」を推定して、ノイズが多い画素ほど強くぼかす方式が、<strong>SVGF</strong>（Spatiotemporal Variance-Guided Filtering、Schied ら 2017）です。分散ガイドのおかげで、静止した部分はシャープに、ノイズの多い部分は大きくぼかす、という切り替えが自動でできます。

実用的な製品としては、NVIDIA の <strong>NRD</strong>（ReBLUR・ReLAX）、AMD の FidelityFX Denoiser があります。オフライン向けの <strong>OIDN</strong>（Intel Open Image Denoise）は、ニューラル ネットワークでデノイズします。最近は、<strong>DLSS Ray Reconstruction</strong> のように、ニューラル ネットワークでデノイズとアップスケールを同時に行う方式も出ています。

### ゴーストとぼやけのトレードオフ

デノイズでは、ゴースト（残像）とぼやけの間で、取引が避けられません。履歴を強く使うとノイズは減りますが、動きに対して残像が出ます。履歴を弱くすると残像は減りますが、ノイズが残ります。履歴の妥当性を、法線・深度・輝度の差で検証して、怪しい履歴は捨てる、という工夫が不可欠です（[Temporal Accumulation](../../ao/filtering/temporal.md)）。

## よくあるミス

??? failure "動く光で、間接光が遅れて追いかけてくる"
    **ブレンド率を上げる**・**履歴を拒否する**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **時間蓄積と空間フィルタで、ノイズを消す**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Ray-Traced GI](index.md)
- [ReSTIR GI](restir.md)
- [AO Filtering](../../ao/filtering/index.md)
