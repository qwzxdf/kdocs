---
title: D3D12SerializeRootSignature
tags:
  - DirectX
api:
  - D3D12SerializeRootSignature
  - D3D12SerializeVersionedRootSignature
---

# D3D12SerializeRootSignature

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">D3D12</span>
`#include <d3d12.h>`
</div>

ルート シグネチャは、C++ の構造体（`D3D12_ROOT_SIGNATURE_DESC`）のままでは GPU のドライバーに渡せません。ドライバーが受け取るのは、バージョンつきのバイト列です。構造体をそのバイト列に変換する自由関数が `D3D12SerializeRootSignature` で、変換した結果を `ID3D12Device::CreateRootSignature` に渡して、ようやくルート シグネチャのオブジェクトができます。

メソッドではなく自由関数なので、デバイスがなくても呼べます。`d3d12.lib` をリンクします。

!!! tip "ポイント"
    - 失敗したときの理由は、4 つ目の引数 `ppErrorBlob` に文字列で入る。
    - `ppErrorBlob` が要らなければ `nullptr` でよいが、開発中は受け取るほうが早く直せる。
    - バージョン 1.1 の構造体（`D3D12_ROOT_SIGNATURE_DESC1`）は、この関数では扱えない。

!!! info "このページを読む前に"
    渡す構造体は [Root Signature Structs](root-signature-structs.md#d3d12_root_signature_desc)、結果の入れ物は [ID3DBlob](id3dblob.md)、変換後の使い道は [ID3D12RootSignature](id3d12rootsignature.md) で説明しています。

## D3D12SerializeRootSignature {#d3d12serializerootsignature}

```cpp
HRESULT D3D12SerializeRootSignature(
    const D3D12_ROOT_SIGNATURE_DESC* pRootSignature,
    D3D_ROOT_SIGNATURE_VERSION       Version,
    ID3DBlob**                       ppBlob,
    ID3DBlob**                       ppErrorBlob);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pRootSignature` | `const D3D12_ROOT_SIGNATURE_DESC*` | 変換する元の記述 |
| `Version` | `D3D_ROOT_SIGNATURE_VERSION` | 書き出すバージョン |
| `ppBlob` | `ID3DBlob**` | 変換結果のバイト列を受け取る |
| `ppErrorBlob` | `ID3DBlob**` | 失敗の理由（文字列）を受け取る。不要なら `nullptr` |

`pRootSignature` は、ルート パラメーターの配列、静的サンプラーの配列、`Flags` をまとめた構造体へのポインターです。配列の中身はこの関数が呼ばれている間だけ読まれるので、変換が終わったら元の構造体やその配列は捨てても構いません。

`Version` には `D3D_ROOT_SIGNATURE_VERSION_1_0`（`D3D_ROOT_SIGNATURE_VERSION_1` も同じ値）を渡します。この関数が受け取る構造体はバージョン 1.0 の形だけなので、`D3D_ROOT_SIGNATURE_VERSION_1_1` を渡すと失敗します。

`ppBlob` には、成功したときにバイト列が入ります。`GetBufferPointer` と `GetBufferSize` をそのまま `CreateRootSignature` の第 2 引数と第 3 引数に渡します。`ppBlob` に `nullptr` を渡すのは、変換結果が要らないということなので意味がありません。

`ppErrorBlob` には、失敗したとき（記述が正しくないとき）に原因を書いた文字列が入ります。成功したときは `nullptr` のままです。

戻り値は、成功なら `S_OK` です。記述の矛盾（ディスクリプタ テーブルの範囲が重なっている、など）は `E_INVALIDARG` で、詳しい理由は `ppErrorBlob` の文字列を見ます。

```cpp
ComPtr<ID3DBlob> blob;
ComPtr<ID3DBlob> error;
HRESULT hr = D3D12SerializeRootSignature(&desc, D3D_ROOT_SIGNATURE_VERSION_1_0,
                                         &blob, &error);
if (FAILED(hr)) {
  if (error) {
    OutputDebugStringA(static_cast<const char*>(error->GetBufferPointer()));
  }
  return false;
}
hr = device->CreateRootSignature(0, blob->GetBufferPointer(), blob->GetBufferSize(),
                                 IID_PPV_ARGS(&root_signature));
```

`error` が空のまま `GetBufferPointer` を呼ぶと、`nullptr` へのアクセスでクラッシュします。必ず `if (error)` で確かめてください。

## D3D12SerializeVersionedRootSignature {#d3d12serializeversionedrootsignature}

```cpp
HRESULT D3D12SerializeVersionedRootSignature(
    const D3D12_VERSIONED_ROOT_SIGNATURE_DESC* pRootSignature,
    ID3DBlob**                                 ppBlob,
    ID3DBlob**                                 ppErrorBlob);
```

バージョン 1.1 の記述（`D3D12_ROOT_SIGNATURE_DESC1`）も扱える版です。`D3D12_VERSIONED_ROOT_SIGNATURE_DESC` は、先頭の `Version` メンバーで 1.0 と 1.1 のどちらの構造体が入っているかを示す入れ物です。ディスクリプタ範囲に `D3D12_DESCRIPTOR_RANGE_FLAGS` を付けて「ディスクリプタはコマンド リストの実行中に書き換えない」などの約束をドライバーに伝えたいときに使います。

バージョン 1.1 に対応していない古い環境ではシリアライズ自体はできても、`CreateRootSignature` が失敗することがあります。まず `D3D12SerializeRootSignature`（1.0）で十分かどうかを考えてください。

## よくあるミス

??? failure "`D3D_ROOT_SIGNATURE_VERSION_1_1` を渡して失敗する"
    `D3D12SerializeRootSignature` は 1.0 の構造体しか受け取りません。1.1 の機能が欲しいときは `D3D12SerializeVersionedRootSignature` を使います。

??? failure "エラーの理由が見えない"
    `ppErrorBlob` に `nullptr` を渡すと、失敗したときに `E_INVALIDARG` だけが返り、原因が分かりません。開発中は受け取って `OutputDebugStringA` で出します。

## 関連ページ

- [ID3D12RootSignature](id3d12rootsignature.md)
- [Root Signature Structs](root-signature-structs.md)
- [ID3DBlob](id3dblob.md)
- [Root Signature](../root-signature.md)
