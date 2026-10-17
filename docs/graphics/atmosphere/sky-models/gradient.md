---
title: Gradient Sky
tags:
  - 描画
---

# Gradient Sky

**空の色を、上と地平線で変えるだけの、最も簡単な方法**です。**軽く、制御しやすい**ので、**スタイライズされた作品や、モバイルで多用されます**。このページでは、**グラデーションの空**を説明します。

!!! tip "ポイント"
    - **天頂の色と、地平線の色を、視線の高さで補間**。
    - **太陽の周りを、明るくする**。
    - **とても軽い**。
    - **物理的には正確でない**。

## グラデーションの空
**もっとも簡単**なのは、**視線の仰角（上下の角度）で、地平線の色と天頂の色を混ぜる**方法です。

```hlsl
float3 GradientSky(float3 view_dir) {
  float elevation = saturate(view_dir.y);
  float t = pow(elevation, 0.5);
  float3 sky = lerp(horizon_color, zenith_color, t);

  float below = saturate(-view_dir.y * 4.0);
  return lerp(sky, ground_color, below);
}
```

| 点 | 説明 |
| --- | --- |
| **`pow(elevation, 0.5)`** | **地平線付近で色が急に変わる**（**天頂は広く青い**）。**空の見た目に近づく** |
| **地面の色** | <strong>地平線より下は、地面（暗い色）</strong>で**塞ぐ**（実際の地面が見えない場合） |
| **太陽の方向で色を寄せる** | **太陽のそばを明るく暖色にする**（下の「太陽」） |
| **時間帯のプリセット** | **朝・昼・夕・夜の色セットを補間** |

**グラデーションは、安く・調整しやすい**ですが**太陽の位置で色が変わる**（夕焼けで太陽の側だけ赤い）**といった表現は、手作業になります**。

## よくあるミス

??? failure "地平線に、色の帯（バンディング）が出る"
    **ディザ**を**加える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **高さで色を補間するだけ**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Sky Models](index.md)
- [Analytic Sky Models](analytic.md)
