---
title: VSM, ESM and MSM
tags:
  - 描画
---

# VSM, ESM and MSM

**通常のシャドウ マップは、深度を比べる「0 か 1」の判定**なので、**そのままぼかす（フィルタする）と、深度の平均になってしまい、正しい影になりません**。**VSM 系は、深度でなく「深度の統計（平均と二乗の平均）」を保存**し、**統計から「影の割合」を計算する**ことで、**シャドウ マップ自体をフィルタ（ぼかし）できます**。**柔らかい影が安く得られる**反面、**光漏れ**という**独特の欠点**があります。このセクションでは、**VSM の仕組み・光漏れ・ESM・EVSM・MSM・比較**を、**1 つずつ別のページ**で説明します。

!!! tip "ポイント"
    - **VSM ＝ 深度の平均と二乗の平均を保存**。**チェビシェフの不等式で、影の割合を計算**。
    - **シャドウ マップを、ガウス・ミップなどで、普通にフィルタ**できる。
    - **弱点は光漏れ**（**影の中に光が漏れる**）。
    - **ESM・EVSM・MSM**は**光漏れを抑える改良版**。

## 発想：深度でなく、統計を保存する
PCF が**平均できない**理由は、**深度を平均してから比べると、誤る**ことでした。VSM は<strong>「ある範囲の深度の分布」</strong>を、**平均 μ と 2 乗平均**の 2 つの数で、**保存**します。**これらは平均（ぼかし）しても意味が保たれる**量です。

保存する量は 2 つです。M₁ = E[z] は深度の平均、M₂ = E[z²] は深度の 2 乗の平均です。この 2 つから、分散 σ² = M₂ − M₁² が求まります。

**分散** は次のとおりです。

<div class="formula">σ² = M₂ − M₁²</div>

シャドウ マップに**深度 z と z² を書き**、<strong>ぼかし（平均）</strong>をすれば、**範囲の M₁・M₂** が得られます。**ぼかしても統計としての意味が保たれる**のがポイントです。

<!-- fig:vsm-chebyshev:begin -->

