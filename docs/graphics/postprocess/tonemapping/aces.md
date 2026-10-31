---
title: ACES
tags:
  - 描画
---

# ACES

<strong>ACES</strong>（Academy Color Encoding System）は、映画業界が色管理のために作った標準です。その中のトーンマップ（RRT と ODT）をゲームが借りて、締まった黒・鮮やかな色・滑らかなハイライトという「映画らしい」絵を作ります。本物の ACES は複雑なので、ゲームでは近似式を使うのが一般的です。このページでは、ACES とは何か・近似式（Narkowicz）・Stephen Hill のフィット・色が偏る理由・使うときの注意を説明します。

!!! tip "ポイント"
    - ACES ＝ <strong>映画の色管理の標準</strong>。<strong>ゲームではそのトーンマップの形を借りる</strong>。
    - 本物は色空間の変換を伴う多段処理。ゲームは近似式（1 行）で代用する。
    - 特徴は強いコントラスト・沈んだ黒・鮮やかな色。
    - 欠点：明るく彩度の高い色が白や黄へ偏る（青い光が紫に赤が橙に）。
    - 近似式は本物と同じではない。「ACES っぽい」曲線だと理解して使う。
    - より良いやり方：Hill のフィット（色空間変換つき）、または[AgX](agx.md)。

!!! info "このページを読む前に"
    - [Tone Mapping and Exposure](index.md)（このセクション全体の地図と、読む順番）

## ACES とは

<strong>ACES</strong> は撮影機材やデジタル素材の色を共通の広い色空間（AP0・AP1）にそろえ、最後に出力デバイスに合わせて変換する仕組み全体の名前です。

<svg class="fig illust" viewBox="0 0 780 150" role="img" aria-label="ACES の流れ">
<text x="20" y="26" class="fig-title">ACES の流れ（本物）：広い色空間で扱い、最後に出力へ</text>
<defs><marker id="ac-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<g font-size="12">
<rect x="20" y="56" width="130" height="60" rx="8" fill="#4c8bf5" fill-opacity="0.18" stroke="#4c8bf5" stroke-width="2"/><text x="85" y="82" text-anchor="middle" style="font-weight:700">入力（IDT）</text><text x="85" y="100" text-anchor="middle" style="font-size:11px">素材の色を ACES へ</text>
<rect x="200" y="56" width="130" height="60" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/><text x="265" y="82" text-anchor="middle" style="font-weight:700">ACES 空間</text><text x="265" y="100" text-anchor="middle" style="font-size:11px">広い色域・リニア</text>
<rect x="380" y="56" width="150" height="60" rx="8" fill="#e5484d" fill-opacity="0.18" stroke="#e5484d" stroke-width="2"/><text x="455" y="82" text-anchor="middle" style="font-weight:700">RRT</text><text x="455" y="100" text-anchor="middle" style="font-size:11px">映画らしい見た目の曲線</text>
<rect x="580" y="56" width="180" height="60" rx="8" fill="#2ea043" fill-opacity="0.18" stroke="#2ea043" stroke-width="2"/><text x="670" y="82" text-anchor="middle" style="font-weight:700">ODT</text><text x="670" y="100" text-anchor="middle" style="font-size:11px">ディスプレイに合わせる</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="152" y1="86" x2="198" y2="86" marker-end="url(#ac-arrow)"/><line x1="332" y1="86" x2="378" y2="86" marker-end="url(#ac-arrow)"/><line x1="532" y1="86" x2="578" y2="86" marker-end="url(#ac-arrow)"/></g>
</svg>

ゲームがほしいのは、この中の「RRT + ODT」が作る曲線の形です。入力の色空間変換（IDT）は、リニアな sRGB のレンダリング結果をそのまま使うので、省略します。

## 近似式：Narkowicz

<strong>Krzysztof Narkowicz</strong> が提案した、有理関数 1 つの近似です。軽くて、ゲームの定番です。

<div class="formula">c = (x · (2.51·x + 0.03)) / (x · (2.43·x + 0.59) + 0.14)</div>

