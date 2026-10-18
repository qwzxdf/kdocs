---
title: Frame Resources
tags:
  - DirectX
---

# Frame Resources

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

[Drawing a Triangle](triangle.md) では、毎フレーム、GPU の完了を待ちました。これは CPU が GPU を待つ間、何もしないので <strong>CPU と GPU が直列になり半分ずつ遊んでしまいます</strong>。実用では CPU が次のフレームを準備している間に GPU が前のフレームを、実行する <strong>フレーム イン フライト</strong>（2〜3 フレーム）にします。このとき、<strong>フレームごとに別のリソース</strong>（アロケーター、定数バッファ、動的な頂点バッファ）が必要になります。

!!! tip "ポイント"
    - フレーム イン フライト ＝ CPU が、GPU より数フレーム、先に進む。通常 2、遅延を気にしないなら 3。
    - <strong>フレームごとに持つ</strong>: コマンド アロケーター、定数バッファの領域、動的なリソース。
    - 共有する物: コマンド リスト（`Reset` で、使い回す）、PSO、ルート シグネチャ、静的なリソース。
    - フレームを再利用する前に <strong>そのフレームのフェンスの値</strong>に GPU が達したかを確認する。
    - 待つのは <strong>「N フレーム前の完了」</strong>だけ。直前のフレームを待たない。

## 直列と並列

```text
毎フレーム待つ（直列）:
  CPU: [記録 1]          [記録 2]          [記録 3]
  GPU:         [実行 1]          [実行 2]          [実行 3]      ← CPU と GPU が、交互に、止まる

フレーム イン フライト 2（並列）:
  CPU: [記録 1][記録 2][記録 3][記録 4]
  GPU:    [実行 1][実行 2][実行 3][実行 4]                       ← 並列に動く。フレームレートが、上がる
```

フレーム イン フライトを 2 にすると、CPU が GPU より 1 フレーム、先に進めます。そのぶん入力から画面までの <strong>遅延は、1 フレーム、増えます</strong>。

## フレームごとのリソース

```cpp
constexpr UINT kFrameCount = 2;                               // フレーム イン フライトの数

struct FrameResource {
  ComPtr<ID3D12CommandAllocator> allocator;                   // 記録した命令の、保管メモリ（フレームごと）
  ComPtr<ID3D12Resource> constant_buffer;                     // 定数バッファ（UPLOAD。フレームごと）
  uint8_t* constant_mapped = nullptr;                         // 永続的に Map したポインター
  UINT64 fence_value = 0;                                     // このフレームの、GPU 完了を、示す、フェンスの値
};

FrameResource frames[kFrameCount];

// 作成: フレームごとに、別のアロケーターと、定数バッファ。
for (auto& frame : frames) {
  device->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, IID_PPV_ARGS(&frame.allocator));
  // 定数バッファは、UPLOAD ヒープに作り、永続 Map（constant-buffer.md）
}
```

フレーム イン フライトの数だけ <strong>アロケーターと CPU が毎フレーム、書くバッファ</strong>を持ちます。コマンド リスト自体は 1 つで、足ります（`Reset` で毎フレーム、別のアロケーターにつなぐ）。

## 毎フレームの流れ

```cpp
UINT frame_number = 0;

void RenderFrame() {
  FrameResource& frame = frames[frame_number % kFrameCount];

  // ① このフレームの、リソースを、前に、使った（kFrameCount フレーム前の）GPU 実行の、完了を、待つ。
  if (fence->GetCompletedValue() < frame.fence_value) {
    fence->SetEventOnCompletion(frame.fence_value, fence_event);
    WaitForSingleObject(fence_event, INFINITE);               // 完了していなければ、ここで、待つ
  }

  // ② もう、GPU が使っていないので、アロケーターを、Reset し、定数バッファを、書き換えてよい。
  frame.allocator->Reset();
  command_list->Reset(frame.allocator.Get(), nullptr);
  UpdateConstants(frame.constant_mapped);                     // このフレーム専用の領域に、書く

  // ③ 記録 → 投げる → Present
  RecordCommands(command_list.Get(), frame);
  command_list->Close();
  ID3D12CommandList* lists[] = {command_list.Get()};
  command_queue->ExecuteCommandLists(1, lists);
  swap_chain->Present(1, 0);

  // ④ このフレームの、完了の目印（Signal）を、キューに積み、値を、覚える。
  frame.fence_value = ++fence_value;
  command_queue->Signal(fence.Get(), frame.fence_value);

  ++frame_number;
}
```

①で待つのは <strong>「同じスロットを前に使ったフレーム」の完了</strong>だけです。フレーム イン フライトが 2 なら「2 フレーム前」の完了を待ちます。普通は、GPU がすでに終えているので、<strong>待たずにすぐ進めます</strong>。

## フェンスの値の流れ

| フレーム | スロット | 開始時に待つ値 | 終了時に Signal する値 |
| --- | --- | --- | --- |
| 0 | 0 | 0（待たない） | 1 |
| 1 | 1 | 0（待たない） | 2 |
| 2 | 0 | 1（フレーム 0 の完了） | 3 |
| 3 | 1 | 2（フレーム 1 の完了） | 4 |

