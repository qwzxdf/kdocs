---
title: Buoyancy and Reaction
tags:
  - 描画
---

# Buoyancy and Reaction

**物が水に浮くには、浮力が必要**で、**水の側も、物から押されて動きます**。このページでは、**浮力の計算と、水への反作用**を説明します。

!!! tip "ポイント"
    - **浮力 ＝ 水に沈んだ体積に比例した、上向きの力**。
    - **物体の数点で、水深を求めて、力を加える**。
    - **水の抵抗（ダンピング）で、揺れが収まる**。
    - **物が水を押す反作用は、高さマップに書く**。

## 浮力と水への反作用
**水面と物の相互作用は、見た目だけでなく、物理にも影響します**。

相互作用の物理の要素です。浮力は、水に浸かった体積に比例します（[Water Waves](../waves/index.md)）。抵抗は、水中を動く物が、速さに比例して減速する効果です。波紋の起点は、物理エンジンの接触や速度から、ブラシの強さを決めます。

## よくあるミス

??? failure "物が、水の上で跳ね続ける"
    **ダンピング**を**加える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **沈んだ体積に応じた力で浮かせる**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Water Interaction](index.md)
- [物を浮かせる](../waves/floating.md)