<svg class="fig illust motion" data-fig="vsm-chebyshev" viewBox="0 0 780 400" role="img"><rect x="0" y="0" width="780" height="400" rx="14" fill="#ffffff"/>
<defs><marker id="arr-vsm-chebyshev" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">VSM:平均と分散から、「光が届く割合の上限」を求める</text>
<rect x="60" y="80" width="460" height="230" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="175.0" y1="80" x2="175.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="137.5" x2="520" y2="137.5" stroke="#e2e8f0" stroke-width="1"/>
<line x1="290.0" y1="80" x2="290.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="195.0" x2="520" y2="195.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="405.0" y1="80" x2="405.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="252.5" x2="520" y2="252.5" stroke="#e2e8f0" stroke-width="1"/>
<text x="520" y="330" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">受け手の深度 t</text>
<text x="60" y="72" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">光が届く割合 p</text>
<path d="M60.0,80.0 L64.6,80.0 L69.2,80.0 L73.8,80.0 L78.4,80.0 L83.0,80.0 L87.6,80.0 L92.2,80.0 L96.8,80.0 L101.4,80.0 L106.0,80.0 L110.6,80.0 L115.2,80.0 L119.8,80.0 L124.4,80.0 L129.0,80.0 L133.6,80.0 L138.2,80.0 L142.8,80.0 L147.4,80.0 L152.0,80.0 L156.6,80.0 L161.2,80.0 L165.8,80.0 L170.4,80.0 L175.0,80.0 L179.6,80.0 L184.2,80.0 L188.8,80.0 L193.4,80.0 L198.0,80.0 L202.6,80.0 L207.2,80.0 L211.8,80.0 L216.4,80.0 L221.0,80.0 L225.6,80.0 L230.2,80.0 L234.8,80.0 L239.4,80.0 L244.0,80.0 L248.6,80.0 L253.2,80.0 L257.8,80.0 L262.4,80.0 L267.0,80.0 L271.6,80.0 L276.2,80.0 L280.8,80.0 L285.4,80.0 L290.0,80.0 L294.6,81.9 L299.2,87.42 L303.8,96.05 L308.4,107.06 L313.0,119.66 L317.6,133.08 L322.2,146.69 L326.8,160.0 L331.4,172.69 L336.0,184.55 L340.6,195.48 L345.2,205.45 L349.8,214.5 L354.4,222.66 L359.0,230.0 L363.6,236.6 L368.2,242.52 L372.8,247.84 L377.4,252.62 L382.0,256.92 L386.6,260.8 L391.2,264.3 L395.8,267.47 L400.4,270.34 L405.0,272.95 L409.6,275.33 L414.2,277.49 L418.8,279.47 L423.4,281.28 L428.0,282.94 L432.6,284.47 L437.2,285.87 L441.8,287.17 L446.4,288.37 L451.0,289.48 L455.6,290.51 L460.2,291.46 L464.8,292.35 L469.4,293.18 L474.0,293.95 L478.6,294.68 L483.2,295.35 L487.8,295.98 L492.4,296.58 L497.0,297.13 L501.6,297.66 L506.2,298.15 L510.8,298.61 L515.4,299.05 L520.0,299.47" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<path d="M60.0,310.0 L64.6,310.0 L69.2,310.0 L73.8,309.99 L78.4,309.99 L83.0,309.98 L87.6,309.98 L92.2,309.97 L96.8,309.96 L101.4,309.94 L106.0,309.91 L110.6,309.88 L115.2,309.83 L119.8,309.77 L124.4,309.68 L129.0,309.58 L133.6,309.43 L138.2,309.25 L142.8,309.02 L147.4,308.72 L152.0,308.35 L156.6,307.89 L161.2,307.33 L165.8,306.64 L170.4,305.81 L175.0,304.82 L179.6,303.65 L184.2,302.28 L188.8,300.68 L193.4,298.85 L198.0,296.78 L202.6,294.45 L207.2,291.85 L211.8,289.0 L216.4,285.91 L221.0,282.59 L225.6,279.07 L230.2,275.38 L234.8,271.58 L239.4,267.72 L244.0,263.85 L248.6,260.05 L253.2,256.39 L257.8,252.93 L262.4,249.75 L267.0,246.92 L271.6,244.51 L276.2,242.58 L280.8,241.16 L285.4,240.29 L290.0,240.0 L294.6,240.29 L299.2,241.16 L303.8,242.58 L308.4,244.51 L313.0,246.92 L317.6,249.75 L322.2,252.93 L326.8,256.39 L331.4,260.05 L336.0,263.85 L340.6,267.72 L345.2,271.58 L349.8,275.38 L354.4,279.07 L359.0,282.59 L363.6,285.91 L368.2,289.0 L372.8,291.85 L377.4,294.45 L382.0,296.78 L386.6,298.85 L391.2,300.68 L395.8,302.28 L400.4,303.65 L405.0,304.82 L409.6,305.81 L414.2,306.64 L418.8,307.33 L423.4,307.89 L428.0,308.35 L432.6,308.72 L437.2,309.02 L441.8,309.25 L446.4,309.43 L451.0,309.58 L455.6,309.68 L460.2,309.77 L464.8,309.83 L469.4,309.88 L474.0,309.91 L478.6,309.94 L483.2,309.96 L487.8,309.97 L492.4,309.98 L497.0,309.98 L501.6,309.99 L506.2,309.99 L510.8,310.0 L515.4,310.0 L520.0,310.0" fill="#bfdbfe" fill-opacity="0.6" stroke="#7c3aed" stroke-width="2"/>
<text x="290.0" y="232" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#7c3aed">保存した深度の分布（平均 μ、分散 σ²）</text>
<line x1="290.0" y1="80" x2="290.0" y2="310" stroke="#7c3aed" stroke-width="1.5" stroke-dasharray="4 3"/>
<circle cx="152.0" cy="80.0" r="7" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0889;0.1137;0.1386;0.1634;0.1883;0.2131;0.2380;0.2629;0.2877;0.3126;0.3374;0.3623;0.3871;0.4120;0.4369;0.4617;0.4866;0.5114;0.5363;0.5611;0.5860;0.6109;0.6357;0.6606;0.6854;0.7103;0.7351;0.7600;1.0000" values="152;152;163.5;175;186.5;198;209.5;221;232.5;244;255.5;267;278.5;290;301.5;313;324.5;336;347.5;359;370.5;382;393.5;405;416.5;428;439.5;451;462.5;474;474"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0889;0.1137;0.1386;0.1634;0.1883;0.2131;0.2380;0.2629;0.2877;0.3126;0.3374;0.3623;0.3871;0.4120;0.4369;0.4617;0.4866;0.5114;0.5363;0.5611;0.5860;0.6109;0.6357;0.6606;0.6854;0.7103;0.7351;0.7600;1.0000" values="80;80;80;80;80;80;80;80;80;80;80;80;80;80;91.39;119.66;153.4;184.55;210.09;230;245.25;256.92;265.93;272.95;278.5;282.94;286.54;289.48;291.92;293.95;293.95"/></circle>
<line x1="152.0" y1="80" x2="152.0" y2="310" stroke="#e5aa28" stroke-width="2.5"><animate attributeName="x1" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0889;0.1137;0.1386;0.1634;0.1883;0.2131;0.2380;0.2629;0.2877;0.3126;0.3374;0.3623;0.3871;0.4120;0.4369;0.4617;0.4866;0.5114;0.5363;0.5611;0.5860;0.6109;0.6357;0.6606;0.6854;0.7103;0.7351;0.7600;1.0000" values="152;152;163.5;175;186.5;198;209.5;221;232.5;244;255.5;267;278.5;290;301.5;313;324.5;336;347.5;359;370.5;382;393.5;405;416.5;428;439.5;451;462.5;474;474"/><animate attributeName="x2" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0889;0.1137;0.1386;0.1634;0.1883;0.2131;0.2380;0.2629;0.2877;0.3126;0.3374;0.3623;0.3871;0.4120;0.4369;0.4617;0.4866;0.5114;0.5363;0.5611;0.5860;0.6109;0.6357;0.6606;0.6854;0.7103;0.7351;0.7600;1.0000" values="152;152;163.5;175;186.5;198;209.5;221;232.5;244;255.5;267;278.5;290;301.5;313;324.5;336;347.5;359;370.5;382;393.5;405;416.5;428;439.5;451;462.5;474;474"/></line>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.20<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.0885;0.0889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.23<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0885;0.0889;0.1134;0.1137;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.25<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1134;0.1137;0.1383;0.1386;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.28<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1383;0.1386;0.1631;0.1634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.30<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1631;0.1634;0.1880;0.1883;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.33<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1880;0.1883;0.2128;0.2131;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.35<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2128;0.2131;0.2377;0.2380;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.38<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2377;0.2380;0.2625;0.2629;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.40<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2625;0.2629;0.2874;0.2877;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.43<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2874;0.2877;0.3123;0.3126;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.45<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3123;0.3126;0.3371;0.3374;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.47<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3371;0.3374;0.3620;0.3623;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.50<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3620;0.3623;0.3868;0.3871;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.53<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3868;0.3871;0.4117;0.4120;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.55<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4117;0.4120;0.4365;0.4369;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.57<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4365;0.4369;0.4614;0.4617;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.60<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4614;0.4617;0.4863;0.4866;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.62<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4863;0.4866;0.5111;0.5114;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.65<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5111;0.5114;0.5360;0.5363;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.68<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5360;0.5363;0.5608;0.5611;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.70<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5608;0.5611;0.5857;0.5860;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.73<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5857;0.5860;0.6105;0.6109;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.75<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6105;0.6109;0.6354;0.6357;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.77<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6354;0.6357;0.6603;0.6606;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.80<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6603;0.6606;0.6851;0.6854;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.82<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6851;0.6854;0.7100;0.7103;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.85<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7100;0.7103;0.7348;0.7351;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="130" text-anchor="start" style="font-size:20px;font-weight:700;fill:#1f2937" opacity="0">t = 0.88<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7348;0.7351;0.7597;0.7600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.0885;0.0889;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0885;0.0889;0.1134;0.1137;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1134;0.1137;0.1383;0.1386;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1383;0.1386;0.1631;0.1634;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1631;0.1634;0.1880;0.1883;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1880;0.1883;0.2128;0.2131;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2128;0.2131;0.2377;0.2380;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2377;0.2380;0.2625;0.2629;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2625;0.2629;0.2874;0.2877;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2874;0.2877;0.3123;0.3126;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3123;0.3126;0.3371;0.3374;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3371;0.3374;0.3620;0.3623;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3620;0.3623;0.3868;0.3871;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.95<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3868;0.3871;0.4117;0.4120;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.83<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4117;0.4120;0.4365;0.4369;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.68<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4365;0.4369;0.4614;0.4617;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.55<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4614;0.4617;0.4863;0.4866;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.43<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4863;0.4866;0.5111;0.5114;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.35<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5111;0.5114;0.5360;0.5363;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.28<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5360;0.5363;0.5608;0.5611;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.23<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5608;0.5611;0.5857;0.5860;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.19<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5857;0.5860;0.6105;0.6109;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.16<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6105;0.6109;0.6354;0.6357;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.14<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6354;0.6357;0.6603;0.6606;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.12<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6603;0.6606;0.6851;0.6854;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.10<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6851;0.6854;0.7100;0.7103;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.09<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7100;0.7103;0.7348;0.7351;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="164" text-anchor="start" style="font-size:20px;font-weight:700;fill:#2563eb" opacity="0">p ≦ 0.08<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7348;0.7351;0.7597;0.7600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="550" y="214" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">t ≦ μ:光が届く（p = 1）</text>
<text x="550" y="238" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">t が μ より遠いほど、p は小さく</text>
<text x="550" y="262" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">p = σ² / (σ² + (t − μ)²)</text>
<text x="60" y="370" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">深度そのものではなく、平均と分散（深度と深度²）を保存する。ぼかしても意味が壊れないので、フィルタが使える。</text>
</svg>

