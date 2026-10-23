---
title: Vegetation Culling
tags:
  - 描画
---

# Vegetation Culling

<strong>見えない草を描かない</strong>ことが、最大の最適化です。視錐台カリング・距離カリング・オクルージョン カリングを組み合わせます。このページでは植生のカリングを説明します。

!!! tip "ポイント"
    - 視錐台カリング：画面の外を除く。
    - 距離カリング：遠くの草を消す（フェードで）。
    - 区画ごとに行うと、効率的。
    - GPU カリングで、インスタンスごとに判定。

## カリング
<strong>画面に映らない・遠すぎる植生は、描きません</strong>。

| 種類 | 内容 |
| --- | --- |
| 距離カリング | 一定距離より遠い物は描かない（草は 50〜100 m 程度）。フェードで消す |
| 視錐台カリング | 視錐台の外を捨てる |
| オクルージョン カリング | 山や建物の裏は捨てる（Hi-Z） |
| 密度の距離減衰 | 遠いほど、間引く（一部の草だけ描き残りを太くする） |

コンピュート シェーダーで全インスタンスを判定し、生き残ったものを別バッファに詰めます。

```hlsl
[numthreads(64, 1, 1)]
void CullInstances(uint3 id : SV_DispatchThreadID) {
  if (id.x >= instance_count) return;
  GrassInstance instance = all_instances[id.x];
  float distance_to_camera = distance(instance.position, camera_position);
  if (distance_to_camera > max_distance) return;
  if (!SphereInFrustum(instance.position, instance.scale * radius)) return;
  uint index;
  visible_count.InterlockedAdd(0, 1, index);
  visible_instances[index] = instance;
}
```

詳しい構成は[GPU Driven](../../../rendering/index.md) と同じ考え方です。

## カリングを段階にする

草の本数は <strong>数十万〜数百万</strong>です。全インスタンスを 1 本ずつ調べると、調べるだけで重くなります。大きな単位で先に捨て残りだけを、細かく調べる段階的なカリングにします。

| 段階 | 単位 | 方法 | 捨てる量 |
| --- | --- | --- | --- |
| ① 区画（タイル） | 数十メートル四方 | 視錐台、距離。区画の AABB で判定 | 画面外の、ほとんど |
| ② 区画の内部 | 区画内の全インスタンス | 計算シェーダーで、1 本ずつ距離・視錐台 | 残りの、無駄な分 |
| ③ オクルージョン | 区画、またはインスタンス | Hi-Z バッファで、山や建物の裏を捨てる | 遮られた分 |

区画ごとに草のインスタンスを事前に、並べておくと①で捨てた区画の、インスタンスには触れずに済みます。

```cpp
struct GrassTile {
  BoundingBox bounds;           // 草の高さまで含めた AABB
  uint32_t first_instance;      // 全インスタンス バッファの中の、この区画の開始位置
  uint32_t instance_count;
};

// ① 区画のカリング（CPU）。見える区画の、インスタンス範囲を、集める。
std::vector<uint2> ranges;
for (const GrassTile& t : tiles) {
  if (DistanceToAabb(camera.position, t.bounds) > max_distance) continue;
  if (!Visible(camera.frustum, t.bounds)) continue;
  ranges.push_back({t.first_instance, t.instance_count});
}
// ② この範囲だけを、計算シェーダーで、1 本ずつ調べる。
```

## 距離カリングとフェード

遠くの草は <strong>小さくて見えません</strong>。ただし、ある距離でいきなり消すと境目が、目立ちます。

| 方法 | 内容 |
| --- | --- |
| 距離で一斉に消す | 簡単。境目がはっきり見える |
| 草の高さを縮めて消す | 距離で、スケールを 0 に近づけて地面に、沈むように消す |
| 密度を間引く（確率的な消し方） | 距離が遠いほど、一部の草だけ描く。草 1 本ごとの乱数との比較で、決める |
| 面積を補う | 間引いた分、残った草を太くする（草原の密度の印象を、保つ） |

