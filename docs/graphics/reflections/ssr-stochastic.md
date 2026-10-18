---
title: Stochastic SSR
tags:
  - 描画
---

# Stochastic SSR

[SSR の基礎](ssr-basics/index.md)と [Hi-Z SSR](ssr-hiz.md)は、**反射方向 R の、1 本のレイ**を追いました。これは**完全な鏡**の反射です。**粗い面**の反射は、**R の周りのさまざまな方向の景色を、BRDF の重みで平均**したものでした。**確率的 SSR**（Stochastic SSR）は、**BRDF の分布に従って、画素ごとにランダムな方向のレイ**を 1 本だけ飛ばし、**近くの画素のレイの結果を再利用し、時間方向にも平均**して、**ぼけた反射を物理的に正しく**得ます。2015 年に Frostbite の Stachowiak が発表した方式が、現在の SSR の標準的な作り方です。

!!! tip "ポイント"
    - 粗い反射 ＝ <strong>BRDF（GGX）の山の中の様々な方向の景色の平均</strong>。<strong>モンテカルロ法</strong>で近似する。
    - <strong>重要度サンプリング</strong>：<strong>GGX の分布に従って</strong>方向を選ぶ（<strong>可視法線サンプリング、VNDF</strong>）。
    - <strong>1 画素 1 本</strong>（半分の解像度でも可）のレイ。<strong>ノイズだらけ</strong>。
    - <strong>空間再利用</strong>：<strong>近くの画素のレイの当たり点</strong>を、自分の反射の<strong>サンプルとして再利用</strong>（重みで補正）。
    - <strong>時間蓄積</strong>と<strong>バイラテラル フィルタ</strong>で、ノイズを消す。
    - 結果は<strong>BRDF の積分（スケール・バイアス）を掛けて</strong>合成する。

## The Idea: Rough Reflections with Monte Carlo {#発想粗い反射をモンテカルロ法で}

鏡面の出射光は、次の積分でした（[Reflections](index.md)）。

<div class="formula">L_o = ∫ f_spec(ω_i, ω_o) · L_i(ω_i) · (n·ω_i) dω_i</div>

**ω_i を、BRDF の山の形に従ってランダムに選ぶ**（**重要度サンプリング**）と、**サンプルの平均**が積分の近似になります。**1 画素あたり 1 本**のレイを、**画素ごとに異なる方向**に飛ばして、**近くの画素と平均**すれば、**ぼけた反射**が出ます。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="粗さと確率的レイ">
<text x="20" y="24" class="fig-title">粗さに応じて、反射方向の周りの「山」から、ランダムな方向を選ぶ</text>
<line x1="60" y1="220" x2="360" y2="220" stroke="currentColor" stroke-width="4"/>
<circle cx="210" cy="220" r="6" fill="currentColor"/>
<line x1="210" y1="220" x2="210" y2="80" stroke="#2ea043" stroke-width="2" stroke-dasharray="4 3"/><text x="218" y="92" style="font-size:12px;fill:#2ea043">法線 n</text>
<line x1="210" y1="220" x2="320" y2="100" stroke="#e5484d" stroke-width="3"/><text x="324" y="96" style="font-size:12px;fill:#e5484d;font-weight:700">反射方向 R</text>
<g stroke="#4c8bf5" stroke-width="1.8"><line x1="210" y1="220" x2="300" y2="86"/><line x1="210" y1="220" x2="340" y2="115"/><line x1="210" y1="220" x2="335" y2="135"/><line x1="210" y1="220" x2="310" y2="112"/><line x1="210" y1="220" x2="290" y2="104"/></g>
<text x="60" y="250" style="font-size:12px">粗いほど、R の周りに、レイが広く散らばる（青）</text>
<rect x="430" y="60" width="330" height="170" rx="10" fill="rgba(150,150,150,0.12)" stroke="currentColor"/>
<text x="446" y="88" style="font-weight:700">粗さ（ラフネス）</text>
<text x="446" y="114" style="font-size:12px">小さい：R の近くだけ（くっきり反射）</text>
<text x="446" y="136" style="font-size:12px">大きい：広い範囲（ぼけた反射）</text>
<text x="446" y="170" style="font-weight:700">サンプルの選び方</text>
<text x="446" y="194" style="font-size:12px">GGX の分布に従い、「法線 h」をランダムに選ぶ</text>
<text x="446" y="214" style="font-size:12px">→ R = reflect(−V, h)</text>
</svg>

<!-- fig:roughness-lobe:begin -->

