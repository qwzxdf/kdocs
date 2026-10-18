---
title: Vertex and Index Buffer Views
tags:
  - DirectX
---

# Vertex and Index Buffer Views

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

頂点バッファとインデックス バッファは、<strong>普通のバッファ（`ID3D12Resource`）</strong>で特別なリソースではありません。描画で使うときはバッファの <strong>GPU アドレスと大きさ 1 頂点の大きさ</strong>をまとめた、<strong>ビュー</strong>（`D3D12_VERTEX_BUFFER_VIEW`、`D3D12_INDEX_BUFFER_VIEW`）を作りコマンド リストに渡します。これらのビューはディスクリプタ ヒープに入れず <strong>小さな構造体のまま</strong>、渡します。

!!! tip "ポイント"
    - 頂点・インデックスのビューは <strong>構造体</strong>（ディスクリプタ ヒープに、置かない）。
    - 頂点バッファ ビュー: `BufferLocation`（GPU アドレス）、`SizeInBytes`、`StrideInBytes`（1 頂点の大きさ）。
    - インデックス バッファ ビュー: `BufferLocation`、`SizeInBytes`、`Format`（`R16_UINT` か `R32_UINT`）。
    - バッファは DEFAULT ヒープに置きアップロードで送る（[Upload Buffer](upload-buffer.md)）。
    - 入力レイアウトは PSO の中（[PSO](pso.md)）。

## 頂点バッファ ビュー

```cpp
struct Vertex {
  DirectX::XMFLOAT3 position;
  DirectX::XMFLOAT4 color;
};

const Vertex vertices[] = {
    {{0.0f, 0.5f, 0.0f}, {1, 0, 0, 1}},       // 反時計回りが表
    {{-0.5f, -0.5f, 0.0f}, {0, 1, 0, 1}},
    {{0.5f, -0.5f, 0.0f}, {0, 0, 1, 1}},
};

// vertex_buffer（DEFAULT ヒープ）を作り、vertices をアップロードした後（upload-buffer.md）:
D3D12_VERTEX_BUFFER_VIEW vertex_buffer_view = {};
vertex_buffer_view.BufferLocation = vertex_buffer->GetGPUVirtualAddress();   // GPU 上の、バッファの先頭アドレス
vertex_buffer_view.SizeInBytes = sizeof(vertices);                            // バッファの、大きさ（バイト）
vertex_buffer_view.StrideInBytes = sizeof(Vertex);                            // 1 頂点の大きさ
```

| メンバー | 内容 |
| --- | --- |
| `BufferLocation` | バッファの GPU 仮想アドレス（`GetGPUVirtualAddress()`）。オフセットを足して一部だけ指せる |
| `SizeInBytes` | ビューが見せる範囲の大きさ |
| `StrideInBytes` | 1 頂点の大きさ。入力レイアウトの合計と一致 |

## インデックス バッファ ビュー

```cpp
const uint16_t indices[] = {0, 1, 2};

D3D12_INDEX_BUFFER_VIEW index_buffer_view = {};
index_buffer_view.BufferLocation = index_buffer->GetGPUVirtualAddress();
index_buffer_view.SizeInBytes = sizeof(indices);
index_buffer_view.Format = DXGI_FORMAT_R16_UINT;                              // 16 ビット（65,536 頂点まで）。32 ビットは R32_UINT
```

## コマンド リストに設定して描く

```cpp
command_list->IASetPrimitiveTopology(D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST);    // 三角形リスト
command_list->IASetVertexBuffers(0, 1, &vertex_buffer_view);                  // スロット 0 から、1 個
command_list->IASetIndexBuffer(&index_buffer_view);

command_list->DrawInstanced(3, 1, 0, 0);                                      // インデックスなし
command_list->DrawIndexedInstanced(3, 1, 0, 0, 0);                            // インデックスあり
```

| 関数 | 内容 |
| --- | --- |
| `IASetVertexBuffers(StartSlot, NumViews, pViews)` | 頂点バッファ ビューの配列をスロットにつなぐ |
| `IASetIndexBuffer(pView)` | インデックス バッファ ビューをつなぐ |
| `IASetPrimitiveTopology(topology)` | 頂点のつなぎ方（`TRIANGLELIST`、`TRIANGLESTRIP`、`LINELIST`、`POINTLIST`） |
| `DrawInstanced(VertexCountPerInstance, InstanceCount, StartVertexLocation, StartInstanceLocation)` | インデックスなしの描画 |
| `DrawIndexedInstanced(IndexCountPerInstance, InstanceCount, StartIndexLocation, BaseVertexLocation, StartInstanceLocation)` | インデックスありの描画 |

