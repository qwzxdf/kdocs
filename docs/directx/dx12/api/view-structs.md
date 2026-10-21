---
title: View and Descriptor Structs
tags:
  - DirectX
api:
  - D3D12_DESCRIPTOR_HEAP_DESC
---

# View and Descriptor Structs

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

GPU はリソースの名前もポインタも知りません。シェーダーがテクスチャを読んだり、出力がレンダー ターゲットに書いたりするには、「このリソースを、この形式で、この範囲で見る」という小さなデータ（ディスクリプタ）をヒープに書いておく必要があります。そのディスクリプタを書き込むときに渡す構造体と、書き込み先を指すハンドルが、このページの主役です。

!!! tip "ポイント"
    - ディスクリプタの置き場は `D3D12_DESCRIPTOR_HEAP_DESC` で作り、書き込み先は `D3D12_CPU_DESCRIPTOR_HANDLE` で指す。
    - `ptr` は生の数値。n 番目は `ptr + n × 増分` で求め、増分は `GetDescriptorHandleIncrementSize` で調べる。
    - `Format` を `UNKNOWN` にするとリソースの形式を引き継ぐ。ただし typeless のときは明示が必要。
    - `ViewDimension` が決めた共用体のメンバーだけを埋める。
    - 頂点・インデックス・定数バッファのビューは、リソースの GPU 仮想アドレスを持つ。

!!! info "このページを読む前に"
    ディスクリプタの考え方は [Descriptor](../descriptor.md) と [Descriptor Heap](../descriptor-heap.md)、書き込むメソッドは [ID3D12Device](id3d12device.md) で説明しています。

## 構造体一覧