<svg class="fig illust motion" data-fig="roughness-lobe" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-roughness-lobe" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">ざらざらした面の反射: 粗さに応じて、光線の向きをばらつかせて平均する(確率的 SSR)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">粗さが上がると、反射の光線が広がる。ばらつかせた光線を少数だけ使うと、ざらつき(ノイズ)が出る</text>
<rect x="30" y="96" width="900" height="170" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 粗さごとの、反射光線の広がり(法線は真上)</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0443;0.0444;1.0000" values="0;0;1;1"/><line x1="60" y1="240.0" x2="240" y2="240.0" stroke="#94a3b8" stroke-width="3"/>
<line x1="150" y1="240.0" x2="145.26" y2="155.13" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="145.19" y2="155.14" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="163.34" y2="156.05" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="158.44" y2="155.42" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="148.02" y2="155.02" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="152.25" y2="155.03" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="141.57" y2="155.42" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="146.46" y2="155.07" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="158.02" y2="155.38" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="171.92" y2="157.88" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="198.99" y2="170.54" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="135.44" y2="156.26" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="160.32" y2="155.63" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="198.91" y2="170.48" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="158.5" y2="155.43" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="150" y1="240.0" x2="144.7" y2="155.17" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<text x="150" y="122" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#7c3aed">粗さ 0.1: 広がり約 14°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1598;0.1600;1.0000" values="0;0;1;1"/><line x1="360" y1="240.0" x2="540" y2="240.0" stroke="#94a3b8" stroke-width="3"/>
<line x1="450" y1="240.0" x2="466.03" y2="156.53" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="529.61" y2="210.21" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="514.19" y2="184.28" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="479.9" y2="160.43" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="386.47" y2="183.52" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="423.94" y2="159.09" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="461.35" y2="155.76" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="459.97" y2="155.59" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="501.48" y2="172.36" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="461.23" y2="155.74" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="464.24" y2="156.2" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="448.3" y2="155.02" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="468.86" y2="157.12" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="414.59" y2="162.73" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="423.73" y2="159.16" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="450" y1="240.0" x2="463.85" y2="156.14" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<text x="450" y="122" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#7c3aed">粗さ 0.4: 広がり約 29°</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2754;0.2756;1.0000" values="0;0;1;1"/><line x1="660" y1="240.0" x2="840" y2="240.0" stroke="#94a3b8" stroke-width="3"/>
<line x1="750" y1="240.0" x2="728.94" y2="157.65" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="670.38" y2="210.24" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="770.91" y2="157.61" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="777.48" y2="159.56" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="730.35" y2="157.3" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="678.29" y2="194.37" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="712.31" y2="163.81" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="830.65" y2="213.16" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="685.18" y2="185.01" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="735.92" y2="156.17" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="833.71" y2="225.24" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="833.71" y2="225.24" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="718.1" y2="161.21" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="782.01" y2="161.26" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="682.67" y2="188.11" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<line x1="750" y1="240.0" x2="692.39" y2="177.5" stroke="#e5484d" stroke-width="1.6" opacity="0.85"/>
<text x="750" y="122" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#7c3aed">粗さ 0.8: 広がり約 47°</text>
</g>
<text x="40" y="296" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">粗さ 0.4 の面に映る縞模様(1 画素ごとに、光線を N 本使って平均)</text>
<text x="40" y="328" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d" opacity="1">N = 1 本</text>
<text x="40" y="368" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28" opacity="1">N = 4 本</text>
<text x="40" y="408" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043" opacity="1">N = 16 本</text>
<rect x="100.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4089" values="#e5e7eb;#262626"/></rect>
<rect x="115.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4102" values="#e5e7eb;#262626"/></rect>
<rect x="130.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4116" values="#e5e7eb;#262626"/></rect>
<rect x="145.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4129" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="160.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4142" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="175.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4156" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="190.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4169" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="205.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4182" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="220.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4196" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="235.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4209" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="250.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4222" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="265.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4236" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="280.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4249" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="295.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4262" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="310.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4276" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="325.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4289" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="340.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4302" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="355.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4316" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="370.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4329" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="385.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4342" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="400.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4356" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="415.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4369" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="430.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4382" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="445.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4396" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="460.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4409" values="#e5e7eb;#262626"/></rect>
<rect x="475.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4422" values="#e5e7eb;#262626"/></rect>
<rect x="490.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4436" values="#e5e7eb;#262626"/></rect>
<rect x="505.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4449" values="#e5e7eb;#262626"/></rect>
<rect x="520.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4462" values="#e5e7eb;#262626"/></rect>
<rect x="535.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4476" values="#e5e7eb;#262626"/></rect>
<rect x="550.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4489" values="#e5e7eb;#262626"/></rect>
<rect x="565.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4502" values="#e5e7eb;#262626"/></rect>
<rect x="580.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4516" values="#e5e7eb;#262626"/></rect>
<rect x="595.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4529" values="#e5e7eb;#262626"/></rect>
<rect x="610.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4542" values="#e5e7eb;#262626"/></rect>
<rect x="625.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4556" values="#e5e7eb;#262626"/></rect>
<rect x="640.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4569" values="#e5e7eb;#262626"/></rect>
<rect x="655.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4582" values="#e5e7eb;#262626"/></rect>
<rect x="670.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4596" values="#e5e7eb;#262626"/></rect>
<rect x="685.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4609" values="#e5e7eb;#262626"/></rect>
<rect x="700.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4622" values="#e5e7eb;#262626"/></rect>
<rect x="715.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4636" values="#e5e7eb;#262626"/></rect>
<rect x="730.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4649" values="#e5e7eb;#262626"/></rect>
<rect x="745.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4662" values="#e5e7eb;#262626"/></rect>
<rect x="760.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4676" values="#e5e7eb;#262626"/></rect>
<rect x="775.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4689" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="790.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4702" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="805.0" y="314.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.4716" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="100.0" y="314" width="720.0" height="15.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="100.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5156" values="#e5e7eb;#262626"/></rect>
<rect x="115.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5169" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="130.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5182" values="#e5e7eb;#565656"/></rect>
<rect x="145.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5196" values="#e5e7eb;#565656"/></rect>
<rect x="160.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5209" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="175.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5222" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="190.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5236" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="205.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5249" values="#e5e7eb;#868686"/></rect>
<rect x="220.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5262" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="235.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5276" values="#e5e7eb;#565656"/></rect>
<rect x="250.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5289" values="#e5e7eb;#565656"/></rect>
<rect x="265.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5302" values="#e5e7eb;#565656"/></rect>
<rect x="280.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5316" values="#e5e7eb;#868686"/></rect>
<rect x="295.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5329" values="#e5e7eb;#565656"/></rect>
<rect x="310.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5342" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="325.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5356" values="#e5e7eb;#868686"/></rect>
<rect x="340.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5369" values="#e5e7eb;#565656"/></rect>
<rect x="355.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5382" values="#e5e7eb;#565656"/></rect>
<rect x="370.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5396" values="#e5e7eb;#262626"/></rect>
<rect x="385.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5409" values="#e5e7eb;#868686"/></rect>
<rect x="400.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5422" values="#e5e7eb;#565656"/></rect>
<rect x="415.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5436" values="#e5e7eb;#565656"/></rect>
<rect x="430.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5449" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="445.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5462" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="460.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5476" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="475.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5489" values="#e5e7eb;#868686"/></rect>
<rect x="490.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5502" values="#e5e7eb;#868686"/></rect>
<rect x="505.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5516" values="#e5e7eb;#262626"/></rect>
<rect x="520.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5529" values="#e5e7eb;#565656"/></rect>
<rect x="535.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5542" values="#e5e7eb;#262626"/></rect>
<rect x="550.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5556" values="#e5e7eb;#262626"/></rect>
<rect x="565.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5569" values="#e5e7eb;#868686"/></rect>
<rect x="580.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5582" values="#e5e7eb;#565656"/></rect>
<rect x="595.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5596" values="#e5e7eb;#868686"/></rect>
<rect x="610.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5609" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="625.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5622" values="#e5e7eb;#868686"/></rect>
<rect x="640.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5636" values="#e5e7eb;#868686"/></rect>
<rect x="655.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5649" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="670.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5662" values="#e5e7eb;#868686"/></rect>
<rect x="685.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5676" values="#e5e7eb;#868686"/></rect>
<rect x="700.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5689" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="715.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5702" values="#e5e7eb;#e6e6e6"/></rect>
<rect x="730.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5716" values="#e5e7eb;#868686"/></rect>
<rect x="745.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5729" values="#e5e7eb;#868686"/></rect>
<rect x="760.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5742" values="#e5e7eb;#565656"/></rect>
<rect x="775.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5756" values="#e5e7eb;#868686"/></rect>
<rect x="790.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5769" values="#e5e7eb;#262626"/></rect>
<rect x="805.0" y="354.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.5782" values="#e5e7eb;#262626"/></rect>
<rect x="100.0" y="354" width="720.0" height="15.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<rect x="100.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6222" values="#e5e7eb;#868686"/></rect>
<rect x="115.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6236" values="#e5e7eb;#aaaaaa"/></rect>
<rect x="130.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6249" values="#e5e7eb;#868686"/></rect>
<rect x="145.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6262" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="160.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6276" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="175.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6289" values="#e5e7eb;#929292"/></rect>
<rect x="190.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6302" values="#e5e7eb;#929292"/></rect>
<rect x="205.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6316" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="220.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6329" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="235.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6342" values="#e5e7eb;#929292"/></rect>
<rect x="250.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6356" values="#e5e7eb;#868686"/></rect>
<rect x="265.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6369" values="#e5e7eb;#929292"/></rect>
<rect x="280.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6382" values="#e5e7eb;#b6b6b6"/></rect>
<rect x="295.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6396" values="#e5e7eb;#c2c2c2"/></rect>
<rect x="310.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6409" values="#e5e7eb;#9e9e9e"/></rect>
<rect x="325.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6422" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="340.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6436" values="#e5e7eb;#9e9e9e"/></rect>
<rect x="355.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6449" values="#e5e7eb;#929292"/></rect>
<rect x="370.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6462" values="#e5e7eb;#929292"/></rect>
<rect x="385.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6476" values="#e5e7eb;#868686"/></rect>
<rect x="400.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6489" values="#e5e7eb;#929292"/></rect>
<rect x="415.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6502" values="#e5e7eb;#929292"/></rect>
<rect x="430.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6516" values="#e5e7eb;#929292"/></rect>
<rect x="445.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6529" values="#e5e7eb;#626262"/></rect>
<rect x="460.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6542" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="475.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6556" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="490.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6569" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="505.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6582" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="520.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6596" values="#e5e7eb;#626262"/></rect>
<rect x="535.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6609" values="#e5e7eb;#868686"/></rect>
<rect x="550.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6622" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="565.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6636" values="#e5e7eb;#4a4a4a"/></rect>
<rect x="580.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6649" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="595.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6662" values="#e5e7eb;#868686"/></rect>
<rect x="610.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6676" values="#e5e7eb;#565656"/></rect>
<rect x="625.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6689" values="#e5e7eb;#929292"/></rect>
<rect x="640.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6702" values="#e5e7eb;#868686"/></rect>
<rect x="655.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6716" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="670.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6729" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="685.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6742" values="#e5e7eb;#868686"/></rect>
<rect x="700.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6756" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="715.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6769" values="#e5e7eb;#9e9e9e"/></rect>
<rect x="730.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6782" values="#e5e7eb;#6e6e6e"/></rect>
<rect x="745.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6796" values="#e5e7eb;#929292"/></rect>
<rect x="760.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6809" values="#e5e7eb;#929292"/></rect>
<rect x="775.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6822" values="#e5e7eb;#868686"/></rect>
<rect x="790.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6836" values="#e5e7eb;#929292"/></rect>
<rect x="805.0" y="394.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.6849" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="100.0" y="394" width="720.0" height="15.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="40" y="440" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">基準(512 本)</text>
<rect x="100.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7289" values="#e5e7eb;#7e7e7e"/></rect>
<rect x="115.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7302" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="130.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7316" values="#e5e7eb;#7e7e7e"/></rect>
<rect x="145.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7329" values="#e5e7eb;#878787"/></rect>
<rect x="160.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7342" values="#e5e7eb;#838383"/></rect>
<rect x="175.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7356" values="#e5e7eb;#8e8e8e"/></rect>
<rect x="190.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7369" values="#e5e7eb;#8d8d8d"/></rect>
<rect x="205.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7382" values="#e5e7eb;#939393"/></rect>
<rect x="220.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7396" values="#e5e7eb;#8e8e8e"/></rect>
<rect x="235.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7409" values="#e5e7eb;#919191"/></rect>
<rect x="250.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7422" values="#e5e7eb;#969696"/></rect>
<rect x="265.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7436" values="#e5e7eb;#929292"/></rect>
<rect x="280.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7449" values="#e5e7eb;#969696"/></rect>
<rect x="295.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7462" values="#e5e7eb;#9a9a9a"/></rect>
<rect x="310.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7476" values="#e5e7eb;#999999"/></rect>
<rect x="325.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7489" values="#e5e7eb;#929292"/></rect>
<rect x="340.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7502" values="#e5e7eb;#9c9c9c"/></rect>
<rect x="355.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7516" values="#e5e7eb;#8e8e8e"/></rect>
<rect x="370.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7529" values="#e5e7eb;#919191"/></rect>
<rect x="385.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7542" values="#e5e7eb;#959595"/></rect>
<rect x="400.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7556" values="#e5e7eb;#939393"/></rect>
<rect x="415.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7569" values="#e5e7eb;#919191"/></rect>
<rect x="430.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7582" values="#e5e7eb;#8a8a8a"/></rect>
<rect x="445.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7596" values="#e5e7eb;#878787"/></rect>
<rect x="460.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7609" values="#e5e7eb;#818181"/></rect>
<rect x="475.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7622" values="#e5e7eb;#7d7d7d"/></rect>
<rect x="490.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7636" values="#e5e7eb;#7c7c7c"/></rect>
<rect x="505.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7649" values="#e5e7eb;#7f7f7f"/></rect>
<rect x="520.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7662" values="#e5e7eb;#7d7d7d"/></rect>
<rect x="535.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7676" values="#e5e7eb;#7e7e7e"/></rect>
<rect x="550.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7689" values="#e5e7eb;#7d7d7d"/></rect>
<rect x="565.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7702" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="580.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7716" values="#e5e7eb;#7a7a7a"/></rect>
<rect x="595.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7729" values="#e5e7eb;#707070"/></rect>
<rect x="610.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7742" values="#e5e7eb;#747474"/></rect>
<rect x="625.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7756" values="#e5e7eb;#717171"/></rect>
<rect x="640.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7769" values="#e5e7eb;#777777"/></rect>
<rect x="655.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7782" values="#e5e7eb;#737373"/></rect>
<rect x="670.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7796" values="#e5e7eb;#7f7f7f"/></rect>
<rect x="685.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7809" values="#e5e7eb;#7b7b7b"/></rect>
<rect x="700.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7822" values="#e5e7eb;#747474"/></rect>
<rect x="715.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7836" values="#e5e7eb;#808080"/></rect>
<rect x="730.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7849" values="#e5e7eb;#7d7d7d"/></rect>
<rect x="745.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7862" values="#e5e7eb;#7e7e7e"/></rect>
<rect x="760.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7876" values="#e5e7eb;#7d7d7d"/></rect>
<rect x="775.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7889" values="#e5e7eb;#888888"/></rect>
<rect x="790.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7902" values="#e5e7eb;#8a8a8a"/></rect>
<rect x="805.0" y="426.0" width="15.3" height="15.3" fill="#e5e7eb"><animate attributeName="fill" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.7916" values="#e5e7eb;#868686"/></rect>
<rect x="100.0" y="426" width="720.0" height="15.0" fill="none" stroke="#94a3b8" stroke-width="1.5"/>
<text x="940" y="330" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">基準とのずれ 0.334<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4798;0.4800;1.0000" values="0;0;1;1"/></text>
<text x="940" y="370" text-anchor="end" style="font-size:12px;font-weight:700;fill:#e5aa28" opacity="0">基準とのずれ 0.190<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5865;0.5867;1.0000" values="0;0;1;1"/></text>
<text x="940" y="410" text-anchor="end" style="font-size:12px;font-weight:700;fill:#2ea043" opacity="0">基準とのずれ 0.061<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6932;0.6933;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8087;0.8089;1.0000" values="0;0;1;1"/><rect x="560" y="462" width="370" height="60" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="576" y="486" text-anchor="start" style="font-size:15px;font-weight:700;fill:#166534">1 本 → 16 本で、ずれは 5.5 分の 1</text>
<text x="576" y="510" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">本数を増やすほど、きれい。代わりに、読み込みが増える</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">粗い面は、いろいろな向きから、光を集める<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0443;0.0444;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">粗さに応じて、光線の向きを確率的にばらつかせる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0443;0.0444;0.4087;0.4089;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">1 画素あたり少数の光線で平均すると、ざらつくので、フレームをまたいで混ぜて消す<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4087;0.4089;0.8087;0.8089;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">(光線を増やす代わりに、TAA やぼかしで、ノイズを消すのが一般的)<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8087;0.8089;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:roughness-lobe:end -->

