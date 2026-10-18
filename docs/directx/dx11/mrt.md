---
title: Multiple Render Targets
tags:
  - DirectX
---

# Multiple Render Targets

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>MRT</strong>（Multiple Render Targets、複数レンダー ターゲット）は、<strong>1 回の描画で、複数のテクスチャに、同時に書く</strong>機能です。ピクセル シェーダーが、複数の値（`SV_Target0`、`SV_Target1`…）を、返し、それぞれが、別のテクスチャに、書き込まれます。ディファード レンダリングの、G バッファ（アルベド、法線、粗さ、深度…を、同時に出力）の、土台です。

!!! tip "ポイント"
    - `OMSetRenderTargets` に、複数の RTV（最大 8 つ）を、渡す。ピクセル シェーダーは、`SV_Target0`〜`7` を、返す。
    - 全部の、ターゲットは、<strong>同じ大きさ</strong>（幅・高さ・サンプル数）。フォーマットは、別々でよい。
    - G バッファ、速度バッファ、WBOIT（累積と透過度）が、典型的な、使い方。
    - ブレンドは、`IndependentBlendEnable` で、ターゲットごとに、別々にできる。
    - 帯域を、食うので、ターゲットの、数と、フォーマットを、絞る。

## G バッファの、例

```cpp
// 3 枚のターゲット: アルベド、法線、材質（粗さ・金属度）。深度は、別の DSV。
struct GBuffer {
  Microsoft::WRL::ComPtr<ID3D11RenderTargetView> rtv[3];
  Microsoft::WRL::ComPtr<ID3D11ShaderResourceView> srv[3];
};

const DXGI_FORMAT formats[3] = {
    DXGI_FORMAT_R8G8B8A8_UNORM_SRGB,       // 0: アルベド（sRGB）
    DXGI_FORMAT_R10G10B10A2_UNORM,         // 1: 法線（精度が要る。xyz を 0〜1 に詰める）
    DXGI_FORMAT_R8G8B8A8_UNORM,            // 2: 粗さ・金属度・AO（リニア）
};

for (int i = 0; i < 3; ++i) {
  D3D11_TEXTURE2D_DESC desc = {};
  desc.Width = width;                                      // 全ターゲットで、同じ大きさ
  desc.Height = height;
  desc.MipLevels = desc.ArraySize = 1;
  desc.Format = formats[i];
  desc.SampleDesc.Count = 1;
  desc.Usage = D3D11_USAGE_DEFAULT;
  desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
  Microsoft::WRL::ComPtr<ID3D11Texture2D> texture;
  device->CreateTexture2D(&desc, nullptr, &texture);
  device->CreateRenderTargetView(texture.Get(), nullptr, &gbuffer.rtv[i]);
  device->CreateShaderResourceView(texture.Get(), nullptr, &gbuffer.srv[i]);
}
```

アルベドは `_SRGB`、法線やデータは、リニアの `_UNORM` にします。法線は、`R10G10B10A2_UNORM`（10 ビット精度）か、`R16G16_FLOAT`（八面体エンコード）で、持つと、バンディングが、減ります。

## 束ねる

```cpp
ID3D11RenderTargetView* targets[3] = {gbuffer.rtv[0].Get(), gbuffer.rtv[1].Get(), gbuffer.rtv[2].Get()};
context->OMSetRenderTargets(3, targets, depth_dsv.Get());

const float clear[4] = {0, 0, 0, 0};
for (auto& rtv : gbuffer.rtv) context->ClearRenderTargetView(rtv.Get(), clear);   // 各ターゲットを、クリア
context->ClearDepthStencilView(depth_dsv.Get(), D3D11_CLEAR_DEPTH, 1.0f, 0);
```

<strong>クリアは、ターゲットごと</strong>に、`ClearRenderTargetView` を、呼びます。

## ピクセル シェーダーから、複数を、出す

```hlsl
struct PSOutput {
  float4 albedo : SV_Target0;      // ターゲット 0
  float4 normal : SV_Target1;      // ターゲット 1
  float4 material : SV_Target2;    // ターゲット 2
};

PSOutput PSMain(VSOutput input) {
  PSOutput output;
  output.albedo = g_albedo.Sample(g_sampler, input.uv);
  output.normal = float4(normalize(input.normal) * 0.5 + 0.5, 0.0);     // −1〜1 を 0〜1 に詰める
  output.material = float4(roughness, metallic, ao, 0.0);
  return output;
}
```

`SV_Target` の、番号が、`OMSetRenderTargets` の、配列の、位置に、対応します。ピクセル シェーダーが、出力する、番号の、ターゲットが、束ねられていないと、その出力は、捨てられます。

