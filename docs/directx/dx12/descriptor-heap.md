---
title: Descriptor Heap
tags:
  - DirectX
---

# Descriptor Heap

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>ディスクリプタ ヒープ</strong>（`ID3D12DescriptorHeap`）は <strong>ディスクリプタ</strong>（リソースの「見方」を、記述した小さなデータ）を <strong>並べて、しまっておく表</strong>です。シェーダーがテクスチャや定数バッファを読むとき GPU はこの表のディスクリプタを見て、「どのメモリをどう読むか」を知ります。D3D12 ではこの表を <strong>自分で作り管理</strong>します。

!!! tip "ポイント"
    - ヒープ ＝ ディスクリプタの配列。種類ごとに別のヒープ: <strong>CBV_SRV_UAV</strong>、<strong>SAMPLER</strong>、<strong>RTV</strong>、<strong>DSV</strong>。
    - <strong>シェーダー可視</strong>（`SHADER_VISIBLE`）にできるのは、CBV_SRV_UAV と SAMPLER だけ。RTV・DSV は CPU 側だけ。
    - ディスクリプタ 1 つの大きさは GPU ごとに違うので `GetDescriptorHandleIncrementSize` で取る。
    - 1 度にコマンド リストに設定できるシェーダー可視ヒープは、<strong>CBV_SRV_UAV と SAMPLER の 1 つずつ</strong>。
    - ヒープの大きさは作成時に決める。足りなくなったら作り直すまたは最初に大きく取る。

## 4 種類のヒープ

| `D3D12_DESCRIPTOR_HEAP_TYPE_*` | 入れるディスクリプタ | シェーダー可視 |
| --- | --- | --- |
| `CBV_SRV_UAV` | 定数バッファ（CBV）、シェーダー リソース（SRV）、UAV | 可（`SHADER_VISIBLE`） |
| `SAMPLER` | サンプラー | 可 |
| `RTV` | レンダー ターゲット ビュー | 不可（CPU 側のみ） |
| `DSV` | 深度ステンシル ビュー | 不可（CPU 側のみ） |

RTV と DSV は `OMSetRenderTargets` に CPU ハンドルを渡すだけなので、シェーダー可視は不要です。

## 作る

```cpp
// RTV 用: 3 枚ぶん。シェーダーからは見えない。
D3D12_DESCRIPTOR_HEAP_DESC rtv_desc = {};
rtv_desc.NumDescriptors = 3;
rtv_desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_RTV;
rtv_desc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_NONE;
ComPtr<ID3D12DescriptorHeap> rtv_heap;
device->CreateDescriptorHeap(&rtv_desc, IID_PPV_ARGS(&rtv_heap));

// CBV/SRV/UAV 用: 1024 個。シェーダーから見える。
D3D12_DESCRIPTOR_HEAP_DESC srv_desc = {};
srv_desc.NumDescriptors = 1024;
srv_desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV;
srv_desc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE;       // シェーダーから、見える
ComPtr<ID3D12DescriptorHeap> srv_heap;
device->CreateDescriptorHeap(&srv_desc, IID_PPV_ARGS(&srv_heap));
```

| メンバー | 内容 |
| --- | --- |
| `Type` | ヒープの種類（上の表） |
| `NumDescriptors` | ディスクリプタの数 |
| `Flags` | `NONE`、`SHADER_VISIBLE`（CBV_SRV_UAV と SAMPLER だけ） |
| `NodeMask` | マルチ GPU のとき。1 つなら 0 |

## ハンドル：ヒープの中の位置

ヒープの中のディスクリプタを指すのが <strong>ハンドル</strong>です。2 種類あります。

| ハンドル | 用途 |
| --- | --- |
| <strong>CPU ハンドル</strong>（`D3D12_CPU_DESCRIPTOR_HANDLE`） | CPU が、ディスクリプタを書き込む（`Create…View`、コピー）。RTV・DSV の束縛 |
| <strong>GPU ハンドル</strong>（`D3D12_GPU_DESCRIPTOR_HANDLE`） | GPU（シェーダー）が、読む位置。`SetGraphicsRootDescriptorTable` に渡す。シェーダー可視ヒープだけ |

