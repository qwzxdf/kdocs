---
title: Wakes and Collisions
tags:
  - 描画
---

# Wakes and Collisions

**船の後ろや、物が水に当たった所には、泡の筋（航跡）ができます**。**物の位置を、泡のバッファに書き込む**ことで、**表現**できます。このページでは、**航跡と衝突の泡**を説明します。

!!! tip "ポイント"
    - **物が通った位置に、泡を書き込む**。
    - **書き込みは、バッファを描く（スプラット）**。
    - **履歴で、ゆっくり消える**。
    - **速さに応じて、強さを変える**。

## 航跡と衝突
**船や泳ぐキャラクターの後ろ**には**泡の筋**が**残ります**。

航跡の作り方は 3 つです。ブラシで泡の履歴に描く方法は、物の位置に丸い点を描き込みます（[Water Interaction](../interaction/index.md)）。パーティクルでしぶきを出す方法もあります。水中の物の深度を使う方法は、岸辺と同じ深度差で、杭の周りに自動で輪を出します。

## よくあるミス

??? failure "船が通っても、泡の筋が出ない"
    **物の位置を、泡のバッファに書き込む**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **通った所に書き込んで、ゆっくり消す**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Shore Foam](index.md)
- [Water Interaction](../interaction/index.md)
