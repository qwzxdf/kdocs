---
title: From the Rendering Equation to AO
tags:
  - 描画
---

# From the Rendering Equation to AO

<strong>AO は、レンダリング方程式を、「天球が一様に明るい」と仮定して、単純化</strong>したものです。<strong>この導出を追うと、AO の式の「コサイン重み」「可視性」「1/π」が、どこから来たのか</strong>が分かります。このページでは、出発点のレンダリング方程式・一様な天球の仮定・球面座標での書き直しを説明します。

!!! tip "ポイント"
    - 出発点は、レンダリング方程式の拡散項。
    - 天球の明るさを一定（1）と仮定すると、積分が「可視性 × コサイン」だけになる。
    - 球面座標（天頂角 θ・方位角 φ）で書き直すと、AO の式が現れる。
    - AO ＝ (1/π) ∫ V(ω) cosθ dω。

## 出発点：レンダリング方程式
面上の点 p から、方向 ω_o へ出ていく光の量 L_o は、次の式で表されます。

<div class="formula">L_o(p, ω_o) = ∫ f_r(p, ω_i, ω_o) · L_i(p, ω_i) · (n·ω_i) dω_i　（積分は法線 n 側の半球 Ω）</div>

| 記号 | 意味 |
| --- | --- |
| <strong>L_i(p, ω_i)</strong> | 方向 ω_i から点 p に届く光の強さ（入射放射輝度） |
| f_r | 面の反射の仕方（BRDF）。物体の色・粗さ・金属度で決まる |
| n·ω_i | 入射方向と法線のなす角のコサイン。斜めから来る光ほど、面を照らす量が少ない |

### 面が拡散反射だけの場合

拡散反射（ランバート）では、`f_r = ρ / π`（ρ はアルベド）で、<strong>方向によらず一定</strong>です。式は次のように簡単になります。

<div class="formula">L_o = (ρ / π) · ∫ L_i(ω_i) · (n·ω_i) dω_i</div>

## 天球が一様に明るいと仮定する
AO では<strong>周囲の明るさを一様</strong>（どの方向からも同じ強さ L_sky）と仮定します。遮られていなければ、空の光がそのまま届きます。遮られている方向からは、<strong>空の光が来ません</strong>（遮蔽物自体の明るさは、ここでは考えません）。

そこで<strong>可視性</strong> V(ω) を導入します。

| V(ω) | 意味 |
| --- | --- |
| 1 | ω 方向に遮蔽物がなく、空が見える |
| 0 | ω 方向が近くの物体で遮られている |

すると入射光は `L_i(ω) = L_sky · V(ω)` となり、出ていく光は次のとおりです。

<div class="formula">L_o = (ρ / π) · L_sky · ∫ V(ω) · (n·ω) dω</div>

<strong>何も遮られていない</strong>（V = 1）場合の積分は半球全体のコサイン重み付きの立体角で、<strong>ちょうど π</strong> になります。

<div class="formula">∫ (n·ω) dω = π　（半球全体）</div>

そのため、遮蔽のない面の明るさは `ρ · L_sky` になります。<strong>遮蔽がある面の遮蔽のない面に対する比</strong>を、<strong>AO の値</strong>と定義します。

<div class="formula">AO(p, n) = (1 / π) · ∫ V(ω) · (n·ω) dω　（0 〜 1）</div>

- 1：遮蔽なし（完全に明るい）。
- 0：すべての方向が遮られている（真っ暗）。
- 平らな床の上の点は、ほぼ 1。壁との角の点は、約 0.5、部屋の隅（3 面が交わる所）は、約 0.3 前後になります。

!!! note "なぜコサインが付くのか"
    斜めに入ってくる光は、面を<strong>薄く</strong>照らします（同じ光の束が広い面積に広がるため）。その効果が `n·ω` です。<strong>真上（法線の方向）の遮蔽は横の遮蔽より、明るさに効きます</strong>。この重みが、AO の見た目の自然さにつながり、後の GTAO では、この重みを正しく扱うことが改善点の 1 つになります。