```hlsl
float3 ACESNarkowicz(float3 x) {
  const float a = 2.51;
  const float b = 0.03;
  const float c = 2.43;
  const float d = 0.59;
  const float e = 0.14;
  return saturate((x * (a * x + b)) / (x * (c * x + d) + e));
}
```

Narkowicz 版のコードの要点です。入力に露出を掛けておく必要があります。この式は、ACES の曲線を露出済みの値に合わせてフィットしたもので、中間灰 0.18 付近がおおよそ 0.27 になります。`saturate` で、1 を超えた分を切ります（式はほぼ 1 に漸近しますが、超えることがあります）。R・G・B にチャンネルごとに適用するので、これが色の偏りの原因にもなります。

## 色空間つきのフィット：Stephen Hill

<strong>もっと本物に近い</strong>のが、Stephen Hill のフィットです。ACES の「色空間の行列変換」も含みます。

```hlsl
static const float3x3 kACESInputMat = {
  { 0.59719, 0.35458, 0.04823 },
  { 0.07600, 0.90834, 0.01566 },
  { 0.02840, 0.13383, 0.83777 }
};

static const float3x3 kACESOutputMat = {
  { 1.60475, -0.53108, -0.07367 },
  { -0.10208, 1.10813, -0.00605 },
  { -0.00327, -0.07276, 1.07602 }
};

float3 RRTAndODTFit(float3 v) {
  float3 a = v * (v + 0.0245786) - 0.000090537;
  float3 b = v * (0.983729 * v + 0.4329510) + 0.238081;
  return a / b;
}

float3 ACESFitted(float3 color) {
  color = mul(kACESInputMat, color);
  color = RRTAndODTFit(color);
  color = mul(kACESOutputMat, color);
  return saturate(color);
}
```

| 点 | 説明 |
| --- | --- |
| 入力・出力の行列 | sRGB ↔ ACES の色空間を 3×3 行列で変換 |
| `RRTAndODTFit` | 曲線の部分（有理関数） |
| 行列を掛ける向き | 列ベクトル規約で書かれている（`mul(行列, ベクトル)`）。行ベクトル規約の C++・HLSL では、転置に注意 |
| Narkowicz との違い | 色空間の変換が入るので、彩度や色相の変化が本物に近い |


原典は、映画業界の標準である Academy Color Encoding System (ACES) で、Narkowicz（2016）と Hill（2017）がこの変換をゲーム向けの軽い式にフィットしました。

原典は、映画業界の標準である Academy Color Encoding System (ACES) で、Narkowicz（2016）と Hill（2017）がこの変換をゲーム向けの軽い式にフィットしました。

## 色が偏る理由

<strong>ACES は、「ハイライトの色が白へ向かう」</strong>ように作られたフィルム的な曲線です。そのため、次の現象が起きます。

ACES は、ハイライトの色が白へ向かうように作られた、フィルム的な曲線です。そのため、いくつかの現象が起きます。青い強い光が紫がかるのは、青の成分だけ先に飽和し、赤が残るためです。赤やオレンジの強い光が黄色へ変わるのは、赤が先に飽和し、緑が目立つためです。彩度の高い明部が白に近づくのは、フィルムのハイライトの特徴で、意図した表現にもなります。

ゲームではネオンやエフェクトの鮮やかな色が意図とずれることがあります。その場合は、AgX や色補正で対処します。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| Hill のフィットを使う | 色空間変換つきで色の偏りが本物に近く、制御しやすい |
| エフェクトの色を事前に調整 | ACES を通った後の見た目で、エフェクトの色を決める |
| ハイライトの色を保つ補正 | 彩度の高い明部で輝度ベースの補正をブレンド（[Preserving Hue](hue-preservation.md)） |
| AgX に替える | <strong>色相の安定を重視するなら、[AgX](agx.md)</strong> |
| LUT に焼く | ACES を 3D LUT にして、グレーディングと統合（[3D LUT](../color-grading/lut-3d.md)） |

<!-- fig:tonemap-aces-curves:begin -->

