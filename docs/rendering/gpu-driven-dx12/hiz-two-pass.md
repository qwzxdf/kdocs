---
title: Hi-Z と 2 パス オクルージョン カリング
tags:
  - 描画最適化
---

# Hi-Z と 2 パス オクルージョン カリング

視錐台カリングは、<strong>「画面の外」</strong>の物を消します。<strong>「画面の中だが他の物の陰に隠れている」</strong>物は**オクルージョン カリング**で消します。GPU Driven では、**前フレームまたは今フレームの深度から、Hi-Z（階層的な深度ピラミッド）を作り**、**コンピュート シェーダーが、境界を Hi-Z と比べて判定**します。**今フレームの深度は、描いてみないと分からない**ので、**2 パス方式**（**前フレームで見えていた物を先に描き、その深度で残りを判定**）を使います。このページでは、**D3D12 での Hi-Z ミップ チェーンの作成・構築 CS・判定 HLSL・2 パスの流れ・バリア**を**実コード**で説明します。

!!! tip "ポイント"
    - <strong>Hi-Z ＝ 深度のミップ チェーン</strong>。<strong>各ミップは、2×2 の「最も遠い深度（最大）」</strong>を保存（<strong>保守的</strong>）。
    - 判定：<strong>物体の AABB を画面に投影</strong>し、<strong>その大きさに合うミップ</strong>を引き、<strong>物体の最も近い深度 ＞ Hi-Z の遠い深度</strong>なら<strong>隠れている</strong>。
    - <strong>2 パス</strong>：<strong>① 前フレーム可視の物を描画 → ② Hi-Z 構築 → ③ 残りの全物体を判定して描画</strong>。
    - <strong>可視フラグ</strong>を<strong>インスタンスごとに保存</strong>し、<strong>次フレームの 1 パス目に使う</strong>。
    - <strong>Hi-Z のミップごとの UAV/SRV</strong>と<strong>バリア</strong>の<strong>管理</strong>が、D3D12 の<strong>実装の山</strong>。
    - <strong>深度は標準 Z（遠いほど 1）</strong>で解説。<strong>Reversed-Z</strong>なら<strong>min/max と比較の向きが逆</strong>。

## Hi-Z テクスチャ

**深度バッファ**から、**ミップ チェーン付きの `R32_FLOAT` テクスチャ**を作ります。

```cpp
void Renderer::CreateHiZ(uint32_t width, uint32_t height) {
  hiz_width_ = NextPowerOfTwoFloor(width);
  hiz_height_ = NextPowerOfTwoFloor(height);
  hiz_mip_count_ = 1 + static_cast<uint32_t>(std::floor(std::log2(std::max(hiz_width_, hiz_height_))));

  CD3DX12_HEAP_PROPERTIES heap_properties(D3D12_HEAP_TYPE_DEFAULT);
  CD3DX12_RESOURCE_DESC desc = CD3DX12_RESOURCE_DESC::Tex2D(
      DXGI_FORMAT_R32_FLOAT, hiz_width_, hiz_height_, 1, static_cast<UINT16>(hiz_mip_count_), 1, 0,
      D3D12_RESOURCE_FLAG_ALLOW_UNORDERED_ACCESS);
  ThrowIfFailed(device_->CreateCommittedResource(&heap_properties, D3D12_HEAP_FLAG_NONE, &desc,
                                                 D3D12_RESOURCE_STATE_NON_PIXEL_SHADER_RESOURCE,
                                                 nullptr, IID_PPV_ARGS(&hiz_)));

  hiz_uav_base_ = bindless_heap_.AllocateRange(hiz_mip_count_);
  hiz_srv_base_ = bindless_heap_.AllocateRange(hiz_mip_count_);
  for (uint32_t mip = 0; mip < hiz_mip_count_; ++mip) {
    D3D12_UNORDERED_ACCESS_VIEW_DESC uav = {};
    uav.Format = DXGI_FORMAT_R32_FLOAT;
    uav.ViewDimension = D3D12_UAV_DIMENSION_TEXTURE2D;
    uav.Texture2D.MipSlice = mip;
    device_->CreateUnorderedAccessView(hiz_.Get(), nullptr, &uav, bindless_heap_.Cpu(hiz_uav_base_ + mip));

    D3D12_SHADER_RESOURCE_VIEW_DESC srv = {};
    srv.Format = DXGI_FORMAT_R32_FLOAT;
    srv.ViewDimension = D3D12_SRV_DIMENSION_TEXTURE2D;
    srv.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;
    srv.Texture2D.MostDetailedMip = mip;
    srv.Texture2D.MipLevels = 1;
    device_->CreateShaderResourceView(hiz_.Get(), &srv, bindless_heap_.Cpu(hiz_srv_base_ + mip));
  }

  D3D12_SHADER_RESOURCE_VIEW_DESC all_mips = {};
  all_mips.Format = DXGI_FORMAT_R32_FLOAT;
  all_mips.ViewDimension = D3D12_SRV_DIMENSION_TEXTURE2D;
  all_mips.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;
  all_mips.Texture2D.MostDetailedMip = 0;
  all_mips.Texture2D.MipLevels = hiz_mip_count_;
  hiz_full_srv_ = bindless_heap_.Allocate();
  device_->CreateShaderResourceView(hiz_.Get(), &all_mips, bindless_heap_.Cpu(hiz_full_srv_));
}
```

