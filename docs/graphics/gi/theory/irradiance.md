---
title: Irradiance
tags:
  - 描画
---

# Irradiance

**拡散の間接光は、「その点の周りの全方向から来る光を、法線に合わせて足し合わせた量」**で、これを**放射照度**と呼びます。**法線ごとに 1 つの値**なので、**環境マップ全体を、法線ごとの放射照度マップに「畳み込んで」おく**と、**実行時は読むだけ**になります。このページでは、**放射照度の意味と、畳み込みの考え方**を説明します。

!!! tip "ポイント"
    - **放射照度 ＝ 法線の半球に入る光の、余弦重み付き平均**。
    - **法線の向きごとに 1 つの値**で、**とてもなめらか**。
    - **環境マップを事前に畳み込んで、放射照度マップを作る**。
    - **実行時は、法線で 1 回読むだけ**。

## 放射照度：拡散の間接光を畳み込む
**ランバート面**では、**出る光の量は視線方向に依存せず**、**入ってくる光を余弦で重みづけて積分した量**（**放射照度 E**）だけで決まります。

<div class="formula">E(n) = ∫ L_i(ω) · max(0, n·ω) dω　、　L_o = (albedo / π) · E(n)</div>

**E は法線 `n` だけの関数**です（位置 `p` は固定とする）。**あらゆる方向からの光を、「n を中心とした余弦」で畳み込んだ**ものなので、<strong>非常になめらか（低周波）</strong>です。**法線が少し変わっても、E はほとんど変わりません**。

この性質のおかげで**間接光（拡散）は、粗い情報**（**少ない数値**）で、**保存できます**。

## よくあるミス

??? failure "環境マップをそのまま拡散に使って、ざらざらする"
    **放射照度マップ（畳み込み済み）**を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **放射照度 ＝ 法線ごとの、なめらかな光の量**
    - [x] **事前の畳み込みで、実行時は読むだけ**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [GI Theory](index.md)
- [Spherical Harmonics (SH)](spherical-harmonics.md)
- [Diffuse and Specular](diffuse-specular.md)
