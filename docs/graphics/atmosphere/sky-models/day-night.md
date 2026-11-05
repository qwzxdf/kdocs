---
title: Day-Night Cycle
tags:
  - 描画
---

# Day-Night Cycle

ゲームの時計を進めると太陽が動き空の色、光の色、影の向き露出までが一緒に変わります。ばらばらに作ると「夕焼けなのに影が短い」「空は暗いのに光は強い」といった食い違いが出ます。そこで、時刻を 1 つの入力にしてそこから全部を導きます。このページでは時刻から太陽の向きを決める式、昼と夜の明るさの桁、薄明の長さ太陽の色、露出の目標までを数字を確かめながら説明し、最後に HLSL の完成形を載せます。

!!! tip "ポイント"
    - 時刻から決めるのは緯度、日付、時刻の 3 つから出る太陽の高度と方位である。残りはすべてそこから導く。
    - 昼と月のない夜の明るさの差は、約 26 段（EV）ある。固定の露出では扱えず自動露出が要る。
    - 太陽の色は大気を通る長さ（空気量）で決まる。青から先に減るので低い太陽は赤くなる。色を手で設定しなくてよい。
    - 日没後も空はしばらく明るい。市民薄明は日没から約 30 分（北緯 35 度の春分）である。
    - 大気の LUT のうち時刻で更新が要るのは、空の見た目のもの（Sky-View、Aerial Perspective、多重散乱）である。透過率の LUT は大気の係数を変えたときだけ更新する。

!!! info "このページを読む前に"
    - [Sky Models](index.md)（このセクション全体の地図と読む順番）

<!-- fig:day-night:begin -->

<svg class="fig illust motion" data-fig="day-night" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-day-night" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">昼夜のサイクル:時刻から、空・太陽・光の色がいっせいに変わる</text>
<rect x="40" y="70" width="700" height="230" fill="#0b1224"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2738;0.3238;0.4571;0.5905;0.6571;0.7071;0.7571;0.8571;1.0000" values="#0b1224;#0b1224;#0b1224;#f59e8b;#7dd3fc;#38bdf8;#7dd3fc;#fb923c;#312e81;#0b1224;#0b1224;#0b1224"/></rect>
<rect x="40" y="190" width="700" height="110" fill="#fb923c" opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2738;0.3238;0.5905;0.6571;0.7071;0.8571;1.0000" values="0;0;0;0.7;0;0;0.8;0;0;0"/></rect>
<circle cx="70" cy="84" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="167" cy="137" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="264" cy="190" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="361" cy="113" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="458" cy="166" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="555" cy="89" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="652" cy="142" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="109" cy="195" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="206" cy="118" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="303" cy="171" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="400" cy="94" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="497" cy="147" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="594" cy="200" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="691" cy="123" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="148" cy="176" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="245" cy="99" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="342" cy="152" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="439" cy="205" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="536" cy="128" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="633" cy="181" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="90" cy="104" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="187" cy="157" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="284" cy="210" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="381" cy="133" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="478" cy="186" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<circle cx="575" cy="109" r="1.8" fill="#ffffff" opacity="1"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0571;0.2238;0.2905;0.6571;0.7238;0.8571;1.0000" values="1;1;1;0;0;1;1;1"/></circle>
<rect x="40" y="300" width="700" height="70" fill="#334155"/>
<circle cx="40" cy="300" r="22" fill="#fde68a" opacity="0"><animate attributeName="cx" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2569;0.2571;0.2671;0.2771;0.2871;0.2971;0.3071;0.3171;0.3271;0.3371;0.3471;0.3571;0.3671;0.3771;0.3871;0.3971;0.4071;0.4171;0.4271;0.4371;0.4471;0.4571;0.4671;0.4771;0.4871;0.4971;0.5071;0.5171;0.5271;0.5371;0.5471;0.5571;0.5671;0.5771;0.5871;0.5971;0.6071;0.6171;0.6271;0.6371;0.6471;0.6571;1.0000" values="40;40;70;86;102;118;134;150;166;182;198;214;230;246;262;278;294;310;326;342;358;374;390;406;422;438;454;470;486;502;518;534;550;566;582;598;614;630;646;662;678;694;710;710"/><animate attributeName="cy" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2571;0.2671;0.2771;0.2871;0.2971;0.3071;0.3171;0.3271;0.3371;0.3471;0.3571;0.3671;0.3771;0.3871;0.3971;0.4071;0.4171;0.4271;0.4371;0.4471;0.4571;0.4671;0.4771;0.4871;0.4971;0.5071;0.5171;0.5271;0.5371;0.5471;0.5571;0.5671;0.5771;0.5871;0.5971;0.6071;0.6171;0.6271;0.6371;0.6471;0.6571;1.0000" values="300;300;285.88;271.84;257.98;244.38;231.12;218.28;205.95;194.2;183.1;172.72;163.13;154.38;146.52;139.62;133.7;128.81;124.97;122.22;120.55;120;120.55;122.22;124.97;128.81;133.7;139.62;146.52;154.38;163.13;172.72;183.1;194.2;205.95;218.28;231.12;244.38;257.98;271.84;285.88;300;300"/><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2569;0.2571;0.6569;0.6571;1.0000" values="0;0;1;1;0;0"/></circle>
<circle cx="40" cy="300" r="16" fill="#e2e8f0" opacity="0"><animate attributeName="cx" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.6569;0.6571;0.6671;0.6771;0.6871;0.6971;0.7071;0.7171;0.7271;0.7371;0.7471;0.7571;0.7671;0.7771;0.7871;0.7971;0.8071;0.8171;0.8271;0.8371;0.8471;0.8571;1.0000" values="40;40;70;86;102;118;134;150;166;182;198;214;230;246;262;278;294;310;326;342;358;374;390;390"/><animate attributeName="cy" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.6571;0.6671;0.6771;0.6871;0.6971;0.7071;0.7171;0.7271;0.7371;0.7471;0.7571;0.7671;0.7771;0.7871;0.7971;0.8071;0.8171;0.8271;0.8371;0.8471;0.8571;1.0000" values="300;300;285.88;271.84;257.98;244.38;231.12;218.28;205.95;194.2;183.1;172.72;163.13;154.38;146.52;139.62;133.7;128.81;124.97;122.22;120.55;120;120"/><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.6569;0.6571;1.0000" values="0;0;1;1"/></circle>
<text x="40" y="52" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">夜（0〜6 時）:月と星<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;0.2569;0.2571;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">日の出:空がオレンジに染まる<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.2569;0.2571;0.3236;0.3238;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">昼:青い空。太陽が高い（白い光）<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3236;0.3238;0.5902;0.5905;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">夕方:再びオレンジ、影が長い<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.5902;0.5905;0.7069;0.7071;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="52" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">夜:星が出る<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.7069;0.7071;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">1 つの「時刻」から、太陽の位置・空の色・光の色・星を計算する。環境光（IBL）も、時刻に合わせて更新する。</text>
</svg>

