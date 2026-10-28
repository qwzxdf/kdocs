---
title: Drawing a Triangle (D3D12)
tags:
  - DirectX
---

# Drawing a Triangle (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

ここまでのページでデバイス、キュー、アロケーター、リスト、フェンス、スワップ チェーン、ディスクリプタ ヒープ、ルート シグネチャ、PSO、頂点バッファと部品を 1 つずつ見てきました。このページではそれをすべてつないで、ウィンドウに三角形を出します。D3D12 の「Hello World」です。

コードは長くなりますが新しい概念は出てきません。1 つずつの部品はこれまでのページで説明したものです。迷ったら各節の末尾にあるリンクから、そのページへ戻ってください。

!!! tip "ポイント"
    - 準備は 1 回だけ。デバイス、キュー、スワップ チェーン、RTV、ルート シグネチャ、PSO、頂点バッファ、フェンスを作る。
    - 毎フレームはアロケーターとリストを `Reset`、バリア、描画、バリア、`Close`、`ExecuteCommandLists`、`Present`、フェンスで待つ。
    - ビューポートとシザー矩形は、必ず設定する。シザー矩形は常に有効。
    - ここでは簡単にするため、毎フレーム GPU の完了を待つ。実用では [Frame Resources](frame-resources.md) のように並列にする。
    - 見えないときはバリア、ビューポートとシザー、PSO の形式、面の向きを疑う。

!!! info "このページを読む前に"
    次のページを読んでから進むとコードのどの部分が何をしているか分かります。[Device and Factory](factory-device.md)、[Command Queue](command-queue.md)、[Command List](command-list.md)、[Fence](fence.md)、[Swap Chain](swap-chain.md)、[Root Signature](root-signature.md)、[PSO](pso.md)、[Upload Buffer](upload-buffer.md) です。構造体を短く書く関数は [Helper Functions](util.md) の `dx12_util.h` を使います。

## 全体の流れ

準備は次の順に進めます。

1. デバイスとコマンド キューを作る（[Device and Factory](factory-device.md)、[Command Queue](command-queue.md)）。
2. スワップ チェーンと RTV を作る（[Swap Chain](swap-chain.md)、[Descriptor Heap](descriptor-heap.md)）。
3. アロケーター、リスト、フェンスを作る（[Command Allocator](command-allocator.md)、[Command List](command-list.md)、[Fence](fence.md)）。
4. ルート シグネチャと PSO を作る（[Root Signature](root-signature.md)、[PSO](pso.md)）。
5. 頂点バッファを作りアップロードする（[Upload Buffer](upload-buffer.md)、[Vertex and Index Buffer Views](vertex-index-view.md)）。

準備が終わったら毎フレーム「記録、実行、`Present`、待つ」を繰り返します。

## 準備のコード

まず、クラスの形を決めます。デバイスから頂点バッファまで、必要な物をメンバーとして持ちます。

