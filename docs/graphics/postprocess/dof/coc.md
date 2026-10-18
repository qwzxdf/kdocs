---
title: Circle of Confusion (CoC)
tags:
  - 描画
---

# Circle of Confusion (CoC)

<strong>錯乱円（Circle of Confusion、CoC）</strong>は、<strong>ピントが合っていない点が、センサー上に作る「円」</strong>です。**この円の大きさがそのままボケの大きさ**になります。**DOF の最初の仕事は、画面の各画素について、この CoC を求めること**です。このページでは、**光学的な仕組み・薄いレンズの式・CoC のグラフ・ピクセルへの換算・符号の意味・物理ベースとアーティスト向けの簡易式**を説明します。

!!! tip "ポイント"
    - ピントが合った点は<strong>センサー上で 1 点</strong>、<strong>ずれた点は円（CoC）</strong>になる。
    - <strong>CoC の大きさ</strong>は<strong>絞り（F 値）・焦点距離・ピント距離・被写体の距離</strong>で決まる。
    - <strong>絞りを開く・望遠にする・被写体に近づく</strong>と<strong>ボケが大きくなる</strong>。
    - <strong>背景は無限遠で CoC が飽和</strong>する。<strong>前景は近づくほど急に大きくなる</strong>。
    - <strong>符号付きで持つ</strong>：<strong>前景（ピントより手前）は負、背景は正</strong>。
    - <strong>画素数に換算し、最大値でクランプ</strong>する（<strong>コストの上限</strong>）。
    - <strong>線形な深度</strong>（ビュー空間の z）を使う。

## How the Optics Work {#光学の仕組み}

**レンズはある距離の点をセンサー上の 1 点に集めます**（**ピントが合う距離**）。**それより近い点・遠い点はセンサーの前や後ろで像を結び、センサー上では広がった円**になります。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="錯乱円の仕組み">
<text x="20" y="26" class="fig-title">ピント面にない点は、センサー上で円になる</text>
<line x1="60" y1="130" x2="730" y2="130" stroke="currentColor" stroke-dasharray="4 3" opacity="0.4"/>
<line x1="330" y1="60" x2="330" y2="200" stroke="currentColor" stroke-width="4"/><text x="300" y="52" style="font-size:12px">レンズ</text>
<circle cx="80" cy="130" r="6" fill="#e5aa28" stroke="currentColor" stroke-width="2"/><text x="40" y="156" style="font-size:12px">被写体（ピント外）</text>
<line x1="80" y1="130" x2="330" y2="82" stroke="currentColor"/><line x1="80" y1="130" x2="330" y2="178" stroke="currentColor"/>
<line x1="330" y1="82" x2="560" y2="130" stroke="currentColor"/><line x1="330" y1="178" x2="560" y2="130" stroke="currentColor"/>
<circle cx="560" cy="130" r="4" fill="currentColor"/><text x="520" y="150" style="font-size:12px">像を結ぶ点</text>
<line x1="650" y1="70" x2="650" y2="190" stroke="currentColor" stroke-width="3"/><text x="620" y="62" style="font-size:12px">センサー</text>
<line x1="330" y1="82" x2="650" y2="104" stroke="currentColor" stroke-dasharray="2 3" opacity="0.6"/><line x1="330" y1="178" x2="650" y2="156" stroke="currentColor" stroke-dasharray="2 3" opacity="0.6"/>
<line x1="662" y1="104" x2="662" y2="156" stroke="#e5484d" stroke-width="3"/><text x="672" y="134" style="font-size:12px;fill:#e5484d;font-weight:700">CoC</text>
<text x="300" y="232" style="font-size:12px">像を結ぶ点がセンサーの手前 → センサー上では光が広がる</text>
</svg>

## From the Thin-Lens Formula {#薄いレンズの式から}

**薄いレンズの式**から、**CoC の直径**（**センサー上の長さ**）が**導けます**。

<div class="formula">CoC = A · |S₂ − S₁| / S₂ · f / (S₁ − f)　（A = f / N）</div>

| 記号 | 意味 | 例 |
| --- | --- | --- |
| **f** | **焦点距離** | **50 mm** |
| **N** | **F 値**（小さいほど開放） | **1.8** |
| **A = f / N** | **絞りの口径** | **約 27.8 mm** |
| **S₁** | **ピントを合わせた距離** | **3 m** |
| **S₂** | **被写体の距離** | **ピント面からの距離次第** |

