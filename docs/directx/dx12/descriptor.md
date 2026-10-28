---
title: Descriptor
tags:
  - DirectX
---

# Descriptor

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

テクスチャのデータそのものは、GPU のメモリに並んでいるバイト列にすぎません。シェーダーがそれを「256×256 の RGBA で、ミップが 9 段あるテクスチャ」として読むためには、メモリの場所、形式、大きさミップの範囲といった情報が必要です。その情報を書いた数十バイトの小さなデータが <strong>ディスクリプタ</strong>です。

シェーダーはリソースそのものではなく、ディスクリプタを通してリソースを読み書きします。ディスクリプタは[Descriptor Heap](descriptor-heap.md) に並べて、GPU に見せます。

!!! tip "ポイント"
    - ディスクリプタはリソースの「見方」を書いた小さなデータ。種類は CBV、SRV、UAV、RTV、DSV、サンプラーの 6 つ。
    - 作るには `device->CreateXxxView(resource, desc, handle)`。`handle` は書き込むヒープの位置。
    - 同じリソースに複数のディスクリプタ（別の形式、別のミップ）を作れる。
    - ディスクリプタを書いたあともリソース本体は別にある。リソースは生かしておく。
    - どのディスクリプタをどのレジスタに結ぶかは、ルート シグネチャが決める（[Root Signature](root-signature.md)）。

!!! info "このページを読む前に"
    ディスクリプタを置く表は [Descriptor Heap](descriptor-heap.md)、リソースそのものは [Heaps and Resources](heaps-resources.md) で説明しています。ビューを作る各メソッドの引数は [ID3D12Device](api/id3d12device.md) にあります。

## 6 種類のディスクリプタ

ディスクリプタは役割で 6 種類に分かれます。

CBV（Constant Buffer View）は、定数バッファを読むためのビューで、HLSL の `cbuffer`（`b0` などのレジスタ）に結びます。SRV（Shader Resource View）は、テクスチャやバッファを読むためのビューで、`Texture2D` や `StructuredBuffer`（`t0` など）に結びます。UAV（Unordered Access View）は、読み書きできるビューで `RWTexture2D` や `RWStructuredBuffer`（`u0` など）に結びます。

RTV（Render Target View）は、描き込み先でピクセル シェーダーの出力（`SV_Target`）が書かれます。DSV（Depth Stencil View）は、深度バッファの見方です。サンプラーはテクスチャの読み方（フィルターや繰り返し方）で、`SamplerState`（`s0` など）に結びます。

CBV、SRV、UAV は同じ種類のヒープ（`CBV_SRV_UAV`）に混ぜて並べられます。RTV、DSV、サンプラーはそれぞれ別のヒープです。

## SRV

SRV はテクスチャを読むときに一番よく使うビューです。

```cpp
D3D12_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;  // テクスチャの読み方（形式）
srv.ViewDimension = D3D12_SRV_DIMENSION_TEXTURE2D;
srv.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;  // RGBA をそのまま
srv.Texture2D.MostDetailedMip = 0;
srv.Texture2D.MipLevels = UINT(-1);  // 全ミップ
device->CreateShaderResourceView(texture.Get(), &srv, cpu_handle);
```

`Format` はシェーダーから見たときの形式です。リソースを作ったときの形式と同じか互換のある形式を選びます。`_SRGB` を付けると読むときに sRGB からリニアへ自動で変換されます。構造化バッファでは `DXGI_FORMAT_UNKNOWN` にします。

`ViewDimension` はリソースの種類です。`TEXTURE2D`、`TEXTURE2DARRAY`、`TEXTURECUBE`、`TEXTURE3D`、`BUFFER` があり DXR の加速構造には `RAYTRACING_ACCELERATION_STRUCTURE` を使います。種類によって書くべきメンバー（`Texture2D` か `Buffer` か）が変わります。

`Shader4ComponentMapping` は**必須の項目**です。R、G、B、A のどのチャンネルをシェーダーの x、y、z、w に割り当てるかを決めます。ふつうは `D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING`（そのまま）を書きます。0 のままにするとすべてのチャンネルが 0 になりテクスチャが真っ黒に見えます。

`MostDetailedMip` と `MipLevels` は見せるミップの範囲です。`MipLevels` に `-1` を渡すと最も詳細なミップから最後までのすべてになります。

## CBV

CBV はほかのビューと作り方が少し違います。リソースを渡さず GPU から見たアドレスで指します。

```cpp
D3D12_CONSTANT_BUFFER_VIEW_DESC cbv = {};
cbv.BufferLocation = constant_buffer->GetGPUVirtualAddress();  // GPU 上のアドレス
cbv.SizeInBytes = (sizeof(PerObject) + 255) & ~255;            // 256 バイトの倍数（必須）
device->CreateConstantBufferView(&cbv, cpu_handle);            // リソースは渡さない
```

`SizeInBytes` は 256 の倍数でなければなりません。構造体の大きさが 256 の倍数でなければ、`(size + 255) & ~255` で切り上げてそのぶんを多めに確保します。同じバッファの中に複数の CBV を並べるときは、`BufferLocation` も 256 バイトの境界にそろえます（[Constant Buffer](constant-buffer.md)）。

## UAV

UAV はコンピュート シェーダーの出力先など読み書きするときに使います。

