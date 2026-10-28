---
title: Queue and Command Enums
tags:
  - DirectX
api:
  - D3D12_COMMAND_LIST_TYPE
  - D3D12_COMMAND_QUEUE_FLAGS
  - D3D12_COMMAND_QUEUE_PRIORITY
  - D3D12_FENCE_FLAGS
  - D3D12_CLEAR_FLAGS
  - D3D12_QUERY_TYPE
  - D3D12_QUERY_HEAP_TYPE
  - D3D12_PRIMITIVE_TOPOLOGY_TYPE
  - D3D_PRIMITIVE_TOPOLOGY
---

# Queue and Command Enums

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

D3D12 の GPU への命令は、コマンド リストに記録して、コマンド キューへ渡して実行します。このとき「どの種類のリスト」「どの優先度のキュー」「どの種類のクエリ」と、種類を選ぶ場面が何度も出てきます。このページは、その選択肢をまとめた辞書です。

!!! tip "ポイント"
    - 描画のコマンド リストとキューは `DIRECT`。ふつうのゲームはこれ 1 本で足りる。
    - 計算だけを並行して走らせたいときは `COMPUTE`、コピーだけなら `COPY`。
    - `BUNDLE` はキューに直接渡せない。`DIRECT` のリストから `ExecuteBundle` で呼ぶ。
    - トポロジは 2 か所で指定する。PSO には大まかな種類（`D3D12_PRIMITIVE_TOPOLOGY_TYPE`）、コマンド リストには細かい並べ方（`D3D_PRIMITIVE_TOPOLOGY`）。

!!! info "このページを読む前に"
    キュー、アロケーター、リストの関係は [Command Queue](../command-queue.md)、[Command Allocator](../command-allocator.md)、[Command List](../command-list.md) を先に読んでください。

## D3D12_COMMAND_LIST_TYPE {#d3d12_command_list_type}

```cpp
typedef enum D3D12_COMMAND_LIST_TYPE {
  D3D12_COMMAND_LIST_TYPE_DIRECT = 0,
  D3D12_COMMAND_LIST_TYPE_BUNDLE = 1,
  D3D12_COMMAND_LIST_TYPE_COMPUTE = 2,
  D3D12_COMMAND_LIST_TYPE_COPY = 3,
  D3D12_COMMAND_LIST_TYPE_VIDEO_DECODE = 4,
  D3D12_COMMAND_LIST_TYPE_VIDEO_PROCESS = 5,
  D3D12_COMMAND_LIST_TYPE_VIDEO_ENCODE = 6,
  D3D12_COMMAND_LIST_TYPE_NONE = -1
} D3D12_COMMAND_LIST_TYPE;
```

GPU は、描画ができるエンジン、計算だけのエンジン、コピー専用のエンジンと、役割の違うエンジンを持っています。この値は、コマンド アロケーター、コマンド リスト、コマンド キューを作るときに「どのエンジン向けか」を決めます。アロケーターとリストとキューは、種類をそろえます。種類が違うリストをキューへ渡したり、アロケーターでリストを `Reset` したりすると失敗します。

#### D3D12_COMMAND_LIST_TYPE_DIRECT {#d3d12_command_list_type_direct}

値は 0 です。描画、計算、コピーのすべてを記録できる最も多機能な種類です。描画に使うキューとリストは、これを選びます。

#### D3D12_COMMAND_LIST_TYPE_BUNDLE {#d3d12_command_list_type_bundle}

値は 1 です。何度も使う短い命令の並びを前もって記録しておくための種類です。キューには直接渡さず、`DIRECT` のリストの中から `ExecuteBundle` で呼びます。ドライバーが記録の時点で最適化しやすくなる反面、使える命令に制限があり、実際のゲームで使う場面は多くありません。

#### D3D12_COMMAND_LIST_TYPE_COMPUTE {#d3d12_command_list_type_compute}

値は 2 です。`Dispatch` とコピーを記録できます。描画（`DrawInstanced` など）はできません。描画と並行して計算だけを走らせる「非同期コンピュート」を作るときに、専用のキューとセットで使います。

#### D3D12_COMMAND_LIST_TYPE_COPY {#d3d12_command_list_type_copy}

値は 3 です。コピーだけを記録できます。GPU のコピー専用エンジンを使うので、描画を止めずに、アセットの読み込みを裏で進められます。使えるのはコピー系の命令だけで、シェーダーの実行やバリアは制限されます。

