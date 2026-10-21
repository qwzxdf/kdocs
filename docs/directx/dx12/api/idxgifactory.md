---
title: IDXGIFactory
tags:
  - DirectX
api:
  - IDXGIFactory
  - IDXGIFactory2
  - IDXGIFactory4
  - IDXGIFactory6
---

# IDXGIFactory

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">DXGI</span>
`#include <dxgi1_6.h>`
</div>

画面に絵を出すには、GPU を選び、ウィンドウに結びついたスワップ チェーンを作る必要があります。ところが D3D12 のデバイスは「GPU に物を作らせる」だけの窓口で、GPU の一覧もウィンドウとの結びつきも持っていません。この 2 つを受け持つのが DXGI で、その入り口がファクトリー（`IDXGIFactory`）です。

ファクトリーは機能を足すたびに番号が増えてきました。`IDXGIFactory2` でスワップ チェーンの作成関数が新しくなり、`IDXGIFactory4` で WARP が取り出せるようになり、`IDXGIFactory6` で GPU を性能順に取り出せるようになりました。実体は同じファクトリーで、`CreateDXGIFactory2` で作るときに最新の `IDXGIFactory6` として受け取ります。

!!! tip "ポイント"
    - ファクトリーはデバイスの前に作る。作るのは `CreateDXGIFactory2`、デバッグ中は `DXGI_CREATE_FACTORY_DEBUG` を付ける。
    - D3D12 のスワップ チェーンは、デバイスではなく DIRECT のコマンド キューを渡して作る。
    - `MakeWindowAssociation` で Alt+Enter の全画面切り替えを止められる。
    - GPU が無い PC では `EnumWarpAdapter` のソフトウェア描画が最後の手段になる。

!!! info "このページを読む前に"
    ファクトリーを作ってアダプターを選びデバイスを作る流れは [Device and Factory](../factory-device.md) に、スワップ チェーンを作ったあとの使い方は [Swap Chain (D3D12)](../swap-chain.md) にあります。`ComPtr` と `IID_PPV_ARGS` は [ComPtr](../../concepts/comptr.md) を見てください。

## メソッド一覧

