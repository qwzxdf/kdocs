---
title: Ray Generation
tags:
  - 描画
---

# Ray Generation

<strong>レイトレ反射の最初の段階は、「どの方向へ、レイを飛ばすか」を決めること</strong>です。<strong>鏡のような面は、完全な反射方向 1 本</strong>ですが、粗い面は、GGX 分布に従って、方向をばらつかせます。このページでは、反射レイの作り方・粗さの扱い・サンプル数を説明します。

!!! tip "ポイント"
    - 鏡面は、反射ベクトルの 1 本だけ。
    - 粗い面は、GGX の分布で、法線をサンプルして、反射方向を作る。
    - 画素あたり 1 本（1 spp）が普通。足りない分は、デノイズで補う。
    - 可視法線サンプリングを使うと、無駄なレイが減る。

## レイの生成
<strong>確率的 SSR と同じ</strong>です（[Stochastic SSR](../ssr-stochastic.md)）。<strong>画素ごと 1 本</strong>（または半分の解像度で 1 本）のレイを、GGX の可視法線サンプリングで作ります。

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
| 粗さのしきい値 | 粗い面はレイを飛ばさず、プローブに任せる（コスト削減） |
| `dot(dir, n) <= 0` | 地平線の下のレイは、無効 |
| ペイロード | 色とヒット距離（デノイズに使う） |
| `ray.Origin = p + n·bias` | 自己交差を避ける |

## 粗さの扱い
粗さごとの対応です。粗さが低い（鏡面に近い）面は、ノイズが少なく効果が高いので、レイトレ（または SSR）を使います。中くらいの粗さは、確率的なレイトレにデノイズを組み合わせます。粗さが高い面は、レイを飛ばさず、プローブや拡散的な間接光に任せます。

粗さのしきい値は 0.4〜0.6 程度に決めるのが一般的です。粗い面の反射は、もともと低周波でぼやけるので、レイトレの精度が見た目に効かず、ノイズとコストだけが増えるからです。

<strong>粗さのしきい値</strong>（0.4〜0.6 程度）で、<strong>レイの数を絞る</strong>のが一般的です。

### 可視法線サンプリング（VNDF）

GGX の粗い面で反射方向を選ぶとき、昔は、法線の分布 D(h) に従ってハーフベクトル h を選んでいました。しかし、この方法では、視線から見て<strong>背面を向いている法線</strong>も選ばれてしまい、その結果の反射方向が地平線の下に潜って、無効になります。粗いほど、無駄なレイが増えます。

Heitz（2018）の<strong>可視法線サンプリング</strong>（VNDF）は、視線から見える法線だけを分布からサンプルします。背面を向いた法線は、そもそも選ばれないので、無効なレイが大幅に減ります。実装は、視線方向を法線の座標系の中で半球に変換して、円盤上の点から法線を作る手順で、数行で書けます。レイトレ反射と確率的 SSR の両方で、標準的な選択になっています。

## どの画素から、どの方向へ、レイを、飛ばすか

<strong>RT 反射</strong>の、最初の、仕事は、<strong>反射する面の、各画素</strong>から、反射方向に、レイを、生成することです。DXR では、レイ生成シェーダー（ray generation shader）が、これを、行います。

## 基本：鏡面の、反射

<strong>粗さが、0</strong>（完全な、鏡）なら、<strong>反射方向</strong>は、1 つに、決まります。

```hlsl
// DXR のレイ生成シェーダー（鏡面）。G バッファから、位置と法線を読み、反射レイを飛ばす。
[shader("raygeneration")]
void ReflectionRayGen() {
  uint2 pixel = DispatchRaysIndex().xy;
  float3 position = g_gbuffer_position[pixel];
  float3 normal = g_gbuffer_normal[pixel];
  float3 view_dir = normalize(position - g_camera_position);          // カメラから、画素へ向かう向き
  float3 reflect_dir = reflect(view_dir, normal);                     // 反射方向

  RayDesc ray;
  ray.Origin = position + normal * 1e-3;                              // 面に、めり込まないように、少し離す
  ray.TMin = 0.0;
  ray.Direction = reflect_dir;
  ray.TMax = g_max_reflection_distance;                               // 遠くは、プローブに、任せる
  ReflectionPayload payload = (ReflectionPayload)0;
  TraceRay(g_scene, RAY_FLAG_NONE, 0xFF, 0, 1, 0, ray, payload);      // 反射レイを、飛ばす
  g_reflection_raw[pixel] = float4(payload.radiance, payload.hit_distance);
}
```

<strong>始点を、法線方向に、少し離す</strong>（`+ normal * 1e-3`）のは、<strong>面自身に、当たる</strong>（自己交差）のを、避けるためです。`TMax` で、レイの、最大距離を、制限し、遠くの、物は、反射プローブに、任せます。

## 粗い面：分布に従って、方向を、選ぶ

<strong>粗さが、0 より、大きい</strong>と、<strong>反射は、1 方向でなく、広がり</strong>ます（反射ローブ）。レイを、ランダムな、方向に、飛ばし、反射ローブの、分布に従って、サンプルします（[Monte Carlo Integration](../../gi/theory/monte-carlo.md)）。

