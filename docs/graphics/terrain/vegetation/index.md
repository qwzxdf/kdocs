---
title: 植生
tags:
  - 描画
---

# 植生

**草や木は、数が非常に多く、地形の見た目を大きく左右します**。**インスタンシングとカリングで数を扱い、風やライティングで生きた見た目にします**。このセクションでは、**配置・インスタンシング・カリング・草の形・風・踏まれる草・木・半透明の問題・ライティング**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **数が多い ＝ インスタンシングとカリングが必須**。
    - **草は、板ポリを交差させて作る**。
    - **風でなびかせると、生きた見た目**。
    - **半透明の葉は、ソートできないので、アルファ テスト系**。

## 配置
**植生の位置**は**何を元に決めるか**です。

| 方法 | 内容 |
| --- | --- |
| **手で置く** | **エディタで 1 本ずつ**。**主役の木・目立つ物** |
| **ブラシで散布** | **範囲に密度を指定してランダムに配置**（**保存は位置のリスト**） |
| **ルールで自動** | **地形の高さ・傾き・スプラット マップ・ノイズ**から**決定的に生成** |
| **GPU 生成** | **カメラ周りのセルについて、コンピュートで毎フレーム生成**（**保存が不要**） |

**GPU 生成の草**は、**ワールドを小さなセル（例：1 m）に区切り**、**セルのハッシュから、乱数で位置・向き・大きさを決めます**。**同じセルは毎回同じ結果になる**ので、**保存が要りません**。

```hlsl
uint HashCell(int2 cell) {
  uint h = uint(cell.x) * 73856093u ^ uint(cell.y) * 19349663u;
  h ^= h >> 13;
  h *= 0x5bd1e995u;
  h ^= h >> 15;
  return h;
}

float Random01(inout uint state) {
  state = state * 1664525u + 1013904223u;
  return float(state >> 8) / 16777216.0;
}

[numthreads(8, 8, 1)]
void GenerateGrass(uint3 id : SV_DispatchThreadID) {
  int2 cell = camera_cell + int2(id.xy) - kHalfCells;
  uint state = HashCell(cell);

  float2 offset = float2(Random01(state), Random01(state));
  float2 xz = (float2(cell) + offset) * cell_size;
  float density = density_map.SampleLevel(linear_clamp, WorldToUV(xz), 0).r;
  if (Random01(state) > density) return;

  float height = SampleTerrainHeight(xz);
  float rotation = Random01(state) * 6.2831853;
  float scale = lerp(0.7, 1.3, Random01(state));
  AppendInstance(float3(xz.x, height, xz.y), rotation, scale);
}
```

| 点 | 説明 |
| --- | --- |
| **セルのハッシュ** | **同じセルは毎フレーム同じ位置**（**揺れない・点滅しない**） |
| **密度マップ** | **スプラット マップの「草」の重み**などで**草が生える所だけ** |
| **カメラ周りのセルだけ** | **遠くのセルは生成しない** |
| **`AppendInstance`** | **`AppendStructuredBuffer`**に書く。**後で `DrawIndexedInstancedIndirect`** |

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [インスタンシング](instancing.md) | 同じメッシュを大量に描く |
| [カリング](culling.md) | 見えない物を描かない |
| [草の形](grass-shape.md) | 板ポリ・メッシュ |
| [風](wind.md) | なびく動き |
| [踏まれる草](trample.md) | キャラクターで倒れる草 |
| [木](trees.md) | 木の LOD・ビルボード |
| [半透明の問題](translucency.md) | 葉の描画の問題 |
| [ライティング](lighting.md) | 葉の光の扱い |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **数は、インスタンシングとカリングで扱う**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [地形](../index.md)
- [アルファ テスト](../../translucency/alpha-test/index.md)
- [カリング](../../../rendering/culling.md)
