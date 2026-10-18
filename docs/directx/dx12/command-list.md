---
title: Command List
tags:
  - DirectX
---

# Command List

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>コマンド リスト</strong>（`ID3D12GraphicsCommandList`）は、GPU への、<strong>命令を、記録する</strong>、窓口です。`DrawInstanced`、`Dispatch`、`ResourceBarrier`、`CopyBufferRegion`、`SetPipelineState`…と、呼ぶと、命令が、[アロケーター](command-allocator.md)のメモリに、<strong>記録されるだけ</strong>で、すぐには、実行されません。記録を、`Close()` し、[キュー](command-queue.md)に、投げると、GPU が、実行します。

!!! tip "ポイント"
    - コマンド リスト ＝ 命令の、記録係。呼ぶだけで、実行は、しない。
    - 流れ: <strong>`Reset`（記録開始）→ 命令を記録 → `Close`（記録終了）→ `ExecuteCommandLists`</strong>。
    - 作成時は、記録中の状態。最初に、すぐ `Close()` するか、そのまま、記録を、始める。
    - リストは、`ExecuteCommandLists` の、<strong>直後に</strong>、`Reset` して、再利用できる。アロケーターは、GPU の完了まで、`Reset` できない。
    - 状態（PSO、ルート シグネチャ、リソースの束縛）は、<strong>リストごと</strong>。`Reset` のたびに、全部、設定し直す。

## 作る

```cpp
ComPtr<ID3D12GraphicsCommandList> command_list;
device->CreateCommandList(0,                                // NodeMask
                          D3D12_COMMAND_LIST_TYPE_DIRECT,   // キュー・アロケーターと、同じ種類
                          command_allocator.Get(),          // 記録先のアロケーター
                          nullptr,                          // 初期の PSO（nullptr で、あとで設定）
                          IID_PPV_ARGS(&command_list));
command_list->Close();                                      // 作った直後は、記録中。すぐ閉じて、最初は、Reset から始める
```

`CreateCommandList` で、作ったリストは、<strong>記録中の状態</strong>です。ふつうは、いったん、`Close()` して、毎フレームの、`Reset` から、記録を、始めます。

## 記録の、サイクル

```cpp
// ① 記録を始める: アロケーターを、巻き戻してから、リストを、Reset する。
command_allocator->Reset();                                 // GPU が、使い終わっている（フェンスで確認済み）こと
command_list->Reset(command_allocator.Get(), pipeline_state.Get());   // 初期の PSO を、渡せる

// ② 命令を、記録する（実行は、されない）。
command_list->SetGraphicsRootSignature(root_signature.Get());
command_list->RSSetViewports(1, &viewport);
command_list->RSSetScissorRects(1, &scissor);
command_list->DrawInstanced(3, 1, 0, 0);

// ③ 記録を、終える。
command_list->Close();

// ④ キューに、投げる。GPU が、あとで、実行する。
ID3D12CommandList* lists[] = {command_list.Get()};
command_queue->ExecuteCommandLists(1, lists);
```

| 関数 | 内容 |
| --- | --- |
| `Reset(allocator, pso)` | 記録を、始める。アロケーターと、初期 PSO を、渡す |
| `Close()` | 記録を、終える。戻り値が、`FAILED` なら、記録中に、エラーが、あった |
| `ExecuteCommandLists`（キュー） | 記録した、リストを、GPU に、投げる |

<strong>`Close` の、戻り値</strong>を、確認します。記録中の、エラー（不正な、状態）は、`Close` で、初めて、分かります。

## 記録できる、命令

| 種類 | 関数の例 |
| --- | --- |
| パイプラインの、設定 | `SetPipelineState`、`SetGraphicsRootSignature`、`SetComputeRootSignature` |
| リソースの、束縛 | `SetGraphicsRootDescriptorTable`、`SetGraphicsRoot32BitConstants`、`SetGraphicsRootConstantBufferView`、`SetDescriptorHeaps` |
| 入力・出力 | `IASetVertexBuffers`、`IASetIndexBuffer`、`IASetPrimitiveTopology`、`OMSetRenderTargets`、`RSSetViewports`、`RSSetScissorRects` |
| 描画 | `DrawInstanced`、`DrawIndexedInstanced`、`ExecuteIndirect` |
| 計算 | `Dispatch`、`DispatchMesh` |
| クリア | `ClearRenderTargetView`、`ClearDepthStencilView`、`ClearUnorderedAccessViewFloat` |
| コピー | `CopyResource`、`CopyBufferRegion`、`CopyTextureRegion`、`ResolveSubresource` |
| バリア | `ResourceBarrier` |
| クエリ | `BeginQuery`、`EndQuery`、`ResolveQueryData` |

## 状態は、リストごと

