---
title: Drawing a Triangle (D3D12)
tags:
  - DirectX
---

# Drawing a Triangle (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

ここまでのページで、作った部品（デバイス、キュー、アロケーター、リスト、フェンス、スワップ チェーン、ディスクリプタ ヒープ、ルート シグネチャ、PSO、頂点バッファ）を、<strong>つないで、三角形を、描きます</strong>。D3D12 の「Hello World」で、コード量は、多いですが、1 つずつの、部品は、これまでの、ページで、説明した物です。

!!! tip "ポイント"
    - 準備（1 回）: デバイス → キュー → スワップ チェーン → RTV → ルート シグネチャ → PSO → 頂点バッファ（アップロード）→ フェンス。
    - 毎フレーム: アロケーター・リストの `Reset` → バリア（`PRESENT` → `RENDER_TARGET`）→ 描画 → バリア（戻す）→ `Close` → `ExecuteCommandLists` → `Present` → フェンスで待つ。
    - ビューポートと、<strong>シザー矩形</strong>は、必ず、設定する（シザーは、常に、有効）。
    - ここでは、簡単のため、毎フレーム、GPU の完了を、待つ。実用では、[Frame Resources](frame-resources.md) で、並列にする。
    - 見えないときは、バリア・ビューポート/シザー・PSO の、フォーマット・面の向きを、疑う。

## 流れ

| 段階 | 内容 | ページ |
| --- | --- | --- |
| 準備 ① | デバイス、コマンド キュー | [Device and Factory](factory-device.md)、[Command Queue](command-queue.md) |
| 準備 ② | スワップ チェーン、RTV | [Swap Chain](swap-chain.md)、[Descriptor Heap](descriptor-heap.md) |
| 準備 ③ | コマンド アロケーター、リスト、フェンス | [Command Allocator](command-allocator.md)、[Command List](command-list.md)、[Fence](fence.md) |
| 準備 ④ | ルート シグネチャ、PSO | [Root Signature](root-signature.md)、[PSO](pso.md) |
| 準備 ⑤ | 頂点バッファ（アップロード） | [Upload Buffer](upload-buffer.md)、[Vertex and Index Buffer Views](vertex-index-view.md) |
| 毎フレーム | 記録 → 実行 → `Present` → 待つ | 下 |

## 毎フレームの、記録

```cpp
void RenderFrame() {
  const UINT index = swap_chain_->GetCurrentBackBufferIndex();

  // ① アロケーターとリストを、Reset（前のフレームの GPU 完了は、待ち済み）
  allocator_->Reset();
  command_list_->Reset(allocator_.Get(), pipeline_state_.Get());
```

`Reset` で、PSO を、渡すと、最初から、その PSO が、設定された状態で、記録を、始められます。

```cpp
  // ② ルート シグネチャ、ビューポート、シザー矩形を、設定する（Reset で、全部、初期化されている）
  command_list_->SetGraphicsRootSignature(root_signature_.Get());
  command_list_->RSSetViewports(1, &viewport_);
  command_list_->RSSetScissorRects(1, &scissor_);
```

<strong>シザー矩形</strong>を、設定し忘れると、描画範囲が、0 に、なり、何も、描かれません（D3D12 は、シザーが、常に、有効）。

```cpp
  // ③ バック バッファを、PRESENT → RENDER_TARGET に、切り替える
  auto to_render = CD3DX12_RESOURCE_BARRIER::Transition(back_buffers_[index].Get(), D3D12_RESOURCE_STATE_PRESENT,
                                                        D3D12_RESOURCE_STATE_RENDER_TARGET);
  command_list_->ResourceBarrier(1, &to_render);

  // ④ 描き込み先を設定して、クリア
  CD3DX12_CPU_DESCRIPTOR_HANDLE rtv(rtv_heap_->GetCPUDescriptorHandleForHeapStart(), index, rtv_size_);
  command_list_->OMSetRenderTargets(1, &rtv, FALSE, nullptr);
  const float clear_color[4] = {0.1f, 0.15f, 0.3f, 1.0f};
  command_list_->ClearRenderTargetView(rtv, clear_color, 0, nullptr);
```

