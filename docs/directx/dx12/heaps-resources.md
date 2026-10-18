---
title: Heaps and Resources
tags:
  - DirectX
---

# Heaps and Resources

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

D3D12 では、リソース（バッファ、テクスチャ）を、作るとき、<strong>GPU メモリの、どこに、置くか</strong>（ヒープの種類）を、自分で、選びます。CPU から、書き込みたい物は、<strong>アップロード ヒープ</strong>、GPU が、速く、読み書きする物は、<strong>デフォルト ヒープ</strong>、GPU の結果を、CPU が、読む物は、<strong>リードバック ヒープ</strong>、というふうに、使い分けます。この選択が、D3D12 の、メモリ管理の、基本です。

!!! tip "ポイント"
    - リソース ＝ GPU メモリ上の、バッファ・テクスチャ。作るときに、<strong>ヒープの種類</strong>を、指定する。
    - ヒープは 3 種類: <strong>DEFAULT</strong>（GPU 専用。最速）、<strong>UPLOAD</strong>（CPU 書き込み → GPU 読み取り）、<strong>READBACK</strong>（GPU 書き込み → CPU 読み取り）。
    - 簡単な作り方は `CreateCommittedResource`（リソースごとに、専用の、ヒープを、作る）。
    - 描画に使う、メッシュ・テクスチャは、<strong>アップロード ヒープに書き、DEFAULT ヒープへ、コピー</strong>する（[Upload Buffer](upload-buffer.md)）。
    - 作成時に、リソースの<strong>初期状態</strong>を、指定する（[Resource Barrier](resource-barrier.md)）。

## 3 種類の、ヒープ

| `D3D12_HEAP_TYPE_*` | 置き場所 | CPU | GPU | 使いどころ |
| --- | --- | --- | --- | --- |
| `DEFAULT` | GPU 専用メモリ（VRAM） | アクセス不可 | 読み書き（最速） | メッシュ、テクスチャ、レンダー ターゲット、深度、UAV |
| `UPLOAD` | CPU から見える、メモリ | 書き込み（`Map`） | 読み取り（やや遅い） | 毎フレームの、定数バッファ、アップロード用の、一時バッファ |
| `READBACK` | CPU から見える、メモリ | 読み取り | 書き込み（コピー先） | GPU の結果の、読み出し（スクリーンショット、ピッキング） |
| `CUSTOM` | 細かく、指定 | — | — | 上級（統合 GPU の最適化） |

<strong>CPU が、DEFAULT ヒープに、直接、書けません</strong>。メッシュや、テクスチャを、DEFAULT に、置くには、UPLOAD ヒープの、一時バッファに、書いて、GPU の、コピー命令で、DEFAULT へ、送ります。

## CreateCommittedResource：最も、簡単な、作り方

```cpp
// 頂点バッファ用の、DEFAULT ヒープの、リソース（GPU 専用）。
const UINT64 buffer_size = sizeof(vertices);
auto heap_properties = CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_DEFAULT);
auto resource_desc = CD3DX12_RESOURCE_DESC::Buffer(buffer_size);

ComPtr<ID3D12Resource> vertex_buffer;
device->CreateCommittedResource(&heap_properties,
                                D3D12_HEAP_FLAG_NONE,
                                &resource_desc,
                                D3D12_RESOURCE_STATE_COPY_DEST,       // 初期状態: これからコピーで、書き込む
                                nullptr,                               // クリア値（レンダー ターゲット・深度のとき）
                                IID_PPV_ARGS(&vertex_buffer));
```

| 引数 | 内容 |
| --- | --- |
| `pHeapProperties` | ヒープの種類（`DEFAULT`、`UPLOAD`、`READBACK`） |
| `HeapFlags` | 通常 `NONE`。`ALLOW_ONLY_BUFFERS` など |
| `pDesc` | リソースの記述（バッファか、テクスチャか、大きさ、フォーマット、フラグ） |
| `InitialResourceState` | 作成直後の、状態（[Resource Barrier](resource-barrier.md)） |
| `pOptimizedClearValue` | レンダー ターゲット・深度の、クリア値（最適化のヒント。指定しておくと、クリアが速い） |

