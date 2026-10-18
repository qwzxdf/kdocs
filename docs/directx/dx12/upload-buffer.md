---
title: Upload Buffer
tags:
  - DirectX
---

# Upload Buffer

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>アップロード バッファ</strong>は CPU のデータを GPU の専用メモリ（DEFAULT ヒープ）へ、送るための <strong>中継用</strong>のバッファです。メッシュの頂点、テクスチャの画素は DEFAULT ヒープに置きたい（速い）のに CPU は、DEFAULT ヒープに書けません。そこで、<strong>CPU が見える UPLOAD ヒープにいったん書き</strong>、GPU のコピー命令で DEFAULT ヒープへ送ります。

!!! tip "ポイント"
    - 流れ: <strong>UPLOAD に `memcpy` → コマンド リストで `CopyBufferRegion` → DEFAULT のリソースが、使えるようになる</strong>。
    - コピーは GPU があとで、実行する。UPLOAD のバッファは <strong>コピーが、終わるまで解放できない</strong>（フェンスで、確認）。
    - コピー先は `COPY_DEST` で、コピー後、`VERTEX_AND_CONSTANT_BUFFER` などにバリアで遷移する。
    - 毎フレーム、変わるデータ（定数バッファ）は UPLOAD ヒープのバッファに直接、書く（DEFAULT へは送らない）。
    - ヘルパー `UpdateSubresources`（`d3dx12.h`）が、テクスチャのアップロードの面倒を見てくれる。

## 頂点バッファのアップロード

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

このコマンド リストを `Close` して、キューに投げ <strong>フェンスで完了を待つ</strong>と `vertex_buffer` が使えます。

```cpp
command_list->Close();
ID3D12CommandList* lists[] = {command_list.Get()};
command_queue->ExecuteCommandLists(1, lists);
WaitForGpu();                                                    // コピーの完了を待つ（fence.md）
upload_buffer.Reset();                                           // ここで初めて、UPLOAD バッファを、解放できる
```

<strong>GPU がコピーを終えるまで `upload_buffer` を解放してはいけません</strong>。ロード時は `WaitForGpu` でまとめて待ちその後、中継バッファを解放します。

## 流れの図

```text
CPU メモリ  ──memcpy──▶  UPLOAD ヒープ  ──CopyBufferRegion（GPU が実行）──▶  DEFAULT ヒープ
 (vertices)              (upload_buffer)                                        (vertex_buffer)
                                                                                  ↑ 描画は、こちらを使う（高速）
```

## 配列のアップロード（複数メッシュ）

多数のメッシュをロードするときメッシュごとに中継バッファを作ると、重いので <strong>1 つの大きな UPLOAD バッファに並べて</strong>、まとめてコピーします。

```cpp
// 大きな UPLOAD バッファ（64 MB）を 1 つ持ち、先頭から、順に、書いていく。
size_t offset = 0;
for (const Mesh& mesh : meshes) {
  std::memcpy(mapped + offset, mesh.vertices.data(), mesh.vertex_bytes);
  command_list->CopyBufferRegion(mesh.gpu_buffer.Get(), 0, upload_buffer.Get(), offset, mesh.vertex_bytes);
  offset = AlignUp(offset + mesh.vertex_bytes, 256);              // 次の、書き込み位置（256 バイトに、そろえる）
}
```

## テクスチャのアップロード

テクスチャのアップロードは <strong>行の幅（ピッチ）のアラインメント</strong>があり面倒なので、`UpdateSubresources`（`d3dx12.h`）を使います（[Texture Upload](texture-upload.md)）。

## 毎フレームのデータ（定数バッファ）

毎フレーム、変わるデータは DEFAULT へ送らず <strong>UPLOAD ヒープのバッファに直接、書き</strong>、GPU がそこから読みます（UPLOAD ヒープは、GPU から読める）。

```cpp
// UPLOAD ヒープの、定数バッファを、永続的に Map したまま、毎フレーム、書き換える。
std::memcpy(mapped_constants + frame_offset, &constants, sizeof(constants));
```

GPU が前のフレームを読んでいる間に同じ領域を書き換えないよう <strong>フレームごとに、別の領域</strong>に書きます（[Frame Resources](frame-resources.md)、[Constant Buffer](constant-buffer.md)）。

## 動的な頂点バッファ

毎フレーム、頂点が変わる（パーティクル、UI）ときも UPLOAD ヒープのバッファに直接、書き頂点バッファ ビューでそこを指します。速度は DEFAULT よりやや落ちますがコピーの手間が要りません。

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

結果を読む前に <strong>フェンスでコピーの完了を待ちます</strong>。毎フレーム、待つと止まるので数フレーム遅れて、読みます（[GPU Queries and Timing](query-timing.md)）。

## ヘルパー：UpdateSubresources

`d3dx12.h` の `UpdateSubresources` は中継バッファへの書き込みとコピーの命令をまとめて、行います。

```cpp
// バッファ・テクスチャの、サブリソース配列を、中継バッファ経由で、DEFAULT リソースへ、アップロードする。
D3D12_SUBRESOURCE_DATA data = {};
data.pData = pixels;
data.RowPitch = width * 4;
data.SlicePitch = data.RowPitch * height;
UpdateSubresources(command_list.Get(), texture.Get(), upload_buffer.Get(), 0, 0, 1, &data);
```

テクスチャの場合は中継バッファの大きさを `GetRequiredIntermediateSize` で求めます（[Texture Upload](texture-upload.md)）。

## よくあるミス

??? failure "コピー後、頂点バッファが化けるまたは空"
    GPU がコピーを終える前に UPLOAD バッファを解放した。または、コピー先の状態遷移（`COPY_DEST` → `VERTEX_AND_CONSTANT_BUFFER`）を忘れた。フェンスで待つ。

??? failure "UPLOAD ヒープのリソースを `COPY_DEST` にしてエラー"
    UPLOAD ヒープは `GENERIC_READ` で固定。コピー先にはできない。コピー先は DEFAULT。

??? failure "毎フレームの定数が、ちらつく前のフレームの値が混ざる"
    GPU が読んでいる、同じ領域を CPU が書き換えている。フレームごとに別の領域に書く。

??? failure "ロードが、遅い（メッシュごとに中継バッファを作る）"
    大きな UPLOAD バッファを 1 つ使い回してまとめてコピーする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] CPU は DEFAULT に書けない。UPLOAD（中継）→ `CopyBufferRegion` → DEFAULT
    - [x] コピーは GPU があとで実行。完了まで UPLOAD バッファを解放しない
    - [x] コピー先は `COPY_DEST`。コピー後にバリアで使う状態へ
    - [x] 毎フレームのデータは UPLOAD に直接書く。フレームごとに別の領域
    - [x] テクスチャは `UpdateSubresources`
    - [x] GPU の結果の読み出しは、READBACK。遅れて読む

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Heaps and Resources](heaps-resources.md)
- [Texture Upload](texture-upload.md)
- [Frame Resources](frame-resources.md)
- [Microsoft Learn: アップロード・リードバック](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/uploading-resources)
