---
title: Constant Buffer
tags:
  - DirectX
---

# Constant Buffer

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>定数バッファ</strong>はシェーダーに パラメータ（行列、色、時間、ライトの位置など）を渡すバッファです。頂点バッファが頂点ごとに変わるデータなのに対して定数バッファは、1 回の描画の間、全頂点・全ピクセルで同じ値です。物を動かすためにワールド行列を渡す最初の必須の仕組みです。

!!! tip "ポイント"
    - 定数バッファ ＝ シェーダーへのパラメータの受け渡し。HLSL では `cbuffer`、C++ では同じ並びの構造体。
    - <strong>16 バイト（`float4`）の境界</strong>をまたげない。C++ 側の構造体と並びをそろえるのが最大の落とし穴。
    - 大きさは <strong>16 の倍数</strong>。`static_assert(sizeof(T) % 16 == 0)` で守る。
    - 毎フレーム、書き換えるなら `DYNAMIC` + `Map(WRITE_DISCARD)`。まれにしか変えないなら `DEFAULT` + `UpdateSubresource`。
    - 行列は `row_major` を付けて、HLSL で行ベクトル（`mul(v, M)`）の規約にそろえる。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

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

`cbuffer` の中の変数はグローバル変数のように使えます。`register(b0)` の `b` は定数バッファ（buffer）で番号は、スロットです。1 つのシェーダーに最大 14 個の定数バッファをつなげます（スロット 0〜13）。

### row_major と行ベクトル

DirectXMath は行列を <strong>行優先</strong>でメモリに並べ 行ベクトル（`v * M`）の規約で、使います。HLSL の `float4x4` は既定で 列優先のパッキングなのでそのまま渡すと転置された行列になります。

| 方法 | HLSL | C++ |
| --- | --- | --- |
| ① `row_major` を付ける（推奨） | `row_major float4x4 m;`、`mul(v, m)` | そのまま `XMFLOAT4X4` を書く |
| ② 転置して渡す | `float4x4 m;`、`mul(m, v)`（列ベクトル） | `XMMatrixTranspose` してから、書く |

このサイトは行ベクトルで統一するので、①です。`#pragma pack_matrix(row_major)` をシェーダーの先頭に書くと全ファイルの既定を `row_major` にできます。

## C++ 側の構造体

```cpp
#include <DirectXMath.h>

struct PerObject {
  DirectX::XMFLOAT4X4 world_view_projection;     // 64 バイト
  DirectX::XMFLOAT4 tint;                        // 16 バイト → 合計 80 バイト（16 の倍数）
};
static_assert(sizeof(PerObject) % 16 == 0, "定数バッファは、16 バイトの倍数");
```

構造体の並びと HLSL の `cbuffer` の並びを同じ順序にそろえます。

## 16 バイト境界の規則

`cbuffer` は <strong>16 バイトずつの行（`float4` 1 つぶん）</strong>に並びます。1 つの変数が行の境界をまたぐ場合は、次の行の先頭から、始まります。

| 並べた型 | HLSL の配置 | C++ の `float3 + float`（普通のパディング無し）との違い |
| --- | --- | --- |
| `float3 a; float b;` | a が行の 0〜11、b が 12〜15（同じ行に収まる） | 一致する |
| `float2 a; float3 b;` | a が 0〜7、b は 8〜19 になり境界（16）をまたぐので b は次の行（16〜27）へ | C++ の構造体は b が、オフセット 8 → ずれる |
| `float a; float4 b;` | a が 0〜3、b は行をまたぐので 16〜 | C++ は、b がオフセット 4 → ずれる |
| `float3 a; float3 b;` | a が 0〜11、b は 12〜 に置こうとして、またぐので 16〜 | C++ は b がオフセット 12 → ずれる |

C++ 側で同じ配置にするには 明示的にパディングを入れるか `alignas(16)` を使います。

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

配列も 各要素が 16 バイトの倍数に切り上げられます。`float values[4]` は HLSL では 4 つの `float4`（64 バイト）として、並びます。`float4 values[4]` で渡して `.x` で使うほうが意図が、明確です。

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

`ByteWidth` が 16 の倍数でないと `CreateBuffer` が、失敗します。大きさの上限は 4096 個の `float4`（64 KB）です。

## 書き込む

```cpp
void UpdateConstants(const PerObject& data) {
  D3D11_MAPPED_SUBRESOURCE mapped = {};
  context->Map(constant_buffer.Get(), 0, D3D11_MAP_WRITE_DISCARD, 0, &mapped);   // 丸ごと書き換える
  std::memcpy(mapped.pData, &data, sizeof(data));
  context->Unmap(constant_buffer.Get(), 0);
}
```

`D3D11_MAP_WRITE_DISCARD` は <strong>古い内容を捨てて全部、書き直す</strong>指定で GPU がまだ前の内容を使っていても待たずに新しい領域を渡します（[Map, Unmap and UpdateSubresource](map-update.md)）。