## ライティングで、読む

```cpp
// G バッファを描き終わったら、書き込みの束縛を、外して、SRV として、読む。
context->OMSetRenderTargets(0, nullptr, nullptr);
ID3D11ShaderResourceView* srvs[] = {gbuffer.srv[0].Get(), gbuffer.srv[1].Get(), gbuffer.srv[2].Get(), depth_srv.Get()};
context->PSSetShaderResources(0, 4, srvs);
```

ライティングのパスは、フルスクリーン三角形で、各ピクセルの、G バッファを、`Load` で、読み、ライティングを、計算します（[D3D11 Pass Recipes](pass-recipes.md)）。

## 制約

| 制約 | 内容 |
| --- | --- |
| ターゲットの数 | 最大 8 |
| 大きさ | 全ターゲットで、同じ幅・高さ・サンプル数（配列の、要素数も、同じ） |
| フォーマット | ターゲットごとに、別でよい（ビット幅も、違ってよい） |
| 深度 | 1 つの DSV（全ターゲット共通） |
| ブレンド | `IndependentBlendEnable = TRUE` で、ターゲットごとに、別。`FALSE` なら、`RenderTarget[0]` の設定を、全部に、使う |

ターゲットごとに、ブレンドを変えるのは、[Blend State](blend-state.md) です。

## 帯域の、コスト

G バッファの、ターゲット数と、フォーマットは、<strong>メモリ帯域</strong>に、直結します。1080p で、`R8G8B8A8`（4 バイト）を 1 枚、描くと、約 8 MB、読み書きします。4 枚の、G バッファに、深度を、加えると、1 フレームで、数十 MB に、なります。

| 工夫 | 内容 |
| --- | --- |
| フォーマットを、小さく | 法線を、2 チャンネル（八面体）に、圧縮する |
| ターゲット数を、減らす | 材質を、1 枚に、まとめる（粗さ・金属度・AO を、1 枚に） |
| 深度から、位置を、復元 | ワールド位置の、ターゲットを、持たない（深度と、逆行列から、計算する） |

## MSAA の、ターゲット

MSAA で、描くときは、`SampleDesc.Count` を、2、4、8 にして、作り、描いた後、`ResolveSubresource` で、普通のテクスチャへ、まとめます。

```cpp
// MSAA のレンダー ターゲットに描いた後、バック バッファ（MSAA でない）へ、解決する。
context->ResolveSubresource(back_buffer.Get(), 0, msaa_texture.Get(), 0, DXGI_FORMAT_R8G8B8A8_UNORM);
```

ディファードと、MSAA は、相性が悪い（G バッファが、MSAA で、巨大に、なる）ので、TAA を、使うのが、一般的です（[TAA](../../graphics/postprocess/antialiasing/taa.md)）。

## よくあるミス

??? failure "`OMSetRenderTargets` が、失敗する（大きさの不一致）"
    ターゲットの、幅・高さ・サンプル数が、そろっていない。深度バッファも、同じ大きさに。

??? failure "G バッファの、1 枚が、全部 0（真っ黒）"
    その `SV_Target` の、番号に、対応する、RTV を、束ねていない。ピクセル シェーダーが、その出力を、書いていない（未初期化）。

??? failure "法線が、おかしい（暗い、方向が、逆）"
    `−1〜1` を、`0〜1` に、詰めるとき、`* 0.5 + 0.5` を、忘れる（負の値が、切れる）。読むときの、`* 2 − 1` を、忘れる。`_SRGB` のターゲットに、法線を、書いた。

??? failure "1 枚だけクリアされず、前のフレームの残りが、見える"
    `ClearRenderTargetView` を、1 枚ぶんしか、呼んでいない。全ターゲットを、クリアする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] MRT ＝ 1 回の描画で、複数のテクスチャに、同時に書く
    - [x] `OMSetRenderTargets(n, rtvs, dsv)`、シェーダーは `SV_Target0〜7`
    - [x] 全ターゲットが、同じ大きさ。フォーマットは、別でよい
    - [x] 色は `_SRGB`、データ（法線、材質）は、リニア
    - [x] 読むときは、書き込みの束縛を、外す
    - [x] 帯域に、直結。フォーマットと数を、絞る

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Render Target View (RTV)](render-target-view.md)
- [Blend State](blend-state.md)
- [D3D11 Pass Recipes](pass-recipes.md)
- [Forward and Deferred](../../rendering/forward-deferred.md)
- [Microsoft Learn: ID3D11DeviceContext::OMSetRenderTargets](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11devicecontext-omsetrendertargets)
