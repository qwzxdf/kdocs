---
title: Translucent Shadows
tags:
  - 描画
---

# Translucent Shadows

ガラスの窓、ステンド グラス、煙、薄い布は光を一部だけ通します。ところが、シャドウ マップは深度しか持たないので、「光が通る」か「完全に遮られる」かの 2 択になります。ガラスを不透明として描くと真っ黒な影になって、描かなければ影がありません。どちらも現実と違います。

<strong>半透明の影は深度だけでは表せないので確率、色、層の 3 つの近似で補います</strong>。このページでは影を落とさない方法、アルファで確率的に落とす方法、色付きの影、深度ごとの透過率を持つ方法を使い分けとともに説明します。

!!! tip "ポイント"
    - 深度は「あるか・ないか」しか表せません。半透明の薄い影は近似が必要です。
    - 確率的な影はアルファの割合の画素だけを書き込みます。PCF や TAA で平均すると、薄い影に見えます。
    - 色付きの影は半透明の物の透過色を別のマップに乗算で積みます。ステンド グラスのような影になります。
    - 煙や髪のように層が重なる物は、深度ごとの透過率を持つ方法（Opacity Shadow Maps など）を使います。
    - 無色の窓ガラスは影を落とさないだけで十分なことが多いです。

!!! info "このページを読む前に"
    - [Special Cases](index.md)（このセクション全体の地図と読む順番）

## 半透明の影の問題 {#problem}

現実の影は物の種類で違います。無色のガラスの影はほぼ透明で、わずかに暗いだけです。色付きガラスは色付きの影を落とします。煙は密度に比例した薄い影です。

通常のシャドウ マップで描いた場合は、次のようになります。

- 不透明として描くとどれも真っ黒な影になります。間違いです。
- 描かないとどれも影がなくなります。無色のガラスではそれが近い結果になります。

## 方法 1: 影を落とさない {#skip}

半透明の物をシャドウ パスで描きません。無色のガラスや薄い物はこれで十分なことが多いです。実装はマテリアルのフラグでシャドウ パスから外すだけです。

## 方法 2: アルファに応じた確率的な影 {#stochastic}

アルファ 0.3 の物を 30 % の画素だけ不透明として、シャドウ マップに描きます。PCF で読むと平均されて約 30 % の濃さの影になります（[Hashed Alpha](../../translucency/alpha-test/hashed-alpha.md)）。ディザ（市松）のように一部の画素を抜いて透けさせる考え方は、スクリーン ドアとも呼ばれます。

<!-- fig:stipple-shadow:begin -->