## パイプラインにつなぐ

```cpp
ID3D11Buffer* buffers[] = {constant_buffer.Get()};
context->VSSetConstantBuffers(0, 1, buffers);              // スロット 0 から、1 個。頂点シェーダー用
context->PSSetConstantBuffers(0, 1, buffers);              // ピクセル シェーダーからも、読むなら
```

| 引数 | 内容 |
| --- | --- |
| `StartSlot` | 最初のスロット（0〜13）。HLSL の `register(b#)` と対応 |
| `NumBuffers` | つなぐバッファの数 |
| `ppConstantBuffers` | バッファの配列 |

シェーダーの種類ごとに設定します（`VS`、`PS`、`CS`、`GS`、`HS`、`DS`）。同じバッファを複数の段につなげます。

## 更新頻度でバッファを分ける

1 つの巨大な定数バッファに全部を入れると 1 つ変わるたびに全部を書き直します。<strong>更新の頻度で分ける</strong>のが定石です。

| バッファ | 更新の頻度 | 中身 |
| --- | --- | --- |
| `PerFrame`（b0） | 毎フレーム 1 回 | カメラのビュー・射影、時間、ライト |
| `PerPass`（b1） | パスごと | 画面サイズ、パスのパラメータ |
| `PerMaterial`（b2） | マテリアルごと | 色、粗さ金属度 |
| `PerObject`（b3） | 物ごと | ワールド行列 |

`PerFrame` は 1 度書いてそのフレーム中、つないだままで使えます。`PerObject` だけを物ごとに書き換えます。

```cpp
// 頻繁に更新するなら、バッファを、複数用意して、使い回す（描画ごとに、Map）。
// 大量の物を描くときは、1 つの、大きなバッファに、物ごとの、データを、並べ、オフセットで、つなぐ（VSSetConstantBuffers1）。
```

### 定数バッファのオフセット指定（D3D11.1）

```cpp
// 1 つの大きな定数バッファの、一部分だけを、つなぐ。FirstConstant と NumConstants は、float4 単位（16 の倍数）。
Microsoft::WRL::ComPtr<ID3D11DeviceContext1> context1;
context.As(&context1);
UINT first = object_index * (256 / 16);                    // 物ごとに 256 バイトの領域（16 バイト単位の、数）
UINT count = 256 / 16;
context1->VSSetConstantBuffers1(1, 1, big_buffer.GetAddressOf(), &first, &count);
```

大量の小さな描画でバッファの切り替えと `Map` の回数を減らせます。

## HLSL の `cbuffer` と `ConstantBuffer<T>`

SM 5.1 以降は `ConstantBuffer<T>` で構造体として、書けます（D3D12 向け）。D3D11（SM 5.0）では `cbuffer` を使います。

## よくあるミス

??? failure "C++ で書いた値とシェーダーで読んだ値がずれる（行列が、おかしい）"
    16 バイト境界の規則で、`float3` の後の `float3`、`float2` の後の `float3` などでオフセットが、ずれている。明示的にパディングを入れる。行列の `row_major` と転置の取り違えも典型。

??? failure "`CreateBuffer` が `E_INVALIDARG` で、失敗する"
    定数バッファの `ByteWidth` が、16 の倍数でない。`static_assert(sizeof(T) % 16 == 0)` で防ぐ。

??? failure "オブジェクトが画面に映らない・歪む（行列）"
    ワールド・ビュー・射影の掛ける順序が規約と合っていない。行ベクトルは `world * view * projection`（左から右）。`row_major` を付け忘れて転置された。

??? failure "全部の物が、同じ位置に描かれる"
    `Map`/`Unmap` で物ごとの行列を書いたが描画（`Draw`）の前に書いていない。または、1 フレームの全描画が終わってから、GPU が実行されるため最後に書いた値が、全描画に使われると思い込んでいる（`Map`（`DISCARD`）のたびに別の領域が割り当てられるので通常は、起きない）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 定数バッファ ＝ シェーダーへのパラメータ。1 回の描画の間、同じ値
    - [x] 16 バイト境界をまたげない。大きさは 16 の倍数
    - [x] C++ の構造体と `cbuffer` の並びをそろえる（パディング、`alignas(16)`）
    - [x] 行列は `row_major`、行ベクトル（`mul(v, M)`）
    - [x] 毎フレームなら `DYNAMIC` + `Map(WRITE_DISCARD)`
    - [x] 更新頻度で、バッファを分ける

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Map, Unmap and UpdateSubresource](map-update.md)
- [Shaders and Compilation](shaders.md)
- [DirectXMath](../../gamemath/directxmath.md)
- [Microsoft Learn: パッキング規則](https://learn.microsoft.com/ja-jp/windows/win32/direct3dhlsl/dx-graphics-hlsl-packing-rules)
