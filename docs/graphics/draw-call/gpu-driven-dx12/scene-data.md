---
title: Scene Data
tags:
  - 描画最適化
---

# Scene Data

GPU Driven の土台は <strong>「シーンの情報が GPU のメモリに常駐している」</strong>ことです。このページでは D3D12 でそのバッファを作るコードを示します。デフォルト ヒープ（GPU 専用）へのアップロード、構造化バッファの SRV/UAV の作り方、毎フレーム更新するインスタンス データのリング バッファ、ルート シグネチャを扱います。

!!! tip "ポイント"
    - 常駐データは<strong>デフォルト ヒープ（GPU 専用メモリ）</strong>に置く。<strong>CPU から直接は書けない</strong>ので、アップロード ヒープ経由でコピー。
    - 構造化バッファはSRV（読み取り）とUAV（読み書き）を別々に作る。`StructureByteStride` を正しく。
    - 毎フレーム変わるデータは、フレーム数ぶんのアップロード バッファ（リング）に書く。GPU がまだ読んでいる領域を上書きしない。
    - ルート シグネチャはルート SRV/CBV（GPU アドレス直指定）を活用すると記述子テーブルが減って簡単。
    - バッファのサイズ・個数の上限（最大インスタンス数）を設計時に決める。

!!! info "このページを読む前に"
    - [GPU Driven Rendering](../gpu-driven.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Bottlenecks](../../optimization/bottlenecks.md)（CPU と GPU のどちらが遅いかの切り分け）

## バッファ作成のヘルパー

**デフォルト ヒープのバッファ**を作りアップロード ヒープ経由で初期データを転送するヘルパーです。

```cpp
// GPU 専用メモリ(デフォルト ヒープ)にバッファを作る。CPU からは直接書けない。
ComPtr<ID3D12Resource> CreateDefaultBuffer(ID3D12Device* device, uint64_t size,
                                           D3D12_RESOURCE_FLAGS flags,
                                           D3D12_RESOURCE_STATES initial_state) {
  D3D12_HEAP_PROPERTIES heap_properties = MakeHeapProperties(D3D12_HEAP_TYPE_DEFAULT);  // GPU 専用
  D3D12_RESOURCE_DESC desc = MakeBufferDesc(size, flags);   // size バイトのバッファ。flags で UAV などを許可する
  ComPtr<ID3D12Resource> buffer;                            // 結果
  ThrowIfFailed(device->CreateCommittedResource(&heap_properties, D3D12_HEAP_FLAG_NONE, &desc,
                                                initial_state, nullptr, IID_PPV_ARGS(&buffer)));  // バッファはクリア値が不要なので nullptr
  return buffer;
}

// CPU から書けるメモリ(アップロード ヒープ)にバッファを作る。GPU は読める。
ComPtr<ID3D12Resource> CreateUploadBuffer(ID3D12Device* device, uint64_t size) {
  D3D12_HEAP_PROPERTIES heap_properties = MakeHeapProperties(D3D12_HEAP_TYPE_UPLOAD);   // CPU が書く用
  D3D12_RESOURCE_DESC desc = MakeBufferDesc(size);          // フラグなしの普通のバッファ
  ComPtr<ID3D12Resource> buffer;
  ThrowIfFailed(device->CreateCommittedResource(&heap_properties, D3D12_HEAP_FLAG_NONE, &desc,
                                                D3D12_RESOURCE_STATE_GENERIC_READ, nullptr,  // アップロード ヒープの初期状態はこれで固定
                                                IID_PPV_ARGS(&buffer)));
  return buffer;
}
```

`CreateDefaultBuffer` で作るバッファは GPU から最速で読み書きできますが、CPU からは触れません。だから初期データを入れるには CPU が書けるアップロード ヒープのバッファを一度経由して、GPU のコピー命令で移します。このとき、アップロード側の初期状態は `GENERIC_READ` で固定です。ほかの状態で作るとエラーになります。DX12 の `d3dx12.h` の便利クラスは使わず `dx12_util.h` の `MakeHeapProperties` と `MakeBufferDesc` で構造体を埋めています。

- `D3D12_HEAP_TYPE_DEFAULT`: GPU 専用メモリ。GPU から最速。CPU からはマップできない
- `D3D12_HEAP_TYPE_UPLOAD`: CPU から書ける（write-combined）。GPU は読める。初期状態は `GENERIC_READ` 固定
- `ALLOW_UNORDERED_ACCESS`: UAV で書くバッファに必須のフラグ（カリング出力など）
- `ThrowIfFailed`: `HRESULT` を検査して例外を投げる自前のヘルパー

