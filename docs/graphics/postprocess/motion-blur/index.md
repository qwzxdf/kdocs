---
title: Motion Blur
tags:
  - 描画
---

# Motion Blur

<strong>モーション ブラー</strong>は <strong>動いている物（またはカメラ）が、動いた方向に「にじむ・流れる」</strong>効果です。<strong>実際のカメラはシャッターが開いている間に物が動くので、その軌跡がぶれて写ります</strong>。ゲームの 1 フレームは「一瞬」を切り取った絵なので動きがカクカクに見えがちですが、ブラーを足すと滑らかでスピード感のある動きになります。このセクションでは速度バッファ・カメラのブラー・オブジェクトのブラー・ぼかしの実装・タイル最大速度・強さと TAA を、1 つずつ別のページで説明します。

## 動きで見る

<!-- fig:motion-blur-shutter:begin -->

<svg class="fig illust motion" data-fig="motion-blur-shutter" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-motion-blur-shutter" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">モーション ブラー: シャッターが開いている間の位置を、全部足して平均する</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 フレームで 16 画素動く棒(幅 4 画素)を、シャッターの開き具合を変えて撮る。8 回に分けて足す</text>
<text x="48.0" y="92" text-anchor="start" style="font-size:14px;font-weight:700;fill:#64748b">シャッター 0°(一瞬)</text>
<rect x="48.0" y="100" width="864.0" height="26" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
<rect x="192.0" y="102" width="72.0" height="22" fill="#64748b" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="192.0" y="102" width="72.0" height="22" fill="#64748b" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0624;0.0626;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="192.0" y="102" width="72.0" height="22" fill="#64748b" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0736;0.0738;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="192.0" y="102" width="72.0" height="22" fill="#64748b" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0849;0.0851;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="192.0" y="102" width="72.0" height="22" fill="#64748b" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0962;0.0964;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="192.0" y="102" width="72.0" height="22" fill="#64748b" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1075;0.1077;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="192.0" y="102" width="72.0" height="22" fill="#64748b" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1188;0.1190;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="192.0" y="102" width="72.0" height="22" fill="#64748b" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1301;0.1303;1.0000" values="0;0;0.9;0.9"/></rect>
<rect x="48.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="66.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="84.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="102.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="120.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="138.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="156.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="174.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="192.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#334155"/></rect>
<rect x="210.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#334155"/></rect>
<rect x="228.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#334155"/></rect>
<rect x="246.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#334155"/></rect>
<rect x="264.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="282.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="300.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="318.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="336.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="354.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="372.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="390.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="408.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="426.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="444.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="462.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="480.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="498.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="516.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="534.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="552.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="570.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="588.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="606.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="624.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="642.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="660.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="678.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="696.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="714.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="732.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="750.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="768.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="786.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="804.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="822.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="840.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="858.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="876.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<rect x="894.0" y="132.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1518" values="#e5e7eb;#f8fafc"/></rect>
<text x="918.0" y="152" text-anchor="start" style="font-size:1px;font-weight:700;fill:#1f2937"/>
<text x="900" y="121" text-anchor="end" style="font-size:14px;font-weight:700;fill:#64748b" opacity="0">最大 100%<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.1516;0.1518;1.0000" values="0;0;1;1"/></text>
<text x="48.0" y="170" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">シャッター 90°</text>
<rect x="48.0" y="178" width="864.0" height="26" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
<rect x="192.0" y="180" width="72.0" height="22" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2254;0.2256;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="228.0" y="196" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">1<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2254;0.2256;1.0000" values="0;0;1;1"/></text>
<rect x="202.29" y="180" width="72.0" height="22" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2367;0.2369;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="238.29" y="196" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">2<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2367;0.2369;1.0000" values="0;0;1;1"/></text>
<rect x="212.57" y="180" width="72.0" height="22" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2480;0.2482;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="248.57" y="196" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">3<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2480;0.2482;1.0000" values="0;0;1;1"/></text>
<rect x="222.86" y="180" width="72.0" height="22" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2593;0.2595;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="258.86" y="196" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">4<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2593;0.2595;1.0000" values="0;0;1;1"/></text>
<rect x="233.14" y="180" width="72.0" height="22" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2706;0.2708;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="269.14" y="196" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">5<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2706;0.2708;1.0000" values="0;0;1;1"/></text>
<rect x="243.43" y="180" width="72.0" height="22" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2818;0.2821;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="279.43" y="196" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">6<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2818;0.2821;1.0000" values="0;0;1;1"/></text>
<rect x="253.71" y="180" width="72.0" height="22" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2931;0.2933;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="289.71" y="196" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">7<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2931;0.2933;1.0000" values="0;0;1;1"/></text>
<rect x="264.0" y="180" width="72.0" height="22" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3044;0.3046;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="300.0" y="196" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">8<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3044;0.3046;1.0000" values="0;0;1;1"/></text>
<rect x="48.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="66.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="84.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="102.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="120.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="138.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="156.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="174.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="192.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#d4eadb"/></rect>
<rect x="210.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#a9d7b3"/></rect>
<rect x="228.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#7dc38c"/></rect>
<rect x="246.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#52b064"/></rect>
<rect x="264.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#52b064"/></rect>
<rect x="282.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#7dc38c"/></rect>
<rect x="300.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#a9d7b3"/></rect>
<rect x="318.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#d4eadb"/></rect>
<rect x="336.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="354.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="372.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="390.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="408.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="426.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="444.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="462.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="480.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="498.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="516.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="534.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="552.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="570.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="588.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="606.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="624.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="642.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="660.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="678.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="696.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="714.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="732.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="750.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="768.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="786.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="804.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="822.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="840.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="858.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="876.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<rect x="894.0" y="210.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3262" values="#e5e7eb;#f8fafc"/></rect>
<text x="918.0" y="230" text-anchor="start" style="font-size:1px;font-weight:700;fill:#1f2937"/>
<text x="900" y="199" text-anchor="end" style="font-size:14px;font-weight:700;fill:#2ea043" opacity="0">最大 82%<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3259;0.3262;1.0000" values="0;0;1;1"/></text>
<text x="48.0" y="248" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">シャッター 180°(映画の標準)</text>
<rect x="48.0" y="256" width="864.0" height="26" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
<rect x="192.0" y="258" width="72.0" height="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4101;0.4103;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="228.0" y="274" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">1<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4101;0.4103;1.0000" values="0;0;1;1"/></text>
<rect x="212.57" y="258" width="72.0" height="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4213;0.4215;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="248.57" y="274" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">2<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4213;0.4215;1.0000" values="0;0;1;1"/></text>
<rect x="233.14" y="258" width="72.0" height="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4326;0.4328;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="269.14" y="274" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">3<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4326;0.4328;1.0000" values="0;0;1;1"/></text>
<rect x="253.71" y="258" width="72.0" height="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4439;0.4441;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="289.71" y="274" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">4<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4439;0.4441;1.0000" values="0;0;1;1"/></text>
<rect x="274.29" y="258" width="72.0" height="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4552;0.4554;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="310.29" y="274" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">5<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4552;0.4554;1.0000" values="0;0;1;1"/></text>
<rect x="294.86" y="258" width="72.0" height="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4665;0.4667;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="330.86" y="274" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">6<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4665;0.4667;1.0000" values="0;0;1;1"/></text>
<rect x="315.43" y="258" width="72.0" height="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4777;0.4779;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="351.43" y="274" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">7<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4777;0.4779;1.0000" values="0;0;1;1"/></text>
<rect x="336.0" y="258" width="72.0" height="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4890;0.4892;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="372.0" y="274" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">8<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4890;0.4892;1.0000" values="0;0;1;1"/></text>
<rect x="48.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="66.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="84.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="102.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="120.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="138.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="156.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="174.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="192.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#dee7fa"/></rect>
<rect x="210.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#c7d7f8"/></rect>
<rect x="228.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#b0c7f6"/></rect>
<rect x="246.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#9ab7f4"/></rect>
<rect x="264.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#9eb9f5"/></rect>
<rect x="282.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#9eb9f5"/></rect>
<rect x="300.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#9eb9f5"/></rect>
<rect x="318.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#9eb9f5"/></rect>
<rect x="336.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#9ab7f4"/></rect>
<rect x="354.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#b0c7f6"/></rect>
<rect x="372.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#c7d7f8"/></rect>
<rect x="390.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#dee7fa"/></rect>
<rect x="408.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="426.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="444.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="462.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="480.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="498.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="516.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="534.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="552.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="570.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="588.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="606.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="624.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="642.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="660.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="678.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="696.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="714.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="732.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="750.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="768.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="786.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="804.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="822.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="840.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="858.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="876.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<rect x="894.0" y="288.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108" values="#e5e7eb;#f8fafc"/></rect>
<text x="918.0" y="308" text-anchor="start" style="font-size:1px;font-weight:700;fill:#1f2937"/>
<text x="900" y="277" text-anchor="end" style="font-size:14px;font-weight:700;fill:#2563eb" opacity="0">最大 45%<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5106;0.5108;1.0000" values="0;0;1;1"/></text>
<text x="48.0" y="326" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">シャッター 360°(開きっぱなし)</text>
<rect x="48.0" y="334" width="864.0" height="26" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
<rect x="192.0" y="336" width="72.0" height="22" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5947;0.5949;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="228.0" y="352" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">1<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5947;0.5949;1.0000" values="0;0;1;1"/></text>
<rect x="233.14" y="336" width="72.0" height="22" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6059;0.6062;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="269.14" y="352" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">2<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6059;0.6062;1.0000" values="0;0;1;1"/></text>
<rect x="274.29" y="336" width="72.0" height="22" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6172;0.6174;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="310.29" y="352" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">3<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6172;0.6174;1.0000" values="0;0;1;1"/></text>
<rect x="315.43" y="336" width="72.0" height="22" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6285;0.6287;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="351.43" y="352" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">4<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6285;0.6287;1.0000" values="0;0;1;1"/></text>
<rect x="356.57" y="336" width="72.0" height="22" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6398;0.6400;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="392.57" y="352" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">5<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6398;0.6400;1.0000" values="0;0;1;1"/></text>
<rect x="397.71" y="336" width="72.0" height="22" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6511;0.6513;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="433.71" y="352" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">6<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6511;0.6513;1.0000" values="0;0;1;1"/></text>
<rect x="438.86" y="336" width="72.0" height="22" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6624;0.6626;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="474.86" y="352" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">7<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6624;0.6626;1.0000" values="0;0;1;1"/></text>
<rect x="480.0" y="336" width="72.0" height="22" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6736;0.6738;1.0000" values="0;0;0.32;0.32"/></rect>
<text x="516.0" y="352" text-anchor="middle" style="font-size:10px;font-weight:700;fill:#ffffff" opacity="0">8<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6736;0.6738;1.0000" values="0;0;1;1"/></text>
<rect x="48.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="66.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="84.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="102.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="120.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="138.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="156.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="174.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="192.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f6e4e6"/></rect>
<rect x="210.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f6e4e6"/></rect>
<rect x="228.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f4d4d6"/></rect>
<rect x="246.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f3ced0"/></rect>
<rect x="264.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f5dadd"/></rect>
<rect x="282.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f3ced0"/></rect>
<rect x="300.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f5dadd"/></rect>
<rect x="318.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f3ced0"/></rect>
<rect x="336.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f4d7da"/></rect>
<rect x="354.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f4d1d3"/></rect>
<rect x="372.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f4d1d3"/></rect>
<rect x="390.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f4d7da"/></rect>
<rect x="408.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f3ced0"/></rect>
<rect x="426.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f5dadd"/></rect>
<rect x="444.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f3ced0"/></rect>
<rect x="462.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f5dadd"/></rect>
<rect x="480.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f3ced0"/></rect>
<rect x="498.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f4d4d6"/></rect>
<rect x="516.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f6e4e6"/></rect>
<rect x="534.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f6e4e6"/></rect>
<rect x="552.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="570.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="588.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="606.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="624.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="642.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="660.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="678.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="696.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="714.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="732.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="750.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="768.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="786.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="804.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="822.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="840.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="858.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="876.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<rect x="894.0" y="366.0" width="18.3" height="18.3" fill="#e5e7eb"><animate attributeName="fill" dur="19.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6954" values="#e5e7eb;#f8fafc"/></rect>
<text x="918.0" y="386" text-anchor="start" style="font-size:1px;font-weight:700;fill:#1f2937"/>
<text x="900" y="355" text-anchor="end" style="font-size:14px;font-weight:700;fill:#e5484d" opacity="0">最大 25%<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6952;0.6954;1.0000" values="0;0;1;1"/></text>
<text x="48" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">足した位置の数(合計):</text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2254;0.2256;1.0000" values="1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">1<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2254;0.2256;0.2367;0.2369;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">2<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2367;0.2369;0.2480;0.2482;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">3<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2480;0.2482;0.2593;0.2595;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2593;0.2595;0.2706;0.2708;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">5<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2706;0.2708;0.2818;0.2821;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">6<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2818;0.2821;0.2931;0.2933;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">7<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2931;0.2933;0.3044;0.3046;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">8<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.3044;0.3046;0.4101;0.4103;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">9<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4101;0.4103;0.4213;0.4215;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">10<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4213;0.4215;0.4326;0.4328;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">11<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4326;0.4328;0.4439;0.4441;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">12<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4439;0.4441;0.4552;0.4554;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">13<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4552;0.4554;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">14<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4665;0.4667;0.4777;0.4779;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">15<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4777;0.4779;0.4890;0.4892;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4890;0.4892;0.5947;0.5949;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">17<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5947;0.5949;0.6059;0.6062;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">18<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6059;0.6062;0.6172;0.6174;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">19<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6172;0.6174;0.6285;0.6287;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">20<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6285;0.6287;0.6398;0.6400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">21<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6398;0.6400;0.6511;0.6513;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">22<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6511;0.6513;0.6624;0.6626;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">23<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6624;0.6626;0.6736;0.6738;1.0000" values="0;0;1;1;0;0"/></text>
<text x="250" y="431" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed" opacity="0">24<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.6736;0.6738;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.7567;0.7569;1.0000" values="0;0;1;1"/><rect x="560" y="406" width="370" height="100" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="576" y="430" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">ブラーの長さ = 速さ × シャッターの開き</text>
<text x="576" y="454" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">0° → 90° → 180° → 360° で、長さ 0 / 4 / 8 / 16 画素</text>
<text x="576" y="476" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">全体の明るさは変えずに、ぼかすので、ピークが下がる</text>
</g>
<text x="48" y="480" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">同じ動きを、シャッターの開き具合だけ変えて撮る<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;1.0000" values="1;1;0;0"/></text>
<text x="48" y="480" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">シャッター 0°: 位置は 1 つ。くっきり止まって見える<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.0511;0.0513;0.2254;0.2256;1.0000" values="0;0;1;1;0;0"/></text>
<text x="48" y="480" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">90°: 動く間の 8 つの位置を足す。少し尾を引く<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.2254;0.2256;0.4101;0.4103;1.0000" values="0;0;1;1;0;0"/></text>
<text x="48" y="480" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">180°: 映画で一般的な長さ<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.4101;0.4103;0.5947;0.5949;1.0000" values="0;0;1;1;0;0"/></text>
<text x="48" y="480" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">360°: 動く全区間が尾になる。薄く長くなる<animate attributeName="opacity" dur="19.5s" repeatCount="indefinite" keyTimes="0.0000;0.5947;0.5949;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:motion-blur-shutter:end -->

