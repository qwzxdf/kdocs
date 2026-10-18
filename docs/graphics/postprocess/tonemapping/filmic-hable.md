---
title: Filmic (Hable)
tags:
  - 描画
---

# Filmic (Hable)

**フィルミック**は、**フィルムの感光特性に似た S 字カーブ**でトーンマップする方式です。**Uncharted 2 で使われた Hable の式**が**有名**で、**暗部を締め（黒を沈め）、中間にコントラストを付け、明部をなだらかにロールオフ**します。**Reinhard の眠さが消え、映画のような絵**になります。このページでは、**S 字の 3 つの領域（つま先・直線部・肩）・Hable の式と各係数の意味・白点・露出との関係・自分で曲線を調整する方法**を説明します。

!!! tip "ポイント"
    - フィルミック ＝ <strong>S 字の曲線</strong>。<strong>つま先（暗部）→ 直線部（中間）→ 肩（明部）</strong>の 3 領域。
    - <strong>つま先</strong>で<strong>暗部を締めて黒を沈め</strong>、<strong>肩</strong>で<strong>明部を滑らかに飽和</strong>させる。
    - Hable の式は<strong>係数 A〜F</strong>で<strong>形を決め</strong>、<strong>白点で割って 1 に正規化</strong>する。
    - <strong>露出倍率</strong>（`× 2.0`）を<strong>曲線の前に</strong>掛けて、<strong>中間の明るさを合わせる</strong>。
    - <strong>より良いやり方</strong>：<strong>係数をアーティストが調整できる</strong>ように**パラメータとして出す**。**3D LUT に焼く**。

## S 字の 3 つの領域

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="S 字カーブの 3 領域">
<text x="20" y="26" class="fig-title">フィルミック曲線：つま先・直線部・肩</text>
<line x1="80" y1="250" x2="720" y2="250" stroke="currentColor" stroke-opacity="0.5"/>
<line x1="80" y1="50" x2="80" y2="250" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#2563eb" stroke-width="4" points="80,250 120,248 160,243 200,232 240,214 280,190 320,162 360,134 400,110 440,92 480,80 520,72 560,66 600,62 640,59 680,57 720,55"/>
<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5 4" points="80,250 720,50"/>
<rect x="80" y="40" width="130" height="210" fill="#e5aa28" fill-opacity="0.12"/>
<rect x="210" y="40" width="250" height="210" fill="#2ea043" fill-opacity="0.1"/>
<rect x="460" y="40" width="260" height="210" fill="#9664e6" fill-opacity="0.1"/>
<text x="145" y="70" text-anchor="middle" style="font-size:13px;font-weight:700">つま先</text><text x="145" y="90" text-anchor="middle" style="font-size:11px">暗部を締める</text>
<text x="335" y="70" text-anchor="middle" style="font-size:13px;font-weight:700">直線部</text><text x="335" y="90" text-anchor="middle" style="font-size:11px">中間にコントラスト</text>
<text x="590" y="110" text-anchor="middle" style="font-size:13px;font-weight:700">肩</text><text x="590" y="130" text-anchor="middle" style="font-size:11px">明部を滑らかに飽和</text>
<text x="400" y="278" text-anchor="middle" style="font-size:12px">入力（HDR の明るさ）→</text>
<text x="40" y="150" style="font-size:12px">出力</text>
<text x="640" y="192" style="font-size:11px;fill:#64748b">灰色の点線 ＝ y = x</text>
</svg>

曲線は 3 つの領域に分けて考えます。<strong>つま先（toe）</strong>は、暗部の立ち上がりを抑える部分で、黒が沈んで締まり、暗部が持ち上がりません。<strong>直線部（linear）</strong>は、中間の傾き（コントラスト）を決める部分で、メリハリが付きます。<strong>肩（shoulder）</strong>は、明部で傾きがゆるやかになり、1 に漸近する部分で、ハイライトが白飛びせず滑らかに白へ向かいます。

原典は、Hable の GDC 2010 の発表 "Uncharted 2: HDR Lighting" です。Kodak のフィルムの特性曲線を参考に、つま先・直線部・肩を 1 つの有理関数（分数の式）で表しました。係数は 6 個（A〜F）と白点 W です。

