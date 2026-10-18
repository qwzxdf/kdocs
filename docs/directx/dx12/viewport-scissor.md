---
title: Viewport and Scissor
tags:
  - DirectX
---

# Viewport and Scissor

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>ビューポート</strong>は、クリップ空間（−1〜1）を、レンダー ターゲットの、どの範囲（ピクセル）に、描くかを、決める、設定です。<strong>シザー矩形</strong>は、その範囲の中で、さらに、描く範囲を、四角形で、<strong>切り抜きます</strong>。D3D12 では、この 2 つを、<strong>コマンド リストごとに、必ず、設定</strong>する必要が、あり、特に、シザー矩形は、<strong>常に、有効</strong>で、設定し忘れると、何も、描かれません。

!!! tip "ポイント"
    - ビューポートと、シザー矩形は、<strong>`Reset` のたびに、設定し直す</strong>（コマンド リストの、状態が、初期化されるため）。
    - シザー矩形は、常に、有効。未設定だと、描画範囲が、0 で、何も、出ない。
    - 通常は、どちらも、レンダー ターゲット全体（0, 0, 幅, 高さ）。
    - 縮小した、レンダー ターゲット（ブルームなど）に、描くときは、同じ大きさに、変える。
    - ビューポートは `float`、シザー矩形は、整数（`D3D12_RECT`: left, top, right, bottom）。

## 設定する

```cpp
D3D12_VIEWPORT viewport = {};
viewport.TopLeftX = 0.0f;
viewport.TopLeftY = 0.0f;
viewport.Width = static_cast<float>(width);
viewport.Height = static_cast<float>(height);
viewport.MinDepth = 0.0f;
viewport.MaxDepth = 1.0f;

D3D12_RECT scissor = {0, 0, static_cast<LONG>(width), static_cast<LONG>(height)};   // left, top, right, bottom

command_list->RSSetViewports(1, &viewport);
command_list->RSSetScissorRects(1, &scissor);
```

| 構造体 | メンバー | 内容 |
| --- | --- | --- |
| `D3D12_VIEWPORT` | `TopLeftX`・`TopLeftY` | 描く範囲の、左上（ピクセル）。`float` |
| | `Width`・`Height` | 描く範囲の、大きさ（ピクセル）。`float` |
| | `MinDepth`・`MaxDepth` | 深度の範囲（通常 0 と 1） |
| `D3D12_RECT` | `left`・`top`・`right`・`bottom` | 切り抜く範囲（ピクセル）。<strong>右・下は、含まない</strong> |

`D3D12_RECT` は、`right`・`bottom` が、<strong>範囲の、外側</strong>（幅 ＝ `right − left`）です。レンダー ターゲット全体は、`{0, 0, width, height}` です。

## ビューポートの、変換

クリップ空間の、座標（x、y が、−1〜1）は、ビューポートで、ピクセル座標に、変わります。

```text
ピクセル x = (クリップ x + 1) / 2 × Width + TopLeftX
ピクセル y = (1 − クリップ y) / 2 × Height + TopLeftY      ← y は、上下が、反転（クリップは y 上向き、ピクセルは y 下向き）
```

深度は、クリップ空間の z（0〜1）が、`MinDepth`〜`MaxDepth` に、写されます（スカイボックスを、`MinDepth = MaxDepth = 1.0` で、描くと、深度が、常に、最も遠くになる）。

## シザー矩形：常に、有効

D3D12 では、シザー矩形が、<strong>常に、有効</strong>です。

| 状況 | 結果 |
| --- | --- |
| 設定していない | 描画範囲が、0（何も、描かれない） |
| ビューポートより、小さい | その範囲だけに、描かれる（切り抜き） |
| ビューポートと、同じ | 全体が、描かれる |

「切り抜きを、使わない」場合も、<strong>ビューポートと、同じ範囲を、設定</strong>します。

## 縮小した、レンダー ターゲットに、描く