```cpp
D3D12_UNORDERED_ACCESS_VIEW_DESC uav = {};
uav.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;
uav.ViewDimension = D3D12_UAV_DIMENSION_TEXTURE2D;
uav.Texture2D.MipSlice = 0;  // 1 つのミップだけ
device->CreateUnorderedAccessView(texture.Get(), nullptr, &uav, cpu_handle);
```

第 2 引数は `AppendStructuredBuffer` のカウンターを別のバッファに置くときの指定で、ふつうは `nullptr` です。UAV は 1 つのミップだけを指すので、ミップ チェーンを作るときはミップごとに UAV を作ります。

UAV にするリソースは作るときに `D3D12_RESOURCE_FLAG_ALLOW_UNORDERED_ACCESS` を付けておく必要があります。`_SRGB` や圧縮形式のように UAV に使えない形式もあります（[Compute Shader](compute-shader.md)）。

## RTV と DSV

RTV と DSV は描き込み先と深度バッファの見方です。

```cpp
// RTV: 描き込み先。バック バッファやレンダー ターゲットに作る。
D3D12_RENDER_TARGET_VIEW_DESC rtv = {};
rtv.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
rtv.ViewDimension = D3D12_RTV_DIMENSION_TEXTURE2D;
device->CreateRenderTargetView(back_buffer.Get(), &rtv, rtv_handle);

// DSV: 深度バッファ。
D3D12_DEPTH_STENCIL_VIEW_DESC dsv = {};
dsv.Format = DXGI_FORMAT_D32_FLOAT;
dsv.ViewDimension = D3D12_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(depth_texture.Get(), &dsv, dsv_handle);
```

RTV と DSV のヒープはシェーダーから見えません。`OMSetRenderTargets` に CPU ハンドルを渡して使います（[Swap Chain](swap-chain.md)、[Depth Buffer](depth-buffer.md)）。

## サンプラー

サンプラーはテクスチャをどう読むか（補間するか端でどうするか）を決めます。

```cpp
D3D12_SAMPLER_DESC sampler = {};
sampler.Filter = D3D12_FILTER_ANISOTROPIC;
sampler.AddressU = sampler.AddressV = sampler.AddressW = D3D12_TEXTURE_ADDRESS_MODE_WRAP;
sampler.MaxAnisotropy = 8;
sampler.ComparisonFunc = D3D12_COMPARISON_FUNC_NEVER;
sampler.MinLOD = 0.0f;
sampler.MaxLOD = D3D12_FLOAT32_MAX;
device->CreateSampler(&sampler, sampler_heap_cpu_handle);  // SAMPLER ヒープへ
```

変わらない固定のサンプラーはルート シグネチャに**静的サンプラー**として埋め込むと、ヒープが要らなくなります（[Root Signature](root-signature.md)）。

## 1 つのリソースに複数のディスクリプタを作る

同じリソースに別の見方のディスクリプタを複数作れます。深度バッファは `R32_TYPELESS` で作り DSV を `D32_FLOAT`、SRV を `R32_FLOAT` で作ります。深度を描いたあとシェーダーで読めるようになります。

ミップ付きのテクスチャでは全ミップを見る SRV とミップごとの UAV を作る、といった使い方をします。配列のテクスチャでは全体を見る SRV と 1 つの面だけの RTV を作れます。キューブ シャドウ マップの 6 面は、この使い方です。

## ディスクリプタとリソースの寿命

ディスクリプタはリソースを指しているだけで、リソースの寿命を延ばしません。リソースを解放するとディスクリプタは無効になります。GPU が使っているディスクリプタの指す先のリソースを解放すると、クラッシュします。

リソースを解放するときは GPU の完了をフェンスで確認してからにします（[Fence](fence.md)）。また、GPU が使っている最中のディスクリプタを書き換えてもいけません。フレームごとに別の位置へ書きます。

## よくあるミス

??? failure "テクスチャが真っ黒に見える"
    SRV の `Shader4ComponentMapping` が 0 です。`D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING` を指定します。

??? failure "CBV の作成で、デバッグ レイヤーがエラーを出す"
    `SizeInBytes` が 256 の倍数ではありません。`(size + 255) & ~255` で切り上げます。

??? failure "`CreateUnorderedAccessView` でエラーになる"
    リソースを作るときに `ALLOW_UNORDERED_ACCESS` を付けていないか形式が UAV に使えません（`_SRGB`、圧縮形式）。

??? failure "リソースを解放したら、あとでクラッシュする"
    GPU がそのリソースを指すディスクリプタをまだ使っています。フェンスで完了を待ちます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ディスクリプタは、リソースの見方を書いた小さなデータ。CBV、SRV、UAV、RTV、DSV、サンプラー
    - [x] `device->CreateXxxView(resource, desc, handle)` でヒープの位置に書く
    - [x] SRV は `Shader4ComponentMapping` を必ず書く。CBV は 256 の倍数で、アドレスで指す
    - [x] 同じリソースに複数の見方を作れる
    - [x] ディスクリプタは、リソースの寿命を延ばさない

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Descriptor Heap](descriptor-heap.md)
- [ID3D12Device](api/id3d12device.md)
- [Root Signature](root-signature.md)
- [Resource Barrier](resource-barrier.md)
- [Microsoft Learn: ディスクリプタ](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/descriptors-overview)