| 点 | 説明 |
| --- | --- |
| **2 のべき乗の大きさ** | **画面サイズ以下の最大の 2 のべき乗**にする。**ミップの縮小が割り切れ**、**判定が単純**になる（**元の深度はサンプリングで縮小して書く**） |
| **ミップ数** | `1 + floor(log2(max(幅, 高さ)))` |
| **ミップごとの UAV/SRV** | <strong>構築 CS は、ミップ i を読み（SRV）、ミップ i+1 に書く（UAV）</strong>。**1 枚のテクスチャの別々のミップを別々のビューで扱う** |
| **全ミップの SRV** | **判定 CS が、`SampleLevel` で、任意のミップを引く**ためのビュー |
| **`AllocateRange` / `Allocate`** | **ビンドレス ヒープの連続した番号を確保する**（先のクラスに追加。**連番確保のメソッド**） |
| **初期状態** | **`NON_PIXEL_SHADER_RESOURCE`**（**構築時に、UAV に遷移**して使う） |

### 深度バッファの SRV

**深度バッファ**を**コンピュートが読む**には、**型なしフォーマットで作成**し、**DSV と SRV で、別のフォーマットのビュー**を作ります。

```cpp
CD3DX12_RESOURCE_DESC depth_desc =
    CD3DX12_RESOURCE_DESC::Tex2D(DXGI_FORMAT_R32_TYPELESS, width, height, 1, 1, 1, 0,
                                 D3D12_RESOURCE_FLAG_ALLOW_DEPTH_STENCIL);

D3D12_DEPTH_STENCIL_VIEW_DESC dsv = {};
dsv.Format = DXGI_FORMAT_D32_FLOAT;
dsv.ViewDimension = D3D12_DSV_DIMENSION_TEXTURE2D;
device_->CreateDepthStencilView(depth_.Get(), &dsv, dsv_handle);

D3D12_SHADER_RESOURCE_VIEW_DESC depth_srv = {};
depth_srv.Format = DXGI_FORMAT_R32_FLOAT;
depth_srv.ViewDimension = D3D12_SRV_DIMENSION_TEXTURE2D;
depth_srv.Shader4ComponentMapping = D3D12_DEFAULT_SHADER_4_COMPONENT_MAPPING;
depth_srv.Texture2D.MipLevels = 1;
device_->CreateShaderResourceView(depth_.Get(), &depth_srv, bindless_heap_.Cpu(depth_srv_index_));
```

## Hi-Z の構築

**ミップ 0**は**深度バッファを、Hi-Z の大きさに縮小しながらコピー**します。**ミップ 1 以降**は、**前のミップの 2×2 の最大値**です。

