---
title: Distance Field Shadows
tags:
  - 描画
---

# Distance Field Shadows

**シャドウ マップ**は、**光から見た深度**を描きます。**距離場の影**（Distance Field Shadows）は、**シーンを符号付き距離場（SDF）として持ち**、**画素から光へ向かう**レイを、**距離場の上で進め**て、**遮蔽を調べる**方式です。**距離場**には<strong>「最も近い物までの距離」</strong>が入っているので**レイを安全な距離だけ一気に進められ**（**スフィア トレーシング**）、<strong>「どれだけ、ぎりぎりをかすめたか」</strong>から、**柔らかい半影**を**ほぼ無料で**作れます。**静的なシーン**・**遠景**の影に向きます。

!!! tip "ポイント"
    - <strong>SDF</strong>：空間の各点に<strong>最も近い表面までの距離</strong>を保存（<strong>3D テクスチャ</strong>）。
    - <strong>スフィア トレーシング</strong>：<strong>その距離だけ、安全に進む</strong>。<strong>数ステップ</strong>で遠くまで届く。
    - <strong>半影</strong>：レイが<strong>物の近くを通るほど暗く</strong>なる。<strong>min(k · d / t)</strong> で、<strong>ソフトな影</strong>が<strong>追加コストなし</strong>。
    - <strong>光源の大きさ</strong>を<strong>k</strong> で調整できる。<strong>接触硬化</strong>が自然に出る。
    - <strong>メッシュの SDF を、事前に作る</strong>（<strong>静的</strong>）。<strong>動く物・変形</strong>に弱い。
    - <strong>メモリ・SDF の解像度</strong>が品質を決める。<strong>細い物</strong>が<strong>消える</strong>ことがある。

## What a Signed Distance Field (SDF) Is {#符号付き距離場sdfとは}

**SDF**（Signed Distance Field）は、<strong>空間の各点に、「最も近い表面までの距離」</strong>を入れたものです。**表面の外側は正、内側は負**です。

SDF の値は、点の位置で符号が変わります。表面の外側は正（表面までの最短距離）、表面上は 0、表面の内側は負です。

**メッシュ**からは、<strong>格子（3D テクスチャ）</strong>に、**各点の距離**を**事前計算**して作ります（**ボクセルごとに最も近い三角形までの距離**）。

## Sphere Tracing {#スフィア-トレーシング}

**距離場の最大の利点**は、<strong>「距離」が、「安全に進める量」</strong>だということです。**ある点の距離が d** なら、**半径 d の球の中には、表面がない**ので**どの方向にも、d だけ進んでも表面にぶつかりません**。

<svg class="fig illust" viewBox="0 0 780 270" role="img" aria-label="スフィア トレーシング">
<text x="20" y="24" class="fig-title">各点の「最も近い物までの距離」だけ、安全に進む（スフィア トレーシング）</text>
<path d="M 450 250 Q 480 150 560 130 Q 650 120 720 240 L 720 250 Z" fill="rgba(150,150,150,0.5)" stroke="currentColor" stroke-width="2"/><text x="520" y="200" style="font-size:12px">形</text>
<circle cx="70" cy="220" r="6" fill="currentColor"/><text x="50" y="244" style="font-size:12px">画素</text>
<circle cx="70" cy="220" r="60" fill="none" stroke="currentColor" stroke-dasharray="4 3" opacity="0.5"/>
<circle cx="140" cy="190" r="6" fill="currentColor"/><circle cx="140" cy="190" r="86" fill="none" stroke="currentColor" stroke-dasharray="4 3" opacity="0.5"/>
<circle cx="240" cy="155" r="6" fill="currentColor"/><circle cx="240" cy="155" r="112" fill="none" stroke="currentColor" stroke-dasharray="4 3" opacity="0.5"/>
<circle cx="362" cy="115" r="6" fill="currentColor"/><circle cx="362" cy="115" r="60" fill="none" stroke="currentColor" stroke-dasharray="4 3" opacity="0.5"/>
<line x1="70" y1="220" x2="700" y2="40" stroke="currentColor" stroke-width="2"/><text x="640" y="32" style="font-size:12px">光へ</text>
<text x="40" y="270" style="font-size:12px">ステップごとに、距離（点線の円の半径）だけ進む。表面に近づくほど、ステップが小さくなる</text>
</svg>

