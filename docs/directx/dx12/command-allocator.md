---
title: Command Allocator
tags:
  - DirectX
---

# Command Allocator

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

コマンド リストは命令を記録する「窓口」です。ただ、記録した命令そのものを置くメモリはリストの中にはありません。その置き場が<strong>コマンド アロケーター</strong>（`ID3D12CommandAllocator`）です。`DrawInstanced` や `ResourceBarrier` を呼ぶたびに命令がアロケーターのメモリへ書き足されていきます。

GPU が命令を実行している間はそのメモリに触れません。読んでいる最中に書き換えると、壊れた命令を GPU が実行してしまいます。アロケーターの扱いは D3D12 で一番ミスが出やすい所の 1 つです。

!!! tip "ポイント"
    - アロケーターは記録した命令を置くメモリ。コマンド リストはそこへ書き込む。
    - GPU が使い終わるまで、`Reset` してはいけない。
    - フレームごとに 1 つ用意する（フレームを同時に進める数だけ）。
    - 1 つのアロケーターで同時に記録できるリストは、1 つだけ。スレッドごとに別のアロケーターを使う。
    - 種類（DIRECT、COMPUTE、COPY）はコマンド リストと同じにする。

!!! info "このページを読む前に"
    命令を記録する側は [Command List](command-list.md)、GPU の完了を確認する仕組みは [Fence](fence.md) で説明しています。先に読んでおくと `Reset` のタイミングの話が分かりやすくなります。メソッドの詳細は [ID3D12CommandAllocator](api/id3d12commandallocator.md) にあります。

## 作る

アロケーターは `CreateCommandAllocator` に種類だけを渡して作ります。

```cpp
ComPtr<ID3D12CommandAllocator> command_allocator;
device->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, IID_PPV_ARGS(&command_allocator));
```

種類は使うキューとコマンド リストの種類と同じにします。DIRECT のアロケーターを使って、COMPUTE のリストを作ることはできません。

## Reset でメモリを巻き戻す

記録のたびにメモリを新しく確保すると遅いので、アロケーターは使ったメモリを先頭へ巻き戻して再利用します。その操作が `Reset` です。

```cpp
// フレームの最初。このアロケーターの命令を GPU が使い終わっているなら、巻き戻して再利用する。
command_allocator->Reset();
```

`Reset` はメモリを解放せず書き込み位置を先頭へ戻します。前に記録した命令は消えます。もし GPU がその命令を実行している最中なら実行中のメモリが上書きされて、クラッシュや画面の乱れが起きます。

`Reset` してよいのは次のどちらかのときです。GPU がそのアロケーターの命令を実行し終えて、フェンスで確認できたとき。あるいはまだ一度も `ExecuteCommandLists` で渡していないときです。渡した直後は GPU が実行している可能性が高いので、すぐには `Reset` できません。

## フレームごとに 1 つ持つ

CPU が次のフレームの命令を記録している間も GPU は前のフレームを実行しています。アロケーターが 1 つしかないと CPU は GPU が終わるまで待たなければなりません。フレームごとに別のアロケーターを持てば、CPU は待たずに先へ進めます。

<svg class="fig flow" viewBox="0 0 720 236" role="img" aria-label="アロケーターを 2 つ交互に使う"><defs><marker id="al" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">フレームごとに別のアロケーター</text><text x="12" y="76" text-anchor="start" style="font-size:12px;font-weight:700">CPU</text><text x="12" y="136" text-anchor="start" style="font-size:12px;font-weight:700">GPU</text><rect x="60" y="56" width="200" height="36" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="160.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">フレーム 0 を記録（A）</text><rect x="270" y="56" width="200" height="36" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="370.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">フレーム 1 を記録（B）</text><rect x="480" y="56" width="220" height="36" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="590.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">フレーム 2 を記録（A を Reset）</text><rect x="270" y="116" width="200" height="36" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="370.0" y="134.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">フレーム 0 を実行（A を読む）</text><rect x="480" y="116" width="220" height="36" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="590.0" y="134.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">フレーム 1 を実行（B を読む）</text><line x1="370" y1="152" x2="560" y2="92" stroke="currentColor" stroke-width="2" marker-end="url(#al)"/><text x="360" y="196" text-anchor="middle" style="font-size:12px;font-weight:400">A の実行が終わった（フェンスで確認）あとだけ、A を Reset できる。</text><text x="360" y="216" text-anchor="middle" style="font-size:12px;font-weight:400">アロケーターが 1 つだと、CPU は GPU が終わるまで待つことになる。</text></svg>

```cpp
constexpr UINT kFrameCount = 2;  // 同時に進めるフレームの数（2 か 3）
ComPtr<ID3D12CommandAllocator> allocators[kFrameCount];
for (auto& allocator : allocators) {
  device->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, IID_PPV_ARGS(&allocator));
}

// フレームの最初。
UINT frame_index = frame_number % kFrameCount;
WaitForFence(frame_fence_values[frame_index]);  // このアロケーターを前に使ったフレームの、GPU の完了を待つ
allocators[frame_index]->Reset();               // これで安全に Reset できる
```

何フレームを同時に進めるかの考え方は、[Frame Resources](frame-resources.md) で説明しています。

## 同時に記録できるのは 1 つ

1 つのアロケーターには同時に記録できるコマンド リストが 1 つだけです。2 つのリストを同じアロケーターで続けて `Reset` すると、2 つ目が失敗します。

```cpp
// 間違い。同じアロケーターに、2 つのリストを同時に記録している。
list_a->Reset(allocator.Get(), nullptr);
list_b->Reset(allocator.Get(), nullptr);  // エラー。list_a が記録中
```

複数のスレッドで記録するならスレッドごとに別のアロケーターを持ちます。たとえば、1 スレッドでフレームを 2 つ同時に進めるならアロケーターは 2 つです。4 つのスレッドが記録しフレームを 3 つ同時に進めるなら 4 × 3 で 12 個になります。

## メモリは増えて縮まない

アロケーターは記録した命令の量に合わせて、メモリを増やします。`Reset` しても縮みません。再利用するための仕組みだからです。そのため、あるフレームで大量の命令を記録すると、その後もずっとそのときの大きさが残ります。

普段のフレームの量で安定するなら気にしなくて構いません。極端に大きくなってしまったときだけアロケーターを作り直して、メモリを解放します。

## よくあるミス

??? failure "ときどき画面が乱れる、またはクラッシュする（再現が安定しない）"
    GPU がまだ実行中のアロケーターを `Reset` しています。フェンスで完了を確認してから `Reset` します。D3D12 の典型的な競合状態です。

??? failure "`Reset` が `E_FAIL` を返す"
    そのアロケーターで記録したリストがまだ `Close` されていないか GPU が実行中です。デバッグ レイヤーがメッセージを出します。

??? failure "複数のスレッドが同じアロケーターに記録してクラッシュする"
    スレッドごとに別のアロケーターを使います。

??? failure "フレームごとにアロケーターを作っては捨てて重い"
    作成は重い処理です。起動時に同時に進めるフレームの数だけ作り `Reset` で使い回します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アロケーターは記録した命令を置くメモリ
    - [x] GPU が使い終わるまで `Reset` できない（フェンスで確認する）
    - [x] フレームごとに 1 つ。同時に記録できるリストは 1 つ
    - [x] `Reset` しても、メモリは縮まない

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3D12CommandAllocator](api/id3d12commandallocator.md)
- [Command List](command-list.md)
- [Fence](fence.md)
- [Frame Resources](frame-resources.md)
- [Microsoft Learn: ID3D12CommandAllocator](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12commandallocator)