<svg class="fig illust" viewBox="0 0 760 300" role="img" aria-label="AO の半球と可視性">
<text x="20" y="24" class="fig-title">点 p の上の半球：遮られた方向（赤）は、空の光が届かない</text>
<line x1="60" y1="230" x2="700" y2="230" stroke="currentColor" stroke-width="3"/>
<path d="M200,230 A150,150 0 0 1 500,230" fill="rgba(76,139,245,0.12)" stroke="currentColor" stroke-width="2" stroke-dasharray="6 4"/>
<circle cx="350" cy="230" r="7" fill="currentColor"/><text x="340" y="256" style="font-size:12px">点 p</text>
<line x1="350" y1="230" x2="350" y2="70" stroke="#2ea043" stroke-width="3"/><text x="358" y="82" style="font-size:12px;fill:#2ea043;font-weight:700">法線 n</text>
<polygon points="520,230 520,150 580,150 580,230" fill="rgba(150,150,150,0.5)" stroke="currentColor" stroke-width="2"/><text x="526" y="142" style="font-size:12px">近くの壁（遮蔽物）</text>
<line x1="350" y1="230" x2="505" y2="170" stroke="#e5484d" stroke-width="3"/><text x="395" y="190" style="font-size:12px;fill:#e5484d;font-weight:700">遮られる</text>
<line x1="350" y1="230" x2="490" y2="116" stroke="#e5484d" stroke-width="2.5" stroke-dasharray="4 3"/>
<line x1="350" y1="230" x2="420" y2="90" stroke="#4c8bf5" stroke-width="2.5"/><text x="396" y="84" style="font-size:12px;fill:#4c8bf5;font-weight:700">空が見える</text>
<line x1="350" y1="230" x2="250" y2="95" stroke="#4c8bf5" stroke-width="2.5"/>
<line x1="350" y1="230" x2="205" y2="170" stroke="#4c8bf5" stroke-width="2.5"/>
<text x="40" y="285" style="font-size:12px">AO ＝ 空が見える方向の、コサイン重み付きの割合。法線に近い方向ほど、重みが大きい</text>
</svg>

## 球面座標での書き直し
半球の方向 ω を<strong>法線を軸にした角度</strong>で表します。法線からの角度を θ（0 〜 π/2）、方位角を φ（0 〜 2π）とすると、`n·ω = cosθ`、`dω = sinθ dθ dφ` です。

<div class="formula">AO = (1 / π) · ∫₀^{2π} ∫₀^{π/2} V(θ, φ) · cosθ · sinθ  dθ dφ</div>

<strong>V がすべて 1</strong> なら、`∫ cosθ sinθ dθ = 1/2`、`∫ dφ = 2π` で、`AO = (1/π)(2π)(1/2) = 1` となり、先ほどの結論と合います。

<!-- fig:cos-weighted-fraction:begin -->

