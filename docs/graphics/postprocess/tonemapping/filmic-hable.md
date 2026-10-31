---
title: Filmic (Hable)
tags:
  - 描画
---

# Filmic (Hable)

<strong>フィルミック</strong>は、フィルムの感光特性に似た S 字カーブでトーンマップする方式です。Uncharted 2 で使われた Hable の式が有名で、暗部を締め（黒を沈め）、中間にコントラストを付け、明部をなだらかにロールオフします。Reinhard の眠さが消え、映画のような絵になります。このページでは、S 字の 3 つの領域（つま先・直線部・肩）・Hable の式と各係数の意味・白点・露出との関係・自分で曲線を調整する方法を説明します。

!!! tip "ポイント"
    - フィルミック ＝ <strong>S 字の曲線</strong>。<strong>つま先（暗部）→ 直線部（中間）→ 肩（明部）</strong>の 3 領域。
    - つま先で暗部を締めて黒を沈め、肩で明部を滑らかに飽和させる。
    - Hable の式は係数 A〜Fで形を決め、白点で割って 1 に正規化する。
    - 露出倍率（`× 2.0`）を曲線の前に掛けて、中間の明るさを合わせる。
    - より良いやり方：係数をアーティストが調整できるようにパラメータとして出す。3D LUT に焼く。

!!! info "このページを読む前に"
    - [Tone Mapping and Exposure](index.md)（このセクション全体の地図と、読む順番）

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
| <strong>つま先（toe）</strong> | 暗部の立ち上がりを抑える | 黒が沈んで締まる。暗部が持ち上がらない |
| 直線部（linear） | 中間の傾き（コントラスト） | メリハリが付く |
| 肩（shoulder） | 明部で傾きがゆるやかになり 1 に漸近 | ハイライトが白飛びせず滑らかに白へ |


原典は、Hable の GDC 2010 の発表 "Uncharted 2: HDR Lighting" です。Kodak のフィルムの特性曲線を参考につま先・直線部・肩を 1 つの有理関数（分数の式）で表しました。係数は 6 個（A〜F）と白点 W です。

原典は、Hable の GDC 2010 の発表 "Uncharted 2: HDR Lighting" です。Kodak のフィルムの特性曲線を参考につま先・直線部・肩を 1 つの有理関数（分数の式）で表しました。係数は 6 個（A〜F）と白点 W です。

Reinhard はつま先がなく、暗部が持ち上がるため眠いです。S 字はつま先で暗部を沈めるので、絵が締まります。

<!-- fig:tonemap-hable:begin -->

