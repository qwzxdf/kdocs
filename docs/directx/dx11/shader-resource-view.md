---
title: Shader Resource View (SRV)
tags:
  - DirectX
---

# Shader Resource View (SRV)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>シェーダー リソース ビュー（SRV）</strong>は、テクスチャや、バッファを、<strong>シェーダーから、読む</strong>ための、窓です。HLSL の `Texture2D`、`StructuredBuffer`、`Buffer` などは、SRV を、通して、渡されます。G バッファを、ライティングで、読む、前の、パスの、結果を、ポスト プロセスで、読む、といった、<strong>パス間の、受け渡し</strong>は、すべて、SRV です。

!!! tip "ポイント"
    - SRV は、<strong>読み取り専用</strong>。書くなら、RTV か UAV。
    - 作成は `CreateShaderResourceView`。束縛は `PSSetShaderResources`（VS・CS なども、同様）。
    - リソースの、`BindFlags` に、`D3D11_BIND_SHADER_RESOURCE` が、必要。
    - HLSL では、`register(t#)` が、スロット。`Texture2D g_albedo : register(t0);`
    - ビューの、`Format` は、リソースと、違う（互換の）形式に、できる（深度の、読み取りなど）。

## 作る

```cpp
// 一番簡単な形: リソースと、同じ形式・全ミップの、既定のビュー。
device->CreateShaderResourceView(texture.Get(), nullptr, &srv);
```

`nullptr` を、渡すと、リソースの、フォーマット、全ミップ、全配列要素を、見る、ビューが、できます。ほとんどの場合は、これで、足ります。

### 記述子で、指定する

```cpp
D3D11_SHADER_RESOURCE_VIEW_DESC desc = {};
desc.Format = DXGI_FORMAT_R32_FLOAT;                        // 深度の R32_TYPELESS を、float として、読む
desc.ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D;
desc.Texture2D.MostDetailedMip = 0;                         // 最も細かい段（0 = 元の大きさ）
desc.Texture2D.MipLevels = 1;                               // 見える段数（-1 で、全部）
device->CreateShaderResourceView(depth_texture.Get(), &desc, &depth_srv);
```

| `ViewDimension` | 内容 | HLSL の型 |
| --- | --- | --- |
| `TEXTURE2D` | 2D テクスチャ（ミップの範囲を、指定） | `Texture2D` |
| `TEXTURE2DARRAY` | 配列の、一部の要素 | `Texture2DArray` |
| `TEXTURECUBE` | キューブマップ | `TextureCube` |
| `TEXTURE2DMS` | MSAA テクスチャ | `Texture2DMS` |
| `TEXTURE3D` | 3D テクスチャ | `Texture3D` |
| `BUFFER` | バッファ（構造化、型つき） | `StructuredBuffer`、`Buffer` |
| `BUFFEREX` | 生のバッファ | `ByteAddressBuffer` |

特定の、ミップだけを、見せる、ビューも、作れます（ブルームの、ミップごとの、読み取りなど）。

```cpp
desc.Texture2D.MostDetailedMip = 3;                         // ミップ 3 から
desc.Texture2D.MipLevels = 1;                               // 1 段だけ
```

## パイプラインにつなぐ

```cpp
ID3D11ShaderResourceView* views[] = {albedo_srv.Get(), normal_srv.Get()};
context->PSSetShaderResources(0, 2, views);                 // スロット 0 から 2 個。ピクセル シェーダー用
```

| 関数 | 段 |
| --- | --- |
| `VSSetShaderResources` | 頂点シェーダー |
| `PSSetShaderResources` | ピクセル シェーダー |
| `CSSetShaderResources` | 計算シェーダー |
| `GSSetShaderResources`、`HSSet…`、`DSSet…` | ジオメトリ、ハル、ドメイン |

HLSL 側の、`register(t0)`、`register(t1)` が、スロット 0、1 に、対応します。

```hlsl
Texture2D g_albedo : register(t0);
Texture2D g_normal : register(t1);
SamplerState g_sampler : register(s0);                      // サンプラー（sampler-state.md）

float4 PSMain(VSOutput input) : SV_Target {
  float4 albedo = g_albedo.Sample(g_sampler, input.uv);     // フィルタリングつきで読む
  return albedo;
}
```

