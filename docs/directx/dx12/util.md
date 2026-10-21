---
title: Helper Functions
tags:
  - DirectX
api:
  - dx12_util.h
---

# Helper Functions

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
`#include "dx12_util.h"`
</div>

D3D12 の構造体はフィールドが多くて、ほとんどの値は決まりきっています。たとえば、バッファを 1 つ作るために `D3D12_RESOURCE_DESC` を埋めると、書く必要があるのは `Width` だけなのに `Height = 1`、`MipLevels = 1`、`SampleDesc.Count = 1` など 11 個のフィールドをすべて決めなければなりません。1 つでも間違えると `CreateCommittedResource` が `E_INVALIDARG` で失敗します。

マイクロソフトの `d3dx12.h` にはこれを短く書くための `CD3DX12_*` が入っています。ただ、フィールドが隠れてしまうので、「この構造体の何が設定されているのか」が、読んでいても分かりません。このサイトでは `d3dx12.h` を使わず**素の構造体**を使います。そのうえで、毎回同じになる部分だけをこのページの小さな関数にまとめます。

!!! tip "ポイント"
    - `d3dx12.h` は使わない。構造体は素の `D3D12_*` を書く。
    - 毎回同じになる組み立てだけを `dx12_util.h` の関数にする。関数の中身はすべてこのページに載っている。
    - 関数は構造体を返すだけ。副作用も隠れた設定もない。
    - 名前は `Make...`。`Make` で始まる関数は構造体を作って返す。

!!! info "このページを読む前に"
    構造体のフィールドの意味は使うページ（[ID3D12Device](api/id3d12device.md)、[ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md)、[Heaps and Resources](heaps-resources.md)、[PSO](pso.md)）で説明しています。このページはそれらを短く書くための道具です。

## 関数一覧

