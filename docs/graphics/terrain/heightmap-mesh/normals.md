---
title: Terrain Normals
tags:
  - 描画
---

# Terrain Normals

**地形の陰影は、法線で決まります**。**高さマップの隣り合う画素の差から、傾きを求めて、法線にします**。**あらかじめ法線マップとして保存**しておくと、**実行時が軽く**なります。このページでは、**地形の法線の求め方**を説明します。

!!! tip "ポイント"
    - **法線 ＝ 隣の高さの差（中央差分）から求める**。
    - **事前に法線マップを作っておくと、軽い**。
    - **LOD で頂点が減っても、法線マップで細部を保てる**。
    - **精度が足りないと、段々（バンディング）が出る**。

## Normals {#法線}
**地形の法線**は**高さマップの勾配**から**求めます**。**隣のテクセルとの高さの差**（**中心差分**）を使います。

<div class="formula">N = normalize( (h_left − h_right,　2·Δ,　h_down − h_up) )　（Δ：テクセル間のワールド距離）</div>

```hlsl
float3 TerrainNormal(float2 uv) {
  float2 texel = 1.0 / height_map_size;
  float hl = height_map.SampleLevel(linear_clamp, uv - float2(texel.x, 0), 0) * height_scale;
  float hr = height_map.SampleLevel(linear_clamp, uv + float2(texel.x, 0), 0) * height_scale;
  float hd = height_map.SampleLevel(linear_clamp, uv - float2(0, texel.y), 0) * height_scale;
  float hu = height_map.SampleLevel(linear_clamp, uv + float2(0, texel.y), 0) * height_scale;
  float texel_world = terrain_size / height_map_size.x;
  return normalize(float3(hl - hr, 2.0 * texel_world, hd - hu));
}
```

| 方式 | 内容 |
| --- | --- |
| **頂点で計算** | **頂点の数だけ**。**頂点が粗いと細かい起伏が出ない** |
| **ピクセルで計算** | **ピクセルごとに高さマップから**。**細かく滑らか**（**頂点が粗くても見た目の凹凸は高さマップの解像度**） |
| **法線マップを焼く** | **事前に法線マップを作る**。**ピクセルで 1 回読むだけ**（**メモリは増える**） |
| **Sobel フィルタ** | **8 近傍でより滑らか**（ノイズの多い高さに有効） |

**法線を計算する `Δ`** は、**高さのスケールと揃えます**（**テクセル間のワールド距離**）。**ここがずれると斜面が急すぎる・緩すぎる見た目**になります。

## Common Mistakes {#よくあるミス}

??? failure "地形の陰影に、段々の模様が出る"
    **高さマップを 16bit** にする。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **隣の高さの差で、法線を求める**

## References {#参考}

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## Related Pages {#関連ページ}

- [Heightmaps and Meshes](index.md)
- [Grid Mesh](grid-mesh.md)
