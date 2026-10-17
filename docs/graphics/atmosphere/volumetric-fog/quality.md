---
title: Quality and Performance
tags:
  - 描画
---

# Quality and Performance

**ボリューメトリック フォグは、解像度とスライス数で、品質とコストが大きく変わります**。このページでは、**品質と速度の目安**を説明します。

!!! tip "ポイント"
    - **解像度：160×90 が標準**（1080p の場合）。
    - **スライス数：64**が**標準**。
    - **ライトの数が多いと、重い**。
    - **品質設定で、解像度とスライス数を切り替える**。

## 品質と速度
品質とコストの目安です。解像度は、160×90×64 で十分で、重ければ 80×45×32 に下げます。コストは 0.3〜1 ms 程度です。局所ライトの数が多いほど重くなるので、影付きのライトは数本までに絞ります。遠距離は、範囲外を距離フォグに任せます（[Aerial Perspective and Fog](../aerial-fog/index.md)）。雲や大気との組み合わせでは、近くをボリューメトリック フォグ、遠くを空気遠近法 LUT で担当させます。

### どこでコストが決まるか

ボリューメトリック フォグのコストは、主に 3 つのパスで発生します。<strong>光の注入</strong>は、セルごとに、すべてのライトと影を評価するので、セル数 × ライト数に比例します。最も重いパスで、影付きライトの数が最大の要因です。<strong>積分</strong>は、奥行き方向の累積で、セル数に比例しますが、1 セルあたりの処理は軽く、全体で 0.1 ms 以下です。<strong>適用</strong>は、画素ごとに 3D テクスチャを 1 回引くだけで、安価です。

したがって、コストを下げたいときは、まず光の注入を見ます。影付きライトを減らす、ライトを遠くのものから省く、セル数（解像度）を下げる、のいずれかです。解像度を下げると、品質が落ちるのは主に光の筋の細かさなので、時間蓄積（[Temporal Accumulation](temporal.md)）で補うと、見た目を保ちながら軽くできます。

### 範囲の選び方

froxel は、カメラの前方のごく近い範囲だけを覆うのが現実的です。たとえば最大距離を 64〜128 m にすれば、64 スライスで十分な密度が出ます。それより遠くは、空気遠近法の LUT で連続的につなぎます。境目で急に変わらないよう、最大距離の手前でボリューメトリック フォグの寄与をフェードアウトさせ、遠景のフォグと重ねます。

## よくあるミス

??? failure "フォグの計算が重く、フレーム時間が伸びる"
    **解像度・スライス数を下げる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **解像度とスライス数で、調整**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Volumetric Fog](index.md)
- [Froxels](froxel.md)