## GGX Distribution and Importance Sampling {#ggx-分布と重要度サンプリング}

**GGX**（Trowbridge-Reitz）は、<strong>微小な面の向き（ハーフベクトル h）の分布 D(h)</strong> を表す、**標準的な式**です。

<div class="formula">D(h) = α² / ( π · ( (n·h)² (α² − 1) + 1 )² )　、　α = roughness²</div>

記号の意味です。α は粗さのパラメータ（`roughness²` が一般的）です。n·h は法線とハーフベクトルのコサインで、1 に近いほど D が大きくなります（山の頂上）。

### Generating Sample Directions {#サンプルの方向を作る}

**ランダムな h** を、**D(h) に比例する確率**で選べば、**効率のよい（分散の小さい）サンプル**になります。**反射方向 L は `reflect(−V, h)`** です。

ランダムな h を D(h) に比例する確率で選ぶと、効率のよい（分散の小さい）サンプルになります。手順は 3 つです。GGX の分布（あるいは可視法線の分布）から、ランダムに h を選びます。反射方向を `L = reflect(−V, h)` で作ります。最後に、`L·N < 0`（面の裏側）なら無効とし、再サンプルするか、寄与を 0 にします。

### Visible Normal Sampling (VNDF) {#可視法線サンプリングvndf}

