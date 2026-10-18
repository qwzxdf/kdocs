---
title: DirectX
tags:
  - DirectX
---

# DirectX

<strong>DirectX</strong>は Windows で、GPU を使って 3D を描く、API の集まりです。このセクションは <strong>DirectX 11 と DirectX 12 をそれぞれ独立した系列</strong>として、ウィンドウを開くところから三角形、テクスチャ、深度、計算シェーダーまで <strong>自分のコードで、動かしながら</strong>、説明します。描画セクション（影、AO、反射、大気、水…）のコードを動かすための土台です。

## どちらから読むか

| あなたは | 読む |
| --- | --- |
| DirectX が初めて | [DirectX 11 Guide](dx11/index.md)（概念を先に、理解しやすい。このサイトの描画コードは DX11 前提） |
| レイトレーシング、メッシュ シェーダー、GPU ドリブンを使いたい | [DirectX 12 Guide](dx12/index.md) |
| DX11 を知っていて DX12 に移る | [DX11 と DX12 の対応表](compare.md) |
| API を選ぶ前に考え方を知りたい | [DirectX Concepts](concepts/index.md) |

## セクションの構成

| 系列 | 内容 | 特徴 |
| --- | --- | --- |
| [概念](concepts/index.md) | GPU パイプライン、リソースとビュー、フォーマット、座標系の規約、同期 | API に依存しない。コードはほぼ無し |
| [DirectX 11](dx11/index.md) | デバイス、スワップ チェーン、シェーダー、バッファ、テクスチャ、ステート、MRT、計算シェーダー | ドライバーが面倒を見る。コードが少ない |
| [DirectX 12](dx12/index.md) | デバイス、コマンド キュー、リスト、フェンス、ディスクリプタ、バリア、PSO、DXR | 自分で管理する。コードが多く高性能 |
| [DX11 と DX12 の対応表](compare.md) | 同じことを 2 つの API で、どう書くか | 移行する人向け |

DX11 と DX12 は <strong>互いに前提にしません</strong>。それぞれウィンドウから最後まで、読み通せます。

## 用語について

DirectX の用語（デバイス、ビュー、ステート、ディスクリプタ、PSO、フェンスなど）は 1 つずつ <strong>専用のページ</strong>を持っています。文章の中の最初の 1 回はそのページへのリンクになります。

## 描画セクションとのつながり

描画セクションの各ページの「DirectX 11 で組む」の節は、このセクションの DX11 のページを使って組み立てます。

| 描画のページ | 使う DX11 のページ |
| --- | --- |
| 影・AO・反射・ポスト プロセス（フルスクリーンのパス） | [Drawing a Triangle](dx11/triangle.md)、[D3D11 Pass Recipes](dx11/pass-recipes.md) |
| G バッファ、ディファード | [Multiple Render Targets](dx11/mrt.md) |
| 計算シェーダーを使う手法（ぼかし、froxel、FFT） | [Compute Shader](dx11/compute-shader.md)、[Unordered Access View (UAV)](dx11/uav.md) |
| レイトレーシング（RTAO、反射、DDGI） | [DXR Host Setup](dx12/dxr-host.md)（DirectX 12） |
| GPU ドリブン | [GPU Driven（D3D12 詳細）](../rendering/gpu-driven-dx12/index.md) |

## 関連ページ

- [DirectXMath](../gamemath/directxmath.md)
- [描画の流れ（入門）](../3d/render-flow/index.md)
- [描画](../graphics/index.md)
- [描画最適化](../rendering/index.md)
