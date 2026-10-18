---
title: Blend State
tags:
  - 描画
---

# Blend State

<strong>半透明の描画は、GPU の「ブレンド ステート」の設定で決まります</strong>。<strong>DirectX 11 では、ソース係数・デスティネーション係数・演算を指定</strong>します。このページでは、代表的な設定（通常・加算・乗算）とコードを説明します。

!!! tip "ポイント"
    - 通常：SrcAlpha / InvSrcAlpha。
    - 加算：One / One（光・炎・魔法）。
    - 乗算：Zero / SrcColor（影・色付きガラス）。
    - 深度の書き込みは OFF、読み取りは ON。

## DirectX 11 のブレンド ステート
```cpp
D3D11_BLEND_DESC blend_desc = {};
blend_desc.RenderTarget[0].BlendEnable = TRUE;
blend_desc.RenderTarget[0].SrcBlend = D3D11_BLEND_SRC_ALPHA;
blend_desc.RenderTarget[0].DestBlend = D3D11_BLEND_INV_SRC_ALPHA;
blend_desc.RenderTarget[0].BlendOp = D3D11_BLEND_OP_ADD;
blend_desc.RenderTarget[0].SrcBlendAlpha = D3D11_BLEND_ONE;
blend_desc.RenderTarget[0].DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
blend_desc.RenderTarget[0].BlendOpAlpha = D3D11_BLEND_OP_ADD;
blend_desc.RenderTarget[0].RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
device->CreateBlendState(&blend_desc, &alpha_blend_state);

D3D11_DEPTH_STENCIL_DESC depth_desc = {};
depth_desc.DepthEnable = TRUE;
depth_desc.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;
depth_desc.DepthFunc = D3D11_COMPARISON_LESS;
device->CreateDepthStencilState(&depth_desc, &transparent_depth_state);
```

| 項目 | 設定 | 意味 |
| --- | --- | --- |
| `SrcBlend` | `SRC_ALPHA` | ソースの色に、ソースのアルファを掛ける |
| `DestBlend` | `INV_SRC_ALPHA` | デスティネーションに、(1 − ソースのアルファ) を掛ける |
| `BlendOp` | `ADD` | 足す |
| `DepthWriteMask` | `ZERO` | 深度を書かない（半透明が、後の半透明を隠さない） |
| `DepthFunc` | `LESS` | 深度テストは行う（不透明の後ろにある物は描かない） |

<strong>深度書き込みを ON のままにする</strong>と、<strong>手前の半透明が、奥の半透明の描画を妨げ</strong>ます（奥が、描かれなくなる）。

<!-- fig:blend-modes:begin -->

<svg class="fig illust motion" data-fig="blend-modes" viewBox="0 0 780 360" role="img"><rect x="0" y="0" width="780" height="360" rx="14" fill="#ffffff"/>
<defs><marker id="arr-blend-modes" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ブレンドの種類:同じ円を、3 つの混ぜ方で重ねる</text>
<text x="130" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">通常（アルファ）</text>
<rect x="30" y="90" width="50" height="170" fill="#e5484d"/>
<rect x="80" y="90" width="50" height="170" fill="#2ea043"/>
<rect x="130" y="90" width="50" height="170" fill="#2563eb"/>
<rect x="180" y="90" width="50" height="170" fill="#fde68a"/>
<rect x="30" y="90" width="200" height="170" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="130" cy="175" r="70" fill="#f97316" opacity="0" style="mix-blend-mode:normal"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0692;0.0696;1.0000" values="0;0;0.6;0.6"/></circle>
<text x="130" y="292" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">背景と混ざる（α で）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0692;0.0696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="380" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">加算（光・炎）</text>
<rect x="280" y="90" width="50" height="170" fill="#e5484d"/>
<rect x="330" y="90" width="50" height="170" fill="#2ea043"/>
<rect x="380" y="90" width="50" height="170" fill="#2563eb"/>
<rect x="430" y="90" width="50" height="170" fill="#fde68a"/>
<rect x="280" y="90" width="200" height="170" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="380" cy="175" r="70" fill="#f97316" opacity="0" style="mix-blend-mode:screen"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3127;0.3130;1.0000" values="0;0;1;1"/></circle>
<text x="380" y="292" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">明るくなる（足し算）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3127;0.3130;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="630" y="70" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">乗算（影・色ガラス）</text>
<rect x="530" y="90" width="50" height="170" fill="#e5484d"/>
<rect x="580" y="90" width="50" height="170" fill="#2ea043"/>
<rect x="630" y="90" width="50" height="170" fill="#2563eb"/>
<rect x="680" y="90" width="50" height="170" fill="#fde68a"/>
<rect x="530" y="90" width="200" height="170" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="630" cy="175" r="70" fill="#8ec5ff" opacity="0" style="mix-blend-mode:multiply"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5562;0.5565;1.0000" values="0;0;1;1"/></circle>
<text x="630" y="292" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">暗くなる（掛け算）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5562;0.5565;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="30" y="336" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">通常:SrcAlpha / InvSrcAlpha、加算:One / One、乗算:Zero / SrcColor</text>
</svg>

