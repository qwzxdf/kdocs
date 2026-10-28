---
title: Texture2D
tags:
  - DirectX
---

# Texture2D

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>2D テクスチャ</strong>（`ID3D11Texture2D`）は GPU 上の画像のリソースです。物の表面に貼る絵、シーンを描く先（レンダー ターゲット）、深度バッファ、G バッファ、シャドウ マップ、計算シェーダーの出力まで画像の形をしたデータはすべて 2D テクスチャです。作り方は 1 つで `BindFlags`（使い方）と <strong>フォーマット</strong>で役割が決まります。

!!! tip "ポイント"
    - テクスチャ（リソース）は、<strong>ビュー</strong>を通して使う。貼るなら SRV、描くなら RTV、計算で書くなら UAV、深度なら DSV。
    - `BindFlags` に使う予定のすべてのビューの種類を <strong>最初に</strong>、書く。あとから足せない。
    - 画像ファイルから、作るにはデコードして `D3D11_SUBRESOURCE_DATA` で渡す（WIC、`DirectXTK` の `CreateWICTextureFromFile`、`stb_image`）。
    - 色（アルベド）は `_SRGB` フォーマット。法線、粗さなど色でないデータは `_UNORM`（リニア）。
    - ミップマップを作ると遠くのちらつきが減る。`GenerateMips`。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

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
| `Width`・`Height` | 大きさ（ピクセル）。2 のべき乗である必要はない（ミップを使うならきれいに割れる大きさが、望ましい） |
| `MipLevels` | ミップマップの段数。1 でミップなし 0 で 1×1 まで、全段 |
| `ArraySize` | 配列の要素の数。キューブマップは 6 |
| `Format` | 画素の形式（[Formats and Typeless](../concepts/formats.md)） |
| `SampleDesc` | MSAA のサンプル数。通常 `{1, 0}` |
| `Usage` | `IMMUTABLE`、`DEFAULT`、`DYNAMIC`、`STAGING`（[Map, Unmap and UpdateSubresource](map-update.md)） |
| `BindFlags` | `SHADER_RESOURCE`、`RENDER_TARGET`、`DEPTH_STENCIL`、`UNORDERED_ACCESS`。OR で複数 |
| `CPUAccessFlags` | `DYNAMIC` のとき `WRITE`、`STAGING` のとき `READ`/`WRITE` |
| `MiscFlags` | `GENERATE_MIPS`、`TEXTURECUBE`、`SHARED` など |

`SysMemPitch` は <strong>1 行のバイト数</strong>です。幅 × 1 画素のバイト数で、圧縮フォーマットなどでは計算が違います。

## 使い方別の BindFlags

| 用途 | `BindFlags` | `Usage` |
| --- | --- | --- |
| 貼る絵（アルベド、法線マップ） | `SHADER_RESOURCE` | `IMMUTABLE`（初期データ有り） |
| シーンの描画先（HDR 色） | `RENDER_TARGET \| SHADER_RESOURCE` | `DEFAULT` |
| 深度 | `DEPTH_STENCIL`（+ `SHADER_RESOURCE`） | `DEFAULT` |
| 計算シェーダーの出力 | `UNORDERED_ACCESS \| SHADER_RESOURCE` | `DEFAULT` |
| 毎フレーム、書く画像（動画、UI） | `SHADER_RESOURCE` | `DYNAMIC` |

## ミップマップ

遠くの物は画面上で小さく写るので、元の画像（大きい）をそのまま読むと 1 画素が多くのテクセルをまたぎ <strong>ちらつき</strong>（エイリアシング）が出ます。<strong>半分、半分、…に縮めた画像の列</strong>（ミップマップ）を用意すると距離に応じて適切な段を読めます。

```cpp
// GPU に、ミップ チェーンを作らせる。RENDER_TARGET と GENERATE_MIPS が必要。
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
device->CreateTexture2D(&desc, nullptr, &texture);          // 初期データは、なし（あとで、ミップ 0 を書く）

device->CreateShaderResourceView(texture.Get(), nullptr, &srv);
context->UpdateSubresource(texture.Get(), 0, nullptr, pixels, width * 4, 0);    // ミップ 0 に、元の画像を書く
context->GenerateMips(srv.Get());                           // 残りの段を GPU が、縮小して、作る
```

`GenerateMips` は SRV を渡します。`DEFAULT` で `RENDER_TARGET` が付いていて `GENERATE_MIPS` の `MiscFlags` がある、テクスチャだけが使えます。製品ではビルド時に高品質なミップを作って、DDS ファイルに保存します（[Texture Streaming](../../rendering/texture-streaming.md)）。