<!-- fig:day-night:end -->

## 読んだ資料 {#sources}

- Sébastien Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", EGSR 2020。本文を第 7 節の性能の途中まで読みました。表 2 の詳細、結論、参考文献は読んでいません。
- Sébastien Lagarde, Charles de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014 コース ノート。太陽の節（4.6）、表 11、EV の節（4.3 あたり）を読みました。ノート全体（122 ページ）は読んでいません。
- Eric Bruneton, Fabrice Neyret, "Precomputed Atmospheric Scattering"（2008）。係数と透過率の式を使いました。詳しくは [Bruneton Precomputed Scattering](../scattering/bruneton.md) を参照してください。
- Wikipedia "Lux" の照度の表。要約を取得して値を書き写しました（一次資料ではありません）。

太陽の位置の式（赤緯と時角の式）、薄明の定義（−6°、−12°、−18°）、空気量の式（Kasten-Young）は、一般的な知識で今回は一次資料を読んでいません。そう書いてある所で区別します。

## 時刻から太陽の向きを決める {#sun-position}

太陽の向きは緯度 φ、赤緯 δ（日付で決まる）、時角 H（時刻で決まる）の 3 つから出ます。

```text
sin(高度) = sin φ sin δ + cos φ cos δ cos H
H = 15° × (時刻 − 12)                （正午が 0、午後が正）
δ ≈ −23.44° × cos(2π (N + 10) / 365)   （N は年初からの日数。近似式）
```

方位は北から時計回りで `atan2(−cos δ sin H, sin δ cos φ − cos δ sin φ cos H)` です。分子と分母に cos(高度) を掛けた形で渡すと象限が自然に決まります。均時差（地球の公転の不均一による太陽時のずれ）と経度のずれは無視しています。ゲームの昼夜ならこれで足ります。

<svg class="fig flow" viewBox="0 0 660 262" role="img" aria-label="太陽の高度の 1 日"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">北緯 35 度の太陽の高度(度)。一日の中の動き</text><line x1="60" y1="226" x2="620" y2="226" stroke="#94a3b8"/><line x1="60" y1="36" x2="60" y2="226" stroke="#94a3b8"/><line x1="60" y1="191.2" x2="620" y2="191.2" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.4"/><text x="54" y="195.16666666666669" text-anchor="end" font-size="10" fill="currentColor">-18</text><line x1="60" y1="181.7" x2="620" y2="181.7" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.4"/><text x="54" y="185.66666666666666" text-anchor="end" font-size="10" fill="currentColor">-12</text><line x1="60" y1="172.2" x2="620" y2="172.2" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.4"/><text x="54" y="176.16666666666669" text-anchor="end" font-size="10" fill="currentColor">-6</text><line x1="60" y1="162.7" x2="620" y2="162.7" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.9"/><text x="54" y="166.66666666666669" text-anchor="end" font-size="10" fill="currentColor">0</text><line x1="60" y1="115.2" x2="620" y2="115.2" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.4"/><text x="54" y="119.16666666666666" text-anchor="end" font-size="10" fill="currentColor">30</text><line x1="60" y1="67.7" x2="620" y2="67.7" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.4"/><text x="54" y="71.66666666666666" text-anchor="end" font-size="10" fill="currentColor">60</text><line x1="60" y1="20.2" x2="620" y2="20.2" stroke="#94a3b8" stroke-dasharray="2 4" opacity="0.4"/><text x="54" y="24.166666666666686" text-anchor="end" font-size="10" fill="currentColor">90</text><rect x="60" y="162.7" width="560" height="9.5" fill="rgba(229,170,40,0.28)" opacity="0.5"/><text x="616" y="171.41666666666666" text-anchor="end" font-size="10" fill="currentColor">市民薄明</text><polyline points="60.0,286.9 65.8,286.1 71.7,284.2 77.5,281.2 83.3,277.6 89.2,273.5 95.0,269.2 100.8,264.7 106.7,260.1 112.5,255.4 118.3,250.6 124.2,245.8 130.0,240.9 135.8,236.1 141.7,231.2 147.5,226.3 153.3,221.5 159.2,216.7 165.0,211.8 170.8,207.0 176.7,202.3 182.5,197.5 188.3,192.8 194.2,188.2 200.0,183.5 205.8,179.0 211.7,174.5 217.5,170.1 223.3,165.7 229.2,161.4 235.0,157.3 240.8,153.2 246.7,149.2 252.5,145.4 258.3,141.7 264.2,138.1 270.0,134.7 275.8,131.5 281.7,128.5 287.5,125.7 293.3,123.1 299.2,120.7 305.0,118.7 310.8,116.9 316.7,115.4 322.5,114.2 328.3,113.4 334.2,112.9 340.0,112.7 345.8,112.9 351.7,113.4 357.5,114.2 363.3,115.4 369.2,116.9 375.0,118.7 380.8,120.7 386.7,123.1 392.5,125.7 398.3,128.5 404.2,131.5 410.0,134.7 415.8,138.1 421.7,141.7 427.5,145.4 433.3,149.2 439.2,153.2 445.0,157.3 450.8,161.4 456.7,165.7 462.5,170.1 468.3,174.5 474.2,179.0 480.0,183.5 485.8,188.2 491.7,192.8 497.5,197.5 503.3,202.3 509.2,207.0 515.0,211.8 520.8,216.7 526.7,221.5 532.5,226.3 538.3,231.2 544.2,236.1 550.0,240.9 555.8,245.8 561.7,250.6 567.5,255.4 573.3,260.1 579.2,264.7 585.0,269.2 590.8,273.5 596.7,277.6 602.5,281.2 608.3,284.2 614.2,286.1 620.0,286.9" fill="none" stroke="#4c8bf5" stroke-width="2.5"/><polyline points="60.0,251.2 65.8,250.9 71.7,250.1 77.5,248.7 83.3,246.8 89.2,244.5 95.0,241.8 100.8,238.7 106.7,235.4 112.5,231.8 118.3,227.9 124.2,223.9 130.0,219.7 135.8,215.4 141.7,211.0 147.5,206.5 153.3,201.8 159.2,197.2 165.0,192.5 170.8,187.7 176.7,182.9 182.5,178.1 188.3,173.2 194.2,168.4 200.0,163.5 205.8,158.6 211.7,153.8 217.5,148.9 223.3,144.1 229.2,139.4 235.0,134.6 240.8,129.9 246.7,125.3 252.5,120.7 258.3,116.3 264.2,111.9 270.0,107.6 275.8,103.5 281.7,99.6 287.5,95.8 293.3,92.3 299.2,89.0 305.0,86.1 310.8,83.4 316.7,81.2 322.5,79.4 328.3,78.1 334.2,77.3 340.0,77.0 345.8,77.3 351.7,78.1 357.5,79.4 363.3,81.2 369.2,83.4 375.0,86.1 380.8,89.0 386.7,92.3 392.5,95.8 398.3,99.6 404.2,103.5 410.0,107.6 415.8,111.9 421.7,116.3 427.5,120.7 433.3,125.3 439.2,129.9 445.0,134.6 450.8,139.4 456.7,144.1 462.5,148.9 468.3,153.8 474.2,158.6 480.0,163.5 485.8,168.4 491.7,173.2 497.5,178.1 503.3,182.9 509.2,187.7 515.0,192.5 520.8,197.2 526.7,201.8 532.5,206.5 538.3,211.0 544.2,215.4 550.0,219.7 555.8,223.9 561.7,227.9 567.5,231.8 573.3,235.4 579.2,238.7 585.0,241.8 590.8,244.5 596.7,246.8 602.5,248.7 608.3,250.1 614.2,250.9 620.0,251.2" fill="none" stroke="#4caf7a" stroke-width="2.5"/><polyline points="60.0,212.6 65.8,212.5 71.7,212.0 77.5,211.1 83.3,209.9 89.2,208.4 95.0,206.7 100.8,204.6 106.7,202.3 112.5,199.7 118.3,196.9 124.2,193.8 130.0,190.6 135.8,187.2 141.7,183.7 147.5,180.0 153.3,176.1 159.2,172.1 165.0,168.1 170.8,163.9 176.7,159.6 182.5,155.3 188.3,150.8 194.2,146.3 200.0,141.8 205.8,137.2 211.7,132.5 217.5,127.8 223.3,123.1 229.2,118.3 235.0,113.5 240.8,108.7 246.7,103.8 252.5,99.0 258.3,94.1 264.2,89.3 270.0,84.4 275.8,79.6 281.7,74.7 287.5,70.0 293.3,65.3 299.2,60.6 305.0,56.1 310.8,51.8 316.7,47.8 322.5,44.1 328.3,41.2 334.2,39.2 340.0,38.5 345.8,39.2 351.7,41.2 357.5,44.1 363.3,47.8 369.2,51.8 375.0,56.1 380.8,60.6 386.7,65.3 392.5,70.0 398.3,74.7 404.2,79.6 410.0,84.4 415.8,89.3 421.7,94.1 427.5,99.0 433.3,103.8 439.2,108.7 445.0,113.5 450.8,118.3 456.7,123.1 462.5,127.8 468.3,132.5 474.2,137.2 480.0,141.8 485.8,146.3 491.7,150.8 497.5,155.3 503.3,159.6 509.2,163.9 515.0,168.1 520.8,172.1 526.7,176.1 532.5,180.0 538.3,183.7 544.2,187.2 550.0,190.6 555.8,193.8 561.7,196.9 567.5,199.7 573.3,202.3 579.2,204.6 585.0,206.7 590.8,208.4 596.7,209.9 602.5,211.1 608.3,212.0 614.2,212.5 620.0,212.6" fill="none" stroke="#e5aa28" stroke-width="2.5"/><text x="340.0" y="32.47" text-anchor="middle" font-size="10" fill="currentColor">夏至 78.4°</text><text x="340.0" y="71.02416666666667" text-anchor="middle" font-size="10" fill="currentColor">春分 54.1°</text><text x="340.0" y="106.69666666666666" text-anchor="middle" font-size="10" fill="currentColor">冬至 31.6°</text><text x="60.0" y="242" text-anchor="middle" font-size="10" fill="currentColor">0</text><text x="200.0" y="242" text-anchor="middle" font-size="10" fill="currentColor">6</text><text x="340.0" y="242" text-anchor="middle" font-size="10" fill="currentColor">12</text><text x="480.0" y="242" text-anchor="middle" font-size="10" fill="currentColor">18</text><text x="620.0" y="242" text-anchor="middle" font-size="10" fill="currentColor">24</text><text x="340.0" y="258" text-anchor="middle" font-size="10" fill="currentColor">時刻</text></svg>

