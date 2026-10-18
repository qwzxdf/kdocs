---
title: Diffuse and Specular
tags:
  - 描画
---

# Diffuse and Specular

**間接光は、「拡散（あらゆる方向へ散る）」と「鏡面（特定の方向へ反射する）」の 2 つに分けて考える**と**扱いやすくなります**。**拡散の間接光は、なめらかなので安く近似でき、鏡面の間接光は、鋭く、別の手法（反射）で扱います**。このページでは、**2 つの違いと、手法の分担**を説明します。

!!! tip "ポイント"
    - **拡散の間接光 ＝ 低周波。なめらか**。
    - **鏡面の間接光 ＝ 高周波。鋭い**（[Reflections](../../reflections/index.md)の領域）。
    - **GI と呼ぶ時は、主に拡散の間接光**を指す。
    - **拡散と鏡面で、別の手法を組み合わせる**のが**普通**。

## Diffuse and Specular {#拡散と鏡面}

BRDF を拡散と鏡面に分けて考えると、間接光の性質がまったく違うことが分かります。

### Diffuse Indirect Light {#拡散の間接光}

ランバート面の BRDF は、ほぼ一定値（albedo / π）です。つまり、入ってくる光がどの方向からでも、同じように全方向へ散らばります。結果として、見る方向に依存せず、見た目の色は法線と周りの光だけで決まります。さらに、前のページで見たように、半球の積分は余弦で畳み込まれて<strong>低周波</strong>になります。粗い情報（プローブ 1 個の SH 係数など）で十分です。

### Specular Indirect Light {#鏡面の間接光}

鏡面反射の BRDF は、反射方向のまわりに鋭いローブ（山）を持ちます。粗さが小さい（つるつるな）ほど山は鋭く、粗いほど広がります。入ってくる光のうち、反射方向の近くの光だけが効くので、周りの景色が<strong>はっきりと映り込みます</strong>。そして、見る方向を変えれば映り込む場所が変わるので、視線に依存します。情報は<strong>高周波</strong>で、細かい情報が必要です。

### Division of Labor Among Methods {#手法の分担}

この違いから、拡散と鏡面は別々の手法で扱うのが普通です。拡散の間接光は、このセクションのライトマップ・プローブ・SSGI・ボクセル・DDGI などが担当します。鏡面の間接光は、[Reflections](../../reflections/index.md) のセクション（平面反射・反射プローブ・SSR・レイトレ反射）が担当します。同じ「他の面から来る光」でも、保存する情報量の違いが、手法を分けています。

ただし、粗さが大きい鏡面は、拡散に近づきます。粗さが十分に高い（マットな）面の鏡面反射は、広いローブになり、低周波になります。その場合は、拡散の手法と同じデータ（プローブなど）をそのまま使っても、見た目の破綻が小さくなります。そのため、実際のエンジンでは、粗い鏡面の間接光を、GI のプローブに任せ、つるつるな面だけを反射の手法で扱う、という分担もよく見られます。

## Common Mistakes {#よくあるミス}

??? failure "鏡面の反射も、GI の手法で出そうとして、ぼやける"
    **鏡面は、反射の手法（SSR・プローブ・RT）で扱う**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **拡散は低周波、鏡面は高周波**
    - [x] **手法を分担する**

## References {#参考}

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## Related Pages {#関連ページ}

- [GI Theory](index.md)
- [Irradiance](irradiance.md)
- [Reflections](../../reflections/index.md)
