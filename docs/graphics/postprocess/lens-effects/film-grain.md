---
title: Film Grain
tags:
  - 描画
---

# Film Grain

**フィルム グレイン**は、**画面に細かい粒状のノイズを加える**効果です。**フィルム写真の「粒子」の質感**を**再現**し、**映画らしい雰囲気**を**出します**。**また、グラデーション（空・暗部）の縞（バンディング）を、ノイズで目立たなくする**という**実用的な効果**も**あります**。**ノイズの質（周波数・分布）と、明るさに応じた強さの付け方**が**見た目を左右**します。このページでは、**ノイズの作り方・強さを明るさで変える方法・動かし方（毎フレーム変える）・ディザリングとの関係・使いどころ**を説明します。

!!! tip "ポイント"
    - グレイン ＝ <strong>画面に、粒状のノイズを足す</strong>。<strong>フィルムの質感</strong>。
    - <strong>ノイズは毎フレーム変える</strong>（<strong>動くノイズ ＝ フィルムの粒子が動く感じ</strong>）。
    - <strong>明るさで強さを変える</strong>：<strong>中間調が最も目立ち、真っ黒・真っ白では弱い</strong>。
    - <strong>ノイズの質</strong>：<strong>白色ノイズ（粗い）か、ブルー ノイズ／ガウス（自然）か</strong>。
    - <strong>ディザリング</strong>（<strong>バンディング隠し</strong>）にも<strong>効く</strong>（<strong>1 ビット分のノイズ</strong>で十分）。
    - <strong>かけすぎない</strong>。<strong>細部が見えなくなる</strong>。<strong>設定で切れる</strong>。

## 実際のグレイン

**フィルムの感光材料は、微小な銀の粒子**からできています。**露光された粒子の分布が、ランダムなので画像に粒状のノイズ**が**見えます**。**感度（ISO）が高いフィルムほど、粒子が大きく、ノイズが目立つ**です。

| 特徴 | 内容 |
| --- | --- |
| **粒子の大きさ** | **ISO が高いほど大きい** |
| **明るさへの依存** | **中間調で目立ち、真っ黒や真っ白では弱い** |
| **フレームごとに違う** | **1 秒間に 24 回違うノイズ → 動いて見える** |
| **色** | **カラーフィルムは色つきのノイズ。白黒は輝度のみ** |

## 基本の実装

**ランダムな値を作り、色に足します**。

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
| **`Hash`** | **座標から擬似乱数を作る関数**（**テクスチャ不要**） |
| **`seed = uv × 解像度 + time`** | **画素ごとに違い、フレームごとに違うシード** |
| **`noise − 0.5`** | **−0.5〜+0.5 の、平均 0 のノイズ** |
| **`intensity`** | <strong>強さ（0.01〜0.05）</strong> |

<!-- fig:film-grain-luma:begin -->

