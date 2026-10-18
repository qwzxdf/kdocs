---
title: Clear and Present
tags:
  - DirectX
---

# Clear and Present

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

1 フレームの、最初に、<strong>画面を、塗りつぶし</strong>（`Clear`）、最後に、<strong>画面に出す</strong>（`Present`）。この 2 つで、フレームが、閉じます。ここまでの、ページで、作った、デバイス、スワップ チェーン、RTV を、使うと、<strong>単色で、塗りつぶした、ウィンドウ</strong>が、表示されます。D3D11 の、最初の、動作確認です。

!!! tip "ポイント"
    - `ClearRenderTargetView` で、レンダー ターゲットを、1 色で、塗る。深度は、`ClearDepthStencilView`。
    - `Present(1, 0)` は、垂直同期（モニターの、更新）を、待つ。`Present(0, 0)` は、待たない。
    - フリップ モデルの、`Present` の後は、レンダー ターゲットの束縛が、外れる。<strong>毎フレーム、`OMSetRenderTargets` を、呼び直す</strong>。
    - 毎フレームの、骨格は、「束ねる → 消す → 描く → 出す」。

## 1 フレームの骨格

```cpp
void RenderFrame() {
  // ① 描き込み先を、パイプラインに、つなぐ（フリップ モデルは、Present のたびに、外れる）
  ID3D11RenderTargetView* targets[] = {rtv.Get()};
  context->OMSetRenderTargets(1, targets, nullptr);

  // ② ビューポートを、設定する（viewport.md）
  D3D11_VIEWPORT viewport = {0.0f, 0.0f, static_cast<float>(width), static_cast<float>(height), 0.0f, 1.0f};
  context->RSSetViewports(1, &viewport);

  // ③ 画面を、塗りつぶす
  const float clear_color[4] = {0.1f, 0.2f, 0.4f, 1.0f};     // RGBA。リニア値（RTV が _SRGB なら、自動で変換）
  context->ClearRenderTargetView(rtv.Get(), clear_color);

  // ④ ここで、描く（triangle.md）

  // ⑤ 画面に出す
  swap_chain->Present(1, 0);
}
```

①の `OMSetRenderTargets` を、毎フレーム、呼ぶのは、フリップ モデルが、`Present` の後に、束縛を、解除するからです。呼び忘れると、2 フレーム目から、何も、描かれません。

## ClearRenderTargetView

```cpp
const float color[4] = {0.0f, 0.0f, 0.0f, 1.0f};
context->ClearRenderTargetView(rtv.Get(), color);
```

| 引数 | 内容 |
| --- | --- |
| `pRenderTargetView` | 塗る、RTV |
| `ColorRGBA` | 4 つの `float`（R、G、B、A） |

RTV の、フォーマットが `_SRGB` のとき、`color` は、<strong>リニア</strong>の値と、解釈され、sRGB に、変換されて、書かれます。見た目の色（0.5 グレー）を、出したいときは、`pow(0.5, 2.2) ≈ 0.22` を、渡します。

## ClearDepthStencilView

```cpp
context->ClearDepthStencilView(dsv.Get(), D3D11_CLEAR_DEPTH | D3D11_CLEAR_STENCIL,
                               1.0f,       // 深度の初期値（1.0 = 最も遠い）
                               0);         // ステンシルの初期値
```

深度は、`1.0` で、塗る（最も遠い、として、すべての物を、描ける状態）。深度バッファは、<strong>毎フレーム、必ず、クリア</strong>します（[Depth Buffer and DSV](depth-stencil.md)）。

## Present

```cpp
HRESULT hr = swap_chain->Present(sync_interval, flags);
```

| 引数 | 内容 |
| --- | --- |
| `SyncInterval` | 0 = 垂直同期を待たず、すぐ表示（ティアリングの、恐れ）。1 = モニターの更新を 1 回待つ（60Hz なら、1/60 秒）。2 = 2 回待つ |
| `Flags` | 0、または、`DXGI_PRESENT_ALLOW_TEARING`（ティアリング許可のスワップ チェーンで、`SyncInterval = 0` の、とき） |