北緯 35 度で C++ に計算させると、正午の高度は冬至が 31.56 度、夏至が 78.44 度で理論値（90 − 緯度 ± 23.44）と一致しました。昼の長さは冬至 9.6 時間、夏至 14.4 時間です。春分と秋分は約 12 時間で、日の出は 6 時ごろです。

方向ベクトルは東を +x、上を +y、北を +z とします。春分の正午は `(0, 0.81, −0.59)` で真南から高さ 54 度の方向です。南向きなので z が負になります。

季節を入れるのは簡単です。日付を動かせば赤緯が変わり太陽の通り道が上下します。ゲームの時間で 1 年を回さなくても、場面ごとに日付を固定するだけで、「夏の昼」と「冬の昼」が作り分けられます。

## 昼と夜の長さ薄明 {#twilight}

日没後も空はしばらく明るいままです。大気の高い層に太陽の光がまだ当たっていて、そこで散乱した光が地上に届くからです。太陽の高度で 3 段階に分けるのが一般的な定義です。

- 市民薄明（高度 0° 〜 −6°）: 屋外で活動できる明るさ。
- 航海薄明（−6° 〜 −12°）: 明るい星が見え地平線がぼんやり見える。
- 天文薄明（−12° 〜 −18°）: ほぼ夜。かすかな明るさが残る。

C++ で日没からそれぞれの高度に達するまでの時間を計算しました（結果は、末尾の実行結果にあります）。

赤道では 1 日の長さが一年中ほぼ同じで、薄明も短く天文薄明が終わるまで 73〜79 分です。北緯 35 度の春分で 89 分、夏至で 112 分です。緯度が高いほど太陽が地平線に斜めに沈むので、薄明が長くなります。北緯 60 度の夏至は太陽が −12° まで下がらず「白夜」になります。

ゲームで 1 日を 20 分に縮めたら、赤道に近い設定の日没は数十秒で終わります。薄明を長めに見せたい（演出）なら時刻の進みを夕方だけ遅くします。

## 光の強さと露出 {#illuminance}

太陽の光の強さは時刻で桁が変わります。Lagarde らはストックホルムの 7 月の晴れた日に照度計で測っています（水平に置いたセンサー）。

- 午前 9 時: 空 + 太陽で 85,500 lux
- 正午: 110,000 lux（空 19,300 + 太陽 90,700）
- 午後 6 時 30 分: 39,800 lux

太陽の光に垂直に置いたセンサーでは午前 9 時に 123,100 lux（太陽のみ）でした。理論値も出ています。太陽の輝度は約 1.6 × 10⁹ cd/m²、見かけの直径は 0.526〜0.545°（地球の軌道で変わる）です。立体角は `2π (1 − cos(直径/2))` で 6.6 × 10⁻⁵ 〜 7.1 × 10⁻⁵ sr です。C++ で掛けると 105,910〜113,699 lux になり Lagarde らの書く「105,000〜114,000 lux」と一致します。

