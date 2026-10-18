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

<svg class="fig illust motion" data-fig="multi-scatter-sum" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-multi-scatter-sum" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">何度も散乱した光を足していく: 1 回だけの 5 分の 1 でも、積み重なる</text>
<rect x="90" y="128.0" width="60" height="192.0" fill="#2563eb" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="0;0;1;1"/></rect>
<text x="120" y="120.0" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b" opacity="0">1.00<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="0;0;1;1"/></text>
<text x="120" y="340" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">1 回</text>
<rect x="164" y="166.39999999999998" width="60" height="153.60000000000002" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1514;0.1517;1.0000" values="0;0;1;1"/></rect>
<text x="194" y="158.39999999999998" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b" opacity="0">0.80<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1514;0.1517;1.0000" values="0;0;1;1"/></text>
<text x="194" y="340" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">2 回</text>
<rect x="238" y="197.11999999999998" width="60" height="122.88000000000002" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2342;0.2345;1.0000" values="0;0;1;1"/></rect>
<text x="268" y="189.11999999999998" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b" opacity="0">0.64<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2342;0.2345;1.0000" values="0;0;1;1"/></text>
<text x="268" y="340" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">3 回</text>
<rect x="312" y="221.69599999999997" width="60" height="98.30400000000003" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3170;0.3172;1.0000" values="0;0;1;1"/></rect>
<text x="342" y="213.69599999999997" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b" opacity="0">0.51<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3170;0.3172;1.0000" values="0;0;1;1"/></text>
<text x="342" y="340" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">4 回</text>
<rect x="386" y="241.35679999999996" width="60" height="78.64320000000002" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/></rect>
<text x="416" y="233.35679999999996" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b" opacity="0">0.41<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;1.0000" values="0;0;1;1"/></text>
<text x="416" y="340" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">5 回</text>
<rect x="460" y="257.08543999999995" width="60" height="62.91456000000002" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4825;0.4828;1.0000" values="0;0;1;1"/></rect>
<text x="490" y="249.08543999999995" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b" opacity="0">0.33<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4825;0.4828;1.0000" values="0;0;1;1"/></text>
<text x="490" y="340" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">6 回</text>
<rect x="534" y="269.66835199999997" width="60" height="50.33164800000002" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5652;0.5655;1.0000" values="0;0;1;1"/></rect>
<text x="564" y="261.66835199999997" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b" opacity="0">0.26<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5652;0.5655;1.0000" values="0;0;1;1"/></text>
<text x="564" y="340" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">7 回</text>
<rect x="608" y="279.7346816" width="60" height="40.26531840000001" fill="#e5aa28" opacity="0"><animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6480;0.6483;1.0000" values="0;0;1;1"/></rect>
<text x="638" y="271.7346816" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#64748b" opacity="0">0.21<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6480;0.6483;1.0000" values="0;0;1;1"/></text>
<text x="638" y="340" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#1f2937">8 回</text>
<line x1="80" y1="320" x2="682" y2="320" stroke="#94a3b8" stroke-width="2"/>
<text x="390" y="380" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">アルベド(反射する割合) 0.8 の媒質。散乱 1 回目の光を 1 とする<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;1.0000" values="1;1;0;0"/></text>
<text x="390" y="380" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">1 回目まで足した合計: 1.00<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.0687;0.0690;0.1514;0.1517;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="380" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">2 回目まで足した合計: 1.80<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.1514;0.1517;0.2342;0.2345;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="380" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">3 回目まで足した合計: 2.44<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.2342;0.2345;0.3170;0.3172;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="380" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">4 回目まで足した合計: 2.95<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3170;0.3172;0.3997;0.4000;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="380" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">5 回目まで足した合計: 3.36<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.3997;0.4000;0.4825;0.4828;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="380" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">6 回目まで足した合計: 3.69<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.4825;0.4828;0.5652;0.5655;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="380" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">7 回目まで足した合計: 3.95<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.5652;0.5655;0.6480;0.6483;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390" y="380" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">8 回目まで足した合計: 4.16<animate attributeName="opacity" dur="14.5s" repeatCount="indefinite" keyTimes="0.0000;0.6480;0.6483;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="390" y="405" text-anchor="middle" style="font-size:12px;font-weight:500;fill:#64748b">無限に足すと 1/(1−0.8) = 5。1 回だけの計算では 8 割以上の光が足りない</text>
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