| 要因 | ボケの大きさ |
| --- | --- |
| <strong>絞りを開く（N を小さく）</strong> | **大きくなる** |
| <strong>焦点距離を長く（望遠）</strong> | **大きくなる** |
| **被写体を近づける** | **大きくなる** |
| **ピント面から離れる** | **大きくなる**（**背景は無限遠で頭打ち**） |

<!-- fig:coc-graph:begin -->

<svg class="fig illust motion" data-fig="coc-graph" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-coc-graph" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">錯乱円(CoC): ピントの距離からのずれで、ぼける半径が決まる。手前は急に、奥はゆるやかに大きくなる</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">レンズの式から計算。ピントを 2 m → 5 m → 20 m に動かして、各距離の CoC(画素)を見る</text>
<rect x="30" y="96" width="900" height="270" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 距離ごとのぼける半径(画素)</text>
<text x="70.0" y="352" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">1 m</text>
<line x1="70.0" y1="120" x2="70.0" y2="334" stroke="#e2e8f0" stroke-width="1.2"/>
<text x="208.82092223100076" y="352" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">2 m</text>
<line x1="208.82" y1="120" x2="208.82" y2="334" stroke="#e2e8f0" stroke-width="1.2"/>
<text x="392.33219948633433" y="352" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">5 m</text>
<line x1="392.33" y1="120" x2="392.33" y2="334" stroke="#e2e8f0" stroke-width="1.2"/>
<text x="531.1531217173351" y="352" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">10 m</text>
<line x1="531.15" y1="120" x2="531.15" y2="334" stroke="#e2e8f0" stroke-width="1.2"/>
<text x="669.9740439483359" y="352" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">20 m</text>
<line x1="669.97" y1="120" x2="669.97" y2="334" stroke="#e2e8f0" stroke-width="1.2"/>
<text x="890.0" y="352" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">60 m</text>
<line x1="890.0" y1="120" x2="890.0" y2="334" stroke="#e2e8f0" stroke-width="1.2"/>
<path d="M70.0,155.57 L78.2,169.57 L86.4,183.0 L94.6,195.89 L102.8,208.27 L111.0,220.15 L119.2,231.56 L127.4,242.5 L135.6,253.01 L143.8,263.1 L152.0,272.78 L160.2,282.07 L168.4,290.99 L176.6,299.55 L184.8,307.77 L193.0,315.66 L201.2,323.23 L209.4,329.5 L217.6,322.52 L225.8,315.82 L234.0,309.39 L242.2,303.22 L250.4,297.3 L258.6,291.61 L266.8,286.16 L275.0,280.92 L283.2,275.89 L291.4,271.06 L299.6,266.43 L307.8,261.98 L316.0,257.71 L324.2,253.62 L332.4,249.68 L340.6,245.91 L348.8,242.28 L357.0,238.8 L365.2,235.47 L373.4,232.26 L381.6,229.18 L389.8,226.23 L398.0,223.4 L406.2,220.68 L414.4,218.06 L422.6,215.56 L430.8,213.15 L439.0,210.84 L447.2,208.62 L455.4,206.49 L463.6,204.45 L471.8,202.49 L480.0,200.61 L488.2,198.8 L496.4,197.07 L504.6,195.4 L512.8,193.8 L521.0,192.27 L529.2,190.8 L537.4,189.39 L545.6,188.03 L553.8,186.73 L562.0,185.48 L570.2,184.28 L578.4,183.13 L586.6,182.02 L594.8,180.96 L603.0,179.94 L611.2,178.96 L619.4,178.02 L627.6,177.12 L635.8,176.26 L644.0,175.43 L652.2,174.63 L660.4,173.87 L668.6,173.13 L676.8,172.43 L685.0,171.75 L693.2,171.1 L701.4,170.48 L709.6,169.88 L717.8,169.31 L726.0,168.76 L734.2,168.23 L742.4,167.72 L750.6,167.23 L758.8,166.77 L767.0,166.32 L775.2,165.89 L783.4,165.47 L791.6,165.07 L799.8,164.69 L808.0,164.33 L816.2,163.98 L824.4,163.64 L832.6,163.32 L840.8,163.0 L849.0,162.71 L857.2,162.42 L865.4,162.15 L873.6,161.88 L881.8,161.63 L890.0,161.39" fill="none" stroke="#e5484d" stroke-width="4"><animate attributeName="d" dur="22.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0667;0.3244;0.5822" values="M70.0,155.57 L78.2,169.57 L86.4,183.0 L94.6,195.89 L102.8,208.27 L111.0,220.15 L119.2,231.56 L127.4,242.5 L135.6,253.01 L143.8,263.1 L152.0,272.78 L160.2,282.07 L168.4,290.99 L176.6,299.55 L184.8,307.77 L193.0,315.66 L201.2,323.23 L209.4,329.5 L217.6,322.52 L225.8,315.82 L234.0,309.39 L242.2,303.22 L250.4,297.3 L258.6,291.61 L266.8,286.16 L275.0,280.92 L283.2,275.89 L291.4,271.06 L299.6,266.43 L307.8,261.98 L316.0,257.71 L324.2,253.62 L332.4,249.68 L340.6,245.91 L348.8,242.28 L357.0,238.8 L365.2,235.47 L373.4,232.26 L381.6,229.18 L389.8,226.23 L398.0,223.4 L406.2,220.68 L414.4,218.06 L422.6,215.56 L430.8,213.15 L439.0,210.84 L447.2,208.62 L455.4,206.49 L463.6,204.45 L471.8,202.49 L480.0,200.61 L488.2,198.8 L496.4,197.07 L504.6,195.4 L512.8,193.8 L521.0,192.27 L529.2,190.8 L537.4,189.39 L545.6,188.03 L553.8,186.73 L562.0,185.48 L570.2,184.28 L578.4,183.13 L586.6,182.02 L594.8,180.96 L603.0,179.94 L611.2,178.96 L619.4,178.02 L627.6,177.12 L635.8,176.26 L644.0,175.43 L652.2,174.63 L660.4,173.87 L668.6,173.13 L676.8,172.43 L685.0,171.75 L693.2,171.1 L701.4,170.48 L709.6,169.88 L717.8,169.31 L726.0,168.76 L734.2,168.23 L742.4,167.72 L750.6,167.23 L758.8,166.77 L767.0,166.32 L775.2,165.89 L783.4,165.47 L791.6,165.07 L799.8,164.69 L808.0,164.33 L816.2,163.98 L824.4,163.64 L832.6,163.32 L840.8,163.0 L849.0,162.71 L857.2,162.42 L865.4,162.15 L873.6,161.88 L881.8,161.63 L890.0,161.39;M70.0,155.57 L78.2,169.57 L86.4,183.0 L94.6,195.89 L102.8,208.27 L111.0,220.15 L119.2,231.56 L127.4,242.5 L135.6,253.01 L143.8,263.1 L152.0,272.78 L160.2,282.07 L168.4,290.99 L176.6,299.55 L184.8,307.77 L193.0,315.66 L201.2,323.23 L209.4,329.5 L217.6,322.52 L225.8,315.82 L234.0,309.39 L242.2,303.22 L250.4,297.3 L258.6,291.61 L266.8,286.16 L275.0,280.92 L283.2,275.89 L291.4,271.06 L299.6,266.43 L307.8,261.98 L316.0,257.71 L324.2,253.62 L332.4,249.68 L340.6,245.91 L348.8,242.28 L357.0,238.8 L365.2,235.47 L373.4,232.26 L381.6,229.18 L389.8,226.23 L398.0,223.4 L406.2,220.68 L414.4,218.06 L422.6,215.56 L430.8,213.15 L439.0,210.84 L447.2,208.62 L455.4,206.49 L463.6,204.45 L471.8,202.49 L480.0,200.61 L488.2,198.8 L496.4,197.07 L504.6,195.4 L512.8,193.8 L521.0,192.27 L529.2,190.8 L537.4,189.39 L545.6,188.03 L553.8,186.73 L562.0,185.48 L570.2,184.28 L578.4,183.13 L586.6,182.02 L594.8,180.96 L603.0,179.94 L611.2,178.96 L619.4,178.02 L627.6,177.12 L635.8,176.26 L644.0,175.43 L652.2,174.63 L660.4,173.87 L668.6,173.13 L676.8,172.43 L685.0,171.75 L693.2,171.1 L701.4,170.48 L709.6,169.88 L717.8,169.31 L726.0,168.76 L734.2,168.23 L742.4,167.72 L750.6,167.23 L758.8,166.77 L767.0,166.32 L775.2,165.89 L783.4,165.47 L791.6,165.07 L799.8,164.69 L808.0,164.33 L816.2,163.98 L824.4,163.64 L832.6,163.32 L840.8,163.0 L849.0,162.71 L857.2,162.42 L865.4,162.15 L873.6,161.88 L881.8,161.63 L890.0,161.39;M70.0,130.0 L78.2,130.0 L86.4,130.0 L94.6,130.0 L102.8,130.0 L111.0,130.0 L119.2,130.0 L127.4,140.76 L135.6,151.11 L143.8,161.04 L152.0,170.57 L160.2,179.73 L168.4,188.51 L176.6,196.94 L184.8,205.04 L193.0,212.81 L201.2,220.27 L209.4,227.42 L217.6,234.3 L225.8,240.89 L234.0,247.22 L242.2,253.3 L250.4,259.13 L258.6,264.73 L266.8,270.11 L275.0,275.27 L283.2,280.22 L291.4,284.97 L299.6,289.54 L307.8,293.92 L316.0,298.12 L324.2,302.16 L332.4,306.03 L340.6,309.75 L348.8,313.32 L357.0,316.74 L365.2,320.03 L373.4,323.19 L381.6,326.22 L389.8,329.13 L398.0,328.08 L406.2,325.4 L414.4,322.83 L422.6,320.36 L430.8,317.99 L439.0,315.72 L447.2,313.53 L455.4,311.44 L463.6,309.43 L471.8,307.49 L480.0,305.64 L488.2,303.86 L496.4,302.15 L504.6,300.51 L512.8,298.94 L521.0,297.43 L529.2,295.98 L537.4,294.59 L545.6,293.25 L553.8,291.97 L562.0,290.74 L570.2,289.56 L578.4,288.42 L586.6,287.33 L594.8,286.29 L603.0,285.29 L611.2,284.32 L619.4,283.4 L627.6,282.51 L635.8,281.66 L644.0,280.84 L652.2,280.06 L660.4,279.31 L668.6,278.58 L676.8,277.89 L685.0,277.22 L693.2,276.58 L701.4,275.97 L709.6,275.38 L717.8,274.82 L726.0,274.27 L734.2,273.75 L742.4,273.25 L750.6,272.77 L758.8,272.31 L767.0,271.87 L775.2,271.44 L783.4,271.04 L791.6,270.64 L799.8,270.27 L808.0,269.91 L816.2,269.56 L824.4,269.23 L832.6,268.91 L840.8,268.61 L849.0,268.31 L857.2,268.03 L865.4,267.76 L873.6,267.5 L881.8,267.25 L890.0,267.01;M70.0,130.0 L78.2,130.0 L86.4,130.0 L94.6,130.0 L102.8,130.0 L111.0,130.0 L119.2,130.0 L127.4,130.0 L135.6,130.0 L143.8,130.0 L152.0,130.0 L160.2,130.0 L168.4,138.43 L176.6,146.8 L184.8,154.83 L193.0,162.54 L201.2,169.94 L209.4,177.05 L217.6,183.87 L225.8,190.41 L234.0,196.7 L242.2,202.73 L250.4,208.52 L258.6,214.08 L266.8,219.41 L275.0,224.53 L283.2,229.45 L291.4,234.16 L299.6,238.69 L307.8,243.04 L316.0,247.21 L324.2,251.22 L332.4,255.06 L340.6,258.75 L348.8,262.29 L357.0,265.69 L365.2,268.96 L373.4,272.09 L381.6,275.1 L389.8,277.98 L398.0,280.75 L406.2,283.41 L414.4,285.97 L422.6,288.42 L430.8,290.77 L439.0,293.03 L447.2,295.19 L455.4,297.27 L463.6,299.27 L471.8,301.19 L480.0,303.03 L488.2,304.79 L496.4,306.49 L504.6,308.12 L512.8,309.68 L521.0,311.18 L529.2,312.62 L537.4,314.0 L545.6,315.32 L553.8,316.6 L562.0,317.82 L570.2,318.99 L578.4,320.12 L586.6,321.2 L594.8,322.23 L603.0,323.23 L611.2,324.19 L619.4,325.1 L627.6,325.98 L635.8,326.83 L644.0,327.64 L652.2,328.42 L660.4,329.17 L668.6,329.88 L676.8,329.43 L685.0,328.77 L693.2,328.13 L701.4,327.52 L709.6,326.94 L717.8,326.38 L726.0,325.84 L734.2,325.32 L742.4,324.83 L750.6,324.35 L758.8,323.89 L767.0,323.45 L775.2,323.03 L783.4,322.63 L791.6,322.24 L799.8,321.87 L808.0,321.51 L816.2,321.17 L824.4,320.84 L832.6,320.52 L840.8,320.22 L849.0,319.92 L857.2,319.65 L865.4,319.38 L873.6,319.12 L881.8,318.87 L890.0,318.63"/></path>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3243;0.3244;1.0000" values="1;1;0;0"/><line x1="208.82" y1="120" x2="208.82" y2="334" stroke="#e5484d" stroke-width="2" stroke-dasharray="5 4"/>
<text x="214.82092223100076" y="136" text-anchor="start" style="font-size:14px;font-weight:700;fill:#e5484d">ピント 2 m</text>
<text x="90" y="160" text-anchor="start" style="font-size:1px;font-weight:700;fill:#1f2937"/>
<text x="90" y="396" text-anchor="start" style="font-size:15px;font-weight:700;fill:#e5484d">ピント 2 m: 手前(1.3 m)で 6.1 画素、奥(3.0 m)で 4.1 画素</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3243;0.3244;0.5820;0.5822;1.0000" values="0;0;1;1;0;0"/><line x1="392.33" y1="120" x2="392.33" y2="334" stroke="#2ea043" stroke-width="2" stroke-dasharray="5 4"/>
<text x="398.33219948633433" y="136" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2ea043">ピント 5 m</text>
<text x="90" y="140" text-anchor="start" style="font-size:1px;font-weight:700;fill:#1f2937"/>
<text x="90" y="396" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2ea043">ピント 5 m: 手前(3.3 m)で 2.4 画素、奥(7.5 m)で 1.6 画素</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5820;0.5822;1.0000" values="0;0;1;1"/><line x1="669.97" y1="120" x2="669.97" y2="334" stroke="#2563eb" stroke-width="2" stroke-dasharray="5 4"/>
<text x="675.9740439483359" y="136" text-anchor="start" style="font-size:14px;font-weight:700;fill:#2563eb">ピント 20 m</text>
<text x="90" y="140" text-anchor="start" style="font-size:1px;font-weight:700;fill:#1f2937"/>
<text x="90" y="396" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">ピント 20 m: 手前(13.3 m)で 0.6 画素、奥(30.0 m)で 0.4 画素</text>
</g>
<text x="40" y="432" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">同じ距離の比(÷1.5 と ×1.5)でも、手前のほうが、ずっとぼける</text>
<text x="40" y="470" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">手前側のぼけ(画素):</text>
<text x="200" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;1.0000" values="1;1;0;0"/></text>
<text x="200" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">6<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0798;0.0800;0.3376;0.3378;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">2<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3376;0.3378;0.5954;0.5956;1.0000" values="0;0;1;1;0;0"/></text>
<text x="200" y="474" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d" opacity="0">1<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5954;0.5956;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8176;0.8178;1.0000" values="0;0;1;1"/><rect x="480" y="446" width="450" height="70" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="496" y="470" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">ピントが近いほど、全体が大きくぼける</text>
<text x="496" y="493" text-anchor="start" style="font-size:13px;font-weight:700;fill:#64748b">ピント 2 m で手前 6.1 画素 / ピント 20 m で 0.6 画素</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ピントの合う距離は、ぼけが 0 になる<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">離れるほど、ぼけが増える。手前は急、奥は頭打ち<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.8398;0.8400;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">ポストプロセスは、この CoC を、深度から画素ごとに計算して使う<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.8398;0.8400;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:coc-graph:end -->