夜までの桁は Wikipedia の表（一次資料ではない）で、次のとおりです。

- 日の出・日没（晴れ）: 約 400 lux
- 市民薄明の端（晴れ）: 3.4 lux
- 満月の夜: 0.05〜0.3 lux
- 月のない晴れた夜: 約 0.002 lux

昼（約 110,000 lux）と月のない夜（0.002 lux）の比は、`log2(110000 / 0.002)` ＝ 25.7 段（EV）です。固定の露出では昼が白飛びするか夜が真っ暗になります。自動露出（[Auto Exposure](../../postprocess/tonemapping/auto-exposure.md)）が事実上必須です。

<svg class="fig flow" viewBox="0 0 700 244" role="img" aria-label="照度の桁と露出"><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">照度(lux、対数軸)とその EV100(アルベド 0.18 の拡散面)</text><text x="202" y="50" text-anchor="end" font-size="11" fill="currentColor">直射日光(測定の上限)</text><rect x="210" y="34" width="343.8" height="20" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="559.835967249581" y="49" text-anchor="start" font-size="10" fill="currentColor">123100 lx(EV 15.8)</text><text x="202" y="80" text-anchor="end" font-size="11" fill="currentColor">晴天の昼(水平)</text><rect x="210" y="64" width="341.8" height="20" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="557.7591891192246" y="79" text-anchor="start" font-size="10" fill="currentColor">110000 lx(EV 15.6)</text><text x="202" y="110" text-anchor="end" font-size="11" fill="currentColor">日の出・日没</text><rect x="210" y="94" width="238.1" height="20" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="454.0875496314384" y="109" text-anchor="start" font-size="10" fill="currentColor">400 lx(EV 7.5)</text><text x="202" y="140" text-anchor="end" font-size="11" fill="currentColor">市民薄明の端</text><rect x="210" y="124" width="150.1" height="20" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="366.08785397429585" y="139" text-anchor="start" font-size="10" fill="currentColor">3.4 lx(EV 0.6)</text><text x="202" y="170" text-anchor="end" font-size="11" fill="currentColor">満月の夜</text><rect x="210" y="154" width="97.8" height="20" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="313.7937748157192" y="169" text-anchor="start" font-size="10" fill="currentColor">0.2 lx(EV -3.4)</text><text x="202" y="200" text-anchor="end" font-size="11" fill="currentColor">月のない晴れた夜</text><rect x="210" y="184" width="12.8" height="20" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="228.7937748157192" y="199" text-anchor="start" font-size="10" fill="currentColor">0.002 lx(EV -10.1)</text><line x1="210" y1="30" x2="210" y2="216" stroke="#94a3b8"/><text x="210.0" y="232" text-anchor="middle" font-size="10" fill="currentColor">10^-3</text><text x="295.0" y="232" text-anchor="middle" font-size="10" fill="currentColor">10^-1</text><text x="380.0" y="232" text-anchor="middle" font-size="10" fill="currentColor">10^1</text><text x="465.0" y="232" text-anchor="middle" font-size="10" fill="currentColor">10^3</text><text x="550.0" y="232" text-anchor="middle" font-size="10" fill="currentColor">10^5</text></svg>

Lagarde らは露出を EV100 で扱います。反射式メーターの定数 K ＝ 12.5 で、輝度 L ＝ 2^(EV − 3) cd/m² です。アルベド 0.18 の拡散面は `L = 0.18 E / π` なので、照度から EV100 が出ます（結果は、末尾の実行結果にあります）。

晴れた昼が EV100 ≒ 15.6、日の出・日没が 7.5、市民薄明の端が 0.6、満月の夜が −3.5、月のない夜が −10.1 です。目標の露出を時刻から導く式にしておけば、自動露出の適応が追いつかない瞬間（トンネルから出るなど）を除いて、時刻の進みに合わせて滑らかに変わります。

## 太陽の色 {#sun-color}

太陽が低いほど光は大気を長く通ります。青の散乱係数が大きいので青から先に失われ赤が残ります。大気の透過率で計算できるので、色を手で設定する必要はありません。

厳密には Bruneton の透過率テクスチャを引きます（[Bruneton Precomputed Scattering](../scattering/bruneton.md)）。軽い近似として Kasten-Young の空気量 `m(θ) = 1 / (cos θ + 0.15 (93.885 − θ[度])^(−1.253))` を使えます。垂直方向の光学的厚み τ ＝ β × スケールハイトに m を掛けて、`exp(−τ m)` です。数値積分と比べた結果は末尾の実行結果にあります。

近似と数値積分が天頂角 85° まで 0.01 以内で一致しました（青の透過率は 88° まで 0.001 以内）。88° では赤の近似が 0.228、数値が 0.199 と少し外れます。夕日の最後の数分を正確に出したいなら LUT を引きます。

空気量が 19.5 になる 88° では、青の透過率が 0.003、赤が 0.199 です。太陽の光がほぼ赤だけになります。この色がそのまま方向光の色になり地面や建物を赤く染めます。

## 空を描く：時刻が変わったら何を更新するか {#sky-update}

Hillaire（2020）の方式では、4 種類のテクスチャを使います。時刻（太陽の位置）が変わったとき更新が要るものを分けて考えます。

- 透過率 LUT: 大気の係数だけで決まる。太陽の位置は関係ない。時刻が動いても更新しない。
- 多重散乱 LUT: 2 次元で、`u = 0.5 + 0.5 cos(θs)`（太陽の天頂角）と高度 v で引く。点の位置と光の向きによらず有効なので、大気の係数を変えたときだけ作り直せばよい（実際は毎フレーム更新しても安い）。
- Sky-View LUT: 現在の視点から見た空を緯度・経度のテクスチャに描く。視点か太陽が動けば変わるので、動くたびに更新する。地平線付近を細かくするため緯度を `v = 0.5 + 0.5 sign(l) √(|l| / (π/2))` と写す。
- Aerial Perspective LUT: カメラの視錐台に合わせた 3D テクスチャで、既定は画面 32 × 32、奥行き 32 スライス、距離 32 km。視点か太陽が動くたびに更新する。

Bruneton（2008）の方式は、時刻に応じた更新が要りません（太陽の位置はテーブルの次元にあるので）。ところが、大気の係数を変える（天候など）と全体の作り直しが要ります。Hillaire は Bruneton の参照実装で LUT を全部更新すると 250 ms かかり、その 99 % が多重散乱の反復だと書いています。時間を分けて更新する方法はあるが、太陽の動きと空の色の間に遅れが出るとも書いています。

