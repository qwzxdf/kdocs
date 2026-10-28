---
title: Fence
tags:
  - DirectX
---

# Fence

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

`ExecuteCommandLists` で仕事を渡すと GPU はそれを非同期に実行します。CPU から見るといつ終わるのかが分かりません。ところが、そのリストが使っているアロケーターやバッファは、GPU が終わるまで再利用も解放もできません。「GPU がここまで終わった」と知る方法が必要です。

その方法が<strong>フェンス</strong>（`ID3D12Fence`）です。中身は 64 ビットの整数が 1 つあるだけです。GPU が仕事を終えるたびにこの数字を進めます。CPU はその数字を読むか特定の数字になるまで待ちます。

!!! tip "ポイント"
    - フェンスは増えていく整数。GPU が `Signal` で書き CPU が `GetCompletedValue` で読む。
    - 使い方は `Signal(fence, N)` をキューに積み GPU がそこまで実行すると値が N になり、CPU がそれを確認する。
    - CPU が待つには `SetEventOnCompletion` でイベントを結び `WaitForSingleObject` で待つ。
    - 値は増やすだけで、減らさない。1 フレームごとに 1 増やすのが定番。
    - フレームの同時進行、終了時の全完了待ちアップロードの完了確認に必ず使う。

!!! info "このページを読む前に"
    `Signal` を積む窓口は [Command Queue](command-queue.md)、フェンスで守る相手は [Command Allocator](command-allocator.md) です。Win32 のイベント（`HANDLE`）が出てきますが、このページの範囲で使い方を説明します。メソッドの引数と戻り値は [ID3D12Fence](api/id3d12fence.md) にあります。

## 作る

```cpp
ComPtr<ID3D12Fence> fence;
UINT64 fence_value = 0;                                             // 次に Signal する値
HANDLE fence_event = CreateEventW(nullptr, FALSE, FALSE, nullptr);  // CPU が待つためのイベント

device->CreateFence(0,  // 初期値
                    D3D12_FENCE_FLAG_NONE,
                    IID_PPV_ARGS(&fence));
```

イベントは Win32 の `CreateEventW` で作ります。フェンスが目的の値に届いたときドライバーがこのイベントをシグナル状態にします。CPU はそのイベントを `WaitForSingleObject` で待ちます。

## 目印を積んで待つ

