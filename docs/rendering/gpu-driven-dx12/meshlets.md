---
title: メッシュレットとメッシュ シェーダー
tags:
  - 描画最適化
---

# メッシュレットとメッシュ シェーダー

ここまでは**インスタンス単位**（1 つの物体）で**カリング**しました。**巨大なメッシュ**（建物・地形・高ポリのキャラ）では**一部だけが見える**ことが多く、**物体全体を描く**のは**無駄**です。**メッシュレット**（Meshlet）は、**メッシュを数十〜百数十個の三角形の小さな塊（クラスタ）に分割**し、**塊ごとにカリング**する仕組みです。D3D12 では、<strong>メッシュ シェーダー（増幅シェーダー ＋ メッシュ シェーダー）</strong>が**メッシュレットを直接処理**できます。このページでは、**メッシュレットのデータ構造・増幅シェーダーでのカリング（視錐台・背面コーン）・メッシュ シェーダー・PSO の作成・`ExecuteIndirect` との組み合わせ**を、**実コード**で説明します。

!!! tip "ポイント"
    - メッシュレット ＝ <strong>最大 64 頂点・124 三角形</strong>程度の<strong>小さな塊</strong>。<strong>塊ごとに境界球と背面コーン</strong>を持つ。
    - <strong>増幅シェーダー（AS）</strong>：<strong>メッシュレットをカリングして、生き残りだけ</strong>を<strong>メッシュ シェーダー（MS）に渡す</strong>。
    - <strong>メッシュ シェーダー</strong>：<strong>1 グループが 1 メッシュレット</strong>を処理し、<strong>頂点とプリミティブを直接出力</strong>。
    - <strong>背面コーン</strong>：<strong>メッシュレットの全三角形が、カメラに背を向けている</strong>なら<strong>丸ごと除外</strong>できる。
    - <strong>`ExecuteIndirect` の引数に `DISPATCH_MESH`</strong>。<strong>インスタンスごとに、AS を起動</strong>する。
    - <strong>メッシュ シェーダー対応（Tier 1）</strong>の GPU が必要。<strong>`meshoptimizer`</strong> で<strong>メッシュレットを作る</strong>。

## メッシュレットとは

**メッシュレット**は、**メッシュの三角形を頂点の再利用を最大化しながら、小さなグループにまとめた**ものです。

| 項目 | 内容 |
| --- | --- |
| **サイズ** | **最大 64 頂点・124（または 126）三角形**が**標準的**（**GPU のメッシュ シェーダー出力の上限・効率**から） |
| **頂点の参照** | **メッシュ全体の頂点バッファへのインデックス**の**配列**（最大 64 個）を持つ |
| **三角形** | **メッシュレット内の頂点番号（0〜63）の 3 つ組** |
| **カリング情報** | **境界球**・**背面コーン**（軸と角度） |

### データ構造

```cpp
struct MeshletData {
  uint32_t vertex_offset;
  uint32_t triangle_offset;
  uint32_t vertex_count;
  uint32_t triangle_count;
};

struct MeshletBounds {
  DirectX::XMFLOAT3 center;
  float radius;
  DirectX::XMFLOAT3 cone_axis;
  float cone_cutoff;
};
```

| フィールド | 内容 |
| --- | --- |
| **`vertex_offset`** | **メッシュレットの頂点インデックス配列**の、**グローバル配列内の開始位置** |
| **`triangle_offset`** | **三角形配列の開始位置**（1 三角形 ＝ 1 ワードにパック） |
| **`cone_axis`** | **メッシュレットの法線の平均方向**（**背面コーンの軸**） |
| **`cone_cutoff`** | **コーンの開き**（`cos(角度)` 相当）。**これを使い、背面を判定** |

### meshoptimizer で作る

**`meshoptimizer`** ライブラリの **`meshopt_buildMeshlets`** と **`meshopt_computeMeshletBounds`** が**標準的**です。

