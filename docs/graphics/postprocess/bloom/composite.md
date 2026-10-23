---
title: Compositing and Intensity
tags:
  - 描画
---

# Compositing and Intensity

<strong>ブルームの最後の工程</strong>は、できあがったにじみを元の絵に足すことです。足す強さ・足す位置（トーンマップの前）・段ごとの重み・レンズ ダート（汚れ）との組み合わせ・コストで見た目と重さが決まります。このページでは、合成の式・強さの決め方・エネルギー保存・レンズ ダート・コスト・パスの統合を説明します。

!!! tip "ポイント"
    - 合成 ＝ <strong>元の HDR 画像 + ブルーム × 強さ</strong>。<strong>トーンマップの前</strong>に足す。
    - 強さは小さく（0.04〜0.2）。かけすぎると眠い絵になる。
    - エネルギー保存型：元 × (1−強さ) + ブルーム × 強さ。明るさが増えない。
    - 段ごとの重みですそ野の形を調整。
    - レンズ ダート：汚れのテクスチャでブルームの強さを画面の場所ごとに変える。
    - コストは帯域が支配的。半解像度・パスの統合で下げる。

## 合成の式

<strong>元の絵に足す（加算）</strong>のが基本です。

<div class="formula">最終 = 元 + ブルーム × 強さ</div>

```hlsl
float3 CompositeBloom(float3 scene, float3 bloom, float intensity) {
  return scene + bloom * intensity;
}
```

| 方式 | 式 | 特徴 |
| --- | --- | --- |
| 加算 | 元 + ブルーム × 強さ | 明るさが増える。簡単・標準 |
| エネルギー保存 | 元 × (1 − 強さ) + ブルーム × 強さ | 全体の明るさが保たれ、眠くなりにくい |
| スクリーン | 1 − (1−元)(1−ブルーム) | LDR 向き（HDR では使わない） |

<!-- fig:bloom-intensity:begin -->

