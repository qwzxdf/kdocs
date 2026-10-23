---
title: Exposure
tags:
  - 描画
---

# Exposure

<strong>露出</strong>は、HDR の光の量に掛ける倍率です。カメラで言う「絞り・シャッター速度・ISO 感度」をまとめた 1 つの数で、画面全体の明るさを決めます。トーンマップの前に掛けるので、同じ光景でも露出で「明るい昼」にも「暗い夜」にも見えます。このページでは、EV（露出値）・カメラの 3 要素・EV100 による物理ベースの露出・露出補正・露出の決め方を説明します。

!!! tip "ポイント"
    - 露出後の値 ＝ <strong>HDR の輝度 × 倍率</strong>。<strong>トーンマップの前に掛ける</strong>。
    - EV は2 の冪で表す指標。EV が 1 上がるごとに、光の量は半分（暗く）。1 EV ＝ 1 ストップ。
    - カメラの絞り・シャッター・ISOはどれも光の量を 2 倍・半分にできる。ゲームでは 1 つの倍率にまとめる。
    - EV100 は ISO 100 を基準にした EV。物理ベース（PBR）の光の単位と相性が良い。
    - 露出補正 ＝ 自動露出の結果に足す EV のずれ。アーティストの調整。
    - 露出が合っていないと、明部が真っ白に飛ぶか、暗部が真っ黒に潰れる。

<!-- fig:exposure-ev:begin -->

