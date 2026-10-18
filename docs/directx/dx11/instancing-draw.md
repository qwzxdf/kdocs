---
title: Instanced Drawing
tags:
  - DirectX
---

# Instanced Drawing

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

<strong>インスタンス描画</strong>は、<strong>同じメッシュを、位置や色だけ変えて、何千個も、1 回の命令で、描く</strong>仕組みです。木、草、岩、弾、パーティクルのように、同じ形が、大量に、並ぶものを、1 つずつ、`Draw` すると、CPU が、命令の、発行で、手一杯になります（ドロー コールの、ボトルネック）。インスタンス描画は、1 回の `DrawIndexedInstanced` で、まとめます。

!!! tip "ポイント"
    - 1 回の命令で、同じメッシュを、N 個描く。物ごとの、違い（位置、色）は、<strong>インスタンス データ</strong>で、渡す。
    - インスタンス データの、渡し方は、2 通り。<strong>入力レイアウトの `PER_INSTANCE_DATA`</strong>（頂点バッファの 2 本目）、または、<strong>`StructuredBuffer` を `SV_InstanceID` で、引く</strong>。
    - 描画は `DrawIndexedInstanced`（`DrawInstanced`）。
    - インスタンスの数が、GPU で決まるなら、`DrawIndexedInstancedIndirect`（間接描画）。
    - ドロー コールを、減らす、最も、基本の手段（[Draw Calls](../../rendering/draw-calls.md)）。

## 方法 1：PER_INSTANCE_DATA（頂点バッファの 2 本目）

メッシュの、頂点バッファ（スロット 0）に、加えて、<strong>インスタンスごとの、データ</strong>を、入れた、バッファ（スロット 1）を、用意します。

```cpp
struct InstanceData {
  DirectX::XMFLOAT4X4 world;      // 物ごとのワールド行列（64 バイト）
  DirectX::XMFLOAT4 color;        // 物ごとの色（16 バイト）
};
```

```cpp
const D3D11_INPUT_ELEMENT_DESC elements[] = {
    // スロット 0: メッシュの頂点（頂点ごと）
    {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0, D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"NORMAL",   0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 12, D3D11_INPUT_PER_VERTEX_DATA, 0},
    // スロット 1: インスタンス データ（インスタンスごと）。4×4 行列は、float4 を 4 本に、分けて渡す。
    {"WORLD", 0, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 0,  D3D11_INPUT_PER_INSTANCE_DATA, 1},
    {"WORLD", 1, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 16, D3D11_INPUT_PER_INSTANCE_DATA, 1},
    {"WORLD", 2, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 32, D3D11_INPUT_PER_INSTANCE_DATA, 1},
    {"WORLD", 3, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 48, D3D11_INPUT_PER_INSTANCE_DATA, 1},
    {"COLOR", 0, DXGI_FORMAT_R32G32B32A32_FLOAT, 1, 64, D3D11_INPUT_PER_INSTANCE_DATA, 1},
};
```

`PER_INSTANCE_DATA` の、要素は、<strong>インスタンスが、1 つ進むごと</strong>（最後の引数 `1`）に、次の、データに、進みます。1 つの要素は、最大 16 バイトなので、4×4 行列は、`float4` の 4 要素（`WORLD0`〜`WORLD3`）に、分けます。

```hlsl
struct VSInput {
  float3 position : POSITION;
  float3 normal : NORMAL;
  row_major float4x4 world : WORLD;     // WORLD0〜3 が、行列として、まとまる
  float4 color : COLOR;
};

VSOutput VSMain(VSInput input) {
  VSOutput output;
  float4 world_position = mul(float4(input.position, 1.0), input.world);
  output.position = mul(world_position, view_projection);
  output.color = input.color;
  return output;
}
```