`CreateCommittedResource` は、リソースごとに、<strong>専用の、ヒープを、割り当て</strong>ます。簡単ですが、リソースが、数千個になると、割り当てが、重く、断片化します。大量の、リソースは、1 つの、大きなヒープに、並べる、<strong>配置リソース</strong>（`CreatePlacedResource`）や、アロケーター ライブラリ（D3D12 Memory Allocator）を、使います。

## リソースの、記述

### バッファ

```cpp
auto desc = CD3DX12_RESOURCE_DESC::Buffer(size_in_bytes);                     // 大きさだけ
auto uav_desc = CD3DX12_RESOURCE_DESC::Buffer(size_in_bytes, D3D12_RESOURCE_FLAG_ALLOW_UNORDERED_ACCESS);   // UAV 可
```

### テクスチャ

```cpp
auto desc = CD3DX12_RESOURCE_DESC::Tex2D(DXGI_FORMAT_R8G8B8A8_UNORM,
                                         width, height,
                                         1,                    // 配列の長さ
                                         1,                    // ミップの数（0 で全段）
                                         1, 0,                 // サンプル数、品質
                                         D3D12_RESOURCE_FLAG_NONE);
```

| フラグ（`D3D12_RESOURCE_FLAG_*`） | 内容 |
| --- | --- |
| `ALLOW_RENDER_TARGET` | RTV を、作れる（レンダー ターゲット） |
| `ALLOW_DEPTH_STENCIL` | DSV を、作れる（深度） |
| `ALLOW_UNORDERED_ACCESS` | UAV を、作れる |
| `DENY_SHADER_RESOURCE` | SRV を、作れない（深度だけの、バッファの、最適化） |
| `ALLOW_SIMULTANEOUS_ACCESS` | 複数のキューが、同時に、アクセス |

<strong>使う予定の、ビューの、種類の、フラグを、作成時に、付けます</strong>。付けなかった、種類の、ディスクリプタは、作れません（[Descriptor](descriptor.md)）。

## クリア値の、最適化

レンダー ターゲット・深度は、作成時に、<strong>最適化された、クリア値</strong>を、渡せます。この値と、同じ値で、クリアすると、高速な、パスが、使えます。違う値でクリアしても、動きますが、デバッグ レイヤーが、警告を、出します。

```cpp
D3D12_CLEAR_VALUE depth_clear = {};
depth_clear.Format = DXGI_FORMAT_D32_FLOAT;
depth_clear.DepthStencil.Depth = 1.0f;                                         // reverse-Z なら 0.0f
depth_clear.DepthStencil.Stencil = 0;

device->CreateCommittedResource(&default_heap, D3D12_HEAP_FLAG_NONE, &depth_desc,
                                D3D12_RESOURCE_STATE_DEPTH_WRITE, &depth_clear, IID_PPV_ARGS(&depth_buffer));
```

## Map：CPU から、読み書きする

アップロード・リードバック ヒープの、リソースは、`Map` で、CPU から、見える、ポインターを、得ます。

```cpp
// アップロード ヒープの、リソースを、Map して、書き込む。
uint8_t* mapped = nullptr;
CD3DX12_RANGE read_range(0, 0);                               // CPU は、読まない（書き込みだけ）
upload_buffer->Map(0, &read_range, reinterpret_cast<void**>(&mapped));
std::memcpy(mapped, data, size);
upload_buffer->Unmap(0, nullptr);
```

<strong>アップロード ヒープは、`Map` したまま、使い続けて</strong>よい（毎フレーム、`Map`/`Unmap` しなくてよい）。永続的に、`Map` した、ポインターに、書き込めば、GPU が、そのまま、読みます。ただし、GPU が、読んでいる間は、書き換えない（フレームごとに、別の領域に、書く。[Frame Resources](frame-resources.md)）。

