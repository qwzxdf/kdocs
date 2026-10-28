---
title: Vertex and Index Buffer Views
tags:
  - DirectX
---

# Vertex and Index Buffer Views

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

頂点バッファとインデックス バッファは、特別なリソースではなく普通のバッファ（`ID3D12Resource`）です。ところが、描画のときには「このバッファのここから、1 頂点がこの大きさで並んでいる」という情報が必要です。その情報をまとめた小さな構造体が**ビュー**（`D3D12_VERTEX_BUFFER_VIEW`、`D3D12_INDEX_BUFFER_VIEW`）です。

ほかのビュー（SRV や RTV）と違って、この 2 つのビューはディスクリプタ ヒープには入れません。構造体のままコマンド リストに直接渡します。

!!! tip "ポイント"
    - 頂点とインデックスのビューは、構造体のまま渡す。ディスクリプタ ヒープには置かない。
    - 頂点バッファ ビューは `BufferLocation`（GPU アドレス）、`SizeInBytes`、`StrideInBytes`（1 頂点の大きさ）。
    - インデックス バッファ ビューは `BufferLocation`、`SizeInBytes`、`Format`（`R16_UINT` か `R32_UINT`）。
    - バッファは DEFAULT のヒープに置きアップロードで送る（[Upload Buffer](upload-buffer.md)）。
    - 入力レイアウトは PSO の中で決める（[PSO](pso.md)）。

!!! info "このページを読む前に"
    バッファの作り方と GPU への送り方は [Heaps and Resources](heaps-resources.md) と [Upload Buffer](upload-buffer.md) で説明しています。入力レイアウトは [PSO](pso.md) の一部です。コマンド リストのメソッドは[ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md) にまとめています。

## 頂点バッファ ビュー

```cpp
struct Vertex {
  DirectX::XMFLOAT3 position;
  DirectX::XMFLOAT4 color;
};

const Vertex vertices[] = {
    {{0.0f, 0.5f, 0.0f}, {1, 0, 0, 1}},  // 反時計回りが表
    {{-0.5f, -0.5f, 0.0f}, {0, 1, 0, 1}},
    {{0.5f, -0.5f, 0.0f}, {0, 0, 1, 1}},
};

// vertex_buffer（DEFAULT のヒープ）を作って、vertices をアップロードしたあと。
D3D12_VERTEX_BUFFER_VIEW vertex_buffer_view = {};
vertex_buffer_view.BufferLocation = vertex_buffer->GetGPUVirtualAddress();  // GPU 上のバッファの先頭アドレス
vertex_buffer_view.SizeInBytes = sizeof(vertices);                          // バッファの大きさ（バイト）
vertex_buffer_view.StrideInBytes = sizeof(Vertex);                          // 1 頂点の大きさ
```

3 つのメンバーの意味は次のとおりです。`BufferLocation` はバッファの GPU アドレスです。`GetGPUVirtualAddress()` で得られオフセットを足せば、バッファの途中を指せます。`SizeInBytes` はビューが見せる範囲の大きさで、**頂点の数ではなくバイト数**です。`StrideInBytes` は 1 頂点の大きさで入力レイアウトの合計と `Vertex` 構造体の大きさに一致させます。

## インデックス バッファ ビュー

```cpp
const uint16_t indices[] = {0, 1, 2};

D3D12_INDEX_BUFFER_VIEW index_buffer_view = {};
index_buffer_view.BufferLocation = index_buffer->GetGPUVirtualAddress();
index_buffer_view.SizeInBytes = sizeof(indices);
index_buffer_view.Format = DXGI_FORMAT_R16_UINT;  // 16 ビット（65,536 頂点まで）。32 ビットは R32_UINT
```

`Format` はインデックス 1 つの大きさで、`DXGI_FORMAT_R16_UINT`（`uint16_t`）か `DXGI_FORMAT_R32_UINT`（`uint32_t`）です。頂点が 65,536 個を超えるメッシュは、32 ビットにします。実際の型と合っていないと描画が壊れます。

## コマンド リストに設定して描く

```cpp
command_list->IASetPrimitiveTopology(D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST);  // 三角形のリスト
command_list->IASetVertexBuffers(0, 1, &vertex_buffer_view);                // スロット 0 から 1 個
command_list->IASetIndexBuffer(&index_buffer_view);

command_list->DrawInstanced(3, 1, 0, 0);            // インデックスなし
command_list->DrawIndexedInstanced(3, 1, 0, 0, 0);  // インデックスあり
```

