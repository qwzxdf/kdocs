---
title: Rendering Depth
tags:
  - 描画
---

# Rendering Depth

<strong>光の行列ができたら、その視点から、シーンの深度だけを描きます</strong>。<strong>色は要らず、深度バッファだけ</strong>に書くので、非常に安いパスです。描くのは「影を落とす物」だけに絞るとさらに速くなります。このページでは、深度専用パスの設定・ピクセル シェーダーなし・カリングの向き・描く対象の絞り込みを説明します。

!!! tip "ポイント"
    - 深度だけを描く（カラー書き込みなし・ピクセル シェーダーなし）。
    - 影を落とさない物は描かない（カリング・フラグ）。
    - 前面カリングを使うとアクネが減ることがある（[Front-Face Culling](../bias/front-face-culling.md)）。
    - アルファ テストの物はピクセル シェーダーが要る（[Alpha-Tested Shadows](../special-cases/alpha-test-shadows.md)）。

## ② シャドウ マップを描く
<strong>深度だけ</strong>を描きます。<strong>ピクセルシェーダーは不要</strong>（アルファ テストする物を除く）で、非常に速い描画です。

```cpp
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = 2048;
desc.Height = 2048;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R32_TYPELESS;
desc.SampleDesc.Count = 1;
desc.BindFlags = D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &shadow_tex);

D3D11_DEPTH_STENCIL_VIEW_DESC dsv_desc = {};
dsv_desc.Format = DXGI_FORMAT_D32_FLOAT;
dsv_desc.ViewDimension = D3D11_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(shadow_tex, &dsv_desc, &shadow_dsv);

D3D11_SHADER_RESOURCE_VIEW_DESC srv_desc = {};
srv_desc.Format = DXGI_FORMAT_R32_FLOAT;
srv_desc.ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D;
srv_desc.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(shadow_tex, &srv_desc, &shadow_srv);
```

| 点 | 説明 |
| --- | --- |
| `R32_TYPELESS` | 深度として書き、シェーダーから読むため、型なしで作る |
| DSV は `D32_FLOAT`、SRV は `R32_FLOAT` | 同じ領域を、2 通りに見る |
| 解像度 | 1024〜4096。大きいほど細かい影・メモリと帯域を食う（[メモリ帯域幅](../../../rendering/bandwidth.md)） |
| フォーマット | 16 ビットで足りることも多い（精度を許容できれば、帯域が半分） |
| 描画する物 | 影を落とす物だけ。ライティングなしのシェーダー（頂点シェーダーのみ） |

## 深度テクスチャを、作る

シャドウ マップは、<strong>深度だけ</strong>を、保存する、テクスチャです。DirectX 11 では、<strong>同じテクスチャ</strong>を、深度ステンシル ビュー（DSV）として、書き込み、シェーダー リソース ビュー（SRV）として、読み取ります。そのため、テクスチャの形式を、TYPELESS（型なし）で作り、ビューごとに、形式を、指定します。

```cpp
// シャドウ マップ: 2048×2048、32 ビット浮動小数点の深度。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = 2048;
desc.Height = 2048;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R32_TYPELESS;                         // 型なし（ビューで、型を決める）
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &shadow_map_tex);
```

シャドウ マップを、2048×2048 の、32 ビット浮動小数点で、作ります。型なし（`TYPELESS`）にしておくと、書き込む、ビューと、読み込む、ビューで、別の型を、使えます。`BindFlags` に、深度ステンシルと、シェーダー リソースの、両方を、指定します。

```cpp
// 書き込み用（シャドウ パスで使う）
D3D11_DEPTH_STENCIL_VIEW_DESC dsv = {};
dsv.Format = DXGI_FORMAT_D32_FLOAT;
dsv.ViewDimension = D3D11_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(shadow_map_tex.Get(), &dsv, &shadow_dsv);
```

書き込み用の、ビュー（DSV）です。`D32_FLOAT` として、深度を、書きます。シャドウ パスでは、これを、出力に、束ねます。

```cpp
// 読み取り用（メイン パスで使う）
D3D11_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_R32_FLOAT;
srv.ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D;
srv.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(shadow_map_tex.Get(), &srv, &shadow_srv);
```

| 形式 | 精度 | メモリ（2048²） | 使いどころ |
| --- | --- | --- | --- |
| `D32_FLOAT` | 32 ビット浮動小数点 | 16 MB | 標準。精度が、高い |
| `D24_UNORM_S8_UINT` | 24 ビット固定小数点 + ステンシル | 16 MB | ステンシルが、必要なとき |
| `D16_UNORM` | 16 ビット | 8 MB | メモリを、節約したい。精度が、低く、バイアスが、大きくなる |

## シャドウ パスの、描画

光の視点で、<strong>カメラの代わりに、光の、ビュー・射影行列</strong>を、使って、<strong>影を、落とす物</strong>を、描きます。色は、書き込まないので、ピクセル シェーダーも、不要（アルファ テストする物を、除く）です。

