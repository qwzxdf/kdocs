---
title: ID3D12PipelineLibrary
tags:
  - DirectX
api:
  - ID3D12PipelineLibrary
---

# ID3D12PipelineLibrary

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

PSO を作るときドライバーはシェーダーを GPU 専用の機械語に変換するので、数ミリ秒から数百ミリ秒かかります。PSO が数百個あるゲームでは、起動のたびに数十秒待たされることもあります。そこで、作った PSO を名前を付けて 1 つのファイルに保存し、次の起動で読み戻して変換を省きます。その入れ物が `ID3D12PipelineLibrary` です。

流れは 3 段階です。起動時にファイルを読んでライブラリを作り、PSO を名前で探して（`LoadGraphicsPipeline`）あれば使い、無ければ作って登録し（`StorePipeline`）、終了時にライブラリごとファイルへ書き出します（`Serialize`）。ライブラリを作るのは `ID3D12Device1::CreatePipelineLibrary` なので、先に `As` で `ID3D12Device1` を取り出します。

!!! tip "ポイント"
    - 名前は PSO ごとに一意。同じ名前を `StorePipeline` するとエラーになる。
    - ライブラリは GPU とドライバーの版に結びつく。合わないファイルは読み込みに失敗するので、作り直す道を持つ。
    - ファイルに書く大きさは `GetSerializedSize` で先に調べる。
    - 保存はゲーム終了時か、新しい PSO を登録したあと。