`IASetVertexBuffers` はビューの配列をスロットの番号から順につなぎます。`IASetIndexBuffer` はインデックスのビューをつなぎます。`IASetPrimitiveTopology` は頂点のつなぎ方で `TRIANGLELIST`、`TRIANGLESTRIP`、`LINELIST`、`POINTLIST` などから選びます。描くときはインデックスがなければ `DrawInstanced`、あれば `DrawIndexedInstanced` を使います（[ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md#drawinstanced)）。

トポロジーは 2 か所で決めます。粗い種類（三角形か線か点か）は PSO の `PrimitiveTopologyType`、細かいつなぎ方（リストかストリップか）はコマンド リストの `IASetPrimitiveTopology` です。両方をそろえておきます。

## 頂点バッファを複数に分ける

位置、法線、UV を別々のバッファに分けて持つならビューを配列で渡します。

```cpp
D3D12_VERTEX_BUFFER_VIEW views[3] = {position_view, normal_view, uv_view};
command_list->IASetVertexBuffers(0, 3, views);  // スロット 0、1、2
```

入力レイアウトの `InputSlot`（0、1、2）がそれぞれのビューに対応します。

## インスタンス用の頂点バッファ

インスタンスごとに違うデータ（ワールド行列や色）は、別の頂点バッファ（スロット 1）に置いて、入力レイアウトの `PER_INSTANCE_DATA` で読みます。

```cpp
const D3D12_INPUT_ELEMENT_DESC elements[] = {
    {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0, D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},
    {"WORLD", 0, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 0, D3D12_INPUT_CLASSIFICATION_PER_INSTANCE_DATA, 1},
    {"WORLD", 1, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 16, D3D12_INPUT_CLASSIFICATION_PER_INSTANCE_DATA, 1},
    {"WORLD", 2, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 32, D3D12_INPUT_CLASSIFICATION_PER_INSTANCE_DATA, 1},
    {"WORLD", 3, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 48, D3D12_INPUT_CLASSIFICATION_PER_INSTANCE_DATA, 1},
};
command_list->DrawIndexedInstanced(index_count, instance_count, 0, 0, 0);  // 全インスタンスを 1 回で描く
```

4×4 行列は `float4` を 4 行に分けて、セマンティクスの番号を 0 から 3 にして読みます。最後の 1 は「インスタンス 1 つごとに次のデータへ進む」という意味です。

## 頂点バッファなしで描く

フルスクリーン三角形のように頂点バッファを使わず `SV_VertexID` だけで描くときは、ビューも入力レイアウトも要りません。

```cpp
command_list->IASetPrimitiveTopology(D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
command_list->DrawInstanced(3, 1, 0, 0);  // 頂点バッファは設定しない
```

PSO の `InputLayout` は空にしておきます。

## 毎フレーム変わる頂点

パーティクルや UI のように毎フレーム頂点が変わるものは、UPLOAD のバッファに直接書いて、そのアドレスでビューを作ります。

```cpp
D3D12_VERTEX_BUFFER_VIEW view = {};
view.BufferLocation = upload_vertex_buffer->GetGPUVirtualAddress() + frame_offset;  // フレームごとに別の領域
view.SizeInBytes = vertex_count * sizeof(Vertex);
view.StrideInBytes = sizeof(Vertex);
```

GPU が読んでいる間に同じ領域を書き換えてはいけません。フレームごとに別の領域へ書きます（[Frame Resources](frame-resources.md)）。

## よくあるミス

??? failure "頂点が化ける"
    `StrideInBytes` が入力レイアウトや `Vertex` 構造体の大きさと違います。

??? failure "メッシュが壊れる（インデックス）"
    `Format` がインデックスの型と合っていません（`uint16_t` なのに `R32_UINT` など）。

??? failure "何も描かれない"
    `IASetPrimitiveTopology` を呼んでいないか PSO の `PrimitiveTopologyType` とコマンド リストのトポロジーが合っていません。頂点バッファの状態を `VERTEX_AND_CONSTANT_BUFFER` に切り替え忘れている場合もあります（[Resource Barrier](resource-barrier.md)）。

??? failure "頂点バッファを解放したら、あとでクラッシュする"
    GPU がまだそのバッファを読んでいます。フェンスで完了を待ってから解放します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 頂点とインデックスのビューは、ヒープに入れない小さな構造体
    - [x] 頂点は `BufferLocation`、`SizeInBytes`、`StrideInBytes`。インデックスは `Format` を足す
    - [x] `IASetVertexBuffers`、`IASetIndexBuffer`、`IASetPrimitiveTopology`、`DrawIndexedInstanced` を使う
    - [x] PSO とコマンド リストのトポロジーをそろえる
    - [x] 頂点バッファなしの描画は、ビューが不要で入力レイアウトは空

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md)
- [Upload Buffer](upload-buffer.md)
- [PSO](pso.md)
- [Drawing a Triangle](triangle.md)
- [Microsoft Learn: D3D12_VERTEX_BUFFER_VIEW](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/ns-d3d12-d3d12_vertex_buffer_view)
