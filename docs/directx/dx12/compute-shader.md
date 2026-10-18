---
title: Compute Shader (D3D12)
tags:
  - DirectX
---

# Compute Shader (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

<strong>計算シェーダー</strong>は描画パイプラインと別に GPU の並列計算を自由に使う、シェーダーです。ぼかしヒストグラム、パーティクルの更新、カリングなど画面のピクセルに縛られない処理を書けます。D3D12 では <strong>計算用の PSO とルート シグネチャ</strong>を作りリソースを、<strong>UAV の状態</strong>（`UNORDERED_ACCESS`）にして、`Dispatch` します。連続する `Dispatch` の間には <strong>UAV バリア</strong>が、要ります。

!!! tip "ポイント"
    - 計算用のルート シグネチャと PSO（`CreateComputePipelineState`）を作る。コマンド リストは `SetComputeRootSignature` と `SetComputeRoot…`。
    - 書き込むリソースは `ALLOW_UNORDERED_ACCESS` つきで作り <strong>`UNORDERED_ACCESS` の状態</strong>で使う。
    - 入力は SRV、出力は UAV。両方ともディスクリプタ ヒープに並べて、ディスクリプタ テーブルで渡す。
    - `Dispatch(x, y, z)` のグループ数は切り上げ。シェーダーで範囲チェック。
    - 連続する `Dispatch` で前の書き込みを後が、読むなら <strong>UAV バリア</strong>。

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

HLSL の書き方（`numthreads`、`groupshared`、アトミック）はほかのシェーダーと同じ HLSL です。ウェーブ命令（SM 6.0 以上）が、使えます（[Shaders and DXC](shaders-dxc.md)）。

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

計算用のルート シグネチャには <strong>頂点入力のフラグは不要</strong>です。

## PSO

```cpp
D3D12_COMPUTE_PIPELINE_STATE_DESC pso_desc = {};
pso_desc.pRootSignature = compute_root_signature.Get();
pso_desc.CS = {cs_blob->GetBufferPointer(), cs_blob->GetBufferSize()};

ComPtr<ID3D12PipelineState> compute_pso;
device->CreateComputePipelineState(&pso_desc, IID_PPV_ARGS(&compute_pso));
```

計算用 PSO は <strong>ルート シグネチャとシェーダー</strong>だけです（[PSO](pso.md)）。

## 出力のリソース

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

UAV にできないフォーマット（`_SRGB`、圧縮、深度）は使えません。型つきの UAV の読み込みは `R32_*` だけ保証されます（[Descriptor](descriptor.md)）。

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
| `SetComputeRootSignature` | 計算用のルート シグネチャ |
| `SetComputeRootDescriptorTable` | ディスクリプタ テーブル |
| `SetComputeRoot32BitConstants` | ルート定数 |
| `SetComputeRootConstantBufferView` | ルート CBV |
| `Dispatch(x, y, z)` | グループ数を指定して、起動 |
| `ExecuteIndirect` | 引数を GPU のバッファから、読む（GPU ドリブン） |

描画用（`SetGraphics…`）と計算用（`SetCompute…`）のルート シグネチャは <strong>別々に保持</strong>されます。

## バリア：連続する Dispatch

```cpp
// A が書いた UAV を、B が読む。UAV バリアで、A の書き込み完了を、待たせる。
command_list->Dispatch(groups_x, groups_y, 1);                         // A

auto barrier = CD3DX12_RESOURCE_BARRIER::UAV(output_texture.Get());
command_list->ResourceBarrier(1, &barrier);

command_list->Dispatch(groups_x, groups_y, 1);                         // B（A の結果を読む）
```

`UAV` バリアが無いと B が A の書き込み途中の値を読みます。FFT の段ごとの `Dispatch`、ヒストグラムの集計、ブルームのダウンサンプルで必須です。

### 計算の結果を描画で読む

```cpp
// 計算シェーダーで書いた結果を、次の描画（ピクセル シェーダー）で、読む。状態を、遷移する。
auto to_read = CD3DX12_RESOURCE_BARRIER::Transition(output_texture.Get(), D3D12_RESOURCE_STATE_UNORDERED_ACCESS,
                                                    D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE);
command_list->ResourceBarrier(1, &to_read);
// ... 描画（SRV として読む）...
// 次のフレームで、また、書くなら、UNORDERED_ACCESS に、戻す。
```

## 描画と計算のキュー

計算シェーダーは DIRECT キューでも COMPUTE キューでも実行できます。<strong>COMPUTE キュー</strong>に投げると描画と並列に動きます（非同期コンピュート）。キュー間の順序はフェンスでそろえます（[Command Queue](command-queue.md)、[Fence](fence.md)）。

## 注意点

| 注意 | 内容 |
| --- | --- |
| グループ数 | `(size + N − 1) / N`。範囲チェックをシェーダーに入れる |
| UAV の状態 | 書くときは `UNORDERED_ACCESS`。読み込みの前に遷移 |
| ディスクリプタ ヒープ | `SetDescriptorHeaps` を `Dispatch` の前に |
| スレッド数 | 1 グループは 64 の倍数（効率）。上限 1024 |
| SM 6 の機能 | ウェーブ命令などは `CheckFeatureSupport` で、確認 |

## よくあるミス

??? failure "出力が真っ黒、または前の値のまま"
    UAV のディスクリプタを書いていない。`SetDescriptorHeaps` を呼んでいない。リソースが `UNORDERED_ACCESS` の状態でない。

??? failure "連続した `Dispatch` で結果が、不安定"
    UAV バリアを入れていない。前の書き込みが終わる前に次が、読んでいる。

??? failure "描画で、計算の結果を読むと乱れる"
    `UNORDERED_ACCESS` から `PIXEL_SHADER_RESOURCE` への遷移バリアを忘れた。

??? failure "`SetGraphicsRoot…` を計算シェーダーに使ってエラー"
    計算用は `SetComputeRoot…`。描画用と別の系列。

??? failure "画面の右端・下端が処理されない"
    グループ数を切り捨てで、計算した。`(size + 7) / 8`。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 計算用のルート シグネチャと PSO（`CreateComputePipelineState`）を作る
    - [x] 出力は `ALLOW_UNORDERED_ACCESS` で作り `UNORDERED_ACCESS` の状態で UAV をヒープに
    - [x] `SetComputeRoot…` でディスクリプタ テーブルを渡して `Dispatch`
    - [x] グループ数は切り上げ。シェーダーで範囲チェック
    - [x] 連続する、`Dispatch` の間には UAV バリア。描画で読むなら遷移バリア
    - [x] COMPUTE キューで描画と並列に（非同期コンピュート）

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Resource Barrier](resource-barrier.md)
- [Root Signature](root-signature.md)
- [PSO](pso.md)
- [Compute Shader](../dx11/compute-shader.md)
- [Microsoft Learn: 計算シェーダー](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/compute-pipeline)
