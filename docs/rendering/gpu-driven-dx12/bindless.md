---
title: バインドレス（記述子の直接参照）
tags:
  - 描画最適化
---

# バインドレス（記述子の直接参照）

従来の描画では、物体を 1 つ描くたびに、CPU が「このドローはこのテクスチャ」とバインドしていました。GPU Driven では、何を描くかを決めるのがカリングのコンピュート シェーダーなので、CPU はどの物体が生き残るのか知りません。ドローの前にテクスチャをバインドしようにも、バインドする本人がいないのです。

そこで発想を逆にします。全テクスチャの記述子を 1 つの大きなヒープに並べておき、シェーダーが「ヒープの何番目」と番号で直接引きます。この方式がバインドレスです。マテリアルが持つのは、テクスチャそのものではなくテクスチャの番号です。番号なら普通のバッファに入れておけるので、GPU が自分で読んで使えます。

「結局どうバインドするのか」を先に答えると、毎ドローのバインドはゼロになり、フレームの頭で 1 回だけ、ヒープとルート シグネチャとバッファを結びます。

!!! tip "ポイント"
    - フレームの頭に結ぶのは、記述子ヒープ、ルート シグネチャ、インスタンス バッファ、マテリアル バッファの 4 つだけ。ドローごとの切り替えはない。
    - ドローごとに変わる値は、`ExecuteIndirect` がルート定数として書き込む（インスタンス番号とマテリアル番号）。
    - シェーダーは「ルート定数 → マテリアル → テクスチャ番号 → `ResourceDescriptorHeap`」とたどる。
    - SM 6.6 の `ResourceDescriptorHeap` を使うには、ルート シグネチャの専用フラグと、`SetDescriptorHeaps` を先に呼ぶ順序が要る。
    - ピクセルの中で番号が変わりうるなら `NonUniformResourceIndex` が必須。
    - 記述子を再利用するときは、GPU が使い終わるまで待つ（遅延解放）。

!!! info "このページを読む前に"
    記述子とヒープの基本は [Descriptor](../../directx/dx12/descriptor.md) と [Descriptor Heap](../../directx/dx12/descriptor-heap.md)、ルート シグネチャは [Root Signature](../../directx/dx12/root-signature.md) で説明しています。コマンドを書く側は [ExecuteIndirect](execute-indirect.md)、バッファの作り方は [シーン データ](scene-data.md) にあります。

## 発想

従来のバインド型とバインドレスの違いは、テクスチャを指定する主体が CPU か、シェーダーかという点です。

| 方式 | テクスチャの指定 | GPU Driven との相性 |
| --- | --- | --- |
| バインド型 | ドローごとに CPU がテーブルを設定する | 合わない（CPU が何を描くか知らない） |
| バインドレス | シェーダーが番号でヒープを直接引く | 合う（番号はバッファに入れておける） |

1 回の `ExecuteIndirect` で、数万個の物体を、それぞれ違うテクスチャで描くには、この方式が前提になります。

## 全体像：誰が、いつ、何を結ぶか

話がいくつもの層にまたがるので、先に全部を並べます。

1. アプリ起動時に 1 回、巨大な記述子ヒープを作ります。テクスチャを読み込むたびに、空いている番号へ SRV を書きます。
2. フレームの頭に 1 回、`SetDescriptorHeaps` でヒープを結び、ルート シグネチャを設定し、インスタンス バッファとマテリアル バッファのアドレス（ルート SRV）と、フレーム定数（ルート CBV）を設定します。
3. ドローごとの値は、`ExecuteIndirect` が引数バッファの中身をルート定数に書き込んでから描きます。CPU は何もしません。
4. シェーダーの中では、ルート定数の番号でマテリアルを引き、マテリアルのテクスチャ番号でヒープを引きます。

たとえば岩のドローなら、次のようにたどります。

| 段階 | 値 | 引く先 |
| --- | --- | --- |
| ルート定数 | `draw_material_index = 7` | `materials[7]` |
| マテリアル | `albedo_index = 215` | `ResourceDescriptorHeap[215]` |
| ヒープの 215 番 | 岩の SRV | `Sample(uv)` |

CPU が書くのは 1 と 2 だけです。3 と 4 はすべて GPU の中で完結します。

## マテリアルのデータ

マテリアルは「テクスチャの番号」を持つ構造体で、GPU バッファに置きます。

```cpp
struct MaterialData {
  uint32_t albedo_index;
  uint32_t normal_index;
  uint32_t orm_index;
  uint32_t emissive_index;
  DirectX::XMFLOAT4 base_color;
  float roughness;
  float metallic;
  uint32_t flags;
  uint32_t reserved;
};
static_assert(sizeof(MaterialData) == 48);
```

先頭の 4 つの `uint32_t` が、ヒープの番号です。`orm_index` は、Occlusion、Roughness、Metallic を 1 枚の R、G、B に詰めたテクスチャで、サンプル回数を減らすための工夫です。残りは、テクスチャがないときの係数（`base_color` など）と、分岐用のフラグです。

HLSL 側は、同じ並びで宣言します。C++ の `static_assert` とそろえておかないと、番号がずれて別のテクスチャが引かれます。

