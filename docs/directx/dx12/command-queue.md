---
title: Command Queue
tags:
  - DirectX
---

# Command Queue

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>コマンド キュー</strong>（`ID3D12CommandQueue`）は <strong>GPU に仕事を渡す窓口</strong>です。CPU が[コマンド リスト](command-list.md)に記録した命令をキューに投げる（`ExecuteCommandLists`）と GPU がキューの順に実行します。キューは GPU の実行エンジン（描画、計算、コピー）の入口で <strong>種類ごとに別のキュー</strong>を持てます。

!!! tip "ポイント"
    - コマンド キュー ＝ GPU への仕事の投入口。`ExecuteCommandLists` でリストを投げる。
    - 種類は 3 つ: <strong>DIRECT</strong>（描画・計算・コピー、全部）、<strong>COMPUTE</strong>（計算・コピー）、<strong>COPY</strong>（コピーだけ）。
    - 投げたリストは <strong>CPU を待たせず</strong>、すぐ戻る。GPU はあとで実行する。
    - キューは <strong>順に</strong>、実行する。別々のキューは <strong>並列</strong>に動ける（非同期コンピュート）。
    - GPU の完了は[フェンス](fence.md)で確認する。
    - スワップ チェーンは DIRECT キューに結びつく。

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
| `Flags` | `DISABLE_GPU_TIMEOUT`（GPU のタイムアウト検出を切る。通常は、使わない） |
| `NodeMask` | マルチ GPU のときどの GPU か。1 つなら 0 |

## キューの種類

| `D3D12_COMMAND_LIST_TYPE_*` | できること | 使いどころ |
| --- | --- | --- |
| `DIRECT` | 描画、計算、コピー（全部） | メインの描画。必須（スワップ チェーンもこれ） |
| `COMPUTE` | 計算、コピー | <strong>非同期コンピュート</strong>（描画と並列に計算） |
| `COPY` | コピーのみ | 非同期のアップロード（テクスチャのストリーミング）。専用の DMA エンジンを使える |
| `BUNDLE` | （キューには投げない） | 小さな命令の再利用（バンドル） |

多くの GPU は描画エンジンと計算エンジン、コピー エンジンを <strong>別々に</strong>、持っています。別のキューで投げると並列に実行されます。

```text
DIRECT キュー:  [シャドウ] [G バッファ] [ライティング] [ポスト プロセス]
COMPUTE キュー:     [パーティクル更新] [カリング]          ← DIRECT と、並列に実行（非同期コンピュート）
COPY キュー:     [テクスチャの、アップロード]               ← 描画を、止めずに、裏で、読み込む
```

キュー同士の順序の保証（「COMPUTE が、終わるまで DIRECT は待つ」）は、フェンスで行います（[Fence](fence.md)）。

## コマンド リストを投げる

```cpp
ID3D12CommandList* lists[] = {command_list.Get()};
command_queue->ExecuteCommandLists(ARRAYSIZE(lists), lists);
```

`ExecuteCommandLists` はリストをキューに <strong>積んで、すぐ戻ります</strong>。GPU が実行を終えるのを待ちません。投げる前にリストは `Close()` されている必要が、あります（[Command List](command-list.md)）。

| 注意 | 内容 |
| --- | --- |
| 投げたリストの再利用 | 投げた直後に `Reset` して別の命令を記録できる（アロケーターは、GPU が使い終わるまで `Reset` できない） |
| 複数のリスト | 配列で、まとめて投げられる。配列の順に実行される |
| 呼び出しのコスト | `ExecuteCommandLists` は <strong>重い</strong>のでフレームに数回にまとめる（リストごとに 1 回ずつ、投げない） |

## Signal と Wait

キューに <strong>フェンスへの書き込み</strong>（`Signal`）や <strong>フェンスの待ち</strong>（`Wait`）を積めます。これが GPU の完了の通知とキュー同士の順序づけの基本です。

```cpp
// このキューの、ここまでの仕事が、終わったら、フェンスに value を書く（GPU が、実行時に、行う）。
command_queue->Signal(fence.Get(), value);

// 別のキューを、「フェンスが value になるまで」止める（GPU 側の、待ち。CPU は、止まらない）。
other_queue->Wait(fence.Get(), value);
```

`Signal` と `Wait` は <strong>GPU が実行する</strong>命令で、CPU は待ちません。CPU が待つには `fence->SetEventOnCompletion` と `WaitForSingleObject` を使います（[Fence](fence.md)）。

## 複数のキューの使い分け

| 構成 | 内容 |
| --- | --- |
| DIRECT だけ | 最も単純。最初はこれ |
| DIRECT + COPY | テクスチャ・メッシュのアップロードを裏で行う（ロード画面を、減らす） |
| DIRECT + COMPUTE | パーティクルの更新、カリング、ポスト プロセスの一部を描画と並列に |

非同期コンピュートは <strong>描画が、GPU の一部しか使っていない</strong>（メモリ帯域や固定機能がボトルネック）ときに効果が、あります。計算が重い処理を並列にすると、GPU の空き時間を埋められます（[Async Compute](../../rendering/async-compute.md)）。

## タイムスタンプ

```cpp
UINT64 frequency;
command_queue->GetTimestampFrequency(&frequency);           // 1 秒あたりの、チック数（GPU のクロック）
```

GPU の処理時間の計測に使います（[GPU Queries and Timing](query-timing.md)）。

## よくあるミス

??? failure "`ExecuteCommandLists` で、クラッシュする"
    リストが `Close()` されていない。または、記録中にエラーがあった（`Close` の戻り値が `FAILED`）。デバッグ レイヤーのメッセージを見る。

??? failure "投げた後、すぐアロケーターを `Reset` してクラッシュする"
    GPU がまだそのアロケーターの命令を実行している。フェンスで完了を確認してから、`Reset` する（[Command Allocator](command-allocator.md)）。

??? failure "COMPUTE キューで、描画命令を使ってエラーになる"
    COMPUTE キューは描画（`DrawInstanced` など）を実行できない。DIRECT キューに投げる。

??? failure "リストごとに `ExecuteCommandLists` を呼んで、CPU が重い"
    複数のリストを配列にまとめて 1 回で投げる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コマンド キュー ＝ GPU への仕事の投入口。`ExecuteCommandLists`
    - [x] 種類は DIRECT（全部）・COMPUTE・COPY。最初は DIRECT だけ
    - [x] 投げたら、すぐ戻る。GPU はあとで実行する
    - [x] 完了はフェンスで、確認する（`Signal` / `Wait`）
    - [x] 別のキューは並列。順序づけはフェンスで

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Command List](command-list.md)
- [Fence](fence.md)
- [Async Compute](../../rendering/async-compute.md)
- [Microsoft Learn: ID3D12CommandQueue](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12commandqueue)
