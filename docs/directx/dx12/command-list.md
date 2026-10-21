---
title: Command List
tags:
  - DirectX
---

# Command List

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

`DrawInstanced` を呼んだらすぐ絵が描かれる。D3D11 まではそう考えても大きな間違いではありませんでした。D3D12 では違います。`DrawInstanced`、`Dispatch`、`ResourceBarrier`、`CopyBufferRegion`、`SetPipelineState` など GPU にさせたいことを呼んでもそれは<strong>命令として記録されるだけ</strong>です。記録を書き込む入れ物が <strong>コマンド リスト</strong>（`ID3D12GraphicsCommandList`）です。

記録を終えたリストを [Command Queue](command-queue.md) に渡して、初めて GPU が実行します。記録と実行を分けると命令を作る仕事を複数のスレッドに分けられます。CPU の負荷を下げられるのが、D3D12 の大きな利点です。

!!! tip "ポイント"
    - コマンド リストは命令の記録係。呼んでも実行はされない。
    - 流れは `Reset`（記録開始）、命令を記録、`Close`（記録終了）、`ExecuteCommandLists`。
    - 作った直後は「記録中」の状態。すぐ `Close` して毎フレームの `Reset` から始めるのが定番。
    - PSO、ルート シグネチャ、ビューポートなどの状態はリストごとに持つ。`Reset` のたびに設定し直す。
    - 記録したリソースは GPU が実行を終えるまで解放してはいけない。

!!! info "このページを読む前に"
    命令の置き場は [Command Allocator](command-allocator.md)、リストを GPU に渡す窓口は [Command Queue](command-queue.md) です。どちらも短いので先に目を通しておくとこのページの流れが追いやすくなります。メソッドの引数と戻り値は[ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md) にまとめています。

## 作る

コマンド リストは `CreateCommandList` で作ります。種類と記録先のアロケーターを渡します。

```cpp
ComPtr<ID3D12GraphicsCommandList> command_list;
device->CreateCommandList(0,                               // NodeMask
                          D3D12_COMMAND_LIST_TYPE_DIRECT,  // キューとアロケーターと同じ種類
                          command_allocator.Get(),         // 記録先のアロケーター
                          nullptr,                         // 初期の PSO（あとで設定するので nullptr）
                          IID_PPV_ARGS(&command_list));
command_list->Close();  // 作った直後は記録中。いったん閉じて、最初のフレームの Reset から始める
```

作ったリストはすでに記録中の状態です。記録するつもりがなければ閉じておかないとあとで `Reset` ができません。

## 記録のサイクル

1 フレームの記録は 4 つの段階に分かれます。

```cpp
// 1. 記録を始める。アロケーターを巻き戻してから、リストを Reset する。
command_allocator->Reset();  // GPU が使い終わっていること（フェンスで確認済み）
command_list->Reset(command_allocator.Get(), pipeline_state.Get());

// 2. 命令を記録する。この時点では、何も実行されない。
command_list->SetGraphicsRootSignature(root_signature.Get());
command_list->RSSetViewports(1, &viewport);
command_list->RSSetScissorRects(1, &scissor);
command_list->DrawInstanced(3, 1, 0, 0);

// 3. 記録を終える。
command_list->Close();

// 4. キューに渡す。GPU があとで実行する。
ID3D12CommandList* lists[] = {command_list.Get()};
command_queue->ExecuteCommandLists(1, lists);
```

`Reset` はリストを記録できる状態に戻す操作です。そのとき、記録先のアロケーターと最初に使う PSO を渡します。アロケーターのほうは先に `Reset` しておきます。順番はアロケーターが先、リストがあとです。

`Close` は記録の終わりを宣言します。戻り値が大切で**記録中に起きたエラー（不正な状態、足りない設定など）は `Close` を呼んで初めて分かります**。`Draw` の呼び出し自体は失敗してもエラーを返しません。戻り値を無視すると壊れたリストをキューに渡してしまいます。

`ExecuteCommandLists` はキューに渡す操作です。戻ったあとで同じリストをすぐ `Reset` して別の命令を記録し始められます。アロケーターのほうは GPU が読み終わるまで、`Reset` できません。

## どんな命令を記録できるか

リストに記録できる命令は役割ごとに次のように分かれます。1 つずつの引数は [ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md) にあります。

パイプラインの設定は `SetPipelineState`、`SetGraphicsRootSignature`、`SetComputeRootSignature` です。シェーダーに渡すリソースは `SetGraphicsRootDescriptorTable`、`SetGraphicsRoot32BitConstants`、`SetGraphicsRootConstantBufferView`、`SetDescriptorHeaps` で結びます。

