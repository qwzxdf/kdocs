---
title: Depth-Stencil State
tags:
  - DirectX
---

# Depth-Stencil State

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
</div>

<strong>深度ステンシル ステート</strong>は、<strong>深度テストと、ステンシル テストを、どう行うか</strong>の、設定です。「深度を、比べるか」「テストに通ったら、深度を、書くか」「ステンシルを、どう使うか」を、決めます。不透明な物、半透明の物、ポスト プロセス、シャドウで、それぞれ、設定が、違うので、用途ごとに、ステートを、作って、切り替えます。

!!! tip "ポイント"
    - 深度ステート ＝ 深度テストの、有効・無効、比較関数、書き込みの有無。
    - <strong>不透明</strong>: テスト有り・書き込み有り・`LESS`。<strong>半透明</strong>: テスト有り・書き込み<strong>無し</strong>。<strong>ポスト プロセス</strong>: テスト無し・書き込み無し。
    - ステートは、`CreateDepthStencilState` で作り、`OMSetDepthStencilState` で、つなぐ。
    - 作ったステートは、使い回す（毎フレーム、作らない）。
    - ステンシルは、マスク（皮膚だけ、ポータルの中だけ）に、使う。

## 不透明な物（既定）

```cpp
D3D11_DEPTH_STENCIL_DESC desc = {};
desc.DepthEnable = TRUE;                                    // 深度テストを、行う
desc.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ALL;           // テストに通ったら、深度を、書く
desc.DepthFunc = D3D11_COMPARISON_LESS;                     // 手前（小さい）なら、通る
desc.StencilEnable = FALSE;

Microsoft::WRL::ComPtr<ID3D11DepthStencilState> state;
device->CreateDepthStencilState(&desc, &state);
context->OMSetDepthStencilState(state.Get(), 0);            // 第 2 引数: ステンシルの、参照値
```

| メンバー | 内容 |
| --- | --- |
| `DepthEnable` | 深度テストを、行うか |
| `DepthWriteMask` | `ALL`（書く）、`ZERO`（書かない） |
| `DepthFunc` | 比較関数（下の表） |
| `StencilEnable` | ステンシルを、使うか |
| `StencilReadMask`・`StencilWriteMask` | ステンシルの、読み書きの、ビット マスク |
| `FrontFace`・`BackFace` | 表面・裏面の、ステンシルの、動作 |

D3D11 の、既定のステート（何も、設定しないとき）は、`DepthEnable = TRUE`、`WriteMask = ALL`、`DepthFunc = LESS`、`StencilEnable = FALSE` です。

## 比較関数

| `DepthFunc` | 通る条件（新しい深度 `<op>` バッファの深度） | 使いどころ |
| --- | --- | --- |
| `LESS` | より小さい（近い） | 通常の、不透明 |
| `LESS_EQUAL` | 以下 | 深度を、事前に描いた後の、本描画（同じ深度を、通す） |
| `GREATER` | より大きい | reverse-Z で、通常の描画 |
| `GREATER_EQUAL` | 以上 | reverse-Z で、事前深度の後 |
| `EQUAL` | 等しい | 事前深度の後、同じ深度の、ピクセルだけ、シェーディング |
| `ALWAYS` | 常に通る | 深度に、関係なく、描く（UI） |
| `NEVER` | 通らない | 使わない |

<strong>reverse-Z</strong>（近い面が 1、遠い面が 0）を、使うときは、`LESS` を、`GREATER` に、`LESS_EQUAL` を、`GREATER_EQUAL` に、読み替えます。クリア値も、`1.0` から `0.0` に、変えます。

## 用途別の、ステート

### 半透明（深度テストだけ）

```cpp
D3D11_DEPTH_STENCIL_DESC desc = {};
desc.DepthEnable = TRUE;
desc.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;          // 書かない（後ろの、半透明が、隠れないように）
desc.DepthFunc = D3D11_COMPARISON_LESS_EQUAL;
```

半透明の、物は、不透明な物に、隠れる（深度テスト有り）が、半透明同士は、互いを、隠さない（書き込み無し）ように、します。奥から、手前の順に、描きます（[Alpha Blending and Sorting](../../graphics/translucency/index.md)）。

### ポスト プロセス・フルスクリーン

```cpp
D3D11_DEPTH_STENCIL_DESC desc = {};
desc.DepthEnable = FALSE;                                   // 深度テストなし・書き込みなし
```

画面全体に、パスを、走らせるときは、深度テストを、無効にします。

### 事前深度パス（Z プリパス）

