---
title: Swap Chain
tags:
  - DirectX
---

# Swap Chain

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>スワップ チェーン</strong>は画面に出す画像の、入れ替えの仕組みです。GPU が次のフレームを描いている間に、前のフレームを画面に出すというふうに、<strong>2 枚以上の画像（バック バッファ）を、交代で</strong>使います。1 枚だけだと描きかけの画像が、画面に出てしまいます。

!!! tip "ポイント"
    - スワップ チェーンは、<strong>ウィンドウに結びついたバック バッファの束</strong>。`Present` で描いた画像を画面へ出す。
    - 今の標準は <strong>フリップ モデル</strong>（`DXGI_SWAP_EFFECT_FLIP_DISCARD`）。バッファは 2 枚以上。
    - フリップ モデルでは、スワップ チェーンのフォーマットに `_SRGB` を、指定できない。<strong>`R8G8B8A8_UNORM` で作り RTV を `_SRGB` で作る</strong>。
    - 作成は `IDXGIFactory2::CreateSwapChainForHwnd`。ファクトリーはデバイスから辿る。
    - 大きさを 0 にすると、ウィンドウの描画領域に合わせてくれる。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

## 作る

```cpp
#include <dxgi1_2.h>

DXGI_SWAP_CHAIN_DESC1 desc = {};
desc.Width = 0;                                            // 0 = ウィンドウの描画領域の大きさ
desc.Height = 0;
desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;                  // フリップ モデルは、_SRGB を指定できない
desc.SampleDesc.Count = 1;                                 // フリップ モデルは、MSAA 不可（1 固定）
desc.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;        // レンダー ターゲットとして使う
desc.BufferCount = 2;                                      // バック バッファの数（フリップは 2 以上）
desc.SwapEffect = DXGI_SWAP_EFFECT_FLIP_DISCARD;           // フリップ モデル（推奨）
desc.Scaling = DXGI_SCALING_STRETCH;
desc.AlphaMode = DXGI_ALPHA_MODE_IGNORE;
desc.Flags = 0;
```

| メンバー | 内容 |
| --- | --- |
| `Width`・`Height` | バック バッファの大きさ。0 でウィンドウの描画領域に、合わせる |
| `Format` | バック バッファの形式。`R8G8B8A8_UNORM`、HDR なら `R16G16B16A16_FLOAT`、`R10G10B10A2_UNORM` |
| `SampleDesc` | 常に `{1, 0}`。MSAA は別のレンダー ターゲットで描いて、`ResolveSubresource` する |
| `BufferUsage` | `RENDER_TARGET_OUTPUT`（描く先）。計算シェーダーで書くなら `UNORDERED_ACCESS` も |
| `BufferCount` | バッファの数。2（ダブル）か 3（トリプル） |
| `SwapEffect` | `FLIP_DISCARD`（標準）、`FLIP_SEQUENTIAL`（前の内容を保つ）。古い `DISCARD` と `SEQUENTIAL` はビット ブリット モデル |
| `Flags` | `ALLOW_TEARING`（垂直同期なしの表示）、`FRAME_LATENCY_WAITABLE_OBJECT`（遅延の制御） |

### フリップ モデルとビット ブリット モデル

| | フリップ モデル（`FLIP_*`） | ビット ブリット モデル（`DISCARD`、`SEQUENTIAL`） |
| --- | --- | --- |
| 画面への出し方 | バッファを、そのまま画面に出す（コピー無し） | バッファを画面に、コピーする |
| 速さ・遅延 | 速い遅延が小さい | 遅い |
| MSAA | 不可 | 可 |
| `_SRGB` フォーマット | 不可 | 可 |
| 今の推奨 | <strong>こちら</strong> | 古い |

MSAA が使えない点は困りませんが別の、レンダー ターゲットに MSAA で描いて、バック バッファへ `ResolveSubresource` します（[Multiple Render Targets](mrt.md)）。

```cpp
Microsoft::WRL::ComPtr<IDXGISwapChain1> swap_chain;
factory2->CreateSwapChainForHwnd(device.Get(),             // D3D11 のデバイス（コマンド キュー代わり）
                                 hwnd, &desc,
                                 nullptr,                  // フルスクリーンの設定（使わない）
                                 nullptr,                  // 出力の制限（使わない）
                                 &swap_chain);

factory2->MakeWindowAssociation(hwnd, DXGI_MWA_NO_ALT_ENTER);   // Alt+Enter での、DXGI 任せのフルスクリーンを、無効にする
```

