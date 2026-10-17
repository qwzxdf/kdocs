---
title: ExecuteIndirect
tags:
  - 描画最適化
---

# ExecuteIndirect

カリング CS が書いた**コマンド バッファ**を、**GPU が自分で読んで描画する**のが **`ExecuteIndirect`** です。**CPU は「描画の回数」を知らなくて済みます**。このページでは、**コマンド シグネチャの作り方**・**ルート定数をコマンドごとに書き換える**仕組み・**描画用のルート シグネチャとシェーダー**・**PSO バケットごとの呼び出し**・**最大数とカウント バッファ**・**ExecuteIndirect の後のルート状態の注意**を、**実コード**で解説します。

!!! tip "ポイント"
    - <strong>コマンド シグネチャ</strong> ＝ <strong>「1 コマンドの中身の並び」</strong>（ルート定数 → Draw など）を<strong>GPU に教える</strong>オブジェクト。
    - <strong>`IndirectCommand` のメモリ配置</strong>と、<strong>コマンド シグネチャ</strong>は<strong>完全に一致</strong>させる。
    - <strong>ルート定数でインスタンス番号</strong>を渡す。<strong>シェーダーはその番号で配列を引く</strong>。
    - <strong>`ExecuteIndirect(signature, 最大数, 引数バッファ, オフセット, カウント バッファ, オフセット)`</strong>。<strong>実行回数 ＝ min(カウント, 最大数)</strong>。
    - <strong>PSO は、コマンドの中で変えられない</strong>。<strong>PSO ごとに、1 回ずつ</strong>呼ぶ。
    - <strong>ExecuteIndirect で書き換えたルート引数は、呼び出し後に「不定」</strong>。<strong>必ず再設定</strong>。

## コマンド シグネチャ

<strong>`ExecuteIndirect` は、「バッファの中のコマンド列」</strong>を**読みます**。**1 コマンドがどんな引数の並びか**を**事前に定義**するのが、**コマンド シグネチャ**です。

<svg class="fig illust" viewBox="0 0 780 190" role="img" aria-label="IndirectCommand の配置">
<text x="20" y="24" class="fig-title">1 コマンド ＝ 24 バイト：ルート定数 1 ワード ＋ DrawIndexedInstanced の引数 5 ワード</text>
<g stroke="currentColor" stroke-width="2"><rect x="40" y="50" width="100" height="44" fill="rgba(229,170,40,0.3)"/><rect x="140" y="50" width="100" height="44" fill="rgba(76,139,245,0.2)"/><rect x="240" y="50" width="100" height="44" fill="rgba(76,139,245,0.2)"/><rect x="340" y="50" width="100" height="44" fill="rgba(76,139,245,0.2)"/><rect x="440" y="50" width="100" height="44" fill="rgba(76,139,245,0.2)"/><rect x="540" y="50" width="100" height="44" fill="rgba(76,139,245,0.2)"/></g>
<g style="font-size:11px"><text x="50" y="76">instance_index</text><text x="148" y="76">IndexCount</text><text x="248" y="76">InstanceCount</text><text x="348" y="76">StartIndex</text><text x="448" y="76">BaseVertex</text><text x="548" y="76">StartInstance</text></g>
<text x="40" y="124" style="font-size:12px">0 バイト目</text><text x="140" y="124" style="font-size:12px">4</text><text x="540" y="124" style="font-size:12px">20（終わりは 24）</text>
<text x="40" y="156" style="font-size:12px">引数 0：ルート定数（1 ワード）　引数 1：DRAW_INDEXED（5 ワード）　ByteStride ＝ 24</text>
</svg>

```cpp
constexpr uint32_t kRootDrawFrame = 0;
constexpr uint32_t kRootDrawConstants = 1;
constexpr uint32_t kRootDrawInstances = 2;
constexpr uint32_t kRootDrawMaterials = 3;

ComPtr<ID3D12CommandSignature> Renderer::CreateCommandSignature() {
  D3D12_INDIRECT_ARGUMENT_DESC arguments[2] = {};
  arguments[0].Type = D3D12_INDIRECT_ARGUMENT_TYPE_CONSTANT;
  arguments[0].Constant.RootParameterIndex = kRootDrawConstants;
  arguments[0].Constant.DestOffsetIn32BitValues = 0;
  arguments[0].Constant.Num32BitValuesToSet = 1;
  arguments[1].Type = D3D12_INDIRECT_ARGUMENT_TYPE_DRAW_INDEXED;

  D3D12_COMMAND_SIGNATURE_DESC desc = {};
  desc.ByteStride = sizeof(IndirectCommand);
  desc.NumArgumentDescs = 2;
  desc.pArgumentDescs = arguments;
  desc.NodeMask = 0;

  ComPtr<ID3D12CommandSignature> signature;
  ThrowIfFailed(device_->CreateCommandSignature(&desc, draw_root_signature_.Get(),
                                                IID_PPV_ARGS(&signature)));
  return signature;
}
```

