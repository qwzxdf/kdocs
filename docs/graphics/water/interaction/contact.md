---
title: Writing Object Contacts
tags:
  - 描画
---

# Writing Object Contacts

**物が水に触れた所を、高さマップに「押し込み」として書き込む**と、**そこから波紋が広がります**。このページでは、**接触の書き込み方**を説明します。

!!! tip "ポイント"
    - **物の位置・大きさを、高さマップにスタンプ**する。
    - **動く速さに応じて、強さを変える**。
    - **水面の高さと比べて、水に入った部分だけ書く**。
    - **書き込みは、シミュレーション用のテクスチャへ**。

## 物の接触を書き込む
**物が水に触れた所に高さを書き込むと**、**そこが波の起点になります**。

| 方法 | 内容 |
| --- | --- |
| <strong>ブラシ（点）</strong> | **位置に丸い凹みを描き込む**（**キャラクターの足・落ちた物**） |
| **移動する物** | **毎フレーム、動いた位置に描く**（**航跡**）。**速さに比例して強く** |
| **水中の物の深度** | **物を上から描いて**、**水面と交わる部分を書き込む** |
| **雨粒** | **ランダムな位置に小さな点**を**描く** |

```hlsl
float2 uv = (world_position.xz - sim_origin) / sim_size;
float distance_to_brush = length(pixel_uv - brush_uv);
float brush = saturate(1.0 - distance_to_brush / brush_radius);
brush = brush * brush * (3.0 - 2.0 * brush);
height_next[p] += brush * brush_strength;
```

| 点 | 説明 |
| --- | --- |
| **滑らかな減衰** | **`smoothstep` 風**にして、**縁を尖らせない** |
| **強さ** | **負なら凹む**（**物が沈む**）、**正なら盛り上がる** |
| **加算** | **既にある波に足す** |

## よくあるミス

??? failure "物が水に入っても、波紋が出ない"
    **接触位置を、高さマップに書き込む**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **接触を、高さマップに書く**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Water Interaction](index.md)
- [高さマップの反映](apply-height.md)