トポロジーの <strong>粗い種類</strong>（三角形か線か点か）は PSO（`PrimitiveTopologyType`）に <strong>細かい</strong>つなぎ方（リストか、ストリップか）はコマンド リスト（`IASetPrimitiveTopology`）に指定します。両方をそろえます。

## 複数の頂点バッファ

位置・法線・uv を別々のバッファに分けて、持つときはビューを配列で渡します。

```cpp
D3D12_VERTEX_BUFFER_VIEW views[3] = {position_view, normal_view, uv_view};
command_list->IASetVertexBuffers(0, 3, views);                                // スロット 0、1、2
```

入力レイアウトの `InputSlot`（0、1、2）が各ビューに対応します。

## インスタンス用の頂点バッファ

インスタンスごとのデータ（ワールド行列、色）は別の頂点バッファ（スロット 1）に置き入力レイアウトの `PER_INSTANCE_DATA` で読みます。

```cpp
const D3D12_INPUT_ELEMENT_DESC elements[] = {
    {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0, D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},
    {"WORLD",    0, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 0,  D3D12_INPUT_CLASSIFICATION_PER_INSTANCE_DATA, 1},
    {"WORLD",    1, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 16, D3D12_INPUT_CLASSIFICATION_PER_INSTANCE_DATA, 1},
    {"WORLD",    2, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 32, D3D12_INPUT_CLASSIFICATION_PER_INSTANCE_DATA, 1},
    {"WORLD",    3, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 48, D3D12_INPUT_CLASSIFICATION_PER_INSTANCE_DATA, 1},
};
command_list->DrawIndexedInstanced(index_count, instance_count, 0, 0, 0);     // インスタンスを、1 回で、描く
```

## 頂点バッファなしの描画

フルスクリーン三角形のように頂点バッファを使わず `SV_VertexID` だけで、描くときはビューも入力レイアウトも不要です。

```cpp
command_list->IASetPrimitiveTopology(D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
command_list->DrawInstanced(3, 1, 0, 0);                                      // 頂点バッファは、設定しない
```

PSO の `InputLayout` は空にします。

## 動的な頂点バッファ

毎フレーム変わる頂点は UPLOAD ヒープのバッファに直接、書きそのアドレスでビューを作ります。

```cpp
D3D12_VERTEX_BUFFER_VIEW view = {};
view.BufferLocation = upload_vertex_buffer->GetGPUVirtualAddress() + frame_offset;   // フレームごとに、別の領域
view.SizeInBytes = vertex_count * sizeof(Vertex);
view.StrideInBytes = sizeof(Vertex);
```

GPU が読んでいる間に同じ領域を書き換えないよう <strong>フレームごとに別の領域</strong>に書きます（[Frame Resources](frame-resources.md)）。

## よくあるミス

??? failure "頂点が、化ける"
    `StrideInBytes` が入力レイアウトと `Vertex` 構造体の大きさと違う。

??? failure "メッシュが、壊れる（インデックス）"
    `Format` がインデックスの型と合っていない（`uint16_t` に `R32_UINT`）。

??? failure "何も描かれない"
    `IASetPrimitiveTopology` を呼んでいない。PSO の `PrimitiveTopologyType` とコマンド リストのトポロジーが合っていない。頂点バッファの状態が `VERTEX_AND_CONSTANT_BUFFER` に遷移していない（[Resource Barrier](resource-barrier.md)）。

??? failure "頂点バッファを解放したら後でクラッシュする"
    GPU がまだそのバッファを読んでいる。フェンスで完了を待ってから解放する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 頂点・インデックスのビューはヒープに入れない小さな構造体
    - [x] 頂点: `BufferLocation`・`SizeInBytes`・`StrideInBytes`。インデックス: 同じく `Format`
    - [x] `IASetVertexBuffers`、`IASetIndexBuffer`、`IASetPrimitiveTopology`、`DrawIndexedInstanced`
    - [x] PSO とコマンド リストのトポロジーをそろえる
    - [x] 頂点バッファなしの描画は、ビュー不要、入力レイアウトは空

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Upload Buffer](upload-buffer.md)
- [PSO](pso.md)
- [Drawing a Triangle](triangle.md)
- [Microsoft Learn: D3D12_VERTEX_BUFFER_VIEW](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/ns-d3d12-d3d12_vertex_buffer_view)
