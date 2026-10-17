---
title: セル シェーディング
tags:
  - 描画
---

# セル シェーディング

<strong>セル シェーディング（トゥーン シェーディング）</strong>は、**陰影を滑らかなグラデーションではなく、数段階（2〜3 段）に区切る**表現です。<strong>手描きアニメの「セル画」</strong>のように、<strong>「明るい面」「影の面」がくっきり分かれる</strong>ので、**アニメ調の絵**になります。**ライティングの結果（明るさ）を、段階に変換する関数**が**核**で、**ランプ テクスチャ**で**自由に調整**できます。**写実的な高品質とは別の方向の表現**で、**画風に合うかどうか**が**基準**です。このページでは、**基本の段階化・ランプ テクスチャ・なめらかな境・スペキュラとリム ライト・影の色・影を受けるときの扱い**を説明します。

!!! tip "ポイント"
    - セル シェーディング ＝ <strong>ライティングの明るさを、数段階に区切る</strong>。
    - 基本 ＝ <strong>`N·L`（拡散）を、しきい値で段階化</strong>。<strong>`step` や `smoothstep`</strong>。
    - <strong>ランプ テクスチャ</strong>：<strong>`N·L` を座標に色を引く 1D テクスチャ</strong>。<strong>アーティストが段階を自由に調整</strong>できる。
    - <strong>境を少しぼかす（`smoothstep`）</strong>と<strong>ちらつき・ジャギーが減る</strong>。
    - <strong>影の色</strong>を<strong>暗い灰色でなく、色相を変えた暗い色</strong>に。
    - <strong>スペキュラ</strong>は<strong>しきい値で、くっきりした白いハイライト</strong>。<strong>リム ライト</strong>で<strong>輪郭を明るく</strong>。

## 基本：N·L を段階化

**普通のライティング**は、**`N·L`（法線と光の向きの内積）で、明るさが滑らかに変わります**。**セルではこれをしきい値で数段階に変換**します。

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="セル シェーディング">
<text x="20" y="26" class="fig-title">滑らかな明るさを、段階に区切る</text>
<defs><linearGradient id="cs-smooth" x1="0" x2="1"><stop offset="0" stop-color="#1e293b"/><stop offset="1" stop-color="#f8e9c8"/></linearGradient></defs>
<g transform="translate(40,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">通常（滑らか）</text>
<circle cx="90" cy="70" r="62" fill="url(#cs-smooth)"/>
</g>
<g transform="translate(280,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">2 段（明・影）</text>
<circle cx="90" cy="70" r="62" fill="#f8e9c8"/><path d="M90,8 A62,62 0 0 0 90,132 Z" fill="#8a7a90" transform="translate(20,0)"/>
</g>
<g transform="translate(520,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">3 段（明・中・影）</text>
<circle cx="90" cy="70" r="62" fill="#f8e9c8"/><circle cx="90" cy="70" r="62" fill="#b5a3a8" clip-path="inset(0 0 0 0)" opacity="0"/>
<path d="M90,8 A62,62 0 0 0 90,132 Z" fill="#b5a3a8" transform="translate(30,0)"/><path d="M90,8 A62,62 0 0 0 90,132 Z" fill="#6f5f78" transform="translate(5,0)"/>
</g>
</svg>

```hlsl
float3 CelShade(float3 albedo, float3 normal, float3 light_dir, float3 light_color) {
  float n_dot_l = dot(normal, light_dir);
  float lit = step(0.0, n_dot_l);
  float3 shadow_color = albedo * float3(0.55, 0.5, 0.7);
  return lerp(shadow_color, albedo * light_color, lit);
}
```

| 点 | 説明 |
| --- | --- |
| **`step(0, N·L)`** | **光に向いていれば 1、背を向けていれば 0**（**2 段**） |
| **`shadow_color`** | **影の色**（**暗い灰色でなく、色味のある暗い色**） |
| **`lerp`** | **影と明部を切り替え** |

## なめらかな境

**`step` は境がジャギーで、動くとちらつきます**。<strong>境を少しだけぼかす（`smoothstep`）</strong>と**きれい**です。

```hlsl
float Toon(float n_dot_l, float threshold, float softness) {
  return smoothstep(threshold - softness, threshold + softness, n_dot_l);
}
```

| `softness` | 見た目 |
| --- | --- |
| **0.0〜0.01** | <strong>ほぼシャープ（アニメ調）</strong> |
| **0.05〜0.1** | <strong>少し柔らかい（水彩・イラスト調）</strong> |

## ランプ テクスチャ

**`N·L`（0〜1 に直したもの）を座標に色を引く 1D テクスチャ**です。**アーティストが段階の数・境の位置・色の変化を自由に描けます**。

```hlsl
Texture2D ramp_texture : register(t3);

float3 CelShadeRamp(float3 albedo, float3 normal, float3 light_dir) {
  float n_dot_l = dot(normal, light_dir) * 0.5 + 0.5;
  float3 ramp = ramp_texture.SampleLevel(clamp_linear, float2(n_dot_l, 0.5), 0).rgb;
  return albedo * ramp;
}
```

