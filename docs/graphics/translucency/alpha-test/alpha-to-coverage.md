---
title: Alpha to Coverage
tags:
  - 描画
---

# Alpha to Coverage

**Alpha to Coverage（A2C）は、MSAA のサンプル マスクを、アルファ値に応じて決める手法**です。**縁がなめらかになり、ソートも不要**なので、**葉や草に最適**です。このページでは、**A2C の仕組みと使い方**を説明します。

!!! tip "ポイント"
    - **アルファ値を、MSAA の「カバレッジ（何サンプル覆うか）」に変換**する。
    - **ソート不要・縁がなめらか**。
    - **MSAA が必要**（4x なら、5 段階の濃さ）。
    - **遠くで細る問題は、アルファの補正で対処**する。

<!-- fig:a2c-coverage:begin -->

<svg class="fig illust motion" data-fig="a2c-coverage" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-a2c-coverage" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">Alpha To Coverage: アルファを、MSAA サブサンプルの「覆う数」に変える</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">葉っぱの縁のようなアルファ(左 0 → 右 1)を、1 列 24 画素で描く。1 画素は 4 サンプル</text>
<text x="60.0" y="100" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">アルファの値(白 = 0、黒 = 1)</text>
<rect x="60.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#ffffff"/></rect>
<rect x="93.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#ffffff"/></rect>
<rect x="126.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#ffffff"/></rect>
<rect x="159.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#ffffff"/></rect>
<rect x="192.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#ffffff"/></rect>
<rect x="225.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#ffffff"/></rect>
<rect x="258.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#f4f4f4"/></rect>
<rect x="291.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#dfdfdf"/></rect>
<rect x="324.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#cacaca"/></rect>
<rect x="357.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#b5b5b5"/></rect>
<rect x="390.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#9f9f9f"/></rect>
<rect x="423.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#8a8a8a"/></rect>
<rect x="456.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#757575"/></rect>
<rect x="489.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#606060"/></rect>
<rect x="522.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#4a4a4a"/></rect>
<rect x="555.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#353535"/></rect>
<rect x="588.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#202020"/></rect>
<rect x="621.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#0b0b0b"/></rect>
<rect x="654.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#000000"/></rect>
<rect x="687.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#000000"/></rect>
<rect x="720.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#000000"/></rect>
<rect x="753.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#000000"/></rect>
<rect x="786.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#000000"/></rect>
<rect x="819.0" y="104.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0171" values="#e5e7eb;#000000"/></rect>
<rect x="60.0" y="104" width="792.0" height="33.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="118" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">正解(アルファをそのまま使う)</text>
<rect x="60.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="93.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0674" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="126.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0777" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="159.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="192.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0983" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="225.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1086" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="258.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1189" values="#e5e7eb;#eaeeea"/></rect>
<rect x="291.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1291" values="#e5e7eb;#d9e5da"/></rect>
<rect x="324.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#c8ddca"/></rect>
<rect x="357.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1497" values="#e5e7eb;#b7d4ba"/></rect>
<rect x="390.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1600" values="#e5e7eb;#a6ccab"/></rect>
<rect x="423.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1703" values="#e5e7eb;#95c49b"/></rect>
<rect x="456.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1806" values="#e5e7eb;#84bb8b"/></rect>
<rect x="489.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1909" values="#e5e7eb;#73b27b"/></rect>
<rect x="522.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2011" values="#e5e7eb;#62aa6b"/></rect>
<rect x="555.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2114" values="#e5e7eb;#51a25b"/></rect>
<rect x="588.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#40994b"/></rect>
<rect x="621.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2320" values="#e5e7eb;#2f903b"/></rect>
<rect x="654.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2423" values="#e5e7eb;#268c33"/></rect>
<rect x="687.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2526" values="#e5e7eb;#268c33"/></rect>
<rect x="720.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2629" values="#e5e7eb;#268c33"/></rect>
<rect x="753.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2731" values="#e5e7eb;#268c33"/></rect>
<rect x="786.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2834" values="#e5e7eb;#268c33"/></rect>
<rect x="819.0" y="124.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2937" values="#e5e7eb;#268c33"/></rect>
<rect x="60.0" y="124" width="792.0" height="33.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="194" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">アルファ テスト(0.5 で切る: 1 サンプル)</text>
<rect x="60.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="93.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0674" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="126.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0777" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="159.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="192.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0983" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="225.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1086" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="258.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1189" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="291.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1291" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="324.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="357.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1497" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="390.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1600" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="423.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1703" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="456.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1806" values="#e5e7eb;#268c33"/></rect>
<rect x="489.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1909" values="#e5e7eb;#268c33"/></rect>
<rect x="522.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2011" values="#e5e7eb;#268c33"/></rect>
<rect x="555.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2114" values="#e5e7eb;#268c33"/></rect>
<rect x="588.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#268c33"/></rect>
<rect x="621.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2320" values="#e5e7eb;#268c33"/></rect>
<rect x="654.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2423" values="#e5e7eb;#268c33"/></rect>
<rect x="687.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2526" values="#e5e7eb;#268c33"/></rect>
<rect x="720.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2629" values="#e5e7eb;#268c33"/></rect>
<rect x="753.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2731" values="#e5e7eb;#268c33"/></rect>
<rect x="786.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2834" values="#e5e7eb;#268c33"/></rect>
<rect x="819.0" y="200.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2937" values="#e5e7eb;#268c33"/></rect>
<rect x="60.0" y="200" width="792.0" height="33.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60.0" y="270" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">Alpha To Coverage(4 サンプルの数に変換)</text>
<rect x="60.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0571" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="93.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0674" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="126.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0777" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="159.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0880" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="192.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0983" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="225.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1086" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="258.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1189" values="#e5e7eb;#f2f2f2"/></rect>
<rect x="291.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1291" values="#e5e7eb;#bfd9c2"/></rect>
<rect x="324.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1394" values="#e5e7eb;#bfd9c2"/></rect>
<rect x="357.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1497" values="#e5e7eb;#bfd9c2"/></rect>
<rect x="390.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1600" values="#e5e7eb;#bfd9c2"/></rect>
<rect x="423.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1703" values="#e5e7eb;#8cbf93"/></rect>
<rect x="456.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1806" values="#e5e7eb;#8cbf93"/></rect>
<rect x="489.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1909" values="#e5e7eb;#59a663"/></rect>
<rect x="522.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2011" values="#e5e7eb;#59a663"/></rect>
<rect x="555.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2114" values="#e5e7eb;#59a663"/></rect>
<rect x="588.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2217" values="#e5e7eb;#59a663"/></rect>
<rect x="621.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2320" values="#e5e7eb;#268c33"/></rect>
<rect x="654.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2423" values="#e5e7eb;#268c33"/></rect>
<rect x="687.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2526" values="#e5e7eb;#268c33"/></rect>
<rect x="720.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2629" values="#e5e7eb;#268c33"/></rect>
<rect x="753.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2731" values="#e5e7eb;#268c33"/></rect>
<rect x="786.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2834" values="#e5e7eb;#268c33"/></rect>
<rect x="819.0" y="276.0" width="33.3" height="33.3" fill="#e5e7eb"><animate attributeName="fill" dur="17.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2937" values="#e5e7eb;#268c33"/></rect>
<rect x="60.0" y="276" width="792.0" height="33.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="60" y="346" width="380" height="150" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="60" y="336" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">画素 12 の中を拡大(4 サンプル)</text>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3266;0.3269;1.0000" values="0;0;1;1"/><rect x="80" y="372" width="75" height="60" fill="#268c33" stroke="#94a3b8" stroke-width="1.5"/>
<text x="117" y="452" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">α=0.43</text>
<text x="117" y="468" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">しきい値 0.38</text>
<text x="117" y="408" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">覆う</text>
<rect x="165" y="372" width="75" height="60" fill="#f2f2f2" stroke="#94a3b8" stroke-width="1.5"/>
<text x="202" y="452" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">α=0.45</text>
<text x="202" y="468" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">しきい値 0.88</text>
<text x="202" y="408" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">覆わない</text>
<rect x="250" y="372" width="75" height="60" fill="#268c33" stroke="#94a3b8" stroke-width="1.5"/>
<text x="287" y="452" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">α=0.47</text>
<text x="287" y="468" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">しきい値 0.12</text>
<text x="287" y="408" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">覆う</text>
<rect x="335" y="372" width="75" height="60" fill="#f2f2f2" stroke="#94a3b8" stroke-width="1.5"/>
<text x="372" y="452" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#1f2937">α=0.49</text>
<text x="372" y="468" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">しきい値 0.62</text>
<text x="372" y="408" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">覆わない</text>
<text x="80" y="488" text-anchor="start" style="font-size:14px;font-weight:700;fill:#7c3aed">覆うサンプルが 2 / 4 個 → 画素の濃さ 0.50</text>
</g>
<text x="480" y="372" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">表せる濃さの段階:</text>
<text x="480" y="396" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">アルファ テスト: 2 段階(0 か 1)<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3266;0.3269;1.0000" values="0;0;1;1"/></text>
<text x="480" y="420" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb" opacity="0">A2C: 5 段階(0, 1/4, 2/4, 3/4, 1)<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3266;0.3269;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3838;0.3840;1.0000" values="0;0;1;1"/><rect x="480" y="440" width="450" height="70" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="496" y="464" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">正解とのずれ: アルファ テスト 0.081 / A2C 0.023</text>
<text x="496" y="488" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">MSAA を使っているときだけ有効。サンプル数が多いほど滑らか</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">葉っぱの縁のアルファは、なめらかに 0 から 1 へ変わる<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">アルファ テスト: 0.5 で切るので、縁が階段状になる(ジャギー)<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.0569;0.0571;0.3266;0.3269;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">A2C: アルファの大きさを「覆うサンプルの数」に変える<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3266;0.3269;0.3838;0.3840;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">同じ画素でも、サンプルごとに覆う / 覆わないが違い、5 段階の濃さになる<animate attributeName="opacity" dur="17.5s" repeatCount="indefinite" keyTimes="0.0000;0.3838;0.3840;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:a2c-coverage:end -->

