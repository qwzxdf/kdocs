---
title: Self-Occlusion
tags:
  - 描画
---

# Self-Occlusion

**平らな面なのに、縞や斑点が出る**のが**自己遮蔽の失敗**です。**深度バッファの精度が足りず、自分自身の面が、サンプルを遮ると判定される**ためです。**バイアス（わずかな余裕）や、法線に沿った半球**で**防ぎます**。このページでは、**自己遮蔽の原因・バイアス・法線方向の半球**を説明します。

!!! tip "ポイント"
    - **自己遮蔽 ＝ 自分の面が、サンプルを遮ると誤判定**。
    - **原因 ＝ 深度の精度・面の傾き**。
    - **対策 ＝ バイアス**（**深度の比較に余裕**）・**法線に沿った半球にサンプルを置く**。
    - **バイアスが大きすぎると、細かい凹凸の AO が消える**。

## Self-Occlusion (Stripes and Spots on Flat Surfaces) {#自己遮蔽平らな面の縞斑点}
### Symptoms {#症状}

**平らな床や壁**に**縞模様・斑点**が出ます。特に**カメラから遠い場所**や**斜めから見た面**に出やすいです。

### Cause: Depth Quantization and Surface Slope {#原因深度の量子化と面の傾き}

SSAO は、画素 p の周りに点を撒き、<strong>「その点の深度が、バッファに書かれた深度より奥にあるか」</strong>を調べます。奥にあれば、その点は「何かの裏側に隠れている」＝「遮蔽されている」と数えます。ここで、p 自身が乗っている平らな面を考えてください。p の隣の画素に撒いた点は、<strong>平らな面の上</strong>にほぼ乗っています。理屈では、バッファの深度と点の深度は同じ値のはずです。

ところが、実際の値には<strong>誤差</strong>が乗ります。誤差の出どころは 3 つあります。

1. <strong>深度の量子化</strong>。24 ビットの固定小数点深度は、遠いほど 1 刻みが粗くなります。たとえば近クリップ 0.1 m・遠クリップ 1000 m の標準 Z では、数十 m 先で 1 刻みが数 mm になり、平らな床が<strong>階段状</strong>になります。この段差が「点は面の裏側」と誤判定され、縞になります。
2. <strong>面の傾き</strong>。面がカメラに対して斜めだと、画面上で 1 画素ずれるだけで、深度が大きく変わります。点を画面座標でサンプルしているので、わずかな位置のずれが、大きな深度差になります。
3. <strong>法線のノイズ</strong>。深度から法線を復元している場合、量子化誤差がそのまま法線の揺れになり、半球の向きがばたつきます。法線マップを含んだ法線を AO に使うと、細かい凹凸がそのまま遮蔽になり、床の模様が AO に焼き付きます。

遠くほど、斜めの面ほど出やすいのは、1 と 2 の誤差が大きくなるためです。

<!-- fig:bias-quant:begin -->

