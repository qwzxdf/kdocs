---
title: Lightmaps
tags:
  - 描画
---

# Lightmaps

<strong>ライトマップは静的なシーンの間接光（と影）を事前に計算（ベイク）してテクスチャに保存する手法</strong>です。実行時はテクスチャを読むだけなので、軽く品質も高いです。ただし、光や物が動くと使えません。このセクションでは原理・ライトマップ UV・ベイクの流れ・方向情報・鏡面・動く物体・動的ライトとの関係を 1 つずつ別のページで説明します。

## 原理
<strong>オフライン</strong>でパス トレーシングなどの、重いが正確な計算を行い 各表面点に届く光（放射照度）を求めます。それをメッシュ専用の UV 座標に沿って、テクスチャ（ライトマップ）に書き込みます。

実行時、ピクセル シェーダーは ライトマップ UV で、ライトマップを引き、アルベド（色）に掛けるだけです。

```hlsl
float3 irradiance = lightmap.Sample(linear_sampler, input.lightmap_uv).rgb;
float3 indirect_diffuse = albedo * irradiance;
```

| 項目 | 内容 |
| --- | --- |
| 保存するもの | 放射照度（またはアルベドを掛けた後の出射光） |
| 実行時のコスト | テクスチャ 1 回 |
| 品質 | ベイクの設定で決まる（バウンス数・サンプル数・解像度） |
| 対象 | 静的なメッシュ・静的なライト（動かないもの） |

### ライトマップが長く使われてきた理由

ライトマップは 1990 年代の『Quake』から使われている古い技術ですが、今でも多くのゲームで現役です。理由は品質とコストの取引が飛び抜けて良いからです。オフラインで数時間かけたパス トレーシングの結果を実行時のテクスチャ 1 回で再現できます。リアルタイムの GI 手法が 1 フレーム数ミリ秒で出せる品質とは、桁違いの差があります。さらに、モバイル GPU のような非力な環境でも、変わらず動きます。

代わりに支払う代償は「動かない」ことです。ライトを動かせないドアを開けると光の入り方が変わる、といった動的な変化には対応できません。したがってライトマップは「動かない背景」の光を担当し、動く物体は[ライト プローブ](../probes/index.md)、動くライトは[リアルタイムのライト](dynamic-lights.md)で補う、という役割分担が標準になっています。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Lightmap UVs (UV2)](uv2.md) | 重ならない、専用の UV |
| [Baking Workflow](baking.md) | 事前計算の手順・方向情報 |
| [Specular and Dynamic Objects](dynamic-objects.md) | 鏡面は別・動く物体との併用 |
| [Lightmaps and Dynamic Lights](dynamic-lights.md) | 静的と動的を組み合わせる |

## ライトマップとは

<strong>ライトマップ</strong>は シーンの静的な面の、明るさ（直接光 + 間接光）をあらかじめ計算してテクスチャに焼き込んだものです。実行時はテクスチャを 1 回読むだけで、間接光まで含めたリアルなライティングがほぼ無料で、得られます。

```text
ベイク（制作時）:  シーンの、静的な、面  →  光を、シミュレーション（光が、何度も、反射）  →  ライトマップ（面ごとの、明るさ）
実行時:             面を描くとき、ライトマップを、読んで、明るさに、する（ライティングの、計算は、不要）
```

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | 品質が最高（時間をかけて何度も反射を計算できる。ソフトな影、カラー ブリーディング） |
| 長所 | 実行時のコストが最小（テクスチャを 1 回読むだけ） |
| 長所 | どんなハードウェアでも、動く（モバイルを含む） |
| 短所 | 静的な光・物だけ（動く物、動くライトには使えない） |
| 短所 | ベイクに時間がかかる（数分〜数時間）。調整のたびにベイクし直し |
| 短所 | メモリ（テクスチャが大きい）。ディスク容量 |
| 短所 | UV の作成が必要（[Lightmap UVs (UV2)](uv2.md)） |
| 短所 | 間接光の解像度がテクスチャの解像度で決まる（細かい影の境目は、ぼやける） |

## ライトマップが焼き込むもの

| 光 | ベイクするか |
| --- | --- |
| 直接光（太陽、ライト）（静的なライトのみ） | する（影を含めて）。実行時のシャドウ マップが不要になる |
| 間接光（反射した光） | する（ライトマップの主な、目的） |
| 環境光（空の光） | する（空が固定なら） |
| 動的なライト（動くライト） | しない（実行時に別途、計算） |

<strong>ライトを「ベイク」と「動的」に分ける</strong>のが普通です（[Lightmaps and Dynamic Lights](dynamic-lights.md)）。

## 仕組み

| 段階 | 内容 | ページ |
| --- | --- | --- |
| ① UV を作る | 各面がライトマップのどこに対応するか（重ならない、専用の UV） | [Lightmap UVs (UV2)](uv2.md) |
| ② ベイク | 光をシミュレーションして、ライトマップに書き込む | [Baking Workflow](baking.md) |
| ③ 実行時の読み込み | 描画で、ライトマップを読む | [Lightmaps and Dynamic Lights](dynamic-lights.md) |
| ④ 動く物への対応 | ライト プローブで、動く物を照らす | [Specular and Dynamic Objects](dynamic-objects.md) |

## 描画での使い方（最小）

```hlsl
Texture2D<float3> g_lightmap : register(t7);

float4 main(PSInput input) : SV_Target {
  float3 albedo = g_albedo.Sample(g_linear_wrap, input.uv).rgb;
  float3 baked_light = g_lightmap.Sample(g_linear_clamp, input.lightmap_uv);      // 専用の UV（UV2）で、読む
  return float4(albedo * baked_light, 1.0);                                        // アルベド × 焼き込んだ、明るさ
}
```

<strong>アルベド</strong>に ライトマップの、明るさを掛けるだけです。ライティングの計算がほぼ不要になります。アルベドは元の UV、ライトマップは専用の UV（UV2、[Lightmap UVs (UV2)](uv2.md)）で、読みます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 静的な光を事前に焼き込む
    - [x] 実行時はほぼ無料で高品質

## 参考

- Goral, Torrance, Greenberg, Battaile, "Modeling the Interaction of Light Between Diffuse Surfaces", SIGGRAPH 1984（ラジオシティ）
- Cohen, Wallace, "Radiosity and Realistic Image Synthesis", Academic Press, 1993
- Iwanicki, Sloan, "Precomputed Lighting in Call of Duty: Infinite Warfare", SIGGRAPH 2017, Advances in Real-Time Rendering in Games
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明、ライトマップ、プローブの章）

## 関連ページ

- [GI](../index.md)
- [Probe GI](../probes/index.md)
- [GI Comparison](../comparison.md)
