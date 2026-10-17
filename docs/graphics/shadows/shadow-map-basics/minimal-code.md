---
title: 最小のコード
tags:
  - 描画
---

# 最小のコード

**ここまでの手順を、最小のコードでつなげて見ます**。**1 本の平行光（太陽）**に対する**シャドウ マップの全体の流れ**です。**実際の製品では、バイアス・フィルタ・カスケードを足します**。このページでは、**全体のコードの流れ**を示します。

!!! tip "ポイント"
    - **全体 ＝ 光の行列 → 深度パス → 比較（ライティング）**。
    - **最小版は、バイアス・フィルタなし**。**これに、バイアスと PCF を足して実用に**。

## 全体のコード（最小）
```hlsl
Texture2D<float> shadow_tex : register(t5);
SamplerComparisonState shadow_sampler : register(s5);

cbuffer ShadowConstant : register(b3) {
  row_major float4x4 light_view_projection;
  float shadow_bias;
}

float3 Shade(float3 world_pos, float3 N, float3 L, float3 albedo, float3 light_color) {
  float shadow = ShadowFactor(world_pos);
  return albedo * light_color * saturate(dot(N, L)) * shadow;
}
```

## よくあるミス

??? failure "最小のコードのまま製品に使って、アクネ・ジャギーが出る"
    **バイアス（[バイアス](../bias/index.md)）とフィルタ（[PCF](../pcf.md)）を足す**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **最小のコードで、全体の流れを確認**
    - [x] **実用にはバイアスとフィルタが必須**

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [シャドウ マップの基礎](index.md)
- [バイアス](../bias/index.md)
- [PCF](../pcf.md)
