---
title: Compute Shader (D3D12)
tags:
  - DirectX
---

# Compute Shader (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

描画パイプラインは頂点を変換して、ピクセルを塗るという流れが決まっています。ぼかしヒストグラム、パーティクルの更新、カリングのように画面のピクセルに縛られない処理を GPU でやりたいときは、この流れが窮屈です。

そこで使うのが <strong>コンピュート シェーダー</strong>です。描画パイプラインとは別に GPU の並列計算をそのまま使えます。D3D12 では計算用の PSO とルート シグネチャを作り書き込むリソースを UAV の状態にして、`Dispatch` で起動します。

!!! tip "ポイント"
    - 計算用のルート シグネチャと PSO（`CreateComputePipelineState`）を作る。コマンド リストは `SetComputeRootSignature` と `SetComputeRoot...` を使う。
    - 書き込むリソースは `ALLOW_UNORDERED_ACCESS` を付けて作り `UNORDERED_ACCESS` の状態で使う。
    - 入力は SRV、出力は UAV。どちらもディスクリプタ ヒープに並べて、ディスクリプタ テーブルで渡す。
    - `Dispatch(x, y, z)` のグループ数は切り上げて求める。シェーダー側で範囲を確認する。
    - 連続する `Dispatch` で、前の書き込みを次が読むなら UAV バリアを入れる。

