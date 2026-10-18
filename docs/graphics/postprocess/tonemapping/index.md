---
title: Tone Mapping and Exposure
tags:
  - 描画
---

# Tone Mapping and Exposure

**現実の明るさ**は、**暗い部屋の 0.01 から、太陽の 100,000 まで**、**桁違いの幅**があります。**ディスプレイが出せる範囲**は、<strong>0〜1（LDR）</strong>です。**HDR で計算した光**を、**この狭い範囲に収める**のが**トーンマッピング**で、**その前段で「どれだけ明るく撮るか」＝露出**を決めます。このセクションでは、**露出・各トーンマップ曲線・色相の保ち方・自動露出・ガンマ**を、**1 つずつ別のページ**で説明します。

## Flow {#流れ}

<svg class="fig illust" viewBox="0 0 780 190" role="img" aria-label="トーンマップの流れ">
<text x="20" y="26" class="fig-title">HDR のリニア画像が、画面に出るまで</text>
<defs><marker id="tm-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs>
<g font-size="13">
<rect x="20" y="60" width="140" height="80" rx="8" fill="#4c8bf5" fill-opacity="0.18" stroke="#4c8bf5" stroke-width="2"/>
<text x="90" y="92" text-anchor="middle" style="font-weight:700">HDR の絵</text><text x="90" y="114" text-anchor="middle" style="font-size:11px">0〜数万（リニア）</text>
<rect x="210" y="60" width="140" height="80" rx="8" fill="#e5aa28" fill-opacity="0.2" stroke="#e5aa28" stroke-width="2"/>
<text x="280" y="92" text-anchor="middle" style="font-weight:700">① 露出</text><text x="280" y="114" text-anchor="middle" style="font-size:11px">× 2^(−EV)</text>
<rect x="400" y="60" width="140" height="80" rx="8" fill="#e5484d" fill-opacity="0.18" stroke="#e5484d" stroke-width="2"/>
<text x="470" y="92" text-anchor="middle" style="font-weight:700">② トーンマップ</text><text x="470" y="114" text-anchor="middle" style="font-size:11px">曲線で 0〜1 へ</text>
<rect x="590" y="60" width="170" height="80" rx="8" fill="#2ea043" fill-opacity="0.18" stroke="#2ea043" stroke-width="2"/>
<text x="675" y="92" text-anchor="middle" style="font-weight:700">③ ガンマ（sRGB）</text><text x="675" y="114" text-anchor="middle" style="font-size:11px">画面へ</text>
</g>
<g stroke="currentColor" stroke-width="2"><line x1="162" y1="100" x2="208" y2="100" marker-end="url(#tm-arrow)"/><line x1="352" y1="100" x2="398" y2="100" marker-end="url(#tm-arrow)"/><line x1="542" y1="100" x2="588" y2="100" marker-end="url(#tm-arrow)"/></g>
<text x="20" y="176" style="font-size:12px">自動露出は、①の倍率を、画面の明るさから毎フレーム決める。</text>
</svg>

## Why Tone Mapping Is Needed {#なぜトーンマップが要るのか}

現実の明るさは、桁違いに幅広く変化します。晴天の太陽の下は、星明かりの 10 億倍以上明るいと言われます。ゲームの内部では、このような広い明るさの範囲を、HDR のリニア値（0 から数万以上）で計算します。ところが、ディスプレイが出せる明るさは、0 から 1（SDR の場合）の狭い範囲に限られます。この差を埋める処理がトーンマップです。

最も単純な方法は、1 を超える値を 1 に切る（クランプ）ことですが、明るい部分が一様な白に潰れて、階調が失われます。トーンマップは、明るい部分を滑らかに圧縮して、白に向かって「ゆるやかに」近づけます。暗い部分はなるべくそのまま残し、明るい部分を大きく圧縮するこの特性を、カメラのフィルムが光に反応する様子（S 字の特性曲線）が参考にされました。

トーンマップには、もう 1 つ重要な役割があります。それは<strong>画作りの方向性を決める</strong>ことです。同じ HDR の絵でも、選ぶ曲線によって、コントラストの強さ、色の出方、ハイライトの白への向かい方が変わります。このセクションでは、露出（入力の明るさを揃える）から始めて、曲線の種類を順に見て、最後に自動露出と、ディスプレイへの出力を扱います。

