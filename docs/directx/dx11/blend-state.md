---
title: Blend State
tags:
  - DirectX
---

# Blend State

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>ブレンド ステート</strong>は、ピクセル シェーダーが、出した色を、<strong>レンダー ターゲットの、すでにある色と、どう混ぜて、書くか</strong>を、決める、設定です。何も、設定しないと、新しい色が、古い色を、上書きします。半透明（ガラス、煙）、光の加算（炎、魔法）、ブルームの足し込み、マスクは、ブレンドで、実現します。

!!! tip "ポイント"
    - ブレンド ＝ 「新しい色（ソース）」と「今ある色（デスト）」の、混ぜ方。式は、`結果 = ソース × 係数 S  演算  デスト × 係数 D`。
    - 通常の半透明は、`SRC_ALPHA` と `INV_SRC_ALPHA`。光の加算は、`ONE` と `ONE`。
    - 作成は `CreateBlendState`、つなぐのは `OMSetBlendState`。
    - 8 枚のレンダー ターゲットに、別々のブレンドを、使うには、`IndependentBlendEnable = TRUE`。
    - 半透明は、<strong>奥から手前の順</strong>に、描かないと、混ざり方が、おかしくなる。

## ブレンドの式

```text
RGB の結果   = (ソース RGB × SrcBlend)  BlendOp  (デスト RGB × DestBlend)
アルファの結果 = (ソース A   × SrcBlendAlpha) BlendOpAlpha (デスト A × DestBlendAlpha)
```

ソースは、ピクセル シェーダーの出力、デストは、レンダー ターゲットに、すでに書かれている色です。

## 通常の、アルファ ブレンド

```cpp
D3D11_BLEND_DESC desc = {};
desc.AlphaToCoverageEnable = FALSE;
desc.IndependentBlendEnable = FALSE;                        // 全レンダー ターゲットで、RenderTarget[0] を使う

D3D11_RENDER_TARGET_BLEND_DESC& rt = desc.RenderTarget[0];
rt.BlendEnable = TRUE;
rt.SrcBlend = D3D11_BLEND_SRC_ALPHA;                        // ソース × ソースのアルファ
rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;                   // デスト × (1 − ソースのアルファ)
rt.BlendOp = D3D11_BLEND_OP_ADD;                            // 足す
rt.SrcBlendAlpha = D3D11_BLEND_ONE;
rt.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
rt.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;    // RGBA を、全部、書く

Microsoft::WRL::ComPtr<ID3D11BlendState> state;
device->CreateBlendState(&desc, &state);

const float blend_factor[4] = {0, 0, 0, 0};
context->OMSetBlendState(state.Get(), blend_factor, 0xFFFFFFFF);   // 第 3 引数: サンプル マスク（通常は、全ビット 1）
```

`SRC_ALPHA` と `INV_SRC_ALPHA` の組み合わせは、「ソースの、アルファ分だけ、新しい色、残りは、古い色」の、混ぜ方で、`結果 = ソース × α + デスト × (1 − α)` です。アルファ 0.3 なら、新しい色が 30%、背景が 70% です。

| メンバー | 内容 |
| --- | --- |
| `BlendEnable` | ブレンドを、有効にするか |
| `SrcBlend`・`DestBlend` | RGB の、ソースと、デストの、係数 |
| `BlendOp` | `ADD`、`SUBTRACT`、`REV_SUBTRACT`、`MIN`、`MAX` |
| `SrcBlendAlpha`・`DestBlendAlpha`・`BlendOpAlpha` | アルファ チャンネル用（RGB と、別に、指定できる） |
| `RenderTargetWriteMask` | 書く、チャンネル（`RED`、`GREEN`、`BLUE`、`ALPHA`、`ALL`） |

## ブレンド係数

| `D3D11_BLEND_*` | 係数 |
| --- | --- |
| `ZERO` | 0 |
| `ONE` | 1 |
| `SRC_COLOR`・`INV_SRC_COLOR` | ソースの色、(1 − ソースの色) |
| `SRC_ALPHA`・`INV_SRC_ALPHA` | ソースのアルファ、(1 − ソースのアルファ) |
| `DEST_COLOR`・`INV_DEST_COLOR` | デストの色、(1 − デストの色) |
| `DEST_ALPHA`・`INV_DEST_ALPHA` | デストのアルファ、(1 − デストのアルファ) |
| `BLEND_FACTOR`・`INV_BLEND_FACTOR` | `OMSetBlendState` で渡した、定数色 |
| `SRC1_COLOR`・`SRC1_ALPHA` | デュアル ソース ブレンド（ピクセル シェーダーが、2 つの色を出力） |

## よく使う、ブレンド

| 目的 | `SrcBlend` | `DestBlend` | `BlendOp` | 結果 |
| --- | --- | --- | --- | --- |
| 上書き（ブレンドなし） | — | — | — | `ソース` |
| 通常の半透明 | `SRC_ALPHA` | `INV_SRC_ALPHA` | `ADD` | `ソース × α + デスト × (1 − α)` |
| プリマルチプライド アルファ | `ONE` | `INV_SRC_ALPHA` | `ADD` | `ソース + デスト × (1 − α)`（ソースに、α が、掛け済み） |
| 加算（光、炎、ブルーム） | `ONE` | `ONE` | `ADD` | `ソース + デスト` |
| アルファ付きの加算（パーティクルの光） | `SRC_ALPHA` | `ONE` | `ADD` | `ソース × α + デスト` |
| 乗算（影、暗くする） | `ZERO` | `SRC_COLOR` | `ADD` | `デスト × ソース` |
| 最大（ブルームの、重ね書き） | `ONE` | `ONE` | `MAX` | `max(ソース, デスト)` |