## テクスチャを、読む、3 つの方法

| 方法 | 内容 | 使いどころ |
| --- | --- | --- |
| `Sample(sampler, uv)` | サンプラーで、フィルタリングして、読む（uv は、0〜1 の小数） | 普通の、テクスチャ貼り |
| `SampleLevel(sampler, uv, mip)` | ミップを、指定して、読む（頂点・計算シェーダーでも、使える） | 計算シェーダー、ブルーム、ミップの、明示 |
| `Load(int3(x, y, mip))` | サンプラーなしで、ピクセルを、そのまま、読む（整数座標） | G バッファ、深度、ポスト プロセスで、ピクセル 1 つ |

`Sample` は、ピクセル シェーダーの中で、使えて、隣の、ピクセルとの、uv の差から、ミップを、自動で、選びます。頂点シェーダーや、計算シェーダーでは、その差が、無いので、`SampleLevel` を使います。

## 深度や、レンダー ターゲットを、読む

パスの出力を、次のパスで、読むとき、<strong>書き込みの、束縛を、外す</strong>必要が、あります（[Render Target View (RTV)](render-target-view.md)）。

```cpp
// パス A: scene_texture に描く。
context->OMSetRenderTargets(1, scene_rtv.GetAddressOf(), depth_dsv.Get());
Draw();

// パス B の前: 書き込みの束縛を、外し、同じテクスチャを、SRV として、読む。
context->OMSetRenderTargets(0, nullptr, nullptr);
context->PSSetShaderResources(0, 1, scene_srv.GetAddressOf());
```

深度バッファを、読むには、`R32_TYPELESS` で作り、SRV を、`R32_FLOAT` で、作ります（[Depth Buffer and DSV](depth-stencil.md)）。

## 束縛を、外す

使い終わった、SRV は、後のパスで、同じテクスチャを、書き込む前に、外します。

```cpp
ID3D11ShaderResourceView* nulls[8] = {};                    // 8 個の、nullptr
context->PSSetShaderResources(0, 8, nulls);
```

D3D11 は、同じリソースが、SRV と RTV（または、UAV、DSV）に、同時に、束ねられると、<strong>読む側の、束縛を、黙って、外します</strong>。結果は、黒い、テクスチャです。デバッグ レイヤーを、有効にすると、警告が、出ます。

## よくあるミス

??? failure "読んだ、テクスチャが、真っ黒"
    同じテクスチャが、まだ、RTV（または、DSV、UAV）として、束ねられている。`OMSetRenderTargets` で、外す。または、SRV が、ビューの、フォーマット違いで、読めていない。

??? failure "`CreateShaderResourceView` が、失敗する"
    リソースの、`BindFlags` に、`SHADER_RESOURCE` が、無い。深度を、`D32_FLOAT` で、作っていて、SRV を、作れない（`R32_TYPELESS` で、作る）。

??? failure "シェーダーで、スロット番号を、間違えて、別のテクスチャが、読まれる"
    HLSL の `register(t#)` と、`PSSetShaderResources` の、`StartSlot` が、ずれている。スロットの、割り当てを、一覧に、して、そろえる。

??? failure "ブルームの、小さなミップが、全部、同じ見た目になる"
    ビューの、`MipLevels` が、-1（全部）で、`SampleLevel` の、ミップ指定と、食い違っている。または、ミップごとに、別の SRV を、作っていない。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SRV ＝ シェーダーが、読むための、窓。読み取り専用
    - [x] `CreateShaderResourceView`、`PSSetShaderResources`、HLSL の `register(t#)`
    - [x] `Sample`（フィルタ有り）、`SampleLevel`（ミップ指定）、`Load`（ピクセル直読み）
    - [x] 深度は、`R32_TYPELESS` で作り、SRV を `R32_FLOAT` に
    - [x] 読む前に、書き込みの束縛を、外す

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Texture2D](texture2d.md)
- [Sampler State](sampler-state.md)
- [Render Target View (RTV)](render-target-view.md)
- [Depth Buffer and DSV](depth-stencil.md)
- [Resources and Views](../concepts/resources-views.md)
- [Microsoft Learn: ID3D11Device::CreateShaderResourceView](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createshaderresourceview)