| 方法 | 内容 |
| --- | --- |
| GGX の、法線分布から、サンプル | 法線の、ずれ（ハーフ ベクトル `H`）を、GGX に従って選び、`H` で、反射。標準 |
| 可視法線の、サンプリング（Heitz、2018） | 視線から、見える、法線だけを、サンプル。無駄な、サンプル（面の裏）が、減り、ノイズが、少ない |

```hlsl
// GGX の、可視法線を、サンプルする（Heitz 2018）。Ve: ローカル座標（法線が +Z）での、視線。
float3 SampleGGXVNDF(float3 Ve, float alpha_x, float alpha_y, float u1, float u2) {
  float3 Vh = normalize(float3(alpha_x * Ve.x, alpha_y * Ve.y, Ve.z));      // 視線を、異方性の、スケールで、半球の形に、変換
  float lensq = Vh.x * Vh.x + Vh.y * Vh.y;
  float3 T1 = lensq > 0.0 ? float3(-Vh.y, Vh.x, 0.0) * rsqrt(lensq) : float3(1, 0, 0);
  float3 T2 = cross(Vh, T1);
  float r = sqrt(u1);
  float phi = 2.0 * 3.14159265 * u2;
  float t1 = r * cos(phi);
  float t2 = r * sin(phi);
  float s = 0.5 * (1.0 + Vh.z);
  t2 = (1.0 - s) * sqrt(1.0 - t1 * t1) + s * t2;                            // 視線の側に、偏らせる
  float3 Nh = t1 * T1 + t2 * T2 + sqrt(max(0.0, 1.0 - t1 * t1 - t2 * t2)) * Vh;
  return normalize(float3(alpha_x * Nh.x, alpha_y * Nh.y, max(0.0, Nh.z)));   // 元の空間に、戻す
}
```

<strong>視線から、見える</strong>法線だけを、<strong>サンプル</strong>するので、反射方向が、面の下を、向く（無効な、サンプル）ことが、減ります。同じ、レイ数で、ノイズが、少なくなります（Heitz、2018）。

```hlsl
// 粗さに応じた、反射レイ: 可視法線 H で、視線を、反射させる。
float3 V_local = WorldToLocal(-view_dir, normal);
float alpha = roughness * roughness;
float3 H_local = SampleGGXVNDF(V_local, alpha, alpha, u.x, u.y);
float3 H = LocalToWorld(H_local, normal);
float3 reflect_dir = reflect(view_dir, H);                                  // 法線を H にして、反射
if (dot(reflect_dir, normal) <= 0.0) { /* 面の下を向いた（まれ）: 無効にする */ }
```

<strong>ガウスの、法線 `N`</strong> の代わりに、<strong>サンプルした、`H`</strong> で、視線を、反射させます。粗い面ほど、反射方向が、大きく、ばらつき、周りの、広い範囲を、サンプルします。

## レイを、飛ばす、画素を、減らす

<strong>すべての画素</strong>から、レイを、飛ばすと、<strong>重い</strong>です。反射が、見えない画素は、スキップします。

| 条件 | 判断 |
| --- | --- |
| 粗さが、高い（0.7 以上） | スキップ（反射プローブに、任せる） |
| 反射率が、低い（非金属で、フレネルが、小さい）、視線が、垂直に近い | スキップ（反射が、見えない） |
| 画面外、空（深度が、最大） | スキップ |
| SSR で、取れた画素 | スキップ（ハイブリッド。[Hybrid Pipeline](hybrid.md)） |

```hlsl
// 反射が、ほぼ、見えない画素は、レイを、飛ばさない。
float reflectivity = lerp(0.04, 1.0, metallic) * (1.0 - roughness);          // 簡易な、反射の強さ
if (roughness > 0.7 || reflectivity < 0.02) { g_reflection_raw[pixel] = 0; return; }
```

## 解像度と、レイ数

| 設定 | 内容 | 品質 | コスト |
| --- | --- | --- | --- |
| フル解像度、1 画素 1 レイ | 最高 | 高 | 大 |
| 半分の、解像度、1 画素 1 レイ | 1/4 の、レイ数。アップサンプル | 中 | 中 |
| フル解像度、粗さに応じて、レイ数を、変える（つるつるは、1 本、粗いは、多め） | バランス | 中〜高 | 中 |

<strong>レイの、方向</strong>は、<strong>ブルー ノイズ</strong>で、選ぶ（ノイズの、粒が、均一で、デノイズが、効きやすい）。

## よくあるミス

??? failure "粗い面の反射がノイズだらけ"
    <strong>粗さが高い面は、レイトレを使わず、プローブにフォールバック</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 鏡面は 1 本、粗い面は分布からサンプル
    - [x] 1 spp ＋ デノイズが基本

## 参考

- Heitz, "Sampling the GGX Distribution of Visible Normals", Journal of Computer Graphics Techniques, Vol. 7, No. 4, 2018
- Walter, Marschner, Li, Torrance, "Microfacet Models for Refraction through Rough Surfaces", Eurographics Symposium on Rendering 2007
- Microsoft, "DirectX Raytracing (DXR) Functional Spec"
- Barré-Brisebois, Halén, Wihlidal, Lauritzen, Bekkers, Stachowiak, Andersson, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 25, 2019
- Stachowiak, "Stochastic All The Things: Raytracing in Hybrid Real-Time Rendering", Digital Dragons 2018

## 関連ページ

- [Ray-Traced Reflections](index.md)
- [Hit Shading and BVH](hit-shading.md)
- [Stochastic SSR](../ssr-stochastic.md)