```cpp
#include <cstring>

#include <d3d12.h>
#include <d3dcompiler.h>
#include <dxgi1_6.h>
#include <windows.h>
#include <wrl/client.h>

#include <DirectXMath.h>

#include "dx12_util.h"

using Microsoft::WRL::ComPtr;

constexpr UINT kFrameCount = 2;
constexpr UINT kWidth = 1280;
constexpr UINT kHeight = 720;

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

`Init` の最初はデバッグ レイヤー、ファクトリー、アダプター、デバイスです。この順番の理由は[Device and Factory](factory-device.md) にあります。

```cpp
void Renderer::Init(HWND hwnd) {
  UINT factory_flags = 0;
#if defined(_DEBUG)
  ComPtr<ID3D12Debug> debug;
  if (SUCCEEDED(D3D12GetDebugInterface(IID_PPV_ARGS(&debug)))) {
    debug->EnableDebugLayer();  // デバイスを作る前に呼ぶ
    factory_flags |= DXGI_CREATE_FACTORY_DEBUG;
  }
#endif
  ComPtr<IDXGIFactory6> factory;
  CreateDXGIFactory2(factory_flags, IID_PPV_ARGS(&factory));
  ComPtr<IDXGIAdapter1> adapter;
  factory->EnumAdapterByGpuPreference(0, DXGI_GPU_PREFERENCE_HIGH_PERFORMANCE, IID_PPV_ARGS(&adapter));
  D3D12CreateDevice(adapter.Get(), D3D_FEATURE_LEVEL_11_0, IID_PPV_ARGS(&device_));
```

次に、コマンド キューとスワップ チェーンを作ります。スワップ チェーンにはデバイスではなく、キューを渡します（[Swap Chain](swap-chain.md)）。

```cpp
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
```

バック バッファごとに RTV を作ります。ヒープの先頭から `i` 番目のハンドルは、`OffsetHandle` で求めます。RTV の形式を `_SRGB` にして、リニアの色を書いたとき sRGB へ自動変換されるようにしています。

```cpp
  D3D12_DESCRIPTOR_HEAP_DESC heap_desc = {};
  heap_desc.NumDescriptors = kFrameCount;
  heap_desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_RTV;
  device_->CreateDescriptorHeap(&heap_desc, IID_PPV_ARGS(&rtv_heap_));
  rtv_size_ = device_->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_RTV);

  D3D12_CPU_DESCRIPTOR_HANDLE rtv_start = rtv_heap_->GetCPUDescriptorHandleForHeapStart();
  for (UINT i = 0; i < kFrameCount; ++i) {
    swap_chain_->GetBuffer(i, IID_PPV_ARGS(&back_buffers_[i]));
    D3D12_RENDER_TARGET_VIEW_DESC rtv = {};
    rtv.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
    rtv.ViewDimension = D3D12_RTV_DIMENSION_TEXTURE2D;
    device_->CreateRenderTargetView(back_buffers_[i].Get(), &rtv, OffsetHandle(rtv_start, i, rtv_size_));
  }
```

アロケーター、フェンス、フェンス用のイベントもこのタイミングで作ります。

```cpp
  device_->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, IID_PPV_ARGS(&allocator_));
  device_->CreateFence(0, D3D12_FENCE_FLAG_NONE, IID_PPV_ARGS(&fence_));
  fence_event_ = CreateEventW(nullptr, FALSE, FALSE, nullptr);
```

ルート シグネチャはこのサンプルではパラメーターなしです。頂点バッファから位置と色を読むだけなので、入力レイアウトを使うというフラグだけを付けます（[Root Signature](root-signature.md)）。

```cpp
  D3D12_ROOT_SIGNATURE_DESC rs_desc = {};
  rs_desc.NumParameters = 0;
  rs_desc.pParameters = nullptr;
  rs_desc.NumStaticSamplers = 0;
  rs_desc.pStaticSamplers = nullptr;
  rs_desc.Flags = D3D12_ROOT_SIGNATURE_FLAG_ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT;

  ComPtr<ID3DBlob> serialized;
  ComPtr<ID3DBlob> errors;
  D3D12SerializeRootSignature(&rs_desc, D3D_ROOT_SIGNATURE_VERSION_1, &serialized, &errors);
  device_->CreateRootSignature(0, serialized->GetBufferPointer(), serialized->GetBufferSize(),
                               IID_PPV_ARGS(&root_signature_));
```

シェーダーはここでは `D3DCompileFromFile`（シェーダー モデル 5.0）でコンパイルします。`dxc` を使うときは [Shaders and DXC](shaders-dxc.md) を見てください。続けて入力レイアウトを使って PSO を作ります。面の向きを `FrontCounterClockwise = FALSE`（時計回りが表）にしていることに注意します。

```cpp
  ComPtr<ID3DBlob> vs;
  ComPtr<ID3DBlob> ps;
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
  pso.RasterizerState = MakeDefaultRasterizerDesc();
  pso.RasterizerState.FrontCounterClockwise = FALSE;  // 時計回りが表
  pso.BlendState = MakeDefaultBlendDesc();
  pso.DepthStencilState.DepthEnable = FALSE;  // 深度は使わない
  device_->CreateGraphicsPipelineState(&pso, IID_PPV_ARGS(&pipeline_state_));
