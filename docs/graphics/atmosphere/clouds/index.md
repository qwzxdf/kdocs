---
title: 雲
tags:
  - 描画
---

# 雲

**雲は、空の表情を決める大事な要素**で、**本格的には、3D のノイズで密度を持ち、レイマーチで描きます**。**重いので、時間蓄積などの高速化が必須**です。このセクションでは、**描き方の段階・雲の層・密度のモデル・レイマーチ・光の計算・影・高速化・簡易な代替**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **雲 ＝ 3D の密度場**。
    - **レイマーチで、密度を積分して描く**。
    - **光の計算（散乱・自己影）が、見た目の鍵**。
    - **時間蓄積で、重さを抑える**。

## 雲の描き方の段階
| 方式 | 内容 | 特徴 |
| --- | --- | --- |
| **スカイボックスの絵** | **雲の絵を空に貼る** | **最も安い。動かない・光が変わらない** |
| <strong>板ポリ（ビルボード）</strong> | **雲の絵を貼った板を空に多数置く** | **動かせる。近づくと板だと分かる** |
| <strong>レイマーチ（ボリューム）</strong> | **雲の体積を視線に沿って積分** | **リアル。重い** |

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [雲の層](layers.md) | 高度ごとの雲の種類 |
| [密度のモデル](density-model.md) | ノイズで形を作る |
| [レイマーチ](raymarch.md) | 視線に沿って進む |
| [光の計算](lighting.md) | 散乱・自己影 |
| [雲の影](shadows.md) | 地上に落ちる影 |
| [高速化：時間蓄積](temporal.md) | 少ないサンプルを重ねる |
| [簡易な代替](cheap.md) | スカイボックス・ビルボード |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **雲は、3D の密度をレイマーチで描く**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [大気](../index.md)
- [空のモデル](../sky-models/index.md)
- [大気散乱](../scattering/index.md)
