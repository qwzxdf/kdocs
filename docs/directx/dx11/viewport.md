---
title: Viewport
tags:
  - DirectX
---

# Viewport

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>ビューポート</strong>はクリップ空間（−1〜1 の正規化された座標）を <strong>レンダー ターゲットのどの範囲（ピクセル）に描くか</strong>を決める設定です。設定し忘れると大きさが 0 のままで何も、描かれません。D3D11 はビューポートの、初期値を持ちません。

!!! tip "ポイント"
    - ビューポートは `RSSetViewports` で毎回、設定する。初期値は無い（大きさ 0）。
    - 通常はレンダー ターゲットの、全体（0, 0, 幅, 高さ）。
    - 深度の範囲 `MinDepth`、`MaxDepth` は通常 0 と 1。
    - 縮小したレンダー ターゲット（ブルームなど）に描くときは <strong>ビューポートも同じ大きさに、変える</strong>。
    - 切り抜き（描く範囲をさらに、制限）はシザー矩形（`RSSetScissorRects`）。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

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
| `TopLeftX`・`TopLeftY` | 描く範囲の左上（ピクセル）。画面の左上が (0, 0) |
| `Width`・`Height` | 描く範囲の大きさ（ピクセル）。`float` なのでキャストが必要 |
| `MinDepth`・`MaxDepth` | クリップ空間の、深度（0〜1）が深度バッファの、どの値に写るか |

クリップ空間の x、y は−1〜1 でビューポートの変換で、`TopLeftX` から `TopLeftX + Width`（x）、`TopLeftY` から `TopLeftY + Height`（y）のピクセル座標に変わります。<strong>y は上下が反転します</strong>（クリップ空間は、y が上向きピクセル座標は y が下向き）。

## 深度の範囲

D3D11 のクリップ空間の z は、0〜1（OpenGL の −1〜1 とは、違う）でビューポートの `MinDepth`、`MaxDepth` で深度バッファの値に写ります。

| 設定 | 使いどころ |
| --- | --- |
| `0.0`〜`1.0` | 通常 |
| `0.0`〜`0.0`（`MinDepth = MaxDepth = 0`） | 全部を最も近い深度に描く（スカイボックスを最も遠くに描くのは逆の `1.0`〜`1.0`） |
| 逆（`1.0`〜`0.0`） | reverse-Z（深度を反転して精度を上げる）の別の実現方法。射影行列で行う方が一般的 |

スカイボックスを `MinDepth = MaxDepth = 1.0` で描くと深度が常に最も遠く（1.0）になり、ほかの物に隠れます。

## 縮小したレンダー ターゲットに描く

縮小したテクスチャ（ブルームの各段、半解像度の AO）に描くときは、ビューポートもその大きさに合わせます。

```cpp
// 半分の大きさの、レンダー ターゲットに描く。
context->OMSetRenderTargets(1, half_rtv.GetAddressOf(), nullptr);
D3D11_VIEWPORT half = {0.0f, 0.0f, static_cast<float>(width / 2), static_cast<float>(height / 2), 0.0f, 1.0f};
context->RSSetViewports(1, &half);
DrawFullscreenTriangle();
```

ビューポートが元の大きさのままだと小さな、テクスチャの左上に画面の一部しか、描かれず残りははみ出して捨てられます。

## 複数のビューポート

ジオメトリ シェーダーで `SV_ViewportArrayIndex` を出力すると 1 回の描画で複数のビューポートに振り分けられます（最大 16 個）。キューブマップの 6 面を 1 回で、描くなどに使えますが普通は使いません。

```cpp
D3D11_VIEWPORT viewports[2] = {left_half, right_half};
context->RSSetViewports(2, viewports);
```

## シザー矩形

ビューポートの範囲の中でさらに、描く範囲を <strong>四角形で切り抜く</strong>のが、シザー矩形です。有効にするにはラスタライザー ステートの `ScissorEnable = TRUE` が、必要です（[Rasterizer State](rasterizer-state.md)）。

```cpp
D3D11_RECT scissor = {100, 100, 500, 400};                 // left, top, right, bottom（ピクセル）
context->RSSetScissorRects(1, &scissor);
```

UI のはみ出しを切る（スクロール領域など）ときに、使います。ビューポートは座標変換を変え、シザー矩形は変換を変えず切り抜くだけです。

## よくあるミス

??? failure "何も、描かれない（画面がクリアの色のまま）"
    `RSSetViewports` を呼んでいない。D3D11 はビューポートの、初期値を持たない。デバッグ レイヤーも警告を出さないことがある。

??? failure "縮小した、テクスチャの左上にしか描かれない"
    ビューポートが元の画面の、大きさのまま。レンダー ターゲットを切り替えるたびに、ビューポートも合わせる。

??? failure "画像が上下、逆さまになる"
    uv の y とクリップ空間の y が、反転している。フルスクリーン三角形で `uv * float2(2, −2) + float2(−1, 1)` と、変換する（[D3D11 Pass Recipes](pass-recipes.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ビューポート ＝ クリップ空間を画面のどこに描くか
    - [x] 初期値が無い。`RSSetViewports` を毎回、設定する
    - [x] 通常はレンダー ターゲット全体。縮小時は同じ大きさに
    - [x] 深度の範囲は、通常 0〜1
    - [x] 切り抜きは、シザー矩形

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Clear and Present](clear-present.md)
- [Rasterizer State](rasterizer-state.md)
- [D3D11 Pass Recipes](pass-recipes.md)
- [Microsoft Learn: ID3D11DeviceContext::RSSetViewports](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11devicecontext-rssetviewports)