<!-- fig:blend-modes:end -->

### ブレンドの種類

| 種類 | `SrcBlend` / `DestBlend` | 式 | 用途 |
| --- | --- | --- | --- |
| <strong>通常（アルファ）</strong> | `SRC_ALPHA` / `INV_SRC_ALPHA` | `C_s·α + C_d·(1−α)` | ガラス・水・UI |
| 加算 | `SRC_ALPHA` / `ONE` | `C_s·α + C_d` | 炎・光・魔法・爆発 |
| <strong>加算（アルファなし）</strong> | `ONE` / `ONE` | `C_s + C_d` | 明るい光の粒 |
| 乗算 | `ZERO` / `SRC_COLOR` | `C_d · C_s` | 影・色付きガラス・暗くする |
| 乗算済みアルファ | `ONE` / `INV_SRC_ALPHA` | `C_s + C_d·(1−α)` | 通常の、安定した方式 |

<strong>加算と乗算は、順序に依存しない</strong>（足し算・掛け算は、交換できる）ので、<strong>ソートが不要</strong>です。炎・光の粒・影は、この性質を利用してソートなしで描けることが多いです。

## ブレンドの式

半透明の描画は、<strong>これから描く色（ソース）</strong>と、<strong>すでに画面に、ある色（デスティネーション）</strong>を、式で、混ぜます。DirectX 11 の、ブレンド ステートは、この式の、部品を、指定します。

```text
結果 = ソース × SrcBlend  [演算 BlendOp]  デスティネーション × DestBlend
```

| 部品 | 意味 | よく使う値 |
| --- | --- | --- |
| `SrcBlend` | ソース（これから描く色）に、掛ける係数 | `SRC_ALPHA`、`ONE` |
| `DestBlend` | デスティネーション（画面の色）に、掛ける係数 | `INV_SRC_ALPHA`、`ONE` |
| `BlendOp` | 2 つを、どう組み合わせるか | `ADD`（足す）、`MAX`、`MIN` |

## 代表的なブレンド

### ① 通常の、アルファ ブレンド

```text
結果 = ソース × α  +  デスティネーション × (1 − α)
```

ガラス、煙、フェードする物の、<strong>標準</strong>です。

```cpp
D3D11_RENDER_TARGET_BLEND_DESC& rt = blend.RenderTarget[0];
rt.BlendEnable = TRUE;
rt.SrcBlend = D3D11_BLEND_SRC_ALPHA;
rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOp = D3D11_BLEND_OP_ADD;
rt.SrcBlendAlpha = D3D11_BLEND_ONE;                // アルファ チャンネルの合成
rt.DestBlendAlpha = D3D11_BLEND_INV_SRC_ALPHA;
rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
rt.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
```

### ② 加算ブレンド

```text
結果 = ソース × α  +  デスティネーション × 1
```

火、光、魔法の、輝きなど、<strong>明るさを、足していく</strong>表現です。<strong>順序に、依存しない</strong>（足し算は、順序を、入れ替えても同じ）ので、ソートが不要です。

```cpp
rt.SrcBlend = D3D11_BLEND_SRC_ALPHA;
rt.DestBlend = D3D11_BLEND_ONE;                    // 画面の色を、そのまま残して、足す
rt.BlendOp = D3D11_BLEND_OP_ADD;
```

加算ブレンドは、<strong>重なるほど、明るく</strong>なり、<strong>白に近づきます</strong>。HDR で、明るさの上限が、無い場合は、ブルームで、光る表現に、つながります（[Bloom](../../postprocess/bloom/index.md)）。

