---
title: Lens Effects
tags:
  - 描画
---

# Lens Effects

<strong>CG の画面は、本来「完璧すぎる」</strong>ものです。<strong>実際のカメラは、レンズの歪み・色のずれ・周辺の暗さ・センサーのノイズ・光の反射</strong>など、<strong>さまざまな「不完全さ」</strong>を<strong>持ちます</strong>。<strong>ポストプロセスでこれらを再現すると、「カメラで撮った絵」</strong>に見え、リアリティや映画らしさが増します。ただし、どれも「あれば高品質」というものではなく、表現の好みの問題です。このセクションでは、色収差・ビネット・フィルム グレイン・レンズ フレアを、1 つずつ別のページで説明します。

## 効果の一覧

| 効果 | 内容 | 向く場面 |
| --- | --- | --- |
| [Chromatic Aberration](chromatic-aberration.md) | 画面の端で赤・緑・青がずれる | ホラー・SF・被ダメージの演出 |
| [Vignette](vignette.md) | 周辺が暗くなる | 視線の誘導・映画風・夜のシーン |
| [Film Grain](film-grain.md) | <strong>細かいノイズ（粒子）</strong> | フィルムの質感・暗部のバンディング隠し |
| [Lens Flare](lens-flare.md) | 強い光源から、ゴーストと光芒 | SF・日光・ヘッドライト |

<strong>光の筋（ゴッド レイ）</strong>は、<strong>大気の効果</strong>なので[God Rays](../../atmosphere/god-rays/index.md)で扱います。

## 動きで見る：色収差の広がり

<!-- fig:chromatic-aberration-shift:begin -->

