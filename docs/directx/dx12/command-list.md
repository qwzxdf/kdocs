---
title: Command List
tags:
  - DirectX
---

# Command List

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>コマンド リスト</strong>（`ID3D12GraphicsCommandList`）は GPU への <strong>命令を記録する</strong>、窓口です。`DrawInstanced`、`Dispatch`、`ResourceBarrier`、`CopyBufferRegion`、`SetPipelineState`…と呼ぶと命令が[アロケーター](command-allocator.md)のメモリに <strong>記録されるだけ</strong>ですぐには、実行されません。記録を `Close()` し[キュー](command-queue.md)に投げると、GPU が実行します。

!!! tip "ポイント"
    - コマンド リスト ＝ 命令の記録係。呼ぶだけで実行はしない。
    - 流れ: <strong>`Reset`（記録開始）→ 命令を記録 → `Close`（記録終了）→ `ExecuteCommandLists`</strong>。
    - 作成時は記録中の状態。最初にすぐ `Close()` するかそのまま記録を始める。
    - リストは `ExecuteCommandLists` の <strong>直後に</strong>、`Reset` して再利用できる。アロケーターは GPU の完了まで、`Reset` できない。
    - 状態（PSO、ルート シグネチャ、リソースの束縛）は <strong>リストごと</strong>。`Reset` のたびに全部、設定し直す。

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

`CreateCommandList` で作ったリストは <strong>記録中の状態</strong>です。ふつうはいったん `Close()` して毎フレームの `Reset` から記録を始めます。

## 記録のサイクル

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
| `Reset(allocator, pso)` | 記録を始める。アロケーターと初期 PSO を渡す |
| `Close()` | 記録を終える。戻り値が `FAILED` なら記録中にエラーが、あった |
| `ExecuteCommandLists`（キュー） | 記録したリストを GPU に投げる |

<strong>`Close` の戻り値</strong>を確認します。記録中のエラー（不正な状態）は `Close` で初めて、分かります。

## 記録できる命令

| 種類 | 関数の例 |
| --- | --- |
| パイプラインの設定 | `SetPipelineState`、`SetGraphicsRootSignature`、`SetComputeRootSignature` |
| リソースの束縛 | `SetGraphicsRootDescriptorTable`、`SetGraphicsRoot32BitConstants`、`SetGraphicsRootConstantBufferView`、`SetDescriptorHeaps` |
| 入力・出力 | `IASetVertexBuffers`、`IASetIndexBuffer`、`IASetPrimitiveTopology`、`OMSetRenderTargets`、`RSSetViewports`、`RSSetScissorRects` |
| 描画 | `DrawInstanced`、`DrawIndexedInstanced`、`ExecuteIndirect` |
| 計算 | `Dispatch`、`DispatchMesh` |
| クリア | `ClearRenderTargetView`、`ClearDepthStencilView`、`ClearUnorderedAccessViewFloat` |
| コピー | `CopyResource`、`CopyBufferRegion`、`CopyTextureRegion`、`ResolveSubresource` |
| バリア | `ResourceBarrier` |
| クエリ | `BeginQuery`、`EndQuery`、`ResolveQueryData` |

## 状態はリストごと

PSO、ルート シグネチャ、ディスクリプタ ヒープ、レンダー ターゲット、ビューポート、シザー矩形、トポロジーといった <strong>パイプラインの状態は、コマンド リストごと</strong>に持たれます。`Reset` すると全部が初期状態（未設定）に戻ります。

```cpp
// Reset のたびに、必要な状態を、すべて、設定し直す。
command_list->Reset(allocator, nullptr);
command_list->SetGraphicsRootSignature(root_signature.Get());       // 設定し忘れると、エラー
command_list->SetDescriptorHeaps(1, &heap);                          // ディスクリプタ ヒープも
command_list->RSSetViewports(1, &viewport);
command_list->RSSetScissorRects(1, &scissor);                        // シザーも、必ず（有効のまま）
command_list->OMSetRenderTargets(1, &rtv_handle, FALSE, &dsv_handle);
```

状態を設定し忘れて `Draw` すると、デバッグ レイヤーがエラーを出します（[Debug Layer](debug-layer.md)）。

## 複数のリストとスレッド

1 つのリストは <strong>1 つのスレッドだけ</strong>が、記録します。複数のスレッドで記録するときは <strong>スレッドごとにリストとアロケーターを持ち</strong>、最後にまとめてキューに投げます。

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

マルチスレッドの記録は D3D12 の大きな利点の 1 つで CPU のボトルネックを、減らします。

## バンドル

バンドル（`D3D12_COMMAND_LIST_TYPE_BUNDLE`）は <strong>小さな命令のかたまりを再利用</strong>する仕組みです。何度も同じ描画の命令を記録するときに使えますが効果は限定的であまり使われません。

## 記録中に使える制約

| 制約 | 内容 |
| --- | --- |
| `Close` の前に `Reset` | 閉じていない、リストを `Reset` するとエラー（`Reset` は閉じたリストだけ） |
| 異なる種類 | DIRECT のリストを COMPUTE キューに投げられない |
| 記録中のアロケーター | 記録中のリストが使っているアロケーターを別のリストで使えない |
| リソースの寿命 | 記録したリソースは GPU が実行を終えるまで、解放できない |

最後の項目が D3D12 の重要な点です。<strong>記録中に参照したリソースは GPU が実行を終えるまで生かしておく</strong>必要があります（アップロード用バッファなど。[Upload Buffer](upload-buffer.md)）。

## よくあるミス

??? failure "`Reset` が、失敗するまたはデバッグ レイヤーが、「記録中」と言う"
    `Close()` していないリストを `Reset` した。または、アロケーターを GPU が使用中に `Reset` した。

??? failure "設定したはずの PSO やルート シグネチャが、効いていない"
    `Reset` で状態が初期化されている。`Reset` のたびに全部、設定し直す。

??? failure "`ExecuteCommandLists` で、クラッシュする"
    `Close()` の戻り値（`HRESULT`）を見ていない。記録中の不正な状態で閉じ損ねている。

??? failure "描画後にリソースを解放してクラッシュする"
    GPU がまだそのリソースを参照する命令を実行している。フェンスで完了を待ってから解放する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コマンド リスト ＝ 命令の記録係。呼んでも実行されない
    - [x] 流れ: `Reset` → 記録 → `Close` → `ExecuteCommandLists`
    - [x] 状態（PSO、ルート シグネチャ、ヒープ、RT、ビューポート）は `Reset` のたびに設定し直す
    - [x] 記録は 1 リスト 1 スレッド。マルチスレッドはリストを分ける
    - [x] 記録したリソースは、GPU が終えるまで生かす

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Command Queue](command-queue.md)
- [Command Allocator](command-allocator.md)
- [Fence](fence.md)
- [Microsoft Learn: ID3D12GraphicsCommandList](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12graphicscommandlist)
