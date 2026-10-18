---
title: Water Fresnel
tags:
  - 描画
---

# Water Fresnel

**水は、真上から見ると、透けて底が見え、斜めから見ると、空を映す鏡のようになります**。**この反射と屈折の割合が、フレネル**です。このページでは、**水のフレネルの式と使い方**を説明します。

!!! tip "ポイント"
    - **水の F0 は 0.02 程度**（ガラスより低い）。
    - **Schlick 近似で、安く計算**。
    - **反射色と屈折色を、F で混ぜる**。
    - **遠く（斜め）ほど、反射が強い**。

<!-- fig:water-fresnel:begin -->

<svg class="fig illust motion" data-fig="water-fresnel" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-water-fresnel" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">水のフレネル:浅い角度ほど、反射が強くなる</text>
<rect x="40" y="250" width="420" height="130" fill="#bae6fd" fill-opacity="0.8"/>
<line x1="40" y1="250" x2="460" y2="250" stroke="#0284c7" stroke-width="3"/>
<rect x="40" y="80" width="420" height="170" fill="#e0f2fe" fill-opacity="0.5"/>
<text x="50" y="104" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">空</text>
<text x="50" y="372" text-anchor="start" style="font-size:12px;font-weight:700;fill:#0284c7">水の中</text>
<circle cx="100" cy="140" r="10" fill="#2563eb"><animate attributeName="cx" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0883;0.1174;0.1464;0.1755;0.2046;0.2336;0.2627;0.2917;0.3208;0.3499;0.3789;0.4080;0.4370;0.4661;0.4952;0.5242;0.5533;0.5823;0.6114;0.6405;0.6695;0.6986;0.7276;0.7567;0.7858;0.8148;1.0000" values="100;100;81.65;83.17;85.16;87.63;90.57;93.96;97.81;102.1;106.81;111.93;117.46;123.36;129.63;136.25;143.19;150.45;157.99;165.79;173.84;182.11;190.57;199.21;207.99;216.89;225.89;234.96;244.07;244.07"/><animate attributeName="cy" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0883;0.1174;0.1464;0.1755;0.2046;0.2336;0.2627;0.2917;0.3208;0.3499;0.3789;0.4080;0.4370;0.4661;0.4952;0.5242;0.5533;0.5823;0.6114;0.6405;0.6695;0.6986;0.7276;0.7567;0.7858;0.8148;1.0000" values="140;140;226.34;217.34;208.43;199.64;191;182.53;174.25;166.19;158.37;150.82;143.55;136.59;129.95;123.67;117.74;112.2;107.05;102.32;98.01;94.15;90.73;87.77;85.27;83.26;81.72;80.67;80.1;80.1"/></circle>
<line x1="100" y1="140" x2="250" y2="250" stroke="#2563eb" stroke-width="3"><animate attributeName="x1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0883;0.1174;0.1464;0.1755;0.2046;0.2336;0.2627;0.2917;0.3208;0.3499;0.3789;0.4080;0.4370;0.4661;0.4952;0.5242;0.5533;0.5823;0.6114;0.6405;0.6695;0.6986;0.7276;0.7567;0.7858;0.8148;1.0000" values="100;100;81.65;83.17;85.16;87.63;90.57;93.96;97.81;102.1;106.81;111.93;117.46;123.36;129.63;136.25;143.19;150.45;157.99;165.79;173.84;182.11;190.57;199.21;207.99;216.89;225.89;234.96;244.07;244.07"/><animate attributeName="y1" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0883;0.1174;0.1464;0.1755;0.2046;0.2336;0.2627;0.2917;0.3208;0.3499;0.3789;0.4080;0.4370;0.4661;0.4952;0.5242;0.5533;0.5823;0.6114;0.6405;0.6695;0.6986;0.7276;0.7567;0.7858;0.8148;1.0000" values="140;140;226.34;217.34;208.43;199.64;191;182.53;174.25;166.19;158.37;150.82;143.55;136.59;129.95;123.67;117.74;112.2;107.05;102.32;98.01;94.15;90.73;87.77;85.27;83.26;81.72;80.67;80.1;80.1"/></line>
<line x1="250" y1="250" x2="400" y2="100" stroke="#e5aa28" stroke-width="3" opacity="1"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0883;0.1174;0.1464;0.1755;0.2046;0.2336;0.2627;0.2917;0.3208;0.3499;0.3789;0.4080;0.4370;0.4661;0.4952;0.5242;0.5533;0.5823;0.6114;0.6405;0.6695;0.6986;0.7276;0.7567;0.7858;0.8148;1.0000" values="400;400;418.35;416.83;414.84;412.37;409.43;406.04;402.19;397.9;393.19;388.07;382.54;376.64;370.37;363.75;356.81;349.55;342.01;334.21;326.16;317.89;309.43;300.79;292.01;283.11;274.11;265.04;255.93;255.93"/><animate attributeName="y2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0883;0.1174;0.1464;0.1755;0.2046;0.2336;0.2627;0.2917;0.3208;0.3499;0.3789;0.4080;0.4370;0.4661;0.4952;0.5242;0.5533;0.5823;0.6114;0.6405;0.6695;0.6986;0.7276;0.7567;0.7858;0.8148;1.0000" values="100;100;226.34;217.34;208.43;199.64;191;182.53;174.25;166.19;158.37;150.82;143.55;136.59;129.95;123.67;117.74;112.2;107.05;102.32;98.01;94.15;90.73;87.77;85.27;83.26;81.72;80.67;80.1;80.1"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0883;0.1174;0.1464;0.1755;0.2046;0.2336;0.2627;0.2917;0.3208;0.3499;0.3789;0.4080;0.4370;0.4661;0.4952;0.5242;0.5533;0.5823;0.6114;0.6405;0.6695;0.6986;0.7276;0.7567;0.7858;0.8148;1.0000" values="1;1;0.56;0.45;0.37;0.31;0.27;0.23;0.21;0.19;0.18;0.18;0.17;0.17;0.17;0.17;0.17;0.17;0.17;0.17;0.17;0.17;0.17;0.17;0.17;0.17;0.17;0.17;0.17;0.17"/></line>
<line x1="250" y1="250" x2="300" y2="360" stroke="#2ea043" stroke-width="3" opacity="1"><animate attributeName="x2" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0883;0.1174;0.1464;0.1755;0.2046;0.2336;0.2627;0.2917;0.3208;0.3499;0.3789;0.4080;0.4370;0.4661;0.4952;0.5242;0.5533;0.5823;0.6114;0.6405;0.6695;0.6986;0.7276;0.7567;0.7858;0.8148;1.0000" values="300;300;309.42;308.88;308.18;307.31;306.27;305.07;303.71;302.2;300.54;298.73;296.78;294.7;292.48;290.15;287.7;285.14;282.48;279.72;276.88;273.96;270.97;267.93;264.83;261.69;258.51;255.31;252.09;252.09"/><animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0883;0.1174;0.1464;0.1755;0.2046;0.2336;0.2627;0.2917;0.3208;0.3499;0.3789;0.4080;0.4370;0.4661;0.4952;0.5242;0.5533;0.5823;0.6114;0.6405;0.6695;0.6986;0.7276;0.7567;0.7858;0.8148;1.0000" values="1;1;0.59;0.7;0.78;0.84;0.88;0.92;0.94;0.96;0.97;0.97;0.98;0.98;0.98;0.98;0.98;0.98;0.98;0.98;0.98;0.98;0.98;0.98;0.98;0.98;0.98;0.98;0.98;0.98"/></line>
<rect x="520" y="90" width="220" height="160" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="575.0" y1="90" x2="575.0" y2="250" stroke="#e2e8f0" stroke-width="1"/>
<line x1="520" y1="130.0" x2="740" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="630.0" y1="90" x2="630.0" y2="250" stroke="#e2e8f0" stroke-width="1"/>
<line x1="520" y1="170.0" x2="740" y2="170.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="685.0" y1="90" x2="685.0" y2="250" stroke="#e2e8f0" stroke-width="1"/>
<line x1="520" y1="210.0" x2="740" y2="210.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="740" y="270" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">見る角度（水面から）</text>
<text x="520" y="82" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">反射の割合</text>
<path d="M520.0,90.0 L523.67,109.48 L527.33,126.96 L531.0,142.59 L534.67,156.52 L538.33,168.88 L542.0,179.82 L545.67,189.46 L549.33,197.91 L553.0,205.3 L556.67,211.73 L560.33,217.3 L564.0,222.1 L567.67,226.22 L571.33,229.75 L575.0,232.74 L578.67,235.28 L582.33,237.41 L586.0,239.19 L589.67,240.67 L593.33,241.9 L597.0,242.91 L600.67,243.73 L604.33,244.4 L608.0,244.93 L611.67,245.36 L615.33,245.7 L619.0,245.97 L622.67,246.18 L626.33,246.34 L630.0,246.46 L633.67,246.56 L637.33,246.62 L641.0,246.68 L644.67,246.71 L648.33,246.74 L652.0,246.76 L655.67,246.77 L659.33,246.78 L663.0,246.79 L666.67,246.79 L670.33,246.8 L674.0,246.8 L677.67,246.8 L681.33,246.8 L685.0,246.8 L688.67,246.8 L692.33,246.8 L696.0,246.8 L699.67,246.8 L703.33,246.8 L707.0,246.8 L710.67,246.8 L714.33,246.8 L718.0,246.8 L721.67,246.8 L725.33,246.8 L729.0,246.8 L732.67,246.8 L736.33,246.8 L740.0,246.8" fill="none" stroke="#e5484d" stroke-width="3" opacity="1"/>
<circle cx="520.0" cy="90.0" r="6" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0883;0.1174;0.1464;0.1755;0.2046;0.2336;0.2627;0.2917;0.3208;0.3499;0.3789;0.4080;0.4370;0.4661;0.4952;0.5242;0.5533;0.5823;0.6114;0.6405;0.6695;0.6986;0.7276;0.7567;0.7858;0.8148;1.0000" values="520;520;539.56;547.08;554.6;562.12;569.64;577.16;584.68;592.21;599.73;607.25;614.77;622.29;629.81;637.33;644.85;652.38;659.9;667.42;674.94;682.46;689.98;697.5;705.03;712.55;720.07;727.59;735.11;735.11"/><animate attributeName="cy" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0883;0.1174;0.1464;0.1755;0.2046;0.2336;0.2627;0.2917;0.3208;0.3499;0.3789;0.4080;0.4370;0.4661;0.4952;0.5242;0.5533;0.5823;0.6114;0.6405;0.6695;0.6986;0.7276;0.7567;0.7858;0.8148;1.0000" values="90;90;172.68;192.84;208.21;219.73;228.19;234.29;238.59;241.55;243.54;244.83;245.66;246.16;246.46;246.62;246.72;246.76;246.78;246.79;246.8;246.8;246.8;246.8;246.8;246.8;246.8;246.8;246.8;246.8"/></circle>
<rect x="520" y="300" width="220" height="26" fill="#2ea043"/>
<rect x="520" y="300" width="0.001" height="26" fill="#e5aa28"><animate attributeName="width" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0883;0.1174;0.1464;0.1755;0.2046;0.2336;0.2627;0.2917;0.3208;0.3499;0.3789;0.4080;0.4370;0.4661;0.4952;0.5242;0.5533;0.5823;0.6114;0.6405;0.6695;0.6986;0.7276;0.7567;0.7858;0.8148;1.0000" values="0.001;0.001;106.31;78.59;57.46;41.62;29.99;21.6;15.69;11.62;8.89;7.1;5.97;5.28;4.87;4.64;4.52;4.45;4.42;4.41;4.4;4.4;4.4;4.4;4.4;4.4;4.4;4.4;4.4;4.4"/></rect>
<text x="520" y="292" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">反射（橙）と屈折（緑）の割合</text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 8° → 反射 48 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0590;0.0593;0.0880;0.0883;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 11° → 反射 35 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0880;0.0883;0.1171;0.1174;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 14° → 反射 25 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1171;0.1174;0.1461;0.1464;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 17° → 反射 18 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1461;0.1464;0.1752;0.1755;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 20° → 反射 13 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.1752;0.1755;0.2043;0.2046;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 24° → 反射 9 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2043;0.2046;0.2333;0.2336;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 27° → 反射 7 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2333;0.2336;0.2624;0.2627;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 30° → 反射 5 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2624;0.2627;0.2914;0.2917;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 33° → 反射 4 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2914;0.2917;0.3205;0.3208;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 36° → 反射 3 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3205;0.3208;0.3496;0.3499;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 40° → 反射 3 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3496;0.3499;0.3786;0.3789;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 43° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3786;0.3789;0.4077;0.4080;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 46° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4077;0.4080;0.4367;0.4370;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 49° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4367;0.4370;0.4658;0.4661;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 52° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4658;0.4661;0.4949;0.4952;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 56° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.4949;0.4952;0.5239;0.5242;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 59° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5239;0.5242;0.5530;0.5533;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 62° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5530;0.5533;0.5820;0.5823;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 65° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5820;0.5823;0.6111;0.6114;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 68° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6111;0.6114;0.6402;0.6405;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 72° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6402;0.6405;0.6692;0.6695;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 75° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6692;0.6695;0.6983;0.6986;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 78° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6983;0.6986;0.7273;0.7276;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 81° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7273;0.7276;0.7564;0.7567;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 84° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7564;0.7567;0.7855;0.7858;1.0000" values="0;0;1;1;0;0"/></text>
<text x="520" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">角度 88° → 反射 2 %<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.7855;0.7858;0.8145;0.8148;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="406" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">真上から見ると、水の底が見える（反射 2 %）。斜めから見ると、空を映す鏡になる。</text>
</svg>

