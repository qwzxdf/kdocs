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

接触を書き込む方法は 4 つです。ブラシ（点）は、位置に丸い凹みを描き込む方法で、キャラクターの足や落ちた物に使います。移動する物は、毎フレーム動いた位置に描き（航跡）、速さに比例して強くします。水中の物の深度を使う方法は、物を上から描いて、水面と交わる部分を書き込みます。雨粒は、ランダムな位置に小さな点を描きます。

```hlsl
float2 uv = (world_position.xz - sim_origin) / sim_size;
float distance_to_brush = length(pixel_uv - brush_uv);
float brush = saturate(1.0 - distance_to_brush / brush_radius);
brush = brush * brush * (3.0 - 2.0 * brush);
height_next[p] += brush * brush_strength;
```

コードの要点です。滑らかな減衰は `smoothstep` 風にして、縁を尖らせません。強さは、負なら凹み（物が沈む）、正なら盛り上がりです。既にある波に足します（加算）。

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
