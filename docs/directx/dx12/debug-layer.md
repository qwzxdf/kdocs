---
title: Debug Layer (D3D12)
tags:
  - DirectX
---

# Debug Layer (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

D3D12 は、リソースの状態、同期、ディスクリプタ、ルート シグネチャと、<strong>間違える所が、非常に多い</strong>ので、デバッグ レイヤーが、必須です。API の、使い方の、誤りを、出力ウィンドウに、メッセージで、出し、さらに、<strong>GPU ベース検証</strong>は、GPU の実行中に、バリアの、間違いや、ディスクリプタの、不正を、検出します。GPU が、ハングした、ときの、原因を、探る、<strong>DRED</strong> も、あります。

!!! tip "ポイント"
    - `ID3D12Debug::EnableDebugLayer()` を、<strong>デバイスを、作る前</strong>に、呼ぶ。
    - <strong>GPU ベース検証</strong>（`SetEnableGPUBasedValidation`）は、遅いが、バリアの、ミスを、正確に、見つける。
    - `ID3D12InfoQueue` で、エラーの、時に、ブレーク（止める）できる。
    - オブジェクトに、`SetName` で、名前を付ける。メッセージが、読みやすくなる。
    - GPU ハング（`DEVICE_REMOVED`）の、原因は、<strong>DRED</strong>（Device Removed Extended Data）で、調べる。
    - 製品（Release）では、外す。

## 有効にする

```cpp
#if defined(_DEBUG)
ComPtr<ID3D12Debug> debug;
if (SUCCEEDED(D3D12GetDebugInterface(IID_PPV_ARGS(&debug)))) {
  debug->EnableDebugLayer();                                    // デバイスを作る「前」に
}
#endif
```

デバイスを、作った後で、有効にすると、既存の、デバイスが、削除されます。必ず、先に、呼びます（[Device and Factory](factory-device.md)）。

## GPU ベース検証

```cpp
#if defined(_DEBUG)
ComPtr<ID3D12Debug1> debug1;
if (SUCCEEDED(debug.As(&debug1))) {
  debug1->SetEnableGPUBasedValidation(TRUE);                   // 遅い。バリア、ディスクリプタの誤りを、GPU 実行中に、検出
}
#endif
```

通常の、デバッグ レイヤーは、<strong>CPU 側</strong>（API の呼び出し）の、誤りを、検出します。GPU ベース検証は、シェーダーに、<strong>計測コードを、挿入</strong>して、実行中の、リソースの、<strong>状態違反</strong>（バリア忘れ）、<strong>ディスクリプタの、不正</strong>、未初期化のリソースを、検出します。ゲームが、数倍、遅くなるので、バグを、探すときだけ、有効にします。

| 検証 | 検出するもの | コスト |
| --- | --- | --- |
| デバッグ レイヤー | API の使い方の、誤り（パラメータ、状態の、組み合わせ） | 小〜中 |
| GPU ベース検証 | バリア忘れ、ディスクリプタの、不正、範囲外アクセス | 大（数倍遅い） |

## メッセージの、見え方

```text
D3D12 ERROR: ID3D12CommandQueue::ExecuteCommandLists: Using ResourceBarrier on Command List (0x...):
Before State (0x4: D3D12_RESOURCE_STATE_RENDER_TARGET) specified in transition barrier does not match
with the state (0x0: D3D12_RESOURCE_STATE_PRESENT) specified by the previous call to ResourceBarrier
[ RESOURCE_MANIPULATION ERROR #527: RESOURCE_BARRIER_BEFORE_AFTER_MISMATCH]
```

この例は、「バリアの、`StateBefore` が、実際の状態と、違う」という、典型的な、エラーです。メッセージに、リソースの、名前（`SetName` で、付けた物）が、出るので、どのリソースか、すぐ、分かります。

## InfoQueue：エラーで、止める