## Alpha to Coverage
**MSAA を使っているとき**、**アルファの値を、そのまま「カバレッジ（どのサンプルを塗るか）」に変換**する機能です。**アルファ 0.5 なら、4 サンプルのうち 2 つを塗る**ことで、**縁が滑らかな段階**になります。

```cpp
D3D11_BLEND_DESC desc = {};
desc.AlphaToCoverageEnable = TRUE;
desc.RenderTarget[0].RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
device->CreateBlendState(&desc, &alpha_to_coverage_state);
```

| 点 | 説明 |
| --- | --- |
| **`AlphaToCoverageEnable`** | **ピクセル シェーダーの出力アルファを、カバレッジ マスクに変換** |
| **MSAA が必要** | **MSAA の描画先**（`SampleDesc.Count` が 2 以上）でのみ**有効** |
| **ブレンドは不要** | **アルファ ブレンドとは別の機構**。**深度も書ける** |
| **効果** | **縁が、MSAA のサンプル数ぶんの段階で滑らかに** |

**4x MSAA では 5 段階**（0/4〜4/4）の**透明度**しか**表せません**。**ディザリングのようなパターン**が**見える**ことがあります。

## アルファ テストの、縁が、ギザギザになる理由

`clip(alpha - 0.5)` は、**画素の中心**で、アルファを調べて、残すか捨てるかを、決めます。**縁の画素は、残るか、消えるかの、二択**なので、**階段状の、ジャギー**になります。MSAA（マルチサンプル アンチエイリアス）を使っていても、**ピクセル シェーダーが、1 画素に 1 回しか、走らない**ので、`clip` の結果は、**4 つのサンプルすべてに、同じ**ように、適用されます。**ポリゴンの縁**には、MSAA が効きますが、**テクスチャの、アルファの縁**には、効きません。

