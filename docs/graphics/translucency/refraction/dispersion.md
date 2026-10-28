---
title: Dispersion
tags:
  - 描画
---

# Dispersion

<strong>光の波長ごとに屈折率が違うため、ガラスの縁で色が分かれて見える</strong>ことがあります。赤・緑・青でずらす量を変えると、この効果を作れます。このページでは分散の表現を説明します。

!!! tip "ポイント"
    - 波長ごとに屈折率が違う ＝ 分散。
    - R・G・B でずらす量を変えて、3 回読む。
    - 宝石・プリズムなど、強い分散の物体に効果的。
    - やりすぎない（普通のガラスは、ほぼ目立たない）。

!!! info "このページを読む前に"
    - [Refraction](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 色収差（分散）
<strong>波長ごとに屈折率が少し違う</strong>ので、ガラスの縁で色がずれて見えます（プリズムの虹）。R・G・B で屈折の強さを少しずつ変えて、3 回サンプルします。

```hlsl
float3 background;
background.r = scene_color_copy.Sample(linear_clamp, screen_uv + offset * 1.00).r;
background.g = scene_color_copy.Sample(linear_clamp, screen_uv + offset * 1.03).g;
background.b = scene_color_copy.Sample(linear_clamp, screen_uv + offset * 1.06).b;
```

わずか（数%）の差で十分です。宝石・水晶・厚いガラスで効果的です。

### 分散の原理

物質の屈折率は光の波長によってわずかに違います。たとえばガラスでは青い光（波長が短い）のほうが、赤い光より少し大きく曲がります。ふつうの窓ガラスでは差が小さく気づきませんが、プリズムやダイヤモンド、水滴の縁ではこの差が白い光を虹色に分けて見せます。これが分散です。

### 実装の考え方

RGB の 3 チャンネルで、屈折率を少しずつ変えて背景を 3 回読みます。赤は屈折率が小さいので歪みが小さく、緑は中間、青は歪みが大きいというようにします。それぞれのチャンネルの結果だけを取り出して合成すれば、縁に虹色の色ずれが出ます。

```hlsl
float3 DispersedRefraction(float2 uv, float2 offset, float spread) {
  float r = scene_color_copy.Sample(linear_clamp, uv + offset * (1.0 - spread)).r;
  float g = scene_color_copy.Sample(linear_clamp, uv + offset).g;
  float b = scene_color_copy.Sample(linear_clamp, uv + offset * (1.0 + spread)).b;
  return float3(r, g, b);
}
```

`spread` は 0.02〜0.1 程度の小さな値です。多くのサンプルで波長を細かく分けるほど、虹が滑らかになります（[Chromatic Aberration](../../postprocess/lens-effects/chromatic-aberration.md) の多サンプル版と同じ方法です）。ダイヤモンドのような強い分散を見せたいときは、サンプルを 8 個以上に増やし、各サンプルに波長に応じた色の重みを付けます。コストは屈折の読み込みの回数倍になるので、宝石のように分散が主役の物にだけ使うのが現実的です。

<!-- fig:dispersion-delta:begin -->

<svg class="fig illust motion" data-fig="dispersion-delta" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-dispersion-delta" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">入射角が大きいほど、赤と青の曲がり方の差が広がる(差を 10 倍で表示)</text>
<rect x="70" y="70" width="640" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="230.0" y1="70" x2="230.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="130.0" x2="710" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="70" x2="390.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="190.0" x2="710" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="550.0" y1="70" x2="550.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="250.0" x2="710" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="70" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">屈折角の差 θ赤 − θ青（度 × 10）</text>
<text x="710" y="346" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">入射角 (度)</text>
<text x="70.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0</text>
<text x="283.33" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">30</text>
<text x="496.67" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">60</text>
<text x="710.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">90</text>
<path d="M70.0,310.0 L77.11,307.4 L84.22,304.81 L91.33,302.21 L98.44,299.61 L105.56,297.01 L112.67,294.41 L119.78,291.81 L126.89,289.2 L134.0,286.6 L141.11,283.99 L148.22,281.38 L155.33,278.77 L162.44,276.15 L169.56,273.54 L176.67,270.92 L183.78,268.29 L190.89,265.67 L198.0,263.04 L205.11,260.4 L212.22,257.77 L219.33,255.13 L226.44,252.48 L233.56,249.84 L240.67,247.19 L247.78,244.53 L254.89,241.88 L262.0,239.21 L269.11,236.55 L276.22,233.88 L283.33,231.21 L290.44,228.54 L297.56,225.87 L304.67,223.19 L311.78,220.52 L318.89,217.84 L326.0,215.16 L333.11,212.48 L340.22,209.8 L347.33,207.12 L354.44,204.45 L361.56,201.78 L368.67,199.11 L375.78,196.44 L382.89,193.79 L390.0,191.14 L397.11,188.49 L404.22,185.86 L411.33,183.23 L418.44,180.62 L425.56,178.02 L432.67,175.44 L439.78,172.87 L446.89,170.33 L454.0,167.8 L461.11,165.3 L468.22,162.82 L475.33,160.36 L482.44,157.94 L489.56,155.55 L496.67,153.19 L503.78,150.87 L510.89,148.59 L518.0,146.35 L525.11,144.15 L532.22,142.01 L539.33,139.91 L546.44,137.87 L553.56,135.88 L560.67,133.96 L567.78,132.1 L574.89,130.3 L582.0,128.57 L589.11,126.92 L596.22,125.34 L603.33,123.84 L610.44,122.42 L617.56,121.09 L624.67,119.84 L631.78,118.68 L638.89,117.61 L646.0,116.64 L653.11,115.76 L660.22,114.98 L667.33,114.3 L674.44,113.73 L681.56,113.25 L688.67,112.88 L695.78,112.62 L702.89,112.46 L710.0,112.41" fill="none" stroke="#7c3aed" stroke-width="4" opacity="1"/>
<circle cx="70.0" cy="310.0" r="7" fill="#1f2937"><animate attributeName="cx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0870;0.0986;0.1101;0.1217;0.1333;0.1449;0.1565;0.1681;0.1797;0.1913;0.2029;0.2145;0.2261;0.2377;0.2493;0.2609;0.2725;0.2841;0.2957;0.3072;0.3188;0.3304;0.3420;0.3536;0.3652;0.3768;0.3884;0.4000;0.4116;0.4232;0.4348;0.4464;0.4580;0.4696;0.4812;0.4928;0.5043;0.5159;0.5275;0.5391;0.5507;0.5623;0.5739;0.5855;0.5971;0.6087;0.6203;0.6319;0.6435;0.6551;0.6667;0.6783;0.6899;0.7014;0.7130;0.7246;0.7362;0.7478;0.7594;0.7710;0.7826;1.0000" values="70;70;80.55;91.1;101.64;112.19;122.74;133.29;143.84;154.39;164.93;175.48;186.03;196.58;207.13;217.67;228.22;238.77;249.32;259.87;270.41;280.96;291.51;302.06;312.61;323.16;333.7;344.25;354.8;365.35;375.9;386.44;396.99;407.54;418.09;428.64;439.19;449.73;460.28;470.83;481.38;491.93;502.47;513.02;523.57;534.12;544.67;555.21;565.76;576.31;586.86;597.41;607.96;618.5;629.05;639.6;650.15;660.7;671.24;681.79;692.34;702.89;702.89"/><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0870;0.0986;0.1101;0.1217;0.1333;0.1449;0.1565;0.1681;0.1797;0.1913;0.2029;0.2145;0.2261;0.2377;0.2493;0.2609;0.2725;0.2841;0.2957;0.3072;0.3188;0.3304;0.3420;0.3536;0.3652;0.3768;0.3884;0.4000;0.4116;0.4232;0.4348;0.4464;0.4580;0.4696;0.4812;0.4928;0.5043;0.5159;0.5275;0.5391;0.5507;0.5623;0.5739;0.5855;0.5971;0.6087;0.6203;0.6319;0.6435;0.6551;0.6667;0.6783;0.6899;0.7014;0.7130;0.7246;0.7362;0.7478;0.7594;0.7710;0.7826;1.0000" values="310;310;306.15;302.29;298.44;294.58;290.72;286.86;282.99;279.12;275.24;271.35;267.46;263.56;259.66;255.74;251.82;247.89;243.96;240.01;236.06;232.1;228.14;224.17;220.2;216.23;212.26;208.28;204.32;200.35;196.4;192.46;188.54;184.63;180.75;176.9;173.09;169.31;165.59;161.91;158.3;154.76;151.29;147.91;144.62;141.44;138.37;135.43;132.62;129.95;127.44;125.09;122.91;120.91;119.11;117.51;116.12;114.93;113.97;113.24;112.73;112.46;112.46"/></circle>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">0 度（真正面）: 差はゼロ。色は分かれない<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0866;0.0870;0.2605;0.2609;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">30 度: 差はわずか<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2605;0.2609;0.4344;0.4348;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">60 度: 差が目に見えてくる<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4344;0.4348;0.6083;0.6087;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">ふちに近い角度: 差が最大 → 縁に虹色が出る<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6083;0.6087;0.7823;0.7826;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:dispersion-delta:end -->

## 分散とは

ガラスの屈折率は <strong>光の波長によって、少し違います</strong>。青い光は赤い光より少し大きく曲がります。結果、白い光がプリズムを通ると虹色に分かれます。これが分散です。

| 色 | 波長 | 屈折率（クラウン ガラス） |
| --- | --- | --- |
| 赤 | 約 650 nm | 約 1.514 |
| 緑 | 約 550 nm | 約 1.519 |
| 青 | 約 450 nm | 約 1.527 |

差は わずか（1% 以下）ですが、曲がる角度のわずかな違いが距離を進むと、はっきりした色のずれになります。ダイヤモンドのきらめき（ファイア）、プリズム、縁の虹色はすべて分散による現象です。

## 屈折率の波長依存

屈折率は波長に対して <strong>単調に減る</strong>（長い波長ほど小さい）。経験式（Cauchy の式、Sellmeier の式）があります。

```text
Cauchy の式:  n(λ) = A + B / λ²                  λ は、マイクロメートル。A、B は、材料ごとの定数
```

| 材料 | A | B（μm²） |
| --- | --- | --- |
| 水 | 1.3199 | 0.00306 |
| クラウン ガラス | 1.5046 | 0.00420 |
| フリント ガラス | 1.7280 | 0.01342 |
| ダイヤモンド | 2.3780 | 0.01158 |

フリント ガラス（鉛を含み分散が大きい）や、ダイヤモンドは `B` が大きく 分散が強い。

```hlsl
// Cauchy の式で、波長（マイクロメートル）から屈折率を求める。
float CauchyIOR(float lambda_um, float A, float B) {
  return A + B / (lambda_um * lambda_um);
}
float ior_r = CauchyIOR(0.65, 1.5046, 0.00420);     // 赤
float ior_g = CauchyIOR(0.55, 1.5046, 0.00420);     // 緑
float ior_b = CauchyIOR(0.45, 1.5046, 0.00420);     // 青
```

## 実装：RGB を別々に、屈折させる

最も簡単な方法は <strong>赤・緑・青の、3 つの屈折率</strong>で 屈折ベクトルを 3 回求めそれぞれ違う位置を読むことです。

```hlsl
float3 view = normalize(input.world_position - g_camera_position);
float3 N = normalize(input.world_normal);

// RGB で、別の屈折率（空気 → ガラス: eta = 1 / n）。
float3 refr_r = refract(view, N, 1.0 / ior_r);
float3 refr_g = refract(view, N, 1.0 / ior_g);
float3 refr_b = refract(view, N, 1.0 / ior_b);

// 画面空間の屈折: それぞれの屈折ベクトルから、ずらし量を求め、別々に、読む。
float2 uv_r = screen_uv + ViewOffset(refr_r) * g_refraction_strength;
float2 uv_g = screen_uv + ViewOffset(refr_g) * g_refraction_strength;
float2 uv_b = screen_uv + ViewOffset(refr_b) * g_refraction_strength;

float3 refracted;
refracted.r = g_scene_copy.Sample(g_linear_clamp, uv_r).r;
refracted.g = g_scene_copy.Sample(g_linear_clamp, uv_g).g;
refracted.b = g_scene_copy.Sample(g_linear_clamp, uv_b).b;
```

簡易版は 法線からずらし量を求め、RGB に少しだけ違う係数を掛けます。

```hlsl
float2 offset = view_normal.xy * g_refraction_strength;
refracted.r = g_scene_copy.Sample(g_linear_clamp, screen_uv + offset * 0.95).r;     // 赤: 小さく曲がる
refracted.g = g_scene_copy.Sample(g_linear_clamp, screen_uv + offset * 1.00).g;
refracted.b = g_scene_copy.Sample(g_linear_clamp, screen_uv + offset * 1.05).b;     // 青: 大きく曲がる
```

0.95、1.00、1.05 の 差を広げるほど、虹色の縁取りが強くなります。水のように分散が小さい物では差をごく小さくします。

## 3 色では足りない

RGB の <strong>3 色だけ</strong>だと 色の分離が 3 つのずれた像に見えます（赤の像、緑の像、青の像）。なめらかな虹にするにはもっと多くの波長で、サンプルします。

```hlsl
// 波長を 8 つに分けて、それぞれ屈折させ、RGB に、変換して足す（スペクトルの、近似）。
float3 acc = 0;
float3 weight_sum = 0;
for (int i = 0; i < 8; ++i) {
  float t = (i + 0.5) / 8.0;                           // 0（赤）〜 1（青）
  float lambda = lerp(0.70, 0.40, t);                   // 波長（μm）
  float ior = CauchyIOR(lambda, A, B);
  float3 refr = refract(view, N, 1.0 / ior);
  float3 sample_color = g_scene_copy.Sample(g_linear_clamp, screen_uv + ViewOffset(refr) * g_refraction_strength).rgb;
  float3 w = WavelengthToRGB(lambda);                   // 波長に対応する、RGB の重み（虹の色）
  acc += sample_color * w;
  weight_sum += w;
}
float3 refracted = acc / weight_sum;
```

`WavelengthToRGB` は 波長（380〜700 nm）から、RGB の重みを返す関数です（虹色の、グラデーションの近似）。8〜16 サンプルで なめらかな虹になります。コストはサンプル数に比例して、増えます。

## どこに現れるか

| 対象 | 分散の見え方 |
| --- | --- |
| 窓ガラス | ほとんど見えない（薄く、分散も小さい） |
| 水 | ほとんど見えない（分散が小さい） |
| ガラスの縁、切り子 | 縁の細い虹色。曲面で強い |
| プリズム | 白い光が虹色に分かれる |
| ダイヤモンド、宝石 | 内部の反射・屈折で、カラフルなきらめき（ファイア） |

<strong>平らな薄いガラス</strong>では 分散はほぼ、見えません。縁や曲がった厚い部分で効果が現れるのでそこに使うとコストの割に見栄えがよくなります。

## 色収差（レンズ）との違い

[Chromatic Aberration](../../postprocess/lens-effects/chromatic-aberration.md) は、<strong>カメラのレンズ</strong>が起こす 色の、ずれで画面の周辺に現れます。物体（ガラス）の分散はガラスの物体の、部分だけに現れます。原因も場所も別です。

## よくあるミス

??? failure "すべてのガラスに強い色収差を付けて、安っぽくなる"
    <strong>宝石など分散が目立つ物だけに使う</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] R・G・B で、ずらす量を変える
    - [x] 控えめに使う

## 参考

- Hecht, "Optics", 5th Edition, Pearson, 2016（スネルの法則、フレネルの式、分散）
- Sellmeier, "Zur Erklärung der abnormen Farbenfolge im Spectrum einiger Substanzen", Annalen der Physik und Chemie, Vol. 219, 1871（屈折率の波長依存の式）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（屈折、フレネル、透過の章）
- Cauchy, "Mémoire sur la dispersion de la lumière", Prague, 1836（Cauchy の式）

## 関連ページ

- [Refraction](index.md)
- [Lens Effects](../../postprocess/lens-effects/index.md)
