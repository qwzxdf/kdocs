---
title: Radiance Cascades
tags:
  - 描画
---

# Radiance Cascades

**Radiance Cascades は、「近くの光は高解像度で、遠くの光は低解像度で」持つ、階層的な方式**です。**2D の GI で特に成功しており、3D にも展開されつつあります**。このページでは、**Radiance Cascades の発想と、利点**を説明します。

!!! tip "ポイント"
    - **近くの光は、細かい空間解像度・粗い方向解像度**。
    - **遠くの光は、粗い空間解像度・細かい方向解像度**。
    - **階層ごとに結果をマージ**して、全体の光を求める。
    - **ノイズが少なく、安定している**。

## Radiance Cascades
**Radiance Cascades**（Alexander Sannikov、2023〜）は、**ノイズのない、全画素の放射照度**を**階層的な構造**で**効率よく計算する**方式です。

<!-- fig:radiance-cascades:begin -->

<svg class="fig illust motion" data-fig="radiance-cascades" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-radiance-cascades" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<clipPath id="rc-clip"><rect x="40" y="80" width="700" height="250"/>
</clipPath>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">Radiance Cascades:近くは細かい位置、遠くは細かい方向</text>
<rect x="40" y="80" width="700" height="250" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/><circle cx="90" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="90" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="90" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="90" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="90" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="140" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="140" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="140" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="140" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="140" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="240" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="240" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="240" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="240" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="240" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="340" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="340" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="340" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="340" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="340" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="440" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="440" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="440" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="440" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="440" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="540" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="540" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="540" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="540" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="540" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="640" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="640" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="640" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="640" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="640" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<line x1="390.0" y1="205.0" x2="445.0" y2="205.0" stroke="#0284c7" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="390.0" y1="205.0" x2="390.0" y2="260.0" stroke="#0284c7" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="390.0" y1="205.0" x2="335.0" y2="205.0" stroke="#0284c7" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="390.0" y1="205.0" x2="390.0" y2="150.0" stroke="#0284c7" stroke-width="2.2" clip-path="url(#rc-clip)"/>
</g>
<text x="390" y="352" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">カスケード 0:プローブ間隔 狭い・方向 4 本・短い距離<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.3256;0.3259;1.0000" values="0;0;1;1;0;0"/></text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;1.0000" values="0;0;1;1"/><circle cx="90" cy="105" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="90" cy="205" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="90" cy="305" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="105" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="205" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="305" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="105" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="205" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="305" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="105" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="205" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="305" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="105" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="205" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="305" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="105" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="205" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="305" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="105" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="205" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="305" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<line x1="445.0" y1="205.0" x2="515.0" y2="205.0" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="428.89" y1="243.89" x2="478.39" y2="293.39" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="390.0" y1="260.0" x2="390.0" y2="330.0" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="351.11" y1="243.89" x2="301.61" y2="293.39" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="335.0" y1="205.0" x2="265.0" y2="205.0" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="351.11" y1="166.11" x2="301.61" y2="116.61" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="390.0" y1="150.0" x2="390.0" y2="80.0" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="428.89" y1="166.11" x2="478.39" y2="116.61" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
</g>
<text x="390" y="352" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">カスケード 1:間隔 2 倍・方向 8 本・中距離<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;0.5775;0.5778;1.0000" values="0;0;1;1;0;0"/></text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5775;0.5778;1.0000" values="0;0;1;1"/><circle cx="190" cy="205" r="4" fill="#fbcfe8" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="205" r="4" fill="#fbcfe8" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="205" r="4" fill="#fbcfe8" stroke="#64748b" stroke-width="1"/>
<line x1="515.0" y1="205.0" x2="660.0" y2="205.0" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="505.48" y1="252.84" x2="639.45" y2="308.32" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="478.39" y1="293.39" x2="580.92" y2="395.92" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="437.84" y1="320.48" x2="493.32" y2="454.45" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="390.0" y1="330.0" x2="390.0" y2="475.0" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="342.16" y1="320.48" x2="286.68" y2="454.45" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="301.61" y1="293.39" x2="199.08" y2="395.92" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="274.52" y1="252.84" x2="140.55" y2="308.32" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="265.0" y1="205.0" x2="120.0" y2="205.0" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="274.52" y1="157.16" x2="140.55" y2="101.68" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="301.61" y1="116.61" x2="199.08" y2="14.08" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="342.16" y1="89.52" x2="286.68" y2="-44.45" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="390.0" y1="80.0" x2="390.0" y2="-65.0" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="437.84" y1="89.52" x2="493.32" y2="-44.45" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="478.39" y1="116.61" x2="580.92" y2="14.08" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="505.48" y1="157.16" x2="639.45" y2="101.68" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
</g>
<text x="390" y="352" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">カスケード 2:間隔 4 倍・方向 16 本・遠距離<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5775;0.5778;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">近い光は多くのプローブで、遠い光は少ないプローブで<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">プローブの数は 1/4 ずつ、方向の数は 2〜4 倍ずつ。階層を重ねて、全体の光を作る<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">合計のレイ数がほぼ一定。ノイズが少なく、安定している（2D の GI で特に成功している）。</text>
</svg>

<!-- fig:radiance-cascades:end -->

### 発想：空間と方向のトレードオフ

**ある点が受け取る光**を**正確に知る**には、<strong>「点を細かく」×「方向を細かく」</strong>の**積**だけ**サンプル**が要りそうです。しかし、<strong>「近い距離の光」と「遠い距離の光」では必要な精度が違います</strong>。

| 距離 | 必要な精度 |
| --- | --- |
| <strong>近い光（短いレイ）</strong> | **点（空間）は細かく**、**方向は粗くてよい**（近い物は角度が大きく見える） |
| <strong>遠い光（長いレイ）</strong> | **点は粗くてよい**、**方向は細かく**（遠い物は角度が小さく、位置が変わっても見える向きが同じ） |

### カスケード

<strong>複数の「カスケード」</strong>を用意します。

| カスケード | プローブの密度（空間） | 方向の数 | 担当する距離 |
| --- | --- | --- | --- |
| **0** | **最も細かい** | **少ない** | **近距離** |
| **1** | **半分** | **倍** | **やや遠く** |
| **2** | **さらに半分** | **さらに倍** | **さらに遠く** |
| … | … | … | … |

<strong>各カスケードは、自分の担当する距離の「区間」</strong>だけを**レイでトレース**します。**最後にカスケードをマージ**（**遠い方の結果を近い方に伝える**）して、**全画素の全距離にわたる放射照度**を得ます。

| 性質 | 内容 |
| --- | --- |
| **ノイズなし** | **ランダム性を使わず、規則的なサンプル**で**ノイズがない** |
| **計算量** | **カスケードごとのレイ数がほぼ一定**（空間が半分・方向が倍で**総数はあまり変わらない**）。**画素数 × 定数** |
| **2D で成功** | **2D ゲームの GI**で、**非常に有効**（**Radiance Cascades の 2D 版**） |
| **3D への拡張** | **研究・実装が進行中**（**3D は方向が球面（2 次元）で、重い**） |

**まだ発展途中**の技術ですが、**ノイズのない GI**として、**注目**されています。

## よくあるミス

??? failure "階層の境目に、段差が見える"
    **階層間を補間**して、なめらかにつなぐ。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **距離ごとに、解像度を変えて持つ**
    - [x] **ノイズが少なく、安定**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Ray-Traced GI](index.md)
- [Choosing a Method](choosing.md)
- [SSGI](../ssgi.md)
