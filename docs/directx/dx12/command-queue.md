---
title: Command Queue
tags:
  - DirectX
---

# Command Queue

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>コマンド キュー</strong>（`ID3D12CommandQueue`）は、<strong>GPU に、仕事を、渡す、窓口</strong>です。CPU が、[コマンド リスト](command-list.md)に、記録した、命令を、キューに、投げる（`ExecuteCommandLists`）と、GPU が、キューの、順に、実行します。キューは、GPU の、実行エンジン（描画、計算、コピー）の、入口で、<strong>種類ごとに、別のキュー</strong>を、持てます。

!!! tip "ポイント"
    - コマンド キュー ＝ GPU への、仕事の、投入口。`ExecuteCommandLists` で、リストを、投げる。
    - 種類は 3 つ: <strong>DIRECT</strong>（描画・計算・コピー、全部）、<strong>COMPUTE</strong>（計算・コピー）、<strong>COPY</strong>（コピーだけ）。
    - 投げた、リストは、<strong>CPU を、待たせず</strong>、すぐ、戻る。GPU は、あとで、実行する。
    - キューは、<strong>順に</strong>、実行する。別々の、キューは、<strong>並列</strong>に、動ける（非同期コンピュート）。
    - GPU の完了は、[フェンス](fence.md)で、確認する。
    - スワップ チェーンは、DIRECT キューに、結びつく。

## 作る

```cpp
D3D12_COMMAND_QUEUE_DESC desc = {};
desc.Type = D3D12_COMMAND_LIST_TYPE_DIRECT;                // 描画も、計算も、コピーも、できる
desc.Priority = D3D12_COMMAND_QUEUE_PRIORITY_NORMAL;
desc.Flags = D3D12_COMMAND_QUEUE_FLAG_NONE;
desc.NodeMask = 0;                                         // GPU が 1 つなら 0

ComPtr<ID3D12CommandQueue> command_queue;
device->CreateCommandQueue(&desc, IID_PPV_ARGS(&command_queue));
```

| メンバー | 内容 |
| --- | --- |
| `Type` | キューの種類（下の表） |
| `Priority` | `NORMAL`、`HIGH`、`GLOBAL_REALTIME`（特権が要る） |
| `Flags` | `DISABLE_GPU_TIMEOUT`（GPU の、タイムアウト検出を、切る。通常は、使わない） |
| `NodeMask` | マルチ GPU のとき、どの GPU か。1 つなら 0 |

## キューの、種類

| `D3D12_COMMAND_LIST_TYPE_*` | できること | 使いどころ |
| --- | --- | --- |
| `DIRECT` | 描画、計算、コピー（全部） | メインの描画。必須（スワップ チェーンも、これ） |
| `COMPUTE` | 計算、コピー | <strong>非同期コンピュート</strong>（描画と、並列に、計算） |
| `COPY` | コピーのみ | 非同期の、アップロード（テクスチャの、ストリーミング）。専用の、DMA エンジンを、使える |
| `BUNDLE` | （キューには、投げない） | 小さな、命令の、再利用（バンドル） |

多くの GPU は、描画エンジンと、計算エンジン、コピー エンジンを、<strong>別々に</strong>、持っています。別のキューで、投げると、並列に、実行されます。

```text
DIRECT キュー:  [シャドウ] [G バッファ] [ライティング] [ポスト プロセス]
COMPUTE キュー:     [パーティクル更新] [カリング]          ← DIRECT と、並列に実行（非同期コンピュート）
COPY キュー:     [テクスチャの、アップロード]               ← 描画を、止めずに、裏で、読み込む
```

キュー同士の、順序の、保証（「COMPUTE が、終わるまで、DIRECT は、待つ」）は、フェンスで、行います（[Fence](fence.md)）。

## コマンド リストを、投げる

```cpp
ID3D12CommandList* lists[] = {command_list.Get()};
command_queue->ExecuteCommandLists(ARRAYSIZE(lists), lists);
```

