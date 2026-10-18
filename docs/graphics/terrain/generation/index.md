---
title: Terrain Generation
tags:
  - 描画
---

# Terrain Generation

**地形を手で作るのは大変なので、ノイズなどから自動で生成します**。**ノイズを重ねて山を作り、侵食で自然な谷を刻み、川を流す**のが**標準的な流れ**です。このセクションでは、**ノイズ・fBm・リッジ ノイズ・ドメイン ワーピング・高さへの変換・侵食・川と湖・生成のタイミング・配置の生成**を、**1 つずつ別のページ**で説明します。

## ノイズとは
**ノイズ関数**は**位置を入れると滑らかに変化するランダムな値を返す**関数です。**同じ位置はいつも同じ値**（**決定的**）で、**近い位置は近い値**になります。

ノイズには 3 種類あります。値ノイズ（Value noise）は、格子点にランダムな値を置き、間を補間します。簡単ですが、格子の向きが目立ちます。勾配ノイズ（Perlin / Simplex）は、格子点にランダムな勾配（向き）を置き、その内積を補間します。自然で滑らかです。ワーリー ノイズ（Worley / セル）は、ランダムな点からの距離で、石・細胞・ひび割れのような模様になります。

### 値ノイズ

**2D の値ノイズ**は、**位置の整数部が属する格子の 4 隅の値を、小数部で補間**します。

```hlsl
float Hash(int2 p) {
  uint h = uint(p.x) * 374761393u + uint(p.y) * 668265263u;
  h = (h ^ (h >> 13)) * 1274126177u;
  return float(h ^ (h >> 16)) / 4294967295.0;
}

float ValueNoise(float2 p) {
  int2 cell = int2(floor(p));
  float2 f = frac(p);
  float2 u = f * f * (3.0 - 2.0 * f);

  float a = Hash(cell);
  float b = Hash(cell + int2(1, 0));
  float c = Hash(cell + int2(0, 1));
  float d = Hash(cell + int2(1, 1));
  return lerp(lerp(a, b, u.x), lerp(c, d, u.x), u.y);
}
```

値ノイズのコードの要点です。`f·f·(3 − 2f)` は smoothstep で補間の重みを滑らかにし、格子の境で傾きが連続になります。ハッシュ関数は、整数の格子座標から再現性のある乱数を作ります。値の範囲は 0〜1 で、使うときは −1〜1 に直すこともあります。

### 勾配ノイズ（Perlin）

**勾配ノイズ**は<strong>各格子点にランダムな単位ベクトル（勾配）</strong>を持ち、**点から位置までのベクトルとの内積**を**補間**します。**値ノイズより、向きの偏りが少なく**、**自然な見た目**です。

```hlsl
float2 GradientAt(int2 p) {
  float angle = Hash(p) * 6.2831853;
  return float2(cos(angle), sin(angle));
}

float PerlinNoise(float2 p) {
  int2 cell = int2(floor(p));
  float2 f = frac(p);
  float2 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);

  float a = dot(GradientAt(cell), f);
  float b = dot(GradientAt(cell + int2(1, 0)), f - float2(1, 0));
  float c = dot(GradientAt(cell + int2(0, 1)), f - float2(0, 1));
  float d = dot(GradientAt(cell + int2(1, 1)), f - float2(1, 1));
  return lerp(lerp(a, b, u.x), lerp(c, d, u.x), u.y);
}
```

Perlin ノイズのコードの要点です。補間の重みは `6f⁵ − 15f⁴ + 10f³` で、改良版の Perlin ノイズです。2 階微分も連続で、法線の見た目が滑らかになります。値の範囲はおおよそ −0.7〜0.7 です。Simplex ノイズは、正方格子でなく三角格子を使い、方向の偏りと計算量が少なくなります。

原典は、Perlin の "An Image Synthesizer"（SIGGRAPH 1985）と、改良版の "Improving Noise"（SIGGRAPH 2002）、Worley の "A Cellular Texture Basis Function"（SIGGRAPH 1996）です。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [fBm](fbm.md) | ノイズを重ねる |
| [Ridged Noise](ridge.md) | 尖った山脈 |
| [Domain Warping](domain-warp.md) | 歪ませて自然に |
| [Converting Noise to Height](height-conversion.md) | ノイズを地形の高さに |
| [Erosion](erosion.md) | 雨と流れによる地形変化 |
| [Rivers and Lakes](rivers.md) | 水の流れの生成 |
| [When to Generate](timing.md) | 事前か、実行時か |
| [Placement Generation](placement.md) | 木・岩の自動配置 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **ノイズで形、侵食でリアルさ**

## 参考

- Ebert, Musgrave, Peachey, Perlin, Worley, "Texturing and Modeling: A Procedural Approach", 3rd Edition, Morgan Kaufmann, 2002（fBm、マルチフラクタル、リッジ ノイズ）
- Perlin, "Improving Noise", SIGGRAPH 2002（補間関数を 5 次式にし、勾配の選び方を直した改良版）
- Musgrave, Kolb, Mace, "The Synthesis and Rendering of Eroded Fractal Terrains", SIGGRAPH 1989
- Mei, Decaudin, Hu, "Fast Hydraulic Erosion Simulation and Visualization on GPU", Pacific Graphics 2007
- Génevaux, Galin, Guérin, Peytavie, Beneš, "Terrain Generation Using Procedural Models Based on Hydrology", ACM Transactions on Graphics (SIGGRAPH 2013)
- Galin, Guérin, Peytavie, Cordonnier, Cani, Beneš, Gain, "A Review of Digital Terrain Modeling", Computer Graphics Forum (Eurographics 2019 STAR)

## 関連ページ

- [Terrain](../index.md)
- [Heightmaps and Meshes](../heightmap-mesh/index.md)
- [Vegetation](../vegetation/index.md)
