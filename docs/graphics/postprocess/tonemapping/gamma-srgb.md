---
title: Gamma and HDR Output
tags:
  - 描画
---

# Gamma and HDR Output

**トーンマップの出力は、リニア（光の量に比例）の 0〜1**です。**ディスプレイに出す前に、sRGB の曲線（ガンマ ≒ 2.2）を掛ける**必要があり、**これを間違えると画面全体が暗く潰れたり、白っぽくなったり**します。**HDR ディスプレイでは、さらに別の出力**（HDR10・scRGB）になります。このページでは、**なぜガンマが要るか・sRGB 変換の位置・レンダー ターゲットの作り方・HDR ディスプレイへの出し方・UI の扱い**を説明します。

!!! tip "ポイント"
    - 光の計算は<strong>リニア空間</strong>。<strong>画像やディスプレイは、暗部を細かく持つガンマ空間</strong>。
    - <strong>sRGB 変換はトーンマップの後・最後</strong>。<strong>前にすると暗部が潰れる</strong>。
    - <strong>`_SRGB` 形式のレンダー ターゲット</strong>に<strong>書けば、ハードウェアが自動変換</strong>する。
    - <strong>テクスチャ（色）は `_SRGB` で読む</strong>。<strong>法線・粗さなどのデータは UNORM</strong>。
    - <strong>HDR ディスプレイ</strong>は<strong>別のトーンマップ・別の出力形式</strong>（PQ・Rec.2020）。
    - <strong>UI</strong>は<strong>ペーパー ホワイト</strong>を<strong>別に調整して合成</strong>する。

<!-- fig:gamma-srgb:begin -->

