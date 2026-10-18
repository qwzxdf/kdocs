---
title: Hit Shading and BVH
tags:
  - 描画
---

# Hit Shading and BVH

<strong>レイが当たった所の「色」を決めるには、その点でライティングを計算する必要があります</strong>。<strong>そのために、材質情報の取得と、BVH（加速構造）の準備</strong>が必要です。このページでは、ヒット点のシェーディングの方法と、BVH の準備を説明します。

!!! tip "ポイント"
    - ヒット点の材質（アルベド・法線・粗さ）を取り出して、ライティングする。
    - フル シェーディングは重いので、簡易ライティング（または、ラジアンス キャッシュ）で代用することも多い。
    - BVH ＝ レイの交差判定を速くする、木構造。
    - 動く物体は、BVH を毎フレーム更新（再構築・リフィット）する。

## ヒット点のシェーディング
<strong>当たった点</strong>の<strong>色</strong>をその場で計算します。最も重い部分です。

| 方法 | 内容 | コスト |
| --- | --- | --- |
| <strong>クローゼスト ヒット シェーダー（フル）</strong> | ヒット点の<strong>マテリアル（テクスチャ・法線）</strong>を評価し、<strong>ライティング（直接光・影・間接光）</strong>を計算 | 大（反射の質は最高） |
| 簡易シェーディング | ベースカラーと簡易ライトだけ。テクスチャの解像度を下げる（ミップを粗く） | 中 |
| ライティング済みの結果を使う（ライト キャッシュ・G-Buffer のスクリーン空間が使える場合） | 画面内のヒットは、スクリーン空間のライティング結果を再利用 | 小 |
| ミス → 空 | スカイ プローブ・スカイ ドーム | 最小 |

### ヒット点でのライティング

ヒット点でのライティングは、直接光、間接光、反射の反射に分けて考えます。直接光は、ライトごとに影のレイ（または影マップ）を使います。間接光は、ライト プローブや環境マップで近似し、さらにレイを飛ばしません（コストが大きすぎるため）。反射の反射は、再帰を 1 回までにして、2 回目はプローブを引きます。

```hlsl
[shader("closesthit")]
void ReflectionClosestHit(inout ReflectionPayload payload, BuiltInTriangleIntersectionAttributes attr) {
  SurfaceData surf = EvaluateMaterial(PrimitiveIndex(), attr.barycentrics);
  float3 hit_pos = WorldRayOrigin() + WorldRayDirection() * RayTCurrent();

  float3 color = EvaluateDirectLighting(surf, hit_pos, -WorldRayDirection());
  color += surf.albedo * SampleIrradiance(hit_pos, surf.normal);

  payload.color = color;
  payload.hit_distance = RayTCurrent();
}
```

<strong>マテリアルの評価</strong>（テクスチャの読み込み）は、<strong>画面の外</strong>なのでミップが決まらない問題があります（レイは微分がない）。ミップを距離・粗さから推定します（レイ コーン）。

## BVH の準備
| 項目 | 内容 |
| --- | --- |
| BLAS（Bottom-Level AS） | メッシュごとの BVH。静的メッシュは、1 回作る |
| TLAS（Top-Level AS） | インスタンスの配置の BVH。毎フレーム更新 |
| 動く・変形するメッシュ | スキニング後の頂点で、BLAS を<strong>更新（リフィット）</strong>または再構築 |
| メモリ | BVH はメッシュの数倍のメモリを食う |

レイトレーシング全般の話は、[描画セクションの入口](../../index.md)から関連ページをたどってください。

## レイが、当たった面の、色を、求める

<strong>反射レイ</strong>が、<strong>三角形に、当たる</strong>と、その面の、色（反射として、返す光）を、求める必要があります。DXR では、ヒット シェーダー（closest hit shader）が、これを、行います。

## 加速構造（BVH）

<strong>レイが、どの三角形に、当たるか</strong>を、<strong>高速に、探す</strong>ために、シーンの、三角形を、加速構造（BVH：Bounding Volume Hierarchy、境界ボリューム階層）に、まとめます。

| 階層 | 内容 |
| --- | --- |
| BLAS（Bottom-Level Acceleration Structure） | 1 つのメッシュの、三角形を、BVH に、まとめたもの |
| TLAS（Top-Level Acceleration Structure） | BLAS の、インスタンス（位置・向き・大きさを、持った、メッシュの、配置）を、まとめたもの |

```text
TLAS（シーン全体）
 ├ インスタンス 1: 岩（BLAS A）  位置 (10, 0, 5)
 ├ インスタンス 2: 岩（BLAS A）  位置 (30, 0, 8)     ← 同じ BLAS を、複数回、使い回す
 ├ インスタンス 3: 木（BLAS B）  位置 (15, 0, 2)
 └ インスタンス 4: キャラクター（BLAS C）  位置 (…)  ← 動く物は、TLAS だけを、更新（BLAS は、アニメーションするなら、再構築）
```

| 更新 | コスト |
| --- | --- |
| 静的メッシュ | BLAS は、1 回だけ作る |
| 動く物（剛体） | TLAS の、変換行列だけを、毎フレーム更新（軽い） |
| スキニング、変形する物 | BLAS を、更新（refit）、または、再構築（重い） |
| TLAS | 毎フレーム再構築（インスタンスの数に、比例） |

## ヒット シェーダーの、流れ

<strong>ヒット シェーダー</strong>で、<strong>当たった面の、色</strong>を、計算します。

