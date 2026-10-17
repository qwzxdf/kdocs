---
title: Atmospheric Scattering
tags:
  - 描画
---

# Atmospheric Scattering

**空が青く、夕焼けが赤いのは、大気中の分子や粒子が、光を散乱させるため**です。**この散乱を計算すると、物理的に正しい空が作れます**。このセクションでは、**空が青い理由・大気のモデル・透過率・単散乱・位相関数・多重散乱・Bruneton の事前計算・Hillaire の 4 つの LUT・地面と宇宙**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **散乱 ＝ 光が、粒子に当たって、方向を変える**。
    - **レイリー散乱（空気分子）は青を強く散らす**。
    - **ミー散乱（エアロゾル）は、波長にあまり依存しない**。
    - **事前計算（LUT）で、リアルタイムにできる**。

## なぜ空は青いか
**太陽光は白色**（全波長を含む）ですが**大気の分子に当たると短い波長（青）ほど強く散らされます**。

<div class="formula">レイリー散乱の強さ ∝ 1 / λ⁴</div>

具体的な数字で見ます。700 nm（赤）の散乱の強さを 1.0 とすると、550 nm（緑）は約 2.6、450 nm（青）は約 5.9 になります。青い光は赤い光の約 6 倍も散らされるので、空全体が青く見えます。

**青い光が全方向に散って空が青く見えます**。**夕方は太陽の光が大気を長く通り、青が散り尽くして赤だけが残る**ので、**太陽が赤く、空が赤く染まります**。

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