!!! info "このページを読む前に"
    PSO の作り方は [PSO](../pso.md)、1 つずつ保存する方法は [ID3D12PipelineState](id3d12pipelinestate.md#getcachedblob) にあります。

## メソッド一覧

| メソッド | 役割 |
| --- | --- |
| [`LoadGraphicsPipeline`](#loadgraphicspipeline) | 描画の PSO を名前で探して取り出す |
| [`LoadComputePipeline`](#loadcomputepipeline) | 計算の PSO を名前で探して取り出す |
| [`StorePipeline`](#storepipeline) | 作った PSO を名前を付けて登録する |
| [`GetSerializedSize`](#getserializedsize) | 保存に必要なバイト数 |
| [`Serialize`](#serialize) | ライブラリをバイト列に書き出す |

## ライブラリを作る

```cpp
ComPtr<ID3D12Device1> device1;
device.As(&device1);

std::vector<uint8_t> file = LoadFile(L"pso_library.bin");    // 無ければ空
ComPtr<ID3D12PipelineLibrary> library;
HRESULT hr = device1->CreatePipelineLibrary(file.data(), file.size(), IID_PPV_ARGS(&library));
if (FAILED(hr)) {
  // ファイルが壊れている、別の GPU やドライバーで作られた、など。空のライブラリを作り直す
  device1->CreatePipelineLibrary(nullptr, 0, IID_PPV_ARGS(&library));
}
```

`CreatePipelineLibrary` は、保存したバイト列とその大きさを受け取ります。空のライブラリを作るときは `nullptr` と 0 を渡します。バイト列が別のドライバーの版で作られたものだと、`D3D12_ERROR_DRIVER_VERSION_MISMATCH`、別のアダプターのものだと `D3D12_ERROR_ADAPTER_NOT_FOUND` で失敗します。どちらも「古いキャッシュを捨てて作り直す」合図です。

## メソッドの詳しい説明

### LoadGraphicsPipeline {#loadgraphicspipeline}

```cpp
HRESULT ID3D12PipelineLibrary::LoadGraphicsPipeline(
    LPCWSTR pName,
    const D3D12_GRAPHICS_PIPELINE_STATE_DESC* pDesc,
    REFIID riid,
    void** ppPipelineState);
```

ライブラリから、名前が `pName` の描画の PSO を取り出します。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pName` | `LPCWSTR` | 登録したときの名前 |
| `pDesc` | `const D3D12_GRAPHICS_PIPELINE_STATE_DESC*` | 作るときと同じ記述子 |
| `riid` | `REFIID` | 取り出すインターフェースの ID。`ID3D12PipelineState` |
| `ppPipelineState` | `void**` | 結果を受け取るポインタのアドレス |

`pDesc` が必要なのは、ライブラリには機械語だけが入っていて、ルート シグネチャやシェーダーのバイト列は含まれないからです。作るときと同じ記述子を渡し、ライブラリに入っている物と食い違っていないか確認させます。記述子が登録時と違うと、読み込みは失敗します。

戻り値は成功なら `S_OK` です。その名前が無いときは `E_INVALIDARG` で、これは「登録されていない」だけの合図なので、PSO を新しく作ってから `StorePipeline` します。

### LoadComputePipeline {#loadcomputepipeline}

```cpp
HRESULT ID3D12PipelineLibrary::LoadComputePipeline(
    LPCWSTR pName,
    const D3D12_COMPUTE_PIPELINE_STATE_DESC* pDesc,
    REFIID riid,
    void** ppPipelineState);
```

計算の PSO を取り出します。引数の意味と失敗の原因は `LoadGraphicsPipeline` と同じで、記述子が `D3D12_COMPUTE_PIPELINE_STATE_DESC` になるだけです。メッシュ シェーダーなどストリーム形式で作った PSO は、`ID3D12PipelineLibrary1::LoadPipeline` で取り出します。

### StorePipeline {#storepipeline}

```cpp
HRESULT ID3D12PipelineLibrary::StorePipeline(LPCWSTR pName, ID3D12PipelineState* pPipeline);
```

作った PSO に名前を付けてライブラリに登録します。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pName` | `LPCWSTR` | 付ける名前。ライブラリの中で一意 |
| `pPipeline` | `ID3D12PipelineState*` | 登録する PSO |

すでに同じ名前があると失敗します（`E_INVALIDARG`）。同じ名前の PSO を作り直したときは、先にライブラリを作り直すか名前を変えます。名前は、材質の名前やシェーダーの組み合わせから決めた文字列にします。

```cpp
HRESULT hr = library->LoadGraphicsPipeline(L"Opaque", &desc, IID_PPV_ARGS(&pso));
if (FAILED(hr)) {
  device->CreateGraphicsPipelineState(&desc, IID_PPV_ARGS(&pso));   // 無かったので作る
  library->StorePipeline(L"Opaque", pso.Get());                      // 次回のために登録する
}
```

### GetSerializedSize {#getserializedsize}

```cpp
SIZE_T ID3D12PipelineLibrary::GetSerializedSize();
```

ライブラリを書き出すのに必要なバイト数を返します。引数はありません。登録した PSO の数が増えると大きくなるので、`Serialize` の直前に呼びます。

### Serialize {#serialize}

```cpp
HRESULT ID3D12PipelineLibrary::Serialize(void* pData, SIZE_T DataSizeInBytes);
```

ライブラリの中身を `pData` に書き出します。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pData` | `void*` | 書き出す先のバッファ |
| `DataSizeInBytes` | `SIZE_T` | バッファの大きさ。`GetSerializedSize` の値に合わせる |

```cpp
std::vector<uint8_t> data(library->GetSerializedSize());
library->Serialize(data.data(), data.size());
SaveFile(L"pso_library.bin", data.data(), data.size());
```

大きさが合わないと失敗します。書き出したバイト列は、ライブラリを手放しても使えます。ただし `CreatePipelineLibrary` に渡すバイト列は、ライブラリが生きている間はメモリに残しておく必要があります。

## よくあるミス

??? failure "毎回 `LoadGraphicsPipeline` が失敗する"
    記述子が登録時と違います（シェーダー、ルート シグネチャ、形式など）。または、ドライバーの更新でキャッシュが無効になっています。失敗したら作って登録し直します。

??? failure "ライブラリを作った直後にバイト列を解放してクラッシュする"
    `CreatePipelineLibrary` に渡したバイト列は、ライブラリが使い続けます。ライブラリを手放すまで保持します。

## 関連ページ

- [PSO](../pso.md)
- [ID3D12PipelineState](id3d12pipelinestate.md)
- [Microsoft Learn: ID3D12PipelineLibrary](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12pipelinelibrary)
