---
title: ID3D12Fence
tags:
  - DirectX
api:
  - ID3D12Fence
---

# ID3D12Fence

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

GPU の仕事は CPU から見ると、いつ終わるか分かりません。そこで、64 ビットの数字を 1 つ持つ「フェンス」を使います。GPU は仕事が終わるたびに数字を進め CPU はその数字を見て、「ここまで終わった」と判断します。

数字を進める側はキューの `Signal`（GPU が進める）かフェンスの `Signal`（CPU が進める）です。見る側は `GetCompletedValue`（今の数字を見る）と `SetEventOnCompletion`（数字になったら、イベントで知らせてもらう）です。

!!! tip "ポイント"
    - 数字は増えるだけ。前より小さい値を `Signal` しても、戻らない。
    - フレームごとに 1 ずつ増やして、「このフレームの GPU 処理が終わったか」を確認するのが定番。
    - 待つときは `SetEventOnCompletion` と `WaitForSingleObject` を組み合わせる。
    - 終了前には必ず最後の数字まで待ってから、リソースを解放する。

!!! info "このページを読む前に"
    フェンスの作り方とフレームごとの使い方は [Fence](../fence.md) で説明しています。GPU に渡す窓口は [ID3D12CommandQueue](id3d12commandqueue.md) です。

## メソッド一覧

| メソッド | 役割 |
| --- | --- |
| [`GetCompletedValue`](#getcompletedvalue) | 今の数字を読む |
| [`SetEventOnCompletion`](#seteventoncompletion) | 数字が届いたら、イベントを知らせる |
| [`Signal`](#signal) | CPU から数字を進める |

## メソッド

### GetCompletedValue {#getcompletedvalue}

```cpp
UINT64 ID3D12Fence::GetCompletedValue();
```

フェンスの今の数字を返します。引数はありません。

GPU が `Signal` を予約した位置まで仕事を終えていれば、その数字になっています。まだなら前の数字のままです。待たずにすぐ値が返ります。

「自分が予約した数字（`fence_value`）が、`GetCompletedValue()` 以下になったか」で終わったかどうかが分かります。デバイスが削除されたときは `UINT64_MAX` が返ります。この値を終了判定に使うと「終わった」と誤解するので、デバイスの削除は別に確認します。

### SetEventOnCompletion {#seteventoncompletion}

```cpp
HRESULT ID3D12Fence::SetEventOnCompletion(
    UINT64 Value,
    HANDLE hEvent);
```

フェンスの数字が `Value` 以上になったとき `hEvent` のイベントをシグナル状態にするよう頼みます。CPU が待つための準備です。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Value` | `UINT64` | 待ちたい数字 |
| `hEvent` | `HANDLE` | 通知を受け取るイベント（`CreateEventW` で作ったもの） |

この関数自体は待ちません。イベントを登録するだけですぐ戻ります。実際に待つのはそのあとの `WaitForSingleObject` です。

```cpp
if (fence->GetCompletedValue() < value) {            // まだ終わっていなければ
  fence->SetEventOnCompletion(value, fence_event);   // 届いたらイベントを鳴らして
  WaitForSingleObject(fence_event, INFINITE);        // ここで待つ
}
```

`Value` にすでに届いている数字を渡すとイベントは、その場でシグナル状態になります。そのため、上のように先に `GetCompletedValue` で確認しておくと無駄な待ちを避けられます。

`hEvent` に `nullptr` を渡すとこの関数の中で、数字が届くまで待ちます。イベントを作る手間がなく簡単ですが、どこで止まっているのかが分かりにくくなります。戻り値は成功なら `S_OK` です。

### Signal {#signal}

```cpp
HRESULT ID3D12Fence::Signal(UINT64 Value);
```

CPU からフェンスの数字を `Value` にします。GPU は関係なくこの呼び出しの時点で、すぐに数字が変わります。

通常、GPU の終了を知らせるのは、`ID3D12CommandQueue::Signal` です。こちらの `Signal` は CPU が数字を進める用途（複数のスレッドの同期やテストなど）で使います。`Value` は現在の数字より大きいものを渡します。戻り値は成功なら `S_OK` です。

## 関連ページ

- [Fence](../fence.md)
- [ID3D12CommandQueue](id3d12commandqueue.md)
- [Microsoft Learn: ID3D12Fence](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12fence)
