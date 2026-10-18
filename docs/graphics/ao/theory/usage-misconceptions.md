---
title: Usage and Misconceptions of AO
tags:
  - 描画
---

# Usage and Misconceptions of AO

<strong>AO は、間接光の「拡散」を暗くするもの</strong>で、<strong>直接光には掛けません</strong>。これを間違えると、画面が不自然に暗くなります。このページでは、AO の正しい適用先・スペキュラ遮蔽・よくある誤解を説明します。

!!! tip "ポイント"
    - AO は、環境光（間接拡散）に掛ける。直接光には掛けない。
    - スペキュラの環境光にはスペキュラ遮蔽（別の式）。
    - AO を全体に掛けて、画面を暗くするのは誤用。
    - よくある誤解：AO ＝ 影・AO ＝ 常に暗くなるもの。

## AO の使い方

### 掛ける相手：間接光の拡散項だけ

AO は「環境光（空や周囲から来る間接光）が、周囲の物にどれだけ遮られるか」を表します。ライト 1 つ 1 つの向きや位置は考えていない量です。そのため、太陽やスポットライトのような<strong>直接光に掛けてはいけません</strong>。直接光の遮蔽は、シャドウ マップなどでライトごとに求めるべきものです。直接光に AO を掛けてしまうと、ライトが当たっている日向の隅まで暗くなり、絵が不自然に汚れます。

```hlsl
float3 ambient = irradiance * albedo * ao;
float3 color = direct_light + ambient;
```

### スペキュラの環境光

IBL（環境マップ）を使うと、環境光は拡散項と鏡面項に分かれます。拡散項には AO をそのまま掛けます。鏡面項（映り込み）に同じ AO を掛けるのは正しくありません。鏡面反射は視線の方向と粗さで決まる狭い方向の光だけを拾うので、拡散用の AO では暗さの程度が合いません。鏡面項には、視線方向と粗さを考えた<strong>スペキュラ遮蔽</strong>という別の式を使います（[GTAO](../gtao.md)）。

### 焼いた AO との併用

メッシュに焼き込んだ AO テクスチャは、<strong>マイクロ AO</strong>（細かいくぼみ・ひび）の役を担います。スクリーン空間 AO は、物体どうしの接触（壁と箱の間など）という、<strong>マクロ AO</strong> の役を担います。両者は役割が違うので、掛け合わせて併用します。同じ領域を二重に暗くしすぎないよう、スクリーン空間の半径は、焼き込みで扱う細かさより大きくしておきます。

### リニア空間で掛ける

AO は<strong>リニアな光の量</strong>に対する係数です。ガンマ空間（sRGB の色のまま）で掛けると、暗部が潰れて見た目が変わります。ライティングの計算が終わるまで、リニア空間のまま処理します（[色の数学](../../../gamemath/color.md)）。

### 強さの調整

`pow(AO, 指数)` で調整します。指数を大きくすると暗い所がより濃くなって、コントラストが上がります。強くしすぎると画面全体が汚れて見えるので、見た目をアーティストが調整できるよう、パラメータを公開しておくとよいでしょう。

## よくある誤解
??? failure "AO は、ライトの影の代わりになる"
    AO は<strong>ライトを考慮しない</strong>ので、<strong>影の向きを表せません</strong>。接地感を出すだけで光源の方向による影は、シャドウ マップなどで別に作ります。

??? failure "AO をシーン全体に掛けて、明るい場所まで暗くなる"
    <strong>間接光だけ</strong>に掛けます。直接光に掛けると<strong>日向まで暗く</strong>なります。

??? failure "半径を大きくして、広い範囲の陰影を出そうとする"
    半径に比例して、サンプルの取りこぼしとコストが増えます。大きな陰影は<strong>間接光の方式</strong>（[GI](../../index.md)）や、ライトマップの役目です。

## よくあるミス

??? failure "直接光（太陽）に AO を掛けて、日向が暗い"
    <strong>AO は、環境光だけ</strong>に掛ける。

## これだけ覚える

!!! abstract "まとめ"
    - [x] AO は、間接拡散にだけ掛ける
    - [x] スペキュラには、スペキュラ遮蔽

## 参考

- Landis, "Production-Ready Global Illumination", SIGGRAPH 2002 Course 16（ambient occlusion の、映画制作での、使われ方）
- Jimenez, Wu, Pesce, Jarabo, "Practical Real-Time Strategies for Accurate Indirect Occlusion", SIGGRAPH 2016, Physically Based Shading in Theory and Practice
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014（スペキュラ オクルージョン）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（Ambient Occlusion の章）

## 関連ページ

- [AO Theory](index.md)
- [AO Artifacts](../artifacts/index.md)
- [PBR](../../../3d/pbr.md)
