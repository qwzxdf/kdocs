---
title: Shadow Map Basics
tags:
  - 描画
---

# Shadow Map Basics

**シャドウ マップ**は、**「光から見える一番手前の物までの距離」を画像に記録し、画面の点がそれより遠ければ影**と判定する方式です。**原理が簡単で、GPU に向いている**ので、**現代のリアルタイムの影の土台**です。このセクションでは、**原理と手順・光の行列・深度を描くパス・比較と比較サンプラー・エイリアシングと安定化・最小のコード**を、**1 つずつ別のページ**で説明します。

## Principle {#原理}
<svg class="fig illust" viewBox="0 0 780 290" role="img" aria-label="シャドウ マップの原理">
<text x="20" y="24" class="fig-title">光から見た一番手前の深度（シャドウ マップ）と、点の深度を比べる</text>
<circle cx="90" cy="130" r="11" fill="#e5a828"/><text x="70" y="112" style="font-size:12px">光源</text>
<rect x="320" y="90" width="26" height="80" fill="rgba(150,150,150,0.6)" stroke="currentColor" stroke-width="2"/><text x="300" y="82" style="font-size:12px">遮蔽物</text>
<line x1="40" y1="250" x2="740" y2="250" stroke="currentColor" stroke-width="4"/>
<line x1="90" y1="130" x2="320" y2="95" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="90" y1="130" x2="320" y2="165" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="90" y1="130" x2="200" y2="250" stroke="#2ea043" stroke-width="2.5"/>
<circle cx="200" cy="250" r="6" fill="#2ea043"/><text x="150" y="272" style="font-size:12px;fill:#2ea043;font-weight:700">日向（光から一番手前）</text>
<line x1="346" y1="125" x2="470" y2="250" stroke="#e5484d" stroke-width="2.5"/>
<circle cx="470" cy="250" r="6" fill="#e5484d"/><text x="400" y="272" style="font-size:12px;fill:#e5484d;font-weight:700">影（手前に遮蔽物がある）</text>
<text x="500" y="110" style="font-weight:700">シャドウ マップ ＝ 各方向の</text>
<text x="500" y="132" style="font-weight:700">「光から一番手前の面」までの深度</text>
<text x="500" y="164" style="font-size:12px">点の深度 ＞ マップの深度 → 遮られている（影）</text>
<text x="500" y="184" style="font-size:12px">点の深度 ≦ マップの深度 → 光が当たっている</text>
</svg>

## Steps {#手順}
| 手順 | 内容 |
| --- | --- |
| **① 光のビュー・射影行列を作る** | 光の位置・向きから、**ビュー**と**射影**（平行光は正射影） |
| **② シャドウ マップを描く** | 光の視点から、**影を落とす物体**の深度だけを描く（**ピクセルシェーダーなし**） |
| **③ 通常の描画で光の座標に変換** | 各ピクセルの**ワールド位置**を、**光のクリップ空間**へ |
| **④ シャドウ マップを引く** | 変換した <strong>(u, v)</strong> で、保存された深度を読む |
| **⑤ 深度を比べる** | <strong>自分の深度（光から見た）</strong>が、**保存された深度より奥**なら、影 |

## Page List {#ページ一覧}

| ページ | 内容 |
| --- | --- |
| [The Light Matrix](light-matrix.md) | 平行光・スポット・点光源の、ビューと射影 |
| [Rendering Depth](render-depth.md) | 光から見た深度だけのパス・設定 |
| [Comparison Samplers](comparison-sampler.md) | 深度の比較・比較サンプラー（ハードウェア PCF） |
| [Aliasing and Stabilization](aliasing-stabilize.md) | 解像度不足・テクセルの揺れ・スナップ |
| [Minimal Code](minimal-code.md) | 全体の流れを、最小のコードで通す |

## See It in Motion {#動きで見る}

<!-- fig:shadow-map-probe:begin -->

