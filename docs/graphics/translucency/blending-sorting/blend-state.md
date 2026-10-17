---
title: Blend State
tags:
  - 描画
---

# Blend State

**半透明の描画は、GPU の「ブレンド ステート」の設定で決まります**。**DirectX 11 では、ソース係数・デスティネーション係数・演算を指定**します。このページでは、**代表的な設定（通常・加算・乗算）とコード**を説明します。

!!! tip "ポイント"
    - **通常：SrcAlpha / InvSrcAlpha**。
    - **加算：One / One**（光・炎・魔法）。
    - **乗算：Zero / SrcColor**（影・色付きガラス）。
    - **深度の書き込みは OFF、読み取りは ON**。

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
| **`SrcBlend`** | `SRC_ALPHA` | **ソースの色に、ソースのアルファを掛ける** |
| **`DestBlend`** | `INV_SRC_ALPHA` | **デスティネーションに、(1 − ソースのアルファ) を掛ける** |
| **`BlendOp`** | `ADD` | **足す** |
| **`DepthWriteMask`** | `ZERO` | **深度を書かない**（半透明が、後の半透明を隠さない） |
| **`DepthFunc`** | `LESS` | **深度テストは行う**（不透明の後ろにある物は描かない） |

**深度書き込みを ON のままにする**と、**手前の半透明が、奥の半透明の描画を妨げ**ます（**奥が、描かれなくなる**）。

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
| **加算** | `SRC_ALPHA` / `ONE` | `C_s·α + C_d` | 炎・光・魔法・爆発 |
| <strong>加算（アルファなし）</strong> | `ONE` / `ONE` | `C_s + C_d` | 明るい光の粒 |
| **乗算** | `ZERO` / `SRC_COLOR` | `C_d · C_s` | 影・色付きガラス・暗くする |
| **乗算済みアルファ** | `ONE` / `INV_SRC_ALPHA` | `C_s + C_d·(1−α)` | 通常の、安定した方式 |

**加算と乗算は、順序に依存しない**（足し算・掛け算は、交換できる）ので、**ソートが不要**です。**炎・光の粒・影**は、**この性質を利用**して**ソートなしで描ける**ことが多いです。

## よくあるミス

??? failure "半透明の物が、後ろの物を隠して、穴が開いたように見える"
    **深度の書き込みを OFF**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **通常・加算・乗算の 3 つを覚える**
    - [x] **半透明は、深度の書き込み OFF**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [Alpha Blending and Sorting](index.md)
- [Premultiplied Alpha](premultiplied.md)
