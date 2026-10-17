---
title: Lightmaps
tags:
  - 描画
---

# Lightmaps

**ライトマップは、静的なシーンの間接光（と影）を、事前に計算（ベイク）して、テクスチャに保存する手法**です。**実行時は、テクスチャを読むだけ**なので、**非常に軽く、品質も高い**です。ただし、**光や物が動くと使えません**。このセクションでは、**原理・ライトマップ UV・ベイクの流れ・方向情報・鏡面・動く物体・動的ライトとの関係**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **静的な光を、事前にテクスチャへ焼き込む**。
    - **実行時は、読むだけ**で**最も軽い**。
    - **ライトマップ用の UV（UV2）が必要**。
    - **動く物体・動く光には使えない**（プローブなどで補う）。

## 原理
**オフライン**で**パス トレーシング**などの、**重いが正確な計算**を行い、<strong>各表面点に届く光（放射照度）</strong>を求めます。それを**メッシュ専用の UV 座標**に沿って、<strong>テクスチャ（ライトマップ）</strong>に書き込みます。

実行時、**ピクセル シェーダー**は、**ライトマップ UV で、ライトマップを引き**、**アルベド（色）に掛け**るだけです。

```hlsl
float3 irradiance = lightmap.Sample(linear_sampler, input.lightmap_uv).rgb;
float3 indirect_diffuse = albedo * irradiance;
```

ライトマップに保存するのは、<strong>放射照度</strong>（またはアルベドを掛けた後の出射光）です。実行時のコストは、テクスチャ 1 回の読み込みだけです。品質はベイクの設定（バウンス数・サンプル数・解像度）で決まり、時間をかければいくらでも上げられます。ただし、対象は静的なメッシュと静的なライトに限られます。

### ライトマップが長く使われてきた理由

ライトマップは 1990 年代の『Quake』から使われている古い技術ですが、今でも多くのゲームで現役です。理由は、品質とコストの取引が飛び抜けて良いからです。オフラインで数時間かけたパス トレーシングの結果を、実行時のテクスチャ 1 回で再現できます。リアルタイムの GI 手法が 1 フレーム数ミリ秒で出せる品質とは、桁違いの差があります。さらに、モバイル GPU のような非力な環境でも、変わらず動きます。

代わりに支払う代償は、「動かない」ことです。ライトを動かせない、ドアを開けると光の入り方が変わる、といった動的な変化には対応できません。したがって、ライトマップは「動かない背景」の光を担当し、動く物体は[ライト プローブ](../probes/index.md)、動くライトは[リアルタイムのライト](dynamic-lights.md)で補う、という役割分担が標準になっています。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [ライトマップ UV](uv2.md) | 重ならない、専用の UV |
| [Baking Workflow](baking.md) | 事前計算の手順・方向情報 |
| [Specular and Dynamic Objects](dynamic-objects.md) | 鏡面は別・動く物体との併用 |
| [Lightmaps and Dynamic Lights](dynamic-lights.md) | 静的と動的を組み合わせる |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **静的な光を、事前に焼き込む**
    - [x] **実行時はほぼ無料で、高品質**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [GI](../index.md)
- [Probe GI](../probes/index.md)
- [GI の比較](../comparison.md)
