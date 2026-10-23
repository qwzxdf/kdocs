---
title: Probe Operation
tags:
  - 描画
---

# Probe Operation

<strong>実際のシーンではプローブを複数置き、場所に応じて混ぜます</strong>。ベイク（事前計算）か動的更新か、空との関係、といった運用の判断も必要です。このページでは複数のプローブの混ぜ方・ベイクと動的更新・スカイボックスを説明します。

!!! tip "ポイント"
    - 影響範囲（ボリューム）の重みで、近いプローブ同士を混ぜる。
    - ベイク ＝ 軽いが、動く物は映らない。動的更新 ＝ 重い。
    - 屋外は空（スカイボックス）のプローブを基準にする。
    - 動的更新は 1 フレームに 1 面だけなど、分割してコストを抑える。

!!! info "このページを読む前に"
    - [Reflection Probes](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 複数のプローブを混ぜる
<strong>1 つのプローブ</strong>では 広いシーンをカバーできません。場所ごとに複数のプローブを置き、表面の位置に応じて混ぜます。

| 方式 | 内容 |
| --- | --- |
| 影響範囲（ボリューム） | 各プローブに影響範囲の箱。範囲内の表面にだけ使う |
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

クラスタード（セル分割）で、各セルに影響するプローブを事前に絞り込むと、速くなります（[Tiled と Clustered](../../../rendering/light-culling.md)のライトと同じ構造）。

## ベイクと動的更新
| 方式 | 内容 | 向く場面 |
| --- | --- | --- |
| 事前ベイク | ビルド時に撮影・フィルタ。実行時のコストなし | 静的な背景 |
| 実行時に更新 | 実行中に、6 面を描き直す（1 フレームに 1 面ずつ分散、など） | 時間帯が変わる・動く物が映る場合 |
| <strong>リアルタイム（毎フレーム）</strong> | 重い。車のミラー・重要な 1 箇所だけ | 限定的 |


事前フィルタ（ミップの作成）は、ベイクなら事前に動的ならコンピュート シェーダーで毎回行います。コストが大きいため更新頻度を下げるのが普通です。

事前フィルタ（ミップの作成）は、ベイクなら事前に動的ならコンピュート シェーダーで毎回行います。コストが大きいため更新頻度を下げるのが普通です。

事前フィルタ（ミップの作成）は、ベイクなら事前、動的ならコンピュート シェーダーで毎回行います。コストが大きいので更新頻度を下げるのが普通です。

## 空（スカイボックス）との関係
<strong>屋外の遠い景色（空）</strong>は プローブの視差を気にしなくてよい（無限遠）のでグローバルなプローブ（スカイ）として、全シーンに適用します。近くの建物・地面はローカル プローブで補います。

## 複数のプローブを使う

<strong>シーンには複数の反射プローブ</strong>（部屋ごと、エリアごと）があります。物の位置に応じてどのプローブを使うか複数が、重なるときにどう混ぜるかを決める必要が、あります。

## 影響範囲

<strong>各プローブ</strong>は 影響範囲（箱、または球）を持ちます。範囲の中の物だけがそのプローブを、使います。

```text
  ┌──────────────┐      ┌──────────────┐
  │  プローブ A   │      │  プローブ B   │
  │      ●       │ ░░░░ │      ●       │       ░░ = A と B の影響範囲が、重なる境目（ブレンド領域）
  └──────────────┘      └──────────────┘
```

範囲の境目で 急に切り替えると反射がぱっと、変わります（ポップ）。境目で 2 つをブレンドしてなめらかに、つなぎます。

## 重みの計算

<strong>物の位置</strong>が 各プローブの範囲のどこに、あるかで重みを決めます。範囲の中心に近いほど重みが大きく端に、近づくと 0 に近づきます。

```hlsl
// 軸に平行な、箱の影響範囲に対する、重み。中心で 1、端で 0 になる（blend_distance だけ、内側からフェード）。
float ProbeWeight(float3 world_pos, float3 box_min, float3 box_max, float blend_distance) {
  float3 inside = min(world_pos - box_min, box_max - world_pos);          // 各軸で、最も近い面までの距離（内側が正）
  float d = min(min(inside.x, inside.y), inside.z);                        // 3 軸のうち、最も近い面までの距離
  return saturate(d / blend_distance);                                      // 面から、blend_distance 以上内側なら 1。面の上で 0
}
```

箱の面からの距離が `blend_distance`（フェードの、幅）より小さければ重みが距離に、比例して減ります。十分、内側なら重み 1です。範囲の外では 0 です。

## 複数を混ぜる

<strong>重みが 0 でないプローブ</strong>（物の位置を含む、範囲）を すべて、読み重みで混ぜます。

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

キューブマップ配列（`TextureCubeArray`）に、全プローブのキューブマップを、まとめてインデックスで選びます。各プローブごとに視差補正（[Parallax Correction](parallax.md)）を行って、引きます。

## 優先度

<strong>プローブの範囲が入れ子</strong>（部屋の中の小さな、部屋）になっているとき内側の小さな、プローブを優先します。面積が小さい範囲ほど優先度が、高い（より局所的な情報）。

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

内側の局所プローブが重みを取り、残りの重みは外側の（空の、グローバル プローブ）で埋めます。局所プローブの範囲の端で空の反射へ、なめらかにつながります。

## プローブの探索

<strong>物ごとに全プローブを調べる</strong>のは、重い（数百個）です。物の位置に影響するプローブだけを、効率よく探します。

| 方法 | 内容 |
| --- | --- |
| CPU で物ごとに決める（動く物） | 物の、位置から影響するプローブを事前に選び物の、定数バッファで渡す（最大 2〜4 個） |
| 画面をクラスターに分ける（クラスタード シェーディング） | クラスターごとに、影響するプローブのリストを持つ（[Shadows for Many Lights](../../shadows/local-lights/many-lights.md) と同じ、仕組み） |
| プローブの範囲を描く（ディファード デカール方式） | 各プローブの範囲を、箱として描きその箱の中の画素に反射を、足し込む |

## 動く物の扱い

<strong>動く物</strong>（車、キャラクター）は 位置が変わるので、影響するプローブも変わります。位置から毎フレーム、プローブを選び重みを計算します。物がプローブの範囲をまたぐとき、なめらかに切り替わるよう重みを、時間方向に補間（前のフレームの重みと、混ぜる）します。

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
