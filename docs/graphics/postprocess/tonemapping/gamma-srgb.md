---
title: Gamma and HDR Output
tags:
  - 描画
---

# Gamma and HDR Output

<strong>トーンマップの出力は、リニア（光の量に比例）の 0〜1</strong>です。<strong>ディスプレイに出す前に、sRGB の曲線（ガンマ ≒ 2.2）を掛ける</strong>必要があり、これを間違えると画面全体が暗く潰れたり、白っぽくなったりします。HDR ディスプレイでは、さらに別の出力（HDR10・scRGB）になります。このページでは、なぜガンマが要るか・sRGB 変換の位置・レンダー ターゲットの作り方・HDR ディスプレイへの出し方・UI の扱いを説明します。

!!! tip "ポイント"
    - 光の計算は<strong>リニア空間</strong>。<strong>画像やディスプレイは、暗部を細かく持つガンマ空間</strong>。
    - <strong>sRGB 変換はトーンマップの後・最後</strong>。<strong>前にすると暗部が潰れる</strong>。
    - <strong>`_SRGB` 形式のレンダー ターゲット</strong>に<strong>書けば、ハードウェアが自動変換</strong>する。
    - <strong>テクスチャ（色）は `_SRGB` で読む</strong>。<strong>法線・粗さなどのデータは UNORM</strong>。
    - <strong>HDR ディスプレイ</strong>は<strong>別のトーンマップ・別の出力形式</strong>（PQ・Rec.2020）。
    - <strong>UI</strong>は<strong>ペーパー ホワイト</strong>を<strong>別に調整して合成</strong>する。

<!-- fig:gamma-srgb:begin -->

