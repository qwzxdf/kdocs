---
title: ACES
tags:
  - 描画
---

# ACES

**ACES**（Academy Color Encoding System）は、**映画業界が色管理のために作った標準**です。<strong>その中のトーンマップ（RRT と ODT）</strong>を**ゲームが借りて**、**締まった黒・鮮やかな色・滑らかなハイライト**という<strong>「映画らしい」絵</strong>を作ります。**本物の ACES は複雑**なので、**ゲームでは近似式**を使うのが一般的です。このページでは、**ACES とは何か・近似式（Narkowicz）・Stephen Hill のフィット・色が偏る理由・使うときの注意**を説明します。

!!! tip "ポイント"
    - ACES ＝ <strong>映画の色管理の標準</strong>。<strong>ゲームではそのトーンマップの形を借りる</strong>。
    - 本物は<strong>色空間の変換を伴う多段処理</strong>。<strong>ゲームは近似式（1 行）で代用</strong>する。
    - 特徴は<strong>強いコントラスト・沈んだ黒・鮮やかな色</strong>。
    - <strong>欠点</strong>：<strong>明るく彩度の高い色が白や黄へ偏る</strong>（<strong>青い光が紫に赤が橙に</strong>）。
    - <strong>近似式は本物と同じではない</strong>。<strong>「ACES っぽい」曲線</strong>だと理解して使う。
    - <strong>より良いやり方</strong>：<strong>Hill のフィット（色空間変換つき）</strong>、または<strong>[AgX](agx.md)</strong>。

## ACES とは

**ACES** は**撮影機材やデジタル素材の色を、共通の広い色空間（AP0・AP1）にそろえ**、**最後に出力デバイスに合わせて変換**する**仕組み全体**の名前です。

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

**ゲームがほしいのは、この中の「RRT + ODT」が作る曲線の形**です。**入力の色空間変換（IDT）は、リニアな sRGB のレンダリング結果をそのまま使う**ので、**省略**します。

## 近似式：Narkowicz

**Krzysztof Narkowicz** が提案した、**有理関数 1 つ**の**近似**です。**軽くて、ゲームの定番**です。

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

| 点 | 説明 |
| --- | --- |
| **入力に露出を掛けておく** | **この式は、ACES の曲線を露出済みの値に合わせてフィットしたもの**。**中間灰 0.18 付近が、おおよそ 0.27 に** |
| **`saturate`** | **1 を超えた分は切る**（**式はほぼ 1 に漸近するが、超えることがある**） |
| **チャンネルごとに適用** | **R・G・B に別々に**掛ける（**それが色の偏りの原因にもなる**） |

## 色空間つきのフィット：Stephen Hill

**もっと本物に近い**のが、**Stephen Hill のフィット**です。**ACES の「色空間の行列変換」も含みます**。

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
| **入力・出力の行列** | **sRGB ↔ ACES の色空間**を、**3×3 行列で変換** |
| **`RRTAndODTFit`** | **曲線の部分**（有理関数） |
| **行列を掛ける向き** | **列ベクトル規約**で書かれている（`mul(行列, ベクトル)`）。**行ベクトル規約の C++・HLSL では、転置**に注意 |
| **Narkowicz との違い** | **色空間の変換が入るので、彩度や色相の変化が本物に近い** |

## 色が偏る理由

<strong>ACES は、「ハイライトの色が白へ向かう」</strong>ように作られた**フィルム的な曲線**です。**そのため**、次の現象が起きます。

| 現象 | 内容 |
| --- | --- |
| **青い強い光が紫がかる** | **青の成分だけ先に飽和し、赤が残る** |
| **赤・オレンジの強い光が黄色へ** | **赤が先に飽和し、緑が目立つ** |
| **彩度の高い明部が白に近づく** | **フィルムのハイライトの特徴**（**意図した表現**にもなる） |

**ゲームではネオンやエフェクトの鮮やかな色が、意図とずれる**ことがあります。**その場合は、AgX や色補正で対処**します。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **Hill のフィットを使う** | **色空間変換つきで色の偏りが本物に近く、制御しやすい** |
| **エフェクトの色を事前に調整** | **ACES を通った後の見た目で、エフェクトの色を決める** |
| **ハイライトの色を保つ補正** | **彩度の高い明部で輝度ベースの補正をブレンド**（[Preserving Hue](hue-preservation.md)） |
| **AgX に替える** | <strong>色相の安定を重視するなら、[AgX](agx.md)</strong> |
| **LUT に焼く** | **ACES を 3D LUT にして、グレーディングと統合**（[3D LUT](../color-grading/lut-3d.md)） |

## よくあるミス

??? failure "「ACES を使っている」と言いつつ、近似式だけで色空間変換がない"
    <strong>近似式は「ACES っぽい曲線」</strong>。**本物の色再現が必要なら、Hill のフィットや OpenColorIO**。

??? failure "行列の掛ける順（転置）を間違えて、色が変になる"
    **Hill のコードは列ベクトル規約**。**行ベクトル規約の環境では、行列を転置**して掛ける。

??? failure "ACES の後に、さらに露出やコントラストを足して、二重になる"
    **ACES はすでにコントラストが強い**。**グレーディングは、控えめに**。

??? failure "ブルームやエフェクトが、紫・黄に偏って見える"
    **ACES の色の偏り**。**エフェクトの色を調整する**、または**AgX を検討**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ACES ＝ <strong>映画の色管理の標準</strong>。<strong>ゲームはトーンマップの形を借りる</strong>
    - [x] <strong>近似式（Narkowicz）は 1 行</strong>で<strong>軽い</strong>。<strong>Hill のフィットは色空間つき</strong>
    - [x] 特徴は<strong>強いコントラストと鮮やかな色</strong>。<strong>欠点は明部の色の偏り</strong>
    - [x] <strong>行列の向き（転置）</strong>に注意
    - [x] <strong>色の安定を重視</strong>するなら <strong>AgX</strong>

## 参考

- Narkowicz, "ACES Filmic Tone Mapping Curve"（2016）
- Hill, "ACES Fitted"（BakingLab, GitHub）
- Academy of Motion Picture Arts and Sciences, "Academy Color Encoding System"

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [Filmic (Hable)](filmic-hable.md)
- [AgX and Others](agx.md)
- [Preserving Hue](hue-preservation.md)