<svg class="fig illust motion" data-fig="exposure-ev" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-exposure-ev" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">露出(EV): 1 段上げると、明るさが 2 倍。同じ絵を、−3 〜 +3 段で並べる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">線形の明るさ 0.02 〜 3 の 5 つの面。EV を変えて、画面(sRGB)での見え方がどう変わるか</text>
<text x="170.0" y="116" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">黒い布</text>
<text x="170.0" y="134" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">明るさ 0.02</text>
<text x="304.0" y="116" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">濃い灰</text>
<text x="304.0" y="134" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">明るさ 0.07</text>
<text x="438.0" y="116" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">中間の灰</text>
<text x="438.0" y="134" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">明るさ 0.18</text>
<text x="572.0" y="116" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">明るい壁</text>
<text x="572.0" y="134" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">明るさ 0.7</text>
<text x="706.0" y="116" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">光る面</text>
<text x="706.0" y="134" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">明るさ 3</text>
<rect x="110.0" y="146" width="120.0" height="100" fill="#050505" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0732;0.2293;0.3854;0.5415;0.6976" values="#050505;#010101;#030303;#050505;#0a0a0a;#292929"/></rect>
<text x="170.0" y="205" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ef4444"/>
<rect x="244.0" y="146" width="120.0" height="100" fill="#121212" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0732;0.2293;0.3854;0.5415;0.6976" values="#121212;#020202;#090909;#121212;#242424;#8f8f8f"/></rect>
<text x="304.0" y="205" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ef4444"/>
<rect x="378.0" y="146" width="120.0" height="100" fill="#2e2e2e" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0732;0.2293;0.3854;0.5415;0.6976" values="#2e2e2e;#060606;#171717;#2e2e2e;#5c5c5c;#ffffff"/></rect>
<text x="438.0" y="205" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ef4444"/>
<rect x="512.0" y="146" width="120.0" height="100" fill="#b2b2b2" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0732;0.2293;0.3854;0.5415;0.6976" values="#b2b2b2;#161616;#595959;#b2b2b2;#ffffff;#ffffff"/></rect>
<text x="572.0" y="205" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ef4444"/>
<rect x="646.0" y="146" width="120.0" height="100" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill" dur="20.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0732;0.2293;0.3854;0.5415;0.6976" values="#ffffff;#606060;#ffffff;#ffffff;#ffffff;#ffffff"/></rect>
<text x="706.0" y="205" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ef4444"/>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2291;0.2293;1.0000" values="1;1;0;0"/><text x="40" y="290" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed">露出 -3 EV(×0.125)</text>
<text x="170.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.003</text>
<text x="170.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">17 / 255</text>
<text x="304.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.009</text>
<text x="304.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">30 / 255</text>
<text x="438.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.022</text>
<text x="438.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">45 / 255</text>
<text x="572.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.087</text>
<text x="572.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">84 / 255</text>
<text x="706.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.375</text>
<text x="706.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">163 / 255</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2291;0.2293;0.3852;0.3854;1.0000" values="0;0;1;1;0;0"/><text x="40" y="290" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed">露出 -1 EV(×0.5)</text>
<text x="170.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.010</text>
<text x="170.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">31 / 255</text>
<text x="304.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.035</text>
<text x="304.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">56 / 255</text>
<text x="438.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.090</text>
<text x="438.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">85 / 255</text>
<text x="572.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.350</text>
<text x="572.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">158 / 255</text>
<text x="706.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ef4444">1.500</text>
<text x="706.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ef4444">白飛び</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3852;0.3854;0.5413;0.5415;1.0000" values="0;0;1;1;0;0"/><text x="40" y="290" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed">露出 +0 EV(×1)</text>
<text x="170.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.020</text>
<text x="170.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">43 / 255</text>
<text x="304.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.070</text>
<text x="304.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">76 / 255</text>
<text x="438.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.180</text>
<text x="438.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">117 / 255</text>
<text x="572.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.700</text>
<text x="572.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">217 / 255</text>
<text x="706.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ef4444">3.000</text>
<text x="706.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ef4444">白飛び</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.5413;0.5415;0.6974;0.6976;1.0000" values="0;0;1;1;0;0"/><text x="40" y="290" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed">露出 +1 EV(×2)</text>
<text x="170.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.040</text>
<text x="170.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">59 / 255</text>
<text x="304.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.140</text>
<text x="304.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">104 / 255</text>
<text x="438.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.360</text>
<text x="438.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">160 / 255</text>
<text x="572.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ef4444">1.400</text>
<text x="572.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ef4444">白飛び</text>
<text x="706.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ef4444">6.000</text>
<text x="706.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ef4444">白飛び</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.6974;0.6976;1.0000" values="0;0;1;1"/><text x="40" y="290" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed">露出 +3 EV(×8)</text>
<text x="170.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.160</text>
<text x="170.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">111 / 255</text>
<text x="304.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">0.560</text>
<text x="304.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">196 / 255</text>
<text x="438.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ef4444">1.440</text>
<text x="438.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ef4444">白飛び</text>
<text x="572.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ef4444">5.600</text>
<text x="572.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ef4444">白飛び</text>
<text x="706.0" y="322" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#ef4444">24.000</text>
<text x="706.0" y="342" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#ef4444">白飛び</text>
</g>
<text x="60" y="322" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">掛けた後</text>
<text x="60" y="342" text-anchor="end" style="font-size:12px;font-weight:700;fill:#64748b">画面の値</text>
<rect x="30" y="372" width="900" height="100" fill="#ffffff" stroke="#e5484d" stroke-width="1.8" rx="6"/>
<text x="30" y="362" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">白飛びした面と、黒くつぶれた面の数</text>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0730;0.0732;1.0000" values="0;0;1;1"/><text x="70" y="414" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">-3 EV</text>
<text x="70" y="436" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">白飛び 0 / つぶれ 2</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.2291;0.2293;1.0000" values="0;0;1;1"/><text x="245" y="414" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">-1 EV</text>
<text x="245" y="436" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">白飛び 1 / つぶれ 0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.3852;0.3854;1.0000" values="0;0;1;1"/><text x="420" y="414" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">+0 EV</text>
<text x="420" y="436" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">白飛び 1 / つぶれ 0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.5413;0.5415;1.0000" values="0;0;1;1"/><text x="595" y="414" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">+1 EV</text>
<text x="595" y="436" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">白飛び 2 / つぶれ 0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.6974;0.6976;1.0000" values="0;0;1;1"/><text x="770" y="414" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">+3 EV</text>
<text x="770" y="436" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">白飛び 3 / つぶれ 0</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.8535;0.8537;1.0000" values="0;0;1;1"/><rect x="560" y="480" width="370" height="40" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="576" y="504" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1e3a8a">全部がちょうど見える露出は、無い → トーンマップが必要</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">1 EV 上げる = 光の量が 2 倍(カメラの絞り 1 段)<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0730;0.0732;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">5 つの面は、明るさがバラバラ。露出を変えると、見える面が、入れ替わる<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.0730;0.0732;0.8535;0.8537;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">暗い面を見えるように上げると、明るい面が白飛びする<animate attributeName="opacity" dur="20.5s" repeatCount="indefinite" keyTimes="0.0000;0.8535;0.8537;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:exposure-ev:end -->

## なぜ露出が要るのか

<strong>HDR の値は、「光の絶対量」に近い</strong>ので幅が非常に広いです。ディスプレイに映せるのは 0〜1 だけなので、どの範囲を 0〜1 に割り当てるかを先に決める必要があります。これが露出です。

