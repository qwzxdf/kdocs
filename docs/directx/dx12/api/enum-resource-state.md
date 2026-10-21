---
title: Resource State Enums
tags:
  - DirectX
api:
  - D3D12_RESOURCE_STATES
  - D3D12_RESOURCE_BARRIER_TYPE
  - D3D12_RESOURCE_BARRIER_FLAGS
---

# Resource State Enums

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

D3D12 の GPU は、リソースが今どう使われているかを自分では追いかけません。「いまこのテクスチャは描き込み先なのか、シェーダーが読む物なのか」をプログラムが `ResourceBarrier` で伝える決まりです。伝える言葉が `D3D12_RESOURCE_STATES` で、バリアの種類を選ぶのが `D3D12_RESOURCE_BARRIER_TYPE`、遷移を前半と後半に分けるのが `D3D12_RESOURCE_BARRIER_FLAGS` です。

状態の書き間違いはデバッグ レイヤーが一番よく指摘するエラーです。値の意味を 1 つずつ知っておくと、メッセージの読み方が変わります。

!!! tip "ポイント"
    - 書き込みの状態（`RENDER_TARGET`、`DEPTH_WRITE`、`UNORDERED_ACCESS`、`COPY_DEST` など）は、同時に 1 つだけ。ほかの状態とは OR できない。
    - 読み取りの状態は OR で重ねられる（`GENERIC_READ` はその詰め合わせ）。
    - `COMMON` と `PRESENT` はどちらも 0。スワップ チェーンのバックバッファは `COMMON` から始まる。
    - `UPLOAD` ヒープのリソースは `GENERIC_READ` のまま、`READBACK` ヒープのリソースは `COPY_DEST` のまま変えられない。

