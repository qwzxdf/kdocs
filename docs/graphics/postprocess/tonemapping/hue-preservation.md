---
title: Preserving Hue
tags:
  - 描画
---

# Preserving Hue

<strong>トーンマップ曲線を R・G・B に別々に掛けるか、輝度にだけ掛けるか</strong>で明るい色の見え方が大きく変わります。別々に掛けると彩度の高い明るい色の比率が崩れ、色相がずれます。輝度にだけ掛けると色相は保てますが派手な色が飽和しすぎます。このページでは、2 つの方式の違い・ハイブリッド・彩度の扱い・どう選ぶかを説明します。

!!! tip "ポイント"
    - <strong>チャンネルごと</strong>：<strong>R・G・B に別々に曲線</strong>。フィルムの特性に近く、明部は白へ向かう。色相はずれる。
    - 輝度ベース：輝度にだけ曲線を掛け、色の比率を保つ。色相は保つが鮮やかな明部が飽和しすぎる。
    - ハイブリッド：両者を混ぜる。ACES・AgX は内部で彩度・色相を調整している。
    - 彩度：輝度が大きいほど、彩度を落とすのが自然な白への向かい方。
    - 選び方：色の忠実さ → 輝度ベース寄り、映画的な絵 → チャンネルごと寄り。

!!! info "このページを読む前に"
    - [Tone Mapping and Exposure](index.md)（このセクション全体の地図と、読む順番）

<!-- fig:hue-preserve:begin -->

