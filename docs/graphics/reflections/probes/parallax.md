---
title: Parallax Correction
tags:
  - 描画
---

# Parallax Correction

<strong>キューブマップは、「プローブの位置から見た景色」なので、別の場所から見ると、反射が実際とずれます</strong>。<strong>部屋の形の箱（ボックス）を想定して、レイと箱の交点を求めて、補正する</strong>のが標準的な方法です。このページでは、視差の問題・ボックス投影・補正の限界を説明します。

!!! tip "ポイント"
    - キューブマップは、無限遠の景色を前提にしているため、近くの壁がずれる。
    - 部屋の形の箱を設定し、レイと箱の交点から、読み出す方向を作り直す（ボックス投影）。
    - 箱の形が実際と違うと、ずれが残る。
    - 床の反射は、補正しても、不自然になりやすい（平面反射を併用）。

## 視差の問題と補正
### 視差の問題

プローブは、<strong>1 点（プローブの位置）から見た景色</strong>です。<strong>面とプローブの位置が離れている</strong>と、面から見た景色とプローブから見た景色が、ずれます。

<svg class="fig illust" viewBox="0 0 780 300" role="img" aria-label="視差の問題">
<text x="20" y="24" class="fig-title">プローブの位置と、反射する面の位置が違うと、映り込みがずれる</text>
<rect x="50" y="50" width="680" height="220" fill="rgba(150,150,150,0.1)" stroke="currentColor" stroke-width="2"/><text x="60" y="68" style="font-size:12px">部屋（壁）</text>
<circle cx="390" cy="160" r="7" fill="#2ea043"/><text x="364" y="184" style="font-size:12px;fill:#2ea043;font-weight:700">プローブ</text>
<line x1="150" y1="250" x2="330" y2="250" stroke="currentColor" stroke-width="5"/><text x="180" y="270" style="font-size:12px">床の面（反射する）</text>
<circle cx="250" cy="250" r="6" fill="currentColor"/><text x="240" y="238" style="font-size:12px">p</text>
<line x1="250" y1="250" x2="500" y2="110" stroke="#e5484d" stroke-width="2.5"/><text x="500" y="104" style="font-size:12px;fill:#e5484d;font-weight:700">本当の反射が当たる壁</text>
<line x1="390" y1="160" x2="640" y2="20" stroke="#4c8bf5" stroke-width="2" stroke-dasharray="5 3"/><text x="520" y="62" style="font-size:12px;fill:#4c8bf5;font-weight:700">プローブから R 方向に引くと…</text>
<text x="420" y="290" style="font-size:12px">→ 実際より、遠く（別の場所）の景色が映ってしまう</text>
</svg>

特に<strong>平らな床</strong>で<strong>壁との境が実際より遠くに映る</strong>・物が宙に浮いて見えるといった症状が出ます。

<!-- fig:parallax-box:begin -->

