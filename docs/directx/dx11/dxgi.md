---
title: DXGI Factory and Adapter
tags:
  - DirectX
---

# DXGI Factory and Adapter

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
</div>

<strong>DXGI</strong>（DirectX Graphics Infrastructure）は、D3D11・D3D12 に、共通の、「GPU と、画面の間」を、つなぐ層です。<strong>どの GPU（アダプター）を使うか、画面にどう出すか（スワップ チェーン）、画面の形式（フォーマット）</strong>を、扱います。D3D11 の、デバイスを、作る前に、アダプターを、選びたいときや、スワップ チェーンを、作るときに、DXGI の、ファクトリーを、使います。

!!! tip "ポイント"
    - DXGI は、D3D とは別の、層。`<dxgi1_6.h>` の、`IDXGIFactory…` と `IDXGIAdapter…` が、中心。
    - <strong>ファクトリー</strong>で、アダプターを、列挙し、スワップ チェーンを、作る。
    - ノート PC の、内蔵 GPU と、外付け GPU から、<strong>高性能なほう</strong>を、選ぶには、`EnumAdapterByGpuPreference` を使う。
    - デバイスから、辿って、ファクトリーを、得ると、デバイスと、同じ GPU の、ファクトリーが、手に入る。
    - フォーマットの名前（`DXGI_FORMAT_…`）も、DXGI の、定義（[Formats and Typeless](../concepts/formats.md)）。

## ファクトリーを作る

```cpp
#include <dxgi1_6.h>
#include <wrl/client.h>

Microsoft::WRL::ComPtr<IDXGIFactory6> factory;
UINT flags = 0;
#if defined(_DEBUG)
flags |= DXGI_CREATE_FACTORY_DEBUG;                        // DXGI のデバッグ メッセージ
#endif
CreateDXGIFactory2(flags, IID_PPV_ARGS(&factory));
```

`IDXGIFactory6` は、Windows 10 1803 以降で、使えます（GPU の、性能による選択が、可能）。`IID_PPV_ARGS` は、COM の、型の取り違えを、防ぐ、マクロで、`IID` と、ポインターの、キャストを、1 度に、書きます。

## アダプターを選ぶ

```cpp
// 高性能な GPU から、順に調べ、D3D11 に対応する、最初のアダプターを、使う。
Microsoft::WRL::ComPtr<IDXGIAdapter1> adapter;
for (UINT i = 0;
     factory->EnumAdapterByGpuPreference(i, DXGI_GPU_PREFERENCE_HIGH_PERFORMANCE, IID_PPV_ARGS(&adapter)) != DXGI_ERROR_NOT_FOUND;
     ++i) {
  DXGI_ADAPTER_DESC1 desc;
  adapter->GetDesc1(&desc);
  if (desc.Flags & DXGI_ADAPTER_FLAG_SOFTWARE) continue;   // ソフトウェア アダプター（WARP）は、飛ばす
  // デバイスが、作れるかだけ確かめる（第 4 引数以降は、実際の作成時と同じ）
  if (SUCCEEDED(D3D11CreateDevice(adapter.Get(), D3D_DRIVER_TYPE_UNKNOWN, nullptr, 0, nullptr, 0, D3D11_SDK_VERSION,
                                  nullptr, nullptr, nullptr))) {
    break;
  }
}
```

`DXGI_GPU_PREFERENCE_HIGH_PERFORMANCE` を、指定すると、性能の高い順に、並びます。ここで、選んだ `adapter` を、`D3D11CreateDevice` の、第 1 引数に、渡し、`DriverType` に、`D3D_DRIVER_TYPE_UNKNOWN` を、指定します（アダプターを、渡すときは、`UNKNOWN` が、決まりです）。

| 値 | 内容 |
| --- | --- |
| `DXGI_GPU_PREFERENCE_UNSPECIFIED` | 並びの指定なし |
| `DXGI_GPU_PREFERENCE_MINIMUM_POWER` | 省電力（内蔵 GPU）を、先に |
| `DXGI_GPU_PREFERENCE_HIGH_PERFORMANCE` | 高性能（外付け GPU）を、先に |

```cpp
// アダプターの情報を表示する（デバッグ用）。
DXGI_ADAPTER_DESC1 desc;
adapter->GetDesc1(&desc);
std::wprintf(L"GPU: %s, VRAM: %zu MB\n", desc.Description, desc.DedicatedVideoMemory / (1024 * 1024));
```

