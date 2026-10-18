---
title: Swap Chain (D3D12)
tags:
  - DirectX
---

# Swap Chain (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>スワップ チェーン</strong>は画面に出す画像（バック バッファ）を交代で使う仕組みです。D3D12 では <strong>コマンド キュー</strong>に結びつけて作りバック バッファが、<strong>複数のリソース</strong>として見えます。今、どのバッファに描くかを自分で管理し、描く前後で <strong>リソースの状態</strong>（`PRESENT` ↔ `RENDER_TARGET`）をバリアで切り替えます。

!!! tip "ポイント"
    - スワップ チェーンは <strong>DIRECT コマンド キュー</strong>を渡して、作る（`CreateSwapChainForHwnd(command_queue, …)`）。
    - バッファの数は 2 か 3。フリップ モデル（`FLIP_DISCARD`）が必須。
    - 今の描き先は `GetCurrentBackBufferIndex()` で取る。
    - 各バッファに RTV を作って、ディスクリプタ ヒープに並べる。
    - 描く前に `PRESENT` → `RENDER_TARGET`、描いた後に `RENDER_TARGET` → `PRESENT` のバリア。
    - `_SRGB` はスワップ チェーンに指定できない。`UNORM` で作り RTV を `_SRGB` で作る。

## 作る

```cpp
DXGI_SWAP_CHAIN_DESC1 desc = {};
desc.Width = width;
desc.Height = height;
desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;                    // フリップ モデルは、_SRGB を、指定できない
desc.SampleDesc.Count = 1;                                   // フリップ モデルは、MSAA 不可
desc.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
desc.BufferCount = kFrameCount;                              // 2 か 3
desc.SwapEffect = DXGI_SWAP_EFFECT_FLIP_DISCARD;             // D3D12 は、フリップ モデルが、必須
desc.Scaling = DXGI_SCALING_STRETCH;
desc.AlphaMode = DXGI_ALPHA_MODE_IGNORE;
desc.Flags = 0;

ComPtr<IDXGISwapChain1> swap_chain1;
factory->CreateSwapChainForHwnd(command_queue.Get(),         // デバイスではなく、DIRECT コマンド キュー
                                hwnd, &desc, nullptr, nullptr, &swap_chain1);
factory->MakeWindowAssociation(hwnd, DXGI_MWA_NO_ALT_ENTER);

ComPtr<IDXGISwapChain3> swap_chain;                          // GetCurrentBackBufferIndex を持つ版
swap_chain1.As(&swap_chain);
```

| メンバー | 内容 |
| --- | --- |
| `BufferCount` | バック バッファの数。2（ダブル）か 3（トリプル） |
| `SwapEffect` | `FLIP_DISCARD`（標準）、`FLIP_SEQUENTIAL`。D3D12 はフリップ モデルだけ |
| `Format` | `R8G8B8A8_UNORM`。HDR は `R16G16B16A16_FLOAT` |
| `Flags` | `ALLOW_TEARING`、`FRAME_LATENCY_WAITABLE_OBJECT` |

D3D12 のスワップ チェーンは <strong>デバイスではなくコマンド キュー</strong>を、渡します。`Present` がそのキューの仕事の後に実行されるためです。

## バック バッファのリソースと RTV

```cpp
// ① RTV 用のディスクリプタ ヒープ（バック バッファの数だけ）。
D3D12_DESCRIPTOR_HEAP_DESC heap_desc = {};
heap_desc.NumDescriptors = kFrameCount;
heap_desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_RTV;
heap_desc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_NONE;           // RTV は、シェーダーから見えない
device->CreateDescriptorHeap(&heap_desc, IID_PPV_ARGS(&rtv_heap));
rtv_descriptor_size = device->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_RTV);

// ② 各バック バッファを取り出して、RTV を作る。
CD3DX12_CPU_DESCRIPTOR_HANDLE handle(rtv_heap->GetCPUDescriptorHandleForHeapStart());
for (UINT i = 0; i < kFrameCount; ++i) {
  swap_chain->GetBuffer(i, IID_PPV_ARGS(&back_buffers[i]));  // i 番目のバック バッファ（ID3D12Resource）
  D3D12_RENDER_TARGET_VIEW_DESC rtv_desc = {};
  rtv_desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;         // 書くときに、リニア → sRGB へ、自動変換
  rtv_desc.ViewDimension = D3D12_RTV_DIMENSION_TEXTURE2D;
  device->CreateRenderTargetView(back_buffers[i].Get(), &rtv_desc, handle);
  handle.Offset(1, rtv_descriptor_size);                     // 次のスロットへ
}
```

D3D12 ではバック バッファは <strong>複数の別々のリソース</strong>として、見えます（`GetBuffer(0)`、`GetBuffer(1)`…）。各々に RTV を作りヒープに並べます。ディスクリプタ ヒープとハンドルの詳細は、[Descriptor Heap](descriptor-heap.md) と [Descriptor](descriptor.md) です。

## 毎フレームの骨格

