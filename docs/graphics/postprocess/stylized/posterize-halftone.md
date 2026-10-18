---
title: Posterization and Halftone
tags:
  - 描画
---

# Posterization and Halftone

**ポスタライズ**は、**色の段階（階調）を減らして、ポスターのように平らな色の面にする**表現です。**ハーフトーンは、網点（ドット）の大きさで濃淡を表す、漫画・印刷のような表現**です。**どちらも、3D の絵を「イラスト・漫画・印刷物」の質感に近づける**ための**後処理**で、**セル シェーディングや輪郭線と組み合わせて、画風を作ります**。**写実的な品質とは別の軸の、好みの表現**です。このページでは、**ポスタライズの式・色数・ディザリングとの組み合わせ・ハーフトーンの網点・クロスハッチ（線の濃淡）・使いどころ**を説明します。

!!! tip "ポイント"
    - ポスタライズ ＝ <strong>各チャンネルを、N 段階に丸める</strong>（<strong>`floor(c × N) / N`</strong>）。<strong>色の面が平らに</strong>。
    - <strong>輝度だけを丸める</strong>と<strong>色相を保てる</strong>。
    - <strong>ハーフトーン</strong> ＝ <strong>明るさに応じた大きさの円（網点）</strong>を、<strong>格子状に並べる</strong>。<strong>角度を付ける</strong>と<strong>漫画風</strong>。
    - <strong>クロスハッチ</strong> ＝ <strong>線の本数で濃淡</strong>（<strong>ペン画・版画風</strong>）。
    - <strong>丸めの境は、ちらつきやすい</strong>。<strong>TAA・ディザリングで抑える</strong>。
    - <strong>どれも画風の選択</strong>。<strong>写実的な絵を良くする技法ではない</strong>。

## Posterization {#ポスタライズ}

**色の連続的な階調**を**少ない段階に丸めます**。

<div class="formula">c' = floor( c × N ) / N　（N：段階数）</div>

```hlsl
float3 Posterize(float3 color, float levels) {
  return floor(color * levels + 0.5) / levels;
}
```

段階数による見た目です。2 段階は白黒で、極端なポスターになります。4〜6 段階はポスターやグラフィック的な絵です。8〜16 段階は控えめで、バンディングが目立ち始めます。

<svg class="fig illust" viewBox="0 0 780 210" role="img" aria-label="ポスタライズ">
<text x="20" y="26" class="fig-title">滑らかなグラデーションを、数段階の面に</text>
<defs><linearGradient id="ph-g" x1="0" x2="1"><stop offset="0" stop-color="#1e293b"/><stop offset="1" stop-color="#fde68a"/></linearGradient></defs>
<g transform="translate(40,56)">
<text x="0" y="-8" style="font-size:12px">元（滑らか）</text><rect x="0" y="0" width="680" height="30" fill="url(#ph-g)"/>
<text x="0" y="52" style="font-size:12px">4 段階</text>
<g><rect x="0" y="60" width="170" height="30" fill="#1e293b"/><rect x="170" y="60" width="170" height="30" fill="#5b5361"/><rect x="340" y="60" width="170" height="30" fill="#b09c78"/><rect x="510" y="60" width="170" height="30" fill="#fde68a"/></g>
<text x="0" y="112" style="font-size:12px">2 段階</text>
<g><rect x="0" y="120" width="340" height="30" fill="#1e293b"/><rect x="340" y="120" width="340" height="30" fill="#fde68a"/></g>
</g>
</svg>

### Rounding Only Luminance {#輝度だけ丸める}

**RGB 別々に丸めると、色相がずれます**（**例：茶色が緑や赤に分かれる**）。**輝度だけを丸め、色の比率を保つ**方が**色の自然さが保たれます**。

```hlsl
float3 PosterizeLuma(float3 color, float levels) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  float quantized = floor(luma * levels + 0.5) / levels;
  return color * (quantized / max(luma, 1e-4));
}
```

ポスタライズの対象は 2 通りです。RGB 別々に丸めると、カラフルでグラフィック的になりますが、色がずれます。輝度だけを丸めると、色味は保ち、陰影だけが段階化され、セル シェーディングに近くなります。

## Combining with Dithering {#ディザリングと組み合わせる}