フレーム 2 が始まるときスロット 0 のリソースを使う前にフレーム 0 の、完了（値 1）を確認します。

## バック バッファのインデックスとフレームのスロット

バック バッファの番号（`GetCurrentBackBufferIndex()`）とフレームごとのリソースのスロット（`frame_number % kFrameCount`）は、<strong>別の物</strong>です。`BufferCount` と `kFrameCount` を同じ数にして <strong>バック バッファのインデックスをそのままスロットにも使う</strong>、簡単な構成も多いです。

```cpp
const UINT index = swap_chain->GetCurrentBackBufferIndex();   // BufferCount == kFrameCount なら、これを、スロットにも、使える
FrameResource& frame = frames[index];
```

## 遅延を制御する

フレーム イン フライトが多いほど CPU が先に進めて滑らかですが、<strong>入力の遅延</strong>が増えます。スワップ チェーンの `FRAME_LATENCY_WAITABLE_OBJECT` で遅延をさらに絞れます。

```cpp
// スワップ チェーンの作成時に、フラグを付ける。
desc.Flags = DXGI_SWAP_CHAIN_FLAG_FRAME_LATENCY_WAITABLE_OBJECT;
// 作成後:
swap_chain->SetMaximumFrameLatency(1);                         // 先行できる、フレーム数を 1 に
HANDLE waitable = swap_chain->GetFrameLatencyWaitableObject();
// 毎フレームの先頭: WaitForSingleObjectEx(waitable, 1000, TRUE);   // GPU が、1 フレーム以内に、追いつくまで、待つ
```

遅延に敏感なゲーム（アクション、VR）で使います。

## 動的なリソースの扱い

毎フレーム、書く動的な頂点バッファ、ディスクリプタ、定数バッファは <strong>フレームごとに別の領域</strong>に書きます。GPU が前のフレームを読んでいる間に書き換えないためです。

| リソース | 持ち方 |
| --- | --- |
| 定数バッファ | 1 つの大きなバッファをフレーム数で、分割（[Constant Buffer](constant-buffer.md)） |
| 動的な頂点バッファ | 同様にフレームごとに領域を分ける |
| ディスクリプタ（動的に書く物） | シェーダー可視ヒープをフレーム数で分割 |
| アップロードの中継バッファ | 使い終わるまで（フェンスで確認）、保持。リングで再利用 |

## 解放の遅延

GPU がまだ使っているかもしれない、リソースをすぐ解放するとクラッシュします。リソースを「解放待ち」のリストに入れ <strong>kFrameCount フレーム後に、解放</strong>する仕組みを持ちます。

```cpp
struct PendingRelease {
  ComPtr<ID3D12Resource> resource;
  UINT64 fence_value;                                          // この値に、GPU が、達したら、解放してよい
};
std::vector<PendingRelease> pending_;

void ScheduleRelease(ComPtr<ID3D12Resource> resource) {
  pending_.push_back({std::move(resource), fence_value + 1});  // 次に Signal する値が、完了したら
}

void CollectGarbage() {                                        // 毎フレーム呼ぶ
  UINT64 completed = fence->GetCompletedValue();
  std::erase_if(pending_, [&](const PendingRelease& p) { return p.fence_value <= completed; });
}
```

## 終了時

```cpp
void Shutdown() {
  // 全フレームの、GPU 完了を、待つ。
  command_queue->Signal(fence.Get(), ++fence_value);
  fence->SetEventOnCompletion(fence_value, fence_event);
  WaitForSingleObject(fence_event, INFINITE);
  CloseHandle(fence_event);
}
```

## よくあるミス

??? failure "ときどき画面が、ちらつく乱れる（再現が不安定）"
    フレームのリソースを GPU の完了確認なしで再利用した（アロケーターを `Reset`、定数バッファを上書き）。①の待ちを確認する。

??? failure "フレームレートが、上がらない"
    毎フレーム、全完了待ち（`WaitForGpu`）をしている。フレーム イン フライト（2 以上）にして、同じスロットを前に使ったフレームだけを待つ。

??? failure "定数バッファを 1 つだけ持って全フレームで、使い回している"
    GPU が読んでいる間に CPU が上書きする。フレーム数だけ領域を持つ。

??? failure "入力から、画面まで遅延が大きい"
    フレーム イン フライトが、多すぎる（3 以上）。2 にするまたは `SetMaximumFrameLatency(1)`。

??? failure "リソースをすぐ解放してクラッシュする"
    GPU がまだ使っている。フェンスの値で遅延して解放する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フレーム イン フライト（2〜3）で、CPU と GPU を並列に
    - [x] フレームごとに持つ: アロケーター、定数バッファの領域、動的リソース
    - [x] 開始時に同じスロットを前に使ったフレームのフェンス値を待つ
    - [x] 終了時に `Signal` して値を覚える
    - [x] 遅延が気になるなら 2 にまたは `SetMaximumFrameLatency`
    - [x] リソースの解放は、完了後に遅延させる

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Fence](fence.md)
- [Command Allocator](command-allocator.md)
- [Constant Buffer](constant-buffer.md)
- [Microsoft Learn: マルチエンジンの同期](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/user-mode-heap-synchronization)
