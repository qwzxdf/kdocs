---
title: Descriptor
tags:
  - DirectX
---

# Descriptor

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>ディスクリプタ</strong>は、<strong>リソースを、GPU に、「どう見せるか」を、記述した、小さなデータ</strong>（数十バイト）です。テクスチャの、アドレス、フォーマット、大きさ、ミップの範囲などが、入っています。シェーダーは、リソース本体ではなく、ディスクリプタを、通して、リソースを、読み書きします。[ディスクリプタ ヒープ](descriptor-heap.md)に、並べて、GPU に、見せます。

!!! tip "ポイント"
    - ディスクリプタ ＝ リソースの「見方」の、小さな、記述。種類は、<strong>CBV・SRV・UAV・RTV・DSV・サンプラー</strong>。
    - 作るには、`device->Create…View(resource, desc, handle)`。`handle` は、書き込む、ヒープの位置。
    - 同じリソースに、<strong>複数のディスクリプタ</strong>（別のフォーマット、別のミップ）を、作れる。
    - ディスクリプタを、書いた後でも、リソース本体は、別。リソースは、生かしておく。
    - ルート シグネチャが、「どの、ディスクリプタを、どのレジスタに」を、決める（[Root Signature](root-signature.md)）。

## 6 種類のディスクリプタ

| 種類 | 作る関数 | 内容 | HLSL |
| --- | --- | --- | --- |
| <strong>CBV</strong>（Constant Buffer View） | `CreateConstantBufferView` | 定数バッファを、読む | `cbuffer`（`b#`） |
| <strong>SRV</strong>（Shader Resource View） | `CreateShaderResourceView` | テクスチャ・バッファを、読む | `Texture2D`、`StructuredBuffer`（`t#`） |
| <strong>UAV</strong>（Unordered Access View） | `CreateUnorderedAccessView` | 読み書き | `RWTexture2D`、`RWStructuredBuffer`（`u#`） |
| <strong>RTV</strong>（Render Target View） | `CreateRenderTargetView` | 描き込み先 | `SV_Target` |
| <strong>DSV</strong>（Depth Stencil View） | `CreateDepthStencilView` | 深度の書き込み | （固定機能） |
| <strong>サンプラー</strong> | `CreateSampler` | テクスチャの、読み方 | `SamplerState`（`s#`） |

CBV・SRV・UAV は、同じ種類のヒープ（`CBV_SRV_UAV`）に、混ぜて、並べられます。RTV・DSV・サンプラーは、それぞれ、別のヒープです。

## SRV

```cpp
D3D12_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;                      // テクスチャの、読み方（形式）
srv.ViewDimension = D3D12_SRV_DIMENSION_TEXTURE2D;
srv.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;   // RGBA を、そのまま（入れ替え可能）
srv.Texture2D.MostDetailedMip = 0;
srv.Texture2D.MipLevels = UINT(-1);                                // 全ミップ
device->CreateShaderResourceView(texture.Get(), &srv, cpu_handle);
```

| メンバー | 内容 |
| --- | --- |
| `Format` | ビューの形式。`DXGI_FORMAT_UNKNOWN` で、リソースと、同じ（構造化バッファ） |
| `ViewDimension` | `TEXTURE2D`、`TEXTURE2DARRAY`、`TEXTURECUBE`、`TEXTURE3D`、`BUFFER`、`RAYTRACING_ACCELERATION_STRUCTURE` |
| `Shader4ComponentMapping` | チャンネルの、並べ替え（`D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING` で、そのまま） |
| `Texture2D.MostDetailedMip`・`MipLevels` | 見せる、ミップの範囲（`-1` で、全部） |

`Shader4ComponentMapping` は、必須の、項目です。0 のままだと、全チャンネルが、0 になり、黒く見えます。

## CBV

```cpp
D3D12_CONSTANT_BUFFER_VIEW_DESC cbv = {};
cbv.BufferLocation = constant_buffer->GetGPUVirtualAddress();      // GPU 上の、アドレス
cbv.SizeInBytes = (sizeof(PerObject) + 255) & ~255;                // 256 バイトの倍数（必須）
device->CreateConstantBufferView(&cbv, cpu_handle);                // リソースは、渡さない（アドレスで、指す）
```

CBV の、大きさは、<strong>256 バイトの倍数</strong>です。リソースを、渡さず、<strong>GPU の仮想アドレス</strong>で、指す点が、他の、ビューと、違います（[Constant Buffer](constant-buffer.md)）。

## UAV

```cpp
D3D12_UNORDERED_ACCESS_VIEW_DESC uav = {};
uav.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;
uav.ViewDimension = D3D12_UAV_DIMENSION_TEXTURE2D;
uav.Texture2D.MipSlice = 0;                                        // 1 つのミップだけ
device->CreateUnorderedAccessView(texture.Get(), nullptr, &uav, cpu_handle);   // 第 2 引数: カウンター リソース（Append 用。普通は nullptr）
```

