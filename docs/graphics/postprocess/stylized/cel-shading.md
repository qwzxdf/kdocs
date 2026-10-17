---
title: セル シェーディング
tags:
  - 描画
---

# セル シェーディング

<strong>セル シェーディング（トゥーン シェーディング）</strong>は、**陰影を滑らかなグラデーションではなく、数段階（2〜3 段）に区切る**表現です。<strong>手描きアニメの「セル画」</strong>のように、<strong>「明るい面」「影の面」がくっきり分かれる</strong>ので、**アニメ調の絵**になります。**ライティングの結果（明るさ）を、段階に変換する関数**が**核**で、**ランプ テクスチャ**で**自由に調整**できます。**写実的な高品質とは別の方向の表現**で、**画風に合うかどうか**が**基準**です。このページでは、**基本の段階化・ランプ テクスチャ・なめらかな境・スペキュラとリム ライト・影の色・影を受けるときの扱い**を説明します。

!!! tip "ポイント"
    - セル シェーディング ＝ <strong>ライティングの明るさを、数段階に区切る</strong>。
    - 基本 ＝ <strong>`N·L`（拡散）を、しきい値で段階化</strong>。<strong>`step` や `smoothstep`</strong>。
    - <strong>ランプ テクスチャ</strong>：<strong>`N·L` を座標に色を引く 1D テクスチャ</strong>。<strong>アーティストが段階を自由に調整</strong>できる。
    - <strong>境を少しぼかす（`smoothstep`）</strong>と<strong>ちらつき・ジャギーが減る</strong>。
    - <strong>影の色</strong>を<strong>暗い灰色でなく、色相を変えた暗い色</strong>に。
    - <strong>スペキュラ</strong>は<strong>しきい値で、くっきりした白いハイライト</strong>。<strong>リム ライト</strong>で<strong>輪郭を明るく</strong>。

## 基本：N·L を段階化

**普通のライティング**は、**`N·L`（法線と光の向きの内積）で、明るさが滑らかに変わります**。**セルではこれをしきい値で数段階に変換**します。

<svg class="fig illust" viewBox="0 0 780 230" role="img" aria-label="セル シェーディング">
<text x="20" y="26" class="fig-title">滑らかな明るさを、段階に区切る</text>
<defs><linearGradient id="cs-smooth" x1="0" x2="1"><stop offset="0" stop-color="#1e293b"/><stop offset="1" stop-color="#f8e9c8"/></linearGradient></defs>
<g transform="translate(40,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">通常（滑らか）</text>
<circle cx="90" cy="70" r="62" fill="url(#cs-smooth)"/>
</g>
<g transform="translate(280,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">2 段（明・影）</text>
<circle cx="90" cy="70" r="62" fill="#f8e9c8"/><path d="M90,8 A62,62 0 0 0 90,132 Z" fill="#8a7a90" transform="translate(20,0)"/>
</g>
<g transform="translate(520,56)">
<text x="0" y="-8" style="font-size:13px;font-weight:700">3 段（明・中・影）</text>
<circle cx="90" cy="70" r="62" fill="#f8e9c8"/><circle cx="90" cy="70" r="62" fill="#b5a3a8" clip-path="inset(0 0 0 0)" opacity="0"/>
<path d="M90,8 A62,62 0 0 0 90,132 Z" fill="#b5a3a8" transform="translate(30,0)"/><path d="M90,8 A62,62 0 0 0 90,132 Z" fill="#6f5f78" transform="translate(5,0)"/>
</g>
</svg>

```hlsl
float3 CelShade(float3 albedo, float3 normal, float3 light_dir, float3 light_color) {
  float n_dot_l = dot(normal, light_dir);
  float lit = step(0.0, n_dot_l);
  float3 shadow_color = albedo * float3(0.55, 0.5, 0.7);
  return lerp(shadow_color, albedo * light_color, lit);
}
```

| 点 | 説明 |
| --- | --- |
| **`step(0, N·L)`** | **光に向いていれば 1、背を向けていれば 0**（**2 段**） |
| **`shadow_color`** | **影の色**（**暗い灰色でなく、色味のある暗い色**） |
| **`lerp`** | **影と明部を切り替え** |

## なめらかな境

