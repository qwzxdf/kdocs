---
title: Reinhard
tags:
  - 描画
---

# Reinhard

**Reinhard** は、**もっとも簡単なトーンマップ**です。**式は `x / (1 + x)` だけ**で**どれだけ明るい値も、1 を超えずに 0〜1 に収まります**。**実装が 1 行**で済むので**最初の一歩**に向きますが、**中間調まで圧縮されて、絵が眠くなりやすい**ので、**見た目の目標が決まったら、フィルミックなどに替えます**。このページでは、<strong>式の性質・白点付きの拡張・チャンネルごとと輝度ベース・改良（より良いやり方）</strong>を説明します。

!!! tip "ポイント"
    - 式 ＝ <strong>`c = x / (1 + x)`</strong>。<strong>どれだけ明るくても 1 に漸近</strong>（飽和しない）。
    - <strong>x = 1 で 0.5</strong>。<strong>中間調が持ち上がり、コントラストが低い</strong>。
    - <strong>拡張版</strong>は<strong>白点 L_w</strong>を決め、<strong>そこでちょうど 1</strong>。<strong>簡単で見た目が良くなる</strong>。
    - <strong>輝度にだけ掛ける</strong>と<strong>色相を保てる</strong>が、<strong>鮮やかな明部が飽和しすぎる</strong>ことがある。
    - <strong>より良いやり方</strong>：<strong>白点付き ＋ 輝度ベースで色を保つ ＋ 軽いコントラストの調整</strong>。

## 式と形

<div class="formula">c = x / (1 + x)</div>

```hlsl
float3 Reinhard(float3 x) {
  return x / (1.0 + x);
}
```

| 入力 x | 出力 c |
| --- | --- |
| **0** | **0** |
| **0.5** | **0.33** |
| **1** | **0.50** |
| **2** | **0.67** |
| **8** | **0.89** |
| **100** | **0.99** |

**x が大きくなるほど増え方が緩やか**になり、**1 に近づきます**。**どんな明るさでも 1 を超えない**ので、**明部が真っ白に潰れる（クランプ）ことはありません**。

<!-- fig:tonemap-reinhard:begin -->

