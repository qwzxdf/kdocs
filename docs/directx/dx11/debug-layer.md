---
title: Debug Layer
tags:
  - DirectX
---

# Debug Layer

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

D3D11 は、描画が、間違っていても、<strong>エラーを、出さずに、黙って、何も、描かない</strong>ことが、よくあります。「ビューポートを、設定し忘れた」「入力レイアウトが、合っていない」「リソースを、読みながら、書いた」。これらの原因を、<strong>文字で、教えてくれる</strong>のが、<strong>デバッグ レイヤー</strong>です。D3D11 の開発では、常に、有効にして、おきます。

!!! tip "ポイント"
    - デバイスを作るとき、`D3D11_CREATE_DEVICE_DEBUG` を、付ける。メッセージが、<strong>Visual Studio の、出力ウィンドウ</strong>に、出る。
    - 使うには、Windows の、オプション機能「<strong>グラフィックス ツール</strong>」が、必要。
    - `ID3D11InfoQueue` で、エラーの時に、ブレーク（止める）できる。メッセージを、フィルタできる。
    - オブジェクトに、<strong>名前</strong>を、付けると、メッセージが、読みやすくなる。
    - 終了時の、`ReportLiveDeviceObjects` で、解放し忘れを、見つける。
    - 製品（Release）では、外す（遅い）。

## 有効にする

```cpp
UINT flags = D3D11_CREATE_DEVICE_BGRA_SUPPORT;
#if defined(_DEBUG)
flags |= D3D11_CREATE_DEVICE_DEBUG;
#endif
D3D11CreateDevice(nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr, flags, levels, ARRAYSIZE(levels), D3D11_SDK_VERSION,
                  &device, nullptr, &context);
```

作成が、`DXGI_ERROR_SDK_COMPONENT_MISSING` で、失敗するときは、Windows の、設定 → アプリ → オプション機能 → 「グラフィックス ツール」を、追加します（[ID3D11Device and Device Context](device.md)）。

## メッセージの、見え方

デバッグ レイヤーが、有効だと、次のような、メッセージが、出力ウィンドウに、出ます。

```text
D3D11 ERROR: ID3D11DeviceContext::DrawIndexed: Input Assembler - Vertex Shader linkage error:
Signatures between stages are incompatible. The input stage requires Semantic/Index (TEXCOORD,0) as input, but it is not provided by the output stage. [ EXECUTION ERROR #342: DEVICE_SHADER_LINKAGE_SEMANTICNAME_NOT_FOUND]
```

読み方は、「どの関数で」「何が」「なぜ」起きたかです。

| 部分 | 内容 |
| --- | --- |
| `ERROR` / `WARNING` / `CORRUPTION` / `INFO` | 重さ。`CORRUPTION` は、メモリ破壊の恐れ |
| `ID3D11DeviceContext::DrawIndexed` | どの呼び出しか |
| 本文 | 何が、問題か（この例は、入力レイアウトと、頂点シェーダーの、セマンティクスが、合わない） |
| `[ EXECUTION ERROR #342 ... ]` | メッセージ ID（検索用） |

## InfoQueue：エラーで、止める

```cpp
#include <d3d11sdklayers.h>

Microsoft::WRL::ComPtr<ID3D11InfoQueue> info_queue;
if (SUCCEEDED(device.As(&info_queue))) {
  info_queue->SetBreakOnSeverity(D3D11_MESSAGE_SEVERITY_CORRUPTION, TRUE);   // メモリ破壊の恐れ → ブレーク
  info_queue->SetBreakOnSeverity(D3D11_MESSAGE_SEVERITY_ERROR, TRUE);        // エラー → ブレーク
  info_queue->SetBreakOnSeverity(D3D11_MESSAGE_SEVERITY_WARNING, FALSE);     // 警告は、止めない
}
```

`SetBreakOnSeverity` を、有効にすると、エラーの起きた、まさにその呼び出しで、デバッガーが、止まり、<strong>コール スタックが、原因の行を、指します</strong>。エラーが、画面に、出る、はるか後で、気づく、ことが、なくなります。

### メッセージを、絞る

```cpp
// 既知の、無害な、メッセージを、非表示にする。
D3D11_MESSAGE_ID hide[] = {D3D11_MESSAGE_ID_DEVICE_DRAW_SAMPLER_NOT_SET};
D3D11_INFO_QUEUE_FILTER filter = {};
filter.DenyList.NumIDs = ARRAYSIZE(hide);
filter.DenyList.pIDList = hide;
info_queue->AddStorageFilterEntries(&filter);
```

メッセージ ID を、見つけたら、`D3D11_MESSAGE_ID_*` で、検索して、絞れます。ただし、無視するのは、<strong>理由が、分かっている、ものだけ</strong>にします。

## オブジェクトに、名前を、付ける

```cpp
const char kName[] = "GBuffer Albedo";
texture->SetPrivateData(WKPDID_D3DDebugObjectName, sizeof(kName) - 1, kName);   // #include <d3dcommon.h>
```

名前を、付けると、デバッグ レイヤーの、メッセージや、グラフィックス デバッガー（PIX、RenderDoc）の、画面に、その名前が、出ます。「`Texture2D` が、1 つ、リークしています」より、「`GBuffer Albedo` が、リーク」の方が、はるかに、探しやすくなります。

```cpp
// 名前を、付ける関数。全オブジェクトに、使う。
template <typename T>
void SetName(T* object, const char* name) {
#if defined(_DEBUG)
  object->SetPrivateData(WKPDID_D3DDebugObjectName, static_cast<UINT>(std::strlen(name)), name);
#endif
}
```

