---
title: Step 2: Light Injection
tags:
  - 描画
---

# Step 2: Light Injection

<strong>各 froxel に太陽やライトの光を計算して、足します</strong>。<strong>シャドウ マップを参照</strong>して、影の中は光を入れないので光の筋ができます。このページでは光の注入を説明します。

!!! tip "ポイント"
    - 各セルでライトの光 × 位相関数 × 影。
    - 太陽・点光源・スポットライトのすべてに対応。
    - シャドウ マップを参照して、光の筋を作る。
    - ライトの数が多いと、重い（クラスタ化で軽く）。

<!-- fig:light-injection:begin -->

<svg class="fig illust motion" data-fig="light-injection" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-light-injection" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">光の注入: 霧の 3D 格子の各マスに、「そこに届く光」を、ライトごとに書き込む</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">上から見た 1 つのスライス(24×12 マス)。2 つのライトと、光を遮る壁。各マスで、光を計算して足す</text>
<rect x="30" y="96" width="620.0" height="320.0" fill="#ffffff" stroke="#e5aa28" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">① 霧の 1 スライス(各マスに、光を足す)</text>
<rect x="40.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698;0.3256" values="#0f172a;#1b140b;#1b140b"/></rect>
<rect x="65.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721;0.3279" values="#0f172a;#261c0f;#261c0f"/></rect>
<rect x="90.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744;0.3302" values="#0f172a;#342715;#342715"/></rect>
<rect x="115.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767;0.3326" values="#0f172a;#47351c;#47351c"/></rect>
<rect x="140.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791;0.3349" values="#0f172a;#564022;#564022"/></rect>
<rect x="165.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0814;0.3372" values="#0f172a;#564022;#564022"/></rect>
<rect x="190.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837;0.3395" values="#0f172a;#47351c;#47351c"/></rect>
<rect x="215.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0860;0.3419" values="#0f172a;#342715;#342715"/></rect>
<rect x="240.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884;0.3442" values="#0f172a;#261c0f;#261c0f"/></rect>
<rect x="265.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907;0.3465" values="#0f172a;#1b140b;#1b140b"/></rect>
<rect x="290.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930;0.3488" values="#0f172a;#140f08;#140f08"/></rect>
<rect x="315.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#0f172a;#475569"/></rect>
<rect x="340.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977;0.3535" values="#0f172a;#000000;#040608"/></rect>
<rect x="365.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.3558" values="#0f172a;#000000;#040609"/></rect>
<rect x="390.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023;0.3581" values="#0f172a;#000000;#05070a"/></rect>
<rect x="415.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047;0.3605" values="#0f172a;#000000;#05080b"/></rect>
<rect x="440.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070;0.3628" values="#0f172a;#000000;#06090c"/></rect>
<rect x="465.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093;0.3651" values="#0f172a;#000000;#06090d"/></rect>
<rect x="490.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116;0.3674" values="#0f172a;#000000;#06090e"/></rect>
<rect x="515.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1140;0.3698" values="#0f172a;#000000;#06090e"/></rect>
<rect x="540.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163;0.3721" values="#0f172a;#000000;#06090d"/></rect>
<rect x="565.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186;0.3744" values="#0f172a;#000000;#06090c"/></rect>
<rect x="590.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209;0.3767" values="#0f172a;#000000;#05080b"/></rect>
<rect x="615.0" y="110.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233;0.3791" values="#0f172a;#000000;#05070a"/></rect>
<rect x="40.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698;0.3256" values="#0f172a;#20180d;#20180d"/></rect>
<rect x="65.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721;0.3279" values="#0f172a;#2e2312;#2e2312"/></rect>
<rect x="90.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744;0.3302" values="#0f172a;#47351c;#47351c"/></rect>
<rect x="115.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767;0.3326" values="#0f172a;#6d522c;#6d522c"/></rect>
<rect x="140.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791;0.3349" values="#0f172a;#96703c;#96703c"/></rect>
<rect x="165.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0814;0.3372" values="#0f172a;#96703c;#96703c"/></rect>
<rect x="190.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837;0.3395" values="#0f172a;#6d522c;#6d522c"/></rect>
<rect x="215.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0860;0.3419" values="#0f172a;#47351c;#47351c"/></rect>
<rect x="240.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884;0.3442" values="#0f172a;#2e2312;#2e2312"/></rect>
<rect x="265.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907;0.3465" values="#0f172a;#20180d;#20180d"/></rect>
<rect x="290.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930;0.3488" values="#0f172a;#171109;#171109"/></rect>
<rect x="315.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#0f172a;#475569"/></rect>
<rect x="340.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977;0.3535" values="#0f172a;#000000;#040609"/></rect>
<rect x="365.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.3558" values="#0f172a;#000000;#05070b"/></rect>
<rect x="390.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023;0.3581" values="#0f172a;#000000;#06090c"/></rect>
<rect x="415.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047;0.3605" values="#0f172a;#000000;#060a0e"/></rect>
<rect x="440.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070;0.3628" values="#0f172a;#000000;#070b10"/></rect>
<rect x="465.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093;0.3651" values="#0f172a;#000000;#080c11"/></rect>
<rect x="490.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116;0.3674" values="#0f172a;#000000;#080c12"/></rect>
<rect x="515.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1140;0.3698" values="#0f172a;#000000;#080c12"/></rect>
<rect x="540.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163;0.3721" values="#0f172a;#000000;#080c11"/></rect>
<rect x="565.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186;0.3744" values="#0f172a;#000000;#070b10"/></rect>
<rect x="590.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209;0.3767" values="#0f172a;#000000;#060a0e"/></rect>
<rect x="615.0" y="135.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233;0.3791" values="#0f172a;#000000;#06090c"/></rect>
<rect x="40.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698;0.3256" values="#0f172a;#221a0e;#221a0e"/></rect>
<rect x="65.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721;0.3279" values="#0f172a;#342715;#342715"/></rect>
<rect x="90.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744;0.3302" values="#0f172a;#564022;#564022"/></rect>
<rect x="115.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767;0.3326" values="#0f172a;#96703c;#96703c"/></rect>
<rect x="140.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791;0.3349" values="#0f172a;#efb35f;#efb35f"/></rect>
<rect x="165.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0814;0.3372" values="#0f172a;#efb35f;#efb35f"/></rect>
<rect x="190.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837;0.3395" values="#0f172a;#96703c;#96703c"/></rect>
<rect x="215.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0860;0.3419" values="#0f172a;#564022;#564022"/></rect>
<rect x="240.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884;0.3442" values="#0f172a;#342715;#342715"/></rect>
<rect x="265.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907;0.3465" values="#0f172a;#221a0e;#221a0e"/></rect>
<rect x="290.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930;0.3488" values="#0f172a;#18120a;#18120a"/></rect>
<rect x="315.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#0f172a;#475569"/></rect>
<rect x="340.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977;0.3535" values="#0f172a;#000000;#05070b"/></rect>
<rect x="365.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.3558" values="#0f172a;#000000;#06090d"/></rect>
<rect x="390.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023;0.3581" values="#0f172a;#000000;#070b0f"/></rect>
<rect x="415.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047;0.3605" values="#0f172a;#000000;#080c12"/></rect>
<rect x="440.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070;0.3628" values="#0f172a;#000000;#090e14"/></rect>
<rect x="465.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093;0.3651" values="#0f172a;#000000;#0a1017"/></rect>
<rect x="490.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116;0.3674" values="#0f172a;#000000;#0b1118"/></rect>
<rect x="515.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1140;0.3698" values="#0f172a;#000000;#0b1118"/></rect>
<rect x="540.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163;0.3721" values="#0f172a;#000000;#0a1017"/></rect>
<rect x="565.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186;0.3744" values="#0f172a;#000000;#090e14"/></rect>
<rect x="590.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209;0.3767" values="#0f172a;#000000;#080c12"/></rect>
<rect x="615.0" y="160.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233;0.3791" values="#0f172a;#000000;#070b0f"/></rect>
<rect x="40.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698;0.3256" values="#0f172a;#221a0e;#221a0e"/></rect>
<rect x="65.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721;0.3279" values="#0f172a;#342715;#342715"/></rect>
<rect x="90.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744;0.3302" values="#0f172a;#564022;#564022"/></rect>
<rect x="115.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767;0.3326" values="#0f172a;#96703c;#96703c"/></rect>
<rect x="140.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791;0.3349" values="#0f172a;#efb35f;#efb35f"/></rect>
<rect x="165.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0814;0.3372" values="#0f172a;#efb35f;#efb35f"/></rect>
<rect x="190.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837;0.3395" values="#0f172a;#96703c;#96703c"/></rect>
<rect x="215.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0860;0.3419" values="#0f172a;#564022;#564022"/></rect>
<rect x="240.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884;0.3442" values="#0f172a;#342715;#342715"/></rect>
<rect x="265.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907;0.3465" values="#0f172a;#221a0e;#221a0e"/></rect>
<rect x="290.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930;0.3488" values="#0f172a;#18120a;#18120a"/></rect>
<rect x="315.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#0f172a;#475569"/></rect>
<rect x="340.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977;0.3535" values="#0f172a;#000000;#06090c"/></rect>
<rect x="365.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.3558" values="#0f172a;#000000;#070b0f"/></rect>
<rect x="390.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023;0.3581" values="#0f172a;#000000;#080d12"/></rect>
<rect x="415.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047;0.3605" values="#0f172a;#000000;#0a1017"/></rect>
<rect x="440.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070;0.3628" values="#0f172a;#000000;#0c131b"/></rect>
<rect x="465.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093;0.3651" values="#0f172a;#000000;#0e1620"/></rect>
<rect x="490.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116;0.3674" values="#0f172a;#000000;#0f1822"/></rect>
<rect x="515.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1140;0.3698" values="#0f172a;#000000;#0f1822"/></rect>
<rect x="540.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163;0.3721" values="#0f172a;#000000;#0e1620"/></rect>
<rect x="565.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186;0.3744" values="#0f172a;#000000;#0c131b"/></rect>
<rect x="590.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209;0.3767" values="#0f172a;#000000;#0a1017"/></rect>
<rect x="615.0" y="185.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233;0.3791" values="#0f172a;#000000;#080d12"/></rect>
<rect x="40.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698;0.3256" values="#0f172a;#20180d;#20180d"/></rect>
<rect x="65.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721;0.3279" values="#0f172a;#2e2312;#2e2312"/></rect>
<rect x="90.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744;0.3302" values="#0f172a;#47351c;#47351c"/></rect>
<rect x="115.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767;0.3326" values="#0f172a;#6d522c;#6d522c"/></rect>
<rect x="140.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791;0.3349" values="#0f172a;#96703c;#96703c"/></rect>
<rect x="165.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0814;0.3372" values="#0f172a;#96703c;#96703c"/></rect>
<rect x="190.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837;0.3395" values="#0f172a;#6d522c;#6d522c"/></rect>
<rect x="215.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0860;0.3419" values="#0f172a;#47351c;#47351c"/></rect>
<rect x="240.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884;0.3442" values="#0f172a;#2e2312;#2e2312"/></rect>
<rect x="265.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907;0.3465" values="#0f172a;#20180d;#20180d"/></rect>
<rect x="290.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930;0.3488" values="#0f172a;#171109;#171109"/></rect>
<rect x="315.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#0f172a;#475569"/></rect>
<rect x="340.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977;0.3535" values="#0f172a;#000000;#060a0e"/></rect>
<rect x="365.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.3558" values="#0f172a;#000000;#080c12"/></rect>
<rect x="390.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023;0.3581" values="#0f172a;#000000;#0a1017"/></rect>
<rect x="415.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047;0.3605" values="#0f172a;#000000;#0d151d"/></rect>
<rect x="440.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070;0.3628" values="#0f172a;#000000;#111a26"/></rect>
<rect x="465.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093;0.3651" values="#0f172a;#000000;#15202e"/></rect>
<rect x="490.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116;0.3674" values="#0f172a;#000000;#172534"/></rect>
<rect x="515.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1140;0.3698" values="#0f172a;#000000;#172534"/></rect>
<rect x="540.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163;0.3721" values="#0f172a;#000000;#15202e"/></rect>
<rect x="565.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186;0.3744" values="#0f172a;#000000;#111a26"/></rect>
<rect x="590.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209;0.3767" values="#0f172a;#000000;#0d151d"/></rect>
<rect x="615.0" y="210.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233;0.3791" values="#0f172a;#000000;#0a1017"/></rect>
<rect x="40.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698;0.3256" values="#0f172a;#1b140b;#1b140b"/></rect>
<rect x="65.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721;0.3279" values="#0f172a;#261c0f;#261c0f"/></rect>
<rect x="90.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744;0.3302" values="#0f172a;#342715;#342715"/></rect>
<rect x="115.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767;0.3326" values="#0f172a;#47351c;#47351c"/></rect>
<rect x="140.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791;0.3349" values="#0f172a;#564022;#564022"/></rect>
<rect x="165.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0814;0.3372" values="#0f172a;#564022;#564022"/></rect>
<rect x="190.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837;0.3395" values="#0f172a;#47351c;#47351c"/></rect>
<rect x="215.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0860;0.3419" values="#0f172a;#342715;#342715"/></rect>
<rect x="240.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884;0.3442" values="#0f172a;#261c0f;#261c0f"/></rect>
<rect x="265.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907;0.3465" values="#0f172a;#1b140b;#1b140b"/></rect>
<rect x="290.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930;0.3488" values="#0f172a;#140f08;#140f08"/></rect>
<rect x="315.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#0f172a;#475569"/></rect>
<rect x="340.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977;0.3535" values="#0f172a;#000000;#070b10"/></rect>
<rect x="365.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.3558" values="#0f172a;#000000;#090e14"/></rect>
<rect x="390.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023;0.3581" values="#0f172a;#000000;#0c131b"/></rect>
<rect x="415.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047;0.3605" values="#0f172a;#000000;#111a26"/></rect>
<rect x="440.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070;0.3628" values="#0f172a;#000000;#172534"/></rect>
<rect x="465.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093;0.3651" values="#0f172a;#000000;#203147"/></rect>
<rect x="490.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116;0.3674" values="#0f172a;#000000;#273c56"/></rect>
<rect x="515.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1140;0.3698" values="#0f172a;#000000;#273c56"/></rect>
<rect x="540.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163;0.3721" values="#0f172a;#000000;#203147"/></rect>
<rect x="565.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186;0.3744" values="#0f172a;#000000;#172534"/></rect>
<rect x="590.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209;0.3767" values="#0f172a;#000000;#111a26"/></rect>
<rect x="615.0" y="235.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233;0.3791" values="#0f172a;#000000;#0c131b"/></rect>
<rect x="40.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698;0.3256" values="#0f172a;#171109;#18130b"/></rect>
<rect x="65.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721;0.3279" values="#0f172a;#1d160c;#1e180e"/></rect>
<rect x="90.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744;0.3302" values="#0f172a;#261c0f;#271e12"/></rect>
<rect x="115.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767;0.3326" values="#0f172a;#2e2312;#302516"/></rect>
<rect x="140.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791;0.3349" values="#0f172a;#342715;#362a19"/></rect>
<rect x="165.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0814;0.3372" values="#0f172a;#342715;#362a19"/></rect>
<rect x="190.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837;0.3395" values="#0f172a;#2e2312;#302617"/></rect>
<rect x="215.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0860;0.3419" values="#0f172a;#261c0f;#261c0f"/></rect>
<rect x="240.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884;0.3442" values="#0f172a;#1d160c;#1d160c"/></rect>
<rect x="265.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907;0.3465" values="#0f172a;#171109;#171109"/></rect>
<rect x="290.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930;0.3488" values="#0f172a;#120d07;#120d07"/></rect>
<rect x="315.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0140" values="#0f172a;#475569"/></rect>
<rect x="340.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977;0.3535" values="#0f172a;#000000;#080c11"/></rect>
<rect x="365.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.3558" values="#0f172a;#000000;#0a1017"/></rect>
<rect x="390.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023;0.3581" values="#0f172a;#000000;#0e1620"/></rect>
<rect x="415.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047;0.3605" values="#0f172a;#000000;#15202e"/></rect>
<rect x="440.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070;0.3628" values="#0f172a;#000000;#203147"/></rect>
<rect x="465.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093;0.3651" values="#0f172a;#000000;#314c6d"/></rect>
<rect x="490.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116;0.3674" values="#0f172a;#000000;#436996"/></rect>
<rect x="515.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1140;0.3698" values="#0f172a;#000000;#436996"/></rect>
<rect x="540.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163;0.3721" values="#0f172a;#000000;#314c6d"/></rect>
<rect x="565.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186;0.3744" values="#0f172a;#000000;#203147"/></rect>
<rect x="590.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209;0.3767" values="#0f172a;#000000;#15202e"/></rect>
<rect x="615.0" y="260.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233;0.3791" values="#0f172a;#000000;#0e1620"/></rect>
<rect x="40.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698;0.3256" values="#0f172a;#120e07;#140f0a"/></rect>
<rect x="65.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721;0.3279" values="#0f172a;#171109;#18130c"/></rect>
<rect x="90.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744;0.3302" values="#0f172a;#1b140b;#1d170e"/></rect>
<rect x="115.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767;0.3326" values="#0f172a;#20180d;#211a10"/></rect>
<rect x="140.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791;0.3349" values="#0f172a;#221a0e;#241c11"/></rect>
<rect x="165.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0814;0.3372" values="#0f172a;#221a0e;#241d12"/></rect>
<rect x="190.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837;0.3395" values="#0f172a;#20180d;#221b12"/></rect>
<rect x="215.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0860;0.3419" values="#0f172a;#1b140b;#1e1911"/></rect>
<rect x="240.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884;0.3442" values="#0f172a;#171109;#1a1610"/></rect>
<rect x="265.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907;0.3465" values="#0f172a;#120e07;#161410"/></rect>
<rect x="290.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930;0.3488" values="#0f172a;#0f0b06;#141311"/></rect>
<rect x="315.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0953;0.3512" values="#0f172a;#0c0905;#121312"/></rect>
<rect x="340.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977;0.3535" values="#0f172a;#000000;#080c12"/></rect>
<rect x="365.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.3558" values="#0f172a;#000000;#0b1118"/></rect>
<rect x="390.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023;0.3581" values="#0f172a;#000000;#0f1822"/></rect>
<rect x="415.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047;0.3605" values="#0f172a;#000000;#172534"/></rect>
<rect x="440.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070;0.3628" values="#0f172a;#000000;#273c56"/></rect>
<rect x="465.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093;0.3651" values="#0f172a;#000000;#436996"/></rect>
<rect x="490.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116;0.3674" values="#0f172a;#000000;#6ba7ef"/></rect>
<rect x="515.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1140;0.3698" values="#0f172a;#000000;#6ba7ef"/></rect>
<rect x="540.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163;0.3721" values="#0f172a;#000000;#436996"/></rect>
<rect x="565.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186;0.3744" values="#0f172a;#000000;#273c56"/></rect>
<rect x="590.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209;0.3767" values="#0f172a;#000000;#172534"/></rect>
<rect x="615.0" y="285.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233;0.3791" values="#0f172a;#000000;#0f1822"/></rect>
<rect x="40.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698;0.3256" values="#0f172a;#0f0b06;#100d08"/></rect>
<rect x="65.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721;0.3279" values="#0f172a;#120d07;#130f0a"/></rect>
<rect x="90.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744;0.3302" values="#0f172a;#140f08;#16110b"/></rect>
<rect x="115.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767;0.3326" values="#0f172a;#171109;#18130c"/></rect>
<rect x="140.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791;0.3349" values="#0f172a;#18120a;#1a150d"/></rect>
<rect x="165.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0814;0.3372" values="#0f172a;#18120a;#1a150e"/></rect>
<rect x="190.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837;0.3395" values="#0f172a;#171109;#19150e"/></rect>
<rect x="215.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0860;0.3419" values="#0f172a;#140f08;#17130e"/></rect>
<rect x="240.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884;0.3442" values="#0f172a;#120d07;#15120e"/></rect>
<rect x="265.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907;0.3465" values="#0f172a;#0f0b06;#13110f"/></rect>
<rect x="290.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930;0.3488" values="#0f172a;#0d0905;#111110"/></rect>
<rect x="315.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0953;0.3512" values="#0f172a;#0b0804;#111112"/></rect>
<rect x="340.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977;0.3535" values="#0f172a;#090704;#111315"/></rect>
<rect x="365.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.3558" values="#0f172a;#000000;#0b1118"/></rect>
<rect x="390.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023;0.3581" values="#0f172a;#000000;#0f1822"/></rect>
<rect x="415.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047;0.3605" values="#0f172a;#000000;#172534"/></rect>
<rect x="440.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070;0.3628" values="#0f172a;#000000;#273c56"/></rect>
<rect x="465.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093;0.3651" values="#0f172a;#000000;#436996"/></rect>
<rect x="490.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116;0.3674" values="#0f172a;#000000;#6ba7ef"/></rect>
<rect x="515.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1140;0.3698" values="#0f172a;#000000;#6ba7ef"/></rect>
<rect x="540.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163;0.3721" values="#0f172a;#000000;#436996"/></rect>
<rect x="565.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186;0.3744" values="#0f172a;#000000;#273c56"/></rect>
<rect x="590.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209;0.3767" values="#0f172a;#000000;#172534"/></rect>
<rect x="615.0" y="310.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233;0.3791" values="#0f172a;#000000;#0f1822"/></rect>
<rect x="40.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698;0.3256" values="#0f172a;#0c0905;#0d0b07"/></rect>
<rect x="65.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721;0.3279" values="#0f172a;#0e0a06;#0f0c08"/></rect>
<rect x="90.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744;0.3302" values="#0f172a;#100c06;#110e09"/></rect>
<rect x="115.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767;0.3326" values="#0f172a;#110d07;#120f0a"/></rect>
<rect x="140.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791;0.3349" values="#0f172a;#120d07;#13100b"/></rect>
<rect x="165.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0814;0.3372" values="#0f172a;#120d07;#14100b"/></rect>
<rect x="190.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837;0.3395" values="#0f172a;#110d07;#13100c"/></rect>
<rect x="215.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0860;0.3419" values="#0f172a;#100c06;#12100c"/></rect>
<rect x="240.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884;0.3442" values="#0f172a;#0e0a06;#110f0d"/></rect>
<rect x="265.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907;0.3465" values="#0f172a;#0c0905;#100f0d"/></rect>
<rect x="290.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930;0.3488" values="#0f172a;#0b0804;#0f0f0f"/></rect>
<rect x="315.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0953;0.3512" values="#0f172a;#090704;#0f1011"/></rect>
<rect x="340.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977;0.3535" values="#0f172a;#080603;#101214"/></rect>
<rect x="365.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.3558" values="#0f172a;#070503;#111519"/></rect>
<rect x="390.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023;0.3581" values="#0f172a;#060402;#141b22"/></rect>
<rect x="415.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047;0.3605" values="#0f172a;#000000;#15202e"/></rect>
<rect x="440.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070;0.3628" values="#0f172a;#000000;#203147"/></rect>
<rect x="465.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093;0.3651" values="#0f172a;#000000;#314c6d"/></rect>
<rect x="490.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116;0.3674" values="#0f172a;#000000;#436996"/></rect>
<rect x="515.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1140;0.3698" values="#0f172a;#000000;#436996"/></rect>
<rect x="540.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163;0.3721" values="#0f172a;#000000;#314c6d"/></rect>
<rect x="565.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186;0.3744" values="#0f172a;#000000;#203147"/></rect>
<rect x="590.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209;0.3767" values="#0f172a;#000000;#15202e"/></rect>
<rect x="615.0" y="335.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233;0.3791" values="#0f172a;#000000;#0e1620"/></rect>
<rect x="40.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698;0.3256" values="#0f172a;#0a0804;#0b0906"/></rect>
<rect x="65.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721;0.3279" values="#0f172a;#0b0804;#0c0a07"/></rect>
<rect x="90.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744;0.3302" values="#0f172a;#0c0905;#0e0b08"/></rect>
<rect x="115.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767;0.3326" values="#0f172a;#0d0a05;#0f0c08"/></rect>
<rect x="140.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791;0.3349" values="#0f172a;#0e0a05;#0f0d09"/></rect>
<rect x="165.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0814;0.3372" values="#0f172a;#0e0a05;#0f0d0a"/></rect>
<rect x="190.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837;0.3395" values="#0f172a;#0d0a05;#0f0d0a"/></rect>
<rect x="215.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0860;0.3419" values="#0f172a;#0c0905;#0f0d0b"/></rect>
<rect x="240.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884;0.3442" values="#0f172a;#0b0804;#0e0d0b"/></rect>
<rect x="265.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907;0.3465" values="#0f172a;#0a0804;#0e0d0c"/></rect>
<rect x="290.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930;0.3488" values="#0f172a;#090704;#0d0e0d"/></rect>
<rect x="315.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0953;0.3512" values="#0f172a;#080603;#0d0f0f"/></rect>
<rect x="340.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977;0.3535" values="#0f172a;#070503;#0e1012"/></rect>
<rect x="365.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.3558" values="#0f172a;#060502;#0f1317"/></rect>
<rect x="390.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023;0.3581" values="#0f172a;#050402;#12171d"/></rect>
<rect x="415.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047;0.3605" values="#0f172a;#050402;#161e27"/></rect>
<rect x="440.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070;0.3628" values="#0f172a;#000000;#172534"/></rect>
<rect x="465.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093;0.3651" values="#0f172a;#000000;#203147"/></rect>
<rect x="490.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116;0.3674" values="#0f172a;#000000;#273c56"/></rect>
<rect x="515.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1140;0.3698" values="#0f172a;#000000;#273c56"/></rect>
<rect x="540.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163;0.3721" values="#0f172a;#000000;#203147"/></rect>
<rect x="565.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186;0.3744" values="#0f172a;#000000;#172534"/></rect>
<rect x="590.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209;0.3767" values="#0f172a;#000000;#111a26"/></rect>
<rect x="615.0" y="360.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233;0.3791" values="#0f172a;#000000;#0c131b"/></rect>
<rect x="40.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0698;0.3256" values="#0f172a;#080603;#090806"/></rect>
<rect x="65.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0721;0.3279" values="#0f172a;#090704;#0a0906"/></rect>
<rect x="90.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0744;0.3302" values="#0f172a;#0a0704;#0b0907"/></rect>
<rect x="115.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0767;0.3326" values="#0f172a;#0a0804;#0c0a07"/></rect>
<rect x="140.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791;0.3349" values="#0f172a;#0b0804;#0c0a08"/></rect>
<rect x="165.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0814;0.3372" values="#0f172a;#0b0804;#0c0b08"/></rect>
<rect x="190.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0837;0.3395" values="#0f172a;#0a0804;#0c0b09"/></rect>
<rect x="215.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0860;0.3419" values="#0f172a;#0a0704;#0c0b09"/></rect>
<rect x="240.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0884;0.3442" values="#0f172a;#090704;#0c0b0a"/></rect>
<rect x="265.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0907;0.3465" values="#0f172a;#080603;#0c0c0b"/></rect>
<rect x="290.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0930;0.3488" values="#0f172a;#080603;#0c0c0c"/></rect>
<rect x="315.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0953;0.3512" values="#0f172a;#070503;#0c0d0e"/></rect>
<rect x="340.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0977;0.3535" values="#0f172a;#060502;#0c0e10"/></rect>
<rect x="365.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1000;0.3558" values="#0f172a;#050402;#0d1014"/></rect>
<rect x="390.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1023;0.3581" values="#0f172a;#050402;#0f1419"/></rect>
<rect x="415.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1047;0.3605" values="#0f172a;#040302;#12181f"/></rect>
<rect x="440.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1070;0.3628" values="#0f172a;#040302;#151d27"/></rect>
<rect x="465.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1093;0.3651" values="#0f172a;#030301;#182330"/></rect>
<rect x="490.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1116;0.3674" values="#0f172a;#000000;#172534"/></rect>
<rect x="515.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1140;0.3698" values="#0f172a;#000000;#172534"/></rect>
<rect x="540.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1163;0.3721" values="#0f172a;#000000;#15202e"/></rect>
<rect x="565.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1186;0.3744" values="#0f172a;#000000;#111a26"/></rect>
<rect x="590.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1209;0.3767" values="#0f172a;#000000;#0d151d"/></rect>
<rect x="615.0" y="385.0" width="25.3" height="25.3" fill="#0f172a"><animate attributeName="fill" dur="21.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1233;0.3791" values="#0f172a;#000000;#0a1017"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0463;0.0465;1.0000" values="0;0;1;1"/><circle cx="165.0" cy="185.0" r="16" fill="#ffbf66" opacity="0.4"/>
<circle cx="165.0" cy="185.0" r="8" fill="#ffbf66" stroke="#ffffff" stroke-width="2.5"/>
<text x="165.0" y="165.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">ライト 1(暖色)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3021;0.3023;1.0000" values="0;0;1;1"/><circle cx="515.0" cy="310.0" r="16" fill="#73b2ff" opacity="0.4"/>
<circle cx="515.0" cy="310.0" r="8" fill="#73b2ff" stroke="#ffffff" stroke-width="2.5"/>
<text x="515.0" y="290.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#ffffff">ライト 2(寒色)</text>
</g>
<text x="327.5" y="301.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#475569">壁(光を遮る)</text>
<rect x="680" y="96" width="250" height="330" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="680" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② かかった計算</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="0;0;1;1"/><text x="694" y="140" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">ライト 1</text>
<text x="694" y="164" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">281 マスで 1 回ずつ計算</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3254;0.3256;1.0000" values="0;0;1;1"/><text x="694" y="210" text-anchor="start" style="font-size:16px;font-weight:700;fill:#7c3aed">ライト 2</text>
<text x="694" y="234" text-anchor="start" style="font-size:13px;font-weight:500;fill:#1f2937">281 マスで 1 回ずつ計算</text>
</g>
<text x="694" y="300" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">計算した回数:</text>
<text x="694" y="332" text-anchor="start" style="font-size:30px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1254;0.1256;1.0000" values="1;1;0;0"/></text>
<text x="694" y="332" text-anchor="start" style="font-size:30px;font-weight:700;fill:#7c3aed" opacity="0">281<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1254;0.1256;0.3812;0.3814;1.0000" values="0;0;1;1;0;0"/></text>
<text x="694" y="332" text-anchor="start" style="font-size:30px;font-weight:700;fill:#7c3aed" opacity="0">562<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3812;0.3814;1.0000" values="0;0;1;1"/></text>
<text x="694" y="372" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">実際の格子 160×90×64 なら</text>
<text x="694" y="392" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">921,600 マス × ライト数</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6091;0.6093;1.0000" values="0;0;1;1"/><rect x="30" y="440" width="900" height="74" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="46" y="464" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e3a8a">格子に書き込むのは、ライトごとに 921,600 マス(ライト 100 個なら 92,160,000 回)</text>
<text x="46" y="488" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">画素ごとに霧の中を進んで、ライトを足す方法なら、画素 2,073,600 × 歩数 64 × ライト数 になる</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">霧の中の各点に、どの色の光が、どれだけ届いているかを、先に調べて貯めておく<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ライト 1: 距離で弱まり、壁の向こうには届かない<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.3254;0.3256;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ライト 2: 足し合わせると、2 色が混ざる所もできる<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3254;0.3256;0.6091;0.6093;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">画面の画素には、関係しない計算量。ライトが増えても、格子の数だけ増える<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.6091;0.6093;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:light-injection:end -->

