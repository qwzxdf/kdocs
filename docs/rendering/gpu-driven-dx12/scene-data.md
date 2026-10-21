---
title: シーン データ（バッファと記述子）
tags:
  - 描画最適化
---

# シーン データ（バッファと記述子）

GPU Driven の土台は、<strong>「シーンの情報が、GPU のメモリに常駐している」</strong>ことです。このページでは、**D3D12 でそのバッファを作る**コードを示します。**デフォルト ヒープ（GPU 専用）へのアップロード**、**構造化バッファの SRV/UAV の作り方**、**毎フレーム更新するインスタンス データのリング バッファ**、**ルート シグネチャ**を扱います。

!!! tip "ポイント"
    - 常駐データは<strong>デフォルト ヒープ（GPU 専用メモリ）</strong>に置く。<strong>CPU から直接は書けない</strong>ので、<strong>アップロード ヒープ経由でコピー</strong>。
    - <strong>構造化バッファ</strong>は<strong>SRV（読み取り）</strong>と<strong>UAV（読み書き）</strong>を<strong>別々に作る</strong>。<strong>`StructureByteStride`</strong> を正しく。
    - <strong>毎フレーム変わるデータ</strong>は、<strong>フレーム数ぶんのアップロード バッファ（リング）</strong>に書く。<strong>GPU がまだ読んでいる領域を、上書きしない</strong>。
    - <strong>ルート シグネチャ</strong>は、<strong>ルート SRV/CBV（GPU アドレス直指定）</strong>を<strong>活用</strong>すると<strong>記述子テーブルが減って簡単</strong>。
    - <strong>バッファのサイズ・個数の上限</strong>（最大インスタンス数）を<strong>設計時に決める</strong>。

## バッファ作成のヘルパー

**デフォルト ヒープのバッファ**を作り、**アップロード ヒープ経由で初期データを転送**するヘルパーです。

```cpp
ComPtr<ID3D12Resource> CreateDefaultBuffer(ID3D12Device* device, uint64_t size,
                                           D3D12_RESOURCE_FLAGS flags,
                                           D3D12_RESOURCE_STATES initial_state) {
  CD3DX12_HEAP_PROPERTIES heap_properties(D3D12_HEAP_TYPE_DEFAULT);
  CD3DX12_RESOURCE_DESC desc = CD3DX12_RESOURCE_DESC::Buffer(size, flags);
  ComPtr<ID3D12Resource> buffer;
  ThrowIfFailed(device->CreateCommittedResource(&heap_properties, D3D12_HEAP_FLAG_NONE, &desc,
                                                initial_state, nullptr, IID_PPV_ARGS(&buffer)));
  return buffer;
}

ComPtr<ID3D12Resource> CreateUploadBuffer(ID3D12Device* device, uint64_t size) {
  CD3DX12_HEAP_PROPERTIES heap_properties(D3D12_HEAP_TYPE_UPLOAD);
  CD3DX12_RESOURCE_DESC desc = CD3DX12_RESOURCE_DESC::Buffer(size);
  ComPtr<ID3D12Resource> buffer;
  ThrowIfFailed(device->CreateCommittedResource(&heap_properties, D3D12_HEAP_FLAG_NONE, &desc,
                                                D3D12_RESOURCE_STATE_GENERIC_READ, nullptr,
                                                IID_PPV_ARGS(&buffer)));
  return buffer;
}
```

| 点 | 説明 |
| --- | --- |
| **`D3D12_HEAP_TYPE_DEFAULT`** | **GPU 専用メモリ**。**GPU から最速**。**CPU からはマップできない** |
| **`D3D12_HEAP_TYPE_UPLOAD`** | **CPU から書ける**（**write-combined**）。**GPU は読める**。**初期状態は `GENERIC_READ` 固定** |
| **`ALLOW_UNORDERED_ACCESS`** | **UAV で書くバッファ**に**必須のフラグ**（カリング出力など） |
| **`ThrowIfFailed`** | **`HRESULT` を検査して、例外を投げる**自前のヘルパー |

### 静的データのアップロード

**メッシュ情報・頂点・インデックス**などの**静的データ**は、**一度だけ**転送します。

