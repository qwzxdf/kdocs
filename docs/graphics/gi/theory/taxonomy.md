---
title: 手法の分類
tags:
  - 描画
---

# 手法の分類

**GI の手法は数多くありますが、「2 つの軸」で整理すると、見通しが良くなります**。**1 つ目は「静的 ↔ 動的」、2 つ目は「画面内の情報 ↔ 世界の情報」**です。このページでは、**2 つの軸と、代表的な手法の位置づけ**を説明します。

!!! tip "ポイント"
    - **軸 1：静的（ベイク）か、動的（リアルタイム）か**。
    - **軸 2：画面の情報だけか、世界全体の情報か**。
    - **ライトマップ ＝ 静的・世界**。**SSGI ＝ 動的・画面**。**DDGI・Lumen ＝ 動的・世界**。
    - **用途と予算に合わせて選ぶ**。

## 手法を分ける 2 つの軸
### 軸 1：いつ計算するか

| 区分 | 内容 | 例 |
| --- | --- | --- |
| <strong>事前（ベイク）</strong> | **オフラインで計算**し、**結果を保存** | ライトマップ・ベイク済みプローブ |
| **準動的** | **静的なジオメトリ**に対し、**光だけ**動的に更新 | プローブの再ライティング・DDGI |
| **完全動的** | **ジオメトリも光も動く**。**毎フレーム計算** | SSGI・ボクセル GI・レイトレ GI |

### 軸 2：どこに情報を持つか

| 保存先 | 内容 | 例 |
| --- | --- | --- |
| <strong>面（テクスチャ）</strong> | **オブジェクトの表面**の UV 上 | ライトマップ |
| **空間の点** | **3D 空間の格子・点** | プローブ・DDGI |
| **画面** | **今見えている画素**だけ | SSGI |
| **ボクセル** | **3D の格子**に**シーンの光・形** | ボクセル GI |
| <strong>世界（レイ）</strong> | **光線を飛ばして、その場で** | レイトレ GI |

**各手法はこの 2 軸のどこに位置するか**で、**長所・短所**がほぼ決まります。

<!-- fig:gi-color-bleeding:begin -->

<svg class="fig illust motion" data-fig="gi-color-bleeding" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-gi-color-bleeding" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<linearGradient id="gi-bleed" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff5a5f" stop-opacity="0.75"/>
<stop offset="1" stop-color="#ff5a5f" stop-opacity="0"/>
</linearGradient>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">間接光:光が壁で跳ね返って、隣の面に色がにじむ</text>
<rect x="80" y="60" width="480" height="270" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/>
<rect x="72" y="60" width="16" height="270" fill="#e5484d"/>
<text x="86" y="52" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">赤い壁</text>
<rect x="80" y="330" width="480" height="14" fill="#94a3b8"/>
<rect x="80" y="320" width="180" height="10" fill="url(#gi-bleed)" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000" values="0;0;1;1"/></rect>
<circle cx="330" cy="72" r="12" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<text x="348" y="78" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">光源</text>
<line x1="330" y1="84" x2="420" y2="328" stroke="#e5aa28" stroke-width="3" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0870;0.1739;1.0000" values="1;1;0;0"/></line>
<polygon points="420,328 411.36,319.67 421.16,316.06" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1736;0.1739;1.0000" values="0;0;1;1"/></polygon>
<rect x="386" y="320" width="68" height="10" fill="#fde68a" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1736;0.1739;1.0000" values="0;0;1;1"/></rect>
<line x1="320" y1="82" x2="86" y2="190" stroke="#e5aa28" stroke-width="3" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2435;0.3304;1.0000" values="1;1;0;0"/></line>
<polygon points="86,190 93.62,180.73 98.0,190.21" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3301;0.3304;1.0000" values="0;0;1;1"/></polygon>
<line x1="86" y1="190" x2="130" y2="328" stroke="#ff5a5f" stroke-width="2.5" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3826;0.4522;1.0000" values="1;1;0;0"/></line>
<polygon points="130,328 121.74,319.29 131.69,316.12" fill="#ff5a5f" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4518;0.4522;1.0000" values="0;0;1;1"/></polygon>
<line x1="86" y1="190" x2="210" y2="328" stroke="#ff5a5f" stroke-width="2.5" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4170;0.4174;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4174;0.4870;1.0000" values="1;1;0;0"/></line>
<polygon points="210,328 198.9,323.45 206.66,316.47" fill="#ff5a5f" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4866;0.4870;1.0000" values="0;0;1;1"/></polygon>
<line x1="86" y1="190" x2="290" y2="328" stroke="#ff5a5f" stroke-width="2.5" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4518;0.4522;1.0000" values="0;0;1;1"/><animate attributeName="stroke-dashoffset" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4522;0.5217;1.0000" values="1;1;0;0"/></line>
<polygon points="290,328 278.13,326.27 283.97,317.62" fill="#ff5a5f" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000" values="0;0;1;1"/></polygon>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">光源から出た光<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① 床に当たる（直接光）→ 明るくなる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2431;0.2435;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② 赤い壁に当たる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;0.3823;0.3826;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">③ 壁は赤い光だけを反射して、四方に跳ね返す<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;0.5214;0.5217;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="358" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">④ 壁の近くの床が、赤っぽくなる（色のにじみ）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5214;0.5217;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="80" y="384" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">間接光は、直接光が当たった面が「次の光源」になる。リアルタイムでは、プローブやボクセルで近似する。</text>
<text x="590" y="90" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">光の跳ね返り</text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">0 回<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;1.0000" values="1;1;0;0"/></text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">1 回（直接）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2431;0.2435;1.0000" values="0;0;1;1;0;0"/></text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">1 回（壁へ）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2431;0.2435;0.3823;0.3826;1.0000" values="0;0;1;1;0;0"/></text>
<text x="590" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937" opacity="0">2 回（壁 → 床）<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3823;0.3826;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:gi-color-bleeding:end -->

## よくあるミス

??? failure "動的な光に、ライトマップを使ってしまう"
    **動的な光には、動的な GI**（プローブ・SSGI など）を選ぶ。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **静的か動的か、画面か世界か**
    - [x] **用途に合わせて選ぶ**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [GI の理論](index.md)
- [GI の比較](../comparison.md)
- [ライトマップ](../lightmaps/index.md)
