---
title: Film Grain
tags:
  - 描画
---

# Film Grain

<strong>フィルム グレイン</strong>は、<strong>画面に細かい粒状のノイズを加える</strong>効果です。フィルム写真の「粒子」の質感を再現し、映画らしい雰囲気を出します。また、グラデーション（空・暗部）の縞（バンディング）を、ノイズで目立たなくするという実用的な効果もあります。ノイズの質（周波数・分布）と、明るさに応じた強さの付け方が見た目を左右します。このページでは、ノイズの作り方・強さを明るさで変える方法・動かし方（毎フレーム変える）・ディザリングとの関係・使いどころを説明します。

!!! tip "ポイント"
    - グレイン ＝ <strong>画面に、粒状のノイズを足す</strong>。<strong>フィルムの質感</strong>。
    - <strong>ノイズは毎フレーム変える</strong>（<strong>動くノイズ ＝ フィルムの粒子が動く感じ</strong>）。
    - <strong>明るさで強さを変える</strong>：<strong>中間調が最も目立ち、真っ黒・真っ白では弱い</strong>。
    - <strong>ノイズの質</strong>：<strong>白色ノイズ（粗い）か、ブルー ノイズ／ガウス（自然）か</strong>。
    - <strong>ディザリング</strong>（<strong>バンディング隠し</strong>）にも<strong>効く</strong>（<strong>1 ビット分のノイズ</strong>で十分）。
    - <strong>かけすぎない</strong>。<strong>細部が見えなくなる</strong>。<strong>設定で切れる</strong>。

## 実際のグレイン

<strong>フィルムの感光材料は、微小な銀の粒子</strong>からできています。<strong>露光された粒子の分布が、ランダムなので画像に粒状のノイズ</strong>が見えます。感度（ISO）が高いフィルムほど、粒子が大きく、ノイズが目立つです。

| 特徴 | 内容 |
| --- | --- |
| 粒子の大きさ | ISO が高いほど大きい |
| 明るさへの依存 | 中間調で目立ち、真っ黒や真っ白では弱い |
| フレームごとに違う | 1 秒間に 24 回違うノイズ → 動いて見える |
| 色 | カラーフィルムは色つきのノイズ。白黒は輝度のみ |

## 基本の実装

<strong>ランダムな値を作り、色に足します</strong>。

```hlsl
float Hash(float2 p) {
  float3 p3 = frac(float3(p.xyx) * 0.1031);
  p3 += dot(p3, p3.yzx + 33.33);
  return frac((p3.x + p3.y) * p3.z);
}

float3 ApplyGrain(float3 color, float2 uv, float time, float intensity) {
  float2 seed = uv * resolution + time * 61.0;
  float noise = Hash(seed) - 0.5;
  return color + noise * intensity;
}
```

| 点 | 説明 |
| --- | --- |
| `Hash` | 座標から擬似乱数を作る関数（テクスチャ不要） |
| `seed = uv × 解像度 + time` | 画素ごとに違い、フレームごとに違うシード |
| `noise − 0.5` | −0.5〜+0.5 の、平均 0 のノイズ |
| `intensity` | <strong>強さ（0.01〜0.05）</strong> |

<!-- fig:film-grain-luma:begin -->

