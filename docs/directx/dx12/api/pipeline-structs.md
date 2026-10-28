---
title: Pipeline State Structs
tags:
  - DirectX
api:
  - D3D12_GRAPHICS_PIPELINE_STATE_DESC
---

# Pipeline State Structs

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

D3D12 では、描画の設定（シェーダー、ブレンド、深度テスト、ラスタライザー、頂点の並び、出力先の形式）をばらばらに切り替えません。すべてを 1 つの構造体にまとめて PSO（パイプライン ステート オブジェクト）として作っておき、描画の直前に丸ごと差し替えます。切り替えの検証を作成時に済ませておくので、描画中の負荷が少なくなります。このページでは、その PSO を作るための構造体を説明します。

!!! tip "ポイント"
    - グラフィックスの PSO は `D3D12_GRAPHICS_PIPELINE_STATE_DESC` 1 つに全部入りで、`= {}` で初期化してから埋める。
    - `SampleMask` は `UINT_MAX` にする。0 のままだと何も描かれない。
    - `NumRenderTargets` と `RTVFormats`、`DSVFormat` は、実際の出力先と一致させる。
    - `FrontCounterClockwise` は左手系・CW が表のこのサイトでは既定の `FALSE` のままにする。
    - ラスタライザー、ブレンド、深度の既定の設定は [`MakeDefaultRasterizerDesc`](../util.md#makedefaultrasterizerdesc) などで作る。

!!! info "このページを読む前に"
    PSO の全体像は [PSO](../pso.md)、シェーダーのコンパイルは [Shaders and DXC](../shaders-dxc.md)、ルート シグネチャは [Root Signature](../root-signature.md) と [Root Signature Structs](root-signature-structs.md) で説明しています。

## 構造体一覧

| 構造体 | 役割 | 使う場所 |
| --- | --- | --- |
| [`D3D12_GRAPHICS_PIPELINE_STATE_DESC`](#d3d12_graphics_pipeline_state_desc) | 描画の PSO の全設定 | `CreateGraphicsPipelineState` |
| [`D3D12_COMPUTE_PIPELINE_STATE_DESC`](#d3d12_compute_pipeline_state_desc) | 計算の PSO の全設定 | `CreateComputePipelineState` |
| [`D3D12_SHADER_BYTECODE`](#d3d12_shader_bytecode) | コンパイル済みシェーダー | PSO の `VS`、`PS`、`CS` など |
| [`D3D12_INPUT_ELEMENT_DESC`](#d3d12_input_element_desc) | 頂点 1 要素の読み方 | 入力レイアウト |
| [`D3D12_RASTERIZER_DESC`](#d3d12_rasterizer_desc) | 三角形からピクセルへの変換 | PSO の `RasterizerState` |
| [`D3D12_BLEND_DESC`](#d3d12_blend_desc) | 色の合成 | PSO の `BlendState` |
| [`D3D12_DEPTH_STENCIL_DESC`](#d3d12_depth_stencil_desc) | 深度とステンシルのテスト | PSO の `DepthStencilState` |
| [`D3D12_DEPTH_STENCILOP_DESC`](#d3d12_depth_stencilop_desc) | ステンシルの表と裏の動作 | `D3D12_DEPTH_STENCIL_DESC` の中身 |

## PSO の全体

### D3D12_GRAPHICS_PIPELINE_STATE_DESC {#d3d12_graphics_pipeline_state_desc}

```cpp
typedef struct D3D12_GRAPHICS_PIPELINE_STATE_DESC {
    ID3D12RootSignature* pRootSignature;
    D3D12_SHADER_BYTECODE VS;
    D3D12_SHADER_BYTECODE PS;
    D3D12_SHADER_BYTECODE DS;
    D3D12_SHADER_BYTECODE HS;
    D3D12_SHADER_BYTECODE GS;
    D3D12_STREAM_OUTPUT_DESC StreamOutput;
    D3D12_BLEND_DESC BlendState;
    UINT SampleMask;
    D3D12_RASTERIZER_DESC RasterizerState;
    D3D12_DEPTH_STENCIL_DESC DepthStencilState;
    D3D12_INPUT_LAYOUT_DESC InputLayout;
    D3D12_INDEX_BUFFER_STRIP_CUT_VALUE IBStripCutValue;
    D3D12_PRIMITIVE_TOPOLOGY_TYPE PrimitiveTopologyType;
    UINT NumRenderTargets;
    DXGI_FORMAT RTVFormats[8];
    DXGI_FORMAT DSVFormat;
    DXGI_SAMPLE_DESC SampleDesc;
    UINT NodeMask;
    D3D12_CACHED_PIPELINE_STATE CachedPSO;
    D3D12_PIPELINE_STATE_FLAGS Flags;
} D3D12_GRAPHICS_PIPELINE_STATE_DESC;
```

描画に必要な設定を全部まとめた構造体です。メンバーが多いのですが、普通の描画で埋めるのは半分ほどで、残りは 0 のままにします。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `pRootSignature` | `ID3D12RootSignature*` | シェーダーが使うリソースの宣言 |
| `VS`、`PS` | `D3D12_SHADER_BYTECODE` | 頂点シェーダー、ピクセル シェーダー |
| `DS`、`HS`、`GS` | `D3D12_SHADER_BYTECODE` | テッセレーション、ジオメトリ シェーダー。使わなければ空 |
| `StreamOutput` | `D3D12_STREAM_OUTPUT_DESC` | ストリーム出力。使わなければ 0 |
| `BlendState` | `D3D12_BLEND_DESC` | 色の合成 |
| `SampleMask` | `UINT` | MSAA のサンプルのマスク。`UINT_MAX` |
| `RasterizerState` | `D3D12_RASTERIZER_DESC` | 面の向きやカリング |
| `DepthStencilState` | `D3D12_DEPTH_STENCIL_DESC` | 深度とステンシル |
| `InputLayout` | `D3D12_INPUT_LAYOUT_DESC` | 頂点の並び（`pInputElementDescs` と `NumElements`） |
| `IBStripCutValue` | `D3D12_INDEX_BUFFER_STRIP_CUT_VALUE` | ストリップを切るインデックス。通常は `DISABLED` |
| `PrimitiveTopologyType` | `D3D12_PRIMITIVE_TOPOLOGY_TYPE` | 点、線、三角形のどれか |
| `NumRenderTargets` | `UINT` | 同時に描くレンダー ターゲットの数（最大 8） |
| `RTVFormats` | `DXGI_FORMAT[8]` | 各レンダー ターゲットの形式 |
| `DSVFormat` | `DXGI_FORMAT` | 深度バッファの形式。使わなければ `UNKNOWN` |
| `SampleDesc` | `DXGI_SAMPLE_DESC` | MSAA の設定。通常は `{1, 0}` |
| `NodeMask` | `UINT` | GPU が 1 つなら 0 |
| `CachedPSO` | `D3D12_CACHED_PIPELINE_STATE` | 保存しておいたコンパイル済みの PSO |
| `Flags` | `D3D12_PIPELINE_STATE_FLAGS` | 通常は `NONE` |

`pRootSignature` は、シェーダーに渡すリソースの置き場を宣言したルート シグネチャで、PSO を作るときに必ず要ります。シェーダー内の宣言（`[RootSignature(...)]`）と一致していないと、PSO の作成は失敗します。

シェーダーは `D3D12_SHADER_BYTECODE` で渡します。頂点シェーダーとピクセル シェーダーの 2 つがあれば、普通の描画ができます。使わないステージは、`pShaderBytecode = nullptr`、`BytecodeLength = 0` のまま（ゼロ初期化のまま）にします。

`SampleMask` は、MSAA で更新するサンプルを選ぶ 32 ビットのマスクです。`0xFFFFFFFF`（`UINT_MAX`）にします。ゼロ初期化のまま 0 にしてしまうと、どのサンプルも更新されず、何も描かれません。MSAA を使わない場合でも同じです。

`PrimitiveTopologyType` は、点、線、三角形、パッチの大分類です。三角形のリストもストリップも `TRIANGLE` で、リストかストリップかは、描画時に `IASetPrimitiveTopology` で決めます。ゼロ初期化のまま `UNDEFINED` にすると、作成に失敗します。

レンダー ターゲットは、`NumRenderTargets` に数、`RTVFormats[0]` からその形式を書きます。使わない配列の要素は `DXGI_FORMAT_UNKNOWN` のままにします。ここに書いた形式は、実際に `OMSetRenderTargets` で使うレンダー ターゲットの形式と一致していなければなりません。ずれると、描画時にデバッグ レイヤーがエラーを出します。バック バッファが `R8G8B8A8_UNORM` なら、PSO も同じにします。RTV を `_SRGB` で作った場合は、PSO も `_SRGB` です。深度バッファを使わないときは `DSVFormat` を `UNKNOWN` にし、使うなら `D32_FLOAT` などをビューの形式と一致させます。

`SampleDesc` は、MSAA を使わなければ `Count = 1`、`Quality = 0` です。`Count = 0` にしたままだと作成が失敗します。

`CachedPSO` に前回保存した PSO のデータを渡すと、起動時のコンパイル時間を短縮できます。使わなければ 0 です。

```cpp
D3D12_GRAPHICS_PIPELINE_STATE_DESC pso = {};
pso.pRootSignature = root_signature.Get();
pso.VS = {vs_blob->GetBufferPointer(), vs_blob->GetBufferSize()};
pso.PS = {ps_blob->GetBufferPointer(), ps_blob->GetBufferSize()};
pso.BlendState = MakeDefaultBlendDesc();
pso.SampleMask = UINT_MAX;                       // 0 のままだと何も描かれない
pso.RasterizerState = MakeDefaultRasterizerDesc();
pso.DepthStencilState = MakeDefaultDepthStencilDesc();
pso.InputLayout = {input_layout.data(), static_cast<UINT>(input_layout.size())};
pso.PrimitiveTopologyType = D3D12_PRIMITIVE_TOPOLOGY_TYPE_TRIANGLE;
pso.NumRenderTargets = 1;
pso.RTVFormats[0] = DXGI_FORMAT_R8G8B8A8_UNORM;
pso.DSVFormat = DXGI_FORMAT_D32_FLOAT;
pso.SampleDesc.Count = 1;
HRESULT hr = device->CreateGraphicsPipelineState(&pso, IID_PPV_ARGS(&pipeline_state));
```

!!! failure "よくあるミス"
    - `SampleMask` が 0 のままで、何も描かれない。
    - `PrimitiveTopologyType` を設定せず、作成に失敗する。
    - `RTVFormats` や `DSVFormat` が、実際のターゲットと違う。
    - 入力レイアウトとシェーダーの入力が合わない。

### D3D12_COMPUTE_PIPELINE_STATE_DESC {#d3d12_compute_pipeline_state_desc}

```cpp
typedef struct D3D12_COMPUTE_PIPELINE_STATE_DESC {
    ID3D12RootSignature* pRootSignature;
    D3D12_SHADER_BYTECODE CS;
    UINT NodeMask;
    D3D12_CACHED_PIPELINE_STATE CachedPSO;
    D3D12_PIPELINE_STATE_FLAGS Flags;
} D3D12_COMPUTE_PIPELINE_STATE_DESC;
```

コンピュート シェーダー用の PSO です。描画の設定が要らないので、メンバーはずっと少なくなります。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `pRootSignature` | `ID3D12RootSignature*` | ルート シグネチャ |
| `CS` | `D3D12_SHADER_BYTECODE` | コンピュート シェーダー |
| `NodeMask` | `UINT` | GPU が 1 つなら 0 |
| `CachedPSO` | `D3D12_CACHED_PIPELINE_STATE` | 保存した PSO。使わなければ 0 |
| `Flags` | `D3D12_PIPELINE_STATE_FLAGS` | 通常は `NONE` |

`pRootSignature` と `CS` の 2 つを埋めれば足ります。

```cpp
D3D12_COMPUTE_PIPELINE_STATE_DESC desc = {};
desc.pRootSignature = compute_root_signature.Get();
desc.CS = {cs_blob->GetBufferPointer(), cs_blob->GetBufferSize()};
HRESULT hr = device->CreateComputePipelineState(&desc, IID_PPV_ARGS(&compute_pso));
```

### D3D12_SHADER_BYTECODE {#d3d12_shader_bytecode}

```cpp
typedef struct D3D12_SHADER_BYTECODE {
    const void* pShaderBytecode;
    SIZE_T BytecodeLength;
} D3D12_SHADER_BYTECODE;
```

コンパイル済みのシェーダーの、先頭のポインタと長さの組です。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `pShaderBytecode` | `const void*` | バイト コードの先頭 |
| `BytecodeLength` | `SIZE_T` | バイト数 |

`ID3DBlob`（コンパイル結果）の `GetBufferPointer()` と `GetBufferSize()` をそのまま入れます。この構造体は中身をコピーしません。ポインタを持つだけなので、PSO を作り終わるまで、元の blob を解放してはいけません（作成が終われば、もう要りません）。長さが 0 のままだと「そのステージを使わない」という意味になるので、渡し忘れたシェーダーは黙って無視され、絵が出ない原因になります。

## 頂点の入力

### D3D12_INPUT_ELEMENT_DESC {#d3d12_input_element_desc}

```cpp
typedef struct D3D12_INPUT_ELEMENT_DESC {
    LPCSTR SemanticName;
    UINT SemanticIndex;
    DXGI_FORMAT Format;
    UINT InputSlot;
    UINT AlignedByteOffset;
    D3D12_INPUT_CLASSIFICATION InputSlotClass;
    UINT InstanceDataStepRate;
} D3D12_INPUT_ELEMENT_DESC;
```

頂点データの 1 つの要素（位置、法線、UV など）をシェーダーの入力とどう結びつけるかを書きます。これの配列が入力レイアウトになります。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `SemanticName` | `LPCSTR` | シェーダーの入力のセマンティクス名（`"POSITION"` など） |
| `SemanticIndex` | `UINT` | 同じ名前が複数あるときの番号 |
| `Format` | `DXGI_FORMAT` | 要素の形式 |
| `InputSlot` | `UINT` | どの頂点バッファから読むか（0〜15） |
| `AlignedByteOffset` | `UINT` | 頂点の先頭からのバイト数 |
| `InputSlotClass` | `D3D12_INPUT_CLASSIFICATION` | 頂点ごとか、インスタンスごとか |
| `InstanceDataStepRate` | `UINT` | インスタンスごとのとき、何インスタンスで進めるか |

`SemanticName` と `SemanticIndex` は、HLSL の頂点シェーダーの入力に付けたセマンティクス（`float3 pos : POSITION;`）と一致させます。`TEXCOORD1` なら名前が `"TEXCOORD"`、番号が 1 です。名前が合わないと、PSO の作成が失敗します。

`Format` は、C++ 側のメンバーの型に合わせます。`XMFLOAT3` なら `R32G32B32_FLOAT`、`XMFLOAT2` なら `R32G32_FLOAT`、`XMFLOAT4` の色なら `R32G32B32A32_FLOAT` です。8 ビットの色を `uint32_t` で持つなら `R8G8B8A8_UNORM` で、シェーダーには 0〜1 の `float4` として渡されます。

`AlignedByteOffset` は、頂点構造体の中の位置（`offsetof`）です。`D3D12_APPEND_ALIGNED_ELEMENT`（`0xffffffff`）を入れると、直前の要素の次に自動で詰めてくれるので、オフセットを数えるミスを防げます。

`InputSlot` は、頂点バッファを複数使うときだけ変えます。位置を 1 本、UV を別の 1 本、のように分けた構成です。

`InputSlotClass` が `PER_VERTEX_DATA` なら頂点ごと、`PER_INSTANCE_DATA` なら、インスタンスごとにデータが進みます。インスタンス描画では、位置のようなメッシュ共通のデータは頂点ごと、インスタンスごとの行列などはインスタンスごとにします。`PER_VERTEX_DATA` のとき、`InstanceDataStepRate` は 0、`PER_INSTANCE_DATA` のときは 1 にします。

```cpp
struct Vertex {
  float position[3];
  float uv[2];
};

std::vector<D3D12_INPUT_ELEMENT_DESC> layout = {
    {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, D3D12_APPEND_ALIGNED_ELEMENT,
     D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},
    {"TEXCOORD", 0, DXGI_FORMAT_R32G32_FLOAT, 0, D3D12_APPEND_ALIGNED_ELEMENT,
     D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},
};
```

`SemanticName` は文字列へのポインタなので、PSO を作り終わるまで有効な文字列を指していなければなりません。リテラルを使えば問題ありません。

## ラスタライザー、ブレンド、深度

### D3D12_RASTERIZER_DESC {#d3d12_rasterizer_desc}

```cpp
typedef struct D3D12_RASTERIZER_DESC {
    D3D12_FILL_MODE FillMode;
    D3D12_CULL_MODE CullMode;
    BOOL FrontCounterClockwise;
    INT DepthBias;
    FLOAT DepthBiasClamp;
    FLOAT SlopeScaledDepthBias;
    BOOL DepthClipEnable;
    BOOL MultisampleEnable;
    BOOL AntialiasedLineEnable;
    UINT ForcedSampleCount;
    D3D12_CONSERVATIVE_RASTERIZATION_MODE ConservativeRaster;
} D3D12_RASTERIZER_DESC;
```

三角形をピクセルに変えるときの規則を決めます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `FillMode` | `D3D12_FILL_MODE` | `SOLID`（塗る）か `WIREFRAME` |
| `CullMode` | `D3D12_CULL_MODE` | `NONE`、`FRONT`、`BACK` |
| `FrontCounterClockwise` | `BOOL` | `TRUE` なら反時計回りが表。`FALSE`（既定）なら時計回りが表 |
| `DepthBias` | `INT` | 深度に足す固定の値 |
| `DepthBiasClamp` | `FLOAT` | バイアスの上限 |
| `SlopeScaledDepthBias` | `FLOAT` | 傾きに比例するバイアス |
| `DepthClipEnable` | `BOOL` | 深度の範囲外を切る。通常は `TRUE` |
| `MultisampleEnable` | `BOOL` | MSAA の画質の設定 |
| `AntialiasedLineEnable` | `BOOL` | 線のアンチエイリアス |
| `ForcedSampleCount` | `UINT` | 通常は 0 |
| `ConservativeRaster` | `D3D12_CONSERVATIVE_RASTERIZATION_MODE` | 通常は `OFF` |

`FrontCounterClockwise` は、ミスが多いメンバーです。D3D12 の既定は `FALSE`（時計回りが表）で、このサイトの座標系（左手系、時計回りが表）と同じです。`TRUE` にするのは、反時計回りが表のメッシュ（読み込み時に頂点の順序を入れ替えていない glTF など）を描くときだけです。メッシュの並びとこの設定が食い違ったまま `CullMode = BACK` にすると、表のはずの面が消えて、裏側だけが見えます。

`CullMode` は、描かない面です。`BACK` は裏面を捨てます。閉じたメッシュでは、これで描画量が半分近くになります。薄い板や、両面が見えるものは `NONE` にします。

`DepthBias` 系の 3 つは、影のマップなどで、自分の影が出る「シャドウ アクネ」を抑えるときに使います。通常の描画では 0 です。

`DepthClipEnable` は、近平面や遠平面の外の三角形を切るかどうかです。`FALSE` にするのは、影のマップで太陽の外側の物も描きたいときなど、特殊な場面だけです。

`ForcedSampleCount` と `ConservativeRaster` は特殊な機能で、通常は 0 と `OFF` です。

0 でゼロ初期化すると `FillMode` が 0（無効）になり、作成が失敗します。そのため、既定の組を返す [`MakeDefaultRasterizerDesc`](../util.md#makedefaultrasterizerdesc) から始めて、変えたいメンバーだけ書き換えます。

```cpp
D3D12_RASTERIZER_DESC rasterizer = MakeDefaultRasterizerDesc();
rasterizer.FrontCounterClockwise = FALSE;      // CW が表（既定）
rasterizer.CullMode = D3D12_CULL_MODE_BACK;
```

### D3D12_BLEND_DESC {#d3d12_blend_desc}

```cpp
typedef struct D3D12_BLEND_DESC {
    BOOL AlphaToCoverageEnable;
    BOOL IndependentBlendEnable;
    D3D12_RENDER_TARGET_BLEND_DESC RenderTarget[8];
} D3D12_BLEND_DESC;

typedef struct D3D12_RENDER_TARGET_BLEND_DESC {
    BOOL BlendEnable;
    BOOL LogicOpEnable;
    D3D12_BLEND SrcBlend;
    D3D12_BLEND DestBlend;
    D3D12_BLEND_OP BlendOp;
    D3D12_BLEND SrcBlendAlpha;
    D3D12_BLEND DestBlendAlpha;
    D3D12_BLEND_OP BlendOpAlpha;
    D3D12_LOGIC_OP LogicOp;
    UINT8 RenderTargetWriteMask;
} D3D12_RENDER_TARGET_BLEND_DESC;
```

これから描くピクセルの色をすでにあるピクセルの色とどう混ぜるかを決めます。半透明の表現にはここが要ります。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `AlphaToCoverageEnable` | `BOOL` | アルファを MSAA のカバレッジに変える（草の葉など） |
| `IndependentBlendEnable` | `BOOL` | `TRUE` なら、レンダー ターゲットごとに別の設定 |
| `RenderTarget[i].BlendEnable` | `BOOL` | ブレンドをするか |
| `RenderTarget[i].LogicOpEnable` | `BOOL` | 論理演算を使うか。`BlendEnable` と同時には使えない |
| `RenderTarget[i].SrcBlend` | `D3D12_BLEND` | 新しい色にかける係数 |
| `RenderTarget[i].DestBlend` | `D3D12_BLEND` | 既存の色にかける係数 |
| `RenderTarget[i].BlendOp` | `D3D12_BLEND_OP` | 2 つの結果を合わせる演算（`ADD` など） |
| `RenderTarget[i].SrcBlendAlpha`、`DestBlendAlpha`、`BlendOpAlpha` | 同上 | アルファ成分の設定 |
| `RenderTarget[i].LogicOp` | `D3D12_LOGIC_OP` | 論理演算。使わなければ `NOOP` |
| `RenderTarget[i].RenderTargetWriteMask` | `UINT8` | 書き込む成分。全部なら `D3D12_COLOR_WRITE_ENABLE_ALL` |

普通の半透明は、`SrcBlend = SRC_ALPHA`、`DestBlend = INV_SRC_ALPHA`、`BlendOp = ADD` です。式にすると、`新しい色 × α + 既存の色 × (1 − α)` になります。加算合成（光や火花）は、`SrcBlend = SRC_ALPHA`、`DestBlend = ONE` です。

`IndependentBlendEnable` が `FALSE` の間は、`RenderTarget[0]` の設定だけが、すべてのレンダー ターゲットに使われます。G-Buffer のように、ターゲットごとに異なる設定をしたいときだけ `TRUE` にして、`RenderTarget[1]` 以降も埋めます。

`RenderTargetWriteMask` は 0 にすると、何も書き込みません。ゼロ初期化のあとに、`D3D12_COLOR_WRITE_ENABLE_ALL` を入れるのを忘れると、何も描かれません。そのため、既定の設定を返す [`MakeDefaultBlendDesc`](../util.md#makedefaultblenddesc) から始めます。`BlendEnable = FALSE` のとき、`SrcBlend` などは無視されますが、値自体は有効な列挙値（`ONE`、`ZERO`、`ADD`）にしておきます。

```cpp
D3D12_BLEND_DESC blend = MakeDefaultBlendDesc();
blend.RenderTarget[0].BlendEnable = TRUE;
blend.RenderTarget[0].SrcBlend = D3D12_BLEND_SRC_ALPHA;
blend.RenderTarget[0].DestBlend = D3D12_BLEND_INV_SRC_ALPHA;
blend.RenderTarget[0].BlendOp = D3D12_BLEND_OP_ADD;
```

### D3D12_DEPTH_STENCIL_DESC {#d3d12_depth_stencil_desc}

```cpp
typedef struct D3D12_DEPTH_STENCIL_DESC {
    BOOL DepthEnable;
    D3D12_DEPTH_WRITE_MASK DepthWriteMask;
    D3D12_COMPARISON_FUNC DepthFunc;
    BOOL StencilEnable;
    UINT8 StencilReadMask;
    UINT8 StencilWriteMask;
    D3D12_DEPTH_STENCILOP_DESC FrontFace;
    D3D12_DEPTH_STENCILOP_DESC BackFace;
} D3D12_DEPTH_STENCIL_DESC;
```

手前にあるものが奥を隠すための、深度テストを決めます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `DepthEnable` | `BOOL` | 深度テストをするか |
| `DepthWriteMask` | `D3D12_DEPTH_WRITE_MASK` | `ALL` なら深度を書く、`ZERO` なら書かない |
| `DepthFunc` | `D3D12_COMPARISON_FUNC` | 通る条件。通常は `LESS` |
| `StencilEnable` | `BOOL` | ステンシル テストをするか |
| `StencilReadMask` | `UINT8` | ステンシルを読むマスク。通常は `0xFF` |
| `StencilWriteMask` | `UINT8` | ステンシルを書くマスク。通常は `0xFF` |
| `FrontFace`、`BackFace` | `D3D12_DEPTH_STENCILOP_DESC` | 表と裏の動作 |

不透明な物は `DepthEnable = TRUE`、`DepthWriteMask = ALL`、`DepthFunc = LESS` です。半透明の物は、不透明な物の奥には隠れるが、自分は深度を書かない、という設定にするので、`DepthEnable = TRUE` と `DepthWriteMask = ZERO` の組み合わせです。空（スカイボックス）などを最後に描くときは、`DepthFunc = LESS_EQUAL` にして、深度が最も奥（1.0）のピクセルだけが通るようにします。

`DepthEnable = FALSE` にすると、`DepthWriteMask` も効かず、深度バッファに何も書かれません。2D の UI やポスト プロセスは、深度を使わないので `FALSE` です。

ステンシルを使わないなら `StencilEnable = FALSE` のままにし、残りの 4 メンバーは既定の組に任せます。ゼロ初期化のままだと、`DepthFunc` が 0（無効）になって作成が失敗するので、[`MakeDefaultDepthStencilDesc`](../util.md#makedefaultdepthstencildesc) から始めます。

### D3D12_DEPTH_STENCILOP_DESC {#d3d12_depth_stencilop_desc}

```cpp
typedef struct D3D12_DEPTH_STENCILOP_DESC {
    D3D12_STENCIL_OP StencilFailOp;
    D3D12_STENCIL_OP StencilDepthFailOp;
    D3D12_STENCIL_OP StencilPassOp;
    D3D12_COMPARISON_FUNC StencilFunc;
} D3D12_DEPTH_STENCILOP_DESC;
```

ステンシル テストの結果に応じて、ステンシル値をどう更新するかを面の表と裏のそれぞれについて決めます。

| メンバー | 型 | 意味 |
| --- | --- | --- |
| `StencilFailOp` | `D3D12_STENCIL_OP` | ステンシル テストに失敗したときの動作 |
| `StencilDepthFailOp` | `D3D12_STENCIL_OP` | ステンシルは通ったが深度で落ちたときの動作 |
| `StencilPassOp` | `D3D12_STENCIL_OP` | 両方通ったときの動作 |
| `StencilFunc` | `D3D12_COMPARISON_FUNC` | ステンシル値と参照値の比較 |

動作は `KEEP`（そのまま）、`REPLACE`（参照値に置き換える）、`INCR`、`DECR` などです。ステンシルを使わない場合は、3 つを `KEEP`、`StencilFunc` を `ALWAYS` にします（これが既定の値です）。

たとえば「輪郭を描く」「鏡の中だけ描く」などの用途では、先に `StencilPassOp = REPLACE` で目印の 1 を書き、次に `StencilFunc = EQUAL`、`KEEP` で、目印のあるところだけを描きます。参照値は `OMSetStencilRef` で渡します。

## 関連ページ

- [ID3D12Device](id3d12device.md) — `CreateGraphicsPipelineState`、`CreateComputePipelineState`
- [PSO](../pso.md) — PSO の考え方
- [Root Signature Structs](root-signature-structs.md) — `pRootSignature` の中身
- [Helper Functions](../util.md) — `MakeDefaultRasterizerDesc` など
- [Depth Buffer (D3D12)](../depth-buffer.md) — 深度バッファの作り方
