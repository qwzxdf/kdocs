---
title: Hiding Tiling
tags:
  - 描画
---

# Hiding Tiling

**タイル テクスチャは、広い範囲に貼ると、繰り返しが目立ちます**。**大きさの違うテクスチャを重ねる・ランダムに回転させる**ことで、**隠せます**。このページでは、**タイリングの隠し方**を説明します。

!!! tip "ポイント"
    - **異なるスケールで 2 回貼って、混ぜる**。
    - **ノイズで、テクスチャ座標をずらす**。
    - **タイルごとに、ランダムに回す・反転する**。
    - **遠くは、低周波の色むらを重ねる**。

<!-- fig:tiling-hide:begin -->

<svg class="fig illust motion" data-fig="tiling-hide" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-tiling-hide" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">繰り返しを隠す:周期の違う 2 つのパターンを、重ねる</text>
<line x1="60" y1="140" x2="720" y2="140" stroke="#e2e8f0" stroke-width="1.5"/>
<text x="60" y="80" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">パターン A（周期 110）</text>
<line x1="60" y1="230" x2="720" y2="230" stroke="#e2e8f0" stroke-width="1.5"/>
<text x="60" y="170" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">パターン B（周期 163、別のスケール）</text>
<line x1="60" y1="340" x2="720" y2="340" stroke="#e2e8f0" stroke-width="1.5"/>
<text x="60" y="280" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">重ねた結果</text>
<circle cx="100" cy="140" r="14" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;1.0000" values="0;0;1;1"/></circle>
<circle cx="210" cy="140" r="14" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1187;0.1190;1.0000" values="0;0;1;1"/></circle>
<circle cx="320" cy="140" r="14" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1425;0.1429;1.0000" values="0;0;1;1"/></circle>
<circle cx="430" cy="140" r="14" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1663;0.1667;1.0000" values="0;0;1;1"/></circle>
<circle cx="540" cy="140" r="14" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1901;0.1905;1.0000" values="0;0;1;1"/></circle>
<circle cx="650" cy="140" r="14" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2139;0.2143;1.0000" values="0;0;1;1"/></circle>
<circle cx="150" cy="230" r="14" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2663;0.2667;1.0000" values="0;0;1;1"/></circle>
<circle cx="313" cy="230" r="14" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2901;0.2905;1.0000" values="0;0;1;1"/></circle>
<circle cx="476" cy="230" r="14" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3139;0.3143;1.0000" values="0;0;1;1"/></circle>
<circle cx="639" cy="230" r="14" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3377;0.3381;1.0000" values="0;0;1;1"/></circle>
<path d="M60,338.24 L64,336.82 L68,334.59 L72,331.35 L76,327.01 L80,321.68 L84,315.73 L88,309.78 L92,304.64 L96,301.1 L100,299.7 L104,300.59 L108,303.42 L112,307.42 L116,311.56 L120,314.79 L124,316.33 L128,315.81 L132,313.34 L136,309.54 L140,305.34 L144,301.8 L148,299.84 L152,300.05 L156,302.49 L160,306.76 L164,312.07 L168,317.48 L172,322.07 L176,325.13 L180,326.21 L184,325.13 L188,322.07 L192,317.48 L196,312.08 L200,306.79 L204,302.58 L208,300.26 L212,300.29 L216,302.71 L220,307.09 L224,312.72 L228,318.76 L232,324.46 L236,329.32 L240,333.1 L244,335.81 L248,337.6 L252,338.69 L256,339.27 L260,339.5 L264,339.41 L268,338.97 L272,338.03 L276,336.32 L280,333.47 L284,329.08 L288,322.79 L292,314.45 L296,304.27 L300,292.93 L304,281.59 L308,271.71 L312,264.78 L316,261.93 L320,263.65 L324,269.65 L328,278.92 L332,290.04 L336,301.5 L340,312.06 L344,320.89 L348,327.69 L352,332.54 L356,335.74 L360,337.7 L364,338.83 L368,339.43 L372,339.7 L376,339.76 L380,339.66 L384,339.34 L388,338.72 L392,337.61 L396,335.82 L400,333.1 L404,329.32 L408,324.45 L412,318.74 L416,312.69 L420,307.01 L424,302.51 L428,299.87 L432,299.4 L436,300.96 L440,303.91 L444,307.31 L448,310.11 L452,311.47 L456,311.0 L460,308.84 L464,305.62 L468,302.32 L472,299.95 L476,299.35 L480,300.89 L484,304.48 L488,309.55 L492,315.27 L496,320.77 L500,325.25 L504,328.17 L508,329.17 L512,328.17 L516,325.26 L520,320.77 L524,315.29 L528,309.6 L532,304.61 L536,301.2 L540,299.99 L544,301.23 L548,304.7 L552,309.81 L556,315.74 L560,321.69 L564,327.01 L568,331.35 L572,334.58 L576,336.8 L580,338.2 L584,338.97 L588,339.28 L592,339.21 L596,338.7 L600,337.61 L604,335.69 L608,332.6 L612,327.98 L616,321.58 L620,313.34 L624,303.54 L628,292.88 L632,282.41 L636,273.42 L640,267.17 L644,264.62 L648,266.16 L652,271.56 L656,279.97 L660,290.19 L664,300.92 L668,311.02 L672,319.69 L676,326.56 L680,331.6 L684,335.05 L688,337.25 L692,338.56 L696,339.29 L700,339.67 L704,339.86 L708,339.94 L712,339.98 L716,339.99 L720,340.0" fill="none" stroke="#e5484d" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4758;0.4762;1.0000" values="0;0;1;1"/></path>
<text x="60" y="376" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">A も B も、それぞれ等間隔（規則的な繰り返し）<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4758;0.4762;1.0000" values="1;1;0;0"/></text>
<text x="60" y="376" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">重ねると、山の位置と高さが不揃い → 繰り返しが目立たない（周期が公約数を持たないほど良い）<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4758;0.4762;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:tiling-hide:end -->

## 繰り返し（タイリング）を隠す
**繰り返しテクスチャは、広い範囲に貼ると同じ模様の並びが目立ちます**。

繰り返しを隠す工夫です。2 つのスケールを重ねて、大きさの違う 2 枚を混ぜると、周期がずれます。近景と遠景でスケールを切り替え、距離で細かいタイルと大きなタイルを使い分けます。タイルごとにランダムに回す方法は、セルごとの回転とオフセットをハッシュで決め、境でブレンドします。マクロ バリエーションは、低周波のノイズで色を少しずらします。ディテール テクスチャは、近づいたときだけ細かい模様を重ねます。

```hlsl
float2 uv_near = world_position.xz * 0.5;
float2 uv_far = world_position.xz * 0.043;
float3 near_color = albedo.Sample(linear_wrap, uv_near).rgb;
float3 far_color = albedo.Sample(linear_wrap, uv_far).rgb;
float3 color = near_color * far_color * 2.0;
```

**2 枚を掛けて 2 倍**にすると、**平均の明るさが保たれます**。

## よくあるミス

??? failure "格子状の繰り返しが、遠くから見て目立つ"
    **スケールを変えた重ね貼り**をする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **スケールを変えて重ね、ノイズでずらす**

## 参考

- Strugar, "Continuous Distance-Dependent Level of Detail for Rendering Heightmaps (CDLOD)"（JGT 2010）
- Losasso & Hoppe, "Geometry Clipmaps"（SIGGRAPH 2004）
- Musgrave et al., "The Synthesis and Rendering of Eroded Fractal Terrains"（SIGGRAPH 1989）

## 関連ページ

- [Terrain Texturing](index.md)
- [Triplanar Mapping](triplanar.md)