**`step` は境がジャギーで、動くとちらつきます**。<strong>境を少しだけぼかす（`smoothstep`）</strong>と**きれい**です。

```hlsl
float Toon(float n_dot_l, float threshold, float softness) {
  return smoothstep(threshold - softness, threshold + softness, n_dot_l);
}
```

| `softness` | 見た目 |
| --- | --- |
| **0.0〜0.01** | <strong>ほぼシャープ（アニメ調）</strong> |
| **0.05〜0.1** | <strong>少し柔らかい（水彩・イラスト調）</strong> |

## ランプ テクスチャ

**`N·L`（0〜1 に直したもの）を座標に色を引く 1D テクスチャ**です。**アーティストが段階の数・境の位置・色の変化を自由に描けます**。

```hlsl
Texture2D ramp_texture : register(t3);

float3 CelShadeRamp(float3 albedo, float3 normal, float3 light_dir) {
  float n_dot_l = dot(normal, light_dir) * 0.5 + 0.5;
  float3 ramp = ramp_texture.SampleLevel(clamp_linear, float2(n_dot_l, 0.5), 0).rgb;
  return albedo * ramp;
}
```

| 点 | 説明 |
| --- | --- |
| **`N·L × 0.5 + 0.5`** | **−1〜1 を 0〜1 に**（**ハーフ ランバート**） |
| **ランプの形** | **階段状の画像をバイリニアでサンプル** |
| **利点** | **コードを変えずに画風を変えられる**（**キャラごとにランプを差し替える**） |

<!-- fig:cel-ramp:begin -->