<svg class="fig illust motion" data-fig="film-grain-luma" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-film-grain-luma" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">フィルム グレイン:中間の明るさで最も強く、暗部と明部では弱い</text>
<rect x="60" y="70" width="360" height="150" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="150.0" y1="70" x2="150.0" y2="220" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="107.5" x2="420" y2="107.5" stroke="#e2e8f0" stroke-width="1"/>
<line x1="240.0" y1="70" x2="240.0" y2="220" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="145.0" x2="420" y2="145.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="330.0" y1="70" x2="330.0" y2="220" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="182.5" x2="420" y2="182.5" stroke="#e2e8f0" stroke-width="1"/>
<text x="420" y="240" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">画素の明るさ</text>
<text x="60" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">粒の強さ</text>
<path d="M60.0,220.0 L69.0,205.38 L78.0,191.5 L87.0,178.38 L96.0,166.0 L105.0,154.38 L114.0,143.5 L123.0,133.38 L132.0,124.0 L141.0,115.38 L150.0,107.5 L159.0,100.38 L168.0,94.0 L177.0,88.38 L186.0,83.5 L195.0,79.38 L204.0,76.0 L213.0,73.38 L222.0,71.5 L231.0,70.38 L240.0,70.0 L249.0,70.38 L258.0,71.5 L267.0,73.38 L276.0,76.0 L285.0,79.38 L294.0,83.5 L303.0,88.38 L312.0,94.0 L321.0,100.38 L330.0,107.5 L339.0,115.38 L348.0,124.0 L357.0,133.38 L366.0,143.5 L375.0,154.38 L384.0,166.0 L393.0,178.38 L402.0,191.5 L411.0,205.38 L420.0,220.0" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<circle cx="60.0" cy="220.0" r="7" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0933;0.1171;0.1409;0.1646;0.1884;0.2122;0.2359;0.2597;0.2835;0.3072;0.3310;0.3548;0.3786;0.4023;0.4261;0.4499;0.4736;0.4974;0.5212;0.5449;0.5687;0.5925;0.6162;0.6400;0.6638;0.6875;0.7113;0.7351;0.7588;0.7826;1.0000" values="60;60;72;84;96;108;120;132;144;156;168;180;192;204;216;228;240;252;264;276;288;300;312;324;336;348;360;372;384;396;408;420;420"/><animate attributeName="cy" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0933;0.1171;0.1409;0.1646;0.1884;0.2122;0.2359;0.2597;0.2835;0.3072;0.3310;0.3548;0.3786;0.4023;0.4261;0.4499;0.4736;0.4974;0.5212;0.5449;0.5687;0.5925;0.6162;0.6400;0.6638;0.6875;0.7113;0.7351;0.7588;0.7826;1.0000" values="220;220;200.67;182.67;166;150.67;136.67;124;112.67;102.67;94;86.67;80.67;76;72.67;70.67;70;70.67;72.67;76;80.67;86.67;94;102.67;112.67;124;136.67;150.67;166;182.67;200.67;220;220"/></circle>
<text x="60" y="258" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">グラデーションに、粒を重ねる（毎フレーム、粒が入れ替わる）</text>
<rect x="60" y="270" width="13" height="20" fill="#000000"/>
<rect x="73" y="270" width="13" height="20" fill="#2c2c2c"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#2c2c2c;#000000;#000000;#282828;#3b3b3b;#000000;#171717;#333333;#404040;#303030;#262626"/></rect>
<rect x="86" y="270" width="13" height="20" fill="#3d3d3d"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#3d3d3d;#585858;#000000;#525252;#2a2a2a;#0f0f0f;#000000;#2c2c2c;#505050;#191919;#424242"/></rect>
<rect x="99" y="270" width="13" height="20" fill="#494949"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#494949;#545454;#3d3d3d;#4d4d4d;#000000;#000000;#252525;#575757;#424242;#363636;#505050"/></rect>
<rect x="112" y="270" width="13" height="20" fill="#535353"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#535353;#4f4f4f;#3c3c3c;#6b6b6b;#646464;#333333;#5a5a5a;#565656;#717171;#676767;#3a3a3a"/></rect>
<rect x="125" y="270" width="13" height="20" fill="#5c5c5c"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#5c5c5c;#848484;#161616;#535353;#737373;#242424;#5b5b5b;#000000;#6c6c6c;#747474;#636363"/></rect>
<rect x="138" y="270" width="13" height="20" fill="#646464"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#646464;#868686;#4c4c4c;#777777;#6e6e6e;#6c6c6c;#5f5f5f;#848484;#8c8c8c;#616161;#757575"/></rect>
<rect x="151" y="270" width="13" height="20" fill="#6b6b6b"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#6b6b6b;#000000;#808080;#7b7b7b;#999999;#8b8b8b;#4d4d4d;#5d5d5d;#7d7d7d;#000000;#676767"/></rect>
<rect x="164" y="270" width="13" height="20" fill="#727272"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#727272;#3a3a3a;#2a2a2a;#000000;#8e8e8e;#2e2e2e;#4c4c4c;#646464;#979797;#161616;#6c6c6c"/></rect>
<rect x="177" y="270" width="13" height="20" fill="#787878"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#787878;#7e7e7e;#a0a0a0;#9a9a9a;#9e9e9e;#585858;#6d6d6d;#656565;#a0a0a0;#a6a6a6;#3b3b3b"/></rect>
<rect x="190" y="270" width="13" height="20" fill="#7e7e7e"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#7e7e7e;#474747;#545454;#545454;#7c7c7c;#898989;#5a5a5a;#000000;#737373;#6c6c6c;#868686"/></rect>
<rect x="203" y="270" width="13" height="20" fill="#848484"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#848484;#b3b3b3;#9a9a9a;#868686;#929292;#989898;#202020;#afafaf;#a3a3a3;#acacac;#a5a5a5"/></rect>
<rect x="216" y="270" width="13" height="20" fill="#898989"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#898989;#7a7a7a;#7b7b7b;#3e3e3e;#999999;#2d2d2d;#303030;#5a5a5a;#4f4f4f;#727272;#282828"/></rect>
<rect x="229" y="270" width="13" height="20" fill="#8e8e8e"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#8e8e8e;#000000;#515151;#434343;#7b7b7b;#202020;#b8b8b8;#9c9c9c;#515151;#686868;#787878"/></rect>
<rect x="242" y="270" width="13" height="20" fill="#939393"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#939393;#808080;#505050;#bababa;#c8c8c8;#8e8e8e;#919191;#444444;#4a4a4a;#7c7c7c;#6f6f6f"/></rect>
<rect x="255" y="270" width="13" height="20" fill="#989898"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#989898;#bdbdbd;#5f5f5f;#333333;#c9c9c9;#9b9b9b;#5b5b5b;#9d9d9d;#353535;#9b9b9b;#cccccc"/></rect>
<rect x="268" y="270" width="13" height="20" fill="#9c9c9c"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#9c9c9c;#c5c5c5;#b4b4b4;#787878;#898989;#656565;#bcbcbc;#a0a0a0;#bdbdbd;#848484;#717171"/></rect>
<rect x="281" y="270" width="13" height="20" fill="#a1a1a1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#a1a1a1;#c4c4c4;#d5d5d5;#c9c9c9;#c4c4c4;#c5c5c5;#bdbdbd;#767676;#a3a3a3;#8c8c8c;#454545"/></rect>
<rect x="294" y="270" width="13" height="20" fill="#a5a5a5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#a5a5a5;#4c4c4c;#858585;#818181;#bcbcbc;#d7d7d7;#9e9e9e;#d5d5d5;#dadada;#d7d7d7;#929292"/></rect>
<rect x="307" y="270" width="13" height="20" fill="#a9a9a9"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#a9a9a9;#7f7f7f;#808080;#7b7b7b;#7c7c7c;#b8b8b8;#d5d5d5;#cfcfcf;#a6a6a6;#bbbbbb;#cbcbcb"/></rect>
<rect x="320" y="270" width="13" height="20" fill="#adadad"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#adadad;#696969;#c0c0c0;#dadada;#cdcdcd;#cacaca;#aaaaaa;#7c7c7c;#cecece;#969696;#cfcfcf"/></rect>
<rect x="333" y="270" width="13" height="20" fill="#b1b1b1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#b1b1b1;#e3e3e3;#a3a3a3;#a4a4a4;#e1e1e1;#cbcbcb;#808080;#777777;#7c7c7c;#dddddd;#d3d3d3"/></rect>
<rect x="346" y="270" width="13" height="20" fill="#b5b5b5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#b5b5b5;#818181;#d8d8d8;#e7e7e7;#c7c7c7;#a1a1a1;#bababa;#7e7e7e;#656565;#e6e6e6;#c6c6c6"/></rect>
<rect x="359" y="270" width="13" height="20" fill="#b8b8b8"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#b8b8b8;#bbbbbb;#e5e5e5;#b0b0b0;#e0e0e0;#dbdbdb;#919191;#979797;#9d9d9d;#959595;#c2c2c2"/></rect>
<rect x="372" y="270" width="13" height="20" fill="#bcbcbc"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#bcbcbc;#9d9d9d;#b2b2b2;#888888;#e6e6e6;#aaaaaa;#b7b7b7;#c5c5c5;#e6e6e6;#b2b2b2;#e7e7e7"/></rect>
<rect x="385" y="270" width="13" height="20" fill="#bfbfbf"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#bfbfbf;#c0c0c0;#c3c3c3;#c2c2c2;#7a7a7a;#b8b8b8;#969696;#777777;#dedede;#949494;#bcbcbc"/></rect>
<rect x="398" y="270" width="13" height="20" fill="#c3c3c3"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#c3c3c3;#dadada;#c9c9c9;#aeaeae;#c5c5c5;#c9c9c9;#e0e0e0;#8f8f8f;#c9c9c9;#a4a4a4;#a8a8a8"/></rect>
<rect x="411" y="270" width="13" height="20" fill="#c6c6c6"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#c6c6c6;#e1e1e1;#c7c7c7;#cdcdcd;#e0e0e0;#eeeeee;#c0c0c0;#d2d2d2;#c7c7c7;#c8c8c8;#dadada"/></rect>
<rect x="424" y="270" width="13" height="20" fill="#cacaca"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#cacaca;#c4c4c4;#cdcdcd;#c7c7c7;#f2f2f2;#dddddd;#ededed;#f2f2f2;#aeaeae;#d0d0d0;#f2f2f2"/></rect>
<rect x="437" y="270" width="13" height="20" fill="#cdcdcd"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#cdcdcd;#ececec;#a4a4a4;#a2a2a2;#c7c7c7;#9b9b9b;#b1b1b1;#9b9b9b;#dddddd;#e7e7e7;#f1f1f1"/></rect>
<rect x="450" y="270" width="13" height="20" fill="#d0d0d0"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d0d0d0;#ababab;#e4e4e4;#dfdfdf;#aaaaaa;#f1f1f1;#f8f8f8;#b3b3b3;#f7f7f7;#c6c6c6;#cfcfcf"/></rect>
<rect x="463" y="270" width="13" height="20" fill="#d3d3d3"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d3d3d3;#fbfbfb;#efefef;#b1b1b1;#cdcdcd;#d4d4d4;#c4c4c4;#b5b5b5;#c2c2c2;#e6e6e6;#a0a0a0"/></rect>
<rect x="476" y="270" width="13" height="20" fill="#d6d6d6"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d6d6d6;#dbdbdb;#d1d1d1;#a6a6a6;#c7c7c7;#e1e1e1;#d7d7d7;#ababab;#fcfcfc;#eeeeee;#fbfbfb"/></rect>
<rect x="489" y="270" width="13" height="20" fill="#d9d9d9"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d9d9d9;#b5b5b5;#c5c5c5;#aeaeae;#efefef;#c5c5c5;#b8b8b8;#d3d3d3;#f8f8f8;#f2f2f2;#c4c4c4"/></rect>
<rect x="502" y="270" width="13" height="20" fill="#dcdcdc"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#dcdcdc;#bfbfbf;#fafafa;#e1e1e1;#ebebeb;#b9b9b9;#b6b6b6;#eaeaea;#d6d6d6;#b7b7b7;#fbfbfb"/></rect>
<rect x="515" y="270" width="13" height="20" fill="#dfdfdf"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#dfdfdf;#e9e9e9;#f4f4f4;#bebebe;#f7f7f7;#bcbcbc;#f8f8f8;#dcdcdc;#d3d3d3;#e3e3e3;#fcfcfc"/></rect>
<rect x="528" y="270" width="13" height="20" fill="#e2e2e2"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#e2e2e2;#d2d2d2;#c7c7c7;#e4e4e4;#cfcfcf;#c5c5c5;#cacaca;#c1c1c1;#cdcdcd;#d5d5d5;#d4d4d4"/></rect>
<rect x="541" y="270" width="13" height="20" fill="#e5e5e5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#e5e5e5;#f4f4f4;#d7d7d7;#e5e5e5;#d0d0d0;#dbdbdb;#c4c4c4;#d5d5d5;#c4c4c4;#f3f3f3;#e8e8e8"/></rect>
<rect x="554" y="270" width="13" height="20" fill="#e8e8e8"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#e8e8e8;#d5d5d5;#e6e6e6;#ffffff;#d0d0d0;#f9f9f9;#e4e4e4;#e7e7e7;#fafafa;#e1e1e1;#e8e8e8"/></rect>
<rect x="567" y="270" width="13" height="20" fill="#eaeaea"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#eaeaea;#f4f4f4;#ffffff;#e2e2e2;#fafafa;#f4f4f4;#f1f1f1;#e5e5e5;#e2e2e2;#d2d2d2;#d6d6d6"/></rect>
<rect x="580" y="270" width="13" height="20" fill="#ededed"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#ededed;#d9d9d9;#f8f8f8;#e2e2e2;#dddddd;#d9d9d9;#fcfcfc;#fdfdfd;#f4f4f4;#e3e3e3;#e1e1e1"/></rect>
<rect x="593" y="270" width="13" height="20" fill="#f0f0f0"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f0f0f0;#e7e7e7;#eeeeee;#e2e2e2;#eeeeee;#e6e6e6;#ffffff;#ffffff;#f1f1f1;#e5e5e5;#ffffff"/></rect>
<rect x="606" y="270" width="13" height="20" fill="#f2f2f2"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f2f2f2;#ececec;#eeeeee;#e1e1e1;#eeeeee;#f1f1f1;#f2f2f2;#e8e8e8;#f2f2f2;#e1e1e1;#eaeaea"/></rect>
<rect x="619" y="270" width="13" height="20" fill="#f5f5f5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f5f5f5;#eaeaea;#f2f2f2;#e8e8e8;#e8e8e8;#f0f0f0;#eeeeee;#f7f7f7;#f6f6f6;#fbfbfb;#f9f9f9"/></rect>
<rect x="632" y="270" width="13" height="20" fill="#f7f7f7"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f7f7f7;#fcfcfc;#ffffff;#f5f5f5;#f4f4f4;#ffffff;#f0f0f0;#fcfcfc;#fafafa;#eeeeee;#fefefe"/></rect>
<rect x="645" y="270" width="13" height="20" fill="#fafafa"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#fafafa;#ffffff;#fcfcfc;#fdfdfd;#fefefe;#f5f5f5;#fafafa;#fafafa;#fefefe;#fefefe;#fefefe"/></rect>
<rect x="658" y="270" width="13" height="20" fill="#fdfdfd"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#fdfdfd;#fdfdfd;#ffffff;#fefefe;#fefefe;#fbfbfb;#f9f9f9;#fafafa;#fcfcfc;#fafafa;#ffffff"/></rect>
<rect x="671" y="270" width="13" height="20" fill="#ffffff"/>
<rect x="60" y="290" width="13" height="20" fill="#000000"/>
<rect x="73" y="290" width="13" height="20" fill="#2c2c2c"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#2c2c2c;#2c2c2c;#252525;#2b2b2b;#353535;#393939;#323232;#333333;#000000;#0a0a0a;#1b1b1b"/></rect>
<rect x="86" y="290" width="13" height="20" fill="#3d3d3d"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#3d3d3d;#4c4c4c;#2b2b2b;#424242;#000000;#000000;#272727;#484848;#494949;#484848;#2a2a2a"/></rect>
<rect x="99" y="290" width="13" height="20" fill="#494949"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#494949;#4a4a4a;#464646;#464646;#000000;#656565;#242424;#6a6a6a;#676767;#000000;#454545"/></rect>
<rect x="112" y="290" width="13" height="20" fill="#535353"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#535353;#6d6d6d;#777777;#4e4e4e;#373737;#2d2d2d;#767676;#2d2d2d;#5b5b5b;#1b1b1b;#565656"/></rect>
<rect x="125" y="290" width="13" height="20" fill="#5c5c5c"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#5c5c5c;#828282;#1d1d1d;#787878;#5d5d5d;#7d7d7d;#6f6f6f;#373737;#7e7e7e;#5b5b5b;#000000"/></rect>
<rect x="138" y="290" width="13" height="20" fill="#646464"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#646464;#000000;#636363;#5e5e5e;#4a4a4a;#272727;#505050;#4c4c4c;#848484;#000000;#7c7c7c"/></rect>
<rect x="151" y="290" width="13" height="20" fill="#6b6b6b"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#6b6b6b;#8c8c8c;#252525;#949494;#818181;#929292;#4e4e4e;#5b5b5b;#5e5e5e;#999999;#757575"/></rect>
<rect x="164" y="290" width="13" height="20" fill="#727272"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#727272;#5f5f5f;#696969;#515151;#000000;#232323;#949494;#535353;#9d9d9d;#4d4d4d;#505050"/></rect>
<rect x="177" y="290" width="13" height="20" fill="#787878"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#787878;#7a7a7a;#454545;#676767;#a6a6a6;#a0a0a0;#999999;#878787;#a2a2a2;#a5a5a5;#7e7e7e"/></rect>
<rect x="190" y="290" width="13" height="20" fill="#7e7e7e"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#7e7e7e;#979797;#0d0d0d;#989898;#787878;#9a9a9a;#8f8f8f;#5e5e5e;#0c0c0c;#ababab;#3a3a3a"/></rect>
<rect x="203" y="290" width="13" height="20" fill="#848484"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#848484;#808080;#6d6d6d;#666666;#9f9f9f;#b5b5b5;#5f5f5f;#969696;#666666;#8b8b8b;#757575"/></rect>
<rect x="216" y="290" width="13" height="20" fill="#898989"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#898989;#505050;#4f4f4f;#595959;#b5b5b5;#898989;#5c5c5c;#b5b5b5;#bdbdbd;#828282;#494949"/></rect>
<rect x="229" y="290" width="13" height="20" fill="#8e8e8e"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#8e8e8e;#5b5b5b;#404040;#777777;#404040;#656565;#696969;#979797;#b9b9b9;#ababab;#828282"/></rect>
<rect x="242" y="290" width="13" height="20" fill="#939393"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#939393;#878787;#969696;#828282;#7c7c7c;#3c3c3c;#717171;#c6c6c6;#505050;#939393;#a3a3a3"/></rect>
<rect x="255" y="290" width="13" height="20" fill="#989898"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#989898;#c1c1c1;#6a6a6a;#757575;#717171;#8a8a8a;#909090;#c9c9c9;#bfbfbf;#c2c2c2;#323232"/></rect>
<rect x="268" y="290" width="13" height="20" fill="#9c9c9c"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#9c9c9c;#3f3f3f;#b5b5b5;#c8c8c8;#999999;#a7a7a7;#313131;#8d8d8d;#cccccc;#c2c2c2;#c5c5c5"/></rect>
<rect x="281" y="290" width="13" height="20" fill="#a1a1a1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#a1a1a1;#d4d4d4;#7a7a7a;#5d5d5d;#686868;#a4a4a4;#b7b7b7;#d1d1d1;#bbbbbb;#b3b3b3;#c0c0c0"/></rect>
<rect x="294" y="290" width="13" height="20" fill="#a5a5a5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#a5a5a5;#9f9f9f;#ababab;#505050;#c5c5c5;#7c7c7c;#d3d3d3;#b7b7b7;#898989;#676767;#808080"/></rect>
<rect x="307" y="290" width="13" height="20" fill="#a9a9a9"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#a9a9a9;#b9b9b9;#c0c0c0;#696969;#5f5f5f;#acacac;#b3b3b3;#9a9a9a;#808080;#b5b5b5;#4e4e4e"/></rect>
<rect x="320" y="290" width="13" height="20" fill="#adadad"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#adadad;#919191;#a8a8a8;#dedede;#bebebe;#d7d7d7;#aaaaaa;#868686;#888888;#dedede;#c5c5c5"/></rect>
<rect x="333" y="290" width="13" height="20" fill="#b1b1b1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#b1b1b1;#979797;#606060;#b1b1b1;#c5c5c5;#a6a6a6;#8f8f8f;#c4c4c4;#dfdfdf;#8a8a8a;#636363"/></rect>
<rect x="346" y="290" width="13" height="20" fill="#b5b5b5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#b5b5b5;#9f9f9f;#ababab;#c9c9c9;#8a8a8a;#d5d5d5;#cfcfcf;#b5b5b5;#8b8b8b;#e6e6e6;#9b9b9b"/></rect>
<rect x="359" y="290" width="13" height="20" fill="#b8b8b8"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#b8b8b8;#dbdbdb;#949494;#929292;#d5d5d5;#9d9d9d;#e7e7e7;#b8b8b8;#8d8d8d;#939393;#aeaeae"/></rect>
<rect x="372" y="290" width="13" height="20" fill="#bcbcbc"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#bcbcbc;#cecece;#eaeaea;#8b8b8b;#afafaf;#969696;#ececec;#8a8a8a;#7a7a7a;#7b7b7b;#afafaf"/></rect>
<rect x="385" y="290" width="13" height="20" fill="#bfbfbf"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#bfbfbf;#e8e8e8;#e6e6e6;#d8d8d8;#f0f0f0;#ebebeb;#ababab;#969696;#ebebeb;#d9d9d9;#7c7c7c"/></rect>
<rect x="398" y="290" width="13" height="20" fill="#c3c3c3"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#c3c3c3;#d4d4d4;#b5b5b5;#b4b4b4;#afafaf;#999999;#7d7d7d;#a8a8a8;#b1b1b1;#efefef;#929292"/></rect>
<rect x="411" y="290" width="13" height="20" fill="#c6c6c6"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#c6c6c6;#f2f2f2;#a3a3a3;#b6b6b6;#e6e6e6;#e6e6e6;#bfbfbf;#8c8c8c;#c3c3c3;#b8b8b8;#eeeeee"/></rect>
<rect x="424" y="290" width="13" height="20" fill="#cacaca"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#cacaca;#a6a6a6;#bbbbbb;#efefef;#8f8f8f;#c0c0c0;#e7e7e7;#e3e3e3;#909090;#8f8f8f;#949494"/></rect>
<rect x="437" y="290" width="13" height="20" fill="#cdcdcd"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#cdcdcd;#f2f2f2;#b2b2b2;#e4e4e4;#f1f1f1;#bcbcbc;#b4b4b4;#f5f5f5;#d8d8d8;#b3b3b3;#e1e1e1"/></rect>
<rect x="450" y="290" width="13" height="20" fill="#d0d0d0"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d0d0d0;#bdbdbd;#b9b9b9;#979797;#e7e7e7;#f4f4f4;#dcdcdc;#f6f6f6;#9a9a9a;#b4b4b4;#cecece"/></rect>
<rect x="463" y="290" width="13" height="20" fill="#d3d3d3"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d3d3d3;#f9f9f9;#f9f9f9;#c8c8c8;#bbbbbb;#cdcdcd;#d2d2d2;#f7f7f7;#b3b3b3;#ededed;#e8e8e8"/></rect>
<rect x="476" y="290" width="13" height="20" fill="#d6d6d6"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d6d6d6;#f0f0f0;#ececec;#dfdfdf;#c6c6c6;#c6c6c6;#cacaca;#ededed;#adadad;#bababa;#ebebeb"/></rect>
<rect x="489" y="290" width="13" height="20" fill="#d9d9d9"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d9d9d9;#c3c3c3;#b1b1b1;#aeaeae;#dddddd;#cacaca;#fdfdfd;#f6f6f6;#fefefe;#c5c5c5;#b3b3b3"/></rect>
<rect x="502" y="290" width="13" height="20" fill="#dcdcdc"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#dcdcdc;#bababa;#dcdcdc;#ececec;#d8d8d8;#c6c6c6;#d6d6d6;#e5e5e5;#e9e9e9;#eeeeee;#f5f5f5"/></rect>
<rect x="515" y="290" width="13" height="20" fill="#dfdfdf"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#dfdfdf;#ebebeb;#c1c1c1;#f6f6f6;#cfcfcf;#e4e4e4;#d6d6d6;#f0f0f0;#c8c8c8;#cccccc;#cccccc"/></rect>
<rect x="528" y="290" width="13" height="20" fill="#e2e2e2"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#e2e2e2;#c9c9c9;#fafafa;#e7e7e7;#d6d6d6;#dbdbdb;#ffffff;#e2e2e2;#cfcfcf;#f6f6f6;#ececec"/></rect>
<rect x="541" y="290" width="13" height="20" fill="#e5e5e5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#e5e5e5;#ffffff;#cacaca;#e3e3e3;#f8f8f8;#f9f9f9;#fdfdfd;#c6c6c6;#d7d7d7;#cbcbcb;#d0d0d0"/></rect>
<rect x="554" y="290" width="13" height="20" fill="#e8e8e8"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#e8e8e8;#ffffff;#ececec;#fefefe;#e0e0e0;#fbfbfb;#e5e5e5;#d9d9d9;#f7f7f7;#ffffff;#d0d0d0"/></rect>
<rect x="567" y="290" width="13" height="20" fill="#eaeaea"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#eaeaea;#efefef;#f0f0f0;#dbdbdb;#e3e3e3;#d7d7d7;#dbdbdb;#dddddd;#efefef;#f2f2f2;#dbdbdb"/></rect>
<rect x="580" y="290" width="13" height="20" fill="#ededed"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#ededed;#d6d6d6;#e5e5e5;#f5f5f5;#dedede;#e4e4e4;#dfdfdf;#fafafa;#efefef;#d8d8d8;#dadada"/></rect>
<rect x="593" y="290" width="13" height="20" fill="#f0f0f0"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f0f0f0;#ececec;#f2f2f2;#f5f5f5;#dfdfdf;#e2e2e2;#f7f7f7;#ececec;#e7e7e7;#e8e8e8;#ffffff"/></rect>
<rect x="606" y="290" width="13" height="20" fill="#f2f2f2"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f2f2f2;#ececec;#f4f4f4;#eeeeee;#f0f0f0;#fefefe;#ffffff;#eeeeee;#e8e8e8;#fafafa;#e8e8e8"/></rect>
<rect x="619" y="290" width="13" height="20" fill="#f5f5f5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f5f5f5;#e7e7e7;#ffffff;#f3f3f3;#fdfdfd;#f2f2f2;#ffffff;#f4f4f4;#ececec;#e8e8e8;#f6f6f6"/></rect>
<rect x="632" y="290" width="13" height="20" fill="#f7f7f7"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f7f7f7;#fafafa;#ffffff;#efefef;#fafafa;#f5f5f5;#f8f8f8;#f0f0f0;#f3f3f3;#f8f8f8;#ffffff"/></rect>
<rect x="645" y="290" width="13" height="20" fill="#fafafa"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#fafafa;#f5f5f5;#fafafa;#fefefe;#ffffff;#f6f6f6;#f5f5f5;#ffffff;#ffffff;#fafafa;#f4f4f4"/></rect>
<rect x="658" y="290" width="13" height="20" fill="#fdfdfd"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#fdfdfd;#ffffff;#fcfcfc;#ffffff;#fdfdfd;#ffffff;#fafafa;#fefefe;#fbfbfb;#fcfcfc;#ffffff"/></rect>
<rect x="671" y="290" width="13" height="20" fill="#ffffff"/>
<rect x="60" y="310" width="13" height="20" fill="#000000"/>
<rect x="73" y="310" width="13" height="20" fill="#2c2c2c"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#2c2c2c;#282828;#313131;#282828;#343434;#292929;#292929;#000000;#323232;#2c2c2c;#191919"/></rect>
<rect x="86" y="310" width="13" height="20" fill="#3d3d3d"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#3d3d3d;#4d4d4d;#4e4e4e;#3a3a3a;#191919;#3b3b3b;#000000;#050505;#373737;#000000;#383838"/></rect>
<rect x="99" y="310" width="13" height="20" fill="#494949"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#494949;#4a4a4a;#000000;#545454;#000000;#5b5b5b;#5e5e5e;#4a4a4a;#000000;#494949;#3d3d3d"/></rect>
<rect x="112" y="310" width="13" height="20" fill="#535353"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#535353;#767676;#191919;#707070;#797979;#676767;#6d6d6d;#292929;#787878;#525252;#767676"/></rect>
<rect x="125" y="310" width="13" height="20" fill="#5c5c5c"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#5c5c5c;#7f7f7f;#282828;#767676;#808080;#000000;#4a4a4a;#737373;#262626;#7e7e7e;#3f3f3f"/></rect>
<rect x="138" y="310" width="13" height="20" fill="#646464"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#646464;#828282;#272727;#646464;#8a8a8a;#393939;#444444;#656565;#4d4d4d;#000000;#333333"/></rect>
<rect x="151" y="310" width="13" height="20" fill="#6b6b6b"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#6b6b6b;#333333;#949494;#7e7e7e;#919191;#353535;#888888;#232323;#6f6f6f;#7a7a7a;#595959"/></rect>
<rect x="164" y="310" width="13" height="20" fill="#727272"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#727272;#979797;#787878;#7b7b7b;#989898;#242424;#a1a1a1;#818181;#646464;#919191;#505050"/></rect>
<rect x="177" y="310" width="13" height="20" fill="#787878"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#787878;#a9a9a9;#818181;#656565;#959595;#717171;#424242;#939393;#000000;#9a9a9a;#535353"/></rect>
<rect x="190" y="310" width="13" height="20" fill="#7e7e7e"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#7e7e7e;#8f8f8f;#b0b0b0;#898989;#919191;#636363;#000000;#000000;#404040;#8c8c8c;#757575"/></rect>
<rect x="203" y="310" width="13" height="20" fill="#848484"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#848484;#858585;#aeaeae;#414141;#585858;#969696;#000000;#000000;#6f6f6f;#393939;#707070"/></rect>
<rect x="216" y="310" width="13" height="20" fill="#898989"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#898989;#5d5d5d;#939393;#949494;#595959;#989898;#868686;#474747;#b8b8b8;#616161;#4b4b4b"/></rect>
<rect x="229" y="310" width="13" height="20" fill="#8e8e8e"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#8e8e8e;#414141;#9f9f9f;#b7b7b7;#afafaf;#818181;#6a6a6a;#121212;#a0a0a0;#969696;#797979"/></rect>
<rect x="242" y="310" width="13" height="20" fill="#939393"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#939393;#a5a5a5;#8b8b8b;#c3c3c3;#afafaf;#6c6c6c;#c0c0c0;#343434;#979797;#868686;#6a6a6a"/></rect>
<rect x="255" y="310" width="13" height="20" fill="#989898"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#989898;#424242;#b8b8b8;#2d2d2d;#9e9e9e;#c8c8c8;#5a5a5a;#676767;#a5a5a5;#999999;#a9a9a9"/></rect>
<rect x="268" y="310" width="13" height="20" fill="#9c9c9c"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#9c9c9c;#c0c0c0;#676767;#808080;#7f7f7f;#454545;#c8c8c8;#bdbdbd;#b6b6b6;#343434;#c3c3c3"/></rect>
<rect x="281" y="310" width="13" height="20" fill="#a1a1a1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#a1a1a1;#bdbdbd;#9c9c9c;#bdbdbd;#9a9a9a;#767676;#5c5c5c;#777777;#494949;#898989;#bebebe"/></rect>
<rect x="294" y="310" width="13" height="20" fill="#a5a5a5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#a5a5a5;#bcbcbc;#cccccc;#bebebe;#828282;#acacac;#9c9c9c;#c6c6c6;#a8a8a8;#828282;#b6b6b6"/></rect>
<rect x="307" y="310" width="13" height="20" fill="#a9a9a9"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#a9a9a9;#dbdbdb;#7e7e7e;#d3d3d3;#505050;#868686;#828282;#c5c5c5;#d9d9d9;#c6c6c6;#919191"/></rect>
<rect x="320" y="310" width="13" height="20" fill="#adadad"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#adadad;#d7d7d7;#959595;#878787;#d9d9d9;#bdbdbd;#c4c4c4;#c0c0c0;#e0e0e0;#a9a9a9;#d3d3d3"/></rect>
<rect x="333" y="310" width="13" height="20" fill="#b1b1b1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#b1b1b1;#c8c8c8;#d8d8d8;#a9a9a9;#cbcbcb;#b9b9b9;#979797;#878787;#bfbfbf;#6d6d6d;#dddddd"/></rect>
<rect x="346" y="310" width="13" height="20" fill="#b5b5b5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#b5b5b5;#808080;#686868;#797979;#e2e2e2;#a0a0a0;#808080;#686868;#6b6b6b;#cbcbcb;#c4c4c4"/></rect>
<rect x="359" y="310" width="13" height="20" fill="#b8b8b8"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#b8b8b8;#cecece;#d2d2d2;#777777;#c3c3c3;#a7a7a7;#dadada;#dbdbdb;#e2e2e2;#777777;#dfdfdf"/></rect>
<rect x="372" y="310" width="13" height="20" fill="#bcbcbc"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#bcbcbc;#e6e6e6;#e9e9e9;#848484;#959595;#858585;#767676;#e0e0e0;#dddddd;#cbcbcb;#dedede"/></rect>
<rect x="385" y="310" width="13" height="20" fill="#bfbfbf"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#bfbfbf;#cecece;#a5a5a5;#898989;#888888;#dadada;#999999;#a9a9a9;#b6b6b6;#7a7a7a;#a1a1a1"/></rect>
<rect x="398" y="310" width="13" height="20" fill="#c3c3c3"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#c3c3c3;#a9a9a9;#d9d9d9;#b3b3b3;#aeaeae;#f0f0f0;#c3c3c3;#e6e6e6;#cfcfcf;#828282;#b9b9b9"/></rect>
<rect x="411" y="310" width="13" height="20" fill="#c6c6c6"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#c6c6c6;#bfbfbf;#e1e1e1;#b5b5b5;#dbdbdb;#cacaca;#a4a4a4;#e9e9e9;#929292;#e6e6e6;#9e9e9e"/></rect>
<rect x="424" y="310" width="13" height="20" fill="#cacaca"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#cacaca;#8a8a8a;#a7a7a7;#e3e3e3;#f5f5f5;#8b8b8b;#c9c9c9;#c9c9c9;#e6e6e6;#a5a5a5;#c9c9c9"/></rect>
<rect x="437" y="310" width="13" height="20" fill="#cdcdcd"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#cdcdcd;#bdbdbd;#ebebeb;#b3b3b3;#f4f4f4;#b6b6b6;#adadad;#e0e0e0;#cdcdcd;#a0a0a0;#dadada"/></rect>
<rect x="450" y="310" width="13" height="20" fill="#d0d0d0"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d0d0d0;#a2a2a2;#eaeaea;#e2e2e2;#e9e9e9;#dcdcdc;#c2c2c2;#c6c6c6;#c6c6c6;#f2f2f2;#a2a2a2"/></rect>
<rect x="463" y="310" width="13" height="20" fill="#d3d3d3"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d3d3d3;#f4f4f4;#a0a0a0;#b6b6b6;#bcbcbc;#f5f5f5;#d3d3d3;#c8c8c8;#f3f3f3;#b9b9b9;#cfcfcf"/></rect>
<rect x="476" y="310" width="13" height="20" fill="#d6d6d6"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d6d6d6;#d9d9d9;#ebebeb;#ebebeb;#e2e2e2;#c8c8c8;#c6c6c6;#b5b5b5;#f2f2f2;#e4e4e4;#eaeaea"/></rect>
<rect x="489" y="310" width="13" height="20" fill="#d9d9d9"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d9d9d9;#bcbcbc;#d4d4d4;#eeeeee;#e0e0e0;#b7b7b7;#d6d6d6;#f6f6f6;#c2c2c2;#bebebe;#c8c8c8"/></rect>
<rect x="502" y="310" width="13" height="20" fill="#dcdcdc"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#dcdcdc;#ebebeb;#f5f5f5;#bfbfbf;#bfbfbf;#c7c7c7;#cecece;#dedede;#c0c0c0;#cecece;#c2c2c2"/></rect>
<rect x="515" y="310" width="13" height="20" fill="#dfdfdf"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#dfdfdf;#ffffff;#efefef;#c0c0c0;#fefefe;#c0c0c0;#d6d6d6;#ffffff;#f3f3f3;#efefef;#dadada"/></rect>
<rect x="528" y="310" width="13" height="20" fill="#e2e2e2"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#e2e2e2;#cccccc;#ebebeb;#c5c5c5;#cdcdcd;#dadada;#bfbfbf;#dbdbdb;#f5f5f5;#eeeeee;#e2e2e2"/></rect>
<rect x="541" y="310" width="13" height="20" fill="#e5e5e5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#e5e5e5;#ededed;#e2e2e2;#cdcdcd;#ebebeb;#dfdfdf;#f3f3f3;#fdfdfd;#e0e0e0;#e9e9e9;#f4f4f4"/></rect>
<rect x="554" y="310" width="13" height="20" fill="#e8e8e8"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#e8e8e8;#e3e3e3;#d8d8d8;#f4f4f4;#fcfcfc;#f6f6f6;#f2f2f2;#fafafa;#f1f1f1;#efefef;#e5e5e5"/></rect>
<rect x="567" y="310" width="13" height="20" fill="#eaeaea"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#eaeaea;#e1e1e1;#f1f1f1;#d5d5d5;#e6e6e6;#f8f8f8;#f5f5f5;#f1f1f1;#dddddd;#e6e6e6;#e8e8e8"/></rect>
<rect x="580" y="310" width="13" height="20" fill="#ededed"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#ededed;#f2f2f2;#e9e9e9;#f5f5f5;#ffffff;#dedede;#f4f4f4;#f9f9f9;#e8e8e8;#ededed;#ffffff"/></rect>
<rect x="593" y="310" width="13" height="20" fill="#f0f0f0"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f0f0f0;#dddddd;#f1f1f1;#e2e2e2;#fafafa;#ffffff;#f0f0f0;#dfdfdf;#f3f3f3;#f1f1f1;#f8f8f8"/></rect>
<rect x="606" y="310" width="13" height="20" fill="#f2f2f2"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f2f2f2;#f3f3f3;#f7f7f7;#fdfdfd;#f3f3f3;#efefef;#ffffff;#e9e9e9;#f8f8f8;#efefef;#fbfbfb"/></rect>
<rect x="619" y="310" width="13" height="20" fill="#f5f5f5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f5f5f5;#ebebeb;#ffffff;#f1f1f1;#e9e9e9;#efefef;#f2f2f2;#e8e8e8;#f3f3f3;#f3f3f3;#fafafa"/></rect>
<rect x="632" y="310" width="13" height="20" fill="#f7f7f7"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f7f7f7;#f4f4f4;#f3f3f3;#f2f2f2;#fcfcfc;#ffffff;#f8f8f8;#f2f2f2;#fdfdfd;#f5f5f5;#f2f2f2"/></rect>
<rect x="645" y="310" width="13" height="20" fill="#fafafa"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#fafafa;#f5f5f5;#fefefe;#fefefe;#fcfcfc;#fafafa;#fbfbfb;#f6f6f6;#ffffff;#f8f8f8;#fcfcfc"/></rect>
<rect x="658" y="310" width="13" height="20" fill="#fdfdfd"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#fdfdfd;#ffffff;#ffffff;#fcfcfc;#fbfbfb;#fdfdfd;#fafafa;#ffffff;#fcfcfc;#ffffff;#fbfbfb"/></rect>
<rect x="671" y="310" width="13" height="20" fill="#ffffff"/>
<rect x="60" y="330" width="13" height="20" fill="#000000"/>
<rect x="73" y="330" width="13" height="20" fill="#2c2c2c"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#2c2c2c;#060606;#3b3b3b;#333333;#000000;#000000;#404040;#343434;#1a1a1a;#000000;#080808"/></rect>
<rect x="86" y="330" width="13" height="20" fill="#3d3d3d"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#3d3d3d;#222222;#4e4e4e;#303030;#121212;#555555;#4f4f4f;#161616;#545454;#444444;#4e4e4e"/></rect>
<rect x="99" y="330" width="13" height="20" fill="#494949"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#494949;#565656;#656565;#5e5e5e;#616161;#242424;#585858;#4c4c4c;#5b5b5b;#434343;#646464"/></rect>
<rect x="112" y="330" width="13" height="20" fill="#535353"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#535353;#585858;#373737;#323232;#1a1a1a;#535353;#000000;#505050;#1c1c1c;#525252;#535353"/></rect>
<rect x="125" y="330" width="13" height="20" fill="#5c5c5c"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#5c5c5c;#606060;#7c7c7c;#000000;#7a7a7a;#595959;#626262;#6c6c6c;#7a7a7a;#4e4e4e;#535353"/></rect>
<rect x="138" y="330" width="13" height="20" fill="#646464"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#646464;#8d8d8d;#000000;#727272;#727272;#000000;#6f6f6f;#767676;#8b8b8b;#4e4e4e;#8e8e8e"/></rect>
<rect x="151" y="330" width="13" height="20" fill="#6b6b6b"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#6b6b6b;#6d6d6d;#6a6a6a;#919191;#000000;#828282;#797979;#565656;#8e8e8e;#5a5a5a;#686868"/></rect>
<rect x="164" y="330" width="13" height="20" fill="#727272"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#727272;#757575;#8e8e8e;#454545;#6a6a6a;#686868;#787878;#939393;#555555;#939393;#666666"/></rect>
<rect x="177" y="330" width="13" height="20" fill="#787878"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#787878;#797979;#565656;#797979;#a8a8a8;#8a8a8a;#979797;#616161;#5e5e5e;#5b5b5b;#828282"/></rect>
<rect x="190" y="330" width="13" height="20" fill="#7e7e7e"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#7e7e7e;#8e8e8e;#9d9d9d;#000000;#979797;#a7a7a7;#848484;#0e0e0e;#616161;#000000;#4b4b4b"/></rect>
<rect x="203" y="330" width="13" height="20" fill="#848484"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#848484;#b1b1b1;#919191;#969696;#a4a4a4;#b0b0b0;#919191;#929292;#939393;#9b9b9b;#909090"/></rect>
<rect x="216" y="330" width="13" height="20" fill="#898989"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#898989;#9f9f9f;#5a5a5a;#9d9d9d;#838383;#a7a7a7;#3d3d3d;#535353;#1e1e1e;#a8a8a8;#b6b6b6"/></rect>
<rect x="229" y="330" width="13" height="20" fill="#8e8e8e"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#8e8e8e;#a1a1a1;#7c7c7c;#b3b3b3;#afafaf;#969696;#696969;#717171;#838383;#737373;#858585"/></rect>
<rect x="242" y="330" width="13" height="20" fill="#939393"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#939393;#a4a4a4;#c3c3c3;#393939;#9c9c9c;#323232;#4e4e4e;#b7b7b7;#9d9d9d;#c1c1c1;#8c8c8c"/></rect>
<rect x="255" y="330" width="13" height="20" fill="#989898"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#989898;#2e2e2e;#888888;#a3a3a3;#c8c8c8;#cccccc;#949494;#8c8c8c;#505050;#a9a9a9;#6a6a6a"/></rect>
<rect x="268" y="330" width="13" height="20" fill="#9c9c9c"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#9c9c9c;#626262;#383838;#333333;#b2b2b2;#5b5b5b;#cfcfcf;#525252;#c6c6c6;#5c5c5c;#393939"/></rect>
<rect x="281" y="330" width="13" height="20" fill="#a1a1a1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#a1a1a1;#bbbbbb;#797979;#bcbcbc;#6f6f6f;#4d4d4d;#c1c1c1;#bababa;#c9c9c9;#bcbcbc;#575757"/></rect>
<rect x="294" y="330" width="13" height="20" fill="#a5a5a5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#a5a5a5;#b5b5b5;#bebebe;#a0a0a0;#d4d4d4;#808080;#d7d7d7;#bfbfbf;#474747;#484848;#b7b7b7"/></rect>
<rect x="307" y="330" width="13" height="20" fill="#a9a9a9"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#a9a9a9;#cdcdcd;#626262;#8e8e8e;#c4c4c4;#757575;#d1d1d1;#a7a7a7;#5c5c5c;#979797;#b2b2b2"/></rect>
<rect x="320" y="330" width="13" height="20" fill="#adadad"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#adadad;#a5a5a5;#c2c2c2;#767676;#cfcfcf;#9a9a9a;#bebebe;#bcbcbc;#a2a2a2;#9e9e9e;#cdcdcd"/></rect>
<rect x="333" y="330" width="13" height="20" fill="#b1b1b1"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#b1b1b1;#e0e0e0;#d1d1d1;#b9b9b9;#949494;#696969;#e3e3e3;#c8c8c8;#d5d5d5;#9a9a9a;#bdbdbd"/></rect>
<rect x="346" y="330" width="13" height="20" fill="#b5b5b5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#b5b5b5;#e7e7e7;#d9d9d9;#c0c0c0;#9b9b9b;#acacac;#dedede;#a5a5a5;#cacaca;#c1c1c1;#dfdfdf"/></rect>
<rect x="359" y="330" width="13" height="20" fill="#b8b8b8"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#b8b8b8;#d9d9d9;#9c9c9c;#696969;#999999;#afafaf;#c2c2c2;#dadada;#e1e1e1;#727272;#dcdcdc"/></rect>
<rect x="372" y="330" width="13" height="20" fill="#bcbcbc"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#bcbcbc;#dddddd;#e2e2e2;#c4c4c4;#9f9f9f;#e1e1e1;#dcdcdc;#d0d0d0;#e6e6e6;#a9a9a9;#808080"/></rect>
<rect x="385" y="330" width="13" height="20" fill="#bfbfbf"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#bfbfbf;#c5c5c5;#dedede;#999999;#dadada;#ebebeb;#9e9e9e;#cbcbcb;#d2d2d2;#bbbbbb;#999999"/></rect>
<rect x="398" y="330" width="13" height="20" fill="#c3c3c3"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#c3c3c3;#a5a5a5;#dddddd;#e0e0e0;#bebebe;#8c8c8c;#e2e2e2;#dfdfdf;#a2a2a2;#cbcbcb;#eaeaea"/></rect>
<rect x="411" y="330" width="13" height="20" fill="#c6c6c6"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#c6c6c6;#ebebeb;#c9c9c9;#c4c4c4;#d0d0d0;#a1a1a1;#a1a1a1;#9f9f9f;#dbdbdb;#b7b7b7;#cdcdcd"/></rect>
<rect x="424" y="330" width="13" height="20" fill="#cacaca"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#cacaca;#bfbfbf;#cbcbcb;#a0a0a0;#919191;#f7f7f7;#bcbcbc;#9a9a9a;#d7d7d7;#e5e5e5;#a1a1a1"/></rect>
<rect x="437" y="330" width="13" height="20" fill="#cdcdcd"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#cdcdcd;#d6d6d6;#bdbdbd;#cfcfcf;#939393;#959595;#f8f8f8;#eeeeee;#cbcbcb;#d3d3d3;#b3b3b3"/></rect>
<rect x="450" y="330" width="13" height="20" fill="#d0d0d0"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d0d0d0;#e9e9e9;#c9c9c9;#f6f6f6;#e8e8e8;#ececec;#f8f8f8;#b7b7b7;#9c9c9c;#b0b0b0;#aeaeae"/></rect>
<rect x="463" y="330" width="13" height="20" fill="#d3d3d3"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d3d3d3;#a8a8a8;#a4a4a4;#d8d8d8;#f2f2f2;#cfcfcf;#f8f8f8;#f5f5f5;#a5a5a5;#dcdcdc;#c9c9c9"/></rect>
<rect x="476" y="330" width="13" height="20" fill="#d6d6d6"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d6d6d6;#b1b1b1;#fafafa;#c0c0c0;#dcdcdc;#e2e2e2;#fafafa;#e4e4e4;#cdcdcd;#d2d2d2;#b6b6b6"/></rect>
<rect x="489" y="330" width="13" height="20" fill="#d9d9d9"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#d9d9d9;#fcfcfc;#fefefe;#c1c1c1;#aeaeae;#c4c4c4;#cdcdcd;#f8f8f8;#f8f8f8;#f3f3f3;#afafaf"/></rect>
<rect x="502" y="330" width="13" height="20" fill="#dcdcdc"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#dcdcdc;#f1f1f1;#ececec;#e7e7e7;#fefefe;#b6b6b6;#bebebe;#efefef;#fbfbfb;#e9e9e9;#cccccc"/></rect>
<rect x="515" y="330" width="13" height="20" fill="#dfdfdf"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#dfdfdf;#e6e6e6;#f1f1f1;#c0c0c0;#d2d2d2;#cccccc;#c1c1c1;#dedede;#c5c5c5;#cbcbcb;#c3c3c3"/></rect>
<rect x="528" y="330" width="13" height="20" fill="#e2e2e2"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#e2e2e2;#ededed;#bebebe;#f0f0f0;#cccccc;#c0c0c0;#fdfdfd;#cecece;#fdfdfd;#f9f9f9;#fafafa"/></rect>
<rect x="541" y="330" width="13" height="20" fill="#e5e5e5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#e5e5e5;#cdcdcd;#e1e1e1;#cacaca;#fefefe;#f9f9f9;#ededed;#e2e2e2;#dbdbdb;#f8f8f8;#e3e3e3"/></rect>
<rect x="554" y="330" width="13" height="20" fill="#e8e8e8"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#e8e8e8;#efefef;#d2d2d2;#d7d7d7;#cdcdcd;#f3f3f3;#ebebeb;#d2d2d2;#fbfbfb;#dadada;#e2e2e2"/></rect>
<rect x="567" y="330" width="13" height="20" fill="#eaeaea"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#eaeaea;#d8d8d8;#dedede;#fbfbfb;#e2e2e2;#d9d9d9;#eaeaea;#e1e1e1;#fefefe;#d6d6d6;#ffffff"/></rect>
<rect x="580" y="330" width="13" height="20" fill="#ededed"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#ededed;#d8d8d8;#fefefe;#f4f4f4;#e0e0e0;#ececec;#e3e3e3;#e2e2e2;#dfdfdf;#e7e7e7;#ffffff"/></rect>
<rect x="593" y="330" width="13" height="20" fill="#f0f0f0"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f0f0f0;#ffffff;#ffffff;#dfdfdf;#e7e7e7;#ffffff;#dedede;#f8f8f8;#e7e7e7;#ffffff;#dcdcdc"/></rect>
<rect x="606" y="330" width="13" height="20" fill="#f2f2f2"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f2f2f2;#fcfcfc;#ededed;#e6e6e6;#e1e1e1;#fdfdfd;#f3f3f3;#e8e8e8;#f0f0f0;#ffffff;#e9e9e9"/></rect>
<rect x="619" y="330" width="13" height="20" fill="#f5f5f5"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f5f5f5;#f7f7f7;#ebebeb;#ececec;#fcfcfc;#fafafa;#ededed;#e9e9e9;#eaeaea;#f8f8f8;#f5f5f5"/></rect>
<rect x="632" y="330" width="13" height="20" fill="#f7f7f7"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#f7f7f7;#f3f3f3;#f1f1f1;#fafafa;#fcfcfc;#fefefe;#f9f9f9;#f1f1f1;#efefef;#fcfcfc;#f6f6f6"/></rect>
<rect x="645" y="330" width="13" height="20" fill="#fafafa"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#fafafa;#fdfdfd;#f4f4f4;#fefefe;#f8f8f8;#ffffff;#ffffff;#fafafa;#f3f3f3;#ffffff;#fafafa"/></rect>
<rect x="658" y="330" width="13" height="20" fill="#fdfdfd"><animate attributeName="fill" dur="11.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0696;0.1478;0.2261;0.3043;0.3826;0.4609;0.5391;0.6174;0.6957;0.7739" values="#fdfdfd;#ffffff;#fbfbfb;#fafafa;#ffffff;#fcfcfc;#fafafa;#fcfcfc;#fdfdfd;#f9f9f9;#fdfdfd"/></rect>
<rect x="671" y="330" width="13" height="20" fill="#ffffff"/>
<text x="60" y="370" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">暗部（左）</text>
<text x="372.0" y="370" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2563eb">中間（粒が最も強い）</text>
<text x="684" y="370" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">明部（右）</text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.00 → 強さ 0.00<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.0692;0.0696;0.1088;0.1092;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.06 → 強さ 0.22<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1088;0.1092;0.1484;0.1488;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.12 → 強さ 0.42<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1484;0.1488;0.1881;0.1884;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.18 → 強さ 0.58<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.1881;0.1884;0.2277;0.2280;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.24 → 強さ 0.72<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2277;0.2280;0.2673;0.2676;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.29 → 強さ 0.83<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.2673;0.2676;0.3069;0.3072;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.35 → 強さ 0.91<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3069;0.3072;0.3465;0.3469;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.41 → 強さ 0.97<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3465;0.3469;0.3861;0.3865;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.47 → 強さ 1.00<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.3861;0.3865;0.4257;0.4261;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.53 → 強さ 1.00<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4257;0.4261;0.4654;0.4657;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.59 → 強さ 0.97<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.4654;0.4657;0.5050;0.5053;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.65 → 強さ 0.91<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5050;0.5053;0.5446;0.5449;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.71 → 強さ 0.83<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5446;0.5449;0.5842;0.5845;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.76 → 強さ 0.72<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.5842;0.5845;0.6238;0.6242;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.82 → 強さ 0.58<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6238;0.6242;0.6634;0.6638;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.88 → 強さ 0.42<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.6634;0.6638;0.7030;0.7034;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 0.94 → 強さ 0.22<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.7030;0.7034;0.7426;0.7430;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="110" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">明るさ 1.00 → 強さ 0.00<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;0.7426;0.7430;0.7823;0.7826;1.0000" values="0;0;1;1;0;0"/></text>
<text x="450" y="150" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">本物のフィルムは、暗部・明部で粒が目立ちにくい<animate attributeName="opacity" dur="11.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
</svg>