## Alpha to Coverage の仕組み

**Alpha to Coverage（A2C）**は、**ピクセル シェーダーが、出力したアルファ**を、**MSAA の、カバレッジ**（その画素の、**サンプルのうち、何個を、描くか**）に、**変換する**機能です。

| アルファ | 4x MSAA で、描かれるサンプル |
| --- | --- |
| 0.0 | 0 個（何も描かない） |
| 0.25 | 1 個 |
| 0.5 | 2 個 |
| 0.75 | 3 個 |
| 1.0 | 4 個（すべて描く） |

画素は、**サンプルごとの、描く・描かない**が、決まり、**解像（リゾルブ）**のとき、**サンプルが、平均**されます。結果、**アルファが 0.5 の画素は、半分の明るさ**で、混ざります。**縁が、なめらかな、ブレンド**に見えます。

```text
アルファ テスト                 Alpha to Coverage（4x MSAA）
████████                       ████████
████▀▀▀▀                       ████▓▒░·       ← 縁の画素が、段階的に、薄くなる
████                           ████
```

**深度を、書き込み**ながら、**縁が、なめらか**になる、**ソート不要**の、半透明表現です。

## DirectX 11 で、設定する

MSAA の、レンダー ターゲットと、深度バッファを、作り、**ブレンド ステートで、A2C を、有効にします**。