```cpp
constexpr size_t kMaxVertices = 64;
constexpr size_t kMaxTriangles = 124;
constexpr float kConeWeight = 0.5f;

void BuildMeshlets(const std::vector<DirectX::XMFLOAT3>& positions,
                   const std::vector<uint32_t>& indices, std::vector<MeshletData>* meshlets,
                   std::vector<MeshletBounds>* bounds, std::vector<uint32_t>* meshlet_vertices,
                   std::vector<uint32_t>* meshlet_triangles) {
  size_t max_meshlets = meshopt_buildMeshletsBound(indices.size(), kMaxVertices, kMaxTriangles);
  std::vector<meshopt_Meshlet> local_meshlets(max_meshlets);
  std::vector<unsigned int> local_vertices(max_meshlets * kMaxVertices);
  std::vector<unsigned char> local_triangles(max_meshlets * kMaxTriangles * 3);

  size_t count = meshopt_buildMeshlets(
      local_meshlets.data(), local_vertices.data(), local_triangles.data(), indices.data(),
      indices.size(), &positions[0].x, positions.size(), sizeof(DirectX::XMFLOAT3), kMaxVertices,
      kMaxTriangles, kConeWeight);

  for (size_t i = 0; i < count; ++i) {
    const meshopt_Meshlet& m = local_meshlets[i];

    MeshletData data;
    data.vertex_offset = static_cast<uint32_t>(meshlet_vertices->size());
    data.triangle_offset = static_cast<uint32_t>(meshlet_triangles->size());
    data.vertex_count = m.vertex_count;
    data.triangle_count = m.triangle_count;
    meshlets->push_back(data);

    for (unsigned int v = 0; v < m.vertex_count; ++v) {
      meshlet_vertices->push_back(local_vertices[m.vertex_offset + v]);
    }
    for (unsigned int t = 0; t < m.triangle_count; ++t) {
      const unsigned char* tri = &local_triangles[m.triangle_offset + t * 3];
      meshlet_triangles->push_back(static_cast<uint32_t>(tri[0]) |
                                   (static_cast<uint32_t>(tri[1]) << 8) |
                                   (static_cast<uint32_t>(tri[2]) << 16));
    }

    meshopt_Bounds b = meshopt_computeMeshletBounds(
        &local_vertices[m.vertex_offset], &local_triangles[m.triangle_offset], m.triangle_count,
        &positions[0].x, positions.size(), sizeof(DirectX::XMFLOAT3));
    MeshletBounds bound;
    bound.center = {b.center[0], b.center[1], b.center[2]};
    bound.radius = b.radius;
    bound.cone_axis = {b.cone_axis[0], b.cone_axis[1], b.cone_axis[2]};
    bound.cone_cutoff = b.cone_cutoff;
    bounds->push_back(bound);
  }
}
```

| 点 | 説明 |
| --- | --- |
| **`kConeWeight`** | **背面コーンのカリング効率を、どれだけ重視して分割するか**（0〜1）。**大きいと法線がそろった塊**になり、**背面カリングの効果が上がる**（**頂点再利用はやや落ちる**） |
| **三角形を、1 ワードにパック** | **`a | b << 8 | c << 16`**。**メッシュ シェーダーで、`uint` 1 つから取り出せる** |
| **`meshopt_computeMeshletBounds`** | **境界球**と**背面コーン**を**計算** |
| **`cone_cutoff`** | **`meshopt_Bounds::cone_cutoff`**。**背面判定は、HLSL で後述** |

## GPU 側のデータ

**メッシュレット情報**を**GPU に常駐**させます。

| バッファ | 内容 |
| --- | --- |
| **メッシュレット バッファ** | **`MeshletData` の配列** |
| **メッシュレット境界バッファ** | **`MeshletBounds` の配列** |
| **メッシュレット頂点インデックス** | **メッシュレットごとの頂点インデックス**（`uint` の配列） |
| **メッシュレット三角形** | **パックした三角形**（`uint` の配列） |
| **頂点バッファ** | **従来どおり**（**StructuredBuffer として、シェーダーから読む**） |

**`MeshInfo`** に**そのメッシュのメッシュレットの開始番号と個数**を**追加**します。

```hlsl
struct MeshInfo {
  float3 bounds_center;
  float bounds_radius;
  float3 aabb_min;
  uint meshlet_offset;
  float3 aabb_max;
  uint meshlet_count;
  uint pso_bucket;
  uint3 reserved;
};
```

## 増幅シェーダー（カリング）

<strong>増幅シェーダー（AS）</strong>は、**メッシュ シェーダーの前**に**動くシェーダー**です。**グループ内のスレッド（例：32）が、それぞれ 1 つのメッシュレットを判定**し、**生き残ったメッシュレットの数だけ、メッシュ シェーダーのグループを起動**します。

