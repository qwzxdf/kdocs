---
title: Atmospheric Scattering
tags:
  - 描画
---

# Atmospheric Scattering

<strong>空が青く、夕焼けが赤いのは、大気中の分子や粒子が、光を散乱させるため</strong>です。<strong>この散乱を計算すると、物理的に正しい空が作れます</strong>。このセクションでは、空が青い理由・大気のモデル・透過率・単散乱・位相関数・多重散乱・Bruneton の事前計算・Hillaire の 4 つの LUT・地面と宇宙を、1 つずつ別のページで説明します。

## なぜ空は青いか
<strong>太陽光は白色</strong>（全波長を含む）ですが<strong>大気の分子に当たると短い波長（青）ほど強く散らされます</strong>。

<div class="formula">レイリー散乱の強さ ∝ 1 / λ⁴</div>

| 波長 | 色 | 相対的な散乱の強さ |
| --- | --- | --- |
| 700 nm | 赤 | 1.0 |
| 550 nm | 緑 | 約 2.6 |
| 450 nm | 青 | 約 5.9 |

<strong>青い光が全方向に散って空が青く見えます</strong>。<strong>夕方は太陽の光が大気を長く通り、青が散り尽くして赤だけが残る</strong>ので、太陽が赤く、空が赤く染まります。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="夕焼けの理由">
<text x="20" y="24" class="fig-title">昼と夕方：光が通る大気の長さが違う</text>
<path d="M60,220 A320,320 0 0 1 720,220" fill="none" stroke="#4c8bf5" stroke-opacity="0.5" stroke-width="22"/>
<line x1="60" y1="220" x2="720" y2="220" stroke="currentColor" stroke-opacity="0.5"/>
<circle cx="390" cy="220" r="5" fill="#e5484d"/>
<text x="400" y="240" style="font-size:12px">観測者</text>
<line x1="390" y1="60" x2="390" y2="215" stroke="#e5aa28" stroke-width="3"/>
<text x="398" y="110" style="font-size:12px">昼：大気を短く通る → 白い</text>
<line x1="80" y1="190" x2="385" y2="218" stroke="#e5484d" stroke-width="3"/>
<text x="110" y="180" style="font-size:12px">夕方：大気を長く通る → 赤い</text>
</svg>

<!-- fig:sunset-path:begin -->