<svg class="fig illust motion" data-fig="tonemap-aces-curves" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-tonemap-aces-curves" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">トーンマップ: 明るさ 0〜8 を画面に出せる 0〜1 に押し込む</text>
<rect x="70" y="70" width="640" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="230.0" y1="70" x2="230.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="130.0" x2="710" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="70" x2="390.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="190.0" x2="710" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="550.0" y1="70" x2="550.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="250.0" x2="710" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="70" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">出力（表示できる明るさ）</text>
<text x="710" y="346" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">入力の明るさ（HDR）</text>
<text x="70.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0</text>
<text x="230.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">2</text>
<text x="390.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">4</text>
<text x="550.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">6</text>
<text x="710.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">8</text>
<path d="M70.0,310.0 L76.4,291.71 L82.8,273.43 L89.2,255.14 L95.6,236.86 L102.0,218.57 L108.4,200.29 L114.8,182.0 L121.2,163.71 L127.6,145.43 L134.0,127.14 L140.4,108.86 L146.8,90.57 L153.2,81.43 L159.6,81.43 L166.0,81.43 L172.4,81.43 L178.8,81.43 L185.2,81.43 L191.6,81.43 L198.0,81.43 L204.4,81.43 L210.8,81.43 L217.2,81.43 L223.6,81.43 L230.0,81.43 L236.4,81.43 L242.8,81.43 L249.2,81.43 L255.6,81.43 L262.0,81.43 L268.4,81.43 L274.8,81.43 L281.2,81.43 L287.6,81.43 L294.0,81.43 L300.4,81.43 L306.8,81.43 L313.2,81.43 L319.6,81.43 L326.0,81.43 L332.4,81.43 L338.8,81.43 L345.2,81.43 L351.6,81.43 L358.0,81.43 L364.4,81.43 L370.8,81.43 L377.2,81.43 L383.6,81.43 L390.0,81.43 L396.4,81.43 L402.8,81.43 L409.2,81.43 L415.6,81.43 L422.0,81.43 L428.4,81.43 L434.8,81.43 L441.2,81.43 L447.6,81.43 L454.0,81.43 L460.4,81.43 L466.8,81.43 L473.2,81.43 L479.6,81.43 L486.0,81.43 L492.4,81.43 L498.8,81.43 L505.2,81.43 L511.6,81.43 L518.0,81.43 L524.4,81.43 L530.8,81.43 L537.2,81.43 L543.6,81.43 L550.0,81.43 L556.4,81.43 L562.8,81.43 L569.2,81.43 L575.6,81.43 L582.0,81.43 L588.4,81.43 L594.8,81.43 L601.2,81.43 L607.6,81.43 L614.0,81.43 L620.4,81.43 L626.8,81.43 L633.2,81.43 L639.6,81.43 L646.0,81.43 L652.4,81.43 L658.8,81.43 L665.2,81.43 L671.6,81.43 L678.0,81.43 L684.4,81.43 L690.8,81.43 L697.2,81.43 L703.6,81.43 L710.0,81.43" fill="none" stroke="#64748b" stroke-width="3" opacity="1" stroke-dasharray="6 5"/>
<path d="M70.0,310.0 L76.4,293.07 L82.8,278.47 L89.2,265.76 L95.6,254.59 L102.0,244.69 L108.4,235.87 L114.8,227.95 L121.2,220.8 L127.6,214.32 L134.0,208.41 L140.4,203.01 L146.8,198.05 L153.2,193.47 L159.6,189.25 L166.0,185.32 L172.4,181.68 L178.8,178.28 L185.2,175.11 L191.6,172.13 L198.0,169.34 L204.4,166.72 L210.8,164.24 L217.2,161.91 L223.6,159.71 L230.0,157.62 L236.4,155.64 L242.8,153.76 L249.2,151.98 L255.6,150.28 L262.0,148.66 L268.4,147.11 L274.8,145.63 L281.2,144.22 L287.6,142.87 L294.0,141.58 L300.4,140.34 L306.8,139.15 L313.2,138.01 L319.6,136.91 L326.0,135.85 L332.4,134.83 L338.8,133.85 L345.2,132.91 L351.6,132.0 L358.0,131.12 L364.4,130.27 L370.8,129.45 L377.2,128.65 L383.6,127.89 L390.0,127.14 L396.4,126.42 L402.8,125.73 L409.2,125.05 L415.6,124.39 L422.0,123.76 L428.4,123.14 L434.8,122.54 L441.2,121.96 L447.6,121.39 L454.0,120.84 L460.4,120.3 L466.8,119.78 L473.2,119.27 L479.6,118.78 L486.0,118.29 L492.4,117.83 L498.8,117.37 L505.2,116.92 L511.6,116.49 L518.0,116.06 L524.4,115.65 L530.8,115.24 L537.2,114.85 L543.6,114.46 L550.0,114.08 L556.4,113.71 L562.8,113.35 L569.2,113.0 L575.6,112.65 L582.0,112.32 L588.4,111.99 L594.8,111.66 L601.2,111.35 L607.6,111.04 L614.0,110.73 L620.4,110.44 L626.8,110.14 L633.2,109.86 L639.6,109.58 L646.0,109.3 L652.4,109.03 L658.8,108.77 L665.2,108.51 L671.6,108.26 L678.0,108.01 L684.4,107.76 L690.8,107.52 L697.2,107.29 L703.6,107.05 L710.0,106.83" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<path d="M70.0,310.0 L76.4,289.18 L82.8,256.78 L89.2,227.71 L95.6,204.5 L102.0,186.39 L108.4,172.19 L114.8,160.9 L121.2,151.78 L127.6,144.28 L134.0,138.04 L140.4,132.78 L146.8,128.28 L153.2,124.41 L159.6,121.03 L166.0,118.07 L172.4,115.44 L178.8,113.11 L185.2,111.02 L191.6,109.14 L198.0,107.44 L204.4,105.89 L210.8,104.48 L217.2,103.18 L223.6,101.99 L230.0,100.89 L236.4,99.87 L242.8,98.93 L249.2,98.05 L255.6,97.23 L262.0,96.47 L268.4,95.75 L274.8,95.07 L281.2,94.44 L287.6,93.84 L294.0,93.28 L300.4,92.75 L306.8,92.24 L313.2,91.77 L319.6,91.31 L326.0,90.88 L332.4,90.47 L338.8,90.08 L345.2,89.7 L351.6,89.35 L358.0,89.01 L364.4,88.68 L370.8,88.37 L377.2,88.07 L383.6,87.78 L390.0,87.5 L396.4,87.24 L402.8,86.98 L409.2,86.74 L415.6,86.5 L422.0,86.27 L428.4,86.05 L434.8,85.84 L441.2,85.64 L447.6,85.44 L454.0,85.25 L460.4,85.06 L466.8,84.88 L473.2,84.71 L479.6,84.54 L486.0,84.38 L492.4,84.22 L498.8,84.06 L505.2,83.92 L511.6,83.77 L518.0,83.63 L524.4,83.49 L530.8,83.36 L537.2,83.23 L543.6,83.11 L550.0,82.98 L556.4,82.86 L562.8,82.75 L569.2,82.63 L575.6,82.52 L582.0,82.42 L588.4,82.31 L594.8,82.21 L601.2,82.11 L607.6,82.01 L614.0,81.92 L620.4,81.82 L626.8,81.73 L633.2,81.64 L639.6,81.56 L646.0,81.47 L652.4,81.39 L658.8,81.31 L665.2,81.23 L671.6,81.15 L678.0,81.07 L684.4,81.0 L690.8,80.93 L697.2,80.85 L703.6,80.78 L710.0,80.72" fill="none" stroke="#e5484d" stroke-width="4" opacity="1"/>
<text x="454.0" y="103.43" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">ACES（近似）</text>
<text x="454.0" y="144.84" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">Reinhard</text>
<text x="198.0" y="73.43" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">そのまま（1 で頭打ち）</text>
<circle cx="70.0" cy="310.0" r="7" fill="#1f2937"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0920;0.1040;0.1160;0.1280;0.1400;0.1520;0.1640;0.1760;0.1880;0.2000;0.2120;0.2240;0.2360;0.2480;0.2600;0.2720;0.2840;0.2960;0.3080;0.3200;0.3320;0.3440;0.3560;0.3680;0.3800;0.3920;0.4040;0.4160;0.4280;0.4400;0.4520;0.4640;0.4760;0.4880;0.5000;0.5120;0.5240;0.5360;0.5480;0.5600;0.5720;0.5840;0.5960;0.6080;0.6200;0.6320;0.6440;0.6560;0.6680;0.6800;0.6920;0.7040;0.7160;0.7280;0.7400;0.7520;0.7640;0.7760;0.7880;0.8000;1.0000" values="70;70;80.67;91.33;102;112.67;123.33;134;144.67;155.33;166;176.67;187.33;198;208.67;219.33;230;240.67;251.33;262;272.67;283.33;294;304.67;315.33;326;336.67;347.33;358;368.67;379.33;390;400.67;411.33;422;432.67;443.33;454;464.67;475.33;486;496.67;507.33;518;528.67;539.33;550;560.67;571.33;582;592.67;603.33;614;624.67;635.33;646;656.67;667.33;678;688.67;699.33;710;710"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0920;0.1040;0.1160;0.1280;0.1400;0.1520;0.1640;0.1760;0.1880;0.2000;0.2120;0.2240;0.2360;0.2480;0.2600;0.2720;0.2840;0.2960;0.3080;0.3200;0.3320;0.3440;0.3560;0.3680;0.3800;0.3920;0.4040;0.4160;0.4280;0.4400;0.4520;0.4640;0.4760;0.4880;0.5000;0.5120;0.5240;0.5360;0.5480;0.5600;0.5720;0.5840;0.5960;0.6080;0.6200;0.6320;0.6440;0.6560;0.6680;0.6800;0.6920;0.7040;0.7160;0.7280;0.7400;0.7520;0.7640;0.7760;0.7880;0.8000;1.0000" values="310;310;267.56;219.33;186.39;164.39;149.12;138.04;129.71;123.23;118.07;113.86;110.37;107.44;104.93;102.77;100.89;99.24;97.77;96.47;95.29;94.24;93.28;92.41;91.61;90.88;90.21;89.58;89.01;88.47;87.97;87.5;87.07;86.66;86.27;85.91;85.57;85.25;84.94;84.65;84.38;84.12;83.87;83.63;83.4;83.19;82.98;82.79;82.6;82.42;82.24;82.08;81.92;81.76;81.61;81.47;81.33;81.2;81.07;80.95;80.83;80.72;80.72"/></circle>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">暗い所: ACES は、暗部を少し沈めてコントラストを付ける<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.2597;0.2600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">中間: 急に立ち上がる(S 字の中央)<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2597;0.2600;0.4397;0.4400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">明るい所: ゆるやかに 1 へ近づく(白飛びしにくい)<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4397;0.4400;0.6197;0.6200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">8 でも 1 を超えない。Reinhard は白に届きにくい<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6197;0.6200;0.7997;0.8000;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:tonemap-aces-curves:end -->

