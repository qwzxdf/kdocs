---
title: Debug Layer (D3D12)
tags:
  - DirectX
---

# Debug Layer (D3D12)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

D3D12 はアプリが自分で管理することが多く、間違える場所がたくさんあります。リソースの状態、同期、ディスクリプタ、ルート シグネチャ。間違えてもすぐにはエラーにならず画面が乱れたりときどきクラッシュしたりするだけのことが多く、原因を探すのがとても大変です。

そこで、**デバッグ レイヤー**を使います。API の使い方の誤りを出力ウィンドウにメッセージで教えてくれます。さらに、**GPU ベース検証**は GPU の実行中にバリアの間違いやディスクリプタの不正を見つけます。GPU が止まってしまったときの原因を探る**DRED** もあります。

!!! tip "ポイント"
    - `ID3D12Debug::EnableDebugLayer()` をデバイスを作る前に呼ぶ。
    - GPU ベース検証（`SetEnableGPUBasedValidation`）は遅いが、バリアのミスを正確に見つける。
    - `ID3D12InfoQueue` でエラーが起きたときにデバッガーを止められる。
    - オブジェクトに `SetName` で名前を付ける。メッセージが読みやすくなる。
    - GPU のハング（`DEVICE_REMOVED`）の原因は、DRED（Device Removed Extended Data）で調べる。
    - 製品（Release）では外す。

