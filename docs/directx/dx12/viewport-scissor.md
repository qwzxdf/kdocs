---
title: Viewport and Scissor
tags:
  - DirectX
---

# Viewport and Scissor

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>ビューポート</strong>はクリップ空間（−1〜1）を、レンダー ターゲットのどの範囲（ピクセル）に、描くかを決める設定です。<strong>シザー矩形</strong>はその範囲の中でさらに、描く範囲を四角形で <strong>切り抜きます</strong>。D3D12 ではこの 2 つを、<strong>コマンド リストごとに必ず、設定</strong>する必要があり特にシザー矩形は <strong>常に、有効</strong>で設定し忘れると何も描かれません。

!!! tip "ポイント"
    - ビューポートとシザー矩形は、<strong>`Reset` のたびに設定し直す</strong>（コマンド リストの状態が、初期化されるため）。
    - シザー矩形は常に有効。未設定だと描画範囲が 0 で何も、出ない。
    - 通常はどちらもレンダー ターゲット全体（0, 0, 幅, 高さ）。
    - 縮小したレンダー ターゲット（ブルームなど）に、描くときは同じ大きさに変える。
    - ビューポートは `float`、シザー矩形は整数（`D3D12_RECT`: left, top, right, bottom）。

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
| `D3D12_RECT` | `left`・`top`・`right`・`bottom` | 切り抜く範囲（ピクセル）。<strong>右・下は含まない</strong> |

`D3D12_RECT` は `right`・`bottom` が <strong>範囲の外側</strong>（幅 ＝ `right − left`）です。レンダー ターゲット全体は `{0, 0, width, height}` です。

## ビューポートの変換

クリップ空間の座標（x、y が−1〜1）はビューポートで、ピクセル座標に変わります。

```text
ピクセル x = (クリップ x + 1) / 2 × Width + TopLeftX
ピクセル y = (1 − クリップ y) / 2 × Height + TopLeftY      ← y は、上下が、反転（クリップは y 上向き、ピクセルは y 下向き）
```

深度はクリップ空間の z（0〜1）が、`MinDepth`〜`MaxDepth` に写されます（スカイボックスを `MinDepth = MaxDepth = 1.0` で描くと深度が常に、最も遠くになる）。

## シザー矩形：常に有効

D3D12 ではシザー矩形が <strong>常に、有効</strong>です。

| 状況 | 結果 |
| --- | --- |
| 設定していない | 描画範囲が、0（何も描かれない） |
| ビューポートより小さい | その範囲だけに、描かれる（切り抜き） |
| ビューポートと同じ | 全体が、描かれる |

「切り抜きを使わない」場合も、<strong>ビューポートと同じ範囲を設定</strong>します。

## 縮小したレンダー ターゲットに描く

縮小テクスチャ（ブルームの各段、半解像度の AO）に描くときは、ビューポートもシザー矩形もその、大きさに合わせます。

```cpp
// 半分の大きさのレンダー ターゲットに、描く。
D3D12_VIEWPORT half_viewport = {0.0f, 0.0f, float(width / 2), float(height / 2), 0.0f, 1.0f};
D3D12_RECT half_scissor = {0, 0, LONG(width / 2), LONG(height / 2)};
command_list->RSSetViewports(1, &half_viewport);
command_list->RSSetScissorRects(1, &half_scissor);
command_list->OMSetRenderTargets(1, &half_rtv, FALSE, nullptr);
command_list->DrawInstanced(3, 1, 0, 0);                        // フルスクリーン三角形
```

ビューポートが元の大きさのままだと小さな、テクスチャの左上に画面の一部しか、描かれません。

## 複数のビューポート

`RSSetViewports` は最大 16 個のビューポートを、設定できます（ジオメトリ シェーダーが `SV_ViewportArrayIndex` で、選ぶ）。キューブマップの 6 面を 1 回で、描くなどに使えますがまれです。

```cpp
D3D12_VIEWPORT viewports[2] = {left_half, right_half};
D3D12_RECT scissors[2] = {left_rect, right_rect};              // ビューポートと、同じ数のシザー矩形が、要る
command_list->RSSetViewports(2, viewports);
command_list->RSSetScissorRects(2, scissors);
```

## 切り抜きの使いみち

シザー矩形はビューポート全体でなく、一部だけを描く用途に使えます。

| 用途 | 内容 |
| --- | --- |
| UI のスクロール領域 | はみ出した内容を、切り抜く |
| ライトの影響範囲 | ライトの、バウンディング ボックスを画面に、投影してその範囲だけライティング |
| 部分更新 | 画面の一部だけ、再描画 |

## リサイズ時

画面の大きさが変わったらビューポートと、シザー矩形も新しい大きさに更新します。

```cpp
void OnResize(UINT width, UINT height) {
  viewport_ = {0.0f, 0.0f, float(width), float(height), 0.0f, 1.0f};
  scissor_ = {0, 0, LONG(width), LONG(height)};
  // バック バッファ、深度、G バッファの作り直し（swap-chain.md）
}
```

## よくあるミス

??? failure "何も、描かれない（クリアの色のまま）"
    シザー矩形を設定していない。D3D12 はシザーが常に有効で、未設定だと範囲が 0。ビューポートも設定したか確認する。

??? failure "`Reset` の後に、描いたら何も出ない"
    `Reset` でビューポート・シザー矩形が、初期化されている。毎フレーム、設定し直す。

??? failure "縮小した、レンダー ターゲットの左上にしか、描かれない"
    ビューポートが元の大きさのまま。レンダー ターゲットを切り替えるたびに、合わせる。

??? failure "画面の、右端・下端が 1 画素、欠ける"
    シザー矩形の `right`・`bottom` が `width − 1`、`height − 1`。`D3D12_RECT` は右・下を含まないので `width`、`height` を指定する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ビューポート ＝ クリップ空間を、画面のどこに描くか。シザー矩形 ＝ その中の切り抜き
    - [x] D3D12 は、シザー矩形が常に有効。未設定だと何も出ない
    - [x] `Reset` のたびに両方、設定し直す
    - [x] 通常はレンダー ターゲット全体。縮小時は同じ大きさに
    - [x] `D3D12_RECT` の `right`・`bottom` は範囲の外側

## 関連ページ

- [DirectX 12 Guide](index.md)
- [Drawing a Triangle](triangle.md)
- [Command List](command-list.md)
- [Viewport](../dx11/viewport.md)
- [Microsoft Learn: RSSetViewports](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nf-d3d12-id3d12graphicscommandlist-rssetviewports)
