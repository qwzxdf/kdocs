---
title: GPU Queries and Timing (D3D12)
tags:
  - DirectX
---

# GPU Queries and Timing (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

GPU の、処理時間を、測るには、<strong>GPU 自身に、時刻を、記録させる</strong>、必要が、あります。CPU の時計では、命令を、記録する、時間しか、測れません。D3D12 では、<strong>クエリ ヒープ</strong>（`ID3D12QueryHeap`）に、タイムスタンプを、書き込み、<strong>`ResolveQueryData`</strong> で、結果を、READBACK の、バッファに、コピーして、CPU で、読みます。

!!! tip "ポイント"
    - タイムスタンプ クエリ ＝ ある瞬間の、GPU の、時刻（チック数）。2 つ（開始・終了）の、差と、周波数で、ミリ秒に、換算。
    - 流れ: <strong>クエリ ヒープを、作る → `EndQuery`（記録）→ `ResolveQueryData`（READBACK バッファへ）→ フェンスで、完了を、確認 → CPU が、`Map` して、読む</strong>。
    - 周波数は、<strong>キューごと</strong>（`GetTimestampFrequency`）。
    - 結果は、数フレーム、遅れて、読む（完了を、待たない）。
    - 本格的な、解析は、PIX、Nsight、Radeon GPU Profiler。

## クエリ ヒープを、作る

```cpp
constexpr UINT kMaxTimestamps = 64;                            // 1 フレームで、記録する、タイムスタンプの数

D3D12_QUERY_HEAP_DESC heap_desc = {};
heap_desc.Type = D3D12_QUERY_HEAP_TYPE_TIMESTAMP;              // タイムスタンプ用
heap_desc.Count = kMaxTimestamps;
ComPtr<ID3D12QueryHeap> query_heap;
device->CreateQueryHeap(&heap_desc, IID_PPV_ARGS(&query_heap));

// 結果を、読むための、READBACK バッファ（タイムスタンプは、各 8 バイト）。
auto readback_heap = CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_READBACK);
auto buffer_desc = CD3DX12_RESOURCE_DESC::Buffer(kMaxTimestamps * sizeof(UINT64));
device->CreateCommittedResource(&readback_heap, D3D12_HEAP_FLAG_NONE, &buffer_desc, D3D12_RESOURCE_STATE_COPY_DEST,
                                nullptr, IID_PPV_ARGS(&readback_buffer));
```

| `D3D12_QUERY_HEAP_TYPE_*` | 内容 |
| --- | --- |
| `TIMESTAMP` | 時刻（DIRECT・COMPUTE キュー） |
| `OCCLUSION` | 通ったピクセル数 |
| `PIPELINE_STATISTICS` | 頂点・ピクセル シェーダーの、呼び出し数など |
| `COPY_QUEUE_TIMESTAMP` | COPY キューの時刻 |

## 時刻を、記録する

```cpp
// 測りたい処理の、前後に、タイムスタンプを、記録する。
command_list->EndQuery(query_heap.Get(), D3D12_QUERY_TYPE_TIMESTAMP, 0);     // インデックス 0: 開始
RunPass();
command_list->EndQuery(query_heap.Get(), D3D12_QUERY_TYPE_TIMESTAMP, 1);     // インデックス 1: 終了
```

D3D12 では、`BeginQuery` は、不要で、タイムスタンプは、`EndQuery` だけで、記録します。複数の、パスを、測るなら、インデックスを、増やします（パス A: 0・1、パス B: 2・3 …）。

## 結果を、READBACK へ

```cpp
// フレームの、最後に、記録した、全クエリを、READBACK バッファへ、コピーする。
command_list->ResolveQueryData(query_heap.Get(), D3D12_QUERY_TYPE_TIMESTAMP,
                               0, used_count,                  // 開始インデックス、個数
                               readback_buffer.Get(), 0);      // コピー先とオフセット
```

`ResolveQueryData` は、GPU の命令で、<strong>コマンド リストに、記録</strong>されます。実際の、コピーは、GPU が、あとで、行います。

## 結果を、読む