## 全体の流れ

| 手順 | 内容 | ページ |
| --- | --- | --- |
| ① 速度を作る | 画素ごとの移動ベクトル | [Velocity Buffer](velocity-buffer.md) |
| ②a カメラの動き | 深度と行列から、背景の速度 | [Camera Motion Blur](camera-blur.md) |
| ②b 物体の動き | 動く物体・スキニングの速度 | [Object Motion Blur](object-blur.md) |
| ③ ぼかす | 速度に沿って、サンプルを集める | [Blur Pass Implementation](blur-pass.md) |
| ④ 高速化 | タイルの最大速度で無駄を省く | [Tile Max Velocity](tile-max.md) |
| ⑤ 設計 | シャッター角・最大長・TAA との関係 | [Strength and TAA](strength-taa.md) |

## DirectX 11 で組む

### 速度バッファを G バッファに混ぜる

```cpp
// 速度は、G バッファの MRT の 1 枚として、ジオメトリのパスで、同時に書く。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R16G16_FLOAT;                         // 画面上のずれ（UV 単位）。負の値も持てる
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_RENDER_TARGET | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &velocity_texture);
```

動く物はジオメトリのパスで速度を、書きます。動かない物（背景）はカメラの動きだけで、決まるので速度を書く必要がなくパスの最後に、深度から計算して補います（[Velocity Buffer](velocity-buffer.md)）。

