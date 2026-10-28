---
title: Command Queue
tags:
  - DirectX
---

# Command Queue

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

コマンド リストに命令を記録しても、GPU は何もしません。記録したものを GPU に渡して、実行を頼む場所が必要です。それが<strong>コマンド キュー</strong>（`ID3D12CommandQueue`）です。キューに渡したリストは渡した順に GPU が実行します。

GPU の中には描画をするエンジン、計算をするエンジン、メモリをコピーするエンジンが別々に載っていることが多くあります。D3D12 はそれぞれの入口として、種類ごとに別のキューを作れるようにしています。種類の違うキューに仕事を渡せば、描画と計算とコピーを同時に進められます。

!!! tip "ポイント"
    - キューは GPU に仕事を渡す入口。`ExecuteCommandLists` でリストを渡す。
    - 種類は 3 つ。DIRECT は描画も計算もコピーもでき COMPUTE は計算とコピー、COPY はコピーだけ。
    - 渡したリストは CPU を待たせずにすぐ戻る。GPU はあとで実行する。
    - 別々のキューは並列に動く。順番をそろえたいときはフェンスを使う。
    - スワップ チェーンは DIRECT のキューに結びつく。

!!! info "このページを読む前に"
    キューに渡すのは記録が終わったコマンド リストです。先に [Command List](command-list.md) を読むと流れが分かります。GPU の完了を知る [Fence](fence.md) もこのページで何度か出てきます。メソッドを 1 つずつ引くときは[ID3D12CommandQueue](api/id3d12commandqueue.md) を見てください。

## キューを作る

キューは `CreateCommandQueue` に `D3D12_COMMAND_QUEUE_DESC` を渡して作ります。最初は DIRECT のキューを 1 つだけ作れば足ります。

```cpp
D3D12_COMMAND_QUEUE_DESC desc = {};
desc.Type = D3D12_COMMAND_LIST_TYPE_DIRECT;   // 描画も計算もコピーもできる
desc.Priority = D3D12_COMMAND_QUEUE_PRIORITY_NORMAL;
desc.Flags = D3D12_COMMAND_QUEUE_FLAG_NONE;
desc.NodeMask = 0;                            // GPU が 1 つなら 0

ComPtr<ID3D12CommandQueue> command_queue;
device->CreateCommandQueue(&desc, IID_PPV_ARGS(&command_queue));
```

`D3D12_COMMAND_QUEUE_DESC` の 4 つのメンバーはそれぞれ次の意味です。

`Type` はこのキューにどの仕事を渡せるかを決めます。次の節で詳しく説明します。

`Priority` は複数のキューが同時に動くときの優先度です。`NORMAL` と `HIGH` はどのアプリでも使えます。`GLOBAL_REALTIME` は OS の特権が必要でふつうのゲームでは使いません。

`Flags` に `DISABLE_GPU_TIMEOUT` を付けると GPU の処理が長引いても、OS がドライバーをリセットしなくなります。ふつうのゲームでは使いません。

`NodeMask` は複数の GPU が連結されているときにどの GPU のキューかを選びます。GPU が 1 つなら `0` です。

## キューの種類

キューの種類は `D3D12_COMMAND_LIST_TYPE` で決めます。コマンド リストの種類と同じ値で、種類が違うリストは渡せません。

DIRECT は描画、計算、コピーのすべてができるキューです。メインの描画は必ずこのキューで行いスワップ チェーンもこのキューに結びつきます。

COMPUTE は計算とコピーだけができるキューです。描画命令は実行できません。描画と並行してパーティクルの更新やカリングのような計算を進める「非同期コンピュート」に使います。

COPY はコピーだけができるキューです。GPU が持つコピー専用のエンジン（DMA）を使えるので、描画を止めずにテクスチャやメッシュを裏で読み込めます。

BUNDLE はキューには渡せません。小さな命令の列を再利用するためのリストです。

