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
| [`D3D12_ROOT_SIGNATURE_FLAGS`](#d3d12_root_signature_flags) | ルート シグネチャ全体への指定 | `D3D12_ROOT_SIGNATURE_DESC` の `Flags` |
| [バージョン 1.1 の構造体](#root-signature-v1-1) | 範囲とルート ディスクリプタへの約束 | `D3D12SerializeVersionedRootSignature` |

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

`RangeType` は、HLSL の `t`（SRV）、`u`（UAV）、`b`（CBV）、`s`（サンプラー）に対応します。`t0` から 4 枚のテクスチャを使うなら、`RangeType = SRV`、`NumDescriptors = 4`、`BaseShaderRegister = 0` です。`NumDescriptors` に `UINT_MAX` を入れると、無制限（バインドレス）として扱われます。

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

## D3D12_ROOT_SIGNATURE_FLAGS {#d3d12_root_signature_flags}

```cpp
typedef enum D3D12_ROOT_SIGNATURE_FLAGS {
    D3D12_ROOT_SIGNATURE_FLAG_NONE                                = 0,
    D3D12_ROOT_SIGNATURE_FLAG_ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT  = 0x1,
    D3D12_ROOT_SIGNATURE_FLAG_DENY_VERTEX_SHADER_ROOT_ACCESS      = 0x2,
    D3D12_ROOT_SIGNATURE_FLAG_DENY_HULL_SHADER_ROOT_ACCESS        = 0x4,
    D3D12_ROOT_SIGNATURE_FLAG_DENY_DOMAIN_SHADER_ROOT_ACCESS      = 0x8,
    D3D12_ROOT_SIGNATURE_FLAG_DENY_GEOMETRY_SHADER_ROOT_ACCESS    = 0x10,
    D3D12_ROOT_SIGNATURE_FLAG_DENY_PIXEL_SHADER_ROOT_ACCESS       = 0x20,
    D3D12_ROOT_SIGNATURE_FLAG_ALLOW_STREAM_OUTPUT                 = 0x40,
    D3D12_ROOT_SIGNATURE_FLAG_LOCAL_ROOT_SIGNATURE                = 0x80,
    D3D12_ROOT_SIGNATURE_FLAG_DENY_AMPLIFICATION_SHADER_ROOT_ACCESS = 0x100,
    D3D12_ROOT_SIGNATURE_FLAG_DENY_MESH_SHADER_ROOT_ACCESS        = 0x200,
    D3D12_ROOT_SIGNATURE_FLAG_CBV_SRV_UAV_HEAP_DIRECTLY_INDEXED   = 0x400,
    D3D12_ROOT_SIGNATURE_FLAG_SAMPLER_HEAP_DIRECTLY_INDEXED       = 0x800
} D3D12_ROOT_SIGNATURE_FLAGS;
```

`D3D12_ROOT_SIGNATURE_DESC::Flags` に入れる、ビットの組み合わせです。大きく分けると、「入力アセンブラを使うか」「どのステージにルートを見せないか」「ストリーム出力を使うか」「ローカルか」「ヒープを番号で直接引くか」の 5 種類です。

#### D3D12_ROOT_SIGNATURE_FLAG_NONE {#d3d12_root_signature_flag_none}

何も指定しません。コンピュート シェーダーだけのルート シグネチャや、頂点バッファを使わず `SV_VertexID` で頂点を作る描画なら、これで足ります。頂点バッファの入力レイアウトを持つ PSO と組み合わせると、描画時にエラーになります。

#### D3D12_ROOT_SIGNATURE_FLAG_ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT {#d3d12_root_signature_flag_allow_input_assembler_input_layout}

入力アセンブラ（頂点バッファとインデックス バッファ）を使う描画に必要です。付け忘れると、入力レイアウトを持つ PSO を作る段階か、描画する段階でエラーになります。頂点バッファを使わないメッシュ シェーダーの経路では、付けません。付けたままでも動きますが、ドライバーが IA 用の準備をするぶん、わずかに無駄です。

#### D3D12_ROOT_SIGNATURE_FLAG_DENY_VERTEX_SHADER_ROOT_ACCESS {#d3d12_root_signature_flag_deny_vertex_shader_root_access}

頂点シェーダーからルート引数を見えなくします。DENY 系は、「このステージはルートを使わない」と宣言する最適化のヒントです。ドライバーは、そのステージのためにルート引数の枠を確保しなくて済みます。ただし、ルート パラメーターの `ShaderVisibility` で個別に絞るほうが細かく指定できるので、実際には全体で足りることが多く、必須の指定ではありません。

#### D3D12_ROOT_SIGNATURE_FLAG_DENY_HULL_SHADER_ROOT_ACCESS {#d3d12_root_signature_flag_deny_hull_shader_root_access}

ハル シェーダー（テッセレーションの制御点を扱うステージ）から見えなくします。テッセレーションを使わないなら、付けておくとドライバーの手間が減ります。

#### D3D12_ROOT_SIGNATURE_FLAG_DENY_DOMAIN_SHADER_ROOT_ACCESS {#d3d12_root_signature_flag_deny_domain_shader_root_access}

ドメイン シェーダー（テッセレーションで生まれた頂点を扱うステージ）から見えなくします。

#### D3D12_ROOT_SIGNATURE_FLAG_DENY_GEOMETRY_SHADER_ROOT_ACCESS {#d3d12_root_signature_flag_deny_geometry_shader_root_access}

ジオメトリ シェーダーから見えなくします。

#### D3D12_ROOT_SIGNATURE_FLAG_DENY_PIXEL_SHADER_ROOT_ACCESS {#d3d12_root_signature_flag_deny_pixel_shader_root_access}

ピクセル シェーダーから見えなくします。深度だけを描くパス（シャドウ マップなど）は、ピクセル シェーダーが要らないので、ここで付けておくと無駄が減ります。

#### D3D12_ROOT_SIGNATURE_FLAG_ALLOW_STREAM_OUTPUT {#d3d12_root_signature_flag_allow_stream_output}

ストリーム出力（頂点シェーダーやジオメトリ シェーダーの結果をバッファへ書き出す機能）を使う PSO で必要です。使わないなら付けません。

#### D3D12_ROOT_SIGNATURE_FLAG_LOCAL_ROOT_SIGNATURE {#d3d12_root_signature_flag_local_root_signature}

DirectX Raytracing のローカル ルート シグネチャであることを表します。シェーダー テーブルのレコードごとに違う引数を持たせるときに使い、通常のグラフィックスやコンピュートには付けません。

#### D3D12_ROOT_SIGNATURE_FLAG_DENY_AMPLIFICATION_SHADER_ROOT_ACCESS {#d3d12_root_signature_flag_deny_amplification_shader_root_access}

増幅シェーダーから見えなくします。メッシュ シェーダーの PSO で、増幅シェーダーを使わないときに付けます。

#### D3D12_ROOT_SIGNATURE_FLAG_DENY_MESH_SHADER_ROOT_ACCESS {#d3d12_root_signature_flag_deny_mesh_shader_root_access}

メッシュ シェーダーから見えなくします。

#### D3D12_ROOT_SIGNATURE_FLAG_CBV_SRV_UAV_HEAP_DIRECTLY_INDEXED {#d3d12_root_signature_flag_cbv_srv_uav_heap_directly_indexed}

Shader Model 6.6 の `ResourceDescriptorHeap[i]` を許可します。シェーダーは、バインドされている CBV/SRV/UAV ヒープを、番号で直接引けるようになります。バインドレスの土台です。付けずに `ResourceDescriptorHeap` を使うシェーダーで PSO を作ると失敗します。このフラグはバージョン 1.1 の記述でシリアライズします。

もう 1 つ決まりがあります。このフラグを付けたルート シグネチャは、`SetGraphicsRootSignature` を呼ぶ時点で、ヒープがすでに `SetDescriptorHeaps` で結ばれている必要があります。順序が逆だと、デバッグ レイヤーがエラーを出します（[バインドレス](../../../rendering/gpu-driven-dx12/bindless.md)）。

#### D3D12_ROOT_SIGNATURE_FLAG_SAMPLER_HEAP_DIRECTLY_INDEXED {#d3d12_root_signature_flag_sampler_heap_directly_indexed}

`SamplerDescriptorHeap[i]` を許可します。サンプラーも番号で引くときに付けます。静的サンプラーだけで足りるなら要りません。

## バージョン 1.1 の構造体 {#root-signature-v1-1}

バージョン 1.1 では、構造体のほとんどに `1` の付いた版（`D3D12_ROOT_SIGNATURE_DESC1`、`D3D12_ROOT_PARAMETER1`、`D3D12_DESCRIPTOR_RANGE1`、`D3D12_ROOT_DESCRIPTOR1`）があります。1.0 との違いは、ドライバーへの「約束」を書く `Flags` メンバーが増えたことだけです。約束を書くと、ドライバーはヒープの中身や、バッファの中身が実行中に変わらないことを前提にして、ルート引数を最適に扱えます。

```cpp
typedef struct D3D12_DESCRIPTOR_RANGE1 {
    D3D12_DESCRIPTOR_RANGE_TYPE  RangeType;
    UINT                         NumDescriptors;
    UINT                         BaseShaderRegister;
    UINT                         RegisterSpace;
    D3D12_DESCRIPTOR_RANGE_FLAGS Flags;                      // 1.1 で増えた
    UINT                         OffsetInDescriptorsFromTableStart;
} D3D12_DESCRIPTOR_RANGE1;

typedef struct D3D12_ROOT_DESCRIPTOR1 {
    UINT                        ShaderRegister;
    UINT                        RegisterSpace;
    D3D12_ROOT_DESCRIPTOR_FLAGS Flags;                       // 1.1 で増えた
} D3D12_ROOT_DESCRIPTOR1;
```

バージョン 1.0 と 1.1 の構造体を、1 つの入れ物で扱うのが `D3D12_VERSIONED_ROOT_SIGNATURE_DESC` です。`Version` で `D3D_ROOT_SIGNATURE_VERSION_1_0` か `_1_1` を選び、対応する `Desc_1_0` か `Desc_1_1` を埋めます。シリアライズは `D3D12SerializeVersionedRootSignature` で行います（[D3D12SerializeRootSignature](d3d12serializerootsignature.md)）。

### D3D12_DESCRIPTOR_RANGE_FLAGS {#d3d12_descriptor_range_flags}

`D3D12_DESCRIPTOR_RANGE1::Flags` に入れる、ディスクリプタ テーブルの 1 区間への約束です。2 種類の約束があります。1 つは「ヒープに書かれたディスクリプタ自体」が変わるか、もう 1 つは「ディスクリプタが指すデータ（バッファやテクスチャの中身）」が変わるかです。

#### D3D12_DESCRIPTOR_RANGE_FLAG_NONE {#d3d12_descriptor_range_flag_none}

既定の約束です。CBV と SRV の区間なら、「ディスクリプタは、テーブルが設定されてから実行が終わるまで変わらない。データも、同じ間は変わらない」という約束になります。UAV の区間は、UAV がシェーダーから書かれるので、データは変わりうる（`DATA_VOLATILE`）ことになります。バージョン 1.0 は、すべてが変わりうる（volatile）という最も緩い約束でした。

#### D3D12_DESCRIPTOR_RANGE_FLAG_DESCRIPTORS_VOLATILE {#d3d12_descriptor_range_flag_descriptors_volatile}

ディスクリプタが、コマンド リストの実行中に書き換えられるかもしれないと伝えます。バインドレスで、テクスチャを後から読み込んで空き番号を埋める使い方では、この指定が必要です。ドライバーは、ディスクリプタを先読みしたり、キャッシュしたりできなくなるので、必要な区間だけに付けます。

#### D3D12_DESCRIPTOR_RANGE_FLAG_DATA_VOLATILE {#d3d12_descriptor_range_flag_data_volatile}

ディスクリプタが指すデータが、実行中に書き換えられるかもしれないと伝えます。UAV で書く区間は、これが既定です。CBV や SRV の区間に付けると、ドライバーはデータをキャッシュできなくなります。

#### D3D12_DESCRIPTOR_RANGE_FLAG_DATA_STATIC_WHILE_SET_AT_EXECUTE {#d3d12_descriptor_range_flag_data_static_while_set_at_execute}

データが、テーブルが設定されてから実行が終わる間は変わらないと約束します。CBV と SRV の既定の約束です。

#### D3D12_DESCRIPTOR_RANGE_FLAG_DATA_STATIC {#d3d12_descriptor_range_flag_data_static}

データが、ディスクリプタが設定された時点から、二度と変わらないと約束します。最も強い約束で、読み込んだあとに書き換えない静的なテクスチャに向きます。この約束を破ると、描画結果は未定義です。

#### D3D12_DESCRIPTOR_RANGE_FLAG_DESCRIPTORS_STATIC_KEEPING_BUFFER_BOUNDS_CHECKS {#d3d12_descriptor_range_flag_descriptors_static_keeping_buffer_bounds_checks}

ディスクリプタは変わらないと約束しつつ、バッファの範囲外アクセスの検査は残します。ディスクリプタが静的なら範囲検査を省けるドライバーがあるので、検査を省かせたくない（範囲外アクセスを 0 として扱う挙動を保ちたい）ときに使います。

### D3D12_ROOT_DESCRIPTOR_FLAGS {#d3d12_root_descriptor_flags}

`D3D12_ROOT_DESCRIPTOR1::Flags` に入れる、ルート CBV / SRV / UAV への約束です。ルート ディスクリプタはアドレスそのものなので、ディスクリプタが変わるという概念がなく、データが変わるかどうかだけを約束します。

#### D3D12_ROOT_DESCRIPTOR_FLAG_NONE {#d3d12_root_descriptor_flag_none}

既定です。CBV と SRV なら「実行中は変わらない」、UAV なら「変わりうる」の約束になります。

#### D3D12_ROOT_DESCRIPTOR_FLAG_DATA_VOLATILE {#d3d12_root_descriptor_flag_data_volatile}

データが実行中に変わりうると伝えます。GPU が自分で書いたバッファを、そのまま次のパスで読むような使い方が当たります。

#### D3D12_ROOT_DESCRIPTOR_FLAG_DATA_STATIC_WHILE_SET_AT_EXECUTE {#d3d12_root_descriptor_flag_data_static_while_set_at_execute}

データが、ルート引数として設定されている間は変わらないと約束します。フレームの頭にアップロードしたあと、そのフレームでは書き換えないインスタンス バッファやマテリアル バッファに向いています。

#### D3D12_ROOT_DESCRIPTOR_FLAG_DATA_STATIC {#d3d12_root_descriptor_flag_data_static}

データが、設定された時点から二度と変わらないと約束します。起動時に作って、そのまま使い続ける定数バッファなどです。

### D3D12_SHADER_VISIBILITY {#d3d12_shader_visibility}

`D3D12_ROOT_PARAMETER::ShaderVisibility` と `D3D12_STATIC_SAMPLER_DESC::ShaderVisibility` に入れる値です。`ALL`、`VERTEX`、`HULL`、`DOMAIN`、`GEOMETRY`、`PIXEL`、`AMPLIFICATION`、`MESH` があります。ステージを 1 つだけ指定すると、そのステージからだけ見えます。複数のステージで同じリソースを使うなら `ALL` にします。絞ったほうが、ドライバーが不要なステージへの受け渡しを省けます。

## 関連ページ

- [ID3D12Device](id3d12device.md) — `CreateRootSignature`
- [ID3D12GraphicsCommandList](id3d12graphicscommandlist.md) — `SetGraphicsRootDescriptorTable` など
- [Root Signature](../root-signature.md) — 設計の考え方
- [View and Descriptor Structs](view-structs.md) — 静的サンプラーなど
- [Pipeline State Structs](pipeline-structs.md) — `pRootSignature` を使う PSO
