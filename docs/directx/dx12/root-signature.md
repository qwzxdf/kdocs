---
title: Root Signature
tags:
  - DirectX
---

# Root Signature

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>ルート シグネチャ</strong>は <strong>シェーダーが、受け取るリソースの「型」</strong>を GPU に教える設定です。「定数バッファが 1 つテクスチャが 3 つサンプラーが 1 つ」といった、<strong>引数の並びと種類</strong>を決めます。関数のシグネチャ（引数の型）に似ています。実際の、リソース（ディスクリプタ）は描画時にコマンド リストでこのルート シグネチャの、スロットに割り当てます。

!!! tip "ポイント"
    - ルート シグネチャ ＝ シェーダーの引数の型（どんなリソースがどのレジスタに、来るか）。<strong>PSO に組み込まれる</strong>。
    - ルート パラメータの 3 種類: <strong>ルート定数</strong>（値を直接）、<strong>ルート ディスクリプタ</strong>（CBV・SRV・UAV をアドレスで）、<strong>ディスクリプタ テーブル</strong>（ヒープの範囲を指す）。
    - ルート シグネチャの大きさの上限は <strong>64 DWORD</strong>（256 バイト）。パラメータごとにコスト（DWORD）がある。
    - 使う頻度の高い物を前に置く（性能のヒント）。
    - サンプラーは <strong>静的サンプラー</strong>として、ルート シグネチャに埋め込める。

## 3 種類のルート パラメータ

| 種類 | 内容 | コスト（DWORD） | 向く用途 |
| --- | --- | --- | --- |
| <strong>ルート定数</strong>（32 ビット定数） | 数値をルート シグネチャに直接、持つ | 値の数 | 少量の頻繁に変わる値（物の ID、マテリアルの番号） |
| <strong>ルート ディスクリプタ</strong>（ルート CBV / SRV / UAV） | バッファの、GPU アドレスを直接、持つ | 2 | 物ごとの定数バッファ（毎回、別のバッファ） |
| <strong>ディスクリプタ テーブル</strong> | ディスクリプタ ヒープの連続範囲を指す | 1 | テクスチャ、バッファのまとまり |

ルート ディスクリプタは <strong>バッファだけ</strong>（テクスチャは、不可）。テクスチャはディスクリプタ テーブルで、渡します。

## 作る

```cpp
// パラメータ 0: ルート CBV（b0）。物ごとの定数バッファ。
// パラメータ 1: ディスクリプタ テーブル。SRV を 1 つ（t0）。
CD3DX12_DESCRIPTOR_RANGE srv_range;
srv_range.Init(D3D12_DESCRIPTOR_RANGE_TYPE_SRV, 1, 0);          // 種類、個数、ベース レジスタ（t0）

CD3DX12_ROOT_PARAMETER parameters[2];
parameters[0].InitAsConstantBufferView(0);                      // b0
parameters[1].InitAsDescriptorTable(1, &srv_range, D3D12_SHADER_VISIBILITY_PIXEL);   // ピクセル シェーダーだけ

// 静的サンプラー（s0）。ルート シグネチャに、埋め込む。
CD3DX12_STATIC_SAMPLER_DESC sampler(0, D3D12_FILTER_ANISOTROPIC);   // 0: レジスタ s0

CD3DX12_ROOT_SIGNATURE_DESC desc;
desc.Init(ARRAYSIZE(parameters), parameters, 1, &sampler,
          D3D12_ROOT_SIGNATURE_FLAG_ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT);   // 頂点入力を、使う
```

```cpp
// シリアライズ（バイナリ化）して、デバイスに、作らせる。
ComPtr<ID3DBlob> serialized, errors;
HRESULT hr = D3D12SerializeRootSignature(&desc, D3D_ROOT_SIGNATURE_VERSION_1, &serialized, &errors);
if (FAILED(hr) && errors) OutputDebugStringA(static_cast<const char*>(errors->GetBufferPointer()));

ComPtr<ID3D12RootSignature> root_signature;
device->CreateRootSignature(0, serialized->GetBufferPointer(), serialized->GetBufferSize(),
                            IID_PPV_ARGS(&root_signature));
```