```

最後に、頂点バッファを作ってアップロードします。DEFAULT に作ったバッファへ UPLOAD のバッファ経由でデータを送り、状態を切り替えて完了を待ちます（[Upload Buffer](upload-buffer.md)）。

```cpp
  device_->CreateCommandList(0, D3D12_COMMAND_LIST_TYPE_DIRECT, allocator_.Get(), nullptr,
                             IID_PPV_ARGS(&command_list_));

  const Vertex vertices[] = {
      {{0.0f, 0.5f, 0.0f}, {1, 0, 0, 1}},
      {{0.5f, -0.5f, 0.0f}, {0, 0, 1, 1}},
      {{-0.5f, -0.5f, 0.0f}, {0, 1, 0, 1}},
  };
  const UINT size = sizeof(vertices);
  D3D12_RESOURCE_DESC buffer_desc = MakeBufferDesc(size);
  D3D12_HEAP_PROPERTIES default_heap = MakeHeapProperties(D3D12_HEAP_TYPE_DEFAULT);
  D3D12_HEAP_PROPERTIES upload_heap = MakeHeapProperties(D3D12_HEAP_TYPE_UPLOAD);
  device_->CreateCommittedResource(&default_heap, D3D12_HEAP_FLAG_NONE, &buffer_desc,
                                   D3D12_RESOURCE_STATE_COPY_DEST, nullptr, IID_PPV_ARGS(&vertex_buffer_));
  device_->CreateCommittedResource(&upload_heap, D3D12_HEAP_FLAG_NONE, &buffer_desc,
                                   D3D12_RESOURCE_STATE_GENERIC_READ, nullptr, IID_PPV_ARGS(&upload_buffer_));

  uint8_t* mapped = nullptr;
  D3D12_RANGE no_read = {0, 0};
  upload_buffer_->Map(0, &no_read, reinterpret_cast<void**>(&mapped));
  std::memcpy(mapped, vertices, size);
  upload_buffer_->Unmap(0, nullptr);

  command_list_->CopyBufferRegion(vertex_buffer_.Get(), 0, upload_buffer_.Get(), 0, size);
  D3D12_RESOURCE_BARRIER barrier = MakeTransitionBarrier(
      vertex_buffer_.Get(), D3D12_RESOURCE_STATE_COPY_DEST, D3D12_RESOURCE_STATE_VERTEX_AND_CONSTANT_BUFFER);
  command_list_->ResourceBarrier(1, &barrier);
  command_list_->Close();
  ID3D12CommandList* lists[] = {command_list_.Get()};
  command_queue_->ExecuteCommandLists(1, lists);
  WaitForGpu();  // コピーの完了を待つ。これでアップロード用のバッファを解放できる
  upload_buffer_.Reset();

  vertex_buffer_view_.BufferLocation = vertex_buffer_->GetGPUVirtualAddress();
  vertex_buffer_view_.SizeInBytes = size;
  vertex_buffer_view_.StrideInBytes = sizeof(Vertex);
}
```

`WaitForGpu` と `Shutdown` は[Fence](fence.md) で説明した形のままです。

```cpp
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

## 毎フレームの記録

準備が終わったら毎フレームの描画です。まず、アロケーターとリストを `Reset` します。前のフレームの GPU の完了はフレームの最後で待ってあります。

```cpp
void Renderer::RenderFrame() {
  const UINT index = swap_chain_->GetCurrentBackBufferIndex();

  allocator_->Reset();
  command_list_->Reset(allocator_.Get(), pipeline_state_.Get());  // 最初から、この PSO で始まる
```

次に、ルート シグネチャ、ビューポート、シザー矩形を設定します。`Reset` で全部が初期化されているので、毎フレーム必要です。**シザー矩形を設定し忘れると、描く範囲が 0 になり何も描かれません。**

```cpp
  command_list_->SetGraphicsRootSignature(root_signature_.Get());
  command_list_->RSSetViewports(1, &viewport_);
  command_list_->RSSetScissorRects(1, &scissor_);
```

バック バッファを描き込み先に切り替えて設定し、クリアします（[Resource Barrier](resource-barrier.md)）。

```cpp
  D3D12_RESOURCE_BARRIER to_render = MakeTransitionBarrier(
      back_buffers_[index].Get(), D3D12_RESOURCE_STATE_PRESENT, D3D12_RESOURCE_STATE_RENDER_TARGET);
  command_list_->ResourceBarrier(1, &to_render);

  D3D12_CPU_DESCRIPTOR_HANDLE rtv = OffsetHandle(rtv_heap_->GetCPUDescriptorHandleForHeapStart(), index, rtv_size_);
  command_list_->OMSetRenderTargets(1, &rtv, FALSE, nullptr);
  const float clear_color[4] = {0.1f, 0.15f, 0.3f, 1.0f};
  command_list_->ClearRenderTargetView(rtv, clear_color, 0, nullptr);
```