<svg class="fig illust motion" data-fig="film-grain-luma" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-film-grain-luma" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">フィルム グレイン: 暗い所と明るい所には、粒を弱く、中間に強く(明るさに応じて強さを変える)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">黒 → 白の階調(48 段)に、でたらめな粒を足す。粒の強さの掛け方を 2 通りで比べる</text>
<text x="60.0" y="108" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">階調(粒なし)</text>
<rect x="60.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#030303"/></rect>
<rect x="77.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#080808"/></rect>
<rect x="94.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#0d0d0d"/></rect>
<rect x="111.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#131313"/></rect>
<rect x="128.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#181818"/></rect>
<rect x="145.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#1d1d1d"/></rect>
<rect x="162.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#232323"/></rect>
<rect x="179.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#282828"/></rect>
<rect x="196.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#2d2d2d"/></rect>
<rect x="213.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#323232"/></rect>
<rect x="230.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#383838"/></rect>
<rect x="247.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#3d3d3d"/></rect>
<rect x="264.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#424242"/></rect>
<rect x="281.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#484848"/></rect>
<rect x="298.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#4d4d4d"/></rect>
<rect x="315.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#525252"/></rect>
<rect x="332.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#585858"/></rect>
<rect x="349.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#5d5d5d"/></rect>
<rect x="366.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#626262"/></rect>
<rect x="383.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#686868"/></rect>
<rect x="400.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#6d6d6d"/></rect>
<rect x="417.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#727272"/></rect>
<rect x="434.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#787878"/></rect>
<rect x="451.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#7d7d7d"/></rect>
<rect x="468.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#828282"/></rect>
<rect x="485.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#878787"/></rect>
<rect x="502.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#8d8d8d"/></rect>
<rect x="519.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#929292"/></rect>
<rect x="536.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#979797"/></rect>
<rect x="553.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#9d9d9d"/></rect>
<rect x="570.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#a2a2a2"/></rect>
<rect x="587.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#a7a7a7"/></rect>
<rect x="604.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#adadad"/></rect>
<rect x="621.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#b2b2b2"/></rect>
<rect x="638.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#b7b7b7"/></rect>
<rect x="655.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bdbdbd"/></rect>
<rect x="672.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="689.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#c7c7c7"/></rect>
<rect x="706.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#cdcdcd"/></rect>
<rect x="723.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#d2d2d2"/></rect>
<rect x="740.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#d7d7d7"/></rect>
<rect x="757.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="774.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="791.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#e7e7e7"/></rect>
<rect x="808.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ececec"/></rect>
<rect x="825.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="842.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#f7f7f7"/></rect>
<rect x="859.0" y="114.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="60.0" y="114" width="816.0" height="34.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="186" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">一様な強さの粒</text>
<rect x="60.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#000000"/></rect>
<rect x="77.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721" values="#e5e7eb;#222222"/></rect>
<rect x="94.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#0a0a0a"/></rect>
<rect x="111.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#e5e7eb;#1a1a1a"/></rect>
<rect x="128.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#202020"/></rect>
<rect x="145.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0814" values="#e5e7eb;#292929"/></rect>
<rect x="162.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#212121"/></rect>
<rect x="179.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0860" values="#e5e7eb;#383838"/></rect>
<rect x="196.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#101010"/></rect>
<rect x="213.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#e5e7eb;#444444"/></rect>
<rect x="230.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#1f1f1f"/></rect>
<rect x="247.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0953" values="#e5e7eb;#373737"/></rect>
<rect x="264.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#343434"/></rect>
<rect x="281.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000" values="#e5e7eb;#434343"/></rect>
<rect x="298.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#3e3e3e"/></rect>
<rect x="315.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047" values="#e5e7eb;#666666"/></rect>
<rect x="332.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#5d5d5d"/></rect>
<rect x="349.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093" values="#e5e7eb;#5a5a5a"/></rect>
<rect x="366.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#444444"/></rect>
<rect x="383.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1140" values="#e5e7eb;#808080"/></rect>
<rect x="400.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#7b7b7b"/></rect>
<rect x="417.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="434.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#646464"/></rect>
<rect x="451.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233" values="#e5e7eb;#6c6c6c"/></rect>
<rect x="468.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#e5e7eb;#7f7f7f"/></rect>
<rect x="485.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1279" values="#e5e7eb;#979797"/></rect>
<rect x="502.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1302" values="#e5e7eb;#757575"/></rect>
<rect x="519.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1326" values="#e5e7eb;#939393"/></rect>
<rect x="536.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1349" values="#e5e7eb;#a0a0a0"/></rect>
<rect x="553.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1372" values="#e5e7eb;#9e9e9e"/></rect>
<rect x="570.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1395" values="#e5e7eb;#b0b0b0"/></rect>
<rect x="587.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1419" values="#e5e7eb;#b3b3b3"/></rect>
<rect x="604.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1442" values="#e5e7eb;#b0b0b0"/></rect>
<rect x="621.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1465" values="#e5e7eb;#a9a9a9"/></rect>
<rect x="638.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1488" values="#e5e7eb;#b9b9b9"/></rect>
<rect x="655.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1512" values="#e5e7eb;#b7b7b7"/></rect>
<rect x="672.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1535" values="#e5e7eb;#cccccc"/></rect>
<rect x="689.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1558" values="#e5e7eb;#b9b9b9"/></rect>
<rect x="706.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1581" values="#e5e7eb;#e8e8e8"/></rect>
<rect x="723.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1605" values="#e5e7eb;#e2e2e2"/></rect>
<rect x="740.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1628" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="757.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1651" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="774.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1674" values="#e5e7eb;#ececec"/></rect>
<rect x="791.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1698" values="#e5e7eb;#f1f1f1"/></rect>
<rect x="808.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1721" values="#e5e7eb;#d2d2d2"/></rect>
<rect x="825.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1744" values="#e5e7eb;#ffffff"/></rect>
<rect x="842.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1767" values="#e5e7eb;#f6f6f6"/></rect>
<rect x="859.0" y="190.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1791" values="#e5e7eb;#e9e9e9"/></rect>
<rect x="60.0" y="190" width="816.0" height="34.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="258" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">明るさに応じた強さの粒(中間が最大)</text>
<rect x="60.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#020202"/></rect>
<rect x="77.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2814" values="#e5e7eb;#0b0b0b"/></rect>
<rect x="94.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2837" values="#e5e7eb;#0d0d0d"/></rect>
<rect x="111.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2860" values="#e5e7eb;#151515"/></rect>
<rect x="128.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2884" values="#e5e7eb;#1b1b1b"/></rect>
<rect x="145.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#222222"/></rect>
<rect x="162.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2930" values="#e5e7eb;#222222"/></rect>
<rect x="179.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2953" values="#e5e7eb;#303030"/></rect>
<rect x="196.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2977" values="#e5e7eb;#1c1c1c"/></rect>
<rect x="213.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3000" values="#e5e7eb;#3e3e3e"/></rect>
<rect x="230.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3023" values="#e5e7eb;#272727"/></rect>
<rect x="247.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3047" values="#e5e7eb;#393939"/></rect>
<rect x="264.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3070" values="#e5e7eb;#373737"/></rect>
<rect x="281.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3093" values="#e5e7eb;#444444"/></rect>
<rect x="298.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3116" values="#e5e7eb;#404040"/></rect>
<rect x="315.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3140" values="#e5e7eb;#636363"/></rect>
<rect x="332.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3163" values="#e5e7eb;#5c5c5c"/></rect>
<rect x="349.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3186" values="#e5e7eb;#5a5a5a"/></rect>
<rect x="366.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3209" values="#e5e7eb;#464646"/></rect>
<rect x="383.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3233" values="#e5e7eb;#7f7f7f"/></rect>
<rect x="400.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3256" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="417.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3279" values="#e5e7eb;#8c8c8c"/></rect>
<rect x="434.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3302" values="#e5e7eb;#646464"/></rect>
<rect x="451.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3326" values="#e5e7eb;#6c6c6c"/></rect>
<rect x="468.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3349" values="#e5e7eb;#7f7f7f"/></rect>
<rect x="485.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3372" values="#e5e7eb;#979797"/></rect>
<rect x="502.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3395" values="#e5e7eb;#757575"/></rect>
<rect x="519.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3419" values="#e5e7eb;#939393"/></rect>
<rect x="536.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3442" values="#e5e7eb;#9f9f9f"/></rect>
<rect x="553.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3465" values="#e5e7eb;#9e9e9e"/></rect>
<rect x="570.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3488" values="#e5e7eb;#afafaf"/></rect>
<rect x="587.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3512" values="#e5e7eb;#b2b2b2"/></rect>
<rect x="604.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3535" values="#e5e7eb;#afafaf"/></rect>
<rect x="621.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3558" values="#e5e7eb;#ababab"/></rect>
<rect x="638.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3581" values="#e5e7eb;#b9b9b9"/></rect>
<rect x="655.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3605" values="#e5e7eb;#b9b9b9"/></rect>
<rect x="672.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3628" values="#e5e7eb;#c9c9c9"/></rect>
<rect x="689.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3651" values="#e5e7eb;#bdbdbd"/></rect>
<rect x="706.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3674" values="#e5e7eb;#dedede"/></rect>
<rect x="723.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3698" values="#e5e7eb;#dbdbdb"/></rect>
<rect x="740.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3721" values="#e5e7eb;#cccccc"/></rect>
<rect x="757.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3744" values="#e5e7eb;#dcdcdc"/></rect>
<rect x="774.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3767" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="791.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3791" values="#e5e7eb;#ebebeb"/></rect>
<rect x="808.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3814" values="#e5e7eb;#e5e5e5"/></rect>
<rect x="825.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3837" values="#e5e7eb;#f5f5f5"/></rect>
<rect x="842.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3860" values="#e5e7eb;#f7f7f7"/></rect>
<rect x="859.0" y="262.0" width="17.3" height="34.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3884" values="#e5e7eb;#fcfcfc"/></rect>
<rect x="60.0" y="262" width="816.0" height="34.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="30" y="320" width="560" height="170" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="310" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">粒の強さ(横 = 明るさ)</text>
<path d="M60.0,346.0 L72.75,346.0 L85.5,346.0 L98.25,346.0 L111.0,346.0 L123.75,346.0 L136.5,346.0 L149.25,346.0 L162.0,346.0 L174.75,346.0 L187.5,346.0 L200.25,346.0 L213.0,346.0 L225.75,346.0 L238.5,346.0 L251.25,346.0 L264.0,346.0 L276.75,346.0 L289.5,346.0 L302.25,346.0 L315.0,346.0 L327.75,346.0 L340.5,346.0 L353.25,346.0 L366.0,346.0 L378.75,346.0 L391.5,346.0 L404.25,346.0 L417.0,346.0 L429.75,346.0 L442.5,346.0 L455.25,346.0 L468.0,346.0 L480.75,346.0 L493.5,346.0 L506.25,346.0 L519.0,346.0 L531.75,346.0 L544.5,346.0 L557.25,346.0 L570.0,346.0" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5021;0.5023;1.0000" values="0;0;1;1"/></path>
<path d="M60.0,466.0 L72.75,454.3 L85.5,443.2 L98.25,432.7 L111.0,422.8 L123.75,413.5 L136.5,404.8 L149.25,396.7 L162.0,389.2 L174.75,382.3 L187.5,376.0 L200.25,370.3 L213.0,365.2 L225.75,360.7 L238.5,356.8 L251.25,353.5 L264.0,350.8 L276.75,348.7 L289.5,347.2 L302.25,346.3 L315.0,346.0 L327.75,346.3 L340.5,347.2 L353.25,348.7 L366.0,350.8 L378.75,353.5 L391.5,356.8 L404.25,360.7 L417.0,365.2 L429.75,370.3 L442.5,376.0 L455.25,382.3 L468.0,389.2 L480.75,396.7 L493.5,404.8 L506.25,413.5 L519.0,422.8 L531.75,432.7 L544.5,443.2 L557.25,454.3 L570.0,466.0" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5487;0.5488;1.0000" values="0;0;1;1"/></path>
<rect x="620" y="320" width="310" height="170" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="620" y="310" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">粒の見え方(平均の揺れ)</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6045;0.6047;1.0000" values="0;0;1;1"/><text x="636" y="366" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">暗い所</text>
<text x="726" y="366" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">一様 0.038</text>
<text x="826" y="366" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">調整 0.011</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6417;0.6419;1.0000" values="0;0;1;1"/><text x="636" y="402" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">中間</text>
<text x="726" y="402" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">一様 0.059</text>
<text x="826" y="402" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">調整 0.059</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6789;0.6791;1.0000" values="0;0;1;1"/><text x="636" y="438" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">明るい所</text>
<text x="726" y="438" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">一様 0.050</text>
<text x="826" y="438" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">調整 0.015</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">粒を足して、フィルムらしくする<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">一様に足すと、暗い所が、粒でざらつく<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.5021;0.5023;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">明るさに応じて強さを変えると、暗部がきれいで、中間に粒が出る(本物のフィルムに近い)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5021;0.5023;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:film-grain-luma:end -->

