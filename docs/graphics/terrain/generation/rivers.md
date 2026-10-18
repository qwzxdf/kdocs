---
title: Rivers and Lakes
tags:
  - 描画
---

# Rivers and Lakes

**川は、高い所から低い所へ流れ、谷に沿います**。**侵食の結果から、流れの量を求めて、川を決められます**。このページでは、**川と湖の生成**を説明します。

!!! tip "ポイント"
    - **流れの量（フロー アキュムレーション）を計算**する。
    - **流量が多い所を、川にする**。
    - **くぼ地に水がたまり、湖になる**。
    - **川の水面は、[Water](../../water/index.md)で描く**。

## 川と湖
**侵食の結果から、川を取り出せます**。

| 方法 | 内容 |
| --- | --- |
| **流量マップ** | **各セルについて、上流から集まる水量を数える**（**高い所から低い所へ累積**）。**水量が多い所が川** |
| **スプライン化** | **川の経路を折れ線／スプラインに抽出**し、**水面メッシュを沿わせる** |
| **窪地の処理** | **行き止まり（窪み）は、湖にするか、堤を越えて流す** |
| **幅と深さ** | **水量に比例**して**川幅を広げる** |

**川の水面**は、[Water](../../water/index.md)の**フローマップ**（[水面のインタラクション](../../water/interaction/index.md)）で**流れを表現**します。

## よくあるミス

??? failure "川が、坂を登っている"
    **水面の高さを、下流ほど低く**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **流量から川を、くぼ地から湖を決める**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain Generation](index.md)
- [Erosion](erosion.md)
- [Water](../../water/index.md)
