---
title: GPU Queries and Timing (D3D12)
tags:
  - DirectX
---

# GPU Queries and Timing (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

ゲームが重いときまず知りたいのは、「どの処理がどれだけ時間を使っているか」です。ところが、CPU の時計で `DrawInstanced` の前後を測っても、意味がありません。D3D12 の描画命令は記録されるだけで、GPU が実際に実行するのは、あとだからです。測れるのは命令を記録する時間だけです。

GPU の処理時間は GPU 自身に時刻を記録させて測ります。クエリ ヒープ（`ID3D12QueryHeap`）へタイムスタンプを書き込み `ResolveQueryData` で結果を READBACK のバッファへコピーして、CPU が読みます。

!!! tip "ポイント"
    - タイムスタンプ クエリは、ある瞬間の GPU の時刻（チックの数）。2 つの差と周波数からミリ秒に換算する。
    - 流れはクエリ ヒープを作り `EndQuery` で記録し、`ResolveQueryData` で READBACK のバッファへコピーし、フェンスで完了を確認して CPU が `Map` して読む。
    - 周波数はキューごとに違う（`GetTimestampFrequency`）。
    - 結果は数フレーム遅れて読む。完了を待たない。
    - 本格的な解析は PIX、Nsight、Radeon GPU Profiler を使う。

