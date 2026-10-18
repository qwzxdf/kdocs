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

## 複数の、プローブを、使う

<strong>シーンには、複数の、反射プローブ</strong>（部屋ごと、エリアごと）が、あります。<strong>物の位置</strong>に、応じて、どのプローブを、使うか、複数が、重なるときに、どう、混ぜるかを、決める必要が、あります。

## 影響範囲

<strong>各プローブ</strong>は、<strong>影響範囲</strong>（箱、または、球）を、持ちます。範囲の中の、物だけが、そのプローブを、使います。

```text
  ┌──────────────┐      ┌──────────────┐
  │  プローブ A   │      │  プローブ B   │
  │      ●       │ ░░░░ │      ●       │       ░░ = A と B の影響範囲が、重なる境目（ブレンド領域）
  └──────────────┘      └──────────────┘
```

<strong>範囲の境目</strong>で、<strong>急に、切り替える</strong>と、反射が、ぱっと、変わります（ポップ）。境目で、2 つを、ブレンドして、なめらかに、つなぎます。

## 重みの、計算

<strong>物の位置</strong>が、<strong>各プローブの、範囲の、どこに、あるか</strong>で、重みを、決めます。範囲の、中心に近いほど、重みが、大きく、端に、近づくと、0 に、近づきます。

```hlsl
// 軸に平行な、箱の影響範囲に対する、重み。中心で 1、端で 0 になる（blend_distance だけ、内側からフェード）。
float ProbeWeight(float3 world_pos, float3 box_min, float3 box_max, float blend_distance) {
  float3 inside = min(world_pos - box_min, box_max - world_pos);          // 各軸で、最も近い面までの距離（内側が正）
  float d = min(min(inside.x, inside.y), inside.z);                        // 3 軸のうち、最も近い面までの距離
  return saturate(d / blend_distance);                                      // 面から、blend_distance 以上内側なら 1。面の上で 0
}
```

<strong>箱の、面からの、距離</strong>が、<strong>`blend_distance`</strong>（フェードの、幅）より、小さければ、重みが、距離に、比例して、減ります。十分、内側なら、重み 1です。範囲の外では、0 です。

## 複数を、混ぜる

<strong>重みが、0 でない、プローブ</strong>（物の位置を、含む、範囲）を、<strong>すべて</strong>、読み、重みで、混ぜます。

```hlsl
// 影響する、すべてのプローブを、重みで混ぜる。重みの合計が 1 を超えたら、正規化する。
float3 SampleProbes(float3 world_pos, float3 R, float roughness, uint probe_count, uint probe_indices[8]) {
  float3 sum = 0.0;
  float weight_sum = 0.0;
  for (uint i = 0; i < probe_count; ++i) {
    ProbeData p = g_probes[probe_indices[i]];
    float w = ProbeWeight(world_pos, p.box_min, p.box_max, p.blend_distance);
    if (w <= 0.0) continue;
    float3 dir = ParallaxCorrect(R, world_pos, p.box_min, p.box_max, p.position);       // 各プローブごとに、視差補正
    float mip = roughness * (p.mip_count - 1);
    sum += g_probe_cubes.SampleLevel(g_linear_clamp, float4(dir, p.cube_index), mip).rgb * w;   // キューブマップ配列から引く
    weight_sum += w;
  }
  return sum / max(weight_sum, 1e-4);
}
```

<strong>キューブマップ配列</strong>（`TextureCubeArray`）に、<strong>全プローブの、キューブマップ</strong>を、まとめて、インデックスで、選びます。各プローブごとに、視差補正（[Parallax Correction](parallax.md)）を、行って、引きます。

## 優先度

<strong>プローブの、範囲が、入れ子</strong>（<strong>部屋の、中の、小さな、部屋</strong>）に、なっているとき、内側の、小さな、プローブを、優先します。面積が、小さい、範囲ほど、優先度が、高い（より、局所的な、情報）。

```hlsl
// 優先度の高い（範囲の小さい）プローブから、順に、重みを「使い切る」方式。
float remaining = 1.0;
for (uint i = 0; i < probe_count; ++i) {                                    // probe_indices は、優先度順（範囲が小さい順）に、ソート済み
  float w = min(ProbeWeight(...), remaining);                                // 残りの重みの、範囲で
  ...
  remaining -= w;
  if (remaining <= 0.0) break;
}
// 残りは、グローバルな反射（空のキューブマップ）で、埋める。
float3 result = local_sum + g_sky_cube.SampleLevel(g_linear_clamp, R, mip).rgb * remaining;
```

<strong>内側の、局所プローブが、重みを、取り</strong>、<strong>残りの、重み</strong>は、外側の（空の、グローバル プローブ）で、埋めます。局所プローブの、範囲の、端で、空の反射へ、なめらかに、つながります。

## プローブの、探索

<strong>物ごとに、全プローブを、調べる</strong>のは、<strong>重い</strong>（数百個）です。物の位置に、影響する、プローブだけを、効率よく、探します。

| 方法 | 内容 |
| --- | --- |
| CPU で、物ごとに、決める（動く物） | 物の、位置から、影響する、プローブを、事前に、選び、物の、定数バッファで、渡す（最大 2〜4 個） |
| 画面を、クラスターに、分ける（クラスタード シェーディング） | クラスターごとに、影響するプローブの、リストを、持つ（[Shadows for Many Lights](../../shadows/local-lights/many-lights.md) と、同じ、仕組み） |
| プローブの、範囲を、描く（ディファード デカール方式） | 各プローブの範囲を、箱として、描き、その、箱の中の画素に、反射を、足し込む |

## 動く物の、扱い

<strong>動く物</strong>（車、キャラクター）は、<strong>位置が、変わる</strong>ので、影響する、プローブも、変わります。位置から、毎フレーム、プローブを、選び、重みを、計算します。物が、プローブの、範囲を、またぐとき、なめらかに、切り替わるよう、重みを、時間方向に、補間（前のフレームの重みと、混ぜる）します。

## よくあるミス

??? failure "プローブの境界で、反射が急に切り替わる"
    <strong>影響範囲の端でフェード</strong>して、混ぜる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複数のプローブを、距離で混ぜる
    - [x] ベイク中心、動的は最小限

## 参考

- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014, Physically Based Shading in Theory and Practice
- Lagarde, Zanuttini, "Local Image-Based Lighting With Parallax-Corrected Cubemap", SIGGRAPH 2012 Talks（箱による、視差補正）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（反射、IBL の章）
- Microsoft Learn, "TextureCubeArray (HLSL)"

## 関連ページ

- [Reflection Probes](index.md)
- [Parallax Correction](parallax.md)
- [Combining with SSR](combine-ssr.md)