<svg class="fig illust motion" data-fig="bloom-intensity" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bloom-intensity" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ブルームの強さ: 足す量を増やすと、光がにじむが、暗い所が白っぽく浮く(コントラスト低下)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列の画像。ブルームの強さ k を 0 → 0.3 → 1.0 → 2.0 にして、トーンマップ後の見え方を比べる</text>
<text x="60.0" y="106" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">ブルームの強さ k = 0</text>
<rect x="60.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#0f172a;#4e514f"/></rect>
<rect x="75.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0716" values="#0f172a;#4e514f"/></rect>
<rect x="90.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0735" values="#0f172a;#4e514f"/></rect>
<rect x="105.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#4e514f"/></rect>
<rect x="120.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0772" values="#0f172a;#4e514f"/></rect>
<rect x="135.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#0f172a;#4e514f"/></rect>
<rect x="150.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#e6dda9"/></rect>
<rect x="165.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0828" values="#0f172a;#e6dda9"/></rect>
<rect x="180.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0847" values="#0f172a;#e6dda9"/></rect>
<rect x="195.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#0f172a;#4e514f"/></rect>
<rect x="210.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884" values="#0f172a;#4e514f"/></rect>
<rect x="225.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0902" values="#0f172a;#4e514f"/></rect>
<rect x="240.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#4e514f"/></rect>
<rect x="255.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0940" values="#0f172a;#4e514f"/></rect>
<rect x="270.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0958" values="#0f172a;#4e514f"/></rect>
<rect x="285.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#4e514f"/></rect>
<rect x="300.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0995" values="#0f172a;#4e514f"/></rect>
<rect x="315.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1014" values="#0f172a;#4e514f"/></rect>
<rect x="330.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#4e514f"/></rect>
<rect x="345.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1051" values="#0f172a;#4e514f"/></rect>
<rect x="360.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070" values="#0f172a;#f5ebb2"/></rect>
<rect x="375.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#4e514f"/></rect>
<rect x="390.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1107" values="#0f172a;#4e514f"/></rect>
<rect x="405.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1126" values="#0f172a;#4e514f"/></rect>
<rect x="420.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#0f172a;#4e514f"/></rect>
<rect x="435.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163" values="#0f172a;#4e514f"/></rect>
<rect x="450.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1181" values="#0f172a;#4e514f"/></rect>
<rect x="465.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#4e514f"/></rect>
<rect x="480.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1219" values="#0f172a;#4e514f"/></rect>
<rect x="495.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1237" values="#0f172a;#4e514f"/></rect>
<rect x="510.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#0f172a;#c2bc94"/></rect>
<rect x="525.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1274" values="#0f172a;#c2bc94"/></rect>
<rect x="540.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1293" values="#0f172a;#c2bc94"/></rect>
<rect x="555.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#0f172a;#c2bc94"/></rect>
<rect x="570.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1330" values="#0f172a;#c2bc94"/></rect>
<rect x="585.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1349" values="#0f172a;#c2bc94"/></rect>
<rect x="600.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1367" values="#0f172a;#4e514f"/></rect>
<rect x="615.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1386" values="#0f172a;#4e514f"/></rect>
<rect x="630.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1405" values="#0f172a;#4e514f"/></rect>
<rect x="645.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1423" values="#0f172a;#4e514f"/></rect>
<rect x="660.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1442" values="#0f172a;#4e514f"/></rect>
<rect x="675.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1460" values="#0f172a;#4e514f"/></rect>
<rect x="690.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1479" values="#0f172a;#4e514f"/></rect>
<rect x="705.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1498" values="#0f172a;#4e514f"/></rect>
<rect x="720.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1516" values="#0f172a;#4e514f"/></rect>
<rect x="735.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1535" values="#0f172a;#4e514f"/></rect>
<rect x="750.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1553" values="#0f172a;#4e514f"/></rect>
<rect x="765.0" y="110.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1572" values="#0f172a;#4e514f"/></rect>
<rect x="60.0" y="110" width="720.0" height="15.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1589;0.1591;1.0000" values="0;0;1;1"/><text x="788.0" y="124" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">光源の近く 0.11</text>
<text x="788.0" y="142" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">暗い所 0.107</text>
</g>
<text x="60.0" y="176" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">ブルームの強さ k = 0.3</text>
<rect x="60.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2558" values="#0f172a;#717164"/></rect>
<rect x="75.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2577" values="#0f172a;#787868"/></rect>
<rect x="90.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2595" values="#0f172a;#81806e"/></rect>
<rect x="105.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2614" values="#0f172a;#8b8974"/></rect>
<rect x="120.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2633" values="#0f172a;#959279"/></rect>
<rect x="135.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2651" values="#0f172a;#9c997e"/></rect>
<rect x="150.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2670" values="#0f172a;#e9dfab"/></rect>
<rect x="165.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2688" values="#0f172a;#e9e0ab"/></rect>
<rect x="180.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2707" values="#0f172a;#e9e0ab"/></rect>
<rect x="195.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2726" values="#0f172a;#9f9c7f"/></rect>
<rect x="210.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2744" values="#0f172a;#9a977c"/></rect>
<rect x="225.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2763" values="#0f172a;#949178"/></rect>
<rect x="240.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2781" values="#0f172a;#8e8c75"/></rect>
<rect x="255.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2800" values="#0f172a;#8b8973"/></rect>
<rect x="270.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2819" values="#0f172a;#8b8973"/></rect>
<rect x="285.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2837" values="#0f172a;#8f8d76"/></rect>
<rect x="300.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2856" values="#0f172a;#95937a"/></rect>
<rect x="315.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2874" values="#0f172a;#9d997e"/></rect>
<rect x="330.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2893" values="#0f172a;#a39f82"/></rect>
<rect x="345.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2912" values="#0f172a;#a7a384"/></rect>
<rect x="360.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2930" values="#0f172a;#f6ebb3"/></rect>
<rect x="375.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2949" values="#0f172a;#a6a284"/></rect>
<rect x="390.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2967" values="#0f172a;#a19e81"/></rect>
<rect x="405.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2986" values="#0f172a;#9a977c"/></rect>
<rect x="420.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3005" values="#0f172a;#918f77"/></rect>
<rect x="435.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3023" values="#0f172a;#888772"/></rect>
<rect x="450.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3042" values="#0f172a;#81806e"/></rect>
<rect x="465.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3060" values="#0f172a;#7d7c6b"/></rect>
<rect x="480.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3079" values="#0f172a;#7b7a6a"/></rect>
<rect x="495.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3098" values="#0f172a;#7b7a6a"/></rect>
<rect x="510.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3116" values="#0f172a;#c8c197"/></rect>
<rect x="525.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3135" values="#0f172a;#c8c197"/></rect>
<rect x="540.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3153" values="#0f172a;#c8c197"/></rect>
<rect x="555.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3172" values="#0f172a;#c8c197"/></rect>
<rect x="570.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3191" values="#0f172a;#c7c197"/></rect>
<rect x="585.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3209" values="#0f172a;#c7c097"/></rect>
<rect x="600.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3228" values="#0f172a;#6e6e62"/></rect>
<rect x="615.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3247" values="#0f172a;#696a5f"/></rect>
<rect x="630.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3265" values="#0f172a;#64655c"/></rect>
<rect x="645.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3284" values="#0f172a;#5f6159"/></rect>
<rect x="660.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3302" values="#0f172a;#5c5d57"/></rect>
<rect x="675.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3321" values="#0f172a;#595b56"/></rect>
<rect x="690.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3340" values="#0f172a;#575954"/></rect>
<rect x="705.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3358" values="#0f172a;#555753"/></rect>
<rect x="720.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3377" values="#0f172a;#545653"/></rect>
<rect x="735.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3395" values="#0f172a;#525552"/></rect>
<rect x="750.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3414" values="#0f172a;#525451"/></rect>
<rect x="765.0" y="180.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3433" values="#0f172a;#515451"/></rect>
<rect x="60.0" y="180" width="720.0" height="15.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3449;0.3451;1.0000" values="0;0;1;1"/><text x="788.0" y="194" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">光源の近く 0.37</text>
<text x="788.0" y="212" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">暗い所 0.137</text>
</g>
<text x="60.0" y="246" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5aa28">ブルームの強さ k = 1</text>
<rect x="60.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4419" values="#0f172a;#9a977d"/></rect>
<rect x="75.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4437" values="#0f172a;#a6a283"/></rect>
<rect x="90.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4456" values="#0f172a;#b1ac8a"/></rect>
<rect x="105.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474" values="#0f172a;#bcb791"/></rect>
<rect x="120.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4493" values="#0f172a;#c6bf96"/></rect>
<rect x="135.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4512" values="#0f172a;#ccc59a"/></rect>
<rect x="150.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4530" values="#0f172a;#ede3ad"/></rect>
<rect x="165.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4549" values="#0f172a;#ede4ad"/></rect>
<rect x="180.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4567" values="#0f172a;#ede4ad"/></rect>
<rect x="195.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4586" values="#0f172a;#cfc89b"/></rect>
<rect x="210.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4605" values="#0f172a;#cac399"/></rect>
<rect x="225.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4623" values="#0f172a;#c5be95"/></rect>
<rect x="240.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4642" values="#0f172a;#bfb992"/></rect>
<rect x="255.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4660" values="#0f172a;#bcb690"/></rect>
<rect x="270.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4679" values="#0f172a;#bcb791"/></rect>
<rect x="285.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4698" values="#0f172a;#c0ba93"/></rect>
<rect x="300.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4716" values="#0f172a;#c6c097"/></rect>
<rect x="315.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4735" values="#0f172a;#cdc69a"/></rect>
<rect x="330.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4753" values="#0f172a;#d2ca9d"/></rect>
<rect x="345.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4772" values="#0f172a;#d5cd9f"/></rect>
<rect x="360.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4791" values="#0f172a;#f7ecb3"/></rect>
<rect x="375.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#0f172a;#d4cd9f"/></rect>
<rect x="390.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4828" values="#0f172a;#d1c99d"/></rect>
<rect x="405.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4847" values="#0f172a;#cac499"/></rect>
<rect x="420.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4865" values="#0f172a;#c2bc94"/></rect>
<rect x="435.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4884" values="#0f172a;#b9b48f"/></rect>
<rect x="450.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4902" values="#0f172a;#b1ac8a"/></rect>
<rect x="465.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4921" values="#0f172a;#aca787"/></rect>
<rect x="480.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4940" values="#0f172a;#a9a585"/></rect>
<rect x="495.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4958" values="#0f172a;#a9a585"/></rect>
<rect x="510.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4977" values="#0f172a;#d2ca9d"/></rect>
<rect x="525.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4995" values="#0f172a;#d2ca9d"/></rect>
<rect x="540.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5014" values="#0f172a;#d2ca9d"/></rect>
<rect x="555.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5033" values="#0f172a;#d1ca9d"/></rect>
<rect x="570.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5051" values="#0f172a;#d0c99c"/></rect>
<rect x="585.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5070" values="#0f172a;#cfc89b"/></rect>
<rect x="600.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5088" values="#0f172a;#96937a"/></rect>
<rect x="615.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5107" values="#0f172a;#8d8b75"/></rect>
<rect x="630.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5126" values="#0f172a;#84836f"/></rect>
<rect x="645.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5144" values="#0f172a;#7b7a6a"/></rect>
<rect x="660.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5163" values="#0f172a;#737365"/></rect>
<rect x="675.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5181" values="#0f172a;#6d6d61"/></rect>
<rect x="690.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5200" values="#0f172a;#67685e"/></rect>
<rect x="705.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5219" values="#0f172a;#63645c"/></rect>
<rect x="720.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5237" values="#0f172a;#60615a"/></rect>
<rect x="735.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5256" values="#0f172a;#5c5d57"/></rect>
<rect x="750.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5274" values="#0f172a;#595b56"/></rect>
<rect x="765.0" y="250.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5293" values="#0f172a;#575a55"/></rect>
<rect x="60.0" y="250" width="720.0" height="15.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5310;0.5312;1.0000" values="0;0;1;1"/><text x="788.0" y="264" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">光源の近く 0.62</text>
<text x="788.0" y="282" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">暗い所 0.196</text>
</g>
<text x="60.0" y="316" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">ブルームの強さ k = 2</text>
<rect x="60.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6279" values="#0f172a;#b7b28e"/></rect>
<rect x="75.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6298" values="#0f172a;#c2bc94"/></rect>
<rect x="90.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6316" values="#0f172a;#ccc59a"/></rect>
<rect x="105.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6335" values="#0f172a;#d5cd9f"/></rect>
<rect x="120.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6353" values="#0f172a;#dcd4a3"/></rect>
<rect x="135.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6372" values="#0f172a;#e1d8a6"/></rect>
<rect x="150.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6391" values="#0f172a;#f1e7b0"/></rect>
<rect x="165.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6409" values="#0f172a;#f1e7b0"/></rect>
<rect x="180.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6428" values="#0f172a;#f1e7b0"/></rect>
<rect x="195.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6447" values="#0f172a;#e3daa7"/></rect>
<rect x="210.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6465" values="#0f172a;#dfd7a5"/></rect>
<rect x="225.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6484" values="#0f172a;#dbd3a3"/></rect>
<rect x="240.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6502" values="#0f172a;#d7d0a1"/></rect>
<rect x="255.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6521" values="#0f172a;#d5cd9f"/></rect>
<rect x="270.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6540" values="#0f172a;#d5cd9f"/></rect>
<rect x="285.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6558" values="#0f172a;#d8d0a1"/></rect>
<rect x="300.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6577" values="#0f172a;#ddd4a4"/></rect>
<rect x="315.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6595" values="#0f172a;#e1d9a6"/></rect>
<rect x="330.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6614" values="#0f172a;#e5dca8"/></rect>
<rect x="345.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6633" values="#0f172a;#e7deaa"/></rect>
<rect x="360.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6651" values="#0f172a;#f8edb4"/></rect>
<rect x="375.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6670" values="#0f172a;#e6dda9"/></rect>
<rect x="390.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6688" values="#0f172a;#e4dba8"/></rect>
<rect x="405.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6707" values="#0f172a;#e0d7a5"/></rect>
<rect x="420.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6726" values="#0f172a;#dad2a2"/></rect>
<rect x="435.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6744" values="#0f172a;#d3cb9e"/></rect>
<rect x="450.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6763" values="#0f172a;#ccc59a"/></rect>
<rect x="465.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6781" values="#0f172a;#c7c197"/></rect>
<rect x="480.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#0f172a;#c5bf96"/></rect>
<rect x="495.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6819" values="#0f172a;#c5be96"/></rect>
<rect x="510.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6837" values="#0f172a;#dbd3a3"/></rect>
<rect x="525.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6856" values="#0f172a;#dbd3a3"/></rect>
<rect x="540.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6874" values="#0f172a;#dbd3a3"/></rect>
<rect x="555.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6893" values="#0f172a;#dad2a2"/></rect>
<rect x="570.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6912" values="#0f172a;#d9d1a1"/></rect>
<rect x="585.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6930" values="#0f172a;#d7cfa0"/></rect>
<rect x="600.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6949" values="#0f172a;#b3ae8b"/></rect>
<rect x="615.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6967" values="#0f172a;#a9a585"/></rect>
<rect x="630.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6986" values="#0f172a;#9f9c7f"/></rect>
<rect x="645.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7005" values="#0f172a;#949279"/></rect>
<rect x="660.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7023" values="#0f172a;#8a8873"/></rect>
<rect x="675.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7042" values="#0f172a;#81806d"/></rect>
<rect x="690.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7060" values="#0f172a;#797969"/></rect>
<rect x="705.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7079" values="#0f172a;#737365"/></rect>
<rect x="720.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7098" values="#0f172a;#6d6e62"/></rect>
<rect x="735.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7116" values="#0f172a;#67685e"/></rect>
<rect x="750.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7135" values="#0f172a;#63645c"/></rect>
<rect x="765.0" y="320.0" width="15.3" height="15.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7153" values="#0f172a;#5f615a"/></rect>
<rect x="60.0" y="320" width="720.0" height="15.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7170;0.7172;1.0000" values="0;0;1;1"/><text x="788.0" y="334" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">光源の近く 0.76</text>
<text x="788.0" y="352" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">暗い所 0.264</text>
</g>
<rect x="30" y="400" width="900" height="80" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="30" y="390" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">暗い所の持ち上がり(k = 0 を基準)</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1589;0.1591;1.0000" values="0;0;1;1"/><text x="50" y="444" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">k = 0</text>
<text x="50" y="468" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2ea043">×1.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3449;0.3451;1.0000" values="0;0;1;1"/><text x="270" y="444" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">k = 0.3</text>
<text x="270" y="468" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2ea043">×1.27</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5310;0.5312;1.0000" values="0;0;1;1"/><text x="490" y="444" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">k = 1</text>
<text x="490" y="468" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d">×1.83</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7170;0.7172;1.0000" values="0;0;1;1"/><text x="710" y="444" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">k = 2</text>
<text x="710" y="468" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d">×2.46</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ブルームは、元の画像に足す<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">k を上げるほど、光源の周りが光るが、暗い所まで持ち上がる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.8603;0.8605;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">強すぎると、画面が白っぽくぼやける。控えめ(k ≈ 0.05〜0.3)が基本<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.8603;0.8605;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:bloom-intensity:end -->

