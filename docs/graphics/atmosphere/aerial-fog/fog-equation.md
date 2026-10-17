---
title: フォグの式
tags:
  - 描画
---

# フォグの式

**距離に応じて、物の色をフォグの色に近づけるのが、フォグ**です。**減衰の式には、線形・指数・指数二乗**があります。このページでは、**フォグの式**を説明します。

!!! tip "ポイント"
    - **線形：距離に比例して増える**。
    - **指数：exp(−密度 × 距離)**（物理的、標準）。
    - **指数二乗：近くは澄み、遠くで急に濃くなる**。
    - **最終色 ＝ 物の色 × 透過率 ＋ フォグの色 × (1 − 透過率)**。

## フォグの式
**光は距離 d を進むと減衰して散乱光と入れ替わります**。**物の色 C は、フォグの色 F と混ざります**。

<div class="formula">C_final = C · T + F · (1 − T)　（T：透過率）</div>

| 種類 | 透過率 T | 特徴 |
| --- | --- | --- |
| **線形** | <strong>T = saturate((end − d) / (end − start))</strong> | **start までは影響なし、end で完全にフォグ**。**調整しやすいが物理的ではない** |
| **指数** | <strong>T = exp(−density · d)</strong> | **物理的に自然**。**遠くが徐々に霞む** |
| **指数の 2 乗** | <strong>T = exp(−(density · d)²)</strong> | **近くはほぼ透明である距離から急に霞む** |

```hlsl
float FogTransmittance(float distance_to_pixel) {
  return exp(-fog_density * distance_to_pixel);
}

float3 ApplyFog(float3 color, float distance_to_pixel) {
  float t = FogTransmittance(distance_to_pixel);
  return lerp(fog_color, color, t);
}
```

| 点 | 説明 |
| --- | --- |
| **距離はカメラからの直線距離** | **深度（Z）ではなく、位置の長さ**を使う（**画面の端でも同じ濃さ**）。**`length(world_position − camera_position)`** |
| **`density`** | **0.001〜0.02 /m** 程度。**視界 200〜2000 m** |
| **HDR で適用** | **トーンマップの前**に掛ける |
| **空にもフォグ** | **地平線付近の空の色をフォグの色と一致させる**（**山が空に溶ける**） |

### 深度から距離を求める

**フル スクリーン パスで、深度バッファから位置を再構築**して**距離**を**出します**。

```hlsl
float3 world_position = ReconstructWorldPosition(uv, depth);
float distance_to_pixel = length(world_position - camera_position);
```

## よくあるミス

??? failure "フォグの境目が急で、不自然"
    **指数フォグ**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **指数フォグが標準**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [空気遠近法・フォグ](index.md)
- [高さフォグ](height-fog.md)
