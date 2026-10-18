---
title: Heaps and Resources
tags:
  - DirectX
---

# Heaps and Resources

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

D3D12 ではリソース（バッファ、テクスチャ）を作るとき <strong>GPU メモリのどこに置くか</strong>（ヒープの種類）を自分で、選びます。CPU から書き込みたい物は <strong>アップロード ヒープ</strong>、GPU が速く読み書きする物は <strong>デフォルト ヒープ</strong>、GPU の結果を CPU が読む物は、<strong>リードバック ヒープ</strong>、というふうに使い分けます。この選択が D3D12 のメモリ管理の基本です。

!!! tip "ポイント"
    - リソース ＝ GPU メモリ上のバッファ・テクスチャ。作るときに <strong>ヒープの種類</strong>を指定する。
    - ヒープは 3 種類: <strong>DEFAULT</strong>（GPU 専用。最速）、<strong>UPLOAD</strong>（CPU 書き込み → GPU 読み取り）、<strong>READBACK</strong>（GPU 書き込み → CPU 読み取り）。
    - 簡単な作り方は `CreateCommittedResource`（リソースごとに専用のヒープを作る）。
    - 描画に使うメッシュ・テクスチャは、<strong>アップロード ヒープに書き DEFAULT ヒープへコピー</strong>する（[Upload Buffer](upload-buffer.md)）。
    - 作成時にリソースの<strong>初期状態</strong>を指定する（[Resource Barrier](resource-barrier.md)）。

## 3 種類のヒープ

| `D3D12_HEAP_TYPE_*` | 置き場所 | CPU | GPU | 使いどころ |
| --- | --- | --- | --- | --- |
| `DEFAULT` | GPU 専用メモリ（VRAM） | アクセス不可 | 読み書き（最速） | メッシュ、テクスチャ、レンダー ターゲット、深度、UAV |
| `UPLOAD` | CPU から見えるメモリ | 書き込み（`Map`） | 読み取り（やや遅い） | 毎フレームの、定数バッファ、アップロード用の一時バッファ |
| `READBACK` | CPU から見えるメモリ | 読み取り | 書き込み（コピー先） | GPU の結果の、読み出し（スクリーンショット、ピッキング） |
| `CUSTOM` | 細かく指定 | — | — | 上級（統合 GPU の最適化） |

<strong>CPU が DEFAULT ヒープに直接、書けません</strong>。メッシュやテクスチャを DEFAULT に置くには UPLOAD ヒープの、一時バッファに書いて GPU のコピー命令で DEFAULT へ送ります。

## CreateCommittedResource：最も簡単な作り方

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
| `pDesc` | リソースの記述（バッファかテクスチャか大きさフォーマット、フラグ） |
| `InitialResourceState` | 作成直後の状態（[Resource Barrier](resource-barrier.md)） |
| `pOptimizedClearValue` | レンダー ターゲット・深度のクリア値（最適化のヒント。指定しておくとクリアが速い） |

`CreateCommittedResource` はリソースごとに <strong>専用のヒープを割り当て</strong>ます。簡単ですがリソースが数千個になると、割り当てが重く断片化します。大量のリソースは 1 つの大きなヒープに並べる <strong>配置リソース</strong>（`CreatePlacedResource`）やアロケーター ライブラリ（D3D12 Memory Allocator）を、使います。

## リソースの記述

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
| `ALLOW_RENDER_TARGET` | RTV を作れる（レンダー ターゲット） |
| `ALLOW_DEPTH_STENCIL` | DSV を作れる（深度） |
| `ALLOW_UNORDERED_ACCESS` | UAV を作れる |
| `DENY_SHADER_RESOURCE` | SRV を作れない（深度だけのバッファの最適化） |
| `ALLOW_SIMULTANEOUS_ACCESS` | 複数のキューが同時にアクセス |

<strong>使う予定のビューの種類のフラグを作成時に付けます</strong>。付けなかった種類のディスクリプタは作れません（[Descriptor](descriptor.md)）。

## クリア値の最適化

レンダー ターゲット・深度は作成時に <strong>最適化されたクリア値</strong>を渡せます。この値と同じ値でクリアすると高速なパスが、使えます。違う値でクリアしても動きますが、デバッグ レイヤーが警告を出します。