```cpp
// ヒープの先頭。
D3D12_CPU_DESCRIPTOR_HANDLE cpu_start = srv_heap->GetCPUDescriptorHandleForHeapStart();
D3D12_GPU_DESCRIPTOR_HANDLE gpu_start = srv_heap->GetGPUDescriptorHandleForHeapStart();   // シェーダー可視のみ

// 1 つのディスクリプタの大きさ（GPU・種類ごとに違う）。
UINT increment = device->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV);
```

<strong>次のディスクリプタ</strong>の位置はハンドルの `ptr` に `increment` を足して、求めます。

```cpp
// i 番目のディスクリプタの CPU ハンドル。
D3D12_CPU_DESCRIPTOR_HANDLE handle = cpu_start;
handle.ptr += static_cast<SIZE_T>(i) * increment;

// d3dx12.h のヘルパーを使うと、短く書ける。
CD3DX12_CPU_DESCRIPTOR_HANDLE handle2(cpu_start, i, increment);
CD3DX12_GPU_DESCRIPTOR_HANDLE gpu_handle(gpu_start, i, increment);
```

ディスクリプタの大きさ（`increment`）は <strong>GPU によって違う</strong>（32 バイトだったり、64 バイトだったり）ので必ず `GetDescriptorHandleIncrementSize` で、取ります。決め打ちで `32` と書いてはいけません。

## ディスクリプタを書き込む

ディスクリプタは `Create…View` にハンドルを渡して、書き込みます。

```cpp
// SRV を、ヒープの i 番目に、書き込む。
D3D12_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
srv.ViewDimension = D3D12_SRV_DIMENSION_TEXTURE2D;
srv.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;    // RGBA を、そのまま
srv.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(texture.Get(), &srv, handle2);
```

ディスクリプタの種類（CBV、SRV、UAV、RTV、DSV、サンプラー）ごとの書き方は[Descriptor](descriptor.md) です。

## ヒープの使い方

### RTV・DSV：作って、ずっと使う

RTV と DSV は数が少なく、変わらないので起動時にまとめて作りそのまま使います（[Swap Chain](swap-chain.md)、[Depth Buffer](depth-buffer.md)）。

### CBV_SRV_UAV：シェーダーから見える

シェーダー可視ヒープは <strong>ディスクリプタ テーブル</strong>（ヒープの連続した範囲）としてルート シグネチャの、パラメータに結びつけます（[Root Signature](root-signature.md)）。

```cpp
// 描画の前に、シェーダー可視ヒープを、コマンド リストに設定する。
ID3D12DescriptorHeap* heaps[] = {srv_heap.Get()};
command_list->SetDescriptorHeaps(ARRAYSIZE(heaps), heaps);

// ルート パラメータ 0 の、ディスクリプタ テーブルを、ヒープの先頭から、指す。
command_list->SetGraphicsRootDescriptorTable(0, srv_heap->GetGPUDescriptorHandleForHeapStart());
```

<strong>`SetDescriptorHeaps` は重い</strong>（GPU のパイプラインが、止まる）のでフレームに 1 回だけ呼びます。複数のヒープを頻繁に切り替えるのは、避けます。

## ヒープの割り当て（アロケーター）

ヒープのどの位置が空いているかを管理する簡単なアロケーターを自作します。