<svg class="fig illust motion" data-fig="tonemap-reinhard" viewBox="0 0 780 360" role="img"><rect x="0" y="0" width="780" height="360" rx="14" fill="#ffffff"/>
<defs><marker id="arr-tonemap-reinhard" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">Reinhard:x / (1 + x)。どんなに明るくても 1 を超えない</text>
<rect x="50" y="70" width="430" height="240" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>
<line x1="157.5" y1="70" x2="157.5" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="130.0" x2="480" y2="130.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="265.0" y1="70" x2="265.0" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="190.0" x2="480" y2="190.0" stroke="#e2e8f0" stroke-width="1"/>
<line x1="372.5" y1="70" x2="372.5" y2="310" stroke="#e2e8f0" stroke-width="1"/>
<line x1="50" y1="250.0" x2="480" y2="250.0" stroke="#e2e8f0" stroke-width="1"/>
<text x="480" y="330" text-anchor="end" style="font-size:12px;font-weight:500;fill:#64748b">入力 x</text>
<text x="50" y="62" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">出力</text>
<path d="M50.0,310.0 L56.72,280.0 L63.44,250.0 L70.16,220.0 L76.88,190.0 L83.59,160.0 L90.31,130.0 L97.03,100.0 L103.75,70.0 L110.47,70.0 L117.19,70.0 L123.91,70.0 L130.62,70.0 L137.34,70.0 L144.06,70.0 L150.78,70.0 L157.5,70.0 L164.22,70.0 L170.94,70.0 L177.66,70.0 L184.38,70.0 L191.09,70.0 L197.81,70.0 L204.53,70.0 L211.25,70.0 L217.97,70.0 L224.69,70.0 L231.41,70.0 L238.12,70.0 L244.84,70.0 L251.56,70.0 L258.28,70.0 L265.0,70.0 L271.72,70.0 L278.44,70.0 L285.16,70.0 L291.88,70.0 L298.59,70.0 L305.31,70.0 L312.03,70.0 L318.75,70.0 L325.47,70.0 L332.19,70.0 L338.91,70.0 L345.62,70.0 L352.34,70.0 L359.06,70.0 L365.78,70.0 L372.5,70.0 L379.22,70.0 L385.94,70.0 L392.66,70.0 L399.38,70.0 L406.09,70.0 L412.81,70.0 L419.53,70.0 L426.25,70.0 L432.97,70.0 L439.69,70.0 L446.41,70.0 L453.12,70.0 L459.84,70.0 L466.56,70.0 L473.28,70.0 L480.0,70.0" fill="none" stroke="#64748b" stroke-width="3" opacity="1" stroke-dasharray="5 4"/>
<path d="M50.0,310.0 L56.72,283.33 L63.44,262.0 L70.16,244.55 L76.88,230.0 L83.59,217.69 L90.31,207.14 L97.03,198.0 L103.75,190.0 L110.47,182.94 L117.19,176.67 L123.91,171.05 L130.62,166.0 L137.34,161.43 L144.06,157.27 L150.78,153.48 L157.5,150.0 L164.22,146.8 L170.94,143.85 L177.66,141.11 L184.38,138.57 L191.09,136.21 L197.81,134.0 L204.53,131.94 L211.25,130.0 L217.97,128.18 L224.69,126.47 L231.41,124.86 L238.12,123.33 L244.84,121.89 L251.56,120.53 L258.28,119.23 L265.0,118.0 L271.72,116.83 L278.44,115.71 L285.16,114.65 L291.88,113.64 L298.59,112.67 L305.31,111.74 L312.03,110.85 L318.75,110.0 L325.47,109.18 L332.19,108.4 L338.91,107.65 L345.62,106.92 L352.34,106.23 L359.06,105.56 L365.78,104.91 L372.5,104.29 L379.22,103.68 L385.94,103.1 L392.66,102.54 L399.38,102.0 L406.09,101.48 L412.81,100.97 L419.53,100.48 L426.25,100.0 L432.97,99.54 L439.69,99.09 L446.41,98.66 L453.12,98.24 L459.84,97.83 L466.56,97.43 L473.28,97.04 L480.0,96.67" fill="none" stroke="#2563eb" stroke-width="4" opacity="1"/>
<path d="M50.0,310.0 L56.72,283.12 L63.44,261.25 L70.16,243.01 L76.88,227.5 L83.59,214.09 L90.31,202.32 L97.03,191.88 L103.75,182.5 L110.47,174.01 L117.19,166.25 L123.91,159.11 L130.62,152.5 L137.34,146.34 L144.06,140.57 L150.78,135.14 L157.5,130.0 L164.22,125.12 L170.94,120.48 L177.66,116.04 L184.38,111.79 L191.09,107.69 L197.81,103.75 L204.53,99.94 L211.25,96.25 L217.97,92.67 L224.69,89.19 L231.41,85.8 L238.12,82.5 L244.84,79.27 L251.56,76.12 L258.28,73.03 L265.0,70.0 L271.72,70.0 L278.44,70.0 L285.16,70.0 L291.88,70.0 L298.59,70.0 L305.31,70.0 L312.03,70.0 L318.75,70.0 L325.47,70.0 L332.19,70.0 L338.91,70.0 L345.62,70.0 L352.34,70.0 L359.06,70.0 L365.78,70.0 L372.5,70.0 L379.22,70.0 L385.94,70.0 L392.66,70.0 L399.38,70.0 L406.09,70.0 L412.81,70.0 L419.53,70.0 L426.25,70.0 L432.97,70.0 L439.69,70.0 L446.41,70.0 L453.12,70.0 L459.84,70.0 L466.56,70.0 L473.28,70.0 L480.0,70.0" fill="none" stroke="#7c3aed" stroke-width="3" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4758;0.4762;1.0000" values="0;0;1;1"/></path>
<text x="297.25" y="178.0" text-anchor="start" style="font-size:12px;font-weight:700;fill:#7c3aed" opacity="0">拡張版（白色点 4）:x=4 で 1<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4758;0.4762;1.0000" values="0;0;1;1"/></text>
<text x="265.0" y="218.8" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2563eb">Reinhard</text>
<circle cx="50.0" cy="310.0" r="7" fill="#2563eb" stroke="#ffffff" stroke-width="1.5"><animate attributeName="cx" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0929;0.1095;0.1262;0.1429;0.1595;0.1762;0.1929;0.2095;0.2262;0.2429;0.2595;0.2762;0.2929;0.3095;0.3262;0.3429;0.3595;0.3762;0.3929;0.4095;0.4262;0.4429;0.4595;0.4762;1.0000" values="50;50;67.92;85.83;103.75;121.67;139.58;157.5;175.42;193.33;211.25;229.17;247.08;265;282.92;300.83;318.75;336.67;354.58;372.5;390.42;408.33;426.25;444.17;462.08;480;480"/><animate attributeName="cy" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0762;0.0929;0.1095;0.1262;0.1429;0.1595;0.1762;0.1929;0.2095;0.2262;0.2429;0.2595;0.2762;0.2929;0.3095;0.3262;0.3429;0.3595;0.3762;0.3929;0.4095;0.4262;0.4429;0.4595;0.4762;1.0000" values="310;310;250;214;190;172.86;160;150;142;135.45;130;125.38;121.43;118;115;112.35;110;107.89;106;104.29;102.73;101.3;100;98.8;97.69;96.67;96.67"/></circle>
<circle cx="50.0" cy="310.0" r="7" fill="#7c3aed" stroke="#ffffff" stroke-width="1.5" opacity="0"><animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4758;0.4762;1.0000" values="0;0;1;1"/><animate attributeName="cx" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4762;0.4905;0.5048;0.5190;0.5333;0.5476;0.5619;0.5762;0.5905;0.6048;0.6190;0.6333;0.6476;0.6619;0.6762;0.6905;0.7048;0.7190;0.7333;0.7476;0.7619;0.7762;0.7905;0.8048;0.8190;1.0000" values="50;50;67.92;85.83;103.75;121.67;139.58;157.5;175.42;193.33;211.25;229.17;247.08;265;282.92;300.83;318.75;336.67;354.58;372.5;390.42;408.33;426.25;444.17;462.08;480;480"/><animate attributeName="cy" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4762;0.4905;0.5048;0.5190;0.5333;0.5476;0.5619;0.5762;0.5905;0.6048;0.6190;0.6333;0.6476;0.6619;0.6762;0.6905;0.7048;0.7190;0.7333;0.7476;0.7619;0.7762;0.7905;0.8048;0.8190;1.0000" values="310;310;248.75;210;182.5;161.43;144.38;130;117.5;106.36;96.25;86.92;78.21;70;70;70;70;70;70;70;70;70;70;70;70;70;70"/></circle>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 0.0<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0758;0.0762;0.0925;0.0929;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 0.3<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0925;0.0929;0.1091;0.1095;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 0.7<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1091;0.1095;0.1258;0.1262;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 1.0<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1258;0.1262;0.1425;0.1429;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 1.3<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1425;0.1429;0.1591;0.1595;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 1.7<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1591;0.1595;0.1758;0.1762;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 2.0<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1758;0.1762;0.1925;0.1929;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 2.3<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1925;0.1929;0.2091;0.2095;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 2.7<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2091;0.2095;0.2258;0.2262;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 3.0<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2258;0.2262;0.2425;0.2429;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 3.3<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2425;0.2429;0.2591;0.2595;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 3.7<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2591;0.2595;0.2758;0.2762;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 4.0<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2758;0.2762;0.2925;0.2929;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 4.3<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2925;0.2929;0.3091;0.3095;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 4.7<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3091;0.3095;0.3258;0.3262;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 5.0<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3258;0.3262;0.3425;0.3429;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 5.3<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3425;0.3429;0.3591;0.3595;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 5.7<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3591;0.3595;0.3758;0.3762;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 6.0<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3758;0.3762;0.3925;0.3929;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 6.3<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3925;0.3929;0.4091;0.4095;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 6.7<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4091;0.4095;0.4258;0.4262;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 7.0<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4258;0.4262;0.4425;0.4429;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 7.3<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4425;0.4429;0.4591;0.4595;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="110" text-anchor="start" style="font-size:18px;font-weight:700;fill:#1f2937" opacity="0">x = 7.7<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4591;0.4595;0.4758;0.4762;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.00<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0758;0.0762;0.0925;0.0929;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.25<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0925;0.0929;0.1091;0.1095;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.40<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1091;0.1095;0.1258;0.1262;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.50<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1258;0.1262;0.1425;0.1429;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.57<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1425;0.1429;0.1591;0.1595;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.62<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1591;0.1595;0.1758;0.1762;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.67<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1758;0.1762;0.1925;0.1929;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.70<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.1925;0.1929;0.2091;0.2095;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.73<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2091;0.2095;0.2258;0.2262;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.75<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2258;0.2262;0.2425;0.2429;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.77<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2425;0.2429;0.2591;0.2595;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.79<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2591;0.2595;0.2758;0.2762;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.80<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2758;0.2762;0.2925;0.2929;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.81<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.2925;0.2929;0.3091;0.3095;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.82<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3091;0.3095;0.3258;0.3262;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.83<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3258;0.3262;0.3425;0.3429;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.84<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3425;0.3429;0.3591;0.3595;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.85<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3591;0.3595;0.3758;0.3762;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.86<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3758;0.3762;0.3925;0.3929;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.86<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.3925;0.3929;0.4091;0.4095;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.87<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4091;0.4095;0.4258;0.4262;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.88<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4258;0.4262;0.4425;0.4429;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.88<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4425;0.4429;0.4591;0.4595;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="146" text-anchor="start" style="font-size:18px;font-weight:700;fill:#2563eb" opacity="0">出力 = 0.88<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4591;0.4595;0.4758;0.4762;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="190" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">x が 1 のとき 0.50<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;0.4758;0.4762;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="190" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">白色点を決めると、その明るさで 1 になる<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4758;0.4762;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="510" y="216" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">x が 8 でも 0.89（白に潰れない）<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.0949;0.0952;0.4758;0.4762;1.0000" values="0;0;1;1;0;0"/></text>
<text x="510" y="216" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b" opacity="0">x = 4 以上は 1（白）に張り付く<animate attributeName="opacity" dur="10.5s" repeatCount="indefinite" keyTimes="0.0000;0.4758;0.4762;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="510" y="262" text-anchor="start" style="font-size:13px;font-weight:500;fill:#e5484d">暗い所も持ち上がる ＝ 眠い絵になりやすい</text>
</svg>

