---
title: Fresnel
tags:
  - 描画
---

# Fresnel

**ガラスや水は、見る角度によって、反射と屈折の割合が変わります**。**真正面からは、ほぼ透明、斜めからは、鏡のようになる**のが**フレネル効果**です。このページでは、**フレネルの式（Schlick 近似）と使い方**を説明します。

!!! tip "ポイント"
    - **正面 ＝ 屈折（透過）が主。斜め ＝ 反射が主**。
    - **Schlick 近似：F = F0 + (1 − F0)(1 − cosθ)⁵**。
    - **反射と屈折を、F で混ぜる**。
    - **ガラスの F0 は 0.04 程度**。

## フレネル
**浅い角度**（面すれすれ）で見るほど、**反射が強く、透過（屈折）が弱く**なります。**水面を、真上から見ると底が見え、遠くを見ると空が映る**のは、**フレネル**です。

**Schlick の近似**：

<div class="formula">F = F₀ + (1 − F₀) · (1 − cos θ)⁵　　F₀ = ((n₁ − n₂) / (n₁ + n₂))²</div>

| 記号 | 意味 |
| --- | --- |
| **F₀** | **真正面から見たときの反射率**（**ガラス・水は約 0.02〜0.04**） |
| **cos θ** | **視線と法線の内積** |
| **F** | **反射率**（0〜1）。**透過は `1 − F`** |

```hlsl
float Fresnel(float cos_theta, float f0) {
  return f0 + (1.0 - f0) * pow(1.0 - saturate(cos_theta), 5.0);
}

float f = Fresnel(dot(normal, -view_dir), 0.04);
float3 color = lerp(refracted_background, reflection, f);
```

| 点 | 説明 |
| --- | --- |
| **`F₀ = 0.04`** | **非金属（ガラス・水・プラスチック）の標準値** |
| **`lerp(屈折, 反射, F)`** | **F が大きいほど、反射が強く**なる |
| **反射の色** | **環境マップ・SSR・プローブ**（[Reflections](../../reflections/index.md)） |

## よくあるミス

??? failure "ガラスが、どの角度でも同じ透明度"
    **フレネルで、反射と屈折の割合を変える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **角度で、反射と屈折の割合が変わる**
    - [x] **Schlick 近似で、安く計算**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [Refraction](index.md)
- [Water Shading](../../water/shading/index.md)