**丸めるだけだと段の境がくっきりします**。**丸める前にノイズやパターン（ディザ）を足す**と**境が模様のように混ざります**（**古いゲーム機・版画風**）。

```hlsl
float3 PosterizeDithered(float3 color, float levels, float2 pixel_position) {
  float dither = Bayer4x4(pixel_position) - 0.5;
  return floor(color * levels + 0.5 + dither) / levels;
}
```

段の境の処理です。ベイヤー（規則的）ディザは、レトロで格子状の模様になります。ブルー ノイズは自然な粒状になります。ディザなしなら、平らな色の面になります。

## Halftone (Dots) {#ハーフトーン網点}

**印刷・漫画の網点**は**明るさに応じた大きさの円を、格子状に並べて濃淡を表します**。

網点の要素です。格子は等間隔の点の配置で、傾けると漫画風になります。点の大きさは、暗いほど大きく、明るいほど小さくします。角度は 45°（白黒）が標準で、カラーは色ごとに別の角度を使います（CMYK の網点）。

```hlsl
float Halftone(float2 pixel_position, float luminance, float cell_size, float angle) {
  float s = sin(angle);
  float c = cos(angle);
  float2 rotated = float2(c * pixel_position.x - s * pixel_position.y, s * pixel_position.x + c * pixel_position.y);
  float2 cell = frac(rotated / cell_size) - 0.5;
  float distance_from_center = length(cell);
  float radius = sqrt(1.0 - luminance) * 0.7;
  return smoothstep(radius + 0.05, radius - 0.05, distance_from_center);
}
```

| 点 | 説明 |
| --- | --- |
| **`rotated / cell_size`** | **傾けた格子のセル座標** |
| **`frac − 0.5`** | **セルの中心を原点に** |
| **`radius = √(1 − 輝度) × 0.7`** | **暗いほど、円が大きい**（**面積が明るさに比例するよう√**） |
| **`smoothstep`** | <strong>円の縁を少しぼかす（ジャギー防止）</strong> |

<!-- fig:halftone-dots:begin -->