```cpp
ComPtr<ID3D12Resource> UploadStaticBuffer(ID3D12Device* device, ID3D12GraphicsCommandList* list,
                                          const void* data, uint64_t size,
                                          D3D12_RESOURCE_STATES final_state,
                                          std::vector<ComPtr<ID3D12Resource>>* keep_alive) {
  ComPtr<ID3D12Resource> gpu_buffer =
      CreateDefaultBuffer(device, size, D3D12_RESOURCE_FLAG_NONE, D3D12_RESOURCE_STATE_COPY_DEST);
  ComPtr<ID3D12Resource> upload_buffer = CreateUploadBuffer(device, size);

  void* mapped = nullptr;
  CD3DX12_RANGE read_range(0, 0);
  ThrowIfFailed(upload_buffer->Map(0, &read_range, &mapped));
  std::memcpy(mapped, data, size);
  upload_buffer->Unmap(0, nullptr);

  list->CopyBufferRegion(gpu_buffer.Get(), 0, upload_buffer.Get(), 0, size);
  CD3DX12_RESOURCE_BARRIER barrier =
      CD3DX12_RESOURCE_BARRIER::Transition(gpu_buffer.Get(), D3D12_RESOURCE_STATE_COPY_DEST,
                                           final_state);
  list->ResourceBarrier(1, &barrier);

  keep_alive->push_back(std::move(upload_buffer));
  return gpu_buffer;
}
```

| 点 | 説明 |
| --- | --- |
| **`keep_alive`** | **コピーが GPU で完了するまで、アップロード バッファを解放してはいけない**。**フェンスの完了後に破棄** |
| **`Map` の `read_range(0, 0)`** | **CPU は読まない**と宣言（**不要なキャッシュ処理を避ける**） |
| **遷移** | **`COPY_DEST` → 用途の状態**（頂点・インデックス・SRV など） |

## 構造化バッファと SRV/UAV

**インスタンス・メッシュ情報**は、**`StructuredBuffer<T>`**として**HLSL から読みます**。**SRV を作る**コードです。

```cpp
void CreateStructuredBufferSrv(ID3D12Device* device, ID3D12Resource* buffer,
                               uint32_t element_count, uint32_t element_stride,
                               D3D12_CPU_DESCRIPTOR_HANDLE handle) {
  D3D12_SHADER_RESOURCE_VIEW_DESC desc = {};
  desc.Format = DXGI_FORMAT_UNKNOWN;
  desc.ViewDimension = D3D12_SRV_DIMENSION_BUFFER;
  desc.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;
  desc.Buffer.FirstElement = 0;
  desc.Buffer.NumElements = element_count;
  desc.Buffer.StructureByteStride = element_stride;
  desc.Buffer.Flags = D3D12_BUFFER_SRV_FLAG_NONE;
  device->CreateShaderResourceView(buffer, &desc, handle);
}

void CreateStructuredBufferUav(ID3D12Device* device, ID3D12Resource* buffer,
                               uint32_t element_count, uint32_t element_stride,
                               D3D12_CPU_DESCRIPTOR_HANDLE handle) {
  D3D12_UNORDERED_ACCESS_VIEW_DESC desc = {};
  desc.Format = DXGI_FORMAT_UNKNOWN;
  desc.ViewDimension = D3D12_UAV_DIMENSION_BUFFER;
  desc.Buffer.FirstElement = 0;
  desc.Buffer.NumElements = element_count;
  desc.Buffer.StructureByteStride = element_stride;
  desc.Buffer.Flags = D3D12_BUFFER_UAV_FLAG_NONE;
  device->CreateUnorderedAccessView(buffer, nullptr, &desc, handle);
}
```

| 点 | 説明 |
| --- | --- |
| **`Format = UNKNOWN`** | **構造化バッファ**は、**フォーマットを指定しない** |
| **`StructureByteStride`** | **1 要素のバイト数**（`sizeof(InstanceData)` など）。**HLSL の構造体と一致**させる |
| **UAV の第 2 引数 `nullptr`** | **カウンタ リソース**（**隠しカウンタ**）を**使わない**。**今回は、`ByteAddressBuffer` に、自前のカウンタ**を置く |

**ByteAddressBuffer**（生バッファ）の **UAV** は、**`Format = R32_TYPELESS`**・**`Buffer.Flags = D3D12_BUFFER_UAV_FLAG_RAW`**・**`NumElements` はワード（4 バイト）数**で**作ります**。

