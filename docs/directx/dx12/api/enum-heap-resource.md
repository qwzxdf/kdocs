---
title: Heap and Resource Enums
tags:
  - DirectX
api:
  - D3D12_HEAP_TYPE
  - D3D12_HEAP_FLAGS
  - D3D12_CPU_PAGE_PROPERTY
  - D3D12_MEMORY_POOL
  - D3D12_RESOURCE_DIMENSION
  - D3D12_TEXTURE_LAYOUT
  - D3D12_RESOURCE_FLAGS
  - D3D12_TEXTURE_COPY_TYPE
---

# Heap and Resource Enums

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

バッファやテクスチャを作るとき、D3D12 では「どのメモリに置くか」「何として使うか」を自分で決めます。メモリの置き場を選ぶのが `D3D12_HEAP_TYPE` とそれを細かくした `D3D12_CPU_PAGE_PROPERTY`、`D3D12_MEMORY_POOL`、ヒープの性質を決めるのが `D3D12_HEAP_FLAGS` です。リソース側は、種類（`D3D12_RESOURCE_DIMENSION`）、メモリ上の並び（`D3D12_TEXTURE_LAYOUT`）、使い方の許可（`D3D12_RESOURCE_FLAGS`）を指定します。コピーの端点の指し方には `D3D12_TEXTURE_COPY_TYPE` が出てきます。

!!! tip "ポイント"
    - ふつうは `DEFAULT`（GPU 専用）、`UPLOAD`（CPU から GPU へ）、`READBACK`（GPU から CPU へ）の 3 つだけを使う。
    - `D3D12_HEAP_FLAG_NONE` と `D3D12_RESOURCE_FLAG_NONE` は 0 で、迷ったら使う既定値。
    - レンダー ターゲット、深度、UAV は、使う前にリソース フラグで許可しておく。許可がないと、ビューを作る時点で失敗する。
    - `CUSTOM` ヒープは `CPU_PAGE_PROPERTY` と `MEMORY_POOL` を自分で組み合わせる上級者向け。

