---
title: PSO
tags:
  - DirectX
---

# PSO

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>PSO</strong>（Pipeline State Object、パイプライン ステート オブジェクト）は、<strong>描画パイプラインの、ほぼ全部の設定を、1 つに、まとめた、オブジェクト</strong>です。シェーダー、入力レイアウト、ブレンド、ラスタライザー、深度ステンシル、レンダー ターゲットの、フォーマット、トポロジーの種類。これらを、<strong>事前に、1 つの PSO として、作って</strong>おき、描画時は、`SetPipelineState` で、<strong>1 回の呼び出し</strong>で、切り替えます。

!!! tip "ポイント"
    - PSO ＝ パイプラインの設定を、まとめた、不変のオブジェクト。作るのは、重い（シェーダーの、最終コンパイルが、走る）。
    - <strong>起動時・ロード時に、作る</strong>。描画中（フレームの中）に、作らない（ヒッチ＝カクつきの原因）。
    - 描画用は `CreateGraphicsPipelineState`、計算用は `CreateComputePipelineState`。
    - PSO を、切り替える数を、減らす（マテリアルを、PSO ごとに、まとめて、描く）。
    - ブレンド、深度、ラスタライザーを、変えたいなら、<strong>別の PSO</strong>。個別には、変えられない。

## 描画用の PSO

```cpp
D3D12_GRAPHICS_PIPELINE_STATE_DESC desc = {};
desc.pRootSignature = root_signature.Get();                       // ルート シグネチャ（root-signature.md）
desc.VS = {vs_blob->GetBufferPointer(), vs_blob->GetBufferSize()};   // シェーダー（shaders-dxc.md）
desc.PS = {ps_blob->GetBufferPointer(), ps_blob->GetBufferSize()};
desc.InputLayout = {input_elements, ARRAYSIZE(input_elements)};   // 頂点の並び
desc.PrimitiveTopologyType = D3D12_PRIMITIVE_TOPOLOGY_TYPE_TRIANGLE;
desc.NumRenderTargets = 1;
desc.RTVFormats[0] = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;             // レンダー ターゲットの形式
desc.DSVFormat = DXGI_FORMAT_D32_FLOAT;                           // 深度の形式
desc.SampleDesc.Count = 1;
desc.SampleMask = UINT_MAX;

desc.RasterizerState = CD3DX12_RASTERIZER_DESC(D3D12_DEFAULT);    // 既定を、まず作って、必要な所を、書き換える
desc.RasterizerState.FrontCounterClockwise = TRUE;                // 反時計回りが表（このサイトの規約）
desc.BlendState = CD3DX12_BLEND_DESC(D3D12_DEFAULT);              // ブレンドなし
desc.DepthStencilState = CD3DX12_DEPTH_STENCIL_DESC(D3D12_DEFAULT);   // 深度テスト有り、LESS

ComPtr<ID3D12PipelineState> pso;
device->CreateGraphicsPipelineState(&desc, IID_PPV_ARGS(&pso));
```

| メンバー | 内容 |
| --- | --- |
| `pRootSignature` | ルート シグネチャ（[Root Signature](root-signature.md)） |
| `VS`・`PS`・`GS`・`HS`・`DS` | シェーダーの、バイトコード（`{ポインター, 大きさ}`） |
| `InputLayout` | 頂点の並び（`D3D12_INPUT_ELEMENT_DESC` の配列） |
| `PrimitiveTopologyType` | `TRIANGLE`、`LINE`、`POINT`、`PATCH`（粗い、種類。細かい、トポロジーは、コマンド リストで） |
| `NumRenderTargets`・`RTVFormats` | レンダー ターゲットの、数と、フォーマット（<strong>描く先と、一致</strong>が、必要） |
| `DSVFormat` | 深度のフォーマット（深度を、使わないなら `DXGI_FORMAT_UNKNOWN`） |
| `RasterizerState` | 面の向き、カリング、深度バイアス |
| `BlendState` | ブレンド |
| `DepthStencilState` | 深度テスト、ステンシル |
| `SampleDesc`・`SampleMask` | MSAA の設定 |

`CD3DX12_*_DESC(D3D12_DEFAULT)` で、既定値の、ステートを、作り、<strong>必要な、メンバーだけ</strong>書き換えるのが、手軽です。

### 入力レイアウト

```cpp
const D3D12_INPUT_ELEMENT_DESC input_elements[] = {
    {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0,  D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},
    {"COLOR",    0, DXGI_FORMAT_R32G32B32A32_FLOAT, 0, 12, D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},
};
```

頂点の並びを、教える、入力レイアウトは、PSO の中に、入れます。<strong>頂点バッファを、使わない描画</strong>（フルスクリーン三角形）は、入力レイアウトを、空（`{nullptr, 0}`）に、します。

## PSO の、ステート（まとめて、1 つ）

D3D12 では、ブレンド・ラスタライザー・深度ステンシルは、<strong>独立した、ステートでは、なく</strong>、PSO の、一部です。「ブレンドだけ、変えたい」ときも、<strong>別の PSO</strong> を、作ります。

| 変えたい物 | PSO を |
| --- | --- |
| ブレンド（不透明 → 半透明） | 別の PSO（`BlendState` だけ違う） |
| カリング（`BACK` → `NONE`） | 別の PSO |
| 深度の書き込みの、有無 | 別の PSO |
| シェーダー | 別の PSO |
| ビューポート、シザー、トポロジーの形（リスト、ストリップ）、ブレンド係数、ステンシル参照値 | PSO と別。コマンド リストで、設定 |

