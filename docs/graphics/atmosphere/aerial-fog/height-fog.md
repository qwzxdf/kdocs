---
title: 高さフォグ
tags:
  - 描画
---

# 高さフォグ

**霧は、低い所にたまります**。**フォグの密度を、高さで指数的に減らす**と、**谷にたまる霧**が**表現**できます。このページでは、**高さフォグ**を説明します。

!!! tip "ポイント"
    - **密度 ＝ 基準密度 × exp(−高さ × 係数)**。
    - **視線に沿って積分すると、解析的に求まる**。
    - **低い所ほど、濃い霧**。
    - **朝霧・谷の霧の表現**に向く。

## 高さフォグ
**谷や低地に霧が溜まる**表現です。**霧の密度が高さに対して指数的に減る**と**仮定します**。

<div class="formula">density(h) = density₀ · exp( −falloff · h )</div>

**視線に沿った光学的厚さは、密度を積分した値**です。**指数関数の積分は、解析的に求まる**ので**ステップを刻まず 1 回で計算できます**。

```hlsl
float HeightFogOpticalDepth(float3 camera_pos, float3 world_pos) {
  float3 delta = world_pos - camera_pos;
  float distance_to_pixel = length(delta);
  float height_difference = delta.y;

  float falloff = fog_height_falloff;
  float base = fog_density * exp(-falloff * (camera_pos.y - fog_base_height));
  float integral;
  if (abs(height_difference) > 0.0001) {
    integral = (1.0 - exp(-falloff * height_difference)) / (falloff * height_difference);
  } else {
    integral = 1.0;
  }
  return base * integral * distance_to_pixel;
}

float transmittance = exp(-HeightFogOpticalDepth(camera_position, world_position));
```

| 点 | 説明 |
| --- | --- |
| **解析解** | **視線の高さが変わる区間の積分を、閉じた式で**（**ステップ不要**） |
| **`base`** | **カメラの高さでの密度** |
| **高さ差が 0 に近い** | **0 除算を避けるため、積分の値を 1 に** |
| **`fog_base_height`** | **霧が最も濃い高さ**（**谷底・海面**） |
| **`falloff`** | **大きいほど、霧が薄い層に集中** |

**雲海・谷の霧・朝霧**の表現に**効果的**です。

## よくあるミス

??? failure "霧が、高さに関係なく一様"
    **高さで密度を減らす**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **高さで密度を減らして、霧をたまらせる**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [空気遠近法・フォグ](index.md)
- [ボリューメトリック フォグ](../volumetric-fog/index.md)
