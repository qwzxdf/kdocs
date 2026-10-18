---
title: ビンドレス（記述子の直接参照）
tags:
  - 描画最適化
---

# ビンドレス（記述子の直接参照）

**GPU Driven では、描画ごとに CPU が「このテクスチャを使え」と設定することができません**（**CPU は何が描かれるか知らない**）。そこで**全テクスチャの記述子を 1 つのヒープに並べ**、**シェーダーが「番号」で直接引く**方式を使います。これが**ビンドレス**（Bindless）です。**D3D12 では、SM 6.6 の `ResourceDescriptorHeap`** が**最も簡単**です。このページでは、**マテリアル構造体・記述子の割り当て・シェーダーでの引き方・`NonUniformResourceIndex` の落とし穴**を説明します。

!!! tip "ポイント"
    - <strong>全テクスチャの SRV を、1 つのシェーダー可視ヒープに並べ</strong>、<strong>シェーダーは「ヒープ内の番号」</strong>で引く。
    - <strong>マテリアル</strong>は、<strong>テクスチャ番号を持つ構造体</strong>のバッファ。<strong>インスタンス → マテリアル番号 → テクスチャ番号</strong>。
    - <strong>SM 6.6</strong>：<strong>`ResourceDescriptorHeap[index]`</strong>。<strong>ルート シグネチャの専用フラグ</strong>が必要。
    - <strong>SM 6.6 以前</strong>：<strong>無制限サイズの記述子テーブル</strong>（<strong>`Texture2D textures[]`</strong>）。
    - <strong>ピクセル内で番号が一定でない</strong>なら<strong>`NonUniformResourceIndex`</strong> が<strong>必須</strong>。
    - <strong>記述子を解放して再利用</strong>するときは、<strong>GPU が使い終わるまで待つ</strong>（<strong>遅延解放</strong>）。

## 発想

**従来**は**描画のたびに**、**CPU がテクスチャを設定**していました。

| 方式 | テクスチャの指定 | GPU Driven との相性 |
| --- | --- | --- |
| <strong>従来（バインド型）</strong> | **ドローごとに、CPU がテクスチャをバインド** | **✕**（CPU が何を描くか知らない） |
| **ビンドレス** | **シェーダーが番号でヒープを直接引く** | **○**（番号はバッファに入れておける） |

**1 回の `ExecuteIndirect` で、数万の物体を異なるテクスチャで描く**には、**この方式が必須**です。

## マテリアルのデータ

**マテリアルがテクスチャの「番号」を持つ**構造体を、**GPU バッファ**に置きます。

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
```

| 要素 | 内容 |
| --- | --- |
| **`albedo_index` など** | **テクスチャの SRV の、ヒープ内の番号** |
| **無効値** | **テクスチャなし**を表す番号（例：`0xFFFFFFFF`）を決め、**シェーダーで分岐** |
| **`orm_index`** | **Occlusion・Roughness・Metallic を 1 枚に詰めた**テクスチャ（**サンプル回数を減らす**） |

**インスタンス → `material_index` → `Material` → テクスチャ番号 → ヒープ**と**たどり**ます。

## 記述子の割り当て

**テクスチャを読み込んだら**、**共有ヒープに SRV を作り、その番号を覚えます**。

```cpp
class BindlessHeap {
 public:
  void Initialize(ID3D12Device* device, uint32_t capacity) {
    heap_.Initialize(device, D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV, capacity, true);
    for (uint32_t i = capacity; i > 0; --i) free_list_.push_back(i - 1);
  }

  uint32_t RegisterTexture(ID3D12Device* device, ID3D12Resource* texture) {
    assert(!free_list_.empty());
    uint32_t index = free_list_.back();
    free_list_.pop_back();
    device->CreateShaderResourceView(texture, nullptr, heap_.Cpu(index));
    return index;
  }

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

  DescriptorHeap heap_;
  std::vector<uint32_t> free_list_;
  std::vector<PendingRelease> pending_release_;
};
```

| 点 | 説明 |
| --- | --- |
| **`CreateShaderResourceView(texture, nullptr, ...)`** | **`nullptr` を渡すと、リソースのデフォルト SRV**（フォーマット・全ミップ）が作られる。**特殊なビューが必要なときは、`D3D12_SHADER_RESOURCE_VIEW_DESC` を渡す** |
| **フリー リスト** | **解放された番号を再利用** |
| <strong>`ScheduleRelease`（遅延解放）</strong> | **テクスチャを破棄する際**、**GPU がまだその記述子を参照している**可能性がある。**そのフレームのフェンス値**を**記録**し、**完了後に番号を返す** |
| **番号 0 をフォールバックに** | **ヒープの先頭に白テクスチャ**などの**デフォルト**を**登録**しておくと、**無効な参照が安全** |

## SM 6.6：ResourceDescriptorHeap

**SM 6.6 以降**では、**シェーダーから、ヒープを直接配列のように引けます**。

```hlsl
SamplerState linear_sampler : register(s0);

