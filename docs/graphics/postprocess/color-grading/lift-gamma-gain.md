---
title: リフト・ガンマ・ゲイン
tags:
  - 描画
---

# リフト・ガンマ・ゲイン

<strong>リフト・ガンマ・ゲイン（LGG）</strong>は、**映画のカラー グレーディングで定番の 3 つのつまみ**で、**暗部（リフト）・中間（ガンマ）・明部（ゲイン）を、別々に調整**します。<strong>「暗い所は青く、明るい所は暖かく」</strong>のように**明るさの領域ごとに色味を変える**表現が**簡単にできます**。このページでは、**3 つの役割・式・ASC CDL（スロープ・オフセット・パワー）との関係・色（RGB）ごとの調整・シャドウ/ミッド/ハイライトのカラー バランス**を説明します。

!!! tip "ポイント"
    - <strong>ゲイン</strong> ＝ <strong>掛け算</strong>。<strong>明部</strong>に<strong>強く効く</strong>（<strong>傾き</strong>）。
    - <strong>リフト</strong> ＝ <strong>足し算</strong>。<strong>暗部</strong>に<strong>強く効く</strong>（<strong>黒の持ち上げ</strong>）。
    - <strong>ガンマ</strong> ＝ <strong>べき乗</strong>。<strong>中間調</strong>の<strong>明るさ</strong>を変える。
    - <strong>RGB 別々に</strong>調整できる → <strong>領域ごとの色味づけ</strong>（<strong>ティール＆オレンジ</strong>など）。
    - <strong>ASC CDL</strong> は<strong>業界標準の形式</strong>（<strong>スロープ・オフセット・パワー・彩度</strong>）。
    - <strong>ゲーム</strong>では<strong>リニアでなく、ガンマ・対数空間</strong>で<strong>行う</strong>と<strong>感覚が合う</strong>。

## 3 つのつまみ

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="リフト・ガンマ・ゲイン">
<text x="20" y="26" class="fig-title">3 つのつまみは、トーン曲線の別々の部分を動かす</text>
<g transform="translate(30,50)">
<text x="0" y="-6" style="font-size:13px;font-weight:700">リフト（暗部）</text>
<line x1="0" y1="150" x2="200" y2="150" stroke="currentColor" stroke-opacity="0.4"/><line x1="0" y1="0" x2="0" y2="150" stroke="currentColor" stroke-opacity="0.4"/>
<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4 3" points="0,150 200,0"/>
<polyline fill="none" stroke="#2563eb" stroke-width="3" points="0,110 200,0"/>
<text x="0" y="172" style="font-size:12px">黒が持ち上がる</text>
</g>
<g transform="translate(280,50)">
<text x="0" y="-6" style="font-size:13px;font-weight:700">ガンマ（中間）</text>
<line x1="0" y1="150" x2="200" y2="150" stroke="currentColor" stroke-opacity="0.4"/><line x1="0" y1="0" x2="0" y2="150" stroke="currentColor" stroke-opacity="0.4"/>
<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4 3" points="0,150 200,0"/>
<polyline fill="none" stroke="#2ea043" stroke-width="3" points="0,150 30,110 70,76 120,44 200,0"/>
<text x="0" y="172" style="font-size:12px">中間が明るくなる</text>
</g>
<g transform="translate(530,50)">
<text x="0" y="-6" style="font-size:13px;font-weight:700">ゲイン（明部）</text>
<line x1="0" y1="150" x2="200" y2="150" stroke="currentColor" stroke-opacity="0.4"/><line x1="0" y1="0" x2="0" y2="150" stroke="currentColor" stroke-opacity="0.4"/>
<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4 3" points="0,150 200,0"/>
<polyline fill="none" stroke="#e5484d" stroke-width="3" points="0,150 150,0"/>
<text x="0" y="172" style="font-size:12px">傾きが変わる（明部が強く動く）</text>
</g>
</svg>

| つまみ | 操作 | 影響が大きい範囲 |
| --- | --- | --- |
| <strong>ゲイン（Gain）</strong> | **掛ける** | **明部**（**黒（0）は動かない**） |
| <strong>リフト（Lift）</strong> | **足す** | **暗部**（**白（1）は、ほぼ動かない**） |
| <strong>ガンマ（Gamma）</strong> | **べき乗** | **中間調**（**0 と 1 は動かない**） |

## 式

```hlsl
float3 LiftGammaGain(float3 color, float3 lift, float3 gamma, float3 gain) {
  color = color * gain + lift;
  color = max(color, 0.0);
  return pow(color, 1.0 / gamma);
}
```

| 点 | 説明 |
| --- | --- |
| **`color * gain + lift`** | **直線の傾き（ゲイン）と切片（リフト）** |
| **`pow(color, 1 / gamma)`** | **中間調の曲げ。`gamma > 1` で明るく** |
| **各パラメータは `float3`** | **RGB ごとに別の値** → **領域ごとの色味づけ** |

### リフトの別の定義

**多くのツールでは、「リフトが白点を動かさない」よう**に**次の形**にします。

<div class="formula">c' = gain · ( c + lift · (1 − c) )</div>

**黒（c = 0）は `lift` だけ持ち上がり、白（c = 1）は変わりません**。**黒を沈めたり持ち上げたりする**のが**自然**になります。