```cpp
ID3D11Buffer* buffers[] = {mesh_vertex_buffer.Get(), instance_buffer.Get()};
UINT strides[] = {sizeof(Vertex), sizeof(InstanceData)};
UINT offsets[] = {0, 0};
context->IASetVertexBuffers(0, 2, buffers, strides, offsets);
context->IASetIndexBuffer(index_buffer.Get(), DXGI_FORMAT_R16_UINT, 0);
context->DrawIndexedInstanced(index_count, instance_count, 0, 0, 0);
```

## 方法 2：StructuredBuffer と SV_InstanceID

インスタンス データを、<strong>構造化バッファ</strong>に、入れて、頂点シェーダーが、`SV_InstanceID` で、引きます。入力レイアウトに、インスタンスの要素が、要らず、構造体を、自由に、設計できます。

```hlsl
struct InstanceData {
  row_major float4x4 world;
  float4 color;
};
StructuredBuffer<InstanceData> g_instances : register(t0);

VSOutput VSMain(VSInput input, uint instance_id : SV_InstanceID) {
  InstanceData instance = g_instances[instance_id];
  float4 world_position = mul(float4(input.position, 1.0), instance.world);
  ...
}
```

```cpp
// 構造化バッファを作り、SRV を、頂点シェーダーに、つなぐ。
D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = sizeof(InstanceData) * max_instances;
desc.Usage = D3D11_USAGE_DYNAMIC;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE;
desc.CPUAccessFlags = D3D11_CPU_ACCESS_WRITE;
desc.MiscFlags = D3D11_RESOURCE_MISC_BUFFER_STRUCTURED;
desc.StructureByteStride = sizeof(InstanceData);
device->CreateBuffer(&desc, nullptr, &instance_buffer);

D3D11_SHADER_RESOURCE_VIEW_DESC srv_desc = {};
srv_desc.Format = DXGI_FORMAT_UNKNOWN;                      // 構造化バッファは、UNKNOWN
srv_desc.ViewDimension = D3D11_SRV_DIMENSION_BUFFER;
srv_desc.Buffer.NumElements = max_instances;
device->CreateShaderResourceView(instance_buffer.Get(), &srv_desc, &instance_srv);

context->VSSetShaderResources(0, 1, instance_srv.GetAddressOf());
context->DrawIndexedInstanced(index_count, instance_count, 0, 0, 0);
```

構造化バッファの、作り方は、[Structured and Raw Buffers](structured-buffer.md) です。計算シェーダーで、カリングした結果を、そのまま、描画に、使う場合（GPU ドリブン）は、この方法が、向いています（[GPU Driven Rendering](../../rendering/gpu-driven.md)）。

| | `PER_INSTANCE_DATA` | `StructuredBuffer` + `SV_InstanceID` |
| --- | --- | --- |
| 入力レイアウト | インスタンスの要素が、要る | 要らない |
| 構造体の自由度 | 1 要素 16 バイトまで、分ける | 自由 |
| 計算シェーダーとの連携 | UAV で、書いた、バッファを、頂点バッファに（`BIND_VERTEX_BUFFER` と `BIND_UNORDERED_ACCESS` は、同時に不可の場合あり） | UAV で書いて、SRV で、読める |
| 向く場面 | 単純な、インスタンス（草、弾） | 大量・複雑な、データ、GPU カリング |

## 描画関数

```cpp
context->DrawIndexedInstanced(IndexCountPerInstance,   // 1 インスタンスの、インデックスの数
                              InstanceCount,           // インスタンスの数
                              StartIndexLocation,      // インデックス バッファの、開始位置
                              BaseVertexLocation,      // 各インデックスに、足す値
                              StartInstanceLocation);  // インスタンス ID の、開始値（SV_InstanceID の、基準）
```

| 関数 | 内容 |
| --- | --- |
| `DrawInstanced(VertexCountPerInstance, InstanceCount, StartVertexLocation, StartInstanceLocation)` | インデックスなしで、インスタンス描画 |
| `DrawIndexedInstanced(…)` | インデックスつき |
| `DrawInstancedIndirect(buffer, offset)` | 引数を、GPU のバッファから、読む |
| `DrawIndexedInstancedIndirect(buffer, offset)` | インデックスつき、間接 |