<svg class="fig illust motion" data-fig="gamma-srgb" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-gamma-srgb" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ガンマ: 光の量(線形)の足し算を、ガンマ空間でやると、暗くなる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">白と黒の細かい縞(縞 1 本ごとに 1 画素)を、縮小して平均する。ガンマ空間で平均する場合と、線形に直してから平均する場合</text>
<text x="70.0" y="108" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">元の縞(白 = 光 1、黒 = 光 0。遠くから見ると、光の量は半分)</text>
<rect x="70.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="96.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="122.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="148.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="174.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="200.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="226.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="252.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="278.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="304.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="330.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="356.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="382.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="408.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="434.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="460.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="486.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="512.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="538.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="564.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="590.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="616.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="642.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="668.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="694.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="720.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="746.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="772.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="798.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="824.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="850.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#ffffff"/></rect>
<rect x="876.0" y="114.0" width="26.3" height="26.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#000000"/></rect>
<rect x="70.0" y="114" width="832.0" height="26.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="70.0" y="194" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">sRGB の値のまま平均(間違い)</text>
<rect x="70.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#808080"/></rect>
<rect x="122.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#808080"/></rect>
<rect x="174.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#808080"/></rect>
<rect x="226.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#808080"/></rect>
<rect x="278.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#808080"/></rect>
<rect x="330.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#808080"/></rect>
<rect x="382.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#e5e7eb;#808080"/></rect>
<rect x="434.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1349" values="#e5e7eb;#808080"/></rect>
<rect x="486.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1442" values="#e5e7eb;#808080"/></rect>
<rect x="538.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1535" values="#e5e7eb;#808080"/></rect>
<rect x="590.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1628" values="#e5e7eb;#808080"/></rect>
<rect x="642.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1721" values="#e5e7eb;#808080"/></rect>
<rect x="694.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1814" values="#e5e7eb;#808080"/></rect>
<rect x="746.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1907" values="#e5e7eb;#808080"/></rect>
<rect x="798.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2000" values="#e5e7eb;#808080"/></rect>
<rect x="850.0" y="200.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2093" values="#e5e7eb;#808080"/></rect>
<rect x="70.0" y="200" width="832.0" height="52.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="70.0" y="264" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">線形に直して平均 → sRGB へ戻す(正しい)</text>
<rect x="70.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2558" values="#e5e7eb;#bababa"/></rect>
<rect x="122.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2651" values="#e5e7eb;#bababa"/></rect>
<rect x="174.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2744" values="#e5e7eb;#bababa"/></rect>
<rect x="226.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2837" values="#e5e7eb;#bababa"/></rect>
<rect x="278.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2930" values="#e5e7eb;#bababa"/></rect>
<rect x="330.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3023" values="#e5e7eb;#bababa"/></rect>
<rect x="382.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3116" values="#e5e7eb;#bababa"/></rect>
<rect x="434.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3209" values="#e5e7eb;#bababa"/></rect>
<rect x="486.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3302" values="#e5e7eb;#bababa"/></rect>
<rect x="538.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3395" values="#e5e7eb;#bababa"/></rect>
<rect x="590.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3488" values="#e5e7eb;#bababa"/></rect>
<rect x="642.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3581" values="#e5e7eb;#bababa"/></rect>
<rect x="694.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3674" values="#e5e7eb;#bababa"/></rect>
<rect x="746.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3767" values="#e5e7eb;#bababa"/></rect>
<rect x="798.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3860" values="#e5e7eb;#bababa"/></rect>
<rect x="850.0" y="270.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3953" values="#e5e7eb;#bababa"/></rect>
<rect x="70.0" y="270" width="832.0" height="52.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="70.0" y="336" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">参照: 光が半分の灰色(sRGB で 186 / 255)</text>
<rect x="70.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="122.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="174.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="226.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="278.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="330.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="382.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="434.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="486.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="538.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="590.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="642.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="694.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="746.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="798.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="850.0" y="342.0" width="52.3" height="52.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#e5e7eb;#bababa"/></rect>
<rect x="70.0" y="342" width="832.0" height="52.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="30" y="414" width="900" height="80" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="404" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">平均後の光の量(1 = 白、本当は 0.50)</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6277;0.6279;1.0000" values="0;0;1;1"/><text x="50" y="450" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">sRGB の値のまま平均</text>
<text x="50" y="478" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d">0.22(本当の光の 44%)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6975;0.6977;1.0000" values="0;0;1;1"/><text x="500" y="450" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">線形に直して平均 → sRGB へ戻す</text>
<text x="500" y="478" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2ea043">0.50(本当の光の 100%)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">画像の値は、暗い所を細かく表すように、ガンマ(約 2.2 乗)で保存されている<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">縮小(平均)を、2 通りでやってみる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.6277;0.6279;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光の足し算は、線形でやらないと、暗くなる(縮小、ブルーム、ブレンドすべて)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6277;0.6279;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:gamma-srgb:end -->

## なぜガンマがあるのか

<strong>人間の目は暗い所の違いに敏感</strong>で<strong>明るい所の違いには鈍感</strong>です。8 ビット（256 段階）に、明るさを比例で割り当てると、暗部の段階が少なすぎて、縞（バンディング）が出ます。そこで暗部に多くの段階を割り当てる曲線（ガンマ）をかけて保存します。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="ガンマ曲線">
<text x="20" y="26" class="fig-title">リニアと sRGB：同じ 8 ビットでも、暗部の段階が増える</text>
<line x1="80" y1="240" x2="420" y2="240" stroke="currentColor" stroke-opacity="0.5"/><line x1="80" y1="50" x2="80" y2="240" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5 4" points="80,240 420,50"/>
<polyline fill="none" stroke="#2563eb" stroke-width="4" points="80,240 90,215 110,190 140,165 180,140 230,115 290,92 350,70 420,50"/>
<text x="425" y="56" style="font-size:12px">sRGB（ガンマ）</text><text x="425" y="240" style="font-size:12px;fill:#64748b">リニアの値 →</text>
<text x="40" y="150" style="font-size:12px">保存値</text>
<g font-size="13">
<text x="480" y="90" style="font-weight:700">リニア値 0.2 を保存すると</text>
<text x="480" y="114">・sRGB なら 約 0.48（0〜255 で 約 124）</text>
<text x="480" y="138">・暗部（0〜0.2）に 約 124 段階を使える</text>
<text x="480" y="172" style="font-weight:700">ガンマが無いと</text>
<text x="480" y="196" style="font-size:12px">・暗部（0〜0.2）は約 51 段階 → 縞</text>
</g>
</svg>