<svg class="fig illust motion" data-fig="cel-ramp" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-cel-ramp" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">セル シェーディング:なめらかな明るさを、数段に区切る</text>
<rect x="50" y="70" width="320" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="130.0" y1="70" x2="130.0" y2="290" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="125.0" x2="370" y2="125.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="210.0" y1="70" x2="210.0" y2="290" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="180.0" x2="370" y2="180.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="290.0" y1="70" x2="290.0" y2="290" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="235.0" x2="370" y2="235.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="370" y="310" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">N·L（光との向き）</text>
<text x="50" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">明るさ</text>
<path d="M50.0,290.0 L66.0,279.0 L82.0,268.0 L98.0,257.0 L114.0,246.0 L130.0,235.0 L146.0,224.0 L162.0,213.0 L178.0,202.0 L194.0,191.0 L210.0,180.0 L226.0,169.0 L242.0,158.0 L258.0,147.0 L274.0,136.0 L290.0,125.0 L306.0,114.0 L322.0,103.0 L338.0,92.0 L354.0,81.0 L370.0,70.0" fill="none" stroke="#64748b" stroke-width="3" opacity="1" stroke-dasharray="5 4"/>
<path d="M50.0,257.0 L51.6,257.0 L53.2,257.0 L54.8,257.0 L56.4,257.0 L58.0,257.0 L59.6,257.0 L61.2,257.0 L62.8,257.0 L64.4,257.0 L66.0,257.0 L67.6,257.0 L69.2,257.0 L70.8,257.0 L72.4,257.0 L74.0,257.0 L75.6,257.0 L77.2,257.0 L78.8,257.0 L80.4,257.0 L82.0,257.0 L83.6,257.0 L85.2,257.0 L86.8,257.0 L88.4,257.0 L90.0,257.0 L91.6,257.0 L93.2,257.0 L94.8,257.0 L96.4,257.0 L98.0,257.0 L99.6,257.0 L101.2,257.0 L102.8,257.0 L104.4,257.0 L106.0,257.0 L107.6,257.0 L109.2,257.0 L110.8,257.0 L112.4,257.0 L114.0,257.0 L115.6,257.0 L117.2,257.0 L118.8,257.0 L120.4,257.0 L122.0,257.0 L123.6,257.0 L125.2,257.0 L126.8,257.0 L128.4,257.0 L130.0,257.0 L131.6,257.0 L133.2,257.0 L134.8,257.0 L136.4,257.0 L138.0,257.0 L139.6,257.0 L141.2,257.0 L142.8,257.0 L144.4,257.0 L146.0,169.0 L147.6,169.0 L149.2,169.0 L150.8,169.0 L152.4,169.0 L154.0,169.0 L155.6,169.0 L157.2,169.0 L158.8,169.0 L160.4,169.0 L162.0,169.0 L163.6,169.0 L165.2,169.0 L166.8,169.0 L168.4,169.0 L170.0,169.0 L171.6,169.0 L173.2,169.0 L174.8,169.0 L176.4,169.0 L178.0,169.0 L179.6,169.0 L181.2,169.0 L182.8,169.0 L184.4,169.0 L186.0,169.0 L187.6,169.0 L189.2,169.0 L190.8,169.0 L192.4,169.0 L194.0,169.0 L195.6,169.0 L197.2,169.0 L198.8,169.0 L200.4,169.0 L202.0,169.0 L203.6,169.0 L205.2,169.0 L206.8,169.0 L208.4,169.0 L210.0,169.0 L211.6,169.0 L213.2,169.0 L214.8,169.0 L216.4,169.0 L218.0,169.0 L219.6,169.0 L221.2,169.0 L222.8,169.0 L224.4,169.0 L226.0,169.0 L227.6,169.0 L229.2,169.0 L230.8,169.0 L232.4,169.0 L234.0,169.0 L235.6,169.0 L237.2,169.0 L238.8,169.0 L240.4,169.0 L242.0,169.0 L243.6,169.0 L245.2,169.0 L246.8,169.0 L248.4,169.0 L250.0,169.0 L251.6,169.0 L253.2,169.0 L254.8,169.0 L256.4,169.0 L258.0,169.0 L259.6,169.0 L261.2,169.0 L262.8,169.0 L264.4,169.0 L266.0,169.0 L267.6,169.0 L269.2,169.0 L270.8,169.0 L272.4,169.0 L274.0,70.0 L275.6,70.0 L277.2,70.0 L278.8,70.0 L280.4,70.0 L282.0,70.0 L283.6,70.0 L285.2,70.0 L286.8,70.0 L288.4,70.0 L290.0,70.0 L291.6,70.0 L293.2,70.0 L294.8,70.0 L296.4,70.0 L298.0,70.0 L299.6,70.0 L301.2,70.0 L302.8,70.0 L304.4,70.0 L306.0,70.0 L307.6,70.0 L309.2,70.0 L310.8,70.0 L312.4,70.0 L314.0,70.0 L315.6,70.0 L317.2,70.0 L318.8,70.0 L320.4,70.0 L322.0,70.0 L323.6,70.0 L325.2,70.0 L326.8,70.0 L328.4,70.0 L330.0,70.0 L331.6,70.0 L333.2,70.0 L334.8,70.0 L336.4,70.0 L338.0,70.0 L339.6,70.0 L341.2,70.0 L342.8,70.0 L344.4,70.0 L346.0,70.0 L347.6,70.0 L349.2,70.0 L350.8,70.0 L352.4,70.0 L354.0,70.0 L355.6,70.0 L357.2,70.0 L358.8,70.0 L360.4,70.0 L362.0,70.0 L363.6,70.0 L365.2,70.0 L366.8,70.0 L368.4,70.0 L370.0,70.0" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<line x1="146.0" y1="70" x2="146.0" y2="290" stroke="#e2e8f0" stroke-width="2" stroke-dasharray="4 3"/>
<line x1="274.0" y1="70" x2="274.0" y2="290" stroke="#e2e8f0" stroke-width="2" stroke-dasharray="4 3"/>
<text x="98.0" y="249.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2563eb">影</text>
<text x="210.0" y="161.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2563eb">中間</text>
<text x="322.0" y="86.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2563eb">明</text>
<circle cx="50.0" cy="290.0" r="7" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0874;0.1052;0.1230;0.1409;0.1587;0.1765;0.1943;0.2122;0.2300;0.2478;0.2657;0.2835;0.3013;0.3191;0.3370;0.3548;0.3726;0.3904;0.4083;0.4261;0.4439;0.4617;0.4796;0.4974;0.5152;0.5330;0.5509;0.5687;0.5865;0.6043;0.6222;0.6400;0.6578;0.6757;0.6935;0.7113;0.7291;0.7470;0.7648;0.7826;1.0000" values="50;50;58;66;74;82;90;98;106;114;122;130;138;146;154;162;170;178;186;194;202;210;218;226;234;242;250;258;266;274;282;290;298;306;314;322;330;338;346;354;362;370;370"/><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0692;0.0696;0.0874;0.1052;0.1230;0.1409;0.1587;0.1765;0.1943;0.2122;0.2300;0.2478;0.2657;0.2835;0.3013;0.3191;0.3370;0.3548;0.3726;0.3904;0.4083;0.4261;0.4439;0.4617;0.4796;0.4974;0.5152;0.5330;0.5509;0.5687;0.5865;0.6043;0.6222;0.6400;0.6578;0.6757;0.6935;0.7113;0.7291;0.7470;0.7648;0.7826;1.0000" values="290;290;257;257;257;257;257;257;257;257;257;257;257;257;169;169;169;169;169;169;169;169;169;169;169;169;169;169;169;169;70;70;70;70;70;70;70;70;70;70;70;70;70;70"/></circle>
<text x="430" y="70" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">球の表面（暗い側 → 明るい側）</text>
<text x="430" y="92" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">なめらか</text>
<rect x="430" y="100" width="17" height="52" fill="#353535"/>
<rect x="448" y="100" width="17" height="52" fill="#575757"/>
<rect x="466" y="100" width="17" height="52" fill="#6e6e6e"/>
<rect x="484" y="100" width="17" height="52" fill="#808080"/>
<rect x="502" y="100" width="17" height="52" fill="#8f8f8f"/>
<rect x="520" y="100" width="17" height="52" fill="#9d9d9d"/>
<rect x="538" y="100" width="17" height="52" fill="#a9a9a9"/>
<rect x="556" y="100" width="17" height="52" fill="#b5b5b5"/>
<rect x="574" y="100" width="17" height="52" fill="#bfbfbf"/>
<rect x="592" y="100" width="17" height="52" fill="#c9c9c9"/>
<rect x="610" y="100" width="17" height="52" fill="#d3d3d3"/>
<rect x="628" y="100" width="17" height="52" fill="#dbdbdb"/>
<rect x="646" y="100" width="17" height="52" fill="#e4e4e4"/>
<rect x="664" y="100" width="17" height="52" fill="#ececec"/>
<rect x="682" y="100" width="17" height="52" fill="#f4f4f4"/>
<rect x="700" y="100" width="17" height="52" fill="#fbfbfb"/>
<text x="430" y="182" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">セル（3 段）</text>
<rect x="430" y="190" width="17" height="52" fill="#6c6c6c"/>
<rect x="448" y="190" width="17" height="52" fill="#6c6c6c"/>
<rect x="466" y="190" width="17" height="52" fill="#6c6c6c"/>
<rect x="484" y="190" width="17" height="52" fill="#6c6c6c"/>
<rect x="502" y="190" width="17" height="52" fill="#6c6c6c"/>
<rect x="520" y="190" width="17" height="52" fill="#c2c2c2"/>
<rect x="538" y="190" width="17" height="52" fill="#c2c2c2"/>
<rect x="556" y="190" width="17" height="52" fill="#c2c2c2"/>
<rect x="574" y="190" width="17" height="52" fill="#c2c2c2"/>
<rect x="592" y="190" width="17" height="52" fill="#c2c2c2"/>
<rect x="610" y="190" width="17" height="52" fill="#c2c2c2"/>
<rect x="628" y="190" width="17" height="52" fill="#ffffff"/>
<rect x="646" y="190" width="17" height="52" fill="#ffffff"/>
<rect x="664" y="190" width="17" height="52" fill="#ffffff"/>
<rect x="682" y="190" width="17" height="52" fill="#ffffff"/>
<rect x="700" y="190" width="17" height="52" fill="#ffffff"/>
<polygon points="438,288 431,300 445,300" fill="#e5484d"><animate attributeName="points" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0692;0.0696;0.0874;0.1052;0.1230;0.1409;0.1587;0.1765;0.1943;0.2122;0.2300;0.2478;0.2657;0.2835;0.3013;0.3191;0.3370;0.3548;0.3726;0.3904;0.4083;0.4261;0.4439;0.4617;0.4796;0.4974;0.5152;0.5330;0.5509;0.5687;0.5865;0.6043;0.6222;0.6400;0.6578;0.6757;0.6935;0.7113;0.7291;0.7470;0.7648;0.7826;1.0000" values="438,288 431,300 445,300;438,288 431,300 445,300;430.0,288 423.0,300 437.0,300;437.2,288 430.2,300 444.2,300;444.4,288 437.4,300 451.4,300;451.6,288 444.6,300 458.6,300;458.8,288 451.8,300 465.8,300;466.0,288 459.0,300 473.0,300;473.2,288 466.2,300 480.2,300;480.4,288 473.4,300 487.4,300;487.6,288 480.6,300 494.6,300;494.8,288 487.8,300 501.8,300;502.0,288 495.0,300 509.0,300;509.2,288 502.2,300 516.2,300;516.4,288 509.4,300 523.4,300;523.6,288 516.6,300 530.6,300;530.8,288 523.8,300 537.8,300;538.0,288 531.0,300 545.0,300;545.2,288 538.2,300 552.2,300;552.4,288 545.4,300 559.4,300;559.6,288 552.6,300 566.6,300;566.8,288 559.8,300 573.8,300;574.0,288 567.0,300 581.0,300;581.2,288 574.2,300 588.2,300;588.4,288 581.4,300 595.4,300;595.6,288 588.6,300 602.6,300;602.8,288 595.8,300 609.8,300;610.0,288 603.0,300 617.0,300;617.2,288 610.2,300 624.2,300;624.4,288 617.4,300 631.4,300;631.6,288 624.6,300 638.6,300;638.8,288 631.8,300 645.8,300;646.0,288 639.0,300 653.0,300;653.2,288 646.2,300 660.2,300;660.4,288 653.4,300 667.4,300;667.6,288 660.6,300 674.6,300;674.8,288 667.8,300 681.8,300;682.0,288 675.0,300 689.0,300;689.2,288 682.2,300 696.2,300;696.4,288 689.4,300 703.4,300;703.6,288 696.6,300 710.6,300;710.8,288 703.8,300 717.8,300;718.0,288 711.0,300 725.0,300;718.0,288 711.0,300 725.0,300"/></polygon>
<rect x="430" y="320" width="130" height="40" fill="#6c6c6c" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0874;0.1052;0.1230;0.1409;0.1587;0.1765;0.1943;0.2122;0.2300;0.2478;0.2657;0.2835;0.3013;0.3191;0.3370;0.3548;0.3726;0.3904;0.4083;0.4261;0.4439;0.4617;0.4796;0.4974;0.5152;0.5330;0.5509;0.5687;0.5865;0.6043;0.6222;0.6400;0.6578;0.6757;0.6935;0.7113;0.7291;0.7470;0.7648;0.7826;1.0000" values="#6c6c6c;#6c6c6c;#6c6c6c;#6c6c6c;#6c6c6c;#6c6c6c;#6c6c6c;#6c6c6c;#6c6c6c;#6c6c6c;#6c6c6c;#6c6c6c;#6c6c6c;#c2c2c2;#c2c2c2;#c2c2c2;#c2c2c2;#c2c2c2;#c2c2c2;#c2c2c2;#c2c2c2;#c2c2c2;#c2c2c2;#c2c2c2;#c2c2c2;#c2c2c2;#c2c2c2;#c2c2c2;#c2c2c2;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff"/></rect>
<text x="570" y="345" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">← 今の明るさ（段でぱっと切り替わる）</text>
<text x="50" y="352" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b" opacity="0">ランプ（表）を引くだけ。段の数・境目で画風が変わる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
</svg>

