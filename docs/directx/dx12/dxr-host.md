---
title: DXR Host Setup
tags:
  - DirectX
---

# DXR Host Setup

レイトレーシングのページ（RTAO、反射、DDGI、影）には `TraceRay` や `RayQuery` を使う HLSL が、出てきます。これを動かすには <strong>DirectX 12 の DXR</strong>（DirectX Raytracing）の、ホスト側の準備が必要です。DirectX 11 にはレイトレーシングの API がありません。このページは準備の全体像と最小のコードを示します。

!!! note "DirectX 11 との関係"
    このサイトの描画のコードは基本的に DirectX 11 です。レイトレーシングの部分だけ DirectX 12 が、必要になります。DirectX 11 のレンダラーに DXR を足すことはできないので、<strong>レイトレーシングを使うならレンダラー全体を D3D12 にする</strong>か D3D11 向けの代用（距離場・ボクセル・スクリーン空間）を、使います。

## 全体の流れ

| 順 | 内容 |
| --- | --- |
| ① | GPU が DXR に対応しているかを調べる |
| ② | メッシュごとに BLAS（下位の加速構造）を作る |
| ③ | インスタンスを並べて、TLAS（上位の加速構造）を作る（毎フレーム） |
| ④ | レイトレーシングのパイプライン（ステート オブジェクト）を作る |
| ⑤ | シェーダー テーブルを作る |
| ⑥ | `DispatchRays` を呼ぶ（または `RayQuery` で、計算シェーダーからインライン） |

## ① 対応の確認

```cpp
// D3D12 の、機能の確認: RaytracingTier が、1.0 以上か（1.1 なら、RayQuery も、使える）。
D3D12_FEATURE_DATA_D3D12_OPTIONS5 options5 = {};
device->CheckFeatureSupport(D3D12_FEATURE_D3D12_OPTIONS5, &options5, sizeof(options5));
bool dxr_supported = options5.RaytracingTier >= D3D12_RAYTRACING_TIER_1_0;
bool inline_supported = options5.RaytracingTier >= D3D12_RAYTRACING_TIER_1_1;     // RayQuery
```

`RaytracingTier` が `NOT_SUPPORTED` の GPU ではレイトレーシングの経路を使わず代用の方式（SSR、シャドウ マップ、プローブ）に切り替えます。

## ② BLAS：メッシュ 1 つぶんの加速構造

```cpp
// 三角形メッシュを、BLAS にする。頂点バッファと、インデックス バッファは、すでに、GPU 上にある前提。
D3D12_RAYTRACING_GEOMETRY_DESC geometry = {};
geometry.Type = D3D12_RAYTRACING_GEOMETRY_TYPE_TRIANGLES;
geometry.Flags = D3D12_RAYTRACING_GEOMETRY_FLAG_OPAQUE;                         // 不透明: any hit シェーダーを、呼ばない（速い）
geometry.Triangles.VertexBuffer.StartAddress = vertex_buffer->GetGPUVirtualAddress();
geometry.Triangles.VertexBuffer.StrideInBytes = sizeof(Vertex);
geometry.Triangles.VertexFormat = DXGI_FORMAT_R32G32B32_FLOAT;
geometry.Triangles.VertexCount = vertex_count;
geometry.Triangles.IndexBuffer = index_buffer->GetGPUVirtualAddress();
geometry.Triangles.IndexFormat = DXGI_FORMAT_R32_UINT;
geometry.Triangles.IndexCount = index_count;
```

メッシュの頂点の位置（`R32G32B32_FLOAT`）とインデックスを指します。不透明なメッシュに `FLAG_OPAQUE` を付けると、`any hit` シェーダー（アルファ テストなど）が、呼ばれず速くなります。

```cpp
// 必要なメモリの大きさを、問い合わせて、作業用バッファと、結果バッファを、確保してから、ビルドする。
D3D12_BUILD_RAYTRACING_ACCELERATION_STRUCTURE_INPUTS inputs = {};
inputs.Type = D3D12_RAYTRACING_ACCELERATION_STRUCTURE_TYPE_BOTTOM_LEVEL;
inputs.Flags = D3D12_RAYTRACING_ACCELERATION_STRUCTURE_BUILD_FLAG_PREFER_FAST_TRACE;
inputs.NumDescs = 1;
inputs.DescsLayout = D3D12_ELEMENTS_LAYOUT_ARRAY;
inputs.pGeometryDescs = &geometry;

D3D12_RAYTRACING_ACCELERATION_STRUCTURE_PREBUILD_INFO prebuild = {};
device5->GetRaytracingAccelerationStructurePrebuildInfo(&inputs, &prebuild);
// prebuild.ScratchDataSizeInBytes（作業用）と ResultDataMaxSizeInBytes（結果）の、UAV バッファを、作る。

D3D12_BUILD_RAYTRACING_ACCELERATION_STRUCTURE_DESC build = {};
build.Inputs = inputs;
build.ScratchAccelerationStructureData = scratch->GetGPUVirtualAddress();
build.DestAccelerationStructureData = blas->GetGPUVirtualAddress();
command_list4->BuildRaytracingAccelerationStructure(&build, 0, nullptr);
// ビルドの完了を待つ: UAV バリアを、入れる（TLAS が、BLAS を、使う前）。
```

