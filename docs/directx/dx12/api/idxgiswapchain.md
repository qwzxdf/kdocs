---
title: IDXGISwapChain
tags:
  - DirectX
api:
  - IDXGISwapChain
  - IDXGISwapChain1
  - IDXGISwapChain2
  - IDXGISwapChain3
---

# IDXGISwapChain

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">DXGI</span>
`#include <dxgi1_6.h>`
</div>

描いた絵を画面に出すとき、途中まで描いた絵が見えてしまっては困ります。そこで、画像（バック バッファ）を 2〜3 枚用意して、1 枚を表示している間に別の 1 枚へ描き、描き終わったら入れ替えます。この入れ替えを受け持つのがスワップ チェーンです。

メソッドは `Present`（画面に出す）、`GetBuffer`（バック バッファのリソースを取り出す）、`ResizeBuffers`（ウィンドウの大きさに合わせて作り直す）が基本です。D3D12 では今どのバッファへ描くかを自分で知る必要があるので `GetCurrentBackBufferIndex` も使います。入力から表示までの遅れを減らしたいときは、`SetMaximumFrameLatency` と `GetFrameLatencyWaitableObject` を足します。この 2 つは番号つきのインターフェースにあり、`IDXGISwapChain3` で全部受け取れます。

!!! tip "ポイント"
    - 作るのは [`CreateSwapChainForHwnd`](idxgifactory.md#createswapchainforhwnd)。受け取った `IDXGISwapChain1` を `As` で `IDXGISwapChain3` にする。
    - 今の描き先は `GetCurrentBackBufferIndex()`。自分で数えない。
    - `Present(1, 0)` が垂直同期あり、`Present(0, DXGI_PRESENT_ALLOW_TEARING)` が同期なし。
    - `ResizeBuffers` の前にバック バッファへの参照を全部手放す。
    - 戻り値が `DXGI_ERROR_DEVICE_REMOVED` ならデバイスが失われている。

!!! info "このページを読む前に"
    スワップ チェーンの作り方とバック バッファの RTV は [Swap Chain (D3D12)](../swap-chain.md) にあります。バリアで `PRESENT` と `RENDER_TARGET` を切り替える話は [Resource Barrier](../resource-barrier.md) です。

## メソッド一覧

| メソッド | 役割 | 持っているインターフェース |
| --- | --- | --- |
| [`Present`](#present) | バック バッファを画面に出す | `IDXGISwapChain` |
| [`GetBuffer`](#getbuffer) | バック バッファのリソースを取り出す | `IDXGISwapChain` |
| [`ResizeBuffers`](#resizebuffers) | バッファの大きさや数を変える | `IDXGISwapChain` |
| [`GetCurrentBackBufferIndex`](#getcurrentbackbufferindex) | いま描くバッファの番号 | `IDXGISwapChain3` |
| [`SetMaximumFrameLatency`](#setmaximumframelatency) | 先に進めるフレームの数を決める | `IDXGISwapChain2` |
| [`GetFrameLatencyWaitableObject`](#getframelatencywaitableobject) | 待ち合わせ用のイベントを取る | `IDXGISwapChain2` |

## メソッドの詳しい説明

### Present {#present}

```cpp
HRESULT IDXGISwapChain::Present(UINT SyncInterval, UINT Flags);
```

描き終えたバック バッファを画面に出す予約をします。D3D12 では、`ExecuteCommandLists` で積んだ仕事のあとに実行されます。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `SyncInterval` | `UINT` | 垂直同期（画面の更新）を待つ回数 |
| `Flags` | `UINT` | `0`、または `DXGI_PRESENT_*` |

`SyncInterval` は 0 から 4 までです。`1` なら画面の更新に 1 回合わせて表示するので、60 Hz のモニターで 1 秒に最大 60 枚です。画面の途中で絵が切り替わる「ティアリング」は起きません。`2` なら 2 回に 1 回しか更新しない（30 fps になる）ので、GPU が重いときの上限として使えます。`0` は待たずにすぐ出すので、描くのが画面の更新より速いとティアリングが出ます。

`0` の場合、フリップ モデルでは「前に出したがまだ表示していないフレーム」を捨てて新しいほうに差し替えます。ティアリングを許して最速で表示したいなら `Flags` に `DXGI_PRESENT_ALLOW_TEARING` を付けます。これを使うには、スワップ チェーンの作成時にも `DXGI_SWAP_CHAIN_FLAG_ALLOW_TEARING` を付けておき、`IDXGIFactory5::CheckFeatureSupport` で対応を確かめる必要があります。

`Flags` のうち、よく使うのは次のものです。

| フラグ | 意味 |
| --- | --- |
| `0` | 通常 |
| `DXGI_PRESENT_ALLOW_TEARING` | ティアリングを許す（可変リフレッシュ レート向け）。`SyncInterval` は 0 |
| `DXGI_PRESENT_TEST` | 実際には出さず、出せる状態かだけを確かめる |

戻り値は次のとおりです。

| 戻り値 | 意味と対処 |
| --- | --- |
| `S_OK` | 成功 |
| `DXGI_STATUS_OCCLUDED` | 成功の一種。ウィンドウが隠れていて表示されない。描画を止めるか間引くとよい |
| `DXGI_ERROR_DEVICE_REMOVED` | GPU が取り外された、ドライバーが更新された、GPU がハングした、など。`ID3D12Device::GetDeviceRemovedReason` で理由を調べる |
| `DXGI_ERROR_DEVICE_RESET` | GPU のリセット。デバイスを作り直す |

`DXGI_STATUS_OCCLUDED` は `SUCCEEDED` が真になる値なので、`FAILED` だけで判定すると見逃します。`FAILED(hr)` のときに `GetDeviceRemovedReason` を呼ぶのが定石です。

```cpp
HRESULT hr = swap_chain->Present(1, 0);
if (hr == DXGI_ERROR_DEVICE_REMOVED || hr == DXGI_ERROR_DEVICE_RESET) {
  HRESULT reason = device->GetDeviceRemovedReason();  // 原因が分かる
  // ログに出して、デバイスとリソースを作り直す
}
```

### GetBuffer {#getbuffer}

```cpp
HRESULT IDXGISwapChain::GetBuffer(UINT Buffer, REFIID riid, void** ppSurface);
```

スワップ チェーンのバック バッファをリソースとして取り出します。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Buffer` | `UINT` | 何番目のバッファか（0 から `BufferCount - 1`） |
| `riid` | `REFIID` | 取り出すインターフェースの ID。`ID3D12Resource` |
| `ppSurface` | `void**` | 結果を受け取るポインタのアドレス |

```cpp
for (UINT i = 0; i < kFrameCount; ++i) {
  swap_chain->GetBuffer(i, IID_PPV_ARGS(&back_buffers[i]));
}
```

フリップ モデルでは、バック バッファが入れ替わるたびに「どのリソースが画面に出る順番か」が変わります。そこで、バッファ全部を最初に取り出して配列に持ち、`GetCurrentBackBufferIndex` の番号で選びます。取り出すたびに参照カウントが 1 増えるので、[`ResizeBuffers`](#resizebuffers) の前にこの参照も手放す必要があります。`Buffer` が範囲外のときや `riid` が合わないときは失敗します。

### ResizeBuffers {#resizebuffers}

```cpp
HRESULT IDXGISwapChain::ResizeBuffers(
    UINT BufferCount,
    UINT Width,
    UINT Height,
    DXGI_FORMAT NewFormat,
    UINT SwapChainFlags);
```

バック バッファの数、大きさ、形式を変えます。ウィンドウの大きさが変わったとき（`WM_SIZE`）に呼びます。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `BufferCount` | `UINT` | 新しいバッファの数。`0` で今のまま |
| `Width` | `UINT` | 新しい幅。`0` でウィンドウのクライアント領域の幅 |
| `Height` | `UINT` | 新しい高さ。`0` でクライアント領域の高さ |
| `NewFormat` | `DXGI_FORMAT` | 新しい形式。`DXGI_FORMAT_UNKNOWN` で今のまま |
| `SwapChainFlags` | `UINT` | `DXGI_SWAP_CHAIN_FLAG_*` の組み合わせ |

0 や `UNKNOWN` が「そのまま」を意味するので、ウィンドウの大きさだけ合わせたいときは `ResizeBuffers(0, 0, 0, DXGI_FORMAT_UNKNOWN, flags)` と書けます。`Width` と `Height` を 0 にすれば、自分でクライアント領域を取らなくても済みます。フリップ モデルのバッファは 2 枚以上必要です。

`SwapChainFlags` には、スワップ チェーンを作ったときと同じ値を渡し直します。`ALLOW_TEARING` や `FRAME_LATENCY_WAITABLE_OBJECT` を付けて作ったなら、同じフラグを付け続けます。変えてしまうと作成時の前提が崩れるので、意図しない動作の元になります。

最もよくある失敗は、バック バッファへの参照が残っていることです。`GetBuffer` で取り出した `ComPtr` を手放し、それを使うコマンド リストが GPU で実行し終えるまで待ってから呼びます。

```cpp
void OnResize(UINT width, UINT height) {
  WaitForGpu();                                    // GPU が使い終わるまで待つ
  for (auto& buffer : back_buffers) buffer.Reset();  // 参照をすべて手放す
  swap_chain->ResizeBuffers(0, width, height, DXGI_FORMAT_UNKNOWN, swap_chain_flags);
  // GetBuffer と CreateRenderTargetView をやり直す
}
```

戻り値は成功なら `S_OK` です。参照が残っているときは失敗します（通常は `DXGI_ERROR_INVALID_CALL`）。デバッグ レイヤーを有効にしていれば、原因がメッセージに出ます。最小化されたウィンドウでは大きさが 0 になるので、そのときは呼ばずに戻します。

### GetCurrentBackBufferIndex {#getcurrentbackbufferindex}

```cpp
UINT IDXGISwapChain3::GetCurrentBackBufferIndex();
```

いま描くべきバック バッファの番号を返します。引数はありません。

`Present` のたびに番号が進みます（2 枚なら 0、1、0、1…）。自分で `frame % kFrameCount` と数えることもできますが、数え間違いやリサイズでの数え直しを避けるため、毎フレームこの関数で取るのが確実です。この番号は、バック バッファの配列、RTV のハンドル、コマンド アロケーターの配列のどれにも同じように使います。

### SetMaximumFrameLatency {#setmaximumframelatency}

```cpp
HRESULT IDXGISwapChain2::SetMaximumFrameLatency(UINT MaxLatency);
```

スワップ チェーンの先に積んでおけるフレームの最大数を決めます。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `MaxLatency` | `UINT` | キューに入れておけるバック バッファのフレーム数。既定は 1 |

小さいほど入力から表示までの遅れが減り、CPU の待ちが増えます。大きいほど、GPU が詰まったときに CPU が先へ進めて滑らかになる代わりに、遅れが増えます。入力の反応が大事なゲームでは 1、描画が重いゲームでは 2 を使うのが一つの目安です。

スワップ チェーンを `DXGI_SWAP_CHAIN_FLAG_FRAME_LATENCY_WAITABLE_OBJECT` を付けて作っていないと、`DXGI_ERROR_INVALID_CALL` で失敗します。デバイスが失われているときは `DXGI_ERROR_DEVICE_REMOVED` です。

### GetFrameLatencyWaitableObject {#getframelatencywaitableobject}

```cpp
HANDLE IDXGISwapChain2::GetFrameLatencyWaitableObject();
```

「次のフレームを描き始めてよい」ことを知らせるイベントのハンドルを返します。引数はありません。

これを `WaitForSingleObjectEx` で待ってから描き始めると、キューに積まれたフレームが `SetMaximumFrameLatency` の数を超えず、遅れが一定に保たれます。待つのは最初のフレームから、レンダリングする全フレームの先頭です。

```cpp
// 作成時: desc.Flags |= DXGI_SWAP_CHAIN_FLAG_FRAME_LATENCY_WAITABLE_OBJECT;
swap_chain->SetMaximumFrameLatency(1);
HANDLE latency_event = swap_chain->GetFrameLatencyWaitableObject();

// 毎フレームの先頭
WaitForSingleObjectEx(latency_event, 1000, TRUE);  // 前のフレームの表示が進むまで待つ
// ... 描く ...

// 終了時
CloseHandle(latency_event);
```

スワップ チェーンを `FRAME_LATENCY_WAITABLE_OBJECT` なしで作っていると、戻り値は `nullptr` です。ハンドルは使い終わったら `CloseHandle` で閉じます。

## よくあるミス

??? failure "リサイズで `ResizeBuffers` が失敗する"
    バック バッファの `ComPtr` を `Reset` していないか、GPU がまだ使っています。フェンスで待ってから全部手放します。

??? failure "最小化すると `ResizeBuffers` で落ちる、または黒くなる"
    最小化のとき、ウィンドウの幅と高さが 0 になります。0 のときは何もせず戻ります。

??? failure "`Present(0, DXGI_PRESENT_ALLOW_TEARING)` が失敗する"
    スワップ チェーンの作成時に `DXGI_SWAP_CHAIN_FLAG_ALLOW_TEARING` を付けていません。`ResizeBuffers` でフラグを 0 にしたときも同じです。

??? failure "`GetFrameLatencyWaitableObject` が `nullptr` を返す"
    作成時のフラグに `DXGI_SWAP_CHAIN_FLAG_FRAME_LATENCY_WAITABLE_OBJECT` がありません。

## 関連ページ

- [Swap Chain (D3D12)](../swap-chain.md)
- [IDXGIFactory](idxgifactory.md)
- [ID3D12Device](id3d12device.md#getdeviceremovedreason)
- [Microsoft Learn: IDXGISwapChain](https://learn.microsoft.com/ja-jp/windows/win32/api/dxgi/nn-dxgi-idxgiswapchain)
