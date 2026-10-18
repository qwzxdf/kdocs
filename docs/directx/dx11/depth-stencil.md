---
title: Depth Buffer and DSV
tags:
  - DirectX
---

# Depth Buffer and DSV

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>深度バッファ</strong>は、各ピクセルで、<strong>カメラから、最も近い、面までの、距離</strong>を、覚えておく、テクスチャです。3D の物を、描くとき、後から描いた物が、手前の物を、上書きしてしまわないように、「すでに、もっと近い物が、描かれているか」を、深度で、判定します（<strong>深度テスト</strong>）。<strong>深度ステンシル ビュー（DSV）</strong>は、そのテクスチャを、深度として、書き込む、窓です。

!!! tip "ポイント"
    - 深度バッファ ＝ 各ピクセルの「最も近い面の、距離」。描く物が、これより遠ければ、捨てる。
    - 作成: `D24_UNORM_S8_UINT`（ステンシルつき）か `D32_FLOAT`。<strong>読むなら、`R32_TYPELESS`</strong>（DSV と SRV で型を分ける）。
    - 毎フレーム、<strong>`ClearDepthStencilView` で 1.0 に</strong>戻す。
    - `OMSetRenderTargets` の、第 3 引数に、DSV を、渡す。
    - D3D11 の、深度は、0（近い）〜1（遠い）。精度を、上げるには、reverse-Z（[Projection](../../3d/projection.md)）。

## 作る（深度だけ）

```cpp
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_D32_FLOAT;                        // 32 ビット浮動小数点の深度
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_DEPTH_STENCIL;
Microsoft::WRL::ComPtr<ID3D11Texture2D> depth_texture;
device->CreateTexture2D(&desc, nullptr, &depth_texture);

Microsoft::WRL::ComPtr<ID3D11DepthStencilView> dsv;
device->CreateDepthStencilView(depth_texture.Get(), nullptr, &dsv);
```

深度バッファの、大きさは、<strong>レンダー ターゲットと、同じ</strong>にします（違うと、`OMSetRenderTargets` が、失敗します）。

## フォーマットの、選び方

| フォーマット | 内容 | 使いどころ |
| --- | --- | --- |
| `D32_FLOAT` | 32 ビット浮動小数点の深度。ステンシルなし | 精度が、必要、ステンシルが、不要（reverse-Z と相性が良い） |
| `D24_UNORM_S8_UINT` | 24 ビット固定小数点の深度 + 8 ビットのステンシル | ステンシルが、要る（輪郭、ポータル、皮膚のマスク） |
| `D32_FLOAT_S8X24_UINT` | 32 ビット浮動小数点 + 8 ビットのステンシル | 精度とステンシルの、両方 |
| `D16_UNORM` | 16 ビット | シャドウ マップ（精度が、粗くてよい、軽量版） |

reverse-Z（近い面が 1、遠い面が 0）は、浮動小数点の、深度と、組み合わせると、<strong>遠くの、精度が、大きく、上がります</strong>。固定小数点（`D24`）では、効果が、小さいです。

## 深度を、読む（SRV）

深度を、あとの、パス（AO、SSR、ソフト パーティクル、フォグ）で、シェーダーから、読むには、<strong>TYPELESS で作り、DSV と SRV で、型を分けます</strong>。

```cpp
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R32_TYPELESS;                     // 型は、ビューで決める
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &depth_texture);

D3D11_DEPTH_STENCIL_VIEW_DESC dsv_desc = {};
dsv_desc.Format = DXGI_FORMAT_D32_FLOAT;                    // 書く: 深度として
dsv_desc.ViewDimension = D3D11_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(depth_texture.Get(), &dsv_desc, &dsv);

D3D11_SHADER_RESOURCE_VIEW_DESC srv_desc = {};
srv_desc.Format = DXGI_FORMAT_R32_FLOAT;                    // 読む: 普通の float として
srv_desc.ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D;
srv_desc.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(depth_texture.Get(), &srv_desc, &depth_srv);
```

深度とステンシルの、組み合わせ（`D24_UNORM_S8_UINT`）の、場合は、typeless が `R24G8_TYPELESS`、深度を、読む SRV が `R24_UNORM_X8_TYPELESS`、ステンシルを、読む SRV が `X24_TYPELESS_G8_UINT` です。