静的なメッシュは 1 回だけビルドします。`PREFER_FAST_TRACE` はビルドが遅くなる代わりにトレースが速い設定です。スキニングするメッシュは `ALLOW_UPDATE` を付けて、毎フレーム、更新（refit）します。

## ③ TLAS：インスタンスを並べる

```cpp
// インスタンス（位置・向き・大きさを持った、BLAS の配置）の配列を、毎フレーム作り、TLAS をビルドする。
D3D12_RAYTRACING_INSTANCE_DESC instance = {};
std::memcpy(instance.Transform, object_to_world_3x4, sizeof(instance.Transform));    // 3×4 行列（行優先）
instance.InstanceID = object_index;                                                   // ヒット シェーダーで、InstanceID() で取れる
instance.InstanceMask = 0xFF;                                                         // TraceRay の、マスクと、AND される
instance.InstanceContributionToHitGroupIndex = material_index;                        // シェーダー テーブルの、どの行を使うか
instance.AccelerationStructure = blas->GetGPUVirtualAddress();
// 全インスタンスを、アップロード バッファに、並べて、TLAS のビルドを呼ぶ（Type = TOP_LEVEL）。
```

同じ BLAS を何度も別の位置に置けるので同じ岩・木をメモリを増やさずに並べられます。`InstanceMask` は「このレイはこのインスタンスを無視する」（例: 影のレイは光源を無視）を実現するビットマスクです。

## ④⑤ ステート オブジェクトとシェーダー テーブル

```cpp
// レイトレーシング パイプライン: シェーダー（DXIL ライブラリ）と、ヒット グループ、設定を、まとめて、1 つのオブジェクトにする。
CD3DX12_STATE_OBJECT_DESC desc(D3D12_STATE_OBJECT_TYPE_RAYTRACING_PIPELINE);

auto* lib = desc.CreateSubobject<CD3DX12_DXIL_LIBRARY_SUBOBJECT>();
D3D12_SHADER_BYTECODE bytecode = {dxil_blob->GetBufferPointer(), dxil_blob->GetBufferSize()};
lib->SetDXILLibrary(&bytecode);                                          // RayGen、ClosestHit、Miss を含む

auto* hit_group = desc.CreateSubobject<CD3DX12_HIT_GROUP_SUBOBJECT>();
hit_group->SetClosestHitShaderImport(L"ReflectionClosestHit");
hit_group->SetHitGroupExport(L"HitGroup");
hit_group->SetHitGroupType(D3D12_HIT_GROUP_TYPE_TRIANGLES);

auto* shader_config = desc.CreateSubobject<CD3DX12_RAYTRACING_SHADER_CONFIG_SUBOBJECT>();
shader_config->Config(sizeof(float) * 4 /* ペイロード */, sizeof(float) * 2 /* 重心座標 */);

auto* pipeline_config = desc.CreateSubobject<CD3DX12_RAYTRACING_PIPELINE_CONFIG_SUBOBJECT>();
pipeline_config->Config(2);                                              // 再帰の最大の深さ

auto* global_root = desc.CreateSubobject<CD3DX12_GLOBAL_ROOT_SIGNATURE_SUBOBJECT>();
global_root->SetRootSignature(global_root_signature.Get());              // 全シェーダーで共通のリソース
device5->CreateStateObject(desc, IID_PPV_ARGS(&rt_state_object));
```

ペイロード（`TraceRay` に渡す構造体）の大きさと最大の再帰の深さをここで、決めます。ペイロードを小さくするほど速くなります。ここまでで「どんなシェーダーがありどうつながるか」を GPU に伝えました。

```cpp
// シェーダー テーブル: RayGen・Miss・HitGroup の、「シェーダー識別子」を、並べたバッファ。
Microsoft::WRL::ComPtr<ID3D12StateObjectProperties> props;
rt_state_object.As(&props);
void* raygen_id = props->GetShaderIdentifier(L"ReflectionRayGen");
void* miss_id = props->GetShaderIdentifier(L"Miss");
void* hit_id = props->GetShaderIdentifier(L"HitGroup");
// 各識別子（D3D12_SHADER_IDENTIFIER_SIZE_IN_BYTES = 32）を、64 バイト境界（テーブルの、レコードの、アラインメント）に、並べて、アップロードする。
```