<svg class="fig illust motion" data-fig="cos-weighted-fraction" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-cos-weighted-fraction" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">半球から届く光の大半は、真上に近い角度から来る(cos で重みが付く)</text>
<rect x="70" y="70" width="640" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="230.0" y1="70" x2="230.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="130.0" x2="710" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="70" x2="390.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="190.0" x2="710" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="550.0" y1="70" x2="550.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="250.0" x2="710" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="70" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">θ 以内から来る光の割合</text>
<text x="710" y="346" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">真上からの角度 θ (度)</text>
<text x="70.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0</text>
<text x="176.67" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">15</text>
<text x="283.33" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">30</text>
<text x="390.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">45</text>
<text x="496.67" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">60</text>
<text x="603.33" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">75</text>
<text x="710.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">90</text>
<path d="M70.0,310.0 L77.11,309.93 L84.22,309.72 L91.33,309.37 L98.44,308.89 L105.56,308.26 L112.67,307.5 L119.78,306.61 L126.89,305.57 L134.0,304.41 L141.11,303.11 L148.22,301.68 L155.33,300.12 L162.44,298.43 L169.56,296.62 L176.67,294.69 L183.78,292.63 L190.89,290.46 L198.0,288.17 L205.11,285.77 L212.22,283.26 L219.33,280.65 L226.44,277.92 L233.56,275.1 L240.67,272.19 L247.78,269.18 L254.89,266.08 L262.0,262.89 L269.11,259.62 L276.22,256.28 L283.33,252.86 L290.44,249.37 L297.56,245.81 L304.67,242.2 L311.78,238.53 L318.89,234.8 L326.0,231.03 L333.11,227.22 L340.22,223.36 L347.33,219.48 L354.44,215.56 L361.56,211.62 L368.67,207.66 L375.78,203.69 L382.89,199.7 L390.0,195.71 L397.11,191.73 L404.22,187.74 L411.33,183.77 L418.44,179.81 L425.56,175.87 L432.67,171.95 L439.78,168.07 L446.89,164.21 L454.0,160.4 L461.11,156.63 L468.22,152.9 L475.33,149.23 L482.44,145.61 L489.56,142.06 L496.67,138.57 L503.78,135.15 L510.89,131.81 L518.0,128.54 L525.11,125.35 L532.22,122.25 L539.33,119.24 L546.44,116.32 L553.56,113.5 L560.67,110.78 L567.78,108.17 L574.89,105.66 L582.0,103.26 L589.11,100.97 L596.22,98.79 L603.33,96.74 L610.44,94.81 L617.56,92.99 L624.67,91.31 L631.78,89.75 L638.89,88.32 L646.0,87.02 L653.11,85.86 L660.22,84.82 L667.33,83.93 L674.44,83.16 L681.56,82.54 L688.67,82.05 L695.78,81.71 L702.89,81.5 L710.0,81.43" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<circle cx="70.0" cy="310.0" r="7" fill="#1f2937"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0920;0.1040;0.1160;0.1280;0.1400;0.1520;0.1640;0.1760;0.1880;0.2000;0.2120;0.2240;0.2360;0.2480;0.2600;0.2720;0.2840;0.2960;0.3080;0.3200;0.3320;0.3440;0.3560;0.3680;0.3800;0.3920;0.4040;0.4160;0.4280;0.4400;0.4520;0.4640;0.4760;0.4880;0.5000;0.5120;0.5240;0.5360;0.5480;0.5600;0.5720;0.5840;0.5960;0.6080;0.6200;0.6320;0.6440;0.6560;0.6680;0.6800;0.6920;0.7040;0.7160;0.7280;0.7400;0.7520;0.7640;0.7760;0.7880;0.8000;1.0000" values="70;70;80.67;91.33;102;112.67;123.33;134;144.67;155.33;166;176.67;187.33;198;208.67;219.33;230;240.67;251.33;262;272.67;283.33;294;304.67;315.33;326;336.67;347.33;358;368.67;379.33;390;400.67;411.33;422;432.67;443.33;454;464.67;475.33;486;496.67;507.33;518;528.67;539.33;550;560.67;571.33;582;592.67;603.33;614;624.67;635.33;646;656.67;667.33;678;688.67;699.33;710;710"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0920;0.1040;0.1160;0.1280;0.1400;0.1520;0.1640;0.1760;0.1880;0.2000;0.2120;0.2240;0.2360;0.2480;0.2600;0.2720;0.2840;0.2960;0.3080;0.3200;0.3320;0.3440;0.3560;0.3680;0.3800;0.3920;0.4040;0.4160;0.4280;0.4400;0.4520;0.4640;0.4760;0.4880;0.5000;0.5120;0.5240;0.5360;0.5480;0.5600;0.5720;0.5840;0.5960;0.6080;0.6200;0.6320;0.6440;0.6560;0.6680;0.6800;0.6920;0.7040;0.7160;0.7280;0.7400;0.7520;0.7640;0.7760;0.7880;0.8000;1.0000" values="310;310;309.84;309.37;308.59;307.5;306.11;304.41;302.41;300.12;297.54;294.69;291.56;288.17;284.53;280.65;276.53;272.19;267.64;262.89;257.96;252.86;247.6;242.2;236.67;231.03;225.29;219.48;213.59;207.66;201.7;195.71;189.73;183.77;177.84;171.95;166.13;160.4;154.76;149.23;143.83;138.57;133.47;128.54;123.79;119.24;114.9;110.78;106.9;103.26;99.87;96.74;93.88;91.31;89.02;87.02;85.32;83.93;82.84;82.05;81.59;81.43;81.43"/></circle>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">θ = 30 度以内: 光の 25%（半球の面積では 13%）<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.2597;0.2600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">θ = 45 度以内: 50%<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2597;0.2600;0.4397;0.4400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">θ = 60 度以内: 75%<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4397;0.4400;0.6197;0.6200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">残りの 25% は、60〜90 度の浅い角度から来る<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6197;0.6200;0.7997;0.8000;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:cos-weighted-fraction:end -->

## よくあるミス

??? failure "AO は、光の方向に依存すると思い込む"
    <strong>AO は、光の方向に依存しない</strong>（<strong>周囲が一様に明るいと仮定している</strong>）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 一様な天球の仮定で、レンダリング方程式が AO になる
    - [x] AO ＝ (1/π) ∫ V cosθ dω

## 参考

- Landis, "Production-Ready Global Illumination", SIGGRAPH 2002 Course 16（ambient occlusion の、映画制作での、使われ方）
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（Ambient Occlusion の章）
- Kajiya, "The Rendering Equation", SIGGRAPH 1986

## 関連ページ

- [AO Theory](index.md)
- [Obscurance](obscurance.md)
- [GI Theory](../../gi/theory/index.md)
