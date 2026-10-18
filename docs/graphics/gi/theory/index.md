---
title: GI Theory
tags:
  - 描画
---

# GI Theory

**GI（グローバル イルミネーション）は、光が壁や床で跳ね返って、周りを照らす「間接光」を表現する技術**です。**手法はたくさんありますが、どれも「レンダリング方程式」という同じ式を、どう近似するかの違い**です。このセクションでは、**レンダリング方程式・拡散と鏡面・放射照度・球面調和関数（SH）・モンテカルロ積分・手法の分類・見た目への効果**を、**1 つずつ別のページ**で説明します。

## レンダリング方程式
点 `p` から、方向 `ω_o` に出る光の量（放射輝度）は、次のとおりです。

<div class="formula">L_o(p, ω_o) = L_e(p, ω_o) + ∫ L_i(p, ω_i) · f(p, ω_i, ω_o) · (n·ω_i) dω_i</div>

| 記号 | 意味 |
| --- | --- |
| **L_o** | 点から、視線方向へ出ていく光 |
| **L_e** | 点自身が出す光（発光） |
| <strong>L_i(p, ω_i)</strong> | 方向 `ω_i` から入ってくる光 |
| **f** | BRDF（入る方向と出る方向の反射の割合） |
| **n·ω_i** | 入射角の余弦（斜めから来る光は、薄まる） |
| **∫ … dω_i** | 半球上の全方向の積分 |

**入ってくる光 `L_i(p, ω_i)`** は、**その方向にある別の面 `q` から出てきた光 `L_o(q, -ω_i)`** です。つまり、**右辺の中に同じ式（別の点で）が含まれる**＝**再帰**です。

ここで入ってくる光 L_i(p, ω_i) は、その方向にある別の面 q から出てきた光 L_o(q, −ω_i) です。つまり、右辺の中に同じ式（別の点で）が含まれる<strong>再帰</strong>になっています。この再帰を、入ってくる光の出どころで分けて呼びます。光源から直接来る光が<strong>直接光</strong>（シャドウ マップとライトの計算で処理）、別の面で 1 回反射してから来る光が 1 バウンスの間接光、2 回以上反射してから来る光が多バウンスの間接光です。

リアルタイムの GI は、ほとんどが 1〜数バウンスを近似したものです。反射するたびに、光は面の反射率（アルベド）の分だけ弱まります。たとえばアルベドが 0.5 の部屋なら、1 バウンス目の光は直接光の約半分、2 バウンス目は約 1/4、3 バウンス目は約 1/8 です。バウンス数が増えるほど急速に弱まるので、<strong>1 バウンスが一番重要</strong>で、その後は急に効きが小さくなります。ただし、アルベドの高い白い部屋では減り方が遅く、バウンスを多く取らないと暗く見えます。そのため、後でマルチ バウンスを補正する工夫が必要になります。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Diffuse and Specular](diffuse-specular.md) | 間接光を 2 つに分けて考える |
| [Irradiance](irradiance.md) | 拡散の間接光を、方向で畳み込む |
| [Spherical Harmonics (SH)](spherical-harmonics.md) | 方向の関数を、少数の係数で持つ |
| [Monte Carlo Integration](monte-carlo.md) | ランダムな試行で積分を近似 |
| [Taxonomy of Methods](taxonomy.md) | 2 つの軸で、GI 手法を整理 |
| [Visual Effect](visual-effect.md) | 間接光があると、何が変わるか |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **GI はレンダリング方程式の近似**
    - [x] **拡散の間接光は低周波で、軽く表せる**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [GI](../index.md)
- [GI Comparison](../comparison.md)
- [AO Theory](../../ao/theory/index.md)