### 静的データのアップロード

メッシュ情報・頂点・インデックスなどの静的データは、一度だけ転送します。

```cpp
// 静的なデータを GPU 専用バッファへ 1 回だけ転送する。コピー コマンドを list に積む。
ComPtr<ID3D12Resource> UploadStaticBuffer(ID3D12Device* device, ID3D12GraphicsCommandList* list,
                                          const void* data, uint64_t size,
                                          D3D12_RESOURCE_STATES final_state,
                                          std::vector<ComPtr<ID3D12Resource>>* keep_alive) {
  ComPtr<ID3D12Resource> gpu_buffer =                       // 最終的に GPU が読むバッファ
      CreateDefaultBuffer(device, size, D3D12_RESOURCE_FLAG_NONE, D3D12_RESOURCE_STATE_COPY_DEST);  // コピーを受けるので COPY_DEST で作る
  ComPtr<ID3D12Resource> upload_buffer = CreateUploadBuffer(device, size);  // 経由用の、CPU が書けるバッファ

  void* mapped = nullptr;
  D3D12_RANGE read_range = {0, 0};                          // CPU は読まない、という宣言
  ThrowIfFailed(upload_buffer->Map(0, &read_range, &mapped));  // CPU から見えるアドレスを得る
  std::memcpy(mapped, data, size);                          // データを書き込む
  upload_buffer->Unmap(0, nullptr);                         // 書き込み終わり

  list->CopyBufferRegion(gpu_buffer.Get(), 0, upload_buffer.Get(), 0, size);  // GPU 上で、アップロード側から専用側へコピー
  D3D12_RESOURCE_BARRIER barrier =
      MakeTransitionBarrier(gpu_buffer.Get(), D3D12_RESOURCE_STATE_COPY_DEST, final_state);  // コピー先 → 使う用途の状態
  list->ResourceBarrier(1, &barrier);

  keep_alive->push_back(std::move(upload_buffer));          // コピーが終わるまで、アップロード側を生かしておく
  return gpu_buffer;
}
```

この関数はコピーを「積む」だけで、実行はしません。実行するのはコマンド リストをキューに投げたあとで、完了はフェンスで知ります。だから `upload_buffer` を関数の中で破棄すると、GPU がまだ読んでいる最中のメモリを消すことになりクラッシュや化けた描画になります。呼び出し側の `keep_alive` に預けてフェンスの完了後にまとめて捨てます。

- `keep_alive`: コピーが GPU で完了するまで、アップロード バッファを解放してはいけない。フェンスの完了後に破棄
- `Map` の `read_range(0, 0)`: CPU は読まないと宣言（不要なキャッシュ処理を避ける）
- 遷移: `COPY_DEST` → 用途の状態（頂点・インデックス・SRV など）

## 構造化バッファと SRV/UAV

**インスタンス・メッシュ情報**は、`StructuredBuffer<T>`としてHLSL から読みます。SRV を作るコードです。

```cpp
// 構造化バッファの読み取りビュー(SRV)を、handle の位置の記述子に書く。
void CreateStructuredBufferSrv(ID3D12Device* device, ID3D12Resource* buffer,
                               uint32_t element_count, uint32_t element_stride,
                               D3D12_CPU_DESCRIPTOR_HANDLE handle) {
  D3D12_SHADER_RESOURCE_VIEW_DESC desc = {};
  desc.Format = DXGI_FORMAT_UNKNOWN;                        // 構造化バッファは形式を持たない
  desc.ViewDimension = D3D12_SRV_DIMENSION_BUFFER;          // バッファのビュー
  desc.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;  // 成分の並びは既定のまま
  desc.Buffer.FirstElement = 0;                             // 先頭の要素から
  desc.Buffer.NumElements = element_count;                  // 要素の数
  desc.Buffer.StructureByteStride = element_stride;         // 1 要素のバイト数(HLSL の構造体と一致させる)
  desc.Buffer.Flags = D3D12_BUFFER_SRV_FLAG_NONE;
  device->CreateShaderResourceView(buffer, &desc, handle);
}

// 構造化バッファの読み書きビュー(UAV)。
void CreateStructuredBufferUav(ID3D12Device* device, ID3D12Resource* buffer,
                               uint32_t element_count, uint32_t element_stride,
                               D3D12_CPU_DESCRIPTOR_HANDLE handle) {
  D3D12_UNORDERED_ACCESS_VIEW_DESC desc = {};
  desc.Format = DXGI_FORMAT_UNKNOWN;                        // 構造化バッファは形式を持たない
  desc.ViewDimension = D3D12_UAV_DIMENSION_BUFFER;
  desc.Buffer.FirstElement = 0;
  desc.Buffer.NumElements = element_count;
  desc.Buffer.StructureByteStride = element_stride;         // 要素の大きさ
  desc.Buffer.Flags = D3D12_BUFFER_UAV_FLAG_NONE;
  device->CreateUnorderedAccessView(buffer, nullptr, &desc, handle);  // 2 つ目の nullptr は隠しカウンタを使わない、という意味
}
```

