---
title: Vignette
tags:
  - 描画
---

# Vignette

<strong>ビネット（周辺減光）</strong>は、**画面の周辺が中心より暗くなる**効果です。**実際のレンズでは、設計や絞り・フィルターの影響で周辺に届く光が減る**ために**起きます**。**視線を画面の中心に集める効果があり**、**映画風・夜・緊張した場面**で**よく使われます**。**実装はとても簡単**ですが、**かけすぎると周辺が見えずプレイしにくい**ので、**注意**が**必要**です。このページでは、**物理的な原因（cos⁴ の法則）・基本の式・形（円・楕円）・色付きのビネット・ゲームでの使い方**を説明します。

!!! tip "ポイント"
    - ビネット ＝ <strong>画面の周辺ほど暗くする</strong>。<strong>中心は変えない</strong>。
    - 物理的な原因 ＝ <strong>cos⁴θ の法則</strong>（<strong>光軸から離れた光ほど、角度の 4 乗で暗い</strong>）と<strong>レンズ・絞りの遮り（機械的ビネット）</strong>。
    - 実装 ＝ <strong>画面中心からの距離で、暗くする係数を `smoothstep` で決め、色に掛ける</strong>。
    - <strong>形</strong>は<strong>円・楕円・四角寄り</strong>。<strong>アスペクト比の補正</strong>が<strong>必要</strong>。
    - <strong>色付き（暗い赤・黒以外）</strong>のビネットも<strong>演出</strong>に<strong>使える</strong>。
    - <strong>強すぎない</strong>。<strong>周辺のゲーム情報が見づらくなる</strong>。<strong>設定で切れる</strong>。

## 起きる理由

**レンズの設計上、光軸（画面の中心）から離れた方向から来る光は、レンズの端で遮られたり、斜めに入る分だけ弱くなったりします**。

<div class="formula">周辺の明るさ = 中心の明るさ × cos⁴(θ)　（θ：光軸からの角度）</div>

ビネットの原因は 3 つあります。cos⁴ の法則（自然なビネット）は、角度 θ が大きいほど、光が 4 乗で弱まる現象です。機械的ビネットは、レンズ鏡筒・フィルター・絞りが斜めの光を遮ることで起きます。光学的ビネットは、レンズ内部の絞りが斜めの光を通しにくいことで起きます。

<svg class="fig illust" viewBox="0 0 780 210" role="img" aria-label="ビネット">
<text x="20" y="26" class="fig-title">ビネット：中心から離れるほど暗くなる</text>
<defs><radialGradient id="vg-g" cx="0.5" cy="0.5" r="0.7"><stop offset="0.4" stop-color="#fff7d1" stop-opacity="1"/><stop offset="1" stop-color="#000000" stop-opacity="0.85"/></radialGradient></defs>
<rect x="40" y="50" width="300" height="140" fill="#fff7d1" stroke="#94a3b8"/><text x="40" y="206" style="font-size:12px">ビネットなし</text>
<rect x="400" y="50" width="300" height="140" fill="#fff7d1" stroke="#94a3b8"/><rect x="400" y="50" width="300" height="140" fill="url(#vg-g)"/><text x="400" y="206" style="font-size:12px">ビネットあり：周辺が暗い</text>
</svg>

## 基本の式

```hlsl
float Vignette(float2 uv, float intensity, float smoothness, float roundness) {
  float2 d = (uv - 0.5) * float2(roundness, 1.0) * 2.0;
  float distance_from_center = length(d);
  return 1.0 - smoothstep(1.0 - intensity - smoothness, 1.0 - intensity, distance_from_center) * intensity;
}

float3 ApplyVignette(float3 color, float2 uv) {
  return color * Vignette(uv, kVignetteIntensity, kVignetteSmoothness, kRoundness);
}
```

| 点 | 説明 |
| --- | --- |
| **`d = (uv − 0.5) × 2`** | **画面中心を原点に±1 の座標**（**角で約 1.4**） |
| **`length(d)`** | **画面中心からの距離** |
| **`smoothstep`** | **暗くなり始める距離〜暗くなりきる距離を、滑らかに** |
| **`intensity`** | <strong>周辺の暗さの強さ（0〜1）</strong> |
| **`smoothness`** | **暗さの移り変わりの幅** |
| **`roundness`** | **アスペクト比の補正**。**1 で画面の縦横比に沿った楕円、画面の高さで円なら調整** |

<!-- fig:vignette-params:begin -->

