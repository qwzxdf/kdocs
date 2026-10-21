---
title: Swap Chain (D3D12)
tags:
  - DirectX
---

# Swap Chain (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

画面に出す絵をそのまま 1 枚の画像に描いていくと描いている途中の半端な絵が見えてしまいます。そこで、画面に出す画像（バック バッファ）を複数用意して、1 枚を表示している間に別の 1 枚へ次の絵を描き描き終えたら入れ替えます。この仕組みが<strong>スワップ チェーン</strong>です。

D3D12 のスワップ チェーンはコマンド キューに結びつけて作ります。バック バッファは別々の `ID3D12Resource` として見えます。今どのバッファへ描くかは自分で管理し、描く前後にバリアでリソースの状態を切り替えます。

!!! tip "ポイント"
    - スワップ チェーンはデバイスではなく DIRECT のコマンド キューを渡して作る（`CreateSwapChainForHwnd`）。
    - バッファの数は 2 か 3 で、フリップ モデル（`FLIP_DISCARD`）が必須。
    - 今の描き先は `GetCurrentBackBufferIndex()` で取る。
    - バッファごとに RTV を作りディスクリプタ ヒープに並べる。
    - 描く前に `PRESENT` から `RENDER_TARGET` へ描いたあとに `RENDER_TARGET` から `PRESENT` へバリアで切り替える。
    - `_SRGB` の形式はスワップ チェーンに指定できない。`UNORM` で作って RTV を `_SRGB` で作る。

!!! info "このページを読む前に"
    バック バッファに描くための RTV は、[Descriptor Heap](descriptor-heap.md) と [Descriptor](descriptor.md) で説明しています。状態の切り替えは [Resource Barrier](resource-barrier.md)、キューは [Command Queue](command-queue.md) が基本です。ウィンドウの作り方は [Win32 Window and Message Loop](window.md) を参照してください。

## 作る

スワップ チェーンは DXGI のファクトリー（[Device and Factory](factory-device.md)）で作ります。D3D12 では `Present` がそのキューの仕事のあとに実行されるようにデバイスではなくキューを渡します。

```cpp
DXGI_SWAP_CHAIN_DESC1 desc = {};
desc.Width = width;
desc.Height = height;
desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;         // フリップ モデルは _SRGB を指定できない
desc.SampleDesc.Count = 1;                        // フリップ モデルは MSAA 不可
desc.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
desc.BufferCount = kFrameCount;                   // 2 か 3
desc.SwapEffect = DXGI_SWAP_EFFECT_FLIP_DISCARD;  // D3D12 はフリップ モデルが必須
desc.Scaling = DXGI_SCALING_STRETCH;
desc.AlphaMode = DXGI_ALPHA_MODE_IGNORE;
desc.Flags = 0;

ComPtr<IDXGISwapChain1> swap_chain1;
factory->CreateSwapChainForHwnd(command_queue.Get(),  // デバイスではなく、DIRECT のコマンド キュー
                                hwnd, &desc, nullptr, nullptr, &swap_chain1);
factory->MakeWindowAssociation(hwnd, DXGI_MWA_NO_ALT_ENTER);

ComPtr<IDXGISwapChain3> swap_chain;  // GetCurrentBackBufferIndex を持つ版
swap_chain1.As(&swap_chain);
```

`D3D12` ではスワップ チェーンの形式に制限があります。`Format` に `_SRGB` を指定できないのは、フリップ モデルの決まりです。リニアの値を書いたとき sRGB に自動変換してほしいならバック バッファは `R8G8B8A8_UNORM` で作り、あとで作る RTV のほうを `R8G8B8A8_UNORM_SRGB` にします。

`BufferCount` はバック バッファの数です。2 枚（ダブル バッファ）か 3 枚（トリプル バッファ）にします。3 枚のほうが GPU の待ちが減って滑らかになりやすい一方、入力から表示までの遅れが少し増えます。

`SwapEffect` は `FLIP_DISCARD` が標準です。表示が終わったバッファの中身は捨てられます。前の絵を残したいときは `FLIP_SEQUENTIAL` を使います。`Flags` にはティアリングを許す `ALLOW_TEARING` や描画の遅れを減らす `FRAME_LATENCY_WAITABLE_OBJECT` を指定できます。

## バック バッファのリソースと RTV を作る

D3D12 のバック バッファは `GetBuffer(0)`、`GetBuffer(1)` のように別々のリソースとして取り出します。それぞれに RTV を作って、ヒープに並べます。

