---
title: ID3D12CommandAllocator
tags:
  - DirectX
api:
  - ID3D12CommandAllocator
---

# ID3D12CommandAllocator

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

コマンド リストは命令を書き込む「窓口」ですが、命令そのものを置くメモリは持っていません。その置き場がコマンド アロケーター（`ID3D12CommandAllocator`）です。リストを記録するたびにアロケーターのメモリに命令が書き足されていきます。

メソッドは `Reset` だけです。ただ、「いつ `Reset` してよいか」を間違えると、GPU が読んでいる最中の命令を壊してしまうので、落とし穴が多い所です。

!!! tip "ポイント"
    - `Reset` してよいのは、GPU がそのアロケーターの命令をすべて読み終えたあとだけ。
    - 1 つのアロケーターに同時に記録できるリストは 1 つだけ。
    - フレームごとにアロケーターを 1 つずつ用意する。
    - `Reset` してもメモリは解放されない。使った分が増えたまま再利用される。

!!! info "このページを読む前に"
    アロケーターを作る `CreateCommandAllocator` は [ID3D12Device](id3d12device.md#createcommandallocator)、リストとの関係は [Command Allocator](../command-allocator.md) と [ID3D12GraphicsCommandList](id3d12graphicscommandlist.md) で説明しています。待つための仕組みは [ID3D12Fence](id3d12fence.md) です。

## Reset {#reset}

```cpp
HRESULT ID3D12CommandAllocator::Reset();
```

アロケーターが持っているメモリを先頭から再利用できる状態に戻します。引数はありません。

大事なのは呼んでよいタイミングです。コマンド リストを `ExecuteCommandLists` で GPU に渡したあと GPU がそのメモリを読み終わるまでは、`Reset` してはいけません。読んでいる最中に消すと GPU が壊れた命令を実行して、デバイスが削除されます。フェンスで「このフレームの GPU 処理が終わった」と確認してから呼びます。

もう 1 つの条件はこのアロケーターで記録中のコマンド リストがないことです。コマンド リストを `Close` する前に `Reset` すると、失敗します。呼ぶ順番はアロケーターの `Reset`、そのあとにコマンド リストの `Reset`、です。

```cpp
// フレームの最初。fence が frame_value まで進んでいる（GPU が終わっている）ことを確認してから。
allocator->Reset();
command_list->Reset(allocator.Get(), nullptr);
```

`Reset` はメモリを解放しません。1 フレームで使った分のメモリはずっとアロケーターに残ります。一度だけ極端に重いフレームがあると、そのときの大きさが以降ずっと残ります。メモリを減らしたいときはアロケーターを作り直します。

戻り値は成功なら `S_OK` です。GPU がまだ使っているときまたは記録中のリストがあるときは、失敗します（`E_FAIL`）。

## 関連ページ

- [Command Allocator](../command-allocator.md)
- [ID3D12GraphicsCommandList](id3d12graphicscommandlist.md)
- [Frame Resources](../frame-resources.md)
- [Microsoft Learn: ID3D12CommandAllocator](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12commandallocator)
