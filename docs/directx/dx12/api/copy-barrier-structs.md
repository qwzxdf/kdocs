---
title: Copy and Barrier Structs
tags:
  - DirectX
api:
  - D3D12_RESOURCE_BARRIER
---

# Copy and Barrier Structs

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

テクスチャを GPU に送るときと、リソースの使い道を切り替えるときは、どちらもコマンド リストに「どのリソースの、どの部分を、どうするか」を構造体で渡します。テクスチャのコピーには「メモリの中でどう並んでいるか」を表す構造体、状態の切り替えには「どの状態からどの状態へ」を表す構造体が必要です。このページではその 2 グループを説明します。

!!! tip "ポイント"
    - テクスチャのコピー元とコピー先は `D3D12_TEXTURE_COPY_LOCATION` で書く。`Type` で共用体の使うメンバーが決まる。
    - バッファ側の並びは `D3D12_PLACED_SUBRESOURCE_FOOTPRINT`。`RowPitch` は 256 の倍数。
    - バリアは `Type` を先に決めて、使うメンバー（`Transition`、`UAV`、`Aliasing`）だけを埋める。
    - 遷移バリアの `StateBefore` は、リソースの実際の今の状態と一致させる。

!!! info "このページを読む前に"
    コピーの手順は [Texture Upload](../texture-upload.md)、バリアの考え方は [Resource Barrier](../resource-barrier.md) で説明しています。構造体を渡すコマンドは [ID3D12GraphicsCommandList](id3d12graphicscommandlist.md) にあります。

## 構造体一覧

