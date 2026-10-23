---
title: Ray Generation
tags:
  - 描画
---

# Ray Generation

<strong>レイトレ反射の最初の段階は、「どの方向へレイを飛ばすか」を決めること</strong>です。鏡のような面は完全な反射方向 1 本ですが、粗い面は GGX 分布に従って、方向をばらつかせます。このページでは反射レイの作り方・粗さの扱い・サンプル数を説明します。

!!! tip "ポイント"
    - 鏡面は反射ベクトルの 1 本だけ。
    - 粗い面は GGX の分布で、法線をサンプルして反射方向を作る。
    - 画素あたり 1 本（1 spp）が普通。足りない分はデノイズで補う。
    - 可視法線サンプリングを使うと、無駄なレイが減る。

!!! info "このページを読む前に"
    - [Ray-Traced Reflections](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## レイの生成
<strong>確率的 SSR と同じ</strong>です（[Stochastic SSR](../ssr-stochastic.md)）。画素ごと 1 本（または半分の解像度で 1 本）のレイを、GGX の可視法線サンプリングで作ります。

```hlsl
[shader("raygeneration")]
void ReflectionRayGen() {
  uint2 pixel = DispatchRaysIndex().xy;
  float3 p = WorldPosition(pixel);
  float3 n = WorldNormal(pixel);
  float3 v = normalize(camera_pos - p);
  float roughness = Roughness(pixel);
```

レイ生成シェーダーの入口です。画素の位置・法線・粗さを G バッファから読み、視線ベクトルを求めます。

```hlsl
  if (roughness > kMaxRoughness) { output[pixel] = 0; return; }
```

粗すぎる画素はレイを飛ばさず、反射プローブに任せます。

```hlsl
  float3 h = SampleGGXVNDFWorld(v, n, roughness, Random2(pixel, frame));
  float3 dir = reflect(-v, h);
  if (dot(dir, n) <= 0.0) { output[pixel] = 0; return; }
```

GGX の可視法線 `h` を乱数で、サンプルしてその `h` で視線を、反射します。反射方向が面の下を向いたら捨てます。

```hlsl
  RayDesc ray;
  ray.Origin = p + n * kRayBias;
  ray.Direction = dir;
  ray.TMin = 0.0;
  ray.TMax = kMaxRayLength;
```

レイを組み立てます。始点は面から少し浮かせて自己交差を、避けます。`TMax` で最大距離を制限します。

```hlsl
  ReflectionPayload payload = (ReflectionPayload)0;
  TraceRay(scene, RAY_FLAG_NONE, 0xFF, 0, 0, 0, ray, payload);
```

レイを飛ばします。ヒット シェーダーがペイロードに色と距離を、書き込みます。

```hlsl
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
粗さごとの対応です。粗さが低い（鏡面に近い）面は、ノイズが少なく効果が高いので、レイトレ（または SSR）を使います。中くらいの粗さは確率的なレイトレにデノイズを組み合わせます。粗さが高い面はレイを飛ばさず、プローブや拡散的な間接光に任せます。

粗さのしきい値は 0.4〜0.6 程度に決めるのが一般的です。粗い面の反射はもともと低周波でぼやけるので、レイトレの精度が見た目に効かず、ノイズとコストだけが増えるからです。

<strong>粗さのしきい値</strong>（0.4〜0.6 程度）で、レイの数を絞るのが一般的です。

### 可視法線サンプリング（VNDF）

GGX の粗い面で反射方向を選ぶとき昔は、法線の分布 D(h) に従ってハーフベクトル h を選んでいました。しかし、この方法では視線から見て背面を向いている法線も選ばれてしまい、その結果の反射方向が地平線の下に潜って、無効になります。粗いほど無駄なレイが増えます。

Heitz（2018）の可視法線サンプリング（VNDF）は、視線から見える法線だけを分布からサンプルします。背面を向いた法線はそもそも選ばれないので、無効なレイが大幅に減ります。実装は視線方向を法線の座標系の中で半球に変換して、円盤上の点から法線を作る手順で、数行で書けます。レイトレ反射と確率的 SSR の両方で、標準的な選択になっています。

## どの画素からどの方向へレイを、飛ばすか

<strong>RT 反射</strong>の最初の仕事は、反射する面の各画素から反射方向にレイを、生成することです。DXR ではレイ生成シェーダー（ray generation shader）がこれを、行います。

## 基本：鏡面の反射

<strong>粗さが 0</strong>（完全な鏡）なら、反射方向は 1 つに決まります。

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

始点を法線方向に少し離す（`+ normal * 1e-3`）のは、面自身に当たる（自己交差）のを、避けるためです。`TMax` でレイの最大距離を制限し遠くの物は、反射プローブに任せます。

## 粗い面：分布に従って方向を選ぶ

<strong>粗さが 0 より大きい</strong>と 反射は、1 方向でなく広がります（反射ローブ）。レイをランダムな方向に飛ばし、反射ローブの分布に従ってサンプルします（[Monte Carlo Integration](../../gi/theory/monte-carlo.md)）。

| 方法 | 内容 |
| --- | --- |
| GGX の法線分布からサンプル | 法線の、ずれ（ハーフ ベクトル `H`）を、GGX に従って選び `H` で反射。標準 |
| 可視法線のサンプリング（Heitz、2018） | 視線から見える、法線だけをサンプル。無駄なサンプル（面の裏）が減り、ノイズが少ない |

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

視線から見える法線だけを、サンプルするので反射方向が、面の下を向く（無効なサンプル）ことが、減ります。同じレイ数でノイズが少なくなります（Heitz、2018）。

```hlsl
// 粗さに応じた、反射レイ: 可視法線 H で、視線を、反射させる。
float3 V_local = WorldToLocal(-view_dir, normal);
float alpha = roughness * roughness;
float3 H_local = SampleGGXVNDF(V_local, alpha, alpha, u.x, u.y);
float3 H = LocalToWorld(H_local, normal);
float3 reflect_dir = reflect(view_dir, H);                                  // 法線を H にして、反射
if (dot(reflect_dir, normal) <= 0.0) { /* 面の下を向いた（まれ）: 無効にする */ }
```

ガウスの法線 `N` の代わりに、サンプルした `H` で視線を、反射させます。粗い面ほど反射方向が大きくばらつき周りの、広い範囲をサンプルします。

## レイを飛ばす画素を減らす

<strong>すべての画素</strong>からレイを飛ばすと、重いです。反射が見えない画素はスキップします。

| 条件 | 判断 |
| --- | --- |
| 粗さが高い（0.7 以上） | スキップ（反射プローブに、任せる） |
| 反射率が低い（非金属でフレネルが、小さい）、視線が垂直に近い | スキップ（反射が、見えない） |
| 画面外、空（深度が最大） | スキップ |
| SSR で取れた画素 | スキップ（ハイブリッド。[Hybrid Pipeline](hybrid.md)） |

```hlsl
// 反射が、ほぼ、見えない画素は、レイを、飛ばさない。
float reflectivity = lerp(0.04, 1.0, metallic) * (1.0 - roughness);          // 簡易な、反射の強さ
if (roughness > 0.7 || reflectivity < 0.02) { g_reflection_raw[pixel] = 0; return; }
```

## 解像度とレイ数

| 設定 | 内容 | 品質 | コスト |
| --- | --- | --- | --- |
| フル解像度、1 画素 1 レイ | 最高 | 高 | 大 |
| 半分の解像度、1 画素 1 レイ | 1/4 の、レイ数。アップサンプル | 中 | 中 |
| フル解像度、粗さに応じてレイ数を変える（つるつるは 1 本、粗いは多め） | バランス | 中〜高 | 中 |

<strong>レイの方向</strong>は ブルー ノイズで、選ぶ（ノイズの粒が均一でデノイズが、効きやすい）。

## よくあるミス

??? failure "粗い面の反射がノイズだらけ"
    <strong>粗さが高い面はレイトレを使わず、プローブにフォールバック</strong>する。

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
