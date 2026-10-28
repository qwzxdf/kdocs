---
title: Alpha Blending and Sorting
tags:
  - 描画
---

# Alpha Blending and Sorting

<strong>半透明は「手前の色」と「奥の色」をアルファ値で混ぜて表現します</strong>。<strong>混ぜる順序で結果が変わる</strong>ので、奥から手前の順（ソート）で描く必要があります。このセクションではブレンドの式・DirectX 11 のブレンド ステート・乗算済みアルファ・ソート・ソフト パーティクルを 1 つずつ別のページで説明します。

## アルファ ブレンドの式
<strong>ソース色 `C_s`</strong>（今描く）、<strong>ソース アルファ `α_s`</strong>、デスティネーション色 `C_d`（すでにある）とします。

<div class="formula">C_out = C_s · α_s + C_d · (1 − α_s)</div>

各記号の意味です。C_s は今描こうとしている色、α_s は今の不透明度（0 で完全に透明、1 で不透明）、C_d は画面（レンダー ターゲット）にある色です。

<strong>α が 0.5 なら半分ずつ混ざり</strong>ます。<strong>この式は「後から描いた物ほど手前にある」</strong>ことを前提にしています。

### 順序で結果が変わる

<strong>赤（α = 0.5）と青（α = 0.5）を白い背景に重ねる</strong>場合を考えます。

赤（α = 0.5）と青（α = 0.5）を白い背景に重ねる場合を考えます。赤を先、青を後（青が手前）に描くと青っぽい紫になります。青を先、赤を後（赤が手前）に描くと赤っぽい紫になります。同じ 2 枚でも順序で結果が変わります。これがソートが必要な理由です。

<strong>どちらが手前か</strong>が <strong>見た目を決める</strong>ので、奥の物から先に描く必要があります。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Blend State](blend-state.md) | DirectX 11 での設定 |
| [Premultiplied Alpha](premultiplied.md) | 式を単純にして、品質も上げる |
| [Sorting](sorting.md) | 描く順序の決め方 |
| [Soft Particles](soft-particles.md) | 深度を読んで、交差の硬い線を消す |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 半透明は奥から手前へ混ぜながら描く
    - [x] 深度は書かず読むだけ

## 参考

- Porter, Duff, "Compositing Digital Images", SIGGRAPH 1984（アルファ合成の原典）
- Smith, "Image Compositing Fundamentals", Microsoft Technical Memo 4, 1995（乗算済みアルファ）
- Lorach, "Soft Particles", NVIDIA White Paper, 2007
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明、屈折、フレネルの章）

## 関連ページ

- [Translucency](../index.md)
- [OIT](../oit/index.md)
- [Alpha Testing](../alpha-test/index.md)