```hlsl
// 距離に応じて、草の描画する確率を下げる。草 1 本ごとに、決まった乱数を使うので、フレームで、ちらつかない。
float DistanceKeepProbability(float dist, float fade_start, float fade_end) {
  return 1.0 - smoothstep(fade_start, fade_end, dist);
}
```

距離に応じて描く確率を下げる関数です。`smoothstep` で近いほど 1、遠いほど 0 になだらかに近づけます。

```hlsl
[numthreads(64, 1, 1)]
void CullGrass(uint3 id : SV_DispatchThreadID) {
  if (id.x >= instance_count) return;
```

1 スレッドが草 1 本を受け持ちます。範囲外のスレッドは何もせずに、戻ります。

```hlsl
  GrassInstance g = g_all_instances[id.x];

  float dist = distance(g.position, camera_position);
  if (dist > fade_end) return;                                  // 遠すぎる
```

草までの距離を求め描画しない、遠さなら捨てます。

```hlsl
  // 1 本ごとに、固定の乱数（0〜1）。確率より小さい物だけ、描く。
  float keep = DistanceKeepProbability(dist, fade_start, fade_end);
  if (g.color_variation > keep) return;                         // 乱数の代わりに、固定の値を使う
```

距離に応じた確率で間引きます。乱数は草 1 本ごとに固定の値（`color_variation`）を、使うのでフレームごとに結果が、変わらずちらつきません。

```hlsl
  // 間引いた分だけ、残りを太くする（面積の保存）
  g.scale *= 1.0 / max(sqrt(keep), 0.3);
```

間引いた分だけ残りの草を太くします。間引くと地面を覆う面積が減って遠くが、すかすかに見えるのを防ぎます。

```hlsl
  if (!SphereInFrustum(g.position + float3(0, g.height * 0.5, 0), g.height)) return;
```

視錐台の外の草を捨てます。残った草だけを「描く草」のバッファに、追加します。

```hlsl
  g_visible.Append(g);
}
```

「1 本ごとの固定の乱数」を使うことが、重要です。フレームごとに乱数を引き直すと、毎フレーム、違う草が消えてちらつきます。

## 視錐台カリング

計算シェーダー内で草の<strong>球</strong>（位置 + 高さの半分を、中心）が視錐台の 6 平面の、内側にあるかを調べます。

```hlsl
cbuffer CullCB : register(b0) {
  float4 frustum_planes[6];       // xyz = 法線（内向き）、w = 距離
  float3 camera_position;
  float fade_start, fade_end;
  uint instance_count;
};

bool SphereInFrustum(float3 center, float radius) {
  [unroll] for (int i = 0; i < 6; ++i) {
    if (dot(frustum_planes[i].xyz, center) + frustum_planes[i].w < -radius) return false;
  }
  return true;
}
```

平面は カメラの視錐台の行列から、CPU で 1 回だけ計算して、定数バッファで渡します。

## オクルージョン カリング（Hi-Z）

山、建物、崖の<strong>裏側の草</strong>は見えないのに、描いています。深度バッファのミップマップ（Hi-Z、各ミップが 4 画素の最も遠い深度）を使って、「草の周りの球が完全に手前の物に、隠れているか」を判定します。

| 手順 | 内容 |
| --- | --- |
| ① 前のフレームの深度から、Hi-Z を作る | 深度のミップを、最大値（遠い方）で縮める |
| ② 草の球を画面に投影する | 球が覆う、画面上の範囲（矩形）と球の最も近い深度を求める |
| ③ 範囲の大きさに合う Hi-Z のミップを、読む | 矩形全体が 1 画素に収まるミップ |
| ④ 比較 | 球の最も近い深度が、Hi-Z の深度より遠いなら、隠れている |

```hlsl
Texture2D<float> g_hiz : register(t1);        // 前のフレームの深度の、Hi-Z（ミップつき）
```