素朴な GGX サンプリングは、**視線から見えない向き**（裏向きの微小面）も選んで**無駄**（無効なレイ）が多くなります。<strong>可視法線の分布（VNDF）</strong>は、**視線 V から見える向きだけ**を、確率的に選ぶので**無駄が少なく、ノイズが小さい**です（Heitz, 2018）。

```hlsl
float3 SampleGGXVNDF(float3 view_ts, float alpha, float2 u) {
  float3 vh = normalize(float3(alpha * view_ts.x, alpha * view_ts.y, view_ts.z));

  float len_sq = vh.x * vh.x + vh.y * vh.y;
  float3 t1 = len_sq > 0.0 ? float3(-vh.y, vh.x, 0.0) * rsqrt(len_sq) : float3(1, 0, 0);
  float3 t2 = cross(vh, t1);

  float r = sqrt(u.x);
  float phi = 6.2831853 * u.y;
  float p1 = r * cos(phi);
  float p2 = r * sin(phi);
  float s = 0.5 * (1.0 + vh.z);
  p2 = (1.0 - s) * sqrt(1.0 - p1 * p1) + s * p2;

  float3 nh = p1 * t1 + p2 * t2 + sqrt(max(0.0, 1.0 - p1 * p1 - p2 * p2)) * vh;
  return normalize(float3(alpha * nh.x, alpha * nh.y, max(0.0, nh.z)));
}
```

