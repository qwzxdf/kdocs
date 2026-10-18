---
title: Hit Shading and BVH
tags:
  - 描画
---

# Hit Shading and BVH

**レイが当たった所の「色」を決めるには、その点でライティングを計算する必要があります**。**そのために、材質情報の取得と、BVH（加速構造）の準備**が**必要**です。このページでは、**ヒット点のシェーディングの方法と、BVH の準備**を説明します。

!!! tip "ポイント"
    - **ヒット点の材質（アルベド・法線・粗さ）を取り出して、ライティング**する。
    - **フル シェーディングは重いので、簡易ライティング（または、ラジアンス キャッシュ）で代用**することも多い。
    - **BVH ＝ レイの交差判定を速くする、木構造**。
    - **動く物体は、BVH を毎フレーム更新（再構築・リフィット）**する。

## ヒット点のシェーディング
**当たった点**の**色**を**その場で計算**します。**最も重い部分**です。

| 方法 | 内容 | コスト |
| --- | --- | --- |
| <strong>クローゼスト ヒット シェーダー（フル）</strong> | ヒット点の<strong>マテリアル（テクスチャ・法線）</strong>を評価し、<strong>ライティング（直接光・影・間接光）</strong>を計算 | **大**（反射の質は最高） |
| **簡易シェーディング** | **ベースカラーと簡易ライト**だけ。テクスチャの解像度を下げる（ミップを粗く） | 中 |
| **ライティング済みの結果を使う**（**ライト キャッシュ**・**G-Buffer のスクリーン空間が使える場合**） | **画面内のヒット**は、**スクリーン空間のライティング結果**を再利用 | 小 |
| **ミス → 空** | スカイ プローブ・スカイ ドーム | 最小 |

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

**マテリアルの評価**（テクスチャの読み込み）は、**画面の外**なので**ミップが決まらない**問題があります（レイは**微分**がない）。**ミップを距離・粗さから推定**します（**レイ コーン**）。

## BVH の準備
| 項目 | 内容 |
| --- | --- |
| **BLAS**（Bottom-Level AS） | **メッシュごと**の BVH。**静的**メッシュは、1 回作る |
| **TLAS**（Top-Level AS） | **インスタンスの配置**の BVH。**毎フレーム更新** |
| **動く・変形するメッシュ** | **スキニング後の頂点**で、BLAS を<strong>更新（リフィット）</strong>または**再構築** |
| **メモリ** | BVH は**メッシュの数倍**のメモリを食う |

レイトレーシング全般の話は、[描画セクションの入口](../../index.md)から関連ページをたどってください。

## よくあるミス

??? failure "BVH の更新が重く、フレーム時間が伸びる"
    **動かない物は静的 BVH**に、**動く物だけ更新**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **当たった点で、ライティングを計算**
    - [x] **BVH で、交差判定を速くする**

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [Ray-Traced Reflections](index.md)
- [Ray Generation](ray-generation.md)
- [Hybrid Pipeline](hybrid.md)
