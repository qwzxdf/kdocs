---
title: Fence
tags:
  - DirectX
---

# Fence

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>フェンス</strong>（`ID3D12Fence`）は <strong>CPU と GPU（または、GPU 同士）の同期</strong>の道具です。中身は <strong>1 つの 64 ビットの整数</strong>で「GPU がここまで、終わった」という <strong>目印</strong>を書き込み CPU がその値を読むまたは、その値になるまで待ちます。D3D12 では GPU が非同期に動くので「いつリソースを再利用してよいか」を知る唯一の、方法です。

!!! tip "ポイント"
    - フェンス ＝ 増えていく整数。GPU が `Signal` で値を書く。CPU が `GetCompletedValue` で読む。
    - 使い方: <strong>`Signal(fence, N)` をキューに積む → GPU が、そこまで実行したら値が N に → CPU は、値が N になるまで待つ</strong>。
    - CPU が待つにはイベント（`HANDLE`）に `SetEventOnCompletion` で結びつけ `WaitForSingleObject`。
    - 値は <strong>単調に増やす</strong>。フレームごとに `+1`。
    - フレーム イン フライト、終了時の全完了待ちアップロードの完了確認に必須。

## 作る

```cpp
ComPtr<ID3D12Fence> fence;
UINT64 fence_value = 0;                                      // 次に、Signal する値
HANDLE fence_event = CreateEventW(nullptr, FALSE, FALSE, nullptr);   // CPU が、待つための、イベント

device->CreateFence(0,                                       // 初期値
                    D3D12_FENCE_FLAG_NONE,
                    IID_PPV_ARGS(&fence));
```

イベントは Win32 の `CreateEventW` で、作ります。フェンスが目的の値に達したとき GPU（ドライバー）がこのイベントをシグナル状態にします。

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
| `ID3D12CommandQueue::Signal(fence, value)` | CPU（積むだけ） | GPU が、そこまで実行したらフェンスに `value` を書く |
| `ID3D12Fence::GetCompletedValue()` | CPU | 今、フェンスに書かれている値を返す（待たない） |
| `ID3D12Fence::SetEventOnCompletion(value, event)` | CPU | フェンスが `value` 以上になったら、イベントをシグナルする |
| `WaitForSingleObject(event, timeout)` | CPU | イベントが、シグナルするまで待つ（Win32） |
| `ID3D12CommandQueue::Wait(fence, value)` | CPU（積むだけ） | <strong>キューを</strong>、フェンスが `value` になるまで止める（GPU の待ち） |
| `ID3D12Fence::Signal(value)` | CPU | CPU が直接、フェンスに値を書く（まれ） |

流れを図にすると次のとおりです。

```text
CPU:  ExecuteCommandLists(list)        ← 仕事を、キューに、投げる
      Signal(fence, 5)                  ← 「ここまで終わったら、5 を書いて」を、キューに、積む
      （CPU は、先へ進める）
GPU:  list を実行 …… 終わった → フェンスに 5 を、書く
CPU:  GetCompletedValue() == 5 ?        ← 5 になっていれば、list の使った、リソースは、再利用できる
```

## フレーム イン フライト

CPU が次のフレームを記録している間、GPU は前のフレームを実行しています。<strong>フレームごとにフェンスの値を覚えておき</strong>、そのフレームのリソース（アロケーター、定数バッファ）を再利用する前にその値に達したかを確認します。

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

フレーム イン フライトが 2 なら CPU は GPU より最大 2 フレーム、先に進めます（[Frame Resources](frame-resources.md)）。

## 複数のキューの同期

別のキュー（COMPUTE と DIRECT）の順序を <strong>GPU の中で</strong>、そろえるには `Signal` と `Wait` を使います。CPU は止まりません。

```cpp
// COMPUTE キューの仕事が、終わるまで、DIRECT キューを、待たせる。
compute_queue->ExecuteCommandLists(1, compute_lists);
compute_queue->Signal(compute_fence.Get(), ++compute_value);          // COMPUTE が、ここまで終わったら、値を書く

direct_queue->Wait(compute_fence.Get(), compute_value);               // DIRECT は、その値になるまで、止まる（GPU の待ち）
direct_queue->ExecuteCommandLists(1, direct_lists);                   // 計算結果を、使う描画
```

`ID3D12CommandQueue::Wait` は CPU を止めず <strong>GPU のキューを</strong>、止めます。非同期コンピュートの結果を描画で、使うときの定番です（[Command Queue](command-queue.md)）。

## 終了時の後始末

```cpp
void Shutdown() {
  WaitForGpu();                                              // GPU が、全部終わるのを、待つ
  CloseHandle(fence_event);
  // この後で、リソース、コマンド キュー、デバイスを、解放する
}
```

GPU がまだ実行中のリソースを解放するとクラッシュします。終了前に必ずフェンスで待ちます。

## タイムアウトと GPU のハング

```cpp
DWORD result = WaitForSingleObject(fence_event, 5000);       // 5 秒で、タイムアウト
if (result == WAIT_TIMEOUT) {
  // GPU が、返ってこない（ハング）。デバイスの、状態を、確認する。
  HRESULT reason = device->GetDeviceRemovedReason();
}
```

`INFINITE` で待つと GPU がハングしたとき永久に止まります。製品ではタイムアウトを設定して `GetDeviceRemovedReason` で原因を記録します（[Debug Layer](debug-layer.md)）。

## よくあるミス

??? failure "画面が乱れる、またはクラッシュする（再現が不安定）"
    フェンスで完了を待たずにアロケーターを `Reset` したまたは、GPU が使用中のリソースを書き換えた。

??? failure "フレームレートが異様に低い"
    毎フレーム、`WaitForGpu`（全完了待ち）をしている。CPU と GPU が直列になり並列性が失われる。フレーム イン フライト（2〜3）で、1 フレームずつ遅れて待つ。

??? failure "終了時にクラッシュする"
    終了前に GPU の完了を待っていない。

??? failure "`WaitForSingleObject` で永久に止まる"
    `Signal` をキューに積んでいないまたは `SetEventOnCompletion` の値が、`Signal` した値と違う。GPU がハングしている（タイムアウトを設定する）。

??? failure "フェンスの値が、巻き戻る・同じ値で 2 回待つ"
    値は単調に増やす。使い回す変数を複数の場所で更新して順序が、崩れている。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フェンス ＝ 増える整数。GPU が `Signal` で書き CPU が、読む・待つ
    - [x] 待つ: `SetEventOnCompletion(value, event)` + `WaitForSingleObject`
    - [x] 毎フレーム、全完了待ちはしない。フェンスの値をフレームごとに覚える
    - [x] キュー同士は `Signal` + `Wait`（GPU の待ち）
    - [x] 終了前に全完了を待つ。タイムアウトを設定する

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Command Queue](command-queue.md)
- [Command Allocator](command-allocator.md)
- [Frame Resources](frame-resources.md)
- [Microsoft Learn: ID3D12Fence](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12fence)