| 構造体 | 役割 | 使う場所 |
| --- | --- | --- |
| [`D3D12_SUBRESOURCE_FOOTPRINT`](#d3d12_subresource_footprint) | バッファ上の 1 サブリソースの形 | `D3D12_PLACED_SUBRESOURCE_FOOTPRINT` の中身 |
| [`D3D12_PLACED_SUBRESOURCE_FOOTPRINT`](#d3d12_placed_subresource_footprint) | バッファ内の位置と形 | `GetCopyableFootprints`、`CopyTextureRegion` |
| [`D3D12_TEXTURE_COPY_LOCATION`](#d3d12_texture_copy_location) | コピーの元と先 | `CopyTextureRegion` |
| [`D3D12_RESOURCE_BARRIER`](#d3d12_resource_barrier) | バリア 1 つ分 | `ResourceBarrier` |
| [`D3D12_RESOURCE_TRANSITION_BARRIER`](#d3d12_resource_transition_barrier) | 状態の遷移 | バリアの `Transition` |
| [`D3D12_RESOURCE_UAV_BARRIER`](#d3d12_resource_uav_barrier) | UAV の書き込み待ち | バリアの `UAV` |
| [`D3D12_RESOURCE_ALIASING_BARRIER`](#d3d12_resource_aliasing_barrier) | 同じメモリを使う入れ替え | バリアの `Aliasing` |

## テクスチャのコピー

### D3D12_SUBRESOURCE_FOOTPRINT {#d3d12_subresource_footprint}

```cpp
typedef struct D3D12_SUBRESOURCE_FOOTPRINT {
    DXGI_FORMAT Format;
    UINT Width;
    UINT Height;
    UINT Depth;
    UINT RowPitch;
} D3D12_SUBRESOURCE_FOOTPRINT;
```

アップロード用のバッファに、テクスチャ 1 枚分のピクセルがどう並んでいるかを表します。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `Format` | `DXGI_FORMAT` | ピクセル形式 |
| `Width` | `UINT` | 幅（ピクセル） |
| `Height` | `UINT` | 高さ（ピクセル） |
| `Depth` | `UINT` | 奥行き。2D は 1 |
| `RowPitch` | `UINT` | 1 行の先頭から次の行の先頭までのバイト数 |

`RowPitch` が大事なメンバーです。`Width × 1 ピクセルのバイト数` の値ではなく、それを 256（`D3D12_TEXTURE_DATA_PITCH_ALIGNMENT`）の倍数に切り上げた値でなければなりません。たとえば幅 100 ピクセルの RGBA8 は 400 バイトですが、`RowPitch` は 512 です。CPU から書き込むときも、1 行ごとに `RowPitch` ずつ進めて書きます。これを守らないと、絵が斜めにずれた砂嵐になります。

`Depth` は 2D テクスチャでは 1 にします（奥行きのない面が 1 枚、という意味です）。

自分で計算しなくても、`GetCopyableFootprints` が `RowPitch` を含めて正しい値を返します。

### D3D12_PLACED_SUBRESOURCE_FOOTPRINT {#d3d12_placed_subresource_footprint}

```cpp
typedef struct D3D12_PLACED_SUBRESOURCE_FOOTPRINT {
    UINT64 Offset;
    D3D12_SUBRESOURCE_FOOTPRINT Footprint;
} D3D12_PLACED_SUBRESOURCE_FOOTPRINT;
```

バッファの中のどこから、どんな形で、サブリソースが置かれているかを表します。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `Offset` | `UINT64` | バッファの先頭からのバイト数 |
| `Footprint` | `D3D12_SUBRESOURCE_FOOTPRINT` | 形（前の節） |

`Offset` は 512 バイト（`D3D12_TEXTURE_DATA_PLACEMENT_ALIGNMENT`）の倍数にします。1 つのアップロード バッファに複数のミップ レベルを並べるときは、それぞれ別の `Offset` を持ちます。

通常は自分で埋めず、`ID3D12Device::GetCopyableFootprints` に任せます。この関数は、テクスチャの `D3D12_RESOURCE_DESC` から、各サブリソースの `D3D12_PLACED_SUBRESOURCE_FOOTPRINT` と、1 行の実バイト数（パディングなし）、必要な合計のバイト数を計算して返します。返された `Offset` と `RowPitch` をそのまま使って CPU から書き込みます。

### D3D12_TEXTURE_COPY_LOCATION {#d3d12_texture_copy_location}

```cpp
typedef struct D3D12_TEXTURE_COPY_LOCATION {
    ID3D12Resource* pResource;
    D3D12_TEXTURE_COPY_TYPE Type;
    union {
        D3D12_PLACED_SUBRESOURCE_FOOTPRINT PlacedFootprint;
        UINT SubresourceIndex;
    };
} D3D12_TEXTURE_COPY_LOCATION;
```

`CopyTextureRegion` の元と先を、1 つずつ指す構造体です。テクスチャからテクスチャ、バッファからテクスチャ、テクスチャからバッファの、どのコピーも同じ構造体で書きます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `pResource` | `ID3D12Resource*` | 対象のリソース |
| `Type` | `D3D12_TEXTURE_COPY_TYPE` | 共用体のどちらを使うか |
| `SubresourceIndex` | `UINT` | `Type = SUBRESOURCE_INDEX` のとき。サブリソースの番号 |
| `PlacedFootprint` | `D3D12_PLACED_SUBRESOURCE_FOOTPRINT` | `Type = PLACED_FOOTPRINT` のとき。バッファ内の配置 |

`Type` は 2 通りです。`D3D12_TEXTURE_COPY_TYPE_SUBRESOURCE_INDEX` は、テクスチャ側の指定に使います。`SubresourceIndex` は `ミップ番号 + 配列番号 × ミップ数` で決まる番号で、1 枚のテクスチャなら 0 です。`D3D12_TEXTURE_COPY_TYPE_PLACED_FOOTPRINT` は、バッファ側（アップロード バッファや、リードバック バッファ）の指定に使います。

したがって、アップロード バッファからテクスチャへのコピーは、`src` がバッファ（`PLACED_FOOTPRINT`）、`dst` がテクスチャ（`SUBRESOURCE_INDEX`）という組み合わせになります。`Type` と中身の組み合わせを間違えると、共用体から意味のない値を読み出して、デバッグ レイヤーのエラーになります。

```cpp
D3D12_PLACED_SUBRESOURCE_FOOTPRINT footprint = {};
UINT rows = 0;
UINT64 row_size = 0, total = 0;
D3D12_RESOURCE_DESC tex_desc = texture->GetDesc();
device->GetCopyableFootprints(&tex_desc, 0, 1, 0, &footprint, &rows, &row_size, &total);

D3D12_TEXTURE_COPY_LOCATION src = {};
src.pResource = upload_buffer.Get();
src.Type = D3D12_TEXTURE_COPY_TYPE_PLACED_FOOTPRINT;
src.PlacedFootprint = footprint;

D3D12_TEXTURE_COPY_LOCATION dst = {};
dst.pResource = texture.Get();
dst.Type = D3D12_TEXTURE_COPY_TYPE_SUBRESOURCE_INDEX;
dst.SubresourceIndex = 0;

command_list->CopyTextureRegion(&dst, 0, 0, 0, &src, nullptr);
```

!!! failure "よくあるミス"
    - `RowPitch` を `Width × 4` のまま書き込む。256 の倍数に切り上げた値を使う。
    - コピー先のテクスチャが `COPY_DEST` の状態になっていない。バリアで切り替えてからコピーする。
    - `Type` を設定せず、0（`SUBRESOURCE_INDEX`）のまま `PlacedFootprint` を書く。

## バリア

### D3D12_RESOURCE_BARRIER {#d3d12_resource_barrier}

```cpp
typedef struct D3D12_RESOURCE_BARRIER {
    D3D12_RESOURCE_BARRIER_TYPE Type;
    D3D12_RESOURCE_BARRIER_FLAGS Flags;
    union {
        D3D12_RESOURCE_TRANSITION_BARRIER Transition;
        D3D12_RESOURCE_ALIASING_BARRIER Aliasing;
        D3D12_RESOURCE_UAV_BARRIER UAV;
    };
} D3D12_RESOURCE_BARRIER;
```

GPU に「リソースの使い方を切り替える」「書き込みの終わりを待つ」と伝える構造体です。`ResourceBarrier` に配列で複数渡せます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `Type` | `D3D12_RESOURCE_BARRIER_TYPE` | `TRANSITION`、`ALIASING`、`UAV` のどれか |
| `Flags` | `D3D12_RESOURCE_BARRIER_FLAGS` | 通常は `NONE`。分割バリアに `BEGIN_ONLY`、`END_ONLY` |
| `Transition` | `D3D12_RESOURCE_TRANSITION_BARRIER` | `Type = TRANSITION` のとき |
| `UAV` | `D3D12_RESOURCE_UAV_BARRIER` | `Type = UAV` のとき |
| `Aliasing` | `D3D12_RESOURCE_ALIASING_BARRIER` | `Type = ALIASING` のとき |

`Type` を先に決めて、その種類のメンバーだけを埋めます。共用体なので、ほかのメンバーを同時に書いても意味がありません。`Type` の既定の値（0）は `TRANSITION` なので、`Type` を書き忘れても遷移バリアとして動き、気づきにくくなります。

`Flags` の `BEGIN_ONLY` と `END_ONLY` は、遷移の開始と完了を別の場所に置く「分割バリア」のためのものです。始めに `BEGIN_ONLY`、あとで `END_ONLY` を同じ内容で入れると、その間の処理と遷移を重ねられる場合があります。分かりにくいので、まず `NONE` から使います。

組み立ては、[`MakeTransitionBarrier`](../util.md#maketransitionbarrier) と [`MakeUavBarrier`](../util.md#makeuavbarrier) を使うと短くなります。

### D3D12_RESOURCE_TRANSITION_BARRIER {#d3d12_resource_transition_barrier}

```cpp
typedef struct D3D12_RESOURCE_TRANSITION_BARRIER {
    ID3D12Resource* pResource;
    UINT Subresource;
    D3D12_RESOURCE_STATES StateBefore;
    D3D12_RESOURCE_STATES StateAfter;
} D3D12_RESOURCE_TRANSITION_BARRIER;
```

リソースの状態を、`StateBefore` から `StateAfter` へ切り替えます。もっとも多く使うバリアです。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `pResource` | `ID3D12Resource*` | 対象のリソース |
| `Subresource` | `UINT` | 対象のサブリソース。全部なら `D3D12_RESOURCE_BARRIER_ALL_SUBRESOURCES` |
| `StateBefore` | `D3D12_RESOURCE_STATES` | 切り替え前の状態 |
| `StateAfter` | `D3D12_RESOURCE_STATES` | 切り替え後の状態 |

`StateBefore` は、「そのリソースが今実際にある状態」と一致させなければなりません。違っていると、デバッグ レイヤーがエラーを出し、GPU が壊れた絵を描くことがあります。スワップ チェーンのバック バッファなら、`PRESENT` から `RENDER_TARGET` へ、描いたあとで逆向きに戻す、のが定番です。

`Subresource` は、ミップや配列の特定の 1 つだけを切り替える番号です。通常は `ALL_SUBRESOURCES`（`0xffffffff`）で、全体を同時に切り替えます。

`StateBefore` と `StateAfter` が同じだとエラーになります。切り替える必要のない場面では、バリアそのものを入れません。

### D3D12_RESOURCE_UAV_BARRIER {#d3d12_resource_uav_barrier}

```cpp
typedef struct D3D12_RESOURCE_UAV_BARRIER {
    ID3D12Resource* pResource;
} D3D12_RESOURCE_UAV_BARRIER;
```

UAV へ書き込む処理の完了を待ってから、次の読み書きを始めるためのバリアです。同じ UAV に、続けて 2 回ディスパッチして、2 回目が 1 回目の結果を読むような場面で必要です。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `pResource` | `ID3D12Resource*` | 待つ対象のリソース。`nullptr` なら、すべての UAV アクセス |

状態の切り替えはなく、リソースは `UNORDERED_ACCESS` のままです。`nullptr` を渡すと、すべての UAV の書き込みを待つので、確実ですが必要以上に待つことがあります。

### D3D12_RESOURCE_ALIASING_BARRIER {#d3d12_resource_aliasing_barrier}

```cpp
typedef struct D3D12_RESOURCE_ALIASING_BARRIER {
    ID3D12Resource* pResourceBefore;
    ID3D12Resource* pResourceAfter;
} D3D12_RESOURCE_ALIASING_BARRIER;
```

`CreatePlacedResource` で同じヒープの同じ範囲に置いた複数のリソースを、使うものに切り替えるときのバリアです。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `pResourceBefore` | `ID3D12Resource*` | それまで使っていたリソース。`nullptr` なら、すべて |
| `pResourceAfter` | `ID3D12Resource*` | これから使うリソース。`nullptr` なら、すべて |

切り替えたあとのリソースの中身は決まっていません。レンダー ターゲットと深度バッファは、使う前にクリアか `DiscardResource` で初期化してください。

```cpp
// バック バッファを PRESENT → RENDER_TARGET に切り替える。
D3D12_RESOURCE_BARRIER barrier = {};
barrier.Type = D3D12_RESOURCE_BARRIER_TYPE_TRANSITION;
barrier.Flags = D3D12_RESOURCE_BARRIER_FLAG_NONE;
barrier.Transition.pResource = back_buffer;
barrier.Transition.Subresource = D3D12_RESOURCE_BARRIER_ALL_SUBRESOURCES;
barrier.Transition.StateBefore = D3D12_RESOURCE_STATE_PRESENT;
barrier.Transition.StateAfter = D3D12_RESOURCE_STATE_RENDER_TARGET;
command_list->ResourceBarrier(1, &barrier);
```

!!! failure "よくあるミス"
    - `StateBefore` が実際の状態と違う。フレームの終わりに `PRESENT` へ戻し忘れ、次のフレームで食い違う。
    - `StateBefore` と `StateAfter` が同じ。
    - `Type = UAV` なのに、`Transition` のメンバーを埋めている。
    - 同じリソースの、複数のサブリソースを別の状態に分けたまま `ALL_SUBRESOURCES` を使う。

## 関連ページ

- [ID3D12GraphicsCommandList](id3d12graphicscommandlist.md) — `ResourceBarrier` と `CopyTextureRegion`
- [ID3D12Device](id3d12device.md) — `GetCopyableFootprints`
- [Resource Barrier](../resource-barrier.md) — 状態と遷移の考え方
- [Texture Upload](../texture-upload.md) — テクスチャを GPU へ送る手順
- [Resource Structs](resource-structs.md) — `D3D12_RESOURCE_DESC` など
