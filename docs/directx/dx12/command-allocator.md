---
title: Command Allocator
tags:
  - DirectX
---

# Command Allocator

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>コマンド アロケーター</strong>（`ID3D12CommandAllocator`）は、[コマンド リスト](command-list.md)が記録した命令を、<strong>しまっておくメモリ</strong>です。コマンド リストは記録の窓口で命令の実体は、アロケーターのメモリに書かれます。GPU が命令を実行している間、<strong>そのメモリは触れません</strong>。このためアロケーターの扱いが、D3D12 のミスの定番です。

!!! tip "ポイント"
    - アロケーター ＝ 記録した命令の、保管メモリ。コマンド リストはこれに書き込む。
    - <strong>GPU が使い終わるまで、`Reset` できない</strong>。`Reset` はメモリを再利用のために、巻き戻す。
    - <strong>フレームごとに、1 つ</strong>（フレーム イン フライトの数だけ）用意する。
    - 1 つのアロケーターに同時に、記録できるコマンド リストは、<strong>1 つだけ</strong>。スレッドごとに別のアロケーター。
    - 種類（DIRECT、COMPUTE、COPY）はコマンド リストと、そろえる。

## 作る

```cpp
ComPtr<ID3D12CommandAllocator> command_allocator;
device->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, IID_PPV_ARGS(&command_allocator));
```

引数は種類だけです。種類は使うキュー、コマンド リストとそろえます（DIRECT のアロケーターに、COMPUTE のリストは使えません）。

## Reset：巻き戻して、再利用する

```cpp
// フレームの最初: このアロケーターの、命令を、GPU が、使い終わっているなら、Reset して、メモリを、再利用する。
command_allocator->Reset();
```

`Reset` は <strong>アロケーターのメモリを先頭に、戻します</strong>（メモリを解放はしない）。前に記録した命令は消えます。<strong>その命令を GPU がまだ実行中なら、実行中のメモリが上書きされて</strong>、クラッシュや画面の乱れが起きます。

| 状況 | `Reset` できるか |
| --- | --- |
| GPU がこのアロケーターの命令を、実行中 | <strong>できない</strong>（未定義の動作） |
| GPU が実行を終えた（フェンスで、確認済み） | できる |
| まだ `ExecuteCommandLists` していない | できる |

`ExecuteCommandLists` で投げた <strong>直後</strong>は GPU がまだ、実行している可能性が高いので、すぐには `Reset` できません（[Fence](fence.md)）。

## フレームごとに 1 つ

CPU が次のフレームの命令を、記録している間に GPU は前のフレームを、実行しています。アロケーターを 1 つしか持たないと、CPU は GPU が終わるまで、待つ必要があります。<strong>フレームごとに別のアロケーター</strong>を持つと、CPU は先に進めます。

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

フレーム イン フライトの詳細は、[Frame Resources](frame-resources.md) です。

## 1 つのアロケーターに同時に複数の、リストは記録できない

```cpp
// 間違い: 同じアロケーターに、2 つのリストを、同時に記録する。
list_a->Reset(allocator.Get(), nullptr);
list_b->Reset(allocator.Get(), nullptr);                    // エラー: list_a の記録中
```

<strong>1 つのアロケーターは 1 度に、1 つのコマンド リストだけ</strong>が記録に、使えます。複数のスレッドで記録するなら、<strong>スレッドごとに別のアロケーター</strong>を、持ちます。

| 構成 | アロケーターの数 |
| --- | --- |
| 1 スレッド、フレーム イン フライト 2 | 2 |
| 4 スレッド（各スレッドが記録）、フレーム イン フライト 3 | 4 × 3 = 12 |

## メモリの増え方

アロケーターは記録した命令に応じて、メモリを <strong>増やします</strong>。`Reset` しても <strong>縮みません</strong>（再利用のため）。1 フレームで大量の命令を記録した、アロケーターはその後も大きいままです。

| 注意 | 内容 |
| --- | --- |
| 巨大な 1 フレーム | 一度、大きくなるとそのまま。通常のフレームの命令の量で安定する |
| 作り直し | 極端に大きくなったら、アロケーターを作り直して解放する |

## よくあるミス

??? failure "ときどき画面が乱れる、またはクラッシュする（再現が、不安定）"
    GPU がまだ実行中の、アロケーターを `Reset` している。フェンスで完了を確認してから、`Reset` する。D3D12 の典型的な競合状態。

??? failure "`Reset` が、`E_FAIL` を返す"
    そのアロケーターから、記録したリストがまだ `Close()` されていないまたは、GPU が実行中（デバッグ レイヤーが、メッセージを出す）。

??? failure "複数のスレッドが同じ、アロケーターに記録してクラッシュする"
    スレッドごとに別のアロケーターを使う。

??? failure "フレームごとに、アロケーターを作って捨てて重い"
    作成は重いので起動時に、フレーム イン フライトの数だけ作り `Reset` で、使い回す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アロケーター ＝ 記録した命令の、保管メモリ
    - [x] GPU が、使い終わるまで `Reset` できない（フェンスで確認）
    - [x] フレームごとに、1 つ（フレーム イン フライトの数）
    - [x] 1 つのアロケーターに同時に、記録できるのは 1 つのリスト。スレッドごとに別
    - [x] `Reset` しても、メモリは縮まない

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Command List](command-list.md)
- [Fence](fence.md)
- [Frame Resources](frame-resources.md)
- [Microsoft Learn: ID3D12CommandAllocator](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12commandallocator)