### ③ 乗算ブレンド

```text
結果 = ソース × デスティネーション
```

<strong>色付きガラス</strong>、<strong>影</strong>、汚れのように、背景の色を、暗くする表現です。

```cpp
rt.SrcBlend = D3D11_BLEND_ZERO;
rt.DestBlend = D3D11_BLEND_SRC_COLOR;              // 画面の色 × ソースの色
```

乗算も、<strong>順序に依存しません</strong>（掛け算は、順序を入れ替えても、同じ）。

### ④ 乗算済みアルファ

```text
結果 = ソース（すでに α が掛かっている）  +  デスティネーション × (1 − α)
```

アルファ ブレンドの、<strong>ソースに、あらかじめ、アルファを、掛けておく</strong>形です（[Premultiplied Alpha](premultiplied.md)）。

```cpp
rt.SrcBlend = D3D11_BLEND_ONE;                     // ソースには、掛けない（掛け済み）
rt.DestBlend = D3D11_BLEND_INV_SRC_ALPHA;
```

## 比較

| ブレンド | SrcBlend | DestBlend | 向く表現 | 順序依存 |
| --- | --- | --- | --- | --- |
| アルファ | SRC_ALPHA | INV_SRC_ALPHA | ガラス、フェード | 依存する |
| 乗算済みアルファ | ONE | INV_SRC_ALPHA | 煙 + 光を、1 つのレイヤーで | 依存する |
| 加算 | SRC_ALPHA（または ONE） | ONE | 火、光、魔法 | しない |
| 乗算 | ZERO | SRC_COLOR | 色ガラス、影 | しない |
| 最大値（MAX） | ONE | ONE（`BlendOp = MAX`） | 重なっても、強い方だけ残す（[Trampled Grass](../../terrain/vegetation/trample.md)） | しない |

## 深度の設定との組み合わせ

半透明は、<strong>深度テストは、行い、深度の書き込みは、しない</strong>のが、基本です。

```cpp
D3D11_DEPTH_STENCIL_DESC ds = {};
ds.DepthEnable = TRUE;                                  // 不透明な物の後ろは、隠す
ds.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;        // 半透明は、深度を書かない
ds.DepthFunc = D3D11_COMPARISON_LESS_EQUAL;
device->CreateDepthStencilState(&ds, &transparent_depth_state);
```

| 設定 | 理由 |
| --- | --- |
| テスト：有効 | 不透明な物の、後ろにある、半透明は、描かない |
| 書き込み：無効 | 半透明が、深度を書くと、その後ろの、半透明が、隠れてしまう |

## 描画の順番

半透明は、<strong>不透明の後</strong>に、描きます。

```text
① 不透明を描く（深度を書く）
② 半透明を描く（深度テストのみ、書き込みなし）、ソートして、奥から手前へ
③ ポストプロセス
```

半透明の中の、順序は、<strong>ソート</strong>で決めます（[Sorting](sorting.md)）。

## 複数の、レンダー ターゲットと、ブレンド

レンダー ターゲットごとに、<strong>別のブレンド</strong>を、指定できます（`IndependentBlendEnable = TRUE`）。OIT の、実装（[WBOIT](../oit/wboit.md)）で、<strong>2 つのターゲット</strong>に、別々の、ブレンドを、使います。

```cpp
blend.IndependentBlendEnable = TRUE;
blend.RenderTarget[0] = accum_blend;         // 加算（WBOIT の、積算）
blend.RenderTarget[1] = reveal_blend;        // 乗算風（WBOIT の、透過度）
```

## よくあるミス

??? failure "半透明の物が、後ろの物を隠して、穴が開いたように見える"
    <strong>深度の書き込みを OFF</strong>にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 通常・加算・乗算の 3 つを覚える
    - [x] 半透明は、深度の書き込み OFF

## 参考

- Porter, Duff, "Compositing Digital Images", SIGGRAPH 1984（アルファ合成の原典）
- Smith, "Image Compositing Fundamentals", Microsoft Technical Memo 4, 1995（乗算済みアルファ）
- Microsoft Learn, "D3D11_RENDER_TARGET_BLEND_DESC"（`SrcBlend`、`DestBlend`、`BlendOp`）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明、屈折、フレネルの章）

## 関連ページ

- [Alpha Blending and Sorting](index.md)
- [Premultiplied Alpha](premultiplied.md)
