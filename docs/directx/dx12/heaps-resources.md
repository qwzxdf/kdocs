---
title: Heaps and Resources
tags:
  - DirectX
---

# Heaps and Resources

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

GPU には CPU のメモリとは別に専用のメモリ（VRAM）があります。VRAM は GPU からはとても速い代わりに CPU からは直接触れません。CPU から見える普通のメモリは書きやすい代わりに GPU からは少し遅くなります。D3D12 ではバッファやテクスチャ（リソース）を作るとき「どちらのメモリに置くか」を自分で決めます。

置き場所の選択肢はヒープの種類として決まっています。CPU が書いて GPU が読むものは UPLOAD、GPU だけが使うものは DEFAULT、GPU が書いて CPU が読むものは READBACK です。この使い分けが D3D12 のメモリ管理の基本です。

!!! tip "ポイント"
    - リソースを作るときにヒープの種類（置き場所）を指定する。
    - ヒープは 3 種類。DEFAULT は GPU 専用で最速、UPLOAD は CPU が書いて GPU が読む READBACK は GPU が書いて CPU が読む。
    - 簡単な作り方は `CreateCommittedResource`。リソースごとに専用のヒープを作る。
    - 描画に使うメッシュとテクスチャは、UPLOAD に書いてから DEFAULT へコピーする（[Upload Buffer](upload-buffer.md)）。
    - 作るときにリソースの初期状態も指定する（[Resource Barrier](resource-barrier.md)）。

