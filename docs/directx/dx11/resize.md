---
title: Window Resize and Device Removal
tags:
  - DirectX
---

# Window Resize and Device Removal

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

ウィンドウの大きさを変えると、<strong>バック バッファ</strong>（とそれに合わせた深度バッファ、G バッファなど）の大きさも変えなければ画像が引き伸ばされて、ぼやけます。また、GPU のドライバーの更新やクラッシュで <strong>デバイスが失われる</strong>こともあります。このページはその 2 つの対処です。

!!! tip "ポイント"
    - `WM_SIZE` で <strong>バック バッファの参照（RTV など）をすべて、解放</strong>してから `ResizeBuffers`、その後、作り直す。
    - 参照が 1 つでも残っていると `ResizeBuffers` が失敗する。
    - 最小化（幅か高さが 0）のときは、何もしない。
    - 画面の大きさに依存する、リソース（深度、G バッファ、ポスト プロセスの中間バッファ）も全部、作り直す。
    - `Present` が `DXGI_ERROR_DEVICE_REMOVED` を返したら、デバイスごと作り直す。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

## バック バッファの作り直し

```cpp
void OnResize(UINT new_width, UINT new_height) {
  if (new_width == 0 || new_height == 0) return;           // 最小化: 何もしない
  if (new_width == width_ && new_height == height_) return;

  // ① バック バッファを参照している物をすべて、解放する（RTV、バック バッファの Texture2D）
  context_->OMSetRenderTargets(0, nullptr, nullptr);       // 束縛も外す
  rtv_.Reset();
  depth_dsv_.Reset();
  depth_texture_.Reset();
  context_->Flush();                                       // 溜まった命令を GPU に、流す

  // ② バッファの大きさを変える
  HRESULT hr = swap_chain_->ResizeBuffers(0,               // 0: バッファの数をそのまま
                                          new_width, new_height,
                                          DXGI_FORMAT_UNKNOWN,   // フォーマットをそのまま
                                          0);                    // フラグをそのまま
  if (FAILED(hr)) { /* デバイスが、失われた可能性（下の節） */ }

  width_ = new_width;
  height_ = new_height;

  // ③ 作り直す
  CreateRenderTarget();                                    // GetBuffer → RTV
  CreateDepthBuffer();                                     // 深度
  CreateScreenSizedResources();                            // G バッファ、ポスト プロセスなど
}
```

`ResizeBuffers` はスワップ チェーンのバッファへの <strong>参照が残っていると `DXGI_ERROR_INVALID_CALL` で失敗</strong>します。`GetBuffer` で取った `ID3D11Texture2D` も RTV も `OMSetRenderTargets` での束縛もすべて外してから、呼びます。

### 引数

| 引数 | 内容 |
| --- | --- |
| `BufferCount` | バッファの数。0 で今のまま |
| `Width`・`Height` | 新しい大きさ。0 でウィンドウの描画領域に合わせる |
| `NewFormat` | フォーマット。`DXGI_FORMAT_UNKNOWN` で今のまま |
| `SwapChainFlags` | 作成時のフラグと同じものを渡す |

## 画面の大きさに依存する、リソース

バック バッファ以外にも画面の大きさで作った、リソースはすべて作り直します。

| リソース | 大きさ |
| --- | --- |
| 深度バッファ | 画面と同じ |
| G バッファ（MRT） | 画面と同じ |
| HDR のシーン色 | 画面と同じ |
| ポスト プロセスの中間バッファ | 画面（または、半分・1/4） |
| TAA の履歴 | 画面と同じ（作り直したら履歴は無効。最初のフレームは履歴を使わない） |

```cpp
void CreateScreenSizedResources() {
  CreateGBuffer(width_, height_);
  CreateSceneColor(width_, height_);
  CreateBloomChain(width_, height_);
  CreateTaaHistory(width_, height_);
  taa_history_valid_ = false;                              // 履歴を捨てる（ゴースト防止）
}
```

大きさの変更をドラッグで連続して行うと `WM_SIZE` が何度も来ます。そのたびに重いリソースを作り直すとカクつくので <strong>ドラッグが終わるまで、待つ</strong>（`WM_EXITSIZEMOVE`）方法もあります。

```cpp
case WM_ENTERSIZEMOVE: resizing_ = true; return 0;         // ドラッグ開始
case WM_EXITSIZEMOVE:
  resizing_ = false;
  OnResize(client_width, client_height);                   // ドラッグ終了時に 1 回だけ
  return 0;
```

## デバイス リセット（DEVICE_REMOVED）

