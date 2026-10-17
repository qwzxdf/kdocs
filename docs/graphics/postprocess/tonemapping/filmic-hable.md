---
title: フィルミック（Hable）
tags:
  - 描画
---

# フィルミック（Hable）

**フィルミック**は、**フィルムの感光特性に似た S 字カーブ**でトーンマップする方式です。**Uncharted 2 で使われた Hable の式**が**有名**で、**暗部を締め（黒を沈め）、中間にコントラストを付け、明部をなだらかにロールオフ**します。**Reinhard の眠さが消え、映画のような絵**になります。このページでは、**S 字の 3 つの領域（つま先・直線部・肩）・Hable の式と各係数の意味・白点・露出との関係・自分で曲線を調整する方法**を説明します。

!!! tip "ポイント"
    - フィルミック ＝ <strong>S 字の曲線</strong>。<strong>つま先（暗部）→ 直線部（中間）→ 肩（明部）</strong>の 3 領域。
    - <strong>つま先</strong>で<strong>暗部を締めて黒を沈め</strong>、<strong>肩</strong>で<strong>明部を滑らかに飽和</strong>させる。
    - Hable の式は<strong>係数 A〜F</strong>で<strong>形を決め</strong>、<strong>白点で割って 1 に正規化</strong>する。
    - <strong>露出倍率</strong>（`× 2.0`）を<strong>曲線の前に</strong>掛けて、<strong>中間の明るさを合わせる</strong>。
    - <strong>より良いやり方</strong>：<strong>係数をアーティストが調整できる</strong>ように**パラメータとして出す**。**3D LUT に焼く**。

## S 字の 3 つの領域

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="S 字カーブの 3 領域">
<text x="20" y="26" class="fig-title">フィルミック曲線：つま先・直線部・肩</text>
<line x1="80" y1="250" x2="720" y2="250" stroke="currentColor" stroke-opacity="0.5"/>
<line x1="80" y1="50" x2="80" y2="250" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#2563eb" stroke-width="4" points="80,250 120,248 160,243 200,232 240,214 280,190 320,162 360,134 400,110 440,92 480,80 520,72 560,66 600,62 640,59 680,57 720,55"/>
<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5 4" points="80,250 720,50"/>
<rect x="80" y="40" width="130" height="210" fill="#e5aa28" fill-opacity="0.12"/>
<rect x="210" y="40" width="250" height="210" fill="#2ea043" fill-opacity="0.1"/>
<rect x="460" y="40" width="260" height="210" fill="#9664e6" fill-opacity="0.1"/>
<text x="145" y="70" text-anchor="middle" style="font-size:13px;font-weight:700">つま先</text><text x="145" y="90" text-anchor="middle" style="font-size:11px">暗部を締める</text>
<text x="335" y="70" text-anchor="middle" style="font-size:13px;font-weight:700">直線部</text><text x="335" y="90" text-anchor="middle" style="font-size:11px">中間にコントラスト</text>
<text x="590" y="110" text-anchor="middle" style="font-size:13px;font-weight:700">肩</text><text x="590" y="130" text-anchor="middle" style="font-size:11px">明部を滑らかに飽和</text>
<text x="400" y="278" text-anchor="middle" style="font-size:12px">入力（HDR の明るさ）→</text>
<text x="40" y="150" style="font-size:12px">出力</text>
<text x="640" y="192" style="font-size:11px;fill:#64748b">灰色の点線 ＝ y = x</text>
</svg>

| 領域 | 役割 | 見た目 |
| --- | --- | --- |
| <strong>つま先（toe）</strong> | **暗部の立ち上がりを抑える** | **黒が沈んで締まる**。**暗部が持ち上がらない** |
| <strong>直線部（linear）</strong> | <strong>中間の傾き（コントラスト）</strong> | **メリハリ**が付く |
| <strong>肩（shoulder）</strong> | **明部で傾きがゆるやかになり 1 に漸近** | **ハイライトが白飛びせず滑らかに白へ** |

**Reinhard はつま先がなく、暗部が持ち上がる**ため**眠い**です。**S 字はつま先で暗部を沈める**ので、**絵が締まります**。

<!-- fig:tonemap-hable:begin -->
<!-- fig:tonemap-hable:end -->

## Hable の式（Uncharted 2）

**有理関数**で**S 字を作る**式です。

<div class="formula">f(x) = ( (x·(A·x + C·B) + D·E) / (x·(A·x + B) + D·F) ) − E/F</div>

