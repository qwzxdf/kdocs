---
title: Window Resize and Device Removal
tags:
  - DirectX
---

# Window Resize and Device Removal

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

ウィンドウの大きさを、変えると、<strong>バック バッファ</strong>（と、それに合わせた、深度バッファ、G バッファなど）の、大きさも、変えなければ、画像が、引き伸ばされて、ぼやけます。また、GPU の、ドライバーの、更新や、クラッシュで、<strong>デバイスが、失われる</strong>ことも、あります。このページは、その、2 つの、対処です。

!!! tip "ポイント"
    - `WM_SIZE` で、<strong>バック バッファの参照（RTV など）を、すべて、解放</strong>してから、`ResizeBuffers`、その後、作り直す。
    - 参照が、1 つでも、残っていると、`ResizeBuffers` が、失敗する。
    - 最小化（幅か高さが 0）のときは、何もしない。
    - 画面の大きさに、依存する、リソース（深度、G バッファ、ポスト プロセスの、中間バッファ）も、全部、作り直す。
    - `Present` が `DXGI_ERROR_DEVICE_REMOVED` を、返したら、デバイスごと、作り直す。

## バック バッファの、作り直し

```cpp
void OnResize(UINT new_width, UINT new_height) {
  if (new_width == 0 || new_height == 0) return;           // 最小化: 何もしない
  if (new_width == width_ && new_height == height_) return;

  // ① バック バッファを、参照している物を、すべて、解放する（RTV、バック バッファの Texture2D）
  context_->OMSetRenderTargets(0, nullptr, nullptr);       // 束縛も外す
  rtv_.Reset();
  depth_dsv_.Reset();
  depth_texture_.Reset();
  context_->Flush();                                       // 溜まった命令を、GPU に、流す

  // ② バッファの大きさを、変える
  HRESULT hr = swap_chain_->ResizeBuffers(0,               // 0: バッファの数を、そのまま
                                          new_width, new_height,
                                          DXGI_FORMAT_UNKNOWN,   // フォーマットを、そのまま
                                          0);                    // フラグを、そのまま
  if (FAILED(hr)) { /* デバイスが、失われた可能性（下の節） */ }

  width_ = new_width;
  height_ = new_height;

  // ③ 作り直す
  CreateRenderTarget();                                    // GetBuffer → RTV
  CreateDepthBuffer();                                     // 深度
  CreateScreenSizedResources();                            // G バッファ、ポスト プロセスなど
}
```

`ResizeBuffers` は、スワップ チェーンの、バッファへの、<strong>参照が、残っていると、`DXGI_ERROR_INVALID_CALL` で失敗</strong>します。`GetBuffer` で取った、`ID3D11Texture2D` も、RTV も、`OMSetRenderTargets` での、束縛も、すべて、外してから、呼びます。

### 引数

| 引数 | 内容 |
| --- | --- |
| `BufferCount` | バッファの数。0 で、今のまま |
| `Width`・`Height` | 新しい大きさ。0 で、ウィンドウの、描画領域に、合わせる |
| `NewFormat` | フォーマット。`DXGI_FORMAT_UNKNOWN` で、今のまま |
| `SwapChainFlags` | 作成時の、フラグと、同じものを、渡す |

## 画面の大きさに、依存する、リソース

バック バッファ以外にも、画面の大きさで、作った、リソースは、すべて、作り直します。

| リソース | 大きさ |
| --- | --- |
| 深度バッファ | 画面と同じ |
| G バッファ（MRT） | 画面と同じ |
| HDR のシーン色 | 画面と同じ |
| ポスト プロセスの、中間バッファ | 画面（または、半分・1/4） |
| TAA の履歴 | 画面と同じ（作り直したら、履歴は、無効。最初のフレームは、履歴を、使わない） |

```cpp
void CreateScreenSizedResources() {
  CreateGBuffer(width_, height_);
  CreateSceneColor(width_, height_);
  CreateBloomChain(width_, height_);
  CreateTaaHistory(width_, height_);
  taa_history_valid_ = false;                              // 履歴を捨てる（ゴースト防止）
}
```

大きさの変更を、ドラッグで、連続して、行うと、`WM_SIZE` が、何度も、来ます。そのたびに、重いリソースを、作り直すと、カクつくので、<strong>ドラッグが、終わるまで、待つ</strong>（`WM_EXITSIZEMOVE`）方法も、あります。

```cpp
case WM_ENTERSIZEMOVE: resizing_ = true; return 0;         // ドラッグ開始
case WM_EXITSIZEMOVE:
  resizing_ = false;
  OnResize(client_width, client_height);                   // ドラッグ終了時に、1 回だけ
  return 0;
```

## デバイス リセット（DEVICE_REMOVED）

GPU のドライバーの更新、GPU の、ハングアップ（TDR: Timeout Detection and Recovery）、GPU の取り外し、などで、<strong>デバイスが、使えなくなる</strong>ことが、あります。`Present` や `ResizeBuffers` が、エラーを、返します。

```cpp
HRESULT hr = swap_chain_->Present(1, 0);
if (hr == DXGI_ERROR_DEVICE_REMOVED || hr == DXGI_ERROR_DEVICE_RESET) {
  HRESULT reason = device_->GetDeviceRemovedReason();      // 原因を取る（ログに出す）
  LogError("Device removed: 0x%08X", reason);
  RecreateDevice();                                         // デバイスから、全部作り直す
}
```