<svg class="fig illust" viewBox="0 0 780 250" role="img" aria-label="露出で範囲を選ぶ">
<text x="20" y="26" class="fig-title">露出 ＝ 広い明るさの中から、見せたい範囲を選んで、0〜1 に合わせる</text>
<defs><linearGradient id="ex-g" x1="0" x2="1"><stop offset="0" stop-color="#0b1020"/><stop offset="1" stop-color="#fff7d1"/></linearGradient></defs>
<rect x="40" y="60" width="700" height="34" fill="url(#ex-g)" stroke="#94a3b8"/>
<g font-size="12"><text x="40" y="112">0.01（暗い部屋）</text><text x="250" y="112">1</text><text x="400" y="112">100</text><text x="540" y="112">10,000</text><text x="700" y="112" text-anchor="start" style="font-size:10px">10 万（太陽）</text></g>
<rect x="170" y="130" width="140" height="22" rx="4" fill="#2563eb" fill-opacity="0.35" stroke="#2563eb" stroke-width="2"/>
<text x="240" y="170" text-anchor="middle" style="font-size:13px;fill:#2563eb">夜の屋内を撮る露出</text>
<rect x="400" y="130" width="200" height="22" rx="4" fill="#e5484d" fill-opacity="0.3" stroke="#e5484d" stroke-width="2"/>
<text x="500" y="170" text-anchor="middle" style="font-size:13px;fill:#e5484d">晴天の屋外を撮る露出</text>
<text x="40" y="214" style="font-size:13px">選んだ範囲の外は、暗い側は真っ黒に潰れ、明るい側は真っ白に飛ぶ。</text>
<text x="40" y="236" style="font-size:13px">屋内から屋外へ出ると、見える範囲を切り替える（＝露出を変える）必要がある。</text>
</svg>

## EV（露出値）

<div class="formula">露出後の値 = 輝度 × 2^(−EV)　（EV が大きいほど暗くなる）</div>

| EV の差 | 光の量 | たとえ |
| --- | --- | --- |
| +1 EV | 半分 | 1 段暗くする（絞りを 1 段絞る） |
| −1 EV | 2 倍 | 1 段明るくする |
| +3 EV | 1/8 | かなり暗く |
| 差が 0 | そのまま | — |

<strong>「1 段（ストップ）」で 2 倍・半分</strong>という単位は、人間の明るさの感じ方が対数的であることに合っています。EV が等間隔なら、見た目の明るさもほぼ等間隔に変わります。

## カメラの 3 つの要素

<strong>実際のカメラは、3 つの要素で光の量を決めます</strong>。どれも「1 段」変えると光が 2 倍・半分になります。

| 要素 | 内容 | 副作用 |
| --- | --- | --- |
| 絞り（F 値） | レンズの穴の大きさ。F が小さいほど明るい | 被写界深度が変わる（開けるとボケる） |
| シャッター速度 | 光を取り込む時間。長いほど明るい | モーション ブラーが変わる（遅いとブレる） |
| ISO 感度 | センサーの増幅率。高いほど明るい | ノイズが増える |


ゲームでは、被写界深度、モーション ブラー、ノイズの効果は別々に処理し、露出は「全体の倍率」として扱うのが普通です。ただし、物理に忠実な設計にしたい場合は、絞りとシャッター速度を、被写界深度とモーション ブラーのパラメータにも接続します。

ゲームでは、被写界深度、モーション ブラー、ノイズの効果は別々に処理し、露出は「全体の倍率」として扱うのが普通です。ただし、物理に忠実な設計にしたい場合は、絞りとシャッター速度を、被写界深度とモーション ブラーのパラメータにも接続します。

<div class="formula">EV = log₂( F² / t ) − log₂( ISO / 100 )　（F：F 値、t：シャッター秒、ISO：感度）</div>

ゲームではこれを 1 つの倍率にまとめます。絞りは DOF（[被写界深度](../dof/index.md)）、シャッターはモーション ブラー（[Motion Blur](../motion-blur/index.md)）と別に決めることも多く、露出としては合計の EV だけ使います。

## EV100 と物理ベースの露出

<strong>EV100</strong> は、ISO 100 に換算した EV です。絞り・シャッターの組み合わせが違っても、同じ EV100 なら、同じ明るさになります。

```hlsl
float ExposureFromEV100(float ev100) {
  float max_luminance = 1.2 * exp2(ev100);
  return 1.0 / max_luminance;
}

float3 ApplyExposure(float3 hdr_color, float ev100) {
  return hdr_color * ExposureFromEV100(ev100);
}
```

コードの要点です。`1.2 * exp2(ev100)` は、この輝度のときにちょうど 1（真っ白）になる飽和輝度です。1.2 は、カメラの標準的な係数です。`1.0 / …` で、その逆数を倍率にします（輝度に倍率を掛けると、0〜1 付近になります）。単位を揃えることも大切で、ライトの強さを物理値（ルクス・カンデラ）にすると、露出とセットで明るさが一貫します。

### 典型的な EV100

| 状況 | EV100 |
| --- | --- |
| 晴天の屋外（日向） | 約 15 |
| 曇り | 約 12 |
| 明るい室内 | 約 7〜8 |
| 暗い室内 | 約 4〜5 |
| 夜景（街灯） | 約 0〜3 |
| 星明かり | 約 −3〜−5 |

