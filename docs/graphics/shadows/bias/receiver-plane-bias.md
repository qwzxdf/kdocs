---
title: Receiver Plane Bias
tags:
  - 描画
---

# Receiver Plane Bias

<strong>PCF のように、1 点でなく周りの複数点を調べるとき</strong>、<strong>中心の点に合わせたバイアスでは、周りの点（別の高さにある）で、アクネ</strong>が出ます。受け手の面の傾きから、周りの点それぞれの正しい深度を計算するのが受け手平面バイアス（Receiver Plane Depth Bias）です。PCF の広いカーネルでも、アクネが出にくいので、高品質な影で使われます。このページでは、問題の理由・平面の式・実装を説明します。

!!! tip "ポイント"
    - PCF の周辺サンプルは、中心とは別の深度にあるので、中心のバイアスでは合わない。
    - 受け手平面バイアス ＝ 面の傾き（深度の勾配）から、サンプルごとの深度を補正する。
    - 画面空間の微分（`ddx`・`ddy`）から、光の空間での勾配を求める。
    - 広い PCF・PCSS で効果が大きい。

## 対策 4：受け手平面バイアス（Receiver Plane Depth Bias）
<strong>PCF</strong>（複数点のサンプル）と組み合わせると<strong>周りのサンプル点</strong>の深度を、中心の点と同じ面の上にあるものとして補正する必要があります。面の傾きから、サンプルごとに深度を補正します。

<strong>シャドウ マップの座標 (u, v) が動いたときの面の深度の変化</strong>（`dz/du`、`dz/dv`）を、<strong>画面上の微分</strong>（`ddx`・`ddy`）から求めます。

```hlsl
float2 ReceiverPlaneDepthBias(float3 uvz_ddx, float3 uvz_ddy) {
  float2 bias;
  bias.x = uvz_ddy.y * uvz_ddx.z - uvz_ddx.y * uvz_ddy.z;
  bias.y = uvz_ddx.x * uvz_ddy.z - uvz_ddy.x * uvz_ddx.z;
  float det = uvz_ddx.x * uvz_ddy.y - uvz_ddx.y * uvz_ddy.x;
  return bias / det;
}
```

関数の引数と戻り値です。`uvz_ddx`・`uvz_ddy` は、光の座標 (u, v, z) の、画面上の x 方向・y 方向の微分です。戻り値は (dz/du, dz/dv) で、uv が 1 だけ動いたときの、面の深度の変化です。

<strong>サンプル点が中心から (du, dv) ずれているとき</strong>の<strong>補正した深度</strong>は、次のとおりです。

<div class="formula">z′ = z + dot( (dz/du, dz/dv), (du, dv) )</div>

```hlsl
float depth = center_depth;
float2 receiver_bias = ReceiverPlaneDepthBias(ddx(uvz), ddy(uvz));
for (each sample offset) {
  float sample_depth = depth + dot(receiver_bias, offset_uv);
  shadow += shadow_tex.SampleCmpLevelZero(shadow_sampler, uv + offset_uv, sample_depth - bias);
}
```

受け手平面バイアスの利点は、PCF の広いカーネルでもアクネが出にくいこと、サンプルごとに面に沿った補正ができること、傾いた面でも浮かせずに済むことです。欠点は、微分の精度が悪い所（深度の不連続）でバイアスが暴れること、計算が増えること、微分を使うのでブランチ内で使えないなどシェーダー上の制約があることです。

原典は、Isidoro の "Shadow Mapping: GPU-based Tips and Techniques"（GDC 2006）です。PCF では、中心の画素の深度勾配から、サンプル位置ごとの本来の深度を外挿して比べることで、広いカーネルでも自己影を避けます。

## PCF と、バイアスの、問題

<strong>PCF</strong>（[PCF](../pcf.md)）は、<strong>1 つの画素</strong>を、シャドウ マップの、複数の画素（3×3、5×5 など）で、比較して、縁を、なめらかにします。ところが、面が、斜めのとき、PCF で読む、周囲の画素は、画素の位置と、深度が、異なる点を、指しています。

