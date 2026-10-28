---
title: Outlines and Toon
tags:
  - 描画
---

# Outlines and Toon

<strong>写実的ではなく、アニメやイラストのような絵</strong>を<strong>作る技法</strong>が<strong>ノンフォトリアリスティック レンダリング（NPR）</strong>です。<strong>輪郭線（アウトライン）で形を強調し、陰影を数段階に区切る（セル シェーディング）</strong>ことで、<strong>「手描きのアニメ」風</strong>の絵になります。どれも写実より優れているわけではなく、作品の画風に合うかどうかの好みの問題です。このセクションでは、背面法の輪郭線・画面空間のエッジ検出・セル シェーディング・ポスタライズとハーフトーンを 1 つずつ別のページで説明します。

## 動きで見る

<!-- fig:toon-stages:begin -->

<svg class="fig illust motion" data-fig="toon-stages" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-toon-stages" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">トゥーンの手順: ベース色 → 段のある陰 → リム ライト → 輪郭線。1 層ずつ足す</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">球の断面(48 画素)。層を 1 つずつ足して、各段階の見え方を実際に計算する</text>
<text x="60.0" y="108" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">① ベース色(一様)</text>
<rect x="60.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667" values="#e5e7eb;#f9c294"/></rect>
<rect x="74.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0684" values="#e5e7eb;#f9c294"/></rect>
<rect x="89.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0702" values="#e5e7eb;#f9c294"/></rect>
<rect x="103.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0720" values="#e5e7eb;#f9c294"/></rect>
<rect x="118.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#e5e7eb;#f9c294"/></rect>
<rect x="132.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0756" values="#e5e7eb;#f9c294"/></rect>
<rect x="147.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0773" values="#e5e7eb;#f9c294"/></rect>
<rect x="161.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#f9c294"/></rect>
<rect x="176.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#e5e7eb;#f9c294"/></rect>
<rect x="190.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0827" values="#e5e7eb;#f9c294"/></rect>
<rect x="205.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#f9c294"/></rect>
<rect x="219.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0862" values="#e5e7eb;#f9c294"/></rect>
<rect x="234.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#f9c294"/></rect>
<rect x="248.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#f9c294"/></rect>
<rect x="263.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0916" values="#e5e7eb;#f9c294"/></rect>
<rect x="277.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0933" values="#e5e7eb;#f9c294"/></rect>
<rect x="292.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#e5e7eb;#f9c294"/></rect>
<rect x="306.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0969" values="#e5e7eb;#f9c294"/></rect>
<rect x="321.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0987" values="#e5e7eb;#f9c294"/></rect>
<rect x="335.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1004" values="#e5e7eb;#f9c294"/></rect>
<rect x="350.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1022" values="#e5e7eb;#f9c294"/></rect>
<rect x="364.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1040" values="#e5e7eb;#f9c294"/></rect>
<rect x="379.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1058" values="#e5e7eb;#f9c294"/></rect>
<rect x="393.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1076" values="#e5e7eb;#f9c294"/></rect>
<rect x="408.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093" values="#e5e7eb;#f9c294"/></rect>
<rect x="422.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111" values="#e5e7eb;#f9c294"/></rect>
<rect x="437.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1129" values="#e5e7eb;#f9c294"/></rect>
<rect x="451.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1147" values="#e5e7eb;#f9c294"/></rect>
<rect x="466.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1164" values="#e5e7eb;#f9c294"/></rect>
<rect x="480.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1182" values="#e5e7eb;#f9c294"/></rect>
<rect x="495.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#e5e7eb;#f9c294"/></rect>
<rect x="509.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1218" values="#e5e7eb;#f9c294"/></rect>
<rect x="524.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1236" values="#e5e7eb;#f9c294"/></rect>
<rect x="538.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1253" values="#e5e7eb;#f9c294"/></rect>
<rect x="553.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1271" values="#e5e7eb;#f9c294"/></rect>
<rect x="567.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1289" values="#e5e7eb;#f9c294"/></rect>
<rect x="582.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1307" values="#e5e7eb;#f9c294"/></rect>
<rect x="596.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1324" values="#e5e7eb;#f9c294"/></rect>
<rect x="611.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1342" values="#e5e7eb;#f9c294"/></rect>
<rect x="625.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1360" values="#e5e7eb;#f9c294"/></rect>
<rect x="640.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1378" values="#e5e7eb;#f9c294"/></rect>
<rect x="654.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1396" values="#e5e7eb;#f9c294"/></rect>
<rect x="669.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1413" values="#e5e7eb;#f9c294"/></rect>
<rect x="683.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1431" values="#e5e7eb;#f9c294"/></rect>
<rect x="698.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1449" values="#e5e7eb;#f9c294"/></rect>
<rect x="712.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1467" values="#e5e7eb;#f9c294"/></rect>
<rect x="727.0" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1484" values="#e5e7eb;#f9c294"/></rect>
<rect x="741.5" y="112.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1502" values="#e5e7eb;#f9c294"/></rect>
<rect x="60.0" y="112" width="696.0" height="40.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;1.0000" values="0;0;1;1"/><text x="766.0" y="128" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">色の種類 1</text>
<text x="766.0" y="148" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">平均の明るさ 0.60</text>
</g>
<text x="60.0" y="178" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">② 段のある陰を掛ける(3 段)</text>
<rect x="60.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2622" values="#e5e7eb;#f9c294"/></rect>
<rect x="74.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2640" values="#e5e7eb;#f9c294"/></rect>
<rect x="89.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2658" values="#e5e7eb;#f9c294"/></rect>
<rect x="103.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2676" values="#e5e7eb;#f9c294"/></rect>
<rect x="118.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2693" values="#e5e7eb;#f9c294"/></rect>
<rect x="132.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2711" values="#e5e7eb;#f9c294"/></rect>
<rect x="147.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2729" values="#e5e7eb;#f9c294"/></rect>
<rect x="161.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2747" values="#e5e7eb;#f9c294"/></rect>
<rect x="176.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2764" values="#e5e7eb;#f9c294"/></rect>
<rect x="190.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2782" values="#e5e7eb;#f9c294"/></rect>
<rect x="205.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#e5e7eb;#f9c294"/></rect>
<rect x="219.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2818" values="#e5e7eb;#f9c294"/></rect>
<rect x="234.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2836" values="#e5e7eb;#f9c294"/></rect>
<rect x="248.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2853" values="#e5e7eb;#f9c294"/></rect>
<rect x="263.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2871" values="#e5e7eb;#f9c294"/></rect>
<rect x="277.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2889" values="#e5e7eb;#f9c294"/></rect>
<rect x="292.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#e5e7eb;#f9c294"/></rect>
<rect x="306.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2924" values="#e5e7eb;#f9c294"/></rect>
<rect x="321.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2942" values="#e5e7eb;#f9c294"/></rect>
<rect x="335.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2960" values="#e5e7eb;#f9c294"/></rect>
<rect x="350.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2978" values="#e5e7eb;#f9c294"/></rect>
<rect x="364.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2996" values="#e5e7eb;#f9c294"/></rect>
<rect x="379.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3013" values="#e5e7eb;#f9c294"/></rect>
<rect x="393.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3031" values="#e5e7eb;#f9c294"/></rect>
<rect x="408.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3049" values="#e5e7eb;#f9c294"/></rect>
<rect x="422.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3067" values="#e5e7eb;#f9c294"/></rect>
<rect x="437.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3084" values="#e5e7eb;#f9c294"/></rect>
<rect x="451.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3102" values="#e5e7eb;#f9c294"/></rect>
<rect x="466.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3120" values="#e5e7eb;#f9c294"/></rect>
<rect x="480.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3138" values="#e5e7eb;#f9c294"/></rect>
<rect x="495.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3156" values="#e5e7eb;#f9c294"/></rect>
<rect x="509.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3173" values="#e5e7eb;#f9c294"/></rect>
<rect x="524.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3191" values="#e5e7eb;#e1b085"/></rect>
<rect x="538.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3209" values="#e5e7eb;#e1b085"/></rect>
<rect x="553.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3227" values="#e5e7eb;#e1b085"/></rect>
<rect x="567.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3244" values="#e5e7eb;#e1b085"/></rect>
<rect x="582.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#e1b085"/></rect>
<rect x="596.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3280" values="#e5e7eb;#e1b085"/></rect>
<rect x="611.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3298" values="#e5e7eb;#e1b085"/></rect>
<rect x="625.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3316" values="#e5e7eb;#e1b085"/></rect>
<rect x="640.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3333" values="#e5e7eb;#be9470"/></rect>
<rect x="654.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3351" values="#e5e7eb;#be9470"/></rect>
<rect x="669.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3369" values="#e5e7eb;#be9470"/></rect>
<rect x="683.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3387" values="#e5e7eb;#be9470"/></rect>
<rect x="698.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3404" values="#e5e7eb;#be9470"/></rect>
<rect x="712.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3422" values="#e5e7eb;#be9470"/></rect>
<rect x="727.0" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3440" values="#e5e7eb;#be9470"/></rect>
<rect x="741.5" y="182.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3458" values="#e5e7eb;#be9470"/></rect>
<rect x="60.0" y="182" width="696.0" height="40.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3509;0.3511;1.0000" values="0;0;1;1"/><text x="766.0" y="198" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">色の種類 3</text>
<text x="766.0" y="218" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">平均の明るさ 0.54</text>
</g>
<text x="60.0" y="248" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">③ リム ライト(縁を明るく)を足す</text>
<rect x="60.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4578" values="#e5e7eb;#fff3d2"/></rect>
<rect x="74.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4596" values="#e5e7eb;#f9c294"/></rect>
<rect x="89.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4613" values="#e5e7eb;#f9c294"/></rect>
<rect x="103.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4631" values="#e5e7eb;#f9c294"/></rect>
<rect x="118.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4649" values="#e5e7eb;#f9c294"/></rect>
<rect x="132.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4667" values="#e5e7eb;#f9c294"/></rect>
<rect x="147.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4684" values="#e5e7eb;#f9c294"/></rect>
<rect x="161.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#e5e7eb;#f9c294"/></rect>
<rect x="176.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4720" values="#e5e7eb;#f9c294"/></rect>
<rect x="190.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4738" values="#e5e7eb;#f9c294"/></rect>
<rect x="205.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#e5e7eb;#f9c294"/></rect>
<rect x="219.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4773" values="#e5e7eb;#f9c294"/></rect>
<rect x="234.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#e5e7eb;#f9c294"/></rect>
<rect x="248.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#e5e7eb;#f9c294"/></rect>
<rect x="263.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4827" values="#e5e7eb;#f9c294"/></rect>
<rect x="277.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4844" values="#e5e7eb;#f9c294"/></rect>
<rect x="292.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#e5e7eb;#f9c294"/></rect>
<rect x="306.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4880" values="#e5e7eb;#f9c294"/></rect>
<rect x="321.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4898" values="#e5e7eb;#f9c294"/></rect>
<rect x="335.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#e5e7eb;#f9c294"/></rect>
<rect x="350.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4933" values="#e5e7eb;#f9c294"/></rect>
<rect x="364.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4951" values="#e5e7eb;#f9c294"/></rect>
<rect x="379.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#e5e7eb;#f9c294"/></rect>
<rect x="393.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4987" values="#e5e7eb;#f9c294"/></rect>
<rect x="408.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5004" values="#e5e7eb;#f9c294"/></rect>
<rect x="422.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#e5e7eb;#f9c294"/></rect>
<rect x="437.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5040" values="#e5e7eb;#f9c294"/></rect>
<rect x="451.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5058" values="#e5e7eb;#f9c294"/></rect>
<rect x="466.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5076" values="#e5e7eb;#f9c294"/></rect>
<rect x="480.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5093" values="#e5e7eb;#f9c294"/></rect>
<rect x="495.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5111" values="#e5e7eb;#f9c294"/></rect>
<rect x="509.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5129" values="#e5e7eb;#f9c294"/></rect>
<rect x="524.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5147" values="#e5e7eb;#e1b085"/></rect>
<rect x="538.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5164" values="#e5e7eb;#e1b085"/></rect>
<rect x="553.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5182" values="#e5e7eb;#e1b085"/></rect>
<rect x="567.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5200" values="#e5e7eb;#e1b085"/></rect>
<rect x="582.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5218" values="#e5e7eb;#e1b085"/></rect>
<rect x="596.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5236" values="#e5e7eb;#e1b085"/></rect>
<rect x="611.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5253" values="#e5e7eb;#e1b085"/></rect>
<rect x="625.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5271" values="#e5e7eb;#e1b085"/></rect>
<rect x="640.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5289" values="#e5e7eb;#be9470"/></rect>
<rect x="654.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5307" values="#e5e7eb;#be9470"/></rect>
<rect x="669.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5324" values="#e5e7eb;#be9470"/></rect>
<rect x="683.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5342" values="#e5e7eb;#be9470"/></rect>
<rect x="698.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5360" values="#e5e7eb;#be9470"/></rect>
<rect x="712.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5378" values="#e5e7eb;#be9470"/></rect>
<rect x="727.0" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5396" values="#e5e7eb;#be9470"/></rect>
<rect x="741.5" y="252.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5413" values="#e5e7eb;#f0d2bd"/></rect>
<rect x="60.0" y="252" width="696.0" height="40.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5465;0.5467;1.0000" values="0;0;1;1"/><text x="766.0" y="268" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">色の種類 5</text>
<text x="766.0" y="288" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">平均の明るさ 0.55</text>
</g>
<text x="60.0" y="318" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">④ 輪郭線(視線に近い縁を黒く)</text>
<rect x="60.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6533" values="#e5e7eb;#fff3d2"/></rect>
<rect x="74.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6551" values="#e5e7eb;#f9c294"/></rect>
<rect x="89.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6569" values="#e5e7eb;#f9c294"/></rect>
<rect x="103.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6587" values="#e5e7eb;#f9c294"/></rect>
<rect x="118.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6604" values="#e5e7eb;#f9c294"/></rect>
<rect x="132.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6622" values="#e5e7eb;#f9c294"/></rect>
<rect x="147.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6640" values="#e5e7eb;#f9c294"/></rect>
<rect x="161.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6658" values="#e5e7eb;#f9c294"/></rect>
<rect x="176.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6676" values="#e5e7eb;#f9c294"/></rect>
<rect x="190.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6693" values="#e5e7eb;#f9c294"/></rect>
<rect x="205.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6711" values="#e5e7eb;#f9c294"/></rect>
<rect x="219.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6729" values="#e5e7eb;#f9c294"/></rect>
<rect x="234.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6747" values="#e5e7eb;#f9c294"/></rect>
<rect x="248.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6764" values="#e5e7eb;#f9c294"/></rect>
<rect x="263.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6782" values="#e5e7eb;#f9c294"/></rect>
<rect x="277.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#e5e7eb;#f9c294"/></rect>
<rect x="292.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6818" values="#e5e7eb;#f9c294"/></rect>
<rect x="306.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6836" values="#e5e7eb;#f9c294"/></rect>
<rect x="321.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6853" values="#e5e7eb;#f9c294"/></rect>
<rect x="335.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6871" values="#e5e7eb;#f9c294"/></rect>
<rect x="350.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6889" values="#e5e7eb;#f9c294"/></rect>
<rect x="364.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#e5e7eb;#f9c294"/></rect>
<rect x="379.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6924" values="#e5e7eb;#f9c294"/></rect>
<rect x="393.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6942" values="#e5e7eb;#f9c294"/></rect>
<rect x="408.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6960" values="#e5e7eb;#f9c294"/></rect>
<rect x="422.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6978" values="#e5e7eb;#f9c294"/></rect>
<rect x="437.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6996" values="#e5e7eb;#f9c294"/></rect>
<rect x="451.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7013" values="#e5e7eb;#f9c294"/></rect>
<rect x="466.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7031" values="#e5e7eb;#f9c294"/></rect>
<rect x="480.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7049" values="#e5e7eb;#f9c294"/></rect>
<rect x="495.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7067" values="#e5e7eb;#f9c294"/></rect>
<rect x="509.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7084" values="#e5e7eb;#f9c294"/></rect>
<rect x="524.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7102" values="#e5e7eb;#e1b085"/></rect>
<rect x="538.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7120" values="#e5e7eb;#e1b085"/></rect>
<rect x="553.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7138" values="#e5e7eb;#e1b085"/></rect>
<rect x="567.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7156" values="#e5e7eb;#e1b085"/></rect>
<rect x="582.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7173" values="#e5e7eb;#e1b085"/></rect>
<rect x="596.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7191" values="#e5e7eb;#e1b085"/></rect>
<rect x="611.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7209" values="#e5e7eb;#e1b085"/></rect>
<rect x="625.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7227" values="#e5e7eb;#e1b085"/></rect>
<rect x="640.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7244" values="#e5e7eb;#be9470"/></rect>
<rect x="654.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7262" values="#e5e7eb;#be9470"/></rect>
<rect x="669.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7280" values="#e5e7eb;#be9470"/></rect>
<rect x="683.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7298" values="#e5e7eb;#be9470"/></rect>
<rect x="698.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7316" values="#e5e7eb;#be9470"/></rect>
<rect x="712.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7333" values="#e5e7eb;#be9470"/></rect>
<rect x="727.0" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7351" values="#e5e7eb;#be9470"/></rect>
<rect x="741.5" y="322.0" width="14.8" height="40.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7369" values="#e5e7eb;#f0d2bd"/></rect>
<rect x="60.0" y="322" width="696.0" height="40.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7420;0.7422;1.0000" values="0;0;1;1"/><text x="766.0" y="338" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">色の種類 5</text>
<text x="766.0" y="358" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">平均の明るさ 0.55</text>
</g>
<text x="40" y="420" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">各段階の「色の種類」(数が少ないほど、べた塗り):</text>
<text x="430" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;1.0000" values="1;1;0;0"/></text>
<text x="430" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">1<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1554;0.1556;0.3509;0.3511;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">3<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3509;0.3511;0.5465;0.5467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">5<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5465;0.5467;0.7420;0.7422;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed" opacity="0">5<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7420;0.7422;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8354;0.8356;1.0000" values="0;0;1;1"/><rect x="40" y="444" width="880" height="66" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="468" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">層は、それぞれ独立。トゥーンは、写実の逆で、わざと情報を減らして「見せたい形」を強調する</text>
<text x="56" y="491" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">輪郭線は、法線と視線のなす角(縁の部分)でも作れる。別方式の輪郭線(裏面・エッジ検出)もある</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">トゥーン調は、いくつかの層の重ね合わせ<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">べた塗り → 段の陰 → リム ライト → 輪郭、と足していく<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8487;0.8489;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">層ごとにオン・オフして、タッチを調整できる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8487;0.8489;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:toon-stages:end -->

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Inverted Hull Outlines](outline-hull.md) | 裏返したメッシュを法線方向に膨らませて、黒く塗る |
| [Screen-Space Edge Detection](outline-edge.md) | 深度・法線・ID の差から、線を検出（Sobel） |
| [Cel Shading](cel-shading.md) | 陰影の段階化・ランプ テクスチャ・スペキュラとリム ライト |
| [Posterization and Halftone](posterize-halftone.md) | 色数を減らす・網点・漫画的表現 |

## 輪郭線の 2 方式

輪郭線の 2 方式を比べます。背面法（Inverted Hull）は、裏面を法線方向に膨らませて黒く描く方法で、線の太さや色を物体ごとに制御でき、安く、きれいです。短所は、角の鋭い物の線が途切れることと、内側の線が出ないことです。画面空間エッジ検出は、深度・法線・ID の画像から差の大きい所を線にする方法で、内側の線も出て、形状に依存しません。短所は、線の太さが一定になりにくいことと、コストが画面サイズに比例することです。

## 関連ページ

- [Post-Processing](../index.md)
- [Color Grading](../color-grading/index.md)
- [PBR](../../../3d/pbr.md)
- [法線とライティング](../../../3d/lighting-normals.md)
