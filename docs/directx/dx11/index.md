---
title: DirectX 11 Guide
tags:
  - DirectX
---

# DirectX 11 Guide

<strong>DirectX 11（Direct3D 11、D3D11）</strong>は Windows で GPU を使って、3D を描く API です。このサイトの描画のコードは DirectX 11 を前提にしています。このセクションは <strong>ウィンドウを開くところから三角形、テクスチャ、深度、計算シェーダーまで</strong>を 1 つずつ自分のコードで動かしながら説明します。DirectX 12 を知らなくても、読めます（[DirectX 12 Guide](../dx12/index.md) とは、別の系列です）。

## この API の考え方

D3D11 は <strong>ドライバーが、面倒を見てくれる API</strong>です。GPU のメモリの置き場所、描画コマンドの順序、リソースの読み書きの衝突の整理をドライバーが裏でやります。そのぶん書くコードは少なく実行時のオーバーヘッドは、DirectX 12 より大きくなります。

| 登場する物 | 役割 |
| --- | --- |
| [ID3D11Device](device.md) | GPU にリソース（バッファ、テクスチャ）やシェーダーを作らせる |
| [ID3D11DeviceContext](device.md#device-context) | 描画や計算の命令を出す |
| [Swap Chain](swap-chain.md) | 画面に出す画像（バック バッファ）の入れ替え |
| ビュー（[RTV](render-target-view.md)、[SRV](shader-resource-view.md)、[UAV](uav.md)、[DSV](depth-stencil.md)） | 1 つのリソースを用途ごとに見る窓 |
| ステート（[ラスタライザー](rasterizer-state.md)、[ブレンド](blend-state.md)、[深度ステンシル](depth-stencil-state.md)、[サンプラー](sampler-state.md)） | 固定機能の設定 |

## 読む順番

| 段階 | ページ |
| --- | --- |
| ① 画面を出す | [Win32 Window and Message Loop](window.md) → [ID3D11Device and Device Context](device.md) → [DXGI Factory and Adapter](dxgi.md) → [Swap Chain](swap-chain.md) → [Render Target View (RTV)](render-target-view.md) → [Clear and Present](clear-present.md) → [Viewport](viewport.md) |
| ② 三角形を描く | [Shaders and Compilation](shaders.md) → [Vertex Buffer](vertex-buffer.md) → [Index Buffer](index-buffer.md) → [Input Layout](input-layout.md) → [Drawing a Triangle](triangle.md) |
| ③ 動かす・貼る | [Constant Buffer](constant-buffer.md) → [Map, Unmap and UpdateSubresource](map-update.md) → [Texture2D](texture2d.md) → [Shader Resource View (SRV)](shader-resource-view.md) → [Sampler State](sampler-state.md) |
| ④ 立体にする | [Depth Buffer and DSV](depth-stencil.md) → [Depth-Stencil State](depth-stencil-state.md) → [Rasterizer State](rasterizer-state.md) → [Blend State](blend-state.md) |
| ⑤ パスを重ねる | [Instanced Drawing](instancing-draw.md) → [Multiple Render Targets](mrt.md) → [Structured and Raw Buffers](structured-buffer.md) → [Compute Shader](compute-shader.md) → [Unordered Access View (UAV)](uav.md) |
| ⑥ 道具 | [GPU Queries and Timing](query-timing.md) → [Debug Layer](debug-layer.md) → [Window Resize and Device Removal](resize.md) → [D3D11 Pass Recipes](pass-recipes.md) |

## このセクションの前提

| 項目 | 内容 |
| --- | --- |
| 言語 | C++23。Google C++ Style（関数は大文字始まり変数は `snake_case`、メンバーは末尾 `_`） |
| COM | `Microsoft::WRL::ComPtr`（`#include <wrl/client.h>`）で解放を自動にする |
| 座標系 | 右手系・Y が上・前は −Z。行ベクトル（`v * M`）。三角形は反時計回り（CCW）が表 |
| シェーダー | HLSL、シェーダー モデル 5.0（`vs_5_0`、`ps_5_0`、`cs_5_0`） |
| 数学 | DirectXMath（[DirectXMath](../../gamemath/directxmath.md)）。型は `DirectX::XMFLOAT4X4` など |
| 機能レベル | 11.0 以上 |

!!! note "DirectX 11 でできないこと"
    レイトレーシング（DXR）、メッシュ シェーダー、バインドレスのような新しい機能は DirectX 12 の機能です（[DirectX 12 Guide](../dx12/index.md)）。

## 用語について

このセクションに出てくる API の名前や用語（デバイス、ビュー、ステートなど）は 1 つずつ専用のページを持っています。文章の中の最初の 1 回はそのページへのリンクになります。

## 関連ページ

- [DirectX 12 Guide](../dx12/index.md)
- [DirectX の概念](../concepts/index.md)
- [DX11 と DX12 の対応表](../compare.md)
- [描画の流れ（入門）](../../3d/render-flow/index.md)
- [シェーダー](../../graphics/index.md)
