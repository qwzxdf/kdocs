---
title: Resource Structs
tags:
  - DirectX
api:
  - D3D12_HEAP_PROPERTIES
---

# Resource Structs

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

バッファやテクスチャを 1 つ作るだけでも、D3D12 では「どのメモリに置くか」「どんな形か」「作った直後の最適なクリア色は何か」を別々の構造体で伝えます。`CreateCommittedResource` の引数が 3 つの構造体ポインタになっているのはそのためです。このページでは、リソースの作成とアクセスに使う構造体を使う順に説明します。

!!! tip "ポイント"
    - 構造体は必ず `= {}` でゼロ初期化してから、使うメンバーだけを埋める。
    - `D3D12_HEAP_PROPERTIES` は `Type` だけ決めればよい（`CUSTOM` 以外）。
    - バッファの `D3D12_RESOURCE_DESC` は、幅がバイト数で、ほかは決まった値になる。
    - CPU から読まない `Map` は `D3D12_RANGE` に `End = 0` を渡す。
    - `D3D12_RECT` は `RECT` と同じ形で、`right` と `bottom` は含まない。

!!! info "このページを読む前に"
    構造体を渡す先のメソッドは [ID3D12Device](id3d12device.md) と [ID3D12Resource](id3d12resource.md)、全体の流れは [Heaps and Resources](../heaps-resources.md) で説明しています。組み立てを短くする関数は [Helper Functions](../util.md) にあります。

## 構造体一覧

