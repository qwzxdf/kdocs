---
title: Weighted Blended OIT (WBOIT)
tags:
  - 描画
---

# Weighted Blended OIT (WBOIT)

**WBOIT は、深度に応じた重みで、半透明の色を加重平均する、近似の手法**です。**1 パスで描けて、とても軽い**ので、**実用的**です。**ただし、近似なので、正確さは劣ります**。このページでは、**WBOIT の式と、重みの選び方**を説明します。

!!! tip "ポイント"
    - **色の合計と、アルファの積を、2 枚のバッファに蓄積**する。
    - **手前ほど重く**する**重み関数**を使う。
    - **1 パスで、ソート不要**。
    - **近似なので、色の順序が正確でない**。

## Weighted Blended OIT
**順序を無視**して、**深度に応じた「重み」を付けた加重平均**で**合成**する、**近似手法**です（**McGuire と Bavoil、2013**）。**1 パスで描け、レンダー ターゲット 2 枚だけ**なので、**軽く**、**ゲームで実用的**です。

<!-- fig:wboit-layers:begin -->

<svg class="fig illust motion" data-fig="wboit-layers" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-wboit-layers" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">WBOIT: 並べ替えずに、重みを付けて 1 回で混ぜる(半透明 3 枚)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 28 画素に、赤・緑・青の半透明を重ねる。正解は「奥から順に混ぜた」結果</text>
<text x="60.0" y="98" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">半透明の 3 枚(深度 3 / 6 / 12)</text>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;1.0000" values="0;0;1;1"/><rect x="110.0" y="106" width="375.0" height="22" fill="#ff4040" fill-opacity="0.5"/>
<text x="116.0" y="122" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">赤 α=0.5 深度 3</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1126;0.1128;1.0000" values="0;0;1;1"/><rect x="260.0" y="132" width="375.0" height="22" fill="#33cc4c" fill-opacity="0.6"/>
<text x="266.0" y="148" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">緑 α=0.6 深度 6</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1742;0.1744;1.0000" values="0;0;1;1"/><rect x="360.0" y="158" width="375.0" height="22" fill="#3366ff" fill-opacity="0.5"/>
<text x="366.0" y="174" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">青 α=0.5 深度 12</text>
</g>
<text x="60.0" y="201" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">正解(奥から順に混ぜる = 並べ替えが必要)</text>
<rect x="60.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2564" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="85.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2626" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="110.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2687" values="#e5e7eb;#f99999"/></rect>
<rect x="135.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2749" values="#e5e7eb;#f99999"/></rect>
<rect x="160.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2810" values="#e5e7eb;#f99999"/></rect>
<rect x="185.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2872" values="#e5e7eb;#f99999"/></rect>
<rect x="210.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2933" values="#e5e7eb;#f99999"/></rect>
<rect x="235.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2995" values="#e5e7eb;#f99999"/></rect>
<rect x="260.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3056" values="#e5e7eb;#bf8e67"/></rect>
<rect x="285.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3118" values="#e5e7eb;#bf8e67"/></rect>
<rect x="310.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3179" values="#e5e7eb;#bf8e67"/></rect>
<rect x="335.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3241" values="#e5e7eb;#bf8e67"/></rect>
<rect x="360.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3303" values="#e5e7eb;#ac8069"/></rect>
<rect x="385.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3364" values="#e5e7eb;#ac8069"/></rect>
<rect x="410.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3426" values="#e5e7eb;#ac8069"/></rect>
<rect x="435.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3487" values="#e5e7eb;#ac8069"/></rect>
<rect x="460.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3549" values="#e5e7eb;#ac8069"/></rect>
<rect x="485.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3610" values="#e5e7eb;#59bf91"/></rect>
<rect x="510.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3672" values="#e5e7eb;#59bf91"/></rect>
<rect x="535.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3733" values="#e5e7eb;#59bf91"/></rect>
<rect x="560.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3795" values="#e5e7eb;#59bf91"/></rect>
<rect x="585.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3856" values="#e5e7eb;#59bf91"/></rect>
<rect x="610.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3918" values="#e5e7eb;#59bf91"/></rect>
<rect x="635.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3979" values="#e5e7eb;#93acf9"/></rect>
<rect x="660.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4041" values="#e5e7eb;#93acf9"/></rect>
<rect x="685.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4103" values="#e5e7eb;#93acf9"/></rect>
<rect x="710.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4164" values="#e5e7eb;#93acf9"/></rect>
<rect x="735.0" y="206.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4226" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="60.0" y="206" width="700.0" height="25.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="257" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">描いた順に混ぜる(並べ替えなし)</text>
<rect x="60.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4697" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="85.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4759" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="110.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4821" values="#e5e7eb;#f99999"/></rect>
<rect x="135.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4882" values="#e5e7eb;#f99999"/></rect>
<rect x="160.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4944" values="#e5e7eb;#f99999"/></rect>
<rect x="185.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5005" values="#e5e7eb;#f99999"/></rect>
<rect x="210.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5067" values="#e5e7eb;#f99999"/></rect>
<rect x="235.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5128" values="#e5e7eb;#f99999"/></rect>
<rect x="260.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5190" values="#e5e7eb;#82b86b"/></rect>
<rect x="285.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5251" values="#e5e7eb;#82b86b"/></rect>
<rect x="310.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5313" values="#e5e7eb;#82b86b"/></rect>
<rect x="335.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5374" values="#e5e7eb;#82b86b"/></rect>
<rect x="360.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5436" values="#e5e7eb;#5b8fb5"/></rect>
<rect x="385.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5497" values="#e5e7eb;#5b8fb5"/></rect>
<rect x="410.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5559" values="#e5e7eb;#5b8fb5"/></rect>
<rect x="435.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5621" values="#e5e7eb;#5b8fb5"/></rect>
<rect x="460.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5682" values="#e5e7eb;#5b8fb5"/></rect>
<rect x="485.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5744" values="#e5e7eb;#59a1c7"/></rect>
<rect x="510.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5805" values="#e5e7eb;#59a1c7"/></rect>
<rect x="535.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5867" values="#e5e7eb;#59a1c7"/></rect>
<rect x="560.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5928" values="#e5e7eb;#59a1c7"/></rect>
<rect x="585.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5990" values="#e5e7eb;#59a1c7"/></rect>
<rect x="610.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6051" values="#e5e7eb;#59a1c7"/></rect>
<rect x="635.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6113" values="#e5e7eb;#93acf9"/></rect>
<rect x="660.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6174" values="#e5e7eb;#93acf9"/></rect>
<rect x="685.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6236" values="#e5e7eb;#93acf9"/></rect>
<rect x="710.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6297" values="#e5e7eb;#93acf9"/></rect>
<rect x="735.0" y="262.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6359" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="60.0" y="262" width="700.0" height="25.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="313" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">WBOIT(重み付き平均・並べ替えなし)</text>
<rect x="60.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6831" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="85.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6892" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="110.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f99999"/></rect>
<rect x="135.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7015" values="#e5e7eb;#f99999"/></rect>
<rect x="160.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7077" values="#e5e7eb;#f99999"/></rect>
<rect x="185.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7138" values="#e5e7eb;#f99999"/></rect>
<rect x="210.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7200" values="#e5e7eb;#f99999"/></rect>
<rect x="235.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7262" values="#e5e7eb;#f99999"/></rect>
<rect x="260.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7323" values="#e5e7eb;#d77d66"/></rect>
<rect x="285.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7385" values="#e5e7eb;#d77d66"/></rect>
<rect x="310.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7446" values="#e5e7eb;#d77d66"/></rect>
<rect x="335.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7508" values="#e5e7eb;#d77d66"/></rect>
<rect x="360.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7569" values="#e5e7eb;#cd6f5c"/></rect>
<rect x="385.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7631" values="#e5e7eb;#cd6f5c"/></rect>
<rect x="410.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7692" values="#e5e7eb;#cd6f5c"/></rect>
<rect x="435.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7754" values="#e5e7eb;#cd6f5c"/></rect>
<rect x="460.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7815" values="#e5e7eb;#cd6f5c"/></rect>
<rect x="485.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7877" values="#e5e7eb;#59c686"/></rect>
<rect x="510.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7938" values="#e5e7eb;#59c686"/></rect>
<rect x="535.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8000" values="#e5e7eb;#59c686"/></rect>
<rect x="560.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8062" values="#e5e7eb;#59c686"/></rect>
<rect x="585.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8123" values="#e5e7eb;#59c686"/></rect>
<rect x="610.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8185" values="#e5e7eb;#59c686"/></rect>
<rect x="635.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8246" values="#e5e7eb;#93acf9"/></rect>
<rect x="660.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8308" values="#e5e7eb;#93acf9"/></rect>
<rect x="685.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8369" values="#e5e7eb;#93acf9"/></rect>
<rect x="710.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8431" values="#e5e7eb;#93acf9"/></rect>
<rect x="735.0" y="318.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8492" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="60.0" y="318" width="700.0" height="25.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="380" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">WBOIT が 1 回の描画で貯める 2 つの値</text>
<rect x="60.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6831" values="#e5e7eb;#f1f5f9"/></rect>
<rect x="85.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6892" values="#e5e7eb;#f1f5f9"/></rect>
<rect x="110.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#9b6cf0"/></rect>
<rect x="135.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7015" values="#e5e7eb;#9b6cf0"/></rect>
<rect x="160.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7077" values="#e5e7eb;#9b6cf0"/></rect>
<rect x="185.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7138" values="#e5e7eb;#9b6cf0"/></rect>
<rect x="210.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7200" values="#e5e7eb;#9b6cf0"/></rect>
<rect x="235.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7262" values="#e5e7eb;#9b6cf0"/></rect>
<rect x="260.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7323" values="#e5e7eb;#8143ee"/></rect>
<rect x="285.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7385" values="#e5e7eb;#8143ee"/></rect>
<rect x="310.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7446" values="#e5e7eb;#8143ee"/></rect>
<rect x="335.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7508" values="#e5e7eb;#8143ee"/></rect>
<rect x="360.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7569" values="#e5e7eb;#7c3aed"/></rect>
<rect x="385.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7631" values="#e5e7eb;#7c3aed"/></rect>
<rect x="410.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7692" values="#e5e7eb;#7c3aed"/></rect>
<rect x="435.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7754" values="#e5e7eb;#7c3aed"/></rect>
<rect x="460.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7815" values="#e5e7eb;#7c3aed"/></rect>
<rect x="485.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7877" values="#e5e7eb;#d2c3f6"/></rect>
<rect x="510.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7938" values="#e5e7eb;#d2c3f6"/></rect>
<rect x="535.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8000" values="#e5e7eb;#d2c3f6"/></rect>
<rect x="560.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8062" values="#e5e7eb;#d2c3f6"/></rect>
<rect x="585.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8123" values="#e5e7eb;#d2c3f6"/></rect>
<rect x="610.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8185" values="#e5e7eb;#d2c3f6"/></rect>
<rect x="635.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8246" values="#e5e7eb;#ececf8"/></rect>
<rect x="660.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8308" values="#e5e7eb;#ececf8"/></rect>
<rect x="685.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8369" values="#e5e7eb;#ececf8"/></rect>
<rect x="710.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8431" values="#e5e7eb;#ececf8"/></rect>
<rect x="735.0" y="388.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8492" values="#e5e7eb;#f1f5f9"/></rect>
<rect x="60.0" y="388" width="700.0" height="25.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="60.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6831" values="#e5e7eb;#f1f5f9"/></rect>
<rect x="85.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6892" values="#e5e7eb;#f1f5f9"/></rect>
<rect x="110.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#80cdf1"/></rect>
<rect x="135.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7015" values="#e5e7eb;#80cdf1"/></rect>
<rect x="160.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7077" values="#e5e7eb;#80cdf1"/></rect>
<rect x="185.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7138" values="#e5e7eb;#80cdf1"/></rect>
<rect x="210.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7200" values="#e5e7eb;#80cdf1"/></rect>
<rect x="235.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7262" values="#e5e7eb;#80cdf1"/></rect>
<rect x="260.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7323" values="#e5e7eb;#3bb5ec"/></rect>
<rect x="285.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7385" values="#e5e7eb;#3bb5ec"/></rect>
<rect x="310.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7446" values="#e5e7eb;#3bb5ec"/></rect>
<rect x="335.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7508" values="#e5e7eb;#3bb5ec"/></rect>
<rect x="360.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7569" values="#e5e7eb;#25adeb"/></rect>
<rect x="385.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7631" values="#e5e7eb;#25adeb"/></rect>
<rect x="410.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7692" values="#e5e7eb;#25adeb"/></rect>
<rect x="435.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7754" values="#e5e7eb;#25adeb"/></rect>
<rect x="460.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7815" values="#e5e7eb;#25adeb"/></rect>
<rect x="485.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7877" values="#e5e7eb;#3bb5ec"/></rect>
<rect x="510.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7938" values="#e5e7eb;#3bb5ec"/></rect>
<rect x="535.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8000" values="#e5e7eb;#3bb5ec"/></rect>
<rect x="560.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8062" values="#e5e7eb;#3bb5ec"/></rect>
<rect x="585.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8123" values="#e5e7eb;#3bb5ec"/></rect>
<rect x="610.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8185" values="#e5e7eb;#3bb5ec"/></rect>
<rect x="635.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8246" values="#e5e7eb;#80cdf1"/></rect>
<rect x="660.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8308" values="#e5e7eb;#80cdf1"/></rect>
<rect x="685.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8369" values="#e5e7eb;#80cdf1"/></rect>
<rect x="710.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8431" values="#e5e7eb;#80cdf1"/></rect>
<rect x="735.0" y="414.0" width="25.3" height="25.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.8492" values="#e5e7eb;#f1f5f9"/></rect>
<rect x="60.0" y="414" width="700.0" height="25.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="768.0" y="403" text-anchor="start" style="font-size:11px;font-weight:500;fill:#7c3aed">合計(α×重み)</text>
<text x="768.0" y="429" text-anchor="start" style="font-size:11px;font-weight:500;fill:#0ea5e9">1 − 透過率</text>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.8962;0.8964;1.0000" values="0;0;1;1"/><rect x="60" y="450" width="840" height="62" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="76" y="474" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">正解とのずれ(平均): 描いた順 0.084 / WBOIT 0.027</text>
<text x="76" y="498" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">WBOIT は、手前ほど重みを大きくして平均する。並べ替えなしの 1 パスで、順序を近似する</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">半透明は、混ぜる順番で色が変わる<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">3 枚が重なる(描いた順 = 手前から)<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;0.2562;0.2564;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">正解: 奥から順に混ぜる。事前の並べ替えが必要<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2562;0.2564;0.4695;0.4697;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">描いた順にそのまま混ぜると、順序が逆なので色が違う<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4695;0.4697;0.6829;0.6831;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">WBOIT: 重み付き平均と、透過率の積を貯めて、最後に合成<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6829;0.6831;0.8962;0.8964;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">完全には一致しないが、並べ替えなしで、かなり近い<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.8962;0.8964;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:wboit-layers:end -->