### 3 つのパス

```cpp
// ① タイル最大: 速度を、16×16 画素のタイルごとの、最大に、縮める（計算シェーダー）。
const UINT tile = 16;
Dispatch(tile_max_cs, {velocity_srv}, {tile_max_uav}, (width + tile - 1) / tile, (height + tile - 1) / tile, 1);

// ② 近傍最大: 周りの 3×3 タイルの、最大を、取る（広がりを、隣へ伝える）。
Dispatch(neighbor_max_cs, {tile_max_srv}, {neighbor_max_uav}, tile_groups_x, tile_groups_y, 1);

// ③ ブラー: 近傍最大の方向へ、シーン色を、サンプル（フルスクリーン）。
context->OMSetRenderTargets(1, motion_blur_rtv.GetAddressOf(), nullptr);
ID3D11ShaderResourceView* srvs[] = {scene_srv.Get(), velocity_srv.Get(), depth_srv.Get(), neighbor_max_srv.Get()};
context->PSSetShaderResources(0, 4, srvs);
DrawFullscreenTriangle();
```

タイル最大は「このタイルの近くで、最も速く動く物はどちらへ動いているか」を、教えます。ブラーのパスはこの方向を基準に、サンプルするので速い物の輪郭の、外側までにじみます（[Tile Max](tile-max.md)）。

## 関連ページ

- [Post-Processing](../index.md)
- [Depth of Field (DOF)](../dof/index.md)
- [TAA](../antialiasing/taa.md)
- [Exposure](../tonemapping/exposure.md)
