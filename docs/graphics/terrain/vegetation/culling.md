---
title: 植生のカリング
tags:
  - 描画
---

# 植生のカリング

**見えない草を描かない**ことが、**最大の最適化**です。**視錐台カリング・距離カリング・オクルージョン カリング**を**組み合わせます**。このページでは、**植生のカリング**を説明します。

!!! tip "ポイント"
    - **視錐台カリング：画面の外を除く**。
    - **距離カリング：遠くの草を消す（フェードで）**。
    - **区画ごとに行う**と、**効率的**。
    - **GPU カリングで、インスタンスごとに判定**。

## カリング
**画面に映らない・遠すぎる植生は、描きません**。

| 種類 | 内容 |
| --- | --- |
| **距離カリング** | **一定距離より遠い物は描かない**（**草は 50〜100 m 程度**）。**フェードで消す** |
| **視錐台カリング** | **視錐台の外を捨てる** |
| **オクルージョン カリング** | **山や建物の裏は捨てる**（**Hi-Z**） |
| **密度の距離減衰** | **遠いほど、間引く**（**一部の草だけ描き、残りを太くする**） |

**コンピュート シェーダーで全インスタンスを判定**し、**生き残ったものを別バッファに詰め**ます。

```hlsl
[numthreads(64, 1, 1)]
void CullInstances(uint3 id : SV_DispatchThreadID) {
  if (id.x >= instance_count) return;
  GrassInstance instance = all_instances[id.x];
  float distance_to_camera = distance(instance.position, camera_position);
  if (distance_to_camera > max_distance) return;
  if (!SphereInFrustum(instance.position, instance.scale * radius)) return;
  uint index;
  visible_count.InterlockedAdd(0, 1, index);
  visible_instances[index] = instance;
}
```

詳しい構成は、[GPU Driven](../../../rendering/index.md) と同じ考え方です。

## よくあるミス

??? failure "遠くの草が、急に消える"
    **距離でフェード**させる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **画面外・遠方・隠れた草を、描かない**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [植生](index.md)
- [インスタンシング](instancing.md)
