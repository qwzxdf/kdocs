---
title: Tuning the Look
tags:
  - 描画
---

# Tuning the Look

**光の筋は、強すぎると、わざとらしく見えます**。**強さ・色・ノイズを調整**して、**自然に**します。このページでは、**見た目の調整**を説明します。

!!! tip "ポイント"
    - **強さは、控えめに**。
    - **色は、太陽の色に合わせる**。
    - **ノイズで、筋にむらを付ける**。
    - **天気（晴れ・霧）で、強さを変える**。

## 見た目の調整
| パラメータ | 影響 |
| --- | --- |
| **霧の密度** | **濃いほど光の筋が強い** |
| **位相関数の g** | **大きいほど、太陽の方向でだけ見える** |
| **光の強さ** | **HDR で強く、ブルームで光らせる** |
| **色** | **朝夕は暖色、昼は白、水中は青緑** |
| **ノイズ・風** | **揺らぎを足す** |
| **カメラが太陽側へ向くとき強く** | **前方散乱** |

## よくあるミス

??? failure "光の筋が強すぎて、画面が白っぽい"
    **強さを下げる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **控えめな強さと、ノイズのむら**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [God Rays](index.md)
- [Bloom](../../postprocess/bloom/index.md)