<svg class="fig illust motion" data-fig="parallax-box" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-parallax-box" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">視差補正: キューブマップの反射を、部屋の箱に合わせて「どこに映るか」を直す</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">部屋(幅 12、高さ 6)の断面。プローブは部屋の中央。床の点から、右の壁へ反射する光線を調べる</text>
<rect x="30" y="96" width="900" height="360" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 部屋の断面</text>
<rect x="360.0" y="178.0" width="504.0" height="252.0" fill="#f8fafc" stroke="#475569" stroke-width="4"/>
<circle cx="612.0" cy="304.0" r="9" fill="#7c3aed"/>
<text x="612.0" y="290.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#7c3aed">プローブ(キューブマップの中心)</text>
<line x1="864.0" y1="430.0" x2="872.0" y2="430.0" stroke="#475569" stroke-width="2"/>
<text x="876.0" y="434.0" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">高さ 0</text>
<line x1="864.0" y1="388.0" x2="872.0" y2="388.0" stroke="#475569" stroke-width="2"/>
<text x="876.0" y="392.0" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">高さ 1</text>
<line x1="864.0" y1="346.0" x2="872.0" y2="346.0" stroke="#475569" stroke-width="2"/>
<text x="876.0" y="350.0" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">高さ 2</text>
<line x1="864.0" y1="304.0" x2="872.0" y2="304.0" stroke="#475569" stroke-width="2"/>
<text x="876.0" y="308.0" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">高さ 3</text>
<line x1="864.0" y1="262.0" x2="872.0" y2="262.0" stroke="#475569" stroke-width="2"/>
<text x="876.0" y="266.0" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">高さ 4</text>
<line x1="864.0" y1="220.0" x2="872.0" y2="220.0" stroke="#475569" stroke-width="2"/>
<text x="876.0" y="224.0" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">高さ 5</text>
<line x1="864.0" y1="178.0" x2="872.0" y2="178.0" stroke="#475569" stroke-width="2"/>
<text x="876.0" y="182.0" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">高さ 6</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0443;0.0444;0.1287;0.1289;1.0000" values="0;0;1;1;0;0"/><circle cx="393.6" cy="430.0" r="7" fill="#1f2937"/>
<line x1="393.6" y1="430.0" x2="864.0" y2="220.56" stroke="#2ea043" stroke-width="3.5"/>
<circle cx="864.0" cy="220.56" r="7" fill="#2ea043"/>
<line x1="612.0" y1="304.0" x2="864.0" y2="191.8" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="6 5"/>
<circle cx="864.0" cy="191.8" r="7" fill="#e5484d"/>
<text x="40" y="150" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">床の点 1(x = 0.8)</text>
<text x="40" y="174" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">本当に映る高さ(緑): 4.99</text>
<text x="40" y="196" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">補正なし(赤): 5.67 → ずれ 0.68</text>
<text x="40" y="218" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">補正あり: 4.99 → ずれ 0.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1287;0.1289;0.2132;0.2133;1.0000" values="0;0;1;1;0;0"/><circle cx="418.8" cy="430.0" r="7" fill="#1f2937"/>
<line x1="418.8" y1="430.0" x2="864.0" y2="231.78" stroke="#2ea043" stroke-width="3.5"/>
<circle cx="864.0" cy="231.78" r="7" fill="#2ea043"/>
<line x1="612.0" y1="304.0" x2="864.0" y2="191.8" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="6 5"/>
<circle cx="864.0" cy="191.8" r="7" fill="#e5484d"/>
<text x="40" y="150" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">床の点 2(x = 1.4)</text>
<text x="40" y="174" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">本当に映る高さ(緑): 4.72</text>
<text x="40" y="196" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">補正なし(赤): 5.67 → ずれ 0.95</text>
<text x="40" y="218" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">補正あり: 4.72 → ずれ 0.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2132;0.2133;0.2976;0.2978;1.0000" values="0;0;1;1;0;0"/><circle cx="444.0" cy="430.0" r="7" fill="#1f2937"/>
<line x1="444.0" y1="430.0" x2="864.0" y2="243.0" stroke="#2ea043" stroke-width="3.5"/>
<circle cx="864.0" cy="243.0" r="7" fill="#2ea043"/>
<line x1="612.0" y1="304.0" x2="864.0" y2="191.8" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="6 5"/>
<circle cx="864.0" cy="191.8" r="7" fill="#e5484d"/>
<text x="40" y="150" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">床の点 3(x = 2.0)</text>
<text x="40" y="174" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">本当に映る高さ(緑): 4.45</text>
<text x="40" y="196" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">補正なし(赤): 5.67 → ずれ 1.22</text>
<text x="40" y="218" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">補正あり: 4.45 → ずれ 0.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2976;0.2978;0.3820;0.3822;1.0000" values="0;0;1;1;0;0"/><circle cx="469.2" cy="430.0" r="7" fill="#1f2937"/>
<line x1="469.2" y1="430.0" x2="864.0" y2="254.22" stroke="#2ea043" stroke-width="3.5"/>
<circle cx="864.0" cy="254.22" r="7" fill="#2ea043"/>
<line x1="612.0" y1="304.0" x2="864.0" y2="191.8" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="6 5"/>
<circle cx="864.0" cy="191.8" r="7" fill="#e5484d"/>
<text x="40" y="150" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">床の点 4(x = 2.6)</text>
<text x="40" y="174" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">本当に映る高さ(緑): 4.19</text>
<text x="40" y="196" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">補正なし(赤): 5.67 → ずれ 1.49</text>
<text x="40" y="218" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">補正あり: 4.19 → ずれ 0.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3820;0.3822;0.4665;0.4667;1.0000" values="0;0;1;1;0;0"/><circle cx="494.4" cy="430.0" r="7" fill="#1f2937"/>
<line x1="494.4" y1="430.0" x2="864.0" y2="265.44" stroke="#2ea043" stroke-width="3.5"/>
<circle cx="864.0" cy="265.44" r="7" fill="#2ea043"/>
<line x1="612.0" y1="304.0" x2="864.0" y2="191.8" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="6 5"/>
<circle cx="864.0" cy="191.8" r="7" fill="#e5484d"/>
<text x="40" y="150" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">床の点 5(x = 3.2)</text>
<text x="40" y="174" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">本当に映る高さ(緑): 3.92</text>
<text x="40" y="196" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">補正なし(赤): 5.67 → ずれ 1.75</text>
<text x="40" y="218" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">補正あり: 3.92 → ずれ 0.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4665;0.4667;0.5509;0.5511;1.0000" values="0;0;1;1;0;0"/><circle cx="519.6" cy="430.0" r="7" fill="#1f2937"/>
<line x1="519.6" y1="430.0" x2="864.0" y2="276.66" stroke="#2ea043" stroke-width="3.5"/>
<circle cx="864.0" cy="276.66" r="7" fill="#2ea043"/>
<line x1="612.0" y1="304.0" x2="864.0" y2="191.8" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="6 5"/>
<circle cx="864.0" cy="191.8" r="7" fill="#e5484d"/>
<text x="40" y="150" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">床の点 6(x = 3.8)</text>
<text x="40" y="174" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">本当に映る高さ(緑): 3.65</text>
<text x="40" y="196" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">補正なし(赤): 5.67 → ずれ 2.02</text>
<text x="40" y="218" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">補正あり: 3.65 → ずれ 0.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5509;0.5511;0.6354;0.6356;1.0000" values="0;0;1;1;0;0"/><circle cx="544.8" cy="430.0" r="7" fill="#1f2937"/>
<line x1="544.8" y1="430.0" x2="864.0" y2="287.88" stroke="#2ea043" stroke-width="3.5"/>
<circle cx="864.0" cy="287.88" r="7" fill="#2ea043"/>
<line x1="612.0" y1="304.0" x2="864.0" y2="191.8" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="6 5"/>
<circle cx="864.0" cy="191.8" r="7" fill="#e5484d"/>
<text x="40" y="150" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">床の点 7(x = 4.4)</text>
<text x="40" y="174" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">本当に映る高さ(緑): 3.38</text>
<text x="40" y="196" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">補正なし(赤): 5.67 → ずれ 2.29</text>
<text x="40" y="218" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">補正あり: 3.38 → ずれ 0.00</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6354;0.6356;1.0000" values="0;0;1;1"/><circle cx="570.0" cy="430.0" r="7" fill="#1f2937"/>
<line x1="570.0" y1="430.0" x2="864.0" y2="299.1" stroke="#2ea043" stroke-width="3.5"/>
<circle cx="864.0" cy="299.1" r="7" fill="#2ea043"/>
<line x1="612.0" y1="304.0" x2="864.0" y2="191.8" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="6 5"/>
<circle cx="864.0" cy="191.8" r="7" fill="#e5484d"/>
<text x="40" y="150" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">床の点 8(x = 5.0)</text>
<text x="40" y="174" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">本当に映る高さ(緑): 3.12</text>
<text x="40" y="196" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">補正なし(赤): 5.67 → ずれ 2.55</text>
<text x="40" y="218" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">補正あり: 3.12 → ずれ 0.00</text>
</g>
<circle cx="46" cy="246" r="6" fill="#2ea043"/>
<text x="56" y="250" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">本当の反射</text>
<circle cx="46" cy="268" r="6" fill="#e5484d"/>
<text x="56" y="272" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">補正なし(プローブから同じ向き)</text>
<text x="40" y="480" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">ずれの平均:</text>
<text x="150" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0532;0.0533;1.0000" values="1;1;0;0"/></text>
<text x="150" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">68<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0532;0.0533;0.1376;0.1378;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">82<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1376;0.1378;0.2220;0.2222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">95<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2220;0.2222;0.3065;0.3067;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">109<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3065;0.3067;0.3909;0.3911;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">122<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3909;0.3911;0.4754;0.4756;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">135<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4754;0.4756;0.5598;0.5600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">149<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5598;0.5600;0.6443;0.6444;1.0000" values="0;0;1;1;0;0"/></text>
<text x="150" y="484" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">162<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6443;0.6444;1.0000" values="0;0;1;1"/></text>
<text x="205" y="484" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">(高さ × 100)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7198;0.7200;1.0000" values="0;0;1;1"/><rect x="300" y="462" width="630" height="62" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="316" y="486" text-anchor="start" style="font-size:15px;font-weight:700;fill:#991b1b">補正なし: 平均 1.62 ずれる(床の点によって違う)</text>
<text x="316" y="510" text-anchor="start" style="font-size:14px;font-weight:700;fill:#166534">補正あり: ずれ 0(部屋が箱なので、光線と箱の交点で厳密に直せる)</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">キューブマップは、プローブの位置から見た景色。床の点とは、見る位置が違う<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0443;0.0444;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">床の点ごとに、本当に映る場所と、プローブから読む場所を比べる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0443;0.0444;0.7198;0.7200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光線と箱の交点を求め、その向きでプローブを読むと、位置が合う<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7198;0.7200;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:parallax-box:end -->

