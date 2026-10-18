---
title: Debug Layer (D3D12)
tags:
  - DirectX
---

# Debug Layer (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

D3D12 はリソースの状態、同期、ディスクリプタ、ルート シグネチャと <strong>間違える所が、非常に多い</strong>のでデバッグ レイヤーが、必須です。API の使い方の誤りを出力ウィンドウにメッセージで出しさらに <strong>GPU ベース検証</strong>は、GPU の実行中にバリアの間違いやディスクリプタの不正を検出します。GPU がハングしたときの原因を探る <strong>DRED</strong> もあります。

!!! tip "ポイント"
    - `ID3D12Debug::EnableDebugLayer()` を <strong>デバイスを作る前</strong>に呼ぶ。
    - <strong>GPU ベース検証</strong>（`SetEnableGPUBasedValidation`）は遅いが、バリアのミスを正確に見つける。
    - `ID3D12InfoQueue` でエラーの時にブレーク（止める）できる。
    - オブジェクトに `SetName` で、名前を付ける。メッセージが読みやすくなる。
    - GPU ハング（`DEVICE_REMOVED`）の原因は、<strong>DRED</strong>（Device Removed Extended Data）で、調べる。
    - 製品（Release）では外す。

## 有効にする

```cpp
#if defined(_DEBUG)
ComPtr<ID3D12Debug> debug;
if (SUCCEEDED(D3D12GetDebugInterface(IID_PPV_ARGS(&debug)))) {
  debug->EnableDebugLayer();                                    // デバイスを作る「前」に
}
#endif
```

デバイスを作った後で有効にすると既存のデバイスが削除されます。必ず先に呼びます（[Device and Factory](factory-device.md)）。

## GPU ベース検証

```cpp
#if defined(_DEBUG)
ComPtr<ID3D12Debug1> debug1;
if (SUCCEEDED(debug.As(&debug1))) {
  debug1->SetEnableGPUBasedValidation(TRUE);                   // 遅い。バリア、ディスクリプタの誤りを、GPU 実行中に、検出
}
#endif
```

通常の、デバッグ レイヤーは <strong>CPU 側</strong>（API の呼び出し）の誤りを検出します。GPU ベース検証はシェーダーに <strong>計測コードを挿入</strong>して実行中のリソースの <strong>状態違反</strong>（バリア忘れ）、<strong>ディスクリプタの不正</strong>、未初期化のリソースを検出します。ゲームが数倍、遅くなるのでバグを探すときだけ有効にします。

| 検証 | 検出するもの | コスト |
| --- | --- | --- |
| デバッグ レイヤー | API の使い方の誤り（パラメータ、状態の組み合わせ） | 小〜中 |
| GPU ベース検証 | バリア忘れディスクリプタの不正、範囲外アクセス | 大（数倍遅い） |

## メッセージの見え方

```text
D3D12 ERROR: ID3D12CommandQueue::ExecuteCommandLists: Using ResourceBarrier on Command List (0x...):
Before State (0x4: D3D12_RESOURCE_STATE_RENDER_TARGET) specified in transition barrier does not match
with the state (0x0: D3D12_RESOURCE_STATE_PRESENT) specified by the previous call to ResourceBarrier
[ RESOURCE_MANIPULATION ERROR #527: RESOURCE_BARRIER_BEFORE_AFTER_MISMATCH]
```

この例は「バリアの `StateBefore` が実際の状態と違う」という典型的なエラーです。メッセージにリソースの名前（`SetName` で、付けた物）が出るのでどのリソースかすぐ分かります。

## InfoQueue：エラーで止める

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

`SetBreakOnSeverity` でエラーが起きた <strong>まさにその呼び出し</strong>でデバッガーが止まりコール スタックが原因の行を、指します。ただし、バリアや同期の誤りは <strong>実行時</strong>（`ExecuteCommandLists`）に報告されることが多く記録した場所ではなく投げた場所で止まります。

## オブジェクトに名前を付ける

```cpp
device->SetName(L"Main Device");
back_buffers[i]->SetName((L"BackBuffer " + std::to_wstring(i)).c_str());
vertex_buffer->SetName(L"Triangle Vertex Buffer");
constant_buffer->SetName(L"Per-Object Constants");
```

