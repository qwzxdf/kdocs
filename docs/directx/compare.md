---
title: DX11 and DX12 Mapping
tags:
  - DirectX
---

# DX11 and DX12 Mapping

DirectX 11 と DirectX 12 は、<strong>同じ GPU を、同じパイプラインで、動かして</strong>いますが、<strong>誰が、何を、管理するか</strong>が、違います。このページは、DX11 で、書き慣れた人が、DX12 に、移るとき、または、その逆の、とき用の、<strong>対応表</strong>です。各項目は、専用のページへ、リンクしています。

!!! tip "ポイント"
    - DX11 は、ドライバーが、メモリ・同期・状態管理を、自動で、行う。DX12 は、<strong>アプリが、明示的に</strong>行う。
    - DX11 の、「コンテキスト」は、DX12 では、<strong>コマンド リスト + コマンド キュー</strong>に、分かれる。
    - DX11 の、ステートの、個別設定（ブレンド、深度、ラスタライザー）は、DX12 では、<strong>PSO に、まとまる</strong>。
    - DX11 の、ビューの、直接束縛は、DX12 では、<strong>ディスクリプタ ヒープ + ルート シグネチャ</strong>。
    - DX11 の、自動の、同期は、DX12 では、<strong>フェンス + リソース バリア</strong>。
    - 同じ、HLSL・フォーマット・DXGI は、どちらでも、同じ。

## 全体の、違い

| 観点 | DirectX 11 | DirectX 12 |
| --- | --- | --- |
| 考え方 | ドライバーが、面倒を見る | アプリが、直接、管理する |
| コードの量 | 少ない | 多い（三角形で、約 3〜4 倍） |
| CPU の、負荷 | 大きい（ドライバーが、多くの仕事） | 小さい |
| マルチスレッド | 限定的（遅延コンテキスト） | 本格的（コマンド リストを、スレッドごとに） |
| 新機能 | 古い | DXR、メッシュ シェーダー、ビンドレス、GPU ドリブン |
| 向く用途 | 学習、中小規模、素早い開発 | 大規模、最高性能、最新機能 |

## 初期化

| やりたいこと | DirectX 11 | DirectX 12 |
| --- | --- | --- |
| デバイスの、作成 | [`D3D11CreateDevice`](dx11/device.md)（デバイスと、コンテキストが、同時に、できる） | [`D3D12CreateDevice`](dx12/factory-device.md)（デバイスだけ） |
| 命令を、出す、窓口 | `ID3D11DeviceContext`（即時コンテキスト） | [コマンド キュー](dx12/command-queue.md) + [コマンド リスト](dx12/command-list.md) + [アロケーター](dx12/command-allocator.md) |
| GPU を、選ぶ | [DXGI で、アダプターを、列挙](dx11/dxgi.md)（省略可） | [DXGI で、アダプターを、列挙](dx12/factory-device.md) |
| スワップ チェーン | [`CreateSwapChainForHwnd(device, …)`](dx11/swap-chain.md) | [`CreateSwapChainForHwnd(command_queue, …)`](dx12/swap-chain.md) |
| デバッグ | [`D3D11_CREATE_DEVICE_DEBUG`](dx11/debug-layer.md) | [`EnableDebugLayer`（デバイス作成の前）+ GPU ベース検証 + DRED](dx12/debug-layer.md) |

## リソースと、ビュー

