---
title: IDXGIAdapter
tags:
  - DirectX
api:
  - IDXGIAdapter1
  - IDXGIAdapter3
---

# IDXGIAdapter

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">DXGI</span>
`#include <dxgi1_6.h>`
</div>

PC には GPU が複数載っていることがあります。ノート PC なら内蔵 GPU と外付け GPU、デスクトップなら加えて CPU が描く WARP です。デバイスを作る前に「どれを使うか」を決めるために、GPU 1 つを表すのがアダプター（`IDXGIAdapter1`）です。

アダプターでできることは 2 つあります。名前や種類を調べて選ぶこと（`GetDesc1`）と、その GPU のメモリがどれだけ使えるかを調べること（`QueryVideoMemoryInfo`）です。後者は `IDXGIAdapter3` にあります。VRAM の使いすぎを避けるために、ゲームが自分で確認します。

!!! tip "ポイント"
    - アダプターは `EnumAdapterByGpuPreference` で取り出し、`D3D12CreateDevice` に渡す。
    - `GetDesc1` の `Flags` に `DXGI_ADAPTER_FLAG_SOFTWARE` があれば WARP。
    - `QueryVideoMemoryInfo` の `Budget` を超える使い方をすると、OS が他のメモリへ追い出して急に遅くなる。
    - `IDXGIAdapter3` は `As` で取り出す。

!!! info "このページを読む前に"
    アダプターを列挙して選ぶ流れは [Device and Factory](../factory-device.md) にあります。取り出したアダプターを作るのは [IDXGIFactory](idxgifactory.md) です。

## メソッド一覧

| メソッド | 役割 |
| --- | --- |
| [`GetDesc1`](../factory-device.md#getdesc1) | 名前、メーカー、専用メモリの大きさ、種類を調べる |
| [`QueryVideoMemoryInfo`](#queryvideomemoryinfo) | メモリの予算と、いまの使用量を調べる |

## メソッドの詳しい説明

`GetDesc1` は [Device and Factory](../factory-device.md#getdesc1) で説明しているので、ここでは `IDXGIAdapter3` のメソッドを見ます。

### QueryVideoMemoryInfo {#queryvideomemoryinfo}

```cpp
HRESULT IDXGIAdapter3::QueryVideoMemoryInfo(
    UINT NodeIndex,
    DXGI_MEMORY_SEGMENT_GROUP MemorySegmentGroup,
    DXGI_QUERY_VIDEO_MEMORY_INFO* pVideoMemoryInfo);
```

GPU が使えるメモリの予算と、アプリがいま使っている量を調べます。VRAM の使いすぎを実行時に見張る用途です。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `NodeIndex` | `UINT` | GPU のノード番号。GPU が 1 つのアダプターなら 0 |
| `MemorySegmentGroup` | `DXGI_MEMORY_SEGMENT_GROUP` | どちらのメモリを調べるか（下の表） |
| `pVideoMemoryInfo` | `DXGI_QUERY_VIDEO_MEMORY_INFO*` | 結果を書き込む構造体 |

`NodeIndex` は、リンクした複数の GPU を 1 つのアダプターとして扱う構成（SLI のような構成）で、その中のどの GPU かを選ぶ番号です。普通の PC では GPU は 1 ノードだけなので 0 を渡します。

`MemorySegmentGroup` は 2 つから選びます。

| 値 | 意味 |
| --- | --- |
| `DXGI_MEMORY_SEGMENT_GROUP_LOCAL` | GPU に近いメモリ。外付け GPU なら VRAM。内蔵 GPU ならシステム メモリのうち GPU 用に確保された部分 |
| `DXGI_MEMORY_SEGMENT_GROUP_NON_LOCAL` | GPU から遠いメモリ。外付け GPU から見たシステム メモリ |

ゲームがテクスチャやバッファを置く場所は、まず `LOCAL` です。外付け GPU で VRAM が足りなくなるとリソースは `NON_LOCAL`（システム メモリ）へ追い出され、PCI Express 経由の遅いアクセスになります。そのため見張るのは `LOCAL` が中心です。

結果の `DXGI_QUERY_VIDEO_MEMORY_INFO` には、4 つの値が入ります。

| 項目 | 意味 |
| --- | --- |
| `Budget` | OS がこのアプリに割り当てた使用量の目安（バイト）。他のアプリの使用量によって上下する |
| `CurrentUsage` | このアプリがいま使っている量 |
| `AvailableForReservation` | 予約（`SetVideoMemoryReservation`）できる最大量 |
| `CurrentReservation` | いま予約している量 |

見るのは `Budget` と `CurrentUsage` です。`CurrentUsage` が `Budget` を超えると、OS が一部を追い出し始めてフレームが急に遅くなります。そのため、`CurrentUsage` が `Budget` に近づいたら、テクスチャの解像度を落とす、使っていないリソースを手放す、といった対応をします。`Budget` は固定の値ではありません。ほかのアプリがメモリを使うと小さくなるので、毎フレームか数フレームに 1 回、調べ直します。

```cpp
ComPtr<IDXGIAdapter3> adapter3;
adapter.As(&adapter3);

DXGI_QUERY_VIDEO_MEMORY_INFO info = {};
adapter3->QueryVideoMemoryInfo(0, DXGI_MEMORY_SEGMENT_GROUP_LOCAL, &info);
if (info.CurrentUsage > info.Budget * 9 / 10) {
  // 予算の 9 割を超えた。解像度を落とす、古いリソースを手放す、など
}
```

戻り値は成功なら `S_OK` です。`NodeIndex` や `MemorySegmentGroup` に存在しない値を渡すと失敗します。`IDXGIAdapter3` は Windows 10 から使えます。

## 関連ページ

- [Device and Factory](../factory-device.md)
- [IDXGIFactory](idxgifactory.md)
- [Microsoft Learn: IDXGIAdapter3](https://learn.microsoft.com/ja-jp/windows/win32/api/dxgi1_4/nn-dxgi1_4-idxgiadapter3)
