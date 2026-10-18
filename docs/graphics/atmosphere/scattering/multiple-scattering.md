---
title: Multiple Scattering
tags:
  - 描画
---

# Multiple Scattering

**光は、何度も散乱しながら進みます**。**単散乱だけだと、空の暗い部分（影・夕方）が暗すぎます**。**多重散乱を近似して足す**と、**明るさが自然**になります。このページでは、**多重散乱**を説明します。

!!! tip "ポイント"
    - **単散乱だけだと、暗すぎる**。
    - **多重散乱は、全方向からの光の和**。
    - **LUT で、近似的に計算する**（Hillaire 2020）。
    - **空の暗部・影・雲が、自然になる**。

## 多重散乱
**単散乱だけだと夕方や影の側の空が暗くなりすぎます**。**実際には一度散った光が何度も散ります**（**多重散乱**）。**地球の大気では、昼間の空の明るさの 1〜2 割は多重散乱**で、**夕暮れの空の明るさは多重散乱で決まります**。

多重散乱の近似は 3 通りあります。<strong>ambient の底上げ</strong>は、単散乱に一定の環境光を足す方法で、手軽ですが粗いです。<strong>Bruneton の多重散乱</strong>は、散乱の次数ごとに事前計算を繰り返す方法で、正確ですが重いです。<strong>Hillaire の近似</strong>は、多重散乱を、等方で無限級数の閉じた式で近似し、小さな 2D LUT にまとめます。軽く、動的な大気にも使えます。

### Hillaire の近似の考え方

Hillaire の近似は、大胆な仮定に基づいています。「2 次以降の散乱光は、散乱のたびに方向がランダムになり、ほぼ等方（どの方向にも均等）になる」。この仮定のもとでは、2 次散乱の光の量 L₂ は、1 次散乱の量から簡単に求まります。3 次の量は 2 次の何倍か、4 次は 3 次の何倍か、と考えると、次数ごとに、同じ比率 f で減っていくと見なせます。すると、すべての次数を足した多重散乱は、等比級数の和になります。

<div class="formula">L_multi = L₂ · (1 + f + f² + …) = L₂ / (1 − f)</div>

ここで f は、各散乱で光が次の散乱へ引き継がれる割合です。これは閉じた式なので、無限に足す必要がありません。この式を、高さと太陽の天頂角の 2 つのパラメータに対して事前に計算して 2D の表（多重散乱 LUT）にしておけば、実行時は 1 回引くだけで、多重散乱の寄与が分かります。

この近似の誤差は小さく、特に夕方や、地平線付近の空の明るさで、単散乱だけの場合との差がはっきり出ます。単散乱だけだと、太陽が地平線に近いとき、空が暗すぎる、青みが足りないなどの問題が出ますが、多重散乱を足すと自然な明るさに近づきます。

<!-- fig:multi-scatter-sum:begin -->

