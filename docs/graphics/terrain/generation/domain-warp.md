---
title: ドメイン ワーピング
tags:
  - 描画
---

# ドメイン ワーピング

**ノイズの入力座標を、別のノイズでゆがませる**と、**うねった、有機的な形**になります。**直線的な規則性が崩れて、自然に見えます**。このページでは、**ドメイン ワーピング**を説明します。

!!! tip "ポイント"
    - **f(p) → f(p + g(p))** の形にする。
    - **ゆがみの強さで、形が変わる**。
    - **fBm と組み合わせる**。
    - **コストは、ノイズの評価が増える分**。

## ドメイン ワーピング
**ノイズの入力座標を別のノイズでゆがめる**と、**自然に曲がりくねった形**になります。

```hlsl
float WarpedFbm(float2 p) {
  float2 q = float2(Fbm(p, 4, 2.0, 0.5), Fbm(p + float2(5.2, 1.3), 4, 2.0, 0.5));
  float2 r = float2(Fbm(p + 4.0 * q + float2(1.7, 9.2), 4, 2.0, 0.5),
                    Fbm(p + 4.0 * q + float2(8.3, 2.8), 4, 2.0, 0.5));
  return Fbm(p + 4.0 * r, 4, 2.0, 0.5);
}
```

| 点 | 説明 |
| --- | --- |
| <strong>ワープの強さ（4.0）</strong> | **大きいと渦のようにねじれる** |
| **層を重ねる** | **q → r → 最終**と**2 段**で**複雑に** |
| **コスト** | **fBm を何度も呼ぶ**ので**重い**。**生成時（ベイク）に使い、実行時には焼いたテクスチャを読む** |

## よくあるミス

??? failure "地形に、規則的な模様が見える"
    **ドメイン ワーピング**で**ゆがめる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **座標をノイズでゆがませる**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [地形の生成](index.md)
- [fBm](fbm.md)