バック バッファの、状態を、`RENDER_TARGET` に、してから、描き込み先に、設定し、クリアします（[Resource Barrier](resource-barrier.md)）。

```cpp
  // ⑤ 三角形を描く
  command_list_->IASetPrimitiveTopology(D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
  command_list_->IASetVertexBuffers(0, 1, &vertex_buffer_view_);
  command_list_->DrawInstanced(3, 1, 0, 0);

  // ⑥ RENDER_TARGET → PRESENT に戻す
  auto to_present = CD3DX12_RESOURCE_BARRIER::Transition(back_buffers_[index].Get(),
                                                         D3D12_RESOURCE_STATE_RENDER_TARGET,
                                                         D3D12_RESOURCE_STATE_PRESENT);
  command_list_->ResourceBarrier(1, &to_present);

  // ⑦ 記録を終えて、キューに投げ、画面に出す
  command_list_->Close();
  ID3D12CommandList* lists[] = {command_list_.Get()};
  command_queue_->ExecuteCommandLists(1, lists);
  swap_chain_->Present(1, 0);

  WaitForGpu();                                              // 簡単のため、毎フレーム待つ（frame-resources.md で、改善）
}
```

## 動く、完全なプログラム

部品を、1 つに、まとめた、完成形です。`triangle.hlsl` は、[Shaders and Compilation](../dx11/shaders.md) と、同じシェーダーで、ここでは、`D3DCompileFromFile`（SM 5.0）で、コンパイルします（`dxc` を、使うなら、[Shaders and DXC](shaders-dxc.md)）。

```cpp
#include <d3d12.h>
#include <d3dcompiler.h>
#include <dxgi1_6.h>
#include <windows.h>
#include <wrl/client.h>

#include <DirectXMath.h>
#include <d3dx12.h>

using Microsoft::WRL::ComPtr;

constexpr UINT kFrameCount = 2;
constexpr UINT kWidth = 1280, kHeight = 720;

struct Vertex {
  DirectX::XMFLOAT3 position;
  DirectX::XMFLOAT4 color;
};

class Renderer {
 public:
  void Init(HWND hwnd);
  void RenderFrame();
  void Shutdown();

 private:
  void WaitForGpu();

  ComPtr<ID3D12Device> device_;
  ComPtr<ID3D12CommandQueue> command_queue_;
  ComPtr<IDXGISwapChain3> swap_chain_;
  ComPtr<ID3D12DescriptorHeap> rtv_heap_;
  ComPtr<ID3D12Resource> back_buffers_[kFrameCount];
  ComPtr<ID3D12CommandAllocator> allocator_;
  ComPtr<ID3D12GraphicsCommandList> command_list_;
  ComPtr<ID3D12RootSignature> root_signature_;
  ComPtr<ID3D12PipelineState> pipeline_state_;
  ComPtr<ID3D12Resource> vertex_buffer_;
  ComPtr<ID3D12Resource> upload_buffer_;
  ComPtr<ID3D12Fence> fence_;
  D3D12_VERTEX_BUFFER_VIEW vertex_buffer_view_ = {};
  D3D12_VIEWPORT viewport_ = {0.0f, 0.0f, float(kWidth), float(kHeight), 0.0f, 1.0f};
  D3D12_RECT scissor_ = {0, 0, LONG(kWidth), LONG(kHeight)};
  HANDLE fence_event_ = nullptr;
  UINT64 fence_value_ = 0;
  UINT rtv_size_ = 0;
};
```

