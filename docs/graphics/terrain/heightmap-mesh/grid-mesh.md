---
title: 格子メッシュ
tags:
  - 描画
---

# 格子メッシュ

**格子状に頂点を並べ、各頂点の高さを、高さマップから読み出して設定**します。**頂点の数が、地形の細かさ**を決めます。このページでは、**格子メッシュの作り方と、頂点の高さ**を説明します。

!!! tip "ポイント"
    - **格子 ＝ 規則的に並べた頂点とインデックス**。
    - **頂点シェーダーで、高さマップを読んで持ち上げる**（頂点テクスチャ フェッチ）。
    - **同じ格子メッシュを、何度も再利用できる**。
    - **頂点が多いほど細かいが、重い**。

## 格子メッシュ
**高さマップの各テクセルに、頂点を 1 つ**対応させると、**格子状のメッシュ**になります。**N×N 頂点の格子は、(N−1)×(N−1) マスで、1 マスが三角形 2 枚**です。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="格子メッシュ">
<text x="20" y="24" class="fig-title">格子メッシュ：1 マスは三角形 2 枚</text>
<g stroke="currentColor" stroke-opacity="0.6" fill="none">
<rect x="100" y="50" width="120" height="120"/><rect x="220" y="50" width="120" height="120"/>
<line x1="100" y1="50" x2="220" y2="170"/><line x1="220" y1="50" x2="340" y2="170"/>
</g>
<circle cx="100" cy="50" r="4" fill="#4c8bf5"/><circle cx="220" cy="50" r="4" fill="#4c8bf5"/><circle cx="340" cy="50" r="4" fill="#4c8bf5"/>
<circle cx="100" cy="170" r="4" fill="#4c8bf5"/><circle cx="220" cy="170" r="4" fill="#4c8bf5"/><circle cx="340" cy="170" r="4" fill="#4c8bf5"/>
<text x="100" y="40" text-anchor="middle" style="font-size:11px">0</text><text x="220" y="40" text-anchor="middle" style="font-size:11px">1</text><text x="340" y="40" text-anchor="middle" style="font-size:11px">2</text>
<text x="100" y="190" text-anchor="middle" style="font-size:11px">N</text><text x="220" y="190" text-anchor="middle" style="font-size:11px">N+1</text><text x="340" y="190" text-anchor="middle" style="font-size:11px">N+2</text>
<text x="420" y="90" style="font-size:13px">頂点番号 ＝ z × N ＋ x</text>
<text x="420" y="116" style="font-size:13px">1 マス ＝ (i, i+1, i+N) と (i+1, i+N+1, i+N)</text>
<text x="420" y="142" style="font-size:13px">時計回りが表（左手系）</text>
</svg>

**頂点は、(x, z) の位置だけ**持てば**十分**です（**高さは頂点シェーダーで読む**）。**メッシュは全タイルで共有**できます。

```cpp
std::vector<uint32_t> BuildGridIndices(uint32_t n) {
  std::vector<uint32_t> indices;
  indices.reserve((n - 1) * (n - 1) * 6);
  for (uint32_t z = 0; z + 1 < n; ++z) {
    for (uint32_t x = 0; x + 1 < n; ++x) {
      uint32_t i = z * n + x;
      indices.push_back(i);
      indices.push_back(i + n);
      indices.push_back(i + 1);
      indices.push_back(i + 1);
      indices.push_back(i + n);
      indices.push_back(i + n + 1);
    }
  }
  return indices;
}
```

| 点 | 説明 |
| --- | --- |
| **時計回りが表** | **左手系・Y 上・+Z 前方**で**上から見て時計回り**（[座標系](../../../3d/index.md)） |
| **対角線の向き** | **一方向に揃えると斜めの縞が出る**ことがある。**交互に切り替える**（**ジグザグ**）と**自然** |
| **インデックス数** | <strong>(N−1)² × 6</strong>。**65×65 頂点で約 2.5 万** |

### 頂点シェーダーで高さを読む

```hlsl
Texture2D<float> height_map : register(t0);
SamplerState linear_clamp : register(s0);

cbuffer TerrainParams : register(b1) {
  float2 terrain_origin;
  float terrain_size;
  float height_scale;
  float base_height;
};

VSOutput VSMain(VSInput input) {
  float2 world_xz = terrain_origin + input.grid_position * tile_size;
  float2 uv = (world_xz - terrain_origin_global) / terrain_size;
  float height = height_map.SampleLevel(linear_clamp, uv, 0) * height_scale + base_height;

  float3 world_position = float3(world_xz.x, height, world_xz.y);
  VSOutput output;
  output.position = mul(float4(world_position, 1), view_projection);
  output.world_position = world_position;
  output.uv = uv;
  return output;
}
```

| 点 | 説明 |
| --- | --- |
| **`SampleLevel`** | **頂点シェーダーでは、ミップ レベルを自分で指定**（`Sample` は使えない） |
| **ミップ レベルを距離で選ぶ** | **遠くの頂点は粗いミップから読む**と**ちらつかない** |
| **UV はワールド座標から** | **タイルの位置が違っても、同じ高さマップを共有** |

## よくあるミス

??? failure "地形がカクカクして見える"
    **頂点密度を上げる**・**法線を滑らかに**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **格子の頂点を、高さマップで持ち上げる**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [高さマップとメッシュ](index.md)
- [LOD](../lod/index.md)