```cpp
void CreateRawBufferUav(ID3D12Device* device, ID3D12Resource* buffer, uint32_t word_count,
                        D3D12_CPU_DESCRIPTOR_HANDLE handle) {
  D3D12_UNORDERED_ACCESS_VIEW_DESC desc = {};
  desc.Format = DXGI_FORMAT_R32_TYPELESS;
  desc.ViewDimension = D3D12_UAV_DIMENSION_BUFFER;
  desc.Buffer.FirstElement = 0;
  desc.Buffer.NumElements = word_count;
  desc.Buffer.Flags = D3D12_BUFFER_UAV_FLAG_RAW;
  device->CreateUnorderedAccessView(buffer, nullptr, &desc, handle);
}
```

## 記述子ヒープ

<strong>SRV/UAV の「記述子」</strong>は、**シェーダーから見えるヒープ**（**shader-visible**）に置きます。**簡単な割り当てクラス**を示します。

```cpp
class DescriptorHeap {
 public:
  void Initialize(ID3D12Device* device, D3D12_DESCRIPTOR_HEAP_TYPE type, uint32_t capacity,
                  bool shader_visible) {
    D3D12_DESCRIPTOR_HEAP_DESC desc = {};
    desc.Type = type;
    desc.NumDescriptors = capacity;
    desc.Flags = shader_visible ? D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE
                                : D3D12_DESCRIPTOR_HEAP_FLAG_NONE;
    ThrowIfFailed(device->CreateDescriptorHeap(&desc, IID_PPV_ARGS(&heap_)));
    increment_ = device->GetDescriptorHandleIncrementSize(type);
    cpu_start_ = heap_->GetCPUDescriptorHandleForHeapStart();
    if (shader_visible) gpu_start_ = heap_->GetGPUDescriptorHandleForHeapStart();
    capacity_ = capacity;
  }

  uint32_t Allocate() {
    assert(next_ < capacity_);
    return next_++;
  }

  D3D12_CPU_DESCRIPTOR_HANDLE Cpu(uint32_t index) const {
    return CD3DX12_CPU_DESCRIPTOR_HANDLE(cpu_start_, static_cast<INT>(index), increment_);
  }

  D3D12_GPU_DESCRIPTOR_HANDLE Gpu(uint32_t index) const {
    return CD3DX12_GPU_DESCRIPTOR_HANDLE(gpu_start_, static_cast<INT>(index), increment_);
  }

  ID3D12DescriptorHeap* Get() const { return heap_.Get(); }

 private:
  ComPtr<ID3D12DescriptorHeap> heap_;
  D3D12_CPU_DESCRIPTOR_HANDLE cpu_start_ = {};
  D3D12_GPU_DESCRIPTOR_HANDLE gpu_start_ = {};
  uint32_t increment_ = 0;
  uint32_t capacity_ = 0;
  uint32_t next_ = 0;
};
```

| 点 | 説明 |
| --- | --- |
| **`GetDescriptorHandleIncrementSize`** | **記述子 1 個のバイト数**（GPU 依存）。**ハンドルを進める**のに使う |
| **シェーダー可視ヒープ** | **`SetDescriptorHeaps` でバインドできるのは、種類ごとに 1 つ**（CBV/SRV/UAV と、サンプラー） |
| **`Allocate`** | **単純な連番**。**解放して再利用する**場合は、**フリー リスト**が要る（[バインドレス](bindless.md)） |

**CBV/SRV/UAV**の**ヒープは、アプリ全体で 1 つの大きなもの**にして、**全リソースの記述子をそこに置く**のが、**GPU Driven・バインドレスの基本**です。

## フレームごとの更新：アップロード リング

**動く物体の行列**など、**毎フレーム変わるデータ**は、**CPU が書き、GPU が読みます**。**GPU は数フレーム遅れて**コマンドを実行しているので、**1 つのバッファを毎フレーム上書きすると、GPU がまだ読んでいる最中のデータを壊します**。**フレーム数（通常 2〜3）ぶんのバッファ**を**用意**し、**交互に使い**ます。