```cpp
// 数フレーム後（このフレームの GPU 完了を、フェンスで、確認した後）に、読む。
UINT64 frequency;
command_queue->GetTimestampFrequency(&frequency);              // 1 秒あたりの、チック数

UINT64* timestamps = nullptr;
CD3DX12_RANGE read_range(0, used_count * sizeof(UINT64));
readback_buffer->Map(0, &read_range, reinterpret_cast<void**>(&timestamps));
const double milliseconds = double(timestamps[1] - timestamps[0]) / double(frequency) * 1000.0;
CD3DX12_RANGE no_write(0, 0);
readback_buffer->Unmap(0, &no_write);
```

周波数は、<strong>キューごと</strong>に、違います（`GetTimestampFrequency` は、そのキューの、値）。COMPUTE キューで、測ったなら、COMPUTE キューの、周波数を、使います。

## フレームごとに、別の、領域

CPU が、結果を、読んでいる間に、GPU が、次のフレームの、結果を、同じ場所に、書くと、壊れます。<strong>フレームごとに、別の、READBACK 領域</strong>を、持ち、フレーム イン フライトと、同じ数だけ、用意します（[Frame Resources](frame-resources.md)）。

```cpp
// READBACK バッファを、フレーム数ぶん持つ。このフレームの結果は、kFrameCount フレーム後に、読む。
const UINT slot = frame_number % kFrameCount;
command_list->ResolveQueryData(query_heap.Get(), D3D12_QUERY_TYPE_TIMESTAMP, 0, used_count,
                               readback_buffer.Get(), slot * kMaxTimestamps * sizeof(UINT64));
```

## オクルージョン クエリ

```cpp
D3D12_QUERY_HEAP_DESC heap_desc = {D3D12_QUERY_HEAP_TYPE_OCCLUSION, 256};
// 描画: BeginQuery / EndQuery で囲む。
command_list->BeginQuery(occlusion_heap.Get(), D3D12_QUERY_TYPE_BINARY_OCCLUSION, index);   // 通ったか否か（0 か 1）
DrawBoundingBox();
command_list->EndQuery(occlusion_heap.Get(), D3D12_QUERY_TYPE_BINARY_OCCLUSION, index);
```

`BINARY_OCCLUSION` は、「1 ピクセルでも、通ったか」だけを、返し、`OCCLUSION` は、ピクセル数を、返します。結果は、遅れて、読み、「前のフレームで、隠れていた物は、描かない」運用に、します（[Culling](../../rendering/culling.md)）。

## 本格的な、計測

| ツール | 特徴 |
| --- | --- |
| PIX on Windows | 無料。D3D12 の標準。GPU カウンター、タイミング、シェーダーの、デバッグ |
| NVIDIA Nsight Graphics | NVIDIA の GPU カウンター、シェーダー プロファイル |
| AMD Radeon GPU Profiler | AMD の、詳細な、プロファイル |
| RenderDoc | フレームの、キャプチャ。D3D12 にも、対応 |

コードの、タイムスタンプ クエリを、デバッグ表示に、出しておくと、どのパスが、重いか、すぐ、確認できます。

## よくあるミス

??? failure "測った時間が、異常に、短い（CPU の時間）"
    CPU の時計で、`DrawInstanced` の前後を、測っている。GPU が、実行するのは、後。GPU タイムスタンプで、測る。

??? failure "時間が、負、巨大な値になる"
    キューごとに、周波数が、違うのに、別のキューの、周波数を、使っている。`GetTimestampFrequency` を、測ったキューで、呼ぶ。

??? failure "結果が、全部 0"
    フェンスで、GPU の完了を、待たず、READBACK を、読んでいる。`ResolveQueryData` を、記録していない。

??? failure "READBACK バッファの、状態エラー"
    READBACK ヒープの、バッファは、`COPY_DEST` の、初期状態（固定）。遷移しない。

## これだけ覚える

!!! abstract "まとめ"
    - [x] GPU の時間は、GPU に、測らせる。クエリ ヒープ（`TIMESTAMP`）+ READBACK バッファ
    - [x] `EndQuery` で、時刻を、記録。`ResolveQueryData` で、READBACK へコピー
    - [x] 周波数は、キューごと（`GetTimestampFrequency`）
    - [x] フレームごとに、別の領域。数フレーム遅れて、読む
    - [x] 本格的には、PIX・Nsight・Radeon GPU Profiler

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Frame Resources](frame-resources.md)
- [Debug Layer](debug-layer.md)
- [Tools](../../rendering/tools.md)
- [GPU Queries and Timing](../dx11/query-timing.md)
- [Microsoft Learn: クエリ](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/queries)