float4 PSMain(VsOutput input) : SV_Target {
  Material material = materials[input.material_index];
  Texture2D<float4> albedo_tex = ResourceDescriptorHeap[NonUniformResourceIndex(material.albedo_index)];
  float4 albedo = albedo_tex.Sample(linear_sampler, input.uv) * material.base_color;
  return albedo;
}
```

| 点 | 説明 |
| --- | --- |
| **`ResourceDescriptorHeap[i]`** | **現在バインドされている CBV/SRV/UAV ヒープの、i 番目**の記述子を**そのまま**型付きで取り出す |
| **型の指定** | **左辺の型**（`Texture2D<float4>` など）で、**ビューの型を解釈**。**実際の SRV の種類と一致**している必要がある |
| **サンプラー** | **`SamplerDescriptorHeap[i]`** で、**同様に引ける**。**数個なら、静的サンプラーで十分** |
| **`NonUniformResourceIndex`** | **次節** |

### ルート シグネチャのフラグ

**`ResourceDescriptorHeap` を使う**には、**ルート シグネチャに専用のフラグ**が**必要**です。

```cpp
CD3DX12_VERSIONED_ROOT_SIGNATURE_DESC desc;
desc.Init_1_1(parameter_count, parameters, static_sampler_count, static_samplers,
              D3D12_ROOT_SIGNATURE_FLAG_CBV_SRV_UAV_HEAP_DIRECTLY_INDEXED |
                  D3D12_ROOT_SIGNATURE_FLAG_SAMPLER_HEAP_DIRECTLY_INDEXED);
```

| フラグ | 内容 |
| --- | --- |
| **`CBV_SRV_UAV_HEAP_DIRECTLY_INDEXED`** | **`ResourceDescriptorHeap` を使う**ために必須 |
| **`SAMPLER_HEAP_DIRECTLY_INDEXED`** | **`SamplerDescriptorHeap` を使う**場合 |

**ヒープはコマンド リストで**、**`SetDescriptorHeaps`** して**バインド**します。

```cpp
ID3D12DescriptorHeap* heaps[] = {bindless_heap_.Get()};
command_list->SetDescriptorHeaps(1, heaps);
```

### 対応の確認

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

| 条件 | 内容 |
| --- | --- |
| **SM 6.6** | **`ResourceDescriptorHeap`** に必要 |
| **ResourceBindingTier 3** | **ヒープ全体を制限なく**使える（**SM 6.6 の直接参照**は、**Tier 3 相当**の機能が前提になる環境が多い） |

## SM 6.6 より前：無制限の記述子テーブル

**SM 6.6 が使えない**環境では、**ルート シグネチャにサイズが「無制限」の記述子テーブル**を**置き**ます。

```cpp
CD3DX12_DESCRIPTOR_RANGE1 range;
range.Init(D3D12_DESCRIPTOR_RANGE_TYPE_SRV, UINT_MAX, 0, 1,
           D3D12_DESCRIPTOR_RANGE_FLAG_DESCRIPTORS_VOLATILE);

CD3DX12_ROOT_PARAMETER1 table_parameter;
table_parameter.InitAsDescriptorTable(1, &range, D3D12_SHADER_VISIBILITY_PIXEL);
```

```hlsl
Texture2D<float4> textures[] : register(t0, space1);