前のフレームの深度から作った、Hi-Z（深度の最大値のミップ）を、読みます。

```hlsl
bool OccludedByHiZ(float3 center, float radius) {
  // 球を、画面に投影した、矩形を求める（簡略化: 中心と半径から）
  float4 clip = mul(float4(center, 1), view_proj);
  float2 ndc = clip.xy / clip.w;
  float2 uv = ndc * float2(0.5, -0.5) + 0.5;
  float screen_radius = radius * proj_scale / clip.w;       // 画面上の半径（UV 単位）
```

草を囲む球を画面に投影して画面上の位置と半径を、求めます。

```hlsl
  // 矩形の大きさに合う、ミップを選ぶ
  float2 size_px = screen_radius * 2.0 * hiz_size;
  float mip = ceil(log2(max(size_px.x, size_px.y)));
```

画面上の矩形の大きさにちょうど合う、ミップを選びます。そのミップでは矩形が 1〜2 画素に、収まるので読み取りが 4 回で、済みます。

```hlsl
  // 矩形の四隅の深度の、最大（最も遠い）を取る
  float2 corner = screen_radius;
  float d = max(max(g_hiz.SampleLevel(g_point, uv + float2(-corner.x, -corner.y), mip),
                    g_hiz.SampleLevel(g_point, uv + float2( corner.x, -corner.y), mip)),
                max(g_hiz.SampleLevel(g_point, uv + float2(-corner.x,  corner.y), mip),
                    g_hiz.SampleLevel(g_point, uv + float2( corner.x,  corner.y), mip)));
```

矩形の 4 隅の深度の最大（最も遠い）を、取ります。これが「この範囲の手前の面が、どこまで遠いか」の保守的な見積もりです。

```hlsl
  // 球の最も近い点の、深度（クリップ空間の z/w）
  float nearest = (clip.z - radius) / (clip.w - radius);
  return nearest > d;     // 球の方が遠い → 隠れている（深度は、遠いほど大きい通常の設定）
}
```

| 注意点 | 内容 |
| --- | --- |
| 前のフレームの深度 | 今のフレームの深度はまだ無い。1 フレーム前の深度を使うので、カメラが速く動くとわずかに取りこぼす。球を少し大きめに取る |
| 草は小さい | 草 1 本の、オクルージョンは効果が小さい。区画の AABB に行うのが、現実的 |
| 逆 Z | 深度の方向を、逆にしている場合（遠いほど小さい）は、比較の向きとミップの縮め方（最小値）を、逆にする |

地形が山岳地帯の場合、山の裏の草の区画をまとめて捨てると、大きく減らせます。

## カリングの結果を確かめる

| 方法 | 内容 |
| --- | --- |
| 見えた本数を表示する | `CopyStructureCount` の値を、読み戻して（デバッグ時のみ）、画面に出す |
| カリングをカメラから切り離す | 別のカメラ（デバッグ カメラ）で、見ながら本来のカメラでカリングする。捨てすぎがすぐ分かる |
| 色で区別する | 区画ごとに、色を変えて描く。境目の不自然なところが見える |

## よくあるミス

??? failure "遠くの草が、急に消える"
    <strong>距離でフェード</strong>させる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 画面外・遠方・隠れた草を、描かない

## 参考

- Wihlidal, "Optimizing the Graphics Pipeline with Compute", Game Developers Conference 2016（フラスタム、背面、オクルージョンの GPU カリング）
- Haar, Aaltonen, "GPU-Driven Rendering Pipelines", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Wohllaib, "Procedural Grass in Ghost of Tsushima", Game Developers Conference 2021
- Hill, Collin, "Practical, Dynamic Visibility for Games", GPU Pro 2, 2011（Hi-Z によるオクルージョン カリング）

## 関連ページ

- [Vegetation](index.md)
- [Instancing](instancing.md)