<svg class="fig illust motion" data-fig="vignette-params" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-vignette-params" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ビネット: 画面の端を暗くする。半径(どこから暗くするか)と、柔らかさで、形が変わる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">横 1 列(中心 → 端)。半径と柔らかさを変えて、端の暗さと、暗くなる範囲を計算する</text>
<rect x="30" y="96" width="620" height="240" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 明るさの倍率(横 = 中心からの距離。1.0 = 画面の端の方向)</text>
<line x1="270.0" y1="120.0" x2="270.0" y2="310.0" stroke="#e2e8f0" stroke-width="1.2" stroke-dasharray="3 4"/>
<line x1="470.0" y1="120.0" x2="470.0" y2="310.0" stroke="#e2e8f0" stroke-width="1.2" stroke-dasharray="3 4"/>
<text x="470.0" y="326" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">画面の端(左右)</text>
<text x="630.0" y="326" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">角</text>
<path d="M70.0,120.0 L79.33,120.0 L88.67,120.0 L98.0,120.0 L107.33,120.0 L116.67,120.0 L126.0,120.0 L135.33,120.0 L144.67,120.0 L154.0,120.0 L163.33,120.0 L172.67,120.0 L182.0,120.0 L191.33,120.0 L200.67,120.0 L210.0,120.0 L219.33,120.0 L228.67,120.0 L238.0,120.0 L247.33,120.0 L256.67,120.0 L266.0,120.0 L275.33,120.76 L284.67,125.47 L294.0,133.83 L303.33,145.09 L312.67,158.48 L322.0,173.28 L331.33,188.72 L340.67,204.05 L350.0,218.52 L359.33,231.38 L368.67,241.88 L378.0,249.28 L387.33,252.81 L396.67,253.0 L406.0,253.0 L415.33,253.0 L424.67,253.0 L434.0,253.0 L443.33,253.0 L452.67,253.0 L462.0,253.0 L471.33,253.0 L480.67,253.0 L490.0,253.0 L499.33,253.0 L508.67,253.0 L518.0,253.0 L527.33,253.0 L536.67,253.0 L546.0,253.0 L555.33,253.0 L564.67,253.0 L574.0,253.0 L583.33,253.0 L592.67,253.0 L602.0,253.0 L611.33,253.0 L620.67,253.0 L630.0,253.0" fill="none" stroke="#e5484d" stroke-width="4"><animate attributeName="d" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698;0.2651;0.4605;0.6558" values="M70.0,120.0 L79.33,120.0 L88.67,120.0 L98.0,120.0 L107.33,120.0 L116.67,120.0 L126.0,120.0 L135.33,120.0 L144.67,120.0 L154.0,120.0 L163.33,120.0 L172.67,120.0 L182.0,120.0 L191.33,120.0 L200.67,120.0 L210.0,120.0 L219.33,120.0 L228.67,120.0 L238.0,120.0 L247.33,120.0 L256.67,120.0 L266.0,120.0 L275.33,120.76 L284.67,125.47 L294.0,133.83 L303.33,145.09 L312.67,158.48 L322.0,173.28 L331.33,188.72 L340.67,204.05 L350.0,218.52 L359.33,231.38 L368.67,241.88 L378.0,249.28 L387.33,252.81 L396.67,253.0 L406.0,253.0 L415.33,253.0 L424.67,253.0 L434.0,253.0 L443.33,253.0 L452.67,253.0 L462.0,253.0 L471.33,253.0 L480.67,253.0 L490.0,253.0 L499.33,253.0 L508.67,253.0 L518.0,253.0 L527.33,253.0 L536.67,253.0 L546.0,253.0 L555.33,253.0 L564.67,253.0 L574.0,253.0 L583.33,253.0 L592.67,253.0 L602.0,253.0 L611.33,253.0 L620.67,253.0 L630.0,253.0;M70.0,120.0 L79.33,120.0 L88.67,120.0 L98.0,120.0 L107.33,120.0 L116.67,120.0 L126.0,120.0 L135.33,120.0 L144.67,120.0 L154.0,120.0 L163.33,120.0 L172.67,120.0 L182.0,120.0 L191.33,120.0 L200.67,120.0 L210.0,120.0 L219.33,120.0 L228.67,120.0 L238.0,120.0 L247.33,120.0 L256.67,120.0 L266.0,120.0 L275.33,120.76 L284.67,125.47 L294.0,133.83 L303.33,145.09 L312.67,158.48 L322.0,173.28 L331.33,188.72 L340.67,204.05 L350.0,218.52 L359.33,231.38 L368.67,241.88 L378.0,249.28 L387.33,252.81 L396.67,253.0 L406.0,253.0 L415.33,253.0 L424.67,253.0 L434.0,253.0 L443.33,253.0 L452.67,253.0 L462.0,253.0 L471.33,253.0 L480.67,253.0 L490.0,253.0 L499.33,253.0 L508.67,253.0 L518.0,253.0 L527.33,253.0 L536.67,253.0 L546.0,253.0 L555.33,253.0 L564.67,253.0 L574.0,253.0 L583.33,253.0 L592.67,253.0 L602.0,253.0 L611.33,253.0 L620.67,253.0 L630.0,253.0;M70.0,120.0 L79.33,120.0 L88.67,120.0 L98.0,120.0 L107.33,120.0 L116.67,120.0 L126.0,120.0 L135.33,120.0 L144.67,120.0 L154.0,120.0 L163.33,120.0 L172.67,120.0 L182.0,120.0 L191.33,120.0 L200.67,120.0 L210.0,120.0 L219.33,120.0 L228.67,120.0 L238.0,120.0 L247.33,120.0 L256.67,120.0 L266.0,120.0 L275.33,120.11 L284.67,120.81 L294.0,122.13 L303.33,124.03 L312.67,126.46 L322.0,129.39 L331.33,132.78 L340.67,136.59 L350.0,140.78 L359.33,145.31 L368.67,150.14 L378.0,155.22 L387.33,160.53 L396.67,166.02 L406.0,171.65 L415.33,177.38 L424.67,183.18 L434.0,188.99 L443.33,194.79 L452.67,200.54 L462.0,206.18 L471.33,211.7 L480.67,217.03 L490.0,222.15 L499.33,227.02 L508.67,231.59 L518.0,235.83 L527.33,239.7 L536.67,243.15 L546.0,246.15 L555.33,248.66 L564.67,250.63 L574.0,252.04 L583.33,252.83 L592.67,253.0 L602.0,253.0 L611.33,253.0 L620.67,253.0 L630.0,253.0;M70.0,120.0 L79.33,120.0 L88.67,120.0 L98.0,120.0 L107.33,120.0 L116.67,120.0 L126.0,120.0 L135.33,120.0 L144.67,120.0 L154.0,120.0 L163.33,120.0 L172.67,120.0 L182.0,120.0 L191.33,120.05 L200.67,122.97 L210.0,129.85 L219.33,139.96 L228.67,152.53 L238.0,166.82 L247.33,182.07 L256.67,197.54 L266.0,212.47 L275.33,226.11 L284.67,237.72 L294.0,246.54 L303.33,251.81 L312.67,253.0 L322.0,253.0 L331.33,253.0 L340.67,253.0 L350.0,253.0 L359.33,253.0 L368.67,253.0 L378.0,253.0 L387.33,253.0 L396.67,253.0 L406.0,253.0 L415.33,253.0 L424.67,253.0 L434.0,253.0 L443.33,253.0 L452.67,253.0 L462.0,253.0 L471.33,253.0 L480.67,253.0 L490.0,253.0 L499.33,253.0 L508.67,253.0 L518.0,253.0 L527.33,253.0 L536.67,253.0 L546.0,253.0 L555.33,253.0 L564.67,253.0 L574.0,253.0 L583.33,253.0 L592.67,253.0 L602.0,253.0 L611.33,253.0 L620.67,253.0 L630.0,253.0;M70.0,120.0 L79.33,120.0 L88.67,120.0 L98.0,120.0 L107.33,120.0 L116.67,120.0 L126.0,120.0 L135.33,120.0 L144.67,120.0 L154.0,120.0 L163.33,120.0 L172.67,120.0 L182.0,120.0 L191.33,120.0 L200.67,120.0 L210.0,120.0 L219.33,120.0 L228.67,120.0 L238.0,120.0 L247.33,120.0 L256.67,120.0 L266.0,120.0 L275.33,120.0 L284.67,120.0 L294.0,120.0 L303.33,120.0 L312.67,120.0 L322.0,120.0 L331.33,120.0 L340.67,120.0 L350.0,120.0 L359.33,120.0 L368.67,120.0 L378.0,120.0 L387.33,120.0 L396.67,129.85 L406.0,166.82 L415.33,212.47 L424.67,246.54 L434.0,253.0 L443.33,253.0 L452.67,253.0 L462.0,253.0 L471.33,253.0 L480.67,253.0 L490.0,253.0 L499.33,253.0 L508.67,253.0 L518.0,253.0 L527.33,253.0 L536.67,253.0 L546.0,253.0 L555.33,253.0 L564.67,253.0 L574.0,253.0 L583.33,253.0 L592.67,253.0 L602.0,253.0 L611.33,253.0 L620.67,253.0 L630.0,253.0"/></path>
<rect x="670" y="96" width="260" height="200" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="670" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 画面の見え方(16:9)</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2649;0.2651;1.0000" values="1;1;0;0"/><rect x="680.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#595959"/></rect>
<rect x="741.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#797979"/></rect>
<rect x="750.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#9f9f9f"/></rect>
<rect x="759.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#c2c2c2"/></rect>
<rect x="768.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#dddddd"/></rect>
<rect x="776.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#eeeeee"/></rect>
<rect x="785.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f7f7f7"/></rect>
<rect x="794.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#fafafa"/></rect>
<rect x="803.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#fafafa"/></rect>
<rect x="812.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f7f7f7"/></rect>
<rect x="820.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#eeeeee"/></rect>
<rect x="829.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#dddddd"/></rect>
<rect x="838.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#c2c2c2"/></rect>
<rect x="847.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#9f9f9f"/></rect>
<rect x="856.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#797979"/></rect>
<rect x="864.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#595959"/></rect>
<rect x="873.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#555555"/></rect>
<rect x="732.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#777777"/></rect>
<rect x="741.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#a4a4a4"/></rect>
<rect x="750.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#cfcfcf"/></rect>
<rect x="759.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#ededed"/></rect>
<rect x="768.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#fdfdfd"/></rect>
<rect x="776.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#fdfdfd"/></rect>
<rect x="838.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#ededed"/></rect>
<rect x="847.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#cfcfcf"/></rect>
<rect x="856.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#a4a4a4"/></rect>
<rect x="864.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#777777"/></rect>
<rect x="873.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#555555"/></rect>
<rect x="882.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4f4f4f"/></rect>
<rect x="724.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#6c6c6c"/></rect>
<rect x="732.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#9c9c9c"/></rect>
<rect x="741.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#cdcdcd"/></rect>
<rect x="750.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f1f1f1"/></rect>
<rect x="759.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f1f1f1"/></rect>
<rect x="856.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#cdcdcd"/></rect>
<rect x="864.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#9c9c9c"/></rect>
<rect x="873.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#6c6c6c"/></rect>
<rect x="882.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4f4f4f"/></rect>
<rect x="891.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#5a5a5a"/></rect>
<rect x="724.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#878787"/></rect>
<rect x="732.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#bebebe"/></rect>
<rect x="741.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#ebebeb"/></rect>
<rect x="750.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#ebebeb"/></rect>
<rect x="864.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#bebebe"/></rect>
<rect x="873.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#878787"/></rect>
<rect x="882.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#5a5a5a"/></rect>
<rect x="891.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#6b6b6b"/></rect>
<rect x="724.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#a1a1a1"/></rect>
<rect x="732.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#d9d9d9"/></rect>
<rect x="741.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#fbfbfb"/></rect>
<rect x="750.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#fbfbfb"/></rect>
<rect x="864.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#d9d9d9"/></rect>
<rect x="873.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#a1a1a1"/></rect>
<rect x="882.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#6b6b6b"/></rect>
<rect x="891.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#515151"/></rect>
<rect x="715.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#7a7a7a"/></rect>
<rect x="724.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#b6b6b6"/></rect>
<rect x="732.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#eaeaea"/></rect>
<rect x="741.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#eaeaea"/></rect>
<rect x="873.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#b6b6b6"/></rect>
<rect x="882.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#7a7a7a"/></rect>
<rect x="891.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#515151"/></rect>
<rect x="900.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#565656"/></rect>
<rect x="715.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#868686"/></rect>
<rect x="724.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#c3c3c3"/></rect>
<rect x="732.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f4f4f4"/></rect>
<rect x="741.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f4f4f4"/></rect>
<rect x="873.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#c3c3c3"/></rect>
<rect x="882.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#868686"/></rect>
<rect x="891.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#565656"/></rect>
<rect x="900.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#595959"/></rect>
<rect x="715.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#8c8c8c"/></rect>
<rect x="724.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#cacaca"/></rect>
<rect x="732.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f8f8f8"/></rect>
<rect x="741.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f8f8f8"/></rect>
<rect x="873.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#cacaca"/></rect>
<rect x="882.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#8c8c8c"/></rect>
<rect x="891.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#595959"/></rect>
<rect x="900.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#595959"/></rect>
<rect x="715.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#8c8c8c"/></rect>
<rect x="724.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#cacaca"/></rect>
<rect x="732.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f8f8f8"/></rect>
<rect x="741.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f8f8f8"/></rect>
<rect x="873.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#cacaca"/></rect>
<rect x="882.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#8c8c8c"/></rect>
<rect x="891.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#595959"/></rect>
<rect x="900.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#565656"/></rect>
<rect x="715.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#868686"/></rect>
<rect x="724.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#c3c3c3"/></rect>
<rect x="732.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f4f4f4"/></rect>
<rect x="741.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f4f4f4"/></rect>
<rect x="873.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#c3c3c3"/></rect>
<rect x="882.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#868686"/></rect>
<rect x="891.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#565656"/></rect>
<rect x="900.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#515151"/></rect>
<rect x="715.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#7a7a7a"/></rect>
<rect x="724.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#b6b6b6"/></rect>
<rect x="732.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#eaeaea"/></rect>
<rect x="741.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#eaeaea"/></rect>
<rect x="873.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#b6b6b6"/></rect>
<rect x="882.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#7a7a7a"/></rect>
<rect x="891.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#515151"/></rect>
<rect x="900.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#6b6b6b"/></rect>
<rect x="724.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#a1a1a1"/></rect>
<rect x="732.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#d9d9d9"/></rect>
<rect x="741.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#fbfbfb"/></rect>
<rect x="750.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#fbfbfb"/></rect>
<rect x="864.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#d9d9d9"/></rect>
<rect x="873.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#a1a1a1"/></rect>
<rect x="882.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#6b6b6b"/></rect>
<rect x="891.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#5a5a5a"/></rect>
<rect x="724.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#878787"/></rect>
<rect x="732.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#bebebe"/></rect>
<rect x="741.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#ebebeb"/></rect>
<rect x="750.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#ebebeb"/></rect>
<rect x="864.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#bebebe"/></rect>
<rect x="873.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#878787"/></rect>
<rect x="882.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#5a5a5a"/></rect>
<rect x="891.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4f4f4f"/></rect>
<rect x="724.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#6c6c6c"/></rect>
<rect x="732.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#9c9c9c"/></rect>
<rect x="741.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#cdcdcd"/></rect>
<rect x="750.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f1f1f1"/></rect>
<rect x="759.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f1f1f1"/></rect>
<rect x="856.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#cdcdcd"/></rect>
<rect x="864.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#9c9c9c"/></rect>
<rect x="873.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#6c6c6c"/></rect>
<rect x="882.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4f4f4f"/></rect>
<rect x="891.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#555555"/></rect>
<rect x="732.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#777777"/></rect>
<rect x="741.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#a4a4a4"/></rect>
<rect x="750.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#cfcfcf"/></rect>
<rect x="759.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#ededed"/></rect>
<rect x="768.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#fdfdfd"/></rect>
<rect x="776.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#fdfdfd"/></rect>
<rect x="838.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#ededed"/></rect>
<rect x="847.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#cfcfcf"/></rect>
<rect x="856.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#a4a4a4"/></rect>
<rect x="864.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#777777"/></rect>
<rect x="873.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#555555"/></rect>
<rect x="882.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#595959"/></rect>
<rect x="741.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#797979"/></rect>
<rect x="750.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#9f9f9f"/></rect>
<rect x="759.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#c2c2c2"/></rect>
<rect x="768.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#dddddd"/></rect>
<rect x="776.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#eeeeee"/></rect>
<rect x="785.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f7f7f7"/></rect>
<rect x="794.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#fafafa"/></rect>
<rect x="803.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#fafafa"/></rect>
<rect x="812.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#f7f7f7"/></rect>
<rect x="820.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#eeeeee"/></rect>
<rect x="829.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#dddddd"/></rect>
<rect x="838.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#c2c2c2"/></rect>
<rect x="847.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#9f9f9f"/></rect>
<rect x="856.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#797979"/></rect>
<rect x="864.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#595959"/></rect>
<rect x="873.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#ffffff;#4d4d4d"/></rect>
<rect x="680" y="120" width="246.40000000000003" height="134.4" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="680" y="270" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">暗くなる範囲(10% 以上): 54%</text>
<text x="40" y="372" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5484d">半径 0.5・柔らかさ 0.3</text>
<text x="40" y="402" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">端の明るさ: 0.30 / 角の明るさ: 0.30</text>
<text x="40" y="428" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">暗くなる範囲: 画面の 54%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2649;0.2651;0.4603;0.4605;1.0000" values="0;0;1;1;0;0"/><rect x="680.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#696969"/></rect>
<rect x="688.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#7a7a7a"/></rect>
<rect x="697.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8d8d8d"/></rect>
<rect x="706.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a0a0a0"/></rect>
<rect x="715.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#b3b3b3"/></rect>
<rect x="724.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#c5c5c5"/></rect>
<rect x="732.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d5d5d5"/></rect>
<rect x="741.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e2e2e2"/></rect>
<rect x="750.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#ededed"/></rect>
<rect x="759.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f5f5f5"/></rect>
<rect x="768.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fafafa"/></rect>
<rect x="776.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="785.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="794.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="803.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="812.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="820.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="829.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fafafa"/></rect>
<rect x="838.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f5f5f5"/></rect>
<rect x="847.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#ededed"/></rect>
<rect x="856.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e2e2e2"/></rect>
<rect x="864.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d5d5d5"/></rect>
<rect x="873.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#c5c5c5"/></rect>
<rect x="882.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#b3b3b3"/></rect>
<rect x="891.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a0a0a0"/></rect>
<rect x="900.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8d8d8d"/></rect>
<rect x="908.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#7a7a7a"/></rect>
<rect x="917.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#696969"/></rect>
<rect x="680.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#717171"/></rect>
<rect x="688.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#848484"/></rect>
<rect x="697.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#989898"/></rect>
<rect x="706.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#adadad"/></rect>
<rect x="715.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#c1c1c1"/></rect>
<rect x="724.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d3d3d3"/></rect>
<rect x="732.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e2e2e2"/></rect>
<rect x="741.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#eeeeee"/></rect>
<rect x="750.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f7f7f7"/></rect>
<rect x="759.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="768.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="847.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f7f7f7"/></rect>
<rect x="856.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#eeeeee"/></rect>
<rect x="864.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e2e2e2"/></rect>
<rect x="873.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d3d3d3"/></rect>
<rect x="882.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#c1c1c1"/></rect>
<rect x="891.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#adadad"/></rect>
<rect x="900.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#989898"/></rect>
<rect x="908.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#848484"/></rect>
<rect x="917.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#717171"/></rect>
<rect x="680.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#797979"/></rect>
<rect x="688.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8e8e8e"/></rect>
<rect x="697.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a3a3a3"/></rect>
<rect x="706.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#b8b8b8"/></rect>
<rect x="715.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#cccccc"/></rect>
<rect x="724.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#dedede"/></rect>
<rect x="732.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#ececec"/></rect>
<rect x="741.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f7f7f7"/></rect>
<rect x="750.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fdfdfd"/></rect>
<rect x="759.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fdfdfd"/></rect>
<rect x="856.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f7f7f7"/></rect>
<rect x="864.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#ececec"/></rect>
<rect x="873.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#dedede"/></rect>
<rect x="882.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#cccccc"/></rect>
<rect x="891.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#b8b8b8"/></rect>
<rect x="900.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a3a3a3"/></rect>
<rect x="908.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8e8e8e"/></rect>
<rect x="917.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#797979"/></rect>
<rect x="680.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#808080"/></rect>
<rect x="688.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#969696"/></rect>
<rect x="697.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#acacac"/></rect>
<rect x="706.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#c2c2c2"/></rect>
<rect x="715.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d6d6d6"/></rect>
<rect x="724.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e7e7e7"/></rect>
<rect x="732.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f4f4f4"/></rect>
<rect x="741.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="750.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="864.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f4f4f4"/></rect>
<rect x="873.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e7e7e7"/></rect>
<rect x="882.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d6d6d6"/></rect>
<rect x="891.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#c2c2c2"/></rect>
<rect x="900.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#acacac"/></rect>
<rect x="908.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#969696"/></rect>
<rect x="917.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#808080"/></rect>
<rect x="680.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#868686"/></rect>
<rect x="688.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#9d9d9d"/></rect>
<rect x="697.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#b4b4b4"/></rect>
<rect x="706.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#cacaca"/></rect>
<rect x="715.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#dddddd"/></rect>
<rect x="724.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#ededed"/></rect>
<rect x="732.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f9f9f9"/></rect>
<rect x="741.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="750.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="864.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f9f9f9"/></rect>
<rect x="873.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#ededed"/></rect>
<rect x="882.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#dddddd"/></rect>
<rect x="891.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#cacaca"/></rect>
<rect x="900.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#b4b4b4"/></rect>
<rect x="908.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#9d9d9d"/></rect>
<rect x="917.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#868686"/></rect>
<rect x="680.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8b8b8b"/></rect>
<rect x="688.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a2a2a2"/></rect>
<rect x="697.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#bababa"/></rect>
<rect x="706.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d0d0d0"/></rect>
<rect x="715.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e3e3e3"/></rect>
<rect x="724.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f2f2f2"/></rect>
<rect x="732.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="741.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="873.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f2f2f2"/></rect>
<rect x="882.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e3e3e3"/></rect>
<rect x="891.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d0d0d0"/></rect>
<rect x="900.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#bababa"/></rect>
<rect x="908.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a2a2a2"/></rect>
<rect x="917.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8b8b8b"/></rect>
<rect x="680.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8f8f8f"/></rect>
<rect x="688.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a6a6a6"/></rect>
<rect x="697.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#bebebe"/></rect>
<rect x="706.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d3d3d3"/></rect>
<rect x="715.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e6e6e6"/></rect>
<rect x="724.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f5f5f5"/></rect>
<rect x="732.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fdfdfd"/></rect>
<rect x="741.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fdfdfd"/></rect>
<rect x="873.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f5f5f5"/></rect>
<rect x="882.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e6e6e6"/></rect>
<rect x="891.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d3d3d3"/></rect>
<rect x="900.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#bebebe"/></rect>
<rect x="908.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a6a6a6"/></rect>
<rect x="917.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8f8f8f"/></rect>
<rect x="680.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#909090"/></rect>
<rect x="688.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a8a8a8"/></rect>
<rect x="697.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#bfbfbf"/></rect>
<rect x="706.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d5d5d5"/></rect>
<rect x="715.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e8e8e8"/></rect>
<rect x="724.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f6f6f6"/></rect>
<rect x="732.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="741.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="873.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f6f6f6"/></rect>
<rect x="882.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e8e8e8"/></rect>
<rect x="891.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d5d5d5"/></rect>
<rect x="900.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#bfbfbf"/></rect>
<rect x="908.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a8a8a8"/></rect>
<rect x="917.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#909090"/></rect>
<rect x="680.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#909090"/></rect>
<rect x="688.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a8a8a8"/></rect>
<rect x="697.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#bfbfbf"/></rect>
<rect x="706.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d5d5d5"/></rect>
<rect x="715.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e8e8e8"/></rect>
<rect x="724.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f6f6f6"/></rect>
<rect x="732.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="741.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="873.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f6f6f6"/></rect>
<rect x="882.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e8e8e8"/></rect>
<rect x="891.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d5d5d5"/></rect>
<rect x="900.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#bfbfbf"/></rect>
<rect x="908.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a8a8a8"/></rect>
<rect x="917.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#909090"/></rect>
<rect x="680.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8f8f8f"/></rect>
<rect x="688.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a6a6a6"/></rect>
<rect x="697.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#bebebe"/></rect>
<rect x="706.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d3d3d3"/></rect>
<rect x="715.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e6e6e6"/></rect>
<rect x="724.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f5f5f5"/></rect>
<rect x="732.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fdfdfd"/></rect>
<rect x="741.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fdfdfd"/></rect>
<rect x="873.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f5f5f5"/></rect>
<rect x="882.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e6e6e6"/></rect>
<rect x="891.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d3d3d3"/></rect>
<rect x="900.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#bebebe"/></rect>
<rect x="908.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a6a6a6"/></rect>
<rect x="917.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8f8f8f"/></rect>
<rect x="680.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8b8b8b"/></rect>
<rect x="688.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a2a2a2"/></rect>
<rect x="697.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#bababa"/></rect>
<rect x="706.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d0d0d0"/></rect>
<rect x="715.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e3e3e3"/></rect>
<rect x="724.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f2f2f2"/></rect>
<rect x="732.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="741.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="873.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f2f2f2"/></rect>
<rect x="882.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e3e3e3"/></rect>
<rect x="891.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d0d0d0"/></rect>
<rect x="900.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#bababa"/></rect>
<rect x="908.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a2a2a2"/></rect>
<rect x="917.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8b8b8b"/></rect>
<rect x="680.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#868686"/></rect>
<rect x="688.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#9d9d9d"/></rect>
<rect x="697.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#b4b4b4"/></rect>
<rect x="706.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#cacaca"/></rect>
<rect x="715.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#dddddd"/></rect>
<rect x="724.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#ededed"/></rect>
<rect x="732.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f9f9f9"/></rect>
<rect x="741.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="750.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="864.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f9f9f9"/></rect>
<rect x="873.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#ededed"/></rect>
<rect x="882.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#dddddd"/></rect>
<rect x="891.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#cacaca"/></rect>
<rect x="900.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#b4b4b4"/></rect>
<rect x="908.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#9d9d9d"/></rect>
<rect x="917.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#868686"/></rect>
<rect x="680.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#808080"/></rect>
<rect x="688.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#969696"/></rect>
<rect x="697.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#acacac"/></rect>
<rect x="706.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#c2c2c2"/></rect>
<rect x="715.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d6d6d6"/></rect>
<rect x="724.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e7e7e7"/></rect>
<rect x="732.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f4f4f4"/></rect>
<rect x="741.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="750.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="864.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f4f4f4"/></rect>
<rect x="873.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e7e7e7"/></rect>
<rect x="882.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d6d6d6"/></rect>
<rect x="891.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#c2c2c2"/></rect>
<rect x="900.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#acacac"/></rect>
<rect x="908.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#969696"/></rect>
<rect x="917.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#808080"/></rect>
<rect x="680.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#797979"/></rect>
<rect x="688.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8e8e8e"/></rect>
<rect x="697.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a3a3a3"/></rect>
<rect x="706.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#b8b8b8"/></rect>
<rect x="715.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#cccccc"/></rect>
<rect x="724.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#dedede"/></rect>
<rect x="732.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#ececec"/></rect>
<rect x="741.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f7f7f7"/></rect>
<rect x="750.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fdfdfd"/></rect>
<rect x="759.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fdfdfd"/></rect>
<rect x="856.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f7f7f7"/></rect>
<rect x="864.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#ececec"/></rect>
<rect x="873.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#dedede"/></rect>
<rect x="882.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#cccccc"/></rect>
<rect x="891.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#b8b8b8"/></rect>
<rect x="900.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a3a3a3"/></rect>
<rect x="908.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8e8e8e"/></rect>
<rect x="917.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#797979"/></rect>
<rect x="680.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#717171"/></rect>
<rect x="688.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#848484"/></rect>
<rect x="697.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#989898"/></rect>
<rect x="706.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#adadad"/></rect>
<rect x="715.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#c1c1c1"/></rect>
<rect x="724.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d3d3d3"/></rect>
<rect x="732.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e2e2e2"/></rect>
<rect x="741.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#eeeeee"/></rect>
<rect x="750.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f7f7f7"/></rect>
<rect x="759.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="768.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="847.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f7f7f7"/></rect>
<rect x="856.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#eeeeee"/></rect>
<rect x="864.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e2e2e2"/></rect>
<rect x="873.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d3d3d3"/></rect>
<rect x="882.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#c1c1c1"/></rect>
<rect x="891.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#adadad"/></rect>
<rect x="900.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#989898"/></rect>
<rect x="908.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#848484"/></rect>
<rect x="917.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#717171"/></rect>
<rect x="680.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#696969"/></rect>
<rect x="688.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#7a7a7a"/></rect>
<rect x="697.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8d8d8d"/></rect>
<rect x="706.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a0a0a0"/></rect>
<rect x="715.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#b3b3b3"/></rect>
<rect x="724.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#c5c5c5"/></rect>
<rect x="732.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d5d5d5"/></rect>
<rect x="741.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e2e2e2"/></rect>
<rect x="750.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#ededed"/></rect>
<rect x="759.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f5f5f5"/></rect>
<rect x="768.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fafafa"/></rect>
<rect x="776.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="785.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="794.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="803.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="812.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fefefe"/></rect>
<rect x="820.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fcfcfc"/></rect>
<rect x="829.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#fafafa"/></rect>
<rect x="838.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#f5f5f5"/></rect>
<rect x="847.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#ededed"/></rect>
<rect x="856.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#e2e2e2"/></rect>
<rect x="864.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#d5d5d5"/></rect>
<rect x="873.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#c5c5c5"/></rect>
<rect x="882.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#b3b3b3"/></rect>
<rect x="891.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#a0a0a0"/></rect>
<rect x="900.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#8d8d8d"/></rect>
<rect x="908.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#7a7a7a"/></rect>
<rect x="917.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#ffffff;#696969"/></rect>
<rect x="680" y="120" width="246.40000000000003" height="134.4" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="680" y="270" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">暗くなる範囲(10% 以上): 39%</text>
<text x="40" y="372" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2ea043">半径 0.5・柔らかさ 0.8</text>
<text x="40" y="402" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">端の明るさ: 0.52 / 角の明るさ: 0.30</text>
<text x="40" y="428" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">暗くなる範囲: 画面の 39%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4603;0.4605;0.6556;0.6558;1.0000" values="0;0;1;1;0;0"/><rect x="680.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="741.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="750.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="759.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="768.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4e4e4e"/></rect>
<rect x="776.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#575757"/></rect>
<rect x="785.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#606060"/></rect>
<rect x="794.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#666666"/></rect>
<rect x="803.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#666666"/></rect>
<rect x="812.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#606060"/></rect>
<rect x="820.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#575757"/></rect>
<rect x="829.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4e4e4e"/></rect>
<rect x="838.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="847.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="856.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="864.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="873.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="741.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="750.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="759.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#565656"/></rect>
<rect x="768.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#6b6b6b"/></rect>
<rect x="776.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#828282"/></rect>
<rect x="785.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#959595"/></rect>
<rect x="794.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#9e9e9e"/></rect>
<rect x="803.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#9e9e9e"/></rect>
<rect x="812.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#959595"/></rect>
<rect x="820.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#828282"/></rect>
<rect x="829.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#6b6b6b"/></rect>
<rect x="838.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#565656"/></rect>
<rect x="847.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="856.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="864.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="873.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="741.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="750.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#595959"/></rect>
<rect x="759.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#797979"/></rect>
<rect x="768.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#9c9c9c"/></rect>
<rect x="776.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#bbbbbb"/></rect>
<rect x="785.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#d0d0d0"/></rect>
<rect x="794.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#dadada"/></rect>
<rect x="803.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#dadada"/></rect>
<rect x="812.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#d0d0d0"/></rect>
<rect x="820.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#bbbbbb"/></rect>
<rect x="829.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#9c9c9c"/></rect>
<rect x="838.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#797979"/></rect>
<rect x="847.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#595959"/></rect>
<rect x="856.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="864.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="873.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="741.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#545454"/></rect>
<rect x="750.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#777777"/></rect>
<rect x="759.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#a5a5a5"/></rect>
<rect x="768.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#cecece"/></rect>
<rect x="776.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#ebebeb"/></rect>
<rect x="785.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#f9f9f9"/></rect>
<rect x="794.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#fdfdfd"/></rect>
<rect x="803.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#fdfdfd"/></rect>
<rect x="812.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#f9f9f9"/></rect>
<rect x="820.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#ebebeb"/></rect>
<rect x="829.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#cecece"/></rect>
<rect x="838.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#a5a5a5"/></rect>
<rect x="847.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#777777"/></rect>
<rect x="856.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#545454"/></rect>
<rect x="864.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="873.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="741.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#686868"/></rect>
<rect x="750.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#9a9a9a"/></rect>
<rect x="759.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#cdcdcd"/></rect>
<rect x="768.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#f1f1f1"/></rect>
<rect x="776.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#f1f1f1"/></rect>
<rect x="838.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#cdcdcd"/></rect>
<rect x="847.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#9a9a9a"/></rect>
<rect x="856.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#686868"/></rect>
<rect x="864.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="873.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#545454"/></rect>
<rect x="741.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#7e7e7e"/></rect>
<rect x="750.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#b7b7b7"/></rect>
<rect x="759.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#e9e9e9"/></rect>
<rect x="768.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#e9e9e9"/></rect>
<rect x="847.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#b7b7b7"/></rect>
<rect x="856.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#7e7e7e"/></rect>
<rect x="864.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#545454"/></rect>
<rect x="873.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#5c5c5c"/></rect>
<rect x="741.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#8f8f8f"/></rect>
<rect x="750.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#cbcbcb"/></rect>
<rect x="759.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#f7f7f7"/></rect>
<rect x="768.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#f7f7f7"/></rect>
<rect x="847.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#cbcbcb"/></rect>
<rect x="856.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#8f8f8f"/></rect>
<rect x="864.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#5c5c5c"/></rect>
<rect x="873.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#616161"/></rect>
<rect x="741.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#989898"/></rect>
<rect x="750.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#d5d5d5"/></rect>
<rect x="759.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#fcfcfc"/></rect>
<rect x="768.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#fcfcfc"/></rect>
<rect x="847.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#d5d5d5"/></rect>
<rect x="856.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#989898"/></rect>
<rect x="864.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#616161"/></rect>
<rect x="873.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#616161"/></rect>
<rect x="741.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#989898"/></rect>
<rect x="750.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#d5d5d5"/></rect>
<rect x="759.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#fcfcfc"/></rect>
<rect x="768.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#fcfcfc"/></rect>
<rect x="847.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#d5d5d5"/></rect>
<rect x="856.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#989898"/></rect>
<rect x="864.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#616161"/></rect>
<rect x="873.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#5c5c5c"/></rect>
<rect x="741.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#8f8f8f"/></rect>
<rect x="750.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#cbcbcb"/></rect>
<rect x="759.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#f7f7f7"/></rect>
<rect x="768.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#f7f7f7"/></rect>
<rect x="847.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#cbcbcb"/></rect>
<rect x="856.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#8f8f8f"/></rect>
<rect x="864.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#5c5c5c"/></rect>
<rect x="873.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#545454"/></rect>
<rect x="741.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#7e7e7e"/></rect>
<rect x="750.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#b7b7b7"/></rect>
<rect x="759.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#e9e9e9"/></rect>
<rect x="768.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#e9e9e9"/></rect>
<rect x="847.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#b7b7b7"/></rect>
<rect x="856.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#7e7e7e"/></rect>
<rect x="864.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#545454"/></rect>
<rect x="873.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="741.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#686868"/></rect>
<rect x="750.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#9a9a9a"/></rect>
<rect x="759.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#cdcdcd"/></rect>
<rect x="768.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#f1f1f1"/></rect>
<rect x="776.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#f1f1f1"/></rect>
<rect x="838.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#cdcdcd"/></rect>
<rect x="847.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#9a9a9a"/></rect>
<rect x="856.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#686868"/></rect>
<rect x="864.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="873.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="741.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#545454"/></rect>
<rect x="750.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#777777"/></rect>
<rect x="759.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#a5a5a5"/></rect>
<rect x="768.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#cecece"/></rect>
<rect x="776.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#ebebeb"/></rect>
<rect x="785.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#f9f9f9"/></rect>
<rect x="794.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#fdfdfd"/></rect>
<rect x="803.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#fdfdfd"/></rect>
<rect x="812.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#f9f9f9"/></rect>
<rect x="820.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#ebebeb"/></rect>
<rect x="829.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#cecece"/></rect>
<rect x="838.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#a5a5a5"/></rect>
<rect x="847.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#777777"/></rect>
<rect x="856.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#545454"/></rect>
<rect x="864.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="873.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="741.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="750.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#595959"/></rect>
<rect x="759.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#797979"/></rect>
<rect x="768.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#9c9c9c"/></rect>
<rect x="776.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#bbbbbb"/></rect>
<rect x="785.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#d0d0d0"/></rect>
<rect x="794.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#dadada"/></rect>
<rect x="803.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#dadada"/></rect>
<rect x="812.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#d0d0d0"/></rect>
<rect x="820.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#bbbbbb"/></rect>
<rect x="829.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#9c9c9c"/></rect>
<rect x="838.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#797979"/></rect>
<rect x="847.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#595959"/></rect>
<rect x="856.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="864.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="873.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="741.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="750.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="759.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#565656"/></rect>
<rect x="768.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#6b6b6b"/></rect>
<rect x="776.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#828282"/></rect>
<rect x="785.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#959595"/></rect>
<rect x="794.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#9e9e9e"/></rect>
<rect x="803.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#9e9e9e"/></rect>
<rect x="812.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#959595"/></rect>
<rect x="820.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#828282"/></rect>
<rect x="829.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#6b6b6b"/></rect>
<rect x="838.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#565656"/></rect>
<rect x="847.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="856.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="864.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="873.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="724.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="732.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="741.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="750.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="759.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="768.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4e4e4e"/></rect>
<rect x="776.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#575757"/></rect>
<rect x="785.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#606060"/></rect>
<rect x="794.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#666666"/></rect>
<rect x="803.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#666666"/></rect>
<rect x="812.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#606060"/></rect>
<rect x="820.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#575757"/></rect>
<rect x="829.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4e4e4e"/></rect>
<rect x="838.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="847.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="856.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="864.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="873.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="882.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="891.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#ffffff;#4d4d4d"/></rect>
<rect x="680" y="120" width="246.40000000000003" height="134.4" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="680" y="270" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">暗くなる範囲(10% 以上): 80%</text>
<text x="40" y="372" text-anchor="start" style="font-size:20px;font-weight:700;fill:#e5aa28">半径 0.3・柔らかさ 0.3</text>
<text x="40" y="402" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">端の明るさ: 0.30 / 角の明るさ: 0.30</text>
<text x="40" y="428" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">暗くなる範囲: 画面の 80%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6556;0.6558;1.0000" values="0;0;1;1"/><rect x="680.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#8d8d8d"/></rect>
<rect x="724.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#fefefe"/></rect>
<rect x="732.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#fefefe"/></rect>
<rect x="882.4" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#8d8d8d"/></rect>
<rect x="891.2" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="120.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#626262"/></rect>
<rect x="715.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#f0f0f0"/></rect>
<rect x="724.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="732.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="882.4" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#f0f0f0"/></rect>
<rect x="891.2" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#626262"/></rect>
<rect x="900.0" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="128.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#b6b6b6"/></rect>
<rect x="715.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="724.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="732.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="882.4" y="136.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="891.2" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#b6b6b6"/></rect>
<rect x="900.0" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="136.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#5f5f5f"/></rect>
<rect x="706.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#f5f5f5"/></rect>
<rect x="715.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="724.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="732.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="882.4" y="145.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="891.2" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#f5f5f5"/></rect>
<rect x="900.0" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#5f5f5f"/></rect>
<rect x="908.8" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="145.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#929292"/></rect>
<rect x="706.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="715.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="724.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="732.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="882.4" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="891.2" y="153.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="900.0" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#929292"/></rect>
<rect x="908.8" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="153.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#c0c0c0"/></rect>
<rect x="706.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="715.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="724.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="732.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="882.4" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="891.2" y="162.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="900.0" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#c0c0c0"/></rect>
<rect x="908.8" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="162.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#dcdcdc"/></rect>
<rect x="706.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="715.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="724.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="732.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="882.4" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="891.2" y="170.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="900.0" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#dcdcdc"/></rect>
<rect x="908.8" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="170.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4f4f4f"/></rect>
<rect x="697.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#e9e9e9"/></rect>
<rect x="706.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="715.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="724.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="732.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="882.4" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="891.2" y="178.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="900.0" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#e9e9e9"/></rect>
<rect x="908.8" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4f4f4f"/></rect>
<rect x="917.6" y="178.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4f4f4f"/></rect>
<rect x="697.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#e9e9e9"/></rect>
<rect x="706.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="715.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="724.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="732.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="882.4" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="891.2" y="187.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="900.0" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#e9e9e9"/></rect>
<rect x="908.8" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4f4f4f"/></rect>
<rect x="917.6" y="187.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#dcdcdc"/></rect>
<rect x="706.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="715.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="724.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="732.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="882.4" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="891.2" y="195.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="900.0" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#dcdcdc"/></rect>
<rect x="908.8" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="195.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#c0c0c0"/></rect>
<rect x="706.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="715.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="724.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="732.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="882.4" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="891.2" y="204.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="900.0" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#c0c0c0"/></rect>
<rect x="908.8" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="204.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#929292"/></rect>
<rect x="706.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="715.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="724.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="732.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="882.4" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="891.2" y="212.4" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="900.0" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#929292"/></rect>
<rect x="908.8" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="212.4" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#5f5f5f"/></rect>
<rect x="706.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#f5f5f5"/></rect>
<rect x="715.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="724.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="732.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="882.4" y="220.8" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="891.2" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#f5f5f5"/></rect>
<rect x="900.0" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#5f5f5f"/></rect>
<rect x="908.8" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="220.8" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#b6b6b6"/></rect>
<rect x="715.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="724.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="732.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="882.4" y="229.2" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="891.2" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#b6b6b6"/></rect>
<rect x="900.0" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="229.2" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#626262"/></rect>
<rect x="715.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#f0f0f0"/></rect>
<rect x="724.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="732.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="882.4" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#f0f0f0"/></rect>
<rect x="891.2" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#626262"/></rect>
<rect x="900.0" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="237.6" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="688.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="697.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="706.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="715.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#8d8d8d"/></rect>
<rect x="724.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#fefefe"/></rect>
<rect x="732.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="741.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="750.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="759.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="768.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="776.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="785.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="794.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="803.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="812.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="820.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="829.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="838.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="847.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="856.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="864.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"/>
<rect x="873.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#fefefe"/></rect>
<rect x="882.4" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#8d8d8d"/></rect>
<rect x="891.2" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="900.0" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="908.8" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="917.6" y="246.0" width="9.1" height="8.7" fill="#ffffff"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6605" values="#ffffff;#4d4d4d"/></rect>
<rect x="680" y="120" width="246.40000000000003" height="134.4" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="680" y="270" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">暗くなる範囲(10% 以上): 24%</text>
<text x="40" y="372" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb">半径 0.8・柔らかさ 0.1</text>
<text x="40" y="402" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">端の明るさ: 0.30 / 角の明るさ: 0.30</text>
<text x="40" y="428" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">暗くなる範囲: 画面の 24%</text>
</g>
<text x="40" y="470" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">暗くなる範囲(%):</text>
<text x="180" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0835;0.0837;1.0000" values="1;1;0;0"/></text>
<text x="180" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">54<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0835;0.0837;0.2789;0.2791;1.0000" values="0;0;1;1;0;0"/></text>
<text x="180" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">39<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2789;0.2791;0.4742;0.4744;1.0000" values="0;0;1;1;0;0"/></text>
<text x="180" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">80<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4742;0.4744;0.6696;0.6698;1.0000" values="0;0;1;1;0;0"/></text>
<text x="180" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#7c3aed" opacity="0">24<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6696;0.6698;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.8324;0.8326;1.0000" values="0;0;1;1"/><rect x="400" y="440" width="530" height="70" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="416" y="464" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">半径が小さいほど、広い範囲が暗い。柔らかさが小さいほど、境目が硬い</text>
<text x="416" y="487" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">強すぎると、画面が見づらい。ゲームでは、弱めにする</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">端を暗くすると、視線が中央に集まる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">半径と柔らかさで、形を決める<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.8510;0.8512;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ダメージ表現などで、強さを時間で変える使い方もある<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.8510;0.8512;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:vignette-params:end -->

