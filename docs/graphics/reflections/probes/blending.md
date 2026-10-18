---
title: Probe Operation
tags:
  - 描画
---

# Probe Operation

<strong>実際のシーンでは、プローブを複数置き、場所に応じて混ぜます</strong>。<strong>ベイク（事前計算）か動的更新か、空との関係、といった運用の判断</strong>も必要です。このページでは、複数のプローブの混ぜ方・ベイクと動的更新・スカイボックスを説明します。

!!! tip "ポイント"
    - 影響範囲（ボリューム）の重みで、近いプローブ同士を混ぜる。
    - ベイク ＝ 軽いが、動く物は映らない。動的更新 ＝ 重い。
    - 屋外は、空（スカイボックス）のプローブを基準にする。
    - 動的更新は、1 フレームに 1 面だけなど、分割してコストを抑える。

## 複数のプローブを混ぜる
<strong>1 つのプローブ</strong>では、<strong>広いシーンをカバーできません</strong>。場所ごとに複数のプローブを置き、表面の位置に応じて、混ぜます。

| 方式 | 内容 |
| --- | --- |
| <strong>影響範囲（ボリューム）</strong> | 各プローブに影響範囲の箱。範囲内の表面にだけ使う |
| ブレンド | 範囲が重なる所は、距離・重みで複数のプローブを混ぜる |
| ブレンド距離 | 範囲の端で徐々に弱める（突然切り替わらないように） |
| 優先度 | 小さいプローブ（部屋の中）を、大きいプローブ（外）より優先 |
| グローバル プローブ | シーン全体（空・遠景）を覆う、粗いプローブ。フォールバック |

```hlsl
float3 BlendedReflection(float3 pos, float3 R, float roughness) {
  float3 result = 0;
  float total_weight = 0;
  for (int i = 0; i < probe_count_in_cell; ++i) {
    Probe p = probes[probe_indices[i]];
    float w = ProbeWeight(p, pos);
    if (w <= 0.0) continue;
    float3 dir = BoxProjection(pos, R, p.position, p.box_min, p.box_max);
    result += p.cube.SampleLevel(sampler, dir, roughness * max_mip).rgb * w;
    total_weight += w;
  }
  return result / max(total_weight, 1e-4);
}
```

<strong>クラスタード（セル分割）</strong>で、各セルに影響するプローブを<strong>事前に絞り込む</strong>と、速くなります（[Tiled と Clustered](../../../rendering/light-culling.md)のライトと同じ構造）。

## ベイクと動的更新
| 方式 | 内容 | 向く場面 |
| --- | --- | --- |
| 事前ベイク | ビルド時に撮影・フィルタ。実行時のコストなし | 静的な背景 |
| 実行時に更新 | 実行中に、6 面を描き直す（1 フレームに 1 面ずつ分散、など） | 時間帯が変わる・動く物が映る場合 |
| <strong>リアルタイム（毎フレーム）</strong> | 非常に重い。車のミラー・重要な 1 箇所だけ | 限定的 |


事前フィルタ（ミップの作成）は、ベイクなら事前に、動的ならコンピュート シェーダーで毎回行います。コストが大きいため、更新頻度を下げるのが普通です。

事前フィルタ（ミップの作成）は、ベイクなら事前に、動的ならコンピュート シェーダーで毎回行います。コストが大きいため、更新頻度を下げるのが普通です。

<strong>事前フィルタ</strong>（ミップの作成）は、<strong>ベイクなら事前、動的なら、コンピュート シェーダーで毎回</strong>行います。コストが大きいので更新頻度を下げるのが普通です。

## 空（スカイボックス）との関係
<strong>屋外の遠い景色（空）</strong>は、<strong>プローブの視差を気にしなくてよい</strong>（無限遠）ので<strong>グローバルなプローブ（スカイ）</strong>として、<strong>全シーンに適用</strong>します。近くの建物・地面はローカル プローブで補います。

## よくあるミス

??? failure "プローブの境界で、反射が急に切り替わる"
    <strong>影響範囲の端でフェード</strong>して、混ぜる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複数のプローブを、距離で混ぜる
    - [x] ベイク中心、動的は最小限

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [Reflection Probes](index.md)
- [Parallax Correction](parallax.md)
- [Combining with SSR](combine-ssr.md)