```hlsl
#define AS_GROUP_SIZE 32

struct Payload {
  uint meshlet_indices[AS_GROUP_SIZE];
  uint instance_index;
};

groupshared Payload s_payload;
groupshared uint s_visible_count;

StructuredBuffer<MeshletBounds> meshlet_bounds : register(t4);

bool MeshletVisible(MeshletBounds bounds, float4x4 world, float3 camera_position) {
  float3 center = mul(float4(bounds.center, 1.0), world).xyz;
  float radius = bounds.radius * MaxScale(world);
  if (!SphereInFrustum(center, radius)) return false;

  float3 axis = normalize(mul(bounds.cone_axis, (float3x3)world));
  float3 to_meshlet = center - camera_position;
  float distance_to_meshlet = length(to_meshlet);
  if (dot(to_meshlet, axis) >= bounds.cone_cutoff * distance_to_meshlet + radius) return false;

  return true;
}

[numthreads(AS_GROUP_SIZE, 1, 1)]
void ASMain(uint group_thread_id : SV_GroupThreadID, uint group_id : SV_GroupID) {
  uint instance_index = draw_instance_index;
  Instance instance = instances[instance_index];
  MeshInfo mesh = meshes[instance.mesh_index];

  if (group_thread_id == 0) s_visible_count = 0;
  GroupMemoryBarrierWithGroupSync();

  uint local_index = group_id * AS_GROUP_SIZE + group_thread_id;
  if (local_index < mesh.meshlet_count) {
    uint meshlet_index = mesh.meshlet_offset + local_index;
    if (MeshletVisible(meshlet_bounds[meshlet_index], instance.world, camera_position)) {
      uint slot;
      InterlockedAdd(s_visible_count, 1, slot);
      s_payload.meshlet_indices[slot] = meshlet_index;
    }
  }

  s_payload.instance_index = instance_index;
  GroupMemoryBarrierWithGroupSync();

  DispatchMesh(s_visible_count, 1, 1, s_payload);
}
```

| 点 | 説明 |
| --- | --- |
| **`Payload`** | **AS → MS へ渡すデータ**。**生き残ったメッシュレット番号の配列**と、**インスタンス番号** |
| **`groupshared` ペイロード** | **ペイロードはグループ共有メモリ**に置く（**`DispatchMesh` に渡す**） |
| **背面コーンの判定** | **`dot(視線ベクトル, 軸) ≥ cutoff * 距離 + 半径`<strong> なら、</strong>全三角形が背面** ⇒ **不可視<strong>（</strong>meshoptimizer の公式の式**） |
| **`InterlockedAdd(s_visible_count, ...)`** | **ウェーブ サイズに依存しない**（**`WavePrefixCountBits`** は、**ウェーブ サイズが 32 未満**のハードウェアで**不正になる**ため**避ける**） |
| **`DispatchMesh(count, 1, 1, payload)`** | **`count` 個のメッシュ シェーダー グループを起動**。**0 なら何も起動しない**。**グループ内の全スレッドが、一様に呼ぶ** |
| **`draw_instance_index`** | **ExecuteIndirect が書いた、ルート定数のインスタンス番号**（前節と同様） |

## メッシュ シェーダー

<strong>メッシュ シェーダー（MS）</strong>は、**1 グループが 1 メッシュレット**を処理し、**頂点とプリミティブ（三角形）を出力**します。

```hlsl
#define MS_GROUP_SIZE 128
#define MAX_VERTICES 64
#define MAX_TRIANGLES 124

StructuredBuffer<MeshletData> meshlets : register(t5);
StructuredBuffer<uint> meshlet_vertices : register(t6);
StructuredBuffer<uint> meshlet_triangles : register(t7);
StructuredBuffer<Vertex> vertices : register(t8);

struct MsVertex {
  float4 position : SV_Position;
  float3 normal : NORMAL;
  float2 uv : TEXCOORD0;
  nointerpolation uint material_index : MATERIAL;
};

[outputtopology("triangle")]
[numthreads(MS_GROUP_SIZE, 1, 1)]
void MSMain(uint group_thread_id : SV_GroupThreadID, uint group_id : SV_GroupID,
            in payload Payload payload, out vertices MsVertex out_vertices[MAX_VERTICES],
            out indices uint3 out_triangles[MAX_TRIANGLES]) {
  uint meshlet_index = payload.meshlet_indices[group_id];
  Instance instance = instances[payload.instance_index];
  MeshletData meshlet = meshlets[meshlet_index];

  SetMeshOutputCounts(meshlet.vertex_count, meshlet.triangle_count);

  for (uint v = group_thread_id; v < meshlet.vertex_count; v += MS_GROUP_SIZE) {
    uint vertex_index = meshlet_vertices[meshlet.vertex_offset + v];
    Vertex vertex = vertices[vertex_index];

    float4 world_position = mul(float4(vertex.position, 1.0), instance.world);
    MsVertex output;
    output.position = mul(world_position, view_projection);
    output.normal = mul(vertex.normal, (float3x3)instance.world);
    output.uv = vertex.uv;
    output.material_index = instance.material_index;
    out_vertices[v] = output;
  }

  for (uint t = group_thread_id; t < meshlet.triangle_count; t += MS_GROUP_SIZE) {
    uint packed = meshlet_triangles[meshlet.triangle_offset + t];
    out_triangles[t] = uint3(packed & 0xFF, (packed >> 8) & 0xFF, (packed >> 16) & 0xFF);
  }
}
```

