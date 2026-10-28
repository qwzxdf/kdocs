---
title: Frame Resources
tags:
  - DirectX
---

# Frame Resources

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

[Drawing a Triangle](triangle.md) では、毎フレーム、GPU の完了を待ちました。分かりやすい代わりに CPU は GPU が終わるまで何もせず GPU は CPU が次のフレームを記録するまで何もしません。2 つが交互にしか動かないので、どちらも半分ずつ遊んでしまいます。

そこで実用では CPU が次のフレームを準備している間に GPU が前のフレームを実行するようにします。これを<strong>フレーム イン フライト</strong>と呼び 2 から 3 フレームを同時に進めます。このとき、CPU が書くものをフレームごとに別にしなければなりません。GPU がまだ前のフレームのデータを読んでいる間に CPU が上書きしてはいけないからです。

!!! tip "ポイント"
    - フレーム イン フライトは、CPU が GPU より数フレーム先に進むこと。ふつうは 2、遅延を気にしないなら 3。
    - フレームごとに持つのは、コマンド アロケーター、定数バッファの領域、動的なリソース。
    - 共有してよいのは、コマンド リスト（`Reset` で使い回す）、PSO、ルート シグネチャ、変わらないリソース。
    - フレームのリソースを再利用する前にそのフレームのフェンスの値に GPU が達したかを確認する。
    - 待つのは「同じスロットを前に使ったフレーム」の完了だけ。直前のフレームは待たない。

!!! info "このページを読む前に"
    フェンスの使い方は [Fence](fence.md)、アロケーターの `Reset` の決まりは [Command Allocator](command-allocator.md)、定数バッファをフレームごとに分ける理由は [Constant Buffer](constant-buffer.md) で説明しています。3 つとも読んでから進むとこのページの流れが分かりやすくなります。

## 直列と並列

毎フレーム待つと CPU と GPU が交互に止まります。フレーム イン フライトを 2 にすると、並列に動きます。

```text
毎フレーム待つ（直列）:
  CPU: [記録 1]          [記録 2]          [記録 3]
  GPU:         [実行 1]          [実行 2]          [実行 3]    ← CPU と GPU が交互に止まる

フレーム イン フライト 2（並列）:
  CPU: [記録 1][記録 2][記録 3][記録 4]
  GPU:    [実行 1][実行 2][実行 3][実行 4]                     ← 並列に動く。フレームレートが上がる
```

並列にすると CPU が GPU より 1 フレーム先に進めます。そのぶん入力が画面に出るまでの遅延が 1 フレームぶん増えます。

## フレームごとのリソース

フレームごとに別のアロケーターと別の定数バッファの領域を持ちます。

```cpp
constexpr UINT kFrameCount = 2;  // フレーム イン フライトの数

struct FrameResource {
  ComPtr<ID3D12CommandAllocator> allocator;  // 記録した命令の保管メモリ（フレームごと）
  ComPtr<ID3D12Resource> constant_buffer;    // 定数バッファ（UPLOAD。フレームごと）
  uint8_t* constant_mapped = nullptr;        // 永続的に Map したポインター
  UINT64 fence_value = 0;                    // このフレームの GPU 完了を示す、フェンスの値
};

FrameResource frames[kFrameCount];

// 作成。フレームごとに、別のアロケーターと定数バッファを作る。
for (auto& frame : frames) {
  device->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, IID_PPV_ARGS(&frame.allocator));
  // 定数バッファは UPLOAD のヒープに作って、永続的に Map する（Constant Buffer のページ）
}
```

コマンド リスト自体は 1 つで足ります。毎フレーム `Reset` で別のアロケーターにつなぎ直します。

## 毎フレームの流れ

```cpp
UINT frame_number = 0;

void RenderFrame() {
  FrameResource& frame = frames[frame_number % kFrameCount];

  // 1. このフレームのリソースを前に使った（kFrameCount フレーム前の）GPU 実行の完了を待つ。
  if (fence->GetCompletedValue() < frame.fence_value) {
    fence->SetEventOnCompletion(frame.fence_value, fence_event);
    WaitForSingleObject(fence_event, INFINITE);  // 完了していなければ、ここで待つ
  }

  // 2. もう GPU が使っていないので、アロケーターを Reset し、定数バッファを書き換えてよい。
  frame.allocator->Reset();
  command_list->Reset(frame.allocator.Get(), nullptr);
  UpdateConstants(frame.constant_mapped);  // このフレーム専用の領域に書く

  // 3. 記録して、渡して、Present する。
  RecordCommands(command_list.Get(), frame);
  command_list->Close();
  ID3D12CommandList* lists[] = {command_list.Get()};
  command_queue->ExecuteCommandLists(1, lists);
  swap_chain->Present(1, 0);

  // 4. このフレームの完了の目印（Signal）をキューに積み、値を覚える。
  frame.fence_value = ++fence_value;
  command_queue->Signal(fence.Get(), frame.fence_value);

  ++frame_number;
}
```

1 番で待つのは同じスロットを前に使ったフレームの完了だけです。フレーム イン フライトが 2 なら 2 フレーム前の完了を待ちます。ふつうは GPU がすでに終えているので、待たずにすぐ進めます。

## フェンスの値の流れ

