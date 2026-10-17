---
title: フォグの色を空に合わせる
tags:
  - 描画
---

# フォグの色を空に合わせる

**フォグの色が、地平線の空の色と違うと、地平線に境目が見えて、不自然**です。**フォグの色を、空の色から取る**ことで、**自然につながります**。このページでは、**フォグの色の決め方**を説明します。

!!! tip "ポイント"
    - **地平線の空の色を、フォグの色にする**。
    - **空のキューブマップの低いミップを使う**。
    - **時刻とともに、自動で変わる**。
    - **夜は、暗い青に**。

## フォグの色を空に合わせる
**フォグの色が空と違う**と、<strong>遠景の山が「浮いて」</strong>見えます。

| 方法 | 内容 |
| --- | --- |
| **空の色を引いてくる** | **視線の向きの空の色**（スカイビュー LUT など）を**フォグの色に使う**（地平線付近の色） |
| **環境マップの低ミップ** | **環境マップの平均色／視線方向の粗いミップ**を引く |
| **手動設定** | **時間帯ごとに色を設定し補間** |

## よくあるミス

??? failure "遠景と空の間に、境目が見える"
    **フォグの色を、空から取る**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **空の色を取って、フォグの色にする**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [空気遠近法・フォグ](index.md)
- [空のモデル](../sky-models/index.md)
