---
title: 密度のモデル
tags:
  - 描画
---

# 密度のモデル

**雲の形は、ノイズで作ります**。**低周波のノイズで大きな形、高周波のノイズで細部**を**作り、重ねます**。このページでは、**雲の密度のモデル**を説明します。

!!! tip "ポイント"
    - **基本形：Perlin-Worley ノイズ**。
    - **細部：高周波のノイズで、縁を削る**。
    - **カバレッジで、雲の量を制御**。
    - **3D テクスチャに事前計算して、実行時に読む**。

## 密度のモデル
**雲の密度は複数の要素を掛け合わせて作ります**。

| 要素 | 役割 |
| --- | --- |
| <strong>天気マップ（2D）</strong> | **どこに雲があるか（被覆率）・どんな種類か** |
| <strong>高さの形（ゲイン）</strong> | **層の下と上で薄くなる**（**雲の底は平ら、頂は丸い**） |
| **基本形の 3D ノイズ** | **雲全体の大まかな塊**（低周波。Perlin–Worley） |
| **ディテールの 3D ノイズ** | **塊の縁の細かい凹凸**（高周波。Worley） |
| **風の流れ** | **ノイズの座標を時間で動かす** |

```hlsl
float CloudDensity(float3 position, float height_fraction) {
  float coverage = weather_map.SampleLevel(linear_wrap, position.xz * weather_scale, 0).r;
  float height_gradient = saturate(Remap(height_fraction, 0.0, 0.1, 0.0, 1.0))
                        * saturate(Remap(height_fraction, 0.6, 1.0, 1.0, 0.0));

  float3 shape_uvw = position * shape_scale + wind * time;
  float4 noise = shape_noise.SampleLevel(linear_wrap, shape_uvw, 0);
  float shape_fbm = dot(noise.gba, float3(0.5, 0.25, 0.125)) ;
  float base = Remap(noise.r, shape_fbm - 1.0, 1.0, 0.0, 1.0);

  float density = Remap(base * height_gradient, 1.0 - coverage, 1.0, 0.0, 1.0) * coverage;

  if (density > 0.0) {
    float3 detail_uvw = position * detail_scale + wind * time * 2.0;
    float3 detail = detail_noise.SampleLevel(linear_wrap, detail_uvw, 0).rgb;
    float detail_fbm = dot(detail, float3(0.5, 0.25, 0.125));
    float detail_mix = lerp(detail_fbm, 1.0 - detail_fbm, saturate(height_fraction * 5.0));
    density = Remap(density, detail_mix * detail_strength, 1.0, 0.0, 1.0);
  }
  return max(density, 0.0);
}

float Remap(float v, float a, float b, float c, float d) {
  return c + (v - a) / (b - a) * (d - c);
}
```

| 点 | 説明 |
| --- | --- |
| **`Remap`** | **値の範囲を変換する道具**。**閾値で塊を切り出すのに便利** |
| **`height_fraction`** | **層の下端を 0、上端を 1 とした位置** |
| **`height_gradient`** | **下と上で薄くなる山型**（底が柔らかく、頂が丸く） |
| <strong>被覆率（coverage）</strong> | **大きいほど雲が多い** |
| **ディテールは密度がある所だけ** | **`if (density > 0)` で計算を省く** |
| **3D ノイズは事前生成** | **128³ と 32³ のテクスチャ**（Perlin と Worley を重ねる） |

**ノイズ テクスチャ**は**事前に生成**します（Perlin ノイズに Worley ノイズを重ね、4 チャンネルに異なる周波数を入れる）。

## よくあるミス

??? failure "雲の縁が、なめらかすぎる"
    **高周波のノイズ**で**縁を削る**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **低周波で形、高周波で細部**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [雲](index.md)
- [雲の層](layers.md)
- [レイマーチ](raymarch.md)
