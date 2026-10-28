---
title: Vertex Buffer
tags:
  - DirectX
---

# Vertex Buffer

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>頂点バッファ</strong>はメッシュの <strong>頂点のデータ</strong>（位置、法線、uv、色など）を GPU のメモリに並べたバッファです。三角形を描くには頂点のデータを頂点バッファに入れてパイプラインにつなぎます。

!!! tip "ポイント"
    - 頂点バッファ ＝ 頂点の配列を GPU に置いたもの。`CreateBuffer` で `D3D11_BIND_VERTEX_BUFFER` を指定して作る。
    - 1 頂点のデータの大きさが <strong>ストライド</strong>。つなぐときストライドとオフセットを渡す。
    - 変わらないメッシュは `D3D11_USAGE_IMMUTABLE`（作成時に初期データを渡す）。毎フレーム、変わるものは `DYNAMIC`。
    - 頂点のデータの <strong>並び</strong>は、入力レイアウトで GPU に教える（[Input Layout](input-layout.md)）。
    - 座標系は左手系・Y 上。三角形は時計回り（CW）が表。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

## 頂点の構造体

```cpp
#include <DirectXMath.h>

struct Vertex {
  DirectX::XMFLOAT3 position;     // 12 バイト
  DirectX::XMFLOAT4 color;        // 16 バイト → 1 頂点 28 バイト
};

// 三角形: 時計回り（CW）が表。クリップ空間の座標をそのまま使う（変換なし）。
const Vertex vertices[] = {
    {{0.0f, 0.5f, 0.0f}, {1.0f, 0.0f, 0.0f, 1.0f}},       // 上: 赤
    {{0.5f, -0.5f, 0.0f}, {0.0f, 0.0f, 1.0f, 1.0f}},      // 右下: 青
    {{-0.5f, -0.5f, 0.0f}, {0.0f, 1.0f, 0.0f, 1.0f}},     // 左下: 緑
};
```

`Vertex` の並び（位置 3 つの `float`、色 4 つの `float`）がそのまま GPU に渡るメモリの並びです。入力レイアウトはこの並びを記述します。上の 3 頂点は上、右下、左下の順で `y` が上向きの座標で、時計回りです。

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
| `Usage` | `IMMUTABLE`（変更しない）、`DEFAULT`（GPU が読み書き）、`DYNAMIC`（CPU が毎フレーム書く）、`STAGING`（CPU が読み書き） |
| `BindFlags` | `VERTEX_BUFFER`、`INDEX_BUFFER`、`CONSTANT_BUFFER`、`SHADER_RESOURCE` など。複数の OR も可能 |
| `CPUAccessFlags` | `DYNAMIC` のとき `WRITE` |
| `StructureByteStride` | 構造化バッファのとき 1 要素の大きさ |

`Usage` の選び方は[Map, Unmap and UpdateSubresource](map-update.md) です。

## パイプラインにつなぐ

```cpp
const UINT stride = sizeof(Vertex);                        // 1 頂点の大きさ（28 バイト）
const UINT offset = 0;                                     // バッファの、先頭から、何バイト目から、使うか
context->IASetVertexBuffers(0, 1, vertex_buffer.GetAddressOf(), &stride, &offset);
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
```

| 引数 | 内容 |
| --- | --- |
| `StartSlot` | 入力スロット（0〜15）。入力レイアウトの `InputSlot` と対応 |
| `NumBuffers` | つなぐバッファの数 |
| `ppVertexBuffers` | バッファの配列 |
| `pStrides` | 各バッファの 1 頂点の大きさ |
| `pOffsets` | 各バッファの使い始める位置（バイト） |

`IASetPrimitiveTopology` で頂点のつなぎ方を決めます。

| 値 | 内容 |
| --- | --- |
| `TRIANGLELIST` | 3 頂点ごとに三角形 1 つ（最も普通） |
| `TRIANGLESTRIP` | 前の 2 頂点を共有して三角形をつなぐ |
| `LINELIST` | 2 頂点ごとに線 1 本（デバッグ描画） |
| `POINTLIST` | 点（パーティクル） |

## 複数のバッファに分ける

位置・法線・uv を別々のバッファに分けて、持つこともできます（SoA）。

```cpp
ID3D11Buffer* buffers[] = {position_buffer.Get(), normal_buffer.Get(), uv_buffer.Get()};
UINT strides[] = {sizeof(XMFLOAT3), sizeof(XMFLOAT3), sizeof(XMFLOAT2)};
UINT offsets[] = {0, 0, 0};
context->IASetVertexBuffers(0, 3, buffers, strides, offsets);
```

シャドウ パスのように位置だけを使う描画では位置のバッファだけをつなぐと読み込むデータが減ります。入力レイアウトの `InputSlot`（0、1、2）が各バッファに対応します。

## 描く

```cpp
context->Draw(3, 0);                                       // 頂点 3 つ、先頭（0 番）から
```

インデックス バッファを使う描画は[Index Buffer](index-buffer.md) です。

## 動的な頂点バッファ

毎フレーム、頂点が変わる（パーティクル、UI の四角形）ときは `DYNAMIC` で作り `Map` で、書きます。

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

`WRITE_DISCARD` は GPU が前のフレームを読んでいても待たず新しい領域を渡します（[Map, Unmap and UpdateSubresource](map-update.md)）。

## よくあるミス

??? failure "三角形が見えない（クリアの色のまま）"
    頂点が反時計回り（CCW）で、裏面として捨てられている。頂点の順序を時計回りに直すか、ラスタライザー ステートの `FrontCounterClockwise` を合わせる（[Rasterizer State](rasterizer-state.md)）。

??? failure "頂点が化けて、ぐちゃぐちゃに見える"
    入力レイアウトのフォーマットやオフセットが `Vertex` 構造体と合っていない。ストライドが間違っている。

??? failure "`IMMUTABLE` なのに、`Map` しようとして失敗する"
    `IMMUTABLE` は作成後に変更できない。変えたいなら `DYNAMIC`（毎フレーム）か `DEFAULT` と `UpdateSubresource`。

??? failure "バッファの一部だけを描くつもりが全部描かれる"
    `Draw` の第 2 引数（`StartVertexLocation`）と `IASetVertexBuffers` のオフセットの使い分けを混同している。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 頂点バッファ ＝ 頂点データの配列。`CreateBuffer` + `D3D11_BIND_VERTEX_BUFFER`
    - [x] 変わらないなら `IMMUTABLE`、毎フレームなら `DYNAMIC` + `Map`
    - [x] ストライド ＝ 1 頂点の大きさ。`IASetVertexBuffers` に渡す
    - [x] 並びは入力レイアウトで教える
    - [x] 三角形は時計回りが表

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Index Buffer](index-buffer.md)
- [Input Layout](input-layout.md)
- [Drawing a Triangle](triangle.md)
- [Map, Unmap and UpdateSubresource](map-update.md)
- [Microsoft Learn: ID3D11Device::CreateBuffer](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createbuffer)
