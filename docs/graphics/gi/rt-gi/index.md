---
title: Ray-Traced GI
tags:
  - 描画
---

# Ray-Traced GI

**レイトレ GI は、レイを飛ばして間接光を直接求める手法**で、**正確ですが、重く、ノイズが出ます**。**このセクションでは、素直な方式・ノイズ対策・ReSTIR・Lumen 的な方式・Radiance Cascades・選び方**を、**1 つずつ別のページ**で説明します。

## 素直なレイトレ GI
**画素のワールド位置と法線**から、**余弦重み付き**で**ランダムな方向**にレイを飛ばし、**ヒット点の放射輝度**を**集めます**。

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
| **余弦重み付き方向** | **`(n·ω)/pdf` が定数**になり、**平均**だけでよい |
| **ヒット点の直接光** | **ライトを評価**し、**シャドウ レイ**（またはシャドウ マップ）で**影** |
| **ヒット点の間接光** | **再帰しない**（**重い**）。**キャッシュ**（**プローブ・前フレームのスクリーン**・**世界空間のキャッシュ**）から**読む**＝**無料の多バウンス** |
| **ミス** | **空の光**（環境マップ） |

### なぜ「再帰しない」ことが鍵なのか

本物のパス トレーシングは、光が何回も跳ね返る経路を追うので、バウンスごとにレイが増え、リアルタイムでは到底追いつきません。そこで、<strong>1 バウンス目だけレイを飛ばし、2 バウンス目以降は「前のフレームまでに溜めた結果」を読む</strong>という近道を取ります。キャッシュには、前のフレームで計算した間接光が入っています。それを今のフレームのヒット点で読めば、2 バウンス目以降の光を「1 フレームの遅れ」と引き換えに、無料で得られます。フレームを重ねるたびに、キャッシュの中身が 1 バウンスずつ育つので、数フレームで多バウンスの GI に収束します。

**再帰を避ける**ことが**リアルタイム化の鍵**です。<strong>1 回のレイでヒット点の光を「キャッシュから読む」</strong>ことで**バウンスを重ねる**代わりに、**フレームを重ねて**蓄積します。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Fighting Noise](noise.md) | デノイズ・時間蓄積 |
| [ReSTIR GI](restir.md) | サンプルの再利用 |
| [Lumen-Style Approaches](lumen-style.md) | ソフトウェア トレース ＋ キャッシュ |
| [Radiance Cascades](radiance-cascades.md) | 距離ごとの解像度でまとめる |
| [Choosing a Method](choosing.md) | 動的 GI の選択と長所短所 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **レイトレ GI は、正確だが重くてノイズが多い**
    - [x] **再利用とデノイズで、実用にする**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [GI](../index.md)
- [DDGI](../ddgi.md)
- [Ray-Traced Reflections](../../reflections/rt-reflections/index.md)
