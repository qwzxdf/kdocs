---
title: Depth of Field (DOF)
tags:
  - 描画
---

# Depth of Field (DOF)

<strong>被写界深度（Depth of Field）</strong>は、**カメラの「ピントが合う範囲」の外がぼける**効果です。**ピントが合った物が際立ち、手前や奥がぼける**ので**視線を誘導し、「撮影された」映画的な絵**になります。**3D の描画は、すべてにピントが合ったピンホール カメラ**なので、**ぼかしを後から加える**必要があります。このセクションでは、**錯乱円・ギャザー方式・スキャッター方式・前景と背景の扱い・ボケの形**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - DOF ＝ <strong>ピント面から離れるほど、ぼかす</strong>。<strong>ぼかしの大きさ ＝ 錯乱円（CoC）</strong>。
    - 処理は<strong>① 各画素の CoC を計算 → ② CoC に応じてぼかす</strong>。
    - <strong>ギャザー</strong>：<strong>各画素が周りを集めてぼける</strong>（<strong>簡単・速い</strong>）。<strong>スキャッター</strong>：<strong>明るい点が円盤として広がる</strong>（<strong>きれい・重い</strong>）。
    - <strong>前景</strong>は<strong>手前の物が奥にぼけて広がる</strong>ので、<strong>背景と別に処理</strong>する。
    - <strong>ボケの形</strong>（<strong>円・絞り羽根の多角形</strong>）が<strong>画の味</strong>を決める。
    - <strong>コスト</strong>は<strong>ボケの最大半径</strong>で決まる。<strong>半解像度・タイル</strong>で抑える。

## 動きで見る

<!-- fig:dof-focus-sweep:begin -->

