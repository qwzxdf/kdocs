---
title: Specular and Dynamic Objects
tags:
  - 描画
---

# Specular and Dynamic Objects

**ライトマップは、拡散の間接光だけ**で、**鏡面の反射は含みません**。**また、動く物体には、ライトマップが無い**ので、**プローブで間接光を補います**。このページでは、**鏡面の扱いと、動く物体との併用**を説明します。

!!! tip "ポイント"
    - **鏡面は別**：**反射プローブ・SSR**で扱う。
    - **動く物体は、ライトマップを持たない**。
    - **周囲のプローブ（SH）から、間接光を受け取る**。
    - **静的な背景と、動く物体の明るさが、揃うように調整**する。

## 鏡面は別
**ライトマップは、拡散の間接光のみ**です。**鏡面反射**は**反射プローブ**（[Reflection Probes](../../reflections/probes/index.md)）が**担当**します。

## 動く物体との併用
**ライトマップは、メッシュの表面**に焼くので、**動く物体・キャラクターには、使えません**。**動く物体**は**ライト プローブ**（[ライト プローブ](../probes/index.md)）から、**周囲の間接光**を受け取ります。**静的な背景はライトマップ、動く物はプローブ**が**標準的な組み合わせ**です。

| 対象 | GI の方式 |
| --- | --- |
| **静的な背景** | ライトマップ |
| <strong>動的な物体（キャラ・乗り物）</strong> | ライト プローブ（ライトマップと**同じ見た目に、そろえる**） |
| **動く物が背景に落とす間接光** | **反映されない**（限界） |

## よくあるミス

??? failure "動く物体だけ、背景と明るさが合わない"
    **ライトプローブ**を置いて、**間接光を揃える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **鏡面は反射の手法で、動く物体はプローブで**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Lightmaps](index.md)
- [Probe GI](../probes/index.md)
- [Reflections](../../reflections/index.md)