<svg class="fig illust motion" data-fig="sunset-path" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-sunset-path" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<clipPath id="sun-clip"><rect x="32" y="98" width="596" height="336"/>
</clipPath>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">夕焼け: 太陽が低いほど、光が空気の中を長く通り、青から先に散ってなくなる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">図は大気の厚みを誇張。太陽の高さを 90° → 30° → 10° → 2° に下げて、色を計算する</text>
<rect x="30" y="96" width="600" height="340" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">地面と大気(断面)</text>
<g clip-path="url(#sun-clip)"><circle cx="330.0" cy="740.0" r="420.0" fill="#d1fae5" stroke="#34d399" stroke-width="2"/>
<circle cx="330.0" cy="740.0" r="476.0" fill="#e0f2fe" fill-opacity="0.0" stroke="#93c5fd" stroke-width="2.5" stroke-dasharray="6 5"/>
</g>
<circle cx="330.0" cy="320.0" r="7" fill="#1f2937"/>
<text x="330.0" y="344.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">見る人</text>
<g opacity="0" clip-path="url(#sun-clip)"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2535;0.2537;1.0000" values="1;1;0;0"/><line x1="330.0" y1="320.0" x2="330.0" y2="105.0" stroke="#fde68a" stroke-width="2" stroke-dasharray="6 5"/>
<line x1="330.0" y1="320.0" x2="330.0" y2="264.0" stroke="#e5484d" stroke-width="4"/>
<circle cx="330.0" cy="105.0" r="14" fill="#e5aa28"/>
<text x="370.0" y="342.0" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">太陽の高さ 90°</text>
</g>
<g opacity="0" clip-path="url(#sun-clip)"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2535;0.2537;0.4583;0.4585;1.0000" values="0;0;1;1;0;0"/><line x1="330.0" y1="320.0" x2="516.2" y2="212.5" stroke="#fde68a" stroke-width="2" stroke-dasharray="6 5"/>
<line x1="330.0" y1="320.0" x2="414.04" y2="271.48" stroke="#e5484d" stroke-width="4"/>
<circle cx="516.2" cy="212.5" r="14" fill="#e5aa28"/>
<text x="370.0" y="342.0" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">太陽の高さ 30°</text>
</g>
<g opacity="0" clip-path="url(#sun-clip)"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.4583;0.4585;0.6632;0.6634;1.0000" values="0;0;1;1;0;0"/><line x1="330.0" y1="320.0" x2="541.73" y2="282.67" stroke="#fde68a" stroke-width="2" stroke-dasharray="6 5"/>
<line x1="330.0" y1="320.0" x2="490.17" y2="291.76" stroke="#e5484d" stroke-width="4"/>
<circle cx="541.73" cy="282.67" r="14" fill="#e5aa28"/>
<text x="370.0" y="342.0" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">太陽の高さ 10°</text>
</g>
<g opacity="0" clip-path="url(#sun-clip)"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.6632;0.6634;1.0000" values="0;0;1;1"/><line x1="330.0" y1="320.0" x2="544.87" y2="312.5" stroke="#fde68a" stroke-width="2" stroke-dasharray="6 5"/>
<line x1="330.0" y1="320.0" x2="539.69" y2="312.68" stroke="#e5484d" stroke-width="4"/>
<circle cx="544.87" cy="312.5" r="14" fill="#e5aa28"/>
<text x="370.0" y="342.0" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">太陽の高さ 2°</text>
</g>
<rect x="660" y="96" width="270" height="340" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="660" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">太陽の色(大気を抜けた後)</text>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2535;0.2537;1.0000" values="1;1;0;0"/><circle cx="795" cy="170" r="44" fill="#faedce" stroke="#334155" stroke-width="2"/>
<text x="795" y="238" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">空気の通る長さ: 天頂の 1.0 倍</text>
<rect x="700" y="262" width="182.26" height="18" fill="#e5484d" opacity="0.85"/>
<text x="688" y="276" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5484d">R</text>
<text x="888.2603306620972" y="276" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">96%</text>
<rect x="700" y="292" width="172.44" height="18" fill="#2ea043" opacity="0.85"/>
<text x="688" y="306" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043">G</text>
<text x="878.4404585309053" y="306" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">91%</text>
<rect x="700" y="322" width="149.92" height="18" fill="#2563eb" opacity="0.85"/>
<text x="688" y="336" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2563eb">B</text>
<text x="855.9185775059016" y="336" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">79%</text>
<text x="795" y="370" text-anchor="middle" style="font-size:16px;font-weight:700;fill:#7c3aed">真上: ほぼ白</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2535;0.2537;0.4583;0.4585;1.0000" values="0;0;1;1;0;0"/><circle cx="795" cy="170" r="44" fill="#f6dca7" stroke="#334155" stroke-width="2"/>
<text x="795" y="238" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">空気の通る長さ: 天頂の 2.0 倍</text>
<rect x="700" y="262" width="174.87" height="18" fill="#e5484d" opacity="0.85"/>
<text x="688" y="276" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5484d">R</text>
<text x="880.8732611407656" y="276" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">92%</text>
<rect x="700" y="292" width="156.58" height="18" fill="#2ea043" opacity="0.85"/>
<text x="688" y="306" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043">G</text>
<text x="862.5816603808343" y="306" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">82%</text>
<rect x="700" y="322" width="118.44" height="18" fill="#2563eb" opacity="0.85"/>
<text x="688" y="336" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2563eb">B</text>
<text x="824.4364661439507" y="336" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">62%</text>
<text x="795" y="370" text-anchor="middle" style="font-size:16px;font-weight:700;fill:#7c3aed">少し黄色っぽい</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.4583;0.4585;0.6632;0.6634;1.0000" values="0;0;1;1;0;0"/><circle cx="795" cy="170" r="44" fill="#e7aa4e" stroke="#334155" stroke-width="2"/>
<text x="795" y="238" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">空気の通る長さ: 天頂の 5.6 倍</text>
<rect x="700" y="262" width="150.6" height="18" fill="#e5484d" opacity="0.85"/>
<text x="688" y="276" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5484d">R</text>
<text x="856.6026602509437" y="276" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">79%</text>
<rect x="700" y="292" width="110.52" height="18" fill="#2ea043" opacity="0.85"/>
<text x="688" y="306" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043">G</text>
<text x="816.5180207990045" y="306" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">58%</text>
<rect x="700" y="322" width="50.56" height="18" fill="#2563eb" opacity="0.85"/>
<text x="688" y="336" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2563eb">B</text>
<text x="756.558625737061" y="336" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">27%</text>
<text x="795" y="370" text-anchor="middle" style="font-size:16px;font-weight:700;fill:#7c3aed">オレンジ</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.6632;0.6634;1.0000" values="0;0;1;1"/><circle cx="795" cy="170" r="44" fill="#bf4104" stroke="#334155" stroke-width="2"/>
<text x="795" y="238" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">空気の通る長さ: 天頂の 19.4 倍</text>
<rect x="700" y="262" width="84.66" height="18" fill="#e5484d" opacity="0.85"/>
<text x="688" y="276" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5484d">R</text>
<text x="790.6564308598158" y="276" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">45%</text>
<rect x="700" y="292" width="28.85" height="18" fill="#2ea043" opacity="0.85"/>
<text x="688" y="306" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043">G</text>
<text x="734.8468065905714" y="306" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">15%</text>
<rect x="700" y="322" width="1.9" height="18" fill="#2563eb" opacity="0.85"/>
<text x="688" y="336" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2563eb">B</text>
<text x="707.8990333274305" y="336" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">1%</text>
<text x="795" y="370" text-anchor="middle" style="font-size:16px;font-weight:700;fill:#7c3aed">深い赤</text>
</g>
<text x="70" y="470" text-anchor="start" style="font-size:30px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;1.0000" values="1;1;0;0"/></text>
<text x="70" y="470" text-anchor="start" style="font-size:30px;font-weight:700;fill:#e5484d" opacity="0">90<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;0.2535;0.2537;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="470" text-anchor="start" style="font-size:30px;font-weight:700;fill:#e5484d" opacity="0">30<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2535;0.2537;0.4583;0.4585;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="470" text-anchor="start" style="font-size:30px;font-weight:700;fill:#e5484d" opacity="0">10<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.4583;0.4585;0.6632;0.6634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="70" y="470" text-anchor="start" style="font-size:30px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.6632;0.6634;1.0000" values="0;0;1;1"/></text>
<text x="120" y="470" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937">度(太陽の高さ)</text>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.8681;0.8683;1.0000" values="0;0;1;1"/><rect x="330" y="450" width="600" height="70" rx="12" fill="#fef2f2" stroke="#e5484d" stroke-width="2.5"/>
<text x="346" y="474" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7f1d1d">青の光は、2° では 1% しか届かない。赤は 45%</text>
<text x="346" y="498" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">短い波長ほど散りやすい(レイリー散乱)。だから夕日は赤く、昼の空は青い</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">太陽の光が、大気を通る長さを計算する<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">真上: 一番短い。ほぼ白<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0488;0.2535;0.2537;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">30°: 通る長さ 2 倍<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2535;0.2537;0.4583;0.4585;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">10°: 5〜6 倍。青が減る<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.4583;0.4585;0.6632;0.6634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">2°: 20 倍以上。青も緑もほとんど散って、赤だけ残る<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.6632;0.6634;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:sunset-path:end -->