## リークの検出

```cpp
#include <d3d11sdklayers.h>

// 終了時（デバイスを、解放する直前）に呼ぶ。まだ、生きている、オブジェクトを、一覧にする。
Microsoft::WRL::ComPtr<ID3D11Debug> debug;
if (SUCCEEDED(device.As(&debug))) {
  debug->ReportLiveDeviceObjects(D3D11_RLDO_DETAIL | D3D11_RLDO_IGNORE_INTERNAL);
}
```

`ReportLiveDeviceObjects` を、呼ぶと、解放されていない、オブジェクトの、名前と、参照カウントが、出力に、出ます。`ComPtr` を、グローバルや、`static` に、持つと、デバイスの、解放より、後に、解放されて、報告に、出ます。

| 結果の、見方 | 内容 |
| --- | --- |
| `Refcount` が 0 でない | 誰かが、まだ、参照している |
| 名前つきのオブジェクト | 名前で、どれか分かる |
| `ID3D11DeviceContext` が、1 つ残る | 通常（デバイスと、コンテキストは、最後に、解放される） |

## よく出る、メッセージ

| メッセージ | 原因 |
| --- | --- |
| `Resource being set to OM RenderTarget slot 0 is still bound on input` | 同じリソースを、SRV と RTV で、同時に、束ねている（[Render Target View (RTV)](render-target-view.md)） |
| `The Pixel Shader unit expects a Sampler to be set at Slot 0` | サンプラーを、つないでいない |
| `Vertex Shader linkage error` | 入力レイアウトと、頂点シェーダーの、セマンティクスが、合わない |
| `The size of the Constant Buffer at slot 0 of the Vertex Shader unit is too small` | 定数バッファの、大きさが、シェーダーの、`cbuffer` より、小さい |
| `Index buffer has not been set` | `DrawIndexed` の前に、`IASetIndexBuffer` を、呼んでいない |
| `Viewport 0 not set` | ビューポートを、設定していない |
| `Live ID3D11Texture2D at …` | 解放し忘れ（リーク） |

メッセージの、本文が、解決の、ほとんどの、手がかりに、なっています。<strong>「分からない」と思ったら、まず、出力ウィンドウを、見る</strong>のが、鉄則です。

## グラフィックス デバッガー

デバッグ レイヤーの、メッセージで、分からない、<strong>見た目の問題</strong>（「何も、映らない」「色が、おかしい」）は、グラフィックス デバッガーで、1 フレームを、撮って、各ドロー コールの、入出力を、目で見ます。

| ツール | 特徴 |
| --- | --- |
| Visual Studio グラフィックス診断 | VS 内蔵。フレームを、キャプチャして、ピクセルの、履歴（なぜ、その色か）を、追える |
| PIX on Windows | 無料。GPU カウンター、タイミング、シェーダーの、デバッグ |
| RenderDoc | 無料。軽量で、D3D11 に、強い。1 フレームを、撮って、各テクスチャ・バッファを、見る |
| NVIDIA Nsight Graphics | ベンダー固有の、詳細な、プロファイル |

```cpp
// 計測用のマーカー: グラフィックス デバッガーで、パスの名前が、見える。
Microsoft::WRL::ComPtr<ID3DUserDefinedAnnotation> annotation;
context.As(&annotation);
annotation->BeginEvent(L"G-Buffer Pass");
DrawGBuffer();
annotation->EndEvent();
```

`BeginEvent`/`EndEvent` の、ペアで、描画命令を、グループ化し、名前を、付けると、キャプチャが、パスごとに、整理されて、読みやすくなります。

## よくあるミス

??? failure "何も、描かれないのに、メッセージも、出ない"
    デバッグ レイヤーを、有効にしていない（`D3D11_CREATE_DEVICE_DEBUG`）。Release ビルドで、動かしている。

??? failure "`D3D11CreateDevice` が、デバッグ フラグで、失敗する"
    「グラフィックス ツール」の、オプション機能が、入っていない。入れるか、フラグを、外して、再試行する。

??? failure "メッセージが、多すぎて、読めない"
    警告の、一部を、フィルタで、絞る。`SetBreakOnSeverity` を、エラーだけに、して、1 つずつ、直す。

??? failure "リークの、報告に、大量の、オブジェクトが、出る"
    `ComPtr` を、デバイスより、長く、持っている（グローバル変数、`static`）。終了時に、リソースを、先に、解放してから、`ReportLiveDeviceObjects`。

## これだけ覚える

!!! abstract "まとめ"
    - [x] D3D11 は、黙って、失敗する。デバッグ レイヤーが、理由を、教える
    - [x] `D3D11_CREATE_DEVICE_DEBUG`（要・グラフィックス ツール）。製品では、外す
    - [x] `ID3D11InfoQueue` で、エラー時に、ブレークする
    - [x] オブジェクトに、名前を、付ける（`SetPrivateData(WKPDID_D3DDebugObjectName…)`）
    - [x] 終了時に `ReportLiveDeviceObjects` で、リークを、見つける
    - [x] 見た目の問題は、PIX・RenderDoc で、1 フレームを、撮る

## 関連ページ

- [DirectX 11 Guide](index.md)
- [ID3D11Device and Device Context](device.md)
- [GPU Queries and Timing](query-timing.md)
- [Tools](../../rendering/tools.md)
- [Microsoft Learn: Direct3D 11 デバッグ レイヤー](https://learn.microsoft.com/ja-jp/windows/win32/direct3d11/overviews-direct3d-11-devices-layers)
