---
title: ID3D12Device
tags:
  - DirectX
api:
  - ID3D12Device
---

# ID3D12Device

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

D3D12 では GPU に置く物はほとんどすべて、`ID3D12Device` のメソッドで作ります。リソース、ヒープ、コマンド キュー、フェンス、PSO と作る物の種類ごとに `CreateXxx` が用意されているので、メソッドの数は多いのですが役割で 4 つに分けると覚えやすくなります。

<svg class="fig flow" viewBox="0 0 720 300" role="img" aria-label="デバイスのメソッドは 4 つの役割に分かれる"><defs><marker id="fdD" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">デバイスの 4 つの役割</text><rect x="250" y="40" width="220" height="40" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="360.0" y="60.0" text-anchor="middle" dominant-baseline="central" style="font-size:14px;font-weight:600">ID3D12Device</text><rect x="12" y="120" width="164" height="36" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="94.0" y="138.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">物を置く</text><line x1="360" y1="80" x2="94" y2="120" stroke="currentColor" stroke-width="2" marker-end="url(#fdD)"/><rect x="12" y="168" width="164" height="24" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="94.0" y="180.0" text-anchor="middle" dominant-baseline="central" style="font-size:9px;font-weight:600">CreateCommittedResource</text><rect x="12" y="198" width="164" height="24" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="94.0" y="210.0" text-anchor="middle" dominant-baseline="central" style="font-size:9px;font-weight:600">CreateHeap</text><rect x="12" y="228" width="164" height="24" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="94.0" y="240.0" text-anchor="middle" dominant-baseline="central" style="font-size:9px;font-weight:600">CreatePlacedResource</text><rect x="188" y="120" width="164" height="36" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="270.0" y="138.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">実行の道具</text><line x1="360" y1="80" x2="270" y2="120" stroke="currentColor" stroke-width="2" marker-end="url(#fdD)"/><rect x="188" y="168" width="164" height="24" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="270.0" y="180.0" text-anchor="middle" dominant-baseline="central" style="font-size:9px;font-weight:600">CreateCommandQueue</text><rect x="188" y="198" width="164" height="24" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="270.0" y="210.0" text-anchor="middle" dominant-baseline="central" style="font-size:9px;font-weight:600">CreateCommandAllocator</text><rect x="188" y="228" width="164" height="24" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="270.0" y="240.0" text-anchor="middle" dominant-baseline="central" style="font-size:9px;font-weight:600">CreateCommandList</text><rect x="188" y="258" width="164" height="24" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="270.0" y="270.0" text-anchor="middle" dominant-baseline="central" style="font-size:9px;font-weight:600">CreateFence</text><rect x="364" y="120" width="164" height="36" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="446.0" y="138.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">ディスクリプタ</text><line x1="360" y1="80" x2="446" y2="120" stroke="currentColor" stroke-width="2" marker-end="url(#fdD)"/><rect x="364" y="168" width="164" height="24" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="446.0" y="180.0" text-anchor="middle" dominant-baseline="central" style="font-size:9px;font-weight:600">CreateDescriptorHeap</text><rect x="364" y="198" width="164" height="24" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="446.0" y="210.0" text-anchor="middle" dominant-baseline="central" style="font-size:9px;font-weight:600">CreateRenderTargetView</text><rect x="364" y="228" width="164" height="24" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="446.0" y="240.0" text-anchor="middle" dominant-baseline="central" style="font-size:9px;font-weight:600">CreateShaderResourceView</text><rect x="364" y="258" width="164" height="24" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="446.0" y="270.0" text-anchor="middle" dominant-baseline="central" style="font-size:9px;font-weight:600">CreateConstantBufferView</text><rect x="540" y="120" width="164" height="36" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="622.0" y="138.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">パイプライン</text><line x1="360" y1="80" x2="622" y2="120" stroke="currentColor" stroke-width="2" marker-end="url(#fdD)"/><rect x="540" y="168" width="164" height="24" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="622.0" y="180.0" text-anchor="middle" dominant-baseline="central" style="font-size:9px;font-weight:600">CreateRootSignature</text><rect x="540" y="198" width="164" height="24" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="622.0" y="210.0" text-anchor="middle" dominant-baseline="central" style="font-size:9px;font-weight:600">CreateGraphicsPipelineState</text><rect x="540" y="228" width="164" height="24" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="622.0" y="240.0" text-anchor="middle" dominant-baseline="central" style="font-size:9px;font-weight:600">CreateComputePipelineState</text></svg>

デバイス自体の作り方は [Device and Factory](../factory-device.md) で説明しています。このページはデバイスができたあとに呼ぶメソッドの辞書です。

!!! tip "ポイント"
    - 作る物はすべて `CreateXxx`。戻り値の `HRESULT` を必ず確認する。
    - ビュー（`CreateXxxView`）だけは `void` を返し、ディスクリプタを指定の場所に書き込む。
    - `nodeMask` は GPU が 1 つなら 0。
    - 取り出すインターフェースは `IID_PPV_ARGS` で渡す。
    - 新しい機能は `ID3D12Device1` 以降にある（[Device and Factory](../factory-device.md#queryinterface-as)）。

!!! info "このページを読む前に"
    デバイスを作る流れと `IID_PPV_ARGS` は [Device and Factory](../factory-device.md)、記録と実行の関係は [DirectX 12 Guide](../index.md) で説明しています。GPU に置く物の種類は [Heaps and Resources](../heaps-resources.md) と [Descriptor Heap](../descriptor-heap.md) が詳しいです。

## メソッド一覧

| メソッド | 作る物・役割 | 詳しいページ |
| --- | --- | --- |
| [`CreateCommittedResource`](#createcommittedresource) | バッファやテクスチャ（ヒープごと） | [Heaps and Resources](../heaps-resources.md) |
| [`CreateCommandQueue`](#createcommandqueue) | コマンド キュー | [Command Queue](../command-queue.md) |
| [`CreateCommandAllocator`](#createcommandallocator) | 命令を記録するメモリ | [Command Allocator](../command-allocator.md) |
| [`CreateCommandList`](#createcommandlist) | 命令を記録する窓口 | [Command List](../command-list.md) |
| [`CreateFence`](#createfence) | CPU と GPU の同期 | [Fence](../fence.md) |
| [`CreateDescriptorHeap`](#createdescriptorheap) | ディスクリプタの置き場 | [Descriptor Heap](../descriptor-heap.md) |
| [`GetDescriptorHandleIncrementSize`](#getdescriptorhandleincrementsize) | ディスクリプタ 1 つの幅 | [Descriptor](../descriptor.md) |
| [`CreateRenderTargetView`](#createrendertargetview) | 描き込み先のビュー | [Descriptor](../descriptor.md) |
| [`CreateDepthStencilView`](#createdepthstencilview) | 深度のビュー | [Depth Buffer](../depth-buffer.md) |
| [`CreateShaderResourceView`](#createshaderresourceview) | 読み取り用のビュー | [Descriptor](../descriptor.md) |
| [`CreateUnorderedAccessView`](#createunorderedaccessview) | 読み書き用のビュー | [Compute Shader](../compute-shader.md) |
| [`CreateConstantBufferView`](#createconstantbufferview) | 定数バッファのビュー | [Constant Buffer](../constant-buffer.md) |
| [`CreateSampler`](#createsampler) | サンプラー | [Descriptor](../descriptor.md) |
| [`CopyDescriptorsSimple`](#copydescriptorssimple) | ディスクリプタのコピー | [Descriptor Heap](../descriptor-heap.md) |
| [`CreateRootSignature`](#createrootsignature) | ルート シグネチャ | [Root Signature](../root-signature.md) |
| [`CreateGraphicsPipelineState`](#creategraphicspipelinestate) | 描画の PSO | [PSO](../pso.md) |
| [`CreateComputePipelineState`](#createcomputepipelinestate) | 計算の PSO | [PSO](../pso.md) |
| [`CreateQueryHeap`](#createqueryheap) | GPU の時刻や統計の記録先 | [GPU Queries and Timing (D3D12)](../query-timing.md) |
| [`CreateHeap`](#createheap) | ヒープだけ（リソースは別に置く） | [Heaps and Resources](../heaps-resources.md) |
| [`CreatePlacedResource`](#createplacedresource) | ヒープの中の指定位置にリソースを置く | [Heaps and Resources](../heaps-resources.md) |
| [`GetCopyableFootprints`](#getcopyablefootprints) | テクスチャのコピーに必要な配置の計算 | [Texture Upload](../texture-upload.md) |
| [`GetDeviceRemovedReason`](#getdeviceremovedreason) | デバイスが消えた理由 | [Debug Layer](../debug-layer.md) |
| [`CheckFeatureSupport`](../factory-device.md#checkfeaturesupport) | GPU の機能の確認 | [Device and Factory](../factory-device.md) |
| [`SetName`](../factory-device.md#setname) | デバッグ用の名前 | [Device and Factory](../factory-device.md) |

## リソースを作る

### CreateCommittedResource {#createcommittedresource}

```cpp
HRESULT ID3D12Device::CreateCommittedResource(
    const D3D12_HEAP_PROPERTIES* pHeapProperties,
    D3D12_HEAP_FLAGS HeapFlags,
    const D3D12_RESOURCE_DESC* pDesc,
    D3D12_RESOURCE_STATES InitialResourceState,
    const D3D12_CLEAR_VALUE* pOptimizedClearValue,
    REFIID riidResource,
    void** ppvResource);
```

バッファやテクスチャを作ります。「Committed」はリソースと同じ大きさのヒープを 1 つ作って、そこへリソース全体を置くという意味です。ヒープを自分で管理しなくてよいので、まず使うのはこれです。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pHeapProperties` | `const D3D12_HEAP_PROPERTIES*` | どこのメモリに置くか（`DEFAULT`、`UPLOAD`、`READBACK`） |
| `HeapFlags` | `D3D12_HEAP_FLAGS` | ヒープの性質。通常は `D3D12_HEAP_FLAG_NONE` |
| `pDesc` | `const D3D12_RESOURCE_DESC*` | 種類（バッファか 2D テクスチャか）、大きさ形式 |
| `InitialResourceState` | `D3D12_RESOURCE_STATES` | 作った直後の状態 |
| `pOptimizedClearValue` | `const D3D12_CLEAR_VALUE*` | レンダー ターゲットと深度バッファの最適化用のクリア値。ほかは `nullptr` |
| `riidResource` / `ppvResource` | `REFIID` / `void**` | `IID_PPV_ARGS(&resource)` で渡す |

`pHeapProperties` は置き場所の選択です。CPU が書いて GPU が読むものは `UPLOAD`（CPU から書けるが GPU からは遅い）、GPU だけが使うものは `DEFAULT`（GPU からは速いが CPU からは触れない）、GPU が書いて CPU が読むものは `READBACK` にします。`DEFAULT` へデータを入れるにはいったん `UPLOAD` に書いて、コピーのコマンドで移します。

`InitialResourceState` はあとで使うバリアの「今の状態」と一致していなければなりません。`UPLOAD` のヒープは必ず `D3D12_RESOURCE_STATE_GENERIC_READ` です。違う値を渡すと失敗します。`DEFAULT` のテクスチャはコピーで中身を入れるなら `COPY_DEST` から始めるのが定番です。

`pOptimizedClearValue` は `ClearRenderTargetView` などで使う色や深度の値を先に伝えておく引数です。ここで伝えた値でクリアすると、GPU が高速なクリアを使えます。別の値でクリアしても動きますが、警告が出ます。

戻り値は成功なら `S_OK` です。主な失敗は次のとおりです。

| 戻り値 | 原因 |
| --- | --- |
| `E_OUTOFMEMORY` | VRAM か共有メモリが足りない |
| `E_INVALIDARG` | `pDesc` と `InitialResourceState` や `HeapProperties` の組み合わせが合わない（`UPLOAD` に `COPY_DEST` など） |
| `DXGI_ERROR_DEVICE_REMOVED` | デバイスがすでに消えている（[GetDeviceRemovedReason](#getdeviceremovedreason)） |

```cpp
// 頂点バッファ（UPLOAD に置く最小の例）。
D3D12_HEAP_PROPERTIES heap = MakeHeapProperties(D3D12_HEAP_TYPE_UPLOAD);  // dx12_util.h（Helper Functions）
D3D12_RESOURCE_DESC desc = MakeBufferDesc(size_in_bytes);
ComPtr<ID3D12Resource> buffer;
HRESULT hr = device->CreateCommittedResource(
    &heap, D3D12_HEAP_FLAG_NONE, &desc,
    D3D12_RESOURCE_STATE_GENERIC_READ,  // UPLOAD は必ずこれ
    nullptr, IID_PPV_ARGS(&buffer));
```

### CreateHeap {#createheap}

```cpp
HRESULT ID3D12Device::CreateHeap(
    const D3D12_HEAP_DESC* pDesc,
    REFIID riid,
    void** ppvHeap);
```

ヒープだけを作ります。リソースは入りません。1 つの大きなヒープに複数のリソースを `CreatePlacedResource` で並べて置くために使います。

引数は `pDesc`（大きさ `D3D12_HEAP_PROPERTIES`、アラインメント、フラグ）と取り出す先です。`pDesc->SizeInBytes` はアラインメント（通常 64 KB）の倍数にします。

ヒープの種類によって置けるリソースが制限されます。`D3D12_HEAP_FLAG_ALLOW_ONLY_BUFFERS` などでバッファだけテクスチャだけのように制限できます。制限なしだとリソース ヒープ層（Resource Heap Tier）が 1 のハードウェアでは、バッファとテクスチャを同じヒープに置けません。

戻り値は成功なら `S_OK` です。失敗は `E_OUTOFMEMORY`（メモリ不足）と `E_INVALIDARG`（大きさやアラインメントが不正）です。

### CreatePlacedResource {#createplacedresource}

```cpp
HRESULT ID3D12Device::CreatePlacedResource(
    ID3D12Heap* pHeap,
    UINT64 HeapOffset,
    const D3D12_RESOURCE_DESC* pDesc,
    D3D12_RESOURCE_STATES InitialState,
    const D3D12_CLEAR_VALUE* pOptimizedClearValue,
    REFIID riid,
    void** ppvResource);
```

`CreateHeap` で作ったヒープの `HeapOffset` の位置にリソースを置きます。使わなくなったリソースの場所へ別のリソースを置き直せるので、一時的なバッファを使い回して VRAM を節約するときに使います。

`HeapOffset` はリソースのアラインメント（`pDesc->Alignment`、通常 64 KB。MSAA は 4 MB）の倍数にします。`GetResourceAllocationInfo` で必要な大きさとアラインメントを先に調べられます。ほかの引数は `CreateCommittedResource` と同じです。

置いた直後のリソースの中身は決まっていません（前に置かれていたリソースのデータが残っている可能性があります）。レンダー ターゲットと深度バッファは、使う前に必ず `DiscardResource` かクリアで初期化します。重なる範囲に置いた複数のリソースは同時には使えません。使い分けるにはエイリアシング バリア（`D3D12_RESOURCE_BARRIER_TYPE_ALIASING`）を入れます。

## 実行の道具を作る

### CreateCommandQueue {#createcommandqueue}

```cpp
HRESULT ID3D12Device::CreateCommandQueue(
    const D3D12_COMMAND_QUEUE_DESC* pDesc,
    REFIID riid,
    void** ppCommandQueue);
```

コマンド キューを作ります。キューは記録したコマンド リストを GPU に渡す窓口です。

`pDesc` の `Type` が大事で `DIRECT`（描画も計算もコピーもできる）、`COMPUTE`（計算とコピー）、`COPY`（コピーだけ）から選びます。スワップ チェーンに結ぶのは `DIRECT` のキューです。`Priority`、`Flags`、`NodeMask` の意味は [Command Queue](../command-queue.md) にあります。

戻り値は成功なら `S_OK` です。`E_INVALIDARG`（`Type` が不正）、`E_OUTOFMEMORY` が失敗の主な原因です。

### CreateCommandAllocator {#createcommandallocator}

```cpp
HRESULT ID3D12Device::CreateCommandAllocator(
    D3D12_COMMAND_LIST_TYPE type,
    REFIID riid,
    void** ppCommandAllocator);
```

コマンド リストが命令を書き込むメモリの置き場（アロケーター）を作ります。

`type` はこのアロケーターから作るコマンド リストの種類で `DIRECT`、`COMPUTE`、`COPY`、`BUNDLE` から選びます。**種類が違うリストには使えません**。DIRECT のアロケーターで COMPUTE のリストを作ろうとすると失敗します。

アロケーターは GPU がそのメモリを読み終わるまで `Reset` できません。1 つのアロケーターには同時に記録中のコマンド リストを 1 つしか結びつけられません。このためフレームごとにアロケーターを 1 つ用意します（[Frame Resources](../frame-resources.md)）。

戻り値は成功なら `S_OK` です。

### CreateCommandList {#createcommandlist}

```cpp
HRESULT ID3D12Device::CreateCommandList(
    UINT nodeMask,
    D3D12_COMMAND_LIST_TYPE type,
    ID3D12CommandAllocator* pCommandAllocator,
    ID3D12PipelineState* pInitialState,
    REFIID riid,
    void** ppCommandList);
```

命令を記録するコマンド リストを作ります。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `nodeMask` | `UINT` | マルチ GPU のときの GPU 指定。1 つなら `0` |
| `type` | `D3D12_COMMAND_LIST_TYPE` | リストの種類。アロケーターと同じにする |
| `pCommandAllocator` | `ID3D12CommandAllocator*` | 記録先のアロケーター。`type` が一致している必要がある |
| `pInitialState` | `ID3D12PipelineState*` | 最初の PSO。`nullptr` でよい（あとから `SetPipelineState` で決める） |
| `riid` / `ppCommandList` | `REFIID` / `void**` | `IID_PPV_ARGS(&list)` で渡す |

作ったリストはすでに**記録中**の状態です。そのため、記録するつもりがないのに放置すると、あとで `Reset` ができません。最初のフレームの前にいったん `Close()` してから、毎フレームの `Reset` から記録を始めるのが定番です。

`pInitialState` に `nullptr` を渡して構いません。PSO はあとで `SetPipelineState` で切り替えるので、初期値は重要ではありません。

戻り値は成功なら `S_OK` です。`E_INVALIDARG`（`type` とアロケーターの種類が合わない）、`E_OUTOFMEMORY` が失敗の原因です。

### CreateFence {#createfence}

```cpp
HRESULT ID3D12Device::CreateFence(
    UINT64 InitialValue,
    D3D12_FENCE_FLAGS Flags,
    REFIID riid,
    void** ppFence);
```

フェンスを作ります。フェンスは 64 ビットの数字を 1 つ持つ物で、GPU が「ここまで終わった」と数字を進め CPU がその数字を見て待つという使い方をします。

`InitialValue` は数字の初期値で通常は `0` です。`Flags` は通常 `D3D12_FENCE_FLAG_NONE` です。複数のデバイス（GPU）で共有するときだけ `SHARED` を使います。

使い方（`Signal`、`SetEventOnCompletion`、`GetCompletedValue`）は [Fence](../fence.md) にあります。

戻り値は成功なら `S_OK` です。

## ディスクリプタを扱う

### CreateDescriptorHeap {#createdescriptorheap}

```cpp
HRESULT ID3D12Device::CreateDescriptorHeap(
    const D3D12_DESCRIPTOR_HEAP_DESC* pDescriptorHeapDesc,
    REFIID riid,
    void** ppvHeap);
```

ディスクリプタ（リソースの「見方」を書いた小さなデータ）を並べる置き場を作ります。

`pDescriptorHeapDesc` の `Type` は置くディスクリプタの種類で `CBV_SRV_UAV`、`SAMPLER`、`RTV`、`DSV` の 4 つから選びます。**種類を混ぜることはできません**。`NumDescriptors` は入る数です。`Flags` の `D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE` を付けるとシェーダーから見えるヒープになり `CBV_SRV_UAV` と `SAMPLER` にだけ付けられます（RTV と DSV には付けられません）。

`SHADER_VISIBLE` のヒープは同じ種類のものを同時にコマンド リストに結べるのが 1 つずつ（`CBV_SRV_UAV` と `SAMPLER` で合計 2 つ）という制限があります。大きなヒープを 1 つ作って、描画ごとに切り分けて使うのが定番です。詳しくは [Descriptor Heap](../descriptor-heap.md) にあります。

戻り値は成功なら `S_OK` です。`E_INVALIDARG`（`RTV` に `SHADER_VISIBLE` を付けたなど）と `E_OUTOFMEMORY` が失敗の主な原因です。

### GetDescriptorHandleIncrementSize {#getdescriptorhandleincrementsize}

```cpp
UINT ID3D12Device::GetDescriptorHandleIncrementSize(
    D3D12_DESCRIPTOR_HEAP_TYPE DescriptorHeapType);
```

ディスクリプタ 1 つの大きさをバイト数で返します。ヒープの `n` 番目のハンドルを求めるときに使います。

大きさは GPU とヒープの種類によって違います。決め打ちで 32 などの値を使うとほかの GPU で壊れます。必ずこのメソッドで調べます。値はヒープの種類ごとに起動時に 1 回調べて、保存しておけば足ります。

```cpp
UINT rtv_size = device->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_RTV);
D3D12_CPU_DESCRIPTOR_HANDLE start = rtv_heap->GetCPUDescriptorHandleForHeapStart();
D3D12_CPU_DESCRIPTOR_HANDLE handle = OffsetHandle(start, 1, rtv_size);  // 1 つ先のスロット
```

### CreateRenderTargetView {#createrendertargetview}

```cpp
void ID3D12Device::CreateRenderTargetView(
    ID3D12Resource* pResource,
    const D3D12_RENDER_TARGET_VIEW_DESC* pDesc,
    D3D12_CPU_DESCRIPTOR_HANDLE DestDescriptor);
```

リソースを「描き込み先」として見るためのディスクリプタ（RTV）を書き込みます。戻り値はありません。

`pResource` は描き込み先のテクスチャ、`DestDescriptor` は書き込む先のヒープ内の位置です。`pDesc` に `nullptr` を渡すとリソースが持つ形式をそのまま使って、全体を 1 つのビューとして作ります。ミップレベルを指定したり sRGB 形式で見たりするときだけ `D3D12_RENDER_TARGET_VIEW_DESC` を渡します。

書き込み先の位置は RTV のヒープの中でなければいけません。型が違うヒープ（`CBV_SRV_UAV` など）を渡すとデバッグ レイヤーがエラーを出します。

### CreateDepthStencilView {#createdepthstencilview}

```cpp
void ID3D12Device::CreateDepthStencilView(
    ID3D12Resource* pResource,
    const D3D12_DEPTH_STENCIL_VIEW_DESC* pDesc,
    D3D12_CPU_DESCRIPTOR_HANDLE DestDescriptor);
```

リソースを「深度・ステンシル」として見るためのディスクリプタ（DSV）を書き込みます。戻り値はありません。

引数の意味は `CreateRenderTargetView` と同じで書き込み先は DSV のヒープです。深度バッファを SRV としても読むときは、リソースを `R32_TYPELESS` などの `TYPELESS` 形式で作り DSV 側は `D32_FLOAT`、SRV 側は `R32_FLOAT` のように見方ごとに形式を決めて `pDesc` で渡します（[Depth Buffer](../depth-buffer.md)）。

### CreateShaderResourceView {#createshaderresourceview}

```cpp
void ID3D12Device::CreateShaderResourceView(
    ID3D12Resource* pResource,
    const D3D12_SHADER_RESOURCE_VIEW_DESC* pDesc,
    D3D12_CPU_DESCRIPTOR_HANDLE DestDescriptor);
```

リソースを「シェーダーが読むもの」として見るディスクリプタ（SRV）を書き込みます。戻り値はありません。

`pDesc` には形式、次元（`D3D12_SRV_DIMENSION_TEXTURE2D` など）、ミップの範囲、`Shader4ComponentMapping`（チャンネルの並べ替え。普通は `D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING`）を入れます。`nullptr` を渡せるのはリソースが `TYPELESS` ではなく、1 つの形式で作られているときだけです。

構造化バッファを読むときは `ViewDimension` を `BUFFER` にして、`Buffer.StructureByteStride` に要素の大きさを書きます。

### CreateUnorderedAccessView {#createunorderedaccessview}

```cpp
void ID3D12Device::CreateUnorderedAccessView(
    ID3D12Resource* pResource,
    ID3D12Resource* pCounterResource,
    const D3D12_UNORDERED_ACCESS_VIEW_DESC* pDesc,
    D3D12_CPU_DESCRIPTOR_HANDLE DestDescriptor);
```

リソースを「読み書きできるもの」として見るディスクリプタ（UAV）を書き込みます。戻り値はありません。コンピュート シェーダーの出力先に使います。

`pCounterResource` は `AppendStructuredBuffer` などのカウンターを別のバッファに置くときの指定です。使わなければ `nullptr` にします。そのとき、`pDesc` には `D3D12_UNORDERED_ACCESS_VIEW_DESC` を必ず渡します（`nullptr` にできないケースがあります）。

UAV にするリソースは `D3D12_RESOURCE_FLAG_ALLOW_UNORDERED_ACCESS` を付けて作っておきます。付いていないとデバッグ レイヤーがエラーを出します。

### CreateConstantBufferView {#createconstantbufferview}

```cpp
void ID3D12Device::CreateConstantBufferView(
    const D3D12_CONSTANT_BUFFER_VIEW_DESC* pDesc,
    D3D12_CPU_DESCRIPTOR_HANDLE DestDescriptor);
```

定数バッファのディスクリプタ（CBV）を書き込みます。他のビューと違ってリソースは引数にありません。`pDesc` の中の `BufferLocation`（GPU 仮想アドレス）と `SizeInBytes` で指定します。

`SizeInBytes` は **256 の倍数**にします。256 の倍数でないとデバッグ レイヤーがエラーを出します。定数バッファは構造体の大きさが 256 の倍数とは限らないので、`(sizeof(T) + 255) & ~255` のように切り上げてそのぶん多めに確保します（[Constant Buffer](../constant-buffer.md)）。

`BufferLocation` は `resource->GetGPUVirtualAddress()` にバッファ内のオフセットを足した値です。これも 256 バイトにそろっていなければいけません。

### CreateSampler {#createsampler}

```cpp
void ID3D12Device::CreateSampler(
    const D3D12_SAMPLER_DESC* pDesc,
    D3D12_CPU_DESCRIPTOR_HANDLE DestDescriptor);
```

サンプラー（テクスチャの読み方）を書き込みます。`pDesc` にはフィルター（`D3D12_FILTER_MIN_MAG_MIP_LINEAR`、`D3D12_FILTER_ANISOTROPIC` など）、アドレス モード（`WRAP`、`CLAMP`、`MIRROR`、`BORDER`）、異方性の最大値などを入れます。

書き込み先は `SAMPLER` 型のヒープです。ルート シグネチャの**静的サンプラー**を使うとディスクリプタ ヒープを使わずにサンプラーを指定できるので、固定のサンプラーはそちらが手軽です。

### CopyDescriptorsSimple {#copydescriptorssimple}

```cpp
void ID3D12Device::CopyDescriptorsSimple(
    UINT NumDescriptors,
    D3D12_CPU_DESCRIPTOR_HANDLE DestDescriptorRangeStart,
    D3D12_CPU_DESCRIPTOR_HANDLE SrcDescriptorRangeStart,
    D3D12_DESCRIPTOR_HEAP_TYPE DescriptorHeapsType);
```

ディスクリプタを連続した範囲でコピーします。`SHADER_VISIBLE` のヒープは CPU から読めないので、「CPU 専用のヒープで作っておいて、描く直前に `SHADER_VISIBLE` のヒープへコピーする」という使い方をします。

`NumDescriptors` 個ぶんを `SrcDescriptorRangeStart` から `DestDescriptorRangeStart` へコピーします。`DescriptorHeapsType` は両方のヒープの種類（同じでなければいけません）です。コピー元とコピー先の範囲は重なってはいけません。

範囲が飛び飛びのときは `CopyDescriptors`（範囲の配列を渡す版）を使います。

## パイプラインを作る

### CreateRootSignature {#createrootsignature}

```cpp
HRESULT ID3D12Device::CreateRootSignature(
    UINT nodeMask,
    const void* pBlobWithRootSignature,
    SIZE_T blobLengthInBytes,
    REFIID riid,
    void** ppvRootSignature);
```

ルート シグネチャ（シェーダーに渡す引数の型の定義）を作ります。

`pBlobWithRootSignature` と `blobLengthInBytes` には `D3D12SerializeRootSignature` が作ったバイト列（`ID3DBlob` の `GetBufferPointer()` と `GetBufferSize()`）を渡します。構造体をそのまま渡すのではなく、いったんシリアライズしたものを渡す点が見落としやすい所です。HLSL のシェーダーにルート シグネチャを埋め込んだ場合は、コンパイル済みシェーダーのバイト列をそのまま渡せます。

戻り値は成功なら `S_OK` です。`E_INVALIDARG` はバイト列がルート シグネチャとして読めないときです。

### CreateGraphicsPipelineState {#creategraphicspipelinestate}

```cpp
HRESULT ID3D12Device::CreateGraphicsPipelineState(
    const D3D12_GRAPHICS_PIPELINE_STATE_DESC* pDesc,
    REFIID riid,
    void** ppPipelineState);
```

描画のパイプライン（PSO）を作ります。シェーダー、ブレンド、ラスタライザー、深度の設定、入力レイアウト、レンダー ターゲットの形式など描画に必要な設定を 1 つにまとめた物です。

`pDesc` にすべてを書きます。何を書くかは [PSO](../pso.md) に一覧があります。作るのは重い処理でドライバーの内部でシェーダーが機械語に変換されます。実行時に作るとフレームが引っかかる原因になるので、ロード中に作っておきます。

`pDesc` の設定に矛盾があると `E_INVALIDARG` で失敗します。多い原因はルート シグネチャとシェーダーの食い違い入力レイアウトと頂点シェーダーの入力の食い違い、`RTVFormats` と `NumRenderTargets` の不一致です。デバッグ レイヤーを有効にしていれば、原因がメッセージで出ます。

### CreateComputePipelineState {#createcomputepipelinestate}

```cpp
HRESULT ID3D12Device::CreateComputePipelineState(
    const D3D12_COMPUTE_PIPELINE_STATE_DESC* pDesc,
    REFIID riid,
    void** ppPipelineState);
```

計算のパイプライン（PSO）を作ります。`pDesc` に必要なのはルート シグネチャとコンピュート シェーダーだけです。描画の PSO よりずっと簡単です。引数の意味と失敗の原因は `CreateGraphicsPipelineState` と同じです。

### CreateQueryHeap {#createqueryheap}

```cpp
HRESULT ID3D12Device::CreateQueryHeap(
    const D3D12_QUERY_HEAP_DESC* pDesc,
    REFIID riid,
    void** ppvHeap);
```

GPU の時刻や統計（タイムスタンプ、オクルージョン、パイプライン統計）を記録するクエリ ヒープを作ります。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pDesc` | `const D3D12_QUERY_HEAP_DESC*` | 種類（`Type`）、記録できる数（`Count`）、`NodeMask` |
| `riid` | `REFIID` | 取り出すインターフェースの ID。`ID3D12QueryHeap` |
| `ppvHeap` | `void**` | 結果を受け取るポインタのアドレス |

`Type` が何を記録するかを決めます。時刻を測るなら `D3D12_QUERY_HEAP_TYPE_TIMESTAMP` です。COPY のキューの時刻だけは別の種類 `COPY_QUEUE_TIMESTAMP` で、DIRECT と COMPUTE のキューの時刻とは混ぜられません。`Count` は、そのヒープに記録できる数です。1 フレームに記録する数に結果を読むまで待つフレーム数を掛けた分を確保します。`NodeMask` は GPU が 1 つなら 0 です。

`riid` と `ppvHeap` は `IID_PPV_ARGS(&query_heap)` でまとめて渡します。戻り値は成功なら `S_OK` で、`pDesc` の内容が不正だと失敗します。使い方（`EndQuery`、`ResolveQueryData`）は [ID3D12QueryHeap](id3d12queryheap.md) と [GPU Queries and Timing (D3D12)](../query-timing.md) にあります。

## 調べる・診断する

### GetCopyableFootprints {#getcopyablefootprints}

```cpp
void ID3D12Device::GetCopyableFootprints(
    const D3D12_RESOURCE_DESC* pResourceDesc,
    UINT FirstSubresource,
    UINT NumSubresources,
    UINT64 BaseOffset,
    D3D12_PLACED_SUBRESOURCE_FOOTPRINT* pLayouts,
    UINT* pNumRows,
    UINT64* pRowSizeInBytes,
    UINT64* pTotalBytes);
```

テクスチャをアップロード用のバッファから `CopyTextureRegion` でコピーするときバッファの中にどう並べればよいかを計算します。

テクスチャの 1 行の大きさ（幅 × 1 ピクセルの大きさ）は、そのままではコピーに使えず 1 行ごとに **256 バイト**の倍数にそろえる必要があります（`D3D12_TEXTURE_DATA_PITCH_ALIGNMENT`）。このそろえ方は `pLayouts` の `Footprint.RowPitch` として返ってきます。

出力は 4 つで各サブリソースの配置（`pLayouts`）、行数（`pNumRows`）、1 行の元のバイト数（`pRowSizeInBytes`）、全体の大きさ（`pTotalBytes`）です。`pTotalBytes` がアップロード用バッファの必要な大きさになります。使わない出力は `nullptr` で構いません。使い方の全体は [Texture Upload](../texture-upload.md) にあります。

### GetDeviceRemovedReason {#getdeviceremovedreason}

```cpp
HRESULT ID3D12Device::GetDeviceRemovedReason();
```

デバイスが「削除された」ときにその理由を返します。引数はありません。

GPU のハング、ドライバーの更新、GPU の取り外しなどでデバイスは突然使えなくなります。`Present` や `Signal` が `DXGI_ERROR_DEVICE_REMOVED` を返したら、このメソッドで理由を確認します。デバイスが無事なら `S_OK` を返します。

戻り値と主な意味は次のとおりです。

| 戻り値 | 意味 |
| --- | --- |
| `DXGI_ERROR_DEVICE_HUNG` | GPU が応答しなくなった。コマンドが無限に長いなど |
| `DXGI_ERROR_DEVICE_RESET` | GPU がリセットされた（不正なコマンドが原因のことが多い） |
| `DXGI_ERROR_DRIVER_INTERNAL_ERROR` | ドライバーの内部エラー |
| `DXGI_ERROR_DEVICE_REMOVED` | GPU が取り外されたドライバーが更新された |

消えたデバイスは二度と使えません。ゲームを終了するかデバイスとそれから作った物のすべてを作り直します。原因を調べるにはデバッグ レイヤーと DRED（Device Removed Extended Data）を使います（[Debug Layer](../debug-layer.md)）。

## 関連ページ

- [Device and Factory](../factory-device.md)
- [Heaps and Resources](../heaps-resources.md)
- [Descriptor Heap](../descriptor-heap.md)
- [Command Queue](../command-queue.md)
- [Microsoft Learn: ID3D12Device](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12device)
