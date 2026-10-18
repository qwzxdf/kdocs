---
title: Quality and Performance
tags:
  - 描画
---

# Quality and Performance

**ボリューメトリック フォグは、解像度とスライス数で、品質とコストが大きく変わります**。このページでは、**品質と速度の目安**を説明します。

!!! tip "ポイント"
    - **解像度：160×90 が標準**（1080p の場合）。
    - **スライス数：64**が**標準**。
    - **ライトの数が多いと、重い**。
    - **品質設定で、解像度とスライス数を切り替える**。

## Quality and Speed {#品質と速度}
| 項目 | 内容 |
| --- | --- |
| **解像度** | **160×90×64 で十分**。**重ければ 80×45×32** |
| **コスト** | **0.3〜1 ms 程度** |
| **局所ライトの数** | **多いほど重い**。**影付きのライトは数本まで** |
| **遠距離** | **範囲外は距離フォグ（[距離フォグ](../aerial-fog/index.md)）に任せる** |
| **雲・大気との組み合わせ** | **近くはボリューメトリック フォグ、遠くは空気遠近法 LUT** |

### Where the Cost Is Decided {#どこでコストが決まるか}

ボリューメトリック フォグのコストは、主に 3 つのパスで発生します。<strong>光の注入</strong>は、セルごとに、すべてのライトと影を評価するので、セル数 × ライト数に比例します。最も重いパスで、影付きライトの数が最大の要因です。<strong>積分</strong>は、奥行き方向の累積で、セル数に比例しますが、1 セルあたりの処理は軽く、全体で 0.1 ms 以下です。<strong>適用</strong>は、画素ごとに 3D テクスチャを 1 回引くだけで、安価です。

したがって、コストを下げたいときは、まず光の注入を見ます。影付きライトを減らす、ライトを遠くのものから省く、セル数（解像度）を下げる、のいずれかです。解像度を下げると、品質が落ちるのは主に光の筋の細かさなので、時間蓄積（[Temporal Accumulation](temporal.md)）で補うと、見た目を保ちながら軽くできます。

### Choosing the Range {#範囲の選び方}

froxel は、カメラの前方のごく近い範囲だけを覆うのが現実的です。たとえば最大距離を 64〜128 m にすれば、64 スライスで十分な密度が出ます。それより遠くは、空気遠近法の LUT で連続的につなぎます。境目で急に変わらないよう、最大距離の手前でボリューメトリック フォグの寄与をフェードアウトさせ、遠景のフォグと重ねます。

<!-- fig:froxel-depth-split:begin -->

<svg class="fig illust motion" data-fig="froxel-depth-split" viewBox="0 0 780 340" role="img"><rect x="0" y="0" width="780" height="340" rx="14" fill="#ffffff"/>
<defs><marker id="arr-froxel-depth-split" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">スライスを奥行きに並べる 2 通り: 等間隔と、手前を細かく</text>
<line x1="60" y1="110" x2="720" y2="110" stroke="#94a3b8" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;1.0000" values="0;0;1;1"/><line x1="60.0" y1="88" x2="60.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="101.25" y1="88" x2="101.25" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="142.5" y1="88" x2="142.5" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="183.75" y1="88" x2="183.75" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="225.0" y1="88" x2="225.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="266.25" y1="88" x2="266.25" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="307.5" y1="88" x2="307.5" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="348.75" y1="88" x2="348.75" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="390.0" y1="88" x2="390.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="431.25" y1="88" x2="431.25" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="472.5" y1="88" x2="472.5" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="513.75" y1="88" x2="513.75" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="555.0" y1="88" x2="555.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="596.25" y1="88" x2="596.25" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="637.5" y1="88" x2="637.5" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="678.75" y1="88" x2="678.75" y2="132" stroke="#64748b" stroke-width="2.5"/>
<line x1="720.0" y1="88" x2="720.0" y2="132" stroke="#64748b" stroke-width="2.5"/>
<text x="60" y="72" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">等間隔(1 枚 6.3 m)</text>
</g>
<line x1="60" y1="220" x2="720" y2="220" stroke="#94a3b8" stroke-width="2"/>
<g opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;1.0000" values="0;0;1;1"/><line x1="60.0" y1="198" x2="60.0" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="63.49744860406542" y1="198" x2="63.49744860406542" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="67.98826150524448" y1="198" x2="67.98826150524448" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="73.75457941194762" y1="198" x2="73.75457941194762" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="81.1586781648561" y1="198" x2="81.1586781648561" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="90.66572915125658" y1="198" x2="90.66572915125658" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="102.87302425554108" y1="198" x2="102.87302425554108" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="118.54750143845021" y1="198" x2="118.54750143845021" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="138.6739285345976" y1="198" x2="138.6739285345976" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="164.5167724731637" y1="198" x2="164.5167724731637" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="197.69964092977727" y1="198" x2="197.69964092977727" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="240.3072874266751" y1="198" x2="240.3072874266751" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="295.01658847393827" y1="198" x2="295.01658847393827" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="365.2647215478455" y1="198" x2="365.2647215478455" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="455.46510988960506" y1="198" x2="455.46510988960506" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="571.2847011155291" y1="198" x2="571.2847011155291" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<line x1="720.0" y1="198" x2="720.0" y2="242" stroke="#2563eb" stroke-width="2.5"/>
<text x="60" y="182" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">指数(手前が細かい)</text>
</g>
<text x="60" y="275" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">カメラ 0 m</text>
<text x="720" y="275" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">100 m</text>
<text x="390" y="315" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">16 枚のスライスを、0〜100 m に並べる<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;1.0000" values="1;1;0;0"/></text>
<text x="390" y="315" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">等間隔: 遠くも近くも同じ粗さ<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;0.3330;0.3333;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="315" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">指数: 目に近い所を細かく、遠くを粗く(遠くは、もともと小さく見える)<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:froxel-depth-split:end -->

## Common Mistakes {#よくあるミス}

??? failure "フォグの計算が重く、フレーム時間が伸びる"
    **解像度・スライス数を下げる**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **解像度とスライス数で、調整**

## References {#参考}

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## Related Pages {#関連ページ}

- [Volumetric Fog](index.md)
- [Froxels](froxel.md)
