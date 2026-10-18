---
title: Grid Mesh
tags:
  - 描画
---

# Grid Mesh

**格子状に頂点を並べ、各頂点の高さを、高さマップから読み出して設定**します。**頂点の数が、地形の細かさ**を決めます。このページでは、**格子メッシュの作り方と、頂点の高さ**を説明します。

!!! tip "ポイント"
    - **格子 ＝ 規則的に並べた頂点とインデックス**。
    - **頂点シェーダーで、高さマップを読んで持ち上げる**（頂点テクスチャ フェッチ）。
    - **同じ格子メッシュを、何度も再利用できる**。
    - **頂点が多いほど細かいが、重い**。

<!-- fig:heightmap-lift:begin -->

<svg class="fig illust motion" data-fig="heightmap-lift" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-heightmap-lift" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">格子メッシュ:高さマップの値で、頂点を持ち上げる</text>
<text x="40" y="78" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">高さマップ（明るい = 高い）</text>
<rect x="66" y="90" width="48" height="34" fill="#6c6c6c"/>
<text x="90" y="140" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">0.15</text>
<rect x="136" y="90" width="48" height="34" fill="#949494"/>
<text x="160" y="140" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">0.30</text>
<rect x="206" y="90" width="48" height="34" fill="#c2c2c2"/>
<text x="230" y="140" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">0.55</text>
<rect x="276" y="90" width="48" height="34" fill="#f3f3f3"/>
<text x="300" y="140" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">0.90</text>
<rect x="346" y="90" width="48" height="34" fill="#d9d9d9"/>
<text x="370" y="140" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">0.70</text>
<rect x="416" y="90" width="48" height="34" fill="#a8a8a8"/>
<text x="440" y="140" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">0.40</text>
<rect x="486" y="90" width="48" height="34" fill="#cacaca"/>
<text x="510" y="140" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">0.60</text>
<rect x="556" y="90" width="48" height="34" fill="#9e9e9e"/>
<text x="580" y="140" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">0.35</text>
<rect x="626" y="90" width="48" height="34" fill="#7b7b7b"/>
<text x="650" y="140" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">0.20</text>
<line x1="60" y1="340" x2="730" y2="340" stroke="#e2e8f0" stroke-width="1.5"/>
<text x="60" y="190" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">メッシュの頂点（最初は平ら）</text>
<circle cx="90" cy="340" r="7" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0870;0.1913;1.0000" values="340;340;317.5;317.5"/></circle>
<circle cx="160" cy="340" r="7" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1304;0.2348;1.0000" values="340;340;295;295"/></circle>
<circle cx="230" cy="340" r="7" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1739;0.2783;1.0000" values="340;340;257.5;257.5"/></circle>
<circle cx="300" cy="340" r="7" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2174;0.3217;1.0000" values="340;340;205;205"/></circle>
<circle cx="370" cy="340" r="7" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2609;0.3652;1.0000" values="340;340;235;235"/></circle>
<circle cx="440" cy="340" r="7" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3043;0.4087;1.0000" values="340;340;280;280"/></circle>
<circle cx="510" cy="340" r="7" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3478;0.4522;1.0000" values="340;340;250;250"/></circle>
<circle cx="580" cy="340" r="7" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3913;0.4957;1.0000" values="340;340;287.5;287.5"/></circle>
<circle cx="650" cy="340" r="7" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4348;0.5391;1.0000" values="340;340;310;310"/></circle>
<line x1="90" y1="340" x2="160" y2="340" stroke="#2563eb" stroke-width="3"><animate attributeName="y1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0870;0.1913;1.0000" values="340;340;317.5;317.5"/><animate attributeName="y2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1304;0.2348;1.0000" values="340;340;295;295"/></line>
<line x1="160" y1="340" x2="230" y2="340" stroke="#2563eb" stroke-width="3"><animate attributeName="y1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1304;0.2348;1.0000" values="340;340;295;295"/><animate attributeName="y2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1739;0.2783;1.0000" values="340;340;257.5;257.5"/></line>
<line x1="230" y1="340" x2="300" y2="340" stroke="#2563eb" stroke-width="3"><animate attributeName="y1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1739;0.2783;1.0000" values="340;340;257.5;257.5"/><animate attributeName="y2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2174;0.3217;1.0000" values="340;340;205;205"/></line>
<line x1="300" y1="340" x2="370" y2="340" stroke="#2563eb" stroke-width="3"><animate attributeName="y1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2174;0.3217;1.0000" values="340;340;205;205"/><animate attributeName="y2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2609;0.3652;1.0000" values="340;340;235;235"/></line>
<line x1="370" y1="340" x2="440" y2="340" stroke="#2563eb" stroke-width="3"><animate attributeName="y1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2609;0.3652;1.0000" values="340;340;235;235"/><animate attributeName="y2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3043;0.4087;1.0000" values="340;340;280;280"/></line>
<line x1="440" y1="340" x2="510" y2="340" stroke="#2563eb" stroke-width="3"><animate attributeName="y1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3043;0.4087;1.0000" values="340;340;280;280"/><animate attributeName="y2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3478;0.4522;1.0000" values="340;340;250;250"/></line>
<line x1="510" y1="340" x2="580" y2="340" stroke="#2563eb" stroke-width="3"><animate attributeName="y1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3478;0.4522;1.0000" values="340;340;250;250"/><animate attributeName="y2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3913;0.4957;1.0000" values="340;340;287.5;287.5"/></line>
<line x1="580" y1="340" x2="650" y2="340" stroke="#2563eb" stroke-width="3"><animate attributeName="y1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3913;0.4957;1.0000" values="340;340;287.5;287.5"/><animate attributeName="y2" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4348;0.5391;1.0000" values="340;340;310;310"/></line>
<polygon points="90,340 160,340 230,340 300,340 370,340 440,340 510,340 580,340 650,340 650,370 90,370" fill="#e7d9b4" fill-opacity="0.9"><animate attributeName="points" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.1076;0.1283;0.1489;0.1696;0.1902;0.2109;0.2315;0.2522;0.2728;0.2935;0.3141;0.3348;0.3554;0.3761;0.3967;0.4174;0.4380;0.4587;0.4793;0.5000;0.5207;0.5413;0.5620;0.5826;1.0000" values="90,340 160,340 230,340 300,340 370,340 440,340 510,340 580,340 650,340 650,370 90,370;90,340 160,340 230,340 300,340 370,340 440,340 510,340 580,340 650,340 650,370 90,370;90,340.0 160,340.0 230,340.0 300,340.0 370,340.0 440,340.0 510,340.0 580,340.0 650,340.0 650,370 90,370;90,335.55 160,340.0 230,340.0 300,340.0 370,340.0 440,340.0 510,340.0 580,340.0 650,340.0 650,370 90,370;90,331.09 160,340.0 230,340.0 300,340.0 370,340.0 440,340.0 510,340.0 580,340.0 650,340.0 650,370 90,370;90,326.64 160,332.03 230,340.0 300,340.0 370,340.0 440,340.0 510,340.0 580,340.0 650,340.0 650,370 90,370;90,322.19 160,323.12 230,340.0 300,340.0 370,340.0 440,340.0 510,340.0 580,340.0 650,340.0 650,370 90,370;90,317.73 160,314.22 230,327.11 300,340.0 370,340.0 440,340.0 510,340.0 580,340.0 650,340.0 650,370 90,370;90,317.5 160,305.31 230,310.78 300,340.0 370,340.0 440,340.0 510,340.0 580,340.0 650,340.0 650,370 90,370;90,317.5 160,296.41 230,294.45 300,321.72 370,340.0 440,340.0 510,340.0 580,340.0 650,340.0 650,370 90,370;90,317.5 160,295.0 230,278.12 300,295.0 370,340.0 440,340.0 510,340.0 580,340.0 650,340.0 650,370 90,370;90,317.5 160,295.0 230,261.8 300,268.28 370,327.97 440,340.0 510,340.0 580,340.0 650,340.0 650,370 90,370;90,317.5 160,295.0 230,257.5 300,241.56 370,307.19 440,340.0 510,340.0 580,340.0 650,340.0 650,370 90,370;90,317.5 160,295.0 230,257.5 300,214.84 370,286.41 440,334.38 510,340.0 580,340.0 650,340.0 650,370 90,370;90,317.5 160,295.0 230,257.5 300,205.0 370,265.62 440,322.5 510,340.0 580,340.0 650,340.0 650,370 90,370;90,317.5 160,295.0 230,257.5 300,205.0 370,244.84 440,310.62 510,333.44 580,340.0 650,340.0 650,370 90,370;90,317.5 160,295.0 230,257.5 300,205.0 370,235.0 440,298.75 510,315.63 580,340.0 650,340.0 650,370 90,370;90,317.5 160,295.0 230,257.5 300,205.0 370,235.0 440,286.88 510,297.81 580,337.27 650,340.0 650,370 90,370;90,317.5 160,295.0 230,257.5 300,205.0 370,235.0 440,280.0 510,280.0 580,326.88 650,340.0 650,370 90,370;90,317.5 160,295.0 230,257.5 300,205.0 370,235.0 440,280.0 510,262.19 580,316.48 650,339.06 650,370 90,370;90,317.5 160,295.0 230,257.5 300,205.0 370,235.0 440,280.0 510,250.0 580,306.09 650,333.12 650,370 90,370;90,317.5 160,295.0 230,257.5 300,205.0 370,235.0 440,280.0 510,250.0 580,295.7 650,327.19 650,370 90,370;90,317.5 160,295.0 230,257.5 300,205.0 370,235.0 440,280.0 510,250.0 580,287.5 650,321.25 650,370 90,370;90,317.5 160,295.0 230,257.5 300,205.0 370,235.0 440,280.0 510,250.0 580,287.5 650,315.31 650,370 90,370;90,317.5 160,295.0 230,257.5 300,205.0 370,235.0 440,280.0 510,250.0 580,287.5 650,310.0 650,370 90,370;90,317.5 160,295.0 230,257.5 300,205.0 370,235.0 440,280.0 510,250.0 580,287.5 650,310.0 650,370 90,370;90,317.5 160,295.0 230,257.5 300,205.0 370,235.0 440,280.0 510,250.0 580,287.5 650,310.0 650,370 90,370;90,317.5 160,295.0 230,257.5 300,205.0 370,235.0 440,280.0 510,250.0 580,287.5 650,310.0 650,370 90,370"/></polygon>
<text x="40" y="400" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">頂点シェーダーで、高さマップの値を読み、頂点の高さにする。格子（頂点とインデックス）は、同じものを使い回せる。</text>
</svg>

<!-- fig:heightmap-lift:end -->

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

格子メッシュのインデックスのコードの要点です。時計回りが表です（左手系・Y 上・+Z 前方で、上から見て時計回り。[座標系](../../../3d/index.md)）。対角線の向きは、一方向に揃えると斜めの縞が出ることがあるので、交互に切り替える（ジグザグ）と自然です。インデックス数は (N−1)² × 6 で、65×65 頂点で約 2.5 万です。

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

高さを読む頂点シェーダーのコードの要点です。`SampleLevel` は、頂点シェーダーではミップ レベルを自分で指定するために使います（`Sample` は使えません）。ミップ レベルを距離で選び、遠くの頂点は粗いミップから読むとちらつきません。UV はワールド座標から求め、タイルの位置が違っても同じ高さマップを共有します。

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

- [Heightmaps and Meshes](index.md)
- [LOD](../lod/index.md)
