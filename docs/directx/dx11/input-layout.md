---
title: Input Layout
tags:
  - DirectX
---

# Input Layout

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>入力レイアウト</strong>（Input Layout）は、<strong>頂点バッファの中のデータの並びを GPU に教える</strong>、設定です。頂点バッファはただのバイトの列なので、「最初の 12 バイトが位置、次の 16 バイトが色」と教えないと頂点シェーダーにどう渡せばよいか分かりません。

!!! tip "ポイント"
    - 入力レイアウト ＝ 「頂点のどのバイトが頂点シェーダーのどの入力か」の対応表。
    - 1 つの頂点の要素ごとに `D3D11_INPUT_ELEMENT_DESC` を書く（セマンティクス名、フォーマット、オフセット）。
    - 作るときに <strong>頂点シェーダーのバイトコード</strong>を渡す（入力のセマンティクスが合うかを検査するため）。
    - 頂点構造体（C++）とレイアウトと頂点シェーダーの入力の <strong>3 つがそろっている</strong>必要がある。
    - インスタンスごとのデータ（`PER_INSTANCE_DATA`）も同じ仕組みで渡せる（[Instanced Drawing](instancing-draw.md)）。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

## 要素の記述

頂点が次の構造体のとき

```cpp
struct Vertex {
  DirectX::XMFLOAT3 position;    // オフセット 0、12 バイト
  DirectX::XMFLOAT4 color;       // オフセット 12、16 バイト
};
```

要素を 1 つずつ書きます。

```cpp
const D3D11_INPUT_ELEMENT_DESC elements[] = {
    // セマンティクス名, 番号, フォーマット,                    スロット, オフセット, 種類,                           インスタンス ステップ
    {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT,    0, 0,  D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"COLOR",    0, DXGI_FORMAT_R32G32B32A32_FLOAT, 0, 12, D3D11_INPUT_PER_VERTEX_DATA, 0},
};
```

| メンバー | 内容 |
| --- | --- |
| `SemanticName` | 頂点シェーダーの入力のセマンティクス名（`POSITION`、`COLOR`、`NORMAL`、`TEXCOORD`） |
| `SemanticIndex` | 同じ名前が複数あるときの番号（`TEXCOORD0`、`TEXCOORD1`） |
| `Format` | この要素のデータの形式（`R32G32B32_FLOAT` ＝ `float3`） |
| `InputSlot` | どの頂点バッファ（スロット 0〜15）から、読むか |
| `AlignedByteOffset` | 頂点の先頭からこの要素までのバイト数。`D3D11_APPEND_ALIGNED_ELEMENT` で自動計算 |
| `InputSlotClass` | `PER_VERTEX_DATA`（頂点ごと）、`PER_INSTANCE_DATA`（インスタンスごと） |
| `InstanceDataStepRate` | インスタンスごとのデータを何インスタンスごとに進めるか（通常 1。頂点ごとなら 0） |

### フォーマットの対応

| HLSL の型 | `DXGI_FORMAT` |
| --- | --- |
| `float` | `R32_FLOAT` |
| `float2` | `R32G32_FLOAT` |
| `float3` | `R32G32B32_FLOAT` |
| `float4` | `R32G32B32A32_FLOAT` |
| `uint` | `R32_UINT` |
| `float4`（8 ビットの色 → 0〜1） | `R8G8B8A8_UNORM` |
| `float2`（16 ビットの半精度） | `R16G16_FLOAT` |

位置は `float3`、法線も `float3`、uv は `float2`、色はメモリを節約して `R8G8B8A8_UNORM`（4 バイト）にするのがよく使われます。GPU が読み込むときに自動で `float` に変換します。

## 自動オフセット

オフセットを自分で数えると間違えやすいので `D3D11_APPEND_ALIGNED_ELEMENT` を使えます。

