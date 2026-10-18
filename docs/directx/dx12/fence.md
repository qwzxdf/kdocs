---
title: Fence
tags:
  - DirectX
---

# Fence

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>フェンス</strong>（`ID3D12Fence`）は、<strong>CPU と GPU（または、GPU 同士）の、同期</strong>の、道具です。中身は、<strong>1 つの、64 ビットの、整数</strong>で、「GPU が、ここまで、終わった」という、<strong>目印</strong>を、書き込み、CPU が、その値を、読む、または、その値に、なるまで、待ちます。D3D12 では、GPU が、非同期に、動くので、「いつ、リソースを、再利用してよいか」を、知る、唯一の、方法です。

!!! tip "ポイント"
    - フェンス ＝ 増えていく、整数。GPU が、`Signal` で、値を、書く。CPU が、`GetCompletedValue` で、読む。
    - 使い方: <strong>`Signal(fence, N)` を、キューに積む → GPU が、そこまで、実行したら、値が N に → CPU は、値が N になるまで、待つ</strong>。
    - CPU が、待つには、イベント（`HANDLE`）に、`SetEventOnCompletion` で、結びつけ、`WaitForSingleObject`。
    - 値は、<strong>単調に、増やす</strong>。フレームごとに、`+1`。
    - フレーム イン フライト、終了時の、全完了待ち、アップロードの、完了確認に、必須。

## 作る

```cpp
ComPtr<ID3D12Fence> fence;
UINT64 fence_value = 0;                                      // 次に、Signal する値
HANDLE fence_event = CreateEventW(nullptr, FALSE, FALSE, nullptr);   // CPU が、待つための、イベント

device->CreateFence(0,                                       // 初期値
                    D3D12_FENCE_FLAG_NONE,
                    IID_PPV_ARGS(&fence));
```

イベントは、Win32 の `CreateEventW` で、作ります。フェンスが、目的の、値に、達した、とき、GPU（ドライバー）が、このイベントを、シグナル状態に、します。

## Signal と待ち

```cpp
// GPU の、現在の仕事が、終わるまで、CPU が、待つ（最も、単純な形）。
void WaitForGpu() {
  const UINT64 value = ++fence_value;                        // 次の目印の値
  command_queue->Signal(fence.Get(), value);                 // キューに「ここまで終わったら、value を書く」を、積む
  if (fence->GetCompletedValue() < value) {                  // GPU が、まだ、そこまで、来ていなければ
    fence->SetEventOnCompletion(value, fence_event);         // value に達したら、イベントを、シグナルする
    WaitForSingleObject(fence_event, INFINITE);              // CPU は、ここで、眠る
  }
}
```

| 関数 | 呼ぶ側 | 内容 |
| --- | --- | --- |
| `ID3D12CommandQueue::Signal(fence, value)` | CPU（積むだけ） | GPU が、そこまで、実行したら、フェンスに `value` を書く |
| `ID3D12Fence::GetCompletedValue()` | CPU | 今、フェンスに、書かれている、値を、返す（待たない） |
| `ID3D12Fence::SetEventOnCompletion(value, event)` | CPU | フェンスが `value` 以上になったら、イベントを、シグナルする |
| `WaitForSingleObject(event, timeout)` | CPU | イベントが、シグナルするまで、待つ（Win32） |
| `ID3D12CommandQueue::Wait(fence, value)` | CPU（積むだけ） | <strong>キューを</strong>、フェンスが `value` になるまで、止める（GPU の、待ち） |
| `ID3D12Fence::Signal(value)` | CPU | CPU が、直接、フェンスに、値を書く（まれ） |

流れを、図にすると、次のとおりです。

```text
CPU:  ExecuteCommandLists(list)        ← 仕事を、キューに、投げる
      Signal(fence, 5)                  ← 「ここまで終わったら、5 を書いて」を、キューに、積む
      （CPU は、先へ進める）
GPU:  list を実行 …… 終わった → フェンスに 5 を、書く
CPU:  GetCompletedValue() == 5 ?        ← 5 になっていれば、list の使った、リソースは、再利用できる
```

## フレーム イン フライト

CPU が、次のフレームを、記録している間、GPU は、前のフレームを、実行しています。<strong>フレームごとに、フェンスの、値を、覚えておき</strong>、そのフレームの、リソース（アロケーター、定数バッファ）を、再利用する前に、その値に、達したかを、確認します。