縮小テクスチャ（ブルームの各段、半解像度の AO）に、描くときは、ビューポートも、シザー矩形も、その、大きさに、合わせます。

```cpp
// 半分の大きさのレンダー ターゲットに、描く。
D3D12_VIEWPORT half_viewport = {0.0f, 0.0f, float(width / 2), float(height / 2), 0.0f, 1.0f};
D3D12_RECT half_scissor = {0, 0, LONG(width / 2), LONG(height / 2)};
command_list->RSSetViewports(1, &half_viewport);
command_list->RSSetScissorRects(1, &half_scissor);
command_list->OMSetRenderTargets(1, &half_rtv, FALSE, nullptr);
command_list->DrawInstanced(3, 1, 0, 0);                        // フルスクリーン三角形
```

ビューポートが、元の、大きさのままだと、小さな、テクスチャの、左上に、画面の一部しか、描かれません。

## 複数のビューポート

`RSSetViewports` は、最大 16 個の、ビューポートを、設定できます（ジオメトリ シェーダーが、`SV_ViewportArrayIndex` で、選ぶ）。キューブマップの、6 面を、1 回で、描くなどに、使えますが、まれです。

```cpp
D3D12_VIEWPORT viewports[2] = {left_half, right_half};
D3D12_RECT scissors[2] = {left_rect, right_rect};              // ビューポートと、同じ数のシザー矩形が、要る
command_list->RSSetViewports(2, viewports);
command_list->RSSetScissorRects(2, scissors);
```

## 切り抜きの、使いみち

シザー矩形は、ビューポート全体でなく、一部だけを、描く、用途に、使えます。

| 用途 | 内容 |
| --- | --- |
| UI の、スクロール領域 | はみ出した、内容を、切り抜く |
| ライトの、影響範囲 | ライトの、バウンディング ボックスを、画面に、投影して、その範囲だけ、ライティング |
| 部分更新 | 画面の、一部だけ、再描画 |

## リサイズ時

画面の大きさが、変わったら、ビューポートと、シザー矩形も、新しい大きさに、更新します。

```cpp
void OnResize(UINT width, UINT height) {
  viewport_ = {0.0f, 0.0f, float(width), float(height), 0.0f, 1.0f};
  scissor_ = {0, 0, LONG(width), LONG(height)};
  // バック バッファ、深度、G バッファの作り直し（swap-chain.md）
}
```

## よくあるミス

??? failure "何も、描かれない（クリアの色のまま）"
    シザー矩形を、設定していない。D3D12 は、シザーが、常に有効で、未設定だと、範囲が 0。ビューポートも、設定したか、確認する。

??? failure "`Reset` の後に、描いたら、何も出ない"
    `Reset` で、ビューポート・シザー矩形が、初期化されている。毎フレーム、設定し直す。

??? failure "縮小した、レンダー ターゲットの、左上にしか、描かれない"
    ビューポートが、元の大きさのまま。レンダー ターゲットを、切り替えるたびに、合わせる。

??? failure "画面の、右端・下端が、1 画素、欠ける"
    シザー矩形の `right`・`bottom` が、`width − 1`、`height − 1`。`D3D12_RECT` は、右・下を、含まないので、`width`、`height` を、指定する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ビューポート ＝ クリップ空間を、画面のどこに描くか。シザー矩形 ＝ その中の、切り抜き
    - [x] D3D12 は、シザー矩形が、常に、有効。未設定だと、何も、出ない
    - [x] `Reset` のたびに、両方、設定し直す
    - [x] 通常は、レンダー ターゲット全体。縮小時は、同じ大きさに
    - [x] `D3D12_RECT` の `right`・`bottom` は、範囲の、外側

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Drawing a Triangle](triangle.md)
- [Command List](command-list.md)
- [Viewport](../dx11/viewport.md)
- [Microsoft Learn: RSSetViewports](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nf-d3d12-id3d12graphicscommandlist-rssetviewports)
