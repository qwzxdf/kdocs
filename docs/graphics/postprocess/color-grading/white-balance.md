---
title: White Balance
tags:
  - 描画
---

# White Balance

**同じ白い紙でも晴天の下では青白く、白熱灯の下では黄色く見えます**。**人間の目はこれを自動で補正して、「白い紙は白い」と感じます**（**色の恒常性**）。**カメラはこの補正を「ホワイト バランス」で行い**、**ゲームでも画面全体の色温度を調整して、「暖かい夕暮れ」や「冷たい夜」を作る**ために**使います**。このページでは、**色温度（ケルビン）と色合い・光源の色を打ち消す考え方・簡易実装（LMS 空間）・ゲームでの使い方・注意点**を説明します。

!!! tip "ポイント"
    - ホワイト バランス ＝ <strong>光源の色を打ち消して、白を白く見せる</strong>。<strong>全体の色味を暖色〜寒色にずらす</strong>。
    - <strong>色温度（K）</strong>：<strong>低い（約 2000 K）は橙、高い（約 10000 K）は青</strong>。<strong>6500 K 前後が日中の昼光（D65）</strong>。
    - <strong>色合い（Tint）</strong>：<strong>緑〜マゼンタの軸</strong>。
    - <strong>実装</strong>：<strong>LMS（錐体）空間で白点の比率で割る</strong>のが<strong>標準的</strong>。
    - <strong>ゲームでは「補正」ではなく、「演出」に使う</strong>こと<strong>が多い</strong>。
    - <strong>トーンマップの前（リニア）で行う</strong>と<strong>自然</strong>。

<!-- fig:white-balance:begin -->

