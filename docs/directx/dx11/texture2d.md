---
title: Texture2D
tags:
  - DirectX
---

# Texture2D

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>2D テクスチャ</strong>（`ID3D11Texture2D`）は、GPU 上の、画像の、リソースです。物の表面に、貼る絵、シーンを描く先（レンダー ターゲット）、深度バッファ、G バッファ、シャドウ マップ、計算シェーダーの、出力まで、画像の形をした、データは、すべて、2D テクスチャです。作り方は、1 つで、`BindFlags`（使い方）と、<strong>フォーマット</strong>で、役割が、決まります。

!!! tip "ポイント"
    - テクスチャ（リソース）は、<strong>ビュー</strong>を通して、使う。貼るなら SRV、描くなら RTV、計算で書くなら UAV、深度なら DSV。
    - `BindFlags` に、使う予定の、すべてのビューの、種類を、<strong>最初に</strong>、書く。あとから、足せない。
    - 画像ファイルから、作るには、デコードして、`D3D11_SUBRESOURCE_DATA` で、渡す（WIC、`DirectXTK` の `CreateWICTextureFromFile`、`stb_image`）。
    - 色（アルベド）は、`_SRGB` フォーマット。法線、粗さなど、色でない、データは、`_UNORM`（リニア）。
    - ミップマップを、作ると、遠くの、ちらつきが、減る。`GenerateMips`。

## 作る

```cpp
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = 1;                                         // ミップの数。0 で、全段
desc.ArraySize = 1;                                         // 配列の長さ。1 で、普通のテクスチャ
desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;              // 色の画像: sRGB
desc.SampleDesc.Count = 1;                                  // MSAA なし
desc.Usage = D3D11_USAGE_IMMUTABLE;                         // 作ったら、変更しない
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE;                // シェーダーから、読む（貼る）

D3D11_SUBRESOURCE_DATA init = {};
init.pSysMem = pixels;                                      // 画素のデータ（RGBA、各 8 ビット）
init.SysMemPitch = width * 4;                               // 1 行のバイト数

Microsoft::WRL::ComPtr<ID3D11Texture2D> texture;
device->CreateTexture2D(&desc, &init, &texture);
```

| メンバー | 内容 |
| --- | --- |
| `Width`・`Height` | 大きさ（ピクセル）。2 のべき乗である、必要は、ない（ミップを、使うなら、きれいに、割れる、大きさが、望ましい） |
| `MipLevels` | ミップマップの、段数。1 でミップなし、0 で、1×1 まで、全段 |
| `ArraySize` | 配列の、要素の数。キューブマップは 6 |
| `Format` | 画素の形式（[Formats and Typeless](../concepts/formats.md)） |
| `SampleDesc` | MSAA の、サンプル数。通常 `{1, 0}` |
| `Usage` | `IMMUTABLE`、`DEFAULT`、`DYNAMIC`、`STAGING`（[Map, Unmap and UpdateSubresource](map-update.md)） |
| `BindFlags` | `SHADER_RESOURCE`、`RENDER_TARGET`、`DEPTH_STENCIL`、`UNORDERED_ACCESS`。OR で、複数 |
| `CPUAccessFlags` | `DYNAMIC` のとき `WRITE`、`STAGING` のとき `READ`/`WRITE` |
| `MiscFlags` | `GENERATE_MIPS`、`TEXTURECUBE`、`SHARED` など |

`SysMemPitch` は、<strong>1 行のバイト数</strong>です。幅 × 1 画素の、バイト数で、圧縮フォーマットなどでは、計算が、違います。

## 使い方別の、BindFlags

| 用途 | `BindFlags` | `Usage` |
| --- | --- | --- |
| 貼る絵（アルベド、法線マップ） | `SHADER_RESOURCE` | `IMMUTABLE`（初期データ有り） |
| シーンの描画先（HDR 色） | `RENDER_TARGET \| SHADER_RESOURCE` | `DEFAULT` |
| 深度 | `DEPTH_STENCIL`（+ `SHADER_RESOURCE`） | `DEFAULT` |
| 計算シェーダーの出力 | `UNORDERED_ACCESS \| SHADER_RESOURCE` | `DEFAULT` |
| 毎フレーム、書く画像（動画、UI） | `SHADER_RESOURCE` | `DYNAMIC` |

## ミップマップ

遠くの、物は、画面上で、小さく、写るので、元の画像（大きい）を、そのまま、読むと、1 画素が、多くの、テクセルを、またぎ、<strong>ちらつき</strong>（エイリアシング）が、出ます。<strong>半分、半分、…に、縮めた、画像の列</strong>（ミップマップ）を、用意すると、距離に応じて、適切な、段を、読めます。

```cpp
// GPU に、ミップ チェーンを、作らせる。RENDER_TARGET と GENERATE_MIPS が必要。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = 0;                                         // 0 = 全段
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_RENDER_TARGET;
desc.MiscFlags = D3D11_RESOURCE_MISC_GENERATE_MIPS;
device->CreateTexture2D(&desc, nullptr, &texture);          // 初期データは、なし（あとで、ミップ 0 を、書く）

device->CreateShaderResourceView(texture.Get(), nullptr, &srv);
context->UpdateSubresource(texture.Get(), 0, nullptr, pixels, width * 4, 0);    // ミップ 0 に、元の画像を書く
context->GenerateMips(srv.Get());                           // 残りの段を、GPU が、縮小して、作る
```

