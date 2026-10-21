---
title: PSO
tags:
  - DirectX
---

# PSO

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

絵を 1 枚描くには決めることがたくさんあります。どのシェーダーを使うか頂点がどんな並びかブレンドはどうするか面の裏表をどう扱うか、深度テストをするか描き込み先の形式は何か。D3D11 まではこれらを 1 つずつ別々に設定していました。

D3D12 ではこれらを**1 つにまとめた不変のオブジェクト**にします。それが <strong>PSO</strong>（Pipeline State Object）です。先に 1 つ作っておき描画のときは `SetPipelineState` を 1 回呼ぶだけで、パイプライン全体を切り替えます。ドライバーが設定の組み合わせを先に知ることができるので、描画の最中に設定を検証したりシェーダーを作り直したりする必要がなくなります。

!!! tip "ポイント"
    - PSO はパイプラインの設定をまとめた変更できないオブジェクト。作るのは重い（シェーダーの最終コンパイルが走る）。
    - 起動時かロード時に作る。フレームの途中で作るとカクつく原因になる。
    - 描画用は `CreateGraphicsPipelineState`、計算用は `CreateComputePipelineState`。
    - PSO を切り替える回数を減らす。同じ PSO で描く物をまとめて描く。
    - ブレンド、深度、ラスタライザーを変えたいときは別の PSO を作る。1 つだけ変えることはできない。

