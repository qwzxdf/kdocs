---
title: Visual Effect
tags:
  - 描画
---

# Visual Effect

**間接光があると、影の中が真っ黒ではなくなり、色が周りへにじみ（カラー ブリーディング）、物が「そこにある」ように見えます**。このページでは、**間接光が、見た目にもたらす効果**を説明します。

!!! tip "ポイント"
    - **影の中が、真っ黒ではなくなる**。
    - **色のにじみ（赤い壁の近くの白い物が、赤みを帯びる）**。
    - **物が地面になじみ、「浮いて」見えなくなる**。
    - **室内の明るさが、自然になる**。

## 間接光の見た目への効果
| 効果 | 内容 |
| --- | --- |
| **日陰の明るさ** | **真っ黒にならず**、**周囲から回り込む光**で**ほのかに明るい** |
| **カラー ブリーディング** | **色付きの面**の近くが**その色に染まる** |
| **接地感** | <strong>AO（環境光遮蔽）</strong>と合わせて、**物が地面になじむ** |
| **屋内の明るさ** | **窓からの光が部屋全体**を**拡散して照らす** |

## よくあるミス

??? failure "GI なしで、影の中が真っ黒"
    **最低限、環境光（アンビエント）を入れる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **GI は、影の暗さ・色のにじみ・なじみを生む**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [GI Theory](index.md)
- [AO](../../ao/index.md)
- [GI の比較](../comparison.md)