<svg class="fig illust motion" data-fig="tonemap-hable" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-tonemap-hable" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">Hable(Uncharted 2)のフィルミック曲線: 暗い所は立ち上がりをゆるやかに(つま先)、明るい所は、なだらかに(肩)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">同じ明るさの階調を直線的な圧縮(Reinhard)と並べる。曲線の傾きが、コントラストを決める</text>
<rect x="30" y="96" width="500" height="270" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 曲線(横 = 入力、対数)</text>
<path d="M70.0,341.88 L75.5,341.57 L81.0,341.23 L86.5,340.87 L92.0,340.48 L97.5,340.06 L103.0,339.62 L108.5,339.14 L114.0,338.62 L119.5,338.07 L125.0,337.48 L130.5,336.84 L136.0,336.17 L141.5,335.44 L147.0,334.66 L152.5,333.83 L158.0,332.94 L163.5,332.0 L169.0,330.99 L174.5,329.91 L180.0,328.76 L185.5,327.54 L191.0,326.24 L196.5,324.85 L202.0,323.39 L207.5,321.83 L213.0,320.18 L218.5,318.44 L224.0,316.59 L229.5,314.65 L235.0,312.6 L240.5,310.44 L246.0,308.17 L251.5,305.79 L257.0,303.3 L262.5,300.7 L268.0,297.98 L273.5,295.15 L279.0,292.21 L284.5,289.16 L290.0,286.0 L295.5,282.74 L301.0,279.38 L306.5,275.93 L312.0,272.39 L317.5,268.77 L323.0,265.08 L328.5,261.32 L334.0,257.51 L339.5,253.66 L345.0,249.77 L350.5,245.85 L356.0,241.92 L361.5,237.99 L367.0,234.07 L372.5,230.17 L378.0,226.29 L383.5,222.46 L389.0,218.68 L394.5,214.95 L400.0,211.3 L405.5,207.72 L411.0,204.23 L416.5,200.82 L422.0,197.52 L427.5,194.31 L433.0,191.21 L438.5,188.22 L444.0,185.33 L449.5,182.56 L455.0,179.91 L460.5,177.36 L466.0,174.93 L471.5,172.61 L477.0,170.4 L482.5,168.3 L488.0,166.31 L493.5,164.42 L499.0,162.63 L504.5,160.93 L510.0,159.33" fill="none" stroke="#2563eb" stroke-width="3.5"/>
<path d="M70.0,342.79 L75.5,342.54 L81.0,342.27 L86.5,341.98 L92.0,341.67 L97.5,341.33 L103.0,340.98 L108.5,340.59 L114.0,340.17 L119.5,339.72 L125.0,339.24 L130.5,338.73 L136.0,338.17 L141.5,337.57 L147.0,336.93 L152.5,336.25 L158.0,335.51 L163.5,334.72 L169.0,333.87 L174.5,332.96 L180.0,331.99 L185.5,330.95 L191.0,329.84 L196.5,328.65 L202.0,327.38 L207.5,326.03 L213.0,324.58 L218.5,323.04 L224.0,321.4 L229.5,319.66 L235.0,317.81 L240.5,315.85 L246.0,313.77 L251.5,311.56 L257.0,309.23 L262.5,306.77 L268.0,304.17 L273.5,301.44 L279.0,298.57 L284.5,295.55 L290.0,292.39 L295.5,289.08 L301.0,285.62 L306.5,282.02 L312.0,278.28 L317.5,274.39 L323.0,270.36 L328.5,266.2 L334.0,261.91 L339.5,257.5 L345.0,252.97 L350.5,248.34 L356.0,243.61 L361.5,238.79 L367.0,233.9 L372.5,228.95 L378.0,223.95 L383.5,218.91 L389.0,213.85 L394.5,208.78 L400.0,203.72 L405.5,198.68 L411.0,193.67 L416.5,188.71 L422.0,183.81 L427.5,178.99 L433.0,174.25 L438.5,169.6 L444.0,165.06 L449.5,160.64 L455.0,156.34 L460.5,152.16 L466.0,148.12 L471.5,144.22 L477.0,140.46 L482.5,136.84 L488.0,136.0 L493.5,136.0 L499.0,136.0 L504.5,136.0 L510.0,136.0" fill="none" stroke="#e5484d" stroke-width="3.5"/>
<circle cx="86" cy="120" r="6" fill="#2563eb"/>
<text x="96" y="124" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">Reinhard</text>
<circle cx="203.2" cy="120" r="6" fill="#e5484d"/>
<text x="213.2" y="124" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">Hable</text>
<line x1="188.19" y1="140" x2="188.19" y2="346" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="3 4"/>
<text x="188.19358620970598" y="360" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">暗い所</text>
<line x1="340.9" y1="140" x2="340.9" y2="346" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="3 4"/>
<text x="340.90320689514704" y="360" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">中間</text>
<line x1="475.48" y1="140" x2="475.48" y2="346" stroke="#e2e8f0" stroke-width="1.5" stroke-dasharray="3 4"/>
<text x="475.48396552426493" y="360" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るい所</text>
<rect x="560" y="96" width="370" height="270" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="560" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② 階調の見え方</text>
<text x="576" y="134" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">入力(ただ明るさを並べた)</text>
<rect x="576.0" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#050505"/></rect>
<rect x="588.5" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0726" values="#e5e7eb;#060606"/></rect>
<rect x="601.0" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#e5e7eb;#080808"/></rect>
<rect x="613.5" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#e5e7eb;#0a0a0a"/></rect>
<rect x="626.0" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#0c0c0c"/></rect>
<rect x="638.5" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#0f0f0f"/></rect>
<rect x="651.0" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#e5e7eb;#131313"/></rect>
<rect x="663.5" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#e5e7eb;#181818"/></rect>
<rect x="676.0" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#e5e7eb;#1e1e1e"/></rect>
<rect x="688.5" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#e5e7eb;#262626"/></rect>
<rect x="701.0" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#2f2f2f"/></rect>
<rect x="713.5" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#e5e7eb;#3b3b3b"/></rect>
<rect x="726.0" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#e5e7eb;#494949"/></rect>
<rect x="738.5" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#e5e7eb;#5b5b5b"/></rect>
<rect x="751.0" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#e5e7eb;#727272"/></rect>
<rect x="763.5" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#8e8e8e"/></rect>
<rect x="776.0" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#e5e7eb;#b2b2b2"/></rect>
<rect x="788.5" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#e5e7eb;#dedede"/></rect>
<rect x="801.0" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#ffffff"/></rect>
<rect x="813.5" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#e5e7eb;#ffffff"/></rect>
<rect x="826.0" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#e5e7eb;#ffffff"/></rect>
<rect x="838.5" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#e5e7eb;#ffffff"/></rect>
<rect x="851.0" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#e5e7eb;#ffffff"/></rect>
<rect x="863.5" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1340" values="#e5e7eb;#ffffff"/></rect>
<rect x="876.0" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1367" values="#e5e7eb;#ffffff"/></rect>
<rect x="888.5" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1395" values="#e5e7eb;#ffffff"/></rect>
<rect x="901.0" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1423" values="#e5e7eb;#ffffff"/></rect>
<rect x="913.5" y="140.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1451" values="#e5e7eb;#ffffff"/></rect>
<rect x="576" y="140" width="350.0" height="12.5" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="576" y="204" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">Reinhard</text>
<rect x="576.0" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2093" values="#e5e7eb;#050505"/></rect>
<rect x="588.5" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2121" values="#e5e7eb;#060606"/></rect>
<rect x="601.0" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2149" values="#e5e7eb;#080808"/></rect>
<rect x="613.5" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2177" values="#e5e7eb;#0a0a0a"/></rect>
<rect x="626.0" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2205" values="#e5e7eb;#0c0c0c"/></rect>
<rect x="638.5" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2233" values="#e5e7eb;#0f0f0f"/></rect>
<rect x="651.0" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2260" values="#e5e7eb;#121212"/></rect>
<rect x="663.5" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2288" values="#e5e7eb;#161616"/></rect>
<rect x="676.0" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2316" values="#e5e7eb;#1b1b1b"/></rect>
<rect x="688.5" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2344" values="#e5e7eb;#212121"/></rect>
<rect x="701.0" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2372" values="#e5e7eb;#282828"/></rect>
<rect x="713.5" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2400" values="#e5e7eb;#303030"/></rect>
<rect x="726.0" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2428" values="#e5e7eb;#393939"/></rect>
<rect x="738.5" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2456" values="#e5e7eb;#434343"/></rect>
<rect x="751.0" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2484" values="#e5e7eb;#4f4f4f"/></rect>
<rect x="763.5" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2512" values="#e5e7eb;#5b5b5b"/></rect>
<rect x="776.0" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2540" values="#e5e7eb;#696969"/></rect>
<rect x="788.5" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2567" values="#e5e7eb;#777777"/></rect>
<rect x="801.0" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2595" values="#e5e7eb;#858585"/></rect>
<rect x="813.5" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2623" values="#e5e7eb;#939393"/></rect>
<rect x="826.0" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2651" values="#e5e7eb;#a0a0a0"/></rect>
<rect x="838.5" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2679" values="#e5e7eb;#adadad"/></rect>
<rect x="851.0" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2707" values="#e5e7eb;#b9b9b9"/></rect>
<rect x="863.5" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2735" values="#e5e7eb;#c4c4c4"/></rect>
<rect x="876.0" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2763" values="#e5e7eb;#cdcdcd"/></rect>
<rect x="888.5" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#d5d5d5"/></rect>
<rect x="901.0" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2819" values="#e5e7eb;#dddddd"/></rect>
<rect x="913.5" y="210.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2847" values="#e5e7eb;#e3e3e3"/></rect>
<rect x="576" y="210" width="350.0" height="12.5" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="576" y="274" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">Hable</text>
<rect x="576.0" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3488" values="#e5e7eb;#040404"/></rect>
<rect x="588.5" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3516" values="#e5e7eb;#050505"/></rect>
<rect x="601.0" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3544" values="#e5e7eb;#060606"/></rect>
<rect x="613.5" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3572" values="#e5e7eb;#080808"/></rect>
<rect x="626.0" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3600" values="#e5e7eb;#090909"/></rect>
<rect x="638.5" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3628" values="#e5e7eb;#0c0c0c"/></rect>
<rect x="651.0" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3656" values="#e5e7eb;#0e0e0e"/></rect>
<rect x="663.5" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3684" values="#e5e7eb;#121212"/></rect>
<rect x="676.0" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3712" values="#e5e7eb;#161616"/></rect>
<rect x="688.5" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3740" values="#e5e7eb;#1b1b1b"/></rect>
<rect x="701.0" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3767" values="#e5e7eb;#212121"/></rect>
<rect x="713.5" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3795" values="#e5e7eb;#292929"/></rect>
<rect x="726.0" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3823" values="#e5e7eb;#313131"/></rect>
<rect x="738.5" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3851" values="#e5e7eb;#3b3b3b"/></rect>
<rect x="751.0" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3879" values="#e5e7eb;#474747"/></rect>
<rect x="763.5" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3907" values="#e5e7eb;#545454"/></rect>
<rect x="776.0" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3935" values="#e5e7eb;#636363"/></rect>
<rect x="788.5" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3963" values="#e5e7eb;#737373"/></rect>
<rect x="801.0" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3991" values="#e5e7eb;#848484"/></rect>
<rect x="813.5" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4019" values="#e5e7eb;#969696"/></rect>
<rect x="826.0" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4047" values="#e5e7eb;#a8a8a8"/></rect>
<rect x="838.5" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4074" values="#e5e7eb;#bababa"/></rect>
<rect x="851.0" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4102" values="#e5e7eb;#cccccc"/></rect>
<rect x="863.5" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4130" values="#e5e7eb;#dddddd"/></rect>
<rect x="876.0" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4158" values="#e5e7eb;#ececec"/></rect>
<rect x="888.5" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4186" values="#e5e7eb;#fafafa"/></rect>
<rect x="901.0" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4214" values="#e5e7eb;#ffffff"/></rect>
<rect x="913.5" y="280.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4242" values="#e5e7eb;#ffffff"/></rect>
<rect x="576" y="280" width="350.0" height="12.5" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="30" y="386" width="900" height="90" fill="#ffffff" stroke="#2ea043" stroke-width="1.8" rx="6"/>
<text x="30" y="376" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">③ 傾き(= コントラスト)。大きいほど、階調の差がはっきり</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4882;0.4884;1.0000" values="0;0;1;1"/><text x="50" y="424" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">暗い所(入力 0.1)</text>
<text x="50" y="448" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">Reinhard 0.08 / Hable 0.07</text>
<text x="50" y="466" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">Hable の方がなだらか</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5440;0.5442;1.0000" values="0;0;1;1"/><text x="350" y="424" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">中間(入力 0.8)</text>
<text x="350" y="448" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">Reinhard 0.25 / Hable 0.29</text>
<text x="350" y="466" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">Hable の方がコントラストが高い</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5998;0.6000;1.0000" values="0;0;1;1"/><text x="650" y="424" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">明るい所(入力 5)</text>
<text x="650" y="448" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">Reinhard 0.14 / Hable 0.24</text>
<text x="650" y="466" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">Hable の方がコントラストが高い</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">曲線の形が画の「味」を決める<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">同じ階調を 3 通りで並べる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.4882;0.4884;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">Hable は、中間のコントラストを上げ、暗部と明部をなだらかにする(フィルムの特性)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4882;0.4884;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:tonemap-hable:end -->

