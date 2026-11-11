---
title: Slope-Scale Bias
tags:
  - 描画
---

# Slope-Scale Bias

定数バイアスは光に正面の面に合わせると、斜めの面でアクネが出て斜めの面に合わせると、正面の面で影が浮きます。必要なバイアスの大きさが面の向きで違うからです。それなら面の傾きに比例してバイアスを変えればよいことになります。

<strong>スロープ スケール バイアスは面の傾き（深度の勾配）に比例してバイアスを増やします</strong>。ハードウェアのラスタライザーが対応しているので、シャドウ マップを描くときに設定するだけで使えます。このページでは必要なバイアスが傾きに比例する理由（導出と数値の検算）、`SlopeScaledDepthBias` の式と値の目安、シェーダーでの計算、限界を説明します。

!!! tip "ポイント"
    - 必要なバイアスは 1 テクセルの大きさ × `tan θ` の半分です。`θ` は面の法線と光のなす角です。
    - ラスタライザー ステートの `SlopeScaledDepthBias` で、深度パスに焼き込めます。
    - 理論上、係数は 0.5〜1.0 で足ります。実際には、1〜3 を使うことが多く余裕を見込んでいます。
    - シェーダー側でも `tan(acos(N·L))` から求められます。`N·L` が 0 に近いと発散するので、上限を設けます。
    - 傾きが極端な面では上限があっても、ピーター パンニングが出ます。

!!! info "このページを読む前に"
    - [Shadow Bias](index.md)（このセクション全体の地図と読む順番）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

<!-- fig:slope-bias:begin -->

