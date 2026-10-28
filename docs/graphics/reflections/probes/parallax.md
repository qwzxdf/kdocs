---
title: Parallax Correction
tags:
  - 描画
---

# Parallax Correction

<strong>キューブマップは「プローブの位置から見た景色」なので、別の場所から見ると反射が実際とずれます</strong>。部屋の形の箱（ボックス）を想定して、レイと箱の交点を求めて補正するのが標準的な方法です。このページでは視差の問題・ボックス投影・補正の限界を説明します。

!!! tip "ポイント"
    - キューブマップは、無限遠の景色を前提にしているため、近くの壁がずれる。
    - 部屋の形の箱を設定し、レイと箱の交点から読み出す方向を作り直す（ボックス投影）。
    - 箱の形が実際と違うと、ずれが残る。
    - 床の反射は補正しても、不自然になりやすい（平面反射を併用）。

!!! info "このページを読む前に"
    - [Reflection Probes](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## 視差の問題と補正
### 視差の問題

プローブは <strong>1 点（プローブの位置）から見た景色</strong>です。面とプローブの位置が離れていると、面から見た景色とプローブから見た景色がずれます。

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

特に平らな床で壁との境が実際より遠くに映る・物が宙に浮いて見えるといった症状が出ます。

<!-- fig:parallax-box:begin -->

<svg class="fig illust motion" data-fig="parallax-box" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-parallax-box" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">視差補正: キューブマップの反射を部屋の箱に合わせて「どこに映るか」を直す</text>
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

プローブが写している範囲（部屋）を箱（または球）で近似します。反射レイを表面の位置 p から R 方向に飛ばして、箱と交差する点 H を求めます。プローブの位置から H への方向で、キューブマップを引きます。

<div class="formula">H = p + R · t　（レイと箱の交点）、　引く方向 R′ = H − probe_pos</div>

表面の位置 p から、本当に当たる壁（H）を求めて、そこをプローブから見た方向で引き直すので、視差のずれが補正されます。

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
    プローブが写す範囲（影響範囲）を部屋の大きさに合わせた箱にします。箱が実際の壁と合っているほど、補正が正確です。合っていないと補正が逆効果になることもあります。

### 視差補正の限界

| 限界 | 説明 |
| --- | --- |
| 箱の近似 | 部屋の中の家具・物体は箱の壁として扱われる → 家具の反射は、壁の位置に映る |
| プローブ位置の物陰 | プローブから見えなかった所（家具の裏）は、撮れていない |
| 不規則な形の部屋 | 箱で表せない部屋では、補正が合わない |
| 動く物 | プローブには映らない（動的な更新が必要） |

## 箱による視差補正

<strong>部屋を箱</strong>と 近似します。反射レイを箱と交差させて当たった位置を求め、その位置からプローブへの向きで、キューブマップを引き直します（Bjorke、2004、Lagarde と Zanuttini、2012）。

```text
  P ──R──→ A（箱の壁との、交点）
  プローブ ● から A への向き R' で、キューブマップを引く → 実際に、A が映るはずの、景色
```

```hlsl
// 箱（軸に平行）による、視差補正。box_min, box_max: 箱の範囲（ワールド座標）、probe_pos: プローブの位置。
float3 ParallaxCorrect(float3 R, float3 world_pos, float3 box_min, float3 box_max, float3 probe_pos) {
  // レイ（world_pos から、R の向き）と、箱の、交点を求める（スラブ法）。
  float3 first_plane = (box_max - world_pos) / R;
  float3 second_plane = (box_min - world_pos) / R;
  float3 furthest = max(first_plane, second_plane);                      // 各軸で、遠い方の、平面までの距離
  float dist = min(min(furthest.x, furthest.y), furthest.z);             // 3 つの軸のうち、最も近い（= 箱から、出る）距離
  float3 hit = world_pos + R * dist;                                      // 箱の壁との交点
  return hit - probe_pos;                                                 // プローブから、交点への向き（これで、キューブマップを引く）
}
```

スラブ法で レイと箱の交点を求めます。各軸についてレイが箱の外へ出る、平面までの距離を求めその最小が箱から出る、距離です。交点からプローブへの向きが補正した、反射方向です。

```hlsl
float3 corrected = ParallaxCorrect(R, input.world_position, g_probe_box_min, g_probe_box_max, g_probe_position);
float3 prefiltered = g_probe_cube.SampleLevel(g_linear_clamp, corrected, mip).rgb;
```

補正した方向で キューブマップを引くだけで反射が面の位置に合い窓が歩くと動いて、見えます。

## 箱の設定

<strong>箱</strong>は 部屋の形に合わせて、アーティストが設定します。

| 設定 | 内容 |
| --- | --- |
| 箱の大きさ | 部屋の壁にぴったり（壁の内側）。大きすぎると補正が弱く小さすぎると映像が歪む |
| プローブの位置 | 箱の中央付近（最も、バランスが良い） |
| 影響範囲（ブレンド用） | プローブが効く、範囲（箱より少し大きく）。範囲の端でフェード（[Probe Operation](blending.md)） |

## 球による補正（屋外）

<strong>屋外</strong>（箱ではない広い空間）では球で、近似する方法もあります。半径を環境の大きさに合わせます。

```hlsl
// 球による、視差補正（プローブを中心とした、半径 radius の球）。
float3 ParallaxCorrectSphere(float3 R, float3 world_pos, float3 center, float radius) {
  float3 oc = world_pos - center;
  float b = dot(oc, R);
  float c = dot(oc, oc) - radius * radius;
  float dist = -b + sqrt(max(b * b - c, 0.0));                             // レイが球から出る距離
  return (world_pos + R * dist) - center;                                   // 球の、交点への向き
}
```

球は箱より単純ですが 部屋の、形（直方体）には合いにくいので、屋内には箱、屋外・円形の空間には球を使い分けます。

## 補正の限界

| 限界 | 内容 |
| --- | --- |
| 箱は近似 | 実際の部屋が直方体でない（柱、家具、凹み）と補正がずれる |
| 物は補正されない | キューブマップに焼かれた家具は箱の壁にあるものとして、扱われる。家具の反射位置はずれる |
| 視線が箱の外 | 面が箱の、外にある（プローブの影響範囲の端）と補正が破綻する。ブレンドで薄める |
| 近い面の補正が強い | 壁の、すぐ近くの面では補正の効果が極端で歪む。箱を少し小さく補正を弱める |

## 補正の強さを調整する

<strong>補正した方向</strong>と 補正なしの、方向を補間して補正の強さを調整します。

```hlsl
float3 dir = lerp(R, corrected, g_parallax_strength);                    // 0 = 補正なし、1 = 完全な補正
```

部屋の形に合わない場合、弱める（0.5〜0.8）と破綻が目立ちません。

## よくあるミス

??? failure "床や壁に映る景色が動くと滑って見える"
    <strong>ボックス投影（視差補正）</strong>を入れる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 箱を想定して、読み出す方向を補正
    - [x] 箱の形が実際に近いほど良い

## 参考

- Lagarde, Zanuttini, "Local Image-Based Lighting With Parallax-Corrected Cubemap", SIGGRAPH 2012 Talks（箱による、視差補正）
- Bjorke, "Image-Based Lighting", GPU Gems, Chapter 19, 2004（キューブマップの、視差補正のはしり）
- Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014, Physically Based Shading in Theory and Practice
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（反射、IBL の章）

## 関連ページ

- [Reflection Probes](index.md)
- [Probe Operation](blending.md)
- [Planar Reflections](../planar.md)