| 点 | 説明 |
| --- | --- |
| <strong>`arguments[0]`（`CONSTANT`）</strong> | **ルート定数の値**を**コマンドの先頭 4 バイトから**セットする。**`RootParameterIndex`** は、**描画用ルート シグネチャの、ルート定数パラメータの番号** |
| <strong>`arguments[1]`（`DRAW_INDEXED`）</strong> | <strong>`D3D12_DRAW_INDEXED_ARGUMENTS`（20 バイト）</strong>が**続く** |
| **引数の順序** | **メモリ上の並び ＝ 配列の順序**。**`IndirectCommand` の定義と一致** |
| **`ByteStride`** | **コマンド 1 個の間隔**。**4 の倍数**でなければならない。**24 バイト** |
| **ルート シグネチャを渡す理由** | **引数にルート定数（ルート引数の変更）が含まれる**場合、**どのルート シグネチャに対するものか**を**指定**する必要がある。**含まれない**（Draw のみ）なら **`nullptr`** |
| **`DRAW_INDEXED` は、引数配列の最後** | **Draw / Dispatch 系は、必ず最後**に置く（**1 コマンドに 1 つ**） |

## 描画用のルート シグネチャ

```cpp
ComPtr<ID3D12RootSignature> Renderer::CreateDrawRootSignature() {
  CD3DX12_ROOT_PARAMETER1 params[4];
  params[kRootDrawFrame].InitAsConstantBufferView(0, 0, D3D12_ROOT_DESCRIPTOR_FLAG_NONE,
                                                  D3D12_SHADER_VISIBILITY_ALL);
  params[kRootDrawConstants].InitAsConstants(1, 1, 0, D3D12_SHADER_VISIBILITY_VERTEX);
  params[kRootDrawInstances].InitAsShaderResourceView(0, 0, D3D12_ROOT_DESCRIPTOR_FLAG_NONE,
                                                      D3D12_SHADER_VISIBILITY_VERTEX);
  params[kRootDrawMaterials].InitAsShaderResourceView(2, 0, D3D12_ROOT_DESCRIPTOR_FLAG_NONE,
                                                      D3D12_SHADER_VISIBILITY_PIXEL);

  D3D12_STATIC_SAMPLER_DESC sampler = {};
  sampler.Filter = D3D12_FILTER_ANISOTROPIC;
  sampler.AddressU = D3D12_TEXTURE_ADDRESS_MODE_WRAP;
  sampler.AddressV = D3D12_TEXTURE_ADDRESS_MODE_WRAP;
  sampler.AddressW = D3D12_TEXTURE_ADDRESS_MODE_WRAP;
  sampler.MaxAnisotropy = 8;
  sampler.MaxLOD = D3D12_FLOAT32_MAX;
  sampler.ShaderRegister = 0;
  sampler.ShaderVisibility = D3D12_SHADER_VISIBILITY_PIXEL;

  CD3DX12_VERSIONED_ROOT_SIGNATURE_DESC desc;
  desc.Init_1_1(_countof(params), params, 1, &sampler,
                D3D12_ROOT_SIGNATURE_FLAG_ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT |
                    D3D12_ROOT_SIGNATURE_FLAG_CBV_SRV_UAV_HEAP_DIRECTLY_INDEXED);

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

| パラメータ | 内容 |
| --- | --- |
| <strong>`kRootDrawFrame`（CBV b0）</strong> | **フレーム定数**（ビュー射影行列など） |
| <strong>`kRootDrawConstants`（32 ビット定数 b1）</strong> | **ExecuteIndirect が、コマンドごとに書き換える**（**インスタンス番号 1 ワード**） |
| <strong>`kRootDrawInstances`（SRV t0）</strong> | **インスタンス バッファ**（頂点シェーダーが読む） |
| <strong>`kRootDrawMaterials`（SRV t2）</strong> | **マテリアル バッファ**（ピクセル シェーダーが読む） |
| **`ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT`** | **頂点バッファを使う**（IA）場合に**必要** |
| **静的サンプラー** | **ルート シグネチャに埋め込む**サンプラー（**ヒープ不要**） |

## 頂点シェーダーとピクセル シェーダー

```hlsl
cbuffer FrameConstants : register(b0) {
  float4x4 view_projection;
};