<svg class="fig illust motion" data-fig="slope-bias" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-slope-bias" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">スロープ スケール バイアス:傾いた面ほど、必要なバイアスは大きい</text>
<rect x="60" y="80" width="360" height="230" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="150.0" y1="80" x2="150.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="137.5" x2="420" y2="137.5" stroke="#e2e8f0" stroke-width="1"/>
<line x1="240.0" y1="80" x2="240.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="195.0" x2="420" y2="195.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="330.0" y1="80" x2="330.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="60" y1="252.5" x2="420" y2="252.5" stroke="#e2e8f0" stroke-width="1"/>
<text x="420" y="330" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">面の傾き（光に対して、度）</text>
<text x="60" y="72" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">必要なバイアス</text>
<path d="M60.0,310.0 L64.5,309.0 L69.0,307.99 L73.5,306.99 L78.0,305.98 L82.5,304.97 L87.0,303.96 L91.5,302.94 L96.0,301.92 L100.5,300.89 L105.0,299.86 L109.5,298.82 L114.0,297.78 L118.5,296.73 L123.0,295.66 L127.5,294.59 L132.0,293.51 L136.5,292.42 L141.0,291.32 L145.5,290.2 L150.0,289.07 L154.5,287.93 L159.0,286.77 L163.5,285.59 L168.0,284.4 L172.5,283.19 L177.0,281.96 L181.5,280.7 L186.0,279.43 L190.5,278.13 L195.0,276.8 L199.5,275.45 L204.0,274.07 L208.5,272.66 L213.0,271.22 L217.5,269.74 L222.0,268.22 L226.5,266.67 L231.0,265.08 L235.5,263.44 L240.0,261.75 L244.5,260.02 L249.0,258.23 L253.5,256.38 L258.0,254.47 L262.5,252.5 L267.0,250.46 L271.5,248.34 L276.0,246.14 L280.5,243.85 L285.0,241.47 L289.5,238.99 L294.0,236.4 L298.5,233.69 L303.0,230.86 L307.5,227.88 L312.0,224.75 L316.5,221.46 L321.0,217.98 L325.5,214.3 L330.0,210.41 L334.5,206.27 L339.0,201.86 L343.5,197.15 L348.0,192.11 L352.5,186.69 L357.0,180.85 L361.5,174.54 L366.0,167.68 L370.5,160.21 L375.0,152.02 L379.5,143.01 L384.0,133.03 L388.5,121.93 L393.0,109.47 L397.5,95.41 L402.0,80.0 L406.5,80.0 L411.0,80.0 L415.5,80.0 L420.0,80.0" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<path d="M60.0,252.5 L240.0,252.5 L420.0,252.5" fill="none" stroke="#e5484d" stroke-width="3" opacity="1" stroke-dasharray="6 4"/>
<text x="294.0" y="244.5" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">定数バイアス（一定）</text>
<text x="96.0" y="103.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2563eb">傾きに比例して増やす（青）</text>
<circle cx="60.0" cy="310.0" r="7" fill="#1f2937" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0955;0.1244;0.1533;0.1821;0.2110;0.2399;0.2687;0.2976;0.3265;0.3554;0.3842;0.4131;0.4420;0.4708;0.4997;0.5286;0.5574;0.5863;0.6152;0.6440;0.6729;0.7018;0.7307;0.7595;0.7884;0.8173;0.8461;0.8750;1.0000" values="60;60;72.54;85.07;97.61;110.14;122.68;135.21;147.75;160.29;172.82;185.36;197.89;210.43;222.96;235.5;248.04;260.57;273.11;285.64;298.18;310.71;323.25;335.79;348.32;360.86;373.39;385.93;398.46;411;411"/><animate attributeName="cy" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0955;0.1244;0.1533;0.1821;0.2110;0.2399;0.2687;0.2976;0.3265;0.3554;0.3842;0.4131;0.4420;0.4708;0.4997;0.5286;0.5574;0.5863;0.6152;0.6440;0.6729;0.7018;0.7307;0.7595;0.7884;0.8173;0.8461;0.8750;1.0000" values="310;310;307.2;304.39;301.55;298.67;295.74;292.73;289.64;286.43;283.1;279.61;275.94;272.04;267.89;263.44;258.61;253.35;247.56;241.13;233.89;225.66;216.17;205.04;191.73;175.47;155.03;128.42;92.15;80;80"/></circle>
<line x1="470" y1="130" x2="470" y2="310" stroke="#e2e8f0" stroke-width="1.5"/>
<line x1="540" y1="130" x2="540" y2="310" stroke="#e2e8f0" stroke-width="1.5"/>
<line x1="610" y1="130" x2="610" y2="310" stroke="#e2e8f0" stroke-width="1.5"/>
<line x1="680" y1="130" x2="680" y2="310" stroke="#e2e8f0" stroke-width="1.5"/>
<line x1="470" y1="300" x2="740" y2="300" stroke="#b8794b" stroke-width="6"><animate attributeName="y1" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0955;0.1244;0.1533;0.1821;0.2110;0.2399;0.2687;0.2976;0.3265;0.3554;0.3842;0.4131;0.4420;0.4708;0.4997;0.5286;0.5574;0.5863;0.6152;0.6440;0.6729;0.7018;0.7307;0.7595;0.7884;0.8173;0.8461;0.8750;1.0000" values="300;300;301.7;303.41;305.14;306.89;308.68;310.51;312.39;314.34;316.37;318.5;320.73;323.1;325.63;328.34;331.28;334.48;338.01;341.92;346.33;351.34;355;355;355;355;355;355;355;355;355"/><animate attributeName="y2" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0955;0.1244;0.1533;0.1821;0.2110;0.2399;0.2687;0.2976;0.3265;0.3554;0.3842;0.4131;0.4420;0.4708;0.4997;0.5286;0.5574;0.5863;0.6152;0.6440;0.6729;0.7018;0.7307;0.7595;0.7884;0.8173;0.8461;0.8750;1.0000" values="300;300;296.59;293.17;289.72;286.21;282.64;278.98;275.21;271.31;267.25;263;258.53;253.79;248.74;243.32;237.44;231.04;223.99;216.15;207.35;197.33;190;190;190;190;190;190;190;190;190"/></line>
<line x1="610" y1="300" x2="610" y2="300" stroke="#e5484d" stroke-width="4"><animate attributeName="y2" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0667;0.0955;0.1244;0.1533;0.1821;0.2110;0.2399;0.2687;0.2976;0.3265;0.3554;0.3842;0.4131;0.4420;0.4708;0.4997;0.5286;0.5574;0.5863;0.6152;0.6440;0.6729;0.7018;0.7307;0.7595;0.7884;0.8173;0.8461;0.8750;1.0000" values="300;300;298.3;296.59;294.86;293.11;291.32;289.49;287.61;285.66;283.63;281.5;279.27;276.9;274.37;271.66;268.72;265.52;261.99;258.08;253.67;248.66;242.89;236.11;228.01;218.11;205.67;200;200;200;200"/></line>
<text x="470" y="120" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">シャドウ マップの 1 テクセル（縦線の間）</text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 0° → 必要なバイアス ∝ tan = 0.0<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;0.0952;0.0955;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 2° → 必要なバイアス ∝ tan = 0.1<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0952;0.0955;0.1241;0.1244;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 5° → 必要なバイアス ∝ tan = 0.1<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1241;0.1244;0.1529;0.1533;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 8° → 必要なバイアス ∝ tan = 0.2<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1529;0.1533;0.1818;0.1821;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 11° → 必要なバイアス ∝ tan = 0.2<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.1818;0.1821;0.2107;0.2110;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 14° → 必要なバイアス ∝ tan = 0.3<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2107;0.2110;0.2395;0.2399;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 17° → 必要なバイアス ∝ tan = 0.3<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2395;0.2399;0.2684;0.2687;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 20° → 必要なバイアス ∝ tan = 0.4<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2684;0.2687;0.2973;0.2976;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 23° → 必要なバイアス ∝ tan = 0.4<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.2973;0.2976;0.3262;0.3265;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 26° → 必要なバイアス ∝ tan = 0.5<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3262;0.3265;0.3550;0.3554;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 28° → 必要なバイアス ∝ tan = 0.6<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3550;0.3554;0.3839;0.3842;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 31° → 必要なバイアス ∝ tan = 0.6<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3839;0.3842;0.4128;0.4131;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 34° → 必要なバイアス ∝ tan = 0.7<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4128;0.4131;0.4416;0.4420;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 37° → 必要なバイアス ∝ tan = 0.8<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4416;0.4420;0.4705;0.4708;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 40° → 必要なバイアス ∝ tan = 0.9<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4705;0.4708;0.4994;0.4997;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 43° → 必要なバイアス ∝ tan = 0.9<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.4994;0.4997;0.5282;0.5286;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 46° → 必要なバイアス ∝ tan = 1.0<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5282;0.5286;0.5571;0.5574;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 49° → 必要なバイアス ∝ tan = 1.2<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5571;0.5574;0.5860;0.5863;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 52° → 必要なバイアス ∝ tan = 1.3<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5860;0.5863;0.6148;0.6152;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 54° → 必要なバイアス ∝ tan = 1.4<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.6148;0.6152;0.6437;0.6440;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 57° → 必要なバイアス ∝ tan = 1.6<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.6437;0.6440;0.6726;0.6729;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 60° → 必要なバイアス ∝ tan = 1.8<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.6726;0.6729;0.7015;0.7018;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 63° → 必要なバイアス ∝ tan = 2.0<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.7015;0.7018;0.7303;0.7307;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 66° → 必要なバイアス ∝ tan = 2.3<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.7303;0.7307;0.7592;0.7595;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 69° → 必要なバイアス ∝ tan = 2.7<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.7592;0.7595;0.7881;0.7884;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 72° → 必要なバイアス ∝ tan = 3.1<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.7881;0.7884;0.8169;0.8173;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 75° → 必要なバイアス ∝ tan = 3.8<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.8169;0.8173;0.8458;0.8461;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="350" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">傾き 78° → 必要なバイアス ∝ tan = 4.7<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.8458;0.8461;0.8747;0.8750;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="384" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">テクセルの中で、面の深度は、傾きに比例して変わる（赤い線の長さ）。それ以上のバイアスが要る。</text>
</svg>

