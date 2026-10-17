---
title: 高さマップとメッシュ
tags:
  - 描画
---

# 高さマップとメッシュ

**地形の形**は、<strong>「各 (x, z) に対する高さ y」を並べた表（高さマップ）</strong>で表すのが**基本**です。**平らな格子メッシュの各頂点を、高さマップの値だけ持ち上げる**と、**起伏のある地形**になります。このページでは、**高さマップの持ち方・格子メッシュの作り方・法線の求め方・任意の位置の高さの取り方・チャンク分割**を説明します。

!!! tip "ポイント"
    - 高さマップ ＝ <strong>2D テクスチャの各テクセルが「高さ」</strong>。<strong>XZ の位置がそのまま UV</strong>。
    - 精度は<strong>16 ビット</strong>が目安（<strong>8 ビットは段々になる</strong>）。
    - メッシュ ＝ <strong>平らな格子</strong>を、<strong>頂点シェーダーで高さマップを読んで持ち上げる</strong>。
    - 法線 ＝ <strong>高さマップの勾配</strong>（<strong>中心差分</strong>）。<strong>頂点でなく、ピクセルで求める</strong>と<strong>滑らか</strong>。
    - 地面の高さ（当たり判定・配置）は<strong>高さマップを双線形補間</strong>して<strong>取る</strong>。
    - 大きな地形は<strong>チャンク（タイル）に分割</strong>して<strong>見える所だけ描く</strong>。

## 高さマップ

**高さマップ**は**白黒の画像**です。**明るいほど高く、暗いほど低い**。

<svg class="fig illust" viewBox="0 0 780 240" role="img" aria-label="高さマップと地形">
<text x="20" y="24" class="fig-title">高さマップ（左）と、それを持ち上げた地形の断面（右）</text>
<defs>
<linearGradient id="hmg" x1="0" x2="1"><stop offset="0" stop-color="#202020"/><stop offset="0.25" stop-color="#707070"/><stop offset="0.5" stop-color="#f0f0f0"/><stop offset="0.75" stop-color="#808080"/><stop offset="1" stop-color="#303030"/></linearGradient>
</defs>
<rect x="40" y="50" width="240" height="160" fill="url(#hmg)" stroke="currentColor" stroke-opacity="0.5"/>
<text x="160" y="228" text-anchor="middle" style="font-size:12px">明るい ＝ 高い</text>
<line x1="330" y1="200" x2="740" y2="200" stroke="currentColor" stroke-opacity="0.4"/>
<polyline fill="#2ea043" fill-opacity="0.25" stroke="#2ea043" stroke-width="3" points="330,200 330,190 400,170 470,120 530,70 580,95 640,150 700,175 740,185 740,200"/>
<text x="540" y="62" text-anchor="middle" style="font-size:12px">山頂</text>
<line x1="280" y1="130" x2="330" y2="130" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="4 4"/>
</svg>

| 形式 | 内容 |
| --- | --- |
| <strong>8 ビット（256 段階）</strong> | **軽いが高さが段々になる**。**広い地形には粗い** |
| <strong>16 ビット（65536 段階）</strong> | **標準**。**`R16_UNORM`**。**高さの範囲を 0〜1 に正規化し、スケールで実際の高さに戻す** |
| **32 ビット浮動小数** | **精度は十分だが大きい**。**生成・編集時に使う** |
| **読み込み元** | <strong>画像（PNG16・RAW）・地形ツール（World Machine・Gaea）の出力・実測データ（DEM）</strong> |

**実際の高さ**は**マップの値にスケールを掛けて求めます**。

<div class="formula">高さ(x, z) = height_map(x / world_size, z / world_size) × height_scale + base_height</div>

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
| **時計回りが表** | **左手系・Y 上・+Z 前方**で**上から見て時計回り**（[座標系](../../3d/index.md)） |
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

## 法線

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

## 任意の位置の高さを取る

**キャラクターを地面に立たせる・草を置く・当たり判定**には、**CPU で任意の (x, z) の高さ**が**必要**です。**高さマップの 4 点を、双線形補間**します。

```cpp
float SampleHeight(const HeightMap& map, float world_x, float world_z) {
  float u = (world_x - map.origin_x) / map.cell_size;
  float v = (world_z - map.origin_z) / map.cell_size;
  int x0 = static_cast<int>(std::floor(u));
  int z0 = static_cast<int>(std::floor(v));
  float fx = u - x0;
  float fz = v - z0;

  float h00 = map.At(x0, z0);
  float h10 = map.At(x0 + 1, z0);
  float h01 = map.At(x0, z0 + 1);
  float h11 = map.At(x0 + 1, z0 + 1);

  float h0 = h00 + (h10 - h00) * fx;
  float h1 = h01 + (h11 - h01) * fx;
  return h0 + (h1 - h0) * fz;
}
```