## 強さの決め方

| 強さ | 見た目 |
| --- | --- |
| 0.0 | ブルームなし |
| 0.04〜0.08 | 上品なにじみ（現代的な、控えめな標準） |
| 0.1〜0.2 | はっきり光る |
| 0.3 以上 | 夢のような、ぼんやりした絵（意図的な表現） |

<strong>強さ</strong>はステージや演出ごとに変えるのが自然です（夜のネオン街は強め、昼の砂漠は控えめ）。

## 足す位置

<strong>ブルームは、HDR のリニア画像に足し、その後でトーンマップ</strong>します。

ブルームは、HDR のリニア画像に足し、その後でトーンマップします。ブルームの後にトーンマップする順序なら、明るい光のにじみが、トーンマップで自然に白へ向かいます。これが正しい順序です。トーンマップの後にブルームを足すと、LDR（0〜1）の絵にぼかしを足すことになり、明るさが足りず、にじみません。これは誤りです。

## エネルギー保存

<strong>単純に足す</strong>と画面全体が少し明るくなります。足す分だけ元を減らすと、全体の明るさが保たれます。

```hlsl
float3 CompositeEnergyConserving(float3 scene, float3 bloom, float intensity) {
  return lerp(scene, bloom, intensity);
}
```

コードの要点です。`lerp(元, ブルーム, 強さ)` は `元 × (1−強さ) + ブルーム × 強さ` と同じです。ブルームが「ぼかした全体の画像」（しきい値なし）のときにだけ使います。しきい値で抜き出した光だけを足す場合は、単純な加算にします。

