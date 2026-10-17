---
title: Refraction
tags:
  - 描画
---

# Refraction

**ガラスや水を通して見ると、後ろの景色が曲がって見えます**。**これが屈折**で、**ゲームでは「画面空間の屈折」で、安く近似**します。このセクションでは、**原理・画面空間の屈折・境界の問題・フレネル・厚みと色・色収差・薄いガラスと厚いガラス・実装の全体像**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **屈折 ＝ 光が、物質の境界で曲がる現象**（スネルの法則）。
    - **ゲームでは、既に描いた画面を、ずらして読むだけで近似**。
    - **フレネル（見る角度による反射の強さ）**も**組み合わせる**。
    - **厚み・色（吸収）・色収差**で、**リアルさが増す**。

<!-- fig:snell-refraction:begin -->

<svg class="fig illust motion" data-fig="snell-refraction" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-snell-refraction" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">スネルの法則:境界で光が曲がる（空気 → ガラス、ガラス → 空気）</text>
<text x="190" y="70" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">空気（n = 1.0）→ ガラス（n = 1.5）</text>
<rect x="20" y="100" width="340" height="130" fill="#f8fafc"/>
<rect x="20" y="230" width="340" height="130" fill="#e0f2fe"/>
<line x1="20" y1="230" x2="360" y2="230" stroke="#1f2937" stroke-width="3"/>
<line x1="190" y1="100" x2="190" y2="360" stroke="#e2e8f0" stroke-width="2" stroke-dasharray="4 4"/>
<line x1="190" y1="230" x2="190" y2="100" stroke="#e5aa28" stroke-width="4"><animate attributeName="x2" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.0849;0.1146;0.1443;0.1740;0.2037;0.2334;0.2631;0.2928;0.3225;0.3523;0.3820;0.4117;0.4414;0.4711;0.5008;0.5305;0.5602;0.5899;0.6196;0.6493;0.6790;0.7088;0.7385;0.7682;0.7979;0.8276;1.0000" values="190;190;183.02;176.06;169.15;162.29;155.51;148.83;142.27;135.85;129.59;123.49;117.59;111.9;106.44;101.21;96.24;91.55;87.13;83.01;79.2;75.71;72.55;69.73;67.25;65.13;63.37;61.97;61.97"/><animate attributeName="y2" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.0849;0.1146;0.1443;0.1740;0.2037;0.2334;0.2631;0.2928;0.3225;0.3523;0.3820;0.4117;0.4414;0.4711;0.5008;0.5305;0.5602;0.5899;0.6196;0.6493;0.6790;0.7088;0.7385;0.7682;0.7979;0.8276;1.0000" values="100;100;100.19;100.75;101.68;102.99;104.66;106.69;109.08;111.81;114.89;118.3;122.03;126.07;130.41;135.04;139.95;145.11;150.52;156.15;162;168.05;174.27;180.65;187.18;193.83;200.59;207.43;207.43"/></line>
<line x1="190" y1="230" x2="190" y2="360" stroke="#2563eb" stroke-width="4"><animate attributeName="x2" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.0849;0.1146;0.1443;0.1740;0.2037;0.2334;0.2631;0.2928;0.3225;0.3523;0.3820;0.4117;0.4414;0.4711;0.5008;0.5305;0.5602;0.5899;0.6196;0.6493;0.6790;0.7088;0.7385;0.7682;0.7979;0.8276;1.0000" values="190;190;194.65;199.29;203.9;208.47;212.99;217.44;221.82;226.1;230.28;234.34;238.27;242.06;245.71;249.19;252.5;255.64;258.58;261.33;263.87;266.19;268.3;270.18;271.83;273.24;274.42;275.35;275.35"/><animate attributeName="y2" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.0849;0.1146;0.1443;0.1740;0.2037;0.2334;0.2631;0.2928;0.3225;0.3523;0.3820;0.4117;0.4414;0.4711;0.5008;0.5305;0.5602;0.5899;0.6196;0.6493;0.6790;0.7088;0.7385;0.7682;0.7979;0.8276;1.0000" values="360;360;359.92;359.67;359.25;358.68;357.95;357.07;356.05;354.89;353.6;352.21;350.71;349.12;347.46;345.74;343.99;342.21;340.44;338.69;336.98;335.33;333.78;332.33;331.01;329.85;328.86;328.06;328.06"/></line>
<line x1="190" y1="230" x2="190" y2="100" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="x2" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.0849;0.1146;0.1443;0.1740;0.2037;0.2334;0.2631;0.2928;0.3225;0.3523;0.3820;0.4117;0.4414;0.4711;0.5008;0.5305;0.5602;0.5899;0.6196;0.6493;0.6790;0.7088;0.7385;0.7682;0.7979;0.8276;1.0000" values="190;190;192.44;194.88;197.3;199.7;202.07;204.41;206.7;208.95;211.14;213.28;215.34;217.33;219.25;221.08;222.81;224.46;226;227.45;228.78;230;231.11;232.09;232.96;233.7;234.32;234.81;234.81"/><animate attributeName="y2" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0549;0.0552;0.0849;0.1146;0.1443;0.1740;0.2037;0.2334;0.2631;0.2928;0.3225;0.3523;0.3820;0.4117;0.4414;0.4711;0.5008;0.5305;0.5602;0.5899;0.6196;0.6493;0.6790;0.7088;0.7385;0.7682;0.7979;0.8276;1.0000" values="100;100;184.5;184.57;184.76;185.09;185.55;186.13;186.84;187.68;188.63;189.71;190.9;192.21;193.63;195.14;196.77;198.48;200.29;202.18;204.15;206.2;208.32;210.49;212.73;215.01;217.34;219.71;222.1;222.1"/><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0549;0.0552;0.0849;0.1146;0.1443;0.1740;0.2037;0.2334;0.2631;0.2928;0.3225;0.3523;0.3820;0.4117;0.4414;0.4711;0.5008;0.5305;0.5602;0.5899;0.6196;0.6493;0.6790;0.7088;0.7385;0.7682;0.7979;0.8276;1.0000" values="0;0;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25"/></line>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 0° → 屈折 0°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0549;0.0552;0.0846;0.0849;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 3° → 屈折 2°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0846;0.0849;0.1143;0.1146;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 6° → 屈折 4°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1143;0.1146;0.1440;0.1443;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 10° → 屈折 6°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1440;0.1443;0.1737;0.1740;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 13° → 屈折 8°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1737;0.1740;0.2034;0.2037;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 16° → 屈折 11°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2034;0.2037;0.2331;0.2334;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 19° → 屈折 13°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2331;0.2334;0.2629;0.2631;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 22° → 屈折 15°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2629;0.2631;0.2926;0.2928;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 26° → 屈折 17°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2926;0.2928;0.3223;0.3225;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 29° → 屈折 19°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3223;0.3225;0.3520;0.3523;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 32° → 屈折 21°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3520;0.3523;0.3817;0.3820;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 35° → 屈折 23°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3817;0.3820;0.4114;0.4117;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 38° → 屈折 24°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4114;0.4117;0.4411;0.4414;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 42° → 屈折 26°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4411;0.4414;0.4708;0.4711;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 45° → 屈折 28°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4708;0.4711;0.5005;0.5008;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 48° → 屈折 30°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5005;0.5008;0.5302;0.5305;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 51° → 屈折 31°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5302;0.5305;0.5599;0.5602;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 54° → 屈折 33°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5599;0.5602;0.5896;0.5899;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 58° → 屈折 34°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5896;0.5899;0.6194;0.6196;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 61° → 屈折 36°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6194;0.6196;0.6491;0.6493;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 64° → 屈折 37°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6491;0.6493;0.6788;0.6790;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 67° → 屈折 38°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6788;0.6790;0.7085;0.7088;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 70° → 屈折 39°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7085;0.7088;0.7382;0.7385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 74° → 屈折 40°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7382;0.7385;0.7679;0.7682;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 77° → 屈折 40°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7679;0.7682;0.7976;0.7979;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 80° → 屈折 41°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7976;0.7979;0.8273;0.8276;1.0000" values="0;0;1;1;0;0"/></text>
<text x="590" y="70" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">ガラス → 空気:一定の角度から、全反射</text>
<rect x="420" y="100" width="340" height="130" fill="#e0f2fe"/>
<rect x="420" y="230" width="340" height="130" fill="#f8fafc"/>
<line x1="420" y1="230" x2="760" y2="230" stroke="#1f2937" stroke-width="3"/>
<line x1="590" y1="100" x2="590" y2="360" stroke="#e2e8f0" stroke-width="2" stroke-dasharray="4 4"/>
<line x1="590" y1="230" x2="590" y2="100" stroke="#e5aa28" stroke-width="4"><animate attributeName="x2" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.0849;0.1146;0.1443;0.1740;0.2037;0.2334;0.2631;0.2928;0.3225;0.3523;0.3820;0.4117;0.4414;0.4711;0.5008;0.5305;0.5602;0.5899;0.6196;0.6493;0.6790;0.7088;0.7385;0.7682;0.7979;0.8276;1.0000" values="590;590;583.02;576.06;569.15;562.29;555.51;548.83;542.27;535.85;529.59;523.49;517.59;511.9;506.44;501.21;496.24;491.55;487.13;483.01;479.2;475.71;472.55;469.73;467.25;465.13;463.37;461.97;461.97"/><animate attributeName="y2" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.0849;0.1146;0.1443;0.1740;0.2037;0.2334;0.2631;0.2928;0.3225;0.3523;0.3820;0.4117;0.4414;0.4711;0.5008;0.5305;0.5602;0.5899;0.6196;0.6493;0.6790;0.7088;0.7385;0.7682;0.7979;0.8276;1.0000" values="100;100;100.19;100.75;101.68;102.99;104.66;106.69;109.08;111.81;114.89;118.3;122.03;126.07;130.41;135.04;139.95;145.11;150.52;156.15;162;168.05;174.27;180.65;187.18;193.83;200.59;207.43;207.43"/></line>
<line x1="590" y1="230" x2="590" y2="360" stroke="#2563eb" stroke-width="4"><animate attributeName="x2" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.0849;0.1146;0.1443;0.1740;0.2037;0.2334;0.2631;0.2928;0.3225;0.3523;0.3820;0.4117;0.4414;0.4711;0.5008;0.5305;0.5602;0.5899;0.6196;0.6493;0.6790;0.7088;0.7385;0.7682;0.7979;0.8276;1.0000" values="590;590;600.47;610.9;621.28;631.57;641.73;651.75;661.59;671.22;680.62;689.76;698.61;707.14;715.34;590;590;590;590;590;590;590;590;590;590;590;590;590;590"/><animate attributeName="y2" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.0849;0.1146;0.1443;0.1740;0.2037;0.2334;0.2631;0.2928;0.3225;0.3523;0.3820;0.4117;0.4414;0.4711;0.5008;0.5305;0.5602;0.5899;0.6196;0.6493;0.6790;0.7088;0.7385;0.7682;0.7979;0.8276;1.0000" values="360;360;359.58;358.31;356.18;353.18;349.26;344.4;338.51;331.5;323.21;313.36;301.44;286.37;264.48;230;230;230;230;230;230;230;230;230;230;230;230;230;230"/></line>
<line x1="590" y1="230" x2="590" y2="100" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="x2" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0552;0.0849;0.1146;0.1443;0.1740;0.2037;0.2334;0.2631;0.2928;0.3225;0.3523;0.3820;0.4117;0.4414;0.4711;0.5008;0.5305;0.5602;0.5899;0.6196;0.6493;0.6790;0.7088;0.7385;0.7682;0.7979;0.8276;1.0000" values="590;590;592.44;594.88;597.3;599.7;602.07;604.41;606.7;608.95;611.14;613.28;615.34;617.33;619.25;678.79;683.76;688.45;692.87;696.99;700.8;704.29;707.45;710.27;712.75;714.87;716.63;718.03;718.03"/><animate attributeName="y2" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0549;0.0552;0.0849;0.1146;0.1443;0.1740;0.2037;0.2334;0.2631;0.2928;0.3225;0.3523;0.3820;0.4117;0.4414;0.4711;0.5008;0.5305;0.5602;0.5899;0.6196;0.6493;0.6790;0.7088;0.7385;0.7682;0.7979;0.8276;1.0000" values="100;100;184.5;184.57;184.76;185.09;185.55;186.13;186.84;187.68;188.63;189.71;190.9;192.21;193.63;195.14;135.04;139.95;145.11;150.52;156.15;162;168.05;174.27;180.65;187.18;193.83;200.59;207.43;207.43"/><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0549;0.0552;0.0849;0.1146;0.1443;0.1740;0.2037;0.2334;0.2631;0.2928;0.3225;0.3523;0.3820;0.4117;0.4414;0.4711;0.5008;0.5305;0.5602;0.5899;0.6196;0.6493;0.6790;0.7088;0.7385;0.7682;0.7979;0.8276;1.0000" values="0;0;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;0.25;1;1;1;1;1;1;1;1;1;1;1;1;1;1"/></line>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 0° → 屈折 0°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0549;0.0552;0.0846;0.0849;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 3° → 屈折 5°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0846;0.0849;0.1143;0.1146;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 6° → 屈折 10°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1143;0.1146;0.1440;0.1443;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 10° → 屈折 14°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1440;0.1443;0.1737;0.1740;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 13° → 屈折 19°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1737;0.1740;0.2034;0.2037;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 16° → 屈折 24°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2034;0.2037;0.2331;0.2334;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 19° → 屈折 30°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2331;0.2334;0.2629;0.2631;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 22° → 屈折 35°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2629;0.2631;0.2926;0.2928;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 26° → 屈折 40°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2926;0.2928;0.3223;0.3225;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 29° → 屈折 46°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3223;0.3225;0.3520;0.3523;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 32° → 屈折 53°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3520;0.3523;0.3817;0.3820;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 35° → 屈折 60°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3817;0.3820;0.4114;0.4117;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 38° → 屈折 69°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4114;0.4117;0.4411;0.4414;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 42° → 屈折 85°<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4411;0.4414;0.4708;0.4711;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 45° → 屈折 なし（全反射）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4708;0.4711;0.5005;0.5008;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 48° → 屈折 なし（全反射）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5005;0.5008;0.5302;0.5305;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 51° → 屈折 なし（全反射）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5302;0.5305;0.5599;0.5602;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 54° → 屈折 なし（全反射）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5599;0.5602;0.5896;0.5899;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 58° → 屈折 なし（全反射）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5896;0.5899;0.6194;0.6196;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 61° → 屈折 なし（全反射）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6194;0.6196;0.6491;0.6493;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 64° → 屈折 なし（全反射）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6491;0.6493;0.6788;0.6790;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 67° → 屈折 なし（全反射）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6788;0.6790;0.7085;0.7088;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 70° → 屈折 なし（全反射）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7085;0.7088;0.7382;0.7385;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 74° → 屈折 なし（全反射）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7382;0.7385;0.7679;0.7682;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 77° → 屈折 なし（全反射）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7679;0.7682;0.7976;0.7979;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">入射 80° → 屈折 なし（全反射）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7976;0.7979;0.8273;0.8276;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="412" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">n₁ sin θ₁ = n₂ sin θ₂。ガラス → 空気は、臨界角（約 42°）を超えると、全反射（赤）になる。</text>
</svg>

