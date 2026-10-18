---
title: Receiver Plane Bias
tags:
  - 描画
---

# Receiver Plane Bias

**PCF のように、1 点でなく周りの複数点を調べるとき**、**中心の点に合わせたバイアスでは、周りの点（別の高さにある）で、アクネ**が出ます。**受け手の面の傾きから、周りの点それぞれの正しい深度を計算する**のが**受け手平面バイアス（Receiver Plane Depth Bias）**です。**PCF の広いカーネルでも、アクネが出にくい**ので、**高品質な影で使われます**。このページでは、**問題の理由・平面の式・実装**を説明します。

!!! tip "ポイント"
    - **PCF の周辺サンプルは、中心とは別の深度にある**ので、**中心のバイアスでは合わない**。
    - **受け手平面バイアス ＝ 面の傾き（深度の勾配）から、サンプルごとの深度を補正**する。
    - **画面空間の微分（`ddx`・`ddy`）**から、**光の空間での勾配**を求める。
    - **広い PCF・PCSS で効果が大きい**。

## Fix 4: Receiver Plane Depth Bias {#対策-4受け手平面バイアスreceiver-plane-depth-bias}
**PCF**（複数点のサンプル）と組み合わせると**周りのサンプル点**の深度を、**中心の点と同じ面の上にあるもの**として**補正**する必要があります。**面の傾き**から、**サンプルごとに深度を補正**します。

**シャドウ マップの座標 (u, v) が動いたときの面の深度の変化**（`dz/du`、`dz/dv`）を、**画面上の微分**（`ddx`・`ddy`）から求めます。

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

**サンプル点が中心から (du, dv) ずれているとき**の**補正した深度**は、次のとおりです。

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

## Common Mistakes {#よくあるミス}

??? failure "平らな面の端で、勾配が壊れて、影がおかしい"
    **勾配に上限を設ける**。**ポリゴンの縁**に注意。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **面の傾きから、周りのサンプルの深度を補正**
    - [x] **広い PCF でアクネを防ぐ**

## References {#参考}

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## Related Pages {#関連ページ}

- [Shadow Bias](index.md)
- [Normal Offset](normal-offset.md)
- [PCF](../pcf.md)
