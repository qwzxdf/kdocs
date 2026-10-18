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

## Generating Rays {#レイの生成}
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

## Handling Roughness {#粗さの扱い}
粗さごとの対応です。粗さが低い（鏡面に近い）面は、ノイズが少なく効果が高いので、レイトレ（または SSR）を使います。中くらいの粗さは、確率的なレイトレにデノイズを組み合わせます。粗さが高い面は、レイを飛ばさず、プローブや拡散的な間接光に任せます。

粗さのしきい値は 0.4〜0.6 程度に決めるのが一般的です。粗い面の反射は、もともと低周波でぼやけるので、レイトレの精度が見た目に効かず、ノイズとコストだけが増えるからです。

**粗さのしきい値**（0.4〜0.6 程度）で、**レイの数を絞る**のが一般的です。

### Visible Normal Sampling (VNDF) {#可視法線サンプリングvndf}

GGX の粗い面で反射方向を選ぶとき、昔は、法線の分布 D(h) に従ってハーフベクトル h を選んでいました。しかし、この方法では、視線から見て<strong>背面を向いている法線</strong>も選ばれてしまい、その結果の反射方向が地平線の下に潜って、無効になります。粗いほど、無駄なレイが増えます。

Heitz（2018）の<strong>可視法線サンプリング</strong>（VNDF）は、視線から見える法線だけを分布からサンプルします。背面を向いた法線は、そもそも選ばれないので、無効なレイが大幅に減ります。実装は、視線方向を法線の座標系の中で半球に変換して、円盤上の点から法線を作る手順で、数行で書けます。レイトレ反射と確率的 SSR の両方で、標準的な選択になっています。

## Common Mistakes {#よくあるミス}

??? failure "粗い面の反射がノイズだらけ"
    **粗さが高い面は、レイトレを使わず、プローブにフォールバック**する。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **鏡面は 1 本、粗い面は分布からサンプル**
    - [x] **1 spp ＋ デノイズ**が基本

## References {#参考}

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## Related Pages {#関連ページ}

- [Ray-Traced Reflections](index.md)
- [ヒット点のシェーディング](hit-shading.md)
- [Stochastic SSR](../ssr-stochastic.md)