<!-- fig:cel-ramp:end -->

## 影の色

**影を単純に「暗くする」と、絵が重く、汚く見えます**。**影は色相を少し変え、彩度を保った、暗い色**に**するとアニメ的**です。

| 影の付け方 | 見た目 |
| --- | --- |
| <strong>単純に暗く（× 0.5）</strong> | **灰色っぽく、汚い** |
| <strong>色相をずらす（青・紫寄り）</strong> | **アニメ調の澄んだ影** |
| **肌：赤みを保つ** | **健康的な肌** |
| **アルベドごとの影色** | <strong>材質ごとに別の影の色（テクスチャ・パラメータ）</strong> |

```hlsl
float3 shadow_tint = lerp(float3(1, 1, 1), float3(0.6, 0.55, 0.85), shadow_strength);
float3 shaded = albedo * shadow_tint;
```

## スペキュラとリム ライト

| 要素 | 内容 |
| --- | --- |
| **スペキュラ** | **ハーフ ベクトルとの内積を、しきい値で 2 値化して、くっきりした白いハイライト** |
| **リム ライト** | **視線と法線が直角に近い所（輪郭付近）を、明るくして、輪郭を際立たせる** |

```hlsl
float ToonSpecular(float3 normal, float3 view_dir, float3 light_dir, float shininess, float threshold) {
  float3 half_vector = normalize(light_dir + view_dir);
  float n_dot_h = saturate(dot(normal, half_vector));
  return step(threshold, pow(n_dot_h, shininess));
}

float RimLight(float3 normal, float3 view_dir, float power, float threshold) {
  float rim = 1.0 - saturate(dot(normal, view_dir));
  return step(threshold, pow(rim, power));
}
```