| やりたいこと | DirectX 11 | DirectX 12 |
| --- | --- | --- |
| バッファ・テクスチャの、作成 | [`CreateBuffer`、`CreateTexture2D`](dx11/texture2d.md)（`Usage` と `BindFlags`） | [`CreateCommittedResource`](dx12/heaps-resources.md)（ヒープの種類と、`ALLOW_*` フラグ） |
| CPU から、書く | [`Map` / `UpdateSubresource`](dx11/map-update.md) | [UPLOAD ヒープに、書いて、コピー](dx12/upload-buffer.md) |
| ビューの、作成 | `CreateRenderTargetView` など。ビュー オブジェクトが、できる | `Create…View(resource, desc, handle)`。[ディスクリプタ ヒープの、位置に、書く](dx12/descriptor.md) |
| ビューの、保管 | ビュー オブジェクト（`ComPtr`） | [ディスクリプタ ヒープ](dx12/descriptor-heap.md) |
| 頂点バッファの、束縛 | [`IASetVertexBuffers`](dx11/vertex-buffer.md)（バッファを、渡す） | [`IASetVertexBuffers`](dx12/vertex-index-view.md)（<strong>ビュー構造体</strong>を、渡す） |
| 定数バッファ | [`VSSetConstantBuffers`。16 バイト境界](dx11/constant-buffer.md) | [ルート CBV。256 バイト境界。フレームごとの領域](dx12/constant-buffer.md) |
| テクスチャの、アップロード | [`UpdateSubresource`、`GenerateMips`](dx11/texture2d.md) | [`UpdateSubresources`。ミップは、自分で](dx12/texture-upload.md) |
| 深度バッファ | [DSV。typeless で、SRV も](dx11/depth-stencil.md) | [DSV ヒープ。typeless で、SRV も](dx12/depth-buffer.md) |

## パイプラインの、設定

| やりたいこと | DirectX 11 | DirectX 12 |
| --- | --- | --- |
| シェーダー | [`CreateVertexShader` など。オブジェクトに](dx11/shaders.md) | [バイトコードを、PSO に、渡す](dx12/shaders-dxc.md) |
| シェーダー コンパイラ | `fxc`（SM 5.0） | `dxc`（SM 6.x）。`fxc` も、可 |
| 入力レイアウト | [`CreateInputLayout`（オブジェクト）](dx11/input-layout.md) | [PSO の中の `InputLayout`](dx12/pso.md) |
| ブレンド・深度・ラスタライザー | [別々の、ステート オブジェクト](dx11/blend-state.md) | [PSO に、まとめる](dx12/pso.md) |
| パイプラインの、切り替え | 個別に、`…SetState` | [`SetPipelineState`（1 回）](dx12/pso.md) |
| リソースの、シェーダーへの、渡し方 | `PSSetShaderResources`、`VSSetConstantBuffers` など | [ルート シグネチャ + ディスクリプタ テーブル](dx12/root-signature.md) |
| サンプラー | [`CreateSamplerState` + `PSSetSamplers`](dx11/sampler-state.md) | [静的サンプラー、または、サンプラー ヒープ](dx12/root-signature.md) |
| ビューポート | [`RSSetViewports`](dx11/viewport.md) | [`RSSetViewports` + `RSSetScissorRects`（シザーは、必須）](dx12/viewport-scissor.md) |

## 描画と、計算

| やりたいこと | DirectX 11 | DirectX 12 |
| --- | --- | --- |
| 描画命令 | [`context->Draw…`（即時）](dx11/triangle.md) | [`command_list->Draw…`（記録）→ 実行](dx12/triangle.md) |
| レンダー ターゲットの、設定 | `OMSetRenderTargets(n, rtvs, dsv)` | `OMSetRenderTargets(n, &rtv_handle, …, &dsv_handle)`（<strong>CPU ハンドル</strong>） |
| クリア | `ClearRenderTargetView(rtv, color)` | `ClearRenderTargetView(handle, color, 0, nullptr)` |
| 計算シェーダー | [`CSSet…` + `Dispatch`](dx11/compute-shader.md) | [計算用 PSO + `SetComputeRoot…` + `Dispatch`](dx12/compute-shader.md) |
| UAV | [`CSSetUnorderedAccessViews`](dx11/uav.md) | [UAV ディスクリプタ + UAV バリア](dx12/compute-shader.md) |
| インスタンス描画 | [`DrawIndexedInstanced`](dx11/instancing-draw.md) | `DrawIndexedInstanced`、`ExecuteIndirect` |
| 間接描画 | `DrawIndexedInstancedIndirect` | [`ExecuteIndirect`](../rendering/gpu-driven-dx12/execute-indirect.md) |

## 同期

