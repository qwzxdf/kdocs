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

## 拡散と鏡面
**BRDF**を**拡散**と**鏡面**に分けると**間接光の性質がまったく違います**。

| 項目 | 拡散の間接光 | 鏡面の間接光 |
| --- | --- | --- |
| **BRDF** | ほぼ一定（ランバート：`albedo / π`） | **鋭いローブ**（粗さで広がる） |
| **視線への依存** | **なし** | **あり** |
| **周波数** | <strong>低い（なめらか）</strong> | <strong>高い（細かい）</strong> |
| **保存のしかた** | **粗い情報で十分**（プローブ・ライトマップ） | **細かい情報が要る**（[Reflections](../../reflections/index.md)） |

<strong>このセクションは、主に「拡散の間接光」</strong>を扱い、**鏡面は、[Reflections](../../reflections/index.md)のセクション**が担当します。

## よくあるミス

??? failure "鏡面の反射も、GI の手法で出そうとして、ぼやける"
    **鏡面は、反射の手法（SSR・プローブ・RT）で扱う**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **拡散は低周波、鏡面は高周波**
    - [x] **手法を分担する**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [GI Theory](index.md)
- [Irradiance](irradiance.md)
- [Reflections](../../reflections/index.md)