<svg class="fig illust motion" data-fig="gamma-srgb" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-gamma-srgb" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ガンマ:リニアな光の量を、表示用に持ち上げる（暗部に多く割り当てる）</text>
<rect x="60" y="80" width="330" height="230" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="142.5" y1="80" x2="142.5" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="137.5" x2="390" y2="137.5" stroke="#e2e8f0" stroke-width="1"/>
<line x1="225.0" y1="80" x2="225.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="195.0" x2="390" y2="195.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="307.5" y1="80" x2="307.5" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="252.5" x2="390" y2="252.5" stroke="#e2e8f0" stroke-width="1"/>
<text x="390" y="330" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">リニアな明るさ（光の量）</text>
<text x="60" y="72" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">表示する値（sRGB）</text>
<path d="M60.0,310.0 L71.0,302.33 L82.0,294.67 L93.0,287.0 L104.0,279.33 L115.0,271.67 L126.0,264.0 L137.0,256.33 L148.0,248.67 L159.0,241.0 L170.0,233.33 L181.0,225.67 L192.0,218.0 L203.0,210.33 L214.0,202.67 L225.0,195.0 L236.0,187.33 L247.0,179.67 L258.0,172.0 L269.0,164.33 L280.0,156.67 L291.0,149.0 L302.0,141.33 L313.0,133.67 L324.0,126.0 L335.0,118.33 L346.0,110.67 L357.0,103.0 L368.0,95.33 L379.0,87.67 L390.0,80.0" fill="none" stroke="#64748b" stroke-width="3" opacity="1" stroke-dasharray="5 4"/>
<path d="M60.0,310.0 L65.5,274.23 L71.0,260.99 L76.5,251.07 L82.0,242.84 L87.5,235.67 L93.0,229.24 L98.5,223.38 L104.0,217.96 L109.5,212.9 L115.0,208.14 L120.5,203.63 L126.0,199.33 L131.5,195.23 L137.0,191.3 L142.5,187.52 L148.0,183.87 L153.5,180.35 L159.0,176.94 L164.5,173.63 L170.0,170.41 L175.5,167.28 L181.0,164.23 L186.5,161.25 L192.0,158.35 L197.5,155.51 L203.0,152.73 L208.5,150.01 L214.0,147.34 L219.5,144.73 L225.0,142.16 L230.5,139.64 L236.0,137.16 L241.5,134.73 L247.0,132.33 L252.5,129.98 L258.0,127.66 L263.5,125.37 L269.0,123.12 L274.5,120.9 L280.0,118.71 L285.5,116.55 L291.0,114.42 L296.5,112.32 L302.0,110.24 L307.5,108.19 L313.0,106.17 L318.5,104.16 L324.0,102.18 L329.5,100.23 L335.0,98.29 L340.5,96.38 L346.0,94.48 L351.5,92.61 L357.0,90.76 L362.5,88.92 L368.0,87.1 L373.5,85.3 L379.0,83.52 L384.5,81.75 L390.0,80.0" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<text x="258.0" y="206.5" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">そのまま</text>
<text x="99.6" y="130.6" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">ガンマ補正</text>
<circle cx="60.0" cy="310.0" r="7" fill="#e5484d" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0908;0.1175;0.1443;0.1711;0.1978;0.2246;0.2514;0.2782;0.3049;0.3317;0.3585;0.3852;0.4120;0.4388;0.4655;0.4923;0.5191;0.5458;0.5726;0.5994;0.6262;0.6529;0.6797;0.7065;0.7332;0.7600;1.0000" values="60;60;72.69;85.38;98.08;110.77;123.46;136.15;148.85;161.54;174.23;186.92;199.62;212.31;225;237.69;250.38;263.08;275.77;288.46;301.15;313.85;326.54;339.23;351.92;364.62;377.31;390;390"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0640;0.0908;0.1175;0.1443;0.1711;0.1978;0.2246;0.2514;0.2782;0.3049;0.3317;0.3585;0.3852;0.4120;0.4388;0.4655;0.4923;0.5191;0.5458;0.5726;0.5994;0.6262;0.6529;0.6797;0.7065;0.7332;0.7600;1.0000" values="310;310;257.69;238.32;223.82;211.78;201.29;191.9;183.32;175.4;167.99;161.03;154.43;148.16;142.16;136.41;130.88;125.55;120.39;115.4;110.56;105.86;101.28;96.82;92.47;88.22;84.06;80;80"/></circle>
<text x="430" y="110" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">リニアの値をそのまま表示</text>
<text x="430" y="210" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">ガンマ補正して表示</text>
<rect x="430" y="120" width="19" height="50" fill="#000000"/>
<rect x="430" y="220" width="19" height="50" fill="#000000"/>
<rect x="449" y="120" width="19" height="50" fill="#111111"/>
<rect x="449" y="220" width="19" height="50" fill="#4a4a4a"/>
<rect x="468" y="120" width="19" height="50" fill="#222222"/>
<rect x="468" y="220" width="19" height="50" fill="#666666"/>
<rect x="487" y="120" width="19" height="50" fill="#333333"/>
<rect x="487" y="220" width="19" height="50" fill="#7b7b7b"/>
<rect x="506" y="120" width="19" height="50" fill="#444444"/>
<rect x="506" y="220" width="19" height="50" fill="#8c8c8c"/>
<rect x="525" y="120" width="19" height="50" fill="#555555"/>
<rect x="525" y="220" width="19" height="50" fill="#9b9b9b"/>
<rect x="544" y="120" width="19" height="50" fill="#666666"/>
<rect x="544" y="220" width="19" height="50" fill="#a8a8a8"/>
<rect x="563" y="120" width="19" height="50" fill="#777777"/>
<rect x="563" y="220" width="19" height="50" fill="#b4b4b4"/>
<rect x="582" y="120" width="19" height="50" fill="#888888"/>
<rect x="582" y="220" width="19" height="50" fill="#c0c0c0"/>
<rect x="601" y="120" width="19" height="50" fill="#999999"/>
<rect x="601" y="220" width="19" height="50" fill="#cacaca"/>
<rect x="620" y="120" width="19" height="50" fill="#aaaaaa"/>
<rect x="620" y="220" width="19" height="50" fill="#d4d4d4"/>
<rect x="639" y="120" width="19" height="50" fill="#bbbbbb"/>
<rect x="639" y="220" width="19" height="50" fill="#dddddd"/>
<rect x="658" y="120" width="19" height="50" fill="#cccccc"/>
<rect x="658" y="220" width="19" height="50" fill="#e6e6e6"/>
<rect x="677" y="120" width="19" height="50" fill="#dddddd"/>
<rect x="677" y="220" width="19" height="50" fill="#efefef"/>
<rect x="696" y="120" width="19" height="50" fill="#eeeeee"/>
<rect x="696" y="220" width="19" height="50" fill="#f7f7f7"/>
<rect x="715" y="120" width="19" height="50" fill="#ffffff"/>
<rect x="715" y="220" width="19" height="50" fill="#ffffff"/>
<rect x="430" y="116" width="19" height="58" fill="none" stroke="#e5aa28" stroke-width="3"><animate attributeName="x" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.1104;0.1568;0.2032;0.2496;0.2960;0.3424;0.3888;0.4352;0.4816;0.5280;0.5744;0.6208;0.6672;0.7136;0.7600" values="430;430;449;468;487;506;525;544;563;582;601;620;639;658;677;696;715"/></rect>
<rect x="430" y="216" width="19" height="58" fill="none" stroke="#e5aa28" stroke-width="3"><animate attributeName="x" dur="12.5s" repeatCount="indefinite" calcMode="discrete" keyTimes="0.0000;0.0640;0.1104;0.1568;0.2032;0.2496;0.2960;0.3424;0.3888;0.4352;0.4816;0.5280;0.5744;0.6208;0.6672;0.7136;0.7600" values="430;430;449;468;487;506;525;544;563;582;601;620;639;658;677;696;715"/></rect>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.00 → 表示 0.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0637;0.0640;0.0904;0.0908;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.04 → 表示 0.23<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0904;0.0908;0.1172;0.1175;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.08 → 表示 0.32<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1172;0.1175;0.1440;0.1443;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.12 → 表示 0.38<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1440;0.1443;0.1708;0.1711;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.16 → 表示 0.43<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1708;0.1711;0.1975;0.1978;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.20 → 表示 0.48<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.1975;0.1978;0.2243;0.2246;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.24 → 表示 0.52<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2243;0.2246;0.2511;0.2514;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.28 → 表示 0.56<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2511;0.2514;0.2778;0.2782;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.32 → 表示 0.60<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2778;0.2782;0.3046;0.3049;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.36 → 表示 0.63<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3046;0.3049;0.3314;0.3317;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.40 → 表示 0.66<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3314;0.3317;0.3581;0.3585;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.44 → 表示 0.69<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3581;0.3585;0.3849;0.3852;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.48 → 表示 0.72<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3849;0.3852;0.4117;0.4120;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.52 → 表示 0.74<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4117;0.4120;0.4384;0.4388;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.56 → 表示 0.77<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4384;0.4388;0.4652;0.4655;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.60 → 表示 0.79<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4652;0.4655;0.4920;0.4923;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.64 → 表示 0.82<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.4920;0.4923;0.5188;0.5191;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.68 → 表示 0.84<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5188;0.5191;0.5455;0.5458;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.72 → 表示 0.86<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5455;0.5458;0.5723;0.5726;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.76 → 表示 0.88<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5723;0.5726;0.5991;0.5994;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.80 → 表示 0.90<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5991;0.5994;0.6258;0.6262;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.84 → 表示 0.92<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6258;0.6262;0.6526;0.6529;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.88 → 表示 0.94<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6526;0.6529;0.6794;0.6797;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.92 → 表示 0.96<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6794;0.6797;0.7061;0.7065;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 0.96 → 表示 0.98<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7061;0.7065;0.7329;0.7332;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:16px;font-weight:700;fill:#1f2937" opacity="0">リニア 1.00 → 表示 1.00<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.7329;0.7332;0.7597;0.7600;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">中間灰（実際の光の 18 %）は、表示では 0.46 に持ち上げられる。人間の目は、暗部の差に敏感なので、暗部を細かく持つ。</text>
</svg>