<!-- fig:tonemap-reinhard:end -->

### 性質

| 性質 | 内容 |
| --- | --- |
| **単調増加** | **入力が増えれば、出力も必ず増える**（階調が逆転しない） |
| **飽和しない** | **∞ でも 1 に漸近する**（**真っ白に張り付かない**） |
| **低コントラスト** | **x=1 で 0.5 に持ち上がり、暗部も中間も圧縮される** → **全体が白っぽく、眠い** |
| **白に届かない** | **x がとても大きくても、1 に届かず、「純白」が出ない** |


原典は、Reinhard らの "Photographic Tone Reproduction for Digital Images"（SIGGRAPH 2002）です。論文では、写真家が使う「ゾーン システム」の考え方を取り入れ、画像全体の平均輝度（キー値）に基づいて、全体の明るさを揃えてから、`x / (1 + x)` で圧縮する構成が示されています。式が簡単で、1 行で書けるため、現在でも広く使われています。

原典は、Reinhard らの "Photographic Tone Reproduction for Digital Images"（SIGGRAPH 2002）です。論文では、写真家が使う「ゾーン システム」の考え方を取り入れ、画像全体の平均輝度（キー値）に基づいて、全体の明るさを揃えてから、`x / (1 + x)` で圧縮する構成が示されています。式が簡単で、1 行で書けるため、現在でも広く使われています。