レイの進め方は、<strong>球トレーシング</strong>です。ステップの大きさは、その点の SDF の値にします。SDF がほぼ 0 になれば、表面に当たったので影です。光に十分近づくか、最大距離に達すれば日向です。ステップ数は、開けた空間では少なく（大きく進める）、物の近くでは増えます。

```hlsl
float SphereTraceShadow(float3 origin, float3 light_dir) {
  float t = kStartOffset;
  [loop] for (int i = 0; i < kMaxSteps; ++i) {
    float3 p = origin + light_dir * t;
    float d = SampleSDF(p);
    if (d < kHitEpsilon) return 0.0;
    t += d;
    if (t > kMaxDistance) break;
  }
  return 1.0;
}
```

<!-- fig:sdf-soft-shadow:begin -->

<svg class="fig illust motion" data-fig="sdf-soft-shadow" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-sdf-soft-shadow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">SDF の柔らかい影: 光に向かう途中で、物にどれだけ「かすったか」で、影の濃さを決める</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">円の物。床の各点から光へ、距離場を使って進む。min(k·距離 ÷ 進んだ長さ)が小さいほど、影が濃い</text>
<rect x="30" y="96" width="900" height="330" fill="#ffffff" stroke="#e5aa28" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">① 光・円の物・床</text>
<line x1="60.0" y1="398.0" x2="900.0" y2="398.0" stroke="#94a3b8" stroke-width="3"/>
<circle cx="480.0" cy="302.0" r="36.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="2"/>
<circle cx="210.0" cy="128.0" r="11" fill="#e5aa28"/>
<text x="226.0" y="132.0" text-anchor="start" style="font-size:13px;font-weight:700;fill:#92400e">光(点)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3287;0.3289;1.0000" values="1;1;0;0"/><circle cx="612.5" cy="395.74" r="126.31" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="612.5" cy="395.74" r="3" fill="#2563eb"/>
<circle cx="507.34" cy="325.78" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="507.34" cy="325.78" r="3" fill="#2563eb"/>
<circle cx="506.34" cy="325.12" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="506.34" cy="325.12" r="3" fill="#2563eb"/>
<circle cx="505.34" cy="324.45" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="505.34" cy="324.45" r="3" fill="#2563eb"/>
<circle cx="504.34" cy="323.79" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="504.34" cy="323.79" r="3" fill="#2563eb"/>
<circle cx="503.34" cy="323.13" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="503.34" cy="323.13" r="3" fill="#2563eb"/>
<circle cx="502.34" cy="322.46" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="502.34" cy="322.46" r="3" fill="#2563eb"/>
<circle cx="501.34" cy="321.8" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="501.34" cy="321.8" r="3" fill="#2563eb"/>
<circle cx="500.34" cy="321.13" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="500.34" cy="321.13" r="3" fill="#2563eb"/>
<circle cx="499.34" cy="320.47" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="499.34" cy="320.47" r="3" fill="#2563eb"/>
<circle cx="498.34" cy="319.8" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="498.34" cy="319.8" r="3" fill="#2563eb"/>
<circle cx="497.34" cy="319.14" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="497.34" cy="319.14" r="3" fill="#2563eb"/>
<circle cx="615.0" cy="397.4" r="6" fill="#1f2937"/>
<text x="40" y="112" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed">k = 4</text>
<rect x="60.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0711" values="#e5e7eb;#fde68a"/></rect>
<rect x="75.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0738" values="#e5e7eb;#fde68a"/></rect>
<rect x="90.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0764" values="#e5e7eb;#fde68a"/></rect>
<rect x="105.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0791" values="#e5e7eb;#fde68a"/></rect>
<rect x="120.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0818" values="#e5e7eb;#fde68a"/></rect>
<rect x="135.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0844" values="#e5e7eb;#fde68a"/></rect>
<rect x="150.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0871" values="#e5e7eb;#fde68a"/></rect>
<rect x="165.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0898" values="#e5e7eb;#fde68a"/></rect>
<rect x="180.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0924" values="#e5e7eb;#fde68a"/></rect>
<rect x="195.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0951" values="#e5e7eb;#fde68a"/></rect>
<rect x="210.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0978" values="#e5e7eb;#fde68a"/></rect>
<rect x="225.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1004" values="#e5e7eb;#fde68a"/></rect>
<rect x="240.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1031" values="#e5e7eb;#fde68a"/></rect>
<rect x="255.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1058" values="#e5e7eb;#fde68a"/></rect>
<rect x="270.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1084" values="#e5e7eb;#fde68a"/></rect>
<rect x="285.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1111" values="#e5e7eb;#fde68a"/></rect>
<rect x="300.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1138" values="#e5e7eb;#fde68a"/></rect>
<rect x="315.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1164" values="#e5e7eb;#fde68a"/></rect>
<rect x="330.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1191" values="#e5e7eb;#fde68a"/></rect>
<rect x="345.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1218" values="#e5e7eb;#fde68a"/></rect>
<rect x="360.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1244" values="#e5e7eb;#fde68a"/></rect>
<rect x="375.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1271" values="#e5e7eb;#fde68a"/></rect>
<rect x="390.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1298" values="#e5e7eb;#fde68a"/></rect>
<rect x="405.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1324" values="#e5e7eb;#fde68a"/></rect>
<rect x="420.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1351" values="#e5e7eb;#fde68a"/></rect>
<rect x="435.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1378" values="#e5e7eb;#fde68a"/></rect>
<rect x="450.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1404" values="#e5e7eb;#fde68a"/></rect>
<rect x="465.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1431" values="#e5e7eb;#fde68a"/></rect>
<rect x="480.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1458" values="#e5e7eb;#fde68a"/></rect>
<rect x="495.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1484" values="#e5e7eb;#e9d685"/></rect>
<rect x="510.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1511" values="#e5e7eb;#928f6e"/></rect>
<rect x="525.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1538" values="#e5e7eb;#4f585c"/></rect>
<rect x="540.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1564" values="#e5e7eb;#334155"/></rect>
<rect x="555.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1591" values="#e5e7eb;#334155"/></rect>
<rect x="570.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1618" values="#e5e7eb;#334155"/></rect>
<rect x="585.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1644" values="#e5e7eb;#334155"/></rect>
<rect x="600.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1671" values="#e5e7eb;#334155"/></rect>
<rect x="615.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1698" values="#e5e7eb;#334155"/></rect>
<rect x="630.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1724" values="#e5e7eb;#334155"/></rect>
<rect x="645.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1751" values="#e5e7eb;#334155"/></rect>
<rect x="660.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1778" values="#e5e7eb;#334155"/></rect>
<rect x="675.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1804" values="#e5e7eb;#334155"/></rect>
<rect x="690.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1831" values="#e5e7eb;#334155"/></rect>
<rect x="705.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1858" values="#e5e7eb;#334155"/></rect>
<rect x="720.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1884" values="#e5e7eb;#334155"/></rect>
<rect x="735.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1911" values="#e5e7eb;#334155"/></rect>
<rect x="750.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1938" values="#e5e7eb;#364356"/></rect>
<rect x="765.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1964" values="#e5e7eb;#3e4a58"/></rect>
<rect x="780.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1991" values="#e5e7eb;#46515a"/></rect>
<rect x="795.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2018" values="#e5e7eb;#4d565c"/></rect>
<rect x="810.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2044" values="#e5e7eb;#535b5d"/></rect>
<rect x="825.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2071" values="#e5e7eb;#59605f"/></rect>
<rect x="840.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2098" values="#e5e7eb;#5d6360"/></rect>
<rect x="855.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2124" values="#e5e7eb;#606661"/></rect>
<rect x="870.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2151" values="#e5e7eb;#646962"/></rect>
<rect x="885.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2178" values="#e5e7eb;#666b62"/></rect>
<rect x="60.0" y="440" width="840.0" height="15.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="436" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">床の明るさ(黄 = 光が届く、暗い = 影)</text>
<text x="60" y="480" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">k = 4: 影の縁のぼけ幅 6.0、1 点あたりの歩数 平均 5.0</text>
<text x="60" y="504" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">k が小さい: 広くぼける(柔らかい影)</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3287;0.3289;0.6132;0.6133;1.0000" values="0;0;1;1;0;0"/><circle cx="612.5" cy="395.74" r="126.31" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="612.5" cy="395.74" r="3" fill="#2563eb"/>
<circle cx="507.34" cy="325.78" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="507.34" cy="325.78" r="3" fill="#2563eb"/>
<circle cx="506.34" cy="325.12" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="506.34" cy="325.12" r="3" fill="#2563eb"/>
<circle cx="505.34" cy="324.45" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="505.34" cy="324.45" r="3" fill="#2563eb"/>
<circle cx="504.34" cy="323.79" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="504.34" cy="323.79" r="3" fill="#2563eb"/>
<circle cx="503.34" cy="323.13" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="503.34" cy="323.13" r="3" fill="#2563eb"/>
<circle cx="502.34" cy="322.46" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="502.34" cy="322.46" r="3" fill="#2563eb"/>
<circle cx="501.34" cy="321.8" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="501.34" cy="321.8" r="3" fill="#2563eb"/>
<circle cx="500.34" cy="321.13" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="500.34" cy="321.13" r="3" fill="#2563eb"/>
<circle cx="499.34" cy="320.47" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="499.34" cy="320.47" r="3" fill="#2563eb"/>
<circle cx="498.34" cy="319.8" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="498.34" cy="319.8" r="3" fill="#2563eb"/>
<circle cx="497.34" cy="319.14" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="497.34" cy="319.14" r="3" fill="#2563eb"/>
<circle cx="615.0" cy="397.4" r="6" fill="#1f2937"/>
<text x="40" y="112" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed">k = 12</text>
<rect x="60.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3556" values="#e5e7eb;#fde68a"/></rect>
<rect x="75.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3582" values="#e5e7eb;#fde68a"/></rect>
<rect x="90.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3609" values="#e5e7eb;#fde68a"/></rect>
<rect x="105.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3636" values="#e5e7eb;#fde68a"/></rect>
<rect x="120.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3662" values="#e5e7eb;#fde68a"/></rect>
<rect x="135.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3689" values="#e5e7eb;#fde68a"/></rect>
<rect x="150.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3716" values="#e5e7eb;#fde68a"/></rect>
<rect x="165.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3742" values="#e5e7eb;#fde68a"/></rect>
<rect x="180.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3769" values="#e5e7eb;#fde68a"/></rect>
<rect x="195.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3796" values="#e5e7eb;#fde68a"/></rect>
<rect x="210.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3822" values="#e5e7eb;#fde68a"/></rect>
<rect x="225.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3849" values="#e5e7eb;#fde68a"/></rect>
<rect x="240.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3876" values="#e5e7eb;#fde68a"/></rect>
<rect x="255.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3902" values="#e5e7eb;#fde68a"/></rect>
<rect x="270.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3929" values="#e5e7eb;#fde68a"/></rect>
<rect x="285.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3956" values="#e5e7eb;#fde68a"/></rect>
<rect x="300.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3982" values="#e5e7eb;#fde68a"/></rect>
<rect x="315.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4009" values="#e5e7eb;#fde68a"/></rect>
<rect x="330.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4036" values="#e5e7eb;#fde68a"/></rect>
<rect x="345.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4062" values="#e5e7eb;#fde68a"/></rect>
<rect x="360.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4089" values="#e5e7eb;#fde68a"/></rect>
<rect x="375.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4116" values="#e5e7eb;#fde68a"/></rect>
<rect x="390.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4142" values="#e5e7eb;#fde68a"/></rect>
<rect x="405.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4169" values="#e5e7eb;#fde68a"/></rect>
<rect x="420.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4196" values="#e5e7eb;#fde68a"/></rect>
<rect x="435.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4222" values="#e5e7eb;#fde68a"/></rect>
<rect x="450.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4249" values="#e5e7eb;#fde68a"/></rect>
<rect x="465.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4276" values="#e5e7eb;#fde68a"/></rect>
<rect x="480.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#e5e7eb;#fde68a"/></rect>
<rect x="495.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329" values="#e5e7eb;#fde68a"/></rect>
<rect x="510.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4356" values="#e5e7eb;#fde68a"/></rect>
<rect x="525.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4382" values="#e5e7eb;#88866b"/></rect>
<rect x="540.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4409" values="#e5e7eb;#334155"/></rect>
<rect x="555.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4436" values="#e5e7eb;#334155"/></rect>
<rect x="570.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462" values="#e5e7eb;#334155"/></rect>
<rect x="585.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4489" values="#e5e7eb;#334155"/></rect>
<rect x="600.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4516" values="#e5e7eb;#334155"/></rect>
<rect x="615.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4542" values="#e5e7eb;#334155"/></rect>
<rect x="630.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4569" values="#e5e7eb;#334155"/></rect>
<rect x="645.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4596" values="#e5e7eb;#334155"/></rect>
<rect x="660.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#334155"/></rect>
<rect x="675.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4649" values="#e5e7eb;#334155"/></rect>
<rect x="690.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4676" values="#e5e7eb;#334155"/></rect>
<rect x="705.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#e5e7eb;#334155"/></rect>
<rect x="720.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4729" values="#e5e7eb;#334155"/></rect>
<rect x="735.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4756" values="#e5e7eb;#334155"/></rect>
<rect x="750.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4782" values="#e5e7eb;#3b4757"/></rect>
<rect x="765.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4809" values="#e5e7eb;#555d5e"/></rect>
<rect x="780.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4836" values="#e5e7eb;#6d7064"/></rect>
<rect x="795.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4862" values="#e5e7eb;#808069"/></rect>
<rect x="810.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4889" values="#e5e7eb;#938f6e"/></rect>
<rect x="825.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4916" values="#e5e7eb;#a59e73"/></rect>
<rect x="840.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4942" values="#e5e7eb;#b1a876"/></rect>
<rect x="855.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4969" values="#e5e7eb;#bbb079"/></rect>
<rect x="870.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4996" values="#e5e7eb;#c5b87b"/></rect>
<rect x="885.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5022" values="#e5e7eb;#cdbf7d"/></rect>
<rect x="60.0" y="440" width="840.0" height="15.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="436" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">床の明るさ(黄 = 光が届く、暗い = 影)</text>
<text x="60" y="480" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">k = 12: 影の縁のぼけ幅 5.0、1 点あたりの歩数 平均 5.0</text>
<text x="60" y="504" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">k が中くらい: ほどよい</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6132;0.6133;1.0000" values="0;0;1;1"/><circle cx="612.5" cy="395.74" r="126.31" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="612.5" cy="395.74" r="3" fill="#2563eb"/>
<circle cx="507.34" cy="325.78" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="507.34" cy="325.78" r="3" fill="#2563eb"/>
<circle cx="506.34" cy="325.12" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="506.34" cy="325.12" r="3" fill="#2563eb"/>
<circle cx="505.34" cy="324.45" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="505.34" cy="324.45" r="3" fill="#2563eb"/>
<circle cx="504.34" cy="323.79" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="504.34" cy="323.79" r="3" fill="#2563eb"/>
<circle cx="503.34" cy="323.13" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="503.34" cy="323.13" r="3" fill="#2563eb"/>
<circle cx="502.34" cy="322.46" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="502.34" cy="322.46" r="3" fill="#2563eb"/>
<circle cx="501.34" cy="321.8" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="501.34" cy="321.8" r="3" fill="#2563eb"/>
<circle cx="500.34" cy="321.13" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="500.34" cy="321.13" r="3" fill="#2563eb"/>
<circle cx="499.34" cy="320.47" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="499.34" cy="320.47" r="3" fill="#2563eb"/>
<circle cx="498.34" cy="319.8" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="498.34" cy="319.8" r="3" fill="#2563eb"/>
<circle cx="497.34" cy="319.14" r="0.6" fill="none" stroke="#60a5fa" stroke-width="1.2" opacity="0.8"/>
<circle cx="497.34" cy="319.14" r="3" fill="#2563eb"/>
<circle cx="615.0" cy="397.4" r="6" fill="#1f2937"/>
<text x="40" y="112" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed">k = 64</text>
<rect x="60.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6400" values="#e5e7eb;#fde68a"/></rect>
<rect x="75.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6427" values="#e5e7eb;#fde68a"/></rect>
<rect x="90.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6453" values="#e5e7eb;#fde68a"/></rect>
<rect x="105.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6480" values="#e5e7eb;#fde68a"/></rect>
<rect x="120.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6507" values="#e5e7eb;#fde68a"/></rect>
<rect x="135.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6533" values="#e5e7eb;#fde68a"/></rect>
<rect x="150.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6560" values="#e5e7eb;#fde68a"/></rect>
<rect x="165.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6587" values="#e5e7eb;#fde68a"/></rect>
<rect x="180.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6613" values="#e5e7eb;#fde68a"/></rect>
<rect x="195.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6640" values="#e5e7eb;#fde68a"/></rect>
<rect x="210.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6667" values="#e5e7eb;#fde68a"/></rect>
<rect x="225.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6693" values="#e5e7eb;#fde68a"/></rect>
<rect x="240.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6720" values="#e5e7eb;#fde68a"/></rect>
<rect x="255.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6747" values="#e5e7eb;#fde68a"/></rect>
<rect x="270.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6773" values="#e5e7eb;#fde68a"/></rect>
<rect x="285.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6800" values="#e5e7eb;#fde68a"/></rect>
<rect x="300.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6827" values="#e5e7eb;#fde68a"/></rect>
<rect x="315.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6853" values="#e5e7eb;#fde68a"/></rect>
<rect x="330.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6880" values="#e5e7eb;#fde68a"/></rect>
<rect x="345.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6907" values="#e5e7eb;#fde68a"/></rect>
<rect x="360.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6933" values="#e5e7eb;#fde68a"/></rect>
<rect x="375.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6960" values="#e5e7eb;#fde68a"/></rect>
<rect x="390.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6987" values="#e5e7eb;#fde68a"/></rect>
<rect x="405.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7013" values="#e5e7eb;#fde68a"/></rect>
<rect x="420.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7040" values="#e5e7eb;#fde68a"/></rect>
<rect x="435.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7067" values="#e5e7eb;#fde68a"/></rect>
<rect x="450.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7093" values="#e5e7eb;#fde68a"/></rect>
<rect x="465.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7120" values="#e5e7eb;#fde68a"/></rect>
<rect x="480.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7147" values="#e5e7eb;#fde68a"/></rect>
<rect x="495.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7173" values="#e5e7eb;#fde68a"/></rect>
<rect x="510.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7200" values="#e5e7eb;#fde68a"/></rect>
<rect x="525.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7227" values="#e5e7eb;#fde68a"/></rect>
<rect x="540.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7253" values="#e5e7eb;#334155"/></rect>
<rect x="555.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7280" values="#e5e7eb;#334155"/></rect>
<rect x="570.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7307" values="#e5e7eb;#334155"/></rect>
<rect x="585.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7333" values="#e5e7eb;#334155"/></rect>
<rect x="600.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7360" values="#e5e7eb;#334155"/></rect>
<rect x="615.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7387" values="#e5e7eb;#334155"/></rect>
<rect x="630.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7413" values="#e5e7eb;#334155"/></rect>
<rect x="645.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7440" values="#e5e7eb;#334155"/></rect>
<rect x="660.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7467" values="#e5e7eb;#334155"/></rect>
<rect x="675.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7493" values="#e5e7eb;#334155"/></rect>
<rect x="690.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7520" values="#e5e7eb;#334155"/></rect>
<rect x="705.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7547" values="#e5e7eb;#334155"/></rect>
<rect x="720.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7573" values="#e5e7eb;#334155"/></rect>
<rect x="735.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7600" values="#e5e7eb;#334155"/></rect>
<rect x="750.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7627" values="#e5e7eb;#5c6260"/></rect>
<rect x="765.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7653" values="#e5e7eb;#e9d685"/></rect>
<rect x="780.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7680" values="#e5e7eb;#fde68a"/></rect>
<rect x="795.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7707" values="#e5e7eb;#fde68a"/></rect>
<rect x="810.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7733" values="#e5e7eb;#fde68a"/></rect>
<rect x="825.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7760" values="#e5e7eb;#fde68a"/></rect>
<rect x="840.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7787" values="#e5e7eb;#fde68a"/></rect>
<rect x="855.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7813" values="#e5e7eb;#fde68a"/></rect>
<rect x="870.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7840" values="#e5e7eb;#fde68a"/></rect>
<rect x="885.0" y="440.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7867" values="#e5e7eb;#fde68a"/></rect>
<rect x="60.0" y="440" width="840.0" height="15.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="60" y="436" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">床の明るさ(黄 = 光が届く、暗い = 影)</text>
<text x="60" y="480" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">k = 64: 影の縁のぼけ幅 1.0、1 点あたりの歩数 平均 5.0</text>
<text x="60" y="504" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">k が大きい: くっきり(ほぼ硬い影)</text>
</g>
<text x="560" y="112" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">1 点あたりの歩数(平均):</text>
<text x="740" y="116" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0620;0.0622;1.0000" values="1;1;0;0"/></text>
<text x="740" y="116" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">5<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0620;0.0622;0.3465;0.3467;1.0000" values="0;0;1;1;0;0"/></text>
<text x="740" y="116" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">5<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3465;0.3467;0.6309;0.6311;1.0000" values="0;0;1;1;0;0"/></text>
<text x="740" y="116" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2563eb" opacity="0">5<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6309;0.6311;1.0000" values="0;0;1;1"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">距離場(SDF)= 各点から、物までの一番近い距離<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0443;0.0444;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光に向かって進みながら、k × 距離 ÷ 進んだ長さ の最小値を記録する<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0443;0.0444;0.8976;0.8978;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">かすった度合いが、そのまま、影の濃さになる。k で、ぼけ具合を調整する<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8976;0.8978;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:sdf-soft-shadow:end -->