## ASC CDL（スロープ・オフセット・パワー）

**ASC CDL**（American Society of Cinematographers Color Decision List）は、**映像業界で標準の色調整の交換形式**です。**LGG に近い 3 つのつまみ＋彩度**で**構成**されます。

| ASC CDL | 対応 | 式 |
| --- | --- | --- |
| <strong>スロープ（Slope）</strong> | **ゲイン** | **掛ける** |
| <strong>オフセット（Offset）</strong> | <strong>リフト（に近い）</strong> | **足す** |
| <strong>パワー（Power）</strong> | <strong>ガンマ（の逆数）</strong> | **べき乗** |
| <strong>彩度（Saturation）</strong> | **彩度** | **輝度との補間** |

<div class="formula">out = ( in × slope + offset ) ^ power　（その後、彩度）</div>

```hlsl
float3 ApplyCDL(float3 color, float3 slope, float3 offset, float3 power, float saturation) {
  float3 c = pow(max(color * slope + offset, 0.0), power);
  float luma = dot(c, float3(0.2126, 0.7152, 0.0722));
  return lerp(float3(luma, luma, luma), c, saturation);
}
```

**Resolve・Nuke などのツールと、数値をやり取りできる**ので、**外部で作ったルックをゲームに持ち込めます**。

## 領域ごとのカラー バランス

<strong>「暗部は青、中間はそのまま、明部は橙」</strong>のように**明るさの領域に別々の色味を乗せる**調整です。**ティール＆オレンジ**など、**映画的なルックの定番**です。

```hlsl
float3 ColorBalance(float3 color, float3 shadows, float3 midtones, float3 highlights) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  float shadow_weight = 1.0 - smoothstep(0.0, 0.5, luma);
  float highlight_weight = smoothstep(0.5, 1.0, luma);
  float midtone_weight = 1.0 - shadow_weight - highlight_weight;
  return color + shadows * shadow_weight + midtones * midtone_weight + highlights * highlight_weight;
}
```

| 点 | 説明 |
| --- | --- |
| **輝度で重みを決める** | **暗部・中間・明部の重みを滑らかに** |
| **`shadows` など** | <strong>色のオフセット（RGB）</strong>。<strong>小さい値（± 0.05）</strong> |
| **用途** | **ティール（暗部）＆オレンジ（明部）で、肌が引き立つ** |

<!-- fig:color-lgg-curves:begin -->
<!-- fig:color-lgg-curves:end -->

## 使いどころ

| ルック | 設定の例 |
| --- | --- |
| **夜・冷たい** | **リフトに青、ゲインを少し下げる** |
| **夕暮れ・暖かい** | **ゲインにオレンジ** |
| **荒廃・色あせ** | **リフトを持ち上げる（黒が浮く）、彩度を下げる** |
| <strong>映画的（ティール＆オレンジ）</strong> | **暗部に青緑、明部にオレンジ** |
| **コントラストの強い劇画風** | **ゲインを上げ、リフトを下げ、ガンマを調整** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **ガンマ・対数空間で** | **映像ツールと感覚が合う** |
| **CDL 形式でやり取り** | **外部のカラリストと数値を共有** |
| **LUT に焼く** | **LGG・バランス・彩度を、1 つの 3D LUT に**（[3D LUT](lut-3d.md)） |
| **小さな値で調整** | **リフト・カラー バランスは、± 0.05 程度** |
| **ボリュームで補間** | **場所ごとに、LGG を補間**（[LUT の作り方](lut-authoring.md)） |

## よくあるミス

??? failure "リフトを上げたら、白まで動いて、全体が白っぽい"
    **リフトの式を、`c + lift · (1 − c)` に**（白を動かさない）。

??? failure "ガンマの向き（`gamma` か `1 / gamma`）を間違えて、逆に動く"
    **`pow(c, 1 / gamma)` で、`gamma > 1` が明るく**。**ツールの定義を確認**。

??? failure "領域ごとのカラー バランスが強すぎて、肌が不自然"
    <strong>小さな値（± 0.05）</strong>、**肌のハイライトを避ける**。

??? failure "リニア空間で LGG を掛けて、効き方がおかしい"
    **ガンマ・対数空間で行う**、またはツールと同じ空間にそろえる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>ゲイン（掛ける・明部）・リフト（足す・暗部）・ガンマ（べき乗・中間）</strong>
    - [x] <strong>RGB 別々に</strong>で<strong>領域ごとの色味づけ</strong>
    - [x] <strong>ASC CDL（スロープ・オフセット・パワー）</strong>は<strong>業界標準</strong>
    - [x] <strong>カラー バランス（シャドウ/ミッド/ハイライト）</strong>は<strong>輝度で重み</strong>
    - [x] <strong>LUT に焼く</strong>。<strong>ガンマ・対数空間で調整</strong>

## 参考

- American Society of Cinematographers, "ASC CDL"
- Selan, "Cinematic Color: From Your Monitor to the Big Screen"（SIGGRAPH 2012）
- Blackmagic Design, "DaVinci Resolve: Primary Color Correction"

## 関連ページ

- [カラー グレーディング](index.md)
- [基本の調整](basic-adjustments.md)
- [ホワイト バランス](white-balance.md)
- [3D LUT](lut-3d.md)