!!! info "このページを読む前に"
    リソースの状態は [Resource Barrier](resource-barrier.md)、アップロードの流れは [Upload Buffer](upload-buffer.md) で説明しています。作るメソッドの引数と戻り値は [ID3D12Device](api/id3d12device.md#createcommittedresource)、作ったあとのメソッドは [ID3D12Resource](api/id3d12resource.md) にあります。構造体を短く書く関数は [Helper Functions](util.md) です。

## 3 種類のヒープ

DEFAULT は GPU 専用のメモリ（VRAM）です。CPU からは見えません。GPU からは最速で読み書きできるので、メッシュ、テクスチャ、レンダー ターゲット、深度バッファ、UAV など描画に使うほとんどのものはここに置きます。

UPLOAD は CPU から見えるメモリです。CPU が `Map` で書き込み GPU は読み取りだけできます。GPU からの読み取りは DEFAULT より遅くなります。毎フレーム書き換える定数バッファや DEFAULT へ送るための一時バッファに使います。

READBACK は同じく CPU から見えるメモリで、GPU が書いた結果を CPU が読みます。スクリーンショットやピッキングの結果を読み出すときに使います。ほかに `CUSTOM` という細かく指定する種類もありますが、統合 GPU の最適化などの上級の使い方なので、ここでは扱いません。

**CPU は DEFAULT のヒープに直接書けません。** メッシュやテクスチャを DEFAULT へ置くには、いったん UPLOAD のバッファに書いて、GPU のコピー命令で DEFAULT へ送ります。

## CreateCommittedResource でリソースを作る

一番簡単な作り方が `CreateCommittedResource` です。

```cpp
// 頂点バッファ用の DEFAULT のリソース（GPU 専用）。
const UINT64 buffer_size = sizeof(vertices);
D3D12_HEAP_PROPERTIES heap_properties = MakeHeapProperties(D3D12_HEAP_TYPE_DEFAULT);
D3D12_RESOURCE_DESC resource_desc = MakeBufferDesc(buffer_size);

ComPtr<ID3D12Resource> vertex_buffer;
device->CreateCommittedResource(&heap_properties,
                                D3D12_HEAP_FLAG_NONE,
                                &resource_desc,
                                D3D12_RESOURCE_STATE_COPY_DEST,  // 初期状態。これからコピーで書き込む
                                nullptr,                         // クリア値（レンダー ターゲットと深度のとき）
                                IID_PPV_ARGS(&vertex_buffer));
```

引数は置き場所（`pHeapProperties`）、ヒープの性質（`HeapFlags`）、リソースの中身（`pDesc`）、初期状態、クリア値、受け取る先の順です。1 つずつの意味は [ID3D12Device::CreateCommittedResource](api/id3d12device.md#createcommittedresource) で詳しく説明しています。

この関数はリソースごとに専用のヒープを割り当てます。簡単な代わりにリソースが数千個になると、割り当てが重くなりメモリも断片化します。大量のリソースを作るときは 1 つの大きなヒープに並べる配置リソース（`CreatePlacedResource`）か、アロケーターのライブラリ（D3D12 Memory Allocator など）を使います。

## リソースの記述

### バッファ

バッファは大きさだけを決めます。UAV として使うならフラグを付けます。

```cpp
D3D12_RESOURCE_DESC desc = MakeBufferDesc(size_in_bytes);  // 大きさだけ
D3D12_RESOURCE_DESC uav_desc = MakeBufferDesc(size_in_bytes, D3D12_RESOURCE_FLAG_ALLOW_UNORDERED_ACCESS);  // UAV 可
```

### テクスチャ

テクスチャは形式、幅、高さミップの数、配列の長さを決めます。

```cpp
D3D12_RESOURCE_DESC desc = MakeTexture2DDesc(DXGI_FORMAT_R8G8B8A8_UNORM, width, height,
                                             1,   // ミップの数（0 で全段）
                                             1);  // 配列の長さ
```

作るときに使う予定のビューのフラグを付けておきます。付けなかった種類のビューはあとから作れません（[Descriptor](descriptor.md)）。`ALLOW_RENDER_TARGET` は RTV を `ALLOW_DEPTH_STENCIL` は DSV を `ALLOW_UNORDERED_ACCESS` は UAV を作れるようにします。

`DENY_SHADER_RESOURCE` は SRV を作れなくするフラグで、深度だけに使うバッファの最適化になります。`ALLOW_SIMULTANEOUS_ACCESS` は複数のキューから同時にアクセスするときに付けます。

## クリア値を伝えておく

レンダー ターゲットと深度バッファは、作るときに最適化のためのクリア値を渡せます。同じ値でクリアすると GPU の高速なクリアが使えます。違う値でクリアしても動きますが、デバッグ レイヤーが警告を出します。

```cpp
D3D12_CLEAR_VALUE depth_clear = {};
depth_clear.Format = DXGI_FORMAT_D32_FLOAT;
depth_clear.DepthStencil.Depth = 1.0f;  // リバース Z なら 0.0f
depth_clear.DepthStencil.Stencil = 0;

device->CreateCommittedResource(&default_heap, D3D12_HEAP_FLAG_NONE, &depth_desc,
                                D3D12_RESOURCE_STATE_DEPTH_WRITE, &depth_clear, IID_PPV_ARGS(&depth_buffer));
```

## Map で CPU から読み書きする

UPLOAD と READBACK のリソースは、`Map` を呼ぶと CPU から触れるポインターが得られます。

```cpp
// UPLOAD のリソースを Map して、書き込む。
uint8_t* mapped = nullptr;
D3D12_RANGE read_range = {0, 0};  // CPU は読まない（書き込むだけ）
upload_buffer->Map(0, &read_range, reinterpret_cast<void**>(&mapped));
std::memcpy(mapped, data, size);
upload_buffer->Unmap(0, nullptr);
```

UPLOAD のヒープは `Map` したまま使い続けて構いません。毎フレーム `Map` と `Unmap` を繰り返す必要はなく、永続的にマップしたポインターへ書き込めば、GPU がそのまま読みます。ただし、GPU が読んでいる間は同じ場所を書き換えません。フレームごとに別の領域へ書きます（[Frame Resources](frame-resources.md)）。

UPLOAD は書き込み用なので、`read_range` は `{0, 0}`（読まない）にします。READBACK は読み取り用なので、読む範囲を `read_range` で指定します。DEFAULT は `Map` できません。

## ヒープの中に置く（配置リソース）

大量のリソースを効率よく作るには大きなヒープを 1 つ作って、その中にリソースを並べます。

```cpp
// 64 MB のヒープを 1 つ作る。
D3D12_HEAP_DESC heap_desc = {};
heap_desc.SizeInBytes = 64 * 1024 * 1024;
heap_desc.Properties = MakeHeapProperties(D3D12_HEAP_TYPE_DEFAULT);
heap_desc.Alignment = D3D12_DEFAULT_RESOURCE_PLACEMENT_ALIGNMENT;  // 64 KB
heap_desc.Flags = D3D12_HEAP_FLAG_ALLOW_ONLY_RT_DS_TEXTURES;
ComPtr<ID3D12Heap> heap;
device->CreateHeap(&heap_desc, IID_PPV_ARGS(&heap));

// ヒープの指定位置にリソースを置く。
device->CreatePlacedResource(heap.Get(), offset, &desc, initial_state, nullptr, IID_PPV_ARGS(&resource));
```

配置リソースはメモリの節約（使わない時間が重ならない一時バッファを同じ位置に重ねる）と、作成の高速化に役立ちます。ただし、管理が細かくなるので最初は `CreateCommittedResource` で十分です（[ID3D12Device::CreatePlacedResource](api/id3d12device.md#createplacedresource)）。

## メモリの予算を確認する

```cpp
// GPU メモリの使用量と、OS が許す予算を取る（DXGI）。
DXGI_QUERY_VIDEO_MEMORY_INFO info;
adapter3->QueryVideoMemoryInfo(0, DXGI_MEMORY_SEGMENT_GROUP_LOCAL, &info);
// info.Budget は OS がこのアプリに許す量、info.CurrentUsage は今の使用量。
```

D3D12 はメモリが足りなくなっても、自動では退避してくれません。予算を見てテクスチャの解像度を下げるなどの対処は、アプリが行います。

## よくあるミス

??? failure "DEFAULT のリソースを `Map` して失敗する"
    DEFAULT は CPU から見えません。UPLOAD に書いてコピーします。

??? failure "ビュー（`CreateRenderTargetView` など）が作れない"
    作るときに `ALLOW_RENDER_TARGET` や `ALLOW_UNORDERED_ACCESS` のフラグを付けていません。

??? failure "UPLOAD のリソースに初期状態 `COPY_DEST` を指定して失敗する"
    UPLOAD のヒープは `GENERIC_READ` で固定です。

??? failure "クリア値が違うという警告が大量に出る"
    作るときの最適化クリア値と `ClearRenderTargetView` の値が違います。そろえます。

??? failure "リソースの作成が遅い（数千個作る）"
    `CreateCommittedResource` を大量に呼んでいます。大きなヒープに配置するかアロケーターのライブラリを使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ヒープの種類を自分で選ぶ。DEFAULT は GPU 専用、UPLOAD は CPU 書き込み READBACK は CPU 読み取り
    - [x] CPU は DEFAULT に書けない。UPLOAD に書いて GPU の命令でコピーする
    - [x] `CreateCommittedResource` が最も簡単。初期状態を指定する
    - [x] 使うビューのフラグ（`ALLOW_*`）を作るときに付ける
    - [x] UPLOAD は `Map` したまま使える。GPU が読む間は書き換えない
    - [x] 大量なら配置リソース（`CreatePlacedResource`）を使う

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3D12Device](api/id3d12device.md)
- [ID3D12Resource](api/id3d12resource.md)
- [Upload Buffer](upload-buffer.md)
- [Resource Barrier](resource-barrier.md)
- [Descriptor](descriptor.md)
- [Microsoft Learn: ID3D12Device::CreateCommittedResource](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nf-d3d12-id3d12device-createcommittedresource)