<!-- fig:snell-refraction:end -->

## 屈折の原理
**光が、空気からガラスや水へ入るとき、境目で曲がります**。<strong>曲がり方は、媒質ごとの「屈折率」</strong>で決まります。

| 媒質 | 屈折率（n） |
| --- | --- |
| **真空・空気** | **1.00** |
| **水** | **1.33** |
| **ガラス** | **約 1.5** |
| **ダイヤモンド** | **約 2.4** |

### スネルの法則

<div class="formula">n₁ · sin θ₁ = n₂ · sin θ₂</div>

| 記号 | 意味 |
| --- | --- |
| **n₁・n₂** | **入る側・出る側の媒質の屈折率** |
| **θ₁** | **入射角**（面の法線と、入る光のなす角） |
| **θ₂** | **屈折角**（面の法線と、曲がった光のなす角） |

**空気（1.0）から水（1.33）へ入る**と、**屈折率が大きい側へ入る**ので、**法線に近づく向きに曲がります**。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="屈折">
<text x="20" y="24" class="fig-title">光は、屈折率の大きい媒質へ入ると、法線に近づく向きに曲がる</text>
<rect x="40" y="140" width="700" height="110" fill="rgba(76,139,245,0.18)"/>
<line x1="40" y1="140" x2="740" y2="140" stroke="currentColor" stroke-width="3"/>
<line x1="390" y1="60" x2="390" y2="230" stroke="currentColor" stroke-dasharray="4 4" stroke-opacity="0.6"/><text x="396" y="70" style="font-size:12px">法線</text>
<line x1="230" y1="50" x2="390" y2="140" stroke="#e5aa28" stroke-width="3"/><text x="230" y="44" style="font-size:12px;fill:#e5aa28">入射光</text>
<line x1="390" y1="140" x2="480" y2="236" stroke="#4c8bf5" stroke-width="3"/><text x="486" y="236" style="font-size:12px;fill:#4c8bf5">屈折光</text>
<line x1="390" y1="140" x2="520" y2="70" stroke="currentColor" stroke-width="2" stroke-opacity="0.5" stroke-dasharray="3 3"/><text x="524" y="68" style="font-size:12px">反射光（フレネルで強さが変わる）</text>
<text x="60" y="120" style="font-size:12px">空気（n = 1.0）</text><text x="60" y="270" style="font-size:12px">ガラスや水（n = 1.33〜1.5）</text>
<path d="M 390 105 A 35 35 0 0 0 366 112" fill="none" stroke="#e5aa28" stroke-width="2"/><text x="352" y="100" style="font-size:12px;fill:#e5aa28">θ₁</text>
<path d="M 390 175 A 35 35 0 0 0 407 170" fill="none" stroke="#4c8bf5" stroke-width="2"/><text x="406" y="196" style="font-size:12px;fill:#4c8bf5">θ₂（θ₁ より小さい）</text>
</svg>