| 点 | 説明 |
| --- | --- |
| **`[outputtopology("triangle")]`** | **三角形リスト**を出力 |
| **`in payload Payload payload`** | **AS からのペイロード**。**`group_id` がペイロードの何番目か** |
| **`out vertices` / `out indices`** | **出力する頂点配列と三角形（頂点番号の 3 つ組）配列**。**上限は、64 頂点・124 三角形** |
| **`SetMeshOutputCounts`** | **実際に出力する頂点数・三角形数を宣言**。**全スレッドが最初に呼ぶ** |
| **`v += MS_GROUP_SIZE`** | **スレッドが 128 個**で、**頂点は最大 64 個**なので、**足りる**が**一般的な形のループ**で**書く** |
| **頂点の変換** | **頂点シェーダーと同じ**（**ワールド → ビュー射影**）。**行ベクトル規約** |

**ピクセル シェーダー**は、**従来と同じ**ものが**そのまま使えます**（**`MsVertex` がピクセル シェーダーの入力**）。

## PSO の作成（メッシュ シェーダー）

<strong>メッシュ シェーダーの PSO は、`D3D12_GRAPHICS_PIPELINE_STATE_DESC` では作れず、「パイプライン ステート ストリーム」</strong>を使います。

```cpp
struct MeshPipelineStateStream {
  CD3DX12_PIPELINE_STATE_STREAM_ROOT_SIGNATURE root_signature;
  CD3DX12_PIPELINE_STATE_STREAM_AS amplification_shader;
  CD3DX12_PIPELINE_STATE_STREAM_MS mesh_shader;
  CD3DX12_PIPELINE_STATE_STREAM_PS pixel_shader;
  CD3DX12_PIPELINE_STATE_STREAM_RASTERIZER rasterizer;
  CD3DX12_PIPELINE_STATE_STREAM_BLEND_DESC blend;
  CD3DX12_PIPELINE_STATE_STREAM_DEPTH_STENCIL depth_stencil;
  CD3DX12_PIPELINE_STATE_STREAM_RENDER_TARGET_FORMATS render_target_formats;
  CD3DX12_PIPELINE_STATE_STREAM_DEPTH_STENCIL_FORMAT depth_stencil_format;
  CD3DX12_PIPELINE_STATE_STREAM_SAMPLE_DESC sample_desc;
  CD3DX12_PIPELINE_STATE_STREAM_SAMPLE_MASK sample_mask;
};

ComPtr<ID3D12PipelineState> Renderer::CreateMeshPso(ID3DBlob* as, ID3DBlob* ms, ID3DBlob* ps) {
  D3D12_RT_FORMAT_ARRAY rtv_formats = {};
  rtv_formats.NumRenderTargets = 1;
  rtv_formats.RTFormats[0] = DXGI_FORMAT_R8G8B8A8_UNORM;

  DXGI_SAMPLE_DESC sample_desc = {1, 0};

  MeshPipelineStateStream stream;
  stream.root_signature = mesh_root_signature_.Get();
  stream.amplification_shader = CD3DX12_SHADER_BYTECODE(as);
  stream.mesh_shader = CD3DX12_SHADER_BYTECODE(ms);
  stream.pixel_shader = CD3DX12_SHADER_BYTECODE(ps);
  stream.rasterizer = CD3DX12_RASTERIZER_DESC(D3D12_DEFAULT);
  stream.blend = CD3DX12_BLEND_DESC(D3D12_DEFAULT);
  stream.depth_stencil = CD3DX12_DEPTH_STENCIL_DESC(D3D12_DEFAULT);
  stream.render_target_formats = rtv_formats;
  stream.depth_stencil_format = DXGI_FORMAT_D32_FLOAT;
  stream.sample_desc = sample_desc;
  stream.sample_mask = UINT_MAX;

  D3D12_PIPELINE_STATE_STREAM_DESC stream_desc = {sizeof(stream), &stream};
  ComPtr<ID3D12PipelineState> pso;
  ThrowIfFailed(device2_->CreatePipelineState(&stream_desc, IID_PPV_ARGS(&pso)));
  return pso;
}
```

