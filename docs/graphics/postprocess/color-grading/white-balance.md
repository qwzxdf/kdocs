---
title: White Balance
tags:
  - 描画
---

# White Balance

<strong>同じ白い紙でも晴天の下では青白く、白熱灯の下では黄色く見えます</strong>。<strong>人間の目はこれを自動で補正して、「白い紙は白い」と感じます</strong>（色の恒常性）。カメラはこの補正を「ホワイト バランス」で行い、ゲームでも画面全体の色温度を調整して、「暖かい夕暮れ」や「冷たい夜」を作るために使います。このページでは、色温度（ケルビン）と色合い・光源の色を打ち消す考え方・簡易実装（LMS 空間）・ゲームでの使い方・注意点を説明します。

!!! tip "ポイント"
    - ホワイト バランス ＝ <strong>光源の色を打ち消して、白を白く見せる</strong>。<strong>全体の色味を暖色〜寒色にずらす</strong>。
    - <strong>色温度（K）</strong>：<strong>低い（約 2000 K）は橙、高い（約 10000 K）は青</strong>。<strong>6500 K 前後が日中の昼光（D65）</strong>。
    - <strong>色合い（Tint）</strong>：<strong>緑〜マゼンタの軸</strong>。
    - <strong>実装</strong>：<strong>LMS（錐体）空間で白点の比率で割る</strong>のが<strong>標準的</strong>。
    - <strong>ゲームでは「補正」ではなく、「演出」に使う</strong>こと<strong>が多い</strong>。
    - <strong>トーンマップの前（リニア）で行う</strong>と<strong>自然</strong>。

<!-- fig:white-balance:begin -->

<svg class="fig illust motion" data-fig="white-balance" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-white-balance" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ホワイト バランス: 暖色の光の下の「白」を、本当の白に戻す。直しすぎると、逆の色が付く</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">灰色の面と、赤い面を、オレンジ色の光(R:G:B = 1 : 0.78 : 0.5)で照らす。補正の強さを 0 → 0.5 → 1.0 → 1.5 に変える</text>
<text x="82.0" y="136" text-anchor="end" style="font-size:14px;font-weight:700;fill:#64748b">補正 0.0</text>
<rect x="90.0" y="108.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#baa688"/></rect>
<rect x="200.0" y="108.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#f3d9b1"/></rect>
<rect x="310.0" y="108.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#e66e4f"/></rect>
<rect x="420.0" y="108.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#7b8da8"/></rect>
<rect x="90.0" y="108" width="440.0" height="56.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0928;0.0930;1.0000" values="0;0;1;1"/><text x="546.0" y="128" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">灰色の色かぶり +0.66</text>
<text x="546.0" y="150" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">暖かすぎる(オレンジ)</text>
</g>
<text x="82.0" y="208" text-anchor="end" style="font-size:14px;font-weight:700;fill:#2563eb">補正 0.5</text>
<rect x="90.0" y="180.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2651" values="#e5e7eb;#b0a696"/></rect>
<rect x="200.0" y="180.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2651" values="#e5e7eb;#e6d9c4"/></rect>
<rect x="310.0" y="180.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2651" values="#e5e7eb;#da6e57"/></rect>
<rect x="420.0" y="180.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2651" values="#e5e7eb;#748dba"/></rect>
<rect x="90.0" y="180" width="440.0" height="56.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2882;0.2884;1.0000" values="0;0;1;1"/><text x="546.0" y="200" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">灰色の色かぶり +0.34</text>
<text x="546.0" y="222" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">まだ少し暖かい</text>
</g>
<text x="82.0" y="280" text-anchor="end" style="font-size:14px;font-weight:700;fill:#2ea043">補正 1.0</text>
<rect x="90.0" y="252.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4605" values="#e5e7eb;#a6a6a6"/></rect>
<rect x="200.0" y="252.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4605" values="#e5e7eb;#d9d9d9"/></rect>
<rect x="310.0" y="252.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4605" values="#e5e7eb;#ce6e60"/></rect>
<rect x="420.0" y="252.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4605" values="#e5e7eb;#6e8dce"/></rect>
<rect x="90.0" y="252" width="440.0" height="56.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4835;0.4837;1.0000" values="0;0;1;1"/><text x="546.0" y="272" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">灰色の色かぶり +0.00</text>
<text x="546.0" y="294" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">灰色が、灰色に戻った</text>
</g>
<text x="82.0" y="352" text-anchor="end" style="font-size:14px;font-weight:700;fill:#e5484d">補正 1.5</text>
<rect x="90.0" y="324.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6558" values="#e5e7eb;#9da6b8"/></rect>
<rect x="200.0" y="324.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6558" values="#e5e7eb;#cdd9f0"/></rect>
<rect x="310.0" y="324.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6558" values="#e5e7eb;#c26e6a"/></rect>
<rect x="420.0" y="324.0" width="110.3" height="56.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6558" values="#e5e7eb;#688de4"/></rect>
<rect x="90.0" y="324" width="440.0" height="56.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6789;0.6791;1.0000" values="0;0;1;1"/><text x="546.0" y="344" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">灰色の色かぶり -0.35</text>
<text x="546.0" y="366" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">直しすぎ(青っぽい)</text>
</g>
<text x="145.0" y="98" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">灰色</text>
<text x="255.0" y="98" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">白</text>
<text x="365.0" y="98" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">赤</text>
<text x="475.0" y="98" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">青</text>
<text x="40" y="420" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">灰色の「色かぶり」(R − B):</text>
<text x="260" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0928;0.0930;1.0000" values="1;1;0;0"/></text>
<text x="260" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">66<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0928;0.0930;0.2882;0.2884;1.0000" values="0;0;1;1;0;0"/></text>
<text x="260" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">34<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2882;0.2884;0.4835;0.4837;1.0000" values="0;0;1;1;0;0"/></text>
<text x="260" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4835;0.4837;0.6789;0.6791;1.0000" values="0;0;1;1;0;0"/></text>
<text x="260" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">-35<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6789;0.6791;1.0000" values="0;0;1;1"/></text>
<text x="310" y="424" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">(×0.01。0 が理想)</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.8324;0.8326;1.0000" values="0;0;1;1"/><rect x="440" y="410" width="490" height="90" rx="12" fill="#f0fdf4" stroke="#2ea043" stroke-width="2.5"/>
<text x="456" y="434" text-anchor="start" style="font-size:14px;font-weight:700;fill:#166534">補正 1.0 で、灰色が灰色に戻る。ほかの色も、本来の色に近づく</text>
<text x="456" y="457" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">補正 1.5 では、逆の色(青)が付く。ゲームでは、演出で、わざと暖かさを残すことが多い</text>
<text x="456" y="478" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">補正 = 光の色の逆数を、R・G・B に掛ける</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">暖かい光の下では、白い物も、オレンジ色に見える<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光の色の逆の倍率を掛けると、白が白に戻る<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.8510;0.8512;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">直しすぎると、逆の色が付く<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.8510;0.8512;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:white-balance:end -->