<!-- fig:slope-bias:end -->

## 必要なバイアスを導く {#derive}

シャドウ マップの 1 テクセルは光に垂直な平面で、幅 `t`（ワールドの距離）です。面が光に対して角度 `θ`（法線と光のなす角）で傾いていると、1 テクセルの範囲の中で面の深度は `t · tan θ` だけ変わります。

シャドウ マップは各テクセルの中心の深度だけを保存します。テクセルの端の点は中心より最大で `(t / 2) · tan θ` だけ奥にあります。この点の深度を保存された中心の深度と比べると、自分の面に自分の影が落ちて見えます。この差を覆うバイアスが必要な最小のバイアスです。

<div class="formula">必要なバイアス = (t / 2) · tan θ</div>

Python で傾いた平面の 1 テクセルの中を 1000 点に分けて調べました。`θ = 30°` で `0.289 t`、`60°` で `0.866 t`、`80°` で `2.836 t`、`85°` で `5.715 t` で `0.5 · tan θ` と一致しました。

範囲 100 m、解像度 2048 の太陽のシャドウ マップなら `t = 100 / 2048 ≒ 4.9 cm` です。必要なバイアスは `30°` で約 1.4 cm、`60°` で約 4.2 cm、`80°` で約 13.8 cm、`85°` で約 27.9 cm です。光に平行に近い面では桁違いに大きなバイアスが要ります。