| 点 | 説明 |
| --- | --- |
| **`ID3D12Device2`** | <strong>`CreatePipelineState`（ストリーム版）</strong>は、**`ID3D12Device2`** のメソッド。**`device_.As(&device2_)`** で**取得** |
| **`CD3DX12_PIPELINE_STATE_STREAM_*`** | **`d3dx12.h` のストリーム用ヘルパー<strong>。</strong>サブオブジェクトごとに、型が決まっている** |
| **頂点シェーダー・入力レイアウトなし** | **メッシュ シェーダーは、IA を使わない**ので**頂点バッファの入力レイアウトは不要** |
| **ルート シグネチャ** | **IA フラグ（`ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT`）は付けない** |
| **コマンド リスト** | **`ID3D12GraphicsCommandList6`**（`DispatchMesh` を持つ）を**使う** |

### 対応の確認

```cpp
D3D12_FEATURE_DATA_D3D12_OPTIONS7 options7 = {};
bool supports_mesh_shader =
    SUCCEEDED(device->CheckFeatureSupport(D3D12_FEATURE_D3D12_OPTIONS7, &options7,
                                          sizeof(options7))) &&
    options7.MeshShaderTier != D3D12_MESH_SHADER_TIER_NOT_SUPPORTED;
```

<strong>対応していない GPU には、従来の頂点シェーダー経路（[ExecuteIndirect](execute-indirect.md)）</strong>を**フォールバック**として**用意**します。

## ExecuteIndirect で DispatchMesh

**インスタンスごとに、AS を起動**する**コマンド**を、**カリング CS が書き**、**`ExecuteIndirect`** で**実行**します。

```cpp
struct MeshIndirectCommand {
  uint32_t instance_index;
  D3D12_DISPATCH_MESH_ARGUMENTS dispatch;
};
static_assert(sizeof(MeshIndirectCommand) == 16);

ComPtr<ID3D12CommandSignature> Renderer::CreateMeshCommandSignature() {
  D3D12_INDIRECT_ARGUMENT_DESC arguments[2] = {};
  arguments[0].Type = D3D12_INDIRECT_ARGUMENT_TYPE_CONSTANT;
  arguments[0].Constant.RootParameterIndex = kRootMeshConstants;
  arguments[0].Constant.DestOffsetIn32BitValues = 0;
  arguments[0].Constant.Num32BitValuesToSet = 1;
  arguments[1].Type = D3D12_INDIRECT_ARGUMENT_TYPE_DISPATCH_MESH;

  D3D12_COMMAND_SIGNATURE_DESC desc = {};
  desc.ByteStride = sizeof(MeshIndirectCommand);
  desc.NumArgumentDescs = 2;
  desc.pArgumentDescs = arguments;

  ComPtr<ID3D12CommandSignature> signature;
  ThrowIfFailed(device_->CreateCommandSignature(&desc, mesh_root_signature_.Get(),
                                                IID_PPV_ARGS(&signature)));
  return signature;
}
```

```hlsl
struct MeshIndirectCommand {
  uint instance_index;
  uint thread_group_count_x;
  uint thread_group_count_y;
  uint thread_group_count_z;
};

command.instance_index = instance_index;
command.thread_group_count_x = (mesh.meshlet_count + AS_GROUP_SIZE - 1) / AS_GROUP_SIZE;
command.thread_group_count_y = 1;
command.thread_group_count_z = 1;
```

| 点 | 説明 |
| --- | --- |
| **`D3D12_DISPATCH_MESH_ARGUMENTS`** | **`ThreadGroupCountX/Y/Z`**（12 バイト）。**AS のグループ数** |
| **グループ数** | **AS 1 グループが、32 メッシュレット**を扱うので、**`ceil(meshlet_count / 32)`** |
| **グループ数の上限** | **X が 65,535 以下**（**1 次元の上限**）。**総数は 2^22 以下**。**非常に大きなメッシュは、Y にも分ける** |
| <strong>`draw_instance_index`（AS）</strong> | **コマンドごとのルート定数**。**AS が参照** |