## 色温度と見た目

<strong>物体を熱すると温度に応じた色で光ります</strong>（<strong>黒体放射</strong>）。<strong>この温度（ケルビン）が「色温度」</strong>で、光源の色を表すのに使われます。

<svg class="fig illust" viewBox="0 0 780 190" role="img" aria-label="色温度">
<text x="20" y="26" class="fig-title">色温度：低いほど橙（暖色）、高いほど青（寒色）</text>
<defs><linearGradient id="wb-g" x1="0" x2="1"><stop offset="0" stop-color="#ff7a1a"/><stop offset="0.25" stop-color="#ffb35c"/><stop offset="0.5" stop-color="#fff4e6"/><stop offset="0.72" stop-color="#e9f1ff"/><stop offset="1" stop-color="#9ec3ff"/></linearGradient></defs>
<rect x="40" y="56" width="700" height="40" fill="url(#wb-g)" stroke="#94a3b8"/>
<g font-size="12" text-anchor="middle"><text x="60" y="116">1900 K</text><text x="60" y="134" style="font-size:11px">ろうそく</text>
<text x="210" y="116">2700 K</text><text x="210" y="134" style="font-size:11px">白熱電球</text>
<text x="390" y="116">5000 K</text><text x="390" y="134" style="font-size:11px">昼白色</text>
<text x="540" y="116">6500 K</text><text x="540" y="134" style="font-size:11px">昼光（D65）</text>
<text x="720" y="116">10000 K</text><text x="720" y="134" style="font-size:10px">青空の日陰</text></g>
</svg>

| 光源 | 色温度 |
| --- | --- |
| ろうそくの炎 | 約 1900 K（橙） |
| 白熱電球 | 約 2700 K（暖かい黄色） |
| 朝・夕方の日光 | 約 3500〜4500 K |
| 正午の日光 | 約 5500〜6500 K（ほぼ白） |
| 曇り・日陰 | 約 7000〜10000 K（青白い） |

