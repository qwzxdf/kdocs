---
title: Water Shading
tags:
  - 描画
---

# Water Shading

**水の見た目は、反射・屈折・吸収・散乱が混ざったものです**。**角度によって反射と屈折の割合が変わり（フレネル）、深いほど色が濃くなります（Beer の法則）**。このセクションでは、**水面で起きていること・フレネル・水深による色・屈折の歪み・スペキュラ・反射・散乱・パラメータ**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **水面では、反射と屈折が、角度で混ざる**。
    - **深いほど、水の色が濃くなる**。
    - **太陽の反射（スペキュラ）が、水らしさを決める**。
    - **散乱で、波頭が明るく透ける**。

## 水面で何が起きているか
**光が水面に当たると一部は反射し、残りは水の中へ屈折して入ります**。**水の中では吸収と散乱を受けながら進み**、**底や水中の物で跳ね返り**、**再び水面を通って目に入ります**。

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

水の見た目は 5 つの成分でできています。<strong>反射</strong>は、空や周囲の景色を映す成分です（[Reflections](../../reflections/index.md)）。<strong>屈折と透過</strong>は、水中の物や底が透けて見える（歪む）成分です。<strong>吸収</strong>は、水を通る距離に応じて、色が変わり暗くなる成分です。<strong>散乱</strong>は、水中の粒子で光が散らばり、水自体が青緑に光る成分です。<strong>スペキュラ</strong>は、太陽や光源の鋭い反射です。

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

合成の手順は 6 段階です。最初に法線を求めます（波の法線に細かい法線マップを足します。[Water Waves](../waves/index.md)）。次にフレネルで、反射と透過の割合を決めます。屈折の色は、歪ませた背景に深度による吸収をかけて求めます。反射の色は、環境マップ・SSR・平面反射から得ます。そして `lerp(屈折, 反射, F)` で混ぜます。最後に、スペキュラ・散乱・泡を足します（[Shore Foam](../shore-foam/index.md)）。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [フレネル](fresnel.md) | 反射と屈折の割合 |
| [Color by Water Depth](depth-color.md) | Beer の法則 |
| [屈折の歪み](refraction.md) | 水中の景色を曲げる |
| [スペキュラ](specular.md) | 太陽の反射 |
| [反射](reflection.md) | 空と周囲の映り込み |
| [散乱（SSS 風）](scattering.md) | 波頭の透け感 |
| [色のパラメータ](parameters.md) | 水の色の決め方 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **水 ＝ 反射 ＋ 屈折 ＋ 吸収 ＋ 散乱**
    - [x] **フレネルと水深で、見た目が決まる**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Water](../index.md)
- [Water Waves](../waves/index.md)
- [Refraction](../../translucency/refraction/index.md)
