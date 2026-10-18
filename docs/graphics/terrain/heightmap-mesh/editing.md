---
title: Editing Heightmaps
tags:
  - 描画
---

# Editing Heightmaps

**地形を作るには、高さマップを、ブラシで盛ったり削ったりして、編集します**。このページでは、**編集の方法と保存**を説明します。

!!! tip "ポイント"
    - **ブラシで高さを上げ下げ・平らにならす**。
    - **編集した範囲だけ、メッシュ・法線を更新**する。
    - **高さマップは、16bit で保存**。
    - **元に戻せる（アンドゥ）ように、差分を記録**する。

## 高さマップの編集
高さマップの編集です。ブラシで盛る・削るは、丸いブラシを加算・減算します。平らにする・均すは、平均を取って段差をならします。ステップ（段丘）は、高さを丸めて段々にします。道や建物の整地は、指定範囲を一定の高さに合わせます（スプライン沿いに整地）。ランタイムの変形は、爆発で穴が開くなどの場合で、高さマップを書き換え、法線と当たり判定も更新します。

## よくあるミス

??? failure "編集のたびに、全体を再生成して遅い"
    **編集した範囲だけ更新**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **範囲だけ更新して、軽く編集**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Heightmaps and Meshes](index.md)
- [地形生成](../generation/index.md)