## How Soft Shadows Work {#ソフト-シャドウの仕組み}

**スフィア トレーシングの途中**で、**レイがどれだけ物に近づいたか**を、記録します。**ぎりぎりをかすめたレイ**は、**半影の領域**にあります。

<div class="formula">shadow = min over t of ( k · d(t) / t )　（0〜1 にクランプ）</div>

| 項 | 意味 |
| --- | --- |
| <strong>d(t)</strong> | レイ上の位置 t での、SDF の値（**物までの距離**） |
| **d / t** | **距離 ÷ 進んだ距離**＝**円錐の開き角（のタンジェント）に相当** |
| **k** | **影の鋭さ**（光源の大きさの逆数）。**大きいほど鋭い** |
| **min** | **最も物に近づいた所**が**影の濃さを決める** |


この式は Quilez が広めた方法で、レイを進めながら「物にどれだけ近づいたか」を記録するだけで、追加コストなしに半影が得られます。

この式は Quilez が広めた方法で、レイを進めながら「物にどれだけ近づいたか」を記録するだけで、追加コストなしに半影が得られます。

```hlsl
float SoftSphereTraceShadow(float3 origin, float3 light_dir, float k) {
  float shadow = 1.0;
  float t = kStartOffset;
  [loop] for (int i = 0; i < kMaxSteps; ++i) {
    float d = SampleSDF(origin + light_dir * t);
    if (d < kHitEpsilon) return 0.0;
    shadow = min(shadow, k * d / t);
    t += d;
    if (t > kMaxDistance) break;
  }
  return saturate(shadow);
}
```