```cpp
void Renderer::Init(HWND hwnd) {
  UINT factory_flags = 0;
#if defined(_DEBUG)
  ComPtr<ID3D12Debug> debug;
  if (SUCCEEDED(D3D12GetDebugInterface(IID_PPV_ARGS(&debug)))) {
    debug->EnableDebugLayer();
    factory_flags |= DXGI_CREATE_FACTORY_DEBUG;
  }
#endif
  ComPtr<IDXGIFactory6> factory;
  CreateDXGIFactory2(factory_flags, IID_PPV_ARGS(&factory));
  ComPtr<IDXGIAdapter1> adapter;
  factory->EnumAdapterByGpuPreference(0, DXGI_GPU_PREFERENCE_HIGH_PERFORMANCE, IID_PPV_ARGS(&adapter));
  D3D12CreateDevice(adapter.Get(), D3D_FEATURE_LEVEL_11_0, IID_PPV_ARGS(&device_));

  D3D12_COMMAND_QUEUE_DESC queue_desc = {};
  queue_desc.Type = D3D12_COMMAND_LIST_TYPE_DIRECT;
  device_->CreateCommandQueue(&queue_desc, IID_PPV_ARGS(&command_queue_));

  DXGI_SWAP_CHAIN_DESC1 sc = {};
  sc.Width = kWidth;
  sc.Height = kHeight;
  sc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
  sc.SampleDesc.Count = 1;
  sc.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
  sc.BufferCount = kFrameCount;
  sc.SwapEffect = DXGI_SWAP_EFFECT_FLIP_DISCARD;
  ComPtr<IDXGISwapChain1> swap_chain1;
  factory->CreateSwapChainForHwnd(command_queue_.Get(), hwnd, &sc, nullptr, nullptr, &swap_chain1);
  factory->MakeWindowAssociation(hwnd, DXGI_MWA_NO_ALT_ENTER);
  swap_chain1.As(&swap_chain_);

  D3D12_DESCRIPTOR_HEAP_DESC heap_desc = {};
  heap_desc.NumDescriptors = kFrameCount;
  heap_desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_RTV;
  device_->CreateDescriptorHeap(&heap_desc, IID_PPV_ARGS(&rtv_heap_));
  rtv_size_ = device_->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_RTV);
  CD3DX12_CPU_DESCRIPTOR_HANDLE handle(rtv_heap_->GetCPUDescriptorHandleForHeapStart());
  for (UINT i = 0; i < kFrameCount; ++i) {
    swap_chain_->GetBuffer(i, IID_PPV_ARGS(&back_buffers_[i]));
    D3D12_RENDER_TARGET_VIEW_DESC rtv = {};
    rtv.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
    rtv.ViewDimension = D3D12_RTV_DIMENSION_TEXTURE2D;
    device_->CreateRenderTargetView(back_buffers_[i].Get(), &rtv, handle);
    handle.Offset(1, rtv_size_);
  }

  device_->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, IID_PPV_ARGS(&allocator_));
  device_->CreateFence(0, D3D12_FENCE_FLAG_NONE, IID_PPV_ARGS(&fence_));
  fence_event_ = CreateEventW(nullptr, FALSE, FALSE, nullptr);
```

