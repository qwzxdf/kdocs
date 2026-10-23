---
title: Forward と Deferred
tags:
  - 最適化
  - 3Dゲーム
---

# Forward と Deferred

**ライティング**（光の計算）を、どの順番で行うかで描画の重さの構造が大きく変わります。多くのエンジンは、最初は Forward（物体を描くたびに光も計算）で、ライトが増えると、Deferred（形を先に描き、光をあとでまとめて計算）に移ります。このページは、Forward の何が重いのか、Deferred で何が改善するのか、その代償を目的から説明します。

!!! tip "ポイント"
    - <strong>Forward</strong>：<strong>物体を描きながら、ピクセルごとに全ライトを計算</strong>。コスト ≒ 物体のピクセル（オーバードロー込み）× ライトの数。
    - 問題：あとで隠れるピクセルにも、重いライティングをする（無駄）。ライトが多いとピクセルシェーダーが爆発。
    - Deferred：① G-Buffer に、形・材質の情報だけ書く　② 画面の、各ピクセルで、1 回だけ、ライティング。コスト ≒ 画面のピクセル × ライト。
    - 改善：「物体の数」と「ライトの数」が、掛け算でなく、足し算に。オーバードローのライティングが消える。
    - 代償：G-Buffer の帯域（書き込み・読み込み）。MSAA・半透明・材質の多様性が難しい。
    - ライトごとにフルスクリーンで読むのは、帯域が重い。→ Tiled / Clustered へ（[Tiled と Clustered](light-culling.md)）。

## 動きで比べる

**同じ画面（28×16 マス）・同じ球体 10 個・同じ色付きのライト 5 個**を、Forward と Deferred で描く様子です。ライトが球体に当たると、ライトの色が付きます（近いライトほど濃く）。最後の絵は同じですが、計算の回数が違います。

