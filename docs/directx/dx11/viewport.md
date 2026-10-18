---
title: Viewport
tags:
  - DirectX
---

# Viewport

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>ビューポート</strong>は、クリップ空間（−1〜1 の正規化された座標）を、<strong>レンダー ターゲットの、どの範囲（ピクセル）に、描くか</strong>を、決める、設定です。設定し忘れると、大きさが、0 のままで、何も、描かれません。D3D11 は、ビューポートの、初期値を、持ちません。

!!! tip "ポイント"
    - ビューポートは、`RSSetViewports` で、毎回、設定する。初期値は、無い（大きさ 0）。
    - 通常は、レンダー ターゲットの、全体（0, 0, 幅, 高さ）。
    - 深度の範囲 `MinDepth`、`MaxDepth` は、通常 0 と 1。
    - 縮小した、レンダー ターゲット（ブルームなど）に、描くときは、<strong>ビューポートも、同じ大きさに、変える</strong>。
    - 切り抜き（描く範囲を、さらに、制限）は、シザー矩形（`RSSetScissorRects`）。

## 設定する

```cpp
D3D11_VIEWPORT viewport = {};
viewport.TopLeftX = 0.0f;
viewport.TopLeftY = 0.0f;
viewport.Width = static_cast<float>(width);
viewport.Height = static_cast<float>(height);
viewport.MinDepth = 0.0f;
viewport.MaxDepth = 1.0f;
context->RSSetViewports(1, &viewport);
```

| メンバー | 内容 |
| --- | --- |
| `TopLeftX`・`TopLeftY` | 描く範囲の、左上（ピクセル）。画面の左上が (0, 0) |
| `Width`・`Height` | 描く範囲の、大きさ（ピクセル）。`float` なので、キャストが、必要 |
| `MinDepth`・`MaxDepth` | クリップ空間の、深度（0〜1）が、深度バッファの、どの値に、写るか |

クリップ空間の x、y は、−1〜1 で、ビューポートの変換で、`TopLeftX` から、`TopLeftX + Width`（x）、`TopLeftY` から、`TopLeftY + Height`（y）の、ピクセル座標に、変わります。<strong>y は、上下が、反転します</strong>（クリップ空間は、y が上向き、ピクセル座標は、y が下向き）。

## 深度の範囲

D3D11 の、クリップ空間の、z は、0〜1（OpenGL の −1〜1 とは、違う）で、ビューポートの、`MinDepth`、`MaxDepth` で、深度バッファの、値に、写ります。

| 設定 | 使いどころ |
| --- | --- |
| `0.0`〜`1.0` | 通常 |
| `0.0`〜`0.0`（`MinDepth = MaxDepth = 0`） | 全部を、最も近い深度に、描く（スカイボックスを、最も遠くに描くのは、逆の `1.0`〜`1.0`） |
| 逆（`1.0`〜`0.0`） | reverse-Z（深度を、反転して、精度を、上げる）の、別の実現方法。射影行列で、行う方が、一般的 |

スカイボックスを、`MinDepth = MaxDepth = 1.0` で、描くと、深度が、常に最も遠く（1.0）になり、ほかの物に、隠れます。

## 縮小した、レンダー ターゲットに、描く

縮小した、テクスチャ（ブルームの、各段、半解像度の AO）に、描くときは、ビューポートも、その、大きさに、合わせます。

```cpp
// 半分の大きさの、レンダー ターゲットに、描く。
context->OMSetRenderTargets(1, half_rtv.GetAddressOf(), nullptr);
D3D11_VIEWPORT half = {0.0f, 0.0f, static_cast<float>(width / 2), static_cast<float>(height / 2), 0.0f, 1.0f};
context->RSSetViewports(1, &half);
DrawFullscreenTriangle();
```

ビューポートが、元の大きさのままだと、小さな、テクスチャの、左上に、画面の、一部しか、描かれず、残りは、はみ出して、捨てられます。

## 複数のビューポート

ジオメトリ シェーダーで、`SV_ViewportArrayIndex` を、出力すると、1 回の描画で、複数のビューポートに、振り分けられます（最大 16 個）。キューブマップの、6 面を、1 回で、描くなどに、使えますが、普通は、使いません。

```cpp
D3D11_VIEWPORT viewports[2] = {left_half, right_half};
context->RSSetViewports(2, viewports);
```

## シザー矩形

ビューポートの範囲の中で、さらに、描く範囲を、<strong>四角形で、切り抜く</strong>のが、シザー矩形です。有効にするには、ラスタライザー ステートの `ScissorEnable = TRUE` が、必要です（[Rasterizer State](rasterizer-state.md)）。

```cpp
D3D11_RECT scissor = {100, 100, 500, 400};                 // left, top, right, bottom（ピクセル）
context->RSSetScissorRects(1, &scissor);
```

UI の、はみ出しを、切る（スクロール領域など）ときに、使います。ビューポートは、座標変換を、変え、シザー矩形は、変換を、変えず、切り抜くだけです。

## よくあるミス

??? failure "何も、描かれない（画面が、クリアの色のまま）"
    `RSSetViewports` を、呼んでいない。D3D11 は、ビューポートの、初期値を、持たない。デバッグ レイヤーも、警告を、出さないことが、ある。

??? failure "縮小した、テクスチャの、左上にしか、描かれない"
    ビューポートが、元の画面の、大きさのまま。レンダー ターゲットを、切り替えるたびに、ビューポートも、合わせる。

??? failure "画像が、上下、逆さまに、なる"
    uv の y と、クリップ空間の y が、反転している。フルスクリーン三角形で、`uv * float2(2, −2) + float2(−1, 1)` と、変換する（[D3D11 Pass Recipes](pass-recipes.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ビューポート ＝ クリップ空間を、画面のどこに描くか
    - [x] 初期値が、無い。`RSSetViewports` を、毎回、設定する
    - [x] 通常は、レンダー ターゲット全体。縮小時は、同じ大きさに
    - [x] 深度の範囲は、通常 0〜1
    - [x] 切り抜きは、シザー矩形

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Clear and Present](clear-present.md)
- [Rasterizer State](rasterizer-state.md)
- [D3D11 Pass Recipes](pass-recipes.md)
- [Microsoft Learn: ID3D11DeviceContext::RSSetViewports](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11devicecontext-rssetviewports)
