---
title: Compute Shader (D3D12)
tags:
  - DirectX
---

# Compute Shader (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

<strong>計算シェーダー</strong>は、描画パイプラインと、別に、GPU の並列計算を、自由に、使う、シェーダーです。ぼかし、ヒストグラム、パーティクルの更新、カリングなど、画面の、ピクセルに、縛られない、処理を、書けます。D3D12 では、<strong>計算用の PSO と、ルート シグネチャ</strong>を、作り、リソースを、<strong>UAV の状態</strong>（`UNORDERED_ACCESS`）に、して、`Dispatch` します。連続する、`Dispatch` の、間には、<strong>UAV バリア</strong>が、要ります。

!!! tip "ポイント"
    - 計算用の、ルート シグネチャと、PSO（`CreateComputePipelineState`）を、作る。コマンド リストは、`SetComputeRootSignature` と `SetComputeRoot…`。
    - 書き込む、リソースは、`ALLOW_UNORDERED_ACCESS` つきで、作り、<strong>`UNORDERED_ACCESS` の状態</strong>で、使う。
    - 入力は SRV、出力は UAV。両方とも、ディスクリプタ ヒープに、並べて、ディスクリプタ テーブルで、渡す。
    - `Dispatch(x, y, z)` の、グループ数は、切り上げ。シェーダーで、範囲チェック。
    - 連続する、`Dispatch` で、前の書き込みを、後が、読むなら、<strong>UAV バリア</strong>。

## HLSL

```hlsl
// 画像をグレースケールに。1 スレッド = 1 ピクセル。
Texture2D<float4> g_input : register(t0);
RWTexture2D<float4> g_output : register(u0);

[numthreads(8, 8, 1)]
void GrayscaleCS(uint3 id : SV_DispatchThreadID) {
  uint width, height;
  g_output.GetDimensions(width, height);
  if (id.x >= width || id.y >= height) return;                  // 端の余り

  float4 color = g_input.Load(int3(id.xy, 0));
  float gray = dot(color.rgb, float3(0.2126, 0.7152, 0.0722));
  g_output[id.xy] = float4(gray, gray, gray, color.a);
}
```

HLSL の、書き方（`numthreads`、`groupshared`、アトミック）は、ほかのシェーダーと、同じ HLSL です。ウェーブ命令（SM 6.0 以上）が、使えます（[Shaders and DXC](shaders-dxc.md)）。

## ルート シグネチャ

```cpp
// パラメータ 0: SRV（t0）、パラメータ 1: UAV（u0）のディスクリプタ テーブル。
CD3DX12_DESCRIPTOR_RANGE srv_range, uav_range;
srv_range.Init(D3D12_DESCRIPTOR_RANGE_TYPE_SRV, 1, 0);          // t0
uav_range.Init(D3D12_DESCRIPTOR_RANGE_TYPE_UAV, 1, 0);          // u0

CD3DX12_ROOT_PARAMETER parameters[2];
parameters[0].InitAsDescriptorTable(1, &srv_range);
parameters[1].InitAsDescriptorTable(1, &uav_range);

CD3DX12_ROOT_SIGNATURE_DESC desc;
desc.Init(ARRAYSIZE(parameters), parameters, 0, nullptr, D3D12_ROOT_SIGNATURE_FLAG_NONE);   // 頂点入力は、不要
// → D3D12SerializeRootSignature → CreateRootSignature（root-signature.md）
```

計算用の、ルート シグネチャには、<strong>頂点入力の、フラグは、不要</strong>です。

## PSO

```cpp
D3D12_COMPUTE_PIPELINE_STATE_DESC pso_desc = {};
pso_desc.pRootSignature = compute_root_signature.Get();
pso_desc.CS = {cs_blob->GetBufferPointer(), cs_blob->GetBufferSize()};

ComPtr<ID3D12PipelineState> compute_pso;
device->CreateComputePipelineState(&pso_desc, IID_PPV_ARGS(&compute_pso));
```

計算用 PSO は、<strong>ルート シグネチャと、シェーダー</strong>だけです（[PSO](pso.md)）。

## 出力の、リソース

```cpp
// UAV で書く、テクスチャ。ALLOW_UNORDERED_ACCESS が必要。UAV の状態で、作る。
auto desc = CD3DX12_RESOURCE_DESC::Tex2D(DXGI_FORMAT_R8G8B8A8_UNORM, width, height, 1, 1, 1, 0,
                                         D3D12_RESOURCE_FLAG_ALLOW_UNORDERED_ACCESS);
auto heap = CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_DEFAULT);
device->CreateCommittedResource(&heap, D3D12_HEAP_FLAG_NONE, &desc, D3D12_RESOURCE_STATE_UNORDERED_ACCESS, nullptr,
                                IID_PPV_ARGS(&output_texture));

// ディスクリプタ ヒープに、SRV（入力）と、UAV（出力）を、並べる。
device->CreateShaderResourceView(input_texture.Get(), &srv_desc, srv_handle);
device->CreateUnorderedAccessView(output_texture.Get(), nullptr, &uav_desc, uav_handle);
```

UAV に、できない、フォーマット（`_SRGB`、圧縮、深度）は、使えません。型つきの、UAV の、読み込みは、`R32_*` だけ、保証されます（[Descriptor](descriptor.md)）。

## ディスパッチ