<svg class="fig illust motion" data-fig="halftone-dots" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-halftone-dots" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ハーフトーン: 明るさを、点の大きさに置き換える。点の面積が、暗さに比例するようにする</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">黒 → 白のグラデーションを、12×4 のセルの点で表す。点の半径の決め方を 2 通り比べる(半径 ∝ 暗さ と、面積 ∝ 暗さ)</text>
<text x="60.0" y="108" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">元のグラデーション(暗い → 明るい)</text>
<rect x="60.0" y="112.0" width="54.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#0b0b0b"/></rect>
<rect x="114.0" y="112.0" width="54.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#202020"/></rect>
<rect x="168.0" y="112.0" width="54.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#353535"/></rect>
<rect x="222.0" y="112.0" width="54.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#4a4a4a"/></rect>
<rect x="276.0" y="112.0" width="54.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#606060"/></rect>
<rect x="330.0" y="112.0" width="54.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#757575"/></rect>
<rect x="384.0" y="112.0" width="54.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#8a8a8a"/></rect>
<rect x="438.0" y="112.0" width="54.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#9f9f9f"/></rect>
<rect x="492.0" y="112.0" width="54.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#b5b5b5"/></rect>
<rect x="546.0" y="112.0" width="54.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#cacaca"/></rect>
<rect x="600.0" y="112.0" width="54.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#dfdfdf"/></rect>
<rect x="654.0" y="112.0" width="54.3" height="20.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#f4f4f4"/></rect>
<rect x="60.0" y="112" width="648.0" height="20.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="154" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">半径 ∝ 暗さ</text>
<rect x="60.0" y="160" width="648.0" height="54.0" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="87.0" cy="187.0" r="25.88" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="0;0;1;1"/></circle>
<circle cx="141.0" cy="187.0" r="23.62" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0812;0.0814;1.0000" values="0;0;1;1"/></circle>
<circle cx="195.0" cy="187.0" r="21.38" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0928;0.0930;1.0000" values="0;0;1;1"/></circle>
<circle cx="249.0" cy="187.0" r="19.12" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1045;0.1047;1.0000" values="0;0;1;1"/></circle>
<circle cx="303.0" cy="187.0" r="16.88" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1161;0.1163;1.0000" values="0;0;1;1"/></circle>
<circle cx="357.0" cy="187.0" r="14.63" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1277;0.1279;1.0000" values="0;0;1;1"/></circle>
<circle cx="411.0" cy="187.0" r="12.38" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1393;0.1395;1.0000" values="0;0;1;1"/></circle>
<circle cx="465.0" cy="187.0" r="10.12" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1510;0.1512;1.0000" values="0;0;1;1"/></circle>
<circle cx="519.0" cy="187.0" r="7.87" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1626;0.1628;1.0000" values="0;0;1;1"/></circle>
<circle cx="573.0" cy="187.0" r="5.63" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1742;0.1744;1.0000" values="0;0;1;1"/></circle>
<circle cx="627.0" cy="187.0" r="3.38" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1859;0.1860;1.0000" values="0;0;1;1"/></circle>
<circle cx="681.0" cy="187.0" r="1.12" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1975;0.1977;1.0000" values="0;0;1;1"/></circle>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2091;0.2093;1.0000" values="0;0;1;1"/><text x="60.0" y="236.0" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">点の面積の割合と、目標の暗さ(最大 π/4 = 0.785)との差の平均: 0.131</text>
</g>
<text x="60.0" y="284" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">面積 ∝ 暗さ(半径 ∝ √暗さ)</text>
<rect x="60.0" y="290" width="648.0" height="54.0" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="87.0" cy="317.0" r="26.43" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3254;0.3256;1.0000" values="0;0;1;1"/></circle>
<circle cx="141.0" cy="317.0" r="25.26" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3370;0.3372;1.0000" values="0;0;1;1"/></circle>
<circle cx="195.0" cy="317.0" r="24.02" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3487;0.3488;1.0000" values="0;0;1;1"/></circle>
<circle cx="249.0" cy="317.0" r="22.72" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3603;0.3605;1.0000" values="0;0;1;1"/></circle>
<circle cx="303.0" cy="317.0" r="21.35" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3719;0.3721;1.0000" values="0;0;1;1"/></circle>
<circle cx="357.0" cy="317.0" r="19.87" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3835;0.3837;1.0000" values="0;0;1;1"/></circle>
<circle cx="411.0" cy="317.0" r="18.28" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3952;0.3953;1.0000" values="0;0;1;1"/></circle>
<circle cx="465.0" cy="317.0" r="16.53" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4068;0.4070;1.0000" values="0;0;1;1"/></circle>
<circle cx="519.0" cy="317.0" r="14.58" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4184;0.4186;1.0000" values="0;0;1;1"/></circle>
<circle cx="573.0" cy="317.0" r="12.32" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4300;0.4302;1.0000" values="0;0;1;1"/></circle>
<circle cx="627.0" cy="317.0" r="9.55" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4417;0.4419;1.0000" values="0;0;1;1"/></circle>
<circle cx="681.0" cy="317.0" r="5.51" fill="#111827" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4533;0.4535;1.0000" values="0;0;1;1"/></circle>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4649;0.4651;1.0000" values="0;0;1;1"/><text x="60.0" y="366.0" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">点の面積の割合と、目標の暗さ(最大 π/4 = 0.785)との差の平均: 0.000</text>
</g>
<rect x="30" y="430" width="900" height="60" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="420" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">暗さが 0.5 のセルでは</text>
<text x="50" y="472" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">目標 0.36 に対して、半径 ∝ 暗さ → 0.16(薄すぎ)/ 面積 ∝ 暗さ → 0.36(ちょうど)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5812;0.5814;1.0000" values="0;0;1;1"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">印刷のような、点で濃淡を作る表現<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">半径を暗さに比例させると、明るく出すぎる(面積は半径の 2 乗)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.5812;0.5814;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">面積が暗さに比例するように、半径に √ を掛ける<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5812;0.5814;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:halftone-dots:end -->

### Color Halftone {#カラーのハーフトーン}

**CMYK の 4 色**を**別々の角度**で**重ねる**と、**印刷物のような、カラーの網点**になります。

| インク | 角度 |
| --- | --- |
| <strong>C（シアン）</strong> | **15°** |
| <strong>M（マゼンタ）</strong> | **75°** |
| <strong>Y（イエロー）</strong> | **0°** |
| <strong>K（黒）</strong> | **45°** |

