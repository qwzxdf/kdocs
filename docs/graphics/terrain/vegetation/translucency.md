---
title: Foliage Translucency
tags:
  - 描画
---

# Foliage Translucency

**葉は、ソートできないほど多いので、通常の半透明は使えません**。**アルファ テスト・Alpha to Coverage・ハッシュド アルファ**で**対処**します。このページでは、**葉の半透明の問題と対策**を説明します。

!!! tip "ポイント"
    - **半透明ブレンドは、ソートが必要で、葉には不向き**。
    - **アルファ テストで、切り抜く**。
    - **遠くで細る問題は、アルファの補正で対処**。
    - **A2C やハッシュドで、縁をなめらかに**。

## 半透明の問題
**草と葉はアルファ テスト（切り抜き）で描きます**。**半透明ブレンドは、ソートが要るので不向き**です。

| 問題 | 対策 |
| --- | --- |
| **ジャギー** | **A2C（Alpha To Coverage）＋ MSAA**。**または TAA で滑らかに** |
| **遠くで草が痩せる** | **ミップでアルファが薄まる**。**ミップごとにアルファを補正**（[Alpha Testing](../../translucency/alpha-test/index.md)） |
| **裏面が暗い／明るい** | **両面描画で裏面の法線を反転**。**葉の透過光を足す** |

## よくあるミス

??? failure "遠くの木の葉が、スカスカに見える"
    **ミップごとにアルファを補正**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **葉は、アルファ テスト系で処理**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Vegetation](index.md)
- [Alpha Testing](../../translucency/alpha-test/index.md)