| 点 | 説明 |
| --- | --- |
| **`step(threshold, pow(...))`** | **くっきりした、はっきりした形のハイライト** |
| **リム ライト** | **輪郭が背景から浮き出る**（**暗い背景で特に効く**） |
| **向き** | **光の向きに沿ったリムだけにすると、自然**（**`rim × N·L`**） |

## 影を受ける

**シャドウ マップの影**（[影](../../shadows/index.md)）を**セルの陰影に取り込む**には**影の判定値（0〜1）を、`N·L` と掛け合わせます**。

```hlsl
float shadow = SampleShadow(world_position);
float n_dot_l = dot(normal, light_dir);
float toon_input = n_dot_l * shadow;
float lit = smoothstep(0.0, 0.02, toon_input);
```

**シャドウ マップの境が、PCF などで柔らかいと、セルの境がぎざぎざになる**ので、**境の硬さを合わせる**（**影も段階化する**）のがよい**です**。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **ランプ テクスチャ** | **アーティストが画風を調整** |
| **影色を色相を変えた暗い色に** | **澄んだ影** |
| **`smoothstep` で境を滑らかに** | **ジャギー・ちらつきを防ぐ** |
| **輪郭線と併用** | <strong>アウトライン（[背面法](outline-hull.md)・[画面空間](outline-edge.md)）</strong> |
| **ライトの扱いをメイン ライトのみに** | **複数ライトを段階化すると複雑** |
| **顔の影を別に調整** | <strong>顔の陰影は法線を補正（顔の影が汚くならない）</strong> |
| **キャラごとのランプ・影色** | **材質ごとのパラメータ** |