変種が、多い（半透明の、有無 × 両面 × …）と、PSO の数が、増えます。<strong>どの組み合わせを、使うかを、洗い出して</strong>、起動時に、まとめて、作ります。

## 計算用の PSO

```cpp
D3D12_COMPUTE_PIPELINE_STATE_DESC desc = {};
desc.pRootSignature = compute_root_signature.Get();
desc.CS = {cs_blob->GetBufferPointer(), cs_blob->GetBufferSize()};

ComPtr<ID3D12PipelineState> compute_pso;
device->CreateComputePipelineState(&desc, IID_PPV_ARGS(&compute_pso));
```

計算用は、シェーダーと、ルート シグネチャだけです（[Compute Shader](compute-shader.md)）。

## 設定する

```cpp
command_list->SetPipelineState(pso.Get());                        // PSO を、切り替える（1 回の呼び出し）
command_list->SetGraphicsRootSignature(root_signature.Get());     // PSO に、組み込んだものと、同じルート シグネチャ
```

`Reset` で、初期の PSO を、渡す方法も、あります（`command_list->Reset(allocator, pso)`）。<strong>PSO と、ルート シグネチャは、一致</strong>が、必要です。

## 作るのは、重い

PSO の、作成時に、ドライバーが、シェーダーの、<strong>最終的な、コンパイル</strong>（GPU 固有の、機械語への、変換）を、行うため、数 ms〜数百 ms かかります。描画中に、作ると、フレームが、止まります（シェーダー コンパイルの、ヒッチ）。

| 対策 | 内容 |
| --- | --- |
| 起動時・ロード時に、全部作る | ロード画面で、必要な、PSO を、すべて、作る |
| 別スレッドで、作る | 作成は、スレッド セーフ。ロード用の、スレッドで、並列に、作る |
| PSO キャッシュ | 作った PSO を、ディスクに、保存し、次回の、起動を、速くする |

### PSO キャッシュ（ライブラリ）

```cpp
// PSO を、ディスクに、保存して、次回の起動で、再利用する（ID3D12PipelineLibrary）。
ComPtr<ID3D12PipelineLibrary> library;
device1->CreatePipelineLibrary(cached_blob.data(), cached_blob.size(), IID_PPV_ARGS(&library));

// キャッシュに、あれば、読み込む。無ければ、作って、登録する。
HRESULT hr = library->LoadGraphicsPipeline(L"OpaquePSO", &desc, IID_PPV_ARGS(&pso));
if (FAILED(hr)) {
  device->CreateGraphicsPipelineState(&desc, IID_PPV_ARGS(&pso));
  library->StorePipeline(L"OpaquePSO", pso.Get());
}
// 終了時: library->Serialize(buffer, size) で、ファイルに保存する。
```

ドライバーや GPU が、変わると、キャッシュは、無効になるので、読み込みの失敗を、考慮して、作り直す、経路を、持ちます。

## PSO の、数を、減らす

| 工夫 | 内容 |
| --- | --- |
| 描画を、PSO ごとに、並べ替える | PSO の、切り替えを、減らす（切り替えは、重い） |
| 不要な、組み合わせを、作らない | 使わない、変種は、作らない |
| ステートを、揃える | 似た、設定を、共通にして、PSO の数を、抑える |
| ルート シグネチャを、共通にする | 同じ、ルート シグネチャの、PSO は、切り替えが、軽い |

## よくあるミス

??? failure "`CreateGraphicsPipelineState` が、失敗する"
    シェーダーの、入力と、入力レイアウトが、合わない。`RTVFormats` の数と、`NumRenderTargets` が、合わない。ルート シグネチャが、シェーダーと、合わない。デバッグ レイヤーの、メッセージで、確認する。

??? failure "描画しても、何も、出ない（PSO の、フォーマットが、違う）"
    PSO の `RTVFormats` が、実際に、描く、レンダー ターゲットの、フォーマットと、違う（`_SRGB` の、有無など）。`DSVFormat` も、同様。

??? failure "初回のとき、フレームが、止まる（ヒッチ）"
    描画中に、PSO を、作っている。起動時・ロード時に、作る。

??? failure "三角形が、見えない（裏面）"
    `RasterizerState.FrontCounterClockwise` が、既定（`FALSE`）のまま。このサイトの、規約は、`TRUE`。

## これだけ覚える

!!! abstract "まとめ"
    - [x] PSO ＝ パイプラインの設定を、まとめた、不変のオブジェクト
    - [x] 作成は、重い。起動時・ロード時に、全部作る。描画中に、作らない
    - [x] 描画は `CreateGraphicsPipelineState`、計算は `CreateComputePipelineState`
    - [x] ブレンド・カリング・深度の変更は、別の PSO
    - [x] PSO と、コマンド リストの、ルート シグネチャは、一致させる
    - [x] 作成を、別スレッドで、PSO キャッシュで、起動を、速くする

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Root Signature](root-signature.md)
- [Shaders and DXC](shaders-dxc.md)
- [Drawing a Triangle](triangle.md)
- [Microsoft Learn: パイプライン ステート](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/managing-graphics-pipeline-state-in-direct3d-12)