#### D3D12_COMMAND_LIST_TYPE_VIDEO_DECODE {#d3d12_command_list_type_video_decode}

値は 4 です。ビデオのデコード用です。ゲームの描画では使いません。

#### D3D12_COMMAND_LIST_TYPE_VIDEO_PROCESS {#d3d12_command_list_type_video_process}

値は 5 です。ビデオの加工（拡大縮小や色変換）用です。ゲームの描画では使いません。

#### D3D12_COMMAND_LIST_TYPE_VIDEO_ENCODE {#d3d12_command_list_type_video_encode}

値は 6 です。ビデオのエンコード用です。ゲームの描画では使いません。

#### D3D12_COMMAND_LIST_TYPE_NONE {#d3d12_command_list_type_none}

値は -1 で、「種類なし」を表します。構造体の初期値として使われる値で、リストやキューを作る引数には渡せません。

## D3D12_COMMAND_QUEUE_FLAGS {#d3d12_command_queue_flags}

```cpp
typedef enum D3D12_COMMAND_QUEUE_FLAGS {
  D3D12_COMMAND_QUEUE_FLAG_NONE = 0,
  D3D12_COMMAND_QUEUE_FLAG_DISABLE_GPU_TIMEOUT = 0x1
} D3D12_COMMAND_QUEUE_FLAGS;
```

`D3D12_COMMAND_QUEUE_DESC` の `Flags` に入れる値です。

#### D3D12_COMMAND_QUEUE_FLAG_NONE {#d3d12_command_queue_flag_none}

値は 0 で、通常のキューです。ほとんどの場合これを使います。

#### D3D12_COMMAND_QUEUE_FLAG_DISABLE_GPU_TIMEOUT {#d3d12_command_queue_flag_disable_gpu_timeout}

値は 0x1 です。GPU タイムアウトの検出を無効にします。Windows は、1 つの命令が約 2 秒を超えても終わらないと、GPU のハングとみなしてデバイスをリセット（TDR）します。この指定で、その検出を止められます。長時間かかる計算を回す特殊な用途のためで、描画のキューには付けません。付けるとハングしたときに、画面が戻らなくなります。

## D3D12_COMMAND_QUEUE_PRIORITY {#d3d12_command_queue_priority}

```cpp
typedef enum D3D12_COMMAND_QUEUE_PRIORITY {
  D3D12_COMMAND_QUEUE_PRIORITY_NORMAL = 0,
  D3D12_COMMAND_QUEUE_PRIORITY_HIGH = 100,
  D3D12_COMMAND_QUEUE_PRIORITY_GLOBAL_REALTIME = 10000
} D3D12_COMMAND_QUEUE_PRIORITY;
```

`D3D12_COMMAND_QUEUE_DESC` の `Priority` に入れる値で、型は `INT` です。同じ種類のキューが複数あるとき、GPU がどちらを先に実行するかの目安になります。

#### D3D12_COMMAND_QUEUE_PRIORITY_NORMAL {#d3d12_command_queue_priority_normal}

値は 0 で、通常の優先度です。ほとんどのキューはこれです。

#### D3D12_COMMAND_QUEUE_PRIORITY_HIGH {#d3d12_command_queue_priority_high}

値は 100 で、高い優先度です。遅れると体感が悪くなる処理（VR のタイムワープなど）を別のキューで先に走らせたいときに使います。

#### D3D12_COMMAND_QUEUE_PRIORITY_GLOBAL_REALTIME {#d3d12_command_queue_priority_global_realtime}

値は 10000 で、システム全体でも最優先のキューです。使うには管理者に近い権限が必要で、失敗する場合があります。一般的なゲームでは使いません。

## D3D12_FENCE_FLAGS {#d3d12_fence_flags}

```cpp
typedef enum D3D12_FENCE_FLAGS {
  D3D12_FENCE_FLAG_NONE = 0,
  D3D12_FENCE_FLAG_SHARED = 0x1,
  D3D12_FENCE_FLAG_SHARED_CROSS_ADAPTER = 0x2,
  D3D12_FENCE_FLAG_NON_MONITORED = 0x4
} D3D12_FENCE_FLAGS;
```

`CreateFence` の引数です。

#### D3D12_FENCE_FLAG_NONE {#d3d12_fence_flag_none}

