---
title: Fighting Noise
tags:
  - 描画
---

# Fighting Noise

**画素あたり 1〜2 本のレイでは、間接光はノイズだらけ**です。**このノイズを、時間蓄積と空間フィルタで消す**のが**デノイズ**です。このページでは、**ノイズの原因と、デノイズの方針**を説明します。

!!! tip "ポイント"
    - **ノイズの原因 ＝ サンプル数が少ない**。
    - **時間蓄積：前フレームの結果と混ぜる**。
    - **空間フィルタ：法線・深度が近い画素だけ平均**。
    - **ゴーストとぼやけが、トレードオフ**。

## ノイズとの戦い
**画素あたり 1 本**のレイでは、**非常にノイズが多い**です。

### 重要度サンプリング

サンプル数が足りないなら、<strong>寄与の大きい方向に、サンプルを多く割り当てる</strong>のが、ノイズを減らす王道です。これを重要度サンプリングと呼びます。

基本は、余弦重み付きです。BRDF の余弦に従って方向を選べば、斜めの方向（寄与の小さい方向）にレイを無駄遣いしません。次に、<strong>NEE</strong>（Next Event Estimation）があります。レイがヒットした点で、ライトを直接サンプルして（シャドウ レイを光源に向けて飛ばす）、直接光を確実に拾う方法です。レイが偶然、小さな光源に当たるのを待つのでなく、光源を狙って飛ばすので、ノイズが激減します。さらに、サンプルの並べ方にも工夫が使えます。<strong>ブルー ノイズ</strong>を乱数として使うと、隣り合う画素のサンプルが偏らず、画面全体で誤差が均されます（[Noise Patterns](../../ao/filtering/noise-pattern.md)）。

### デノイズ

重要度サンプリングを使っても、1 画素 1 本のレイでは足りません。ノイズは、後処理の<strong>デノイザ</strong>で消します。主な手法は、段階的に発展してきました。

最も基本の技術は<strong>時間蓄積</strong>です。前のフレームの結果を、動きベクトルで再投影し、今のフレームと混ぜます（[Temporal Accumulation](../../ao/filtering/temporal.md)）。次に<strong>空間フィルタ</strong>で、法線と深度を手がかりに、同じ面の画素だけを平均してぼかします。この 2 つを組み合わせ、さらに「ノイズの大きさ（分散）」を推定して、ノイズが多い画素ほど強くぼかす方式が、<strong>SVGF</strong>（Spatiotemporal Variance-Guided Filtering、Schied ら 2017）です。分散ガイドのおかげで、静止した部分はシャープに、ノイズの多い部分は大きくぼかす、という切り替えが自動でできます。

実用的な製品としては、NVIDIA の <strong>NRD</strong>（ReBLUR・ReLAX）、AMD の FidelityFX Denoiser があります。オフライン向けの <strong>OIDN</strong>（Intel Open Image Denoise）は、ニューラル ネットワークでデノイズします。最近は、<strong>DLSS Ray Reconstruction</strong> のように、ニューラル ネットワークでデノイズとアップスケールを同時に行う方式も出ています。

### ゴーストとぼやけのトレードオフ

デノイズでは、ゴースト（残像）とぼやけの間で、取引が避けられません。履歴を強く使うとノイズは減りますが、動きに対して残像が出ます。履歴を弱くすると残像は減りますが、ノイズが残ります。履歴の妥当性を、法線・深度・輝度の差で検証して、怪しい履歴は捨てる、という工夫が不可欠です（[Temporal Accumulation](../../ao/filtering/temporal.md)）。

<!-- fig:mc-noise-samples:begin -->