```hlsl
// 最も近い交点で、呼ばれる。当たった面の、属性（UV、法線、マテリアル）から、色を求める。
[shader("closesthit")]
void ReflectionClosestHit(inout ReflectionPayload payload, in BuiltInTriangleIntersectionAttributes attr) {
  // ① 当たった三角形の、頂点属性を、補間して、UV と法線を得る（重心座標 attr.barycentrics）。
  Vertex v = InterpolateVertex(InstanceID(), PrimitiveIndex(), attr.barycentrics);
  float3 hit_position = WorldRayOrigin() + WorldRayDirection() * RayTCurrent();
  float3 normal = normalize(mul(v.normal, (float3x3)ObjectToWorld3x4()));
```

<strong>ヒット シェーダー</strong>では、<strong>画面の G バッファが、無い</strong>（画面外の、面かもしれない）ので、頂点バッファと、インデックス バッファから、当たった三角形の、属性を、自分で、補間します（重心座標）。

```hlsl
  // ② マテリアルを、読む（アルベド、粗さなど）。テクスチャは、ミップを、手で選ぶ（レイは、画面の微分を、持たない）。
  Material m = g_materials[v.material_id];
  float mip = ComputeRayConeMip(payload.cone_width + RayTCurrent() * payload.cone_spread, v);   // レイ コーンから、ミップを決める
  float3 albedo = g_textures[m.albedo_index].SampleLevel(g_linear_wrap, v.uv, mip).rgb;
```

<strong>ヒット シェーダーでは、画面の微分</strong>（`ddx`、`ddy`）が、<strong>使えません</strong>。ミップを、自分で、決める必要が、あり、レイ コーン（レイが、進むほど、広がる、円錐の、幅）から、ミップを、求めます（近似）。

```hlsl
  // ③ ライティング: 直接光（太陽 + 影レイ）+ 間接光（簡易）。
  float3 radiance = 0.0;
  float3 L = -g_sun_dir;
  float n_dot_l = saturate(dot(normal, L));
  if (n_dot_l > 0.0 && !InShadow(hit_position + normal * 1e-3, L)) {                // 影レイ（別のレイ）
    radiance += albedo / 3.14159265 * g_sun_color * n_dot_l;
  }
  radiance += albedo * SampleAmbient(normal);                                       // 簡易な間接光（SH、プローブ）
  payload.radiance = radiance;
  payload.hit_distance = RayTCurrent();
}
```

<strong>直接光</strong>は、<strong>影レイ</strong>（光の方向に、短いレイを、飛ばして、遮られるか）で、影を、判定します。間接光は、簡易（SH、ライト プローブ）にします（反射の、反射に、フル GIを、使うと、重すぎる）。

## コストを、減らす、工夫

<strong>ヒット シェーダーが、重い</strong>と、<strong>RT 反射全体が、重く</strong>なります。当たる、面の、シェーディングは、簡略化します。

| 工夫 | 内容 |
| --- | --- |
| 影を、省く（または、遠くだけ） | 影レイを、飛ばさない（反射の中の、影は、見えにくい）。シャドウ マップで、代用 |
| 間接光を、簡易に | SH プローブ、環境光。フル GI は、使わない |
| ライティングを、キャッシュから | 当たった面の、ライティングを、サーフェス キャッシュから、読む（[Lumen-Style Approaches](../../gi/rt-gi/lumen-style.md)） |
| LOD | 反射の中の、物は、低 LOD のメッシュで、BVH を、作る（三角形が、少ない） |
| テクスチャの、ミップを、粗く | ミップ バイアスで、粗いテクスチャを、読む（反射は、細かい模様が、見えにくい） |
| 透過・アルファ テスト | アルファ テストの、メッシュは、any hit シェーダーが、必要（重い）。反射では、アルファ テストを、省く、または、不透明として、扱う |

## 反射の、反射（再帰）

<strong>反射レイが、当たった面</strong>が、<strong>さらに、反射する</strong>（つるつる）なら、2 回目の、反射レイを、飛ばせます（再帰）。反射の中の、反射です。

| 再帰の、深さ | 内容 |
| --- | --- |
| 1（反射なし） | 当たった面は、拡散として、ライティング。最安 |
| 2 | 1 回の、反射の、反射（鏡の部屋、向かい合う、窓）。重い |
| 3 以上 | 非常に、重い。ほぼ、不要（2 回目以降は、暗く、見えにくい） |

<strong>実用</strong>では、<strong>再帰は、1〜2 回</strong>に、制限し、それ以降は、プローブや、空の色で、打ち切ります。

## よくあるミス

??? failure "BVH の更新が重く、フレーム時間が伸びる"
    <strong>動かない物は静的 BVH</strong>に、<strong>動く物だけ更新</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 当たった点で、ライティングを計算
    - [x] BVH で、交差判定を速くする

## 参考

- Microsoft, "DirectX Raytracing (DXR) Functional Spec"
- Barré-Brisebois, Halén, Wihlidal, Lauritzen, Bekkers, Stachowiak, Andersson, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 25, 2019
- Stachowiak, "Stochastic All The Things: Raytracing in Hybrid Real-Time Rendering", Digital Dragons 2018
- Akenine-Möller, Nilsson, Andersson, Barré-Brisebois, Toth, Karis, "Texture Level of Detail Strategies for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 20, 2019（レイ コーンによる、ミップの選択）

## 関連ページ

- [Ray-Traced Reflections](index.md)
- [Ray Generation](ray-generation.md)
- [Hybrid Pipeline](hybrid.md)