| リソース | DSV | 深度を読む SRV | ステンシルを読む SRV |
| --- | --- | --- | --- |
| `R32_TYPELESS` | `D32_FLOAT` | `R32_FLOAT` | （ステンシルなし） |
| `R24G8_TYPELESS` | `D24_UNORM_S8_UINT` | `R24_UNORM_X8_TYPELESS` | `X24_TYPELESS_G8_UINT` |
| `R32G8X24_TYPELESS` | `D32_FLOAT_S8X24_UINT` | `R32_FLOAT_X8X24_TYPELESS` | `X32_TYPELESS_G8X24_UINT` |
| `R16_TYPELESS` | `D16_UNORM` | `R16_UNORM` | （ステンシルなし） |

## 読み取り専用の DSV

深度テストは、しつつ、<strong>同じ深度を、SRV でも、読みたい</strong>（ソフト パーティクル、半透明）ときは、<strong>読み取り専用の DSV</strong> を、作ります。

```cpp
dsv_desc.Flags = D3D11_DSV_READ_ONLY_DEPTH;                 // 深度は、書き込めない（テストだけ）
device->CreateDepthStencilView(depth_texture.Get(), &dsv_desc, &readonly_dsv);
```

通常の DSV を、束ねたまま、SRV で、読むと、束縛の衝突に、なりますが、読み取り専用の、DSV なら、同じ深度を、同時に、SRV として、読めます。

## クリア

```cpp
context->ClearDepthStencilView(dsv.Get(),
                               D3D11_CLEAR_DEPTH | D3D11_CLEAR_STENCIL,
                               1.0f,       // 深度の初期値: 最も遠い（reverse-Z なら 0.0f）
                               0);         // ステンシルの初期値
```

毎フレーム、必ず、クリアします。クリアしないと、前のフレームの、深度が、残り、新しい描画が、はじかれます。

## パイプラインにつなぐ

```cpp
context->OMSetRenderTargets(1, rtv.GetAddressOf(), dsv.Get());
```

DSV を、渡さない（`nullptr`）と、深度テストも、深度の書き込みも、行われません（ポスト プロセスなど）。深度テストの、設定（比較関数、書き込みの有無）は、[Depth-Stencil State](depth-stencil-state.md) です。

## 深度の、精度と、near・far

深度は、距離に、対して、非線形です（近くに、精度が、集中する）。`near` を、小さくしすぎると、遠くの、精度が、足りず、<strong>Z ファイティング</strong>（同じ位置の、面が、ちらつく）が、出ます。

| 対策 | 内容 |
| --- | --- |
| `near` を、大きく | 0.01 → 0.1 で、精度が、10 倍 |
| `far` を、小さく | 必要な、範囲に、絞る |
| `D32_FLOAT` | 24 ビットの、固定小数点より、精度が、よい |
| reverse-Z | `D32_FLOAT` と組み合わせて、遠くの精度が、大幅に、上がる |

## よくあるミス

??? failure "物が、前後、逆に見える（奥の物が、手前に）"
    深度バッファを、`OMSetRenderTargets` に、渡していない。または、深度テストを、無効にしている（`DepthEnable = FALSE`）。

??? failure "物が、半分だけ、消える、または、画面が、真っ黒"
    深度を、クリアしていない、または、クリア値が 0（全部、近い扱い）。`1.0` でクリア。

??? failure "`CreateShaderResourceView` が、深度で、失敗する"
    `D32_FLOAT` で、作っている。`R32_TYPELESS` で作り、DSV と SRV で、型を分ける。

??? failure "`OMSetRenderTargets` が、失敗する（警告）"
    深度バッファの大きさが、レンダー ターゲットと、違う。

??? failure "面が、ちらつく（Z ファイティング）"
    `near` が、小さすぎる。`D32_FLOAT` と reverse-Z に、する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 深度バッファ ＝ 各ピクセルの、最も近い面の距離。近い面が、勝つ
    - [x] 作成は `D32_FLOAT` か `D24_UNORM_S8_UINT`。読むなら `R32_TYPELESS`
    - [x] 毎フレーム `ClearDepthStencilView`（1.0）
    - [x] `OMSetRenderTargets` の第 3 引数に DSV
    - [x] 深度を読みつつ、テストする、には、読み取り専用の DSV
    - [x] 精度は、`near` を大きく、`D32_FLOAT`、reverse-Z

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Depth-Stencil State](depth-stencil-state.md)
- [Shader Resource View (SRV)](shader-resource-view.md)
- [Formats and Typeless](../concepts/formats.md)
- [Projection](../../3d/projection.md)
- [Microsoft Learn: ID3D11Device::CreateDepthStencilView](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createdepthstencilview)
