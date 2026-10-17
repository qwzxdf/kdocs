---
title: レイトレース AO・距離場 AO・ボクセル AO
tags:
  - 描画
---

# レイトレース AO・距離場 AO・ボクセル AO

スクリーン空間の AO（SSAO・HBAO・GTAO）は、**深度バッファという「画面から見える面」しか知らない**ので**画面外・隠れた物・薄い物**で破綻します。この限界を超えるには、**画面ではなく、シーンそのもの**を調べる必要があります。このページでは、**シーン全体のデータ**（三角形・距離場・ボクセル）を使う、3 種類の AO を説明します。いずれも、<strong>「V(ω)（その方向が遮られているか）」を、本物のシーン</strong>で調べる、という点が共通しています。

!!! tip "ポイント"
    - スクリーン空間の限界を超えるには、<strong>シーン全体のデータ構造</strong>が必要。
    - <strong>レイトレース AO（RTAO）</strong>：<strong>三角形の BVH</strong> に<strong>コサイン分布のレイ</strong>を飛ばす。<strong>正確</strong>。<strong>ノイズ除去が必須</strong>。
    - <strong>距離場 AO（DFAO）</strong>：<strong>符号付き距離場（SDF）</strong>で、<strong>円錐をトレース</strong>。<strong>ソフトでノイズが少ない</strong>。<strong>静的なシーン向き</strong>。
    - <strong>ボクセル AO（VXAO）</strong>：<strong>ボクセル化</strong>したシーンを、<strong>円錐でトレース</strong>。<strong>動的なシーンにも使える</strong>が、<strong>粗い</strong>。
    - どれも<strong>画面外・隠れた物も遮蔽に入れられる</strong>。コスト・メモリはスクリーン空間より大きい。

## 共通する考え方

[理論](theory.md)の AO は、`AO = (1/π) ∫ V(ω)(n·ω) dω` でした。V(ω) は、**方向 ω にレイを飛ばして、半径 R 以内に何かに当たるか**です。3 方式は**この V を別々のデータ構造で求める**だけです。

| 方式 | V を求めるデータ | 求め方 |
| --- | --- | --- |
| **RTAO** | 三角形の BVH（加速構造） | **レイを飛ばして**、最大距離 R 以内に当たるか |
| **DFAO** | 符号付き距離場（SDF） | **円錐**に沿って、**距離場から、遮蔽の割合**を求める |
| **VXAO** | ボクセル（占有度の 3D グリッド） | **円錐**に沿って、**ボクセルの占有度を積み上げる** |

## レイトレース AO（RTAO）

**DXR**（DirectX Raytracing）などのレイトレーシングで、**三角形に実際にレイを飛ばして**、AO を求めます。

### 手順

| 手順 | 内容 |
| --- | --- |
| **① 画素の位置と法線を得る** | G-Buffer から |
| **② レイの方向を作る** | **法線の側の半球**に**コサイン分布**で |
| **③ レイを飛ばす** | **最大距離 R**（影響半径）まで。**any-hit は不要**（当たったかだけ分かればよい） |
| **④ 当たったか** | 当たれば V = 0、当たらなければ V = 1 |
| **⑤ 平均する** | `AO = 平均(V)` |

[理論](theory.md)のとおり、**コサイン分布でサンプルすれば、`AO = V の平均`**です。

```hlsl
[shader("raygeneration")]
void RtaoRayGen() {
  uint2 pixel = DispatchRaysIndex().xy;
  float3 p = WorldPosition(pixel);
  float3 n = WorldNormal(pixel);

  float3 dir = CosineSampleHemisphere(n, Random2(pixel, frame_index));

  RayDesc ray;
  ray.Origin = p + n * kRayBias;
  ray.Direction = dir;
  ray.TMin = 0.0;
  ray.TMax = ao_radius;

  AoPayload payload;
  payload.hit = 1.0;
  TraceRay(scene, RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH | RAY_FLAG_SKIP_CLOSEST_HIT_SHADER,
           0xFF, 0, 0, 0, ray, payload);

  ao_output[pixel] = payload.hit;
}
```

| 点 | 説明 |
| --- | --- |
| **`ACCEPT_FIRST_HIT_AND_END_SEARCH`** | **最初に当たった時点で終了**。最も近い交点は不要なので、**速い** |
| **`SKIP_CLOSEST_HIT_SHADER`** | 当たった後のシェーダーを省略 |
| **ミス シェーダーで `hit = 0`** | 当たらなければ、可視（payload の初期値を 1 にして、ミスで 0 にする、などの規約） |
| **`ray.TMax = R`** | **半径 R**。これが、AO の影響範囲 |
| **レイのバイアス** | 自己交差を避けるため、**法線方向に少し浮かせる** |

### 特徴

| 利点 | 欠点 |
| --- | --- |
| **正確**（画面外・隠れた物・薄い物も正しく遮蔽） | **1 画素 1〜2 本**のレイでは、**ノイズが大きい** |
| **ハローなどのアーティファクトが無い** | **ノイズ除去（デノイザー）が必須**（[フィルタ](filtering.md)） |
| **コサイン重みが自然に入る** | **レイトレーシング対応の GPU** が必要。**BVH の構築・更新**のコスト |
| **半径の大きさに強い** | 動く物体が多いと、**BVH の更新**が重い |

### デノイズ

レイは**画素あたり 1 本**程度なので、**ノイズだらけ**です。<strong>空間（バイラテラル）と時間（再投影）</strong>で平均します。<strong>AO は 1 チャンネル（スカラー）</strong>で、他のレイトレ効果（反射・GI）より、**デノイズが軽い**です。

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