<!-- fig:gamma-srgb:end -->

## なぜガンマがあるのか

**人間の目は暗い所の違いに敏感**で**明るい所の違いには鈍感**です。**8 ビット（256 段階）に、明るさを比例で割り当てると**、**暗部の段階が少なすぎて、縞（バンディング）が出ます**。**そこで暗部に多くの段階を割り当てる曲線**（**ガンマ**）を**かけて保存**します。

<svg class="fig illust" viewBox="0 0 780 280" role="img" aria-label="ガンマ曲線">
<text x="20" y="26" class="fig-title">リニアと sRGB：同じ 8 ビットでも、暗部の段階が増える</text>
<line x1="80" y1="240" x2="420" y2="240" stroke="currentColor" stroke-opacity="0.5"/><line x1="80" y1="50" x2="80" y2="240" stroke="currentColor" stroke-opacity="0.5"/>
<polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5 4" points="80,240 420,50"/>
<polyline fill="none" stroke="#2563eb" stroke-width="4" points="80,240 90,215 110,190 140,165 180,140 230,115 290,92 350,70 420,50"/>
<text x="425" y="56" style="font-size:12px">sRGB（ガンマ）</text><text x="425" y="240" style="font-size:12px;fill:#64748b">リニアの値 →</text>
<text x="40" y="150" style="font-size:12px">保存値</text>
<g font-size="13">
<text x="480" y="90" style="font-weight:700">リニア値 0.2 を保存すると</text>
<text x="480" y="114">・sRGB なら 約 0.48（0〜255 で 約 124）</text>
<text x="480" y="138">・暗部（0〜0.2）に 約 124 段階を使える</text>
<text x="480" y="172" style="font-weight:700">ガンマが無いと</text>
<text x="480" y="196" style="font-size:12px">・暗部（0〜0.2）は約 51 段階 → 縞</text>
</g>
</svg>