<svg class="fig illust motion" data-fig="white-balance" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-white-balance" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<linearGradient id="wb-grad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#60a5fa"/>
<stop offset="0.5" stop-color="#ffffff"/>
<stop offset="1" stop-color="#fb923c"/>
</linearGradient>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ホワイト バランス:光源の色かぶりを打ち消して、白を白に戻す</text>
<rect x="80" y="110" width="130" height="110" fill="#ceba9e" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0716;0.0791;0.0867;0.0942;0.1018;0.1093;0.1169;0.1244;0.1320;0.1396;0.1471;0.1547;0.1622;0.1698;0.1773;0.1849;0.1924;0.2000;0.2178;0.2356;0.2533;0.2711;0.2889;0.3067;0.3244;0.3422;0.3600;0.3778;0.3956;0.4133;0.4311;0.4489;0.4667;0.4844;0.5022;0.5200;0.5311;0.5422;0.5533;0.5644;0.5756;0.5867;0.5978;0.6089;0.6200;0.6311;0.6422;0.6533;0.6644;0.6756;0.6867;0.6978;0.7089;0.7200;1.0000" values="#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#ceba9e;#cdbaa0;#ccbaa1;#cabaa3;#c9baa4;#c8baa6;#c7baa7;#c6baa9;#c5baaa;#c4baac;#c3baad;#c2baaf;#c0bab0;#bfbab2;#bebab3;#bdbab5;#bcbab7;#bbbab8;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa;#bababa"/></rect>
<text x="145" y="100" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">グレーの紙</text>
<rect x="250" y="110" width="130" height="110" fill="#fff6d1" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0716;0.0791;0.0867;0.0942;0.1018;0.1093;0.1169;0.1244;0.1320;0.1396;0.1471;0.1547;0.1622;0.1698;0.1773;0.1849;0.1924;0.2000;0.2178;0.2356;0.2533;0.2711;0.2889;0.3067;0.3244;0.3422;0.3600;0.3778;0.3956;0.4133;0.4311;0.4489;0.4667;0.4844;0.5022;0.5200;0.5311;0.5422;0.5533;0.5644;0.5756;0.5867;0.5978;0.6089;0.6200;0.6311;0.6422;0.6533;0.6644;0.6756;0.6867;0.6978;0.7089;0.7200;1.0000" values="#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d1;#fff6d3;#fff6d5;#fff6d6;#fff6d8;#fff6da;#fff6dc;#fff6de;#fff6e0;#fff6e2;#fff6e4;#fff6e7;#fef6e9;#fdf6eb;#fbf6ed;#faf6ef;#f8f6f1;#f7f6f3;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6;#f6f6f6"/></rect>
<text x="315" y="100" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">白い壁</text>
<rect x="420" y="110" width="130" height="110" fill="#ff7b68" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0716;0.0791;0.0867;0.0942;0.1018;0.1093;0.1169;0.1244;0.1320;0.1396;0.1471;0.1547;0.1622;0.1698;0.1773;0.1849;0.1924;0.2000;0.2178;0.2356;0.2533;0.2711;0.2889;0.3067;0.3244;0.3422;0.3600;0.3778;0.3956;0.4133;0.4311;0.4489;0.4667;0.4844;0.5022;0.5200;0.5311;0.5422;0.5533;0.5644;0.5756;0.5867;0.5978;0.6089;0.6200;0.6311;0.6422;0.6533;0.6644;0.6756;0.6867;0.6978;0.7089;0.7200;1.0000" values="#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#ff7b68;#fe7b69;#fc7b6a;#fb7b6b;#f97b6c;#f87b6d;#f77b6e;#f57b6f;#f47b70;#f27b71;#f17b72;#f07b73;#ee7b74;#ed7b75;#ec7b76;#ea7b77;#e97b79;#e87b7a;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b;#e67b7b"/></rect>
<text x="485" y="100" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">赤い服</text>
<rect x="590" y="110" width="130" height="110" fill="#8894c4" stroke="#94a3b8" stroke-width="2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0716;0.0791;0.0867;0.0942;0.1018;0.1093;0.1169;0.1244;0.1320;0.1396;0.1471;0.1547;0.1622;0.1698;0.1773;0.1849;0.1924;0.2000;0.2178;0.2356;0.2533;0.2711;0.2889;0.3067;0.3244;0.3422;0.3600;0.3778;0.3956;0.4133;0.4311;0.4489;0.4667;0.4844;0.5022;0.5200;0.5311;0.5422;0.5533;0.5644;0.5756;0.5867;0.5978;0.6089;0.6200;0.6311;0.6422;0.6533;0.6644;0.6756;0.6867;0.6978;0.7089;0.7200;1.0000" values="#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8894c4;#8794c6;#8694c7;#8694c9;#8594cb;#8494cd;#8394cf;#8394d1;#8294d3;#8194d4;#8094d6;#8094d8;#7f94da;#7e94dc;#7d94de;#7d94e0;#7c94e2;#7b94e4;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6;#7b94e6"/></rect>
<text x="655" y="100" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">青い服</text>
<rect x="80" y="290" width="620" height="14" rx="7" fill="url(#wb-grad)"/>
<text x="80" y="280" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">色温度（青い光 ← → 暖かい光）</text>
<circle cx="588.4" cy="297" r="11" fill="#1f2937" stroke="#ffffff" stroke-width="2"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.2000;0.5200;0.7200;1.0000" values="588.4;588.4;588.4;390;390;390"/></circle>
<text x="80" y="360" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">暖色の光の下:グレーの紙が、橙がかって見える<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;1.0000" values="1;1;0;0"/></text>
<text x="80" y="360" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">色温度を青い側へ動かして、色かぶりを打ち消す…<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;0.5197;0.5200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="80" y="360" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">グレーの紙が、無彩色に戻った。他の色も、自然な色に<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5197;0.5200;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:white-balance:end -->

## 色温度と見た目

**物体を熱すると温度に応じた色で光ります**（**黒体放射**）。<strong>この温度（ケルビン）が「色温度」</strong>で、**光源の色を表す**のに**使われます**。

