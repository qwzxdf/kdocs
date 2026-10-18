---
title: Atmosphere Model
tags:
  - 描画
---

# Atmosphere Model

**大気を、高さごとの密度を持つ層として表します**。**空気分子（レイリー）、エアロゾル（ミー）、オゾンが、それぞれ違う散乱・吸収を持ちます**。このページでは、**大気のモデル**を説明します。

!!! tip "ポイント"
    - **レイリー：高さとともに指数で薄くなる（約 8 km）**。
    - **ミー：低い所に多い（約 1.2 km）**。
    - **オゾン：青を吸収し、夕空の色に効く**。
    - **散乱係数は、波長ごとに持つ**。

<!-- fig:rayleigh-wavelength:begin -->

<svg class="fig illust motion" data-fig="rayleigh-wavelength" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-rayleigh-wavelength" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">レイリー散乱: 散る量は、波長の 4 乗に反比例する。だから、昼の空は青く、夕日は赤い</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">波長 400〜700 nm の光。散る量を計算して、空の色(散った光)と、夕日の色(残った光)を、作る</text>
<rect x="30" y="96" width="560" height="200" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 波長ごとに散る量(550 nm を 1 とする)</text>
<rect x="54.0" y="120.0" width="30.5" height="150.0" fill="#02001c" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="0;0;1;1"/></rect>
<text x="70.25" y="288" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">400</text>
<rect x="86.5" y="146.59" width="30.5" height="123.41" fill="#0d0066" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0679;0.0681;1.0000" values="0;0;1;1"/></rect>
<rect x="119.0" y="167.55" width="30.5" height="102.45" fill="#1f01e6" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0722;0.0723;1.0000" values="0;0;1;1"/></rect>
<rect x="151.5" y="184.24" width="30.5" height="85.76" fill="#1f06e6" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0764;0.0766;1.0000" values="0;0;1;1"/></rect>
<text x="167.75" y="288" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">460</text>
<rect x="184.0" y="197.66" width="30.5" height="72.34" fill="#0d1c66" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0807;0.0809;1.0000" values="0;0;1;1"/></rect>
<rect x="216.5" y="208.56" width="30.5" height="61.44" fill="#04541c" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0849;0.0851;1.0000" values="0;0;1;1"/></rect>
<rect x="249.0" y="217.48" width="30.5" height="52.52" fill="#0aa90e" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0892;0.0894;1.0000" values="0;0;1;1"/></rect>
<text x="265.25" y="288" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">520</text>
<rect x="281.5" y="224.84" width="30.5" height="45.16" fill="#27e30d" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0934;0.0936;1.0000" values="0;0;1;1"/></rect>
<rect x="314.0" y="230.95" width="30.5" height="39.05" fill="#68cd0d" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0977;0.0979;1.0000" values="0;0;1;1"/></rect>
<rect x="346.5" y="236.07" width="30.5" height="33.93" fill="#bc7d0d" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1021;1.0000" values="0;0;1;1"/></rect>
<text x="362.75" y="288" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">580</text>
<rect x="379.0" y="240.37" width="30.5" height="29.63" fill="#e6340d" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1062;0.1064;1.0000" values="0;0;1;1"/></rect>
<rect x="411.5" y="244.01" width="30.5" height="25.99" fill="#bc0e0d" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1105;0.1106;1.0000" values="0;0;1;1"/></rect>
<rect x="444.0" y="247.11" width="30.5" height="22.89" fill="#68030d" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1147;0.1149;1.0000" values="0;0;1;1"/></rect>
<text x="460.25" y="288" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">640</text>
<rect x="476.5" y="249.76" width="30.5" height="20.24" fill="#27000d" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1190;0.1191;1.0000" values="0;0;1;1"/></rect>
<rect x="509.0" y="252.04" width="30.5" height="17.96" fill="#0a000d" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1232;0.1234;1.0000" values="0;0;1;1"/></rect>
<rect x="541.5" y="254.01" width="30.5" height="15.99" fill="#02000d" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1275;0.1277;1.0000" values="0;0;1;1"/></rect>
<text x="557.75" y="288" text-anchor="middle" style="font-size:9px;font-weight:500;fill:#64748b">700</text>
<text x="54" y="118" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb" opacity="0">400 nm(青)は 700 nm(赤)の 9.4 倍 散る<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1317;0.1319;1.0000" values="0;0;1;1"/></text>
<rect x="610" y="96" width="320" height="200" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="610" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 昼の空の色(散った光)</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1658;0.1660;1.0000" values="0;0;1;1"/><rect x="630" y="130" width="280" height="90" fill="#cfdaff" stroke="#94a3b8" stroke-width="1.5"/>
<text x="630" y="244" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">R 0.63 / G 0.71 / B 1.00</text>
<text x="630" y="268" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">散る量の多い、短い波長が、空の色になる</text>
</g>
<rect x="30" y="316" width="900" height="150" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="30" y="306" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">③ 太陽の光が、空気の中を通った後の色(空気の量 = 天頂の何倍か)</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2934;0.2936;1.0000" values="0;0;1;1"/><circle cx="86" cy="388" r="32" fill="#fff4cb" stroke="#334155" stroke-width="2"/>
<text x="132" y="372" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">空気なし</text>
<text x="132" y="394" text-anchor="start" style="font-size:11px;font-weight:500;fill:#1f2937">R 1.00 G 0.91 B 0.61</text>
<text x="132" y="414" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">元の太陽(白)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3956;0.3957;1.0000" values="0;0;1;1"/><circle cx="306" cy="388" r="32" fill="#ffeba2" stroke="#334155" stroke-width="2"/>
<text x="352" y="372" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">空気 1 倍</text>
<text x="352" y="394" text-anchor="start" style="font-size:11px;font-weight:500;fill:#1f2937">R 1.00 G 0.84 B 0.37</text>
<text x="352" y="414" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">昼(少し黄色)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4977;0.4979;1.0000" values="0;0;1;1"/><circle cx="526" cy="388" r="32" fill="#ffc644" stroke="#334155" stroke-width="2"/>
<text x="572" y="372" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">空気 5 倍</text>
<text x="572" y="394" text-anchor="start" style="font-size:11px;font-weight:500;fill:#1f2937">R 1.00 G 0.57 B 0.05</text>
<text x="572" y="414" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">夕方(橙)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;1.0000" values="0;0;1;1"/><circle cx="746" cy="388" r="32" fill="#ff9411" stroke="#334155" stroke-width="2"/>
<text x="792" y="372" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">空気 12 倍</text>
<text x="792" y="394" text-anchor="start" style="font-size:11px;font-weight:500;fill:#1f2937">R 1.00 G 0.30 B 0.00</text>
<text x="792" y="414" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">夕焼け(赤)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7232;0.7234;1.0000" values="0;0;1;1"/><rect x="40" y="478" width="880" height="40" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="502" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">青い光は、空の方へ散り、赤い光は、太陽の方向に残る</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光の波長によって、空気で散る量が違う(波長の 4 乗に反比例)<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">短い青は、赤の約 9 倍 散る<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0638;0.1658;0.1660;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">散った光を見ると、空は青い<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1658;0.1660;0.2934;0.2936;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">空気を長く通った太陽は、青が抜けて、赤くなる<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2934;0.2936;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:rayleigh-wavelength:end -->