## よくあるミス

??? failure "「ACES を使っている」と言いつつ、近似式だけで色空間変換がない"
    <strong>近似式は「ACES っぽい曲線」</strong>。本物の色再現が必要なら、Hill のフィットや OpenColorIO。

??? failure "行列の掛ける順（転置）を間違えて、色が変になる"
    Hill のコードは列ベクトル規約。行ベクトル規約の環境では、行列を転置して掛ける。

??? failure "ACES の後にさらに露出やコントラストを足して、二重になる"
    ACES はすでにコントラストが強い。グレーディングは、控えめに。

??? failure "ブルームやエフェクトが紫・黄に偏って見える"
    ACES の色の偏り。エフェクトの色を調整する、またはAgX を検討。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ACES ＝ <strong>映画の色管理の標準</strong>。ゲームはトーンマップの形を借りる
    - [x] 近似式（Narkowicz）は 1 行で軽い。Hill のフィットは色空間つき
    - [x] 特徴は強いコントラストと鮮やかな色。欠点は明部の色の偏り
    - [x] 行列の向き（転置）に注意
    - [x] 色の安定を重視するなら AgX

## 参考

- Narkowicz, "ACES Filmic Tone Mapping Curve"（2016）
- Hill, "ACES Fitted"（BakingLab, GitHub）
- Academy of Motion Picture Arts and Sciences, "Academy Color Encoding System"

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [Filmic (Hable)](filmic-hable.md)
- [AgX and Others](agx.md)
- [Preserving Hue](hue-preservation.md)
