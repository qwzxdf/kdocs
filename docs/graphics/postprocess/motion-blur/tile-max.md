---
title: タイル最大速度
tags:
  - 描画
---

# タイル最大速度

**画素ごとに長い距離を多数サンプル**するのは**重い**うえ、**速い物体の輪郭の外側（背景）の画素は自分の速度が 0 なので、尾が伸びません**。**そこで画面を小さなタイル（例：16×16 画素）に分け、各タイルの「最大の速度」を求め、周囲のタイルの最大速度も合わせた「近傍最大速度」を作る**のが**標準の手法**です。**ぼかしの方向・長さ・スキップの判断に使えます**。このページでは、**TileMax・NeighborMax の 2 段階・実装・使い方・コスト**を説明します。

!!! tip "ポイント"
    - TileMax ＝ <strong>各タイル（16×16 画素）内で最大の速度ベクトル</strong>（<strong>長さが最大のもの</strong>）。
    - NeighborMax ＝ <strong>周囲 3×3 タイルの TileMax の中で、最大のもの</strong>。<strong>隣のタイルの速い動きが、流れ込む</strong>のを考慮。
    - ぼかしの<strong>方向と長さ</strong>は<strong>NeighborMax</strong>から決める。<strong>輪郭の外にも尾が伸びる</strong>。
    - <strong>NeighborMax の長さが閾値以下のタイル</strong>は<strong>ぼかしをスキップ</strong>（<strong>高速化</strong>）。
    - <strong>タイル サイズ ＝ 最大ブラー長</strong>にそろえる。
    - <strong>タイルの数は少ない</strong>（1080p で 120×68）。<strong>コストは小さい</strong>。

## なぜ必要か

**速い物体のブラー**は、**物体の外側にも**尾を引くべきです。**画素 P 自身の速度**だけを**使う**と、**P が背景（速度 0）なら、ぼけません**。**P の近くに速い物体があれば、その速度の分だけ、P の周りを見る必要があります**。

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="タイルの最大速度">
<text x="20" y="26" class="fig-title">タイルの最大速度：近くにある速い動きを、周りの画素に知らせる</text>
<g transform="translate(40,56)">
<rect x="0" y="0" width="320" height="140" fill="#f8fafc" stroke="#94a3b8"/>
<g stroke="#e2e8f0"><line x1="80" y1="0" x2="80" y2="140"/><line x1="160" y1="0" x2="160" y2="140"/><line x1="240" y1="0" x2="240" y2="140"/><line x1="0" y1="35" x2="320" y2="35"/><line x1="0" y1="70" x2="320" y2="70"/><line x1="0" y1="105" x2="320" y2="105"/></g>
<rect x="165" y="45" width="30" height="20" fill="#2563eb"/>
<line x1="165" y1="55" x2="130" y2="55" stroke="#e5484d" stroke-width="3" marker-end="url(#tm2-arrow)"/>
<defs><marker id="tm2-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#e5484d"/></marker></defs>
<rect x="160" y="35" width="80" height="35" fill="#e5aa28" fill-opacity="0.35"/>
<text x="164" y="30" style="font-size:11px">速い物体を含むタイル</text>
<rect x="80" y="35" width="80" height="35" fill="#e5484d" fill-opacity="0.2"/>
<text x="84" y="88" style="font-size:11px">隣のタイル（背景）にも伝える</text>
</g>
<g font-size="13"><text x="400" y="90" style="font-weight:700">2 段階</text>
<text x="400" y="116">① TileMax：各タイルの最大速度</text>
<text x="400" y="140">② NeighborMax：周囲 3×3 の最大</text>
<text x="400" y="176" style="font-weight:700">→ 背景のタイルにも、物体の速度が伝わる</text></g>
</svg>

## 手順

| 手順 | 内容 |
| --- | --- |
| **① TileMax** | **各タイル内の速度のうち、長さが最大のベクトル**を**求める**（**共有メモリで縮約**） |
| **② NeighborMax** | **周囲 3×3 の TileMax の最大**を**求める** |
| **③ ぼかし** | **NeighborMax の方向・長さ**で**サンプル**する |

## ① TileMax

```hlsl
Texture2D<float2> velocity_buffer : register(t0);
RWTexture2D<float2> tile_max : register(u0);

groupshared float2 s_velocity[256];

[numthreads(16, 16, 1)]
void TileMaxMain(uint3 id : SV_DispatchThreadID, uint3 group_id : SV_GroupID, uint group_index : SV_GroupIndex) {
  float2 v = velocity_buffer.Load(int3(id.xy, 0));
  s_velocity[group_index] = v;
  GroupMemoryBarrierWithGroupSync();
  for (uint stride = 128; stride > 0; stride >>= 1) {
    if (group_index < stride) {
      float2 other = s_velocity[group_index + stride];
      if (dot(other, other) > dot(s_velocity[group_index], s_velocity[group_index])) {
        s_velocity[group_index] = other;
      }
    }
    GroupMemoryBarrierWithGroupSync();
  }
  if (group_index == 0) tile_max[group_id.xy] = s_velocity[0];
}
```

