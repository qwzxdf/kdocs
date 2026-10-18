---
title: Dithered Transparency
tags:
  - 描画
---

# Dithered Transparency

**ディザ透明は、規則的な点の模様（ディザ パターン）で、画素を間引いて、半透明に見せる手法**です。**カメラに近づいた物体や、キャラクターを隠す壁を、なめらかに消す**のに使われます。このページでは、**ディザ透明の仕組みと使い所**を説明します。

!!! tip "ポイント"
    - **規則的なパターンで、アルファに応じて画素を捨てる**。
    - **ソート不要・深度も書ける**。
    - **カメラ近くの物の、フェード アウトに便利**。
    - **ハッシュド アルファより、パターンが見える**。

## Dithered Transparency {#ディザ透明}
**カメラに近づいた物を、半透明にして向こうを見えるようにする**（例：**キャラの前の壁・木**）ときに、**ブレンドではなく、ディザ パターンで捨てる**方法があります。

```hlsl
static const float kBayer4x4[16] = {
    0.0 / 16, 8.0 / 16, 2.0 / 16, 10.0 / 16,
    12.0 / 16, 4.0 / 16, 14.0 / 16, 6.0 / 16,
    3.0 / 16, 11.0 / 16, 1.0 / 16, 9.0 / 16,
    15.0 / 16, 7.0 / 16, 13.0 / 16, 5.0 / 16};

uint2 p = uint2(input.position.xy) % 4;
float threshold = kBayer4x4[p.y * 4 + p.x];
clip(fade_alpha - threshold);
```

**不透明のまま、深度も書き、ソートも不要**で、**半透明のような見た目**になります（**ゲームのカメラが、壁を透かす**用途で定番）。

### How Dithered Transparency Works {#ディザ透明の仕組み}

ディザ透明は、透明度を<strong>画素の点々の密度</strong>で表します。たとえば透明度 50 % なら、画素の半分を捨て、残り半分を不透明に描きます。捨てる画素は、画面上で規則的な模様（ベイヤー行列など）で決めます。ベイヤー行列は、4×4 の画素に 0〜1 のしきい値を割り当てた表で、アルファが各画素のしきい値より大きいときだけ残します。

```hlsl
static const float kBayer4x4[16] = {
   0.0 / 16,  8.0 / 16,  2.0 / 16, 10.0 / 16,
  12.0 / 16,  4.0 / 16, 14.0 / 16,  6.0 / 16,
   3.0 / 16, 11.0 / 16,  1.0 / 16,  9.0 / 16,
  15.0 / 16,  7.0 / 16, 13.0 / 16,  5.0 / 16 };

float threshold = kBayer4x4[(pixel.y % 4) * 4 + (pixel.x % 4)];
clip(alpha - threshold);
```

### Use: See Through Obstacles in Front of the Camera {#使いどころカメラ前の遮蔽物を透かす}

最もよく使われるのは、カメラとプレイヤーの間に入った壁や木を、近づくほど透かして消す表現です。距離に応じてアルファを下げ、ディザで抜けば、ソートも深度の問題もなく、不透明のまま（深度を書けるので、影やポストプロセスも正しく動きます）、自然にフェードアウトします。

### Combining with TAA {#taa-と組み合わせる}

規則的な模様は、そのままだと網目が見えます。TAA を使うなら、フレームごとにしきい値の表をずらし（ベイヤー行列の代わりにブルー ノイズや、フレーム番号で回転した行列を使い）、TAA に平均させると、網目が溶けて、滑らかな半透明に見えます（[Hashed Alpha](hashed-alpha.md) と同じ原理です）。

<!-- fig:dither-alpha:begin -->

