---
title: ハッシュド アルファ
tags:
  - 描画
---

# ハッシュド アルファ

**ハッシュド アルファは、画素ごとにランダムなしきい値で clip する手法**で、**平均すると、半透明に見えます**。**TAA と組み合わせると、ノイズが消えて、なめらかな半透明**になります。このページでは、**ハッシュド アルファの仕組み**を説明します。

!!! tip "ポイント"
    - **画素ごとのハッシュで、しきい値を変える**。
    - **平均すると、アルファ値どおりの透明度**。
    - **ソート不要・深度も書ける**。
    - **TAA が前提**（そうでないと、ノイズが見える）。

## ハッシュド アルファ（確率的アルファ テスト）
**アルファを「確率」と見なし、画素ごとのノイズ（ハッシュ）と比べて、捨てるか残すか**を決めます。**1 フレームでは、ノイズ状**ですが、**TAA（時間蓄積）で平均されて、滑らかな半透明**に見えます。

```hlsl
float Hash(float2 p) {
  return frac(sin(dot(p, float2(12.9898, 78.233))) * 43758.5453);
}

float alpha = albedo_texture.Sample(linear_sampler, input.uv).a;
float threshold = Hash(input.position.xy);
clip(alpha - threshold);
```

| 点 | 説明 |
| --- | --- |
| <strong>`threshold`（ランダム）</strong> | **画素ごとに違う閾値**。**アルファが 0.3 なら、約 30% の画素が残る** |
| **TAA と併用** | **毎フレーム、違うノイズ**にすると、**時間平均で滑らかな半透明** |
| **ミップにも強い** | **アルファが薄くなっても、確率的に残る**ので、**スカスカにならない** |
| **欠点** | **TAA がないと、ノイズが見える** |

**ハッシュ（ノイズ）を、ワールド座標・オブジェクト座標**から作る（**Wyman と McGuire の Hashed Alpha Testing**）と、**動いても、ノイズが物体に貼りつく**ので**安定**します。

## よくあるミス

??? failure "ハッシュド アルファのノイズが消えない"
    **TAA を有効**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **ランダムなしきい値で clip**
    - [x] **TAA でなめらかになる**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [アルファ テスト](index.md)
- [TAA](../../postprocess/antialiasing/taa.md)
- [ディザ透明](dither.md)