色の空間は 2 つに使い分けます。<strong>リニア</strong>は、光の計算・合成・ブルーム・トーンマップに使います。物理的に正しい足し算ができるからです。<strong>sRGB（ガンマ）</strong>は、保存と表示に使います（画像ファイルとディスプレイ）。

## 変換の位置

変換の位置は、次のとおりです。色のテクスチャの読み込みでは、sRGB からリニアへ変換します（`_SRGB` 形式で自動）。ライティング・露出・ブルーム・トーンマップは、リニアで行います。画面への出力で、リニアから sRGB へ変換します（最後に、`_SRGB` の RTV で自動）。

**ガンマ変換をトーンマップの前に入れる**と、**暗部が潰れて眠い絵**になります（**典型的な事故**）。

## sRGB の式

<div class="formula">
sRGB(c) = 12.92 · c　　（c ≦ 0.0031308）<br>
sRGB(c) = 1.055 · c^(1/2.4) − 0.055　　（それ以外）
</div>

```hlsl
float3 LinearToSRGB(float3 c) {
  float3 low = c * 12.92;
  float3 high = 1.055 * pow(max(c, 0.0), 1.0 / 2.4) - 0.055;
  return (c <= 0.0031308) ? low : high;
}

float3 SRGBToLinear(float3 c) {
  float3 low = c / 12.92;
  float3 high = pow((c + 0.055) / 1.055, 2.4);
  return (c <= 0.04045) ? low : high;
}
```

ガンマ変換の近似は 2 通りです。`pow(c, 1/2.2)` はよく使われる近似ですが、暗部で少しずれます。正確な sRGB は、区分式を使う方法で、ハードウェアの自動変換もこちらです。

## DX11 での設定

```cpp
DXGI_SWAP_CHAIN_DESC1 desc = {};
desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;

D3D11_RENDER_TARGET_VIEW_DESC rtv_desc = {};
rtv_desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM_SRGB;
rtv_desc.ViewDimension = D3D11_RTV_DIMENSION_TEXTURE2D;
device->CreateRenderTargetView(back_buffer.Get(), &rtv_desc, rtv.GetAddressOf());
```

出力設定の要点です。スワップチェーンの形式は UNORM にします。FLIP モデルでは `_SRGB` のスワップチェーンが作れないので、RTV だけを `_SRGB` にします。RTV を `_SRGB` にすると、シェーダーのリニアな出力を、ハードウェアが sRGB に変換して書き込みます。RTV が `_SRGB` なのにシェーダーで `pow` もすると、二重にガンマがかかって白っぽくなるので、シェーダーでは `pow` しません。

### テクスチャの読み込み

| テクスチャ | 形式 | 理由 |
| --- | --- | --- |
| <strong>アルベド（色）</strong> | **`_SRGB`** | **画像が sRGB で保存されているので、読み込み時にリニアへ** |
| **法線マップ** | <strong>UNORM（リニア）</strong> | **データであって、色ではない** |
| **粗さ・金属度・AO** | **UNORM** | **同上** |
| **HDR テクスチャ** | **FLOAT** | **すでにリニア** |

