---
title: Terrain Generation
tags:
  - 描画
---

# Terrain Generation

**地形を手で作るのは大変なので、ノイズなどから自動で生成します**。**ノイズを重ねて山を作り、侵食で自然な谷を刻み、川を流す**のが**標準的な流れ**です。このセクションでは、**ノイズ・fBm・リッジ ノイズ・ドメイン ワーピング・高さへの変換・侵食・川と湖・生成のタイミング・配置の生成**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **ノイズを、複数の周波数で重ねると、地形らしくなる**。
    - **侵食を加えると、自然な谷や尾根が出る**。
    - **事前生成か、実行時生成かを選ぶ**。
    - **植生や岩の配置も、生成する**。

## ノイズとは
**ノイズ関数**は**位置を入れると滑らかに変化するランダムな値を返す**関数です。**同じ位置はいつも同じ値**（**決定的**）で、**近い位置は近い値**になります。

| ノイズ | 内容 |
| --- | --- |
| <strong>値ノイズ（Value noise）</strong> | **格子点にランダムな値**を置き、**間を補間**。**簡単だが格子の向きが目立つ** |
| <strong>勾配ノイズ（Perlin / Simplex）</strong> | <strong>格子点にランダムな勾配（向き）</strong>を置き、**その内積を補間**。**自然で滑らか** |
| <strong>ワーリー ノイズ（Worley / セル）</strong> | **ランダムな点からの距離**。**石・細胞・ひび割れのような模様** |

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

| 点 | 説明 |
| --- | --- |
| **`f·f·(3 − 2f)`** | **smoothstep で補間の重みを滑らかに**（**格子の境で傾きが連続**） |
| **ハッシュ関数** | **整数の格子座標から、再現性のある乱数** |
| **値の範囲** | **0〜1**。**使うときは −1〜1 に直すこともある** |

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

| 点 | 説明 |
| --- | --- |
| **補間の重み** | **`6f⁵ − 15f⁴ + 10f³`**（**改良版 Perlin。2 階微分も連続**）。**法線の見た目が滑らか** |
| **値の範囲** | **おおよそ −0.7〜0.7** |
| **Simplex ノイズ** | **正方格子でなく三角格子を使い、方向の偏りと計算量が少ない** |

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [fBm](fbm.md) | ノイズを重ねる |
| [Ridged Noise](ridge.md) | 尖った山脈 |
| [Domain Warping](domain-warp.md) | 歪ませて自然に |
| [高さへの変換](height-conversion.md) | ノイズを地形の高さに |
| [Erosion](erosion.md) | 雨と流れによる地形変化 |
| [Rivers and Lakes](rivers.md) | 水の流れの生成 |
| [When to Generate](timing.md) | 事前か、実行時か |
| [Placement Generation](placement.md) | 木・岩の自動配置 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **ノイズで形、侵食でリアルさ**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain](../index.md)
- [Heightmaps and Meshes](../heightmap-mesh/index.md)
- [Vegetation](../vegetation/index.md)