<!-- fig:film-grain-luma:end -->

## 明るさで強さを変える

**真っ黒や真っ白にもグレインを足す**と、**黒が浮き、白が汚れます**。**中間調で最も強く、暗部と明部で弱める**のが**自然**です。

```hlsl
float3 ApplyGrainLuma(float3 color, float2 uv, float time, float intensity) {
  float luma = dot(color, float3(0.2126, 0.7152, 0.0722));
  float response = 4.0 * luma * (1.0 - luma);
  float noise = Hash(uv * resolution + time * 61.0) - 0.5;
  return color + noise * intensity * response;
}
```

| 点 | 説明 |
| --- | --- |
| **`4 · luma · (1 − luma)`** | **luma 0.5 で最大（1）、0 と 1 で 0** の**放物線** |
| **効果** | **中間調の質感が出て、黒と白はクリーン** |

## ノイズの質

| ノイズ | 特徴 | 見た目 |
| --- | --- | --- |
| <strong>白色ノイズ（一様乱数）</strong> | **各画素が独立** | <strong>粗く、ザラザラ（デジタル的）</strong> |
| **ガウス ノイズ** | **平均付近が多く、外れ値が少ない** | **自然な粒状** |
| **ブルー ノイズ** | **高周波に偏り、低周波が少ない** | **目に優しく、均一** |
| **フィルム グレイン テクスチャ** | **実際のフィルムをスキャンして作る** | **最もリアル** |

