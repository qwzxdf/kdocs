---
title: Resource Barrier
tags:
  - DirectX
---

# Resource Barrier

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

同じテクスチャを描き込み先（RTV）として使ったあとシェーダーで読む（SRV）。ゲームではごく普通にある流れです。ところが GPU の中では描き込み先として使っている間は、書き込みの結果がキャッシュに残っていたり圧縮された形で置かれていたりします。読む前に書き込みの完了を待ちキャッシュを書き出し、読み取り用のメモリの扱いに切り替える必要があります。

D3D11 ではこの切り替えをドライバーが自動でやっていました。D3D12 では <strong>アプリが GPU に明示します</strong>。その命令が <strong>リソース バリア</strong>です。忘れると画面が乱れたりクラッシュしたりします。D3D12 で一番バグが出やすい所のひとつです。

!!! tip "ポイント"
    - リソースは常にある「状態」（`RENDER_TARGET`、`PIXEL_SHADER_RESOURCE`、`COPY_DEST` など）にある。使い方を変える前に遷移バリアで状態を切り替える。
    - バリアは 3 種類。遷移バリアは状態の切り替え UAV バリアは同じ UAV への書き込みと読み込みの順序づけ、エイリアシング バリアはメモリを共有するリソースの切り替え。
    - バック バッファは `PRESENT` と `RENDER_TARGET` を行き来する。
    - バリアはコマンド リストに記録される。GPU が実行するときに処理される。
    - 複数のバリアは 1 回の `ResourceBarrier` でまとめて渡すほうが効率がよい。
    - デバッグ レイヤー（GPU ベース検証）が、バリアの間違いを教えてくれる。

