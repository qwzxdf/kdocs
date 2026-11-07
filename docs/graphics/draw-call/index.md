---
title: Draw Call
tags:
  - 描画
  - 最適化
---

# Draw Call

描画の命令を GPU に渡すまでの話。物が 1 万個あっても、GPU は命令がなければ何もしません。命令を作るのは CPU で、ドロー コールごとにドライバが時間を使うので、物の数が増えると、GPU が遊んでいるのに CPU が追いつかない、という状態になります。このセクションは、**何を描くかを決め、どう命令にして渡すか**を扱います。見えない物を捨てる（カリング）、遠くの物の詳細度を下げる（LOD）、命令をまとめる（バッチ・インスタンシング）、判断と命令づくりを GPU に任せる（GPU Driven、Mesh Shader）です。

GPU の中での負荷（帯域、オーバードロー、シェーダー）は、[Optimization](../optimization/index.md)で扱います。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Rendering Pipeline Overview](overview.md) | CPU から画面までの流れと、基本用語 |
| [Draw Calls and Batching](draw-calls.md) | CPU 側の負担、バッチ・インスタンシング・ステートの整理 |
| [Culling](culling.md) | 視錐台・オクルージョン・距離。見えないものを描かない |
| [LOD and Impostors](lod.md) | 遠くの物の詳細度を下げる |
| [GPU Driven Rendering](gpu-driven.md) | カリングと描画命令を GPU が作る |
| [GPU Driven (D3D12)](gpu-driven-dx12/index.md) | D3D12 で組む GPU Driven |
| [Mesh Shader and Meshlet](mesh-shaders.md) | 三角形の塊単位の細かいカリング |
| [2D Rendering](2d.md) | スプライト・タイルマップ・UI |

## 関連ページ

- [Lighting](../lighting/index.md)
- [Optimization](../optimization/index.md)
- [深度とカリング](../../3d/depth-culling.md)
- [メッシュとテクスチャ](../../3d/mesh-textures.md)