## 白点付き Reinhard

**白点 `L_w`**（**この入力値でちょうど 1 になる**）を決める**拡張**です。

<div class="formula">c = x · (1 + x / L_w²) / (1 + x)</div>

```hlsl
float3 ReinhardExtended(float3 x, float white_point) {
  float3 numerator = x * (1.0 + x / (white_point * white_point));
  return numerator / (1.0 + x);
}
```

`white_point` の値による見た目です。小さい値（例：2）なら、早く白に届き、明るくコントラストが強くなります。大きい値（例：8）なら、ゆっくり白に近づき、ハイライトに余裕が残ります。∞にすると、元の Reinhard と同じです。

**白点を使うと、「真っ白」が出せる**ので**太陽や強い光がちゃんと白く飛びます**。

## チャンネルごと・輝度ベース

**R・G・B に別々に掛ける**と**彩度の高い明るい色の色相がずれます**。**輝度にだけ掛けて、色の比率を保つ**方法もあります。

```hlsl
float Luminance(float3 c) {
  return dot(c, float3(0.2126, 0.7152, 0.0722));
}

float3 ReinhardLuminance(float3 color, float white_point) {
  float l_old = Luminance(color);
  float l_new = l_old * (1.0 + l_old / (white_point * white_point)) / (1.0 + l_old);
  return color * (l_new / max(l_old, 1e-4));
}
```