SRV と UAV は別のビューで、別の記述子として作ります。同じバッファをカリングの前は SRV で読みカリング中は UAV で書く、という使い分けになります。`StructureByteStride` が HLSL の `StructuredBuffer<T>` の `T` の大きさと違うと 2 つ目以降の要素の位置がずれて、意味のない値が読まれます。

- `Format = UNKNOWN`: 構造化バッファはフォーマットを指定しない
- `StructureByteStride`: 1 要素のバイト数（`sizeof(InstanceData)` など）。HLSL の構造体と一致させる
- UAV の第 2 引数 `nullptr`: カウンタ リソース（隠しカウンタ）を使わない。今回は `ByteAddressBuffer` に自前のカウンタを置く

ByteAddressBuffer（生バッファ）の UAV は、`Format = R32_TYPELESS`・`Buffer.Flags = D3D12_BUFFER_UAV_FLAG_RAW`・`NumElements` はワード（4 バイト）数で作ります。

```cpp
// ByteAddressBuffer(生バッファ)の UAV。4 バイト単位の読み書きになる。
void CreateRawBufferUav(ID3D12Device* device, ID3D12Resource* buffer, uint32_t word_count,
                        D3D12_CPU_DESCRIPTOR_HANDLE handle) {
  D3D12_UNORDERED_ACCESS_VIEW_DESC desc = {};
  desc.Format = DXGI_FORMAT_R32_TYPELESS;                   // 生バッファの決まった形式
  desc.ViewDimension = D3D12_UAV_DIMENSION_BUFFER;
  desc.Buffer.FirstElement = 0;
  desc.Buffer.NumElements = word_count;                     // 4 バイトのワードの数(バイト数ではない)
  desc.Buffer.Flags = D3D12_BUFFER_UAV_FLAG_RAW;            // 生バッファの印
  device->CreateUnorderedAccessView(buffer, nullptr, &desc, handle);
}
```

## 記述子ヒープ

<strong>SRV/UAV の「記述子」</strong>はシェーダーから見えるヒープ（shader-visible）に置きます。簡単な割り当てクラスを示します。

```cpp
class DescriptorHeap {
 public:
  void Initialize(ID3D12Device* device, D3D12_DESCRIPTOR_HEAP_TYPE type, uint32_t capacity,
                  bool shader_visible) {
    D3D12_DESCRIPTOR_HEAP_DESC desc = {};
    desc.Type = type;                                       // CBV_SRV_UAV / サンプラー / RTV / DSV
    desc.NumDescriptors = capacity;                         // 記述子の数
    desc.Flags = shader_visible ? D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE   // シェーダーから見える(GPU ハンドルを持つ)
                                : D3D12_DESCRIPTOR_HEAP_FLAG_NONE;
    ThrowIfFailed(device->CreateDescriptorHeap(&desc, IID_PPV_ARGS(&heap_)));
    increment_ = device->GetDescriptorHandleIncrementSize(type);   // 記述子 1 個の幅(GPU ごとに違う)
    cpu_start_ = heap_->GetCPUDescriptorHandleForHeapStart();      // CPU が書く側の先頭
    if (shader_visible) gpu_start_ = heap_->GetGPUDescriptorHandleForHeapStart();  // GPU が読む側の先頭
    capacity_ = capacity;
  }

  uint32_t Allocate() {                                     // 空いている番号を 1 つ返す
    assert(next_ < capacity_);                              // 容量を超えたら設計の見直し
    return next_++;
  }

  D3D12_CPU_DESCRIPTOR_HANDLE Cpu(uint32_t index) const {   // index 番目の CPU ハンドル
    return OffsetHandle(cpu_start_, index, increment_);
  }

  D3D12_GPU_DESCRIPTOR_HANDLE Gpu(uint32_t index) const {   // index 番目の GPU ハンドル
    return OffsetHandle(gpu_start_, index, increment_);
  }

  ID3D12DescriptorHeap* Get() const { return heap_.Get(); }

 private:
  ComPtr<ID3D12DescriptorHeap> heap_;
  D3D12_CPU_DESCRIPTOR_HANDLE cpu_start_ = {};
  D3D12_GPU_DESCRIPTOR_HANDLE gpu_start_ = {};
  uint32_t increment_ = 0;                                  // 1 個の幅
  uint32_t capacity_ = 0;                                   // 全体の数
  uint32_t next_ = 0;                                       // 次に渡す番号
};
```

