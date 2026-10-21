---
title: Root Signature
tags:
  - DirectX
---

# Root Signature

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

シェーダーは関数に似ています。関数には「int を 1 つ float を 2 つ受け取る」というように、引数の型があります。シェーダーにも「定数バッファが 1 つテクスチャが 3 つサンプラーが 1 つ」といった、受け取るリソースの並びがあります。この**引数の並びと種類**を GPU に教える設定が、<strong>ルート シグネチャ</strong>です。

実際に渡すリソース（ディスクリプタ）は、描画のときにコマンド リストでルート シグネチャの各スロットへ割り当てます。つまり、ルート シグネチャは「型」、コマンド リストでの割り当ては「呼び出し」にあたります。

!!! tip "ポイント"
    - ルート シグネチャはシェーダーの引数の型。どのリソースがどのレジスタに来るかを決める。PSO に組み込む。
    - ルート パラメーターは 3 種類。ルート定数は値を直接渡しルート ディスクリプタはバッファのアドレスを渡し、ディスクリプタ テーブルはヒープの範囲を指す。
    - ルート シグネチャの大きさは、最大 64 DWORD（256 バイト）。パラメーターごとにコストがある。
    - 変わる頻度の高いものを前に置く（性能のヒント）。
    - 固定のサンプラーは静的サンプラーとして埋め込める。

