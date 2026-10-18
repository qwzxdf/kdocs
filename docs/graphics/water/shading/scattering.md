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

## Scattering Color (SSS-Like) {#散乱の色sss-風}
**波頭に光が透けて、明るい青緑に光って見える**ことがあります（**太陽を背にして波を見たとき**）。**波の高い所ほど、水が薄く、光が通り抜ける**ためです。

```hlsl
float wave_height_factor = saturate(height_offset / max_wave_height);
float sun_behind = pow(saturate(dot(view_dir, -light_dir)), 4.0);
float3 scatter = scatter_color * wave_height_factor * sun_behind * sun_intensity;
```

コードの要点です。波の高さが高い波頂ほど、散乱の寄与が強くなります。太陽が水面の向こう（視線と反対）にあるときにも強く出ます。色は、明るい青緑（例：(0.1, 0.5, 0.45)）です。

### Why Wave Crests Glow Translucent {#なぜ波頂が透けて光るのか}

波頂では水の層が薄く、背後から来た太陽光が水の中を通り抜けて、目に届きます。このとき、水が光を散乱して青緑に光るので、波頂が内側から光っているような透け感が出ます。これを SSS（表面下散乱）風と呼びますが、実際には皮膚や大理石のような本格的な SSS 計算ではなく、「波の高さ」「太陽の向き」「視線」の 3 つから決める、簡易な近似です。

式の形は、`散乱の色 × 波頂の高さ × max(0, dot(視線, 太陽方向)) ^ k × 太陽の強さ` のようになります。dot の項は、太陽が視線の向こう側にあるときに大きくなり、k で広がりを絞ります。この項を、屈折の色に足せば、波が逆光で光る効果が出ます。夕方の海で、波の向こうに太陽があるとき、波の頂が緑色に透けて光るのは、この効果です。

## Common Mistakes {#よくあるミス}

??? failure "水がぼんやり光って見える"
    **散乱の強さを抑える**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **波頭の透け感を、近似で足す**

## References {#参考}

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## Related Pages {#関連ページ}

- [Water Shading](index.md)
- [Color by Water Depth](depth-color.md)