| ミップ | 大きさ（1024×1024 の場合） |
| --- | --- |
| 0 | 1024×1024 |
| 1 | 512×512 |
| 2 | 256×256 |
| … | … |
| 10 | 1×1 |

ミップを全段、持つとメモリは <strong>元の約 1.33 倍</strong>（1 + 1/4 + 1/16 + …）です。

## 画像ファイルから読み込む

D3D11 自身は PNG や JPG をデコードできません。次のライブラリを使います。

| 方法 | 内容 |
| --- | --- |
| DirectXTK の `CreateWICTextureFromFile` | WIC（Windows の画像デコーダー）で PNG、JPG などを読み SRV まで、作る |
| DirectXTK の `CreateDDSTextureFromFile` | DDS（圧縮・ミップ入り）を読む。ゲームの標準形式 |
| `stb_image` | 1 ファイルの軽量デコーダー。RGBA のピクセル列を返す。自分で `CreateTexture2D` |

```cpp
// DirectXTK（ライブラリ）
#include <WICTextureLoader.h>

Microsoft::WRL::ComPtr<ID3D11ShaderResourceView> srv;
DirectX::CreateWICTextureFromFileEx(device.Get(), context.Get(), L"albedo.png", 0,
                                    D3D11_USAGE_DEFAULT, D3D11_BIND_SHADER_RESOURCE, 0, 0,
                                    DirectX::WIC_LOADER_FORCE_SRGB | DirectX::WIC_LOADER_MIP_AUTOGEN,
                                    nullptr, &srv);
```

`WIC_LOADER_FORCE_SRGB` で色の画像を `_SRGB` で読み `WIC_LOADER_MIP_AUTOGEN` で、ミップを自動生成します。ファイルが sRGB かリニアかはファイル自体からは分からないことが、多いので <strong>用途で決めて明示</strong>します。

## 配列とキューブマップ

`ArraySize` を 2 以上にすると同じ大きさ・形式の画像をまとめた <strong>配列</strong>になります。`Texture2DArray` としてシェーダーでインデックスで、選べます。

```cpp
desc.ArraySize = 6;
desc.MiscFlags = D3D11_RESOURCE_MISC_TEXTURECUBE;           // 6 面で、キューブマップ（反射プローブ、スカイボックス）
```

```hlsl
TextureCube g_sky : register(t0);
float4 color = g_sky.Sample(g_sampler, direction);          // 3D の方向で、引く
```

## サブリソース

テクスチャの各ミップ・各配列要素を <strong>サブリソース</strong>と呼びます。サブリソースの番号は `ミップ + 配列の要素 × ミップ数` です。

```cpp
UINT subresource = D3D11CalcSubresource(mip_slice, array_slice, mip_levels);
```

`UpdateSubresource`、`Map`、`CopySubresourceRegion` にこの番号を渡します。

## よくあるミス

??? failure "テクスチャが暗い（または色がくすむ）"
    色の画像（アルベド）を `_UNORM` で、読んでいる。`_SRGB` にする。逆に、法線マップを `_SRGB` で読むと値が歪む。

??? failure "`CreateShaderResourceView` が、失敗する"
    `BindFlags` に `SHADER_RESOURCE` が無い。`CreateRenderTargetView` も同様（`RENDER_TARGET` が無い）。

??? failure "遠くの床がちらつく・ざらざらする"
    ミップマップが無い（`MipLevels = 1`）。ミップを作る。サンプラーがミップを使う設定になっているかも確認（[Sampler State](sampler-state.md)）。

??? failure "テクスチャが斜めにずれて、見える"
    `SysMemPitch` が間違っている（`width * 4` のところに別の値）。または、元の画像の行のパディングを無視している。

??? failure "メモリ使用量が想定より大きい"
    ミップで 1.33 倍。`R32G32B32A32_FLOAT` など大きなフォーマットを使っている。圧縮（BC1、BC7）を使う（[Formats and Typeless](../concepts/formats.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2D テクスチャ ＝ 画像のリソース。使い方はビューと `BindFlags` で決まる
    - [x] `CreateTexture2D` に `D3D11_SUBRESOURCE_DATA`（画素と行の幅）を渡す
    - [x] 色は `_SRGB`、色でないデータは `_UNORM`（リニア）
    - [x] ミップマップで遠くのちらつきを抑える（`GenerateMips`、または DDS）
    - [x] 画像ファイルは DirectXTK か `stb_image` で、デコードする
    - [x] `BindFlags` は最初に全部書く

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Shader Resource View (SRV)](shader-resource-view.md)
- [Sampler State](sampler-state.md)
- [Formats and Typeless](../concepts/formats.md)
- [Map, Unmap and UpdateSubresource](map-update.md)
- [Microsoft Learn: ID3D11Device::CreateTexture2D](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createtexture2d)
