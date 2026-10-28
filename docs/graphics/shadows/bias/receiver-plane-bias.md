---
title: Receiver Plane Bias
tags:
  - 描画
---

# Receiver Plane Bias

<strong>PCF のように 1 点でなく周りの複数点を調べるとき</strong>、中心の点に合わせたバイアスでは、周りの点（別の高さにある）で、アクネが出ます。受け手の面の傾きから周りの点それぞれの正しい深度を計算するのが受け手平面バイアス（Receiver Plane Depth Bias）です。PCF の広いカーネルでもアクネが出にくいので、高品質な影で使われます。このページでは問題の理由・平面の式・実装を説明します。

!!! tip "ポイント"
    - PCF の周辺サンプルは、中心とは別の深度にあるので中心のバイアスでは合わない。
    - 受け手平面バイアス ＝ 面の傾き（深度の勾配）から、サンプルごとの深度を補正する。
    - 画面空間の微分（`ddx`・`ddy`）から、光の空間での勾配を求める。
    - 広い PCF・PCSS で効果が大きい。

!!! info "このページを読む前に"
    - [Shadow Bias](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 対策 4：受け手平面バイアス（Receiver Plane Depth Bias）
<strong>PCF</strong>（複数点のサンプル）と組み合わせると周りのサンプル点の深度を中心の点と同じ面の上にあるものとして補正する必要があります。面の傾きからサンプルごとに深度を補正します。

シャドウ マップの座標 (u, v) が動いたときの面の深度の変化（`dz/du`、`dz/dv`）を 画面上の微分（`ddx`・`ddy`）から求めます。

```hlsl
float2 ReceiverPlaneDepthBias(float3 uvz_ddx, float3 uvz_ddy) {
  float2 bias;
  bias.x = uvz_ddy.y * uvz_ddx.z - uvz_ddx.y * uvz_ddy.z;
  bias.y = uvz_ddx.x * uvz_ddy.z - uvz_ddy.x * uvz_ddx.z;
  float det = uvz_ddx.x * uvz_ddy.y - uvz_ddx.y * uvz_ddy.x;
  return bias / det;
}
```

関数の引数と戻り値です。`uvz_ddx`・`uvz_ddy` は光の座標 (u, v, z) の、画面上の x 方向・y 方向の微分です。戻り値は (dz/du, dz/dv) で、uv が 1 だけ動いたときの、面の深度の変化です。

サンプル点が中心から (du, dv) ずれているときの補正した深度は、次のとおりです。

<div class="formula">z′ = z + dot( (dz/du, dz/dv), (du, dv) )</div>

```hlsl
float depth = center_depth;
float2 receiver_bias = ReceiverPlaneDepthBias(ddx(uvz), ddy(uvz));
for (each sample offset) {
  float sample_depth = depth + dot(receiver_bias, offset_uv);
  shadow += shadow_tex.SampleCmpLevelZero(shadow_sampler, uv + offset_uv, sample_depth - bias);
}
```

受け手平面バイアスの利点は PCF の広いカーネルでもアクネが出にくいこと、サンプルごとに面に沿った補正ができること、傾いた面でも浮かせずに済むことです。欠点は微分の精度が悪い所（深度の不連続）でバイアスが暴れること、計算が増えること微分を使うのでブランチ内で使えないなどシェーダー上の制約があることです。

原典は Isidoro の "Shadow Mapping: GPU-based Tips and Techniques"（GDC 2006）です。PCF では中心の画素の深度勾配から、サンプル位置ごとの本来の深度を外挿して比べることで、広いカーネルでも自己影を避けます。

## PCF とバイアスの問題

<strong>PCF</strong>（[PCF](../pcf.md)）は 1 つの画素をシャドウ マップの複数の画素（3×3、5×5 など）で比較して縁をなめらかにします。ところが、面が斜めのとき PCF で読む、周囲の画素は画素の位置と深度が異なる点を指しています。

```text
 光
 ↓       ↓       ↓        ← PCF が、読む、隣の画素（x−1, x, x+1）
 ─────────╲───────────╲──   斜めの面
          ↘ 深度が、画素ごとに、違う
```

中心の画素の深度で 隣の画素の、シャドウ マップ値を比べると面が斜めなので隣の画素の実際の深度は中心と、異なります。比較が常に「中心の深度」だと隣の本来、光が当たる点が影と判定され自己影（縞）が出ます。

## レシーバー平面バイアス

<strong>レシーバー平面深度バイアス</strong>（Receiver Plane Depth Bias、Isidoro、2006）は 画素の周りの面を平面とみなし、PCF で読む各サンプル位置での、平面の深度を計算してその深度で、比べます。1 つの深度ではなく位置ごとの深度を使うので面が斜めでも各サンプルで、正しい比較になります。

### 平面の深度の求め方

画素のシャドウ座標 `(u, v, z)` の 画面空間の、微分（`ddx`、`ddy`）から `z` が `u`、`v` に対してどう変わるか（深度の勾配）を求めます。

```text
dz/du、dz/dv を求める:
  [ ∂u/∂x  ∂v/∂x ] [dz/du]   [ ∂z/∂x ]
  [ ∂u/∂y  ∂v/∂y ] [dz/dv] = [ ∂z/∂y ]
```

2×2 の連立方程式を 逆行列で、解きます。

```hlsl
// シャドウ座標 (u, v, z) の、画面の微分から、深度の勾配 (dz/du, dz/dv) を求める。
float2 ReceiverPlaneDepthBias(float3 shadow_coord_ddx, float3 shadow_coord_ddy) {
  float2 bias_uv;
  // 2×2 の逆行列（行列式で割る）
  bias_uv.x = shadow_coord_ddy.y * shadow_coord_ddx.z - shadow_coord_ddx.y * shadow_coord_ddy.z;
  bias_uv.y = shadow_coord_ddx.x * shadow_coord_ddy.z - shadow_coord_ddy.x * shadow_coord_ddx.z;
  float det = shadow_coord_ddx.x * shadow_coord_ddy.y - shadow_coord_ddx.y * shadow_coord_ddy.x;
  bias_uv /= max(abs(det), 1e-6) * sign(det);
  return bias_uv;                       // x = dz/du、y = dz/dv
}
```

### PCF の各サンプルで、平面の深度を使う

```hlsl
float ShadowPCFReceiverPlane(float3 coord) {
  // ① 深度の勾配を求める（画面の微分から）
  float2 dz_duv = ReceiverPlaneDepthBias(ddx(coord), ddy(coord));

  // ② PCF の、各サンプル位置で、平面の深度を使って、比べる
  float sum = 0.0;
  const int kRadius = 2;                                         // 5×5
  [unroll] for (int y = -kRadius; y <= kRadius; ++y) {
    [unroll] for (int x = -kRadius; x <= kRadius; ++x) {
      float2 offset = float2(x, y) * g_shadow_texel_size;         // シャドウ マップ上の、ずれ（UV）
      float z_at_sample = coord.z + dot(dz_duv, offset);          // 平面に沿った、そのサンプルでの深度
      sum += g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, coord.xy + offset, z_at_sample - kSmallBias);
    }
  }
  return sum / float((2 * kRadius + 1) * (2 * kRadius + 1));
}
```

| 要素 | 内容 |
| --- | --- |
| `dz_duv` | 面の傾きに沿った、深度の変化（UV 方向に 1 だけ動いたとき） |
| `z_at_sample` | サンプル位置での、平面の深度 = 中心の深度 + 勾配 × ずれ |
| `kSmallBias` | ごく小さな定数バイアス（量子化誤差の、補正用） |

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | PCF を広く取っても、斜めの面で自己影が出ない。バイアスを小さく保てる |
| 長所 | ピーター パンニングが少ない（バイアスを大きく取らなくて、よい） |
| 長所 | カスケードごとの調整が少ない（平面に沿うので解像度に依存しにくい） |
| 短所 | 画面の微分（`ddx`、`ddy`）に依存する。分岐の中や画素の端で不安定になる |
| 短所 | 平面を仮定する。曲面、角では平面の仮定が崩れずれる |
| 短所 | 微分が極端な値（光と、ほぼ平行な面）になり数値が暴走する。クランプが必要 |
| 短所 | 計算がやや多い（微分と、逆行列） |

### 暴走を防ぐ

```hlsl
// 勾配が極端に大きくならないよう、上限をかける。
dz_duv = clamp(dz_duv, -kMaxSlope, kMaxSlope);
```

また、<strong>画面の微分</strong>は 2×2 のクアッド（隣り合う 4 画素）で、計算されるのでクアッドの画素が別の面にまたがる（物の縁）と微分が乱れます。縁ではこの方式の効果が弱まります。

## 他の方式との使い分け

| 状況 | 方式 |
| --- | --- |
| 2×2 PCF（比較サンプラー、ハードウェア） | 傾き依存バイアス（[Slope-Scale Bias](slope-scale-bias.md)）で、十分 |
| 3×3〜5×5 PCF（ソフトな縁） | レシーバー平面バイアスが効く |
| PCSS（広い範囲で読む） | レシーバー平面バイアスがほぼ、必須（[PCSS](../pcss.md)） |
| VSM / ESM（フィルタ可能な、シャドウ マップ） | 別の、問題（光漏れ）。この方式は使わない |

## よくあるミス

??? failure "平らな面の端で、勾配が壊れて影がおかしい"
    <strong>勾配に上限を設ける</strong>。ポリゴンの縁に注意。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 面の傾きから、周りのサンプルの深度を補正
    - [x] 広い PCF でアクネを防ぐ

## 参考

- Isidoro, "Shadow Mapping: GPU-based Tips and Techniques", Game Developers Conference 2006（レシーバー平面の深度バイアスなど）
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"（Direct3D 11 のドキュメント。バイアス、平行光源、PCF）
- Fernando, "Percentage-Closer Soft Shadows", SIGGRAPH 2005 Sketches

## 関連ページ

- [Shadow Bias](index.md)
- [Normal Offset](normal-offset.md)
- [PCF](../pcf.md)