```cpp
// 1. RTV 用のディスクリプタ ヒープ（バック バッファの数だけ）。
D3D12_DESCRIPTOR_HEAP_DESC heap_desc = {};
heap_desc.NumDescriptors = kFrameCount;
heap_desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_RTV;
heap_desc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_NONE;  // RTV はシェーダーから見えない
device->CreateDescriptorHeap(&heap_desc, IID_PPV_ARGS(&rtv_heap));
rtv_descriptor_size = device->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_RTV);

// 2. 各バック バッファを取り出して、RTV を作る。
D3D12_CPU_DESCRIPTOR_HANDLE rtv_start = rtv_heap->GetCPUDescriptorHandleForHeapStart();
for (UINT i = 0; i < kFrameCount; ++i) {
  swap_chain->GetBuffer(i, IID_PPV_ARGS(&back_buffers[i]));  // i 番目のバック バッファ
  D3D12_RENDER_TARGET_VIEW_DESC rtv_desc = {};
  rtv_desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;  // 書くときに、リニアから sRGB へ自動変換する
  rtv_desc.ViewDimension = D3D12_RTV_DIMENSION_TEXTURE2D;
  device->CreateRenderTargetView(back_buffers[i].Get(), &rtv_desc,
                                 OffsetHandle(rtv_start, i, rtv_descriptor_size));
}
```

