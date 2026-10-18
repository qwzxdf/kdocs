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

## Specular Is Separate {#鏡面は別}

ライトマップが保存するのは、拡散の間接光だけです。鏡面反射（周りの景色の映り込み）は含みません。鏡面は視線に依存するので、1 つの値としてテクスチャに焼いておくことができないからです（[Diffuse and Specular](../theory/diffuse-specular.md)）。鏡面反射は、[反射プローブ](../../reflections/probes/index.md)や SSR が担当します。ライトマップだけを使うと、つるつるした面が周りを映さず、違和感が出ます。

## Combining with Moving Objects {#動く物体との併用}

ライトマップは、メッシュの表面（UV2）に焼き込むため、動く物体・キャラクターには使えません。動く物体は、位置が変わるたびに受ける間接光が変わるからです。そこで、空間の点に間接光を保存した[ライト プローブ](../probes/index.md)から、周囲の間接光を受け取ります。静的な背景はライトマップ、動く物はプローブ、というのが標準的な組み合わせです。

この組み合わせで大切なのは、<strong>両者の見た目を揃える</strong>ことです。ライトマップで照らされた壁の前を、プローブで照らされたキャラクターが歩くとき、明るさや色が大きく違うと、キャラクターだけが浮いて見えます。プローブは、ライトマップと同じベイクの結果（同じ光源、同じバウンス数）から作るので、基本的には揃いますが、プローブの置き方が粗いと、壁の近くで差が出ます。

限界もあります。動く物体が背景に落とす間接光（キャラクターの赤い服が壁をほんのり赤くする）は、ライトマップに反映されません。ライトマップは焼き込み済みで、動く物体の存在を知らないためです。また、動く物体が背景に作る接触の暗さは、AO で補います（[AO](../../ao/index.md)）。

## Common Mistakes {#よくあるミス}

??? failure "動く物体だけ、背景と明るさが合わない"
    **ライトプローブ**を置いて、**間接光を揃える**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **鏡面は反射の手法で、動く物体はプローブで**

## References {#参考}

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## Related Pages {#関連ページ}

- [Lightmaps](index.md)
- [Probe GI](../probes/index.md)
- [Reflections](../../reflections/index.md)
