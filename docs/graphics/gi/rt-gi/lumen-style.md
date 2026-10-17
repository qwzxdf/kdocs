---
title: Lumen-Style Approaches
tags:
  - 描画
---

# Lumen-Style Approaches

**Lumen のような方式は、シーンを簡略化した表現（距離場やサーフェス キャッシュ）でレイを飛ばし、結果をキャッシュして、再利用します**。**ハードウェアのレイトレが無くても動く**のが**特徴**です。このページでは、**この方式の構成と、利点・欠点**を説明します。

!!! tip "ポイント"
    - **シーンを簡略化して持つ**（距離場・サーフェス キャッシュ）。
    - **画面のプローブから、簡略化したシーンへトレース**。
    - **結果をキャッシュして、時間的に再利用**。
    - **ハードウェア RT が無い環境でも動く**。
    - **細部の精度は、ハードウェア RT に劣る**。

## Lumen 的な方式
**Unreal Engine 5 の Lumen**は、**ハードウェア レイトレースが無くても**動く**GI**です。**複数の手法を階層的に組み合わせて**います。

| 要素 | 内容 |
| --- | --- |
| **サーフェス キャッシュ** | <strong>メッシュの表面を小さな「カード」</strong>に**キャプチャ**し、**各カードに直接光・間接光を保存**（**ヒット点の光を安く得る**ため） |
| **距離場によるトレース** | **メッシュごとの SDF**と**グローバル SDF**で、**ソフトウェア レイトレース**（[Distance Field Shadows](../../shadows/sdf-shadows.md)） |
| <strong>画面空間トレース（最初の手段）</strong> | **近距離は画面の深度バッファ**で**精密に**トレース（[SSGI](../ssgi.md)） |
| **スクリーン プローブ** | **画面上に間引いて置いた**プローブから、**レイ**を飛ばし、**画素へ補間**（**画素ごとにレイを飛ばさない**） |
| <strong>ワールド プローブ（遠距離）</strong> | **遠くの光**は**世界空間の粗いプローブ**から |
| **HW RT モード** | **対応 GPU**では、**距離場の代わりにハードウェア レイトレース** |

<strong>「画素ごと」ではなく「間引いたプローブ」からレイを飛ばす</strong>ことで、**コストを大幅に下げ**ています。

## よくあるミス

??? failure "薄い壁や小さい物で、光漏れが起きる"
    **簡略化の精度を上げる**・**ハードウェア RT を併用**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **簡略化したシーンへトレースして、キャッシュ**
    - [x] **ハードウェア RT 無しでも動く**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Ray-Traced GI](index.md)
- [距離場 AO](../../ao/world-space/dfao.md)
- [DDGI](../ddgi.md)