### プリマルチプライド アルファ

色に、アルファを、あらかじめ、掛けて、持つ、形式です（`rgb = rgb × a`）。通常の、アルファ ブレンドより、<strong>フィルタリングで、縁が、にじまず</strong>、加算と、通常の、半透明を、<strong>同じ、ブレンド</strong>（`ONE`、`INV_SRC_ALPHA`）で、扱えます。パーティクルの、現在の、標準です。

```hlsl
float4 color = texture.Sample(sampler, uv);
return float4(color.rgb * color.a, color.a);                // アルファを、色に、掛けてから、返す
```

## 描く、順序

通常の、アルファ ブレンドは、<strong>順序に、依存する</strong>演算で、奥の物を、先に、描かないと、結果が、変わります。

| 種類 | 順序 |
| --- | --- |
| 不透明 | 順序は、自由（深度テストが、解決する）。手前から、描くと、オーバードローが、減る |
| 半透明（通常のアルファ） | <strong>奥から、手前</strong>の、順（ソートが、必要） |
| 加算（`ONE`、`ONE`） | 順序に、依存しない（足し算は、交換できる）。ソート不要 |

順序の問題を、避ける方法は、[OIT](../../graphics/translucency/oit/index.md) です。

## 複数の、レンダー ターゲットに、別々のブレンド

```cpp
desc.IndependentBlendEnable = TRUE;                         // RenderTarget[0]〜[7] を、それぞれ指定する
desc.RenderTarget[0].BlendEnable = TRUE;                    // ターゲット 0: 加算
desc.RenderTarget[0].SrcBlend = D3D11_BLEND_ONE;
desc.RenderTarget[0].DestBlend = D3D11_BLEND_ONE;
desc.RenderTarget[1].BlendEnable = TRUE;                    // ターゲット 1: 乗算
desc.RenderTarget[1].SrcBlend = D3D11_BLEND_ZERO;
desc.RenderTarget[1].DestBlend = D3D11_BLEND_INV_SRC_COLOR;
```

[Weighted Blended OIT](../../graphics/translucency/oit/wboit.md) のように、1 回の描画で、2 枚の、ターゲットに、別の混ぜ方で、書くときに、使います。

## RenderTargetWriteMask

```cpp
rt.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_RED | D3D11_COLOR_WRITE_ENABLE_GREEN | D3D11_COLOR_WRITE_ENABLE_BLUE;   // アルファは、書かない
rt.RenderTargetWriteMask = 0;                               // 何も、書かない（深度だけ描く、ステンシルだけ書く）
```

深度だけを、書きたい（事前深度、シャドウ）ときは、ピクセル シェーダーを、`nullptr` にして、書き込みマスクを、0 にします。

## アルファ トゥ カバレッジ

```cpp
desc.AlphaToCoverageEnable = TRUE;                          // MSAA 時に、アルファを、サブサンプルの、カバレッジに変える
```

葉や、フェンスの、アルファ テストを、MSAA で、なめらかにします（[Alpha to Coverage](../../graphics/translucency/alpha-test/alpha-to-coverage.md)）。

## よくあるミス

??? failure "半透明の物の、前後関係が、おかしい"
    奥から、手前の順に、描いていない。または、深度の書き込みを、有効のままにしている（[Depth-Stencil State](depth-stencil-state.md)）。

??? failure "パーティクルの縁に、暗い（白い）縁取りが、出る"
    通常のアルファ ブレンドで、アルファ 0 の、ピクセルの色（黒や白）が、フィルタリングで、にじむ。プリマルチプライド アルファに、する。

??? failure "加算した色が、まぶしすぎる（白飛び）"
    HDR のレンダー ターゲットでは、1 を、超えて、足せる。LDR（`R8G8B8A8_UNORM`）では、1 で、頭打ち。トーン マッピングを、見直す。

??? failure "ブレンドを、設定したのに、効かない"
    `BlendEnable = FALSE` のまま、または、`OMSetBlendState` を、呼んでいない。`IndependentBlendEnable = FALSE` のとき、`RenderTarget[0]` が、全ターゲットに、適用される。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ブレンド ＝ 新しい色と、今ある色の、混ぜ方
    - [x] 通常の半透明 `SRC_ALPHA`・`INV_SRC_ALPHA`、加算 `ONE`・`ONE`
    - [x] パーティクルは、プリマルチプライド アルファ（`ONE`・`INV_SRC_ALPHA`）が標準
    - [x] 半透明（通常）は、奥から手前に描く。加算は、順序に依存しない
    - [x] 複数ターゲットに、別のブレンドは、`IndependentBlendEnable`
    - [x] 作成は `CreateBlendState`、束縛は `OMSetBlendState`

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Depth-Stencil State](depth-stencil-state.md)
- [Multiple Render Targets](mrt.md)
- [OIT](../../graphics/translucency/oit/index.md)
- [Microsoft Learn: ID3D11Device::CreateBlendState](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createblendstate)
