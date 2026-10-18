---
title: ID3D11Device and Device Context
tags:
  - DirectX
---

# ID3D11Device and Device Context

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

D3D11 の、すべての、出発点は、<strong>デバイス</strong>（`ID3D11Device`）と、<strong>デバイス コンテキスト</strong>（`ID3D11DeviceContext`）の、2 つです。デバイスは、「GPU に、物を作らせる窓口」、コンテキストは、「GPU に、命令を出す窓口」です。この 2 つを、1 回の呼び出しで、作ります。

!!! tip "ポイント"
    - <strong>デバイス = 作る</strong>（バッファ・テクスチャ・シェーダー・ステート・ビューの `Create…`）。<strong>コンテキスト = 命令する</strong>（`Draw`・`Dispatch`・`…Set…`・`Map`）。
    - 作成は、`D3D11CreateDevice` 1 回。デバッグ ビルドでは、`D3D11_CREATE_DEVICE_DEBUG` を付ける。
    - 機能レベルの、配列を渡すと、GPU が対応する、最も高いレベルが、選ばれる。
    - コンテキストの、命令は、<strong>1 つのスレッドから</strong>出す（即時コンテキスト）。
    - 全部の COM オブジェクトは、`ComPtr` で、持つ。

## ID3D11Device

デバイスは、GPU 1 つ（のドライバー）を、表すオブジェクトです。GPU 上の、あらゆる物は、デバイスが、作ります。

| 作るもの | 関数 |
| --- | --- |
| バッファ | `CreateBuffer`（[頂点](vertex-buffer.md)、[インデックス](index-buffer.md)、[定数](constant-buffer.md)、[構造化](structured-buffer.md)） |
| テクスチャ | `CreateTexture2D`（[Texture2D](texture2d.md)）、`CreateTexture1D`、`CreateTexture3D` |
| ビュー | `CreateRenderTargetView`、`CreateShaderResourceView`、`CreateUnorderedAccessView`、`CreateDepthStencilView` |
| シェーダー | `CreateVertexShader`、`CreatePixelShader`、`CreateComputeShader`（[Shaders and Compilation](shaders.md)） |
| 入力レイアウト | `CreateInputLayout`（[Input Layout](input-layout.md)） |
| ステート | `CreateRasterizerState`、`CreateBlendState`、`CreateDepthStencilState`、`CreateSamplerState` |
| クエリ | `CreateQuery`（[GPU Queries and Timing](query-timing.md)） |

デバイスの関数は、<strong>どのスレッドからでも</strong>、呼べます（スレッド セーフ）。ロード用のスレッドで、テクスチャを作る、といった使い方ができます。

## ID3D11DeviceContext {#device-context}

コンテキストは、GPU に、命令を、積む窓口です。命令は、2 種類に分かれます。

| 種類 | 関数の例 | 内容 |
| --- | --- | --- |
| 束縛（バインド） | `IASetVertexBuffers`、`VSSetShader`、`PSSetShaderResources`、`OMSetRenderTargets`、`CSSetUnorderedAccessViews` | パイプラインに、リソースや、ステートを、つなぐ |
| 実行 | `Draw`、`DrawIndexed`、`DrawInstanced`、`Dispatch`、`Clear…`、`CopyResource` | GPU に、仕事を、させる |
| データ | `Map`/`Unmap`、`UpdateSubresource` | CPU から、GPU のリソースへ、書く |

関数の、名前の、接頭辞が、<strong>パイプラインの段</strong>を、表します。

| 接頭辞 | 段 |
| --- | --- |
| `IA` | 入力アセンブラー（頂点・インデックス） |
| `VS`、`HS`、`DS`、`GS` | 頂点・ハル・ドメイン・ジオメトリ シェーダー |
| `RS` | ラスタライザー（ビューポート、ステート） |
| `PS` | ピクセル シェーダー |
| `OM` | 出力マージャー（レンダー ターゲット、深度、ブレンド） |
| `CS` | 計算シェーダー |

<strong>即時コンテキスト</strong>（`ID3D11DeviceContext`）の命令は、1 つのスレッドから、出します。複数のスレッドで、命令を、作りたいときは、<strong>遅延コンテキスト</strong>（`CreateDeferredContext`）で、コマンド リストを、作る方法が、ありますが、効果は、限定的です。マルチスレッドの、描画が、本命なら、[DirectX 12](../dx12/index.md) を、検討します。

## D3D11CreateDevice

```cpp
#include <d3d11.h>
#include <wrl/client.h>

Microsoft::WRL::ComPtr<ID3D11Device> device;
Microsoft::WRL::ComPtr<ID3D11DeviceContext> context;
```

型は、`ComPtr` で持ちます。`ComPtr` は、スコープを、抜けると、`Release` を呼ぶので、解放し忘れが、ありません。

```cpp
UINT flags = D3D11_CREATE_DEVICE_BGRA_SUPPORT;             // Direct2D などと、組み合わせるときに必要
#if defined(_DEBUG)
flags |= D3D11_CREATE_DEVICE_DEBUG;                        // デバッグ レイヤー（debug-layer.md）
#endif
```

