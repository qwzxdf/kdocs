---
title: Terrain Texturing
tags:
  - 描画
---

# Terrain Texturing

**地形は広いので、1 枚の大きな画像では足りず、草・土・岩などのタイル テクスチャを、混ぜて貼ります**。**これを「スプラット マッピング」と呼びます**。このセクションでは、**スプラット・重み・高さブレンド・トライプラナー・繰り返しを隠す・異方性フィルタ・仮想テクスチャ・デカール**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **複数のタイル テクスチャを、重みで混ぜる**。
    - **急斜面は、トライプラナーで伸びを防ぐ**。
    - **繰り返しは、目立つので、隠す工夫**が要る。
    - **広大な地形は、仮想テクスチャ**。

## スプラット マッピング
**スプラット マップ**は、**各位置で「どのテクスチャをどれだけ使うか」を表す重みテクスチャ**です。**RGBA の 4 チャンネルで 4 種類**を**扱います**。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="スプラット マッピング">
<text x="20" y="24" class="fig-title">スプラット マッピング：重みマップで、複数の地面テクスチャを混ぜる</text>
<rect x="40" y="60" width="140" height="100" fill="#2ea043" fill-opacity="0.5" stroke="currentColor" stroke-opacity="0.5"/>
<rect x="190" y="60" width="140" height="100" fill="#a0763c" fill-opacity="0.6" stroke="currentColor" stroke-opacity="0.5"/>
<rect x="340" y="60" width="140" height="100" fill="#8a8a8a" fill-opacity="0.6" stroke="currentColor" stroke-opacity="0.5"/>
<rect x="490" y="60" width="140" height="100" fill="#f0f4f8" fill-opacity="0.8" stroke="currentColor" stroke-opacity="0.5"/>
<text x="110" y="180" text-anchor="middle" style="font-size:12px">草（R）</text>
<text x="260" y="180" text-anchor="middle" style="font-size:12px">土（G）</text>
<text x="410" y="180" text-anchor="middle" style="font-size:12px">岩（B）</text>
<text x="560" y="180" text-anchor="middle" style="font-size:12px">雪（A）</text>
<text x="400" y="52" text-anchor="middle" style="font-size:12px">繰り返しテクスチャ</text>
<text x="700" y="100" text-anchor="middle" style="font-size:13px">× 重み</text>
<text x="700" y="124" text-anchor="middle" style="font-size:13px">（スプラット）</text>
<text x="700" y="148" text-anchor="middle" style="font-size:13px">＝ 地面の色</text>
</svg>

```hlsl
Texture2D<float4> splat_map : register(t0);
Texture2DArray<float4> albedo_array : register(t1);
Texture2DArray<float4> normal_array : register(t2);

float4 weights = splat_map.Sample(linear_clamp, terrain_uv);
weights /= (weights.r + weights.g + weights.b + weights.a + 1e-5);

float2 tile_uv = world_position.xz * tile_scale;
float3 color = 0;
float3 normal_ts = 0;
for (int i = 0; i < 4; ++i) {
  float3 uvw = float3(tile_uv, i);
  color += albedo_array.Sample(linear_wrap, uvw).rgb * weights[i];
  normal_ts += (normal_array.Sample(linear_wrap, uvw).xyz * 2.0 - 1.0) * weights[i];
}
normal_ts = normalize(normal_ts);
```

| 点 | 説明 |
| --- | --- |
| **スプラット マップは地形全体** | **解像度は高さマップと同程度かそれ以上**。**低解像度だと境目がぼやける** |
| **テクスチャ配列** | **層ごとに別のテクスチャを持たず、`Texture2DArray` にまとめる**（**スロットを節約**） |
| **重みの正規化** | **合計を 1 にする**（**暗くなる・明るくなる**のを防ぐ） |
| **タイルの UV** | **ワールド座標 × スケール**。**メッシュの UV に依らず、継ぎ目が出ない** |
| **層数が多い** | **スプラット マップを複数枚にして、重みの大きい上位 4 つだけ読む** |
| **法線・粗さも混ぜる** | **アルベドだけでなく、法線・粗さ・AO も同じ重みで** |

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Splat Weights](weights.md) | 高さ・傾き・ペイントで決める |
| [Height-Based Blending](height-blend.md) | 境目を自然に |
| [Triplanar Mapping](triplanar.md) | 急斜面の伸びを防ぐ |
| [Hiding Tiling](tiling.md) | タイリングの隠し方 |
| [異方性フィルタ](anisotropic.md) | 斜めから見た時のぼけ |
| [Virtual Texturing](virtual-texture.md) | 巨大なテクスチャ |
| [デカールと道](decals.md) | 道・足跡の表現 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **スプラットで混ぜ、トライプラナーで伸びを防ぐ**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain](../index.md)
- [LOD](../lod/index.md)
