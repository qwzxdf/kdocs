---
title: Ray Generation
tags:
  - 描画
---

# Ray Generation

**レイトレ反射の最初の段階は、「どの方向へ、レイを飛ばすか」を決めること**です。**鏡のような面は、完全な反射方向 1 本**ですが、**粗い面は、GGX 分布に従って、方向をばらつかせます**。このページでは、**反射レイの作り方・粗さの扱い・サンプル数**を説明します。

!!! tip "ポイント"
    - **鏡面は、反射ベクトルの 1 本だけ**。
    - **粗い面は、GGX の分布で、法線をサンプルして、反射方向を作る**。
    - **画素あたり 1 本（1 spp）**が**普通**。**足りない分は、デノイズで補う**。
    - **可視法線サンプリング**を使うと、**無駄なレイが減る**。

## レイの生成
**確率的 SSR と同じ**です（[Stochastic SSR](../ssr-stochastic.md)）。**画素ごと 1 本**（または**半分の解像度**で 1 本）のレイを、**GGX の可視法線サンプリング**で作ります。

```hlsl
[shader("raygeneration")]
void ReflectionRayGen() {
  uint2 pixel = DispatchRaysIndex().xy;
  float3 p = WorldPosition(pixel);
  float3 n = WorldNormal(pixel);
  float3 v = normalize(camera_pos - p);
  float roughness = Roughness(pixel);

  if (roughness > kMaxRoughness) { output[pixel] = 0; return; }

  float3 h = SampleGGXVNDFWorld(v, n, roughness, Random2(pixel, frame));
  float3 dir = reflect(-v, h);
  if (dot(dir, n) <= 0.0) { output[pixel] = 0; return; }

  RayDesc ray;
  ray.Origin = p + n * kRayBias;
  ray.Direction = dir;
  ray.TMin = 0.0;
  ray.TMax = kMaxRayLength;

  ReflectionPayload payload = (ReflectionPayload)0;
  TraceRay(scene, RAY_FLAG_NONE, 0xFF, 0, 0, 0, ray, payload);

  output[pixel] = float4(payload.color, payload.hit_distance);
}
```

| 点 | 説明 |
| --- | --- |
| **粗さのしきい値** | **粗い面はレイを飛ばさず**、プローブに任せる（コスト削減） |
| **`dot(dir, n) <= 0`** | 地平線の下のレイは、無効 |
| **ペイロード** | **色**と**ヒット距離**（デノイズに使う） |
| **`ray.Origin = p + n·bias`** | 自己交差を避ける |

## 粗さの扱い
| 粗さ | 対応 |
| --- | --- |
| <strong>低い（鏡面）</strong> | <strong>レイトレ（または SSR）</strong>。ノイズが少なく、効果が高い |
| **中くらい** | レイトレ（確率的）＋デノイズ |
| <strong>高い（粗い）</strong> | **レイを飛ばさない**。**プローブ**・**拡散的な間接光**に任せる |

**粗さのしきい値**（0.4〜0.6 程度）で、**レイの数を絞る**のが一般的です。

## よくあるミス

??? failure "粗い面の反射がノイズだらけ"
    **粗さが高い面は、レイトレを使わず、プローブにフォールバック**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **鏡面は 1 本、粗い面は分布からサンプル**
    - [x] **1 spp ＋ デノイズ**が基本

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [Ray-Traced Reflections](index.md)
- [ヒット点のシェーディング](hit-shading.md)
- [Stochastic SSR](../ssr-stochastic.md)