!!! info "このページを読む前に"
    リソースとヒープの関係は [Heaps and Resources](../heaps-resources.md)、作るメソッドは [ID3D12Device](id3d12device.md#createcommittedresource) を先に読んでください。

## D3D12_HEAP_TYPE {#d3d12_heap_type}

```cpp
typedef enum D3D12_HEAP_TYPE {
  D3D12_HEAP_TYPE_DEFAULT = 1,
  D3D12_HEAP_TYPE_UPLOAD = 2,
  D3D12_HEAP_TYPE_READBACK = 3,
  D3D12_HEAP_TYPE_CUSTOM = 4,
  D3D12_HEAP_TYPE_GPU_UPLOAD = 5
} D3D12_HEAP_TYPE;
```

0 の値は無く、`D3D12_HEAP_PROPERTIES` を 0 初期化したまま使うと不正な値になります。メモリの特徴は GPU ごとに違うので、API は「CPU がどう触るか」を基準に 3 つの型を用意しています。型を選べば、メモリの種類（VRAM かシステム メモリか）は実装が決めます。

#### D3D12_HEAP_TYPE_DEFAULT {#d3d12_heap_type_default}

GPU が最も速く読み書きできるメモリです。専用 VRAM を持つ GPU では VRAM、内蔵 GPU ではその GPU が速く扱える領域に置かれます。代わりに CPU からは `Map` できません。

メッシュ、テクスチャ、レンダー ターゲット、深度バッファなど、ゲームのリソースの大半はここに置きます。中身を入れるには、`UPLOAD` ヒープのバッファに CPU が書いて、コピー コマンドで移します。

#### D3D12_HEAP_TYPE_UPLOAD {#d3d12_heap_type_upload}

CPU が書いて GPU が読む用のメモリです。CPU から `Map` して直接書き込めます。CPU の書き込みはライト コンバインのメモリに対して行われるので、書くのは速い一方で、CPU から読み返すと遅くなります。読み返さず、先頭から順に書く使い方にします。

GPU から見ると読み取り専用で、初期状態は必ず `D3D12_RESOURCE_STATE_GENERIC_READ` です。置けるのはバッファです（テクスチャは直接置けません）。毎フレーム変わる定数バッファや、アップロード用の一時バッファに使います。

#### D3D12_HEAP_TYPE_READBACK {#d3d12_heap_type_readback}

GPU が書いて CPU が読む用のメモリです。GPU が計算した結果を CPU で受け取る場合（画面キャプチャ、オクルージョン クエリの結果、タイムスタンプ クエリの解決）に使います。CPU のキャッシュ付きで読めるので、読み取りが速いのが特徴です。

初期状態は必ず `D3D12_RESOURCE_STATE_COPY_DEST` で、あとから変えられません。置けるのはバッファだけです。

#### D3D12_HEAP_TYPE_CUSTOM {#d3d12_heap_type_custom}

`CPUPageProperty` と `MemoryPoolPreference` を自分で組み合わせるヒープです。特定のアーキテクチャで、CPU と GPU が同じメモリを共有できる環境（内蔵 GPU）を最大限に活かすときに使います。先に `D3D12_FEATURE_ARCHITECTURE` で、CPU と GPU がメモリを共有する構成（UMA）かどうかを調べておく必要があります。移植性が下がるので、入門では使いません。

#### D3D12_HEAP_TYPE_GPU_UPLOAD {#d3d12_heap_type_gpu_upload}

CPU から直接書けて、GPU からも VRAM と同じくらい速く読めるヒープです。Resizable BAR（CPU が VRAM 全体を覗ける機能）が使える環境で、CPU が書いたデータをアップロードのコピーを挟まずに GPU が読めます。比較的新しい種類で、使える Agility SDK と GPU が限られます。`D3D12_FEATURE_D3D12_OPTIONS16` の `GPUUploadHeapSupported` で確認してから使います。対応していなければ `UPLOAD` と `DEFAULT` の組み合わせに戻します。

## D3D12_CPU_PAGE_PROPERTY {#d3d12_cpu_page_property}

```cpp
typedef enum D3D12_CPU_PAGE_PROPERTY {
  D3D12_CPU_PAGE_PROPERTY_UNKNOWN = 0,
  D3D12_CPU_PAGE_PROPERTY_NOT_AVAILABLE = 1,
  D3D12_CPU_PAGE_PROPERTY_WRITE_COMBINE = 2,
  D3D12_CPU_PAGE_PROPERTY_WRITE_BACK = 3
} D3D12_CPU_PAGE_PROPERTY;
```

`D3D12_HEAP_PROPERTIES` の `CPUPageProperty` に入れる値で、CPU がそのメモリをどう扱えるかを表します。`CUSTOM` 以外のヒープ型では必ず `UNKNOWN` にします。

#### D3D12_CPU_PAGE_PROPERTY_UNKNOWN {#d3d12_cpu_page_property_unknown}

`DEFAULT`、`UPLOAD`、`READBACK` のときに指定する値で、「ヒープの型から決まる」という意味です。ふつうはこれだけ使います。`CUSTOM` で指定すると失敗します。

#### D3D12_CPU_PAGE_PROPERTY_NOT_AVAILABLE {#d3d12_cpu_page_property_not_available}

CPU からアクセスできないメモリです。`Map` はできません。`DEFAULT` ヒープに相当する `CUSTOM` ヒープで使います。

#### D3D12_CPU_PAGE_PROPERTY_WRITE_COMBINE {#d3d12_cpu_page_property_write_combine}

CPU の書き込みをまとめて送る（ライト コンバイン）メモリです。書き込みは速く、読み出しは遅くなります。`UPLOAD` と同じ性質です。

#### D3D12_CPU_PAGE_PROPERTY_WRITE_BACK {#d3d12_cpu_page_property_write_back}

CPU のキャッシュを通常どおり使うメモリです。CPU から読むのも速いので、`READBACK` と同じ性質です。

## D3D12_MEMORY_POOL {#d3d12_memory_pool}

```cpp
typedef enum D3D12_MEMORY_POOL {
  D3D12_MEMORY_POOL_UNKNOWN = 0,
  D3D12_MEMORY_POOL_L0 = 1,
  D3D12_MEMORY_POOL_L1 = 2
} D3D12_MEMORY_POOL;
```

`D3D12_HEAP_PROPERTIES` の `MemoryPoolPreference` に入れる値で、どのメモリの池に置くかを表します。`CUSTOM` 以外では `UNKNOWN` にします。

#### D3D12_MEMORY_POOL_UNKNOWN {#d3d12_memory_pool_unknown}

型から池が決まるときの値です。`DEFAULT`、`UPLOAD`、`READBACK` では、これを指定します。

#### D3D12_MEMORY_POOL_L0 {#d3d12_memory_pool_l0}

システム メモリ（CPU 側の RAM）です。専用 VRAM を持つ GPU では、GPU からは PCIe 越しになり遅く、CPU からは速いメモリです。内蔵 GPU では、CPU と共有する唯一のメモリです。

#### D3D12_MEMORY_POOL_L1 {#d3d12_memory_pool_l1}

GPU 専用のメモリ（VRAM）です。専用 VRAM を持つ GPU にだけあります。CPU からは触れないので、組み合わせる `CPUPageProperty` は `NOT_AVAILABLE` にします。内蔵 GPU には存在しません。

## D3D12_HEAP_FLAGS {#d3d12_heap_flags}

```cpp
typedef enum D3D12_HEAP_FLAGS {
  D3D12_HEAP_FLAG_NONE = 0,
  D3D12_HEAP_FLAG_SHARED = 0x1,
  D3D12_HEAP_FLAG_DENY_BUFFERS = 0x4,
  // ... 以下、各値の節
} D3D12_HEAP_FLAGS;
```

ヒープの性質を決めるフラグで、`|` で組み合わせます。`CreateCommittedResource` では引数に `CreateHeap` では `D3D12_HEAP_DESC` のメンバーとして渡します。フラグのうち、ゲームでふつうに使うのは `NONE` と、`CreateHeap` で置ける物を限定する 3 つです。

#### D3D12_HEAP_FLAG_NONE {#d3d12_heap_flag_none}

値は 0 で、特別な性質を求めません。`CreateCommittedResource` では、この値を渡せば足ります。

#### D3D12_HEAP_FLAG_SHARED {#d3d12_heap_flag_shared}

値は 0x1 です。別のプロセスや、D3D11 などの別の API とヒープを共有できるようにします。共有ハンドル（`CreateSharedHandle`）を作るときに必要です。

#### D3D12_HEAP_FLAG_DENY_BUFFERS {#d3d12_heap_flag_deny_buffers}

値は 0x4 です。バッファを置けなくします。リソース ヒープ層 1 の GPU では、バッファ、レンダー ターゲット・深度のテクスチャ、それ以外のテクスチャを同じヒープに置けないので、この否定のフラグを組み合わせて、置ける物を 1 種類にします。ただし否定のフラグを自分で組み合わせるより、下の `ALLOW_ONLY_*` を使うほうが読みやすくなります。

#### D3D12_HEAP_FLAG_ALLOW_DISPLAY {#d3d12_heap_flag_allow_display}

値は 0x8 です。画面に直接出すリソース（表示用のバッファ）をこのヒープに置けるようにします。スワップ チェーンを自前で作る特殊な場面で使い、通常は触りません。

#### D3D12_HEAP_FLAG_SHARED_CROSS_ADAPTER {#d3d12_heap_flag_shared_cross_adapter}

値は 0x20 です。複数のアダプター（GPU）間でヒープを共有できるようにします。マルチ GPU で、一方が描いた結果をもう一方が読む場合に使います。`D3D12_RESOURCE_FLAG_ALLOW_CROSS_ADAPTER` とセットで使います。

#### D3D12_HEAP_FLAG_DENY_RT_DS_TEXTURES {#d3d12_heap_flag_deny_rt_ds_textures}

値は 0x40 です。レンダー ターゲットと深度ステンシルのテクスチャを置けなくします。

#### D3D12_HEAP_FLAG_DENY_NON_RT_DS_TEXTURES {#d3d12_heap_flag_deny_non_rt_ds_textures}

値は 0x80 です。レンダー ターゲットと深度ステンシル以外のテクスチャを置けなくします。

#### D3D12_HEAP_FLAG_HARDWARE_PROTECTED {#d3d12_heap_flag_hardware_protected}

値は 0x100 です。ハードウェアで保護されたメモリに置きます。DRM 付きの映像再生などの用途で、ゲームでは使いません。

#### D3D12_HEAP_FLAG_ALLOW_WRITE_WATCH {#d3d12_heap_flag_allow_write_watch}

値は 0x200 です。CPU の書き込みを追跡できるようにします。`GetWriteWatch` を使う特殊な管理のためで、ふつうは使いません。

#### D3D12_HEAP_FLAG_ALLOW_SHADER_ATOMICS {#d3d12_heap_flag_allow_shader_atomics}

値は 0x400 です。複数の GPU や CPU を経由するメモリに対して、シェーダーのアトミック操作を許可します。

#### D3D12_HEAP_FLAG_CREATE_NOT_RESIDENT {#d3d12_heap_flag_create_not_resident}

値は 0x800 です。ヒープをメモリに載せない（常駐させない）状態で作ります。あとで `MakeResident` を呼ぶまで、使えません。大量のリソースを先に作っておいて、必要になったものだけ載せる管理に使います。

#### D3D12_HEAP_FLAG_CREATE_NOT_ZEROED {#d3d12_heap_flag_create_not_zeroed}

値は 0x1000 です。作成時にメモリをゼロで埋める処理を省きます。通常、新しく割り当てたメモリは前に使っていたプロセスのデータが見えないようにゼロ クリアされます。このフラグを付けると、作成が速くなる代わりに、中身が未定義になります。書き込んでから読む用途で、作成が重い場面を軽くしたいときに使います。

#### D3D12_HEAP_FLAG_TOOLS_USE_MANUAL_WRITE_TRACKING {#d3d12_heap_flag_tools_use_manual_write_tracking}

値は 0x2000 です。PIX などのツールが書き込みの追跡を手動で行うことを示します。自分で指定することはほとんどありません。

#### D3D12_HEAP_FLAG_ALLOW_ALL_BUFFERS_AND_TEXTURES {#d3d12_heap_flag_allow_all_buffers_and_textures}

値は 0 で、`NONE` と同じです。バッファとテクスチャのどれでも置けるという意味を名前で示します。リソース ヒープ層 2 以上の GPU でしか通りません。

#### D3D12_HEAP_FLAG_ALLOW_ONLY_BUFFERS {#d3d12_heap_flag_allow_only_buffers}

値は 0xc0 で、`DENY_RT_DS_TEXTURES | DENY_NON_RT_DS_TEXTURES` の組み合わせです。バッファだけを置けるヒープにします。層 1 の GPU でヒープを分けるときの 1 つ目です。

#### D3D12_HEAP_FLAG_ALLOW_ONLY_NON_RT_DS_TEXTURES {#d3d12_heap_flag_allow_only_non_rt_ds_textures}

値は 0x44 で、`DENY_BUFFERS | DENY_RT_DS_TEXTURES` の組み合わせです。通常のテクスチャ（シェーダーが読む絵）だけを置けるヒープにします。

#### D3D12_HEAP_FLAG_ALLOW_ONLY_RT_DS_TEXTURES {#d3d12_heap_flag_allow_only_rt_ds_textures}

値は 0x84 で、`DENY_BUFFERS | DENY_NON_RT_DS_TEXTURES` の組み合わせです。レンダー ターゲットと深度ステンシルのテクスチャだけを置けるヒープにします。画面と同じ大きさの描画先をヒープごと使い回すときに、この指定を使います。

## D3D12_RESOURCE_DIMENSION {#d3d12_resource_dimension}

```cpp
typedef enum D3D12_RESOURCE_DIMENSION {
  D3D12_RESOURCE_DIMENSION_UNKNOWN = 0,
  D3D12_RESOURCE_DIMENSION_BUFFER = 1,
  D3D12_RESOURCE_DIMENSION_TEXTURE1D = 2,
  D3D12_RESOURCE_DIMENSION_TEXTURE2D = 3,
  D3D12_RESOURCE_DIMENSION_TEXTURE3D = 4
} D3D12_RESOURCE_DIMENSION;
```

`D3D12_RESOURCE_DESC` の `Dimension` に入れる値で、リソースの種類を決めます。立方体や配列は別の値ではなく、2D テクスチャの `DepthOrArraySize` で表します。

#### D3D12_RESOURCE_DIMENSION_UNKNOWN {#d3d12_resource_dimension_unknown}

値は 0 で、初期化していない構造体の値です。この値のままリソースを作ろうとすると、失敗します。

#### D3D12_RESOURCE_DIMENSION_BUFFER {#d3d12_resource_dimension_buffer}

バイト列の並びです。頂点バッファ、インデックス バッファ、定数バッファ、構造化バッファがすべてこれです。`Height`、`DepthOrArraySize`、`MipLevels` は 1、`Format` は `DXGI_FORMAT_UNKNOWN`、`Layout` は `ROW_MAJOR` にします。`Width` が大きさ（バイト）です。

#### D3D12_RESOURCE_DIMENSION_TEXTURE1D {#d3d12_resource_dimension_texture1d}

幅だけを持つ 1 次元のテクスチャです。グラデーションを引く LUT（色の対応表）に使えますが、ゲームで使う場面は少なく、幅 N × 高さ 1 の 2D テクスチャで済ませることが多くなります。

#### D3D12_RESOURCE_DIMENSION_TEXTURE2D {#d3d12_resource_dimension_texture2d}

幅と高さを持つ 2 次元のテクスチャで、最もよく使います。通常の画像、レンダー ターゲット、深度バッファ、キューブマップ（`DepthOrArraySize` を 6）、テクスチャ配列がすべてこの値です。

#### D3D12_RESOURCE_DIMENSION_TEXTURE3D {#d3d12_resource_dimension_texture3d}

幅、高さ、奥行きを持つボリューム テクスチャです。ボリューム フォグのデータや 3D LUT（カラー グレーディング用）に使います。`DepthOrArraySize` が奥行きです。

## D3D12_TEXTURE_LAYOUT {#d3d12_texture_layout}

```cpp
typedef enum D3D12_TEXTURE_LAYOUT {
  D3D12_TEXTURE_LAYOUT_UNKNOWN = 0,
  D3D12_TEXTURE_LAYOUT_ROW_MAJOR = 1,
  D3D12_TEXTURE_LAYOUT_64KB_UNDEFINED_SWIZZLE = 2,
  D3D12_TEXTURE_LAYOUT_64KB_STANDARD_SWIZZLE = 3
} D3D12_TEXTURE_LAYOUT;
```

`D3D12_RESOURCE_DESC` の `Layout` に入れる値で、メモリ上の並びを決めます。GPU は最適化のために、テクスチャを独自の並びで保存します。

#### D3D12_TEXTURE_LAYOUT_UNKNOWN {#d3d12_texture_layout_unknown}

値は 0 で、並びを GPU に任せます。テクスチャの既定値で、`UNKNOWN` のテクスチャは、`Map` できません。CPU から中身を入れたいときは、`UPLOAD` ヒープのバッファに書いて、`CopyTextureRegion` で移します。

#### D3D12_TEXTURE_LAYOUT_ROW_MAJOR {#d3d12_texture_layout_row_major}

行を順に並べた、普通の画像と同じ並びです。バッファは必ずこれにします。テクスチャに使うと `Map` はできますが、GPU の読み取りが遅くなるなどの制限が多く、ふつうは使いません。

#### D3D12_TEXTURE_LAYOUT_64KB_UNDEFINED_SWIZZLE {#d3d12_texture_layout_64kb_undefined_swizzle}

64KB 単位のタイルで並べる形式で、並びの詳細は GPU 依存です。タイルド リソースなどで使う特殊な値で、ふつうのゲームでは触りません。

#### D3D12_TEXTURE_LAYOUT_64KB_STANDARD_SWIZZLE {#d3d12_texture_layout_64kb_standard_swizzle}

64KB 単位のタイルを標準のスウィズルで並べる形式です。複数のアダプター間で並びをそろえたい場合や、CPU が直接タイルの中身を扱いたい場合の値で、対応しない GPU もあります。使う前に `D3D12_FEATURE_DATA_D3D12_OPTIONS` の `StandardSwizzle64KBSupported` で確認します。

## D3D12_RESOURCE_FLAGS {#d3d12_resource_flags}

```cpp
typedef enum D3D12_RESOURCE_FLAGS {
  D3D12_RESOURCE_FLAG_NONE = 0,
  D3D12_RESOURCE_FLAG_ALLOW_RENDER_TARGET = 0x1,
  D3D12_RESOURCE_FLAG_ALLOW_DEPTH_STENCIL = 0x2,
  D3D12_RESOURCE_FLAG_ALLOW_UNORDERED_ACCESS = 0x4,
  D3D12_RESOURCE_FLAG_DENY_SHADER_RESOURCE = 0x8,
  // ... 以下、各値の節
} D3D12_RESOURCE_FLAGS;
```

`D3D12_RESOURCE_DESC` の `Flags` に入れる値で、リソースをどう使うかを前もって宣言します。宣言しておくと、GPU はそれに合ったメモリの並びや圧縮を選べます。宣言しなかった使い方（たとえば `ALLOW_RENDER_TARGET` なしのテクスチャへのレンダー ターゲット ビュー）は、ビューを作る時点でエラーになります。

#### D3D12_RESOURCE_FLAG_NONE {#d3d12_resource_flag_none}

値は 0 で、特別な使い方をしません。シェーダーが読むだけの通常のテクスチャや、頂点・インデックス・定数の各バッファです。

#### D3D12_RESOURCE_FLAG_ALLOW_RENDER_TARGET {#d3d12_resource_flag_allow_render_target}

値は 0x1 で、レンダー ターゲットとして描き込むことを許します。`CreateRenderTargetView` で RTV を作るリソースに付けます。バッファには付けられず、2D テクスチャなどに使います。

#### D3D12_RESOURCE_FLAG_ALLOW_DEPTH_STENCIL {#d3d12_resource_flag_allow_depth_stencil}

値は 0x2 で、深度ステンシルとして使うことを許します。`CreateDepthStencilView` で DSV を作るリソースに付けます。`ALLOW_RENDER_TARGET` や `ALLOW_UNORDERED_ACCESS` とは同時に付けられません。深度バッファをシェーダーで読むなら、`DENY_SHADER_RESOURCE` を付けないままにします。

#### D3D12_RESOURCE_FLAG_ALLOW_UNORDERED_ACCESS {#d3d12_resource_flag_allow_unordered_access}

値は 0x4 で、UAV として読み書きすることを許します。コンピュート シェーダーの出力先になるバッファとテクスチャに付けます。付けると GPU の圧縮が使えなくなる場合があるので、必要なリソースにだけ付けます。

#### D3D12_RESOURCE_FLAG_DENY_SHADER_RESOURCE {#d3d12_resource_flag_deny_shader_resource}

値は 0x8 で、SRV として読むことを禁止します。`ALLOW_DEPTH_STENCIL` のリソースにだけ付けられます。深度バッファをシェーダーで読まないと分かっているなら、付けると GPU が深度専用の最適な並びを選べます。

#### D3D12_RESOURCE_FLAG_ALLOW_CROSS_ADAPTER {#d3d12_resource_flag_allow_cross_adapter}

値は 0x10 で、複数の GPU から同じリソースを使うことを許します。`D3D12_HEAP_FLAG_SHARED_CROSS_ADAPTER` のヒープに置いて使います。

#### D3D12_RESOURCE_FLAG_ALLOW_SIMULTANEOUS_ACCESS {#d3d12_resource_flag_allow_simultaneous_access}

値は 0x20 で、複数のキュー（描画とコンピュートなど）から同時にアクセスすることを許します。付けたテクスチャは、`COMMON` からの暗黙の昇格と、実行後の減衰の対象になります。代わりに GPU の圧縮が使えなくなり、読み取りが遅くなりがちなので、必要なときだけ付けます。

#### D3D12_RESOURCE_FLAG_VIDEO_DECODE_REFERENCE_ONLY {#d3d12_resource_flag_video_decode_reference_only}

値は 0x40 で、ビデオ デコードの参照フレーム専用のリソースを表します。ゲームでは使いません。

#### D3D12_RESOURCE_FLAG_VIDEO_ENCODE_REFERENCE_ONLY {#d3d12_resource_flag_video_encode_reference_only}

値は 0x80 で、ビデオ エンコードの参照フレーム専用のリソースを表します。ゲームでは使いません。

#### D3D12_RESOURCE_FLAG_RAYTRACING_ACCELERATION_STRUCTURE {#d3d12_resource_flag_raytracing_acceleration_structure}

値は 0x100 で、DXR の加速構造を置くバッファに付けます。このフラグを付けたバッファは、`D3D12_RESOURCE_STATE_RAYTRACING_ACCELERATION_STRUCTURE` 状態で作り、加速構造以外には使えません。`ALLOW_UNORDERED_ACCESS` と一緒に付けます（[DXR Host](../dxr-host.md)）。

## D3D12_TEXTURE_COPY_TYPE {#d3d12_texture_copy_type}

```cpp
typedef enum D3D12_TEXTURE_COPY_TYPE {
  D3D12_TEXTURE_COPY_TYPE_SUBRESOURCE_INDEX = 0,
  D3D12_TEXTURE_COPY_TYPE_PLACED_FOOTPRINT = 1
} D3D12_TEXTURE_COPY_TYPE;
```

`CopyTextureRegion` の宛先と元は、`D3D12_TEXTURE_COPY_LOCATION` 構造体で指します。その `Type` に入れる値で、「テクスチャのサブリソース」を指すのか、「バッファの中の配置済みのテクスチャ データ」を指すのかを選びます。テクスチャをアップロードする場合は、宛先がテクスチャ側の `SUBRESOURCE_INDEX`、元がバッファ側の `PLACED_FOOTPRINT` になります。

#### D3D12_TEXTURE_COPY_TYPE_SUBRESOURCE_INDEX {#d3d12_texture_copy_type_subresource_index}

値は 0 で、リソース（テクスチャ）のサブリソースの番号を指します。`SubresourceIndex` に、ミップマップや配列スライスを通した番号を入れます。ミップ 0 の 1 枚目なら 0 です。

#### D3D12_TEXTURE_COPY_TYPE_PLACED_FOOTPRINT {#d3d12_texture_copy_type_placed_footprint}

値は 1 で、バッファの中に配置したテクスチャ データを指します。`PlacedFootprint`（バッファ内のオフセット、フォーマット、幅、高さ、`RowPitch`）に値を入れます。`RowPitch` は `D3D12_TEXTURE_DATA_PITCH_ALIGNMENT`（256）の倍数にします。`GetCopyableFootprints` が、この値を計算してくれます（[Texture Upload](../texture-upload.md)）。

## よくあるミス

??? failure "UPLOAD ヒープのリソースを GENERIC_READ 以外で作った"
    `CreateCommittedResource` が `E_INVALIDARG` で失敗します。`UPLOAD` は `GENERIC_READ`、`READBACK` は `COPY_DEST` で作ります。

??? failure "ALLOW_RENDER_TARGET を付け忘れた"
    テクスチャは作れても、`CreateRenderTargetView` の呼び出しや、実行時のバリアでエラーになります。描き込むテクスチャは、作成時にフラグを付けます。

??? failure "RowPitch を 256 の倍数にしていない"
    画像の行の幅をそのまま `RowPitch` にすると、`CopyTextureRegion` が失敗します。アップロード用バッファには、256 の倍数に切り上げた幅で 1 行ずつコピーします。

## 関連ページ

- [Heaps and Resources](../heaps-resources.md)
- [Upload Buffer](../upload-buffer.md)
- [Texture Upload](../texture-upload.md)
- [Resource State Enums](enum-resource-state.md)
