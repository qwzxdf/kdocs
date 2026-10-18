---
title: Clouds
tags:
  - 描画
---

# Clouds

**雲は、空の表情を決める大事な要素**で、**本格的には、3D のノイズで密度を持ち、レイマーチで描きます**。**重いので、時間蓄積などの高速化が必須**です。このセクションでは、**描き方の段階・雲の層・密度のモデル・レイマーチ・光の計算・影・高速化・簡易な代替**を、**1 つずつ別のページ**で説明します。

## 雲の描き方の段階
| 方式 | 内容 | 特徴 |
| --- | --- | --- |
| **スカイボックスの絵** | **雲の絵を空に貼る** | **最も安い。動かない・光が変わらない** |
| <strong>板ポリ（ビルボード）</strong> | **雲の絵を貼った板を空に多数置く** | **動かせる。近づくと板だと分かる** |
| <strong>レイマーチ（ボリューム）</strong> | **雲の体積を視線に沿って積分** | **リアル。重い** |

## 現代のボリューメトリック クラウドの流れ

現在のゲームで標準になっているボリューメトリック クラウドは、Schneider の "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）と、その後の改良（"Nubis"、2017 年以降）が土台です。考え方は次のとおりです。

雲の形は、<strong>低解像度の 3D ノイズ</strong>（雲の基本形）と<strong>高解像度の 3D ノイズ</strong>（縁の細かい凹凸）を組み合わせ、さらに<strong>カバレッジ マップ</strong>（どこに雲があるか）と<strong>高度プロファイル</strong>（高さごとの雲の種類）で形作ります（[Cloud Density Model](density-model.md)）。描画は、視線に沿ったレイマーチで、密度を積分します（[Cloud Raymarching](raymarch.md)）。各サンプルで、太陽方向にも短くマーチして、光の減衰を求めます（[Cloud Lighting](lighting.md)）。そして、これを毎フレーム全画素でやるのは重すぎるので、<strong>時間をかけて少しずつ更新</strong>します（[Cloud Temporal Reprojection](temporal.md)）。

この流れは、単純なパーツの組み合わせでできていて、パーツごとに独立して調整できるのが強みです。形はノイズとカバレッジ、光は Beer の法則と位相関数、速さは時間蓄積、という具合に、見た目の問題を担当するパーツに切り分けて考えられます。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Cloud Layers](layers.md) | 高度ごとの雲の種類 |
| [Cloud Density Model](density-model.md) | ノイズで形を作る |
| [Cloud Raymarching](raymarch.md) | 視線に沿って進む |
| [Cloud Lighting](lighting.md) | 散乱・自己影 |
| [Cloud Shadows](shadows.md) | 地上に落ちる影 |
| [Cloud Temporal Reprojection](temporal.md) | 少ないサンプルを重ねる |
| [Cheap Alternatives](cheap.md) | スカイボックス・ビルボード |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **雲は、3D の密度をレイマーチで描く**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Sky and Atmosphere](../index.md)
- [Sky Models](../sky-models/index.md)
- [Atmospheric Scattering](../scattering/index.md)