| 点 | 説明 |
| --- | --- |
| **16×16 のグループ ＝ 1 タイル** | **1 グループが 1 タイルを担当** |
| **`dot(v, v)`（長さの 2 乗）で比較** | **平方根を避ける** |
| **共有メモリでの縮約** | **256 → 1 を 8 回の比較**で**求める** |

## ② NeighborMax

<strong>TileMax の画像（小さい）</strong>を**読み、周囲 3×3 の最大**を**取ります**。

```hlsl
Texture2D<float2> tile_max_texture : register(t0);
RWTexture2D<float2> neighbor_max : register(u0);

[numthreads(8, 8, 1)]
void NeighborMaxMain(uint3 id : SV_DispatchThreadID) {
  float2 best = 0;
  float best_length_sq = 0;
  for (int y = -1; y <= 1; ++y) {
    for (int x = -1; x <= 1; ++x) {
      int2 p = clamp(int2(id.xy) + int2(x, y), 0, tile_count - 1);
      float2 v = tile_max_texture.Load(int3(p, 0));
      float len_sq = dot(v, v);
      if (len_sq > best_length_sq) {
        best = v;
        best_length_sq = len_sq;
      }
    }
  }
  neighbor_max[id.xy] = best;
}
```

| 点 | 説明 |
| --- | --- |
| **3×3** | **隣のタイルの速い物体が、1 タイル先まで影響する**ため（**タイルの大きさ ＝ 最大ブラー長**） |
| **端は `clamp`** | **画面の外は端のタイルを繰り返す** |

### より正確な NeighborMax

**単純な 3×3 の最大**は、**向きを無視して長さだけ**で選びます。<strong>「そのタイルの速度が自分のタイルに向かっているか」</strong>を**考慮**する**と**、**より正確**です（**McGuire 方式**）。

## ぼかしでの使い方

```hlsl
float2 neighbor_velocity = neighbor_max.SampleLevel(point_clamp, uv, 0).xy;
float neighbor_length = length(neighbor_velocity * resolution);
if (neighbor_length < kMinVelocityPixels) {
  return scene_color.SampleLevel(point_clamp, uv, 0).rgb;
}
```

| 用途 | 内容 |
| --- | --- |
| **ぼかしの方向** | **NeighborMax の向きにサンプルを配置** |
| **ぼかしの長さ** | **NeighborMax の長さ**（**最大ブラー長で制限**） |
| **スキップ判定** | **長さが小さいタイル（< 0.5 画素）は、ぼかしを省略** |
| **自分の速度との組み合わせ** | **サンプルの重み付けに自分の速度も使う**（[ぼかしの実装](blur-pass.md)） |

## コスト

| 項目 | 内容 |
| --- | --- |
| **TileMax** | **フル解像度の速度を 1 回読む**（**帯域は R16G16 のみ**） |
| **NeighborMax** | <strong>タイル数分（1080p で 120×68）</strong>。**ほぼ無料** |
| **効果** | **静止している多くの画素で、ぼかしをスキップ**。**フレーム全体で大幅に節約** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **タイル サイズ ＝ 最大ブラー長** | **16〜20 画素が一般的** |
| **NeighborMax に向きを考慮** | **精度が上がる** |
| **スキップ判定で分岐の一貫性** | **タイル単位で同じ分岐になり、GPU が効率的** |
| **DOF のタイルと共用** | **同じ 16×16 のタイルで、DOF の最大 CoC も計算**（[前景と背景](../dof/near-far.md)） |

## よくあるミス

??? failure "NeighborMax を使わず、輪郭の外にブラーが出ない"
    **周囲の速度をタイルの最大で伝える**。

??? failure "タイルの大きさがブラー長より小さく、速い物体の尾が届かない"
    **タイル サイズ ≧ 最大ブラー長**にする。

??? failure "画面の端のタイルで、範囲外を読んで壊れる"
    **`clamp` で端をそろえる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>TileMax</strong> ＝ <strong>タイルごとの最大速度</strong>。<strong>NeighborMax</strong> ＝ <strong>周囲 3×3 の最大</strong>
    - [x] <strong>背景の画素にも、近くの速い物体の速度を伝え、尾を伸ばす</strong>
    - [x] <strong>遅いタイルは、ぼかしをスキップ</strong>（<strong>高速化</strong>）
    - [x] <strong>タイル サイズ ＝ 最大ブラー長</strong>
    - [x] <strong>共有メモリで縮約</strong>

## 参考

- McGuire et al., "A Reconstruction Filter for Plausible Motion Blur"（I3D 2012）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）

## 関連ページ

- [モーション ブラー](index.md)
- [速度バッファ](velocity-buffer.md)
- [ぼかしの実装](blur-pass.md)
- [前景と背景（DOF）](../dof/near-far.md)