```cpp
#include <d3d12sdklayers.h>

ComPtr<ID3D12InfoQueue> info_queue;
if (SUCCEEDED(device.As(&info_queue))) {
  info_queue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_CORRUPTION, TRUE);
  info_queue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_ERROR, TRUE);        // エラーで、デバッガーが、止まる
  info_queue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_WARNING, FALSE);

  // 既知の、無害な、メッセージを、非表示にする。
  D3D12_MESSAGE_ID hide[] = {D3D12_MESSAGE_ID_CLEARRENDERTARGETVIEW_MISMATCHINGCLEARVALUE};
  D3D12_INFO_QUEUE_FILTER filter = {};
  filter.DenyList.NumIDs = ARRAYSIZE(hide);
  filter.DenyList.pIDList = hide;
  info_queue->AddStorageFilterEntries(&filter);
}
```

`SetBreakOnSeverity` で、エラーが、起きた、<strong>まさに、その呼び出し</strong>で、デバッガーが、止まり、コール スタックが、原因の行を、指します。ただし、バリアや、同期の、誤りは、<strong>実行時</strong>（`ExecuteCommandLists`）に、報告されることが、多く、記録した、場所では、なく、投げた場所で、止まります。

## オブジェクトに、名前を、付ける

```cpp
device->SetName(L"Main Device");
back_buffers[i]->SetName((L"BackBuffer " + std::to_wstring(i)).c_str());
vertex_buffer->SetName(L"Triangle Vertex Buffer");
constant_buffer->SetName(L"Per-Object Constants");
```

名前が、あると、メッセージと、PIX の画面で、どのオブジェクトか、分かります。「リソース 0x000001... の、状態が、違う」より、「`GBuffer Albedo` の、状態が、違う」の、方が、はるかに、探しやすい。

## DRED：GPU ハングの、原因を、調べる

GPU が、ハングする（無限ループ、不正なアクセス）と、`DXGI_ERROR_DEVICE_REMOVED` が、返ります。<strong>DRED</strong>（Device Removed Extended Data）を、有効にすると、「GPU が、最後に、実行していた、命令」が、分かります。

```cpp
ComPtr<ID3D12DeviceRemovedExtendedDataSettings> dred_settings;
if (SUCCEEDED(D3D12GetDebugInterface(IID_PPV_ARGS(&dred_settings)))) {
  dred_settings->SetAutoBreadcrumbsEnablement(D3D12_DRED_ENABLEMENT_FORCED_ON);   // 実行した命令の、パンくずリスト
  dred_settings->SetPageFaultEnablement(D3D12_DRED_ENABLEMENT_FORCED_ON);         // ページ フォルトの、位置
}
```

```cpp
// DEVICE_REMOVED を検出したら、DRED の情報を、取る。
if (hr == DXGI_ERROR_DEVICE_REMOVED) {
  ComPtr<ID3D12DeviceRemovedExtendedData> dred;
  if (SUCCEEDED(device.As(&dred))) {
    D3D12_DRED_AUTO_BREADCRUMBS_OUTPUT breadcrumbs;
    dred->GetAutoBreadcrumbsOutput(&breadcrumbs);              // どのコマンド リストの、どの命令まで、実行したか
    D3D12_DRED_PAGE_FAULT_OUTPUT page_fault;
    dred->GetPageFaultAllocationOutput(&page_fault);           // 不正アクセスした、アドレスと、近くのリソース
  }
}
```

「パンくずリスト」は、各コマンド リストの、命令の、実行状況（完了、実行中、未実行）を、示します。ハングした、命令を、特定できます。DRED は、設定を、<strong>デバイスを、作る前</strong>に、有効にします。

## GPU ハングの、検出