<svg class="fig illust motion" data-fig="hue-preserve" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-hue-preserve" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">色相の保存: 色ごとにトーンマップすると、明るい所で色が白くずれる。明るさだけを圧縮すると、色が保たれる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">オレンジ(R:G:B = 1 : 0.45 : 0.1)の明るさを 0.1 〜 16 倍。2 通りの方法で、色相(色の種類)の変化を計算する</text>
<text x="70.0" y="114" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">色ごとにトーンマップ(R, G, B それぞれに x ÷ (1 + x))</text>
<rect x="70.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#e5e7eb;#563d1f"/></rect>
<rect x="98.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744" values="#e5e7eb;#5d4222"/></rect>
<rect x="126.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#644825"/></rect>
<rect x="154.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#e5e7eb;#6b4e28"/></rect>
<rect x="182.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#e5e7eb;#73542c"/></rect>
<rect x="210.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930" values="#e5e7eb;#7c5b30"/></rect>
<rect x="238.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#e5e7eb;#846234"/></rect>
<rect x="266.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023" values="#e5e7eb;#8d6a38"/></rect>
<rect x="294.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#e5e7eb;#96713d"/></rect>
<rect x="322.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#e5e7eb;#9f7a42"/></rect>
<rect x="350.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#e5e7eb;#a78248"/></rect>
<rect x="378.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209" values="#e5e7eb;#b08b4e"/></rect>
<rect x="406.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#e5e7eb;#b89454"/></rect>
<rect x="434.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1302" values="#e5e7eb;#c09c5b"/></rect>
<rect x="462.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1349" values="#e5e7eb;#c7a562"/></rect>
<rect x="490.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1395" values="#e5e7eb;#ceae6a"/></rect>
<rect x="518.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1442" values="#e5e7eb;#d4b671"/></rect>
<rect x="546.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1488" values="#e5e7eb;#dabe7a"/></rect>
<rect x="574.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1535" values="#e5e7eb;#dfc682"/></rect>
<rect x="602.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1581" values="#e5e7eb;#e4cd8b"/></rect>
<rect x="630.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1628" values="#e5e7eb;#e8d394"/></rect>
<rect x="658.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1674" values="#e5e7eb;#ebd99c"/></rect>
<rect x="686.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1721" values="#e5e7eb;#eedea5"/></rect>
<rect x="714.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1767" values="#e5e7eb;#f1e3ae"/></rect>
<rect x="742.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1814" values="#e5e7eb;#f3e7b6"/></rect>
<rect x="770.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1860" values="#e5e7eb;#f5ebbe"/></rect>
<rect x="798.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1907" values="#e5e7eb;#f7eec6"/></rect>
<rect x="826.0" y="120.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1953" values="#e5e7eb;#f8f0cd"/></rect>
<rect x="70.0" y="120" width="784.0" height="28.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="70.0" y="184" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">明るさ(輝度)だけを圧縮して、色の比率は保つ</text>
<rect x="70.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2558" values="#e5e7eb;#573d1f"/></rect>
<rect x="98.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2605" values="#e5e7eb;#5f4221"/></rect>
<rect x="126.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2651" values="#e5e7eb;#674724"/></rect>
<rect x="154.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#e5e7eb;#6f4d27"/></rect>
<rect x="182.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2744" values="#e5e7eb;#78532a"/></rect>
<rect x="210.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#815a2d"/></rect>
<rect x="238.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2837" values="#e5e7eb;#8b6131"/></rect>
<rect x="266.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2884" values="#e5e7eb;#966835"/></rect>
<rect x="294.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2930" values="#e5e7eb;#a17038"/></rect>
<rect x="322.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2977" values="#e5e7eb;#ac783c"/></rect>
<rect x="350.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3023" values="#e5e7eb;#b77f40"/></rect>
<rect x="378.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3070" values="#e5e7eb;#c38844"/></rect>
<rect x="406.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3116" values="#e5e7eb;#cf9049"/></rect>
<rect x="434.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3163" values="#e5e7eb;#da984d"/></rect>
<rect x="462.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3209" values="#e5e7eb;#e5a051"/></rect>
<rect x="490.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3256" values="#e5e7eb;#f0a754"/></rect>
<rect x="518.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3302" values="#e5e7eb;#fbaf58"/></rect>
<rect x="546.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3349" values="#e5e7eb;#ffb55c"/></rect>
<rect x="574.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3395" values="#e5e7eb;#ffbc5f"/></rect>
<rect x="602.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3442" values="#e5e7eb;#ffc262"/></rect>
<rect x="630.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3488" values="#e5e7eb;#ffc765"/></rect>
<rect x="658.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3535" values="#e5e7eb;#ffcc67"/></rect>
<rect x="686.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3581" values="#e5e7eb;#ffd069"/></rect>
<rect x="714.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3628" values="#e5e7eb;#ffd46b"/></rect>
<rect x="742.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3674" values="#e5e7eb;#ffd86d"/></rect>
<rect x="770.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3721" values="#e5e7eb;#ffda6e"/></rect>
<rect x="798.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3767" values="#e5e7eb;#ffdd70"/></rect>
<rect x="826.0" y="190.0" width="28.3" height="28.3" fill="#e5e7eb"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3814" values="#e5e7eb;#ffdf71"/></rect>
<rect x="70.0" y="190" width="784.0" height="28.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="70.0" y="262" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">← 暗い(×0.1)                       明るい(×16) →</text>
<rect x="30" y="286" width="900" height="190" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="276" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">色相のずれ(度)。元のオレンジ = 23°</text>
<path d="M70.0,447.6 L100.37,446.35 L130.74,444.86 L161.11,443.11 L191.48,441.06 L221.85,438.66 L252.22,435.87 L282.59,432.66 L312.96,428.99 L343.33,424.83 L373.7,420.18 L404.07,415.02 L434.44,409.38 L464.81,403.3 L495.19,396.85 L525.56,390.11 L555.93,383.2 L586.3,376.22 L616.67,369.31 L647.04,362.57 L677.41,356.12 L707.78,350.05 L738.15,344.41 L768.52,339.25 L798.89,334.6 L829.26,330.44 L859.63,326.77 L890.0,323.57" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4649;0.4651;1.0000" values="0;0;1;1"/></path>
<path d="M70.0,454.0 L100.37,454.0 L130.74,454.0 L161.11,454.0 L191.48,454.0 L221.85,454.0 L252.22,454.0 L282.59,454.0 L312.96,454.0 L343.33,454.0 L373.7,454.0 L404.07,454.0 L434.44,454.0 L464.81,454.0 L495.19,454.0 L525.56,454.0 L555.93,454.0 L586.3,447.02 L616.67,435.47 L647.04,424.21 L677.41,413.4 L707.78,403.2 L738.15,393.72 L768.52,385.04 L798.89,377.2 L829.26,370.19 L859.63,364.0 L890.0,358.57" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5347;0.5349;1.0000" values="0;0;1;1"/></path>
<circle cx="86" cy="466" r="6" fill="#e5484d"/>
<text x="96" y="470" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">色ごと(最大ずれ 25°)</text>
<circle cx="260.2" cy="466" r="6" fill="#2ea043"/>
<text x="270.2" y="470" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">輝度だけ(最大ずれ 18°)</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6277;0.6279;1.0000" values="0;0;1;1"/><rect x="80" y="300" width="470" height="70" rx="12" fill="#faf5ff" stroke="#7c3aed" stroke-width="2.5"/>
<text x="96" y="324" text-anchor="start" style="font-size:13px;font-weight:700;fill:#991b1b">色ごと: 明るいほど、白っぽくなる(彩度 0.90 → 0.35)</text>
<text x="96" y="346" text-anchor="start" style="font-size:13px;font-weight:700;fill:#166534">輝度だけ: 色相が保たれる。ただし、1 を超える成分は切る必要がある</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">明るい炎は、色ごとに圧縮すると、白に近づく(色が失われる)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">2 通りで、明るさ 28 段階を塗る<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.4649;0.4651;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">輝度だけを圧縮すると、色相が保たれる。どちらが良いかは、絵作りで決める<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.4649;0.4651;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:hue-preserve:end -->