**描画ループ**は、**`ExecuteIndirect` を、`ID3D12GraphicsCommandList6`** の**メッシュ PSO**で**呼ぶ**だけです。

## 効果とトレードオフ

| 利点 | 内容 |
| --- | --- |
| **細かいカリング** | **巨大メッシュの見えない部分**を**メッシュレット単位**で**除外** |
| **頂点処理の効率** | **メッシュレット内の頂点を、1 回だけ変換**し、**三角形で再利用**（**頂点キャッシュに頼らない**） |
| **IA が不要** | **入力アセンブラの制約**（インデックス フェッチ）が**ない** |
| **LOD との相性** | <strong>メッシュレット単位の LOD（クラスタ LOD、Nanite 的）</strong>の**基礎** |

| 注意点 | 内容 |
| --- | --- |
| **対応 GPU** | **メッシュ シェーダー対応**（NVIDIA Turing 以降、AMD RDNA2 以降、Intel Arc など） |
| **小さなメッシュ** | **AS・MS 起動のオーバーヘッド**のほうが**大きい**ことがある。**大きなメッシュ**から**効果** |
| **前処理** | **メッシュレット生成**が**必要**（**ビルド時に、meshoptimizer**） |
| **スキニング・頂点アニメ** | **MS で行うか、事前にコンピュートで計算**する（**複雑**） |

## よくあるミス

??? failure "DispatchMesh を、スレッドごとに別の値で呼んで、動作が未定義になる"
    **グループ内で一様に**、**`GroupMemoryBarrierWithGroupSync` の後**で**呼ぶ**。

??? failure "WavePrefixCountBits で出力位置を決め、ウェーブ サイズが 32 未満の GPU で壊れる"
    **`groupshared` のカウンタ ＋ `InterlockedAdd`**。

??? failure "SetMeshOutputCounts を呼ばずに出力して、何も描かれない"
    **全スレッドが出力前に呼ぶ**。

??? failure "メッシュレットの頂点・三角形が上限（64/124）を超える"
    **meshoptimizer に、同じ上限を渡す**。**HLSL の配列サイズと一致**させる。

??? failure "PSO の作成が失敗する（IA フラグ・入力レイアウトを指定している）"
    **メッシュ シェーダーの PSO は、IA 関連を指定しない**。**ストリーム版**で作る。

??? failure "背面コーンの式を、座標系（左手系・行ベクトル）に合わせず、見える面を消す"
    **ワールド空間でコーン軸を変換してから判定**する。**視線は `center − camera`**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メッシュレット ＝ <strong>最大 64 頂点・124 三角形の小さな塊</strong>。<strong>境界球と背面コーン</strong>を持つ（<strong>meshoptimizer</strong> で作る）
    - [x] <strong>増幅シェーダー</strong>が<strong>メッシュレットをカリング</strong>し、<strong>生き残りだけ</strong>を<strong>`DispatchMesh`</strong> で<strong>メッシュ シェーダーに渡す</strong>
    - [x] <strong>メッシュ シェーダー</strong>：<strong>1 グループ ＝ 1 メッシュレット</strong>。<strong>`SetMeshOutputCounts`</strong> と<strong>頂点・三角形の出力</strong>
    - [x] <strong>PSO は、パイプライン ステート ストリーム</strong>で作る。<strong>IA は使わない</strong>
    - [x] <strong>`ExecuteIndirect` の引数に `DISPATCH_MESH`</strong>。<strong>インスタンスごとに AS を起動</strong>

## 参考

- Microsoft, "Mesh Shader"（DirectX-Specs）
- Kapoulkine, "meshoptimizer"（meshopt_buildMeshlets）
- Haar, Aaltonen, "GPU-Driven Rendering Pipelines"（SIGGRAPH 2015、クラスタ カリング）
- Karis et al., "A Deep Dive into Nanite Virtualized Geometry"（SIGGRAPH 2021）

## 関連ページ

- [GPU Driven（D3D12 詳細）](index.md)
- [カリング（コンピュート）](culling.md)
- [ExecuteIndirect](execute-indirect.md)
- [メッシュ シェーダー](../mesh-shaders.md)
- [LOD](../lod.md)