| 点 | 説明 |
| --- | --- |
| **`view_ts`** | **接空間**での視線ベクトル（法線を z 軸とする座標系） |
| **`u`** | 2 つの一様乱数（画素・フレームごとに変える） |
| **戻り値** | 接空間での**ハーフベクトル h** |
| **接空間 → ワールド** | TBN（法線から作る）で、ワールドの h に |

**確率密度**（レイの方向 L に対する）は、次のとおりです（重み付けに使う）。

<div class="formula">pdf(L) = D_V(h) / (4 · (V·h))　、　D_V(h) = G1(V) · max(0, V·h) · D(h) / (n·V)</div>

式の項は、次のとおりです。G1(V) は、視線方向の遮蔽関数（Smith の G1）で、見える割合を表します。`4 (V·h)` は、h の分布から反射方向 L の分布へ変換する係数（ヤコビアン）です。

## Overall Flow {#全体の流れ}

| パス | 内容 |
| --- | --- |
| **① レイ生成** | **1 画素 1 本**（半分の解像度のことも）。**粗さに応じた GGX VNDF** で、方向を選ぶ |
| **② Hi-Z トレース** | レイを進めて、<strong>当たり点（位置・距離）</strong>を求める（[Hi-Z SSR](ssr-hiz.md)） |
| **③ 色の取得** | 当たり点の色（前フレームの HDR、動きベクトルで再投影） |
| **④ 空間リゾルブ** | **近隣画素のレイ**を再利用して、各画素の反射を再構成（下記） |
| **⑤ 時間蓄積** | 過去フレームと混ぜる |
| **⑥ バイラテラル フィルタ** | 粗さ・深度・法線を考慮して、ノイズを消す |
| **⑦ 合成** | <strong>BRDF の積分（スケール・バイアス）</strong>を掛け、**フォールバックと混ぜる** |

