---
title: Frame Resources
tags:
  - DirectX
---

# Frame Resources

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

[Drawing a Triangle](triangle.md) では、毎フレーム、GPU の完了を、待ちました。これは、CPU が、GPU を、待つ間、何もしない、ので、<strong>CPU と GPU が、直列に、なり、半分ずつ、遊んでしまいます</strong>。実用では、CPU が、次のフレームを、準備している間に、GPU が、前のフレームを、実行する、<strong>フレーム イン フライト</strong>（2〜3 フレーム）にします。このとき、<strong>フレームごとに、別の、リソース</strong>（アロケーター、定数バッファ、動的な頂点バッファ）が、必要になります。

!!! tip "ポイント"
    - フレーム イン フライト ＝ CPU が、GPU より、数フレーム、先に、進む。通常 2、遅延を、気にしないなら 3。
    - <strong>フレームごとに、持つ</strong>: コマンド アロケーター、定数バッファの領域、動的な、リソース。
    - 共有する物: コマンド リスト（`Reset` で、使い回す）、PSO、ルート シグネチャ、静的なリソース。
    - フレームを、再利用する前に、<strong>そのフレームの、フェンスの値</strong>に、GPU が、達したかを、確認する。
    - 待つのは、<strong>「N フレーム前の、完了」</strong>だけ。直前のフレームを、待たない。

## 直列と、並列

```text
毎フレーム待つ（直列）:
  CPU: [記録 1]          [記録 2]          [記録 3]
  GPU:         [実行 1]          [実行 2]          [実行 3]      ← CPU と GPU が、交互に、止まる

フレーム イン フライト 2（並列）:
  CPU: [記録 1][記録 2][記録 3][記録 4]
  GPU:    [実行 1][実行 2][実行 3][実行 4]                       ← 並列に動く。フレームレートが、上がる
```

フレーム イン フライトを、2 にすると、CPU が、GPU より、1 フレーム、先に、進めます。そのぶん、入力から、画面までの、<strong>遅延は、1 フレーム、増えます</strong>。

## フレームごとの、リソース

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

フレーム イン フライトの、数だけ、<strong>アロケーターと、CPU が、毎フレーム、書く、バッファ</strong>を、持ちます。コマンド リスト自体は、1 つで、足ります（`Reset` で、毎フレーム、別の、アロケーターに、つなぐ）。

## 毎フレームの、流れ

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

①で、待つのは、<strong>「同じ、スロットを、前に、使ったフレーム」の、完了</strong>だけです。フレーム イン フライトが 2 なら、「2 フレーム前」の完了を、待ちます。普通は、GPU が、すでに、終えているので、<strong>待たずに、すぐ、進めます</strong>。

## フェンスの値の、流れ

| フレーム | スロット | 開始時に、待つ値 | 終了時に、Signal する値 |
| --- | --- | --- | --- |
| 0 | 0 | 0（待たない） | 1 |
| 1 | 1 | 0（待たない） | 2 |
| 2 | 0 | 1（フレーム 0 の完了） | 3 |
| 3 | 1 | 2（フレーム 1 の完了） | 4 |

フレーム 2 が、始まる、とき、スロット 0 の、リソースを、使う、前に、フレーム 0 の、完了（値 1）を、確認します。

## バック バッファの、インデックスと、フレームの、スロット

バック バッファの、番号（`GetCurrentBackBufferIndex()`）と、フレームごとの、リソースの、スロット（`frame_number % kFrameCount`）は、<strong>別の物</strong>です。`BufferCount` と `kFrameCount` を、同じ数にして、<strong>バック バッファの、インデックスを、そのまま、スロットにも、使う</strong>、簡単な、構成も、多いです。

```cpp
const UINT index = swap_chain->GetCurrentBackBufferIndex();   // BufferCount == kFrameCount なら、これを、スロットにも、使える
FrameResource& frame = frames[index];
```

## 遅延を、制御する

フレーム イン フライトが、多いほど、CPU が、先に、進めて、滑らかですが、<strong>入力の、遅延</strong>が、増えます。スワップ チェーンの、`FRAME_LATENCY_WAITABLE_OBJECT` で、遅延を、さらに、絞れます。

```cpp
// スワップ チェーンの作成時に、フラグを付ける。
desc.Flags = DXGI_SWAP_CHAIN_FLAG_FRAME_LATENCY_WAITABLE_OBJECT;
// 作成後:
swap_chain->SetMaximumFrameLatency(1);                         // 先行できる、フレーム数を 1 に
HANDLE waitable = swap_chain->GetFrameLatencyWaitableObject();
// 毎フレームの先頭: WaitForSingleObjectEx(waitable, 1000, TRUE);   // GPU が、1 フレーム以内に、追いつくまで、待つ
```

遅延に、敏感な、ゲーム（アクション、VR）で、使います。

## 動的なリソースの、扱い

毎フレーム、書く、動的な、頂点バッファ、ディスクリプタ、定数バッファは、<strong>フレームごとに、別の領域</strong>に、書きます。GPU が、前のフレームを、読んでいる間に、書き換えないためです。

| リソース | 持ち方 |
| --- | --- |
| 定数バッファ | 1 つの、大きなバッファを、フレーム数で、分割（[Constant Buffer](constant-buffer.md)） |
| 動的な頂点バッファ | 同様に、フレームごとに、領域を、分ける |
| ディスクリプタ（動的に、書く物） | シェーダー可視ヒープを、フレーム数で、分割 |
| アップロードの、中継バッファ | 使い終わるまで（フェンスで、確認）、保持。リングで、再利用 |

## 解放の、遅延

GPU が、まだ、使っているかもしれない、リソースを、すぐ、解放すると、クラッシュします。リソースを、「解放待ち」の、リストに、入れ、<strong>kFrameCount フレーム後に、解放</strong>する、仕組みを、持ちます。

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

??? failure "ときどき、画面が、ちらつく、乱れる（再現が、不安定）"
    フレームの、リソースを、GPU の、完了確認なしで、再利用した（アロケーターを、`Reset`、定数バッファを、上書き）。①の、待ちを、確認する。

??? failure "フレームレートが、上がらない"
    毎フレーム、全完了待ち（`WaitForGpu`）を、している。フレーム イン フライト（2 以上）に、して、同じスロットを、前に、使った、フレームだけを、待つ。

??? failure "定数バッファを、1 つだけ、持って、全フレームで、使い回している"
    GPU が、読んでいる間に、CPU が、上書きする。フレーム数だけ、領域を、持つ。

??? failure "入力から、画面まで、遅延が、大きい"
    フレーム イン フライトが、多すぎる（3 以上）。2 にする、または、`SetMaximumFrameLatency(1)`。

??? failure "リソースを、すぐ、解放して、クラッシュする"
    GPU が、まだ、使っている。フェンスの値で、遅延して、解放する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フレーム イン フライト（2〜3）で、CPU と GPU を、並列に
    - [x] フレームごとに、持つ: アロケーター、定数バッファの領域、動的リソース
    - [x] 開始時に、同じスロットを、前に、使ったフレームの、フェンス値を、待つ
    - [x] 終了時に、`Signal` して、値を、覚える
    - [x] 遅延が、気になるなら、2 に、または、`SetMaximumFrameLatency`
    - [x] リソースの解放は、完了後に、遅延させる

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Fence](fence.md)
- [Command Allocator](command-allocator.md)
- [Constant Buffer](constant-buffer.md)
- [Microsoft Learn: マルチエンジンの同期](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/user-mode-heap-synchronization)
