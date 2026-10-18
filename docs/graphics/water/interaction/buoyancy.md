---
title: Buoyancy and Reaction
tags:
  - 描画
---

# Buoyancy and Reaction

**物が水に浮くには、浮力が必要**で、**水の側も、物から押されて動きます**。このページでは、**浮力の計算と、水への反作用**を説明します。

!!! tip "ポイント"
    - **浮力 ＝ 水に沈んだ体積に比例した、上向きの力**。
    - **物体の数点で、水深を求めて、力を加える**。
    - **水の抵抗（ダンピング）で、揺れが収まる**。
    - **物が水を押す反作用は、高さマップに書く**。

## 浮力と水への反作用
**水面と物の相互作用は、見た目だけでなく、物理にも影響します**。

相互作用の物理の要素です。浮力は、水に浸かった体積に比例します（[Water Waves](../waves/index.md)）。抵抗は、水中を動く物が、速さに比例して減速する効果です。波紋の起点は、物理エンジンの接触や速度から、ブラシの強さを決めます。

<!-- fig:buoyancy-draft:begin -->

<svg class="fig illust motion" data-fig="buoyancy-draft" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-buoyancy-draft" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">浮力は沈んだ体積に比例し、重さと釣り合う深さで止まる</text>
<rect x="70" y="70" width="640" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="230.0" y1="70" x2="230.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="130.0" x2="710" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="70" x2="390.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="190.0" x2="710" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="550.0" y1="70" x2="550.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="250.0" x2="710" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="70" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">力（重さ = 1 とする）</text>
<text x="710" y="346" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">沈んでいる深さ ÷ 箱の高さ</text>
<text x="70.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0</text>
<text x="230.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0.25</text>
<text x="390.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0.5</text>
<text x="550.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">0.75</text>
<text x="710.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">1</text>
<path d="M70.0,138.57 L80.67,138.57 L91.33,138.57 L102.0,138.57 L112.67,138.57 L123.33,138.57 L134.0,138.57 L144.67,138.57 L155.33,138.57 L166.0,138.57 L176.67,138.57 L187.33,138.57 L198.0,138.57 L208.67,138.57 L219.33,138.57 L230.0,138.57 L240.67,138.57 L251.33,138.57 L262.0,138.57 L272.67,138.57 L283.33,138.57 L294.0,138.57 L304.67,138.57 L315.33,138.57 L326.0,138.57 L336.67,138.57 L347.33,138.57 L358.0,138.57 L368.67,138.57 L379.33,138.57 L390.0,138.57 L400.67,138.57 L411.33,138.57 L422.0,138.57 L432.67,138.57 L443.33,138.57 L454.0,138.57 L464.67,138.57 L475.33,138.57 L486.0,138.57 L496.67,138.57 L507.33,138.57 L518.0,138.57 L528.67,138.57 L539.33,138.57 L550.0,138.57 L560.67,138.57 L571.33,138.57 L582.0,138.57 L592.67,138.57 L603.33,138.57 L614.0,138.57 L624.67,138.57 L635.33,138.57 L646.0,138.57 L656.67,138.57 L667.33,138.57 L678.0,138.57 L688.67,138.57 L699.33,138.57 L710.0,138.57" fill="none" stroke="#e5484d" stroke-width="3" opacity="1" stroke-dasharray="6 5"/>
<text x="82.8" y="128.57" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">重さ（下向き）</text>
<path d="M70.0,310.0 L78.0,306.43 L86.0,302.86 L94.0,299.29 L102.0,295.71 L110.0,292.14 L118.0,288.57 L126.0,285.0 L134.0,281.43 L142.0,277.86 L150.0,274.29 L158.0,270.71 L166.0,267.14 L174.0,263.57 L182.0,260.0 L190.0,256.43 L198.0,252.86 L206.0,249.29 L214.0,245.71 L222.0,242.14 L230.0,238.57 L238.0,235.0 L246.0,231.43 L254.0,227.86 L262.0,224.29 L270.0,220.71 L278.0,217.14 L286.0,213.57 L294.0,210.0 L302.0,206.43 L310.0,202.86 L318.0,199.29 L326.0,195.71 L334.0,192.14 L342.0,188.57 L350.0,185.0 L358.0,181.43 L366.0,177.86 L374.0,174.29 L382.0,170.71 L390.0,167.14 L398.0,163.57 L406.0,160.0 L414.0,156.43 L422.0,152.86 L430.0,149.29 L438.0,145.71 L446.0,142.14 L454.0,138.57 L462.0,135.0 L470.0,131.43 L478.0,127.86 L486.0,124.29 L494.0,120.71 L502.0,117.14 L510.0,113.57 L518.0,110.0 L526.0,106.43 L534.0,102.86 L542.0,99.29 L550.0,95.71 L558.0,92.14 L566.0,88.57 L574.0,85.0 L582.0,81.43 L590.0,77.86 L598.0,74.29 L606.0,70.71 L614.0,70.0 L622.0,70.0 L630.0,70.0 L638.0,70.0 L646.0,70.0 L654.0,70.0 L662.0,70.0 L670.0,70.0 L678.0,70.0 L686.0,70.0 L694.0,70.0 L702.0,70.0 L710.0,70.0" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<text x="166.0" y="253.14" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">浮力（上向き）</text>
<circle cx="70.0" cy="310.0" r="7" fill="#1f2937"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0917;0.1033;0.1150;0.1267;0.1383;0.1500;0.1617;0.1733;0.1850;0.1967;0.2083;0.2200;0.2317;0.2433;0.2550;0.2667;0.2783;0.2900;0.3017;0.3133;0.3250;0.3367;0.3483;0.3600;0.3717;0.3833;0.3950;0.4067;0.4183;0.4300;0.4417;0.4533;0.4650;0.4767;0.4883;0.5000;0.5117;0.5233;0.5350;0.5467;0.5583;0.5700;0.5817;0.5933;0.6050;0.6167;0.6283;0.6400;1.0000" values="70;70;78;86;94;102;110;118;126;134;142;150;158;166;174;182;190;198;206;214;222;230;238;246;254;262;270;278;286;294;302;310;318;326;334;342;350;358;366;374;382;390;398;406;414;422;430;438;446;454;454"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0917;0.1033;0.1150;0.1267;0.1383;0.1500;0.1617;0.1733;0.1850;0.1967;0.2083;0.2200;0.2317;0.2433;0.2550;0.2667;0.2783;0.2900;0.3017;0.3133;0.3250;0.3367;0.3483;0.3600;0.3717;0.3833;0.3950;0.4067;0.4183;0.4300;0.4417;0.4533;0.4650;0.4767;0.4883;0.5000;0.5117;0.5233;0.5350;0.5467;0.5583;0.5700;0.5817;0.5933;0.6050;0.6167;0.6283;0.6400;1.0000" values="310;310;306.43;302.86;299.29;295.71;292.14;288.57;285;281.43;277.86;274.29;270.71;267.14;263.57;260;256.43;252.86;249.29;245.71;242.14;238.57;235;231.43;227.86;224.29;220.71;217.14;213.57;210;206.43;202.86;199.29;195.71;192.14;188.57;185;181.43;177.86;174.29;170.71;167.14;163.57;160;156.43;152.86;149.29;145.71;142.14;138.57;138.57"/></circle>
<circle cx="454.0" cy="138.57" r="10" fill="none" stroke="#2ea043" stroke-width="4" opacity="0"><animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6397;0.6400;1.0000" values="0;0;1;1"/></circle>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">箱の密度が、水の 0.6 倍だとする<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">沈めるほど、押し返す力が増える<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.3197;0.3200;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">浮力 &lt; 重さ: まだ沈む<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3197;0.3200;0.6397;0.6400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">深さ 0.6 で浮力 = 重さ → 釣り合って止まる(緑の丸)<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6397;0.6400;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:buoyancy-draft:end -->

## よくあるミス

??? failure "物が、水の上で跳ね続ける"
    **ダンピング**を**加える**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **沈んだ体積に応じた力で浮かせる**

## 参考

- Tessendorf, "Simulating Ocean Water"（SIGGRAPH Course Notes 2001）
- Finch, "Effective Water Simulation from Physical Models"（GPU Gems 2004）
- Vlachos, "Water Flow in Portal 2"（SIGGRAPH 2010）

## 関連ページ

- [Water Interaction](index.md)
- [Floating Objects](../waves/floating.md)
