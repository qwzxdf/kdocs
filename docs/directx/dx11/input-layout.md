---
title: Input Layout
tags:
  - DirectX
---

# Input Layout

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>入力レイアウト</strong>（Input Layout）は、<strong>頂点バッファの中の、データの並びを、GPU に、教える</strong>、設定です。頂点バッファは、ただの、バイトの列なので、「最初の 12 バイトが位置、次の 16 バイトが色」と、教えないと、頂点シェーダーに、どう、渡せばよいか、分かりません。

!!! tip "ポイント"
    - 入力レイアウト ＝ 「頂点の、どのバイトが、頂点シェーダーの、どの入力か」の、対応表。
    - 1 つの頂点の、要素ごとに、`D3D11_INPUT_ELEMENT_DESC` を、書く（セマンティクス名、フォーマット、オフセット）。
    - 作るときに、<strong>頂点シェーダーの、バイトコード</strong>を、渡す（入力の、セマンティクスが、合うかを、検査するため）。
    - 頂点構造体（C++）と、レイアウトと、頂点シェーダーの、入力の、<strong>3 つが、そろっている</strong>必要がある。
    - インスタンスごとのデータ（`PER_INSTANCE_DATA`）も、同じ仕組みで、渡せる（[Instanced Drawing](instancing-draw.md)）。

## 要素の記述

頂点が、次の構造体のとき、

```cpp
struct Vertex {
  DirectX::XMFLOAT3 position;    // オフセット 0、12 バイト
  DirectX::XMFLOAT4 color;       // オフセット 12、16 バイト
};
```

要素を、1 つずつ、書きます。

```cpp
const D3D11_INPUT_ELEMENT_DESC elements[] = {
    // セマンティクス名, 番号, フォーマット,                    スロット, オフセット, 種類,                           インスタンス ステップ
    {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT,    0, 0,  D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"COLOR",    0, DXGI_FORMAT_R32G32B32A32_FLOAT, 0, 12, D3D11_INPUT_PER_VERTEX_DATA, 0},
};
```

| メンバー | 内容 |
| --- | --- |
| `SemanticName` | 頂点シェーダーの、入力の、セマンティクス名（`POSITION`、`COLOR`、`NORMAL`、`TEXCOORD`） |
| `SemanticIndex` | 同じ名前が、複数あるときの、番号（`TEXCOORD0`、`TEXCOORD1`） |
| `Format` | この要素の、データの形式（`R32G32B32_FLOAT` ＝ `float3`） |
| `InputSlot` | どの頂点バッファ（スロット 0〜15）から、読むか |
| `AlignedByteOffset` | 頂点の先頭から、この要素までの、バイト数。`D3D11_APPEND_ALIGNED_ELEMENT` で、自動計算 |
| `InputSlotClass` | `PER_VERTEX_DATA`（頂点ごと）、`PER_INSTANCE_DATA`（インスタンスごと） |
| `InstanceDataStepRate` | インスタンスごとの、データを、何インスタンスごとに、進めるか（通常 1。頂点ごとなら 0） |

### フォーマットの、対応

| HLSL の型 | `DXGI_FORMAT` |
| --- | --- |
| `float` | `R32_FLOAT` |
| `float2` | `R32G32_FLOAT` |
| `float3` | `R32G32B32_FLOAT` |
| `float4` | `R32G32B32A32_FLOAT` |
| `uint` | `R32_UINT` |
| `float4`（8 ビットの色 → 0〜1） | `R8G8B8A8_UNORM` |
| `float2`（16 ビットの、半精度） | `R16G16_FLOAT` |

位置は `float3`、法線も `float3`、uv は `float2`、色は、メモリを、節約して、`R8G8B8A8_UNORM`（4 バイト）に、するのが、よく使われます。GPU が、読み込むときに、自動で、`float` に、変換します。

## 自動オフセット

オフセットを、自分で、数えると、間違えやすいので、`D3D11_APPEND_ALIGNED_ELEMENT` を、使えます。