`DedicatedVideoMemory` は、GPU 専用の、メモリ（VRAM）の大きさです。内蔵 GPU は、小さく、共有メモリを使います。

## デバイスから、ファクトリーを辿る

すでに、デバイスを、作っている場合は、デバイスから、ファクトリーを、辿れます。<strong>デバイスと、同じ GPU</strong> の、ファクトリーが、得られるので、スワップ チェーンの作成に、使います。

```cpp
// ID3D11Device → IDXGIDevice → IDXGIAdapter → IDXGIFactory2
Microsoft::WRL::ComPtr<IDXGIDevice> dxgi_device;
device.As(&dxgi_device);                                   // QueryInterface（別のインターフェースを、取り出す）

Microsoft::WRL::ComPtr<IDXGIAdapter> adapter;
dxgi_device->GetAdapter(&adapter);

Microsoft::WRL::ComPtr<IDXGIFactory2> factory2;
adapter->GetParent(IID_PPV_ARGS(&factory2));
```

`ComPtr::As` は、COM の、`QueryInterface` で、1 つのオブジェクトの、別の顔（インターフェース）を、取り出します。`ID3D11Device` と `IDXGIDevice` は、同じ、デバイスの、別の、見方です。別の GPU の、ファクトリーを、使うと、スワップ チェーンが、作れません。

## 出力（モニター）の列挙

```cpp
// 接続されている、モニターの、一覧と、対応する解像度。
Microsoft::WRL::ComPtr<IDXGIOutput> output;
for (UINT i = 0; adapter->EnumOutputs(i, &output) != DXGI_ERROR_NOT_FOUND; ++i) {
  DXGI_OUTPUT_DESC desc;
  output->GetDesc(&desc);
  std::wprintf(L"Output %u: %s\n", i, desc.DeviceName);
}
```

フルスクリーンの解像度の選択、HDR の対応の確認で、使います。普通の、ウィンドウ モードの、ゲームでは、列挙の、必要は、ありません。

## ティアリング（垂直同期なしの、表示）

```cpp
// 垂直同期なしで、表示してよいか（可変リフレッシュレート G-Sync・FreeSync 対応環境で、有用）。
BOOL allow_tearing = FALSE;
factory->CheckFeatureSupport(DXGI_FEATURE_PRESENT_ALLOW_TEARING, &allow_tearing, sizeof(allow_tearing));
```

対応していれば、スワップ チェーンの作成時に `DXGI_SWAP_CHAIN_FLAG_ALLOW_TEARING` を、付け、`Present` で、`DXGI_PRESENT_ALLOW_TEARING` を、使えます（[Swap Chain](swap-chain.md)）。

## よくあるミス

??? failure "ノート PC で、内蔵 GPU が、選ばれて、遅い"
    アダプターを、`nullptr` の、既定に、任せている。`EnumAdapterByGpuPreference` で、高性能な GPU を、選ぶ。

??? failure "スワップ チェーンの作成で、`DXGI_ERROR_INVALID_CALL`"
    デバイスを、作った GPU と、別の GPU の、ファクトリーを、使っている。デバイスから、辿った、ファクトリーを、使う。

??? failure "WARP（ソフトウェア）を、選んで、極端に、遅い"
    アダプターの列挙で、`DXGI_ADAPTER_FLAG_SOFTWARE` を、除いていない。

## これだけ覚える

!!! abstract "まとめ"
    - [x] DXGI は、D3D11・D3D12 で、共通の、GPU と、画面の層
    - [x] ファクトリー → アダプター（GPU）を、列挙・選択
    - [x] 高性能な GPU は、`EnumAdapterByGpuPreference(HIGH_PERFORMANCE)`
    - [x] デバイスから、辿ると、同じ GPU の、ファクトリーが、得られる
    - [x] 次は、スワップ チェーンの作成

## 関連ページ

- [DirectX 11 Guide](index.md)
- [ID3D11Device and Device Context](device.md)
- [Swap Chain](swap-chain.md)
- [Formats and Typeless](../concepts/formats.md)
- [Microsoft Learn: DXGI](https://learn.microsoft.com/ja-jp/windows/win32/direct3ddxgi/d3d10-graphics-programming-guide-dxgi)
