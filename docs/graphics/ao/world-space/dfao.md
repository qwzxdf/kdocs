---
title: 距離場 AO（DFAO）
tags:
  - 描画
---

# 距離場 AO（DFAO）

**距離場 AO は、シーンを「符号付き距離場（各点から、最も近い面までの距離）」で表し、その距離場の上で円錐を進めて、遮蔽を求めます**。**レイトレーシングのハードウェアが無くても、画面外の遮蔽を含む AO が得られます**。**距離場は事前計算（静的）**で、**動く物体は別途扱います**。このページでは、**距離場とは・円錐トレースによる AO・長所と短所**を説明します。

!!! tip "ポイント"
    - **距離場 ＝ 各点から、最も近い面までの符号付き距離**。
    - **距離場上を、円錐で進み、距離が小さければ遮蔽**。
    - **ハードウェア レイトレ不要**。
    - **弱点**：**距離場の解像度・動く物体・メモリ**。

## 距離場 AO（DFAO）
<strong>符号付き距離場（SDF）</strong>は、**空間の各点から、最も近い表面までの距離**を、3D テクスチャに格納したものです。**距離がわかる**ので**円錐に沿って歩く**と**遮蔽の割合**を**サンプルを数えずに**求められます。

### 円錐トレース

<strong>法線の周りの円錐（半角 θ）</strong>に沿って、**距離 t**だけ進んだ点での<strong>距離場の値 d(t)</strong> を読みます。**d(t) が、円錐の半径（t·tanθ）より小さければ、円錐が遮られている**ことになります。

<div class="formula">visibility(円錐) ≈ min over t of  clamp( d(t) / (t · tanθ), 0, 1 )</div>

| d(t) と円錐の半径 | 意味 |
| --- | --- |
| **d(t) ≥ t·tanθ** | 近くに表面がない。円錐の断面全体が空いている → 1 |
| **d(t) < t·tanθ** | 表面が円錐の断面の内側に入っている → 遮蔽。**比で割合を出す** |

**最小値**を取る（最も遮られた所で決まる）ので**ソフト シャドウの円錐トレース**と同じ考え方です。

```hlsl
float ConeVisibility(float3 origin, float3 dir, float tan_half_angle) {
  float visibility = 1.0;
  float t = kStartOffset;
  for (int i = 0; i < kSteps && t < max_distance; ++i) {
    float d = SampleDistanceField(origin + dir * t);
    visibility = min(visibility, saturate(d / (t * tan_half_angle)));
    t += max(d, kMinStep);
  }
  return visibility;
}
```

**数本（たとえば 9〜16 本）の円錐**を**法線の周りに配置**して、**コサインで重み付けして平均**したものが、AO です。

### 特徴

| 利点 | 欠点 |
| --- | --- |
| **ノイズが少ない**（円錐 = 領域の平均。点ではない） | **SDF の生成・格納**が必要（メッシュごとの SDF、グローバル SDF） |
| **ソフトで滑らか** | **細い物・薄い物は、SDF の解像度**で潰れる |
| **画面外・隠れた物も効く** | **動く物体・変形**に弱い（SDF の更新が高コスト） |
| **レイトレ ハードウェア不要** | **メモリを食う**（SDF ボリューム） |

**静的な背景**には向き、**キャラクターなどの動く物**は、別途（**カプセルの近似**など）扱うのが一般的です。

## よくあるミス

??? failure "距離場の解像度が粗く、細い物の AO が出ない"
    **解像度を上げる・細い物は別の方法**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **距離場の上で、円錐を進めて遮蔽を求める**
    - [x] **ハードウェア不要だが、距離場の管理が必要**

## 参考

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## 関連ページ

- [世界空間 AO](index.md)
- [レイトレース AO](rtao.md)
- [距離場の影](../../shadows/sdf-shadows.md)
