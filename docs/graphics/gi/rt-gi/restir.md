---
title: ReSTIR GI
tags:
  - 描画
---

# ReSTIR GI

**ReSTIR は、「良いサンプルを、隣の画素や前フレームから借りる」ことで、少ないレイでも、きれいな結果を出す手法**です。**重みつきリザーバー サンプリング**を使い、**サンプルを再利用**します。このページでは、**ReSTIR の考え方と効果**を説明します。

!!! tip "ポイント"
    - **リザーバーに、「良さそうなサンプル」を 1 つだけ保持**する。
    - **隣の画素・前フレームのリザーバーと混ぜる（再利用）**。
    - **再利用すると、実質のサンプル数が、桁違いに増える**。
    - **バイアスの管理（再利用してよいかの判定）が難しい**。

<!-- fig:restir-reservoir:begin -->

<svg class="fig illust motion" data-fig="restir-reservoir" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-restir-reservoir" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">リザーバー:候補を流して見ながら、良さそうな 1 つだけ覚える</text>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0825;0.0828;1.0000" values="0;0;1;1"/><rect x="60" y="130" width="62" height="24.0" fill="#94a3b8" stroke="#1f2937" stroke-width="1.5"/>
<text x="91" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 A</text>
<text x="91" y="172.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 0.1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1652;0.1655;1.0000" values="0;0;1;1"/><rect x="140" y="130" width="62" height="32.0" fill="#60a5fa" stroke="#1f2937" stroke-width="1.5"/>
<text x="171" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 B</text>
<text x="171" y="180.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 0.3</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2480;0.2483;1.0000" values="0;0;1;1"/><rect x="220" y="130" width="62" height="116.0" fill="#e5484d" stroke="#1f2937" stroke-width="1.5"/>
<text x="251" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 C</text>
<text x="251" y="264.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 2.4</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3308;0.3310;1.0000" values="0;0;1;1"/><rect x="300" y="130" width="62" height="28.0" fill="#94a3b8" stroke="#1f2937" stroke-width="1.5"/>
<text x="331" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 D</text>
<text x="331" y="176.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 0.2</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4135;0.4138;1.0000" values="0;0;1;1"/><rect x="380" y="130" width="62" height="40.0" fill="#fbbf24" stroke="#1f2937" stroke-width="1.5"/>
<text x="411" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 E</text>
<text x="411" y="188.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 0.5</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4963;0.4966;1.0000" values="0;0;1;1"/><rect x="460" y="130" width="62" height="64.0" fill="#2ea043" stroke="#1f2937" stroke-width="1.5"/>
<text x="491" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 F</text>
<text x="491" y="212.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 1.1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5790;0.5793;1.0000" values="0;0;1;1"/><rect x="540" y="130" width="62" height="26.0" fill="#94a3b8" stroke="#1f2937" stroke-width="1.5"/>
<text x="571" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 G</text>
<text x="571" y="174.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 0.1</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6618;0.6621;1.0000" values="0;0;1;1"/><rect x="620" y="130" width="62" height="36.0" fill="#a78bfa" stroke="#1f2937" stroke-width="1.5"/>
<text x="651" y="122" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#1f2937">候補 H</text>
<text x="651" y="184.0" text-anchor="middle" style="font-size:11px;font-weight:700;fill:#64748b">明るさ 0.4</text>
</g>
<rect x="60" y="290" width="200" height="70" fill="#ffffff" stroke="#1f2937" stroke-width="2.5" rx="6"/>
<text x="160" y="282" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">リザーバー（1 つだけ保持）</text>
<rect x="70" y="300" width="60" height="50" fill="#e2e8f0"><animate attributeName="fill" dur="14.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.1172;0.2000;0.2828;0.3655;0.4483;0.5310;0.6138;0.6966" values="#e2e8f0;#94a3b8;#60a5fa;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d;#e5484d"/></rect>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 A<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1170;0.1172;0.1997;0.2000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 B<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1997;0.2000;0.2825;0.2828;1.0000" values="0;0;1;1;0;0"/></text>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 C<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2825;0.2828;0.3652;0.3655;1.0000" values="0;0;1;1;0;0"/></text>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 C<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3652;0.3655;0.4480;0.4483;1.0000" values="0;0;1;1;0;0"/></text>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 C<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4480;0.4483;0.5308;0.5310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 C<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5308;0.5310;0.6135;0.6138;1.0000" values="0;0;1;1;0;0"/></text>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 C<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6135;0.6138;0.6963;0.6966;1.0000" values="0;0;1;1;0;0"/></text>
<text x="140" y="335" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">= 候補 C<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6963;0.6966;0.7790;0.7793;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 A 到着:採用の確率 = 0.1 / (累計 0.1) = 100 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0825;0.0828;0.1652;0.1655;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 B 到着:採用の確率 = 0.3 / (累計 0.4) = 75 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1652;0.1655;0.2480;0.2483;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 C 到着:採用の確率 = 2.4 / (累計 2.8) = 86 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2480;0.2483;0.3308;0.3310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 D 到着:採用の確率 = 0.2 / (累計 3.0) = 7 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3308;0.3310;0.4135;0.4138;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 E 到着:採用の確率 = 0.5 / (累計 3.5) = 14 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4135;0.4138;0.4963;0.4966;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 F 到着:採用の確率 = 1.1 / (累計 4.6) = 24 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4963;0.4966;0.5790;0.5793;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 G 到着:採用の確率 = 0.1 / (累計 4.8) = 3 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5790;0.5793;0.6618;0.6621;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="300" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">候補 H 到着:採用の確率 = 0.4 / (累計 5.2) = 8 %<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6618;0.6621;0.7446;0.7448;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 採用! リザーバーを入れ替える<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0825;0.0828;0.1652;0.1655;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 採用! リザーバーを入れ替える<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1652;0.1655;0.2480;0.2483;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 採用! リザーバーを入れ替える<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2480;0.2483;0.3308;0.3310;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 不採用（今のまま）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3308;0.3310;0.4135;0.4138;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 不採用（今のまま）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4135;0.4138;0.4963;0.4966;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 不採用（今のまま）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4963;0.4966;0.5790;0.5793;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 不採用（今のまま）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5790;0.5793;0.6618;0.6621;1.0000" values="0;0;1;1;0;0"/></text>
<text x="300" y="328" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043" opacity="0">サイコロ → 不採用（今のまま）<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6618;0.6621;0.7446;0.7448;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">最後に残った 1 つが、重みに比例して選ばれた「良い」サンプル。全部を覚えなくても、1 つだけで済む。<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.7790;0.7793;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="70" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">候補を 1 つずつ流す。明るい（寄与の大きい）候補ほど、残りやすい。</text>
</svg>