しきい値なしのブルーム（全画素をぼかす）とこの合成の組み合わせは、物理的にも自然です。

## 段ごとの重み

<strong>ミップ チェーンの各段を足し合わせるとき、重みを付ける</strong>とすそ野の形が変わります。

ミップ チェーンの各段を足し合わせるときに重みを付けると、すそ野の形が変わります。均等なら標準です。細かい段を強くすると、くっきりしたシャープなにじみになります。粗い段を強くすると、広い柔らかい「もや」になります。

```hlsl
float3 CombineLevels(float3 l0, float3 l1, float3 l2, float3 l3, float3 l4, float4 weights_a, float weight_e) {
  return l0 * weights_a.x + l1 * weights_a.y + l2 * weights_a.z + l3 * weights_a.w + l4 * weight_e;
}
```

## レンズ ダート

<strong>カメラのレンズに付いた汚れ・傷</strong>に強い光が当たると汚れが光って見えます。汚れのテクスチャをブルームに掛けると、この効果が出ます。

```hlsl
float3 ApplyLensDirt(float3 bloom, float2 uv, Texture2D dirt, float dirt_intensity) {
  float3 d = dirt.SampleLevel(linear_clamp, uv, 0).rgb;
  return bloom * (1.0 + d * dirt_intensity);
}
```

