---
title: Ray-Traced GI
tags:
  - 描画
---

# Ray-Traced GI

<strong>レイトレ GI は、レイを飛ばして間接光を直接求める手法</strong>で、<strong>正確ですが、重く、ノイズが出ます</strong>。このセクションでは、素直な方式・ノイズ対策・ReSTIR・Lumen 的な方式・Radiance Cascades・選び方を、1 つずつ別のページで説明します。

## 素直なレイトレ GI
<strong>画素のワールド位置と法線</strong>から、<strong>余弦重み付き</strong>でランダムな方向にレイを飛ばし、ヒット点の放射輝度を集めます。

```hlsl
float3 PathTraceGI(float3 pos, float3 normal, uint2 pixel) {
  float3 dir = CosineSampleHemisphere(normal, BlueNoise2D(pixel));
  Hit hit = TraceRay(pos + normal * kRayBias, dir);
  if (!hit.valid) return SampleSky(dir);
  float3 direct = EvaluateDirectLight(hit);
  float3 indirect = ReadIrradianceCache(hit.position, hit.normal);
  return hit.albedo * (direct + indirect);
}
```

| 点 | 説明 |
| --- | --- |
| 余弦重み付き方向 | `(n·ω)/pdf` が定数になり、平均だけでよい |
| ヒット点の直接光 | ライトを評価し、シャドウ レイ（またはシャドウ マップ）で影 |
| ヒット点の間接光 | 再帰しない（重い）。キャッシュ（プローブ・前フレームのスクリーン・世界空間のキャッシュ）から読む＝無料の多バウンス |
| ミス | 空の光（環境マップ） |

### なぜ「再帰しない」ことが鍵なのか

本物のパス トレーシングは、光が何回も跳ね返る経路を追うので、バウンスごとにレイが増え、リアルタイムでは到底追いつきません。そこで、<strong>1 バウンス目だけレイを飛ばし、2 バウンス目以降は「前のフレームまでに溜めた結果」を読む</strong>という近道を取ります。キャッシュには、前のフレームで計算した間接光が入っています。それを今のフレームのヒット点で読めば、2 バウンス目以降の光を「1 フレームの遅れ」と引き換えに、無料で得られます。フレームを重ねるたびに、キャッシュの中身が 1 バウンスずつ育つので、数フレームで多バウンスの GI に収束します。

<strong>再帰を避ける</strong>ことが<strong>リアルタイム化の鍵</strong>です。<strong>1 回のレイでヒット点の光を「キャッシュから読む」</strong>ことでバウンスを重ねる代わりに、フレームを重ねて蓄積します。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Fighting Noise](noise.md) | デノイズ・時間蓄積 |
| [ReSTIR GI](restir.md) | サンプルの再利用 |
| [Lumen-Style Approaches](lumen-style.md) | ソフトウェア トレース ＋ キャッシュ |
| [Radiance Cascades](radiance-cascades.md) | 距離ごとの解像度でまとめる |
| [Choosing a Method](choosing.md) | 動的 GI の選択と長所短所 |

## レイトレーシングで、間接光を求める

