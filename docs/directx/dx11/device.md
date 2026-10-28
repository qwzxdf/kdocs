---
title: ID3D11Device and Device Context
tags:
  - DirectX
---

# ID3D11Device and Device Context

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

D3D11 のすべての出発点は <strong>デバイス</strong>（`ID3D11Device`）と <strong>デバイス コンテキスト</strong>（`ID3D11DeviceContext`）の、2 つです。デバイスは「GPU に物を作らせる窓口」、コンテキストは「GPU に命令を出す窓口」です。この 2 つを 1 回の呼び出しで、作ります。

!!! tip "ポイント"
    - <strong>デバイス = 作る</strong>（バッファ・テクスチャ・シェーダー・ステート・ビューの `Create…`）。<strong>コンテキスト = 命令する</strong>（`Draw`・`Dispatch`・`…Set…`・`Map`）。
    - 作成は `D3D11CreateDevice` 1 回。デバッグ ビルドでは `D3D11_CREATE_DEVICE_DEBUG` を付ける。
    - 機能レベルの配列を渡すと GPU が対応する最も高いレベルが選ばれる。
    - コンテキストの命令は <strong>1 つのスレッドから</strong>出す（即時コンテキスト）。
    - 全部の COM オブジェクトは `ComPtr` で持つ。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

## ID3D11Device

デバイスは GPU 1 つ（のドライバー）を表すオブジェクトです。GPU 上のあらゆる物はデバイスが作ります。

| 作るもの | 関数 |
| --- | --- |
| バッファ | `CreateBuffer`（[頂点](vertex-buffer.md)、[インデックス](index-buffer.md)、[定数](constant-buffer.md)、[構造化](structured-buffer.md)） |
| テクスチャ | `CreateTexture2D`（[Texture2D](texture2d.md)）、`CreateTexture1D`、`CreateTexture3D` |
| ビュー | `CreateRenderTargetView`、`CreateShaderResourceView`、`CreateUnorderedAccessView`、`CreateDepthStencilView` |
| シェーダー | `CreateVertexShader`、`CreatePixelShader`、`CreateComputeShader`（[Shaders and Compilation](shaders.md)） |
| 入力レイアウト | `CreateInputLayout`（[Input Layout](input-layout.md)） |
| ステート | `CreateRasterizerState`、`CreateBlendState`、`CreateDepthStencilState`、`CreateSamplerState` |
| クエリ | `CreateQuery`（[GPU Queries and Timing](query-timing.md)） |

デバイスの関数は <strong>どのスレッドからでも</strong>、呼べます（スレッド セーフ）。ロード用のスレッドでテクスチャを作るといった使い方ができます。

## ID3D11DeviceContext {#device-context}

コンテキストは GPU に命令を積む窓口です。命令は 2 種類に分かれます。

| 種類 | 関数の例 | 内容 |
| --- | --- | --- |
| 束縛（バインド） | `IASetVertexBuffers`、`VSSetShader`、`PSSetShaderResources`、`OMSetRenderTargets`、`CSSetUnorderedAccessViews` | パイプラインにリソースやステートをつなぐ |
| 実行 | `Draw`、`DrawIndexed`、`DrawInstanced`、`Dispatch`、`Clear…`、`CopyResource` | GPU に仕事をさせる |
| データ | `Map`/`Unmap`、`UpdateSubresource` | CPU から GPU のリソースへ書く |

関数の名前の接頭辞が <strong>パイプラインの段</strong>を表します。

| 接頭辞 | 段 |
| --- | --- |
| `IA` | 入力アセンブラー（頂点・インデックス） |
| `VS`、`HS`、`DS`、`GS` | 頂点・ハル・ドメイン・ジオメトリ シェーダー |
| `RS` | ラスタライザー（ビューポート、ステート） |
| `PS` | ピクセル シェーダー |
| `OM` | 出力マージャー（レンダー ターゲット、深度、ブレンド） |
| `CS` | 計算シェーダー |

<strong>即時コンテキスト</strong>（`ID3D11DeviceContext`）の命令は 1 つのスレッドから出します。複数のスレッドで命令を作りたいときは、<strong>遅延コンテキスト</strong>（`CreateDeferredContext`）で、コマンド リストを作る方法がありますが効果は限定的です。マルチスレッドの描画が本命なら[DirectX 12](../dx12/index.md) を検討します。

## D3D11CreateDevice

```cpp
#include <d3d11.h>
#include <wrl/client.h>

Microsoft::WRL::ComPtr<ID3D11Device> device;
Microsoft::WRL::ComPtr<ID3D11DeviceContext> context;
```

型は `ComPtr` で持ちます。`ComPtr` はスコープを抜けると `Release` を呼ぶので、解放し忘れがありません。

```cpp
UINT flags = D3D11_CREATE_DEVICE_BGRA_SUPPORT;             // Direct2D などと、組み合わせるときに必要
#if defined(_DEBUG)
flags |= D3D11_CREATE_DEVICE_DEBUG;                        // デバッグ レイヤー（debug-layer.md）
#endif
```

`D3D11_CREATE_DEVICE_DEBUG` を付けると API の使い方の誤りが、出力ウィンドウにメッセージとして、出ます。Release ビルドでは付けません（遅くなり環境にグラフィックス ツールが要るため）。

