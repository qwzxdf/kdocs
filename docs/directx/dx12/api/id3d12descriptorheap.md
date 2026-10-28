---
title: ID3D12DescriptorHeap
tags:
  - DirectX
api:
  - ID3D12DescriptorHeap
---

# ID3D12DescriptorHeap

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

ディスクリプタ ヒープはディスクリプタ（リソースの「見方」を書いた小さなデータ）を 1 列に並べておく置き場です。ディスクリプタを書き込む位置は「先頭から何番目か」で決まります。その先頭の位置を教えてくれるのが、このインターフェースのメソッドです。

位置は**CPU から書き込むとき**に使うハンドル（CPU ハンドル）と、**GPU のシェーダーが読むとき**に使うハンドル（GPU ハンドル）の 2 種類があります。見かけが似ていますが取り違えるとクラッシュするので、使い分けが大切です。

!!! tip "ポイント"
    - 書き込むとき（`CreateXxxView`、`CopyDescriptors`）は CPU ハンドル。
    - ルート引数に渡すとき（`SetGraphicsRootDescriptorTable`）は GPU ハンドル。
    - GPU ハンドルを取れるのは、`SHADER_VISIBLE` のヒープだけ。
    - 先頭から数えて n 番目のハンドルは、先頭に `n × 増分` を足して求める。

!!! info "このページを読む前に"
    ヒープの作り方と種類は [ID3D12Device::CreateDescriptorHeap](id3d12device.md#createdescriptorheap)、ディスクリプタの考え方は [Descriptor Heap](../descriptor-heap.md) と [Descriptor](../descriptor.md) で説明しています。

## メソッド一覧

| メソッド | 役割 |
| --- | --- |
| [`GetCPUDescriptorHandleForHeapStart`](#getcpudescriptorhandleforheapstart) | CPU が書くときの先頭の位置 |
| [`GetGPUDescriptorHandleForHeapStart`](#getgpudescriptorhandleforheapstart) | シェーダーが読むときの先頭の位置 |
| [`GetDesc`](#getdesc) | ヒープを作ったときの設定 |

## メソッド

### GetCPUDescriptorHandleForHeapStart {#getcpudescriptorhandleforheapstart}

```cpp
D3D12_CPU_DESCRIPTOR_HANDLE ID3D12DescriptorHeap::GetCPUDescriptorHandleForHeapStart();
```

ヒープの先頭の CPU ハンドルを返します。引数はありません。

`CreateRenderTargetView` や `CreateShaderResourceView` の最後の引数（書き込み先）には、このハンドルに位置のぶんを足したものを渡します。位置を足すには `ptr` に「位置 × 幅」を足します（[Helper Functions](../util.md#offsethandle) の `OffsetHandle`）。1 つぶんの幅は `GetDescriptorHandleIncrementSize` で調べます。

```cpp
D3D12_CPU_DESCRIPTOR_HANDLE start = rtv_heap->GetCPUDescriptorHandleForHeapStart();
for (UINT i = 0; i < frame_count; ++i) {
  D3D12_CPU_DESCRIPTOR_HANDLE handle = OffsetHandle(start, i, rtv_increment);  // i 番目のスロット
  device->CreateRenderTargetView(back_buffers[i].Get(), nullptr, handle);
}
```

`SHADER_VISIBLE` でないヒープでも CPU ハンドルは使えます。RTV と DSV のヒープはシェーダーから見えないので、CPU ハンドルしかありません。

### GetGPUDescriptorHandleForHeapStart {#getgpudescriptorhandleforheapstart}

```cpp
D3D12_GPU_DESCRIPTOR_HANDLE ID3D12DescriptorHeap::GetGPUDescriptorHandleForHeapStart();
```

ヒープの先頭の GPU ハンドルを返します。引数はありません。

`SetGraphicsRootDescriptorTable` のようにシェーダーが読むディスクリプタの位置を伝える関数には、こちらを渡します。`D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE` を付けて作ったヒープに対してだけ有効な値が返ります。付けていないヒープに呼ぶと無効な値（0）が返ります。

GPU ハンドルも先頭に「位置 × 増分」を足して、n 番目を求めます（GPU ハンドル用の `OffsetHandle`）。CPU ハンドルと GPU ハンドルは、同じ位置を指していても**数値は違います**。片方で作ったハンドルをもう片方の引数に渡してはいけません。

### GetDesc {#getdesc}

```cpp
D3D12_DESCRIPTOR_HEAP_DESC ID3D12DescriptorHeap::GetDesc();
```

ヒープを作ったときの設定（`Type`、`NumDescriptors`、`Flags`、`NodeMask`）を返します。ヒープを渡された関数が種類や大きさを知りたいときに使います。

## 関連ページ

- [Descriptor Heap](../descriptor-heap.md)
- [ID3D12Device](id3d12device.md)
- [ID3D12GraphicsCommandList](id3d12graphicscommandlist.md)
- [Microsoft Learn: ID3D12DescriptorHeap](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12descriptorheap)