```hlsl
Texture2D<float> source : register(t0);
RWTexture2D<float> destination : register(u0);

cbuffer HiZConstants : register(b0) {
  uint2 source_size;
  uint2 destination_size;
};

float MaxDepth4(uint2 base_texel) {
  uint2 max_texel = source_size - 1;
  float d0 = source.Load(int3(min(base_texel + uint2(0, 0), max_texel), 0));
  float d1 = source.Load(int3(min(base_texel + uint2(1, 0), max_texel), 0));
  float d2 = source.Load(int3(min(base_texel + uint2(0, 1), max_texel), 0));
  float d3 = source.Load(int3(min(base_texel + uint2(1, 1), max_texel), 0));
  return max(max(d0, d1), max(d2, d3));
}

[numthreads(8, 8, 1)]
void HiZMain(uint3 id : SV_DispatchThreadID) {
  if (any(id.xy >= destination_size)) return;
  uint2 base_texel = id.xy * 2;
  destination[id.xy] = MaxDepth4(base_texel);
}
```

| 点 | 説明 |
| --- | --- |
| <strong>`max`（標準 Z）</strong> | **標準 Z では、遠いほど値が大きい**。**2×2 の最大 ＝ そのブロック内で最も遠い深度**。<strong>「この範囲のどこを見てもこれより手前には何もない」</strong>を表す＝**保守的** |
| **ミップ 0 の縮小** | <strong>深度が、Hi-Z より大きい（例：1920×1080 → 1024×512）</strong>場合、**`source_size` と `destination_size` の比**で**ブロック**を**とる**必要がある。**簡単な場合**、<strong>2×2 でなく、比率（スケール）</strong>で**範囲の最大をとる** |
| **`min(..., max_texel)`** | **奇数サイズの端**で**範囲外を読まない** |

**ミップ 0 を比率で縮小**する、**一般的な版**です（**非 2 のべき乗の深度を、2 のべき乗の Hi-Z にする**）。

```hlsl
[numthreads(8, 8, 1)]
void HiZBaseMain(uint3 id : SV_DispatchThreadID) {
  if (any(id.xy >= destination_size)) return;

  uint2 begin = id.xy * source_size / destination_size;
  uint2 end = max((id.xy + 1) * source_size / destination_size, begin + 1);
  end = min(end, source_size);

  float result = 0.0;
  for (uint y = begin.y; y < end.y; ++y) {
    for (uint x = begin.x; x < end.x; ++x) {
      result = max(result, source.Load(int3(x, y, 0)));
    }
  }
  destination[id.xy] = result;
}
```

### C++：ミップごとにディスパッチ