```cpp
const D3D_FEATURE_LEVEL levels[] = {D3D_FEATURE_LEVEL_11_1, D3D_FEATURE_LEVEL_11_0};
D3D_FEATURE_LEVEL obtained = {};

HRESULT hr = D3D11CreateDevice(
    nullptr,                       // アダプター: nullptr = 既定の GPU（dxgi.md で、選ぶ方法）
    D3D_DRIVER_TYPE_HARDWARE,      // GPU を使う（WARP は、ソフトウェア）
    nullptr,                       // ソフトウェア ラスタライザーの DLL（使わない）
    flags,
    levels, ARRAYSIZE(levels),     // 試す機能レベル（高い順）
    D3D11_SDK_VERSION,
    &device, &obtained, &context);
if (FAILED(hr)) {
  // 失敗: GPU が非対応、または、デバッグ レイヤーが入っていない（下の表）
}
```

`levels` の配列を高い順に渡すと GPU が対応する、最も高いレベルが `obtained` に返ります。11.1 を含めると一部の機能（UAV を頂点シェーダーで使うなど）が使えます。

| 引数 | 内容 |
| --- | --- |
| `pAdapter` | 使う GPU。`nullptr` で既定。`D3D_DRIVER_TYPE_UNKNOWN` とアダプターを渡すと特定の GPU を選べる |
| `DriverType` | `HARDWARE`（GPU）、`WARP`（ソフトウェア。GPU が無い環境やテスト用）、`REFERENCE`（遅い基準実装） |
| `Flags` | `D3D11_CREATE_DEVICE_DEBUG`、`BGRA_SUPPORT`、`SINGLETHREADED`（スレッドのロックを省く）など |
| `pFeatureLevels` | 試す機能レベルの配列 |
| `SDKVersion` | 必ず `D3D11_SDK_VERSION` |
| 戻り値 | `S_OK`、または失敗の `HRESULT` |

## 機能レベル

<strong>機能レベル</strong>（Feature Level）は、GPU が対応する機能のまとまりです。D3D11 の API で古い GPU（D3D10 世代）も動かせるよう機能レベルで分けています。

| レベル | 主な内容 |
| --- | --- |
| 11.0 | シェーダー モデル 5.0、計算シェーダー、テッセレーション |
| 11.1 | UAV の追加の用途、一部のフォーマット、`ID3D11DeviceContext1`（`ClearView` など） |
| 10.0・10.1 | 計算シェーダーなし（古い GPU） |

今の PC の GPU はほとんど 11.1 以上に対応しています。11.0 を下限として 11.1 を使える範囲で使います。

```cpp
// 計算シェーダーや、特定のフォーマットの、UAV が使えるか: 機能ごとに、さらに、確認する。
D3D11_FEATURE_DATA_D3D11_OPTIONS options = {};
device->CheckFeatureSupport(D3D11_FEATURE_D3D11_OPTIONS, &options, sizeof(options));
```

## 失敗の原因

`D3D11CreateDevice` が失敗する主な原因です。

| 症状 | 原因 |
| --- | --- |
| `DXGI_ERROR_SDK_COMPONENT_MISSING`（`0x887A002D`） | デバッグ レイヤーを要求したが Windows のオプション機能「グラフィックス ツール」が入っていない |
| `E_INVALIDARG`（Windows 7） | 機能レベル 11.1 を含めたが OS が非対応。リストから 11.1 を外して、再試行する |
| `DXGI_ERROR_UNSUPPORTED` | GPU が機能レベル 10 以上に対応していない。`D3D_DRIVER_TYPE_WARP` で再試行する |

デバッグ レイヤーが使えないときに `DEBUG` フラグを外してもう一度、作るフォールバックを入れておくと環境の違いで起動しないことが、減ります。

## 後始末

`ComPtr` はスコープを抜けると自動で、解放します。ただし、<strong>パイプラインに束ねたままのリソースは解放が遅れます</strong>。終了時やリソースの作り直しの前に `ClearState` を呼び束縛を外します。

```cpp
context->ClearState();         // すべての束縛（シェーダー、リソース、レンダー ターゲット）を外す
context->Flush();              // 溜まっている命令を GPU へ送る
```

## よくあるミス

??? failure "`D3D11CreateDevice` が、失敗して起動しない"
    デバッグ レイヤーを要求したが環境に無い。`DEBUG` を外して再試行する（`DXGI_ERROR_SDK_COMPONENT_MISSING`）。

??? failure "別のスレッドから、`Draw` を呼んでクラッシュする"
    即時コンテキストはスレッド セーフではない。命令は 1 つのスレッドから。リソースの作成（デバイス）はどのスレッドからでもよい。

??? failure "終了時にリーク警告が大量に出る"
    `ComPtr` の寿命がデバイスより長いまたは、グローバル変数に置いている。デバイスは最後に解放する。`ReportLiveDeviceObjects`（[Debug Layer](debug-layer.md)）で、残っている物を確認する。

??? failure "ノート PC で、遅い GPU が選ばれる"
    `pAdapter` が `nullptr` だと内蔵 GPU が、選ばれることがある。DXGI で高性能な GPU を選ぶ（[DXGI Factory and Adapter](dxgi.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] デバイス＝作るコンテキスト＝命令する
    - [x] `D3D11CreateDevice` 1 回で、両方できる
    - [x] 機能レベルは高い順に配列で渡す
    - [x] デバッグ ビルドは `D3D11_CREATE_DEVICE_DEBUG`
    - [x] 命令は 1 スレッド。作成はどのスレッドでも
    - [x] 終了前に `ClearState`

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Win32 Window and Message Loop](window.md)
- [DXGI Factory and Adapter](dxgi.md)
- [Debug Layer](debug-layer.md)
- [Microsoft Learn: D3D11CreateDevice](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-d3d11createdevice)