## 白を白に戻す考え方

<strong>光源が橙（低い色温度）のとき、白い物は橙に映ります</strong>。<strong>その橙を打ち消す（青を足す・橙を減らす）</strong>と、<strong>白が白に戻ります</strong>。これがホワイト バランスの補正です。

操作ごとの結果です。光源の色温度を指定すると、その光源の色が白になるように補正されます（画面全体は逆の色へ寄ります）。ホワイト バランスの温度を上げると、画面が暖かく（橙に）なります（青い光源を想定して補正しすぎるため）。下げると、画面が青く（寒色に）なります。

<strong>ゲームでは、「補正」というより、画面の色味を作る「演出」</strong>として<strong>使います</strong>。<strong>温度を上げて暖かく・下げて冷たく</strong>調整します。

## 実装（LMS 空間）

<strong>人間の錐体（L・M・S）の反応</strong>を<strong>表す LMS 空間</strong>で、光源の白点を基準の白に合わせるのが標準的です。

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
| `temperature`・`tint` | −1〜+1 のつまみ（<strong>色温度（暖〜寒）と、色合い（緑〜マゼンタ）</strong>） |
| `x, y` | 色度座標。D65 の白（0.31271, 0.32902）を基準にずらす |
| `white_lms / lms` | <strong>光源の LMS で割る比率（ゲイン）</strong> |
| `kRgbToLms` など | 色空間変換の 3×3 行列（公開されている値） |

<strong>もっと簡単な近似</strong>は、<strong>RGB にゲインを掛けるだけ</strong>です。

```hlsl
float3 SimpleWhiteBalance(float3 color, float temperature) {
  float3 warm = float3(1.0, 0.9, 0.75);
  float3 cool = float3(0.8, 0.9, 1.0);
  float3 gain = lerp(warm, cool, saturate(0.5 - temperature * 0.5));
  return color * gain;
}
```

2 つの方式を比べます。LMS 空間（本格）は、錐体の応答に近い空間でゲインを掛けるので精度が高く、行列を使います。RGB ゲイン（簡易）は、RGB の各チャンネルに直接ゲインを掛けるので粗く（明るさが変わります）、1 行で済みます。

## 色合い（Tint）

<strong>色温度が「橙〜青」の軸</strong>だとすると<strong>色合いは「緑〜マゼンタ」の軸</strong>です。蛍光灯の緑かぶりを打ち消したり、ファンタジーな色味を作るのに使います。

2 つのつまみの軸です。温度（Temperature）は橙と青の軸です。色合い（Tint）は緑とマゼンタの軸です。

## ゲームでの使い方

| 使い方 | 内容 |
| --- | --- |
| 時間帯の演出 | 朝：暖かく、昼：中立、夕方：橙、夜：青 |
| 場所の演出 | 洞窟：冷たい青、火山：暖かい橙 |
| 状態の演出 | 体力が低い：色が冷える・彩度が下がる |
| 光源との整合 | 画面の主光源の色とホワイト バランスで調和させる |

<strong>時間帯の変化</strong>に<strong>合わせて、色温度を補間</strong>すると自然な移り変わりになります（[空と大気](../../atmosphere/sky-models/index.md)）。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| リニア空間でトーンマップの前 | 物理的に自然（HDR の値で比率を保つ） |
| LMS（錐体）空間で | より自然な補正 |
| LUT に焼く | ほかの調整と一緒に 1 つに（[3D LUT](lut-3d.md)） |
| ボリュームで補間 | 場所ごとに温度を変えて、境で滑らかに |
| ライトの色と合わせる | 光源の色（ライト）と、ホワイト バランスで二重に偏らない |

## よくあるミス

??? failure "ホワイト バランスと、ライトの色の両方を動かして、色かぶりが強すぎる"
    <strong>ライトの色と全体のホワイト バランスの役割を分ける</strong>（<strong>光源は物理的に全体の色味は演出</strong>）。

??? failure "RGB ゲインで調整したら、全体の明るさも変わった"
    <strong>LMS で輝度を保つ</strong>、または<strong>簡易版の後に輝度を補正</strong>する。

??? failure "ガンマ空間でホワイト バランスして、色が不自然"
    <strong>リニア空間</strong>で行う。

??? failure "場所の切り替えで、色温度が急に変わる"
    <strong>ボリュームで補間</strong>する。

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