```hlsl
struct Material {
  uint albedo_index;
  uint normal_index;
  uint orm_index;
  uint emissive_index;
  float4 base_color;
  float roughness;
  float metallic;
  uint flags;
  uint reserved;
};
StructuredBuffer<Material> materials : register(t2);

static const uint kInvalidTexture = 0xFFFFFFFF;
```

`kInvalidTexture` は「テクスチャなし」を表す印です。ヒープの範囲外を引くと未定義の動作になるので、シェーダーで必ず確かめてから引きます（分岐の中で `Sample` を呼ぶ落とし穴は、後の節で説明します）。

## 記述子ヒープを作る

バインドレスの土台は、シェーダーから見える（shader-visible）CBV/SRV/UAV ヒープを 1 つ、大きく作ることです。作り方は [ID3D12Device の `CreateDescriptorHeap`](../../directx/dx12/api/id3d12device.md#createdescriptorheap) と [D3D12_DESCRIPTOR_HEAP_DESC](../../directx/dx12/api/view-structs.md#d3d12_descriptor_heap_desc) で説明しているとおりで、ここでは容量の決め方を押さえます。

```cpp
D3D12_DESCRIPTOR_HEAP_DESC heap_desc = {};
heap_desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV;
heap_desc.NumDescriptors = kBindlessCapacity;  // 例: 65536
heap_desc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE;
heap_desc.NodeMask = 0;
```

`NumDescriptors` は、ゲームで同時に読み込むテクスチャ数に余裕を見た値にします。シェーダーから見えるヒープの上限は、ResourceBindingTier によって変わります。Tier 1 と Tier 2 では 1,000,000 個までで、Tier 3 はこれを超えて確保できます。実際には数万個で足りることがほとんどなので、最初は 65536 のような値で始めます。

`Flags` の `SHADER_VISIBLE` は、このヒープをシェーダーから引くために必須です。付けないヒープは CPU が書くための置き場でしかなく、`SetDescriptorHeaps` に渡せません。

サンプラーも番号で引きたいときは、別にサンプラー ヒープを作ります。こちらの上限は 2048 個です。数種類のフィルターしか使わないなら、サンプラーは静的サンプラー（ルート シグネチャに埋め込む）で十分で、バインドレスにする必要はありません。

## 記述子を登録する

テクスチャを読み込んだら、空いている番号を 1 つもらい、その位置に SRV を書きます。番号の管理は、フリー リストで行います。

```cpp
class BindlessHeap {
 public:
  void Initialize(ID3D12Device* device, uint32_t capacity) {
    D3D12_DESCRIPTOR_HEAP_DESC desc = {};
    desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV;
    desc.NumDescriptors = capacity;
    desc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE;
    ThrowIfFailed(device->CreateDescriptorHeap(&desc, IID_PPV_ARGS(&heap_)));

    increment_ = device->GetDescriptorHandleIncrementSize(
        D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV);
    cpu_start_ = heap_->GetCPUDescriptorHandleForHeapStart();

    // 小さい番号から順に配るため、逆順に積む。
    for (uint32_t i = capacity; i > 0; --i) free_list_.push_back(i - 1);
  }
```

`GetDescriptorHandleIncrementSize` は、記述子 1 つの幅（バイト）で、GPU の種類によって違います。n 番目の位置を求めるのに使います。

```cpp
  uint32_t Register(ID3D12Device* device, ID3D12Resource* texture,
                    const D3D12_SHADER_RESOURCE_VIEW_DESC& srv) {
    assert(!free_list_.empty());
    uint32_t index = free_list_.back();
    free_list_.pop_back();
    device->CreateShaderResourceView(
        texture, &srv, OffsetHandle(cpu_start_, index, increment_));
    return index;
  }
```

`Register` は、空き番号を 1 つ取り出し、その番号の位置に SRV を書いて、番号を返します。返された番号が、`MaterialData::albedo_index` などに入ります。

SRV の記述（`D3D12_SHADER_RESOURCE_VIEW_DESC`）は、バインドレスで事故が起きやすい所です。色テクスチャの例を示します。

```cpp
D3D12_SHADER_RESOURCE_VIEW_DESC MakeColorTextureSrv(const D3D12_RESOURCE_DESC& desc) {
  D3D12_SHADER_RESOURCE_VIEW_DESC srv = {};
  srv.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
  srv.ViewDimension = D3D12_SRV_DIMENSION_TEXTURE2D;
  srv.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;
  srv.Texture2D.MostDetailedMip = 0;
  srv.Texture2D.MipLevels = desc.MipLevels;
  srv.Texture2D.PlaneSlice = 0;
  srv.Texture2D.ResourceMinLODClamp = 0.0f;
  return srv;
}
```

メンバーごとに、バインドレスでの意味を説明します。全メンバーの一般的な意味は [D3D12_SHADER_RESOURCE_VIEW_DESC](../../directx/dx12/api/view-structs.md#d3d12_shader_resource_view_desc) にあります。

`Format` は、ビューの形式です。アルベドのような色のテクスチャは `_SRGB` の形式で読みます。`_SRGB` にすると、サンプルするときにハードウェアがリニアへ変換してくれるので、シェーダーで `pow(c, 2.2)` と書く必要がなくなります。法線マップや ORM のようなデータ用のテクスチャは `_SRGB` にしてはいけません。値が曲げられてしまいます。リソースを `R8G8B8A8_TYPELESS` で作っておけば、同じリソースから `_SRGB` のビューと `_UNORM` のビューを両方作れます。

`ViewDimension` は、シェーダーでの型と一致させます。`TEXTURE2D` で作った記述子は `Texture2D` として、`TEXTURECUBE` は `TextureCube` として引きます。ヒープの番号の指す SRV の種類と、シェーダーで宣言する型が食い違うと、読み出しは未定義になります。

`Shader4ComponentMapping` は、R、G、B、A をどの成分から読むかを決めます。0 のままだと、全成分が成分 0 から読まれて、1 色の塗りつぶしに見えます。通常は `D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING` を入れます。1 チャンネルのテクスチャ（高さマップなど）を R だけでなく G、B にも広げたいときは、`D3D12_ENCODE_SHADER_4_COMPONENT_MAPPING(0, 0, 0, 1)` のように組み立てます。

`Texture2D.MostDetailedMip` と `MipLevels` は、ビューから見えるミップの範囲です。`MipLevels` に 0 を入れると作成に失敗するので、リソース側の値か、`-1`（すべて）を入れます。テクスチャ ストリーミングで、低解像度のミップしかまだ読み込んでいない場合は、`MostDetailedMip` を上げたビューを作ります。

`ResourceMinLODClamp` は、これ未満の詳細度（小さい値ほど詳細）へは下げない下限です。通常は 0 です。ストリーミング中に、読み込み前のミップを誤って引かないようにするために使います。

最後に、SRV を `nullptr` で作る方法があります。

```cpp
device->CreateShaderResourceView(texture, nullptr, handle);  // リソースの既定のビュー
```

`nullptr` を渡すと、リソースの形式と全ミップをそのまま使う既定のビューになります。ただし `TYPELESS` の形式で作ったリソースには使えません（形式が決まらないため）。バインドレスでは、`_SRGB` にするかどうかを明示したいので、`D3D12_SHADER_RESOURCE_VIEW_DESC` を渡すほうが安全です。

### 解放は遅らせる

テクスチャを捨てるとき、その番号をすぐ空き番号に戻してはいけません。GPU がまだ前のフレームの描画で、その記述子を引いているかもしれないからです。そのフレームのフェンス値を記録しておき、GPU が完了したあとで番号を返します。

```cpp
  void ScheduleRelease(uint32_t index, uint64_t fence_value) {
    pending_release_.push_back({index, fence_value});
  }

  void CollectGarbage(uint64_t completed_fence_value) {
    auto it = pending_release_.begin();
    while (it != pending_release_.end()) {
      if (it->fence_value <= completed_fence_value) {
        free_list_.push_back(it->index);
        it = pending_release_.erase(it);
      } else {
        ++it;
      }
    }
  }

  ID3D12DescriptorHeap* Get() const { return heap_.Get(); }

 private:
  struct PendingRelease {
    uint32_t index;
    uint64_t fence_value;
  };

  ComPtr<ID3D12DescriptorHeap> heap_;
  D3D12_CPU_DESCRIPTOR_HANDLE cpu_start_ = {};
  UINT increment_ = 0;
  std::vector<uint32_t> free_list_;
  std::vector<PendingRelease> pending_release_;
};
```

`ScheduleRelease` はテクスチャを破棄する側で呼び、`CollectGarbage` は毎フレームの頭で、フェンスの完了値（`ID3D12Fence::GetCompletedValue`）を渡して呼びます。

番号 0 には、白いテクスチャなどのフォールバックを必ず登録しておきます。マテリアルの番号が初期化されていなかったときでも、真っ白に見えるだけで済み、クラッシュしません。

## ルート シグネチャ

SM 6.6 の `ResourceDescriptorHeap` を使うには、ルート シグネチャにそのためのフラグを付けます。このフラグはバージョン 1.1 の記述（`D3D12_ROOT_SIGNATURE_DESC1`）で使うので、`D3D12SerializeVersionedRootSignature` で変換します。

```cpp
constexpr UINT kRootFrame = 0;      // b0: フレーム定数（ルート CBV）
constexpr UINT kRootDraw = 1;       // b1: ドローごとの定数（ExecuteIndirect が書く）
constexpr UINT kRootInstances = 2;  // t0: インスタンス バッファ（ルート SRV）
constexpr UINT kRootMaterials = 3;  // t2: マテリアル バッファ（ルート SRV）

ComPtr<ID3D12RootSignature> CreateBindlessRootSignature(ID3D12Device* device) {
  D3D12_ROOT_PARAMETER1 params[4] = {};

  params[kRootFrame].ParameterType = D3D12_ROOT_PARAMETER_TYPE_CBV;
  params[kRootFrame].Descriptor.ShaderRegister = 0;
  params[kRootFrame].Descriptor.RegisterSpace = 0;
  params[kRootFrame].Descriptor.Flags = D3D12_ROOT_DESCRIPTOR_FLAG_NONE;
  params[kRootFrame].ShaderVisibility = D3D12_SHADER_VISIBILITY_ALL;
```

ルート CBV は、定数バッファの GPU アドレスをそのまま渡す口です。記述子ヒープには何も置かないので、ヒープの番号を消費しません。

```cpp
  params[kRootDraw].ParameterType = D3D12_ROOT_PARAMETER_TYPE_32BIT_CONSTANTS;
  params[kRootDraw].Constants.ShaderRegister = 1;
  params[kRootDraw].Constants.RegisterSpace = 0;
  params[kRootDraw].Constants.Num32BitValues = 2;  // instance_index, material_index
  params[kRootDraw].ShaderVisibility = D3D12_SHADER_VISIBILITY_ALL;
```

この 32 ビット定数が、ドローごとに変わる値の入り口です。`ExecuteIndirect` がコマンドごとにここへ値を書き込みます。頂点シェーダーでもピクセル シェーダーでも読むので、`ShaderVisibility` は `ALL` にします。`PIXEL` だけにすると、頂点シェーダーからは見えません。

```cpp
  params[kRootInstances].ParameterType = D3D12_ROOT_PARAMETER_TYPE_SRV;
  params[kRootInstances].Descriptor.ShaderRegister = 0;
  params[kRootInstances].Descriptor.RegisterSpace = 0;
  params[kRootInstances].Descriptor.Flags =
      D3D12_ROOT_DESCRIPTOR_FLAG_DATA_STATIC_WHILE_SET_AT_EXECUTE;
  params[kRootInstances].ShaderVisibility = D3D12_SHADER_VISIBILITY_VERTEX;

  params[kRootMaterials].ParameterType = D3D12_ROOT_PARAMETER_TYPE_SRV;
  params[kRootMaterials].Descriptor.ShaderRegister = 2;
  params[kRootMaterials].Descriptor.RegisterSpace = 0;
  params[kRootMaterials].Descriptor.Flags =
      D3D12_ROOT_DESCRIPTOR_FLAG_DATA_STATIC_WHILE_SET_AT_EXECUTE;
  params[kRootMaterials].ShaderVisibility = D3D12_SHADER_VISIBILITY_PIXEL;
```

インスタンスとマテリアルのバッファは、ルート SRV で渡します。ルート SRV は構造化バッファか生のバッファにしか使えません（型付きのバッファは不可）。`Flags` の `DATA_STATIC_WHILE_SET_AT_EXECUTE` は、「このバッファの中身は、ルート引数として設定されている間は変わらない」とドライバーに約束する指定です。約束を守れるなら、ドライバーが最適化しやすくなります。描画中に書き換える（UAV で書く）バッファには付けられません。

```cpp
  D3D12_STATIC_SAMPLER_DESC sampler = {};
  sampler.Filter = D3D12_FILTER_ANISOTROPIC;
  sampler.AddressU = D3D12_TEXTURE_ADDRESS_MODE_WRAP;
  sampler.AddressV = D3D12_TEXTURE_ADDRESS_MODE_WRAP;
  sampler.AddressW = D3D12_TEXTURE_ADDRESS_MODE_WRAP;
  sampler.MaxAnisotropy = 8;
  sampler.ComparisonFunc = D3D12_COMPARISON_FUNC_NEVER;
  sampler.BorderColor = D3D12_STATIC_BORDER_COLOR_OPAQUE_BLACK;
  sampler.MaxLOD = D3D12_FLOAT32_MAX;
  sampler.ShaderRegister = 0;
  sampler.RegisterSpace = 0;
  sampler.ShaderVisibility = D3D12_SHADER_VISIBILITY_PIXEL;
```

サンプラーは静的サンプラーにして、ルート シグネチャに埋め込みます。ヒープの番号を使わず、サンプラー ヒープも要りません。`MaxLOD` を `D3D12_FLOAT32_MAX` にするのは、全ミップを使えるようにするためで、0 のままだと一番詳細なミップしか使われません。

```cpp
  D3D12_VERSIONED_ROOT_SIGNATURE_DESC desc = {};
  desc.Version = D3D_ROOT_SIGNATURE_VERSION_1_1;
  desc.Desc_1_1.NumParameters = _countof(params);
  desc.Desc_1_1.pParameters = params;
  desc.Desc_1_1.NumStaticSamplers = 1;
  desc.Desc_1_1.pStaticSamplers = &sampler;
  desc.Desc_1_1.Flags =
      D3D12_ROOT_SIGNATURE_FLAG_ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT |
      D3D12_ROOT_SIGNATURE_FLAG_CBV_SRV_UAV_HEAP_DIRECTLY_INDEXED;
```

ここが肝心の `Flags` です。

`CBV_SRV_UAV_HEAP_DIRECTLY_INDEXED` は、シェーダーが `ResourceDescriptorHeap[i]` で、バインドされている CBV/SRV/UAV ヒープを直接引くことを許可します。付けずに `ResourceDescriptorHeap` を使ったシェーダーで PSO を作ると、失敗します。サンプラーも番号で引くなら `SAMPLER_HEAP_DIRECTLY_INDEXED` も付けます。このページの例は静的サンプラーなので付けません。

`ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT` は、頂点バッファから頂点を読む通常のドローに必要です。メッシュ シェーダー（[メッシュレット](meshlets.md)）の経路では付けません。

```cpp
  ComPtr<ID3DBlob> blob, error;
  HRESULT hr = D3D12SerializeVersionedRootSignature(&desc, &blob, &error);
  if (FAILED(hr)) {
    if (error) OutputDebugStringA(static_cast<const char*>(error->GetBufferPointer()));
    ThrowIfFailed(hr);
  }

  ComPtr<ID3D12RootSignature> root_signature;
  ThrowIfFailed(device->CreateRootSignature(
      0, blob->GetBufferPointer(), blob->GetBufferSize(), IID_PPV_ARGS(&root_signature)));
  return root_signature;
}
```

構造体のメンバーの意味と、フラグの全種類は [Root Signature Structs](../../directx/dx12/api/root-signature-structs.md) にあります。

## フレームの頭で結ぶ

ルート シグネチャを作ったら、コマンド リストに結びつけます。順序が大事です。

```cpp
void Renderer::BeginBindless(ID3D12GraphicsCommandList* list, D3D12_GPU_VIRTUAL_ADDRESS frame_cb) {
  ID3D12DescriptorHeap* heaps[] = {bindless_.Get()};
  list->SetDescriptorHeaps(1, heaps);  // 先にヒープ
  list->SetGraphicsRootSignature(draw_root_signature_.Get());

  list->SetGraphicsRootConstantBufferView(kRootFrame, frame_cb);
  list->SetGraphicsRootShaderResourceView(kRootInstances,
                                          instance_buffer_->GetGPUVirtualAddress());
  list->SetGraphicsRootShaderResourceView(kRootMaterials,
                                          material_buffer_->GetGPUVirtualAddress());
}
```

`DIRECTLY_INDEXED` のフラグを付けたルート シグネチャは、設定する時点でヒープがバインドされている必要があります。そのため、`SetDescriptorHeaps` を `SetGraphicsRootSignature` よりも先に呼びます。順序が逆だと、デバッグ レイヤーがエラーを出します。

`SetDescriptorHeaps` に渡せるのは、CBV/SRV/UAV ヒープとサンプラー ヒープを 1 つずつです。フレームの途中で別のヒープに切り替えると、GPU のパイプラインが止まることがあります。バインドレス ヒープをフレーム全体で 1 つにして、最初に結んだら変えないのが基本です。

### ドローごとの値は ExecuteIndirect が書く

ドローごとに変わる値（ルート定数）は、コマンド シグネチャで指定して、引数バッファの中身から書き込ませます。

```cpp
struct IndirectCommand {
  uint32_t instance_index;
  uint32_t material_index;
  D3D12_DRAW_INDEXED_ARGUMENTS draw;
};
static_assert(sizeof(IndirectCommand) == 28);

ComPtr<ID3D12CommandSignature> CreateCommandSignature(ID3D12Device* device,
                                                      ID3D12RootSignature* root_signature) {
  D3D12_INDIRECT_ARGUMENT_DESC args[2] = {};
  args[0].Type = D3D12_INDIRECT_ARGUMENT_TYPE_CONSTANT;
  args[0].Constant.RootParameterIndex = kRootDraw;
  args[0].Constant.DestOffsetIn32BitValues = 0;
  args[0].Constant.Num32BitValuesToSet = 2;  // instance_index と material_index の 2 ワード
  args[1].Type = D3D12_INDIRECT_ARGUMENT_TYPE_DRAW_INDEXED;

  D3D12_COMMAND_SIGNATURE_DESC desc = {};
  desc.ByteStride = sizeof(IndirectCommand);
  desc.NumArgumentDescs = 2;
  desc.pArgumentDescs = args;

  ComPtr<ID3D12CommandSignature> signature;
  ThrowIfFailed(device->CreateCommandSignature(&desc, root_signature, IID_PPV_ARGS(&signature)));
  return signature;
}
```

`args[0]` は、コマンドの先頭 8 バイトを、ルート パラメーター `kRootDraw` の 0 番目から 2 ワードに書き込むという意味です。続く `args[1]` が、`DrawIndexedInstanced` の 20 バイトの引数です。ルート定数を書き換える引数を含むので、`CreateCommandSignature` の第 2 引数にルート シグネチャを渡す必要があります。

マテリアル番号を、インスタンス バッファから引くのではなく、コマンドに直接入れているのがここの工夫です。カリングの CS が、ドローを書くときに `instances[i].material_index` をコピーして書くだけで、シェーダーが 1 回引く手間を省けます。インスタンス番号だけを渡して、シェーダーで `instances[draw_instance_index].material_index` と引く方法でも動きます。コマンドが大きくなるのと、シェーダーの読み出しが 1 回増えるのを、天秤にかけて選びます。

描画の呼び出しは、これだけです。

```cpp
list->ExecuteIndirect(command_signature_.Get(), kMaxDraws, command_buffer_.Get(), 0,
                      count_buffer_.Get(), 0);
```

テクスチャのバインドは、1 つもありません。どのマテリアルのドローが何個あっても、この 1 行で終わります。

## シェーダーで引く

シェーダーは、ルート定数、マテリアル、ヒープの順にたどります。

```hlsl
cbuffer FrameConstants : register(b0) {
  float4x4 view_projection;
};

cbuffer DrawConstants : register(b1) {
  uint draw_instance_index;
  uint draw_material_index;
};

StructuredBuffer<Instance> instances : register(t0);
StructuredBuffer<Material> materials : register(t2);
SamplerState linear_sampler : register(s0);

struct VsOutput {
  float4 position : SV_Position;
  float3 normal : NORMAL;
  float2 uv : TEXCOORD0;
};

VsOutput VSMain(float3 position : POSITION, float3 normal : NORMAL, float2 uv : TEXCOORD0) {
  Instance instance = instances[draw_instance_index];
  VsOutput output;
  output.position = mul(mul(float4(position, 1.0), instance.world), view_projection);
  output.normal = mul(normal, (float3x3)instance.world);
  output.uv = uv;
  return output;
}
```

頂点シェーダーは、ルート定数の `draw_instance_index` でインスタンスの行列を引き、位置を変換します。マテリアル番号は頂点シェーダーから渡さなくてかまいません。ルート定数はドロー全体で同じ値なので、頂点ごとの出力に入れて補間する必要がないからです。

```hlsl
float4 PSMain(VsOutput input) : SV_Target {
  Material material = materials[draw_material_index];

  float4 albedo = material.base_color;
  if (material.albedo_index != kInvalidTexture) {
    Texture2D<float4> albedo_tex = ResourceDescriptorHeap[material.albedo_index];
    albedo *= albedo_tex.Sample(linear_sampler, input.uv);
  }
  return albedo;
}
```

ピクセル シェーダーで、`materials[draw_material_index]` からマテリアルを引き、その `albedo_index` で `ResourceDescriptorHeap` を引きます。左辺の型 `Texture2D<float4>` が、ヒープの記述子をどのビューとして解釈するかを決めます。ここで宣言した型と、登録した SRV の `ViewDimension` を一致させるのが約束です。

このシェーダーは、`ps_6_6` 以上でコンパイルします（dxc の `-T ps_6_6`）。

## 対応しているか確かめる

```cpp
D3D12_FEATURE_DATA_SHADER_MODEL shader_model = {D3D_SHADER_MODEL_6_6};
bool supports_sm66 =
    SUCCEEDED(device->CheckFeatureSupport(D3D12_FEATURE_SHADER_MODEL, &shader_model,
                                          sizeof(shader_model))) &&
    shader_model.HighestShaderModel >= D3D_SHADER_MODEL_6_6;

D3D12_FEATURE_DATA_D3D12_OPTIONS options = {};
device->CheckFeatureSupport(D3D12_FEATURE_D3D12_OPTIONS, &options, sizeof(options));
bool supports_tier3 = options.ResourceBindingTier == D3D12_RESOURCE_BINDING_TIER_3;
```

`HighestShaderModel` は、入力として渡した値が使えるかを確かめ、使える最大の値に書き換えて返す入出力のメンバーです。6.6 を入れて呼び、返ってきた値が 6.6 以上なら対応しています。ResourceBindingTier が 3 であることは、ヒープ全体を制限なく使うための条件で、SM 6.6 の直接参照を使う環境では、Tier 3 相当を前提にして設計するのが無難です。

## SM 6.6 より前：無制限の記述子テーブル

SM 6.6 が使えない環境では、ルート シグネチャに、サイズが無制限の記述子テーブルを 1 つ置きます。シェーダーでは、テクスチャの配列として宣言します。

```cpp
D3D12_DESCRIPTOR_RANGE1 range = {};
range.RangeType = D3D12_DESCRIPTOR_RANGE_TYPE_SRV;
range.NumDescriptors = UINT_MAX;  // 無制限
range.BaseShaderRegister = 0;
range.RegisterSpace = 1;  // 他の t0 と衝突させない
range.Flags = D3D12_DESCRIPTOR_RANGE_FLAG_DESCRIPTORS_VOLATILE;
range.OffsetInDescriptorsFromTableStart = D3D12_DESCRIPTOR_RANGE_OFFSET_APPEND;

D3D12_ROOT_PARAMETER1 table = {};
table.ParameterType = D3D12_ROOT_PARAMETER_TYPE_DESCRIPTOR_TABLE;
table.DescriptorTable.NumDescriptorRanges = 1;
table.DescriptorTable.pDescriptorRanges = &range;
table.ShaderVisibility = D3D12_SHADER_VISIBILITY_PIXEL;
```

```hlsl
Texture2D<float4> textures[] : register(t0, space1);

float4 c = textures[NonUniformResourceIndex(material.albedo_index)].Sample(linear_sampler, uv);
```

`NumDescriptors = UINT_MAX` は「ヒープの終わりまで」という意味の無制限です。`RegisterSpace = 1` は、他の `t0` のバインディングと衝突しないように、レジスタ空間を分けています。無制限の範囲は、その空間の `t` レジスタを全部使い切るので、同じ空間に別の SRV を置けません。

`DESCRIPTORS_VOLATILE` は、「コマンド リストの実行中に、この範囲の記述子が書き換えられるかもしれない」とドライバーに伝えます。テクスチャを後から読み込んで、空いている番号を埋めていく使い方では必要です。

ドローの前に、ヒープの先頭の GPU ハンドルを 1 回だけ渡します。

```cpp
list->SetGraphicsRootDescriptorTable(kRootTextures, bindless_.GpuStart());
```

この方式では、テクスチャの種類ごと（`Texture2D`、`TextureCube`、`Texture2DArray`）に別の空間で配列を宣言します。SM 6.6 の `ResourceDescriptorHeap` は、型を左辺で自由に決められるので、そのような分割が不要です。

## NonUniformResourceIndex

バインドレスの最大の落とし穴です。GPU は、32 個や 64 個のスレッド（レーン）を 1 つのウェーブにまとめて、同じ命令を同時に実行します。記述子の読み出しは、ウェーブ全体で同じ番号を使うことを前提に最適化されている場合があります。

1 つのウェーブの中で、レーンごとに違う番号が入りうるのに `NonUniformResourceIndex` を付けないと、動作は未定義です。たとえば、先頭のレーンの番号が全レーンに使われて、隣のピクセルに別のテクスチャが貼られます。

| 状況 | 番号は一様か |
| --- | --- |
| ドローごとのルート定数で渡したマテリアル番号 | 一様（付けなくてよい） |
| インスタンスごとにマテリアルが 1 つで、1 ドロー 1 インスタンス | ほぼ一様。実装に依存するので付けるのが安全 |
| 複数のインスタンスを 1 ドローにまとめた | 非一様 |
| ビジビリティ バッファの画素ごとのシェーディング | 非一様（必須） |

```hlsl
Texture2D<float4> tex = ResourceDescriptorHeap[NonUniformResourceIndex(material.albedo_index)];
```

付けると、ハードウェアが「ウェーブの中の異なる番号ごとにループして処理する」命令に切り替えます。番号が全レーンで同じなら、ループは 1 回で済み、ほとんど遅くなりません。番号が何種類もあるときは、その種類の数だけ繰り返すので遅くなります。判断の基準は、「同じウェーブに違う番号が入りうるか」です。迷ったら付けます。

### 分岐の中の Sample

「テクスチャがあるときだけサンプルする」と書くと、もう 1 つ別の落とし穴にはまります。

```hlsl
// 危ない: 画素ごとに条件が違うと、Sample の微分（ddx/ddy）が未定義になる。
if (material.albedo_index != kInvalidTexture) {
  albedo *= tex.Sample(linear_sampler, uv);
}
```

`Sample` は、隣のピクセルとの UV の差から、ミップ レベルを決めます。ウェーブの中で、サンプルするピクセルとしないピクセルが混ざる分岐の中では、この差が使えません。ドローごとの定数でマテリアルを決めているこのページの構成なら、分岐はドローの中で一様なので問題ありませんが、画素ごとにマテリアルが違う場合は、微分を分岐の外で先に求めて `SampleGrad` に渡します。

```hlsl
float2 dx = ddx(uv);  // 分岐の外で先に計算する
float2 dy = ddy(uv);
if (material.albedo_index != kInvalidTexture) {
  albedo *= tex.SampleGrad(linear_sampler, uv, dx, dy);
}
```

## マテリアルごとの分岐を減らす

テクスチャを番号で引けるので、マテリアルが違っても同じ PSO、同じシェーダーで描けます。マテリアルの数だけ PSO が増える心配がなくなり、PSO のバケット数（`ExecuteIndirect` の呼び出し回数）が減ります。

シェーダーを 1 本にまとめるウーバー シェーダーでは、`flags` で分岐します。バケットを分けるのは、PSO の状態が本当に違うものだけです。不透明、アルファ テスト、両面、半透明（ブレンド）の違いは、ラスタライザー ステートやブレンド ステートが違うので、PSO を分けます。

<!-- fig:bindless-index:begin -->

<svg class="fig illust motion" data-fig="bindless-index" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bindless-index" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">バインドレス: マテリアルが「テクスチャの番号」を持ち、シェーダーが番号で引く</text>
<rect x="60" y="100" width="120" height="56" fill="#ffffff" stroke="#7c3aed" stroke-width="3"/>
<text x="120" y="134" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">物体: 岩</text>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/><rect x="300" y="100" width="150" height="56" fill="#ffffff" stroke="#7c3aed" stroke-width="3"/>
<text x="375" y="134" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#7c3aed">textureIndex = 2</text>
</g>
<line x1="184" y1="128" x2="296" y2="128" stroke="#7c3aed" stroke-width="3" marker-end="url(#arr-bindless-index)" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="0;0;1;1"/></line>
<line x1="454" y1="128" x2="596" y2="252" stroke="#7c3aed" stroke-width="3" marker-end="url(#arr-bindless-index)" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1288;0.1290;1.0000" values="0;0;1;1"/></line>
<rect x="60" y="180" width="120" height="56" fill="#ffffff" stroke="#2ea043" stroke-width="3"/>
<text x="120" y="214" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">物体: 木</text>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2836;0.2839;1.0000" values="0;0;1;1"/><rect x="300" y="180" width="150" height="56" fill="#ffffff" stroke="#2ea043" stroke-width="3"/>
<text x="375" y="214" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#2ea043">textureIndex = 0</text>
</g>
<line x1="184" y1="208" x2="296" y2="208" stroke="#2ea043" stroke-width="3" marker-end="url(#arr-bindless-index)" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2836;0.2839;1.0000" values="0;0;1;1"/></line>
<line x1="454" y1="208" x2="596" y2="128" stroke="#2ea043" stroke-width="3" marker-end="url(#arr-bindless-index)" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3481;0.3484;1.0000" values="0;0;1;1"/></line>
<rect x="60" y="260" width="120" height="56" fill="#ffffff" stroke="#e5aa28" stroke-width="3"/>
<text x="120" y="294" text-anchor="middle" style="font-size:15px;font-weight:700;fill:#1f2937">物体: 壁</text>
<g opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5030;0.5032;1.0000" values="0;0;1;1"/><rect x="300" y="260" width="150" height="56" fill="#ffffff" stroke="#e5aa28" stroke-width="3"/>
<text x="375" y="294" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#e5aa28">textureIndex = 1</text>
</g>
<line x1="184" y1="288" x2="296" y2="288" stroke="#e5aa28" stroke-width="3" marker-end="url(#arr-bindless-index)" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5030;0.5032;1.0000" values="0;0;1;1"/></line>
<line x1="454" y1="288" x2="596" y2="190" stroke="#e5aa28" stroke-width="3" marker-end="url(#arr-bindless-index)" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5675;0.5677;1.0000" values="0;0;1;1"/></line>
<rect x="600" y="100" width="130" height="52" fill="#2ea043" opacity="0.9"/>
<text x="665" y="132" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">heap[0] 画像</text>
<rect x="600" y="162" width="130" height="52" fill="#e5aa28" opacity="0.9"/>
<text x="665" y="194" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">heap[1] 画像</text>
<rect x="600" y="224" width="130" height="52" fill="#7c3aed" opacity="0.9"/>
<text x="665" y="256" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ffffff">heap[2] 画像</text>
<rect x="600" y="286" width="130" height="52" fill="#cbd5e1" opacity="0.9"/>
<text x="665" y="318" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">heap[3] 画像</text>
<text x="665" y="88" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">記述子ヒープ(全テクスチャ)</text>
<text x="390" y="380" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">全テクスチャを、1 つの配列(ヒープ)に入れておく<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;1.0000" values="1;1;0;0"/></text>
<text x="390" y="380" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">岩: 番号 2 → heap[2]<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.2836;0.2839;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="380" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">木: 番号 0 → heap[0]<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2836;0.2839;0.5030;0.5032;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="380" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">壁: 番号 1 → heap[1]。物体ごとのテクスチャ切り替え命令が、要らなくなる<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5030;0.5032;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:bindless-index:end -->

## デバッグ

バインドレスは、間違えたときの症状が分かりにくい方式です。範囲外の番号を引くと、デバイスが消えることもあります。次の準備をしておくと、原因を絞り込めます。

開発中は、シェーダーで番号を範囲に収めます。`min(index, kBindlessCapacity - 1)` と書けば、クラッシュの代わりに、違うテクスチャが貼られるという目に見える症状になります。GPU-Based Validation（デバッグ レイヤーの `SetEnableGPUBasedValidation`）は、描画時に実際に引いた記述子の中身を検査してくれるので、「未初期化の番号を引いた」「型が違う」を見つけられます。PIX では、ドローごとに、ヒープのどの記述子が使われたかを見られます。

## よくあるミス

??? failure "NonUniformResourceIndex を付けず、画素ごとに違うはずのテクスチャが、全部同じになる"
    非一様な番号には、必ず `NonUniformResourceIndex` を付ける。

??? failure "ルート シグネチャに DIRECTLY_INDEXED フラグを付けず、PSO の作成に失敗する"
    `CBV_SRV_UAV_HEAP_DIRECTLY_INDEXED` を付けて、バージョン 1.1 の記述でシリアライズする。

??? failure "SetGraphicsRootSignature のあとに SetDescriptorHeaps を呼び、エラーになる"
    DIRECTLY_INDEXED のルート シグネチャは、ヒープを先に結んでから設定する。

??? failure "テクスチャを破棄した直後に番号を再利用して、別のテクスチャが一瞬映る"
    フェンスの完了を待って番号を返す（遅延解放）。

??? failure "SRV の種類（Texture2D と TextureCube など）が、シェーダーの型と合わない"
    登録時の `ViewDimension` と、シェーダーの型を一致させる。

??? failure "SRV の Shader4ComponentMapping を 0 のままにして、テクスチャが 1 色に見える"
    `D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING` を入れる。

??? failure "法線マップを _SRGB のビューで登録して、陰影がおかしい"
    色以外のデータ用のテクスチャは、`_UNORM` のビューで登録する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バインドレスは、全テクスチャの記述子を 1 つのヒープに並べ、シェーダーが番号で引く方式
    - [x] マテリアルはテクスチャの番号を持つ。ドローごとの値は `ExecuteIndirect` がルート定数として書く
    - [x] フレームの頭にバインドするのは、ヒープ、ルート シグネチャ、インスタンス、マテリアルだけ
    - [x] SM 6.6 では `ResourceDescriptorHeap[i]` と、ルート シグネチャの `DIRECTLY_INDEXED` フラグ。`SetDescriptorHeaps` が先
    - [x] 画素ごとに番号が変わりうるなら `NonUniformResourceIndex`
    - [x] 記述子の再利用は、GPU が使い終わってから

## 参考

- Microsoft, "HLSL Shader Model 6.6: Dynamic Resources"
- Microsoft, "Resource Binding in HLSL"
- Microsoft, "Root Signature Version 1.1"

## 関連ページ

- [GPU Driven（D3D12 詳細）](index.md)
- [シーン データ](scene-data.md)
- [ExecuteIndirect](execute-indirect.md)
- [ビジビリティ バッファ](../visibility-buffer.md)
- [Root Signature Structs](../../directx/dx12/api/root-signature-structs.md)