```hlsl
float3 HableCurve(float3 x) {
  const float a = 0.15;
  const float b = 0.50;
  const float c = 0.10;
  const float d = 0.20;
  const float e = 0.02;
  const float f = 0.30;
  return ((x * (a * x + c * b) + d * e) / (x * (a * x + b) + d * f)) - e / f;
}

float3 HableTonemap(float3 color) {
  const float exposure_bias = 2.0;
  const float white_point = 11.2;
  float3 mapped = HableCurve(color * exposure_bias);
  float3 white_scale = 1.0 / HableCurve(white_point);
  return mapped * white_scale;
}
```

### 各係数の意味

| 係数 | 名前 | 効き方 |
| --- | --- | --- |
| <strong>A（0.15）</strong> | **肩の強さ** | **大きいと明部が早く頭打ち** |
| <strong>B（0.50）</strong> | **直線部の強さ** | <strong>中間の傾き（コントラスト）</strong> |
| <strong>C（0.10）</strong> | **直線部の角度** | **直線の傾きの調整** |
| <strong>D（0.20）</strong> | **つま先の強さ** | **大きいと暗部が沈む** |
| <strong>E（0.02）</strong> | **つま先の分子** | **つま先の細かい形** |
| <strong>F（0.30）</strong> | **つま先の分母** | **つま先の細かい形** |
| <strong>W（11.2）</strong> | **白点** | **この入力で出力がちょうど 1** |

### 白点で正規化する理由

**曲線は、x が大きくても 1 に届きません**。**白点 W の出力で割る**（`white_scale`）ことで**入力 W のとき出力がちょうど 1** になります。

| 入力 | 出力（おおよそ） |
| --- | --- |
| **0** | **0** |
| **0.18（中間灰）× 2** | **約 0.22** |
| **1 × 2** | **約 0.55** |
| **11.2** | **1** |

### `exposure_bias`（2.0）

**曲線の前に掛ける倍率**で、**中間の明るさを合わせる**ためのものです。**露出（[露出](exposure.md)）が別にある**ので**二重にならないよう**、**この値は「曲線に合わせた補正」と考え、あまり動かさない**ようにします。

## 色の保ち方

**Hable をチャンネルごとに掛ける**と、**フィルムのように明るい色が白へ向かう**絵になります。**色相を保ちたい**なら、**輝度に掛けて比率を保つ**方式もあります（[色相の保ち方](hue-preservation.md)）。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **係数をパラメータで出す** | **A〜F をアーティストが調整できる**ようにする（**肩・つま先・白点**を**スライダー**で） |
| **形を「見た目の言葉」で設定** | <strong>「つま先の強さ」「肩の長さ」「白点」</strong> の**3 つだけ**を出し、**内部で A〜F に変換** |
| **3D LUT に焼く** | **計算の重い曲線を、LUT に焼いて、1 回の表引き**にする（[カラー グレーディング](../color-grading/index.md)） |
| **ACES・AgX と比べる** | **同じシーンで比べ、色の出方で選ぶ**（[ACES](aces.md)・[AgX](agx.md)） |
| **HDR 出力と分ける** | **HDR ディスプレイでは、別の曲線**（[ガンマと HDR 出力](gamma-srgb.md)） |

## よくあるミス

??? failure "露出を `exposure_bias` で調整して、自動露出と二重になる"
    **明るさの調整は、露出（EV）で**。**`exposure_bias` は固定**。

??? failure "白点を変えたのに、白が出ない"
    **`white_scale` の計算を忘れた**。**`1 / HableCurve(white_point)` を掛ける**。

??? failure "暗部が潰れすぎて、夜のシーンが真っ黒"
    **つま先（D・E・F）を弱める**、**露出を上げる**、**曲線の前にオフセット**を加える。

??? failure "色相が変わって、赤い物がオレンジに見える"
    **チャンネルごとの副作用**。**輝度ベースにする、または AgX・ACES の色補正**を検討。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フィルミック ＝ <strong>S 字（つま先・直線部・肩）</strong>。<strong>暗部を締め、明部を滑らかに</strong>
    - [x] Hable の式は<strong>係数 A〜F ＋ 白点 W</strong>。<strong>白点の出力で割って 1 に正規化</strong>
    - [x] <strong>つま先が暗部を沈める</strong>ので、<strong>Reinhard より締まる</strong>
    - [x] <strong>露出は別に</strong>。<strong>`exposure_bias` は固定</strong>
    - [x] <strong>パラメータ化・LUT 化</strong>で<strong>画作りを制御しやすく</strong>

## 参考

- Hable, "Uncharted 2: HDR Lighting"（GDC 2010）
- Hable, "Filmic Tonemapping Operators"（filmicworlds.com）
- Duiker, "Filmic Tonemapping for Real-time Rendering"（SIGGRAPH 2010）

## 関連ページ

- [トーンマッピングと露出](index.md)
- [Reinhard](reinhard.md)
- [ACES](aces.md)
- [色相の保ち方](hue-preservation.md)