<svg class="fig illust motion" data-fig="multi-scatter-sum" viewBox="0 0 960 540" role="img"><rect x="0" y="0" width="960" height="540" rx="14" fill="#ffffff"/>
<defs><marker id="arr-multi-scatter-sum" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="30" y="32" text-anchor="start" style="font-size:22px;font-weight:700;fill:#1f2937">多重散乱: 光は、何度も散る。アルベド(反射する割合)が高いほど、何回目まで足さないと、足りない</text>
<text x="30" y="52" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">1 回目の散乱を 1 とする。散乱 k 回目の光は、アルベド^(k−1)。アルベド 0.5・0.8・0.95 で、合計がどう積み上がるかを計算する</text>
<rect x="30" y="96" width="640" height="280" fill="#ffffff" stroke="#2563eb" stroke-width="1.8" rx="6"/>
<text x="30" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#2563eb">① 散乱を k 回足したときの合計</text>
<text x="70.0" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">1</text>
<text x="169.1304347826087" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">5</text>
<text x="293.04347826086956" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">10</text>
<text x="416.95652173913044" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">15</text>
<text x="540.8695652173913" y="366" text-anchor="middle" style="font-size:10px;font-weight:500;fill:#64748b">20</text>
<path d="M70.0,339.55 L94.78,334.32 L119.57,331.7 L144.35,330.4 L169.13,329.74 L193.91,329.42 L218.7,329.25 L243.48,329.17 L268.26,329.13 L293.04,329.11 L317.83,329.1 L342.61,329.1 L367.39,329.09 L392.17,329.09 L416.96,329.09 L441.74,329.09 L466.52,329.09 L491.3,329.09 L516.09,329.09 L540.87,329.09 L565.65,329.09 L590.43,329.09 L615.22,329.09 L640.0,329.09" fill="none" stroke="#2ea043" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="0;0;1;1"/></path>
<line x1="70" y1="329.09" x2="640" y2="329.09" stroke="#2ea043" stroke-width="1.5" stroke-dasharray="4 4" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;1.0000" values="0;0;1;1"/></line>
<text x="640" y="324.09" text-anchor="end" style="font-size:11px;font-weight:700;fill:#2ea043" opacity="0">上限 2.0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0887;0.0889;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,339.55 L94.78,331.18 L119.57,324.49 L144.35,319.14 L169.13,314.86 L193.91,311.43 L218.7,308.69 L243.48,306.5 L268.26,304.74 L293.04,303.34 L317.83,302.22 L342.61,301.32 L367.39,300.6 L392.17,300.03 L416.96,299.57 L441.74,299.2 L466.52,298.9 L491.3,298.67 L516.09,298.48 L540.87,298.33 L565.65,298.21 L590.43,298.11 L615.22,298.04 L640.0,297.97" fill="none" stroke="#e5aa28" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.2798;0.2800;1.0000" values="0;0;1;1"/></path>
<line x1="70" y1="297.73" x2="640" y2="297.73" stroke="#e5aa28" stroke-width="1.5" stroke-dasharray="4 4" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3020;0.3022;1.0000" values="0;0;1;1"/></line>
<text x="640" y="292.73" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5aa28" opacity="0">上限 5.0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3020;0.3022;1.0000" values="0;0;1;1"/></text>
<path d="M70.0,339.55 L94.78,329.61 L119.57,320.18 L144.35,311.21 L169.13,302.7 L193.91,294.61 L218.7,286.93 L243.48,279.62 L268.26,272.69 L293.04,266.1 L317.83,259.84 L342.61,253.89 L367.39,248.24 L392.17,242.88 L416.96,237.78 L441.74,232.94 L466.52,228.33 L491.3,223.96 L516.09,219.81 L540.87,215.87 L565.65,212.12 L590.43,208.56 L615.22,205.17 L640.0,201.96" fill="none" stroke="#e5484d" stroke-width="3.5" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.4932;0.4933;1.0000" values="0;0;1;1"/></path>
<line x1="70" y1="140.91" x2="640" y2="140.91" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="4 4" opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5154;0.5156;1.0000" values="0;0;1;1"/></line>
<text x="640" y="135.91" text-anchor="end" style="font-size:11px;font-weight:700;fill:#e5484d" opacity="0">上限 20.0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5154;0.5156;1.0000" values="0;0;1;1"/></text>
<rect x="690" y="96" width="240" height="280" fill="#ffffff" stroke="#7c3aed" stroke-width="1.8" rx="6"/>
<text x="690" y="86" text-anchor="start" style="font-size:15px;font-weight:700;fill:#7c3aed">95% に届くまでの回数</text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1022;1.0000" values="0;0;1;1"/><text x="706" y="140" text-anchor="start" style="font-size:13px;font-weight:700;fill:#2ea043">アルベド 0.50</text>
<text x="706" y="168" text-anchor="start" style="font-size:24px;font-weight:700;fill:#2ea043">5 回</text>
<text x="706" y="188" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">1 回だけでは 1/2.0 = 50%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3154;0.3156;1.0000" values="0;0;1;1"/><text x="706" y="216" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">アルベド 0.80</text>
<text x="706" y="244" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5aa28">14 回</text>
<text x="706" y="264" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">1 回だけでは 1/5.0 = 20%</text>
</g>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5287;0.5289;1.0000" values="0;0;1;1"/><text x="706" y="292" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5484d">アルベド 0.95</text>
<text x="706" y="320" text-anchor="start" style="font-size:24px;font-weight:700;fill:#e5484d">59 回</text>
<text x="706" y="340" text-anchor="start" style="font-size:11px;font-weight:500;fill:#64748b">1 回だけでは 1/20.0 = 5%</text>
</g>
<text x="40" y="410" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937">95% に必要な回数:</text>
<text x="240" y="414" text-anchor="start" style="font-size:28px;font-weight:700;fill:#7c3aed" opacity="1">0<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1022;1.0000" values="1;1;0;0"/></text>
<text x="240" y="414" text-anchor="start" style="font-size:28px;font-weight:700;fill:#7c3aed" opacity="0">5<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.1020;0.1022;0.3154;0.3156;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="414" text-anchor="start" style="font-size:28px;font-weight:700;fill:#7c3aed" opacity="0">14<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.3154;0.3156;0.5287;0.5289;1.0000" values="0;0;1;1;0;0"/></text>
<text x="240" y="414" text-anchor="start" style="font-size:28px;font-weight:700;fill:#7c3aed" opacity="0">59<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.5287;0.5289;1.0000" values="0;0;1;1"/></text>
<g opacity="0"><animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.6932;0.6933;1.0000" values="0;0;1;1"/><rect x="40" y="440" width="880" height="70" rx="12" fill="#eff6ff" stroke="#2563eb" stroke-width="2.5"/>
<text x="56" y="464" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1e3a8a">雲(アルベド 0.95 以上)は、1 回の散乱では、全体の 5% しか光らない。20 回以上必要</text>
<text x="56" y="487" text-anchor="start" style="font-size:12px;font-weight:700;fill:#64748b">毎回レイマーチで何十回も散らせるのは無理 → 少数の回数を、減衰を弱めて、足す近似(オクターブ)を使う</text>
</g>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">光は、媒質の中で、何度も散る<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;1.0000" values="1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">アルベドが高いほど、後の回数まで、光が残る<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.0665;0.0667;0.7065;0.7067;1.0000" values="0;0;1;1;0;0"/></text>
<text x="30" y="534" text-anchor="start" style="font-size:14px;font-weight:500;fill:#64748b" opacity="0">雲や霧は、アルベドが高い。多重散乱を、近似で足す<animate attributeName="opacity" dur="22.5s" repeatCount="indefinite" keyTimes="0.0000;0.7065;0.7067;1.0000;1.0000" values="0;0;1;1;0"/></text>
</svg>

<!-- fig:multi-scatter-sum:end -->

## よくあるミス

??? failure "影になる部分の空が、真っ黒"
    **多重散乱**を**足す**。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **何度も散乱した光を、近似で足す**

## 参考

- Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique"（EGSR 2020）
- Bruneton & Neyret, "Precomputed Atmospheric Scattering"（EGSR 2008）
- Wronski, "Volumetric Fog and Lighting"（SIGGRAPH 2014）
- Schneider, "The Real-Time Volumetric Cloudscapes of Horizon Zero Dawn"（SIGGRAPH 2015）

## 関連ページ

- [Atmospheric Scattering](index.md)
- [Hillaire 2020](hillaire.md)
