---
title: Forward と Deferred
tags:
  - 最適化
  - 3Dゲーム
---

# Forward と Deferred

**ライティング**（光の計算）を、**どの順番で行うか**で**描画の重さの構造**が大きく変わります。多くのエンジンは、**最初は Forward**（物体を描くたびに光も計算）で、**ライトが増える**と、**Deferred**（**形を先に描き、光をあとでまとめて計算**）に移ります。このページは、**Forward の何が重いのか**、**Deferred で何が改善するのか**、**その代償**を**目的から**説明します。

!!! tip "ポイント"
    - <strong>Forward</strong>：<strong>物体を描きながら、ピクセルごとに全ライトを計算</strong>。<strong>コスト ≒ 物体のピクセル（オーバードロー込み）× ライトの数</strong>。
    - <strong>問題</strong>：<strong>あとで隠れるピクセルにも、重いライティングをする</strong>（無駄）。<strong>ライトが多いとピクセルシェーダーが爆発</strong>。
    - <strong>Deferred</strong>：<strong>① G-Buffer に、形・材質の情報だけ書く　② 画面の、各ピクセルで、1 回だけ、ライティング</strong>。<strong>コスト ≒ 画面のピクセル × ライト</strong>。
    - <strong>改善</strong>：<strong>「物体の数」と「ライトの数」が、掛け算でなく、足し算に</strong>。<strong>オーバードローのライティングが消える</strong>。
    - <strong>代償</strong>：<strong>G-Buffer の帯域（書き込み・読み込み）</strong>。<strong>MSAA・半透明・材質の多様性が難しい</strong>。
    - <strong>ライトごとにフルスクリーンで読む</strong>のは、<strong>帯域が重い</strong>。→ <strong>Tiled / Clustered へ</strong>（[Tiled と Clustered](light-culling.md)）。

## 動きで比べる