## このセクションの流れ

大気散乱は、物理の式が多く出てくる分野なので、見通しを先に示します。目標は、「空の色」と「遠景のかすみ」を、物理的に正しく計算することです。

最初に、大気を<strong>どう表すか</strong>を決めます（[Atmosphere Model](atmosphere-model.md)）。地球の大気を、球状の層とみなし、高さに応じて指数的に薄くなる分子（レイリー散乱）と微粒子（ミー散乱）、そして光を吸収するオゾンで表します。次に、光が大気を通るときの<strong>減り方</strong>を扱います（[Transmittance](transmittance.md)）。そして、視線に沿って<strong>散乱された光を足し合わせる</strong>式を立てます（[Single-Scattering Integral](single-scattering.md)）。この式には、散乱の方向依存性を表す<strong>位相関数</strong>が登場します（[Phase Functions](phase-function.md)）。

ここまでが単散乱（光が 1 回だけ散乱する場合）です。実際には、散乱された光がさらに散乱される<strong>多重散乱</strong>も効いてきます（[Multiple Scattering](multiple-scattering.md)）。これを毎フレーム計算するのは重いので、実用的な方式が 2 つ提案されています。Bruneton の方式は、すべてを 4 次元のテーブルに事前計算します（[Bruneton Precomputed Scattering](bruneton.md)）。Hillaire の方式は、小さな LUT を毎フレーム更新して、動的な大気にも対応します（[Hillaire 2020: Four LUTs](hillaire.md)）。最後に、地上と宇宙で、視点の位置による違いを扱います（[Ground and Space Views](ground-space.md)）。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Atmosphere Model](atmosphere-model.md) | 層・密度・散乱係数 |
| [Transmittance](transmittance.md) | 光が減衰する割合 |
| [Single-Scattering Integral](single-scattering.md) | 視線に沿って足し合わせる |
| [Phase Functions](phase-function.md) | 散乱の方向分布 |
| [Multiple Scattering](multiple-scattering.md) | 何度も散乱した光 |
| [Bruneton Precomputed Scattering](bruneton.md) | 4D のテーブル |
| [Hillaire 2020](hillaire.md) | 4 つの LUT |
| [Ground and Space Views](ground-space.md) | 視点の位置による違い |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 散乱の積分を、LUT で高速化する

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)（4 つの LUT を使う方式。公開デモの実装がある）
- Bruneton, Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum (Eurographics Symposium on Rendering 2008)
- Nishita, Sirai, Tadamura, Nakamae, "Display of the Earth Taking into Account Atmospheric Scattering", SIGGRAPH 1993（大気散乱の、CG への導入）
- O'Neil, "Accurate Atmospheric Scattering", GPU Gems 2, Chapter 16, 2005
- Wrenninge, "Art-Directable Multiple Volumetric Scattering", SIGGRAPH 2015 Talks（多重散乱の、オクターブによる近似）

## 関連ページ

- [Sky and Atmosphere](../index.md)
- [Sky Models](../sky-models/index.md)
- [Aerial Perspective and Fog](../aerial-fog/index.md)
