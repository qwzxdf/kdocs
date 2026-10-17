---
title: Radiance Cascades
tags:
  - 描画
---

# Radiance Cascades

**Radiance Cascades は、「近くの光は高解像度で、遠くの光は低解像度で」持つ、階層的な方式**です。**2D の GI で特に成功しており、3D にも展開されつつあります**。このページでは、**Radiance Cascades の発想と、利点**を説明します。

!!! tip "ポイント"
    - **近くの光は、細かい空間解像度・粗い方向解像度**。
    - **遠くの光は、粗い空間解像度・細かい方向解像度**。
    - **階層ごとに結果をマージ**して、全体の光を求める。
    - **ノイズが少なく、安定している**。

## Radiance Cascades
**Radiance Cascades**（Alexander Sannikov、2023〜）は、**ノイズのない、全画素の放射照度**を**階層的な構造**で**効率よく計算する**方式です。

<!-- fig:radiance-cascades:begin -->

<svg class="fig illust motion" data-fig="radiance-cascades" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-radiance-cascades" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<clipPath id="rc-clip"><rect x="40" y="80" width="700" height="250"/>
</clipPath>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">Radiance Cascades:近くは細かい位置、遠くは細かい方向</text>
<rect x="40" y="80" width="700" height="250" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="0;0;1;1"/><circle cx="90" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="90" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="90" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="90" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="90" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="140" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="140" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="140" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="140" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="140" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="240" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="240" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="240" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="240" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="240" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="340" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="340" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="340" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="340" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="340" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="440" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="440" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="440" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="440" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="440" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="540" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="540" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="540" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="540" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="540" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="640" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="640" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="640" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="640" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="640" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="105" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="155" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="205" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="255" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="305" r="6" fill="#bae6fd" stroke="#64748b" stroke-width="1"/>
<line x1="390.0" y1="205.0" x2="445.0" y2="205.0" stroke="#0284c7" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="390.0" y1="205.0" x2="390.0" y2="260.0" stroke="#0284c7" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="390.0" y1="205.0" x2="335.0" y2="205.0" stroke="#0284c7" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="390.0" y1="205.0" x2="390.0" y2="150.0" stroke="#0284c7" stroke-width="2.2" clip-path="url(#rc-clip)"/>
</g>
<text x="390" y="352" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">カスケード 0:プローブ間隔 狭い・方向 4 本・短い距離<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.3256;0.3259;1.0000" values="0;0;1;1;0;0"/></text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;1.0000" values="0;0;1;1"/><circle cx="90" cy="105" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="90" cy="205" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="90" cy="305" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="105" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="205" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="190" cy="305" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="105" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="205" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="290" cy="305" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="105" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="205" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="305" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="105" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="205" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="490" cy="305" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="105" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="205" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="305" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="105" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="205" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<circle cx="690" cy="305" r="5" fill="#fde68a" stroke="#64748b" stroke-width="1"/>
<line x1="445.0" y1="205.0" x2="515.0" y2="205.0" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="428.89" y1="243.89" x2="478.39" y2="293.39" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="390.0" y1="260.0" x2="390.0" y2="330.0" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="351.11" y1="243.89" x2="301.61" y2="293.39" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="335.0" y1="205.0" x2="265.0" y2="205.0" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="351.11" y1="166.11" x2="301.61" y2="116.61" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="390.0" y1="150.0" x2="390.0" y2="80.0" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="428.89" y1="166.11" x2="478.39" y2="116.61" stroke="#d97706" stroke-width="2.2" clip-path="url(#rc-clip)"/>
</g>
<text x="390" y="352" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">カスケード 1:間隔 2 倍・方向 8 本・中距離<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;0.5775;0.5778;1.0000" values="0;0;1;1;0;0"/></text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5775;0.5778;1.0000" values="0;0;1;1"/><circle cx="190" cy="205" r="4" fill="#fbcfe8" stroke="#64748b" stroke-width="1"/>
<circle cx="390" cy="205" r="4" fill="#fbcfe8" stroke="#64748b" stroke-width="1"/>
<circle cx="590" cy="205" r="4" fill="#fbcfe8" stroke="#64748b" stroke-width="1"/>
<line x1="515.0" y1="205.0" x2="660.0" y2="205.0" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="505.48" y1="252.84" x2="639.45" y2="308.32" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="478.39" y1="293.39" x2="580.92" y2="395.92" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="437.84" y1="320.48" x2="493.32" y2="454.45" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="390.0" y1="330.0" x2="390.0" y2="475.0" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="342.16" y1="320.48" x2="286.68" y2="454.45" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="301.61" y1="293.39" x2="199.08" y2="395.92" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="274.52" y1="252.84" x2="140.55" y2="308.32" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="265.0" y1="205.0" x2="120.0" y2="205.0" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="274.52" y1="157.16" x2="140.55" y2="101.68" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="301.61" y1="116.61" x2="199.08" y2="14.08" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="342.16" y1="89.52" x2="286.68" y2="-44.45" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="390.0" y1="80.0" x2="390.0" y2="-65.0" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="437.84" y1="89.52" x2="493.32" y2="-44.45" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="478.39" y1="116.61" x2="580.92" y2="14.08" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
<line x1="505.48" y1="157.16" x2="639.45" y2="101.68" stroke="#db2777" stroke-width="2.2" clip-path="url(#rc-clip)"/>
</g>
<text x="390" y="352" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">カスケード 2:間隔 4 倍・方向 16 本・遠距離<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5775;0.5778;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">近い光は多くのプローブで、遠い光は少ないプローブで<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000" values="1;1;0;0"/></text>
<text x="40" y="60" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">プローブの数は 1/4 ずつ、方向の数は 2〜4 倍ずつ。階層を重ねて、全体の光を作る<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="396" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">合計のレイ数がほぼ一定。ノイズが少なく、安定している（2D の GI で特に成功している）。</text>
</svg>

