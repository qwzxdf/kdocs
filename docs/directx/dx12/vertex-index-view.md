---
title: Vertex and Index Buffer Views
tags:
  - DirectX
---

# Vertex and Index Buffer Views

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

頂点バッファと、インデックス バッファは、<strong>普通の、バッファ（`ID3D12Resource`）</strong>で、特別な、リソースでは、ありません。描画で、使うときは、バッファの、<strong>GPU アドレスと、大きさ、1 頂点の、大きさ</strong>を、まとめた、<strong>ビュー</strong>（`D3D12_VERTEX_BUFFER_VIEW`、`D3D12_INDEX_BUFFER_VIEW`）を、作り、コマンド リストに、渡します。これらの、ビューは、ディスクリプタ ヒープに、入れず、<strong>小さな構造体のまま</strong>、渡します。

!!! tip "ポイント"
    - 頂点・インデックスの、ビューは、<strong>構造体</strong>（ディスクリプタ ヒープに、置かない）。
    - 頂点バッファ ビュー: `BufferLocation`（GPU アドレス）、`SizeInBytes`、`StrideInBytes`（1 頂点の大きさ）。
    - インデックス バッファ ビュー: `BufferLocation`、`SizeInBytes`、`Format`（`R16_UINT` か `R32_UINT`）。
    - バッファは、DEFAULT ヒープに、置き、アップロードで、送る（[Upload Buffer](upload-buffer.md)）。
    - 入力レイアウトは、PSO の中（[PSO](pso.md)）。

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
| `BufferLocation` | バッファの、GPU 仮想アドレス（`GetGPUVirtualAddress()`）。オフセットを、足して、一部だけ、指せる |
| `SizeInBytes` | ビューが、見せる、範囲の大きさ |
| `StrideInBytes` | 1 頂点の大きさ。入力レイアウトの、合計と、一致 |

## インデックス バッファ ビュー

```cpp
const uint16_t indices[] = {0, 1, 2};

D3D12_INDEX_BUFFER_VIEW index_buffer_view = {};
index_buffer_view.BufferLocation = index_buffer->GetGPUVirtualAddress();
index_buffer_view.SizeInBytes = sizeof(indices);
index_buffer_view.Format = DXGI_FORMAT_R16_UINT;                              // 16 ビット（65,536 頂点まで）。32 ビットは R32_UINT
```

## コマンド リストに、設定して、描く

```cpp
command_list->IASetPrimitiveTopology(D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST);    // 三角形リスト
command_list->IASetVertexBuffers(0, 1, &vertex_buffer_view);                  // スロット 0 から、1 個
command_list->IASetIndexBuffer(&index_buffer_view);

command_list->DrawInstanced(3, 1, 0, 0);                                      // インデックスなし
command_list->DrawIndexedInstanced(3, 1, 0, 0, 0);                            // インデックスあり
```

| 関数 | 内容 |
| --- | --- |
| `IASetVertexBuffers(StartSlot, NumViews, pViews)` | 頂点バッファ ビューの、配列を、スロットに、つなぐ |
| `IASetIndexBuffer(pView)` | インデックス バッファ ビューを、つなぐ |
| `IASetPrimitiveTopology(topology)` | 頂点の、つなぎ方（`TRIANGLELIST`、`TRIANGLESTRIP`、`LINELIST`、`POINTLIST`） |
| `DrawInstanced(VertexCountPerInstance, InstanceCount, StartVertexLocation, StartInstanceLocation)` | インデックスなしの、描画 |
| `DrawIndexedInstanced(IndexCountPerInstance, InstanceCount, StartIndexLocation, BaseVertexLocation, StartInstanceLocation)` | インデックスありの、描画 |

トポロジーの、<strong>粗い種類</strong>（三角形か、線か、点か）は、PSO（`PrimitiveTopologyType`）に、<strong>細かい</strong>つなぎ方（リストか、ストリップか）は、コマンド リスト（`IASetPrimitiveTopology`）に、指定します。両方を、そろえます。

## 複数の、頂点バッファ

位置・法線・uv を、別々の、バッファに、分けて、持つときは、ビューを、配列で、渡します。

```cpp
D3D12_VERTEX_BUFFER_VIEW views[3] = {position_view, normal_view, uv_view};
command_list->IASetVertexBuffers(0, 3, views);                                // スロット 0、1、2
```

入力レイアウトの、`InputSlot`（0、1、2）が、各ビューに、対応します。

## インスタンス用の、頂点バッファ

インスタンスごとの、データ（ワールド行列、色）は、別の頂点バッファ（スロット 1）に、置き、入力レイアウトの、`PER_INSTANCE_DATA` で、読みます。

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

## 頂点バッファなしの、描画

フルスクリーン三角形のように、頂点バッファを、使わず、`SV_VertexID` だけで、描くときは、ビューも、入力レイアウトも、不要です。

```cpp
command_list->IASetPrimitiveTopology(D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
command_list->DrawInstanced(3, 1, 0, 0);                                      // 頂点バッファは、設定しない
```

PSO の `InputLayout` は、空にします。

## 動的な、頂点バッファ

毎フレーム変わる、頂点は、UPLOAD ヒープの、バッファに、直接、書き、そのアドレスで、ビューを、作ります。

```cpp
D3D12_VERTEX_BUFFER_VIEW view = {};
view.BufferLocation = upload_vertex_buffer->GetGPUVirtualAddress() + frame_offset;   // フレームごとに、別の領域
view.SizeInBytes = vertex_count * sizeof(Vertex);
view.StrideInBytes = sizeof(Vertex);
```

GPU が、読んでいる間に、同じ領域を、書き換えないよう、<strong>フレームごとに、別の領域</strong>に、書きます（[Frame Resources](frame-resources.md)）。

## よくあるミス

??? failure "頂点が、化ける"
    `StrideInBytes` が、入力レイアウトと、`Vertex` 構造体の、大きさと、違う。

??? failure "メッシュが、壊れる（インデックス）"
    `Format` が、インデックスの、型と、合っていない（`uint16_t` に `R32_UINT`）。

??? failure "何も、描かれない"
    `IASetPrimitiveTopology` を、呼んでいない。PSO の `PrimitiveTopologyType` と、コマンド リストの、トポロジーが、合っていない。頂点バッファの、状態が、`VERTEX_AND_CONSTANT_BUFFER` に、遷移していない（[Resource Barrier](resource-barrier.md)）。

??? failure "頂点バッファを、解放したら、後で、クラッシュする"
    GPU が、まだ、そのバッファを、読んでいる。フェンスで、完了を、待ってから、解放する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 頂点・インデックスの、ビューは、ヒープに、入れない、小さな、構造体
    - [x] 頂点: `BufferLocation`・`SizeInBytes`・`StrideInBytes`。インデックス: 同じく `Format`
    - [x] `IASetVertexBuffers`、`IASetIndexBuffer`、`IASetPrimitiveTopology`、`DrawIndexedInstanced`
    - [x] PSO と、コマンド リストの、トポロジーを、そろえる
    - [x] 頂点バッファなしの描画は、ビュー不要、入力レイアウトは、空

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Upload Buffer](upload-buffer.md)
- [PSO](pso.md)
- [Drawing a Triangle](triangle.md)
- [Microsoft Learn: D3D12_VERTEX_BUFFER_VIEW](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/ns-d3d12-d3d12_vertex_buffer_view)