GPU のドライバーの更新、GPU のハングアップ（TDR: Timeout Detection and Recovery）、GPU の取り外しなどで <strong>デバイスが使えなくなる</strong>ことがあります。`Present` や `ResizeBuffers` がエラーを返します。

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
| `DXGI_ERROR_DEVICE_HUNG` | GPU が応答しなくなった（重すぎる無限ループのシェーダー） |
| `DXGI_ERROR_DEVICE_REMOVED` | GPU が取り外されたまたは、ドライバーが更新された |
| `DXGI_ERROR_DEVICE_RESET` | 不正な描画命令で、リセットされた |
| `DXGI_ERROR_DRIVER_INTERNAL_ERROR` | ドライバーの内部エラー |
| `DXGI_ERROR_INVALID_CALL` | API の使い方が間違っていた |

### 作り直し

デバイスが失われると <strong>全リソースが無効</strong>になります。デバイス、スワップ チェーン、全テクスチャ、バッファ、シェーダー、ステートを作り直します。

```cpp
void RecreateDevice() {
  ReleaseAllResources();                                    // ComPtr を全部、Reset
  CreateDevice();
  CreateSwapChain(hwnd_);
  CreateAllResources();                                     // シェーダー、メッシュ、テクスチャを読み込み直す
}
```

リソースを「作る関数」にまとめておくと起動時とリセット時で同じコードを使えます。製品ではゲームの状態は保つ（シーンは、そのまま）ように作ります。

## 最小化・フォーカスの扱い

| 状態 | 対処 |
| --- | --- |
| 最小化（`SIZE_MINIMIZED`） | 描画を止める。バック バッファは作り直さない |
| 最小化から復帰（`SIZE_RESTORED`） | 大きさが、変わっていれば作り直す |
| `Present` が `DXGI_STATUS_OCCLUDED` | ウィンドウが隠れている。描画をスキップして少し待つ |
| フォーカスを失う | 必要なら更新を一時停止 |

## フルスクリーン

`IDXGISwapChain::SetFullscreenState`（排他フルスクリーン）は古い方法で問題が多いです。現在は <strong>ボーダーレス ウィンドウ</strong>（枠なしで、画面全体の大きさのウィンドウ）が標準で、フリップ モデルのスワップ チェーンは、これでも独占に近い低遅延で動きます。

```cpp
// ボーダーレス フルスクリーンへの、切り替え: ウィンドウのスタイルを変えて、モニター全体に広げる。
SetWindowLongPtrW(hwnd, GWL_STYLE, WS_POPUP | WS_VISIBLE);
MONITORINFO mi = {sizeof(mi)};
GetMonitorInfoW(MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST), &mi);
SetWindowPos(hwnd, HWND_TOP, mi.rcMonitor.left, mi.rcMonitor.top,
             mi.rcMonitor.right - mi.rcMonitor.left, mi.rcMonitor.bottom - mi.rcMonitor.top,
             SWP_FRAMECHANGED | SWP_SHOWWINDOW);
// この後、WM_SIZE が来て、OnResize が、バック バッファを作り直す。
```

## よくあるミス

??? failure "`ResizeBuffers` が `DXGI_ERROR_INVALID_CALL` で、失敗する"
    バック バッファへの参照（RTV、`GetBuffer` で取った `Texture2D`、`OMSetRenderTargets` の束縛）が残っている。全部、解放してから呼ぶ。

??? failure "大きさを変えると画像が引き伸ばされて、ぼやける"
    `ResizeBuffers` を呼んでいない（スワップ チェーンの大きさが変わらない）。または、深度・G バッファを作り直していない。

??? failure "最小化すると、クラッシュする"
    幅か高さが 0 のサイズで `ResizeBuffers` やテクスチャを作ろうとしている。`WM_SIZE` で 0 を除く。

??? failure "リサイズの直後に TAA のゴーストが出る"
    履歴を作り直した後も古い内容を使っている。履歴を無効にして最初のフレームは今のフレームだけで描く。

??? failure "ドライバーの更新後に画面が固まる"
    `Present` の戻り値を見ていない。`DEVICE_REMOVED` を検出してデバイスを作り直す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 大きさ変更は `WM_SIZE` → 参照を全部解放 → `ResizeBuffers` → 作り直す
    - [x] 最小化（幅か高さが 0）は、何もしない
    - [x] 画面の大きさに依存する全リソースを作り直す。TAA の履歴は捨てる
    - [x] `Present` の戻り値で `DEVICE_REMOVED` を検出し `GetDeviceRemovedReason` で原因をログに出す
    - [x] リソースの作成を関数にまとめて再作成に備える
    - [x] フルスクリーンは、ボーダーレス ウィンドウが標準

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Swap Chain](swap-chain.md)
- [Clear and Present](clear-present.md)
- [Win32 Window and Message Loop](window.md)
- [Microsoft Learn: IDXGISwapChain::ResizeBuffers](https://learn.microsoft.com/ja-jp/windows/win32/api/dxgi/nf-dxgi-idxgiswapchain-resizebuffers)
