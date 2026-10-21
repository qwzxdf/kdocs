---
title: Descriptor Heap
tags:
  - DirectX
---

# Descriptor Heap

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

シェーダーでテクスチャを読むとき GPU は「そのテクスチャが、メモリのどこにあってどんな形式で、何ピクセル四方なのか」を知る必要があります。この「見方」を書いた小さなデータが、<strong>ディスクリプタ</strong>です。そして、ディスクリプタを並べて置いておく表が、<strong>ディスクリプタ ヒープ</strong>（`ID3D12DescriptorHeap`）です。

D3D11 ではこの表をドライバーが裏で管理してくれました。D3D12 では表を自分で作って、自分で中身を書きます。そのぶん描画のたびにテクスチャを結び直す必要がなくなり表の中の場所を伝えるだけで済むようになります。

!!! tip "ポイント"
    - ヒープはディスクリプタの配列。種類ごとに別のヒープで CBV_SRV_UAV、SAMPLER、RTV、DSV の 4 つがある。
    - シェーダーから見える（`SHADER_VISIBLE`）ようにできるのは、CBV_SRV_UAV と SAMPLER だけ。
    - ディスクリプタ 1 つの幅は GPU ごとに違うので、`GetDescriptorHandleIncrementSize` で取る。
    - コマンド リストに同時に設定できるシェーダー可視ヒープは、CBV_SRV_UAV と SAMPLER の 1 つずつ。
    - ヒープの大きさは作るときに決める。足りなくなったら作り直すので、最初に大きめに取る。

