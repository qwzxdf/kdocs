---
title: Single-Scattering Integral
tags:
  - 描画
---

# Single-Scattering Integral

**視線に沿って進みながら、各点で太陽の光が、視線方向に散乱される量を足し合わせます**。**これが単散乱の積分**で、**空の色の大部分を決めます**。このページでは、**単散乱の積分**を説明します。

!!! tip "ポイント"
    - **視線を分割し、各点で「太陽の光 × 散乱 × 透過率」を足す**。
    - **太陽の光も、大気で減衰した後のもの**。
    - **分割数（16〜32）で、精度とコストが決まる**。
    - **LUT に入れると、積分が不要**になる。

## 単散乱の積分
**視線に沿った各点で、「太陽光が届く量」×「視線方向へ散る割合」を足し合わせる**のが**空の色**です。

<div class="formula">L = ∫ T(カメラ → p) · σs(p) · P(θ) · T(p → 太陽) · E_sun ds</div>

| 項 | 意味 |
| --- | --- |
| <strong>T(カメラ → p)</strong> | **点 p から、カメラまで届く間の減衰** |
| <strong>σs(p)</strong> | **点 p の散乱係数**（高さで決まる） |
| <strong>P(θ)</strong> | **位相関数**：**太陽の向きから視線の向きへ、どれだけ散るか** |
| <strong>T(p → 太陽)</strong> | **太陽から点 p まで届く間の減衰** |
| **E_sun** | **大気の外での太陽の強さ** |

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="単散乱">
<text x="20" y="24" class="fig-title">単散乱：視線の上の各点で、太陽光が届いて、視線方向へ散る</text>
<path d="M60,230 A320,320 0 0 1 720,230" fill="none" stroke="#4c8bf5" stroke-opacity="0.35" stroke-width="30"/>
<circle cx="200" cy="225" r="6" fill="#e5484d"/><text x="150" y="248" style="font-size:12px">カメラ</text>
<line x1="200" y1="225" x2="500" y2="90" stroke="currentColor" stroke-width="2"/>
<circle cx="330" cy="166" r="4" fill="#2ea043"/><circle cx="400" cy="135" r="4" fill="#2ea043"/><circle cx="460" cy="108" r="4" fill="#2ea043"/>
<line x1="330" y1="40" x2="330" y2="166" stroke="#e5aa28" stroke-width="2" stroke-dasharray="5 4"/>
<line x1="400" y1="40" x2="400" y2="135" stroke="#e5aa28" stroke-width="2" stroke-dasharray="5 4"/>
<line x1="460" y1="40" x2="460" y2="108" stroke="#e5aa28" stroke-width="2" stroke-dasharray="5 4"/>
<text x="540" y="60" style="font-size:12px;fill:#e5aa28">太陽光（平行）</text>
<text x="520" y="100" style="font-size:12px">視線を刻んで、各点の寄与を足す</text>
</svg>

```hlsl
float3 SingleScattering(float3 ray_origin, float3 ray_dir, float ray_length, float3 sun_dir, int steps) {
  float step_length = ray_length / steps;
  float3 rayleigh_sum = 0;
  float3 mie_sum = 0;
  float3 optical_depth_view = 0;

  float cos_theta = dot(ray_dir, sun_dir);
  float phase_r = RayleighPhase(cos_theta);
  float phase_m = HenyeyGreenstein(cos_theta, kMieG);

  for (int i = 0; i < steps; ++i) {
    float3 p = ray_origin + ray_dir * (i + 0.5) * step_length;
    float h = length(p) - kPlanetRadius;
    float density_r = exp(-h / kRayleighScaleHeight);
    float density_m = exp(-h / kMieScaleHeight);

    optical_depth_view += (kRayleighScattering * density_r + kMieExtinction * density_m) * step_length;

    float3 optical_depth_sun = SunOpticalDepth(p, sun_dir);
    float3 attenuation = exp(-(optical_depth_view + optical_depth_sun));

    rayleigh_sum += attenuation * density_r * step_length;
    mie_sum += attenuation * density_m * step_length;
  }
  return sun_intensity * (kRayleighScattering * phase_r * rayleigh_sum
                        + kMieScattering * phase_m * mie_sum);
}
```

コードの要点です。`SunOpticalDepth` は、点 p から太陽方向へ、大気の外まで進んだ光学的厚さで、内側のループです。地面で遮られる向きは 0 として扱います。二重ループになるので、視線 16 ステップに太陽 8 ステップで 128 回の密度計算が必要になり、リアルタイムには重い処理です。レイリーとミーは、位相関数が違うため、別々に足します。

## よくあるミス

??? failure "積分の分割が粗く、空に段が出る"
    **分割数を増やす**、または**サンプルをずらす**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **視線に沿って、散乱を足し合わせる**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Transmittance](transmittance.md)
- [Phase Functions](phase-function.md)