<svg class="fig flow" viewBox="0 0 720 250" role="img" aria-label="面の傾きごとの必要なバイアス。テクセル 4.9 cm のとき、30 度で 1.4 cm、85 度で 27.9 cm"><text x="14" y="22" class="fig-title">必要なバイアス（テクセル 4.9 cm = 範囲 100 m ÷ 2048）</text>
<line x1="60" y1="200" x2="690" y2="200" stroke="currentColor" stroke-width="1.5"/>
<g fill="rgba(76,139,245,0.28)" stroke="#4c8bf5" stroke-width="2"><rect x="100" y="187" width="80" height="13"/><rect x="230" y="162" width="80" height="38"/><rect x="360" y="108" width="80" height="92"/><rect x="490" y="42" width="80" height="158"/></g>
<g style="font-size:12px" text-anchor="middle"><text x="140" y="181">1.4 cm</text><text x="270" y="156">4.2 cm</text><text x="400" y="102">13.8 cm</text><text x="530" y="36">27.9 cm（縦軸は縮めてある）</text>
<text x="140" y="220">θ = 30°</text><text x="270" y="220">60°</text><text x="400" y="220">80°</text><text x="530" y="220">85°</text></g>
<text x="360" y="244" text-anchor="middle" style="font-size:12px">必要量は (t/2)·tan θ。光に平行に近づくほど、急に大きくなる</text></svg>

## ハードウェアで行う {#hardware}

`D3D11_RASTERIZER_DESC` の `SlopeScaledDepthBias` がこれです。ハードウェアが三角形ごとに深度の傾きを計算して、バイアスに自動で反映します。

```cpp
// （コンパイルしていない）シャドウ パスのラスタライザー ステート
D3D11_RASTERIZER_DESC rs = {};
rs.DepthBias = 1000;                  // 定数分（最小の深度刻みの倍数）
rs.SlopeScaledDepthBias = 1.5f;       // 傾き係数。深度の最大の傾きに、この値を掛ける
rs.DepthBiasClamp = 0.01f;            // バイアスの上限（ピーター パンニングの暴走を防ぐ）
device->CreateRasterizerState(&rs, &shadow_rs);
```

バイアスの全体の式は Direct3D の仕様で、次のとおりです。

```text
Bias = DepthBias × r  +  SlopeScaledDepthBias × MaxDepthSlope
Bias は、DepthBiasClamp を超えない
```

`DepthBias × r` は定数バイアスです。`r` は最小の深度の刻みです。`MaxDepthSlope` は三角形の深度の傾きで `max(|∂z/∂x|, |∂z/∂y|)` です（画面空間、つまりシャドウ マップのテクセルあたりの深度の変化）。`SlopeScaledDepthBias` は傾きに掛ける係数です。`DepthBiasClamp` は上限で斜めの面でバイアスが暴走して影が消えるのを防ぎます。

先ほどの式との対応を見ます。`MaxDepthSlope` はテクセル 1 つあたりの深度の変化なので、正規化した値で `tan θ · t / 範囲` です。必要なバイアスは軸に沿った傾きならその 0.5 倍です。斜め方向の傾きではテクセルの角の点で、`0.5 · (|gx| + |gy|)` が必要になり `MaxDepthSlope` の最大 1 倍までです。つまり、係数が 0.5〜1.0 あれば、理論上は足ります。実際には、1〜3 が一般的です。深度の量子化誤差や PCF の広がりのぶんの余裕を見込んでいるからです。

## シェーダーで行う {#shader}

ハードウェアのバイアスはシャドウ パスで書く深度に効きます。メイン パスで比較する側をシェーダーで補正する方法もあります。面の法線と光の方向から傾きを計算します。

```hlsl
Texture2D<float> g_shadow_map : register(t0);
SamplerComparisonState g_shadow_sampler : register(s0);

cbuffer SlopeBiasConstants : register(b0) {
  float4x4 g_world_to_light;
  float3 g_light_dir;          // 光の来る向き（太陽へ向かう単位ベクトル）
  float g_base_bias;           // 定数の下駄。正規化深度。例: 0.0002
  float g_slope_bias;          // 傾きの係数。正規化深度。例: 0.0004
  float g_max_tan;             // tan の上限。例: 10
  float2 _pad;
};

// 法線と光の方向から、深度の傾きに比例したバイアスを求める
float SlopeScaledBias(float3 normal, float3 light_dir) {
  float cos_theta = saturate(dot(normal, light_dir));
  float sin_theta = sqrt(1.0 - cos_theta * cos_theta);
  float tan_theta = sin_theta / max(cos_theta, 0.05);          // tan(光と法線の角度)。斜めほど大きい
  return g_base_bias + g_slope_bias * min(tan_theta, g_max_tan);   // 上限で暴走を防ぐ
}

float4 SlopeBiasPS(float3 world_pos : TEXCOORD0, float3 normal : TEXCOORD1) : SV_Target {
  float4 clip = mul(float4(world_pos, 1.0), g_world_to_light);
  float3 ndc = clip.xyz / clip.w;
  float2 uv = float2(ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5);
  float bias = SlopeScaledBias(normalize(normal), g_light_dir);
  float lit = g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, uv, ndc.z - bias);
  return float4(lit, lit, lit, 1.0);
}
```