```cpp
HRESULT hr = swap_chain->Present(1, 0);
if (hr == DXGI_ERROR_DEVICE_REMOVED || hr == DXGI_ERROR_DEVICE_RESET) {
  HRESULT reason = device->GetDeviceRemovedReason();
  // DXGI_ERROR_DEVICE_HUNG: GPU が、応答しない（重すぎる処理、無限ループ）
  // DXGI_ERROR_DEVICE_REMOVED: GPU の、取り外し・ドライバー更新
  // DXGI_ERROR_DRIVER_INTERNAL_ERROR: ドライバーの、内部エラー
  LogError("Device removed: 0x%08X", reason);
}
```

GPU が、2 秒以上、応答しないと、Windows の TDR（Timeout Detection and Recovery）が、ドライバーを、リセットし、デバイスが、失われます。1 回の `Dispatch`・`Draw` を、重くしすぎないように、します。

## 終了時の、リーク検出

```cpp
// 終了時（デバイスを解放する直前）に、生きている、オブジェクトを、一覧にする。
ComPtr<IDXGIDebug1> dxgi_debug;
if (SUCCEEDED(DXGIGetDebugInterface1(0, IID_PPV_ARGS(&dxgi_debug)))) {
  dxgi_debug->ReportLiveObjects(DXGI_DEBUG_ALL, DXGI_DEBUG_RLO_ALL);
}
```

`ComPtr` を、グローバルや `static` に、持つと、デバイスの、解放より、後に、解放され、報告に、出ます。

## グラフィックス デバッガー

デバッグ レイヤーで、分からない、<strong>見た目の問題</strong>は、PIX で、1 フレームを、撮って、各ドロー コールの、入出力を、見ます。

| ツール | 特徴 |
| --- | --- |
| PIX on Windows | D3D12 の、標準。バリア・ヒープ・ディスクリプタの、可視化。GPU キャプチャ |
| RenderDoc | 軽量で、無料。D3D12 にも、対応 |
| NVIDIA Nsight Graphics | NVIDIA 固有の、詳細 |
| AMD Radeon GPU Profiler | AMD 固有の、詳細 |

```cpp
// コマンド リストに、マーカーを、付ける（PIX・RenderDoc で、パスの名前が、見える）。
#include <pix3.h>                                              // WinPixEventRuntime（PIX のヘッダー）
PIXBeginEvent(command_list.Get(), PIX_COLOR(0, 255, 0), L"G-Buffer Pass");
DrawGBuffer();
PIXEndEvent(command_list.Get());
```

## よくあるミス

??? failure "デバッグ レイヤーを、有効にしたのに、メッセージが、出ない"
    `EnableDebugLayer` を、デバイスを、作った後に、呼んでいる。デバイスの作成前に、呼ぶ。

??? failure "バリアの、ミスを、見逃す（見た目は、動く）"
    GPU ベース検証を、使っていない。デバッグ レイヤーだけでは、実行時の、状態違反を、全部は、検出できない。バグの、調査では、GPU ベース検証を、有効に。

??? failure "GPU ハングの、原因が、分からない"
    DRED を、有効にしていない。パンくずリストで、最後に、実行した命令を、特定する。

??? failure "メッセージが、多すぎて、読めない"
    警告の一部を、フィルタで、絞る。`SetBreakOnSeverity` を、エラーだけにして、1 つずつ、直す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] D3D12 は、間違えやすい。デバッグ レイヤーは、必須。デバイス作成の「前」に、有効に
    - [x] GPU ベース検証で、バリアと、ディスクリプタの誤りを、見つける（遅いので、調査時だけ）
    - [x] `ID3D12InfoQueue` で、エラー時に、ブレーク
    - [x] `SetName` で、全オブジェクトに、名前を付ける
    - [x] GPU ハングは、DRED（パンくずリスト）で、原因を、調べる
    - [x] 見た目の問題は、PIX・RenderDoc

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Device and Factory](factory-device.md)
- [Resource Barrier](resource-barrier.md)
- [GPU Queries and Timing](query-timing.md)
- [Debug Layer](../dx11/debug-layer.md)
- [Microsoft Learn: D3D12 デバッグ レイヤー](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/understanding-the-d3d12-debug-layer)