## 違いを見る

<strong>赤 (4.0, 0.5, 0.2) という、明るい赤橙</strong>をReinhard に通すと、次のようになります。

| 方式 | 計算 | 結果（R, G, B） |
| --- | --- | --- |
| 入力 | — | (4.0, 0.5, 0.2) |
| チャンネルごと | 各成分に `x/(1+x)` | (0.80, 0.33, 0.17) |
| 輝度ベース | 輝度 L ≒ 1.2 → L/(1+L) ≒ 0.55、色に比を掛ける | (1.0 を超える → 飽和) |

チャンネルごとだと、R の比率が下がって、G・B の比率が相対的に上がるため、赤が少し黄色（橙）寄りに見えます。これがフィルムのような、明部の色の変化です。

<svg class="fig illust" viewBox="0 0 780 220" role="img" aria-label="色相の変化の比較">
<text x="20" y="26" class="fig-title">赤橙の光をだんだん明るくしていくと</text>
<defs>
<linearGradient id="hp-ch" x1="0" x2="1"><stop offset="0" stop-color="#7a1d10"/><stop offset="0.4" stop-color="#e5602f"/><stop offset="0.75" stop-color="#ffb24a"/><stop offset="1" stop-color="#fff2c6"/></linearGradient>
<linearGradient id="hp-lum" x1="0" x2="1"><stop offset="0" stop-color="#7a1d10"/><stop offset="0.5" stop-color="#e5483a"/><stop offset="1" stop-color="#ff5a45"/></linearGradient>
<linearGradient id="hp-hy" x1="0" x2="1"><stop offset="0" stop-color="#7a1d10"/><stop offset="0.5" stop-color="#e5543a"/><stop offset="0.85" stop-color="#ff9a6a"/><stop offset="1" stop-color="#ffe9d6"/></linearGradient>
</defs>
<g font-size="13">
<text x="40" y="62" style="font-weight:700">チャンネルごと</text><rect x="40" y="70" width="500" height="26" fill="url(#hp-ch)"/><text x="560" y="88" style="font-size:10px">橙 → 黄 → 白（フィルム的、色相は変わる）</text>
<text x="40" y="126" style="font-weight:700">輝度ベース</text><rect x="40" y="134" width="500" height="26" fill="url(#hp-lum)"/><text x="560" y="152" style="font-size:10px">赤のまま（色相は保つが、白に届かず飽和）</text>
<text x="40" y="190" style="font-weight:700">ハイブリッド</text><rect x="40" y="198" width="500" height="18" fill="url(#hp-hy)"/><text x="560" y="212" style="font-size:12px">赤 → 淡い赤 → 白（自然）</text>
</g>
</svg>

## チャンネルごと

```hlsl
float3 TonemapPerChannel(float3 color) {
  return ACESNarkowicz(color);
}
```

