---
title: Slope-Scale Bias
tags:
  - 描画
---

# Slope-Scale Bias

<strong>面が光に対して斜めなほどアクネが出やすく、必要なバイアスは大きくなります</strong>。面の傾き（深度の勾配）に比例してバイアスを増やすのがスロープ スケール バイアスです。ハードウェアのラスタライザが、これをサポートしているのでシャドウ マップを描くときに設定するだけで使えます。このページでは傾きとアクネの関係・ハードウェアの設定（`SlopeScaledDepthBias`）・シェーダーでの計算を説明します。

!!! tip "ポイント"
    - スロープ スケール ＝ 面の傾きに比例して、バイアスを増やす。
    - ラスタライザ ステートの `SlopeScaledDepthBias` で設定できる（深度パスで焼き込み）。
    - シェーダー側では、`tan(acos(N·L))` で傾きを計算してバイアスを決められる。
    - 傾きが極端な面は、バイアスが爆発するので上限を設ける。

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

## 対策 2：スロープ スケール バイアス
<strong>面の傾き（深度の勾配）に比例</strong>して、バイアスを大きくします。Direct3D のラスタライザ ステートに、機能があります。

```cpp
D3D11_RASTERIZER_DESC desc = {};
desc.DepthBias = 100;
desc.SlopeScaledDepthBias = 2.0f;
desc.DepthBiasClamp = 0.01f;
```

ラスタライザ ステートの 3 つの項目の意味です。`DepthBias` は定数で深度バッファの最小単位（精度）の倍数です。D32_FLOAT の場合は、深度値の大きさに応じて変わります。`SlopeScaledDepthBias` はポリゴンの画面上での深度の勾配（`max(|dz/dx|, |dz/dy|)`）に、この値を掛けて加えます。`DepthBiasClamp` はバイアスの上限で極端に傾いた面で暴走しないようにします。

この設定はシャドウ マップを描くときに使います（書き込む深度にオフセットを足す）。

スロープ スケール バイアスの利点は、斜めの面ほど自動で大きくなること、ハードウェアが処理するので追加のシェーダー コストがないことです。欠点は浮動小数点の深度では定数バイアスの意味が変わること（値の大きさで単位が変わる）、すべての面に同じ係数を使うので、極端に斜めな面では結局浮いてしまうことです。

## 傾き依存バイアスとは

面が <strong>光に対して斜めになるほど</strong>、シャドウ マップの 1 画素の中で、深度が大きく変わります。その変化の大きさ（深度の傾き）に、比例してバイアスを大きくするのが、傾き依存（slope-scale）バイアスです。

```text
バイアス = 定数 + 傾き係数 × 深度の傾き
```

| 面の向き | 深度の傾き | バイアス |
| --- | --- | --- |
| 光に正面 | 小さい | 小さい |
| 斜め | 中くらい | 中くらい |
| 光とほぼ平行 | 非常に大きい | 大きい |

## ハードウェアで行う

`D3D11_RASTERIZER_DESC` の <strong>`SlopeScaledDepthBias`</strong> がこれです。ハードウェアが三角形ごとに、深度の傾きを計算して自動で、バイアスに反映します。

```cpp
D3D11_RASTERIZER_DESC rs = {};
rs.DepthBias = 1000;                  // 定数分
rs.SlopeScaledDepthBias = 1.5f;       // 傾き係数。深度の最大の傾きに、この値を掛ける
rs.DepthBiasClamp = 0.01f;            // バイアスの、上限（ピーター パンニングの、暴走を、防ぐ）
device->CreateRasterizerState(&rs, &shadow_rs);
```

バイアスの全体の式は次のとおりです（Direct3D の、仕様）。

```text
Bias = DepthBias × r  +  SlopeScaledDepthBias × MaxDepthSlope
Bias は、DepthBiasClamp を、超えない
```