Hillaire の性能は NVIDIA 1080 で、最終的な空と空気遠近法の画面への合成が 0.14 ms、LUT の更新を含めた全体が 1280 × 720 で 0.31 ms です。宇宙から見るときは Sky-View LUT の多くが空の部分で無駄になるので、画面上のレイマーチに切り替わり全体は 0.5 ms です。

論文は地球でオゾンの層が重要だと書いています。オゾンは散乱せず吸収だけをして、太陽が地平線にあるときの空の青（夕焼けの上のほうの青）を出すのに欠かせません。分布は高度 25 km を中心とする、幅 30 km の三角形の関数です。

薄明の空には惑星の影が映ります。日没後に太陽の反対側の空に見える青灰色の帯です。論文の図 9 の「150 度の視野」で、Bruneton と Hillaire のどちらもこの影の淡い散乱色を再現できると書かれています。

## 夜と月 {#night}

太陽が沈むと月と星の出番です。月の位置は本来は軌道の計算が要ります（Meeus の本など）。簡易版では満月に限って太陽の反対側に置きます。月の照度は Wikipedia の表で、満月が 0.05〜0.3 lux です。太陽の約 40 万分の 1 で、上に述べた自動露出がこの明るさに合わせます。

星は夜にフェード インさせます（[Sun, Moon and Stars](celestial.md)）。薄明の度合い（高度 0° で 0、−18° で 1）で重みを付ければ、日没後に滑らかに現れます。

## 連動させるもの {#coupling}

時刻から連動させるものを一覧にします。

- 空（大気散乱）: LUT を太陽の位置で更新する。
- 太陽光（方向光）: 向き色、強さ。色と強さは透過率から出る。
- 月光: 夜は月を方向光にする。
- 環境光（空のライティング）: 空の色から再計算する（[Using the Sky for Lighting](sky-lighting.md)）。
- 星と月の見た目: 薄明の度合いでフェードする。
- 霧（空気遠近法）: 空の色に合わせる（[Matching Fog Color to the Sky](../aerial-fog/color-match.md)）。
- 影: 太陽が低いと影が長くなる。シャドウ マップの範囲とバイアスを調整する。
- 露出: 目標の EV100 を時刻から出し、自動露出が数秒かけて追う。
- 人工の光: 街灯と窓を夜に点ける。
- カラー グレーディング: 夜は青みがかり彩度が下がる（暗所での目の見え方の演出）。

## 実装してみる {#code}

### 時刻から太陽・月・環境光・露出を決める {#code-gpu}

```hlsl
// 時刻から、太陽・月・環境光・露出をまとめて決める（1 スレッドのコンピュート シェーダー）。
// CPU で同じ計算をしてもよい。ここでは、結果を構造体バッファに書いて、他のシェーダーが読む形にしている。
//   入力: 緯度・日付・時刻・大気の係数
//   出力: 太陽の向きと色つきの照度、月の向きと照度、環境光の強さ、目標の露出 EV100

struct TimeOfDayOut {
  float3 sun_dir;            // 太陽へ向かう単位ベクトル（x = 東、y = 上、z = 北）
  float sun_altitude;        // 太陽の高度 [rad]
  float3 sun_illuminance;    // 地表での太陽の照度（RGB、lux）。大気の透過率を掛けたもの
  float twilight;            // 薄明の度合い。昼 = 0、夜 = 1（高度 0° から -18° へ）
  float3 moon_dir;           // 月へ向かう単位ベクトル
  float moon_illuminance;    // 月の照度 [lux]（簡易）
  float ambient_scale;       // 空の環境光の強さ（昼 = 1）
  float target_ev100;        // 自動露出の目標 EV100
  float2 pad;
};
RWStructuredBuffer<TimeOfDayOut> g_out : register(u0);

cbuffer TimeOfDayCB : register(b0) {
  float g_latitude;          // 緯度 [rad]。北が正
  float g_day_of_year;       // 年初からの日数（1〜365）
  float g_hour;              // 現地の太陽時（0〜24）
  float g_sun_illuminance_perp;   // 大気の外から数えた、太陽に垂直な面の照度の基準 [lux]。一例: 128000（透過率を掛ける前）
  float3 g_beta_rayleigh;    // レイリー散乱係数 [1/km]。(5.8, 13.5, 33.1) × 1e-3（Bruneton 2008）
  float g_beta_mie_extinct;  // Mie の消散係数 [1/km]。2.2e-2 / 0.9
  float g_height_rayleigh;   // 8 km
  float g_height_mie;        // 1.2 km
  float g_moon_phase;        // 月の満ち欠け（0 = 新月、1 = 満月）
  float g_pad;
};

static const float kPi = 3.14159265;

// 太陽の赤緯 [rad]。年間の近似式 δ = -23.44° cos(2π (N + 10) / 365)（一般的な近似）。
float Declination(float day_of_year) {
  return -radians(23.44) * cos(2.0 * kPi * (day_of_year + 10.0) / 365.0);
}

// 緯度 phi、赤緯 delta、時角 hour_angle [rad] から、高度と方位を求め、単位ベクトルにする。
float3 DirectionFromAngles(float phi, float delta, float hour_angle, out float altitude) {
  float sin_alt = sin(phi) * sin(delta) + cos(phi) * cos(delta) * cos(hour_angle);
  altitude = asin(clamp(sin_alt, -1.0, 1.0));
  // 方位（北から時計回り）。分子と分母に cos(alt) を掛けた形で atan2 に渡せば、象限が決まる。
  float az = atan2(-cos(delta) * sin(hour_angle),
                   sin(delta) * cos(phi) - cos(delta) * sin(phi) * cos(hour_angle));
  return float3(cos(altitude) * sin(az), sin(altitude), cos(altitude) * cos(az));
}

// 空気量 m(θ)。Kasten-Young の式（一般的な式）。θ は天頂角 [rad]。90° 以上では上限に張りつく。
float AirMass(float zenith) {
  float deg = min(degrees(zenith), 93.0);                  // 93.885 で発散するので手前で打ち切る。足した処理
  return 1.0 / (cos(zenith) + 0.15 * pow(93.885 - deg, -1.253));
}

// 太陽の光の色。垂直方向の光学的厚み τ = β × スケールハイトに、空気量を掛けて exp。
// 青は係数が大きいので、空気量が増えるほど先に減り、朝夕は赤くなる。
float3 SunTransmittance(float zenith) {
  float3 tau = g_beta_rayleigh * g_height_rayleigh + g_beta_mie_extinct * g_height_mie;
  return exp(-tau * AirMass(zenith));
}

[numthreads(1, 1, 1)]
void UpdateTimeOfDayCS() {
  TimeOfDayOut o;

  // ---- 太陽 ----
  float delta = Declination(g_day_of_year);
  float hour_angle = radians(15.0 * (g_hour - 12.0));            // 正午が 0、午後が正
  o.sun_dir = DirectionFromAngles(g_latitude, delta, hour_angle, o.sun_altitude);

  // 地平線の下では太陽の光は届かない。地平線の少し上から下へ、なめらかに 0 にする（太陽は円盤で半径があるため）。
  float zenith = kPi * 0.5 - o.sun_altitude;
  float horizon_fade = smoothstep(-0.01, 0.01, o.sun_altitude);   // 約 ±0.6° の幅（太陽の見かけの半径の 2 倍強）
  float3 transmittance = SunTransmittance(min(zenith, kPi * 0.5));
  o.sun_illuminance = g_sun_illuminance_perp * transmittance * horizon_fade;

  // 薄明の度合い: 高度 0° で 0、-18° で 1。昼 = 0。
  o.twilight = saturate(-degrees(o.sun_altitude) / 18.0);

  // ---- 月（簡易）----
  // 本来は月の軌道から求める（Meeus の本など）。ここでは太陽の反対側に置く簡易版（満月のとき正しい）。足した処理。
  float moon_alt;
  o.moon_dir = DirectionFromAngles(g_latitude, -delta, hour_angle + kPi, moon_alt);
  // 満月で約 0.2 lux（Wikipedia の表: 0.05〜0.3）。満ち欠けで比例させ、地平線の下で 0。
  o.moon_illuminance = 0.2 * g_moon_phase * smoothstep(-0.01, 0.05, moon_alt);

  // ---- 環境光 ----
  // 空の明るさは、太陽が沈んだ後もしばらく残る（高い層が照らされる）。薄明の度合いに合わせて減らす。
  o.ambient_scale = lerp(1.0, 0.0, smoothstep(0.0, 1.0, o.twilight));

  // ---- 目標の露出 ----
  // 水平面の照度を、昼は 110,000 lux 程度、夜は月の照度 + 星明かり 0.002 lux とする。
  float lux_horizontal = max(o.sun_illuminance.g * max(o.sun_dir.y, 0.0) + 20000.0 * o.ambient_scale,
                             o.moon_illuminance + 0.002);
  // 拡散面（アルベド 0.18）の輝度 L = 0.18 E / π。EV100 = log2(L × 100 / 12.5)（K = 12.5）。
  float luminance = 0.18 * lux_horizontal / kPi;
  o.target_ev100 = log2(luminance * 100.0 / 12.5);
  o.pad = 0.0;

  g_out[0] = o;
}
```

