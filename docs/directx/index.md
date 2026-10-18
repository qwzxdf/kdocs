---
title: DirectX
tags:
  - DirectX
---

# DirectX

<strong>DirectX</strong>は、Windows で、GPU を使って、3D を描く、API の、集まりです。このセクションは、<strong>DirectX 11 と DirectX 12 を、それぞれ、独立した、系列</strong>として、ウィンドウを、開くところから、三角形、テクスチャ、深度、計算シェーダーまで、<strong>自分のコードで、動かしながら</strong>、説明します。描画セクション（影、AO、反射、大気、水…）の、コードを、動かす、ための、土台です。

## どちらから、読むか

| あなたは | 読む |
| --- | --- |
| DirectX が、初めて | [DirectX 11 Guide](dx11/index.md)（概念を、先に、理解しやすい。このサイトの描画コードは、DX11 前提） |
| レイトレーシング、メッシュ シェーダー、GPU ドリブンを、使いたい | [DirectX 12 Guide](dx12/index.md) |
| DX11 を、知っていて、DX12 に、移る | [DX11 と DX12 の対応表](compare.md) |
| API を、選ぶ前に、考え方を、知りたい | [DirectX Concepts](concepts/index.md) |

## セクションの、構成

| 系列 | 内容 | 特徴 |
| --- | --- | --- |
| [概念](concepts/index.md) | GPU パイプライン、リソースとビュー、フォーマット、座標系の規約、同期 | API に、依存しない。コードは、ほぼ無し |
| [DirectX 11](dx11/index.md) | デバイス、スワップ チェーン、シェーダー、バッファ、テクスチャ、ステート、MRT、計算シェーダー | ドライバーが、面倒を、見る。コードが、少ない |
| [DirectX 12](dx12/index.md) | デバイス、コマンド キュー、リスト、フェンス、ディスクリプタ、バリア、PSO、DXR | 自分で、管理する。コードが、多く、高性能 |
| [DX11 と DX12 の、対応表](compare.md) | 同じことを、2 つの API で、どう書くか | 移行する人向け |

DX11 と DX12 は、<strong>互いに、前提にしません</strong>。それぞれ、ウィンドウから、最後まで、読み通せます。

## 用語について

DirectX の、用語（デバイス、ビュー、ステート、ディスクリプタ、PSO、フェンスなど）は、1 つずつ、<strong>専用のページ</strong>を、持っています。文章の中の、最初の 1 回は、そのページへの、リンクになります。

## 描画セクションとの、つながり

描画セクションの、各ページの、「DirectX 11 で組む」の節は、このセクションの、DX11 の、ページを、使って、組み立てます。

| 描画のページ | 使う、DX11 のページ |
| --- | --- |
| 影・AO・反射・ポスト プロセス（フルスクリーンの、パス） | [Drawing a Triangle](dx11/triangle.md)、[D3D11 Pass Recipes](dx11/pass-recipes.md) |
| G バッファ、ディファード | [Multiple Render Targets](dx11/mrt.md) |
| 計算シェーダーを、使う、手法（ぼかし、froxel、FFT） | [Compute Shader](dx11/compute-shader.md)、[Unordered Access View (UAV)](dx11/uav.md) |
| レイトレーシング（RTAO、反射、DDGI） | [DXR Host Setup](dx12/dxr-host.md)（DirectX 12） |
| GPU ドリブン | [GPU Driven（D3D12 詳細）](../rendering/gpu-driven-dx12/index.md) |

## 関連ページ

- [DirectXMath](../gamemath/directxmath.md)
- [描画の流れ（入門）](../3d/render-flow/index.md)
- [描画](../graphics/index.md)
- [描画最適化](../rendering/index.md)