## Hable の式（Uncharted 2）

<strong>有理関数</strong>でS 字を作る式です。

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
| A（0.15） | 肩の強さ | 大きいと明部が早く頭打ち |
| B（0.50） | 直線部の強さ | 中間の傾き（コントラスト） |
| C（0.10） | 直線部の角度 | 直線の傾きの調整 |
| D（0.20） | つま先の強さ | 大きいと暗部が沈む |
| E（0.02） | つま先の分子 | つま先の細かい形 |
| F（0.30） | つま先の分母 | つま先の細かい形 |
| W（11.2） | 白点 | この入力で出力がちょうど 1 |

### 白点で正規化する理由

曲線は、x が大きくても 1 に届きません。白点 W の出力で割る（`white_scale`）ことで入力 W のとき出力がちょうど 1 になります。

| 入力 | 出力（おおよそ） |
| --- | --- |
| 0 | 0 |
| 0.18（中間灰）× 2 | 約 0.22 |
| 1 × 2 | 約 0.55 |
| 11.2 | 1 |

### `exposure_bias`（2.0）

曲線の前に掛ける倍率で、中間の明るさを合わせるためのものです。露出（[Exposure](exposure.md)）が別にあるので二重にならないよう、この値は「曲線に合わせた補正」と考え、あまり動かさないようにします。

