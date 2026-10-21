---
title: ID3D12QueryHeap
tags:
  - DirectX
api:
  - ID3D12QueryHeap
---

# ID3D12QueryHeap

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

GPU の処理に何ミリ秒かかったか、何個のピクセルが描かれたか。こうした GPU の中の数字は、CPU からは直接測れません。GPU に頼んで、時刻や数を記録してもらいます。その記録先が、クエリ ヒープ（`ID3D12QueryHeap`）です。

このインターフェースに自分のメソッドはありません。作るのは `ID3D12Device::CreateQueryHeap`、記録は `BeginQuery` と `EndQuery`、結果の取り出しは `ResolveQueryData` で、どれもほかのオブジェクトのメソッドです。ヒープは「記録の置き場」だけを受け持ちます。

!!! tip "ポイント"
    - 作るときに `Type`（TIMESTAMP、OCCLUSION など）と `Count`（記録できる数）を決める。
    - 記録は `EndQuery`（タイムスタンプなら `EndQuery` だけ）。結果は `ResolveQueryData` で READBACK のバッファへ。
    - 結果を読むのは GPU が終わってから。数フレーム遅らせて読む。

!!! info "このページを読む前に"
    計測の流れ全体は [GPU Queries and Timing (D3D12)](../query-timing.md) にあります。

## 種類

`D3D12_QUERY_HEAP_DESC::Type` で記録の種類を決めます。

| `Type` | 記録するもの |
| --- | --- |
| `D3D12_QUERY_HEAP_TYPE_TIMESTAMP` | 時刻（DIRECT と COMPUTE のキュー） |
| `D3D12_QUERY_HEAP_TYPE_COPY_QUEUE_TIMESTAMP` | 時刻（COPY のキュー） |
| `D3D12_QUERY_HEAP_TYPE_OCCLUSION` | 深度テストを通ったサンプルの数 |
| `D3D12_QUERY_HEAP_TYPE_PIPELINE_STATISTICS` | 頂点やピクセル シェーダーの呼び出し数などの統計 |
| `D3D12_QUERY_HEAP_TYPE_SO_STATISTICS` | ストリーム アウトプットの統計 |

`Count` は、そのヒープに記録できる数です。1 フレームに記録する数に、飛ばして読むフレーム数を掛けた分より多く確保します。

## 作って使う

```cpp
D3D12_QUERY_HEAP_DESC heap_desc = {};
heap_desc.Type = D3D12_QUERY_HEAP_TYPE_TIMESTAMP;
heap_desc.Count = 64;
ComPtr<ID3D12QueryHeap> query_heap;
device->CreateQueryHeap(&heap_desc, IID_PPV_ARGS(&query_heap));

command_list->EndQuery(query_heap.Get(), D3D12_QUERY_TYPE_TIMESTAMP, 0);   // 開始の時刻
// ... 測りたい処理 ...
command_list->EndQuery(query_heap.Get(), D3D12_QUERY_TYPE_TIMESTAMP, 1);   // 終了の時刻
command_list->ResolveQueryData(query_heap.Get(), D3D12_QUERY_TYPE_TIMESTAMP, 0, 2,
                               readback_buffer.Get(), 0);
```

`CreateQueryHeap` は [ID3D12Device](id3d12device.md#createqueryheap)、`EndQuery` と `ResolveQueryData` は [ID3D12GraphicsCommandList](id3d12graphicscommandlist.md#endquery) にあります。

## 関連ページ

- [GPU Queries and Timing (D3D12)](../query-timing.md)
- [ID3D12Device](id3d12device.md#createqueryheap)
- [ID3D12GraphicsCommandList](id3d12graphicscommandlist.md#endquery)
- [Microsoft Learn: ID3D12QueryHeap](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12queryheap)
