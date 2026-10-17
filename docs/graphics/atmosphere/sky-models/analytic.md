---
title: Analytic Sky Models
tags:
  - 描画
---

# Analytic Sky Models

**Preetham や Hosek-Wilkie などは、太陽の位置と大気の濁りから、空の色を式で求めるモデル**です。**グラデーションより物理的で、積分も要りません**。このページでは、**解析的な空のモデル**を説明します。

!!! tip "ポイント"
    - **太陽の高さと、濁り（タービディティ）で、空の色が決まる**。
    - **Hosek-Wilkie は、Preetham より精度が高い**。
    - **1 画素ごとに式を評価するだけ**。
    - **宇宙からの視点には、向かない**。

## 解析的な空のモデル
<strong>Preetham（1999）・Hosek-Wilkie（2012）</strong>は、**空の輝度分布を少数のパラメータの数式で近似**します。<strong>パラメータは太陽の高さ（天頂角）と、大気の濁り（turbidity）</strong>です。**実測・シミュレーションにフィットさせた式**なので、**手作業のグラデーションより自然**で、**時刻による移り変わりも連続**します。

### Preetham（Perez の式）

**Perez の式**で<strong>視線ごとの輝度（Y）と色度（x, y）</strong>を**求めます**。

<div class="formula">F(θ, γ) = (1 + A·e^(B / cos θ)) · (1 + C·e^(D·γ) + E·cos²γ)</div>

| 記号 | 意味 |
| --- | --- |
| **θ** | **視線の天頂角**（真上から何度か） |
| **γ** | **視線と太陽のなす角** |
| **A〜E** | **係数**。**turbidity から線形式で決まる** |

**最終的な空の輝度は、天頂の輝度に比をかけて出します**。

<div class="formula">Y = Y_zenith · F(θ, γ) / F(0, θ_sun)</div>

```hlsl
float Perez(float cos_theta, float gamma, float cos_gamma, PerezCoefficients coeff) {
  return (1.0 + coeff.A * exp(coeff.B / max(cos_theta, 0.01)))
       * (1.0 + coeff.C * exp(coeff.D * gamma) + coeff.E * cos_gamma * cos_gamma);
}
```

| 点 | 説明 |
| --- | --- |
| **`max(cos θ, 0.01)`** | **地平線で発散するのを防ぐ** |
| **xyY から RGB** | **色度 (x, y) と輝度 Y を、XYZ → sRGB（線形）に変換** |
| **露出を掛ける** | <strong>輝度が絶対値（cd/m²）</strong>なので**露出で合わせる** |

### Hosek-Wilkie

**Hosek-Wilkie** は **Preetham の改良版**で、**特に太陽が低いとき、地面の反射率（アルベド）を考慮したとき**に**精度が高い**です。<strong>係数テーブル（9 つのパラメータ × 3 色 × turbidity × albedo × 高さ）</strong>を**公開データとして持ち、式の形は Preetham に似ています**。

| 項目 | Preetham | Hosek-Wilkie |
| --- | --- | --- |
| **精度** | **太陽が低いと不正確** | **より正確** |
| **パラメータ** | **turbidity** | **turbidity ＋ 地面のアルベド** |
| **データ** | <strong>数式の係数のみ（少ない）</strong> | <strong>係数テーブルが必要（大きい）</strong> |
| **用途** | **軽量・手軽** | **品質重視** |

**どちらも空の見た目だけ**で<strong>大気の中を通る光（遠景の霞・光の筋）</strong>は**別に計算**する必要があります。**そこは[Atmospheric Scattering](../scattering/index.md)の担当**です。

## よくあるミス

??? failure "日没近くで、空の色が不自然"
    **Hosek-Wilkie** などの**精度の高いモデル**を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **式で空の色を求める。軽い**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Sky Models](index.md)
- [Atmospheric Scattering](../scattering/index.md)