作成は 2 段階です。まず、`D3D12SerializeRootSignature` でバイナリ（`ID3DBlob`）にして次に `CreateRootSignature` で、オブジェクトにします。<strong>シリアライズのエラー</strong>（`errors`）は必ず表示します。

## コマンド リストで割り当てる

```cpp
command_list->SetGraphicsRootSignature(root_signature.Get());   // ルート シグネチャを、設定

// パラメータ 0（ルート CBV）: 物ごとの定数バッファの、GPU アドレスを、直接渡す。
command_list->SetGraphicsRootConstantBufferView(0, constant_buffer->GetGPUVirtualAddress() + object_offset);

// パラメータ 1（ディスクリプタ テーブル）: シェーダー可視ヒープの、ある位置から、始まる範囲を、指す。
ID3D12DescriptorHeap* heaps[] = {srv_heap.Get()};
command_list->SetDescriptorHeaps(1, heaps);
command_list->SetGraphicsRootDescriptorTable(1, texture_gpu_handle);
```

| 関数 | 内容 |
| --- | --- |
| `SetGraphicsRootSignature` | 描画用のルート シグネチャを設定 |
| `SetComputeRootSignature` | 計算用 |
| `SetGraphicsRoot32BitConstants(index, count, data, offset)` | ルート定数を書く |
| `SetGraphicsRootConstantBufferView(index, address)` | ルート CBV |
| `SetGraphicsRootShaderResourceView(index, address)` | ルート SRV（バッファ） |
| `SetGraphicsRootUnorderedAccessView(index, address)` | ルート UAV（バッファ） |
| `SetGraphicsRootDescriptorTable(index, handle)` | ディスクリプタ テーブル |

計算シェーダーは `SetCompute…` の系列を使います。

## ルート定数

```cpp
// パラメータ 2: ルート定数 4 つ（uint の物 ID、マテリアル ID など）。
parameters[2].InitAsConstants(4, 1);                            // 4 個の 32 ビット値、レジスタ b1

// 描画のたびに、直接、書く（ディスクリプタも、バッファも、不要）。
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

ルート定数は <strong>最速</strong>の渡し方ですが、ルート シグネチャの容量（64 DWORD）を食うので少量だけにします。

## 容量とコスト

ルート シグネチャは <strong>最大 64 DWORD</strong>（1 DWORD = 4 バイト、合計 256 バイト）です。

| パラメータ | コスト |
| --- | --- |
| ルート定数 | 1 つにつき 1 DWORD |
| ルート ディスクリプタ（CBV・SRV・UAV） | 2 DWORD（64 ビットアドレス） |
| ディスクリプタ テーブル | 1 DWORD |
| 静的サンプラー | 0（容量を使わない） |

```text
例: ルート CBV 2 つ（4）+ ディスクリプタ テーブル 3 つ（3）+ ルート定数 4 つ（4）= 11 DWORD
```

容量が足りないときはパラメータを <strong>ディスクリプタ テーブルにまとめる</strong>（1 DWORD で多数の、ディスクリプタを指せる）ことで、節約します。

## 静的サンプラー

```cpp
// 変わらないサンプラーは、ルート シグネチャに、埋め込むと、ディスクリプタ ヒープが、不要になる。
CD3DX12_STATIC_SAMPLER_DESC samplers[2] = {
    CD3DX12_STATIC_SAMPLER_DESC(0, D3D12_FILTER_ANISOTROPIC, D3D12_TEXTURE_ADDRESS_MODE_WRAP,
                                D3D12_TEXTURE_ADDRESS_MODE_WRAP, D3D12_TEXTURE_ADDRESS_MODE_WRAP),     // s0: 貼る絵用
    CD3DX12_STATIC_SAMPLER_DESC(1, D3D12_FILTER_MIN_MAG_MIP_POINT, D3D12_TEXTURE_ADDRESS_MODE_CLAMP,
                                D3D12_TEXTURE_ADDRESS_MODE_CLAMP, D3D12_TEXTURE_ADDRESS_MODE_CLAMP),   // s1: G バッファ用
};
```

固定のサンプラー（異方性、ポイント、シャドウの比較）は静的サンプラーにすると、ヒープの管理が要らず容量も使いません。

## 可視性

パラメータは <strong>どのシェーダーから、見えるか</strong>（`D3D12_SHADER_VISIBILITY_*`）を指定できます。

| 値 | 内容 |
| --- | --- |
| `ALL` | 全段から見える |
| `VERTEX`、`PIXEL`、`GEOMETRY`、`HULL`、`DOMAIN` | その段だけ |
| `MESH`、`AMPLIFICATION` | メッシュ・増幅シェーダー |

特定の段だけに制限するとドライバーが、最適化できることがあります。

## ルート シグネチャのフラグ

| フラグ | 内容 |
| --- | --- |
| `ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT` | 頂点バッファの入力レイアウトを使う（頂点入力を使うなら必須） |
| `DENY_VERTEX_SHADER_ROOT_ACCESS` など | その段から、アクセスさせない（最適化） |
| `CBV_SRV_UAV_HEAP_DIRECTLY_INDEXED` | ビンドレス（SM 6.6 の `ResourceDescriptorHeap`）を使う |
| `SAMPLER_HEAP_DIRECTLY_INDEXED` | サンプラーのビンドレス |

## パラメータの順序

ルート パラメータは <strong>変わる頻度が、高い物を前に</strong>、置くのが推奨です。ドライバーがルート シグネチャを一部、レジスタに置いて前のパラメータを速く、読めるようにすることがあるためです。

```text
推奨の、並び（頻度の、高い順）:
  0: 物ごとの CBV（毎描画で、変わる）
  1: マテリアルの、ディスクリプタ テーブル（マテリアルごと）
  2: フレーム共通の、ディスクリプタ テーブル（フレームに 1 回）