```cpp
void Renderer::RecordBuildHiZ(ID3D12GraphicsCommandList* list) {
  CD3DX12_RESOURCE_BARRIER depth_to_read = CD3DX12_RESOURCE_BARRIER::Transition(
      depth_.Get(), D3D12_RESOURCE_STATE_DEPTH_WRITE,
      D3D12_RESOURCE_STATE_NON_PIXEL_SHADER_RESOURCE);
  list->ResourceBarrier(1, &depth_to_read);

  CD3DX12_RESOURCE_BARRIER hiz_to_uav = CD3DX12_RESOURCE_BARRIER::Transition(
      hiz_.Get(), D3D12_RESOURCE_STATE_NON_PIXEL_SHADER_RESOURCE,
      D3D12_RESOURCE_STATE_UNORDERED_ACCESS);
  list->ResourceBarrier(1, &hiz_to_uav);

  ID3D12DescriptorHeap* heaps[] = {bindless_heap_.Get()};
  list->SetDescriptorHeaps(1, heaps);
  list->SetComputeRootSignature(hiz_root_signature_.Get());

  uint32_t source_width = width_;
  uint32_t source_height = height_;
  uint32_t dest_width = hiz_width_;
  uint32_t dest_height = hiz_height_;

  list->SetPipelineState(hiz_base_pso_.Get());
  RecordHiZPass(list, bindless_heap_.Gpu(depth_srv_index_), bindless_heap_.Gpu(hiz_uav_base_),
                source_width, source_height, dest_width, dest_height);

  for (uint32_t mip = 1; mip < hiz_mip_count_; ++mip) {
    CD3DX12_RESOURCE_BARRIER uav_barrier = CD3DX12_RESOURCE_BARRIER::UAV(hiz_.Get());
    list->ResourceBarrier(1, &uav_barrier);

    source_width = dest_width;
    source_height = dest_height;
    dest_width = std::max(1u, dest_width / 2);
    dest_height = std::max(1u, dest_height / 2);

    list->SetPipelineState(hiz_mip_pso_.Get());
    RecordHiZPass(list, bindless_heap_.Gpu(hiz_srv_base_ + mip - 1),
                  bindless_heap_.Gpu(hiz_uav_base_ + mip), source_width, source_height, dest_width,
                  dest_height);
  }

  CD3DX12_RESOURCE_BARRIER to_read[2] = {
      CD3DX12_RESOURCE_BARRIER::Transition(hiz_.Get(), D3D12_RESOURCE_STATE_UNORDERED_ACCESS,
                                           D3D12_RESOURCE_STATE_NON_PIXEL_SHADER_RESOURCE),
      CD3DX12_RESOURCE_BARRIER::Transition(depth_.Get(),
                                           D3D12_RESOURCE_STATE_NON_PIXEL_SHADER_RESOURCE,
                                           D3D12_RESOURCE_STATE_DEPTH_WRITE),
  };
  list->ResourceBarrier(2, to_read);
}

void Renderer::RecordHiZPass(ID3D12GraphicsCommandList* list, D3D12_GPU_DESCRIPTOR_HANDLE source,
                             D3D12_GPU_DESCRIPTOR_HANDLE destination, uint32_t source_width,
                             uint32_t source_height, uint32_t dest_width, uint32_t dest_height) {
  uint32_t constants[4] = {source_width, source_height, dest_width, dest_height};
  list->SetComputeRoot32BitConstants(0, 4, constants, 0);
  list->SetComputeRootDescriptorTable(1, source);
  list->SetComputeRootDescriptorTable(2, destination);
  list->Dispatch((dest_width + 7) / 8, (dest_height + 7) / 8, 1);
}
```

| 点 | 説明 |
| --- | --- |
| **深度の遷移** | **`DEPTH_WRITE` → `NON_PIXEL_SHADER_RESOURCE`**。**読み終えたら、`DEPTH_WRITE` に戻す**（**2 パス目の描画**が**同じ深度に書く**ため） |
| **Hi-Z の遷移** | **構築中は `UNORDERED_ACCESS`**、**終わったら読み取り状態**へ |
| **UAV バリア** | **同じテクスチャの別ミップを、連続して読み書きする**とき、**前のディスパッチの書き込みが終わるのを保証**。**`CD3DX12_RESOURCE_BARRIER::UAV(hiz_)`** |
| **同じリソースの別ミップの SRV と UAV** | **同時に**、<strong>読み（ミップ i-1）と書き（ミップ i）</strong>を**している**ので**サブリソースを分けた状態管理**が**理論上は必要**だが、**UAV 状態のまま、SRV としても読める**ので、**構築中は `UNORDERED_ACCESS` で通す**（**実装では、UAV バリアで順序保証**） |
| **ルート シグネチャ** | <strong>0：32 ビット定数 4 つ、1：SRV のテーブル（t0）、2：UAV のテーブル（u0）</strong> |

!!! note "1 回のディスパッチで、全ミップを作る方法"
    <strong>AMD の Single Pass Downsampler（SPD）</strong>などは、**1 回のディスパッチで、全ミップ**を**作り**ます（**グループ間の同期にグローバル アトミック**を使う）。**ミップごとの UAV バリアが不要**になり、**高速**です。**まず、上記の素直な方式で動かし**、**コストが問題なら SPD を導入**します。

## 判定のシェーダー

<strong>境界ボックス（AABB）</strong>の**8 隅をクリップ空間に変換**し、**画面上の矩形と最も近い深度**を**求めます**。