| メソッド・関数 | 役割 |
| --- | --- |
| [`CreateDXGIFactory2`](../factory-device.md#createdxgifactory2) | ファクトリーを作る（自由関数） |
| [`EnumAdapterByGpuPreference`](../factory-device.md#enumadapterbygpupreference) | GPU を性能の高い順に取り出す |
| [`EnumWarpAdapter`](#enumwarpadapter) | ソフトウェア描画（WARP）のアダプターを取り出す |
| [`CreateSwapChainForHwnd`](#createswapchainforhwnd) | ウィンドウに結びついたスワップ チェーンを作る |
| [`MakeWindowAssociation`](#makewindowassociation) | ウィンドウの Alt+Enter などの監視を止める |

`CreateDXGIFactory2`、`EnumAdapterByGpuPreference` と、アダプターの名前を調べる `GetDesc1` は、デバイスを作る流れの中で説明しているので [Device and Factory](../factory-device.md) を見てください。

## メソッドの詳しい説明

### EnumWarpAdapter {#enumwarpadapter}

```cpp
HRESULT IDXGIFactory4::EnumWarpAdapter(REFIID riid, void** ppvAdapter);
```

WARP（Windows Advanced Rasterization Platform）のアダプターを取り出します。WARP は GPU の代わりに CPU が描くソフトウェアの実装で、GPU が無い PC や、GPU のドライバーが壊れている PC でも D3D12 を動かせます。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `riid` | `REFIID` | 取り出すインターフェースの ID。`IDXGIAdapter1` など |
| `ppvAdapter` | `void**` | 結果を受け取るポインタのアドレス |

`riid` と `ppvAdapter` は `IID_PPV_ARGS(&adapter)` でまとめて渡します。

```cpp
ComPtr<IDXGIAdapter1> adapter;
HRESULT hr = D3D12CreateDevice(gpu_adapter.Get(), D3D_FEATURE_LEVEL_11_0, IID_PPV_ARGS(&device));
if (FAILED(hr)) {
  // 本物の GPU でデバイスが作れなかった。最後の手段として WARP で作る
  factory->EnumWarpAdapter(IID_PPV_ARGS(&adapter));
  D3D12CreateDevice(adapter.Get(), D3D_FEATURE_LEVEL_11_0, IID_PPV_ARGS(&device));
}
```

戻り値は成功なら `S_OK` です。WARP は動作の確認や CI で GPU が無いサーバーで動かす用途に向いていて、ゲームを遊ぶ速さは出ません。`IDXGIAdapter1::GetDesc1` の `Flags` に `DXGI_ADAPTER_FLAG_SOFTWARE` が立っていれば、WARP です。

### CreateSwapChainForHwnd {#createswapchainforhwnd}

```cpp
HRESULT IDXGIFactory2::CreateSwapChainForHwnd(
    IUnknown* pDevice,
    HWND hWnd,
    const DXGI_SWAP_CHAIN_DESC1* pDesc,
    const DXGI_SWAP_CHAIN_FULLSCREEN_DESC* pFullscreenDesc,
    IDXGIOutput* pRestrictToOutput,
    IDXGISwapChain1** ppSwapChain);
```

ウィンドウ（`HWND`）に結びついたスワップ チェーンを作ります。スワップ チェーンは、描いた画像（バック バッファ）を順番に画面へ出す仕組みです。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pDevice` | `IUnknown*` | D3D12 では DIRECT のコマンド キュー（`ID3D12CommandQueue*`） |
| `hWnd` | `HWND` | 表示先のウィンドウ |
| `pDesc` | `const DXGI_SWAP_CHAIN_DESC1*` | 大きさ、形式、バッファの数、フリップ モデルなどの記述 |
| `pFullscreenDesc` | `const DXGI_SWAP_CHAIN_FULLSCREEN_DESC*` | 全画面の設定。`nullptr` でウィンドウ表示 |
| `pRestrictToOutput` | `IDXGIOutput*` | 表示を特定のモニターに制限する。`nullptr` で制限なし |
| `ppSwapChain` | `IDXGISwapChain1**` | 結果を受け取るポインタのアドレス |

6 つの引数のうち、間違えやすいところを順に見ます。

`pDevice` には D3D12 ではデバイスではなくコマンド キューを渡します。`Present` した画像を出すのは、そのキューに積んだ仕事が終わったあとにしたいからです。デバイスを渡すと失敗します。キューは DIRECT（`D3D12_COMMAND_LIST_TYPE_DIRECT`）のものを渡します。`hWnd` と `pDesc` は `nullptr` にできません。

`pDesc` の `Width` と `Height` に 0 を入れると、ウィンドウのクライアント領域の大きさが使われます。実際の大きさは `IDXGISwapChain1::GetDesc1` で読み戻せます。`Format` に `_SRGB` は指定できません（フリップ モデルの決まりです）。`SwapEffect` は `DXGI_SWAP_EFFECT_FLIP_DISCARD`、`SampleDesc.Count` は 1 にします。各項目の意味は [Swap Chain (D3D12)](../swap-chain.md) にあります。

`pFullscreenDesc` は `nullptr` にするとウィンドウ表示のスワップ チェーンになります。全画面の排他モードが必要なときだけ渡します。「枠なしの全画面ウィンドウ」にして `nullptr` のままにするほうが、Alt+Tab などの扱いが楽です。`pRestrictToOutput` は特殊な用途なので、ふつうは `nullptr` です。

`ppSwapChain` は他の作成関数と違って `riid` と `void**` のペアではなく、`IDXGISwapChain1**` を直接受け取ります。`IID_PPV_ARGS` は使えません。`IDXGISwapChain3` が欲しいときは、`IDXGISwapChain1` で受け取ったあと [`As`](../../concepts/comptr.md#as) で取り出します。

戻り値は次のとおりです。

| 戻り値 | 原因 |
| --- | --- |
| `S_OK` | 成功 |
| `DXGI_ERROR_INVALID_CALL` | `pDesc` の内容が不正（`_SRGB` 形式、フリップ モデルで MSAA、バッファが 1 枚など）。引数の `nullptr` もこれ |
| `E_OUTOFMEMORY` | メモリ不足 |

また、1 つのウィンドウに結びつけられるフリップ モデルのスワップ チェーンは同時に 1 つだけです。作り直すときは、古いほうを先に完全に手放してから作ります。

### MakeWindowAssociation {#makewindowassociation}

```cpp
HRESULT IDXGIFactory::MakeWindowAssociation(HWND WindowHandle, UINT Flags);
```

DXGI がウィンドウのメッセージを監視して行う動作を、止めます。標準では DXGI が Alt+Enter を拾って全画面とウィンドウを自動で切り替えますが、ゲームが自分で切り替えを管理したいときにこれが邪魔になります。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `WindowHandle` | `HWND` | 対象のウィンドウ。`nullptr` で、結びつけを解除する |
| `Flags` | `UINT` | 止めたい動作（下の表） |

| フラグ | 止める動作 |
| --- | --- |
| `DXGI_MWA_NO_WINDOW_CHANGES` | DXGI がウィンドウの大きさやスタイルを変えること全般 |
| `DXGI_MWA_NO_ALT_ENTER` | Alt+Enter での全画面の切り替え |
| `DXGI_MWA_NO_PRINT_SCREEN` | Print Screen でのスクリーンショット |

ゲームで使うのは `DXGI_MWA_NO_ALT_ENTER` です。自分で全画面を切り替えるなら、Alt+Enter を `WM_SYSKEYDOWN` で拾って処理します。呼ぶのは `CreateSwapChainForHwnd` のあとです。スワップ チェーンを作る前に呼んでも、あとから作るスワップ チェーンの動作を変えられません。戻り値は成功なら `S_OK` です。

## よくあるミス

??? failure "`CreateSwapChainForHwnd` が `DXGI_ERROR_INVALID_CALL` で失敗する"
    デバイスを渡している（キューを渡す）、`Format` に `_SRGB` を指定している、フリップ モデルで MSAA にしている、バッファの数が 1 枚、のいずれかです。デバッグ レイヤーのメッセージに理由が出ます。

??? failure "Alt+Enter で勝手に全画面になり、描画がおかしくなる"
    `MakeWindowAssociation(hwnd, DXGI_MWA_NO_ALT_ENTER)` を呼んでいません。

??? failure "ノート PC で WARP が選ばれて遅い"
    アダプターの列挙で `DXGI_ADAPTER_FLAG_SOFTWARE` を飛ばしていません。`EnumAdapterByGpuPreference` で高性能な GPU から順に確認します。

## 関連ページ

- [Device and Factory](../factory-device.md)
- [Swap Chain (D3D12)](../swap-chain.md)
- [IDXGIAdapter](idxgiadapter.md)
- [IDXGISwapChain](idxgiswapchain.md)
- [ComPtr](../../concepts/comptr.md)
- [Microsoft Learn: IDXGIFactory2](https://learn.microsoft.com/ja-jp/windows/win32/api/dxgi1_2/nn-dxgi1_2-idxgifactory2)
