---
title: DXR Host Setup
tags:
  - DirectX
---

# DXR Host Setup

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
</div>

影、反射、AO、GI のようなレイトレーシングの解説（RTAO、DDGI など）には `TraceRay` や `RayQuery` を使う HLSL が出てきます。このシェーダーを動かすには D3D12 の機能である **DXR**（DirectX Raytracing）の、ホスト側の準備が必要です。

シェーダーを書くだけでは光線は飛びません。GPU に光線を当てる相手の形を教えるために**加速構造**というデータを作ります。シェーダーどうしのつながりを教える**ステート オブジェクト**とどのシェーダーを呼ぶかを決める**シェーダー テーブル**も要ります。このページはその全体像と最小のコードを示します。

!!! tip "ポイント"
    - 準備の順番は BLAS（メッシュごと）、TLAS（インスタンス、毎フレーム）、ステート オブジェクト、シェーダー テーブル、`DispatchRays`。
    - 当たったかどうかだけが欲しい影や AO は `RayQuery` で、計算シェーダーから直接飛ばせる。
    - ペイロード（`TraceRay` に渡す構造体）は小さく、再帰は浅くする。
    - GPU が対応していないときは、SSR やシャドウ マップなどの代用に切り替える。

!!! info "このページを読む前に"
    GPU の機能の確認は [Device and Factory](factory-device.md#checkfeaturesupport)、バッファの作り方は [Heaps and Resources](heaps-resources.md)、UAV バリアは [Resource Barrier](resource-barrier.md)、コンピュート シェーダーの基本は [Compute Shader](compute-shader.md) で説明しています。DXR のシェーダー側は [Ray Generation](../../graphics/reflections/rt-reflections/ray-generation.md) にあります。

## 全体の流れ

準備は 6 つの段階です。

1. GPU が DXR に対応しているかを調べる。
2. メッシュごとに BLAS（下位の加速構造）を作る。
3. インスタンスを並べて TLAS（上位の加速構造）を作る。毎フレーム更新する。
4. レイトレーシングのパイプライン（ステート オブジェクト）を作る。
5. シェーダー テーブルを作る。
6. `DispatchRays` を呼ぶ。または、`RayQuery` で計算シェーダーからインラインで飛ばす。

## 対応しているかを調べる

```cpp
// RaytracingTier が 1.0 以上か。1.1 なら RayQuery も使える。
D3D12_FEATURE_DATA_D3D12_OPTIONS5 options5 = {};
device->CheckFeatureSupport(D3D12_FEATURE_D3D12_OPTIONS5, &options5, sizeof(options5));
bool dxr_supported = options5.RaytracingTier >= D3D12_RAYTRACING_TIER_1_0;
bool inline_supported = options5.RaytracingTier >= D3D12_RAYTRACING_TIER_1_1;  // RayQuery
```

`RaytracingTier` が `NOT_SUPPORTED` の GPU ではレイトレーシングの経路を使わず代用の方式（SSR、シャドウ マップ、プローブ）へ切り替えます。

## BLAS でメッシュ 1 つぶんの加速構造を作る

まず、三角形メッシュを説明する構造体を作ります。頂点バッファとインデックス バッファは、すでに GPU 上にある前提です。

```cpp
D3D12_RAYTRACING_GEOMETRY_DESC geometry = {};
geometry.Type = D3D12_RAYTRACING_GEOMETRY_TYPE_TRIANGLES;
geometry.Flags = D3D12_RAYTRACING_GEOMETRY_FLAG_OPAQUE;  // 不透明。any hit シェーダーを呼ばないので速い
geometry.Triangles.VertexBuffer.StartAddress = vertex_buffer->GetGPUVirtualAddress();
geometry.Triangles.VertexBuffer.StrideInBytes = sizeof(Vertex);
geometry.Triangles.VertexFormat = DXGI_FORMAT_R32G32B32_FLOAT;
geometry.Triangles.VertexCount = vertex_count;
geometry.Triangles.IndexBuffer = index_buffer->GetGPUVirtualAddress();
geometry.Triangles.IndexFormat = DXGI_FORMAT_R32_UINT;
geometry.Triangles.IndexCount = index_count;
```

頂点の位置（`R32G32B32_FLOAT`）とインデックスを指します。不透明なメッシュには `FLAG_OPAQUE` を付けます。アルファ テストのための any hit シェーダーが呼ばれなくなり速くなります。

次に、必要なメモリの大きさを問い合わせて、作業用のバッファと結果のバッファを確保してから、ビルドします。

```cpp
D3D12_BUILD_RAYTRACING_ACCELERATION_STRUCTURE_INPUTS inputs = {};
inputs.Type = D3D12_RAYTRACING_ACCELERATION_STRUCTURE_TYPE_BOTTOM_LEVEL;
inputs.Flags = D3D12_RAYTRACING_ACCELERATION_STRUCTURE_BUILD_FLAG_PREFER_FAST_TRACE;
inputs.NumDescs = 1;
inputs.DescsLayout = D3D12_ELEMENTS_LAYOUT_ARRAY;
inputs.pGeometryDescs = &geometry;

D3D12_RAYTRACING_ACCELERATION_STRUCTURE_PREBUILD_INFO prebuild = {};
device5->GetRaytracingAccelerationStructurePrebuildInfo(&inputs, &prebuild);
// prebuild.ScratchDataSizeInBytes（作業用）と ResultDataMaxSizeInBytes（結果）の UAV バッファを作る。

D3D12_BUILD_RAYTRACING_ACCELERATION_STRUCTURE_DESC build = {};
build.Inputs = inputs;
build.ScratchAccelerationStructureData = scratch->GetGPUVirtualAddress();
build.DestAccelerationStructureData = blas->GetGPUVirtualAddress();
command_list4->BuildRaytracingAccelerationStructure(&build, 0, nullptr);
// ビルドの完了を待つために UAV バリアを入れる（TLAS が BLAS を使う前）。
```

静的なメッシュは 1 回だけビルドします。`PREFER_FAST_TRACE` はビルドが遅くなる代わりに飛ばすときが速くなる設定です。スキニングするメッシュは `ALLOW_UPDATE` を付けて、毎フレーム更新（refit）します。

## TLAS でインスタンスを並べる

BLAS はメッシュの形です。それをシーンのどこにどの向きで置くかを決めるのが、TLAS のインスタンスです。毎フレーム作ります。

```cpp
D3D12_RAYTRACING_INSTANCE_DESC instance = {};
std::memcpy(instance.Transform, object_to_world_3x4, sizeof(instance.Transform));  // 3x4 行列（行優先）
instance.InstanceID = object_index;           // ヒット シェーダーで InstanceID() として取れる
instance.InstanceMask = 0xFF;                 // TraceRay のマスクと AND される
instance.InstanceContributionToHitGroupIndex = material_index;  // シェーダー テーブルのどの行を使うか
instance.AccelerationStructure = blas->GetGPUVirtualAddress();
// 全インスタンスをアップロード バッファへ並べて、TLAS のビルドを呼ぶ（Type は TOP_LEVEL）。
```

同じ BLAS を何度も別の位置に置けます。同じ岩や木をメモリを増やさずに並べられます。`InstanceMask` は「このレイはこのインスタンスを無視する」を実現するビットマスクです（例：影のレイは光源を無視する）。

## ステート オブジェクトとシェーダー テーブル

レイトレーシングのパイプラインはシェーダー（DXIL のライブラリ）、ヒット グループ、設定をまとめて 1 つのオブジェクトにします。`D3D12_STATE_SUBOBJECT` を並べてそれぞれ作った構造体を指します。

```cpp
// 1. DXIL のライブラリ。RayGen、ClosestHit、Miss を含む。
D3D12_DXIL_LIBRARY_DESC lib_desc = {};
lib_desc.DXILLibrary = {dxil_blob->GetBufferPointer(), dxil_blob->GetBufferSize()};

// 2. ヒット グループ。三角形に当たったとき、どのシェーダーを呼ぶか。
D3D12_HIT_GROUP_DESC hit_desc = {};
hit_desc.HitGroupExport = L"HitGroup";
hit_desc.Type = D3D12_HIT_GROUP_TYPE_TRIANGLES;
hit_desc.ClosestHitShaderImport = L"ReflectionClosestHit";

// 3. ペイロードと属性の大きさ。4. 再帰の最大の深さ。5. 全シェーダーで共通のルート シグネチャ。
D3D12_RAYTRACING_SHADER_CONFIG shader_config = {sizeof(float) * 4 /* ペイロード */, sizeof(float) * 2 /* 重心座標 */};
D3D12_RAYTRACING_PIPELINE_CONFIG pipeline_config = {2};
D3D12_GLOBAL_ROOT_SIGNATURE global_root = {global_root_signature.Get()};

D3D12_STATE_SUBOBJECT subobjects[5] = {};
subobjects[0] = {D3D12_STATE_SUBOBJECT_TYPE_DXIL_LIBRARY, &lib_desc};
subobjects[1] = {D3D12_STATE_SUBOBJECT_TYPE_HIT_GROUP, &hit_desc};
subobjects[2] = {D3D12_STATE_SUBOBJECT_TYPE_RAYTRACING_SHADER_CONFIG, &shader_config};
subobjects[3] = {D3D12_STATE_SUBOBJECT_TYPE_RAYTRACING_PIPELINE_CONFIG, &pipeline_config};
subobjects[4] = {D3D12_STATE_SUBOBJECT_TYPE_GLOBAL_ROOT_SIGNATURE, &global_root};

D3D12_STATE_OBJECT_DESC desc = {};
desc.Type = D3D12_STATE_OBJECT_TYPE_RAYTRACING_PIPELINE;
desc.NumSubobjects = ARRAYSIZE(subobjects);
desc.pSubobjects = subobjects;
device5->CreateStateObject(&desc, IID_PPV_ARGS(&rt_state_object));
```

ペイロードの大きさと再帰の最大の深さをここで決めます。ペイロードが小さいほど速くなります。ここまでで「どんなシェーダーがありどうつながるか」を GPU に伝えました。

次に、シェーダー テーブルを作ります。RayGen、Miss、HitGroup の「シェーダー識別子」を並べたバッファです。

```cpp
Microsoft::WRL::ComPtr<ID3D12StateObjectProperties> props;
rt_state_object.As(&props);
void* raygen_id = props->GetShaderIdentifier(L"ReflectionRayGen");
void* miss_id = props->GetShaderIdentifier(L"Miss");
void* hit_id = props->GetShaderIdentifier(L"HitGroup");
// 各識別子（D3D12_SHADER_IDENTIFIER_SIZE_IN_BYTES = 32 バイト）を
// 64 バイトの境界（テーブルのレコードのアラインメント）に並べて、アップロードする。
```

識別子を並べたテーブルを `DispatchRays` に渡すと GPU は光線が何かに当たったとき、テーブルのどの行のヒット グループを呼ぶかを `InstanceContributionToHitGroupIndex` から決めます。マテリアルごとに別のヒット シェーダーを使いたいときは、行を増やします。

## 光線を飛ばす

```cpp
command_list4->SetPipelineState1(rt_state_object.Get());
command_list4->SetComputeRootSignature(global_root_signature.Get());
// ... TLAS の SRV、出力の UAV、定数バッファをルート シグネチャへ結ぶ ...

D3D12_DISPATCH_RAYS_DESC dispatch = {};
dispatch.RayGenerationShaderRecord = {table_address + 0, 64};
dispatch.MissShaderTable = {table_address + 64, 64, 64};
dispatch.HitGroupTable = {table_address + 128, 64, 64};
dispatch.Width = width;
dispatch.Height = height;
dispatch.Depth = 1;
command_list4->DispatchRays(&dispatch);
```

`Width × Height` のスレッドがそれぞれ `RayGen` を実行します。`DispatchRaysIndex()` がそのスレッドの画素の座標です。

### インライン レイトレーシング（RayQuery）

ステート オブジェクトやシェーダー テーブルを使わずにコンピュート シェーダー（またはピクセル シェーダー）の中から、直接光線を飛ばせます（DXR 1.1）。

```hlsl
RaytracingAccelerationStructure g_scene : register(t0);  // TLAS を SRV として結ぶ

[numthreads(8, 8, 1)]
void ShadowCS(uint3 id : SV_DispatchThreadID) {
  RayDesc ray = MakeShadowRay(id.xy);
  RayQuery<RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH | RAY_FLAG_CULL_NON_OPAQUE> q;
  q.TraceRayInline(g_scene, RAY_FLAG_NONE, 0xFF, ray);
  q.Proceed();
  g_shadow[id.xy] = (q.CommittedStatus() == COMMITTED_NOTHING) ? 1.0 : 0.0;  // 何にも当たらなければ光が当たる
}
```

影や AO のように「当たったかどうか」だけが必要なときは、`RayQuery` が簡単です。マテリアルごとにシェーダーを切り替えたい反射や GI では、ステート オブジェクトとシェーダー テーブルが向いています。

## よくあるミス

??? failure "光線がどこにも当たらない（全部外れる）"
    BLAS のビルドの完了を待たずに TLAS をビルドしています（UAV バリアが足りません）。インスタンスの変換行列が転置している場合もあります（`Transform` は 3×4 の行優先です）。`InstanceMask` と `TraceRay` のマスクが重なっていない場合も当たりません。

??? failure "ヒット シェーダーが呼ばれない、または違うマテリアルになる"
    `InstanceContributionToHitGroupIndex` とシェーダー テーブルの並びが合っていません。`TraceRay` の `RayContributionToHitGroupIndex` と `MultiplierForGeometryContributionToHitGroupIndex` の組み合わせで、行が決まります。

??? failure "毎フレーム BLAS を作り直して重い"
    静的なメッシュの BLAS を毎フレーム作っています。BLAS は 1 回だけです。動く物はインスタンスの行列を更新して、TLAS だけを再構築します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] DXR は D3D12 の機能。使う前に `CheckFeatureSupport` で対応を確認する
    - [x] BLAS（メッシュごとに 1 回）、TLAS（インスタンス、毎フレーム）、ステート オブジェクト、シェーダー テーブル、`DispatchRays` の順に進む
    - [x] 当たったかだけが欲しい影や AO は `RayQuery` で、計算シェーダーから直接飛ばす
    - [x] ペイロードは小さく、再帰は浅くする
    - [x] 対応していない GPU には、SSR やシャドウ マップなどの代用へ切り替える

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Device and Factory](factory-device.md)
- [Compute Shader](compute-shader.md)
- [Ray-Traced AO (RTAO)](../../graphics/ao/world-space/rtao.md)
- [Ray Generation](../../graphics/reflections/rt-reflections/ray-generation.md)
- [Hit Shading and BVH](../../graphics/reflections/rt-reflections/hit-shading.md)
- [Ray-Traced Shadows](../../graphics/shadows/ray-traced.md)
- [Microsoft Learn: DirectX Raytracing (DXR) Functional Spec](https://microsoft.github.io/DirectX-Specs/d3d/Raytracing.html)