**同じ画面（16×9 マス）・同じ球体 10 個・同じ色付きのライト 5 個**を、**Forward と Deferred で描く**様子です。**ライトが球体に当たると、ライトの色が付きます**（**近いライトほど濃く**）。**最後の絵は同じ**ですが、**計算の回数が違います**。

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
</defs>
<rect x="32" y="50" width="416.0" height="237.71" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="512" y="50" width="416.0" height="237.71" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<g clip-path="url(#fd-clip-f)"><rect x="76.57" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0390;0.0556;0.0645;0.0746;0.0867" values="none;#ffffff;#ffd9db;#ffd9db;#ffd9db;#ffd9db;#ffd9db"/></rect>
<rect x="91.43" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0392;0.0556;0.0641;0.0746;0.0867" values="none;#ffffff;#ffc1c4;#ffc1c4;#ffc1c4;#ffc1c4;#ffc1c4"/></rect>
<rect x="106.29" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0395;0.0556;0.0638;0.0746;0.0867" values="none;#ffffff;#ffcacd;#ffcacd;#fec9cc;#fec9cc;#fec9cc"/></rect>
<rect x="121.14" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0399;0.0556;0.0635;0.0747;0.0867" values="none;#ffffff;#ffeaec;#ffeaec;#fceaea;#fceaea;#fceaea"/></rect>
<rect x="61.71" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0389;0.0556;0.0647;0.0743;0.0867" values="none;#ffffff;#ffdee0;#ffdee0;#ffdee0;#ffdee0;#ffdee0"/></rect>
<rect x="76.57" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0386;0.0556;0.0643;0.0742;0.0867" values="none;#ffffff;#ffa2a8;#ffa2a8;#ffa2a8;#fea1a8;#fea1a8"/></rect>
<rect x="91.43" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0389;0.0556;0.0639;0.0742;0.0867" values="none;#ffffff;#ff8890;#ff8890;#fc888f;#fa878f;#fa878f"/></rect>
<rect x="106.29" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0394;0.0556;0.0636;0.0742;0.0867" values="none;#ffffff;#ff979e;#ff979e;#f6979a;#f4969a;#f4969a"/></rect>
<rect x="121.14" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0398;0.0556;0.0632;0.0743;0.0867" values="none;#ffffff;#ffc3c6;#ffc3c6;#f1c1be;#f0c1be;#f0c1be"/></rect>
<rect x="136.0" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0402;0.0556;0.0629;0.0744;0.0867" values="none;#ffffff;#fff6f6;#fff6f6;#f3f5ee;#f3f5ee;#f3f5ee"/></rect>
<rect x="61.71" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0391;0.0556;0.0645;0.0739;0.0867" values="none;#ffffff;#ffcacd;#ffcacd;#ffcacd;#fcc9cd;#fcc9cd"/></rect>
<rect x="76.57" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0389;0.0556;0.0641;0.0738;0.0867" values="none;#ffffff;#ff8d94;#ff8d94;#fe8d94;#f58a94;#f58a94"/></rect>
<rect x="91.43" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0391;0.0556;0.0637;0.0738;0.0867" values="none;#ffffff;#ff747d;#ff747d;#f8747a;#ec707a;#ec707a"/></rect>
<rect x="106.29" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0394;0.0556;0.0633;0.0738;0.0867" values="none;#ffffff;#ff858d;#ff858d;#ed8485;#e28085;#e28085"/></rect>
<rect x="121.14" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0398;0.0556;0.0630;0.0739;0.0867" values="none;#ffffff;#ffb4b8;#ffb4b8;#e2b1a9;#dcaea9;#dcaea9"/></rect>
<rect x="136.0" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0403;0.0556;0.0626;0.0740;0.0867" values="none;#ffffff;#ffebec;#ffebec;#e3e8d8;#e2e7d8;#e2e7d8"/></rect>
<rect x="61.71" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0394;0.0556;0.0644;0.0735;0.0867" values="none;#ffffff;#ffd6d9;#ffd6d9;#ffd6d9;#f7d2d9;#f7d2d9"/></rect>
<rect x="76.57" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0393;0.0556;0.0640;0.0734;0.0867" values="none;#ffffff;#ffa0a6;#ffa0a6;#fda0a5;#e998a5;#e998a5"/></rect>
<rect x="91.43" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0394;0.0556;0.0636;0.0734;0.0867" values="none;#ffffff;#ff8991;#ff8991;#f4898c;#da7f8c;#da7f8c"/></rect>
<rect x="106.29" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0397;0.0556;0.0632;0.0734;0.0867" values="none;#ffffff;#ff989e;#ff989e;#e69693;#ce8c93;#ce8c93"/></rect>
<rect x="121.14" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0400;0.0556;0.0628;0.0734;0.0867" values="none;#ffffff;#ffc1c5;#ffc1c5;#d9beaf;#cab5af;#cab5af"/></rect>
<rect x="136.0" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0404;0.0556;0.0624;0.0736;0.0867" values="none;#ffffff;#fff2f2;#fff2f2;#dceed9;#d6ead9;#d6ead9"/></rect>
<rect x="61.71" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0398;0.0556;0.0642;0.0730;0.0867" values="none;#ffffff;#fff9f9;#fff9f9;#fff9f9;#f7f4f9;#f7f4f9"/></rect>
<rect x="76.57" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0397;0.0556;0.0638;0.0730;0.0867" values="none;#ffffff;#ffcdd0;#ffcdd0;#fecdd0;#e0bed0;#e0bed0"/></rect>
<rect x="91.43" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0398;0.0556;0.0634;0.0729;0.0867" values="none;#ffffff;#ffbbbf;#ffbbbf;#f5bab9;#cea7b9;#cea7b9"/></rect>
<rect x="106.29" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0400;0.0556;0.0630;0.0730;0.0867" values="none;#ffffff;#ffc4c8;#ffc4c8;#e7c2ba;#c3afba;#c3afba"/></rect>
<rect x="121.14" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0403;0.0556;0.0626;0.0730;0.0867" values="none;#ffffff;#ffe2e4;#ffe2e4;#dddfcd;#c6d0cd;#c6d0cd"/></rect>
<rect x="136.0" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0406;0.0556;0.0622;0.0732;0.0867" values="none;#ffffff;#ffffff;#ffffff;#e8fced;#e2f8ed;#e2f8ed"/></rect>
<rect x="76.57" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0402;0.0556;0.0638;0.0725;0.0867" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#eff5ff;#eff5ff"/></rect>
<rect x="91.43" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0402;0.0556;0.0633;0.0725;0.0867" values="none;#ffffff;#fff3f4;#fff3f4;#fbf2f1;#d9def1;#d9def1"/></rect>
<rect x="106.29" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0404;0.0556;0.0629;0.0725;0.0867" values="none;#ffffff;#fff6f7;#fff6f7;#f3f5ee;#d3e1ee;#d3e1ee"/></rect>
<rect x="121.14" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0296;0.0406;0.0556;0.0625;0.0726;0.0867" values="none;#ffffff;#ffffff;#ffffff;#f3fef6;#e5f5f6;#e5f5f6"/></rect>
<circle cx="106.29" cy="106.46" r="47.54" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0293;0.0296;1.0000" values="0;0;1;1"/></circle>
<circle cx="106.29" cy="106.46" r="47.54" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0901;0.0904;1.0000" values="0;0;1;1"/></circle>
<circle cx="106.29" cy="106.46" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0293;0.0296;1.0000" values="0;0;1;1"/></circle>
<text x="106.29" y="111.46" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0293;0.0296;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><rect x="106.29" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1060;0.1222;0.1302;0.1409;0.1533" values="none;#ffffff;#ffdcde;#ffdcde;#ffdcde;#ffdcde;#ffdcde"/></rect>
<rect x="121.14" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1065;0.1222;0.1299;0.1409;0.1533" values="none;#ffffff;#ffcbce;#ffcbce;#ffcbce;#ffcbce;#ffcbce"/></rect>
<rect x="136.0" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1069;0.1222;0.1295;0.1410;0.1533" values="none;#ffffff;#ffdbdd;#ffdbdd;#fadada;#fadada;#fadada"/></rect>
<rect x="150.86" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1073;0.1222;0.1292;0.1412;0.1533" values="none;#ffffff;#fff9f9;#fff9f9;#faf8f6;#faf8f6;#faf8f6"/></rect>
<rect x="91.43" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1057;0.1222;0.1304;0.1404;0.1533" values="none;#ffffff;#ffdfe1;#ffdfe1;#ffdfe1;#ffdfe1;#ffdfe1"/></rect>
<rect x="106.29" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1061;0.1222;0.1300;0.1405;0.1533" values="none;#ffffff;#ffa7ac;#ffa7ac;#fea7ac;#fba5ac;#fba5ac"/></rect>
<rect x="121.14" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1065;0.1222;0.1296;0.1405;0.1533" values="none;#ffffff;#ff9ea4;#ff9ea4;#f49d9f;#f09b9f;#f09b9f"/></rect>
<rect x="136.0" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1069;0.1222;0.1293;0.1406;0.1533" values="none;#ffffff;#ffb7bc;#ffb7bc;#e7b5ae;#e4b4ae;#e4b4ae"/></rect>
<rect x="150.86" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1073;0.1222;0.1289;0.1408;0.1533" values="none;#ffffff;#ffdfe1;#ffdfe1;#e1dccd;#e1dccd;#e1dccd"/></rect>
<rect x="165.71" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1078;0.1218;0.1286;0.1409;0.1533" values="none;#ffffff;#ffffff;#ffffff;#f0fdf4;#f0fdf4;#f0fdf4"/></rect>
<rect x="91.43" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1061;0.1222;0.1302;0.1400;0.1533" values="none;#ffffff;#ffcace;#ffcace;#ffcace;#f9c8ce;#f9c8ce"/></rect>
<rect x="106.29" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1063;0.1222;0.1298;0.1400;0.1533" values="none;#ffffff;#ff9aa0;#ff9aa0;#f99a9e;#ea949e;#ea949e"/></rect>
<rect x="121.14" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1067;0.1222;0.1294;0.1401;0.1533" values="none;#ffffff;#ff959b;#ff959b;#e89391;#d88d91;#d88d91"/></rect>
<rect x="136.0" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1071;0.1222;0.1291;0.1402;0.1533" values="none;#ffffff;#ffb0b5;#ffb0b5;#d4ad9d;#c8a79d;#c8a79d"/></rect>
<rect x="150.86" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1074;0.1222;0.1287;0.1404;0.1533" values="none;#ffffff;#ffd9dc;#ffd9dc;#c8d4b7;#c3d0b7;#c3d0b7"/></rect>
<rect x="165.71" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1078;0.1218;0.1284;0.1406;0.1533" values="none;#ffffff;#fffdfd;#fffdfd;#d7f9df;#d7f8df;#d7f8df"/></rect>
<rect x="91.43" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1065;0.1222;0.1301;0.1396;0.1533" values="none;#ffffff;#ffdbdd;#ffdbdd;#ffdbdd;#f2d4dd;#f2d4dd"/></rect>
<rect x="106.29" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1067;0.1222;0.1297;0.1396;0.1533" values="none;#ffffff;#ffb1b6;#ffb1b6;#f7b1b2;#d9a3b2;#d9a3b2"/></rect>
<rect x="121.14" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1069;0.1222;0.1293;0.1397;0.1533" values="none;#ffffff;#ffacb1;#ffacb1;#e2aaa2;#c29ba2;#c29ba2"/></rect>
<rect x="136.0" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1073;0.1222;0.1289;0.1398;0.1533" values="none;#ffffff;#ffc3c6;#ffc3c6;#cabea7;#b3b0a7;#b3b0a7"/></rect>
<rect x="150.86" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1076;0.1222;0.1285;0.1400;0.1533" values="none;#ffffff;#ffe5e6;#ffe5e6;#bddeb9;#b1d5b9;#b1d5b9"/></rect>
<rect x="165.71" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1080;0.1219;0.1281;0.1402;0.1533" values="none;#ffffff;#ffffff;#ffffff;#d0f9db;#cef8db;#cef8db"/></rect>
<rect x="106.29" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1070;0.1222;0.1296;0.1392;0.1533" values="none;#ffffff;#ffdddf;#ffdddf;#fadcdb;#d5c8db;#d5c8db"/></rect>
<rect x="121.14" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1073;0.1222;0.1292;0.1393;0.1533" values="none;#ffffff;#ffd6d8;#ffd6d8;#e7d3c9;#bcbbc9;#bcbbc9"/></rect>
<rect x="136.0" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1075;0.1222;0.1288;0.1394;0.1533" values="none;#ffffff;#ffe3e5;#ffe3e5;#d1dec6;#b2c9c6;#b2c9c6"/></rect>
<rect x="150.86" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1079;0.1222;0.1283;0.1396;0.1533" values="none;#ffffff;#fff9f9;#fff9f9;#caf3d2;#bae7d2;#bae7d2"/></rect>
<rect x="121.14" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1076;0.1222;0.1291;0.1389;0.1533" values="none;#ffffff;#fffefe;#fffefe;#f8fef9;#daeaf9;#daeaf9"/></rect>
<rect x="136.0" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0963;0.1079;0.1222;0.1287;0.1391;0.1533" values="none;#ffffff;#ffffff;#ffffff;#eefdf2;#d7eef2;#d7eef2"/></rect>
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
<rect x="106.29" y="139.14" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="121.14" y="139.14" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
</g>
<circle cx="136.0" cy="121.31" r="44.57" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;1.0000" values="0;0;1;1"/></circle>
<circle cx="136.0" cy="121.31" r="44.57" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1567;0.1570;1.0000" values="0;0;1;1"/></circle>
<circle cx="136.0" cy="121.31" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;1.0000" values="0;0;1;1"/></circle>
<text x="136.0" y="126.31" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><rect x="344.0" y="50.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1836;0.1971;0.2096;0.2188" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff"/></rect>
<rect x="358.86" y="50.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1832;0.1974;0.2096;0.2188" values="none;#ffffff;#ffffff;#fffefc;#fffefc;#fffefc;#fffefc"/></rect>
<rect x="329.14" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1838;0.1965;0.2096;0.2185" values="none;#ffffff;#ffffff;#fff9e2;#f9f8de;#f9f8de;#f9f8de"/></rect>
<rect x="344.0" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1834;0.1968;0.2096;0.2184" values="none;#ffffff;#ffffff;#fff0ba;#fbefb8;#fbefb8;#fbefb8"/></rect>
<rect x="358.86" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1830;0.1971;0.2096;0.2183" values="none;#ffffff;#ffffff;#ffecaa;#feecaa;#feecaa;#feecaa"/></rect>
<rect x="373.71" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1827;0.1975;0.2096;0.2183" values="none;#ffffff;#ffffff;#fff1c1;#fff1c1;#fff1c1;#fff1c1"/></rect>
<rect x="314.29" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1842;0.1959;0.2096;0.2182" values="none;#ffffff;#ffffff;#fffdf5;#edfbe8;#edfbe8;#edfbe8"/></rect>
<rect x="329.14" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1838;0.1962;0.2096;0.2181" values="none;#ffffff;#ffffff;#fff1bf;#e9eeb2;#e9eeb2;#e8eeb2"/></rect>
<rect x="344.0" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1833;0.1965;0.2096;0.2180" values="none;#ffffff;#ffffff;#ffe58c;#f0e486;#f0e486;#efe286"/></rect>
<rect x="358.86" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1829;0.1969;0.2096;0.2179" values="none;#ffffff;#ffffff;#ffe074;#f9e072;#f9e072;#f8dd72"/></rect>
<rect x="373.71" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1825;0.1972;0.2096;0.2179" values="none;#ffffff;#ffffff;#ffe589;#ffe589;#ffe589;#fee389"/></rect>
<rect x="388.57" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1824;0.1976;0.2096;0.2179" values="none;#ffffff;#ffffff;#fff3cb;#fff3cb;#fff3cb;#fff3cb"/></rect>
<rect x="314.29" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1843;0.1956;0.2096;0.2178" values="none;#ffffff;#ffffff;#fffbef;#dbf7d5;#dbf7d5;#dbf6d5"/></rect>
<rect x="329.14" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1839;0.1960;0.2096;0.2177" values="none;#ffffff;#ffffff;#ffefb7;#d7eba1;#d7eba1;#d5e5a1"/></rect>
<rect x="344.0" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1835;0.1963;0.2096;0.2176" values="none;#ffffff;#ffffff;#ffe383;#e3e078;#e3e078;#e0d778"/></rect>
<rect x="358.86" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1831;0.1967;0.2096;0.2175" values="none;#ffffff;#ffffff;#ffde6a;#f2dc65;#f2dc65;#eed165"/></rect>
<rect x="373.71" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1828;0.1971;0.2096;0.2175" values="none;#ffffff;#ffffff;#ffe27d;#fce27c;#fce27c;#fad97c"/></rect>
<rect x="388.57" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1828;0.1974;0.2096;0.2175" values="none;#ffffff;#ffffff;#fff0bc;#fff0bc;#fff0bc;#feedbc"/></rect>
<rect x="314.29" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1844;0.1954;0.2096;0.2174" values="none;#ffffff;#ffffff;#fffef9;#d4f9d9;#d4f9d9;#d4f5d9"/></rect>
<rect x="329.14" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1840;0.1957;0.2096;0.2173" values="none;#ffffff;#ffffff;#fff3ca;#cdeeac;#cdeeac;#cae0ac"/></rect>
<rect x="344.0" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1837;0.1961;0.2096;0.2171" values="none;#ffffff;#ffffff;#ffe99e;#dae68d;#dae68d;#d5d08d"/></rect>
<rect x="358.86" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1834;0.1965;0.2096;0.2171" values="none;#ffffff;#ffffff;#ffe589;#ede382;#ede382;#e6cb82"/></rect>
<rect x="373.71" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1832;0.1969;0.2096;0.2171" values="none;#ffffff;#ffffff;#ffe99b;#fbe899;#fbe899;#f5d599"/></rect>
<rect x="388.57" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1832;0.1973;0.2096;0.2171" values="none;#ffffff;#ffffff;#fff5d2;#fff5d2;#fff5d2;#fcecd2"/></rect>
<rect x="314.29" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1846;0.1952;0.2096;0.2170" values="none;#ffffff;#ffffff;#ffffff;#ebfdef;#ebfdef;#eafaef"/></rect>
<rect x="329.14" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1843;0.1955;0.2096;0.2169" values="none;#ffffff;#ffffff;#fffbed;#d5f6cf;#d5f6cf;#d0e4cf"/></rect>
<rect x="344.0" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1840;0.1959;0.2096;0.2167" values="none;#ffffff;#ffffff;#fff4cf;#def1bb;#def1bb;#d6d2bb"/></rect>
<rect x="358.86" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1838;0.1963;0.2096;0.2167" values="none;#ffffff;#ffffff;#fff2c3;#eff0b9;#eff0b9;#e6ceb9"/></rect>
<rect x="373.71" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1836;0.1968;0.2096;0.2166" values="none;#ffffff;#ffffff;#fff5d2;#fcf5d0;#fcf5d0;#f5dad0"/></rect>
<rect x="388.57" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1836;0.1972;0.2096;0.2167" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#fdf9ff"/></rect>
<rect x="344.0" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1843;0.1958;0.2096;0.2163" values="none;#ffffff;#ffffff;#ffffff;#f2fdf5;#f2fdf5;#ece7f5"/></rect>
<rect x="358.86" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1630;0.1785;0.1841;0.1962;0.2096;0.2162" values="none;#ffffff;#ffffff;#fffffd;#fafef9;#fafef9;#f3e5f9"/></rect>
<circle cx="358.86" cy="103.49" r="47.54" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1627;0.1630;1.0000" values="0;0;1;1"/></circle>
<circle cx="358.86" cy="103.49" r="47.54" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2234;0.2237;1.0000" values="0;0;1;1"/></circle>
<circle cx="358.86" cy="103.49" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1627;0.1630;1.0000" values="0;0;1;1"/></circle>
<text x="358.86" y="108.49" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1627;0.1630;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><rect x="358.86" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2496;0.2636;0.2763;0.2846" values="none;#ffffff;#ffffff;#fffae7;#fef9e6;#fef9e6;#fef9e6"/></rect>
<rect x="373.71" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2492;0.2639;0.2763;0.2846" values="none;#ffffff;#ffffff;#fff0bd;#fef0bc;#fef0bc;#fef0bc"/></rect>
<rect x="388.57" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2491;0.2643;0.2763;0.2846" values="none;#ffffff;#ffffff;#fff0bc;#fff0bc;#fff0bc;#fff0bc"/></rect>
<rect x="403.43" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2495;0.2647;0.2763;0.2847" values="none;#ffffff;#ffffff;#fff9e5;#fff9e5;#fff9e5;#fff9e5"/></rect>
<rect x="344.0" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2501;0.2630;0.2763;0.2842" values="none;#ffffff;#ffffff;#fffefc;#fafef9;#fafef9;#fafef9"/></rect>
<rect x="358.86" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2498;0.2633;0.2763;0.2842" values="none;#ffffff;#ffffff;#ffefb5;#f5edb0;#f5edb0;#f4ecb0"/></rect>
<rect x="373.71" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2495;0.2637;0.2763;0.2841" values="none;#ffffff;#ffffff;#ffe589;#f9e486;#f9e486;#f8e086"/></rect>
<rect x="388.57" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2494;0.2641;0.2763;0.2842" values="none;#ffffff;#ffffff;#ffe487;#fee487;#fee487;#fde087"/></rect>
<rect x="403.43" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2497;0.2645;0.2763;0.2842" values="none;#ffffff;#ffffff;#ffeeb2;#ffeeb2;#ffeeb2;#ffedb2"/></rect>
<rect x="418.29" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2500;0.2649;0.2763;0.2843" values="none;#ffffff;#ffffff;#fffefb;#fffefb;#fffefb;#fffefb"/></rect>
<rect x="344.0" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2504;0.2628;0.2763;0.2838" values="none;#ffffff;#ffffff;#fffcf0;#f0fae5;#f0fae5;#eff8e5"/></rect>
<rect x="358.86" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2501;0.2632;0.2763;0.2837" values="none;#ffffff;#ffffff;#ffedb0;#ebeba5;#ebeba5;#e8e0a5"/></rect>
<rect x="373.71" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2499;0.2636;0.2763;0.2837" values="none;#ffffff;#ffffff;#ffe486;#f3e381;#f3e381;#efd381"/></rect>
<rect x="388.57" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2498;0.2640;0.2763;0.2838" values="none;#ffffff;#ffffff;#ffe484;#fce383;#fce383;#f7d483"/></rect>
<rect x="403.43" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2500;0.2644;0.2763;0.2838" values="none;#ffffff;#ffffff;#ffedac;#ffedac;#ffedac;#fce3ac"/></rect>
<rect x="418.29" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2503;0.2648;0.2763;0.2839" values="none;#ffffff;#ffffff;#fffbee;#fffbee;#fffbee;#fffaee"/></rect>
<rect x="344.0" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2507;0.2626;0.2763;0.2834" values="none;#ffffff;#ffffff;#ffffff;#f1fdf4;#f1fdf4;#f0f9f4"/></rect>
<rect x="358.86" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2504;0.2630;0.2763;0.2833" values="none;#ffffff;#ffffff;#fff4cd;#e9f1bf;#e9f1bf;#e3dbbf"/></rect>
<rect x="373.71" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2503;0.2634;0.2763;0.2833" values="none;#ffffff;#ffffff;#ffecab;#f1eba4;#f1eba4;#e9cca4"/></rect>
<rect x="388.57" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2503;0.2638;0.2763;0.2833" values="none;#ffffff;#ffffff;#ffecaa;#fbeca8;#fbeca8;#f2cea8"/></rect>
<rect x="403.43" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2504;0.2642;0.2763;0.2834" values="none;#ffffff;#ffffff;#fff3ca;#fff3ca;#fff3ca;#f9e0ca"/></rect>
<rect x="418.29" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2506;0.2647;0.2763;0.2835" values="none;#ffffff;#ffffff;#fffffe;#fffffe;#fffffe;#fefcfe"/></rect>
<rect x="358.86" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2508;0.2629;0.2763;0.2829" values="none;#ffffff;#ffffff;#fffdf8;#f1fcee;#f1fcee;#ece5ee"/></rect>
<rect x="373.71" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2507;0.2633;0.2763;0.2829" values="none;#ffffff;#ffffff;#fff8e2;#f5f7db;#f5f7db;#ebd2db"/></rect>
<rect x="388.57" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2507;0.2638;0.2763;0.2829" values="none;#ffffff;#ffffff;#fff8e1;#fcf8df;#fcf8df;#f3d4df"/></rect>
<rect x="403.43" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2296;0.2452;0.2508;0.2642;0.2763;0.2830" values="none;#ffffff;#ffffff;#fffdf7;#fffdf7;#fffdf7;#faeaf7"/></rect>
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
</g>
<circle cx="388.57" cy="118.34" r="41.6" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2293;0.2296;1.0000" values="0;0;1;1"/></circle>
<circle cx="388.57" cy="118.34" r="41.6" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2901;0.2904;1.0000" values="0;0;1;1"/></circle>
<circle cx="388.57" cy="118.34" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2293;0.2296;1.0000" values="0;0;1;1"/></circle>
<text x="388.57" y="123.34" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">4<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2293;0.2296;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><rect x="195.43" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3087;0.3210;0.3278;0.3410;0.3529" values="none;#ffffff;#fff4f4;#fff4f4;#fff4f4;#fff4f4;#fff4f4"/></rect>
<rect x="210.29" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3091;0.3206;0.3276;0.3413;0.3526" values="none;#ffffff;#fff8f9;#fff8f9;#f4f7f1;#f4f7f1;#f4f7f1"/></rect>
<rect x="225.14" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3095;0.3202;0.3274;0.3416;0.3523" values="none;#ffffff;#fffefe;#fffefd;#fafdf9;#fafdf9;#fafdf9"/></rect>
<rect x="180.57" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3084;0.3215;0.3278;0.3404;0.3531" values="none;#ffffff;#ffe1e3;#ffe1e3;#f3e0db;#f0dedb;#f0dedb"/></rect>
<rect x="195.43" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3088;0.3211;0.3274;0.3407;0.3527" values="none;#ffffff;#ffe4e5;#ffe4e5;#cedfc4;#ccddc4;#ccddc4"/></rect>
<rect x="210.29" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3092;0.3207;0.3272;0.3410;0.3524" values="none;#ffffff;#fff0f1;#fff0ef;#b7e8bc;#b6e7bc;#b6e7bc"/></rect>
<rect x="225.14" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3096;0.3203;0.3270;0.3413;0.3520" values="none;#ffffff;#fffbfb;#fff9f5;#bcf2c4;#bcf2c4;#bcf1c4"/></rect>
<rect x="240.0" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3100;0.3199;0.3270;0.3416;0.3517" values="none;#ffffff;#ffffff;#fffdf6;#dff9de;#dff9de;#dff9de"/></rect>
<rect x="165.71" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3082;0.3220;0.3279;0.3399;0.3532" values="none;#ffffff;#ffeaec;#ffeaec;#ffeaec;#f8e6ec;#f8e6ec"/></rect>
<rect x="180.57" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3086;0.3216;0.3275;0.3401;0.3529" values="none;#ffffff;#ffdadd;#ffdadd;#d5d6c1;#c8cec1;#c8cec1"/></rect>
<rect x="195.43" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3089;0.3212;0.3272;0.3404;0.3525" values="none;#ffffff;#ffe2e3;#ffe2e3;#a2d8a4;#99d1a4;#99d1a4"/></rect>
<rect x="210.29" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3093;0.3208;0.3268;0.3407;0.3521" values="none;#ffffff;#ffeff0;#ffefef;#81e195;#7edd95;#7edd95"/></rect>
<rect x="225.14" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3097;0.3204;0.3266;0.3411;0.3518" values="none;#ffffff;#fffafa;#fff9f4;#85eb9b;#84ea9b;#84e89b"/></rect>
<rect x="240.0" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3101;0.3200;0.3266;0.3414;0.3514" values="none;#ffffff;#ffffff;#fffcf4;#b0f3ba;#b0f3ba;#aff0ba"/></rect>
<rect x="254.86" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3105;0.3196;0.3268;0.3418;0.3511" values="none;#ffffff;#ffffff;#fffdf8;#f5fcf0;#f5fcf0;#f4fbf0"/></rect>
<rect x="165.71" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3085;0.3221;0.3278;0.3395;0.3531" values="none;#ffffff;#ffeced;#ffeced;#ffeced;#ece1ed;#ece1ed"/></rect>
<rect x="180.57" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3088;0.3217;0.3274;0.3398;0.3527" values="none;#ffffff;#ffe2e4;#ffe2e4;#c8dcbe;#b0cbbe;#b0cbbe"/></rect>
<rect x="195.43" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3092;0.3213;0.3270;0.3401;0.3523" values="none;#ffffff;#ffe9ea;#ffe9ea;#8edc9b;#80ce9b;#80ce9b"/></rect>
<rect x="210.29" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3095;0.3210;0.3266;0.3405;0.3519" values="none;#ffffff;#fff3f4;#fff3f4;#69e386;#63da86;#63d986"/></rect>
<rect x="225.14" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3099;0.3206;0.3262;0.3408;0.3515" values="none;#ffffff;#fffcfc;#fffbf8;#6cea8b;#6ae78b;#6ae28b"/></rect>
<rect x="240.0" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3103;0.3202;0.3262;0.3412;0.3512" values="none;#ffffff;#ffffff;#fffdf7;#9bf2ad;#9bf1ad;#9ae9ad"/></rect>
<rect x="254.86" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3107;0.3198;0.3266;0.3415;0.3508" values="none;#ffffff;#ffffff;#fffef9;#e7fbe7;#e7fbe7;#e6f5e7"/></rect>
<rect x="165.71" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3087;0.3222;0.3278;0.3392;0.3529" values="none;#ffffff;#fff9f9;#fff9f9;#fff9f9;#edeef9;#edeef9"/></rect>
<rect x="180.57" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3091;0.3219;0.3274;0.3395;0.3525" values="none;#ffffff;#fff0f1;#fff0f1;#d3ebd1;#b2d4d1;#b2d4d1"/></rect>
<rect x="195.43" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3094;0.3215;0.3270;0.3399;0.3521" values="none;#ffffff;#fff3f4;#fff3f4;#9de8ac;#87d4ac;#87d4ac"/></rect>
<rect x="210.29" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3097;0.3211;0.3266;0.3402;0.3517" values="none;#ffffff;#fffafa;#fffafa;#7bea97;#71de97;#70dc97"/></rect>
<rect x="225.14" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3101;0.3208;0.3262;0.3406;0.3513" values="none;#ffffff;#fffefe;#fffefd;#7fef9c;#7bea9c;#7ae39c"/></rect>
<rect x="240.0" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3105;0.3204;0.3262;0.3410;0.3510" values="none;#ffffff;#ffffff;#fffefc;#adf5be;#acf4be;#aae9be"/></rect>
<rect x="254.86" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3108;0.3201;0.3266;0.3414;0.3506" values="none;#ffffff;#ffffff;#fffffe;#f8fef8;#f8fef8;#f6f8f8"/></rect>
<rect x="180.57" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3093;0.3221;0.3275;0.3393;0.3524" values="none;#ffffff;#fffcfc;#fffcfc;#f4fbf3;#d6e8f3;#d6e8f3"/></rect>
<rect x="195.43" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3097;0.3217;0.3271;0.3396;0.3520" values="none;#ffffff;#fffcfc;#fffcfc;#caf6d4;#b0e2d4;#b0e2d4"/></rect>
<rect x="210.29" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3100;0.3214;0.3268;0.3400;0.3516" values="none;#ffffff;#fffefe;#fffefe;#b1f5c3;#a3e9c3;#a2e7c3"/></rect>
<rect x="225.14" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3103;0.3210;0.3266;0.3404;0.3512" values="none;#ffffff;#ffffff;#ffffff;#b7f6c8;#b1f2c8;#b0ecc8"/></rect>
<rect x="240.0" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3107;0.3207;0.3266;0.3408;0.3508" values="none;#ffffff;#ffffff;#ffffff;#dffbe6;#dffbe6;#ddf3e6"/></rect>
<rect x="195.43" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3099;0.3219;0.3274;0.3395;0.3519" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#f6faff;#f6faff"/></rect>
<rect x="210.29" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3102;0.3216;0.3271;0.3399;0.3515" values="none;#ffffff;#ffffff;#ffffff;#f7fef9;#f0f9f9;#f0f9f9"/></rect>
<rect x="225.14" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2963;0.3106;0.3213;0.3270;0.3403;0.3510" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#feffff;#fefeff"/></rect>
<circle cx="217.71" cy="159.94" r="49.03" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;1.0000" values="0;0;1;1"/></circle>
<circle cx="217.71" cy="159.94" r="49.03" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3567;0.3570;1.0000" values="0;0;1;1"/></circle>
<circle cx="217.71" cy="159.94" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;1.0000" values="0;0;1;1"/></circle>
<text x="217.71" y="164.94" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">5<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><rect x="225.14" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3763;0.3869;0.3937;0.4080;0.4187" values="none;#ffffff;#fffefe;#fffefe;#fefefd;#fefefd;#fefefd"/></rect>
<rect x="240.0" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3767;0.3865;0.3937;0.4083;0.4184" values="none;#ffffff;#fffefe;#fffdfb;#e5fae8;#e5fae8;#e5fae8"/></rect>
<rect x="254.86" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3771;0.3861;0.3938;0.4087;0.4180" values="none;#ffffff;#ffffff;#fffdf5;#e9fae5;#e9fae5;#e9fae5"/></rect>
<rect x="269.71" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3775;0.3857;0.3941;0.4090;0.4178" values="none;#ffffff;#ffffff;#fffdf6;#fffdf6;#fffdf6;#fffdf6"/></rect>
<rect x="210.29" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3760;0.3875;0.3935;0.4074;0.4188" values="none;#ffffff;#fffcfc;#fffcfc;#fcfbfa;#fcfbfa;#fcfbfa"/></rect>
<rect x="225.14" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3764;0.3871;0.3933;0.4077;0.4184" values="none;#ffffff;#fff9f9;#fff9f9;#c0f2ca;#bff1ca;#bff1ca"/></rect>
<rect x="240.0" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3768;0.3867;0.3933;0.4081;0.4181" values="none;#ffffff;#fffdfd;#fffbf6;#a3f0b2;#a3f0b2;#a3efb2"/></rect>
<rect x="254.86" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3772;0.3863;0.3935;0.4084;0.4178" values="none;#ffffff;#ffffff;#fffbee;#abf1b2;#abf1b2;#abeeb2"/></rect>
<rect x="269.71" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3776;0.3859;0.3938;0.4088;0.4174" values="none;#ffffff;#ffffff;#fff9e6;#d2f4c7;#d2f4c7;#d1eec7"/></rect>
<rect x="284.57" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3780;0.3856;0.3942;0.4092;0.4172" values="none;#ffffff;#ffffff;#fffcf2;#fffcf2;#fffcf2;#fefaf2"/></rect>
<rect x="210.29" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3762;0.3876;0.3933;0.4071;0.4186" values="none;#ffffff;#fff9f9;#fff9f9;#dcf5e0;#d7f1e0;#d7f1e0"/></rect>
<rect x="225.14" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3766;0.3872;0.3929;0.4075;0.4182" values="none;#ffffff;#fff9fa;#fff9f9;#9aeead;#95e9ad;#95e9ad"/></rect>
<rect x="240.0" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3769;0.3869;0.3929;0.4078;0.4178" values="none;#ffffff;#fffdfd;#fffcf8;#79ec94;#77ea94;#76e694"/></rect>
<rect x="254.86" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3773;0.3865;0.3933;0.4082;0.4175" values="none;#ffffff;#ffffff;#fffcf0;#84ed97;#84ed97;#82e297"/></rect>
<rect x="269.71" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3777;0.3861;0.3937;0.4086;0.4172" values="none;#ffffff;#ffffff;#fffae8;#b3f1b3;#b3f1b3;#b0e0b3"/></rect>
<rect x="284.57" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3781;0.3858;0.3941;0.4090;0.4169" values="none;#ffffff;#ffffff;#fffbeb;#eff9e0;#eff9e0;#ecebe0"/></rect>
<rect x="210.29" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3764;0.3878;0.3933;0.4069;0.4184" values="none;#ffffff;#fffcfc;#fffcfc;#dcf8e2;#d2f1e2;#d2f1e2"/></rect>
<rect x="225.14" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3768;0.3874;0.3929;0.4073;0.4180" values="none;#ffffff;#fffcfc;#fffcfc;#99f0af;#92e9af;#91e8af"/></rect>
<rect x="240.0" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3771;0.3871;0.3929;0.4076;0.4176" values="none;#ffffff;#fffefe;#fffefc;#78ee96;#75ea96;#74e296"/></rect>
<rect x="254.86" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3775;0.3867;0.3933;0.4080;0.4173" values="none;#ffffff;#ffffff;#fffdf7;#83ef9b;#83ee9b;#80dc9b"/></rect>
<rect x="269.71" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3779;0.3864;0.3937;0.4084;0.4169" values="none;#ffffff;#ffffff;#fffcf1;#b3f3ba;#b3f3ba;#add8ba"/></rect>
<rect x="284.57" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3783;0.3861;0.3941;0.4088;0.4166" values="none;#ffffff;#ffffff;#fffcf4;#effbe8;#effbe8;#eae4e8"/></rect>
<rect x="210.29" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3766;0.3880;0.3935;0.4067;0.4182" values="none;#ffffff;#ffffff;#ffffff;#fcfffd;#f5fafd;#f5fafd"/></rect>
<rect x="225.14" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3770;0.3877;0.3932;0.4071;0.4178" values="none;#ffffff;#ffffff;#ffffff;#bff7ce;#b6efce;#b5eece"/></rect>
<rect x="240.0" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3773;0.3873;0.3932;0.4075;0.4174" values="none;#ffffff;#ffffff;#ffffff;#a2f4b7;#9df0b7;#9ce6b7"/></rect>
<rect x="254.86" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3777;0.3870;0.3935;0.4079;0.4171" values="none;#ffffff;#ffffff;#fffffd;#aaf5bd;#a9f3bd;#a5dfbd"/></rect>
<rect x="269.71" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3781;0.3867;0.3938;0.4083;0.4167" values="none;#ffffff;#ffffff;#fffefb;#d1f9d9;#d1f9d9;#cbdcd9"/></rect>
<rect x="284.57" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3785;0.3864;0.3942;0.4087;0.4163" values="none;#ffffff;#ffffff;#fffffe;#fffffe;#fffffe;#fbf0fe"/></rect>
<rect x="225.14" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3772;0.3879;0.3937;0.4069;0.4177" values="none;#ffffff;#ffffff;#ffffff;#fefffe;#fafcfe;#fafcfe"/></rect>
<rect x="240.0" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3776;0.3876;0.3937;0.4073;0.4173" values="none;#ffffff;#ffffff;#ffffff;#e4fceb;#e1faeb;#e0f5eb"/></rect>
<rect x="254.86" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3779;0.3873;0.3938;0.4077;0.4169" values="none;#ffffff;#ffffff;#ffffff;#e8fcee;#e8fcee;#e5efee"/></rect>
<rect x="269.71" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3630;0.3783;0.3870;0.3941;0.4082;0.4165" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#fcf4ff"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3627;0.3630;0.4279;0.4281;1.0000" values="0;0;1;1;0;0"/><rect x="225.14" y="124.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="240.0" y="124.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
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
<circle cx="254.86" cy="168.86" r="44.57" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3627;0.3630;1.0000" values="0;0;1;1"/></circle>
<circle cx="254.86" cy="168.86" r="44.57" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4234;0.4237;1.0000" values="0;0;1;1"/></circle>
<circle cx="254.86" cy="168.86" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3627;0.3630;1.0000" values="0;0;1;1"/></circle>
<text x="254.86" y="173.86" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">6<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3627;0.3630;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><rect x="91.43" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4415;0.4556;0.4633;0.4712;0.4867" values="none;#ffffff;#ffe6e7;#ffe6e7;#fee6e7;#f8e3e7;#f8e3e7"/></rect>
<rect x="106.29" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4415;0.4556;0.4629;0.4713;0.4867" values="none;#ffffff;#ffe0e2;#ffe0e2;#f5dfdb;#e7d7db;#e7d7db"/></rect>
<rect x="121.14" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4417;0.4556;0.4625;0.4714;0.4867" values="none;#ffffff;#ffebec;#ffebec;#eee9e0;#e9e6e0;#e9e6e0"/></rect>
<rect x="76.57" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4419;0.4556;0.4638;0.4709;0.4867" values="none;#ffffff;#ffedef;#ffedef;#ffedef;#eae1ef;#eae1ef"/></rect>
<rect x="91.43" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4419;0.4556;0.4634;0.4708;0.4867" values="none;#ffffff;#ffdee0;#ffdee0;#f9dedc;#c0bddc;#c0bddc"/></rect>
<rect x="106.29" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4420;0.4556;0.4630;0.4709;0.4867" values="none;#ffffff;#ffdcdf;#ffdcdf;#ebdad1;#abb5d1;#abb5d1"/></rect>
<rect x="121.14" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4421;0.4556;0.4626;0.4711;0.4867" values="none;#ffffff;#ffe6e7;#ffe6e7;#dce2cf;#afc5cf;#afc5cf"/></rect>
<rect x="136.0" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4423;0.4556;0.4622;0.4714;0.4867" values="none;#ffffff;#fff5f6;#fff5f6;#daf1da;#cce7da;#cce7da"/></rect>
<rect x="76.57" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4423;0.4556;0.4639;0.4705;0.4867" values="none;#ffffff;#fff2f3;#fff2f3;#fff2f3;#c8d2f3;#c8d2f3"/></rect>
<rect x="91.43" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4423;0.4556;0.4635;0.4704;0.4867" values="none;#ffffff;#ffe9eb;#ffe9eb;#f9e9e6;#95aee6;#95aee6"/></rect>
<rect x="106.29" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4424;0.4556;0.4631;0.4705;0.4867" values="none;#ffffff;#ffe9ea;#ffe9ea;#ebe7dc;#80a5dc;#80a5dc"/></rect>
<rect x="121.14" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4425;0.4556;0.4628;0.4708;0.4867" values="none;#ffffff;#ffeff0;#ffeff0;#dbebd6;#8db6d6;#8db6d6"/></rect>
<rect x="136.0" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4426;0.4556;0.4624;0.4711;0.4867" values="none;#ffffff;#fff9f9;#fff9f9;#d4f4d9;#b0dad9;#b0dad9"/></rect>
<rect x="150.86" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4428;0.4556;0.4620;0.4715;0.4864" values="none;#ffffff;#ffffff;#ffffff;#eefdf2;#eefdf2;#eefdf2"/></rect>
<rect x="76.57" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4427;0.4556;0.4641;0.4702;0.4867" values="none;#ffffff;#fffbfb;#fffbfb;#fffbfb;#c0d4fb;#c0d4fb"/></rect>
<rect x="91.43" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4427;0.4556;0.4637;0.4700;0.4867" values="none;#ffffff;#fff7f7;#fff7f7;#fcf6f5;#8ab1f5;#8ab1f5"/></rect>
<rect x="106.29" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4428;0.4556;0.4633;0.4702;0.4867" values="none;#ffffff;#fff6f7;#fff6f7;#f2f5ed;#77a7ed;#77a7ed"/></rect>
<rect x="121.14" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4429;0.4556;0.4630;0.4705;0.4867" values="none;#ffffff;#fff9fa;#fff9fa;#e5f6e6;#89b8e6;#89b8e6"/></rect>
<rect x="136.0" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4430;0.4556;0.4626;0.4709;0.4867" values="none;#ffffff;#fffefe;#fffefe;#e0fae6;#b4dbe6;#b4dbe6"/></rect>
<rect x="150.86" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4432;0.4556;0.4623;0.4713;0.4863" values="none;#ffffff;#ffffff;#ffffff;#f4fef6;#f4fef6;#f4fef6"/></rect>
<rect x="76.57" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4431;0.4556;0.4643;0.4701;0.4867" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#dbe9ff;#dbe9ff"/></rect>
<rect x="91.43" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4431;0.4556;0.4639;0.4697;0.4867" values="none;#ffffff;#fffefe;#fffefe;#fffefe;#a8c8fe;#a8c8fe"/></rect>
<rect x="106.29" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4432;0.4556;0.4635;0.4700;0.4867" values="none;#ffffff;#fffefe;#fffefe;#fafdfa;#97befa;#97befa"/></rect>
<rect x="121.14" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4433;0.4556;0.4632;0.4705;0.4867" values="none;#ffffff;#ffffff;#ffffff;#f3fdf6;#a9cdf6;#a9cdf6"/></rect>
<rect x="136.0" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4434;0.4556;0.4628;0.4709;0.4867" values="none;#ffffff;#ffffff;#ffffff;#f2fef5;#d6ebf5;#d6ebf5"/></rect>
<rect x="91.43" y="258.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4436;0.4556;0.4641;0.4701;0.4867" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#e7f0ff;#e7f0ff"/></rect>
<rect x="106.29" y="258.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4436;0.4556;0.4638;0.4703;0.4867" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#d8e7ff;#d8e7ff"/></rect>
<rect x="121.14" y="258.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4296;0.4437;0.4556;0.4634;0.4706;0.4867" values="none;#ffffff;#ffffff;#ffffff;#fefffe;#e8f1fe;#e8f1fe"/></rect>
<circle cx="115.2" cy="228.29" r="44.57" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;1.0000" values="0;0;1;1"/></circle>
<circle cx="115.2" cy="228.29" r="44.57" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4901;0.4904;1.0000" values="0;0;1;1"/></circle>
<circle cx="115.2" cy="228.29" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;1.0000" values="0;0;1;1"/></circle>
<text x="115.2" y="233.29" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">7<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><rect x="121.14" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5080;0.5222;0.5291;0.5385;0.5533" values="none;#ffffff;#ffd9db;#ffd9db;#f6d8d5;#e5ced5;#e5ced5"/></rect>
<rect x="136.0" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5082;0.5222;0.5287;0.5387;0.5533" values="none;#ffffff;#ffdadc;#ffdadc;#e1d7c8;#d0cdc8;#d0cdc8"/></rect>
<rect x="150.86" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5085;0.5222;0.5283;0.5389;0.5533" values="none;#ffffff;#ffeaeb;#ffeaeb;#d3e5cc;#cde1cc;#cde1cc"/></rect>
<rect x="165.71" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5087;0.5222;0.5278;0.5392;0.5529" values="none;#ffffff;#fffcfd;#fffcfd;#e6f9e9;#e6f9e9;#e6f9e9"/></rect>
<rect x="106.29" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5082;0.5222;0.5296;0.5380;0.5533" values="none;#ffffff;#ffe6e8;#ffe6e8;#ffe6e8;#ded4e8;#ded4e8"/></rect>
<rect x="121.14" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5084;0.5222;0.5292;0.5381;0.5533" values="none;#ffffff;#ffd9db;#ffd9db;#edd7cf;#b4b7cf;#b4b7cf"/></rect>
<rect x="136.0" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5086;0.5222;0.5287;0.5383;0.5533" values="none;#ffffff;#ffdddf;#ffdddf;#d1d8c0;#a1b9c0;#a1b9c0"/></rect>
<rect x="150.86" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5088;0.5222;0.5283;0.5386;0.5532" values="none;#ffffff;#ffebec;#ffebec;#bbe4bc;#a1d0bc;#a1d0bc"/></rect>
<rect x="165.71" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5090;0.5222;0.5279;0.5389;0.5528" values="none;#ffffff;#fffafa;#fffafa;#c1f2cb;#bbeecb;#bbeecb"/></rect>
<rect x="106.29" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5086;0.5222;0.5297;0.5375;0.5533" values="none;#ffffff;#fff0f1;#fff0f1;#fff0f1;#c5cef1;#c5cef1"/></rect>
<rect x="121.14" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5088;0.5222;0.5293;0.5377;0.5533" values="none;#ffffff;#ffe8ea;#ffe8ea;#eee6de;#98b2de;#98b2de"/></rect>
<rect x="136.0" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5089;0.5222;0.5289;0.5380;0.5533" values="none;#ffffff;#ffebed;#ffebed;#d4e7ce;#8ab5ce;#8ab5ce"/></rect>
<rect x="150.86" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5091;0.5222;0.5285;0.5383;0.5531" values="none;#ffffff;#fff4f5;#fff4f5;#bfedc6;#93cbc6;#93cbc6"/></rect>
<rect x="165.71" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5094;0.5222;0.5281;0.5387;0.5527" values="none;#ffffff;#fffdfd;#fffdfd;#c1f6ce;#b2eace;#b2eace"/></rect>
<rect x="106.29" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5090;0.5222;0.5298;0.5372;0.5533" values="none;#ffffff;#fffcfc;#fffcfc;#fffcfc;#cbdcfc;#cbdcfc"/></rect>
<rect x="121.14" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5092;0.5222;0.5294;0.5374;0.5533" values="none;#ffffff;#fff8f8;#fff8f8;#f7f7f2;#9dbff2;#9dbff2"/></rect>
<rect x="136.0" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5093;0.5222;0.5290;0.5378;0.5533" values="none;#ffffff;#fff9f9;#fff9f9;#e4f6e5;#93bfe5;#93bfe5"/></rect>
<rect x="150.86" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5095;0.5222;0.5287;0.5381;0.5530" values="none;#ffffff;#fffdfd;#fffdfd;#d5f8dd;#a4d4dd;#a4d4dd"/></rect>
<rect x="165.71" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5097;0.5222;0.5283;0.5385;0.5526" values="none;#ffffff;#ffffff;#ffffff;#dafbe3;#ccf0e3;#ccf0e3"/></rect>
<rect x="121.14" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5096;0.5222;0.5296;0.5372;0.5533" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#ccdfff;#ccdfff"/></rect>
<rect x="136.0" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5097;0.5222;0.5293;0.5376;0.5533" values="none;#ffffff;#ffffff;#ffffff;#f8fefa;#c2dbfa;#c2dbfa"/></rect>
<rect x="150.86" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4963;0.5099;0.5222;0.5289;0.5380;0.5530" values="none;#ffffff;#ffffff;#ffffff;#f3fef6;#d6eaf6;#d6eaf6"/></rect>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;0.5612;0.5615;1.0000" values="0;0;1;1;0;0"/><rect x="165.71" y="168.86" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="106.29" y="183.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="121.14" y="183.71" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="106.29" y="198.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="121.14" y="198.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="136.0" y="198.57" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="106.29" y="213.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="121.14" y="213.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="136.0" y="213.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="150.86" y="213.43" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="121.14" y="228.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="136.0" y="228.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="150.86" y="228.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
</g>
<circle cx="144.91" cy="204.51" r="41.6" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;1.0000" values="0;0;1;1"/></circle>
<circle cx="144.91" cy="204.51" r="41.6" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5567;0.5570;1.0000" values="0;0;1;1"/></circle>
<circle cx="144.91" cy="204.51" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;1.0000" values="0;0;1;1"/></circle>
<text x="144.91" y="209.51" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">8<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><rect x="344.0" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5855;0.5958;0.6096;0.6151" values="none;#ffffff;#ffffff;#fffbec;#ecf9df;#ecf9df;#ecf8df"/></rect>
<rect x="358.86" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5854;0.5962;0.6096;0.6150" values="none;#ffffff;#ffffff;#fff7da;#f0f5d0;#f0f5d0;#ebe3d0"/></rect>
<rect x="373.71" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5853;0.5967;0.6096;0.6149" values="none;#ffffff;#ffffff;#fff6d6;#f9f5d2;#f9f5d2;#f4e2d2"/></rect>
<rect x="388.57" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5853;0.5971;0.6096;0.6150" values="none;#ffffff;#ffffff;#fff9e6;#fff9e5;#fff9e5;#fef6e5"/></rect>
<rect x="329.14" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5860;0.5955;0.6096;0.6151" values="none;#ffffff;#ffffff;#fffef9;#e2fae4;#e2fae4;#e2f8e4"/></rect>
<rect x="344.0" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5859;0.5959;0.6096;0.6148" values="none;#ffffff;#ffffff;#fffae8;#daf6ce;#daf6ce;#d0cdce"/></rect>
<rect x="358.86" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5858;0.5963;0.6096;0.6146" values="none;#ffffff;#ffffff;#fff7da;#e6f4c9;#e6f4c9;#d5b2c9"/></rect>
<rect x="373.71" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5857;0.5967;0.6096;0.6145" values="none;#ffffff;#ffffff;#fff6d7;#f4f5d0;#f4f5d0;#e2afd0"/></rect>
<rect x="388.57" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5857;0.5972;0.6096;0.6146" values="none;#ffffff;#ffffff;#fff8e0;#fdf8df;#fdf8df;#f0c9df"/></rect>
<rect x="403.43" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5858;0.5976;0.6096;0.6148" values="none;#ffffff;#ffffff;#fffdf4;#fffdf4;#fffdf4;#fdf6f4"/></rect>
<rect x="329.14" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5864;0.5957;0.6096;0.6148" values="none;#ffffff;#ffffff;#fffefb;#dafadf;#dafadf;#d5e3df"/></rect>
<rect x="344.0" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5863;0.5961;0.6096;0.6145" values="none;#ffffff;#ffffff;#fffcf1;#d9f7d5;#d9f7d5;#c8aed5"/></rect>
<rect x="358.86" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5862;0.5965;0.6096;0.6142" values="none;#ffffff;#ffffff;#fffae9;#e6f7d7;#e6f7d7;#cb8bd7"/></rect>
<rect x="373.71" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5861;0.5969;0.6096;0.6141" values="none;#ffffff;#ffffff;#fff9e6;#f4f8df;#f4f8df;#d788df"/></rect>
<rect x="388.57" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5861;0.5973;0.6096;0.6142" values="none;#ffffff;#ffffff;#fffbeb;#fdfaea;#fdfaea;#e7a6ea"/></rect>
<rect x="403.43" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5862;0.5977;0.6096;0.6145" values="none;#ffffff;#ffffff;#fffdf7;#fffdf7;#fffdf7;#f6ddf7"/></rect>
<rect x="329.14" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5868;0.5959;0.6096;0.6146" values="none;#ffffff;#ffffff;#ffffff;#e4fcea;#e4fcea;#dee0ea"/></rect>
<rect x="344.0" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5867;0.5963;0.6096;0.6142" values="none;#ffffff;#ffffff;#fffefb;#e3fbe6;#e3fbe6;#cfa7e6"/></rect>
<rect x="358.86" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5866;0.5967;0.6096;0.6139" values="none;#ffffff;#ffffff;#fffdf7;#edfbe9;#edfbe9;#ce80e9"/></rect>
<rect x="373.71" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5866;0.5970;0.6096;0.6137" values="none;#ffffff;#ffffff;#fffdf5;#f8fcf0;#f8fcf0;#d77cf0"/></rect>
<rect x="388.57" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5866;0.5974;0.6096;0.6139" values="none;#ffffff;#ffffff;#fffdf8;#fefdf7;#fefdf7;#e59ef7"/></rect>
<rect x="403.43" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5866;0.5978;0.6096;0.6143" values="none;#ffffff;#ffffff;#fffffd;#fffffd;#fffffd;#f5d9fd"/></rect>
<rect x="329.14" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5872;0.5962;0.6096;0.6146" values="none;#ffffff;#ffffff;#ffffff;#f6fef8;#f6fef8;#f3f3f8"/></rect>
<rect x="344.0" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5871;0.5965;0.6096;0.6142" values="none;#ffffff;#ffffff;#ffffff;#f2fdf5;#f2fdf5;#e2bff5"/></rect>
<rect x="358.86" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5870;0.5969;0.6096;0.6137" values="none;#ffffff;#ffffff;#fffffe;#f7fef8;#f7fef8;#dd9af8"/></rect>
<rect x="373.71" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5870;0.5972;0.6096;0.6134" values="none;#ffffff;#ffffff;#fffffe;#fdfefc;#fdfefc;#e197fc"/></rect>
<rect x="388.57" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5870;0.5976;0.6096;0.6138" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#ecb7ff"/></rect>
<rect x="403.43" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5870;0.5980;0.6096;0.6142" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#faeeff"/></rect>
<rect x="344.0" y="258.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5875;0.5968;0.6096;0.6143" values="none;#ffffff;#ffffff;#ffffff;#fefffe;#fefffe;#f9effe"/></rect>
<rect x="358.86" y="258.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5874;0.5971;0.6096;0.6140" values="none;#ffffff;#ffffff;#ffffff;#fefffe;#fefffe;#f2d3fe"/></rect>
<rect x="373.71" y="258.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5874;0.5975;0.6096;0.6138" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#f3d1ff"/></rect>
<rect x="388.57" y="258.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5630;0.5785;0.5874;0.5978;0.6096;0.6140" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#faebff"/></rect>
<circle cx="373.71" cy="228.29" r="47.54" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;1.0000" values="0;0;1;1"/></circle>
<circle cx="373.71" cy="228.29" r="47.54" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6234;0.6237;1.0000" values="0;0;1;1"/></circle>
<circle cx="373.71" cy="228.29" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;1.0000" values="0;0;1;1"/></circle>
<text x="373.71" y="233.29" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">9<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-f)"><rect x="329.14" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6516;0.6620;0.6763;0.6828" values="none;#ffffff;#ffffff;#fffcf1;#fafbed;#fafbed;#fafbed"/></rect>
<rect x="344.0" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6514;0.6624;0.6763;0.6826" values="none;#ffffff;#ffffff;#fffbeb;#fffbeb;#fffbeb;#fffbeb"/></rect>
<rect x="314.29" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6522;0.6616;0.6763;0.6826" values="none;#ffffff;#ffffff;#fffbee;#d4f6d0;#d4f6d0;#d3f4d0"/></rect>
<rect x="329.14" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6519;0.6620;0.6763;0.6824" values="none;#ffffff;#ffffff;#fff6d8;#d8f2be;#d8f2be;#d3e0be"/></rect>
<rect x="344.0" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6518;0.6624;0.6763;0.6822" values="none;#ffffff;#ffffff;#fff4cc;#ebf1c0;#ebf1c0;#e5d8c0"/></rect>
<rect x="358.86" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6516;0.6629;0.6763;0.6821" values="none;#ffffff;#ffffff;#fff6d7;#fdf6d5;#fdf6d5;#f8e6d5"/></rect>
<rect x="299.43" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6528;0.6613;0.6757;0.6826" values="none;#ffffff;#ffffff;#ffffff;#dbfbe3;#dbfbe3;#dbfbe3"/></rect>
<rect x="314.29" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6525;0.6617;0.6762;0.6823" values="none;#ffffff;#ffffff;#fffcf0;#bff4c2;#bff4c2;#baddc2"/></rect>
<rect x="329.14" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6523;0.6621;0.6763;0.6820" values="none;#ffffff;#ffffff;#fff8df;#caf2bb;#caf2bb;#bfc0bb"/></rect>
<rect x="344.0" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6521;0.6625;0.6763;0.6818" values="none;#ffffff;#ffffff;#fff6d5;#e3f2c2;#e3f2c2;#d3b3c2"/></rect>
<rect x="358.86" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6520;0.6629;0.6763;0.6817" values="none;#ffffff;#ffffff;#fff7da;#f8f6d5;#f8f6d5;#eac2d5"/></rect>
<rect x="373.71" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6520;0.6633;0.6763;0.6816" values="none;#ffffff;#ffffff;#fffcf2;#fffcf2;#fffcf2;#fbeff2"/></rect>
<rect x="299.43" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6531;0.6614;0.6757;0.6824" values="none;#ffffff;#ffffff;#ffffff;#dbfbe4;#dbfbe4;#dbfae4"/></rect>
<rect x="314.29" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6529;0.6618;0.6761;0.6820" values="none;#ffffff;#ffffff;#fffef9;#c4f7cd;#c4f7cd;#bcd1cd"/></rect>
<rect x="329.14" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6527;0.6622;0.6763;0.6817" values="none;#ffffff;#ffffff;#fffbef;#cff6cd;#cff6cd;#bfadcd"/></rect>
<rect x="344.0" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6525;0.6626;0.6763;0.6814" values="none;#ffffff;#ffffff;#fffae8;#e6f7d7;#e6f7d7;#d09cd7"/></rect>
<rect x="358.86" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6524;0.6630;0.6763;0.6813" values="none;#ffffff;#ffffff;#fffbeb;#fafae7;#fafae7;#e5ade7"/></rect>
<rect x="373.71" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6524;0.6634;0.6763;0.6812" values="none;#ffffff;#ffffff;#fffef9;#fffef9;#fffef9;#f8e2f9"/></rect>
<rect x="314.29" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6533;0.6620;0.6760;0.6818" values="none;#ffffff;#ffffff;#ffffff;#ddfbe5;#ddfbe5;#d5d9e5"/></rect>
<rect x="329.14" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6531;0.6624;0.6763;0.6815" values="none;#ffffff;#ffffff;#fffefc;#e3fbe6;#e3fbe6;#d1b3e6"/></rect>
<rect x="344.0" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6530;0.6628;0.6763;0.6811" values="none;#ffffff;#ffffff;#fffef9;#f2fcef;#f2fcef;#dba3ef"/></rect>
<rect x="358.86" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6529;0.6631;0.6763;0.6809" values="none;#ffffff;#ffffff;#fffefb;#fefefa;#fefefa;#ebb7fa"/></rect>
<rect x="314.29" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6536;0.6623;0.6760;0.6817" values="none;#ffffff;#ffffff;#ffffff;#fdfffd;#fdfffd;#fcfcfd"/></rect>
<rect x="329.14" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6535;0.6626;0.6763;0.6813" values="none;#ffffff;#ffffff;#ffffff;#f9fefb;#f9fefb;#f0dbfb"/></rect>
<rect x="344.0" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6534;0.6630;0.6763;0.6809" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#f2d1ff"/></rect>
<rect x="358.86" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6296;0.6452;0.6533;0.6633;0.6763;0.6805" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff;#fbefff"/></rect>
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
<rect x="329.14" y="228.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="344.0" y="228.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
<rect x="358.86" y="228.29" width="14.86" height="14.86" fill="none" stroke="#e5484d" stroke-width="1.2"/>
</g>
<circle cx="344.0" cy="201.54" r="41.6" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;1.0000" values="0;0;1;1"/></circle>
<circle cx="344.0" cy="201.54" r="41.6" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6901;0.6904;1.0000" values="0;0;1;1"/></circle>
<circle cx="344.0" cy="201.54" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;1.0000" values="0;0;1;1"/></circle>
<text x="344.0" y="206.54" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">10<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;1.0000" values="0;0;1;1"/></text>
</g>
<g clip-path="url(#fd-clip-d)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;1.0000" values="0;0;1;1"/><rect x="556.57" y="64.86" width="5.15" height="15.16" fill="#ffffff"/>
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
<rect x="556.57" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4208;0.4875;0.5542;0.6208;0.6875" values="none;#ffd9db;#ffd9db;#ffd9db;#ffd9db;#ffd9db"/></rect>
<rect x="571.43" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4220;0.4887;0.5554;0.6220;0.6887" values="none;#ffc1c4;#ffc1c4;#ffc1c4;#ffc1c4;#ffc1c4"/></rect>
<rect x="586.29" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4233;0.4899;0.5566;0.6233;0.6899" values="none;#ffcacd;#ffcacd;#fec9cc;#fec9cc;#fec9cc"/></rect>
<rect x="601.14" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4245;0.4911;0.5578;0.6245;0.6911" values="none;#ffeaec;#ffeaec;#fceaea;#fceaea;#fceaea"/></rect>
<rect x="541.71" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4208;0.4875;0.5542;0.6208;0.6875" values="none;#ffdee0;#ffdee0;#ffdee0;#ffdee0;#ffdee0"/></rect>
<rect x="556.57" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4220;0.4887;0.5554;0.6220;0.6887" values="none;#ffa2a8;#ffa2a8;#ffa2a8;#fea1a8;#fea1a8"/></rect>
<rect x="571.43" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4233;0.4899;0.5566;0.6233;0.6899" values="none;#ff8890;#ff8890;#fc888f;#fa878f;#fa878f"/></rect>
<rect x="541.71" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4220;0.4887;0.5554;0.6220;0.6887" values="none;#ffcacd;#ffcacd;#ffcacd;#fcc9cd;#fcc9cd"/></rect>
<rect x="556.57" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4233;0.4899;0.5566;0.6233;0.6899" values="none;#ff8d94;#ff8d94;#fe8d94;#f58a94;#f58a94"/></rect>
<rect x="541.71" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4233;0.4899;0.5566;0.6233;0.6899" values="none;#ffd6d9;#ffd6d9;#ffd6d9;#f7d2d9;#f7d2d9"/></rect>
<rect x="556.57" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4245;0.4911;0.5578;0.6245;0.6911" values="none;#ffa0a6;#ffa0a6;#fda0a5;#e998a5;#e998a5"/></rect>
<rect x="541.71" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4245;0.4911;0.5578;0.6245;0.6911" values="none;#fff9f9;#fff9f9;#fff9f9;#f7f4f9;#f7f4f9"/></rect>
<rect x="556.57" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257;0.4923;0.5590;0.6257;0.6923" values="none;#ffcdd0;#ffcdd0;#fecdd0;#e0bed0;#e0bed0"/></rect>
<rect x="556.57" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4269;0.4935;0.5602;0.6269;0.6935" values="none;#ffffff;#ffffff;#ffffff;#eff5ff;#eff5ff"/></rect>
<rect x="571.43" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4281;0.4947;0.5614;0.6281;0.6947" values="none;#fff3f4;#fff3f4;#fbf2f1;#d9def1;#d9def1"/></rect>
<circle cx="586.29" cy="106.46" r="47.54" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;1.0000" values="0;0;1;1"/></circle>
<circle cx="586.29" cy="106.46" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;1.0000" values="0;0;1;1"/></circle>
<text x="586.29" y="111.46" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;1.0000" values="0;0;1;1"/></text>
<circle cx="586.29" cy="106.46" r="47.54" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0923;0.0926;1.0000" values="0;0;1;1"/><rect x="586.29" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
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
<rect x="601.14" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="154.0" width="5.15" height="15.16" fill="#6af2b3"/>
<rect x="611.05" y="154.0" width="5.15" height="15.16" fill="#bbbbbb"/>
<rect x="616.0" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="154.0" width="5.15" height="15.16" fill="#95f2b3"/>
<rect x="625.9" y="154.0" width="5.15" height="15.16" fill="#bbbbbb"/>
</g>
<rect x="586.29" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4245;0.4911;0.5578;0.6245;0.6911" values="none;#ffdcde;#ffdcde;#ffdcde;#ffdcde;#ffdcde"/></rect>
<rect x="601.14" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257;0.4923;0.5590;0.6257;0.6923" values="none;#ffcbce;#ffcbce;#ffcbce;#ffcbce;#ffcbce"/></rect>
<rect x="616.0" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4269;0.4935;0.5602;0.6269;0.6935" values="none;#ffdbdd;#ffdbdd;#fadada;#fadada;#fadada"/></rect>
<rect x="630.86" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4281;0.4947;0.5614;0.6281;0.6947" values="none;#fff9f9;#fff9f9;#faf8f6;#faf8f6;#faf8f6"/></rect>
<rect x="571.43" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4245;0.4911;0.5578;0.6245;0.6911" values="none;#ffdfe1;#ffdfe1;#ffdfe1;#ffdfe1;#ffdfe1"/></rect>
<rect x="586.29" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257;0.4923;0.5590;0.6257;0.6923" values="none;#ffa7ac;#ffa7ac;#fea7ac;#fba5ac;#fba5ac"/></rect>
<rect x="601.14" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4269;0.4935;0.5602;0.6269;0.6935" values="none;#ff9ea4;#ff9ea4;#f49d9f;#f09b9f;#f09b9f"/></rect>
<rect x="616.0" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4281;0.4947;0.5614;0.6281;0.6947" values="none;#ffb7bc;#ffb7bc;#e7b5ae;#e4b4ae;#e4b4ae"/></rect>
<rect x="630.86" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4293;0.4960;0.5626;0.6293;0.6960" values="none;#ffdfe1;#ffdfe1;#e1dccd;#e1dccd;#e1dccd"/></rect>
<rect x="645.71" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4305;0.4972;0.5638;0.6305;0.6972" values="none;#ffffff;#ffffff;#f0fdf4;#f0fdf4;#f0fdf4"/></rect>
<rect x="571.43" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4257;0.4923;0.5590;0.6257;0.6923" values="none;#ffcace;#ffcace;#ffcace;#f9c8ce;#f9c8ce"/></rect>
<rect x="586.29" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4269;0.4935;0.5602;0.6269;0.6935" values="none;#ff9aa0;#ff9aa0;#f99a9e;#ea949e;#ea949e"/></rect>
<rect x="601.14" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4281;0.4947;0.5614;0.6281;0.6947" values="none;#ff959b;#ff959b;#e89391;#d88d91;#d88d91"/></rect>
<rect x="616.0" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4293;0.4960;0.5626;0.6293;0.6960" values="none;#ffb0b5;#ffb0b5;#d4ad9d;#c8a79d;#c8a79d"/></rect>
<rect x="630.86" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4305;0.4972;0.5638;0.6305;0.6972" values="none;#ffd9dc;#ffd9dc;#c8d4b7;#c3d0b7;#c3d0b7"/></rect>
<rect x="645.71" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4317;0.4984;0.5650;0.6317;0.6984" values="none;#fffdfd;#fffdfd;#d7f9df;#d7f8df;#d7f8df"/></rect>
<rect x="571.43" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4269;0.4935;0.5602;0.6269;0.6935" values="none;#ffdbdd;#ffdbdd;#ffdbdd;#f2d4dd;#f2d4dd"/></rect>
<rect x="586.29" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4281;0.4947;0.5614;0.6281;0.6947" values="none;#ffb1b6;#ffb1b6;#f7b1b2;#d9a3b2;#d9a3b2"/></rect>
<rect x="601.14" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4293;0.4960;0.5626;0.6293;0.6960" values="none;#ffacb1;#ffacb1;#e2aaa2;#c29ba2;#c29ba2"/></rect>
<rect x="616.0" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4305;0.4972;0.5638;0.6305;0.6972" values="none;#ffc3c6;#ffc3c6;#cabea7;#b3b0a7;#b3b0a7"/></rect>
<rect x="630.86" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4317;0.4984;0.5650;0.6317;0.6984" values="none;#ffe5e6;#ffe5e6;#bddeb9;#b1d5b9;#b1d5b9"/></rect>
<rect x="645.71" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329;0.4996;0.5662;0.6329;0.6996" values="none;#ffffff;#ffffff;#d0f9db;#cef8db;#cef8db"/></rect>
<rect x="586.29" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4293;0.4960;0.5626;0.6293;0.6960" values="none;#ffdddf;#ffdddf;#fadcdb;#d5c8db;#d5c8db"/></rect>
<rect x="601.14" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4305;0.4972;0.5638;0.6305;0.6972" values="none;#ffd6d8;#ffd6d8;#e7d3c9;#bcbbc9;#bcbbc9"/></rect>
<rect x="616.0" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4317;0.4984;0.5650;0.6317;0.6984" values="none;#ffe3e5;#ffe3e5;#d1dec6;#b2c9c6;#b2c9c6"/></rect>
<rect x="630.86" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329;0.4996;0.5662;0.6329;0.6996" values="none;#fff9f9;#fff9f9;#caf3d2;#bae7d2;#bae7d2"/></rect>
<rect x="601.14" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4317;0.4984;0.5650;0.6317;0.6984" values="none;#fffefe;#fffefe;#f8fef9;#daeaf9;#daeaf9"/></rect>
<rect x="616.0" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329;0.4996;0.5662;0.6329;0.6996" values="none;#ffffff;#ffffff;#eefdf2;#d7eef2;#d7eef2"/></rect>
<circle cx="616.0" cy="121.31" r="44.57" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0923;0.0926;1.0000" values="0;0;1;1"/></circle>
<circle cx="616.0" cy="121.31" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0923;0.0926;1.0000" values="0;0;1;1"/></circle>
<text x="616.0" y="126.31" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0923;0.0926;1.0000" values="0;0;1;1"/></text>
<circle cx="616.0" cy="121.31" r="44.57" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1256;0.1259;1.0000" values="0;0;1;1"/><rect x="824.0" y="50.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="50.0" width="5.15" height="15.16" fill="#6c0498"/>
<rect x="833.9" y="50.0" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="838.86" y="50.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="50.0" width="5.15" height="15.16" fill="#930498"/>
<rect x="848.76" y="50.0" width="5.15" height="15.16" fill="#aaaaaa"/>
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
<rect x="824.0" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="139.14" width="5.15" height="15.16" fill="#6cf3b2"/>
<rect x="833.9" y="139.14" width="5.15" height="15.16" fill="#aaaaaa"/>
<rect x="838.86" y="139.14" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="843.81" y="139.14" width="5.15" height="15.16" fill="#93f3b2"/>
<rect x="848.76" y="139.14" width="5.15" height="15.16" fill="#aaaaaa"/>
</g>
<rect x="824.0" y="50.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413;0.5080;0.5747;0.6413;0.7080" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#ffffff"/></rect>
<rect x="838.86" y="50.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425;0.5092;0.5759;0.6425;0.7092" values="none;#ffffff;#fffefc;#fffefc;#fffefc;#fffefc"/></rect>
<rect x="809.14" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413;0.5080;0.5747;0.6413;0.7080" values="none;#ffffff;#fff9e2;#f9f8de;#f9f8de;#f9f8de"/></rect>
<rect x="824.0" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425;0.5092;0.5759;0.6425;0.7092" values="none;#ffffff;#fff0ba;#fbefb8;#fbefb8;#fbefb8"/></rect>
<rect x="838.86" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438;0.5104;0.5771;0.6438;0.7104" values="none;#ffffff;#ffecaa;#feecaa;#feecaa;#feecaa"/></rect>
<rect x="853.71" y="64.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450;0.5116;0.5783;0.6450;0.7116" values="none;#ffffff;#fff1c1;#fff1c1;#fff1c1;#fff1c1"/></rect>
<rect x="794.29" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413;0.5080;0.5747;0.6413;0.7080" values="none;#ffffff;#fffdf5;#edfbe8;#edfbe8;#edfbe8"/></rect>
<rect x="809.14" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425;0.5092;0.5759;0.6425;0.7092" values="none;#ffffff;#fff1bf;#e9eeb2;#e9eeb2;#e8eeb2"/></rect>
<rect x="824.0" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438;0.5104;0.5771;0.6438;0.7104" values="none;#ffffff;#ffe58c;#f0e486;#f0e486;#efe286"/></rect>
<rect x="794.29" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425;0.5092;0.5759;0.6425;0.7092" values="none;#ffffff;#fffbef;#dbf7d5;#dbf7d5;#dbf6d5"/></rect>
<rect x="809.14" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438;0.5104;0.5771;0.6438;0.7104" values="none;#ffffff;#ffefb7;#d7eba1;#d7eba1;#d5e5a1"/></rect>
<rect x="794.29" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438;0.5104;0.5771;0.6438;0.7104" values="none;#ffffff;#fffef9;#d4f9d9;#d4f9d9;#d4f5d9"/></rect>
<rect x="809.14" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450;0.5116;0.5783;0.6450;0.7116" values="none;#ffffff;#fff3ca;#cdeeac;#cdeeac;#cae0ac"/></rect>
<rect x="794.29" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450;0.5116;0.5783;0.6450;0.7116" values="none;#ffffff;#ffffff;#ebfdef;#ebfdef;#eafaef"/></rect>
<rect x="809.14" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462;0.5128;0.5795;0.6462;0.7128" values="none;#ffffff;#fffbed;#d5f6cf;#d5f6cf;#d0e4cf"/></rect>
<rect x="824.0" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486;0.5152;0.5819;0.6486;0.7152" values="none;#ffffff;#ffffff;#f2fdf5;#f2fdf5;#ece7f5"/></rect>
<circle cx="838.86" cy="103.49" r="47.54" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1256;0.1259;1.0000" values="0;0;1;1"/></circle>
<circle cx="838.86" cy="103.49" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1256;0.1259;1.0000" values="0;0;1;1"/></circle>
<text x="838.86" y="108.49" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1256;0.1259;1.0000" values="0;0;1;1"/></text>
<circle cx="838.86" cy="103.49" r="47.54" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1590;0.1593;1.0000" values="0;0;1;1"/><rect x="838.86" y="79.71" width="5.15" height="15.16" fill="#ffffff"/>
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
</g>
<rect x="838.86" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450;0.5116;0.5783;0.6450;0.7116" values="none;#ffffff;#fffae7;#fef9e6;#fef9e6;#fef9e6"/></rect>
<rect x="853.71" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462;0.5128;0.5795;0.6462;0.7128" values="none;#ffffff;#fff0bd;#fef0bc;#fef0bc;#fef0bc"/></rect>
<rect x="868.57" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474;0.5140;0.5807;0.6474;0.7140" values="none;#ffffff;#fff0bc;#fff0bc;#fff0bc;#fff0bc"/></rect>
<rect x="883.43" y="79.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486;0.5152;0.5819;0.6486;0.7152" values="none;#ffffff;#fff9e5;#fff9e5;#fff9e5;#fff9e5"/></rect>
<rect x="824.0" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450;0.5116;0.5783;0.6450;0.7116" values="none;#ffffff;#fffefc;#fafef9;#fafef9;#fafef9"/></rect>
<rect x="838.86" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462;0.5128;0.5795;0.6462;0.7128" values="none;#ffffff;#ffefb5;#f5edb0;#f5edb0;#f4ecb0"/></rect>
<rect x="853.71" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474;0.5140;0.5807;0.6474;0.7140" values="none;#ffffff;#ffe589;#f9e486;#f9e486;#f8e086"/></rect>
<rect x="868.57" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486;0.5152;0.5819;0.6486;0.7152" values="none;#ffffff;#ffe487;#fee487;#fee487;#fde087"/></rect>
<rect x="883.43" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498;0.5165;0.5831;0.6498;0.7165" values="none;#ffffff;#ffeeb2;#ffeeb2;#ffeeb2;#ffedb2"/></rect>
<rect x="898.29" y="94.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510;0.5177;0.5843;0.6510;0.7177" values="none;#ffffff;#fffefb;#fffefb;#fffefb;#fffefb"/></rect>
<rect x="824.0" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462;0.5128;0.5795;0.6462;0.7128" values="none;#ffffff;#fffcf0;#f0fae5;#f0fae5;#eff8e5"/></rect>
<rect x="838.86" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474;0.5140;0.5807;0.6474;0.7140" values="none;#ffffff;#ffedb0;#ebeba5;#ebeba5;#e8e0a5"/></rect>
<rect x="853.71" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486;0.5152;0.5819;0.6486;0.7152" values="none;#ffffff;#ffe486;#f3e381;#f3e381;#efd381"/></rect>
<rect x="868.57" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498;0.5165;0.5831;0.6498;0.7165" values="none;#ffffff;#ffe484;#fce383;#fce383;#f7d483"/></rect>
<rect x="883.43" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510;0.5177;0.5843;0.6510;0.7177" values="none;#ffffff;#ffedac;#ffedac;#ffedac;#fce3ac"/></rect>
<rect x="898.29" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522;0.5189;0.5855;0.6522;0.7189" values="none;#ffffff;#fffbee;#fffbee;#fffbee;#fffaee"/></rect>
<rect x="824.0" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474;0.5140;0.5807;0.6474;0.7140" values="none;#ffffff;#ffffff;#f1fdf4;#f1fdf4;#f0f9f4"/></rect>
<rect x="838.86" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486;0.5152;0.5819;0.6486;0.7152" values="none;#ffffff;#fff4cd;#e9f1bf;#e9f1bf;#e3dbbf"/></rect>
<rect x="853.71" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498;0.5165;0.5831;0.6498;0.7165" values="none;#ffffff;#ffecab;#f1eba4;#f1eba4;#e9cca4"/></rect>
<rect x="868.57" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510;0.5177;0.5843;0.6510;0.7177" values="none;#ffffff;#ffecaa;#fbeca8;#fbeca8;#f2cea8"/></rect>
<rect x="883.43" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522;0.5189;0.5855;0.6522;0.7189" values="none;#ffffff;#fff3ca;#fff3ca;#fff3ca;#f9e0ca"/></rect>
<rect x="898.29" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4534;0.5201;0.5867;0.6534;0.7201" values="none;#ffffff;#fffffe;#fffffe;#fffffe;#fefcfe"/></rect>
<rect x="838.86" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498;0.5165;0.5831;0.6498;0.7165" values="none;#ffffff;#fffdf8;#f1fcee;#f1fcee;#ece5ee"/></rect>
<rect x="853.71" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510;0.5177;0.5843;0.6510;0.7177" values="none;#ffffff;#fff8e2;#f5f7db;#f5f7db;#ebd2db"/></rect>
<rect x="868.57" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522;0.5189;0.5855;0.6522;0.7189" values="none;#ffffff;#fff8e1;#fcf8df;#fcf8df;#f3d4df"/></rect>
<rect x="883.43" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4534;0.5201;0.5867;0.6534;0.7201" values="none;#ffffff;#fffdf7;#fffdf7;#fffdf7;#faeaf7"/></rect>
<circle cx="868.57" cy="118.34" r="41.6" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1590;0.1593;1.0000" values="0;0;1;1"/></circle>
<circle cx="868.57" cy="118.34" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1590;0.1593;1.0000" values="0;0;1;1"/></circle>
<text x="868.57" y="123.34" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">4<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1590;0.1593;1.0000" values="0;0;1;1"/></text>
<circle cx="868.57" cy="118.34" r="41.6" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;1.0000" values="0;0;1;1"/><rect x="675.43" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="680.38" y="109.43" width="5.15" height="15.16" fill="#590faf"/>
<rect x="685.33" y="109.43" width="5.15" height="15.16" fill="#878787"/>
<rect x="690.29" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="695.24" y="109.43" width="5.15" height="15.16" fill="#800fbc"/>
<rect x="700.19" y="109.43" width="5.15" height="15.16" fill="#878787"/>
<rect x="705.14" y="109.43" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="710.1" y="109.43" width="5.15" height="15.16" fill="#a60faf"/>
<rect x="715.05" y="109.43" width="5.15" height="15.16" fill="#878787"/>
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
<rect x="675.43" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341;0.5008;0.5674;0.6341;0.7008" values="none;#fff4f4;#fff4f4;#fff4f4;#fff4f4;#fff4f4"/></rect>
<rect x="690.29" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353;0.5020;0.5686;0.6353;0.7020" values="none;#fff8f9;#fff8f9;#f4f7f1;#f4f7f1;#f4f7f1"/></rect>
<rect x="705.14" y="109.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365;0.5032;0.5699;0.6365;0.7032" values="none;#fffefe;#fffefd;#fafdf9;#fafdf9;#fafdf9"/></rect>
<rect x="660.57" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341;0.5008;0.5674;0.6341;0.7008" values="none;#ffe1e3;#ffe1e3;#f3e0db;#f0dedb;#f0dedb"/></rect>
<rect x="675.43" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353;0.5020;0.5686;0.6353;0.7020" values="none;#ffe4e5;#ffe4e5;#cedfc4;#ccddc4;#ccddc4"/></rect>
<rect x="690.29" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365;0.5032;0.5699;0.6365;0.7032" values="none;#fff0f1;#fff0ef;#b7e8bc;#b6e7bc;#b6e7bc"/></rect>
<rect x="645.71" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341;0.5008;0.5674;0.6341;0.7008" values="none;#ffeaec;#ffeaec;#ffeaec;#f8e6ec;#f8e6ec"/></rect>
<rect x="660.57" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353;0.5020;0.5686;0.6353;0.7020" values="none;#ffdadd;#ffdadd;#d5d6c1;#c8cec1;#c8cec1"/></rect>
<rect x="675.43" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365;0.5032;0.5699;0.6365;0.7032" values="none;#ffe2e3;#ffe2e3;#a2d8a4;#99d1a4;#99d1a4"/></rect>
<rect x="645.71" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353;0.5020;0.5686;0.6353;0.7020" values="none;#ffeced;#ffeced;#ffeced;#ece1ed;#ece1ed"/></rect>
<rect x="660.57" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365;0.5032;0.5699;0.6365;0.7032" values="none;#ffe2e4;#ffe2e4;#c8dcbe;#b0cbbe;#b0cbbe"/></rect>
<rect x="675.43" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377;0.5044;0.5711;0.6377;0.7044" values="none;#ffe9ea;#ffe9ea;#8edc9b;#80ce9b;#80ce9b"/></rect>
<rect x="660.57" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377;0.5044;0.5711;0.6377;0.7044" values="none;#fff0f1;#fff0f1;#d3ebd1;#b2d4d1;#b2d4d1"/></rect>
<rect x="675.43" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389;0.5056;0.5723;0.6389;0.7056" values="none;#fff3f4;#fff3f4;#9de8ac;#87d4ac;#87d4ac"/></rect>
<rect x="660.57" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389;0.5056;0.5723;0.6389;0.7056" values="none;#fffcfc;#fffcfc;#f4fbf3;#d6e8f3;#d6e8f3"/></rect>
<rect x="675.43" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401;0.5068;0.5735;0.6401;0.7068" values="none;#fffcfc;#fffcfc;#caf6d4;#b0e2d4;#b0e2d4"/></rect>
<rect x="675.43" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413;0.5080;0.5747;0.6413;0.7080" values="none;#ffffff;#ffffff;#ffffff;#f6faff;#f6faff"/></rect>
<rect x="690.29" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425;0.5092;0.5759;0.6425;0.7092" values="none;#ffffff;#ffffff;#f7fef9;#f0f9f9;#f0f9f9"/></rect>
<circle cx="697.71" cy="159.94" r="49.03" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;1.0000" values="0;0;1;1"/></circle>
<circle cx="697.71" cy="159.94" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;1.0000" values="0;0;1;1"/></circle>
<text x="697.71" y="164.94" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">5<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;1.0000" values="0;0;1;1"/></text>
<circle cx="697.71" cy="159.94" r="49.03" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2256;0.2259;1.0000" values="0;0;1;1"/><rect x="705.14" y="124.29" width="5.15" height="15.16" fill="#ffffff"/>
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
<rect x="705.14" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377;0.5044;0.5711;0.6377;0.7044" values="none;#fffefe;#fffefe;#fefefd;#fefefd;#fefefd"/></rect>
<rect x="720.0" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389;0.5056;0.5723;0.6389;0.7056" values="none;#fffefe;#fffdfb;#e5fae8;#e5fae8;#e5fae8"/></rect>
<rect x="734.86" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401;0.5068;0.5735;0.6401;0.7068" values="none;#ffffff;#fffdf5;#e9fae5;#e9fae5;#e9fae5"/></rect>
<rect x="749.71" y="124.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413;0.5080;0.5747;0.6413;0.7080" values="none;#ffffff;#fffdf6;#fffdf6;#fffdf6;#fffdf6"/></rect>
<rect x="690.29" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377;0.5044;0.5711;0.6377;0.7044" values="none;#fffcfc;#fffcfc;#fcfbfa;#fcfbfa;#fcfbfa"/></rect>
<rect x="705.14" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389;0.5056;0.5723;0.6389;0.7056" values="none;#fff9f9;#fff9f9;#c0f2ca;#bff1ca;#bff1ca"/></rect>
<rect x="720.0" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401;0.5068;0.5735;0.6401;0.7068" values="none;#fffdfd;#fffbf6;#a3f0b2;#a3f0b2;#a3efb2"/></rect>
<rect x="734.86" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413;0.5080;0.5747;0.6413;0.7080" values="none;#ffffff;#fffbee;#abf1b2;#abf1b2;#abeeb2"/></rect>
<rect x="749.71" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425;0.5092;0.5759;0.6425;0.7092" values="none;#ffffff;#fff9e6;#d2f4c7;#d2f4c7;#d1eec7"/></rect>
<rect x="764.57" y="139.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438;0.5104;0.5771;0.6438;0.7104" values="none;#ffffff;#fffcf2;#fffcf2;#fffcf2;#fefaf2"/></rect>
<rect x="690.29" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389;0.5056;0.5723;0.6389;0.7056" values="none;#fff9f9;#fff9f9;#dcf5e0;#d7f1e0;#d7f1e0"/></rect>
<rect x="705.14" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401;0.5068;0.5735;0.6401;0.7068" values="none;#fff9fa;#fff9f9;#9aeead;#95e9ad;#95e9ad"/></rect>
<rect x="720.0" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413;0.5080;0.5747;0.6413;0.7080" values="none;#fffdfd;#fffcf8;#79ec94;#77ea94;#76e694"/></rect>
<rect x="734.86" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425;0.5092;0.5759;0.6425;0.7092" values="none;#ffffff;#fffcf0;#84ed97;#84ed97;#82e297"/></rect>
<rect x="749.71" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438;0.5104;0.5771;0.6438;0.7104" values="none;#ffffff;#fffae8;#b3f1b3;#b3f1b3;#b0e0b3"/></rect>
<rect x="764.57" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450;0.5116;0.5783;0.6450;0.7116" values="none;#ffffff;#fffbeb;#eff9e0;#eff9e0;#ecebe0"/></rect>
<rect x="690.29" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401;0.5068;0.5735;0.6401;0.7068" values="none;#fffcfc;#fffcfc;#dcf8e2;#d2f1e2;#d2f1e2"/></rect>
<rect x="705.14" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413;0.5080;0.5747;0.6413;0.7080" values="none;#fffcfc;#fffcfc;#99f0af;#92e9af;#91e8af"/></rect>
<rect x="720.0" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425;0.5092;0.5759;0.6425;0.7092" values="none;#fffefe;#fffefc;#78ee96;#75ea96;#74e296"/></rect>
<rect x="734.86" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438;0.5104;0.5771;0.6438;0.7104" values="none;#ffffff;#fffdf7;#83ef9b;#83ee9b;#80dc9b"/></rect>
<rect x="749.71" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450;0.5116;0.5783;0.6450;0.7116" values="none;#ffffff;#fffcf1;#b3f3ba;#b3f3ba;#add8ba"/></rect>
<rect x="764.57" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462;0.5128;0.5795;0.6462;0.7128" values="none;#ffffff;#fffcf4;#effbe8;#effbe8;#eae4e8"/></rect>
<rect x="690.29" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4413;0.5080;0.5747;0.6413;0.7080" values="none;#ffffff;#ffffff;#fcfffd;#f5fafd;#f5fafd"/></rect>
<rect x="705.14" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4425;0.5092;0.5759;0.6425;0.7092" values="none;#ffffff;#ffffff;#bff7ce;#b6efce;#b5eece"/></rect>
<rect x="720.0" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438;0.5104;0.5771;0.6438;0.7104" values="none;#ffffff;#ffffff;#a2f4b7;#9df0b7;#9ce6b7"/></rect>
<rect x="734.86" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450;0.5116;0.5783;0.6450;0.7116" values="none;#ffffff;#fffffd;#aaf5bd;#a9f3bd;#a5dfbd"/></rect>
<rect x="749.71" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462;0.5128;0.5795;0.6462;0.7128" values="none;#ffffff;#fffefb;#d1f9d9;#d1f9d9;#cbdcd9"/></rect>
<rect x="764.57" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474;0.5140;0.5807;0.6474;0.7140" values="none;#ffffff;#fffffe;#fffffe;#fffffe;#fbf0fe"/></rect>
<rect x="705.14" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4438;0.5104;0.5771;0.6438;0.7104" values="none;#ffffff;#ffffff;#fefffe;#fafcfe;#fafcfe"/></rect>
<rect x="720.0" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4450;0.5116;0.5783;0.6450;0.7116" values="none;#ffffff;#ffffff;#e4fceb;#e1faeb;#e0f5eb"/></rect>
<rect x="734.86" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462;0.5128;0.5795;0.6462;0.7128" values="none;#ffffff;#ffffff;#e8fcee;#e8fcee;#e5efee"/></rect>
<rect x="749.71" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4474;0.5140;0.5807;0.6474;0.7140" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#fcf4ff"/></rect>
<circle cx="734.86" cy="168.86" r="44.57" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2256;0.2259;1.0000" values="0;0;1;1"/></circle>
<circle cx="734.86" cy="168.86" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2256;0.2259;1.0000" values="0;0;1;1"/></circle>
<text x="734.86" y="173.86" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">6<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2256;0.2259;1.0000" values="0;0;1;1"/></text>
<circle cx="734.86" cy="168.86" r="44.57" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;1.0000" values="0;0;1;1"/><rect x="571.43" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="183.71" width="5.15" height="15.16" fill="#5115b4"/>
<rect x="581.33" y="183.71" width="5.15" height="15.16" fill="#646464"/>
<rect x="586.29" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="183.71" width="5.15" height="15.16" fill="#7b15c6"/>
<rect x="596.19" y="183.71" width="5.15" height="15.16" fill="#646464"/>
<rect x="601.14" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="183.71" width="5.15" height="15.16" fill="#a615bb"/>
<rect x="611.05" y="183.71" width="5.15" height="15.16" fill="#646464"/>
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
<rect x="571.43" y="258.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="576.38" y="258.0" width="5.15" height="15.16" fill="#51eab4"/>
<rect x="581.33" y="258.0" width="5.15" height="15.16" fill="#646464"/>
<rect x="586.29" y="258.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="591.24" y="258.0" width="5.15" height="15.16" fill="#7beac6"/>
<rect x="596.19" y="258.0" width="5.15" height="15.16" fill="#646464"/>
<rect x="601.14" y="258.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="258.0" width="5.15" height="15.16" fill="#a6eabb"/>
<rect x="611.05" y="258.0" width="5.15" height="15.16" fill="#646464"/>
</g>
<rect x="571.43" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4317;0.4984;0.5650;0.6317;0.6984" values="none;#ffe6e7;#ffe6e7;#fee6e7;#f8e3e7;#f8e3e7"/></rect>
<rect x="556.57" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4317;0.4984;0.5650;0.6317;0.6984" values="none;#ffedef;#ffedef;#ffedef;#eae1ef;#eae1ef"/></rect>
<rect x="571.43" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329;0.4996;0.5662;0.6329;0.6996" values="none;#ffdee0;#ffdee0;#f9dedc;#c0bddc;#c0bddc"/></rect>
<rect x="556.57" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329;0.4996;0.5662;0.6329;0.6996" values="none;#fff2f3;#fff2f3;#fff2f3;#c8d2f3;#c8d2f3"/></rect>
<rect x="571.43" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341;0.5008;0.5674;0.6341;0.7008" values="none;#ffe9eb;#ffe9eb;#f9e9e6;#95aee6;#95aee6"/></rect>
<rect x="556.57" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341;0.5008;0.5674;0.6341;0.7008" values="none;#fffbfb;#fffbfb;#fffbfb;#c0d4fb;#c0d4fb"/></rect>
<rect x="571.43" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353;0.5020;0.5686;0.6353;0.7020" values="none;#fff7f7;#fff7f7;#fcf6f5;#8ab1f5;#8ab1f5"/></rect>
<rect x="586.29" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365;0.5032;0.5699;0.6365;0.7032" values="none;#fff6f7;#fff6f7;#f2f5ed;#77a7ed;#77a7ed"/></rect>
<rect x="556.57" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353;0.5020;0.5686;0.6353;0.7020" values="none;#ffffff;#ffffff;#ffffff;#dbe9ff;#dbe9ff"/></rect>
<rect x="571.43" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365;0.5032;0.5699;0.6365;0.7032" values="none;#fffefe;#fffefe;#fffefe;#a8c8fe;#a8c8fe"/></rect>
<rect x="586.29" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377;0.5044;0.5711;0.6377;0.7044" values="none;#fffefe;#fffefe;#fafdfa;#97befa;#97befa"/></rect>
<rect x="601.14" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389;0.5056;0.5723;0.6389;0.7056" values="none;#ffffff;#ffffff;#f3fdf6;#a9cdf6;#a9cdf6"/></rect>
<rect x="616.0" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401;0.5068;0.5735;0.6401;0.7068" values="none;#ffffff;#ffffff;#f2fef5;#d6ebf5;#d6ebf5"/></rect>
<rect x="571.43" y="258.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377;0.5044;0.5711;0.6377;0.7044" values="none;#ffffff;#ffffff;#ffffff;#e7f0ff;#e7f0ff"/></rect>
<rect x="586.29" y="258.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389;0.5056;0.5723;0.6389;0.7056" values="none;#ffffff;#ffffff;#ffffff;#d8e7ff;#d8e7ff"/></rect>
<rect x="601.14" y="258.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401;0.5068;0.5735;0.6401;0.7068" values="none;#ffffff;#ffffff;#fefffe;#e8f1fe;#e8f1fe"/></rect>
<circle cx="595.2" cy="228.29" r="44.57" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;1.0000" values="0;0;1;1"/></circle>
<circle cx="595.2" cy="228.29" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;1.0000" values="0;0;1;1"/></circle>
<text x="595.2" y="233.29" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">7<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;1.0000" values="0;0;1;1"/></text>
<circle cx="595.2" cy="228.29" r="44.57" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2923;0.2926;1.0000" values="0;0;1;1"/><rect x="601.14" y="168.86" width="5.15" height="15.16" fill="#ffffff"/>
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
<rect x="601.14" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="606.1" y="228.29" width="5.15" height="15.16" fill="#4ddfc3"/>
<rect x="611.05" y="228.29" width="5.15" height="15.16" fill="#535353"/>
<rect x="616.0" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="620.95" y="228.29" width="5.15" height="15.16" fill="#7bdfd4"/>
<rect x="625.9" y="228.29" width="5.15" height="15.16" fill="#535353"/>
<rect x="630.86" y="228.29" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="635.81" y="228.29" width="5.15" height="15.16" fill="#a8dfc9"/>
<rect x="640.76" y="228.29" width="5.15" height="15.16" fill="#535353"/>
</g>
<rect x="601.14" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329;0.4996;0.5662;0.6329;0.6996" values="none;#ffd9db;#ffd9db;#f6d8d5;#e5ced5;#e5ced5"/></rect>
<rect x="616.0" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341;0.5008;0.5674;0.6341;0.7008" values="none;#ffdadc;#ffdadc;#e1d7c8;#d0cdc8;#d0cdc8"/></rect>
<rect x="630.86" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353;0.5020;0.5686;0.6353;0.7020" values="none;#ffeaeb;#ffeaeb;#d3e5cc;#cde1cc;#cde1cc"/></rect>
<rect x="645.71" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365;0.5032;0.5699;0.6365;0.7032" values="none;#fffcfd;#fffcfd;#e6f9e9;#e6f9e9;#e6f9e9"/></rect>
<rect x="586.29" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329;0.4996;0.5662;0.6329;0.6996" values="none;#ffe6e8;#ffe6e8;#ffe6e8;#ded4e8;#ded4e8"/></rect>
<rect x="601.14" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341;0.5008;0.5674;0.6341;0.7008" values="none;#ffd9db;#ffd9db;#edd7cf;#b4b7cf;#b4b7cf"/></rect>
<rect x="616.0" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353;0.5020;0.5686;0.6353;0.7020" values="none;#ffdddf;#ffdddf;#d1d8c0;#a1b9c0;#a1b9c0"/></rect>
<rect x="630.86" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365;0.5032;0.5699;0.6365;0.7032" values="none;#ffebec;#ffebec;#bbe4bc;#a1d0bc;#a1d0bc"/></rect>
<rect x="645.71" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377;0.5044;0.5711;0.6377;0.7044" values="none;#fffafa;#fffafa;#c1f2cb;#bbeecb;#bbeecb"/></rect>
<rect x="586.29" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4341;0.5008;0.5674;0.6341;0.7008" values="none;#fff0f1;#fff0f1;#fff0f1;#c5cef1;#c5cef1"/></rect>
<rect x="601.14" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353;0.5020;0.5686;0.6353;0.7020" values="none;#ffe8ea;#ffe8ea;#eee6de;#98b2de;#98b2de"/></rect>
<rect x="616.0" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365;0.5032;0.5699;0.6365;0.7032" values="none;#ffebed;#ffebed;#d4e7ce;#8ab5ce;#8ab5ce"/></rect>
<rect x="630.86" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377;0.5044;0.5711;0.6377;0.7044" values="none;#fff4f5;#fff4f5;#bfedc6;#93cbc6;#93cbc6"/></rect>
<rect x="645.71" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389;0.5056;0.5723;0.6389;0.7056" values="none;#fffdfd;#fffdfd;#c1f6ce;#b2eace;#b2eace"/></rect>
<rect x="586.29" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4353;0.5020;0.5686;0.6353;0.7020" values="none;#fffcfc;#fffcfc;#fffcfc;#cbdcfc;#cbdcfc"/></rect>
<rect x="601.14" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4365;0.5032;0.5699;0.6365;0.7032" values="none;#fff8f8;#fff8f8;#f7f7f2;#9dbff2;#9dbff2"/></rect>
<rect x="616.0" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377;0.5044;0.5711;0.6377;0.7044" values="none;#fff9f9;#fff9f9;#e4f6e5;#93bfe5;#93bfe5"/></rect>
<rect x="630.86" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389;0.5056;0.5723;0.6389;0.7056" values="none;#fffdfd;#fffdfd;#d5f8dd;#a4d4dd;#a4d4dd"/></rect>
<rect x="645.71" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401;0.5068;0.5735;0.6401;0.7068" values="none;#ffffff;#ffffff;#dafbe3;#ccf0e3;#ccf0e3"/></rect>
<rect x="601.14" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4377;0.5044;0.5711;0.6377;0.7044" values="none;#ffffff;#ffffff;#ffffff;#ccdfff;#ccdfff"/></rect>
<rect x="616.0" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4389;0.5056;0.5723;0.6389;0.7056" values="none;#ffffff;#ffffff;#f8fefa;#c2dbfa;#c2dbfa"/></rect>
<rect x="630.86" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4401;0.5068;0.5735;0.6401;0.7068" values="none;#ffffff;#ffffff;#f3fef6;#d6eaf6;#d6eaf6"/></rect>
<circle cx="624.91" cy="204.51" r="41.6" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2923;0.2926;1.0000" values="0;0;1;1"/></circle>
<circle cx="624.91" cy="204.51" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2923;0.2926;1.0000" values="0;0;1;1"/></circle>
<text x="624.91" y="209.51" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">8<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2923;0.2926;1.0000" values="0;0;1;1"/></text>
<circle cx="624.91" cy="204.51" r="41.6" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;1.0000" values="0;0;1;1"/><rect x="824.0" y="183.71" width="5.15" height="15.16" fill="#ffffff"/>
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
<rect x="868.57" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4558;0.5225;0.5891;0.6558;0.7225" values="none;#ffffff;#fff9e6;#fff9e5;#fff9e5;#fef6e5"/></rect>
<rect x="868.57" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4570;0.5237;0.5904;0.6570;0.7237" values="none;#ffffff;#fff8e0;#fdf8df;#fdf8df;#f0c9df"/></rect>
<rect x="883.43" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4582;0.5249;0.5916;0.6582;0.7249" values="none;#ffffff;#fffdf4;#fffdf4;#fffdf4;#fdf6f4"/></rect>
<rect x="853.71" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4570;0.5237;0.5904;0.6570;0.7237" values="none;#ffffff;#fff9e6;#f4f8df;#f4f8df;#d788df"/></rect>
<rect x="868.57" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4582;0.5249;0.5916;0.6582;0.7249" values="none;#ffffff;#fffbeb;#fdfaea;#fdfaea;#e7a6ea"/></rect>
<rect x="883.43" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4594;0.5261;0.5928;0.6594;0.7261" values="none;#ffffff;#fffdf7;#fffdf7;#fffdf7;#f6ddf7"/></rect>
<rect x="853.71" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4582;0.5249;0.5916;0.6582;0.7249" values="none;#ffffff;#fffdf5;#f8fcf0;#f8fcf0;#d77cf0"/></rect>
<rect x="868.57" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4594;0.5261;0.5928;0.6594;0.7261" values="none;#ffffff;#fffdf8;#fefdf7;#fefdf7;#e59ef7"/></rect>
<rect x="883.43" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4606;0.5273;0.5940;0.6606;0.7273" values="none;#ffffff;#fffffd;#fffffd;#fffffd;#f5d9fd"/></rect>
<rect x="809.14" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4558;0.5225;0.5891;0.6558;0.7225" values="none;#ffffff;#ffffff;#f6fef8;#f6fef8;#f3f3f8"/></rect>
<rect x="824.0" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4570;0.5237;0.5904;0.6570;0.7237" values="none;#ffffff;#ffffff;#f2fdf5;#f2fdf5;#e2bff5"/></rect>
<rect x="838.86" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4582;0.5249;0.5916;0.6582;0.7249" values="none;#ffffff;#fffffe;#f7fef8;#f7fef8;#dd9af8"/></rect>
<rect x="853.71" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4594;0.5261;0.5928;0.6594;0.7261" values="none;#ffffff;#fffffe;#fdfefc;#fdfefc;#e197fc"/></rect>
<rect x="868.57" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4606;0.5273;0.5940;0.6606;0.7273" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#ecb7ff"/></rect>
<rect x="883.43" y="243.14" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4618;0.5285;0.5952;0.6618;0.7285" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#faeeff"/></rect>
<rect x="824.0" y="258.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4582;0.5249;0.5916;0.6582;0.7249" values="none;#ffffff;#ffffff;#fefffe;#fefffe;#f9effe"/></rect>
<rect x="838.86" y="258.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4594;0.5261;0.5928;0.6594;0.7261" values="none;#ffffff;#ffffff;#fefffe;#fefffe;#f2d3fe"/></rect>
<rect x="853.71" y="258.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4606;0.5273;0.5940;0.6606;0.7273" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#f3d1ff"/></rect>
<rect x="868.57" y="258.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4618;0.5285;0.5952;0.6618;0.7285" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#faebff"/></rect>
<circle cx="853.71" cy="228.29" r="47.54" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;1.0000" values="0;0;1;1"/></circle>
<circle cx="853.71" cy="228.29" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;1.0000" values="0;0;1;1"/></circle>
<text x="853.71" y="233.29" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">9<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;1.0000" values="0;0;1;1"/></text>
<circle cx="853.71" cy="228.29" r="47.54" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<g clip-path="url(#fd-clip-d)"><g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;1.0000" values="0;0;1;1"/><rect x="809.14" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="814.1" y="154.0" width="5.15" height="15.16" fill="#690598"/>
<rect x="819.05" y="154.0" width="5.15" height="15.16" fill="#303030"/>
<rect x="824.0" y="154.0" width="5.15" height="15.16" fill="#ffffff"/>
<rect x="828.95" y="154.0" width="5.15" height="15.16" fill="#960598"/>
<rect x="833.9" y="154.0" width="5.15" height="15.16" fill="#303030"/>
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
<rect x="809.14" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486;0.5152;0.5819;0.6486;0.7152" values="none;#ffffff;#fffcf1;#fafbed;#fafbed;#fafbed"/></rect>
<rect x="824.0" y="154.0" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498;0.5165;0.5831;0.6498;0.7165" values="none;#ffffff;#fffbeb;#fffbeb;#fffbeb;#fffbeb"/></rect>
<rect x="794.29" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486;0.5152;0.5819;0.6486;0.7152" values="none;#ffffff;#fffbee;#d4f6d0;#d4f6d0;#d3f4d0"/></rect>
<rect x="809.14" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498;0.5165;0.5831;0.6498;0.7165" values="none;#ffffff;#fff6d8;#d8f2be;#d8f2be;#d3e0be"/></rect>
<rect x="824.0" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510;0.5177;0.5843;0.6510;0.7177" values="none;#ffffff;#fff4cc;#ebf1c0;#ebf1c0;#e5d8c0"/></rect>
<rect x="838.86" y="168.86" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522;0.5189;0.5855;0.6522;0.7189" values="none;#ffffff;#fff6d7;#fdf6d5;#fdf6d5;#f8e6d5"/></rect>
<rect x="779.43" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4486;0.5152;0.5819;0.6486;0.7152" values="none;#ffffff;#ffffff;#dbfbe3;#dbfbe3;#dbfbe3"/></rect>
<rect x="794.29" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498;0.5165;0.5831;0.6498;0.7165" values="none;#ffffff;#fffcf0;#bff4c2;#bff4c2;#baddc2"/></rect>
<rect x="809.14" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510;0.5177;0.5843;0.6510;0.7177" values="none;#ffffff;#fff8df;#caf2bb;#caf2bb;#bfc0bb"/></rect>
<rect x="824.0" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522;0.5189;0.5855;0.6522;0.7189" values="none;#ffffff;#fff6d5;#e3f2c2;#e3f2c2;#d3b3c2"/></rect>
<rect x="838.86" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4534;0.5201;0.5867;0.6534;0.7201" values="none;#ffffff;#fff7da;#f8f6d5;#f8f6d5;#eac2d5"/></rect>
<rect x="853.71" y="183.71" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4546;0.5213;0.5879;0.6546;0.7213" values="none;#ffffff;#fffcf2;#fffcf2;#fffcf2;#fbeff2"/></rect>
<rect x="779.43" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4498;0.5165;0.5831;0.6498;0.7165" values="none;#ffffff;#ffffff;#dbfbe4;#dbfbe4;#dbfae4"/></rect>
<rect x="794.29" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4510;0.5177;0.5843;0.6510;0.7177" values="none;#ffffff;#fffef9;#c4f7cd;#c4f7cd;#bcd1cd"/></rect>
<rect x="809.14" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522;0.5189;0.5855;0.6522;0.7189" values="none;#ffffff;#fffbef;#cff6cd;#cff6cd;#bfadcd"/></rect>
<rect x="824.0" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4534;0.5201;0.5867;0.6534;0.7201" values="none;#ffffff;#fffae8;#e6f7d7;#e6f7d7;#d09cd7"/></rect>
<rect x="838.86" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4546;0.5213;0.5879;0.6546;0.7213" values="none;#ffffff;#fffbeb;#fafae7;#fafae7;#e5ade7"/></rect>
<rect x="853.71" y="198.57" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4558;0.5225;0.5891;0.6558;0.7225" values="none;#ffffff;#fffef9;#fffef9;#fffef9;#f8e2f9"/></rect>
<rect x="794.29" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4522;0.5189;0.5855;0.6522;0.7189" values="none;#ffffff;#ffffff;#ddfbe5;#ddfbe5;#d5d9e5"/></rect>
<rect x="809.14" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4534;0.5201;0.5867;0.6534;0.7201" values="none;#ffffff;#fffefc;#e3fbe6;#e3fbe6;#d1b3e6"/></rect>
<rect x="824.0" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4546;0.5213;0.5879;0.6546;0.7213" values="none;#ffffff;#fffef9;#f2fcef;#f2fcef;#dba3ef"/></rect>
<rect x="838.86" y="213.43" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4558;0.5225;0.5891;0.6558;0.7225" values="none;#ffffff;#fffefb;#fefefa;#fefefa;#ebb7fa"/></rect>
<rect x="794.29" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4534;0.5201;0.5867;0.6534;0.7201" values="none;#ffffff;#ffffff;#fdfffd;#fdfffd;#fcfcfd"/></rect>
<rect x="809.14" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4546;0.5213;0.5879;0.6546;0.7213" values="none;#ffffff;#ffffff;#f9fefb;#f9fefb;#f0dbfb"/></rect>
<rect x="824.0" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4558;0.5225;0.5891;0.6558;0.7225" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#f2d1ff"/></rect>
<rect x="838.86" y="228.29" width="15.16" height="15.16" fill="none"><animate attributeName="fill" dur="13.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4570;0.5237;0.5904;0.6570;0.7237" values="none;#ffffff;#ffffff;#ffffff;#ffffff;#fbefff"/></rect>
<circle cx="824.0" cy="201.54" r="41.6" fill="none" stroke="#1e293b" stroke-width="2" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;1.0000" values="0;0;1;1"/></circle>
<circle cx="824.0" cy="201.54" r="11" fill="#ffffff" stroke="#334155" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;1.0000" values="0;0;1;1"/></circle>
<text x="824.0" y="206.54" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">10<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;1.0000" values="0;0;1;1"/></text>
<circle cx="824.0" cy="201.54" r="41.6" fill="url(#fd-sphere)" opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7441;0.7444;1.0000" values="0;0;1;1"/></circle>
</g>
<line x1="84.0" y1="89.0" x2="84.0" y2="89.0" stroke="#ff3340" stroke-width="3" stroke-dasharray="6 4" opacity="0"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0382;0.0385;0.1049;0.1052;0.1716;0.1719;0.2382;0.2385;0.3049;0.3052;0.3716;0.3719;0.4382;0.4385;0.5049;0.5052;0.5716;0.5719;0.6382;0.6385;1.0000" values="84;84;106.29;106.29;136;136;358.86;358.86;388.57;388.57;217.71;217.71;254.86;254.86;115.2;115.2;144.91;144.91;373.71;373.71;344;344"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0382;0.0385;0.1049;0.1052;0.1716;0.1719;0.2382;0.2385;0.3049;0.3052;0.3716;0.3719;0.4382;0.4385;0.5049;0.5052;0.5716;0.5719;0.6382;0.6385;1.0000" values="89;89;106.46;106.46;121.31;121.31;103.49;103.49;118.34;118.34;159.94;159.94;168.86;168.86;228.29;228.29;204.51;204.51;228.29;228.29;201.54;201.54"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0382;0.0385;0.0464;0.0467;0.1049;0.1052;0.1130;0.1133;0.1716;0.1719;0.1797;0.1800;0.2382;0.2385;0.2464;0.2467;0.3049;0.3052;0.3130;0.3133;0.3716;0.3719;0.3797;0.3800;0.4382;0.4385;0.4464;0.4467;0.5049;0.5052;0.5130;0.5133;0.5716;0.5719;0.5797;0.5800;0.6382;0.6385;0.6464;0.6467;1.0000" values="0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0"/></line>
<line x1="390.8" y1="83.8" x2="390.8" y2="83.8" stroke="#ffcc1a" stroke-width="3" stroke-dasharray="6 4" opacity="0"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0489;0.1153;0.1156;0.1819;0.1822;0.2486;0.2489;0.3153;0.3156;0.3819;0.3822;0.4486;0.4489;0.5153;0.5156;0.5819;0.5822;0.6486;0.6489;1.0000" values="390.8;390.8;106.29;106.29;136;136;358.86;358.86;388.57;388.57;217.71;217.71;254.86;254.86;115.2;115.2;144.91;144.91;373.71;373.71;344;344"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0489;0.1153;0.1156;0.1819;0.1822;0.2486;0.2489;0.3153;0.3156;0.3819;0.3822;0.4486;0.4489;0.5153;0.5156;0.5819;0.5822;0.6486;0.6489;1.0000" values="83.8;83.8;106.46;106.46;121.31;121.31;103.49;103.49;118.34;118.34;159.94;159.94;168.86;168.86;228.29;228.29;204.51;204.51;228.29;228.29;201.54;201.54"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0489;0.0567;0.0570;0.1153;0.1156;0.1234;0.1237;0.1819;0.1822;0.1901;0.1904;0.2486;0.2489;0.2567;0.2570;0.3153;0.3156;0.3234;0.3237;0.3819;0.3822;0.3901;0.3904;0.4486;0.4489;0.4567;0.4570;0.5153;0.5156;0.5234;0.5237;0.5819;0.5822;0.5901;0.5904;0.6486;0.6489;0.6567;0.6570;1.0000" values="0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0"/></line>
<line x1="240.0" y1="169.6" x2="240.0" y2="169.6" stroke="#26e659" stroke-width="3" stroke-dasharray="6 4" opacity="0"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.1256;0.1259;0.1923;0.1926;0.2590;0.2593;0.3256;0.3259;0.3923;0.3926;0.4590;0.4593;0.5256;0.5259;0.5923;0.5926;0.6590;0.6593;1.0000" values="240;240;106.29;106.29;136;136;358.86;358.86;388.57;388.57;217.71;217.71;254.86;254.86;115.2;115.2;144.91;144.91;373.71;373.71;344;344"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.1256;0.1259;0.1923;0.1926;0.2590;0.2593;0.3256;0.3259;0.3923;0.3926;0.4590;0.4593;0.5256;0.5259;0.5923;0.5926;0.6590;0.6593;1.0000" values="169.6;169.6;106.46;106.46;121.31;121.31;103.49;103.49;118.34;118.34;159.94;159.94;168.86;168.86;228.29;228.29;204.51;204.51;228.29;228.29;201.54;201.54"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0671;0.0674;0.1256;0.1259;0.1338;0.1341;0.1923;0.1926;0.2004;0.2007;0.2590;0.2593;0.2671;0.2674;0.3256;0.3259;0.3338;0.3341;0.3923;0.3926;0.4004;0.4007;0.4590;0.4593;0.4671;0.4674;0.5256;0.5259;0.5338;0.5341;0.5923;0.5926;0.6004;0.6007;0.6590;0.6593;0.6671;0.6674;1.0000" values="0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0"/></line>
<line x1="99.6" y1="247.6" x2="99.6" y2="247.6" stroke="#3380ff" stroke-width="3" stroke-dasharray="6 4" opacity="0"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0693;0.0696;0.1360;0.1363;0.2027;0.2030;0.2693;0.2696;0.3360;0.3363;0.4027;0.4030;0.4693;0.4696;0.5360;0.5363;0.6027;0.6030;0.6693;0.6696;1.0000" values="99.6;99.6;106.29;106.29;136;136;358.86;358.86;388.57;388.57;217.71;217.71;254.86;254.86;115.2;115.2;144.91;144.91;373.71;373.71;344;344"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0693;0.0696;0.1360;0.1363;0.2027;0.2030;0.2693;0.2696;0.3360;0.3363;0.4027;0.4030;0.4693;0.4696;0.5360;0.5363;0.6027;0.6030;0.6693;0.6696;1.0000" values="247.6;247.6;106.46;106.46;121.31;121.31;103.49;103.49;118.34;118.34;159.94;159.94;168.86;168.86;228.29;228.29;204.51;204.51;228.29;228.29;201.54;201.54"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0693;0.0696;0.0775;0.0778;0.1360;0.1363;0.1441;0.1444;0.2027;0.2030;0.2108;0.2111;0.2693;0.2696;0.2775;0.2778;0.3360;0.3363;0.3441;0.3444;0.4027;0.4030;0.4108;0.4111;0.4693;0.4696;0.4775;0.4778;0.5360;0.5363;0.5441;0.5444;0.6027;0.6030;0.6108;0.6111;0.6693;0.6696;0.6775;0.6778;1.0000" values="0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0"/></line>
<line x1="380.4" y1="247.6" x2="380.4" y2="247.6" stroke="#cc40ff" stroke-width="3" stroke-dasharray="6 4" opacity="0"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1464;0.1467;0.2130;0.2133;0.2797;0.2800;0.3464;0.3467;0.4130;0.4133;0.4797;0.4800;0.5464;0.5467;0.6130;0.6133;0.6797;0.6800;1.0000" values="380.4;380.4;106.29;106.29;136;136;358.86;358.86;388.57;388.57;217.71;217.71;254.86;254.86;115.2;115.2;144.91;144.91;373.71;373.71;344;344"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1464;0.1467;0.2130;0.2133;0.2797;0.2800;0.3464;0.3467;0.4130;0.4133;0.4797;0.4800;0.5464;0.5467;0.6130;0.6133;0.6797;0.6800;1.0000" values="247.6;247.6;106.46;106.46;121.31;121.31;103.49;103.49;118.34;118.34;159.94;159.94;168.86;168.86;228.29;228.29;204.51;204.51;228.29;228.29;201.54;201.54"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.0879;0.0881;0.1464;0.1467;0.1545;0.1548;0.2130;0.2133;0.2212;0.2215;0.2797;0.2800;0.2879;0.2881;0.3464;0.3467;0.3545;0.3548;0.4130;0.4133;0.4212;0.4215;0.4797;0.4800;0.4879;0.4881;0.5464;0.5467;0.5545;0.5548;0.6130;0.6133;0.6212;0.6215;0.6797;0.6800;0.6879;0.6881;1.0000" values="0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0;0.95;0.95;0;0"/></line>
<text x="32" y="324" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ライト</text>
<circle cx="106" cy="318" r="11" fill="#ff3340" stroke="#1f2937" stroke-width="1.5" opacity="0.22"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0382;0.0385;0.0464;0.0467;0.1049;0.1052;0.1130;0.1133;0.1716;0.1719;0.1797;0.1800;0.2382;0.2385;0.2464;0.2467;0.3049;0.3052;0.3130;0.3133;0.3716;0.3719;0.3797;0.3800;0.4382;0.4385;0.4464;0.4467;0.5049;0.5052;0.5130;0.5133;0.5716;0.5719;0.5797;0.5800;0.6382;0.6385;0.6464;0.6467;1.0000" values="0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22"/></circle>
<circle cx="142" cy="318" r="11" fill="#ffcc1a" stroke="#1f2937" stroke-width="1.5" opacity="0.22"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0489;0.0567;0.0570;0.1153;0.1156;0.1234;0.1237;0.1819;0.1822;0.1901;0.1904;0.2486;0.2489;0.2567;0.2570;0.3153;0.3156;0.3234;0.3237;0.3819;0.3822;0.3901;0.3904;0.4486;0.4489;0.4567;0.4570;0.5153;0.5156;0.5234;0.5237;0.5819;0.5822;0.5901;0.5904;0.6486;0.6489;0.6567;0.6570;1.0000" values="0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22"/></circle>
<circle cx="178" cy="318" r="11" fill="#26e659" stroke="#1f2937" stroke-width="1.5" opacity="0.22"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0671;0.0674;0.1256;0.1259;0.1338;0.1341;0.1923;0.1926;0.2004;0.2007;0.2590;0.2593;0.2671;0.2674;0.3256;0.3259;0.3338;0.3341;0.3923;0.3926;0.4004;0.4007;0.4590;0.4593;0.4671;0.4674;0.5256;0.5259;0.5338;0.5341;0.5923;0.5926;0.6004;0.6007;0.6590;0.6593;0.6671;0.6674;1.0000" values="0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22"/></circle>
<circle cx="214" cy="318" r="11" fill="#3380ff" stroke="#1f2937" stroke-width="1.5" opacity="0.22"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0693;0.0696;0.0775;0.0778;0.1360;0.1363;0.1441;0.1444;0.2027;0.2030;0.2108;0.2111;0.2693;0.2696;0.2775;0.2778;0.3360;0.3363;0.3441;0.3444;0.4027;0.4030;0.4108;0.4111;0.4693;0.4696;0.4775;0.4778;0.5360;0.5363;0.5441;0.5444;0.6027;0.6030;0.6108;0.6111;0.6693;0.6696;0.6775;0.6778;1.0000" values="0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22"/></circle>
<circle cx="250" cy="318" r="11" fill="#cc40ff" stroke="#1f2937" stroke-width="1.5" opacity="0.22"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.0879;0.0881;0.1464;0.1467;0.1545;0.1548;0.2130;0.2133;0.2212;0.2215;0.2797;0.2800;0.2879;0.2881;0.3464;0.3467;0.3545;0.3548;0.4130;0.4133;0.4212;0.4215;0.4797;0.4800;0.4879;0.4881;0.5464;0.5467;0.5545;0.5548;0.6130;0.6133;0.6212;0.6215;0.6797;0.6800;0.6879;0.6881;1.0000" values="0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22;1;1;0.22;0.22"/></circle>
<text x="512" y="324" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ライト</text>
<circle cx="586" cy="318" r="11" fill="#ff3340" stroke="#1f2937" stroke-width="1.5" opacity="0.22"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4145;0.4148;0.4812;0.4815;1.0000" values="0.22;0.22;1;1;0.22;0.22"/></circle>
<circle cx="622" cy="318" r="11" fill="#ffcc1a" stroke="#1f2937" stroke-width="1.5" opacity="0.22"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;0.5479;0.5481;1.0000" values="0.22;0.22;1;1;0.22;0.22"/></circle>
<circle cx="658" cy="318" r="11" fill="#26e659" stroke="#1f2937" stroke-width="1.5" opacity="0.22"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;0.6145;0.6148;1.0000" values="0.22;0.22;1;1;0.22;0.22"/></circle>
<circle cx="694" cy="318" r="11" fill="#3380ff" stroke="#1f2937" stroke-width="1.5" opacity="0.22"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6145;0.6148;0.6812;0.6815;1.0000" values="0.22;0.22;1;1;0.22;0.22"/></circle>
<circle cx="730" cy="318" r="11" fill="#cc40ff" stroke="#1f2937" stroke-width="1.5" opacity="0.22"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6812;0.6815;0.7479;0.7481;1.0000" values="0.22;0.22;1;1;0.22;0.22"/></circle>
<text x="32" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① 物体 1/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0293;0.0296;0.0960;0.0963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② 物体 2/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;0.1627;0.1630;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">③ 物体 3/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1627;0.1630;0.2293;0.2296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">④ 物体 4/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2293;0.2296;0.2960;0.2963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">⑤ 物体 5/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2960;0.2963;0.3627;0.3630;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">⑥ 物体 6/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3627;0.3630;0.4293;0.4296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">⑦ 物体 7/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4293;0.4296;0.4960;0.4963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">⑧ 物体 8/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;0.5627;0.5630;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">⑨ 物体 9/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5627;0.5630;0.6293;0.6296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">⑩ 物体 10/10:その形のピクセルすべてにライト 5 つ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;0.7182;0.7185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="436" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d" opacity="0">赤枠 = 前の物体を上書き(前の計算が無駄に)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0293;0.0296;0.7182;0.7185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="32" y="358" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937">ピクセル計算:</text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="1">0<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0382;0.0385;1.0000" values="1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">32<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0382;0.0385;0.0486;0.0489;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">64<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0486;0.0489;0.0590;0.0593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">96<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0693;0.0696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">128<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0693;0.0696;0.0797;0.0800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">160<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1049;0.1052;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">188<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1049;0.1052;0.1153;0.1156;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">216<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1153;0.1156;0.1256;0.1259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">244<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1256;0.1259;0.1360;0.1363;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">272<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1360;0.1363;0.1464;0.1467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">300<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1464;0.1467;0.1716;0.1719;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">332<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1716;0.1719;0.1819;0.1822;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">364<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1819;0.1822;0.1923;0.1926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">396<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;0.2027;0.2030;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">428<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2027;0.2030;0.2130;0.2133;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">460<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2130;0.2133;0.2382;0.2385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">486<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2382;0.2385;0.2486;0.2489;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">512<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2486;0.2489;0.2590;0.2593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">538<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;0.2693;0.2696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">564<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2693;0.2696;0.2797;0.2800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">590<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2797;0.2800;0.3049;0.3052;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">627<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3049;0.3052;0.3153;0.3156;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">664<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3153;0.3156;0.3256;0.3259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">701<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;0.3360;0.3363;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">738<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3360;0.3363;0.3464;0.3467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">775<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3464;0.3467;0.3716;0.3719;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">807<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3716;0.3719;0.3819;0.3822;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">839<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3819;0.3822;0.3923;0.3926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">871<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3923;0.3926;0.4027;0.4030;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">903<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4027;0.4030;0.4130;0.4133;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">935<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4130;0.4133;0.4382;0.4385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">963<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4382;0.4385;0.4486;0.4489;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">991<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4486;0.4489;0.4590;0.4593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,019<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4590;0.4593;0.4693;0.4696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,047<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4693;0.4696;0.4797;0.4800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,075<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4797;0.4800;0.5049;0.5052;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,097<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5049;0.5052;0.5153;0.5156;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,119<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5153;0.5156;0.5256;0.5259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,141<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5256;0.5259;0.5360;0.5363;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,163<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5360;0.5363;0.5464;0.5467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,185<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5464;0.5467;0.5716;0.5719;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,217<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5716;0.5719;0.5819;0.5822;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,249<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5819;0.5822;0.5923;0.5926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,281<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5923;0.5926;0.6027;0.6030;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,313<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6027;0.6030;0.6130;0.6133;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,345<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6130;0.6133;0.6382;0.6385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,371<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6382;0.6385;0.6486;0.6489;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,397<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6486;0.6489;0.6590;0.6593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,423<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6590;0.6593;0.6693;0.6696;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,449<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6693;0.6696;0.6797;0.6800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="162" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,475<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6797;0.6800;1.0000" values="0;0;1;1"/></text>
<text x="32" y="388" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">うち、あとで上書きされて無駄:</text>
<text x="264" y="388" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;1.0000" values="1;1;0;0"/></text>
<text x="264" y="388" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">85<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0960;0.0963;0.2293;0.2296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="264" y="388" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">165<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2293;0.2296;0.3627;0.3630;1.0000" values="0;0;1;1;0;0"/></text>
<text x="264" y="388" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">255<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3627;0.3630;0.4960;0.4963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="264" y="388" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">320<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4960;0.4963;0.6293;0.6296;1.0000" values="0;0;1;1;0;0"/></text>
<text x="264" y="388" text-anchor="start" style="font-size:18px;font-weight:700;fill:#e5484d" opacity="0">385<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6293;0.6296;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7182;0.7185;1.0000" values="0;0;1;1"/><rect x="32" y="398" width="416" height="128" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="48" y="428" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1e3a8a">物体10 × ライト5 = 50回の描画</text>
<text x="48" y="458" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1e3a8a">ピクセル計算 295 マス × ライト5 = 1,475回</text>
<text x="48" y="490" text-anchor="start" style="font-size:19px;font-weight:700;fill:#e5484d">隠れて見えない部分も計算:無駄 約26%</text>
<text x="48" y="514" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">(重なったマスの計算は、あとで上書きされて捨てられる)</text>
</g>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(1/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0923;0.0926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(2/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0923;0.0926;0.1256;0.1259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(3/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1256;0.1259;0.1590;0.1593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(4/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1590;0.1593;0.1923;0.1926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(5/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1923;0.1926;0.2256;0.2259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(6/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2256;0.2259;0.2590;0.2593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(7/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2590;0.2593;0.2923;0.2926;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(8/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2923;0.2926;0.3256;0.3259;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(9/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3256;0.3259;0.3590;0.3593;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">① Pass 1:物体を G-Buffer に書く(10/10)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3590;0.3593;0.4145;0.4148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② Pass 2:絵のあるピクセルにライトを1つずつ(1/5)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4145;0.4148;0.4812;0.4815;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② Pass 2:絵のあるピクセルにライトを1つずつ(2/5)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;0.5479;0.5481;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② Pass 2:絵のあるピクセルにライトを1つずつ(3/5)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;0.6145;0.6148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② Pass 2:絵のあるピクセルにライトを1つずつ(4/5)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6145;0.6148;0.6812;0.6815;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="412" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">② Pass 2:絵のあるピクセルにライトを1つずつ(5/5)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6812;0.6815;0.7701;0.7704;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="436" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed" opacity="0">1マスに 色 | 法線 | 深度 の3種類を保存<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.4145;0.4148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="436" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed" opacity="0">物体の数に関係なく、画面を1回なぞる × 5 ライト<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4145;0.4148;0.7701;0.7704;1.0000" values="0;0;1;1;0;0"/></text>
<line x1="512" y1="50" x2="512" y2="287.71" stroke="#ff3340" stroke-width="5" opacity="0" clip-path="url(#fd-clip-d)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4145;0.4148;0.4671;0.4674;1.0000" values="0;0;0.9;0.9;0;0"/><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4148;0.4667;1.0000" values="512;512;1165.71;1165.71"/><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4145;0.4148;0.4667;1.0000" values="512;512;274.29;928;928"/></line>
<line x1="512" y1="50" x2="512" y2="287.71" stroke="#ffcc1a" stroke-width="5" opacity="0" clip-path="url(#fd-clip-d)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;0.5338;0.5341;1.0000" values="0;0;0.9;0.9;0;0"/><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4815;0.5333;1.0000" values="512;512;1165.71;1165.71"/><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4812;0.4815;0.5333;1.0000" values="512;512;274.29;928;928"/></line>
<line x1="512" y1="50" x2="512" y2="287.71" stroke="#26e659" stroke-width="5" opacity="0" clip-path="url(#fd-clip-d)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;0.6004;0.6007;1.0000" values="0;0;0.9;0.9;0;0"/><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5481;0.6000;1.0000" values="512;512;1165.71;1165.71"/><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;0.6000;1.0000" values="512;512;274.29;928;928"/></line>
<line x1="512" y1="50" x2="512" y2="287.71" stroke="#3380ff" stroke-width="5" opacity="0" clip-path="url(#fd-clip-d)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6145;0.6148;0.6671;0.6674;1.0000" values="0;0;0.9;0.9;0;0"/><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6148;0.6667;1.0000" values="512;512;1165.71;1165.71"/><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6145;0.6148;0.6667;1.0000" values="512;512;274.29;928;928"/></line>
<line x1="512" y1="50" x2="512" y2="287.71" stroke="#cc40ff" stroke-width="5" opacity="0" clip-path="url(#fd-clip-d)"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6812;0.6815;0.7338;0.7341;1.0000" values="0;0;0.9;0.9;0;0"/><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6815;0.7333;1.0000" values="512;512;1165.71;1165.71"/><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6812;0.6815;0.7333;1.0000" values="512;512;274.29;928;928"/></line>
<text x="512" y="358" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937">ピクセル計算:</text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="1">0<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4178;0.4181;1.0000" values="1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">5<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4178;0.4181;0.4242;0.4245;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">28<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4242;0.4245;0.4307;0.4310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">67<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4307;0.4310;0.4372;0.4375;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">115<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4372;0.4375;0.4437;0.4440;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">155<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4437;0.4440;0.4502;0.4505;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">195<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4502;0.4505;0.4566;0.4569;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">216<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4566;0.4569;0.4631;0.4634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">218<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4631;0.4634;0.4844;0.4847;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">223<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4844;0.4847;0.4909;0.4912;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">246<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4909;0.4912;0.4974;0.4977;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">285<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4974;0.4977;0.5039;0.5042;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">333<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5039;0.5042;0.5104;0.5106;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">373<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5104;0.5106;0.5168;0.5171;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">413<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5168;0.5171;0.5233;0.5236;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">434<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5233;0.5236;0.5298;0.5301;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">436<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5298;0.5301;0.5511;0.5514;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">441<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5511;0.5514;0.5576;0.5579;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">464<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5576;0.5579;0.5641;0.5644;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">503<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5641;0.5644;0.5705;0.5708;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">551<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5705;0.5708;0.5770;0.5773;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">591<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5770;0.5773;0.5835;0.5838;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">631<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5835;0.5838;0.5900;0.5903;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">652<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5900;0.5903;0.5965;0.5968;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">654<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5965;0.5968;0.6178;0.6181;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">659<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6178;0.6181;0.6242;0.6245;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">682<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6242;0.6245;0.6307;0.6310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">721<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6307;0.6310;0.6372;0.6375;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">769<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6372;0.6375;0.6437;0.6440;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">809<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6437;0.6440;0.6502;0.6505;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">849<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6502;0.6505;0.6566;0.6569;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">870<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6566;0.6569;0.6631;0.6634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">872<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6631;0.6634;0.6844;0.6847;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">877<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6844;0.6847;0.6909;0.6912;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">900<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6909;0.6912;0.6974;0.6977;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">939<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6974;0.6977;0.7039;0.7042;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">987<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7039;0.7042;0.7104;0.7106;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,027<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7104;0.7106;0.7168;0.7171;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,067<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7168;0.7171;0.7233;0.7236;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,088<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7233;0.7236;0.7298;0.7301;1.0000" values="0;0;1;1;0;0"/></text>
<text x="642" y="360" text-anchor="start" style="font-size:26px;font-weight:700;fill:#1f2937" opacity="0">1,090<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7298;0.7301;1.0000" values="0;0;1;1"/></text>
<text x="512" y="388" text-anchor="start" style="font-size:15px;font-weight:500;fill:#64748b" opacity="0">いまは材質を貯めているだけ(光の計算はまだ 0)<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.4145;0.4148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="512" y="388" text-anchor="start" style="font-size:15px;font-weight:500;fill:#64748b" opacity="0">光の計算は画面のマス数(448)が上限<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4145;0.4148;0.7701;0.7704;1.0000" values="0;0;1;1;0;0"/></text>
<g opacity="0"><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7701;0.7704;1.0000" values="0;0;1;1"/><rect x="512" y="398" width="416" height="128" rx="12" fill="#f5f3ff" stroke="#7c3aed" stroke-width="2.5"/>
<text x="528" y="428" text-anchor="start" style="font-size:19px;font-weight:700;fill:#4c1d95">③ ライティングは画面ピクセルごとに1回</text>
<text x="528" y="458" text-anchor="start" style="font-size:17px;font-weight:700;fill:#4c1d95">218 px × ライト5 = 1,090回</text>
<text x="528" y="490" text-anchor="start" style="font-size:16px;font-weight:700;fill:#4c1d95">物体が10個でも100個でも、最大 448 px × 5 まで</text>
<text x="528" y="514" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">(代わりに G-Buffer の書き込みと読み込みが増える)</text>
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
| **Forward（左）** | **球体を 1 つずつ描き、そのたびにライト 5 つを全部計算**。**赤枠は前の球体を上書きしたマス（前の計算が無駄になる）** |
| **Deferred（右）** | **① 球体の「色・法線・深度」を G-Buffer に貯める　② 画面全体をライト 1 つずつ、斜めになぞる** |
| **カウンター** | **実際に数えた計算回数**。**Forward は重なるほど増え、Deferred は画面のマス数 × ライト数で止まる** |

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
| **オーバードロー** | **手前の物体が後から描かれる**と**奥の物体のライティング済みの色が、無駄**になる。**重い計算を捨てている** |
| **ライトが多いと** | **1 ピクセルごとに全ライトをループ**。**100 個で、100 倍** |
| **ライトの数が物体ごとに違う** | **物体ごとにシェーダー（バリアント）を切り替える**（**ライト数 N のシェーダー**）。**ドロー コール・状態切り替えが増える** |
| **範囲外のライト** | **遠いライトも計算**（**影響がゼロでも**）してしまう |

### 工夫と限界

| 工夫 | 説明 |
| --- | --- |
| **Z プリパス**（深度だけ、先に描く） | **オーバードローのライティングを避ける**（[オーバードロー](overdraw.md)）。**ジオメトリを、2 回描く** |
| **ライトの上限**（物体ごとに近い 4 つだけ） | **簡単だがライトがちらつく・多数のライトが使えない** |
| **ライトの事前の絞り込み** | **Tiled / Clustered Forward**（[Tiled と Clustered](light-culling.md)） |

### Forward の、長所

| 長所 | 説明 |
| --- | --- |
| **帯域が少ない** | **G-Buffer が不要**。**直接、画面に書く** |
| **MSAA が使える** | **ハードウェアのアンチエイリアシングが、素直に使える** |
| **半透明が扱える** | **普通にブレンドできる** |
| **材質が自由** | **物体ごとにシェーダーを変えて、特殊な表現**（髪・肌・布）ができる |
| **単純** | **仕組みが分かりやすい** |

**ライトが少ない**（太陽 ＋ 数個）なら、**Forward が最適**なことも多いです（**VR・モバイル・スタイライズされた表現**）。

## Deferred（遅延）レンダリング

<strong>「形と材質の情報」を、先にバッファ（G-Buffer）に書き</strong>、<strong>「ライティング」を、あとで画面全体に対して、まとめて行う</strong>方式です。

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
| **オーバードローのライティングが消える** | **ライティングは、最終的に見えるピクセルだけ**（1 ピクセル 1 回） |
| <strong>「物体 × ライト」が、「物体 ＋ ライト」に</strong> | **ジオメトリの数とライトの数が独立**。**ライトをたくさん置ける** |
| **ライトの範囲を使える** | **ライトが影響する範囲（球・円錐）のピクセルだけ**、計算できる（ライト ボリューム） |
| **シェーダーの切り替えが、減る** | **ライティングのシェーダーは、1 種類**。**材質の違いは、G-Buffer の値** |
| **ポストエフェクトに使える** | **G-Buffer（法線・深度）を、AO・SSR・デカールが再利用** |

**ライトが数百個**（**街灯・たいまつ・窓の明かり**）ある**大規模なシーン**で、**Deferred が使われます**。

### ライト ボリューム

**ライトごとに影響する範囲**（球・円錐）を、**簡単な形**として描き、**その形が覆うピクセルだけ**を、**ライティング**します。

| ライトの種類 | 描く形 |
| --- | --- |
| **ポイントライト** | **球** |
| **スポットライト** | **円錐** |
| <strong>ディレクショナル（太陽）</strong> | **フルスクリーン**（画面全体） |

**遠くのライトは、小さな範囲**なので**少ないピクセル**で済みます。**ライトごとに、G-Buffer を読み直す**——これが次の問題になります。

### 代償（何が悪くなるか）

| 問題 | 説明 |
| --- | --- |
| **帯域が重い** | **G-Buffer の書き込み**（複数 RT）と、**ライトごとの読み込み**。**100 ライトで数百 GB/s**（[メモリ帯域幅](bandwidth.md)） |
| **MSAA が難しい** | **G-Buffer がサンプル数倍**になる。**TAA・FXAA** で代用 |
| **半透明が使えない** | **G-Buffer に、1 ピクセル 1 つの情報しか、書けない**。**半透明は別の Forward パス**で描く |
| **材質の多様性が制限される** | **G-Buffer に入る項目だけ**。**特殊な材質（髪・肌・布）は、工夫**（シェーディング モデル ID） |
| **ライトのブレンドの帯域** | **ライトごとに結果を加算ブレンドで書く**（読み書きが重なる） |
| **G-Buffer の設計が、難しい** | **何をどのフォーマットで詰めるか** |

## 比べ

| | **Forward** | **Deferred** |
| --- | --- | --- |
| **ライティングの回数** | <strong>物体ごと（オーバードロー込み）</strong> | **ピクセルごとに、1 回** |
| **ライトが多い** | **苦手**（掛け算） | **得意** |
| **帯域** | **少ない** | **多い**（G-Buffer） |
| **MSAA** | **◎** | **×**（難しい） |
| **半透明** | **◎** | **×**（別パス） |
| **材質の自由度** | **◎** | **△**（G-Buffer に収まる範囲） |
| **向く場面** | **ライトが少ない・VR・モバイル** | **ライトが多い・大規模な屋外** |

**実際のエンジンは、組み合わせ**ます：**不透明は Deferred、半透明は Forward**。**Clustered / Tiled** で、**どちらもライトが多くても速く**できます。

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

**次のページ**：[Tiled と Clustered](light-culling.md)（ライトの絞り込みで**帯域も計算も減らす**）。

## よくあるミス

??? failure "ライトが数個なのに、Deferred にして、遅くなる"
    **G-Buffer の帯域**が、**メリットを上回ります**。**Forward が速い**こともあります。

??? failure "Deferred で、MSAA を使おうとして、帯域が爆発する"
    **TAA** など、別の方式にします。

??? failure "半透明を、Deferred のパスで描こうとする"
    **半透明は、Forward パス**で、**後から**描きます。

??? failure "ライトごとに、フルスクリーンで描画する"
    **帯域が尽きます**。**ライト ボリューム**で範囲を絞るか、**Tiled / Clustered**に。

??? failure "G-Buffer に、位置（RGBA32F）を、保存する"
    **深度から復元**します（[メモリ帯域幅](bandwidth.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>Forward ＝ 物体を描きながら、ライティング</strong>。<strong>コスト ＝ 物体のピクセル（オーバードロー込み）× ライト</strong>
    - [x] <strong>Deferred ＝ G-Buffer に書いてから、画面の各ピクセルで 1 回だけ、ライティング</strong>
    - [x] 改善：<strong>オーバードローのライティングが消える</strong>。<strong>物体とライトの掛け算が足し算に</strong>
    - [x] 代償：<strong>G-Buffer の帯域・MSAA・半透明・材質の自由度</strong>
    - [x] <strong>ライトが少なければ Forward、多ければ Deferred</strong>。<strong>半透明は Forward で</strong>
    - [x] 次は<strong>Tiled / Clustered</strong>（ライトの絞り込み）

## 関連ページ

- [描画の最適化（詳細）](index.md)
- [メモリ帯域幅](bandwidth.md)
- [Tiled と Clustered](light-culling.md)
- [オーバードローと Z プリパス](overdraw.md)
- [法線とライティング](../3d/lighting-normals.md)
- [PBR](../3d/pbr.md)