レンズ ダートのコードの要点です。汚れマスクは、ふつうの絵（白黒〜淡い色）のテクスチャを、画面全体に貼ります。これをブルームに掛けるので、ブルームが強い所ほど、汚れが目立ちます。用途は、戦争ゲームの爆風、SF の宇宙船、FPS のカメラ表現などです。

詳しい演出は[Lens Effects](../lens-effects/index.md)も参照してください。

## コストと最適化

<strong>ブルームは画面全体を何度も読み書きする</strong>ので、帯域が支配的です。

| 項目 | 目安 | 対策 |
| --- | --- | --- |
| 最初の縮小 | フル解像度の読み込み（重い） | 最初から半解像度・13 タップを 1 回 |
| 各段の読み書き | 小さいので安い | 段数を 5〜6 に |
| 最終合成 | フル解像度の読み書き | トーンマップと同じパスにまとめる |
| フォーマット | R16G16B16A16_FLOAT | R11G11B10_FLOAT（半分のメモリ） |

### パスの統合

ブルームの最後の足し算は、トーンマップ・ビネット・色収差などの画面全体のパスと同じシェーダーにまとめることができます。

```hlsl
float3 FinalPass(float2 uv) {
  float3 scene = hdr_color.SampleLevel(point_clamp, uv, 0).rgb;
  float3 bloom = bloom_chain.SampleLevel(linear_clamp, uv, 0).rgb;
  float3 color = scene + bloom * bloom_intensity;
  color = ApplyExposure(color);
  color = Tonemap(color);
  color = ApplyVignette(color, uv);
  return LinearToSRGB(color);
}
```