```text
 光
 ↓       ↓       ↓        ← PCF が、読む、隣の画素（x−1, x, x+1）
 ─────────╲───────────╲──   斜めの面
          ↘ 深度が、画素ごとに、違う
```

<strong>中心の画素の、深度</strong>で、<strong>隣の画素の、シャドウ マップ値</strong>を、比べると、面が、斜めなので、隣の画素の、実際の深度は、中心と、異なります。比較が、常に、「中心の深度」だと、隣の、本来、光が当たる点が、影と判定され、自己影（縞）が、出ます。

## レシーバー平面バイアス

<strong>レシーバー平面深度バイアス</strong>（Receiver Plane Depth Bias、Isidoro、2006）は、<strong>画素の周りの、面を、平面とみなし</strong>、PCF で読む、各サンプル位置での、平面の深度を、計算して、その深度で、比べます。1 つの深度ではなく、位置ごとの、深度を、使うので、面が、斜めでも、各サンプルで、正しい比較になります。

### 平面の、深度の、求め方

画素の、シャドウ座標 `(u, v, z)` の、<strong>画面空間の、微分</strong>（`ddx`、`ddy`）から、<strong>`z` が、`u`、`v` に対して、どう変わるか</strong>（深度の勾配）を、求めます。

```text
dz/du、dz/dv を求める:
  [ ∂u/∂x  ∂v/∂x ] [dz/du]   [ ∂z/∂x ]
  [ ∂u/∂y  ∂v/∂y ] [dz/dv] = [ ∂z/∂y ]
```

2×2 の、連立方程式を、<strong>逆行列</strong>で、解きます。

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

### PCF の、各サンプルで、平面の深度を、使う

```hlsl
float ShadowPCFReceiverPlane(float3 coord) {
  // ① 深度の勾配を、求める（画面の微分から）
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
| `dz_duv` | 面の傾きに、沿った、深度の変化（UV 方向に、1 だけ動いたとき） |
| `z_at_sample` | サンプル位置での、平面の深度 = 中心の深度 + 勾配 × ずれ |
| `kSmallBias` | ごく小さな定数バイアス（量子化誤差の、補正用） |

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | PCF を、広く取っても、斜めの面で、自己影が、出ない。バイアスを、小さく保てる |
| 長所 | ピーター パンニングが、少ない（バイアスを、大きく取らなくて、よい） |
| 長所 | カスケードごとの、調整が、少ない（平面に、沿うので、解像度に、依存しにくい） |
| 短所 | 画面の微分（`ddx`、`ddy`）に、依存する。分岐の中や、画素の、端で、不安定になる |
| 短所 | 平面を、仮定する。曲面、角では、平面の仮定が、崩れ、ずれる |
| 短所 | 微分が、極端な値（光と、ほぼ平行な面）になり、数値が、暴走する。クランプが、必要 |
| 短所 | 計算が、やや多い（微分と、逆行列） |

### 暴走を、防ぐ

```hlsl
// 勾配が、極端に大きくならないよう、上限をかける。
dz_duv = clamp(dz_duv, -kMaxSlope, kMaxSlope);
```

また、<strong>画面の微分</strong>は、<strong>2×2 のクアッド</strong>（隣り合う 4 画素）で、計算されるので、クアッドの、画素が、別の面に、またがる（物の、縁）と、微分が、乱れます。縁では、この方式の、効果が、弱まります。

## 他の方式との、使い分け

| 状況 | 方式 |
| --- | --- |
| 2×2 PCF（比較サンプラー、ハードウェア） | 傾き依存バイアス（[Slope-Scale Bias](slope-scale-bias.md)）で、十分 |
| 3×3〜5×5 PCF（ソフトな縁） | レシーバー平面バイアスが、効く |
| PCSS（広い範囲で、読む） | レシーバー平面バイアスが、ほぼ、必須（[PCSS](../pcss.md)） |
| VSM / ESM（フィルタ可能な、シャドウ マップ） | 別の、問題（光漏れ）。この方式は、使わない |

## よくあるミス

??? failure "平らな面の端で、勾配が壊れて、影がおかしい"
    <strong>勾配に上限を設ける</strong>。<strong>ポリゴンの縁</strong>に注意。

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