**粒子の大きさを調整**するには、<strong>ノイズの座標を 1 画素より粗く（2×2 画素単位など）</strong>します。

```hlsl
float2 coarse = floor(uv * resolution / grain_size) * grain_size;
float noise = Hash(coarse + time * 61.0) - 0.5;
```

| `grain_size` | 見た目 |
| --- | --- |
| **1** | <strong>細かい（デジタル ノイズ寄り）</strong> |
| **2〜3** | **フィルムのような粒子** |

## 動かし方

**フィルムでは、1 コマごとに別の粒子**が**写る**ので、**グレインは毎フレーム変わる**のが**自然**です。**変わらないと画面に汚れが貼りついたように見えます**。

| 方式 | 内容 |
| --- | --- |
| **毎フレーム変える** | **`time` やフレーム番号でシードを変える** |
| **24 FPS 相当で変える** | **映画の動きに合わせる**（**ゲームが 60 FPS でも、グレインは 24 回/秒**） |
| **TAA との関係** | **TAA がノイズを平均して、弱めてしまう**ので、**TAA の後に足す** |

## ディザリングとの関係

<strong>8 ビット出力のグラデーション（暗い空・霧）</strong>は、<strong>量子化で縞（バンディング）</strong>が**出ます**。<strong>±0.5 ステップ程度の、微小なノイズを足す（ディザリング）</strong>と、**縞が見えなくなります**。