!!! info "このページを読む前に"
    デバイスを作る順番は [Device and Factory](factory-device.md) で説明しています。メッセージによく出てくる「状態」と「バリア」は [Resource Barrier](resource-barrier.md) が基本です。`EnableDebugLayer` と `D3D12GetDebugInterface` の引数は [Device and Factory](factory-device.md#enabledebuglayer) にあります。

## 有効にする

```cpp
#if defined(_DEBUG)
ComPtr<ID3D12Debug> debug;
if (SUCCEEDED(D3D12GetDebugInterface(IID_PPV_ARGS(&debug)))) {
  debug->EnableDebugLayer();  // デバイスを作る「前」に
}
#endif
```

デバイスを作ったあとで有効にすると、すでにあるデバイスが削除されます。必ず先に呼びます。

## GPU ベース検証

```cpp
#if defined(_DEBUG)
ComPtr<ID3D12Debug1> debug1;
if (SUCCEEDED(debug.As(&debug1))) {
  debug1->SetEnableGPUBasedValidation(TRUE);  // 遅い。バリアやディスクリプタの誤りを、GPU の実行中に検出する
}
#endif
```

ふつうのデバッグ レイヤーは CPU 側（API の呼び出し）の誤りを見つけます。GPU ベース検証はシェーダーに計測用のコードを差し込んで、実行中のリソースの状態違反（バリアの付け忘れ）、ディスクリプタの不正、初期化していないリソースの使用を見つけます。ゲームが数倍遅くなるのでバグを探すときだけ有効にします。

デバッグ レイヤーはパラメーターや状態の組み合わせの誤りを見つけます。コストは小さいか中くらいです。GPU ベース検証はバリアの付け忘れディスクリプタの不正、範囲外のアクセスまで見つけますが、コストは大きく数倍遅くなります。

## メッセージの見え方

```text
D3D12 ERROR: ID3D12CommandQueue::ExecuteCommandLists: Using ResourceBarrier on Command List (0x...):
Before State (0x4: D3D12_RESOURCE_STATE_RENDER_TARGET) specified in transition barrier does not match
with the state (0x0: D3D12_RESOURCE_STATE_PRESENT) specified by the previous call to ResourceBarrier
[ RESOURCE_MANIPULATION ERROR #527: RESOURCE_BARRIER_BEFORE_AFTER_MISMATCH]
```

この例は「バリアの前の状態（`StateBefore`）が、実際の状態と違う」という典型的なエラーです。メッセージにはリソースの名前が出ます。`SetName` で名前を付けておくとどのリソースかがすぐ分かります。

## InfoQueue でエラーのときに止める

```cpp
#include <d3d12sdklayers.h>

ComPtr<ID3D12InfoQueue> info_queue;
if (SUCCEEDED(device.As(&info_queue))) {
  info_queue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_CORRUPTION, TRUE);
  info_queue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_ERROR, TRUE);  // エラーでデバッガーが止まる
  info_queue->SetBreakOnSeverity(D3D12_MESSAGE_SEVERITY_WARNING, FALSE);

  // 既知の無害なメッセージを非表示にする。
  D3D12_MESSAGE_ID hide[] = {D3D12_MESSAGE_ID_CLEARRENDERTARGETVIEW_MISMATCHINGCLEARVALUE};
  D3D12_INFO_QUEUE_FILTER filter = {};
  filter.DenyList.NumIDs = ARRAYSIZE(hide);
  filter.DenyList.pIDList = hide;
  info_queue->AddStorageFilterEntries(&filter);
}
```

`SetBreakOnSeverity` を使うとエラーが起きたその呼び出しで、デバッガーが止まります。コール スタックが原因の行を指します。ただし、バリアや同期の誤りは記録した場所ではなく、実行する `ExecuteCommandLists` の時点で報告されることが多く、止まるのはリストを渡した場所になります。

## オブジェクトに名前を付ける

```cpp
device->SetName(L"Main Device");
back_buffers[i]->SetName((L"BackBuffer " + std::to_wstring(i)).c_str());
vertex_buffer->SetName(L"Triangle Vertex Buffer");
constant_buffer->SetName(L"Per-Object Constants");
```

名前があるとメッセージと PIX の画面で、どのオブジェクトかが分かります。「リソース 0x000001... の状態が違う」というより「`GBuffer Albedo` の状態が違う」のほうが、はるかに探しやすくなります（[Device and Factory](factory-device.md#setname)）。

## DRED で GPU ハングの原因を調べる

GPU が止まる（無限ループや不正なメモリのアクセス）と `DXGI_ERROR_DEVICE_REMOVED` が返ります。ただ、「どの命令で止まったか」は分かりません。**DRED**（Device Removed Extended Data）を有効にすると、GPU が最後に実行していた命令が分かります。

```cpp
ComPtr<ID3D12DeviceRemovedExtendedDataSettings> dred_settings;
if (SUCCEEDED(D3D12GetDebugInterface(IID_PPV_ARGS(&dred_settings)))) {
  dred_settings->SetAutoBreadcrumbsEnablement(D3D12_DRED_ENABLEMENT_FORCED_ON);  // 実行した命令のパンくずリスト
  dred_settings->SetPageFaultEnablement(D3D12_DRED_ENABLEMENT_FORCED_ON);        // ページ フォルトの位置
}
```

```cpp
// DEVICE_REMOVED を検出したら、DRED の情報を取る。
if (hr == DXGI_ERROR_DEVICE_REMOVED) {
  ComPtr<ID3D12DeviceRemovedExtendedData> dred;
  if (SUCCEEDED(device.As(&dred))) {
    D3D12_DRED_AUTO_BREADCRUMBS_OUTPUT breadcrumbs;
    dred->GetAutoBreadcrumbsOutput(&breadcrumbs);  // どのコマンド リストの、どの命令まで実行したか
    D3D12_DRED_PAGE_FAULT_OUTPUT page_fault;
    dred->GetPageFaultAllocationOutput(&page_fault);  // 不正にアクセスしたアドレスと、近くのリソース
  }
}
```

パンくずリストは各コマンド リストの命令が完了、実行中、未実行のどれかを示します。止まった命令を特定できます。DRED の設定はデバイスを作る前に有効にします。

## GPU ハングを検出する

```cpp
HRESULT hr = swap_chain->Present(1, 0);
if (hr == DXGI_ERROR_DEVICE_REMOVED || hr == DXGI_ERROR_DEVICE_RESET) {
  HRESULT reason = device->GetDeviceRemovedReason();
  // DXGI_ERROR_DEVICE_HUNG は、GPU が応答しない（重すぎる処理、無限ループ）。
  // DXGI_ERROR_DEVICE_REMOVED は、GPU の取り外しか、ドライバーの更新。
  // DXGI_ERROR_DRIVER_INTERNAL_ERROR は、ドライバーの内部エラー。
  LogError("Device removed: 0x%08X", reason);
}
```

GPU が 2 秒以上応答しないと Windows の TDR（Timeout Detection and Recovery）が、ドライバーをリセットしてデバイスが失われます。1 回の `Dispatch` や `Draw` を重くしすぎないようにします（[ID3D12Device::GetDeviceRemovedReason](api/id3d12device.md#getdeviceremovedreason)）。

## 終了時のリーク検出

```cpp
// 終了時（デバイスを解放する直前）に、生きているオブジェクトを一覧にする。
ComPtr<IDXGIDebug1> dxgi_debug;
if (SUCCEEDED(DXGIGetDebugInterface1(0, IID_PPV_ARGS(&dxgi_debug)))) {
  dxgi_debug->ReportLiveObjects(DXGI_DEBUG_ALL, DXGI_DEBUG_RLO_ALL);
}
```

`ComPtr` をグローバルや `static` に持つとデバイスより後に解放されて、報告に出ます。

## グラフィックス デバッガー

デバッグ レイヤーで分からない見た目の問題は、PIX で 1 フレームを撮って、各ドロー コールの入力と出力を見ます。PIX on Windows は D3D12 の標準のツールでバリア、ヒープ、ディスクリプタの可視化や GPU キャプチャができます。RenderDoc は軽くて無料で、D3D12 にも対応しています。NVIDIA Nsight Graphics と AMD Radeon GPU Profiler は、それぞれの GPU に固有の詳細を見られます。

```cpp
// コマンド リストにマーカーを付ける（PIX と RenderDoc で、パスの名前が見える）。
#include <pix3.h>  // WinPixEventRuntime（PIX のヘッダー）
PIXBeginEvent(command_list.Get(), PIX_COLOR(0, 255, 0), L"G-Buffer Pass");
DrawGBuffer();
PIXEndEvent(command_list.Get());
```

## よくあるミス

??? failure "デバッグ レイヤーを有効にしたのにメッセージが出ない"
    `EnableDebugLayer` をデバイスを作ったあとに呼んでいます。デバイスの作成前に呼びます。

??? failure "バリアのミスを見逃す（見た目は動く）"
    GPU ベース検証を使っていません。デバッグ レイヤーだけでは実行時の状態違反をすべては見つけられません。バグの調査では GPU ベース検証を有効にします。

??? failure "GPU ハングの原因が分からない"
    DRED を有効にしていません。パンくずリストで最後に実行した命令を特定します。

??? failure "メッセージが多すぎて読めない"
    警告の一部をフィルターで絞ります。`SetBreakOnSeverity` をエラーだけにして 1 つずつ直します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] D3D12 は間違えやすい。デバッグ レイヤーは必須でデバイスを作る前に有効にする
    - [x] GPU ベース検証で、バリアとディスクリプタの誤りを見つける（遅いので調査のときだけ）
    - [x] `ID3D12InfoQueue` でエラーのときにデバッガーを止める
    - [x] `SetName` ですべてのオブジェクトに名前を付ける
    - [x] GPU のハングは、DRED のパンくずリストで原因を調べる
    - [x] 見た目の問題は PIX か RenderDoc で見る

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Device and Factory](factory-device.md)
- [ID3D12Device](api/id3d12device.md)
- [Resource Barrier](resource-barrier.md)
- [GPU Queries and Timing](query-timing.md)
- [Microsoft Learn: D3D12 デバッグ レイヤー](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/understanding-the-d3d12-debug-layer)
