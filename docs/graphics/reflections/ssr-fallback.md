---
title: SSR のフォールバックと合成
tags:
  - 描画
---

# SSR のフォールバックと合成

SSR は**画面に映っているものだけ**を反射できます。**画面の端・カメラの後ろ・物の裏側・画面の外**への反射は、**映りません**。そのまま使うと**反射が突然消えたり、現れたり**して、**不自然**です。そこで、**SSR が反射を作れない部分**を、**別の方式（プローブ・平面反射・空）で補い**、**滑らかに混ぜます**。このページでは、**フォールバックの考え方・信頼度・合成の順序・混ぜ方・注意点**を説明します。

!!! tip "ポイント"
    - SSR の結果には、<strong>信頼度（0〜1）</strong>を付ける。<strong>当たらなかった・端・遠い・粗い</strong>ほど、信頼度が低い。
    - 最終的な反射 ＝ <strong>SSR × 信頼度 ＋ フォールバック × (1 − 信頼度)</strong>。
    - フォールバックの優先順位：<strong>平面反射 → SSR → ローカル プローブ → グローバル プローブ（空）</strong>。
    - SSR とプローブは、<strong>同じ BRDF の積分（スケール・バイアス）</strong>を掛けて、<strong>調子をそろえる</strong>。
    - <strong>スペキュラ遮蔽</strong>（隅で反射を弱める）を、<strong>プローブ側に</strong>掛ける。
    - 画面外へ出たレイは、<strong>空（またはプローブ）</strong>を引く。

## SSR が反射できないもの

| 状況 | 理由 |
| --- | --- |
| **画面の外にある物** | 深度・色がそもそも画面にない |
| **カメラの後ろ側の物** | 同上 |
| <strong>物の裏側（見えていない面）</strong> | 深度バッファは、手前の面だけ |
| **半透明の物** | 深度に書かれない |
| **画面端付近** | レイがすぐに画面外へ出る |
| **レイが薄い物を突き抜ける** | 厚みの限界で当たらない |

これらの**反射が出ない部分**で、<strong>何も映さない（真っ黒）</strong>と、**不自然**です。**別の方法で映すべきもの**を補います。

<!-- fig:ssr-edge-fade:begin -->