### 視差補正：プローブの範囲を箱で近似する

<strong>プローブが写している範囲（部屋）を、箱（または球）で近似</strong>します。<strong>反射レイ</strong>を表面の位置 p から R 方向に飛ばして、箱と交差する点 H を求めます。プローブの位置から H への方向で、キューブマップを引きます。

<div class="formula">H = p + R · t　（レイと箱の交点）、　引く方向 R′ = H − probe_pos</div>

<strong>表面の位置 p から</strong>、<strong>本当に当たる壁（H）</strong>を求めて、そこを<strong>プローブから見た方向</strong>で引き直すので、視差のずれが補正されます。

### 箱（AABB）との交差

```hlsl
float3 BoxProjection(float3 world_pos, float3 R, float3 probe_pos,
                     float3 box_min, float3 box_max) {
  float3 first_plane = (box_max - world_pos) / R;
  float3 second_plane = (box_min - world_pos) / R;
  float3 furthest = max(first_plane, second_plane);
  float distance = min(min(furthest.x, furthest.y), furthest.z);
  float3 hit = world_pos + R * distance;
  return hit - probe_pos;
}
```

| 点 | 説明 |
| --- | --- |
| `(box_max − pos) / R`・`(box_min − pos) / R` | 3 軸の箱の面までの距離（レイが各面に当たる t） |
| `max(first, second)` | 前向き（レイが進む側）の面を選ぶ |
| `min(…x, y, z)` | 最初に当たる面（箱の内側からの出口） |
| 戻り値 | プローブから見た方向（正規化はサンプラーが不要） |