## ② 光の注入
<strong>各 froxel が受けている光を計算します</strong>。<strong>太陽光とローカル ライト（点光源・スポットライト）</strong>が<strong>対象</strong>です。

<div class="formula">散乱光 = 密度 × アルベド × Σ ( 光の色 × 影 × 位相関数(θ) )</div>

```hlsl
float3 inscattered = 0;

float shadow = SampleCascadeShadow(world_position);
float phase = HenyeyGreenstein(dot(view_dir, -sun_direction), g);
inscattered += sun_color * shadow * phase;

for (uint i = 0; i < light_count; ++i) {
  float3 to_light = lights[i].position - world_position;
  float distance_to_light = length(to_light);
  float3 light_dir = to_light / distance_to_light;
  float attenuation = LightAttenuation(lights[i], distance_to_light);
  float light_shadow = SampleLocalShadow(lights[i], world_position);
  float p = HenyeyGreenstein(dot(view_dir, -light_dir), g);
  inscattered += lights[i].color * attenuation * light_shadow * p;
}

inscattered += ambient_fog_color;
float3 scattering = inscattered * density * albedo;
```

| 点 | 説明 |
| --- | --- |
| シャドウ マップを引く | 影の中の霧は光らない。この結果、物の影が光の筋として見える |
| 位相関数 | <strong>前方に強く散る（g ≈ 0.6〜0.8）</strong>。太陽の方を見ると霧が明るい（[Atmospheric Scattering](../scattering/index.md)） |
| 環境光 | 全体にうっすら足す（暗すぎる霧の防止） |
| ライトの数が多い場合 | froxel ごとにライトをカリング（[Tiled と Clustered](../../../rendering/light-culling.md)） |
| 解像度が低くても綺麗 | 霧は低周波（細かい構造がない）ので低解像度で十分 |