```hlsl
Texture2D<float> hiz : register(t3);
SamplerState point_sampler : register(s0);

cbuffer OcclusionConstants : register(b1) {
  float4x4 view_projection;
  float2 hiz_size;
  uint hiz_mip_count;
  uint pass_index;
};

bool IsOccluded(float3 center, float radius_unused, float3 aabb_min, float3 aabb_max,
                float4x4 world) {
  float2 uv_min = float2(1.0, 1.0);
  float2 uv_max = float2(0.0, 0.0);
  float nearest_depth = 1.0;

  [unroll] for (int i = 0; i < 8; ++i) {
    float3 corner = float3((i & 1) ? aabb_max.x : aabb_min.x, (i & 2) ? aabb_max.y : aabb_min.y,
                           (i & 4) ? aabb_max.z : aabb_min.z);
    float4 world_position = mul(float4(corner, 1.0), world);
    float4 clip = mul(world_position, view_projection);
    if (clip.w <= 0.0) return false;

    float3 ndc = clip.xyz / clip.w;
    float2 uv = float2(ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5);
    uv_min = min(uv_min, uv);
    uv_max = max(uv_max, uv);
    nearest_depth = min(nearest_depth, ndc.z);
  }

  uv_min = saturate(uv_min);
  uv_max = saturate(uv_max);

  float2 size_in_pixels = (uv_max - uv_min) * hiz_size;
  float mip_level = ceil(log2(max(max(size_in_pixels.x, size_in_pixels.y), 1.0)));
  mip_level = min(mip_level, float(hiz_mip_count - 1));

  float d0 = hiz.SampleLevel(point_sampler, float2(uv_min.x, uv_min.y), mip_level);
  float d1 = hiz.SampleLevel(point_sampler, float2(uv_max.x, uv_min.y), mip_level);
  float d2 = hiz.SampleLevel(point_sampler, float2(uv_min.x, uv_max.y), mip_level);
  float d3 = hiz.SampleLevel(point_sampler, float2(uv_max.x, uv_max.y), mip_level);
  float farthest_occluder = max(max(d0, d1), max(d2, d3));

  return nearest_depth > farthest_occluder;
}
```

| 点 | 説明 |
| --- | --- |
| **`clip.w <= 0`** | <strong>カメラの後ろ（または近平面をまたぐ）</strong>角がある。**投影が破綻**するので<strong>隠れていない（可視）</strong>として**扱う**（**保守的**） |
| **`uv.y = 0.5 - ndc.y * 0.5`** | **D3D のテクスチャ座標は、上が 0<strong>。</strong>NDC の y は上が +1** なので**反転** |
| **`nearest_depth = min(...)`** | **物体の最も手前の深度**（**標準 Z：小さいほど近い**） |
| **`mip_level = ceil(log2(最大辺の画素数))`** | **矩形がそのミップの 1〜2 テクセルに収まる**ミップを選ぶ（**4 点の取得で矩形全体を覆える**） |
| **4 隅のサンプル** | **矩形の 4 隅**の<strong>Hi-Z（最も遠い深度）</strong>の**最大**が**その範囲で物体を隠しうる、最も遠い遮蔽物の深度** |
| **`nearest_depth > farthest_occluder`** | **物体の一番手前が範囲内の最も遠い遮蔽物より奥** ＝ **全体が隠れている** |
| **`point_sampler`** | **補間しない**（**最大値を保つ**ため、**ポイント サンプリング**） |

**保守的**に作ってあるため、**見えている物を誤って消すことはなく**、**隠れている物を見逃す**ことはあります（**描画が増えるだけ**）。

## 2 パス方式