構造体 `TimeOfDayOut` に太陽、月、環境光、露出をまとめて書きます。他のシェーダーがこの 1 つの構造体を読みます。薄明の度合いは `saturate(−高度[度] / 18)` で高度 0° の日没で 0、−18° で 1 です。太陽の照度は地平線のすぐ下で滑らかに 0 になるようにしています。太陽が円盤で半径があるためで、約 ±0.6° の幅です。

HLSL は `fxc`（cs_5_0）でコンパイルして確かめました。実行して絵は確かめていません。月の位置は太陽の反対側に置く簡易版で、満月でしか正しくありません。

### 数字を出す C++ {#cpp}

太陽の位置、昼の長さ薄明、立体角と照度、EV100、透過率の近似の確認を 1 本の C++ で出します。

MSVC（`/std:c++latest /W4`）でコンパイルして実行しました。

```cpp
// 時刻から太陽の位置・照度・露出を求める。数字を出して確かめる。
//  1. 太陽の高度・方位（緯度・日付・時刻から）。至点・分点の正午の高度と、昼の長さ
//  2. 薄明（市民・航海・天文）の長さ
//  3. 太陽の立体角と、地表の照度の理論値（Lagarde & de Rousiers 2014 の式）
//  4. 照度 → 露出 EV100（反射式メーターの K = 12.5、アルベド 0.18 の拡散面）
#include <cmath>
#include <cstdio>
#include <initializer_list>

namespace {
constexpr double kPi = 3.14159265358979323846;
double Rad(double deg) { return deg * kPi / 180.0; }
double Deg(double rad) { return rad * 180.0 / kPi; }

struct Sun {
  double altitude_deg;   // 高度 [度]。0 が地平線
  double azimuth_deg;    // 方位 [度]。北から時計回り（90 が東、180 が南）
  double dir[3];         // 単位ベクトル。x = 東、y = 上、z = 北（左手系、y が上）
};

// 太陽の赤緯 [度]。N は年初からの日数（1〜365）。
// 近似式 δ = -23.44° cos(2π (N + 10) / 365)。冬至が N = 355 付近（12/21）で -23.44°。一般的な近似で、出典は読んでいない。
double Declination(int day_of_year) { return -23.44 * std::cos(2.0 * kPi * (day_of_year + 10) / 365.0); }

// 緯度 latitude_deg [度]、日付、時刻 hour（現地の太陽時 0〜24）から、太陽の位置を求める。
// 太陽時角 H = 15° × (hour - 12)（正午が 0、午後が正）。均時差と経度のずれは無視する。
Sun SunPosition(double latitude_deg, int day_of_year, double hour) {
  const double phi = Rad(latitude_deg);
  const double delta = Rad(Declination(day_of_year));
  const double h = Rad(15.0 * (hour - 12.0));
  // 高度: sin(alt) = sin φ sin δ + cos φ cos δ cos H
  const double sin_alt = std::sin(phi) * std::sin(delta) + std::cos(phi) * std::cos(delta) * std::cos(h);
  const double alt = std::asin(sin_alt);
  // 方位（北から時計回り）: 北向きを +z、東向きを +x とする。
  // 分子と分母に cos(alt) を掛けた形で atan2 に渡すと、象限が正しく決まる。
  const double az = std::atan2(-std::cos(delta) * std::sin(h),
                               std::sin(delta) * std::cos(phi) - std::cos(delta) * std::sin(phi) * std::cos(h));
  Sun s;
  s.altitude_deg = Deg(alt);
  s.azimuth_deg = std::fmod(Deg(az) + 360.0, 360.0);
  s.dir[0] = std::cos(alt) * std::sin(az);      // 東
  s.dir[1] = std::sin(alt);                      // 上
  s.dir[2] = std::cos(alt) * std::cos(az);       // 北
  return s;
}

// 高度が target_deg を横切る時刻 [時] を、午前と午後で探す（0.01 時間刻み）。見つからなければ -1。
void FindCrossing(double lat, int day, double target_deg, double* morning, double* evening) {
  *morning = *evening = -1;
  double prev = SunPosition(lat, day, 0.0).altitude_deg;
  for (double t = 0.01; t <= 24.0; t += 0.01) {
    const double a = SunPosition(lat, day, t).altitude_deg;
    if (prev < target_deg && a >= target_deg && *morning < 0) *morning = t;
    if (prev >= target_deg && a < target_deg && *evening < 0 && t > 12) *evening = t;
    prev = a;
  }
}
}  // namespace

int main() {
  const double lat = 35.0;
  std::printf("== 北緯 %.0f 度の正午の高度 ==\n", lat);
  const struct { const char* name; int day; } days[] = {{"冬至 (12/21)", 355}, {"春分 (3/20)", 79}, {"夏至 (6/21)", 172}, {"秋分 (9/22)", 265}};
  for (const auto& d : days) {
    const Sun s = SunPosition(lat, d.day, 12.0);
    double rise, set;
    FindCrossing(lat, d.day, 0.0, &rise, &set);
    std::printf("%-14s 赤緯 %+6.2f 度、正午の高度 %5.2f 度、日の出 %5.2f 時、日の入り %5.2f 時（昼 %4.1f 時間）\n", d.name,
                Declination(d.day), s.altitude_deg, rise, set, set - rise);
  }
  std::printf("理論値: 正午の高度 = 90 - 緯度 + 赤緯。夏至 %.2f 度、冬至 %.2f 度\n", 90 - lat + 23.44, 90 - lat - 23.44);

  std::printf("\n== 春分の 1 日（北緯 %.0f 度）==\n", lat);
  std::printf("時刻   高度[度]  方位[度]  方向ベクトル (東, 上, 北)\n");
  for (double hr : {5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 18.0, 19.0}) {
    const Sun s = SunPosition(lat, 79, hr);
    std::printf("%4.1f   %7.2f   %7.2f   (%+.3f, %+.3f, %+.3f)\n", hr, s.altitude_deg, s.azimuth_deg, s.dir[0], s.dir[1], s.dir[2]);
  }

  std::printf("\n== 薄明の長さ（日没から、高度が下の値になるまで）==\n");
  std::printf("緯度  日付   日没後 市民(-6°)  航海(-12°)  天文(-18°)  [分]\n");
  for (double l : {0.0, 35.0, 60.0}) {
    for (const auto& d : {days[1], days[2]}) {
      double r0, s0, r6, s6, r12, s12, r18, s18;
      FindCrossing(l, d.day, 0.0, &r0, &s0);
      FindCrossing(l, d.day, -6.0, &r6, &s6);
      FindCrossing(l, d.day, -12.0, &r12, &s12);
      FindCrossing(l, d.day, -18.0, &r18, &s18);
      std::printf("%3.0f   %-12s", l, d.name);
      for (double s : {s6, s12, s18}) {
        if (s < 0) std::printf("   (沈まない)"); else std::printf("   %7.0f", (s - s0) * 60.0);
      }
      std::printf("\n");
    }
  }

  std::printf("\n== 太陽の立体角と照度の理論値 ==\n");
  for (double ad : {0.526, 0.545}) {
    const double omega = 2.0 * kPi * (1.0 - std::cos(Rad(0.5 * ad)));
    std::printf("見かけの直径 %.3f 度 → 立体角 %.3e sr → 照度 = 1.6e9 cd/m2 x 立体角 = %.0f lx\n", ad, omega, 1.6e9 * omega);
  }

  std::printf("\n== 地表の照度 → 露出 EV100 ==\n");
  std::printf("EV100 = log2(L * 100 / 12.5)（K = 12.5）。拡散面 L = 0.18 E / pi（アルベド 0.18）\n");
  std::printf("状況                          照度[lx]   EV100\n");
  const struct { const char* name; double lux; } rows[] = {
      {"正午の直射日光（測定の上限）", 123100}, {"晴天の昼（太陽 + 空、水平）", 110000}, {"日の出・日没", 400},
      {"市民薄明の端", 3.4},                  {"満月の夜", 0.2},                     {"月のない晴れた夜", 0.002}};
  for (const auto& r : rows) {
    const double L = 0.18 * r.lux / kPi;
    std::printf("%-26s %10.3f   %6.2f\n", r.name, r.lux, std::log2(L * 100.0 / 12.5));
  }
  std::printf("昼と月のない夜の差: %.1f EV（段）\n", std::log2(110000.0 / 0.002));

  // ---- 太陽の色: 大気の透過率の近似 ----
  // 空気量 m(θ) = 1 / (cos θ + 0.15 (93.885 - θ[度])^-1.253)（Kasten-Young の式。一般的な式で、出典は読んでいない）。
  // 垂直方向の光学的厚み τ = β × H（レイリー: β_R × 8 km、Mie: β_Me × 1.2 km）に m を掛けて exp する。
  // 数値積分（Bruneton のページの C++ と同じ、球の大気 6360〜6420 km）と比べる。
  std::printf("\n== 太陽の透過率: 空気量の近似 と 数値積分（赤 / 緑 / 青）==\n");
  const double beta_r[3] = {5.8e-3, 13.5e-3, 33.1e-3};      // [1/km]（680, 550, 440 nm）
  const double beta_me = 2.2e-2 / 0.9;                       // Mie の消散係数 [1/km]
  const double hr = 8.0, hm = 1.2;                           // スケールハイト [km]
  const double rg = 6360.0, rt = 6420.0;
  for (double zenith : {0.0, 60.0, 80.0, 85.0, 88.0}) {
    const double mu = std::cos(Rad(zenith));
    // 数値積分（台形則）
    const double disc = rg * rg * (mu * mu - 1.0) + rt * rt;
    const double len = -rg * mu + std::sqrt(disc);
    const int n = 4000;
    double lr = 0, lm = 0;
    for (int i = 0; i <= n; ++i) {
      const double d = len * i / n;
      const double h = std::sqrt(d * d + 2 * rg * mu * d + rg * rg) - rg;
      const double w = (i == 0 || i == n) ? 0.5 : 1.0;
      lr += std::exp(-h / hr) * w * len / n;
      lm += std::exp(-h / hm) * w * len / n;
    }
    const double m = 1.0 / (mu + 0.15 * std::pow(93.885 - zenith, -1.253));
    std::printf("%4.0f 度  空気量 %5.2f  近似 %.3f / %.3f / %.3f   数値 %.3f / %.3f / %.3f\n", zenith, m,
                std::exp(-(beta_r[0] * hr + beta_me * hm) * m), std::exp(-(beta_r[1] * hr + beta_me * hm) * m),
                std::exp(-(beta_r[2] * hr + beta_me * hm) * m), std::exp(-(beta_r[0] * lr + beta_me * lm)),
                std::exp(-(beta_r[1] * lr + beta_me * lm)), std::exp(-(beta_r[2] * lr + beta_me * lm)));
  }
  return 0;
}
```

