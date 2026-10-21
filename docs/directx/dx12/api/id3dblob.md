---
title: ID3DBlob
tags:
  - DirectX
api:
  - ID3DBlob
---

# ID3DBlob

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3dcommon.h>`
</div>

シェーダーのコンパイル結果やシリアライズしたルート シグネチャは、どちらも「ただのバイト列」です。それを入れて運ぶ入れ物が `ID3DBlob` です。中身の意味は持たずバイト列の先頭アドレスと大きさだけを教えてくれます。

出てくる場面は 3 つあります。`D3DCompileFromFile` が返すコンパイル済みシェーダー、`D3D12SerializeRootSignature` が返すルート シグネチャ、そしてコンパイルに失敗したときのエラー メッセージです。エラー メッセージも `ID3DBlob` に入った文字列です。

!!! tip "ポイント"
    - 中身を見るのは `GetBufferPointer` と `GetBufferSize` の 2 つだけ。
    - エラー メッセージの blob は、`char*` の文字列として読める。
    - コンパイル済みシェーダーの blob は、そのまま PSO に渡す（`D3D12_SHADER_BYTECODE`）。
    - 寿命は `ComPtr` で管理する。blob を解放すると取り出したポインタも無効になる。

!!! info "このページを読む前に"
    シェーダーのコンパイルは [Shaders and DXC](../shaders-dxc.md)、ルート シグネチャは [Root Signature](../root-signature.md) で説明しています。

## メソッド一覧

| メソッド | 役割 |
| --- | --- |
| [`GetBufferPointer`](#getbufferpointer) | バイト列の先頭アドレス |
| [`GetBufferSize`](#getbuffersize) | バイト列の大きさ |

## メソッド

### GetBufferPointer {#getbufferpointer}

```cpp
LPVOID ID3DBlob::GetBufferPointer();
```

バイト列の先頭アドレスを返します。引数はありません。型は `void*` なので使うときに用途に合った型へ変換します。

エラー メッセージは `char*` に変換して、`OutputDebugStringA` などで出力します。コンパイル済みシェーダーはそのまま `D3D12_SHADER_BYTECODE` の `pShaderBytecode` に渡します。blob を解放するとこのポインタは無効になるので、blob が生きている間だけ使います。

```cpp
ComPtr<ID3DBlob> shader, error;
HRESULT hr = D3DCompileFromFile(L"shader.hlsl", nullptr, nullptr, "VSMain", "vs_5_1", 0, 0, &shader, &error);
if (FAILED(hr) && error) {
  OutputDebugStringA(static_cast<const char*>(error->GetBufferPointer()));  // エラーの文字列
}
```

### GetBufferSize {#getbuffersize}

```cpp
SIZE_T ID3DBlob::GetBufferSize();
```

バイト列の大きさをバイト数で返します。引数はありません。

`D3D12_SHADER_BYTECODE` の `BytecodeLength` や `CreateRootSignature` の `blobLengthInBytes` にはこの値を渡します。エラー メッセージの blob は末尾に終端の `\0` を含むので、文字数は `GetBufferSize() - 1` です。

```cpp
D3D12_SHADER_BYTECODE bytecode = {shader->GetBufferPointer(), shader->GetBufferSize()};
```

## 関連ページ

- [Shaders and DXC](../shaders-dxc.md)
- [Root Signature](../root-signature.md)
- [ID3D12Device](id3d12device.md)
- [Microsoft Learn: ID3DBlob](https://learn.microsoft.com/ja-jp/windows/win32/api/d3dcommon/nn-d3dcommon-id3d10blob)
