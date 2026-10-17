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

## 対策 4：受け手平面バイアス（Receiver Plane Depth Bias）
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

| 引数 | 意味 |
| --- | --- |
| **`uvz_ddx`・`uvz_ddy`** | 光の座標 (u, v, z) の、**画面上の x・y 方向の微分** |
| **戻り値** | <strong>(dz/du, dz/dv)</strong>。**uv が 1 だけ動いたときの、面の深度の変化** |

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

| 利点 | 欠点 |
| --- | --- |
| **PCF の広いカーネルでも、アクネが出にくい** | **微分の精度**が悪い所（深度の不連続）で、**バイアスが暴れる** |
| **サンプルごとに面に沿った補正** | **計算が増える** |
| 傾いた面でも**浮かせずに**済む | **微分を使う**ので**ブランチ内で使えない**など、シェーダーの制約 |

## よくあるミス

??? failure "平らな面の端で、勾配が壊れて、影がおかしい"
    **勾配に上限を設ける**。**ポリゴンの縁**に注意。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **面の傾きから、周りのサンプルの深度を補正**
    - [x] **広い PCF でアクネを防ぐ**

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [Shadow Bias](index.md)
- [Normal Offset](normal-offset.md)
- [PCF](../pcf.md)