| 長所 | 短所 |
| --- | --- |
| 明るい色が自然に白へ向かう | 色相が変わる（青 → 紫、赤 → 黄） |
| 実装が簡単 | 意図した色が強い光で変わる（エフェクト） |
| フィルムのような質感 | — |

## 輝度ベース

```hlsl
float Luminance(float3 c) {
  return dot(c, float3(0.2126, 0.7152, 0.0722));
}

float3 TonemapByLuminance(float3 color) {
  float l = Luminance(color);
  float mapped = Reinhard(float3(l, l, l)).x;
  return color * (mapped / max(l, 1e-4));
}
```

輝度ベースの長所は、色相が完全に保たれることと、意図した色のままになることです。短所は、彩度の高い明るい色が 1 を超えて飽和すること（最後に切ると色が濃すぎる）と、白に向かわないので眩しさが出にくいことです。

<strong>1 を超える値の処理</strong>が課題です。飽和した成分を他の成分に分配（ガマット マッピング）したり、白へ混ぜたりして対処します。

## ハイブリッド

<strong>両者を混ぜる</strong>のが定番です。

```hlsl
float3 TonemapHybrid(float3 color, float blend) {
  float3 per_channel = ACESNarkowicz(color);
  float l = Luminance(color);
  float l_mapped = Luminance(per_channel);
  float3 by_luminance = color * (l_mapped / max(l, 1e-4));
  return lerp(by_luminance, per_channel, blend);
}
```

`blend` の値による見た目です。0 なら色相を完全に保ちます（輝度ベース）。1 ならフィルム的になります（チャンネルごと）。0.3〜0.6 が、ほどよく自然です。

## 彩度を落として白へ向かわせる

<strong>実際の光は明るいと目やセンサーの飽和で白っぽく</strong>見えます。輝度が大きいほど彩度を落とすと、自然に白へ向かいます。

```hlsl
float3 DesaturateHighlights(float3 color, float threshold, float strength) {
  float l = Luminance(color);
  float t = saturate((l - threshold) / threshold) * strength;
  return lerp(color, float3(l, l, l), t);
}
```

彩度を落とす方式のコードの要点です。`threshold` は、この輝度から彩度を落とし始める閾値です。`strength` は、どれだけ白へ向かうかを表します（0〜1）。トーンマップの前に HDR のうちに行います。

AgX・Tony McMapface は、こうした彩度の処理を曲線の設計に組み込んでいます。

## 選び方

| 優先すること | 選ぶ方式 |
| --- | --- |
| 映画的・フィルムの質感 | チャンネルごと（ACES・Hable） |
| 色の忠実さ・エフェクトの色が大事 | 輝度ベース寄りのハイブリッド、AgX |
| まず簡単に | チャンネルごと（1 行） |
| 色相の破綻を許さない | AgX・Tony McMapface・PBR Neutral |

## よくあるミス

??? failure "輝度ベースで、1 を超えた値をそのまま出力して、色が破綻する"
    <strong>最後に `saturate`</strong>、またはガマット マッピング（超えた分を他の成分へ分配）。

??? failure "輝度の係数を BT.601（0.299, 0.587, 0.114）にしてしまう"
    sRGB（Rec.709）の原色なら、`(0.2126, 0.7152, 0.0722)`。

??? failure "彩度を落とす処理をトーンマップの後で行って、効きが弱い"
    HDR のうち（トーンマップの前）に行う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>チャンネルごと</strong> ＝ フィルム的。色相がずれる
    - [x] 輝度ベース ＝ 色相を保つが、鮮やかな明部が飽和
    - [x] ハイブリッド（blend 0.3〜0.6）が実用的
    - [x] 輝度が大きいほど彩度を落とすと自然に白へ
    - [x] 輝度の係数は Rec.709（0.2126, 0.7152, 0.0722）

## 参考

- Troy Sobotka, "AgX"（色相の保持）
- Pharr, Jakob, Humphreys, "Physically Based Rendering"（色と輝度）
- Hart, "Tone Mapping with Hue Preservation"（解説）

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [Reinhard](reinhard.md)
- [ACES](aces.md)
- [AgX and Others](agx.md)