## ボクセル AO（VXAO）

**シーンをボクセル（3D の小さな箱）の格子に変換**し、各ボクセルに**占有度**（どれだけ埋まっているか）を保存します。**ミップマップ**を作り、**粗いレベルは広い範囲の平均の占有度**を持ちます。AO は**円錐に沿って、ミップを上げながら、占有度を積み上げる**ことで求めます。

### 円錐トレース

**円錐の断面は距離が離れるほど広がる**ので、**距離に応じたミップ**を読みます（近くは細かく、遠くは粗く）。**占有度を前から順に合成**します。

<div class="formula">occ ← occ + (1 − occ) · α(位置)　、　（α：その位置のボクセル占有度）</div>

```hlsl
float ConeOcclusion(float3 origin, float3 dir, float aperture) {
  float occlusion = 0.0;
  float t = kStartOffset;
  while (t < max_distance && occlusion < 1.0) {
    float diameter = 2.0 * aperture * t;
    float mip = log2(diameter / voxel_size);
    float alpha = voxel_tex.SampleLevel(linear_sampler, WorldToVoxel(origin + dir * t), mip).a;
    occlusion += (1.0 - occlusion) * alpha * DistanceFalloff(t);
    t += diameter * 0.5;
  }
  return 1.0 - occlusion;
}
```

| 点 | 説明 |
| --- | --- |
| **`mip`** | 円錐の直径に応じて、ボクセルのミップを選ぶ |
| **前から合成** | 手前の占有度が奥の寄与を隠す（アルファ合成と同じ） |
| **距離の減衰** | 遠い遮蔽を弱める（オブスキュランス） |

### 特徴

| 利点 | 欠点 |
| --- | --- |
| **動的なシーンにも使える**（毎フレーム、ボクセル化を更新） | **ボクセルの解像度が粗い**。**細部・薄い物は潰れる** |
| **AO だけでなく、間接光・反射・影**にも同じ構造が使える（**VXGI**。[GI](../index.md)） | **ボクセル化のコスト**と**メモリ**（3D テクスチャ） |
| **レイトレ ハードウェア不要** | <strong>漏れ（ライト リーク）</strong>・**ブロック状のアーティファクト** |

## 3 方式の比較

| 項目 | RTAO | DFAO | VXAO |
| --- | --- | --- | --- |
| **データ** | 三角形の BVH | SDF | ボクセルとミップ |
| **精度** | <strong>高（正確）</strong> | 中（SDF の解像度） | 低〜中（ボクセルの解像度） |
| **ノイズ** | **大**（レイ 1〜2 本） | **小** | 小〜中 |
| **動的なシーン** | BVH の更新で対応 | **弱い** | **強い** |
| **ハードウェア** | **レイトレ対応 GPU** | 不要 | 不要 |
| **メモリ** | BVH | SDF ボリューム | ボクセル ボリューム |
| **薄い物・細部** | **正確** | 弱い | 弱い |
| **向く場面** | 高品質・レイトレ対応の環境 | 静的な屋外・広い範囲 | 動的なシーン・GI との併用 |

## スクリーン空間との使い分け

| 状況 | おすすめ |
| --- | --- |
| **広い対応環境** | スクリーン空間（[GTAO](gtao.md) など） |
| **画面外の遮蔽が必要・最高品質** | RTAO |
| **広い屋外の静的な AO** | DFAO |
| **GI とまとめて、動的に** | VXAO など |
| **併用** | **大きな遮蔽は世界空間の方式**、**細部の接触はスクリーン空間**（組み合わせる） |

## よくあるミス

??? failure "RTAO で、ノイズ除去をせず、ざらざらの画面になる"
    **空間・時間のデノイズ**が前提です（[フィルタ](filtering.md)）。

??? failure "RTAO のレイの起点が、面にめり込んで自己交差する"
    **法線方向にわずかに浮かせて**起点にします。

??? failure "SDF の解像度が足りず、細い柱の AO が消える"
    SDF の解像度を上げるか、細い物は別に扱います。

??? failure "ボクセルの更新を、毎フレーム全部やって、重い"
    動く物の周辺だけ、更新します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 世界空間の AO は、<strong>画面に頼らず、シーン全体のデータで V(ω) を求める</strong>
    - [x] <strong>RTAO</strong>：BVH にレイ。<strong>正確だがノイズ除去が必須</strong>
    - [x] <strong>DFAO</strong>：距離場で円錐トレース。<strong>ソフトでノイズが少ないが、静的向き</strong>
    - [x] <strong>VXAO</strong>：ボクセルのミップで円錐トレース。<strong>動的に使えるが粗い</strong>
    - [x] <strong>大きな遮蔽は世界空間、細部の接触はスクリーン空間</strong>、と併用する手もある

## 参考

- Microsoft, DirectX Raytracing (DXR) 仕様書（`TraceRay` と `RAY_FLAG_*`）
- Crassin et al., "Interactive Indirect Illumination Using Voxel Cone Tracing"（2011）
- Wright, "Dynamic Occlusion with Signed Distance Fields"（SIGGRAPH 2015 Advances in Real-Time Rendering）

## 関連ページ

- [環境光遮蔽（AO）](index.md)
- [AO の理論](theory.md)
- [GTAO](gtao.md)
- [フィルタ](filtering.md)
- [方式の比較](comparison.md)
