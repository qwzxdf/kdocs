---
title: ID3D12GraphicsCommandList
tags:
  - DirectX
api:
  - ID3D12GraphicsCommandList
  - ID3D12CommandList
---

# ID3D12GraphicsCommandList

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

D3D12 では `Draw` を呼んだ瞬間に GPU が絵を描くわけではありません。描く命令はいったんコマンド リストに記録されて、あとでまとめて GPU に渡されます。記録する窓口になるのが `ID3D12GraphicsCommandList` でバリア、クリア、描画の設定、描画、コピーなど GPU にさせたいことはほとんどここから出します。

<svg class="fig flow" viewBox="0 0 720 190" role="img" aria-label="コマンド リストの記録から実行まで"><defs><marker id="fdE" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">記録して、閉じて、渡す</text><rect x="16" y="56" width="90" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="61.0" y="78.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">Reset</text><rect x="156" y="56" width="180" height="44" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="246.0" y="78.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">記録（Draw など）</text><rect x="386" y="56" width="90" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="431.0" y="78.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">Close</text><rect x="526" y="56" width="190" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="621.0" y="78.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">ExecuteCommandLists</text><line x1="106" y1="78" x2="156" y2="78" stroke="currentColor" stroke-width="2" marker-end="url(#fdE)"/><line x1="336" y1="78" x2="386" y2="78" stroke="currentColor" stroke-width="2" marker-end="url(#fdE)"/><line x1="476" y1="78" x2="526" y2="78" stroke="currentColor" stroke-width="2" marker-end="url(#fdE)"/><text x="246" y="126" text-anchor="middle" style="font-size:12px;font-weight:400">ここでは GPU は動かない（命令を書き込むだけ）</text><text x="621" y="126" text-anchor="middle" style="font-size:12px;font-weight:400">ここで GPU に渡る</text><text x="360" y="168" text-anchor="middle" style="font-size:12px;font-weight:400">Close のあとに記録するには、もう一度 Reset が必要（設定はすべて消える）</text></svg>

メソッドの多くは呼んだ時点では何も実行されず「あとでこうしてね」という命令がリストに書き込まれるだけです。そのため、ほとんどが `void` を返します。失敗は記録中には分からず `Close` の戻り値で、まとめて分かります。

!!! tip "ポイント"
    - 記録は `Reset` で始めて `Close` で終える。そのあと `ExecuteCommandLists` で GPU に渡す。
    - `Reset` のたびにビューポートやルート シグネチャなどすべての設定が消える。毎回、全部を設定し直す。
    - リソースの状態が変わるときは、必ず `ResourceBarrier` を入れる。
    - 記録中のエラーは `Close` の戻り値に出る。`Close` の戻り値を無視しない。
    - 1 つのリストを複数のスレッドから同時に記録してはいけない。

!!! info "このページを読む前に"
    コマンド リストの作り方は [Command List](../command-list.md)、記録したものを渡す窓口は [Command Queue](../command-queue.md)、アロケーターは [Command Allocator](../command-allocator.md) で説明しています。ルート シグネチャとディスクリプタは [Root Signature](../root-signature.md) と [Descriptor Heap](../descriptor-heap.md) を先に読むと、後半が分かりやすくなります。

## メソッド一覧

| メソッド | 役割 |
| --- | --- |
| [`Reset`](#reset) | 記録を始める |
| [`Close`](#close) | 記録を終える |
| [`ResourceBarrier`](#resourcebarrier) | リソースの状態を切り替える |
| [`ClearRenderTargetView`](#clearrendertargetview) | 描き込み先を塗りつぶす |
| [`ClearDepthStencilView`](#cleardepthstencilview) | 深度とステンシルを初期化する |
| [`OMSetRenderTargets`](#omsetrendertargets) | 描き込み先を決める |
| [`RSSetViewports`](#rssetviewports) | 画面上の描く範囲を決める |
| [`RSSetScissorRects`](#rssetscissorrects) | 描き込みを許す矩形を決める |
| [`SetPipelineState`](#setpipelinestate) | PSO を切り替える |
| [`SetGraphicsRootSignature`](#setgraphicsrootsignature) | 描画のルート シグネチャを決める |
| [`SetComputeRootSignature`](#setcomputerootsignature) | 計算のルート シグネチャを決める |
| [`SetDescriptorHeaps`](#setdescriptorheaps) | シェーダーから見えるヒープを決める |
| [`SetGraphicsRootDescriptorTable`](#setgraphicsrootdescriptortable) | 描画のルート引数にディスクリプタの表を渡す |
| [`SetComputeRootDescriptorTable`](#setcomputerootdescriptortable) | 計算のルート引数にディスクリプタの表を渡す |
| [`SetGraphicsRootConstantBufferView`](#setgraphicsrootconstantbufferview) | 描画のルート引数に定数バッファを直接渡す |
| [`SetGraphicsRoot32BitConstants`](#setgraphicsroot32bitconstants) | 描画のルート引数に小さな値を直接渡す |
| [`IASetPrimitiveTopology`](#iasetprimitivetopology) | 頂点のつなぎ方を決める |
| [`IASetVertexBuffers`](#iasetvertexbuffers) | 頂点バッファを結ぶ |
| [`IASetIndexBuffer`](#iasetindexbuffer) | インデックス バッファを結ぶ |
| [`DrawInstanced`](#drawinstanced) | 頂点で描く |
| [`DrawIndexedInstanced`](#drawindexedinstanced) | インデックスで描く |
| [`Dispatch`](#dispatch) | コンピュート シェーダーを走らせる |
| [`CopyBufferRegion`](#copybufferregion) | バッファの一部をコピーする |
| [`CopyTextureRegion`](#copytextureregion) | テクスチャへコピーする |
| [`BeginQuery`](#beginquery) | 計測を始める |
| [`EndQuery`](#endquery) | 計測を終える |
| [`ResolveQueryData`](#resolvequerydata) | 計測結果をバッファに書き出す |

## 記録の開始と終了

### Reset {#reset}

```cpp
HRESULT ID3D12GraphicsCommandList::Reset(
    ID3D12CommandAllocator* pAllocator,
    ID3D12PipelineState* pInitialState);
```

コマンド リストを記録できる状態に戻します。毎フレームの最初に呼びます。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pAllocator` | `ID3D12CommandAllocator*` | 命令の書き込み先。リストと同じ種類のもの |
| `pInitialState` | `ID3D12PipelineState*` | 最初の PSO。`nullptr` でよい |

`pAllocator` が大事です。GPU がまだそのアロケーターのメモリを読んでいる間は、同じアロケーターを `Reset` してはいけません。フェンスで「このフレームの GPU 処理は終わった」と確認してから、`ID3D12CommandAllocator::Reset` を呼びそのあとでリストを `Reset` します。順番を逆にするとリストの `Reset` が失敗します。

`pInitialState` に PSO を渡すと `SetPipelineState` を呼ばなくても、その PSO で始まります。最初の描画の PSO が決まっているならそれを渡せますが、あとから `SetPipelineState` で切り替えるなら `nullptr` で構いません。

`Reset` はリストの設定を全部消します。ビューポート、シザー矩形、ルート シグネチャ、PSO、ディスクリプタ ヒープ、レンダー ターゲットなどは前のフレームから引き継がれません。

戻り値は成功なら `S_OK` です。リストがまだ記録中（`Close` していない）のときやアロケーターが別のリストで記録中のときは、失敗します。

```cpp
allocator->Reset();                        // GPU が読み終わったあとにだけ
command_list->Reset(allocator.Get(), nullptr);
// ここから記録。ビューポートなどを毎回設定し直す
```

### Close {#close}

```cpp
HRESULT ID3D12GraphicsCommandList::Close();
```

記録を終えます。引数はありません。閉じたリストだけが `ExecuteCommandLists` で実行できます。

記録中に起きたエラー（バリアの状態が合わない、不正な引数など）は記録している間は何も言ってきません。`Close` を呼んだときにまとめて `HRESULT` で返ってきます。戻り値が失敗のときはそのリストを実行してはいけません。デバッグ レイヤーを有効にしておけば、原因が出力ウィンドウに出ます。

閉じたあとにもう一度記録するには `Reset` が必要です。`Close` を 2 回呼ぶこともできません。

## バリアとクリア

### ResourceBarrier {#resourcebarrier}

```cpp
void ID3D12GraphicsCommandList::ResourceBarrier(
    UINT NumBarriers,
    const D3D12_RESOURCE_BARRIER* pBarriers);
```

リソースの使い方（状態）が変わることを GPU に伝えます。たとえば、描き込み先として使っていたテクスチャを次はシェーダーで読むときに入れます。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `NumBarriers` | `UINT` | バリアの数 |
| `pBarriers` | `const D3D12_RESOURCE_BARRIER*` | バリアの配列 |

バリアには 3 つの種類があります。**遷移（Transition）** は、リソースの状態を `Before` から `After` へ切り替えます。一番よく使います。**UAV バリア**は同じ UAV に書いた結果を次の処理が読む前に書き込みの完了を待たせます。**エイリアシング バリア**は同じヒープの場所を共有する複数のリソースを、切り替えるときに使います。

遷移バリアの `Before` はリソースの今の状態と一致していなければなりません。一致していないとデバッグ レイヤーがエラーを出します。状態は自分で追いかけて覚えておくしかありません。フレームの最初と最後で状態がそろうように設計します（バックバッファなら `PRESENT` で始まって `PRESENT` で終わる）。

複数のバリアはまとめて 1 回の呼び出しで渡すほうが速くなります。`NumBarriers` を 2 以上にして配列で渡します。

```cpp
// バックバッファを、表示用から描き込み用に切り替える。
D3D12_RESOURCE_BARRIER barrier = MakeTransitionBarrier(
    back_buffer.Get(),
    D3D12_RESOURCE_STATE_PRESENT,        // 今の状態
    D3D12_RESOURCE_STATE_RENDER_TARGET); // 次の状態
command_list->ResourceBarrier(1, &barrier);
```

状態の一覧とバリアの詳しい使い方は [Resource Barrier](../resource-barrier.md) にあります。

### ClearRenderTargetView {#clearrendertargetview}

```cpp
void ID3D12GraphicsCommandList::ClearRenderTargetView(
    D3D12_CPU_DESCRIPTOR_HANDLE RenderTargetView,
    const FLOAT ColorRGBA[4],
    UINT NumRects,
    const D3D12_RECT* pRects);
```

描き込み先（レンダー ターゲット）を 1 色で塗りつぶします。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `RenderTargetView` | `D3D12_CPU_DESCRIPTOR_HANDLE` | 塗る対象の RTV |
| `ColorRGBA` | `const FLOAT[4]` | 色（R、G、B、A。0〜1） |
| `NumRects` | `UINT` | 塗る矩形の数。全体なら `0` |
| `pRects` | `const D3D12_RECT*` | 矩形の配列。全体なら `nullptr` |

`NumRects` を `0`、`pRects` を `nullptr` にするとビュー全体が塗られます。ほとんどはこの使い方です。

塗る前にそのリソースが `RENDER_TARGET` の状態になっている必要があります。また、`CreateCommittedResource` で `pOptimizedClearValue` に指定した色と同じ色で塗ると、GPU の高速なクリアが使えます。違う色で塗るとデバッグ レイヤーが警告を出します。動きはしますが遅くなります。

### ClearDepthStencilView {#cleardepthstencilview}

```cpp
void ID3D12GraphicsCommandList::ClearDepthStencilView(
    D3D12_CPU_DESCRIPTOR_HANDLE DepthStencilView,
    D3D12_CLEAR_FLAGS ClearFlags,
    FLOAT Depth,
    UINT8 Stencil,
    UINT NumRects,
    const D3D12_RECT* pRects);
```

深度とステンシルを初期化します。`ClearFlags` でどちらを塗るかを選びます。`D3D12_CLEAR_FLAG_DEPTH` は深度、`D3D12_CLEAR_FLAG_STENCIL` はステンシルで両方を `|` で並べることもできます。

`Depth` は 0〜1 の値で通常の深度（手前が小さい値）では `1.0f`（一番奥）で初期化します。リバース Z を使うときは `0.0f` です。`Stencil` は 0〜255 の整数です。矩形の指定は `ClearRenderTargetView` と同じです。

深度バッファは `DEPTH_WRITE` の状態になっている必要があります。

## 描画の設定

### OMSetRenderTargets {#omsetrendertargets}

```cpp
void ID3D12GraphicsCommandList::OMSetRenderTargets(
    UINT NumRenderTargetDescriptors,
    const D3D12_CPU_DESCRIPTOR_HANDLE* pRenderTargetDescriptors,
    BOOL RTsSingleHandleToDescriptorRange,
    const D3D12_CPU_DESCRIPTOR_HANDLE* pDepthStencilDescriptor);
```

これから描き込む先（レンダー ターゲットと深度バッファ）を決めます。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `NumRenderTargetDescriptors` | `UINT` | レンダー ターゲットの数（0〜8） |
| `pRenderTargetDescriptors` | `const D3D12_CPU_DESCRIPTOR_HANDLE*` | RTV のハンドル。数は上の引数と同じ |
| `RTsSingleHandleToDescriptorRange` | `BOOL` | ハンドルの渡し方（下で説明） |
| `pDepthStencilDescriptor` | `const D3D12_CPU_DESCRIPTOR_HANDLE*` | DSV のハンドルへのポインタ。深度を使わないなら `nullptr` |

`RTsSingleHandleToDescriptorRange` はハンドルの渡し方の選択です。`FALSE` なら `pRenderTargetDescriptors` は `NumRenderTargetDescriptors` 個のハンドルの配列です。`TRUE` なら先頭のハンドル 1 つだけを渡して、残りは「連続して並んだ RTV」として扱われます（ヒープの中で、続けて作った RTV にだけ使えます）。レンダー ターゲットが 1 つだけならどちらでも同じです。

`pDepthStencilDescriptor` はハンドルそのものではなく、**ハンドルへのポインタ**です。`&dsv_handle` のようにアドレスを渡します。値渡しで書いてしまうミスが多いので、気をつけます。

ここで決めたレンダー ターゲットの形式と数は、PSO の `RTVFormats`、`NumRenderTargets` と一致していなければなりません。

```cpp
command_list->OMSetRenderTargets(1, &rtv_handle, FALSE, &dsv_handle);
```

### RSSetViewports {#rssetviewports}

```cpp
void ID3D12GraphicsCommandList::RSSetViewports(
    UINT NumViewports,
    const D3D12_VIEWPORT* pViewports);
```

描く範囲（ビューポート）を画面上の位置と深度の範囲で決めます。`D3D12_VIEWPORT` に左上の `TopLeftX`、`TopLeftY`、大きさの `Width`、`Height`、深度の範囲の `MinDepth`、`MaxDepth` を入れます。ふつうは画面全体で `MinDepth = 0.0f`、`MaxDepth = 1.0f` です。

`Reset` のたびに設定が消えるので、毎フレーム呼びます。呼び忘れると何も描かれません（ビューポートの大きさが 0 のため）。ウィンドウの大きさが変わったときは新しい大きさで設定し直します。詳しくは [Viewport and Scissor](../viewport-scissor.md) にあります。

### RSSetScissorRects {#rssetscissorrects}

```cpp
void ID3D12GraphicsCommandList::RSSetScissorRects(
    UINT NumRects,
    const D3D12_RECT* pRects);
```

描き込みを許す矩形（シザー矩形）を決めます。この矩形の外にはピクセルが書き込まれません。`D3D12_RECT` の `left`、`top`、`right`、`bottom` をピクセル単位で書きます。

ビューポートと違ってシザー矩形は**常に有効**です。そのため、設定し忘れると矩形が 0 のままで、何も描かれません。ビューポートと同じ大きさ（画面全体）を毎フレーム設定するのが基本です。

### SetPipelineState {#setpipelinestate}

```cpp
void ID3D12GraphicsCommandList::SetPipelineState(
    ID3D12PipelineState* pPipelineState);
```

PSO（シェーダー、ブレンド、ラスタライザー、深度の設定をまとめた物）を切り替えます。以降の描画はこの PSO で行われます。

PSO の切り替えはそこそこ重い処理です。同じ PSO を使う描画をまとめて並べると、切り替えの回数を減らせます。PSO の形式は `OMSetRenderTargets` で決めたレンダー ターゲットと合っていなければなりません。

### SetGraphicsRootSignature {#setgraphicsrootsignature}

```cpp
void ID3D12GraphicsCommandList::SetGraphicsRootSignature(
    ID3D12RootSignature* pRootSignature);
```

描画に使うルート シグネチャを決めます。PSO を作ったときに使ったルート シグネチャと**同じ**ものを渡します。違うものを渡すと描画のときにエラーになります。

ルート シグネチャを切り替えると、それまで設定したルート引数（`SetGraphicsRootXxx` で渡したもの）は、すべて無効になります。切り替えたあとに必要な引数を設定し直します。

### SetComputeRootSignature {#setcomputerootsignature}

```cpp
void ID3D12GraphicsCommandList::SetComputeRootSignature(
    ID3D12RootSignature* pRootSignature);
```

計算（`Dispatch`）に使うルート シグネチャを決めます。意味は `SetGraphicsRootSignature` と同じで描画用とは別に覚えておく設定です。描画と計算で同じルート シグネチャを使っても、両方に別々に設定します。

### SetDescriptorHeaps {#setdescriptorheaps}

```cpp
void ID3D12GraphicsCommandList::SetDescriptorHeaps(
    UINT NumDescriptorHeaps,
    ID3D12DescriptorHeap* const* ppDescriptorHeaps);
```

シェーダーから見えるディスクリプタ ヒープをコマンド リストに結びつけます。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `NumDescriptorHeaps` | `UINT` | ヒープの数（最大 2） |
| `ppDescriptorHeaps` | `ID3D12DescriptorHeap* const*` | ヒープの配列 |

結びつけられるのは `SHADER_VISIBLE` の `CBV_SRV_UAV` ヒープ 1 つと `SAMPLER` ヒープ 1 つだけです。同じ種類のヒープを 2 つ渡すことはできません。RTV と DSV のヒープはシェーダーから見えないので、ここには渡しません。

ヒープを切り替えると GPU が内部で待ち（フラッシュ）を入れる場合があり、重くなります。1 フレームの間はできるだけ同じヒープを使い続けるように設計します。また、`SetGraphicsRootDescriptorTable` を呼ぶ**前**に設定しておく必要があります。

```cpp
ID3D12DescriptorHeap* heaps[] = {srv_heap.Get()};
command_list->SetDescriptorHeaps(1, heaps);
```

### SetGraphicsRootDescriptorTable {#setgraphicsrootdescriptortable}

```cpp
void ID3D12GraphicsCommandList::SetGraphicsRootDescriptorTable(
    UINT RootParameterIndex,
    D3D12_GPU_DESCRIPTOR_HANDLE BaseDescriptor);
```

ルート シグネチャのディスクリプタ テーブルの引数にヒープの中の位置を教えます。シェーダーはその位置から並んだディスクリプタをテクスチャや定数バッファとして読みます。

`RootParameterIndex` はルート シグネチャで何番目の引数かです（定義した順の番号）。`BaseDescriptor` はテーブルの先頭のディスクリプタの **GPU ハンドル**です。CPU ハンドルではない点に注意します（`GetGPUDescriptorHandleForHeapStart` に `Offset` で位置を足して作ります）。CPU ハンドルを渡すとクラッシュすることがあります。

結びつけるヒープは先に `SetDescriptorHeaps` で設定しておく必要があります。

### SetComputeRootDescriptorTable {#setcomputerootdescriptortable}

```cpp
void ID3D12GraphicsCommandList::SetComputeRootDescriptorTable(
    UINT RootParameterIndex,
    D3D12_GPU_DESCRIPTOR_HANDLE BaseDescriptor);
```

計算用のルート シグネチャのディスクリプタ テーブルの引数に位置を教えます。引数の意味は `SetGraphicsRootDescriptorTable` と同じです。コンピュート シェーダーに入力テクスチャ（SRV）や出力バッファ（UAV）を渡すときに使います。

### SetGraphicsRootConstantBufferView {#setgraphicsrootconstantbufferview}

```cpp
void ID3D12GraphicsCommandList::SetGraphicsRootConstantBufferView(
    UINT RootParameterIndex,
    D3D12_GPU_VIRTUAL_ADDRESS BufferLocation);
```

ルート シグネチャの CBV の引数に定数バッファを**ヒープを経由せずに**直接渡します。ディスクリプタを作る手間がなく、描画ごとに違う定数バッファを渡すのに向いています。

`BufferLocation` はバッファの GPU 仮想アドレスです。`resource->GetGPUVirtualAddress()` にバッファ内のオフセットを足して作ります。256 バイトにそろっていなければいけません。

### SetGraphicsRoot32BitConstants {#setgraphicsroot32bitconstants}

```cpp
void ID3D12GraphicsCommandList::SetGraphicsRoot32BitConstants(
    UINT RootParameterIndex,
    UINT Num32BitValuesToSet,
    const void* pSrcData,
    UINT DestOffsetIn32BitValues);
```

ルート シグネチャの 32 ビット定数の引数に小さな値を直接書き込みます。行列 1 つ分（16 個）程度までの小さなデータを定数バッファなしで渡せます。

`Num32BitValuesToSet` は書き込む 32 ビット値の個数です（`float` や `uint` を何個書くか）。バイト数ではありません。`DestOffsetIn32BitValues` は引数の中の書き始める位置です（ふつうは `0`）。

値はコマンド リストに記録された時点の内容が使われます。描画ごとに値を変えても前の描画には影響しません。ただし、ルート シグネチャ全体の大きさには上限（64 ワード = 256 バイト）があるので、多く使いすぎないようにします。

## 頂点の入力と描画

### IASetPrimitiveTopology {#iasetprimitivetopology}

```cpp
void ID3D12GraphicsCommandList::IASetPrimitiveTopology(
    D3D12_PRIMITIVE_TOPOLOGY PrimitiveTopology);
```

頂点をどうつないで三角形などを作るかを決めます。三角形を並べて描くなら `D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST` です（3 つの頂点ごとに 1 枚の三角形）。ほかに線（`LINELIST`）、点（`POINTLIST`）、三角形の帯（`TRIANGLESTRIP`）があります。

PSO の `PrimitiveTopologyType`（`TRIANGLE` など）と種類が合っていなければなりません。PSO は大きな分類（三角形か線か点か）を決めここで、その中の細かいつなぎ方を決めます。

### IASetVertexBuffers {#iasetvertexbuffers}

```cpp
void ID3D12GraphicsCommandList::IASetVertexBuffers(
    UINT StartSlot,
    UINT NumViews,
    const D3D12_VERTEX_BUFFER_VIEW* pViews);
```

頂点バッファを描画に結びつけます。

`StartSlot` は最初に結ぶスロットの番号で、入力レイアウトの `InputSlot` と対応します。`NumViews` は続けて結ぶバッファの数です。`pViews` は `D3D12_VERTEX_BUFFER_VIEW` の配列で各要素にバッファの GPU アドレス（`BufferLocation`）、全体の大きさ（`SizeInBytes`）、頂点 1 つの大きさ（`StrideInBytes`）を入れます。

`StrideInBytes` が頂点の構造体の大きさと合っていないと頂点の読み取りがずれて、絵が壊れます。`SizeInBytes` を頂点の数ではなくバイト数で書くことも間違えやすい所です。

### IASetIndexBuffer {#iasetindexbuffer}

```cpp
void ID3D12GraphicsCommandList::IASetIndexBuffer(
    const D3D12_INDEX_BUFFER_VIEW* pView);
```

インデックス バッファを結びつけます。`D3D12_INDEX_BUFFER_VIEW` に `BufferLocation`、`SizeInBytes`、`Format`（`DXGI_FORMAT_R16_UINT` か `DXGI_FORMAT_R32_UINT`）を入れます。

`Format` が実際のインデックスの大きさ（`uint16_t` か `uint32_t`）と合っていないと描画が壊れます。頂点が 65,536 個を超えるメッシュは、32 ビットにします。インデックスを使わない描画のときは呼ぶ必要がありません。

### DrawInstanced {#drawinstanced}

```cpp
void ID3D12GraphicsCommandList::DrawInstanced(
    UINT VertexCountPerInstance,
    UINT InstanceCount,
    UINT StartVertexLocation,
    UINT StartInstanceLocation);
```

頂点バッファの頂点を順に読んで描きます。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `VertexCountPerInstance` | `UINT` | 1 インスタンスあたりの頂点の数 |
| `InstanceCount` | `UINT` | インスタンスの数。1 つだけなら `1` |
| `StartVertexLocation` | `UINT` | 読み始める頂点の位置 |
| `StartInstanceLocation` | `UINT` | インスタンス ID の開始値 |

三角形 1 枚なら `DrawInstanced(3, 1, 0, 0)` です。インスタンスは同じメッシュを位置だけ変えて何回も描く仕組みで、`InstanceCount` を増やすと `SV_InstanceID` が 0、1、2…と変わりながら同じ頂点が何度も流れます。インスタンスの数が 1 のときは引数の意味を気にする必要はありません。

### DrawIndexedInstanced {#drawindexedinstanced}

```cpp
void ID3D12GraphicsCommandList::DrawIndexedInstanced(
    UINT IndexCountPerInstance,
    UINT InstanceCount,
    UINT StartIndexLocation,
    INT BaseVertexLocation,
    UINT StartInstanceLocation);
```

インデックス バッファの順に頂点を読んで描きます。頂点を共有できるのでメッシュの描画は、ほぼこちらです。

`IndexCountPerInstance` はインデックスの数（三角形の数 × 3）、`StartIndexLocation` は読み始めるインデックスの位置です。`BaseVertexLocation` はインデックスが指す頂点の番号に**足される値**で、負の値も使えます。1 つの大きな頂点バッファに複数のメッシュを並べたときメッシュごとの頂点の開始位置を、ここで指定します。

インデックス バッファは先に `IASetIndexBuffer` で結んでおく必要があります。

## 計算とコピー

### Dispatch {#dispatch}

```cpp
void ID3D12GraphicsCommandList::Dispatch(
    UINT ThreadGroupCountX,
    UINT ThreadGroupCountY,
    UINT ThreadGroupCountZ);
```

コンピュート シェーダーを走らせます。引数はスレッド グループの数を X、Y、Z の 3 方向で指定します。

走るスレッドの総数は `グループ数 × シェーダーの [numthreads(x, y, z)]` です。たとえば、1920×1080 の画像を `numthreads(8, 8, 1)` で処理するなら `Dispatch(240, 135, 1)` です。割り切れない大きさのときは切り上げた数を渡して、シェーダーの中で範囲外のスレッドを捨てます。1 方向のグループ数は最大 65,535 です。

事前に `SetPipelineState` で計算用の PSO、`SetComputeRootSignature` で計算用のルート シグネチャを設定しておく必要があります。詳しくは [Compute Shader](../compute-shader.md) にあります。

### CopyBufferRegion {#copybufferregion}

```cpp
void ID3D12GraphicsCommandList::CopyBufferRegion(
    ID3D12Resource* pDstBuffer,
    UINT64 DstOffset,
    ID3D12Resource* pSrcBuffer,
    UINT64 SrcOffset,
    UINT64 NumBytes);
```

バッファの一部を別のバッファへコピーします。UPLOAD ヒープに書いたデータを DEFAULT ヒープのバッファへ移すときに使います。

コピー先は `COPY_DEST`、コピー元は `COPY_SOURCE` の状態にします。UPLOAD ヒープのバッファは最初から `GENERIC_READ` で、これはコピー元として使えるので、バリアは要りません。`NumBytes` はバイト数で要素の数ではありません。

### CopyTextureRegion {#copytextureregion}

```cpp
void ID3D12GraphicsCommandList::CopyTextureRegion(
    const D3D12_TEXTURE_COPY_LOCATION* pDst,
    UINT DstX,
    UINT DstY,
    UINT DstZ,
    const D3D12_TEXTURE_COPY_LOCATION* pSrc,
    const D3D12_BOX* pSrcBox);
```

テクスチャへまたはテクスチャから、コピーします。アップロード用のバッファから、DEFAULT のテクスチャへ画像を移すときに使います。

`pDst` と `pSrc` は `D3D12_TEXTURE_COPY_LOCATION` で「どのリソースのどのサブリソースか」（`SUBRESOURCE_INDEX`）、または「バッファの中のどんな配置か」（`PLACED_FOOTPRINT`）を示します。バッファからテクスチャへコピーするときは、コピー元が `PLACED_FOOTPRINT`、コピー先が `SUBRESOURCE_INDEX` です。`PLACED_FOOTPRINT` の配置は `GetCopyableFootprints` で計算します。`DstX`、`DstY`、`DstZ` はコピー先の中の位置、`pSrcBox` はコピー元の範囲で全体なら `nullptr` です。

コピー先は `COPY_DEST` の状態にします。使い方の全体は [Texture Upload](../texture-upload.md) にあります。

## 計測

### BeginQuery {#beginquery}

```cpp
void ID3D12GraphicsCommandList::BeginQuery(
    ID3D12QueryHeap* pQueryHeap,
    D3D12_QUERY_TYPE Type,
    UINT Index);
```

オクルージョン クエリ（描かれたピクセルの数）などの区間の計測を始めます。`pQueryHeap` は計測結果を置く場所、`Type` は計測の種類（`D3D12_QUERY_TYPE_BINARY_OCCLUSION` など）、`Index` はヒープの中の何番目に結果を置くかです。`EndQuery` と対にして使います。

タイムスタンプ（`D3D12_QUERY_TYPE_TIMESTAMP`）は時点を測るもので、区間ではありません。`BeginQuery` は使えず `EndQuery` だけを使います。

### EndQuery {#endquery}

```cpp
void ID3D12GraphicsCommandList::EndQuery(
    ID3D12QueryHeap* pQueryHeap,
    D3D12_QUERY_TYPE Type,
    UINT Index);
```

区間の計測を終えます。タイムスタンプのときはこの呼び出しの時点の GPU の時刻を `Index` の場所に書き込みます。引数の意味は `BeginQuery` と同じです。

GPU の処理時間を測るには測りたい処理の前と後で `EndQuery` を 1 回ずつ呼び、2 つの時刻の差を `ID3D12CommandQueue::GetTimestampFrequency` で得た周波数で割ります。結果をバッファへ取り出すのが、次の `ResolveQueryData` です。詳しくは [GPU Queries and Timing](../query-timing.md) にあります。

### ResolveQueryData {#resolvequerydata}

```cpp
void ID3D12GraphicsCommandList::ResolveQueryData(
    ID3D12QueryHeap* pQueryHeap,
    D3D12_QUERY_TYPE Type,
    UINT StartIndex,
    UINT NumQueries,
    ID3D12Resource* pDestinationBuffer,
    UINT64 AlignedDestinationBufferOffset);
```

クエリの結果をバッファに書き出します。クエリのヒープは CPU から直接は読めないので、いったん READBACK ヒープのバッファへ書き出して、CPU から `Map` で読みます。

`StartIndex` と `NumQueries` は書き出すクエリの範囲です。`AlignedDestinationBufferOffset` は書き込み先の位置で**8 バイトの倍数**にします。書き込み先のバッファは `COPY_DEST` の状態にしておきます。結果は `UINT64` が 1 つずつ並びます。

## 関連ページ

- [Command List](../command-list.md)
- [Command Queue](../command-queue.md)
- [Resource Barrier](../resource-barrier.md)
- [ID3D12Device](id3d12device.md)
- [Microsoft Learn: ID3D12GraphicsCommandList](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12graphicscommandlist)
