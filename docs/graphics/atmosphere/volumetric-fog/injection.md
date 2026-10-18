---
title: Step 2: Light Injection
tags:
  - 描画
---

# Step 2: Light Injection

**各 froxel に、太陽やライトの光を計算して、足します**。**シャドウ マップを参照**して、**影の中は光を入れない**ので、**光の筋ができます**。このページでは、**光の注入**を説明します。

!!! tip "ポイント"
    - **各セルで、ライトの光 × 位相関数 × 影**。
    - **太陽・点光源・スポットライトのすべてに対応**。
    - **シャドウ マップを参照**して、**光の筋**を作る。
    - **ライトの数が多いと、重い**（クラスタ化で軽く）。

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

## ② Light Injection {#②-光の注入}
**各 froxel が受けている光を計算します**。<strong>太陽光とローカル ライト（点光源・スポットライト）</strong>が**対象**です。

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
| **シャドウ マップを引く** | **影の中の霧は光らない**。**この結果、物の影が光の筋として見える** |
| **位相関数** | <strong>前方に強く散る（g ≈ 0.6〜0.8）</strong>。**太陽の方を見ると霧が明るい**（[大気散乱](../scattering/index.md)） |
| **環境光** | **全体にうっすら足す**（暗すぎる霧の防止） |
| **ライトの数が多い場合** | **froxel ごとにライトをカリング**（[ライト カリング](../../../rendering/light-culling.md)） |
| **解像度が低くても綺麗** | **霧は低周波**（細かい構造がない）ので低解像度で十分 |

## Common Mistakes {#よくあるミス}

??? failure "光の筋が出ない"
    **シャドウ マップを参照**する。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **セルごとに、ライトと影を計算**

## References {#参考}

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## Related Pages {#関連ページ}

- [Volumetric Fog](index.md)
- [密度](density.md)
- [積分](integration.md)
