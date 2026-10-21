---
title: ID3D12Heap
tags:
  - DirectX
api:
  - ID3D12Heap
---

# ID3D12Heap

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

リソースを 1 つ作るたびに GPU のメモリを確保すると、小さな確保が大量に並び、遅くてメモリも無駄になります。そこで、大きなメモリの塊を先に 1 つ確保して、その中にリソースを並べて置く方法があります。この塊が `ID3D12Heap` です。

`CreateCommittedResource` はヒープとリソースを同時に作ります。`ID3D12Heap` は、それを分けて、先にヒープだけを作る（`CreateHeap`）ためのオブジェクトです。リソースは `CreatePlacedResource` でヒープの中の好きな位置に置きます。使い終わったリソースの場所へ別のリソースを重ねて置けるので、一時的にしか使わない大きなテクスチャのメモリを使い回せます。

メソッドは、作ったときの記述子を読み戻す `GetDesc` の 1 つです。

!!! tip "ポイント"
    - ヒープは `CreateHeap`、そこに置くリソースは `CreatePlacedResource`。
    - 同じ場所に重ねて置いたリソースは、同時には使えない（エイリアシング）。切り替えにバリアが要る。
    - ヒープの種類（DEFAULT、UPLOAD、READBACK）と、置けるリソースの種類（バッファ、テクスチャ、レンダー ターゲット）は作るときに決まる。

!!! info "このページを読む前に"
    コミテッドとプレースドの違いは [Heaps and Resources](../heaps-resources.md) にあります。作るメソッドは [ID3D12Device](id3d12device.md#createheap) です。

## メソッド一覧

| メソッド | 役割 |
| --- | --- |
| [`GetDesc`](#getdesc) | ヒープを作ったときの記述子を返す |

## メソッドの詳しい説明

### GetDesc {#getdesc}

```cpp
D3D12_HEAP_DESC ID3D12Heap::GetDesc();
```

`CreateHeap` に渡した記述子（`D3D12_HEAP_DESC`）を返します。引数はありません。

`D3D12_HEAP_DESC` には、ヒープの大きさ（`SizeInBytes`）、種類を含む `Properties`、置くときの境界（`Alignment`）、`Flags`（置けるリソースの種類）が入っています。作ったあとでその値が必要になったとき（ヒープの大きさを超えて置こうとしていないか確かめる、など）に使います。

```cpp
D3D12_HEAP_DESC desc = heap->GetDesc();
if (offset + resource_size > desc.SizeInBytes) {
  // ヒープからはみ出す
}
```

値を返す関数で、失敗しません。

## 関連ページ

- [Heaps and Resources](../heaps-resources.md)
- [ID3D12Device](id3d12device.md#createheap)
- [ID3D12Resource](id3d12resource.md)
- [Microsoft Learn: ID3D12Heap](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12heap)