<svg class="fig illust motion" data-fig="ssr-edge-fade" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-ssr-edge-fade" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">画面の端:反射が当たった位置が端へ近づくほど、SSR を弱める</text>
<rect x="50" y="80" width="340" height="220" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="135.0" y1="80" x2="135.0" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="135.0" x2="390" y2="135.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="220.0" y1="80" x2="220.0" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="190.0" x2="390" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="305.0" y1="80" x2="305.0" y2="300" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="245.0" x2="390" y2="245.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="390" y="320" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">当たった位置（画面の横、0〜1）</text>
<text x="50" y="72" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">SSR の信頼度</text>
<path d="M50.0,300.0 L53.4,297.2 L56.8,289.31 L60.2,277.12 L63.6,261.41 L67.0,242.96 L70.4,222.56 L73.8,200.98 L77.2,179.02 L80.6,157.44 L84.0,137.04 L87.4,118.59 L90.8,102.88 L94.2,90.69 L97.6,82.8 L101.0,80.0 L104.4,80.0 L107.8,80.0 L111.2,80.0 L114.6,80.0 L118.0,80.0 L121.4,80.0 L124.8,80.0 L128.2,80.0 L131.6,80.0 L135.0,80.0 L138.4,80.0 L141.8,80.0 L145.2,80.0 L148.6,80.0 L152.0,80.0 L155.4,80.0 L158.8,80.0 L162.2,80.0 L165.6,80.0 L169.0,80.0 L172.4,80.0 L175.8,80.0 L179.2,80.0 L182.6,80.0 L186.0,80.0 L189.4,80.0 L192.8,80.0 L196.2,80.0 L199.6,80.0 L203.0,80.0 L206.4,80.0 L209.8,80.0 L213.2,80.0 L216.6,80.0 L220.0,80.0 L223.4,80.0 L226.8,80.0 L230.2,80.0 L233.6,80.0 L237.0,80.0 L240.4,80.0 L243.8,80.0 L247.2,80.0 L250.6,80.0 L254.0,80.0 L257.4,80.0 L260.8,80.0 L264.2,80.0 L267.6,80.0 L271.0,80.0 L274.4,80.0 L277.8,80.0 L281.2,80.0 L284.6,80.0 L288.0,80.0 L291.4,80.0 L294.8,80.0 L298.2,80.0 L301.6,80.0 L305.0,80.0 L308.4,80.0 L311.8,80.0 L315.2,80.0 L318.6,80.0 L322.0,80.0 L325.4,80.0 L328.8,80.0 L332.2,80.0 L335.6,80.0 L339.0,80.0 L342.4,82.8 L345.8,90.69 L349.2,102.88 L352.6,118.59 L356.0,137.04 L359.4,157.44 L362.8,179.02 L366.2,200.98 L369.6,222.56 L373.0,242.96 L376.4,261.41 L379.8,277.12 L383.2,289.31 L386.6,297.2 L390.0,300.0" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<circle cx="220.0" cy="80.0" r="7" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.0872;0.1104;0.1336;0.1568;0.1800;0.2032;0.2264;0.2496;0.2728;0.2960;0.3192;0.3424;0.3656;0.3888;0.4120;0.4352;0.4584;0.4816;0.5048;0.5280;0.5512;0.5744;0.5976;0.6208;0.6440;0.6672;0.6904;0.7136;0.7368;0.7600;1.0000" values="220;220;50;61.33;72.67;84;95.33;106.67;118;129.33;140.67;152;163.33;174.67;186;197.33;208.67;220;231.33;242.67;254;265.33;276.67;288;299.33;310.67;322;333.33;344.67;356;367.33;378.67;390;390"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.0872;0.1104;0.1336;0.1568;0.1800;0.2032;0.2264;0.2496;0.2728;0.2960;0.3192;0.3424;0.3656;0.3888;0.4120;0.4352;0.4584;0.4816;0.5048;0.5280;0.5512;0.5744;0.5976;0.6208;0.6440;0.6672;0.6904;0.7136;0.7368;0.7600;1.0000" values="80;80;300;272.24;208.26;137.04;87.54;80;80;80;80;80;80;80;80;80;80;80;80;80;80;80;80;80;80;80;80;80;87.54;137.04;208.26;272.24;300;300"/></circle>
<text x="430" y="90" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">SSR の色（空の青）</text>
<rect x="430" y="100" width="130" height="40" fill="#38bdf8"/>
<text x="580" y="90" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">プローブの色（灰）</text>
<rect x="580" y="100" width="130" height="40" fill="#94a3b8"/>
<rect x="505" y="190" width="130" height="60" fill="#94a3b8" stroke="#475569" stroke-width="2"><animate attributeName="fill" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0872;0.1104;0.1336;0.1568;0.1800;0.2032;0.2264;0.2496;0.2728;0.2960;0.3192;0.3424;0.3656;0.3888;0.4120;0.4352;0.4584;0.4816;0.5048;0.5280;0.5512;0.5744;0.5976;0.6208;0.6440;0.6672;0.6904;0.7136;0.7368;0.7600;1.0000" values="#94a3b8;#94a3b8;#88a6c0;#6eaed3;#50b6e7;#3bbcf6;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#38bdf8;#3bbcf6;#50b6e7;#6eaed3;#88a6c0;#94a3b8;#94a3b8"/></rect>
<text x="570" y="180" text-anchor="middle" style="font-size:13px;font-weight:700;fill:#64748b">最終的な反射の色</text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.00 → 信頼度 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.0869;0.0872;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.03 → 信頼度 0.13<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0869;0.0872;0.1101;0.1104;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.07 → 信頼度 0.42<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1101;0.1104;0.1333;0.1336;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.10 → 信頼度 0.74<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1333;0.1336;0.1565;0.1568;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.13 → 信頼度 0.97<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1565;0.1568;0.1797;0.1800;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.17 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1797;0.1800;0.2029;0.2032;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.20 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2029;0.2032;0.2261;0.2264;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.23 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2261;0.2264;0.2493;0.2496;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.27 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2493;0.2496;0.2725;0.2728;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.30 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2725;0.2728;0.2957;0.2960;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.33 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2957;0.2960;0.3189;0.3192;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.37 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3189;0.3192;0.3421;0.3424;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.40 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3421;0.3424;0.3653;0.3656;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.43 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3653;0.3656;0.3885;0.3888;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.47 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3885;0.3888;0.4117;0.4120;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.50 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4117;0.4120;0.4349;0.4352;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.53 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4349;0.4352;0.4581;0.4584;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.57 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4581;0.4584;0.4813;0.4816;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.60 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4813;0.4816;0.5045;0.5048;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.63 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5045;0.5048;0.5277;0.5280;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.67 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5277;0.5280;0.5509;0.5512;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.70 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5509;0.5512;0.5741;0.5744;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.73 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5741;0.5744;0.5973;0.5976;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.77 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5973;0.5976;0.6205;0.6208;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.80 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6205;0.6208;0.6437;0.6440;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.83 → 信頼度 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6437;0.6440;0.6669;0.6672;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.87 → 信頼度 0.97<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6669;0.6672;0.6901;0.6904;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.90 → 信頼度 0.74<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6901;0.6904;0.7133;0.7136;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.93 → 信頼度 0.42<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7133;0.7136;0.7365;0.7368;1.0000" values="0;0;1;1;0;0"/></text>
<text x="430" y="290" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">位置 0.97 → 信頼度 0.13<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7365;0.7368;0.7597;0.7600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="50" y="350" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">端に近いと、画面の外にあるはずの物が足りない。信頼度で、SSR とフォールバック（プローブ）を混ぜる。<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;1.0000;1.0000" values="1;1;0"/></text>
</svg>