### 物理的な cos⁴

**画面中心からの距離と視野角から、`cos⁴(θ)` で暗くする**と**自然なビネット**になります。

```hlsl
float NaturalVignette(float2 uv, float vertical_fov_radians, float aspect) {
  float2 d = (uv - 0.5) * 2.0;
  float2 tan_half = tan(vertical_fov_radians * 0.5) * float2(aspect, 1.0);
  float2 ray = d * tan_half;
  float cos_theta = rsqrt(1.0 + dot(ray, ray));
  float c2 = cos_theta * cos_theta;
  return c2 * c2;
}
```

物理版のコードの要点です。`tan(fov/2)` は、画面の端に対応する視線の傾きです。`cos θ = 1 / √(1 + tan²)` で、視線の角度の余弦を求めます。`cos⁴` が、物理的なビネットの係数です。

**広角（視野角が大きい）ほど、周辺が暗くなる**ことが**自然**に**再現**されます。

## 形

ビネットの形は 3 種類です。円形は、`roundness` を画面のアスペクト比にして真円にします。楕円（画面に沿う）は、`roundness` を 1 にして、画面の縦横比に沿った楕円にします。四角寄りは、距離に最大ノルム（`max(|x|, |y|)`）を使い、画面の四隅だけをほんのり暗くします。