| ヒープ | `Map` |
| --- | --- |
| `UPLOAD` | 書き込み用。`read_range` は、`(0, 0)`（読まないと、宣言） |
| `READBACK` | 読み取り用。読む範囲を、`read_range` で、指定 |
| `DEFAULT` | `Map` できない |

## ヒープ内の、配置（Placed Resource）

大量の、リソースを、効率よく、作るには、<strong>大きなヒープを、1 つ作り</strong>、その中に、リソースを、並べます。

```cpp
// 64 MB のヒープを 1 つ作る。
D3D12_HEAP_DESC heap_desc = {};
heap_desc.SizeInBytes = 64 * 1024 * 1024;
heap_desc.Properties = CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_DEFAULT);
heap_desc.Alignment = D3D12_DEFAULT_RESOURCE_PLACEMENT_ALIGNMENT;             // 64 KB
heap_desc.Flags = D3D12_HEAP_FLAG_ALLOW_ONLY_RT_DS_TEXTURES;
ComPtr<ID3D12Heap> heap;
device->CreateHeap(&heap_desc, IID_PPV_ARGS(&heap));

// ヒープの、指定位置に、リソースを置く。
device->CreatePlacedResource(heap.Get(), offset, &desc, initial_state, nullptr, IID_PPV_ARGS(&resource));
```

配置リソースは、<strong>メモリの、節約</strong>（使わない、一時バッファを、同じ位置に、重ねる、エイリアシング）や、<strong>作成の、高速化</strong>に、使います。細かい管理が、必要なので、最初は、`CreateCommittedResource` で、十分です。

## メモリの、予算

```cpp
// GPU メモリの、使用量と、予算を、取る（DXGI）。
DXGI_QUERY_VIDEO_MEMORY_INFO info;
adapter3->QueryVideoMemoryInfo(0, DXGI_MEMORY_SEGMENT_GROUP_LOCAL, &info);
// info.Budget: OS が、このアプリに、許す量、info.CurrentUsage: 今の、使用量
```

D3D12 は、<strong>メモリが、足りなくなっても、自動で、退避しません</strong>。予算を、見て、テクスチャの、解像度を、下げる、などの、対処は、アプリが、行います。

## よくあるミス

??? failure "DEFAULT ヒープの、リソースを、`Map` して、失敗する"
    DEFAULT ヒープは、CPU から、見えない。UPLOAD ヒープに、書いて、コピーする。

??? failure "リソースの、ビューが、作れない（`CreateRenderTargetView` など）"
    作成時に、`ALLOW_RENDER_TARGET`・`ALLOW_UNORDERED_ACCESS` などの、フラグを、付けていない。

??? failure "UPLOAD ヒープの、リソースに、初期状態 `COPY_DEST` を、指定して、失敗する"
    UPLOAD ヒープは、`GENERIC_READ` が、固定。

??? failure "クリア値が、違う、という警告が、大量に出る"
    作成時の、最適化クリア値と、`ClearRenderTargetView` の、値が、違う。そろえる。

??? failure "リソースの作成が、遅い（数千個）"
    `CreateCommittedResource` を、大量に、呼んでいる。大きな、ヒープに、配置する（`CreatePlacedResource`）、または、アロケーター ライブラリを、使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ヒープの種類を、自分で選ぶ: DEFAULT（GPU 専用）、UPLOAD（CPU 書き込み）、READBACK（CPU 読み取り）
    - [x] CPU は、DEFAULT に、書けない。UPLOAD に書いて、GPU の命令で、コピーする
    - [x] `CreateCommittedResource` が、最も簡単。初期状態を、指定する
    - [x] 使うビューの、フラグ（`ALLOW_*`）を、作成時に、付ける
    - [x] UPLOAD は、`Map` したまま、使える。GPU が、読む間は、書き換えない
    - [x] 大量なら、配置リソース（`CreatePlacedResource`）

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Upload Buffer](upload-buffer.md)
- [Resource Barrier](resource-barrier.md)
- [Descriptor](descriptor.md)
- [Microsoft Learn: ID3D12Device::CreateCommittedResource](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nf-d3d12-id3d12device-createcommittedresource)