**Reinhard はつま先がなく、暗部が持ち上がる**ため**眠い**です。**S 字はつま先で暗部を沈める**ので、**絵が締まります**。

<!-- fig:tonemap-hable:begin -->

<svg class="fig illust motion" data-fig="tonemap-hable" viewBox="0 0 780 380" role="img"><rect x="0" y="0" width="780" height="380" rx="14" fill="#ffffff"/>
<defs><marker id="arr-tonemap-hable" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">フィルミックの S 字:つま先・直線部・肩の 3 つの領域</text>
<rect x="50" y="70" width="430" height="250" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="157.5" y1="70" x2="157.5" y2="320" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="132.5" x2="480" y2="132.5" stroke="#e2e8f0" stroke-width="1"/>
<line x1="265.0" y1="70" x2="265.0" y2="320" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="195.0" x2="480" y2="195.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="372.5" y1="70" x2="372.5" y2="320" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="257.5" x2="480" y2="257.5" stroke="#e2e8f0" stroke-width="1"/>
<text x="480" y="340" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">入力 x</text>
<text x="50" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">出力</text>
<path d="M50.0,320.0 L56.72,298.57 L63.44,280.53 L70.16,265.12 L76.88,251.82 L83.59,240.21 L90.31,230.0 L97.03,220.94 L103.75,212.86 L110.47,205.59 L117.19,199.03 L123.91,193.08 L130.62,187.65 L137.34,182.68 L144.06,178.11 L150.78,173.9 L157.5,170.0 L164.22,166.39 L170.94,163.02 L177.66,159.89 L184.38,156.96 L191.09,154.21 L197.81,151.63 L204.53,149.21 L211.25,146.92 L217.97,144.77 L224.69,142.73 L231.41,140.8 L238.12,138.97 L244.84,137.23 L251.56,135.57 L258.28,134.0 L265.0,132.5 L271.72,131.07 L278.44,129.7 L285.16,128.39 L291.88,127.14 L298.59,125.94 L305.31,124.79 L312.03,123.69 L318.75,122.63 L325.47,121.61 L332.19,120.63 L338.91,119.69 L345.62,118.78 L352.34,117.9 L359.06,117.06 L365.78,116.24 L372.5,115.45 L379.22,114.69 L385.94,113.96 L392.66,113.24 L399.38,112.55 L406.09,111.88 L412.81,111.24 L419.53,110.61 L426.25,110.0 L432.97,109.41 L439.69,108.83 L446.41,108.28 L453.12,107.74 L459.84,107.21 L466.56,106.7 L473.28,106.2 L480.0,105.71" fill="none" stroke="#64748b" stroke-width="3" opacity="1" stroke-dasharray="5 4"/>
<text x="279.33" y="165.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">Reinhard（比較）</text>
<path d="M50.0,320.0 L51.25,318.32 L52.51,316.65 L53.76,314.98 L55.02,313.33 L56.27,311.68 L57.52,310.05 L58.78,308.44 L60.03,306.83 L61.29,305.24 L62.54,303.67 L63.8,302.11 L65.05,300.57 L66.3,299.04 L67.56,297.52 L68.81,296.02 L70.07,294.53 L71.32,293.06 L72.58,291.6 L73.83,290.16 L75.08,288.73 L76.34,287.31 L77.59,285.91 L78.85,284.52 L80.1,283.14 L81.35,281.78 L82.61,280.42 L83.86,279.09 L85.12,277.76 L86.37,276.45 L87.62,275.14 L88.88,273.86 L90.13,272.58 L91.39,271.31 L92.64,270.06 L93.9,268.81 L95.15,267.58 L96.4,266.36 L97.66,265.15 L98.91,263.95 L100.17,262.76" fill="none" stroke="#7c3aed" stroke-width="5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0692;0.0696;1.0000" values="0;0;1;1"/></path>
<text x="520" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#7c3aed" opacity="0">つま先<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0692;0.0696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="520" y="132" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">暗部を沈めて、締まった絵に<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0692;0.0696;1.0000;1.0000" values="0;0;1;1;0"/></text>
<path d="M100.17,262.76 L103.57,259.59 L106.97,256.49 L110.38,253.47 L113.78,250.51 L117.19,247.63 L120.59,244.8 L124.0,242.04 L127.4,239.34 L130.8,236.7 L134.21,234.12 L137.61,231.59 L141.02,229.12 L144.42,226.7 L147.82,224.33 L151.23,222.0 L154.63,219.73 L158.04,217.5 L161.44,215.31 L164.85,213.17 L168.25,211.07 L171.65,209.01 L175.06,206.99 L178.46,205.01 L181.87,203.06 L185.27,201.15 L188.68,199.28 L192.08,197.44 L195.48,195.63 L198.89,193.86 L202.29,192.12 L205.7,190.41 L209.1,188.73 L212.5,187.07 L215.91,185.45 L219.31,183.85 L222.72,182.28 L226.12,180.74 L229.53,179.23 L232.93,177.73 L236.33,176.27" fill="none" stroke="#2563eb" stroke-width="5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000" values="0;0;1;1"/></path>
<text x="520" y="172" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">直線部<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="520" y="194" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">中間の明るさは、素直に保つ<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2783;1.0000;1.0000" values="0;0;1;1;0"/></text>
<path d="M236.33,176.27 L242.43,173.7 L248.52,171.2 L254.61,168.78 L260.7,166.42 L266.79,164.13 L272.88,161.9 L278.98,159.72 L285.07,157.61 L291.16,155.55 L297.25,153.54 L303.34,151.58 L309.43,149.67 L315.53,147.81 L321.62,146.0 L327.71,144.22 L333.8,142.49 L339.89,140.8 L345.98,139.15 L352.07,137.54 L358.17,135.96 L364.26,134.42 L370.35,132.91 L376.44,131.43 L382.53,129.99 L388.62,128.58 L394.72,127.2 L400.81,125.85 L406.9,124.52 L412.99,123.22 L419.08,121.95 L425.17,120.71 L431.27,119.49 L437.36,118.29 L443.45,117.12 L449.54,115.97 L455.63,114.84 L461.73,113.73 L467.82,112.64 L473.91,111.58 L480.0,110.53" fill="none" stroke="#2ea043" stroke-width="5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4866;0.4870;1.0000" values="0;0;1;1"/></path>
<text x="520" y="234" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">肩<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4866;0.4870;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="520" y="256" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">明部をなめらかに圧縮して、白飛びを防ぐ<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4866;0.4870;1.0000;1.0000" values="0;0;1;1;0"/></text>
<circle cx="50.0" cy="320.0" r="7" fill="#1f2937" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6953;0.6957;1.0000" values="0;0;1;1"/><animate attributeName="cx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6957;0.7065;0.7174;0.7283;0.7391;0.7500;0.7609;0.7717;0.7826;0.7935;0.8043;0.8152;0.8261;0.8370;0.8478;0.8587;0.8696;1.0000" values="50;50;76.88;103.75;130.62;157.5;184.38;211.25;238.12;265;291.88;318.75;345.62;372.5;399.38;426.25;453.12;480;480"/><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6957;0.7065;0.7174;0.7283;0.7391;0.7500;0.7609;0.7717;0.7826;0.7935;0.8043;0.8152;0.8261;0.8370;0.8478;0.8587;0.8696;1.0000" values="320;320;286.71;259.43;236.84;217.85;201.65;187.68;175.5;164.8;155.31;146.84;139.25;132.39;126.16;120.49;115.3;110.53;110.53"/></circle>
<text x="50" y="352" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937" opacity="0">つま先 → 直線部 → 肩の順に、曲線が現れる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6953;0.6957;1.0000" values="1;1;0;0"/></text>
<text x="50" y="352" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937" opacity="0">Reinhard より、暗部が低い（つま先） ＝ コントラストが高い<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6953;0.6957;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:tonemap-hable:end -->