```cpp
// ① 書き込み先を、シャドウ マップだけにする（レンダー ターゲットは、なし）。
context->OMSetRenderTargets(0, nullptr, shadow_dsv.Get());
context->ClearDepthStencilView(shadow_dsv.Get(), D3D11_CLEAR_DEPTH, 1.0f, 0);

// ② ビューポートを、シャドウ マップの大きさに。
D3D11_VIEWPORT vp = {0, 0, 2048, 2048, 0.0f, 1.0f};
context->RSSetViewports(1, &vp);

// ③ 頂点シェーダーだけ（ピクセル シェーダーは、なし）。
context->VSSetShader(shadow_vs.Get(), nullptr, 0);
context->PSSetShader(nullptr, nullptr, 0);                    // 深度だけなので、ピクセル シェーダーは、無し

// ④ 光の行列を、定数バッファに入れて、影を落とす物を、描く。
UpdateLightCB(light_view_proj);
DrawShadowCasters();
```

```hlsl
// シャドウ パスの、頂点シェーダー: 光の行列で、頂点を、変換するだけ。
cbuffer LightCB : register(b0) { float4x4 g_light_view_proj; };
cbuffer ObjectCB : register(b1) { float4x4 g_world; };

float4 main(float3 position : POSITION) : SV_Position {
  return mul(mul(float4(position, 1.0), g_world), g_light_view_proj);
}
```

<strong>ピクセル シェーダーを、無し</strong>にすると、GPU は、<strong>深度書き込みだけ</strong>を、高速に、行います（多くの GPU が、通常の、2 倍以上の、速さ）。

## 描く物を、絞る

シャドウ パスは、<strong>物を、もう一度、描く</strong>ので、<strong>描画コストが、増えます</strong>。減らす工夫です。

| 工夫 | 内容 |
| --- | --- |
| 影を落とさない物を、除く | 小さな物、遠くの物、影が、目立たない物を、シャドウ パスから、外す |
| 光の視錐台で、カリング | 光の、視錐台の外にある物は、描かない（カメラの視錐台とは、別） |
| LOD | シャドウ パスでは、粗い LOD を、使う（影は、細部が、見えない） |
| 静的な物の、キャッシュ | 動かない物の、シャドウ マップを、保存し、動く物だけを、毎フレーム、描き足す（[Shadows for Many Lights](../local-lights/many-lights.md)） |
| 更新の、間引き | 遠くのカスケードは、数フレームに、1 回だけ、更新する（[CSM](../cascaded.md)） |

## 表裏の、カリング

シャドウ パスで、<strong>どの面を、描くか</strong>（表面か、裏面か）が、<strong>バイアスの問題</strong>に、関わります。

| 描く面 | 内容 |
| --- | --- |
| 表面（通常） | 光に、向いた面の、深度が、保存される。自己影が、出やすい（地面の、表面と、同じ面を、比べるため） |
| 裏面（表面を、カリング） | 光から、遠い側の面の、深度が、保存される。表面との間に、厚み（物の、厚さ）が、できて、バイアスが、不要に近い。ただし、薄い物（板）では、影が、欠ける（[Front-Face Culling](../bias/front-face-culling.md)） |

```cpp
// 裏面を描く: 表面をカリング。
D3D11_RASTERIZER_DESC rs = {};
rs.FillMode = D3D11_FILL_SOLID;
rs.CullMode = D3D11_CULL_FRONT;                  // 光に向いた面を、描かない（このサイトでは、反時計回りが表）
rs.FrontCounterClockwise = TRUE;
rs.DepthClipEnable = TRUE;
```

## 射影の、種類と、深度の、精度

| 光 | 射影 | 深度の分布 |
| --- | --- | --- |
| 平行光源（正射影） | 正射影 | 深度は、線形（近くから、遠くまで、一定の精度）。バイアスが、扱いやすい |
| スポット、点光源（透視） | 透視投影 | 深度は、非線形（近くで、精度が高く、遠くで、粗い）。バイアスを、距離で、変える必要 |

透視投影の、シャドウ マップでは、<strong>ニア面を、できるだけ、遠く</strong>に置いて、深度の、精度を、保ちます（ニア面が、近すぎると、遠くの、精度が、落ちる）。

## よくあるミス

??? failure "画面に映らない物だけを描いて、影が欠ける"
    <strong>光から見える物を描く</strong>。<strong>画面外の物も、影を落とす</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 光から見た深度だけを描く、軽いパス
    - [x] 対象を絞る。ピクセル シェーダー不要（アルファ テスト以外）

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces", SIGGRAPH 1978（シャドウ マップの原典）
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"（Direct3D 11 のドキュメント。バイアス、平行光源、PCF）
- Microsoft Learn, "D3D11_RASTERIZER_DESC"（`DepthBias`、`SlopeScaledDepthBias`、`DepthBiasClamp`）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）

## 関連ページ

- [Shadow Map Basics](index.md)
- [The Light Matrix](light-matrix.md)
- [Comparison Samplers](comparison-sampler.md)
