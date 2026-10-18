---
title: Vertex Buffer
tags:
  - DirectX
---

# Vertex Buffer

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>頂点バッファ</strong>は、メッシュの、<strong>頂点のデータ</strong>（位置、法線、uv、色など）を、GPU のメモリに、並べた、バッファです。三角形を描くには、頂点の、データを、頂点バッファに、入れて、パイプラインに、つなぎます。

!!! tip "ポイント"
    - 頂点バッファ ＝ 頂点の配列を、GPU に置いたもの。`CreateBuffer` で、`D3D11_BIND_VERTEX_BUFFER` を指定して作る。
    - 1 頂点のデータの、大きさが、<strong>ストライド</strong>。つなぐとき、ストライドと、オフセットを、渡す。
    - 変わらない、メッシュは、`D3D11_USAGE_IMMUTABLE`（作成時に、初期データを、渡す）。毎フレーム、変わるものは、`DYNAMIC`。
    - 頂点のデータの、<strong>並び</strong>は、入力レイアウトで、GPU に、教える（[Input Layout](input-layout.md)）。
    - 座標系は、右手系・Y 上。三角形は、反時計回り（CCW）が、表。

## 頂点の、構造体

```cpp
#include <DirectXMath.h>

struct Vertex {
  DirectX::XMFLOAT3 position;     // 12 バイト
  DirectX::XMFLOAT4 color;        // 16 バイト → 1 頂点 28 バイト
};

// 三角形: 反時計回り（CCW）が表。クリップ空間の座標を、そのまま使う（変換なし）。
const Vertex vertices[] = {
    {{0.0f, 0.5f, 0.0f}, {1.0f, 0.0f, 0.0f, 1.0f}},       // 上: 赤
    {{-0.5f, -0.5f, 0.0f}, {0.0f, 1.0f, 0.0f, 1.0f}},     // 左下: 緑
    {{0.5f, -0.5f, 0.0f}, {0.0f, 0.0f, 1.0f, 1.0f}},      // 右下: 青
};
```

`Vertex` の並び（位置 3 つの `float`、色 4 つの `float`）が、そのまま、GPU に、渡るメモリの並びです。入力レイアウトは、この並びを、記述します。上の、3 頂点は、上、左下、右下の順で、`y` が上向きの、座標で、反時計回りです。

## 作る

```cpp
D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = sizeof(vertices);                         // バッファ全体の大きさ（バイト）
desc.Usage = D3D11_USAGE_IMMUTABLE;                        // 作ったら、変更しない
desc.BindFlags = D3D11_BIND_VERTEX_BUFFER;                 // 頂点バッファとして使う
desc.CPUAccessFlags = 0;

D3D11_SUBRESOURCE_DATA init = {};
init.pSysMem = vertices;                                   // 初期データ（CPU のメモリ）

Microsoft::WRL::ComPtr<ID3D11Buffer> vertex_buffer;
device->CreateBuffer(&desc, &init, &vertex_buffer);
```

| メンバー | 内容 |
| --- | --- |
| `ByteWidth` | バッファの大きさ（バイト） |
| `Usage` | `IMMUTABLE`（変更しない）、`DEFAULT`（GPU が読み書き）、`DYNAMIC`（CPU が、毎フレーム書く）、`STAGING`（CPU が、読み書き） |
| `BindFlags` | `VERTEX_BUFFER`、`INDEX_BUFFER`、`CONSTANT_BUFFER`、`SHADER_RESOURCE` など。複数の、OR も、可能 |
| `CPUAccessFlags` | `DYNAMIC` のとき `WRITE` |
| `StructureByteStride` | 構造化バッファのとき、1 要素の大きさ |

`Usage` の、選び方は、[Map, Unmap and UpdateSubresource](map-update.md) です。

## パイプラインにつなぐ

```cpp
const UINT stride = sizeof(Vertex);                        // 1 頂点の大きさ（28 バイト）
const UINT offset = 0;                                     // バッファの、先頭から、何バイト目から、使うか
context->IASetVertexBuffers(0, 1, vertex_buffer.GetAddressOf(), &stride, &offset);
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
```

| 引数 | 内容 |
| --- | --- |
| `StartSlot` | 入力スロット（0〜15）。入力レイアウトの、`InputSlot` と、対応 |
| `NumBuffers` | つなぐ、バッファの数 |
| `ppVertexBuffers` | バッファの、配列 |
| `pStrides` | 各バッファの、1 頂点の、大きさ |
| `pOffsets` | 各バッファの、使い始める、位置（バイト） |