<svg class="fig illust motion" data-fig="stipple-shadow" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-stipple-shadow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">半透明の影: 透明度に応じて、シャドウ マップに「点描」で書き込み、PCF でなめらかにする</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 24 マスの影の表に透明度の違う 3 枚の板の影を書く。点描のパターンのままだと粗いが、PCF で平均すると、薄い影になる</text>
<text x="60.0" y="100" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">① 透明度の違う 3 枚(α = 0.25、0.5、0.8)</text>
<rect x="60.0" y="108" width="238.0" height="22" fill="#94a3b8" fill-opacity="0.25"/>
<text x="180.0" y="124" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">α = 0.25</text>
<rect x="300.0" y="108" width="238.0" height="22" fill="#94a3b8" fill-opacity="0.5"/>
<text x="420.0" y="124" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">α = 0.50</text>
<rect x="540.0" y="108" width="238.0" height="22" fill="#94a3b8" fill-opacity="0.8"/>
<text x="660.0" y="124" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">α = 0.80</text>
<rect x="52.0" y="150" width="736.0" height="134" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="52.0" y="140" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 影の表への書き込み(黒 = 書く、白 = 書かない)</text>
<rect x="60.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0732" values="#ffffff;#334155"/></rect>
<rect x="90.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="120.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0878" values="#ffffff;#334155"/></rect>
<rect x="150.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="180.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1024" values="#ffffff;#334155"/></rect>
<rect x="210.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="240.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1171" values="#ffffff;#334155"/></rect>
<rect x="270.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="300.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1317" values="#ffffff;#334155"/></rect>
<rect x="330.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="360.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1463" values="#ffffff;#334155"/></rect>
<rect x="390.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="420.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1610" values="#ffffff;#334155"/></rect>
<rect x="450.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="480.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1756" values="#ffffff;#334155"/></rect>
<rect x="510.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="540.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1902" values="#ffffff;#334155"/></rect>
<rect x="570.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1976" values="#ffffff;#334155"/></rect>
<rect x="600.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2049" values="#ffffff;#334155"/></rect>
<rect x="630.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2122" values="#ffffff;#334155"/></rect>
<rect x="660.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2195" values="#ffffff;#334155"/></rect>
<rect x="690.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2268" values="#ffffff;#334155"/></rect>
<rect x="720.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2341" values="#ffffff;#334155"/></rect>
<rect x="750.0" y="158.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2415" values="#ffffff;#334155"/></rect>
<rect x="60.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="90.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="120.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="150.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="180.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="210.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="240.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="270.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="300.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="330.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1390" values="#ffffff;#334155"/></rect>
<rect x="360.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="390.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1537" values="#ffffff;#334155"/></rect>
<rect x="420.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="450.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1683" values="#ffffff;#334155"/></rect>
<rect x="480.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="510.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1829" values="#ffffff;#334155"/></rect>
<rect x="540.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1902" values="#ffffff;#334155"/></rect>
<rect x="570.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1976" values="#ffffff;#334155"/></rect>
<rect x="600.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="630.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2122" values="#ffffff;#334155"/></rect>
<rect x="660.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2195" values="#ffffff;#334155"/></rect>
<rect x="690.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2268" values="#ffffff;#334155"/></rect>
<rect x="720.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="750.0" y="188.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2415" values="#ffffff;#334155"/></rect>
<rect x="60.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0732" values="#ffffff;#334155"/></rect>
<rect x="90.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="120.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0878" values="#ffffff;#334155"/></rect>
<rect x="150.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="180.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1024" values="#ffffff;#334155"/></rect>
<rect x="210.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="240.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1171" values="#ffffff;#334155"/></rect>
<rect x="270.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="300.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1317" values="#ffffff;#334155"/></rect>
<rect x="330.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="360.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1463" values="#ffffff;#334155"/></rect>
<rect x="390.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="420.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1610" values="#ffffff;#334155"/></rect>
<rect x="450.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="480.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1756" values="#ffffff;#334155"/></rect>
<rect x="510.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="540.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1902" values="#ffffff;#334155"/></rect>
<rect x="570.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1976" values="#ffffff;#334155"/></rect>
<rect x="600.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2049" values="#ffffff;#334155"/></rect>
<rect x="630.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2122" values="#ffffff;#334155"/></rect>
<rect x="660.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2195" values="#ffffff;#334155"/></rect>
<rect x="690.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2268" values="#ffffff;#334155"/></rect>
<rect x="720.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2341" values="#ffffff;#334155"/></rect>
<rect x="750.0" y="218.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2415" values="#ffffff;#334155"/></rect>
<rect x="60.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="90.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="120.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="150.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="180.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="210.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="240.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="270.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="300.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="330.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1390" values="#ffffff;#334155"/></rect>
<rect x="360.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="390.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1537" values="#ffffff;#334155"/></rect>
<rect x="420.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="450.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1683" values="#ffffff;#334155"/></rect>
<rect x="480.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="510.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1829" values="#ffffff;#334155"/></rect>
<rect x="540.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="570.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1976" values="#ffffff;#334155"/></rect>
<rect x="600.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="630.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2122" values="#ffffff;#334155"/></rect>
<rect x="660.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="690.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2268" values="#ffffff;#334155"/></rect>
<rect x="720.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"/>
<rect x="750.0" y="248.0" width="30.3" height="30.3" fill="#ffffff"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2415" values="#ffffff;#334155"/></rect>
<rect x="60.0" y="158" width="720.0" height="120.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="318" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">③ 平均する(PCF): 4 マス × 4 行</text>
<rect x="60.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2780" values="#e5e7eb;#9f9f9f"/></rect>
<rect x="90.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2820" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="120.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2859" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="150.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="180.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2937" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="210.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2976" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="240.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3015" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="270.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3054" values="#e5e7eb;#9f9f9f"/></rect>
<rect x="300.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3093" values="#e5e7eb;#9f9f9f"/></rect>
<rect x="330.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3132" values="#e5e7eb;#808080"/></rect>
<rect x="360.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3171" values="#e5e7eb;#808080"/></rect>
<rect x="390.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3210" values="#e5e7eb;#808080"/></rect>
<rect x="420.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3249" values="#e5e7eb;#808080"/></rect>
<rect x="450.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3288" values="#e5e7eb;#808080"/></rect>
<rect x="480.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3327" values="#e5e7eb;#707070"/></rect>
<rect x="510.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3366" values="#e5e7eb;#505050"/></rect>
<rect x="540.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3405" values="#e5e7eb;#505050"/></rect>
<rect x="570.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3444" values="#e5e7eb;#303030"/></rect>
<rect x="600.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3483" values="#e5e7eb;#303030"/></rect>
<rect x="630.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3522" values="#e5e7eb;#303030"/></rect>
<rect x="660.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3561" values="#e5e7eb;#303030"/></rect>
<rect x="690.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3600" values="#e5e7eb;#303030"/></rect>
<rect x="720.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3639" values="#e5e7eb;#202020"/></rect>
<rect x="750.0" y="326.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3678" values="#e5e7eb;#202020"/></rect>
<rect x="60.0" y="326" width="720.0" height="30.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="378" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">④ 本当の影の濃さ(正解)</text>
<rect x="60.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2780" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="90.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2820" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="120.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2859" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="150.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2898" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="180.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2937" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="210.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2976" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="240.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3015" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="270.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3054" values="#e5e7eb;#bfbfbf"/></rect>
<rect x="300.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3093" values="#e5e7eb;#808080"/></rect>
<rect x="330.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3132" values="#e5e7eb;#808080"/></rect>
<rect x="360.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3171" values="#e5e7eb;#808080"/></rect>
<rect x="390.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3210" values="#e5e7eb;#808080"/></rect>
<rect x="420.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3249" values="#e5e7eb;#808080"/></rect>
<rect x="450.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3288" values="#e5e7eb;#808080"/></rect>
<rect x="480.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3327" values="#e5e7eb;#808080"/></rect>
<rect x="510.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3366" values="#e5e7eb;#808080"/></rect>
<rect x="540.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3405" values="#e5e7eb;#333333"/></rect>
<rect x="570.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3444" values="#e5e7eb;#333333"/></rect>
<rect x="600.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3483" values="#e5e7eb;#333333"/></rect>
<rect x="630.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3522" values="#e5e7eb;#333333"/></rect>
<rect x="660.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3561" values="#e5e7eb;#333333"/></rect>
<rect x="690.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3600" values="#e5e7eb;#333333"/></rect>
<rect x="720.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3639" values="#e5e7eb;#333333"/></rect>
<rect x="750.0" y="386.0" width="30.3" height="30.3" fill="#e5e7eb"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3678" values="#e5e7eb;#333333"/></rect>
<rect x="60.0" y="386" width="720.0" height="30.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.4008;0.4010;1.0000" values="0;0;1;1"/><rect x="60" y="436" width="840" height="74" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="76" y="460" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">正解とのずれ: 点描のまま(縦に平均)0.146 → PCF 0.040</text>
<text x="76" y="484" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">点描は、1 マスに 0 か 1 しか書けない。周りの平均で、薄い影を作る(特別なテクスチャは不要)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">シャドウ マップは「物がある / ない」の 2 値。薄い影は書けない<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0730;0.0732;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">透明度を点描(しきい値との比較)で、書く / 書かないに変える<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0730;0.0732;0.2779;0.2780;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">PCF で平均すると、点描が混ざって、薄い影になる<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2779;0.2780;0.4008;0.4010;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">透明度に近い濃さになる<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.4008;0.4010;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:stipple-shadow:end -->