```cpp
void RenderFrame() {
  const UINT index = swap_chain->GetCurrentBackBufferIndex();   // 今、描くべき、バック バッファの番号

  // ① アロケーターとリストを、Reset（GPU の、完了確認の後）
  allocators[index]->Reset();
  command_list->Reset(allocators[index].Get(), nullptr);

  // ② バック バッファを、PRESENT → RENDER_TARGET に、切り替える（バリア）
  auto to_render = CD3DX12_RESOURCE_BARRIER::Transition(back_buffers[index].Get(), D3D12_RESOURCE_STATE_PRESENT,
                                                        D3D12_RESOURCE_STATE_RENDER_TARGET);
  command_list->ResourceBarrier(1, &to_render);

  // ③ 描き先を設定して、クリア、描画
  CD3DX12_CPU_DESCRIPTOR_HANDLE rtv(rtv_heap->GetCPUDescriptorHandleForHeapStart(), index, rtv_descriptor_size);
  command_list->OMSetRenderTargets(1, &rtv, FALSE, nullptr);
  const float clear_color[4] = {0.1f, 0.15f, 0.3f, 1.0f};
  command_list->ClearRenderTargetView(rtv, clear_color, 0, nullptr);
  // ... 描画 ...

  // ④ RENDER_TARGET → PRESENT に戻す
  auto to_present = CD3DX12_RESOURCE_BARRIER::Transition(back_buffers[index].Get(), D3D12_RESOURCE_STATE_RENDER_TARGET,
                                                         D3D12_RESOURCE_STATE_PRESENT);
  command_list->ResourceBarrier(1, &to_present);

  command_list->Close();
  ID3D12CommandList* lists[] = {command_list.Get()};
  command_queue->ExecuteCommandLists(1, lists);

  // ⑤ 画面に出す
  swap_chain->Present(1, 0);
  // ⑥ フェンスに Signal（fence.md）
}
```

<strong>描く前にバリアで `PRESENT` から `RENDER_TARGET` に</strong>、<strong>描いた後に `PRESENT` に戻す</strong>のが、決まりです。バリアを忘れるとデバッグ レイヤーが、エラーを出し画面が乱れます（[Resource Barrier](resource-barrier.md)）。

## GetCurrentBackBufferIndex

フリップ モデルでは `Present` のたびにバック バッファが入れ替わります。<strong>今フレームで描くべきバッファの番号</strong>は `GetCurrentBackBufferIndex()` で、取ります（自分で `+1` して数えるより確実です）。

| 時点 | `GetCurrentBackBufferIndex()` |
| --- | --- |
| 最初のフレーム | 0 |
| `Present` の後 | 次のバッファ（1、2、0、1、…。`BufferCount` で循環） |

## Present

```cpp
HRESULT hr = swap_chain->Present(1, 0);
if (hr == DXGI_ERROR_DEVICE_REMOVED || hr == DXGI_ERROR_DEVICE_RESET) {
  HRESULT reason = device->GetDeviceRemovedReason();         // 原因（GPU のハング、ドライバー更新、取り外し）
}
```

`Present(1, 0)` は垂直同期を待ちます。`Present(0, DXGI_PRESENT_ALLOW_TEARING)` で待たずに表示できます（スワップ チェーンの作成時に `ALLOW_TEARING` が、必要）。

## 大きさの変更

```cpp
void OnResize(UINT width, UINT height) {
  WaitForGpu();                                              // GPU が、バック バッファを、使い終わるのを、待つ
  for (auto& buffer : back_buffers) buffer.Reset();          // バック バッファへの、参照を、すべて、解放する
  swap_chain->ResizeBuffers(kFrameCount, width, height, DXGI_FORMAT_UNKNOWN, 0);
  // GetBuffer と、CreateRenderTargetView を、やり直す
}
```

バック バッファを GPU がまだ使っている間は解放・作り直しが、できません。フェンスで完了を待ってから行います（[Fence](fence.md)）。

## よくあるミス

??? failure "`CreateSwapChainForHwnd` が、失敗する"
    デバイスを渡している（D3D12 は、コマンド キューを渡す）。`_SRGB` や MSAA、`SwapEffect` がビット ブリット モデルになっている。

??? failure "画面が乱れる、描かれない（バリア）"
    `PRESENT` ↔ `RENDER_TARGET` のバリアを入れていないまたは前後が逆。デバッグ レイヤーのメッセージを見る。

??? failure "`ResizeBuffers` が、失敗する"
    バック バッファへの参照（`ComPtr`）が残っているまたは、GPU がまだ使用中。全部、解放しフェンスで待ってから呼ぶ。

??? failure "色が、暗い（明るい）"
    リニアの値を `UNORM` の RTV に書いている。RTV を `_SRGB` にして作る。

## これだけ覚える

!!! abstract "まとめ"
    - [x] D3D12 のスワップ チェーンはコマンド キューを渡して作る
    - [x] フリップ モデル（`FLIP_DISCARD`）、2〜3 枚。`_SRGB` は RTV で
    - [x] バック バッファは複数のリソース。各々に RTV を作る
    - [x] 今の描き先は `GetCurrentBackBufferIndex()`
    - [x] 描く前後にバリア（`PRESENT` ↔ `RENDER_TARGET`）
    - [x] 大きさ変更の前に GPU の完了を待つ

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Descriptor Heap](descriptor-heap.md)
- [Resource Barrier](resource-barrier.md)
- [Fence](fence.md)
- [Microsoft Learn: DXGI スワップ チェーン](https://learn.microsoft.com/ja-jp/windows/win32/direct3ddxgi/d3d10-graphics-programming-guide-dxgi)