!!! info "このページを読む前に"
    バリアを置く流れは [Resource Barrier](../resource-barrier.md)、`ResourceBarrier` メソッドの引数は [ID3D12GraphicsCommandList](id3d12graphicscommandlist.md#resourcebarrier) を先に読んでください。リソースの作り方は [Heaps and Resources](../heaps-resources.md) にあります。

## D3D12_RESOURCE_STATES {#d3d12_resource_states}

```cpp
typedef enum D3D12_RESOURCE_STATES {
  D3D12_RESOURCE_STATE_COMMON = 0,
  D3D12_RESOURCE_STATE_VERTEX_AND_CONSTANT_BUFFER = 0x1,
  // ... 以下、各値の節
} D3D12_RESOURCE_STATES;
```

リソースの現在の使い方を表すフラグです。`CreateCommittedResource` の初期状態、`ResourceBarrier` の `StateBefore` と `StateAfter`、バッファの `UPLOAD` ヒープでの制約など、状態を書く場所はすべてこの型を使います。

値は大きく 2 つに分かれます。読み取りだけの状態（`VERTEX_AND_CONSTANT_BUFFER`、`INDEX_BUFFER`、`NON_PIXEL_SHADER_RESOURCE`、`PIXEL_SHADER_RESOURCE`、`INDIRECT_ARGUMENT`、`COPY_SOURCE`、`DEPTH_READ`、`RESOLVE_SOURCE` など）は、`|` でいくつでも重ねられます。書き込みを伴う状態（`RENDER_TARGET`、`UNORDERED_ACCESS`、`DEPTH_WRITE`、`STREAM_OUT`、`COPY_DEST`、`RESOLVE_DEST`）は、そのうち 1 つだけを単独で指定します。書き込みの状態に読み取りの状態を足すと、デバッグ レイヤーがエラーにします。

状態の遷移は「リソースごと」ではなく「サブリソースごと」です。ミップマップや配列スライスの一部だけを別の状態にもできますが、通常は `D3D12_RESOURCE_BARRIER_ALL_SUBRESOURCES` で全体を一度に切り替えます。

#### 暗黙の昇格と減衰

バリアを書かなくてよい場面が 2 つあります。

1 つ目は昇格です。`COMMON` 状態のバッファと、`ALLOW_SIMULTANEOUS_ACCESS` を付けたテクスチャは、GPU が最初に使った時点でその使い方の状態に自動で変わります。昇格できる先は、頂点・定数、インデックス、レンダー ターゲット、UAV、非ピクセル・ピクセルのシェーダー リソース、ストリーム出力、間接引数、コピー先、コピー元、リゾルブ、述語です。ふつうのテクスチャ（同時アクセスなし）は、シェーダー リソース（2 種類）、`COPY_DEST`、`COPY_SOURCE` にしか昇格できません。深度ステンシルは昇格できません。

2 つ目は減衰です。次の資源は、`ExecuteCommandLists` が GPU で終わると `COMMON` に戻ります。コピー キューで使った資源、すべてのバッファ、`ALLOW_SIMULTANEOUS_ACCESS` 付きのテクスチャ、読み取り状態へ昇格した資源です。同じ `ExecuteCommandLists` に渡した複数のコマンド リストの間では減衰しません。

つまり、頂点バッファのコピーのように「使うたびに `COMMON` から始まる」バッファでは、バリアを省いたほうが速く、正しく動きます。逆にバッファを毎回 `COMMON` へ戻すバリアを入れると、不要な同期になります。

#### D3D12_RESOURCE_STATE_COMMON {#d3d12_resource_state_common}

値は 0 です。「どの使い方にも固定されていない状態」で、リソースを作るときの初期状態として一番無難です。バッファとテクスチャの昇格はこの状態から起こります。

スワップ チェーンのバックバッファは、作られた時点でこの状態にあります。また複数のキュー（たとえば描画キューとコピー キュー）の間でリソースを受け渡すときは、いったん `COMMON` に戻してから渡すのが決まりです。コピー キューで使う資源は、`COMMON` から始まります。

#### D3D12_RESOURCE_STATE_PRESENT {#d3d12_resource_state_present}

値は `COMMON` と同じ 0 で、名前だけが違います。画面に出す直前のバックバッファに使います。`Present` を呼ぶ時点でバックバッファがこの状態でないと、デバッグ レイヤーが警告を出します。

描画を終えた `RENDER_TARGET` から `PRESENT` へのバリアは、毎フレームの最後に必ず入れるものです。入れ忘れても動く環境は多いのですが、バリアが必要な GPU では画面が乱れます。

#### D3D12_RESOURCE_STATE_VERTEX_AND_CONSTANT_BUFFER {#d3d12_resource_state_vertex_and_constant_buffer}

値は 0x1 です。頂点バッファと定数バッファとして読む状態を、1 つの値にまとめています。読み取り専用なので、ほかの読み取り状態と OR できます。

`DEFAULT` ヒープに置いた頂点バッファは、コピーが終わったあとにこの状態へ遷移させます。定数バッファ ビュー（CBV）で読むバッファもこの状態です。ただし定数バッファを `UPLOAD` ヒープに置いているなら、そもそも `GENERIC_READ` のまま変えないので、この値は出番がありません。

#### D3D12_RESOURCE_STATE_INDEX_BUFFER {#d3d12_resource_state_index_buffer}

値は 0x2 です。インデックス バッファとして読む状態です。頂点バッファの状態とは別の値なので、バッファを両方に使うなら `VERTEX_AND_CONSTANT_BUFFER | INDEX_BUFFER` と OR します。1 つのバッファに頂点とインデックスを同居させる場合に必要になります。

#### D3D12_RESOURCE_STATE_RENDER_TARGET {#d3d12_resource_state_render_target}

値は 0x4 です。レンダー ターゲットとして描き込む状態で、書き込み側の状態です。`OMSetRenderTargets` に渡す前、`ClearRenderTargetView` を呼ぶ前に、リソースはこの状態になっていなければなりません。

バックバッファなら `PRESENT` から入り、描き終えたら `PRESENT` へ戻します。シャドウやポストプロセスの中間テクスチャは、描き込むときにこの状態、次のパスで読むときに `PIXEL_SHADER_RESOURCE` へ遷移させます。作成時にこの状態を初期状態にすると、最初のパスでバリアが要りません。

#### D3D12_RESOURCE_STATE_UNORDERED_ACCESS {#d3d12_resource_state_unordered_access}

値は 0x8 です。UAV として読み書きする状態です。コンピュート シェーダーの出力先や、ピクセル シェーダーからの `RWTexture2D` 書き込みに使います。リソースには `D3D12_RESOURCE_FLAG_ALLOW_UNORDERED_ACCESS` が必要です。

この状態のまま、同じリソースへの読み書きの順序を保証するには、`UAV` バリア（`D3D12_RESOURCE_BARRIER_TYPE_UAV`）を挟みます。状態の遷移とは別の話で、同じ状態のままでも書き込み同士の完了を待たせたいときに使います。

#### D3D12_RESOURCE_STATE_DEPTH_WRITE {#d3d12_resource_state_depth_write}

値は 0x10 です。深度ステンシルとして書き込める状態です。深度テストをして書き込む通常の描画は、この状態にします。`ClearDepthStencilView` を呼ぶときもこの状態です。

深度ステンシルは昇格できないので、バッファの作成時にこの状態を初期状態にしておくのが一般的です。

#### D3D12_RESOURCE_STATE_DEPTH_READ {#d3d12_resource_state_depth_read}

値は 0x20 です。深度ステンシルを読み取り専用で使う状態です。深度は読むだけで書かない描画（半透明の描画など）に使います。DSV 側で `D3D12_DSV_FLAG_READ_ONLY_DEPTH` を指定したビューと組にして、同じ深度バッファをシェーダーから読むこともできます。その場合は `DEPTH_READ | PIXEL_SHADER_RESOURCE` のように OR します。

#### D3D12_RESOURCE_STATE_NON_PIXEL_SHADER_RESOURCE {#d3d12_resource_state_non_pixel_shader_resource}

値は 0x40 です。ピクセル シェーダー以外のシェーダー（頂点、ジオメトリ、ハル、ドメイン、コンピュート、メッシュ）が SRV として読む状態です。コンピュート シェーダーだけが読む入力テクスチャは、この状態にします。

ピクセル シェーダーでも使うなら次の値と OR して、`ALL_SHADER_RESOURCE` を使います。

#### D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE {#d3d12_resource_state_pixel_shader_resource}

値は 0x80 です。ピクセル シェーダーが SRV として読む状態で、通常のテクスチャが描画中に取る状態です。コピーで中身を入れ終えたテクスチャは、`COPY_DEST` からこの状態へ遷移させます。

ピクセル シェーダーとそれ以外で読む場合の区別は、GPU が読み取りキャッシュを別々に持っているために存在します。不安なときは両方を OR した `ALL_SHADER_RESOURCE` にしておけば、どのシェーダーからも読めます。

#### D3D12_RESOURCE_STATE_STREAM_OUT {#d3d12_resource_state_stream_out}

値は 0x100 です。ストリーム出力（ジオメトリ シェーダーの結果をバッファに書き出す機能）のターゲットにする状態です。メッシュ シェーダーやコンピュート シェーダーが主流になった今、ゲームではほとんど使いません。

#### D3D12_RESOURCE_STATE_INDIRECT_ARGUMENT {#d3d12_resource_state_indirect_argument}

値は 0x200 です。`ExecuteIndirect` の引数バッファとして読む状態です。GPU が計算した描画回数（GPU カリングの結果など）を、そのまま描画コマンドへ渡すときに使います。述語（`SetPredication`）の値として読む状態も、同じ値 0x200 で、`D3D12_RESOURCE_STATE_PREDICATION` という別名が付いています。

#### D3D12_RESOURCE_STATE_COPY_DEST {#d3d12_resource_state_copy_dest}

値は 0x400 です。コピーの書き込み先になる状態です。`CopyBufferRegion`、`CopyTextureRegion`、`CopyResource` の宛先は、すべてこの状態でなければなりません。

テクスチャや `DEFAULT` ヒープのバッファは、`COPY_DEST` で作ってコピーを記録し、終わったらシェーダーが読む状態へ遷移させる、が定番の流れです。`READBACK` ヒープのリソースは、この状態から変えられません。`UPLOAD` ヒープのリソースにこの状態を指定すると、作成が失敗します。

#### D3D12_RESOURCE_STATE_COPY_SOURCE {#d3d12_resource_state_copy_source}

値は 0x800 です。コピーの読み取り元になる状態です。読み取り状態なので、ほかの読み取りと OR できます。`UPLOAD` ヒープのリソースは `GENERIC_READ` に含まれているので、コピー元にそのまま使えます。

画面をキャプチャするときは、バックバッファを `PRESENT` から `COPY_SOURCE` へ遷移させて、`READBACK` のバッファへコピーします。

#### D3D12_RESOURCE_STATE_RESOLVE_DEST {#d3d12_resource_state_resolve_dest}

値は 0x1000 です。MSAA のリゾルブ（`ResolveSubresource`）で、結果を受け取る側の状態です。リゾルブ先は 1 サンプルの通常のテクスチャです。

#### D3D12_RESOURCE_STATE_RESOLVE_SOURCE {#d3d12_resource_state_resolve_source}

値は 0x2000 です。MSAA のリゾルブで、複数サンプルの元になる側の状態です。MSAA のレンダー ターゲットは、描き終えたらこの状態へ遷移させて、リゾルブ先のバックバッファの `RESOLVE_DEST` へ書き出します。

#### D3D12_RESOURCE_STATE_RAYTRACING_ACCELERATION_STRUCTURE {#d3d12_resource_state_raytracing_acceleration_structure}

値は 0x400000 です。DXR の加速構造（BLAS・TLAS）を、レイ トレーシングのシェーダーが読む状態です。`D3D12_HEAP_TYPE_DEFAULT` に作る加速構造のバッファは、作成時から `D3D12_RESOURCE_FLAG_RAYTRACING_ACCELERATION_STRUCTURE` を付けて、この状態で作ります。ビルド中は `UNORDERED_ACCESS` ではなくこの状態のままで構いません。ビルド同士の順序は UAV バリアで保ちます。

#### D3D12_RESOURCE_STATE_SHADING_RATE_SOURCE {#d3d12_resource_state_shading_rate_source}

値は 0x1000000 です。可変レートシェーディング（VRS）のシェーディング レート イメージとして読む状態です。`RSSetShadingRateImage` で使うテクスチャは、この状態にします。

#### D3D12_RESOURCE_STATE_GENERIC_READ {#d3d12_resource_state_generic_read}

読み取り状態の詰め合わせです。中身は `VERTEX_AND_CONSTANT_BUFFER | INDEX_BUFFER | NON_PIXEL_SHADER_RESOURCE | PIXEL_SHADER_RESOURCE | INDIRECT_ARGUMENT | COPY_SOURCE`（ヘッダーでは 0x1 | 0x2 | 0x40 | 0x80 | 0x200 | 0x800）です。

`UPLOAD` ヒープのリソースは、CPU が書く専用なので、GPU から見ると読み取りしかしません。そのため作成時にこの状態を指定する決まりで、あとから変えられません。これ以外の値を渡すと、`CreateCommittedResource` が失敗します。

#### D3D12_RESOURCE_STATE_ALL_SHADER_RESOURCE {#d3d12_resource_state_all_shader_resource}

`NON_PIXEL_SHADER_RESOURCE | PIXEL_SHADER_RESOURCE`（0x40 | 0x80）の別名です。どのシェーダー ステージからも SRV で読めるようにします。迷ったらこれを選べば間違いありませんが、`NON_PIXEL` 側を読まないことが分かっているなら `PIXEL_SHADER_RESOURCE` だけのほうが、ドライバーが余計な同期をしないで済みます。

#### D3D12_RESOURCE_STATE_PREDICATION {#d3d12_resource_state_predication}

`INDIRECT_ARGUMENT` と同じ 0x200 の別名です。`SetPredication` が参照する述語バッファの状態を表すときに、読みやすくするために使います。

#### ビデオ関連の値

`D3D12_RESOURCE_STATE_VIDEO_DECODE_READ`（0x10000）、`VIDEO_DECODE_WRITE`（0x20000）、`VIDEO_PROCESS_READ`（0x40000）、`VIDEO_PROCESS_WRITE`（0x80000）、`VIDEO_ENCODE_READ`（0x200000）、`VIDEO_ENCODE_WRITE`（0x800000）は、D3D12 のビデオ デコード、処理、エンコード用です。ゲームの描画では使いません。`RESERVED_INTERNAL_*` で始まる値はシステムが使う予約です。

## D3D12_RESOURCE_BARRIER_TYPE {#d3d12_resource_barrier_type}

```cpp
typedef enum D3D12_RESOURCE_BARRIER_TYPE {
  D3D12_RESOURCE_BARRIER_TYPE_TRANSITION = 0,
  D3D12_RESOURCE_BARRIER_TYPE_ALIASING = 1,
  D3D12_RESOURCE_BARRIER_TYPE_UAV = 2
} D3D12_RESOURCE_BARRIER_TYPE;
```

`D3D12_RESOURCE_BARRIER` 構造体は、この値で共用体の中身（`Transition`、`Aliasing`、`UAV`）を切り替えます。型を `TRANSITION` にしながら `UAV` のメンバーに値を入れる、という食い違いは気づきにくいミスです。

#### D3D12_RESOURCE_BARRIER_TYPE_TRANSITION {#d3d12_resource_barrier_type_transition}

値は 0 で、構造体を `{}` で 0 初期化したときの既定の種類でもあります。リソースの状態を `StateBefore` から `StateAfter` に変えます。ほとんどのバリアはこれです。

`StateBefore` は、そのサブリソースが今実際にある状態と一致していなければなりません。食い違うとデバッグ レイヤーがエラーを出し、実行時には GPU のハングや描画の乱れにつながります。1 度に複数の遷移を渡せるので、まとめて 1 回の `ResourceBarrier` で呼ぶと速くなります。

#### D3D12_RESOURCE_BARRIER_TYPE_ALIASING {#d3d12_resource_barrier_type_aliasing}

値は 1 です。同じヒープの同じ範囲に重ねて置いた 2 つのリソース（`CreatePlacedResource` で作ったもの）の、使う側を切り替えるときに入れます。`pResourceBefore` が今まで使っていた側、`pResourceAfter` がこれから使う側です。どちらかを `nullptr` にすると、「重なっているすべてのリソース」の意味になります。

切り替え後のリソースの中身は未定義です。レンダー ターゲットや深度バッファなら、使う前にクリアか `DiscardResource` が必要です。

#### D3D12_RESOURCE_BARRIER_TYPE_UAV {#d3d12_resource_barrier_type_uav}

値は 2 です。UAV への書き込みが終わるまで、後続の同じ UAV へのアクセスを待たせます。状態は変わりません。コンピュート シェーダーを 2 回続けて呼び、2 回目が 1 回目の結果を読むなら、その間にこのバリアを入れます。

`pResource` に `nullptr` を渡すと「すべての UAV」になりますが、必要以上に待たせるので、リソースが分かっているなら指定します。読み取りだけの 2 回の間や、同じ UAV に書き込み順が結果に影響しない書き込みをする間には要りません。

## D3D12_RESOURCE_BARRIER_FLAGS {#d3d12_resource_barrier_flags}

```cpp
typedef enum D3D12_RESOURCE_BARRIER_FLAGS {
  D3D12_RESOURCE_BARRIER_FLAG_NONE = 0,
  D3D12_RESOURCE_BARRIER_FLAG_BEGIN_ONLY = 0x1,
  D3D12_RESOURCE_BARRIER_FLAG_END_ONLY = 0x2
} D3D12_RESOURCE_BARRIER_FLAGS;
```

遷移バリアを「分割バリア」にするためのフラグです。リソースを使い終わった時点で遷移の開始を宣言し、次に使う直前で完了を宣言すると、GPU はその間に遷移の仕事を進められます。間に別の描画やコンピュートを挟めるときに効きます。

#### D3D12_RESOURCE_BARRIER_FLAG_NONE {#d3d12_resource_barrier_flag_none}

値は 0 です。普通のバリアで、その場で遷移が完了します。ほとんどの場合これを使います。

#### D3D12_RESOURCE_BARRIER_FLAG_BEGIN_ONLY {#d3d12_resource_barrier_flag_begin_only}

値は 0x1 です。遷移の開始だけを宣言します。この時点から `END_ONLY` が来るまでは、そのサブリソースは「遷移中」で、GPU は読むことも書くこともできません。許されるバリアは、同じ `StateBefore` と `StateAfter` で `END_ONLY` を付けた完了だけです。

#### D3D12_RESOURCE_BARRIER_FLAG_END_ONLY {#d3d12_resource_barrier_flag_end_only}

値は 0x2 です。`BEGIN_ONLY` で始めた遷移を完了させます。この呼び出しのあとから、リソースを `StateAfter` として使えます。`BEGIN_ONLY` と対にせず単独で使うと、デバッグ レイヤーがエラーにします。

分割バリアの効果はドライバー次第で、あまり差が出ない GPU もあります。まず普通のバリアで正しく動かして、計測してから分割を試すのが順序です。

## よくあるミス

??? failure "StateBefore が実際の状態と違う"
    `COPY_DEST` から `PIXEL_SHADER_RESOURCE` へ遷移させるつもりで、書き込み側の初期状態を `COMMON` で作っていた、という形が多いです。作成時の状態と、最初のバリアの `StateBefore` を同じにします。デバッグ レイヤーは `D3D12 ERROR: ... Before state (0x...) of resource ... doesn't match with the state (0x...) specified in the previous call` と出します。

??? failure "書き込みの状態と読み取りの状態を OR した"
    `RENDER_TARGET | PIXEL_SHADER_RESOURCE` のような値は、同時には成り立ちません。同じテクスチャへ描きながら読むことはできないので、パスを分けて遷移させます。

??? failure "UPLOAD ヒープのリソースにバリアを入れた"
    `UPLOAD` のリソースは `GENERIC_READ` で固定です。`COPY_DEST` などへ遷移させようとすると、エラーになります。CPU が `Map` で書き、GPU はそのまま読みます。

## 関連ページ

- [Resource Barrier](../resource-barrier.md)
- [ID3D12GraphicsCommandList](id3d12graphicscommandlist.md)
- [ID3D12Device](id3d12device.md#createcommittedresource)