## Spatial Resolve: Reusing Neighboring Rays {#空間リゾルブ近隣のレイの再利用}

**1 画素 1 本**のレイでは、ノイズが大きすぎます。**近隣の画素（たとえば 4〜9 個）が、それぞれ飛ばしたレイの当たり点**を、**自分のサンプルとして再利用**します。

**近隣の画素 j のレイが、当たり点 H_j を持つ**とします。**自分（画素 i）から見た H_j への方向 L**は、`L = normalize(H_j − P_i)` です。**この L は自分の BRDF から見て、どれくらいありえる方向か**で、サンプルを**重み付け**します。

<div class="formula">L_o(i) ≈ Σ_j w_j · Color(H_j) / Σ_j w_j　、　w_j = f_spec,i(L_j) · (n_i·L_j) / pdf_j(L_j)</div>

式の項です。f_spec,i(L_j) は、自分の BRDF で方向 L_j を評価した値です。pdf_j(L_j) は、そのレイを生成した画素 j の確率密度、つまり画素 j の法線・粗さ・視線から求めた、その方向に飛ぶ確率です。重み w_j は、<strong>「自分にとっての価値」を「j がその方向を選ぶ確率」で割った値</strong>で、重要度の補正になります。

つまり、**他の画素が選んだレイを、自分にとって妥当な方向として、「借りて」きて**、**確率の違いを重みで補正**しています。**1 画素 1 本のレイが、実質 4〜9 本分**になり、**ノイズが大きく減ります**。