| 設定 | 動き |
| --- | --- |
| `Present(1, 0)` | 垂直同期。フレームレートが、モニターに、合う。ティアリング無し。遅延は、やや大きい |
| `Present(0, DXGI_PRESENT_ALLOW_TEARING)` | 最速。ティアリング有り。可変リフレッシュレートの、モニターで、有用 |

### Present が返す、エラー

```cpp
if (hr == DXGI_ERROR_DEVICE_REMOVED || hr == DXGI_ERROR_DEVICE_RESET) {
  // GPU が、リセットされた、または、取り外された。デバイスを、作り直す（resize.md）。
} else if (hr == DXGI_STATUS_OCCLUDED) {
  // ウィンドウが、隠れている（最小化など）。描かずに、少し待つ。
}
```

`Present` の、戻り値は、必ず、確認します。GPU の、ドライバーの、クラッシュや、更新で、デバイスが、失われると、`DEVICE_REMOVED` が、返り、デバイスを、作り直す、必要が、あります（[Window Resize and Device Removal](resize.md)）。

## 毎フレームの、束縛

D3D11 は、「状態を、持つ」API で、一度、設定した、束縛は、次の、設定まで、残ります。ただし、次の、場面では、設定し直します。

| 場面 | 理由 |
| --- | --- |
| フリップ モデルの `Present` の後 | レンダー ターゲットの、束縛が、外れる |
| 別のパスの前 | 別のパスは、別の、シェーダー・リソース・ステートが、必要 |
| リソースの、読み書きを、切り替えるとき | 読みながら、書けない（[Render Target View (RTV)](render-target-view.md)） |

`context->ClearState()` で、全束縛を、外せますが、毎フレーム呼ぶと、遅いので、フレームの、最初と、最後には、使いません。

## フレームレートの、制御

`Present(1, 0)` で、モニターの、リフレッシュレート（60Hz なら 60 FPS）に、合わせるのが、基本です。ゲームの、更新を、固定の、時間刻みで、行うときは、経過時間を、`QueryPerformanceCounter` で、測ります。

```cpp
#include <chrono>

auto previous = std::chrono::steady_clock::now();
// ループの中:
auto now = std::chrono::steady_clock::now();
float delta_seconds = std::chrono::duration<float>(now - previous).count();
previous = now;
```

## よくあるミス

??? failure "最初のフレームは、描けるのに、2 フレーム目から、真っ黒になる"
    フリップ モデルで、`OMSetRenderTargets` を、毎フレーム、呼んでいない。`Present` の後、束縛が、外れる。

??? failure "物が、前のフレームと、重なって、見える"
    深度バッファを、クリアしていない（古い深度が、残って、新しい描画を、はじく）。または、`ClearRenderTargetView` を、呼んでいない。

??? failure "フレームレートが、60 を、超えて、ティアリングが出る"
    `Present(0, …)` で、垂直同期を、切っている。通常は、`Present(1, 0)`。

??? failure "GPU の、更新後に、突然、描画されなくなる"
    `Present` の戻り値（`DXGI_ERROR_DEVICE_REMOVED`）を、見ていない。デバイスを、作り直す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 毎フレーム: 束ねる → ビューポート → Clear → 描く → Present
    - [x] `ClearRenderTargetView`（色）、`ClearDepthStencilView`（深度 1.0）
    - [x] `Present(1, 0)` が、垂直同期あり。0 は、待たない
    - [x] フリップ モデルは、`Present` の後に、束縛が外れる
    - [x] `Present` の戻り値を、確認する

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Render Target View (RTV)](render-target-view.md)
- [Viewport](viewport.md)
- [Swap Chain](swap-chain.md)
- [Window Resize and Device Removal](resize.md)
- [Microsoft Learn: IDXGISwapChain::Present](https://learn.microsoft.com/ja-jp/windows/win32/api/dxgi/nf-dxgi-idxgiswapchain-present)
