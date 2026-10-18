---
title: Upload Buffer
tags:
  - DirectX
---

# Upload Buffer

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>アップロード バッファ</strong>は、CPU の、データを、GPU の、専用メモリ（DEFAULT ヒープ）へ、送るための、<strong>中継用</strong>の、バッファです。メッシュの、頂点、テクスチャの、画素は、DEFAULT ヒープに、置きたい（速い）のに、CPU は、DEFAULT ヒープに、書けません。そこで、<strong>CPU が、見える、UPLOAD ヒープに、いったん、書き</strong>、GPU の、コピー命令で、DEFAULT ヒープへ、送ります。

!!! tip "ポイント"
    - 流れ: <strong>UPLOAD に、`memcpy` → コマンド リストで、`CopyBufferRegion` → DEFAULT のリソースが、使えるようになる</strong>。
    - コピーは、GPU が、あとで、実行する。UPLOAD の、バッファは、<strong>コピーが、終わるまで、解放できない</strong>（フェンスで、確認）。
    - コピー先は、`COPY_DEST` で、コピー後、`VERTEX_AND_CONSTANT_BUFFER` などに、バリアで、遷移する。
    - 毎フレーム、変わる、データ（定数バッファ）は、UPLOAD ヒープの、バッファに、直接、書く（DEFAULT へは、送らない）。
    - ヘルパー `UpdateSubresources`（`d3dx12.h`）が、テクスチャの、アップロードの、面倒を、見てくれる。

## 頂点バッファの、アップロード

```cpp
// ① DEFAULT ヒープの、頂点バッファ（GPU 専用）。初期状態は COPY_DEST。
auto default_heap = CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_DEFAULT);
auto buffer_desc = CD3DX12_RESOURCE_DESC::Buffer(vertex_buffer_size);
device->CreateCommittedResource(&default_heap, D3D12_HEAP_FLAG_NONE, &buffer_desc,
                                D3D12_RESOURCE_STATE_COPY_DEST, nullptr, IID_PPV_ARGS(&vertex_buffer));

// ② UPLOAD ヒープの、中継バッファ（CPU が書ける）。初期状態は GENERIC_READ（固定）。
auto upload_heap = CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_UPLOAD);
device->CreateCommittedResource(&upload_heap, D3D12_HEAP_FLAG_NONE, &buffer_desc,
                                D3D12_RESOURCE_STATE_GENERIC_READ, nullptr, IID_PPV_ARGS(&upload_buffer));
```

```cpp
// ③ CPU のデータを、UPLOAD バッファに、書く。
uint8_t* mapped = nullptr;
CD3DX12_RANGE no_read(0, 0);
upload_buffer->Map(0, &no_read, reinterpret_cast<void**>(&mapped));
std::memcpy(mapped, vertices, vertex_buffer_size);
upload_buffer->Unmap(0, nullptr);

// ④ GPU に、コピーさせる（コマンド リストに記録）。
command_list->CopyBufferRegion(vertex_buffer.Get(), 0,           // コピー先とオフセット
                               upload_buffer.Get(), 0,           // コピー元とオフセット
                               vertex_buffer_size);

// ⑤ コピー後は、頂点バッファとして、読めるよう、バリアで、状態を、遷移する。
auto barrier = CD3DX12_RESOURCE_BARRIER::Transition(vertex_buffer.Get(), D3D12_RESOURCE_STATE_COPY_DEST,
                                                    D3D12_RESOURCE_STATE_VERTEX_AND_CONSTANT_BUFFER);
command_list->ResourceBarrier(1, &barrier);
```

この、コマンド リストを、`Close` して、キューに、投げ、<strong>フェンスで、完了を、待つ</strong>と、`vertex_buffer` が、使えます。

```cpp
command_list->Close();
ID3D12CommandList* lists[] = {command_list.Get()};
command_queue->ExecuteCommandLists(1, lists);
WaitForGpu();                                                    // コピーの完了を待つ（fence.md）
upload_buffer.Reset();                                           // ここで初めて、UPLOAD バッファを、解放できる
```

<strong>GPU が、コピーを、終えるまで、`upload_buffer` を、解放してはいけません</strong>。ロード時は、`WaitForGpu` で、まとめて、待ち、その後、中継バッファを、解放します。

## 流れの、図

```text
CPU メモリ  ──memcpy──▶  UPLOAD ヒープ  ──CopyBufferRegion（GPU が実行）──▶  DEFAULT ヒープ
 (vertices)              (upload_buffer)                                        (vertex_buffer)
                                                                                  ↑ 描画は、こちらを使う（高速）
```

## 配列の、アップロード（複数メッシュ）

多数のメッシュを、ロードするとき、メッシュごとに、中継バッファを、作ると、重いので、<strong>1 つの、大きな、UPLOAD バッファに、並べて</strong>、まとめてコピーします。

```cpp
// 大きな UPLOAD バッファ（64 MB）を 1 つ持ち、先頭から、順に、書いていく。
size_t offset = 0;
for (const Mesh& mesh : meshes) {
  std::memcpy(mapped + offset, mesh.vertices.data(), mesh.vertex_bytes);
  command_list->CopyBufferRegion(mesh.gpu_buffer.Get(), 0, upload_buffer.Get(), offset, mesh.vertex_bytes);
  offset = AlignUp(offset + mesh.vertex_bytes, 256);              // 次の、書き込み位置（256 バイトに、そろえる）
}
```