## Hable の式（Uncharted 2）

**有理関数**で**S 字を作る**式です。

<div class="formula">f(x) = ( (x·(A·x + C·B) + D·E) / (x·(A·x + B) + D·F) ) − E/F</div>

```hlsl
float3 HableCurve(float3 x) {
  const float a = 0.15;
  const float b = 0.50;
  const float c = 0.10;
  const float d = 0.20;
  const float e = 0.02;
  const float f = 0.30;
  return ((x * (a * x + c * b) + d * e) / (x * (a * x + b) + d * f)) - e / f;
}

float3 HableTonemap(float3 color) {
  const float exposure_bias = 2.0;
  const float white_point = 11.2;
  float3 mapped = HableCurve(color * exposure_bias);
  float3 white_scale = 1.0 / HableCurve(white_point);
  return mapped * white_scale;
}
```

### 各係数の意味

各係数の意味です。A（0.15）は肩の強さで、大きいと明部が早く頭打ちになります。B（0.50）は直線部の強さ（中間の傾き、コントラスト）です。C（0.10）は直線部の角度で、直線の傾きを調整します。D（0.20）はつま先の強さで、大きいと暗部が沈みます。E（0.02）とF（0.30）は、つま先の分子と分母で、つま先の細かい形を決めます。W（11.2）は白点で、この入力で出力がちょうど 1 になります。