フル解像度のパスを 1 回に減らすだけで、帯域が大きく減ります。

## より良いやり方

| 工夫 | 内容 |
| --- | --- |
| 強さは小さく | 0.04〜0.1 を出発点に、ステージで調整 |
| トーンマップ・ビネットと 1 パスに | フル解像度のパスを減らす |
| 半解像度から始める | フル解像度の最初の縮小を避ける |
| 段ごとの重みで形を調整 | 見た目をアーティストが制御できるようにする |
| 品質設定で段数を変える | 低スペックでは 4 段、高スペックでは 7 段 |
| 画面の明るさに合わせる | 露出が変わる場面では、ブルームの強さも追従させる |

## よくあるミス

??? failure "ブルームを強くしすぎて、画面全体が眠く、ぼんやりする"
    <strong>強さを 0.05〜0.1 に</strong>。しきい値なしなら、エネルギー保存。

??? failure "トーンマップの後でブルームを足して、にじまない"
    ブルームは HDR のうちに、トーンマップの前に足す。

??? failure "フル解像度のパスが多くて、帯域で重い"
    合成・トーンマップ・ビネットを 1 パスにまとめる。

??? failure "レンズ ダートを強くしすぎて、汚れが常に見える"
    強い光のときだけ見えるよう、強さを弱くする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 合成 ＝ <strong>元 + ブルーム × 強さ</strong>。HDR のうちにトーンマップの前
    - [x] 強さは小さく（0.04〜0.1）。エネルギー保存も選べる
    - [x] 段ごとの重みですそ野の形を調整
    - [x] レンズ ダートで場所ごとの強さを演出
    - [x] パスを統合して帯域を節約

## 参考

- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Unity, "Post-processing: Bloom, Lens Dirt"
- Epic Games, "Unreal Engine: Bloom"

## 関連ページ

- [Bloom](index.md)
- [Threshold](threshold.md)
- [Dual Filter](dual-filter.md)
- [Lens Effects](../lens-effects/index.md)
- [Tone Mapping and Exposure](../tonemapping/index.md)