値は 0 で、そのプロセスの中だけで使う通常のフェンスです。CPU と GPU の同期は、これで足ります。

#### D3D12_FENCE_FLAG_SHARED {#d3d12_fence_flag_shared}

値は 0x1 です。別のプロセスや別の API とフェンスを共有します。共有用のハンドル（`CreateSharedHandle`）を作るときに必要です。

#### D3D12_FENCE_FLAG_SHARED_CROSS_ADAPTER {#d3d12_fence_flag_shared_cross_adapter}

値は 0x2 です。複数のアダプター（GPU）の間でフェンスを共有します。`D3D12_HEAP_FLAG_SHARED_CROSS_ADAPTER` のヒープと組にして、マルチ GPU の同期に使います。

#### D3D12_FENCE_FLAG_NON_MONITORED {#d3d12_fence_flag_non_monitored}

値は 0x4 です。フェンスを OS が監視しないようにします。Windows が行うフェンスの値の検証を省くので、特殊な用途のフェンスで使い、通常は付けません。

## D3D12_CLEAR_FLAGS {#d3d12_clear_flags}

```cpp
typedef enum D3D12_CLEAR_FLAGS {
  D3D12_CLEAR_FLAG_DEPTH = 0x1,
  D3D12_CLEAR_FLAG_STENCIL = 0x2
} D3D12_CLEAR_FLAGS;
```

`ClearDepthStencilView` の第 2 引数で、深度とステンシルのどちらをクリアするかを選びます。両方なら `|` で重ねます。0 にすると何もクリアされません。

#### D3D12_CLEAR_FLAG_DEPTH {#d3d12_clear_flag_depth}

値は 0x1 で、深度をクリアします。`Depth` 引数の値（通常 1.0f）で埋めます。毎フレームの描画の最初に呼ぶものです。

#### D3D12_CLEAR_FLAG_STENCIL {#d3d12_clear_flag_stencil}

値は 0x2 で、ステンシルをクリアします。`Stencil` 引数の値（通常 0）で埋めます。ステンシルを持たないフォーマット（`D32_FLOAT` など）に付けると、デバッグ レイヤーがエラーを出します。

## D3D12_QUERY_TYPE {#d3d12_query_type}

```cpp
typedef enum D3D12_QUERY_TYPE {
  D3D12_QUERY_TYPE_OCCLUSION = 0,
  D3D12_QUERY_TYPE_BINARY_OCCLUSION = 1,
  D3D12_QUERY_TYPE_TIMESTAMP = 2,
  D3D12_QUERY_TYPE_PIPELINE_STATISTICS = 3,
  D3D12_QUERY_TYPE_SO_STATISTICS_STREAM0 = 4,
  // ... STREAM1〜3 が 5〜7
  D3D12_QUERY_TYPE_VIDEO_DECODE_STATISTICS = 8,
  D3D12_QUERY_TYPE_PIPELINE_STATISTICS1 = 10
} D3D12_QUERY_TYPE;
```

`BeginQuery`、`EndQuery`、`ResolveQueryData` で、何を測るかを選びます。結果は `ResolveQueryData` で `READBACK` ヒープのバッファへ書き出して、CPU が読みます（[Query and Timing](../query-timing.md)）。

#### D3D12_QUERY_TYPE_OCCLUSION {#d3d12_query_type_occlusion}

値は 0 です。`BeginQuery` と `EndQuery` で挟んだ描画で、深度テストを通ったサンプル（ピクセル）の数を返します。結果は `UINT64` です。ある物体が隠れているかを調べる、オクルージョン カリングに使います。

#### D3D12_QUERY_TYPE_BINARY_OCCLUSION {#d3d12_query_type_binary_occlusion}

値は 1 です。`OCCLUSION` の簡易版で、1 つでも通ったかどうか（0 か 1）だけを返します。数を数えなくてよい分、速く、述語（`SetPredication`）で描画を自動的にスキップするのに向いています。

#### D3D12_QUERY_TYPE_TIMESTAMP {#d3d12_query_type_timestamp}

値は 2 です。`EndQuery` を呼んだ時点の GPU のタイムスタンプを返します。2 つの時刻の差を `GetTimestampFrequency` で割ると秒になります。GPU の処理時間を測る標準の方法です。`BeginQuery` は使えず、`EndQuery` だけを呼びます。