**判定に使う Hi-Z は、「今フレームの深度」が理想**ですが**今フレームの深度は、描画前には存在しません**。**2 パス方式**で**解決**します。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="2 パス オクルージョン">
<text x="20" y="24" class="fig-title">前フレームで見えていた物を先に描き、その深度で、残りを判定する</text>
<rect x="30" y="50" width="200" height="50" rx="6" fill="rgba(76,139,245,0.18)" stroke="currentColor" stroke-width="2"/><text x="42" y="72" style="font-size:12px">1 パス目のカリング</text><text x="42" y="90" style="font-size:11px">視錐台 ＋ 前フレーム可視</text>
<rect x="260" y="50" width="200" height="50" rx="6" fill="rgba(46,160,67,0.22)" stroke="currentColor" stroke-width="2"/><text x="272" y="72" style="font-size:12px">1 パス目の描画</text><text x="272" y="90" style="font-size:11px">深度（＋ G バッファ）</text>
<rect x="490" y="50" width="200" height="50" rx="6" fill="rgba(229,170,40,0.25)" stroke="currentColor" stroke-width="2"/><text x="502" y="72" style="font-size:12px">Hi-Z 構築</text><text x="502" y="90" style="font-size:11px">今の深度から</text>
<rect x="490" y="140" width="200" height="50" rx="6" fill="rgba(76,139,245,0.18)" stroke="currentColor" stroke-width="2"/><text x="502" y="162" style="font-size:12px">2 パス目のカリング</text><text x="502" y="180" style="font-size:11px">視錐台 ＋ Hi-Z 判定</text>
<rect x="260" y="140" width="200" height="50" rx="6" fill="rgba(46,160,67,0.22)" stroke="currentColor" stroke-width="2"/><text x="272" y="162" style="font-size:12px">2 パス目の描画</text><text x="272" y="180" style="font-size:11px">新しく見えた物だけ</text>
<rect x="30" y="140" width="200" height="50" rx="6" fill="rgba(150,150,150,0.25)" stroke="currentColor" stroke-width="2"/><text x="42" y="162" style="font-size:12px">可視フラグ更新</text><text x="42" y="180" style="font-size:11px">次フレームの 1 パス目用</text>
<g stroke="currentColor" stroke-width="2"><line x1="230" y1="75" x2="260" y2="75"/><line x1="460" y1="75" x2="490" y2="75"/><line x1="590" y1="100" x2="590" y2="140"/><line x1="490" y1="165" x2="460" y2="165"/><line x1="260" y1="165" x2="230" y2="165"/></g>
<text x="30" y="226" style="font-size:12px">前フレームで見えていた物はおそらく今も見える → 先に描けば、良い遮蔽深度が得られる</text>
</svg>

| 段階 | 内容 |
| --- | --- |
| **1 パス目** | **視錐台カリング**を通り、**前フレームで可視だった物**を**描く**（**オクルージョン判定なし**）。**多くの遮蔽物がここで描かれる** |
| **Hi-Z 構築** | **1 パス目の深度**から、**Hi-Z を作る** |
| **2 パス目** | **全インスタンス**を**視錐台 ＋ Hi-Z で判定**。**通過し、かつ、1 パス目で描かれていない物だけ**を**描く** |
| **可視フラグの更新** | **2 パス目の判定で「可視」だった物**を<strong>次フレームの「前フレーム可視」</strong>として**記録** |

**前フレームで見えていた物が、今フレームも見える**ことが**多い**ので、**1 パス目でほとんどの遮蔽物が描かれます**。<strong>2 パス目の Hi-Z は、「ほぼ完全な深度」</strong>に近く、**正確な判定**ができます。**前フレームで見えず、今フレームで新しく見えた物**は、**2 パス目で拾われる**ので、**取りこぼしません**。

### 可視フラグ

```cpp
visibility_buffer_ = CreateDefaultBuffer(device_.Get(), sizeof(uint32_t) * kMaxInstances,
                                         D3D12_RESOURCE_FLAG_ALLOW_UNORDERED_ACCESS,
                                         D3D12_RESOURCE_STATE_UNORDERED_ACCESS);
```

**1 インスタンスにつき 1 ワード**（0 か 1）の**バッファ**を**フレームをまたいで保持**します。<strong>RWByteAddressBuffer か RWStructuredBuffer\<uint\></strong> として使います。

### 2 パスのカリング シェーダー

**カリング CS**に、**`pass_index`**（0 か 1）を**追加**します。