### 考え方

**手前の物ほど、重みを大きく**して、**平均**します。**順序を知らなくても、「手前らしさ」を深度から推定**して、**近似的な順序づけ**を得ます。

<div class="formula">C = Σ(Cᵢ · αᵢ · wᵢ) / Σ(αᵢ · wᵢ)　、　α_total = 1 − Π(1 − αᵢ)</div>

記号の意味です。wᵢ は層 i の重みで、深度が小さい（手前）ほど大きくなります。Σ(Cᵢ αᵢ wᵢ) は重み付きの色の合計（アキュムレーション）です。Π(1 − αᵢ) は全層の透過率の積で、リビール（背景の見える割合）と呼びます。

原典は、McGuire と Bavoil の "Weighted Blended Order-Independent Transparency"（Journal of Computer Graphics Techniques、2013）です。

### 2 枚のレンダー ターゲット

2 枚のレンダー ターゲットを使います。アキュムレーションは `R16G16B16A16_FLOAT` で、`(Cᵢ·αᵢ·wᵢ, αᵢ·wᵢ)` を加算します（ブレンドは ONE / ONE）。リビールは `R8_UNORM` で、`αᵢ` を透過率として乗算します（ブレンドは ZERO / INV_SRC_COLOR で、`(1 − αᵢ)` を掛けます）。