```cpp
command_list->SetPipelineState(compute_pso.Get());
command_list->SetComputeRootSignature(compute_root_signature.Get());   // 計算用（SetGraphics… ではない）

ID3D12DescriptorHeap* heaps[] = {srv_uav_heap.Get()};
command_list->SetDescriptorHeaps(1, heaps);
command_list->SetComputeRootDescriptorTable(0, srv_gpu_handle);        // t0
command_list->SetComputeRootDescriptorTable(1, uav_gpu_handle);        // u0

const UINT groups_x = (width + 7) / 8;                                 // 切り上げ
const UINT groups_y = (height + 7) / 8;
command_list->Dispatch(groups_x, groups_y, 1);
```

| 関数 | 内容 |
| --- | --- |
| `SetComputeRootSignature` | 計算用の、ルート シグネチャ |
| `SetComputeRootDescriptorTable` | ディスクリプタ テーブル |
| `SetComputeRoot32BitConstants` | ルート定数 |
| `SetComputeRootConstantBufferView` | ルート CBV |
| `Dispatch(x, y, z)` | グループ数を、指定して、起動 |
| `ExecuteIndirect` | 引数を、GPU のバッファから、読む（GPU ドリブン） |

描画用（`SetGraphics…`）と、計算用（`SetCompute…`）の、ルート シグネチャは、<strong>別々に、保持</strong>されます。

## バリア：連続する、Dispatch

```cpp
// A が書いた UAV を、B が読む。UAV バリアで、A の書き込み完了を、待たせる。
command_list->Dispatch(groups_x, groups_y, 1);                         // A

auto barrier = CD3DX12_RESOURCE_BARRIER::UAV(output_texture.Get());
command_list->ResourceBarrier(1, &barrier);

command_list->Dispatch(groups_x, groups_y, 1);                         // B（A の結果を読む）
```

`UAV` バリアが、無いと、B が、A の、書き込み途中の値を、読みます。FFT の、段ごとの `Dispatch`、ヒストグラムの集計、ブルームの、ダウンサンプルで、必須です。

### 計算の結果を、描画で、読む

```cpp
// 計算シェーダーで書いた結果を、次の描画（ピクセル シェーダー）で、読む。状態を、遷移する。
auto to_read = CD3DX12_RESOURCE_BARRIER::Transition(output_texture.Get(), D3D12_RESOURCE_STATE_UNORDERED_ACCESS,
                                                    D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE);
command_list->ResourceBarrier(1, &to_read);
// ... 描画（SRV として読む）...
// 次のフレームで、また、書くなら、UNORDERED_ACCESS に、戻す。
```

## 描画と、計算の、キュー

計算シェーダーは、DIRECT キューでも、COMPUTE キューでも、実行できます。<strong>COMPUTE キュー</strong>に、投げると、描画と、並列に、動きます（非同期コンピュート）。キュー間の、順序は、フェンスで、そろえます（[Command Queue](command-queue.md)、[Fence](fence.md)）。

## 注意点

| 注意 | 内容 |
| --- | --- |
| グループ数 | `(size + N − 1) / N`。範囲チェックを、シェーダーに入れる |
| UAV の、状態 | 書くときは、`UNORDERED_ACCESS`。読み込みの前に、遷移 |
| ディスクリプタ ヒープ | `SetDescriptorHeaps` を、`Dispatch` の前に |
| スレッド数 | 1 グループは、64 の倍数（効率）。上限 1024 |
| SM 6 の機能 | ウェーブ命令などは、`CheckFeatureSupport` で、確認 |

## よくあるミス

??? failure "出力が、真っ黒、または、前の値のまま"
    UAV の、ディスクリプタを、書いていない。`SetDescriptorHeaps` を、呼んでいない。リソースが、`UNORDERED_ACCESS` の、状態でない。

??? failure "連続した `Dispatch` で、結果が、不安定"
    UAV バリアを、入れていない。前の書き込みが、終わる前に、次が、読んでいる。

??? failure "描画で、計算の結果を、読むと、乱れる"
    `UNORDERED_ACCESS` から、`PIXEL_SHADER_RESOURCE` への、遷移バリアを、忘れた。

??? failure "`SetGraphicsRoot…` を、計算シェーダーに、使って、エラー"
    計算用は、`SetComputeRoot…`。描画用と、別の、系列。

??? failure "画面の、右端・下端が、処理されない"
    グループ数を、切り捨てで、計算した。`(size + 7) / 8`。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 計算用の、ルート シグネチャと PSO（`CreateComputePipelineState`）を、作る
    - [x] 出力は、`ALLOW_UNORDERED_ACCESS` で作り、`UNORDERED_ACCESS` の状態で、UAV を、ヒープに
    - [x] `SetComputeRoot…` で、ディスクリプタ テーブルを、渡して、`Dispatch`
    - [x] グループ数は、切り上げ。シェーダーで、範囲チェック
    - [x] 連続する、`Dispatch` の間には、UAV バリア。描画で、読むなら、遷移バリア
    - [x] COMPUTE キューで、描画と、並列に（非同期コンピュート）

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Resource Barrier](resource-barrier.md)
- [Root Signature](root-signature.md)
- [PSO](pso.md)
- [Compute Shader](../dx11/compute-shader.md)
- [Microsoft Learn: 計算シェーダー](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/compute-pipeline)