<!-- fig:radiance-cascades:end -->

### 発想：空間と方向のトレードオフ

ある点が受け取る光を正確に知りたいとします。素朴に考えれば、点（空間）を細かく取り、さらに方向も細かく取って、その積の数だけレイが要ります。画面全体に対して、画素ごとに数百本のレイは、とても払えません。

ここで、Sannikov は次の観察をしました。<strong>光の届く距離によって、必要な空間の細かさと方向の細かさが逆になる</strong>のです。

近くの光源（短いレイで届く光）を考えます。近い光源は、点の位置が少し動くと、見える方向が大きく変わります。だから、点は細かく取らなければなりません。一方、近い光源は大きく見えるので、方向は粗くても、見逃しません。逆に、遠くの光源（長いレイで届く光）では、点が少し動いても、見える方向はほとんど変わらないので、点は粗くてかまいません。ただし、遠い光源は小さく見えるので、見逃さないように、方向は細かく取らなければなりません。

つまり、「細かい点 × 粗い方向」で近距離を、「粗い点 × 細かい方向」で遠距離を担当させれば、どちらも少ないサンプルで済みます。

### カスケード

この観察を、複数の<strong>カスケード</strong>という階層で実現します。カスケード 0 は、最も細かい間隔で配置したプローブで、持つ方向の数は少なく、担当するのは近距離です。カスケード 1 は、プローブの間隔が倍（数は 1/4）、方向の数は 4 倍（2D の場合）で、やや遠い距離を担当します。カスケード 2 は、さらに間隔が倍、方向が 4 倍で、さらに遠くを担当し、以下同様に続きます。

各カスケードのレイは、全距離を追うのでなく、<strong>自分の担当する距離の区間だけ</strong>を追います。区間は、カスケード n の区間を [t_n, t_(n+1)] として、距離が 4 倍ずつ伸びるように決めます。近いカスケードは短い区間を、遠いカスケードは長い区間を担当するので、全体で原点から無限遠まで、隙間なく覆えます。

プローブの数が 1/4 になり、方向の数が 4 倍になるので、<strong>カスケードごとのレイの総数は一定</strong>になります。カスケードの数は距離の対数に比例して増えるだけなので、全体の計算量は「画素数 × カスケードの数」と、とても小さく済みます。

### マージ：遠い光を近い方に伝える

各カスケードは、自分の区間の光しか知りません。全体の光を得るには、<strong>遠いカスケードの結果を、近いカスケードに伝えます</strong>（マージ）。

具体的には、カスケード n のある方向のレイが、自分の区間を進んで何にも当たらなかったとします。そのレイが見ている、さらに遠くの光は、カスケード n+1 が担当しています。そこで、カスケード n+1 の近傍の 4 つのプローブから、同じ方向をカバーしているレイの値を、補間して持ってきます。当たった場合は、当たった点の光が、そのレイの値です。この処理を、最も遠いカスケードから、順にカスケード 0 まで繰り返すと、カスケード 0 に全距離の光が集まります。

```hlsl
float3 MergeCascade(int cascade, float2 probe_pos, int dir_index) {
  float4 near = TraceInterval(cascade, probe_pos, dir_index);
  float3 radiance = near.rgb;
  float transmittance = near.a;
  if (cascade + 1 < kCascadeCount && transmittance > 0.0) {
    float3 far = SampleUpperCascade(cascade + 1, probe_pos, dir_index);
    radiance += transmittance * far;
  }
  return radiance;
}
```

`near.a` は、区間の途中で何かに遮られなかった割合（透過率）で、遮られていれば遠くの光は見えないので、0 に近づきます。補間によって、段差が出ないように、カスケード間をなめらかにつなぎます。

### 画素の放射照度の求め方

カスケード 0 のプローブは、全方向（少数の方向）の光を持っています。各画素は、近傍のカスケード 0 のプローブから、法線に沿った余弦重みで方向を足し合わせることで、放射照度を得ます。

### 性質

Radiance Cascades は、ランダムを使わず、規則的なサンプルなので、<strong>ノイズがありません</strong>。計算量は、画素数に比例して、ほぼ一定です。2D ゲームの GI で特に成功しており、『Path of Exile 2』の GI の仕組みとして使われています。3D への拡張は、方向が球面（2 次元）に広がり、サンプル数が増えるため、研究と実装が進んでいる段階です。

原典は、Alexander Sannikov による公開資料と、Osborne らによる論文（2024 年）です。この手法は発展の途中なので、最新の情報は原典を確認してください。

## よくあるミス

??? failure "階層の境目に、段差が見える"
    **階層間を補間**して、なめらかにつなぐ。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **距離ごとに、解像度を変えて持つ**
    - [x] **ノイズが少なく、安定**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Ray-Traced GI](index.md)
- [Choosing a Method](choosing.md)
- [SSGI](../ssgi.md)