色の扱いには 2 通りあります。<strong>チャンネルごと</strong>に適用する方式は、明るい色が白へ向かい、フィルムのような見た目になりますが、色相がずれます（オレンジが黄に）。<strong>輝度ベース</strong>の方式は、色相が保たれますが、彩度が高い明部が飽和して、色が濃すぎることがあります。

詳しくは[Preserving Hue](hue-preservation.md)で比べます。

## より良いやり方

**Reinhard をそのまま使う**と**眠い絵**になりがちです。**次の工夫で簡単なまま見栄えを上げられます**。

| 工夫 | 内容 |
| --- | --- |
| **白点を設定する** | **`L_w` を 4〜8 程度**にして、**ハイライトに余裕を持たせつつ、白を出す** |
| **暗部を少し締める** | **トーンマップ後に軽く S 字のコントラスト（`pow(c, 1.1)` など）を掛ける** |
| **輝度ベースで色を保つ** | **鮮やかな色が白に飛びすぎるのを防ぐ**（ただし、飽和に注意） |
| **ブレンド** | **チャンネルごと 50 % ＋ 輝度ベース 50 %**（**ハイブリッド**） |
| **早めに卒業する** | <strong>画作りが固まったら、[フィルミック](filmic-hable.md)・[ACES](aces.md)・[AgX](agx.md)</strong> へ |

## 使いどころ

使いどころの目安です。プロトタイプやデバッグ表示には向きます（1 行で済むため）。UI や 2D 寄りの絵にも向きます（コントラストを強く出さないため）。映画のような画作りの本番には不向きです（眠い絵になるため）。

## よくあるミス

??? failure "Reinhard を掛けたら、全体が白っぽく眠い"
    **曲線の性質**。**白点を設定し、軽くコントラストを足す**、または**別の曲線**へ。

??? failure "白点を 1 にして、明るい所が飽和しすぎる"
    **`white_point` は 1 より十分大きく**（4〜8）。**1 だとほぼクランプ**と同じ。

??? failure "輝度ベースで、鮮やかな光が派手すぎる"
    **チャンネルごととブレンド**する。または**彩度を軽く落とす**。

??? failure "ガンマ変換の後に Reinhard を掛けて、暗部が潰れる"
    **トーンマップはリニアで**。**sRGB は最後**（[Gamma and HDR Output](gamma-srgb.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Reinhard ＝ <strong>`x / (1 + x)`</strong>。<strong>1 行でどんな明るさも 0〜1 に収まる</strong>
    - [x] <strong>中間調が持ち上がって低コントラスト</strong>。<strong>眠い絵になりやすい</strong>
    - [x] <strong>白点付き</strong>で<strong>ちゃんと白を出す</strong>（<strong>4〜8</strong> が目安）
    - [x] <strong>輝度ベース</strong>で<strong>色相を保つ</strong>。ただし<strong>飽和に注意</strong>
    - [x] <strong>本番の画作りは、フィルミック・ACES・AgX へ</strong>

## 参考

- Reinhard et al., "Photographic Tone Reproduction for Digital Images"（SIGGRAPH 2002）
- Reinhard, Stark, Shirley, Ferwerda, "Photographic Tone Reproduction for Images"（同）

## 関連ページ

- [Tone Mapping and Exposure](index.md)
- [Exposure](exposure.md)
- [Filmic (Hable)](filmic-hable.md)
- [Preserving Hue](hue-preservation.md)