## ステップ 2：ライトの光を、注入する

<strong>密度</strong>（[Step 1: Density](density.md)）が、決まったら <strong>各セルに</strong>、ライトの光を散乱光として書き込みます（注入）。そのセルの霧がライトに照らされて、どれだけ光るかを計算します。

## セルでの光の計算

<strong>ライト 1 つ</strong>について <strong>そのセルで、カメラの方向へ散乱される光</strong>は、次のとおりです。

```text
散乱光 = 散乱係数 × 位相関数 × ライトの強さ × 影（光が、届くか） × 減衰（距離）
```

| 項 | 内容 |
| --- | --- |
| 散乱係数（`σ_s`） | セルの、密度（霧が濃いほどよく光る） |
| 位相関数 | ライトの向きと、カメラへの向きの角度に依存（[Phase Functions](../scattering/phase-function.md)） |
| ライトの強さ | 太陽、点光源の明るさ |
| 影 | シャドウ マップで光が、届くか |
| 減衰 | 点光源の距離による、減衰 |

## 太陽（平行光）を注入する

```hlsl
// 計算シェーダー: 各セルに、太陽の光の、散乱を、足す。
[numthreads(8, 8, 4)]
void InjectSunCS(uint3 id : SV_DispatchThreadID) {
  float4 cell = g_froxel_scatter[id];                                      // 密度のステップで書いた値
  float3 scattering = cell.xyz;                                            // 散乱係数（RGB）
  if (cell.w < 1e-6) return;                                               // 霧が、無いセルは、スキップ

  float3 world = FroxelToWorld(float3(id) + JitterOffset());
  float3 view_dir = normalize(world - g_camera_position);                  // カメラから、セルへ向かう向き
```