```cpp
// ① MSAA のレンダー ターゲット（4x）を作る。
D3D11_TEXTURE2D_DESC color_desc = {};
color_desc.Width = width; color_desc.Height = height;
color_desc.MipLevels = 1; color_desc.ArraySize = 1;
color_desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;
color_desc.SampleDesc.Count = 4;                         // 4x MSAA
color_desc.SampleDesc.Quality = 0;
color_desc.Usage = D3D11_USAGE_DEFAULT;
color_desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&color_desc, nullptr, &msaa_color);
// 深度バッファも、SampleDesc.Count = 4 で作る。

// ② ブレンド ステートで、Alpha to Coverage を有効にする。
D3D11_BLEND_DESC blend = {};
blend.AlphaToCoverageEnable = TRUE;                      // ここが肝心
blend.IndependentBlendEnable = FALSE;
blend.RenderTarget[0].BlendEnable = FALSE;               // 通常のブレンドは、使わない
blend.RenderTarget[0].RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
device->CreateBlendState(&blend, &a2c_blend_state);

const float factor[4] = {0, 0, 0, 0};
context->OMSetBlendState(a2c_blend_state.Get(), factor, 0xffffffff);
```

| 設定 | 内容 |
| --- | --- |
| `AlphaToCoverageEnable` | `TRUE`。ピクセル シェーダーの、**SV_Target の、アルファ**を、カバレッジに変換する |
| `BlendEnable` | `FALSE`。A2C は、ブレンドではなく、**サンプルの、描く・描かない**で、動く |
| MSAA | **必須**。MSAA が無い（サンプル 1 つ）と、A2C は、**アルファ テストと、ほぼ同じ**で、意味がない |

```hlsl
// ピクセル シェーダー: アルファを、そのまま出力する。clip は、使わない。
float4 main(PSInput input) : SV_Target {
  float4 color = g_albedo.Sample(g_linear_wrap, input.uv);
  return float4(color.rgb, color.a);        // color.a が、カバレッジに変換される
}
```

## アルファの、**シャープ化**

テクスチャの、アルファが、**なだらかな、勾配**を持つ（ぼやけた縁）と、A2C の効果で、**縁が、広く、ぼやけて**しまいます。**しきい値の周りの、狭い範囲だけ**を、段階的にして、ぴったりの縁を、作ります。

```hlsl
// アルファを、しきい値の周りで、鋭くする（画面上の、1 画素の幅に合わせて）。
float alpha = g_albedo.Sample(g_linear_wrap, uv).a;
float width = fwidth(alpha);                              // 画面の 1 画素あたりの、アルファの変化
alpha = saturate((alpha - 0.5) / max(width, 1e-4) + 0.5); // しきい値 0.5 を中心に、1 画素の幅だけ、なだらか
```

`fwidth(alpha)` は、**隣の画素との、アルファの差**です。これを、**縁のなだらかさの、幅**に使うと、**どの距離でも、縁が、ちょうど、1 画素ぶん、なだらか**になります。**近くで、ぼやけず**、**遠くで、ちらつかない**、定番の、書き方です。