## Page List {#ページ一覧}

| ページ | 内容 |
| --- | --- |
| [Exposure](exposure.md) | EV・絞り／シャッター／ISO・EV100・露出補正 |
| [Reinhard](reinhard.md) | x/(1+x)・白点付き・もっとも簡単な曲線 |
| [Filmic (Hable)](filmic-hable.md) | S 字・肩とつま先・Uncharted 2 の式 |
| [ACES](aces.md) | 映画業界の標準・近似式・色の偏り |
| [AgX and Others](agx.md) | AgX・Tony McMapface・Khronos PBR Neutral |
| [Preserving Hue](hue-preservation.md) | チャンネルごと / 輝度ベース / ハイブリッド |
| [Auto Exposure](auto-exposure.md) | 平均輝度・ヒストグラム・時間追従 |
| [Gamma and HDR Output](gamma-srgb.md) | sRGB・リニア空間・HDR10 への出力 |

## Compare by Moving the Curve {#曲線を動かして比べる}

**入力の明るさ x を 0 から増やしたとき、各曲線の出力がどう変わるか**を見ます。

<!-- fig:tonemap-curves:begin -->

<svg class="fig illust motion" data-fig="tonemap-curves" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-tonemap-curves" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">トーンマップの比較: 明るさ(HDR)を、画面に出せる 0〜1 に押し込む</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">オレンジ色の物体を、暗い所から、白より 16 倍明るい所まで 32 段階で並べる。4 つの方法で、画面に出す</text>
<text x="70.0" y="96" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">切り捨て(1 で頭打ち)</text>
<rect x="70.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0465" values="#e5e7eb;#412d17"/></rect>
<rect x="94.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0493" values="#e5e7eb;#473119"/></rect>
<rect x="118.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0521" values="#e5e7eb;#4d361b"/></rect>
<rect x="142.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0549" values="#e5e7eb;#543b1e"/></rect>
<rect x="166.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0577" values="#e5e7eb;#5c4020"/></rect>
<rect x="190.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0605" values="#e5e7eb;#644523"/></rect>
<rect x="214.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0633" values="#e5e7eb;#6d4b26"/></rect>
<rect x="238.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0660" values="#e5e7eb;#765229"/></rect>
<rect x="262.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0688" values="#e5e7eb;#81592d"/></rect>
<rect x="286.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0716" values="#e5e7eb;#8c6131"/></rect>
<rect x="310.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#986a35"/></rect>
<rect x="334.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0772" values="#e5e7eb;#a6733a"/></rect>
<rect x="358.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0800" values="#e5e7eb;#b47d3f"/></rect>
<rect x="382.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0828" values="#e5e7eb;#c48845"/></rect>
<rect x="406.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0856" values="#e5e7eb;#d6954b"/></rect>
<rect x="430.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#e8a252"/></rect>
<rect x="454.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0912" values="#e5e7eb;#fdb059"/></rect>
<rect x="478.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0940" values="#e5e7eb;#ffbf61"/></rect>
<rect x="502.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0967" values="#e5e7eb;#ffd069"/></rect>
<rect x="526.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0995" values="#e5e7eb;#ffe372"/></rect>
<rect x="550.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#fff77d"/></rect>
<rect x="574.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1051" values="#e5e7eb;#ffff88"/></rect>
<rect x="598.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1079" values="#e5e7eb;#ffff93"/></rect>
<rect x="622.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1107" values="#e5e7eb;#ffffa0"/></rect>
<rect x="646.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1135" values="#e5e7eb;#ffffaf"/></rect>
<rect x="670.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#ffffbe"/></rect>
<rect x="694.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1191" values="#e5e7eb;#ffffcf"/></rect>
<rect x="718.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1219" values="#e5e7eb;#ffffe1"/></rect>
<rect x="742.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1247" values="#e5e7eb;#fffff5"/></rect>
<rect x="766.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1274" values="#e5e7eb;#ffffff"/></rect>
<rect x="790.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1302" values="#e5e7eb;#ffffff"/></rect>
<rect x="814.0" y="100.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1330" values="#e5e7eb;#ffffff"/></rect>
<rect x="70.0" y="100" width="768.0" height="24.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1403;0.1405;1.0000" values="0;0;1;1"/><text x="846.0" y="114" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">白飛び 3 段</text>
<text x="846.0" y="132" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">使える段 21 / 32</text>
</g>
<text x="70.0" y="162" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">Reinhard</text>
<rect x="70.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2140" values="#e5e7eb;#402d17"/></rect>
<rect x="94.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2167" values="#e5e7eb;#453119"/></rect>
<rect x="118.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2195" values="#e5e7eb;#4b351b"/></rect>
<rect x="142.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2223" values="#e5e7eb;#513a1d"/></rect>
<rect x="166.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2251" values="#e5e7eb;#583e20"/></rect>
<rect x="190.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2279" values="#e5e7eb;#5e4423"/></rect>
<rect x="214.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2307" values="#e5e7eb;#664926"/></rect>
<rect x="238.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2335" values="#e5e7eb;#6d4f29"/></rect>
<rect x="262.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2363" values="#e5e7eb;#75562d"/></rect>
<rect x="286.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2391" values="#e5e7eb;#7e5c31"/></rect>
<rect x="310.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2419" values="#e5e7eb;#866435"/></rect>
<rect x="334.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2447" values="#e5e7eb;#8f6b39"/></rect>
<rect x="358.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2474" values="#e5e7eb;#97733e"/></rect>
<rect x="382.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2502" values="#e5e7eb;#a07b43"/></rect>
<rect x="406.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2530" values="#e5e7eb;#a98449"/></rect>
<rect x="430.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2558" values="#e5e7eb;#b18c4f"/></rect>
<rect x="454.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2586" values="#e5e7eb;#b99555"/></rect>
<rect x="478.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2614" values="#e5e7eb;#c19e5c"/></rect>
<rect x="502.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2642" values="#e5e7eb;#c8a663"/></rect>
<rect x="526.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2670" values="#e5e7eb;#cfaf6a"/></rect>
<rect x="550.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#e5e7eb;#d5b772"/></rect>
<rect x="574.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2726" values="#e5e7eb;#dbbf7a"/></rect>
<rect x="598.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2753" values="#e5e7eb;#e0c683"/></rect>
<rect x="622.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2781" values="#e5e7eb;#e4cd8c"/></rect>
<rect x="646.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#e5e7eb;#e8d394"/></rect>
<rect x="670.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2837" values="#e5e7eb;#ecd99d"/></rect>
<rect x="694.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2865" values="#e5e7eb;#efdea6"/></rect>
<rect x="718.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2893" values="#e5e7eb;#f1e3ae"/></rect>
<rect x="742.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2921" values="#e5e7eb;#f3e7b6"/></rect>
<rect x="766.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2949" values="#e5e7eb;#f5ebbe"/></rect>
<rect x="790.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2977" values="#e5e7eb;#f7eec6"/></rect>
<rect x="814.0" y="166.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3005" values="#e5e7eb;#f8f0cd"/></rect>
<rect x="70.0" y="166" width="768.0" height="24.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3077;0.3079;1.0000" values="0;0;1;1"/><text x="846.0" y="180" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">白飛び 0 段</text>
<text x="846.0" y="198" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">使える段 32 / 32</text>
</g>
<text x="70.0" y="228" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">ACES</text>
<rect x="70.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3814" values="#e5e7eb;#3e230d"/></rect>
<rect x="94.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3842" values="#e5e7eb;#47280f"/></rect>
<rect x="118.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3870" values="#e5e7eb;#502e11"/></rect>
<rect x="142.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3898" values="#e5e7eb;#5b3413"/></rect>
<rect x="166.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3926" values="#e5e7eb;#673b15"/></rect>
<rect x="190.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3953" values="#e5e7eb;#734418"/></rect>
<rect x="214.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3981" values="#e5e7eb;#804d1b"/></rect>
<rect x="238.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4009" values="#e5e7eb;#8d581e"/></rect>
<rect x="262.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4037" values="#e5e7eb;#9b6323"/></rect>
<rect x="286.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4065" values="#e5e7eb;#a86f27"/></rect>
<rect x="310.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4093" values="#e5e7eb;#b47c2d"/></rect>
<rect x="334.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4121" values="#e5e7eb;#bf8a33"/></rect>
<rect x="358.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4149" values="#e5e7eb;#c9973b"/></rect>
<rect x="382.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4177" values="#e5e7eb;#d2a443"/></rect>
<rect x="406.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4205" values="#e5e7eb;#dab04d"/></rect>
<rect x="430.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4233" values="#e5e7eb;#e1bc57"/></rect>
<rect x="454.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4260" values="#e5e7eb;#e6c662"/></rect>
<rect x="478.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4288" values="#e5e7eb;#ebd06e"/></rect>
<rect x="502.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#e5e7eb;#efd87b"/></rect>
<rect x="526.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4344" values="#e5e7eb;#f3df88"/></rect>
<rect x="550.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4372" values="#e5e7eb;#f5e596"/></rect>
<rect x="574.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4400" values="#e5e7eb;#f8eaa3"/></rect>
<rect x="598.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4428" values="#e5e7eb;#faeeaf"/></rect>
<rect x="622.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4456" values="#e5e7eb;#fbf2bb"/></rect>
<rect x="646.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4484" values="#e5e7eb;#fcf5c5"/></rect>
<rect x="670.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4512" values="#e5e7eb;#fef7cf"/></rect>
<rect x="694.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4540" values="#e5e7eb;#fef9d7"/></rect>
<rect x="718.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4567" values="#e5e7eb;#fffbde"/></rect>
<rect x="742.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4595" values="#e5e7eb;#fffce4"/></rect>
<rect x="766.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4623" values="#e5e7eb;#fffde9"/></rect>
<rect x="790.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4651" values="#e5e7eb;#fffeee"/></rect>
<rect x="814.0" y="232.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4679" values="#e5e7eb;#fffff1"/></rect>
<rect x="70.0" y="232" width="768.0" height="24.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4752;0.4753;1.0000" values="0;0;1;1"/><text x="846.0" y="246" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">白飛び 0 段</text>
<text x="846.0" y="264" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">使える段 24 / 32</text>
</g>
<text x="70.0" y="294" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">Hable(Uncharted 2)</text>
<rect x="70.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5488" values="#e5e7eb;#3a2814"/></rect>
<rect x="94.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5516" values="#e5e7eb;#3f2c16"/></rect>
<rect x="118.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5544" values="#e5e7eb;#443018"/></rect>
<rect x="142.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5572" values="#e5e7eb;#4a341a"/></rect>
<rect x="166.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5600" values="#e5e7eb;#50381d"/></rect>
<rect x="190.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5628" values="#e5e7eb;#573d1f"/></rect>
<rect x="214.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5656" values="#e5e7eb;#5e4222"/></rect>
<rect x="238.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5684" values="#e5e7eb;#654825"/></rect>
<rect x="262.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5712" values="#e5e7eb;#6d4e28"/></rect>
<rect x="286.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5740" values="#e5e7eb;#76552b"/></rect>
<rect x="310.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5767" values="#e5e7eb;#7e5c2f"/></rect>
<rect x="334.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5795" values="#e5e7eb;#876333"/></rect>
<rect x="358.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5823" values="#e5e7eb;#916b38"/></rect>
<rect x="382.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5851" values="#e5e7eb;#9b733d"/></rect>
<rect x="406.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5879" values="#e5e7eb;#a47c42"/></rect>
<rect x="430.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5907" values="#e5e7eb;#ae8548"/></rect>
<rect x="454.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5935" values="#e5e7eb;#b88e4e"/></rect>
<rect x="478.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5963" values="#e5e7eb;#c19854"/></rect>
<rect x="502.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5991" values="#e5e7eb;#cba15b"/></rect>
<rect x="526.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6019" values="#e5e7eb;#d4ab62"/></rect>
<rect x="550.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6047" values="#e5e7eb;#dcb56a"/></rect>
<rect x="574.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6074" values="#e5e7eb;#e4bf72"/></rect>
<rect x="598.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6102" values="#e5e7eb;#ebc87b"/></rect>
<rect x="622.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6130" values="#e5e7eb;#f2d184"/></rect>
<rect x="646.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6158" values="#e5e7eb;#f8da8d"/></rect>
<rect x="670.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6186" values="#e5e7eb;#fde297"/></rect>
<rect x="694.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6214" values="#e5e7eb;#ffe9a1"/></rect>
<rect x="718.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6242" values="#e5e7eb;#fff0aa"/></rect>
<rect x="742.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6270" values="#e5e7eb;#fff6b4"/></rect>
<rect x="766.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6298" values="#e5e7eb;#fffcbe"/></rect>
<rect x="790.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6326" values="#e5e7eb;#ffffc7"/></rect>
<rect x="814.0" y="298.0" width="24.3" height="24.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6353" values="#e5e7eb;#ffffd0"/></rect>
<rect x="70.0" y="298" width="768.0" height="24.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6426;0.6428;1.0000" values="0;0;1;1"/><text x="846.0" y="312" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">白飛び 0 段</text>
<text x="846.0" y="330" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">使える段 28 / 32</text>
</g>
<text x="70.0" y="82" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">← 暗い      露出(0.05 〜 16 倍)      明るい →</text>
<rect x="30" y="372" width="900" height="144" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="362" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">明るい所での色の変化(色相。元のオレンジ = 23°)</text>
<circle cx="76" cy="432" r="24" fill="#ffffff" stroke="#334155" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7347;0.7349;1.0000" values="0;0;1;1"/></circle>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7347;0.7349;1.0000" values="0;0;1;1"/><text x="112" y="424" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">切り捨て</text>
<text x="112" y="446" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">色相 0°(差 23°)</text>
<text x="112" y="468" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">白く潰れる</text>
</g>
<circle cx="296" cy="432" r="24" fill="#f5ebbe" stroke="#334155" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7347;0.7349;1.0000" values="0;0;1;1"/></circle>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7347;0.7349;1.0000" values="0;0;1;1"/><text x="332" y="424" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">Reinhard</text>
<text x="332" y="446" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">色相 48°(差 25°)</text>
<text x="332" y="468" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">くすんで暗い</text>
</g>
<circle cx="516" cy="432" r="24" fill="#fffde9" stroke="#334155" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7347;0.7349;1.0000" values="0;0;1;1"/></circle>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7347;0.7349;1.0000" values="0;0;1;1"/><text x="552" y="424" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">ACES</text>
<text x="552" y="446" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">色相 55°(差 32°)</text>
<text x="552" y="468" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">鮮やか(少し黄寄り)</text>
</g>
<circle cx="736" cy="432" r="24" fill="#fffcbe" stroke="#334155" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7347;0.7349;1.0000" values="0;0;1;1"/></circle>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7347;0.7349;1.0000" values="0;0;1;1"/><text x="772" y="424" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">Hable</text>
<text x="772" y="446" text-anchor="start" style="font-size:12px;font-weight:500;fill:#1f2937">色相 57°(差 34°)</text>
<text x="772" y="468" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">なだらか</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">同じ明るさの並びを、4 つの方法で画面に出す<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">上から順に: 切り捨て、Reinhard、ACES、Hable<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;0.7161;0.7163;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">切り捨てだと、明るい所が全部白に潰れる。曲線で圧縮すると、明るい所の差も残る<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7161;0.7163;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:tonemap-curves:end -->

グラフの曲線を見比べてください。単純なクランプは、1 で急に頭打ちになるので、明部が真っ白に潰れます。Reinhard はなだらかですが、中間も持ち上がって低コントラストになります。Hable と ACES は、暗部を締めて、明部を滑らかにロールオフさせる S 字になります。

## Which One to Choose {#どれを選ぶか}

| 目的 | 選ぶ曲線 |
| --- | --- |
| **とにかく簡単に** | <strong>Reinhard（白点付き）</strong> |
| **映画のような締まった画** | **ACES 近似・Hable** |
| **色が破綻しにくい中立** | **AgX・Khronos PBR Neutral** |
| **画作りを細かく制御** | **独自の曲線を 3D LUT にする**（[カラー グレーディング](../color-grading/index.md)） |

## Related Pages {#関連ページ}

- [Post-Processing](../index.md)
- [Bloom](../bloom/index.md)
- [Color Grading](../color-grading/index.md)
- [PBR](../../../3d/pbr.md)