```cpp
// パス 1: 深度だけ描く（色は、書かない）。通常の、LESS、書き込み有り。
// パス 2: 色を描く。深度は、書かず、EQUAL（または LESS_EQUAL）で、同じ深度だけを、通す。
D3D11_DEPTH_STENCIL_DESC color_pass = {};
color_pass.DepthEnable = TRUE;
color_pass.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;
color_pass.DepthFunc = D3D11_COMPARISON_EQUAL;
```

深度を、先に描くと、本描画の、ピクセル シェーダーが、見える物だけで、走り、<strong>オーバードロー</strong>（隠れる物の、シェーディング）が、なくなります（[Overdraw](../../rendering/overdraw.md)）。

### スカイボックス

```cpp
desc.DepthEnable = TRUE;
desc.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;
desc.DepthFunc = D3D11_COMPARISON_LESS_EQUAL;               // 頂点シェーダーで、z = w（深度 1.0）に、固定して、描く
```

不透明な物を、先に描いた後、空を、最後に、深度 1.0 で、描くと、空に、隠れていない、ピクセルだけが、塗られます。

## ステンシル

ステンシルは、深度と、同じ、バッファに、同居する、8 ビットの、<strong>マスク</strong>です。ピクセルごとに、整数の、値を、書き、後の、パスで、その値で、描くかを、決めます。

```cpp
// 例: 皮膚のピクセルに、ステンシル値 1 を書く（描画パス）。
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
// 皮膚の後処理: ステンシルが 1 のピクセルだけ、シェーダーを、走らせる。
D3D11_DEPTH_STENCIL_DESC test = {};
test.DepthEnable = FALSE;
test.StencilEnable = TRUE;
test.StencilReadMask = 0xFF;
test.FrontFace.StencilFunc = D3D11_COMPARISON_EQUAL;        // ステンシルが、参照値と、等しければ、通る
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
| `REPLACE` | 参照値で、置き換える |
| `INCR_SAT`・`DECR_SAT` | 増やす・減らす（0・255 で止まる） |
| `INCR`・`DECR` | 増やす・減らす（巻き戻る） |
| `INVERT` | ビット反転 |

ステンシルの、使いどころは、皮膚の SSS のマスク（[Screen-Space SSS](../../graphics/skin-hair/skin/screen-space-sss.md)）、輪郭線、ポータル、シャドウ ボリュームなどです。

## ステートの、使い回し

ステートは、<strong>不変（イミュータブル）</strong>な、オブジェクトで、作ったら、変更できません。用途ごとに、起動時に、作り、毎フレーム、`OMSetDepthStencilState` で、切り替えます。

```cpp
struct DepthStates {
  ComPtr<ID3D11DepthStencilState> opaque;          // テスト有り・書き込み有り・LESS
  ComPtr<ID3D11DepthStencilState> transparent;     // テスト有り・書き込み無し
  ComPtr<ID3D11DepthStencilState> off;             // テスト無し
  ComPtr<ID3D11DepthStencilState> sky;             // LESS_EQUAL・書き込み無し
};
```

## よくあるミス

??? failure "半透明の物が、互いを、隠して、おかしく見える"
    半透明の物に、深度の書き込みが、有効。`DepthWriteMask = ZERO` にする。

??? failure "ポスト プロセスが、画面の一部しか、描かれない"
    深度テストが、有効のまま。`DepthEnable = FALSE` にする。または、DSV が、`OMSetRenderTargets` に、束ねられたまま。

??? failure "事前深度の後、本描画で、ちらつく（Z ファイティング）"
    `LESS` で、同じ深度を、通そうとして、はじかれている。`EQUAL`、または、`LESS_EQUAL` を、使う。頂点シェーダーの、計算が、2 つのパスで、同じ結果になるように、`invariant` を、考える。

??? failure "reverse-Z にしたのに、何も、描かれない"
    `DepthFunc` が、`LESS` のまま。クリア値が、`1.0` のまま。`GREATER` と `0.0` に、そろえる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 深度ステート ＝ 深度テストの、設定（有効・書き込み・比較関数）
    - [x] 不透明は、テスト有り・書き込み有り。半透明は、書き込み無し。ポスト プロセスは、無し
    - [x] 事前深度の後は、`EQUAL`（または `LESS_EQUAL`）
    - [x] reverse-Z は、`GREATER`、クリア 0.0
    - [x] ステンシルは、マスク（皮膚、ポータル）
    - [x] ステートは、起動時に作り、使い回す

## 関連ページ

- [DirectX 11 Guide](index.md)
- [Depth Buffer and DSV](depth-stencil.md)
- [Blend State](blend-state.md)
- [Rasterizer State](rasterizer-state.md)
- [Overdraw](../../rendering/overdraw.md)
- [Microsoft Learn: ID3D11Device::CreateDepthStencilState](https://learn.microsoft.com/ja-jp/windows/win32/api/d3d11/nf-d3d11-id3d11device-createdepthstencilstate)
