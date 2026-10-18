---
title: Cheap Alternatives
tags:
  - 描画
---

# Cheap Alternatives

**レイマーチが重い環境では、簡易な代替があります**。**スカイボックスのテクスチャ・ビルボード・平面に貼る雲**などで、**雰囲気を出します**。このページでは、**簡易な雲の表現**を説明します。

!!! tip "ポイント"
    - **スカイボックスに、雲を描いておく**。
    - **平面に、雲のテクスチャを流す**（スクロール）。
    - **ビルボードの雲**を配置する。
    - **モバイルでは、これが標準**。

## Simple Alternatives {#簡易な代替}
**重いレイマーチが使えない場面**の**代替**です。

| 方式 | 内容 |
| --- | --- |
| **雲のスカイボックス** | **事前に描いた雲のキューブマップを回す** |
| <strong>2D の雲（スカイドームの絵）</strong> | **スクロールする雲のテクスチャ ＋ 法線マップで凹凸** |
| **フローマップで動かす** | **雲の絵を流れの向きに動かす**（[水のフローマップ](../../water/interaction/index.md)） |
| <strong>ボリューム テクスチャ（事前焼き）</strong> | **雲の塊を 3D テクスチャに焼き、ビルボードで描く** |
| <strong>雲の板（インポスター）</strong> | **遠景の雲を板で置く** |

### Which One to Choose {#どれを選ぶか}

簡易な方式の選択は、「雲をどれだけ近くから見るか」で決まります。地上の視点から、ほぼ動かない遠くの空として見るだけなら、スカイボックスか 2D のスクロールで十分です。2D の雲に<strong>視差</strong>（視点移動で見え方が変わる効果）を足したければ、雲の高さのテクスチャをもとに、視線の方向に UV をずらす「パララックス マッピング」を雲のドームに適用します。雲の層を 2〜3 枚、高さを変えて重ねれば、奥行きが生まれます。

飛行機や気球のように、雲に近づく、雲の中を通る場面があるなら、板では限界があります。その場面だけ、ボリューム テクスチャを貼ったビルボードか、本物のレイマーチに切り替えます。近づくほど板が分かりやすくなるので、見る距離に応じて方式を切り替える（LOD）設計が現実的です。

モバイルでは、スカイボックスと 2D の雲が標準的な選択です。これに時刻に応じた色の変化（ライティングの色を空の色に合わせる）を足せば、静的な絵でも、昼から夕方への移り変わりを違和感なく表現できます。

## Common Mistakes {#よくあるミス}

??? failure "簡易な雲が、動かず、不自然"
    **テクスチャを、ゆっくりスクロール**させる。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **重い環境では、テクスチャとビルボードで代替**

## References {#参考}

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## Related Pages {#関連ページ}

- [Clouds](index.md)
- [Gradient Sky](../sky-models/gradient.md)