```cpp
const D3D11_INPUT_ELEMENT_DESC elements[] = {
    {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT,    0, 0,                             D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"NORMAL",   0, DXGI_FORMAT_R32G32B32_FLOAT,    0, D3D11_APPEND_ALIGNED_ELEMENT,  D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"TEXCOORD", 0, DXGI_FORMAT_R32G32_FLOAT,       0, D3D11_APPEND_ALIGNED_ELEMENT,  D3D11_INPUT_PER_VERTEX_DATA, 0},
};
```

2 つ目以降が、「直前の要素の、すぐ後ろ」に、自動で、並びます。C++ 側の、構造体の、パディング（`float` 以外の、型が、混ざるとき）に、注意します。

## 作る

```cpp
Microsoft::WRL::ComPtr<ID3D11InputLayout> input_layout;
device->CreateInputLayout(elements, ARRAYSIZE(elements),
                          vs_bytecode->GetBufferPointer(),      // 頂点シェーダーの、バイトコード
                          vs_bytecode->GetBufferSize(),
                          &input_layout);
```

頂点シェーダーの、バイトコードを、渡すのは、<strong>レイアウトの、要素と、シェーダーの、入力が、合うかを、検査する</strong>ためです。セマンティクスの、名前や、型が、合わないと、作成が、失敗します。シェーダーが、使わない、要素は、レイアウトに、あっても、かまいません（無視されます）。

## パイプラインにつなぐ

```cpp
context->IASetInputLayout(input_layout.Get());
```

頂点バッファ、インデックス バッファ、入力レイアウト、プリミティブ トポロジーを、設定して、はじめて、描けます（[Drawing a Triangle](triangle.md)）。

## 3 つが、そろう

頂点が、化けるときは、次の 3 つを、見比べます。

| C++（`Vertex`） | 入力レイアウト | HLSL（`VSInput`） |
| --- | --- | --- |
| `XMFLOAT3 position`（オフセット 0） | `POSITION`、`R32G32B32_FLOAT`、0 | `float3 position : POSITION` |
| `XMFLOAT4 color`（オフセット 12） | `COLOR`、`R32G32B32A32_FLOAT`、12 | `float4 color : COLOR` |

<strong>セマンティクス名が、レイアウトと、HLSL で、一致</strong>し、<strong>フォーマットと、オフセットが、C++ の、構造体と、一致</strong>している必要が、あります。

## 頂点バッファなしの描画

頂点バッファを、使わず、`SV_VertexID` だけで、頂点を、作る方法も、あります（フルスクリーン三角形）。このとき、入力レイアウトは、不要で、`nullptr` を、設定します。

```cpp
context->IASetInputLayout(nullptr);
context->Draw(3, 0);
```

## よくあるミス

??? failure "`CreateInputLayout` が、失敗する"
    頂点シェーダーの、入力と、レイアウトの、セマンティクスが、合わない（名前、番号、型）。レイアウトに、無い、要素を、シェーダーが、要求している。

??? failure "頂点の、位置や色が、化ける"
    `AlignedByteOffset` が、C++ の構造体と、ずれている。構造体の、パディング（`XMFLOAT3` の後の、`float` など）を、考慮していない。

??? failure "デバッグ レイヤーが、`INPUT_LAYOUT` の、警告を、出す"
    レイアウトが、頂点バッファの、ストライドと、合わない。`IASetVertexBuffers` の、ストライドが、レイアウトの、要素の、合計と、違う。

??? failure "`IASetInputLayout` を、呼ばずに、描いた"
    何も、描かれない。または、警告が、出る。レイアウトの、設定を、忘れない（頂点バッファなしの描画を、除く）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入力レイアウト ＝ 頂点バッファの、データの並びの、説明
    - [x] 要素ごとに、セマンティクス名・フォーマット・オフセットを、書く
    - [x] 作るとき、頂点シェーダーの、バイトコードを、渡す
    - [x] C++ の構造体・レイアウト・HLSL の入力が、そろう
    - [x] 頂点バッファなしなら、`IASetInputLayout(nullptr)`

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Vertex Buffer](vertex-buffer.md)
- [Shaders and Compilation](shaders.md)
- [Instanced Drawing](instancing-draw.md)
- [Microsoft Learn: ID3D11Device::CreateInputLayout](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createinputlayout)