!!! info "このページを読む前に"
    ディスクリプタが何を書いたものかは [Descriptor](descriptor.md) で説明しています。このページはそれを並べる「ヒープ」の話です。ヒープを作る `CreateDescriptorHeap` は [ID3D12Device](api/id3d12device.md#createdescriptorheap)、先頭のハンドルを取るメソッドは [ID3D12DescriptorHeap](api/id3d12descriptorheap.md) にあります。

## 4 種類のヒープ

ヒープは入れるディスクリプタの種類ごとに別々です。種類を混ぜることはできません。

`CBV_SRV_UAV` のヒープには定数バッファ（CBV）、シェーダーが読むリソース（SRV）、シェーダーが読み書きするリソース（UAV）の 3 種類を混ぜて入れられます。この 3 つは同じ大きさでひとつのヒープに並びます。`SAMPLER` のヒープにはサンプラー（テクスチャの読み方）を入れます。

`RTV` は描き込み先、`DSV` は深度バッファの見方です。この 2 つはシェーダーが直接読むものではなく、`OMSetRenderTargets` にハンドルを渡すだけで使います。そのため、シェーダーから見える設定は不要で、付けることもできません。

## ヒープを作る

```cpp
// RTV 用。3 枚ぶん。シェーダーからは見えない。
D3D12_DESCRIPTOR_HEAP_DESC rtv_desc = {};
rtv_desc.NumDescriptors = 3;
rtv_desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_RTV;
rtv_desc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_NONE;
ComPtr<ID3D12DescriptorHeap> rtv_heap;
device->CreateDescriptorHeap(&rtv_desc, IID_PPV_ARGS(&rtv_heap));

// CBV/SRV/UAV 用。1024 個。シェーダーから見える。
D3D12_DESCRIPTOR_HEAP_DESC srv_desc = {};
srv_desc.NumDescriptors = 1024;
srv_desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV;
srv_desc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE;
ComPtr<ID3D12DescriptorHeap> srv_heap;
device->CreateDescriptorHeap(&srv_desc, IID_PPV_ARGS(&srv_heap));
```

`D3D12_DESCRIPTOR_HEAP_DESC` の 4 つのメンバーのうち考える必要があるのは 3 つです。

`Type` は入れるディスクリプタの種類です。作ったあとで変えられません。

`NumDescriptors` はヒープの大きさ（ディスクリプタの数）です。作ったあとで増やせません。足りなくなると作り直してコピーするしかないので、最初に余裕を持たせます。テクスチャをたくさん使うゲームでは数千から数万個を取ることもあります。

`Flags` は `NONE` か `SHADER_VISIBLE` です。`SHADER_VISIBLE` のヒープはシェーダーから読めるようになる代わりに CPU からは書き込み専用の扱いになります。`NodeMask` は複数の GPU を使うときの指定で、普通は `0` です。

## ハンドルでヒープの中の位置を指す

ヒープの中の 1 つのディスクリプタは、**ハンドル**で指します。ハンドルは 2 種類あります。

CPU ハンドル（`D3D12_CPU_DESCRIPTOR_HANDLE`）は CPU がディスクリプタを書き込むときに使います。`CreateXxxView` の最後の引数や `OMSetRenderTargets` に渡すのは、こちらです。GPU ハンドル（`D3D12_GPU_DESCRIPTOR_HANDLE`）は GPU のシェーダーが読む位置を教えるときに使います。`SetGraphicsRootDescriptorTable` に渡すのはこちらです。シェーダー可視のヒープからしか取れません。

2 つのハンドルは同じ位置を指していても、数値が違います。片方をもう片方の引数に渡すとクラッシュします。型が別なので取り違えるとコンパイル時に分かります。

```cpp
// ヒープの先頭。
D3D12_CPU_DESCRIPTOR_HANDLE cpu_start = srv_heap->GetCPUDescriptorHandleForHeapStart();
D3D12_GPU_DESCRIPTOR_HANDLE gpu_start = srv_heap->GetGPUDescriptorHandleForHeapStart();  // シェーダー可視のみ

// ディスクリプタ 1 つの幅（GPU と種類によって違う）。
UINT increment = device->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV);

// i 番目のディスクリプタのハンドル。
D3D12_CPU_DESCRIPTOR_HANDLE cpu_i = OffsetHandle(cpu_start, i, increment);
D3D12_GPU_DESCRIPTOR_HANDLE gpu_i = OffsetHandle(gpu_start, i, increment);
```

ハンドルの中身は `ptr` という整数 1 つだけです。次のディスクリプタの位置は `ptr` に幅（`increment`）を足せば求まります。`OffsetHandle` はその足し算を関数にしたものです（[Helper Functions](util.md#offsethandle)）。

`increment` は GPU によって違います（32 バイトだったり 64 バイトだったりします）。決め打ちで `32` と書くとほかの GPU で位置がずれます。必ず `GetDescriptorHandleIncrementSize` で調べます。

## ディスクリプタを書き込む

ディスクリプタは `CreateXxxView` にハンドルを渡して書き込みます。

```cpp
// SRV を、ヒープの i 番目に書き込む。
D3D12_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
srv.ViewDimension = D3D12_SRV_DIMENSION_TEXTURE2D;
srv.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;  // RGBA をそのまま
srv.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(texture.Get(), &srv, cpu_i);
```

どのビューに何を書くかは[Descriptor](descriptor.md) と [ID3D12Device](api/id3d12device.md) の `CreateXxxView` にあります。

## ヒープの使い方

RTV と DSV のヒープは数が少なく、あまり変わりません。起動時にまとめて作ってそのまま使い続けます（[Swap Chain](swap-chain.md)、[Depth Buffer](depth-buffer.md)）。

CBV_SRV_UAV のヒープはシェーダーから見える**ディスクリプタ テーブル**として使います。ヒープの連続した範囲をルート シグネチャのパラメーターに結びます（[Root Signature](root-signature.md)）。

```cpp
// 描画の前に、シェーダー可視ヒープをコマンド リストに設定する。
ID3D12DescriptorHeap* heaps[] = {srv_heap.Get()};
command_list->SetDescriptorHeaps(ARRAYSIZE(heaps), heaps);

// ルート パラメーター 0 のテーブルを、ヒープの先頭から指す。
command_list->SetGraphicsRootDescriptorTable(0, srv_heap->GetGPUDescriptorHandleForHeapStart());
```

`SetDescriptorHeaps` は GPU のパイプラインを止めることがある重い命令です。1 フレームに 1 回だけ呼びます。複数のヒープを頻繁に切り替えるのは避けて、1 つの大きなヒープに全部を並べます。

## ヒープの空きを管理する

ヒープのどの位置が空いているかは自分で管理します。最小の例を示します。

```cpp
class DescriptorAllocator {
 public:
  void Init(ID3D12Device* device, D3D12_DESCRIPTOR_HEAP_TYPE type, UINT count, bool shader_visible) {
    D3D12_DESCRIPTOR_HEAP_DESC desc = {};
    desc.Type = type;
    desc.NumDescriptors = count;
    desc.Flags = shader_visible ? D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE : D3D12_DESCRIPTOR_HEAP_FLAG_NONE;
    device->CreateDescriptorHeap(&desc, IID_PPV_ARGS(&heap_));
    increment_ = device->GetDescriptorHandleIncrementSize(type);
    cpu_start_ = heap_->GetCPUDescriptorHandleForHeapStart();
    if (shader_visible) gpu_start_ = heap_->GetGPUDescriptorHandleForHeapStart();
  }

  // 1 つ確保して、その番号を返す（簡易版。解放はしない）。
  UINT Allocate() { return next_++; }
  D3D12_CPU_DESCRIPTOR_HANDLE Cpu(UINT i) const { return OffsetHandle(cpu_start_, i, increment_); }
  D3D12_GPU_DESCRIPTOR_HANDLE Gpu(UINT i) const { return OffsetHandle(gpu_start_, i, increment_); }
  ID3D12DescriptorHeap* Heap() const { return heap_.Get(); }

 private:
  ComPtr<ID3D12DescriptorHeap> heap_;
  D3D12_CPU_DESCRIPTOR_HANDLE cpu_start_ = {};
  D3D12_GPU_DESCRIPTOR_HANDLE gpu_start_ = {};
  UINT increment_ = 0;
  UINT next_ = 0;
};
```

製品では解放の仕組み（フリー リスト）やフレームごとに使い捨てる領域（リング）を足します。

## 動的に変わるディスクリプタ

物ごとマテリアルごとに使うテクスチャが変わるときは、先に CPU 側のヒープ（シェーダー不可視）にディスクリプタを書いておきます。そして、描画の直前にシェーダー可視のヒープへコピーするのが定石です。

```cpp
// CPU 側のヒープから、シェーダー可視ヒープの使う位置へ、1 つコピーする。
device->CopyDescriptorsSimple(1,                // 個数
                              dest_cpu_handle,  // コピー先（シェーダー可視ヒープ）
                              src_cpu_handle,   // コピー元（CPU 側のヒープ）
                              D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV);
```

こうするとテクスチャごとのディスクリプタは一度だけ書けば済み `CreateXxxView` の呼び出しを減らせます。バインドレスではヒープ全体を 1 つの配列として、シェーダーが番号で直接引きます（[Bindless](../../rendering/gpu-driven-dx12/bindless.md)）。

## よくあるミス

??? failure "`CreateDescriptorHeap` が `SHADER_VISIBLE` で失敗する"
    RTV か DSV のヒープに `SHADER_VISIBLE` を指定しています。シェーダー可視にできるのは CBV_SRV_UAV と SAMPLER だけです。

??? failure "描画でテクスチャが真っ黒になる（または別のテクスチャになる）"
    `SetDescriptorHeaps` を呼んでいないハンドルの位置（`increment`）がずれている、ディスクリプタを書き込んだヒープと設定したヒープが違うのどれかです。

??? failure "ハンドルの位置がずれる（決め打ちの 32）"
    ディスクリプタの幅を固定値で書いています。`GetDescriptorHandleIncrementSize` で調べます。

??? failure "毎フレーム `SetDescriptorHeaps` を何度も呼んで遅い"
    ヒープの切り替えで GPU が止まります。フレームに 1 回、1 つの大きなヒープに全部を並べます。

??? failure "ヒープが足りなくなる"
    `NumDescriptors` が小さすぎます。最初に大きく（数千から数万）取るかフレームごとのリングで使い回します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ヒープはディスクリプタの表。種類は CBV_SRV_UAV、SAMPLER、RTV、DSV
    - [x] シェーダー可視にできるのは、CBV_SRV_UAV と SAMPLER だけ
    - [x] 位置はハンドル（CPU と GPU）。次の位置は `GetDescriptorHandleIncrementSize` ずつ進む
    - [x] `SetDescriptorHeaps` は 1 フレームに 1 回。重い
    - [x] 動的なものは CPU 側に書いて、`CopyDescriptorsSimple` で可視ヒープへ

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Descriptor](descriptor.md)
- [ID3D12DescriptorHeap](api/id3d12descriptorheap.md)
- [Root Signature](root-signature.md)
- [Bindless](../../rendering/gpu-driven-dx12/bindless.md)
- [Microsoft Learn: ID3D12DescriptorHeap](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12descriptorheap)