## 大気のモデル
**地球の大気は球殻**です。**密度は高さに対して指数的に減ります**。

<div class="formula">ρ(h) = exp( −h / H )　（H：スケール ハイト）</div>

| 成分 | スケール ハイト H | 特徴 |
| --- | --- | --- |
| <strong>レイリー（空気分子）</strong> | **約 8 km** | **青く散る。後ろにも前にも均等に** |
| <strong>ミー（エアロゾル）</strong> | **約 1.2 km** | <strong>ほぼ白く散る。前方に強い（太陽の周りのにじみ）</strong> |
| **オゾン** | **高さ 25 km 付近に層** | **散らさず、吸収する**（**朝夕の空の青みの基**） |

**地球の半径は 6360 km、大気の上端は 6460 km**（高さ 100 km）です。

係数は 3 種類あります。<strong>散乱係数 σs</strong>は、単位長さあたり散らされる割合で、RGB で値が違います。<strong>吸収係数 σa</strong>は、単位長さあたり吸われる割合です。<strong>消散係数 σt = σs + σa</strong>は、減る割合の合計です。

具体的な値として、Hillaire の実装で使われる地表（高さ 0）での値（単位は 1/km）を挙げます。レイリー散乱は (5.802, 13.558, 33.1) × 10⁻³ で、青が赤の約 5.7 倍と、先ほどの波長の比に対応します。ミー散乱は 3.996 × 10⁻³、ミー消散は 4.44 × 10⁻³ （吸収が少し含まれる）です。オゾン吸収は (0.650, 1.881, 0.085) × 10⁻³ で、緑の吸収が最も強く、これが夕方の空に紫や青みを足します。

これらの値に、高さごとの密度 ρ(h) = exp(−h / H) を掛けると、その高さでの係数になります。ミーとレイリーは指数関数的に薄くなりますが、オゾンは高さ 25 km を中心とした三角形状の分布で近似します。

<strong>レイリー散乱係数（海面）</strong> は、**RGB で (5.8, 13.5, 33.1) × 10⁻⁶ /m** 程度（**青が大きい**）、**ミー散乱は (3.9, 3.9, 3.9) × 10⁻⁶ /m** 程度です。

## よくあるミス

??? failure "夕焼けが、赤くならない"
    **オゾンの吸収**と **波長ごとの散乱係数**を**入れる**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **高さごとの密度と、波長ごとの係数**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Transmittance](transmittance.md)