| 構造体 | 役割 | 使う場所 |
| --- | --- | --- |
| [`D3D12_DESCRIPTOR_HEAP_DESC`](#d3d12_descriptor_heap_desc) | ディスクリプタ ヒープの設計 | `CreateDescriptorHeap` |
| [`D3D12_CPU_DESCRIPTOR_HANDLE`](#d3d12_cpu_descriptor_handle) | CPU から書き込む位置 | `CreateXxxView`、`ClearRenderTargetView` |
| [`D3D12_GPU_DESCRIPTOR_HANDLE`](#d3d12_gpu_descriptor_handle) | GPU が読む位置 | `SetGraphicsRootDescriptorTable` |
| [`D3D12_RENDER_TARGET_VIEW_DESC`](#d3d12_render_target_view_desc) | RTV の形 | `CreateRenderTargetView` |
| [`D3D12_DEPTH_STENCIL_VIEW_DESC`](#d3d12_depth_stencil_view_desc) | DSV の形 | `CreateDepthStencilView` |
| [`D3D12_SHADER_RESOURCE_VIEW_DESC`](#d3d12_shader_resource_view_desc) | SRV の形 | `CreateShaderResourceView` |
| [`D3D12_UNORDERED_ACCESS_VIEW_DESC`](#d3d12_unordered_access_view_desc) | UAV の形 | `CreateUnorderedAccessView` |
| [`D3D12_CONSTANT_BUFFER_VIEW_DESC`](#d3d12_constant_buffer_view_desc) | CBV の形 | `CreateConstantBufferView` |
| [`D3D12_VERTEX_BUFFER_VIEW`](#d3d12_vertex_buffer_view) | 頂点バッファの指定 | `IASetVertexBuffers` |
| [`D3D12_INDEX_BUFFER_VIEW`](#d3d12_index_buffer_view) | インデックス バッファの指定 | `IASetIndexBuffer` |
| [`D3D12_SAMPLER_DESC`](#d3d12_sampler_desc) | サンプラーの設定 | `CreateSampler` |
| [`D3D12_STATIC_SAMPLER_DESC`](#d3d12_static_sampler_desc) | ルート シグネチャに埋め込むサンプラー | `D3D12_ROOT_SIGNATURE_DESC` |

## ヒープとハンドル

### D3D12_DESCRIPTOR_HEAP_DESC {#d3d12_descriptor_heap_desc}

```cpp
typedef struct D3D12_DESCRIPTOR_HEAP_DESC {
    D3D12_DESCRIPTOR_HEAP_TYPE Type;
    UINT NumDescriptors;
    D3D12_DESCRIPTOR_HEAP_FLAGS Flags;
    UINT NodeMask;
} D3D12_DESCRIPTOR_HEAP_DESC;
```

ディスクリプタを並べて置くヒープを、どんな種類でいくつ作るかを決めます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `Type` | `D3D12_DESCRIPTOR_HEAP_TYPE` | `CBV_SRV_UAV`、`SAMPLER`、`RTV`、`DSV` のどれか |
| `NumDescriptors` | `UINT` | ヒープに置けるディスクリプタの数 |
| `Flags` | `D3D12_DESCRIPTOR_HEAP_FLAGS` | `NONE` か `SHADER_VISIBLE` |
| `NodeMask` | `UINT` | GPU が 1 つなら 0 |

`Type` は 1 つのヒープに 1 種類だけです。CBV・SRV・UAV は同じヒープに混ぜられますが、サンプラー、RTV、DSV は別々のヒープが要ります。ディスクリプタ 1 つの大きさが種類ごとに違うので、`NumDescriptors` と合わせて、ヒープの大きさが決まります。

`Flags` の `SHADER_VISIBLE` は「シェーダー（GPU）から見える」ヒープを意味します。コマンド リストに `SetDescriptorHeaps` で渡せるのは、このフラグ付きのヒープだけです。付けられるのは `CBV_SRV_UAV` と `SAMPLER` だけで、`RTV` と `DSV` に付けると作成が失敗します。シェーダー可視のヒープはメモリが限られるので、数を無駄に大きくしないようにします。

`NodeMask` は GPU が 1 つなら 0 です。

```cpp
D3D12_DESCRIPTOR_HEAP_DESC desc = {};
desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_RTV;
desc.NumDescriptors = 2;                      // ダブル バッファ
desc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_NONE; // RTV は SHADER_VISIBLE にできない
HRESULT hr = device->CreateDescriptorHeap(&desc, IID_PPV_ARGS(&rtv_heap));
```

### D3D12_CPU_DESCRIPTOR_HANDLE {#d3d12_cpu_descriptor_handle}

```cpp
typedef struct D3D12_CPU_DESCRIPTOR_HANDLE {
    SIZE_T ptr;
} D3D12_CPU_DESCRIPTOR_HANDLE;
```

ディスクリプタ ヒープの中の、CPU から書き込む位置を表します。メンバーは `ptr` が 1 つだけで、中身はメモリのアドレスのような数値です。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `ptr` | `SIZE_T` | ヒープ内の位置を表す数値 |

ヒープの先頭は `GetCPUDescriptorHandleForHeapStart()` で取ります。n 番目の位置は、`ptr` に `n × 増分` を足します。増分はドライバーごとに違うので、`ID3D12Device::GetDescriptorHandleIncrementSize` で種類ごとに調べます。固定の値（32 など）を決め打ちしてはいけません。

この足し算は [`OffsetHandle`](../util.md#offsethandle) に任せます。

```cpp
UINT rtv_size = device->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_RTV);
D3D12_CPU_DESCRIPTOR_HANDLE rtv0 = rtv_heap->GetCPUDescriptorHandleForHeapStart();
D3D12_CPU_DESCRIPTOR_HANDLE rtv1 = OffsetHandle(rtv0, 1, rtv_size);  // 1 番目
```

### D3D12_GPU_DESCRIPTOR_HANDLE {#d3d12_gpu_descriptor_handle}

```cpp
typedef struct D3D12_GPU_DESCRIPTOR_HANDLE {
    UINT64 ptr;
} D3D12_GPU_DESCRIPTOR_HANDLE;
```

シェーダー可視のヒープの中の、GPU が読む位置を表します。ルート シグネチャのディスクリプタ テーブルへ、「この位置から始まる」と教えるために使います。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `ptr` | `UINT64` | ヒープ内の位置を表す数値 |

`ptr` が 64 ビット固定なのは、CPU のハンドルと違って GPU の仮想アドレス空間にあるからです。`GetGPUDescriptorHandleForHeapStart()` で取れるのは、`SHADER_VISIBLE` のヒープだけで、そうでないヒープで呼ぶと 0 が返ります。CPU のハンドルと同じ増分で、`OffsetHandle` で n 番目を求められます。

CPU のハンドルと GPU のハンドルは別の型で、互いに代入できません。書き込むときは CPU、`SetGraphicsRootDescriptorTable` に渡すときは GPU、と使い分けます。

!!! failure "よくあるミス"
    - 増分を固定の数値にして、別の GPU で壊れる。
    - RTV のヒープを `SHADER_VISIBLE` にして作成に失敗する。
    - `SHADER_VISIBLE` でないヒープの GPU ハンドルを使う。

## ビューの形

### D3D12_RENDER_TARGET_VIEW_DESC {#d3d12_render_target_view_desc}

```cpp
typedef struct D3D12_RENDER_TARGET_VIEW_DESC {
    DXGI_FORMAT Format;
    D3D12_RTV_DIMENSION ViewDimension;
    union {
        D3D12_BUFFER_RTV Buffer;
        D3D12_TEX1D_RTV Texture1D;
        D3D12_TEX1D_ARRAY_RTV Texture1DArray;
        D3D12_TEX2D_RTV Texture2D;
        D3D12_TEX2D_ARRAY_RTV Texture2DArray;
        D3D12_TEX2DMS_RTV Texture2DMS;
        D3D12_TEX2DMS_ARRAY_RTV Texture2DMSArray;
        D3D12_TEX3D_RTV Texture3D;
    };
} D3D12_RENDER_TARGET_VIEW_DESC;
```

テクスチャを「描き込み先」として見るときの形を決めます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `Format` | `DXGI_FORMAT` | ビューの形式。`UNKNOWN` ならリソースの形式 |
| `ViewDimension` | `D3D12_RTV_DIMENSION` | `TEXTURE2D`、`TEXTURE2DARRAY` など |
| `Texture2D.MipSlice` | `UINT` | 描き込むミップ レベル |
| `Texture2D.PlaneSlice` | `UINT` | 通常は 0（平面形式のためのもの） |

`ViewDimension` を決めると、共用体の中で使うメンバーが決まります。普通の 2D レンダー ターゲットなら `D3D12_RTV_DIMENSION_TEXTURE2D` にして、`Texture2D` の `MipSlice`（普通は 0）を書きます。配列の特定のスライスに描くときは `TEXTURE2DARRAY` にして、`FirstArraySlice` と `ArraySize` を決めます。

`Format` は、typeless のリソースに RTV を作るときに必要です。たとえば `R8G8B8A8_TYPELESS` のテクスチャに `R8G8B8A8_UNORM_SRGB` で RTV を作ると、書き込み時に sRGB への変換が自動で行われます。

スワップ チェーンのバック バッファなどでリソースの形式がそのまま使えるなら、`CreateRenderTargetView` の第 2 引数に `nullptr` を渡すこともできます。そのときはこの構造体を作らなくて済みます。

```cpp
D3D12_RENDER_TARGET_VIEW_DESC rtv = {};
rtv.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
rtv.ViewDimension = D3D12_RTV_DIMENSION_TEXTURE2D;
rtv.Texture2D.MipSlice = 0;
device->CreateRenderTargetView(back_buffer, &rtv, rtv_handle);
```

### D3D12_DEPTH_STENCIL_VIEW_DESC {#d3d12_depth_stencil_view_desc}

```cpp
typedef struct D3D12_DEPTH_STENCIL_VIEW_DESC {
    DXGI_FORMAT Format;
    D3D12_DSV_DIMENSION ViewDimension;
    D3D12_DSV_FLAGS Flags;
    union {
        D3D12_TEX1D_DSV Texture1D;
        D3D12_TEX1D_ARRAY_DSV Texture1DArray;
        D3D12_TEX2D_DSV Texture2D;
        D3D12_TEX2D_ARRAY_DSV Texture2DArray;
        D3D12_TEX2DMS_DSV Texture2DMS;
        D3D12_TEX2DMS_ARRAY_DSV Texture2DMSArray;
    };
} D3D12_DEPTH_STENCIL_VIEW_DESC;
```

深度バッファの形を決めます。RTV と似ていますが、`Flags` があります。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `Format` | `DXGI_FORMAT` | `D32_FLOAT`、`D24_UNORM_S8_UINT` など深度の形式 |
| `ViewDimension` | `D3D12_DSV_DIMENSION` | `TEXTURE2D` など |
| `Flags` | `D3D12_DSV_FLAGS` | `NONE`、`READ_ONLY_DEPTH`、`READ_ONLY_STENCIL` |
| `Texture2D.MipSlice` | `UINT` | ミップ レベル。普通は 0 |

`Format` には、深度の書ける形式を指定します。リソースが `R32_TYPELESS` なら `D32_FLOAT` です。

`Flags` の `READ_ONLY_DEPTH` は、深度を「読み取り専用」で使う DSV にします。同じ深度バッファをシェーダーで読みながら、深度テストにも使いたいとき（ソフト パーティクルなど）に、この DSV と SRV を同時に使えます。通常は `NONE` です。

### D3D12_SHADER_RESOURCE_VIEW_DESC {#d3d12_shader_resource_view_desc}

```cpp
typedef struct D3D12_SHADER_RESOURCE_VIEW_DESC {
    DXGI_FORMAT Format;
    D3D12_SRV_DIMENSION ViewDimension;
    UINT Shader4ComponentMapping;
    union {
        D3D12_BUFFER_SRV Buffer;
        D3D12_TEX1D_SRV Texture1D;
        D3D12_TEX1D_ARRAY_SRV Texture1DArray;
        D3D12_TEX2D_SRV Texture2D;
        D3D12_TEX2D_ARRAY_SRV Texture2DArray;
        D3D12_TEX2DMS_SRV Texture2DMS;
        D3D12_TEX2DMS_ARRAY_SRV Texture2DMSArray;
        D3D12_TEX3D_SRV Texture3D;
        D3D12_TEXCUBE_SRV TextureCube;
        D3D12_TEXCUBE_ARRAY_SRV TextureCubeArray;
        D3D12_RAYTRACING_ACCELERATION_STRUCTURE_SRV RaytracingAccelerationStructure;
    };
} D3D12_SHADER_RESOURCE_VIEW_DESC;
```

シェーダーがテクスチャやバッファを読むときの形を決めます。メンバーが多いのは、読み方の種類が多いからです。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `Format` | `DXGI_FORMAT` | 読むときの形式 |
| `ViewDimension` | `D3D12_SRV_DIMENSION` | `TEXTURE2D`、`TEXTURECUBE`、`BUFFER` など |
| `Shader4ComponentMapping` | `UINT` | R、G、B、A をどの成分から読むか |
| `Texture2D.MostDetailedMip` | `UINT` | 見える最も詳細なミップ |
| `Texture2D.MipLevels` | `UINT` | 見えるミップの数。`-1`（`UINT_MAX`）は、すべて |
| `Texture2D.PlaneSlice` | `UINT` | 通常は 0 |
| `Texture2D.ResourceMinLODClamp` | `FLOAT` | これ未満の詳細度へは下げない。通常は 0 |

`Shader4ComponentMapping` は、必ず設定します。0 のままだと、すべての成分が成分 0（R）から読まれて、おかしな見た目になります。通常は `D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING`（R、G、B、A の順そのまま）を入れます。成分を入れ替えたい（例えば 1 チャンネルのテクスチャを、RGB すべてに広げる）ときだけ、`D3D12_ENCODE_SHADER_4_COMPONENT_MAPPING` で組み立てます。

`MipLevels` に `UINT_MAX`（`-1`）を入れると、`MostDetailedMip` から最後までのすべてを見ます。0 や、実際の数を超える値は、作成の失敗になります。

深度バッファを SRV として読むときは、`Format` を深度の読める形式にします（`D32_FLOAT` のリソースなら `R32_FLOAT`）。

```cpp
D3D12_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
srv.ViewDimension = D3D12_SRV_DIMENSION_TEXTURE2D;
srv.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;
srv.Texture2D.MostDetailedMip = 0;
srv.Texture2D.MipLevels = static_cast<UINT>(-1);  // すべてのミップ
device->CreateShaderResourceView(texture, &srv, srv_handle);
```

!!! failure "よくあるミス"
    - `Shader4ComponentMapping` が 0 のままで、テクスチャが 1 色に見える。
    - `Texture2D.MipLevels` を 0 のままにして、作成が失敗する。
    - `ViewDimension` と違うメンバーを埋めている。

### D3D12_UNORDERED_ACCESS_VIEW_DESC {#d3d12_unordered_access_view_desc}

```cpp
typedef struct D3D12_UNORDERED_ACCESS_VIEW_DESC {
    DXGI_FORMAT Format;
    D3D12_UAV_DIMENSION ViewDimension;
    union {
        D3D12_BUFFER_UAV Buffer;
        D3D12_TEX1D_UAV Texture1D;
        D3D12_TEX1D_ARRAY_UAV Texture1DArray;
        D3D12_TEX2D_UAV Texture2D;
        D3D12_TEX2D_ARRAY_UAV Texture2DArray;
        D3D12_TEX2DMS_UAV Texture2DMS;
        D3D12_TEX2DMS_ARRAY_UAV Texture2DMSArray;
        D3D12_TEX3D_UAV Texture3D;
    };
} D3D12_UNORDERED_ACCESS_VIEW_DESC;
```

コンピュート シェーダーなどが、読み書きの両方に使うビューの形を決めます。リソースの `Flags` に `ALLOW_UNORDERED_ACCESS` が必要です。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `Format` | `DXGI_FORMAT` | 形式。構造化バッファは `UNKNOWN` |
| `ViewDimension` | `D3D12_UAV_DIMENSION` | `BUFFER`、`TEXTURE2D` など |
| `Texture2D.MipSlice` | `UINT` | 対象のミップ レベル |
| `Texture2D.PlaneSlice` | `UINT` | 通常は 0 |
| `Buffer.FirstElement` | `UINT64` | 先頭の要素番号 |
| `Buffer.NumElements` | `UINT` | 要素の数 |
| `Buffer.StructureByteStride` | `UINT` | 構造化バッファの 1 要素のバイト数。構造化でなければ 0 |
| `Buffer.CounterOffsetInBytes` | `UINT64` | カウンターの位置。使わなければ 0 |
| `Buffer.Flags` | `D3D12_BUFFER_UAV_FLAGS` | `NONE` か `RAW` |

UAV は SRV と違い、ミップを 1 つだけ選びます。範囲は選べません。バッファでは、`Format` が `UNKNOWN` で `StructureByteStride` が 0 以外なら構造化バッファ、`Flags` が `RAW` で `Format` が `R32_TYPELESS` ならバイト アドレス バッファになります。カウンターを使わないなら、`CreateUnorderedAccessView` の 2 番目の引数（カウンター用リソース）は `nullptr` にします。

### D3D12_CONSTANT_BUFFER_VIEW_DESC {#d3d12_constant_buffer_view_desc}

```cpp
typedef struct D3D12_CONSTANT_BUFFER_VIEW_DESC {
    D3D12_GPU_VIRTUAL_ADDRESS BufferLocation;
    UINT SizeInBytes;
} D3D12_CONSTANT_BUFFER_VIEW_DESC;
```

定数バッファのどこからどこまでを、シェーダーが見るかを決めます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `BufferLocation` | `D3D12_GPU_VIRTUAL_ADDRESS` | 先頭の GPU 仮想アドレス。256 の倍数 |
| `SizeInBytes` | `UINT` | 範囲の大きさ。256 の倍数 |

`BufferLocation` は `ID3D12Resource::GetGPUVirtualAddress()` で取った値に、バッファの中のオフセットを足したものです。256 バイトの倍数でない位置を指定すると、作成に失敗します。`SizeInBytes` も 256 の倍数に切り上げます。1 つの大きな定数バッファに複数のオブジェクト分を並べて、オブジェクトごとに 256 バイトずつずらした CBV を作るのは、定番のやり方です。

## 頂点バッファとインデックス バッファ

### D3D12_VERTEX_BUFFER_VIEW {#d3d12_vertex_buffer_view}

```cpp
typedef struct D3D12_VERTEX_BUFFER_VIEW {
    D3D12_GPU_VIRTUAL_ADDRESS BufferLocation;
    UINT SizeInBytes;
    UINT StrideInBytes;
} D3D12_VERTEX_BUFFER_VIEW;
```

頂点バッファをコマンド リストに伝えます。ディスクリプタ ヒープは使わず、構造体をそのまま `IASetVertexBuffers` に渡します。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `BufferLocation` | `D3D12_GPU_VIRTUAL_ADDRESS` | 先頭の GPU 仮想アドレス |
| `SizeInBytes` | `UINT` | バッファ全体のバイト数 |
| `StrideInBytes` | `UINT` | 頂点 1 つのバイト数 |

`StrideInBytes` は、頂点の構造体の `sizeof` です。入力レイアウトに書いた各要素の合計と合わなくても、エラーになるとは限らず、描かれた絵だけが壊れます。`SizeInBytes` は頂点数ではなくバイト数です。

```cpp
D3D12_VERTEX_BUFFER_VIEW vbv = {};
vbv.BufferLocation = vertex_buffer->GetGPUVirtualAddress();
vbv.SizeInBytes = static_cast<UINT>(sizeof(Vertex) * vertices.size());
vbv.StrideInBytes = sizeof(Vertex);
command_list->IASetVertexBuffers(0, 1, &vbv);
```

### D3D12_INDEX_BUFFER_VIEW {#d3d12_index_buffer_view}

```cpp
typedef struct D3D12_INDEX_BUFFER_VIEW {
    D3D12_GPU_VIRTUAL_ADDRESS BufferLocation;
    UINT SizeInBytes;
    DXGI_FORMAT Format;
} D3D12_INDEX_BUFFER_VIEW;
```

インデックス バッファを、`IASetIndexBuffer` に伝えます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `BufferLocation` | `D3D12_GPU_VIRTUAL_ADDRESS` | 先頭の GPU 仮想アドレス |
| `SizeInBytes` | `UINT` | バッファ全体のバイト数 |
| `Format` | `DXGI_FORMAT` | `R16_UINT` か `R32_UINT` |

`Format` はインデックス 1 つの大きさです。実際のデータが 16 ビットなら `R16_UINT`、32 ビットなら `R32_UINT` にします。食い違うと、頂点がめちゃくちゃにつながります。`R16_UINT` で表せる頂点は 65,536 個までです。

!!! failure "よくあるミス"
    - `StrideInBytes` が `sizeof(Vertex)` と違う。
    - `SizeInBytes` に要素数を入れる。
    - インデックスが 16 ビットなのに `R32_UINT` を指定する。

## サンプラー

### D3D12_SAMPLER_DESC {#d3d12_sampler_desc}

```cpp
typedef struct D3D12_SAMPLER_DESC {
    D3D12_FILTER Filter;
    D3D12_TEXTURE_ADDRESS_MODE AddressU;
    D3D12_TEXTURE_ADDRESS_MODE AddressV;
    D3D12_TEXTURE_ADDRESS_MODE AddressW;
    FLOAT MipLODBias;
    UINT MaxAnisotropy;
    D3D12_COMPARISON_FUNC ComparisonFunc;
    FLOAT BorderColor[4];
    FLOAT MinLOD;
    FLOAT MaxLOD;
} D3D12_SAMPLER_DESC;
```

テクスチャを読むときの補間や、範囲外の扱いを決めます。サンプラー ヒープにディスクリプタとして書き込みます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `Filter` | `D3D12_FILTER` | 補間の方法（ポイント、リニア、異方性、比較） |
| `AddressU`、`AddressV`、`AddressW` | `D3D12_TEXTURE_ADDRESS_MODE` | 0〜1 の外側の扱い |
| `MipLODBias` | `FLOAT` | ミップ選択へのかたより。通常は 0 |
| `MaxAnisotropy` | `UINT` | 異方性フィルタの最大値（1〜16） |
| `ComparisonFunc` | `D3D12_COMPARISON_FUNC` | 比較サンプラーの比較。通常は `NEVER` |
| `BorderColor` | `FLOAT[4]` | `BORDER` のときの色 |
| `MinLOD`、`MaxLOD` | `FLOAT` | 使えるミップの範囲 |

`Filter` は見た目と重さの両方を決めます。`MIN_MAG_MIP_POINT` は最も軽く、ドット絵向けです。`MIN_MAG_MIP_LINEAR` が標準で、`ANISOTROPIC` は斜めから見る床がぼやけにくくなります。`ANISOTROPIC` を選んだときだけ `MaxAnisotropy` が使われます。

`AddressU/V/W` は、UV が 0〜1 の外へ出たときの動きです。`WRAP` は繰り返し、`CLAMP` は端の色を伸ばし、`MIRROR` は鏡のように折り返し、`BORDER` は `BorderColor` を使います。

`MaxLOD` を 0 にすると、ミップマップの最も詳細なレベルしか使われず、遠くが粗くなります。ミップを全部使うなら `D3D12_FLOAT32_MAX` です。ゼロ初期化のまま忘れやすいメンバーです。

```cpp
D3D12_SAMPLER_DESC sampler = {};
sampler.Filter = D3D12_FILTER_MIN_MAG_MIP_LINEAR;
sampler.AddressU = D3D12_TEXTURE_ADDRESS_MODE_WRAP;
sampler.AddressV = D3D12_TEXTURE_ADDRESS_MODE_WRAP;
sampler.AddressW = D3D12_TEXTURE_ADDRESS_MODE_WRAP;
sampler.MaxAnisotropy = 1;
sampler.ComparisonFunc = D3D12_COMPARISON_FUNC_NEVER;
sampler.MinLOD = 0.0f;
sampler.MaxLOD = D3D12_FLOAT32_MAX;   // 0 のままだとミップが効かない
device->CreateSampler(&sampler, sampler_handle);
```

### D3D12_STATIC_SAMPLER_DESC {#d3d12_static_sampler_desc}

```cpp
typedef struct D3D12_STATIC_SAMPLER_DESC {
    D3D12_FILTER Filter;
    D3D12_TEXTURE_ADDRESS_MODE AddressU;
    D3D12_TEXTURE_ADDRESS_MODE AddressV;
    D3D12_TEXTURE_ADDRESS_MODE AddressW;
    FLOAT MipLODBias;
    UINT MaxAnisotropy;
    D3D12_COMPARISON_FUNC ComparisonFunc;
    D3D12_STATIC_BORDER_COLOR BorderColor;
    FLOAT MinLOD;
    FLOAT MaxLOD;
    UINT ShaderRegister;
    UINT RegisterSpace;
    D3D12_SHADER_VISIBILITY ShaderVisibility;
} D3D12_STATIC_SAMPLER_DESC;
```

サンプラーを、ディスクリプタ ヒープではなくルート シグネチャの中に埋め込む形です。サンプラーの設定が固定なら、ヒープを用意しなくてよいので、最もよく使います。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `Filter` から `ComparisonFunc` | （上の表と同じ） | `D3D12_SAMPLER_DESC` と同じ |
| `BorderColor` | `D3D12_STATIC_BORDER_COLOR` | `TRANSPARENT_BLACK`、`OPAQUE_BLACK`、`OPAQUE_WHITE` の 3 つだけ |
| `MinLOD`、`MaxLOD` | `FLOAT` | 使えるミップの範囲 |
| `ShaderRegister` | `UINT` | シェーダーの `s0` などの番号 |
| `RegisterSpace` | `UINT` | 通常は 0 |
| `ShaderVisibility` | `D3D12_SHADER_VISIBILITY` | どのステージから見えるか。通常は `ALL` か `PIXEL` |

`D3D12_SAMPLER_DESC` との違いは、境界色が 3 つの定数に限られる点と、シェーダー側のレジスタを指定する 3 つのメンバーが加わる点です。`ShaderRegister` は HLSL の `register(s0)` の `0` に対応します。`ShaderVisibility` はサンプラーを使うステージにだけ絞ると、無駄が減ります。ピクセル シェーダーでしか使わないなら `PIXEL` です。

静的サンプラーは、ルート シグネチャの `pStaticSamplers` に配列で渡します。

## 関連ページ

- [ID3D12Device](id3d12device.md) — `CreateXxxView`、`CreateSampler`
- [ID3D12DescriptorHeap](id3d12descriptorheap.md) — ハンドルの取得
- [Descriptor](../descriptor.md) — ディスクリプタの全体像
- [Descriptor Heap](../descriptor-heap.md) — ヒープの使い方
- [Vertex and Index Buffer Views](../vertex-index-view.md) — 頂点バッファの使い方
- [Constant Buffer (D3D12)](../constant-buffer.md) — 256 バイトのアラインメント