<!-- fig:ssr-edge-fade:end -->

## 信頼度（Confidence）

SSR の各画素に、<strong>「この反射をどれだけ信頼してよいか」</strong>の値（**信頼度**）を持たせます。

| 要因 | 信頼度への影響 |
| --- | --- |
| **当たらなかった** | 0 |
| **当たり点が画面の端に近い** | 端に近づくほど、下げる |
| **レイが長い**（遠い当たり） | 遠いほど、下げる |
| **粗さが大きい** | 粗いほど、下げる（SSR はぼけた反射に不安定） |
| **反射がカメラ側を向く** | 画面に映らない領域を指す。下げる |
| **当たり点の法線がレイと同じ向き**（**裏側に当たった**） | その面はレイから見て、裏向き。**無効**（フロント ヒットのみ採用） |
| **厚みの検証で怪しい** | 下げる |

```hlsl
float Confidence(float2 hit_uv, float ray_length, float roughness,
                 float3 hit_normal_vs, float3 dir_vs) {
  float2 edge_dist = abs(hit_uv - 0.5) * 2.0;
  float edge = 1.0 - smoothstep(0.85, 1.0, max(edge_dist.x, edge_dist.y));

  float length_fade = 1.0 - smoothstep(0.5, 1.0, ray_length / max_ray_length);
  float rough_fade = 1.0 - smoothstep(0.6, 0.9, roughness);

  float back_face = step(dot(hit_normal_vs, dir_vs), 0.0);
  return edge * length_fade * rough_fade * back_face;
}
```

<strong>滑らかに（`smoothstep` で）</strong>変化させるのが重要です。**急に切り替える**と**反射の境目がはっきり見えます**。

## 合成：SSR とフォールバックを混ぜる

**SSR の出力**を、<strong>RGB（反射の色）＋ A（信頼度）</strong>とします。**ライティングのパス**で**フォールバック（プローブ・空）と混ぜます**。

<div class="formula">反射 = SSR.rgb × SSR.a ＋ フォールバック × (1 − SSR.a)</div>

```hlsl
float4 ssr = ssr_tex.Sample(linear_sampler, uv);
float3 probe = ProbeReflection(world_pos, N, V, roughness);
float3 reflection = lerp(probe, ssr.rgb, ssr.a);

float3 specular = reflection * (F0 * brdf.x + brdf.y) * SpecularOcclusion(...);
```

| 点 | 説明 |
| --- | --- |
| **`lerp(probe, ssr, confidence)`** | 信頼度が高いほど SSR、低いほどプローブ |
| **BRDF の積分を最後に掛ける** | **SSR・プローブ共通**に、`F0 · A + B` |
| **スペキュラ遮蔽** | **隅で反射を弱める**（[GTAO](../ao/gtao.md)）。**プローブ由来の反射**に特に必要（**SSR は画面にあるものだけを映すので、遮蔽が自然に入る**） |

## フォールバックの階層

**複数の手段**があるとき、**優先順位**をつけて、**信頼度の低い順**に補います。

| 優先 | 方式 | 適用範囲 |
| --- | --- | --- |
| **1** | **平面反射**（[平面反射](planar.md)） | 水面・鏡など、**平面のみ**。最も正確 |
| **2** | **SSR**（画面内の当たり） | 画面に映る物。**信頼度でフェード** |
| **3** | **ローカル プローブ**（[プローブ](probes/index.md)） | **部屋・エリア**ごと。視差補正 |
| **4** | **グローバル プローブ**（空・遠景） | シーン全体の最後の砦 |

<strong>実装は、「下のものから順に混ぜる」</strong>形にします。

```hlsl
float3 color = global_probe_color;
color = lerp(color, local_probe_color, local_probe_weight);
color = lerp(color, ssr.rgb, ssr.a);
color = lerp(color, planar_color, planar_weight);
```

## レイが画面外へ出たとき

**レイが画面の外**に出てしまったとき、**何を映すか**は**フォールバックの役目**です。

| 状況 | 映すもの |
| --- | --- |
| **レイが画面上端から上へ抜けた** | **空**（スカイ プローブ）。屋外ではこれが正解のことが多い |
| **レイが画面の左右・下へ抜けた** | **ローカル プローブ**（画面外の景色をプローブが持っている） |
| **レイがカメラの後ろへ向かう** | プローブ（SSR は使えない） |