## Shape of the CoC Graph {#coc-のグラフの形}

**被写体の距離 S₂ を横軸**にすると、**CoC は次の形**になります。

- **S₂ = S₁（ピント面）で 0**。
- **手前（S₂ < S₁）に行くと急に大きくなる**（**前景のボケは近いほど極端**）。
- **奥（S₂ > S₁）に行くと緩やかに大きくなり、無限遠で一定の値に近づく**。

**したがって、前景は大きくぼけ、背景はある大きさで頭打ち**になります。

## HLSL

```hlsl
cbuffer DofConstants : register(b0) {
  float focal_length;
  float f_number;
  float focus_distance;
  float sensor_height;
  float image_height_in_pixels;
  float max_coc_in_pixels;
  float2 padding;
};

float CircleOfConfusion(float linear_depth) {
  float aperture = focal_length / f_number;
  float coc = aperture * abs(linear_depth - focus_distance) / linear_depth
            * focal_length / (focus_distance - focal_length);
  return coc;
}

float SignedCocPixels(float linear_depth) {
  float coc = CircleOfConfusion(linear_depth);
  float pixels = coc / sensor_height * image_height_in_pixels;
  float sign_value = linear_depth < focus_distance ? -1.0 : 1.0;
  return sign_value * min(pixels, max_coc_in_pixels);
}
```