<strong>ハードウェア レイトレーシング</strong>（DXR、[DirectX Raytracing](https://learn.microsoft.com/windows/win32/direct3d12/direct3d-12-raytracing)）が、<strong>GPU で、使える</strong>ようになり、間接光を、実際に、レイを、飛ばして、求めることが、リアルタイムで、可能になりました。シーンの、形状を、近似せず（ボクセル、距離場、画面空間）、本物の、三角形に対して、レイを、飛ばせます。

## 基本の、考え方

<strong>各画素</strong>から、<strong>半球の、ランダムな、方向</strong>に、レイを、飛ばし（モンテカルロ、[Monte Carlo Integration](../theory/monte-carlo.md)）、当たった面の、ライティングを、集めます。1 回の反射（1 バウンス）で、間接光を、直接、サンプルします。

```hlsl
// DXR: 各画素の、拡散の、間接光を、1 本のレイで、推定する（レイ生成シェーダー）。
[shader("raygeneration")]
void GIRayGen() {
  uint2 pixel = DispatchRaysIndex().xy;
  float3 position = g_gbuffer_position[pixel];
  float3 normal = g_gbuffer_normal[pixel];
  float3 albedo = g_gbuffer_albedo[pixel];

  float2 u = Random2(pixel, g_frame_index);
  float3 dir = LocalToWorld(CosineHemisphere(u.x, u.y), normal);         // 余弦重みづけ（拡散）

  RayDesc ray = { position + normal * 1e-3, 0.0, dir, 1e27 };
  Payload payload = { float3(0, 0, 0) };
  TraceRay(g_scene, RAY_FLAG_NONE, 0xFF, 0, 1, 0, ray, payload);         // 本物の三角形に対して、レイを飛ばす

  g_gi_raw[pixel] = float4(albedo * payload.radiance, 1.0);              // 余弦重みづけなので、albedo × 光（約分されている）
}
```

<strong>ヒット シェーダー</strong>（当たった面）で、<strong>その面の、直接光</strong>（太陽、ライト + 影レイ）と、前のフレームの、間接光（多重反射）を、計算して、返します。

## 問題：ノイズ

<strong>1 画素あたり、1 本</strong>の、レイでは、<strong>ノイズだらけ</strong>です（[Monte Carlo Integration](../theory/monte-carlo.md)：誤差は、`1/√N`）。リアルタイムでは、レイを、増やせないので、デノイズ（[Fighting Noise](noise.md)）、再利用（[ReSTIR GI](restir.md)）、キャッシュ（プローブ。[DDGI](../ddgi.md)）で、補います。

## 代表的な、アプローチ

| アプローチ | 内容 | ページ |
| --- | --- | --- |
| 画素ごとに、レイ + デノイズ | 1 画素に、1 本のレイ + 時空間フィルタ | [Fighting Noise](noise.md) |
| ReSTIR GI | 隣の画素・前フレームの、レイの結果を、再利用 | [ReSTIR GI](restir.md) |
| キャッシュ（プローブ）に、レイ | プローブから、レイを、飛ばし、結果を、蓄積（[DDGI](../ddgi.md)） | [DDGI](../ddgi.md) |
| Lumen 型（ハイブリッド） | 画面空間 + 距離場 + サーフェス キャッシュを、組み合わせる | [Lumen-Style Approaches](lumen-style.md) |
| Radiance Cascades | カスケード状に、レイを、まとめて、再利用 | [Radiance Cascades](radiance-cascades.md) |

## 選び方

| 状況 | おすすめ |
| --- | --- |
| ハードウェア RT が、使える、高品質 | ReSTIR GI + デノイズ、DDGI |
| ハードウェア RT が、無い | Lumen 型（ソフトウェア距離場）、ボクセル GI、SSGI + プローブ |
| 2D ゲーム、画面空間 | Radiance Cascades |
| 広い、オープン ワールド | Lumen 型、DDGI（カスケードの、プローブ） |

詳しい、判断は、[Choosing a Method](choosing.md) を、見てください。

## DirectX 11 では動かない部分

<strong>DXR（DirectX Raytracing）は、DirectX 12 の機能です。DirectX 11 には、ありません。</strong>このページの `TraceRay`・`RayQuery` を使うコードは、D3D12 のレンダラーで動かします。D3D11 だけで、同じ効果を狙うときは、次のように、置き換えます。

| やりたいこと | D3D11 での代用 |
| --- | --- |
| レイと三角形の、交差 | 距離場（SDF）・ボクセル、またはスクリーン空間のレイマーチ（[Linear Marching](../../reflections/ssr-basics/linear-march.md)） |
| 影 | シャドウ マップ（[Shadow Map Basics](../../shadows/shadow-map-basics/index.md)） |
| 間接光 | ライトマップ・プローブ・SSGI・ボクセル GI（[Global Illumination (GI)](../../gi/index.md)） |

D3D12 側の、初期化（加速構造・ステート オブジェクト・シェーダー テーブル・`DispatchRays`）は、[DXR Host Setup](../../../directx/dx12/dxr-host.md) に、まとめています。

## これだけ覚える

!!! abstract "まとめ"
    - [x] レイトレ GI は、正確だが重くてノイズが多い
    - [x] 再利用とデノイズで、実用にする

## 参考

- Microsoft, "DirectX Raytracing (DXR) Functional Spec"
- Schied, Kaplanyan, Wyman, Patney, Chaitanya, Burgess, Liu, Dachsbacher, Lefohn, Salvi, "Spatiotemporal Variance-Guided Filtering: Real-Time Reconstruction for Path-Traced Global Illumination", High-Performance Graphics 2017（SVGF）
- Bitterli, Wyman, Pharr, Shirley, Lefohn, Jarosz, "Spatiotemporal Reservoir Resampling for Real-Time Ray Tracing with Dynamic Direct Lighting", ACM Transactions on Graphics (SIGGRAPH 2020)（ReSTIR）
- Ouyang, Liu, Kettunen, Pharr, Pantaleoni, "ReSTIR GI: Path Resampling for Real-Time Path Tracing", Computer Graphics Forum (High-Performance Graphics 2021)
- Wright, Narkowicz, Kelly, "Lumen: Real-time Global Illumination in Unreal Engine 5", SIGGRAPH 2022, Advances in Real-Time Rendering in Games
- Majercik, Guertin, Nowrouzezahrai, McGuire, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields", Journal of Computer Graphics Techniques, Vol. 8, No. 2, 2019（DDGI）

## 関連ページ

- [GI](../index.md)
- [DDGI](../ddgi.md)
- [Ray-Traced Reflections](../../reflections/rt-reflections/index.md)