```hlsl
RWStructuredBuffer<uint> visibility : register(u2);

[numthreads(64, 1, 1)]
void CullTwoPassMain(uint3 id : SV_DispatchThreadID) {
  uint instance_index = id.x;
  if (instance_index >= instance_count) return;

  Instance instance = instances[instance_index];
  MeshInfo mesh = meshes[instance.mesh_index];

  float3 center = mul(float4(mesh.bounds_center, 1.0), instance.world).xyz;
  float radius = mesh.bounds_radius * MaxScale(instance.world);

  bool in_frustum = SphereInFrustum(center, radius);
  uint was_visible = visibility[instance_index];

  bool draw = false;
  if (pass_index == 0) {
    draw = in_frustum && (was_visible != 0);
  } else {
    bool occluded = true;
    if (in_frustum) {
      occluded = IsOccluded(mesh.bounds_center, mesh.bounds_radius, mesh.aabb_min,
                            mesh.aabb_max, instance.world);
    }
    visibility[instance_index] = (in_frustum && !occluded) ? 1 : 0;
    draw = in_frustum && !occluded && (was_visible == 0);
  }

  if (!draw) return;

  uint slot;
  command_counts.InterlockedAdd(mesh.pso_bucket * 4, 1, slot);
  if (slot >= MAX_COMMANDS_PER_BUCKET) return;

  IndirectCommand command;
  command.instance_index = instance_index;
  command.index_count = mesh.index_count;
  command.instance_count = 1;
  command.start_index = mesh.start_index;
  command.base_vertex = mesh.base_vertex;
  command.start_instance = 0;
  commands[mesh.pso_bucket * MAX_COMMANDS_PER_BUCKET + slot] = command;
}
```

| 点 | 説明 |
| --- | --- |
| <strong>1 パス目（`pass_index == 0`）</strong> | **視錐台内 ＆ 前フレーム可視**の物を**描く**。**可視フラグは更新しない** |
| <strong>2 パス目（`pass_index == 1`）</strong> | **視錐台内の全物体**を**Hi-Z で判定**。**可視フラグを今回の判定で更新** |
| <strong>`draw` の条件（2 パス目）</strong> | <strong>今回可視 かつ 1 パス目で描かれていない（`was_visible == 0`）</strong>物だけ**描く**（**二重描画を避ける**） |
| **1 パス目で描かれたが、2 パス目で隠れていた物** | **可視フラグは 0 になる**（**次フレームの 1 パス目で描かれない**）。**今フレームは既に描かれてしまっている**（**描画の無駄はあるが見た目は正しい**） |
| **`mesh.aabb_min/max`** | **`MeshInfo` に AABB を追加**する（**境界球だけでなく、AABB も必要**） |

!!! note "MeshInfo に AABB を追加する"
    **Hi-Z の判定は AABB を使う**ので、**`MeshInfo`**（[全体の構造体](index.md)）に、**`float3 aabb_min; float3 aabb_max;`** を**追加**します。**サイズが変わる**ので、**`static_assert` と HLSL の構造体**を**更新**します。

### フレームの流れ（C++）

```cpp
void Renderer::RecordFrame(ID3D12GraphicsCommandList* list) {
  UploadInstances(list, instance_count_);

  RecordCull(list, cull_constants_pass0_, constants_address_pass0_);
  RecordDraw(list, frame_address_);

  RecordBuildHiZ(list);

  RecordCull(list, cull_constants_pass1_, constants_address_pass1_);
  RecordDraw(list, frame_address_);
}
```

| 点 | 説明 |
| --- | --- |
| **カウンタのリセットとコマンド バッファ** | **`RecordCull` が、毎回、カウンタをリセット**する。**2 パス目は新しいコマンド列** |
| **深度クリアは、1 パス目の前だけ** | **2 パス目の描画は、同じ深度バッファに追加で描く**（**クリアしない**） |
| **定数の `pass_index`** | **`cull_constants_pass0_` / `pass1_`** で**値を変える**。**アップロード リングの別の領域** |
| **Hi-Z の判定に使うビュー射影行列** | **今フレームの値**（**2 パス目の Hi-Z は、今フレームの深度から作られている**ので、**再投影は不要**） |

## 前フレームの Hi-Z を使う簡易版

**2 パス方式は、実装が複雑**です。**簡易版**として、<strong>前フレームの Hi-Z を、そのまま使う（1 パスのみ）</strong>方法があります。

| 項目 | 2 パス方式 | 前フレーム Hi-Z（1 パス） |
| --- | --- | --- |
| **実装** | **複雑** | **簡単** |
| **カメラが動いたとき** | **今の深度**を使うので**正確** | **前のカメラ位置の深度**で判定するため、**再投影が必要**。<strong>急な動きで誤って消す（ポップイン）</strong> |
| **安全策** | **不要**（保守的） | **前フレームのビュー射影で、AABB を投影**して判定する（**再投影**）。**さらに保守的な余白** |
| **品質** | **高い** | **動きが速い・急な視点移動でちらつく** |