| 構造体 | 役割 | 使う場所 |
| --- | --- | --- |
| [`D3D12_HEAP_PROPERTIES`](#d3d12_heap_properties) | どのメモリに置くか | `CreateCommittedResource`、`CreateHeap` |
| [`D3D12_HEAP_DESC`](#d3d12_heap_desc) | ヒープそのものの大きさと性質 | `CreateHeap` |
| [`D3D12_RESOURCE_DESC`](#d3d12_resource_desc) | バッファやテクスチャの形 | `CreateCommittedResource`、`CreatePlacedResource` |
| [`D3D12_CLEAR_VALUE`](#d3d12_clear_value) | 最適化するクリア値 | リソースの作成 |
| [`D3D12_RANGE`](#d3d12_range) | `Map` で CPU が触る範囲 | `Map`、`Unmap` |
| [`D3D12_BOX`](#d3d12_box) | コピー元の直方体の範囲 | `CopyTextureRegion` |
| [`D3D12_RECT`](#d3d12_rect) | 画面上の四角形 | `ClearRenderTargetView`、`RSSetScissorRects` |
| [`D3D12_VIEWPORT`](#d3d12_viewport) | 描画先への変換 | `RSSetViewports` |

## D3D12_HEAP_PROPERTIES {#d3d12_heap_properties}

```cpp
typedef struct D3D12_HEAP_PROPERTIES {
    D3D12_HEAP_TYPE Type;
    D3D12_CPU_PAGE_PROPERTY CPUPageProperty;
    D3D12_MEMORY_POOL MemoryPoolPreference;
    UINT CreationNodeMask;
    UINT VisibleNodeMask;
} D3D12_HEAP_PROPERTIES;
```

リソースを置くメモリの種類を決める構造体です。GPU 専用の速いメモリに置くか、CPU が書き込める共有メモリに置くかで、使い方がまったく変わるので、リソースを作るときは必ず渡します。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `Type` | `D3D12_HEAP_TYPE` | `DEFAULT`、`UPLOAD`、`READBACK`、`CUSTOM`、`GPU_UPLOAD` のどれか |
| `CPUPageProperty` | `D3D12_CPU_PAGE_PROPERTY` | `CUSTOM` のときだけ決める CPU からの見え方 |
| `MemoryPoolPreference` | `D3D12_MEMORY_POOL` | `CUSTOM` のときだけ決めるメモリの場所 |
| `CreationNodeMask` | `UINT` | リソースを作る GPU（ノード）のビットマスク |
| `VisibleNodeMask` | `UINT` | リソースが見える GPU のビットマスク |

`Type` が一番大事なメンバーです。`DEFAULT` は GPU が最も速く読み書きできる場所で、CPU からは触れません。`UPLOAD` は CPU が書いて GPU が読む場所で、CPU からは `Map` で書けますが GPU からの読み取りは `DEFAULT` より遅くなります。`READBACK` は GPU が書いて CPU が読む場所です。頂点バッファやテクスチャの中身は、`UPLOAD` に書いてから `DEFAULT` へコピーするのが定番の手順です。`CUSTOM` は次の 2 つのメンバーを自分で決める上級者向けの指定で、普通は使いません。

`CPUPageProperty` と `MemoryPoolPreference` は、`Type` が `CUSTOM` 以外のときは `UNKNOWN` にします。`DEFAULT` や `UPLOAD` のときに `UNKNOWN` 以外の値を入れると、リソースの作成が失敗します。`UNKNOWN` は 0 なので、`= {}` で初期化すればそのまま正しい値です。

`CreationNodeMask` と `VisibleNodeMask` は、GPU を複数つなぐ構成（マルチ アダプター）でどの GPU を使うかを指定します。GPU が 1 つなら `1` を入れます。0 を入れても、1 と同じに扱われます。

この 4 つ以外を毎回書くのは面倒なので、普段は [`MakeHeapProperties`](../util.md#makeheapproperties) を使います。

```cpp
// 素の構造体で書くとこうなる（MakeHeapProperties と同じ結果）。
D3D12_HEAP_PROPERTIES upload = {};
upload.Type = D3D12_HEAP_TYPE_UPLOAD;
upload.CreationNodeMask = 1;
upload.VisibleNodeMask = 1;
```

!!! failure "よくあるミス"
    - `Type = UPLOAD` なのに `InitialResourceState` を `GENERIC_READ` 以外にして `E_INVALIDARG` になる。`UPLOAD` は必ず `GENERIC_READ`、`READBACK` は必ず `COPY_DEST` で作る。
    - `UPLOAD` のバッファにレンダー ターゲットや深度バッファの `Flags` を付ける。`UPLOAD` と `READBACK` に置けるのはバッファだけである。
    - `Type` が `DEFAULT` なのに `CPUPageProperty` を書いてしまう。

## D3D12_HEAP_DESC {#d3d12_heap_desc}

```cpp
typedef struct D3D12_HEAP_DESC {
    UINT64 SizeInBytes;
    D3D12_HEAP_PROPERTIES Properties;
    UINT64 Alignment;
    D3D12_HEAP_FLAGS Flags;
} D3D12_HEAP_DESC;
```

ヒープだけを作る `CreateHeap` に渡す構造体です。大きなメモリを先に 1 つ確保して、その中へ複数のリソースを `CreatePlacedResource` で並べるときに使います。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `SizeInBytes` | `UINT64` | ヒープの大きさ（バイト） |
| `Properties` | `D3D12_HEAP_PROPERTIES` | どのメモリか（前の節） |
| `Alignment` | `UINT64` | 置き位置の境界。0、64 KB、4 MB のどれか |
| `Flags` | `D3D12_HEAP_FLAGS` | 置けるリソースの制限など |

`SizeInBytes` は `Alignment` の倍数にします。倍数でない値は `E_INVALIDARG` になるので、`AlignUp` のような関数で切り上げてから渡します。

`Alignment` は、0 にすると 64 KB（`D3D12_DEFAULT_RESOURCE_PLACEMENT_ALIGNMENT`）になります。MSAA のテクスチャをこのヒープに置くなら 4 MB（`D3D12_DEFAULT_MSAA_RESOURCE_PLACEMENT_ALIGNMENT`）が必要です。

`Flags` は、通常は `D3D12_HEAP_FLAG_NONE` です。リソース ヒープ層（`D3D12_RESOURCE_HEAP_TIER`）が 1 のハードウェアでは、1 つのヒープにバッファとテクスチャを混ぜられないため、`ALLOW_ONLY_BUFFERS`、`ALLOW_ONLY_NON_RT_DS_TEXTURES`、`ALLOW_ONLY_RT_DS_TEXTURES` のどれかで種類を制限します。層が 2 ならフラグなしで混ぜて置けます。

```cpp
D3D12_HEAP_DESC desc = {};
desc.SizeInBytes = 64ull * 1024 * 1024;              // 64 MB
desc.Properties = MakeHeapProperties(D3D12_HEAP_TYPE_DEFAULT);
desc.Alignment = 0;                                  // 64 KB
desc.Flags = D3D12_HEAP_FLAG_ALLOW_ONLY_RT_DS_TEXTURES;
HRESULT hr = device->CreateHeap(&desc, IID_PPV_ARGS(&heap));
```

## D3D12_RESOURCE_DESC {#d3d12_resource_desc}

```cpp
typedef struct D3D12_RESOURCE_DESC {
    D3D12_RESOURCE_DIMENSION Dimension;
    UINT64 Alignment;
    UINT64 Width;
    UINT Height;
    UINT16 DepthOrArraySize;
    UINT16 MipLevels;
    DXGI_FORMAT Format;
    DXGI_SAMPLE_DESC SampleDesc;
    D3D12_TEXTURE_LAYOUT Layout;
    D3D12_RESOURCE_FLAGS Flags;
} D3D12_RESOURCE_DESC;
```

バッファかテクスチャかを問わず、リソースの形をすべて表す構造体です。D3D12 ではバッファも 1 次元の「リソース」なので、同じ構造体で書きます。バッファとテクスチャでメンバーの使い方が違うため、間違えやすい構造体です。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `Dimension` | `D3D12_RESOURCE_DIMENSION` | `BUFFER`、`TEXTURE1D`、`TEXTURE2D`、`TEXTURE3D` |
| `Alignment` | `UINT64` | 0 にすると既定の境界になる |
| `Width` | `UINT64` | バッファはバイト数、テクスチャはピクセル数 |
| `Height` | `UINT` | テクスチャの高さ。バッファは 1 |
| `DepthOrArraySize` | `UINT16` | 3D は奥行き、1D と 2D は配列の要素数 |
| `MipLevels` | `UINT16` | ミップの数。0 は全ミップ |
| `Format` | `DXGI_FORMAT` | ピクセル形式。バッファは `UNKNOWN` |
| `SampleDesc` | `DXGI_SAMPLE_DESC` | `Count` と `Quality`。MSAA を使わなければ `{1, 0}` |
| `Layout` | `D3D12_TEXTURE_LAYOUT` | テクスチャは `UNKNOWN`、バッファは `ROW_MAJOR` |
| `Flags` | `D3D12_RESOURCE_FLAGS` | ビューにしてよい用途 |

`Dimension` が決まると、ほかのメンバーの意味が決まります。バッファなら `Width` が全体のバイト数で、`Height` と `DepthOrArraySize` と `MipLevels` はすべて 1、`Format` は `UNKNOWN`、`Layout` は `ROW_MAJOR` です。バッファでこの約束を破ると `E_INVALIDARG` になります。2D テクスチャなら `Width` と `Height` がピクセル数、`DepthOrArraySize` は配列のスライス数（キューブ マップは 6）、`Layout` は `UNKNOWN` です。`Width` だけが `UINT64` なのは、バッファの大きさが 4 GB を超えられるようにするためです。

`Alignment` は 0 のままにします。0 なら、通常のリソースは 64 KB、MSAA は 4 MB になります。小さなテクスチャだけ 4 KB にしたい場合など（`D3D12_SMALL_RESOURCE_PLACEMENT_ALIGNMENT`）は例外ですが、初心者は気にする必要がありません。

`MipLevels` が 0 のときは、1×1 になるまでの全段のミップが作られます。作ったあとの本当の数は `GetDesc()` で調べます。

`Format` は、使い道によって typeless にします。たとえば深度バッファを深度として書きつつ、シェーダーでも読みたいときは `DXGI_FORMAT_R32_TYPELESS` で作って、DSV は `D32_FLOAT`、SRV は `R32_FLOAT` で作ります。深度バッファに `D32_FLOAT` で作ると SRV を作れません。

`SampleDesc` は MSAA を使わなければ `Count = 1`、`Quality = 0` です。`Count = 0` にするとリソースの作成が失敗します。ゼロ初期化したあとに `Count` だけを 1 にするのを忘れる事故がよくあります。

`Flags` は、ビューにしてよい用途を前もって宣言するものです。`ALLOW_RENDER_TARGET` は RTV、`ALLOW_DEPTH_STENCIL` は DSV、`ALLOW_UNORDERED_ACCESS` は UAV を作るために必要です。`DENY_SHADER_RESOURCE` は、深度バッファを SRV にしないと宣言して、GPU の最適化を引き出す指定です。宣言のない用途のビューを作ると、`CreateXxxView` でデバッグ レイヤーのエラーになります。

組み立ては [`MakeBufferDesc`](../util.md#makebufferdesc) と [`MakeTexture2DDesc`](../util.md#maketexture2ddesc) に任せると短くなります。

```cpp
// 深度バッファ（シェーダーでも読む）。
D3D12_RESOURCE_DESC depth = MakeTexture2DDesc(
    DXGI_FORMAT_R32_TYPELESS, 1280, 720, 1, 1, D3D12_RESOURCE_FLAG_ALLOW_DEPTH_STENCIL);
// MSAA を使うなら、素の構造体で SampleDesc を変える。
depth.SampleDesc.Count = 4;
```

!!! failure "よくあるミス"
    - 2D テクスチャで `SampleDesc.Count` を 0 のままにする。必ず 1 以上にする。
    - バッファの `Width` を要素数で書く。単位はバイトである。定数バッファは 256 の倍数に切り上げる。
    - `ALLOW_RENDER_TARGET` を付け忘れて、RTV の作成でエラーになる。
    - `ALLOW_RENDER_TARGET` と `ALLOW_DEPTH_STENCIL` を同じリソースに付ける。両立しない。

## D3D12_CLEAR_VALUE {#d3d12_clear_value}

```cpp
typedef struct D3D12_CLEAR_VALUE {
    DXGI_FORMAT Format;
    union {
        FLOAT Color[4];
        D3D12_DEPTH_STENCIL_VALUE DepthStencil;
    };
} D3D12_CLEAR_VALUE;
```

「このリソースは普段この値でクリアする」と作成時に伝える構造体です。GPU は伝えられた値でクリアするとき、メモリを実際に塗らずに圧縮情報だけを書き換える最適化を使えることがあります。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `Format` | `DXGI_FORMAT` | ビューの形式。typeless は不可 |
| `Color` | `FLOAT[4]` | レンダー ターゲットのクリア色（RGBA） |
| `DepthStencil` | `D3D12_DEPTH_STENCIL_VALUE` | 深度バッファの `Depth` と `Stencil` |

`Color` と `DepthStencil` は union で、同じ場所を共有します。レンダー ターゲットには `Color`、深度バッファには `DepthStencil` を使い、両方を埋めることはできません。

`Format` に typeless を入れてはいけません。深度バッファを `R32_TYPELESS` で作る場合も、ここには `D32_FLOAT` のようにビューで使う形式を書きます。

この構造体を渡す先は `CreateCommittedResource` と `CreatePlacedResource` の `pOptimizedClearValue` です。バッファと、レンダー ターゲットでも深度バッファでもないテクスチャには `nullptr` を渡します。レンダー ターゲットと深度バッファには指定できますが、省略もできます。あとで別の値で `ClearRenderTargetView` を呼ぶと動きはしますが、デバッグ レイヤーが警告を出し、最適化も効きません。

```cpp
D3D12_CLEAR_VALUE clear = {};
clear.Format = DXGI_FORMAT_D32_FLOAT;   // ビューの形式
clear.DepthStencil.Depth = 1.0f;
clear.DepthStencil.Stencil = 0;

HRESULT hr = device->CreateCommittedResource(
    &heap, D3D12_HEAP_FLAG_NONE, &depth_desc,
    D3D12_RESOURCE_STATE_DEPTH_WRITE, &clear, IID_PPV_ARGS(&depth_buffer));
```

## D3D12_RANGE {#d3d12_range}

```cpp
typedef struct D3D12_RANGE {
    SIZE_T Begin;
    SIZE_T End;
} D3D12_RANGE;
```

`ID3D12Resource::Map` と `Unmap` に渡す、バイト単位の範囲です。「CPU がこの範囲を読む（書いた）」と宣言するためのものです。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `Begin` | `SIZE_T` | 範囲の先頭（バイト）。範囲に含む |
| `End` | `SIZE_T` | 範囲の終わり（バイト）。範囲に含まない |

`Begin` から `End` の手前までが範囲です。`End == Begin` なら空の範囲を表します。

`Map` の `pReadRange` では「CPU が読む範囲」を伝えます。書き込みしかしない `UPLOAD` のバッファでは、読まないので `Begin = End = 0` の範囲を渡します。`nullptr` を渡すと「全体を読むかもしれない」という意味になります。`READBACK` のバッファで結果を読むときは、読む範囲、または `nullptr` を渡します。

`Unmap` の `pWrittenRange` では、CPU が書いた範囲を伝えます。`nullptr` は全体を書いた可能性があるという意味です。範囲を絞ると、不要なキャッシュの同期を省けます。

```cpp
void* mapped = nullptr;
D3D12_RANGE read_range = {0, 0};  // この Map では読まない
HRESULT hr = buffer->Map(0, &read_range, &mapped);
std::memcpy(mapped, data, size);
D3D12_RANGE written = {0, size};  // 0 から size の手前まで書いた
buffer->Unmap(0, &written);
```

!!! failure "よくあるミス"
    - `End` に「含む」最後の位置を入れてしまい、1 バイトずれる。`End` は範囲の外側の位置である。
    - `UPLOAD` に書くだけなのに `nullptr` を渡す。動くが、読む可能性があるという宣言になる。

## D3D12_BOX {#d3d12_box}

```cpp
typedef struct D3D12_BOX {
    UINT left;
    UINT top;
    UINT front;
    UINT right;
    UINT bottom;
    UINT back;
} D3D12_BOX;
```

テクスチャの一部をコピーするとき、コピー元の範囲を直方体で指定します。`CopyTextureRegion` の `pSrcBox` が受け取ります。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `left`、`right` | `UINT` | X の範囲。ピクセル単位（バッファはバイト単位） |
| `top`、`bottom` | `UINT` | Y の範囲 |
| `front`、`back` | `UINT` | Z の範囲。2D なら `front = 0`、`back = 1` |

どの軸も、`left` と `right` のように「小さいほうを含み、大きいほうを含まない」範囲です。`right` が `left` 以下のように、どれかの軸で幅が 0 以下になると、範囲は空になり、何もコピーされません。

2D テクスチャでは Z 軸が存在しないため、`front = 0`、`back = 1` にします。`back` を 0 のままにすると空の範囲になり、コピーされないので注意してください。`pSrcBox` に `nullptr` を渡せば、コピー元のサブリソース全体を意味します。

```cpp
// 256x256 のテクスチャの左上 128x128 だけをコピーする。
D3D12_BOX box = {};
box.left = 0;
box.top = 0;
box.front = 0;
box.right = 128;
box.bottom = 128;
box.back = 1;  // 2D は 1 にする
```

## D3D12_RECT {#d3d12_rect}

```cpp
typedef RECT D3D12_RECT;   // LONG left, top, right, bottom
```

画面上の四角形を表します。Win32 の `RECT` と同じ型です。クリアの範囲（`ClearRenderTargetView` の `pRects`）と、シザー矩形（`RSSetScissorRects`）で使います。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `left` | `LONG` | 左端の X。範囲に含む |
| `top` | `LONG` | 上端の Y。範囲に含む |
| `right` | `LONG` | 右端の X。範囲に含まない |
| `bottom` | `LONG` | 下端の Y。範囲に含まない |

座標の原点は左上で、Y は下向きに増えます。`right` と `bottom` はその位置を含まないので、画面全体を指すときは `{0, 0, width, height}` です。`width - 1` にしてしまうと、右端と下端が 1 ピクセル欠けます。`LONG` は符号付きなので、負の値も書けますが、ターゲットの外の部分は切り取られます。

シザー矩形は、[`D3D12_VIEWPORT`](#d3d12_viewport) の外側を切る別の仕組みです。ビューポートを設定しただけではシザー矩形は設定されません。毎フレーム、両方を設定します。`RSSetScissorRects` を呼ばないと何も描かれません。

```cpp
D3D12_RECT scissor = {0, 0, static_cast<LONG>(width), static_cast<LONG>(height)};
command_list->RSSetScissorRects(1, &scissor);
```

## D3D12_VIEWPORT {#d3d12_viewport}

```cpp
typedef struct D3D12_VIEWPORT {
    FLOAT TopLeftX;
    FLOAT TopLeftY;
    FLOAT Width;
    FLOAT Height;
    FLOAT MinDepth;
    FLOAT MaxDepth;
} D3D12_VIEWPORT;
```

頂点シェーダーが出す座標（クリップ空間）をレンダー ターゲットのピクセル座標へ変える範囲を決めます。描き込む四角形の位置と大きさ、深度の範囲を指定します。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `TopLeftX`、`TopLeftY` | `FLOAT` | ビューポートの左上（ピクセル） |
| `Width`、`Height` | `FLOAT` | 大きさ（ピクセル） |
| `MinDepth`、`MaxDepth` | `FLOAT` | 深度の範囲。通常は 0.0 と 1.0 |

画面全体に描くときは `TopLeftX = TopLeftY = 0`、`Width` と `Height` にレンダー ターゲットの大きさ、深度は 0 と 1 にします。画面を分割して 2 人プレイにしたり、ミニマップを小さく描いたりするときは、描き込む範囲だけを変えます。

`MinDepth` と `MaxDepth` は、ピクセルの深度を 0〜1 のどこに写すかです。ほぼ常に 0 と 1 です。0 のままにする（`MaxDepth` を 0 にする）と、すべてのピクセルの深度が 0 になり、深度テストがおかしくなります。ゼロ初期化したときに `MaxDepth` だけ書き忘れる事故が多いです。

D3D12 では、ビューポートとシザー矩形はコマンド リストごとに必ず設定します。コマンド リストをリセットするたびに、設定は忘れられます。

```cpp
D3D12_VIEWPORT viewport = {};
viewport.Width = static_cast<float>(width);
viewport.Height = static_cast<float>(height);
viewport.MinDepth = 0.0f;
viewport.MaxDepth = 1.0f;   // 0 のままだと深度が全部 0 になる
command_list->RSSetViewports(1, &viewport);
```

!!! failure "よくあるミス"
    - `MaxDepth` を設定し忘れる。
    - ビューポートだけ設定して `RSSetScissorRects` を呼ばず、何も描かれない。
    - ウィンドウをリサイズしたのに、ビューポートが古い大きさのままになる。

## 関連ページ

- [ID3D12Device](id3d12device.md) — `CreateCommittedResource` と `CreateHeap`
- [ID3D12Resource](id3d12resource.md) — `Map`、`Unmap`
- [Heaps and Resources](../heaps-resources.md) — ヒープとリソースの全体像
- [Viewport and Scissor](../viewport-scissor.md) — ビューポートとシザー矩形の使い方
- [Helper Functions](../util.md) — `MakeHeapProperties`、`MakeBufferDesc`
