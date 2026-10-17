---
title: 水のフレネル
tags:
  - 描画
---

# 水のフレネル

**水は、真上から見ると、透けて底が見え、斜めから見ると、空を映す鏡のようになります**。**この反射と屈折の割合が、フレネル**です。このページでは、**水のフレネルの式と使い方**を説明します。

!!! tip "ポイント"
    - **水の F0 は 0.02 程度**（ガラスより低い）。
    - **Schlick 近似で、安く計算**。
    - **反射色と屈折色を、F で混ぜる**。
    - **遠く（斜め）ほど、反射が強い**。

## フレネル
**フレネル**は、<strong>「見る角度が浅いほど、反射が強くなる」</strong>という現象です。**水面に真上から（垂直に）近い角度で見ると反射は約 2 %** で**ほとんどが透過**します。**水平に近い角度で見ると、反射は 100 % に近づき**、**鏡のように**なります。

<div class="formula">F(θ) = F₀ + (1 − F₀) · (1 − cos θ)⁵　（Schlick 近似、水の F₀ ≈ 0.02）</div>

| 記号 | 意味 |
| --- | --- |
| **θ** | **視線と法線のなす角**（`cos θ = dot(N, V)`） |
| **F₀** | **真上から見たときの反射率**。**水は約 0.02**（屈折率 1.33 から求まる） |
| **F** | **反射の割合**（0〜1）。**透過は 1 − F** |

**屈折率 n から F₀ を求める式**です。

<div class="formula">F₀ = ((n₁ − n₂) / (n₁ + n₂))²　（空気 n₁ = 1.0、水 n₂ = 1.33 → F₀ ≈ 0.02）</div>

```hlsl
float Fresnel(float3 normal, float3 view_dir) {
  float cos_theta = saturate(dot(normal, view_dir));
  const float kF0 = 0.02;
  return kF0 + (1.0 - kF0) * pow(1.0 - cos_theta, 5.0);
}
```

<strong>`view_dir` は、「水面から目へ向かう向き」</strong>（正規化済み）です。**向きを逆にすると、`cos θ` の符号が変わる**ので**注意**します。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="フレネルのグラフ">
<text x="20" y="24" class="fig-title">フレネル：見る角度で、反射の割合が変わる（水：F₀ = 0.02）</text>
<line x1="80" y1="220" x2="720" y2="220" stroke="currentColor" stroke-opacity="0.5"/>
<line x1="80" y1="50" x2="80" y2="220" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#4c8bf5" stroke-width="3" points="80,216 160,215 240,213 320,210 400,205 480,196 560,180 620,155 670,110 700,70 720,52"/>
<text x="84" y="44" style="font-size:12px">F（反射の割合）</text>
<text x="76" y="238" style="font-size:12px" text-anchor="end">0</text>
<text x="86" y="240" style="font-size:12px">真上から見る（θ = 0°）</text>
<text x="720" y="240" style="font-size:12px" text-anchor="end">水平に近い（θ → 90°）</text>
<text x="420" y="150" style="font-size:13px">ほとんど変わらない</text>
<text x="560" y="100" style="font-size:13px">急に反射が増える</text>
<line x1="90" y1="52" x2="720" y2="52" stroke="#e5484d" stroke-opacity="0.5" stroke-dasharray="4 4"/>
<text x="400" y="46" style="font-size:12px;fill:#e5484d">F = 1（完全な鏡）</text>
</svg>

**水面の見た目の大半は、この 1 つの式で決まります**。**足元の水は透けて底が見え**、**遠くの水は空を映す**のは、**フレネルのため**です。

## よくあるミス

??? failure "水が、どの角度でも同じ透明度"
    **フレネルで混ぜ比を変える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **角度で、反射と屈折が入れ替わる**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [水の質感](index.md)
- [フレネル（屈折）](../../translucency/refraction/fresnel.md)
