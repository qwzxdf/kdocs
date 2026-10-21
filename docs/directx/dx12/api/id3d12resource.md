---
title: ID3D12Resource
tags:
  - DirectX
api:
  - ID3D12Resource
---

# ID3D12Resource

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

バッファもテクスチャも GPU のメモリに置かれた物は、すべて `ID3D12Resource` です。作るのは [ID3D12Device::CreateCommittedResource](id3d12device.md#createcommittedresource) で、作ったあとにリソース自身へ呼ぶメソッドは、多くありません。CPU からデータを書き込むための `Map` と `Unmap`、GPU のアドレスを取り出す `GetGPUVirtualAddress`、作ったときの設定を調べる `GetDesc` の 4 つが中心です。

!!! tip "ポイント"
    - `Map` できるのは UPLOAD と READBACK のヒープに置いたものだけ。DEFAULT のリソースは `Map` できない。
    - UPLOAD のバッファは、`Map` したままにしておいてよい（毎フレーム `Map` し直さなくてよい）。
    - `Map` の `pReadRange` に「読まない」を伝える（`{0, 0}`）と無駄な同期を避けられる。
    - GPU アドレスを取れるのは、バッファだけ。

!!! info "このページを読む前に"
    ヒープの種類（`DEFAULT`、`UPLOAD`、`READBACK`）は [Heaps and Resources](../heaps-resources.md)、書き込み用のバッファの使い方は [Upload Buffer](../upload-buffer.md) で説明しています。

## メソッド一覧

| メソッド | 役割 |
| --- | --- |
| [`Map`](#map) | CPU からメモリを見えるようにする |
| [`Unmap`](#unmap) | CPU から見えなくする |
| [`GetGPUVirtualAddress`](#getgpuvirtualaddress) | バッファの GPU アドレスを返す |
| [`GetDesc`](#getdesc) | 作ったときの設定を返す |

## メソッド

### Map {#map}

```cpp
HRESULT ID3D12Resource::Map(
    UINT Subresource,
    const D3D12_RANGE* pReadRange,
    void** ppData);
```

リソースのメモリを CPU から読み書きできるアドレスとして取り出します。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Subresource` | `UINT` | 対象のサブリソース。バッファは `0` |
| `pReadRange` | `const D3D12_RANGE*` | CPU が読む範囲。読まないなら `{0, 0}`。`nullptr` は「全体を読むかもしれない」 |
| `ppData` | `void**` | 取り出したポインタの書き込み先 |

`pReadRange` は CPU がこのメモリを**読む**範囲を前もって伝える引数です。UPLOAD のバッファは書き込むだけなので、`D3D12_RANGE{0, 0}`（読む範囲なし）を渡します。`nullptr` を渡すと「全体を読むかもしれない」と解釈されて、デバッグ レイヤーが読んでいないのに範囲が大きすぎると指摘することがあります。READBACK のバッファを読むときは、実際に読む範囲を渡します。

`Map` できるのは UPLOAD と READBACK のヒープだけです。DEFAULT のリソースを `Map` すると失敗します。DEFAULT へデータを入れるには、いったん UPLOAD に書いて、`CopyBufferRegion` や `CopyTextureRegion` でコピーします。

返ったポインタは `Unmap` するまで有効ですが、**書き込んだ内容を GPU が読むのは、コマンドを実行するとき**です。CPU が書いたあとに GPU が読むまで待つ必要があります。同じバッファを GPU が使っている最中に CPU が上書きしないようにフレームごとにバッファを分けるのが定番です。

戻り値は成功なら `S_OK` です。DEFAULT のリソースやメモリ不足のときに失敗します。

```cpp
void* mapped = nullptr;
D3D12_RANGE read_range = {0, 0};                   // CPU は読まない（Begin = End = 0）
upload_buffer->Map(0, &read_range, &mapped);
memcpy(mapped, data, size_in_bytes);               // 書き込む
upload_buffer->Unmap(0, nullptr);
```

### Unmap {#unmap}

```cpp
void ID3D12Resource::Unmap(
    UINT Subresource,
    const D3D12_RANGE* pWrittenRange);
```

`Map` で取り出したポインタを使い終わりにします。

`pWrittenRange` は CPU が**書いた**範囲です。`nullptr` なら全体を書いたかもしれない、という意味になります。書いていないなら `{0, 0}` を渡します。`Map` ごとに `Unmap` を 1 回呼びます。

UPLOAD のバッファは `Map` したまま `Unmap` しなくても構いません。アプリの終了までずっと `Map` したままにしておき毎フレームそのポインタに書き込めば、`Map` と `Unmap` のコストが要りません。この「常時マップ」が定数バッファなどの定番のやり方です。

### GetGPUVirtualAddress {#getgpuvirtualaddress}

```cpp
D3D12_GPU_VIRTUAL_ADDRESS ID3D12Resource::GetGPUVirtualAddress();
```

バッファの GPU から見たアドレスを返します。引数はありません。

このアドレスは頂点バッファビュー（`D3D12_VERTEX_BUFFER_VIEW` の `BufferLocation`）、インデックス バッファビュー、定数バッファビュー（`D3D12_CONSTANT_BUFFER_VIEW_DESC`）、`SetGraphicsRootConstantBufferView` などで使います。バッファの途中を指したいときは返り値にオフセット（バイト）を足します。

定数バッファのアドレスは 256 バイトに頂点バッファは要素の大きさにそろえる必要があります。テクスチャのリソースには使えません（返る値は 0 です）。

### GetDesc {#getdesc}

```cpp
D3D12_RESOURCE_DESC ID3D12Resource::GetDesc();
```

リソースを作ったときの設定（種類、大きさ形式、ミップの数、フラグ）を返します。

リソースを渡された関数がその大きさや形式を知りたいときに使います。ビューを作るときにリソースの形式を引き継ぎたい場合などです。値渡しで返ってきます。

## 関連ページ

- [Heaps and Resources](../heaps-resources.md)
- [Upload Buffer](../upload-buffer.md)
- [ID3D12Device](id3d12device.md)
- [Microsoft Learn: ID3D12Resource](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12resource)