```cpp
const D3D11_INPUT_ELEMENT_DESC elements[] = {
    {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT,    0, 0,                             D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"NORMAL",   0, DXGI_FORMAT_R32G32B32_FLOAT,    0, D3D11_APPEND_ALIGNED_ELEMENT,  D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"TEXCOORD", 0, DXGI_FORMAT_R32G32_FLOAT,       0, D3D11_APPEND_ALIGNED_ELEMENT,  D3D11_INPUT_PER_VERTEX_DATA, 0},
};
```

2 つ目以降が「直前の要素のすぐ後ろ」に自動で並びます。C++ 側の構造体のパディング（`float` 以外の型が、混ざるとき）に注意します。

## 作る

```cpp
Microsoft::WRL::ComPtr<ID3D11InputLayout> input_layout;
device->CreateInputLayout(elements, ARRAYSIZE(elements),
                          vs_bytecode->GetBufferPointer(),      // 頂点シェーダーの、バイトコード
                          vs_bytecode->GetBufferSize(),
                          &input_layout);
```

頂点シェーダーのバイトコードを渡すのは <strong>レイアウトの要素とシェーダーの入力が合うかを検査する</strong>ためです。セマンティクスの名前や型が合わないと作成が、失敗します。シェーダーが使わない要素はレイアウトにあってもかまいません（無視されます）。

## パイプラインにつなぐ

```cpp
context->IASetInputLayout(input_layout.Get());
```

頂点バッファ、インデックス バッファ、入力レイアウト、プリミティブ トポロジーを設定して、はじめて描けます（[Drawing a Triangle](triangle.md)）。

## 3 つがそろう

頂点が化けるときは次の 3 つを見比べます。

| C++（`Vertex`） | 入力レイアウト | HLSL（`VSInput`） |
| --- | --- | --- |
| `XMFLOAT3 position`（オフセット 0） | `POSITION`、`R32G32B32_FLOAT`、0 | `float3 position : POSITION` |
| `XMFLOAT4 color`（オフセット 12） | `COLOR`、`R32G32B32A32_FLOAT`、12 | `float4 color : COLOR` |

<strong>セマンティクス名がレイアウトと HLSL で一致</strong>し <strong>フォーマットとオフセットが C++ の構造体と、一致</strong>している必要があります。

## 頂点バッファなしの描画

頂点バッファを使わず `SV_VertexID` だけで頂点を作る方法もあります（フルスクリーン三角形）。このとき、入力レイアウトは不要で `nullptr` を設定します。

```cpp
context->IASetInputLayout(nullptr);
context->Draw(3, 0);
```

## よくあるミス

??? failure "`CreateInputLayout` が、失敗する"
    頂点シェーダーの入力とレイアウトのセマンティクスが、合わない（名前、番号、型）。レイアウトに無い要素をシェーダーが、要求している。

??? failure "頂点の位置や色が化ける"
    `AlignedByteOffset` が C++ の構造体とずれている。構造体のパディング（`XMFLOAT3` の後の `float` など）を考慮していない。

??? failure "デバッグ レイヤーが `INPUT_LAYOUT` の警告を出す"
    レイアウトが頂点バッファのストライドと合わない。`IASetVertexBuffers` のストライドがレイアウトの要素の合計と違う。

??? failure "`IASetInputLayout` を呼ばずに描いた"
    何も描かれない。または、警告が出る。レイアウトの設定を忘れない（頂点バッファなしの描画を除く）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入力レイアウト ＝ 頂点バッファのデータの並びの説明
    - [x] 要素ごとにセマンティクス名・フォーマット・オフセットを書く
    - [x] 作るとき頂点シェーダーのバイトコードを渡す
    - [x] C++ の構造体・レイアウト・HLSL の入力がそろう
    - [x] 頂点バッファなしなら `IASetInputLayout(nullptr)`

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Vertex Buffer](vertex-buffer.md)
- [Shaders and Compilation](shaders.md)
- [Instanced Drawing](instancing-draw.md)
- [Microsoft Learn: ID3D11Device::CreateInputLayout](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createinputlayout)