#### D3D12_QUERY_TYPE_PIPELINE_STATISTICS {#d3d12_query_type_pipeline_statistics}

値は 3 です。頂点の数、プリミティブの数、ピクセル シェーダーの呼び出し数など、パイプラインの各段の統計を `D3D12_QUERY_DATA_PIPELINE_STATISTICS` で返します。描画が重い原因を探るプロファイル用です。

#### D3D12_QUERY_TYPE_SO_STATISTICS_STREAM0 {#d3d12_query_type_so_statistics_stream0}

値は 4 です。ストリーム出力のストリーム 0 について、書き出したプリミティブ数とバッファが足りなかった数を返します。`STREAM1`〜`STREAM3`（値 5〜7）は、同じものを別のストリームについて測ります。ストリーム出力を使う場合だけ必要です。

#### D3D12_QUERY_TYPE_VIDEO_DECODE_STATISTICS {#d3d12_query_type_video_decode_statistics}

値は 8 です。ビデオ デコードの統計です。ゲームの描画では使いません。

#### D3D12_QUERY_TYPE_PIPELINE_STATISTICS1 {#d3d12_query_type_pipeline_statistics1}

値は 10 です。`PIPELINE_STATISTICS` に、メッシュ シェーダーとアンプリフィケーション シェーダーの統計を足した新しい版です。結果は `D3D12_QUERY_DATA_PIPELINE_STATISTICS1` で、`D3D12_QUERY_HEAP_TYPE_PIPELINE_STATISTICS1` のクエリ ヒープが必要です。

## D3D12_QUERY_HEAP_TYPE {#d3d12_query_heap_type}

```cpp
typedef enum D3D12_QUERY_HEAP_TYPE {
  D3D12_QUERY_HEAP_TYPE_OCCLUSION = 0,
  D3D12_QUERY_HEAP_TYPE_TIMESTAMP = 1,
  D3D12_QUERY_HEAP_TYPE_PIPELINE_STATISTICS = 2,
  D3D12_QUERY_HEAP_TYPE_SO_STATISTICS = 3,
  D3D12_QUERY_HEAP_TYPE_VIDEO_DECODE_STATISTICS = 4,
  D3D12_QUERY_HEAP_TYPE_COPY_QUEUE_TIMESTAMP = 5,
  D3D12_QUERY_HEAP_TYPE_PIPELINE_STATISTICS1 = 7
} D3D12_QUERY_HEAP_TYPE;
```

`CreateQueryHeap` で作るクエリ ヒープの種類です。ヒープの種類と、その中で使えるクエリの種類は対応しています。

#### D3D12_QUERY_HEAP_TYPE_OCCLUSION {#d3d12_query_heap_type_occlusion}

値は 0 です。`QUERY_TYPE_OCCLUSION` と `BINARY_OCCLUSION` のためのヒープです。

#### D3D12_QUERY_HEAP_TYPE_TIMESTAMP {#d3d12_query_heap_type_timestamp}

値は 1 です。`QUERY_TYPE_TIMESTAMP` のためのヒープです。GPU の処理時間を測るなら、最初に作るのはこれです。

#### D3D12_QUERY_HEAP_TYPE_PIPELINE_STATISTICS {#d3d12_query_heap_type_pipeline_statistics}

値は 2 です。`QUERY_TYPE_PIPELINE_STATISTICS` のためのヒープです。

#### D3D12_QUERY_HEAP_TYPE_SO_STATISTICS {#d3d12_query_heap_type_so_statistics}

値は 3 です。ストリーム出力の統計（`QUERY_TYPE_SO_STATISTICS_STREAM0` 〜 `STREAM3`）のためのヒープです。

#### D3D12_QUERY_HEAP_TYPE_VIDEO_DECODE_STATISTICS {#d3d12_query_heap_type_video_decode_statistics}

値は 4 です。ビデオ デコードの統計のためのヒープです。

#### D3D12_QUERY_HEAP_TYPE_COPY_QUEUE_TIMESTAMP {#d3d12_query_heap_type_copy_queue_timestamp}

値は 5 です。コピー キューのタイムスタンプのためのヒープです。コピー キューは `TIMESTAMP` ヒープを直接使えないことがあるので、専用の種類が用意されています。使えるかは `D3D12_FEATURE_D3D12_OPTIONS3` の `CopyQueueTimestampQueriesSupported` で確認します。