<svg class="fig illust motion" data-fig="dither-alpha" viewBox="0 0 780 440" role="img"><rect x="0" y="0" width="780" height="440" rx="14" fill="#ffffff"/>
<defs><marker id="arr-dither-alpha" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ディザ透明: アルファを上げると、閾値の小さい画素から順に不透明になる</text>
<rect x="150" y="90" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="150" y="90" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0864;0.0867;1.0000" values="0;0;1;1"/></rect>
<text x="179.0" y="125.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.03</text>
<rect x="212" y="90" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="212" y="90" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4413;0.4415;1.0000" values="0;0;1;1"/></rect>
<text x="241.0" y="125.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.53</text>
<rect x="274" y="90" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="274" y="90" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1751;0.1754;1.0000" values="0;0;1;1"/></rect>
<text x="303.0" y="125.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.16</text>
<rect x="336" y="90" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="336" y="90" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5300;0.5302;1.0000" values="0;0;1;1"/></rect>
<text x="365.0" y="125.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.66</text>
<rect x="150" y="152" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="150" y="152" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.6187;0.6190;1.0000" values="0;0;1;1"/></rect>
<text x="179.0" y="187.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.78</text>
<rect x="212" y="152" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="212" y="152" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2639;0.2641;1.0000" values="0;0;1;1"/></rect>
<text x="241.0" y="187.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.28</text>
<rect x="274" y="152" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="274" y="152" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.7074;0.7077;1.0000" values="0;0;1;1"/></rect>
<text x="303.0" y="187.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.91</text>
<rect x="336" y="152" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="336" y="152" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3526;0.3528;1.0000" values="0;0;1;1"/></rect>
<text x="365.0" y="187.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.41</text>
<rect x="150" y="214" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="150" y="214" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.2195;0.2198;1.0000" values="0;0;1;1"/></rect>
<text x="179.0" y="249.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.22</text>
<rect x="212" y="214" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="212" y="214" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5743;0.5746;1.0000" values="0;0;1;1"/></rect>
<text x="241.0" y="249.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.72</text>
<rect x="274" y="214" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="274" y="214" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1308;0.1310;1.0000" values="0;0;1;1"/></rect>
<text x="303.0" y="249.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.09</text>
<rect x="336" y="214" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="336" y="214" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4856;0.4859;1.0000" values="0;0;1;1"/></rect>
<text x="365.0" y="249.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.59</text>
<rect x="150" y="276" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="150" y="276" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.7518;0.7520;1.0000" values="0;0;1;1"/></rect>
<text x="179.0" y="311.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.97</text>
<rect x="212" y="276" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="212" y="276" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3969;0.3972;1.0000" values="0;0;1;1"/></rect>
<text x="241.0" y="311.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.47</text>
<rect x="274" y="276" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="274" y="276" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.6630;0.6633;1.0000" values="0;0;1;1"/></rect>
<text x="303.0" y="311.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.84</text>
<rect x="336" y="276" width="58" height="58" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="336" y="276" width="58" height="58" fill="#1f2937" opacity="0"><animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3082;0.3085;1.0000" values="0;0;1;1"/></rect>
<text x="365.0" y="311.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">0.34</text>
<text x="150" y="78" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">各画素の数字 = 閾値。アルファ &gt; 閾値 なら描く(黒)</text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">アルファ = 0.08 → 1 / 16 画素が不透明<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.0643;0.0645;0.1825;0.1828;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">アルファ = 0.25 → 4 / 16 画素が不透明<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.1825;0.1828;0.3008;0.3011;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">アルファ = 0.42 → 7 / 16 画素が不透明<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.3008;0.3011;0.4191;0.4194;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">アルファ = 0.58 → 9 / 16 画素が不透明<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.4191;0.4194;0.5374;0.5376;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">アルファ = 0.75 → 12 / 16 画素が不透明<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.5374;0.5376;0.6557;0.6559;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="395" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">アルファ = 0.92 → 15 / 16 画素が不透明<animate attributeName="opacity" dur="15.5s" repeatCount="indefinite" keyTimes="0.0000;0.6557;0.6559;0.7739;0.7742;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:dither-alpha:end -->

## Common Mistakes {#よくあるミス}

??? failure "ディザの点々が目立つ"
    **TAA を併用**する・**ブルー ノイズ**を使う。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **パターンで間引いて、半透明に見せる**
    - [x] **カメラ近くのフェードに便利**

## References {#参考}

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## Related Pages {#関連ページ}

- [Alpha Testing](index.md)
- [Hashed Alpha](hashed-alpha.md)