<svg class="fig flow" viewBox="0 0 720 276" role="img" aria-label="フェンスの値で、GPU の完了を知る"><defs><marker id="fe" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">Signal で目印を積み、値が届いたら完了</text><text x="12" y="76" text-anchor="start" style="font-size:12px;font-weight:700">CPU</text><text x="12" y="146" text-anchor="start" style="font-size:12px;font-weight:700">GPU</text><text x="12" y="206" text-anchor="start" style="font-size:12px;font-weight:700">フェンス</text><rect x="70" y="56" width="150" height="36" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="145.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">ExecuteCommandLists</text><rect x="230" y="56" width="120" height="36" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="290.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">Signal(fence, 5)</text><rect x="360" y="56" width="230" height="36" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="475.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">別の仕事を進める（待たない）</text><rect x="70" y="126" width="280" height="36" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="210.0" y="144.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">リストを実行している…</text><rect x="350" y="126" width="90" height="36" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="395.0" y="144.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">5 を書く</text><line x1="290" y1="92" x2="290" y2="126" stroke="currentColor" stroke-width="2" marker-end="url(#fe)"/><rect x="70" y="188" width="60" height="34" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="100.0" y="205.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">4</text><rect x="440" y="188" width="70" height="34" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="475.0" y="205.0" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">5</text><line x1="395" y1="162" x2="460" y2="188" stroke="currentColor" stroke-width="2" marker-end="url(#fe)"/><rect x="600" y="56" width="110" height="36" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="655.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">値が 5 か確認</text><line x1="480" y1="188" x2="650" y2="92" stroke="currentColor" stroke-width="2" marker-end="url(#fe)"/><text x="360" y="258" text-anchor="middle" style="font-size:12px;font-weight:400">CPU は、フェンスの値が 5 になったら「この仕事は終わった」と分かる。</text></svg>

上の図の流れをそのままコードにしたのが、次の関数です。GPU がここまでの仕事を終えるのを CPU が待ちます。

```cpp
void WaitForGpu() {
  const UINT64 value = ++fence_value;         // 次の目印の値
  command_queue->Signal(fence.Get(), value);  // 「ここまで終わったら value を書く」をキューに積む
  if (fence->GetCompletedValue() < value) {   // GPU がまだそこまで来ていなければ
    fence->SetEventOnCompletion(value, fence_event);  // value に届いたらイベントを鳴らす
    WaitForSingleObject(fence_event, INFINITE);       // CPU はここで眠る
  }
}
```

`command_queue->Signal` はキューの中に「ここまでの仕事が終わったら、この数字を書く」という命令を積みます。積むだけで CPU は待ちません。GPU がその位置まで来ると、フェンスの数字が `value` になります。

`GetCompletedValue` は今の数字をすぐ返します。すでに届いていれば待つ必要がありません。先に確認しておくと無駄な待ちを避けられます。

`SetEventOnCompletion` は「数字が `value` 以上になったら、このイベントを鳴らしてください」という予約です。この関数自体は待たずに戻ります。実際に待つのはそのあとの `WaitForSingleObject` です。

`ID3D12Fence::Signal` のように CPU から直接フェンスの数字を書く方法もありますが、まれにしか使いません。GPU の完了を知るときはキューの `Signal` を使います。

## フレームを同時に進める

CPU が次のフレームを記録している間、GPU は前のフレームを実行しています。1 フレームごとに全完了を待つと CPU と GPU が交互にしか動けず並列性が失われます。そこで、フレームごとに「ここまで終われば再利用してよい」という値を覚えておき再利用の直前にその値だけを確認します。

```cpp
UINT64 frame_fence_values[kFrameCount] = {};  // 各フレームの「ここまで終われば再利用できる」値

void BeginFrame(UINT frame_index) {
  // このフレーム用のリソースを前に使ったフレームが GPU で終わるのを待つ。
  const UINT64 needed = frame_fence_values[frame_index];
  if (fence->GetCompletedValue() < needed) {
    fence->SetEventOnCompletion(needed, fence_event);
    WaitForSingleObject(fence_event, INFINITE);
  }
  allocators[frame_index]->Reset();  // これで安全に Reset できる
}

void EndFrame(UINT frame_index) {
  command_queue->Signal(fence.Get(), ++fence_value);  // このフレームの完了の目印
  frame_fence_values[frame_index] = fence_value;
}
```

同時に進めるフレームが 2 つなら CPU は GPU より最大 2 フレーム先に進めます。考え方の詳細は [Frame Resources](frame-resources.md) にあります。

## 複数のキューの順番をそろえる

COMPUTE と DIRECT のように別のキューの順番をそろえたいときは、`Signal` と `Wait` を使います。`ID3D12CommandQueue::Wait` は CPU を止めず**GPU のキューだけを止めます**。

```cpp
// COMPUTE の仕事が終わるまで、DIRECT のキューを待たせる。
compute_queue->ExecuteCommandLists(1, compute_lists);
compute_queue->Signal(compute_fence.Get(), ++compute_value);  // COMPUTE がここまで終わったら値を書く

direct_queue->Wait(compute_fence.Get(), compute_value);  // DIRECT は、その値になるまで止まる（GPU の待ち）
direct_queue->ExecuteCommandLists(1, direct_lists);      // 計算の結果を使う描画
```

非同期コンピュートの結果を描画で使うときの定番の形です（[Command Queue](command-queue.md)）。

## 終了するときの後始末

アプリを終了するときは GPU が使っているリソースを解放しないために全完了を待ちます。

```cpp
void Shutdown() {
  WaitForGpu();  // GPU がすべて終わるのを待つ
  CloseHandle(fence_event);
  // このあとで、リソース、コマンド キュー、デバイスを解放する
}
```

GPU がまだ実行中のリソースを解放すると、クラッシュします。

## タイムアウトと GPU のハング

`INFINITE` で待つと GPU がハングしたときに CPU が永久に止まります。製品ではタイムアウトを付けて、原因を記録します。

```cpp
DWORD result = WaitForSingleObject(fence_event, 5000);  // 5 秒でタイムアウト
if (result == WAIT_TIMEOUT) {
  // GPU が返ってこない（ハング）。デバイスの状態を確認する。
  HRESULT reason = device->GetDeviceRemovedReason();
}
```

`GetDeviceRemovedReason` の見方は [ID3D12Device](api/id3d12device.md#getdeviceremovedreason) にあります。

## よくあるミス

??? failure "画面が乱れる、またはクラッシュする（再現が不安定）"
    フェンスで完了を待たずにアロケーターを `Reset` したか GPU が使用中のリソースを書き換えています。

??? failure "フレームレートが異様に低い"
    毎フレーム `WaitForGpu` で全完了を待っています。CPU と GPU が直列になります。フレームを 2〜3 つ同時に進めて、1 フレームずつ遅れて待ちます。

??? failure "終了時にクラッシュする"
    終了前に GPU の完了を待っていません。

??? failure "`WaitForSingleObject` で永久に止まる"
    `Signal` をキューに積んでいないか `SetEventOnCompletion` の値が `Signal` した値と違います。GPU がハングしている場合もあるので、タイムアウトを付けます。

??? failure "フェンスの値が巻き戻る同じ値で 2 回待つ"
    値は増やすだけです。1 つの変数を複数の場所で更新して、順番が崩れていないか確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フェンスは増える整数。GPU が `Signal` で書き CPU が読むか待つ
    - [x] 待つときは `SetEventOnCompletion` と `WaitForSingleObject`
    - [x] 毎フレーム全完了を待たずフレームごとに値を覚える
    - [x] キューどうしは `Signal` と `Wait`（GPU の待ち）
    - [x] 終了前に全完了を待つ。タイムアウトを付ける

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3D12Fence](api/id3d12fence.md)
- [Command Queue](command-queue.md)
- [Command Allocator](command-allocator.md)
- [Frame Resources](frame-resources.md)
- [Microsoft Learn: ID3D12Fence](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12fence)