<svg class="fig illust" viewBox="0 0 780 190" role="img" aria-label="色温度">
<text x="20" y="26" class="fig-title">色温度：低いほど橙（暖色）、高いほど青（寒色）</text>
<defs><linearGradient id="wb-g" x1="0" x2="1"><stop offset="0" stop-color="#ff7a1a"/><stop offset="0.25" stop-color="#ffb35c"/><stop offset="0.5" stop-color="#fff4e6"/><stop offset="0.72" stop-color="#e9f1ff"/><stop offset="1" stop-color="#9ec3ff"/></linearGradient></defs>
<rect x="40" y="56" width="700" height="40" fill="url(#wb-g)" stroke="#94a3b8"/>
<g font-size="12" text-anchor="middle"><text x="60" y="116">1900 K</text><text x="60" y="134" style="font-size:11px">ろうそく</text>
<text x="210" y="116">2700 K</text><text x="210" y="134" style="font-size:11px">白熱電球</text>
<text x="390" y="116">5000 K</text><text x="390" y="134" style="font-size:11px">昼白色</text>
<text x="540" y="116">6500 K</text><text x="540" y="134" style="font-size:11px">昼光（D65）</text>
<text x="720" y="116">10000 K</text><text x="720" y="134" style="font-size:11px">青空の日陰</text></g>
</svg>

| 光源 | 色温度 |
| --- | --- |
| **ろうそくの炎** | **約 1900 K**（**橙**） |
| **白熱電球** | **約 2700 K**（**暖かい黄色**） |
| **朝・夕方の日光** | **約 3500〜4500 K** |
| **正午の日光** | **約 5500〜6500 K**（**ほぼ白**） |
| **曇り・日陰** | **約 7000〜10000 K**（**青白い**） |

## 白を白に戻す考え方

**光源が橙（低い色温度）のとき、白い物は橙に映ります**。<strong>その橙を打ち消す（青を足す・橙を減らす）</strong>と、**白が白に戻ります**。**これがホワイト バランスの補正**です。

| 操作 | 結果 |
| --- | --- |
| **光源の色温度を指定** | **その光源の色が白になる**ように補正（**画面全体が逆の色へ**） |
| <strong>ホワイト バランスの温度を「上げる」</strong> | <strong>画面が暖かく（橙）</strong>なる（**青い光源を想定して、補正しすぎ**） |
| <strong>「下げる」</strong> | <strong>画面が青く（寒色）</strong>なる |

<strong>ゲームでは、「補正」というより、画面の色味を作る「演出」</strong>として**使います**。**温度を上げて暖かく・下げて冷たく**調整します。

## 実装（LMS 空間）

**人間の錐体（L・M・S）の反応**を**表す LMS 空間**で、**光源の白点を基準の白に合わせる**のが**標準的**です。

```hlsl
float3 WhiteBalance(float3 color, float temperature, float tint) {
  float t1 = temperature / 0.6;
  float t2 = tint / 0.6;
  float x = 0.31271 - t1 * (t1 < 0.0 ? 0.1 : 0.05);
  float y = 2.87 * x - 3.0 * x * x - 0.27509 + t2 * 0.05;
  float3 xyz = float3(x / y, 1.0, (1.0 - x - y) / y);
  float3 lms = mul(kXyzToLms, xyz);
  float3 white_lms = mul(kXyzToLms, float3(0.95047, 1.0, 1.08883));
  float3 balance = white_lms / lms;
  float3 color_lms = mul(kRgbToLms, color);
  return mul(kLmsToRgb, color_lms * balance);
}
```

| 点 | 説明 |
| --- | --- |
| **`temperature`・`tint`** | **−1〜+1 のつまみ**（<strong>色温度（暖〜寒）と、色合い（緑〜マゼンタ）</strong>） |
| **`x, y`** | **色度座標**。**D65 の白（0.31271, 0.32902）を基準にずらす** |
| **`white_lms / lms`** | <strong>光源の LMS で割る比率（ゲイン）</strong> |
| **`kRgbToLms` など** | **色空間変換の 3×3 行列**（**公開されている値**） |