| 点 | 説明 |
| --- | --- |
| **双線形補間** | **4 点を補間**して**滑らかな高さ** |
| **メッシュの三角形と一致させる** | **見た目のメッシュは三角形 2 枚**なので、**厳密には三角形に沿って補間する**と**ずれない**（**足が浮く・めり込む**を防ぐ） |
| **GPU と同じデータ** | **CPU 側にも同じ高さマップを保持** |
| **範囲外** | **`At` は端にクランプ** |

**対角線方向の三角形に沿った補間**は、**マス内の位置 (fx, fz) が `fx + fz < 1` かどうか**で**三角形を選び**、**その三角形上の平面の式**で**高さを出します**。

## チャンクに分割する

**広大な地形を 1 枚のメッシュで描く**と、**画面外も全部描いてしまいます**。**チャンク（タイル）に分けて、見える所だけ描きます**。

| 項目 | 内容 |
| --- | --- |
| **チャンクのサイズ** | **32〜128 マス四方**（**頂点が 65×65・129×129** など） |
| **視錐台カリング** | **チャンクごとに AABB を持ち、視錐台の外を描かない** |
| **AABB の高さ** | **チャンク内の最小・最大の高さを事前に計算して持つ** |
| **メッシュの共有** | **全チャンクで同じ格子メッシュ**を使い、**位置と高さマップの範囲**だけを**渡す**（インスタンシング） |
| **ストリーミング** | **カメラ周りのチャンクだけ、高さマップを読み込む** |

```cpp
struct TerrainChunk {
  int grid_x;
  int grid_z;
  float min_height;
  float max_height;
  BoundingBox bounds;
  int lod_level;
};
```

**チャンクごとに LOD を変える**と、**遠くのチャンクを粗くして**、**三角形の数を大きく減らせます**（[LOD](lod.md)）。

## 高さマップの編集

| 方法 | 内容 |
| --- | --- |
| **ブラシで盛る・削る** | **高さマップに丸いブラシを加算・減算** |
| **平らにする・均す** | **平均を取って、段差をならす** |
| <strong>ステップ（段丘）</strong> | **高さを丸めて、段々にする** |
| **道・建物の整地** | **指定範囲を一定の高さに合わせる**（**スプライン沿いに整地**） |
| **ランタイムの変形** | **爆発で穴が開く**など。**高さマップを書き換え、法線・当たり判定も更新** |

## よくあるミス

??? failure "高さが 8 ビットで、地形が段々（階段）になる"
    **16 ビット以上の高さマップ**を使う。

??? failure "法線の Δ（テクセル間距離）を間違えて、斜面の明暗がおかしい"
    **`terrain_size / height_map_size`** と**高さスケールを揃える**。

??? failure "頂点シェーダーで `Sample` を呼んでコンパイルが通らない"
    **`SampleLevel` を使う**。

??? failure "遠くの地形が、ちらつく"
    **遠くは粗いミップ レベルで高さを読む**。**LOD で頂点を減らす**。

??? failure "足が地面に浮く・めり込む"
    **CPU の高さ計算をメッシュの三角形と揃える**。**LOD でメッシュが粗いと、実際の見た目とずれる**ので、**当たり判定は最も細かい高さマップで取る**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 地形 ＝ <strong>高さマップ（16 ビット）</strong>を<strong>格子メッシュに読んで、持ち上げる</strong>
    - [x] <strong>頂点シェーダーでは `SampleLevel`</strong>。<strong>遠くは粗いミップ</strong>
    - [x] <strong>法線は高さの中心差分</strong>。<strong>ピクセルで求めると滑らか</strong>
    - [x] <strong>CPU の高さ取得は双線形補間</strong>（<strong>三角形に合わせる</strong>と<strong>ずれない</strong>）
    - [x] <strong>チャンク分割</strong>で<strong>視錐台カリング</strong>、<strong>LOD</strong>

## 参考

- Ulrich, "Rendering Massive Terrains using Chunked Level of Detail Control"（SIGGRAPH 2002）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps"（2010）

## 関連ページ

- [地形](index.md)
- [LOD](lod.md)
- [地形のテクスチャ](texturing.md)
- [地形の生成](generation.md)