<strong>霧がない</strong>セル（密度 0）は、<strong>光らない</strong>のでスキップします。カメラからセルへの向きが位相関数に、必要です。

```hlsl
  // 太陽の光が、このセルに、届くか。シャドウ マップ（カスケード）を、1 回引く。雲の影も、掛ける。
  float shadow = SampleCascadedShadow(world) * CloudShadow(world);

  // 位相関数: 太陽の光が、カメラの方向へ、散る割合。霧は、前方に、やや強く、散る。
  float phase = HenyeyGreenstein(dot(view_dir, g_sun_dir), g_phase_g);

  float3 sun_scatter = scattering * g_sun_color * shadow * phase;
  g_froxel_scatter[id] = float4(cell.xyz, cell.w);                          // 密度は、そのまま
  g_froxel_lighting[id] += float4(sun_scatter, 0);                          // 散乱光を、別のテクスチャに、足す
}
```

<strong>シャドウ マップ</strong>（[CSM](../../shadows/cascaded.md)）を、<strong>セルごとに 1 回</strong>、引きます。影の中のセルは光らず光が届くセルだけが、散乱光を持ちます。これが光の筋（ゴッド レイ）の、源です（[Volume-Based God Rays](../god-rays/volume.md)）。

## 点光源・スポットライトを、注入する