`D3D11_CREATE_DEVICE_DEBUG` を、付けると、API の、使い方の誤りが、出力ウィンドウに、メッセージとして、出ます。Release ビルドでは、付けません（遅くなり、環境に、グラフィックス ツールが、要るため）。

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
  // 失敗: GPU が非対応、または、デバッグ レイヤーが、入っていない（下の表）
}
```

`levels` の、配列を、高い順に、渡すと、GPU が対応する、最も高いレベルが、`obtained` に、返ります。11.1 を、含めると、一部の機能（UAV を、頂点シェーダーで、使う、など）が、使えます。

| 引数 | 内容 |
| --- | --- |
| `pAdapter` | 使う GPU。`nullptr` で、既定。`D3D_DRIVER_TYPE_UNKNOWN` と、アダプターを渡すと、特定の GPU を、選べる |
| `DriverType` | `HARDWARE`（GPU）、`WARP`（ソフトウェア。GPU が、無い環境や、テスト用）、`REFERENCE`（遅い基準実装） |
| `Flags` | `D3D11_CREATE_DEVICE_DEBUG`、`BGRA_SUPPORT`、`SINGLETHREADED`（スレッドの、ロックを、省く）など |
| `pFeatureLevels` | 試す機能レベルの配列 |
| `SDKVersion` | 必ず `D3D11_SDK_VERSION` |
| 戻り値 | `S_OK`、または、失敗の `HRESULT` |

## 機能レベル

<strong>機能レベル</strong>（Feature Level）は、GPU が、対応する、機能の、まとまりです。D3D11 の API で、古い GPU（D3D10 世代）も、動かせるよう、機能レベルで、分けています。

| レベル | 主な内容 |
| --- | --- |
| 11.0 | シェーダー モデル 5.0、計算シェーダー、テッセレーション |
| 11.1 | UAV の、追加の用途、一部のフォーマット、`ID3D11DeviceContext1`（`ClearView` など） |
| 10.0・10.1 | 計算シェーダーなし（古い GPU） |

今の PC の GPU は、ほとんど、11.1 以上に、対応しています。11.0 を、下限と、して、11.1 を、使える範囲で、使います。

```cpp
// 計算シェーダーや、特定のフォーマットの、UAV が使えるか: 機能ごとに、さらに、確認する。
D3D11_FEATURE_DATA_D3D11_OPTIONS options = {};
device->CheckFeatureSupport(D3D11_FEATURE_D3D11_OPTIONS, &options, sizeof(options));
```

## 失敗の原因

`D3D11CreateDevice` が、失敗する、主な原因です。

| 症状 | 原因 |
| --- | --- |
| `DXGI_ERROR_SDK_COMPONENT_MISSING`（`0x887A002D`） | デバッグ レイヤーを、要求したが、Windows の、オプション機能「グラフィックス ツール」が、入っていない |
| `E_INVALIDARG`（Windows 7） | 機能レベル 11.1 を、含めたが、OS が、非対応。リストから、11.1 を、外して、再試行する |
| `DXGI_ERROR_UNSUPPORTED` | GPU が、機能レベル 10 以上に、対応していない。`D3D_DRIVER_TYPE_WARP` で、再試行する |

デバッグ レイヤーが、使えないときに、`DEBUG` フラグを、外して、もう一度、作る、フォールバックを、入れておくと、環境の違いで、起動しないことが、減ります。

## 後始末

`ComPtr` は、スコープを、抜けると、自動で、解放します。ただし、<strong>パイプラインに、束ねたままの、リソースは、解放が、遅れます</strong>。終了時や、リソースの、作り直しの前に、`ClearState` を呼び、束縛を、外します。

```cpp
context->ClearState();         // すべての束縛（シェーダー、リソース、レンダー ターゲット）を、外す
context->Flush();              // 溜まっている命令を、GPU へ送る
```

## よくあるミス

??? failure "`D3D11CreateDevice` が、失敗して、起動しない"
    デバッグ レイヤーを、要求したが、環境に、無い。`DEBUG` を、外して、再試行する（`DXGI_ERROR_SDK_COMPONENT_MISSING`）。

??? failure "別のスレッドから、`Draw` を呼んで、クラッシュする"
    即時コンテキストは、スレッド セーフではない。命令は、1 つのスレッドから。リソースの、作成（デバイス）は、どのスレッドからでも、よい。

??? failure "終了時に、リーク警告が、大量に出る"
    `ComPtr` の、寿命が、デバイスより、長い、または、グローバル変数に、置いている。デバイスは、最後に、解放する。`ReportLiveDeviceObjects`（[Debug Layer](debug-layer.md)）で、残っている物を、確認する。

??? failure "ノート PC で、遅い GPU が、選ばれる"
    `pAdapter` が `nullptr` だと、内蔵 GPU が、選ばれることがある。DXGI で、高性能な GPU を、選ぶ（[DXGI Factory and Adapter](dxgi.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] デバイス＝作る、コンテキスト＝命令する
    - [x] `D3D11CreateDevice` 1 回で、両方できる
    - [x] 機能レベルは、高い順に、配列で渡す
    - [x] デバッグ ビルドは、`D3D11_CREATE_DEVICE_DEBUG`
    - [x] 命令は 1 スレッド。作成は、どのスレッドでも
    - [x] 終了前に、`ClearState`

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Win32 Window and Message Loop](window.md)
- [DXGI Factory and Adapter](dxgi.md)
- [Debug Layer](debug-layer.md)
- [Microsoft Learn: D3D11CreateDevice](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-d3d11createdevice)