ヒープの作り方とハンドルの求め方（`OffsetHandle`）は、[Descriptor Heap](descriptor-heap.md) と [Helper Functions](util.md#offsethandle) にあります。`CreateRenderTargetView` の引数は [ID3D12Device](api/id3d12device.md#createrendertargetview) にまとめています。

## バック バッファの交代

<svg class="fig flow" viewBox="0 0 720 232" role="img" aria-label="スワップ チェーンのバック バッファは、交代で使う"><defs><marker id="sw" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">バック バッファの交代</text><rect x="20" y="60" width="200" height="44" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="120.0" y="82.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">バック バッファ 0</text><text x="120" y="126" text-anchor="middle" style="font-size:12px;font-weight:400">画面に表示中</text><rect x="252" y="60" width="200" height="44" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="352.0" y="82.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">バック バッファ 1</text><text x="352" y="126" text-anchor="middle" style="font-size:12px;font-weight:400">次に描く（index = 1）</text><rect x="484" y="60" width="200" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="584.0" y="82.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">バック バッファ 2</text><text x="584" y="126" text-anchor="middle" style="font-size:12px;font-weight:400">待機中</text><line x1="150" y1="150" x2="252" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#sw)"/><line x1="380" y1="150" x2="484" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#sw)"/><text x="360" y="190" text-anchor="middle" style="font-size:12px;font-weight:400">Present のたびに、描く先の番号が 1 つ進む（BufferCount で一周する）。</text><text x="360" y="210" text-anchor="middle" style="font-size:12px;font-weight:400">番号は、自分で数えず GetCurrentBackBufferIndex() で取る。</text></svg>

フリップ モデルでは `Present` のたびにバック バッファの役割が入れ替わります。今のフレームで描くバッファの番号は `GetCurrentBackBufferIndex()` で取ります。自分で `+1` して数えるより確実です。最初のフレームは 0 で `Present` のあとは、次の番号（1、2、0、1…）になります。

## 毎フレームの骨格

1 フレームの描画はバリア、描き先の設定、描画、バリア、`Present` の順です。

```cpp
void RenderFrame() {
  const UINT index = swap_chain->GetCurrentBackBufferIndex();  // 今描くバック バッファの番号

  // 1. アロケーターとリストを Reset する（GPU の完了を確認したあと）。
  allocators[index]->Reset();
  command_list->Reset(allocators[index].Get(), nullptr);

  // 2. バック バッファを PRESENT から RENDER_TARGET へ切り替える。
  D3D12_RESOURCE_BARRIER to_render = MakeTransitionBarrier(
      back_buffers[index].Get(), D3D12_RESOURCE_STATE_PRESENT, D3D12_RESOURCE_STATE_RENDER_TARGET);
  command_list->ResourceBarrier(1, &to_render);

  // 3. 描き先を設定して、クリアして、描画する。
  D3D12_CPU_DESCRIPTOR_HANDLE rtv = OffsetHandle(rtv_heap->GetCPUDescriptorHandleForHeapStart(), index, rtv_descriptor_size);
  command_list->OMSetRenderTargets(1, &rtv, FALSE, nullptr);
  const float clear_color[4] = {0.1f, 0.15f, 0.3f, 1.0f};
  command_list->ClearRenderTargetView(rtv, clear_color, 0, nullptr);
  // ... 描画 ...

  // 4. RENDER_TARGET から PRESENT へ戻す。
  D3D12_RESOURCE_BARRIER to_present = MakeTransitionBarrier(
      back_buffers[index].Get(), D3D12_RESOURCE_STATE_RENDER_TARGET, D3D12_RESOURCE_STATE_PRESENT);
  command_list->ResourceBarrier(1, &to_present);

  command_list->Close();
  ID3D12CommandList* lists[] = {command_list.Get()};
  command_queue->ExecuteCommandLists(1, lists);

  // 5. 画面に出す。
  swap_chain->Present(1, 0);
  // 6. フェンスに Signal する（Fence のページを参照）。
}
```

描く前にバリアで `PRESENT` から `RENDER_TARGET` に切り替え描いたあとで `PRESENT` に戻すのは、決まりです。バリアを忘れるとデバッグ レイヤーがエラーを出し、画面が乱れます（[Resource Barrier](resource-barrier.md)）。

## Present

```cpp
HRESULT hr = swap_chain->Present(1, 0);
if (hr == DXGI_ERROR_DEVICE_REMOVED || hr == DXGI_ERROR_DEVICE_RESET) {
  HRESULT reason = device->GetDeviceRemovedReason();  // 原因（GPU のハング、ドライバーの更新、取り外し）
}
```

`Present` の第 1 引数は垂直同期を待つ回数です。`Present(1, 0)` は画面の更新に合わせて表示します。`Present(0, DXGI_PRESENT_ALLOW_TEARING)` は待たずに表示できティアリング（画面のずれ）を許します。スワップ チェーンを作るときに `ALLOW_TEARING` を付けておく必要があります。

戻り値が `DXGI_ERROR_DEVICE_REMOVED` のときはデバイスが失われています。理由は `GetDeviceRemovedReason` で調べます（[ID3D12Device](api/id3d12device.md#getdeviceremovedreason)）。

## ウィンドウの大きさを変える

ウィンドウの大きさが変わったら、バック バッファを作り直します。GPU がまだバック バッファを使っているときは、解放も作り直しもできません。

```cpp
void OnResize(UINT width, UINT height) {
  WaitForGpu();                                      // GPU がバック バッファを使い終わるのを待つ
  for (auto& buffer : back_buffers) buffer.Reset();  // バック バッファへの参照をすべて解放する
  swap_chain->ResizeBuffers(kFrameCount, width, height, DXGI_FORMAT_UNKNOWN, 0);
  // GetBuffer と CreateRenderTargetView をやり直す
}
```

`ResizeBuffers` はバック バッファへの参照が 1 つでも残っていると失敗します。`ComPtr` をすべて `Reset` してから呼びます。フェンスで待つ方法は [Fence](fence.md) にあります。

## よくあるミス

??? failure "`CreateSwapChainForHwnd` が失敗する"
    デバイスを渡しています。D3D12 ではコマンド キューを渡します。`_SRGB` の形式、MSAA、ビット ブリット モデルの `SwapEffect` も失敗の原因になります。

??? failure "画面が乱れる、何も描かれない（バリア）"
    `PRESENT` と `RENDER_TARGET` の切り替えを入れていないか前後が逆です。デバッグ レイヤーのメッセージを見ます。

??? failure "`ResizeBuffers` が失敗する"
    バック バッファへの参照（`ComPtr`）が残っているか GPU がまだ使っています。すべて解放してフェンスで待ってから呼びます。

??? failure "色が暗い（または明るい）"
    リニアの値を `UNORM` の RTV に書いています。RTV を `_SRGB` で作ります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] D3D12 のスワップ チェーンは、コマンド キューを渡して作る
    - [x] フリップ モデル（`FLIP_DISCARD`）で 2〜3 枚。`_SRGB` は RTV に付ける
    - [x] バック バッファは別々のリソース。それぞれに RTV を作る
    - [x] 今の描き先は `GetCurrentBackBufferIndex()`
    - [x] 描く前後にバリアで `PRESENT` と `RENDER_TARGET` を切り替える
    - [x] 大きさを変える前に GPU の完了を待つ

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Descriptor Heap](descriptor-heap.md)
- [Resource Barrier](resource-barrier.md)
- [Fence](fence.md)
- [Helper Functions](util.md)
- [Microsoft Learn: DXGI スワップ チェーン](https://learn.microsoft.com/ja-jp/windows/win32/direct3ddxgi/d3d10-graphics-programming-guide-dxgi)
