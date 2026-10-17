---
title: Volume-Based God Rays
tags:
  - 描画
---

# Volume-Based God Rays

**ボリューメトリック フォグの froxel を使うと、ゴッド レイも自然に得られます**。**光の注入の段階で、シャドウを参照するだけ**で、**複数のライトにも対応**します。このページでは、**ボリュームを使った方法**を説明します。

!!! tip "ポイント"
    - **froxel の光の注入で、影を参照するだけ**。
    - **複数のライトで、筋が出る**。
    - **フォグを使うなら、追加コストがほぼ無い**。
    - **解像度が低いので、細い筋は出にくい**。

## ボリュームを使う方法
**ボリューメトリック フォグ**（[Volumetric Fog](../volumetric-fog/index.md)）を**使っていれば、光の筋は自動で出ます**。**froxel に太陽光とシャドウを注入**しているため、**影による筋が自然に現れます**。**別途レイマーチを用意する必要はありません**。

| 状況 | おすすめ |
| --- | --- |
| **ボリューメトリック フォグを使っている** | <strong>それを使う（自動）</strong> |
| **光の筋だけ欲しい** | **シャドウ マップのレイマーチ** |
| **とにかく軽く** | **放射ぼかし** |
| **固定の窓の光** | **メッシュの光の柱** |

## よくあるミス

??? failure "細い光の筋が、ぼやける"
    **froxel の解像度を上げる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **フォグのボリュームに、影を入れるだけ**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [God Rays](index.md)
- [Volumetric Fog](../volumetric-fog/index.md)