## 明るさで強さを変える

<strong>真っ黒や真っ白にもグレインを足す</strong>と、<strong>黒が浮き、白が汚れます</strong>。中間調で最も強く、暗部と明部で弱めるのが自然です。

```hlsl
float3 ApplyGrainLuma(float3 color, float2 uv, float time, float intensity) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  float response = 4.0 * luma * (1.0 - luma);
  float noise = Hash(uv * resolution + time * 61.0) - 0.5;
  return color + noise * intensity * response;
}
```

明るさ依存のコードの要点です。`4 · luma · (1 − luma)` は、luma が 0.5 で最大（1）、0 と 1 で 0 になる放物線です。効果として、中間調の質感が出て、黒と白はクリーンになります。

## ノイズの質

| ノイズ | 特徴 | 見た目 |
| --- | --- | --- |
| <strong>白色ノイズ（一様乱数）</strong> | 各画素が独立 | <strong>粗く、ザラザラ（デジタル的）</strong> |
| ガウス ノイズ | 平均付近が多く、外れ値が少ない | 自然な粒状 |
| ブルー ノイズ | 高周波に偏り、低周波が少ない | 目に優しく、均一 |
| フィルム グレイン テクスチャ | 実際のフィルムをスキャンして作る | 最もリアル |

<strong>粒子の大きさを調整</strong>するには、<strong>ノイズの座標を 1 画素より粗く（2×2 画素単位など）</strong>します。