### HLSL の refract

**HLSL の組み込み関数 `refract`** が、**屈折した向き**を返します。

```hlsl
float3 refracted = refract(incident, normal, eta);
```

| 引数 | 内容 |
| --- | --- |
| **`incident`** | **入射する光の向き**（**正規化**済み。**光が進む向き**＝視線方向） |
| **`normal`** | **面の法線**（**入る側を向く**） |
| **`eta`** | **屈折率の比 `n₁ / n₂`**（**空気 → 水なら 1.0 / 1.33**） |
| **戻り値** | **屈折した向き**。**全反射**（臨界角を超える）なら、**`(0, 0, 0)`** |

**視線方向**（カメラから面へ向かう向き）を `incident` に渡します。**反射は `reflect(incident, normal)`** で得られます。

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Screen-Space Refraction](screen-space.md) | 法線で画面をずらす |
| [境界の問題](boundary.md) | 屈折の先に、手前の物が混ざる問題 |
| [Fresnel](fresnel.md) | 反射と屈折の割合 |
| [Thickness and Color](thickness-color.md) | ビア＝ランバートの法則 |
| [Dispersion](dispersion.md) | 色ごとにずらす |
| [Thin and Thick Glass](thin-thick.md) | 窓ガラスと、ガラスの塊 |
| [Implementation Overview and Cost](implementation.md) | 手順・限界 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] **屈折は、画面をずらして読む近似が基本**
    - [x] **フレネル・厚み・色で、リアルになる**

## 参考

- McGuire & Bavoil, "Weighted Blended Order-Independent Transparency"（JCGT 2013）
- Everitt, "Interactive Order-Independent Transparency"（NVIDIA 2001）
- Wyman & McGuire, "Hashed Alpha Testing"（I3D 2017）

## 関連ページ

- [Translucency](../index.md)
- [Water Shading](../../water/shading/index.md)
- [OIT](../oit/index.md)