記述子ヒープは記述子を並べておく配列のようなものです。CPU ハンドルはビューを作る（`CreateShaderResourceView` など）ときに書き込む先で、GPU ハンドルはシェーダーが読むときに `SetComputeRootDescriptorTable` などで渡す先です。同じ番号の記述子を指します。`Allocate` が返すのは番号だけでハンドルは必要なときに `Cpu` と `Gpu` で求めます。

- `GetDescriptorHandleIncrementSize`: 記述子 1 個のバイト数（GPU 依存）。ハンドルを進めるのに使う
- シェーダー可視ヒープ: `SetDescriptorHeaps` でバインドできるのは、種類ごとに 1 つ（CBV/SRV/UAV とサンプラー）
- `Allocate`: 単純な連番。解放して再利用する場合はフリー リストが要る（[バインドレス](bindless.md)）

CBV/SRV/UAVのヒープはアプリ全体で 1 つの大きなものにして、全リソースの記述子をそこに置くのが、GPU Driven・バインドレスの基本です。

## フレームごとの更新：アップロード リング

**動く物体の行列**など毎フレーム変わるデータは、CPU が書き GPU が読みます。GPU は数フレーム遅れてコマンドを実行しているので、1 つのバッファを毎フレーム上書きすると、GPU がまだ読んでいる最中のデータを壊します。フレーム数（通常 2〜3）ぶんのバッファを用意し、交互に使います。

```cpp
constexpr uint32_t kFrameCount = 3;                         // 同時に飛んでいるフレームの数
constexpr uint32_t kMaxInstances = 262144;                  // 扱えるインスタンスの上限(2 の 18 乗)

struct FrameResources {                                     // フレームごとに 1 組
  ComPtr<ID3D12Resource> instance_upload;                   // CPU が書く、そのフレーム用のバッファ
  InstanceData* instance_mapped = nullptr;                  // Map したままの CPU アドレス
  uint64_t fence_value = 0;                                 // このフレームが GPU で終わったことを示すフェンス値
};

void Renderer::CreateFrameResources() {
  const uint64_t size = sizeof(InstanceData) * kMaxInstances;   // 上限ぶんを確保する
  for (FrameResources& frame : frames_) {
    frame.instance_upload = CreateUploadBuffer(device_.Get(), size);
    D3D12_RANGE read_range = {0, 0};                        // CPU は読まない
    ThrowIfFailed(frame.instance_upload->Map(0, &read_range,
                                             reinterpret_cast<void**>(&frame.instance_mapped)));  // 永続マップ(Unmap しない)
  }
}
```

リングの考え方は倉庫の棚と同じです。CPU は今のフレームの棚に書き GPU は 1〜2 フレーム前の棚を読んでいます。棚を 3 つ用意しておけば書く棚と読まれている棚が重なりません。`fence_value` はその棚を GPU が読み終えたことを確かめるための印です。再利用する直前にフェンスの現在値がこの値以上か確かめて、足りなければ待ちます（[Synchronization and Debugging](sync-debug.md)）。

- 永続マップ: `Map` したまま `Unmap` しない。アップロード ヒープでは問題ない（毎フレーム Map/Unmap しない）
- フレームごとのバッファ: `frames_[frame_index_]` を使う。そのフレームのフェンスが完了してから再利用
- `kMaxInstances`: 最大インスタンス数。超えたら書き込まない・警告（バッファ オーバーランを防ぐ）

### GPU 側への反映

アップロード ヒープの内容を GPU 専用のインスタンス バッファへコピーします。