`tan θ` は光に正面で 0、平行に近づくと無限大に近づきます。`max(cos_theta, 0.05)` と `min(tan_theta, g_max_tan)` で暴走を防ぎます。`g_slope_bias` の値は導出から決められます。正射影なら `0.5 · t / 範囲` が理論値です。範囲 100 m、解像度 2048 なら約 `2.4 × 10⁻⁴` です。例の 0.0004 は余裕を見込んだ値です。

ハードウェア（`SlopeScaledDepthBias`）は設定が簡単で、三角形ごとに正確な傾きを使えます。ただし、シャドウ パスの深度に効きます。値の意味が直感的でありません（プリミティブごとに傾きが決まる）。シェーダー（法線と光から）はメイン パス側で調整できて、値の意味が明確です。法線が必要でカスケードごとの調整が要ります。

!!! note "確かめた範囲"
    HLSL は `fxc`（`ps_5_0`）で、`SlopeBiasPS` をコンパイルしてエラーが出ないことを確かめました。C++ はコンパイルしていません。必要なバイアスの式は Python で 1 テクセルの中を調べて確かめました（1 次元）。2 次元の斜め方向は上限の見積もりです。GPU での描画は確認していません。

## 限界 {#limits}

傾き依存バイアスはほとんどの場面で有効ですが、次の問題が残ります。

- 光に平行に近い面でバイアスが大きくなって、ピーター パンニングが出ます。`85°` で約 28 cm です。
- PCF を広く取ると範囲の中で面の深度がさらに変化して、傾き依存だけでは足りません（[Receiver Plane Bias](receiver-plane-bias.md)）。
- 曲面では 1 つの三角形の中で傾きが一定とは限りません。

法線オフセット（[Normal Offset](normal-offset.md)）と併用すると、バイアスを小さく保ったまま自己影を抑えられます。

## よくあるミス {#mistakes}

??? failure "`N·L` が 0 に近い面で、バイアスが無限大になって影が消える"
    原因は `tan θ` が発散することです。`max(cos_theta, 0.05)` で割る値に下限を設けて `tan` にも上限を設けます。ハードウェアなら `DepthBiasClamp` を設定します。

??? failure "`SlopeScaledDepthBias` を上げても、斜めの面のアクネが残る"
    原因は PCF のカーネルが広く、傾きだけでは足りないことです。受け手平面バイアスでサンプルごとに深度を補正します。

??? failure "深度の形式を変えたら、影が変わった"
    原因は `DepthBias` の単位が深度の形式（`D24_UNORM` と `D32_FLOAT`）で違うことです。`SlopeScaledDepthBias` は形式に依存せず傾きに掛ける係数ですが、`DepthBias` は見直します。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] 必要なバイアスは `(t/2)·tan θ` で、傾きに比例します。
    - [x] `SlopeScaledDepthBias` は理論上 0.5〜1.0 で足りて、実用は 1〜3 です。
    - [x] `tan θ` は発散するので、上限を設けます。
    - [x] 広い PCF や光に平行な面には、受け手平面バイアスや法線オフセットを併用します。

## 参考 {#references}

このページは次の資料を読まずに書きました。必要なバイアスの式は幾何から自分で導いて、数値で確かめました。

- Microsoft Learn, "D3D11_RASTERIZER_DESC"（`DepthBias`、`SlopeScaledDepthBias`、`DepthBiasClamp`）
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"（Direct3D 11 のドキュメント。バイアス、平行光源、PCF）
- Isidoro, "Shadow Mapping: GPU-based Tips and Techniques", Game Developers Conference 2006（レシーバー平面の深度バイアスなど）
- Brabec, Annen, Seidel, "Practical Shadow Mapping", Journal of Graphics Tools, Vol. 7, No. 4, 2002

## 関連ページ

- [Shadow Bias](index.md)
- [Constant Bias](constant-bias.md)
- [Normal Offset](normal-offset.md)