名前があるとメッセージと PIX の画面で、どのオブジェクトか分かります。「リソース 0x000001... の状態が、違う」より「`GBuffer Albedo` の状態が違う」の方が、はるかに探しやすい。

## DRED：GPU ハングの原因を調べる

GPU がハングする（無限ループ、不正なアクセス）と `DXGI_ERROR_DEVICE_REMOVED` が返ります。<strong>DRED</strong>（Device Removed Extended Data）を、有効にすると「GPU が最後に実行していた命令」が分かります。

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

「パンくずリスト」は各コマンド リストの命令の実行状況（完了、実行中、未実行）を示します。ハングした命令を特定できます。DRED は設定を <strong>デバイスを作る前</strong>に有効にします。

## GPU ハングの検出

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

GPU が 2 秒以上、応答しないと Windows の TDR（Timeout Detection and Recovery）が、ドライバーをリセットしデバイスが、失われます。1 回の `Dispatch`・`Draw` を重くしすぎないようにします。

## 終了時のリーク検出

```cpp
// 終了時（デバイスを解放する直前）に、生きている、オブジェクトを、一覧にする。
ComPtr<IDXGIDebug1> dxgi_debug;
if (SUCCEEDED(DXGIGetDebugInterface1(0, IID_PPV_ARGS(&dxgi_debug)))) {
  dxgi_debug->ReportLiveObjects(DXGI_DEBUG_ALL, DXGI_DEBUG_RLO_ALL);
}
```

`ComPtr` をグローバルや `static` に持つとデバイスの解放より後に解放され報告に出ます。

## グラフィックス デバッガー

デバッグ レイヤーで分からない、<strong>見た目の問題</strong>は PIX で、1 フレームを撮って各ドロー コールの入出力を見ます。

| ツール | 特徴 |
| --- | --- |
| PIX on Windows | D3D12 の標準。バリア・ヒープ・ディスクリプタの可視化。GPU キャプチャ |
| RenderDoc | 軽量で無料。D3D12 にも対応 |
| NVIDIA Nsight Graphics | NVIDIA 固有の、詳細 |
| AMD Radeon GPU Profiler | AMD 固有の詳細 |

```cpp
// コマンド リストに、マーカーを、付ける（PIX・RenderDoc で、パスの名前が、見える）。
#include <pix3.h>                                              // WinPixEventRuntime（PIX のヘッダー）
PIXBeginEvent(command_list.Get(), PIX_COLOR(0, 255, 0), L"G-Buffer Pass");
DrawGBuffer();
PIXEndEvent(command_list.Get());
```

## よくあるミス

??? failure "デバッグ レイヤーを有効にしたのにメッセージが出ない"
    `EnableDebugLayer` をデバイスを作った後に呼んでいる。デバイスの作成前に呼ぶ。

??? failure "バリアのミスを見逃す（見た目は動く）"
    GPU ベース検証を使っていない。デバッグ レイヤーだけでは実行時の状態違反を全部は検出できない。バグの調査では GPU ベース検証を有効に。

??? failure "GPU ハングの原因が、分からない"
    DRED を有効にしていない。パンくずリストで最後に実行した命令を特定する。

??? failure "メッセージが、多すぎて読めない"
    警告の一部をフィルタで絞る。`SetBreakOnSeverity` をエラーだけにして 1 つずつ直す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] D3D12 は間違えやすい。デバッグ レイヤーは必須。デバイス作成の「前」に有効に
    - [x] GPU ベース検証で、バリアとディスクリプタの誤りを見つける（遅いので調査時だけ）
    - [x] `ID3D12InfoQueue` でエラー時にブレーク
    - [x] `SetName` で全オブジェクトに名前を付ける
    - [x] GPU ハングは、DRED（パンくずリスト）で原因を調べる
    - [x] 見た目の問題は PIX・RenderDoc

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Device and Factory](factory-device.md)
- [Resource Barrier](resource-barrier.md)
- [GPU Queries and Timing](query-timing.md)
- [Debug Layer](../dx11/debug-layer.md)
- [Microsoft Learn: D3D12 デバッグ レイヤー](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/understanding-the-d3d12-debug-layer)
