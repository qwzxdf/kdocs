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

**光の寄与が大きい方向**を、**多めにサンプル**します。

| 方法 | 内容 |
| --- | --- |
| **余弦重み付き** | **BRDF の余弦**に従う（基本） |
| <strong>ライトのサンプリング（NEE）</strong> | **ヒット点でライトを直接サンプル**（**Next Event Estimation**） |
| **ブルー ノイズ** | **サンプルの偏りを画面全体で均す** |

### デノイズ

| 手法 | 内容 |
| --- | --- |
| **時間蓄積** | **前フレームの結果**を**再投影**して**混ぜる** |
| **空間フィルタ** | **法線・深度**を**手がかり**に**エッジ保存**で**ぼかす** |
| <strong>分散ガイド（SVGF 系）</strong> | **分散**を推定して、**ノイズの多い画素**を**強くぼかす** |
| **専用デノイザ** | <strong>NVIDIA NRD（ReBLUR・ReLAX）</strong>・**AMD FidelityFX Denoiser**・**OIDN**（オフライン向け） |
| **機械学習** | **DLSS Ray Reconstruction** など、**ニューラル ネットワークで、デノイズとアップスケールを同時に** |

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
