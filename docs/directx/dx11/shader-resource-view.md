---
title: Shader Resource View (SRV)
tags:
  - DirectX
---

# Shader Resource View (SRV)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>シェーダー リソース ビュー（SRV）</strong>は、テクスチャやバッファを <strong>シェーダーから、読む</strong>ための窓です。HLSL の `Texture2D`、`StructuredBuffer`、`Buffer` などは SRV を通して渡されます。G バッファをライティングで読む前のパスの結果をポスト プロセスで読むといった、<strong>パス間の受け渡し</strong>はすべて、SRV です。

!!! tip "ポイント"
    - SRV は <strong>読み取り専用</strong>。書くなら RTV か UAV。
    - 作成は `CreateShaderResourceView`。束縛は `PSSetShaderResources`（VS・CS なども同様）。
    - リソースの `BindFlags` に `D3D11_BIND_SHADER_RESOURCE` が必要。
    - HLSL では `register(t#)` が、スロット。`Texture2D g_albedo : register(t0);`
    - ビューの `Format` はリソースと違う（互換の）形式にできる（深度の、読み取りなど）。

## 作る

```cpp
// 一番簡単な形: リソースと、同じ形式・全ミップの、既定のビュー。
device->CreateShaderResourceView(texture.Get(), nullptr, &srv);
```

`nullptr` を渡すとリソースのフォーマット、全ミップ、全配列要素を見るビューができます。ほとんどの場合はこれで足ります。

### 記述子で指定する

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
| `TEXTURE2D` | 2D テクスチャ（ミップの範囲を指定） | `Texture2D` |
| `TEXTURE2DARRAY` | 配列の一部の要素 | `Texture2DArray` |
| `TEXTURECUBE` | キューブマップ | `TextureCube` |
| `TEXTURE2DMS` | MSAA テクスチャ | `Texture2DMS` |
| `TEXTURE3D` | 3D テクスチャ | `Texture3D` |
| `BUFFER` | バッファ（構造化、型つき） | `StructuredBuffer`、`Buffer` |
| `BUFFEREX` | 生のバッファ | `ByteAddressBuffer` |

特定のミップだけを見せるビューも作れます（ブルームのミップごとの読み取りなど）。

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

HLSL 側の `register(t0)`、`register(t1)` がスロット 0、1 に対応します。

```hlsl
Texture2D g_albedo : register(t0);
Texture2D g_normal : register(t1);
SamplerState g_sampler : register(s0);                      // サンプラー（sampler-state.md）

float4 PSMain(VSOutput input) : SV_Target {
  float4 albedo = g_albedo.Sample(g_sampler, input.uv);     // フィルタリングつきで読む
  return albedo;
}
```

## テクスチャを読む 3 つの方法

| 方法 | 内容 | 使いどころ |
| --- | --- | --- |
| `Sample(sampler, uv)` | サンプラーでフィルタリングして、読む（uv は 0〜1 の小数） | 普通のテクスチャ貼り |
| `SampleLevel(sampler, uv, mip)` | ミップを指定して、読む（頂点・計算シェーダーでも使える） | 計算シェーダー、ブルーム、ミップの明示 |
| `Load(int3(x, y, mip))` | サンプラーなしで、ピクセルをそのまま読む（整数座標） | G バッファ、深度、ポスト プロセスでピクセル 1 つ |

`Sample` はピクセル シェーダーの中で使えて隣のピクセルとの uv の差からミップを自動で、選びます。頂点シェーダーや計算シェーダーではその差が無いので `SampleLevel` を使います。

## 深度やレンダー ターゲットを読む

パスの出力を次のパスで読むとき <strong>書き込みの束縛を外す</strong>必要が、あります（[Render Target View (RTV)](render-target-view.md)）。

```cpp
// パス A: scene_texture に描く。
context->OMSetRenderTargets(1, scene_rtv.GetAddressOf(), depth_dsv.Get());
Draw();

// パス B の前: 書き込みの束縛を、外し、同じテクスチャを、SRV として、読む。
context->OMSetRenderTargets(0, nullptr, nullptr);
context->PSSetShaderResources(0, 1, scene_srv.GetAddressOf());
```

深度バッファを読むには `R32_TYPELESS` で作り SRV を `R32_FLOAT` で作ります（[Depth Buffer and DSV](depth-stencil.md)）。

## 束縛を外す

使い終わった SRV は後のパスで、同じテクスチャを書き込む前に外します。

```cpp
ID3D11ShaderResourceView* nulls[8] = {};                    // 8 個の、nullptr
context->PSSetShaderResources(0, 8, nulls);
```

D3D11 は同じリソースが、SRV と RTV（または UAV、DSV）に同時に束ねられると、<strong>読む側の束縛を黙って外します</strong>。結果は黒いテクスチャです。デバッグ レイヤーを有効にすると警告が、出ます。

## よくあるミス

??? failure "読んだ、テクスチャが真っ黒"
    同じテクスチャがまだ RTV（または DSV、UAV）として束ねられている。`OMSetRenderTargets` で外す。または、SRV がビューのフォーマット違いで、読めていない。

??? failure "`CreateShaderResourceView` が、失敗する"
    リソースの `BindFlags` に `SHADER_RESOURCE` が無い。深度を `D32_FLOAT` で作っていて SRV を作れない（`R32_TYPELESS` で作る）。

??? failure "シェーダーで、スロット番号を間違えて別のテクスチャが、読まれる"
    HLSL の `register(t#)` と `PSSetShaderResources` の `StartSlot` が、ずれている。スロットの割り当てを一覧にして、そろえる。

??? failure "ブルームの小さなミップが全部、同じ見た目になる"
    ビューの `MipLevels` が-1（全部）で `SampleLevel` のミップ指定と食い違っている。または、ミップごとに別の SRV を作っていない。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SRV ＝ シェーダーが、読むための窓。読み取り専用
    - [x] `CreateShaderResourceView`、`PSSetShaderResources`、HLSL の `register(t#)`
    - [x] `Sample`（フィルタ有り）、`SampleLevel`（ミップ指定）、`Load`（ピクセル直読み）
    - [x] 深度は `R32_TYPELESS` で作り SRV を `R32_FLOAT` に
    - [x] 読む前に書き込みの束縛を外す

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Texture2D](texture2d.md)
- [Sampler State](sampler-state.md)
- [Render Target View (RTV)](render-target-view.md)
- [Depth Buffer and DSV](depth-stencil.md)
- [Resources and Views](../concepts/resources-views.md)
- [Microsoft Learn: ID3D11Device::CreateShaderResourceView](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createshaderresourceview)