入力と出力の設定は `IASetVertexBuffers`、`IASetIndexBuffer`、`IASetPrimitiveTopology`、`OMSetRenderTargets`、`RSSetViewports`、`RSSetScissorRects` です。描画は `DrawInstanced`、`DrawIndexedInstanced`、`ExecuteIndirect`、計算は `Dispatch` と `DispatchMesh` を使います。

クリアは `ClearRenderTargetView`、`ClearDepthStencilView` などコピーは `CopyResource`、`CopyBufferRegion`、`CopyTextureRegion` です。リソースの状態の切り替えは `ResourceBarrier`、計測は `BeginQuery`、`EndQuery`、`ResolveQueryData` を使います。

## 状態はリストごとに持つ

PSO、ルート シグネチャ、ディスクリプタ ヒープ、レンダー ターゲット、ビューポート、シザー矩形などの「パイプラインの状態」は、リストごとに持たれます。`Reset` するとすべて未設定に戻ります。前のフレームの設定は引き継がれません。

```cpp
// Reset のたびに、必要な状態をすべて設定し直す。
command_list->Reset(allocator, nullptr);
command_list->SetGraphicsRootSignature(root_signature.Get());
command_list->SetDescriptorHeaps(1, &heap);
command_list->RSSetViewports(1, &viewport);
command_list->RSSetScissorRects(1, &scissor);  // シザーは常に有効。設定しないと何も描かれない
command_list->OMSetRenderTargets(1, &rtv_handle, FALSE, &dsv_handle);
```

設定を 1 つ忘れて `Draw` を呼ぶとデバッグ レイヤーがエラーを出します（[Debug Layer](debug-layer.md)）。ビューポートとシザー矩形を忘れると、何のエラーもなく画面に何も描かれないことがあります。

## 複数のスレッドで記録する

1 つのリストを記録できるのは、1 つのスレッドだけです。複数のスレッドで記録するならスレッドごとにリストとアロケーターを持ちます。最後に、できたリストをまとめてキューに渡します。

```cpp
// 4 つのスレッドで、シーンを 4 つに分けて記録する。
std::vector<std::thread> threads;
for (int i = 0; i < 4; ++i) {
  threads.emplace_back([&, i] {
    lists[i]->Reset(thread_allocators[i].Get(), pso.Get());
    RecordScenePart(lists[i].Get(), i);  // 各スレッドが、別のリストに記録する
    lists[i]->Close();
  });
}
for (auto& t : threads) t.join();

ID3D12CommandList* raw[] = {lists[0].Get(), lists[1].Get(), lists[2].Get(), lists[3].Get()};
command_queue->ExecuteCommandLists(4, raw);  // 配列の順に実行される
```

複数のスレッドで記録できることは D3D12 の大きな利点で、CPU がボトルネックのゲームで効果があります。

## 記録中の決まりごと

リストを `Reset` できるのは閉じたリストだけです。閉じていないリストを `Reset` すると、エラーになります。DIRECT のリストを COMPUTE のキューに渡すことはできません。また、記録中のリストが使っているアロケーターを別のリストが使うことはできません。

もう 1 つ見落としやすい決まりがあります。**記録したコマンドが参照するリソースは、GPU が実行を終えるまで生かしておく必要があります**。記録の時点で参照を覚えるだけで、GPU がそのリソースを読むのは、あとだからです。アップロード用のバッファをコピーの命令を記録したあとすぐ解放してはいけません（[Upload Buffer](upload-buffer.md)）。

## よくあるミス

??? failure "`Reset` が失敗する、またはデバッグ レイヤーが「記録中」と言う"
    `Close` していないリストを `Reset` したかアロケーターを GPU が使用中に `Reset` しました。

??? failure "設定したはずの PSO やルート シグネチャが効いていない"
    `Reset` で状態が初期化されています。`Reset` のたびにすべて設定し直します。

??? failure "`ExecuteCommandLists` でクラッシュする"
    `Close` の戻り値（`HRESULT`）を見ていません。記録中のエラーで閉じ損ねたリストを渡しています。

??? failure "描画のあとにリソースを解放してクラッシュする"
    GPU がまだそのリソースを参照する命令を実行しています。フェンスで完了を待ってから解放します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コマンド リストは、命令の記録係。呼んでも実行されない
    - [x] 流れは `Reset`、記録、`Close`、`ExecuteCommandLists`
    - [x] 状態は `Reset` のたびに設定し直す
    - [x] 記録は 1 リスト 1 スレッド。マルチスレッドはリストを分ける
    - [x] 記録したリソースは、GPU が終えるまで生かす

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md)
- [Command Queue](command-queue.md)
- [Command Allocator](command-allocator.md)
- [Fence](fence.md)
- [Microsoft Learn: ID3D12GraphicsCommandList](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12graphicscommandlist)
