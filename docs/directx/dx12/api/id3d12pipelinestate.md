---
title: ID3D12PipelineState
tags:
  - DirectX
api:
  - ID3D12PipelineState
---

# ID3D12PipelineState

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

PSO（Pipeline State Object）は、シェーダー、ブレンド、ラスタライザー、深度などの設定を 1 つにまとめた不変のオブジェクトです。`ID3D12PipelineState` は、その PSO を表すインターフェースです。作ったあとに中身は変えられず、描画のときは `SetPipelineState` で切り替えるだけです。

メソッドは `GetCachedBlob` の 1 つだけです。PSO を作るのは重い処理なので、ドライバーが作った機械語のキャッシュをファイルに保存して、次の起動ではそれを渡して速く作るために使います。

!!! tip "ポイント"
    - 作るのは `CreateGraphicsPipelineState` と `CreateComputePipelineState`。
    - 作ったあとに設定は変えられない。変えたければ新しい PSO を作る。
    - `GetCachedBlob` で取った塊は、同じ GPU とドライバーでしか使えない。
    - 複数の PSO をまとめて保存するなら [ID3D12PipelineLibrary](id3d12pipelinelibrary.md) のほうが楽。

!!! info "このページを読む前に"
    PSO の中身の組み立て方は [PSO](../pso.md)、作るメソッドは [ID3D12Device](id3d12device.md#creategraphicspipelinestate) にあります。

## メソッド一覧

| メソッド | 役割 |
| --- | --- |
| [`GetCachedBlob`](#getcachedblob) | ドライバーが作った機械語のキャッシュを取り出す |

## メソッドの詳しい説明

### GetCachedBlob {#getcachedblob}

```cpp
HRESULT ID3D12PipelineState::GetCachedBlob(ID3DBlob** ppBlob);
```

PSO を作るときにドライバーがシェーダーから作った、その GPU 専用の機械語を、バイト列の塊として取り出します。

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ppBlob` | `ID3DBlob**` | 結果を受け取る。`GetBufferPointer` と `GetBufferSize` で中身を読む |

取り出した塊をファイルに保存しておき、次の起動で PSO を作るときに記述子の `CachedPSO`（`D3D12_CACHED_PIPELINE_STATE`）へ渡すと、シェーダーの最終コンパイルを省けます。

```cpp
// 保存する（初回の起動後）
ComPtr<ID3DBlob> blob;
pso->GetCachedBlob(&blob);
SaveFile(L"opaque.psocache", blob->GetBufferPointer(), blob->GetBufferSize());

// 次の起動で使う
std::vector<uint8_t> cache = LoadFile(L"opaque.psocache");
desc.CachedPSO.pCachedBlob = cache.data();
desc.CachedPSO.CachedBlobSizeInBytes = cache.size();
HRESULT hr = device->CreateGraphicsPipelineState(&desc, IID_PPV_ARGS(&pso));
if (FAILED(hr)) {
  // キャッシュが合わなかった。CachedPSO を空にして作り直す
  desc.CachedPSO = {};
  device->CreateGraphicsPipelineState(&desc, IID_PPV_ARGS(&pso));
}
```

キャッシュは GPU とドライバーの版に結びついています。ドライバーを更新した PC や別の GPU では使えず、`CreateGraphicsPipelineState` が失敗することがあります。その場合は `CachedPSO` を空にして作り直す道を必ず用意します。このページの方法は PSO 1 つごとにファイルを作りますが、数が多いときは [ID3D12PipelineLibrary](id3d12pipelinelibrary.md) で 1 つのファイルにまとめられます。

戻り値は成功なら `S_OK` です。

## 関連ページ

- [PSO](../pso.md)
- [ID3D12Device](id3d12device.md#creategraphicspipelinestate)
- [ID3D12PipelineLibrary](id3d12pipelinelibrary.md)
- [Microsoft Learn: ID3D12PipelineState](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12pipelinestate)
