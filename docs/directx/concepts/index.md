---
title: DirectX Concepts
tags:
  - DirectX
---

# DirectX Concepts

DirectX 11 と DirectX 12 は、書き方が、大きく違いますが、<strong>同じ GPU を、同じパイプラインで、動かしている</strong>、という点は、同じです。このセクションは、<strong>API に、依存しない、考え方だけ</strong>を、まとめます。コードは、ほとんど、出てきません。DirectX 11 でも、DirectX 12 でも、先に、ここを、読んでおくと、各ページの、用語が、すっと、入ります。

## このセクションの読み方

| ページ | 内容 |
| --- | --- |
| [GPU Pipeline Overview](gpu-pipeline.md) | GPU が、頂点から、ピクセルの色を、作るまでの、流れ。各段の、役割 |
| [Resources and Views](resources-views.md) | リソース（バッファ・テクスチャ）と、ビュー（見方）の、分離 |
| [Formats and Typeless](formats.md) | 画素の、形式（`DXGI_FORMAT`）、sRGB とリニア、typeless |
| [Coordinate Conventions](conventions.md) | このサイトの、座標系、行列の規約、クリップ空間、uv の向き |
| [Why Synchronization](synchronization.md) | CPU と GPU が、非同期に、動く理由と、読み書きの、衝突 |

## このあとに、読むもの

| 目的 | ページ |
| --- | --- |
| DirectX 11 で、描きたい | [DirectX 11 Guide](../dx11/index.md) |
| DirectX 12 で、描きたい | [DirectX 12 Guide](../dx12/index.md) |
| 2 つの、違いを、知りたい | [DX11 と DX12 の対応表](../compare.md) |

## 関連ページ

- [DirectX 11 Guide](../dx11/index.md)
- [DirectX 12 Guide](../dx12/index.md)
- [描画の流れ（入門）](../../3d/render-flow/index.md)