<svg class="fig illust motion" data-fig="mc-noise-samples" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-mc-noise-samples" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">ノイズはサンプル数の平方根に反比例: 4 倍の本数で、ノイズは半分</text>
<rect x="70" y="70" width="640" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="230.0" y1="70" x2="230.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="130.0" x2="710" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="390.0" y1="70" x2="390.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="190.0" x2="710" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="550.0" y1="70" x2="550.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="70" y1="250.0" x2="710" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="70" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">ノイズの大きさ 1/√N</text>
<text x="710" y="346" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">1 ピクセルあたりのサンプル数 N</text>
<text x="70.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">1</text>
<text x="198.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">4</text>
<text x="326.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">16</text>
<text x="454.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">64</text>
<text x="582.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">256</text>
<text x="710.0" y="328" text-anchor="middle" style="font-size:11px;font-weight:500;fill:#64748b">1024</text>
<path d="M70.0,81.43 L76.4,89.21 L82.8,96.74 L89.2,104.0 L95.6,111.02 L102.0,117.8 L108.4,124.34 L114.8,130.67 L121.2,136.78 L127.6,142.68 L134.0,148.38 L140.4,153.88 L146.8,159.2 L153.2,164.34 L159.6,169.3 L166.0,174.09 L172.4,178.72 L178.8,183.19 L185.2,187.51 L191.6,191.68 L198.0,195.71 L204.4,199.61 L210.8,203.37 L217.2,207.0 L223.6,210.51 L230.0,213.9 L236.4,217.17 L242.8,220.33 L249.2,223.39 L255.6,226.34 L262.0,229.19 L268.4,231.94 L274.8,234.6 L281.2,237.17 L287.6,239.65 L294.0,242.05 L300.4,244.36 L306.8,246.6 L313.2,248.76 L319.6,250.84 L326.0,252.86 L332.4,254.8 L338.8,256.68 L345.2,258.5 L351.6,260.25 L358.0,261.95 L364.4,263.59 L370.8,265.17 L377.2,266.69 L383.6,268.17 L390.0,269.59 L396.4,270.97 L402.8,272.3 L409.2,273.58 L415.6,274.82 L422.0,276.02 L428.4,277.18 L434.8,278.3 L441.2,279.38 L447.6,280.42 L454.0,281.43 L460.4,282.4 L466.8,283.34 L473.2,284.25 L479.6,285.13 L486.0,285.97 L492.4,286.79 L498.8,287.58 L505.2,288.35 L511.6,289.08 L518.0,289.8 L524.4,290.49 L530.8,291.15 L537.2,291.79 L543.6,292.41 L550.0,293.01 L556.4,293.59 L562.8,294.15 L569.2,294.69 L575.6,295.21 L582.0,295.71 L588.4,296.2 L594.8,296.67 L601.2,297.12 L607.6,297.56 L614.0,297.99 L620.4,298.4 L626.8,298.79 L633.2,299.17 L639.6,299.54 L646.0,299.9 L652.4,300.24 L658.8,300.57 L665.2,300.9 L671.6,301.21 L678.0,301.51 L684.4,301.8 L690.8,302.07 L697.2,302.34 L703.6,302.61 L710.0,302.86" fill="none" stroke="#e5484d" stroke-width="4" opacity="1"/>
<circle cx="70.0" cy="81.43" r="7" fill="#1f2937"><animate attributeName="cx" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0920;0.1040;0.1160;0.1280;0.1400;0.1520;0.1640;0.1760;0.1880;0.2000;0.2120;0.2240;0.2360;0.2480;0.2600;0.2720;0.2840;0.2960;0.3080;0.3200;0.3320;0.3440;0.3560;0.3680;0.3800;0.3920;0.4040;0.4160;0.4280;0.4400;0.4520;0.4640;0.4760;0.4880;0.5000;0.5120;0.5240;0.5360;0.5480;0.5600;0.5720;0.5840;0.5960;0.6080;0.6200;0.6320;0.6440;0.6560;0.6680;0.6800;0.6920;0.7040;0.7160;0.7280;0.7400;0.7520;0.7640;0.7760;0.7880;0.8000;1.0000" values="70;70;80.67;91.33;102;112.67;123.33;134;144.67;155.33;166;176.67;187.33;198;208.67;219.33;230;240.67;251.33;262;272.67;283.33;294;304.67;315.33;326;336.67;347.33;358;368.67;379.33;390;400.67;411.33;422;432.67;443.33;454;464.67;475.33;486;496.67;507.33;518;528.67;539.33;550;560.67;571.33;582;592.67;603.33;614;624.67;635.33;646;656.67;667.33;678;688.67;699.33;710;710"/><animate attributeName="cy" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0800;0.0920;0.1040;0.1160;0.1280;0.1400;0.1520;0.1640;0.1760;0.1880;0.2000;0.2120;0.2240;0.2360;0.2480;0.2600;0.2720;0.2840;0.2960;0.3080;0.3200;0.3320;0.3440;0.3560;0.3680;0.3800;0.3920;0.4040;0.4160;0.4280;0.4400;0.4520;0.4640;0.4760;0.4880;0.5000;0.5120;0.5240;0.5360;0.5480;0.5600;0.5720;0.5840;0.5960;0.6080;0.6200;0.6320;0.6440;0.6560;0.6680;0.6800;0.6920;0.7040;0.7160;0.7280;0.7400;0.7520;0.7640;0.7760;0.7880;0.8000;1.0000" values="81.43;81.43;94.26;106.37;117.8;128.58;138.76;148.38;157.45;166.01;174.09;181.72;188.92;195.71;202.13;208.18;213.9;219.29;224.38;229.19;233.72;238;242.05;245.86;249.46;252.86;256.06;259.09;261.95;264.65;267.19;269.59;271.86;274;276.02;277.93;279.73;281.43;283.03;284.55;285.97;287.32;288.6;289.8;290.93;292;293.01;293.96;294.86;295.71;296.52;297.27;297.99;298.66;299.3;299.9;300.47;301;301.51;301.98;302.43;302.86;302.86"/></circle>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1〜4 本: ノイズ 1 → 0.5<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.0797;0.0800;0.2237;0.2240;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">4〜16 本: 0.5 → 0.25<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.2237;0.2240;0.3677;0.3680;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">16〜64 本: 0.25 → 0.13<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.3677;0.3680;0.5117;0.5120;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">64〜256 本: 0.13 → 0.06<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.5117;0.5120;0.6557;0.6560;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="392" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">256〜1024 本: 0.06 → 0.03。ここまで増やしても 1/32<animate attributeName="opacity" dur="12.5s" repeatCount="indefinite" keyTimes="0.0000;0.6557;0.6560;0.7997;0.8000;1.0000" values="0;0;1;1;0;0"/></text>
</svg>

<!-- fig:mc-noise-samples:end -->

## よくあるミス

??? failure "動く光で、間接光が遅れて追いかけてくる"
    **ブレンド率を上げる**・**履歴を拒否する**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **時間蓄積と空間フィルタで、ノイズを消す**

## 参考

- Kajiya, "The Rendering Equation"（SIGGRAPH 1986）
- Ramamoorthi & Hanrahan, "An Efficient Representation for Irradiance Environment Maps"（SIGGRAPH 2001）
- Majercik et al., "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"（JCGT 2019）

## 関連ページ

- [Ray-Traced GI](index.md)
- [ReSTIR GI](restir.md)
- [AO Filtering](../../ao/filtering/index.md)
