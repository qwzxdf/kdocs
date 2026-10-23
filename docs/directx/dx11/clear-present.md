---
title: Clear and Present
tags:
  - DirectX
---

# Clear and Present

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

1 フレームの最初に <strong>画面を塗りつぶし</strong>（`Clear`）、最後に <strong>画面に出す</strong>（`Present`）。この 2 つでフレームが閉じます。ここまでのページで作ったデバイス、スワップ チェーン、RTV を使うと <strong>単色で塗りつぶしたウィンドウ</strong>が表示されます。D3D11 の最初の動作確認です。

!!! tip "ポイント"
    - `ClearRenderTargetView` でレンダー ターゲットを 1 色で塗る。深度は `ClearDepthStencilView`。
    - `Present(1, 0)` は垂直同期（モニターの更新）を待つ。`Present(0, 0)` は待たない。
    - フリップ モデルの `Present` の後はレンダー ターゲットの束縛が、外れる。<strong>毎フレーム、`OMSetRenderTargets` を呼び直す</strong>。
    - 毎フレームの骨格は「束ねる → 消す → 描く → 出す」。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

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

①の `OMSetRenderTargets` を毎フレーム、呼ぶのはフリップ モデルが `Present` の後に束縛を解除するからです。呼び忘れると 2 フレーム目から何も描かれません。

## ClearRenderTargetView

```cpp
const float color[4] = {0.0f, 0.0f, 0.0f, 1.0f};
context->ClearRenderTargetView(rtv.Get(), color);
```

| 引数 | 内容 |
| --- | --- |
| `pRenderTargetView` | 塗る RTV |
| `ColorRGBA` | 4 つの `float`（R、G、B、A） |

RTV のフォーマットが `_SRGB` のとき `color` は、<strong>リニア</strong>の値と解釈され sRGB に変換されて書かれます。見た目の色（0.5 グレー）を出したいときは `pow(0.5, 2.2) ≈ 0.22` を渡します。

## ClearDepthStencilView

```cpp
context->ClearDepthStencilView(dsv.Get(), D3D11_CLEAR_DEPTH | D3D11_CLEAR_STENCIL,
                               1.0f,       // 深度の初期値（1.0 = 最も遠い）
                               0);         // ステンシルの初期値
```

深度は `1.0` で塗る（最も遠いとして、すべての物を描ける状態）。深度バッファは <strong>毎フレーム、必ずクリア</strong>します（[Depth Buffer and DSV](depth-stencil.md)）。

## Present

```cpp
HRESULT hr = swap_chain->Present(sync_interval, flags);
```

| 引数 | 内容 |
| --- | --- |
| `SyncInterval` | 0 = 垂直同期を待たずすぐ表示（ティアリングの恐れ）。1 = モニターの更新を 1 回待つ（60Hz なら 1/60 秒）。2 = 2 回待つ |
| `Flags` | 0、または `DXGI_PRESENT_ALLOW_TEARING`（ティアリング許可のスワップ チェーンで `SyncInterval = 0` のとき） |

| 設定 | 動き |
| --- | --- |
| `Present(1, 0)` | 垂直同期。フレームレートがモニターに合う。ティアリング無し。遅延はやや大きい |
| `Present(0, DXGI_PRESENT_ALLOW_TEARING)` | 最速。ティアリング有り。可変リフレッシュレートのモニターで、有用 |

### Present が返すエラー

```cpp
if (hr == DXGI_ERROR_DEVICE_REMOVED || hr == DXGI_ERROR_DEVICE_RESET) {
  // GPU が、リセットされた、または、取り外された。デバイスを、作り直す（resize.md）。
} else if (hr == DXGI_STATUS_OCCLUDED) {
  // ウィンドウが、隠れている（最小化など）。描かずに、少し待つ。
}
```

`Present` の戻り値は必ず確認します。GPU のドライバーのクラッシュや更新で、デバイスが失われると `DEVICE_REMOVED` が返りデバイスを作り直す必要があります（[Window Resize and Device Removal](resize.md)）。

## 毎フレームの束縛

D3D11 は「状態を持つ」API で一度、設定した束縛は次の設定まで残ります。ただし、次の場面では設定し直します。

| 場面 | 理由 |
| --- | --- |
| フリップ モデルの `Present` の後 | レンダー ターゲットの束縛が、外れる |
| 別のパスの前 | 別のパスは別のシェーダー・リソース・ステートが、必要 |
| リソースの読み書きを切り替えるとき | 読みながら、書けない（[Render Target View (RTV)](render-target-view.md)） |

`context->ClearState()` で全束縛を外せますが毎フレーム呼ぶと遅いのでフレームの最初と最後には、使いません。

## フレームレートの制御

`Present(1, 0)` でモニターのリフレッシュレート（60Hz なら 60 FPS）に合わせるのが基本です。ゲームの更新を固定の時間刻みで、行うときは経過時間を `QueryPerformanceCounter` で測ります。

```cpp
#include <chrono>

auto previous = std::chrono::steady_clock::now();
// ループの中:
auto now = std::chrono::steady_clock::now();
float delta_seconds = std::chrono::duration<float>(now - previous).count();
previous = now;
```

## よくあるミス

??? failure "最初のフレームは、描けるのに 2 フレーム目から、真っ黒になる"
    フリップ モデルで `OMSetRenderTargets` を毎フレーム、呼んでいない。`Present` の後、束縛が外れる。

??? failure "物が、前のフレームと重なって見える"
    深度バッファをクリアしていない（古い深度が残って、新しい描画をはじく）。または、`ClearRenderTargetView` を呼んでいない。

??? failure "フレームレートが、60 を超えてティアリングが出る"
    `Present(0, …)` で垂直同期を切っている。通常は、`Present(1, 0)`。

??? failure "GPU の更新後に突然、描画されなくなる"
    `Present` の戻り値（`DXGI_ERROR_DEVICE_REMOVED`）を見ていない。デバイスを作り直す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 毎フレーム: 束ねる → ビューポート → Clear → 描く → Present
    - [x] `ClearRenderTargetView`（色）、`ClearDepthStencilView`（深度 1.0）
    - [x] `Present(1, 0)` が垂直同期あり。0 は待たない
    - [x] フリップ モデルは、`Present` の後に束縛が外れる
    - [x] `Present` の戻り値を確認する

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Render Target View (RTV)](render-target-view.md)
- [Viewport](viewport.md)
- [Swap Chain](swap-chain.md)
- [Window Resize and Device Removal](resize.md)
- [Microsoft Learn: IDXGISwapChain::Present](https://learn.microsoft.com/ja-jp/windows/win32/api/dxgi/nf-dxgi-idxgiswapchain-present)
