---
title: Render Target View (RTV)
tags:
  - DirectX
---

# Render Target View (RTV)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>レンダー ターゲット ビュー（RTV）</strong>は、「テクスチャを、<strong>描き込み先</strong>として、見る窓」です。ピクセル シェーダーの出力は、RTV を通して、テクスチャに、書き込まれます。画面に出す、バック バッファも、シーンの HDR 色も、G バッファも、すべて、RTV を作って、描きます。

!!! tip "ポイント"
    - D3D11 では、リソース（テクスチャ）を、直接、パイプラインに、つなげない。<strong>ビュー</strong>を作って、つなぐ（[Resources and Views](../concepts/resources-views.md)）。
    - RTV は、<strong>書く用</strong>。読むには、別に、SRV を作る（[Shader Resource View (SRV)](shader-resource-view.md)）。
    - 作成は `CreateRenderTargetView`。つなぐのは `OMSetRenderTargets`。
    - テクスチャを作るとき、`D3D11_BIND_RENDER_TARGET` を、付けておく。
    - 同じテクスチャを、読みながら、書けない（RTV と SRV を、同時に束ねない）。

## バック バッファの RTV

```cpp
Microsoft::WRL::ComPtr<ID3D11Texture2D> back_buffer;
swap_chain->GetBuffer(0, IID_PPV_ARGS(&back_buffer));

D3D11_RENDER_TARGET_VIEW_DESC desc = {};
desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;             // 書くときに、リニア → sRGB に変換（swap-chain.md）
desc.ViewDimension = D3D11_RTV_DIMENSION_TEXTURE2D;
desc.Texture2D.MipSlice = 0;

Microsoft::WRL::ComPtr<ID3D11RenderTargetView> rtv;
device->CreateRenderTargetView(back_buffer.Get(), &desc, &rtv);
```

`desc` を、`nullptr` にすると、リソースと、同じ形式の、既定の、ビューが、できます。バック バッファは、`UNORM` で、作られているので、`_SRGB` の、ビューにしたいときだけ、記述子を、書きます。

| メンバー | 内容 |
| --- | --- |
| `Format` | ビューの、フォーマット。`DXGI_FORMAT_UNKNOWN` で、リソースと同じ |
| `ViewDimension` | `TEXTURE2D`（普通）、`TEXTURE2DARRAY`（配列の、一部の面）、`TEXTURE2DMS`（MSAA）、`TEXTURE3D` |
| `Texture2D.MipSlice` | どのミップに、書くか。ミップ チェーンの、各段に、描くときに、使う |

## 自分で作る、レンダー ターゲット

```cpp
// シーンを描く、HDR のテクスチャ。RTV で描き、SRV で読む（ポスト プロセス用）。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;   // 描く・読む、両方を、指定
Microsoft::WRL::ComPtr<ID3D11Texture2D> scene_texture;
device->CreateTexture2D(&desc, nullptr, &scene_texture);

device->CreateRenderTargetView(scene_texture.Get(), nullptr, &scene_rtv);
device->CreateShaderResourceView(scene_texture.Get(), nullptr, &scene_srv);
```

`BindFlags` に、`D3D11_BIND_RENDER_TARGET` を、付けると、RTV が作れます。あとで、読む（SRV）予定が、あるなら、`D3D11_BIND_SHADER_RESOURCE` も、同時に、付けます。<strong>`BindFlags` に、書かなかった種類の、ビューは、あとから、作れません。</strong>

## パイプラインにつなぐ

```cpp
ID3D11RenderTargetView* targets[] = {scene_rtv.Get()};
context->OMSetRenderTargets(1, targets, depth_dsv.Get());   // 第 3 引数: 深度ステンシル ビュー（無ければ nullptr）
```

`OMSetRenderTargets` は、<strong>出力マージャー</strong>（OM）に、描き込み先を、設定します。1 回で、最大 8 枚の、RTV を、束ねられます（[Multiple Render Targets](mrt.md)）。第 3 引数の、深度バッファが、無ければ、`nullptr` で、深度テストは、行われません（[Depth Buffer and DSV](depth-stencil.md)）。

| 引数 | 内容 |
| --- | --- |
| `NumViews` | RTV の数（0〜8） |
| `ppRenderTargetViews` | RTV の配列 |
| `pDepthStencilView` | DSV。無ければ `nullptr` |

## 読みながら、書けない

<strong>同じテクスチャを、RTV で書きつつ、SRV で読む</strong>ことは、できません。D3D11 は、エラーを、出さず、読む側の、束縛を、黙って、外します（デバッグ レイヤーが、有効なら、警告が、出ます）。

```cpp
// パス A で scene_texture に描いた後、パス B で、それを、読む前に、書き込みの束縛を、外す。
ID3D11RenderTargetView* none[] = {nullptr};
context->OMSetRenderTargets(1, none, nullptr);
context->PSSetShaderResources(0, 1, scene_srv.GetAddressOf());
```

詳しくは、[D3D11 Pass Recipes](pass-recipes.md) の、「束縛の衝突」です。

## よくあるミス

??? failure "`CreateRenderTargetView` が、失敗する"
    テクスチャに、`D3D11_BIND_RENDER_TARGET` を、付けていない。圧縮フォーマット（BC）や、深度フォーマットは、RTV に、できない。

??? failure "描いたのに、画面が、真っ黒"
    `OMSetRenderTargets` を、呼んでいない。または、ビューポートが、0 のまま。または、`Present` していない。

??? failure "読もうとした、テクスチャが、真っ黒"
    同じテクスチャが、まだ、RTV として、束ねられている。`OMSetRenderTargets` で、外してから、SRV で、束ねる。

??? failure "画面の色が、暗い（または、明るい）"
    バック バッファの、RTV を、`_SRGB` にしたのに、シェーダーで、ガンマ変換も、している（二重）。または、その逆。

## これだけ覚える

!!! abstract "まとめ"
    - [x] RTV ＝ テクスチャを、描き込み先として、見る窓
    - [x] 作成 `CreateRenderTargetView`、束縛 `OMSetRenderTargets`
    - [x] `BindFlags` に、`RENDER_TARGET`（読むなら `SHADER_RESOURCE` も）
    - [x] バック バッファの RTV は、`_SRGB` にできる
    - [x] 読みながら、書けない。つなぎ目で、外す

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Swap Chain](swap-chain.md)
- [Shader Resource View (SRV)](shader-resource-view.md)
- [Multiple Render Targets](mrt.md)
- [Resources and Views](../concepts/resources-views.md)
- [Microsoft Learn: ID3D11Device::CreateRenderTargetView](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createrendertargetview)
