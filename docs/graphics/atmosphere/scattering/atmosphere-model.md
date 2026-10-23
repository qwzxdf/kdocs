---
title: Atmosphere Model
tags:
  - 描画
---

# Atmosphere Model

<strong>大気を高さごとの密度を持つ層として表します</strong>。空気分子（レイリー）、エアロゾル（ミー）、オゾンがそれぞれ違う散乱・吸収を持ちます。このページでは大気のモデルを説明します。

!!! tip "ポイント"
    - レイリー：高さとともに指数で薄くなる（約 8 km）。
    - ミー：低い所に多い（約 1.2 km）。
    - オゾン：青を吸収し、夕空の色に効く。
    - 散乱係数は波長ごとに持つ。

!!! info "このページを読む前に"
    - [Atmospheric Scattering](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

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
<strong>地球の大気は球殻</strong>です。密度は高さに対して指数的に減ります。

<div class="formula">ρ(h) = exp( −h / H )　（H：スケール ハイト）</div>

| 成分 | スケール ハイト H | 特徴 |
| --- | --- | --- |
| レイリー（空気分子） | 約 8 km | 青く散る。後ろにも前にも均等に |
| ミー（エアロゾル） | 約 1.2 km | ほぼ白く散る。前方に強い（太陽の周りのにじみ） |
| オゾン | 高さ 25 km 付近に層 | 散らさず、吸収する（朝夕の空の青みの基） |

地球の半径は 6360 km、大気の上端は 6460 km（高さ 100 km）です。

係数は 3 種類あります。散乱係数 σsは単位長さあたり散らされる割合で、RGB で値が違います。吸収係数 σaは単位長さあたり吸われる割合です。消散係数 σt = σs + σaは、減る割合の合計です。

具体的な値として Hillaire の実装で使われる地表（高さ 0）での値（単位は 1/km）を挙げます。レイリー散乱は (5.802, 13.558, 33.1) × 10⁻³ で、青が赤の約 5.7 倍と先ほどの波長の比に対応します。ミー散乱は 3.996 × 10⁻³、ミー消散は 4.44 × 10⁻³ （吸収が少し含まれる）です。オゾン吸収は (0.650, 1.881, 0.085) × 10⁻³ で、緑の吸収が最も強くこれが夕方の空に紫や青みを足します。

これらの値に高さごとの密度 ρ(h) = exp(−h / H) を掛けると、その高さでの係数になります。ミーとレイリーは指数関数的に薄くなりますが、オゾンは高さ 25 km を中心とした三角形状の分布で近似します。

レイリー散乱係数（海面） は、RGB で (5.8, 13.5, 33.1) × 10⁻⁶ /m 程度（青が大きい）、ミー散乱は (3.9, 3.9, 3.9) × 10⁻⁶ /m 程度です。

## 大気をどうモデル化するか

空の色や遠景の霞を物理的に計算するには、<strong>大気を層状の媒質</strong>としてモデル化します。惑星は球、大気はその周りの薄い殻です。

```text
         大気の上端（半径 6460 km）
       ╭──────────────────╮
      ╱  ╭────────────╮    ╲
     │  ╱   惑星        ╲    │       大気の厚さ ≈ 100 km（地球の半径の、約 1.6%）
     │ │  （半径 6360 km）│    │
      ╲  ╲              ╱    ╱
       ╰──╰────────────╯───╯
```

| 要素 | 値の例（地球） |
| --- | --- |
| 惑星の半径（地表） | 6,360 km |
| 大気の上端 | 6,460 km（地表から、100 km） |
| 地表の反射率（アルベド） | 0.3 程度（草地・土・海の平均） |

大気の厚さは 惑星の半径に比べて、薄いので 地表付近では平らな層と、みなせますが地平線の近くや宇宙から見るときは、球の曲率が重要になります。

## 3 つの成分

大気は <strong>光を散乱・吸収</strong>する、3 種類の成分でできています。

| 成分 | 大きさ | 散乱の性質 | 層の厚さ（スケール ハイト） |
| --- | --- | --- | --- |
| 空気の分子（レイリー） | 波長より、はるかに小さい | 波長の 4 乗に、反比例。前後に均等に散る | 8 km（厚い） |
| エアロゾル（ミー） | 波長と、同程度 | 波長にほぼ無関係（白っぽい）。前方に強く散る | 1.2 km（地表近く） |
| オゾン | 分子 | 散乱せず、吸収のみ。赤〜緑の一部を吸収 | 高度 25 km 付近に、集中（帯状） |

### レイリー散乱：空が青い理由

レイリー散乱の強さは 波長の 4 乗に、反比例します。青い光（波長が短い）は赤い光（波長が、長い）の約 5〜6 倍、強く散ります。太陽の光が大気を通る間に青が、あらゆる方向へ散り空全体が青く見えます。

```text
散乱の強さ ∝ 1 / λ⁴
   青（450 nm）: 1 / 450⁴ ≈ 2.4e-11
   赤（650 nm）: 1 / 650⁴ ≈ 5.6e-12      → 青は、赤の約 4.3 倍
```

### ミー散乱：霞と白い空

エアロゾルは 波長に依存せず、白く散ります。地平線の近くで空が白っぽくなるのは視線が、地表近くの濃いエアロゾルの層を、長く通るためです。

### オゾン：空の深い青

オゾンは 吸収だけを行います。赤〜緑の光を少し吸うので日没の、太陽の光が長い距離を通ったとき空の、深い青（天頂付近）が保たれます。オゾンを無視すると夕方の空が、緑がかります。

## 係数の値

Hillaire（2020）の実装が、使っている地球の大気の係数です（単位は、<strong>1 / km</strong>）。

| 成分 | 散乱係数 | 吸収係数 | RGB |
| --- | --- | --- | --- |
| レイリー | (0.005802, 0.013558, 0.0331) | 0 | 青が、最大 |
| ミー | 0.003996 | 0.00444 | 白（RGB 同じ） |
| オゾン | 0 | (0.00065, 0.001881, 0.000085) | 赤・緑を、吸う |

```hlsl
// 係数の定義。単位は、1 / km。メートル単位で、計算するなら、1000 で割る。
static const float3 kRayleighScattering = float3(0.005802, 0.013558, 0.0331);
static const float kMieScattering = 0.003996;
static const float kMieAbsorption = 0.00444;
static const float3 kOzoneAbsorption = float3(0.00065, 0.001881, 0.000085);
```

レイリーの `(0.0058, 0.0136, 0.0331)` は 赤:緑:青 ≈ 1 : 2.3 : 5.7 で 青が、約 6 倍です。この比が空の青さの源です。

## 密度の分布

各成分の密度は <strong>高度の関数</strong>です。

```hlsl
// 高度 h（km）での、各成分の、密度（地表で 1）。
float RayleighDensity(float h_km) { return exp(-h_km / 8.0); }
float MieDensity(float h_km) { return exp(-h_km / 1.2); }
// オゾンは、高度 25 km を中心とした、三角形の分布（15 km 〜 35 km の、層）。
float OzoneDensity(float h_km) {
  return (h_km < 25.0) ? saturate(h_km / 15.0 - 2.0 / 3.0) : saturate(-h_km / 15.0 + 8.0 / 3.0);
}
```

レイリーとミーは 指数関数で、高度とともに薄くなります。オゾンは特定の高度の層（25 km 付近）に、集中するので三角形の関数で近似します。

## 消散係数の合計

ある点での <strong>光を失う割合</strong>（消散係数）は、各成分の散乱と吸収の合計です。

```hlsl
// 点での、消散係数 σ_t（RGB）。散乱 + 吸収の、全成分。
float3 ExtinctionAt(float h_km) {
  float3 rayleigh = kRayleighScattering * RayleighDensity(h_km);
  float mie = (kMieScattering + kMieAbsorption) * MieDensity(h_km);
  float3 ozone = kOzoneAbsorption * OzoneDensity(h_km);
  return rayleigh + mie + ozone;
}
```

散乱だけが 視線の方向へ、光を足す（空の色を作る）のに、使われる一方、消散（散乱 + 吸収）は透過率（光が、失われる量）に使われます（[Transmittance](transmittance.md)）。

## 大気のパラメーターを変える

係数を変えると <strong>別の惑星</strong>や、天候を表現できます。

| 変更 | 効果 |
| --- | --- |
| ミー散乱を増やす | 霞んだ空（スモッグ、湿気）。地平線が白い |
| ミー散乱を減らす | 澄んだ空（高山、乾燥）。青が濃く遠くまで見える |
| レイリーのスケール ハイトを、変える | 大気の厚さの感じ |
| オゾンをゼロに | 夕方の空が、緑がかる |
| 惑星の半径を変える | 地平線の、見え方。小さい惑星は地平線が近く曲がって見える |

火星の空（赤い塵が多い）は ミー散乱が強く、赤いエアロゾルを持つモデルで、表現できます。

## よくあるミス

??? failure "夕焼けが、赤くならない"
    <strong>オゾンの吸収</strong>と 波長ごとの散乱係数を入れる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 高さごとの密度と、波長ごとの係数

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)
- Bruneton, Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum (Eurographics Symposium on Rendering 2008)
- Bruneton, "A Qualitative and Quantitative Evaluation of 8 Clear Sky Models", IEEE Transactions on Visualization and Computer Graphics, Vol. 23, No. 12, 2017
- Nishita, Sirai, Tadamura, Nakamae, "Display of the Earth Taking into Account Atmospheric Scattering", SIGGRAPH 1993
- O'Neil, "Accurate Atmospheric Scattering", GPU Gems 2, Chapter 16, 2005

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Transmittance](transmittance.md)