#### D3D12_QUERY_HEAP_TYPE_PIPELINE_STATISTICS1 {#d3d12_query_heap_type_pipeline_statistics1}

値は 7 です。`QUERY_TYPE_PIPELINE_STATISTICS1` のためのヒープです。

## D3D12_PRIMITIVE_TOPOLOGY_TYPE {#d3d12_primitive_topology_type}

```cpp
typedef enum D3D12_PRIMITIVE_TOPOLOGY_TYPE {
  D3D12_PRIMITIVE_TOPOLOGY_TYPE_UNDEFINED = 0,
  D3D12_PRIMITIVE_TOPOLOGY_TYPE_POINT = 1,
  D3D12_PRIMITIVE_TOPOLOGY_TYPE_LINE = 2,
  D3D12_PRIMITIVE_TOPOLOGY_TYPE_TRIANGLE = 3,
  D3D12_PRIMITIVE_TOPOLOGY_TYPE_PATCH = 4
} D3D12_PRIMITIVE_TOPOLOGY_TYPE;
```

`D3D12_GRAPHICS_PIPELINE_STATE_DESC` の `PrimitiveTopologyType` に入れる値です。PSO には、点・線・三角形・パッチのどの系統かだけを伝えます。ストリップかリストかのような細かい並べ方は、コマンド リストの `IASetPrimitiveTopology` で選びます。

#### D3D12_PRIMITIVE_TOPOLOGY_TYPE_UNDEFINED {#d3d12_primitive_topology_type_undefined}

値は 0 で、未指定です。この値のままだと PSO の作成が失敗します。

#### D3D12_PRIMITIVE_TOPOLOGY_TYPE_POINT {#d3d12_primitive_topology_type_point}

値は 1 で、点です。パーティクルを点で描く場合などに使い、あとで `POINTLIST` を指定します。

#### D3D12_PRIMITIVE_TOPOLOGY_TYPE_LINE {#d3d12_primitive_topology_type_line}

値は 2 で、線です。デバッグ描画の線分や枠線に使い、あとで `LINELIST` か `LINESTRIP` を指定します。

#### D3D12_PRIMITIVE_TOPOLOGY_TYPE_TRIANGLE {#d3d12_primitive_topology_type_triangle}

値は 3 で、三角形です。メッシュの描画は、ほとんどこれです。あとで `TRIANGLELIST` か `TRIANGLESTRIP` を指定します。

#### D3D12_PRIMITIVE_TOPOLOGY_TYPE_PATCH {#d3d12_primitive_topology_type_patch}

値は 4 で、テッセレーション用のパッチです。ハル シェーダーとドメイン シェーダーを使うときに指定し、あとで `n_CONTROL_POINT_PATCHLIST` を指定します。

## D3D_PRIMITIVE_TOPOLOGY {#d3d_primitive_topology}

```cpp
void ID3D12GraphicsCommandList::IASetPrimitiveTopology(
    D3D12_PRIMITIVE_TOPOLOGY PrimitiveTopology);  // D3D_PRIMITIVE_TOPOLOGY の別名
```

頂点（またはインデックス）の並びをどう図形としてつなぐかを決めます。型としては `D3D_PRIMITIVE_TOPOLOGY` を使います。`D3D12_PRIMITIVE_TOPOLOGY` はその別名です。PSO の `PrimitiveTopologyType` と食い違う組み合わせ（`TRIANGLE` の PSO に `LINELIST`）は、描画時にエラーになります。

#### D3D_PRIMITIVE_TOPOLOGY_UNDEFINED {#d3d_primitive_topology_undefined}

値は 0 で、未指定です。`IASetPrimitiveTopology` を呼び忘れると、この値のまま描画してしまい、デバッグ レイヤーが警告します。

#### D3D_PRIMITIVE_TOPOLOGY_POINTLIST {#d3d_primitive_topology_pointlist}

値は 1 です。頂点 1 つが点 1 つになります。

#### D3D_PRIMITIVE_TOPOLOGY_LINELIST {#d3d_primitive_topology_linelist}

値は 2 です。頂点 2 つで線分 1 本になります。線分同士はつながりません。デバッグ用にバラバラの線を描くときに向いています。

#### D3D_PRIMITIVE_TOPOLOGY_LINESTRIP {#d3d_primitive_topology_linestrip}