<svg class="fig illust" viewBox="0 0 780 200" role="img" aria-label="EV100 の目盛り">
<text x="20" y="26" class="fig-title">EV100 の目盛り：1 つ違うごとに、光の量が 2 倍</text>
<line x1="40" y1="100" x2="740" y2="100" stroke="currentColor" stroke-width="2"/>
<g font-size="12" text-anchor="middle">
<line x1="60" y1="92" x2="60" y2="108" stroke="currentColor"/><text x="60" y="126">−3</text><text x="60" y="146" style="font-size:11px">星明かり</text>
<line x1="170" y1="92" x2="170" y2="108" stroke="currentColor"/><text x="170" y="126">2</text><text x="170" y="146" style="font-size:11px">夜景</text>
<line x1="290" y1="92" x2="290" y2="108" stroke="currentColor"/><text x="290" y="126">5</text><text x="290" y="146" style="font-size:11px">暗い室内</text>
<line x1="410" y1="92" x2="410" y2="108" stroke="currentColor"/><text x="410" y="126">8</text><text x="410" y="146" style="font-size:11px">明るい室内</text>
<line x1="540" y1="92" x2="540" y2="108" stroke="currentColor"/><text x="540" y="126">12</text><text x="540" y="146" style="font-size:11px">曇り</text>
<line x1="680" y1="92" x2="680" y2="108" stroke="currentColor"/><text x="680" y="126">15</text><text x="680" y="146" style="font-size:11px">晴天の屋外</text>
</g>
<text x="40" y="60" style="font-size:12px">暗い ←　　　　　　　　　　　　　　　　　　　　　　　　　　　　　→ 明るい（EV100 が大きいほど、倍率は小さい＝暗く映す）</text>
</svg>

## 露出補正

<strong>自動露出が決めた EV に、手で EV を足す</strong>のが露出補正です。画作りの意図（ここは少し暗く、雰囲気を出す）を反映できます。

```hlsl
float finalEV100 = autoEV100 + exposure_compensation;
```

露出の補正（Exposure Compensation）の使い道です。ステージごとの調整として、ホラー ステージは −1、砂漠は +0.5 のように設定します。イベント演出として、爆発の瞬間だけ −2 してまぶしさを演出します。ユーザー設定として、明るさ（ガンマ）スライダーにも使えます。

## ゲームでの露出の決め方

| 方式 | 内容 | 向く場面 |
| --- | --- | --- |
| 固定の EV | ステージごとに決めた値 | 室内のみ・明るさが一定のゲーム |
| エリアごとの EV | ボリュームで EV を指定し、境で補間 | 屋内外が混在するゲーム |
| 自動露出 | 画面の明るさから毎フレーム決める（[Auto Exposure](auto-exposure.md)） | 明るさが大きく変わるゲーム |
| 自動 ＋ 補正 ＋ 範囲制限 | 自動の結果に補正を足し、最小・最大 EV を決める | 多くのゲームの標準 |

## よくあるミス

??? failure "露出をトーンマップの後に掛けて、明るさが調整できない"
    <strong>露出は HDR のリニア値に、トーンマップの前</strong>に掛ける。

??? failure "EV の符号を逆にして、明るくしたつもりが暗くなる"
    EV が大きいほど暗い（`× 2^(−EV)`）。明るくしたいなら EV を下げる。

??? failure "ライトの強さがバラバラで、露出を変えるとあるものだけ飛ぶ"
    ライトを物理単位にそろえる。オブジェクトごとの強さの「調整」を露出で隠さない。

??? failure "屋内と屋外の境で、画面が急に明るく・暗くなる"
    露出を境でゆっくり補間する（[Auto Exposure](auto-exposure.md)の時間追従）。

??? failure "絞り・シャッターの値をそのまま倍率に使って、DOF やブレとぶつかる"
    露出（明るさ）と、DOF・ブレ（見た目の効果）は、別に設計する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 露出 ＝ <strong>HDR に掛ける倍率</strong>。トーンマップの前に掛ける
    - [x] EV が 1 増えると光は半分。`× 2^(−EV)`
    - [x] カメラの絞り・シャッター・ISOはどれも 1 段で 2 倍。ゲームでは 1 つの倍率にまとめる
    - [x] EV100（ISO 100 基準）と物理単位のライトで明るさが一貫
    - [x] 露出補正は自動露出に足す EV

## 参考

- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering"（SIGGRAPH 2014、EV100 と露出）
- ISO 2720:1974, "General Purpose Photographic Exposure Meters"
- Hoffman, "Physically Based Shading in Theory and Practice"（SIGGRAPH Course）

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [Auto Exposure](auto-exposure.md)
- [Reinhard](reinhard.md)
- [Depth of Field (DOF)](../dof/index.md)
- [PBR](../../../3d/pbr.md)