```cpp
D3D12_CLEAR_VALUE depth_clear = {};
depth_clear.Format = DXGI_FORMAT_D32_FLOAT;
depth_clear.DepthStencil.Depth = 1.0f;                                         // reverse-Z なら 0.0f
depth_clear.DepthStencil.Stencil = 0;

device->CreateCommittedResource(&default_heap, D3D12_HEAP_FLAG_NONE, &depth_desc,
                                D3D12_RESOURCE_STATE_DEPTH_WRITE, &depth_clear, IID_PPV_ARGS(&depth_buffer));
```

## Map：CPU から読み書きする

アップロード・リードバック ヒープのリソースは `Map` で CPU から見える、ポインターを得ます。

```cpp
// アップロード ヒープの、リソースを、Map して、書き込む。
uint8_t* mapped = nullptr;
CD3DX12_RANGE read_range(0, 0);                               // CPU は、読まない（書き込みだけ）
upload_buffer->Map(0, &read_range, reinterpret_cast<void**>(&mapped));
std::memcpy(mapped, data, size);
upload_buffer->Unmap(0, nullptr);
```

<strong>アップロード ヒープは `Map` したまま使い続けて</strong>よい（毎フレーム、`Map`/`Unmap` しなくてよい）。永続的に `Map` したポインターに書き込めば GPU がそのまま読みます。ただし、GPU が読んでいる間は書き換えない（フレームごとに別の領域に書く。[Frame Resources](frame-resources.md)）。

| ヒープ | `Map` |
| --- | --- |
| `UPLOAD` | 書き込み用。`read_range` は `(0, 0)`（読まないと宣言） |
| `READBACK` | 読み取り用。読む範囲を `read_range` で指定 |
| `DEFAULT` | `Map` できない |

## ヒープ内の配置（Placed Resource）

大量のリソースを効率よく作るには <strong>大きなヒープを 1 つ作り</strong>、その中にリソースを並べます。

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

配置リソースは <strong>メモリの節約</strong>（使わない、一時バッファを同じ位置に重ねるエイリアシング）や <strong>作成の高速化</strong>に使います。細かい管理が必要なので最初は `CreateCommittedResource` で、十分です。

## メモリの予算

```cpp
// GPU メモリの、使用量と、予算を、取る（DXGI）。
DXGI_QUERY_VIDEO_MEMORY_INFO info;
adapter3->QueryVideoMemoryInfo(0, DXGI_MEMORY_SEGMENT_GROUP_LOCAL, &info);
// info.Budget: OS が、このアプリに、許す量、info.CurrentUsage: 今の、使用量
```

D3D12 は <strong>メモリが足りなくなっても自動で、退避しません</strong>。予算を見てテクスチャの解像度を下げるなどの対処は、アプリが行います。

## よくあるミス

??? failure "DEFAULT ヒープのリソースを `Map` して失敗する"
    DEFAULT ヒープは CPU から見えない。UPLOAD ヒープに書いて、コピーする。

??? failure "リソースのビューが作れない（`CreateRenderTargetView` など）"
    作成時に `ALLOW_RENDER_TARGET`・`ALLOW_UNORDERED_ACCESS` などのフラグを付けていない。

??? failure "UPLOAD ヒープのリソースに初期状態 `COPY_DEST` を指定して、失敗する"
    UPLOAD ヒープは `GENERIC_READ` が固定。

??? failure "クリア値が違うという警告が大量に出る"
    作成時の最適化クリア値と `ClearRenderTargetView` の値が違う。そろえる。

??? failure "リソースの作成が、遅い（数千個）"
    `CreateCommittedResource` を大量に呼んでいる。大きなヒープに配置する（`CreatePlacedResource`）、またはアロケーター ライブラリを使う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ヒープの種類を自分で選ぶ: DEFAULT（GPU 専用）、UPLOAD（CPU 書き込み）、READBACK（CPU 読み取り）
    - [x] CPU は DEFAULT に書けない。UPLOAD に書いて GPU の命令で、コピーする
    - [x] `CreateCommittedResource` が最も簡単。初期状態を指定する
    - [x] 使うビューのフラグ（`ALLOW_*`）を作成時に付ける
    - [x] UPLOAD は、`Map` したまま使える。GPU が読む間は書き換えない
    - [x] 大量なら配置リソース（`CreatePlacedResource`）

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Upload Buffer](upload-buffer.md)
- [Resource Barrier](resource-barrier.md)
- [Descriptor](descriptor.md)
- [Microsoft Learn: ID3D12Device::CreateCommittedResource](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nf-d3d12-id3d12device-createcommittedresource)
