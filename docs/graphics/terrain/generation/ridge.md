---
title: Ridged Noise
tags:
  - 描画
---

# Ridged Noise

**通常のノイズは、丸い丘になりがち**で、**山脈の鋭い稜線は出ません**。**ノイズの絶対値を反転させると、尖った稜線ができます**。このページでは、**リッジ ノイズ**を説明します。

!!! tip "ポイント"
    - **1 − |ノイズ|** で、**稜線**ができる。
    - **fBm と同じように重ねて使う**。
    - **山脈・峡谷**に向く。
    - **丘と混ぜて、使い分ける**。

## リッジ ノイズ
**山脈の尾根**を作るには、**ノイズの絶対値を取って反転**します。**ゼロ付近が鋭い尾根**になります。

```hlsl
float RidgedFbm(float2 p, int octaves, float lacunarity, float gain) {
  float sum = 0.0;
  float amplitude = 0.5;
  float weight = 1.0;
  for (int i = 0; i < octaves; ++i) {
    float n = 1.0 - abs(PerlinNoise(p));
    n *= n;
    n *= weight;
    weight = saturate(n * 2.0);
    sum += n * amplitude;
    p *= lacunarity;
    amplitude *= gain;
  }
  return sum;
}
```

コードの要点です。`1 − abs(noise)` で、0 付近の線が尾根になります。`n *= n` で尾根を鋭くします。`weight` で、低い所では細かい起伏を弱め、谷を滑らかに、尾根をごつごつにします。使い分けとして、山地はリッジ、平原は通常の fBm を使い、ノイズでブレンドします。

## よくあるミス

??? failure "山が、丸くて、山脈らしくない"
    **リッジ ノイズ**を混ぜる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **絶対値を反転して、尖らせる**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain Generation](index.md)
- [fBm](fbm.md)