!!! note "箱の範囲の決め方"
    <strong>プローブが写す範囲</strong>（影響範囲）を、<strong>部屋の大きさに合わせた箱</strong>にします。箱が実際の壁と合っているほど、補正が正確です。合っていないと補正が逆効果になることもあります。

### 視差補正の限界

| 限界 | 説明 |
| --- | --- |
| 箱の近似 | 部屋の中の家具・物体は箱の壁として扱われる → 家具の反射は、壁の位置に映る |
| プローブ位置の物陰 | プローブから見えなかった所（家具の裏）は、撮れていない |
| 不規則な形の部屋 | 箱で表せない部屋では、補正が合わない |
| 動く物 | プローブには映らない（動的な更新が必要） |

## よくあるミス

??? failure "床や壁に映る景色が、動くと滑って見える"
    <strong>ボックス投影（視差補正）</strong>を入れる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 箱を想定して、読み出す方向を補正
    - [x] 箱の形が、実際に近いほど良い

## 参考

- McGuire & Mara, "Efficient GPU Screen-Space Ray Tracing"（JCGT 2014）
- Karis, "Real Shading in Unreal Engine 4"（SIGGRAPH 2013）
- Stachowiak, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015）

## 関連ページ

- [Reflection Probes](index.md)
- [Probe Operation](blending.md)
- [Planar Reflections](../planar.md)
