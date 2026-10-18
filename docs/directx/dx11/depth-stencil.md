---
title: Depth Buffer and DSV
tags:
  - DirectX
---

# Depth Buffer and DSV

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>深度バッファ</strong>は各ピクセルで、<strong>カメラから最も近い面までの距離</strong>を覚えておくテクスチャです。3D の物を描くとき後から描いた物が、手前の物を上書きしてしまわないように「すでにもっと近い物が描かれているか」を深度で、判定します（<strong>深度テスト</strong>）。<strong>深度ステンシル ビュー（DSV）</strong>は、そのテクスチャを深度として書き込む窓です。

!!! tip "ポイント"
    - 深度バッファ ＝ 各ピクセルの「最も近い面の距離」。描く物がこれより遠ければ捨てる。
    - 作成: `D24_UNORM_S8_UINT`（ステンシルつき）か `D32_FLOAT`。<strong>読むなら `R32_TYPELESS`</strong>（DSV と SRV で型を分ける）。
    - 毎フレーム、<strong>`ClearDepthStencilView` で 1.0 に</strong>戻す。
    - `OMSetRenderTargets` の第 3 引数に DSV を渡す。
    - D3D11 の深度は 0（近い）〜1（遠い）。精度を上げるには reverse-Z（[Projection](../../3d/projection.md)）。

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

深度バッファの大きさは <strong>レンダー ターゲットと同じ</strong>にします（違うと `OMSetRenderTargets` が、失敗します）。

## フォーマットの選び方

| フォーマット | 内容 | 使いどころ |
| --- | --- | --- |
| `D32_FLOAT` | 32 ビット浮動小数点の深度。ステンシルなし | 精度が必要、ステンシルが不要（reverse-Z と相性が良い） |
| `D24_UNORM_S8_UINT` | 24 ビット固定小数点の深度 + 8 ビットのステンシル | ステンシルが、要る（輪郭、ポータル、皮膚のマスク） |
| `D32_FLOAT_S8X24_UINT` | 32 ビット浮動小数点 + 8 ビットのステンシル | 精度とステンシルの、両方 |
| `D16_UNORM` | 16 ビット | シャドウ マップ（精度が、粗くてよい軽量版） |

reverse-Z（近い面が 1、遠い面が 0）は浮動小数点の深度と組み合わせると <strong>遠くの精度が大きく、上がります</strong>。固定小数点（`D24`）では効果が小さいです。

## 深度を読む（SRV）

深度をあとのパス（AO、SSR、ソフト パーティクル、フォグ）でシェーダーから読むには <strong>TYPELESS で作り DSV と SRV で、型を分けます</strong>。

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

深度とステンシルの組み合わせ（`D24_UNORM_S8_UINT`）の場合は、typeless が `R24G8_TYPELESS`、深度を読む SRV が `R24_UNORM_X8_TYPELESS`、ステンシルを読む SRV が `X24_TYPELESS_G8_UINT` です。

| リソース | DSV | 深度を読む SRV | ステンシルを読む SRV |
| --- | --- | --- | --- |
| `R32_TYPELESS` | `D32_FLOAT` | `R32_FLOAT` | （ステンシルなし） |
| `R24G8_TYPELESS` | `D24_UNORM_S8_UINT` | `R24_UNORM_X8_TYPELESS` | `X24_TYPELESS_G8_UINT` |
| `R32G8X24_TYPELESS` | `D32_FLOAT_S8X24_UINT` | `R32_FLOAT_X8X24_TYPELESS` | `X32_TYPELESS_G8X24_UINT` |
| `R16_TYPELESS` | `D16_UNORM` | `R16_UNORM` | （ステンシルなし） |

## 読み取り専用の DSV

深度テストはしつつ <strong>同じ深度を SRV でも読みたい</strong>（ソフト パーティクル、半透明）ときは <strong>読み取り専用の DSV</strong> を作ります。

```cpp
dsv_desc.Flags = D3D11_DSV_READ_ONLY_DEPTH;                 // 深度は、書き込めない（テストだけ）
device->CreateDepthStencilView(depth_texture.Get(), &dsv_desc, &readonly_dsv);
```

通常の DSV を束ねたまま SRV で読むと束縛の衝突になりますが読み取り専用の DSV なら、同じ深度を同時に SRV として、読めます。

## クリア

```cpp
context->ClearDepthStencilView(dsv.Get(),
                               D3D11_CLEAR_DEPTH | D3D11_CLEAR_STENCIL,
                               1.0f,       // 深度の初期値: 最も遠い（reverse-Z なら 0.0f）
                               0);         // ステンシルの初期値
```

毎フレーム、必ずクリアします。クリアしないと前のフレームの深度が残り新しい描画がはじかれます。

## パイプラインにつなぐ

```cpp
context->OMSetRenderTargets(1, rtv.GetAddressOf(), dsv.Get());
```

DSV を渡さない（`nullptr`）と深度テストも深度の書き込みも行われません（ポスト プロセスなど）。深度テストの設定（比較関数、書き込みの有無）は[Depth-Stencil State](depth-stencil-state.md) です。

## 深度の精度と near・far

深度は距離に対して非線形です（近くに精度が、集中する）。`near` を小さくしすぎると遠くの精度が足りず <strong>Z ファイティング</strong>（同じ位置の面が、ちらつく）が出ます。

| 対策 | 内容 |
| --- | --- |
| `near` を大きく | 0.01 → 0.1 で精度が、10 倍 |
| `far` を小さく | 必要な範囲に絞る |
| `D32_FLOAT` | 24 ビットの固定小数点より精度が、よい |
| reverse-Z | `D32_FLOAT` と組み合わせて、遠くの精度が大幅に上がる |

## よくあるミス

??? failure "物が前後、逆に見える（奥の物が手前に）"
    深度バッファを `OMSetRenderTargets` に渡していない。または、深度テストを無効にしている（`DepthEnable = FALSE`）。

??? failure "物が、半分だけ消えるまたは画面が真っ黒"
    深度をクリアしていないまたは、クリア値が 0（全部、近い扱い）。`1.0` でクリア。

??? failure "`CreateShaderResourceView` が深度で、失敗する"
    `D32_FLOAT` で作っている。`R32_TYPELESS` で作り DSV と SRV で、型を分ける。

??? failure "`OMSetRenderTargets` が、失敗する（警告）"
    深度バッファの大きさが、レンダー ターゲットと違う。

??? failure "面が、ちらつく（Z ファイティング）"
    `near` が小さすぎる。`D32_FLOAT` と reverse-Z にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 深度バッファ ＝ 各ピクセルの最も近い面の距離。近い面が勝つ
    - [x] 作成は `D32_FLOAT` か `D24_UNORM_S8_UINT`。読むなら `R32_TYPELESS`
    - [x] 毎フレーム `ClearDepthStencilView`（1.0）
    - [x] `OMSetRenderTargets` の第 3 引数に DSV
    - [x] 深度を読みつつテストするには読み取り専用の DSV
    - [x] 精度は `near` を大きく `D32_FLOAT`、reverse-Z

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Depth-Stencil State](depth-stencil-state.md)
- [Shader Resource View (SRV)](shader-resource-view.md)
- [Formats and Typeless](../concepts/formats.md)
- [Projection](../../3d/projection.md)
- [Microsoft Learn: ID3D11Device::CreateDepthStencilView](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createdepthstencilview)