```

## ルート シグネチャと PSO

ルート シグネチャは <strong>PSO に組み込む</strong>必要があります（`pso_desc.pRootSignature`）。コマンド リストにも同じルート シグネチャを設定します。<strong>PSO のルート シグネチャとコマンド リストに設定したルート シグネチャが、一致</strong>しないとエラーです（[PSO](pso.md)）。

## よくあるミス

??? failure "`D3D12SerializeRootSignature` が、失敗する"
    パラメータの設定が不正（レジスタの重複、容量超過）。`errors` の文字列を表示して確認する。

??? failure "描画しても、リソースがシェーダーに届かない（真っ黒）"
    パラメータの番号（`SetGraphicsRoot…` の第 1 引数）がルート シグネチャの並びと違う。`SetDescriptorHeaps` を呼んでいない。

??? failure "ルート シグネチャの容量（64 DWORD）が足りない"
    ルート ディスクリプタ（2 DWORD）を多用している。ディスクリプタ テーブルにまとめる。

??? failure "PSO とルート シグネチャが合わない、エラー"
    コマンド リストに設定したルート シグネチャが PSO に組み込んだ物と違う。同じオブジェクトを使う。

??? failure "テクスチャをルート SRV で渡そうとして、失敗する"
    ルート ディスクリプタはバッファだけ。テクスチャはディスクリプタ テーブル。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ルート シグネチャ ＝ シェーダーの引数の型。PSO に組み込む
    - [x] 3 種類: ルート定数（直接の値）、ルート ディスクリプタ（バッファのアドレス）、ディスクリプタ テーブル（ヒープの範囲）
    - [x] 容量は 64 DWORD。ルート定数 1、ルート ディスクリプタ 2、テーブル 1
    - [x] 作成: `D3D12SerializeRootSignature` → `CreateRootSignature`。エラー文字列を表示
    - [x] 固定サンプラーは、静的サンプラー
    - [x] 変わる頻度の高いものを前に

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Descriptor Heap](descriptor-heap.md)
- [PSO](pso.md)
- [Constant Buffer](constant-buffer.md)
- [Microsoft Learn: ルート シグネチャ](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/root-signatures)
