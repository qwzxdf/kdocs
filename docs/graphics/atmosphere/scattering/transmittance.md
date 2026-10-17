---
title: 透過率
tags:
  - 描画
---

# 透過率

**光が大気を通ると、散乱や吸収で弱まります**。**弱まる割合が透過率で、Beer の法則（指数）で表します**。このページでは、**透過率の計算**を説明します。

!!! tip "ポイント"
    - **透過率 ＝ exp(−∫ 消散係数 ds)**。
    - **波長（RGB）ごとに計算**する。
    - **長い道のり ＝ 低い太陽 ＝ 赤くなる**（青が先に消える）。
    - **LUT に事前計算しておく**と**速い**。

## 透過率
**光が距離 d を進むと、強さは指数的に減ります**（Beer–Lambert の法則）。

<div class="formula">T(a → b) = exp( −∫ σt(s) ds )　（光学的厚さ τ = ∫ σt ds）</div>

```hlsl
float3 Transmittance(float3 start, float3 end, int steps) {
  float3 delta = (end - start) / steps;
  float step_length = length(delta);
  float3 optical_depth = 0;
  for (int i = 0; i < steps; ++i) {
    float3 p = start + delta * (i + 0.5);
    float h = length(p) - kPlanetRadius;
    float3 extinction = kRayleighScattering * exp(-h / kRayleighScaleHeight)
                      + kMieExtinction * exp(-h / kMieScaleHeight)
                      + kOzoneAbsorption * OzoneDensity(h);
    optical_depth += extinction * step_length;
  }
  return exp(-optical_depth);
}
```

| 点 | 説明 |
| --- | --- |
| **中点法** | **各区間の中点で密度を取る** |
| **色ごとに別の値** | **RGB の消散係数が違う → 青が先に減る** |
| **球の外・内** | <strong>地面にぶつかる向きは、光が届かない（T = 0 扱い）</strong> |

## よくあるミス

??? failure "日没の太陽が、白いまま"
    **透過率を RGB ごと**に**計算**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **距離と係数で、指数で減衰する**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [大気散乱](index.md)
- [大気のモデル](atmosphere-model.md)
- [単散乱](single-scattering.md)