!!! info "このページを読む前に"
    ルート シグネチャが指す先の [Descriptor Heap](descriptor-heap.md) と [Descriptor](descriptor.md) を先に読むと、ディスクリプタ テーブルの話が分かりやすくなります。HLSL のレジスタ（`b0`、`t0`、`s0`）は [Shaders and DXC](shaders-dxc.md) にあります。作るメソッドは [ID3D12Device::CreateRootSignature](api/id3d12device.md#createrootsignature) です。

## 3 種類のルート パラメーター

ルート シグネチャはルート パラメーターの並びです。パラメーターには 3 種類あります。

**ルート定数**（32 ビット定数）は、数値をルート シグネチャの中に直接持ちます。ディスクリプタもバッファも要らず一番速く渡せます。物の ID やマテリアルの番号のような少量で頻繁に変わる値に向いています。コストは値の数ぶんの DWORD です。

**ルート ディスクリプタ**（ルート CBV、SRV、UAV）はバッファの GPU アドレスを直接持ちます。ヒープにディスクリプタを作らなくて済むので、物ごとに別のバッファを渡す定数バッファに向いています。コストは 2 DWORD です。ただし、渡せるのはバッファだけでテクスチャは渡せません。

**ディスクリプタ テーブル**はディスクリプタ ヒープの連続した範囲を指します。テクスチャや複数のバッファのまとまりを渡すときに使います。コストは 1 DWORD で、指す先がいくつあっても変わりません。

## ルート シグネチャを作る

ここでは、物ごとの CBV（b0）と SRV を 1 つ含むテーブルと静的サンプラー（s0）を持つルート シグネチャを作ります。まず、ディスクリプタ テーブルが指す範囲を決めます。

```cpp
// テーブルが指す範囲。SRV を 1 つ、レジスタ t0 から。
D3D12_DESCRIPTOR_RANGE srv_range = {};
srv_range.RangeType = D3D12_DESCRIPTOR_RANGE_TYPE_SRV;
srv_range.NumDescriptors = 1;
srv_range.BaseShaderRegister = 0;  // t0
srv_range.RegisterSpace = 0;
srv_range.OffsetInDescriptorsFromTableStart = D3D12_DESCRIPTOR_RANGE_OFFSET_APPEND;
```

`RangeType` は `SRV`、`UAV`、`CBV`、`SAMPLER` のどれかです。`NumDescriptors` は範囲に含まれるディスクリプタの数、`BaseShaderRegister` は先頭のレジスタ番号です。`OffsetInDescriptorsFromTableStart` に `D3D12_DESCRIPTOR_RANGE_OFFSET_APPEND` を渡すと直前の範囲の続きに並びます。

次に、パラメーターを 2 つ作ります。

```cpp
D3D12_ROOT_PARAMETER parameters[2] = {};

// パラメーター 0: ルート CBV（b0）。物ごとの定数バッファ。
parameters[0].ParameterType = D3D12_ROOT_PARAMETER_TYPE_CBV;
parameters[0].Descriptor.ShaderRegister = 0;  // b0
parameters[0].Descriptor.RegisterSpace = 0;
parameters[0].ShaderVisibility = D3D12_SHADER_VISIBILITY_ALL;

// パラメーター 1: ディスクリプタ テーブル。ピクセル シェーダーだけから見える。
parameters[1].ParameterType = D3D12_ROOT_PARAMETER_TYPE_DESCRIPTOR_TABLE;
parameters[1].DescriptorTable.NumDescriptorRanges = 1;
parameters[1].DescriptorTable.pDescriptorRanges = &srv_range;
parameters[1].ShaderVisibility = D3D12_SHADER_VISIBILITY_PIXEL;
```

`ParameterType` で種類を決めると使うメンバーが変わります。ルート CBV は `Descriptor`、ディスクリプタ テーブルは `DescriptorTable` です。`ShaderVisibility` はどのシェーダーの段から見えるかで、特定の段だけに絞るとドライバーが最適化できることがあります。

そのあと静的サンプラーを作り全体をまとめます。

```cpp
// 静的サンプラー（s0）。ルート シグネチャに埋め込む。
D3D12_STATIC_SAMPLER_DESC sampler = {};
sampler.Filter = D3D12_FILTER_ANISOTROPIC;
sampler.AddressU = D3D12_TEXTURE_ADDRESS_MODE_WRAP;
sampler.AddressV = D3D12_TEXTURE_ADDRESS_MODE_WRAP;
sampler.AddressW = D3D12_TEXTURE_ADDRESS_MODE_WRAP;
sampler.MipLODBias = 0.0f;
sampler.MaxAnisotropy = 8;
sampler.ComparisonFunc = D3D12_COMPARISON_FUNC_NEVER;
sampler.BorderColor = D3D12_STATIC_BORDER_COLOR_OPAQUE_BLACK;
sampler.MinLOD = 0.0f;
sampler.MaxLOD = D3D12_FLOAT32_MAX;
sampler.ShaderRegister = 0;  // s0
sampler.RegisterSpace = 0;
sampler.ShaderVisibility = D3D12_SHADER_VISIBILITY_PIXEL;

D3D12_ROOT_SIGNATURE_DESC desc = {};
desc.NumParameters = ARRAYSIZE(parameters);
desc.pParameters = parameters;
desc.NumStaticSamplers = 1;
desc.pStaticSamplers = &sampler;
desc.Flags = D3D12_ROOT_SIGNATURE_FLAG_ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT;  // 頂点入力を使う
```

ルート シグネチャの作成は 2 段階です。まず `D3D12SerializeRootSignature` でバイト列（`ID3DBlob`）にして、次に `CreateRootSignature` でオブジェクトにします。

```cpp
ComPtr<ID3DBlob> serialized;
ComPtr<ID3DBlob> errors;
HRESULT hr = D3D12SerializeRootSignature(&desc, D3D_ROOT_SIGNATURE_VERSION_1, &serialized, &errors);
if (FAILED(hr) && errors) {
  OutputDebugStringA(static_cast<const char*>(errors->GetBufferPointer()));  // エラーの文字列
}

ComPtr<ID3D12RootSignature> root_signature;
device->CreateRootSignature(0, serialized->GetBufferPointer(), serialized->GetBufferSize(),
                            IID_PPV_ARGS(&root_signature));
```

シリアライズに失敗したときの理由は `errors` の文字列にだけ書かれています。必ず表示します（[ID3DBlob](api/id3dblob.md)）。

## コマンド リストで割り当てる

ルート シグネチャを設定したら、パラメーターの番号ごとに実際のリソースを割り当てます。

```cpp
command_list->SetGraphicsRootSignature(root_signature.Get());

// パラメーター 0（ルート CBV）。物ごとの定数バッファの GPU アドレスを、直接渡す。
command_list->SetGraphicsRootConstantBufferView(0, constant_buffer->GetGPUVirtualAddress() + object_offset);

// パラメーター 1（ディスクリプタ テーブル）。シェーダー可視ヒープの、ある位置から始まる範囲を指す。
ID3D12DescriptorHeap* heaps[] = {srv_heap.Get()};
command_list->SetDescriptorHeaps(1, heaps);
command_list->SetGraphicsRootDescriptorTable(1, texture_gpu_handle);
```

割り当てる関数はパラメーターの種類ごとに違います。ルート定数は `SetGraphicsRoot32BitConstants`、ルート CBV は `SetGraphicsRootConstantBufferView`、ルート SRV と UAV は `SetGraphicsRootShaderResourceView` と `SetGraphicsRootUnorderedAccessView`、ディスクリプタ テーブルは `SetGraphicsRootDescriptorTable` です。計算シェーダーでは `SetCompute...` の系列を使います。第 1 引数は必ずパラメーターの番号です（[ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md)）。

## ルート定数を使う

ルート定数はパラメーターを作るときに値の個数とレジスタを決めます。

```cpp
// パラメーター 2: ルート定数 4 個、レジスタ b1。
parameters[2].ParameterType = D3D12_ROOT_PARAMETER_TYPE_32BIT_CONSTANTS;
parameters[2].Constants.ShaderRegister = 1;  // b1
parameters[2].Constants.RegisterSpace = 0;
parameters[2].Constants.Num32BitValues = 4;
parameters[2].ShaderVisibility = D3D12_SHADER_VISIBILITY_ALL;

// 描画のたびに、直接書き込む。ディスクリプタもバッファも要らない。
uint32_t values[4] = {object_id, material_id, 0, 0};
command_list->SetGraphicsRoot32BitConstants(2, 4, values, 0);
```

```hlsl
cbuffer ObjectInfo : register(b1) {
  uint object_id;
  uint material_id;
  uint2 padding;
};
```

最速の渡し方ですがルート シグネチャの容量（64 DWORD）を使います。少量の値だけにします。

## 容量とコスト

ルート シグネチャの容量は最大 64 DWORD（1 DWORD は 4 バイトで、合計 256 バイト）です。ルート定数は 1 つにつき 1 DWORD、ルート ディスクリプタは 2 DWORD（64 ビットのアドレス）、ディスクリプタ テーブルは 1 DWORD を使います。静的サンプラーは容量を使いません。

```text
例: ルート CBV 2 つ（4）+ ディスクリプタ テーブル 3 つ（3）+ ルート定数 4 つ（4）= 11 DWORD
```

容量が足りなくなったときはバッファや SRV をディスクリプタ テーブルにまとめます。1 DWORD でたくさんのディスクリプタを指せるからです。

## 静的サンプラー

変わらないサンプラーは静的サンプラーとしてルート シグネチャに埋め込めます。サンプラー用のヒープを管理する必要がなく、容量も使いません。異方性フィルター、ポイント サンプリング、シャドウの比較など固定の設定のものは、静的サンプラーにするのが手軽です。

静的サンプラーを複数使うときは `D3D12_STATIC_SAMPLER_DESC` の配列を作り `ShaderRegister` を `0`、`1` と変えて並べます。たとえば、`s0` に貼る絵用の異方性フィルター（`WRAP`）、`s1` に G バッファ用のポイント サンプリング（`CLAMP`）を割り当てます。

## 可視性とフラグ

`ShaderVisibility` はそのパラメーターをどのシェーダーの段から見えるようにするかを決めます。`ALL` は全段、`VERTEX` や `PIXEL` はその段だけ `MESH` と `AMPLIFICATION` はメッシュ シェーダーと増幅シェーダーです。段を絞るとドライバーが最適化できることがあります。

ルート シグネチャ全体の `Flags` で、主に使うのは次の 2 つです。`ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT` は頂点バッファの入力レイアウトを使うときに必須です。`CBV_SRV_UAV_HEAP_DIRECTLY_INDEXED` と `SAMPLER_HEAP_DIRECTLY_INDEXED` はバインドレス（シェーダー モデル 6.6 の `ResourceDescriptorHeap`）を使うときに付けます。`DENY_VERTEX_SHADER_ROOT_ACCESS` のように特定の段からのアクセスを禁止するフラグもあります。

## パラメーターの並べ方

変わる頻度が高いパラメーターを前に置くのが推奨です。ドライバーが先頭のパラメーターをレジスタに置いて、速く読めるようにすることがあるためです。

```text
推奨の並び（頻度の高い順）:
  0: 物ごとの CBV（描画のたびに変わる）
  1: マテリアルのディスクリプタ テーブル（マテリアルごと）
  2: フレーム共通のディスクリプタ テーブル（フレームに 1 回）
```

## ルート シグネチャと PSO

ルート シグネチャは PSO に組み込む必要があります（`pso_desc.pRootSignature`）。コマンド リストにも同じルート シグネチャを設定します。PSO のルート シグネチャとコマンド リストに設定したルート シグネチャが一致していないと、エラーになります（[PSO](pso.md)）。

## HLSL にルート シグネチャを書く

ルート シグネチャは C++ で組み立てる代わりに HLSL の中に文字列で書く方法もあります（[Shaders and DXC](shaders-dxc.md)）。短く書けますが C++ 側での動的な制御はできません。

## よくあるミス

??? failure "`D3D12SerializeRootSignature` が失敗する"
    パラメーターの設定が不正です（レジスタの重複、容量の超過など）。`errors` の文字列を表示して確認します。

??? failure "描画してもリソースがシェーダーに届かない（真っ黒になる）"
    `SetGraphicsRoot...` の第 1 引数の番号が、ルート シグネチャの並びと違います。`SetDescriptorHeaps` を呼んでいない場合もあります。

??? failure "ルート シグネチャの容量（64 DWORD）が足りない"
    ルート ディスクリプタ（2 DWORD）を多用しています。ディスクリプタ テーブルにまとめます。

??? failure "PSO とルート シグネチャが合わなくてエラーになる"
    コマンド リストに設定したルート シグネチャが、PSO に組み込んだものと違います。同じオブジェクトを使います。

??? failure "テクスチャをルート SRV で渡そうとして失敗する"
    ルート ディスクリプタに渡せるのは、バッファだけです。テクスチャはディスクリプタ テーブルで渡します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ルート シグネチャは、シェーダーの引数の型。PSO に組み込む
    - [x] 3 種類はルート定数（直接の値）、ルート ディスクリプタ（バッファのアドレス）、ディスクリプタ テーブル（ヒープの範囲）
    - [x] 容量は 64 DWORD。ルート定数は 1、ルート ディスクリプタは 2、テーブルは 1
    - [x] 作成は `D3D12SerializeRootSignature` から `CreateRootSignature`。エラーの文字列を表示する
    - [x] 固定のサンプラーは、静的サンプラーにする
    - [x] 変わる頻度の高いものを前に置く

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3D12Device](api/id3d12device.md)
- [Descriptor Heap](descriptor-heap.md)
- [PSO](pso.md)
- [Constant Buffer](constant-buffer.md)
- [Microsoft Learn: ルート シグネチャ](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/root-signatures)