```cpp
void Renderer::UploadInstances(ID3D12GraphicsCommandList* list, uint32_t count) {
  FrameResources& frame = frames_[frame_index_];            // 今のフレームのバッファ(GPU が使い終わっている)
  std::memcpy(frame.instance_mapped, cpu_instances_.data(), sizeof(InstanceData) * count);  // CPU のデータをアップロード側へ

  D3D12_RESOURCE_BARRIER to_copy = MakeTransitionBarrier(   // 読み取り状態 → コピー先
      instance_buffer_.Get(), D3D12_RESOURCE_STATE_NON_PIXEL_SHADER_RESOURCE |
                                  D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE,
      D3D12_RESOURCE_STATE_COPY_DEST);
  list->ResourceBarrier(1, &to_copy);

  list->CopyBufferRegion(instance_buffer_.Get(), 0, frame.instance_upload.Get(), 0,
                         sizeof(InstanceData) * count);     // アップロード側 → GPU 専用のインスタンス バッファ

  D3D12_RESOURCE_BARRIER to_read = MakeTransitionBarrier(   // コピー先 → 読み取り状態(カリング CS が読む)
      instance_buffer_.Get(), D3D12_RESOURCE_STATE_COPY_DEST,
      D3D12_RESOURCE_STATE_NON_PIXEL_SHADER_RESOURCE | D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE);
  list->ResourceBarrier(1, &to_read);
}
```

- 全体コピー: 全インスタンスをコピーする単純な形。動く物が少ないなら動いた範囲だけコピー（ダーティ範囲）
- バリアで挟む: SRV 状態 → コピー先 → SRV 状態。カリング CS が読む前にコピーが完了するように
- `NON_PIXEL_SHADER_RESOURCE`: コンピュート／頂点シェーダーが読む状態。ピクセル シェーダーも読むなら `PIXEL_SHADER_RESOURCE` を OR する

動く物体が少ないなら変更された要素だけを CS で書き換える（スキャッター更新）方法もあります。大規模ではこれが効きます。

## ルート シグネチャ

**カリング用**と描画用でルート シグネチャを分けます。

### カリング用

```cpp
enum CullRoot : uint32_t {                                  // ルート パラメーターの番号(名前で管理する)
  kCullRootConstants,                                       // 0: 定数バッファ(視錐台など)
  kCullRootInstances,                                       // 1: インスタンスの SRV
  kCullRootMeshes,                                          // 2: メッシュ表の SRV
  kCullRootCommands,                                        // 3: コマンドの UAV
  kCullRootCounts,                                          // 4: カウンタの UAV
  kCullRootCount                                            // 個数
};

ComPtr<ID3D12RootSignature> Renderer::CreateCullRootSignature() {
  D3D12_ROOT_PARAMETER1 params[kCullRootCount] = {};        // 5 つとも「GPU アドレスを直接渡すルート記述子」
  auto init_root_descriptor = [&params](uint32_t index, D3D12_ROOT_PARAMETER_TYPE type, uint32_t reg) {
    params[index].ParameterType = type;                     // CBV / SRV / UAV のどれか
    params[index].Descriptor.ShaderRegister = reg;          // b0 / t0 / u0 などの番号
    params[index].Descriptor.RegisterSpace = 0;
    params[index].Descriptor.Flags = D3D12_ROOT_DESCRIPTOR_FLAG_NONE;
    params[index].ShaderVisibility = D3D12_SHADER_VISIBILITY_ALL;
  };
  init_root_descriptor(kCullRootConstants, D3D12_ROOT_PARAMETER_TYPE_CBV, 0);   // b0
  init_root_descriptor(kCullRootInstances, D3D12_ROOT_PARAMETER_TYPE_SRV, 0);   // t0
  init_root_descriptor(kCullRootMeshes, D3D12_ROOT_PARAMETER_TYPE_SRV, 1);      // t1
  init_root_descriptor(kCullRootCommands, D3D12_ROOT_PARAMETER_TYPE_UAV, 0);    // u0
  init_root_descriptor(kCullRootCounts, D3D12_ROOT_PARAMETER_TYPE_UAV, 1);      // u1

  D3D12_VERSIONED_ROOT_SIGNATURE_DESC desc = {};
  desc.Version = D3D_ROOT_SIGNATURE_VERSION_1_1;
  desc.Desc_1_1.NumParameters = kCullRootCount;
  desc.Desc_1_1.pParameters = params;
  desc.Desc_1_1.Flags = D3D12_ROOT_SIGNATURE_FLAG_NONE;     // コンピュート専用なので入力アセンブラーのフラグは不要

  ComPtr<ID3DBlob> blob;                                    // シリアライズ結果
  ComPtr<ID3DBlob> error;                                   // 失敗したときのメッセージ
  ThrowIfFailed(D3D12SerializeVersionedRootSignature(&desc, &blob, &error));
  ComPtr<ID3D12RootSignature> root_signature;
  ThrowIfFailed(device_->CreateRootSignature(0, blob->GetBufferPointer(), blob->GetBufferSize(),
                                             IID_PPV_ARGS(&root_signature)));
  return root_signature;
}
```