!!! info "このページを読む前に"
    PSO に渡すものは、[Shaders and DXC](shaders-dxc.md)（コンパイル済みのシェーダー）と [Root Signature](root-signature.md)（引数の型）です。この 2 つを先に読んでおくと組み立ての流れが分かります。作るメソッドは [ID3D12Device::CreateGraphicsPipelineState](api/id3d12device.md#creategraphicspipelinestate) にあります。既定の設定を作る関数は [Helper Functions](util.md) です。

## 描画用の PSO を作る

```cpp
D3D12_GRAPHICS_PIPELINE_STATE_DESC desc = {};
desc.pRootSignature = root_signature.Get();  // ルート シグネチャ
desc.VS = {vs_blob->GetBufferPointer(), vs_blob->GetBufferSize()};  // シェーダー
desc.PS = {ps_blob->GetBufferPointer(), ps_blob->GetBufferSize()};
desc.InputLayout = {input_elements, ARRAYSIZE(input_elements)};  // 頂点の並び
desc.PrimitiveTopologyType = D3D12_PRIMITIVE_TOPOLOGY_TYPE_TRIANGLE;
desc.NumRenderTargets = 1;
desc.RTVFormats[0] = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;  // レンダー ターゲットの形式
desc.DSVFormat = DXGI_FORMAT_D32_FLOAT;                // 深度の形式
desc.SampleDesc.Count = 1;
desc.SampleMask = UINT_MAX;

desc.RasterizerState = MakeDefaultRasterizerDesc();  // 既定を作って、必要な所だけ書き換える
desc.RasterizerState.FrontCounterClockwise = TRUE;   // 反時計回りが表（このサイトの規約）
desc.BlendState = MakeDefaultBlendDesc();            // ブレンドなし
desc.DepthStencilState = MakeDefaultDepthStencilDesc();  // 深度テストあり、LESS

ComPtr<ID3D12PipelineState> pso;
device->CreateGraphicsPipelineState(&desc, IID_PPV_ARGS(&pso));
```

`D3D12_GRAPHICS_PIPELINE_STATE_DESC` にはたくさんのメンバーがあります。考えるべきものを順に説明します。

`pRootSignature` はこの PSO が使うルート シグネチャです。コマンド リストに設定するものと同じものでなければなりません。`VS` と `PS`（ほかに `GS`、`HS`、`DS`）はシェーダーのバイトコードで、ポインターと大きさを並べて渡します。使わない段は空のままにします。

`InputLayout` は頂点バッファの並び（位置、色など）を伝える `D3D12_INPUT_ELEMENT_DESC` の配列です。頂点バッファを使わない描画（フルスクリーン三角形など）では、空（`{nullptr, 0}`）にします。

`PrimitiveTopologyType` は三角形、線、点、パッチのどれを描くかという大きな分類です。リストかストリップかのような細かいつなぎ方は、コマンド リストの `IASetPrimitiveTopology` で決めます。

`NumRenderTargets` と `RTVFormats` は描き込み先の数と形式です。**実際に描く先のレンダー ターゲットと必ず一致させます。** 一致していないと描画しても何も出ません。`_SRGB` の付け忘れがよくある原因です。`DSVFormat` は深度バッファの形式で深度を使わないなら `DXGI_FORMAT_UNKNOWN` にします。

`RasterizerState`、`BlendState`、`DepthStencilState` は面の向きとカリング、ブレンド、深度テストの設定です。既定値を作ってから必要なメンバーだけを書き換えるのが、手軽です。このサイトでは反時計回りが表なので、`FrontCounterClockwise = TRUE` を必ず書きます。`SampleDesc` と `SampleMask` はマルチサンプルの設定で、使わないなら `Count = 1`、`SampleMask = UINT_MAX` です。

### 入力レイアウト

```cpp
const D3D12_INPUT_ELEMENT_DESC input_elements[] = {
    {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, 0, D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},
    {"COLOR", 0, DXGI_FORMAT_R32G32B32A32_FLOAT, 0, 12, D3D12_INPUT_CLASSIFICATION_PER_VERTEX_DATA, 0},
};
```

1 つの要素はセマンティクス名とその番号、形式、入力スロット、バイトのオフセット、頂点ごとかインスタンスごとかの順です。`POSITION` が先頭の 12 バイト（`float` 3 つ）、`COLOR` がそのあとの 16 バイト（`float` 4 つ）という並びをここで伝えています。

## 設定をまとめて 1 つにする意味

D3D12 ではブレンド、ラスタライザー、深度ステンシルは独立した設定ではなく、PSO の一部です。そのため、「ブレンドだけ変えたい」ときも別の PSO を作ります。たとえば、不透明から半透明への切り替えは `BlendState` だけが違う別の PSO です。カリングの切り替え深度の書き込みの有無、シェーダーの違いもすべて別の PSO になります。

一方、ビューポート、シザー矩形、トポロジーの細かい形、ブレンド係数、ステンシルの参照値は PSO とは別で、コマンド リストで設定します。

変種が多いと PSO の数が増えます。半透明の有無、両面描画、シェーダーの違いを掛け合わせると、数百になることもあります。どの組み合わせを使うかを先に洗い出して、起動時にまとめて作ります。

## 計算用の PSO

計算用の PSO はルート シグネチャとコンピュート シェーダーだけで作れます。

```cpp
D3D12_COMPUTE_PIPELINE_STATE_DESC desc = {};
desc.pRootSignature = compute_root_signature.Get();
desc.CS = {cs_blob->GetBufferPointer(), cs_blob->GetBufferSize()};

ComPtr<ID3D12PipelineState> compute_pso;
device->CreateComputePipelineState(&desc, IID_PPV_ARGS(&compute_pso));
```

使い方は [Compute Shader](compute-shader.md) にあります。

## コマンド リストで切り替える

```cpp
command_list->SetPipelineState(pso.Get());                     // PSO を切り替える（1 回の呼び出し）
command_list->SetGraphicsRootSignature(root_signature.Get());  // PSO に組み込んだものと同じルート シグネチャ
```

`Reset` で最初の PSO を渡す方法もあります（`command_list->Reset(allocator, pso)`）。PSO のルート シグネチャとコマンド リストに設定したルート シグネチャは、一致している必要があります。

## 作るのは重い

PSO を作るときドライバーはシェーダーの最終的なコンパイル（その GPU 専用の機械語への変換）を行います。数ミリ秒からものによっては数百ミリ秒かかります。フレームの途中で作るとその間、描画が止まります（シェーダー コンパイルのヒッチ）。

対策は 3 つあります。1 つ目は起動時かロード時に必要な PSO をすべて作ることです。2 つ目は別のスレッドで作ることで、PSO の作成はスレッド セーフなので、ロード用のスレッドで並列に作れます。3 つ目は作った PSO をディスクに保存して、次回の起動を速くする PSO キャッシュです。

### PSO キャッシュ（ライブラリ）

```cpp
// PSO をディスクに保存して、次回の起動で再利用する（ID3D12PipelineLibrary）。
ComPtr<ID3D12PipelineLibrary> library;
device1->CreatePipelineLibrary(cached_blob.data(), cached_blob.size(), IID_PPV_ARGS(&library));

// キャッシュにあれば読み込む。なければ作って登録する。
HRESULT hr = library->LoadGraphicsPipeline(L"OpaquePSO", &desc, IID_PPV_ARGS(&pso));
if (FAILED(hr)) {
  device->CreateGraphicsPipelineState(&desc, IID_PPV_ARGS(&pso));
  library->StorePipeline(L"OpaquePSO", pso.Get());
}
// 終了時に、library->Serialize(buffer, size) でファイルに保存する。
```

ドライバーや GPU が変わると、キャッシュは使えなくなります。読み込みに失敗したときに作り直す道を必ず持ちます。

## PSO の数を減らす

PSO を切り替える処理は重いので、同じ PSO で描くものをまとめて並べ替えると、切り替えの回数が減ります。使わない組み合わせはそもそも作りません。似た設定は共通にして PSO の数を抑えます。また、同じルート シグネチャを使う PSO どうしは、切り替えが軽くなります。

## よくあるミス

??? failure "`CreateGraphicsPipelineState` が失敗する"
    シェーダーの入力と入力レイアウトが合っていないか `RTVFormats` の数と `NumRenderTargets` が合っていないか、ルート シグネチャがシェーダーと合っていません。デバッグ レイヤーのメッセージで確認します。

??? failure "描画しても何も出ない（PSO の形式が違う）"
    PSO の `RTVFormats` が実際に描くレンダー ターゲットの形式と違います（`_SRGB` の有無など）。`DSVFormat` も同じです。

??? failure "最初に描くときフレームが止まる（ヒッチ）"
    描画の途中で PSO を作っています。起動時かロード時に作ります。

??? failure "三角形が見えない（裏面になっている）"
    `RasterizerState.FrontCounterClockwise` が既定の `FALSE` のままです。このサイトの規約は `TRUE` です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] PSO はパイプラインの設定をまとめた変更できないオブジェクト
    - [x] 作成は重い。起動時かロード時に全部作る。描画の途中で作らない
    - [x] 描画は `CreateGraphicsPipelineState`、計算は `CreateComputePipelineState`
    - [x] ブレンドやカリング、深度の変更は別の PSO にする
    - [x] PSO とコマンド リストのルート シグネチャは一致させる
    - [x] 作成は別スレッドで。PSO キャッシュで起動を速くする

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3D12Device](api/id3d12device.md)
- [Helper Functions](util.md)
- [Root Signature](root-signature.md)
- [Shaders and DXC](shaders-dxc.md)
- [Drawing a Triangle](triangle.md)
- [Microsoft Learn: パイプライン ステート](https://learn.microsoft.com/ja-jp/windows/win32/direct3d12/managing-graphics-pipeline-state-in-direct3d-12)