| 点 | 説明 |
| --- | --- |
| **`linear_depth`** | **カメラからの線形な距離**（ビュー空間の z）。**深度バッファの非線形な値は使えない** |
| **符号** | **前景は負、背景は正**。**前景と背景を別々に扱うため** |
| **センサー高さで割って画素数へ** | **ミリメートルの CoC を、画像の画素数に換算** |
| **`max_coc_in_pixels`** | <strong>ボケの最大半径（画素）</strong>。**コストの上限**（20〜50 画素） |

**単位をそろえる**ことが**大切**です（**焦点距離・距離・センサー高さをすべてミリメートルかメートル**に）。

## A Simple Formula for Artists {#アーティスト向けの簡易式}

**物理式はパラメータの意味が直感的でない**ことがあります。<strong>「ピント距離・ピントが合う幅・ぼかしの強さ」</strong>だけで**決める簡易式**も**よく使われます**。

```hlsl
float SimpleCoc(float linear_depth, float focus, float range, float scale) {
  float d = linear_depth - focus;
  float t = saturate(abs(d) / range);
  return sign(d) * t * scale;
}
```

簡易版のパラメータです。`focus` はピント距離、`range` はピントが十分に合って見える幅（この幅で最大のボケに達する）、`scale` はぼかしの最大強さ（画素）です。