`IASetPrimitiveTopology` で、頂点の、つなぎ方を、決めます。

| 値 | 内容 |
| --- | --- |
| `TRIANGLELIST` | 3 頂点ごとに、三角形 1 つ（最も、普通） |
| `TRIANGLESTRIP` | 前の 2 頂点を、共有して、三角形を、つなぐ |
| `LINELIST` | 2 頂点ごとに、線 1 本（デバッグ描画） |
| `POINTLIST` | 点（パーティクル） |

## 複数のバッファに、分ける

位置・法線・uv を、別々の、バッファに、分けて、持つこともできます（SoA）。

```cpp
ID3D11Buffer* buffers[] = {position_buffer.Get(), normal_buffer.Get(), uv_buffer.Get()};
UINT strides[] = {sizeof(XMFLOAT3), sizeof(XMFLOAT3), sizeof(XMFLOAT2)};
UINT offsets[] = {0, 0, 0};
context->IASetVertexBuffers(0, 3, buffers, strides, offsets);
```

シャドウ パスのように、位置だけを、使う描画では、位置のバッファだけを、つなぐと、読み込む、データが、減ります。入力レイアウトの、`InputSlot`（0、1、2）が、各バッファに、対応します。

## 描く

```cpp
context->Draw(3, 0);                                       // 頂点 3 つ、先頭（0 番）から
```

インデックス バッファを、使う描画は、[Index Buffer](index-buffer.md) です。

## 動的な頂点バッファ

毎フレーム、頂点が変わる（パーティクル、UI の四角形）ときは、`DYNAMIC` で作り、`Map` で、書きます。

```cpp
desc.Usage = D3D11_USAGE_DYNAMIC;
desc.CPUAccessFlags = D3D11_CPU_ACCESS_WRITE;
desc.ByteWidth = sizeof(Vertex) * kMaxVertices;
device->CreateBuffer(&desc, nullptr, &dynamic_vertex_buffer);

// 毎フレーム:
D3D11_MAPPED_SUBRESOURCE mapped;
context->Map(dynamic_vertex_buffer.Get(), 0, D3D11_MAP_WRITE_DISCARD, 0, &mapped);
std::memcpy(mapped.pData, vertices.data(), sizeof(Vertex) * vertices.size());
context->Unmap(dynamic_vertex_buffer.Get(), 0);
```

`WRITE_DISCARD` は、GPU が、前のフレームを、読んでいても、待たず、新しい領域を、渡します（[Map, Unmap and UpdateSubresource](map-update.md)）。

## よくあるミス

??? failure "三角形が、見えない（クリアの色のまま）"
    頂点が、時計回り（CW）で、裏面として、捨てられている。ラスタライザー ステートの `FrontCounterClockwise = TRUE`（このサイトの規約）にするか、頂点の順序を、変える（[Rasterizer State](rasterizer-state.md)）。

??? failure "頂点が、化けて、ぐちゃぐちゃに見える"
    入力レイアウトの、フォーマットや、オフセットが、`Vertex` 構造体と、合っていない。ストライドが、間違っている。

??? failure "`IMMUTABLE` なのに、`Map` しようとして、失敗する"
    `IMMUTABLE` は、作成後に、変更できない。変えたいなら、`DYNAMIC`（毎フレーム）か、`DEFAULT` と `UpdateSubresource`。

??? failure "バッファの、一部だけを、描くつもりが、全部描かれる"
    `Draw` の、第 2 引数（`StartVertexLocation`）と、`IASetVertexBuffers` の、オフセットの、使い分けを、混同している。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 頂点バッファ ＝ 頂点データの配列。`CreateBuffer` + `D3D11_BIND_VERTEX_BUFFER`
    - [x] 変わらないなら `IMMUTABLE`、毎フレームなら `DYNAMIC` + `Map`
    - [x] ストライド ＝ 1 頂点の大きさ。`IASetVertexBuffers` に渡す
    - [x] 並びは、入力レイアウトで教える
    - [x] 三角形は、反時計回りが表

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Index Buffer](index-buffer.md)
- [Input Layout](input-layout.md)
- [Drawing a Triangle](triangle.md)
- [Map, Unmap and UpdateSubresource](map-update.md)
- [Microsoft Learn: ID3D11Device::CreateBuffer](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createbuffer)