## MSAA の、サンプル数と、段階

| MSAA | アルファの段階 | 縁の見え方 |
| --- | --- | --- |
| 2x | 3 段階 | まだ、ジャギーが、残る |
| 4x | 5 段階 | まずまず。標準 |
| 8x | 9 段階 | なめらか。メモリ、帯域が、増える |

**サンプル数が、少ない**と、アルファの、段階が、粗く、**縁に、縞（バンディング）**が、出ます。ディザで、ごまかす手法もあります（次の節）。

## バンディングを、隠す

4x では、**5 段階しか**、**アルファを、表現できません**。広い範囲で、**なだらかに、薄くなる**表現（フェード）では、**縞**が見えます。画素ごとに、**ランダムな、オフセット**を、アルファに足して、段階を、ディザで、ならします。

```hlsl
// 画素ごとの、ノイズで、アルファを、少しずらして、バンディングを、細かい点に変える。
float noise = InterleavedGradientNoise(input.position.xy);           // 0〜1（Jimenez 2014）
float alpha_dithered = saturate(alpha + (noise - 0.5) * (1.0 / 4.0)); // サンプル数の逆数だけ、揺らす
return float4(color.rgb, alpha_dithered);
```

```hlsl
// Interleaved Gradient Noise（Jimenez 2014）。画面座標から、安い式で、ノイズを作る。
float InterleavedGradientNoise(float2 screen_pos) {
  float3 magic = float3(0.06711056, 0.00583715, 52.9829189);
  return frac(magic.z * frac(dot(screen_pos, magic.xy)));
}
```

## A2C の、**注意点**

| 項目 | 内容 |
| --- | --- |
| MSAA が必要 | **ディファード レンダリング**では、MSAA が、重いので、使いにくい。**フォワード**向き |
| 他の、アルファ | A2C を使うと、ブレンド ステートが、占有される。**通常のアルファ ブレンドと、併用できない** |
| 色 | アルファ以外の、出力（色）は、通常どおり。カバレッジが、決まるだけ |
| ミップ | 遠くで、アルファが、薄くなる問題は、残る（[Foliage Translucency](../../terrain/vegetation/translucency.md)） |
| 重なり | 複数の、A2C の面が、**同じ画素に、重なる**と、**同じサンプルが、取り合い**になる。**重なりに、強くない**（アルファの合計が、1 を超えると、もう、描けない） |
| 動き | **TAA**を使うなら、A2C なしでも、**ハッシュ アルファ**（時間方向に、平均）で、同等のことが、できる（[Hashed Alpha](hashed-alpha.md)） |

## 使いどころ

| 対象 | A2C |
| --- | --- |
| 木の葉、草（フォワード + MSAA） | **最も、有効**（縁が、なめらか、ソート不要、深度書き込み可） |
| フェンス、金網 | 有効 |
| 髪の毛 | 有効（ただし、重なりが、多い。[Hair Transparency](../../skin-hair/hair/transparency.md)） |
| ガラス、水など、本当の半透明 | **不向き**（アルファを、段階的な、サンプルに、変換するだけで、混ざらない） |

## よくあるミス

??? failure "A2C を設定したのに、効果が出ない"
    **MSAA を有効**にし、**ブレンド ステートで A2C を ON**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **アルファを MSAA のカバレッジに変換**
    - [x] **葉や草に最適**

## 参考

- Microsoft Learn, "D3D11_BLEND_DESC"（`AlphaToCoverageEnable`、`D3D11_RENDER_TARGET_BLEND_DESC`）
- Castaño, "Computing Alpha Mipmaps", 2010（ミップごとに、アルファを補正して、カバレッジを保つ）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014, Advances in Real-Time Rendering in Games（Interleaved Gradient Noise）
- Wyman, McGuire, "Hashed Alpha Testing", Symposium on Interactive 3D Graphics and Games 2017
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（透明と、アルファ合成の章）

## 関連ページ

- [Alpha Testing](index.md)
- [Hashed Alpha](hashed-alpha.md)
- [Method Comparison](comparison.md)
