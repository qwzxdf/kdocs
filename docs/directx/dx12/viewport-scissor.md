---
title: Viewport and Scissor
tags:
  - DirectX
---

# Viewport and Scissor

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

頂点シェーダーが出力する座標は画面のピクセルではなく、クリップ空間（x と y が −1 から 1）という正規化された座標です。これをレンダー ターゲットのどの範囲（ピクセル）に当てはめて描くかを決めるのが、<strong>ビューポート</strong>です。さらに、その範囲の中で四角形の外側を切り捨てる設定が <strong>シザー矩形</strong>です。

D3D12 ではこの 2 つをコマンド リストごとに必ず設定します。特にシザー矩形は**常に有効**で、設定し忘れると何も描かれません。D3D12 を始めたばかりの人がよくはまる所です。

!!! tip "ポイント"
    - ビューポートとシザー矩形は、`Reset` のたびに設定し直す。コマンド リストの状態は `Reset` で初期化される。
    - シザー矩形は常に有効。未設定だと描画範囲が 0 になり何も出ない。
    - ふつうはどちらもレンダー ターゲット全体（0、0、幅、高さ）にする。
    - 縮小したレンダー ターゲット（ブルームなど）に描くときは、同じ大きさに変える。
    - ビューポートは `float`、シザー矩形は整数（`D3D12_RECT`。left、top、right、bottom）。

!!! info "このページを読む前に"
    この 2 つはコマンド リストに記録する命令です。先に [Command List](command-list.md) を読むと「`Reset` で設定が消える」理由が分かります。メソッドの引数は [ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md#rssetviewports) にあります。

## 設定する

```cpp
D3D12_VIEWPORT viewport = {};
viewport.TopLeftX = 0.0f;
viewport.TopLeftY = 0.0f;
viewport.Width = static_cast<float>(width);
viewport.Height = static_cast<float>(height);
viewport.MinDepth = 0.0f;
viewport.MaxDepth = 1.0f;

D3D12_RECT scissor = {0, 0, static_cast<LONG>(width), static_cast<LONG>(height)};  // left, top, right, bottom

command_list->RSSetViewports(1, &viewport);
command_list->RSSetScissorRects(1, &scissor);
```

`D3D12_VIEWPORT` は描く範囲の左上（`TopLeftX`、`TopLeftY`）と大きさ（`Width`、`Height`）をピクセル単位の `float` で持ちます。`MinDepth` と `MaxDepth` は深度の範囲でふつうは 0 と 1 です。

`D3D12_RECT` は `left`、`top`、`right`、`bottom` を整数で持ちます。**`right` と `bottom` は範囲の外側**で、幅は `right − left` になります。レンダー ターゲット全体は `{0, 0, width, height}` です。`width - 1` と書くと右端と下端が 1 画素ずつ欠けます。

## ビューポートの変換

クリップ空間の座標はビューポートでピクセルの座標に変わります。

```text
ピクセル x = (クリップ x + 1) / 2 × Width + TopLeftX
ピクセル y = (1 − クリップ y) / 2 × Height + TopLeftY    ← 上下が反転する（クリップは y が上向き、ピクセルは y が下向き）
```

深度はクリップ空間の z（0 から 1）が `MinDepth` から `MaxDepth` の範囲へ写されます。スカイボックスを `MinDepth = MaxDepth = 1.0` で描くと深度がいつも最も遠くになるので、ほかの物の後ろに描けます。

## シザー矩形は常に有効

D3D12 のシザー矩形はいつも有効です。設定していないと描画範囲は 0 になり何も描かれません。ビューポートより小さい矩形を設定すると、その範囲だけに描かれます。ビューポートと同じ矩形なら全体が描かれます。

切り抜きを使いたくないときも**ビューポートと同じ範囲を設定**します。

## 縮小したレンダー ターゲットに描く

ブルームの各段や半解像度の AO のように縮小したテクスチャに描くときは、ビューポートとシザー矩形もその大きさに合わせます。

```cpp
// 半分の大きさのレンダー ターゲットに描く。
D3D12_VIEWPORT half_viewport = {0.0f, 0.0f, float(width / 2), float(height / 2), 0.0f, 1.0f};
D3D12_RECT half_scissor = {0, 0, LONG(width / 2), LONG(height / 2)};
command_list->RSSetViewports(1, &half_viewport);
command_list->RSSetScissorRects(1, &half_scissor);
command_list->OMSetRenderTargets(1, &half_rtv, FALSE, nullptr);
command_list->DrawInstanced(3, 1, 0, 0);  // フルスクリーン三角形
```

ビューポートが元の大きさのままだと小さなテクスチャの左上に画面の一部しか描かれません。

## 複数のビューポート

`RSSetViewports` は最大 16 個のビューポートを一度に設定できます。ジオメトリ シェーダーが `SV_ViewportArrayIndex` で選びます。キューブ マップの 6 面を 1 回で描く、などに使いますがまれです。シザー矩形もビューポートと同じ数が必要です。

```cpp
D3D12_VIEWPORT viewports[2] = {left_half, right_half};
D3D12_RECT scissors[2] = {left_rect, right_rect};  // ビューポートと同じ数が要る
command_list->RSSetViewports(2, viewports);
command_list->RSSetScissorRects(2, scissors);
```

## 切り抜きの使いみち

シザー矩形はビューポートの全体ではなく、一部だけを描くのに使えます。UI のスクロール領域でははみ出した内容を切り抜きます。ライトの影響範囲ではライトのバウンディング ボックスを画面へ投影して、その範囲だけをライティングします。画面の一部だけを再描画する部分更新にも使えます。

## 画面の大きさが変わったとき

ウィンドウの大きさが変わったら、ビューポートとシザー矩形も新しい大きさへ更新します。

```cpp
void OnResize(UINT width, UINT height) {
  viewport_ = {0.0f, 0.0f, float(width), float(height), 0.0f, 1.0f};
  scissor_ = {0, 0, LONG(width), LONG(height)};
  // バック バッファ、深度、G バッファを作り直す（Swap Chain のページ）
}
```

## よくあるミス

??? failure "何も描かれない（クリアの色のまま）"
    シザー矩形を設定していません。D3D12 はシザーが常に有効で、未設定だと範囲が 0 になります。ビューポートも設定したか確認します。

??? failure "`Reset` のあとに描いたら、何も出ない"
    `Reset` でビューポートとシザー矩形が初期化されています。毎フレーム設定し直します。

??? failure "縮小したレンダー ターゲットの左上にしか描かれない"
    ビューポートが元の大きさのままです。レンダー ターゲットを切り替えるたびに合わせます。

??? failure "画面の右端と下端が 1 画素欠ける"
    シザー矩形の `right` と `bottom` を `width − 1`、`height − 1` にしています。`D3D12_RECT` は右と下を含まないので `width` と `height` を指定します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ビューポートはクリップ空間を画面のどこに描くか。シザー矩形はその中の切り抜き
    - [x] D3D12 では、シザー矩形が常に有効。未設定だと何も出ない
    - [x] `Reset` のたびに両方を設定し直す
    - [x] ふつうはレンダー ターゲット全体。縮小したときは同じ大きさにする
    - [x] `D3D12_RECT` の `right` と `bottom` は、範囲の外側

## 関連ページ

- [DirectX 12 Guide](index.md)
- [ID3D12GraphicsCommandList](api/id3d12graphicscommandlist.md)
- [Drawing a Triangle](triangle.md)
- [Command List](command-list.md)
- [Microsoft Learn: RSSetViewports](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d12/nf-d3d12-id3d12graphicscommandlist-rssetviewports)
