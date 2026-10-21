---
title: Root Signature Structs
tags:
  - DirectX
api:
  - D3D12_ROOT_SIGNATURE_DESC
---

# Root Signature Structs

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

シェーダーは `register(t0)` や `register(b0)` と書くだけで、どのテクスチャや定数バッファを使うのかを知りません。実際にそのレジスタへ何を結びつけるかは、描画の前にアプリが決めます。その対応表がルート シグネチャで、表の形を構造体で書き、バイナリに変換（シリアライズ）してから `CreateRootSignature` に渡します。このページでは、その表を書く構造体を説明します。

!!! tip "ポイント"
    - ルート シグネチャは `D3D12_ROOT_SIGNATURE_DESC` に、`D3D12_ROOT_PARAMETER` の配列と静的サンプラーを入れて作る。
    - `D3D12_ROOT_PARAMETER` は `ParameterType` で、共用体のどれを使うかが決まる。
    - ディスクリプタ テーブルは `D3D12_DESCRIPTOR_RANGE` の配列で書く。
    - ルート パラメーターは少ないほど速い。32 ビット定数は 1 つにつき 1 DWORD。
    - 入力レイアウトを使う描画では `ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT` を付ける。

!!! info "このページを読む前に"
    ルート シグネチャの考え方は [Root Signature](../root-signature.md)、テーブルが指すものは [Descriptor Heap](../descriptor-heap.md) で説明しています。サンプラーの構造体は [View and Descriptor Structs](view-structs.md#d3d12_static_sampler_desc) にあります。

## 構造体一覧

| 構造体 | 役割 | 使う場所 |
| --- | --- | --- |
| [`D3D12_ROOT_SIGNATURE_DESC`](#d3d12_root_signature_desc) | ルート シグネチャ全体 | `D3D12SerializeRootSignature` |
| [`D3D12_ROOT_PARAMETER`](#d3d12_root_parameter) | 1 つのルート パラメーター | `D3D12_ROOT_SIGNATURE_DESC` の配列 |
| [`D3D12_DESCRIPTOR_RANGE`](#d3d12_descriptor_range) | テーブルの 1 区間 | `D3D12_ROOT_DESCRIPTOR_TABLE` の配列 |
| [`D3D12_ROOT_DESCRIPTOR_TABLE`](#d3d12_root_descriptor_table) | ディスクリプタ テーブル | `D3D12_ROOT_PARAMETER` の `DescriptorTable` |
| [`D3D12_ROOT_CONSTANTS`](#d3d12_root_constants) | 32 ビット定数 | `D3D12_ROOT_PARAMETER` の `Constants` |
| [`D3D12_ROOT_DESCRIPTOR`](#d3d12_root_descriptor) | 直接書くディスクリプタ | `D3D12_ROOT_PARAMETER` の `Descriptor` |

## D3D12_ROOT_SIGNATURE_DESC {#d3d12_root_signature_desc}

```cpp
typedef struct D3D12_ROOT_SIGNATURE_DESC {
    UINT NumParameters;
    const D3D12_ROOT_PARAMETER* pParameters;
    UINT NumStaticSamplers;
    const D3D12_STATIC_SAMPLER_DESC* pStaticSamplers;
    D3D12_ROOT_SIGNATURE_FLAGS Flags;
} D3D12_ROOT_SIGNATURE_DESC;
```

ルート シグネチャの中身を、まとめて書きます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `NumParameters` | `UINT` | ルート パラメーターの数 |
| `pParameters` | `const D3D12_ROOT_PARAMETER*` | パラメーターの配列 |
| `NumStaticSamplers` | `UINT` | 静的サンプラーの数 |
| `pStaticSamplers` | `const D3D12_STATIC_SAMPLER_DESC*` | サンプラーの配列 |
| `Flags` | `D3D12_ROOT_SIGNATURE_FLAGS` | 追加の指定 |

`pParameters` は、`NumParameters` 個の配列です。配列の何番目か（ルート パラメーターのインデックス）は、のちに `SetGraphicsRootDescriptorTable(index, ...)` などで使う番号になるため、並べる順番を決めて、コードにも書いておきます。パラメーターが 0 個なら `nullptr` と 0 にします。

`Flags` の `ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT` は、頂点バッファから頂点を読む通常の描画に必要です。付け忘れると、入力レイアウトを使う PSO で、描画時にエラーになります。反対に、頂点バッファを使わない（頂点を `SV_VertexID` で生成する）パスや、コンピュート シェーダーだけのときは付けなくて済みます。`DENY_VERTEX_SHADER_ROOT_ACCESS` などの `DENY_*` は、使わないステージにルートを見せないことで、一部のハードウェアでの最適化に役立てるものです。

シリアライズは `D3D12SerializeRootSignature` で行い、その結果の blob を `CreateRootSignature` に渡します。バージョン 1.0 の構造体は上のとおりで、`D3D_ROOT_SIGNATURE_VERSION_1` を指定します。

```cpp
D3D12_ROOT_SIGNATURE_DESC desc = {};
desc.NumParameters = static_cast<UINT>(parameters.size());
desc.pParameters = parameters.data();
desc.NumStaticSamplers = 1;
desc.pStaticSamplers = &static_sampler;
desc.Flags = D3D12_ROOT_SIGNATURE_FLAG_ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT;

ComPtr<ID3DBlob> blob, error;
HRESULT hr = D3D12SerializeRootSignature(&desc, D3D_ROOT_SIGNATURE_VERSION_1,
                                         &blob, &error);
if (FAILED(hr) && error) {
  OutputDebugStringA(static_cast<const char*>(error->GetBufferPointer()));
}
```

`error` に、失敗の理由が文字列で入ります。シリアライズに失敗したら、必ず中身を出力してください。

## D3D12_ROOT_PARAMETER {#d3d12_root_parameter}

```cpp
typedef struct D3D12_ROOT_PARAMETER {
    D3D12_ROOT_PARAMETER_TYPE ParameterType;
    union {
        D3D12_ROOT_DESCRIPTOR_TABLE DescriptorTable;
        D3D12_ROOT_CONSTANTS Constants;
        D3D12_ROOT_DESCRIPTOR Descriptor;
    };
    D3D12_SHADER_VISIBILITY ShaderVisibility;
} D3D12_ROOT_PARAMETER;
```

ルート シグネチャの「1 つの口」です。口の種類は 3 つで、`ParameterType` で選びます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `ParameterType` | `D3D12_ROOT_PARAMETER_TYPE` | `DESCRIPTOR_TABLE`、`32BIT_CONSTANTS`、`CBV`、`SRV`、`UAV` |
| `DescriptorTable` | `D3D12_ROOT_DESCRIPTOR_TABLE` | 種類が `DESCRIPTOR_TABLE` のとき |
| `Constants` | `D3D12_ROOT_CONSTANTS` | 種類が `32BIT_CONSTANTS` のとき |
| `Descriptor` | `D3D12_ROOT_DESCRIPTOR` | 種類が `CBV`、`SRV`、`UAV` のとき |
| `ShaderVisibility` | `D3D12_SHADER_VISIBILITY` | この口が見えるステージ |

`DESCRIPTOR_TABLE` は、ディスクリプタ ヒープの連続した区間を指す 1 DWORD のポインタです。テクスチャを何枚も使うときの標準の方法です。`32BIT_CONSTANTS` は、数 DWORD の値をコマンド リストに直接書き込む方法で、毎フレーム変わる小さな値（行列 1 つなど）に向きます。`CBV` / `SRV` / `UAV` は、ヒープを介さず、バッファの GPU アドレスを直接渡します。アドレスなので 2 DWORD を使います。

ルート シグネチャの大きさは 64 DWORD までです。テーブルが 1、定数が値の数、直接のディスクリプタが 2 を消費します。多く使うと、ドライバーがルート引数をメモリへ退避するようになり、遅くなります。

`ShaderVisibility` は、`ALL` ならすべてのステージから見え、`PIXEL` などに絞ると、そのステージだけになります。絞ったほうが無駄が減りますが、頂点シェーダーとピクセル シェーダーの両方で使うリソースを `PIXEL` にすると、頂点側で読めません。迷ったら `ALL` です。

`ParameterType` が違うのに別の共用体のメンバーを埋めてしまうミスがあります。たとえば `CBV` なのに `DescriptorTable` に書くと、ルートの値が 0 のままで、デバッグ レイヤーのエラーになります。

```cpp
std::array<D3D12_ROOT_PARAMETER, 2> parameters = {};

// 0 番: 定数バッファ b0 を、アドレスで直接渡す。
parameters[0].ParameterType = D3D12_ROOT_PARAMETER_TYPE_CBV;
parameters[0].Descriptor.ShaderRegister = 0;
parameters[0].Descriptor.RegisterSpace = 0;
parameters[0].ShaderVisibility = D3D12_SHADER_VISIBILITY_ALL;

// 1 番: テクスチャ t0 のテーブル（次の節で範囲を作る）。
parameters[1].ParameterType = D3D12_ROOT_PARAMETER_TYPE_DESCRIPTOR_TABLE;
parameters[1].DescriptorTable.NumDescriptorRanges = 1;
parameters[1].DescriptorTable.pDescriptorRanges = &srv_range;
parameters[1].ShaderVisibility = D3D12_SHADER_VISIBILITY_PIXEL;
```

!!! failure "よくあるミス"
    - ルート パラメーターのインデックスを間違えて、別のリソースが結びつく。
    - 範囲の配列（`D3D12_DESCRIPTOR_RANGE`）を、ローカル変数のまま関数を抜けて、ポインタが無効になる。シリアライズが終わるまで、配列を生かしておく。
    - シェーダーの `register(t0)` と、`BaseShaderRegister` が合わない。

## D3D12_DESCRIPTOR_RANGE {#d3d12_descriptor_range}

```cpp
typedef struct D3D12_DESCRIPTOR_RANGE {
    D3D12_DESCRIPTOR_RANGE_TYPE RangeType;
    UINT NumDescriptors;
    UINT BaseShaderRegister;
    UINT RegisterSpace;
    UINT OffsetInDescriptorsFromTableStart;
} D3D12_DESCRIPTOR_RANGE;
```

ディスクリプタ テーブルの 1 区間を表します。「この種類のディスクリプタが、この数だけ並んでいて、シェーダーのこのレジスタから始まる」と書きます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `RangeType` | `D3D12_DESCRIPTOR_RANGE_TYPE` | `SRV`、`UAV`、`CBV`、`SAMPLER` |
| `NumDescriptors` | `UINT` | ディスクリプタの数。`-1` は無制限 |
| `BaseShaderRegister` | `UINT` | 最初のレジスタ番号（`t0` なら 0） |
| `RegisterSpace` | `UINT` | レジスタ スペース。通常は 0 |
| `OffsetInDescriptorsFromTableStart` | `UINT` | テーブルの先頭からの位置。`D3D12_DESCRIPTOR_RANGE_OFFSET_APPEND` で直前の続き |

`RangeType` は、HLSL の `t`（SRV）、`u`（UAV）、`b`（CBV）、`s`（サンプラー）に対応します。`t0` から 4 枚のテクスチャを使うなら、`RangeType = SRV`、`NumDescriptors = 4`、`BaseShaderRegister = 0` です。`NumDescriptors` に `UINT_MAX` を入れると、無制限（ブラインドレス）として扱われます。

`RegisterSpace` を変えると、同じ `t0` でも別の領域として扱えます。ライブラリごとに空間を分けたいときに使い、普通は 0 です。

`OffsetInDescriptorsFromTableStart` に `D3D12_DESCRIPTOR_RANGE_OFFSET_APPEND` を入れると、前の区間の直後に続きます。これを使えば、位置を自分で数えなくて済みます。

```cpp
D3D12_DESCRIPTOR_RANGE srv_range = {};
srv_range.RangeType = D3D12_DESCRIPTOR_RANGE_TYPE_SRV;
srv_range.NumDescriptors = 1;
srv_range.BaseShaderRegister = 0;   // t0
srv_range.RegisterSpace = 0;
srv_range.OffsetInDescriptorsFromTableStart = D3D12_DESCRIPTOR_RANGE_OFFSET_APPEND;
```

## D3D12_ROOT_DESCRIPTOR_TABLE {#d3d12_root_descriptor_table}

```cpp
typedef struct D3D12_ROOT_DESCRIPTOR_TABLE {
    UINT NumDescriptorRanges;
    const D3D12_DESCRIPTOR_RANGE* pDescriptorRanges;
} D3D12_ROOT_DESCRIPTOR_TABLE;
```

テーブル 1 つを、複数の区間の並びとして書きます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `NumDescriptorRanges` | `UINT` | 区間の数 |
| `pDescriptorRanges` | `const D3D12_DESCRIPTOR_RANGE*` | 区間の配列 |

1 つのテーブルに、`CBV` の区間と `SRV` の区間を並べることもできます。1 回の `SetGraphicsRootDescriptorTable` で、その全部のヒープの区間を結びつけられます。ただし、サンプラーは別のヒープなので、同じテーブルには混ぜられません。

## D3D12_ROOT_CONSTANTS {#d3d12_root_constants}

```cpp
typedef struct D3D12_ROOT_CONSTANTS {
    UINT ShaderRegister;
    UINT RegisterSpace;
    UINT Num32BitValues;
} D3D12_ROOT_CONSTANTS;
```

定数を、ディスクリプタを介さずルートに直接置く指定です。シェーダーからは、`cbuffer` の定数バッファとして見えます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `ShaderRegister` | `UINT` | `b` レジスタの番号 |
| `RegisterSpace` | `UINT` | 通常は 0 |
| `Num32BitValues` | `UINT` | 32 ビット値の個数 |

`Num32BitValues` は DWORD の数です。4×4 行列 1 つなら 16、`float4` 1 つなら 4 です。値は `SetGraphicsRoot32BitConstants` で、コマンド リストに直接書き込みます。コマンド リストに値が埋め込まれるため、毎回ヒープを更新する必要がなく、速いのですが、ルートの 64 DWORD の枠を使うので、大きいデータには向きません。

## D3D12_ROOT_DESCRIPTOR {#d3d12_root_descriptor}

```cpp
typedef struct D3D12_ROOT_DESCRIPTOR {
    UINT ShaderRegister;
    UINT RegisterSpace;
} D3D12_ROOT_DESCRIPTOR;
```

CBV / SRV / UAV を、ヒープを介さず GPU アドレスで直接結びつける指定です。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `ShaderRegister` | `UINT` | レジスタ番号（`b0` なら 0） |
| `RegisterSpace` | `UINT` | 通常は 0 |

実際のアドレスは、コマンド リストの `SetGraphicsRootConstantBufferView` などに `GetGPUVirtualAddress()` の値を渡して設定します。ヒープのディスクリプタを作る手間がなく、毎フレーム変わる定数バッファに便利です。ただし、バッファとしてしか結びつけられず、テクスチャは指せません。直接の SRV や UAV は、構造化バッファや、バイト アドレス バッファに限られます。

## 関連ページ

- [ID3D12Device](id3d12device.md) — `CreateRootSignature`
- [ID3D12GraphicsCommandList](id3d12graphicscommandlist.md) — `SetGraphicsRootDescriptorTable` など
- [Root Signature](../root-signature.md) — 設計の考え方
- [View and Descriptor Structs](view-structs.md) — 静的サンプラーなど
- [Pipeline State Structs](pipeline-structs.md) — `pRootSignature` を使う PSO