```cpp
UINT64 frame_fence_values[kFrameCount] = {};                 // 各フレームの、「ここまで終われば、再利用できる」値

void BeginFrame(UINT frame_index) {
  // このフレーム用の、リソースを、前に、使った、フレームの、GPU 完了を、待つ。
  const UINT64 needed = frame_fence_values[frame_index];
  if (fence->GetCompletedValue() < needed) {
    fence->SetEventOnCompletion(needed, fence_event);
    WaitForSingleObject(fence_event, INFINITE);
  }
  allocators[frame_index]->Reset();                          // 安全に、Reset できる
}

void EndFrame(UINT frame_index) {
  command_queue->Signal(fence.Get(), ++fence_value);         // このフレームの、完了の、目印
  frame_fence_values[frame_index] = fence_value;
}
```

フレーム イン フライトが、2 なら、CPU は、GPU より、最大 2 フレーム、先に、進めます（[Frame Resources](frame-resources.md)）。

## 複数のキューの、同期

別の、キュー（COMPUTE と DIRECT）の、順序を、<strong>GPU の中で</strong>、そろえるには、`Signal` と `Wait` を、使います。CPU は、止まりません。

```cpp
// COMPUTE キューの仕事が、終わるまで、DIRECT キューを、待たせる。
compute_queue->ExecuteCommandLists(1, compute_lists);
compute_queue->Signal(compute_fence.Get(), ++compute_value);          // COMPUTE が、ここまで終わったら、値を書く

direct_queue->Wait(compute_fence.Get(), compute_value);               // DIRECT は、その値になるまで、止まる（GPU の待ち）
direct_queue->ExecuteCommandLists(1, direct_lists);                   // 計算結果を、使う描画
```

`ID3D12CommandQueue::Wait` は、CPU を、止めず、<strong>GPU の、キューを</strong>、止めます。非同期コンピュートの、結果を、描画で、使うときの、定番です（[Command Queue](command-queue.md)）。

## 終了時の、後始末

```cpp
void Shutdown() {
  WaitForGpu();                                              // GPU が、全部終わるのを、待つ
  CloseHandle(fence_event);
  // この後で、リソース、コマンド キュー、デバイスを、解放する
}
```

GPU が、まだ、実行中の、リソースを、解放すると、クラッシュします。終了前に、必ず、フェンスで、待ちます。

## タイムアウトと、GPU のハング

```cpp
DWORD result = WaitForSingleObject(fence_event, 5000);       // 5 秒で、タイムアウト
if (result == WAIT_TIMEOUT) {
  // GPU が、返ってこない（ハング）。デバイスの、状態を、確認する。
  HRESULT reason = device->GetDeviceRemovedReason();
}
```

`INFINITE` で、待つと、GPU が、ハングしたとき、永久に、止まります。製品では、タイムアウトを、設定して、`GetDeviceRemovedReason` で、原因を、記録します（[Debug Layer](debug-layer.md)）。

## よくあるミス

??? failure "画面が、乱れる、またはクラッシュする（再現が不安定）"
    フェンスで、完了を、待たずに、アロケーターを、`Reset` した、または、GPU が、使用中の、リソースを、書き換えた。

??? failure "フレームレートが、異様に、低い"
    毎フレーム、`WaitForGpu`（全完了待ち）を、している。CPU と GPU が、直列に、なり、並列性が、失われる。フレーム イン フライト（2〜3）で、1 フレームずつ、遅れて、待つ。

??? failure "終了時に、クラッシュする"
    終了前に、GPU の、完了を、待っていない。

??? failure "`WaitForSingleObject` で、永久に、止まる"
    `Signal` を、キューに、積んでいない、または、`SetEventOnCompletion` の、値が、`Signal` した、値と、違う。GPU が、ハングしている（タイムアウトを、設定する）。

??? failure "フェンスの値が、巻き戻る・同じ値で、2 回待つ"
    値は、単調に、増やす。使い回す変数を、複数の、場所で、更新して、順序が、崩れている。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フェンス ＝ 増える整数。GPU が `Signal` で書き、CPU が、読む・待つ
    - [x] 待つ: `SetEventOnCompletion(value, event)` + `WaitForSingleObject`
    - [x] 毎フレーム、全完了待ちは、しない。フェンスの値を、フレームごとに、覚える
    - [x] キュー同士は、`Signal` + `Wait`（GPU の待ち）
    - [x] 終了前に、全完了を、待つ。タイムアウトを、設定する

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Command Queue](command-queue.md)
- [Command Allocator](command-allocator.md)
- [Frame Resources](frame-resources.md)
- [Microsoft Learn: ID3D12Fence](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12fence)