## SSR とプローブの、色の調子を合わせる

**SSR の色**（シーンの HDR）と、**プローブの色**は、**調子が違う**ことがあります。**境目で色がずれる**と**フェードが目立ちます**。

| 原因 | 対策 |
| --- | --- |
| **プローブが古いライティング**（ベイク時の明るさ） | **時間帯・ライトの変化**に追従して、**プローブを更新**（または**露出の補正**） |
| **SSR の入力色が露出・ブルーム後** | **露出前の HDR**（**ブルーム前**）から取る |
| **プローブに物体の影が映っていない** | **ライティングの条件**をそろえる |
| **粗さの扱いの違い** | **同じ粗さ→ミップの対応**を使う |

## 動く物体・影・スペキュラ遮蔽

| 項目 | 内容 |
| --- | --- |
| **動く物体** | **SSR には映る**（画面にあれば）。**プローブには映らない**。フェードで**動く物の反射が突然消える**ことがある |
| **影** | SSR は**シーン色をそのまま**使う（影込み）。**プローブはベイク時の影**。**ずれる** |
| **スペキュラ遮蔽** | **プローブの反射**に、**AO ベースのスペキュラ遮蔽**を掛ける。SSR 側はすでに**遮蔽が入っている**ので不要（または弱め） |

## 半透明・水面との関係

| 状況 | 扱い |
| --- | --- |
| **半透明（ガラス・水）の反射** | **深度が書かれない**ので、SSR は使えない。**専用の反射**（平面反射・プローブ）を、**半透明のシェーダーの中で**計算 |
| **半透明の後ろの不透明物の反射** | 通常の SSR が**半透明より前のシーン色**で動く |
| **水面** | 平面反射（または SSR ＋ プローブ）を、フレネルで合成。屈折と混ぜる（[水](../index.md)） |

## 画面端のフェードの設計

| 方式 | 内容 |
| --- | --- |
| **一定の幅で画面端を弱める** | 端から、**10% 程度**の幅で、`smoothstep` |
| **レイの当たり点の位置で** | **当たり点が端に近い**ほど弱める |
| **反射する画素の位置は、見ない** | **反射する面が画面の端**にあることは、問題ない（問題は**当たり点**が画面外に近いか） |
| **ガード バンド** | **画面より少し広い範囲**を描画して、端の反射を改善 |

## 長所と短所（組み合わせ）

| 長所 | 短所 |
| --- | --- |
| **反射が画面の端・視点の変化で突然消えない** | **実装が複雑**（複数の方式・信頼度・合成） |
| **SSR の細かさ ＋ プローブの安定** | **プローブ・SSR の調子がずれる** |
| **コストを方式ごとに配分**できる | **デバッグが難しい**（どの方式が効いているか） |

## よくあるミス

??? failure "信頼度で、急に切り替えて、反射の境目が見える"
    `smoothstep` で、**滑らかに**変化させます。

??? failure "SSR とプローブで、BRDF の積分（スケール・バイアス）を、別々に掛けて、明るさが違う"
    **最後に 1 回**、共通の式で掛けます。

??? failure "SSR の入力に、ブルーム・露出調整後の画像を使い、色がずれる"
    **露出前・ブルーム前の HDR** を使います。

??? failure "プローブにスペキュラ遮蔽を掛けず、隅にまぶしい反射が映る"
    スペキュラ遮蔽を入れます。

??? failure "デバッグで、どの方式が効いているか分からない"
    **SSR のみ・プローブのみ・信頼度**をそれぞれ**画面に出して**確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] SSR は<strong>画面に映らないものを反射できない</strong>。<strong>信頼度</strong>で<strong>フォールバック（プローブ・空）と滑らかに混ぜる</strong>
    - [x] 優先順位：<strong>平面反射 → SSR → ローカル プローブ → グローバル プローブ</strong>
    - [x] 信頼度は<strong>当たり・端・距離・粗さ・向き</strong>から、<strong>`smoothstep` で滑らかに</strong>
    - [x] <strong>BRDF の積分は、最後に共通で</strong>掛ける。<strong>スペキュラ遮蔽</strong>も
    - [x] <strong>半透明・水面</strong>は別の反射の仕組み

## 参考

- Stachowiak, Uludag, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering"（プローブと反射の階層）

## 関連ページ

- [反射](index.md)
- [リフレクション プローブ](probes/index.md)
- [SSR の基礎](ssr-basics/index.md)
- [確率的 SSR](ssr-stochastic.md)
- [GTAO（スペキュラ遮蔽）](../ao/gtao.md)