`factory2` はデバイスから辿ったもの（[DXGI Factory and Adapter](dxgi.md)）です。`MakeWindowAssociation` で `Alt + Enter` の自動フルスクリーン切り替えを、無効にします（ゲーム側で制御するため）。

## バック バッファを取り出す

```cpp
Microsoft::WRL::ComPtr<ID3D11Texture2D> back_buffer;
swap_chain->GetBuffer(0, IID_PPV_ARGS(&back_buffer));      // 0 番のバッファ（フリップ モデルは、常に 0 番に描く）
```

フリップ モデルでは <strong>常にバッファ 0 番</strong>に、描きます。`Present` のたびに裏でバッファが入れ替わり `GetBuffer(0)` が今の、描き先を指します。バック バッファは普通の `ID3D11Texture2D` なので、ビュー（[Render Target View (RTV)](render-target-view.md)）を作って、描き込みます。

## Present

```cpp
swap_chain->Present(1, 0);                                 // 垂直同期を待って、画面に出す
```

`Present` の使い方は[Clear and Present](clear-present.md) です。

## sRGB とリニアの扱い

フリップ モデルのスワップ チェーンの、フォーマットは `R8G8B8A8_UNORM` ですが <strong>RTV を、`R8G8B8A8_UNORM_SRGB` で作る</strong>とシェーダーがリニアの値を、書いたときハードウェアが自動で、sRGB に変換して書き込みます。

```cpp
D3D11_RENDER_TARGET_VIEW_DESC rtv_desc = {};
rtv_desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;         // 書くときに、リニア → sRGB へ、自動変換
rtv_desc.ViewDimension = D3D11_RTV_DIMENSION_TEXTURE2D;
device->CreateRenderTargetView(back_buffer.Get(), &rtv_desc, &rtv);
```

バック バッファ自体は `UNORM` でも、ビューを `UNORM_SRGB` にできるのは同じ、ビット幅のフォーマット同士（`R8G8B8A8_UNORM` と `_UNORM_SRGB`）が、同じ「型のファミリー」だからです（[Formats and Typeless](../concepts/formats.md)）。

## HDR 出力

HDR のモニターへの出力は `R16G16B16A16_FLOAT` と、色空間（`DXGI_COLOR_SPACE_RGB_FULL_G10_NONE_P709`）の設定が必要です。`IDXGISwapChain3::SetColorSpace1` で色空間を指定します。詳しくは[Gamma and sRGB](../../graphics/postprocess/tonemapping/gamma-srgb.md) を、参照してください。

## よくあるミス

??? failure "`CreateSwapChainForHwnd` が、`E_INVALIDARG` で失敗する"
    フリップ モデルで `_SRGB` の、フォーマットや `SampleDesc.Count > 1`、`BufferCount < 2` を指定している。

??? failure "画面が、暗い・明るすぎる（ガンマがおかしい）"
    リニアの値を sRGB に、変換せずに書いている。RTV を `_SRGB` で作るかシェーダーで、`pow(x, 1/2.2)` する。両方やると二重に変換される。

??? failure "Alt+Enter で画面が、おかしくなる"
    DXGI の自動フルスクリーン切り替えが、有効のまま。`MakeWindowAssociation(hwnd, DXGI_MWA_NO_ALT_ENTER)` で無効にする。

??? failure "描き込んでも画面に、反映されない"
    `GetBuffer` で取ったバック バッファの、RTV を `OMSetRenderTargets` に束ねていない。または、`Present` を呼んでいない。

## これだけ覚える

!!! abstract "まとめ"
    - [x] スワップ チェーン＝画面に出す画像の、入れ替え機構
    - [x] 標準はフリップ モデル（`FLIP_DISCARD`、`BufferCount = 2`）
    - [x] フリップ モデルは、`_SRGB` 不可・MSAA 不可。RTV を `_SRGB` にする
    - [x] `GetBuffer(0)` でバック バッファを取り、RTV を作る
    - [x] 画面に出すのは `Present`

## 関連ページ

- [DirectX 11 Guide](index.md)
- [DXGI Factory and Adapter](dxgi.md)
- [Render Target View (RTV)](render-target-view.md)
- [Clear and Present](clear-present.md)
- [Window Resize and Device Removal](resize.md)
- [Microsoft Learn: スワップ チェーン](https://learn.microsoft.com/ja-jp/windows/win32/direct3ddxgi/d3d10-graphics-programming-guide-dxgi#swap-chains)