```hlsl
float2 coarse = floor(uv * resolution / grain_size) * grain_size;
float noise = Hash(coarse + time * 61.0) - 0.5;
```

`grain_size` による見た目の違いです。1 は細かく、デジタル ノイズ寄りです。2〜3 はフィルムのような粒子になります。

## 動かし方

<strong>フィルムでは、1 コマごとに別の粒子</strong>が<strong>写る</strong>ので、グレインは毎フレーム変わるのが自然です。変わらないと画面に汚れが貼りついたように見えます。

フィルムでは、1 コマごとに別の粒子が写るので、グレインは毎フレーム変わるのが自然です。変わらないと、画面に汚れが貼りついたように見えます。毎フレーム変える方法は、`time` やフレーム番号でシードを変えます。24 FPS 相当で変える方法は、映画の動きに合わせて、ゲームが 60 FPS でも、グレインは 1 秒に 24 回変えます。TAA との関係では、TAA がノイズを平均して弱めてしまうので、TAA の後に足します。

## ディザリングとの関係

<strong>8 ビット出力のグラデーション（暗い空・霧）</strong>は、<strong>量子化で縞（バンディング）</strong>が<strong>出ます</strong>。<strong>±0.5 ステップ程度の、微小なノイズを足す（ディザリング）</strong>と、<strong>縞が見えなくなります</strong>。

