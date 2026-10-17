---
title: ぼかしの実装
tags:
  - 描画
---

# ぼかしの実装

**速度バッファができたら、画素ごとに速度の向きへ、画像を複数サンプルして平均**します。**単純な線形ブラーは、速い物体の輪郭がぷつっと切れ、静止した前景に背景の動きがにじむ**などの破綻を起こすので、**深度と速度で重みを付ける**のが**標準**です。このページでは、**基本のぼかし・ジッターでバンディングを消す方法・前景と背景の重み付け（McGuire 方式）・サンプル数・コスト**を説明します。

!!! tip "ポイント"
    - ぼかし ＝ <strong>画素の速度ベクトルに沿って、前後にサンプルして平均</strong>。
    - サンプル数は<strong>8〜16</strong>。<strong>少ないとサンプルが離散的に見える（縞）</strong>。
    - <strong>サンプル位置を画素ごとにジッター</strong>すると、<strong>縞がノイズに変わる</strong>。
    - <strong>重み付き平均</strong>：<strong>手前の速い物は奥にかぶさり、奥の速い物は手前の遅い物には、にじまない</strong>。
    - <strong>速度の長さ</strong>を<strong>最大値で制限</strong>し、<strong>短い速度（< 0.5 画素）はスキップ</strong>。
    - <strong>半解像度</strong>や<strong>タイル</strong>で<strong>コストを下げる</strong>。

## 基本のぼかし

```hlsl
float3 MotionBlurBasic(float2 uv, float2 velocity_uv, int sample_count) {
  float3 sum = scene_color.SampleLevel(linear_clamp, uv, 0).rgb;
  [loop] for (int i = 1; i < sample_count; ++i) {
    float t = float(i) / float(sample_count - 1) - 0.5;
    float2 sample_uv = uv + velocity_uv * t;
    sum += scene_color.SampleLevel(linear_clamp, sample_uv, 0).rgb;
  }
  return sum / float(sample_count);
}
```

| 点 | 説明 |
| --- | --- |
| <strong>`t`（−0.5〜+0.5）</strong> | **速度ベクトルの両側（前後）にサンプルを置く**（**中心がその画素**） |
| **`velocity_uv`** | **シャッター角を掛けた、UV での移動量** |
| **サンプル数** | **8〜16**。**速い動きは多く必要** |

**線形ブラーの欠点**：**サンプルが一直線に並ぶので、サンプル数が少ないと、「点の列」が見える**。**輪郭がくっきり**出ない**。

## ジッターで縞を消す

**サンプルの位置を画素ごとに少しずらす**と、**規則的な縞が細かいノイズに変わり、目立たなくなります**。

```hlsl
float3 MotionBlurJitter(float2 uv, float2 velocity_uv, int sample_count, float noise) {
  float3 sum = 0;
  [loop] for (int i = 0; i < sample_count; ++i) {
    float t = (float(i) + noise) / float(sample_count) - 0.5;
    float2 sample_uv = uv + velocity_uv * t;
    sum += scene_color.SampleLevel(linear_clamp, sample_uv, 0).rgb;
  }
  return sum / float(sample_count);
}
```

| 点 | 説明 |
| --- | --- |
| <strong>`noise`（0〜1）</strong> | **インターリーブド グラディエント ノイズ**などを**使う**（**ブルー ノイズが理想**） |
| **効果** | **サンプルが 8 個でも、なめらかに見える** |
| **TAA と併用** | **フレームごとに `noise` を変えると、TAA が平均して、さらに滑らか** |

<!-- fig:motion-blur-jitter:begin -->
<!-- fig:motion-blur-jitter:end -->

## 前景と背景の問題

**単純な平均では、次の破綻が起きます**。

| 状況 | 問題 |
| --- | --- |
| <strong>速い物体の輪郭の外（背景）</strong> | **背景の画素は速度 0 なので、ぼけず、物体の尾が輪郭でぷつっと切れる** |
| **静止した前景の物の縁** | **背景の速い動きでぼかした色が、静止した前景にまでにじむ** |

## 深度と速度による重み付け

**サンプルを集めるとき**、**そのサンプルが自分より手前か奥か**、**サンプルの速度が自分の位置まで届くか**で**重み**を**決めます**（**McGuire らの方法**）。

```hlsl
float SampleWeight(float center_depth, float sample_depth,
                   float2 center_velocity_px, float2 sample_velocity_px,
                   float offset_length_px) {
  float depth_compare = saturate(0.5 + (sample_depth - center_depth) * kDepthScale);
  float center_reach = saturate(1.0 - offset_length_px / max(length(center_velocity_px), 1e-4));
  float sample_reach = saturate(1.0 - offset_length_px / max(length(sample_velocity_px), 1e-4));
  float front = (1.0 - depth_compare) * sample_reach;
  float back = depth_compare * center_reach;
  return front + back;
}
```