<!-- fig:vsm-chebyshev:end -->

## 影の割合：チェビシェフの不等式
受け手の深度を `t` とします。**範囲の深度の分布**（平均 μ・分散 σ²）から、<strong>「t より、奥にある深度の割合」</strong>＝**日向の割合**を**見積もります**。**正確な分布は分からない**ので、**チェビシェフの（片側）不等式**で**上限**を使います。

<div class="formula">t ≤ μ のとき：日向 = 1　、　t &gt; μ のとき：p_max(t) = σ² / (σ² + (t − μ)²)</div>

チェビシェフの不等式による判定は、2 つの場合に分かれます。t ≤ μ（受け手が平均より手前）なら、完全に日向です。t > μ（受け手が平均より奥）なら、遮蔽物がある可能性があり、日向の割合の上限が `p_max` で与えられます。

`p_max` は、**t が μ に近いほど 1 に近く、離れるほど 0 に近づきます**。**分散が大きい**（深度がばらついている＝**エッジの近く**）ほど、<strong>半影（中間の値）</strong>が出ます。

```hlsl
float ChebyshevUpperBound(float2 moments, float t) {
  float mean = moments.x;
  float variance = max(moments.y - mean * mean, kMinVariance);
  float d = t - mean;
  float p_max = variance / (variance + d * d);
  return (t <= mean) ? 1.0 : p_max;
}
```