リソースを、作るときに、`D3D12_RESOURCE_FLAG_ALLOW_UNORDERED_ACCESS` が、必要です（[Compute Shader](compute-shader.md)）。

## RTV と DSV

```cpp
// RTV: 描き込み先。バック バッファや、レンダー ターゲットに。
D3D12_RENDER_TARGET_VIEW_DESC rtv = {};
rtv.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
rtv.ViewDimension = D3D12_RTV_DIMENSION_TEXTURE2D;
device->CreateRenderTargetView(back_buffer.Get(), &rtv, rtv_handle);

// DSV: 深度。
D3D12_DEPTH_STENCIL_VIEW_DESC dsv = {};
dsv.Format = DXGI_FORMAT_D32_FLOAT;
dsv.ViewDimension = D3D12_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(depth_texture.Get(), &dsv, dsv_handle);
```

RTV・DSV の、ヒープは、シェーダー不可視で、`OMSetRenderTargets` に、CPU ハンドルを、渡して、使います（[Swap Chain](swap-chain.md)、[Depth Buffer](depth-buffer.md)）。

## サンプラー

```cpp
D3D12_SAMPLER_DESC sampler = {};
sampler.Filter = D3D12_FILTER_ANISOTROPIC;
sampler.AddressU = sampler.AddressV = sampler.AddressW = D3D12_TEXTURE_ADDRESS_MODE_WRAP;
sampler.MaxAnisotropy = 8;
sampler.ComparisonFunc = D3D12_COMPARISON_FUNC_NEVER;
sampler.MinLOD = 0.0f;
sampler.MaxLOD = D3D12_FLOAT32_MAX;
device->CreateSampler(&sampler, sampler_heap_cpu_handle);          // SAMPLER ヒープへ
```

固定のサンプラー（変わらない設定）は、ルート シグネチャに、<strong>静的サンプラー</strong>（`D3D12_STATIC_SAMPLER_DESC`）として、埋め込むと、ヒープが、不要になります（[Root Signature](root-signature.md)）。

## 複数の、ディスクリプタ

同じリソースに、別の、見方の、ディスクリプタを、複数、作れます。

| 例 | ディスクリプタ |
| --- | --- |
| 深度バッファ（`R32_TYPELESS`） | DSV（`D32_FLOAT`）、SRV（`R32_FLOAT`） |
| ミップ付きテクスチャ | 全ミップの SRV、ミップごとの UAV（ミップ チェーンの生成） |
| 配列テクスチャ | 全体の SRV、1 つの面だけの RTV（キューブ シャドウ マップの、6 面） |

## ディスクリプタと、リソースの、寿命

ディスクリプタは、リソースを、<strong>参照するだけ</strong>で、リソースの、寿命を、延ばしません。リソースを、解放すると、ディスクリプタは、<strong>無効</strong>に、なります。GPU が、使用中の、ディスクリプタが、指す、リソースを、解放すると、クラッシュします。

| 注意 | 内容 |
| --- | --- |
| リソースの解放 | GPU の、完了を、フェンスで、確認してから（[Fence](fence.md)） |
| ディスクリプタの、書き換え | GPU が、そのディスクリプタを、使用中に、書き換えない（フレームごとに、別の位置に書く） |

## よくあるミス

??? failure "テクスチャが、真っ黒に、見える"
    SRV の、`Shader4ComponentMapping` が 0。`D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING` を、指定する。

??? failure "CBV の作成で、デバッグ レイヤーが、エラーを、出す"
    `SizeInBytes` が、256 の倍数でない。`(size + 255) & ~255` で、切り上げる。

??? failure "`CreateUnorderedAccessView` が、エラー"
    リソースの、作成時に、`ALLOW_UNORDERED_ACCESS` を、付けていない。フォーマットが、UAV に、使えない（`_SRGB`、圧縮）。

??? failure "リソースを、解放したら、後で、クラッシュする"
    GPU が、まだ、そのリソースを、参照する、ディスクリプタを、使っている。フェンスで、完了を、待つ。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ディスクリプタ ＝ リソースの、見方の、小さな、記述。CBV・SRV・UAV・RTV・DSV・サンプラー
    - [x] `device->Create…View(resource, desc, handle)` で、ヒープの、位置に、書く
    - [x] SRV は、`Shader4ComponentMapping`。CBV は、256 の倍数、アドレスで、指す
    - [x] 同じリソースに、複数の、見方を、作れる
    - [x] ディスクリプタは、リソースの寿命を、延ばさない

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Descriptor Heap](descriptor-heap.md)
- [Root Signature](root-signature.md)
- [Resource Barrier](resource-barrier.md)
- [Microsoft Learn: ディスクリプタ](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/descriptors-overview)
