---
title: Upload Buffer
tags:
  - DirectX
---

# Upload Buffer

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

メッシュの頂点やテクスチャの画素は GPU の専用メモリ（DEFAULT ヒープ）に置きたいデータです。そのほうが速いからです。ところが CPU は DEFAULT のヒープに直接書けません。

そこで、CPU から見える UPLOAD ヒープにいったんデータを書いておき GPU のコピー命令で DEFAULT ヒープへ送ります。この一時的な中継用のバッファが <strong>アップロード バッファ</strong>です。

!!! tip "ポイント"
    - 流れは UPLOAD に `memcpy`、コマンド リストで `CopyBufferRegion`、DEFAULT のリソースが使えるようになる。
    - コピーは GPU があとで実行する。UPLOAD のバッファはコピーが終わるまで解放できない（フェンスで確認する）。
    - コピー先は `COPY_DEST` で、コピーのあとはバリアで `VERTEX_AND_CONSTANT_BUFFER` などへ切り替える。
    - 毎フレーム変わるデータ（定数バッファ）は、UPLOAD のバッファへ直接書く。DEFAULT へは送らない。
    - テクスチャのアップロードは、行の幅の決まりがあるので[Texture Upload](texture-upload.md) で説明する。

!!! info "このページを読む前に"
    ヒープの種類は [Heaps and Resources](heaps-resources.md)、状態の切り替えは [Resource Barrier](resource-barrier.md)、完了の待ち方は [Fence](fence.md) で説明しています。コピーの命令は [ID3D12GraphicsCommandList::CopyBufferRegion](api/id3d12graphicscommandlist.md#copybufferregion)、`Map` は [ID3D12Resource](api/id3d12resource.md#map) にあります。

## 頂点バッファを送る

まず、2 つのバッファを作ります。GPU が描くときに使う DEFAULT のバッファと中継用の UPLOAD のバッファです。

```cpp
// 1. DEFAULT の頂点バッファ（GPU 専用）。初期状態は COPY_DEST。
D3D12_HEAP_PROPERTIES default_heap = MakeHeapProperties(D3D12_HEAP_TYPE_DEFAULT);
D3D12_RESOURCE_DESC buffer_desc = MakeBufferDesc(vertex_buffer_size);
device->CreateCommittedResource(&default_heap, D3D12_HEAP_FLAG_NONE, &buffer_desc,
                                D3D12_RESOURCE_STATE_COPY_DEST, nullptr, IID_PPV_ARGS(&vertex_buffer));

// 2. UPLOAD の中継バッファ（CPU が書ける）。初期状態は GENERIC_READ で固定。
D3D12_HEAP_PROPERTIES upload_heap = MakeHeapProperties(D3D12_HEAP_TYPE_UPLOAD);
device->CreateCommittedResource(&upload_heap, D3D12_HEAP_FLAG_NONE, &buffer_desc,
                                D3D12_RESOURCE_STATE_GENERIC_READ, nullptr, IID_PPV_ARGS(&upload_buffer));
```

UPLOAD のバッファは初期状態を必ず `GENERIC_READ` にします。DEFAULT のほうはこれからコピーを受けるので、`COPY_DEST` から始めます。

次に、CPU のデータを UPLOAD に書き GPU にコピーさせます。

```cpp
// 3. CPU のデータを UPLOAD のバッファに書く。
uint8_t* mapped = nullptr;
D3D12_RANGE no_read = {0, 0};
upload_buffer->Map(0, &no_read, reinterpret_cast<void**>(&mapped));
std::memcpy(mapped, vertices, vertex_buffer_size);
upload_buffer->Unmap(0, nullptr);

// 4. GPU にコピーさせる（コマンド リストに記録）。
command_list->CopyBufferRegion(vertex_buffer.Get(), 0,  // コピー先とオフセット
                               upload_buffer.Get(), 0,  // コピー元とオフセット
                               vertex_buffer_size);

// 5. コピーのあと、頂点バッファとして読めるように、状態を切り替える。
D3D12_RESOURCE_BARRIER barrier = MakeTransitionBarrier(
    vertex_buffer.Get(), D3D12_RESOURCE_STATE_COPY_DEST, D3D12_RESOURCE_STATE_VERTEX_AND_CONSTANT_BUFFER);
command_list->ResourceBarrier(1, &barrier);
```

最後に、このコマンド リストを閉じて、キューに渡しフェンスで完了を待ちます。

```cpp
command_list->Close();
ID3D12CommandList* lists[] = {command_list.Get()};
command_queue->ExecuteCommandLists(1, lists);
WaitForGpu();         // コピーの完了を待つ（Fence のページ）
upload_buffer.Reset();  // ここで初めて、UPLOAD のバッファを解放できる
```

**GPU がコピーを終えるまで、`upload_buffer` を解放してはいけません。** コピーの命令を記録した時点では、まだコピーされていないからです。ロード時はまとめて `WaitForGpu` で待ってから、中継バッファを解放します。

流れを図にすると次のとおりです。

```text
CPU メモリ  ──memcpy──▶  UPLOAD ヒープ  ──CopyBufferRegion（GPU が実行）──▶  DEFAULT ヒープ
 (vertices)              (upload_buffer)                                        (vertex_buffer)
                                                                                  ↑ 描画は、こちらを使う（高速）
```

## たくさんのメッシュを送る

メッシュごとに中継バッファを作ると、作成の負担が大きくなります。1 つの大きな UPLOAD のバッファを用意して、先頭から順に書きまとめてコピーします。

```cpp
// 大きな UPLOAD バッファ（64 MB）を 1 つ持ち、先頭から順に書いていく。
size_t offset = 0;
for (const Mesh& mesh : meshes) {
  std::memcpy(mapped + offset, mesh.vertices.data(), mesh.vertex_bytes);
  command_list->CopyBufferRegion(mesh.gpu_buffer.Get(), 0, upload_buffer.Get(), offset, mesh.vertex_bytes);
  offset = AlignUp(offset + mesh.vertex_bytes, 256);  // 次の書き込み位置（256 バイトにそろえる）
}
```

`AlignUp` は値を決まった倍数へ切り上げる小さな関数です。UPLOAD のバッファの中で、データの先頭を 256 バイトの境界にそろえておくと定数バッファなどにも使い回せます。

## 毎フレーム変わるデータは直接書く

毎フレーム変わるデータ（定数バッファなど）は、DEFAULT へ送らず UPLOAD のバッファに直接書きます。UPLOAD のヒープは GPU からも読めます。

```cpp
// UPLOAD の定数バッファを永続的に Map したまま、毎フレーム書き換える。
std::memcpy(mapped_constants + frame_offset, &constants, sizeof(constants));
```

GPU が前のフレームを読んでいる間に同じ領域を書き換えてはいけません。フレームごとに別の領域へ書きます（[Frame Resources](frame-resources.md)、[Constant Buffer](constant-buffer.md)）。

パーティクルや UI のように毎フレーム頂点が変わるものも同じ考え方です。UPLOAD のバッファに直接書いて、頂点バッファ ビューでそこを指します。DEFAULT よりやや遅くなりますが、コピーの手間が要りません。

## READBACK で GPU の結果を読む

GPU が書いた結果を CPU で読むときは、READBACK のバッファへコピーして、`Map` で読みます。

```cpp
// READBACK のバッファへ GPU の結果をコピーして、CPU が読む。
D3D12_HEAP_PROPERTIES readback_heap = MakeHeapProperties(D3D12_HEAP_TYPE_READBACK);
device->CreateCommittedResource(&readback_heap, D3D12_HEAP_FLAG_NONE, &buffer_desc,
                                D3D12_RESOURCE_STATE_COPY_DEST, nullptr, IID_PPV_ARGS(&readback_buffer));

command_list->CopyBufferRegion(readback_buffer.Get(), 0, gpu_buffer.Get(), 0, size);  // GPU から READBACK へ
// ... Close、Execute、フェンスで完了を待つ ...

void* data = nullptr;
D3D12_RANGE read_range = {0, size};
readback_buffer->Map(0, &read_range, &data);  // 読む範囲を指定
// data を読む
D3D12_RANGE no_write = {0, 0};
readback_buffer->Unmap(0, &no_write);  // CPU は書かなかった
```

結果を読む前にフェンスでコピーの完了を待ちます。毎フレーム待つと止まってしまうので、数フレーム遅れて読むのが定番です（[GPU Queries and Timing](query-timing.md)）。

## テクスチャを送る

テクスチャも同じ流れで送ります。ただし、UPLOAD のバッファの中では画像の 1 行ごとの幅（ピッチ）を決まった倍数にそろえる必要があるので、少し面倒です。その手順は [Texture Upload](texture-upload.md) で説明しています。

## よくあるミス

??? failure "コピーしたあと頂点バッファが化けるまたは空になる"
    GPU がコピーを終える前に UPLOAD のバッファを解放しました。または、コピー先の状態の切り替え（`COPY_DEST` から `VERTEX_AND_CONSTANT_BUFFER`）を忘れました。フェンスで待ちます。

??? failure "UPLOAD のリソースを `COPY_DEST` にしようとしてエラーになる"
    UPLOAD のヒープは `GENERIC_READ` で固定です。コピー先にはできません。コピー先は DEFAULT のリソースです。

??? failure "毎フレームの定数がちらつく、前のフレームの値が混ざる"
    GPU が読んでいる同じ領域を CPU が書き換えています。フレームごとに別の領域へ書きます。

??? failure "ロードが遅い（メッシュごとに中継バッファを作っている）"
    大きな UPLOAD のバッファを 1 つ使い回して、まとめてコピーします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] CPU は DEFAULT に書けない。UPLOAD（中継）に書いて、`CopyBufferRegion` で DEFAULT へ送る
    - [x] コピーは GPU があとで実行する。完了まで UPLOAD のバッファを解放しない
    - [x] コピー先は `COPY_DEST`。コピーのあとにバリアで使う状態へ切り替える
    - [x] 毎フレームのデータは、UPLOAD に直接書く。フレームごとに別の領域へ書く
    - [x] GPU の結果を読むときは、READBACK を使い数フレーム遅れて読む

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Heaps and Resources](heaps-resources.md)
- [ID3D12Resource](api/id3d12resource.md)
- [Texture Upload](texture-upload.md)
- [Frame Resources](frame-resources.md)
- [Microsoft Learn: アップロードとリードバック](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/uploading-resources)