```text title="実行結果"
== 北緯 35 度の正午の高度 ==
冬至 (12/21) 赤緯 -23.44 度、正午の高度 31.56 度、日の出  7.18 時、日の入り 16.83 時（昼  9.6 時間）
春分 (3/20)  赤緯  -0.91 度、正午の高度 54.09 度、日の出  6.05 時、日の入り 17.96 時（昼 11.9 時間）
夏至 (6/21)  赤緯 +23.44 度、正午の高度 78.44 度、日の出  4.83 時、日の入り 19.18 時（昼 14.4 時間）
秋分 (9/22)  赤緯  -0.50 度、正午の高度 54.50 度、日の出  6.03 時、日の入り 17.98 時（昼 12.0 時間）
理論値: 正午の高度 = 90 - 緯度 + 赤緯。夏至 78.44 度、冬至 31.56 度
```

```text title="実行結果（続き）"
== 春分の 1 日（北緯 35 度）==
時刻   高度[度]  方位[度]  方向ベクトル (東, 上, 北)
 5.0    -12.77     82.02   (+0.966, -0.221, +0.135)
 6.0     -0.52     90.74   (+1.000, -0.009, -0.013)
 8.0     23.61    109.09   (+0.866, +0.400, -0.300)
10.0     44.45    135.55   (+0.500, +0.700, -0.510)
12.0     54.09    180.00   (-0.000, +0.810, -0.586)
15.0     34.76    239.38   (-0.707, +0.570, -0.419)
18.0     -0.52    269.26   (-1.000, -0.009, -0.013)
19.0    -12.77    277.98   (-0.966, -0.221, +0.135)
```