!!! info "このページを読む前に"
    バリアはコマンド リストに記録する命令です。先に [Command List](command-list.md) を読むと流れが分かります。リソースの作り方は [Heaps and Resources](heaps-resources.md)、`ResourceBarrier` の引数は [ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md#resourcebarrier) にあります。バリアを作る小さな関数は [Helper Functions](util.md) です。

## リソースの状態

リソースは作るときに初期状態を指定し、そのあとはバリアで状態を変えます。主な状態の意味は次のとおりです。

`COMMON` と `PRESENT` は初期状態です。画面表示用の `PRESENT` は `COMMON` と同じ値です。`RENDER_TARGET` はレンダー ターゲットとして書き込む状態、`DEPTH_WRITE` は深度バッファに書き込む状態です。深度を読み取り専用でテストするだけなら `DEPTH_READ` を使います。

`PIXEL_SHADER_RESOURCE` はピクセル シェーダーで読む状態、`NON_PIXEL_SHADER_RESOURCE` は頂点シェーダーやコンピュート シェーダーで読む状態です。`UNORDERED_ACCESS` は UAV として読み書きする状態です。

`COPY_SOURCE` と `COPY_DEST` はコピーの元と先です。`VERTEX_AND_CONSTANT_BUFFER` と `INDEX_BUFFER` は頂点、定数、インデックスのバッファとして読む状態で `INDIRECT_ARGUMENT` は、間接描画の引数として読む状態です。`GENERIC_READ` は読み取り系の状態をまとめたもので、アップロード ヒープの初期状態です。

読み取り系の状態は OR で組み合わせられます。`PIXEL_SHADER_RESOURCE | NON_PIXEL_SHADER_RESOURCE` はすべてのシェーダーで読める状態です。一方、書き込み系の状態（`RENDER_TARGET`、`UNORDERED_ACCESS`、`COPY_DEST`）は単独でしか使えません。

## 遷移バリア

一番よく使うのが遷移バリアです。状態を今の状態から次の状態へ切り替えます。

```cpp
// レンダー ターゲットに描いたテクスチャを、次のパスで読む前に、状態を切り替える。
D3D12_RESOURCE_BARRIER barrier = MakeTransitionBarrier(
    scene_texture.Get(),
    D3D12_RESOURCE_STATE_RENDER_TARGET,       // 前の状態
    D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE);  // 後の状態
command_list->ResourceBarrier(1, &barrier);
```

バリアに書く内容は 4 つです。対象のリソース、前の状態（`StateBefore`）、後の状態（`StateAfter`）、そして対象のサブリソースです。サブリソースはミップ 1 枚、または配列の 1 要素を指せます。`D3D12_RESOURCE_BARRIER_ALL_SUBRESOURCES` なら全体を一度に切り替えます。

**前の状態はリソースが今実際にある状態と正確に一致していなければなりません。** 違うとデバッグ レイヤーがエラーを出します。そのため、リソースごとに「今の状態」を覚えておく仕組みを自分で持つのが一般的です。

```cpp
// 簡単な状態の追跡。リソースごとに今の状態を持ち、遷移が要るときだけバリアを入れる。
struct TrackedResource {
  ComPtr<ID3D12Resource> resource;
  D3D12_RESOURCE_STATES state = D3D12_RESOURCE_STATE_COMMON;

  void TransitionTo(ID3D12GraphicsCommandList* list, D3D12_RESOURCE_STATES next) {
    if (state == next) return;  // 同じなら何もしない
    D3D12_RESOURCE_BARRIER barrier = MakeTransitionBarrier(resource.Get(), state, next);
    list->ResourceBarrier(1, &barrier);
    state = next;
  }
};
```

## よくある遷移の流れ

バック バッファは描く前に `PRESENT` から `RENDER_TARGET` へ描いたあとに `PRESENT` へ戻します。描いたシーンの色を次のパスで読むなら `RENDER_TARGET` から `PIXEL_SHADER_RESOURCE` へ切り替えます。

G バッファはジオメトリ パスで `RENDER_TARGET` として書きライティングのパスで `PIXEL_SHADER_RESOURCE` として読み、次のフレームでまた `RENDER_TARGET` に戻します。深度バッファを AO などで読むときは、`DEPTH_WRITE` から `NON_PIXEL_SHADER_RESOURCE`（コンピュート シェーダー）または `PIXEL_SHADER_RESOURCE` へ切り替えます。

頂点バッファを作るときは `COPY_DEST` でコピーを受けたあと `VERTEX_AND_CONSTANT_BUFFER` に切り替えます。コンピュート シェーダーの出力は `UNORDERED_ACCESS` から `PIXEL_SHADER_RESOURCE` に切り替えて、次の描画で読みます。アップロード ヒープのバッファは常に `GENERIC_READ` で、遷移しません。

## UAV バリア

同じ UAV に対してコンピュート シェーダーの `Dispatch` を続けて呼びあとのほうが前の結果を読むときは、前の `Dispatch` の書き込みが終わるのを待たせる必要があります。そのためのバリアが UAV バリアです。状態は `UNORDERED_ACCESS` のまま変わりません。

```cpp
// 計算シェーダー A が書いた UAV を、計算シェーダー B が読む前に。
D3D12_RESOURCE_BARRIER uav_barrier = MakeUavBarrier(uav_resource.Get());
command_list->ResourceBarrier(1, &uav_barrier);
command_list->Dispatch(group_x, group_y, 1);  // B
```

UAV バリアがないと B が A の書き込み途中の値を読みます。FFT の段ごとの `Dispatch` やヒストグラムの集計など前の結果に依存する処理には必須です（[Compute Shader](compute-shader.md)）。

## エイリアシング バリア

同じメモリを複数のリソースで共有して使い回すときリソース A から B に切り替える合図が、エイリアシング バリアです。使わない時間が重ならない一時バッファを同じメモリに重ねて、VRAM を節約する上級の技術で使います。

```cpp
D3D12_RESOURCE_BARRIER aliasing = {};
aliasing.Type = D3D12_RESOURCE_BARRIER_TYPE_ALIASING;
aliasing.Aliasing.pResourceBefore = resource_a.Get();
aliasing.Aliasing.pResourceAfter = resource_b.Get();
command_list->ResourceBarrier(1, &aliasing);
```

`pResourceBefore` と `pResourceAfter` のどちらかを `nullptr` にすると、「すべてのリソース」を表します。

## まとめて渡す

バリアは GPU のパイプラインに待ち（フラッシュ）を起こすことがあります。1 つずつ何度も呼ぶよりまとめて 1 回で渡すほうが、待ちが減ります。

```cpp
D3D12_RESOURCE_BARRIER barriers[] = {
    MakeTransitionBarrier(gbuffer_albedo.Get(), D3D12_RESOURCE_STATE_RENDER_TARGET,
                          D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE),
    MakeTransitionBarrier(gbuffer_normal.Get(), D3D12_RESOURCE_STATE_RENDER_TARGET,
                          D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE),
    MakeTransitionBarrier(depth.Get(), D3D12_RESOURCE_STATE_DEPTH_WRITE,
                          D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE),
};
command_list->ResourceBarrier(ARRAYSIZE(barriers), barriers);
```

逆に、不要なバリアを入れすぎても性能が落ちます。同じ状態への遷移は状態の追跡で省きます。

## 分割バリアと拡張バリア

遷移の「開始」と「終了」を分けて記録できる `BEGIN_ONLY` と `END_ONLY` があります。2 つの間に別の仕事を挟むと GPU が遷移を裏で進められます。上級の最適化です。

新しいバリアの API（Enhanced Barriers、`ID3D12Device10` と `ID3D12GraphicsCommandList7`）は状態の代わりに「どの段が、どのアクセスを終えたか」で書きます。より細かく制御できますが対応した環境が必要です（[Device and Factory](factory-device.md#enhanced-barriers)）。

## 暗黙の状態遷移

特定の場面では状態が自動で変わることがあります。`COMMON` のリソースはコピーや読み取りで使うと自動で必要な状態へ昇格し、実行が終わると `COMMON` に戻ります。アップロードとリードバックのヒープは、状態が固定されていて遷移できません。

この暗黙の遷移に頼ると状態の追跡が複雑になります。明示的に遷移させるほうが安全です。

## よくあるミス

??? failure "画面が乱れる、テクスチャがちらつくときどきクラッシュする"
    バリアが足りません（書いたあと読む前に遷移していません）。または、前の状態が実際と違います。GPU ベース検証とデバッグ レイヤーで検出します。

??? failure "計算シェーダーの連続した `Dispatch` で結果が不安定になる"
    UAV バリアを入れていません。前の `Dispatch` の書き込みが終わる前に次が読んでいます。

??? failure "アップロード バッファを `COPY_DEST` に遷移しようとしてエラーになる"
    アップロード ヒープのリソースは、`GENERIC_READ` で固定されています。コピー先は DEFAULT ヒープのリソースです。

??? failure "バリアを入れすぎて遅い"
    1 つずつ毎回遷移しています。まとめて 1 回で渡します。状態の追跡で同じ状態への遷移を省きます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バリアはリソースの使い方（状態）を切り替える合図
    - [x] 遷移バリアは前の状態を正確に書く
    - [x] UAV バリアは、連続する計算シェーダーの書き込みと読み込みの順序づけ
    - [x] バック バッファは、`PRESENT` と `RENDER_TARGET` を行き来する
    - [x] まとめて渡す。リソースの状態は追跡する
    - [x] GPU ベース検証で、バリアの間違いを見つける

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md)
- [Helper Functions](util.md)
- [Swap Chain](swap-chain.md)
- [Compute Shader](compute-shader.md)
- [Debug Layer](debug-layer.md)
- [Microsoft Learn: リソース バリア](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/using-resource-barriers-to-synchronize-resource-states-in-direct3d-12)