色の空間は 2 つに使い分けます。<strong>リニア</strong>は、光の計算・合成・ブルーム・トーンマップに使います。物理的に正しい足し算ができるからです。<strong>sRGB（ガンマ）</strong>は、保存と表示に使います（画像ファイルとディスプレイ）。

## 変換の位置

変換の位置は、次のとおりです。色のテクスチャの読み込みでは、sRGB からリニアへ変換します（`_SRGB` 形式で自動）。ライティング・露出・ブルーム・トーンマップは、リニアで行います。画面への出力で、リニアから sRGB へ変換します（最後に、`_SRGB` の RTV で自動）。

<strong>ガンマ変換をトーンマップの前に入れる</strong>と、<strong>暗部が潰れて眠い絵</strong>になります（典型的な事故）。

## sRGB の式

<div class="formula">
sRGB(c) = 12.92 · c　　（c ≦ 0.0031308）<br>
sRGB(c) = 1.055 · c^(1/2.4) − 0.055　　（それ以外）
</div>

```hlsl
float3 LinearToSRGB(float3 c) {
  float3 low = c * 12.92;
  float3 high = 1.055 * pow(max(c, 0.0), 1.0 / 2.4) - 0.055;
  return (c <= 0.0031308) ? low : high;
}

float3 SRGBToLinear(float3 c) {
  float3 low = c / 12.92;
  float3 high = pow((c + 0.055) / 1.055, 2.4);
  return (c <= 0.04045) ? low : high;
}
```

ガンマ変換の近似は 2 通りです。`pow(c, 1/2.2)` はよく使われる近似ですが、暗部で少しずれます。正確な sRGB は、区分式を使う方法で、ハードウェアの自動変換もこちらです。

## DX11 での設定

```cpp
DXGI_SWAP_CHAIN_DESC1 desc = {};
desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;

D3D11_RENDER_TARGET_VIEW_DESC rtv_desc = {};
rtv_desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
rtv_desc.ViewDimension = D3D11_RTV_DIMENSION_TEXTURE2D;
device->CreateRenderTargetView(back_buffer.Get(), &rtv_desc, rtv.GetAddressOf());
```

出力設定の要点です。スワップチェーンの形式は UNORM にします。FLIP モデルでは `_SRGB` のスワップチェーンが作れないので、RTV だけを `_SRGB` にします。RTV を `_SRGB` にすると、シェーダーのリニアな出力を、ハードウェアが sRGB に変換して書き込みます。RTV が `_SRGB` なのにシェーダーで `pow` もすると、二重にガンマがかかって白っぽくなるので、シェーダーでは `pow` しません。

### テクスチャの読み込み

| テクスチャ | 形式 | 理由 |
| --- | --- | --- |
| <strong>アルベド（色）</strong> | `_SRGB` | 画像が sRGB で保存されているので、読み込み時にリニアへ |
| 法線マップ | <strong>UNORM（リニア）</strong> | データであって、色ではない |
| 粗さ・金属度・AO | UNORM | 同上 |
| HDR テクスチャ | FLOAT | すでにリニア |

## HDR ディスプレイへの出力

<strong>HDR ディスプレイは、SDR より広い明るさ（数百〜数千ニト）と広い色域</strong>を<strong>出せます</strong>。SDR 用のトーンマップの結果をそのまま送ると、HDR の良さが活きません。

