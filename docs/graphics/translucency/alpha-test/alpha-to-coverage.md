---
title: Alpha to Coverage
tags:
  - 描画
---

# Alpha to Coverage

**Alpha to Coverage（A2C）は、MSAA のサンプル マスクを、アルファ値に応じて決める手法**です。**縁がなめらかになり、ソートも不要**なので、**葉や草に最適**です。このページでは、**A2C の仕組みと使い方**を説明します。

!!! tip "ポイント"
    - **アルファ値を、MSAA の「カバレッジ（何サンプル覆うか）」に変換**する。
    - **ソート不要・縁がなめらか**。
    - **MSAA が必要**（4x なら、5 段階の濃さ）。
    - **遠くで細る問題は、アルファの補正で対処**する。

<!-- fig:a2c-coverage:begin -->

<svg class="fig illust motion" data-fig="a2c-coverage" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-a2c-coverage" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">Alpha to Coverage:アルファを、MSAA のサンプルの数に置き換える</text>
<rect x="65.0" y="115.0" width="190" height="190" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
<circle cx="112.5" cy="162.5" r="14" fill="#ffffff" stroke="#1f2937" stroke-width="2.5"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.1926;0.3111;0.4296;0.5481;0.6667" values="#ffffff;#ffffff;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d"/></circle>
<circle cx="207.5" cy="162.5" r="14" fill="#ffffff" stroke="#1f2937" stroke-width="2.5"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.1926;0.3111;0.4296;0.5481;0.6667" values="#ffffff;#ffffff;#ffffff;#ffffff;#e5484d;#e5484d;#ffffff"/></circle>
<circle cx="112.5" cy="257.5" r="14" fill="#ffffff" stroke="#1f2937" stroke-width="2.5"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.1926;0.3111;0.4296;0.5481;0.6667" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#e5484d;#ffffff"/></circle>
<circle cx="207.5" cy="257.5" r="14" fill="#ffffff" stroke="#1f2937" stroke-width="2.5"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.1926;0.3111;0.4296;0.5481;0.6667" values="#ffffff;#ffffff;#ffffff;#e5484d;#e5484d;#e5484d;#e5484d"/></circle>
<rect x="420" y="120" width="170" height="100" fill="#ffffff" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0741;0.1926;0.3111;0.4296;0.5481;0.6667" values="#ffffff;#ffffff;#f8d1d2;#f2a4a6;#ec767a;#e5484d;#f2a4a6"/></rect>
<text x="505" y="110" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">解像した結果（4 サンプルの平均）</text>
<text x="420" y="260" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">アルファ 0.00 → 覆うサンプル 0 / 4<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.1923;0.1926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="420" y="260" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">アルファ 0.25 → 覆うサンプル 1 / 4<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;0.3108;0.3111;1.0000" values="0;0;1;1;0;0"/></text>
<text x="420" y="260" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">アルファ 0.50 → 覆うサンプル 2 / 4<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3108;0.3111;0.4293;0.4296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="420" y="260" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">アルファ 0.75 → 覆うサンプル 3 / 4<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;0.5479;0.5481;1.0000" values="0;0;1;1;0;0"/></text>
<text x="420" y="260" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">アルファ 1.00 → 覆うサンプル 4 / 4<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;0.6664;0.6667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="420" y="260" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">アルファ 0.50 → 覆うサンプル 2 / 4<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6664;0.6667;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="420" y="292" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">覆ったサンプルだけに、色を書く<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="340" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">1 画素の中の 4 つのサンプル。アルファに応じた数のサンプルだけを「覆う」。ソート不要で、縁がなめらかになる。</text>
<text x="60" y="362" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">MSAA 4x なら 5 段階（0〜4）。段数が少ないので、縞が出やすい（ハッシュドや TAA と併用する）。</text>
</svg>

<!-- fig:a2c-coverage:end -->

## Alpha to Coverage
**MSAA を使っているとき**、**アルファの値を、そのまま「カバレッジ（どのサンプルを塗るか）」に変換**する機能です。**アルファ 0.5 なら、4 サンプルのうち 2 つを塗る**ことで、**縁が滑らかな段階**になります。

```cpp
D3D11_BLEND_DESC desc = {};
desc.AlphaToCoverageEnable = TRUE;
desc.RenderTarget[0].RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
device->CreateBlendState(&desc, &alpha_to_coverage_state);
```

| 点 | 説明 |
| --- | --- |
| **`AlphaToCoverageEnable`** | **ピクセル シェーダーの出力アルファを、カバレッジ マスクに変換** |
| **MSAA が必要** | **MSAA の描画先**（`SampleDesc.Count` が 2 以上）でのみ**有効** |
| **ブレンドは不要** | **アルファ ブレンドとは別の機構**。**深度も書ける** |
| **効果** | **縁が、MSAA のサンプル数ぶんの段階で滑らかに** |

**4x MSAA では 5 段階**（0/4〜4/4）の**透明度**しか**表せません**。**ディザリングのようなパターン**が**見える**ことがあります。

## よくあるミス

??? failure "A2C を設定したのに、効果が出ない"
    **MSAA を有効**にし、**ブレンド ステートで A2C を ON**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **アルファを MSAA のカバレッジに変換**
    - [x] **葉や草に最適**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [Alpha Testing](index.md)
- [Hashed Alpha](hashed-alpha.md)
- [比較](comparison.md)