**物に近づくほど `d` が小さく**、**遠くの物（`t` が大きい）ほど、`d / t` がさらに小さく**なります。**接触部（`t` が小さい）は鋭く**、**遠くの遮蔽物は、ぼける**ので**接触硬化**が自然に出ます（[PCSS](pcss.md)と同じ性質）。

### Improvement: Smooth Penumbra {#改良滑らかな半影}

単純な `min(k · d / t)` は、**半影に縞**（段差）が出ることがあります。**1 つ前のステップの `d` との差**から、**より正確な距離**（「最も近づいた点」）を**補間して求める**改良（**Inigo Quilez の improved soft shadows**）があります。

## Distance Fields from Meshes {#メッシュからの距離場}

SDF の作り方は 3 通りです。<strong>メッシュ SDF（オブジェクトごと）</strong>は、各メッシュの SDF を事前計算し、3D テクスチャに保存します。配置された物体ごとに、ワールド空間から物体のローカル空間へ変換して引きます（Unreal Engine の Distance Field Shadows）。<strong>グローバル SDF</strong>は、オブジェクトの SDF を、視点の周りの大きな 1 つの SDF に合成します。1 回のサンプルでシーン全体の距離が得られ、カスケードで遠くを粗くします。<strong>解析 SDF</strong>は、球・箱・カプセルのように、式で距離が出る形で、キャラクターの影（カプセル シャドウ）などに使います。