## HDR ディスプレイへの出力

**HDR ディスプレイは、SDR より広い明るさ（数百〜数千ニト）と広い色域**を**出せます**。**SDR 用のトーンマップの結果をそのまま送る**と、**HDR の良さが活きません**。

| 項目 | 内容 |
| --- | --- |
| **色空間** | **Rec.2020**（広い色域） |
| **伝達関数** | <strong>PQ（ST.2084）</strong>：**絶対的な明るさ（ニト）を、10 ビットに効率よく入れる曲線** |
| **スワップチェーン形式** | <strong>`R10G10B10A2_UNORM`（HDR10）</strong>、または <strong>`R16G16B16A16_FLOAT`（scRGB）</strong> |
| **色空間の設定** | **`IDXGISwapChain3::SetColorSpace1`** で **`DXGI_COLOR_SPACE_RGB_FULL_G2084_NONE_P2020`** |
| **トーンマップ** | **ディスプレイの最大輝度（ニト）に合わせた HDR 用の曲線**。**SDR 用とは別** |

```cpp
swap_chain->SetColorSpace1(DXGI_COLOR_SPACE_RGB_FULL_G2084_NONE_P2020);
```

```hlsl
float3 LinearToPQ(float3 nits) {
  const float m1 = 0.1593017578125;
  const float m2 = 78.84375;
  const float c1 = 0.8359375;
  const float c2 = 18.8515625;
  const float c3 = 18.6875;
  float3 y = pow(nits / 10000.0, m1);
  return pow((c1 + c2 * y) / (1.0 + c3 * y), m2);
}
```

コードの要点です。`nits / 10000` は、PQ が 10,000 ニトを 1 とするためです。最大輝度は `IDXGIOutput6::GetDesc1` でディスプレイの値を得て、曲線のロールオフに使います。

### ペーパー ホワイトと UI

**HDR では、「白」の明るさに決まりがありません**。**UI の白をゲーム画面の最大輝度で出すと、まぶしすぎる**ので、**UI の白を「ペーパー ホワイト」（約 200〜300 ニト）に決め**、**ゲーム画面とは別に変換して合成**します。

HDR での UI の扱いです。ゲーム画面は、HDR 用トーンマップで PQ にします。UI は、ペーパー ホワイトに合わせたニトに変換してから合成します。ユーザー設定として、最大輝度とペーパー ホワイトを調整できるようにします。

## よくあるミス

??? failure "ガンマ変換を二重にして、全体が白っぽい"
    **RTV が `_SRGB` なら、シェーダーで `pow` しない**。

??? failure "ガンマ変換が無くて、全体が暗く潰れる"
    **リニアのまま UNORM に書いている**。**`_SRGB` の RTV にする**。

??? failure "法線マップを `_SRGB` で読んで、ライティングが崩れる"
    **データのテクスチャは UNORM**。

??? failure "SDR 用の曲線を HDR ディスプレイにそのまま出して、地味"
    **HDR 用のトーンマップ**と**PQ の出力**を使う。

??? failure "HDR で UI がまぶしすぎる"
    **ペーパー ホワイトを決めて、UI を別に変換**する。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>計算はリニア、保存・表示は sRGB</strong>。<strong>ガンマは最後</strong>
    - [x] <strong>RTV を `_SRGB`</strong> にすれば<strong>自動変換</strong>。<strong>シェーダーで `pow` しない</strong>
    - [x] <strong>色テクスチャは `_SRGB`、データは UNORM</strong>
    - [x] <strong>HDR ディスプレイ</strong>は<strong>別のトーンマップ ＋ PQ ＋ Rec.2020</strong>
    - [x] <strong>UI はペーパー ホワイト</strong>で<strong>別に合成</strong>

## 参考

- Microsoft, "DXGI Color Space"・"High Dynamic Range and Wide Color Gamut"（Microsoft Learn）
- SMPTE ST 2084, "High Dynamic Range Electro-Optical Transfer Function"
- IEC 61966-2-1, "sRGB"

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [Exposure](exposure.md)
- [Color Grading](../color-grading/index.md)
- [画面に出す](../../../3d/render-flow/present.md)