## 間接描画（Indirect）

描画の引数（インデックスの数、インスタンスの数など）を、<strong>GPU 上のバッファ</strong>に、置き、CPU を、介さず、描きます。計算シェーダーで、カリングして、描く数が、GPU で、決まるときに、使います。

```cpp
// 引数バッファ: D3D11_DRAW_INDEXED_INSTANCED_INDIRECT_ARGS の形（5 つの uint）。
D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = 5 * sizeof(UINT);
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_UNORDERED_ACCESS;
desc.MiscFlags = D3D11_RESOURCE_MISC_DRAWINDIRECT_ARGS | D3D11_RESOURCE_MISC_BUFFER_ALLOW_RAW_VIEWS;
device->CreateBuffer(&desc, nullptr, &args_buffer);

context->DrawIndexedInstancedIndirect(args_buffer.Get(), 0);   // 引数は、バッファの、先頭から
```

引数バッファの、中身は、`IndexCountPerInstance`、`InstanceCount`、`StartIndexLocation`、`BaseVertexLocation`、`StartInstanceLocation` の、5 つの `uint` です。計算シェーダーが、`InstanceCount` を、書き込みます（[Compute Shader](compute-shader.md)）。`CopyStructureCount` で、追加型の、構造化バッファの、要素数を、引数バッファへ、コピーする方法も、あります。

## ドロー コールを、減らす、効果

| 方法 | 1000 本の木を描くときの、ドロー コール |
| --- | --- |
| 1 本ずつ `DrawIndexed` | 1000 回 |
| `DrawIndexedInstanced`（同じ木） | 1 回 |
| 種類の違う木（5 種類）ごとに、インスタンス描画 | 5 回 |

ドロー コールが、数千回を、超えると、CPU の、ドライバーの、処理が、ボトルネックに、なります。インスタンス描画で、数十回に、減らせます。

## よくあるミス

??? failure "全部の、インスタンスが、同じ位置に、描かれる"
    `PER_INSTANCE_DATA` の、`InstanceDataStepRate` が 0（頂点ごと）。`1` にする。または、`SV_InstanceID` で、バッファを、引いていない。

??? failure "入力レイアウトの作成が、失敗する（行列）"
    `WORLD` の、セマンティクス番号（`WORLD0`〜`WORLD3`）が、シェーダーの、`float4x4` の、入力と、合っていない。4 つの `float4` に、分けて、書く。

??? failure "インスタンスの、一部だけ、描かれる"
    バッファの、要素数が、`InstanceCount` より、少ない。`DYNAMIC` バッファの、`Map` で、全インスタンスぶん、書いていない。

??? failure "大量のインスタンスで、フレームレートが、落ちる"
    見えない物（視錐台の外、遠すぎる物）も、描いている。カリングしてから、インスタンス バッファを、作る（[Culling](../../rendering/culling.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] インスタンス描画 ＝ 同じメッシュを、1 回の命令で、N 個描く。ドロー コールを、減らす基本
    - [x] インスタンス データは、`PER_INSTANCE_DATA`（2 本目の頂点バッファ）か、`StructuredBuffer` + `SV_InstanceID`
    - [x] 描画は `DrawIndexedInstanced`
    - [x] 4×4 行列は、`float4` の 4 要素に、分けて、入力する
    - [x] 描く数が、GPU で決まるなら、間接描画（`…Indirect`）

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Input Layout](input-layout.md)
- [Structured and Raw Buffers](structured-buffer.md)
- [Draw Calls](../../rendering/draw-calls.md)
- [GPU Driven Rendering](../../rendering/gpu-driven.md)
- [Microsoft Learn: ID3D11DeviceContext::DrawIndexedInstanced](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11devicecontext-drawindexedinstanced)