<!-- fig:water-fresnel:end -->

## Fresnel {#フレネル}
**フレネル**は、<strong>「見る角度が浅いほど、反射が強くなる」</strong>という現象です。**水面に真上から（垂直に）近い角度で見ると反射は約 2 %** で**ほとんどが透過**します。**水平に近い角度で見ると、反射は 100 % に近づき**、**鏡のように**なります。

<div class="formula">F(θ) = F₀ + (1 − F₀) · (1 − cos θ)⁵　（Schlick 近似、水の F₀ ≈ 0.02）</div>

| 記号 | 意味 |
| --- | --- |
| **θ** | **視線と法線のなす角**（`cos θ = dot(N, V)`） |
| **F₀** | **真上から見たときの反射率**。**水は約 0.02**（屈折率 1.33 から求まる） |
| **F** | **反射の割合**（0〜1）。**透過は 1 − F** |

**屈折率 n から F₀ を求める式**です。

<div class="formula">F₀ = ((n₁ − n₂) / (n₁ + n₂))²　（空気 n₁ = 1.0、水 n₂ = 1.33 → F₀ ≈ 0.02）</div>

```hlsl
float Fresnel(float3 normal, float3 view_dir) {
  float cos_theta = saturate(dot(normal, view_dir));
  const float kF0 = 0.02;
  return kF0 + (1.0 - kF0) * pow(1.0 - cos_theta, 5.0);
}
```