<strong>ライトの周りの霧</strong>は <strong>光の玉</strong>になります。セルごとに影響するライトを探して、足し合わせます。

```hlsl
// 点光源: セルから、ライトへの距離で、減衰させ、位相関数と、影（ライトの、シャドウ マップ）を、掛ける。
float3 InjectPointLight(Light light, float3 world, float3 view_dir, float3 scattering) {
  float3 to_light = light.position - world;
  float dist = length(to_light);
  if (dist > light.range) return 0.0;                                       // 範囲外
  float3 light_dir = to_light / dist;

  float attenuation = saturate(1.0 - pow(dist / light.range, 4.0));        // 距離による、減衰（窓関数）
  attenuation *= attenuation / (dist * dist + 1.0);                         // 逆二乗の、減衰
  float shadow = (light.shadow_slot >= 0) ? SamplePointShadow(light, world) : 1.0;
  float phase = HenyeyGreenstein(dot(view_dir, -light_dir), g_phase_g);

  return scattering * light.color * light.intensity * attenuation * shadow * phase;
}
```

<strong>光源からの距離</strong>の<strong>2 乗に、反比例</strong>して暗くなる逆二乗の法則と、範囲での打ち切り（窓関数）を、組み合わせます。影つきのライトはライトのシャドウ マップ（[Point Lights: Cube Maps](../../shadows/local-lights/point-cubemap.md)）を、セルごとに引きます。

