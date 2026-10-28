---
title: Depth-Stencil State
tags:
  - DirectX
---

# Depth-Stencil State

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>深度ステンシル ステート</strong>は、<strong>深度テストとステンシル テストをどう行うか</strong>の設定です。「深度を比べるか」「テストに通ったら深度を書くか」「ステンシルをどう使うか」を決めます。不透明な物、半透明の物、ポスト プロセス、シャドウでそれぞれ設定が違うので、用途ごとにステートを作って切り替えます。

!!! tip "ポイント"
    - 深度ステート ＝ 深度テストの、有効・無効、比較関数、書き込みの有無。
    - <strong>不透明</strong>: テスト有り・書き込み有り・`LESS`。<strong>半透明</strong>: テスト有り・書き込み<strong>無し</strong>。<strong>ポスト プロセス</strong>: テスト無し・書き込み無し。
    - ステートは `CreateDepthStencilState` で作り `OMSetDepthStencilState` で、つなぐ。
    - 作ったステートは、使い回す（毎フレーム、作らない）。
    - ステンシルはマスク（皮膚だけ、ポータルの中だけ）に使う。

!!! info "このページを読む前に"
    - [DirectX 11 Guide](index.md)（このセクション全体の地図と、読む順番）
    - [GPU Pipeline Overview](../concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）
    - [Coordinate Conventions](../concepts/conventions.md)（このセクションの約束（座標系・行列））
    - [DirectX 11 Guide](guide.md)（全体の手順（どの順に作るか））

## 不透明な物（既定）

```cpp
D3D11_DEPTH_STENCIL_DESC desc = {};
desc.DepthEnable = TRUE;                                    // 深度テストを行う
desc.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ALL;           // テストに通ったら、深度を書く
desc.DepthFunc = D3D11_COMPARISON_LESS;                     // 手前（小さい）なら、通る
desc.StencilEnable = FALSE;

Microsoft::WRL::ComPtr<ID3D11DepthStencilState> state;
device->CreateDepthStencilState(&desc, &state);
context->OMSetDepthStencilState(state.Get(), 0);            // 第 2 引数: ステンシルの、参照値
```

| メンバー | 内容 |
| --- | --- |
| `DepthEnable` | 深度テストを行うか |
| `DepthWriteMask` | `ALL`（書く）、`ZERO`（書かない） |
| `DepthFunc` | 比較関数（下の表） |
| `StencilEnable` | ステンシルを使うか |
| `StencilReadMask`・`StencilWriteMask` | ステンシルの、読み書きのビット マスク |
| `FrontFace`・`BackFace` | 表面・裏面の、ステンシルの動作 |

D3D11 の既定のステート（何も、設定しないとき）は `DepthEnable = TRUE`、`WriteMask = ALL`、`DepthFunc = LESS`、`StencilEnable = FALSE` です。

## 比較関数

| `DepthFunc` | 通る条件（新しい深度 `<op>` バッファの深度） | 使いどころ |
| --- | --- | --- |
| `LESS` | より小さい（近い） | 通常の、不透明 |
| `LESS_EQUAL` | 以下 | 深度を事前に描いた後の本描画（同じ深度を通す） |
| `GREATER` | より大きい | reverse-Z で、通常の描画 |
| `GREATER_EQUAL` | 以上 | reverse-Z で、事前深度の後 |
| `EQUAL` | 等しい | 事前深度の後、同じ深度のピクセルだけシェーディング |
| `ALWAYS` | 常に通る | 深度に関係なく描く（UI） |
| `NEVER` | 通らない | 使わない |

<strong>reverse-Z</strong>（近い面が 1、遠い面が 0）を使うときは `LESS` を `GREATER` に `LESS_EQUAL` を `GREATER_EQUAL` に、読み替えます。クリア値も `1.0` から `0.0` に変えます。

## 用途別のステート

### 半透明（深度テストだけ）

```cpp
D3D11_DEPTH_STENCIL_DESC desc = {};
desc.DepthEnable = TRUE;
desc.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;          // 書かない（後ろの、半透明が隠れないように）
desc.DepthFunc = D3D11_COMPARISON_LESS_EQUAL;
```

半透明の物は不透明な物に隠れる（深度テスト有り）が半透明同士は互いを隠さない（書き込み無し）ように、します。奥から手前の順に描きます（[Alpha Blending and Sorting](../../graphics/translucency/index.md)）。

### ポスト プロセス・フルスクリーン

```cpp
D3D11_DEPTH_STENCIL_DESC desc = {};
desc.DepthEnable = FALSE;                                   // 深度テストなし・書き込みなし
```

画面全体にパスを走らせるときは、深度テストを無効にします。

### 事前深度パス（Z プリパス）

```cpp
// パス 1: 深度だけ描く（色は、書かない）。通常の、LESS、書き込み有り。
// パス 2: 色を描く。深度は、書かず、EQUAL（または LESS_EQUAL）で、同じ深度だけを通す。
D3D11_DEPTH_STENCIL_DESC color_pass = {};
color_pass.DepthEnable = TRUE;
color_pass.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;
color_pass.DepthFunc = D3D11_COMPARISON_EQUAL;
```

深度を先に描くと本描画のピクセル シェーダーが見える物だけで走り <strong>オーバードロー</strong>（隠れる物の、シェーディング）がなくなります（[Overdraw](../../rendering/overdraw.md)）。

### スカイボックス

```cpp
desc.DepthEnable = TRUE;
desc.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;
desc.DepthFunc = D3D11_COMPARISON_LESS_EQUAL;               // 頂点シェーダーで、z = w（深度 1.0）に固定して、描く
```

不透明な物を先に描いた後、空を最後に深度 1.0 で描くと空に隠れていないピクセルだけが塗られます。

## ステンシル

ステンシルは深度と同じバッファに同居する 8 ビットの <strong>マスク</strong>です。ピクセルごとに整数の値を書き後のパスで、その値で描くかを決めます。

```cpp
// 例: 皮膚のピクセルにステンシル値 1 を書く（描画パス）。
D3D11_DEPTH_STENCIL_DESC write = {};
write.DepthEnable = TRUE;
write.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ALL;
write.DepthFunc = D3D11_COMPARISON_LESS;
write.StencilEnable = TRUE;
write.StencilReadMask = 0xFF;
write.StencilWriteMask = 0xFF;
write.FrontFace.StencilFunc = D3D11_COMPARISON_ALWAYS;      // 常に通る
write.FrontFace.StencilPassOp = D3D11_STENCIL_OP_REPLACE;   // 通ったら、参照値で、置き換える
write.FrontFace.StencilFailOp = D3D11_STENCIL_OP_KEEP;
write.FrontFace.StencilDepthFailOp = D3D11_STENCIL_OP_KEEP;
write.BackFace = write.FrontFace;
device->CreateDepthStencilState(&write, &skin_write_state);
context->OMSetDepthStencilState(skin_write_state.Get(), 1); // 参照値 1
```

```cpp
// 皮膚の後処理: ステンシルが 1 のピクセルだけ、シェーダーを走らせる。
D3D11_DEPTH_STENCIL_DESC test = {};
test.DepthEnable = FALSE;
test.StencilEnable = TRUE;
test.StencilReadMask = 0xFF;
test.FrontFace.StencilFunc = D3D11_COMPARISON_EQUAL;        // ステンシルが参照値と、等しければ、通る
test.FrontFace.StencilPassOp = D3D11_STENCIL_OP_KEEP;
test.FrontFace.StencilFailOp = D3D11_STENCIL_OP_KEEP;
test.FrontFace.StencilDepthFailOp = D3D11_STENCIL_OP_KEEP;
test.BackFace = test.FrontFace;
device->CreateDepthStencilState(&test, &skin_test_state);
context->OMSetDepthStencilState(skin_test_state.Get(), 1);
```

| 動作（`StencilOp`） | 内容 |
| --- | --- |
| `KEEP` | 変えない |
| `ZERO` | 0 にする |
| `REPLACE` | 参照値で置き換える |
| `INCR_SAT`・`DECR_SAT` | 増やす・減らす（0・255 で止まる） |
| `INCR`・`DECR` | 増やす・減らす（巻き戻る） |
| `INVERT` | ビット反転 |

ステンシルの使いどころは皮膚の SSS のマスク（[Screen-Space SSS](../../graphics/skin-hair/skin/screen-space-sss.md)）、輪郭線、ポータル、シャドウ ボリュームなどです。

## ステートの使い回し

ステートは <strong>不変（イミュータブル）</strong>な、オブジェクトで作ったら変更できません。用途ごとに起動時に作り毎フレーム、`OMSetDepthStencilState` で切り替えます。

```cpp
struct DepthStates {
  ComPtr<ID3D11DepthStencilState> opaque;          // テスト有り・書き込み有り・LESS
  ComPtr<ID3D11DepthStencilState> transparent;     // テスト有り・書き込み無し
  ComPtr<ID3D11DepthStencilState> off;             // テスト無し
  ComPtr<ID3D11DepthStencilState> sky;             // LESS_EQUAL・書き込み無し
};
```

## よくあるミス

??? failure "半透明の物が互いを隠して、おかしく見える"
    半透明の物に深度の書き込みが有効。`DepthWriteMask = ZERO` にする。

??? failure "ポスト プロセスが画面の一部しか描かれない"
    深度テストが有効のまま。`DepthEnable = FALSE` にする。または、DSV が `OMSetRenderTargets` に束ねられたまま。

??? failure "事前深度の後、本描画でちらつく（Z ファイティング）"
    `LESS` で同じ深度を通そうとして、はじかれている。`EQUAL`、または `LESS_EQUAL` を使う。頂点シェーダーの計算が 2 つのパスで、同じ結果になるように `invariant` を考える。

??? failure "reverse-Z にしたのに何も、描かれない"
    `DepthFunc` が `LESS` のまま。クリア値が `1.0` のまま。`GREATER` と `0.0` にそろえる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 深度ステート ＝ 深度テストの、設定（有効・書き込み・比較関数）
    - [x] 不透明は、テスト有り・書き込み有り。半透明は書き込み無し。ポスト プロセスは無し
    - [x] 事前深度の後は、`EQUAL`（または `LESS_EQUAL`）
    - [x] reverse-Z は `GREATER`、クリア 0.0
    - [x] ステンシルは、マスク（皮膚、ポータル）
    - [x] ステートは、起動時に作り使い回す

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Depth Buffer and DSV](depth-stencil.md)
- [Blend State](blend-state.md)
- [Rasterizer State](rasterizer-state.md)
- [Overdraw](../../rendering/overdraw.md)
- [Microsoft Learn: ID3D11Device::CreateDepthStencilState](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createdepthstencilstate)