<svg class="fig illust motion" data-fig="chromatic-aberration-shift" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-chromatic-aberration-shift" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">色収差: 画面の中心から離れるほど、赤と青が逆向きにずれ、白い縁に、色のにじみが出る</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 列 64 画素。白と黒の境目(縁)が 3 カ所。赤を外へ、青を内へ、中心からの距離に比例してずらす</text>
<text x="60.0" y="112" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">ずれの強さ k = 0</text>
<rect x="60.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698" values="#0f172a;#000000"/></rect>
<rect x="70.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0712" values="#0f172a;#000000"/></rect>
<rect x="81.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0726" values="#0f172a;#000000"/></rect>
<rect x="91.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0740" values="#0f172a;#000000"/></rect>
<rect x="102.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0753" values="#0f172a;#000000"/></rect>
<rect x="112.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767" values="#0f172a;#000000"/></rect>
<rect x="123.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0781" values="#0f172a;#000000"/></rect>
<rect x="133.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0795" values="#0f172a;#000000"/></rect>
<rect x="144.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0809" values="#0f172a;#000000"/></rect>
<rect x="154.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0823" values="#0f172a;#000000"/></rect>
<rect x="165.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837" values="#0f172a;#000000"/></rect>
<rect x="175.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0851" values="#0f172a;#000000"/></rect>
<rect x="186.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0865" values="#0f172a;#000000"/></rect>
<rect x="196.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0879" values="#0f172a;#000000"/></rect>
<rect x="207.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0893" values="#0f172a;#000000"/></rect>
<rect x="217.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907" values="#0f172a;#000000"/></rect>
<rect x="228.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0921" values="#0f172a;#ffffff"/></rect>
<rect x="238.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0935" values="#0f172a;#ffffff"/></rect>
<rect x="249.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0949" values="#0f172a;#ffffff"/></rect>
<rect x="259.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963" values="#0f172a;#ffffff"/></rect>
<rect x="270.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977" values="#0f172a;#ffffff"/></rect>
<rect x="280.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0991" values="#0f172a;#ffffff"/></rect>
<rect x="291.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1005" values="#0f172a;#ffffff"/></rect>
<rect x="301.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1019" values="#0f172a;#ffffff"/></rect>
<rect x="312.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1033" values="#0f172a;#ffffff"/></rect>
<rect x="322.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047" values="#0f172a;#ffffff"/></rect>
<rect x="333.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1060" values="#0f172a;#ffffff"/></rect>
<rect x="343.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1074" values="#0f172a;#ffffff"/></rect>
<rect x="354.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1088" values="#0f172a;#ffffff"/></rect>
<rect x="364.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102" values="#0f172a;#ffffff"/></rect>
<rect x="375.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116" values="#0f172a;#ffffff"/></rect>
<rect x="385.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1130" values="#0f172a;#ffffff"/></rect>
<rect x="396.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1144" values="#0f172a;#000000"/></rect>
<rect x="406.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1158" values="#0f172a;#000000"/></rect>
<rect x="417.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172" values="#0f172a;#000000"/></rect>
<rect x="427.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186" values="#0f172a;#000000"/></rect>
<rect x="438.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1200" values="#0f172a;#000000"/></rect>
<rect x="448.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1214" values="#0f172a;#000000"/></rect>
<rect x="459.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1228" values="#0f172a;#000000"/></rect>
<rect x="469.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1242" values="#0f172a;#000000"/></rect>
<rect x="480.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1256" values="#0f172a;#000000"/></rect>
<rect x="490.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1270" values="#0f172a;#000000"/></rect>
<rect x="501.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1284" values="#0f172a;#000000"/></rect>
<rect x="511.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1298" values="#0f172a;#000000"/></rect>
<rect x="522.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1312" values="#0f172a;#000000"/></rect>
<rect x="532.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1326" values="#0f172a;#000000"/></rect>
<rect x="543.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1340" values="#0f172a;#000000"/></rect>
<rect x="553.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1353" values="#0f172a;#000000"/></rect>
<rect x="564.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1367" values="#0f172a;#000000"/></rect>
<rect x="574.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1381" values="#0f172a;#000000"/></rect>
<rect x="585.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1395" values="#0f172a;#000000"/></rect>
<rect x="595.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1409" values="#0f172a;#000000"/></rect>
<rect x="606.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1423" values="#0f172a;#000000"/></rect>
<rect x="616.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1437" values="#0f172a;#000000"/></rect>
<rect x="627.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1451" values="#0f172a;#000000"/></rect>
<rect x="637.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1465" values="#0f172a;#000000"/></rect>
<rect x="648.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1479" values="#0f172a;#ffffff"/></rect>
<rect x="658.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1493" values="#0f172a;#ffffff"/></rect>
<rect x="669.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1507" values="#0f172a;#ffffff"/></rect>
<rect x="679.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1521" values="#0f172a;#ffffff"/></rect>
<rect x="690.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1535" values="#0f172a;#ffffff"/></rect>
<rect x="700.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1549" values="#0f172a;#ffffff"/></rect>
<rect x="711.0" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1563" values="#0f172a;#ffffff"/></rect>
<rect x="721.5" y="116.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1577" values="#0f172a;#ffffff"/></rect>
<rect x="60.0" y="116" width="672.0" height="30.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1393;0.1395;1.0000" values="0;0;1;1"/><text x="742.0" y="128" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">中心の縁 0 画素</text>
<text x="742.0" y="146" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">端の縁 0 画素</text>
</g>
<text x="60.0" y="174" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">ずれの強さ k = 0.5</text>
<rect x="60.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2558" values="#0f172a;#000000"/></rect>
<rect x="70.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2572" values="#0f172a;#000000"/></rect>
<rect x="81.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2586" values="#0f172a;#000000"/></rect>
<rect x="91.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2600" values="#0f172a;#000000"/></rect>
<rect x="102.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2614" values="#0f172a;#000000"/></rect>
<rect x="112.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2628" values="#0f172a;#000000"/></rect>
<rect x="123.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2642" values="#0f172a;#000000"/></rect>
<rect x="133.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2656" values="#0f172a;#000000"/></rect>
<rect x="144.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2670" values="#0f172a;#000000"/></rect>
<rect x="154.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2684" values="#0f172a;#000000"/></rect>
<rect x="165.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2698" values="#0f172a;#000000"/></rect>
<rect x="175.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2712" values="#0f172a;#000000"/></rect>
<rect x="186.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2726" values="#0f172a;#000000"/></rect>
<rect x="196.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2740" values="#0f172a;#000000"/></rect>
<rect x="207.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2753" values="#0f172a;#930000"/></rect>
<rect x="217.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2767" values="#0f172a;#ff0000"/></rect>
<rect x="228.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2781" values="#0f172a;#ffff00"/></rect>
<rect x="238.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2795" values="#0f172a;#ffffb1"/></rect>
<rect x="249.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2809" values="#0f172a;#ffffff"/></rect>
<rect x="259.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2823" values="#0f172a;#ffffff"/></rect>
<rect x="270.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2837" values="#0f172a;#ffffff"/></rect>
<rect x="280.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2851" values="#0f172a;#ffffff"/></rect>
<rect x="291.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2865" values="#0f172a;#ffffff"/></rect>
<rect x="301.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2879" values="#0f172a;#ffffff"/></rect>
<rect x="312.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2893" values="#0f172a;#ffffff"/></rect>
<rect x="322.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2907" values="#0f172a;#ffffff"/></rect>
<rect x="333.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2921" values="#0f172a;#ffffff"/></rect>
<rect x="343.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2935" values="#0f172a;#ffffff"/></rect>
<rect x="354.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2949" values="#0f172a;#ffffff"/></rect>
<rect x="364.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963" values="#0f172a;#ffffff"/></rect>
<rect x="375.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2977" values="#0f172a;#ffffff"/></rect>
<rect x="385.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2991" values="#0f172a;#f4ffff"/></rect>
<rect x="396.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3005" values="#0f172a;#0b0000"/></rect>
<rect x="406.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3019" values="#0f172a;#000000"/></rect>
<rect x="417.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3033" values="#0f172a;#000000"/></rect>
<rect x="427.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3047" values="#0f172a;#000000"/></rect>
<rect x="438.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3060" values="#0f172a;#000000"/></rect>
<rect x="448.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3074" values="#0f172a;#000000"/></rect>
<rect x="459.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3088" values="#0f172a;#000000"/></rect>
<rect x="469.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3102" values="#0f172a;#000000"/></rect>
<rect x="480.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3116" values="#0f172a;#000000"/></rect>
<rect x="490.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3130" values="#0f172a;#000000"/></rect>
<rect x="501.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3144" values="#0f172a;#000000"/></rect>
<rect x="511.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3158" values="#0f172a;#000000"/></rect>
<rect x="522.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3172" values="#0f172a;#000000"/></rect>
<rect x="532.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3186" values="#0f172a;#000000"/></rect>
<rect x="543.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3200" values="#0f172a;#000000"/></rect>
<rect x="553.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3214" values="#0f172a;#000000"/></rect>
<rect x="564.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3228" values="#0f172a;#000000"/></rect>
<rect x="574.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3242" values="#0f172a;#000000"/></rect>
<rect x="585.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3256" values="#0f172a;#000000"/></rect>
<rect x="595.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3270" values="#0f172a;#000000"/></rect>
<rect x="606.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3284" values="#0f172a;#000000"/></rect>
<rect x="616.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3298" values="#0f172a;#000000"/></rect>
<rect x="627.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3312" values="#0f172a;#0000ff"/></rect>
<rect x="637.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3326" values="#0f172a;#0000ff"/></rect>
<rect x="648.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3340" values="#0f172a;#00ffff"/></rect>
<rect x="658.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3353" values="#0f172a;#00ffff"/></rect>
<rect x="669.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3367" values="#0f172a;#9dffff"/></rect>
<rect x="679.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3381" values="#0f172a;#ffffff"/></rect>
<rect x="690.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3395" values="#0f172a;#ffffff"/></rect>
<rect x="700.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3409" values="#0f172a;#ffffff"/></rect>
<rect x="711.0" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3423" values="#0f172a;#ffffff"/></rect>
<rect x="721.5" y="178.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3437" values="#0f172a;#ffffff"/></rect>
<rect x="60.0" y="178" width="672.0" height="30.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3254;0.3256;1.0000" values="0;0;1;1"/><text x="742.0" y="190" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">中心の縁 0 画素</text>
<text x="742.0" y="208" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">端の縁 5 画素</text>
</g>
<text x="60.0" y="236" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">ずれの強さ k = 1</text>
<rect x="60.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4419" values="#0f172a;#000000"/></rect>
<rect x="70.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4433" values="#0f172a;#000000"/></rect>
<rect x="81.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4447" values="#0f172a;#000000"/></rect>
<rect x="91.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4460" values="#0f172a;#000000"/></rect>
<rect x="102.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474" values="#0f172a;#000000"/></rect>
<rect x="112.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4488" values="#0f172a;#000000"/></rect>
<rect x="123.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4502" values="#0f172a;#000000"/></rect>
<rect x="133.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4516" values="#0f172a;#000000"/></rect>
<rect x="144.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4530" values="#0f172a;#000000"/></rect>
<rect x="154.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4544" values="#0f172a;#000000"/></rect>
<rect x="165.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4558" values="#0f172a;#000000"/></rect>
<rect x="175.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4572" values="#0f172a;#000000"/></rect>
<rect x="186.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4586" values="#0f172a;#820000"/></rect>
<rect x="196.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4600" values="#0f172a;#ff0000"/></rect>
<rect x="207.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4614" values="#0f172a;#ff0000"/></rect>
<rect x="217.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4628" values="#0f172a;#ff0000"/></rect>
<rect x="228.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4642" values="#0f172a;#ffff00"/></rect>
<rect x="238.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4656" values="#0f172a;#ffff00"/></rect>
<rect x="249.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4670" values="#0f172a;#ffff91"/></rect>
<rect x="259.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4684" values="#0f172a;#ffffff"/></rect>
<rect x="270.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4698" values="#0f172a;#ffffff"/></rect>
<rect x="280.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4712" values="#0f172a;#ffffff"/></rect>
<rect x="291.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4726" values="#0f172a;#ffffff"/></rect>
<rect x="301.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4740" values="#0f172a;#ffffff"/></rect>
<rect x="312.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4753" values="#0f172a;#ffffff"/></rect>
<rect x="322.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4767" values="#0f172a;#ffffff"/></rect>
<rect x="333.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4781" values="#0f172a;#ffffff"/></rect>
<rect x="343.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4795" values="#0f172a;#ffffff"/></rect>
<rect x="354.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#0f172a;#ffffff"/></rect>
<rect x="364.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4823" values="#0f172a;#ffffff"/></rect>
<rect x="375.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4837" values="#0f172a;#ffffff"/></rect>
<rect x="385.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4851" values="#0f172a;#e8ffff"/></rect>
<rect x="396.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4865" values="#0f172a;#170000"/></rect>
<rect x="406.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4879" values="#0f172a;#000000"/></rect>
<rect x="417.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4893" values="#0f172a;#000000"/></rect>
<rect x="427.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4907" values="#0f172a;#000000"/></rect>
<rect x="438.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4921" values="#0f172a;#000000"/></rect>
<rect x="448.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4935" values="#0f172a;#000000"/></rect>
<rect x="459.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4949" values="#0f172a;#000000"/></rect>
<rect x="469.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963" values="#0f172a;#000000"/></rect>
<rect x="480.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4977" values="#0f172a;#000000"/></rect>
<rect x="490.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4991" values="#0f172a;#000000"/></rect>
<rect x="501.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5005" values="#0f172a;#000000"/></rect>
<rect x="511.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5019" values="#0f172a;#000000"/></rect>
<rect x="522.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5033" values="#0f172a;#000000"/></rect>
<rect x="532.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5047" values="#0f172a;#000000"/></rect>
<rect x="543.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5060" values="#0f172a;#000000"/></rect>
<rect x="553.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5074" values="#0f172a;#000000"/></rect>
<rect x="564.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5088" values="#0f172a;#000000"/></rect>
<rect x="574.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5102" values="#0f172a;#000000"/></rect>
<rect x="585.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5116" values="#0f172a;#000000"/></rect>
<rect x="595.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5130" values="#0f172a;#000000"/></rect>
<rect x="606.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5144" values="#0f172a;#0000b0"/></rect>
<rect x="616.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5158" values="#0f172a;#0000ff"/></rect>
<rect x="627.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5172" values="#0f172a;#0000ff"/></rect>
<rect x="637.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5186" values="#0f172a;#0000ff"/></rect>
<rect x="648.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5200" values="#0f172a;#00ffff"/></rect>
<rect x="658.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5214" values="#0f172a;#00ffff"/></rect>
<rect x="669.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5228" values="#0f172a;#00ffff"/></rect>
<rect x="679.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5242" values="#0f172a;#00ffff"/></rect>
<rect x="690.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5256" values="#0f172a;#00ffff"/></rect>
<rect x="700.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5270" values="#0f172a;#b0ffff"/></rect>
<rect x="711.0" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5284" values="#0f172a;#ffffff"/></rect>
<rect x="721.5" y="240.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5298" values="#0f172a;#ffffff"/></rect>
<rect x="60.0" y="240" width="672.0" height="30.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5114;0.5116;1.0000" values="0;0;1;1"/><text x="742.0" y="252" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">中心の縁 0 画素</text>
<text x="742.0" y="270" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">端の縁 10 画素</text>
</g>
<text x="60.0" y="298" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">ずれの強さ k = 2</text>
<rect x="60.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6279" values="#0f172a;#000000"/></rect>
<rect x="70.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6293" values="#0f172a;#000000"/></rect>
<rect x="81.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6307" values="#0f172a;#000000"/></rect>
<rect x="91.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6321" values="#0f172a;#000000"/></rect>
<rect x="102.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6335" values="#0f172a;#000000"/></rect>
<rect x="112.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6349" values="#0f172a;#000000"/></rect>
<rect x="123.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6363" values="#0f172a;#2e0000"/></rect>
<rect x="133.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6377" values="#0f172a;#d10000"/></rect>
<rect x="144.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6391" values="#0f172a;#ff0000"/></rect>
<rect x="154.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6405" values="#0f172a;#ff0000"/></rect>
<rect x="165.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6419" values="#0f172a;#ff0000"/></rect>
<rect x="175.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6433" values="#0f172a;#ff0000"/></rect>
<rect x="186.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6447" values="#0f172a;#ff0000"/></rect>
<rect x="196.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6460" values="#0f172a;#ff0000"/></rect>
<rect x="207.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6474" values="#0f172a;#ff0000"/></rect>
<rect x="217.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6488" values="#0f172a;#ff0000"/></rect>
<rect x="228.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6502" values="#0f172a;#ffff00"/></rect>
<rect x="238.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6516" values="#0f172a;#ffff00"/></rect>
<rect x="249.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6530" values="#0f172a;#ffff00"/></rect>
<rect x="259.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6544" values="#0f172a;#ffff00"/></rect>
<rect x="270.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6558" values="#0f172a;#ffffdb"/></rect>
<rect x="280.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6572" values="#0f172a;#ffffff"/></rect>
<rect x="291.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6586" values="#0f172a;#ffffff"/></rect>
<rect x="301.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6600" values="#0f172a;#ffffff"/></rect>
<rect x="312.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6614" values="#0f172a;#ffffff"/></rect>
<rect x="322.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6628" values="#0f172a;#ffffff"/></rect>
<rect x="333.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6642" values="#0f172a;#ffffff"/></rect>
<rect x="343.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6656" values="#0f172a;#ffffff"/></rect>
<rect x="354.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6670" values="#0f172a;#ffffff"/></rect>
<rect x="364.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6684" values="#0f172a;#ffffff"/></rect>
<rect x="375.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6698" values="#0f172a;#ffffff"/></rect>
<rect x="385.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6712" values="#0f172a;#d1ffff"/></rect>
<rect x="396.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6726" values="#0f172a;#2e0000"/></rect>
<rect x="406.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6740" values="#0f172a;#000000"/></rect>
<rect x="417.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6753" values="#0f172a;#000000"/></rect>
<rect x="427.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6767" values="#0f172a;#000000"/></rect>
<rect x="438.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6781" values="#0f172a;#000000"/></rect>
<rect x="448.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6795" values="#0f172a;#000000"/></rect>
<rect x="459.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6809" values="#0f172a;#000000"/></rect>
<rect x="469.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6823" values="#0f172a;#000000"/></rect>
<rect x="480.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6837" values="#0f172a;#000000"/></rect>
<rect x="490.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6851" values="#0f172a;#000000"/></rect>
<rect x="501.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6865" values="#0f172a;#000000"/></rect>
<rect x="511.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6879" values="#0f172a;#000000"/></rect>
<rect x="522.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6893" values="#0f172a;#000000"/></rect>
<rect x="532.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#0f172a;#000000"/></rect>
<rect x="543.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6921" values="#0f172a;#000000"/></rect>
<rect x="553.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6935" values="#0f172a;#000000"/></rect>
<rect x="564.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6949" values="#0f172a;#000000"/></rect>
<rect x="574.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6963" values="#0f172a;#00004c"/></rect>
<rect x="585.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6977" values="#0f172a;#0000ff"/></rect>
<rect x="595.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6991" values="#0f172a;#0000ff"/></rect>
<rect x="606.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7005" values="#0f172a;#0000ff"/></rect>
<rect x="616.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7019" values="#0f172a;#0000ff"/></rect>
<rect x="627.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7033" values="#0f172a;#0000ff"/></rect>
<rect x="637.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7047" values="#0f172a;#0000ff"/></rect>
<rect x="648.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7060" values="#0f172a;#00ffff"/></rect>
<rect x="658.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7074" values="#0f172a;#00ffff"/></rect>
<rect x="669.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7088" values="#0f172a;#00ffff"/></rect>
<rect x="679.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7102" values="#0f172a;#00ffff"/></rect>
<rect x="690.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7116" values="#0f172a;#00ffff"/></rect>
<rect x="700.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7130" values="#0f172a;#00ffff"/></rect>
<rect x="711.0" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7144" values="#0f172a;#00ffff"/></rect>
<rect x="721.5" y="302.0" width="10.8" height="30.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7158" values="#0f172a;#00ffff"/></rect>
<rect x="60.0" y="302" width="672.0" height="30.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6975;0.6977;1.0000" values="0;0;1;1"/><text x="742.0" y="314" text-anchor="start" style="font-size:12px;font-weight:700;fill:#1f2937">中心の縁 2 画素</text>
<text x="742.0" y="332" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">端の縁 12 画素</text>
</g>
<line x1="228.0" y1="100" x2="228.0" y2="366" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="3 4"/>
<line x1="396.0" y1="100" x2="396.0" y2="366" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="3 4"/>
<line x1="648.0" y1="100" x2="648.0" y2="366" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="3 4"/>
<text x="390.75" y="380" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b">▲ 画面の中心</text>
<text x="40" y="420" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">端の縁の、色のにじみ(画素):</text>
<text x="240" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1393;0.1395;1.0000" values="1;1;0;0"/></text>
<text x="240" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1393;0.1395;0.3254;0.3256;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">5<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3254;0.3256;0.5114;0.5116;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">10<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5114;0.5116;0.6975;0.6977;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="424" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">12<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6975;0.6977;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.7905;0.7907;1.0000" values="0;0;1;1"/><rect x="480" y="410" width="450" height="70" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="496" y="434" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">中心はずれない。端ほど、赤と青が離れる</text>
<text x="496" y="457" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">中心の縁: 0 → 2 画素 / 端の縁: 0 → 12 画素</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">レンズは、色(波長)によって、曲がり方が少し違う<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">中心からの距離に比例して、赤を外へ、青を内へずらす<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.8138;0.8140;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ずれを強くしすぎると、見づらい。やりすぎない<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.8138;0.8140;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:chromatic-aberration-shift:end -->