```hlsl
float BoxVignette(float2 uv, float intensity, float smoothness) {
  float2 d = abs(uv - 0.5) * 2.0;
  float distance_from_center = max(d.x, d.y);
  return 1.0 - smoothstep(1.0 - intensity - smoothness, 1.0, distance_from_center) * intensity;
}
```

## 色付きのビネット

**黒だけでなく、色を付ける**と**演出**になります。

| 色 | 演出 |
| --- | --- |
| **暗い赤** | **体力が少ない・ダメージ・危険** |
| **暗い青** | **水中・夜・冷たさ** |
| **暗い緑** | **毒・ナイト ビジョン** |
| <strong>白（明るい縁）</strong> | **夢・回想・眩しさ** |

```hlsl
float3 ColoredVignette(float3 color, float2 uv, float3 vignette_color) {
  float v = 1.0 - Vignette(uv, kVignetteIntensity, kVignetteSmoothness, kRoundness);
  return lerp(color, vignette_color, v);
}
```

## ゲームでの使い方

| 場面 | 使い方 |
| --- | --- |
| **映画風の常時** | <strong>ごく弱く（0.2〜0.3）</strong> |
| **夜・洞窟** | **強め**（**懐中電灯の円のような**） |
| **体力が低い** | **赤いビネットを体力に応じて濃く** |
| **狙い・ズーム** | <strong>スコープ中は強いビネット（円）</strong> |
| **会話・カットシーン** | **視線を中心に集める** |

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| **`smoothstep` で滑らかに** | **境が見えない** |
| **アスペクト比を補正** | **ウルトラワイドでも形が崩れない** |
| **物理的な cos⁴** | **視野角に応じた、自然な暗さ** |
| **色付きにして演出に使う** | **体力・状態** |
| **トーンマップ後（LDR）で乗算** | **見た目の明るさに直接** |
| **他のパスと統合** | **色収差・グレイン・トーンマップと 1 パス** |
| **オプションで切れる** | **プレイしにくい人のため** |