**角度をずらす**ことで**モアレ（干渉縞）を避けます**。

## Cross-Hatching (Line Density) {#クロスハッチ線の濃淡}

**線の本数と向きで濃淡**を**表す**のが**クロスハッチ**で、<strong>ペン画・版画・ゲーム「オブラ・ディン号の帰還」</strong>の**ような絵**になります。

| 明るさ | 線 |
| --- | --- |
| **明るい** | <strong>線なし（白）</strong> |
| **やや暗い** | **斜線 1 方向** |
| **暗い** | <strong>斜線 2 方向（交差）</strong> |
| **とても暗い** | **さらに別の方向を重ねる** |

```hlsl
float Hatch(float2 pixel_position, float luminance) {
  float2 p = pixel_position / kHatchSpacing;
  float line1 = step(0.5, frac(p.x + p.y)) * step(luminance, 0.8);
  float line2 = step(0.5, frac(p.x - p.y)) * step(luminance, 0.55);
  float line3 = step(0.5, frac(p.x)) * step(luminance, 0.3);
  return 1.0 - max(line1, max(line2, line3));
}
```

**画面に固定した網点・線**は<strong>カメラが動くと、「画面に張り付いた模様」</strong>に**見えます**（**シャワー ドア効果**）。**物体の表面（UV やワールド座標）に貼る**と**物体と一緒に動いて自然**です（**トゥーン レンダリングの手法の 1 つ**）。

## Where to Use It {#使いどころ}

| 表現 | 使い方 |
| --- | --- |
| **ポスタライズ** | **グラフィック ノベル・ポスター風・夢のシーン・回想** |
| **ハーフトーン** | **漫画風・印刷物風・コミック調のゲーム** |
| **クロスハッチ** | **ペン画・版画・ノワール** |
| **ディザ付きポスタライズ** | **古いゲーム機風・レトロ・Pixel Art 風** |

## Better Approaches {#より良いやり方}

| 工夫 | 内容 |
| --- | --- |
| **輝度だけ丸める** | **色相が保たれる** |
| **ディザで段の境を混ぜる** | **レトロ・版画風** |
| **網点・線を物体表面に貼る** | **画面に張り付いて見える違和感を避ける** |
| **TAA と相性に注意** | **細かい網点は、TAA でぼけ・モアレ** |
| **強さを時間で切り替える** | **回想・特殊状態** |
| **輪郭線・セルと組み合わせる** | **統一した画風に** |

## Common Mistakes {#よくあるミス}

??? failure "RGB 別々にポスタライズして、色相がずれる"
    **輝度だけを丸める**。

??? failure "網点が、画面に張り付いて見える"
    **物体表面（UV・ワールド）に貼る**。

??? failure "細かい網点が、モアレになる"
    **セルの大きさを大きく**、**解像度に合わせる**、**TAA の影響を確認**。

??? failure "段の境がちらつく"
    **丸める前に軽くぼかす**、**TAA**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] ポスタライズ ＝ <strong>色の階調を N 段階に丸める</strong>。<strong>輝度だけ丸めると色相を保てる</strong>
    - [x] <strong>ディザ</strong>と組み合わせて<strong>レトロ・版画風</strong>
    - [x] ハーフトーン ＝ <strong>明るさに応じた大きさの網点を、傾けた格子に並べる</strong>
    - [x] <strong>クロスハッチ</strong> ＝ <strong>線の本数で濃淡</strong>
    - [x] <strong>画面固定の模様に注意</strong>。<strong>画風の選択</strong>（<strong>好みの問題</strong>）

## References {#参考}

- Praun et al., "Real-Time Hatching"（SIGGRAPH 2001）
- Lake et al., "Stylized Rendering Techniques for Scalable Real-Time 3D Animation"（NPAR 2000）
- Pope, "Return of the Obra Dinn" 開発日誌（TIGSource, ディザリングの解説）

## Related Pages {#関連ページ}

- [Outlines and Toon](index.md)
- [Cel Shading](cel-shading.md)
- [Inverted Hull Outlines](outline-hull.md)
- [Film Grain](../lens-effects/film-grain.md)
