---
title: Command Allocator
tags:
  - DirectX
---

# Command Allocator

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>コマンド アロケーター</strong>（`ID3D12CommandAllocator`）は、[コマンド リスト](command-list.md)が、記録した、命令を、<strong>しまっておく、メモリ</strong>です。コマンド リストは、記録の、窓口で、命令の、実体は、アロケーターの、メモリに、書かれます。GPU が、命令を、実行している間、<strong>そのメモリは、触れません</strong>。このため、アロケーターの、扱いが、D3D12 の、ミスの、定番です。

!!! tip "ポイント"
    - アロケーター ＝ 記録した、命令の、保管メモリ。コマンド リストは、これに、書き込む。
    - <strong>GPU が、使い終わるまで、`Reset` できない</strong>。`Reset` は、メモリを、再利用のために、巻き戻す。
    - <strong>フレームごとに、1 つ</strong>（フレーム イン フライトの数だけ）用意する。
    - 1 つのアロケーターに、同時に、記録できる、コマンド リストは、<strong>1 つだけ</strong>。スレッドごとに、別のアロケーター。
    - 種類（DIRECT、COMPUTE、COPY）は、コマンド リストと、そろえる。

## 作る

```cpp
ComPtr<ID3D12CommandAllocator> command_allocator;
device->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, IID_PPV_ARGS(&command_allocator));
```

引数は、種類だけです。種類は、使う、キュー、コマンド リストと、そろえます（DIRECT のアロケーターに、COMPUTE のリストは、使えません）。

## Reset：巻き戻して、再利用する

```cpp
// フレームの最初: このアロケーターの、命令を、GPU が、使い終わっているなら、Reset して、メモリを、再利用する。
command_allocator->Reset();
```

`Reset` は、<strong>アロケーターの、メモリを、先頭に、戻します</strong>（メモリを、解放は、しない）。前に、記録した、命令は、消えます。<strong>その命令を、GPU が、まだ、実行中なら、実行中の、メモリが、上書きされて</strong>、クラッシュや、画面の、乱れが、起きます。

| 状況 | `Reset` できるか |
| --- | --- |
| GPU が、このアロケーターの、命令を、実行中 | <strong>できない</strong>（未定義の動作） |
| GPU が、実行を、終えた（フェンスで、確認済み） | できる |
| まだ、`ExecuteCommandLists` していない | できる |

`ExecuteCommandLists` で、投げた、<strong>直後</strong>は、GPU が、まだ、実行している可能性が、高いので、すぐには、`Reset` できません（[Fence](fence.md)）。

## フレームごとに、1 つ

CPU が、次のフレームの、命令を、記録している間に、GPU は、前のフレームを、実行しています。アロケーターを、1 つしか、持たないと、CPU は、GPU が、終わるまで、待つ必要が、あります。<strong>フレームごとに、別のアロケーター</strong>を、持つと、CPU は、先に、進めます。

```cpp
constexpr UINT kFrameCount = 2;                              // フレーム イン フライトの数（2 か 3）
ComPtr<ID3D12CommandAllocator> allocators[kFrameCount];
for (auto& allocator : allocators) {
  device->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, IID_PPV_ARGS(&allocator));
}

// フレームの最初:
UINT frame_index = frame_number % kFrameCount;
WaitForFence(frame_fence_values[frame_index]);               // このアロケーターを、前に使ったフレームの、GPU 完了を、待つ
allocators[frame_index]->Reset();                            // もう安全に、Reset できる
```

フレーム イン フライトの、詳細は、[Frame Resources](frame-resources.md) です。

## 1 つのアロケーターに、同時に、複数の、リストは、記録できない

```cpp
// 間違い: 同じアロケーターに、2 つのリストを、同時に記録する。
list_a->Reset(allocator.Get(), nullptr);
list_b->Reset(allocator.Get(), nullptr);                    // エラー: list_a の記録中
```

<strong>1 つのアロケーターは、1 度に、1 つの、コマンド リストだけ</strong>が、記録に、使えます。複数の、スレッドで、記録するなら、<strong>スレッドごとに、別のアロケーター</strong>を、持ちます。

| 構成 | アロケーターの、数 |
| --- | --- |
| 1 スレッド、フレーム イン フライト 2 | 2 |
| 4 スレッド（各スレッドが、記録）、フレーム イン フライト 3 | 4 × 3 = 12 |

## メモリの、増え方

アロケーターは、記録した、命令に、応じて、メモリを、<strong>増やします</strong>。`Reset` しても、<strong>縮みません</strong>（再利用のため）。1 フレームで、大量の、命令を、記録した、アロケーターは、その後も、大きいままです。

| 注意 | 内容 |
| --- | --- |
| 巨大な、1 フレーム | 一度、大きくなると、そのまま。通常のフレームの、命令の量で、安定する |
| 作り直し | 極端に、大きくなったら、アロケーターを、作り直して、解放する |

## よくあるミス

??? failure "ときどき、画面が、乱れる、またはクラッシュする（再現が、不安定）"
    GPU が、まだ、実行中の、アロケーターを、`Reset` している。フェンスで、完了を、確認してから、`Reset` する。D3D12 の、典型的な、競合状態。

??? failure "`Reset` が、`E_FAIL` を返す"
    そのアロケーターから、記録した、リストが、まだ、`Close()` されていない、または、GPU が、実行中（デバッグ レイヤーが、メッセージを、出す）。

??? failure "複数のスレッドが、同じ、アロケーターに、記録して、クラッシュする"
    スレッドごとに、別のアロケーターを、使う。

??? failure "フレームごとに、アロケーターを、作って、捨てて、重い"
    作成は、重いので、起動時に、フレーム イン フライトの、数だけ、作り、`Reset` で、使い回す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アロケーター ＝ 記録した、命令の、保管メモリ
    - [x] GPU が、使い終わるまで、`Reset` できない（フェンスで、確認）
    - [x] フレームごとに、1 つ（フレーム イン フライトの数）
    - [x] 1 つのアロケーターに、同時に、記録できるのは、1 つのリスト。スレッドごとに、別
    - [x] `Reset` しても、メモリは、縮まない

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Command List](command-list.md)
- [Fence](fence.md)
- [Frame Resources](frame-resources.md)
- [Microsoft Learn: ID3D12CommandAllocator](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12commandallocator)