<svg class="fig illust motion" data-fig="bias-quant" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-bias-quant" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">自己遮蔽: 深度の丸め誤差より、バイアスが小さいと、平らな面が、自分で自分を暗くする(縞・斑点)</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">傾いた平らな床。深度を、段(1/16・1/64・1/256)に丸めて保存する。床の上のサンプル点が、丸めた深度に隠されて、誤って「遮蔽」と判定される割合</text>
<rect x="30" y="96" width="700" height="280" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① バイアスと、誤って遮蔽と判定される割合</text>
<line x1="70.0" y1="350" x2="710.0" y2="350" stroke="#e2e8f0" stroke-width="1.2"/>
<text x="64.0" y="354" text-anchor="end" style="font-size:10px;font-weight:500;fill:#64748b">0%</text>
<line x1="70.0" y1="295.0" x2="710.0" y2="295.0" stroke="#e2e8f0" stroke-width="1.2"/>
<text x="64.0" y="299.0" text-anchor="end" style="font-size:10px;font-weight:500;fill:#64748b">25%</text>
<line x1="70.0" y1="240.0" x2="710.0" y2="240.0" stroke="#e2e8f0" stroke-width="1.2"/>
<text x="64.0" y="244.0" text-anchor="end" style="font-size:10px;font-weight:500;fill:#64748b">50%</text>
<path d="M70.0,237.07 L86.0,240.0 L102.0,243.67 L118.0,246.23 L134.0,249.17 L150.0,252.47 L166.0,255.4 L182.0,258.33 L198.0,262.0 L214.0,265.3 L230.0,268.6 L246.0,271.9 L262.0,274.83 L278.0,278.13 L294.0,282.17 L310.0,285.47 L326.0,288.77 L342.0,291.7 L358.0,295.0 L374.0,298.3 L390.0,301.97 L406.0,305.27 L422.0,307.47 L438.0,310.77 L454.0,313.33 L470.0,316.27 L486.0,319.93 L502.0,322.5 L518.0,325.07 L534.0,328.37 L550.0,330.93 L566.0,333.5 L582.0,337.17 L598.0,340.1 L614.0,342.67 L630.0,345.6 L646.0,348.17 L662.0,350.0 L678.0,350.0 L694.0,350.0 L710.0,350.0" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="0;0;1;1"/></path>
<text x="670.0" y="323.6" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d" opacity="0">深度 1/16 刻み<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,239.27 L86.0,251.37 L102.0,264.57 L118.0,276.67 L134.0,287.3 L150.0,298.67 L166.0,310.03 L182.0,321.77 L198.0,335.7 L214.0,347.8 L230.0,350.0 L246.0,350.0 L262.0,350.0 L278.0,350.0 L294.0,350.0 L310.0,350.0 L326.0,350.0 L342.0,350.0 L358.0,350.0 L374.0,350.0 L390.0,350.0 L406.0,350.0 L422.0,350.0 L438.0,350.0 L454.0,350.0 L470.0,350.0 L486.0,350.0 L502.0,350.0 L518.0,350.0 L534.0,350.0 L550.0,350.0 L566.0,350.0 L582.0,350.0 L598.0,350.0 L614.0,350.0 L630.0,350.0 L646.0,350.0 L662.0,350.0 L678.0,350.0 L694.0,350.0 L710.0,350.0" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2091;0.2093;1.0000" values="0;0;1;1"/></path>
<text x="238.0" y="306.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28" opacity="0">深度 1/64 刻み<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2091;0.2093;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,243.3 L86.0,289.13 L102.0,336.43 L118.0,350.0 L134.0,350.0 L150.0,350.0 L166.0,350.0 L182.0,350.0 L198.0,350.0 L214.0,350.0 L230.0,350.0 L246.0,350.0 L262.0,350.0 L278.0,350.0 L294.0,350.0 L310.0,350.0 L326.0,350.0 L342.0,350.0 L358.0,350.0 L374.0,350.0 L390.0,350.0 L406.0,350.0 L422.0,350.0 L438.0,350.0 L454.0,350.0 L470.0,350.0 L486.0,350.0 L502.0,350.0 L518.0,350.0 L534.0,350.0 L550.0,350.0 L566.0,350.0 L582.0,350.0 L598.0,350.0 L614.0,350.0 L630.0,350.0 L646.0,350.0 L662.0,350.0 L678.0,350.0 L694.0,350.0 L710.0,350.0" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3487;0.3488;1.0000" values="0;0;1;1"/></path>
<text x="126.0" y="288.4" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043" opacity="0">深度 1/256 刻み<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3487;0.3488;1.0000" values="0;0;1;1"/></text>
<text x="70.0" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">0.000</text>
<text x="230.0" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">0.009</text>
<text x="390.0" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">0.017</text>
<text x="550.0" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">0.026</text>
<text x="710.0" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">0.034</text>
<text x="710.0" y="384" text-anchor="end" style="font-size:11px;font-weight:500;fill:#64748b">バイアス(深度の単位)</text>
<rect x="750" y="96" width="180" height="280" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="750" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">斑点が消える最小のバイアス</text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1068;0.1070;1.0000" values="0;0;1;1"/><text x="766" y="150" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5484d">深度 1/16 刻み</text>
<text x="766" y="178" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5484d">0.0314</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2463;0.2465;1.0000" values="0;0;1;1"/><text x="766" y="220" text-anchor="start" style="font-size:12px;font-weight:700;fill:#e5aa28">深度 1/64 刻み</text>
<text x="766" y="248" text-anchor="start" style="font-size:22px;font-weight:700;fill:#e5aa28">0.0085</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3859;0.3860;1.0000" values="0;0;1;1"/><text x="766" y="290" text-anchor="start" style="font-size:12px;font-weight:700;fill:#2ea043">深度 1/256 刻み</text>
<text x="766" y="318" text-anchor="start" style="font-size:22px;font-weight:700;fill:#2ea043">0.0026</text>
</g>
<text x="40" y="410" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937">バイアス 0 での、誤遮蔽(%):</text>
<text x="280" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="1">0<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1068;0.1070;1.0000" values="1;1;0;0"/></text>
<text x="280" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">51<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.1068;0.1070;0.2463;0.2465;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">50<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.2463;0.2465;0.3859;0.3860;1.0000" values="0;0;1;1;0;0"/></text>
<text x="280" y="414" text-anchor="start" style="font-size:26px;font-weight:700;fill:#e5484d" opacity="0">48<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.3859;0.3860;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5347;0.5349;1.0000" values="0;0;1;1"/><rect x="40" y="440" width="880" height="70" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="464" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">丸めた深度は、最大で、半分の段ぶん(1/32・1/128・1/512)ずれる。バイアスは、それより大きく</text>
<text x="56" y="487" text-anchor="start" style="font-size:13px;font-weight:700;fill:#1f2937">深度の精度が荒いほど、必要なバイアスが大きい(0.0314 → 0.0026)。大きすぎると、影や遮蔽が、浮く</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">深度バッファは、段階的に丸められている<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">バイアスが小さいと、平らな床が、自分の丸め誤差で、遮蔽と判定される<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.0696;0.0698;0.5347;0.5349;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">精度に合わせて、バイアスを決める(16 ビット深度なら、特に大きく)<animate attributeName="opacity" dur="21.5s" repeatCount="indefinite" keyTimes="0.0000;0.5347;0.5349;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:bias-quant:end -->