### Capsule Shadows {#カプセル-シャドウ}

**キャラクターの骨**に<strong>カプセル（線分 ＋ 半径）</strong>を割り当て、**カプセルの SDF の式**で、**ソフトな影**を作ります。**変形するキャラクター**にも、**安い近似の影**が作れます（**シャドウ マップと併用**）。

## Pros and Cons {#長所と短所}

| 長所 | 短所 |
| --- | --- |
| **ソフトな影**が**追加コストなし**（接触硬化も自然） | **静的なシーン**向き（SDF の事前計算が要る） |
| **レイのステップが少ない**（距離だけ進む） | **メモリ**（3D テクスチャ）。**SDF の解像度**で品質が決まる |
| **シャドウ マップのアクネ・解像度の問題がない** | **細い物・薄い物が、SDF で消える** |
| **遠景の影に低コスト** | **動く物・変形する物**は**別の手段**が必要 |
| **光源サイズの調整が直感的** | **半影の近似**が**物理的に正確ではない** |

## Where to Use It {#使いどころ}

| 状況 | 使い方 |
| --- | --- |
| **遠景の大きな影** | **カスケードの遠い範囲を距離場の影で**（シャドウ マップは、近くだけ） |
| **静的なシーン** | **柔らかい太陽の影**を全域で |
| **キャラクター** | **カプセル シャドウ**で柔らかい接地影 |
| <strong>間接的な、空の遮蔽（距離場 AO）</strong> | **同じ SDF を、AO にも使う**（[AO の手法](../ao/world-space/index.md)） |