アルファが小さいほど深度が書かれにくくなります。

```hlsl
Texture2D<float4> g_albedo : register(t0);
SamplerState g_linear_wrap : register(s0);

cbuffer MaterialConstants : register(b0) {
  float g_opacity;           // マテリアル全体の不透明度 0..1
  float3 _pad;
};

// 画面上の位置から、決定的に 0..1 のしきい値を作る（ベイヤー 4×4）
float Bayer4x4(float2 pixel) {
  static const float kBayer[16] = {
     0,  8,  2, 10,
    12,  4, 14,  6,
     3, 11,  1,  9,
    15,  7, 13,  5};
  uint2 p = uint2(pixel) & 3;
  return (kBayer[p.y * 4 + p.x] + 0.5) / 16.0;
}

// シャドウ パス（深度だけ書く）。しきい値より小さいアルファの画素は捨てる
void StochasticShadowPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) {
  float alpha = g_albedo.Sample(g_linear_wrap, uv).a * g_opacity;
  clip(alpha - Bayer4x4(pos.xy));
}
```

`clip` は引数が負の画素を捨てます。アルファが 0.3 ならしきい値が 0.3 未満の画素（16 個のうち約 5 個）だけが、深度を書きます。

数字で確かめます。PCF が 4 × 4 の 16 サンプルなら不透明な画素の数は 0 から 16 まで整数でしか変わりません。アルファ 0.3 の期待値は `16 × 0.3 = 4.8` 個で、5 個と 4 個の間で揺れます。ランダムに選ぶ場合の標準偏差は `sqrt(0.3 × 0.7 / 16) ≒ 0.115` で、影の濃さが 0.3 ± 0.12 ほどばらつきます。ベイヤー行列のような規則的なパターンならばらつきが減りますが、模様が見えます。TAA を併用してフレーム間で平均すると、さらに目立たなくなります。

