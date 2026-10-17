---
title: Probe Operation
tags:
  - 描画
---

# Probe Operation

**実際のシーンでは、プローブを複数置き、場所に応じて混ぜます**。**ベイク（事前計算）か動的更新か、空との関係、といった運用の判断**も**必要**です。このページでは、**複数のプローブの混ぜ方・ベイクと動的更新・スカイボックス**を説明します。

!!! tip "ポイント"
    - **影響範囲（ボリューム）の重みで、近いプローブ同士を混ぜる**。
    - **ベイク ＝ 軽いが、動く物は映らない**。**動的更新 ＝ 重い**。
    - **屋外は、空（スカイボックス）のプローブを基準**にする。
    - **動的更新は、1 フレームに 1 面だけ**など、**分割**して**コストを抑える**。

## 複数のプローブを混ぜる
**1 つのプローブ**では、**広いシーンをカバーできません**。**場所ごとに複数のプローブ**を置き、**表面の位置に応じて、混ぜます**。

複数のプローブを混ぜる仕組みは、5 つの要素でできています。各プローブには<strong>影響範囲（ボリューム）</strong>の箱があり、範囲内の表面にだけ使います。範囲が重なる所では、距離で決めた重みで複数のプローブを<strong>ブレンド</strong>します。<strong>ブレンド距離</strong>は、範囲の端で徐々に弱める幅で、突然切り替わるのを防ぎます。<strong>優先度</strong>は、小さいプローブ（部屋の中）を大きいプローブ（外）より優先する順序です。そして<strong>グローバル プローブ</strong>は、シーン全体（空・遠景）を覆う粗いプローブで、最後のフォールバックになります。

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

<strong>クラスタード（セル分割）</strong>で、各セルに影響するプローブを**事前に絞り込む**と、速くなります（[Tiled と Clustered](../../../rendering/light-culling.md)のライトと同じ構造）。

## ベイクと動的更新
更新の方式は 3 段階です。<strong>事前ベイク</strong>は、ビルド時に撮影とフィルタを済ませるので、実行時のコストがなく、静的な背景に向きます。<strong>実行時に更新</strong>は、実行中に 6 面を描き直す方式で、1 フレームに 1 面ずつ分散するなどして負荷を抑えます。時間帯が変わる場合や、動く物を映したい場合に使います。<strong>毎フレーム更新</strong>は非常に重いので、車のミラーのような、重要な 1 箇所に限ります。

事前フィルタ（ミップの作成）は、ベイクなら事前に、動的ならコンピュート シェーダーで毎回行います。コストが大きいため、更新頻度を下げるのが普通です。

**事前フィルタ**（ミップの作成）は、**ベイクなら事前、動的なら、コンピュート シェーダーで毎回**行います。**コストが大きい**ので**更新頻度を下げる**のが普通です。

## 空（スカイボックス）との関係
<strong>屋外の遠い景色（空）</strong>は、**プローブの視差を気にしなくてよい**（無限遠）ので<strong>グローバルなプローブ（スカイ）</strong>として、**全シーンに適用**します。**近くの建物・地面**は**ローカル プローブ**で補います。

## よくあるミス

??? failure "プローブの境界で、反射が急に切り替わる"
    **影響範囲の端でフェード**して、混ぜる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **複数のプローブを、距離で混ぜる**
    - [x] **ベイク中心、動的は最小限**

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [Reflection Probes](index.md)
- [Parallax Correction](parallax.md)
- [Combining with SSR](combine-ssr.md)
