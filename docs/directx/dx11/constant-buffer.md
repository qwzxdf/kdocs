---
title: Constant Buffer
tags:
  - DirectX
---

# Constant Buffer

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>定数バッファ</strong>は、シェーダーに、<strong>パラメータ</strong>（行列、色、時間、ライトの、位置など）を、渡す、バッファです。頂点バッファが、頂点ごとに、変わる、データなのに対して、定数バッファは、<strong>1 回の描画の間、全頂点・全ピクセルで、同じ値</strong>です。物を動かすために、ワールド行列を、渡す、最初の、必須の、仕組みです。

!!! tip "ポイント"
    - 定数バッファ ＝ シェーダーへの、パラメータの、受け渡し。HLSL では `cbuffer`、C++ では、同じ並びの、構造体。
    - <strong>16 バイト（`float4`）の境界</strong>を、またげない。C++ 側の、構造体と、並びを、そろえるのが、最大の、落とし穴。
    - 大きさは、<strong>16 の倍数</strong>。`static_assert(sizeof(T) % 16 == 0)` で、守る。
    - 毎フレーム、書き換えるなら、`DYNAMIC` + `Map(WRITE_DISCARD)`。まれにしか、変えないなら、`DEFAULT` + `UpdateSubresource`。
    - 行列は、`row_major` を、付けて、HLSL で、行ベクトル（`mul(v, M)`）の、規約に、そろえる。

## HLSL 側

```hlsl
// register(b0): スロット 0 の、定数バッファ。C++ の VSSetConstantBuffers(0, …) と、対応する。
cbuffer PerObject : register(b0) {
  row_major float4x4 world_view_projection;     // 行ベクトルの規約（v * M）。C++ の XMFLOAT4X4 と、同じ並び
  float4 tint;
};

struct VSInput {
  float3 position : POSITION;
  float4 color : COLOR;
};

struct VSOutput {
  float4 position : SV_Position;
  float4 color : COLOR;
};

VSOutput VSMain(VSInput input) {
  VSOutput output;
  output.position = mul(float4(input.position, 1.0), world_view_projection);   // 行ベクトル × 行列
  output.color = input.color * tint;
  return output;
}
```

`cbuffer` の中の、変数は、グローバル変数のように、使えます。`register(b0)` の `b` は、定数バッファ（buffer）で、番号は、スロットです。1 つのシェーダーに、最大 14 個の、定数バッファを、つなげます（スロット 0〜13）。

### row_major と、行ベクトル

DirectXMath は、行列を、<strong>行優先</strong>で、メモリに、並べ、<strong>行ベクトル</strong>（`v * M`）の、規約で、使います。HLSL の、`float4x4` は、既定で、<strong>列優先</strong>の、パッキングなので、そのまま、渡すと、転置された、行列に、なります。

| 方法 | HLSL | C++ |
| --- | --- | --- |
| ① `row_major` を、付ける（推奨） | `row_major float4x4 m;`、`mul(v, m)` | そのまま、`XMFLOAT4X4` を、書く |
| ② 転置して、渡す | `float4x4 m;`、`mul(m, v)`（列ベクトル） | `XMMatrixTranspose` してから、書く |

このサイトは、行ベクトルで、統一するので、①です。`#pragma pack_matrix(row_major)` を、シェーダーの、先頭に、書くと、全ファイルの、既定を、`row_major` に、できます。

## C++ 側の、構造体

```cpp
#include <DirectXMath.h>

struct PerObject {
  DirectX::XMFLOAT4X4 world_view_projection;     // 64 バイト
  DirectX::XMFLOAT4 tint;                        // 16 バイト → 合計 80 バイト（16 の倍数）
};
static_assert(sizeof(PerObject) % 16 == 0, "定数バッファは、16 バイトの倍数");
```

構造体の、並びと、HLSL の、`cbuffer` の、並びを、同じ順序に、そろえます。

## 16 バイト境界の、規則

`cbuffer` は、<strong>16 バイトずつの、行（`float4` 1 つぶん）</strong>に、並びます。1 つの変数が、行の、境界を、またぐ場合は、<strong>次の行の、先頭から</strong>、始まります。

