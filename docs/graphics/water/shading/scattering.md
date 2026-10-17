---
title: Scattering Color (SSS-Like)
tags:
  - 描画
---

# Scattering Color (SSS-Like)

**波頭などの薄い部分では、光が水の中で散乱して、明るい緑〜水色に透けて見えます**。**これを SSS 風の近似で表せます**。このページでは、**散乱の色の足し方**を説明します。

!!! tip "ポイント"
    - **波頭（高い所）が、明るく透ける**。
    - **光の方向と視線が近い時に、強くなる**。
    - **高さと太陽方向から、近似で計算**する。
    - **入れすぎると、水が発光して見える**。

## 散乱の色（SSS 風）
**波頭に光が透けて、明るい青緑に光って見える**ことがあります（**太陽を背にして波を見たとき**）。**波の高い所ほど、水が薄く、光が通り抜ける**ためです。

```hlsl
float wave_height_factor = saturate(height_offset / max_wave_height);
float sun_behind = pow(saturate(dot(view_dir, -light_dir)), 4.0);
float3 scatter = scatter_color * wave_height_factor * sun_behind * sun_intensity;
```

| 点 | 説明 |
| --- | --- |
| **波の高さ** | **波頂ほど強い** |
| **太陽の向き** | **太陽が水面の向こう（視線と反対）にあるとき強い** |
| **色** | **明るい青緑**（例：(0.1, 0.5, 0.45)） |

## よくあるミス

??? failure "水がぼんやり光って見える"
    **散乱の強さを抑える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **波頭の透け感を、近似で足す**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Water Shading](index.md)
- [Color by Water Depth](depth-color.md)