| 関数 | 作る物 | 使う場面 |
| --- | --- | --- |
| [`MakeHeapProperties`](#makeheapproperties) | `D3D12_HEAP_PROPERTIES` | リソースを作る |
| [`MakeBufferDesc`](#makebufferdesc) | バッファの `D3D12_RESOURCE_DESC` | 頂点・定数バッファなどを作る |
| [`MakeTexture2DDesc`](#maketexture2ddesc) | 2D テクスチャの `D3D12_RESOURCE_DESC` | テクスチャ、深度バッファを作る |
| [`MakeTransitionBarrier`](#maketransitionbarrier) | 遷移バリア | 状態を切り替える |
| [`MakeUavBarrier`](#makeuavbarrier) | UAV バリア | 書き込みの完了を待つ |
| [`OffsetHandle`](#offsethandle) | ハンドル | ヒープの n 番目のディスクリプタ |
| [`MakeDefaultRasterizerDesc`](#makedefaultrasterizerdesc) | `D3D12_RASTERIZER_DESC` | PSO |
| [`MakeDefaultBlendDesc`](#makedefaultblenddesc) | `D3D12_BLEND_DESC` | PSO |
| [`MakeDefaultDepthStencilDesc`](#makedefaultdepthstencildesc) | `D3D12_DEPTH_STENCIL_DESC` | PSO |

## ヘッダー全体

```cpp
#pragma once

#include <d3d12.h>

// このセクションで使う、小さな補助関数。d3dx12.h は使わない。

// ヒープの置き場所（DEFAULT / UPLOAD / READBACK）から、D3D12_HEAP_PROPERTIES を作る。
inline D3D12_HEAP_PROPERTIES MakeHeapProperties(D3D12_HEAP_TYPE type) {
  D3D12_HEAP_PROPERTIES props = {};
  props.Type = type;
  props.CPUPageProperty = D3D12_CPU_PAGE_PROPERTY_UNKNOWN;
  props.MemoryPoolPreference = D3D12_MEMORY_POOL_UNKNOWN;
  props.CreationNodeMask = 1;
  props.VisibleNodeMask = 1;
  return props;
}

// 大きさ size バイトのバッファの D3D12_RESOURCE_DESC を作る。
inline D3D12_RESOURCE_DESC MakeBufferDesc(UINT64 size,
                                          D3D12_RESOURCE_FLAGS flags = D3D12_RESOURCE_FLAG_NONE) {
  D3D12_RESOURCE_DESC desc = {};
  desc.Dimension = D3D12_RESOURCE_DIMENSION_BUFFER;
  desc.Alignment = 0;
  desc.Width = size;
  desc.Height = 1;
  desc.DepthOrArraySize = 1;
  desc.MipLevels = 1;
  desc.Format = DXGI_FORMAT_UNKNOWN;
  desc.SampleDesc.Count = 1;
  desc.SampleDesc.Quality = 0;
  desc.Layout = D3D12_TEXTURE_LAYOUT_ROW_MAJOR;
  desc.Flags = flags;
  return desc;
}

// 2D テクスチャの D3D12_RESOURCE_DESC を作る。mip_levels = 0 は「1x1 までの全ミップ」。
inline D3D12_RESOURCE_DESC MakeTexture2DDesc(DXGI_FORMAT format, UINT64 width, UINT height,
                                             UINT16 mip_levels = 1, UINT16 array_size = 1,
                                             D3D12_RESOURCE_FLAGS flags = D3D12_RESOURCE_FLAG_NONE) {
  D3D12_RESOURCE_DESC desc = {};
  desc.Dimension = D3D12_RESOURCE_DIMENSION_TEXTURE2D;
  desc.Alignment = 0;
  desc.Width = width;
  desc.Height = height;
  desc.DepthOrArraySize = array_size;
  desc.MipLevels = mip_levels;
  desc.Format = format;
  desc.SampleDesc.Count = 1;
  desc.SampleDesc.Quality = 0;
  desc.Layout = D3D12_TEXTURE_LAYOUT_UNKNOWN;
  desc.Flags = flags;
  return desc;
}

// リソースの状態を before から after に切り替える、遷移バリアを作る。
inline D3D12_RESOURCE_BARRIER MakeTransitionBarrier(
    ID3D12Resource* resource, D3D12_RESOURCE_STATES before, D3D12_RESOURCE_STATES after,
    UINT subresource = D3D12_RESOURCE_BARRIER_ALL_SUBRESOURCES) {
  D3D12_RESOURCE_BARRIER barrier = {};
  barrier.Type = D3D12_RESOURCE_BARRIER_TYPE_TRANSITION;
  barrier.Flags = D3D12_RESOURCE_BARRIER_FLAG_NONE;
  barrier.Transition.pResource = resource;
  barrier.Transition.Subresource = subresource;
  barrier.Transition.StateBefore = before;
  barrier.Transition.StateAfter = after;
  return barrier;
}

// UAV バリア（同じリソースへの、書き込みの完了を待つ）を作る。
inline D3D12_RESOURCE_BARRIER MakeUavBarrier(ID3D12Resource* resource) {
  D3D12_RESOURCE_BARRIER barrier = {};
  barrier.Type = D3D12_RESOURCE_BARRIER_TYPE_UAV;
  barrier.Flags = D3D12_RESOURCE_BARRIER_FLAG_NONE;
  barrier.UAV.pResource = resource;
  return barrier;
}

// ヒープの先頭から index 番目のディスクリプタのハンドルを求める。
// increment は GetDescriptorHandleIncrementSize で調べた 1 つ分の幅。
inline D3D12_CPU_DESCRIPTOR_HANDLE OffsetHandle(D3D12_CPU_DESCRIPTOR_HANDLE start, UINT index,
                                                UINT increment) {
  start.ptr += static_cast<SIZE_T>(index) * increment;
  return start;
}

inline D3D12_GPU_DESCRIPTOR_HANDLE OffsetHandle(D3D12_GPU_DESCRIPTOR_HANDLE start, UINT index,
                                                UINT increment) {
  start.ptr += static_cast<UINT64>(index) * increment;
  return start;
}

// 既定のラスタライザー設定（裏面カリング、塗りつぶし）。
// 表を反時計回りにするなら、あとで FrontCounterClockwise = TRUE にする。
inline D3D12_RASTERIZER_DESC MakeDefaultRasterizerDesc() {
  D3D12_RASTERIZER_DESC desc = {};
  desc.FillMode = D3D12_FILL_MODE_SOLID;
  desc.CullMode = D3D12_CULL_MODE_BACK;
  desc.FrontCounterClockwise = FALSE;
  desc.DepthBias = D3D12_DEFAULT_DEPTH_BIAS;
  desc.DepthBiasClamp = D3D12_DEFAULT_DEPTH_BIAS_CLAMP;
  desc.SlopeScaledDepthBias = D3D12_DEFAULT_SLOPE_SCALED_DEPTH_BIAS;
  desc.DepthClipEnable = TRUE;
  desc.MultisampleEnable = FALSE;
  desc.AntialiasedLineEnable = FALSE;
  desc.ForcedSampleCount = 0;
  desc.ConservativeRaster = D3D12_CONSERVATIVE_RASTERIZATION_MODE_OFF;
  return desc;
}

// 既定のブレンド設定（ブレンドなし。上書き）。
inline D3D12_BLEND_DESC MakeDefaultBlendDesc() {
  D3D12_BLEND_DESC desc = {};
  desc.AlphaToCoverageEnable = FALSE;
  desc.IndependentBlendEnable = FALSE;
  for (auto& rt : desc.RenderTarget) {
    rt.BlendEnable = FALSE;
    rt.LogicOpEnable = FALSE;
    rt.SrcBlend = D3D12_BLEND_ONE;
    rt.DestBlend = D3D12_BLEND_ZERO;
    rt.BlendOp = D3D12_BLEND_OP_ADD;
    rt.SrcBlendAlpha = D3D12_BLEND_ONE;
    rt.DestBlendAlpha = D3D12_BLEND_ZERO;
    rt.BlendOpAlpha = D3D12_BLEND_OP_ADD;
    rt.LogicOp = D3D12_LOGIC_OP_NOOP;
    rt.RenderTargetWriteMask = D3D12_COLOR_WRITE_ENABLE_ALL;
  }
  return desc;
}

// 既定の深度・ステンシル設定（深度テストあり、手前ほど小さい値、ステンシルなし）。
inline D3D12_DEPTH_STENCIL_DESC MakeDefaultDepthStencilDesc() {
  D3D12_DEPTH_STENCIL_DESC desc = {};
  desc.DepthEnable = TRUE;
  desc.DepthWriteMask = D3D12_DEPTH_WRITE_MASK_ALL;
  desc.DepthFunc = D3D12_COMPARISON_FUNC_LESS;
  desc.StencilEnable = FALSE;
  desc.StencilReadMask = D3D12_DEFAULT_STENCIL_READ_MASK;
  desc.StencilWriteMask = D3D12_DEFAULT_STENCIL_WRITE_MASK;
  const D3D12_DEPTH_STENCILOP_DESC keep = {D3D12_STENCIL_OP_KEEP, D3D12_STENCIL_OP_KEEP,
                                           D3D12_STENCIL_OP_KEEP, D3D12_COMPARISON_FUNC_ALWAYS};
  desc.FrontFace = keep;
  desc.BackFace = keep;
  return desc;
}
```

## 関数の詳しい説明

### MakeHeapProperties {#makeheapproperties}

```cpp
D3D12_HEAP_PROPERTIES MakeHeapProperties(D3D12_HEAP_TYPE type);
```

リソースをどのメモリに置くかを決める `D3D12_HEAP_PROPERTIES` を作ります。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `type` | `D3D12_HEAP_TYPE` | `DEFAULT`（GPU 専用）、`UPLOAD`（CPU が書く）、`READBACK`（CPU が読む） |

`D3D12_HEAP_PROPERTIES` には 5 つのフィールドがありますが、`Type` を `DEFAULT`、`UPLOAD`、`READBACK` のどれかにしたときは残りの 4 つは決まりきった値になります。`CPUPageProperty` と `MemoryPoolPreference` は `UNKNOWN`（`Type` に任せる）、`CreationNodeMask` と `VisibleNodeMask` は GPU が 1 つなら 1 です。この 4 つを自分で書いて間違えることが多いので、関数にまとめています。

`CUSTOM` のヒープ（`CPUPageProperty` と `MemoryPoolPreference` を自分で決める）は、この関数では作れません。特殊な使い方なので必要なときだけ構造体を自分で埋めます。

### MakeBufferDesc {#makebufferdesc}

```cpp
D3D12_RESOURCE_DESC MakeBufferDesc(
    UINT64 size,
    D3D12_RESOURCE_FLAGS flags = D3D12_RESOURCE_FLAG_NONE);
```

大きさ `size` バイトのバッファを表す `D3D12_RESOURCE_DESC` を作ります。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `size` | `UINT64` | バッファの大きさ（バイト数） |
| `flags` | `D3D12_RESOURCE_FLAGS` | 通常は `NONE`。UAV にするなら `ALLOW_UNORDERED_ACCESS` |

バッファは「幅だけが意味を持つ 1 次元の並び」です。そのため、`Width` が大きさ `Height` と `DepthOrArraySize` と `MipLevels` はすべて 1、`Format` は `UNKNOWN`、`Layout` は `ROW_MAJOR` と決まっています。`Format` を `UNKNOWN` 以外にしたり `Layout` を `ROW_MAJOR` 以外にしたりすると、バッファの作成が失敗します。

定数バッファを作るときは `size` を 256 の倍数に切り上げて渡します。この関数は渡された `size` をそのまま使い切り上げは行いません。

### MakeTexture2DDesc {#maketexture2ddesc}

```cpp
D3D12_RESOURCE_DESC MakeTexture2DDesc(
    DXGI_FORMAT format,
    UINT64 width,
    UINT height,
    UINT16 mip_levels = 1,
    UINT16 array_size = 1,
    D3D12_RESOURCE_FLAGS flags = D3D12_RESOURCE_FLAG_NONE);
```

2D テクスチャ（配列も含む）を表す `D3D12_RESOURCE_DESC` を作ります。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `format` | `DXGI_FORMAT` | ピクセルの形式。`DXGI_FORMAT_R8G8B8A8_UNORM` など |
| `width`、`height` | `UINT64`、`UINT` | 大きさ（ピクセル）。幅は `UINT64`、高さは `UINT` |
| `mip_levels` | `UINT16` | ミップの数。`0` は 1×1 までの全ミップ |
| `array_size` | `UINT16` | 配列の要素数。キューブ マップなら 6 |
| `flags` | `D3D12_RESOURCE_FLAGS` | `ALLOW_RENDER_TARGET`、`ALLOW_DEPTH_STENCIL`、`ALLOW_UNORDERED_ACCESS` など |

`mip_levels` の `0` は特別な値です。そのままでは作れずテクスチャを作るときに GPU が全ミップの数を計算します。作ったあとで本当の数は `GetDesc().MipLevels` で分かります。ミップを 1 つだけにするなら `1` を渡します（既定値です）。

`Layout` は `UNKNOWN`（GPU が決めた並び）にします。`ROW_MAJOR` にできるのはバッファか特殊な使い方に限られます。レンダー ターゲットや深度バッファにするときは、`flags` に `ALLOW_RENDER_TARGET` か `ALLOW_DEPTH_STENCIL` を付けます。付け忘れるとあとでビューを作るときにエラーになります。

### MakeTransitionBarrier {#maketransitionbarrier}

```cpp
D3D12_RESOURCE_BARRIER MakeTransitionBarrier(
    ID3D12Resource* resource,
    D3D12_RESOURCE_STATES before,
    D3D12_RESOURCE_STATES after,
    UINT subresource = D3D12_RESOURCE_BARRIER_ALL_SUBRESOURCES);
```

リソースの状態を `before` から `after` へ切り替える遷移バリアを作ります。`ResourceBarrier` に渡して使います。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `resource` | `ID3D12Resource*` | 対象のリソース |
| `before` | `D3D12_RESOURCE_STATES` | 今の状態。実際の状態と一致していなければならない |
| `after` | `D3D12_RESOURCE_STATES` | 次の状態 |
| `subresource` | `UINT` | 対象のサブリソース。既定はすべて |

`before` はリソースが今実際にある状態と必ず一致させます。一致していないとデバッグ レイヤーがエラーを出します。`subresource` を指定するとミップ 1 枚、または配列の 1 要素だけの状態を切り替えられます。

```cpp
// バックバッファを、表示用から描き込み用へ。
D3D12_RESOURCE_BARRIER barrier = MakeTransitionBarrier(
    back_buffer.Get(), D3D12_RESOURCE_STATE_PRESENT, D3D12_RESOURCE_STATE_RENDER_TARGET);
command_list->ResourceBarrier(1, &barrier);
```

### MakeUavBarrier {#makeuavbarrier}

```cpp
D3D12_RESOURCE_BARRIER MakeUavBarrier(ID3D12Resource* resource);
```

UAV バリアを作ります。引数は対象のリソース 1 つです。同じ UAV に続けて 2 回のコンピュート シェーダーで書き込んで、2 回目が 1 回目の結果を読むとき 1 回目の書き込みの完了を待たせるために、2 回の間に入れます。状態は変わらないので `before` と `after` はありません。

`resource` に `nullptr` を渡すと「すべての UAV」に対するバリアになります。どのリソースが対象か分からないときやまとめて待ちたいときに使えますが、必要以上に待つので重くなります。

### OffsetHandle {#offsethandle}

```cpp
D3D12_CPU_DESCRIPTOR_HANDLE OffsetHandle(
    D3D12_CPU_DESCRIPTOR_HANDLE start, UINT index, UINT increment);

D3D12_GPU_DESCRIPTOR_HANDLE OffsetHandle(
    D3D12_GPU_DESCRIPTOR_HANDLE start, UINT index, UINT increment);
```

ディスクリプタ ヒープの `index` 番目のハンドルを求めます。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `start` | CPU または GPU のハンドル | ヒープの先頭（`GetCPUDescriptorHandleForHeapStart` など） |
| `index` | `UINT` | 先頭から何番目か（0 から） |
| `increment` | `UINT` | ディスクリプタ 1 つの幅。`GetDescriptorHandleIncrementSize` の値 |

ハンドルの中身は `ptr` という整数 1 つだけです。n 番目のハンドルは `ptr` に「n × 幅」を足せば求まります。CPU ハンドルと GPU ハンドルは、別の型なので同じ名前の関数を 2 つ用意して、引数の型で呼び分けています。どちらか片方のハンドルをもう片方の引数に渡すとコンパイルエラーになるので、取り違えを防げます。

```cpp
UINT rtv_increment = device->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_RTV);
D3D12_CPU_DESCRIPTOR_HANDLE rtv_start = rtv_heap->GetCPUDescriptorHandleForHeapStart();
D3D12_CPU_DESCRIPTOR_HANDLE rtv_1 = OffsetHandle(rtv_start, 1, rtv_increment);  // 1 番目
```

### MakeDefaultRasterizerDesc {#makedefaultrasterizerdesc}

```cpp
D3D12_RASTERIZER_DESC MakeDefaultRasterizerDesc();
```

PSO のラスタライザー設定の既定値を返します。

塗りつぶし（`FillMode = SOLID`）、裏面のカリング（`CullMode = BACK`）、深度クリップあり（`DepthClipEnable = TRUE`）、深度バイアスなしが既定です。そのうえで、`FrontCounterClockwise` は `FALSE`、つまり**時計回りが表**の設定になっています。このサイトでは反時計回りを表にするので、PSO を作るときこの関数の戻り値のあとに `FrontCounterClockwise = TRUE` と書きます（[PSO](pso.md)）。

```cpp
D3D12_RASTERIZER_DESC rasterizer = MakeDefaultRasterizerDesc();
rasterizer.FrontCounterClockwise = TRUE;  // このサイトでは、反時計回りが表
```

### MakeDefaultBlendDesc {#makedefaultblenddesc}

```cpp
D3D12_BLEND_DESC MakeDefaultBlendDesc();
```

PSO のブレンド設定の既定値を返します。ブレンドを使わずピクセル シェーダーの出力で、レンダー ターゲットを上書きする設定です。

8 つのレンダー ターゲットすべてに同じ値を入れます。`BlendEnable = FALSE` なので `SrcBlend` と `DestBlend` は使われませんが、値は決まっています（`ONE` と `ZERO`）。`RenderTargetWriteMask` は `ALL`（RGBA の全部を書く）です。アルファ ブレンドを使うときは `RenderTarget[0].BlendEnable = TRUE` にして `SrcBlend = SRC_ALPHA`、`DestBlend = INV_SRC_ALPHA` を設定します。

### MakeDefaultDepthStencilDesc {#makedefaultdepthstencildesc}

```cpp
D3D12_DEPTH_STENCIL_DESC MakeDefaultDepthStencilDesc();
```

PSO の深度・ステンシル設定の既定値を返します。

深度テストあり（`DepthEnable = TRUE`）、深度の書き込みあり（`DepthWriteMask = ALL`）、手前ほど小さい値（`DepthFunc = LESS`）、ステンシルなしの設定です。このとき、PSO の `DSVFormat` を `DXGI_FORMAT_UNKNOWN` にしたままだと深度バッファが使えず PSO の作成が失敗します。深度バッファを使うなら `DSVFormat` に `DXGI_FORMAT_D32_FLOAT` などを必ず指定します。

## `d3dx12.h` との対応

もし、ほかの資料で `d3dx12.h` のコードを見かけたときは、次のように読み替えられます。

| `d3dx12.h` | このサイトの書き方 |
| --- | --- |
| `CD3DX12_HEAP_PROPERTIES(type)` | `MakeHeapProperties(type)` |
| `CD3DX12_RESOURCE_DESC::Buffer(size)` | `MakeBufferDesc(size)` |
| `CD3DX12_RESOURCE_DESC::Tex2D(...)` | `MakeTexture2DDesc(...)` |
| `CD3DX12_RESOURCE_BARRIER::Transition(...)` | `MakeTransitionBarrier(...)` |
| `CD3DX12_RESOURCE_BARRIER::UAV(res)` | `MakeUavBarrier(res)` |
| `CD3DX12_CPU_DESCRIPTOR_HANDLE h(start, n, inc)` | `OffsetHandle(start, n, inc)` |
| `CD3DX12_RASTERIZER_DESC(D3D12_DEFAULT)` | `MakeDefaultRasterizerDesc()` |
| `CD3DX12_RANGE(0, 0)` | `D3D12_RANGE{0, 0}` |
| `UpdateSubresources(...)` | `GetCopyableFootprints` と `CopyTextureRegion`（[Texture Upload](texture-upload.md)） |

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3D12Device](api/id3d12device.md)
- [Resource Barrier](resource-barrier.md)
- [PSO](pso.md)