**前フレームの Hi-Z で判定する**場合は、**前フレームのビュー射影行列**で**AABB を投影**して、**前フレームの Hi-Z と比べる**必要があります。

## 注意点と対策

| 問題 | 対策 |
| --- | --- |
| **小さな物体がちらつく** | **Hi-Z の最大値**を使っているので**通常は保守的**。**ちらつくなら、判定に余白（ε）を持たせる** |
| **画面の端・近平面をまたぐ物体** | **`clip.w <= 0` なら、可視として扱う** |
| **アルファ テスト・半透明** | **遮蔽物にならない**ので、**Hi-Z を作る描画から、除外**する |
| **ダブル バッファのビジビリティ** | **可視フラグをフレームごとに 2 面持つ**構成は、**1 つだと読み書きが競合しうる**場合の対策 |
| **大量のインスタンスの AABB 投影** | **ほとんどが早期（視錐台）で除外**されるので、**Hi-Z 判定の負担は、限定的** |

## よくあるミス

??? failure "Hi-Z を min で作って（標準 Z）、遠くの物が全部、隠れる判定になる"
    <strong>標準 Z は max（遠い深度）</strong>。**Reversed-Z は min**。

??? failure "UV の y を反転せず、上下がずれた位置を判定して、物が消える"
    **`uv.y = 0.5 - ndc.y * 0.5`**。

??? failure "近平面をまたぐ物体を投影して、破綻して消える"
    **`clip.w <= 0` は、可視として扱う**。

??? failure "Hi-Z のミップ間の UAV バリアを入れず、ミップが壊れる"
    **各ディスパッチの間に UAV バリア**。

??? failure "深度を DEPTH_WRITE のまま、CS から SRV で読んで、デバッグ レイヤーがエラー"
    **`NON_PIXEL_SHADER_RESOURCE` に遷移して読み、終わったら戻す**。

??? failure "2 パス目も、1 パス目で描いた物を再度描いて、二重描画"
    **`was_visible == 0` の物だけ**描く。

??? failure "Hi-Z に、アルファ テストの葉などを含めて、穴だらけの物を遮蔽物にして、後ろの物が消える"
    **遮蔽物に使う描画**（**深度のみのパス**）から、**半透明・アルファ テスト**を**除外**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Hi-Z ＝ <strong>深度のミップ チェーン</strong>。<strong>標準 Z では 2×2 の最大（最も遠い）</strong>を保存して<strong>保守的</strong>に
    - [x] 判定 ＝ <strong>AABB を投影し、大きさに合うミップの 4 隅の最大</strong>と、<strong>物体の最も近い深度</strong>を比べる
    - [x] <strong>2 パス</strong>：<strong>前フレーム可視を描く → Hi-Z → 残りを判定して描く</strong>。<strong>可視フラグ</strong>を<strong>保存</strong>
    - [x] <strong>`clip.w ≤ 0` は可視</strong>、<strong>UV の y 反転</strong>、<strong>ミップ間の UAV バリア</strong>に注意
    - [x] <strong>深度の状態遷移</strong>（<strong>DEPTH_WRITE ↔ NON_PIXEL_SHADER_RESOURCE</strong>）を<strong>忘れない</strong>

## 参考

- Aaltonen, "GPU-Based Clay Simulation and Ray-Tracing Tech in Claybook"／"Optimizing Occlusion Culling in Assassin's Creed Unity"（GDC 2015、2 パス手法）
- Haar, Aaltonen, "GPU-Driven Rendering Pipelines"（SIGGRAPH 2015）
- AMD, "FidelityFX Single Pass Downsampler (SPD)"

## 関連ページ

- [GPU Driven（D3D12 詳細）](index.md)
- [カリング（コンピュート）](culling.md)
- [ExecuteIndirect](execute-indirect.md)
- [Hi-Z](../hiz.md)
- [オクルージョン カリング](../culling.md)