## よくあるミス

??? failure "ビネットが強すぎて、周辺の敵や UI が見えない"
    <strong>控えめに（0.2〜0.3）</strong>、**オプションで調整**。

??? failure "ウルトラワイドで、ビネットが横に伸びて不自然"
    **アスペクト比を補正**。

??? failure "ビネットの境がはっきり見える"
    **`smoothness` を大きく**し、**`smoothstep`** を使う。

??? failure "UI まで暗くなる"
    **ビネットは UI の前に掛ける**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ビネット ＝ <strong>画面の周辺ほど暗くする</strong>。<strong>視線を中心へ</strong>
    - [x] <strong>物理的な原因は cos⁴θ</strong>（と<strong>レンズの遮り</strong>）
    - [x] <strong>中心からの距離 ＋ `smoothstep`</strong> で<strong>簡単に実装</strong>。<strong>アスペクト比を補正</strong>
    - [x] <strong>色付き</strong>で<strong>体力・水中・毒</strong>などの<strong>演出</strong>
    - [x] <strong>控えめに</strong>。<strong>UI の前に設定で切れる</strong>

## 参考

- Wikipedia, "Vignetting"
- Pharr, Jakob, Humphreys, "Physically Based Rendering"（cos⁴ の法則）
- Unity, "Post-processing: Vignette"

## 関連ページ

- [Lens Effects](index.md)
- [Chromatic Aberration](chromatic-aberration.md)
- [Film Grain](film-grain.md)
- [Color Grading](../color-grading/index.md)
