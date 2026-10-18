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

## よくあるミス

??? failure "A2C を設定したのに、効果が出ない"
    **MSAA を有効**にし、**ブレンド ステートで A2C を ON**にする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **アルファを MSAA のカバレッジに変換**
    - [x] **葉や草に最適**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [Alpha Testing](index.md)
- [Hashed Alpha](hashed-alpha.md)
- [比較](comparison.md)