```hlsl
struct PsOutput {
  float4 accumulation : SV_Target0;
  float reveal : SV_Target1;
};

PsOutput PSWeighted(VsOutput input) {
  float4 color = Shade(input);
  float z = input.position.z;
  float weight = max(min(1.0, max(max(color.r, color.g), color.b) * color.a), color.a) *
                 clamp(0.03 / (1e-5 + pow(z / 200.0, 4.0)), 1e-2, 3e3);

  PsOutput output;
  output.accumulation = float4(color.rgb * color.a, color.a) * weight;
  output.reveal = color.a;
  return output;
}
```

出力のコードの要点です。`weight` は McGuire らの、深度に基づく重み関数で、手前（z 小）ほど大きくなります。`output.accumulation` は `(RGB·α·w, α·w)` で、加算ブレンドで累積します。`output.reveal` は `α` で、乗算ブレンドにより `(1 − α)` の積が残ります。

### 合成

```hlsl
float4 PSComposite(VsOutput input) : SV_Target {
  float4 accum = accumulation_texture.Load(int3(input.position.xy, 0));
  float reveal = reveal_texture.Load(int3(input.position.xy, 0)).r;
  if (reveal >= 0.999) discard;
  float3 average_color = accum.rgb / max(accum.a, 1e-5);
  return float4(average_color, 1.0 - reveal);
}
```

合成のコードの要点です。`reveal`（背景の見える割合）が 1 なら、半透明が何もないので、描かずに捨てます。`average_color` は重み付き平均の色です。出力アルファ `1 − reveal` は、半透明全体の不透明度で、通常のアルファ ブレンドで背景に重ねます。

WBOIT の利点は、1 パスで軽いこと（2 枚の RT）、ソート不要なこと、パーティクル・草・髪などの大量の重なりに強いことです。欠点は、近似であること（同じ色の層が多いと順序が反映されません）、色が違う層の重なりで順序が違って見えること（手前の赤と奥の青が混ざって見える）、重み関数の調整が必要なこと（シーンの深度範囲に合わせます）です。

## よくあるミス

??? failure "半透明の重なりの色が、不自然"
    **重み関数を調整**する、または **PPLL**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **重み付き平均で、近似**
    - [x] **軽くて、実用的**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [OIT](index.md)
- [PPLL](ppll.md)
- [Hybrid Approaches and Choosing](hybrid.md)