```hlsl
float4 ResolveSpatial(int2 pixel) {
  float3 p = ViewPosition(pixel);
  float3 n = ViewNormal(pixel);
  float3 v = -normalize(p);
  float roughness = Roughness(pixel);

  float4 sum = 0;
  float weight_sum = 0;
  for (int i = 0; i < kNeighborCount; ++i) {
    int2 neighbor = pixel + kOffsets[i];
    float4 ray = ray_hit_tex.Load(int3(neighbor, 0));
    float3 hit_vs = ray.xyz;
    float neighbor_pdf = ray.w;

    float3 l = normalize(hit_vs - p);
    float weight = SpecularBRDF(n, v, l, roughness) * saturate(dot(n, l)) / max(neighbor_pdf, 1e-5);

    sum += float4(HitColor(neighbor), 1.0) * weight;
    weight_sum += weight;
  }
  return sum / max(weight_sum, 1e-5);
}
```

| 点 | 説明 |
| --- | --- |
| **`kOffsets`** | 近隣のオフセット（4〜9 個。**画素ごとにパターンを回す**） |
| **当たり点とその pdf を保存** | レイ生成パスで**当たり位置と確率密度**を書き出しておく |
| **`HitColor`** | 近隣の当たり点の色（前フレームから取得済み） |
| **有効性** | **深度・法線が近くない**近隣は除外（別の面） |
| **サンプルの偏り** | 大きな近隣の範囲（ぼけすぎ）を避けるため、**範囲は小さく** |

## Temporal Accumulation {#時間蓄積}

**フレームごとにランダムな方向**を変えて、**過去のフレームと平均**します。

| 要素 | 内容 |
| --- | --- |
| **再投影** | **今の画素の位置**を前フレームの画面へ。**動きベクトル** |
| **反射の再投影** | **鏡面反射**は**映っている物の動き**に従う。**反射した当たり点**（仮想的な位置）を使って、再投影する |
| **履歴の検証** | 深度・法線・**粗さ**が近いか |
| **混合係数** | `α = 0.05〜0.2`（粗い面ほど、強く蓄積できる） |
| **近傍クランプ** | **周囲の画素の範囲**に履歴を制限して、ゴーストを防ぐ |

**粗い面**は**反射がぼけている**ので**少々のずれは目立たず**、**強く蓄積**できます。**鏡面に近い面**は、**くっきり**しているので**ずれ（ゴースト）が目立ち**、**慎重に**扱います。

### Motion of Reflections (Virtual Position) {#反射の動き仮想的な位置}

反射像は**表面の動きと映っている物の動きとカメラの動き**で**複雑に動き**ます。**表面の動きだけ**で再投影すると、**反射像が引きずられます**。

再投影の方法は、反射の種類で変わります。表面の動きベクトルは、粗い反射には十分ですが、鏡面に近いとゴーストが出ます。当たり点の動き（レイの先の動き）を使うと、鏡面反射でも映った物体の動きに追従します。仮想的な位置（反射像が鏡の向こうに見える位置）を使う方法は、鏡面反射に最適ですが、複雑です。

## Filtering and Denoising {#フィルタとノイズ除去}

リゾルブと時間蓄積のあとも、**ノイズが残る**ことがあります。**空間フィルタ**（バイラテラル）で、**さらに滑らか**にします。

| 工夫 | 内容 |
| --- | --- |
| **粗さに比例した、フィルタの大きさ** | **粗いほど、広くぼかす**（反射がもともとぼけているため） |
| **深度・法線の重み** | 境界をまたがない |
| **ホタル（極端に明るい点）の除去** | **色の上限**（輝度クランプ）、**外れ値の除去** |
| **解像度を下げて計算** | 粗い反射は半分・4 分の 1 でも十分 |

## Multiplying by the BRDF Integral {#brdf-の積分を掛ける}