```cpp
  // ルート シグネチャ: パラメータなし（頂点入力だけ）。
  CD3DX12_ROOT_SIGNATURE_DESC rs_desc;
  rs_desc.Init(0, nullptr, 0, nullptr, D3D12_ROOT_SIGNATURE_FLAG_ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT);
  ComPtr<ID3DBlob> serialized, errors;
  D3D12SerializeRootSignature(&rs_desc, D3D_ROOT_SIGNATURE_VERSION_1, &serialized, &errors);
  device_->CreateRootSignature(0, serialized->GetBufferPointer(), serialized->GetBufferSize(),
                               IID_PPV_ARGS(&root_signature_));

  // シェーダー（SM 5.0 で、コンパイル）。
  ComPtr<ID3DBlob> vs, ps;
  D3DCompileFromFile(L"triangle.hlsl", nullptr, nullptr, "VSMain", "vs_5_0", D3DCOMPILE_ENABLE_STRICTNESS, 0, &vs, &errors);
  D3DCompileFromFile(L"triangle.hlsl", nullptr, nullptr, "PSMain", "ps_5_0", D3DCOMPILE_ENABLE_STRICTNESS, 0, &ps, &errors);

  const D3D12_INPUT_ELEMENT_DESC elements[] = {
      {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0, D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},
      {"COLOR", 0, DXGI_FORMAT_R32G32B32A32_FLOAT, 0, 12, D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},
  };
  D3D12_GRAPHICS_PIPELINE_STATE_DESC pso = {};
  pso.pRootSignature = root_signature_.Get();
  pso.VS = {vs->GetBufferPointer(), vs->GetBufferSize()};
  pso.PS = {ps->GetBufferPointer(), ps->GetBufferSize()};
  pso.InputLayout = {elements, ARRAYSIZE(elements)};
  pso.PrimitiveTopologyType = D3D12_PRIMITIVE_TOPOLOGY_TYPE_TRIANGLE;
  pso.NumRenderTargets = 1;
  pso.RTVFormats[0] = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
  pso.SampleDesc.Count = 1;
  pso.SampleMask = UINT_MAX;
  pso.RasterizerState = CD3DX12_RASTERIZER_DESC(D3D12_DEFAULT);
  pso.RasterizerState.FrontCounterClockwise = TRUE;
  pso.BlendState = CD3DX12_BLEND_DESC(D3D12_DEFAULT);
  pso.DepthStencilState.DepthEnable = FALSE;
  device_->CreateGraphicsPipelineState(&pso, IID_PPV_ARGS(&pipeline_state_));
```

```cpp
  // コマンド リスト（アップロードのコピーを、記録する）。
  device_->CreateCommandList(0, D3D12_COMMAND_LIST_TYPE_DIRECT, allocator_.Get(), nullptr, IID_PPV_ARGS(&command_list_));

  // 頂点バッファ: DEFAULT に作り、UPLOAD 経由で、データを送る。
  const Vertex vertices[] = {
      {{0.0f, 0.5f, 0.0f}, {1, 0, 0, 1}},
      {{-0.5f, -0.5f, 0.0f}, {0, 1, 0, 1}},
      {{0.5f, -0.5f, 0.0f}, {0, 0, 1, 1}},
  };
  const UINT size = sizeof(vertices);
  auto buffer_desc = CD3DX12_RESOURCE_DESC::Buffer(size);
  auto default_heap = CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_DEFAULT);
  auto upload_heap = CD3DX12_HEAP_PROPERTIES(D3D12_HEAP_TYPE_UPLOAD);
  device_->CreateCommittedResource(&default_heap, D3D12_HEAP_FLAG_NONE, &buffer_desc, D3D12_RESOURCE_STATE_COPY_DEST,
                                   nullptr, IID_PPV_ARGS(&vertex_buffer_));
  device_->CreateCommittedResource(&upload_heap, D3D12_HEAP_FLAG_NONE, &buffer_desc, D3D12_RESOURCE_STATE_GENERIC_READ,
                                   nullptr, IID_PPV_ARGS(&upload_buffer_));
  uint8_t* mapped = nullptr;
  CD3DX12_RANGE no_read(0, 0);
  upload_buffer_->Map(0, &no_read, reinterpret_cast<void**>(&mapped));
  std::memcpy(mapped, vertices, size);
  upload_buffer_->Unmap(0, nullptr);

  command_list_->CopyBufferRegion(vertex_buffer_.Get(), 0, upload_buffer_.Get(), 0, size);
  auto barrier = CD3DX12_RESOURCE_BARRIER::Transition(vertex_buffer_.Get(), D3D12_RESOURCE_STATE_COPY_DEST,
                                                      D3D12_RESOURCE_STATE_VERTEX_AND_CONSTANT_BUFFER);
  command_list_->ResourceBarrier(1, &barrier);
  command_list_->Close();
  ID3D12CommandList* lists[] = {command_list_.Get()};
  command_queue_->ExecuteCommandLists(1, lists);
  WaitForGpu();                                              // コピーの完了を、待つ（その後、upload_buffer_ を、解放できる）
  upload_buffer_.Reset();

  vertex_buffer_view_.BufferLocation = vertex_buffer_->GetGPUVirtualAddress();
  vertex_buffer_view_.SizeInBytes = size;
  vertex_buffer_view_.StrideInBytes = sizeof(Vertex);
}

void Renderer::WaitForGpu() {
  const UINT64 value = ++fence_value_;
  command_queue_->Signal(fence_.Get(), value);
  if (fence_->GetCompletedValue() < value) {
    fence_->SetEventOnCompletion(value, fence_event_);
    WaitForSingleObject(fence_event_, INFINITE);
  }
}

void Renderer::Shutdown() {
  WaitForGpu();
  CloseHandle(fence_event_);
}
```

