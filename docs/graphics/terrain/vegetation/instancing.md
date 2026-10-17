---
title: インスタンシング
tags:
  - 描画
---

# インスタンシング

**草は、同じメッシュを何十万個も描きます**。**インスタンシングは、1 回の描画命令で、同じメッシュを、位置を変えて、大量に描く**方法で、**描画命令の数を減らせます**。このページでは、**インスタンシング**を説明します。

!!! tip "ポイント"
    - **1 回の DrawIndexedInstanced で、大量に描く**。
    - **位置・向き・大きさは、インスタンス バッファに**。
    - **GPU 駆動なら、カリングも GPU で**行える。
    - **描画命令の数が、減る**。

## インスタンシング
**同じメッシュを位置・向き・大きさだけ変えて、大量に描く**のが**インスタンシング**です。

| 方式 | 内容 |
| --- | --- |
| **`DrawIndexedInstanced`** | **インスタンス数を指定**。**インスタンスごとのデータは、頂点バッファか StructuredBuffer** |
| **`DrawIndexedInstancedIndirect`** | **インスタンス数を GPU が決める**（**カリング結果をそのまま**）。**CPU 待ちが無い** |
| **インスタンス データ** | **位置（float3）・回転（1 つの角度）・スケール・色の個体差**など。**16〜32 バイト** |

```hlsl
struct GrassInstance {
  float3 position;
  float rotation;
  float scale;
  float color_variation;
  float2 padding;
};

StructuredBuffer<GrassInstance> instances : register(t0);

VSOutput VSMain(VSInput input, uint instance_id : SV_InstanceID) {
  GrassInstance instance = instances[instance_id];
  float s = sin(instance.rotation);
  float c = cos(instance.rotation);
  float3 local = input.position * instance.scale;
  float3 rotated = float3(local.x * c + local.z * s, local.y, -local.x * s + local.z * c);
  float3 world = rotated + instance.position;

  VSOutput output;
  output.position = mul(float4(world, 1), view_projection);
  output.color_variation = instance.color_variation;
  return output;
}
```

**1 つの描画命令にまとめる**ので、**CPU の負担が小さく**、**GPU も効率的**です。**メッシュ（ポリゴン数）が小さい**ほど、**インスタンシングの効果が大きい**です。

## よくあるミス

??? failure "草の描画命令が多すぎて、CPU が遅い"
    **インスタンシング**を使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **同じメッシュを、1 命令で大量に**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [植生](index.md)
- [カリング](culling.md)