## Better Approaches {#より良いやり方}

| 工夫 | 内容 |
| --- | --- |
| **物理式を使い、カメラのパラメータをそのまま出す** | **シネマ カメラのように、F 値・焦点距離で直感的に** |
| **ピント距離を注視点から自動で決める** | **画面中心の深度を読んで、ピント距離を追従**（**オートフォーカス**） |
| **ピントの移動をなめらかに** | **ピント距離を指数的に追従させる**（[自動露出](../tonemapping/auto-exposure.md)と同じ考え方） |
| **CoC を専用のバッファに保存** | <strong>カラーのアルファに入れる（FP16）</strong>と、**読み込みが 1 回で済む** |
| **最大 CoC でクランプ** | **コストの上限を保証** |
| **半解像度で処理** | **CoC も半解像度で扱い、コストを 1/4** |

## Common Mistakes {#よくあるミス}

??? failure "非線形の深度バッファの値を、そのまま CoC の計算に使う"
    **ビュー空間の線形な z に直してから**使う。

??? failure "単位がバラバラで、ボケの大きさが極端になる"
    **焦点距離・距離・センサー高さの単位をそろえる**。

??? failure "前景と背景の符号を持たず、前景のボケが背景扱いになる"
    **符号付きで持ち、前景・背景を別に処理**する（[Foreground and Background](near-far.md)）。

??? failure "ピント距離が、画面中心の深度に追従せず、ガクガク動く"
    **ピント距離を時間で滑らかに追従**させる。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] CoC ＝ <strong>ピント外の点が、センサー上に作る円</strong>。<strong>大きさ ＝ ボケの大きさ</strong>
    - [x] <strong>`CoC = A·|S₂−S₁|/S₂·f/(S₁−f)`</strong>。<strong>絞りを開く・望遠・近づくと大きい</strong>
    - [x] <strong>前景は急に、背景は頭打ち</strong>。<strong>符号付きで持つ</strong>
    - [x] <strong>画素数に換算し、最大値でクランプ</strong>
    - [x] <strong>線形な深度</strong>を使う。<strong>単位をそろえる</strong>

## References {#参考}

- Potmesil & Chakravarty, "A Lens and Aperture Camera Model for Synthetic Image Generation"（SIGGRAPH 1981）
- Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare"（SIGGRAPH 2014）
- Wikipedia, "Circle of confusion"

## Related Pages {#関連ページ}

- [Depth of Field (DOF)](index.md)
- [Gather Method](gather.md)
- [Foreground and Background](near-far.md)
- [Exposure](../tonemapping/exposure.md)