確率的 SSR の出力は、<strong>「その方向の景色の（重み付き）平均」</strong>です。**反射の最終的な明るさ**には、**BRDF の積分**（Split-Sum の第 2 項）を掛けます（[プローブ](probes/index.md)）。

```hlsl
float2 brdf = brdf_lut.Sample(linear_sampler, float2(n_dot_v, roughness)).rg;
float3 F0 = lerp(0.04, albedo, metallic);
float3 specular = ssr_color * (F0 * brdf.x + brdf.y);
```

**プローブ**で使うのと**同じ式**なので、**SSR とプローブを同じ調子で混ぜられます**（[フォールバック](ssr-fallback.md)）。

## Tuning Cost and Quality {#コストと品質の調整}

| 設定 | 品質への影響 | コスト |
| --- | --- | --- |
| **レイの解像度**（フル・半分・4 分の 1） | 下げるとにじむ | 大きく減る |
| **近隣の数**（リゾルブ） | 増やすとノイズが減る・ぼけが増える | 少し増える |
| **時間蓄積の強さ** | 強いと滑らかだが遅れる | ほぼ無し |
| **最大レイ長・Hi-Z 反復数** | 長いと遠くの映り込み | 増える |
| **粗さの上限** | これ以上の粗さは、SSR をやめる（プローブへ） | 大きく減る |

## Pros and Cons {#長所と短所}

| 長所 | 短所 |
| --- | --- |
| **粗さに応じた、物理的に正しいぼけ** | **ノイズ**が大きく、**フィルタが必須** |
| **1 画素 1 本のレイで済む** | **ゴースト・遅れ**（時間蓄積） |
| **粗さの全域を 1 つの仕組みで**扱える | **実装が複雑**（レイ・リゾルブ・時間・フィルタ・合成） |
| **レイトレ反射とほぼ同じ構造**（デノイズなど） | 画面外・裏側が映らない限界は同じ |


原典は、Stachowiak と Uludag の "Stochastic Screen-Space Reflections"（SIGGRAPH 2015、Frostbite）と、Heitz の可視法線サンプリング（2018）です。

原典は、Stachowiak と Uludag の "Stochastic Screen-Space Reflections"（SIGGRAPH 2015、Frostbite）と、Heitz の可視法線サンプリング（2018）です。

## Common Mistakes {#よくあるミス}

??? failure "GGX のサンプリングで、裏向き（地平線の下）のレイを使って、暗い縞・ノイズ"
    `L·N < 0` を**無効**にします。**VNDF** で無駄を減らします。

??? failure "近隣のレイを再利用するとき、pdf で割らず、偏りが出る"
    **レイを生成した画素の pdf** で、重みを補正します。

??? failure "鏡面に近い面に、強い時間蓄積をして、ゴーストが出る"
    **粗さに応じて**蓄積の強さを変える。**反射の動き**で再投影する。

??? failure "ホタル（極端に明るい点）が、ノイズ除去後も残る"
    **輝度クランプ**、**外れ値の除去**を入れます。

??? failure "BRDF の積分（スケール・バイアス）を掛け忘れて、反射が明るすぎる・暗すぎる"
    Split-Sum の第 2 項を、掛けます。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] 確率的 SSR ＝ <strong>粗さに合わせた GGX（VNDF）で、画素ごとにランダムなレイを 1 本飛ばす</strong>
    - [x] <strong>近隣の画素のレイを再利用</strong>（<strong>重み ＝ BRDF ÷ そのレイの pdf</strong>）して、ノイズを減らす
    - [x] <strong>時間蓄積</strong>（粗いほど強く）と<strong>バイラテラル</strong>でさらに滑らかに
    - [x] <strong>BRDF の積分（スケール・バイアス）</strong>を掛けて、<strong>プローブと同じ調子</strong>で合成
    - [x] レイトレ反射と、<strong>ほぼ同じ構造</strong>（レイ生成 → 当たり → デノイズ）

## References {#参考}

- Stachowiak, Uludag, "Stochastic Screen-Space Reflections"（SIGGRAPH 2015 Advances in Real-Time Rendering、Frostbite）
- Heitz, "Sampling the GGX Distribution of Visible Normals"（Journal of Computer Graphics Techniques, 2018）

## Related Pages {#関連ページ}

- [Reflections](index.md)
- [Hi-Z SSR](ssr-hiz.md)
- [SSR Fallback and Compositing](ssr-fallback.md)
- [レイトレース反射](rt-reflections/index.md)
- [PBR](../../3d/pbr.md)
- [AO Filtering](../ao/filtering/index.md)