| 並べた型 | HLSL の配置 | C++ の `float3 + float`（普通のパディング無し）との違い |
| --- | --- | --- |
| `float3 a; float b;` | a が、行の 0〜11、b が、12〜15（同じ行に、収まる） | 一致する |
| `float2 a; float3 b;` | a が 0〜7、b は、8〜19 になり、境界（16）を、またぐので、b は、次の行（16〜27）へ | C++ の構造体は、b が、オフセット 8 → <strong>ずれる</strong> |
| `float a; float4 b;` | a が 0〜3、b は、行を、またぐので、16〜 | C++ は、b がオフセット 4 → ずれる |
| `float3 a; float3 b;` | a が 0〜11、b は、12〜 に、置こうとして、またぐので、16〜 | C++ は、b がオフセット 12 → ずれる |

C++ 側で、同じ配置に、するには、<strong>明示的に、パディングを、入れる</strong>か、`alignas(16)` を、使います。

```cpp
struct Lighting {
  DirectX::XMFLOAT3 direction;       // 0〜11
  float intensity;                   // 12〜15  ← float3 の直後の float は、同じ行に収まる
  DirectX::XMFLOAT3 color;           // 16〜27
  float padding;                     // 28〜31  ← 明示的に詰めて、次の変数は、32 から
  DirectX::XMFLOAT2 uv_scale;        // 32〜39
  DirectX::XMFLOAT2 uv_offset;       // 40〜47
};
static_assert(sizeof(Lighting) == 48, "HLSL の cbuffer と同じ大きさ");
```

配列も、<strong>各要素が、16 バイトの、倍数</strong>に、切り上げられます。`float values[4]` は、HLSL では、4 つの `float4`（64 バイト）として、並びます。`float4 values[4]` で、渡して、`.x` で、使うほうが、意図が、明確です。

## 作る

```cpp
D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = sizeof(PerObject);                        // 16 の倍数
desc.Usage = D3D11_USAGE_DYNAMIC;                          // 毎フレーム、CPU から書く
desc.BindFlags = D3D11_BIND_CONSTANT_BUFFER;
desc.CPUAccessFlags = D3D11_CPU_ACCESS_WRITE;

Microsoft::WRL::ComPtr<ID3D11Buffer> constant_buffer;
device->CreateBuffer(&desc, nullptr, &constant_buffer);
```

`ByteWidth` が、16 の倍数でないと、`CreateBuffer` が、失敗します。大きさの、上限は、4096 個の `float4`（64 KB）です。

## 書き込む

```cpp
void UpdateConstants(const PerObject& data) {
  D3D11_MAPPED_SUBRESOURCE mapped = {};
  context->Map(constant_buffer.Get(), 0, D3D11_MAP_WRITE_DISCARD, 0, &mapped);   // 丸ごと書き換える
  std::memcpy(mapped.pData, &data, sizeof(data));
  context->Unmap(constant_buffer.Get(), 0);
}
```

`D3D11_MAP_WRITE_DISCARD` は、<strong>古い内容を、捨てて、全部、書き直す</strong>指定で、GPU が、まだ、前の内容を、使っていても、待たずに、新しい領域を、渡します（[Map, Unmap and UpdateSubresource](map-update.md)）。

## パイプラインにつなぐ

```cpp
ID3D11Buffer* buffers[] = {constant_buffer.Get()};
context->VSSetConstantBuffers(0, 1, buffers);              // スロット 0 から、1 個。頂点シェーダー用
context->PSSetConstantBuffers(0, 1, buffers);              // ピクセル シェーダーからも、読むなら
```

| 引数 | 内容 |
| --- | --- |
| `StartSlot` | 最初のスロット（0〜13）。HLSL の `register(b#)` と、対応 |
| `NumBuffers` | つなぐ、バッファの数 |
| `ppConstantBuffers` | バッファの、配列 |

シェーダーの、種類ごとに、設定します（`VS`、`PS`、`CS`、`GS`、`HS`、`DS`）。同じバッファを、複数の、段に、つなげます。

## 更新頻度で、バッファを、分ける