`ExecuteCommandLists` は、リストを、キューに、<strong>積んで、すぐ戻ります</strong>。GPU が、実行を、終えるのを、待ちません。投げる前に、リストは、`Close()` されている必要が、あります（[Command List](command-list.md)）。

| 注意 | 内容 |
| --- | --- |
| 投げた、リストの、再利用 | 投げた直後に、`Reset` して、別の命令を、記録できる（アロケーターは、GPU が、使い終わるまで、`Reset` できない） |
| 複数のリスト | 配列で、まとめて、投げられる。配列の、順に、実行される |
| 呼び出しの、コスト | `ExecuteCommandLists` は、<strong>重い</strong>ので、フレームに、数回に、まとめる（リストごとに、1 回ずつ、投げない） |

## Signal と Wait

キューに、<strong>フェンスへの、書き込み</strong>（`Signal`）や、<strong>フェンスの、待ち</strong>（`Wait`）を、積めます。これが、GPU の、完了の、通知と、キュー同士の、順序づけの、基本です。

```cpp
// このキューの、ここまでの仕事が、終わったら、フェンスに value を書く（GPU が、実行時に、行う）。
command_queue->Signal(fence.Get(), value);

// 別のキューを、「フェンスが value になるまで」止める（GPU 側の、待ち。CPU は、止まらない）。
other_queue->Wait(fence.Get(), value);
```

`Signal` と `Wait` は、<strong>GPU が、実行する</strong>命令で、CPU は、待ちません。CPU が、待つには、`fence->SetEventOnCompletion` と、`WaitForSingleObject` を、使います（[Fence](fence.md)）。

## 複数のキューの、使い分け

| 構成 | 内容 |
| --- | --- |
| DIRECT だけ | 最も、単純。最初は、これ |
| DIRECT + COPY | テクスチャ・メッシュの、アップロードを、裏で、行う（ロード画面を、減らす） |
| DIRECT + COMPUTE | パーティクルの更新、カリング、ポスト プロセスの、一部を、描画と、並列に |

非同期コンピュートは、<strong>描画が、GPU の、一部しか、使っていない</strong>（メモリ帯域や、固定機能が、ボトルネック）ときに、効果が、あります。計算が、重い処理を、並列に、すると、GPU の、空き時間を、埋められます（[Async Compute](../../rendering/async-compute.md)）。

## タイムスタンプ

```cpp
UINT64 frequency;
command_queue->GetTimestampFrequency(&frequency);           // 1 秒あたりの、チック数（GPU のクロック）
```

GPU の、処理時間の、計測に、使います（[GPU Queries and Timing](query-timing.md)）。

## よくあるミス

??? failure "`ExecuteCommandLists` で、クラッシュする"
    リストが、`Close()` されていない。または、記録中に、エラーが、あった（`Close` の戻り値が、`FAILED`）。デバッグ レイヤーの、メッセージを、見る。

??? failure "投げた後、すぐ、アロケーターを、`Reset` して、クラッシュする"
    GPU が、まだ、そのアロケーターの、命令を、実行している。フェンスで、完了を、確認してから、`Reset` する（[Command Allocator](command-allocator.md)）。

??? failure "COMPUTE キューで、描画命令を、使って、エラーになる"
    COMPUTE キューは、描画（`DrawInstanced` など）を、実行できない。DIRECT キューに、投げる。

??? failure "リストごとに、`ExecuteCommandLists` を、呼んで、CPU が、重い"
    複数のリストを、配列に、まとめて、1 回で、投げる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コマンド キュー ＝ GPU への、仕事の投入口。`ExecuteCommandLists`
    - [x] 種類は、DIRECT（全部）・COMPUTE・COPY。最初は、DIRECT だけ
    - [x] 投げたら、すぐ戻る。GPU は、あとで、実行する
    - [x] 完了は、フェンスで、確認する（`Signal` / `Wait`）
    - [x] 別のキューは、並列。順序づけは、フェンスで

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Command List](command-list.md)
- [Fence](fence.md)
- [Async Compute](../../rendering/async-compute.md)
- [Microsoft Learn: ID3D12CommandQueue](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12commandqueue)
