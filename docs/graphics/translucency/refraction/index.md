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

<svg class="fig illust motion" data-fig="snell-refraction" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-snell-refraction" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">屈折: ガラス板を斜めに通る光は、曲がり、横にずれて出てくる(スネルの法則)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">厚さ 3 のガラス板(n = 1.5)。入射角を 20° → 40° → 60° → 75° に変えて、曲がる角度とずれを計算する</text>
<rect x="30" y="96" width="900" height="280" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① ガラス板の断面(上 = 空気、中 = ガラス、下 = 空気)</text>
<rect x="150.0" y="215.0" width="360.0" height="90.0" fill="#bae6fd" fill-opacity="0.5" stroke="#38bdf8" stroke-width="2"/>
<text x="156.0" y="233.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#0369a1">ガラス(n = 1.5)</text>
<text x="156.0" y="207.0" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">空気(n = 1)</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2637;0.2638;1.0000" values="1;1;0;0"/><line x1="314.61" y1="172.71" x2="330.0" y2="215.0" stroke="#e5aa28" stroke-width="4"/>
<line x1="330.0" y1="215.0" x2="351.08" y2="305.0" stroke="#e5484d" stroke-width="4"/>
<line x1="351.08" y1="305.0" x2="366.47" y2="347.29" stroke="#e5aa28" stroke-width="4"/>
<line x1="330.0" y1="215.0" x2="362.76" y2="305.0" stroke="#64748b" stroke-width="2" stroke-dasharray="6 5"/>
<line x1="362.76" y1="305.0" x2="378.15" y2="347.29" stroke="#64748b" stroke-width="2" stroke-dasharray="6 5"/>
<line x1="330.0" y1="170.0" x2="330.0" y2="245.0" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="3 4"/>
<text x="50" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed">入射角 20°</text>
<text x="50" y="158" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">sin 20° ÷ 1.5 = sin(屈折角)</text>
<text x="50" y="182" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">屈折角 13.2°</text>
<text x="50" y="208" text-anchor="start" style="font-size:14px;font-weight:700;fill:#92400e">出口の横ずれ(灰色 = 曲がらない場合との差): 0.37</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2637;0.2638;0.4849;0.4851;1.0000" values="0;0;1;1;0;0"/><line x1="301.07" y1="180.53" x2="330.0" y2="215.0" stroke="#e5aa28" stroke-width="4"/>
<line x1="330.0" y1="215.0" x2="372.69" y2="305.0" stroke="#e5484d" stroke-width="4"/>
<line x1="372.69" y1="305.0" x2="401.61" y2="339.47" stroke="#e5aa28" stroke-width="4"/>
<line x1="330.0" y1="215.0" x2="405.52" y2="305.0" stroke="#64748b" stroke-width="2" stroke-dasharray="6 5"/>
<line x1="405.52" y1="305.0" x2="434.44" y2="339.47" stroke="#64748b" stroke-width="2" stroke-dasharray="6 5"/>
<line x1="330.0" y1="170.0" x2="330.0" y2="245.0" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="3 4"/>
<text x="50" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed">入射角 40°</text>
<text x="50" y="158" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">sin 40° ÷ 1.5 = sin(屈折角)</text>
<text x="50" y="182" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">屈折角 25.4°</text>
<text x="50" y="208" text-anchor="start" style="font-size:14px;font-weight:700;fill:#92400e">出口の横ずれ(灰色 = 曲がらない場合との差): 0.84</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4849;0.4851;0.7062;0.7064;1.0000" values="0;0;1;1;0;0"/><line x1="291.03" y1="192.5" x2="330.0" y2="215.0" stroke="#e5aa28" stroke-width="4"/>
<line x1="330.0" y1="215.0" x2="393.64" y2="305.0" stroke="#e5484d" stroke-width="4"/>
<line x1="393.64" y1="305.0" x2="432.61" y2="327.5" stroke="#e5aa28" stroke-width="4"/>
<line x1="330.0" y1="215.0" x2="485.88" y2="305.0" stroke="#64748b" stroke-width="2" stroke-dasharray="6 5"/>
<line x1="485.88" y1="305.0" x2="524.86" y2="327.5" stroke="#64748b" stroke-width="2" stroke-dasharray="6 5"/>
<line x1="330.0" y1="170.0" x2="330.0" y2="245.0" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="3 4"/>
<text x="50" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed">入射角 60°</text>
<text x="50" y="158" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">sin 60° ÷ 1.5 = sin(屈折角)</text>
<text x="50" y="182" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">屈折角 35.3°</text>
<text x="50" y="208" text-anchor="start" style="font-size:14px;font-weight:700;fill:#92400e">出口の横ずれ(灰色 = 曲がらない場合との差): 1.54</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7062;0.7064;1.0000" values="0;0;1;1"/><line x1="286.53" y1="203.35" x2="330.0" y2="215.0" stroke="#e5aa28" stroke-width="4"/>
<line x1="330.0" y1="215.0" x2="405.75" y2="305.0" stroke="#e5484d" stroke-width="4"/>
<line x1="405.75" y1="305.0" x2="449.22" y2="316.65" stroke="#e5aa28" stroke-width="4"/>
<line x1="330.0" y1="215.0" x2="665.88" y2="305.0" stroke="#64748b" stroke-width="2" stroke-dasharray="6 5"/>
<line x1="665.88" y1="305.0" x2="709.35" y2="316.65" stroke="#64748b" stroke-width="2" stroke-dasharray="6 5"/>
<line x1="330.0" y1="170.0" x2="330.0" y2="245.0" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="3 4"/>
<text x="50" y="130" text-anchor="start" style="font-size:22px;font-weight:700;fill:#7c3aed">入射角 75°</text>
<text x="50" y="158" text-anchor="start" style="font-size:14px;font-weight:500;fill:#1f2937">sin 75° ÷ 1.5 = sin(屈折角)</text>
<text x="50" y="182" text-anchor="start" style="font-size:16px;font-weight:700;fill:#e5484d">屈折角 40.1°</text>
<text x="50" y="208" text-anchor="start" style="font-size:14px;font-weight:700;fill:#92400e">出口の横ずれ(灰色 = 曲がらない場合との差): 2.24</text>
</g>
<text x="40" y="410" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">背景の縞模様を、ガラスごしに見たときのずれ:</text>
<rect x="40.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="56.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="72.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="88.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="104.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="120.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="136.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="152.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="168.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="184.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="200.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="216.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="232.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="248.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="264.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="280.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="296.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="312.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="328.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="344.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="360.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="376.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="392.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="408.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="424.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="440.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="456.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="472.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="488.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="504.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="520.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="536.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="552.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#2563eb"/></rect>
<rect x="568.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="584.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="600.0" y="424.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0128" values="#e5e7eb;#93c5fd"/></rect>
<rect x="40.0" y="424" width="576.0" height="16.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="624.0" y="438" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">ガラスなし</text>
<rect x="40.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#2563eb;#93c5fd;#93c5fd"/></rect>
<rect x="56.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="72.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#93c5fd;#93c5fd;#2563eb"/></rect>
<rect x="88.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#93c5fd;#2563eb;#2563eb"/></rect>
<rect x="104.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#2563eb;#2563eb;#2563eb"/></rect>
<rect x="120.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#2563eb;#2563eb;#93c5fd"/></rect>
<rect x="136.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#2563eb;#93c5fd;#93c5fd"/></rect>
<rect x="152.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="168.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#93c5fd;#93c5fd;#2563eb"/></rect>
<rect x="184.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#93c5fd;#2563eb;#2563eb"/></rect>
<rect x="200.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#2563eb;#2563eb;#2563eb"/></rect>
<rect x="216.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#2563eb;#2563eb;#93c5fd"/></rect>
<rect x="232.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#2563eb;#93c5fd;#93c5fd"/></rect>
<rect x="248.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="264.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#93c5fd;#93c5fd;#2563eb"/></rect>
<rect x="280.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#93c5fd;#2563eb;#2563eb"/></rect>
<rect x="296.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#2563eb;#2563eb;#2563eb"/></rect>
<rect x="312.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#2563eb;#2563eb;#93c5fd"/></rect>
<rect x="328.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#2563eb;#93c5fd;#93c5fd"/></rect>
<rect x="344.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="360.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#93c5fd;#93c5fd;#2563eb"/></rect>
<rect x="376.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#93c5fd;#2563eb;#2563eb"/></rect>
<rect x="392.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#2563eb;#2563eb;#2563eb"/></rect>
<rect x="408.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#2563eb;#2563eb;#93c5fd"/></rect>
<rect x="424.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#2563eb;#93c5fd;#93c5fd"/></rect>
<rect x="440.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="456.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#93c5fd;#93c5fd;#2563eb"/></rect>
<rect x="472.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#93c5fd;#2563eb;#2563eb"/></rect>
<rect x="488.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#2563eb;#2563eb;#2563eb"/></rect>
<rect x="504.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#2563eb;#2563eb;#93c5fd"/></rect>
<rect x="520.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#2563eb;#93c5fd;#93c5fd"/></rect>
<rect x="536.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#93c5fd;#93c5fd;#93c5fd"/></rect>
<rect x="552.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#93c5fd;#93c5fd;#2563eb"/></rect>
<rect x="568.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#93c5fd;#2563eb;#2563eb"/></rect>
<rect x="584.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#93c5fd;#2563eb;#2563eb;#2563eb"/></rect>
<rect x="600.0" y="452.0" width="16.3" height="16.3" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0596;0.2809;0.5021;0.7234" values="#e5e7eb;#2563eb;#2563eb;#2563eb;#93c5fd"/></rect>
<rect x="40.0" y="452" width="576.0" height="16.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="624.0" y="466" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">ガラスごし</text>
<text x="40" y="502" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">ずれの大きさ(×100):</text>
<text x="200" y="506" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0551;0.0553;1.0000" values="1;1;0;0"/></text>
<text x="200" y="506" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">37<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0551;0.0553;0.2764;0.2766;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="506" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">84<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2764;0.2766;0.4977;0.4979;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="506" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">154<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4977;0.4979;0.7190;0.7191;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="506" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d" opacity="0">224<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7190;0.7191;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.9105;0.9106;1.0000" values="0;0;1;1"/><rect x="640" y="480" width="290" height="50" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="656" y="504" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">入射角が大きいほど、横ずれが増える</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光は、空気からガラスへ入ると、曲がる(屈折率が違うため)<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">角度を変えると、曲がり方と、横ずれが変わる<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;0.9275;0.9277;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ゲームでは、ガラスの法線を使って、画面の背景を、ずらして見せる(スクリーン スペース屈折)<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.9275;0.9277;1.0000;1.0000" values="0;0;1;1;0"/></text>
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