### 白点で正規化する理由

**曲線は、x が大きくても 1 に届きません**。**白点 W の出力で割る**（`white_scale`）ことで**入力 W のとき出力がちょうど 1** になります。

曲線は x が大きくても 1 に届かないので、白点 W の出力で割る（`white_scale`）ことで、入力 W のとき出力がちょうど 1 になるようにします。具体的な値は、入力 0 が出力 0、入力が中間灰（0.18）の 2 倍で約 0.22、入力が 1 の 2 倍で約 0.55、入力 11.2 で 1 です。

### `exposure_bias`（2.0）

**曲線の前に掛ける倍率**で、**中間の明るさを合わせる**ためのものです。**露出（[Exposure](exposure.md)）が別にある**ので**二重にならないよう**、**この値は「曲線に合わせた補正」と考え、あまり動かさない**ようにします。

## 色の保ち方

**Hable をチャンネルごとに掛ける**と、**フィルムのように明るい色が白へ向かう**絵になります。**色相を保ちたい**なら、**輝度に掛けて比率を保つ**方式もあります（[Preserving Hue](hue-preservation.md)）。

## より良いやり方

より良いやり方を挙げます。係数 A〜F をアーティストが調整できるパラメータとして出し、肩・つま先・白点をスライダーで調整できるようにします。そのまま 6 個の係数を出すと扱いにくいので、「つま先の強さ」「肩の長さ」「白点」の 3 つだけを見せ、内部で A〜F に変換する設計もあります。計算の重い曲線は、3D LUT に焼いて、1 回の表引きにできます（[Color Grading](../color-grading/index.md)）。ACES や AgX と同じシーンで比べて、色の出方で選びます（[ACES](aces.md)、[AgX](agx.md)）。HDR ディスプレイでは別の曲線が必要です（[Gamma and HDR Output](gamma-srgb.md)）。

## よくあるミス

??? failure "露出を `exposure_bias` で調整して、自動露出と二重になる"
    **明るさの調整は、露出（EV）で**。**`exposure_bias` は固定**。

??? failure "白点を変えたのに、白が出ない"
    **`white_scale` の計算を忘れた**。**`1 / HableCurve(white_point)` を掛ける**。

??? failure "暗部が潰れすぎて、夜のシーンが真っ黒"
    **つま先（D・E・F）を弱める**、**露出を上げる**、**曲線の前にオフセット**を加える。

??? failure "色相が変わって、赤い物がオレンジに見える"
    **チャンネルごとの副作用**。**輝度ベースにする、または AgX・ACES の色補正**を検討。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フィルミック ＝ <strong>S 字（つま先・直線部・肩）</strong>。<strong>暗部を締め、明部を滑らかに</strong>
    - [x] Hable の式は<strong>係数 A〜F ＋ 白点 W</strong>。<strong>白点の出力で割って 1 に正規化</strong>
    - [x] <strong>つま先が暗部を沈める</strong>ので、<strong>Reinhard より締まる</strong>
    - [x] <strong>露出は別に</strong>。<strong>`exposure_bias` は固定</strong>
    - [x] <strong>パラメータ化・LUT 化</strong>で<strong>画作りを制御しやすく</strong>

## 参考

- Hable, "Uncharted 2: HDR Lighting"（GDC 2010）
- Hable, "Filmic Tonemapping Operators"（filmicworlds.com）
- Duiker, "Filmic Tonemapping for Real-time Rendering"（SIGGRAPH 2010）

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [Reinhard](reinhard.md)
- [ACES](aces.md)
- [Preserving Hue](hue-preservation.md)
