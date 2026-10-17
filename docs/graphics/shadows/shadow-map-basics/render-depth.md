---
title: Rendering Depth
tags:
  - 描画
---

# Rendering Depth

**光の行列ができたら、その視点から、シーンの深度だけを描きます**。**色は要らず、深度バッファだけ**に書くので、**非常に安いパス**です。**描くのは「影を落とす物」だけ**に**絞る**と**さらに速くなります**。このページでは、**深度専用パスの設定・ピクセル シェーダーなし・カリングの向き・描く対象の絞り込み**を説明します。

!!! tip "ポイント"
    - **深度だけを描く**（**カラー書き込みなし・ピクセル シェーダーなし**）。
    - **影を落とさない物は描かない**（**カリング・フラグ**）。
    - **前面カリング**を使うと**アクネが減る**ことがある（[バイアス](../bias/front-face-culling.md)）。
    - **アルファ テストの物**は**ピクセル シェーダーが要る**（[Alpha-Tested Shadows](../special-cases/alpha-test-shadows.md)）。

## ② シャドウ マップを描く
**深度だけ**を描きます。**ピクセルシェーダーは不要**（アルファ テストする物を除く）で、**非常に速い**描画です。

```cpp
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = 2048;
desc.Height = 2048;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R32_TYPELESS;
desc.SampleDesc.Count = 1;
desc.BindFlags = D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &shadow_tex);

D3D11_DEPTH_STENCIL_VIEW_DESC dsv_desc = {};
dsv_desc.Format = DXGI_FORMAT_D32_FLOAT;
dsv_desc.ViewDimension = D3D11_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(shadow_tex, &dsv_desc, &shadow_dsv);

D3D11_SHADER_RESOURCE_VIEW_DESC srv_desc = {};
srv_desc.Format = DXGI_FORMAT_R32_FLOAT;
srv_desc.ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D;
srv_desc.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(shadow_tex, &srv_desc, &shadow_srv);
```

設定の要点です。`R32_TYPELESS` は、深度として書き、シェーダーから読むため、型なしで作ります。DSV は `D32_FLOAT`、SRV は `R32_FLOAT` で、同じ領域を 2 通りに見ます。解像度は 1024〜4096 で、大きいほど細かい影になりますが、メモリと帯域を食います（[メモリ帯域幅](../../../rendering/bandwidth.md)）。フォーマットは 16 ビットで足りることも多く、精度を許容できれば帯域が半分になります。描画する物は影を落とす物だけで、ライティングなしのシェーダー（頂点シェーダーのみ）で描きます。

## よくあるミス

??? failure "画面に映らない物だけを描いて、影が欠ける"
    **光から見える物を描く**。**画面外の物も、影を落とす**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **光から見た深度だけを描く、軽いパス**
    - [x] **対象を絞る**。**ピクセル シェーダー不要（アルファ テスト以外）**

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [Shadow Map Basics](index.md)
- [The Light Matrix](light-matrix.md)
- [Comparison Samplers](comparison-sampler.md)