| 項目 | 内容 |
| --- | --- |
| 色空間 | Rec.2020（広い色域） |
| 伝達関数 | <strong>PQ（ST.2084）</strong>：絶対的な明るさ（ニト）を、10 ビットに効率よく入れる曲線 |
| スワップチェーン形式 | <strong>`R10G10B10A2_UNORM`（HDR10）</strong>、または <strong>`R16G16B16A16_FLOAT`（scRGB）</strong> |
| 色空間の設定 | `IDXGISwapChain3::SetColorSpace1` で `DXGI_COLOR_SPACE_RGB_FULL_G2084_NONE_P2020` |
| トーンマップ | ディスプレイの最大輝度（ニト）に合わせた HDR 用の曲線。SDR 用とは別 |

```cpp
swap_chain->SetColorSpace1(DXGI_COLOR_SPACE_RGB_FULL_G2084_NONE_P2020);
```

```hlsl
float3 LinearToPQ(float3 nits) {
  const float m1 = 0.1593017578125;
  const float m2 = 78.84375;
  const float c1 = 0.8359375;
  const float c2 = 18.8515625;
  const float c3 = 18.6875;
  float3 y = pow(nits / 10000.0, m1);
  return pow((c1 + c2 * y) / (1.0 + c3 * y), m2);
}
```

コードの要点です。`nits / 10000` は、PQ が 10,000 ニトを 1 とするためです。最大輝度は `IDXGIOutput6::GetDesc1` でディスプレイの値を得て、曲線のロールオフに使います。

### ペーパー ホワイトと UI

<strong>HDR では、「白」の明るさに決まりがありません</strong>。<strong>UI の白をゲーム画面の最大輝度で出すと、まぶしすぎる</strong>ので、UI の白を「ペーパー ホワイト」（約 200〜300 ニト）に決め、ゲーム画面とは別に変換して合成します。

HDR での UI の扱いです。ゲーム画面は、HDR 用トーンマップで PQ にします。UI は、ペーパー ホワイトに合わせたニトに変換してから合成します。ユーザー設定として、最大輝度とペーパー ホワイトを調整できるようにします。

## よくあるミス

??? failure "ガンマ変換を二重にして、全体が白っぽい"
    <strong>RTV が `_SRGB` なら、シェーダーで `pow` しない</strong>。

??? failure "ガンマ変換が無くて、全体が暗く潰れる"
    <strong>リニアのまま UNORM に書いている</strong>。<strong>`_SRGB` の RTV にする</strong>。

??? failure "法線マップを `_SRGB` で読んで、ライティングが崩れる"
    <strong>データのテクスチャは UNORM</strong>。

??? failure "SDR 用の曲線を HDR ディスプレイにそのまま出して、地味"
    <strong>HDR 用のトーンマップ</strong>と<strong>PQ の出力</strong>を使う。

??? failure "HDR で UI がまぶしすぎる"
    <strong>ペーパー ホワイトを決めて、UI を別に変換</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>計算はリニア、保存・表示は sRGB</strong>。<strong>ガンマは最後</strong>
    - [x] <strong>RTV を `_SRGB`</strong> にすれば<strong>自動変換</strong>。<strong>シェーダーで `pow` しない</strong>
    - [x] <strong>色テクスチャは `_SRGB`、データは UNORM</strong>
    - [x] <strong>HDR ディスプレイ</strong>は<strong>別のトーンマップ ＋ PQ ＋ Rec.2020</strong>
    - [x] <strong>UI はペーパー ホワイト</strong>で<strong>別に合成</strong>

## 参考

- Microsoft, "DXGI Color Space"・"High Dynamic Range and Wide Color Gamut"（Microsoft Learn）
- SMPTE ST 2084, "High Dynamic Range Electro-Optical Transfer Function"
- IEC 61966-2-1, "sRGB"

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [Exposure](exposure.md)
- [Color Grading](../color-grading/index.md)
- [画面に出す](../../../3d/render-flow/present.md)