## テクスチャの、アップロード

テクスチャの、アップロードは、<strong>行の幅（ピッチ）の、アラインメント</strong>が、あり、面倒なので、`UpdateSubresources`（`d3dx12.h`）を、使います（[Texture Upload](texture-upload.md)）。

## 毎フレームの、データ（定数バッファ）

毎フレーム、変わる、データは、DEFAULT へ、送らず、<strong>UPLOAD ヒープの、バッファに、直接、書き</strong>、GPU が、そこから、読みます（UPLOAD ヒープは、GPU から、読める）。

```cpp
// UPLOAD ヒープの、定数バッファを、永続的に Map したまま、毎フレーム、書き換える。
std::memcpy(mapped_constants + frame_offset, &constants, sizeof(constants));
```

GPU が、前のフレームを、読んでいる間に、同じ領域を、書き換えないよう、<strong>フレームごとに、別の領域</strong>に、書きます（[Frame Resources](frame-resources.md)、[Constant Buffer](constant-buffer.md)）。

## 動的な、頂点バッファ

毎フレーム、頂点が、変わる（パーティクル、UI）ときも、UPLOAD ヒープの、バッファに、直接、書き、頂点バッファ ビューで、そこを、指します。速度は、DEFAULT より、やや、落ちますが、コピーの、手間が、要りません。

## READBACK：GPU から、CPU へ

```cpp
// READBACK ヒープの、バッファに、GPU の結果を、コピーして、CPU が読む。
auto readback_heap = CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_READBACK);
device->CreateCommittedResource(&readback_heap, D3D12_HEAP_FLAG_NONE, &buffer_desc,
                                D3D12_RESOURCE_STATE_COPY_DEST, nullptr, IID_PPV_ARGS(&readback_buffer));

command_list->CopyBufferRegion(readback_buffer.Get(), 0, gpu_buffer.Get(), 0, size);   // GPU → READBACK
// ... Close、Execute、フェンスで完了を待つ ...

void* data = nullptr;
CD3DX12_RANGE read_range(0, size);
readback_buffer->Map(0, &read_range, &data);                    // 読む範囲を、指定
// data を読む
CD3DX12_RANGE no_write(0, 0);
readback_buffer->Unmap(0, &no_write);                            // CPU は、書かなかった
```

結果を、読む前に、<strong>フェンスで、コピーの完了を、待ちます</strong>。毎フレーム、待つと、止まるので、数フレーム遅れて、読みます（[GPU Queries and Timing](query-timing.md)）。

## ヘルパー：UpdateSubresources

`d3dx12.h` の、`UpdateSubresources` は、中継バッファへの、書き込みと、コピーの、命令を、まとめて、行います。

```cpp
// バッファ・テクスチャの、サブリソース配列を、中継バッファ経由で、DEFAULT リソースへ、アップロードする。
D3D12_SUBRESOURCE_DATA data = {};
data.pData = pixels;
data.RowPitch = width * 4;
data.SlicePitch = data.RowPitch * height;
UpdateSubresources(command_list.Get(), texture.Get(), upload_buffer.Get(), 0, 0, 1, &data);
```

テクスチャの、場合は、中継バッファの、大きさを、`GetRequiredIntermediateSize` で、求めます（[Texture Upload](texture-upload.md)）。

## よくあるミス

??? failure "コピー後、頂点バッファが、化ける、または、空"
    GPU が、コピーを、終える前に、UPLOAD バッファを、解放した。または、コピー先の、状態遷移（`COPY_DEST` → `VERTEX_AND_CONSTANT_BUFFER`）を、忘れた。フェンスで、待つ。

??? failure "UPLOAD ヒープの、リソースを、`COPY_DEST` に、して、エラー"
    UPLOAD ヒープは、`GENERIC_READ` で、固定。コピー先には、できない。コピー先は、DEFAULT。

??? failure "毎フレームの、定数が、ちらつく、前のフレームの値が、混ざる"
    GPU が、読んでいる、同じ領域を、CPU が、書き換えている。フレームごとに、別の領域に、書く。

??? failure "ロードが、遅い（メッシュごとに、中継バッファを作る）"
    大きな、UPLOAD バッファを、1 つ、使い回して、まとめて、コピーする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] CPU は、DEFAULT に、書けない。UPLOAD（中継）→ `CopyBufferRegion` → DEFAULT
    - [x] コピーは、GPU が、あとで実行。完了まで、UPLOAD バッファを、解放しない
    - [x] コピー先は、`COPY_DEST`。コピー後に、バリアで、使う状態へ
    - [x] 毎フレームの、データは、UPLOAD に、直接書く。フレームごとに、別の領域
    - [x] テクスチャは、`UpdateSubresources`
    - [x] GPU の結果の読み出しは、READBACK。遅れて、読む

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Heaps and Resources](heaps-resources.md)
- [Texture Upload](texture-upload.md)
- [Frame Resources](frame-resources.md)
- [Microsoft Learn: アップロード・リードバック](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/uploading-resources)