<!-- fig:restir-reservoir:end -->

## ReSTIR GI
**ReSTIR**（Reservoir-based Spatiotemporal Importance Resampling）は、<strong>「良いサンプルを近い画素・前フレームから借りる」</strong>ことで、**1 画素あたりの有効なサンプル数**を**大幅に増やす**手法です。

| 概念 | 内容 |
| --- | --- |
| **リザーバー** | <strong>画素ごとに、「これまでで最良のサンプル 1 つ」</strong>と**重みの合計**を保持（**重み付きリザーバー サンプリング**） |
| **時間的な再利用** | **前フレームの同じ位置のリザーバー**と**マージ** |
| **空間的な再利用** | **近隣の画素のリザーバー**と**マージ** |
| **バイアスの補正** | **他の画素のサンプル**が**この画素にとって有効か**（**可視性・ヤコビアン**）を**補正** |
| **効果** | <strong>少ないレイ（1 本）</strong>で、**多数のレイを飛ばしたような**品質 |

**ReSTIR DI**（直接光）から、**ReSTIR GI**（間接光）、**ReSTIR PT**（パス全体）へと**発展**しています。**NVIDIA RTXDI・RTXGI** などに**採用**されています。

## よくあるミス

??? failure "再利用が強すぎて、光が不自然ににじむ"
    **法線・深度が合わないサンプルは再利用しない**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **良いサンプルを借りて、少ないレイで高品質**
    - [x] **バイアスの管理が、鍵**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [レイトレ GI](index.md)
- [ノイズとの戦い](noise.md)
- [手法の選び方](choosing.md)