<svg class="fig illust motion" data-fig="shadow-map-probe" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-shadow-map-probe" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">シャドウ マップ: 光から見た「いちばん手前の深度」と比べて、影かどうかを決める</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">断面図。地面 28 マスのそれぞれを、光の側の深度表(シャドウ マップ)と比べる</text>
<rect x="30" y="92" width="500" height="200" fill="#ffffff" stroke="#e5aa28" stroke-width="1.8" rx="6"/>
<text x="30" y="82" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5aa28">① 光から見たシーン(断面)</text>
<line x1="44.0" y1="258.0" x2="520.0" y2="258.0" stroke="#94a3b8" stroke-width="3"/>
<rect x="180.0" y="207.0" width="68.0" height="51.0" fill="#cbd5e1" stroke="#94a3b8" stroke-width="2"/>
<text x="214.0" y="238.2" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#64748b">箱</text>
<line x1="61.0" y1="113.5" x2="182.25" y2="258.0" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="5 5" opacity="0.85"/>
<line x1="122.2" y1="113.5" x2="243.45" y2="258.0" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="5 5" opacity="0.85"/>
<line x1="183.4" y1="113.5" x2="304.65" y2="258.0" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="5 5" opacity="0.85"/>
<line x1="244.6" y1="113.5" x2="365.85" y2="258.0" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="5 5" opacity="0.85"/>
<line x1="305.8" y1="113.5" x2="427.05" y2="258.0" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="5 5" opacity="0.85"/>
<line x1="367.0" y1="113.5" x2="488.25" y2="258.0" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="5 5" opacity="0.85"/>
<line x1="428.2" y1="113.5" x2="549.45" y2="258.0" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="5 5" opacity="0.85"/>
<circle cx="47.4" cy="105.0" r="9" fill="#e5aa28"/>
<text x="61.4" y="109.0" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">光</text>
<rect x="560" y="92" width="370" height="200" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="560" y="82" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">② シャドウ マップ(光から見た深度の表)</text>
<rect x="575.0" y="250.0" width="19.25" height="20.0" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="0;0;1;1"/></rect>
<rect x="596.25" y="242.0" width="19.25" height="28.0" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0517;0.0519;1.0000" values="0;0;1;1"/></rect>
<rect x="617.5" y="234.0" width="19.25" height="36.0" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0611;0.0613;1.0000" values="0;0;1;1"/></rect>
<rect x="638.75" y="226.0" width="19.25" height="44.0" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0705;0.0706;1.0000" values="0;0;1;1"/></rect>
<rect x="660.0" y="218.0" width="19.25" height="52.0" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;1.0000" values="0;0;1;1"/></rect>
<rect x="681.25" y="225.22" width="19.25" height="44.78" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0892;0.0894;1.0000" values="0;0;1;1"/></rect>
<rect x="702.5" y="230.72" width="19.25" height="39.28" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0986;0.0987;1.0000" values="0;0;1;1"/></rect>
<rect x="723.75" y="222.72" width="19.25" height="47.28" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1079;0.1081;1.0000" values="0;0;1;1"/></rect>
<rect x="745.0" y="214.72" width="19.25" height="55.28" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1173;0.1174;1.0000" values="0;0;1;1"/></rect>
<rect x="766.25" y="178.0" width="19.25" height="92.0" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1266;0.1268;1.0000" values="0;0;1;1"/></rect>
<rect x="787.5" y="170.0" width="19.25" height="100.0" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1360;0.1362;1.0000" values="0;0;1;1"/></rect>
<rect x="808.75" y="162.0" width="19.25" height="108.0" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1454;0.1455;1.0000" values="0;0;1;1"/></rect>
<rect x="830.0" y="154.0" width="19.25" height="116.0" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1547;0.1549;1.0000" values="0;0;1;1"/></rect>
<rect x="851.25" y="146.0" width="19.25" height="124.0" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1641;0.1643;1.0000" values="0;0;1;1"/></rect>
<rect x="872.5" y="138.0" width="19.25" height="132.0" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1734;0.1736;1.0000" values="0;0;1;1"/></rect>
<rect x="893.75" y="130.0" width="19.25" height="140.0" fill="#c4b5fd" stroke="#7c3aed" stroke-width="1" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1828;0.1830;1.0000" values="0;0;1;1"/></rect>
<text x="575" y="112" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">各マスに「いちばん近い面までの距離」を 1 つだけ書く</text>
<text x="916" y="284" text-anchor="end" style="font-size:11px;font-weight:500;fill:#64748b">(棒が長い = 遠い)</text>
<text x="575" y="312" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">表への書き込み:</text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">1<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;0.0517;0.0519;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">2<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0517;0.0519;0.0611;0.0613;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">3<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0611;0.0613;0.0705;0.0706;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">4<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0705;0.0706;0.0798;0.0800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">5<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;0.0892;0.0894;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">6<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0892;0.0894;0.0986;0.0987;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">7<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0986;0.0987;0.1079;0.1081;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">8<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1079;0.1081;0.1173;0.1174;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">9<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1173;0.1174;0.1266;0.1268;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">10<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1266;0.1268;0.1360;0.1362;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">11<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1360;0.1362;0.1454;0.1455;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">12<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1454;0.1455;0.1547;0.1549;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">13<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1547;0.1549;0.1641;0.1643;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">14<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1641;0.1643;0.1734;0.1736;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1734;0.1736;0.1828;0.1830;1.0000" values="0;0;1;1;0;0"/></text>
<text x="690" y="314" text-anchor="start" style="font-size:20px;font-weight:700;fill:#7c3aed" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.1828;0.1830;1.0000" values="0;0;1;1"/></text>
<text x="730" y="312" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">マス(深度の最小値だけ残す)</text>
<text x="30" y="340" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">③ 地面の 28 マスを、表と比べる(黄 = 光が当たる / 暗い = 影、赤枠 = 偽の影、青枠 = 欠けた影)</text>
<rect x="134.0" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2434" values="#e5e7eb;#fde68a"/></rect>
<rect x="146.5" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2485" values="#e5e7eb;#475569"/></rect>
<rect x="159.0" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2536" values="#e5e7eb;#fde68a"/></rect>
<rect x="171.5" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2587" values="#e5e7eb;#fde68a"/></rect>
<rect x="184.0" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2638" values="#e5e7eb;#475569"/></rect>
<rect x="196.5" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2689" values="#e5e7eb;#fde68a"/></rect>
<rect x="209.0" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2740" values="#e5e7eb;#475569"/></rect>
<rect x="221.5" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2791" values="#e5e7eb;#fde68a"/></rect>
<rect x="234.0" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2843" values="#e5e7eb;#475569"/></rect>
<rect x="246.5" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2894" values="#e5e7eb;#475569"/></rect>
<rect x="259.0" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2945" values="#e5e7eb;#475569"/></rect>
<rect x="271.5" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.2996" values="#e5e7eb;#475569"/></rect>
<rect x="284.0" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3047" values="#e5e7eb;#475569"/></rect>
<rect x="296.5" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3098" values="#e5e7eb;#475569"/></rect>
<rect x="309.0" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3149" values="#e5e7eb;#475569"/></rect>
<rect x="321.5" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3200" values="#e5e7eb;#fde68a"/></rect>
<rect x="334.0" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3251" values="#e5e7eb;#475569"/></rect>
<rect x="346.5" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3302" values="#e5e7eb;#fde68a"/></rect>
<rect x="359.0" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3353" values="#e5e7eb;#475569"/></rect>
<rect x="371.5" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3404" values="#e5e7eb;#fde68a"/></rect>
<rect x="384.0" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3455" values="#e5e7eb;#fde68a"/></rect>
<rect x="396.5" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3506" values="#e5e7eb;#475569"/></rect>
<rect x="409.0" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3557" values="#e5e7eb;#fde68a"/></rect>
<rect x="421.5" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3609" values="#e5e7eb;#475569"/></rect>
<rect x="434.0" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3660" values="#e5e7eb;#fde68a"/></rect>
<rect x="446.5" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3711" values="#e5e7eb;#fde68a"/></rect>
<rect x="459.0" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3762" values="#e5e7eb;#475569"/></rect>
<rect x="471.5" y="368.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.3813" values="#e5e7eb;#fde68a"/></rect>
<rect x="134.0" y="368" width="350.0" height="12.5" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="30" y="381" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">バイアス 0</text>
<rect x="146.5" y="368.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2483;0.2485;1.0000" values="0;0;1;1"/></rect>
<rect x="184.0" y="368.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2637;0.2638;1.0000" values="0;0;1;1"/></rect>
<rect x="209.0" y="368.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2739;0.2740;1.0000" values="0;0;1;1"/></rect>
<rect x="334.0" y="368.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3249;0.3251;1.0000" values="0;0;1;1"/></rect>
<rect x="359.0" y="368.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3351;0.3353;1.0000" values="0;0;1;1"/></rect>
<rect x="396.5" y="368.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3505;0.3506;1.0000" values="0;0;1;1"/></rect>
<rect x="421.5" y="368.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3607;0.3609;1.0000" values="0;0;1;1"/></rect>
<rect x="459.0" y="368.0" width="12.5" height="12.5" fill="none" stroke="#e5484d" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3760;0.3762;1.0000" values="0;0;1;1"/></rect>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2432;0.2434;1.0000" values="1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2432;0.2434;0.2483;0.2485;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2483;0.2485;0.2534;0.2536;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">3<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2534;0.2536;0.2586;0.2587;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">4<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2586;0.2587;0.2637;0.2638;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">5<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2637;0.2638;0.2688;0.2689;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">6<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2688;0.2689;0.2739;0.2740;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">7<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2739;0.2740;0.2790;0.2791;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">8<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2790;0.2791;0.2841;0.2843;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">9<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2841;0.2843;0.2892;0.2894;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">10<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2892;0.2894;0.2943;0.2945;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">11<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2943;0.2945;0.2994;0.2996;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">12<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2994;0.2996;0.3045;0.3047;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">13<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3045;0.3047;0.3096;0.3098;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">14<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3096;0.3098;0.3147;0.3149;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3147;0.3149;0.3198;0.3200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3198;0.3200;0.3249;0.3251;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">17<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3249;0.3251;0.3300;0.3302;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">18<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3300;0.3302;0.3351;0.3353;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">19<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3351;0.3353;0.3403;0.3404;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">20<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3403;0.3404;0.3454;0.3455;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">21<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3454;0.3455;0.3505;0.3506;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">22<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3505;0.3506;0.3556;0.3557;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">23<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3556;0.3557;0.3607;0.3609;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">24<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3607;0.3609;0.3658;0.3660;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">25<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3658;0.3660;0.3709;0.3711;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">26<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3709;0.3711;0.3760;0.3762;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">27<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3760;0.3762;0.3811;0.3813;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="387" text-anchor="start" style="font-size:17px;font-weight:700;fill:#e5484d" opacity="0">28<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.3811;0.3813;1.0000" values="0;0;1;1"/></text>
<text x="532.0" y="386" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">マス</text>
<rect x="134.0" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4460" values="#e5e7eb;#fde68a"/></rect>
<rect x="146.5" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4511" values="#e5e7eb;#fde68a"/></rect>
<rect x="159.0" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4562" values="#e5e7eb;#fde68a"/></rect>
<rect x="171.5" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4613" values="#e5e7eb;#fde68a"/></rect>
<rect x="184.0" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4664" values="#e5e7eb;#fde68a"/></rect>
<rect x="196.5" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4715" values="#e5e7eb;#fde68a"/></rect>
<rect x="209.0" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4766" values="#e5e7eb;#fde68a"/></rect>
<rect x="221.5" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4817" values="#e5e7eb;#fde68a"/></rect>
<rect x="234.0" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4868" values="#e5e7eb;#475569"/></rect>
<rect x="246.5" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4919" values="#e5e7eb;#475569"/></rect>
<rect x="259.0" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4970" values="#e5e7eb;#475569"/></rect>
<rect x="271.5" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5021" values="#e5e7eb;#475569"/></rect>
<rect x="284.0" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5072" values="#e5e7eb;#475569"/></rect>
<rect x="296.5" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5123" values="#e5e7eb;#475569"/></rect>
<rect x="309.0" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5174" values="#e5e7eb;#475569"/></rect>
<rect x="321.5" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5226" values="#e5e7eb;#fde68a"/></rect>
<rect x="334.0" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5277" values="#e5e7eb;#fde68a"/></rect>
<rect x="346.5" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5328" values="#e5e7eb;#fde68a"/></rect>
<rect x="359.0" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5379" values="#e5e7eb;#fde68a"/></rect>
<rect x="371.5" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5430" values="#e5e7eb;#fde68a"/></rect>
<rect x="384.0" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5481" values="#e5e7eb;#fde68a"/></rect>
<rect x="396.5" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5532" values="#e5e7eb;#fde68a"/></rect>
<rect x="409.0" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5583" values="#e5e7eb;#fde68a"/></rect>
<rect x="421.5" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5634" values="#e5e7eb;#fde68a"/></rect>
<rect x="434.0" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5685" values="#e5e7eb;#fde68a"/></rect>
<rect x="446.5" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5736" values="#e5e7eb;#fde68a"/></rect>
<rect x="459.0" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5787" values="#e5e7eb;#fde68a"/></rect>
<rect x="471.5" y="420.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5838" values="#e5e7eb;#fde68a"/></rect>
<rect x="134.0" y="420" width="350.0" height="12.5" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="30" y="433" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">バイアス 0.8</text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4458;0.4460;1.0000" values="1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">1<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4458;0.4460;0.4509;0.4511;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">2<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4509;0.4511;0.4560;0.4562;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">3<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4560;0.4562;0.4611;0.4613;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">4<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4611;0.4613;0.4662;0.4664;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">5<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4662;0.4664;0.4713;0.4715;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">6<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4713;0.4715;0.4764;0.4766;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">7<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4764;0.4766;0.4815;0.4817;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">8<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4815;0.4817;0.4866;0.4868;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">9<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4866;0.4868;0.4917;0.4919;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">10<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4917;0.4919;0.4969;0.4970;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">11<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4969;0.4970;0.5020;0.5021;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">12<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5020;0.5021;0.5071;0.5072;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">13<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5071;0.5072;0.5122;0.5123;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">14<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5122;0.5123;0.5173;0.5174;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5173;0.5174;0.5224;0.5226;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5224;0.5226;0.5275;0.5277;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">17<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5275;0.5277;0.5326;0.5328;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">18<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5326;0.5328;0.5377;0.5379;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">19<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5377;0.5379;0.5428;0.5430;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">20<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5428;0.5430;0.5479;0.5481;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">21<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5479;0.5481;0.5530;0.5532;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">22<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5530;0.5532;0.5581;0.5583;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">23<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5581;0.5583;0.5632;0.5634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">24<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5632;0.5634;0.5683;0.5685;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">25<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5683;0.5685;0.5734;0.5736;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">26<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5734;0.5736;0.5786;0.5787;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">27<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5786;0.5787;0.5837;0.5838;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="439" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">28<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.5837;0.5838;1.0000" values="0;0;1;1"/></text>
<text x="532.0" y="438" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">マス</text>
<rect x="134.0" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6485" values="#e5e7eb;#fde68a"/></rect>
<rect x="146.5" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6536" values="#e5e7eb;#fde68a"/></rect>
<rect x="159.0" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6587" values="#e5e7eb;#fde68a"/></rect>
<rect x="171.5" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6638" values="#e5e7eb;#fde68a"/></rect>
<rect x="184.0" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6689" values="#e5e7eb;#fde68a"/></rect>
<rect x="196.5" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6740" values="#e5e7eb;#fde68a"/></rect>
<rect x="209.0" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6791" values="#e5e7eb;#fde68a"/></rect>
<rect x="221.5" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6843" values="#e5e7eb;#fde68a"/></rect>
<rect x="234.0" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6894" values="#e5e7eb;#fde68a"/></rect>
<rect x="246.5" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6945" values="#e5e7eb;#475569"/></rect>
<rect x="259.0" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6996" values="#e5e7eb;#475569"/></rect>
<rect x="271.5" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7047" values="#e5e7eb;#475569"/></rect>
<rect x="284.0" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7098" values="#e5e7eb;#475569"/></rect>
<rect x="296.5" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7149" values="#e5e7eb;#475569"/></rect>
<rect x="309.0" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7200" values="#e5e7eb;#475569"/></rect>
<rect x="321.5" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7251" values="#e5e7eb;#fde68a"/></rect>
<rect x="334.0" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7302" values="#e5e7eb;#fde68a"/></rect>
<rect x="346.5" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7353" values="#e5e7eb;#fde68a"/></rect>
<rect x="359.0" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7404" values="#e5e7eb;#fde68a"/></rect>
<rect x="371.5" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7455" values="#e5e7eb;#fde68a"/></rect>
<rect x="384.0" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7506" values="#e5e7eb;#fde68a"/></rect>
<rect x="396.5" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7557" values="#e5e7eb;#fde68a"/></rect>
<rect x="409.0" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7609" values="#e5e7eb;#fde68a"/></rect>
<rect x="421.5" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7660" values="#e5e7eb;#fde68a"/></rect>
<rect x="434.0" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7711" values="#e5e7eb;#fde68a"/></rect>
<rect x="446.5" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7762" values="#e5e7eb;#fde68a"/></rect>
<rect x="459.0" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7813" values="#e5e7eb;#fde68a"/></rect>
<rect x="471.5" y="472.0" width="12.8" height="12.8" fill="#e5e7eb"><animate attributeName="fill" dur="23.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7864" values="#e5e7eb;#fde68a"/></rect>
<rect x="134.0" y="472" width="350.0" height="12.5" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="30" y="485" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">バイアス 1.6</text>
<rect x="234.0" y="472.0" width="12.5" height="12.5" fill="none" stroke="#2563eb" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6892;0.6894;1.0000" values="0;0;1;1"/></rect>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="1">0<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6483;0.6485;1.0000" values="1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">1<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6483;0.6485;0.6534;0.6536;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">2<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6534;0.6536;0.6586;0.6587;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">3<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6586;0.6587;0.6637;0.6638;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">4<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6637;0.6638;0.6688;0.6689;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">5<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6688;0.6689;0.6739;0.6740;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">6<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6739;0.6740;0.6790;0.6791;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">7<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6790;0.6791;0.6841;0.6843;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">8<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6841;0.6843;0.6892;0.6894;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">9<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6892;0.6894;0.6943;0.6945;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">10<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6943;0.6945;0.6994;0.6996;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">11<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6994;0.6996;0.7045;0.7047;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">12<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7045;0.7047;0.7096;0.7098;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">13<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7096;0.7098;0.7147;0.7149;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">14<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7147;0.7149;0.7198;0.7200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">15<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7198;0.7200;0.7249;0.7251;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">16<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7249;0.7251;0.7300;0.7302;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">17<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7300;0.7302;0.7351;0.7353;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">18<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7351;0.7353;0.7403;0.7404;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">19<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7403;0.7404;0.7454;0.7455;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">20<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7454;0.7455;0.7505;0.7506;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">21<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7505;0.7506;0.7556;0.7557;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">22<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7556;0.7557;0.7607;0.7609;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">23<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7607;0.7609;0.7658;0.7660;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">24<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7658;0.7660;0.7709;0.7711;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">25<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7709;0.7711;0.7760;0.7762;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">26<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7760;0.7762;0.7811;0.7813;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">27<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7811;0.7813;0.7862;0.7864;1.0000" values="0;0;1;1;0;0"/></text>
<text x="498.0" y="491" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2563eb" opacity="0">28<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.7862;0.7864;1.0000" values="0;0;1;1"/></text>
<text x="532.0" y="490" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">マス</text>
<g opacity="0"><animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8509;0.8511;1.0000" values="0;0;1;1"/><rect x="610" y="346" width="320" height="134" rx="12" fill="#faf5ff" stroke="#7c3aed" stroke-width="2.5"/>
<text x="626" y="370" text-anchor="start" style="font-size:15px;font-weight:700;fill:#991b1b">バイアス 0: 偽の影 8 マス(縞)</text>
<text x="626" y="394" text-anchor="start" style="font-size:15px;font-weight:700;fill:#166534">バイアス 0.8: 偽の影 0、欠け 0 → 良い</text>
<text x="626" y="418" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1e40af">バイアス 1.6: 影が 1 マス欠ける</text>
<text x="626" y="442" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">小さすぎると縞、大きすぎると影が浮く</text>
</g>
<text x="30" y="524" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光から見て、各方向のいちばん手前の面までの距離だけを覚える<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;1.0000" values="1;1;0;0"/></text>
<text x="30" y="524" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">① 光から見た深度を、表(シャドウ マップ)に書く(マスの中心だけで測る)<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.0424;0.0426;0.2177;0.2179;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="524" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">② 地面の各マスの「光からの距離」を、表と比べる(バイアス 0)<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.2432;0.2434;0.4458;0.4460;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="524" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">③ 比べる前に、少しだけ引く → 縞が消える<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.4458;0.4460;0.6483;0.6485;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="524" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">④ 引きすぎると、本物の影まで欠ける(影が浮く)<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.6483;0.6485;0.8509;0.8511;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="524" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">バイアスは、偽の影が消える最小に近い値にする<animate attributeName="opacity" dur="23.5s" repeatCount="indefinite" keyTimes="0.0000;0.8509;0.8511;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:shadow-map-probe:end -->

## Common Mistakes {#よくあるミス}

??? failure "影が出ない・全面が影になる"
    **深度の向き（比較の向き）・行列の掛け順・ビューポート**を**確認**する。**RenderDoc でシャドウ マップの中身を見る**。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **光から見た深度を撮り、画面の点と比べる**
    - [x] **行列 → 深度パス → 比較**の 3 手順
    - [x] **バイアスとエイリアシング対策が品質の鍵**

## References {#参考}

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## Related Pages {#関連ページ}

- [Shadows](../index.md)
- [Shadow Bias](../bias/index.md)
- [PCF](../pcf.md)