長所は簡単なことです。PCF がそのまま使えて半透明の度合いが反映されます。短所はノイズが出ることと色が反映されないこと（影がグレーになること）です。

## 方法 3: 色付きの影 {#colored}

色付きガラスの影はガラスの色に染まります。光がガラスを通る間に一部の色が吸収されて、ガラスの色だけが残るからです。この影を作るにはシャドウ マップを 2 枚使います。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="不透明の深度と、半透明の透過色の 2 枚のマップを使い、ガラスより奥の画素だけ光を染める"><defs><marker id="tsA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">2 枚のマップで、遮る影と染める影を分ける</text>
<rect x="20" y="50" width="200" height="70" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="120" y="78" text-anchor="middle" style="font-size:13px;font-weight:600">① 不透明の深度</text><text x="120" y="98" text-anchor="middle" style="font-size:12px">光を遮る（0 か 1）</text>
<rect x="20" y="136" width="200" height="70" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="120" y="164" text-anchor="middle" style="font-size:13px;font-weight:600">② 透過色 ＋ ガラスの深度</text><text x="120" y="184" text-anchor="middle" style="font-size:12px">乗算で積む（RGB）</text>
<line x1="220" y1="85" x2="300" y2="115" stroke="currentColor" stroke-width="2" marker-end="url(#tsA)"/><line x1="220" y1="171" x2="300" y2="140" stroke="currentColor" stroke-width="2" marker-end="url(#tsA)"/>
<rect x="302" y="86" width="190" height="70" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="397" y="114" text-anchor="middle" style="font-size:13px;font-weight:600">メイン パス</text><text x="397" y="134" text-anchor="middle" style="font-size:12px">光 = 色 × 透過色 × 遮り</text>
<line x1="492" y1="121" x2="540" y2="121" stroke="currentColor" stroke-width="2" marker-end="url(#tsA)"/>
<rect x="542" y="86" width="160" height="70" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="622" y="114" text-anchor="middle" style="font-size:12px">ガラスの奥だけ</text><text x="622" y="134" text-anchor="middle" style="font-size:12px">色付きの光になる</text>
<text x="360" y="236" text-anchor="middle" style="font-size:12px">ガラスより手前にある物は、染めない（深度で判定する）</text></svg>