```hlsl
float3 Dither(float3 color, float2 pixel_position) {
  float noise = Hash(pixel_position + time * 61.0) - 0.5;
  return color + noise / 255.0;
}
```

ノイズの強さは、目的で変わります。ディザリング（バンディング隠し）は、1/255（見えない程度）です。グレイン（質感）は、0.01〜0.05（見える強さ）です。

<strong>グレインを足すとディザリングも兼ねられます</strong>（<strong>強さが十分あれば、バンディングも見えなくなる</strong>）。

## 使いどころ

| 場面 | 使い方 |
| --- | --- |
| 映画風の画作り | 控えめなグレイン |
| ホラー・古い映像 | 強め ＋ 白黒・粗い粒 |
| 暗いシーン | 暗部のバンディング隠し |
| ゲーム全体 | ほぼ不要（クリアな絵が好まれる場合も） |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| 明るさで強さを変える | 中間調のみ |
| 粒の大きさを調整 | 細かすぎないフィルムのような粒子 |
| TAA の後に足す | TAA がノイズを消さない |
| LDR（トーンマップ後）で | 見た目の明るさに対して |
| 他のパスと統合 | ビネット・色収差・トーンマップと 1 パス |
| オプションで切れる | 細部が見えづらい人のため |
| ディザリングを別に常時オン | グレインを使わなくても、バンディングを防ぐ |

## よくあるミス

??? failure "グレインが固定で、画面に汚れが貼り付いて見える"
    <strong>毎フレーム、シードを変える</strong>。

??? failure "真っ黒な所にもグレインが乗って、黒が浮く"
    <strong>明るさで強さを変える</strong>（<strong>暗部を弱める</strong>）。

??? failure "TAA で、グレインが平均されて消える"
    <strong>TAA の後</strong>に足す。

??? failure "強すぎて、細部が見えない"
    <strong>0.01〜0.03 に</strong>、<strong>オプションで調整</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] グレイン ＝ <strong>画面に、粒状のノイズを足す</strong>。<strong>フィルムの質感</strong>
    - [x] <strong>毎フレーム変え</strong>、<strong>中間調で強く、黒・白で弱く</strong>
    - [x] <strong>粒の大きさ</strong>で<strong>質感が変わる</strong>。<strong>TAA の後に足す</strong>
    - [x] <strong>ディザリング（1/255）</strong>で<strong>バンディング隠し</strong>にもなる
    - [x] <strong>控えめに設定で切れる</strong>

## 参考

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Gjøl & Svendsen, "The Rendering of INSIDE"（GDC 2016, ディザリング）
- Wikipedia, "Film grain"

## 関連ページ

- [Lens Effects](index.md)
- [Vignette](vignette.md)
- [Chromatic Aberration](chromatic-aberration.md)
- [Gamma and HDR Output](../tonemapping/gamma-srgb.md)
