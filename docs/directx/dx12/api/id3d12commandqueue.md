---
title: ID3D12CommandQueue
tags:
  - DirectX
api:
  - ID3D12CommandQueue
---

# ID3D12CommandQueue

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

コマンド リストに記録しただけでは GPU は何もしません。記録したリストを GPU に渡して、実行を頼むための窓口が `ID3D12CommandQueue` です。キューに渡したリストは渡した順に GPU が実行します。

渡す作業は CPU を待たせずにすぐ戻ります。「いつ終わるか」はキューのメソッドでは分からずフェンスで調べます。このため `ID3D12CommandQueue` のメソッドはリストを渡す `ExecuteCommandLists` とフェンスを使う `Signal`、`Wait` が中心になります。

!!! tip "ポイント"
    - 渡すリストは必ず `Close` したもの。
    - `ExecuteCommandLists` は待たずに戻る。終わったかどうかはフェンスで確認する。
    - 同じキューに渡したものは、渡した順に実行される。別のキューどうしは並列に動ける。
    - `Signal` は「ここまで終わったら、この数字を書く」という GPU への予約。

!!! info "このページを読む前に"
    キューの作り方と種類は [Command Queue](../command-queue.md)、記録は [ID3D12GraphicsCommandList](id3d12graphicscommandlist.md)、フェンスの使い方は [Fence](../fence.md) で説明しています。

## メソッド一覧

| メソッド | 役割 |
| --- | --- |
| [`ExecuteCommandLists`](#executecommandlists) | 記録したリストを GPU に渡す |
| [`Signal`](#signal) | キューの処理がここまで終わったら、フェンスの数字を進める |
| [`Wait`](#wait) | フェンスが指定の数字になるまで、キューを止める |
| [`GetTimestampFrequency`](#gettimestampfrequency) | タイムスタンプの 1 秒あたりの刻み数 |

## メソッド

### ExecuteCommandLists {#executecommandlists}

```cpp
void ID3D12CommandQueue::ExecuteCommandLists(
    UINT NumCommandLists,
    ID3D12CommandList* const* ppCommandLists);
```

記録の終わったコマンド リストを GPU に渡します。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `NumCommandLists` | `UINT` | リストの数 |
| `ppCommandLists` | `ID3D12CommandList* const*` | リストの配列 |

`ppCommandLists` は `ID3D12CommandList*`（基底クラス）の配列です。`ID3D12GraphicsCommandList*` は自動で変換できますが配列を作るときは、基底クラスの型で宣言します。

```cpp
ID3D12CommandList* lists[] = {command_list.Get()};
command_queue->ExecuteCommandLists(1, lists);
```

渡すリストはすべて `Close` 済みでなければいけません。閉じていないリストを渡すとデバッグ レイヤーがエラーを出し、最悪の場合はデバイスが削除されます。リストの種類はキューが受け付ける種類と合っている必要があります（DIRECT のキューは、全種類。COMPUTE のキューに DIRECT のリストは渡せません）。

複数のリストを一度に渡すと配列の順に実行されます。1 回ずつ分けて渡すよりまとめたほうが、CPU の負担が小さくなります。

この関数は GPU の終了を待たずにすぐ戻ります。戻った直後にリストのアロケーターを `Reset` してはいけません。GPU がまだ読んでいる可能性があるからです。フェンスで終了を確認してからにします。

戻り値はありません。失敗はデバッグ レイヤーのメッセージかあとで `GetDeviceRemovedReason` に出ます。

### Signal {#signal}

```cpp
HRESULT ID3D12CommandQueue::Signal(
    ID3D12Fence* pFence,
    UINT64 Value);
```

このキューに「ここまでの仕事が終わったら、フェンスの数字を `Value` にする」と予約します。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pFence` | `ID3D12Fence*` | 数字を書き込むフェンス |
| `Value` | `UINT64` | 書き込む数字 |

予約した時点ではフェンスの数字は変わりません。キューが `Signal` より前に渡された仕事をすべて終えたとき GPU が数字を書き込みます。CPU は `GetCompletedValue` で数字を見るか `SetEventOnCompletion` で待つことで、終了を知ります。

`Value` は前回より大きい数字を渡します。数字は増えるだけで減らせません。フレームごとに 1 ずつ増やすのが定番です。戻り値は成功なら `S_OK` です。

```cpp
const UINT64 value = ++fence_value;
command_queue->Signal(fence.Get(), value);  // この時点までの GPU の仕事が終わったら value になる
```

### Wait {#wait}

```cpp
HRESULT ID3D12CommandQueue::Wait(
    ID3D12Fence* pFence,
    UINT64 Value);
```

フェンスの数字が `Value` 以上になるまで、**このキューの**以降の仕事を止めます。CPU は止まりません。

別のキューの結果を待つときに使います。たとえば、COPY キューでテクスチャを読み込んで、その完了を DIRECT キューで待ってから描く、という使い方です。CPU が待つ必要はなく GPU どうしで待ち合うので、CPU が空いたままになります。

`pFence` には待つ相手のキューが `Signal` するフェンスを渡します。数字がすでに `Value` 以上なら待たずに進みます。戻り値は成功なら `S_OK` です。

### GetTimestampFrequency {#gettimestampfrequency}

```cpp
HRESULT ID3D12CommandQueue::GetTimestampFrequency(UINT64* pFrequency);
```

タイムスタンプ クエリの値が、1 秒あたり何刻みかを返します。`pFrequency` に結果が書き込まれます。

2 つのタイムスタンプの差をこの値で割ると、秒になります。1,000 を掛けるとミリ秒です。値は GPU ごとに違うので、決め打ちにせず起動時に 1 回取得しておきます。戻り値は成功なら `S_OK` です。使い方の全体は [GPU Queries and Timing](../query-timing.md) にあります。

## 関連ページ

- [Command Queue](../command-queue.md)
- [ID3D12Fence](id3d12fence.md)
- [ID3D12GraphicsCommandList](id3d12graphicscommandlist.md)
- [Microsoft Learn: ID3D12CommandQueue](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12commandqueue)