```text title="実行結果（続き）"
== 薄明の長さ（日没から、高度が下の値になるまで）==
緯度  日付   日没後 市民(-6°)  航海(-12°)  天文(-18°)  [分]
  0   春分 (3/20)        25        49        73
  0   夏至 (6/21)        26        53        79
 35   春分 (3/20)        29        59        89
 35   夏至 (6/21)        35        71       112
 60   春分 (3/20)        48        98       151
 60   夏至 (6/21)       118   (沈まない)   (沈まない)
```

```text title="実行結果（続き）"
== 太陽の立体角と照度の理論値 ==
見かけの直径 0.526 度 → 立体角 6.619e-05 sr → 照度 = 1.6e9 cd/m2 x 立体角 = 105910 lx
見かけの直径 0.545 度 → 立体角 7.106e-05 sr → 照度 = 1.6e9 cd/m2 x 立体角 = 113699 lx
```

```text title="実行結果（続き）"
== 地表の照度 → 露出 EV100 ==
EV100 = log2(L * 100 / 12.5)（K = 12.5）。拡散面 L = 0.18 E / pi（アルベド 0.18）
状況                          照度[lx]   EV100
正午の直射日光（測定の上限） 123100.000    15.78
晴天の昼（太陽 + 空、水平） 110000.000    15.62
日の出・日没            400.000     7.52
市民薄明の端              3.400     0.64
満月の夜                    0.200    -3.45
月のない晴れた夜        0.002   -10.09
昼と月のない夜の差: 25.7 EV（段）
```

```text title="実行結果（続き）"
== 太陽の透過率: 空気量の近似 と 数値積分（赤 / 緑 / 青）==
   0 度  空気量  1.00  近似 0.927 / 0.872 / 0.745   数値 0.927 / 0.872 / 0.745
  60 度  空気量  1.99  近似 0.860 / 0.761 / 0.556   数値 0.860 / 0.761 / 0.557
  80 度  空気量  5.58  近似 0.655 / 0.465 / 0.194   数値 0.654 / 0.464 / 0.195
  85 度  空気量 10.32  近似 0.458 / 0.242 / 0.048   数値 0.450 / 0.241 / 0.049
  88 度  空気量 19.54  近似 0.228 / 0.068 / 0.003   数値 0.199 / 0.063 / 0.003
```

## 1 日の時間を進める {#advance}

ゲームでは 1 日を数十分に縮めます。時刻を一定の速さで進めます。

```cpp
// ゲーム内の時刻（時）を進める。1 日を day_length_minutes 分に縮める。
float AdvanceTime(float hour, float dt_seconds, float day_length_minutes) {
  const float hours_per_second = 24.0f / (day_length_minutes * 60.0f);   // 現実の 1 秒で、ゲーム内で何時間進むか
  hour += dt_seconds * hours_per_second;                                  // フレームの時間ぶん進める
  if (hour >= 24.0f) hour -= 24.0f;                                       // 24 時を超えたら 0 時へ戻す
  return hour;
}
```

昼を長く夜を短くする（プレイしやすい）ときは、時刻に応じて進む速さを変えます。日付を進めて季節を回すことも場面ごとに固定することもできます。

## よくあるミス

??? failure "日没で、影が長くならない・向きが変わらない"
    影に使う方向光の向きが、時刻に連動していない。太陽の向きを時刻から計算して、方向光とシャドウ マップに使う。

??? failure "夜になると、画面が真っ暗になる"
    露出が固定。夜の EV100 は昼より約 26 段低い。時刻から目標の露出を出し自動露出に渡す。

??? failure "日没後すぐ空が真っ暗になる"
    薄明を入れていない。環境光を太陽の高度が −18° になるまで、なめらかに減らす。

??? failure "夕方の太陽が白いまま"
    太陽の色に透過率を掛けていない。空気量から透過率を出し方向光の色に掛ける。

??? failure "地平線で太陽の光が突然切れる"
    高度 0° で 0 と 1 を切り替えている。太陽は円盤なので約 ±0.6° の幅で滑らかに 0 にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 時刻（緯度・日付・時刻）から太陽の向きを決め残りは全部そこから導く。
    - [x] 昼と夜の差は約 26 EV。自動露出が要る。
    - [x] 太陽の色は透過率で決まる。朝夕は青が減って赤くなる。
    - [x] 薄明は日没後も続く。市民で約 30 分、天文で約 90 分（北緯 35 度の春分）。
    - [x] 時刻で更新するのは、Sky-View、Aerial Perspective、多重散乱の LUT。

## 参考

- Sébastien Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Proc. EGSR 2020) 39(4), 2020. <https://sebh.github.io/publications/egsr2020.pdf>（第 7 節の途中まで読んだ。表 2 の詳細と結論は読んでいない）
- Sébastien Lagarde, Charles de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014 Course: Physically Based Shading in Theory and Practice, 2014.（太陽の節と表 11、EV の節を読んだ。全体は読んでいない）
- Eric Bruneton, Fabrice Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum 27(4) (EGSR 2008), 2008.（係数と透過率）
- Wikipedia, "Lux"（照度の表。一次資料ではない）
- Jean Meeus, "Astronomical Algorithms", Willmann-Bell, 1991（太陽・月の位置の精密な計算。今回は読んでいない）
- 太陽の赤緯の近似式と Kasten-Young の空気量の式は、一般的な式で今回は出典を読んでいない。

## 関連ページ

- [Sky Models](index.md)
- [Sun, Moon and Stars](celestial.md)
- [Using the Sky for Lighting](sky-lighting.md)
- [Bruneton Precomputed Scattering](../scattering/bruneton.md)
- [Hillaire 2020](../scattering/hillaire.md)
