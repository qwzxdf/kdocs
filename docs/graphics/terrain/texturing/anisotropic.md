---
title: 異方性フィルタリング
tags:
  - 描画
---

# 異方性フィルタリング

**地面を斜めから見ると、遠くのテクスチャがぼやけます**。**異方性フィルタリングは、縦と横で別々にフィルタして、ぼけを防ぎます**。このページでは、**異方性フィルタの効果**を説明します。

!!! tip "ポイント"
    - **斜めの面で、ぼけを防ぐ**。
    - **サンプル数（2x〜16x）で、品質とコストが変わる**。
    - **地形では、ほぼ必須**。
    - **設定で ON にするだけ**。

## 異方性フィルタリング
**斜めから見る地面**は、**テクスチャが縦に潰れる**ので、**ぼやけます**。<strong>異方性フィルタリング（16x など）</strong>を**有効**にすると**遠くの地面もくっきり**します。**地形ではほぼ必須**です。

## よくあるミス

??? failure "遠くの地面が、ぼやけている"
    **異方性フィルタリング（8x〜16x）**を有効にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **斜めの面のぼけを防ぐ**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [地形のテクスチャ](index.md)
- [テクスチャ フィルタ](../../../3d/mesh-textures.md)