<svg class="fig illust motion" data-fig="dof-focus-sweep" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-dof-focus-sweep" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
<filter id="df-b0" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3.0"/>
</filter>
<filter id="df-b1" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="6.0"/>
</filter>
<filter id="df-b2" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="10.0"/>
</filter>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ピント位置を動かすと、ボケる物が変わる</text>
<line x1="60" y1="110" x2="720" y2="110" stroke="#1f2937" stroke-width="2"/>
<text x="60" y="72" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">カメラ → 奥行き</text>
<circle cx="137.6470588235294" cy="110" r="10" fill="#e5484d"/>
<text x="137.6470588235294" y="138" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5484d">手前</text>
<circle cx="370.5882352941176" cy="110" r="10" fill="#2ea043"/>
<text x="370.5882352941176" y="138" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2ea043">中間</text>
<circle cx="603.5294117647059" cy="110" r="10" fill="#2563eb"/>
<text x="603.5294117647059" y="138" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#2563eb">奥</text>
<rect x="57.0" y="84" width="6" height="52" fill="#e5aa28"><animate attributeName="x" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.1013;0.1225;0.1437;0.1650;0.1862;0.2075;0.2288;0.2500;0.2712;0.2925;0.3137;0.3350;0.3563;0.3775;0.3987;0.4200;0.4412;0.4625;0.4838;0.5050;0.5262;0.5475;0.5687;0.5900;0.6112;0.6325;0.6538;0.6750;0.6963;0.7175;0.7388;0.7600;1.0000" values="57;57;76.41;95.82;115.24;134.65;154.06;173.47;192.88;212.29;231.71;251.12;270.53;289.94;309.35;328.76;348.18;367.59;387;406.41;425.82;445.24;464.65;484.06;503.47;522.88;542.29;561.71;581.12;600.53;619.94;639.35;658.76;678.18;678.18"/></rect>
<text x="60" y="166" text-anchor="start" style="font-size:12px;font-weight:500;fill:#e5aa28">橙の線 = ピントが合う奥行き</text>
<rect x="60" y="190" width="660" height="170" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5"/>
<circle cx="190" cy="275" r="34" fill="#e5484d" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1013;0.1225;0.1437;0.1650;0.1862;0.2075;0.2288;0.2500;0.2712;0.2925;0.3137;0.3350;0.3563;0.3775;0.3987;0.4200;0.4412;0.4625;0.4838;0.5050;0.5262;0.5475;0.5687;0.5900;0.6112;0.6325;0.6538;0.6750;0.6963;0.7175;0.7388;0.7600;1.0000" values="0;0;0.53;0.65;0.77;0.88;1;0.88;0.77;0.65;0.53;0.42;0.3;0.18;0.07;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0"/></circle>
<circle cx="190" cy="275" r="34" fill="#e5484d" opacity="0" filter="url(#df-b0)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1013;0.1225;0.1437;0.1650;0.1862;0.2075;0.2288;0.2500;0.2712;0.2925;0.3137;0.3350;0.3563;0.3775;0.3987;0.4200;0.4412;0.4625;0.4838;0.5050;0.5262;0.5475;0.5687;0.5900;0.6112;0.6325;0.6538;0.6750;0.6963;0.7175;0.7388;0.7600;1.0000" values="0;0;0.47;0.35;0.23;0.12;0;0.12;0.23;0.35;0.47;0.58;0.7;0.82;0.93;0.95;0.83;0.72;0.6;0.48;0.37;0.25;0.13;0.02;0;0;0;0;0;0;0;0;0;0;0;0"/></circle>
<circle cx="190" cy="275" r="34" fill="#e5484d" opacity="0" filter="url(#df-b1)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.1013;0.1225;0.1437;0.1650;0.1862;0.2075;0.2288;0.2500;0.2712;0.2925;0.3137;0.3350;0.3563;0.3775;0.3987;0.4200;0.4412;0.4625;0.4838;0.5050;0.5262;0.5475;0.5687;0.5900;0.6112;0.6325;0.6538;0.6750;0.6963;0.7175;0.7388;0.7600;1.0000" values="0;0;0;0;0;0;0;0;0;0;0;0;0;0;0.05;0.17;0.28;0.4;0.52;0.63;0.75;0.87;0.98;0.93;0.84;0.75;0.66;0.58;0.49;0.4;0.31;0.23;0.14;0.05;0.05"/></circle>
<circle cx="190" cy="275" r="34" fill="#e5484d" opacity="0" filter="url(#df-b2)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.1013;0.1225;0.1437;0.1650;0.1862;0.2075;0.2288;0.2500;0.2712;0.2925;0.3137;0.3350;0.3563;0.3775;0.3987;0.4200;0.4412;0.4625;0.4838;0.5050;0.5262;0.5475;0.5687;0.5900;0.6112;0.6325;0.6538;0.6750;0.6963;0.7175;0.7388;0.7600;1.0000" values="0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0.07;0.16;0.25;0.34;0.42;0.51;0.6;0.69;0.77;0.86;0.95;0.95"/></circle>
<circle cx="360" cy="275" r="28" fill="#2ea043" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.1013;0.1225;0.1437;0.1650;0.1862;0.2075;0.2288;0.2500;0.2712;0.2925;0.3137;0.3350;0.3563;0.3775;0.3987;0.4200;0.4412;0.4625;0.4838;0.5050;0.5262;0.5475;0.5687;0.5900;0.6112;0.6325;0.6538;0.6750;0.6963;0.7175;0.7388;0.7600;1.0000" values="0;0;0;0;0;0;0;0;0;0.07;0.18;0.3;0.42;0.53;0.65;0.77;0.88;1;0.88;0.77;0.65;0.53;0.42;0.3;0.18;0.07;0;0;0;0;0;0;0;0;0"/></circle>
<circle cx="360" cy="275" r="28" fill="#2ea043" opacity="0" filter="url(#df-b0)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1013;0.1225;0.1437;0.1650;0.1862;0.2075;0.2288;0.2500;0.2712;0.2925;0.3137;0.3350;0.3563;0.3775;0.3987;0.4200;0.4412;0.4625;0.4838;0.5050;0.5262;0.5475;0.5687;0.5900;0.6112;0.6325;0.6538;0.6750;0.6963;0.7175;0.7388;0.7600;1.0000" values="0;0;0.13;0.25;0.37;0.48;0.6;0.72;0.83;0.95;0.93;0.82;0.7;0.58;0.47;0.35;0.23;0.12;0;0.12;0.23;0.35;0.47;0.58;0.7;0.82;0.93;0.95;0.83;0.72;0.6;0.48;0.37;0.25;0.13;0.13"/></circle>
<circle cx="360" cy="275" r="28" fill="#2ea043" opacity="0" filter="url(#df-b1)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1013;0.1225;0.1437;0.1650;0.1862;0.2075;0.2288;0.2500;0.2712;0.2925;0.3137;0.3350;0.3563;0.3775;0.3987;0.4200;0.4412;0.4625;0.4838;0.5050;0.5262;0.5475;0.5687;0.5900;0.6112;0.6325;0.6538;0.6750;0.6963;0.7175;0.7388;0.7600;1.0000" values="0;0;0.87;0.75;0.63;0.52;0.4;0.28;0.17;0.05;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0.05;0.17;0.28;0.4;0.52;0.63;0.75;0.87;0.87"/></circle>
<circle cx="360" cy="275" r="28" fill="#2ea043" opacity="0" filter="url(#df-b2)"/>
<circle cx="530" cy="275" r="22" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.1013;0.1225;0.1437;0.1650;0.1862;0.2075;0.2288;0.2500;0.2712;0.2925;0.3137;0.3350;0.3563;0.3775;0.3987;0.4200;0.4412;0.4625;0.4838;0.5050;0.5262;0.5475;0.5687;0.5900;0.6112;0.6325;0.6538;0.6750;0.6963;0.7175;0.7388;0.7600;1.0000" values="0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0.07;0.18;0.3;0.42;0.53;0.65;0.77;0.88;1;0.88;0.77;0.65;0.53;0.53"/></circle>
<circle cx="530" cy="275" r="22" fill="#2563eb" opacity="0" filter="url(#df-b0)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.1013;0.1225;0.1437;0.1650;0.1862;0.2075;0.2288;0.2500;0.2712;0.2925;0.3137;0.3350;0.3563;0.3775;0.3987;0.4200;0.4412;0.4625;0.4838;0.5050;0.5262;0.5475;0.5687;0.5900;0.6112;0.6325;0.6538;0.6750;0.6963;0.7175;0.7388;0.7600;1.0000" values="0;0;0;0;0;0;0;0;0;0;0;0;0.02;0.13;0.25;0.37;0.48;0.6;0.72;0.83;0.95;0.93;0.82;0.7;0.58;0.47;0.35;0.23;0.12;0;0.12;0.23;0.35;0.47;0.47"/></circle>
<circle cx="530" cy="275" r="22" fill="#2563eb" opacity="0" filter="url(#df-b1)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1013;0.1225;0.1437;0.1650;0.1862;0.2075;0.2288;0.2500;0.2712;0.2925;0.3137;0.3350;0.3563;0.3775;0.3987;0.4200;0.4412;0.4625;0.4838;0.5050;0.5262;0.5475;0.5687;0.5900;0.6112;0.6325;0.6538;0.6750;0.6963;0.7175;0.7388;0.7600;1.0000" values="0;0;0.05;0.14;0.23;0.31;0.4;0.49;0.58;0.66;0.75;0.84;0.93;0.98;0.87;0.75;0.63;0.52;0.4;0.28;0.17;0.05;0;0;0;0;0;0;0;0;0;0;0;0;0;0"/></circle>
<circle cx="530" cy="275" r="22" fill="#2563eb" opacity="0" filter="url(#df-b2)"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1013;0.1225;0.1437;0.1650;0.1862;0.2075;0.2288;0.2500;0.2712;0.2925;0.3137;0.3350;0.3563;0.3775;0.3987;0.4200;0.4412;0.4625;0.4838;0.5050;0.5262;0.5475;0.5687;0.5900;0.6112;0.6325;0.6538;0.6750;0.6963;0.7175;0.7388;0.7600;1.0000" values="0;0;0.95;0.86;0.77;0.69;0.6;0.51;0.42;0.34;0.25;0.16;0.07;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0"/></circle>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 1.0（手前）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.1009;0.1013;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 1.3（手前）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1009;0.1013;0.1222;0.1225;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 1.5（手前）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1222;0.1225;0.1434;0.1437;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 1.8（手前）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1434;0.1437;0.1647;0.1650;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 2.0（手前）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1647;0.1650;0.1859;0.1862;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 2.3（手前）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1859;0.1862;0.2072;0.2075;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 2.5（手前）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2072;0.2075;0.2284;0.2288;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 2.8（手前）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2284;0.2288;0.2497;0.2500;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 3.1（手前）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2497;0.2500;0.2709;0.2712;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 3.3（手前）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2709;0.2712;0.2922;0.2925;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 3.6（中間）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2922;0.2925;0.3134;0.3137;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 3.8（中間）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3134;0.3137;0.3347;0.3350;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 4.1（中間）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3347;0.3350;0.3559;0.3563;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 4.4（中間）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3559;0.3563;0.3772;0.3775;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 4.6（中間）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3772;0.3775;0.3984;0.3987;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 4.9（中間）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3984;0.3987;0.4197;0.4200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 5.1（中間）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4197;0.4200;0.4409;0.4412;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 5.4（中間）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4409;0.4412;0.4622;0.4625;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 5.6（中間）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4622;0.4625;0.4834;0.4838;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 5.9（中間）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4834;0.4838;0.5047;0.5050;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 6.2（中間）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5047;0.5050;0.5259;0.5262;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 6.4（中間）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5259;0.5262;0.5472;0.5475;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 6.7（奥）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5472;0.5475;0.5684;0.5687;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 6.9（奥）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5684;0.5687;0.5897;0.5900;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 7.2（奥）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5897;0.5900;0.6109;0.6112;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 7.5（奥）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6109;0.6112;0.6322;0.6325;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 7.7（奥）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6322;0.6325;0.6534;0.6538;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 8.0（奥）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6534;0.6538;0.6747;0.6750;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 8.2（奥）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6747;0.6750;0.6959;0.6963;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 8.5（奥）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6959;0.6963;0.7172;0.7175;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 8.7（奥）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7172;0.7175;0.7384;0.7388;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">ピント = 奥行き 9.0（奥）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7384;0.7388;0.7597;0.7600;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:dof-focus-sweep:end -->