!!! info "このページを読む前に"
    計算の結果を置く UAV は [Descriptor](descriptor.md)、ルート シグネチャは [Root Signature](root-signature.md)、PSO は [PSO](pso.md)、UAV バリアは [Resource Barrier](resource-barrier.md) で説明しています。`Dispatch` の引数は [ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md#dispatch) にあります。

## HLSL

画像をグレースケールにする最小のコンピュート シェーダーです。1 つのスレッドが 1 ピクセルを担当します。

```hlsl
Texture2D<float4> g_input : register(t0);
RWTexture2D<float4> g_output : register(u0);

[numthreads(8, 8, 1)]
void GrayscaleCS(uint3 id : SV_DispatchThreadID) {
  uint width, height;
  g_output.GetDimensions(width, height);
  if (id.x >= width || id.y >= height) return;  // 端の余り

  float4 color = g_input.Load(int3(id.xy, 0));
  float gray = dot(color.rgb, float3(0.2126, 0.7152, 0.0722));
  g_output[id.xy] = float4(gray, gray, gray, color.a);
}
```

`[numthreads(8, 8, 1)]` は 1 グループのスレッド数（8×8 = 64）です。`SV_DispatchThreadID` は全体の中でのスレッドの番号で、ここではピクセルの座標として使っています。`if` で範囲を確認しているのは、画像の大きさが 8 の倍数とは限らないためです。`groupshared` メモリやアトミック命令、ウェーブ命令（SM 6.0 以上）も使えます（[Shaders and DXC](shaders-dxc.md)）。

## ルート シグネチャ

入力の SRV と出力の UAV をそれぞれディスクリプタ テーブルで渡すルート シグネチャです。

```cpp
// パラメーター 0 は SRV（t0）、パラメーター 1 は UAV（u0）のディスクリプタ テーブル。
D3D12_DESCRIPTOR_RANGE srv_range = {};
srv_range.RangeType = D3D12_DESCRIPTOR_RANGE_TYPE_SRV;
srv_range.NumDescriptors = 1;
srv_range.BaseShaderRegister = 0;  // t0
srv_range.OffsetInDescriptorsFromTableStart = D3D12_DESCRIPTOR_RANGE_OFFSET_APPEND;

D3D12_DESCRIPTOR_RANGE uav_range = srv_range;
uav_range.RangeType = D3D12_DESCRIPTOR_RANGE_TYPE_UAV;  // u0

D3D12_ROOT_PARAMETER parameters[2] = {};
parameters[0].ParameterType = D3D12_ROOT_PARAMETER_TYPE_DESCRIPTOR_TABLE;
parameters[0].DescriptorTable.NumDescriptorRanges = 1;
parameters[0].DescriptorTable.pDescriptorRanges = &srv_range;
parameters[0].ShaderVisibility = D3D12_SHADER_VISIBILITY_ALL;
parameters[1] = parameters[0];
parameters[1].DescriptorTable.pDescriptorRanges = &uav_range;

D3D12_ROOT_SIGNATURE_DESC desc = {};
desc.NumParameters = ARRAYSIZE(parameters);
desc.pParameters = parameters;
desc.Flags = D3D12_ROOT_SIGNATURE_FLAG_NONE;  // 頂点入力は不要
// D3D12SerializeRootSignature から CreateRootSignature へ進む（Root Signature のページ）
```

計算用のルート シグネチャには頂点入力のフラグは要りません。

## PSO

計算用の PSO はルート シグネチャとシェーダーだけです。

```cpp
D3D12_COMPUTE_PIPELINE_STATE_DESC pso_desc = {};
pso_desc.pRootSignature = compute_root_signature.Get();
pso_desc.CS = {cs_blob->GetBufferPointer(), cs_blob->GetBufferSize()};

ComPtr<ID3D12PipelineState> compute_pso;
device->CreateComputePipelineState(&pso_desc, IID_PPV_ARGS(&compute_pso));
```

## 出力のリソースを作る

UAV に書くテクスチャは `ALLOW_UNORDERED_ACCESS` のフラグを付けて作ります。初期状態は `UNORDERED_ACCESS` にします。

```cpp
D3D12_RESOURCE_DESC desc = MakeTexture2DDesc(DXGI_FORMAT_R8G8B8A8_UNORM, width, height, 1, 1,
                                             D3D12_RESOURCE_FLAG_ALLOW_UNORDERED_ACCESS);
D3D12_HEAP_PROPERTIES heap = MakeHeapProperties(D3D12_HEAP_TYPE_DEFAULT);
device->CreateCommittedResource(&heap, D3D12_HEAP_FLAG_NONE, &desc, D3D12_RESOURCE_STATE_UNORDERED_ACCESS,
                                nullptr, IID_PPV_ARGS(&output_texture));

// ディスクリプタ ヒープに、SRV（入力）と UAV（出力）を並べる。
device->CreateShaderResourceView(input_texture.Get(), &srv_desc, srv_handle);
device->CreateUnorderedAccessView(output_texture.Get(), nullptr, &uav_desc, uav_handle);
```

UAV にできない形式（`_SRGB`、圧縮形式、深度）は使えません。型つきの UAV を読めるのは、`R32_*` の形式だけが保証されています（[Descriptor](descriptor.md)）。

## Dispatch する

```cpp
command_list->SetPipelineState(compute_pso.Get());
command_list->SetComputeRootSignature(compute_root_signature.Get());  // 計算用（SetGraphics... ではない）

ID3D12DescriptorHeap* heaps[] = {srv_uav_heap.Get()};
command_list->SetDescriptorHeaps(1, heaps);
command_list->SetComputeRootDescriptorTable(0, srv_gpu_handle);  // t0
command_list->SetComputeRootDescriptorTable(1, uav_gpu_handle);  // u0

const UINT groups_x = (width + 7) / 8;  // 切り上げ
const UINT groups_y = (height + 7) / 8;
command_list->Dispatch(groups_x, groups_y, 1);
```

描画用（`SetGraphics...`）と計算用（`SetCompute...`）のルート シグネチャは、別々に保持されます。計算では `SetComputeRootSignature`、`SetComputeRootDescriptorTable`、`SetComputeRoot32BitConstants`、`SetComputeRootConstantBufferView` を使います。引数を GPU のバッファから読む `ExecuteIndirect` もあります（GPU ドリブン）。

## 連続する Dispatch の間にバリア

A の `Dispatch` が書いた UAV を B の `Dispatch` が読むときは、UAV バリアで A の書き込みの完了を待たせます。

```cpp
command_list->Dispatch(groups_x, groups_y, 1);  // A

D3D12_RESOURCE_BARRIER barrier = MakeUavBarrier(output_texture.Get());
command_list->ResourceBarrier(1, &barrier);

command_list->Dispatch(groups_x, groups_y, 1);  // B（A の結果を読む）
```

UAV バリアがないと B は A の書き込み途中の値を読みます。FFT の段ごとの `Dispatch`、ヒストグラムの集計、ブルームのダウンサンプルで必須です。

### 計算の結果を描画で読む

計算シェーダーが書いた結果を次の描画のピクセル シェーダーで読むときは、状態を切り替えます。

```cpp
D3D12_RESOURCE_BARRIER to_read = MakeTransitionBarrier(
    output_texture.Get(), D3D12_RESOURCE_STATE_UNORDERED_ACCESS, D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE);
command_list->ResourceBarrier(1, &to_read);
// ... 描画（SRV として読む）...
// 次のフレームでまた書くなら、UNORDERED_ACCESS に戻す。
```

## どのキューで実行するか

計算シェーダーは DIRECT のキューでも COMPUTE のキューでも実行できます。COMPUTE のキューに渡すと描画と並列に動きます（非同期コンピュート）。キューどうしの順番はフェンスでそろえます（[Command Queue](command-queue.md)、[Fence](fence.md)）。

## 注意点

グループ数は `(size + N − 1) / N` と切り上げて求め範囲の確認をシェーダーに入れます。UAV に書くときは `UNORDERED_ACCESS` の状態で、読む前に遷移します。`SetDescriptorHeaps` は `Dispatch` の前に呼びます。1 グループのスレッド数は 64 の倍数にすると効率がよく、上限は 1024 です。SM 6 の機能（ウェーブ命令など）は、`CheckFeatureSupport` で対応を確認します。

## よくあるミス

??? failure "出力が真っ黒、または前の値のまま"
    UAV のディスクリプタを書いていないか `SetDescriptorHeaps` を呼んでいないかリソースが `UNORDERED_ACCESS` の状態になっていません。

??? failure "連続した `Dispatch` で結果が不安定になる"
    UAV バリアを入れていません。前の書き込みが終わる前に次が読んでいます。

??? failure "描画で、計算の結果を読むと乱れる"
    `UNORDERED_ACCESS` から `PIXEL_SHADER_RESOURCE` への遷移バリアを忘れています。

??? failure "計算シェーダーに `SetGraphicsRoot...` を使ってエラーになる"
    計算用は `SetComputeRoot...` です。描画用とは別の系列です。

??? failure "画面の右端と下端が処理されない"
    グループ数を切り捨てで計算しています。`(size + 7) / 8` と切り上げます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 計算用のルート シグネチャと PSO（`CreateComputePipelineState`）を作る
    - [x] 出力は `ALLOW_UNORDERED_ACCESS` で作り `UNORDERED_ACCESS` の状態で UAV をヒープへ置く
    - [x] `SetComputeRoot...` でディスクリプタ テーブルを渡して、`Dispatch` する
    - [x] グループ数は切り上げる。シェーダーで範囲を確認する
    - [x] 連続する `Dispatch` の間は UAV バリア。描画で読むなら遷移バリア
    - [x] COMPUTE のキューで、描画と並列に動かせる（非同期コンピュート）

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md)
- [Resource Barrier](resource-barrier.md)
- [Root Signature](root-signature.md)
- [PSO](pso.md)
- [Microsoft Learn: 計算パイプライン](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/compute-pipeline)