```hlsl
// ライトが、多いとき: クラスターごとの、ライトのリストを、使い、そのセルに影響する、ライトだけを、ループする。
uint cluster = ClusterIndexAt(world);
uint count = g_cluster_light_count[cluster];
float3 total = 0.0;
for (uint i = 0; i < count; ++i) {
  Light light = g_lights[g_cluster_light_indices[cluster * kMaxLightsPerCluster + i]];
  total += InjectPointLight(light, world, view_dir, scattering);
}
```

<strong>ライトが数百個</strong>ある場合、<strong>全ライト</strong>を全セルでループすると非常に、重いです。クラスター（空間を小さな領域に分け、各領域に影響するライトのリストを、持つ）を使います（[Shadows for Many Lights](../../shadows/local-lights/many-lights.md)）。

## 環境光（空の光）を足す

<strong>ライトが無い</strong>場所でも <strong>霧は、空の光</strong>でぼんやりと明るいものです。環境光を一様に足します。

```hlsl
float3 ambient_scatter = scattering * g_ambient_color * g_ambient_strength;     // 空の光が、霧を、全方向から、照らす
```

<strong>霧の中の日陰が真っ黒にならない</strong>ための、<strong>重要な項</strong>です。空の色（青い）が霧の日陰の色です（[Using the Sky for Lighting](../sky-models/sky-lighting.md)）。

## 結果

注入が終わると <strong>3D テクスチャの、各セル</strong>に <strong>そのセルの散乱光</strong>（RGB）と、消散係数（A）が入っています。次の段階（[Steps 3 and 4: Integration and Application](integration.md)）で、奥行き方向に積分します。

## よくあるミス

??? failure "光の筋が出ない"
    <strong>シャドウ マップを参照</strong>する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] セルごとに、ライトと影を計算

## 参考

- Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games
- Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games
- Olsson, Billeter, Assarsson, "Clustered Deferred and Forward Shading", High-Performance Graphics 2012
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）

## 関連ページ

- [Volumetric Fog](index.md)
- [Step 1: Density](density.md)
- [Steps 3 and 4: Integration and Application](integration.md)
