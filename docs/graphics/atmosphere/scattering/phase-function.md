---
title: 位相関数
tags:
  - 描画
---

# 位相関数

**光が散乱される時、どの方向へ散るかを表すのが位相関数**です。**レイリーは前後に均等、ミーは前方に強く偏ります**。このページでは、**位相関数**を説明します。

!!! tip "ポイント"
    - **レイリー：(1 + cos²θ) に比例**。
    - **ミー：Henyey-Greenstein などで、前方に偏る**。
    - **ミーの偏り g は、約 0.76〜0.8**。
    - **太陽の周りが、白くにじむのは、ミーの前方散乱**。

## 位相関数
<strong>位相関数 P(θ)</strong> は、**散乱の方向分布**です。**θ は元の光の進行方向と散乱後の方向のなす角**です。

### レイリー

<div class="formula">P_R(θ) = (3 / 16π) · (1 + cos²θ)</div>

**前後に対称**で**横方向へ少し弱い**形です。

### ミー（Henyey-Greenstein）

<div class="formula">P_HG(θ) = (1 / 4π) · (1 − g²) / (1 + g² − 2g·cosθ)^(3/2)</div>

| g | 意味 |
| --- | --- |
| **0** | <strong>等方（全方向に均等）</strong> |
| **0.76 付近** | **大気のミー散乱：前方に強く散る**（**太陽の周りが明るくにじむ**） |
| **負** | **後方へ散る** |

```hlsl
float RayleighPhase(float cos_theta) {
  return 3.0 / (16.0 * 3.14159265) * (1.0 + cos_theta * cos_theta);
}

float HenyeyGreenstein(float cos_theta, float g) {
  float g2 = g * g;
  float denom = 1.0 + g2 - 2.0 * g * cos_theta;
  return (1.0 - g2) / (4.0 * 3.14159265 * pow(denom, 1.5));
}
```

**雲や霧の散乱**（[雲](../clouds/index.md)・[ボリューメトリック フォグ](../volumetric-fog/index.md)）も、**同じ位相関数**を使います。

## よくあるミス

??? failure "太陽の周りの、白いにじみが出ない"
    **ミー散乱の位相関数**を**入れる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **レイリーは均等、ミーは前方に偏る**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [大気散乱](index.md)
- [単散乱の積分](single-scattering.md)