| 点 | 説明 |
| --- | --- |
| **`N·L × 0.5 + 0.5`** | **−1〜1 を 0〜1 に**（**ハーフ ランバート**） |
| **ランプの形** | **階段状の画像をバイリニアでサンプル** |
| **利点** | **コードを変えずに画風を変えられる**（**キャラごとにランプを差し替える**） |

<!-- fig:cel-ramp:begin -->
<!-- fig:cel-ramp:end -->

## 影の色

**影を単純に「暗くする」と、絵が重く、汚く見えます**。**影は色相を少し変え、彩度を保った、暗い色**に**するとアニメ的**です。

| 影の付け方 | 見た目 |
| --- | --- |
| <strong>単純に暗く（× 0.5）</strong> | **灰色っぽく、汚い** |
| <strong>色相をずらす（青・紫寄り）</strong> | **アニメ調の澄んだ影** |
| **肌：赤みを保つ** | **健康的な肌** |
| **アルベドごとの影色** | <strong>材質ごとに別の影の色（テクスチャ・パラメータ）</strong> |

```hlsl
float3 shadow_tint = lerp(float3(1, 1, 1), float3(0.6, 0.55, 0.85), shadow_strength);
float3 shaded = albedo * shadow_tint;
```

## スペキュラとリム ライト

| 要素 | 内容 |
| --- | --- |
| **スペキュラ** | **ハーフ ベクトルとの内積を、しきい値で 2 値化して、くっきりした白いハイライト** |
| **リム ライト** | **視線と法線が直角に近い所（輪郭付近）を、明るくして、輪郭を際立たせる** |

```hlsl
float ToonSpecular(float3 normal, float3 view_dir, float3 light_dir, float shininess, float threshold) {
  float3 half_vector = normalize(light_dir + view_dir);
  float n_dot_h = saturate(dot(normal, half_vector));
  return step(threshold, pow(n_dot_h, shininess));
}

float RimLight(float3 normal, float3 view_dir, float power, float threshold) {
  float rim = 1.0 - saturate(dot(normal, view_dir));
  return step(threshold, pow(rim, power));
}
```

| 点 | 説明 |
| --- | --- |
| **`step(threshold, pow(...))`** | **くっきりした、はっきりした形のハイライト** |
| **リム ライト** | **輪郭が背景から浮き出る**（**暗い背景で特に効く**） |
| **向き** | **光の向きに沿ったリムだけにすると、自然**（**`rim × N·L`**） |

## 影を受ける

**シャドウ マップの影**（[影](../../shadows/index.md)）を**セルの陰影に取り込む**には**影の判定値（0〜1）を、`N·L` と掛け合わせます**。

```hlsl
float shadow = SampleShadow(world_position);
float n_dot_l = dot(normal, light_dir);
float toon_input = n_dot_l * shadow;
float lit = smoothstep(0.0, 0.02, toon_input);
```

**シャドウ マップの境が、PCF などで柔らかいと、セルの境がぎざぎざになる**ので、**境の硬さを合わせる**（**影も段階化する**）のがよい**です**。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **ランプ テクスチャ** | **アーティストが画風を調整** |
| **影色を色相を変えた暗い色に** | **澄んだ影** |
| **`smoothstep` で境を滑らかに** | **ジャギー・ちらつきを防ぐ** |
| **輪郭線と併用** | <strong>アウトライン（[背面法](outline-hull.md)・[画面空間](outline-edge.md)）</strong> |
| **ライトの扱いをメイン ライトのみに** | **複数ライトを段階化すると複雑** |
| **顔の影を別に調整** | <strong>顔の陰影は法線を補正（顔の影が汚くならない）</strong> |
| **キャラごとのランプ・影色** | **材質ごとのパラメータ** |

## よくあるミス

??? failure "影の境がジャギー・ちらつく"
    **`smoothstep` で、狭い範囲をぼかす**。

??? failure "影が灰色っぽく、絵が汚い"
    **影色に色相を持たせる**。

??? failure "複数のライトを、全部段階化して、ごちゃごちゃする"
    **メイン ライトだけセル化**し、**他は弱い環境光**に。

??? failure "顔に、鼻や顎の汚い影が出る"
    **顔の法線を平らにする**（**法線の補正**）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] セル シェーディング ＝ <strong>ライティングの明るさを、数段階に区切る</strong>
    - [x] <strong>`N·L` をしきい値で段階化</strong>。<strong>`smoothstep` で境を滑らかに</strong>
    - [x] <strong>ランプ テクスチャ</strong>で<strong>画風を自由に調整</strong>
    - [x] <strong>影は、色相を変えた暗い色</strong>に
    - [x] <strong>スペキュラ・リム ライトは、くっきり</strong>。<strong>輪郭線と併用</strong>

## 参考

- Xu et al., "Guilty Gear Xrd's Art Style: The X Factor Between 2D and 3D"（GDC 2015）
- Lake et al., "Stylized Rendering Techniques for Scalable Real-Time 3D Animation"（NPAR 2000）
- Barla et al., "X-Toon: An Extended Toon Shader"（NPAR 2006）

## 関連ページ

- [輪郭線・トゥーン](index.md)
- [背面法の輪郭線](outline-hull.md)
- [ポスタライズとハーフトーン](posterize-halftone.md)
- [法線とライティング](../../../3d/lighting-normals.md)