cbuffer DrawConstants : register(b1) {
  uint instance_index;
};

StructuredBuffer<Instance> instances : register(t0);
StructuredBuffer<Material> materials : register(t2);
SamplerState linear_sampler : register(s0);

static const float3 kLightDirection = float3(0.3, 0.8, -0.5);

struct VsOutput {
  float4 position : SV_Position;
  float3 normal : NORMAL;
  float2 uv : TEXCOORD0;
  nointerpolation uint material_index : MATERIAL;
};

VsOutput VSMain(float3 position : POSITION, float3 normal : NORMAL, float2 uv : TEXCOORD0) {
  Instance instance = instances[instance_index];
  float4 world_position = mul(float4(position, 1.0), instance.world);

  VsOutput output;
  output.position = mul(world_position, view_projection);
  output.normal = mul(normal, (float3x3)instance.world);
  output.uv = uv;
  output.material_index = instance.material_index;
  return output;
}

float4 PSMain(VsOutput input) : SV_Target {
  Material material = materials[input.material_index];
  Texture2D<float4> albedo_tex =
      ResourceDescriptorHeap[NonUniformResourceIndex(material.albedo_index)];
  float4 albedo = albedo_tex.Sample(linear_sampler, input.uv) * material.base_color;
  float3 n = normalize(input.normal);
  float lambert = saturate(dot(n, kLightDirection)) * 0.8 + 0.2;
  return float4(albedo.rgb * lambert, albedo.a);
}
```

| 点 | 説明 |
| --- | --- |
| **`instance_index`** | **`ExecuteIndirect` が、コマンドごとにルート定数を書き換えた値**。**シェーダーは通常のルート定数として読む** |
| **`instances[instance_index]`** | **インスタンスの行列・マテリアル番号**を**配列から引く** |
| **`mul(float4(p, 1), W)`、`mul(world_pos, VP)`** | **行ベクトル規約** |
| **`nointerpolation`** | **マテリアル番号は整数**。**補間しない** |
| **法線を同じワールド行列で変換** | **サイトの標準**（右手系アセットの X 反転ルートでも、**位置と同じ行列**）。**非一様スケールがある場合は、逆転置行列** |

## PSO バケットごとの描画

**`ExecuteIndirect` の中では、パイプライン ステート（PSO）を変えられません**。<strong>PSO が違う物（不透明・アルファ テスト・両面など）</strong>は、**カリングの段階でバケットに分け**、**バケットごとに 1 回ずつ呼びます**。

```cpp
void Renderer::RecordDraw(ID3D12GraphicsCommandList* list, D3D12_GPU_VIRTUAL_ADDRESS frame_address) {
  list->SetGraphicsRootSignature(draw_root_signature_.Get());
  ID3D12DescriptorHeap* heaps[] = {bindless_heap_.Get()};
  list->SetDescriptorHeaps(1, heaps);

  list->IASetPrimitiveTopology(D3D_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
  list->IASetVertexBuffers(0, 1, &global_vertex_view_);
  list->IASetIndexBuffer(&global_index_view_);

  list->SetGraphicsRootConstantBufferView(kRootDrawFrame, frame_address);
  list->SetGraphicsRootShaderResourceView(kRootDrawInstances,
                                          instance_buffer_->GetGPUVirtualAddress());
  list->SetGraphicsRootShaderResourceView(kRootDrawMaterials,
                                          material_buffer_->GetGPUVirtualAddress());

  for (uint32_t bucket = 0; bucket < kBucketCount; ++bucket) {
    list->SetPipelineState(bucket_psos_[bucket].Get());
    list->ExecuteIndirect(
        command_signature_.Get(), kMaxCommandsPerBucket, command_buffer_.Get(),
        static_cast<uint64_t>(bucket) * kMaxCommandsPerBucket * sizeof(IndirectCommand),
        count_buffer_.Get(), static_cast<uint64_t>(bucket) * sizeof(uint32_t));
  }
}
```

### ExecuteIndirect の引数

```cpp
void ExecuteIndirect(ID3D12CommandSignature* command_signature, UINT max_command_count,
                     ID3D12Resource* argument_buffer, UINT64 argument_buffer_offset,
                     ID3D12Resource* count_buffer, UINT64 count_buffer_offset);
```

| 引数 | 内容 |
| --- | --- |
| **`command_signature`** | **作成したコマンド シグネチャ** |
| **`max_command_count`** | **実行するコマンド数の上限**。**カウント バッファがある場合、`min(上限, カウント)` が実行数**。**カウントがない（`nullptr`）場合はこの値が実行数** |
| **`argument_buffer`** | **コマンド列が入った、バッファ**（**`INDIRECT_ARGUMENT` 状態**） |
| **`argument_buffer_offset`** | **読み始めのバイト位置**（**4 バイト境界**）。**バケットごとの領域**を指す |
| **`count_buffer`** | **実行数が入った 32 ビット整数**のバッファ（**`INDIRECT_ARGUMENT` 状態**）。**`nullptr` なら、`max_command_count` を使う** |
| **`count_buffer_offset`** | **カウントの位置**（4 バイト境界） |

**カウント バッファ**があるので、**CPU が、「何個描くか」を知らずに**、**GPU が書いたカウントの数だけ**描画されます。**カウントが 0 なら、何も描かれません**。

## ExecuteIndirect 後のルート状態

**`ExecuteIndirect` の引数に、ルート引数の変更（ここではルート定数）が含まれる**場合、**呼び出し後、そのルート引数の値は、不定**になります（**仕様**）。**次の描画でルート定数に依存する**なら、**再設定**が必要です。

| 状況 | 対処 |
| --- | --- |
| <strong>次の `ExecuteIndirect`（同じシグネチャ）</strong> | **ルート定数はコマンドごとに書かれる**ので、**問題ない** |
| **通常の `DrawIndexedInstanced` が続く** | **ルート定数 `b1` を**、**`SetGraphicsRoot32BitConstant` で再設定** |
| **コマンド リストの別の場所** | **ルート シグネチャを再設定**・**全ルート引数を再バインド**すると**安全** |

## 引数バッファの状態と、複数のキュー

| 点 | 内容 |
| --- | --- |
| **バッファの状態** | **`D3D12_RESOURCE_STATE_INDIRECT_ARGUMENT`**（**他の読み取り状態と OR 可能**。**書き込み状態との OR は不可**） |
| **UAV で書いたあと** | **UAV バリアではなく、状態遷移**（`UNORDERED_ACCESS` → `INDIRECT_ARGUMENT`）が**必要** |
| **非同期コンピュート** | **カリングを非同期コンピュート キュー**で**実行**し、**フェンスで同期**して**描画キューで ExecuteIndirect**する構成も可能（<strong>[非同期コンピュート](../async-compute.md)</strong>）。**リソースの所有権・状態の扱いが複雑** |

## 1 コマンドで複数の引数を設定する

**ルート定数だけでなく**、**頂点バッファ ビュー・インデックス バッファ ビュー・ルート CBV/SRV/UAV の GPU アドレス**も、**コマンドごとに設定**できます。

| 引数の種類 | 内容 |
| --- | --- |
| **`D3D12_INDIRECT_ARGUMENT_TYPE_VERTEX_BUFFER_VIEW`** | **スロット番号**を指定。<strong>`D3D12_VERTEX_BUFFER_VIEW`（16 バイト）</strong>が**コマンドに含まれる** |
| **`D3D12_INDIRECT_ARGUMENT_TYPE_INDEX_BUFFER_VIEW`** | <strong>`D3D12_INDEX_BUFFER_VIEW`（16 バイト）</strong> |
| **`D3D12_INDIRECT_ARGUMENT_TYPE_CONSTANT_BUFFER_VIEW`** | **ルート CBV の GPU アドレス**（8 バイト） |
| **`..._SHADER_RESOURCE_VIEW` / `..._UNORDERED_ACCESS_VIEW`** | **ルート SRV/UAV の GPU アドレス**（8 バイト） |
| **`D3D12_INDIRECT_ARGUMENT_TYPE_DISPATCH` / `DISPATCH_MESH`** | **コンピュート／メッシュ シェーダーのディスパッチ** |

<strong>今回は、「巨大な共有頂点バッファ」</strong>を**1 つ**使うので**頂点バッファ ビューを、コマンドごとに変える必要がありません**。**メッシュごとに別バッファ**を使う設計では、**これらをコマンドに含めます**（**コマンドが大きくなる**）。

## 描画数の上限とデバッグ用の読み戻し

**実際に何個描かれたか**を、**CPU で確認したい**ことがあります（**統計・デバッグ**）。**カウント バッファをリードバック ヒープにコピー**します。

```cpp
void Renderer::RecordReadbackCounts(ID3D12GraphicsCommandList* list) {
  CD3DX12_RESOURCE_BARRIER to_source = CD3DX12_RESOURCE_BARRIER::Transition(
      count_buffer_.Get(), D3D12_RESOURCE_STATE_INDIRECT_ARGUMENT,
      D3D12_RESOURCE_STATE_COPY_SOURCE);
  list->ResourceBarrier(1, &to_source);

  list->CopyBufferRegion(count_readback_[frame_index_].Get(), 0, count_buffer_.Get(), 0,
                         sizeof(uint32_t) * kBucketCount);

  CD3DX12_RESOURCE_BARRIER to_indirect = CD3DX12_RESOURCE_BARRIER::Transition(
      count_buffer_.Get(), D3D12_RESOURCE_STATE_COPY_SOURCE,
      D3D12_RESOURCE_STATE_INDIRECT_ARGUMENT);
  list->ResourceBarrier(1, &to_indirect);
}
```

**読み戻した値は、GPU がそのフレームを終えてから**（**フェンス完了後**）**CPU が `Map` して読みます**。**数フレーム遅れ**ますが**統計表示には十分**です（[同期とデバッグ](sync-debug.md)）。

## よくあるミス

??? failure "IndirectCommand の並びと、コマンド シグネチャの引数の並びが違って、描画が壊れる"
    **メモリ配置 ＝ 引数配列の順序**。**`static_assert(sizeof(IndirectCommand) == ByteStride)`**。

??? failure "ルート定数を含むシグネチャを、ルート シグネチャ nullptr で作って失敗する"
    **ルート引数の変更を含む**場合は、**ルート シグネチャを指定**する。

??? failure "`DRAW_INDEXED` を、引数配列の途中に置く"
    **Draw/Dispatch 系は、最後**。

??? failure "ExecuteIndirect の後、ルート定数に依存する通常のドローで、値が不定"
    **ルート定数を再設定**する。

??? failure "引数バッファが `INDIRECT_ARGUMENT` 状態でなく、デバッグ レイヤーがエラー"
    **UAV 書き込みの後に、状態遷移**。

??? failure "カウントが最大数を超えているのに、超過分が読まれて壊れる"
    **`ExecuteIndirect` は、`min(カウント, 最大数)`** で**切り詰める**。**シェーダー側でも、`slot >= MAX` では書かない**。

??? failure "PSO の異なる物を、同じ ExecuteIndirect に混ぜる"
    **PSO ごとにバケットを分け**、**バケットごとに呼ぶ**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>コマンド シグネチャ</strong>で、<strong>1 コマンドの中身（ルート定数 ＋ Draw）の並び</strong>を<strong>GPU に教える</strong>
    - [x] <strong>`IndirectCommand`（24 バイト）</strong>の<strong>配置・`ByteStride`・引数の順序</strong>を<strong>一致</strong>させる
    - [x] <strong>ルート定数でインスタンス番号</strong>を渡し、<strong>シェーダーは配列から引く</strong>
    - [x] <strong>`ExecuteIndirect(..., 最大数, 引数, オフセット, カウント, オフセット)`</strong>。<strong>実行数 ＝ min(カウント, 最大数)</strong>
    - [x] <strong>PSO ごとにバケット</strong>を分け、<strong>バケットごとに呼ぶ</strong>。<strong>呼び出し後のルート定数は不定</strong>

## 参考

- Microsoft, "Indirect Drawing"（Direct3D 12 Programming Guide）
- Microsoft, "ID3D12GraphicsCommandList::ExecuteIndirect"
- Microsoft, "D3D12_INDIRECT_ARGUMENT_DESC"

## 関連ページ

- [GPU Driven（D3D12 詳細）](index.md)
- [カリング](culling.md)
- [ビンドレス](bindless.md)
- [Hi-Z と 2 パス](hiz-two-pass.md)
- [非同期コンピュート](../async-compute.md)