1 つの、巨大な、定数バッファに、全部を、入れると、1 つ変わるたびに、全部を、書き直します。<strong>更新の頻度で、分ける</strong>のが、定石です。

| バッファ | 更新の頻度 | 中身 |
| --- | --- | --- |
| `PerFrame`（b0） | 毎フレーム 1 回 | カメラの、ビュー・射影、時間、ライト |
| `PerPass`（b1） | パスごと | 画面サイズ、パスの、パラメータ |
| `PerMaterial`（b2） | マテリアルごと | 色、粗さ、金属度 |
| `PerObject`（b3） | 物ごと | ワールド行列 |

`PerFrame` は、1 度書いて、そのフレーム中、つないだままで、使えます。`PerObject` だけを、物ごとに、書き換えます。

```cpp
// 頻繁に更新するなら、バッファを、複数用意して、使い回す（描画ごとに、Map）。
// 大量の物を描くときは、1 つの、大きなバッファに、物ごとの、データを、並べ、オフセットで、つなぐ（VSSetConstantBuffers1）。
```

### 定数バッファの、オフセット指定（D3D11.1）

```cpp
// 1 つの大きな定数バッファの、一部分だけを、つなぐ。FirstConstant と NumConstants は、float4 単位（16 の倍数）。
Microsoft::WRL::ComPtr<ID3D11DeviceContext1> context1;
context.As(&context1);
UINT first = object_index * (256 / 16);                    // 物ごとに 256 バイトの領域（16 バイト単位の、数）
UINT count = 256 / 16;
context1->VSSetConstantBuffers1(1, 1, big_buffer.GetAddressOf(), &first, &count);
```

大量の、小さな、描画で、バッファの切り替えと、`Map` の、回数を、減らせます。

## HLSL の `cbuffer` と `ConstantBuffer<T>`

SM 5.1 以降は、`ConstantBuffer<T>` で、構造体として、書けます（D3D12 向け）。D3D11（SM 5.0）では、`cbuffer` を、使います。

## よくあるミス

??? failure "C++ で書いた値と、シェーダーで読んだ値が、ずれる（行列が、おかしい）"
    16 バイト境界の、規則で、`float3` の後の `float3`、`float2` の後の `float3` などで、オフセットが、ずれている。明示的に、パディングを、入れる。行列の、`row_major` と、転置の、取り違えも、典型。

??? failure "`CreateBuffer` が、`E_INVALIDARG` で、失敗する"
    定数バッファの、`ByteWidth` が、16 の倍数でない。`static_assert(sizeof(T) % 16 == 0)` で、防ぐ。

??? failure "オブジェクトが、画面に、映らない・歪む（行列）"
    ワールド・ビュー・射影の、掛ける順序が、規約と、合っていない。行ベクトルは、`world * view * projection`（左から右）。`row_major` を、付け忘れて、転置された。

??? failure "全部の物が、同じ位置に、描かれる"
    `Map`/`Unmap` で、物ごとの、行列を、書いたが、描画（`Draw`）の前に、書いていない。または、1 フレームの、全描画が、終わってから、GPU が、実行されるため、最後に書いた値が、全描画に、使われる、と、思い込んでいる（`Map`（`DISCARD`）の、たびに、別の領域が、割り当てられるので、通常は、起きない）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 定数バッファ ＝ シェーダーへの、パラメータ。1 回の描画の間、同じ値
    - [x] 16 バイト境界を、またげない。大きさは、16 の倍数
    - [x] C++ の構造体と、`cbuffer` の並びを、そろえる（パディング、`alignas(16)`）
    - [x] 行列は `row_major`、行ベクトル（`mul(v, M)`）
    - [x] 毎フレームなら `DYNAMIC` + `Map(WRITE_DISCARD)`
    - [x] 更新頻度で、バッファを、分ける

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Map, Unmap and UpdateSubresource](map-update.md)
- [Shaders and Compilation](shaders.md)
- [DirectXMath](../../gamemath/directxmath.md)
- [Microsoft Learn: パッキング規則](https://learn.microsoft.com/ja-jp/windows/win32/direct3dhlsl/dx-graphics-hlsl-packing-rules)