<svg class="fig illust motion" data-fig="sunset-path" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-sunset-path" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">夕焼け:太陽が低いほど、光が大気を長く通って青が散り尽くす</text>
<rect x="40" y="150" width="700" height="170" fill="#6fb3ff"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0870;0.1087;0.1304;0.1522;0.1739;0.1957;0.2174;0.2391;0.2609;0.2826;0.3043;0.3261;0.3478;0.3696;0.3913;0.4130;0.4348;0.4565;0.4783;0.5000;0.5217;0.5435;0.5652;0.5870;0.6087;0.6304;0.6522;0.6739;0.6957;0.7174;0.7391;1.0000" values="#6fb3ff;#6fb3ff;#6fb3fe;#71b2fd;#73b2fa;#76b1f6;#7ab0f2;#7eafec;#83ade6;#88ace0;#8eaad8;#94a8d1;#9ba7c8;#a2a5c0;#a9a3b7;#b0a1ae;#b79ea6;#be9c9d;#c59a94;#cc988b;#d39683;#da957a;#e09373;#e6916b;#eb9065;#f08e5f;#f48d59;#f88c55;#fb8b51;#fd8b4e;#ff8a4d;#ff8a4c;#ff8a4c"/></rect>
<rect x="40" y="320" width="700" height="40" fill="#3f5d3a"/>
<text x="46" y="142" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">大気の層（上端）</text>
<line x1="40" y1="150" x2="740" y2="150" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="5 4"/>
<circle cx="390" cy="320" r="7" fill="#e5484d"/>
<text x="402" y="342" text-anchor="start" style="font-size:13px;font-weight:700;fill:#ffffff">観測者</text>
<circle cx="500" cy="100" r="22" fill="#fff3b0" stroke="#f59e0b" stroke-width="2"><animate attributeName="cx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.1087;0.1304;0.1522;0.1739;0.1957;0.2174;0.2391;0.2609;0.2826;0.3043;0.3261;0.3478;0.3696;0.3913;0.4130;0.4348;0.4565;0.4783;0.5000;0.5217;0.5435;0.5652;0.5870;0.6087;0.6304;0.6522;0.6739;0.6957;0.7174;0.7391;1.0000" values="500;500;447.3;461.43;475.41;489.23;502.87;516.29;529.46;542.38;555;567.31;579.28;590.89;602.12;612.94;623.35;633.3;642.79;651.81;660.32;668.32;675.79;682.71;689.08;694.88;700.1;704.73;708.76;712.18;714.99;717.18;718.74;718.74"/><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.1087;0.1304;0.1522;0.1739;0.1957;0.2174;0.2391;0.2609;0.2826;0.3043;0.3261;0.3478;0.3696;0.3913;0.4130;0.4348;0.4565;0.4783;0.5000;0.5217;0.5435;0.5652;0.5870;0.6087;0.6304;0.6522;0.6739;0.6957;0.7174;0.7391;1.0000" values="100;100;-4.99;-2.18;1.24;5.27;9.9;15.12;20.92;27.29;34.21;41.68;49.68;58.19;67.21;76.7;86.65;97.06;107.88;119.11;130.72;142.69;155;167.62;180.54;193.71;207.13;220.77;234.59;248.57;262.7;276.93;291.24;291.24"/></circle>
<line x1="500" y1="150" x2="390" y2="320" stroke="#ffffff" stroke-width="5"><animate attributeName="x1" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.1087;0.1304;0.1522;0.1739;0.1957;0.2174;0.2391;0.2609;0.2826;0.3043;0.3261;0.3478;0.3696;0.3913;0.4130;0.4348;0.4565;0.4783;0.5000;0.5217;0.5435;0.5652;0.5870;0.6087;0.6304;0.6522;0.6739;0.6957;0.7174;0.7391;1.0000" values="500;500;419.98;427.69;435.55;443.6;451.87;460.42;469.27;478.5;488.15;498.3;509.04;520.45;532.65;545.78;560;575.52;592.6;611.55;632.79;656.85;684.45;716.57;735;735;735;735;735;735;735;735;735;735"/><animate attributeName="stroke" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0870;0.1087;0.1304;0.1522;0.1739;0.1957;0.2174;0.2391;0.2609;0.2826;0.3043;0.3261;0.3478;0.3696;0.3913;0.4130;0.4348;0.4565;0.4783;0.5000;0.5217;0.5435;0.5652;0.5870;0.6087;0.6304;0.6522;0.6739;0.6957;0.7174;0.7391;1.0000" values="#ffffff;#ffffff;#fffefe;#fffdfc;#fffaf9;#fff6f5;#fff2f0;#ffece9;#ffe6e2;#ffe0da;#ffd9d2;#ffd1c9;#ffc9bf;#ffc0b5;#ffb8ab;#ffafa1;#ffa696;#ff9d8c;#ff9482;#ff8c78;#ff836e;#ff7b64;#ff735b;#ff6c53;#ff664b;#ff6044;#ff5a3d;#ff5638;#ff5234;#ff4f31;#ff4e2f;#ff4d2e;#ff4d2e"/></line>
<text x="540" y="80" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">光が大気を通る距離</text>
<rect x="540" y="90" width="190" height="14" fill="#f1f5f9" stroke="#94a3b8"/>
<rect x="540" y="90" width="17" height="14" fill="#ff6b3d"><animate attributeName="width" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0870;0.1087;0.1304;0.1522;0.1739;0.1957;0.2174;0.2391;0.2609;0.2826;0.3043;0.3261;0.3478;0.3696;0.3913;0.4130;0.4348;0.4565;0.4783;0.5000;0.5217;0.5435;0.5652;0.5870;0.6087;0.6304;0.6522;0.6739;0.6957;0.7174;0.7391;1.0000" values="17;17;17.15;17.33;17.55;17.82;18.12;18.47;18.87;19.33;19.85;20.44;21.1;21.85;22.71;23.68;24.78;26.05;27.5;29.19;31.16;33.48;36.26;39.61;43.75;48.95;55.67;64.69;77.35;96.41;128.26;190;190"/></rect>
<text x="40" y="392" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 80°:大気を通る距離 = 1.0 倍<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2605;0.2609;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="392" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 60°:大気を通る距離 = 1.1 倍<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;0.4344;0.4348;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="392" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 40°:大気を通る距離 = 1.5 倍<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;0.6083;0.6087;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="392" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 20°:大気を通る距離 = 2.9 倍<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6083;0.6087;0.6953;0.6957;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="392" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 10°:大気を通る距離 = 5.7 倍<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6953;0.6957;0.7388;0.7391;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="392" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">太陽の高さ 5°:大気を通る距離 = 11.3 倍<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.7388;0.7391;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">昼:光は大気を短く通る → 青い光が散って空は青い<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;1.0000" values="1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">夕方:長く通る間に青が散り尽くし、赤だけが残って届く<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;1.0000;1.0000" values="0;0;1;1;0"/></text>
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
    - [x] **散乱の積分を、LUT で高速化する**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [大気](../index.md)
- [Sky Models](../sky-models/index.md)
- [空気遠近法](../aerial-fog/index.md)