| やりたいこと | DirectX 11 | DirectX 12 |
| --- | --- | --- |
| 読み書きの、順序 | ドライバーが、自動 | [リソース バリアで、明示](dx12/resource-barrier.md) |
| CPU が、GPU の、完了を、待つ | `D3D11_QUERY_EVENT`、`Map(READ)`（暗黙に待つ） | [フェンス + イベント](dx12/fence.md) |
| 動的な、データの、更新 | [`Map(WRITE_DISCARD)`（ドライバーが、領域を、割り当てる）](dx11/map-update.md) | [フレームごとに、別の領域](dx12/frame-resources.md) |
| 解放 | ドライバーが、参照を、数えて、遅延 | アプリが、フェンスで、完了を、確認 |
| GPU の、時間の、計測 | [`D3D11_QUERY_TIMESTAMP`](dx11/query-timing.md) | [`ID3D12QueryHeap` + `ResolveQueryData`](dx12/query-timing.md) |
| ウィンドウの、リサイズ | [`ResizeBuffers`（参照を、解放してから）](dx11/resize.md) | [GPU の完了を待ってから `ResizeBuffers`](dx12/swap-chain.md) |

## 1 枚の、三角形で、比べる

| 作る物 | DirectX 11 | DirectX 12 |
| --- | --- | --- |
| デバイス | `D3D11CreateDevice`（1 回） | `D3D12CreateDevice` + `CreateCommandQueue` |
| スワップ チェーン | 1 つ | 1 つ（キューを、渡す） |
| RTV | `CreateRenderTargetView`（ビュー オブジェクト） | RTV ヒープ + `CreateRenderTargetView(handle)` |
| シェーダー | `CreateVertexShader`、`CreatePixelShader` | （PSO の一部） |
| 入力レイアウト | `CreateInputLayout` | （PSO の一部） |
| ラスタライザー | `CreateRasterizerState` | （PSO の一部） |
| 頂点バッファ | `CreateBuffer`（`IMMUTABLE`、初期データを、渡す） | DEFAULT バッファ + UPLOAD の中継 + コピー + バリア |
| ルート シグネチャ | （無い） | 必要 |
| PSO | （無い） | 必要 |
| コマンド アロケーター・リスト | （無い） | 必要 |
| フェンス | （無い） | 必要 |
| 毎フレームの、描画 | `Set…`、`Draw`、`Present` | `Reset`、バリア、`Set…`、`Draw`、バリア、`Close`、`Execute`、`Present`、フェンス |

## どちらを、選ぶか

| 状況 | 選択 |
| --- | --- |
| 初めて、DirectX を、学ぶ | DX11（概念を、先に、理解できる） |
| 小〜中規模の、ゲーム、ツール | DX11（開発が、速い。性能は、十分） |
| レイトレーシング（DXR）、メッシュ シェーダー、ビンドレスを、使う | DX12 |
| CPU が、ボトルネック（ドロー コールが、多い）、マルチスレッド描画 | DX12 |
| GPU ドリブン、非同期コンピュート | DX12 |
| 最高の、性能を、引き出したい（専任の、レンダリング プログラマーが、いる） | DX12 |

DX12 は、DX11 より、<strong>必ずしも、速くなるわけでは、ありません</strong>。ドライバーの、仕事を、アプリが、引き受けるので、<strong>うまく、書けないと、DX11 より、遅く</strong>なります。

## 共通の、部分

| 共通 | 内容 |
| --- | --- |
| HLSL | どちらも、HLSL（SM は、DX11 が 5.0、DX12 が 5.1〜6.x） |
| DXGI | アダプター、スワップ チェーン、フォーマット（`DXGI_FORMAT`） |
| DirectXMath | 数学ライブラリ（[DirectXMath](../gamemath/directxmath.md)） |
| 座標系・規約 | [Coordinate Conventions](concepts/conventions.md) |
| パイプラインの、考え方 | [GPU Pipeline Overview](concepts/gpu-pipeline.md) |

## 関連ページ

- [DirectX 11 Guide](dx11/index.md)
- [DirectX 12 Guide](dx12/index.md)
- [DirectX Concepts](concepts/index.md)
- [Why Synchronization](concepts/synchronization.md)
