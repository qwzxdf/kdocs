---
title: Water Shading
tags:
  - 描画
---

# Water Shading

<strong>水の見た目は、反射・屈折・吸収・散乱が混ざったものです</strong>。<strong>角度によって反射と屈折の割合が変わり（フレネル）、深いほど色が濃くなります（Beer の法則）</strong>。このセクションでは、水面で起きていること・フレネル・水深による色・屈折の歪み・スペキュラ・反射・散乱・パラメータを、1 つずつ別のページで説明します。

## 水面で何が起きているか
<strong>光が水面に当たると一部は反射し、残りは水の中へ屈折して入ります</strong>。<strong>水の中では吸収と散乱を受けながら進み</strong>、底や水中の物で跳ね返り、再び水面を通って目に入ります。

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="水面で起きること">
<text x="20" y="24" class="fig-title">水面で起きること：反射 ＋ 水中を通ってきた光</text>
<rect x="40" y="130" width="700" height="150" fill="#4c8bf5" fill-opacity="0.18"/>
<line x1="40" y1="130" x2="740" y2="130" stroke="#4c8bf5" stroke-width="3"/>
<line x1="150" y1="40" x2="330" y2="130" stroke="#e5aa28" stroke-width="3"/>
<polygon points="330,130 316,116 308,128" fill="#e5aa28" transform="translate(0,0)" opacity="0"/>
<line x1="330" y1="130" x2="500" y2="45" stroke="#e5484d" stroke-width="3"/>
<text x="505" y="52" style="font-size:13px">反射（F）</text>
<line x1="330" y1="130" x2="400" y2="250" stroke="#2ea043" stroke-width="3"/>
<text x="408" y="248" style="font-size:13px">屈折して水中へ（1 − F）</text>
<line x1="400" y1="250" x2="640" y2="250" stroke="currentColor" stroke-opacity="0.5" stroke-width="2"/>
<text x="470" y="270" style="font-size:12px">底で跳ね返る</text>
<line x1="640" y1="250" x2="560" y2="130" stroke="#2ea043" stroke-width="3" stroke-dasharray="6 4"/>
<line x1="560" y1="130" x2="640" y2="40" stroke="#2ea043" stroke-width="3" stroke-dasharray="6 4"/>
<text x="648" y="44" style="font-size:13px">目へ</text>
<text x="100" y="68" style="font-size:13px">太陽</text>
<line x1="330" y1="130" x2="330" y2="60" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="4 4"/>
<text x="338" y="76" style="font-size:12px">法線</text>
</svg>

| 成分 | 内容 |
| --- | --- |
| 反射 | 空・周囲の景色を映す（[Reflections](../../reflections/index.md)） |
| 屈折＋透過 | 水中の物・底が透けて見える（歪む） |
| 吸収 | 水を通る距離に応じて、色が変わり暗くなる |
| 散乱 | 水中の粒子で光が散らばり、水自体が青緑に光る |
| スペキュラ | 太陽・光源の鋭い反射 |

## 合成の全体像
```hlsl
float3 N = ComputeNormal(input);
float3 V = normalize(camera_position - input.world_position);

float fresnel = Fresnel(N, V);

float3 reflection = SampleReflection(N, V);

float3 refracted = SampleRefraction(N, screen_uv, water_depth);

float3 color = lerp(refracted, reflection, fresnel);
color += specular + scatter + foam;
```

| 手順 | 内容 |
| --- | --- |
| ① 法線 | 波の法線 ＋ 細かい法線マップ（[Water Waves](../waves/index.md)） |
| ② フレネル | 反射と透過の割合 |
| ③ 屈折の色 | 歪ませた背景 ＋ 深度による吸収 |
| ④ 反射の色 | 環境マップ・SSR・平面反射 |
| ⑤ 混ぜる | `lerp(屈折, 反射, F)` |
| ⑥ 足す | スペキュラ・散乱・泡（[Shore Foam](../shore-foam/index.md)） |

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Water Fresnel](fresnel.md) | 反射と屈折の割合 |
| [Color by Water Depth](depth-color.md) | Beer の法則 |
| [Water Refraction Distortion](refraction.md) | 水中の景色を曲げる |
| [Specular (Sun Glint)](specular.md) | 太陽の反射 |
| [Water Reflection](reflection.md) | 空と周囲の映り込み |
| [Scattering Color (SSS-Like)](scattering.md) | 波頭の透け感 |
| [Water Color Parameters](parameters.md) | 水の色の決め方 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 水 ＝ 反射 ＋ 屈折 ＋ 吸収 ＋ 散乱
    - [x] フレネルと水深で、見た目が決まる

## 参考

- Gordon, Brown, Jacobs, "Computed Relationships between the Inherent and Apparent Optical Properties of a Flat Homogeneous Ocean", Applied Optics, Vol. 14, No. 2, 1975（水中の散乱と吸収から、水の色を求める式）
- Pope, Fry, "Absorption Spectrum (380–700 nm) of Pure Water. II. Integrating Cavity Measurements", Applied Optics, Vol. 36, No. 33, 1997（純水の吸収係数の測定値）
- Schlick, "An Inexpensive BRDF Model for Physically-based Rendering", Computer Graphics Forum, Vol. 13, No. 3, 1994（Schlick 近似）
- Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, 2005（画面のコピーを、ずらして使う屈折）
- Cox, Munk, "Measurement of the Roughness of the Sea Surface from Photographs of the Sun's Glitter", Journal of the Optical Society of America, Vol. 44, No. 11, 1954（風速と波の傾きの関係）
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014（反射と、フレネルの扱い）

## 関連ページ

- [Water](../index.md)
- [Water Waves](../waves/index.md)
- [Refraction](../../translucency/refraction/index.md)