<svg class="fig flow" viewBox="0 0 720 252" role="img" aria-label="DIRECT、COMPUTE、COPY の 3 つのキューが並列に動く"><defs><marker id="qa" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">キューごとに、別の仕事を並列に</text><text x="12" y="80" text-anchor="start" style="font-size:12px;font-weight:700">DIRECT</text><text x="12" y="136" text-anchor="start" style="font-size:12px;font-weight:700">COMPUTE</text><text x="12" y="192" text-anchor="start" style="font-size:12px;font-weight:700">COPY</text><rect x="100" y="56" width="90" height="36" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="145.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">シャドウ</text><rect x="196" y="56" width="90" height="36" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="241.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">G バッファ</text><rect x="292" y="56" width="100" height="36" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="342.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">ライティング</text><rect x="398" y="56" width="120" height="36" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="458.0" y="74.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">ポスト プロセス</text><rect x="160" y="112" width="120" height="36" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="220.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">パーティクル更新</text><rect x="300" y="112" width="90" height="36" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="345.0" y="130.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">カリング</text><rect x="100" y="168" width="220" height="36" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="210.0" y="186.0" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">テクスチャのアップロード</text><line x1="345" y1="148" x2="345" y2="92" stroke="currentColor" stroke-width="2" marker-end="url(#qa)"/><text x="420" y="126" text-anchor="start" style="font-size:12px;font-weight:400">Signal → Wait（フェンス）で、順番を守る</text><text x="360" y="232" text-anchor="middle" style="font-size:12px;font-weight:400">別のキューは並列に動く。キューの中は、渡した順に実行される。</text></svg>

上の図のように別のキューの仕事は並列に実行されます。ただし、「COMPUTE の結果を DIRECT が使う」のような順番は、キューどうしでは保証されません。順番をそろえたいときはフェンスを使います。

## コマンド リストを渡す

記録して `Close` したリストを `ExecuteCommandLists` で渡します。

```cpp
ID3D12CommandList* lists[] = {command_list.Get()};
command_queue->ExecuteCommandLists(ARRAYSIZE(lists), lists);
```

この呼び出しはリストをキューに積んですぐ戻ります。GPU が実行を終えるのを待ちません。そのため、渡した直後にコマンド リストを `Reset` して、別の命令を記録し始められます。一方で、リストが使っていたアロケーターは GPU が読み終わるまで `Reset` できません（[Command Allocator](command-allocator.md)）。

複数のリストは配列にまとめて、1 回で渡せます。リストは配列の順に実行されます。`ExecuteCommandLists` は呼び出しの負担が重いので、リストごとに 1 回ずつ呼ばず 1 フレームに数回までにまとめるのが定番です。

## Signal と Wait

キューにはフェンスに数字を書き込む `Signal` とフェンスが指定の数字になるまで待つ `Wait` も積めます。これは GPU が実行する命令で、CPU は待ちません。

```cpp
// このキューの、ここまでの仕事が終わったら、フェンスに value を書く。
command_queue->Signal(fence.Get(), value);

// 別のキューをフェンスが value になるまで止める。GPU の中の待ちで、CPU は止まらない。
other_queue->Wait(fence.Get(), value);
```

`Signal` は GPU の完了を CPU に知らせるときにもキューどうしの順番をそろえるときにも使います。CPU が待ちたいときはフェンスの `SetEventOnCompletion` と `WaitForSingleObject` を使います（[Fence](fence.md)）。

## 複数のキューをどう使い分けるか

最初は DIRECT のキューだけで十分です。次の段階として COPY のキューを足すとテクスチャやメッシュの読み込みを裏で進められます。ロード画面を短くしたいときに効きます。

COMPUTE のキューは描画が GPU の一部しか使っていないときに効果があります。たとえば、メモリ帯域や固定機能がボトルネックの描画と計算の重い処理を並行させると、GPU の空きを埋められます。ただし、描画と計算が同じ部分を取り合うとかえって遅くなることもあります。必ず計測してから採用します（[Async Compute](../../rendering/async-compute.md)）。

## よくあるミス

??? failure "`ExecuteCommandLists` でクラッシュする"
    リストが `Close` されていないか記録中にエラーがありました（`Close` の戻り値が失敗でした）。デバッグ レイヤーのメッセージを見ます。

??? failure "渡したあとすぐアロケーターを `Reset` してクラッシュする"
    GPU がまだそのアロケーターの命令を実行しています。フェンスで完了を確認してから `Reset` します（[Command Allocator](command-allocator.md)）。

??? failure "COMPUTE のキューで描画命令がエラーになる"
    COMPUTE のキューは `DrawInstanced` などの描画を実行できません。DIRECT のキューに渡します。

??? failure "リストごとに `ExecuteCommandLists` を呼んで、CPU が重い"
    複数のリストを配列にまとめて、1 回で渡します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] キューは GPU への仕事の入口で、`ExecuteCommandLists` で渡す
    - [x] 種類は DIRECT（全部）、COMPUTE、COPY。最初は DIRECT だけでよい
    - [x] 渡したらすぐ戻る。完了はフェンスで確認する
    - [x] 別のキューは並列に動く。順番はフェンスでそろえる

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3D12CommandQueue](api/id3d12commandqueue.md)
- [Command List](command-list.md)
- [Fence](fence.md)
- [Async Compute](../../rendering/async-compute.md)
- [Microsoft Learn: ID3D12CommandQueue](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12commandqueue)