<!-- fig:forward-deferred:begin -->
<svg class="fig illust motion" data-fig="forward-vs-deferred" viewBox="0 0 960 540" role="img" data-still="11.5"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<line x1="480" y1="16" x2="480" y2="524" stroke="#cbd5e1" stroke-width="2"/>
<text x="32" y="32" text-anchor="start" style="font-size:26px;font-weight:700;fill:#2563eb">Forward</text>
<text x="512" y="32" text-anchor="start" style="font-size:26px;font-weight:700;fill:#7c3aed">Deferred</text>
<text x="182" y="32" text-anchor="start" style="font-size:15px;font-weight:500;fill:#64748b">物体ごとに光を計算</text>
<text x="682" y="32" text-anchor="start" style="font-size:15px;font-weight:500;fill:#64748b">まず絵を貯めて、あとで光を計算</text>
<defs><radialGradient id="fd-sphere" cx="0.5" cy="0.5" r="0.5" fx="0.36" fy="0.3"><stop offset="0" stop-color="#ffffff" stop-opacity="0.5"/>
<stop offset="0.45" stop-color="#ffffff" stop-opacity="0"/>
<stop offset="0.8" stop-color="#000000" stop-opacity="0.08"/>
<stop offset="1" stop-color="#000000" stop-opacity="0.4"/>
</radialGradient>
<clipPath id="fd-clip-f"><rect x="32" y="50" width="416.0" height="237.71"/>
</clipPath>
<clipPath id="fd-clip-d"><rect x="512" y="50" width="416.0" height="237.71"/>
</clipPath>
<clipPath id="fd-sph-F0"><circle cx="106.29" cy="106.46" r="52.0"/>
</clipPath>
<clipPath id="fd-sph-F1"><circle cx="136.0" cy="121.31" r="49.03"/>
</clipPath>
<clipPath id="fd-sph-F2"><circle cx="358.86" cy="103.49" r="52.0"/>
</clipPath>
<clipPath id="fd-sph-F3"><circle cx="388.57" cy="118.34" r="46.06"/>
</clipPath>
<clipPath id="fd-sph-F4"><circle cx="217.71" cy="159.94" r="53.49"/>
</clipPath>
<clipPath id="fd-sph-F5"><circle cx="254.86" cy="168.86" r="49.03"/>
</clipPath>
<clipPath id="fd-sph-F6"><circle cx="115.2" cy="228.29" r="49.03"/>
</clipPath>
<clipPath id="fd-sph-F7"><circle cx="144.91" cy="204.51" r="46.06"/>
</clipPath>
<clipPath id="fd-sph-F8"><circle cx="373.71" cy="228.29" r="52.0"/>
</clipPath>
<clipPath id="fd-sph-F9"><circle cx="344.0" cy="201.54" r="46.06"/>
</clipPath>
<clipPath id="fd-sph-D0"><circle cx="586.29" cy="106.46" r="52.0"/>
</clipPath>
<clipPath id="fd-sph-D1"><circle cx="616.0" cy="121.31" r="49.03"/>
</clipPath>
<clipPath id="fd-sph-D2"><circle cx="838.86" cy="103.49" r="52.0"/>
</clipPath>
<clipPath id="fd-sph-D3"><circle cx="868.57" cy="118.34" r="46.06"/>
</clipPath>
<clipPath id="fd-sph-D4"><circle cx="697.71" cy="159.94" r="53.49"/>
</clipPath>
<clipPath id="fd-sph-D5"><circle cx="734.86" cy="168.86" r="49.03"/>
</clipPath>
<clipPath id="fd-sph-D6"><circle cx="595.2" cy="228.29" r="49.03"/>
</clipPath>
<clipPath id="fd-sph-D7"><circle cx="624.91" cy="204.51" r="46.06"/>
</clipPath>
<clipPath id="fd-sph-D8"><circle cx="853.71" cy="228.29" r="52.0"/>
</clipPath>
<clipPath id="fd-sph-D9"><circle cx="824.0" cy="201.54" r="46.06"/>
</clipPath>
</defs>
<rect x="32" y="50" width="416.0" height="237.71" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="512" y="50" width="416.0" height="237.71" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<g clip-path="url(#fd-clip-f)"><g clip-path="url(#fd-sph-F0)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0293;0.0296;1.0000" values="0;0;1;1"/><rect x="91.43" y="50.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0402;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff525d;#ff525d;#ff525d;#ff525d;#ff525d"/></rect>
<rect x="106.29" y="50.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0406;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff606a;#ff606a;#ff606a;#ff606a;#ff606a"/></rect>
<rect x="61.71" y="64.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0396;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff4753;#ff4753;#ff4753;#ff4753;#ff4753"/></rect>
<rect x="76.57" y="64.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0393;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff4753;#ff4753;#ff4753;#ff4753;#ff4753"/></rect>
<rect x="91.43" y="64.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0396;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff4753;#ff4753;#ff4753;#ff4753;#ff4753"/></rect>
<rect x="106.29" y="64.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0401;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff515c;#ff515c;#ff515c;#ff515c;#ff515c"/></rect>
<rect x="121.14" y="64.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0408;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff6770;#ff6770;#ff6770;#ff6770;#ff6770"/></rect>
<rect x="136.0" y="64.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0414;0.0556;0.0657;0.0763;0.0867" values="#ffffff;#ff7e86;#ff7e86;#f87d83;#f87d83;#f87d83"/></rect>
<rect x="61.71" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0392;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff4753;#ff4753;#ff4753;#ff4753;#ff4753"/></rect>
<rect x="76.57" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0386;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff4753;#ff4753;#ff4753;#ff4753;#ff4753"/></rect>
<rect x="91.43" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0392;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff4753;#ff4753;#ff4753;#ff4753;#ff4753"/></rect>
<rect x="106.29" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0399;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff4a55;#ff4a55;#ff4a55;#ff4a55;#ff4a55"/></rect>
<rect x="121.14" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0406;0.0556;0.0658;0.0763;0.0867" values="#ffffff;#ff626c;#ff626c;#fb626a;#fb626a;#fb626a"/></rect>
<rect x="136.0" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0413;0.0556;0.0653;0.0763;0.0867" values="#ffffff;#ff7a82;#ff7a82;#e77979;#e77979;#e77979"/></rect>
<rect x="61.71" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0395;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff4753;#ff4753;#ff4753;#ff4753;#ff4753"/></rect>
<rect x="76.57" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0391;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff4753;#ff4753;#ff4753;#ff4753;#ff4753"/></rect>
<rect x="91.43" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0395;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff4753;#ff4753;#ff4753;#ff4753;#ff4753"/></rect>
<rect x="106.29" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0401;0.0556;0.0659;0.0763;0.0867" values="#ffffff;#ff4e59;#ff4e59;#ff4e59;#ff4e59;#ff4e59"/></rect>
<rect x="121.14" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0407;0.0556;0.0654;0.0763;0.0867" values="#ffffff;#ff656f;#ff656f;#ec6468;#ec6468;#ec6468"/></rect>
<rect x="136.0" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0414;0.0556;0.0648;0.0763;0.0867" values="#ffffff;#ff7c85;#ff7c85;#d77a75;#d77a75;#d77a75"/></rect>
<rect x="61.71" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0400;0.0556;0.0659;0.0760;0.0867" values="#ffffff;#ff4d58;#ff4d58;#ff4d58;#f44b58;#f44b58"/></rect>
<rect x="76.57" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0398;0.0556;0.0659;0.0758;0.0867" values="#ffffff;#ff4753;#ff4753;#ff4753;#f04553;#f04553"/></rect>
<rect x="91.43" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0400;0.0556;0.0659;0.0758;0.0867" values="#ffffff;#ff4d58;#ff4d58;#ff4d58;#ee4a58;#ee4a58"/></rect>
<rect x="106.29" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0404;0.0556;0.0657;0.0758;0.0867" values="#ffffff;#ff5c66;#ff5c66;#f85b64;#e85864;#e85864"/></rect>
<rect x="121.14" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0410;0.0556;0.0651;0.0760;0.0867" values="#ffffff;#ff6f78;#ff6f78;#e06d6d;#d66a6d;#d66a6d"/></rect>
<rect x="136.0" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0416;0.0556;0.0645;0.0761;0.0867" values="#ffffff;#ff848c;#ff848c;#c98175;#c57f75;#c57f75"/></rect>
<rect x="61.71" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0407;0.0556;0.0659;0.0753;0.0867" values="#ffffff;#ff636d;#ff636d;#ff636d;#dc5b6d;#dc5b6d"/></rect>
<rect x="76.57" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0405;0.0556;0.0659;0.0752;0.0867" values="#ffffff;#ff5f69;#ff5f69;#ff5f69;#d85669;#d85669"/></rect>
<rect x="91.43" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0407;0.0556;0.0659;0.0751;0.0867" values="#ffffff;#ff636d;#ff636d;#ff636d;#d6596d;#d6596d"/></rect>
<rect x="106.29" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0410;0.0556;0.0655;0.0751;0.0867" values="#ffffff;#ff6e77;#ff6e77;#ef6d71;#ca6371;#ca6371"/></rect>
<rect x="121.14" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0414;0.0556;0.0648;0.0753;0.0867" values="#ffffff;#ff7e86;#ff7e86;#d67c76;#b97176;#b97176"/></rect>
<rect x="136.0" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0420;0.0556;0.0642;0.0755;0.0867" values="#ffffff;#ff9197;#ff9197;#be8c7a;#a9837a;#a9837a"/></rect>
<rect x="76.57" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0412;0.0556;0.0659;0.0745;0.0867" values="#ffffff;#ff7780;#ff7780;#ff7780;#c06580;#c06580"/></rect>
<rect x="91.43" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0413;0.0556;0.0659;0.0744;0.0867" values="#ffffff;#ff7a82;#ff7a82;#ff7a82;#be6782;#be6782"/></rect>
<rect x="106.29" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0416;0.0556;0.0653;0.0744;0.0867" values="#ffffff;#ff838b;#ff838b;#e98281;#af6d81;#af6d81"/></rect>
<rect x="121.14" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0420;0.0556;0.0646;0.0746;0.0867" values="#ffffff;#ff9097;#ff9097;#d08d81;#a07981;#a07981"/></rect>
</g>
</g>
<circle cx="106.29" cy="106.46" r="52.0" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0293;0.0296;1.0000" values="0;0;1;1"/></circle>
<circle cx="106.29" cy="106.46" r="52.0" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0901;0.0904;1.0000" values="0;0;1;1"/></circle>
<circle cx="106.29" cy="106.46" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0293;0.0296;1.0000" values="0;0;1;1"/></circle>
<text x="106.29" y="111.46" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0293;0.0296;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><g clip-path="url(#fd-sph-F1)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;1.0000" values="0;0;1;1"/><rect x="106.29" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1066;0.1222;0.1326;0.1430;0.1533" values="#ffffff;#ff4a55;#ff4a55;#ff4a55;#ff4a55;#ff4a55"/></rect>
<rect x="121.14" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1073;0.1222;0.1325;0.1430;0.1533" values="#ffffff;#ff626c;#ff626c;#fb626a;#fb626a;#fb626a"/></rect>
<rect x="136.0" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1080;0.1222;0.1319;0.1430;0.1533" values="#ffffff;#ff7a82;#ff7a82;#e77979;#e77979;#e77979"/></rect>
<rect x="150.86" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1087;0.1222;0.1314;0.1430;0.1533" values="#ffffff;#ff9299;#ff9299;#d48f85;#d48f85;#d48f85"/></rect>
<rect x="91.43" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1061;0.1222;0.1326;0.1430;0.1533" values="#ffffff;#ff4753;#ff4753;#ff4753;#ff4753;#ff4753"/></rect>
<rect x="106.29" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1067;0.1222;0.1326;0.1430;0.1533" values="#ffffff;#ff4e59;#ff4e59;#ff4e59;#ff4e59;#ff4e59"/></rect>
<rect x="121.14" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1074;0.1222;0.1321;0.1430;0.1533" values="#ffffff;#ff656f;#ff656f;#ec6468;#ec6468;#ec6468"/></rect>
<rect x="136.0" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1081;0.1222;0.1315;0.1430;0.1533" values="#ffffff;#ff7c85;#ff7c85;#d77a75;#d77a75;#d77a75"/></rect>
<rect x="150.86" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1087;0.1222;0.1309;0.1430;0.1533" values="#ffffff;#ff949b;#ff949b;#c2907f;#c2907f;#c2907f"/></rect>
<rect x="165.71" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1094;0.1222;0.1304;0.1430;0.1533" values="#ffffff;#ffacb1;#ffacb1;#afa687;#afa687;#afa687"/></rect>
<rect x="91.43" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1067;0.1222;0.1326;0.1425;0.1533" values="#ffffff;#ff4d58;#ff4d58;#ff4d58;#ee4a58;#ee4a58"/></rect>
<rect x="106.29" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1071;0.1222;0.1324;0.1425;0.1533" values="#ffffff;#ff5c66;#ff5c66;#f85b64;#e85864;#e85864"/></rect>
<rect x="121.14" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1077;0.1222;0.1317;0.1426;0.1533" values="#ffffff;#ff6f78;#ff6f78;#e06d6d;#d66a6d;#d66a6d"/></rect>
<rect x="136.0" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1083;0.1222;0.1311;0.1428;0.1533" values="#ffffff;#ff848c;#ff848c;#c98175;#c57f75;#c57f75"/></rect>
<rect x="150.86" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1089;0.1222;0.1305;0.1430;0.1533" values="#ffffff;#ff9ba1;#ff9ba1;#b3957c;#b3957c;#b3957c"/></rect>
<rect x="165.71" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1096;0.1222;0.1299;0.1430;0.1533" values="#ffffff;#ffb1b6;#ffb1b6;#9ea981;#9ea981;#9ea981"/></rect>
<rect x="91.43" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1073;0.1222;0.1326;0.1418;0.1533" values="#ffffff;#ff636d;#ff636d;#ff636d;#d6596d;#d6596d"/></rect>
<rect x="106.29" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1076;0.1222;0.1322;0.1418;0.1533" values="#ffffff;#ff6e77;#ff6e77;#ef6d71;#ca6371;#ca6371"/></rect>
<rect x="121.14" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1081;0.1222;0.1315;0.1419;0.1533" values="#ffffff;#ff7e86;#ff7e86;#d67c76;#b97176;#b97176"/></rect>
<rect x="136.0" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1086;0.1222;0.1308;0.1421;0.1533" values="#ffffff;#ff9197;#ff9197;#be8c7a;#a9837a;#a9837a"/></rect>
<rect x="150.86" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1092;0.1222;0.1302;0.1424;0.1533" values="#ffffff;#ffa5aa;#ffa5aa;#a79e7d;#9b977d;#9b977d"/></rect>
<rect x="165.71" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1099;0.1222;0.1296;0.1428;0.1533" values="#ffffff;#ffbabf;#ffbabf;#90b17f;#8cae7f;#8cae7f"/></rect>
<rect x="91.43" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1080;0.1222;0.1326;0.1411;0.1533" values="#ffffff;#ff7a82;#ff7a82;#ff7a82;#be6782;#be6782"/></rect>
<rect x="106.29" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1082;0.1222;0.1320;0.1411;0.1533" values="#ffffff;#ff838b;#ff838b;#e98281;#af6d81;#af6d81"/></rect>
<rect x="121.14" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1086;0.1222;0.1313;0.1413;0.1533" values="#ffffff;#ff9097;#ff9097;#d08d81;#a07981;#a07981"/></rect>
<rect x="136.0" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1091;0.1222;0.1306;0.1415;0.1533" values="#ffffff;#ffa0a6;#ffa0a6;#b79b82;#938882;#938882"/></rect>
<rect x="150.86" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1096;0.1222;0.1299;0.1418;0.1533" values="#ffffff;#ffb2b7;#ffb2b7;#9eaa82;#859a82;#859a82"/></rect>
<rect x="165.71" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1102;0.1222;0.1293;0.1422;0.1533" values="#ffffff;#ffc6ca;#ffc6ca;#85bb80;#78af80;#78af80"/></rect>
<rect x="106.29" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1089;0.1222;0.1319;0.1404;0.1533" values="#ffffff;#ff999f;#ff999f;#e69793;#977793;#977793"/></rect>
<rect x="121.14" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1092;0.1222;0.1312;0.1406;0.1533" values="#ffffff;#ffa4a9;#ffa4a9;#cca090;#8b8090;#8b8090"/></rect>
<rect x="136.0" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1096;0.1222;0.1305;0.1409;0.1533" values="#ffffff;#ffb2b7;#ffb2b7;#b3ac8d;#808d8d;#808d8d"/></rect>
<rect x="150.86" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1101;0.1222;0.1298;0.1412;0.1533" values="#ffffff;#ffc2c6;#ffc2c6;#99b989;#759e89;#759e89"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;0.1612;0.1615;1.0000" values="0;0;1;1;0;0"/><rect x="106.29" y="79.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="121.14" y="79.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="136.0" y="79.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="91.43" y="94.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="106.29" y="94.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="121.14" y="94.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="136.0" y="94.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="91.43" y="109.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="106.29" y="109.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="121.14" y="109.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="136.0" y="109.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="91.43" y="124.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="106.29" y="124.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="121.14" y="124.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="136.0" y="124.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="91.43" y="139.14" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="106.29" y="139.14" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="121.14" y="139.14" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
</g>
</g>
</g>
<circle cx="136.0" cy="121.31" r="49.03" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;1.0000" values="0;0;1;1"/></circle>
<circle cx="136.0" cy="121.31" r="49.03" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1567;0.1570;1.0000" values="0;0;1;1"/></circle>
<circle cx="136.0" cy="121.31" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;1.0000" values="0;0;1;1"/></circle>
<text x="136.0" y="126.31" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><g clip-path="url(#fd-sph-F2)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1627;0.1630;1.0000" values="0;0;1;1"/><rect x="329.14" y="50.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1851;0.1993;0.2096;0.2200" values="#ffffff;#ffffff;#ffde6b;#ffde6b;#ffde6b;#ffde6b"/></rect>
<rect x="344.0" y="50.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1845;0.1993;0.2096;0.2200" values="#ffffff;#ffffff;#ffd953;#ffd953;#ffd953;#ffd953"/></rect>
<rect x="358.86" y="50.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1839;0.1993;0.2096;0.2200" values="#ffffff;#ffffff;#ffd43f;#ffd43f;#ffd43f;#ffd43f"/></rect>
<rect x="373.71" y="50.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1835;0.1993;0.2096;0.2200" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="314.29" y="64.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1855;0.1986;0.2096;0.2200" values="#ffffff;#ffffff;#ffe27d;#e7e074;#e7e074;#e7e074"/></rect>
<rect x="329.14" y="64.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1848;0.1991;0.2096;0.2200" values="#ffffff;#ffffff;#ffdc62;#f8db60;#f8db60;#f8db60"/></rect>
<rect x="344.0" y="64.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1842;0.1993;0.2096;0.2200" values="#ffffff;#ffffff;#ffd648;#ffd648;#ffd648;#ffd648"/></rect>
<rect x="358.86" y="64.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1835;0.1993;0.2096;0.2200" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="373.71" y="64.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1829;0.1993;0.2096;0.2200" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="388.57" y="64.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1828;0.1993;0.2096;0.2200" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="314.29" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1855;0.1981;0.2096;0.2200" values="#ffffff;#ffffff;#ffe27b;#d4dd6b;#d4dd6b;#d4dd6b"/></rect>
<rect x="329.14" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1848;0.1986;0.2096;0.2200" values="#ffffff;#ffffff;#ffdc60;#e7d959;#e7d959;#e7d959"/></rect>
<rect x="344.0" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1841;0.1991;0.2096;0.2200" values="#ffffff;#ffffff;#ffd645;#fbd544;#fbd544;#fbd544"/></rect>
<rect x="358.86" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1834;0.1993;0.2096;0.2200" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="373.71" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1827;0.1993;0.2096;0.2200" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="388.57" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1825;0.1993;0.2096;0.2200" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="314.29" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1856;0.1976;0.2096;0.2200" values="#ffffff;#ffffff;#ffe380;#c2dc68;#c2dc68;#c2dc68"/></rect>
<rect x="329.14" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1849;0.1982;0.2096;0.2200" values="#ffffff;#ffffff;#ffdd65;#d7d959;#d7d959;#d7d959"/></rect>
<rect x="344.0" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1843;0.1987;0.2096;0.2200" values="#ffffff;#ffffff;#ffd74c;#ecd548;#ecd548;#ecd548"/></rect>
<rect x="358.86" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1837;0.1993;0.2096;0.2200" values="#ffffff;#ffffff;#ffd235;#ffd235;#ffd235;#ffd235"/></rect>
<rect x="373.71" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1832;0.1993;0.2096;0.2200" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="388.57" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1831;0.1993;0.2096;0.2200" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="314.29" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1858;0.1972;0.2096;0.2200" values="#ffffff;#ffffff;#ffe589;#b3dd6a;#b3dd6a;#b3dd6a"/></rect>
<rect x="329.14" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1852;0.1978;0.2096;0.2198" values="#ffffff;#ffffff;#ffdf71;#c9da5f;#c9da5f;#c8d65f"/></rect>
<rect x="344.0" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1847;0.1984;0.2096;0.2197" values="#ffffff;#ffffff;#ffdb5b;#e0d752;#e0d752;#dece52"/></rect>
<rect x="358.86" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1842;0.1991;0.2096;0.2195" values="#ffffff;#ffffff;#ffd648;#f8d646;#f8d646;#f4c946"/></rect>
<rect x="373.71" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1838;0.1993;0.2096;0.2195" values="#ffffff;#ffffff;#ffd43c;#ffd43c;#ffd43c;#fbc63c"/></rect>
<rect x="388.57" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1838;0.1993;0.2096;0.2196" values="#ffffff;#ffffff;#ffd33a;#ffd33a;#ffd33a;#fbc73a"/></rect>
<rect x="314.29" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1862;0.1968;0.2096;0.2195" values="#ffffff;#ffffff;#ffe897;#a7de6f;#a7de6f;#a4cf6f"/></rect>
<rect x="329.14" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1856;0.1975;0.2096;0.2192" values="#ffffff;#ffffff;#ffe381;#bedc68;#bedc68;#b9c668"/></rect>
<rect x="344.0" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1852;0.1982;0.2096;0.2190" values="#ffffff;#ffffff;#ffdf6e;#d6db61;#d6db61;#cfbe61"/></rect>
<rect x="358.86" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1848;0.1988;0.2096;0.2188" values="#ffffff;#ffffff;#ffdc5f;#efda5b;#efda5b;#e6ba5b"/></rect>
<rect x="373.71" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1845;0.1993;0.2096;0.2188" values="#ffffff;#ffffff;#ffd956;#ffd956;#ffd956;#f5b956"/></rect>
<rect x="388.57" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1845;0.1993;0.2096;0.2189" values="#ffffff;#ffffff;#ffd955;#ffd955;#ffd955;#f5ba55"/></rect>
<rect x="329.14" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1861;0.1973;0.2096;0.2185" values="#ffffff;#ffffff;#ffe795;#b7e074;#b7e074;#aeb674"/></rect>
<rect x="344.0" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1857;0.1980;0.2096;0.2183" values="#ffffff;#ffffff;#ffe484;#d0df72;#d0df72;#c4af72"/></rect>
<rect x="358.86" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1854;0.1987;0.2096;0.2182" values="#ffffff;#ffffff;#ffe178;#e9df70;#e9df70;#daab70"/></rect>
<rect x="373.71" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1785;0.1852;0.1993;0.2096;0.2181" values="#ffffff;#ffffff;#ffdf71;#ffdf71;#ffdf71;#efaa71"/></rect>
</g>
</g>
<circle cx="358.86" cy="103.49" r="52.0" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1627;0.1630;1.0000" values="0;0;1;1"/></circle>
<circle cx="358.86" cy="103.49" r="52.0" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2234;0.2237;1.0000" values="0;0;1;1"/></circle>
<circle cx="358.86" cy="103.49" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1627;0.1630;1.0000" values="0;0;1;1"/></circle>
<text x="358.86" y="108.49" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1627;0.1630;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><g clip-path="url(#fd-sph-F3)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2293;0.2296;1.0000" values="0;0;1;1"/><rect x="358.86" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2501;0.2659;0.2763;0.2867" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="373.71" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2494;0.2659;0.2763;0.2867" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="388.57" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2492;0.2659;0.2763;0.2867" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="403.43" y="79.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2498;0.2659;0.2763;0.2867" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="344.0" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2509;0.2654;0.2763;0.2867" values="#ffffff;#ffffff;#ffd74c;#ecd548;#ecd548;#ecd548"/></rect>
<rect x="358.86" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2503;0.2659;0.2763;0.2867" values="#ffffff;#ffffff;#ffd235;#ffd235;#ffd235;#ffd235"/></rect>
<rect x="373.71" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2499;0.2659;0.2763;0.2867" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="388.57" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2498;0.2659;0.2763;0.2867" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="403.43" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2502;0.2659;0.2763;0.2867" values="#ffffff;#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="418.29" y="94.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2507;0.2659;0.2763;0.2867" values="#ffffff;#ffffff;#ffd645;#ffd645;#ffd645;#ffd645"/></rect>
<rect x="344.0" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2513;0.2651;0.2763;0.2863" values="#ffffff;#ffffff;#ffdb5b;#e0d752;#e0d752;#dece52"/></rect>
<rect x="358.86" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2508;0.2657;0.2763;0.2862" values="#ffffff;#ffffff;#ffd648;#f8d646;#f8d646;#f4c946"/></rect>
<rect x="373.71" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2505;0.2659;0.2763;0.2862" values="#ffffff;#ffffff;#ffd43c;#ffd43c;#ffd43c;#fbc63c"/></rect>
<rect x="388.57" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2505;0.2659;0.2763;0.2862" values="#ffffff;#ffffff;#ffd33a;#ffd33a;#ffd33a;#fbc73a"/></rect>
<rect x="403.43" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2507;0.2659;0.2763;0.2863" values="#ffffff;#ffffff;#ffd544;#ffd544;#ffd544;#fccd44"/></rect>
<rect x="418.29" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2512;0.2659;0.2763;0.2865" values="#ffffff;#ffffff;#ffd955;#ffd955;#ffd955;#fed655"/></rect>
<rect x="344.0" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2518;0.2648;0.2763;0.2856" values="#ffffff;#ffffff;#ffdf6e;#d6db61;#d6db61;#cfbe61"/></rect>
<rect x="358.86" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2514;0.2655;0.2763;0.2855" values="#ffffff;#ffffff;#ffdc5f;#efda5b;#efda5b;#e6ba5b"/></rect>
<rect x="373.71" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2512;0.2659;0.2763;0.2855" values="#ffffff;#ffffff;#ffd956;#ffd956;#ffd956;#f5b956"/></rect>
<rect x="388.57" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2512;0.2659;0.2763;0.2855" values="#ffffff;#ffffff;#ffd955;#ffd955;#ffd955;#f5ba55"/></rect>
<rect x="403.43" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2513;0.2659;0.2763;0.2857" values="#ffffff;#ffffff;#ffdb5c;#ffdb5c;#ffdb5c;#f6bf5c"/></rect>
<rect x="418.29" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2517;0.2659;0.2763;0.2859" values="#ffffff;#ffffff;#ffde69;#ffde69;#ffde69;#f8c869"/></rect>
<rect x="358.86" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2521;0.2653;0.2763;0.2848" values="#ffffff;#ffffff;#ffe178;#e9df70;#e9df70;#daab70"/></rect>
<rect x="373.71" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2519;0.2659;0.2763;0.2848" values="#ffffff;#ffffff;#ffdf71;#ffdf71;#ffdf71;#efaa71"/></rect>
<rect x="388.57" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2519;0.2659;0.2763;0.2848" values="#ffffff;#ffffff;#ffdf70;#ffdf70;#ffdf70;#efab70"/></rect>
<rect x="403.43" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2520;0.2659;0.2763;0.2850" values="#ffffff;#ffffff;#ffe075;#ffe075;#ffe075;#f1b175"/></rect>
<rect x="373.71" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2526;0.2659;0.2763;0.2841" values="#ffffff;#ffffff;#ffe58c;#ffe58c;#ffe58c;#e99a8c"/></rect>
<rect x="388.57" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2452;0.2526;0.2659;0.2763;0.2841" values="#ffffff;#ffffff;#ffe58b;#ffe58b;#ffe58b;#e99c8b"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2293;0.2296;0.2945;0.2948;1.0000" values="0;0;1;1;0;0"/><rect x="358.86" y="79.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="373.71" y="79.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="388.57" y="79.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="344.0" y="94.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="358.86" y="94.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="373.71" y="94.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="388.57" y="94.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="344.0" y="109.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="358.86" y="109.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="373.71" y="109.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="388.57" y="109.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="344.0" y="124.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="358.86" y="124.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="373.71" y="124.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="388.57" y="124.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="358.86" y="139.14" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="373.71" y="139.14" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
</g>
</g>
</g>
<circle cx="388.57" cy="118.34" r="46.06" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2293;0.2296;1.0000" values="0;0;1;1"/></circle>
<circle cx="388.57" cy="118.34" r="46.06" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2901;0.2904;1.0000" values="0;0;1;1"/></circle>
<circle cx="388.57" cy="118.34" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2293;0.2296;1.0000" values="0;0;1;1"/></circle>
<text x="388.57" y="123.34" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">4<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2293;0.2296;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><g clip-path="url(#fd-sph-F4)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;1.0000" values="0;0;1;1"/><rect x="180.57" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3103;0.3222;0.3294;0.3430;0.3533" values="#ffffff;#ffc9cc;#ffc9cc;#8bbe85;#8bbe85;#8bbe85"/></rect>
<rect x="195.43" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3110;0.3222;0.3290;0.3430;0.3533" values="#ffffff;#ffe0e2;#ffe0e2;#7bd288;#7bd288;#7bd288"/></rect>
<rect x="210.29" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3116;0.3222;0.3286;0.3430;0.3533" values="#ffffff;#fff8f8;#fff8f8;#6ee78c;#6ee78c;#6ee78c"/></rect>
<rect x="225.14" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3284;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#67ed8b;#67ed8b;#67ed8b"/></rect>
<rect x="240.0" y="109.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3284;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#67ed8b;#67ed8b;#67ed8b"/></rect>
<rect x="165.71" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3099;0.3222;0.3296;0.3428;0.3533" values="#ffffff;#ffbabf;#ffbabf;#90b17f;#8cae7f;#8cae7f"/></rect>
<rect x="180.57" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3105;0.3222;0.3290;0.3430;0.3533" values="#ffffff;#ffd0d3;#ffd0d3;#7ac47f;#7ac47f;#7ac47f"/></rect>
<rect x="195.43" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3112;0.3222;0.3284;0.3430;0.3533" values="#ffffff;#ffe7e8;#ffe7e8;#67d77e;#67d77e;#67d77e"/></rect>
<rect x="210.29" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3118;0.3222;0.3280;0.3430;0.3533" values="#ffffff;#fffefe;#fffefe;#57ea7e;#57ea7e;#57ea7e"/></rect>
<rect x="225.14" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3277;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#4eea78;#4eea78;#4eea78"/></rect>
<rect x="240.0" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3277;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#4eea78;#4eea78;#4eea78"/></rect>
<rect x="254.86" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3220;0.3280;0.3430;0.3533" values="#ffffff;#ffffff;#fffdf8;#57ea7b;#57ea7b;#57ea7b"/></rect>
<rect x="165.71" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3102;0.3222;0.3293;0.3422;0.3533" values="#ffffff;#ffc6ca;#ffc6ca;#85bb80;#78af80;#78af80"/></rect>
<rect x="180.57" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3108;0.3222;0.3286;0.3426;0.3533" values="#ffffff;#ffdbdd;#ffdbdd;#6dcc7d;#69c67d;#69c67d"/></rect>
<rect x="195.43" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3114;0.3222;0.3280;0.3430;0.3533" values="#ffffff;#fff0f1;#fff0f1;#57de77;#57de77;#57de77"/></rect>
<rect x="210.29" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3274;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#43e96f;#43e96f;#43e96f"/></rect>
<rect x="225.14" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3271;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="240.0" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3271;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="254.86" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3274;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#43e96f;#43e96f;#43e96f"/></rect>
<rect x="165.71" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3106;0.3222;0.3291;0.3416;0.3533" values="#ffffff;#ffd4d7;#ffd4d7;#80c885;#69b285;#69b285"/></rect>
<rect x="180.57" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3112;0.3222;0.3284;0.3421;0.3533" values="#ffffff;#ffe8e9;#ffe8e9;#66d77e;#5bc87e;#5bc87e"/></rect>
<rect x="195.43" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3118;0.3222;0.3277;0.3426;0.3533" values="#ffffff;#fffcfc;#fffcfc;#4de775;#4ae175;#4ae175"/></rect>
<rect x="210.29" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3270;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="225.14" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3264;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="240.0" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3264;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="254.86" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3270;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="165.71" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3111;0.3222;0.3291;0.3411;0.3533" values="#ffffff;#ffe4e6;#ffe4e6;#7fd78e;#60b68e;#60b68e"/></rect>
<rect x="180.57" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3116;0.3222;0.3284;0.3417;0.3533" values="#ffffff;#fff6f7;#fff6f7;#66e585;#54cc85;#54cc85"/></rect>
<rect x="195.43" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3277;0.3422;0.3533" values="#ffffff;#ffffff;#ffffff;#4cea76;#45db76;#45db76"/></rect>
<rect x="210.29" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3270;0.3428;0.3533" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3be56a;#3be56a"/></rect>
<rect x="225.14" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3264;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="240.0" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3264;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="254.86" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3270;0.3430;0.3532" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce46a"/></rect>
<rect x="180.57" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3286;0.3413;0.3533" values="#ffffff;#ffffff;#ffffff;#6cee8f;#53cb8f;#53cb8f"/></rect>
<rect x="195.43" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3280;0.3419;0.3533" values="#ffffff;#ffffff;#ffffff;#55eb7d;#49d57d;#49d57d"/></rect>
<rect x="210.29" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3274;0.3425;0.3533" values="#ffffff;#ffffff;#ffffff;#41e96d;#3cdf6d;#3cdf6d"/></rect>
<rect x="225.14" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3270;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="240.0" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3270;0.3430;0.3533" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="195.43" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3284;0.3416;0.3533" values="#ffffff;#ffffff;#ffffff;#65ed89;#52d189;#52d189"/></rect>
<rect x="210.29" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3279;0.3422;0.3533" values="#ffffff;#ffffff;#ffffff;#55eb7d;#4cdc7d;#4cdc7d"/></rect>
<rect x="225.14" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3119;0.3222;0.3277;0.3429;0.3533" values="#ffffff;#ffffff;#ffffff;#4bea76;#4ae876;#4ae876"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;0.3612;0.3615;1.0000" values="0;0;1;1;0;0"/><rect x="165.71" y="124.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="165.71" y="139.14" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
</g>
</g>
</g>
<circle cx="217.71" cy="159.94" r="53.49" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;1.0000" values="0;0;1;1"/></circle>
<circle cx="217.71" cy="159.94" r="53.49" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3567;0.3570;1.0000" values="0;0;1;1"/></circle>
<circle cx="217.71" cy="159.94" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;1.0000" values="0;0;1;1"/></circle>
<text x="217.71" y="164.94" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">5<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><g clip-path="url(#fd-sph-F5)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3627;0.3630;1.0000" values="0;0;1;1"/><rect x="225.14" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3944;0.4096;0.4200" values="#ffffff;#ffffff;#ffffff;#4eea78;#4eea78;#4eea78"/></rect>
<rect x="240.0" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3944;0.4096;0.4200" values="#ffffff;#ffffff;#ffffff;#4eea78;#4eea78;#4eea78"/></rect>
<rect x="254.86" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3887;0.3947;0.4096;0.4200" values="#ffffff;#ffffff;#fffdf8;#57ea7b;#57ea7b;#57ea7b"/></rect>
<rect x="269.71" y="124.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3880;0.3951;0.4096;0.4200" values="#ffffff;#ffffff;#fff8de;#67e679;#67e679;#67e679"/></rect>
<rect x="210.29" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3941;0.4096;0.4200" values="#ffffff;#ffffff;#ffffff;#43e96f;#43e96f;#43e96f"/></rect>
<rect x="225.14" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3937;0.4096;0.4200" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="240.0" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3937;0.4096;0.4200" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="254.86" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3941;0.4096;0.4200" values="#ffffff;#ffffff;#ffffff;#43e96f;#43e96f;#43e96f"/></rect>
<rect x="269.71" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3884;0.3947;0.4096;0.4200" values="#ffffff;#ffffff;#fffaea;#57e774;#57e774;#57e774"/></rect>
<rect x="284.57" y="139.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3878;0.3953;0.4096;0.4197" values="#ffffff;#ffffff;#fff5d3;#6de577;#6de577;#6cdb77"/></rect>
<rect x="210.29" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3937;0.4096;0.4200" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="225.14" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3931;0.4096;0.4200" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="240.0" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3931;0.4096;0.4200" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="254.86" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3937;0.4096;0.4200" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="269.71" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3887;0.3944;0.4096;0.4197" values="#ffffff;#ffffff;#fffef9;#4de974;#4de974;#4cdf74"/></rect>
<rect x="284.57" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3882;0.3951;0.4096;0.4192" values="#ffffff;#ffffff;#fff9e3;#66e77b;#66e77b;#63cf7b"/></rect>
<rect x="210.29" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3937;0.4095;0.4200" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3be56a;#3be56a"/></rect>
<rect x="225.14" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3931;0.4096;0.4200" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="240.0" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3931;0.4096;0.4200" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="254.86" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3937;0.4096;0.4199" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce46a"/></rect>
<rect x="269.71" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3944;0.4096;0.4193" values="#ffffff;#ffffff;#ffffff;#4cea76;#4cea76;#4ad476"/></rect>
<rect x="284.57" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3886;0.3951;0.4096;0.4187" values="#ffffff;#ffffff;#fffdf4;#66eb84;#66eb84;#61c484"/></rect>
<rect x="210.29" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3941;0.4091;0.4200" values="#ffffff;#ffffff;#ffffff;#41e96d;#3cdf6d;#3cdf6d"/></rect>
<rect x="225.14" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3937;0.4096;0.4200" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="240.0" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3937;0.4096;0.4200" values="#ffffff;#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="254.86" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3941;0.4096;0.4195" values="#ffffff;#ffffff;#ffffff;#41e96d;#41e96d;#40da6d"/></rect>
<rect x="269.71" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3946;0.4096;0.4189" values="#ffffff;#ffffff;#ffffff;#55eb7d;#55eb7d;#52ca7d"/></rect>
<rect x="284.57" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3953;0.4096;0.4183" values="#ffffff;#ffffff;#ffffff;#6cee8f;#6cee8f;#66ba8f"/></rect>
<rect x="225.14" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3943;0.4095;0.4200" values="#ffffff;#ffffff;#ffffff;#4bea76;#4ae876;#4ae876"/></rect>
<rect x="240.0" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3943;0.4096;0.4199" values="#ffffff;#ffffff;#ffffff;#4bea76;#4bea76;#4be776"/></rect>
<rect x="254.86" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3946;0.4096;0.4192" values="#ffffff;#ffffff;#ffffff;#55eb7d;#55eb7d;#53d57d"/></rect>
<rect x="269.71" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3785;0.3889;0.3950;0.4096;0.4186" values="#ffffff;#ffffff;#ffffff;#65ed89;#65ed89;#60c389"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3627;0.3630;0.4279;0.4281;1.0000" values="0;0;1;1;0;0"/><rect x="225.14" y="124.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="240.0" y="124.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="254.86" y="124.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="210.29" y="139.14" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="225.14" y="139.14" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="240.0" y="139.14" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="254.86" y="139.14" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="210.29" y="154.0" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="225.14" y="154.0" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="240.0" y="154.0" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="254.86" y="154.0" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="210.29" y="168.86" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="225.14" y="168.86" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="240.0" y="168.86" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="254.86" y="168.86" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="210.29" y="183.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="225.14" y="183.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="240.0" y="183.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="225.14" y="198.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
</g>
</g>
</g>
<circle cx="254.86" cy="168.86" r="49.03" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3627;0.3630;1.0000" values="0;0;1;1"/></circle>
<circle cx="254.86" cy="168.86" r="49.03" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4234;0.4237;1.0000" values="0;0;1;1"/></circle>
<circle cx="254.86" cy="168.86" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3627;0.3630;1.0000" values="0;0;1;1"/></circle>
<text x="254.86" y="173.86" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">6<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3627;0.3630;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><g clip-path="url(#fd-sph-F6)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;1.0000" values="0;0;1;1"/><rect x="76.57" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4433;0.4556;0.4659;0.4724;0.4867" values="#ffffff;#ffc0c4;#ffc0c4;#ffc0c4;#7981c4;#7981c4"/></rect>
<rect x="91.43" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4434;0.4556;0.4659;0.4723;0.4867" values="#ffffff;#ffc1c5;#ffc1c5;#ffc1c5;#7580c5;#7580c5"/></rect>
<rect x="106.29" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4435;0.4556;0.4653;0.4724;0.4867" values="#ffffff;#ffc6ca;#ffc6ca;#e8c4bc;#6e83bc;#6e83bc"/></rect>
<rect x="121.14" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438;0.4556;0.4646;0.4726;0.4867" values="#ffffff;#ffcfd2;#ffcfd2;#cfcab4;#698cb4;#698cb4"/></rect>
<rect x="136.0" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4441;0.4556;0.4639;0.4730;0.4867" values="#ffffff;#ffdadc;#ffdadc;#b6d2ac;#6598ac;#6598ac"/></rect>
<rect x="76.57" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4440;0.4556;0.4659;0.4717;0.4867" values="#ffffff;#ffd8da;#ffd8da;#ffd8da;#6285da;#6285da"/></rect>
<rect x="91.43" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4441;0.4556;0.4659;0.4716;0.4867" values="#ffffff;#ffd9dc;#ffd9dc;#ffd9dc;#5d83dc;#5d83dc"/></rect>
<rect x="106.29" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4442;0.4556;0.4655;0.4717;0.4867" values="#ffffff;#ffdee0;#ffdee0;#eedcd5;#5b87d5;#5b87d5"/></rect>
<rect x="121.14" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4444;0.4556;0.4648;0.4720;0.4867" values="#ffffff;#ffe5e7;#ffe5e7;#d6e1ca;#5a90ca;#5a90ca"/></rect>
<rect x="136.0" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4447;0.4556;0.4641;0.4725;0.4867" values="#ffffff;#ffeff0;#ffeff0;#bde8c1;#5c9dc1;#5c9dc1"/></rect>
<rect x="150.86" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4451;0.4556;0.4635;0.4730;0.4867" values="#ffffff;#fffbfb;#fffbfb;#a6f1b8;#5daeb8;#5daeb8"/></rect>
<rect x="61.71" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4448;0.4556;0.4659;0.4715;0.4867" values="#ffffff;#fff1f2;#fff1f2;#fff1f2;#5b91f2;#5b91f2"/></rect>
<rect x="76.57" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4447;0.4556;0.4659;0.4711;0.4867" values="#ffffff;#fff0f1;#fff0f1;#fff0f1;#4c87f1;#4c87f1"/></rect>
<rect x="91.43" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4448;0.4556;0.4659;0.4709;0.4867" values="#ffffff;#fff1f2;#fff1f2;#fff1f2;#4785f2;#4785f2"/></rect>
<rect x="106.29" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4449;0.4556;0.4657;0.4711;0.4867" values="#ffffff;#fff5f6;#fff5f6;#f7f4f0;#4888f0;#4888f0"/></rect>
<rect x="121.14" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4451;0.4556;0.4651;0.4715;0.4867" values="#ffffff;#fffcfc;#fffcfc;#dff8e4;#4e94e4;#4e94e4"/></rect>
<rect x="136.0" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4644;0.4721;0.4867" values="#ffffff;#ffffff;#ffffff;#c8f9d5;#55a0d5;#55a0d5"/></rect>
<rect x="150.86" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4638;0.4727;0.4867" values="#ffffff;#ffffff;#ffffff;#b2f6c4;#5babc4;#5babc4"/></rect>
<rect x="61.71" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4659;0.4712;0.4867" values="#ffffff;#ffffff;#ffffff;#ffffff;#4f91ff;#4f91ff"/></rect>
<rect x="76.57" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4659;0.4706;0.4867" values="#ffffff;#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="91.43" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4659;0.4702;0.4867" values="#ffffff;#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="106.29" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4659;0.4705;0.4867" values="#ffffff;#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="121.14" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4654;0.4711;0.4867" values="#ffffff;#ffffff;#ffffff;#ebfdf0;#468ef0;#468ef0"/></rect>
<rect x="136.0" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4648;0.4718;0.4867" values="#ffffff;#ffffff;#ffffff;#d5fadf;#539bdf;#539bdf"/></rect>
<rect x="150.86" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4642;0.4725;0.4867" values="#ffffff;#ffffff;#ffffff;#c1f8cf;#5da7cf;#5da7cf"/></rect>
<rect x="76.57" y="243.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4659;0.4704;0.4867" values="#ffffff;#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="91.43" y="243.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4659;0.4698;0.4867" values="#ffffff;#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="106.29" y="243.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4659;0.4703;0.4867" values="#ffffff;#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="121.14" y="243.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4658;0.4710;0.4867" values="#ffffff;#ffffff;#ffffff;#f9fefb;#478dfb;#478dfb"/></rect>
<rect x="136.0" y="243.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4652;0.4717;0.4867" values="#ffffff;#ffffff;#ffffff;#e5fceb;#579aeb;#579aeb"/></rect>
<rect x="150.86" y="243.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4647;0.4724;0.4867" values="#ffffff;#ffffff;#ffffff;#d2fadd;#64a8dd;#64a8dd"/></rect>
<rect x="76.57" y="258.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4659;0.4707;0.4867" values="#ffffff;#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="91.43" y="258.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4659;0.4705;0.4867" values="#ffffff;#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="106.29" y="258.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4659;0.4707;0.4867" values="#ffffff;#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="121.14" y="258.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4659;0.4712;0.4867" values="#ffffff;#ffffff;#ffffff;#ffffff;#5192ff;#5192ff"/></rect>
<rect x="136.0" y="258.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4452;0.4556;0.4657;0.4719;0.4867" values="#ffffff;#ffffff;#ffffff;#f6fef8;#639ff8;#639ff8"/></rect>
</g>
</g>
<circle cx="115.2" cy="228.29" r="49.03" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;1.0000" values="0;0;1;1"/></circle>
<circle cx="115.2" cy="228.29" r="49.03" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4901;0.4904;1.0000" values="0;0;1;1"/></circle>
<circle cx="115.2" cy="228.29" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;1.0000" values="0;0;1;1"/></circle>
<text x="115.2" y="233.29" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">7<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><g clip-path="url(#fd-sph-F7)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;1.0000" values="0;0;1;1"/><rect x="136.0" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5096;0.5222;0.5305;0.5409;0.5533" values="#ffffff;#ffb2b7;#ffb2b7;#b3ac8d;#808d8d;#808d8d"/></rect>
<rect x="150.86" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5101;0.5222;0.5298;0.5412;0.5533" values="#ffffff;#ffc2c6;#ffc2c6;#99b989;#759e89;#759e89"/></rect>
<rect x="106.29" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5095;0.5222;0.5319;0.5397;0.5533" values="#ffffff;#ffafb4;#ffafb4;#e6ada7;#817ea7;#817ea7"/></rect>
<rect x="121.14" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5098;0.5222;0.5312;0.5399;0.5533" values="#ffffff;#ffb9bd;#ffb9bd;#ccb5a0;#7986a0;#7986a0"/></rect>
<rect x="136.0" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5102;0.5222;0.5305;0.5403;0.5533" values="#ffffff;#ffc5c9;#ffc5c9;#b2be9b;#71939b;#71939b"/></rect>
<rect x="150.86" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5106;0.5222;0.5298;0.5407;0.5533" values="#ffffff;#ffd4d7;#ffd4d7;#99ca95;#69a395;#69a395"/></rect>
<rect x="165.71" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5111;0.5222;0.5291;0.5411;0.5533" values="#ffffff;#ffe4e6;#ffe4e6;#7fd78e;#60b68e;#60b68e"/></rect>
<rect x="106.29" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5102;0.5222;0.5320;0.5390;0.5533" values="#ffffff;#ffc6ca;#ffc6ca;#e8c4bc;#6e83bc;#6e83bc"/></rect>
<rect x="121.14" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5104;0.5222;0.5313;0.5393;0.5533" values="#ffffff;#ffcfd2;#ffcfd2;#cfcab4;#698cb4;#698cb4"/></rect>
<rect x="136.0" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5108;0.5222;0.5306;0.5397;0.5533" values="#ffffff;#ffdadc;#ffdadc;#b6d2ac;#6598ac;#6598ac"/></rect>
<rect x="150.86" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5112;0.5222;0.5299;0.5401;0.5533" values="#ffffff;#ffe7e8;#ffe7e8;#9ddca4;#61a8a4;#61a8a4"/></rect>
<rect x="165.71" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5116;0.5222;0.5292;0.5407;0.5533" values="#ffffff;#fff6f7;#fff6f7;#85e89c;#5cbb9c;#5cbb9c"/></rect>
<rect x="180.57" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5119;0.5222;0.5286;0.5413;0.5533" values="#ffffff;#ffffff;#ffffff;#6cee8f;#53cb8f;#53cb8f"/></rect>
<rect x="106.29" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5109;0.5222;0.5321;0.5384;0.5533" values="#ffffff;#ffdee0;#ffdee0;#eedcd5;#5b87d5;#5b87d5"/></rect>
<rect x="121.14" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5111;0.5222;0.5315;0.5387;0.5533" values="#ffffff;#ffe5e7;#ffe5e7;#d6e1ca;#5a90ca;#5a90ca"/></rect>
<rect x="136.0" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5114;0.5222;0.5308;0.5392;0.5533" values="#ffffff;#ffeff0;#ffeff0;#bde8c1;#5c9dc1;#5c9dc1"/></rect>
<rect x="150.86" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5117;0.5222;0.5302;0.5397;0.5533" values="#ffffff;#fffbfb;#fffbfb;#a6f1b8;#5daeb8;#5daeb8"/></rect>
<rect x="165.71" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5119;0.5222;0.5295;0.5403;0.5533" values="#ffffff;#ffffff;#ffffff;#8ff2a9;#5bbba9;#5bbba9"/></rect>
<rect x="180.57" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5119;0.5222;0.5289;0.5409;0.5533" values="#ffffff;#ffffff;#ffffff;#79ef98;#57c698;#57c698"/></rect>
<rect x="106.29" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5116;0.5222;0.5324;0.5377;0.5533" values="#ffffff;#fff5f6;#fff5f6;#f7f4f0;#4888f0;#4888f0"/></rect>
<rect x="121.14" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5118;0.5222;0.5317;0.5382;0.5533" values="#ffffff;#fffcfc;#fffcfc;#dff8e4;#4e94e4;#4e94e4"/></rect>
<rect x="136.0" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5119;0.5222;0.5311;0.5387;0.5533" values="#ffffff;#ffffff;#ffffff;#c8f9d5;#55a0d5;#55a0d5"/></rect>
<rect x="150.86" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5119;0.5222;0.5305;0.5393;0.5533" values="#ffffff;#ffffff;#ffffff;#b2f6c4;#5babc4;#5babc4"/></rect>
<rect x="165.71" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5119;0.5222;0.5299;0.5400;0.5533" values="#ffffff;#ffffff;#ffffff;#9df3b4;#5eb6b4;#5eb6b4"/></rect>
<rect x="106.29" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5119;0.5222;0.5326;0.5372;0.5533" values="#ffffff;#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="121.14" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5119;0.5222;0.5320;0.5378;0.5533" values="#ffffff;#ffffff;#ffffff;#ebfdf0;#468ef0;#468ef0"/></rect>
<rect x="136.0" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5119;0.5222;0.5315;0.5384;0.5533" values="#ffffff;#ffffff;#ffffff;#d5fadf;#539bdf;#539bdf"/></rect>
<rect x="150.86" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5119;0.5222;0.5309;0.5391;0.5533" values="#ffffff;#ffffff;#ffffff;#c1f8cf;#5da7cf;#5da7cf"/></rect>
<rect x="165.71" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5119;0.5222;0.5304;0.5398;0.5533" values="#ffffff;#ffffff;#ffffff;#aef5c1;#64b4c1;#64b4c1"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;0.5612;0.5615;1.0000" values="0;0;1;1;0;0"/><rect x="136.0" y="154.0" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="150.86" y="154.0" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="165.71" y="168.86" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="106.29" y="183.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="121.14" y="183.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="136.0" y="183.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="180.57" y="183.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="106.29" y="198.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="121.14" y="198.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="136.0" y="198.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="150.86" y="198.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="106.29" y="213.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="121.14" y="213.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="136.0" y="213.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="150.86" y="213.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="106.29" y="228.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="121.14" y="228.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="136.0" y="228.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="150.86" y="228.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
</g>
</g>
</g>
<circle cx="144.91" cy="204.51" r="46.06" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;1.0000" values="0;0;1;1"/></circle>
<circle cx="144.91" cy="204.51" r="46.06" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5567;0.5570;1.0000" values="0;0;1;1"/></circle>
<circle cx="144.91" cy="204.51" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;1.0000" values="0;0;1;1"/></circle>
<text x="144.91" y="209.51" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">8<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><g clip-path="url(#fd-sph-F8)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;1.0000" values="0;0;1;1"/><rect x="344.0" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5876;0.5980;0.6096;0.6163" values="#ffffff;#ffffff;#fff4ce;#cfefb0;#cfefb0;#b680b0"/></rect>
<rect x="358.86" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5874;0.5986;0.6096;0.6161" values="#ffffff;#ffffff;#fff2c6;#e8f0b9;#e8f0b9;#ca79b9"/></rect>
<rect x="373.71" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5873;0.5993;0.6096;0.6160" values="#ffffff;#ffffff;#fff1c2;#fff1c2;#fff1c2;#dd77c2"/></rect>
<rect x="388.57" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5873;0.5993;0.6096;0.6161" values="#ffffff;#ffffff;#fff1c1;#fff1c1;#fff1c1;#dd7ac1"/></rect>
<rect x="329.14" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5885;0.5975;0.6096;0.6162" values="#ffffff;#ffffff;#fffcf1;#bdf4c2;#bdf4c2;#a57ec2"/></rect>
<rect x="344.0" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5883;0.5981;0.6096;0.6157" values="#ffffff;#ffffff;#fffae8;#d6f5cb;#d6f5cb;#b771cb"/></rect>
<rect x="358.86" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5881;0.5988;0.6096;0.6154" values="#ffffff;#ffffff;#fff8e1;#eef6d5;#eef6d5;#c967d5"/></rect>
<rect x="373.71" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5880;0.5993;0.6096;0.6153" values="#ffffff;#ffffff;#fff7dd;#fff7dd;#fff7dd;#d764dd"/></rect>
<rect x="388.57" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5880;0.5993;0.6096;0.6154" values="#ffffff;#ffffff;#fff7dd;#fff7dd;#fff7dd;#d868dd"/></rect>
<rect x="403.43" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5881;0.5993;0.6096;0.6158" values="#ffffff;#ffffff;#fff8df;#fff8df;#fff8df;#db73df"/></rect>
<rect x="329.14" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5978;0.6096;0.6158" values="#ffffff;#ffffff;#ffffff;#c8f9d5;#c8f9d5;#ab73d5"/></rect>
<rect x="344.0" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5984;0.6096;0.6152" values="#ffffff;#ffffff;#ffffff;#dffbe7;#dffbe7;#bb62e7"/></rect>
<rect x="358.86" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5888;0.5990;0.6096;0.6148" values="#ffffff;#ffffff;#fffefc;#f7fdf5;#f7fdf5;#cb55f5"/></rect>
<rect x="373.71" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5887;0.5993;0.6096;0.6146" values="#ffffff;#ffffff;#fffdf8;#fffdf8;#fffdf8;#d152f8"/></rect>
<rect x="388.57" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5887;0.5993;0.6096;0.6148" values="#ffffff;#ffffff;#fffdf8;#fffdf8;#fffdf8;#d256f8"/></rect>
<rect x="403.43" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5888;0.5993;0.6096;0.6152" values="#ffffff;#ffffff;#fffefa;#fffefa;#fffefa;#d665fa"/></rect>
<rect x="329.14" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5981;0.6096;0.6155" values="#ffffff;#ffffff;#ffffff;#d5fadf;#d5fadf;#b56bdf"/></rect>
<rect x="344.0" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5987;0.6096;0.6148" values="#ffffff;#ffffff;#ffffff;#ebfdf0;#ebfdf0;#c257f0"/></rect>
<rect x="358.86" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5993;0.6096;0.6142" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="373.71" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5993;0.6096;0.6139" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="388.57" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5993;0.6096;0.6143" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="403.43" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5993;0.6096;0.6149" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#d35aff"/></rect>
<rect x="329.14" y="243.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5985;0.6096;0.6154" values="#ffffff;#ffffff;#ffffff;#e5fceb;#e5fceb;#c16aeb"/></rect>
<rect x="344.0" y="243.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5991;0.6096;0.6147" values="#ffffff;#ffffff;#ffffff;#f9fefb;#f9fefb;#cd54fb"/></rect>
<rect x="358.86" y="243.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5993;0.6096;0.6140" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="373.71" y="243.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5993;0.6096;0.6135" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="388.57" y="243.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5993;0.6096;0.6141" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="403.43" y="243.14" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5993;0.6096;0.6148" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#d256ff"/></rect>
<rect x="344.0" y="258.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5993;0.6096;0.6149" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#d35cff"/></rect>
<rect x="358.86" y="258.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5993;0.6096;0.6144" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="373.71" y="258.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5993;0.6096;0.6142" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="388.57" y="258.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5785;0.5889;0.5993;0.6096;0.6145" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
</g>
</g>
<circle cx="373.71" cy="228.29" r="52.0" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;1.0000" values="0;0;1;1"/></circle>
<circle cx="373.71" cy="228.29" r="52.0" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6234;0.6237;1.0000" values="0;0;1;1"/></circle>
<circle cx="373.71" cy="228.29" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;1.0000" values="0;0;1;1"/></circle>
<text x="373.71" y="233.29" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">9<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><g clip-path="url(#fd-sph-F9)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;1.0000" values="0;0;1;1"/><rect x="314.29" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6538;0.6631;0.6763;0.6849" values="#ffffff;#ffffff;#fff0bb;#99e582;#99e582;#90b282"/></rect>
<rect x="329.14" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6534;0.6638;0.6763;0.6846" values="#ffffff;#ffffff;#ffecaa;#b3e483;#b3e483;#a6a783"/></rect>
<rect x="344.0" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6530;0.6645;0.6763;0.6843" values="#ffffff;#ffffff;#ffe99c;#cce484;#cce484;#bc9f84"/></rect>
<rect x="358.86" y="154.0" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6527;0.6652;0.6763;0.6841" values="#ffffff;#ffffff;#ffe792;#e6e487;#e6e487;#d29b87"/></rect>
<rect x="299.43" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6548;0.6624;0.6763;0.6848" values="#ffffff;#ffffff;#fff8e1;#7fea8b;#7fea8b;#77b48b"/></rect>
<rect x="314.29" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6543;0.6631;0.6763;0.6844" values="#ffffff;#ffffff;#fff5d0;#99e990;#99e990;#8da590"/></rect>
<rect x="329.14" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6540;0.6638;0.6763;0.6840" values="#ffffff;#ffffff;#fff1c1;#b2e995;#b2e995;#a29995"/></rect>
<rect x="344.0" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6536;0.6645;0.6763;0.6836" values="#ffffff;#ffffff;#ffeeb5;#cce999;#cce999;#b79099"/></rect>
<rect x="358.86" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6534;0.6652;0.6763;0.6834" values="#ffffff;#ffffff;#ffedac;#e6ea9f;#e6ea9f;#cd8a9f"/></rect>
<rect x="373.71" y="168.86" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6533;0.6659;0.6763;0.6834" values="#ffffff;#ffffff;#ffeba7;#ffeba7;#ffeba7;#e389a7"/></rect>
<rect x="299.43" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6553;0.6626;0.6763;0.6844" values="#ffffff;#ffffff;#fffdf6;#85ef9c;#85ef9c;#7aaa9c"/></rect>
<rect x="314.29" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6549;0.6633;0.6763;0.6838" values="#ffffff;#ffffff;#fffae6;#9deea3;#9deea3;#8e99a3"/></rect>
<rect x="329.14" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6546;0.6639;0.6763;0.6834" values="#ffffff;#ffffff;#fff7d9;#b6eea9;#b6eea9;#a28ba9"/></rect>
<rect x="344.0" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6543;0.6646;0.6763;0.6830" values="#ffffff;#ffffff;#fff4ce;#cfefb0;#cfefb0;#b680b0"/></rect>
<rect x="358.86" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6541;0.6653;0.6763;0.6827" values="#ffffff;#ffffff;#fff2c6;#e8f0b9;#e8f0b9;#ca79b9"/></rect>
<rect x="373.71" y="183.71" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6540;0.6659;0.6763;0.6827" values="#ffffff;#ffffff;#fff1c2;#fff1c2;#fff1c2;#dd77c2"/></rect>
<rect x="299.43" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6556;0.6629;0.6763;0.6840" values="#ffffff;#ffffff;#ffffff;#8ff2a9;#8ff2a9;#82a0a9"/></rect>
<rect x="314.29" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6555;0.6635;0.6763;0.6834" values="#ffffff;#ffffff;#fffffe;#a6f4ba;#a6f4ba;#938fba"/></rect>
<rect x="329.14" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6552;0.6641;0.6763;0.6829" values="#ffffff;#ffffff;#fffcf1;#bdf4c2;#bdf4c2;#a57ec2"/></rect>
<rect x="344.0" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6550;0.6648;0.6763;0.6824" values="#ffffff;#ffffff;#fffae8;#d6f5cb;#d6f5cb;#b771cb"/></rect>
<rect x="358.86" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6548;0.6655;0.6763;0.6821" values="#ffffff;#ffffff;#fff8e1;#eef6d5;#eef6d5;#c967d5"/></rect>
<rect x="373.71" y="198.57" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6547;0.6659;0.6763;0.6820" values="#ffffff;#ffffff;#fff7dd;#fff7dd;#fff7dd;#d764dd"/></rect>
<rect x="299.43" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6556;0.6632;0.6763;0.6837" values="#ffffff;#ffffff;#ffffff;#9df3b4;#9df3b4;#8d98b4"/></rect>
<rect x="314.29" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6556;0.6638;0.6763;0.6830" values="#ffffff;#ffffff;#ffffff;#b2f6c4;#b2f6c4;#9c85c4"/></rect>
<rect x="329.14" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6556;0.6644;0.6763;0.6824" values="#ffffff;#ffffff;#ffffff;#c8f9d5;#c8f9d5;#ab73d5"/></rect>
<rect x="344.0" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6556;0.6651;0.6763;0.6819" values="#ffffff;#ffffff;#ffffff;#dffbe7;#dffbe7;#bb62e7"/></rect>
<rect x="358.86" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6555;0.6657;0.6763;0.6814" values="#ffffff;#ffffff;#fffefc;#f7fdf5;#f7fdf5;#cb55f5"/></rect>
<rect x="373.71" y="213.43" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6554;0.6659;0.6763;0.6813" values="#ffffff;#ffffff;#fffdf8;#fffdf8;#fffdf8;#d152f8"/></rect>
<rect x="314.29" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6556;0.6642;0.6763;0.6828" values="#ffffff;#ffffff;#ffffff;#c1f8cf;#c1f8cf;#a87fcf"/></rect>
<rect x="329.14" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6556;0.6648;0.6763;0.6821" values="#ffffff;#ffffff;#ffffff;#d5fadf;#d5fadf;#b56bdf"/></rect>
<rect x="344.0" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6556;0.6654;0.6763;0.6815" values="#ffffff;#ffffff;#ffffff;#ebfdf0;#ebfdf0;#c257f0"/></rect>
<rect x="358.86" y="228.29" width="15.16" height="15.16" fill="#ffffff"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6452;0.6556;0.6659;0.6763;0.6809" values="#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;0.6945;0.6948;1.0000" values="0;0;1;1;0;0"/><rect x="344.0" y="183.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="358.86" y="183.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="373.71" y="183.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="329.14" y="198.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="344.0" y="198.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="358.86" y="198.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="373.71" y="198.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="329.14" y="213.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="344.0" y="213.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="358.86" y="213.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="373.71" y="213.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="329.14" y="228.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="344.0" y="228.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="358.86" y="228.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
</g>
</g>
</g>
<circle cx="344.0" cy="201.54" r="46.06" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;1.0000" values="0;0;1;1"/></circle>
<circle cx="344.0" cy="201.54" r="46.06" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6901;0.6904;1.0000" values="0;0;1;1"/></circle>
<circle cx="344.0" cy="201.54" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;1.0000" values="0;0;1;1"/></circle>
<text x="344.0" y="206.54" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">10<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-d)"><g clip-path="url(#fd-sph-D0)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;1.0000" values="0;0;1;1"/><rect x="571.43" y="50.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="50.0" width="5.15" height="15.16" fill="#6c0084"/>
<rect x="581.33" y="50.0" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="586.29" y="50.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="50.0" width="5.15" height="15.16" fill="#930084"/>
<rect x="596.19" y="50.0" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="541.71" y="64.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="546.67" y="64.86" width="5.15" height="15.16" fill="#1c2484"/>
<rect x="551.62" y="64.86" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="556.57" y="64.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="561.52" y="64.86" width="5.15" height="15.16" fill="#4424c1"/>
<rect x="566.48" y="64.86" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="571.43" y="64.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="64.86" width="5.15" height="15.16" fill="#6c24d6"/>
<rect x="581.33" y="64.86" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="586.29" y="64.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="64.86" width="5.15" height="15.16" fill="#9324d6"/>
<rect x="596.19" y="64.86" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="601.14" y="64.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="64.86" width="5.15" height="15.16" fill="#bb24c1"/>
<rect x="611.05" y="64.86" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="616.0" y="64.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="64.86" width="5.15" height="15.16" fill="#e32484"/>
<rect x="625.9" y="64.86" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="541.71" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="546.67" y="79.71" width="5.15" height="15.16" fill="#1c4cbc"/>
<rect x="551.62" y="79.71" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="556.57" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="561.52" y="79.71" width="5.15" height="15.16" fill="#444ce4"/>
<rect x="566.48" y="79.71" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="571.43" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="79.71" width="5.15" height="15.16" fill="#6c4cf2"/>
<rect x="581.33" y="79.71" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="586.29" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="79.71" width="5.15" height="15.16" fill="#934cf2"/>
<rect x="596.19" y="79.71" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="601.14" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="79.71" width="5.15" height="15.16" fill="#bb4ce4"/>
<rect x="611.05" y="79.71" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="616.0" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="79.71" width="5.15" height="15.16" fill="#e34cbc"/>
<rect x="625.9" y="79.71" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="541.71" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="546.67" y="94.57" width="5.15" height="15.16" fill="#1c74ce"/>
<rect x="551.62" y="94.57" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="556.57" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="561.52" y="94.57" width="5.15" height="15.16" fill="#4474ef"/>
<rect x="566.48" y="94.57" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="571.43" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="94.57" width="5.15" height="15.16" fill="#6c74fd"/>
<rect x="581.33" y="94.57" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="586.29" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="94.57" width="5.15" height="15.16" fill="#9374fd"/>
<rect x="596.19" y="94.57" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="601.14" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="94.57" width="5.15" height="15.16" fill="#bb74ef"/>
<rect x="611.05" y="94.57" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="616.0" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="94.57" width="5.15" height="15.16" fill="#e374ce"/>
<rect x="625.9" y="94.57" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="541.71" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="546.67" y="109.43" width="5.15" height="15.16" fill="#1c9bca"/>
<rect x="551.62" y="109.43" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="556.57" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="561.52" y="109.43" width="5.15" height="15.16" fill="#449bed"/>
<rect x="566.48" y="109.43" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="571.43" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="109.43" width="5.15" height="15.16" fill="#6c9bfa"/>
<rect x="581.33" y="109.43" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="586.29" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="109.43" width="5.15" height="15.16" fill="#939bfa"/>
<rect x="596.19" y="109.43" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="601.14" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="109.43" width="5.15" height="15.16" fill="#bb9bed"/>
<rect x="611.05" y="109.43" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="616.0" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="109.43" width="5.15" height="15.16" fill="#e39bca"/>
<rect x="625.9" y="109.43" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="541.71" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="546.67" y="124.29" width="5.15" height="15.16" fill="#1cc3a9"/>
<rect x="551.62" y="124.29" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="556.57" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="561.52" y="124.29" width="5.15" height="15.16" fill="#44c3d9"/>
<rect x="566.48" y="124.29" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="571.43" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="124.29" width="5.15" height="15.16" fill="#6cc3ea"/>
<rect x="581.33" y="124.29" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="586.29" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="124.29" width="5.15" height="15.16" fill="#93c3ea"/>
<rect x="596.19" y="124.29" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="601.14" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="124.29" width="5.15" height="15.16" fill="#bbc3d9"/>
<rect x="611.05" y="124.29" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="616.0" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="124.29" width="5.15" height="15.16" fill="#e3c3a9"/>
<rect x="625.9" y="124.29" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="556.57" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="561.52" y="139.14" width="5.15" height="15.16" fill="#44eba1"/>
<rect x="566.48" y="139.14" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="571.43" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="139.14" width="5.15" height="15.16" fill="#6cebc1"/>
<rect x="581.33" y="139.14" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="586.29" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="139.14" width="5.15" height="15.16" fill="#93ebc1"/>
<rect x="596.19" y="139.14" width="5.15" height="15.16" fill="#cccccc"/>
<rect x="601.14" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="139.14" width="5.15" height="15.16" fill="#bbeba1"/>
<rect x="611.05" y="139.14" width="5.15" height="15.16" fill="#cccccc"/>
</g>
<g><rect x="571.43" y="50.0" width="15.16" height="15.16" fill="#ff525d" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4208" values="0;1"/></rect>
<rect x="586.29" y="50.0" width="15.16" height="15.16" fill="#ff606a" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4220" values="0;1"/></rect>
<rect x="541.71" y="64.86" width="15.16" height="15.16" fill="#ff4753" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4196" values="0;1"/></rect>
<rect x="556.57" y="64.86" width="15.16" height="15.16" fill="#ff4753" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4208" values="0;1"/></rect>
<rect x="571.43" y="64.86" width="15.16" height="15.16" fill="#ff4753" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4220" values="0;1"/></rect>
<rect x="586.29" y="64.86" width="15.16" height="15.16" fill="#ff515c" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4233" values="0;1"/></rect>
<rect x="601.14" y="64.86" width="15.16" height="15.16" fill="#ff6770" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4245" values="0;1"/></rect>
<rect x="616.0" y="64.86" width="15.16" height="15.16" fill="#ff7e86" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4923;0.5590;0.6257;0.6923" values="#ff7e86;#ff7e86;#f87d83;#f87d83;#f87d83"/></rect>
<rect x="541.71" y="79.71" width="15.16" height="15.16" fill="#ff4753" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4208" values="0;1"/></rect>
<rect x="556.57" y="79.71" width="15.16" height="15.16" fill="#ff4753" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4220" values="0;1"/></rect>
<rect x="571.43" y="79.71" width="15.16" height="15.16" fill="#ff4753" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4233" values="0;1"/></rect>
<rect x="541.71" y="94.57" width="15.16" height="15.16" fill="#ff4753" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4220" values="0;1"/></rect>
<rect x="556.57" y="94.57" width="15.16" height="15.16" fill="#ff4753" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4233" values="0;1"/></rect>
<rect x="541.71" y="109.43" width="15.16" height="15.16" fill="#ff4d58" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4233" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4899;0.5566;0.6233;0.6899" values="#ff4d58;#ff4d58;#ff4d58;#f44b58;#f44b58"/></rect>
<rect x="556.57" y="109.43" width="15.16" height="15.16" fill="#ff4753" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4245" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4911;0.5578;0.6245;0.6911" values="#ff4753;#ff4753;#ff4753;#f04553;#f04553"/></rect>
<rect x="541.71" y="124.29" width="15.16" height="15.16" fill="#ff636d" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4245" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4911;0.5578;0.6245;0.6911" values="#ff636d;#ff636d;#ff636d;#dc5b6d;#dc5b6d"/></rect>
<rect x="556.57" y="124.29" width="15.16" height="15.16" fill="#ff5f69" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4923;0.5590;0.6257;0.6923" values="#ff5f69;#ff5f69;#ff5f69;#d85669;#d85669"/></rect>
<rect x="556.57" y="139.14" width="15.16" height="15.16" fill="#ff7780" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4269" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4935;0.5602;0.6269;0.6935" values="#ff7780;#ff7780;#ff7780;#c06580;#c06580"/></rect>
</g>
</g>
<circle cx="586.29" cy="106.46" r="52.0" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;1.0000" values="0;0;1;1"/></circle>
<circle cx="586.29" cy="106.46" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;1.0000" values="0;0;1;1"/></circle>
<text x="586.29" y="111.46" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;1.0000" values="0;0;1;1"/></text>
<circle cx="586.29" cy="106.46" r="52.0" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g clip-path="url(#fd-sph-D1)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0923;0.0926;1.0000" values="0;0;1;1"/><rect x="586.29" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="79.71" width="5.15" height="15.16" fill="#401eb3"/>
<rect x="596.19" y="79.71" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="601.14" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="79.71" width="5.15" height="15.16" fill="#6a1ecf"/>
<rect x="611.05" y="79.71" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="616.0" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="79.71" width="5.15" height="15.16" fill="#951ecf"/>
<rect x="625.9" y="79.71" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="630.86" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="79.71" width="5.15" height="15.16" fill="#bf1eb3"/>
<rect x="640.76" y="79.71" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="571.43" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="94.57" width="5.15" height="15.16" fill="#1548ab"/>
<rect x="581.33" y="94.57" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="586.29" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="94.57" width="5.15" height="15.16" fill="#4048df"/>
<rect x="596.19" y="94.57" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="601.14" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="94.57" width="5.15" height="15.16" fill="#6a48f0"/>
<rect x="611.05" y="94.57" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="616.0" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="94.57" width="5.15" height="15.16" fill="#9548f0"/>
<rect x="625.9" y="94.57" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="630.86" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="94.57" width="5.15" height="15.16" fill="#bf48df"/>
<rect x="640.76" y="94.57" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="645.71" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="650.67" y="94.57" width="5.15" height="15.16" fill="#ea48ab"/>
<rect x="655.62" y="94.57" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="571.43" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="109.43" width="5.15" height="15.16" fill="#1573c5"/>
<rect x="581.33" y="109.43" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="586.29" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="109.43" width="5.15" height="15.16" fill="#4073ed"/>
<rect x="596.19" y="109.43" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="601.14" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="109.43" width="5.15" height="15.16" fill="#6a73fd"/>
<rect x="611.05" y="109.43" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="616.0" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="109.43" width="5.15" height="15.16" fill="#9573fd"/>
<rect x="625.9" y="109.43" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="630.86" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="109.43" width="5.15" height="15.16" fill="#bf73ed"/>
<rect x="640.76" y="109.43" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="645.71" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="650.67" y="109.43" width="5.15" height="15.16" fill="#ea73c5"/>
<rect x="655.62" y="109.43" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="571.43" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="124.29" width="5.15" height="15.16" fill="#159dbf"/>
<rect x="581.33" y="124.29" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="586.29" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="124.29" width="5.15" height="15.16" fill="#409dea"/>
<rect x="596.19" y="124.29" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="601.14" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="124.29" width="5.15" height="15.16" fill="#6a9dfa"/>
<rect x="611.05" y="124.29" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="616.0" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="124.29" width="5.15" height="15.16" fill="#959dfa"/>
<rect x="625.9" y="124.29" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="630.86" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="124.29" width="5.15" height="15.16" fill="#bf9dea"/>
<rect x="640.76" y="124.29" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="645.71" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="650.67" y="124.29" width="5.15" height="15.16" fill="#ea9dbf"/>
<rect x="655.62" y="124.29" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="571.43" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="139.14" width="5.15" height="15.16" fill="#15c884"/>
<rect x="581.33" y="139.14" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="586.29" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="139.14" width="5.15" height="15.16" fill="#40c8d3"/>
<rect x="596.19" y="139.14" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="601.14" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="139.14" width="5.15" height="15.16" fill="#6ac8e6"/>
<rect x="611.05" y="139.14" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="616.0" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="139.14" width="5.15" height="15.16" fill="#95c8e6"/>
<rect x="625.9" y="139.14" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="630.86" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="139.14" width="5.15" height="15.16" fill="#bfc8d3"/>
<rect x="640.76" y="139.14" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="645.71" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="650.67" y="139.14" width="5.15" height="15.16" fill="#eac884"/>
<rect x="655.62" y="139.14" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="586.29" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="154.0" width="5.15" height="15.16" fill="#40f284"/>
<rect x="596.19" y="154.0" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="601.14" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="154.0" width="5.15" height="15.16" fill="#6af2b3"/>
<rect x="611.05" y="154.0" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="616.0" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="154.0" width="5.15" height="15.16" fill="#95f2b3"/>
<rect x="625.9" y="154.0" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="630.86" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="154.0" width="5.15" height="15.16" fill="#bff284"/>
<rect x="640.76" y="154.0" width="5.15" height="15.16" fill="#bbbbbb"/>
</g>
<g><rect x="586.29" y="79.71" width="15.16" height="15.16" fill="#ff4a55" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4245" values="0;1"/></rect>
<rect x="601.14" y="79.71" width="15.16" height="15.16" fill="#ff626c" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4923;0.5590;0.6257;0.6923" values="#ff626c;#ff626c;#fb626a;#fb626a;#fb626a"/></rect>
<rect x="616.0" y="79.71" width="15.16" height="15.16" fill="#ff7a82" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4269" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4935;0.5602;0.6269;0.6935" values="#ff7a82;#ff7a82;#e77979;#e77979;#e77979"/></rect>
<rect x="630.86" y="79.71" width="15.16" height="15.16" fill="#ff9299" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4281" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4947;0.5614;0.6281;0.6947" values="#ff9299;#ff9299;#d48f85;#d48f85;#d48f85"/></rect>
<rect x="571.43" y="94.57" width="15.16" height="15.16" fill="#ff4753" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4245" values="0;1"/></rect>
<rect x="586.29" y="94.57" width="15.16" height="15.16" fill="#ff4e59" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="0;1"/></rect>
<rect x="601.14" y="94.57" width="15.16" height="15.16" fill="#ff656f" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4269" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4935;0.5602;0.6269;0.6935" values="#ff656f;#ff656f;#ec6468;#ec6468;#ec6468"/></rect>
<rect x="616.0" y="94.57" width="15.16" height="15.16" fill="#ff7c85" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4281" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4947;0.5614;0.6281;0.6947" values="#ff7c85;#ff7c85;#d77a75;#d77a75;#d77a75"/></rect>
<rect x="630.86" y="94.57" width="15.16" height="15.16" fill="#ff949b" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4293" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960;0.5626;0.6293;0.6960" values="#ff949b;#ff949b;#c2907f;#c2907f;#c2907f"/></rect>
<rect x="645.71" y="94.57" width="15.16" height="15.16" fill="#ffacb1" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4305" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4972;0.5638;0.6305;0.6972" values="#ffacb1;#ffacb1;#afa687;#afa687;#afa687"/></rect>
<rect x="571.43" y="109.43" width="15.16" height="15.16" fill="#ff4d58" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4923;0.5590;0.6257;0.6923" values="#ff4d58;#ff4d58;#ff4d58;#ee4a58;#ee4a58"/></rect>
<rect x="586.29" y="109.43" width="15.16" height="15.16" fill="#ff5c66" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4269" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4935;0.5602;0.6269;0.6935" values="#ff5c66;#ff5c66;#f85b64;#e85864;#e85864"/></rect>
<rect x="601.14" y="109.43" width="15.16" height="15.16" fill="#ff6f78" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4281" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4947;0.5614;0.6281;0.6947" values="#ff6f78;#ff6f78;#e06d6d;#d66a6d;#d66a6d"/></rect>
<rect x="616.0" y="109.43" width="15.16" height="15.16" fill="#ff848c" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4293" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960;0.5626;0.6293;0.6960" values="#ff848c;#ff848c;#c98175;#c57f75;#c57f75"/></rect>
<rect x="630.86" y="109.43" width="15.16" height="15.16" fill="#ff9ba1" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4305" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4972;0.5638;0.6305;0.6972" values="#ff9ba1;#ff9ba1;#b3957c;#b3957c;#b3957c"/></rect>
<rect x="645.71" y="109.43" width="15.16" height="15.16" fill="#ffb1b6" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4317" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4984;0.5650;0.6317;0.6984" values="#ffb1b6;#ffb1b6;#9ea981;#9ea981;#9ea981"/></rect>
<rect x="571.43" y="124.29" width="15.16" height="15.16" fill="#ff636d" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4269" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4935;0.5602;0.6269;0.6935" values="#ff636d;#ff636d;#ff636d;#d6596d;#d6596d"/></rect>
<rect x="586.29" y="124.29" width="15.16" height="15.16" fill="#ff6e77" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4281" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4947;0.5614;0.6281;0.6947" values="#ff6e77;#ff6e77;#ef6d71;#ca6371;#ca6371"/></rect>
<rect x="601.14" y="124.29" width="15.16" height="15.16" fill="#ff7e86" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4293" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960;0.5626;0.6293;0.6960" values="#ff7e86;#ff7e86;#d67c76;#b97176;#b97176"/></rect>
<rect x="616.0" y="124.29" width="15.16" height="15.16" fill="#ff9197" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4305" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4972;0.5638;0.6305;0.6972" values="#ff9197;#ff9197;#be8c7a;#a9837a;#a9837a"/></rect>
<rect x="630.86" y="124.29" width="15.16" height="15.16" fill="#ffa5aa" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4317" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4984;0.5650;0.6317;0.6984" values="#ffa5aa;#ffa5aa;#a79e7d;#9b977d;#9b977d"/></rect>
<rect x="571.43" y="139.14" width="15.16" height="15.16" fill="#ff7a82" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4281" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4947;0.5614;0.6281;0.6947" values="#ff7a82;#ff7a82;#ff7a82;#be6782;#be6782"/></rect>
<rect x="586.29" y="139.14" width="15.16" height="15.16" fill="#ff838b" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4293" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4960;0.5626;0.6293;0.6960" values="#ff838b;#ff838b;#e98281;#af6d81;#af6d81"/></rect>
<rect x="601.14" y="139.14" width="15.16" height="15.16" fill="#ff9097" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4305" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4972;0.5638;0.6305;0.6972" values="#ff9097;#ff9097;#d08d81;#a07981;#a07981"/></rect>
<rect x="616.0" y="139.14" width="15.16" height="15.16" fill="#ffa0a6" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4317" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4984;0.5650;0.6317;0.6984" values="#ffa0a6;#ffa0a6;#b79b82;#938882;#938882"/></rect>
<rect x="630.86" y="139.14" width="15.16" height="15.16" fill="#ffb2b7" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996;0.5662;0.6329;0.6996" values="#ffb2b7;#ffb2b7;#9eaa82;#859a82;#859a82"/></rect>
<rect x="586.29" y="154.0" width="15.16" height="15.16" fill="#ff999f" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4305" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4972;0.5638;0.6305;0.6972" values="#ff999f;#ff999f;#e69793;#977793;#977793"/></rect>
<rect x="601.14" y="154.0" width="15.16" height="15.16" fill="#ffa4a9" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4317" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4984;0.5650;0.6317;0.6984" values="#ffa4a9;#ffa4a9;#cca090;#8b8090;#8b8090"/></rect>
</g>
</g>
<circle cx="616.0" cy="121.31" r="49.03" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0923;0.0926;1.0000" values="0;0;1;1"/></circle>
<circle cx="616.0" cy="121.31" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0923;0.0926;1.0000" values="0;0;1;1"/></circle>
<text x="616.0" y="126.31" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0923;0.0926;1.0000" values="0;0;1;1"/></text>
<circle cx="616.0" cy="121.31" r="49.03" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g clip-path="url(#fd-sph-D2)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1256;0.1259;1.0000" values="0;0;1;1"/><rect x="809.14" y="50.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="50.0" width="5.15" height="15.16" fill="#440484"/>
<rect x="819.05" y="50.0" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="824.0" y="50.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="50.0" width="5.15" height="15.16" fill="#6c0498"/>
<rect x="833.9" y="50.0" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="838.86" y="50.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="50.0" width="5.15" height="15.16" fill="#930498"/>
<rect x="848.76" y="50.0" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="853.71" y="50.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="50.0" width="5.15" height="15.16" fill="#bb0484"/>
<rect x="863.62" y="50.0" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="794.29" y="64.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="799.24" y="64.86" width="5.15" height="15.16" fill="#1c2c84"/>
<rect x="804.19" y="64.86" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="809.14" y="64.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="64.86" width="5.15" height="15.16" fill="#442ccb"/>
<rect x="819.05" y="64.86" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="824.0" y="64.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="64.86" width="5.15" height="15.16" fill="#6c2cde"/>
<rect x="833.9" y="64.86" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="838.86" y="64.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="64.86" width="5.15" height="15.16" fill="#932cde"/>
<rect x="848.76" y="64.86" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="853.71" y="64.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="64.86" width="5.15" height="15.16" fill="#bb2ccb"/>
<rect x="863.62" y="64.86" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="868.57" y="64.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="64.86" width="5.15" height="15.16" fill="#e32c84"/>
<rect x="878.48" y="64.86" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="794.29" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="799.24" y="79.71" width="5.15" height="15.16" fill="#1c54c2"/>
<rect x="804.19" y="79.71" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="809.14" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="79.71" width="5.15" height="15.16" fill="#4454e7"/>
<rect x="819.05" y="79.71" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="824.0" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="79.71" width="5.15" height="15.16" fill="#6c54f6"/>
<rect x="833.9" y="79.71" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="838.86" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="79.71" width="5.15" height="15.16" fill="#9354f6"/>
<rect x="848.76" y="79.71" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="853.71" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="79.71" width="5.15" height="15.16" fill="#bb54e7"/>
<rect x="863.62" y="79.71" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="868.57" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="79.71" width="5.15" height="15.16" fill="#e354c2"/>
<rect x="878.48" y="79.71" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="794.29" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="799.24" y="94.57" width="5.15" height="15.16" fill="#1c7ccf"/>
<rect x="804.19" y="94.57" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="809.14" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="94.57" width="5.15" height="15.16" fill="#447cf0"/>
<rect x="819.05" y="94.57" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="824.0" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="94.57" width="5.15" height="15.16" fill="#6c7cfd"/>
<rect x="833.9" y="94.57" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="838.86" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="94.57" width="5.15" height="15.16" fill="#937cfd"/>
<rect x="848.76" y="94.57" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="853.71" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="94.57" width="5.15" height="15.16" fill="#bb7cf0"/>
<rect x="863.62" y="94.57" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="868.57" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="94.57" width="5.15" height="15.16" fill="#e37ccf"/>
<rect x="878.48" y="94.57" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="794.29" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="799.24" y="109.43" width="5.15" height="15.16" fill="#1ca3c7"/>
<rect x="804.19" y="109.43" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="809.14" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="109.43" width="5.15" height="15.16" fill="#44a3ea"/>
<rect x="819.05" y="109.43" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="824.0" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="109.43" width="5.15" height="15.16" fill="#6ca3f8"/>
<rect x="833.9" y="109.43" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="838.86" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="109.43" width="5.15" height="15.16" fill="#93a3f8"/>
<rect x="848.76" y="109.43" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="853.71" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="109.43" width="5.15" height="15.16" fill="#bba3ea"/>
<rect x="863.62" y="109.43" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="868.57" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="109.43" width="5.15" height="15.16" fill="#e3a3c7"/>
<rect x="878.48" y="109.43" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="794.29" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="799.24" y="124.29" width="5.15" height="15.16" fill="#1ccb98"/>
<rect x="804.19" y="124.29" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="809.14" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="124.29" width="5.15" height="15.16" fill="#44cbd3"/>
<rect x="819.05" y="124.29" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="824.0" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="124.29" width="5.15" height="15.16" fill="#6ccbe4"/>
<rect x="833.9" y="124.29" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="838.86" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="124.29" width="5.15" height="15.16" fill="#93cbe4"/>
<rect x="848.76" y="124.29" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="853.71" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="124.29" width="5.15" height="15.16" fill="#bbcbd3"/>
<rect x="863.62" y="124.29" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="868.57" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="124.29" width="5.15" height="15.16" fill="#e3cb98"/>
<rect x="878.48" y="124.29" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="809.14" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="139.14" width="5.15" height="15.16" fill="#44f384"/>
<rect x="819.05" y="139.14" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="824.0" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="139.14" width="5.15" height="15.16" fill="#6cf3b2"/>
<rect x="833.9" y="139.14" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="838.86" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="139.14" width="5.15" height="15.16" fill="#93f3b2"/>
<rect x="848.76" y="139.14" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="853.71" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="139.14" width="5.15" height="15.16" fill="#bbf384"/>
<rect x="863.62" y="139.14" width="5.15" height="15.16" fill="#aaaaaa"/>
</g>
<g><rect x="809.14" y="50.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5068;0.5735;0.6401;0.7068" values="#ffffff;#ffde6b;#ffde6b;#ffde6b;#ffde6b"/></rect>
<rect x="824.0" y="50.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5080;0.5747;0.6413;0.7080" values="#ffffff;#ffd953;#ffd953;#ffd953;#ffd953"/></rect>
<rect x="838.86" y="50.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5092;0.5759;0.6425;0.7092" values="#ffffff;#ffd43f;#ffd43f;#ffd43f;#ffd43f"/></rect>
<rect x="853.71" y="50.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5104;0.5771;0.6438;0.7104" values="#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="794.29" y="64.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5068;0.5735;0.6401;0.7068" values="#ffffff;#ffe27d;#e7e074;#e7e074;#e7e074"/></rect>
<rect x="809.14" y="64.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5080;0.5747;0.6413;0.7080" values="#ffffff;#ffdc62;#f8db60;#f8db60;#f8db60"/></rect>
<rect x="824.0" y="64.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5092;0.5759;0.6425;0.7092" values="#ffffff;#ffd648;#ffd648;#ffd648;#ffd648"/></rect>
<rect x="838.86" y="64.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5104;0.5771;0.6438;0.7104" values="#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="853.71" y="64.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5116;0.5783;0.6450;0.7116" values="#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="868.57" y="64.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5128;0.5795;0.6462;0.7128" values="#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="794.29" y="79.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5080;0.5747;0.6413;0.7080" values="#ffffff;#ffe27b;#d4dd6b;#d4dd6b;#d4dd6b"/></rect>
<rect x="809.14" y="79.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5092;0.5759;0.6425;0.7092" values="#ffffff;#ffdc60;#e7d959;#e7d959;#e7d959"/></rect>
<rect x="824.0" y="79.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5104;0.5771;0.6438;0.7104" values="#ffffff;#ffd645;#fbd544;#fbd544;#fbd544"/></rect>
<rect x="794.29" y="94.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5092;0.5759;0.6425;0.7092" values="#ffffff;#ffe380;#c2dc68;#c2dc68;#c2dc68"/></rect>
<rect x="809.14" y="94.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5104;0.5771;0.6438;0.7104" values="#ffffff;#ffdd65;#d7d959;#d7d959;#d7d959"/></rect>
<rect x="794.29" y="109.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5104;0.5771;0.6438;0.7104" values="#ffffff;#ffe589;#b3dd6a;#b3dd6a;#b3dd6a"/></rect>
<rect x="809.14" y="109.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5116;0.5783;0.6450;0.7116" values="#ffffff;#ffdf71;#c9da5f;#c9da5f;#c8d65f"/></rect>
<rect x="794.29" y="124.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5116;0.5783;0.6450;0.7116" values="#ffffff;#ffe897;#a7de6f;#a7de6f;#a4cf6f"/></rect>
<rect x="809.14" y="124.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5128;0.5795;0.6462;0.7128" values="#ffffff;#ffe381;#bedc68;#bedc68;#b9c668"/></rect>
<rect x="809.14" y="139.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5140;0.5807;0.6474;0.7140" values="#ffffff;#ffe795;#b7e074;#b7e074;#aeb674"/></rect>
<rect x="824.0" y="139.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5152;0.5819;0.6486;0.7152" values="#ffffff;#ffe484;#d0df72;#d0df72;#c4af72"/></rect>
</g>
</g>
<circle cx="838.86" cy="103.49" r="52.0" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1256;0.1259;1.0000" values="0;0;1;1"/></circle>
<circle cx="838.86" cy="103.49" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1256;0.1259;1.0000" values="0;0;1;1"/></circle>
<text x="838.86" y="108.49" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1256;0.1259;1.0000" values="0;0;1;1"/></text>
<circle cx="838.86" cy="103.49" r="52.0" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g clip-path="url(#fd-sph-D3)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1590;0.1593;1.0000" values="0;0;1;1"/><rect x="838.86" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="79.71" width="5.15" height="15.16" fill="#3b20b1"/>
<rect x="848.76" y="79.71" width="5.15" height="15.16" fill="#989898"/>
<rect x="853.71" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="79.71" width="5.15" height="15.16" fill="#6920d1"/>
<rect x="863.62" y="79.71" width="5.15" height="15.16" fill="#989898"/>
<rect x="868.57" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="79.71" width="5.15" height="15.16" fill="#9620d1"/>
<rect x="878.48" y="79.71" width="5.15" height="15.16" fill="#989898"/>
<rect x="883.43" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="888.38" y="79.71" width="5.15" height="15.16" fill="#c420b1"/>
<rect x="893.33" y="79.71" width="5.15" height="15.16" fill="#989898"/>
<rect x="824.0" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="94.57" width="5.15" height="15.16" fill="#0e4d9c"/>
<rect x="833.9" y="94.57" width="5.15" height="15.16" fill="#989898"/>
<rect x="838.86" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="94.57" width="5.15" height="15.16" fill="#3b4ddf"/>
<rect x="848.76" y="94.57" width="5.15" height="15.16" fill="#989898"/>
<rect x="853.71" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="94.57" width="5.15" height="15.16" fill="#694df3"/>
<rect x="863.62" y="94.57" width="5.15" height="15.16" fill="#989898"/>
<rect x="868.57" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="94.57" width="5.15" height="15.16" fill="#964df3"/>
<rect x="878.48" y="94.57" width="5.15" height="15.16" fill="#989898"/>
<rect x="883.43" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="888.38" y="94.57" width="5.15" height="15.16" fill="#c44ddf"/>
<rect x="893.33" y="94.57" width="5.15" height="15.16" fill="#989898"/>
<rect x="898.29" y="94.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="903.24" y="94.57" width="5.15" height="15.16" fill="#f14d9c"/>
<rect x="908.19" y="94.57" width="5.15" height="15.16" fill="#989898"/>
<rect x="824.0" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="109.43" width="5.15" height="15.16" fill="#0e7bb9"/>
<rect x="833.9" y="109.43" width="5.15" height="15.16" fill="#989898"/>
<rect x="838.86" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="109.43" width="5.15" height="15.16" fill="#3b7beb"/>
<rect x="848.76" y="109.43" width="5.15" height="15.16" fill="#989898"/>
<rect x="853.71" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="109.43" width="5.15" height="15.16" fill="#697bfd"/>
<rect x="863.62" y="109.43" width="5.15" height="15.16" fill="#989898"/>
<rect x="868.57" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="109.43" width="5.15" height="15.16" fill="#967bfd"/>
<rect x="878.48" y="109.43" width="5.15" height="15.16" fill="#989898"/>
<rect x="883.43" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="888.38" y="109.43" width="5.15" height="15.16" fill="#c47beb"/>
<rect x="893.33" y="109.43" width="5.15" height="15.16" fill="#989898"/>
<rect x="898.29" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="903.24" y="109.43" width="5.15" height="15.16" fill="#f17bb9"/>
<rect x="908.19" y="109.43" width="5.15" height="15.16" fill="#989898"/>
<rect x="824.0" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="124.29" width="5.15" height="15.16" fill="#0ea8a8"/>
<rect x="833.9" y="124.29" width="5.15" height="15.16" fill="#989898"/>
<rect x="838.86" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="124.29" width="5.15" height="15.16" fill="#3ba8e3"/>
<rect x="848.76" y="124.29" width="5.15" height="15.16" fill="#989898"/>
<rect x="853.71" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="124.29" width="5.15" height="15.16" fill="#69a8f6"/>
<rect x="863.62" y="124.29" width="5.15" height="15.16" fill="#989898"/>
<rect x="868.57" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="124.29" width="5.15" height="15.16" fill="#96a8f6"/>
<rect x="878.48" y="124.29" width="5.15" height="15.16" fill="#989898"/>
<rect x="883.43" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="888.38" y="124.29" width="5.15" height="15.16" fill="#c4a8e3"/>
<rect x="893.33" y="124.29" width="5.15" height="15.16" fill="#989898"/>
<rect x="898.29" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="903.24" y="124.29" width="5.15" height="15.16" fill="#f1a8a8"/>
<rect x="908.19" y="124.29" width="5.15" height="15.16" fill="#989898"/>
<rect x="838.86" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="139.14" width="5.15" height="15.16" fill="#3bd6c0"/>
<rect x="848.76" y="139.14" width="5.15" height="15.16" fill="#989898"/>
<rect x="853.71" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="139.14" width="5.15" height="15.16" fill="#69d6da"/>
<rect x="863.62" y="139.14" width="5.15" height="15.16" fill="#989898"/>
<rect x="868.57" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="139.14" width="5.15" height="15.16" fill="#96d6da"/>
<rect x="878.48" y="139.14" width="5.15" height="15.16" fill="#989898"/>
<rect x="883.43" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="888.38" y="139.14" width="5.15" height="15.16" fill="#c4d6c0"/>
<rect x="893.33" y="139.14" width="5.15" height="15.16" fill="#989898"/>
<rect x="853.71" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="154.0" width="5.15" height="15.16" fill="#69ff84"/>
<rect x="863.62" y="154.0" width="5.15" height="15.16" fill="#989898"/>
<rect x="868.57" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="154.0" width="5.15" height="15.16" fill="#96ff84"/>
<rect x="878.48" y="154.0" width="5.15" height="15.16" fill="#989898"/>
</g>
<g><rect x="838.86" y="79.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5116;0.5783;0.6450;0.7116" values="#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="853.71" y="79.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5128;0.5795;0.6462;0.7128" values="#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="868.57" y="79.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5140;0.5807;0.6474;0.7140" values="#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="883.43" y="79.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5152;0.5819;0.6486;0.7152" values="#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="824.0" y="94.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5116;0.5783;0.6450;0.7116" values="#ffffff;#ffd74c;#ecd548;#ecd548;#ecd548"/></rect>
<rect x="838.86" y="94.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5128;0.5795;0.6462;0.7128" values="#ffffff;#ffd235;#ffd235;#ffd235;#ffd235"/></rect>
<rect x="853.71" y="94.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5140;0.5807;0.6474;0.7140" values="#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="868.57" y="94.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5152;0.5819;0.6486;0.7152" values="#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="883.43" y="94.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5165;0.5831;0.6498;0.7165" values="#ffffff;#ffd130;#ffd130;#ffd130;#ffd130"/></rect>
<rect x="898.29" y="94.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5177;0.5843;0.6510;0.7177" values="#ffffff;#ffd645;#ffd645;#ffd645;#ffd645"/></rect>
<rect x="824.0" y="109.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5128;0.5795;0.6462;0.7128" values="#ffffff;#ffdb5b;#e0d752;#e0d752;#dece52"/></rect>
<rect x="838.86" y="109.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5140;0.5807;0.6474;0.7140" values="#ffffff;#ffd648;#f8d646;#f8d646;#f4c946"/></rect>
<rect x="853.71" y="109.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5152;0.5819;0.6486;0.7152" values="#ffffff;#ffd43c;#ffd43c;#ffd43c;#fbc63c"/></rect>
<rect x="868.57" y="109.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5165;0.5831;0.6498;0.7165" values="#ffffff;#ffd33a;#ffd33a;#ffd33a;#fbc73a"/></rect>
<rect x="883.43" y="109.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5177;0.5843;0.6510;0.7177" values="#ffffff;#ffd544;#ffd544;#ffd544;#fccd44"/></rect>
<rect x="898.29" y="109.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5189;0.5855;0.6522;0.7189" values="#ffffff;#ffd955;#ffd955;#ffd955;#fed655"/></rect>
<rect x="824.0" y="124.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5140;0.5807;0.6474;0.7140" values="#ffffff;#ffdf6e;#d6db61;#d6db61;#cfbe61"/></rect>
<rect x="838.86" y="124.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5152;0.5819;0.6486;0.7152" values="#ffffff;#ffdc5f;#efda5b;#efda5b;#e6ba5b"/></rect>
<rect x="853.71" y="124.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5165;0.5831;0.6498;0.7165" values="#ffffff;#ffd956;#ffd956;#ffd956;#f5b956"/></rect>
<rect x="868.57" y="124.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5177;0.5843;0.6510;0.7177" values="#ffffff;#ffd955;#ffd955;#ffd955;#f5ba55"/></rect>
<rect x="883.43" y="124.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5189;0.5855;0.6522;0.7189" values="#ffffff;#ffdb5c;#ffdb5c;#ffdb5c;#f6bf5c"/></rect>
<rect x="898.29" y="124.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4534" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5201;0.5867;0.6534;0.7201" values="#ffffff;#ffde69;#ffde69;#ffde69;#f8c869"/></rect>
<rect x="838.86" y="139.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5165;0.5831;0.6498;0.7165" values="#ffffff;#ffe178;#e9df70;#e9df70;#daab70"/></rect>
<rect x="853.71" y="139.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5177;0.5843;0.6510;0.7177" values="#ffffff;#ffdf71;#ffdf71;#ffdf71;#efaa71"/></rect>
<rect x="868.57" y="139.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5189;0.5855;0.6522;0.7189" values="#ffffff;#ffdf70;#ffdf70;#ffdf70;#efab70"/></rect>
<rect x="883.43" y="139.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4534" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5201;0.5867;0.6534;0.7201" values="#ffffff;#ffe075;#ffe075;#ffe075;#f1b175"/></rect>
<rect x="853.71" y="154.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5189;0.5855;0.6522;0.7189" values="#ffffff;#ffe58c;#ffe58c;#ffe58c;#e99a8c"/></rect>
<rect x="868.57" y="154.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4534" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5201;0.5867;0.6534;0.7201" values="#ffffff;#ffe58b;#ffe58b;#ffe58b;#e99c8b"/></rect>
</g>
</g>
<circle cx="868.57" cy="118.34" r="46.06" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1590;0.1593;1.0000" values="0;0;1;1"/></circle>
<circle cx="868.57" cy="118.34" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1590;0.1593;1.0000" values="0;0;1;1"/></circle>
<text x="868.57" y="123.34" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">4<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1590;0.1593;1.0000" values="0;0;1;1"/></text>
<circle cx="868.57" cy="118.34" r="46.06" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g clip-path="url(#fd-sph-D4)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;1.0000" values="0;0;1;1"/><rect x="660.57" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="665.52" y="109.43" width="5.15" height="15.16" fill="#320f84"/>
<rect x="670.48" y="109.43" width="5.15" height="15.16" fill="#878787"/>
<rect x="675.43" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="680.38" y="109.43" width="5.15" height="15.16" fill="#590faf"/>
<rect x="685.33" y="109.43" width="5.15" height="15.16" fill="#878787"/>
<rect x="690.29" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="695.24" y="109.43" width="5.15" height="15.16" fill="#800fbc"/>
<rect x="700.19" y="109.43" width="5.15" height="15.16" fill="#878787"/>
<rect x="705.14" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="710.1" y="109.43" width="5.15" height="15.16" fill="#a60faf"/>
<rect x="715.05" y="109.43" width="5.15" height="15.16" fill="#878787"/>
<rect x="720.0" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="724.95" y="109.43" width="5.15" height="15.16" fill="#cd0f84"/>
<rect x="729.9" y="109.43" width="5.15" height="15.16" fill="#878787"/>
<rect x="645.71" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="650.67" y="124.29" width="5.15" height="15.16" fill="#0c3684"/>
<rect x="655.62" y="124.29" width="5.15" height="15.16" fill="#878787"/>
<rect x="660.57" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="665.52" y="124.29" width="5.15" height="15.16" fill="#3236c5"/>
<rect x="670.48" y="124.29" width="5.15" height="15.16" fill="#878787"/>
<rect x="675.43" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="680.38" y="124.29" width="5.15" height="15.16" fill="#5936e0"/>
<rect x="685.33" y="124.29" width="5.15" height="15.16" fill="#878787"/>
<rect x="690.29" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="695.24" y="124.29" width="5.15" height="15.16" fill="#8036e8"/>
<rect x="700.19" y="124.29" width="5.15" height="15.16" fill="#878787"/>
<rect x="705.14" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="710.1" y="124.29" width="5.15" height="15.16" fill="#a636e0"/>
<rect x="715.05" y="124.29" width="5.15" height="15.16" fill="#878787"/>
<rect x="720.0" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="724.95" y="124.29" width="5.15" height="15.16" fill="#cd36c5"/>
<rect x="729.9" y="124.29" width="5.15" height="15.16" fill="#878787"/>
<rect x="734.86" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="739.81" y="124.29" width="5.15" height="15.16" fill="#f33684"/>
<rect x="744.76" y="124.29" width="5.15" height="15.16" fill="#878787"/>
<rect x="645.71" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="650.67" y="139.14" width="5.15" height="15.16" fill="#0c5da8"/>
<rect x="655.62" y="139.14" width="5.15" height="15.16" fill="#878787"/>
<rect x="660.57" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="665.52" y="139.14" width="5.15" height="15.16" fill="#325ddf"/>
<rect x="670.48" y="139.14" width="5.15" height="15.16" fill="#878787"/>
<rect x="675.43" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="680.38" y="139.14" width="5.15" height="15.16" fill="#595df4"/>
<rect x="685.33" y="139.14" width="5.15" height="15.16" fill="#878787"/>
<rect x="690.29" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="695.24" y="139.14" width="5.15" height="15.16" fill="#805dfa"/>
<rect x="700.19" y="139.14" width="5.15" height="15.16" fill="#878787"/>
<rect x="705.14" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="710.1" y="139.14" width="5.15" height="15.16" fill="#a65df4"/>
<rect x="715.05" y="139.14" width="5.15" height="15.16" fill="#878787"/>
<rect x="720.0" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="724.95" y="139.14" width="5.15" height="15.16" fill="#cd5ddf"/>
<rect x="729.9" y="139.14" width="5.15" height="15.16" fill="#878787"/>
<rect x="734.86" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="739.81" y="139.14" width="5.15" height="15.16" fill="#f35da8"/>
<rect x="744.76" y="139.14" width="5.15" height="15.16" fill="#878787"/>
<rect x="645.71" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="650.67" y="154.0" width="5.15" height="15.16" fill="#0c83b4"/>
<rect x="655.62" y="154.0" width="5.15" height="15.16" fill="#878787"/>
<rect x="660.57" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="665.52" y="154.0" width="5.15" height="15.16" fill="#3283e5"/>
<rect x="670.48" y="154.0" width="5.15" height="15.16" fill="#878787"/>
<rect x="675.43" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="680.38" y="154.0" width="5.15" height="15.16" fill="#5983f9"/>
<rect x="685.33" y="154.0" width="5.15" height="15.16" fill="#878787"/>
<rect x="690.29" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="695.24" y="154.0" width="5.15" height="15.16" fill="#8083ff"/>
<rect x="700.19" y="154.0" width="5.15" height="15.16" fill="#878787"/>
<rect x="705.14" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="710.1" y="154.0" width="5.15" height="15.16" fill="#a683f9"/>
<rect x="715.05" y="154.0" width="5.15" height="15.16" fill="#878787"/>
<rect x="720.0" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="724.95" y="154.0" width="5.15" height="15.16" fill="#cd83e5"/>
<rect x="729.9" y="154.0" width="5.15" height="15.16" fill="#878787"/>
<rect x="734.86" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="739.81" y="154.0" width="5.15" height="15.16" fill="#f383b4"/>
<rect x="744.76" y="154.0" width="5.15" height="15.16" fill="#878787"/>
<rect x="645.71" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="650.67" y="168.86" width="5.15" height="15.16" fill="#0caa9f"/>
<rect x="655.62" y="168.86" width="5.15" height="15.16" fill="#878787"/>
<rect x="660.57" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="665.52" y="168.86" width="5.15" height="15.16" fill="#32aadc"/>
<rect x="670.48" y="168.86" width="5.15" height="15.16" fill="#878787"/>
<rect x="675.43" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="680.38" y="168.86" width="5.15" height="15.16" fill="#59aaf1"/>
<rect x="685.33" y="168.86" width="5.15" height="15.16" fill="#878787"/>
<rect x="690.29" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="695.24" y="168.86" width="5.15" height="15.16" fill="#80aaf8"/>
<rect x="700.19" y="168.86" width="5.15" height="15.16" fill="#878787"/>
<rect x="705.14" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="710.1" y="168.86" width="5.15" height="15.16" fill="#a6aaf1"/>
<rect x="715.05" y="168.86" width="5.15" height="15.16" fill="#878787"/>
<rect x="720.0" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="724.95" y="168.86" width="5.15" height="15.16" fill="#cdaadc"/>
<rect x="729.9" y="168.86" width="5.15" height="15.16" fill="#878787"/>
<rect x="734.86" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="739.81" y="168.86" width="5.15" height="15.16" fill="#f3aa9f"/>
<rect x="744.76" y="168.86" width="5.15" height="15.16" fill="#878787"/>
<rect x="660.57" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="665.52" y="183.71" width="5.15" height="15.16" fill="#32d1bc"/>
<rect x="670.48" y="183.71" width="5.15" height="15.16" fill="#878787"/>
<rect x="675.43" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="680.38" y="183.71" width="5.15" height="15.16" fill="#59d1da"/>
<rect x="685.33" y="183.71" width="5.15" height="15.16" fill="#878787"/>
<rect x="690.29" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="695.24" y="183.71" width="5.15" height="15.16" fill="#80d1e2"/>
<rect x="700.19" y="183.71" width="5.15" height="15.16" fill="#878787"/>
<rect x="705.14" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="710.1" y="183.71" width="5.15" height="15.16" fill="#a6d1da"/>
<rect x="715.05" y="183.71" width="5.15" height="15.16" fill="#878787"/>
<rect x="720.0" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="724.95" y="183.71" width="5.15" height="15.16" fill="#cdd1bc"/>
<rect x="729.9" y="183.71" width="5.15" height="15.16" fill="#878787"/>
<rect x="675.43" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="680.38" y="198.57" width="5.15" height="15.16" fill="#59f794"/>
<rect x="685.33" y="198.57" width="5.15" height="15.16" fill="#878787"/>
<rect x="690.29" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="695.24" y="198.57" width="5.15" height="15.16" fill="#80f7ab"/>
<rect x="700.19" y="198.57" width="5.15" height="15.16" fill="#878787"/>
<rect x="705.14" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="710.1" y="198.57" width="5.15" height="15.16" fill="#a6f794"/>
<rect x="715.05" y="198.57" width="5.15" height="15.16" fill="#878787"/>
</g>
<g><rect x="660.57" y="109.43" width="15.16" height="15.16" fill="#ffc9cc" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996;0.5662;0.6329;0.6996" values="#ffc9cc;#ffc9cc;#8bbe85;#8bbe85;#8bbe85"/></rect>
<rect x="675.43" y="109.43" width="15.16" height="15.16" fill="#ffe0e2" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5008;0.5674;0.6341;0.7008" values="#ffe0e2;#ffe0e2;#7bd288;#7bd288;#7bd288"/></rect>
<rect x="690.29" y="109.43" width="15.16" height="15.16" fill="#fff8f8" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5020;0.5686;0.6353;0.7020" values="#fff8f8;#fff8f8;#6ee78c;#6ee78c;#6ee78c"/></rect>
<rect x="705.14" y="109.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5032;0.5699;0.6365;0.7032" values="#ffffff;#ffffff;#67ed8b;#67ed8b;#67ed8b"/></rect>
<rect x="720.0" y="109.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5044;0.5711;0.6377;0.7044" values="#ffffff;#ffffff;#67ed8b;#67ed8b;#67ed8b"/></rect>
<rect x="645.71" y="124.29" width="15.16" height="15.16" fill="#ffbabf" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996;0.5662;0.6329;0.6996" values="#ffbabf;#ffbabf;#90b17f;#8cae7f;#8cae7f"/></rect>
<rect x="660.57" y="124.29" width="15.16" height="15.16" fill="#ffd0d3" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5008;0.5674;0.6341;0.7008" values="#ffd0d3;#ffd0d3;#7ac47f;#7ac47f;#7ac47f"/></rect>
<rect x="675.43" y="124.29" width="15.16" height="15.16" fill="#ffe7e8" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5020;0.5686;0.6353;0.7020" values="#ffe7e8;#ffe7e8;#67d77e;#67d77e;#67d77e"/></rect>
<rect x="690.29" y="124.29" width="15.16" height="15.16" fill="#fffefe" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5032;0.5699;0.6365;0.7032" values="#fffefe;#fffefe;#57ea7e;#57ea7e;#57ea7e"/></rect>
<rect x="645.71" y="139.14" width="15.16" height="15.16" fill="#ffc6ca" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5008;0.5674;0.6341;0.7008" values="#ffc6ca;#ffc6ca;#85bb80;#78af80;#78af80"/></rect>
<rect x="660.57" y="139.14" width="15.16" height="15.16" fill="#ffdbdd" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5020;0.5686;0.6353;0.7020" values="#ffdbdd;#ffdbdd;#6dcc7d;#69c67d;#69c67d"/></rect>
<rect x="675.43" y="139.14" width="15.16" height="15.16" fill="#fff0f1" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5032;0.5699;0.6365;0.7032" values="#fff0f1;#fff0f1;#57de77;#57de77;#57de77"/></rect>
<rect x="645.71" y="154.0" width="15.16" height="15.16" fill="#ffd4d7" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5020;0.5686;0.6353;0.7020" values="#ffd4d7;#ffd4d7;#80c885;#69b285;#69b285"/></rect>
<rect x="660.57" y="154.0" width="15.16" height="15.16" fill="#ffe8e9" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5032;0.5699;0.6365;0.7032" values="#ffe8e9;#ffe8e9;#66d77e;#5bc87e;#5bc87e"/></rect>
<rect x="675.43" y="154.0" width="15.16" height="15.16" fill="#fffcfc" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5044;0.5711;0.6377;0.7044" values="#fffcfc;#fffcfc;#4de775;#4ae175;#4ae175"/></rect>
<rect x="660.57" y="168.86" width="15.16" height="15.16" fill="#fff6f7" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5044;0.5711;0.6377;0.7044" values="#fff6f7;#fff6f7;#66e585;#54cc85;#54cc85"/></rect>
<rect x="675.43" y="168.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5056;0.5723;0.6389;0.7056" values="#ffffff;#ffffff;#4cea76;#45db76;#45db76"/></rect>
<rect x="675.43" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5068;0.5735;0.6401;0.7068" values="#ffffff;#ffffff;#55eb7d;#49d57d;#49d57d"/></rect>
<rect x="675.43" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5080;0.5747;0.6413;0.7080" values="#ffffff;#ffffff;#65ed89;#52d189;#52d189"/></rect>
<rect x="690.29" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5092;0.5759;0.6425;0.7092" values="#ffffff;#ffffff;#55eb7d;#4cdc7d;#4cdc7d"/></rect>
</g>
</g>
<circle cx="697.71" cy="159.94" r="53.49" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;1.0000" values="0;0;1;1"/></circle>
<circle cx="697.71" cy="159.94" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;1.0000" values="0;0;1;1"/></circle>
<text x="697.71" y="164.94" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">5<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;1.0000" values="0;0;1;1"/></text>
<circle cx="697.71" cy="159.94" r="53.49" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g clip-path="url(#fd-sph-D5)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2256;0.2259;1.0000" values="0;0;1;1"/><rect x="705.14" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="710.1" y="124.29" width="5.15" height="15.16" fill="#40159e"/>
<rect x="715.05" y="124.29" width="5.15" height="15.16" fill="#767676"/>
<rect x="720.0" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="724.95" y="124.29" width="5.15" height="15.16" fill="#6a15c3"/>
<rect x="729.9" y="124.29" width="5.15" height="15.16" fill="#767676"/>
<rect x="734.86" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="739.81" y="124.29" width="5.15" height="15.16" fill="#9515c3"/>
<rect x="744.76" y="124.29" width="5.15" height="15.16" fill="#767676"/>
<rect x="749.71" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="754.67" y="124.29" width="5.15" height="15.16" fill="#bf159e"/>
<rect x="759.62" y="124.29" width="5.15" height="15.16" fill="#767676"/>
<rect x="690.29" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="695.24" y="139.14" width="5.15" height="15.16" fill="#15409e"/>
<rect x="700.19" y="139.14" width="5.15" height="15.16" fill="#767676"/>
<rect x="705.14" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="710.1" y="139.14" width="5.15" height="15.16" fill="#4040da"/>
<rect x="715.05" y="139.14" width="5.15" height="15.16" fill="#767676"/>
<rect x="720.0" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="724.95" y="139.14" width="5.15" height="15.16" fill="#6a40ec"/>
<rect x="729.9" y="139.14" width="5.15" height="15.16" fill="#767676"/>
<rect x="734.86" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="739.81" y="139.14" width="5.15" height="15.16" fill="#9540ec"/>
<rect x="744.76" y="139.14" width="5.15" height="15.16" fill="#767676"/>
<rect x="749.71" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="754.67" y="139.14" width="5.15" height="15.16" fill="#bf40da"/>
<rect x="759.62" y="139.14" width="5.15" height="15.16" fill="#767676"/>
<rect x="764.57" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="769.52" y="139.14" width="5.15" height="15.16" fill="#ea409e"/>
<rect x="774.48" y="139.14" width="5.15" height="15.16" fill="#767676"/>
<rect x="690.29" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="695.24" y="154.0" width="5.15" height="15.16" fill="#156ac3"/>
<rect x="700.19" y="154.0" width="5.15" height="15.16" fill="#767676"/>
<rect x="705.14" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="710.1" y="154.0" width="5.15" height="15.16" fill="#406aec"/>
<rect x="715.05" y="154.0" width="5.15" height="15.16" fill="#767676"/>
<rect x="720.0" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="724.95" y="154.0" width="5.15" height="15.16" fill="#6a6afb"/>
<rect x="729.9" y="154.0" width="5.15" height="15.16" fill="#767676"/>
<rect x="734.86" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="739.81" y="154.0" width="5.15" height="15.16" fill="#956afb"/>
<rect x="744.76" y="154.0" width="5.15" height="15.16" fill="#767676"/>
<rect x="749.71" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="754.67" y="154.0" width="5.15" height="15.16" fill="#bf6aec"/>
<rect x="759.62" y="154.0" width="5.15" height="15.16" fill="#767676"/>
<rect x="764.57" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="769.52" y="154.0" width="5.15" height="15.16" fill="#ea6ac3"/>
<rect x="774.48" y="154.0" width="5.15" height="15.16" fill="#767676"/>
<rect x="690.29" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="695.24" y="168.86" width="5.15" height="15.16" fill="#1595c3"/>
<rect x="700.19" y="168.86" width="5.15" height="15.16" fill="#767676"/>
<rect x="705.14" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="710.1" y="168.86" width="5.15" height="15.16" fill="#4095ec"/>
<rect x="715.05" y="168.86" width="5.15" height="15.16" fill="#767676"/>
<rect x="720.0" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="724.95" y="168.86" width="5.15" height="15.16" fill="#6a95fb"/>
<rect x="729.9" y="168.86" width="5.15" height="15.16" fill="#767676"/>
<rect x="734.86" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="739.81" y="168.86" width="5.15" height="15.16" fill="#9595fb"/>
<rect x="744.76" y="168.86" width="5.15" height="15.16" fill="#767676"/>
<rect x="749.71" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="754.67" y="168.86" width="5.15" height="15.16" fill="#bf95ec"/>
<rect x="759.62" y="168.86" width="5.15" height="15.16" fill="#767676"/>
<rect x="764.57" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="769.52" y="168.86" width="5.15" height="15.16" fill="#ea95c3"/>
<rect x="774.48" y="168.86" width="5.15" height="15.16" fill="#767676"/>
<rect x="690.29" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="695.24" y="183.71" width="5.15" height="15.16" fill="#15bf9e"/>
<rect x="700.19" y="183.71" width="5.15" height="15.16" fill="#767676"/>
<rect x="705.14" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="710.1" y="183.71" width="5.15" height="15.16" fill="#40bfda"/>
<rect x="715.05" y="183.71" width="5.15" height="15.16" fill="#767676"/>
<rect x="720.0" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="724.95" y="183.71" width="5.15" height="15.16" fill="#6abfec"/>
<rect x="729.9" y="183.71" width="5.15" height="15.16" fill="#767676"/>
<rect x="734.86" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="739.81" y="183.71" width="5.15" height="15.16" fill="#95bfec"/>
<rect x="744.76" y="183.71" width="5.15" height="15.16" fill="#767676"/>
<rect x="749.71" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="754.67" y="183.71" width="5.15" height="15.16" fill="#bfbfda"/>
<rect x="759.62" y="183.71" width="5.15" height="15.16" fill="#767676"/>
<rect x="764.57" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="769.52" y="183.71" width="5.15" height="15.16" fill="#eabf9e"/>
<rect x="774.48" y="183.71" width="5.15" height="15.16" fill="#767676"/>
<rect x="705.14" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="710.1" y="198.57" width="5.15" height="15.16" fill="#40ea9e"/>
<rect x="715.05" y="198.57" width="5.15" height="15.16" fill="#767676"/>
<rect x="720.0" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="724.95" y="198.57" width="5.15" height="15.16" fill="#6aeac3"/>
<rect x="729.9" y="198.57" width="5.15" height="15.16" fill="#767676"/>
<rect x="734.86" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="739.81" y="198.57" width="5.15" height="15.16" fill="#95eac3"/>
<rect x="744.76" y="198.57" width="5.15" height="15.16" fill="#767676"/>
<rect x="749.71" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="754.67" y="198.57" width="5.15" height="15.16" fill="#bfea9e"/>
<rect x="759.62" y="198.57" width="5.15" height="15.16" fill="#767676"/>
</g>
<g><rect x="705.14" y="124.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5044;0.5711;0.6377;0.7044" values="#ffffff;#ffffff;#4eea78;#4eea78;#4eea78"/></rect>
<rect x="720.0" y="124.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5056;0.5723;0.6389;0.7056" values="#ffffff;#ffffff;#4eea78;#4eea78;#4eea78"/></rect>
<rect x="734.86" y="124.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5068;0.5735;0.6401;0.7068" values="#ffffff;#fffdf8;#57ea7b;#57ea7b;#57ea7b"/></rect>
<rect x="749.71" y="124.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5080;0.5747;0.6413;0.7080" values="#ffffff;#fff8de;#67e679;#67e679;#67e679"/></rect>
<rect x="690.29" y="139.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5044;0.5711;0.6377;0.7044" values="#ffffff;#ffffff;#43e96f;#43e96f;#43e96f"/></rect>
<rect x="705.14" y="139.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5056;0.5723;0.6389;0.7056" values="#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="720.0" y="139.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5068;0.5735;0.6401;0.7068" values="#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="734.86" y="139.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5080;0.5747;0.6413;0.7080" values="#ffffff;#ffffff;#43e96f;#43e96f;#43e96f"/></rect>
<rect x="749.71" y="139.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5092;0.5759;0.6425;0.7092" values="#ffffff;#fffaea;#57e774;#57e774;#57e774"/></rect>
<rect x="764.57" y="139.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5104;0.5771;0.6438;0.7104" values="#ffffff;#fff5d3;#6de577;#6de577;#6cdb77"/></rect>
<rect x="690.29" y="154.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5056;0.5723;0.6389;0.7056" values="#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="705.14" y="154.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5068;0.5735;0.6401;0.7068" values="#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="720.0" y="154.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5080;0.5747;0.6413;0.7080" values="#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="734.86" y="154.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5092;0.5759;0.6425;0.7092" values="#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="749.71" y="154.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5104;0.5771;0.6438;0.7104" values="#ffffff;#fffef9;#4de974;#4de974;#4cdf74"/></rect>
<rect x="764.57" y="154.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5116;0.5783;0.6450;0.7116" values="#ffffff;#fff9e3;#66e77b;#66e77b;#63cf7b"/></rect>
<rect x="690.29" y="168.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5068;0.5735;0.6401;0.7068" values="#ffffff;#ffffff;#3ce86a;#3be56a;#3be56a"/></rect>
<rect x="705.14" y="168.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5080;0.5747;0.6413;0.7080" values="#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="720.0" y="168.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5092;0.5759;0.6425;0.7092" values="#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="734.86" y="168.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5104;0.5771;0.6438;0.7104" values="#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce46a"/></rect>
<rect x="749.71" y="168.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5116;0.5783;0.6450;0.7116" values="#ffffff;#ffffff;#4cea76;#4cea76;#4ad476"/></rect>
<rect x="764.57" y="168.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5128;0.5795;0.6462;0.7128" values="#ffffff;#fffdf4;#66eb84;#66eb84;#61c484"/></rect>
<rect x="690.29" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5080;0.5747;0.6413;0.7080" values="#ffffff;#ffffff;#41e96d;#3cdf6d;#3cdf6d"/></rect>
<rect x="705.14" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5092;0.5759;0.6425;0.7092" values="#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="720.0" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5104;0.5771;0.6438;0.7104" values="#ffffff;#ffffff;#3ce86a;#3ce86a;#3ce86a"/></rect>
<rect x="734.86" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5116;0.5783;0.6450;0.7116" values="#ffffff;#ffffff;#41e96d;#41e96d;#40da6d"/></rect>
<rect x="749.71" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5128;0.5795;0.6462;0.7128" values="#ffffff;#ffffff;#55eb7d;#55eb7d;#52ca7d"/></rect>
<rect x="764.57" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5140;0.5807;0.6474;0.7140" values="#ffffff;#ffffff;#6cee8f;#6cee8f;#66ba8f"/></rect>
<rect x="705.14" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5104;0.5771;0.6438;0.7104" values="#ffffff;#ffffff;#4bea76;#4ae876;#4ae876"/></rect>
<rect x="720.0" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5116;0.5783;0.6450;0.7116" values="#ffffff;#ffffff;#4bea76;#4bea76;#4be776"/></rect>
<rect x="734.86" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5128;0.5795;0.6462;0.7128" values="#ffffff;#ffffff;#55eb7d;#55eb7d;#53d57d"/></rect>
<rect x="749.71" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5140;0.5807;0.6474;0.7140" values="#ffffff;#ffffff;#65ed89;#65ed89;#60c389"/></rect>
</g>
</g>
<circle cx="734.86" cy="168.86" r="49.03" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2256;0.2259;1.0000" values="0;0;1;1"/></circle>
<circle cx="734.86" cy="168.86" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2256;0.2259;1.0000" values="0;0;1;1"/></circle>
<text x="734.86" y="173.86" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">6<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2256;0.2259;1.0000" values="0;0;1;1"/></text>
<circle cx="734.86" cy="168.86" r="49.03" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g clip-path="url(#fd-sph-D6)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;1.0000" values="0;0;1;1"/><rect x="556.57" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="561.52" y="183.71" width="5.15" height="15.16" fill="#261584"/>
<rect x="566.48" y="183.71" width="5.15" height="15.16" fill="#646464"/>
<rect x="571.43" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="183.71" width="5.15" height="15.16" fill="#5115b4"/>
<rect x="581.33" y="183.71" width="5.15" height="15.16" fill="#646464"/>
<rect x="586.29" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="183.71" width="5.15" height="15.16" fill="#7b15c6"/>
<rect x="596.19" y="183.71" width="5.15" height="15.16" fill="#646464"/>
<rect x="601.14" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="183.71" width="5.15" height="15.16" fill="#a615bb"/>
<rect x="611.05" y="183.71" width="5.15" height="15.16" fill="#646464"/>
<rect x="616.0" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="183.71" width="5.15" height="15.16" fill="#d01584"/>
<rect x="625.9" y="183.71" width="5.15" height="15.16" fill="#646464"/>
<rect x="556.57" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="561.52" y="198.57" width="5.15" height="15.16" fill="#2640c1"/>
<rect x="566.48" y="198.57" width="5.15" height="15.16" fill="#646464"/>
<rect x="571.43" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="198.57" width="5.15" height="15.16" fill="#5140e4"/>
<rect x="581.33" y="198.57" width="5.15" height="15.16" fill="#646464"/>
<rect x="586.29" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="198.57" width="5.15" height="15.16" fill="#7b40ee"/>
<rect x="596.19" y="198.57" width="5.15" height="15.16" fill="#646464"/>
<rect x="601.14" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="198.57" width="5.15" height="15.16" fill="#a640e7"/>
<rect x="611.05" y="198.57" width="5.15" height="15.16" fill="#646464"/>
<rect x="616.0" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="198.57" width="5.15" height="15.16" fill="#d040cb"/>
<rect x="625.9" y="198.57" width="5.15" height="15.16" fill="#646464"/>
<rect x="630.86" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="198.57" width="5.15" height="15.16" fill="#fb4084"/>
<rect x="640.76" y="198.57" width="5.15" height="15.16" fill="#646464"/>
<rect x="541.71" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="546.67" y="213.43" width="5.15" height="15.16" fill="#006a84"/>
<rect x="551.62" y="213.43" width="5.15" height="15.16" fill="#646464"/>
<rect x="556.57" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="561.52" y="213.43" width="5.15" height="15.16" fill="#266ad8"/>
<rect x="566.48" y="213.43" width="5.15" height="15.16" fill="#646464"/>
<rect x="571.43" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="213.43" width="5.15" height="15.16" fill="#516af4"/>
<rect x="581.33" y="213.43" width="5.15" height="15.16" fill="#646464"/>
<rect x="586.29" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="213.43" width="5.15" height="15.16" fill="#7b6afd"/>
<rect x="596.19" y="213.43" width="5.15" height="15.16" fill="#646464"/>
<rect x="601.14" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="213.43" width="5.15" height="15.16" fill="#a66af7"/>
<rect x="611.05" y="213.43" width="5.15" height="15.16" fill="#646464"/>
<rect x="616.0" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="213.43" width="5.15" height="15.16" fill="#d06ae0"/>
<rect x="625.9" y="213.43" width="5.15" height="15.16" fill="#646464"/>
<rect x="630.86" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="213.43" width="5.15" height="15.16" fill="#fb6a98"/>
<rect x="640.76" y="213.43" width="5.15" height="15.16" fill="#646464"/>
<rect x="541.71" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="546.67" y="228.29" width="5.15" height="15.16" fill="#009584"/>
<rect x="551.62" y="228.29" width="5.15" height="15.16" fill="#646464"/>
<rect x="556.57" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="561.52" y="228.29" width="5.15" height="15.16" fill="#2695d8"/>
<rect x="566.48" y="228.29" width="5.15" height="15.16" fill="#646464"/>
<rect x="571.43" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="228.29" width="5.15" height="15.16" fill="#5195f4"/>
<rect x="581.33" y="228.29" width="5.15" height="15.16" fill="#646464"/>
<rect x="586.29" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="228.29" width="5.15" height="15.16" fill="#7b95fd"/>
<rect x="596.19" y="228.29" width="5.15" height="15.16" fill="#646464"/>
<rect x="601.14" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="228.29" width="5.15" height="15.16" fill="#a695f7"/>
<rect x="611.05" y="228.29" width="5.15" height="15.16" fill="#646464"/>
<rect x="616.0" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="228.29" width="5.15" height="15.16" fill="#d095e0"/>
<rect x="625.9" y="228.29" width="5.15" height="15.16" fill="#646464"/>
<rect x="630.86" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="228.29" width="5.15" height="15.16" fill="#fb9598"/>
<rect x="640.76" y="228.29" width="5.15" height="15.16" fill="#646464"/>
<rect x="556.57" y="243.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="561.52" y="243.14" width="5.15" height="15.16" fill="#26bfc1"/>
<rect x="566.48" y="243.14" width="5.15" height="15.16" fill="#646464"/>
<rect x="571.43" y="243.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="243.14" width="5.15" height="15.16" fill="#51bfe4"/>
<rect x="581.33" y="243.14" width="5.15" height="15.16" fill="#646464"/>
<rect x="586.29" y="243.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="243.14" width="5.15" height="15.16" fill="#7bbfee"/>
<rect x="596.19" y="243.14" width="5.15" height="15.16" fill="#646464"/>
<rect x="601.14" y="243.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="243.14" width="5.15" height="15.16" fill="#a6bfe7"/>
<rect x="611.05" y="243.14" width="5.15" height="15.16" fill="#646464"/>
<rect x="616.0" y="243.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="243.14" width="5.15" height="15.16" fill="#d0bfcb"/>
<rect x="625.9" y="243.14" width="5.15" height="15.16" fill="#646464"/>
<rect x="630.86" y="243.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="243.14" width="5.15" height="15.16" fill="#fbbf84"/>
<rect x="640.76" y="243.14" width="5.15" height="15.16" fill="#646464"/>
<rect x="556.57" y="258.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="561.52" y="258.0" width="5.15" height="15.16" fill="#26ea84"/>
<rect x="566.48" y="258.0" width="5.15" height="15.16" fill="#646464"/>
<rect x="571.43" y="258.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="258.0" width="5.15" height="15.16" fill="#51eab4"/>
<rect x="581.33" y="258.0" width="5.15" height="15.16" fill="#646464"/>
<rect x="586.29" y="258.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="258.0" width="5.15" height="15.16" fill="#7beac6"/>
<rect x="596.19" y="258.0" width="5.15" height="15.16" fill="#646464"/>
<rect x="601.14" y="258.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="258.0" width="5.15" height="15.16" fill="#a6eabb"/>
<rect x="611.05" y="258.0" width="5.15" height="15.16" fill="#646464"/>
<rect x="616.0" y="258.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="258.0" width="5.15" height="15.16" fill="#d0ea84"/>
<rect x="625.9" y="258.0" width="5.15" height="15.16" fill="#646464"/>
</g>
<g><rect x="556.57" y="183.71" width="15.16" height="15.16" fill="#ffc0c4" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4305" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4972;0.5638;0.6305;0.6972" values="#ffc0c4;#ffc0c4;#ffc0c4;#7981c4;#7981c4"/></rect>
<rect x="571.43" y="183.71" width="15.16" height="15.16" fill="#ffc1c5" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4317" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4984;0.5650;0.6317;0.6984" values="#ffc1c5;#ffc1c5;#ffc1c5;#7580c5;#7580c5"/></rect>
<rect x="556.57" y="198.57" width="15.16" height="15.16" fill="#ffd8da" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4317" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4984;0.5650;0.6317;0.6984" values="#ffd8da;#ffd8da;#ffd8da;#6285da;#6285da"/></rect>
<rect x="571.43" y="198.57" width="15.16" height="15.16" fill="#ffd9dc" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996;0.5662;0.6329;0.6996" values="#ffd9dc;#ffd9dc;#ffd9dc;#5d83dc;#5d83dc"/></rect>
<rect x="541.71" y="213.43" width="15.16" height="15.16" fill="#fff1f2" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4317" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4984;0.5650;0.6317;0.6984" values="#fff1f2;#fff1f2;#fff1f2;#5b91f2;#5b91f2"/></rect>
<rect x="556.57" y="213.43" width="15.16" height="15.16" fill="#fff0f1" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996;0.5662;0.6329;0.6996" values="#fff0f1;#fff0f1;#fff0f1;#4c87f1;#4c87f1"/></rect>
<rect x="571.43" y="213.43" width="15.16" height="15.16" fill="#fff1f2" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5008;0.5674;0.6341;0.7008" values="#fff1f2;#fff1f2;#fff1f2;#4785f2;#4785f2"/></rect>
<rect x="541.71" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996;0.5662;0.6329;0.6996" values="#ffffff;#ffffff;#ffffff;#4f91ff;#4f91ff"/></rect>
<rect x="556.57" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5008;0.5674;0.6341;0.7008" values="#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="571.43" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5020;0.5686;0.6353;0.7020" values="#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="556.57" y="243.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5020;0.5686;0.6353;0.7020" values="#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="571.43" y="243.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5032;0.5699;0.6365;0.7032" values="#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="586.29" y="243.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5044;0.5711;0.6377;0.7044" values="#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="601.14" y="243.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5056;0.5723;0.6389;0.7056" values="#ffffff;#ffffff;#f9fefb;#478dfb;#478dfb"/></rect>
<rect x="616.0" y="243.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5068;0.5735;0.6401;0.7068" values="#ffffff;#ffffff;#e5fceb;#579aeb;#579aeb"/></rect>
<rect x="630.86" y="243.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5080;0.5747;0.6413;0.7080" values="#ffffff;#ffffff;#d2fadd;#64a8dd;#64a8dd"/></rect>
<rect x="556.57" y="258.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5032;0.5699;0.6365;0.7032" values="#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="571.43" y="258.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5044;0.5711;0.6377;0.7044" values="#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="586.29" y="258.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5056;0.5723;0.6389;0.7056" values="#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="601.14" y="258.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5068;0.5735;0.6401;0.7068" values="#ffffff;#ffffff;#ffffff;#5192ff;#5192ff"/></rect>
<rect x="616.0" y="258.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5080;0.5747;0.6413;0.7080" values="#ffffff;#ffffff;#f6fef8;#639ff8;#639ff8"/></rect>
</g>
</g>
<circle cx="595.2" cy="228.29" r="49.03" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;1.0000" values="0;0;1;1"/></circle>
<circle cx="595.2" cy="228.29" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;1.0000" values="0;0;1;1"/></circle>
<text x="595.2" y="233.29" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">7<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;1.0000" values="0;0;1;1"/></text>
<circle cx="595.2" cy="228.29" r="49.03" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g clip-path="url(#fd-sph-D7)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2923;0.2926;1.0000" values="0;0;1;1"/><rect x="616.0" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="154.0" width="5.15" height="15.16" fill="#7b0084"/>
<rect x="625.9" y="154.0" width="5.15" height="15.16" fill="#535353"/>
<rect x="630.86" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="154.0" width="5.15" height="15.16" fill="#a80084"/>
<rect x="640.76" y="154.0" width="5.15" height="15.16" fill="#535353"/>
<rect x="586.29" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="168.86" width="5.15" height="15.16" fill="#202984"/>
<rect x="596.19" y="168.86" width="5.15" height="15.16" fill="#535353"/>
<rect x="601.14" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="168.86" width="5.15" height="15.16" fill="#4d29cf"/>
<rect x="611.05" y="168.86" width="5.15" height="15.16" fill="#535353"/>
<rect x="616.0" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="168.86" width="5.15" height="15.16" fill="#7b29dd"/>
<rect x="625.9" y="168.86" width="5.15" height="15.16" fill="#535353"/>
<rect x="630.86" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="168.86" width="5.15" height="15.16" fill="#a829d4"/>
<rect x="640.76" y="168.86" width="5.15" height="15.16" fill="#535353"/>
<rect x="645.71" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="650.67" y="168.86" width="5.15" height="15.16" fill="#d629a3"/>
<rect x="655.62" y="168.86" width="5.15" height="15.16" fill="#535353"/>
<rect x="586.29" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="183.71" width="5.15" height="15.16" fill="#2057c9"/>
<rect x="596.19" y="183.71" width="5.15" height="15.16" fill="#535353"/>
<rect x="601.14" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="183.71" width="5.15" height="15.16" fill="#4d57ed"/>
<rect x="611.05" y="183.71" width="5.15" height="15.16" fill="#535353"/>
<rect x="616.0" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="183.71" width="5.15" height="15.16" fill="#7b57f8"/>
<rect x="625.9" y="183.71" width="5.15" height="15.16" fill="#535353"/>
<rect x="630.86" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="183.71" width="5.15" height="15.16" fill="#a857f1"/>
<rect x="640.76" y="183.71" width="5.15" height="15.16" fill="#535353"/>
<rect x="645.71" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="650.67" y="183.71" width="5.15" height="15.16" fill="#d657d4"/>
<rect x="655.62" y="183.71" width="5.15" height="15.16" fill="#535353"/>
<rect x="660.57" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="665.52" y="183.71" width="5.15" height="15.16" fill="#ff5784"/>
<rect x="670.48" y="183.71" width="5.15" height="15.16" fill="#535353"/>
<rect x="586.29" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="198.57" width="5.15" height="15.16" fill="#2084d4"/>
<rect x="596.19" y="198.57" width="5.15" height="15.16" fill="#535353"/>
<rect x="601.14" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="198.57" width="5.15" height="15.16" fill="#4d84f5"/>
<rect x="611.05" y="198.57" width="5.15" height="15.16" fill="#535353"/>
<rect x="616.0" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="198.57" width="5.15" height="15.16" fill="#7b84ff"/>
<rect x="625.9" y="198.57" width="5.15" height="15.16" fill="#535353"/>
<rect x="630.86" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="198.57" width="5.15" height="15.16" fill="#a884f8"/>
<rect x="640.76" y="198.57" width="5.15" height="15.16" fill="#535353"/>
<rect x="645.71" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="650.67" y="198.57" width="5.15" height="15.16" fill="#d684dd"/>
<rect x="655.62" y="198.57" width="5.15" height="15.16" fill="#535353"/>
<rect x="660.57" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="665.52" y="198.57" width="5.15" height="15.16" fill="#ff8484"/>
<rect x="670.48" y="198.57" width="5.15" height="15.16" fill="#535353"/>
<rect x="586.29" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="213.43" width="5.15" height="15.16" fill="#20b2c3"/>
<rect x="596.19" y="213.43" width="5.15" height="15.16" fill="#535353"/>
<rect x="601.14" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="213.43" width="5.15" height="15.16" fill="#4db2ea"/>
<rect x="611.05" y="213.43" width="5.15" height="15.16" fill="#535353"/>
<rect x="616.0" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="213.43" width="5.15" height="15.16" fill="#7bb2f5"/>
<rect x="625.9" y="213.43" width="5.15" height="15.16" fill="#535353"/>
<rect x="630.86" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="213.43" width="5.15" height="15.16" fill="#a8b2ed"/>
<rect x="640.76" y="213.43" width="5.15" height="15.16" fill="#535353"/>
<rect x="645.71" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="650.67" y="213.43" width="5.15" height="15.16" fill="#d6b2cf"/>
<rect x="655.62" y="213.43" width="5.15" height="15.16" fill="#535353"/>
<rect x="586.29" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="228.29" width="5.15" height="15.16" fill="#20df84"/>
<rect x="596.19" y="228.29" width="5.15" height="15.16" fill="#535353"/>
<rect x="601.14" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="228.29" width="5.15" height="15.16" fill="#4ddfc3"/>
<rect x="611.05" y="228.29" width="5.15" height="15.16" fill="#535353"/>
<rect x="616.0" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="228.29" width="5.15" height="15.16" fill="#7bdfd4"/>
<rect x="625.9" y="228.29" width="5.15" height="15.16" fill="#535353"/>
<rect x="630.86" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="228.29" width="5.15" height="15.16" fill="#a8dfc9"/>
<rect x="640.76" y="228.29" width="5.15" height="15.16" fill="#535353"/>
<rect x="645.71" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="650.67" y="228.29" width="5.15" height="15.16" fill="#d6df84"/>
<rect x="655.62" y="228.29" width="5.15" height="15.16" fill="#535353"/>
</g>
<g><rect x="616.0" y="154.0" width="15.16" height="15.16" fill="#ffb2b7" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996;0.5662;0.6329;0.6996" values="#ffb2b7;#ffb2b7;#b3ac8d;#808d8d;#808d8d"/></rect>
<rect x="630.86" y="154.0" width="15.16" height="15.16" fill="#ffc2c6" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5008;0.5674;0.6341;0.7008" values="#ffc2c6;#ffc2c6;#99b989;#759e89;#759e89"/></rect>
<rect x="586.29" y="168.86" width="15.16" height="15.16" fill="#ffafb4" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4317" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4984;0.5650;0.6317;0.6984" values="#ffafb4;#ffafb4;#e6ada7;#817ea7;#817ea7"/></rect>
<rect x="601.14" y="168.86" width="15.16" height="15.16" fill="#ffb9bd" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996;0.5662;0.6329;0.6996" values="#ffb9bd;#ffb9bd;#ccb5a0;#7986a0;#7986a0"/></rect>
<rect x="616.0" y="168.86" width="15.16" height="15.16" fill="#ffc5c9" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5008;0.5674;0.6341;0.7008" values="#ffc5c9;#ffc5c9;#b2be9b;#71939b;#71939b"/></rect>
<rect x="630.86" y="168.86" width="15.16" height="15.16" fill="#ffd4d7" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5020;0.5686;0.6353;0.7020" values="#ffd4d7;#ffd4d7;#99ca95;#69a395;#69a395"/></rect>
<rect x="645.71" y="168.86" width="15.16" height="15.16" fill="#ffe4e6" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5032;0.5699;0.6365;0.7032" values="#ffe4e6;#ffe4e6;#7fd78e;#60b68e;#60b68e"/></rect>
<rect x="586.29" y="183.71" width="15.16" height="15.16" fill="#ffc6ca" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996;0.5662;0.6329;0.6996" values="#ffc6ca;#ffc6ca;#e8c4bc;#6e83bc;#6e83bc"/></rect>
<rect x="601.14" y="183.71" width="15.16" height="15.16" fill="#ffcfd2" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5008;0.5674;0.6341;0.7008" values="#ffcfd2;#ffcfd2;#cfcab4;#698cb4;#698cb4"/></rect>
<rect x="616.0" y="183.71" width="15.16" height="15.16" fill="#ffdadc" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5020;0.5686;0.6353;0.7020" values="#ffdadc;#ffdadc;#b6d2ac;#6598ac;#6598ac"/></rect>
<rect x="630.86" y="183.71" width="15.16" height="15.16" fill="#ffe7e8" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5032;0.5699;0.6365;0.7032" values="#ffe7e8;#ffe7e8;#9ddca4;#61a8a4;#61a8a4"/></rect>
<rect x="645.71" y="183.71" width="15.16" height="15.16" fill="#fff6f7" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5044;0.5711;0.6377;0.7044" values="#fff6f7;#fff6f7;#85e89c;#5cbb9c;#5cbb9c"/></rect>
<rect x="660.57" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5056;0.5723;0.6389;0.7056" values="#ffffff;#ffffff;#6cee8f;#53cb8f;#53cb8f"/></rect>
<rect x="586.29" y="198.57" width="15.16" height="15.16" fill="#ffdee0" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5008;0.5674;0.6341;0.7008" values="#ffdee0;#ffdee0;#eedcd5;#5b87d5;#5b87d5"/></rect>
<rect x="601.14" y="198.57" width="15.16" height="15.16" fill="#ffe5e7" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5020;0.5686;0.6353;0.7020" values="#ffe5e7;#ffe5e7;#d6e1ca;#5a90ca;#5a90ca"/></rect>
<rect x="616.0" y="198.57" width="15.16" height="15.16" fill="#ffeff0" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5032;0.5699;0.6365;0.7032" values="#ffeff0;#ffeff0;#bde8c1;#5c9dc1;#5c9dc1"/></rect>
<rect x="630.86" y="198.57" width="15.16" height="15.16" fill="#fffbfb" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5044;0.5711;0.6377;0.7044" values="#fffbfb;#fffbfb;#a6f1b8;#5daeb8;#5daeb8"/></rect>
<rect x="645.71" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5056;0.5723;0.6389;0.7056" values="#ffffff;#ffffff;#8ff2a9;#5bbba9;#5bbba9"/></rect>
<rect x="660.57" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5068;0.5735;0.6401;0.7068" values="#ffffff;#ffffff;#79ef98;#57c698;#57c698"/></rect>
<rect x="586.29" y="213.43" width="15.16" height="15.16" fill="#fff5f6" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5020;0.5686;0.6353;0.7020" values="#fff5f6;#fff5f6;#f7f4f0;#4888f0;#4888f0"/></rect>
<rect x="601.14" y="213.43" width="15.16" height="15.16" fill="#fffcfc" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5032;0.5699;0.6365;0.7032" values="#fffcfc;#fffcfc;#dff8e4;#4e94e4;#4e94e4"/></rect>
<rect x="616.0" y="213.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5044;0.5711;0.6377;0.7044" values="#ffffff;#ffffff;#c8f9d5;#55a0d5;#55a0d5"/></rect>
<rect x="630.86" y="213.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5056;0.5723;0.6389;0.7056" values="#ffffff;#ffffff;#b2f6c4;#5babc4;#5babc4"/></rect>
<rect x="645.71" y="213.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5068;0.5735;0.6401;0.7068" values="#ffffff;#ffffff;#9df3b4;#5eb6b4;#5eb6b4"/></rect>
<rect x="586.29" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5032;0.5699;0.6365;0.7032" values="#ffffff;#ffffff;#ffffff;#478cff;#478cff"/></rect>
<rect x="601.14" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5044;0.5711;0.6377;0.7044" values="#ffffff;#ffffff;#ebfdf0;#468ef0;#468ef0"/></rect>
<rect x="616.0" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5056;0.5723;0.6389;0.7056" values="#ffffff;#ffffff;#d5fadf;#539bdf;#539bdf"/></rect>
<rect x="630.86" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5068;0.5735;0.6401;0.7068" values="#ffffff;#ffffff;#c1f8cf;#5da7cf;#5da7cf"/></rect>
<rect x="645.71" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5080;0.5747;0.6413;0.7080" values="#ffffff;#ffffff;#aef5c1;#64b4c1;#64b4c1"/></rect>
</g>
</g>
<circle cx="624.91" cy="204.51" r="46.06" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2923;0.2926;1.0000" values="0;0;1;1"/></circle>
<circle cx="624.91" cy="204.51" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2923;0.2926;1.0000" values="0;0;1;1"/></circle>
<text x="624.91" y="209.51" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">8<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2923;0.2926;1.0000" values="0;0;1;1"/></text>
<circle cx="624.91" cy="204.51" r="46.06" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g clip-path="url(#fd-sph-D8)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;1.0000" values="0;0;1;1"/><rect x="824.0" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="183.71" width="5.15" height="15.16" fill="#441cb4"/>
<rect x="833.9" y="183.71" width="5.15" height="15.16" fill="#414141"/>
<rect x="838.86" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="183.71" width="5.15" height="15.16" fill="#6c1ccd"/>
<rect x="848.76" y="183.71" width="5.15" height="15.16" fill="#414141"/>
<rect x="853.71" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="183.71" width="5.15" height="15.16" fill="#931ccd"/>
<rect x="863.62" y="183.71" width="5.15" height="15.16" fill="#414141"/>
<rect x="868.57" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="183.71" width="5.15" height="15.16" fill="#bb1cb4"/>
<rect x="878.48" y="183.71" width="5.15" height="15.16" fill="#414141"/>
<rect x="809.14" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="198.57" width="5.15" height="15.16" fill="#1c44b4"/>
<rect x="819.05" y="198.57" width="5.15" height="15.16" fill="#414141"/>
<rect x="824.0" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="198.57" width="5.15" height="15.16" fill="#4444df"/>
<rect x="833.9" y="198.57" width="5.15" height="15.16" fill="#414141"/>
<rect x="838.86" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="198.57" width="5.15" height="15.16" fill="#6c44ee"/>
<rect x="848.76" y="198.57" width="5.15" height="15.16" fill="#414141"/>
<rect x="853.71" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="198.57" width="5.15" height="15.16" fill="#9344ee"/>
<rect x="863.62" y="198.57" width="5.15" height="15.16" fill="#414141"/>
<rect x="868.57" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="198.57" width="5.15" height="15.16" fill="#bb44df"/>
<rect x="878.48" y="198.57" width="5.15" height="15.16" fill="#414141"/>
<rect x="883.43" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="888.38" y="198.57" width="5.15" height="15.16" fill="#e344b4"/>
<rect x="893.33" y="198.57" width="5.15" height="15.16" fill="#414141"/>
<rect x="809.14" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="213.43" width="5.15" height="15.16" fill="#1c6ccd"/>
<rect x="819.05" y="213.43" width="5.15" height="15.16" fill="#414141"/>
<rect x="824.0" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="213.43" width="5.15" height="15.16" fill="#446cee"/>
<rect x="833.9" y="213.43" width="5.15" height="15.16" fill="#414141"/>
<rect x="838.86" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="213.43" width="5.15" height="15.16" fill="#6c6cfc"/>
<rect x="848.76" y="213.43" width="5.15" height="15.16" fill="#414141"/>
<rect x="853.71" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="213.43" width="5.15" height="15.16" fill="#936cfc"/>
<rect x="863.62" y="213.43" width="5.15" height="15.16" fill="#414141"/>
<rect x="868.57" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="213.43" width="5.15" height="15.16" fill="#bb6cee"/>
<rect x="878.48" y="213.43" width="5.15" height="15.16" fill="#414141"/>
<rect x="883.43" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="888.38" y="213.43" width="5.15" height="15.16" fill="#e36ccd"/>
<rect x="893.33" y="213.43" width="5.15" height="15.16" fill="#414141"/>
<rect x="809.14" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="228.29" width="5.15" height="15.16" fill="#1c93cd"/>
<rect x="819.05" y="228.29" width="5.15" height="15.16" fill="#414141"/>
<rect x="824.0" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="228.29" width="5.15" height="15.16" fill="#4493ee"/>
<rect x="833.9" y="228.29" width="5.15" height="15.16" fill="#414141"/>
<rect x="838.86" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="228.29" width="5.15" height="15.16" fill="#6c93fc"/>
<rect x="848.76" y="228.29" width="5.15" height="15.16" fill="#414141"/>
<rect x="853.71" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="228.29" width="5.15" height="15.16" fill="#9393fc"/>
<rect x="863.62" y="228.29" width="5.15" height="15.16" fill="#414141"/>
<rect x="868.57" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="228.29" width="5.15" height="15.16" fill="#bb93ee"/>
<rect x="878.48" y="228.29" width="5.15" height="15.16" fill="#414141"/>
<rect x="883.43" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="888.38" y="228.29" width="5.15" height="15.16" fill="#e393cd"/>
<rect x="893.33" y="228.29" width="5.15" height="15.16" fill="#414141"/>
<rect x="809.14" y="243.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="243.14" width="5.15" height="15.16" fill="#1cbbb4"/>
<rect x="819.05" y="243.14" width="5.15" height="15.16" fill="#414141"/>
<rect x="824.0" y="243.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="243.14" width="5.15" height="15.16" fill="#44bbdf"/>
<rect x="833.9" y="243.14" width="5.15" height="15.16" fill="#414141"/>
<rect x="838.86" y="243.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="243.14" width="5.15" height="15.16" fill="#6cbbee"/>
<rect x="848.76" y="243.14" width="5.15" height="15.16" fill="#414141"/>
<rect x="853.71" y="243.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="243.14" width="5.15" height="15.16" fill="#93bbee"/>
<rect x="863.62" y="243.14" width="5.15" height="15.16" fill="#414141"/>
<rect x="868.57" y="243.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="243.14" width="5.15" height="15.16" fill="#bbbbdf"/>
<rect x="878.48" y="243.14" width="5.15" height="15.16" fill="#414141"/>
<rect x="883.43" y="243.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="888.38" y="243.14" width="5.15" height="15.16" fill="#e3bbb4"/>
<rect x="893.33" y="243.14" width="5.15" height="15.16" fill="#414141"/>
<rect x="824.0" y="258.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="258.0" width="5.15" height="15.16" fill="#44e3b4"/>
<rect x="833.9" y="258.0" width="5.15" height="15.16" fill="#414141"/>
<rect x="838.86" y="258.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="258.0" width="5.15" height="15.16" fill="#6ce3cd"/>
<rect x="848.76" y="258.0" width="5.15" height="15.16" fill="#414141"/>
<rect x="853.71" y="258.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="258.0" width="5.15" height="15.16" fill="#93e3cd"/>
<rect x="863.62" y="258.0" width="5.15" height="15.16" fill="#414141"/>
<rect x="868.57" y="258.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="873.52" y="258.0" width="5.15" height="15.16" fill="#bbe3b4"/>
<rect x="878.48" y="258.0" width="5.15" height="15.16" fill="#414141"/>
</g>
<g><rect x="868.57" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4558" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5225;0.5891;0.6558;0.7225" values="#ffffff;#fff1c1;#fff1c1;#fff1c1;#dd7ac1"/></rect>
<rect x="868.57" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4570" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5237;0.5904;0.6570;0.7237" values="#ffffff;#fff7dd;#fff7dd;#fff7dd;#d868dd"/></rect>
<rect x="883.43" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4582" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5249;0.5916;0.6582;0.7249" values="#ffffff;#fff8df;#fff8df;#fff8df;#db73df"/></rect>
<rect x="868.57" y="213.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4582" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5249;0.5916;0.6582;0.7249" values="#ffffff;#fffdf8;#fffdf8;#fffdf8;#d256f8"/></rect>
<rect x="883.43" y="213.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4594" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5261;0.5928;0.6594;0.7261" values="#ffffff;#fffefa;#fffefa;#fffefa;#d665fa"/></rect>
<rect x="853.71" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4582" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5249;0.5916;0.6582;0.7249" values="#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="868.57" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4594" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5261;0.5928;0.6594;0.7261" values="#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="883.43" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4606" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5273;0.5940;0.6606;0.7273" values="#ffffff;#ffffff;#ffffff;#ffffff;#d35aff"/></rect>
<rect x="809.14" y="243.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4558" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5225;0.5891;0.6558;0.7225" values="#ffffff;#ffffff;#e5fceb;#e5fceb;#c16aeb"/></rect>
<rect x="824.0" y="243.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4570" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5237;0.5904;0.6570;0.7237" values="#ffffff;#ffffff;#f9fefb;#f9fefb;#cd54fb"/></rect>
<rect x="838.86" y="243.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4582" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5249;0.5916;0.6582;0.7249" values="#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="853.71" y="243.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4594" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5261;0.5928;0.6594;0.7261" values="#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="868.57" y="243.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4606" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5273;0.5940;0.6606;0.7273" values="#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="883.43" y="243.14" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4618" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5285;0.5952;0.6618;0.7285" values="#ffffff;#ffffff;#ffffff;#ffffff;#d256ff"/></rect>
<rect x="824.0" y="258.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4582" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5249;0.5916;0.6582;0.7249" values="#ffffff;#ffffff;#ffffff;#ffffff;#d35cff"/></rect>
<rect x="838.86" y="258.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4594" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5261;0.5928;0.6594;0.7261" values="#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="853.71" y="258.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4606" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5273;0.5940;0.6606;0.7273" values="#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
<rect x="868.57" y="258.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4618" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5285;0.5952;0.6618;0.7285" values="#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
</g>
</g>
<circle cx="853.71" cy="228.29" r="52.0" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;1.0000" values="0;0;1;1"/></circle>
<circle cx="853.71" cy="228.29" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;1.0000" values="0;0;1;1"/></circle>
<text x="853.71" y="233.29" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">9<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;1.0000" values="0;0;1;1"/></text>
<circle cx="853.71" cy="228.29" r="52.0" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g clip-path="url(#fd-sph-D9)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;1.0000" values="0;0;1;1"/><rect x="794.29" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="799.24" y="154.0" width="5.15" height="15.16" fill="#3b0584"/>
<rect x="804.19" y="154.0" width="5.15" height="15.16" fill="#303030"/>
<rect x="809.14" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="154.0" width="5.15" height="15.16" fill="#690598"/>
<rect x="819.05" y="154.0" width="5.15" height="15.16" fill="#303030"/>
<rect x="824.0" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="154.0" width="5.15" height="15.16" fill="#960598"/>
<rect x="833.9" y="154.0" width="5.15" height="15.16" fill="#303030"/>
<rect x="838.86" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="154.0" width="5.15" height="15.16" fill="#c40584"/>
<rect x="848.76" y="154.0" width="5.15" height="15.16" fill="#303030"/>
<rect x="779.43" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="784.38" y="168.86" width="5.15" height="15.16" fill="#0e3284"/>
<rect x="789.33" y="168.86" width="5.15" height="15.16" fill="#303030"/>
<rect x="794.29" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="799.24" y="168.86" width="5.15" height="15.16" fill="#3b32ca"/>
<rect x="804.19" y="168.86" width="5.15" height="15.16" fill="#303030"/>
<rect x="809.14" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="168.86" width="5.15" height="15.16" fill="#6932e2"/>
<rect x="819.05" y="168.86" width="5.15" height="15.16" fill="#303030"/>
<rect x="824.0" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="168.86" width="5.15" height="15.16" fill="#9632e2"/>
<rect x="833.9" y="168.86" width="5.15" height="15.16" fill="#303030"/>
<rect x="838.86" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="168.86" width="5.15" height="15.16" fill="#c432ca"/>
<rect x="848.76" y="168.86" width="5.15" height="15.16" fill="#303030"/>
<rect x="853.71" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="168.86" width="5.15" height="15.16" fill="#f13284"/>
<rect x="863.62" y="168.86" width="5.15" height="15.16" fill="#303030"/>
<rect x="779.43" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="784.38" y="183.71" width="5.15" height="15.16" fill="#0e60af"/>
<rect x="789.33" y="183.71" width="5.15" height="15.16" fill="#303030"/>
<rect x="794.29" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="799.24" y="183.71" width="5.15" height="15.16" fill="#3b60e6"/>
<rect x="804.19" y="183.71" width="5.15" height="15.16" fill="#303030"/>
<rect x="809.14" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="183.71" width="5.15" height="15.16" fill="#6960f9"/>
<rect x="819.05" y="183.71" width="5.15" height="15.16" fill="#303030"/>
<rect x="824.0" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="183.71" width="5.15" height="15.16" fill="#9660f9"/>
<rect x="833.9" y="183.71" width="5.15" height="15.16" fill="#303030"/>
<rect x="838.86" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="183.71" width="5.15" height="15.16" fill="#c460e6"/>
<rect x="848.76" y="183.71" width="5.15" height="15.16" fill="#303030"/>
<rect x="853.71" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="183.71" width="5.15" height="15.16" fill="#f160af"/>
<rect x="863.62" y="183.71" width="5.15" height="15.16" fill="#303030"/>
<rect x="779.43" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="784.38" y="198.57" width="5.15" height="15.16" fill="#0e8db7"/>
<rect x="789.33" y="198.57" width="5.15" height="15.16" fill="#303030"/>
<rect x="794.29" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="799.24" y="198.57" width="5.15" height="15.16" fill="#3b8dea"/>
<rect x="804.19" y="198.57" width="5.15" height="15.16" fill="#303030"/>
<rect x="809.14" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="198.57" width="5.15" height="15.16" fill="#698dfc"/>
<rect x="819.05" y="198.57" width="5.15" height="15.16" fill="#303030"/>
<rect x="824.0" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="198.57" width="5.15" height="15.16" fill="#968dfc"/>
<rect x="833.9" y="198.57" width="5.15" height="15.16" fill="#303030"/>
<rect x="838.86" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="198.57" width="5.15" height="15.16" fill="#c48dea"/>
<rect x="848.76" y="198.57" width="5.15" height="15.16" fill="#303030"/>
<rect x="853.71" y="198.57" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="198.57" width="5.15" height="15.16" fill="#f18db7"/>
<rect x="863.62" y="198.57" width="5.15" height="15.16" fill="#303030"/>
<rect x="779.43" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="784.38" y="213.43" width="5.15" height="15.16" fill="#0ebb84"/>
<rect x="789.33" y="213.43" width="5.15" height="15.16" fill="#303030"/>
<rect x="794.29" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="799.24" y="213.43" width="5.15" height="15.16" fill="#3bbbd9"/>
<rect x="804.19" y="213.43" width="5.15" height="15.16" fill="#303030"/>
<rect x="809.14" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="213.43" width="5.15" height="15.16" fill="#69bbee"/>
<rect x="819.05" y="213.43" width="5.15" height="15.16" fill="#303030"/>
<rect x="824.0" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="213.43" width="5.15" height="15.16" fill="#96bbee"/>
<rect x="833.9" y="213.43" width="5.15" height="15.16" fill="#303030"/>
<rect x="838.86" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="213.43" width="5.15" height="15.16" fill="#c4bbd9"/>
<rect x="848.76" y="213.43" width="5.15" height="15.16" fill="#303030"/>
<rect x="853.71" y="213.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="858.67" y="213.43" width="5.15" height="15.16" fill="#f1bb84"/>
<rect x="863.62" y="213.43" width="5.15" height="15.16" fill="#303030"/>
<rect x="794.29" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="799.24" y="228.29" width="5.15" height="15.16" fill="#3be898"/>
<rect x="804.19" y="228.29" width="5.15" height="15.16" fill="#303030"/>
<rect x="809.14" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="228.29" width="5.15" height="15.16" fill="#69e8c5"/>
<rect x="819.05" y="228.29" width="5.15" height="15.16" fill="#303030"/>
<rect x="824.0" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="228.29" width="5.15" height="15.16" fill="#96e8c5"/>
<rect x="833.9" y="228.29" width="5.15" height="15.16" fill="#303030"/>
<rect x="838.86" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="228.29" width="5.15" height="15.16" fill="#c4e898"/>
<rect x="848.76" y="228.29" width="5.15" height="15.16" fill="#303030"/>
</g>
<g><rect x="794.29" y="154.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5140;0.5807;0.6474;0.7140" values="#ffffff;#fff0bb;#99e582;#99e582;#90b282"/></rect>
<rect x="809.14" y="154.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5152;0.5819;0.6486;0.7152" values="#ffffff;#ffecaa;#b3e483;#b3e483;#a6a783"/></rect>
<rect x="824.0" y="154.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5165;0.5831;0.6498;0.7165" values="#ffffff;#ffe99c;#cce484;#cce484;#bc9f84"/></rect>
<rect x="838.86" y="154.0" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5177;0.5843;0.6510;0.7177" values="#ffffff;#ffe792;#e6e487;#e6e487;#d29b87"/></rect>
<rect x="779.43" y="168.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5140;0.5807;0.6474;0.7140" values="#ffffff;#fff8e1;#7fea8b;#7fea8b;#77b48b"/></rect>
<rect x="794.29" y="168.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5152;0.5819;0.6486;0.7152" values="#ffffff;#fff5d0;#99e990;#99e990;#8da590"/></rect>
<rect x="809.14" y="168.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5165;0.5831;0.6498;0.7165" values="#ffffff;#fff1c1;#b2e995;#b2e995;#a29995"/></rect>
<rect x="824.0" y="168.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5177;0.5843;0.6510;0.7177" values="#ffffff;#ffeeb5;#cce999;#cce999;#b79099"/></rect>
<rect x="838.86" y="168.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5189;0.5855;0.6522;0.7189" values="#ffffff;#ffedac;#e6ea9f;#e6ea9f;#cd8a9f"/></rect>
<rect x="853.71" y="168.86" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4534" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5201;0.5867;0.6534;0.7201" values="#ffffff;#ffeba7;#ffeba7;#ffeba7;#e389a7"/></rect>
<rect x="779.43" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5152;0.5819;0.6486;0.7152" values="#ffffff;#fffdf6;#85ef9c;#85ef9c;#7aaa9c"/></rect>
<rect x="794.29" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5165;0.5831;0.6498;0.7165" values="#ffffff;#fffae6;#9deea3;#9deea3;#8e99a3"/></rect>
<rect x="809.14" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5177;0.5843;0.6510;0.7177" values="#ffffff;#fff7d9;#b6eea9;#b6eea9;#a28ba9"/></rect>
<rect x="824.0" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5189;0.5855;0.6522;0.7189" values="#ffffff;#fff4ce;#cfefb0;#cfefb0;#b680b0"/></rect>
<rect x="838.86" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4534" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5201;0.5867;0.6534;0.7201" values="#ffffff;#fff2c6;#e8f0b9;#e8f0b9;#ca79b9"/></rect>
<rect x="853.71" y="183.71" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4546" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5213;0.5879;0.6546;0.7213" values="#ffffff;#fff1c2;#fff1c2;#fff1c2;#dd77c2"/></rect>
<rect x="779.43" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5165;0.5831;0.6498;0.7165" values="#ffffff;#ffffff;#8ff2a9;#8ff2a9;#82a0a9"/></rect>
<rect x="794.29" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5177;0.5843;0.6510;0.7177" values="#ffffff;#fffffe;#a6f4ba;#a6f4ba;#938fba"/></rect>
<rect x="809.14" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5189;0.5855;0.6522;0.7189" values="#ffffff;#fffcf1;#bdf4c2;#bdf4c2;#a57ec2"/></rect>
<rect x="824.0" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4534" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5201;0.5867;0.6534;0.7201" values="#ffffff;#fffae8;#d6f5cb;#d6f5cb;#b771cb"/></rect>
<rect x="838.86" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4546" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5213;0.5879;0.6546;0.7213" values="#ffffff;#fff8e1;#eef6d5;#eef6d5;#c967d5"/></rect>
<rect x="853.71" y="198.57" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4558" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5225;0.5891;0.6558;0.7225" values="#ffffff;#fff7dd;#fff7dd;#fff7dd;#d764dd"/></rect>
<rect x="779.43" y="213.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5177;0.5843;0.6510;0.7177" values="#ffffff;#ffffff;#9df3b4;#9df3b4;#8d98b4"/></rect>
<rect x="794.29" y="213.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5189;0.5855;0.6522;0.7189" values="#ffffff;#ffffff;#b2f6c4;#b2f6c4;#9c85c4"/></rect>
<rect x="809.14" y="213.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4534" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5201;0.5867;0.6534;0.7201" values="#ffffff;#ffffff;#c8f9d5;#c8f9d5;#ab73d5"/></rect>
<rect x="824.0" y="213.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4546" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5213;0.5879;0.6546;0.7213" values="#ffffff;#ffffff;#dffbe7;#dffbe7;#bb62e7"/></rect>
<rect x="838.86" y="213.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4558" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5225;0.5891;0.6558;0.7225" values="#ffffff;#fffefc;#f7fdf5;#f7fdf5;#cb55f5"/></rect>
<rect x="853.71" y="213.43" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4570" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5237;0.5904;0.6570;0.7237" values="#ffffff;#fffdf8;#fffdf8;#fffdf8;#d152f8"/></rect>
<rect x="794.29" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4534" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5201;0.5867;0.6534;0.7201" values="#ffffff;#ffffff;#c1f8cf;#c1f8cf;#a87fcf"/></rect>
<rect x="809.14" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4546" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5213;0.5879;0.6546;0.7213" values="#ffffff;#ffffff;#d5fadf;#d5fadf;#b56bdf"/></rect>
<rect x="824.0" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4558" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5225;0.5891;0.6558;0.7225" values="#ffffff;#ffffff;#ebfdf0;#ebfdf0;#c257f0"/></rect>
<rect x="838.86" y="228.29" width="15.16" height="15.16" fill="#ffffff" fill-opacity="0"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4570" values="0;1"/><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5237;0.5904;0.6570;0.7237" values="#ffffff;#ffffff;#ffffff;#ffffff;#d153ff"/></rect>
</g>
</g>
<circle cx="824.0" cy="201.54" r="46.06" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;1.0000" values="0;0;1;1"/></circle>
<circle cx="824.0" cy="201.54" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;1.0000" values="0;0;1;1"/></circle>
<text x="824.0" y="206.54" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">10<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;1.0000" values="0;0;1;1"/></text>
<circle cx="824.0" cy="201.54" r="46.06" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<line x1="84.0" y1="89.0" x2="84.0" y2="89.0" stroke="#ff3340" stroke-width="3" stroke-dasharray="6 4" opacity="0"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0382;0.0385;0.1049;0.1052;0.1716;0.1719;0.2382;0.2385;0.3049;0.3052;0.3716;0.3719;0.4382;0.4385;0.5049;0.5052;0.5716;0.5719;0.6382;0.6385;1.0000" values="84;84;106.29;106.29;136;136;358.86;358.86;388.57;388.57;217.71;217.71;254.86;254.86;115.2;115.2;144.91;144.91;373.71;373.71;344;344"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0382;0.0385;0.1049;0.1052;0.1716;0.1719;0.2382;0.2385;0.3049;0.3052;0.3716;0.3719;0.4382;0.4385;0.5049;0.5052;0.5716;0.5719;0.6382;0.6385;1.0000" values="89;89;106.46;106.46;121.31;121.31;103.49;103.49;118.34;118.34;159.94;159.94;168.86;168.86;228.29;228.29;204.51;204.51;228.29;228.29;201.54;201.54"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0382;0.0385;0.0464;0.0467;0.1049;0.1052;0.1130;0.1133;0.1716;0.1719;0.1797;0.1800;0.2382;0.2385;0.2464;0.2467;0.3049;0.3052;0.3130;0.3133;0.3716;0.3719;0.3797;0.3800;0.4382;0.4385;0.4464;0.4467;0.5049;0.5052;0.5130;0.5133;0.5716;0.5719;0.5797;0.5800;0.6382;0.6385;0.6464;0.6467;1.0000" values="0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0"/></line>
<line x1="390.8" y1="83.8" x2="390.8" y2="83.8" stroke="#ffcc1a" stroke-width="3" stroke-dasharray="6 4" opacity="0"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0489;0.1153;0.1156;0.1819;0.1822;0.2486;0.2489;0.3153;0.3156;0.3819;0.3822;0.4486;0.4489;0.5153;0.5156;0.5819;0.5822;0.6486;0.6489;1.0000" values="390.8;390.8;106.29;106.29;136;136;358.86;358.86;388.57;388.57;217.71;217.71;254.86;254.86;115.2;115.2;144.91;144.91;373.71;373.71;344;344"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0489;0.1153;0.1156;0.1819;0.1822;0.2486;0.2489;0.3153;0.3156;0.3819;0.3822;0.4486;0.4489;0.5153;0.5156;0.5819;0.5822;0.6486;0.6489;1.0000" values="83.8;83.8;106.46;106.46;121.31;121.31;103.49;103.49;118.34;118.34;159.94;159.94;168.86;168.86;228.29;228.29;204.51;204.51;228.29;228.29;201.54;201.54"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0489;0.0567;0.0570;0.1153;0.1156;0.1234;0.1237;0.1819;0.1822;0.1901;0.1904;0.2486;0.2489;0.2567;0.2570;0.3153;0.3156;0.3234;0.3237;0.3819;0.3822;0.3901;0.3904;0.4486;0.4489;0.4567;0.4570;0.5153;0.5156;0.5234;0.5237;0.5819;0.5822;0.5901;0.5904;0.6486;0.6489;0.6567;0.6570;1.0000" values="0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0"/></line>
<line x1="240.0" y1="169.6" x2="240.0" y2="169.6" stroke="#26e659" stroke-width="3" stroke-dasharray="6 4" opacity="0"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.1256;0.1259;0.1923;0.1926;0.2590;0.2593;0.3256;0.3259;0.3923;0.3926;0.4590;0.4593;0.5256;0.5259;0.5923;0.5926;0.6590;0.6593;1.0000" values="240;240;106.29;106.29;136;136;358.86;358.86;388.57;388.57;217.71;217.71;254.86;254.86;115.2;115.2;144.91;144.91;373.71;373.71;344;344"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.1256;0.1259;0.1923;0.1926;0.2590;0.2593;0.3256;0.3259;0.3923;0.3926;0.4590;0.4593;0.5256;0.5259;0.5923;0.5926;0.6590;0.6593;1.0000" values="169.6;169.6;106.46;106.46;121.31;121.31;103.49;103.49;118.34;118.34;159.94;159.94;168.86;168.86;228.29;228.29;204.51;204.51;228.29;228.29;201.54;201.54"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0671;0.0674;0.1256;0.1259;0.1338;0.1341;0.1923;0.1926;0.2004;0.2007;0.2590;0.2593;0.2671;0.2674;0.3256;0.3259;0.3338;0.3341;0.3923;0.3926;0.4004;0.4007;0.4590;0.4593;0.4671;0.4674;0.5256;0.5259;0.5338;0.5341;0.5923;0.5926;0.6004;0.6007;0.6590;0.6593;0.6671;0.6674;1.0000" values="0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0"/></line>
<line x1="99.6" y1="247.6" x2="99.6" y2="247.6" stroke="#3380ff" stroke-width="3" stroke-dasharray="6 4" opacity="0"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0693;0.0696;0.1360;0.1363;0.2027;0.2030;0.2693;0.2696;0.3360;0.3363;0.4027;0.4030;0.4693;0.4696;0.5360;0.5363;0.6027;0.6030;0.6693;0.6696;1.0000" values="99.6;99.6;106.29;106.29;136;136;358.86;358.86;388.57;388.57;217.71;217.71;254.86;254.86;115.2;115.2;144.91;144.91;373.71;373.71;344;344"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0693;0.0696;0.1360;0.1363;0.2027;0.2030;0.2693;0.2696;0.3360;0.3363;0.4027;0.4030;0.4693;0.4696;0.5360;0.5363;0.6027;0.6030;0.6693;0.6696;1.0000" values="247.6;247.6;106.46;106.46;121.31;121.31;103.49;103.49;118.34;118.34;159.94;159.94;168.86;168.86;228.29;228.29;204.51;204.51;228.29;228.29;201.54;201.54"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0693;0.0696;0.0775;0.0778;0.1360;0.1363;0.1441;0.1444;0.2027;0.2030;0.2108;0.2111;0.2693;0.2696;0.2775;0.2778;0.3360;0.3363;0.3441;0.3444;0.4027;0.4030;0.4108;0.4111;0.4693;0.4696;0.4775;0.4778;0.5360;0.5363;0.5441;0.5444;0.6027;0.6030;0.6108;0.6111;0.6693;0.6696;0.6775;0.6778;1.0000" values="0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0"/></line>
<line x1="380.4" y1="247.6" x2="380.4" y2="247.6" stroke="#cc40ff" stroke-width="3" stroke-dasharray="6 4" opacity="0"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1464;0.1467;0.2130;0.2133;0.2797;0.2800;0.3464;0.3467;0.4130;0.4133;0.4797;0.4800;0.5464;0.5467;0.6130;0.6133;0.6797;0.6800;1.0000" values="380.4;380.4;106.29;106.29;136;136;358.86;358.86;388.57;388.57;217.71;217.71;254.86;254.86;115.2;115.2;144.91;144.91;373.71;373.71;344;344"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1464;0.1467;0.2130;0.2133;0.2797;0.2800;0.3464;0.3467;0.4130;0.4133;0.4797;0.4800;0.5464;0.5467;0.6130;0.6133;0.6797;0.6800;1.0000" values="247.6;247.6;106.46;106.46;121.31;121.31;103.49;103.49;118.34;118.34;159.94;159.94;168.86;168.86;228.29;228.29;204.51;204.51;228.29;228.29;201.54;201.54"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.0879;0.0881;0.1464;0.1467;0.1545;0.1548;0.2130;0.2133;0.2212;0.2215;0.2797;0.2800;0.2879;0.2881;0.3464;0.3467;0.3545;0.3548;0.4130;0.4133;0.4212;0.4215;0.4797;0.4800;0.4879;0.4881;0.5464;0.5467;0.5545;0.5548;0.6130;0.6133;0.6212;0.6215;0.6797;0.6800;0.6879;0.6881;1.0000" values="0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0"/></line>
<text x="32" y="306" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">共通シーン(物体 10 個・ライト 5 個)</text>
<circle cx="46" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="46" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="46" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">1</text>
<rect x="32" y="316" width="28" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0293;0.0296;0.0960;0.0963;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="70" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="70" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="70" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">2</text>
<rect x="56" y="316" width="28" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;0.1627;0.1630;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="94" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="94" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="94" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">3</text>
<rect x="80" y="316" width="28" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1627;0.1630;0.2293;0.2296;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="118" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="118" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="118" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">4</text>
<rect x="104" y="316" width="28" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2293;0.2296;0.2960;0.2963;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="142" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="142" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="142" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">5</text>
<rect x="128" y="316" width="28" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;0.3627;0.3630;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="166" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="166" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="166" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">6</text>
<rect x="152" y="316" width="28" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3627;0.3630;0.4293;0.4296;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="190" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="190" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="190" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">7</text>
<rect x="176" y="316" width="28" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;0.4960;0.4963;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="214" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="214" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="214" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">8</text>
<rect x="200" y="316" width="28" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;0.5627;0.5630;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="238" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="238" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="238" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">9</text>
<rect x="224" y="316" width="28" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;0.6293;0.6296;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="262" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="262" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="262" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">10</text>
<rect x="248" y="316" width="28" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;0.7182;0.7185;1.0000" values="0;0;1;1;0;0"/></rect>
<line x1="316.5" y1="330.0" x2="321.0" y2="330.0" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<line x1="314.01" y1="336.01" x2="317.19" y2="339.19" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<line x1="308.0" y1="338.5" x2="308.0" y2="343.0" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<line x1="301.99" y1="336.01" x2="298.81" y2="339.19" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<line x1="299.5" y1="330.0" x2="295.0" y2="330.0" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<line x1="301.99" y1="323.99" x2="298.81" y2="320.81" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<line x1="308.0" y1="321.5" x2="308.0" y2="317.0" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<line x1="314.01" y1="323.99" x2="317.19" y2="320.81" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<circle cx="308" cy="330" r="6.5" fill="#ff3340" stroke="#ffffff" stroke-width="1"/>
<rect x="293" y="315" width="30" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0382;0.0385;0.0486;0.0489;0.1049;0.1052;0.1153;0.1156;0.1716;0.1719;0.1819;0.1822;0.2382;0.2385;0.2486;0.2489;0.3049;0.3052;0.3153;0.3156;0.3716;0.3719;0.3819;0.3822;0.4382;0.4385;0.4486;0.4489;0.5049;0.5052;0.5153;0.5156;0.5716;0.5719;0.5819;0.5822;0.6382;0.6385;0.6486;0.6489;1.0000" values="0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0"/></rect>
<line x1="346.5" y1="330.0" x2="351.0" y2="330.0" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<line x1="344.01" y1="336.01" x2="347.19" y2="339.19" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<line x1="338.0" y1="338.5" x2="338.0" y2="343.0" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<line x1="331.99" y1="336.01" x2="328.81" y2="339.19" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<line x1="329.5" y1="330.0" x2="325.0" y2="330.0" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<line x1="331.99" y1="323.99" x2="328.81" y2="320.81" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<line x1="338.0" y1="321.5" x2="338.0" y2="317.0" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<line x1="344.01" y1="323.99" x2="347.19" y2="320.81" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<circle cx="338" cy="330" r="6.5" fill="#ffcc1a" stroke="#ffffff" stroke-width="1"/>
<rect x="323" y="315" width="30" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0489;0.0590;0.0593;0.1153;0.1156;0.1256;0.1259;0.1819;0.1822;0.1923;0.1926;0.2486;0.2489;0.2590;0.2593;0.3153;0.3156;0.3256;0.3259;0.3819;0.3822;0.3923;0.3926;0.4486;0.4489;0.4590;0.4593;0.5153;0.5156;0.5256;0.5259;0.5819;0.5822;0.5923;0.5926;0.6486;0.6489;0.6590;0.6593;1.0000" values="0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0"/></rect>
<line x1="376.5" y1="330.0" x2="381.0" y2="330.0" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<line x1="374.01" y1="336.01" x2="377.19" y2="339.19" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<line x1="368.0" y1="338.5" x2="368.0" y2="343.0" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<line x1="361.99" y1="336.01" x2="358.81" y2="339.19" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<line x1="359.5" y1="330.0" x2="355.0" y2="330.0" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<line x1="361.99" y1="323.99" x2="358.81" y2="320.81" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<line x1="368.0" y1="321.5" x2="368.0" y2="317.0" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<line x1="374.01" y1="323.99" x2="377.19" y2="320.81" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<circle cx="368" cy="330" r="6.5" fill="#26e659" stroke="#ffffff" stroke-width="1"/>
<rect x="353" y="315" width="30" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0693;0.0696;0.1256;0.1259;0.1360;0.1363;0.1923;0.1926;0.2027;0.2030;0.2590;0.2593;0.2693;0.2696;0.3256;0.3259;0.3360;0.3363;0.3923;0.3926;0.4027;0.4030;0.4590;0.4593;0.4693;0.4696;0.5256;0.5259;0.5360;0.5363;0.5923;0.5926;0.6027;0.6030;0.6590;0.6593;0.6693;0.6696;1.0000" values="0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0"/></rect>
<line x1="406.5" y1="330.0" x2="411.0" y2="330.0" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="404.01" y1="336.01" x2="407.19" y2="339.19" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="398.0" y1="338.5" x2="398.0" y2="343.0" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="391.99" y1="336.01" x2="388.81" y2="339.19" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="389.5" y1="330.0" x2="385.0" y2="330.0" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="391.99" y1="323.99" x2="388.81" y2="320.81" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="398.0" y1="321.5" x2="398.0" y2="317.0" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="404.01" y1="323.99" x2="407.19" y2="320.81" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<circle cx="398" cy="330" r="6.5" fill="#3380ff" stroke="#ffffff" stroke-width="1"/>
<rect x="383" y="315" width="30" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0693;0.0696;0.0797;0.0800;0.1360;0.1363;0.1464;0.1467;0.2027;0.2030;0.2130;0.2133;0.2693;0.2696;0.2797;0.2800;0.3360;0.3363;0.3464;0.3467;0.4027;0.4030;0.4130;0.4133;0.4693;0.4696;0.4797;0.4800;0.5360;0.5363;0.5464;0.5467;0.6027;0.6030;0.6130;0.6133;0.6693;0.6696;0.6797;0.6800;1.0000" values="0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0"/></rect>
<line x1="436.5" y1="330.0" x2="441.0" y2="330.0" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="434.01" y1="336.01" x2="437.19" y2="339.19" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="428.0" y1="338.5" x2="428.0" y2="343.0" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="421.99" y1="336.01" x2="418.81" y2="339.19" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="419.5" y1="330.0" x2="415.0" y2="330.0" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="421.99" y1="323.99" x2="418.81" y2="320.81" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="428.0" y1="321.5" x2="428.0" y2="317.0" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="434.01" y1="323.99" x2="437.19" y2="320.81" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<circle cx="428" cy="330" r="6.5" fill="#cc40ff" stroke="#ffffff" stroke-width="1"/>
<rect x="413" y="315" width="30" height="40" rx="5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.0901;0.0904;0.1464;0.1467;0.1567;0.1570;0.2130;0.2133;0.2234;0.2237;0.2797;0.2800;0.2901;0.2904;0.3464;0.3467;0.3567;0.3570;0.4130;0.4133;0.4234;0.4237;0.4797;0.4800;0.4901;0.4904;0.5464;0.5467;0.5567;0.5570;0.6130;0.6133;0.6234;0.6237;0.6797;0.6800;0.6901;0.6904;1.0000" values="0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0;1;1;0;0"/></rect>
<text x="512" y="306" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">共通シーン(物体 10 個・ライト 5 個)</text>
<circle cx="526" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="526" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="526" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">1</text>
<rect x="512" y="316" width="28" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0923;0.0926;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="550" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="550" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="550" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">2</text>
<rect x="536" y="316" width="28" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0923;0.0926;0.1256;0.1259;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="574" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="574" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="574" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">3</text>
<rect x="560" y="316" width="28" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1256;0.1259;0.1590;0.1593;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="598" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="598" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="598" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">4</text>
<rect x="584" y="316" width="28" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1590;0.1593;0.1923;0.1926;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="622" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="622" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="622" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">5</text>
<rect x="608" y="316" width="28" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;0.2256;0.2259;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="646" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="646" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="646" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">6</text>
<rect x="632" y="316" width="28" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2256;0.2259;0.2590;0.2593;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="670" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="670" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="670" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">7</text>
<rect x="656" y="316" width="28" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;0.2923;0.2926;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="694" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="694" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="694" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">8</text>
<rect x="680" y="316" width="28" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2923;0.2926;0.3256;0.3259;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="718" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="718" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="718" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">9</text>
<rect x="704" y="316" width="28" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;0.3590;0.3593;1.0000" values="0;0;1;1;0;0"/></rect>
<circle cx="742" cy="330" r="10" fill="#ffffff" stroke="#64748b" stroke-width="1.2"/>
<circle cx="742" cy="330" r="10" fill="url(#fd-sphere)"/>
<text x="742" y="355" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">10</text>
<rect x="728" y="316" width="28" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;0.3923;0.3926;1.0000" values="0;0;1;1;0;0"/></rect>
<line x1="796.5" y1="330.0" x2="801.0" y2="330.0" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<line x1="794.01" y1="336.01" x2="797.19" y2="339.19" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<line x1="788.0" y1="338.5" x2="788.0" y2="343.0" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<line x1="781.99" y1="336.01" x2="778.81" y2="339.19" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<line x1="779.5" y1="330.0" x2="775.0" y2="330.0" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<line x1="781.99" y1="323.99" x2="778.81" y2="320.81" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<line x1="788.0" y1="321.5" x2="788.0" y2="317.0" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<line x1="794.01" y1="323.99" x2="797.19" y2="320.81" stroke="#ff3340" stroke-width="2.2" stroke-linecap="round"/>
<circle cx="788" cy="330" r="6.5" fill="#ff3340" stroke="#ffffff" stroke-width="1"/>
<rect x="773" y="315" width="30" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4145;0.4148;0.4812;0.4815;1.0000" values="0;0;1;1;0;0"/></rect>
<line x1="826.5" y1="330.0" x2="831.0" y2="330.0" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<line x1="824.01" y1="336.01" x2="827.19" y2="339.19" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<line x1="818.0" y1="338.5" x2="818.0" y2="343.0" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<line x1="811.99" y1="336.01" x2="808.81" y2="339.19" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<line x1="809.5" y1="330.0" x2="805.0" y2="330.0" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<line x1="811.99" y1="323.99" x2="808.81" y2="320.81" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<line x1="818.0" y1="321.5" x2="818.0" y2="317.0" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<line x1="824.01" y1="323.99" x2="827.19" y2="320.81" stroke="#ffcc1a" stroke-width="2.2" stroke-linecap="round"/>
<circle cx="818" cy="330" r="6.5" fill="#ffcc1a" stroke="#ffffff" stroke-width="1"/>
<rect x="803" y="315" width="30" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;0.5479;0.5481;1.0000" values="0;0;1;1;0;0"/></rect>
<line x1="856.5" y1="330.0" x2="861.0" y2="330.0" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<line x1="854.01" y1="336.01" x2="857.19" y2="339.19" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<line x1="848.0" y1="338.5" x2="848.0" y2="343.0" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<line x1="841.99" y1="336.01" x2="838.81" y2="339.19" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<line x1="839.5" y1="330.0" x2="835.0" y2="330.0" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<line x1="841.99" y1="323.99" x2="838.81" y2="320.81" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<line x1="848.0" y1="321.5" x2="848.0" y2="317.0" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<line x1="854.01" y1="323.99" x2="857.19" y2="320.81" stroke="#26e659" stroke-width="2.2" stroke-linecap="round"/>
<circle cx="848" cy="330" r="6.5" fill="#26e659" stroke="#ffffff" stroke-width="1"/>
<rect x="833" y="315" width="30" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;0.6145;0.6148;1.0000" values="0;0;1;1;0;0"/></rect>
<line x1="886.5" y1="330.0" x2="891.0" y2="330.0" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="884.01" y1="336.01" x2="887.19" y2="339.19" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="878.0" y1="338.5" x2="878.0" y2="343.0" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="871.99" y1="336.01" x2="868.81" y2="339.19" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="869.5" y1="330.0" x2="865.0" y2="330.0" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="871.99" y1="323.99" x2="868.81" y2="320.81" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="878.0" y1="321.5" x2="878.0" y2="317.0" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="884.01" y1="323.99" x2="887.19" y2="320.81" stroke="#3380ff" stroke-width="2.2" stroke-linecap="round"/>
<circle cx="878" cy="330" r="6.5" fill="#3380ff" stroke="#ffffff" stroke-width="1"/>
<rect x="863" y="315" width="30" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6145;0.6148;0.6812;0.6815;1.0000" values="0;0;1;1;0;0"/></rect>
<line x1="916.5" y1="330.0" x2="921.0" y2="330.0" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="914.01" y1="336.01" x2="917.19" y2="339.19" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="908.0" y1="338.5" x2="908.0" y2="343.0" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="901.99" y1="336.01" x2="898.81" y2="339.19" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="899.5" y1="330.0" x2="895.0" y2="330.0" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="901.99" y1="323.99" x2="898.81" y2="320.81" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="908.0" y1="321.5" x2="908.0" y2="317.0" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<line x1="914.01" y1="323.99" x2="917.19" y2="320.81" stroke="#cc40ff" stroke-width="2.2" stroke-linecap="round"/>
<circle cx="908" cy="330" r="6.5" fill="#cc40ff" stroke="#ffffff" stroke-width="1"/>
<rect x="893" y="315" width="30" height="40" rx="5" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6812;0.6815;0.7701;0.7704;1.0000" values="0;0;1;1;0;0"/></rect>
<text x="32" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① 物体 1/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0293;0.0296;0.0960;0.0963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② 物体 2/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;0.1627;0.1630;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">③ 物体 3/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1627;0.1630;0.2293;0.2296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">④ 物体 4/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2293;0.2296;0.2960;0.2963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">⑤ 物体 5/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;0.3627;0.3630;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">⑥ 物体 6/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3627;0.3630;0.4293;0.4296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">⑦ 物体 7/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;0.4960;0.4963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">⑧ 物体 8/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;0.5627;0.5630;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">⑨ 物体 9/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;0.6293;0.6296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">⑩ 物体 10/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;0.7182;0.7185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="450" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">赤枠 = 前の物体を上書き(前の計算が無駄に)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0293;0.0296;0.7182;0.7185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="378" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937">ピクセル計算:</text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="1">0<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0382;0.0385;1.0000" values="1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">36<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0382;0.0385;0.0486;0.0489;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">72<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0489;0.0590;0.0593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">108<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0693;0.0696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">144<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0693;0.0696;0.0797;0.0800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">180<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1049;0.1052;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">212<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1049;0.1052;0.1153;0.1156;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">244<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1153;0.1156;0.1256;0.1259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">276<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1256;0.1259;0.1360;0.1363;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">308<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1360;0.1363;0.1464;0.1467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">340<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1464;0.1467;0.1716;0.1719;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">378<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1716;0.1719;0.1819;0.1822;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">416<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1819;0.1822;0.1923;0.1926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">454<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;0.2027;0.2030;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">492<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2027;0.2030;0.2130;0.2133;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">530<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2130;0.2133;0.2382;0.2385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">558<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2382;0.2385;0.2486;0.2489;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">586<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2486;0.2489;0.2590;0.2593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">614<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;0.2693;0.2696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">642<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2693;0.2696;0.2797;0.2800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">670<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2797;0.2800;0.3049;0.3052;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">711<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3049;0.3052;0.3153;0.3156;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">752<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3153;0.3156;0.3256;0.3259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">793<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;0.3360;0.3363;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">834<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3360;0.3363;0.3464;0.3467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">875<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3464;0.3467;0.3716;0.3719;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">907<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3716;0.3719;0.3819;0.3822;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">939<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3819;0.3822;0.3923;0.3926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">971<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3923;0.3926;0.4027;0.4030;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,003<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4027;0.4030;0.4130;0.4133;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,035<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4130;0.4133;0.4382;0.4385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,071<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4382;0.4385;0.4486;0.4489;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,107<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4486;0.4489;0.4590;0.4593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,143<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4590;0.4593;0.4693;0.4696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,179<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4693;0.4696;0.4797;0.4800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,215<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4797;0.4800;0.5049;0.5052;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,244<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5049;0.5052;0.5153;0.5156;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,273<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5153;0.5156;0.5256;0.5259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,302<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5256;0.5259;0.5360;0.5363;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,331<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5360;0.5363;0.5464;0.5467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,360<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5464;0.5467;0.5716;0.5719;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,392<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5716;0.5719;0.5819;0.5822;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,424<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5819;0.5822;0.5923;0.5926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,456<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5923;0.5926;0.6027;0.6030;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,488<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6027;0.6030;0.6130;0.6133;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,520<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6130;0.6133;0.6382;0.6385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,552<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6382;0.6385;0.6486;0.6489;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,584<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6486;0.6489;0.6590;0.6593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,616<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6590;0.6593;0.6693;0.6696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,648<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6693;0.6696;0.6797;0.6800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,680<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6797;0.6800;1.0000" values="0;0;1;1"/></text>
<text x="32" y="404" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">うち、あとで上書きされて無駄:</text>
<text x="264" y="404" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;1.0000" values="1;1;0;0"/></text>
<text x="264" y="404" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">90<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;0.2293;0.2296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="264" y="404" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">175<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2293;0.2296;0.2960;0.2963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="264" y="404" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">185<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;0.3627;0.3630;1.0000" values="0;0;1;1;0;0"/></text>
<text x="264" y="404" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">280<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3627;0.3630;0.4960;0.4963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="264" y="404" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">375<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;0.6293;0.6296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="264" y="404" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">445<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7182;0.7185;1.0000" values="0;0;1;1"/><rect x="32" y="414" width="416" height="118" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="48" y="436" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1e3a8a">物体10 × ライト5 = 50回の描画</text>
<text x="48" y="462" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1e3a8a">ピクセル計算 336 マス × ライト5 = 1,680回</text>
<text x="48" y="488" text-anchor="start" style="font-size:19px;font-weight:700;fill:#e5484d">隠れて見えない部分も計算:無駄 約26%</text>
<text x="48" y="512" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">(重なったマスの計算は、あとで上書きされて捨てられる)</text>
</g>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(1/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0923;0.0926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(2/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0923;0.0926;0.1256;0.1259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(3/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1256;0.1259;0.1590;0.1593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(4/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1590;0.1593;0.1923;0.1926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(5/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;0.2256;0.2259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(6/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2256;0.2259;0.2590;0.2593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(7/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;0.2923;0.2926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(8/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2923;0.2926;0.3256;0.3259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(9/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;0.3590;0.3593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(10/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;0.4145;0.4148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② Pass 2:絵のあるピクセルにライトを1つずつ(1/5)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4145;0.4148;0.4812;0.4815;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② Pass 2:絵のあるピクセルにライトを1つずつ(2/5)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;0.5479;0.5481;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② Pass 2:絵のあるピクセルにライトを1つずつ(3/5)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;0.6145;0.6148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② Pass 2:絵のあるピクセルにライトを1つずつ(4/5)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6145;0.6148;0.6812;0.6815;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="428" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② Pass 2:絵のあるピクセルにライトを1つずつ(5/5)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6812;0.6815;0.7701;0.7704;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="450" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed" opacity="0">1マスに 色 | 法線 | 深度 の3種類を保存<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.4145;0.4148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="450" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed" opacity="0">物体の数に関係なく、画面を1回なぞる × 5 ライト<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4145;0.4148;0.7701;0.7704;1.0000" values="0;0;1;1;0;0"/></text>
<line x1="512" y1="50" x2="512" y2="287.71" stroke="#ff3340" stroke-width="5" opacity="0" clip-path="url(#fd-clip-d)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4145;0.4148;0.4671;0.4674;1.0000" values="0;0;0.9;0.9;0;0"/><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4148;0.4667;1.0000" values="512;512;1165.71;1165.71"/><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4145;0.4148;0.4667;1.0000" values="512;512;274.29;928;928"/></line>
<line x1="512" y1="50" x2="512" y2="287.71" stroke="#ffcc1a" stroke-width="5" opacity="0" clip-path="url(#fd-clip-d)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;0.5338;0.5341;1.0000" values="0;0;0.9;0.9;0;0"/><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4815;0.5333;1.0000" values="512;512;1165.71;1165.71"/><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;0.5333;1.0000" values="512;512;274.29;928;928"/></line>
<line x1="512" y1="50" x2="512" y2="287.71" stroke="#26e659" stroke-width="5" opacity="0" clip-path="url(#fd-clip-d)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;0.6004;0.6007;1.0000" values="0;0;0.9;0.9;0;0"/><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5481;0.6000;1.0000" values="512;512;1165.71;1165.71"/><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;0.6000;1.0000" values="512;512;274.29;928;928"/></line>
<line x1="512" y1="50" x2="512" y2="287.71" stroke="#3380ff" stroke-width="5" opacity="0" clip-path="url(#fd-clip-d)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6145;0.6148;0.6671;0.6674;1.0000" values="0;0;0.9;0.9;0;0"/><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6148;0.6667;1.0000" values="512;512;1165.71;1165.71"/><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6145;0.6148;0.6667;1.0000" values="512;512;274.29;928;928"/></line>
<line x1="512" y1="50" x2="512" y2="287.71" stroke="#cc40ff" stroke-width="5" opacity="0" clip-path="url(#fd-clip-d)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6812;0.6815;0.7338;0.7341;1.0000" values="0;0;0.9;0.9;0;0"/><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6815;0.7333;1.0000" values="512;512;1165.71;1165.71"/><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6812;0.6815;0.7333;1.0000" values="512;512;274.29;928;928"/></line>
<text x="512" y="378" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937">ピクセル計算:</text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="1">0<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4178;0.4181;1.0000" values="1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">8<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4178;0.4181;0.4242;0.4245;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">32<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4242;0.4245;0.4307;0.4310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">78<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4307;0.4310;0.4372;0.4375;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">134<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4372;0.4375;0.4437;0.4440;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">179<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4437;0.4440;0.4502;0.4505;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">224<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4502;0.4505;0.4566;0.4569;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">245<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4566;0.4569;0.4631;0.4634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">247<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4631;0.4634;0.4844;0.4847;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">255<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4844;0.4847;0.4909;0.4912;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">279<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4909;0.4912;0.4974;0.4977;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">325<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4974;0.4977;0.5039;0.5042;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">381<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5039;0.5042;0.5104;0.5106;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">426<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5104;0.5106;0.5168;0.5171;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">471<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5168;0.5171;0.5233;0.5236;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">492<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5233;0.5236;0.5298;0.5301;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">494<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5298;0.5301;0.5511;0.5514;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">502<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5511;0.5514;0.5576;0.5579;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">526<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5576;0.5579;0.5641;0.5644;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">572<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5641;0.5644;0.5705;0.5708;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">628<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5705;0.5708;0.5770;0.5773;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">673<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5770;0.5773;0.5835;0.5838;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">718<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5835;0.5838;0.5900;0.5903;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">739<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5900;0.5903;0.5965;0.5968;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">741<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5965;0.5968;0.6178;0.6181;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">749<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6178;0.6181;0.6242;0.6245;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">773<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6242;0.6245;0.6307;0.6310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">819<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6307;0.6310;0.6372;0.6375;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">875<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6372;0.6375;0.6437;0.6440;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">920<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6437;0.6440;0.6502;0.6505;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">965<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6502;0.6505;0.6566;0.6569;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">986<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6566;0.6569;0.6631;0.6634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">988<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6631;0.6634;0.6844;0.6847;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">996<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6844;0.6847;0.6909;0.6912;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,020<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6909;0.6912;0.6974;0.6977;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,066<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6974;0.6977;0.7039;0.7042;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,122<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7039;0.7042;0.7104;0.7106;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,167<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7104;0.7106;0.7168;0.7171;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,212<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7168;0.7171;0.7233;0.7236;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,233<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7233;0.7236;0.7298;0.7301;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="380" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,235<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7298;0.7301;1.0000" values="0;0;1;1"/></text>
<text x="512" y="404" text-anchor="start" style="font-size:15px;font-weight:500;fill:#64748b" opacity="0">いまは材質を貯めているだけ(光の計算はまだ 0)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.4145;0.4148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="404" text-anchor="start" style="font-size:15px;font-weight:500;fill:#64748b" opacity="0">光の計算は画面のマス数(448)が上限<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4145;0.4148;0.7701;0.7704;1.0000" values="0;0;1;1;0;0"/></text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7701;0.7704;1.0000" values="0;0;1;1"/><rect x="512" y="414" width="416" height="118" rx="12" fill="#f5f3ff" stroke="#7c3aed" stroke-width="2.5"/>
<text x="528" y="436" text-anchor="start" style="font-size:19px;font-weight:700;fill:#4c1d95">③ ライティングは画面ピクセルごとに1回</text>
<text x="528" y="462" text-anchor="start" style="font-size:17px;font-weight:700;fill:#4c1d95">247 px × ライト5 = 1,235回</text>
<text x="528" y="488" text-anchor="start" style="font-size:16px;font-weight:700;fill:#4c1d95">物体が10個でも100個でも、最大 448 px × 5 まで</text>
<text x="528" y="512" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">(代わりに G-Buffer の書き込みと読み込みが増える)</text>
</g>
<g opacity="0.25"><line x1="46.86" y1="50" x2="46.86" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="61.71" y1="50" x2="61.71" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="76.57" y1="50" x2="76.57" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="91.43" y1="50" x2="91.43" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="106.29" y1="50" x2="106.29" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="121.14" y1="50" x2="121.14" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="136.0" y1="50" x2="136.0" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="150.86" y1="50" x2="150.86" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="165.71" y1="50" x2="165.71" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="180.57" y1="50" x2="180.57" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="195.43" y1="50" x2="195.43" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="210.29" y1="50" x2="210.29" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="225.14" y1="50" x2="225.14" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="240.0" y1="50" x2="240.0" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="254.86" y1="50" x2="254.86" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="269.71" y1="50" x2="269.71" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="284.57" y1="50" x2="284.57" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="299.43" y1="50" x2="299.43" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="314.29" y1="50" x2="314.29" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="329.14" y1="50" x2="329.14" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="344.0" y1="50" x2="344.0" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="358.86" y1="50" x2="358.86" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="373.71" y1="50" x2="373.71" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="388.57" y1="50" x2="388.57" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="403.43" y1="50" x2="403.43" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="418.29" y1="50" x2="418.29" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="433.14" y1="50" x2="433.14" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="64.86" x2="448.0" y2="64.86" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="79.71" x2="448.0" y2="79.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="94.57" x2="448.0" y2="94.57" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="109.43" x2="448.0" y2="109.43" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="124.29" x2="448.0" y2="124.29" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="139.14" x2="448.0" y2="139.14" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="154.0" x2="448.0" y2="154.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="168.86" x2="448.0" y2="168.86" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="183.71" x2="448.0" y2="183.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="198.57" x2="448.0" y2="198.57" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="213.43" x2="448.0" y2="213.43" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="228.29" x2="448.0" y2="228.29" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="243.14" x2="448.0" y2="243.14" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="258.0" x2="448.0" y2="258.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="32" y1="272.86" x2="448.0" y2="272.86" stroke="#ffffff" stroke-width="0.5"/>
<rect x="32" y="50" width="416.0" height="237.71" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<g opacity="0.25"><line x1="526.86" y1="50" x2="526.86" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="541.71" y1="50" x2="541.71" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="556.57" y1="50" x2="556.57" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="571.43" y1="50" x2="571.43" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="586.29" y1="50" x2="586.29" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="601.14" y1="50" x2="601.14" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="616.0" y1="50" x2="616.0" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="630.86" y1="50" x2="630.86" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="645.71" y1="50" x2="645.71" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="660.57" y1="50" x2="660.57" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="675.43" y1="50" x2="675.43" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="690.29" y1="50" x2="690.29" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="705.14" y1="50" x2="705.14" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="720.0" y1="50" x2="720.0" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="734.86" y1="50" x2="734.86" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="749.71" y1="50" x2="749.71" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="764.57" y1="50" x2="764.57" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="779.43" y1="50" x2="779.43" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="794.29" y1="50" x2="794.29" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="809.14" y1="50" x2="809.14" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="824.0" y1="50" x2="824.0" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="838.86" y1="50" x2="838.86" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="853.71" y1="50" x2="853.71" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="868.57" y1="50" x2="868.57" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="883.43" y1="50" x2="883.43" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="898.29" y1="50" x2="898.29" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="913.14" y1="50" x2="913.14" y2="287.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="64.86" x2="928.0" y2="64.86" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="79.71" x2="928.0" y2="79.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="94.57" x2="928.0" y2="94.57" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="109.43" x2="928.0" y2="109.43" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="124.29" x2="928.0" y2="124.29" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="139.14" x2="928.0" y2="139.14" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="154.0" x2="928.0" y2="154.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="168.86" x2="928.0" y2="168.86" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="183.71" x2="928.0" y2="183.71" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="198.57" x2="928.0" y2="198.57" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="213.43" x2="928.0" y2="213.43" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="228.29" x2="928.0" y2="228.29" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="243.14" x2="928.0" y2="243.14" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="258.0" x2="928.0" y2="258.0" stroke="#ffffff" stroke-width="0.5"/>
<line x1="512" y1="272.86" x2="928.0" y2="272.86" stroke="#ffffff" stroke-width="0.5"/>
<rect x="512" y="50" width="416.0" height="237.71" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
</g>
<circle cx="84.0" cy="89.0" r="15" fill="#ff3340" opacity="0.28"/>
<circle cx="84.0" cy="89.0" r="7" fill="#ff3340" stroke="#ffffff" stroke-width="2.5"/>
<circle cx="390.8" cy="83.8" r="15" fill="#ffcc1a" opacity="0.28"/>
<circle cx="390.8" cy="83.8" r="7" fill="#ffcc1a" stroke="#ffffff" stroke-width="2.5"/>
<circle cx="240.0" cy="169.6" r="15" fill="#26e659" opacity="0.28"/>
<circle cx="240.0" cy="169.6" r="7" fill="#26e659" stroke="#ffffff" stroke-width="2.5"/>
<circle cx="99.6" cy="247.6" r="15" fill="#3380ff" opacity="0.28"/>
<circle cx="99.6" cy="247.6" r="7" fill="#3380ff" stroke="#ffffff" stroke-width="2.5"/>
<circle cx="380.4" cy="247.6" r="15" fill="#cc40ff" opacity="0.28"/>
<circle cx="380.4" cy="247.6" r="7" fill="#cc40ff" stroke="#ffffff" stroke-width="2.5"/>
<circle cx="564.0" cy="89.0" r="15" fill="#ff3340" opacity="0.28"/>
<circle cx="564.0" cy="89.0" r="7" fill="#ff3340" stroke="#ffffff" stroke-width="2.5"/>
<circle cx="870.8" cy="83.8" r="15" fill="#ffcc1a" opacity="0.28"/>
<circle cx="870.8" cy="83.8" r="7" fill="#ffcc1a" stroke="#ffffff" stroke-width="2.5"/>
<circle cx="720.0" cy="169.6" r="15" fill="#26e659" opacity="0.28"/>
<circle cx="720.0" cy="169.6" r="7" fill="#26e659" stroke="#ffffff" stroke-width="2.5"/>
<circle cx="579.6" cy="247.6" r="15" fill="#3380ff" opacity="0.28"/>
<circle cx="579.6" cy="247.6" r="7" fill="#3380ff" stroke="#ffffff" stroke-width="2.5"/>
<circle cx="860.4" cy="247.6" r="15" fill="#cc40ff" opacity="0.28"/>
<circle cx="860.4" cy="247.6" r="7" fill="#cc40ff" stroke="#ffffff" stroke-width="2.5"/>
<circle cx="480" cy="180" r="24" fill="#1f2937"/>
<text x="480" y="188" text-anchor="middle" style="font-size:22px;font-weight:700;fill:#ffffff">VS</text>
</svg>

<!-- fig:forward-deferred:end -->

| 見る所 | 内容 |
| --- | --- |
| Forward（左） | 球体を 1 つずつ描き、そのたびにライト 5 つを全部計算。赤枠は前の球体を上書きしたマス（前の計算が無駄になる） |
| Deferred（右） | ① 球体の「色・法線・深度」を G-Buffer に貯める　② 画面全体をライト 1 つずつ、斜めになぞる |
| カウンター | 実際に数えた計算回数。Forward は重なるほど増え、Deferred は画面のマス数 × ライト数で止まる |

## Forward（前向き）レンダリング

**物体を描くとき、その場で色（ライティング込み）を、完成させる**方式です。

<svg class="fig illust" viewBox="0 0 800 270" role="img" aria-label="Forward レンダリングの流れ">
<defs><marker id="fd1" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">Forward：物体ごとに、ピクセルごとに、ライトの数だけ、計算する</text>
<rect x="30" y="50" width="120" height="70" rx="10" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="3"/><text x="90" y="82" text-anchor="middle" style="font-weight:700">物体 A</text><text x="90" y="102" text-anchor="middle" style="font-size:12px">頂点 → ピクセル</text>
<rect x="30" y="140" width="120" height="70" rx="10" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="3"/><text x="90" y="172" text-anchor="middle" style="font-weight:700">物体 B</text><text x="90" y="192" text-anchor="middle" style="font-size:12px">頂点 → ピクセル</text>
<line x1="158" y1="85" x2="258" y2="125" stroke="currentColor" stroke-width="3" marker-end="url(#fd1)"/><line x1="158" y1="175" x2="258" y2="135" stroke="currentColor" stroke-width="3" marker-end="url(#fd1)"/>
<rect x="266" y="90" width="270" height="80" rx="12" fill="rgba(229,72,77,0.2)" stroke="currentColor" stroke-width="3"/>
<text x="401" y="122" text-anchor="middle" style="font-weight:700">ピクセルシェーダー</text><text x="401" y="144" text-anchor="middle" style="font-size:12px">全ライトを、ループで計算</text><text x="401" y="160" text-anchor="middle" style="font-size:12px">（隠れるピクセルでも、実行）</text>
<line x1="544" y1="130" x2="614" y2="130" stroke="currentColor" stroke-width="3" marker-end="url(#fd1)"/>
<rect x="622" y="90" width="150" height="80" rx="12" fill="rgba(46,160,67,0.22)" stroke="currentColor" stroke-width="3"/><text x="697" y="124" text-anchor="middle" style="font-weight:700">完成した色</text><text x="697" y="146" text-anchor="middle" style="font-size:12px">画面へ</text>
<text x="20" y="245" style="font-size:12px">コスト ＝ Σ（各物体のピクセル数 ×（オーバードロー）× 影響するライトの数）</text>
</svg>

### 何が重いのか

| 問題 | 説明 |
| --- | --- |
| オーバードロー | 手前の物体が後から描かれると奥の物体のライティング済みの色が、無駄になる。重い計算を捨てている |
| ライトが多いと | 1 ピクセルごとに全ライトをループ。100 個で、100 倍 |
| ライトの数が物体ごとに違う | 物体ごとにシェーダー（バリアント）を切り替える（ライト数 N のシェーダー）。ドロー コール・状態切り替えが増える |
| 範囲外のライト | 遠いライトも計算（影響がゼロでも）してしまう |

### 工夫と限界

| 工夫 | 説明 |
| --- | --- |
| Z プリパス（深度だけ、先に描く） | オーバードローのライティングを避ける（[オーバードロー](overdraw.md)）。ジオメトリを、2 回描く |
| ライトの上限（物体ごとに近い 4 つだけ） | 簡単だがライトがちらつく・多数のライトが使えない |
| ライトの事前の絞り込み | Tiled / Clustered Forward（[Tiled と Clustered](light-culling.md)） |

### Forward の、長所

| 長所 | 説明 |
| --- | --- |
| 帯域が少ない | G-Buffer が不要。直接、画面に書く |
| MSAA が使える | ハードウェアのアンチエイリアシングが、素直に使える |
| 半透明が扱える | 普通にブレンドできる |
| 材質が自由 | 物体ごとにシェーダーを変えて、特殊な表現（髪・肌・布）ができる |
| 単純 | 仕組みが分かりやすい |

ライトが少ない（太陽 ＋ 数個）なら、Forward が最適なことも多いです（VR・モバイル・スタイライズされた表現）。

## Deferred（遅延）レンダリング

<strong>「形と材質の情報」を、先にバッファ（G-Buffer）に書き</strong>、「ライティング」を、あとで画面全体に対して、まとめて行う方式です。

<svg class="fig illust" viewBox="0 0 820 300" role="img" aria-label="Deferred レンダリングの流れ">
<defs><marker id="fd2" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="24" class="fig-title">Deferred：① 形と材質を G-Buffer に書く　② 画面のピクセルごとに 1 回だけ、ライティング</text>
<rect x="20" y="60" width="130" height="100" rx="10" fill="rgba(76,139,245,0.22)" stroke="currentColor" stroke-width="3"/><text x="85" y="96" text-anchor="middle" style="font-weight:700">全ての物体</text><text x="85" y="118" text-anchor="middle" style="font-size:12px">材質の情報を</text><text x="85" y="136" text-anchor="middle" style="font-size:12px">書くだけ（軽い）</text>
<line x1="158" y1="110" x2="228" y2="110" stroke="currentColor" stroke-width="3" marker-end="url(#fd2)"/><text x="193" y="98" text-anchor="middle" style="font-size:12px">① 書く</text>
<g>
<rect x="236" y="48" width="140" height="30" fill="rgba(229,170,40,0.4)" stroke="currentColor" stroke-width="2"/><text x="306" y="68" text-anchor="middle" style="font-size:12px">アルベド（色）</text>
<rect x="236" y="82" width="140" height="30" fill="rgba(46,160,67,0.4)" stroke="currentColor" stroke-width="2"/><text x="306" y="102" text-anchor="middle" style="font-size:12px">法線</text>
<rect x="236" y="116" width="140" height="30" fill="rgba(150,100,230,0.4)" stroke="currentColor" stroke-width="2"/><text x="306" y="136" text-anchor="middle" style="font-size:12px">金属度・粗さ・AO</text>
<rect x="236" y="150" width="140" height="30" fill="rgba(229,72,77,0.35)" stroke="currentColor" stroke-width="2"/><text x="306" y="170" text-anchor="middle" style="font-size:12px">深度（位置を復元）</text>
</g>
<text x="306" y="198" text-anchor="middle" style="font-weight:700">G-Buffer</text>
<line x1="386" y1="110" x2="466" y2="110" stroke="currentColor" stroke-width="3" marker-end="url(#fd2)"/><text x="426" y="98" text-anchor="middle" style="font-size:12px">② 読む</text>
<rect x="474" y="60" width="170" height="100" rx="10" fill="rgba(229,72,77,0.2)" stroke="currentColor" stroke-width="3"/><text x="559" y="96" text-anchor="middle" style="font-weight:700">ライティング パス</text><text x="559" y="118" text-anchor="middle" style="font-size:12px">画面の各ピクセルに、</text><text x="559" y="136" text-anchor="middle" style="font-size:12px">1 回だけ、光を計算</text>
<line x1="652" y1="110" x2="716" y2="110" stroke="currentColor" stroke-width="3" marker-end="url(#fd2)"/>
<rect x="724" y="60" width="80" height="100" rx="10" fill="rgba(46,160,67,0.22)" stroke="currentColor" stroke-width="3"/><text x="764" y="116" text-anchor="middle" style="font-weight:700">画面</text>
<text x="20" y="250" style="font-size:12px">コスト ＝ ジオメトリ（G-Buffer への書き込み）＋ 画面のピクセル × ライト（物体の数に、無関係）</text>
<text x="20" y="272" style="font-size:12px">オーバードローしても、ライティングは「最後に残ったピクセル」だけ。無駄が、なくなる</text>
</svg>

### 何が改善するのか

| 改善 | 説明 |
| --- | --- |
| オーバードローのライティングが消える | ライティングは、最終的に見えるピクセルだけ（1 ピクセル 1 回） |
| 「物体 × ライト」が、「物体 ＋ ライト」に | ジオメトリの数とライトの数が独立。ライトをたくさん置ける |
| ライトの範囲を使える | ライトが影響する範囲（球・円錐）のピクセルだけ、計算できる（ライト ボリューム） |
| シェーダーの切り替えが、減る | ライティングのシェーダーは、1 種類。材質の違いは、G-Buffer の値 |
| ポストエフェクトに使える | G-Buffer（法線・深度）を、AO・SSR・デカールが再利用 |

ライトが数百個（街灯・たいまつ・窓の明かり）ある大規模なシーンで、Deferred が使われます。

### ライト ボリューム

ライトごとに影響する範囲（球・円錐）を、簡単な形として描き、その形が覆うピクセルだけを、ライティングします。

| ライトの種類 | 描く形 |
| --- | --- |
| ポイントライト | 球 |
| スポットライト | 円錐 |
| ディレクショナル（太陽） | フルスクリーン（画面全体） |

遠くのライトは、小さな範囲なので少ないピクセルで済みます。ライトごとに、G-Buffer を読み直す——これが次の問題になります。

### 代償（何が悪くなるか）

| 問題 | 説明 |
| --- | --- |
| 帯域が重い | G-Buffer の書き込み（複数 RT）と、ライトごとの読み込み。100 ライトで数百 GB/s（[メモリ帯域幅](bandwidth.md)） |
| MSAA が難しい | G-Buffer がサンプル数倍になる。TAA・FXAA で代用 |
| 半透明が使えない | G-Buffer に、1 ピクセル 1 つの情報しか、書けない。半透明は別の Forward パスで描く |
| 材質の多様性が制限される | G-Buffer に入る項目だけ。特殊な材質（髪・肌・布）は、工夫（シェーディング モデル ID） |
| ライトのブレンドの帯域 | ライトごとに結果を加算ブレンドで書く（読み書きが重なる） |
| G-Buffer の設計が、難しい | 何をどのフォーマットで詰めるか |

## 比べ

| | **Forward** | Deferred |
| --- | --- | --- |
| ライティングの回数 | 物体ごと（オーバードロー込み） | ピクセルごとに、1 回 |
| ライトが多い | 苦手（掛け算） | 得意 |
| 帯域 | 少ない | 多い（G-Buffer） |
| MSAA | ◎ | ×（難しい） |
| 半透明 | ◎ | ×（別パス） |
| 材質の自由度 | ◎ | △（G-Buffer に収まる範囲） |
| 向く場面 | ライトが少ない・VR・モバイル | ライトが多い・大規模な屋外 |

実際のエンジンは、組み合わせます：不透明は Deferred、半透明は Forward。Clustered / Tiled で、どちらもライトが多くても速くできます。

## 流れのまとめ（次の段階へ）

<svg class="fig illust" viewBox="0 0 800 130" role="img" aria-label="ライティング手法の進化">
<defs><marker id="fd3" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<rect x="10" y="30" width="150" height="70" rx="10" fill="rgba(150,150,150,0.2)" stroke="currentColor" stroke-width="2"/><text x="85" y="58" text-anchor="middle" style="font-weight:700">Forward</text><text x="85" y="80" text-anchor="middle" style="font-size:11px">物体×ピクセル×ライト</text>
<line x1="166" y1="65" x2="206" y2="65" stroke="currentColor" stroke-width="3" marker-end="url(#fd3)"/>
<rect x="214" y="30" width="150" height="70" rx="10" fill="rgba(76,139,245,0.25)" stroke="currentColor" stroke-width="2"/><text x="289" y="58" text-anchor="middle" style="font-weight:700">Deferred</text><text x="289" y="80" text-anchor="middle" style="font-size:11px">ピクセル×ライト</text>
<line x1="370" y1="65" x2="410" y2="65" stroke="currentColor" stroke-width="3" marker-end="url(#fd3)"/>
<rect x="418" y="30" width="170" height="70" rx="10" fill="rgba(46,160,67,0.25)" stroke="currentColor" stroke-width="2"/><text x="503" y="58" text-anchor="middle" style="font-weight:700">Tiled</text><text x="503" y="80" text-anchor="middle" style="font-size:11px">ピクセル×近くのライト</text>
<line x1="594" y1="65" x2="634" y2="65" stroke="currentColor" stroke-width="3" marker-end="url(#fd3)"/>
<rect x="642" y="30" width="150" height="70" rx="10" fill="rgba(229,170,40,0.3)" stroke="currentColor" stroke-width="2"/><text x="717" y="58" text-anchor="middle" style="font-weight:700">Clustered</text><text x="717" y="80" text-anchor="middle" style="font-size:11px">3 次元で、さらに絞る</text>
</svg>

**次のページ**：[Tiled と Clustered](light-culling.md)（ライトの絞り込みで帯域も計算も減らす）。

## よくあるミス

??? failure "ライトが数個なのに、Deferred にして、遅くなる"
    **G-Buffer の帯域**が、メリットを上回ります。Forward が速いこともあります。

??? failure "Deferred で、MSAA を使おうとして、帯域が爆発する"
    TAA など、別の方式にします。

??? failure "半透明を、Deferred のパスで描こうとする"
    半透明は、Forward パスで、後から描きます。

??? failure "ライトごとに、フルスクリーンで描画する"
    帯域が尽きます。ライト ボリュームで範囲を絞るか、Tiled / Clusteredに。

??? failure "G-Buffer に、位置（RGBA32F）を、保存する"
    深度から復元します（[メモリ帯域幅](bandwidth.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>Forward ＝ 物体を描きながら、ライティング</strong>。コスト ＝ 物体のピクセル（オーバードロー込み）× ライト
    - [x] Deferred ＝ G-Buffer に書いてから、画面の各ピクセルで 1 回だけ、ライティング
    - [x] 改善：オーバードローのライティングが消える。物体とライトの掛け算が足し算に
    - [x] 代償：G-Buffer の帯域・MSAA・半透明・材質の自由度
    - [x] ライトが少なければ Forward、多ければ Deferred。半透明は Forward で
    - [x] 次はTiled / Clustered（ライトの絞り込み）

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [メモリ帯域幅](bandwidth.md)
- [Tiled と Clustered](light-culling.md)
- [オーバードローと Z プリパス](overdraw.md)
- [法線とライティング](../3d/lighting-normals.md)
- [PBR](../3d/pbr.md)