```cpp
constexpr uint32_t kFrameCount = 3;
constexpr uint32_t kMaxInstances = 262144;

struct FrameResources {
  ComPtr<ID3D12Resource> instance_upload;
  InstanceData* instance_mapped = nullptr;
  uint64_t fence_value = 0;
};

void Renderer::CreateFrameResources() {
  const uint64_t size = sizeof(InstanceData) * kMaxInstances;
  for (FrameResources& frame : frames_) {
    frame.instance_upload = CreateUploadBuffer(device_.Get(), size);
    CD3DX12_RANGE read_range(0, 0);
    ThrowIfFailed(frame.instance_upload->Map(0, &read_range,
                                             reinterpret_cast<void**>(&frame.instance_mapped)));
  }
}
```

| 点 | 説明 |
| --- | --- |
| **永続マップ** | **`Map` したまま、`Unmap` しない**。**アップロード ヒープでは、問題ない**（**毎フレーム Map/Unmap しない**） |
| **フレームごとのバッファ** | **`frames_[frame_index_]` を使う**。**そのフレームのフェンスが完了してから、再利用** |
| **`kMaxInstances`** | **最大インスタンス数**。**超えたら、書き込まない・警告**（バッファ オーバーランを防ぐ） |

### GPU 側への反映

**アップロード ヒープの内容**を、**GPU 専用のインスタンス バッファへコピー**します。

```cpp
void Renderer::UploadInstances(ID3D12GraphicsCommandList* list, uint32_t count) {
  FrameResources& frame = frames_[frame_index_];
  std::memcpy(frame.instance_mapped, cpu_instances_.data(), sizeof(InstanceData) * count);

  CD3DX12_RESOURCE_BARRIER to_copy = CD3DX12_RESOURCE_BARRIER::Transition(
      instance_buffer_.Get(), D3D12_RESOURCE_STATE_NON_PIXEL_SHADER_RESOURCE |
                                  D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE,
      D3D12_RESOURCE_STATE_COPY_DEST);
  list->ResourceBarrier(1, &to_copy);

  list->CopyBufferRegion(instance_buffer_.Get(), 0, frame.instance_upload.Get(), 0,
                         sizeof(InstanceData) * count);

  CD3DX12_RESOURCE_BARRIER to_read = CD3DX12_RESOURCE_BARRIER::Transition(
      instance_buffer_.Get(), D3D12_RESOURCE_STATE_COPY_DEST,
      D3D12_RESOURCE_STATE_NON_PIXEL_SHADER_RESOURCE | D3D12_RESOURCE_STATE_PIXEL_SHADER_RESOURCE);
  list->ResourceBarrier(1, &to_read);
}
```

| 点 | 説明 |
| --- | --- |
| **全体コピー** | **全インスタンスをコピー**する単純な形。**動く物が少ないなら、動いた範囲だけ**コピー（**ダーティ範囲**） |
| **バリアで挟む** | **SRV 状態 → コピー先 → SRV 状態**。**カリング CS が読む前に、コピーが完了**するように |
| **`NON_PIXEL_SHADER_RESOURCE`** | **コンピュート／頂点シェーダーが読む**状態。**ピクセル シェーダーも読む**なら `PIXEL_SHADER_RESOURCE` を OR する |

**動く物体が非常に少ない**なら、**変更された要素だけ**を、**CS で書き換える**（**スキャッター更新**）方法もあります。**大規模ではこれが効きます**。

## ルート シグネチャ

**カリング用**と**描画用**で**ルート シグネチャを分けます**。

### カリング用

```cpp
enum CullRoot : uint32_t {
  kCullRootConstants,
  kCullRootInstances,
  kCullRootMeshes,
  kCullRootCommands,
  kCullRootCounts,
  kCullRootCount
};

ComPtr<ID3D12RootSignature> Renderer::CreateCullRootSignature() {
  CD3DX12_ROOT_PARAMETER1 params[kCullRootCount];
  params[kCullRootConstants].InitAsConstantBufferView(0);
  params[kCullRootInstances].InitAsShaderResourceView(0);
  params[kCullRootMeshes].InitAsShaderResourceView(1);
  params[kCullRootCommands].InitAsUnorderedAccessView(0);
  params[kCullRootCounts].InitAsUnorderedAccessView(1);

  CD3DX12_VERSIONED_ROOT_SIGNATURE_DESC desc;
  desc.Init_1_1(kCullRootCount, params, 0, nullptr, D3D12_ROOT_SIGNATURE_FLAG_NONE);

  ComPtr<ID3DBlob> blob;
  ComPtr<ID3DBlob> error;
  ThrowIfFailed(D3DX12SerializeVersionedRootSignature(&desc, D3D_ROOT_SIGNATURE_VERSION_1_1,
                                                      &blob, &error));
  ComPtr<ID3D12RootSignature> root_signature;
  ThrowIfFailed(device_->CreateRootSignature(0, blob->GetBufferPointer(), blob->GetBufferSize(),
                                             IID_PPV_ARGS(&root_signature)));
  return root_signature;
}
```

