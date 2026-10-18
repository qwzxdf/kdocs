---
title: Alpha Blending and Sorting
tags:
  - 描画
---

# Alpha Blending and Sorting

**半透明は、「手前の色」と「奥の色」を、アルファ値で混ぜて表現します**。**混ぜる順序で結果が変わる**ので、**奥から手前の順（ソート）で描く必要があります**。このセクションでは、**ブレンドの式・DirectX 11 のブレンド ステート・乗算済みアルファ・ソート・ソフト パーティクル**を、**1 つずつ別のページ**で説明します。

## The Alpha Blend Formula {#アルファ-ブレンドの式}
**ソース色 `C_s`**（今描く）、**ソース アルファ `α_s`**、**デスティネーション色 `C_d`**（すでにある）とします。

<div class="formula">C_out = C_s · α_s + C_d · (1 − α_s)</div>

各記号の意味です。C_s は今描こうとしている色、α_s は今の不透明度（0 で完全に透明、1 で不透明）、C_d は画面（レンダー ターゲット）にある色です。

**α が 0.5 なら、半分ずつ混ざり**ます。<strong>この式は「後から描いた物ほど、手前にある」</strong>ことを前提にしています。

### Order Changes the Result {#順序で結果が変わる}

**赤（α = 0.5）と青（α = 0.5）を、白い背景に重ねる**場合を考えます。

赤（α = 0.5）と青（α = 0.5）を白い背景に重ねる場合を考えます。赤を先、青を後（青が手前）に描くと、青っぽい紫になります。青を先、赤を後（赤が手前）に描くと、赤っぽい紫になります。同じ 2 枚でも、順序で結果が変わります。これがソートが必要な理由です。

**どちらが手前か**が、**見た目を決める**ので、**奥の物から先に描く**必要があります。

## Page List {#ページ一覧}

| ページ | 内容 |
| --- | --- |
| [Blend State](blend-state.md) | DirectX 11 での設定 |
| [Premultiplied Alpha](premultiplied.md) | 式を単純にして、品質も上げる |
| [Sorting](sorting.md) | 描く順序の決め方 |
| [Soft Particles](soft-particles.md) | 深度を読んで、交差の硬い線を消す |

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **半透明は、奥から手前へ、混ぜながら描く**
    - [x] **深度は書かず、読むだけ**

## References {#参考}

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## Related Pages {#関連ページ}

- [Translucency](../index.md)
- [OIT](../oit/index.md)
- [Alpha Testing](../alpha-test/index.md)