`RenderFrame` は、上の「毎フレームの、記録」の通りです。ウィンドウの、作成と、メッセージ ループは、[Win32 Window and Message Loop](../dx11/window.md) と、同じで、`Renderer::Init(hwnd)` を、呼び、ループで `RenderFrame()` を、呼びます。リンクする、ライブラリは、`d3d12.lib`、`dxgi.lib`、`d3dcompiler.lib` です。

## 何も、見えないときの、チェックリスト

| 順 | 確認 | 原因の例 |
| --- | --- | --- |
| 1 | クリアの色は、出ているか | 出ない → スワップ チェーン・RTV・バリア・`Present` |
| 2 | シザー矩形を、設定したか | 設定忘れで、描画範囲が 0 |
| 3 | ビューポートを、設定したか | 大きさ 0 |
| 4 | PSO の `RTVFormats` は、RTV と、一致か | `_SRGB` の、有無の、食い違い |
| 5 | `FrontCounterClockwise` | 反時計回りの三角形が、裏面として、捨てられている |
| 6 | 頂点バッファの、状態遷移と、完了待ち | `COPY_DEST` のまま、または、コピーが、終わる前に、描いた |
| 7 | デバッグ レイヤーの、メッセージ | 原因が、ほぼ、必ず、出ている（[Debug Layer](debug-layer.md)） |
| 8 | PIX で、1 フレームを、撮る | 各命令の、結果を、目で、見る |

## よくあるミス

??? failure "クリアの色は、出るが、三角形が、出ない"
    シザー矩形が、未設定。または、PSO の、面の向きが、時計回りが、表のまま。

??? failure "最初のフレームだけ、描ける、または、2 フレーム目に、エラー"
    アロケーターを、GPU の、完了を、待たずに、`Reset` した。毎フレーム、`WaitForGpu` する（この例）。または、フレーム ごとの、フェンスで、管理する。

??? failure "デバッグ レイヤーが、「リソースの、状態が、違う」と、言う"
    バリアの、前の状態（`StateBefore`）が、実際と、違う。バック バッファの、遷移を、確認する。

??? failure "終了時に、クラッシュ"
    終了前に、GPU の完了を、待っていない。`Shutdown` で、`WaitForGpu`。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 準備（1 回）: デバイス・キュー・スワップ チェーン・RTV・ルート シグネチャ・PSO・頂点バッファ・フェンス
    - [x] 毎フレーム: `Reset` → ルート シグネチャ・ビューポート・シザー → バリア → 描画 → バリア → `Close` → `Execute` → `Present` → 待つ
    - [x] シザー矩形は、必須。設定し忘れると、何も、出ない
    - [x] PSO の、フォーマットは、描く先と、一致させる
    - [x] ここでは、毎フレーム待つ。実用は、フレーム イン フライトで、並列に

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Constant Buffer](constant-buffer.md)
- [Frame Resources](frame-resources.md)
- [Debug Layer](debug-layer.md)
- [描画の流れ（入門）](../../3d/render-flow/index.md)
