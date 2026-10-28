---
title: 第 3 章 Engine に DirectX 12 を載せる
tags:
  - C#連携
---

# 第 3 章 Engine に DirectX 12 を載せる

エンジンが何も描かないままでは、エディタにつないでも、本当に動いているのか確かめようがありません。そこで、`Engine::Tick` の中で DirectX 12 を使って、ウィンドウを 1 色で塗りつぶすところまで作ります。DirectX 12 の部品（デバイス、キュー、フェンス、スワップ チェーン）の詳しい説明は、[DirectX 12 Guide](../directx/dx12/index.md) にあります。この章で説明するのは、それらを Engine の中に組み込む形と、WPF から使うことを見据えた設計（ウィンドウのリサイズ、例外を境界の外に出さない）だけです。

!!! info "このページを読む前に"
    - [第 2 章 Engine プロジェクト：DLL の骨組み](02-engine-skeleton.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## この章の考え方

DirectX 12 は、GPU に仕事を頼む手順をプログラマーが細かく書く仕組みです。そのため、画面を 1 色で塗るだけでも、デバイス、コマンド キュー、スワップ チェーン、フェンスなど、たくさんの部品が要ります。初めて見ると、量の多さに驚くかもしれません。

まず、全体の流れを言葉で説明しておきます。

1. GPU を選び、窓口（デバイス）を作る。
2. 仕事の受付（コマンド キュー）を作る。GPU への仕事は、ここに並べて頼む。
3. 画面に出す絵を入れる板（バック バッファ）の束、つまりスワップ チェーンを作る。裏の板に描いて、表の板と入れ替える。
4. 毎フレーム、「何をするか」の指示書（コマンド リスト）を書いて、キューに出す。
5. GPU が終わったかどうかを目印（フェンス）で確かめる。終わる前に指示書や板を触ってはいけない。

この章のコードは、この 5 つをそのまま書いたものです。各部品の詳しい意味は、DirectX 12 Guide の各ページにあります。この教材では、「WPF の中に埋め込んでも壊れない」ために必要な点（リサイズ、後片付け、例外の扱い）に絞って説明します。

DirectX 12 を初めて触る人は、先に [DirectX 12 Guide](../directx/dx12/index.md) の最初の数ページを読んでおくと、この章がずっと読みやすくなります。

## この章のゴール

- Engine に DX12 の描画クラス `Renderer`（非公開）を追加する。
- `Engine::Create` がウィンドウ（`HWND`）にスワップ チェーンを作る。
- `Engine::Tick` が毎フレーム、色が変わる塗りつぶしを描く。
- `Engine::Resize` でウィンドウの大きさの変化に追従する。
- エラーを例外にして、境界で捕まえる（例外を DLL の外に出さない）。

## 追加するもの

```text
Engine\
  third_party\d3dx12\   ← d3dx12.h（DX12 の補助ヘッダー）
  src\
    Dx12Util.h          エラー確認のヘルパー
    Renderer.h / .cpp   DX12 の描画（非公開）
    Engine.cpp          Renderer を持つように変更
```

## 手順 1：d3dx12.h を用意する

`d3dx12.h`（`CD3DX12_…` というヘルパー群）は Windows SDK に入っていません。Microsoft の DirectX-Headers リポジトリから入手します。

1. <https://github.com/microsoft/DirectX-Headers> の `include/directx/` にある `d3dx12.h` と `d3dx12_*.h` をすべて取得する（新しい版では、複数のファイルに分かれています）。
2. `Engine\third_party\d3dx12\` に置く。
3. Engine プロジェクトの「追加のインクルード ディレクトリ」に `$(ProjectDir)third_party\d3dx12` を足す。

| 新しく出てきたもの | 説明 |
| --- | --- |
| `d3dx12.h` | `CD3DX12_RESOURCE_BARRIER` や `CD3DX12_CPU_DESCRIPTOR_HANDLE` など DX12 の構造体を簡単に書くための補助。ヘッダーだけ（ライブラリは不要） |
| `third_party\` | 外部から持ってきたコードを置くフォルダー。自分のコードと分けておく |

## 手順 2：エラー確認のヘルパー

DX12 の関数は、失敗すると `HRESULT`（負の値）を返します。毎回 `if (FAILED(hr))` を書くのは大変なので、失敗したら例外を投げる関数を作ります。

`src\Dx12Util.h`:

```cpp
#pragma once

#include <windows.h>

#include <format>
#include <stdexcept>

namespace mini {

// HRESULT が失敗なら例外を投げる。DX12 の呼び出しをこれで包む。
inline void ThrowIfFailed(HRESULT hr, const char* what) {
  if (FAILED(hr)) {
    throw std::runtime_error(std::format("{} に失敗しました（HRESULT 0x{:08X}）", what, static_cast<unsigned>(hr)));
  }
}

}  // namespace mini
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `HRESULT` | Windows API の結果コード（32 ビット整数）。成功は 0 以上、失敗は負。`FAILED(hr)` で判定 |
| `std::runtime_error` | 「実行時に起きたエラー」を表す標準の例外クラス。メッセージを持てる |
| 例外 | `throw` で投げると、呼び出し元をさかのぼって `catch` まで飛ぶ。DLL の境界を越えさせてはいけない（C# は、C++ の例外を受け取れない。第 32 章） |

## 手順 3：Renderer のヘッダー

`src\Renderer.h`:

```cpp
#pragma once

#include <d3d12.h>
#include <dxgi1_6.h>
#include <wrl/client.h>

#include <array>
#include <cstdint>

namespace mini {

// DirectX 12 の描画。Engine の中だけで使う（公開ヘッダーには出さない）。
class Renderer {
 public:
  static constexpr UINT kFrameCount = 3;            // バック バッファの数 = 同時に進める、フレームの数

  Renderer(HWND window, UINT width, UINT height);
  ~Renderer();
  Renderer(const Renderer&) = delete;
  Renderer& operator=(const Renderer&) = delete;

  void Resize(UINT width, UINT height);
  void Render(const float clear_color[4]);          // 1 フレーム描いて、画面に出す

 private:
  void CreateRenderTargets();                       // バック バッファの RTV を作る
  void WaitForGpu();                                // GPU の、全仕事が終わるまで待つ
  void WaitForSlot(UINT slot);                      // そのスロットの、前回の仕事が終わるまで待つ

  template <typename T>
  using ComPtr = Microsoft::WRL::ComPtr<T>;

  ComPtr<IDXGIFactory6> factory_;
  ComPtr<ID3D12Device> device_;
  ComPtr<ID3D12CommandQueue> queue_;
  ComPtr<IDXGISwapChain3> swap_chain_;
  ComPtr<ID3D12DescriptorHeap> rtv_heap_;
  std::array<ComPtr<ID3D12Resource>, kFrameCount> back_buffers_;
  std::array<ComPtr<ID3D12CommandAllocator>, kFrameCount> allocators_;
  ComPtr<ID3D12GraphicsCommandList> list_;
  ComPtr<ID3D12Fence> fence_;
  HANDLE fence_event_ = nullptr;
  std::array<UINT64, kFrameCount> slot_fence_values_{};   // 各スロットが「ここまで終われば、再利用できる」値
  UINT64 fence_value_ = 0;
  UINT frame_slot_ = 0;
  UINT rtv_size_ = 0;
  UINT width_ = 0;
  UINT height_ = 0;
};

}  // namespace mini
```

## 手順 4：Renderer の実装

`src\Renderer.cpp`:

```cpp
#include "Renderer.h"

#include <d3dx12.h>

#include "Dx12Util.h"

#pragma comment(lib, "d3d12.lib")
#pragma comment(lib, "dxgi.lib")

namespace mini {

Renderer::Renderer(HWND window, UINT width, UINT height) : width_(width), height_(height) {
  // ① デバッグ レイヤー（Debug ビルドだけ）。デバイスを作る「前」に有効にする。
  UINT factory_flags = 0;
#if defined(_DEBUG)
  ComPtr<ID3D12Debug> debug;
  if (SUCCEEDED(D3D12GetDebugInterface(IID_PPV_ARGS(&debug)))) {
    debug->EnableDebugLayer();
    factory_flags |= DXGI_CREATE_FACTORY_DEBUG;
  }
#endif

  // ② ファクトリー → 高性能な GPU → デバイス。
  ThrowIfFailed(CreateDXGIFactory2(factory_flags, IID_PPV_ARGS(&factory_)), "DXGI ファクトリーの作成");
  ComPtr<IDXGIAdapter1> adapter;
  factory_->EnumAdapterByGpuPreference(0, DXGI_GPU_PREFERENCE_HIGH_PERFORMANCE, IID_PPV_ARGS(&adapter));
  ThrowIfFailed(D3D12CreateDevice(adapter.Get(), D3D_FEATURE_LEVEL_11_0, IID_PPV_ARGS(&device_)), "D3D12 デバイスの作成");

  // ③ コマンド キュー。
  D3D12_COMMAND_QUEUE_DESC queue_desc = {};
  queue_desc.Type = D3D12_COMMAND_LIST_TYPE_DIRECT;
  ThrowIfFailed(device_->CreateCommandQueue(&queue_desc, IID_PPV_ARGS(&queue_)), "コマンド キューの作成");

  // ④ スワップ チェーン（フリップ モデル。コマンド キューを渡す）。
  DXGI_SWAP_CHAIN_DESC1 sc = {};
  sc.Width = width;
  sc.Height = height;
  sc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
  sc.SampleDesc.Count = 1;
  sc.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
  sc.BufferCount = kFrameCount;
  sc.SwapEffect = DXGI_SWAP_EFFECT_FLIP_DISCARD;
  ComPtr<IDXGISwapChain1> swap_chain1;
  ThrowIfFailed(factory_->CreateSwapChainForHwnd(queue_.Get(), window, &sc, nullptr, nullptr, &swap_chain1),
                "スワップ チェーンの作成");
  factory_->MakeWindowAssociation(window, DXGI_MWA_NO_ALT_ENTER);     // Alt+Enter の、自動フルスクリーンを無効に
  ThrowIfFailed(swap_chain1.As(&swap_chain_), "IDXGISwapChain3 の取得");

  // ⑤ RTV 用のディスクリプタ ヒープと、各バック バッファの RTV。
  D3D12_DESCRIPTOR_HEAP_DESC heap_desc = {};
  heap_desc.NumDescriptors = kFrameCount;
  heap_desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_RTV;
  ThrowIfFailed(device_->CreateDescriptorHeap(&heap_desc, IID_PPV_ARGS(&rtv_heap_)), "RTV ヒープの作成");
  rtv_size_ = device_->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_RTV);
  CreateRenderTargets();

  // ⑥ フレームごとのコマンド アロケーター、コマンド リスト、フェンス。
  for (auto& allocator : allocators_) {
    ThrowIfFailed(device_->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, IID_PPV_ARGS(&allocator)),
                  "コマンド アロケーターの作成");
  }
  ThrowIfFailed(device_->CreateCommandList(0, D3D12_COMMAND_LIST_TYPE_DIRECT, allocators_[0].Get(), nullptr,
                                           IID_PPV_ARGS(&list_)),
                "コマンド リストの作成");
  list_->Close();                                                      // 作った直後は記録中。いったん閉じる
  ThrowIfFailed(device_->CreateFence(0, D3D12_FENCE_FLAG_NONE, IID_PPV_ARGS(&fence_)), "フェンスの作成");
  fence_event_ = CreateEventW(nullptr, FALSE, FALSE, nullptr);
}

Renderer::~Renderer() {
  WaitForGpu();                                                        // GPU が使い終わるまで待ってから、解放する
  if (fence_event_) CloseHandle(fence_event_);
}

void Renderer::CreateRenderTargets() {
  CD3DX12_CPU_DESCRIPTOR_HANDLE handle(rtv_heap_->GetCPUDescriptorHandleForHeapStart());
  for (UINT i = 0; i < kFrameCount; ++i) {
    ThrowIfFailed(swap_chain_->GetBuffer(i, IID_PPV_ARGS(&back_buffers_[i])), "バック バッファの取得");
    D3D12_RENDER_TARGET_VIEW_DESC rtv = {};
    rtv.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;                      // 書くとき、リニア → sRGB へ、自動変換
    rtv.ViewDimension = D3D12_RTV_DIMENSION_TEXTURE2D;
    device_->CreateRenderTargetView(back_buffers_[i].Get(), &rtv, handle);
    handle.Offset(1, rtv_size_);
  }
}

void Renderer::Render(const float clear_color[4]) {
  // ① このスロットを前に使った仕事が終わるまで待つ（終わっていれば、すぐ進む）。
  WaitForSlot(frame_slot_);

  // ② 記録の準備。
  auto& allocator = allocators_[frame_slot_];
  ThrowIfFailed(allocator->Reset(), "アロケーターのリセット");
  ThrowIfFailed(list_->Reset(allocator.Get(), nullptr), "コマンド リストのリセット");

  // ③ 描くバック バッファを決めて、PRESENT → RENDER_TARGET に切り替え、塗りつぶして、戻す。
  const UINT index = swap_chain_->GetCurrentBackBufferIndex();
  auto* back_buffer = back_buffers_[index].Get();
  CD3DX12_CPU_DESCRIPTOR_HANDLE rtv(rtv_heap_->GetCPUDescriptorHandleForHeapStart(), static_cast<INT>(index), rtv_size_);

  auto to_render = CD3DX12_RESOURCE_BARRIER::Transition(back_buffer, D3D12_RESOURCE_STATE_PRESENT,
                                                        D3D12_RESOURCE_STATE_RENDER_TARGET);
  list_->ResourceBarrier(1, &to_render);
  list_->OMSetRenderTargets(1, &rtv, FALSE, nullptr);
  list_->ClearRenderTargetView(rtv, clear_color, 0, nullptr);
  auto to_present = CD3DX12_RESOURCE_BARRIER::Transition(back_buffer, D3D12_RESOURCE_STATE_RENDER_TARGET,
                                                         D3D12_RESOURCE_STATE_PRESENT);
  list_->ResourceBarrier(1, &to_present);
  ThrowIfFailed(list_->Close(), "コマンド リストのクローズ");

  // ④ キューに投げて、画面に出し、このスロットの完了の目印（フェンス）を積む。
  ID3D12CommandList* lists[] = {list_.Get()};
  queue_->ExecuteCommandLists(1, lists);
  ThrowIfFailed(swap_chain_->Present(1, 0), "Present");
  slot_fence_values_[frame_slot_] = ++fence_value_;
  ThrowIfFailed(queue_->Signal(fence_.Get(), fence_value_), "フェンスの Signal");

  frame_slot_ = (frame_slot_ + 1) % kFrameCount;
}

void Renderer::Resize(UINT width, UINT height) {
  if (width == 0 || height == 0) return;                               // 最小化のとき
  if (width == width_ && height == height_) return;
  WaitForGpu();                                                        // バック バッファを GPU が使い終わるまで待つ
  for (auto& buffer : back_buffers_) buffer.Reset();                   // 参照をすべて解放（残っていると、失敗する）
  ThrowIfFailed(swap_chain_->ResizeBuffers(kFrameCount, width, height, DXGI_FORMAT_UNKNOWN, 0), "ResizeBuffers");
  width_ = width;
  height_ = height;
  CreateRenderTargets();
}

void Renderer::WaitForSlot(UINT slot) {
  const UINT64 value = slot_fence_values_[slot];
  if (fence_->GetCompletedValue() < value) {
    fence_->SetEventOnCompletion(value, fence_event_);
    WaitForSingleObject(fence_event_, INFINITE);
  }
}

void Renderer::WaitForGpu() {
  queue_->Signal(fence_.Get(), ++fence_value_);
  fence_->SetEventOnCompletion(fence_value_, fence_event_);
  WaitForSingleObject(fence_event_, INFINITE);
}

}  // namespace mini
```

この中の各部品は、DX12 Guide の各ページで説明しています。

| 部分 | 参照するページ |
| --- | --- |
| ①② デバッグ レイヤー、ファクトリー、デバイス | [Device and Factory](../directx/dx12/factory-device.md)、[Debug Layer](../directx/dx12/debug-layer.md) |
| ③ コマンド キュー | [Command Queue](../directx/dx12/command-queue.md) |
| ④ スワップ チェーン | [Swap Chain (D3D12)](../directx/dx12/swap-chain.md) |
| ⑤ RTV とヒープ | [Descriptor Heap](../directx/dx12/descriptor-heap.md)、[Descriptor](../directx/dx12/descriptor.md) |
| ⑥ アロケーター、リスト、フェンス | [Command Allocator](../directx/dx12/command-allocator.md)、[Command List](../directx/dx12/command-list.md)、[Fence](../directx/dx12/fence.md) |
| バリア | [Resource Barrier](../directx/dx12/resource-barrier.md) |
| フレームのスロット | [Frame Resources](../directx/dx12/frame-resources.md) |

WPF と組み合わせるうえで、この Renderer の特に大事な点は 2 つです。

| 点 | 理由 |
| --- | --- |
| `Resize` が `WaitForGpu` → バック バッファの解放 → `ResizeBuffers` → RTV の作り直しの順 | WPF の中の子ウィンドウは、ユーザーがウィンドウを広げたり縮めたりするたびに大きさが変わる。バック バッファへの参照が残っていると、`ResizeBuffers` が失敗する |
| デストラクターで `WaitForGpu` | エディタを閉じるとき（またはエンジンを作り直すとき）に GPU が使っている物を解放してクラッシュするのを防ぐ |

## 手順 5：Engine に Renderer を持たせる

`src\Engine.cpp` を次のように書き換えます。ここでは、例外を捕まえて `nullptr` を返すのが要点です。

```cpp
#include "Engine/Engine.h"

#include <windows.h>

#include <cmath>
#include <memory>

#include "Engine/Log.h"
#include "Renderer.h"

namespace mini {

struct Engine::Impl {
  EngineDesc desc;
  std::unique_ptr<Renderer> renderer;
  std::uint64_t frame_count = 0;
  float elapsed_seconds = 0.0f;
};

Engine* Engine::Create(const EngineDesc& desc) {
  auto* engine = new Engine();
  engine->impl_ = new Impl();
  engine->impl_->desc = desc;
  try {
    engine->impl_->renderer = std::make_unique<Renderer>(reinterpret_cast<HWND>(desc.window), desc.width, desc.height);
  } catch (const std::exception& e) {
    // 例外は、ここで止める。境界の外へは、出さない。
    LogError("Engine の作成に失敗: {}", e.what());
    delete engine->impl_;
    delete engine;
    return nullptr;
  }
  LogInfo("Engine を作成しました（{}x{}）", desc.width, desc.height);
  return engine;
}

void Engine::Destroy(Engine* engine) {
  if (!engine) return;
  LogInfo("Engine を破棄します（{} フレーム）", engine->impl_->frame_count);
  delete engine->impl_;                       // Renderer も、ここで壊れる（GPU の完了を待ってから）
  delete engine;
}

void Engine::Resize(std::uint32_t width, std::uint32_t height) {
  impl_->desc.width = width;
  impl_->desc.height = height;
  try {
    impl_->renderer->Resize(width, height);
  } catch (const std::exception& e) {
    LogError("Resize に失敗: {}", e.what());
  }
}

void Engine::Tick(float delta_seconds) {
  impl_->elapsed_seconds += delta_seconds;
  ++impl_->frame_count;

  // 時間で色が変わる塗りつぶし（動いていることが、見てわかる）。
  const float t = impl_->elapsed_seconds;
  const float color[4] = {0.5f + 0.5f * std::sin(t), 0.5f + 0.5f * std::sin(t + 2.1f), 0.5f + 0.5f * std::sin(t + 4.2f),
                          1.0f};
  try {
    impl_->renderer->Render(color);
  } catch (const std::exception& e) {
    LogError("Render に失敗: {}", e.what());
  }
}

std::uint64_t Engine::FrameCount() const {
  return impl_->frame_count;
}

}  // namespace mini
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `reinterpret_cast<HWND>(desc.window)` | `HWND__*`（公開ヘッダーの型）を `HWND`（`windows.h` の型）として扱う。実体は同じ |
| `std::make_unique` | `std::unique_ptr` を作る。`new` の素の呼び出しより安全 |
| `try` / `catch (const std::exception& e)` | 例外を捕まえる。`e.what()` でメッセージを読む |
| `std::sin` | 正弦。`t` が進むと色がなめらかに変わる |
| 例外を境界で止める | `Create` / `Resize` / `Tick` は、外から呼ばれる入口。ここから例外が出ると、呼び出し元（C# を含む）の動作が不定になる。必ず中で捕まえる |

## 動作確認

この時点で Engine をビルドして、エラーがないことを確認します（`Ctrl + Shift + B`、または「ビルド → Engine のビルド」）。画面に出るのは次の章（Player）からです。

## よくあるミス

??? failure "`d3dx12.h` が見つからない（`C1083`）"
    インクルード ディレクトリに `third_party\\d3dx12` を足していないか、`d3dx12.h` だけを置いて `d3dx12_*.h` を置いていません。

??? failure "`LNK2019`（`D3D12CreateDevice` が未解決）"
    `d3d12.lib` がリンクされていません。`#pragma comment(lib, "d3d12.lib")` を書いた `.cpp` が、ビルドに含まれているかを確認してください。

??? failure "`C4189`、`C4100` などの警告がエラーになる（`/WX`）"
    未使用の変数や引数を消すか、名前をコメントにしてください（`float /*delta_seconds*/`）。

??? failure "`Present` が `DXGI_ERROR_INVALID_CALL`"
    スワップ チェーンを作るときに、デバイスを渡していませんか（D3D12 では、コマンド キューを渡します）。また、フォーマットに `_SRGB` を指定していませんか（フリップ モデルでは指定できません）。

## この章で作ったもの

```text
Engine::Create(desc)  → DX12 のデバイス・キュー・スワップ チェーンを作る（失敗なら nullptr）
Engine::Tick(dt)      → 色が変わる塗りつぶしを描いて Present
Engine::Resize(w, h)  → スワップ チェーンの作り直し
Engine::Destroy(e)    → GPU の完了を待って解放
```

## 次の章へ

次の章（[第 4 章 Player：エンジンを動かす実行側](04-player.md)）では、`Player` プロジェクトに Win32 のウィンドウを作って、`Engine` を動かします。色が変わるウィンドウが画面に出ることを確認します。