### Fix 1: Allow a Margin with Bias {#対策-1バイアスで余裕を持たせる}

最も基本の対策は、深度の比較に<strong>わずかな余裕（バイアス）</strong>を持たせることです。

<div class="formula">遮蔽 ⇔ z_サンプル &gt; z_バッファ + ε</div>

「同じ値かもしれない」程度の差では遮蔽と数えず、ε 以上はっきり奥にあるときだけ数えます。ε を固定にすると、近くでは大きすぎ（細かい凹凸の AO が消える）、遠くでは小さすぎ（縞が出る）ので、<strong>距離に比例させる</strong>のが定石です（ε = β · z。Alchemy AO・SAO の β）。

バイアスは大きいほど安全ですが、大きすぎると、壁と床の継ぎ目や、物の接地面のような<strong>本来暗くなるべき浅い隙間</strong>の AO まで消えます。縞が消える最小の値を探して決めてください。

### Fix 2: Use a Hemisphere Along the Normal {#対策-2法線に沿った半球にする}

球状にサンプルを撒く古い方式（[Crytek SSAO](../ssao-crytek.md)）では、平らな面でも点の半分が面の内側に入り、<strong>平らな面が灰色</strong>になります。サンプルを<strong>法線側の半球</strong>だけに撒けば、平らな面の AO は 0（遮蔽なし）になります（[Hemisphere SSAO](../ssao-hemisphere.md)）。このとき使う法線は、法線マップ込みのものでなく、<strong>メッシュ本来のジオメトリ法線</strong>を使います。細かい模様まで遮蔽にしたくないためです。

### Fix 3: Ensure Precision {#対策-3精度を確保する}

* <strong>32 ビット浮動小数点の深度</strong>と reverse-Z を使う。遠くでも誤差が小さい。
* 比較は、非線形の深度値ではなく、<strong>ビュー空間の z（線形深度）</strong>で行う。非線形深度の誤差を、比較の前に増幅させない。
* SAO のように深度から位置を復元する方式では、復元した位置の誤差が縞になるので、深度を 2 チャンネルに分けて持つなど、精度を保つ工夫がある（[SAO](../sao.md)）。

### Better Approach: Bias Based on Surface Slope {#より良いやり方面の傾きに応じたバイアス}

固定のバイアスの限界を超えるには、<strong>面の傾き（法線とカメラ方向の角度）に応じて</strong>バイアスを変えます。斜めの面ほど深度の勾配が大きいので、勾配に比例した余裕を足します。これは、シャドウ マップの[スロープ スケール バイアス](../../shadows/bias/slope-scale-bias.md)とまったく同じ考え方です。影と AO は「深度の比較に誤差が混じる」という同じ問題を抱えているので、バイアスの道具立ても共通です。

そのうえで最後に、<strong>バイラテラル ブラー</strong>で残った細かい斑点を均します（[Bilateral Blur](../filtering/bilateral-blur.md)）。ブラーは根本の解決ではなく仕上げです。ブラーに頼って縞を消すと、ぼかしの強さで他の細部まで消えるので、先にバイアスと精度を直してください。

### Troubleshooting Steps {#確認の手順}

遠い平らな床だけが映る視点にして、AO のみを出します。縞が出ていれば、バイアスの係数 β を少しずつ上げ、縞が消えた値の 1.2 倍程度に決めます。近距離の壁の隅が暗いまま残っているかも、同時に確認してください。

## Common Mistakes {#よくあるミス}

??? failure "平らな床に、縞模様の AO が出る"
    **バイアスを入れる**、**法線に沿った半球**にする。

## Key Takeaways {#これだけ覚える}

!!! abstract "まとめ"
    - [x] **自分の面を、遮蔽物と誤判定**
    - [x] **バイアス・法線半球で防ぐ**

## References {#参考}

- Mittring, "Finding Next Gen: CryEngine 2"（SIGGRAPH 2007）
- Jimenez et al., "Practical Real-Time Strategies for Accurate Indirect Occlusion"（SIGGRAPH 2016）

## Related Pages {#関連ページ}

- [AO Artifacts](index.md)
- [Halo](halo.md)
- [Hemisphere SSAO](../ssao-hemisphere.md)