## 適用の順序

| 順序 | 効果 | 理由 |
| --- | --- | --- |
| ① HDR のうち | ブルーム・レンズ フレア | 明るさが 1 を超える光が必要 |
| ② トーンマップ | HDR → LDR | — |
| ③ LDR で | 色収差・ビネット・グレイン | 見た目の色に直接かける |
| ④ UI の前に | UI はこれらの影響を受けない | 文字が歪まない・読める |

<strong>1 つのパスに色収差・ビネット・グレイン・トーンマップ・ガンマをまとめる</strong>と<strong>フル解像度のパスが 1 回で済み</strong>、帯域が減ります。

## かけすぎない

| 効果 | かけすぎると |
| --- | --- |
| 色収差 | 画面が溶けて見え、目が疲れる・酔う |
| ビネット | 画面の周辺が見えず、プレイしにくい |
| グレイン | ざらざらで細部が見えない |
| フレア | 眩しすぎて、何も見えない |

<strong>これらは全部「オプションでオフ」にできる</strong>ように<strong>します</strong>。<strong>アクセシビリティ（光過敏・酔いやすい人）</strong>にも重要です。

## 関連ページ

- [Post-Processing](../index.md)
- [Bloom](../bloom/index.md)
- [Color Grading](../color-grading/index.md)
- [God Rays](../../atmosphere/god-rays/index.md)