まず、半透明のシャドウ パスです。光の透過色を乗算ブレンドで積みます。ブレンドは `SrcBlend = ZERO`、`DestBlend = SRC_COLOR` で現在の値に出力色を掛けます。レンダー ターゲットは先に `(1, 1, 1)` でクリアしておきます。

```hlsl
// 半透明のシャドウ パス: 光の透過色を乗算で積む（RGB のレンダー ターゲット）
float4 ColorShadowPS(float4 pos : SV_Position, float2 uv : TEXCOORD0) : SV_Target {
  float4 tint = g_albedo.Sample(g_linear_wrap, uv);
  // アルファが小さい（透明）ほど白（影響なし）、大きいほどガラスの色
  float3 transmit = lerp(float3(1, 1, 1), tint.rgb, tint.a);
  return float4(transmit, 1.0);
}
```

2 枚重なると透過色が掛け算で重なります。アルファ 0.5 の赤（`(1, 0, 0)`）なら 1 枚の透過色は `lerp(1, (1,0,0), 0.5) = (1, 0.5, 0.5)` です。2 枚重ねると `(1, 0.25, 0.25)` で赤が強くなります。

メイン パスでは不透明の影で光を遮って、半透明の影の色で光を染めます。

```hlsl
Texture2D<float> g_opaque_shadow : register(t1);
SamplerComparisonState g_shadow_sampler : register(s1);
Texture2D<float3> g_translucent_shadow : register(t2);   // 透過色
Texture2D<float> g_translucent_depth : register(t3);     // 半透明の最も手前の深度
SamplerState g_linear_clamp : register(s2);

cbuffer LightConstants : register(b1) {
  float4x4 g_world_to_light;
  float3 g_light_color;
  float _pad1;
};

float4 ShadeWithColoredShadowPS(float3 world_pos : TEXCOORD0) : SV_Target {
  float4 clip = mul(float4(world_pos, 1.0), g_world_to_light);
  float3 ndc = clip.xyz / clip.w;
  float2 uv = float2(ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5);

  // 不透明の影: 光を遮る（PCF 込みの比較で 0..1 が返る）
  float opaque_lit = g_opaque_shadow.SampleCmpLevelZero(g_shadow_sampler, uv, ndc.z - 0.001);

  // 半透明の影: 光を染める。ガラスより奥の画素だけ受ける
  float3 tint = g_translucent_shadow.SampleLevel(g_linear_clamp, uv, 0);
  float glass_depth = g_translucent_depth.SampleLevel(g_linear_clamp, uv, 0);
  float3 light = (ndc.z > glass_depth) ? g_light_color * tint : g_light_color;

  return float4(light * opaque_lit, 1.0);        // 本来は、これにライティングの計算を掛ける
}
```

「画素がガラスの奥にあるか」の判定のためにガラスの深度（半透明な物の最も手前の深度）を別に持ちます。

## 方法 4: 深度ごとの透過率を持つ {#layers}

煙、髪、葉のように半透明の物が何枚も重なると、光は層を順に通って奥へ進むほど減っていきます。深度ごとの光の通過率をマップに持つ方法です。

- Deep Shadow Maps（Lokovic と Veach、2000）は画素ごとに深度に対する透過率の関数（区分的な線形）を保存します。映画のレンダリングで使われました。
- Opacity Shadow Maps（Kim と Neumann、2001）は深度を複数の層（スライス）に分けて、各層での累積した不透明度をテクスチャに保存します。

```text
Opacity Shadow Maps:
   層 1（手前） 層 2    層 3    層 4（奥）
   ┌────┐     ┌────┐  ┌────┐  ┌────┐     各層に、そこまでの累積した不透明度を保存
   │ 0.2│     │ 0.5│  │ 0.8│  │ 0.9│
   └────┘     └────┘  └────┘  └────┘
画素の深度が層 3 と 4 の間 → 2 つの不透明度を補間 → 約 0.85 の影
```

保存する値は深度に対する不透明度 `α(z)` です。光の通過率は `1 − α(z)` です。たとえば、画素の深度が層 3（0.8）と層 4（0.9）の真ん中なら補間して 0.85 で、通過率は 0.15 です。光の 15 % だけが届きます。

