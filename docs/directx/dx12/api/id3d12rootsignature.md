---
title: ID3D12RootSignature
tags:
  - DirectX
api:
  - ID3D12RootSignature
---

# ID3D12RootSignature

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

シェーダーが使うテクスチャや定数バッファを、CPU 側のどこから受け取るか。その「引数の型」を決めておくのがルート シグネチャです。`ID3D12RootSignature` は、その型を表すオブジェクトで、PSO を作るときとコマンド リストで描くときの両方に渡します。

このインターフェースには、自分のメソッドはありません。`ID3D12Object` から引き継いだ `SetName` などがあるだけです。作る手順に注意が要ります。まず `D3D12SerializeRootSignature` で記述子をバイト列（`ID3DBlob`）に変換し、それを `ID3D12Device::CreateRootSignature` に渡します。

!!! tip "ポイント"
    - 作る流れは「記述子 → `D3D12SerializeRootSignature` → `ID3DBlob` → `CreateRootSignature`」。
    - PSO にもコマンド リストにも同じルート シグネチャを渡す。食い違うと描画が壊れる。
    - HLSL の中でルート シグネチャを書いておけば、コンパイラーが blob にして出してくれる。

!!! info "このページを読む前に"
    引数の種類（定数、CBV、ディスクリプタ テーブル）は [Root Signature](../root-signature.md) で説明しています。

## 作る

```cpp
D3D12_ROOT_SIGNATURE_DESC desc = {};
desc.Flags = D3D12_ROOT_SIGNATURE_FLAG_ALLOW_INPUT_ASSEMBLER_INPUT_LAYOUT;

ComPtr<ID3DBlob> blob;
ComPtr<ID3DBlob> error;
HRESULT hr = D3D12SerializeRootSignature(&desc, D3D_ROOT_SIGNATURE_VERSION_1_0, &blob, &error);
if (FAILED(hr)) {
  OutputDebugStringA(static_cast<const char*>(error->GetBufferPointer()));  // 理由が文字列で入る
}

ComPtr<ID3D12RootSignature> root_signature;
device->CreateRootSignature(0, blob->GetBufferPointer(), blob->GetBufferSize(),
                            IID_PPV_ARGS(&root_signature));
```

`D3D12SerializeRootSignature` の引数と戻り値は [D3D12SerializeRootSignature](d3d12serializerootsignature.md)、`CreateRootSignature` は [ID3D12Device](id3d12device.md#createrootsignature) で説明しています。

## 使う

PSO を作るときに記述子の `pRootSignature` へ渡し、描くときにコマンド リストへ渡します。

```cpp
desc.pRootSignature = root_signature.Get();                          // PSO を作る記述子
command_list->SetGraphicsRootSignature(root_signature.Get());        // 描く前に毎回
```

PSO のルート シグネチャとコマンド リストに設定したルート シグネチャが食い違うと、デバッグ レイヤーがエラーを出し、描画の結果も壊れます。リストをリセットするたびに設定し直す必要があるのは、リストの状態が `Reset` でなくなるからです（[`SetGraphicsRootSignature`](id3d12graphicscommandlist.md#setgraphicsrootsignature)）。

## HLSL に書く方法

ルート シグネチャは、HLSL のシェーダーの中にも書けます。`[RootSignature(...)]` 属性を付けて DXC でコンパイルすると、シェーダーのバイナリにルート シグネチャが含まれます。`CreateRootSignature` には、シェーダー全体のバイト列をそのまま渡せます。C++ とシェーダーの両方に同じ内容を書く二重管理をなくせます。

## 関連ページ

- [Root Signature](../root-signature.md)
- [D3D12SerializeRootSignature](d3d12serializerootsignature.md)
- [ID3D12Device](id3d12device.md#createrootsignature)
- [Microsoft Learn: ID3D12RootSignature](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nn-d3d12-id3d12rootsignature)