## よくあるミス

??? failure "影の境がジャギー・ちらつく"
    **`smoothstep` で、狭い範囲をぼかす**。

??? failure "影が灰色っぽく、絵が汚い"
    **影色に色相を持たせる**。

??? failure "複数のライトを、全部段階化して、ごちゃごちゃする"
    **メイン ライトだけセル化**し、**他は弱い環境光**に。

??? failure "顔に、鼻や顎の汚い影が出る"
    **顔の法線を平らにする**（**法線の補正**）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] セル シェーディング ＝ <strong>ライティングの明るさを、数段階に区切る</strong>
    - [x] <strong>`N·L` をしきい値で段階化</strong>。<strong>`smoothstep` で境を滑らかに</strong>
    - [x] <strong>ランプ テクスチャ</strong>で<strong>画風を自由に調整</strong>
    - [x] <strong>影は、色相を変えた暗い色</strong>に
    - [x] <strong>スペキュラ・リム ライトは、くっきり</strong>。<strong>輪郭線と併用</strong>

## 参考

- Xu et al., "Guilty Gear Xrd's Art Style: The X Factor Between 2D and 3D"（GDC 2015）
- Lake et al., "Stylized Rendering Techniques for Scalable Real-Time 3D Animation"（NPAR 2000）
- Barla et al., "X-Toon: An Extended Toon Shader"（NPAR 2006）

## 関連ページ

- [輪郭線・トゥーン](index.md)
- [背面法の輪郭線](outline-hull.md)
- [ポスタライズとハーフトーン](posterize-halftone.md)
- [法線とライティング](../../../3d/lighting-normals.md)