## 色の保ち方

<strong>Hable をチャンネルごとに掛ける</strong>と、フィルムのように明るい色が白へ向かう絵になります。色相を保ちたいなら、輝度に掛けて比率を保つ方式もあります（[Preserving Hue](hue-preservation.md)）。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| 係数をパラメータで出す | A〜F をアーティストが調整できるようにする（肩・つま先・白点をスライダーで） |
| 形を「見た目の言葉」で設定 | <strong>「つま先の強さ」「肩の長さ」「白点」</strong> の3 つだけを出し、内部で A〜F に変換 |
| 3D LUT に焼く | 計算の重い曲線を LUT に焼いて、1 回の表引きにする（[Color Grading](../color-grading/index.md)） |
| ACES・AgX と比べる | 同じシーンで比べ、色の出方で選ぶ（[ACES](aces.md)・[AgX](agx.md)） |
| HDR 出力と分ける | HDR ディスプレイでは、別の曲線（[Gamma and HDR Output](gamma-srgb.md)） |

## よくあるミス

??? failure "露出を `exposure_bias` で調整して、自動露出と二重になる"
    <strong>明るさの調整は、露出（EV）で</strong>。`exposure_bias` は固定。

??? failure "白点を変えたのに、白が出ない"
    `white_scale` の計算を忘れた。`1 / HableCurve(white_point)` を掛ける。

??? failure "暗部が潰れすぎて、夜のシーンが真っ黒"
    つま先（D・E・F）を弱める、露出を上げる、曲線の前にオフセットを加える。

??? failure "色相が変わって、赤い物がオレンジに見える"
    チャンネルごとの副作用。輝度ベースにする、または AgX・ACES の色補正を検討。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フィルミック ＝ <strong>S 字（つま先・直線部・肩）</strong>。暗部を締め、明部を滑らかに
    - [x] Hable の式は係数 A〜F ＋ 白点 W。白点の出力で割って 1 に正規化
    - [x] つま先が暗部を沈めるので、Reinhard より締まる
    - [x] 露出は別に。`exposure_bias` は固定
    - [x] パラメータ化・LUT 化で画作りを制御しやすく

## 参考

- Hable, "Uncharted 2: HDR Lighting"（GDC 2010）
- Hable, "Filmic Tonemapping Operators"（filmicworlds.com）
- Duiker, "Filmic Tonemapping for Real-time Rendering"（SIGGRAPH 2010）

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [Reinhard](reinhard.md)
- [ACES](aces.md)
- [Preserving Hue](hue-preservation.md)
