---
title: Sun Inscatter
tags:
  - 描画
---

# Sun Inscatter

**太陽の方向を見ると、フォグが明るく黄色っぽく霞みます**。**視線と太陽の方向が近いほど、フォグの色を太陽の色に寄せる**と、**自然**です。このページでは、**太陽方向のにじみ**を説明します。

!!! tip "ポイント"
    - **視線と太陽の内積で、フォグの色を変える**。
    - **太陽側は、暖色・明るい**。
    - **反対側は、空の青**。
    - **ミー散乱の前方散乱に対応**。

## 太陽方向のにじみ
**太陽の方向を見ると霧が明るく・暖色に光ります**（**前方散乱**）。**フォグの色を視線と太陽の角度で変えます**。

```hlsl
float sun_amount = saturate(dot(view_dir, sun_dir));
float3 fog_color_dir = lerp(fog_color, sun_fog_color, pow(sun_amount, 8.0));
```

| 点 | 説明 |
| --- | --- |
| **`pow(.., 8)`** | **太陽のすぐ周りだけ** |
| **ミー散乱の位相関数** | **より正確には、Henyey-Greenstein**（[Atmospheric Scattering](../scattering/index.md)） |
| **夕方** | **太陽側が赤橙、反対側が青紫**になる |

## よくあるミス

??? failure "太陽の方向でも、フォグが青いまま"
    **太陽方向の色**を**足す**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **太陽の方向で、フォグの色を変える**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Aerial Perspective and Fog](index.md)
- [Phase Functions](../scattering/phase-function.md)