## 全体の流れ

| 手順 | 内容 | ページ |
| --- | --- | --- |
| **① CoC を求める** | **深度とカメラの設定から、各画素のボケの大きさ** | [錯乱円](coc.md) |
| <strong>② ぼかす（集める）</strong> | **各画素が周りを集めて平均** | [Gather Method](gather.md) |
| <strong>②' ぼかす（散らす）</strong> | **明るい点を円盤として広げる** | [Scatter Method](scatter.md) |
| **③ 前景と背景** | **ピントの手前と奥を別々に処理して、境の破綻を防ぐ** | [Foreground and Background](near-far.md) |
| **④ ボケの形** | **円盤・多角形・サンプル配置・光学的な個性** | [Bokeh Shape](bokeh-shape.md) |

## 方式の比較

| 方式 | 内容 | 品質 | 速さ | 向く場面 |
| --- | --- | --- | --- | --- |
| **ガウスで近似** | **CoC でガウスのぼかしを使い分け** | <strong>低（形が出ない）</strong> | **最速** | **モバイル・簡易** |
| <strong>ギャザー（螺旋サンプル）</strong> | **各画素が円盤状に周りを集める** | **中〜高** | **速い** | **標準** |
| **スキャッター** | **明るい点をスプライトとして広げる** | <strong>最高（ボケの形が正確）</strong> | **重い** | **映画風・ハイエンド** |
| **レイトレ DOF** | **光線をレンズ上でずらして撮る** | **最高** | **非常に重い** | **オフライン・研究** |

## 関連ページ

- [Post-Processing](../index.md)
- [Exposure](../tonemapping/exposure.md)
- [Motion Blur](../motion-blur/index.md)
- [Bloom](../bloom/index.md)
