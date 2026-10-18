---
title: GPU Queries and Timing (D3D12)
tags:
  - DirectX
---

# GPU Queries and Timing (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

GPU の処理時間を測るには <strong>GPU 自身に時刻を記録させる</strong>、必要があります。CPU の時計では命令を記録する、時間しか測れません。D3D12 では <strong>クエリ ヒープ</strong>（`ID3D12QueryHeap`）にタイムスタンプを書き込み <strong>`ResolveQueryData`</strong> で結果を、READBACK のバッファにコピーして CPU で読みます。

!!! tip "ポイント"
    - タイムスタンプ クエリ ＝ ある瞬間の GPU の時刻（チック数）。2 つ（開始・終了）の差と周波数で、ミリ秒に換算。
    - 流れ: <strong>クエリ ヒープを作る → `EndQuery`（記録）→ `ResolveQueryData`（READBACK バッファへ）→ フェンスで完了を、確認 → CPU が `Map` して、読む</strong>。
    - 周波数は <strong>キューごと</strong>（`GetTimestampFrequency`）。
    - 結果は数フレーム、遅れて読む（完了を待たない）。
    - 本格的な解析は PIX、Nsight、Radeon GPU Profiler。

## クエリ ヒープを作る

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
| `PIPELINE_STATISTICS` | 頂点・ピクセル シェーダーの呼び出し数など |
| `COPY_QUEUE_TIMESTAMP` | COPY キューの時刻 |

## 時刻を記録する

```cpp
// 測りたい処理の、前後に、タイムスタンプを、記録する。
command_list->EndQuery(query_heap.Get(), D3D12_QUERY_TYPE_TIMESTAMP, 0);     // インデックス 0: 開始
RunPass();
command_list->EndQuery(query_heap.Get(), D3D12_QUERY_TYPE_TIMESTAMP, 1);     // インデックス 1: 終了
```

D3D12 では `BeginQuery` は不要で、タイムスタンプは `EndQuery` だけで記録します。複数のパスを測るならインデックスを増やします（パス A: 0・1、パス B: 2・3 …）。

## 結果を READBACK へ

```cpp
// フレームの、最後に、記録した、全クエリを、READBACK バッファへ、コピーする。
command_list->ResolveQueryData(query_heap.Get(), D3D12_QUERY_TYPE_TIMESTAMP,
                               0, used_count,                  // 開始インデックス、個数
                               readback_buffer.Get(), 0);      // コピー先とオフセット
```

`ResolveQueryData` は GPU の命令で <strong>コマンド リストに記録</strong>されます。実際の、コピーは GPU があとで行います。

## 結果を読む

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

周波数は <strong>キューごと</strong>に違います（`GetTimestampFrequency` は、そのキューの値）。COMPUTE キューで測ったなら COMPUTE キューの周波数を使います。

## フレームごとに別の領域

CPU が結果を読んでいる間に GPU が次のフレームの結果を同じ場所に書くと壊れます。<strong>フレームごとに別の READBACK 領域</strong>を持ちフレーム イン フライトと同じ数だけ、用意します（[Frame Resources](frame-resources.md)）。

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

`BINARY_OCCLUSION` は「1 ピクセルでも通ったか」だけを返し `OCCLUSION` は、ピクセル数を返します。結果は遅れて読み「前のフレームで、隠れていた物は描かない」運用にします（[Culling](../../rendering/culling.md)）。

## 本格的な計測

| ツール | 特徴 |
| --- | --- |
| PIX on Windows | 無料。D3D12 の標準。GPU カウンター、タイミング、シェーダーのデバッグ |
| NVIDIA Nsight Graphics | NVIDIA の GPU カウンター、シェーダー プロファイル |
| AMD Radeon GPU Profiler | AMD の詳細な、プロファイル |
| RenderDoc | フレームのキャプチャ。D3D12 にも対応 |

コードのタイムスタンプ クエリをデバッグ表示に出しておくとどのパスが重いかすぐ、確認できます。

## よくあるミス

??? failure "測った時間が異常に短い（CPU の時間）"
    CPU の時計で `DrawInstanced` の前後を測っている。GPU が実行するのは後。GPU タイムスタンプで測る。

??? failure "時間が負、巨大な値になる"
    キューごとに周波数が、違うのに別のキューの周波数を使っている。`GetTimestampFrequency` を測ったキューで呼ぶ。

??? failure "結果が、全部 0"
    フェンスで GPU の完了を待たず READBACK を読んでいる。`ResolveQueryData` を記録していない。

??? failure "READBACK バッファの状態エラー"
    READBACK ヒープのバッファは `COPY_DEST` の初期状態（固定）。遷移しない。

## これだけ覚える

!!! abstract "まとめ"
    - [x] GPU の時間は、GPU に測らせる。クエリ ヒープ（`TIMESTAMP`）+ READBACK バッファ
    - [x] `EndQuery` で時刻を記録。`ResolveQueryData` で READBACK へコピー
    - [x] 周波数はキューごと（`GetTimestampFrequency`）
    - [x] フレームごとに別の領域。数フレーム遅れて読む
    - [x] 本格的には PIX・Nsight・Radeon GPU Profiler

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Frame Resources](frame-resources.md)
- [Debug Layer](debug-layer.md)
- [Tools](../../rendering/tools.md)
- [GPU Queries and Timing](../dx11/query-timing.md)
- [Microsoft Learn: クエリ](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/queries)