フレーム 0 とフレーム 1 はまだどのスロットも使われていないので、待たずに進めます。終わるときにそれぞれ 1 と 2 を `Signal` します。フレーム 2 はスロット 0 を再び使うので、始める前にフレーム 0 の完了（値 1）を確認します。フレーム 3 はスロット 1 を使うので、フレーム 1 の完了（値 2）を確認します。そして、それぞれ 3 と 4 を `Signal` します。

## バック バッファの番号とフレームのスロット

バック バッファの番号（`GetCurrentBackBufferIndex()`）とフレームごとのリソースのスロット（`frame_number % kFrameCount`）は、別のものです。`BufferCount` と `kFrameCount` を同じ数にしてバック バッファの番号をそのままスロットにも使う簡単な構成がよく使われます。

```cpp
const UINT index = swap_chain->GetCurrentBackBufferIndex();  // BufferCount と kFrameCount が同じなら、スロットにも使える
FrameResource& frame = frames[index];
```

## 遅延を絞る

フレーム イン フライトを増やすと CPU が先へ進めて滑らかになる代わりに、入力の遅延が増えます。スワップ チェーンの `FRAME_LATENCY_WAITABLE_OBJECT` を使うと遅延をさらに絞れます。

```cpp
// スワップ チェーンを作るときに、フラグを付ける。
desc.Flags = DXGI_SWAP_CHAIN_FLAG_FRAME_LATENCY_WAITABLE_OBJECT;
// 作ったあと。
swap_chain->SetMaximumFrameLatency(1);  // 先行できるフレーム数を 1 にする
HANDLE waitable = swap_chain->GetFrameLatencyWaitableObject();
// 毎フレームの先頭で WaitForSingleObjectEx(waitable, 1000, TRUE) を呼び、GPU が追いつくのを待つ
```

遅延に敏感なアクション ゲームや VR で使います。

## 動的なリソースの扱い

毎フレーム書く動的な頂点バッファ、ディスクリプタ、定数バッファはフレームごとに別の領域へ書きます。定数バッファと動的な頂点バッファは 1 つの大きなバッファをフレームの数で分割します。動的に書くディスクリプタはシェーダー可視ヒープをフレームの数で分割します。アップロードの中継バッファは使い終わる（フェンスで確認する）まで持ち続け、リングで再利用します。

## 解放を遅らせる

GPU がまだ使っているかもしれないリソースをすぐ解放すると、クラッシュします。そこで、リソースを「解放待ち」のリストへ入れて、`kFrameCount` フレームあとに解放する仕組みを持ちます。

```cpp
struct PendingRelease {
  ComPtr<ID3D12Resource> resource;
  UINT64 fence_value;  // この値に GPU が達したら、解放してよい
};
std::vector<PendingRelease> pending_;

void ScheduleRelease(ComPtr<ID3D12Resource> resource) {
  pending_.push_back({std::move(resource), fence_value + 1});  // 次に Signal する値が完了したら
}

void CollectGarbage() {  // 毎フレーム呼ぶ
  UINT64 completed = fence->GetCompletedValue();
  std::erase_if(pending_, [&](const PendingRelease& p) { return p.fence_value <= completed; });
}
```

## 終了するとき

終了前には全フレームの GPU の完了を待ちます。

```cpp
void Shutdown() {
  command_queue->Signal(fence.Get(), ++fence_value);
  fence->SetEventOnCompletion(fence_value, fence_event);
  WaitForSingleObject(fence_event, INFINITE);
  CloseHandle(fence_event);
}
```

## よくあるミス

??? failure "ときどき画面がちらつく、乱れる（再現が不安定）"
    フレームのリソースを GPU の完了を確認せずに再利用しています（アロケーターを `Reset` したり、定数バッファを上書きしたりしています）。1 番の待ちを確認します。

??? failure "フレームレートが上がらない"
    毎フレーム、全完了待ち（`WaitForGpu`）をしています。フレーム イン フライトを 2 以上にして、同じスロットを前に使ったフレームだけを待ちます。

??? failure "定数バッファを 1 つだけ持って、全フレームで使い回している"
    GPU が読んでいる間に CPU が上書きします。フレームの数だけ領域を持ちます。

??? failure "入力から画面までの遅延が大きい"
    フレーム イン フライトが多すぎます（3 以上）。2 にするか `SetMaximumFrameLatency(1)` を使います。

??? failure "リソースをすぐ解放してクラッシュする"
    GPU がまだ使っています。フェンスの値で遅らせて解放します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フレーム イン フライト（2 から 3）で、CPU と GPU を並列にする
    - [x] フレームごとに持つのは、アロケーター、定数バッファの領域、動的なリソース
    - [x] フレームの開始時に同じスロットを前に使ったフレームのフェンスの値を待つ
    - [x] 終わりに `Signal` して、値を覚える
    - [x] 遅延が気になるなら 2 にするか `SetMaximumFrameLatency` を使う
    - [x] リソースの解放は、完了後まで遅らせる

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Fence](fence.md)
- [Command Allocator](command-allocator.md)
- [Constant Buffer](constant-buffer.md)
- [Microsoft Learn: マルチエンジンの同期](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/user-mode-heap-synchronization)