`GenerateMips` は、SRV を、渡します。`DEFAULT` で、`RENDER_TARGET` が、付いていて、`GENERATE_MIPS` の、`MiscFlags` が、ある、テクスチャだけが、使えます。製品では、ビルド時に、高品質な、ミップを、作って、DDS ファイルに、保存します（[Texture Streaming](../../rendering/texture-streaming.md)）。

| ミップ | 大きさ（1024×1024 の場合） |
| --- | --- |
| 0 | 1024×1024 |
| 1 | 512×512 |
| 2 | 256×256 |
| … | … |
| 10 | 1×1 |

ミップを、全段、持つと、メモリは、<strong>元の約 1.33 倍</strong>（1 + 1/4 + 1/16 + …）です。

## 画像ファイルから、読み込む

D3D11 自身は、PNG や JPG を、デコードできません。次の、ライブラリを、使います。

| 方法 | 内容 |
| --- | --- |
| DirectXTK の `CreateWICTextureFromFile` | WIC（Windows の画像デコーダー）で、PNG、JPG などを、読み、SRV まで、作る |
| DirectXTK の `CreateDDSTextureFromFile` | DDS（圧縮・ミップ入り）を、読む。ゲームの、標準形式 |
| `stb_image` | 1 ファイルの、軽量デコーダー。RGBA の、ピクセル列を、返す。自分で `CreateTexture2D` |

```cpp
// DirectXTK（ライブラリ）
#include <WICTextureLoader.h>

Microsoft::WRL::ComPtr<ID3D11ShaderResourceView> srv;
DirectX::CreateWICTextureFromFileEx(device.Get(), context.Get(), L"albedo.png", 0,
                                    D3D11_USAGE_DEFAULT, D3D11_BIND_SHADER_RESOURCE, 0, 0,
                                    DirectX::WIC_LOADER_FORCE_SRGB | DirectX::WIC_LOADER_MIP_AUTOGEN,
                                    nullptr, &srv);
```

`WIC_LOADER_FORCE_SRGB` で、色の画像を、`_SRGB` で、読み、`WIC_LOADER_MIP_AUTOGEN` で、ミップを、自動生成します。ファイルが、sRGB か、リニアかは、ファイル自体からは、分からないことが、多いので、<strong>用途で、決めて、明示</strong>します。

## 配列とキューブマップ

`ArraySize` を、2 以上にすると、同じ、大きさ・形式の、画像を、まとめた、<strong>配列</strong>に、なります。`Texture2DArray` として、シェーダーで、インデックスで、選べます。

```cpp
desc.ArraySize = 6;
desc.MiscFlags = D3D11_RESOURCE_MISC_TEXTURECUBE;           // 6 面で、キューブマップ（反射プローブ、スカイボックス）
```

```hlsl
TextureCube g_sky : register(t0);
float4 color = g_sky.Sample(g_sampler, direction);          // 3D の方向で、引く
```

## サブリソース

テクスチャの、各ミップ・各配列要素を、<strong>サブリソース</strong>と、呼びます。サブリソースの、番号は、`ミップ + 配列の要素 × ミップ数` です。

```cpp
UINT subresource = D3D11CalcSubresource(mip_slice, array_slice, mip_levels);
```

`UpdateSubresource`、`Map`、`CopySubresourceRegion` に、この番号を、渡します。

## よくあるミス

??? failure "テクスチャが、暗い（または、色が、くすむ）"
    色の画像（アルベド）を、`_UNORM` で、読んでいる。`_SRGB` にする。逆に、法線マップを、`_SRGB` で、読むと、値が、歪む。

??? failure "`CreateShaderResourceView` が、失敗する"
    `BindFlags` に `SHADER_RESOURCE` が、無い。`CreateRenderTargetView` も、同様（`RENDER_TARGET` が、無い）。

??? failure "遠くの床が、ちらつく・ざらざらする"
    ミップマップが、無い（`MipLevels = 1`）。ミップを、作る。サンプラーが、ミップを、使う設定に、なっているかも、確認（[Sampler State](sampler-state.md)）。

??? failure "テクスチャが、斜めに、ずれて、見える"
    `SysMemPitch` が、間違っている（`width * 4` のところに、別の値）。または、元の画像の、行の、パディングを、無視している。

??? failure "メモリ使用量が、想定より、大きい"
    ミップで、1.33 倍。`R32G32B32A32_FLOAT` など、大きなフォーマットを、使っている。圧縮（BC1、BC7）を、使う（[Formats and Typeless](../concepts/formats.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2D テクスチャ ＝ 画像のリソース。使い方は、ビューと、`BindFlags` で、決まる
    - [x] `CreateTexture2D` に、`D3D11_SUBRESOURCE_DATA`（画素と、行の幅）を、渡す
    - [x] 色は `_SRGB`、色でないデータは `_UNORM`（リニア）
    - [x] ミップマップで、遠くの、ちらつきを、抑える（`GenerateMips`、または、DDS）
    - [x] 画像ファイルは、DirectXTK か `stb_image` で、デコードする
    - [x] `BindFlags` は、最初に、全部書く

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Shader Resource View (SRV)](shader-resource-view.md)
- [Sampler State](sampler-state.md)
- [Formats and Typeless](../concepts/formats.md)
- [Map, Unmap and UpdateSubresource](map-update.md)
- [Microsoft Learn: ID3D11Device::CreateTexture2D](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createtexture2d)