| 値 | 意味 |
| --- | --- |
| `DepthBias × r` | 定数バイアス（`r` は最小の、深度の刻み） |
| `MaxDepthSlope` | 三角形の深度の傾き（`max(|∂z/∂x|, |∂z/∂y|)`、画面空間での変化） |
| `SlopeScaledDepthBias` | 傾きに掛ける係数。1〜3 が一般的 |
| `DepthBiasClamp` | 上限。非常に斜めの面でバイアスが暴走して影が、消えるのを防ぐ |

### 傾きの直感

光にほぼ平行な面（朝夕の光が地面に、すれすれ）ではシャドウ マップの 1 画素が、地面の非常に長い範囲を覆い、その範囲での深度の変化が大きい。ハードウェアがその大きな傾きに、比例してバイアスを自動で足します。

## シェーダーで行う

ハードウェアのバイアスは <strong>シャドウ パスで、書く深度</strong>に効きます。メイン パスで比較する側を、シェーダーで補正する方法もあります。面の法線と光の方向から傾きを、計算します。

```hlsl
// 法線と光の方向から、深度の傾きに、比例した、バイアスを求める。
float SlopeScaledBias(float3 normal, float3 light_dir, float base_bias, float slope_bias) {
  float cos_theta = saturate(dot(normal, -light_dir));
  float sin_theta = sqrt(1.0 - cos_theta * cos_theta);
  float tan_theta = sin_theta / max(cos_theta, 0.05);          // tan(光と法線の角度)。斜めほど大きい
  return base_bias + slope_bias * min(tan_theta, 10.0);         // 暴走を、防ぐ上限
}

float bias = SlopeScaledBias(N, g_light_dir, 0.0005, 0.0005);
float lit = g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, coord.xy, coord.z - bias);
```

`tan θ` は 光に正面で 0、平行に近づくと無限大に近づきます。上限（`min(…, 10)`）を入れて暴走を防ぎます。

| 方式 | 長所 | 短所 |
| --- | --- | --- |
| ハードウェア（`SlopeScaledDepthBias`） | 設定が簡単。三角形ごとに正確な傾きを使える | シャドウ パスの深度に効く。値の意味が直感的でない（プリミティブごとに傾きが、決まる） |
| シェーダー（法線と光から） | メイン パス側で、調整できる。値の意味が明確 | 法線が必要。カスケードごとの調整が必要 |

## 限界

傾き依存バイアスは <strong>ほとんどの場面で、有効</strong>ですが次の問題が残ります。

| 問題 | 内容 |
| --- | --- |
| 非常に斜めの面 | バイアスが非常に、大きくなりピーター パンニング |
| PCF を広く取る | PCF の、範囲の中で面の深度はさらに変化する。傾き依存だけでは足りない（[Receiver Plane Bias](receiver-plane-bias.md)） |
| 曲面 | 1 つの三角形内で傾きが、一定とは限らない |

法線オフセット（[Normal Offset](normal-offset.md)）と、併用するとバイアスを小さく、保ったまま自己影を抑えられます。

## よくあるミス

??? failure "`N·L` が 0 に近い面で、バイアスが無限大になって影が消える"
    <strong>上限（クランプ）を設ける</strong>。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 傾きに比例してバイアスを増やす
    - [x] ハードウェアの設定で簡単に使える。上限を設ける

## 参考

- Microsoft Learn, "D3D11_RASTERIZER_DESC"（`DepthBias`、`SlopeScaledDepthBias`、`DepthBiasClamp`）
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"（Direct3D 11 のドキュメント。バイアス、平行光源、PCF）
- Isidoro, "Shadow Mapping: GPU-based Tips and Techniques", Game Developers Conference 2006（レシーバー平面の深度バイアスなど）
- Brabec, Annen, Seidel, "Practical Shadow Mapping", Journal of Graphics Tools, Vol. 7, No. 4, 2002

## 関連ページ

- [Shadow Bias](index.md)
- [Constant Bias](constant-bias.md)
- [Normal Offset](normal-offset.md)