**もっと簡単な近似**は、**RGB にゲインを掛けるだけ**です。

```hlsl
float3 SimpleWhiteBalance(float3 color, float temperature) {
  float3 warm = float3(1.0, 0.9, 0.75);
  float3 cool = float3(0.8, 0.9, 1.0);
  float3 gain = lerp(warm, cool, saturate(0.5 - temperature * 0.5));
  return color * gain;
}
```

| 方式 | 精度 | 手軽さ |
| --- | --- | --- |
| <strong>LMS 空間（本格）</strong> | **高い** | **行列を使う** |
| <strong>RGB ゲイン（簡易）</strong> | <strong>粗い（明るさが変わる）</strong> | **1 行** |

## 色合い（Tint）

**色温度が「橙〜青」の軸**だとすると**色合いは「緑〜マゼンタ」の軸**です。**蛍光灯の緑かぶり**を**打ち消したり**、**ファンタジーな色味**を**作るのに使います**。

| つまみ | 軸 |
| --- | --- |
| <strong>温度（Temperature）</strong> | **橙 ⇔ 青** |
| <strong>色合い（Tint）</strong> | **緑 ⇔ マゼンタ** |

## ゲームでの使い方

| 使い方 | 内容 |
| --- | --- |
| **時間帯の演出** | **朝：暖かく、昼：中立、夕方：橙、夜：青** |
| **場所の演出** | **洞窟：冷たい青、火山：暖かい橙** |
| **状態の演出** | **体力が低い：色が冷える・彩度が下がる** |
| **光源との整合** | **画面の主光源の色とホワイト バランスで調和させる** |

**時間帯の変化**に**合わせて、色温度を補間**すると**自然な移り変わり**になります（[空と大気](../../atmosphere/sky-models/index.md)）。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **リニア空間でトーンマップの前** | **物理的に自然**（**HDR の値で比率を保つ**） |
| **LMS（錐体）空間で** | **より自然な補正** |
| **LUT に焼く** | **ほかの調整と一緒に 1 つに**（[3D LUT](lut-3d.md)） |
| **ボリュームで補間** | **場所ごとに温度を変えて、境で滑らかに** |
| **ライトの色と合わせる** | **光源の色（ライト）と、ホワイト バランスで二重に偏らない** |

## よくあるミス

??? failure "ホワイト バランスと、ライトの色の両方を動かして、色かぶりが強すぎる"
    **ライトの色と全体のホワイト バランスの役割を分ける**（**光源は物理的に全体の色味は演出**）。

??? failure "RGB ゲインで調整したら、全体の明るさも変わった"
    **LMS で輝度を保つ**、または**簡易版の後に輝度を補正**する。

??? failure "ガンマ空間でホワイト バランスして、色が不自然"
    **リニア空間**で行う。

??? failure "場所の切り替えで、色温度が急に変わる"
    **ボリュームで補間**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ホワイト バランス ＝ <strong>光源の色を打ち消して、全体の色味をずらす</strong>
    - [x] <strong>色温度（K）</strong>：<strong>低い ＝ 橙、高い ＝ 青</strong>。<strong>色合い</strong>は<strong>緑〜マゼンタ</strong>
    - [x] <strong>LMS 空間で、白点の比で割る</strong>のが<strong>本格的</strong>。<strong>RGB ゲインは簡易</strong>
    - [x] <strong>ゲームでは「演出」</strong>に使う（<strong>時間帯・場所・状態</strong>）
    - [x] <strong>リニア・トーンマップの前</strong>で行う

## 参考

- CIE, "Colorimetry"（色度図・色温度）
- Selan, "Cinematic Color: From Your Monitor to the Big Screen"（SIGGRAPH 2012）
- Bruce Lindbloom, "RGB/XYZ Matrices"

## 関連ページ

- [Color Grading](index.md)
- [Basic Adjustments](basic-adjustments.md)
- [Lift, Gamma, Gain](lift-gamma-gain.md)
- [Sky Models](../../atmosphere/sky-models/index.md)