```hlsl
float3 Dither(float3 color, float2 pixel_position) {
  float noise = Hash(pixel_position + time * 61.0) - 0.5;
  return color + noise / 255.0;
}
```

| 目的 | ノイズの強さ |
| --- | --- |
| <strong>ディザリング（バンディング隠し）</strong> | <strong>1/255（見えない程度）</strong> |
| <strong>グレイン（質感）</strong> | <strong>0.01〜0.05（見える）</strong> |

**グレインを足すとディザリングも兼ねられます**（**強さが十分あれば、バンディングも見えなくなる**）。

## 使いどころ

| 場面 | 使い方 |
| --- | --- |
| **映画風の画作り** | **控えめなグレイン** |
| **ホラー・古い映像** | **強め ＋ 白黒・粗い粒** |
| **暗いシーン** | **暗部のバンディング隠し** |
| **ゲーム全体** | **ほぼ不要**（**クリアな絵が好まれる場合も**） |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **明るさで強さを変える** | **中間調のみ** |
| **粒の大きさを調整** | **細かすぎないフィルムのような粒子** |
| **TAA の後に足す** | **TAA がノイズを消さない** |
| **LDR（トーンマップ後）で** | **見た目の明るさに対して** |
| **他のパスと統合** | **ビネット・色収差・トーンマップと 1 パス** |
| **オプションで切れる** | **細部が見えづらい人のため** |
| **ディザリングを別に常時オン** | **グレインを使わなくても、バンディングを防ぐ** |

## よくあるミス

??? failure "グレインが固定で、画面に汚れが貼り付いて見える"
    **毎フレーム、シードを変える**。

??? failure "真っ黒な所にもグレインが乗って、黒が浮く"
    **明るさで強さを変える**（**暗部を弱める**）。

??? failure "TAA で、グレインが平均されて消える"
    **TAA の後**に足す。

??? failure "強すぎて、細部が見えない"
    **0.01〜0.03 に**、**オプションで調整**。

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
