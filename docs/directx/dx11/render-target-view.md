---
title: Render Target View (RTV)
tags:
  - DirectX
---

# Render Target View (RTV)

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>レンダー ターゲット ビュー（RTV）</strong>は、「テクスチャを <strong>描き込み先</strong>として、見る窓」です。ピクセル シェーダーの出力は RTV を通してテクスチャに書き込まれます。画面に出すバック バッファもシーンの HDR 色も G バッファもすべて、RTV を作って描きます。

!!! tip "ポイント"
    - D3D11 ではリソース（テクスチャ）を直接、パイプラインにつなげない。<strong>ビュー</strong>を作ってつなぐ（[Resources and Views](../concepts/resources-views.md)）。
    - RTV は <strong>書く用</strong>。読むには別に SRV を作る（[Shader Resource View (SRV)](shader-resource-view.md)）。
    - 作成は `CreateRenderTargetView`。つなぐのは `OMSetRenderTargets`。
    - テクスチャを作るとき `D3D11_BIND_RENDER_TARGET` を付けておく。
    - 同じテクスチャを読みながら書けない（RTV と SRV を同時に束ねない）。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

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

`desc` を `nullptr` にするとリソースと同じ形式の既定のビューができます。バック バッファは `UNORM` で作られているので `_SRGB` のビューにしたいときだけ記述子を、書きます。

| メンバー | 内容 |
| --- | --- |
| `Format` | ビューのフォーマット。`DXGI_FORMAT_UNKNOWN` でリソースと同じ |
| `ViewDimension` | `TEXTURE2D`（普通）、`TEXTURE2DARRAY`（配列の一部の面）、`TEXTURE2DMS`（MSAA）、`TEXTURE3D` |
| `Texture2D.MipSlice` | どのミップに書くか。ミップ チェーンの各段に描くときに使う |

## 自分で作るレンダー ターゲット

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

`BindFlags` に `D3D11_BIND_RENDER_TARGET` を付けると RTV が作れます。あとで読む（SRV）予定があるなら `D3D11_BIND_SHADER_RESOURCE` も同時に付けます。<strong>`BindFlags` に書かなかった種類のビューはあとから作れません。</strong>

## パイプラインにつなぐ

```cpp
ID3D11RenderTargetView* targets[] = {scene_rtv.Get()};
context->OMSetRenderTargets(1, targets, depth_dsv.Get());   // 第 3 引数: 深度ステンシル ビュー（無ければ nullptr）
```

`OMSetRenderTargets` は <strong>出力マージャー</strong>（OM）に描き込み先を設定します。1 回で最大 8 枚の RTV を束ねられます（[Multiple Render Targets](mrt.md)）。第 3 引数の深度バッファが、無ければ `nullptr` で深度テストは行われません（[Depth Buffer and DSV](depth-stencil.md)）。

| 引数 | 内容 |
| --- | --- |
| `NumViews` | RTV の数（0〜8） |
| `ppRenderTargetViews` | RTV の配列 |
| `pDepthStencilView` | DSV。無ければ `nullptr` |

## 読みながら書けない

<strong>同じテクスチャを RTV で書きつつ SRV で読む</strong>ことはできません。D3D11 はエラーを出さず読む側の束縛を黙って外します（デバッグ レイヤーが、有効なら警告が出ます）。

```cpp
// パス A で scene_texture に描いた後、パス B で、それを、読む前に、書き込みの束縛を、外す。
ID3D11RenderTargetView* none[] = {nullptr};
context->OMSetRenderTargets(1, none, nullptr);
context->PSSetShaderResources(0, 1, scene_srv.GetAddressOf());
```

詳しくは[D3D11 Pass Recipes](pass-recipes.md) の「束縛の衝突」です。

## よくあるミス

??? failure "`CreateRenderTargetView` が、失敗する"
    テクスチャに `D3D11_BIND_RENDER_TARGET` を付けていない。圧縮フォーマット（BC）や深度フォーマットは、RTV にできない。

??? failure "描いたのに画面が、真っ黒"
    `OMSetRenderTargets` を呼んでいない。または、ビューポートが 0 のまま。または、`Present` していない。

??? failure "読もうとしたテクスチャが真っ黒"
    同じテクスチャがまだ RTV として束ねられている。`OMSetRenderTargets` で外してから SRV で束ねる。

??? failure "画面の色が、暗い（または明るい）"
    バック バッファの RTV を `_SRGB` にしたのにシェーダーでガンマ変換も、している（二重）。または、その逆。

## これだけ覚える

!!! abstract "まとめ"
    - [x] RTV ＝ テクスチャを描き込み先として見る窓
    - [x] 作成 `CreateRenderTargetView`、束縛 `OMSetRenderTargets`
    - [x] `BindFlags` に `RENDER_TARGET`（読むなら `SHADER_RESOURCE` も）
    - [x] バック バッファの RTV は、`_SRGB` にできる
    - [x] 読みながら、書けない。つなぎ目で外す

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Swap Chain](swap-chain.md)
- [Shader Resource View (SRV)](shader-resource-view.md)
- [Multiple Render Targets](mrt.md)
- [Resources and Views](../concepts/resources-views.md)
- [Microsoft Learn: ID3D11Device::CreateRenderTargetView](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createrendertargetview)
