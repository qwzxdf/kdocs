---
title: PSO
tags:
  - DirectX
---

# PSO

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>PSO</strong>（Pipeline State Object、パイプライン ステート オブジェクト）は、<strong>描画パイプラインのほぼ全部の設定を 1 つにまとめたオブジェクト</strong>です。シェーダー、入力レイアウト、ブレンド、ラスタライザー、深度ステンシル、レンダー ターゲットのフォーマット、トポロジーの種類。これらを <strong>事前に 1 つの PSO として、作って</strong>おき描画時は `SetPipelineState` で <strong>1 回の呼び出し</strong>で、切り替えます。

!!! tip "ポイント"
    - PSO ＝ パイプラインの設定をまとめた不変のオブジェクト。作るのは重い（シェーダーの最終コンパイルが、走る）。
    - <strong>起動時・ロード時に作る</strong>。描画中（フレームの中）に作らない（ヒッチ＝カクつきの原因）。
    - 描画用は `CreateGraphicsPipelineState`、計算用は `CreateComputePipelineState`。
    - PSO を切り替える数を減らす（マテリアルを PSO ごとに、まとめて描く）。
    - ブレンド、深度、ラスタライザーを変えたいなら <strong>別の PSO</strong>。個別には変えられない。

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
| `VS`・`PS`・`GS`・`HS`・`DS` | シェーダーのバイトコード（`{ポインター, 大きさ}`） |
| `InputLayout` | 頂点の並び（`D3D12_INPUT_ELEMENT_DESC` の配列） |
| `PrimitiveTopologyType` | `TRIANGLE`、`LINE`、`POINT`、`PATCH`（粗い種類。細かいトポロジーはコマンド リストで） |
| `NumRenderTargets`・`RTVFormats` | レンダー ターゲットの数とフォーマット（<strong>描く先と一致</strong>が、必要） |
| `DSVFormat` | 深度のフォーマット（深度を使わないなら `DXGI_FORMAT_UNKNOWN`） |
| `RasterizerState` | 面の向きカリング、深度バイアス |
| `BlendState` | ブレンド |
| `DepthStencilState` | 深度テスト、ステンシル |
| `SampleDesc`・`SampleMask` | MSAA の設定 |

`CD3DX12_*_DESC(D3D12_DEFAULT)` で既定値のステートを作り <strong>必要なメンバーだけ</strong>書き換えるのが、手軽です。

### 入力レイアウト

```cpp
const D3D12_INPUT_ELEMENT_DESC input_elements[] = {
    {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0,  D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},
    {"COLOR",    0, DXGI_FORMAT_R32G32B32A32_FLOAT, 0, 12, D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},
};
```

頂点の並びを教える入力レイアウトは PSO の中に入れます。<strong>頂点バッファを使わない描画</strong>（フルスクリーン三角形）は、入力レイアウトを空（`{nullptr, 0}`）にします。

## PSO のステート（まとめて、1 つ）

D3D12 ではブレンド・ラスタライザー・深度ステンシルは、<strong>独立したステートではなく</strong>、PSO の一部です。「ブレンドだけ変えたい」ときも <strong>別の PSO</strong> を作ります。

| 変えたい物 | PSO を |
| --- | --- |
| ブレンド（不透明 → 半透明） | 別の PSO（`BlendState` だけ違う） |
| カリング（`BACK` → `NONE`） | 別の PSO |
| 深度の書き込みの有無 | 別の PSO |
| シェーダー | 別の PSO |
| ビューポート、シザー、トポロジーの形（リスト、ストリップ）、ブレンド係数、ステンシル参照値 | PSO と別。コマンド リストで設定 |

変種が多い（半透明の有無 × 両面 × …）と PSO の数が増えます。<strong>どの組み合わせを使うかを洗い出して</strong>、起動時にまとめて作ります。

## 計算用の PSO

```cpp
D3D12_COMPUTE_PIPELINE_STATE_DESC desc = {};
desc.pRootSignature = compute_root_signature.Get();
desc.CS = {cs_blob->GetBufferPointer(), cs_blob->GetBufferSize()};

ComPtr<ID3D12PipelineState> compute_pso;
device->CreateComputePipelineState(&desc, IID_PPV_ARGS(&compute_pso));
```

計算用はシェーダーとルート シグネチャだけです（[Compute Shader](compute-shader.md)）。

## 設定する

```cpp
command_list->SetPipelineState(pso.Get());                        // PSO を、切り替える（1 回の呼び出し）
command_list->SetGraphicsRootSignature(root_signature.Get());     // PSO に、組み込んだものと、同じルート シグネチャ
```

`Reset` で初期の PSO を渡す方法もあります（`command_list->Reset(allocator, pso)`）。<strong>PSO とルート シグネチャは一致</strong>が必要です。

## 作るのは重い

PSO の作成時にドライバーが、シェーダーの <strong>最終的なコンパイル</strong>（GPU 固有の機械語への変換）を行うため数 ms〜数百 ms かかります。描画中に作るとフレームが止まります（シェーダー コンパイルのヒッチ）。

| 対策 | 内容 |
| --- | --- |
| 起動時・ロード時に全部作る | ロード画面で必要な PSO をすべて作る |
| 別スレッドで作る | 作成はスレッド セーフ。ロード用のスレッドで並列に作る |
| PSO キャッシュ | 作った PSO をディスクに保存し次回の起動を、速くする |

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

ドライバーや GPU が変わると、キャッシュは無効になるので読み込みの失敗を考慮して作り直す経路を持ちます。

## PSO の数を減らす

| 工夫 | 内容 |
| --- | --- |
| 描画を PSO ごとに並べ替える | PSO の切り替えを減らす（切り替えは、重い） |
| 不要な組み合わせを作らない | 使わない変種は、作らない |
| ステートを揃える | 似た設定を共通にして PSO の数を抑える |
| ルート シグネチャを共通にする | 同じルート シグネチャの PSO は、切り替えが軽い |

## よくあるミス

??? failure "`CreateGraphicsPipelineState` が、失敗する"
    シェーダーの入力と入力レイアウトが、合わない。`RTVFormats` の数と `NumRenderTargets` が合わない。ルート シグネチャがシェーダーと合わない。デバッグ レイヤーのメッセージで、確認する。

??? failure "描画しても何も出ない（PSO のフォーマットが、違う）"
    PSO の `RTVFormats` が実際に描く、レンダー ターゲットのフォーマットと違う（`_SRGB` の有無など）。`DSVFormat` も同様。

??? failure "初回のときフレームが止まる（ヒッチ）"
    描画中に PSO を作っている。起動時・ロード時に作る。

??? failure "三角形が、見えない（裏面）"
    `RasterizerState.FrontCounterClockwise` が既定（`FALSE`）のまま。このサイトの規約は `TRUE`。

## これだけ覚える

!!! abstract "まとめ"
    - [x] PSO ＝ パイプラインの設定をまとめた不変のオブジェクト
    - [x] 作成は重い。起動時・ロード時に全部作る。描画中に作らない
    - [x] 描画は `CreateGraphicsPipelineState`、計算は `CreateComputePipelineState`
    - [x] ブレンド・カリング・深度の変更は、別の PSO
    - [x] PSO とコマンド リストのルート シグネチャは、一致させる
    - [x] 作成を別スレッドで、PSO キャッシュで起動を速くする

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Root Signature](root-signature.md)
- [Shaders and DXC](shaders-dxc.md)
- [Drawing a Triangle](triangle.md)
- [Microsoft Learn: パイプライン ステート](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/managing-graphics-pipeline-state-in-direct3d-12)