| 点 | 説明 |
| --- | --- |
| **`depth_compare`** | **サンプルが自分より奥（1 に近い）か手前（0 に近い）か** |
| **`sample_reach`** | **手前のサンプルの速度が、自分の位置まで届くか**（**手前の動く物が自分にかぶさる**） |
| **`center_reach`** | **自分の速度が奥のサンプルまで届くか**（**自分の動きが奥の色を混ぜる**） |
| **`front + back`** | <strong>手前なら「相手の速度が届く」、奥なら「自分の速度が届く」</strong> |

**考え方**：**手前の動く物のブラーは、奥の背景にかぶさる**。**奥の物が動いていても手前の静止した物にはにじまない**。

```hlsl
float3 MotionBlurWeighted(float2 uv, int sample_count, float noise) {
  float center_depth = LinearDepth(uv);
  float2 center_velocity = velocity.SampleLevel(point_clamp, uv, 0).xy * resolution;
  float2 neighbor_velocity = neighbor_max.SampleLevel(point_clamp, uv, 0).xy * resolution;
  float3 sum = scene_color.SampleLevel(linear_clamp, uv, 0).rgb;
  float weight_sum = 1.0;
  [loop] for (int i = 0; i < sample_count; ++i) {
    float t = (float(i) + noise) / float(sample_count) - 0.5;
    float2 offset_px = neighbor_velocity * t;
    float2 sample_uv = uv + offset_px / resolution;
    float sample_depth = LinearDepth(sample_uv);
    float2 sample_velocity = velocity.SampleLevel(point_clamp, sample_uv, 0).xy * resolution;
    float w = SampleWeight(center_depth, sample_depth, center_velocity, sample_velocity, length(offset_px));
    sum += scene_color.SampleLevel(linear_clamp, sample_uv, 0).rgb * w;
    weight_sum += w;
  }
  return sum / weight_sum;
}
```

**サンプルの方向と長さ**には、<strong>自分の速度ではなく、近傍の最大速度（`neighbor_velocity`）</strong>を**使う**ことで**輪郭の外側にも尾が伸びます**（[タイル最大速度](tile-max.md)）。

## サンプル数と最大長

| 項目 | 目安 |
| --- | --- |
| **サンプル数** | **8〜16**（**ジッターありなら 8 で足りる**） |
| **最大ブラー長** | **画面の高さの 3〜5 %**（**それ以上の速度は切る**） |
| **最小速度** | **0.5 画素未満の画素は、ブラーをスキップ** |
| **解像度** | **半解像度でも見た目は大きく変わらない**（**合成時に境界に注意**） |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **重み付き平均** | **輪郭のにじみ・かぶりを自然に**（必須） |
| <strong>ジッター（ブルー ノイズ）</strong> | **少ないサンプルでなめらか** |
| **近傍最大速度** | **尾の長さと方向に使う** |
| **速度が小さい画素はスキップ** | **コスト削減** |
| **TAA と併用** | **ノイズをさらにならす** |
| **カメラ・物体を同じパスで** | **速度バッファで一括処理** |

## よくあるミス

??? failure "サンプルが点の列に見える（縞）"
    **画素ごとのジッター**を入れる。

??? failure "静止した前景に、背景の動きがにじむ"
    **深度と速度の重み付け**を使う。

??? failure "速い物体の輪郭で、ぼかしが切れる"
    **近傍の最大速度**を使い、**尾を輪郭の外へ**伸ばす。

??? failure "サンプル数を増やしても、重いだけで効果が少ない"
    **ジッター**で**ノイズ化**する方が**効く**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ぼかし ＝ <strong>速度に沿って前後にサンプルして平均</strong>
    - [x] <strong>画素ごとのジッター</strong>で<strong>縞をノイズに</strong>
    - [x] <strong>深度と速度の重み付け</strong>で<strong>前景・背景の破綻を防ぐ</strong>
    - [x] <strong>近傍最大速度</strong>で<strong>輪郭の外にも尾を伸ばす</strong>
    - [x] <strong>最大長で制限、遅い画素はスキップ</strong>

## 参考

- McGuire et al., "A Reconstruction Filter for Plausible Motion Blur"（I3D 2012）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Sousa, "Graphics Gems from CryENGINE 3"（SIGGRAPH 2013）

## 関連ページ

- [モーション ブラー](index.md)
- [速度バッファ](velocity-buffer.md)
- [タイル最大速度](tile-max.md)
- [強さと TAA](strength-taa.md)