```cpp
class DescriptorAllocator {
 public:
  void Init(ID3D12Device* device, D3D12_DESCRIPTOR_HEAP_TYPE type, UINT count, bool shader_visible) {
    D3D12_DESCRIPTOR_HEAP_DESC desc = {type, count,
                                       shader_visible ? D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE
                                                      : D3D12_DESCRIPTOR_HEAP_FLAG_NONE, 0};
    device->CreateDescriptorHeap(&desc, IID_PPV_ARGS(&heap_));
    increment_ = device->GetDescriptorHandleIncrementSize(type);
    cpu_start_ = heap_->GetCPUDescriptorHandleForHeapStart();
    if (shader_visible) gpu_start_ = heap_->GetGPUDescriptorHandleForHeapStart();
    capacity_ = count;
  }

  // 1 つ確保して、そのインデックスを返す（簡易。解放は、しない）。
  UINT Allocate() { return next_++; }
  D3D12_CPU_DESCRIPTOR_HANDLE Cpu(UINT i) const { return {cpu_start_.ptr + static_cast<SIZE_T>(i) * increment_}; }
  D3D12_GPU_DESCRIPTOR_HANDLE Gpu(UINT i) const { return {gpu_start_.ptr + static_cast<UINT64>(i) * increment_}; }
  ID3D12DescriptorHeap* Heap() const { return heap_.Get(); }

 private:
  ComPtr<ID3D12DescriptorHeap> heap_;
  D3D12_CPU_DESCRIPTOR_HANDLE cpu_start_ = {};
  D3D12_GPU_DESCRIPTOR_HANDLE gpu_start_ = {};
  UINT increment_ = 0, next_ = 0, capacity_ = 0;
};
```

製品では解放（フリー リスト）やフレームごとのリング（毎フレーム、動的に書いて使い捨てる領域）を足します。

## 動的なディスクリプタ

物ごとマテリアルごとに使うテクスチャが、変わるとき <strong>CPU 側のヒープ（非シェーダー可視）にディスクリプタを書いておき</strong>、描画の直前にシェーダー可視ヒープへ <strong>コピー</strong>（`CopyDescriptorsSimple`）する方法が定石です。

```cpp
// CPU 側のヒープ（シェーダー不可視）から、シェーダー可視ヒープの、使う位置へ、1 つコピーする。
device->CopyDescriptorsSimple(1,                              // 個数
                              dest_cpu_handle,                // コピー先（シェーダー可視ヒープ）
                              src_cpu_handle,                 // コピー元（CPU 側ヒープ）
                              D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV);
```

これで「テクスチャごとのディスクリプタは、一度だけ書き描画のたびにコピーするだけ」にでき `Create…View` の呼び出しを減らせます。バインドレス（`ResourceDescriptorHeap`）ではヒープ全体を 1 つの配列としてシェーダーから直接、インデックスで引きます（[Bindless](../../rendering/gpu-driven-dx12/bindless.md)）。

## よくあるミス

??? failure "`CreateDescriptorHeap` が `SHADER_VISIBLE` で、失敗する"
    RTV・DSV のヒープに `SHADER_VISIBLE` を指定している。シェーダー可視は CBV_SRV_UAV と SAMPLER だけ。

??? failure "描画で、テクスチャが真っ黒（または別のテクスチャ）"
    `SetDescriptorHeaps` を呼んでいない。ハンドルの位置（`increment`）がずれている。ディスクリプタを書き込んだヒープと設定したヒープが違う。

??? failure "ハンドルの位置が、ずれる（決め打ちの 32）"
    ディスクリプタの大きさを固定値で書いている。`GetDescriptorHandleIncrementSize` で取る。

??? failure "毎フレーム `SetDescriptorHeaps` を何度も呼んで遅い"
    GPU がヒープの切り替えで、止まる。フレームに 1 回、1 つの大きなヒープに全部、並べる。

??? failure "ヒープが、足りなくなる"
    `NumDescriptors` が小さい。最初に大きく（数千〜数万）取る。または、フレームごとのリングで使い回す。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ヒープ ＝ ディスクリプタの表。種類は CBV_SRV_UAV・SAMPLER・RTV・DSV
    - [x] シェーダー可視にできるのは、CBV_SRV_UAV と SAMPLER だけ
    - [x] 位置はハンドル（CPU / GPU）。次の位置は `GetDescriptorHandleIncrementSize` ずつ
    - [x] `SetDescriptorHeaps` はフレームに 1 回。重い
    - [x] 動的な物は CPU 側に書いて `CopyDescriptorsSimple` で可視ヒープへ

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Descriptor](descriptor.md)
- [Root Signature](root-signature.md)
- [Bindless](../../rendering/gpu-driven-dx12/bindless.md)
- [Microsoft Learn: ID3D12DescriptorHeap](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12descriptorheap)