## Common Mistakes {#よくあるミス}

??? failure "SDF の解像度が粗く、細い物（柵・葉）の影が消える"
    **解像度を上げる**・**細い物は別扱い**（シャドウ マップ）にします。

??? failure "レイの開始位置が表面にあり、自己遮蔽で真っ暗"
    **開始位置を法線方向に少しずらす**（`kStartOffset`）。

??? failure "動く物体を、静的な SDF に入れて、影が遅れる・出ない"
    **動く物はシャドウ マップ・カプセル**で補います。

??? failure "`min(k · d / t)` で、半影に縞が出る"
    **改良版**（補間による距離の補正）を使います。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] <strong>SDF</strong> ＝ <strong>各点に、最も近い表面までの距離</strong>を保存した 3D テクスチャ
    - [x] <strong>スフィア トレーシング</strong>：<strong>距離だけ安全に進む</strong>。<strong>少ないステップで遠くまで</strong>
    - [x] <strong>半影</strong> ＝ <strong>min(k · d / t)</strong>。<strong>接触硬化が自然に出る</strong>（追加コストなし）
    - [x] <strong>静的なシーン・遠景・カプセル影</strong>に向く。<strong>動く物・細い物</strong>は苦手
    - [x] <strong>シャドウ マップと併用</strong>が、実用的

## References {#参考}

- Quilez, "soft shadows in raymarched SDFs"（iquilezles.org）
- Epic Games, "Distance Field Shadows"（Unreal Engine ドキュメント）
- Hart, "Sphere Tracing: A Geometric Method for the Antialiased Ray Tracing of Implicit Surfaces"（1996）

## Related Pages {#関連ページ}

- [Shadows](index.md)
- [PCSS](pcss.md)
- [Cascaded Shadow Maps (CSM)](cascaded.md)
- [AO のその他の手法（距離場 AO）](../ao/world-space/index.md)