PSO、ルート シグネチャ、ディスクリプタ ヒープ、レンダー ターゲット、ビューポート、シザー矩形、トポロジーといった、<strong>パイプラインの、状態は、コマンド リストごと</strong>に、持たれます。`Reset` すると、全部が、初期状態（未設定）に、戻ります。

```cpp
// Reset のたびに、必要な状態を、すべて、設定し直す。
command_list->Reset(allocator, nullptr);
command_list->SetGraphicsRootSignature(root_signature.Get());       // 設定し忘れると、エラー
command_list->SetDescriptorHeaps(1, &heap);                          // ディスクリプタ ヒープも
command_list->RSSetViewports(1, &viewport);
command_list->RSSetScissorRects(1, &scissor);                        // シザーも、必ず（有効のまま）
command_list->OMSetRenderTargets(1, &rtv_handle, FALSE, &dsv_handle);
```

状態を、設定し忘れて、`Draw` すると、デバッグ レイヤーが、エラーを、出します（[Debug Layer](debug-layer.md)）。

## 複数のリストと、スレッド

1 つのリストは、<strong>1 つのスレッドだけ</strong>が、記録します。複数の、スレッドで、記録するときは、<strong>スレッドごとに、リストと、アロケーターを、持ち</strong>、最後に、まとめて、キューに、投げます。

```cpp
// 4 スレッドで、シーンを、4 分割して、記録する。
std::vector<std::thread> threads;
for (int i = 0; i < 4; ++i) {
  threads.emplace_back([&, i] {
    lists[i]->Reset(thread_allocators[i].Get(), pso.Get());
    RecordScenePart(lists[i].Get(), i);                      // 各スレッドが、別のリストに、記録
    lists[i]->Close();
  });
}
for (auto& t : threads) t.join();

ID3D12CommandList* raw[] = {lists[0].Get(), lists[1].Get(), lists[2].Get(), lists[3].Get()};
command_queue->ExecuteCommandLists(4, raw);                  // 配列の順に、実行される
```

マルチスレッドの、記録は、D3D12 の、大きな、利点の、1 つで、CPU の、ボトルネックを、減らします。

## バンドル

バンドル（`D3D12_COMMAND_LIST_TYPE_BUNDLE`）は、<strong>小さな、命令の、かたまりを、再利用</strong>する、仕組みです。何度も、同じ、描画の命令を、記録するときに、使えますが、効果は、限定的で、あまり、使われません。

## 記録中に、使える、制約

| 制約 | 内容 |
| --- | --- |
| `Close` の前に、`Reset` | 閉じていない、リストを、`Reset` すると、エラー（`Reset` は、閉じた、リストだけ） |
| 異なる、種類 | DIRECT のリストを、COMPUTE キューに、投げられない |
| 記録中の、アロケーター | 記録中の、リストが、使っている、アロケーターを、別のリストで、使えない |
| リソースの寿命 | 記録した、リソースは、GPU が、実行を、終えるまで、解放できない |

最後の項目が、D3D12 の、重要な、点です。<strong>記録中に、参照した、リソースは、GPU が、実行を、終えるまで、生かしておく</strong>必要があります（アップロード用バッファなど。[Upload Buffer](upload-buffer.md)）。

## よくあるミス

??? failure "`Reset` が、失敗する、または、デバッグ レイヤーが、「記録中」と、言う"
    `Close()` していない、リストを、`Reset` した。または、アロケーターを、GPU が、使用中に、`Reset` した。

??? failure "設定したはずの、PSO や、ルート シグネチャが、効いていない"
    `Reset` で、状態が、初期化されている。`Reset` のたびに、全部、設定し直す。

??? failure "`ExecuteCommandLists` で、クラッシュする"
    `Close()` の戻り値（`HRESULT`）を、見ていない。記録中の、不正な状態で、閉じ損ねている。

??? failure "描画後に、リソースを、解放して、クラッシュする"
    GPU が、まだ、そのリソースを、参照する、命令を、実行している。フェンスで、完了を、待ってから、解放する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コマンド リスト ＝ 命令の、記録係。呼んでも、実行されない
    - [x] 流れ: `Reset` → 記録 → `Close` → `ExecuteCommandLists`
    - [x] 状態（PSO、ルート シグネチャ、ヒープ、RT、ビューポート）は、`Reset` のたびに、設定し直す
    - [x] 記録は、1 リスト 1 スレッド。マルチスレッドは、リストを、分ける
    - [x] 記録したリソースは、GPU が、終えるまで、生かす

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Command Queue](command-queue.md)
- [Command Allocator](command-allocator.md)
- [Fence](fence.md)
- [Microsoft Learn: ID3D12GraphicsCommandList](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12graphicscommandlist)