```hlsl
Texture2DArray<float> g_opacity_layers : register(t4);    // 層ごとの累積不透明度
static const int kLayers = 4;

// 画素の深度（0..1）から、層の間を補間した、累積の不透明度を返す
float OpacityAtDepth(float2 uv, float depth01) {
  float f = saturate(depth01) * (kLayers - 1);   // 0 .. kLayers-1 の層の座標
  int l0 = (int)floor(f);
  int l1 = min(l0 + 1, kLayers - 1);
  float t = f - l0;
  float a0 = g_opacity_layers.SampleLevel(g_linear_clamp, float3(uv, l0), 0);
  float a1 = g_opacity_layers.SampleLevel(g_linear_clamp, float3(uv, l1), 0);
  return lerp(a0, a1, t);
}

float TransmittanceFromLayers(float2 uv, float depth01) {
  return 1.0 - OpacityAtDepth(uv, depth01);       // 通過率。影の濃さは 1 - これ
}
```

実装は複雑でメモリも重くなります。層の数だけテクスチャが要るからです。層が少ないと層と層の間の補間で、境目の縞が出ます。髪（[Hair Shadows](../../skin-hair/hair/shadows.md)）や煙・雲（[Cloud Shadows](../../atmosphere/clouds/shadows.md)）など、半透明の層が密に重なる物で使われます。

!!! note "確かめた範囲"
    HLSL は `fxc`（`ps_5_0`）で `StochasticShadowPS`、`ColorShadowPS`、`ShadeWithColoredShadowPS` とレイヤーの補間関数をコンパイルして、エラーが出ないことを確かめました。確率の標準偏差は手計算です。GPU での描画は確認していません。

## 使い分け {#choice}

- 無色の窓ガラスは影を落としません（方法 1）。
- 薄い布や半透明の植物は確率的な影にします（方法 2）。
- 色付きガラスやステンド グラスは、色付きの影にします（方法 3）。重要な演出のときだけです。
- 煙や霧やパーティクルは確率的な影かボリューム ライティングにします（[Volumetric Fog](../../atmosphere/volumetric-fog/index.md)）。
- 髪や雲のように層が密に重なる物は、Deep か Opacity シャドウ マップ、または専用の手法です。

レイトレーシングの影なら Any-Hit シェーダーで透過率を累積できます（[Ray-Traced Shadows](../ray-traced.md)）。

## よくあるミス {#mistakes}

??? failure "ガラスが、真っ黒な影を落とす"
    原因は半透明の物を不透明と同じ深度パスで描いていることです。半透明の物をシャドウ パスから外すかアルファで `clip` する確率的な影にします。

??? failure "確率的な影が、ざらざらしてちらつく"
    原因はノイズがフレームごとに変わるのに、平均していないことです。PCF のカーネルを広げるか TAA で時間方向にならします。規則的なパターン（ベイヤー）に替えると、ちらつきは減りますが模様が出ます。

??? failure "色付きの影が、ガラスの手前の物まで染める"
    原因はガラスの深度を比べていないことです。ガラスより奥の画素だけが光を受けます。ガラスの深度を別に持って画素の深度と比べます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 深度のシャドウ マップは、半透明の薄い影を表せません。
    - [x] 確率的な影はアルファの割合だけ書き込んで、PCF と TAA で平均します。
    - [x] 色付きの影は透過色を乗算で積んだ別のマップで作ります。
    - [x] 層が重なる物は深度ごとの透過率を持ちます。

## 参考 {#references}

このページは次の資料を読まずに書きました。式と HLSL は一般的な考え方から自分で書いたもので、`fxc` でのコンパイルまで確かめています。

- Lokovic, Veach, "Deep Shadow Maps", SIGGRAPH 2000（半透明の影）
- Kim, Neumann, "Opacity Shadow Maps", Eurographics Workshop on Rendering 2001
- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018

## 関連ページ

- [Special Cases](index.md)
- [Alpha Blending and Sorting](../../translucency/blending-sorting/index.md)