!!! info "このページを読む前に"
    結果を読み出す READBACK のバッファは [Heaps and Resources](heaps-resources.md) と [Upload Buffer](upload-buffer.md)、フレームごとに領域を分ける考え方は [Frame Resources](frame-resources.md) で説明しています。クエリの命令は [ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md#endquery)、周波数は [ID3D12CommandQueue](api/id3d12commandqueue.md#gettimestampfrequency) にあります。

## クエリ ヒープを作る

```cpp
constexpr UINT kMaxTimestamps = 64;  // 1 フレームで記録するタイムスタンプの数

D3D12_QUERY_HEAP_DESC heap_desc = {};
heap_desc.Type = D3D12_QUERY_HEAP_TYPE_TIMESTAMP;  // タイムスタンプ用
heap_desc.Count = kMaxTimestamps;
ComPtr<ID3D12QueryHeap> query_heap;
device->CreateQueryHeap(&heap_desc, IID_PPV_ARGS(&query_heap));

// 結果を読むための READBACK のバッファ（タイムスタンプは、1 つが 8 バイト）。
D3D12_HEAP_PROPERTIES readback_heap = MakeHeapProperties(D3D12_HEAP_TYPE_READBACK);
D3D12_RESOURCE_DESC buffer_desc = MakeBufferDesc(kMaxTimestamps * sizeof(UINT64));
device->CreateCommittedResource(&readback_heap, D3D12_HEAP_FLAG_NONE, &buffer_desc, D3D12_RESOURCE_STATE_COPY_DEST,
                                nullptr, IID_PPV_ARGS(&readback_buffer));
```

クエリ ヒープの種類は `Type` で選びます。`TIMESTAMP` は DIRECT と COMPUTE のキューの時刻を測ります。`OCCLUSION` は通ったピクセルの数、`PIPELINE_STATISTICS` は頂点シェーダーやピクセル シェーダーの呼び出し数などです。COPY のキューの時刻は `COPY_QUEUE_TIMESTAMP` で測ります。

## 時刻を記録する

測りたい処理の前後にタイムスタンプを記録します。

```cpp
command_list->EndQuery(query_heap.Get(), D3D12_QUERY_TYPE_TIMESTAMP, 0);  // 番号 0: 開始
RunPass();
command_list->EndQuery(query_heap.Get(), D3D12_QUERY_TYPE_TIMESTAMP, 1);  // 番号 1: 終了
```

タイムスタンプは時点を測るので、`BeginQuery` は要りません。`EndQuery` だけで時刻が記録されます。複数のパスを測るなら番号を増やします（パス A は 0 と 1、パス B は 2 と 3 のように）。

## 結果を READBACK へ

フレームの最後に記録したすべてのクエリを READBACK のバッファへコピーします。

```cpp
command_list->ResolveQueryData(query_heap.Get(), D3D12_QUERY_TYPE_TIMESTAMP,
                               0, used_count,                  // 開始の番号と個数
                               readback_buffer.Get(), 0);      // コピー先とオフセット
```

`ResolveQueryData` は GPU の命令でコマンド リストに記録されます。実際のコピーは GPU があとで行います。

## 結果を読む

数フレームあとそのフレームの GPU 完了をフェンスで確認してから読みます。

```cpp
UINT64 frequency;
command_queue->GetTimestampFrequency(&frequency);  // 1 秒あたりのチック数

UINT64* timestamps = nullptr;
D3D12_RANGE read_range = {0, used_count * sizeof(UINT64)};
readback_buffer->Map(0, &read_range, reinterpret_cast<void**>(&timestamps));
const double milliseconds = double(timestamps[1] - timestamps[0]) / double(frequency) * 1000.0;
D3D12_RANGE no_write = {0, 0};
readback_buffer->Unmap(0, &no_write);
```

2 つのタイムスタンプの差がチックの数です。周波数で割ると秒になり 1000 を掛けるとミリ秒です。周波数はキューごとに違います。COMPUTE のキューで測ったなら COMPUTE のキューで `GetTimestampFrequency` を呼びます。

## フレームごとに別の領域を使う

CPU が結果を読んでいる間に GPU が次のフレームの結果を同じ場所へ書くと、値が壊れます。READBACK の領域はフレームを同時に進める数だけ持って、フレームごとに分けます（[Frame Resources](frame-resources.md)）。

```cpp
// READBACK のバッファをフレームの数だけ分ける。このフレームの結果は、kFrameCount フレームあとに読む。
const UINT slot = frame_number % kFrameCount;
command_list->ResolveQueryData(query_heap.Get(), D3D12_QUERY_TYPE_TIMESTAMP, 0, used_count,
                               readback_buffer.Get(), slot * kMaxTimestamps * sizeof(UINT64));
```

## オクルージョン クエリ

描画した物が 1 ピクセルでも画面に出たかを調べるのが、オクルージョン クエリです。物の境界ボックスを描いて通ったかどうかを見ます。

```cpp
D3D12_QUERY_HEAP_DESC heap_desc = {D3D12_QUERY_HEAP_TYPE_OCCLUSION, 256};
// 描画を BeginQuery と EndQuery で囲む。
command_list->BeginQuery(occlusion_heap.Get(), D3D12_QUERY_TYPE_BINARY_OCCLUSION, index);  // 通ったか（0 か 1）
DrawBoundingBox();
command_list->EndQuery(occlusion_heap.Get(), D3D12_QUERY_TYPE_BINARY_OCCLUSION, index);
```

`BINARY_OCCLUSION` は「1 ピクセルでも通ったか」だけを返します。`OCCLUSION` は通ったピクセル数を返します。結果は遅れて読むので「前のフレームで隠れていた物は、描かない」という使い方をします（[Culling](../../rendering/culling.md)）。

## 本格的に計測する

PIX on Windows は無料で、D3D12 の標準のツールです。GPU のカウンター、タイミング、シェーダーのデバッグができます。NVIDIA Nsight Graphics は、NVIDIA の GPU のカウンターとシェーダーのプロファイルを見られます。AMD Radeon GPU Profiler は、AMD の詳細なプロファイルを取れます。RenderDoc はフレームのキャプチャで、D3D12 にも対応しています。

コードの中のタイムスタンプ クエリをデバッグ表示に出しておくとどのパスが重いかをすぐ確認できます。

## よくあるミス

??? failure "測った時間が異常に短い（CPU の時間になっている）"
    CPU の時計で `DrawInstanced` の前後を測っています。GPU が実行するのはあとです。GPU のタイムスタンプで測ります。

??? failure "時間が負になる巨大な値になる"
    キューごとに周波数が違うのに、別のキューの周波数を使っています。測ったキューで `GetTimestampFrequency` を呼びます。

??? failure "結果がすべて 0 になる"
    フェンスで GPU の完了を待たずに READBACK を読んでいます。または、`ResolveQueryData` を記録していません。

??? failure "READBACK のバッファの状態でエラーになる"
    READBACK のヒープのバッファは、`COPY_DEST` の初期状態で固定です。遷移しません。

## これだけ覚える

!!! abstract "まとめ"
    - [x] GPU の時間は、GPU に測らせる。クエリ ヒープ（`TIMESTAMP`）と READBACK のバッファを使う
    - [x] `EndQuery` で時刻を記録し、`ResolveQueryData` で READBACK へコピーする
    - [x] 周波数はキューごと（`GetTimestampFrequency`）
    - [x] フレームごとに別の領域を使い数フレーム遅れて読む
    - [x] 本格的には PIX、Nsight、Radeon GPU Profiler を使う

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3D12CommandQueue](api/id3d12commandqueue.md)
- [Frame Resources](frame-resources.md)
- [Debug Layer](debug-layer.md)
- [Tools](../../rendering/tools.md)
- [Microsoft Learn: クエリ](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/queries)