ここでは、5 つのパラメーターを全部「ルート記述子」で作っています。記述子ヒープにビューを作らなくても、バッファの GPU アドレスを `SetComputeRoot…View` で直接渡せる仕組みです。手間は減りますが型付きバッファやテクスチャには使えません。`d3dx12.h` の `CD3DX12_ROOT_PARAMETER1` は使わず `D3D12_ROOT_PARAMETER1` を直接埋めています（共通部分は `init_root_descriptor` にまとめました）。

- ルート CBV/SRV/UAV: 記述子ではなく、GPU 仮想アドレスを直接渡せる（`SetComputeRootShaderResourceView(index, address)`）。記述子テーブル・ヒープの管理が不要
- ルート SRV/UAV の制限: バッファのみ（テクスチャは不可）。`StructuredBuffer`・`ByteAddressBuffer` は使える（型付きバッファは不可）
- ルート パラメータのコスト: ルート シグネチャは 64 ワードまで。CBV/SRV/UAV の GPU アドレスは 2 ワード。今回は 10 ワード程度で余裕
- `kCullRootCount` の列挙: インデックスを名前付き定数で管理（番号の取り違えを防ぐ）

カリング パスでルート引数を設定するコードは、[カリング](culling.md)で示します。

### 描画用

描画用ルート シグネチャは `ExecuteIndirect` でルート定数を書き換えるので、[ExecuteIndirect](execute-indirect.md) と一緒に示します。

## 最大数の設計

**GPU Driven ではバッファのサイズを事前に決める**必要があります（GPU が書く量が CPU には分からないため）。

- 最大インスタンス数: シーンの最大の物体数＋余裕
- コマンド バッファの大きさ: 最大インスタンス数 × `sizeof(IndirectCommand)`（最悪、全物体が見える場合に備える）
- PSO バケットごとの最大数: バケット数 × バケットあたりの最大。超えた分は破棄（描かれない）

メモリ：262,144 インスタンス × 24 バイト ≒ 6 MB。GPU Driven としては軽いです。

## よくあるミス

??? failure "アップロード バッファを毎フレーム同じものに書いて、GPU の読み出し中に壊す"
    **フレーム数ぶんのリング**にし、フェンスの完了を待ってから再利用する。

??? failure "StructureByteStride を HLSL の構造体サイズと違う値にして、要素がずれる"
    `static_assert(sizeof(...))` と HLSL の構造体を照合する。HLSL は 16 バイト境界のパッキング規則がある。

??? failure "UAV を使うバッファに ALLOW_UNORDERED_ACCESS を付け忘れる"
    作成時のフラグを確認する（`CreateUnorderedAccessView` が失敗する）。

??? failure "コピー完了前にアップロード バッファを解放して、クラッシュ・化ける"
    フェンスで完了を確認してから解放する（`keep_alive`）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 常駐データは<strong>デフォルト ヒープ</strong>。アップロード ヒープ経由でコピーし、遷移バリアで用途の状態へ
    - [x] 構造化バッファの SRV/UAVは別々に作る。`StructureByteStride` は構造体サイズと一致
    - [x] 毎フレーム更新するデータは、フレーム数ぶんのアップロード バッファ（リング）
    - [x] ルート SRV/UAV（GPU アドレス直渡し）で、記述子の管理を減らせる
    - [x] 最大数を設計時に決め超えた分の扱いも決めておく

## 参考

- Microsoft, "Direct3D 12 Programming Guide"（Resource Binding・Descriptor Heaps）
- Microsoft, "D3D12 Memory Management"（Heap types）

## 関連ページ

- [GPU Driven (D3D12)](index.md)
- [バインドレス](bindless.md)
- [カリング](culling.md)
- [Synchronization and Debugging](sync-debug.md)