値は 3 です。頂点を順に結んで、つながった折れ線にします。N 個の頂点で N−1 本の線分ができます。

#### D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST {#d3d_primitive_topology_trianglelist}

値は 4 です。頂点 3 つで三角形 1 つになります。頂点の順序は、左手系・CW が表です。三角形同士はつながっていないので、メッシュはこれにインデックス バッファを組み合わせて、頂点を共有します。最もよく使う値です。

#### D3D_PRIMITIVE_TOPOLOGY_TRIANGLESTRIP {#d3d_primitive_topology_trianglestrip}

値は 5 です。直前の 2 頂点に 1 頂点ずつ足して、三角形を連ねます。N 個の頂点で N−2 個の三角形ができ、頂点数が少なくて済みます。ただし、三角形ごとに表裏の向きが入れ替わる決まりがあります。ストリップを途中で切るには、インデックスに特別な値（0xFFFF や 0xFFFFFFFF）を置くカット値が必要で、`D3D12_INDEX_BUFFER_STRIP_CUT_VALUE` で PSO に伝えます。

#### D3D_PRIMITIVE_TOPOLOGY_TRIANGLEFAN {#d3d_primitive_topology_trianglefan}

値は 6 です。D3D11 までにあった三角形ファンの値ですが、D3D12 では使えません。ヘッダーには定義がありますが、指定すると描画に失敗します。

#### D3D_PRIMITIVE_TOPOLOGY_LINELIST_ADJ {#d3d_primitive_topology_linelist_adj}

値は 10 です。隣接情報つきの線分リストで、ジオメトリ シェーダーが前後の頂点を参照するために使います。

#### D3D_PRIMITIVE_TOPOLOGY_LINESTRIP_ADJ {#d3d_primitive_topology_linestrip_adj}

値は 11 です。隣接情報つきの折れ線です。ジオメトリ シェーダー用です。

#### D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST_ADJ {#d3d_primitive_topology_trianglelist_adj}

値は 12 です。隣接情報つきの三角形リストで、1 つの三角形に 6 頂点を使います。ジオメトリ シェーダーで輪郭線（シルエット）を抽出するときなどに使います。

#### D3D_PRIMITIVE_TOPOLOGY_TRIANGLESTRIP_ADJ {#d3d_primitive_topology_trianglestrip_adj}

値は 13 です。隣接情報つきの三角形ストリップです。ジオメトリ シェーダー用です。

#### D3D_PRIMITIVE_TOPOLOGY_3_CONTROL_POINT_PATCHLIST {#d3d_primitive_topology_3_control_point_patchlist}

テッセレーション用のパッチで、制御点が 3 つです。三角形のパッチを細かく分割するときに使います。同じ並びで `1_CONTROL_POINT_PATCHLIST` から `32_CONTROL_POINT_PATCHLIST` まで、制御点の数だけ値が用意されています。PSO 側は `D3D12_PRIMITIVE_TOPOLOGY_TYPE_PATCH` にします。

#### D3D_PRIMITIVE_TOPOLOGY_4_CONTROL_POINT_PATCHLIST {#d3d_primitive_topology_4_control_point_patchlist}

制御点が 4 つのパッチです。四角形のパッチ（地形をタイルごとに細分化するときなど）に使います。

## よくあるミス

??? failure "リストとキューの種類が合っていない"
    `COPY` のリストを `DIRECT` のアロケーターで `Reset` する、`COMPUTE` のリストに `DrawInstanced` を記録する、といった食い違いは、リストの作成や `Close`、`ExecuteCommandLists` で失敗します。作るときに 3 つの種類をそろえます。

??? failure "PSO のトポロジ タイプと IASetPrimitiveTopology が合っていない"
    PSO を `TRIANGLE` で作ったのに `LINELIST` を設定して描く、という組み合わせはデバッグ レイヤーがエラーにします。PSO が持つのは系統だけで、細かい並べ方は描画の直前に決めます。

??? failure "IASetPrimitiveTopology を呼び忘れた"
    D3D12 のコマンド リストは、`Reset` のたびに状態が白紙に戻ります。トポロジを一度設定したから大丈夫、とはなりません。

## 関連ページ

- [Command Queue](../command-queue.md)
- [Command List](../command-list.md)
- [Fence](../fence.md)
- [Query and Timing](../query-timing.md)
- [PSO](../pso.md)
