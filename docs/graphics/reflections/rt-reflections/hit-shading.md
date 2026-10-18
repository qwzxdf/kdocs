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

## よくあるミス

??? failure "BVH の更新が重く、フレーム時間が伸びる"
    <strong>動かない物は静的 BVH</strong>に、<strong>動く物だけ更新</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 当たった点で、ライティングを計算
    - [x] BVH で、交差判定を速くする

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [Ray-Traced Reflections](index.md)
- [Ray Generation](ray-generation.md)
- [Hybrid Pipeline](hybrid.md)