識別子を並べたテーブルを `DispatchRays` に渡すと GPU はレイが何かに当たったとき、テーブルのどの行のヒット グループを呼ぶかを `InstanceContributionToHitGroupIndex` から決めます。マテリアルごとに別のヒット シェーダーを使いたいときは行を増やします。

## ⑥ レイを飛ばす

```cpp
// DispatchRays: 画面の幅×高さの、スレッドで、RayGen シェーダーを、起動する。
command_list4->SetPipelineState1(rt_state_object.Get());
command_list4->SetComputeRootSignature(global_root_signature.Get());
// ... TLAS の SRV、出力 UAV、定数バッファを、ルート シグネチャに、束ねる ...

D3D12_DISPATCH_RAYS_DESC dispatch = {};
dispatch.RayGenerationShaderRecord = {table_address + 0, 64};
dispatch.MissShaderTable = {table_address + 64, 64, 64};
dispatch.HitGroupTable = {table_address + 128, 64, 64};
dispatch.Width = width;
dispatch.Height = height;
dispatch.Depth = 1;
command_list4->DispatchRays(&dispatch);
```

`Width × Height` のスレッドがそれぞれ `RayGen` を実行します。`DispatchRaysIndex()` がそのスレッドの画素の座標です（[Ray Generation](../../graphics/reflections/rt-reflections/ray-generation.md)）。

### インライン レイトレーシング（RayQuery）

ステート オブジェクトやシェーダー テーブルを使わず計算シェーダー（またはピクセル シェーダー）の中から直接、レイを飛ばせます（DXR 1.1）。

```hlsl
// TLAS を、SRV として束ね、シェーダーの中から、レイを飛ばす。
RaytracingAccelerationStructure g_scene : register(t0);

[numthreads(8, 8, 1)]
void ShadowCS(uint3 id : SV_DispatchThreadID) {
  RayDesc ray = MakeShadowRay(id.xy);
  RayQuery<RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH | RAY_FLAG_CULL_NON_OPAQUE> q;
  q.TraceRayInline(g_scene, RAY_FLAG_NONE, 0xFF, ray);
  q.Proceed();
  g_shadow[id.xy] = (q.CommittedStatus() == COMMITTED_NOTHING) ? 1.0 : 0.0;       // 何にも当たらなければ、光が当たる
}
```

影・AO のように「当たったかどうか」だけが必要な場合は `RayQuery` が、簡単です。マテリアルごとにシェーダーを切り替える必要がある（反射、GI）場合はステート オブジェクトとシェーダー テーブルが向いています。

## よくあるミス

??? failure "レイが、どこにも当たらない（全部、外れ）"
    BLAS のビルドの完了を待たずに TLAS をビルドした（UAV バリアが、足りない）。TLAS のインスタンスの変換行列が、転置している（`Transform` は 3×4 の行優先）。`InstanceMask` と `TraceRay` のマスクが重ならない。

??? failure "ヒット シェーダーが、呼ばれないまたは違うマテリアルになる"
    `InstanceContributionToHitGroupIndex` とシェーダー テーブルの並びが、合っていない。`TraceRay` の `RayContributionToHitGroupIndex`・`MultiplierForGeometryContributionToHitGroupIndex` の組み合わせで行が、決まる。

??? failure "毎フレーム、TLAS を作り直して重い"
    静的なメッシュの BLAS を毎フレーム、作っている。BLAS は 1 回だけ。動く物はインスタンスの行列を更新して TLAS だけを再構築する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] DXR は DirectX 12 の機能。DirectX 11 にはない
    - [x] BLAS（メッシュごと 1 回）→ TLAS（インスタンス、毎フレーム）→ ステート オブジェクト → シェーダー テーブル → `DispatchRays`
    - [x] 当たったかだけ知りたい（影・AO）なら `RayQuery` で、計算シェーダーから直接
    - [x] ペイロードは小さく。再帰は浅く
    - [x] 対応していない GPU には、SSR・シャドウ マップなどの代用に切り替える

## 関連ページ

- [D3D11 Pass Recipes](../dx11/pass-recipes.md)
- [Ray-Traced AO (RTAO)](../../graphics/ao/world-space/rtao.md)
- [Ray Generation](../../graphics/reflections/rt-reflections/ray-generation.md)
- [Hit Shading and BVH](../../graphics/reflections/rt-reflections/hit-shading.md)
- [Ray-Traced Shadows](../../graphics/shadows/ray-traced.md)
- [Microsoft Learn: DirectX Raytracing (DXR) Functional Spec](https://microsoft.github.io/DirectX-Specs/d3d/Raytracing.html)