三角形を描きます。トポロジー、頂点バッファ、`DrawInstanced` の順です。

```cpp
  command_list_->IASetPrimitiveTopology(D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
  command_list_->IASetVertexBuffers(0, 1, &vertex_buffer_view_);
  command_list_->DrawInstanced(3, 1, 0, 0);
```

描き終えたら状態を `PRESENT` へ戻して、リストを閉じキューに渡して画面に出します。そのあと簡単のため毎フレーム GPU の完了を待ちます。

```cpp
  D3D12_RESOURCE_BARRIER to_present = MakeTransitionBarrier(
      back_buffers_[index].Get(), D3D12_RESOURCE_STATE_RENDER_TARGET, D3D12_RESOURCE_STATE_PRESENT);
  command_list_->ResourceBarrier(1, &to_present);

  command_list_->Close();
  ID3D12CommandList* lists[] = {command_list_.Get()};
  command_queue_->ExecuteCommandLists(1, lists);
  swap_chain_->Present(1, 0);

  WaitForGpu();  // 毎フレーム待つ。Frame Resources で並列にする
}
```

ウィンドウの作成とメッセージ ループは、[Win32 Window and Message Loop](window.md) にまとめています。`Renderer::Init(hwnd)` を呼びループの中で `RenderFrame()` を呼びます。リンクするライブラリは `d3d12.lib`、`dxgi.lib`、`d3dcompiler.lib` です。

## 何も見えないときの確認の順番

画面に何も出ないときは次の順に確認します。

1. クリアの色は出ていますか。出ていなければスワップ チェーン、RTV、バリア、`Present` のどこかが原因です。
2. シザー矩形を設定しましたか。設定し忘れると描く範囲が 0 になります。
3. ビューポートを設定しましたか。大きさが 0 だと何も描かれません。
4. PSO の `RTVFormats` は RTV の形式と一致していますか。`_SRGB` の有無の食い違いがよくある原因です。
5. `FrontCounterClockwise` はどうなっていますか。頂点の並びと食い違うと、三角形が裏面として捨てられます。
6. 頂点バッファの状態の切り替えと完了待ちをしましたか。`COPY_DEST` のままだったりコピーが終わる前に描いたりしていないか確認します。
7. デバッグ レイヤーのメッセージを見ましたか。原因はほぼ必ず出ています（[Debug Layer](debug-layer.md)）。
8. PIX で 1 フレームを撮ると、各命令の結果を目で見られます。

## よくあるミス

??? failure "クリアの色は出るが、三角形が出ない"
    シザー矩形が未設定か PSO の面の向きが、頂点の並びと逆のままです。

??? failure "最初のフレームだけ描けて、2 フレーム目にエラーになる"
    GPU の完了を待たずにアロケーターを `Reset` しています。この例のように毎フレーム `WaitForGpu` するかフレームごとのフェンスで管理します。

??? failure "デバッグ レイヤーが「リソースの状態が違う」と言う"
    バリアの前の状態（`StateBefore`）が実際と違います。バック バッファの遷移を確認します。

??? failure "終了時にクラッシュする"
    終了前に GPU の完了を待っていません。`Shutdown` で `WaitForGpu` を呼びます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 準備は 1 回。デバイス、キュー、スワップ チェーン、RTV、ルート シグネチャ、PSO、頂点バッファ、フェンス
    - [x] 毎フレームは `Reset`、ルート シグネチャとビューポートとシザー、バリア、描画、バリア、`Close`、`Execute`、`Present`、待つ
    - [x] シザー矩形は必須。設定し忘れると何も出ない
    - [x] PSO の形式は、描く先と一致させる
    - [x] ここでは毎フレーム待つ。実用ではフレームを並列に進める

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Helper Functions](util.md)
- [Constant Buffer](constant-buffer.md)
- [Frame Resources](frame-resources.md)
- [Debug Layer](debug-layer.md)
- [描画の流れ（入門）](../../3d/render-flow/index.md)