コードの要点です。`kMinVariance` は、分散が 0（平らな面）のとき、0 除算やアクネにならないようにする下限で、バイアスの代わりになります。`t ≤ mean` なら完全に日向です。戻り値は日向の割合（上限）で、影の濃さは `1 − 日向` です。

## 手順
VSM の処理は 3 段階です。深度でなく (z, z²) をピクセル シェーダーで書き込みます（浮動小数点の 2 チャンネル）。次に、分離可能なガウス ブラーや、ミップ・異方性フィルタでぼかします。最後に、受け手の深度でぼかされたモーメントを引き、チェビシェフで日向の割合を求めます。

```hlsl
float2 WriteMoments(float depth) {
  float dx = ddx(depth);
  float dy = ddy(depth);
  float moment2 = depth * depth + 0.25 * (dx * dx + dy * dy);
  return float2(depth, moment2);
}
```

コードの要点です。`ddx・ddy` の項は、面の傾きによる深度の分散を `M₂` に足すもので、傾いた面でもアクネが出ません（バイアスの代わり）。フォーマットは `R32G32_FLOAT` にします。精度が大事で、16 ビットでは足りないことが多いです。ぼかしは、シャドウ マップに分離したガウス ブラーをかけ、ミップを作って遠くを粗くすることもできます。

### 利点：フィルタが安い

| フィルタ | PCF | VSM |
| --- | --- | --- |
| **広いソフトネス** | サンプルを**増やす**（重い） | **ぼかして**おくだけ（シャドウ マップ全体に、1 回）。**画素あたりは、1 サンプル** |
| **ミップ・異方性** | **使えない** | **使える**（遠くの影を安く滑らか） |
| **MSAA** | 難しい | **使える** |
| **アクネ** | バイアスが必要 | **出にくい**（面の傾きが分散に入る） |

## ページ一覧

| ページ | 内容 |
| --- | --- |
| [Light Bleeding](light-bleeding.md) | VSM の最大の弱点と、対策 |
| [ESM](esm.md) | 指数で深度をゆがめる、簡単な改良 |
| [EVSM](evsm.md) | 指数と VSM を組み合わせる |
| [MSM](msm.md) | 高次のモーメントで、光漏れを抑える |
| [Comparison with PCF](comparison.md) | VSM 系の比較・PCF との選び方 |

## よくあるミス

??? failure "VSM の影の中に、光が漏れて、白い筋が出る"
    **光漏れ**。**[Light Bleeding](light-bleeding.md)の対策**（**しきい値で絞る**・**EVSM・MSM**）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **VSM は、深度の統計を保存して、フィルタ可能にする**
    - [x] **柔らかい影が安いが、光漏れがある**

## 参考

- Eisemann et al., "Real-Time Shadows"（CRC Press 2011）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（Microsoft Learn）

## 関連ページ

- [Shadows](../index.md)
- [PCF](../pcf.md)
- [Light Bleeding](light-bleeding.md)