float4 sample = textures[NonUniformResourceIndex(material.albedo_index)].Sample(linear_sampler, uv);
```

| 点 | 説明 |
| --- | --- |
| **`NumDescriptors = UINT_MAX`** | **無制限**（実際のヒープの大きさまで） |
| **`space1`** | **レジスタ空間を分けて**、**他のバインディングと衝突**しないように |
| **`SetGraphicsRootDescriptorTable`** | **ヒープの先頭の GPU ハンドル**を渡す |
| **要件** | **ResourceBindingTier 3**（**無制限サイズのテーブル**に必要） |

## NonUniformResourceIndex

**ビンドレスの最大の落とし穴**です。**同じ命令（ウェーブ）内の全レーンが同じ番号**でなら**問題**ありませんが、**レーンごとに番号が違う**場合、**`NonUniformResourceIndex` を付けない**と、**未定義の動作**になります（**1 番目のレーンの番号が、全レーンに使われる**など）。

| 状況 | 番号は一様か |
| --- | --- |
| **ドロー単位の定数**（ルート定数のマテリアル番号） | **一様**（付けなくてよい） |
| **ExecuteIndirect の、1 ドローが 1 インスタンス**で、**マテリアルがインスタンスごとに 1 つ** | **ほぼ一様**（**ドロー内では全ピクセルが同じ番号**）。**ただし、実装依存なので付けるのが安全** |
| **ビジビリティ バッファのシェーディング**（画素ごとにマテリアルが違う） | **非一様**（**必須**） |
| **インスタンスを 1 ドローにまとめる**（ジオメトリ シェーダーなど） | **非一様** |

```hlsl
Texture2D<float4> tex = ResourceDescriptorHeap[NonUniformResourceIndex(material.albedo_index)];
```

| 点 | 説明 |
| --- | --- |
| **性能** | **非一様の場合、ハードウェアがレーンごとに「ループ」して処理**する場合があり、**わずかに遅い** |
| **付ける基準** | <strong>「同じウェーブに違う番号が入りうる」なら、付ける</strong>。**迷ったら付ける** |

## マテリアルごとの分岐を減らす

**テクスチャを番号で引ける**ので**マテリアルが違っても同じ PSO・同じシェーダー**で**描けます**。**PSO の数**（**PSO バケットの数**）が**減り**、**ExecuteIndirect の呼び出し**も**減ります**。

| 方針 | 内容 |
| --- | --- |
| **ウーバー シェーダー** | **多くのマテリアルを、1 つのシェーダー**で（**フラグで分岐**） |
| **バケット数を絞る** | **不透明・アルファ テスト・両面**など、**PSO の状態が本当に違うもの**だけ**分ける** |
| **テクスチャ番号をフラグで制御** | **ない場合はデフォルト値** |

<!-- fig:bindless-index:begin -->

<svg class="fig illust motion" data-fig="bindless-index" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bindless-index" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ビンドレス: マテリアルが「テクスチャの番号」を持ち、シェーダーが番号で引く</text>
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

## よくあるミス

??? failure "NonUniformResourceIndex を付けず、画素ごとに違うテクスチャが引かれるはずが、全部同じになる"
    **非一様な番号には、必ず `NonUniformResourceIndex`**。

??? failure "ルート シグネチャに DIRECTLY_INDEXED フラグを付けず、ResourceDescriptorHeap を使って、PSO 作成に失敗"
    **`CBV_SRV_UAV_HEAP_DIRECTLY_INDEXED`** を**指定**する。

??? failure "テクスチャを破棄した直後に、記述子を再利用して、GPU が別のテクスチャを参照して化ける"
    **遅延解放**（**フェンス完了後**に返却）。

??? failure "SetDescriptorHeaps を呼ばず、またはフレーム中に別のヒープに切り替えて、記述子が無効になる"
    **ビンドレス ヒープをフレーム全体で 1 つ**にし、**最初にバインド**する。

??? failure "SRV の種類（Texture2D と TextureCube など）が、シェーダーの型と合わない"
    **ヒープの番号が指す SRV の種類**と、**シェーダーで宣言する型**を**一致**させる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ビンドレス ＝ <strong>全テクスチャの記述子を 1 つのヒープに並べ</strong>、<strong>シェーダーが番号で引く</strong>
    - [x] <strong>マテリアル構造体にテクスチャ番号</strong>を入れる。<strong>インスタンス → マテリアル → テクスチャ</strong>
    - [x] <strong>SM 6.6</strong>：<strong>`ResourceDescriptorHeap[i]`</strong> と<strong>ルート シグネチャの専用フラグ</strong>
    - [x] <strong>非一様な番号</strong>には<strong>`NonUniformResourceIndex`</strong>。<strong>迷ったら付ける</strong>
    - [x] <strong>記述子の再利用は、GPU の使用が終わってから</strong>（<strong>遅延解放</strong>）

## 参考

- Microsoft, "HLSL Shader Model 6.6: Dynamic Resources"
- Microsoft, "Resource Binding in HLSL"
- Microsoft, "Root Signature Version 1.1"

## 関連ページ

- [GPU Driven（D3D12 詳細）](index.md)
- [シーン データ](scene-data.md)
- [ExecuteIndirect](execute-indirect.md)
- [ビジビリティ バッファ](../visibility-buffer.md)