<strong>`view_dir` は、「水面から目へ向かう向き」</strong>（正規化済み）です。**向きを逆にすると、`cos θ` の符号が変わる**ので**注意**します。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="フレネルのグラフ">
<text x="20" y="24" class="fig-title">フレネル：見る角度で、反射の割合が変わる（水：F₀ = 0.02）</text>
<line x1="80" y1="220" x2="720" y2="220" stroke="currentColor" stroke-opacity="0.5"/>
<line x1="80" y1="50" x2="80" y2="220" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#4c8bf5" stroke-width="3" points="80,216 160,215 240,213 320,210 400,205 480,196 560,180 620,155 670,110 700,70 720,52"/>
<text x="84" y="44" style="font-size:12px">F（反射の割合）</text>
<text x="76" y="238" style="font-size:12px" text-anchor="end">0</text>
<text x="86" y="240" style="font-size:12px">真上から見る（θ = 0°）</text>
<text x="720" y="240" style="font-size:12px" text-anchor="end">水平に近い（θ → 90°）</text>
<text x="420" y="150" style="font-size:13px">ほとんど変わらない</text>
<text x="560" y="100" style="font-size:13px">急に反射が増える</text>
<line x1="90" y1="52" x2="720" y2="52" stroke="#e5484d" stroke-opacity="0.5" stroke-dasharray="4 4"/>
<text x="400" y="46" style="font-size:12px;fill:#e5484d">F = 1（完全な鏡）</text>
</svg>

**水面の見た目の大半は、この 1 つの式で決まります**。**足元の水は透けて底が見え**、**遠くの水は空を映す**のは、**フレネルのため**です。

## Common Mistakes {#よくあるミス}

??? failure "水が、どの角度でも同じ透明度"
    **フレネルで混ぜ比を変える**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **角度で、反射と屈折が入れ替わる**

## References {#参考}

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## Related Pages {#関連ページ}

- [Water Shading](index.md)
- [フレネル（屈折）](../../translucency/refraction/fresnel.md)