| `GetDeviceRemovedReason` の値 | 内容 |
| --- | --- |
| `DXGI_ERROR_DEVICE_HUNG` | GPU が、応答しなくなった（重すぎる、無限ループのシェーダー） |
| `DXGI_ERROR_DEVICE_REMOVED` | GPU が、取り外された、または、ドライバーが、更新された |
| `DXGI_ERROR_DEVICE_RESET` | 不正な描画命令で、リセットされた |
| `DXGI_ERROR_DRIVER_INTERNAL_ERROR` | ドライバーの、内部エラー |
| `DXGI_ERROR_INVALID_CALL` | API の、使い方が、間違っていた |

### 作り直し

デバイスが、失われると、<strong>全リソースが、無効</strong>に、なります。デバイス、スワップ チェーン、全テクスチャ、バッファ、シェーダー、ステートを、作り直します。

```cpp
void RecreateDevice() {
  ReleaseAllResources();                                    // ComPtr を全部、Reset
  CreateDevice();
  CreateSwapChain(hwnd_);
  CreateAllResources();                                     // シェーダー、メッシュ、テクスチャを、読み込み直す
}
```

リソースを、「作る関数」に、まとめておくと、起動時と、リセット時で、同じコードを、使えます。製品では、ゲームの、状態は、保つ（シーンは、そのまま）ように、作ります。

## 最小化・フォーカスの、扱い

| 状態 | 対処 |
| --- | --- |
| 最小化（`SIZE_MINIMIZED`） | 描画を、止める。バック バッファは、作り直さない |
| 最小化から、復帰（`SIZE_RESTORED`） | 大きさが、変わっていれば、作り直す |
| `Present` が `DXGI_STATUS_OCCLUDED` | ウィンドウが、隠れている。描画を、スキップして、少し待つ |
| フォーカスを失う | 必要なら、更新を、一時停止 |

## フルスクリーン

`IDXGISwapChain::SetFullscreenState`（排他フルスクリーン）は、古い方法で、問題が、多いです。現在は、<strong>ボーダーレス ウィンドウ</strong>（枠なしで、画面全体の大きさの、ウィンドウ）が、標準で、フリップ モデルの、スワップ チェーンは、これでも、独占に近い、低遅延で、動きます。

```cpp
// ボーダーレス フルスクリーンへの、切り替え: ウィンドウのスタイルを変えて、モニター全体に広げる。
SetWindowLongPtrW(hwnd, GWL_STYLE, WS_POPUP | WS_VISIBLE);
MONITORINFO mi = {sizeof(mi)};
GetMonitorInfoW(MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST), &mi);
SetWindowPos(hwnd, HWND_TOP, mi.rcMonitor.left, mi.rcMonitor.top,
             mi.rcMonitor.right - mi.rcMonitor.left, mi.rcMonitor.bottom - mi.rcMonitor.top,
             SWP_FRAMECHANGED | SWP_SHOWWINDOW);
// この後、WM_SIZE が来て、OnResize が、バック バッファを、作り直す。
```

## よくあるミス

??? failure "`ResizeBuffers` が、`DXGI_ERROR_INVALID_CALL` で、失敗する"
    バック バッファへの、参照（RTV、`GetBuffer` で取った `Texture2D`、`OMSetRenderTargets` の束縛）が、残っている。全部、解放してから、呼ぶ。

??? failure "大きさを、変えると、画像が、引き伸ばされて、ぼやける"
    `ResizeBuffers` を、呼んでいない（スワップ チェーンの、大きさが、変わらない）。または、深度・G バッファを、作り直していない。

??? failure "最小化すると、クラッシュする"
    幅か高さが 0 の、サイズで、`ResizeBuffers` や、テクスチャを、作ろうとしている。`WM_SIZE` で、0 を、除く。

??? failure "リサイズの、直後に、TAA の、ゴーストが、出る"
    履歴を、作り直した後も、古い内容を、使っている。履歴を、無効にして、最初のフレームは、今のフレームだけで、描く。

??? failure "ドライバーの、更新後に、画面が、固まる"
    `Present` の、戻り値を、見ていない。`DEVICE_REMOVED` を、検出して、デバイスを、作り直す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 大きさ変更は、`WM_SIZE` → 参照を全部解放 → `ResizeBuffers` → 作り直す
    - [x] 最小化（幅か高さが 0）は、何もしない
    - [x] 画面の大きさに、依存する、全リソースを、作り直す。TAA の、履歴は、捨てる
    - [x] `Present` の戻り値で、`DEVICE_REMOVED` を、検出し、`GetDeviceRemovedReason` で、原因を、ログに出す
    - [x] リソースの作成を、関数に、まとめて、再作成に備える
    - [x] フルスクリーンは、ボーダーレス ウィンドウが、標準

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Swap Chain](swap-chain.md)
- [Clear and Present](clear-present.md)
- [Win32 Window and Message Loop](window.md)
- [Microsoft Learn: IDXGISwapChain::ResizeBuffers](https://learn.microsoft.com/ja-jp/windows/win32/api/dxgi/nf-dxgi-idxgiswapchain-resizebuffers)