| 点 | 説明 |
| --- | --- |
| **ルート CBV/SRV/UAV** | **記述子ではなく、GPU 仮想アドレスを直接**渡せる（`SetComputeRootShaderResourceView(index, address)`）。**記述子テーブル・ヒープの管理が不要** |
| **ルート SRV/UAV の制限** | **バッファのみ**（テクスチャは不可）。**`StructuredBuffer`・`ByteAddressBuffer`** は**使える**（**型付きバッファは不可**） |
| **ルート パラメータのコスト** | **ルート シグネチャは 64 ワード**まで。**CBV/SRV/UAV の GPU アドレスは 2 ワード**。**今回は 10 ワード程度**で**余裕** |
| **`kCullRootCount` の列挙** | **インデックスを名前付き定数で管理**（番号の取り違えを防ぐ） |

**カリング パス**で**ルート引数を設定**するコードは、[カリング](culling.md)で示します。

### 描画用

**描画用ルート シグネチャ**は、**`ExecuteIndirect` でルート定数を書き換える**ので、<strong>[ExecuteIndirect](execute-indirect.md)</strong> と**一緒**に示します。

## 最大数の設計

**GPU Driven では、バッファのサイズを事前に決める**必要があります（**GPU が書く量が、CPU には分からない**ため）。

| 項目 | 決め方 |
| --- | --- |
| **最大インスタンス数** | **シーンの最大の物体数**＋余裕 |
| **コマンド バッファの大きさ** | **最大インスタンス数 × `sizeof(IndirectCommand)`**（**最悪、全物体が見える**場合に備える） |
| **PSO バケットごとの最大数** | **バケット数 × バケットあたりの最大**。**超えた分は破棄**（**描かれない**） |

**メモリ**：**262,144 インスタンス × 24 バイト ≒ 6 MB**。**GPU Driven としては、軽い**です。

## よくあるミス

??? failure "アップロード バッファを、毎フレーム同じものに書いて、GPU の読み出し中に壊す"
    **フレーム数ぶんのリング**にし、**フェンスの完了を待って**から**再利用**する。

??? failure "StructureByteStride を、HLSL の構造体サイズと違う値にして、要素がずれる"
    **`static_assert(sizeof(...))` と HLSL の構造体**を**照合**する。**HLSL は 16 バイト境界のパッキング規則**がある。

??? failure "UAV を使うバッファに、ALLOW_UNORDERED_ACCESS を付け忘れる"
    **作成時のフラグ**を確認する（**`CreateUnorderedAccessView` が失敗**する）。

??? failure "コピー完了前に、アップロード バッファを解放して、クラッシュ・化ける"
    **フェンスで完了を確認**してから**解放**する（`keep_alive`）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 常駐データは<strong>デフォルト ヒープ</strong>。<strong>アップロード ヒープ経由でコピー</strong>し、<strong>遷移バリア</strong>で用途の状態へ
    - [x] <strong>構造化バッファの SRV/UAV</strong>は<strong>別々に作る</strong>。<strong>`StructureByteStride`</strong> は<strong>構造体サイズと一致</strong>
    - [x] <strong>毎フレーム更新するデータ</strong>は、<strong>フレーム数ぶんのアップロード バッファ（リング）</strong>
    - [x] <strong>ルート SRV/UAV（GPU アドレス直渡し）</strong>で、<strong>記述子の管理を減らせる</strong>
    - [x] <strong>最大数</strong>を<strong>設計時に決め</strong>、<strong>超えた分の扱い</strong>も決めておく

## 参考

- Microsoft, "Direct3D 12 Programming Guide"（Resource Binding・Descriptor Heaps）
- Microsoft, "D3D12 Memory Management"（Heap types）

## 関連ページ

- [GPU Driven（D3D12 詳細）](index.md)
- [バインドレス](bindless.md)
- [カリング](culling.md)
- [同期とデバッグ](sync-debug.md)
