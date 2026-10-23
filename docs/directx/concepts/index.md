---
title: DirectX Concepts
tags:
  - DirectX
---

# DirectX Concepts

DirectX 11 と DirectX 12 は、書き方が大きく違いますが <strong>同じ GPU を同じパイプラインで動かしている</strong>、という点は同じです。このセクションは <strong>API に依存しない考え方だけ</strong>をまとめます。コードはほとんど出てきません。DirectX 11 でも DirectX 12 でも先にここを読んでおくと各ページの用語がすっと、入ります。

## このセクションの読み方

| ページ | 内容 |
| --- | --- |
| [GPU Pipeline Overview](gpu-pipeline.md) | GPU が、頂点からピクセルの色を作るまでの流れ。各段の役割 |
| [Resources and Views](resources-views.md) | リソース（バッファ・テクスチャ）と、ビュー（見方）の分離 |
| [Formats and Typeless](formats.md) | 画素の形式（`DXGI_FORMAT`）、sRGB とリニア、typeless |
| [Constant Buffer Packing](cbuffer-packing.md) | `cbuffer` の詰め方（16 バイトのレジスタ）。C++ の構造体との、ずれの原因と直し方 |
| [Coordinate Conventions](conventions.md) | このサイトの座標系、行列の規約、クリップ空間、uv の向き |
| [Why Synchronization](synchronization.md) | CPU と GPU が、非同期に動く理由と読み書きの衝突 |

## このあとに読むもの

| 目的 | ページ |
| --- | --- |
| DirectX 11 で、描きたい | [DirectX 11 Guide](../dx11/index.md) |
| DirectX 12 で、描きたい | [DirectX 12 Guide](../dx12/index.md) |
| 2 つの違いを知りたい | [DX11 と DX12 の対応表](../compare.md) |

## 関連ページ

- [DirectX 11 Guide](../dx11/index.md)
- [DirectX 12 Guide](../dx12/index.md)
- [描画の流れ（入門）](../../3d/render-flow/index.md)
